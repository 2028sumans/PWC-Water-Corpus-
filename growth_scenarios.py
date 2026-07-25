"""
2050 growth scenarios — where the county's data-center water demand is heading,
and the two levers that actually bend the curve.

Built on three anchors, each already in the repo:
  - TODAY: the shipped fleet (243 buildings, ~6,470 effective IT MW, 49.6 MGD
    plug-in central).
  - 2030-31: the ~1,970 MW of delivery-point (grid) load in the PJM TEAC forward
    pipeline (data/pwc_datacenter_load_pipeline.json), in-service 2027-2031.
  - 2050: buildout SCENARIOS (not forecasts) as multiples of today's effective
    IT MW -- low (pipeline only), central (~2x, consistent with JLARC's
    doubling), high (~3x, queue-driven) -- crossed with a GRID scenario.

TWO FRAMINGS, KEPT SEPARATE (this is the important part)
  - TOTAL footprint (Scope 1+2+3): dominated by Scope 2 (~87%), i.e. water
    consumed at the generating plants, mostly OUTSIDE the basin (§13).
  - ON-SITE Scope 1 only: the direct local draw. This is the quantity ICPRB's
    regional forecast measures (~4 MGD WMA-wide today, ~22 MGD by 2050), so ONLY
    Scope 1 is comparable to it -- comparing our total to ICPRB's on-site number
    would be a category error. PWC Scope 1 is a subset of the WMA total.

THE TWO LEVERS
  1. BUILDOUT (how much gets built) -- the dominant driver of the total.
  2. GRID water-intensity (gal/MWh) -- because Scope 2 dominates, greening the
     grid (wind/solar consume ~0 water) bends the curve more than any facility
     efficiency measure. Facility PUE/cooling is held at central because the
     value-of-disclosure analysis (§35) showed facility levers barely move the
     county total; grid + buildout dominate. Intensity is transparent, from the
     estimator's own constants.

Reads the shipped model; pure NumPy-free arithmetic. Writes
public/data/growth_scenarios.json.
"""
import json
import os

import indirect_water_footprint as m

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
PIPELINE = os.path.join(HERE, "data", "pwc_datacenter_load_pipeline.json")
OUT = os.path.join(HERE, "public", "data", "growth_scenarios.json")

HOURS = 24
PUE_NEW = 1.20               # new-build effective PUE (central)
WUP_CENTRAL = m.WUP_GAL_PER_MW_DAY["pwc_observed"]      # 309 gal/MW/day
S3_FRAC = 0.10
# grid water-intensity scenarios (gal/MWh)
GRID_TODAY = None            # filled from the estimator's blended factor
GRID_DECARB_2050 = 100.0     # illustrative deep-decarbonization (renewables ~0 water)

# ICPRB regional on-site consumptive anchors (ledger-quoted, WMA-wide)
ICPRB_WMA_ONSITE_2025 = 4.0
ICPRB_WMA_ONSITE_2050 = 22.0


def water_from_eff_mw(eff_mw, grid_gal_per_mwh, wup=WUP_CENTRAL, pue=PUE_NEW):
    """Scope 1 (on-site), Scope 2, Scope 3, total MGD from effective IT MW."""
    s1 = eff_mw * wup / 1e6
    s2 = eff_mw * pue * HOURS * grid_gal_per_mwh / 1e6
    s3 = (s1 + s2) * S3_FRAC
    return s1, s2, s3, s1 + s2 + s3


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]
    eff_today = sum(b["scope_water_footprint"]["power"]["effective_it_mw_central"] for b in bs)
    s1_today = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["mgd_central"] for b in bs)
    total_today = sum(b["scope_water_footprint"]["total_mgd_central"] for b in bs)

    mix, cf = m.DOMINION_GENERATION_MIX, m.CONSUMPTION_FACTORS_GAL_PER_MWH
    grid_today = sum(mix[f] * cf[f] for f in mix)

    pipeline = json.load(open(PIPELINE))
    pipe_grid_mw = pipeline["total_mw"]                 # delivery-point (grid) MW
    pipe_eff_mw = pipe_grid_mw / PUE_NEW                # -> effective IT MW

    # effective-IT-MW buildout by horizon
    levels = {
        "today": eff_today,
        "2030_31_pipeline": eff_today + pipe_eff_mw,
        "2050_low": eff_today + pipe_eff_mw,            # pipeline only, no further
        "2050_central": 2.0 * eff_today,                # ~doubling (JLARC)
        "2050_high": 3.0 * eff_today,                   # queue-driven
    }

    scenarios = {}
    for name, eff in levels.items():
        cur = water_from_eff_mw(eff, grid_today)
        row = {"effective_it_mw": round(eff), "grid_today": {
            "scope1_onsite_mgd": round(cur[0], 2), "scope2_mgd": round(cur[1], 2),
            "total_mgd": round(cur[3], 2)}}
        if name.startswith("2050"):
            dec = water_from_eff_mw(eff, GRID_DECARB_2050)
            row["grid_decarbonized"] = {"scope1_onsite_mgd": round(dec[0], 2),
                                        "scope2_mgd": round(dec[1], 2),
                                        "total_mgd": round(dec[3], 2)}
        scenarios[name] = row

    # calibrate "today" arithmetic to the actual fleet (sanity): our per-MW proxy
    # vs the real plug-in central.
    calib = {"model_today_total_mgd": round(water_from_eff_mw(eff_today, grid_today,
             pue=1.24)[3], 1), "actual_plug_in_total_mgd": round(total_today, 1),
             "actual_onsite_s1_mgd": round(s1_today, 2)}

    # G2 — bottom-up vs ICPRB regional (ON-SITE ONLY; PWC is a WMA subset)
    icprb = {
        "note": "ICPRB forecasts ON-SITE (Scope 1) consumptive use for the whole "
                "Washington Metro Area; PWC is a subset. Only our Scope 1 is "
                "comparable -- our TOTAL is ~87% Scope 2 (off-site power-plant water) "
                "that ICPRB's on-site number excludes. That our on-site is a fraction "
                "of the WMA total, while our total dwarfs it, IS the displacement thesis.",
        "pwc_onsite_today_mgd": round(s1_today, 2),
        "icprb_wma_onsite_2025_mgd": ICPRB_WMA_ONSITE_2025,
        "pwc_onsite_2050_central_mgd": scenarios["2050_central"]["grid_today"]["scope1_onsite_mgd"],
        "icprb_wma_onsite_2050_mgd": ICPRB_WMA_ONSITE_2050,
        "pwc_share_of_wma_onsite_today_pct": round(100 * s1_today / ICPRB_WMA_ONSITE_2025),
        "consistent_direction": scenarios["2050_central"]["grid_today"]["scope1_onsite_mgd"] < ICPRB_WMA_ONSITE_2050,
    }

    c = scenarios["2050_central"]
    out = {
        "framing": "Buildout scenarios (multiples of today's effective IT MW), not "
                   "forecasts. TOTAL is Scope 1+2+3 (~87% off-site Scope 2); ON-SITE "
                   "is Scope 1 only (the ICPRB-comparable quantity).",
        "baseline_today": {"effective_it_mw": round(eff_today),
                           "total_mgd": round(total_today, 1),
                           "onsite_s1_mgd": round(s1_today, 2)},
        "pipeline_mw_grid": pipe_grid_mw, "pipeline_mw_effective": round(pipe_eff_mw),
        "scenarios": scenarios,
        "calibration": calib,
        "icprb_cross_check_onsite": icprb,
        "headline": (
            f"Today ~{total_today:.0f} MGD total ({s1_today:.1f} MGD on-site). The committed "
            f"~{pipe_grid_mw:.0f} MW pipeline lifts the total to "
            f"~{scenarios['2030_31_pipeline']['grid_today']['total_mgd']:.0f} MGD by 2030-31. "
            f"By 2050 the total spans ~{scenarios['2050_low']['grid_today']['total_mgd']:.0f} "
            f"(pipeline only) to ~{scenarios['2050_high']['grid_today']['total_mgd']:.0f} MGD "
            f"(3x buildout) on today's grid -- but DECARBONIZING the grid cuts the central "
            f"case from ~{c['grid_today']['total_mgd']:.0f} to "
            f"~{c['grid_decarbonized']['total_mgd']:.0f} MGD, a bigger lever than any facility "
            f"measure because Scope 2 dominates. On-site Scope 1 rises to "
            f"~{c['grid_today']['scope1_onsite_mgd']:.0f} MGD, still a fraction of ICPRB's "
            f"~{ICPRB_WMA_ONSITE_2050:.0f} MGD WMA-wide on-site forecast (consistent)."
        ),
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print(out["headline"], "\n")
    print(f"{'horizon':<20}{'eff MW':>9}{'S1 on-site':>12}{'total (grid today)':>20}{'total (decarb)':>16}")
    for name, r in scenarios.items():
        dec = r.get("grid_decarbonized", {}).get("total_mgd", "")
        print(f"{name:<20}{r['effective_it_mw']:>9,}{r['grid_today']['scope1_onsite_mgd']:>12.2f}"
              f"{r['grid_today']['total_mgd']:>20.1f}{('' if dec=='' else f'{dec:.1f}'):>16}")
    print(f"\ncalibration (model 'today' vs actual): {calib}")
    print(f"ICPRB on-site cross-check: PWC today {icprb['pwc_onsite_today_mgd']} MGD "
          f"= {icprb['pwc_share_of_wma_onsite_today_pct']}% of WMA {ICPRB_WMA_ONSITE_2025}; "
          f"PWC 2050 central on-site {icprb['pwc_onsite_2050_central_mgd']} < WMA {ICPRB_WMA_ONSITE_2050} "
          f"= {icprb['consistent_direction']}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
