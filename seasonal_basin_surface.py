"""
S2 — the seasonal x basin stress surface: where AND when the local draw is
largest relative to the water available.

Two prior results are one-dimensional slices of the same question:
  §31 (seasonal_stress) -- WHEN demand peaks vs when regional flow bottoms, county-wide.
  §41 (basin_stress)    -- WHERE the draw is large relative to basin flow, annual/peak.
This crosses them: for each watershed and each month, the on-site draw as a share
of that basin's flow in that month. The maximum of the surface is the binding
space-time condition, and it is not visible in either slice alone.

DEMAND SHAPE -- CORRECTED 2026-08-03. Read this before changing anything.

This file previously modelled the monthly shape as a small year-round baseload
plus a CDD-proportional component, sweeping the baseload share over
(0.10, 0.30, 0.50) with 0.30 central. That model is ~70% too peaky in summer and
less than half the observed winter floor:

    month          Jul    Aug    Jan    peak/trough
    CDD model b=.30  3.04   2.61   0.30       10.1x
    ICPRB OBSERVED   1.50   1.80   0.70        3.0x

The observed series is ICPRB's Table A.3-2 (2025 WMA Water Supply Study,
Appendix A.3), derived from actual utility-reported data-center water use in the
Loudoun Water and Prince William Water service areas -- i.e. measured, in the two
counties that matter, including ours.

Back-fitting the CDD model's baseload share to that series gives b ~ 0.70-0.76,
outside the swept range entirely. The physical reason is that a data center runs
its IT load year-round and rejects heat year-round; only the *incremental*
evaporative duty tracks temperature. JLARC (Rpt598 p.39) confirms this
independently: data centers "do not currently participate in demand response
programs" because "energy use is driven by computing activity."

So: OBSERVED_MONTHLY_FACTORS is now the CENTRAL case and the CDD model is retained
only as a sensitivity. Every seasonal percentage this file emits changed.

A DISAGREEMENT INSIDE THE SOURCE, stated rather than resolved silently:
ICPRB's two-page public fact sheet (March 2026) says summer monthly use "can be
close to three times the average annual demand," which matches the OLD CDD model's
3.04x. Their technical appendix (Table A.3-2, above) caps the observed monthly
factor at 1.8. We follow the appendix, because it is observed data rather than a
summary sentence, and because the fact sheet's "three times" is almost certainly
summer-versus-winter (1.8/0.6 = 3.0) rather than summer-versus-annual-average.
The peak-DAY factor ("as much as 10 times") is a separate claim and is unaffected.

FLOW is the USGS monthly mean-discharge climatology per basin (§41), used as-is.

FRAMING (carried from §41, unchanged): this is a SCALE COMPARISON, not a
withdrawal attribution. Prince William data centers are supplied from the
Occoquan/Potomac public system, not from these streams.

Reads basin_stress.json + seasonal_stress.json. Writes
public/data/seasonal_basin_surface.json.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public", "data")
BASIN = os.path.join(PUB, "basin_stress.json")
SEASON = os.path.join(PUB, "seasonal_stress.json")
OUT = os.path.join(PUB, "seasonal_basin_surface.json")

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# ---------------------------------------------------------------------------
# CENTRAL demand shape: OBSERVED, not modelled.
# ---------------------------------------------------------------------------
# ICPRB, "2025 Washington Metropolitan Area Water Supply Study" (ICP-596,
# December 2025), Appendix A.3, Table A.3-2: monthly factors for data-center
# water use, derived from observed usage patterns in Loudoun and Prince William
# Counties. Series already has mean 1.00 over the 12 months (sums to 12.0).
OBSERVED_MONTHLY_FACTORS = {
    "Jan": 0.7, "Feb": 0.6, "Mar": 0.6, "Apr": 0.7,
    "May": 0.9, "Jun": 1.0, "Jul": 1.5, "Aug": 1.8,
    "Sep": 1.5, "Oct": 1.0, "Nov": 0.9, "Dec": 0.8,
}
OBSERVED_SOURCE = (
    "ICPRB, 2025 Washington Metropolitan Area Water Supply Study (ICP-596, "
    "Dec 2025), Appendix A.3, Table A.3-2 -- monthly data-center water-use "
    "factors derived from observed utility-reported usage in the Loudoun Water "
    "and Prince William Water service areas. Peak month August (1.8x annual "
    "mean); peak-to-trough 3.0x. Supersedes the CDD-proportional model used "
    "here through 2026-08-02, which gave 3.04x in July and 10.1x peak-to-trough."
)

# ---------------------------------------------------------------------------
# SENSITIVITY only: the former central model, retained so the correction is
# auditable and so the CDD driver can still be exercised.
# ---------------------------------------------------------------------------
BASELOAD_SHARE = 0.75            # best fit to OBSERVED_MONTHLY_FACTORS (~0.70-0.76)
SWEEP = (0.30, 0.50, 0.75)       # 0.30 = the superseded central value, kept for audit

# DROUGHT DENOMINATOR SENSITIVITY
#
# Every percentage in this file divides demand by an OBSERVED historical monthly
# flow. That denominator is not stationary. Prince William's own vulnerability
# assessment (AECOM, "FINAL Vulnerability Assessment Report," 9 Jan 2023,
# Table 7) projects the average number of months per year in drought to rise by:
#
#     moderate (PDSI -2 to -3)   +39% to +67%
#     severe   (PDSI -3 to -4)   +114% to +350%
#     extreme  (PDSI < -4)       +201% to +1534%
#
# across RCP4.5/RCP8.5 and 2050/2075. The stated mechanism is that
# "precipitation will fall in more intense bursts followed by longer dry
# periods" -- i.e. annual totals hold up while low flows deepen. Demand moves
# the same way: the same report has days >=95 F rising by 13-15 (2050) and
# 21-32 (2075), and this model's demand shape is CDD-proportional.
#
# AECOM report months-in-drought, not a flow multiplier, and converting one to
# the other needs a rainfall-runoff model this project does not have. So rather
# than invent a number, the denominator is SWEPT and the direction is cited.
#
# RE-LABELLED 2026-08-03. This sweep was previously documented as "a sensitivity,
# NOT a projection." It is neither. The observed county PDSI record shows the
# longest unbroken run of severe-or-worse months in 132 years -- 23 months,
# 202406 through 202604, STILL OPEN at the data cutoff. The reduced-flow branches
# therefore describe a CURRENT CONDITION, not a hypothetical tail.
#
# Also note AECOM's baseline is 2.6x low for severe and 6.7x low for extreme
# against the observed record (METHODOLOGY 63.2), so their percentages are used
# here only for DIRECTION, never for magnitude.
DROUGHT_FLOW_SWEEP = (1.00, 0.90, 0.80, 0.70)
DROUGHT_SOURCE = (
    "OBSERVED CONDITION, not a hypothetical sensitivity. NOAA/NCEI county PDSI "
    "1895-2026 shows the longest unbroken severe-or-worse run in the record -- 23 "
    "months, 202406-202604, still open at data cutoff; severe-drought return "
    "period has fallen from 1-in-3.9 yr (full record) to 1-in-2.5 yr (since 1976). "
    "Direction of change corroborated by AECOM, FINAL Vulnerability Assessment "
    "Report, Prince William County (9 Jan 2023), Table 7 -- used for direction "
    "only, since AECOM's modelled baseline is 2.6x (severe) to 6.7x (extreme) "
    "below the observed record. Multipliers remain a denominator sweep, not a "
    "rainfall-runoff projection."
)


# ---------------------------------------------------------------------------
# LEG 3 OF THE PAPER: timing. The municipal baseline, measured.
# ---------------------------------------------------------------------------
# The seasonal result only lands if BOTH sides are measured. ICPRB publishes the
# municipal side from 11 years of daily production data (2013-2023), so the
# contrast is measured-vs-measured rather than modelled-vs-asserted.
#
# Peak-day / annual-average factors, ICPRB 2025 WMA Water Supply Study Ch.2:
MUNICIPAL_PEAK_DAY_FACTORS = {
    "WSSC Water": 1.6,
    "Washington Aqueduct": 1.7,
    "Fairfax Water": 1.9,
    "Loudoun Water": 1.5,
    "Combined CO-OP": 1.6,
}
# Data centers, same metric: ICPRB fact sheet says peak daily use is "as much as
# 10 times" the average. Our own evidence ladder reproduces 9.9x independently
# (harness check 14), from building-derived annual means rather than utility data.
DATACENTER_PEAK_DAY_FACTOR_ICPRB = 10.0
DATACENTER_PEAK_DAY_FACTOR_OURS = 9.9

# Monthly production factors, ICPRB Table 4-3 (11 years of daily data). Municipal
# demand swings ~1.3x across the year; data-center demand swings 3x on the
# observed monthly shape and ~10x on a peak-day basis, in the SAME months.
MUNICIPAL_MONTHLY_FACTORS = {
    "Fairfax Water":       {"Jan": 0.89, "Jul": 1.18},
    "WSSC Water":          {"Jan": 0.97, "Jul": 1.10},
    "Washington Aqueduct": {"Jan": 0.94, "Jul": 1.14},
    "Loudoun Water":       {"Jan": 0.80, "Jul": 1.31},
}
MUNICIPAL_SOURCE = (
    "ICPRB, 2025 WMA Water Supply Study (ICP-596, Dec 2025): peak-day factors from "
    "Ch.2; monthly production factors from Table 4-3, derived from 11 years of "
    "daily production data 2013-2023 for four suppliers."
)
# Why the data-center load is flat rather than weather-driven -- an independent,
# non-hydrologic reason to expect the high baseload the observed shape implies:
FLAT_LOAD_CORROBORATION = (
    "JLARC Rpt598 p.39: 'Data center companies in Virginia do not currently "
    "participate in demand response programs' because 'energy use is driven by "
    "computing activity'. p.41: 'at the end of the day, a 200 MW data center is "
    "going to be a 200 MW data center.' A year-round IT load rejects heat "
    "year-round; only the incremental evaporative duty tracks temperature."
)


def observed_weights():
    """CENTRAL. Monthly share of annual on-site water, from ICPRB Table A.3-2."""
    f = [OBSERVED_MONTHLY_FACTORS[m] for m in MONTHS]
    s = sum(f) or 1.0
    return [x / s for x in f]      # sums to 1 across the year


def monthly_weights(cdd_norm, baseload_share):
    """SENSITIVITY. Superseded model: baseload + CDD-proportional.

    Retained so the 2026-08-03 correction stays auditable. Do not use as the
    central case -- see the module docstring.
    """
    cdd = [cdd_norm[m] for m in MONTHS]
    tot = sum(cdd) or 1.0
    w = [baseload_share / 12.0 + (1 - baseload_share) * c / tot for c in cdd]
    s = sum(w) or 1.0
    return [x / s for x in w]      # sums to 1 across the year


def main():
    b = json.load(open(BASIN))
    s = json.load(open(SEASON))
    cdd_norm = s["demand_cdd"]["monthly_norm"]

    surfaces, peaks = {}, {}
    for ws, row in b["basins"].items():
        flow = row.get("monthly_flow_mgd")
        if not flow:
            continue
        annual_draw = row["draw_annual_mgd"]
        completed_annual = None
        # completed-only annual draw, scaled from the completed peak-day ratio
        if row.get("completed_only_peak_day_mgd") and row.get("draw_peak_day_mgd"):
            completed_annual = annual_draw * row["completed_only_peak_day_mgd"] / row["draw_peak_day_mgd"]

        def surface_for(weights):
            """One monthly surface from a set of 12 normalized weights."""
            draw_m = [annual_draw * 12 * wi for wi in weights]
            ratio = [100 * d / flow[m] for d, m in zip(draw_m, MONTHS)]
            return {
                "monthly_draw_mgd": {m: round(d, 3) for m, d in zip(MONTHS, draw_m)},
                "monthly_pct_of_flow": {m: round(r, 1) for m, r in zip(MONTHS, ratio)},
                "worst_month": MONTHS[max(range(12), key=lambda i: ratio[i])],
                "worst_pct_of_flow": round(max(ratio), 1),
            }

        # CENTRAL: observed ICPRB shape.
        w_c = observed_weights()
        central = surface_for(w_c)

        # SENSITIVITY: the superseded CDD model across its baseload sweep.
        per_share = {f"cdd_baseload_{int(bl*100)}pct": surface_for(monthly_weights(cdd_norm, bl))
                     for bl in SWEEP}

        # Same central demand shape, shrinking the flow denominator. Answers
        # "how much of the headroom is an artefact of a stationary denominator?"
        draw_c = [annual_draw * 12 * wi for wi in w_c]
        drought = {}
        for mult in DROUGHT_FLOW_SWEEP:
            ratio = [100 * d / (flow[m] * mult) for d, m in zip(draw_c, MONTHS)]
            i = max(range(12), key=lambda k: ratio[k])
            drought[f"flow_x{mult:.2f}"] = {
                "worst_month": MONTHS[i],
                "worst_pct_of_flow": round(ratio[i], 1),
            }

        surfaces[ws] = {
            "n_buildings": row["n_buildings"],
            "gage": row["gage"],
            "annual_draw_mgd": annual_draw,
            "completed_only_annual_draw_mgd": round(completed_annual, 3) if completed_annual else None,
            "monthly_flow_mgd": flow,
            "central_shape": "observed_icprb_a32",
            "central": central,
            "drought_denominator_sweep": drought,
            "drought_denominator_source": DROUGHT_SOURCE,
            "cdd_model_sensitivity": {k: {"worst_month": v["worst_month"],
                                          "worst_pct_of_flow": v["worst_pct_of_flow"]}
                                      for k, v in per_share.items()},
        }
        peaks[ws] = (central["worst_month"], central["worst_pct_of_flow"])

    worst_ws = max(peaks, key=lambda k: peaks[k][1]) if peaks else None
    wm, wp = peaks.get(worst_ws, (None, None))
    # the value of crossing: compare to the one-dimensional slices
    br = surfaces.get("BROAD RUN", {})
    annual_flat = (100 * br.get("annual_draw_mgd", 0)
                   / (sum(br.get("monthly_flow_mgd", {}).values()) / 12)) if br else None

    obs = OBSERVED_MONTHLY_FACTORS
    out = {
        "framing": b["framing"],
        "demand_shape": (
            "CENTRAL: observed monthly data-center water-use factors from ICPRB Table A.3-2, "
            "normalized to the building-derived annual mean. Peak August 1.8x, trough February "
            "0.6x, peak-to-trough 3.0x. SENSITIVITY: the superseded baseload + CDD-proportional "
            f"model, swept over baseload shares {SWEEP}. The CDD model at its former central "
            "baseload of 30% gives 3.04x in July and 10.1x peak-to-trough -- roughly 70% too "
            "peaky in summer and less than half the observed winter floor."),
        "demand_shape_source": OBSERVED_SOURCE,
        "observed_monthly_factors": obs,
        "observed_peak_to_trough": round(max(obs.values()) / min(obs.values()), 2),
        "superseded_cdd_model": {
            "note": "Retained as a sensitivity so the 2026-08-03 correction is auditable.",
            "former_central_baseload_share": 0.30,
            "best_fit_baseload_share": BASELOAD_SHARE,
            "corroboration": (
                "JLARC Rpt598 p.39: data centers 'do not currently participate in demand "
                "response programs' because 'energy use is driven by computing activity' -- "
                "an independent reason to expect a high, near-constant baseload."),
        },
        "timing_leg": {
            "claim": ("Data-center demand is roughly six times peakier than the municipal "
                      "demand the supply system was engineered around, and it peaks in the "
                      "same months regional flows bottom."),
            "municipal_peak_day_factors": MUNICIPAL_PEAK_DAY_FACTORS,
            "municipal_peak_day_range": [min(MUNICIPAL_PEAK_DAY_FACTORS.values()),
                                         max(MUNICIPAL_PEAK_DAY_FACTORS.values())],
            "datacenter_peak_day_icprb": DATACENTER_PEAK_DAY_FACTOR_ICPRB,
            "datacenter_peak_day_ours": DATACENTER_PEAK_DAY_FACTOR_OURS,
            "peakiness_ratio_vs_municipal_mean": round(
                DATACENTER_PEAK_DAY_FACTOR_OURS
                / (sum(MUNICIPAL_PEAK_DAY_FACTORS.values())
                   / len(MUNICIPAL_PEAK_DAY_FACTORS)), 1),
            "municipal_monthly_factors": MUNICIPAL_MONTHLY_FACTORS,
            "source": MUNICIPAL_SOURCE,
            "why_the_load_is_flat": FLAT_LOAD_CORROBORATION,
            "NOT_AN_INDEPENDENT_REPRODUCTION": (
                "CORRECTED 2026-08-03. An earlier version of this block claimed our 9.9x "
                "peak-day factor was an INDEPENDENT reproduction of ICPRB's ~10x. It is "
                "not. Our 9.9 = WUP_PEAK_GAL_PER_MW_DAY['pwc_observed'] (3,060) / "
                "WUP_GAL_PER_MW_DAY['pwc_observed'] (309), and BOTH of those constants "
                "are ICPRB figures derived from the SAME source -- Prince William Water's "
                "reported 2023 use of 0.42 MGD average and 4.2 MGD peak day (ratio 10.0). "
                "We are dividing ICPRB's two numbers by each other. It is a consistency "
                "check on our own arithmetic, NOT external validation. Do not present it "
                "as an out-of-sample check."),
            "what_IS_independent": (
                "The COINCIDENCE is independent. The demand peak (Jul-Sep) comes from "
                "ICPRB/utility water data; the flow minimum (Aug) comes from USGS gage "
                "records -- Potomac at Little Falls bottoms at 41% of annual mean in "
                "August, Cedar Run at 47%. Two unrelated measurement systems. The claim "
                "'demand peaks when flow bottoms' is therefore genuinely supported; the "
                "claim 'we independently reproduced the peak factor' is not."),
            "honest_limitation": (
                "ICPRB's own regressions 'tend to under-predict the highest demands', "
                "and all six of their models show negative mean residuals. Peak "
                "estimates in this literature -- including the WUP figures this model "
                "borrows -- are therefore systematically conservative."),
        },
        "surfaces": surfaces,
        "binding_condition": {
            "watershed": worst_ws, "month": wm, "pct_of_monthly_flow": wp,
            "note": "Maximum of the space-time surface -- the month and basin where the on-site "
                    "draw is largest relative to the water actually in the stream.",
        },
        "why_crossing_matters": {
            "annual_flat_pct_of_mean_flow": round(annual_flat, 1) if annual_flat else None,
            "seasonal_only": "county-wide demand peaks in Jul; regional flow bottoms in Aug (§31)",
            "basin_only": "Broad Run carries 166/243 buildings (§41)",
            "crossed": f"{worst_ws} in {wm} reaches {wp}% of that month's flow -- "
                       f"vs {round(annual_flat,1) if annual_flat else '?'}% on a flat annual basis. "
                       f"Neither the seasonal slice nor the basin slice shows this alone.",
        },
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print("SEASONAL x BASIN STRESS SURFACE — on-site draw as % of that month's flow")
    print("CENTRAL SHAPE: observed (ICPRB Table A.3-2). "
          f"peak {max(obs, key=obs.get)} {max(obs.values())}x, peak/trough "
          f"{max(obs.values())/min(obs.values()):.1f}x\n")
    hdr = "watershed".ljust(16) + "".join(m.rjust(6) for m in MONTHS)
    print(hdr); print("-" * len(hdr))
    for ws, v in surfaces.items():
        r = v["central"]["monthly_pct_of_flow"]
        print(ws.ljust(16) + "".join(f"{r[m]:>6.1f}" for m in MONTHS))
    print(f"\nbinding condition: {worst_ws} in {wm} at {wp}% of that month's mean flow")
    print("\nsuperseded CDD model, for audit:")
    for ws, v in surfaces.items():
        print(f"  {ws:<16} " + ", ".join(
            f"b={k.split('_')[2]}->{x['worst_pct_of_flow']}% ({x['worst_month']})"
            for k, x in v["cdd_model_sensitivity"].items()))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
