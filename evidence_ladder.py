"""
V2 + S1 — the evidence ladder made quantitative, and the peak-day view.

V2 EVIDENCE LADDER
The estimator's central claim is that uncertainty tracks EVIDENCE, not modelling
effort: a building whose power comes from a VADEQ permit should carry a visibly
tighter interval than one inferred from floor area. That is asserted throughout
the methodology; this measures it. For each power-evidence tier we report the
distribution of per-building 90% CI widths (already computed by monte_carlo.py),
so the ladder becomes a table a reviewer can check rather than a claim.

  tier 1  permit generator capacity x ICPRB Eq 6-3   (observed)
  tier 3  fitted GFA->MW, operator-calibrated        (inferred, operator-informed)
  tier 4  fitted GFA->MW, generic curve              (inferred, no operator prior)
  (tier 2, stated critical load, is empty -- see METHODOLOGY 28: the ePortal
   sweep found no per-building stated loads. Its emptiness IS a finding.)

S1 PEAK-DAY VIEW
The estimator reports annual averages. ICPRB's own peak-day WUP (3,060 vs 309
gal/MW/day in Prince William) implies the local draw on a hot summer day is
~10x the annual mean. Since the county's supply stress is a SUMMER problem
(seasonal_stress.py), the peak-day number -- not the annual mean -- is the one a
water utility plans against. Reported for the local Scope 1 draw only, because
peak-day is a local-infrastructure question.

Reads the shipped model. Writes public/data/evidence_ladder.json.
"""
import json
import os
import statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "evidence_ladder.json")

TIER_LABEL = {
    1: "permit generator capacity (observed)",
    2: "stated critical load (EMPTY -- no per-building disclosure exists)",
    3: "fitted GFA->MW, operator-calibrated (inferred)",
    4: "fitted GFA->MW, generic curve (inferred)",
    5: "legacy vintage density band (unused)",
}


def pct(vals, p):
    return float(st.quantiles(sorted(vals), n=100)[p - 1]) if len(vals) > 2 else float(st.mean(vals))


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    # ---- V2: CI width by evidence tier --------------------------------------
    by_tier = defaultdict(list)
    mw_by_tier = defaultdict(float)
    for b in bs:
        swf = b["scope_water_footprint"]
        t = swf["power"].get("evidence_tier")
        u = swf.get("uncertainty", {}).get("relative_width_pct")
        if t is None or u is None:
            continue
        by_tier[t].append(u)
        mw_by_tier[t] += swf["power"]["effective_it_mw_central"]

    tiers = {}
    for t in sorted(by_tier):
        v = by_tier[t]
        tiers[str(t)] = {
            "label": TIER_LABEL.get(t, f"tier {t}"),
            "n_buildings": len(v),
            "effective_it_mw": round(mw_by_tier[t]),
            "ci_width_pct_median": round(st.median(v), 0),
            "ci_width_pct_p25": round(pct(v, 25), 0),
            "ci_width_pct_p75": round(pct(v, 75), 0),
            "ci_halfwidth_pct_median": round(st.median(v) / 2, 0),
        }
    # record the empty tier explicitly -- its emptiness is a finding
    if "2" not in tiers:
        tiers["2"] = {"label": TIER_LABEL[2], "n_buildings": 0, "effective_it_mw": 0,
                      "note": "No Prince William data-center building publishes a stated "
                              "critical IT load recoverable from public records (METHODOLOGY 28)."}

    t1 = tiers.get("1", {}).get("ci_width_pct_median")
    t4 = tiers.get("4", {}).get("ci_width_pct_median")
    ratio = round(t4 / t1, 1) if t1 and t4 else None

    # ---- S1: peak-day vs annual (local Scope 1) -----------------------------
    s1 = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["mgd_central"] for b in bs)
    peak = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["peak_day_mgd"] for b in bs)
    completed = [b for b in bs if (b.get("status") or "").lower() == "completed"]
    s1_c = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["mgd_central"] for b in completed)
    peak_c = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["peak_day_mgd"] for b in completed)

    peak_view = {
        "all_243_buildings": {"annual_avg_s1_mgd": round(s1, 2), "peak_day_s1_mgd": round(peak, 2),
                              "ratio": round(peak / s1, 1)},
        "completed_only": {"annual_avg_s1_mgd": round(s1_c, 2), "peak_day_s1_mgd": round(peak_c, 2),
                           "ratio": round(peak_c / s1_c, 1) if s1_c else None,
                           "n": len(completed)},
        "basis": "ICPRB Prince William peak-day WUP 3,060 vs annual-average 309 gal/MW/day",
        "why_it_matters": "Utilities size infrastructure to peak day, not annual mean, and the "
                          "peak coincides with the July-August streamflow minimum (METHODOLOGY 31). "
                          "The annual-average framing understates the infrastructure-relevant draw "
                          "by ~10x.",
    }

    out = {
        "evidence_ladder": {
            "purpose": "Per-building 90% CI width by power-evidence tier -- the estimator's "
                       "claim that uncertainty tracks evidence, measured rather than asserted.",
            "tiers": tiers,
            "tier4_over_tier1_width_ratio": ratio,
            "headline": (
                f"Permit-observed buildings (tier 1, n={tiers.get('1',{}).get('n_buildings')}) carry a "
                f"median 90% interval of +/-{tiers.get('1',{}).get('ci_halfwidth_pct_median')}%, versus "
                f"+/-{tiers.get('4',{}).get('ci_halfwidth_pct_median')}% for generic floor-area "
                f"buildings (tier 4, n={tiers.get('4',{}).get('n_buildings')}) -- a {ratio}x wider "
                f"interval for the same modelling effort, purely from the evidence available. "
                f"Tier 2 (stated critical load) is EMPTY: no building discloses one."),
        },
        "peak_day": peak_view,
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print("EVIDENCE LADDER — 90% CI width by power-evidence tier\n")
    print(f"{'tier':<5}{'n':>5}{'eff MW':>9}{'CI ±% (median)':>17}  label")
    for k in sorted(tiers, key=lambda x: int(x)):
        t = tiers[k]
        hw = t.get("ci_halfwidth_pct_median")
        print(f"{k:<5}{t['n_buildings']:>5}{t['effective_it_mw']:>9,}"
              f"{('' if hw is None else f'±{hw:.0f}%'):>17}  {t['label']}")
    print(f"\n  tier4/tier1 width ratio: {ratio}x\n")
    print("PEAK DAY vs ANNUAL (local Scope 1)")
    for k in ("all_243_buildings", "completed_only"):
        v = peak_view[k]
        print(f"  {k:<20} annual {v['annual_avg_s1_mgd']:>6.2f} MGD   peak-day "
              f"{v['peak_day_s1_mgd']:>6.2f} MGD   ({v['ratio']}x)")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
