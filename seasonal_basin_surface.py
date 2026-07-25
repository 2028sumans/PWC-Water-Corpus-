"""
S2 — the seasonal x basin stress surface: where AND when the local draw is
largest relative to the water available.

Two prior results are one-dimensional slices of the same question:
  §31 (seasonal_stress) -- WHEN demand peaks vs when regional flow bottoms, county-wide.
  §41 (basin_stress)    -- WHERE the draw is large relative to basin flow, annual/peak.
This crosses them: for each watershed and each month, the on-site draw as a share
of that basin's flow in that month. The maximum of the surface is the binding
space-time condition, and it is not visible in either slice alone.

DEMAND SHAPE (stated, because it is the one modelled ingredient)
On-site Scope 1 water is cooling-driven, so its monthly shape follows cooling
degree days, not IT load. Monthly draw is modelled as a small year-round baseload
plus a CDD-proportional component, normalized so the 12-month mean equals the
building-derived annual draw. The baseload share is the one free parameter
(BASELOAD_SHARE) and is swept, because the winter floor for evaporative makeup is
not documented per facility -- the same treatment as §31.3.

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
BASELOAD_SHARE = 0.30            # central: 30% of annual on-site water is non-CDD baseload
SWEEP = (0.10, 0.30, 0.50)


def monthly_weights(cdd_norm, baseload_share):
    """Monthly share of annual on-site water: baseload + CDD-proportional."""
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

        per_share = {}
        for bl in SWEEP:
            w = monthly_weights(cdd_norm, bl)
            # monthly mean draw in MGD: annual mean x 12 x monthly share
            draw_m = [annual_draw * 12 * wi for wi in w]
            ratio = [100 * d / flow[m] for d, m in zip(draw_m, MONTHS)]
            per_share[f"baseload_{int(bl*100)}pct"] = {
                "monthly_draw_mgd": {m: round(d, 3) for m, d in zip(MONTHS, draw_m)},
                "monthly_pct_of_flow": {m: round(r, 1) for m, r in zip(MONTHS, ratio)},
                "worst_month": MONTHS[max(range(12), key=lambda i: ratio[i])],
                "worst_pct_of_flow": round(max(ratio), 1),
            }
        central = per_share[f"baseload_{int(BASELOAD_SHARE*100)}pct"]
        surfaces[ws] = {
            "n_buildings": row["n_buildings"],
            "gage": row["gage"],
            "annual_draw_mgd": annual_draw,
            "completed_only_annual_draw_mgd": round(completed_annual, 3) if completed_annual else None,
            "monthly_flow_mgd": flow,
            "central_baseload_share": BASELOAD_SHARE,
            "central": central,
            "baseload_sweep": {k: {"worst_month": v["worst_month"],
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

    out = {
        "framing": b["framing"],
        "demand_shape": (
            "Monthly on-site draw = small year-round baseload + CDD-proportional cooling "
            f"component, normalized to the building-derived annual mean. Baseload share is the one "
            f"free parameter (central {int(BASELOAD_SHARE*100)}%), swept {SWEEP} because the winter "
            "floor for evaporative makeup is undocumented per facility."),
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
    print(f"(central baseload share {int(BASELOAD_SHARE*100)}%)\n")
    hdr = "watershed".ljust(16) + "".join(m.rjust(6) for m in MONTHS)
    print(hdr); print("-" * len(hdr))
    for ws, v in surfaces.items():
        r = v["central"]["monthly_pct_of_flow"]
        print(ws.ljust(16) + "".join(f"{r[m]:>6.1f}" for m in MONTHS))
    print(f"\nbinding condition: {worst_ws} in {wm} at {wp}% of that month's mean flow")
    for ws, v in surfaces.items():
        print(f"  {ws:<16} sweep: " + ", ".join(
            f"{k.split('_')[1]}->{x['worst_pct_of_flow']}% ({x['worst_month']})"
            for k, x in v["baseload_sweep"].items()))
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
