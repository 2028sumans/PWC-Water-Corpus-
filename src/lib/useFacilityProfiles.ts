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

/** How trustworthy this facility's floor-area figure is. `proffer_split`
 * means only a site-wide proffered entitlement existed and it was divided
 * evenly across the buildings sharing it. */
export type GfaQuality = "assessed" | "permit" | "estimated" | "proffer_split" | "entitlement";

export interface OperatorCrossCheck {
  operator: string;
  operator_mw_range: [number, number];
  agrees: boolean;
  note: string;
}

/** Permit-derived power provenance, present only when basis is
 *  "permit_generator_capacity". A permit covers a SITE, so site_generator_mw is
 *  the whole site's permitted capacity and gfa_share apportions this building's
 *  slice of it. */
export interface ScopePermitPower {
  registration_no: string;
  site_generator_mw: number;
  gfa_share: number;
  n_buildings_on_permit: number;
  n_buildings_matched: number;
  /** Fraction of permitted capacity that is NON-EMERGENCY. ICPRB's 0.5
   *  redundancy factor assumes 2N emergency backup, so a high share here means
   *  the halving is weakly justified for this site. */
  non_emergency_share?: number | null;
  redundancy_assumption_note?: string | null;
}

export interface ScopePowerEstimate {
  effective_it_mw_range: [number, number];
  effective_it_mw_central: number;
  /**
   * "permit_generator_capacity" means power came from a VADEQ air permit's
   * generator schedule via ICPRB Equation 6-3, and the 8,818 sqft/MW density
   * bridge was NOT used for this building.
   */
  basis: "gfa_icprb_density" | "permit_generator_capacity";
  permit: ScopePermitPower | null;
  sqft_per_effective_mw: number;
  /** Build-era band actually used for this building's density, and the figure
   *  it resolved to. Null when power came from a permit, which bypasses
   *  density entirely. */
  /**
   * A build-era band (new_build/modern/standard/legacy/unknown), OR an
   * `operator_<name>` label when the density was calibrated to that operator's
   * own permit-backed buildings in the county rather than to a build year —
   * which is a better predictor and is empirical rather than assumed.
   */
  density_class:
    | "new_build" | "modern" | "standard" | "legacy" | "unknown"
    | `operator_${string}` | null;
  density_sqft_per_mw_used: number | null;
  density_source: string | null;
  gfa_sqft: number;
  gfa_field_used: string | null;
  gfa_quality: GfaQuality | null;
  note: string;
  operator_cross_check: OperatorCrossCheck | null;
  hv_plausibility: string | null;
}

export interface Scope1Onsite {
  mgd_range: [number, number];
  mgd_central: number;
  peak_day_mgd: number;
  consumptive_mgd_central: number;
  wup_gal_per_mw_day: { low: number; central: number; high: number };
  wup_reference_tiers: Record<string, number>;
  /** How the technology envelope was narrowed, best evidence first. */
  /**
   * "disclosed_cooling_evaporative" is evidence pointing the OTHER way from the
   * narrowing cases: cooling towers listed as permitted equipment in the
   * facility's VADEQ air permit, which lifts the estimate off the air-cooled
   * floor rather than pulling it down to one.
   */
  basis:
    | "disclosed_cooling"
    | "disclosed_cooling_evaporative"
    | "operator_closed_loop_commitment"
    | "technology_envelope";
  narrowed_by: string | null;
  methodology: string;
  note: string;
}

export interface Scope2Electricity {
  mgd_range: [number, number];
  mgd_central: number;
  /**
   * "operator_disclosed" means the operator publishes a fleet PUE and it was
   * used directly; the vintage classes are inferences from a build date, and
   * "new_build" covers unbuilt facilities, which are going up to current
   * practice rather than being of unknown vintage.
   */
  pue_class:
    | "operator_disclosed"
    | "new_build"
    | "modern"
    | "standard"
    | "legacy"
    | "unknown";
  pue_range: [number, number];
  pue_capped_by_proffer: boolean;
  /** Citation for a disclosed fleet PUE; null when a vintage class was used. */
  pue_source: string | null;
  blended_consumption_gal_per_mwh: number;
  /** GHG Protocol requires both. mgd_central above is the location-based one. */
  accounting_basis: "location_based";
  /**
   * What the operator would publish, given its renewable-matching claim. Null
   * for operators with no such claim on file. Contractual, not physical: a REC
   * does not stop the plant that actually served this building evaporating.
   */
  market_based: {
    mgd_central: number;
    renewable_matched_share: number;
    effective_gal_per_mwh: number;
    claim: string;
    caveat: string;
  } | null;
  methodology: string;
  note: string;
}

export interface Scope3Embodied {
  mgd_range: [number, number];
  mgd_central: number;
  proportional_range: [number, number];
  methodology: string;
  note: string;
}

/** Plausibility check of the modeled Scope 1 figure against JLARC's measured
 * per-building water use for Virginia data centers (2023). */
export interface BenchmarkCheck {
  flag: "exceeds_largest_measured" | "large" | "typical_or_below" | "normal";
  verdict: string;
  reference_mgd: Record<string, number>;
}

export interface ScopeWaterFootprint {
  power: ScopePowerEstimate;
  scope1_onsite_cooling: Scope1Onsite;
  scope2_electricity: Scope2Electricity;
  scope3_embodied: Scope3Embodied;
  total_mgd_range: [number, number];
  total_mgd_central: number;
  /**
   * The same total with ICPRB's 0.75 consumptive-use factor applied to Scope 1.
   * total_mgd_central mixes bases: Scope 1 is DELIVERED water (ICPRB's WUP
   * intensities come from utility billing records, so blowdown returning to the
   * basin is counted), while Scope 2 is CONSUMPTION at the generating plant.
   * Use delivered against utility supply, consumptive against basin balance.
   */
  total_consumptive_mgd_central: number;
  total_basis_note: string;
  total_note: string;
  benchmark: BenchmarkCheck;
}

export interface PermitCoolingConditions {
  air_or_closed_loop: boolean;
  mandatory_source_restriction: boolean;
  /** True when the proffer regulates air-cooled chillers without requiring
   *  them — evidence the applicant anticipates air cooling, not a commitment. */
  anticipates_air_cooled_chillers?: boolean;
  source: string;
}

export interface EPortalCoolingPermit {
  permit_no: string | null;
  permit_type: string | null;
  status: string | null;
  description: string | null;
  matched_term: string | null;
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
  gfa_quality: GfaQuality | null;
  permit_case: string | null;
  permit_status: string | null;
  use_permits: FacilityCaseRecord[];
  bza_cases: FacilityCaseRecord[];
  pending_cases: FacilityCaseRecord[];
  permit_cooling_conditions: PermitCoolingConditions | null;
  /** County ePortal trade permits naming cooling equipment on this parcel.
   *  Evidence only — a chiller permit does not say how heat is finally
   *  rejected, so it never narrows the Scope 1 estimate. */
  eportal_cooling_permits: EPortalCoolingPermit[];
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
  /** Entitlement GFA / (acres x 43,560). Prince William transects cap FAR at
   *  0.57 (I-3 transect 3) and 1.38 (highest); approved data centres cluster at
   *  0.50-0.55. A campus above those cannot physically fit its stated floor
   *  area — usually because an entitlement figure was repeated from a larger
   *  site. */
  implied_far: number | null;
  far_flag: "exceeds_i3_transect" | "exceeds_all_transects" | null;
  n_parcels: number;
  gpins: string[];
  built_buildings_on_site: string[];
  use_permits: FacilityCaseRecord[];
  bza_cases: FacilityCaseRecord[];
  pending_cases: FacilityCaseRecord[];
  permit_cooling_conditions: PermitCoolingConditions | null;
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
