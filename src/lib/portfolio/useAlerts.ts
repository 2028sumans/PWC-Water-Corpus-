"use client";

/**
 * Drives the in-app alerts feed by diffing against previous state.
 *
 * Two signals fire alerts:
 *   1. Saved-search match count changed since the previous evaluation.
 *   2. A portfolio parcel's Water Legibility Score moved by ≥3 points since
 *      the last sample.
 *
 * This hook is mounted ONCE at the app root (AppShell). All consumers read
 * the alert feed via useViraStore().alerts.
 */
import { useEffect, useRef } from "react";
import { useViraStore } from "@/store/useViraStore";
import { useScoredParcels } from "@/lib/useScoredParcels";
import { parcelReadinessAt } from "@/lib/parcelReadiness";
import { type ScoredParcel } from "@/lib/useScoredParcels";
import type { SavedSearch } from "@/store/useViraStore";

const SCORE_DELTA_THRESHOLD = 3;
const MATCH_COUNT_DELTA_THRESHOLD = 1;

interface SearchSnapshot {
  count: number;
  ts: number;
}

function matchesSavedSearch(p: ScoredParcel, s: SavedSearch, r: number): boolean {
  const f = s.filters;
  if (f.dcBuildingsOnly && p.in_dc_building !== 1) return false;
  if (f.inWatershedStress && (p.n_dc_in_watershed ?? 0) < 5) return false;
  if (f.nearStream && (p.d_stream_ft === null || p.d_stream_ft === undefined || p.d_stream_ft >= 300)) return false;
  if (f.noNpdesCoverage && p.has_npdes === 1) return false;
  if (f.hasMonitoringStation && (p.n_wqp_stations_1mi ?? 0) === 0 && (p.n_deq_monitoring_1mi ?? 0) === 0) return false;
  if (f.minWaterRisk > 0 && r < f.minWaterRisk) return false;
  if (s.searchQuery) {
    const q = s.searchQuery.toLowerCase();
    const hit =
      p.GPIN.toLowerCase().includes(q) ||
      (p.zoning ?? "").toLowerCase().includes(q) ||
      (p.StreetName ?? "").toLowerCase().includes(q) ||
      (p.City ?? "").toLowerCase().includes(q) ||
      (p.SubdivisionName ?? "").toLowerCase().includes(q) ||
      (p.lrlu ?? "").toLowerCase().includes(q) ||
      (p.watershed_name ?? "").toLowerCase().includes(q);
    if (!hit) return false;
  }
  return true;
}

export function usePortfolioAlerts() {
  const portfolios = useViraStore((s) => s.portfolios);
  const savedSearches = useViraStore((s) => s.savedSearches);
  const pushAlert = useViraStore((s) => s.pushAlert);
  const setSavedSearchMatchCount = useViraStore((s) => s.setSavedSearchMatchCount);
  const subScoreWeights = useViraStore((s) => s.subScoreWeights);

  const { parcels } = useScoredParcels();

  const prevPortfolioScoresRef = useRef<Map<string, number>>(new Map());
  const prevSearchCountsRef = useRef<Map<string, SearchSnapshot>>(new Map());

  // 1) PORTFOLIO PARCEL SCORE SHIFTS ─────────────────────────────────────────
  useEffect(() => {
    if (!parcels) return;
    const next = new Map<string, number>();
    const gpins = new Set<string>();
    for (const p of portfolios) {
      for (const g of p.gpins) gpins.add(g);
    }
    gpins.forEach((gpin) => {
      const parcel = parcels.find((x) => x.GPIN === gpin);
      if (!parcel) return;
      const r = parcelReadinessAt(parcel, subScoreWeights);
      if (r === null) return;
      next.set(gpin, r);
      const prev = prevPortfolioScoresRef.current.get(gpin);
      if (prev !== undefined && Math.abs(r - prev) >= SCORE_DELTA_THRESHOLD) {
        const owningPortfolio =
          portfolios.find((p) => p.gpins.includes(gpin))?.name ?? "portfolio";
        pushAlert({
          kind: r > prev ? "score_rise" : "score_drop",
          message: `${gpin} (in ${owningPortfolio}) ${r > prev ? "↑" : "↓"} ${Math.abs(r - prev)} → Water Legibility ${r}/100.`,
          meta: { gpin, prev, next: r },
        });
      }
    });
    prevPortfolioScoresRef.current = next;
  }, [parcels, portfolios, subScoreWeights, pushAlert]);

  // 2) SAVED-SEARCH MATCH-COUNT DIFFS ────────────────────────────────────────
  useEffect(() => {
    if (!parcels || savedSearches.length === 0) return;
    savedSearches.forEach((s) => {
      let count = 0;
      for (const p of parcels) {
        if (!p.GPIN || p.GPIN === "9999-99-9999") continue;
        const r = parcelReadinessAt(p, subScoreWeights) ?? p.readiness;
        if (matchesSavedSearch(p, s, r)) count += 1;
      }
      const snapshot = prevSearchCountsRef.current.get(s.id);
      const previous = snapshot?.count ?? s.lastMatchCount;
      if (previous !== undefined && Math.abs(count - previous) >= MATCH_COUNT_DELTA_THRESHOLD) {
        pushAlert({
          kind: "match_count_change",
          message: `"${s.name}" now matches ${count.toLocaleString()} parcel${count === 1 ? "" : "s"} (was ${previous.toLocaleString()}).`,
          meta: { savedSearchId: s.id, previous, current: count },
        });
      }
      prevSearchCountsRef.current.set(s.id, { count, ts: Date.now() });
      if (count !== s.lastMatchCount) {
        setSavedSearchMatchCount(s.id, count);
      }
    });
  }, [parcels, savedSearches, subScoreWeights, pushAlert, setSavedSearchMatchCount]);
}
