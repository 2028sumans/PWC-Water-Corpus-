"use client";

import { useEffect, useMemo, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { useFacilityProfiles } from "@/lib/useFacilityProfiles";
import { usePolicyIndex } from "@/lib/usePolicyIndex";
import { useUrlStateSync } from "@/lib/useUrlStateSync";
import { FacilitiesView } from "./FacilitiesView";
import { RightPanel } from "./RightPanel";

export function AppShell() {
  const rightPanelOpen = useViraStore((s) => s.rightPanelOpen);
  const selectedGpin = useViraStore((s) => s.selectedGpin);
  const closeRightPanel = useViraStore((s) => s.closeRightPanel);
  const setSelectedGpin = useViraStore((s) => s.setSelectedGpin);

  // Preload facility dossiers at app start so clicks resolve immediately.
  const data = useFacilityProfiles();
  // Bidirectional URL ↔ store sync so refreshes preserve the session.
  useUrlStateSync();
  // Preload policy-corpus index so the right panel can show citation counts.
  usePolicyIndex();

  // Single-letter keyboard shortcuts.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement | null)?.tagName ?? "";
      const typing = tag === "INPUT" || tag === "TEXTAREA";
      const key = e.key.toLowerCase();

      if (e.key === "Escape") {
        closeRightPanel();
        setSelectedGpin(null);
        return;
      }
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      if (typing) return;

      if (key === "g") {
        e.preventDefault();
        window.dispatchEvent(new CustomEvent("vira:generate-memo"));
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [closeRightPanel, setSelectedGpin]);

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

  // Rotating mini-tickers — derived live from the same Scope 1/2/3 water
  // footprint estimates (indirect_water_footprint.py) the right panel shows,
  // so the headline numbers always match what the analyst sees on click.
  // BUILDINGS ONLY: a campus's entitlement GFA is not net of the buildings
  // already built on it, so summing buildings + campuses double-counts.
  const tickerStats = useMemo(() => {
    if (!data) return null;
    let topName = "";
    let topCentral = -1;
    let completedS1 = 0;
    let completedN = 0;
    let allCentral = 0;
    let noNpdesCount = 0;
    let npdesCount = 0;
    let n = 0;
    for (const f of data.buildings) {
      const swf = f.scope_water_footprint;
      if (!swf) continue;
      n++;
      allCentral += swf.total_mgd_central;
      if (f.status === "Completed") {
        completedS1 += swf.scope1_onsite_cooling.mgd_central;
        completedN++;
      }
      if (f.water_context?.has_npdes === 1) npdesCount++;
      else noNpdesCount++;
      if (swf.total_mgd_central > topCentral) {
        topCentral = swf.total_mgd_central;
        topName = f.name ?? "Unnamed building";
      }
    }
    return { topName, topCentral, completedS1, completedN, allCentral, noNpdesCount, npdesCount, n };
  }, [data]);

  const topCandidateValue = tickerStats && tickerStats.topName
    ? `${tickerStats.topName} · ~${tickerStats.topCentral.toFixed(2)} MGD central est.`
    : "loading…";
  const npdesValue = tickerStats
    ? `${tickerStats.noNpdesCount} of ${tickerStats.n} buildings with NO NPDES coverage · ${tickerStats.npdesCount} with permits`
    : "loading…";
  const totalValue = tickerStats
    ? `${tickerStats.completedS1.toFixed(2)} MGD direct on-site, ${tickerStats.completedN} completed buildings (validated vs. PWC Water 2023)`
    : "loading…";

  const TICKERS: Array<{ label: string; value: string; tone?: "good" | "bad" | "neutral" }> = [
    { label: "LARGEST ESTIMATED FOOTPRINT", value: topCandidateValue, tone: "bad" },
    { label: "COMPLETED FLEET, DIRECT WATER", value: totalValue },
    { label: "NPDES COVERAGE", value: npdesValue, tone: "bad" },
    { label: "RAG CORPUS", value: "policy + methodology docs" },
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
        </div>
        <div className="flex items-center gap-3 text-xs text-neutral-400">
          <span className="text-neutral-300 tabular-nums">
            PRINCE WILLIAM COUNTY, VA
          </span>
        </div>
      </header>

      {/* Function bar */}
      <div className="flex items-center justify-between border-b border-neutral-900 bg-black px-6 py-1 text-[10px] uppercase tracking-wider text-neutral-500">
        <div className="flex items-center gap-3 tabular-nums min-w-0">
          <span className="text-amber-400/70 shrink-0">▸ FACILITIES</span>
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
          <FacilitiesView />
        </div>
        {/* Keyed on the selection so switching facilities remounts the panel
            with fresh per-facility state (memo/Q&A streams, open popovers). */}
        {rightPanelOpen && <RightPanel key={selectedGpin} />}
      </div>

      {/* Status footer */}
      <footer className="flex items-center border-t border-neutral-900 bg-black px-6 py-0.5 text-[9px] uppercase tracking-[0.18em] text-neutral-600">
        <span className="text-amber-400/60">PWC WATER ATLAS</span>
      </footer>
    </div>
  );
}
