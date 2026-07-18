/**
 * Single source of truth for every overlay layer the Spatial Map can render.
 *
 * Each entry pairs the Zustand store key (`id`) used by the toggle
 * checkboxes with the bundled PMTiles filename, the source-layer name baked
 * in by tippecanoe, and the paint properties for a MapLibre Layer.
 *
 * Color convention: blues/teals for water layers, grays for infrastructure,
 * amber/red for disclosure gaps and hazards, the accent color (#4fa3d1) for
 * data-center infrastructure.
 */

export type LayerGroup = "Hydrology" | "Hazard & Stormwater" | "Disclosure" | "Monitoring" | "Power & Land";

export interface MapLayerSpec {
  id: string;
  label: string;
  group: LayerGroup;
  pmtilesFile: string;
  sourceLayer: string;
  kind: "fill" | "line" | "circle";
  outline?: boolean;
  color: string;
  fillOpacity?: number;
  lineWidth?: number;
  minzoom?: number;
  patternImage?: string;
  circleRadiusBase?: number;
  circleStrokeColor?: string;
  circleStrokeWidth?: number;
}

export const MAP_LAYERS: MapLayerSpec[] = [
  // ===== HYDROLOGY (blues/teals) =====
  {
    id: "watersheds",
    label: "Watersheds",
    group: "Hydrology",
    pmtilesFile: "watersheds.pmtiles",
    sourceLayer: "watersheds",
    kind: "fill",
    outline: true,
    color: "#4fa3d1",
    fillOpacity: 0.1,
    lineWidth: 1,
  },
  {
    id: "streams",
    label: "Streams",
    group: "Hydrology",
    pmtilesFile: "streams.pmtiles",
    sourceLayer: "streams",
    kind: "line",
    color: "#38bdf8",
    lineWidth: 1,
  },
  {
    id: "hydrologyFeatures",
    label: "Hydrological Features",
    group: "Hydrology",
    pmtilesFile: "hydrology.pmtiles",
    sourceLayer: "hydrology",
    kind: "fill",
    color: "#0ea5e9",
    fillOpacity: 0.25,
  },
  {
    id: "rpa",
    label: "Resource Protection Areas (RPA)",
    group: "Hydrology",
    pmtilesFile: "rpa.pmtiles",
    sourceLayer: "rpa",
    kind: "fill",
    outline: true,
    color: "#7dd3c0",
    fillOpacity: 0.22,
    lineWidth: 1,
  },
  {
    id: "groundwaterSprings",
    label: "Springs / Groundwater",
    group: "Hydrology",
    pmtilesFile: "springs.pmtiles",
    sourceLayer: "springs",
    kind: "circle",
    color: "#22d3ee",
    circleRadiusBase: 5,
  },
  {
    id: "surfaceWaterTemp",
    label: "Surface Water Temperature",
    group: "Hydrology",
    pmtilesFile: "surface_temp.pmtiles",
    sourceLayer: "surface_temp",
    kind: "circle",
    color: "#f472b6",
    circleRadiusBase: 5,
  },
  {
    id: "cedarRunGage",
    label: "Cedar Run Discharge Gage",
    group: "Hydrology",
    pmtilesFile: "cedar_run_gage.pmtiles",
    sourceLayer: "cedar_run_gage",
    kind: "circle",
    color: "#0284c7",
    circleRadiusBase: 8,
    circleStrokeColor: "#ffffff",
    circleStrokeWidth: 1.5,
  },
  {
    id: "gwWell",
    label: "Groundwater Depth Well",
    group: "Hydrology",
    pmtilesFile: "gw_well.pmtiles",
    sourceLayer: "gw_well",
    kind: "circle",
    color: "#0369a1",
    circleRadiusBase: 8,
    circleStrokeColor: "#ffffff",
    circleStrokeWidth: 1.5,
  },
  {
    id: "tidalFlowPaths",
    label: "Tidal Flow Paths",
    group: "Hydrology",
    pmtilesFile: "tidal_flow.pmtiles",
    sourceLayer: "tidal_flow",
    kind: "line",
    color: "#67e8f9",
    lineWidth: 1.2,
  },

  // ===== HAZARD & STORMWATER =====
  {
    id: "stormwaterSegments",
    label: "Stormwater Segments",
    group: "Hazard & Stormwater",
    pmtilesFile: "stormwater_seg.pmtiles",
    sourceLayer: "stormwater_seg",
    kind: "line",
    color: "#94a3b8",
    lineWidth: 1,
  },
  {
    id: "stormwaterStructures",
    label: "Stormwater Structures",
    group: "Hazard & Stormwater",
    pmtilesFile: "stormwater_struct.pmtiles",
    sourceLayer: "stormwater_struct",
    kind: "circle",
    color: "#cbd5e1",
    circleRadiusBase: 4,
  },
  {
    id: "damInundation",
    label: "Dam-Break Inundation Zones",
    group: "Hazard & Stormwater",
    pmtilesFile: "dam.pmtiles",
    sourceLayer: "dam",
    kind: "fill",
    outline: true,
    color: "#8b5e5e",
    fillOpacity: 0.24,
    lineWidth: 1,
  },
  {
    id: "soil",
    label: "Soil Construction Category",
    group: "Hazard & Stormwater",
    pmtilesFile: "soil.pmtiles",
    sourceLayer: "soil",
    kind: "fill",
    color: "#a8a29e",
    fillOpacity: 0.16,
  },

  // ===== DISCLOSURE (the headline finding) =====
  {
    id: "npdesPermits",
    label: "NPDES Permitted Facilities",
    group: "Disclosure",
    pmtilesFile: "npdes_facilities.pmtiles",
    sourceLayer: "npdes_facilities",
    kind: "circle",
    color: "#7dd3c0",
    circleRadiusBase: 8,
    circleStrokeColor: "#ffffff",
    circleStrokeWidth: 1.8,
  },
  {
    id: "dcBuildings",
    label: "Data Center Buildings",
    group: "Disclosure",
    pmtilesFile: "dc_buildings.pmtiles",
    sourceLayer: "dc_buildings",
    kind: "circle",
    color: "#8b5e5e",
    circleRadiusBase: 10,
    circleStrokeColor: "#ffffff",
    circleStrokeWidth: 2,
  },
  {
    id: "dcProjects",
    label: "Planned Data Center Campuses",
    group: "Disclosure",
    pmtilesFile: "dc_projects.pmtiles",
    sourceLayer: "dc_projects",
    kind: "fill",
    outline: true,
    color: "#e0b96a",
    fillOpacity: 0.2,
    lineWidth: 1.2,
  },

  // ===== MONITORING =====
  {
    id: "wqpStations",
    label: "WQP Monitoring Stations",
    group: "Monitoring",
    pmtilesFile: "wqp_stations.pmtiles",
    sourceLayer: "wqp_stations",
    kind: "circle",
    color: "#4fa3d1",
    circleRadiusBase: 6,
    circleStrokeColor: "#0f2942",
    circleStrokeWidth: 1,
  },
  {
    id: "deqMonitoring",
    label: "DEQ Monitoring Stations",
    group: "Monitoring",
    pmtilesFile: "deq_monitoring.pmtiles",
    sourceLayer: "deq_monitoring",
    kind: "circle",
    color: "#38bdf8",
    circleRadiusBase: 6,
    circleStrokeColor: "#0f2942",
    circleStrokeWidth: 1,
  },
  {
    id: "inatObservations",
    label: "iNaturalist Observations",
    group: "Monitoring",
    pmtilesFile: "inat_obs.pmtiles",
    sourceLayer: "inat_obs",
    kind: "circle",
    color: "#84cc16",
    circleRadiusBase: 3,
  },

  // ===== POWER & LAND =====
  {
    id: "transmissionLines",
    label: "Transmission Lines",
    group: "Power & Land",
    pmtilesFile: "transmission.pmtiles",
    sourceLayer: "transmission",
    kind: "line",
    color: "#e0b96a",
    lineWidth: 1.4,
  },
  {
    id: "zoning",
    label: "Zoning Districts",
    group: "Power & Land",
    pmtilesFile: "zoning.pmtiles",
    sourceLayer: "zoning",
    kind: "line",
    color: "#818cf8",
    lineWidth: 0.6,
  },
  {
    id: "usePermits",
    label: "Historical Use Permits",
    group: "Power & Land",
    pmtilesFile: "use_permits.pmtiles",
    sourceLayer: "use_permits",
    kind: "fill",
    outline: true,
    color: "#0d9488",
    fillOpacity: 0.12,
    lineWidth: 0.8,
  },
  {
    id: "bza",
    label: "BZA Variances",
    group: "Power & Land",
    pmtilesFile: "bza.pmtiles",
    sourceLayer: "bza",
    kind: "fill",
    color: "#f97316",
    fillOpacity: 0.2,
  },
  {
    id: "pendingCases",
    label: "Planning Pending Cases",
    group: "Power & Land",
    pmtilesFile: "pending.pmtiles",
    sourceLayer: "pending",
    kind: "fill",
    outline: true,
    color: "#60a5fa",
    fillOpacity: 0.18,
    lineWidth: 1,
  },
  {
    id: "lrlu",
    label: "LRLU Developable Areas",
    group: "Power & Land",
    pmtilesFile: "lrlu.pmtiles",
    sourceLayer: "lrlu",
    kind: "fill",
    outline: true,
    color: "#6366f1",
    fillOpacity: 0.14,
    lineWidth: 0.8,
  },
  {
    id: "protectedOpenSpace",
    label: "Protected Open Space",
    group: "Power & Land",
    pmtilesFile: "protected.pmtiles",
    sourceLayer: "protected",
    kind: "fill",
    color: "#059669",
    fillOpacity: 0.26,
  },
  {
    id: "stateLand",
    label: "State Land",
    group: "Power & Land",
    pmtilesFile: "state_land.pmtiles",
    sourceLayer: "state_land",
    kind: "fill",
    outline: true,
    color: "#b91c1c",
    fillOpacity: 0.16,
    lineWidth: 1,
  },
];
