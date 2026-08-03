"""
Climate and drought context for the water footprint — the water-STRESS dimension.

The estimator says how much water data centers consume. This says WHEN and under
what conditions that demand lands. It reads the NOAA monthly county series
(1895-present) that the audit found unused and computes four things the footprint
must be read against:

  1. Drought severity NOW vs the full 130-year record (Palmer indices).
  2. The long-run trend in cooling demand (cooling degree days), which drives the
     evaporative Scope 1 load.
  3. The seasonal shape of that cooling load (what share falls in Jun-Sep).
  4. The recent precipitation deficit.

The finding these converge on: rising, summer-concentrated cooling demand is
landing during a near-record drought, in the same months when river flows are
lowest -- the ICPRB study's exact concern (2025 WMA Study Section 6.2). None of
this was in the model before the July 2026 dataset re-audit.

Source: NOAA Climate at a Glance, Prince William County, VA (monthly, 1895-2026),
vendored in data/water_raw/*.json.
"""
import json
import os
import statistics as st
from collections import defaultdict, Counter

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "water_raw")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data",
                   "climate_context.json")


def _series(fname):
    d = json.load(open(os.path.join(RAW, fname)))["data"]
    return [(k, v["value"]) for k, v in d.items() if v.get("value") is not None]


def drought():
    out = {}
    for name, f in [("PDSI", "PDSI.json"), ("PHDI", "PHDI.json"),
                    ("PMDI", "PMDI.json"), ("Palmer_Z", "Palmer_Z.json")]:
        s = _series(f)
        vals = [v for _, v in s]
        cur_month, cur = s[-1]
        pctile = 100 * sum(1 for v in vals if v <= cur) / len(vals)
        out[name] = {
            "latest_month": cur_month, "latest_value": cur,
            "min_ever": min(vals), "max_ever": max(vals),
            "percentile_of_record": round(pctile, 1), "n_months": len(vals),
        }
    return out


def drought_return_periods():
    """OBSERVED drought return periods from the 132-year county PDSI record.

    Added 2026-08-03. This replaces the projection-based drought framing that
    METHODOLOGY 63.2 previously carried. Prince William's own vulnerability
    assessment (AECOM, 9 Jan 2023, Table 7) reports projected *percentage*
    changes in months-per-year in drought -- +114% to +350% severe, +201% to
    +1534% extreme. Backing AECOM's implied baseline out of their own table
    (change-in-months alongside percent-change) gives ~0.25 severe months/yr and
    ~0.057 extreme months/yr. The OBSERVED county record gives 0.66 and 0.38.

    So AECOM's baseline is ~2.6x low for severe and ~6.7x low for extreme, and
    those eye-catching percentages come off a near-zero modelled base. Observed
    beats modelled where both exist, and here both exist.

    Method: annual worst monthly PDSI, empirical exceedance over the full record
    and over the post-1976 half. No model, no downscaling, no RCP.
    """
    s = _series("PDSI.json")
    worst, permo = {}, defaultdict(Counter)
    for k, v in s:
        y = int(k[:4])
        worst[y] = min(worst.get(y, 99), v)
        if v <= -2: permo[y]["moderate"] += 1
        if v <= -3: permo[y]["severe"] += 1
        if v <= -4: permo[y]["extreme"] += 1
    years = sorted(worst)
    n = len(years)
    recent = [y for y in years if y >= 1976]

    def rp(yrs, thr):
        hits = sum(1 for y in yrs if worst[y] <= thr)
        p = hits / len(yrs) if yrs else 0
        return {"years_with_event": hits, "p_any_year": round(p, 4),
                "return_period_years": round(1 / p, 1) if p else None}

    classes = {"any_drought": -1, "moderate": -2, "severe": -3,
               "extreme": -4, "pdsi_le_5": -5, "pdsi_le_6": -6}

    # longest unbroken run of severe-or-worse months, and whether it is still open
    ks = sorted(k for k, _ in s)
    vals = dict(s)
    run = best = 0
    best_span = cur_start = None
    for k in ks:
        if vals[k] <= -3:
            if run == 0: cur_start = k
            run += 1
            if run > best: best, best_span = run, (cur_start, k)
        else:
            run = 0
    still_open = best_span is not None and best_span[1] == ks[-1]

    # months/yr by 30-year epoch, severe-or-worse
    epochs = {}
    for a in (1896, 1926, 1956, 1986):
        span = [y for y in years if a <= y < a + 30]
        if len(span) == 30:
            tot = sum(permo[y]["severe"] for y in span)
            epochs[f"{a}-{a+29}"] = {"severe_or_worse_months": tot,
                                     "per_year": round(tot / 30, 2)}

    return {
        "record": {"first_year": years[0], "last_year": years[-1],
                   "n_years": n, "n_months": len(s)},
        "return_periods_full_record": {k: rp(years, t) for k, t in classes.items()},
        "return_periods_since_1976": {k: rp(recent, t) for k, t in classes.items()},
        "observed_months_per_year": {
            c: round(sum(permo[y][c] for y in years) / n, 2)
            for c in ("moderate", "severe", "extreme")},
        "aecom_implied_baseline_months_per_year": {
            "severe": 0.25, "extreme": 0.057,
            "note": ("Backed out of AECOM Table 7 itself: +0.289 severe months = "
                     "+114% implies a 0.25 baseline; +0.114 extreme = +201% implies "
                     "0.057. Observed is 0.66 and 0.38 -- AECOM's baseline is 2.6x "
                     "low for severe and 6.7x low for extreme.")},
        "longest_severe_run": {
            "months": best,
            "from": best_span[0] if best_span else None,
            "to": best_span[1] if best_span else None,
            "still_open_at_data_cutoff": still_open,
            "note": ("Longest unbroken run of severe-or-worse (PDSI <= -3) months in "
                     "the record. If still_open, the run does not end -- the data does.")},
        "severe_or_worse_by_epoch": epochs,
        "worst_years_by_min_monthly_pdsi": [
            {"year": y, "min_monthly_pdsi": round(worst[y], 2),
             "severe_or_worse_months": permo[y]["severe"]}
            for y in sorted(years, key=lambda y: worst[y])[:6]],
        "source": ("NOAA/NCEI Climate at a Glance, Prince William County VA, monthly "
                   "PDSI, 1895-2026 (data/water_raw/PDSI.json). Observed record, not "
                   "a projection."),
    }


def cooling_degree_days():
    s = _series("Cooling Degree Days.json")
    ann, mon = defaultdict(float), defaultdict(list)
    for k, v in s:
        yr = int(k[:4])
        ann[yr] += v
        mon[k[4:6]].append(v)
    by_decade = defaultdict(list)
    for yr, tot in ann.items():
        if 1895 <= yr <= 2025:
            by_decade[(yr // 10) * 10].append(tot)
    decade = {f"{d}s": round(st.mean(v)) for d, v in sorted(by_decade.items())}
    monthly = {m: round(st.mean(mon[m])) for m in sorted(mon)}
    tot = sum(monthly.values()) or 1
    jun_sep = sum(monthly[m] for m in ("06", "07", "08", "09"))
    early = st.mean([v for d, v in by_decade.items() if d < 1950 for v in [st.mean(v)]] or [1])
    return {
        "annual_by_decade": decade,
        "monthly_climatology": monthly,
        "jun_sep_share_pct": round(100 * jun_sep / tot, 0),
        "recent_2010s_2020s_mean": round(st.mean(by_decade[2010] + by_decade[2020])),
        "pct_increase_vs_pre1950": round(
            100 * (st.mean(by_decade[2010] + by_decade[2020]) /
                   st.mean(sum([by_decade[d] for d in by_decade if d < 1950], [])) - 1)),
    }


def precipitation():
    s = _series("Precipitation.json")
    last12 = sum(v for _, v in s[-12:])
    ann = defaultdict(float)
    for k, v in s:
        ann[int(k[:4])] += v
    full = [t for y, t in ann.items() if 1895 <= y <= 2025]
    mean_ann = st.mean(full)
    return {
        "last_12mo_total_in": round(last12, 1),
        "long_run_mean_annual_in": round(mean_ann, 1),
        "deficit_in": round(last12 - mean_ann, 1),
        "deficit_pct": round(100 * (last12 - mean_ann) / mean_ann),
    }


def main():
    ctx = {
        "source": "NOAA Climate at a Glance, Prince William County VA (monthly 1895-2026)",
        "drought": drought(),
        "drought_return_periods": drought_return_periods(),
        "cooling_degree_days": cooling_degree_days(),
        "precipitation": precipitation(),
    }
    dr = ctx["drought"]["PDSI"]
    cdd = ctx["cooling_degree_days"]
    pr = ctx["precipitation"]
    ctx["headline"] = (
        f"Prince William County is in extreme drought: PDSI {dr['latest_value']} "
        f"({dr['latest_month']}), the driest {dr['percentile_of_record']}% of "
        f"{dr['n_months']} months since 1895. Cooling degree days are up "
        f"{cdd['pct_increase_vs_pre1950']}% since the early record "
        f"({cdd['recent_2010s_2020s_mean']}/yr now) and {cdd['jun_sep_share_pct']:.0f}% "
        f"of them fall in Jun-Sep. Last 12 months of precipitation are "
        f"{pr['deficit_pct']}% below normal. Data-center cooling demand is rising, "
        f"summer-concentrated, and landing during a near-record drought in the "
        f"months when river flows are lowest."
    )
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(ctx, open(OUT, "w"), indent=1)
    print(ctx["headline"])
    rp = ctx["drought_return_periods"]
    f, r = rp["return_periods_full_record"], rp["return_periods_since_1976"]
    print(f"\nOBSERVED drought return periods ({rp['record']['n_years']} yr, "
          f"{rp['record']['first_year']}-{rp['record']['last_year']}):")
    for c in ("moderate", "severe", "extreme"):
        print(f"   {c:<10} full record 1 in {f[c]['return_period_years']} yr  |  "
              f"since 1976 1 in {r[c]['return_period_years']} yr")
    lr = rp["longest_severe_run"]
    print(f"   longest severe-or-worse run: {lr['months']} months, {lr['from']}-{lr['to']}"
          f"{'  (STILL OPEN at data cutoff)' if lr['still_open_at_data_cutoff'] else ''}")
    print(f"   severe+ months/yr by epoch: "
          + ", ".join(f"{k}={v['per_year']}" for k, v in rp['severe_or_worse_by_epoch'].items()))
    print(f"\nCDD by decade: {cdd['annual_by_decade']}")
    print(f"Monthly CDD: {cdd['monthly_climatology']}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
