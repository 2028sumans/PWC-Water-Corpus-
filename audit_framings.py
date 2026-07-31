"""Framing audit: does the prose respect the caveat its source file declares?

Every error found in review so far has the same signature -- the analysis file
states a framing, and the abstract quietly violates it. Arithmetic reproduces;
interpretation drifts. The research-readiness harness recomputes numbers, so it
is blind to exactly this class.

This script does not check numbers. For each claim in the abstract it prints the
framing note attached to its source, so the two can be read side by side. It is
a checklist for a human, not an automated pass/fail -- the judgement "does this
sentence honour that caveat?" is not mechanizable.

Run: python3 audit_framings.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public", "data")

# claim in the abstract -> (source, the framing it must not violate, status)
CLAIMS = [
    ("243 data-center buildings, reconstructed from public records",
     "facility_profiles.json",
     "Building classification is a judgement: which parcels count as data-center "
     "buildings. 243 = county GIS + permit records; no independent list exists to "
     "check it against.",
     "OPEN -- inclusion criteria are documented in METHODOLOGY 5 but never "
     "externally validated. If a reviewer asks 'how do you know it is 243', the "
     "answer is 'this is what the county records show', not 'we verified it'."),

    ("consumptive water footprint",
     "indirect_water_footprint.py:1105",
     "Scope 1 mgd_central is DELIVERED water; Scope 2 is CONSUMPTION. "
     "total_mgd_central mixes bases.",
     "RESOLVED METHODOLOGY 53 -- abstract uses total_consumptive throughout."),

    ("Electricity generation accounts for 88%",
     "indirect_water_footprint.py + Privette et al.",
     "The denominator includes Scope 3, which is a LITERATURE RANGE (5-15% of "
     "Scope 1+2, Privette et al. 2026) applied as a multiplier -- not a local "
     "estimate. No PDF in the corpus; ledger marks it not machine-verifiable.",
     "OPEN -- 88% is a share of a total containing an unverifiable component. "
     "Scope 2 / (Scope 1 + Scope 2) alone would be ~97%. State which."),

    ("more than 40% assigned to Lake Anna (average accounting)",
     "basin_attribution / DOMINION_GENERATION_MIX",
     "Scales with Dominion's generation mix; the 2025 IRP figure (nuclear 25%) is "
     "one of several defensible conventions (2023 delivered ex-purchases gives "
     "28.4 MGD, all-VA generation 21.0).",
     "DISCLOSED METHODOLOGY 49.4 -- the RATIO is robust, the LEVEL is convention-"
     "dependent. Abstract quotes the ratio. OK."),

    ("0% attributed to Lake Anna (marginal accounting)",
     "PJM_MARGINAL_FUEL_MIX + nuclear_never_marginal",
     "Zero is DEFINITIONAL (nuclear absent from PJM's marginal fuel list), and the "
     "framing is SHORT-RUN because PJM's statistic is short-run by construction. "
     "Marginal water = marginal fuel shares x AVERAGE intensity, a proxy.",
     "RESOLVED METHODOLOGY 54-55 -- abstract says 'short-run marginal (dispatch)'."),

    ("about +/-60% uncertainty from floor area",
     "evidence_ladder.json",
     "+/-60% is the TIER 4 median (generic fitted curve, n=141). Tier 1 "
     "(permit-observed, n=45) is +/-26%. The fleet is not uniformly +/-60%.",
     "OK -- abstract scopes it to 'power inferred from floor area', which is "
     "tiers 3-4. Do not let it drift to 'the estimate carries +/-60%'."),

    ("within 1.3x at every quartile",
     "validation_effect_size.py",
     "Benchmark is a lognormal fit to JLARC anchors RESCALED by PWC intensity "
     "(309/1139). No paired per-building data exists. PWC is one of the six "
     "localities inside JLARC's dataset -- partially, not fully, independent.",
     "PARTLY RESOLVED -- 'intensity-rescaled' is now stated; the partial-"
     "independence caveat is carried verbally only (no room in 2000 chars)."),

    ("3% of mean annual flow, 17-25% of July flow",
     "seasonal_basin_surface.json",
     "SCALE COMPARISON, not withdrawal attribution -- the buildings are supplied "
     "by Prince William Water (Occoquan/Potomac), not from these streams. Also: "
     "the demand SHAPE is modelled (CDD-proportional, baseload swept 0.1/0.3/0.5); "
     "only the streamflow is measured.",
     "RESOLVED (withdrawal) METHODOLOGY 56 -- abstract now says 'on-site use by "
     "the buildings in one basin equivalent to' + explicit scale-comparison note. "
     "OPEN (shape): the abstract does not say the demand curve is modelled."),

    ("regional water authority's assessment covers on-site use only",
     "ICPRB.DataCentersandWaterUse.March2026.pdf",
     "ICPRB's study is POTOMAC BASIN / WMA-wide and distinguishes facilities "
     "upstream of WMA intakes from those within it. It is not a Broad Run study.",
     "RESOLVED METHODOLOGY 56 -- 'this basin' (antecedent Broad Run) replaced "
     "with 'basin-wide'."),

    ("under 3% of our estimate",
     "derived",
     "Compares ICPRB's SCOPE (on-site) to OUR total (PWC county, all 243). "
     "Different geographies: their assessment is basin-wide, ours is one county.",
     "OPEN -- the SCOPE claim is sound; the implied geographic comparison is not "
     "like-for-like. Safer framing: 'covers only the on-site component, which is "
     "under 3% of the footprint we estimate for this county.'"),
]


def main():
    print("FRAMING AUDIT -- prose vs the caveat its source declares")
    print("=" * 72)
    counts = {}
    for claim, src, framing, status in CLAIMS:
        tag = status.split()[0].rstrip("-")
        counts[tag] = counts.get(tag, 0) + 1
        print(f"\nCLAIM   {claim}")
        print(f"SOURCE  {src}")
        print(f"FRAMING {framing}")
        print(f"STATUS  {status}")
    print("\n" + "=" * 72)
    print("  ".join(f"{k}: {v}" for k, v in sorted(counts.items())))
    print("\nThis script cannot pass or fail. 'Does the sentence honour the "
          "caveat' is a judgement call --\nthe point is to put them next to each "
          "other so the call gets made deliberately.")

    # the framing strings are live: re-read them so this file cannot go stale
    print("\nLIVE framing notes still present in the shipped JSON:")
    for f in ("seasonal_basin_surface", "basin_stress", "growth_scenarios"):
        d = json.load(open(os.path.join(PUB, f + ".json")))
        note = d.get("framing", "(none)")
        print(f"  {f}: {note[:88]}...")


if __name__ == "__main__":
    main()
