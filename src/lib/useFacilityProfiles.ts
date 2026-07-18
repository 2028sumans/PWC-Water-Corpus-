"use client";

/**
 * Loads the per-facility evidence dossiers produced by
 * build_facility_profiles.py — one record per data-center BUILDING (203)
 * and one per CAMPUS/project (51). This is deliberately not a water-demand
 * estimator: every field is either directly observed (a permit case number,
 * a year built, a matched staff report) or absent. The Right Panel renders
 * this as a checklist so an analyst can see exactly which claims about a
 * facility are backed by a public record and which are not — the same
 * observable/inferable/unresolved discipline the sub-scores apply, just at
 * facility granularity instead of parcel granularity.
 */
import { useEffect, useState } from "react";

export interface FacilityCaseRecord {
  ZoningCaseNumber?: string;
  UsePermitType?: string;
  ZoningCaseName?: string | null;
  DateApproved?: string | null;
  DateExpired?: string | null;
  UsePermitStatus?: string;
  BZACaseNumber?: string;
  BZACaseType?: string;
  BZACaseName?: string | null;
  PlanningCaseNumber?: string;
  PlanningCaseType?: string;
  PlanningCaseName?: string;
  TransmittalDate?: string;
  StaffReportLink?: string;
}

export interface FacilityWaterContext {
  watershed_name: string | null;
  watershed_acres: number | null;
  n_dc_in_watershed: number | null;
  watershed_major_basin: string | null;
  n_dc_in_major_basin: number | null;
  d_stream_ft: number | null;
  stream_order: number | null;
  stream_name: string | null;
  d_hydro_ft: number | null;
  d_spring_ft: number | null;
  rpa: number | null;
  wetland: number | null;
  in_tidal_flow_path: number | null;
  tidal_class: string | null;
  tidal_zone: string | null;
  dam: number | null;
  dam_haz_class: string | null;
  soil_cat: string | null;
  hsg: string | null;
  erosion_susceptibility: number | null;
  soil_permeability: number | null;
  near_h2oquality_protected_land: number | null;
  sw_segments: number | null;
  sw_structures: number | null;
  sw_facilities: number | null;
  n_wqp_stations_1mi: number | null;
  n_deq_monitoring_1mi: number | null;
  n_deq_gage_1mi: number | null;
  nearest_benthic_n: number | null;
  n_inat_1mi: number | null;
  n_inat_research_1mi: number | null;
  has_npdes: number | null;
  has_deq_permit: number | null;
  n_npdes_violations: number | null;
  dmr_nodi_code: string | null;
  dmr_flow_mgd: number | null;
  echo_facility_name: string | null;
  general_permit_type: string | null;
  compliance_status: string | null;
  frs_id: string | null;
  d_transmission_ft: number | null;
  d_hv_transmission_ft: number | null;
  nearest_hv_sub_1: string | null;
  nearest_hv_sub_2: string | null;
  zoning: string | null;
  cdd: number | null;                          // trailing-12mo cooling degree days (countywide)
  has_proffers: number | null;                 // this zoning district has a proffered rezoning on record
  watershed_mgmt_plan_number: string | null;    // PWC Watershed Management Plan section reference
}

export interface GfaPowerEstimate {
  gfa_sqft: number;
  density_class: "standard" | "modern_ai" | "unknown";
  it_power_density_w_per_sqft: [number, number];
  it_mw_range: [number, number];
  pue_class: "modern" | "standard" | "unknown";
  pue_range: [number, number];
  facility_mw_range: [number, number];
}

export interface ScopePowerEstimate {
  mw_range: [number, number];
  basis: "intersection" | "disagreement" | "gfa_only" | "operator_only";
  note: string;
  gfa_estimate: GfaPowerEstimate | null;
  gfa_field_used: string | null;
  operator_match: { operator: string; mw_range: [number, number] } | null;
  source: string | null;
  hv_plausibility: string | null;
}

export interface Scope1Onsite {
  mgd_range: [number, number];
  wue_range_l_per_kwh: [number, number];
  climate_weighted_point_mgd: number | null;
  climate_weighted_wue_l_per_kwh: number | null;
  climate_note: string | null;
  methodology: string;
  note: string;
}

export interface Scope2Electricity {
  mgd_range: [number, number];
  blended_consumption_gal_per_mwh: number;
  assumed_utilization: number;
  methodology: string;
}

export interface Scope3Embodied {
  mgd_range: [number, number];
  proportional_range: [number, number];
  methodology: string;
  note: string;
}

export interface ScopeWaterFootprint {
  power: ScopePowerEstimate;
  scope1_onsite_cooling: Scope1Onsite;
  scope2_electricity: Scope2Electricity;
  scope3_embodied: Scope3Embodied;
  total_mgd_range: [number, number];
  total_note: string;
}

export interface BuildingProfile {
  kind: "building";
  id: string | null;
  name: string | null;
  gpin: string | null;
  address: string | null;
  status: string | null;
  year_built: number | null;
  gfa_sqft: number | null;
  gfa_field_used: string | null;
  permit_case: string | null;
  permit_status: string | null;
  use_permits: FacilityCaseRecord[];
  bza_cases: FacilityCaseRecord[];
  pending_cases: FacilityCaseRecord[];
  water_context: FacilityWaterContext | null;
  scope_water_footprint: ScopeWaterFootprint | null;
}

export interface CampusProfile {
  kind: "campus";
  case_number: string | null;
  name: string | null;
  zoning_district: string | null;
  remaining_gfa_sqft: number | null;
  planned_gfa_sqft: number | null;
  gis_acreage: number | null;
  n_parcels: number;
  gpins: string[];
  built_buildings_on_site: string[];
  use_permits: FacilityCaseRecord[];
  bza_cases: FacilityCaseRecord[];
  pending_cases: FacilityCaseRecord[];
  water_context: FacilityWaterContext | null;
  scope_water_footprint: ScopeWaterFootprint | null;
}

interface FacilityProfilesFile {
  generated_at: string;
  buildings: BuildingProfile[];
  campuses: CampusProfile[];
}

let _cache: FacilityProfilesFile | null = null;

export function useFacilityProfiles() {
  const [data, setData] = useState<FacilityProfilesFile | null>(_cache);

  useEffect(() => {
    if (_cache) return;
    let cancelled = false;
    fetch("/data/facility_profiles.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((d: FacilityProfilesFile | null) => {
        if (cancelled || !d) return;
        _cache = d;
        setData(d);
      })
      .catch(() => {
        // Optional file — the panel just won't show a dossier section.
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}

/** Building profile hosted on this exact parcel, if any. */
export function findBuildingByGpin(gpin: string): BuildingProfile | undefined {
  return _cache?.buildings.find((b) => b.gpin === gpin);
}

/** Campus profile whose polygon covers this parcel, if any. */
export function findCampusByGpin(gpin: string): CampusProfile | undefined {
  return _cache?.campuses.find((c) => c.gpins.includes(gpin));
}
