"""
The convention table — the paper's central result, computed rather than asserted.

The claim is that WHICH BASIN bears a data center's electricity-related water is
set by accounting convention, not by measurement. Testing that needs more than the
two conventions the abstract compares. Six standard conventions exist for the same
physical electricity; this script computes the ones that can be computed and states
plainly which cannot.

  1  Dominion utility-average        location-based, single-utility fleet
  2  PJM RTO-wide average            location-based, whole-market
  3  eGRID SERC Virginia/Carolina    location-based, THE COUNTY'S OWN BASIS
  4  Market-based (PPA/VPPA/REC)     NOT COMPUTABLE -- no dataset of who holds what
  5  Short-run marginal              PJM real-time marginal fuel shares (2022)
  6  Long-run marginal               CITED from JLARC/E3, not recomputed here

Conventions 1-3 and 5 are computed below from the shipped model. 4 and 6 are
carried as documented bounds so the table is complete and honest about its gaps.

WHY 3 MATTERS MOST: eGRID SERC Virginia/Carolina is the basis Prince William County
uses for its own Board-adopted climate accounting (CESMP Appendix F.2). A paper
arguing that convention decides the answer is far stronger when the REGULATOR'S OWN
convention gives a different answer than the modeller's.

Reads facility_profiles.json + the plant->basin map. Writes
public/data/convention_table.json.
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public", "data")
OUT = os.path.join(PUB, "convention_table.json")

# The basin that holds North Anna, i.e. the one the paper's headline is about.
LAKE_ANNA_BASIN_HINT = "york"


def _lake_anna_share(by_basin, total):
    """Share of Scope 2 water landing in the York basin (Lake Anna / North Anna)."""
    if not total:
        return 0.0
    v = sum(m for b, m in by_basin.items() if LAKE_ANNA_BASIN_HINT in b.lower())
    return 100.0 * v / total


def attribute(mix, factors, plants, s2_total):
    """Distribute s2_total across generating basins using a fuel mix.

    Fuels with no water factor (oil, municipal waste) are EXCLUDED and the
    remainder renormalized; the excluded share is reported so the omission is
    visible rather than silent. Their water intensity is small and unassigned in
    this corpus -- inventing one would be worse than declaring it.
    """
    known = {f: s for f, s in mix.items() if f in factors}
    excluded = sum(s for f, s in mix.items() if f not in factors)
    blended = sum(known[f] * factors[f] for f in known)
    by_basin = defaultdict(float)
    if not blended:
        return by_basin, 0.0, excluded
    for fuel in known:
        if fuel not in plants:
            continue                      # fuel has no located plants (e.g. renewable)
        fuel_mgd = s2_total * (known[fuel] * factors[fuel]) / blended
        tot = sum(p["consumption_mgd"] for p in plants[fuel]) or 1
        for p in plants[fuel]:
            by_basin[p["basin"]] += fuel_mgd * p["consumption_mgd"] / tot
    return by_basin, blended, excluded


def main():
    import indirect_water_footprint as m
    from basin_analysis import load_plants

    prof = json.load(open(os.path.join(PUB, "facility_profiles.json")))
    bs = [b for b in prof["buildings"] if b.get("scope_water_footprint")]
    s2 = sum(b["scope_water_footprint"]["scope2_electricity"]["mgd_central"] for b in bs)
    s2_marg = sum(b["scope_water_footprint"]["scope2_electricity"]
                  ["marginal_based"]["mgd_central"] for b in bs)
    plants = load_plants()
    cf = m.CONSUMPTION_FACTORS_GAL_PER_MWH

    rows = {}

    # --- conventions 1-3: location-based averages ---------------------------
    #
    # GEOGRAPHY TRAP, and the reason this is not a one-liner. The plant->basin
    # map covers VIRGINIA plants only. Attributing a PJM-wide or SERC-wide
    # nuclear share across North Anna and Surry alone silently assumes every
    # nuclear plant in the convention's geography sits in Virginia -- which
    # inflates Lake Anna instead of deflating it, i.e. it gets the DIRECTION
    # wrong. A convention whose geography is broader than the plant map must
    # therefore be scaled by Virginia's share of that geography's nuclear
    # generation, and where that share is not sourceable the convention is
    # reported as non-computable rather than guessed.
    for cid, spec in m.LOCATION_BASED_CONVENTIONS.items():
        by_basin, blended, excluded = attribute(spec["mix"], cf, plants, s2)
        raw = _lake_anna_share(by_basin, s2)
        va_share = spec.get("va_share_of_nuclear", 1.0)
        broader = "va_share_of_nuclear" in spec

        if broader and va_share is None:
            rows[cid] = {
                "label": spec["label"], "family": "location_based",
                "computable": False,
                "geography": spec["geography"], "source": spec["source"],
                "nuclear_share_of_mix_pct": round(100 * spec["mix"].get("nuclear", 0), 2),
                "lake_anna_pct_of_scope2": None,
                "why_not_computable": (
                    "The convention's geography is broader than Virginia, and no source "
                    "in this corpus splits its nuclear generation between Virginia and "
                    "the rest of the subregion. SERC Virginia/Carolina nuclear includes "
                    "Duke's North Carolina fleet. Direction is certain -- Lake Anna's "
                    "share FALLS relative to the Dominion convention, because the "
                    "nuclear denominator gains plants outside Virginia -- but the "
                    "magnitude is not computable here."),
                "unscaled_if_all_nuclear_were_virginian_pct": round(raw, 2),
                "bound": f"below {rows['dominion_utility_average']['lake_anna_pct_of_scope2']}%",
                "unassigned_fuel_share": round(excluded, 4),
            }
            continue

        scaled = raw * (va_share if va_share is not None else 1.0)
        rows[cid] = {
            "label": spec["label"],
            "family": "location_based",
            "computable": True,
            "geography": spec["geography"],
            "source": spec["source"],
            "nuclear_share_of_mix_pct": round(100 * spec["mix"].get("nuclear", 0), 2),
            "blended_intensity_gal_per_mwh": round(blended, 1),
            "scope2_mgd": round(s2, 2),
            "lake_anna_pct_of_scope2": round(scaled, 2),
            "by_basin_mgd": {b: round(v, 3) for b, v in
                             sorted(by_basin.items(), key=lambda kv: -kv[1])},
            "unassigned_fuel_share": round(excluded, 4),
        }
        if broader:
            rows[cid]["geography_scaling"] = {
                "va_share_of_convention_nuclear": round(va_share, 4),
                "source": spec.get("va_share_source"),
                "unscaled_pct": round(raw, 2),
                "note": ("Unscaled figure assumes every nuclear plant in the "
                         "convention's geography is in Virginia, which is false and "
                         "would invert the result."),
            }

    # --- convention 5: short-run marginal -----------------------------------
    mmix = m.PJM_MARGINAL_FUEL_MIX
    mcf = m.MARGINAL_CONSUMPTION_FACTORS_GAL_PER_MWH
    by_basin, blended, excluded = attribute(mmix, mcf, plants, s2_marg)
    rows["short_run_marginal"] = {
        "label": "Short-run marginal (PJM real-time marginal fuel shares, 2022)",
        "family": "marginal",
        "computable": True,
        "geography": "PJM real-time dispatch stack",
        "source": ("Monitoring Analytics 2023 SOM Sec.3 Table 3-69, published 2022 row. "
                   "YEAR IS LOAD-BEARING: nuclear's marginal share runs 0.39-1.35% over "
                   "2019-2023, so Lake Anna moves 0.87% (2022) / 1.38% (2023) / 2.90% "
                   "(2019). 'Under 2%' holds for 2022-23 and fails for 2019-21."),
        "nuclear_share_of_mix_pct": round(100 * mmix.get("nuclear", 0), 2),
        "blended_intensity_gal_per_mwh": round(blended, 1),
        "scope2_mgd": round(s2_marg, 2),
        "lake_anna_pct_of_scope2": round(_lake_anna_share(by_basin, s2_marg), 2),
        "by_basin_mgd": {b: round(v, 3) for b, v in
                         sorted(by_basin.items(), key=lambda kv: -kv[1])},
        "unassigned_fuel_share": round(excluded, 4),
    }

    # --- convention 4: market-based. NOT COMPUTABLE. ------------------------
    rows["market_based"] = {
        "label": "Market-based (PPA / VPPA / unbundled REC)",
        "family": "market_based",
        "computable": False,
        "geography": "contractual, not geographic",
        "lake_anna_pct_of_scope2": None,
        "why_not_computable": (
            "No dataset in this corpus, or in any public source located, records "
            "WHICH operators hold clean-energy contracts for WHICH buildings. The "
            "county states the practice exists -- CESMP p.26: 'some existing data "
            "centers in the county are already procuring 100% clean electricity for "
            "their operations', and Action E.4 notes 'Both Dominion and NOVEC offer "
            "100% renewable electricity options' -- but not who or how much. For a "
            "buyer at 100% clean the market-based Lake Anna share is ~0 by "
            "construction; for a non-participant it is the location-based figure. "
            "Reported as a bound, not a number."),
        "bound": "0% for 100%-clean contract holders; location-based otherwise",
        "source": "PWC CESMP p.26 and Action E.4",
        "note": ("The GHG Protocol REQUIRES dual location- and market-based reporting "
                 "for Scope 2 carbon. Water has no equivalent norm -- which is the "
                 "paper's closing argument."),
    }

    # --- convention 6: long-run marginal. CITED, NOT RECOMPUTED. ------------
    rows["long_run_marginal"] = {
        "label": "Long-run marginal (capacity expansion)",
        "family": "marginal",
        "computable": False,
        "geography": "Virginia + PJM imports",
        "lake_anna_pct_of_scope2": None,
        "why_not_computable": (
            "This requires a capacity-expansion model, which this project does not "
            "have. JLARC commissioned one (Energy + Environmental Economics, E3) and "
            "published its output, so the figure is CITED rather than recomputed."),
        "cited_result": {
            "va_nuclear_twh_2040_unconstrained": 56,
            "va_nuclear_twh_2040_no_new_datacenter": 32,
            "datacenter_attributable_twh": 24,
            "datacenter_attributable_imports_twh_2040": "79 to 92",
            "reading": ("Under E3's model data centers are responsible for the ENTIRE "
                        "projected increase in Virginia nuclear generation (+24 TWh/yr "
                        "by 2040 on a flat 32 TWh baseline) -- and simultaneously for "
                        "+79 to +92 TWh of imports, meaning roughly three-quarters of "
                        "the incremental energy is generated outside Virginia entirely."),
        },
        "source": "JLARC Rpt598 (Dec 2024) Appendix H, Tables H-4 / H-5 / H-6; Table 3-1 p.29",
        "MANDATORY_CAVEAT": (
            "E3's new nuclear is UNSITED and assumed unavailable until 2035 -- "
            "presumably SMRs, NOT North Anna uprates. This quantifies long-run "
            "marginal NUCLEAR, not long-run marginal LAKE ANNA. It must not be "
            "presented as a Lake Anna share."),
    }

    computed = {k: v["lake_anna_pct_of_scope2"] for k, v in rows.items()
                if v.get("computable")}
    lo, hi = min(computed.values()), max(computed.values())

    out = {
        "purpose": ("Which basin bears a data center's electricity-related water, "
                    "under each standard accounting convention. The spread IS the "
                    "result: the physics is identical in every row."),
        "fleet_basis": f"all {len(bs)} buildings, full buildout",
        "scope2_location_based_mgd": round(s2, 2),
        "scope2_marginal_based_mgd": round(s2_marg, 2),
        "conventions": rows,
        "lake_anna_share_range_pct": {"min": round(lo, 2), "max": round(hi, 2),
                                      "spread_factor": round(hi / lo, 1) if lo else None},
        "n_computable": len(computed),
        "n_documented_not_computable": len(rows) - len(computed),
        "headline": (
            f"Across {len(computed)} computable standard conventions, Lake Anna's share "
            f"of the same physical electricity-related water ranges from {lo:.1f}% to "
            f"{hi:.1f}% -- a factor of {hi/lo:.0f}. "
            f"{len(rows)-len(computed)} further conventions are documented but not "
            f"computable from this corpus: market-based (driven to ~0 by contract for "
            f"participants) and long-run marginal (attributes the entire projected "
            f"Virginia nuclear build to this load). Every row describes the same "
            f"physical electricity."),
        "the_ordering_is_the_point": (
            "The computable conventions sort by the GEOGRAPHIC BREADTH of the accounting "
            "boundary, and Lake Anna's share falls monotonically as that boundary widens: "
            "Dominion's Virginia-only fleet 43.32%, the three-state eGRID SERC "
            "Virginia/Carolina subregion 12.16%, the thirteen-state PJM footprint 5.31%. "
            "The mechanism is simple -- a wider boundary admits more non-Virginia nuclear "
            "plants to share the load, and Virginia holds only 23.2% of SRVC nuclear and "
            "11.7% of PJM nuclear. Short-run marginal (0.87%) sits lowest for a different "
            "reason entirely: it is not a boundary question at all, but a causal one -- "
            "nuclear is baseload and almost never the generator that responds to new "
            "demand. So three of the four differ only in where the line is drawn, and the "
            "fourth differs in what question is being asked."),
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print("THE CONVENTION TABLE — Lake Anna share of the SAME physical Scope 2 water\n")
    print(f"{'convention':<46}{'nuclear in mix':>16}{'Lake Anna % of Scope 2':>24}")
    print("-" * 86)
    for k, v in rows.items():
        share = v["lake_anna_pct_of_scope2"]
        nuc = v.get("nuclear_share_of_mix_pct")
        print(f"{v['label'][:45]:<46}"
              f"{(f'{nuc}%' if nuc is not None else '--'):>16}"
              f"{(f'{share:.2f}%' if share is not None else 'not computable'):>24}")
    print()
    print(out["headline"])
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
