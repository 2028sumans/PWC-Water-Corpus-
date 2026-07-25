"use client";

/**
 * The only view: every named data-center building and campus in PWC,
 * ranked by its estimated total Scope 1/2/3 water footprint
 * (indirect_water_footprint.py). This is the tool's actual thesis.
 */
import { useMemo, useRef, useState } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useViraStore } from "@/store/useViraStore";
import { useFacilityProfiles, type BuildingProfile, type CampusProfile } from "@/lib/useFacilityProfiles";
import { Building2, Search } from "lucide-react";

interface FacilityRow {
  kind: "building" | "campus";
  gpin: string;
  name: string;
  status: string | null;
  hasNpdes: boolean;
  totalRange: [number, number];
  totalCentral: number;
  s1Central: number;
  s2Central: number;
  s3Central: number;
  peakDay: number;
  effMw: number;
  narrowed: boolean;
}

function toRow(f: BuildingProfile | CampusProfile): FacilityRow | null {
  const swf = f.scope_water_footprint;
  if (!swf) return null;
  const gpin = f.kind === "building" ? f.gpin : f.gpins[0];
  if (!gpin) return null;
  return {
    kind: f.kind,
    gpin,
    name: f.name ?? (f.kind === "building" ? "Unnamed building" : "Unnamed campus"),
    status: f.kind === "building" ? f.status : null,
    hasNpdes: f.water_context?.has_npdes === 1,
    totalRange: swf.total_mgd_range,
    totalCentral: swf.total_mgd_central,
    s1Central: swf.scope1_onsite_cooling.mgd_central,
    s2Central: swf.scope2_electricity.mgd_central,
    s3Central: swf.scope3_embodied.mgd_central,
    peakDay: swf.scope1_onsite_cooling.peak_day_mgd,
    effMw: swf.power.effective_it_mw_central,
    narrowed: swf.scope1_onsite_cooling.basis !== "technology_envelope",
  };
}

function totalBarColor(maxMgd: number): string {
  if (maxMgd >= 2) return "bg-red-500";
  if (maxMgd >= 0.75) return "bg-orange-500";
  if (maxMgd >= 0.2) return "bg-yellow-500";
  return "bg-emerald-500";
}

export function FacilitiesView() {
  const selectedGpin = useViraStore((s) => s.selectedGpin);
  const setSelectedGpin = useViraStore((s) => s.setSelectedGpin);
  const data = useFacilityProfiles();
  const [query, setQuery] = useState("");
  const [kindFilter, setKindFilter] = useState<"all" | "building" | "campus">("all");
  const [sortBy, setSortBy] = useState<"total" | "s2" | "name">("total");

  const rows = useMemo<FacilityRow[]>(() => {
    if (!data) return [];
    const all: FacilityRow[] = [];
    for (const b of data.buildings) {
      const r = toRow(b);
      if (r) all.push(r);
    }
    for (const c of data.campuses) {
      const r = toRow(c);
      if (r) all.push(r);
    }
    return all;
  }, [data]);

  const filteredSorted = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = rows;
    if (kindFilter !== "all") list = list.filter((r) => r.kind === kindFilter);
    if (q) list = list.filter((r) => r.name.toLowerCase().includes(q) || r.gpin.toLowerCase().includes(q));
    const sorted = [...list];
    if (sortBy === "total") sorted.sort((a, b) => b.totalCentral - a.totalCentral);
    else if (sortBy === "s2") sorted.sort((a, b) => b.s2Central - a.s2Central);
    else sorted.sort((a, b) => a.name.localeCompare(b.name));
    return sorted;
  }, [rows, query, kindFilter, sortBy]);

  // Campus entitlements are NOT net of the buildings already built on them
  // (remaining_gfa_sqft == planned_gfa_sqft on every campus checked) — a
  // campus and the buildings sitting on it describe overlapping square
  // footage. Summing both into one "countywide total" double- or triple-
  // counts, so the headline aggregates BUILDINGS ONLY, which is the tool's
  // actual physical inventory. Campuses remain visible and sortable as rows.
  const headline = useMemo(() => {
    const buildingRows = rows.filter((r) => r.kind === "building");
    if (!buildingRows.length) return null;
    const completed = buildingRows.filter((r) => r.status === "Completed");
    const completedS1 = completed.reduce((s, r) => s + r.s1Central, 0);
    const completedTotal = completed.reduce((s, r) => s + r.totalCentral, 0);
    const allTotal = buildingRows.reduce((s, r) => s + r.totalCentral, 0);
    const nNoNpdes = buildingRows.filter((r) => !r.hasNpdes).length;
    const nNarrowed = buildingRows.filter((r) => r.narrowed).length;
    return {
      completedS1,
      completedTotal,
      completedN: completed.length,
      allTotal,
      nNoNpdes,
      nNarrowed,
      n: buildingRows.length,
    };
  }, [rows]);

  const parentRef = useRef<HTMLDivElement | null>(null);
  const rowVirtualizer = useVirtualizer({
    count: filteredSorted.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 52,
    overscan: 12,
  });

  if (!data) {
    return (
      <div className="flex h-full w-full items-center justify-center bg-neutral-950">
        <div className="text-center">
          <div className="text-amber-400 text-sm mb-2">Loading facility dossiers...</div>
          <div className="text-neutral-500 text-xs">243 buildings + 51 campuses · Scope 1/2/3 water footprint estimator</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full w-full">
      {/* Left rail */}
      <aside className="w-72 shrink-0 border-r border-neutral-800 bg-neutral-950 p-4 overflow-y-auto">
        <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">Search</div>
        <div className="relative">
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-neutral-500" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Facility name, GPIN..."
            className="w-full rounded-sm border border-neutral-800 bg-black pl-8 pr-2 py-1.5 text-xs text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
          />
        </div>
        <div className="mt-2 text-[10px] text-neutral-500">
          {filteredSorted.length.toLocaleString()} of {rows.length.toLocaleString()} facilities
        </div>

        <div className="mt-6 text-[10px] uppercase tracking-wider text-neutral-500 mb-2">Kind</div>
        <div className="inline-flex w-full border border-neutral-800">
          {([
            { key: "all", label: "All" },
            { key: "building", label: "Built" },
            { key: "campus", label: "Campuses" },
          ] as const).map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setKindFilter(key)}
              className={`flex-1 px-2 py-1 text-[10px] uppercase tracking-wider transition ${
                kindFilter === key ? "bg-amber-500 text-neutral-950" : "text-neutral-500 hover:text-neutral-200 hover:bg-neutral-900"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        <div className="mt-6 text-[10px] uppercase tracking-wider text-neutral-500 mb-2">Sort by</div>
        <div className="inline-flex w-full border border-neutral-800">
          {([
            { key: "total", label: "Total MGD" },
            { key: "s2", label: "Scope 2" },
            { key: "name", label: "Name" },
          ] as const).map(({ key, label }) => (
            <button
              key={key}
              onClick={() => setSortBy(key)}
              className={`flex-1 px-2 py-1 text-[10px] uppercase tracking-wider transition ${
                sortBy === key ? "bg-amber-500 text-neutral-950" : "text-neutral-500 hover:text-neutral-200 hover:bg-neutral-900"
              }`}
            >
              {label}
            </button>
          ))}
        </div>

        {headline && (
          <div className="mt-8 rounded border border-neutral-800 bg-neutral-900/50 p-3 text-[11px] text-neutral-400 leading-relaxed space-y-2">
            <div>
              <span className="text-neutral-200 font-medium">{headline.completedS1.toFixed(2)} MGD</span>{" "}
              direct on-site cooling water, {headline.completedN}{" "}completed buildings today.
              Prince William Water reported 0.42 MGD across its service area in 2023 — a wider
              boundary than the county, and not an independent check, since the intensity this
              model uses was itself derived from that figure.
            </div>
            <div>
              <span className="text-neutral-300 font-medium">{headline.allTotal.toFixed(1)} MGD</span>{" "}
              Scope 1+2+3 central estimate across all {headline.n} tracked buildings (built, under
              construction, and planned).
            </div>
            <div className="text-amber-400/90">
              {headline.nNoNpdes} of {headline.n} hold no NPDES water discharge permit under their own facility.
            </div>
            {headline.nNarrowed > 0 && (
              <div className="text-emerald-400/90">
                {headline.nNarrowed} narrowed below the default technology envelope by a published
                operator cooling commitment or a binding permit condition.
              </div>
            )}
          </div>
        )}
        <div className="mt-4 text-[10px] text-neutral-600 leading-relaxed italic">
          Central estimates use Prince William Water&apos;s own observed intensity
          (309 gal/MW/day, ICPRB 2025). Campus rows are entitlements that
          overlap with buildings already counted above, so they&apos;re
          excluded from these totals — sort by campus to see them
          individually. Click a facility for the full derivation.
        </div>
      </aside>

      {/* Center: virtualized facility table */}
      <main className="flex-1 flex flex-col bg-neutral-950 min-w-0">
        <div className="border-b border-neutral-800 bg-neutral-950 px-4 py-2 flex items-baseline gap-3">
          <h2 className="text-[11px] uppercase tracking-[0.15em] text-neutral-300">
            <span className="text-amber-400/80">PWC</span>
            <span className="text-neutral-700 mx-2">·</span>
            <span className="tabular-nums">{filteredSorted.length.toLocaleString()}</span>
            <span className="text-neutral-500 ml-1.5">facilities</span>
          </h2>
        </div>

        <div className="sticky top-0 z-10 grid grid-cols-[minmax(200px,1fr)_90px_90px_130px_130px_130px_150px] gap-0 px-0 py-1.5 border-b border-neutral-800 bg-black text-[10px] uppercase tracking-[0.15em] text-neutral-500 [&>*]:px-3 [&>*]:border-l [&>*]:border-neutral-900/70 [&>*:first-child]:border-l-0">
          <div>Facility</div>
          <div>Kind</div>
          <div className="text-right" title="Effective IT load — from a VADEQ permit where observed, otherwise inferred via the fitted GFA→MW model">IT MW</div>
          <div className="text-right" title="Direct on-site cooling water, central estimate">Scope 1</div>
          <div className="text-right" title="Water consumed at the generating plant, central estimate">Scope 2</div>
          <div className="text-right" title="Embodied / supply-chain, central estimate">Scope 3</div>
          <div title="Central estimate, with the summer peak-day direct draw beneath">Total MGD · peak</div>
        </div>

        <div ref={parentRef} className="flex-1 overflow-auto">
          <div style={{ height: rowVirtualizer.getTotalSize(), width: "100%", position: "relative" }}>
            {rowVirtualizer.getVirtualItems().map((vItem) => {
              const r = filteredSorted[vItem.index];
              const isSelected = r.gpin === selectedGpin;
              return (
                <div
                  key={`${r.gpin}-${vItem.index}`}
                  onClick={() => setSelectedGpin(r.gpin)}
                  className={`grid grid-cols-[minmax(200px,1fr)_90px_90px_130px_130px_130px_150px] gap-0 px-0 py-2 border-b border-neutral-900 cursor-pointer text-xs [&>*]:px-3 [&>*]:border-l [&>*]:border-neutral-900/50 [&>*:first-child]:border-l-0 ${
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
                  <div className="min-w-0">
                    <div className="text-neutral-100 truncate flex items-center gap-1.5">
                      <Building2 className="h-3 w-3 text-neutral-600 shrink-0" />
                      {r.name}
                    </div>
                    <div className="text-[10px] text-neutral-500 truncate">
                      {r.gpin} {r.status ? `· ${r.status}` : ""} {!r.hasNpdes ? "· no NPDES coverage" : ""}
                    </div>
                  </div>
                  <div className="text-neutral-400 text-[11px] flex items-center capitalize">
                    {r.kind}
                    {r.narrowed && (
                      <span className="ml-1 text-emerald-400" title="Narrowed by a published operator WUE or binding permit condition">
                        ◆
                      </span>
                    )}
                  </div>
                  <div className="text-right text-neutral-300 tabular-nums text-[11px] flex items-center justify-end">
                    {r.effMw.toFixed(0)}
                  </div>
                  <div className="text-right text-amber-300/90 tabular-nums text-[11px] flex items-center justify-end">
                    {r.s1Central.toFixed(3)}
                  </div>
                  <div className="text-right text-sky-300/90 tabular-nums text-[11px] flex items-center justify-end">
                    {r.s2Central.toFixed(3)}
                  </div>
                  <div className="text-right text-violet-300/90 tabular-nums text-[11px] flex items-center justify-end">
                    {r.s3Central.toFixed(3)}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-12 h-1.5 rounded bg-neutral-800 overflow-hidden shrink-0">
                      <div
                        className={`h-full ${totalBarColor(r.totalCentral)} transition-all duration-300`}
                        style={{ width: `${Math.min(100, (r.totalCentral / 3) * 100)}%` }}
                      />
                    </div>
                    <span className="text-neutral-200 tabular-nums text-[11px]">
                      {r.totalCentral.toFixed(2)}
                    </span>
                    <span className="text-neutral-600 tabular-nums text-[10px]" title="Summer peak-day direct on-site draw">
                      ▲{r.peakDay.toFixed(2)}
                    </span>
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
