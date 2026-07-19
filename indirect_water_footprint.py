"""
Facility-level Scope 1/2/3 water footprint estimator, calibrated on measured
Prince William County utility data.

WHY THIS WAS REBUILT (v2)
-------------------------
The first version of this module estimated Scope 1 from the full published
Water Usage Effectiveness envelope (0.0-2.4 L/kWh) applied to a power figure
derived from rack-density benchmarks (100-450 W/sqft). Both inputs were
defensible in isolation and catastrophically wrong in combination:

  - A WUE floor of exactly 0.0 makes every lower bound meaningless.
  - 100-450 W/sqft is a WHITE-SPACE / rack density. Applied to GROSS floor
    area (which is roughly half white space, plus mechanical/electrical/
    shell) it overstates power by ~2-4x.
  - The resulting county-wide total was 151.8-2132.3 MGD. JLARC measured the
    ENTIRE Virginia data center industry at 2.1 billion gal/yr = 5.75 MGD in
    2023. The model was off by up to two orders of magnitude, and its median
    facility range spanned 16x.

This version replaces the literature-envelope approach with the empirical,
region-specific relationship ICPRB derived from actual utility billing
records in the Loudoun Water, Fairfax Water, and PRINCE WILLIAM WATER service
areas, cross-referenced against per-facility power capacity from the JLARC /
VADEQ air-permit database.

VALIDATION -- WITHDRAWN, IT WAS CIRCULAR
----------------------------------------
This module used to claim the following check:

    11,094,472 sqft / 8,818 sqft per effective MW = 1,258 effective IT MW
      x 309 gal/MW/day (PWC observed WUP)          = 0.389 MGD
    versus Prince William Water's reported 0.42 MGD -> within 7.4%

That is not a validation. ICPRB derived 309 BY DIVIDING that same 0.42 MGD by
its own generator-derived estimate of effective power demand (WMA study p.6-13:
"WUP was then calculated by dividing utility reported data center water use by
effective power demand"). So 309 := 0.42e6 / 1,359 MW, and substituting it back:

    (1,258 x 0.42e6 / 1,359) / 0.42e6  ==  1,258 / 1,359

The water figure cancels. The check reduces to comparing this module's
GFA-derived power estimate against ICPRB's generator-derived one -- and returns
-7.4% either way, which is the tell. It tests the POWER SPINE, not water use,
and it does so against a WATER UTILITY SERVICE AREA whose boundary is not the
county.

A genuine validation is possible but must avoid 309 entirely: take per-facility
generator capacity from VADEQ air permits, run ICPRB's Equation 6-3, apply a
cooling-type WUP from the physical tiers (150 air-cooled / 1,577 fully
evaporative), sum bottom-up, and compare to the 0.42 MGD. Nothing cancels in
that chain, and it doubles as a falsifiable test of the cooling-type
assignments. See METHODOLOGY.md section 7.

THE DIRECTION PROBLEM WITH 8,818
--------------------------------
ICPRB never derives megawatts from floor area. Equation 6-3 is:

    Effective (IT) Power Demand
        = Total Generator Power Capacity x Redundancy (0.5) x Utilization (0.8)

with power taken from backup generator capacity in VADEQ air permits. The 8,818
sqft/MW figure appears once, as a unit bridge used to convert Loudoun Water's
0.017 gal/day/sqft into the 150 gal/MW/day air-cooled tier (0.017 x 8,818 =
149.9). This module runs that bridge BACKWARD, which no source validates.

For air-cooled facilities the round trip cancels -- (GFA/8,818) x 150 is
identically GFA x 0.017 -- so the megawatt figure does no work. For every other
tier, and for all of Scope 2, the constant does real unvalidated predictive work,
and it is now the single largest swing factor in the model (64%; see
sensitivity_analysis.py). ICPRB's own Fairfax figures imply 12,722 sqft/MW, 44%
higher and outside this module's +/-25% tolerance.

THE GFA BUG THIS ALSO FIXES
---------------------------
Data_Center_Buildings.geojson carries a GFASource field that the previous
version ignored. When GFASource == "Proffer", the GFA column holds the
SITE-WIDE PROFFERED ENTITLEMENT, repeated identically on every building
record on that site -- e.g. 1,132,540 sqft appears on all four Amazon AWS
IAD-10x buildings AND both DLR IAD-5x buildings. Coalescing GFA first meant
153 of 202 buildings inherited a campus entitlement as their own floor area,
inflating the county total to 87.5M sqft. BPGFA (building-permit GFA) and
REATaxedGFA (assessed) are genuinely per-building. Corrected resolution
order is assessed -> permit -> estimated -> proffer-split; see resolve_gfa().

SCOPE DEFINITIONS (unchanged)
-----------------------------
  Scope 1 - water evaporated on site, mostly by cooling towers / adiabatic
    humidification. Now estimated as effective IT power x a measured
    gal/MW/day intensity rather than a WUE envelope.
  Scope 2 - water consumed at the power plants generating the facility's
    electricity. Dominion generation-mix-blended consumption factor.
  Scope 3 - embodied/supply-chain water. Still a proportional anchor; no
    facility-specific data exists.

CITATIONS
---------
  - Water Use per Unit of Power (WUP) tiers, the 8,818 sqft/effective-MW
    infrastructure density, the 0.75 consumptive-use factor, and the
    redundancy (0.5) / utilization (0.8) factors used to convert permitted
    generator capacity to effective load: ICPRB, "2025 Washington
    Metropolitan Area Water Supply Study" (December 2025), Section 6.2 and
    Table 6-5; and ICPRB, "Data Centers and Water Use in the Potomac River
    Basin" (March 2026). WUP values are derived from utility-reported water
    use in the Loudoun Water, Fairfax Water, and Prince William Water
    service areas divided by effective power demand from the JLARC/VADEQ
    air-permit database.
  - Measured per-building and industry-wide water use benchmarks: JLARC,
    "Data Centers in Virginia" (Report 598, December 2024), Chapter 5,
    based on data provided by the water utilities serving Fairfax, Henrico,
    Loudoun, Mecklenburg, and Prince William counties.
  - Operator-published WUE: Amazon 2025 sustainability reporting
    (0.12 L/kWh global, and a reported 42% year-over-year reduction in
    Northern Virginia); Microsoft datacenter sustainability reporting
    (0.27 L/kWh). Industry-average 0.84 L/kWh academic estimate as cited by
    Amazon.
  - Generation-technology water consumption factors: Macknick, J. et al.,
    NREL/TP-6A20-50900 (2011). Dominion Energy Virginia 2025 generation mix
    (58% gas / 25% nuclear / 14% renewable / 3% coal) per EIA and Dominion
    reporting.
  - PUE ranges: hyperscaler fleet disclosures (2023-2025) vs. Uptime
    Institute global survey.
  - Scope 3 proportional anchor and the >99% embodied-water outlier:
    Privette et al., AGU Advances (2026).
"""

# ---------------------------------------------------------------------------
# ICPRB empirical constants (Section 6.2, Table 6-5)
# ---------------------------------------------------------------------------

# Infrastructure density: gross floor area per unit of EFFECTIVE power demand.
# Derived by ICPRB from the JLARC/VADEQ database across the Virginia fleet.
SQFT_PER_EFFECTIVE_MW = 8818

# Water Use per Unit of Power, gallons/day per effective MW.
WUP_GAL_PER_MW_DAY = {
    "air_cooled": 150,          # closed-loop / dry / air-cooled floor
    "pwc_observed": 309,        # Prince William Water actual, 2023 fleet average
    "loudoun_observed": 1006,   # Loudoun Water actual, 2024 fleet average
    "basin_medium": 800,        # ICPRB representative basin-wide average
    "fully_water_cooled": 1577, # implied 100%-evaporative ceiling
}

# Peak-day intensities. Summer peak is dramatically higher than annual mean --
# in PWC the observed ratio is nearly 10x, which is the single most important
# operational fact about data center water demand in this county.
WUP_PEAK_GAL_PER_MW_DAY = {
    "pwc_observed": 3060,       # Prince William Water actual peak day, 2023
    "loudoun_observed": 2716,
    "basin_medium": 2900,
    "fully_water_cooled": 5200,
}

# Fraction of delivered water that is consumptively lost (evaporated, not
# returned to the basin). ICPRB applies 0.75 uniformly based on utility data.
CONSUMPTIVE_USE_FACTOR = 0.75

# Measured reference points from JLARC Report 598 (2023 data), used as an
# independent plausibility check rather than as model inputs.
JLARC_BENCHMARKS_MGD = {
    "typical_building": 6.7e6 / 365 / 1e6,    # 0.018 MGD - an average large office building
    "large_building_threshold": 50e6 / 365 / 1e6,  # 0.137 MGD - 11 VA buildings exceeded this
    "largest_va_building": 243e6 / 365 / 1e6,  # 0.666 MGD - single largest in Virginia
    "entire_va_industry": 2.1e9 / 365 / 1e6,   # 5.75 MGD - ALL Virginia data centers
    "pwc_water_reported_avg": 0.42,            # PWC Water service area, 2023
    "pwc_water_reported_peak": 4.2,
}

GAL_PER_LITER = 0.264172
HOURS_PER_DAY = 24

# Operators with a public, specific commitment to closed-loop / air-cooled /
# zero-evaporation cooling in their newer builds. This is deliberately NOT the
# operators' headline global WUE number: a global fleet WUE (e.g. Amazon's
# 0.12 L/kWh) is measured over every region including hot/dry sites and uses a
# different accounting boundary than ICPRB's Prince William-calibrated, per-
# effective-MW WUP scale -- converting one to the other produces figures that
# disagree with the locally-validated calibration and, perversely, make the
# most efficient operators look thirstier. Instead we map a credible cooling
# COMMITMENT onto ICPRB's own measured air-cooled tier, which keeps every
# number on one validated scale and narrows Scope 1 in the correct direction.
OPERATOR_CLOSED_LOOP_COMMITMENT = {
    "AMAZON": "Amazon/AWS reports deploying closed-loop, direct-to-chip cold-plate cooling that adds no evaporative water on new AI infrastructure, and a 42% year-over-year water reduction in its Northern Virginia region (2025 sustainability reporting). Global fleet WUE 0.12 L/kWh.",
    "AWS": "Amazon/AWS reports deploying closed-loop, direct-to-chip cold-plate cooling that adds no evaporative water on new AI infrastructure, and a 42% year-over-year water reduction in its Northern Virginia region (2025 sustainability reporting). Global fleet WUE 0.12 L/kWh.",
    "MICROSOFT": "Microsoft reports deploying closed-loop, zero-water-evaporation cooling on new builds (datacenter sustainability reporting, Dec 2025). Global fleet WUE 0.27 L/kWh.",
}

# ---------------------------------------------------------------------------
# Scope 2 - grid consumption intensity (unchanged; mix independently verified)
# ---------------------------------------------------------------------------
# Consumption factors are VIRGINIA-SPECIFIC, computed from USGS plant-level
# model estimates rather than national medians. See derive_va_consumption_factors()
# in usgs_va_factors.py for the derivation; values are generation-weighted across
# every Virginia plant of that type in the USGS 2015 (v1.2, July 2024) release.
#
# The nuclear figure is the correction that mattered most. The previous value of
# 700 gal/MWh was a national median that blended two Virginia plants with opposite
# water profiles:
#
#   Surry (EIA 3806)      once-through saline, James River estuary
#                         consumption 0.0 Mgal/d ->     0 gal/MWh
#   North Anna (EIA 6168) "complex" -- Lake Anna cooling reservoir
#                         consumption 18.6 Mgal/d ->  417 gal/MWh
#
# Generation-weighted across the two: 242 gal/MWh, 65% below the national median.
# Surry consumes no water in USGS's model because heat is discharged to a large
# tidal estuary; its 1,220 Mgal/d WITHDRAWAL is enormous but non-consumptive, and
# is saline rather than fresh. That distinction is invisible in a single blended
# national constant and is the whole reason this fix moves the answer so much.
CONSUMPTION_FACTORS_GAL_PER_MWH = {
    "natural_gas_cc": 213,   # VA NGCC fleet, 11.2M MWh
    "nuclear": 242,          # VA nuclear fleet (Surry + North Anna), 28.1M MWh
    "coal": 451,             # VA coal fleet, 7.2M MWh
    "renewable": 0,          # see RENEWABLE_FACTOR_CAVEAT
}

# Low/high bounds from USGS MIN_CONSUMPTION / MAX_CONSUMPTION, same weighting.
CONSUMPTION_FACTOR_BOUNDS_GAL_PER_MWH = {
    "natural_gas_cc": (210, 225),
    "nuclear": (189, 289),
    "coal": (440, 474),
    "renewable": (0, 0),
}

# The national medians this replaced (Macknick et al., NREL/TP-6A20-50900, 2011),
# retained so the size of the correction stays visible.
NREL_NATIONAL_FACTORS_GAL_PER_MWH = {
    "natural_gas_cc": 210,
    "nuclear": 700,
    "coal": 687,
    "renewable": 0,
}

RENEWABLE_FACTOR_CAVEAT = (
    "Renewables are carried at 0 gal/MWh. This is a floor, not a measurement: "
    "hydroelectric reservoirs have very large evaporative consumption in NREL's own "
    "tables, and solar requires panel washing. Dominion's 14% renewable share is "
    "predominantly solar, but any hydro within it is understated here."
)

DOMINION_GENERATION_MIX = {
    "natural_gas_cc": 0.58,
    "nuclear": 0.25,
    "renewable": 0.14,
    "coal": 0.03,
}

BLENDED_CONSUMPTION_GAL_PER_MWH = sum(
    DOMINION_GENERATION_MIX[f] * CONSUMPTION_FACTORS_GAL_PER_MWH[f]
    for f in DOMINION_GENERATION_MIX
)  # ~317 gal/MWh

# ---------------------------------------------------------------------------
# PUE -- second-largest swing factor after the density bridge (29%)
# ---------------------------------------------------------------------------
# Anchors:
#   Uptime Institute 2025 Global Data Center Survey -- industry weighted average
#   annual PUE of 1.54, essentially flat for six consecutive years. That figure
#   spans the whole installed base including legacy stock, so it is a ceiling
#   for new construction rather than a typical value for it.
#
#   Operator-disclosed fleet averages (2024-2025 sustainability reporting):
#   Meta 1.08, Google 1.09, AWS 1.14, Microsoft 1.16.
#
# A disclosed fleet PUE is a global average across every climate the operator
# runs in, so it is applied with a band rather than as a point value. It is
# still far better evidence than a vintage guess: it is the operator's own
# measured number, on the same metric definition.
OPERATOR_DISCLOSED_PUE = {
    "META": (1.08, "Meta 2024 fleet average PUE 1.08"),
    "FACEBOOK": (1.08, "Meta 2024 fleet average PUE 1.08"),
    "GOOGLE": (1.09, "Google 2024 global fleet average PUE 1.09"),
    "AMAZON": (1.14, "AWS 2025 global average PUE 1.14 (1.15 in 2024)"),
    "AWS": (1.14, "AWS 2025 global average PUE 1.14 (1.15 in 2024)"),
    "MICROSOFT": (1.16, "Microsoft 2024 global average PUE 1.16"),
}
# Spread applied around a disclosed fleet average, for site-versus-fleet
# variation. Operators' best sites run ~0.05-0.10 below their fleet mean
# (AWS best 1.04 vs fleet 1.14), so this is deliberately symmetric and modest.
DISCLOSED_PUE_TOLERANCE = 0.06

PUE_RANGE = {
    # An UNBUILT building is not of unknown vintage -- it is being built now, to
    # current design practice. Treating Planned / Under Construction / Pending
    # facilities as "unknown" applied a 1.10-1.50 band to 147 buildings whose
    # only real uncertainty is which operator standard they will meet. This band
    # sits between hyperscaler best practice and the Uptime industry average.
    "new_build": (1.15, 1.35),
    "modern": (1.15, 1.40),       # completed 2020+
    "standard": (1.30, 1.55),     # completed 2010-2019
    "legacy": (1.45, 1.80),       # completed pre-2010
    "unknown": (1.15, 1.54),      # no vintage and no status -- floor to Uptime average
}

# ---------------------------------------------------------------------------
# Scope 3 - embodied / supply-chain (proportional anchor)
# ---------------------------------------------------------------------------
SCOPE3_PROPORTIONAL_RANGE = (0.05, 0.15)

SCOPE3_OUTLIER_NOTE = (
    "At least one hyperscale operator has disclosed embodied/supply-chain water "
    "exceeding 99% of its total corporate water footprint (Privette et al., AGU "
    "Advances, 2026) -- that figure reflects a company-wide accounting boundary "
    "choice, not a physical per-facility ratio. It is flagged as evidence the "
    "5-15% anchor is a floor, not a ceiling."
)


# ---------------------------------------------------------------------------
# GFA resolution -- fixes the proffer-entitlement bug described in the header
# ---------------------------------------------------------------------------
def _num(v):
    try:
        v = float(v)
        return v if v > 0 else None
    except (TypeError, ValueError):
        return None


def resolve_gfa(props: dict, proffer_group_sizes: dict | None = None):
    """
    Resolve a genuine PER-BUILDING gross floor area.

    Returns (sqft, field_used, quality) where quality is one of:
      assessed      - REATaxedGFA, the real-estate-assessed floor area
      permit        - BPGFA, the building-permit floor area
      estimated     - GFA where GFASource is not a proffer
      proffer_split - a site-wide proffered entitlement divided by the number
                      of buildings sharing that identical entitlement figure
    """
    v = _num(props.get("REATaxedGFA"))
    if v:
        return v, "REATaxedGFA", "assessed"
    v = _num(props.get("BPGFA"))
    if v:
        return v, "BPGFA", "permit"

    src = (props.get("GFASource") or "").strip().lower()
    g = _num(props.get("GFA"))
    if g and not src.startswith("proffer"):
        return g, "GFA", "estimated"
    if g and src.startswith("proffer"):
        n = (proffer_group_sizes or {}).get(g, 1)
        return g / n, f"GFA/proffer-split({n})", "proffer_split"
    return None, None, None


def build_proffer_group_sizes(all_props) -> dict:
    """Count how many building records share each identical proffer GFA value,
    so a site entitlement can be split evenly across its buildings."""
    sizes: dict = {}
    for p in all_props:
        src = (p.get("GFASource") or "").strip().lower()
        g = _num(p.get("GFA"))
        if g and src.startswith("proffer"):
            sizes[g] = sizes.get(g, 0) + 1
    return sizes


# ---------------------------------------------------------------------------
# Power
# ---------------------------------------------------------------------------
# Facility-to-facility variation around the fleet-average density. ICPRB
# publishes 8,818 as a single figure; individual buildings vary with rack
# density and mechanical layout. +/-25% is applied to avoid presenting a
# fleet average as a facility-specific certainty.
DENSITY_TOLERANCE = 0.25


def effective_power_from_gfa(gfa_sqft):
    """Effective IT power (MW) from gross floor area, via ICPRB's measured
    infrastructure density. Returns (central, lo, hi)."""
    if not gfa_sqft or gfa_sqft <= 0:
        return None
    central = gfa_sqft / SQFT_PER_EFFECTIVE_MW
    lo = gfa_sqft / (SQFT_PER_EFFECTIVE_MW * (1 + DENSITY_TOLERANCE))
    hi = gfa_sqft / (SQFT_PER_EFFECTIVE_MW * (1 - DENSITY_TOLERANCE))
    return round(central, 1), round(lo, 1), round(hi, 1)


# Uncertainty on permit-derived power comes from ICPRB's own conversion factors
# rather than from floor area. Equation 6-3 applies redundancy 0.5 and
# utilization 0.8 (product 0.40); plausible spans of 0.4-0.6 and 0.7-0.9 give a
# product of 0.28-0.54, i.e. -30%/+35% about the central value.
PERMIT_FACTOR_CENTRAL = 0.5 * 0.8
PERMIT_FACTOR_LOW = 0.4 * 0.7
PERMIT_FACTOR_HIGH = 0.6 * 0.9


def effective_power_from_permit(site_generator_mw, gfa_share):
    """Effective IT power (MW) for one building from its site's permitted
    generator capacity.

    site_generator_mw -- total nameplate generator capacity on the permit
    gfa_share         -- this building's share of the site's floor area

    Floor area is used ONLY to apportion a measured site total between the
    buildings that share the permit. That is a far weaker use of GFA than the
    density bridge makes of it: an error in floor area rescales one building
    against its neighbours, rather than generating the site's power from
    scratch.
    """
    if not site_generator_mw or not gfa_share:
        return None
    base = site_generator_mw * gfa_share
    return (round(base * PERMIT_FACTOR_CENTRAL, 1),
            round(base * PERMIT_FACTOR_LOW, 1),
            round(base * PERMIT_FACTOR_HIGH, 1))


# Interconnection-queue operator ranges. Retained ONLY as a cross-check --
# these are portfolio-wide spans, not building-specific, and are no longer
# allowed to widen a GFA-derived estimate.
OPERATOR_MW_RANGES = {
    "AMAZON": (50, 250), "AWS": (50, 250), "CLOUDHQ": (10, 250), "CLOUD HQ": (10, 250),
    "IRON MOUNTAIN": (100, 250), "QTS": (250, 400), "STACK": (25, 100), "NTT": (100, 250),
    "EQUINIX": (1, 25), "CORPORATE OFFICE PROPERTIES": (100, 250), "DIGITAL REALTY": (10, 25),
    "DLR": (10, 25), "VERIZON": (10, 25), "COMCAST": (1, 50), "OATH": (1, 50),
    "MICROSOFT": (25, 50), "GAINESVILLE CROSSING": (250, 400), "CORSCALE": (250, 400),
}


def match_operator(name: str):
    if not name:
        return None
    upper = name.upper()
    for kw in sorted(OPERATOR_MW_RANGES.keys(), key=len, reverse=True):
        if kw in upper:
            return kw, OPERATOR_MW_RANGES[kw]
    return None


def match_operator_commitment(name: str):
    """Return (operator, source_note) if this operator has a public
    closed-loop / air-cooled cooling commitment."""
    if not name:
        return None
    upper = name.upper()
    for kw in sorted(OPERATOR_CLOSED_LOOP_COMMITMENT.keys(), key=len, reverse=True):
        if kw in upper:
            return kw, OPERATOR_CLOSED_LOOP_COMMITMENT[kw]
    return None


UNBUILT_STATUSES = ("planned", "under construction", "pending")


def _vintage_class(year_built, status=None):
    """Classify a building for PUE purposes.

    Status is consulted before vintage, because an unbuilt facility has no year
    built and that absence is not ignorance -- it means the building is going up
    now, to current practice.
    """
    if year_built is None:
        if status and status.strip().lower() in UNBUILT_STATUSES:
            return "new_build"
        return "unknown"
    if year_built >= 2020:
        return "modern"
    if year_built >= 2010:
        return "standard"
    return "legacy"


def match_disclosed_pue(name):
    """Return (pue, source_note) if this building's operator publishes a fleet
    PUE, else None."""
    if not name:
        return None
    upper = name.upper()
    for kw in sorted(OPERATOR_DISCLOSED_PUE.keys(), key=len, reverse=True):
        if kw in upper:
            return OPERATOR_DISCLOSED_PUE[kw]
    return None


# ---------------------------------------------------------------------------
# Scope 1 - on-site cooling, from measured WUP intensities
# ---------------------------------------------------------------------------
def scope1_onsite_cooling(eff_mw, eff_lo, eff_hi, operator_commitment=None, cooling_disclosure=None):
    """
    Scope 1 from effective IT power x measured gal/MW/day intensity, all on
    ICPRB's Prince William-calibrated scale.

    Narrowing precedence, best evidence first (both narrow toward the measured
    AIR-COOLED tier -- the efficient direction -- rather than substituting an
    off-scale external number):
      1. cooling_disclosure -- a binding permit/proffer condition prohibiting
         water-cooled systems pins this to the air-cooled tier.
      2. operator_commitment -- a public closed-loop/air-cooled commitment from
         the operator narrows the range to air-cooled..PWC-observed.
      3. otherwise -- the full measured technology envelope, air-cooled (150)
         to fully water-cooled (1,577), with the Prince William Water observed
         fleet average (309) as the central estimate.
    """
    air = WUP_GAL_PER_MW_DAY["air_cooled"]
    water = WUP_GAL_PER_MW_DAY["fully_water_cooled"]
    pwc = WUP_GAL_PER_MW_DAY["pwc_observed"]

    basis = "technology_envelope"
    narrowed_by = None
    wup_lo, wup_hi, wup_central = air, water, pwc

    if cooling_disclosure and cooling_disclosure.get("evaporative"):
        # Evidence that the facility IS water-cooled -- cooling towers listed as
        # permitted equipment in its VADEQ air permit.
        #
        # Until this path existed the model was ASYMMETRIC: it could narrow a
        # facility down toward the air-cooled floor on an operator commitment,
        # but had no way to represent evidence pointing the other way, so every
        # facility was implicitly presumed no-worse-than-average. Confirmed
        # evaporative cooling now lifts the floor off the air-cooled tier and
        # centres the estimate on ICPRB's basin-representative intensity.
        wup_lo, wup_hi, wup_central = pwc, water, WUP_GAL_PER_MW_DAY["basin_medium"]
        basis = "disclosed_cooling_evaporative"
        narrowed_by = cooling_disclosure.get("source")
    elif cooling_disclosure and cooling_disclosure.get("air_or_closed_loop"):
        # Binding: water-cooled prohibited -> air-cooled tier.
        wup_lo, wup_hi, wup_central = air, round(air * 1.5), air
        basis = "disclosed_cooling"
        narrowed_by = cooling_disclosure.get("source")
    elif operator_commitment:
        op, note = operator_commitment
        # Operator commits to closed-loop/air cooling on newer builds; narrow
        # to air-cooled..PWC-observed, central at the air-cooled tier.
        wup_lo, wup_hi, wup_central = air, pwc, air
        basis = "operator_closed_loop_commitment"
        narrowed_by = f"{op}: {note}"

    def mgd(mw, wup):
        return mw * wup / 1e6

    lo = mgd(eff_lo, wup_lo)
    hi = mgd(eff_hi, wup_hi)
    central = mgd(eff_mw, wup_central)
    peak = mgd(eff_mw, WUP_PEAK_GAL_PER_MW_DAY["pwc_observed"])

    return {
        "mgd_range": [round(lo, 4), round(hi, 4)],
        "mgd_central": round(central, 4),
        "peak_day_mgd": round(peak, 4),
        "consumptive_mgd_central": round(central * CONSUMPTIVE_USE_FACTOR, 4),
        "wup_gal_per_mw_day": {
            "low": round(wup_lo, 1),
            "central": round(wup_central, 1),
            "high": round(wup_hi, 1),
        },
        "wup_reference_tiers": dict(WUP_GAL_PER_MW_DAY),
        "basis": basis,
        "narrowed_by": narrowed_by,
        "methodology": (
            f"Effective IT power (MW) x measured Water Use per Unit of Power "
            f"({round(wup_lo)}-{round(wup_hi)} gal/MW/day). WUP values are ICPRB's, derived from "
            f"utility-reported data center water use divided by effective power demand in the "
            f"Loudoun Water, Fairfax Water, and Prince William Water service areas (ICPRB 2025 WMA "
            f"Water Supply Study, Section 6.2 / Table 6-5). Central estimate uses the Prince "
            f"William Water observed fleet average of {pwc} gal/MW/day."
        ),
        "note": (
            f"Peak-day demand in Prince William Water's service area runs about "
            f"{WUP_PEAK_GAL_PER_MW_DAY['pwc_observed'] / pwc:.0f}x the annual average "
            f"({WUP_PEAK_GAL_PER_MW_DAY['pwc_observed']} gal/MW/day observed), so summer stress is far "
            f"higher than the annual figure implies. A consumptive-use factor of "
            f"{CONSUMPTIVE_USE_FACTOR} applies to the delivered volume."
        ),
    }


# ---------------------------------------------------------------------------
# Scope 2 - electricity-driven consumptive water
# ---------------------------------------------------------------------------
def scope2_electricity(eff_mw, eff_lo, eff_hi, year_built=None, pue_cap=None,
                       name=None, status=None):
    # Operator-disclosed PUE supersedes any vintage class: it is the operator's
    # own measured figure on the same metric definition, where the class is an
    # inference from a build date.
    disclosed = match_disclosed_pue(name)
    if disclosed:
        pue, note = disclosed
        vclass = "operator_disclosed"
        pue_lo = round(pue - DISCLOSED_PUE_TOLERANCE, 2)
        pue_hi = round(pue + DISCLOSED_PUE_TOLERANCE, 2)
        pue_source = note
    else:
        vclass = _vintage_class(year_built, status)
        pue_lo, pue_hi = PUE_RANGE[vclass]
        pue_source = None
    capped = False
    if pue_cap and pue_cap < pue_hi:
        pue_hi = pue_cap
        capped = True
    pue_central = (pue_lo + pue_hi) / 2

    def mgd(mw, pue):
        return mw * pue * HOURS_PER_DAY * BLENDED_CONSUMPTION_GAL_PER_MWH / 1e6

    return {
        "mgd_range": [round(mgd(eff_lo, pue_lo), 4), round(mgd(eff_hi, pue_hi), 4)],
        "mgd_central": round(mgd(eff_mw, pue_central), 4),
        "pue_class": vclass,
        "pue_range": [round(pue_lo, 2), round(pue_hi, 2)],
        "pue_capped_by_proffer": capped,
        "pue_source": pue_source,
        "blended_consumption_gal_per_mwh": round(BLENDED_CONSUMPTION_GAL_PER_MWH, 1),
        "methodology": (
            f"Effective IT MW x PUE ({pue_lo}-{pue_hi}, "
            f"{pue_source if pue_source else vclass + ' vintage'}) x 24 h/day x "
            f"{BLENDED_CONSUMPTION_GAL_PER_MWH:.0f} gal/MWh (Dominion generation-mix-blended "
            f"consumption factor) = consumptive water at the generating plant. Dominion's 2025 "
            f"mix is 58% gas / 25% nuclear / 14% renewable / 3% coal. Per-technology factors are "
            f"VIRGINIA-SPECIFIC, generation-weighted from USGS plant-level model estimates "
            f"(2015 release v1.2, July 2024) rather than national medians -- nuclear is "
            f"{CONSUMPTION_FACTORS_GAL_PER_MWH['nuclear']} gal/MWh here against a national median "
            f"of {NREL_NATIONAL_FACTORS_GAL_PER_MWH['nuclear']}, because Surry discharges to a "
            f"tidal estuary and consumes nothing while North Anna evaporates from Lake Anna."
        ),
        "note": (
            "System-average grid intensity, not marginal-generator attribution -- no published "
            "marginal water-intensity dataset exists for PJM/Dominion (NREL Cambium is "
            "carbon-only)."
        ),
    }


# ---------------------------------------------------------------------------
# Scope 3 - embodied / supply-chain
# ---------------------------------------------------------------------------
def scope3_embodied(s1_range, s2_range, s1_central, s2_central):
    lo_f, hi_f = SCOPE3_PROPORTIONAL_RANGE
    return {
        "mgd_range": [
            round((s1_range[0] + s2_range[0]) * lo_f, 4),
            round((s1_range[1] + s2_range[1]) * hi_f, 4),
        ],
        "mgd_central": round((s1_central + s2_central) * (lo_f + hi_f) / 2, 4),
        "proportional_range": [lo_f, hi_f],
        "methodology": (
            f"{lo_f:.0%}-{hi_f:.0%} of the operational (Scope 1 + Scope 2) total, anchored to "
            f"corporate embodied-vs-operational water disclosure ratios (Privette et al. 2026) -- "
            f"not a physical estimate specific to this facility's hardware or construction supply "
            f"chain, which lies entirely outside any Virginia dataset."
        ),
        "note": SCOPE3_OUTLIER_NOTE,
    }


# ---------------------------------------------------------------------------
# Plausibility checks
# ---------------------------------------------------------------------------
HV_PLAUSIBILITY_THRESHOLD_MW = 50
HV_PLAUSIBILITY_DISTANCE_FT = 26400  # 5 miles


def hv_plausibility_note(mw_hi, d_hv_transmission_ft):
    if d_hv_transmission_ft is None or mw_hi < HV_PLAUSIBILITY_THRESHOLD_MW:
        return None
    miles = d_hv_transmission_ft / 5280
    if d_hv_transmission_ft > HV_PLAUSIBILITY_DISTANCE_FT:
        return (
            f"Estimated load exceeds {HV_PLAUSIBILITY_THRESHOLD_MW} MW but the nearest in-service "
            f">=230kV HIFLD line is {miles:.1f} mi away -- flagged for scrutiny, not adjusted."
        )
    return f"Nearest in-service >=230kV HIFLD line is {miles:.1f} mi away, consistent with this load."


def benchmark_check(total_central_mgd, s1_central_mgd):
    """Compare the direct (Scope 1) estimate against JLARC's measured
    per-building figures. Scope 1 is the only scope JLARC measured, so it is
    the only one that can be checked this way."""
    b = JLARC_BENCHMARKS_MGD
    if s1_central_mgd > b["largest_va_building"]:
        verdict = (
            f"Direct on-site estimate ({s1_central_mgd:.3f} MGD) EXCEEDS the largest single "
            f"measured data center building in Virginia ({b['largest_va_building']:.3f} MGD, "
            f"243 Mgal/yr, JLARC 2024). Treat with scrutiny."
        )
        flag = "exceeds_largest_measured"
    elif s1_central_mgd > b["large_building_threshold"]:
        verdict = (
            f"Direct on-site estimate ({s1_central_mgd:.3f} MGD) places this among the largest "
            f"water-using data centers in Virginia -- only 11 buildings statewide exceeded "
            f"{b['large_building_threshold']:.3f} MGD in 2023 (JLARC 2024)."
        )
        flag = "large"
    elif s1_central_mgd < b["typical_building"]:
        verdict = (
            f"Direct on-site estimate ({s1_central_mgd:.3f} MGD) is below the water use of an "
            f"average large office building ({b['typical_building']:.3f} MGD) -- consistent with "
            f"JLARC's finding that most data centers use no more water than one."
        )
        flag = "typical_or_below"
    else:
        verdict = (
            f"Direct on-site estimate ({s1_central_mgd:.3f} MGD) sits in the normal measured band "
            f"for Virginia data centers (JLARC 2024)."
        )
        flag = "normal"
    return {
        "flag": flag,
        "verdict": verdict,
        "reference_mgd": {k: round(v, 4) for k, v in b.items()},
    }


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------
def estimate_scope_water_footprint(
    name,
    gfa_sqft=None,
    gfa_source=None,
    gfa_quality=None,
    year_built=None,
    d_hv_transmission_ft=None,
    cdd=None,
    pue_cap=None,
    cooling_disclosure=None,
    permit_power=None,
    status=None,
):
    """
    Returns the Scope 1/2/3 estimate for one facility, or None if there is no
    floor-area figure to derive power from.

    gfa_quality      -- assessed | permit | estimated | proffer_split (see resolve_gfa)
    pue_cap          -- an annualized PUE ceiling from a binding proffer, if any
    cooling_disclosure -- {"air_or_closed_loop": bool, "source": str} from a
                        permit/proffer condition, if any
    """
    # MW-source precedence. A permit-derived figure comes from ICPRB's own
    # input (air-permit generator capacity) run through their Equation 6-3, in
    # the direction that equation validates -- so it supersedes the GFA bridge,
    # which runs the 8,818 sqft/MW constant backwards. Validation across 11
    # Prince William sites puts the two within 2% at the median, so this
    # sharpens per-facility precision rather than moving the aggregate.
    power_basis = "gfa_icprb_density"
    permit_meta = None
    eff = None
    if permit_power:
        eff = effective_power_from_permit(permit_power.get("site_generator_mw"),
                                          permit_power.get("gfa_share"))
        if eff:
            power_basis = "permit_generator_capacity"
            permit_meta = permit_power
    if eff is None:
        eff = effective_power_from_gfa(gfa_sqft)
    if eff is None:
        return None
    eff_mw, eff_lo, eff_hi = eff

    operator_commitment = match_operator_commitment(name)
    operator_match = match_operator(name)

    s1 = scope1_onsite_cooling(eff_mw, eff_lo, eff_hi, operator_commitment, cooling_disclosure)
    s2 = scope2_electricity(eff_mw, eff_lo, eff_hi, year_built, pue_cap,
                            name=name, status=status)
    s3 = scope3_embodied(s1["mgd_range"], s2["mgd_range"], s1["mgd_central"], s2["mgd_central"])

    total_lo = s1["mgd_range"][0] + s2["mgd_range"][0] + s3["mgd_range"][0]
    total_hi = s1["mgd_range"][1] + s2["mgd_range"][1] + s3["mgd_range"][1]
    total_central = s1["mgd_central"] + s2["mgd_central"] + s3["mgd_central"]

    # Cross-check the GFA-derived power against the operator's interconnection
    # span. This can CONFIRM or FLAG, but never widen -- the operator figure is
    # portfolio-wide and less specific than this building's own floor area.
    xcheck = None
    if operator_match:
        op, (op_lo, op_hi) = operator_match
        overlap = not (eff_hi < op_lo or eff_lo > op_hi)
        xcheck = {
            "operator": op,
            "operator_mw_range": [op_lo, op_hi],
            "agrees": overlap,
            "note": (
                f"interconnection.fyi lists {op_lo}-{op_hi} MW across {op}'s Prince William / "
                f"Manassas portfolio. "
                + (
                    "The floor-area-derived estimate falls inside that span."
                    if overlap
                    else "The floor-area-derived estimate falls outside that span; the operator "
                         "figure is portfolio-wide rather than building-specific, so it is "
                         "reported as a flag rather than used to widen the range."
                )
            ),
        }

    return {
        "power": {
            "effective_it_mw_range": [eff_lo, eff_hi],
            "effective_it_mw_central": eff_mw,
            "basis": power_basis,
            "sqft_per_effective_mw": SQFT_PER_EFFECTIVE_MW,
            "gfa_sqft": gfa_sqft,
            "gfa_field_used": gfa_source,
            "gfa_quality": gfa_quality,
            "permit": permit_meta,
            "note": (
                (
                    f"VADEQ air permit {permit_meta['registration_no']} covers this site with "
                    f"{permit_meta['site_generator_mw']:,.1f} MW of permitted backup generator "
                    f"capacity across {permit_meta['n_buildings_on_permit']} building(s). This "
                    f"building's {permit_meta['gfa_share']:.0%} floor-area share x ICPRB Equation "
                    f"6-3 (capacity x 0.5 redundancy x 0.8 utilization) = {eff_mw} MW effective IT "
                    f"load. Floor area is used only to apportion a measured site total, not to "
                    f"generate it -- the 8,818 sqft/MW density bridge is not used for this "
                    f"building."
                )
                if permit_meta else
                f"{gfa_sqft:,.0f} sqft / {SQFT_PER_EFFECTIVE_MW:,} sqft per effective MW = "
                f"{eff_mw} MW effective IT load (+/-{DENSITY_TOLERANCE:.0%} for facility-level "
                f"variation around the fleet-average density). Density is ICPRB's, computed from "
                f"the JLARC/VADEQ air-permit database of Virginia data centers."
            ),
            "operator_cross_check": xcheck,
            "hv_plausibility": hv_plausibility_note(eff_hi, d_hv_transmission_ft),
        },
        "scope1_onsite_cooling": s1,
        "scope2_electricity": s2,
        "scope3_embodied": s3,
        "total_mgd_range": [round(total_lo, 4), round(total_hi, 4)],
        "total_mgd_central": round(total_central, 4),
        "total_note": (
            "Envelope sum of independent scope minima and maxima -- a conservative bound, not a "
            "statistical confidence interval (the three scopes are not assumed to co-vary). The "
            "central estimate uses Prince William Water's own observed intensity and is the "
            "figure to quote."
        ),
        "benchmark": benchmark_check(total_central, s1["mgd_central"]),
    }
