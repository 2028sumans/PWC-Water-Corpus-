/**
 * Source-citation registry. Maps every data source that contributes to the
 * Water Legibility Score to a working URL + human-readable title + category.
 *
 * Used by topSourcesForParcel() to render the dynamic "Source documentation"
 * block in the right panel — only the citations that actually drove THIS
 * parcel's score are shown.
 */

export type SourceCategory =
  | "spatial-hydrology"    // Watersheds, streams, springs, hydrology
  | "spatial-hazard"       // Dam-break, stormwater
  | "regulatory"           // NPDES, DEQ, EPA ECHO
  | "monitoring"           // WQP, DEQ monitoring, iNaturalist
  | "climate"              // Palmer indices, NOAA temp/precip
  | "utility"              // Prince William Water
  | "policy";              // Policy PDFs / JSONs

export interface SourceCitation {
  key: string;
  title: string;
  href: string;
  external?: boolean;
  category: SourceCategory;
  description?: string;
}

export const SOURCES: Record<string, SourceCitation> = {
  // ===== HYDROLOGY =====
  "spatial:watersheds": {
    key: "spatial:watersheds",
    title: "PWC Watersheds (222 sub-areas)",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/maps/75f20bd568ad4828838705cae3b98b45",
    external: true,
    category: "spatial-hydrology",
  },
  "spatial:stream": {
    key: "spatial:stream",
    title: "PWC Streams",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/maps/edee2bb6022b406f85c5e27629d708a6",
    external: true,
    category: "spatial-hydrology",
    description: "100-ft buffer triggers the RPA setback requirement.",
  },
  "spatial:hydro": {
    key: "spatial:hydro",
    title: "Hydrological Features (PWC GIS)",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/datasets/7d0098c603bc407699f358a19e078571_5/explore",
    external: true,
    category: "spatial-hydrology",
  },
  "spatial:springs": {
    key: "spatial:springs",
    title: "Springs / Groundwater Layers",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/",
    external: true,
    category: "spatial-hydrology",
  },
  "spatial:rpa": {
    key: "spatial:rpa",
    title: "Resource Protection Areas (RPA)",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/maps/962b024b26854020a9879001c08e9d1b",
    external: true,
    category: "spatial-hydrology",
    description: "Chesapeake Bay Preservation Act buffer.",
  },
  "spatial:surface-temp": {
    key: "spatial:surface-temp",
    title: "Surface Water Temperature Monitoring",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/",
    external: true,
    category: "spatial-hydrology",
  },
  "usgs:cedar-run": {
    key: "usgs:cedar-run",
    title: "USGS Cedar Run Near Catlett, VA — discharge/gage",
    href: "https://waterdata.usgs.gov/monitoring-location/01659500",
    external: true,
    category: "spatial-hydrology",
  },
  "usgs:gw-well": {
    key: "usgs:gw-well",
    title: "USGS Groundwater Depth Well VA087-383951077415001",
    href: "https://waterdata.usgs.gov/nwis/gw",
    external: true,
    category: "spatial-hydrology",
  },

  // ===== HAZARD =====
  "spatial:dam": {
    key: "spatial:dam",
    title: "Dam Break Inundation Zones",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/datasets/d34e5ee1ca0d4783b065924595b628b9_7/explore",
    external: true,
    category: "spatial-hazard",
    description: "VA-DCR-regulated dam inundation polygons with HAZ_CLASS.",
  },
  "spatial:stormwater-seg": {
    key: "spatial:stormwater-seg",
    title: "PWC Stormwater Segments",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/maps/3ddee1e0e90c4b39b80b76a75224bc64",
    external: true,
    category: "spatial-hazard",
  },
  "spatial:stormwater-struct": {
    key: "spatial:stormwater-struct",
    title: "PWC Stormwater Management Structures",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/",
    external: true,
    category: "spatial-hazard",
  },

  // ===== REGULATORY / DISCLOSURE =====
  "epa:icis-npdes": {
    key: "epa:icis-npdes",
    title: "EPA ICIS-NPDES Facility Registry",
    href: "https://echo.epa.gov/tools/data-downloads/icis-npdes-download-summary",
    external: true,
    category: "regulatory",
    description: "The federal water-discharge permit registry — the source of the '0 of 203 data centers hold NPDES permits' finding.",
  },
  "epa:echo-exporter": {
    key: "epa:echo-exporter",
    title: "EPA ECHO Exporter (compliance history)",
    href: "https://echo.epa.gov/tools/data-downloads",
    external: true,
    category: "regulatory",
  },
  "epa:npdes-dmr": {
    key: "epa:npdes-dmr",
    title: "EPA NPDES Discharge Monitoring Reports (DMR)",
    href: "https://echo.epa.gov/tools/data-downloads/dmr-data-downloads",
    external: true,
    category: "regulatory",
    description: "NODI=C (no discharge indicated) is the DMR code driving the headline finding.",
  },
  "epa:frs": {
    key: "epa:frs",
    title: "EPA Facility Registry Service (FRS)",
    href: "https://www.epa.gov/frs",
    external: true,
    category: "regulatory",
    description: "Cross-program linkage key (NPDES / RCRA / CAA facility IDs).",
  },
  "va-deq:permits": {
    key: "va-deq:permits",
    title: "Virginia DEQ Water Permits",
    href: "https://www.deq.virginia.gov/permits-regulations",
    external: true,
    category: "regulatory",
  },

  // ===== MONITORING =====
  "wqp:stations": {
    key: "wqp:stations",
    title: "Water Quality Portal — PWC monitoring stations",
    href: "https://www.waterqualitydata.us/",
    external: true,
    category: "monitoring",
  },
  "pwc:deq-monitoring": {
    key: "pwc:deq-monitoring",
    title: "Water Quality Monitoring Plan Stations (PWC, current)",
    href: "https://gisdata-pwcgov.opendata.arcgis.com/",
    external: true,
    category: "monitoring",
  },
  "inat:observations": {
    key: "inat:observations",
    title: "iNaturalist community observations",
    href: "https://www.inaturalist.org/",
    external: true,
    category: "monitoring",
  },

  // ===== CLIMATE =====
  "noaa:palmer": {
    key: "noaa:palmer",
    title: "NOAA Palmer Drought Indices (PDSI/PHDI/PMDI/Z-Index)",
    href: "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/county/time-series/VA-153/pdsi/1/0/1895-2026",
    external: true,
    category: "climate",
  },
  "noaa:climate-normals": {
    key: "noaa:climate-normals",
    title: "NOAA Climate Normals (temp, precip, degree days)",
    href: "https://www.ncei.noaa.gov/products/land-based-station/us-climate-normals",
    external: true,
    category: "climate",
  },

  // ===== UTILITY =====
  "pw-water:faq": {
    key: "pw-water:faq",
    title: "Prince William Water — Data Center Water Use FAQ",
    href: "https://www.pwcsa.org/",
    external: true,
    category: "utility",
    description: "Discloses data-center share of peak/average system demand.",
  },
  "pjm:load-report": {
    key: "pjm:load-report",
    title: "PJM Load Report (Dominion zone)",
    href: "https://www.pjm.com/library/reports-notices/load-forecast-report",
    external: true,
    category: "utility",
  },

  // ===== POLICY =====
  "policy:jlarc-598": {
    key: "policy:jlarc-598",
    title: "JLARC Report 598 — Data Centers in Virginia",
    href: "/data/policy/Rpt598.json",
    category: "policy",
  },
  "policy:icprb-dec2025": {
    key: "policy:icprb-dec2025",
    title: "ICPRB 2025 WMA Water Supply Study",
    href: "/data/policy/2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.json",
    category: "policy",
  },
  "policy:icprb-mar2026": {
    key: "policy:icprb-mar2026",
    title: "ICPRB — Data Centers and Water Use (Mar 2026)",
    href: "/data/policy/ICPRB.DataCentersandWaterUse.ICPRB_.March2026.json",
    category: "policy",
  },
  "policy:dominion-gs5": {
    key: "policy:dominion-gs5",
    title: "Dominion GS-5 Large Load Rate Class",
    href: "/data/policy/Dominion_GS-5_LargeLoad_RateClass.json",
    category: "policy",
  },
  "policy:lbnl-queued": {
    key: "policy:lbnl-queued",
    title: "LBNL Queued Up 2025 (interconnection queue report)",
    href: "/data/policy/LBNL_QueuedUp_2025.json",
    category: "policy",
  },
  "policy:cesmp": {
    key: "policy:cesmp",
    title: "PWC Community Energy & Sustainability Master Plan",
    href: "/data/policy/prince_william_cesmp_full.json",
    category: "policy",
  },
  "policy:res-20-773": {
    key: "policy:res-20-773",
    title: "PWC Res. 20-773 — Climate Mitigation Goals",
    href: "/data/policy/Res No 20-773 Climate Mitigation and Resiliency Goals.json",
    category: "policy",
  },
};
