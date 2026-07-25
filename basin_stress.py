"""
B2 (+S2) — per-basin supply stress: how the local data-center draw compares in
SCALE to the flow of the streams those buildings sit on, month by month.

WHAT THIS IS -- AND EXPLICITLY IS NOT
Prince William's data centers are supplied by PRINCE WILLIAM WATER (public
supply, sourced from the Occoquan Reservoir / Potomac system). They do NOT
withdraw from the small streams they sit beside. So this is a SCALE COMPARISON,
not a withdrawal attribution: it answers "how big is the county's data-center
draw relative to the water moving through these basins?" -- the standard way to
express whether a demand is hydrologically material -- and it is the local
counterpart to the regional low-flow coincidence in seasonal_stress.py (§31).
Nothing here should be read as "facility X takes water from stream Y."

METHOD
  - Local draw per watershed: from basin_attribution.json (Scope 1 annual mean
    and ICPRB peak-day), which allocates each building's on-site draw to the PWC
    watershed polygon it sits in.
  - Basin flow: USGS NWIS monthly mean-discharge climatology at the gage draining
    each watershed, full record.
  - The gage drains a LARGER area than the watershed polygon containing the
    buildings, so gage flow overstates the water available at the buildings'
    locations, and the reported draw-to-flow ratios are therefore CONSERVATIVE
    (they understate local stress). Stated rather than corrected, because a
    drainage-area transfer onto a 4 sq mi polygon would add more error than it
    removes.

RECORD CAVEAT
Broad Run and Bull Run gages were discontinued (records end 1986 and 1981); their
climatologies are historical monthly means, used as a stationary reference. S F
Quantico runs to 2026. This is flagged in the output rather than hidden -- and
the drought context (§31: PDSI -5.3, driest 0.9% of months) means current flows
are likely BELOW these historical means, again making the ratios conservative.

Reads basin_attribution.json + vendored NWIS files. Writes
public/data/basin_stress.json.
"""
import json
import os
import statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "water_raw")
BASIN = os.path.join(HERE, "data", "basin_attribution.json")
OUT = os.path.join(HERE, "public", "data", "basin_stress.json")

CFS_TO_MGD = 0.6463168831
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# watershed (as named in facility water_context) -> representative USGS gage
GAGES = {
    "BROAD RUN":      {"site": "01656500", "name": "Broad Run at Buckland",
                       "drainage_sqmi": 50.2, "record": "1950-1986 (discontinued)",
                       # Broad Run has two usable gages bracketing the data-center
                       # corridor; whether the buildings sit above or below any one
                       # gage changes the flow available at their location, so the
                       # downstream gage is carried as an explicit sensitivity
                       # rather than assuming one is "conservative".
                       "alt_site": "01656650", "alt_name": "Broad Run near Bristow",
                       "alt_drainage_sqmi": 89.6, "alt_record": "1974-1986"},
    "BULL RUN":       {"site": "01657000", "name": "Bull Run near Manassas",
                       "drainage_sqmi": 146.0, "record": "1950-1981 (discontinued)"},
    "QUANTICO CREEK": {"site": "01658500", "name": "S F Quantico Creek near Independent Hill",
                       "drainage_sqmi": 7.62, "record": "1951-2026 (active)"},
    # POWELLS CREEK: gage 01657895 has only ~2 years (1995-96) -- insufficient for
    # a climatology; recorded as a data gap rather than estimated.
}


def flow_climatology(site):
    path = os.path.join(RAW, f"nwis_monthly_{site}.rdb")
    by_month, yrs = defaultdict(list), set()
    for line in open(path):
        if line.startswith(("#", "agency_cd", "5s")) or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        try:
            yr, mo, mean_va = int(f[5]), int(f[6]), float(f[7])
        except (ValueError, IndexError):
            continue
        by_month[mo].append(mean_va)
        yrs.add(yr)
    if len(by_month) < 12:
        return None
    mgd = {m: st.mean(by_month[m]) * CFS_TO_MGD for m in range(1, 13)}
    return {"monthly_mgd": mgd, "annual_mean_mgd": st.mean(mgd.values()),
            "low_month": min(mgd, key=mgd.get), "low_mgd": min(mgd.values()),
            "n_years": len(yrs)}


def completed_draw_by_watershed():
    """Today's operating fleet only, so the full-buildout figures can be put in
    context rather than read as current conditions."""
    prof = json.load(open(os.path.join(HERE, "public", "data", "facility_profiles.json")))
    out = defaultdict(lambda: {"n": 0, "s1": 0.0, "peak": 0.0})
    for b in prof["buildings"]:
        swf = b.get("scope_water_footprint")
        if not swf or (b.get("status") or "").lower() != "completed":
            continue
        ws = (b.get("water_context") or {}).get("watershed_name") or "UNKNOWN"
        out[ws]["n"] += 1
        out[ws]["s1"] += swf["scope1_onsite_cooling"]["mgd_central"]
        out[ws]["peak"] += swf["scope1_onsite_cooling"]["peak_day_mgd"]
    return out


def main():
    ba = json.load(open(BASIN))
    local = ba["scope1_by_watershed"]
    done = completed_draw_by_watershed()

    rows, gaps = {}, []
    for ws, meta in GAGES.items():
        draw = local.get(ws)
        clim = flow_climatology(meta["site"])
        if not draw or not clim:
            gaps.append(ws)
            continue
        lo_m = clim["low_month"]
        rows[ws] = {
            "gage": meta["name"], "site": meta["site"],
            "drainage_sqmi": meta["drainage_sqmi"], "record": meta["record"],
            "n_years": clim["n_years"],
            "n_buildings": draw["n"],
            "draw_annual_mgd": round(draw["s1"], 3),
            "draw_peak_day_mgd": round(draw["peak"], 2),
            "completed_only_n": done.get(ws, {}).get("n", 0),
            "completed_only_peak_day_mgd": round(done.get(ws, {}).get("peak", 0.0), 2),
            "completed_only_pct_of_low_month_flow_PEAK": round(
                100 * done.get(ws, {}).get("peak", 0.0) / clim["low_mgd"], 1),
            "flow_annual_mean_mgd": round(clim["annual_mean_mgd"], 1),
            "flow_low_month": MONTHS[lo_m - 1],
            "flow_low_month_mgd": round(clim["low_mgd"], 1),
            "pct_of_annual_mean_flow_annual_draw": round(100 * draw["s1"] / clim["annual_mean_mgd"], 2),
            "pct_of_low_month_flow_annual_draw": round(100 * draw["s1"] / clim["low_mgd"], 2),
            "pct_of_low_month_flow_PEAK_draw": round(100 * draw["peak"] / clim["low_mgd"], 1),
            "monthly_flow_mgd": {MONTHS[m - 1]: round(clim["monthly_mgd"][m], 1) for m in range(1, 13)},
        }
        # downstream-gage sensitivity where a second gage brackets the corridor
        if meta.get("alt_site"):
            alt = flow_climatology(meta["alt_site"])
            if alt:
                rows[ws]["downstream_gage_sensitivity"] = {
                    "gage": meta["alt_name"], "drainage_sqmi": meta["alt_drainage_sqmi"],
                    "record": meta["alt_record"],
                    "flow_low_month": MONTHS[alt["low_month"] - 1],
                    "flow_low_month_mgd": round(alt["low_mgd"], 1),
                    "pct_of_low_month_flow_PEAK_draw": round(100 * draw["peak"] / alt["low_mgd"], 1),
                }

    # POWELLS CREEK explicitly recorded as a gap
    if "POWELLS CREEK" in local:
        gaps.append("POWELLS CREEK (gage 01657895 has ~2 years of record -- insufficient)")

    worst = max(rows, key=lambda k: rows[k]["pct_of_low_month_flow_PEAK_draw"]) if rows else None
    w = rows.get(worst, {})

    out = {
        "framing": (
            "SCALE COMPARISON, not withdrawal attribution. Prince William data centers are "
            "supplied by Prince William Water (Occoquan/Potomac public supply), not by direct "
            "withdrawal from these streams. Ratios express how large the local on-site draw is "
            "relative to the water moving through the basins the buildings occupy."),
        "buildout_caveat": (
            "Draw figures cover ALL buildings in the watershed (built, under construction and "
            "planned) -- i.e. a full-buildout condition, not today's operating fleet. Today's "
            "completed-only draw is far smaller (see completed_only_* fields)."),
        "gage_sensitivity": (
            "Flow depends on which gage represents the buildings' position in the basin. Broad "
            "Run is bracketed by two gages (Buckland 50.2 sq mi upstream, Bristow 89.6 sq mi "
            "downstream) and BOTH ratios are reported rather than assuming one is conservative. "
            "Historical (discontinued) records are stationary references; under the current "
            "drought (PDSI -5.3, METHODOLOGY 31) actual flows are likely below them, which would "
            "make the ratios larger, not smaller."),
        "basins": rows,
        "data_gaps": gaps,
        "headline": (
            (lambda br: (
                f"Broad Run carries the county's data-center concentration ({br['n_buildings']} "
                f"buildings, {br['completed_only_n']} built today). On an annual-average basis the "
                f"on-site draw is only {br['pct_of_annual_mean_flow_annual_draw']}% of the basin's "
                f"mean flow. But on an ICPRB peak summer day at FULL BUILDOUT it reaches "
                f"{br['pct_of_low_month_flow_PEAK_draw']}% of the basin's lowest-month mean flow "
                f"({br['downstream_gage_sensitivity']['pct_of_low_month_flow_PEAK_draw']}% at the "
                f"downstream gage) -- i.e. of the same order as the entire low flow of the stream "
                f"the buildings sit on, and in the month that flow is lowest (METHODOLOGY 31). "
                f"Today's completed fleet is {br['completed_only_pct_of_low_month_flow_PEAK']}%. "
                f"This is a scale comparison, not a withdrawal: the water is supplied from the "
                f"Occoquan/Potomac system. The binding constraint is peak-day-on-low-flow, not the "
                f"annual mean."))(rows["BROAD RUN"])
            if "BROAD RUN" in rows else "insufficient gage coverage"),
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print("PER-BASIN SCALE COMPARISON (on-site Scope 1 draw vs basin flow)\n")
    print(f"{'watershed':<16}{'bldgs':>6}{'draw ann':>10}{'draw peak':>11}"
          f"{'flow mean':>11}{'low month':>11}{'peak % of low':>15}")
    print("-" * 82)
    for ws, r in sorted(rows.items(), key=lambda kv: -kv[1]["pct_of_low_month_flow_PEAK_draw"]):
        print(f"{ws:<16}{r['n_buildings']:>6}{r['draw_annual_mgd']:>10.3f}{r['draw_peak_day_mgd']:>11.2f}"
              f"{r['flow_annual_mean_mgd']:>11.1f}{r['flow_low_month']+' '+str(r['flow_low_month_mgd']):>11}"
              f"{r['pct_of_low_month_flow_PEAK_draw']:>14.1f}%")
    if gaps:
        print(f"\ndata gaps: {gaps}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
