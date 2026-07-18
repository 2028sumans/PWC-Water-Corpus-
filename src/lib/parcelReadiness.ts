/**
 * Single source of truth for the headline Water Legibility Score of a parcel.
 *
 * Pipeline (used by BOTH the Decision Terminal table and the right panel):
 *   1. Look up the cached synthesized 7 sub-scores by GPIN — computed once
 *      when parcels load, see useScoredParcels.ts.
 *   2. Weighted-sum the sub-scores using the user-tunable subScoreWeights.
 *      Output is 0..100, clipped. No composite-level caps (unlike Vira's
 *      Option B) — the water tool doesn't need siting-specific caps.
 *
 * Returns null only if the GPIN isn't in the synth cache (shouldn't happen
 * after the initial load completes).
 */
import type { SubScoreKey } from "@/store/useViraStore";
import { getCachedSynth, type ScoredParcel } from "@/lib/useScoredParcels";

/**
 * Weighted composite Water Legibility Score from sub-scores and weights.
 * Weights are normalized; user can reweight via the onboarding tier-2.
 */
export function computeReadiness(
  subScores: Record<SubScoreKey, number>,
  weights: Record<SubScoreKey, number>,
): number {
  let weighted = 0;
  let totalWeight = 0;
  for (const k of Object.keys(subScores) as SubScoreKey[]) {
    const w = weights[k] || 0;
    weighted += subScores[k] * w;
    totalWeight += w;
  }
  if (totalWeight === 0) return 0;
  return Math.round(weighted / totalWeight);
}

/**
 * Compute the headline Water Legibility Score for a parcel at the given
 * weights. Cheap — ~10 ops per call. Safe to use in a virtualizer hot path.
 */
export function parcelReadinessAt(
  parcel: ScoredParcel | { GPIN: string },
  weights: Record<SubScoreKey, number>,
): number | null {
  const synth = getCachedSynth(parcel.GPIN);
  if (!synth) return null;
  const composite = computeReadiness(synth.subScores, weights);
  return Math.max(0, Math.min(100, Math.round(composite)));
}
