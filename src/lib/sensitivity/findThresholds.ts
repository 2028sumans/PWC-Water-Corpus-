/**
 * Sensitivity analysis — "what would have to be true" for the binding
 * sub-scores to clear a target threshold. Surfaces the specific external
 * conditions (and by how much) that would need to change to improve a
 * parcel's Water Legibility Score, ranked by weighted contribution to the
 * composite gap.
 */
import type { ScoredParcel } from "@/lib/useScoredParcels";
import type { SubScoreKey } from "@/store/useViraStore";

export interface SensitivityThreshold {
  id: string;
  subScore: SubScoreKey;
  currentScore: number;
  targetScore: number;
  lever: string;
  currentValue: string;
  targetValue: string;
  byYear: number | null;
  rationale: string;
  source: string;
  pointsRecovered: number;
  plausibility: "high" | "medium" | "low";
}

interface SynthesizeOptions {
  targetScore?: number;
  maxThresholds?: number;
}

export function synthesizeThresholds(
  parcel: ScoredParcel,
  currentSubScores: Record<SubScoreKey, number>,
  weights: Record<SubScoreKey, number>,
  options: SynthesizeOptions = {},
): SensitivityThreshold[] {
  const targetScore = options.targetScore ?? 60;
  const maxThresholds = options.maxThresholds ?? 4;

  const ranked: Array<{ key: SubScoreKey; gap: number; weighted: number }> = [];
  for (const k of Object.keys(currentSubScores) as SubScoreKey[]) {
    const gap = targetScore - currentSubScores[k];
    if (gap <= 0) continue;
    const w = weights[k] ?? 0;
    ranked.push({ key: k, gap, weighted: gap * w });
  }
  ranked.sort((a, b) => b.weighted - a.weighted);

  const thresholds: SensitivityThreshold[] = [];
  for (const { key, gap } of ranked) {
    const t = buildThresholdFor(key, parcel, currentSubScores[key], targetScore, gap);
    if (t) thresholds.push(t);
    if (thresholds.length >= maxThresholds) break;
  }
  return thresholds.map((t, i) => ({ ...t, id: `S${i + 1}` }));
}

function buildThresholdFor(
  key: SubScoreKey,
  parcel: ScoredParcel,
  currentScore: number,
  targetScore: number,
  gap: number,
): SensitivityThreshold | null {
  switch (key) {
    case "watershedVulnerability":
    case "droughtExposure":
      return buildPhdiThreshold(key, currentScore, targetScore, gap, parcel);
    case "disclosureLegibility":
      return buildDisclosureThreshold(parcel, currentScore, targetScore, gap);
    case "communityObsDensity":
      return buildMonitoringThreshold(parcel, currentScore, targetScore, gap);
    case "municipalSupplyHeadroom":
      return buildSupplyThreshold(parcel, currentScore, targetScore, gap);
    default:
      // facilityWaterContext, stormwaterBurden — driven by fixed parcel
      // geometry (distance to stream, on-parcel infrastructure). No
      // realistic single-parcel lever beyond categorical hard-fact removal.
      return null;
  }
}

function buildPhdiThreshold(
  key: SubScoreKey,
  currentScore: number,
  targetScore: number,
  gap: number,
  parcel: ScoredParcel,
): SensitivityThreshold | null {
  const phdi = parcel.phdi ?? -5.3;
  const phdiNeeded = phdi + gap / 10;
  const phdiDelta = phdiNeeded - phdi;
  const yearsToRecover = Math.max(2, Math.ceil(phdiDelta * 3));
  const byYear = new Date().getFullYear() + yearsToRecover;
  const plausibility: SensitivityThreshold["plausibility"] =
    phdiDelta < 1.5 ? "high" : phdiDelta < 3.5 ? "medium" : "low";
  return {
    id: "",
    subScore: key,
    currentScore,
    targetScore,
    lever: "PHDI countywide drought index",
    currentValue: phdi.toFixed(2),
    targetValue: phdiNeeded.toFixed(2),
    byYear,
    rationale: `For ${key} to recover from ${currentScore} to ≥${targetScore}, the countywide PHDI (currently ${phdi.toFixed(2)}) would need to climb to ${phdiNeeded.toFixed(2)} by ${byYear} — roughly ${yearsToRecover} years of normal-to-wet precipitation.`,
    source: "PHDI.json (monthly 1895–present)",
    pointsRecovered: gap,
    plausibility,
  };
}

function buildDisclosureThreshold(
  parcel: ScoredParcel,
  currentScore: number,
  targetScore: number,
  gap: number,
): SensitivityThreshold | null {
  if (parcel.has_npdes) return null; // already the max-legibility state
  const gain = parcel.in_dc_building ? 40 : 20;
  return {
    id: "",
    subScore: "disclosureLegibility",
    currentScore,
    targetScore,
    lever: "NPDES water discharge permit filing",
    currentValue: "no NPDES permit on record",
    targetValue: "NPDES permit filed",
    byYear: null,
    rationale: `Disclosure Legibility gains +${gain} points if this parcel's operator files for an NPDES water discharge permit — currently only 4 facilities in all of Virginia hold one. This is the single largest legibility lever and the one almost no data center exercises.`,
    source: "EPA ICIS-NPDES facility registry",
    pointsRecovered: Math.min(gap, gain),
    plausibility: "low",
  };
}

function buildMonitoringThreshold(
  parcel: ScoredParcel,
  currentScore: number,
  targetScore: number,
  gap: number,
): SensitivityThreshold | null {
  const nWqp = parcel.n_wqp_stations_1mi ?? 0;
  if (nWqp >= 3) return null;
  const targetN = Math.min(3, nWqp + Math.ceil(gap / 15));
  return {
    id: "",
    subScore: "communityObsDensity",
    currentScore,
    targetScore,
    lever: "Water Quality Portal monitoring stations within 1 mi",
    currentValue: `${nWqp} station${nWqp === 1 ? "" : "s"}`,
    targetValue: `${targetN} stations`,
    byYear: new Date().getFullYear() + 3,
    rationale: `Community Observation Density would clear ${targetScore} if ${targetN - nWqp} additional WQP or DEQ monitoring station(s) were sited within 1 mile — a plausible outcome of a citizen-science or utility monitoring expansion.`,
    source: "Water Quality Portal station registry",
    pointsRecovered: gap,
    plausibility: targetN - nWqp <= 1 ? "high" : "medium",
  };
}

function buildSupplyThreshold(
  parcel: ScoredParcel,
  currentScore: number,
  targetScore: number,
  gap: number,
): SensitivityThreshold | null {
  const peak = parcel.pw_water_pct_peak ?? 10.1;
  const peakNeeded = Math.max(0, peak - gap / 5);
  return {
    id: "",
    subScore: "municipalSupplyHeadroom",
    currentScore,
    targetScore,
    lever: "Data center share of PW Water peak demand",
    currentValue: `${peak.toFixed(1)}%`,
    targetValue: `${peakNeeded.toFixed(1)}%`,
    byYear: new Date().getFullYear() + 4,
    rationale: `Municipal Supply Headroom would recover ${gap} points if data centers' share of Prince William Water's peak system demand fell from ${peak.toFixed(1)}% to ${peakNeeded.toFixed(1)}% — via either reduced consumption or expanded supply capacity.`,
    source: "Prince William Water FAQ disclosure",
    pointsRecovered: gap,
    plausibility: peak - peakNeeded < 2 ? "medium" : "low",
  };
}
