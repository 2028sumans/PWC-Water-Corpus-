"use client";

import { useViraStore } from "@/store/useViraStore";
import { LayoutGrid, MapPin } from "lucide-react";

export function ViewToggle() {
  const view = useViraStore((s) => s.view);
  const setView = useViraStore((s) => s.setView);

  return (
    <div className="inline-flex items-center border border-neutral-800 bg-black">
      <button
        onClick={() => setView("terminal")}
        className={`flex items-center gap-1.5 px-3 py-1 text-[11px] uppercase tracking-wider transition border-r border-neutral-800 ${
          view === "terminal"
            ? "bg-amber-500 text-neutral-950"
            : "text-neutral-500 hover:text-neutral-200 hover:bg-neutral-950"
        }`}
        aria-pressed={view === "terminal"}
        title="Decision Terminal — press T"
      >
        <LayoutGrid className="h-3 w-3" />
        Decision Terminal
        <kbd className={`ml-1 text-[9px] tracking-normal px-1 border ${view === "terminal" ? "border-neutral-900/40 text-neutral-900/70" : "border-neutral-800 text-neutral-700"}`}>T</kbd>
      </button>
      <button
        onClick={() => setView("map")}
        className={`flex items-center gap-1.5 px-3 py-1 text-[11px] uppercase tracking-wider transition ${
          view === "map"
            ? "bg-amber-500 text-neutral-950"
            : "text-neutral-500 hover:text-neutral-200 hover:bg-neutral-950"
        }`}
        aria-pressed={view === "map"}
        title="Spatial Map — press M"
      >
        <MapPin className="h-3 w-3" />
        Spatial Map
        <kbd className={`ml-1 text-[9px] tracking-normal px-1 border ${view === "map" ? "border-neutral-900/40 text-neutral-900/70" : "border-neutral-800 text-neutral-700"}`}>M</kbd>
      </button>
    </div>
  );
}
