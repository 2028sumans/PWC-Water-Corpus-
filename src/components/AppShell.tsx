"use client";

import { useEffect, useMemo, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { useFacilityProfiles } from "@/lib/useFacilityProfiles";
import { useCountyAnalysis } from "@/lib/useCountyAnalysis";
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
  useFacilityProfiles();
  // County analyses, for the headline line below and the panel in the sidebar.
  const analysis = useCountyAnalysis();
  // Bidirectional URL ↔ store sync so refreshes preserve the session.
  useUrlStateSync();
  // Preload policy-corpus index so the right panel can show citation counts.
  usePolicyIndex();

  // Escape closes the right panel and clears the selection.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== "Escape") return;
      closeRightPanel();
      setSelectedGpin(null);
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

  // ONE static headline, not a carousel.
  //
  // This bar used to rotate nine claims on a 4s timer. That is hostile to the
  // reader in a way that is easy to miss while building it: a fact you cannot
  // finish reading, cannot re-read, and cannot point at is worse than no fact,
  // and motion in the chrome competes with the table that is the actual work.
  // It also buried the result -- the convention spread got 4 seconds in 36.
  //
  // So: state the headline result and leave it on screen. Everything the
  // rotation used to carry is either in the sidebar summary (fleet total, NPDES
  // coverage, narrowed count) or in the county-analysis panel below it, where a
  // reader can go at their own pace.
  const headline = useMemo(() => {
    const r = analysis?.conventions?.lake_anna_share_range_pct;
    if (!r) {
      return { label: "SCOPE 2 DOMINATES", value: "grid water, not on-site cooling, is the bulk of the footprint" };
    }
    return {
      label: "WHICH BASIN GETS CHARGED",
      value: `Lake Anna carries ${r.min}%–${r.max}% of the same electricity-related water — a ${Math.round(
        r.spread_factor,
      )}× swing on accounting convention alone, before anything physical changes`,
    };
  }, [analysis]);

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
          <span className="text-neutral-600 shrink-0">{headline.label}</span>
          <span className="truncate text-neutral-300">{headline.value}</span>
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
            with fresh per-facility state (the verdict stream, open popovers). */}
        {rightPanelOpen && <RightPanel key={selectedGpin} />}
      </div>

      {/* Status footer */}
      <footer className="flex items-center border-t border-neutral-900 bg-black px-6 py-0.5 text-[9px] uppercase tracking-[0.18em] text-neutral-600">
        <span className="text-amber-400/60">PWC WATER ATLAS</span>
      </footer>
    </div>
  );
}
