import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";

export type ViewMode = "terminal" | "map";

export type SubScoreKey =
  | "watershedVulnerability"
  | "facilityWaterContext"
  | "droughtExposure"
  | "disclosureLegibility"
  | "communityObsDensity"
  | "municipalSupplyHeadroom"
  | "stormwaterBurden";

export type DataQuality = "M" | "Md" | "I"; // Measured | Modeled | Inferred

export type Preset = "none" | "hardBlockers" | "powerReady" | "politicallyWarm";

/**
 * Quick-filter state lifted out of DecisionTerminal so it can be (a) snapshotted
 * by saved searches and (b) restored when a saved search runs. The shape is
 * the same as the local QuickFilters interface the terminal used to maintain.
 */
export interface QuickFilters {
  dcBuildingsOnly: boolean;
  inWatershedStress: boolean;
  nearStream: boolean;
  noNpdesCoverage: boolean;
  hasMonitoringStation: boolean;
  minWaterRisk: number;          // 0 disables the filter
}

export const DEFAULT_QUICK_FILTERS: QuickFilters = {
  dcBuildingsOnly: false,
  inWatershedStress: false,
  nearStream: false,
  noNpdesCoverage: false,
  hasMonitoringStation: false,
  minWaterRisk: 0,
};

export interface Portfolio {
  id: string;
  name: string;
  gpins: string[];
  createdAt: number;
}

export interface SavedSearch {
  id: string;
  name: string;
  searchQuery: string;
  filters: QuickFilters;
  /** Last observed match count — used to diff for alerts. */
  lastMatchCount?: number;
  createdAt: number;
}

export type AlertKind =
  | "score_drop"
  | "score_rise"
  | "match_count_change";

export interface AlertEntry {
  id: string;
  ts: number;
  kind: AlertKind;
  message: string;
  read: boolean;
  meta?: Record<string, unknown>;
}

interface ViraState {
  // View
  view: ViewMode;
  setView: (v: ViewMode) => void;

  // Selection
  selectedParcelId: string | null;
  setSelectedParcel: (gpin: string | null) => void;

  // Pinned parcel for compare view. When this is set AND selectedParcelId
  // points at a different parcel, the right panel renders a two-column
  // comparison view. Clicking the pin button on the panel header toggles
  // the current parcel into this slot.
  pinnedParcelId: string | null;
  setPinnedParcel: (gpin: string | null) => void;

  // Filters + search
  searchQuery: string;
  setSearchQuery: (q: string) => void;

  // Quick filters (lifted from DecisionTerminal so saved searches can capture them).
  quickFilters: QuickFilters;
  setQuickFilter: <K extends keyof QuickFilters>(k: K, v: QuickFilters[K]) => void;
  resetQuickFilters: () => void;

  // Layer toggles (map view)
  activeLayers: Record<string, boolean>;
  toggleLayer: (id: string) => void;
  setLayers: (m: Record<string, boolean>) => void;

  // Smart preset
  preset: Preset;
  setPreset: (p: Preset) => void;

  // Right panel
  rightPanelOpen: boolean;
  openRightPanel: () => void;
  closeRightPanel: () => void;

  // Sub-score weights (user reweighting in onboarding tier 2)
  subScoreWeights: Record<SubScoreKey, number>;
  setSubScoreWeight: (k: SubScoreKey, w: number) => void;
  resetWeights: () => void;

  // Portfolio mode ─────────────────────────────────────────────────────────
  portfolios: Portfolio[];
  activePortfolioId: string | null;
  createPortfolio: (name: string) => string;     // returns new id
  deletePortfolio: (id: string) => void;
  renamePortfolio: (id: string, name: string) => void;
  setActivePortfolio: (id: string | null) => void;
  addToPortfolio: (portfolioId: string, gpin: string) => void;
  removeFromPortfolio: (portfolioId: string, gpin: string) => void;
  /** Convenience: add to the active portfolio, creating a default one if none. */
  addToActivePortfolio: (gpin: string) => void;

  // Saved searches ─────────────────────────────────────────────────────────
  savedSearches: SavedSearch[];
  saveCurrentSearch: (name: string) => string;
  deleteSavedSearch: (id: string) => void;
  applySavedSearch: (id: string) => void;
  setSavedSearchMatchCount: (id: string, count: number) => void;

  // Alerts ──────────────────────────────────────────────────────────────────
  // Ephemeral by design — not persisted across reloads. The persistent log
  // would need server-side storage; in-app + session-only matches the user's
  // "in-app only" choice for alert delivery.
  alerts: AlertEntry[];
  pushAlert: (a: Omit<AlertEntry, "id" | "ts" | "read">) => void;
  markAlertRead: (id: string) => void;
  markAllAlertsRead: () => void;
  clearAlerts: () => void;
}

const DEFAULT_WEIGHTS: Record<SubScoreKey, number> = {
  watershedVulnerability: 0.20,
  facilityWaterContext: 0.20,
  droughtExposure: 0.15,
  disclosureLegibility: 0.15,
  communityObsDensity: 0.10,
  municipalSupplyHeadroom: 0.10,
  stormwaterBurden: 0.10,
};

const DEFAULT_LAYERS: Record<string, boolean> = {
  parcels: true,
  dcBuildings: true,
  dcProjects: true,
  watersheds: true,
  streams: false,
  rpa: false,
  hydrologyFeatures: false,
  stormwaterStructures: false,
  stormwaterSegments: false,
  damInundation: false,
  soil: false,
  groundwaterSprings: false,
  surfaceWaterTemp: false,
  wqpStations: true,
  deqMonitoring: false,
  inatObservations: false,
  npdesPermits: true,
  protectedOpenSpace: false,
  zoning: false,
  cedarRunGage: false,
  gwWell: false,
  tidalFlowPaths: false,
  echoFacilities: true,
  transmissionLines: false,
  usePermits: false,
  bza: false,
  pendingCases: false,
  lrlu: false,
  stateLand: false,
};

function newId(): string {
  // Short, sortable enough, no extra dependency. Format: ts-base36 + 4 random chars.
  return `${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 6)}`;
}

const MAX_ALERTS = 50;

export const useViraStore = create<ViraState>()(
  persist(
    (set, get) => ({
      view: "terminal",
      setView: (v) => set({ view: v }),

      selectedParcelId: null,
      setSelectedParcel: (gpin) =>
        set({ selectedParcelId: gpin, rightPanelOpen: gpin !== null }),

      pinnedParcelId: null,
      setPinnedParcel: (gpin) => set({ pinnedParcelId: gpin }),

      searchQuery: "",
      setSearchQuery: (q) => set({ searchQuery: q }),

      quickFilters: DEFAULT_QUICK_FILTERS,
      setQuickFilter: (k, v) =>
        set((state) => ({ quickFilters: { ...state.quickFilters, [k]: v } })),
      resetQuickFilters: () => set({ quickFilters: DEFAULT_QUICK_FILTERS }),

      activeLayers: DEFAULT_LAYERS,
      toggleLayer: (id) =>
        set((state) => ({
          activeLayers: { ...state.activeLayers, [id]: !state.activeLayers[id] },
        })),
      setLayers: (m) => set({ activeLayers: m }),

      preset: "none",
      setPreset: (p) => set({ preset: p }),

      rightPanelOpen: false,
      openRightPanel: () => set({ rightPanelOpen: true }),
      closeRightPanel: () => set({ rightPanelOpen: false }),

      subScoreWeights: DEFAULT_WEIGHTS,
      setSubScoreWeight: (k, w) =>
        set((state) => ({
          subScoreWeights: { ...state.subScoreWeights, [k]: w },
        })),
      resetWeights: () => set({ subScoreWeights: DEFAULT_WEIGHTS }),

      // Portfolio actions ──────────────────────────────────────────────────
      portfolios: [],
      activePortfolioId: null,
      createPortfolio: (name) => {
        const id = newId();
        set((state) => ({
          portfolios: [
            ...state.portfolios,
            { id, name: name.trim() || "Untitled portfolio", gpins: [], createdAt: Date.now() },
          ],
          activePortfolioId: id,
        }));
        return id;
      },
      deletePortfolio: (id) =>
        set((state) => ({
          portfolios: state.portfolios.filter((p) => p.id !== id),
          activePortfolioId:
            state.activePortfolioId === id ? null : state.activePortfolioId,
        })),
      renamePortfolio: (id, name) =>
        set((state) => ({
          portfolios: state.portfolios.map((p) =>
            p.id === id ? { ...p, name: name.trim() || p.name } : p,
          ),
        })),
      setActivePortfolio: (id) => set({ activePortfolioId: id }),
      addToPortfolio: (portfolioId, gpin) =>
        set((state) => ({
          portfolios: state.portfolios.map((p) =>
            p.id === portfolioId && !p.gpins.includes(gpin)
              ? { ...p, gpins: [...p.gpins, gpin] }
              : p,
          ),
        })),
      removeFromPortfolio: (portfolioId, gpin) =>
        set((state) => ({
          portfolios: state.portfolios.map((p) =>
            p.id === portfolioId
              ? { ...p, gpins: p.gpins.filter((g) => g !== gpin) }
              : p,
          ),
        })),
      addToActivePortfolio: (gpin) => {
        const state = get();
        let id = state.activePortfolioId;
        if (!id) {
          id = state.createPortfolio("My pipeline");
        }
        state.addToPortfolio(id, gpin);
      },

      // Saved searches ─────────────────────────────────────────────────────
      savedSearches: [],
      saveCurrentSearch: (name) => {
        const { searchQuery, quickFilters } = get();
        const id = newId();
        set((state) => ({
          savedSearches: [
            ...state.savedSearches,
            {
              id,
              name: name.trim() || "Untitled search",
              searchQuery,
              filters: { ...quickFilters },
              createdAt: Date.now(),
            },
          ],
        }));
        return id;
      },
      deleteSavedSearch: (id) =>
        set((state) => ({
          savedSearches: state.savedSearches.filter((s) => s.id !== id),
        })),
      applySavedSearch: (id) => {
        const search = get().savedSearches.find((s) => s.id === id);
        if (!search) return;
        set({
          searchQuery: search.searchQuery,
          quickFilters: { ...search.filters },
          view: "terminal",
        });
      },
      setSavedSearchMatchCount: (id, count) =>
        set((state) => ({
          savedSearches: state.savedSearches.map((s) =>
            s.id === id ? { ...s, lastMatchCount: count } : s,
          ),
        })),

      // Alerts ─────────────────────────────────────────────────────────────
      alerts: [],
      pushAlert: (a) =>
        set((state) => ({
          alerts: [
            { ...a, id: newId(), ts: Date.now(), read: false },
            ...state.alerts,
          ].slice(0, MAX_ALERTS),
        })),
      markAlertRead: (id) =>
        set((state) => ({
          alerts: state.alerts.map((a) => (a.id === id ? { ...a, read: true } : a)),
        })),
      markAllAlertsRead: () =>
        set((state) => ({
          alerts: state.alerts.map((a) => ({ ...a, read: true })),
        })),
      clearAlerts: () => set({ alerts: [] }),
    }),
    {
      name: "water-atlas-state",
      storage: createJSONStorage(() => localStorage),
      // Only persist a subset; selection/panel are session-only.
      // Portfolios + savedSearches PERSIST — they're the heart of the v2
      // portfolio mode. Alerts do NOT persist (ephemeral session log).
      partialize: (state) => ({
        view: state.view,
        searchQuery: state.searchQuery,
        quickFilters: state.quickFilters,
        activeLayers: state.activeLayers,
        preset: state.preset,
        subScoreWeights: state.subScoreWeights,
        portfolios: state.portfolios,
        activePortfolioId: state.activePortfolioId,
        savedSearches: state.savedSearches,
      }),
    }
  )
);

export const SUBSCORE_LABELS: Record<SubScoreKey, string> = {
  watershedVulnerability: "Watershed Vulnerability",
  facilityWaterContext: "Facility–Water Proximity",
  droughtExposure: "Drought Exposure",
  disclosureLegibility: "Disclosure Legibility",
  communityObsDensity: "Community Obs. Density",
  municipalSupplyHeadroom: "Municipal Supply Headroom",
  stormwaterBurden: "Stormwater Burden",
};
