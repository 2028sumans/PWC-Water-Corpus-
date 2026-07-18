/**
 * Derive the 7-sub-score Water Legibility breakdown for a scored parcel from
 * the pre-computed spatial flags + countywide climate/utility constants.
 *
 * IMPORTANT: this synthesis pipeline is the CANONICAL Water Legibility
 * computation. Both the Decision Terminal table and the right panel run
 * their headline number through this same code path so they always agree.
 * The Python-side `parcel.readiness` from preprocessing is just a
 * sort-bootstrap hint — see useScoredParcels.ts.
 *
 * disclosureLegibility IS the observable / inferable / unresolved taxonomy,
 * quantified per parcel: NPDES + DEQ permit status is the one federal water
 * disclosure regime that exists, and it's what the tool's headline finding
 * (203 DC buildings, 0 NPDES permits) makes visible.
 */
import type { SubScoreKey } from "@/store/useViraStore";
import type { ScoredParcel } from "@/lib/useScoredParcels";

export type SubScoreRecord = Record<SubScoreKey, number>;
export type SubScoreQualityRecord = Record<SubScoreKey, "M" | "Md" | "I">;

function clip(n: number) {
  return Math.max(0, Math.min(100, Math.round(n)));
}

/**
 * Piecewise-linear interpolation. Takes a value x and a list of (x, y) anchor
 * points (sorted ascending by x), returns the linearly-interpolated y.
 */
function piecewiseLinear(x: number, points: ReadonlyArray<readonly [number, number]>): number {
  if (points.length === 0) return 0;
  if (x <= points[0][0]) return points[0][1];
  if (x >= points[points.length - 1][0]) return points[points.length - 1][1];
  for (let i = 0; i < points.length - 1; i++) {
    const [x1, y1] = points[i];
    const [x2, y2] = points[i + 1];
    if (x >= x1 && x <= x2) {
      const t = (x - x1) / (x2 - x1);
      return y1 + t * (y2 - y1);
    }
  }
  return points[points.length - 1][1];
}

// PHDI (and other Palmer indices) → 0-100 severity curve. -6 = extreme
// drought (severe), 0 = near-normal, +3 = wet.
const PALMER_SEVERITY: ReadonlyArray<readonly [number, number]> = [
  [-6, 95],
  [-3, 70],
  [0, 40],
  [3, 15],
];

// Stream-proximity risk curve for facilityWaterContext.
const STREAM_PROXIMITY_ADJ: ReadonlyArray<readonly [number, number]> = [
  [0, 40],
  [100, 30],
  [300, 15],
  [1000, 5],
  [5000, 0],
];

// Community-observation density curve — x = n_inat_1mi + monitoring*10.
const OBS_DENSITY: ReadonlyArray<readonly [number, number]> = [
  [0, 10],
  [5, 30],
  [20, 50],
  [50, 70],
  [100, 85],
  [200, 95],
];

export function synthesizeSubScores(p: ScoredParcel): {
  subScores: SubScoreRecord;
  quality: SubScoreQualityRecord;
} {
  const inDcBuilding = !!p.in_dc_building;

  // ---- 1. Watershed Vulnerability ----------------------------------------
  const phdi = p.phdi ?? null;
  let watershedVuln = phdi !== null ? piecewiseLinear(phdi, PALMER_SEVERITY) : 50;
  const nDcInWatershed = p.n_dc_in_watershed ?? 0;
  if (nDcInWatershed >= 10) watershedVuln += 15;
  else if (nDcInWatershed >= 5) watershedVuln += 8;
  else if (nDcInWatershed >= 1) watershedVuln += 3;
  const watershedAcres = p.watershed_acres ?? null;
  if (watershedAcres !== null) {
    if (watershedAcres >= 5000) watershedVuln -= 5;
    else if (watershedAcres < 500) watershedVuln += 8;
  }

  // ---- 2. Facility–Water Proximity ---------------------------------------
  let facilityWater = 30;
  const dStreamFt = p.d_stream_ft ?? null;
  if (dStreamFt !== null) facilityWater += piecewiseLinear(dStreamFt, STREAM_PROXIMITY_ADJ);
  if (p.rpa) facilityWater += 15;
  const dSpringFt = p.d_spring_ft ?? null;
  if (dSpringFt !== null) {
    if (dSpringFt < 1000) facilityWater += 10;
    else if (dSpringFt < 3000) facilityWater += 5;
  }
  const dHydroFt = p.d_hydro_ft ?? null;
  if (dHydroFt !== null && dHydroFt < 500) facilityWater += 8;
  if (inDcBuilding && dStreamFt !== null && dStreamFt < 300) facilityWater += 10;
  // Adjacent to protected open space / conservation land — ecological
  // buffer sensitivity (a hard-facing facility next to protected land
  // carries more downstream-ecology consequence than one surrounded by
  // other industrial parcels).
  if (p.near_protected_open_space) facilityWater += 6;
  // The county's own purpose flag distinguishes land protected specifically
  // FOR water quality from land protected for habitat/recreation — a purpose-
  // weighted upgrade over the generic proximity boolean above.
  if (p.near_h2oquality_protected_land) facilityWater += 4;
  // Stream order (Stream.StreamType) is a proxy for flow magnitude and
  // assimilative capacity: a facility near a low-order headwater stream
  // imposes far more relative stress than the same proximity to a high-order
  // river. Only credited when the facility is already close enough (<300ft)
  // that a discharge pathway is plausible.
  const streamOrder = p.stream_order ?? null;
  if (inDcBuilding && dStreamFt !== null && dStreamFt < 300 && streamOrder !== null && streamOrder > 0) {
    if (streamOrder <= 3) facilityWater += 6;
    else if (streamOrder >= 5) facilityWater -= 3;
  }
  // A parcel within the tidal-flow-path trigger AND resolved to a real VA
  // Water Quality Standards CLASS (only true for PWC's Potomac-adjacent
  // parcels — the layer is statewide) sits in a regulated receiving water
  // whose thermal/blowdown discharge capacity is legally bounded.
  if (p.in_tidal_flow_path && p.tidal_class) facilityWater += 8;

  // ---- 3. Drought Exposure (countywide) ----------------------------------
  const palmerValues = [p.pdsi, p.phdi, p.pmdi, p.palmer_z].filter(
    (v): v is number => v !== null && v !== undefined,
  );
  let droughtExposure =
    palmerValues.length > 0
      ? palmerValues.reduce((sum, v) => sum + piecewiseLinear(v, PALMER_SEVERITY), 0) / palmerValues.length
      : 50;
  const cdd = p.cdd ?? null;
  if (cdd !== null) {
    if (cdd > 2000) droughtExposure += 10;
    else if (cdd > 1500) droughtExposure += 5;
  }
  const precip = p.precip_in ?? null;
  const precipNormal = p.precip_normal_in ?? null;
  if (precip !== null && precipNormal !== null && precipNormal > 0) {
    const deficitPct = (precipNormal - precip) / precipNormal;
    if (deficitPct > 0.2) droughtExposure += 10;
    else if (deficitPct > 0.1) droughtExposure += 5;
  }
  // VA DEQ's own Mann-Kendall/Theil-Sen trend test on the nearest gauged
  // stream — a statistically-tested warming signal, not a raw reading.
  // Only credited when the trend is significant (p < 0.05) so a noisy,
  // insignificant slope doesn't move the score.
  if (p.surftemp_trend === "DEGRADING" && (p.surftemp_pvalcovs ?? 1) < 0.05) {
    droughtExposure += 8;
  }

  // ---- 4. Disclosure Legibility (higher = MORE legible) ------------------
  let disclosureLegibility = inDcBuilding ? 10 : 50;
  if (p.has_npdes) disclosureLegibility += inDcBuilding ? 40 : 20;
  if (p.has_deq_permit) disclosureLegibility += inDcBuilding ? 25 : 15;
  const nWqp = p.n_wqp_stations_1mi ?? 0;
  if (nWqp >= 3) disclosureLegibility += 10;
  else if (nWqp >= 1) disclosureLegibility += 5;
  if (p.utility_aggregate_available) disclosureLegibility += 5;

  // ---- 5. Community Observation Density ----------------------------------
  // A DEQ station flagged STA_LV4_CODE='GAGE' is an actual flow-measurement
  // point (rarer and more capable than a generic sampling station); a
  // nearby benthic-macroinvertebrate sample is a second, independent
  // literature-established bioindicator alongside the amphibian
  // (iNaturalist) signal — VA's own stream biomonitoring program is built
  // on benthic community health. Both weighted into the density input as
  // higher-value observation types, not just more observations.
  const obsX =
    (p.n_inat_1mi ?? 0) +
    nWqp * 10 +
    (p.n_deq_monitoring_1mi ?? 0) * 10 +
    (p.n_deq_gage_1mi ?? 0) * 15 +
    (p.nearest_benthic_n != null ? 10 : 0);
  const communityObsDensity = piecewiseLinear(obsX, OBS_DENSITY);

  // ---- 6. Municipal Supply Headroom (countywide) -------------------------
  const pwPeak = p.pw_water_pct_peak ?? null;
  let municipalSupplyHeadroom = pwPeak !== null ? 100 - pwPeak * 5 : 55;
  const nQueued = p.n_queued_projects_nearby ?? 0;
  if (nQueued > 20) municipalSupplyHeadroom -= 10;
  else if (nQueued > 10) municipalSupplyHeadroom -= 5;
  const pjmGrowth = p.pjm_zone_load_growth_pct ?? null;
  if (pjmGrowth !== null && pjmGrowth > 5) municipalSupplyHeadroom -= 5;

  // ---- 7. Stormwater Burden -----------------------------------------------
  let stormwaterBurden = 20;
  const nSw = p.sw_segments ?? 0;
  const nSwFac = p.sw_facilities ?? 0;
  const nSwStruct = p.sw_structures ?? 0;
  if (nSw >= 5) stormwaterBurden += 20;
  else if (nSw >= 2) stormwaterBurden += 8;
  if (nSwFac >= 1) stormwaterBurden += 25;
  if (nSwStruct >= 5) stormwaterBurden += 10;
  const haz = (p.dam_haz_class ?? "").toUpperCase();
  if (p.dam) {
    if (haz === "HIGH") stormwaterBurden += 20;
    else if (haz === "SIG" || haz === "SIGNIFICANT") stormwaterBurden += 10;
    else stormwaterBurden += 4;
  }
  const lc = (p.land_cover ?? "").toLowerCase();
  if (lc.includes("impervious") || lc.includes("pavement")) stormwaterBurden += 8;
  // Hydrologic Soil Group: D = poor infiltration, most runoff generated;
  // A = high infiltration, least runoff. Erosion susceptibility is a 0-1
  // NRCS soil-survey index — higher means more sediment/turbidity risk to
  // the receiving stream per unit of disturbed/impervious area.
  const hsg = (p.hsg ?? "").toUpperCase();
  if (hsg === "D") stormwaterBurden += 8;
  else if (hsg === "C") stormwaterBurden += 4;
  else if (hsg === "A") stormwaterBurden -= 4;
  const erosion = p.erosion_susceptibility ?? null;
  if (erosion !== null && erosion >= 0.4) stormwaterBurden += 5;

  const subScores: SubScoreRecord = {
    watershedVulnerability: clip(watershedVuln),
    facilityWaterContext: clip(facilityWater),
    droughtExposure: clip(droughtExposure),
    disclosureLegibility: clip(disclosureLegibility),
    communityObsDensity: clip(communityObsDensity),
    municipalSupplyHeadroom: clip(municipalSupplyHeadroom),
    stormwaterBurden: clip(stormwaterBurden),
  };

  // ---- Quality flags -------------------------------------------------------
  const watershedJoined = p.watershed_id != null;
  const streamAvail = dStreamFt !== null;
  const springAvail = dSpringFt !== null;
  const palmerLoaded = palmerValues.length > 0;
  const npdesFlagSet = p.has_npdes !== undefined;
  const deqFlagSet = p.has_deq_permit !== undefined;
  const wqpPresent = nWqp > 0;
  const inatOnly = !wqpPresent && (p.n_inat_1mi ?? 0) > 0;
  const stormwaterJoined = p.sw_segments !== undefined || p.sw_structures !== undefined || p.sw_facilities !== undefined;

  const quality: SubScoreQualityRecord = {
    watershedVulnerability: watershedJoined && phdi !== null ? "M" : phdi !== null ? "Md" : "I",
    facilityWaterContext: streamAvail && springAvail ? "M" : streamAvail ? "Md" : "I",
    droughtExposure: palmerLoaded ? "M" : "I",
    disclosureLegibility: npdesFlagSet && deqFlagSet ? "M" : npdesFlagSet ? "Md" : "I",
    communityObsDensity: wqpPresent ? "M" : inatOnly ? "I" : "I",
    municipalSupplyHeadroom: "M",
    stormwaterBurden: stormwaterJoined ? "M" : "I",
  };

  return { subScores, quality };
}
