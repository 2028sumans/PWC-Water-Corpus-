"use client";

import { useEffect, useMemo, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { useScoredParcels } from "@/lib/useScoredParcels";
import { usePolicyIndex } from "@/lib/usePolicyIndex";
import { useUrlStateSync } from "@/lib/useUrlStateSync";
import { parcelReadinessAt } from "@/lib/parcelReadiness";
import { usePortfolioAlerts } from "@/lib/portfolio/useAlerts";
import { AlertsFeed } from "./AlertsFeed";
import { ViewToggle } from "./ViewToggle";
import { DecisionTerminal } from "./DecisionTerminal";
import { SpatialMap } from "./SpatialMap";
import { RightPanel } from "./RightPanel";

export function AppShell() {
  const view = useViraStore((s) => s.view);
  const setView = useViraStore((s) => s.setView);
  const rightPanelOpen = useViraStore((s) => s.rightPanelOpen);
  const closeRightPanel = useViraStore((s) => s.closeRightPanel);
  const setSelectedParcel = useViraStore((s) => s.setSelectedParcel);
  const subScoreWeights = useViraStore((s) => s.subScoreWeights);

  // Preload the scored parcels at app start so map clicks resolve immediately
  // regardless of whether the user visited the Terminal first.
  const { parcels: allParcels } = useScoredParcels();
  // Mount the centralized alerts hook at the root.
  usePortfolioAlerts();
  // Bidirectional URL ↔ store sync so refreshes preserve the session.
  useUrlStateSync();
  // Preload policy-corpus index so the right panel can show citation counts.
  usePolicyIndex();
  // Warm the PMTiles route handler's in-memory buffer cache.
  useEffect(() => {
    fetch("/api/tiles/parcels.pmtiles", { method: "HEAD" }).catch(() => {
      /* ignore — the map will trigger a real GET when shown */
    });
  }, []);

  // Single-letter keyboard shortcuts.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName ?? "";
      const typing = tag === "INPUT" || tag === "TEXTAREA";
      const key = e.key.toLowerCase();

      if (e.key === "Escape") {
        closeRightPanel();
        setSelectedParcel(null);
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (typing) return;

      if (key === "t") {
        e.preventDefault();
        setView("terminal");
      } else if (key === "m") {
        e.preventDefault();
        setView("map");
      } else if (key === "/") {
        e.preventDefault();
        const el = document.getElementById("vira-search") as HTMLInputElement | null;
        if (el) {
          setView("terminal");
          setTimeout(() => el.focus(), 50);
        }
      } else if (key === "g") {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent("vira:generate-memo"));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [setView, closeRightPanel, setSelectedParcel]);

  // Live clock.
  const [clock, setClock] = useState<string | null>(null);
  useEffect(() => {
    const tick = () => {
      setClock(
        new Date().toLocaleTimeString("en-US", {
          hour: "2-digit",
          minute: "2-digit",
          second: "2-digit",
          hour12: false,
        }),
      );
    };
    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, []);

  // Rotating mini-tickers — derived live from the canonical pipeline
  // (parcelReadinessAt) so the headline numbers always match what the
  // analyst sees when they click a parcel.
  const tickerStats = useMemo(() => {
    if (!allParcels) return null;
    let topGpin = "";
    let topR = -1;
    let topAcres = -1;
    let topWatershed: string | null = null;
    let noNpdesDcCount = 0;
    let npdesDcCount = 0;
    for (const p of allParcels) {
      if (!p.GPIN || p.GPIN === "9999-99-9999") continue;
      const r = parcelReadinessAt(p, subScoreWeights);
      if (r == null) continue;
      if (p.in_dc_building === 1) {
        if (p.has_npdes === 1) npdesDcCount++;
        else noNpdesDcCount++;
      }
      if (r > topR || (r === topR && p.acres > topAcres)) {
        topR = r;
        topAcres = p.acres;
        topGpin = p.GPIN;
        topWatershed = p.watershed_name ?? null;
      }
    }
    return { topGpin, topR, topWatershed, noNpdesDcCount, npdesDcCount };
  }, [allParcels, subScoreWeights]);

  const topCandidateValue = tickerStats && tickerStats.topGpin
    ? `${tickerStats.topGpin} · legibility=${tickerStats.topR}${tickerStats.topWatershed ? ` · ${tickerStats.topWatershed}` : ""}`
    : "loading…";
  const npdesValue = tickerStats
    ? `${tickerStats.noNpdesDcCount} DC buildings with NO NPDES coverage · ${tickerStats.npdesDcCount} with permits`
    : "loading…";

  const TICKERS: Array<{ label: string; value: string; tone?: "good" | "bad" | "neutral" }> = [
    { label: "MOST LEGIBLE PARCEL", value: topCandidateValue, tone: "good" },
    { label: "PHDI APR-2026", value: "-5.30 · EXTREME DROUGHT", tone: "bad" },
    { label: "NPDES COVERAGE", value: npdesValue, tone: "bad" },
    { label: "RAG CORPUS", value: "15 water-policy docs" },
    { label: "HEADLINE FINDING", value: "0 of 203 DC buildings hold NPDES water discharge permits", tone: "bad" },
  ];
  const [tickerIdx, setTickerIdx] = useState(0);
  useEffect(() => {
    const id = setInterval(() => {
      setTickerIdx((i) => (i + 1) % TICKERS.length);
    }, 4000);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  const currentTicker = TICKERS[tickerIdx];

  return (
    <div className="flex h-screen w-screen flex-col bg-neutral-950 text-neutral-100">
      {/* Primary header */}
      <header className="flex items-center justify-between border-b border-neutral-800 bg-neutral-950 px-6 py-2">
        <div className="flex items-center gap-6">
          <div className="flex items-baseline gap-2.5 select-none">
            <span className="text-base font-semibold tracking-[0.18em] text-amber-400">
              PWC WATER ATLAS
            </span>
          </div>
          <ViewToggle />
        </div>
        <div className="flex items-center gap-3 text-xs text-neutral-400">
          <AlertsFeed />
          <span className="text-neutral-300 tabular-nums">
            PRINCE WILLIAM COUNTY, VA
          </span>
        </div>
      </header>

      {/* Function bar */}
      <div className="flex items-center justify-between border-b border-neutral-900 bg-black px-6 py-1 text-[10px] uppercase tracking-wider text-neutral-500">
        <div className="flex items-center gap-3 tabular-nums min-w-0">
          <span className="text-amber-400/70 shrink-0">
            ▸ {view === "terminal" ? "DECISION TERMINAL" : "SPATIAL MAP"}
          </span>
          <span className="text-neutral-800 shrink-0">·</span>
          <span className="text-neutral-600 shrink-0">{currentTicker.label}</span>
          <span
            className={`truncate transition-colors duration-300 ${
              currentTicker.tone === "good"
                ? "text-emerald-400/90"
                : currentTicker.tone === "bad"
                  ? "text-amber-400/90"
                  : "text-neutral-300"
            }`}
            key={tickerIdx}
          >
            {currentTicker.value}
          </span>
        </div>
        <div className="flex items-center gap-3 tabular-nums shrink-0">
          <span>{clock ?? "—"}</span>
        </div>
      </div>

      {/* Main content area */}
      <div className="flex flex-1 overflow-hidden">
        <div className="flex-1 overflow-hidden">
          {view === "terminal" ? <DecisionTerminal /> : <SpatialMap />}
        </div>
        {rightPanelOpen && <RightPanel />}
      </div>

      {/* Status footer */}
      <footer className="flex items-center border-t border-neutral-900 bg-black px-6 py-0.5 text-[9px] uppercase tracking-[0.18em] text-neutral-600">
        <span className="text-amber-400/60">PWC WATER ATLAS</span>
      </footer>
    </div>
  );
}
