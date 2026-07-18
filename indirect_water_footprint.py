"""
Facility-level Scope 1/2/3 water footprint estimator.

This is the load-bearing module behind the tool's actual thesis: not "rank
parcels," but "for a named data-center building or campus, what is the
defensible RANGE of its water footprint, broken into the three components
the literature uses to categorize data-center water (Privette et al., AGU
Advances 2026; Li et al., ACM 2025; Mytton, Nature 2021)?"

  Scope 1 — on-site: water evaporated at the facility itself, mostly by
    evaporative cooling towers / adiabatic humidification. Governed by the
    Water Usage Effectiveness (WUE) metric (The Green Grid): L of water per
    kWh of IT equipment energy. Cooling TECHNOLOGY (dry/closed-loop vs.
    hybrid vs. open evaporative) is not disclosed per facility in any PWC
    public dataset, so this is reported as the FULL published envelope, not
    narrowed by an unstated assumption.

  Scope 2 — electricity-driven: water consumed (evaporated, not returned)
    at the power plants generating the facility's electricity. Estimable
    from public data because it depends only on (a) facility power draw and
    (b) the grid mix's water-consumption intensity — the same calculation
    this module has always done, now fed by a second, independent power
    estimate (see below) instead of interconnection.fyi alone.

  Scope 3 — embodied/supply-chain: water used to fabricate the semiconductors,
    servers, and construction materials that make up the facility, before it
    ever draws power. Not attributable to a single PWC facility from any
    dataset here (chip fabs are not in Virginia); modeled as a proportional
    anchor to the operational (Scope 1 + 2) total, per corporate disclosure
    ratios, with an explicit caveat about the reported outlier case.

POWER ESTIMATION — two independent methods, cross-checked:
  (A) GFA-based: Data_Center_Buildings.GFA (coalesced across GFA / BPGFA /
      ApprovedGFA / REATaxedGFA / PermittedGFA — 202/203 buildings have at
      least one non-null value) x an IT power density benchmark (W/sqft of
      gross floor area) x a PUE range selected by building vintage.
  (B) Operator-keyword match against interconnection.fyi's public
      interconnection-queue MW ranges (unchanged from the original version
      of this module).
  When both exist, the reported range is their INTERSECTION where they
  overlap (two independent methods agreeing is the strongest evidence this
  tool can produce) — or, if they don't overlap, both bounds are kept and
  the disagreement is flagged rather than silently resolved.

WHAT THIS STILL EXCLUDES:
  - Any claim about which specific cooling technology a given building
    uses — Scope 1 stays a full envelope until a genuinely new evidence
    source (e.g., permit-PDF mechanical-system text) narrows it.
  - Marginal-generator attribution for Scope 2 — no published marginal-
    water-intensity dataset exists (NREL Cambium is carbon-only), so this
    uses Dominion's system-average generation mix, stated as such.
  - A physical (rather than proportional-anchor) Scope 3 estimate.

CITATIONS:
  - WUE definition and full published range (~0.0-2.4 L/kWh across dry,
    hybrid, and open-evaporative cooling): The Green Grid WUE metric;
    Mytton, D., "Data centre water consumption," npj Clean Water /
    Nature portfolio (2021); Privette et al., AGU Advances (2026).
  - IT power density benchmarks (100-200 W/sqft standard; 250-450 W/sqft
    modern AI-class): Uptime Institute / LBNL data center benchmarking
    surveys; Open Compute Project (OCP) "Diablo" rack power spec
    (50-135 kW/rack GPU racks, up to 1 MW/rack roadmap); LBNL "Queued Up"
    (2025) on the AI-driven step-change in PWC-area interconnection
    requests.
  - PUE ranges (1.08-1.15 modern hyperscale; 1.20-1.60 standard/enterprise):
    hyperscaler fleet-average PUE disclosures (Google, Microsoft, Meta
    sustainability reports, 2023-2025) vs. Uptime Institute's global
    survey average for enterprise/colo facilities.
  - Generation-technology water CONSUMPTION factors and Dominion Energy
    Virginia's 2025 generation mix: Macknick, J. et al., NREL/TP-6A20-50900
    (2011); EIA "Today in Energy" / Virginia generation-mix reporting.
  - Facility MW capacity ranges: interconnection.fyi public data-center
    interconnection-queue tracker, accessed 2026.
  - Scope 3 proportional-anchor ratio and the >99% embodied-water outlier
    disclosure: Privette et al., AGU Advances (2026).
"""

# ---------------------------------------------------------------------------
# Scope 2 — grid consumption intensity
# ---------------------------------------------------------------------------
CONSUMPTION_FACTORS_GAL_PER_MWH = {
    "natural_gas_cc": 210,   # combined-cycle, recirculating cooling
    "nuclear": 700,          # recirculating cooling, midpoint of 600-820 range
    "coal": 687,             # steam-Rankine, recirculating cooling (NREL review midpoint)
    "renewable": 0,          # solar PV / wind — negligible operational water consumption
}

DOMINION_GENERATION_MIX = {
    "natural_gas_cc": 0.58,
    "nuclear": 0.25,
    "renewable": 0.14,
    "coal": 0.03,
}

BLENDED_CONSUMPTION_GAL_PER_MWH = sum(
    DOMINION_GENERATION_MIX[fuel] * CONSUMPTION_FACTORS_GAL_PER_MWH[fuel]
    for fuel in DOMINION_GENERATION_MIX
)  # ~318 gal/MWh

ASSUMED_UTILIZATION = 0.90
HOURS_PER_YEAR = 8760
GAL_PER_LITER = 0.264172

# ---------------------------------------------------------------------------
# Power estimate (A): GFA-based
# ---------------------------------------------------------------------------
IT_POWER_DENSITY_W_PER_SQFT = {
    "standard": (100, 200),
    "modern_ai": (250, 450),
    "unknown": (100, 450),
}

PUE_RANGE = {
    "modern": (1.08, 1.15),
    "standard": (1.20, 1.60),
    "unknown": (1.08, 1.60),
}


def _density_class(year_built):
    if year_built and year_built >= 2023:
        return "modern_ai"
    if year_built:
        return "standard"
    return "unknown"


def _vintage_class(year_built):
    if year_built is None:
        return "unknown"
    return "modern" if year_built >= 2020 else "standard"


def gfa_power_estimate(gfa_sqft, year_built):
    """Independent power estimate (A): building floor area -> IT power ->
    facility power, via density + PUE benchmarks. Returns None if no GFA."""
    if not gfa_sqft or gfa_sqft <= 0:
        return None
    dclass = _density_class(year_built)
    w_lo, w_hi = IT_POWER_DENSITY_W_PER_SQFT[dclass]
    it_mw_lo = gfa_sqft * w_lo / 1_000_000
    it_mw_hi = gfa_sqft * w_hi / 1_000_000
    vclass = _vintage_class(year_built)
    pue_lo, pue_hi = PUE_RANGE[vclass]
    return {
        "gfa_sqft": gfa_sqft,
        "density_class": dclass,
        "it_power_density_w_per_sqft": [w_lo, w_hi],
        "it_mw_range": [round(it_mw_lo, 1), round(it_mw_hi, 1)],
        "pue_class": vclass,
        "pue_range": [pue_lo, pue_hi],
        "facility_mw_range": [round(it_mw_lo * pue_lo, 1), round(it_mw_hi * pue_hi, 1)],
    }


# ---------------------------------------------------------------------------
# Power estimate (B): interconnection.fyi operator match (unchanged source)
# ---------------------------------------------------------------------------
OPERATOR_MW_RANGES = {
    "AMAZON": (50, 250),
    "AWS": (50, 250),
    "CLOUDHQ": (10, 250),
    "CLOUD HQ": (10, 250),
    "IRON MOUNTAIN": (100, 250),
    "QTS": (250, 400),
    "STACK": (25, 100),
    "NTT": (100, 250),
    "EQUINIX": (1, 25),
    "CORPORATE OFFICE PROPERTIES": (100, 250),
    "DIGITAL REALTY": (10, 25),
    "DLR": (10, 25),
    "VERIZON": (10, 25),
    "COMCAST": (1, 50),
    "OATH": (1, 50),
    "MICROSOFT": (25, 50),
    "GAINESVILLE CROSSING": (250, 400),
    "CORSCALE": (250, 400),
}

OPERATOR_SOURCE_NOTE = (
    "MW range from interconnection.fyi public interconnection-queue registry "
    "(operator-level span across that operator's Prince William County / "
    "Manassas listings, not a building-specific figure)."
)


def match_operator(name: str):
    if not name:
        return None
    upper = name.upper()
    for kw in sorted(OPERATOR_MW_RANGES.keys(), key=len, reverse=True):
        if kw in upper:
            return kw, OPERATOR_MW_RANGES[kw]
    return None


def reconcile_power(gfa_est, operator_match):
    """Cross-check the two independent power estimates. Intersection where
    they overlap; both bounds kept (flagged) where they don't; whichever one
    exists alone if only one does."""
    op_range = operator_match[1] if operator_match else None
    gfa_range = gfa_est["facility_mw_range"] if gfa_est else None

    if gfa_range and op_range:
        lo = max(gfa_range[0], op_range[0])
        hi = min(gfa_range[1], op_range[1])
        if lo <= hi:
            return {
                "mw_range": [round(lo, 1), round(hi, 1)],
                "basis": "intersection",
                "note": (
                    f"GFA-derived estimate ({gfa_range[0]}-{gfa_range[1]} MW) and "
                    f"interconnection.fyi operator range ({op_range[0]}-{op_range[1]} MW, "
                    f"{operator_match[0]}) overlap; range narrowed to their intersection."
                ),
            }
        lo, hi = min(gfa_range[0], op_range[0]), max(gfa_range[1], op_range[1])
        return {
            "mw_range": [round(lo, 1), round(hi, 1)],
            "basis": "disagreement",
            "note": (
                f"GFA-derived estimate ({gfa_range[0]}-{gfa_range[1]} MW) and "
                f"interconnection.fyi operator range ({op_range[0]}-{op_range[1]} MW, "
                f"{operator_match[0]}) do NOT overlap — both methods' bounds are kept "
                f"rather than resolving the disagreement, since neither source is "
                f"building-specific enough to override the other."
            ),
        }
    if gfa_range:
        return {"mw_range": gfa_range, "basis": "gfa_only", "note": "No matching interconnection.fyi operator listing; GFA-derived estimate only."}
    if op_range:
        return {"mw_range": [op_range[0], op_range[1]], "basis": "operator_only", "note": "No GFA on record for this building; interconnection.fyi operator-level range only."}
    return None


# ---------------------------------------------------------------------------
# Scope 2 — electricity-driven consumptive water
# ---------------------------------------------------------------------------
def scope2_electricity(facility_mw_range):
    lo_mw, hi_mw = facility_mw_range

    def mgd_for(mw):
        annual_mwh = mw * HOURS_PER_YEAR * ASSUMED_UTILIZATION
        annual_gal = annual_mwh * BLENDED_CONSUMPTION_GAL_PER_MWH
        return annual_gal / 365 / 1_000_000

    return {
        "mgd_range": [round(mgd_for(lo_mw), 3), round(mgd_for(hi_mw), 3)],
        "blended_consumption_gal_per_mwh": round(BLENDED_CONSUMPTION_GAL_PER_MWH, 1),
        "assumed_utilization": ASSUMED_UTILIZATION,
        "methodology": (
            f"facility MW range x {HOURS_PER_YEAR}h/yr x {ASSUMED_UTILIZATION:.0%} utilization x "
            f"{BLENDED_CONSUMPTION_GAL_PER_MWH:.0f} gal/MWh (Dominion generation-mix-blended "
            f"consumption factor, NREL Macknick et al. 2011) = annual consumptive water "
            f"footprint at the power plant, converted to MGD."
        ),
    }


# ---------------------------------------------------------------------------
# Scope 1 — on-site cooling (WUE envelope)
# ---------------------------------------------------------------------------
FULL_WUE_ENVELOPE_L_PER_KWH = (0.0, 2.4)  # dry/closed-loop .. open evaporative

WUE_NOTE = (
    "Cooling technology (dry/closed-loop, hybrid, or open evaporative) is not "
    "disclosed per facility in any PWC public dataset, so this reports the full "
    "published WUE envelope rather than an unstated single-technology assumption. "
    "Basis for the IT power figure used here (not facility power): WUE is defined "
    "relative to IT equipment energy, since IT load is what generates the heat "
    "the cooling system removes (The Green Grid)."
)


# Wet-bulb / evaporative-demand climate modulation. No direct wet-bulb
# series exists in this corpus, and deriving one from precipitation (as a
# humidity proxy) would overstate precision the input doesn't support — so
# this uses trailing-12mo Cooling Degree Days (base 65F) directly, as a
# defensible, already-computed proxy for how many hours/year an
# evaporative or hybrid system would actually be cycling. It does NOT
# narrow the WUE envelope (cooling technology is still undisclosed): it
# computes a separate, clearly-labeled CLIMATE-WEIGHTED POINT inside the
# existing bounds — "if this facility uses evaporative/hybrid cooling,
# PWC's current climate suggests operation nearer this point than the
# envelope's midpoint" — reported alongside the authoritative range, never
# replacing it.
# Baselines: ~800 CDD/yr approximates a mild/cool temperate US climate
# (low evaporative-cooling demand); ~2200 CDD/yr approximates a hot-humid
# climate (high evaporative-cooling demand, e.g. Deep South). PWC's own
# trailing-12mo CDD (~1300, see preprocess_score_parcels.py) falls roughly
# a third of the way up this range — a humid-continental/subtropical
# transition climate, consistent with its Köppen classification.
CDD_BASELINE_LOW = 800
CDD_BASELINE_HIGH = 2200


def climate_weighted_wue_point(cdd, wue_lo, wue_hi):
    if cdd is None:
        return None
    frac = (cdd - CDD_BASELINE_LOW) / (CDD_BASELINE_HIGH - CDD_BASELINE_LOW)
    frac = max(0.0, min(1.0, frac))
    return round(wue_lo + frac * (wue_hi - wue_lo), 3)


def scope1_onsite_cooling(it_mw_range, cdd=None):
    lo_mw, hi_mw = it_mw_range
    wue_lo, wue_hi = FULL_WUE_ENVELOPE_L_PER_KWH

    def mgd_for(mw, wue):
        annual_kwh = mw * 1000 * HOURS_PER_YEAR * ASSUMED_UTILIZATION
        annual_l = annual_kwh * wue
        annual_gal = annual_l * GAL_PER_LITER
        return annual_gal / 365 / 1_000_000

    climate_wue = climate_weighted_wue_point(cdd, wue_lo, wue_hi)
    climate_point_mgd = None
    climate_note = None
    if climate_wue is not None:
        # Use the midpoint of the IT power range for the point estimate —
        # this is a single "most climate-plausible point," not a bound.
        mid_mw = (lo_mw + hi_mw) / 2
        climate_point_mgd = round(mgd_for(mid_mw, climate_wue), 3)
        climate_note = (
            f"At {cdd:.0f} trailing-12mo cooling degree days, PWC's current climate "
            f"suggests a WUE nearer {climate_wue} L/kWh than the envelope midpoint IF "
            f"this facility uses evaporative/hybrid cooling (CDD-based proxy for "
            f"evaporative-operation hours, not a wet-bulb measurement — dry/closed-loop "
            f"facilities would sit near 0 regardless of climate). This is an "
            f"explicitly-approximate modulator on top of the full envelope below, not a "
            f"narrowed range."
        )

    return {
        "mgd_range": [round(mgd_for(lo_mw, wue_lo), 3), round(mgd_for(hi_mw, wue_hi), 3)],
        "wue_range_l_per_kwh": [wue_lo, wue_hi],
        "climate_weighted_point_mgd": climate_point_mgd,
        "climate_weighted_wue_l_per_kwh": climate_wue,
        "climate_note": climate_note,
        "methodology": (
            f"IT power MW range x {HOURS_PER_YEAR}h/yr x {ASSUMED_UTILIZATION:.0%} utilization x "
            f"{wue_lo}-{wue_hi} L/kWh (full published Water Usage Effectiveness envelope, "
            f"Mytton 2021 / Privette et al. 2026) = annual on-site evaporative water use, "
            f"converted to MGD."
        ),
        "note": WUE_NOTE,
    }


# ---------------------------------------------------------------------------
# Scope 3 — embodied / supply-chain (proportional anchor)
# ---------------------------------------------------------------------------
SCOPE3_PROPORTIONAL_RANGE = (0.05, 0.15)

SCOPE3_OUTLIER_NOTE = (
    "At least one hyperscale operator has disclosed embodied/supply-chain water "
    "exceeding 99% of its total corporate water footprint (Privette et al., AGU "
    "Advances, 2026) — that figure reflects a specific company-wide accounting "
    "boundary choice (e.g., excluding utility-side power-plant water from its "
    "reported Scope 2), not a physical per-facility ratio. It is not used as a "
    "default multiplier here; it is flagged as evidence the 5-15% anchor below is "
    "a floor, not a ceiling, for facilities with unusually water-light Scope 1/2."
)


def scope3_embodied(scope1_mgd_range, scope2_mgd_range):
    op_lo = scope1_mgd_range[0] + scope2_mgd_range[0]
    op_hi = scope1_mgd_range[1] + scope2_mgd_range[1]
    lo_frac, hi_frac = SCOPE3_PROPORTIONAL_RANGE
    return {
        "mgd_range": [round(op_lo * lo_frac, 3), round(op_hi * hi_frac, 3)],
        "proportional_range": [lo_frac, hi_frac],
        "methodology": (
            f"{lo_frac:.0%}-{hi_frac:.0%} of the operational (Scope 1 + Scope 2) total, "
            f"anchored to corporate embodied-vs-operational water disclosure ratios "
            f"(Privette et al. 2026) — not a physical estimate specific to this "
            f"facility's actual hardware/construction supply chain, which is entirely "
            f"outside any PWC dataset."
        ),
        "note": SCOPE3_OUTLIER_NOTE,
    }


# ---------------------------------------------------------------------------
# Top-level entry point
# ---------------------------------------------------------------------------
HV_PLAUSIBILITY_THRESHOLD_MW = 50   # loads above this need proximate high-voltage service
HV_PLAUSIBILITY_DISTANCE_FT = 26400  # 5 miles — beyond this, a 50MW+ draw has no obvious nearby supply

def hv_plausibility_note(mw_range, d_hv_transmission_ft):
    """Power-availability plausibility check: a 50MW+ estimated load with no
    in-service >=230kV HIFLD line within 5 miles is a signal the estimate
    (or the facility's actual grid interconnection) needs scrutiny — the
    dataset can't attribute capacity to a line, but distance-to-service is a
    real constraint on what a facility can plausibly draw."""
    if d_hv_transmission_ft is None or mw_range[1] < HV_PLAUSIBILITY_THRESHOLD_MW:
        return None
    if d_hv_transmission_ft > HV_PLAUSIBILITY_DISTANCE_FT:
        return (
            f"Estimated load ({mw_range[0]}-{mw_range[1]} MW) exceeds {HV_PLAUSIBILITY_THRESHOLD_MW}MW but the "
            f"nearest in-service >=230kV HIFLD line is {d_hv_transmission_ft/5280:.1f} mi away — flagging for "
            f"scrutiny, not adjusting the range (line capacity isn't attributable to one facility anyway)."
        )
    return (
        f"Nearest in-service >=230kV HIFLD line is {d_hv_transmission_ft/5280:.1f} mi away, consistent with a "
        f"{mw_range[0]}-{mw_range[1]} MW load."
    )


def estimate_scope_water_footprint(name, gfa_sqft=None, gfa_source=None, year_built=None, d_hv_transmission_ft=None, cdd=None):
    """
    Returns a dict with independent scope1/scope2/scope3 ranges plus the
    power-reconciliation detail behind scope2, or None if there's neither a
    GFA figure nor an operator match to build any estimate from.
    """
    gfa_est = gfa_power_estimate(gfa_sqft, year_built)
    operator_match = match_operator(name)
    power = reconcile_power(gfa_est, operator_match)
    if power is None:
        return None

    it_mw_range = gfa_est["it_mw_range"] if gfa_est else power["mw_range"]

    s2 = scope2_electricity(power["mw_range"])
    s1 = scope1_onsite_cooling(it_mw_range, cdd=cdd)
    s3 = scope3_embodied(s1["mgd_range"], s2["mgd_range"])

    total_lo = s1["mgd_range"][0] + s2["mgd_range"][0] + s3["mgd_range"][0]
    total_hi = s1["mgd_range"][1] + s2["mgd_range"][1] + s3["mgd_range"][1]

    return {
        "power": {
            "mw_range": power["mw_range"],
            "basis": power["basis"],
            "note": power["note"],
            "gfa_estimate": gfa_est,
            "gfa_field_used": gfa_source,
            "operator_match": {"operator": operator_match[0], "mw_range": list(operator_match[1])} if operator_match else None,
            "source": OPERATOR_SOURCE_NOTE if operator_match else None,
            "hv_plausibility": hv_plausibility_note(power["mw_range"], d_hv_transmission_ft),
        },
        "scope1_onsite_cooling": s1,
        "scope2_electricity": s2,
        "scope3_embodied": s3,
        "total_mgd_range": [round(total_lo, 3), round(total_hi, 3)],
        "total_note": (
            "Envelope sum of independent scope minima and maxima — a conservative "
            "bound, not a statistical confidence interval (the three scopes are not "
            "assumed to co-vary)."
        ),
    }
