/**
 * Enumerate the data layers that go into a parcel's Data Depth score and
 * report which are present vs missing. Data Depth = (present points /
 * total possible points) * 100, computed dynamically from the rows below
 * (see convictionSummary) rather than a hardcoded layer count. This file
 * mirrors preprocess_score_parcels.py's bookkeeping so the right panel can
 * show "checking the work" when a user clicks the Data Depth badge.
 */
import type { ScoredParcel } from "@/lib/useScoredParcels";

export interface ConvictionRow {
  /** Short label shown in the popover list. */
  label: string;
  /** Data-depth point contribution if present. */
  points: number;
  /** Whether this signal contributed real data for this parcel. */
  present: boolean;
  /** Human-readable value to display when present. */
  detail?: string;
  /** Category for visual grouping. */
  group: "Watershed & hydrology" | "Drought & climate" | "Disclosure" | "Community monitoring" | "Stormwater & hazard" | "Power & permitting";
}

function fmt(v: string | number | null | undefined, suffix = ""): string {
  if (v === null || v === undefined || v === "") return "—";
  return `${v}${suffix}`;
}

export function convictionGaps(p: ScoredParcel): ConvictionRow[] {
  return [
    // Watershed & hydrology
    { label: "Watershed join", points: 3, present: p.watershed_id != null, detail: fmt(p.watershed_name), group: "Watershed & hydrology" },
    { label: "Stream distance", points: 3, present: p.d_stream_ft != null, detail: p.d_stream_ft != null ? `${p.d_stream_ft.toFixed(0)} ft` : undefined, group: "Watershed & hydrology" },
    { label: "Spring/groundwater distance", points: 3, present: p.d_spring_ft != null, detail: p.d_spring_ft != null ? `${p.d_spring_ft.toFixed(0)} ft` : undefined, group: "Watershed & hydrology" },
    { label: "Hydrology features distance", points: 3, present: p.d_hydro_ft != null, detail: p.d_hydro_ft != null ? `${p.d_hydro_ft.toFixed(0)} ft` : undefined, group: "Watershed & hydrology" },
    { label: "RPA overlap", points: 2, present: p.rpa !== undefined, detail: p.rpa ? "inside RPA" : "outside RPA", group: "Watershed & hydrology" },
    { label: "Soil construction category", points: 2, present: !!p.soil_cat, detail: fmt(p.soil_cat), group: "Watershed & hydrology" },
    { label: "Surface water temperature", points: 2, present: p.d_surftemp_ft != null, detail: p.d_surftemp_ft != null ? `${p.d_surftemp_ft.toFixed(0)} ft to nearest station` : undefined, group: "Watershed & hydrology" },
    { label: "Stream warming trend (Mann-Kendall/Theil-Sen)", points: 3, present: !!p.surftemp_trend, detail: p.surftemp_trend ? `${p.surftemp_trend}${p.surftemp_theilsen_slope != null ? ` (${p.surftemp_theilsen_slope > 0 ? "+" : ""}${p.surftemp_theilsen_slope.toFixed(3)}°F/yr)` : ""}` : undefined, group: "Watershed & hydrology" },
    { label: "Nearest spring/groundwater chemistry", points: 2, present: p.spring_ph != null, detail: p.spring_ph != null ? `pH ${p.spring_ph}${p.spring_sample_date ? ` (sampled ${p.spring_sample_date.slice(0, 10)})` : ""}` : undefined, group: "Watershed & hydrology" },
    { label: "Hydrologic soil group", points: 2, present: !!p.hsg, detail: fmt(p.hsg), group: "Watershed & hydrology" },
    { label: "Erosion susceptibility", points: 1, present: p.erosion_susceptibility != null, detail: p.erosion_susceptibility != null ? p.erosion_susceptibility.toFixed(2) : undefined, group: "Watershed & hydrology" },
    { label: "Protected open space adjacency", points: 1, present: p.near_protected_open_space !== undefined, detail: p.near_protected_open_space ? "adjacent" : "not adjacent", group: "Watershed & hydrology" },
    { label: "Watershed major basin", points: 1, present: !!p.watershed_major_basin, detail: fmt(p.watershed_major_basin), group: "Watershed & hydrology" },
    { label: "Watershed management plan reference", points: 1, present: !!p.watershed_mgmt_plan_number, detail: fmt(p.watershed_mgmt_plan_number), group: "Watershed & hydrology" },
    { label: "Cedar Run gage height", points: 2, present: p.cedar_run_gage_height_ft != null, detail: p.cedar_run_gage_height_ft != null ? `${p.cedar_run_gage_height_ft} ft (stage, not discharge)` : undefined, group: "Watershed & hydrology" },
    { label: "Groundwater well depth", points: 2, present: p.gw_depth_ft != null, detail: p.gw_depth_ft != null ? `${p.gw_depth_ft} ft` : undefined, group: "Watershed & hydrology" },
    { label: "Tidal flow path", points: 1, present: p.in_tidal_flow_path !== undefined, detail: p.in_tidal_flow_path ? `in tidal flow path${p.tidal_class ? ` (VA WQS Class ${p.tidal_class})` : ""}` : "not tidal", group: "Watershed & hydrology" },
    { label: "Stream order (StreamType)", points: 1, present: p.stream_order != null && p.stream_order > 0, detail: p.stream_order != null && p.stream_order > 0 ? `order ${p.stream_order}${p.stream_name ? ` (${p.stream_name})` : ""}` : undefined, group: "Watershed & hydrology" },
    { label: "Water-quality-protected land adjacency", points: 1, present: p.near_h2oquality_protected_land !== undefined, detail: p.near_h2oquality_protected_land ? "adjacent (H2OQuality=Yes)" : "not adjacent", group: "Watershed & hydrology" },

    // Drought & climate
    { label: "PDSI", points: 2, present: p.pdsi != null, detail: p.pdsi?.toFixed(2), group: "Drought & climate" },
    { label: "PHDI", points: 2, present: p.phdi != null, detail: p.phdi?.toFixed(2), group: "Drought & climate" },
    { label: "PMDI", points: 2, present: p.pmdi != null, detail: p.pmdi?.toFixed(2), group: "Drought & climate" },
    { label: "Palmer Z-Index", points: 2, present: p.palmer_z != null, detail: p.palmer_z?.toFixed(2), group: "Drought & climate" },
    { label: "Average temp", points: 1, present: p.avg_temp_f != null, detail: p.avg_temp_f != null ? `${p.avg_temp_f}°F` : undefined, group: "Drought & climate" },
    { label: "Max temp", points: 1, present: p.max_temp_f != null, detail: p.max_temp_f != null ? `${p.max_temp_f}°F` : undefined, group: "Drought & climate" },
    { label: "Min temp", points: 1, present: p.min_temp_f != null, detail: p.min_temp_f != null ? `${p.min_temp_f}°F` : undefined, group: "Drought & climate" },
    { label: "Cooling degree days", points: 1, present: p.cdd != null, detail: fmt(p.cdd), group: "Drought & climate" },
    { label: "Heating degree days", points: 1, present: p.hdd != null, detail: fmt(p.hdd), group: "Drought & climate" },
    { label: "Precipitation", points: 1, present: p.precip_in != null, detail: p.precip_in != null ? `${p.precip_in} in` : undefined, group: "Drought & climate" },
    { label: "Manassas precipitation", points: 1, present: p.precip_manassas_in != null, detail: p.precip_manassas_in != null ? `${p.precip_manassas_in} in` : undefined, group: "Drought & climate" },

    // Disclosure
    { label: "NPDES facility flag", points: 4, present: p.has_npdes !== undefined, detail: p.has_npdes ? "has NPDES permit" : "no NPDES permit", group: "Disclosure" },
    { label: "DEQ permit flag", points: 3, present: p.has_deq_permit !== undefined, detail: p.has_deq_permit ? "has DEQ permit" : "no DEQ permit", group: "Disclosure" },
    { label: "NPDES violations (ECHO)", points: 2, present: p.n_npdes_violations != null, detail: p.n_npdes_violations != null ? `${p.n_npdes_violations} violations` : undefined, group: "Disclosure" },
    { label: "DMR discharge monitoring", points: 2, present: p.dmr_nodi_code != null, detail: fmt(p.dmr_nodi_code), group: "Disclosure" },
    { label: "ECHO compliance status", points: 2, present: p.compliance_status != null, detail: fmt(p.compliance_status), group: "Disclosure" },
    { label: "FRS registry linkage", points: 1, present: p.frs_id != null, detail: fmt(p.frs_id), group: "Disclosure" },
    { label: "Municipal supply aggregate", points: 2, present: p.utility_aggregate_available !== undefined, detail: p.utility_aggregate_available ? "PW Water disclosed" : undefined, group: "Disclosure" },

    // Community monitoring
    { label: "WQP monitoring stations (1mi)", points: 3, present: p.n_wqp_stations_1mi != null, detail: p.n_wqp_stations_1mi != null ? `${p.n_wqp_stations_1mi} stations` : undefined, group: "Community monitoring" },
    { label: "DEQ monitoring stations (1mi)", points: 2, present: p.n_deq_monitoring_1mi != null, detail: p.n_deq_monitoring_1mi != null ? `${p.n_deq_monitoring_1mi} stations` : undefined, group: "Community monitoring" },
    { label: "DEQ stream gages (1mi)", points: 2, present: (p.n_deq_gage_1mi ?? 0) > 0, detail: (p.n_deq_gage_1mi ?? 0) > 0 ? `${p.n_deq_gage_1mi} flow-measurement stations` : undefined, group: "Community monitoring" },
    { label: "Benthic macroinvertebrate sampling", points: 1, present: p.nearest_benthic_n != null, detail: p.nearest_benthic_n != null ? `n=${p.nearest_benthic_n} at nearest station` : undefined, group: "Community monitoring" },
    { label: "iNaturalist observations (1mi)", points: 2, present: p.n_inat_1mi != null, detail: p.n_inat_1mi != null ? `${p.n_inat_1mi} observations (${p.n_inat_research_1mi ?? 0} research-grade)` : undefined, group: "Community monitoring" },

    // Stormwater & hazard
    { label: "Stormwater segments", points: 2, present: p.sw_segments != null, detail: p.sw_segments != null ? `${p.sw_segments} crossing` : undefined, group: "Stormwater & hazard" },
    { label: "Stormwater structures", points: 2, present: p.sw_structures != null, detail: p.sw_structures != null ? `${p.sw_structures} structures` : undefined, group: "Stormwater & hazard" },
    { label: "Stormwater facilities", points: 2, present: p.sw_facilities != null, detail: p.sw_facilities != null ? `${p.sw_facilities} basins` : undefined, group: "Stormwater & hazard" },
    { label: "Dam-break inundation", points: 2, present: p.dam !== undefined, detail: p.dam ? fmt(p.dam_haz_class) : "outside zone", group: "Stormwater & hazard" },

    // Power & permitting
    { label: "Use permits on parcel", points: 1, present: p.n_use_permits_on_parcel != null, detail: fmt(p.n_use_permits_on_parcel), group: "Power & permitting" },
    { label: "Transmission line distance", points: 1, present: p.d_transmission_ft != null, detail: p.d_transmission_ft != null ? `${p.d_transmission_ft.toFixed(0)} ft` : undefined, group: "Power & permitting" },
    { label: "In-service ≥230kV line distance", points: 2, present: p.d_hv_transmission_ft != null, detail: p.d_hv_transmission_ft != null ? `${p.d_hv_transmission_ft.toFixed(0)} ft${p.nearest_hv_sub_1 ? ` (${p.nearest_hv_sub_1}${p.nearest_hv_sub_2 && p.nearest_hv_sub_2 !== "NOT AVAILABLE" ? `–${p.nearest_hv_sub_2}` : ""})` : ""}` : undefined, group: "Power & permitting" },
    { label: "Interconnection queue count nearby", points: 1, present: p.n_queued_projects_nearby != null, detail: fmt(p.n_queued_projects_nearby), group: "Power & permitting" },
    { label: "PJM zone load growth", points: 1, present: p.pjm_zone_load_growth_pct != null, detail: p.pjm_zone_load_growth_pct != null ? `${p.pjm_zone_load_growth_pct}%/yr` : undefined, group: "Power & permitting" },
    { label: "Zoning proffer conditions", points: 1, present: p.has_proffers !== undefined, detail: p.has_proffers ? "proffered rezoning on record" : "no proffers on record", group: "Power & permitting" },
  ];
}

export function convictionSummary(rows: ConvictionRow[]) {
  const present = rows.filter((r) => r.present);
  const missing = rows.filter((r) => !r.present);
  const totalContributed = present.reduce((s, r) => s + r.points, 0);
  const totalPossible = rows.reduce((s, r) => s + r.points, 0);
  return { present, missing, totalContributed, totalPossible };
}
