"use client";

/**
 * Bidirectional sync between the Zustand store and the URL hash, so
 * refreshing preserves the analyst's session (view, selected parcel, pinned
 * parcel, filter set, sub-score weights) AND so links are shareable.
 *
 * Format: `#view=map&gpin=7596-81-5396&pin=7695-77-7535&q=manassas&w_wshed=0.3`
 * Default-valued keys are omitted to keep links short.
 */
import { useEffect, useRef } from "react";
import { useViraStore, type SubScoreKey, type ViewMode, type Preset } from "@/store/useViraStore";

const VIEW_VALUES = new Set(["terminal", "map"]);
const PRESET_VALUES = new Set(["none", "hardBlockers", "powerReady", "politicallyWarm"]);

const DEFAULT_WEIGHTS: Record<SubScoreKey, number> = {
  watershedVulnerability: 0.20,
  facilityWaterContext: 0.20,
  droughtExposure: 0.15,
  disclosureLegibility: 0.15,
  communityObsDensity: 0.10,
  municipalSupplyHeadroom: 0.10,
  stormwaterBurden: 0.10,
};

const WEIGHT_KEY_TO_SLUG: Record<SubScoreKey, string> = {
  watershedVulnerability: "w_wshed",
  facilityWaterContext: "w_fac",
  droughtExposure: "w_drought",
  disclosureLegibility: "w_disc",
  communityObsDensity: "w_obs",
  municipalSupplyHeadroom: "w_supply",
  stormwaterBurden: "w_sw",
};
const SLUG_TO_WEIGHT_KEY: Record<string, SubScoreKey> = Object.fromEntries(
  Object.entries(WEIGHT_KEY_TO_SLUG).map(([k, v]) => [v, k as SubScoreKey]),
) as Record<string, SubScoreKey>;

function parseHash(): URLSearchParams {
  const raw = typeof window === "undefined" ? "" : window.location.hash.replace(/^#/, "");
  return new URLSearchParams(raw);
}

function applyHashToStore(p: URLSearchParams) {
  const s = useViraStore.getState();
  const view = p.get("view");
  if (view && VIEW_VALUES.has(view)) s.setView(view as ViewMode);
  const gpin = p.get("gpin");
  if (gpin) s.setSelectedParcel(gpin);
  const pin = p.get("pin");
  if (pin) s.setPinnedParcel(pin);
  const q = p.get("q");
  if (q !== null) s.setSearchQuery(q);
  const preset = p.get("preset");
  if (preset && PRESET_VALUES.has(preset)) s.setPreset(preset as Preset);
  for (const [slug, k] of Object.entries(SLUG_TO_WEIGHT_KEY)) {
    const v = p.get(slug);
    if (v !== null) {
      const n = Number(v);
      if (Number.isFinite(n) && n >= 0 && n <= 1) s.setSubScoreWeight(k, n);
    }
  }
}

function buildHashFromStore(): string {
  const s = useViraStore.getState();
  const p = new URLSearchParams();
  if (s.view !== "terminal") p.set("view", s.view);
  if (s.selectedParcelId) p.set("gpin", s.selectedParcelId);
  if (s.pinnedParcelId) p.set("pin", s.pinnedParcelId);
  if (s.searchQuery) p.set("q", s.searchQuery);
  if (s.preset !== "none") p.set("preset", s.preset);
  for (const [k, slug] of Object.entries(WEIGHT_KEY_TO_SLUG) as Array<[SubScoreKey, string]>) {
    const v = s.subScoreWeights[k];
    if (Math.abs(v - DEFAULT_WEIGHTS[k]) > 0.005) {
      p.set(slug, v.toFixed(2));
    }
  }
  const s2 = p.toString();
  return s2 ? `#${s2}` : "";
}

export function useUrlStateSync(): void {
  const hydratedRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    applyHashToStore(parseHash());
    hydratedRef.current = true;
    const onHashChange = () => applyHashToStore(parseHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    let pending: number | null = null;
    const flush = () => {
      if (!hydratedRef.current) return;
      const next = buildHashFromStore();
      const current = window.location.hash || "";
      if (next !== current) {
        window.history.replaceState(null, "", next || window.location.pathname + window.location.search);
      }
    };
    const unsubscribe = useViraStore.subscribe(() => {
      if (pending !== null) window.clearTimeout(pending);
      pending = window.setTimeout(flush, 200);
    });
    return () => {
      if (pending !== null) window.clearTimeout(pending);
      unsubscribe();
    };
  }, []);
}
