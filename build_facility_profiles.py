#!/usr/bin/env python3
"""
Build per-facility evidence dossiers for every data center building and
campus in Prince William County.

This is deliberately NOT a water-demand estimator. It answers a narrower,
defensible question: "tell me everything observable about Facility X" —
identity, permit history, physical footprint, power/land context, and the
same watershed/disclosure/monitoring context already computed per-parcel by
preprocess_score_parcels.py. Every field traces to a specific source dataset
and is either present (cite it) or absent (say so) — no synthesized numbers,
no confidence percentages, no water-use figures. The gap between "the
underlying facility has X characteristics" and "therefore it uses Y water"
is exactly the disclosure gap this tool exists to make visible, not paper
over.

Two record types, one per row:
  - building profiles: keyed by BuildingID, one per built structure (203)
  - campus profiles:   keyed by CaseNumber, one per planned/entitled project (51)

Output: public/data/facility_profiles.json
"""
import json
import re
import os
import time

import geopandas as gpd
import pandas as pd

from indirect_water_footprint import (
    SQFT_PER_EFFECTIVE_MW,
    build_proffer_group_sizes,
    estimate_scope_water_footprint,
    resolve_gfa,
)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("PWC_DATA_ROOT", os.path.join(_SCRIPT_DIR, "data", "water_raw"))
OUT_ROOT = os.environ.get("VIRA_OUT_ROOT", os.path.join(_SCRIPT_DIR, "public", "data"))


def t(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def p(name):
    return os.path.join(DATA_ROOT, name)


def clean(v):
    """NaN / NaT / pandas-missing -> None, for JSON safety."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except (TypeError, ValueError):
        pass
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return v


t("Loading parcel water/disclosure context (from preprocess_score_parcels.py output)...")
with open(os.path.join(OUT_ROOT, "parcels_scored.json")) as f:
    parcels_scored = json.load(f)
by_gpin = {r["GPIN"]: r for r in parcels_scored if r.get("GPIN")}
t(f"  {len(by_gpin):,} parcel records available for context lookup")

t("Loading DC buildings + projects + regulatory case layers...")
dc_buildings = gpd.read_file(p("Data_Center_Buildings.geojson")).to_crs("EPSG:5070")
dc_projects = gpd.read_file(p("Data_Center_Projects.geojson")).to_crs("EPSG:5070")
parcels = gpd.read_file(p("Parcel.geojson")).to_crs("EPSG:5070")
use_permits = gpd.read_file(p("Use_Permits.geojson")).to_crs("EPSG:5070")
bza = gpd.read_file(p("Zoning_Appeals_and_Variances.geojson")).to_crs("EPSG:5070")
pending = gpd.read_file(p("Planning_Pending_Cases.geojson")).to_crs("EPSG:5070")
t(f"  buildings={len(dc_buildings)} projects={len(dc_projects)} use_permits={len(use_permits)} bza={len(bza)} pending={len(pending)}")

WATER_CONTEXT_FIELDS = [
    "watershed_name", "watershed_acres", "n_dc_in_watershed", "watershed_major_basin", "n_dc_in_major_basin",
    "d_stream_ft", "stream_order", "stream_name", "d_hydro_ft", "d_spring_ft", "rpa", "wetland",
    "in_tidal_flow_path", "tidal_class", "tidal_zone",
    "dam", "dam_haz_class", "soil_cat", "hsg", "erosion_susceptibility", "soil_permeability",
    "near_h2oquality_protected_land",
    "sw_segments", "sw_structures", "sw_facilities",
    "n_wqp_stations_1mi", "n_deq_monitoring_1mi", "n_deq_gage_1mi", "nearest_benthic_n",
    "n_inat_1mi", "n_inat_research_1mi",
    "has_npdes", "has_deq_permit", "n_npdes_violations", "dmr_nodi_code", "dmr_flow_mgd",
    "echo_facility_name", "general_permit_type", "compliance_status", "frs_id",
    "d_transmission_ft", "d_hv_transmission_ft", "nearest_hv_sub_1", "nearest_hv_sub_2", "zoning",
    "cdd", "has_proffers", "watershed_mgmt_plan_number",
]


def water_context_for_gpin(gpin):
    row = by_gpin.get(gpin)
    if not row:
        return None
    return {k: row.get(k) for k in WATER_CONTEXT_FIELDS}


def water_context_for_geometry(geom):
    """For campuses spanning multiple/no exact GPIN match, aggregate context
    from every parcel the campus polygon intersects."""
    hits = parcels[parcels.intersects(geom)]
    gpins = [g for g in hits.get("GPIN", []) if isinstance(g, str) and g]
    rows = [by_gpin[g] for g in gpins if g in by_gpin]
    if not rows:
        return None, []
    # Countywide/point-context fields: take the first non-null. Count-ish
    # fields: take the max across constituent parcels (worst/most-relevant
    # case for a multi-parcel campus).
    out = {}
    for k in WATER_CONTEXT_FIELDS:
        vals = [r.get(k) for r in rows if r.get(k) is not None]
        if not vals:
            out[k] = None
            continue
        if isinstance(vals[0], (int, float)) and k not in ("watershed_name", "dam_haz_class", "dmr_nodi_code", "echo_facility_name", "general_permit_type", "compliance_status", "frs_id", "zoning"):
            out[k] = max(vals)
        else:
            out[k] = vals[0]
    return out, gpins


t("Matching regulatory case history (use permits / BZA / pending cases) to each building...")


def matched_cases(geom, layer, cols):
    hits = layer[layer.intersects(geom)]
    return [{c: clean(row[c]) for c in cols} for _, row in hits.iterrows()]


def coalesce_gfa(row, fields):
    """First non-null/non-zero figure among `fields`, plus which field it came
    from. Used for CAMPUS entitlement areas, where a site-wide total is the
    correct quantity. Per-BUILDING areas must go through resolve_gfa()
    instead -- see the note below."""
    for f in fields:
        v = clean(row.get(f))
        if v not in (None, 0):
            return v, f
    return None, None


# Per-building floor area is resolved by indirect_water_footprint.resolve_gfa,
# which knows that Data_Center_Buildings.GFA holds the SITE-WIDE PROFFERED
# ENTITLEMENT (repeated on every building on that site) whenever GFASource is
# a proffer. Coalescing GFA first -- as this script used to -- gave 153 of 202
# buildings a campus entitlement as their own footprint and inflated the
# county total from ~42M to 87.5M sqft.
_proffer_group_sizes = build_proffer_group_sizes(
    [row for _, row in dc_buildings.iterrows()]
)
t(f"  proffer-entitlement GFA values shared across multiple buildings: {len(_proffer_group_sizes)}")

# Binding cooling / PUE conditions extracted from special use permits. These
# are the strongest narrowing evidence the county produces: a proffer that
# specifies air or closed-loop cooling collapses the Scope 1 technology
# envelope for that facility. Keyed by the case number that carries them.
#
# SUP2025-00016 (Hornbaker Road) proffer text, verbatim:
#   "c. Data Center Cooling: Groundwater, surface water withdrawals, or
#    surface water discharges shall not be used to cool the data center
#    buildings on the Property."  <- MANDATORY
#   "d. Sustainability: The Applicant shall incorporate ... a minimum of
#    eight (8) sustainability measures ... may include ...
#    xvi. Design the data center building to operate below an annualized
#    1.5 PUE ...; xvii. Use of air or closed loop cooling rather than
#    water-cooled alternatives"  <- MENU: 8 of 19 required, so xvi/xvii are
#    NOT guaranteed. Recorded as available-but-unconfirmed, never as fact.
PERMIT_COOLING_CONDITIONS = {
    # REZ2025-00003 ("Project Industry" / Aura Development), proffer statement
    # dated April 24, 2026. Same menu structure as SUP2025-00016 below, and the
    # same conclusion: cooling appears as item 15 of 16 in a sustainability
    # menu from which only EIGHT must be implemented, so it is not guaranteed.
    #
    #   "15. Use of air or closed loop cooling rather than water-cooled
    #    alternatives; or"
    #   "14. Design the data center building to operate below an annualized
    #    1.5 PUE (Power Utilization Effectiveness) standard;"
    #
    # A separate MANDATORY proffer is suggestive but does not bind cooling type:
    #
    #   "D. Noise Mitigation: All air-cooled chiller equipment installed on the
    #    Property, whether ground-mounted or roof-mounted, shall include ...
    #    low noise emission fans ... magnetic bearing compressors"
    #
    # That governs air-cooled chillers IF installed; it does not require that
    # cooling be air-cooled. An applicant does not usually write a noise proffer
    # for equipment it has no plan to install, so this is real evidence of
    # intent -- but it is inferable, not binding, and does not narrow the
    # estimate.
    "REZ2025-00003": {
        "mandatory_no_ground_or_surface_water_cooling": False,
        "menu_includes_air_or_closed_loop": True,
        "menu_includes_pue_cap": 1.5,
        "menu_required_count": 8,
        "menu_total_count": 16,
        "anticipates_air_cooled_chillers": True,
        "source": (
            "REZ2025-00003 (Project Industry) proffer statement dated April 24, 2026: air or "
            "closed-loop cooling appears as item 15 of 16 in a sustainability menu from which the "
            "applicant must implement at least 8, so it is available but not guaranteed. A separate "
            "mandatory noise proffer regulates 'all air-cooled chiller equipment installed on the "
            "Property', which indicates air-cooled chillers are anticipated but does not require them."
        ),
    },
    "SUP2025-00016": {
        "mandatory_no_ground_or_surface_water_cooling": True,
        "menu_includes_air_or_closed_loop": True,
        "menu_includes_pue_cap": 1.5,
        "menu_required_count": 8,
        "menu_total_count": 19,
        "source": (
            "SUP2025-00016 (Hornbaker Road) proffers dated July 31, 2025: cooling with "
            "groundwater or surface water is prohibited outright; air/closed-loop cooling and a "
            "1.5 annualized PUE cap appear as items xvii and xvi in a sustainability menu from "
            "which the applicant must implement at least 8 of 19 and document the selection "
            "before occupancy."
        ),
    },
}


def permit_conditions_for(case_records):
    """Match any binding cooling/PUE conditions to this facility via its
    matched case history. Returns (pue_cap, cooling_disclosure) -- both None
    when nothing applies."""
    for rec in case_records or []:
        for key in ("ZoningCaseNumber", "BZACaseNumber", "PlanningCaseNumber"):
            num = rec.get(key)
            if num and num in PERMIT_COOLING_CONDITIONS:
                c = PERMIT_COOLING_CONDITIONS[num]
                # The PUE cap and air-cooling commitment are menu items, not
                # guarantees, so they are surfaced as context rather than used
                # to narrow the estimate. Only mandatory conditions narrow.
                return None, {
                    "air_or_closed_loop": False,
                    "mandatory_source_restriction": c["mandatory_no_ground_or_surface_water_cooling"],
                    "source": c["source"],
                }
    return None, None


# ---------------------------------------------------------------------------
# VADEQ air-permit generator capacity -- the strongest per-facility power input
# ---------------------------------------------------------------------------
# Permits are issued per SITE and name the buildings they cover, so a permit's
# capacity must be APPORTIONED across those buildings rather than assigned to
# each -- assigning per-building inflates a campus by its building count, the
# same aggregation error that made interconnection.fyi's operator ranges
# unusable. Apportionment is by floor-area share.
#
# Matching is deliberately strict, because three separate join bugs were found
# while validating this pipeline: codenames are not unique across operators
# (VA-10 is both NTT's and Iron Mountain's), substring matching makes IAD-7
# match IAD-74, and GPIN is the parcel rather than the building.
_PERMIT_PATH = os.path.join(_SCRIPT_DIR, "data", "permit_capacity.json")
_OPERATOR_ALIASES = {
    "amazon": ["amazon", "aws"], "microsoft": ["microsoft"], "ntt": ["ntt"],
    "digital realty": ["digital realty", "dlr", "digital third", "digital carver", "porpoise"],
    "equinix": ["equinix"],
    "gainesville crossing": ["gainesville crossing", "gcdc", "corscale"],
    "nova mango": ["nova mango"],
    "iron mountain": ["iron mountain"], "qts": ["qts"],
    "stack": ["stack", "si nva"], "cloudhq": ["cloudhq", "cloud hq"],
    "corporate office properties": ["corporate office properties", "copt"],
    "oath": ["oath"], "comcast": ["comcast"],
}


def _codes(name):
    return [f"{m.group(1)}-{m.group(2)}".upper()
            for m in re.finditer(r'\b(IAD|DCA|MNZ|NVA|VA)[- ]?(\d+[A-Za-z]?)', name or '')]


def _operator(name):
    t = (name or "").lower()
    for canonical, aliases in _OPERATOR_ALIASES.items():
        if any(a in t for a in aliases):
            return canonical
    return None


def build_permit_power_index(buildings_df):
    """Map building name -> permit-derived power inputs.

    Returns {building_name: {registration_no, site_generator_mw, gfa_share,
    n_buildings_on_permit}}.
    """
    if not os.path.exists(_PERMIT_PATH):
        t("  no permit_capacity.json found -- power falls back to the GFA bridge")
        return {}

    permits = [p for p in json.load(open(_PERMIT_PATH)) if p.get("confidence") == "high"]
    rows = []
    for _, b in buildings_df.iterrows():
        nm = clean(b.get("BuildingName"))
        if not nm:
            continue
        g, _f, _q = resolve_gfa(b, _proffer_group_sizes)
        rows.append({"name": nm, "codes": set(_codes(nm)), "op": _operator(nm), "gfa": g or 0.0})

    index = {}
    for p in permits:
        if "prince william" not in (p.get("location") or "").lower():
            continue
        pcodes = set(p.get("building_codes") or [])
        if not pcodes:
            continue
        cands = [r for r in rows if pcodes & r["codes"]]
        ops = [r["op"] for r in cands if r["op"]]
        op = max(set(ops), key=ops.count) if ops else None
        hits = [r for r in cands if r["op"] == op] if op else cands
        # More matches than the permit names means the join is ambiguous; skip
        # rather than guess.
        if not hits or len(hits) > len(pcodes):
            continue
        total_gfa = sum(r["gfa"] for r in hits)
        if not total_gfa:
            continue
        # Buildings on the permit we do not track (usually permitted-but-unbuilt)
        # still draw on the site's capacity, so scale the denominator up as if
        # they were of average size. Without this the tracked buildings absorb
        # the whole site.
        scale = len(pcodes) / len(hits)
        for r in hits:
            index[r["name"]] = {
                "registration_no": p["registration_no"],
                "site_generator_mw": p["permanent_generator_mw"],
                "gfa_share": (r["gfa"] / total_gfa) / scale,
                "n_buildings_on_permit": len(pcodes),
                "n_buildings_matched": len(hits),
                "cooling_evidence": p.get("cooling_evidence"),
            }
    return index


# ---------------------------------------------------------------------------
# Tier 2: operator-matched permits, for the 7 permits that name no buildings
# ---------------------------------------------------------------------------
# Seven high-confidence PWC permits carry no building codenames at all -- QTS,
# Gainesville Crossing, Digital Realty, Nova Mango, CloudHQ, COPT, Comcast --
# holding 902 MW of effective IT power that codename matching cannot reach.
# Every one of them belongs to an operator with exactly ONE Prince William
# permit, which makes operator a safe key for precisely these cases. Amazon (12
# permits) and Microsoft (2) stay on codenames, where the key is ambiguous.
#
# The hazard is that one permit rarely covers an operator's whole county
# portfolio. CloudHQ is the proof: permit 74107 covers the MCC1/MCC6 halls at
# 61 MW, while CloudHQ has 13 buildings totalling 475 MW of GFA-derived load.
# Spreading that permit across all 13 would understate them roughly eightfold.
#
# So a coverage test gates the match: the permit's power must be within the
# range that codename-matched permits actually showed against the GFA bridge
# (0.64-1.61 across 11 sites, so 0.6-1.7 here). This is a test of WHETHER THE
# PERMIT COVERS THIS BUILDING SET, not a calibration of the estimate -- a ratio
# far from 1 means the permit describes a different set of buildings than the
# one it is about to be applied to.
_DEQ_PERMIT_PATH = os.path.join(_SCRIPT_DIR, "data", "vadeq_air_permits_pwc.json")
OPERATOR_COVERAGE_MIN = 0.6
OPERATOR_COVERAGE_MAX = 1.7


def build_operator_permit_index(buildings_df, already_matched, permit_index):
    if not (os.path.exists(_PERMIT_PATH) and os.path.exists(_DEQ_PERMIT_PATH)):
        return {}

    caps = [p for p in json.load(open(_PERMIT_PATH)) if p.get("confidence") == "high"]
    deq = json.load(open(_DEQ_PERMIT_PATH))["permits"]
    site_by_reg = {p["registration_no"].split("-")[0]: p["site_name"] for p in deq}

    # Only operators with exactly one Prince William permit are eligible.
    by_op = {}
    for c in caps:
        if "prince william" not in (c.get("location") or "").lower():
            continue
        op = _operator(site_by_reg.get(c["registration_no"], ""))
        if not op:
            continue
        by_op.setdefault(op, []).append(c)
    eligible = {op: v[0] for op, v in by_op.items() if len(v) == 1}

    # A permit already consumed by codename matching must not be spent again.
    # Iron Mountain's permit 74112 was matched to VA-1/2/3/6/7 by codename, and
    # the operator pass then applied the SAME 148 MW to five further Iron
    # Mountain buildings -- assigning one site's capacity twice.
    spent = {v["registration_no"] for v in permit_index.values()}
    for op in [o for o, p in eligible.items() if p["registration_no"] in spent]:
        t(f"    operator '{op}': permit {eligible[op]['registration_no']} already "
          f"consumed by codename matching -- not reused")
        del eligible[op]

    rows = []
    for _, b in buildings_df.iterrows():
        nm = clean(b.get("BuildingName"))
        if not nm or nm in already_matched:
            continue
        g, _f, _q = resolve_gfa(b, _proffer_group_sizes)
        rows.append({"name": nm, "op": _operator(nm), "gfa": g or 0.0})

    index = {}
    for op, permit in eligible.items():
        hits = [r for r in rows if r["op"] == op and r["gfa"] > 0]
        if not hits:
            continue
        total_gfa = sum(r["gfa"] for r in hits)
        gfa_mw = total_gfa / SQFT_PER_EFFECTIVE_MW
        ratio = permit["effective_it_mw"] / gfa_mw if gfa_mw else 0
        if not (OPERATOR_COVERAGE_MIN <= ratio <= OPERATOR_COVERAGE_MAX):
            t(f"    operator '{op}': permit {permit['registration_no']} rejected, "
              f"coverage ratio {ratio:.2f} outside [{OPERATOR_COVERAGE_MIN}, {OPERATOR_COVERAGE_MAX}] "
              f"({len(hits)} buildings) -- the permit does not cover this building set")
            continue
        t(f"    operator '{op}': permit {permit['registration_no']} accepted, "
          f"coverage ratio {ratio:.2f} across {len(hits)} buildings")
        for r in hits:
            index[r["name"]] = {
                "registration_no": permit["registration_no"],
                "site_generator_mw": permit["permanent_generator_mw"],
                "gfa_share": r["gfa"] / total_gfa,
                "n_buildings_on_permit": len(hits),
                "n_buildings_matched": len(hits),
                "match_basis": "operator_single_permit",
                "coverage_ratio": round(ratio, 2),
                "cooling_evidence": permit.get("cooling_evidence"),
            }
    return index


_permit_power_index = build_permit_power_index(dc_buildings)
t(f"  buildings matched to a permit by BUILDING CODENAME: {len(_permit_power_index)}")
_operator_index = build_operator_permit_index(dc_buildings, set(_permit_power_index), _permit_power_index)
t(f"  buildings matched to a permit by OPERATOR (single-permit operators): {len(_operator_index)}")
for _k, _v in _operator_index.items():
    _permit_power_index.setdefault(_k, _v)
t(f"  buildings with permit-derived power: {len(_permit_power_index)} of {len(dc_buildings)}")

building_profiles = []
for _, b in dc_buildings.iterrows():
    geom = b.geometry
    host = parcels[parcels.intersects(geom)]
    gpin = host.iloc[0]["GPIN"] if len(host) else None
    water_ctx = water_context_for_gpin(gpin) if gpin else None
    if water_ctx is None and len(host):
        water_ctx, _ = water_context_for_geometry(geom)

    year_built = int(y) if (y := clean(b.get("YearBuilt"))) is not None else None
    gfa_val, gfa_field, gfa_quality = resolve_gfa(b, _proffer_group_sizes)

    use_permits_here = matched_cases(geom, use_permits, ["ZoningCaseNumber", "UsePermitType", "ZoningCaseName", "DateApproved", "DateExpired", "UsePermitStatus"])
    bza_here = matched_cases(geom, bza, ["BZACaseNumber", "BZACaseType", "BZACaseName"])
    pending_here = matched_cases(geom, pending, ["PlanningCaseNumber", "PlanningCaseType", "PlanningCaseName", "TransmittalDate", "StaffReportLink"])
    pue_cap, cooling_disc = permit_conditions_for(use_permits_here + bza_here + pending_here)

    # A VADEQ permit that lists cooling towers as permitted equipment is direct
    # evidence of evaporative cooling. It is merged in only where a county
    # proffer has not already spoken, so a binding local condition still wins.
    _pp = _permit_power_index.get(clean(b.get("BuildingName"))) or {}
    _ce = _pp.get("cooling_evidence")
    if _ce and not cooling_disc:
        cooling_disc = {
            "evaporative": True,
            "air_or_closed_loop": False,
            "source": (
                f"VADEQ air permit {_pp['registration_no']} lists cooling towers as permitted "
                f"equipment ({_ce['evidence']})."
            ),
        }

    profile = {
        "kind": "building",
        "id": clean(b.get("BuildingID")) or None,
        "name": clean(b.get("BuildingName")),
        "gpin": gpin,
        "address": clean(b.get("Address")),
        "status": clean(b.get("BuildingStatus")),
        "year_built": year_built,
        "gfa_sqft": gfa_val,
        "gfa_field_used": gfa_field,
        "gfa_quality": gfa_quality,
        "permit_case": clean(b.get("PermitCase")) or None,
        "permit_status": clean(b.get("PermitStatus")) or None,
        "use_permits": use_permits_here,
        "bza_cases": bza_here,
        "pending_cases": pending_here,
        "permit_cooling_conditions": cooling_disc,
        "water_context": water_ctx,
        "scope_water_footprint": estimate_scope_water_footprint(
            b.get("BuildingName"), gfa_sqft=gfa_val, gfa_source=gfa_field,
            gfa_quality=gfa_quality, year_built=year_built,
            d_hv_transmission_ft=(water_ctx or {}).get("d_hv_transmission_ft"),
            cdd=(water_ctx or {}).get("cdd"),
            pue_cap=pue_cap, cooling_disclosure=cooling_disc,
            permit_power=_permit_power_index.get(clean(b.get("BuildingName"))),
            status=clean(b.get("BuildingStatus")),
        ),
    }
    building_profiles.append(profile)
t(f"  built {len(building_profiles)} building profiles")

campus_profiles = []
for _, c in dc_projects.iterrows():
    geom = c.geometry
    water_ctx, gpins = water_context_for_geometry(geom)
    buildings_here = [
        bp["id"] for bp in building_profiles
        if bp["gpin"] and bp["gpin"] in gpins and bp["id"]
    ]
    campus_gfa_val, campus_gfa_field = coalesce_gfa(c, fields=["PlannedGFA", "RemainingGFA"])

    # Campuses were never run through permit_conditions_for(), so a proffer
    # cooling condition attached to a REZONING case was silently dropped for all
    # 51 of them -- REZ2025-00003's cooling and PUE menu items sit on the Aura
    # Development CAMPUS record, not on any building, and so never surfaced.
    campus_use = matched_cases(geom, use_permits, ["ZoningCaseNumber", "UsePermitType", "ZoningCaseName", "DateApproved", "DateExpired", "UsePermitStatus"])
    campus_bza = matched_cases(geom, bza, ["BZACaseNumber", "BZACaseType", "BZACaseName"])
    campus_pending = matched_cases(geom, pending, ["PlanningCaseNumber", "PlanningCaseType", "PlanningCaseName", "TransmittalDate", "StaffReportLink"])
    campus_pue_cap, campus_cooling = permit_conditions_for(campus_use + campus_bza + campus_pending)

    profile = {
        "kind": "campus",
        "case_number": clean(c.get("CaseNumber")),
        "name": clean(c.get("CaseName")),
        "zoning_district": clean(c.get("ZoningDistrict")),
        "remaining_gfa_sqft": clean(c.get("RemainingGFA")),
        "planned_gfa_sqft": clean(c.get("PlannedGFA")),
        "gis_acreage": clean(c.get("GISAcreage")),
        "n_parcels": len(gpins),
        "gpins": gpins[:50],  # cap for payload size; full list rarely needed client-side
        "built_buildings_on_site": buildings_here,
        "use_permits": campus_use,
        "bza_cases": campus_bza,
        "pending_cases": campus_pending,
        "permit_cooling_conditions": campus_cooling,
        "water_context": water_ctx,
        "scope_water_footprint": estimate_scope_water_footprint(
            c.get("CaseName"), gfa_sqft=campus_gfa_val, gfa_source=campus_gfa_field,
            gfa_quality="entitlement", year_built=None,
            d_hv_transmission_ft=(water_ctx or {}).get("d_hv_transmission_ft"),
            cdd=(water_ctx or {}).get("cdd"),
            pue_cap=campus_pue_cap, cooling_disclosure=campus_cooling,
            status="Planned",
        ),
    }
    campus_profiles.append(profile)
t(f"  built {len(campus_profiles)} campus profiles")

out = {
    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "buildings": building_profiles,
    "campuses": campus_profiles,
}
out_path = os.path.join(OUT_ROOT, "facility_profiles.json")
with open(out_path, "w") as f:
    json.dump(out, f, separators=(",", ":"), default=str, allow_nan=False)
size_kb = os.path.getsize(out_path) / 1024
t(f"Wrote {out_path} ({size_kb:.0f} KB)")
t("DONE.")
