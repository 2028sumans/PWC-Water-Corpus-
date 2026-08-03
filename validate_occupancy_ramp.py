"""Validate the fit-out ramp against two independent top-down anchors.

Until now every check on this model tested distributional SHAPE (the JLARC
per-building water distribution, the ICPRB on-site scope). None tested the
LEVEL. Two external sources give a level, and both are derived independently of
our floor-area ladder:

  JLARC Rpt598 (Dec 2024), Ch.1 p.5 + Table B-1 p.102
      Virginia data centers use ~5,050 MW, from the 2024 peak-load forecasts of
      Dominion and the Mecklenburg / Northern Virginia / Rappahannock co-ops
      (made Aug 2023). Loudoun is "approximately half" of the state. Loudoun's
      market is "three times larger than Prince William's" -- corroborated by
      JLARC's own site counts, Loudoun 71 vs Prince William 24 (ratio 2.96).
      => Prince William ~= 5050 * 0.5 / 3 ~= 842 MW, as of 2024.

  ICPRB "Data Centers and Water Use in the Potomac River Basin" (March 2026)
      "over 290 individual buildings" in the basin, "total power demand
      (estimated at about 5,400 MW) and total floor space (estimated at
      56 million square feet)". => 10,370 sqft/MW basin-wide.

The JLARC anchor is a 2024 quantity. Twenty of our 54 occupied buildings
received their Certificate of Occupancy after that snapshot, so comparing our
2026 fleet against it is not like-for-like. This script rebuilds the fleet
as-of an arbitrary date and reports both the raw and ramped comparison.

Run: /Library/Frameworks/Python.framework/Versions/3.13/bin/python3 validate_occupancy_ramp.py
"""
import datetime
import json

from indirect_water_footprint import (
    RAMP_YEARS_CENTRAL, RAMP_YEARS_FAST, RAMP_YEARS_SLOW,
    SQFT_PER_EFFECTIVE_MW, occupancy_ramp,
)

PROFILES = "public/data/facility_profiles.json"

# --- anchors -------------------------------------------------------------
JLARC_VA_MW = 5050.0
JLARC_LOUDOUN_SHARE = 0.5
JLARC_LOUDOUN_OVER_PWC = 3.0
JLARC_PWC_MW = JLARC_VA_MW * JLARC_LOUDOUN_SHARE / JLARC_LOUDOUN_OVER_PWC
JLARC_AS_OF = datetime.date(2024, 7, 1)

ICPRB_BASIN_MW = 5400.0
ICPRB_BASIN_SQFT = 56_000_000.0

# Facility load = IT load x PUE. The shipped PUE band is 1.3-1.55 for standard
# vintage; 1.25 is used here as a deliberately conservative multiplier so the
# comparison cannot be flattered by a high PUE assumption.
PUE_FOR_SITE_LOAD = 1.25


def load():
    prof = json.load(open(PROFILES))["buildings"]
    out = []
    for b in prof:
        sw = b.get("scope_water_footprint") or {}
        p = sw.get("power") or {}
        r = p.get("ramp") or {}
        if not r.get("applied"):
            continue
        out.append({
            "id": b["id"],
            "installed": p["installed_it_mw_central"],
            "occ": datetime.date.fromisoformat(r["occupancy_date"]),
        })
    return out


def fleet_as_of(rows, as_of, ramp_years=RAMP_YEARS_CENTRAL):
    """Installed and ramped IT MW for buildings occupied on or before as_of."""
    inst = ramped = 0.0
    n = 0
    for r in rows:
        if r["occ"] > as_of:
            continue
        age = (as_of - r["occ"]).days / 365.25
        inst += r["installed"]
        ramped += r["installed"] * occupancy_ramp(age, ramp_years)
        n += 1
    return n, inst, ramped


def main():
    rows = load()
    today = datetime.date.today()
    ok = True

    print("=" * 72)
    print("FIT-OUT RAMP VALIDATION")
    print("=" * 72)
    print(f"occupied buildings in model: {len(rows)}")
    print(f"ramp: linear to full load over {RAMP_YEARS_CENTRAL:g} y "
          f"(range {RAMP_YEARS_FAST:g}-{RAMP_YEARS_SLOW:g} y)")
    print()

    # --- 1. vintage-matched comparison against JLARC ---------------------
    n, inst, ramped = fleet_as_of(rows, JLARC_AS_OF)
    raw_site = inst * PUE_FOR_SITE_LOAD
    ramp_site = ramped * PUE_FOR_SITE_LOAD
    print(f"[1] JLARC anchor, vintage-matched at {JLARC_AS_OF}")
    print(f"    JLARC-implied Prince William load : {JLARC_PWC_MW:7.1f} MW")
    print(f"    our buildings occupied by then    : {n}")
    print(f"    unramped (installed x PUE)        : {raw_site:7.1f} MW  "
          f"= {raw_site / JLARC_PWC_MW:.2f}x anchor")
    print(f"    ramped   (energized x PUE)        : {ramp_site:7.1f} MW  "
          f"= {ramp_site / JLARC_PWC_MW:.2f}x anchor")
    ratio = ramp_site / JLARC_PWC_MW
    good = 0.70 <= ratio <= 1.40
    ok &= good
    print(f"    -> ramped estimate within 0.70-1.40x of an independent "
          f"utility-forecast anchor: {good}")
    if not good:
        print("       FAIL: the ramp does not reconcile the level.")
    print()

    # --- 2. the ramp must move the level in the right direction ----------
    improved = abs(ramp_site - JLARC_PWC_MW) < abs(raw_site - JLARC_PWC_MW)
    ok &= improved
    print(f"[2] ramp reduces the gap to the anchor rather than widening it: {improved}")
    print()

    # --- 3. present-day fleet -------------------------------------------
    n_now, inst_now, ramped_now = fleet_as_of(rows, today)
    print(f"[3] present day ({today})")
    print(f"    occupied buildings                : {n_now}")
    print(f"    installed IT                      : {inst_now:7.1f} MW")
    print(f"    energized IT (ramped)             : {ramped_now:7.1f} MW  "
          f"({ramped_now / inst_now * 100:.0f}% of installed)")
    print(f"    implied site load                 : {ramped_now * PUE_FOR_SITE_LOAD:7.1f} MW")
    print()

    # --- 4. ICPRB basin plausibility ------------------------------------
    # Prince William cannot be an implausible share of the whole Potomac basin,
    # which ICPRB says is "predominantly located within Loudoun County".
    share_raw = inst_now * PUE_FOR_SITE_LOAD / ICPRB_BASIN_MW
    share_ramp = ramped_now * PUE_FOR_SITE_LOAD / ICPRB_BASIN_MW
    print(f"[4] ICPRB basin plausibility (basin = {ICPRB_BASIN_MW:,.0f} MW, March 2026)")
    print(f"    PWC share of basin, unramped      : {share_raw * 100:5.1f}%")
    print(f"    PWC share of basin, ramped        : {share_ramp * 100:5.1f}%")
    plausible = share_ramp < 0.25
    ok &= plausible
    print(f"    -> under 25%, consistent with ICPRB's 'predominantly Loudoun': "
          f"{plausible}")
    print()

    # --- 5. density cross-check -----------------------------------------
    # ICPRB's own basin figures imply a floor-area-to-power density. Ours must
    # be in the same neighbourhood or the ladder itself is wrong.
    icprb_density = ICPRB_BASIN_SQFT / ICPRB_BASIN_MW
    rel = abs(SQFT_PER_EFFECTIVE_MW - icprb_density) / icprb_density
    close = rel < 0.30
    ok &= close
    print(f"[5] density bridge vs ICPRB basin-wide")
    print(f"    ICPRB implied     : {icprb_density:8,.0f} sqft/MW")
    print(f"    ours              : {SQFT_PER_EFFECTIVE_MW:8,.0f} sqft/MW")
    print(f"    -> within 30% ({rel * 100:.0f}%): {close}")
    print()

    # --- 6. shares must be invariant to the ramp -------------------------
    # The ramp multiplies IT power, and every scope is proportional to IT power,
    # so it must not move any reported share. This is the guarantee that lets
    # the abstract keep its share claims while the volumes change.
    prof = json.load(open(PROFILES))["buildings"]
    comp = [b for b in prof if b.get("status") in ("Completed", "Finaled")]
    def shares(S, unramp):
        s1 = s2 = s3 = 0.0
        for b in S:
            sw = b["scope_water_footprint"]
            f = 1.0
            if unramp:
                r = sw["power"]["ramp"]["energized_fraction_central"]
                f = 1.0 / r if r > 0 else 0.0
            s1 += sw["scope1_onsite_cooling"]["mgd_central"] * f
            s2 += sw["scope2_electricity"]["mgd_central"] * f
            s3 += sw["scope3_embodied"]["mgd_central"] * f
        t = s1 + s2 + s3
        return s2 / t, s1 / t
    live = [b for b in comp
            if b["scope_water_footprint"]["power"]["ramp"]["energized_fraction_central"] > 0]
    s2r, s1r = shares(live, False)
    s2u, s1u = shares(live, True)
    inv = abs(s2r - s2u) < 5e-3 and abs(s1r - s1u) < 5e-3
    ok &= inv
    print(f"[6] share invariance under the ramp")
    print(f"    Scope 2 share  ramped {s2r * 100:.2f}%  unramped {s2u * 100:.2f}%")
    print(f"    on-site share  ramped {s1r * 100:.2f}%  unramped {s1u * 100:.2f}%")
    print(f"    -> ramp moves volumes, not shares: {inv}")
    print()

    print("=" * 72)
    print("PASS" if ok else "FAIL")
    print("=" * 72)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
