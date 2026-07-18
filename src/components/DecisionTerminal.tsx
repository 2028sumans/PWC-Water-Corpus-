"use client";

import { useMemo, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useViraStore, type QuickFilters } from "@/store/useViraStore";
import { useScoredParcels, parcelAddress, type ScoredParcel } from "@/lib/useScoredParcels";
import { parcelReadinessAt } from "@/lib/parcelReadiness";
import { Search } from "lucide-react";
import { PortfolioBar, AddToPortfolioButton } from "./PortfolioBar";

function scoreColor(score: number): string {
  if (score >= 80) return "bg-green-900/60 text-green-200";
  if (score >= 60) return "bg-yellow-900/60 text-yellow-200";
  if (score >= 40) return "bg-orange-900/60 text-orange-200";
  return "bg-red-900/60 text-red-200";
}

function legibilityBarColor(score: number): string {
  if (score >= 80) return "bg-green-500";
  if (score >= 60) return "bg-yellow-500";
  if (score >= 40) return "bg-orange-500";
  return "bg-red-500";
}

export function DecisionTerminal() {
  const selectedParcelId = useViraStore((s) => s.selectedParcelId);
  const setSelectedParcel = useViraStore((s) => s.setSelectedParcel);
  const searchQuery = useViraStore((s) => s.searchQuery);
  const setSearchQuery = useViraStore((s) => s.setSearchQuery);
  const subScoreWeights = useViraStore((s) => s.subScoreWeights);

  const { parcels, loading, error } = useScoredParcels();
  const filters = useViraStore((s) => s.quickFilters);
  const setQuickFilter = useViraStore((s) => s.setQuickFilter);
  const resetQuickFilters = useViraStore((s) => s.resetQuickFilters);
  const toggleFilter = (k: keyof QuickFilters) =>
    setQuickFilter(k, !filters[k] as QuickFilters[typeof k]);

  // Each visible row needs its CANONICAL Water Legibility Score — the same
  // number the right panel shows — not the raw Python-precomputed hint.
  // Computed once per parcel here so we can both sort and display from the
  // same value. Re-runs only when weights, filters, or search changes.
  const filteredSorted = useMemo<Array<{ p: ScoredParcel; r: number }>>(() => {
    if (!parcels) return [];
    const q = searchQuery.trim().toLowerCase();
    // Drop county placeholder GPINs ("9999-99-9999") — these are ROW / common
    // areas / unrecorded fragments, not real parcels.
    let list = parcels.filter((p) => p.GPIN && p.GPIN !== "9999-99-9999");
    if (q) {
      list = list.filter((p) => {
        if (p.GPIN.toLowerCase().includes(q)) return true;
        if (p.zoning && p.zoning.toLowerCase().includes(q)) return true;
        if (p.StreetName && p.StreetName.toLowerCase().includes(q)) return true;
        if (p.City && p.City.toLowerCase().includes(q)) return true;
        if (p.SubdivisionName && p.SubdivisionName.toLowerCase().includes(q)) return true;
        if (p.watershed_name && p.watershed_name.toLowerCase().includes(q)) return true;
        return false;
      });
    }
    // Quick filters
    if (filters.dcBuildingsOnly) list = list.filter((p) => p.in_dc_building === 1);
    if (filters.inWatershedStress) list = list.filter((p) => (p.n_dc_in_watershed ?? 0) >= 5);
    if (filters.nearStream)
      list = list.filter((p) => p.d_stream_ft !== null && p.d_stream_ft !== undefined && p.d_stream_ft < 300);
    if (filters.noNpdesCoverage) list = list.filter((p) => p.has_npdes !== 1);
    if (filters.hasMonitoringStation)
      list = list.filter((p) => (p.n_wqp_stations_1mi ?? 0) > 0 || (p.n_deq_monitoring_1mi ?? 0) > 0);

    // Compute the canonical Water Legibility Score once per parcel — same
    // pipeline the right panel uses, so the table and panel always match.
    let scored = list.map((p) => ({
      p,
      r: parcelReadinessAt(p, subScoreWeights) ?? p.readiness,
    }));
    if (filters.minWaterRisk > 0) {
      scored = scored.filter(({ r }) => r >= filters.minWaterRisk);
    }

    // Sort by Water Legibility desc, tiebreak by acres desc
    scored.sort((a, b) => {
      if (b.r !== a.r) return b.r - a.r;
      return b.p.acres - a.p.acres;
    });
    return scored;
  }, [parcels, searchQuery, filters, subScoreWeights]);

  // Virtualizer
  const parentRef = useRef<HTMLDivElement | null>(null);
  const rowVirtualizer = useVirtualizer({
    count: filteredSorted.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 44,
    overscan: 12,
  });

  if (loading) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-neutral-950">
        <div className="text-center">
          <div className="text-amber-400 text-sm mb-2">Loading scored parcels...</div>
          <div className="text-neutral-500 text-xs">159,181 parcels · pre-computed Water Legibility across 38 data layers</div>
        </div>
      </div>
    );
  }
  if (error) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-neutral-950">
        <div className="max-w-md text-center">
          <div className="text-red-400 text-sm mb-2">Could not load parcel scores</div>
          <pre className="text-[11px] text-neutral-500 bg-neutral-900 p-3 rounded border border-neutral-800 text-left">
            {error}
          </pre>
          <p className="text-xs text-neutral-500 mt-3 leading-relaxed">
            The scoring script may still be running. Once
            <code className="bg-neutral-800 px-1 mx-1 rounded text-[10px]">
              public/data/parcels_scored.json.gz
            </code>
            exists, refresh the page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full">
      {/* Left rail */}
      <aside className="w-72 shrink-0 border-r border-neutral-800 bg-neutral-950 p-4 overflow-y-auto">
        <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
          Search
        </div>
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-500" />
          <input
            id="vira-search"
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="GPIN, street, zoning, watershed..."
            className="w-full rounded-sm border border-neutral-800 bg-black pl-8 pr-2 py-1.5 text-xs text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
          />
          <kbd className="absolute right-1.5 top-1/2 -translate-y-1/2 text-[9px] text-neutral-600 px-1 border border-neutral-800 pointer-events-none">
            /
          </kbd>
        </div>
        <div className="mt-2 text-[10px] text-neutral-500">
          {filteredSorted.length.toLocaleString()} of {(parcels ?? []).length.toLocaleString()} parcels
        </div>

        <div className="mt-6 text-[10px] uppercase tracking-wider text-neutral-500 mb-2 flex items-center justify-between">
          <span>Quick Filters</span>
          {(filters.dcBuildingsOnly ||
            filters.inWatershedStress ||
            filters.nearStream ||
            filters.noNpdesCoverage ||
            filters.hasMonitoringStation ||
            filters.minWaterRisk > 0) && (
            <button
              onClick={() => resetQuickFilters()}
              className="text-amber-400 hover:text-amber-300 text-[9px] normal-case"
            >
              clear all
            </button>
          )}
        </div>
        <div className="space-y-1 text-xs">
          {([
            { key: "dcBuildingsOnly", label: "Data center building" },
            { key: "inWatershedStress", label: "In watershed stress (≥5 DCs)" },
            { key: "nearStream", label: "Within 300ft of stream" },
            { key: "noNpdesCoverage", label: "No NPDES coverage" },
            { key: "hasMonitoringStation", label: "Has monitoring station" },
          ] as const).map(({ key, label }) => (
            <label
              key={key}
              className="flex items-center gap-2 text-neutral-400 hover:text-neutral-200 cursor-pointer"
            >
              <input
                type="checkbox"
                checked={filters[key]}
                onChange={() => toggleFilter(key)}
                className="accent-amber-500"
              />
              <span className={filters[key] ? "text-amber-300" : ""}>{label}</span>
            </label>
          ))}
        </div>

        <PortfolioBar />

        <div className="mt-8 rounded border border-neutral-800 bg-neutral-900/50 p-3 text-[11px] text-neutral-500 leading-relaxed">
          <span className="text-neutral-300 font-medium">Tip:</span> rows are
          sorted by Water Legibility Score — the least-legible parcels
          (built DC, no NPDES coverage) are the tool&apos;s headline finding.
        </div>
      </aside>

      {/* Center: virtualized table */}
      <main className="flex-1 flex flex-col bg-neutral-950 min-w-0">
        <div className="border-b border-neutral-800 bg-neutral-950 px-4 py-2 flex items-baseline gap-3">
          <h2 className="text-[11px] uppercase tracking-[0.15em] text-neutral-300">
            <span className="text-amber-400/80">PWC</span>
            <span className="text-neutral-700 mx-2">·</span>
            <span className="tabular-nums">{filteredSorted.length.toLocaleString()}</span>
            <span className="text-neutral-500 ml-1.5">parcels</span>
          </h2>
        </div>

        <div className="sticky top-0 z-10 grid grid-cols-[140px_minmax(180px,1fr)_70px_70px_120px_120px_26px] gap-0 px-0 py-1.5 border-b border-neutral-800 bg-black text-[10px] uppercase tracking-[0.15em] text-neutral-500 [&>*]:px-3 [&>*]:border-l [&>*]:border-neutral-900/70 [&>*:first-child]:border-l-0">
          <div>GPIN</div>
          <div>Address / Subdivision</div>
          <div className="text-right">Acres</div>
          <div>Zoning</div>
          <div>Watershed</div>
          <div className="text-center">Water Legibility</div>
          <div className="text-center" title="Add to active portfolio">+</div>
        </div>

        {/* Virtual list scroller */}
        <div ref={parentRef} className="flex-1 overflow-auto">
          <div
            style={{
              height: rowVirtualizer.getTotalSize(),
              width: "100%",
              position: "relative",
            }}
          >
            {rowVirtualizer.getVirtualItems().map((vItem) => {
              const { p, r } = filteredSorted[vItem.index];
              const isSelected = p.GPIN === selectedParcelId;
              return (
                <div
                  key={`${p.GPIN}-${vItem.index}`}
                  onClick={() => setSelectedParcel(p.GPIN)}
                  className={`grid grid-cols-[140px_minmax(180px,1fr)_70px_70px_120px_120px_26px] gap-0 px-0 py-2 border-b border-neutral-900 cursor-pointer text-xs [&>*]:px-3 [&>*]:border-l [&>*]:border-neutral-900/50 [&>*:first-child]:border-l-0 ${
                    isSelected ? "bg-amber-500/10" : "hover:bg-neutral-900"
                  }`}
                  style={{
                    position: "absolute",
                    top: 0,
                    left: 0,
                    right: 0,
                    height: vItem.size,
                    transform: `translateY(${vItem.start}px)`,
                  }}
                >
                  <div className="text-[11px] text-amber-400 truncate">
                    {p.GPIN}
                  </div>
                  <div className="min-w-0">
                    <div className="text-neutral-100 truncate">
                      {parcelAddress(p) || (p.SubdivisionName ?? "—")}
                    </div>
                    {p.City && (
                      <div className="text-[10px] text-neutral-500 truncate">
                        {p.City} {p.in_dc_building ? "· DC building" : ""}
                      </div>
                    )}
                  </div>
                  <div className="text-right text-neutral-300 tabular-nums">
                    {p.acres < 1 ? p.acres.toFixed(2) : p.acres.toFixed(1)}
                  </div>
                  <div className="text-neutral-300 truncate">{p.zoning ?? "—"}</div>
                  <div className="text-neutral-400 text-[11px] truncate">
                    {p.watershed_name ?? ""}
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <div className="w-12 h-1.5 rounded bg-neutral-800 overflow-hidden">
                      <div
                        className={`h-full ${legibilityBarColor(r)} transition-all duration-300`}
                        style={{ width: `${r}%` }}
                      />
                    </div>
                    <span
                      className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${scoreColor(r)} transition-colors duration-300`}
                    >
                      {r}
                    </span>
                  </div>
                  <div className="flex items-center justify-center">
                    <AddToPortfolioButton gpin={p.GPIN} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </main>
    </div>
  );
}
