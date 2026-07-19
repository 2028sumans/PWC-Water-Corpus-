"""
Where the water actually comes from.

The estimator reports a facility's total footprint. This asks a different
question, and the answer is the most hydrologically interesting thing in the
project: the basins that supply a Prince William data centre are mostly NOT the
basin it sits in.

Scope 1 is drawn locally, from the Occoquan/Potomac headwater streams the
buildings sit on. Scope 2 is consumed at the generating plants, which sit in the
James, York, Roanoke and Rappahannock basins. Since Scope 2 is ~87% of the
total, the great majority of the footprint is displaced out of the county's own
watersheds entirely -- and out of the reach of the county's land-use review,
which is the only body that reviewed these facilities.

Generating-plant basins are assigned from the USGS thermoelectric dataset's own
NAME_OF_WATER_SOURCE field; per-plant consumption shares come from the same
file, so the attribution uses one consistent source.
"""
import csv
import json
from collections import defaultdict

PROFILES = "public/data/facility_profiles.json"
USGS = "data/Version_1.2_2015_TE_Model_Estimates.csv"

# USGS water-source strings mapped to major basin. "Municipality" means the
# plant buys treated water rather than withdrawing directly; the consumption is
# real but the basin is the municipal supplier's, which the dataset does not
# name -- recorded as unresolved rather than guessed.
BASIN_OF_SOURCE = {
    "North Anna River": "York (Lake Anna)",
    "Pamunkey River": "York",
    "Mattaponi River": "York",
    "James River": "James",
    "James River (ECTI)": "James",
    "Appomattox River": "James",
    "Chickahominy River": "James",
    "Roanoke River": "Roanoke",
    "John H Kerr Reservoir": "Roanoke",
    "Rappahannock River": "Rappahannock",
    "Clinch River": "Tennessee/Clinch",
    "New River": "New/Kanawha",
    "Potomac River": "Potomac",
    "Municipality": "unresolved (purchased municipal water)",
    "Wells": "unresolved (groundwater)",
}

FUEL_OF_USGS_TYPE = {"NUCLEAR": "nuclear", "NGCC": "natural_gas_cc", "COAL": "coal"}


def _num(s):
    try:
        return float(str(s).replace(",", ""))
    except (TypeError, ValueError):
        return None


def load_plants():
    rows = list(csv.reader(open(USGS, encoding="latin-1")))
    ix = {c: i for i, c in enumerate(rows[2])}
    out = defaultdict(list)
    for r in rows[3:]:
        if len(r) <= ix["NET_GENERATION"] or r[ix["STATE"]] != "VA":
            continue
        fuel = FUEL_OF_USGS_TYPE.get(r[ix["GENERATION_TYPE"]])
        gen, cons = _num(r[ix["NET_GENERATION"]]), _num(r[ix["CONSUMPTION"]])
        if not fuel or not gen or cons is None:
            continue
        out[fuel].append({
            "plant": r[ix["PLANT_NAME"]],
            "source": r[ix["NAME_OF_WATER_SOURCE"]],
            "basin": BASIN_OF_SOURCE.get(r[ix["NAME_OF_WATER_SOURCE"]], "unclassified"),
            "consumption_mgd": cons,
        })
    return out


def main():
    import indirect_water_footprint as m

    prof = json.load(open(PROFILES))
    bs = [b for b in prof["buildings"] if b.get("scope_water_footprint")]

    # ---- Scope 1: local, by receiving watershed -------------------------------
    local = defaultdict(lambda: {"n": 0, "s1": 0.0, "peak": 0.0, "mw": 0.0, "acres": 0.0})
    s1 = s2 = s3 = 0.0
    for b in bs:
        s = b["scope_water_footprint"]
        s1 += s["scope1_onsite_cooling"]["mgd_central"]
        s2 += s["scope2_electricity"]["mgd_central"]
        s3 += s["scope3_embodied"]["mgd_central"]
        w = (b.get("water_context") or {}).get("watershed_name") or "UNKNOWN"
        a = local[w]
        a["n"] += 1
        a["s1"] += s["scope1_onsite_cooling"]["mgd_central"]
        a["peak"] += s["scope1_onsite_cooling"]["peak_day_mgd"]
        a["mw"] += s["power"]["effective_it_mw_central"]
        a["acres"] = max(a["acres"], (b.get("water_context") or {}).get("watershed_acres") or 0)

    print("SCOPE 1 — drawn locally, by receiving watershed (all Potomac basin)\n")
    print(f"{'watershed':<16}{'bldgs':>6}{'IT MW':>8}{'annual':>9}{'summer peak':>13}"
          f"{'ws acres':>10}{'peak gal/acre/d':>17}")
    print("-" * 80)
    for w, a in sorted(local.items(), key=lambda kv: -kv[1]["s1"]):
        gpa = a["peak"] * 1e6 / a["acres"] if a["acres"] else 0
        print(f"{w:<16}{a['n']:>6}{a['mw']:>8.0f}{a['s1']:>9.3f}{a['peak']:>13.3f}"
              f"{a['acres']:>10,.0f}{gpa:>17,.0f}")

    # ---- Scope 2: displaced, by generating basin ------------------------------
    plants = load_plants()
    mix, cf = m.DOMINION_GENERATION_MIX, m.CONSUMPTION_FACTORS_GAL_PER_MWH
    blended = sum(mix[f] * cf[f] for f in mix)

    by_basin = defaultdict(float)
    for fuel, share_num in ((f, mix[f] * cf[f]) for f in mix):
        if fuel not in plants:
            continue
        fuel_mgd = s2 * share_num / blended
        tot_cons = sum(p["consumption_mgd"] for p in plants[fuel]) or 1
        for p in plants[fuel]:
            by_basin[p["basin"]] += fuel_mgd * p["consumption_mgd"] / tot_cons

    print(f"\n\nSCOPE 2 — consumed at the generating plant, by basin\n")
    print(f"{'basin':<40}{'MGD':>9}{'% of Scope 2':>14}")
    print("-" * 63)
    for b_, v in sorted(by_basin.items(), key=lambda kv: -kv[1]):
        print(f"{b_:<40}{v:>9.2f}{100*v/s2:>13.1f}%")

    # ---- Scope 2 under MARGINAL dispatch, by basin ----------------------------
    # Same plant-level attribution, but weighting fuels by the marginal mix (what
    # a new load turns on) rather than the average mix. Nuclear drops out because
    # it is baseload and ~never marginal, so the York basin nearly empties.
    mmix = m.PJM_MARGINAL_FUEL_MIX
    mcf = m.MARGINAL_CONSUMPTION_FACTORS_GAL_PER_MWH
    mblended = sum(mmix[f] * mcf[f] for f in mmix)
    s2_marginal = sum(
        b["scope_water_footprint"]["scope2_electricity"]["marginal_based"]["mgd_central"]
        for b in bs
    )
    marg_basin = defaultdict(float)
    for fuel in mmix:
        # CC and CT both draw from the gas fleet's plants/basins; CT adds little
        # water but sits in the same basins.
        plant_fuel = "natural_gas_cc" if fuel.startswith("natural_gas") else fuel
        if plant_fuel not in plants:
            continue
        fuel_mgd = s2_marginal * (mmix[fuel] * mcf[fuel]) / mblended
        tot_cons = sum(p["consumption_mgd"] for p in plants[plant_fuel]) or 1
        for p in plants[plant_fuel]:
            marg_basin[p["basin"]] += fuel_mgd * p["consumption_mgd"] / tot_cons

    print(f"\n\nSCOPE 2 under MARGINAL dispatch (a new load turns on gas, not nuclear)\n")
    print(f"{'basin':<40}{'avg MGD':>10}{'marginal MGD':>14}")
    print("-" * 64)
    allb = sorted(set(by_basin) | set(marg_basin),
                  key=lambda k: -(by_basin.get(k, 0) + marg_basin.get(k, 0)))
    for b_ in allb:
        print(f"{b_:<40}{by_basin.get(b_,0):>10.2f}{marg_basin.get(b_,0):>14.2f}")
    york_avg = by_basin.get("York (Lake Anna)", 0.0)
    york_marg = marg_basin.get("York (Lake Anna)", 0.0)
    print(f"\n  York basin (North Anna): {york_avg:.2f} MGD average  ->  {york_marg:.2f} MGD marginal")
    print(f"  i.e. {1-york_marg/york_avg:.0%} of the Lake Anna attribution is an average-mix artifact;")
    print(f"  the water a NEW data centre actually causes is consumed in the James gas fleet.")

    # ---- the displacement ------------------------------------------------------
    total = s1 + s2 + s3
    potomac = s1 + by_basin.get("Potomac", 0.0)
    print(f"\n\nBASIN DISPLACEMENT\n")
    print(f"  total footprint                     {total:>7.2f} MGD")
    print(f"  consumed in the Potomac basin       {potomac:>7.2f} MGD  ({100*potomac/total:>4.1f}%)")
    print(f"  consumed in OTHER basins            {s2 - by_basin.get('Potomac', 0.0):>7.2f} MGD  "
          f"({100*(s2-by_basin.get('Potomac',0.0))/total:>4.1f}%)")
    print(f"  Scope 3, basin not locatable        {s3:>7.2f} MGD  ({100*s3/total:>4.1f}%)")
    york = by_basin.get("York (Lake Anna)", 0.0)
    print(f"\n  North Anna alone (York basin)       {york:>7.2f} MGD"
          f"  = {york/s1:.1f}x the entire local Scope 1")
    peak = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["peak_day_mgd"] for b in bs)
    print(f"  summer peak, local draw             {peak:>7.2f} MGD  = {peak/s1:.1f}x annual average")

    json.dump({"scope1_by_watershed": {k: dict(v) for k, v in local.items()},
               "scope2_by_generating_basin": dict(by_basin),
               "scope2_marginal_by_generating_basin": dict(marg_basin),
               "scope2_marginal_total_mgd": s2_marginal,
               "totals_mgd": {"scope1": s1, "scope2": s2, "scope3": s3, "total": total},
               "summer_peak_local_mgd": peak},
              open("data/basin_attribution.json", "w"), indent=1)
    print("\nwrote data/basin_attribution.json")


if __name__ == "__main__":
    main()
