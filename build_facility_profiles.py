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
import os
import time

import geopandas as gpd
import pandas as pd

from indirect_water_footprint import (
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
        "use_permits": matched_cases(geom, use_permits, ["ZoningCaseNumber", "UsePermitType", "ZoningCaseName", "DateApproved", "DateExpired", "UsePermitStatus"]),
        "bza_cases": matched_cases(geom, bza, ["BZACaseNumber", "BZACaseType", "BZACaseName"]),
        "pending_cases": matched_cases(geom, pending, ["PlanningCaseNumber", "PlanningCaseType", "PlanningCaseName", "TransmittalDate", "StaffReportLink"]),
        "water_context": water_ctx,
        "scope_water_footprint": estimate_scope_water_footprint(
            c.get("CaseName"), gfa_sqft=campus_gfa_val, gfa_source=campus_gfa_field,
            gfa_quality="entitlement", year_built=None,
            d_hv_transmission_ft=(water_ctx or {}).get("d_hv_transmission_ft"),
            cdd=(water_ctx or {}).get("cdd"),
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
