"""
Seasonal water-stress model — WHEN data-center water demand lands relative to
WHEN the basin can least afford it.

The estimator answers "how much" as an annual average. This answers the timing
question the annual average hides: the sector's water demand is cooling-driven
and therefore summer-concentrated, and it peaks in the same months the region's
rivers are at their seasonal low. That coincidence -- not the annual mean -- is
the ICPRB study's central supply concern (2025 WMA Study Sec. 6.2; ICPRB Data
Centers & Water Use, March 2026).

TWO HARD-DATA CURVES, ONE MODELED OVERLAY
  SUPPLY   monthly streamflow climatology at two USGS gages, full record:
             - 01646500 Potomac R at Little Falls (ICPRB's regional reference
               gage, record from 1930) -- the metro supply master gage.
             - 01663500 Cedar Run near Catlett (Occoquan basin, PWC-local,
               record from 1942).
           Source: USGS NWIS monthly-statistics service (mean daily discharge).
  DEMAND   monthly cooling-degree-day climatology, Prince William County
           (NOAA, 1895-2026), already computed in climate_context.py.
  OVERLAY  a transparent monthly fleet-water model: a flat baseload (IT-driven
           Scope 2 + Scope 3, present every month) plus a cooling-variable
           component that scales with CDD. The cooling-variable SHARE is the one
           free parameter and is swept, so the seasonal amplitude is reported as
           a band, not a point.

WHAT IS AND IS NOT CLAIMED
  Claimed: the demand peak and the supply trough coincide in calendar time, and
  the sector's consumptive draw is largest exactly when flow is smallest. Both
  curves are measured; the coincidence is not modeled.
  Not claimed: a precise gallons-per-month figure. The overlay's amplitude
  depends on the cooling-variable share, which is why it is banded.
"""
import json
import os
import statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "water_raw")
CLIMATE = os.path.join(HERE, "public", "data", "climate_context.json")
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "seasonal_stress.json")

CFS_TO_MGD = 0.6463168831  # 1 cubic foot/s = 0.6463 million gal/day
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

GAGES = {
    "01646500": {"name": "Potomac R at Little Falls", "role": "ICPRB regional reference"},
    "01663500": {"name": "Cedar Run near Catlett", "role": "Occoquan basin, PWC-local"},
}


def flow_climatology(site):
    """Monthly mean discharge (MGD) across the full record, from NWIS rdb."""
    path = os.path.join(RAW, f"nwis_monthly_{site}.rdb")
    by_month = defaultdict(list)
    yrs = set()
    for line in open(path):
        if line.startswith(("#", "agency_cd", "5s")) or not line.strip():
            continue
        f = line.rstrip("\n").split("\t")
        # agency, site, param, ts_id, loc, year, month, mean_va
        try:
            yr, mo, mean_va = int(f[5]), int(f[6]), float(f[7])
        except (ValueError, IndexError):
            continue
        by_month[mo].append(mean_va)
        yrs.add(yr)
    clim_cfs = {m: st.mean(by_month[m]) for m in range(1, 13)}
    clim_mgd = {m: clim_cfs[m] * CFS_TO_MGD for m in range(1, 13)}
    ann_mean = st.mean(clim_mgd.values())
    norm = {m: clim_mgd[m] / ann_mean for m in range(1, 13)}
    low_m = min(norm, key=norm.get)
    return {
        "record_years": f"{min(yrs)}-{max(yrs)}",
        "n_years": len(yrs),
        "monthly_mgd": {MONTHS[m - 1]: round(clim_mgd[m], 1) for m in range(1, 13)},
        "monthly_norm": {MONTHS[m - 1]: round(norm[m], 3) for m in range(1, 13)},
        "annual_mean_mgd": round(ann_mean, 1),
        "low_flow_month": MONTHS[low_m - 1],
        "low_flow_pct_of_annual": round(100 * norm[low_m]),
    }


def county_annual_water_mgd():
    """Fleet annual-average total water (central), summed over buildings only."""
    d = json.load(open(PROFILES))
    tot = 0.0
    for b in d["buildings"]:
        swf = b.get("scope_water_footprint")
        if swf:
            tot += swf["total_mgd_central"]
    return tot


def main():
    clim = json.load(open(CLIMATE))
    cdd = clim["cooling_degree_days"]["monthly_climatology"]  # {"01":..,"12":..}
    cdd_m = {int(k): v for k, v in cdd.items()}
    cdd_mean = st.mean(cdd_m.values())
    cdd_norm = {m: cdd_m[m] / cdd_mean for m in range(1, 13)}
    peak_m = max(cdd_norm, key=cdd_norm.get)

    flows = {s: flow_climatology(s) for s in GAGES}

    # Coincidence index against the ICPRB regional gage: demand share x scarcity.
    ref = flows["01646500"]
    ref_norm = {MONTHS.index(k) + 1: v for k, v in ref["monthly_norm"].items()}
    stress = {m: cdd_norm[m] / ref_norm[m] for m in range(1, 13)}
    stress_peak = max(stress, key=stress.get)

    # Transparent monthly fleet-water overlay. Total annual water = baseload
    # (flat, every month) + cooling-variable (scales with CDD). Sweep the
    # cooling-variable SHARE of the annual total; report the summer/winter swing
    # as a band. A share of ~0 -> flat; higher share -> larger summer peak.
    annual = county_annual_water_mgd()
    overlay = {}
    for share in (0.15, 0.30, 0.45):
        base = annual * (1 - share)
        var_annual = annual * share
        # distribute the variable part in proportion to CDD across the year
        cdd_year = sum(cdd_m.values())
        monthly = {m: base + var_annual * 12 * (cdd_m[m] / cdd_year) for m in range(1, 13)}
        # (var_annual is an annual-average MGD; * 12 * monthly_share spreads it)
        # normalize so the 12-month mean equals `annual`
        scale = annual / st.mean(monthly.values())
        monthly = {m: monthly[m] * scale for m in range(1, 13)}
        swing = max(monthly.values()) / min(monthly.values())
        overlay[f"cooling_var_share_{int(share*100)}pct"] = {
            "monthly_mgd": {MONTHS[m - 1]: round(monthly[m], 1) for m in range(1, 13)},
            "summer_peak_mgd": round(max(monthly.values()), 1),
            "winter_trough_mgd": round(min(monthly.values()), 1),
            "peak_to_trough_ratio": round(swing, 2),
        }

    headline = (
        f"Data-center cooling demand peaks in {MONTHS[peak_m-1]} "
        f"(CDD climatology); the Potomac at Little Falls is at its seasonal low "
        f"in {ref['low_flow_month']}, averaging {ref['low_flow_pct_of_annual']}% "
        f"of its annual-mean flow, and Cedar Run "
        f"(PWC-local) bottoms in {flows['01663500']['low_flow_month']} at "
        f"{flows['01663500']['low_flow_pct_of_annual']}% of annual mean. The "
        f"demand-to-scarcity coincidence index peaks in {MONTHS[stress_peak-1]}. "
        f"The sector's water draw is largest in the exact months the region's "
        f"rivers carry the least water."
    )

    out = {
        "purpose": "Seasonal coincidence of data-center cooling-water demand with "
                   "regional low-flow. Two measured curves (CDD demand shape, "
                   "USGS streamflow climatology) plus a banded monthly fleet-water overlay.",
        "demand_cdd": {
            "monthly_norm": {MONTHS[m - 1]: round(cdd_norm[m], 3) for m in range(1, 13)},
            "peak_month": MONTHS[peak_m - 1],
            "jun_sep_share_pct": clim["cooling_degree_days"]["jun_sep_share_pct"],
        },
        "supply_streamflow": {GAGES[s]["name"]: {**flows[s], **GAGES[s]} for s in GAGES},
        "coincidence_index": {
            "monthly": {MONTHS[m - 1]: round(stress[m], 2) for m in range(1, 13)},
            "peak_month": MONTHS[stress_peak - 1],
            "definition": "normalized CDD demand / normalized Potomac flow; >1 = "
                          "demand-heavy relative to supply that month",
        },
        "fleet_water_overlay": {
            "annual_mean_total_mgd": round(annual, 1),
            "note": "baseload (flat) + cooling-variable (CDD-shaped); the "
                    "cooling-variable share is swept because PWC's air/closed-loop "
                    "dominant fleet has a modest direct-water seasonal amplitude, "
                    "while its Scope-2 thermoelectric water is more summer-peaked.",
            "scenarios": overlay,
        },
        "headline": headline,
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print(headline, "\n")
    print(f"{'Month':<5}{'CDD_norm':>9}{'Potomac':>9}{'CedarRun':>9}{'Stress':>8}")
    for m in range(1, 13):
        print(f"{MONTHS[m-1]:<5}{cdd_norm[m]:>9.2f}{ref_norm[m]:>9.2f}"
              f"{flows['01663500']['monthly_norm'][MONTHS[m-1]]:>9.2f}{stress[m]:>8.2f}")
    print(f"\nFleet annual-mean water: {annual:.1f} MGD")
    for k, v in overlay.items():
        print(f"  {k}: summer {v['summer_peak_mgd']} / winter {v['winter_trough_mgd']} "
              f"MGD  (x{v['peak_to_trough_ratio']})")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
