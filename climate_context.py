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
from collections import defaultdict

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
    print(f"\nCDD by decade: {cdd['annual_by_decade']}")
    print(f"Monthly CDD: {cdd['monthly_climatology']}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
