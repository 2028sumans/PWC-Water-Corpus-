"use client";

import { useEffect, useMemo, useState } from "react";
import { useViraStore, SUBSCORE_LABELS, type SubScoreKey } from "@/store/useViraStore";
import { findScoredParcel, parcelAddress } from "@/lib/useScoredParcels";
import { computeReadiness } from "@/lib/parcelReadiness";
import { synthesizeSubScores } from "@/lib/synthesizeSubScores";
import { usePolicyIndex } from "@/lib/usePolicyIndex";
import { topSourcesForParcel } from "@/lib/topSourcesForParcel";
import { useMemoStream, type MemoRequest } from "@/lib/useMemoStream";
import { convictionGaps, convictionSummary } from "@/lib/convictionGaps";
import { synthesizeThresholds, type SensitivityThreshold } from "@/lib/sensitivity/findThresholds";
import { useFacilityProfiles, findBuildingByGpin, findCampusByGpin, type FacilityCaseRecord } from "@/lib/useFacilityProfiles";
import { CitedText } from "./CitedText";
import { X, ExternalLink, MessageSquare, Loader2, Check, Minus, Pin, ArrowLeftRight, FileText } from "lucide-react";

function EvidenceRow({ label, value }: { label: string; value: string | number | null | undefined }) {
  const present = value !== null && value !== undefined && value !== "";
  return (
    <div className="flex items-start gap-1.5 text-[11px]">
      {present ? (
        <Check className="h-3 w-3 mt-0.5 text-green-500 shrink-0" />
      ) : (
        <Minus className="h-3 w-3 mt-0.5 text-neutral-600 shrink-0" />
      )}
      <span className="text-neutral-500 shrink-0">{label}:</span>
      <span className={present ? "text-neutral-200" : "text-neutral-600 italic"}>
        {present ? value : "not on record"}
      </span>
    </div>
  );
}

const SCOPE_TONE_CLASSES: Record<"amber" | "sky" | "violet", { text: string; border: string; bg: string }> = {
  amber: { text: "text-amber-300", border: "border-amber-900/40", bg: "bg-amber-950/10" },
  sky: { text: "text-sky-300", border: "border-sky-900/40", bg: "bg-sky-950/10" },
  violet: { text: "text-violet-300", border: "border-violet-900/40", bg: "bg-violet-950/10" },
};

function ScopeRow({
  label,
  tone,
  mgdRange,
  detail,
  methodology,
  climatePointMgd,
  climateNote,
}: {
  label: string;
  tone: "amber" | "sky" | "violet";
  mgdRange: [number, number];
  detail: string;
  methodology: string;
  climatePointMgd?: number | null;
  climateNote?: string | null;
}) {
  const c = SCOPE_TONE_CLASSES[tone];
  return (
    <div className={`mt-1.5 rounded border ${c.border} ${c.bg} px-2.5 py-1.5`}>
      <div className="flex items-baseline justify-between gap-2">
        <span className={`text-[10px] uppercase tracking-wider ${c.text}`}>{label}</span>
        <span className="text-sm font-light text-neutral-100 shrink-0">
          {mgdRange[0].toFixed(3)}–{mgdRange[1].toFixed(3)}{" "}
          <span className="text-[9px] text-neutral-500 font-normal">MGD</span>
        </span>
      </div>
      <div className="mt-1 text-[10px] text-neutral-500 leading-relaxed">{detail}</div>
      <div className="mt-1 text-[9px] text-neutral-600 leading-relaxed italic">{methodology}</div>
      {climatePointMgd != null && (
        <div className={`mt-1.5 pt-1.5 border-t ${c.border} text-[10px] ${c.text} leading-relaxed`}>
          Climate-weighted point (if evaporative/hybrid): <span className="font-medium">{climatePointMgd.toFixed(3)} MGD</span>
          {climateNote && <div className="mt-0.5 text-neutral-600 italic">{climateNote}</div>}
        </div>
      )}
    </div>
  );
}

function CaseHistoryRow({ c }: { c: FacilityCaseRecord }) {
  const number = c.ZoningCaseNumber ?? c.BZACaseNumber ?? c.PlanningCaseNumber;
  const type = c.UsePermitType ?? c.BZACaseType ?? c.PlanningCaseType;
  const name = c.ZoningCaseName ?? c.BZACaseName ?? c.PlanningCaseName;
  const status = c.UsePermitStatus;
  const dates = [c.DateApproved, c.TransmittalDate].filter(Boolean)[0];
  return (
    <div className="rounded border border-neutral-800 bg-neutral-900/40 px-2.5 py-1.5 text-[11px]">
      <div className="flex items-center justify-between gap-2">
        <span className="text-amber-400">{number}</span>
        <span className="text-neutral-500 text-[10px]">{type}</span>
      </div>
      {name && <div className="text-neutral-300 mt-0.5 truncate">{name}</div>}
      <div className="mt-0.5 flex items-center gap-2 text-[10px] text-neutral-500">
        {status && <span>{status}</span>}
        {dates && <span>{new Date(dates).getFullYear()}</span>}
        {c.StaffReportLink && (
          <a
            href={c.StaffReportLink}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-sky-400 hover:text-sky-300"
          >
            <FileText className="h-2.5 w-2.5" />
            staff report
          </a>
        )}
      </div>
    </div>
  );
}

const ORDERED_SUBSCORES: SubScoreKey[] = [
  "watershedVulnerability",
  "facilityWaterContext",
  "droughtExposure",
  "disclosureLegibility",
  "communityObsDensity",
  "municipalSupplyHeadroom",
  "stormwaterBurden",
];

function qualityBadge(q: "M" | "Md" | "I") {
  if (q === "M") return { label: "Measured", className: "border-green-700 text-green-300" };
  if (q === "Md") return { label: "Modeled", className: "border-amber-700 text-amber-300" };
  return { label: "Inferred", className: "border-neutral-700 text-neutral-400" };
}

function legibilityColor(s: number) {
  if (s >= 80) return "text-green-400";
  if (s >= 60) return "text-yellow-400";
  if (s >= 40) return "text-orange-400";
  return "text-red-400";
}

export function RightPanel() {
  const selectedParcelId = useViraStore((s) => s.selectedParcelId);
  const closeRightPanel = useViraStore((s) => s.closeRightPanel);
  const setSelectedParcel = useViraStore((s) => s.setSelectedParcel);
  const subScoreWeights = useViraStore((s) => s.subScoreWeights);
  // Compare-view state.
  const pinnedParcelId = useViraStore((s) => s.pinnedParcelId);
  const setPinnedParcel = useViraStore((s) => s.setPinnedParcel);
  const pinnedParcel = useMemo(
    () => (pinnedParcelId ? findScoredParcel(pinnedParcelId) : undefined),
    [pinnedParcelId],
  );
  const pinnedSynth = useMemo(
    () => (pinnedParcel ? synthesizeSubScores(pinnedParcel) : null),
    [pinnedParcel],
  );
  const pinnedLegibility = useMemo(() => {
    if (!pinnedSynth) return null;
    return computeReadiness(pinnedSynth.subScores, subScoreWeights);
  }, [pinnedSynth, subScoreWeights]);
  const isComparing = !!pinnedParcelId && pinnedParcelId !== selectedParcelId;
  const policy = usePolicyIndex();
  useFacilityProfiles();

  const scored = useMemo(
    () => (selectedParcelId ? findScoredParcel(selectedParcelId) : undefined),
    [selectedParcelId]
  );

  const synthesized = useMemo(
    () => (scored ? synthesizeSubScores(scored) : null),
    [scored]
  );

  // The top source documents/datasets that ACTUALLY drove this parcel's
  // score, ranked by impact magnitude.
  const topSources = useMemo(
    () => (scored ? topSourcesForParcel(scored, 6) : []),
    [scored]
  );

  const legibility = useMemo(() => {
    if (!synthesized) return null;
    return computeReadiness(synthesized.subScores, subScoreWeights);
  }, [synthesized, subScoreWeights]);

  // LLM streaming state — one stream instance per output (memo / counter /
  // qa / verdict). Each gets reset when the selected parcel changes.
  const memo = useMemoStream();
  const counter = useMemoStream();
  const qa = useMemoStream();
  const verdict = useMemoStream();
  const [qaQuestion, setQaQuestion] = useState("");
  const [dataDepthOpen, setDataDepthOpen] = useState(false);
  useEffect(() => {
    memo.reset();
    counter.reset();
    qa.reset();
    verdict.reset();
    setQaQuestion("");
    setDataDepthOpen(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedParcelId]);

  // Auto-fire the one-sentence AI verdict the moment a parcel is selected.
  useEffect(() => {
    if (!scored) return;
    const id = window.setTimeout(() => {
      if (verdict.isLoading || verdict.text) return;
      verdict.generate({
        gpin: scored.GPIN,
        mode: "verdict" as MemoRequest["mode"],
        parcelContext: buildParcelContext(),
      });
    }, 60);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [scored?.GPIN]);

  // Listen for the global "g" keyboard shortcut (dispatched by AppShell).
  useEffect(() => {
    const onGenerate = () => {
      if (!scored || memo.isLoading) return;
      memo.generate({
        gpin: scored.GPIN,
        mode: "memo",
        parcelContext: buildParcelContext(),
      });
    };
    window.addEventListener("vira:generate-memo", onGenerate);
    return () => window.removeEventListener("vira:generate-memo", onGenerate);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  });

  // Sensitivity thresholds — "what would have to be true" for the binding
  // sub-scores to clear a target.
  const sensitivityThresholds: SensitivityThreshold[] = useMemo(() => {
    if (!scored || !synthesized) return [];
    return synthesizeThresholds(scored, synthesized.subScores, subScoreWeights, { targetScore: 60, maxThresholds: 4 });
  }, [scored, synthesized, subScoreWeights]);

  const buildingProfile = scored ? findBuildingByGpin(scored.GPIN) : undefined;
  const campusProfile = scored ? findCampusByGpin(scored.GPIN) : undefined;
  const allCases = [
    ...(buildingProfile?.use_permits ?? []),
    ...(buildingProfile?.bza_cases ?? []),
    ...(buildingProfile?.pending_cases ?? []),
    ...(campusProfile?.use_permits ?? []),
    ...(campusProfile?.bza_cases ?? []),
    ...(campusProfile?.pending_cases ?? []),
  ];

  if (!scored || !synthesized || legibility === null) return null;

  const displayName = scored.SubdivisionName ?? parcelAddress(scored) ?? "Parcel " + scored.GPIN;
  const displayAddress = parcelAddress(scored) ?? "—";

  // Compact parcel context sent to /api/memo — only the bits the LLM needs.
  function buildParcelContext(): MemoRequest["parcelContext"] {
    const flags: string[] = [];
    if (scored!.in_dc_building) {
      const n = scored!.n_dc_buildings ?? 1;
      flags.push(
        n > 1
          ? `${n} data center buildings on parcel (${scored!.dc_building_name ?? "first one"} + ${n - 1} more)`
          : `Data center building on parcel${scored!.dc_building_name ? `: ${scored!.dc_building_name}` : ""}`,
      );
    } else if (scored!.in_dc_campus) {
      flags.push(`Planned DC campus footprint${scored!.dc_campus_name ? `: ${scored!.dc_campus_name}` : ""}`);
    }
    if (scored!.has_npdes) flags.push("Holds an NPDES water discharge permit (rare)");
    else if (scored!.in_dc_building) flags.push("Data center building present, NO NPDES permit on record");
    if (scored!.rpa) flags.push("Resource Protection Area (RPA) buffer");
    if (scored!.d_stream_ft != null && scored!.d_stream_ft < 300) flags.push(`${scored!.d_stream_ft.toFixed(0)} ft from nearest stream`);
    if (scored!.dam) flags.push(`Dam-break inundation zone: ${scored!.dam_haz_class ?? "unclassified"}`);
    if (scored!.watershed_name) flags.push(`Watershed: ${scored!.watershed_name}${scored!.n_dc_in_watershed ? ` (${scored!.n_dc_in_watershed} DCs sharing basin)` : ""}`);
    return {
      address: displayAddress,
      acres: scored!.acres,
      zoning: scored!.zoning,
      watershed: scored!.watershed_name,
      hasNpdes: scored!.has_npdes,
      inDcBuilding: scored!.in_dc_building,
      inDcCampus: scored!.in_dc_campus,
      nDcBuildings: scored!.n_dc_buildings,
      waterLegibility: legibility,
      dataDepth: scored!.conviction,
      subScores: {
        WatershedVulnerability: synthesized!.subScores.watershedVulnerability,
        FacilityWaterContext: synthesized!.subScores.facilityWaterContext,
        DroughtExposure: synthesized!.subScores.droughtExposure,
        DisclosureLegibility: synthesized!.subScores.disclosureLegibility,
        CommunityObsDensity: synthesized!.subScores.communityObsDensity,
        MunicipalSupplyHeadroom: synthesized!.subScores.municipalSupplyHeadroom,
        StormwaterBurden: synthesized!.subScores.stormwaterBurden,
      },
      flags,
    };
  }

  return (
    <aside className="flex h-full w-[440px] shrink-0 flex-col border-l border-neutral-800 bg-neutral-950">
      {/* Header */}
      <div className="border-b border-neutral-800 px-5 py-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="text-[11px] text-amber-400">
              {scored.GPIN}
            </div>
            <h3 className="mt-0.5 text-sm font-medium text-neutral-100 leading-tight">
              {displayName}
            </h3>
            <div className="mt-1 text-[11px] text-neutral-400">
              {displayAddress}
            </div>
          </div>
          <div className="flex items-center gap-0.5">
            <button
              onClick={() => {
                if (pinnedParcelId === scored.GPIN) setPinnedParcel(null);
                else setPinnedParcel(scored.GPIN);
              }}
              className={`rounded p-1 hover:bg-neutral-800 ${
                pinnedParcelId === scored.GPIN ? "text-amber-400" : "text-neutral-500 hover:text-neutral-200"
              }`}
              title={pinnedParcelId === scored.GPIN ? "Unpin (currently pinned for compare)" : "Pin for compare"}
              aria-label={pinnedParcelId === scored.GPIN ? "Unpin parcel" : "Pin parcel for compare"}
            >
              <Pin className="h-4 w-4" />
            </button>
            <button
              onClick={() => {
                setSelectedParcel(null);
                closeRightPanel();
              }}
              className="rounded p-1 text-neutral-500 hover:bg-neutral-800 hover:text-neutral-200"
              aria-label="Close panel"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="mt-3 flex flex-wrap gap-1.5 text-[10px]">
          <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-neutral-300">
            {scored.acres < 1 ? scored.acres.toFixed(2) : scored.acres.toFixed(1)} ac
          </span>
          {scored.zoning && (
            <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-neutral-300">
              {scored.zoning}
            </span>
          )}
          {scored.watershed_name && (
            <span className="rounded bg-sky-900/60 px-1.5 py-0.5 text-sky-200">
              {scored.watershed_name} watershed
            </span>
          )}
          {scored.in_dc_building === 1 && (
            <span
              className="rounded bg-red-900/80 px-1.5 py-0.5 text-red-100 font-medium"
              title="A data center is built on this parcel."
            >
              {(scored.n_dc_buildings ?? 1) > 1 ? (
                <>{scored.n_dc_buildings} built DCs on site{scored.dc_building_name ? ` (${scored.dc_building_name} + ${(scored.n_dc_buildings ?? 1) - 1} more)` : ""}</>
              ) : (
                <>Built DC on site{scored.dc_building_name ? `: ${scored.dc_building_name}` : ""}</>
              )}
            </span>
          )}
          {scored.in_dc_campus === 1 && scored.in_dc_building !== 1 && (
            <span className="rounded bg-amber-900/60 px-1.5 py-0.5 text-amber-200">
              Planned DC campus{scored.dc_campus_name ? `: ${scored.dc_campus_name}` : ""}
            </span>
          )}
          {scored.has_npdes === 1 ? (
            <span className="rounded bg-emerald-900/60 px-1.5 py-0.5 text-emerald-200" title="Holds an NPDES water discharge permit — rare (4 in all of VA)">
              NPDES permit on file
            </span>
          ) : scored.in_dc_building === 1 ? (
            <span className="rounded bg-red-900/60 px-1.5 py-0.5 text-red-200" title="No NPDES water discharge permit on record for this data center">
              No NPDES coverage
            </span>
          ) : null}
          {scored.has_deq_permit === 1 && (
            <span className="rounded bg-emerald-900/60 px-1.5 py-0.5 text-emerald-200">
              DEQ permit on file
            </span>
          )}
          {scored.rpa === 1 && (
            <span className="rounded bg-teal-900/60 px-1.5 py-0.5 text-teal-200">
              RPA buffer
            </span>
          )}
          {scored.wetland === 1 && (
            <span className="rounded bg-teal-900/60 px-1.5 py-0.5 text-teal-200">
              Wetlands
            </span>
          )}
          {scored.dam === 1 && (
            <span className={`rounded px-1.5 py-0.5 ${scored.dam_haz_class === "HIGH" ? "bg-red-900/60 text-red-200" : "bg-amber-900/60 text-amber-200"}`}>
              Dam-break {scored.dam_haz_class ?? "zone"}
            </span>
          )}
          {scored.d_stream_ft != null && scored.d_stream_ft < 300 && (
            <span className="rounded bg-amber-900/60 px-1.5 py-0.5 text-amber-200">
              {scored.d_stream_ft.toFixed(0)}ft from stream
            </span>
          )}
          {scored.is_state_land === 1 && (
            <span className="rounded bg-red-900/60 px-1.5 py-0.5 text-red-200">
              State land
            </span>
          )}
          {scored.in_tidal_flow_path === 1 && (
            <span className="rounded bg-cyan-900/60 px-1.5 py-0.5 text-cyan-200">
              Tidal flow path
            </span>
          )}
          {(scored.n_wqp_stations_1mi ?? 0) > 0 && (
            <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-neutral-300">
              {scored.n_wqp_stations_1mi} WQP station{(scored.n_wqp_stations_1mi ?? 0) > 1 ? "s" : ""} / 1mi
            </span>
          )}
          {(scored.sw_facilities ?? 0) > 0 && (
            <span className="rounded bg-amber-900/60 px-1.5 py-0.5 text-amber-200" title="Detention/retention basins inside the parcel">
              {scored.sw_facilities} SW basin{(scored.sw_facilities ?? 0) > 1 ? "s" : ""}
            </span>
          )}
        </div>

        {/* Drought / power context */}
        {(scored.phdi != null || scored.pw_water_pct_peak != null) && (
          <div className="mt-3 flex flex-wrap gap-3 text-[10px] text-neutral-500">
            {scored.phdi != null && (
              <span>
                PHDI (drought):{" "}
                <span className={`${scored.phdi < -3 ? "text-red-400" : "text-neutral-200"}`}>
                  {scored.phdi.toFixed(2)}
                </span>
              </span>
            )}
            {scored.pw_water_pct_peak != null && (
              <span>
                DC share of PW Water peak demand:{" "}
                <span className="text-neutral-200">{scored.pw_water_pct_peak}%</span>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Scroll area */}
      <div className="flex-1 overflow-y-auto">
        {/* Compare card */}
        {isComparing && pinnedParcel && pinnedLegibility != null && (
          <div className="border-b-2 border-amber-700/40 bg-amber-950/15 px-4 py-3">
            <div className="flex items-center justify-between mb-2">
              <div className="text-[9px] uppercase tracking-wider text-amber-400/80 flex items-center gap-1.5">
                <Pin className="h-3 w-3" />
                <span>Comparing · pinned</span>
              </div>
              <div className="flex items-center gap-0.5">
                <button
                  onClick={() => {
                    const currentSel = selectedParcelId;
                    setSelectedParcel(pinnedParcel.GPIN);
                    if (currentSel) setPinnedParcel(currentSel);
                  }}
                  className="rounded p-1 text-neutral-500 hover:bg-neutral-800 hover:text-amber-400"
                  title="Swap with selected"
                  aria-label="Swap pinned and selected"
                >
                  <ArrowLeftRight className="h-3 w-3" />
                </button>
                <button
                  onClick={() => setPinnedParcel(null)}
                  className="rounded p-1 text-neutral-500 hover:bg-neutral-800 hover:text-neutral-200"
                  title="Unpin"
                  aria-label="Unpin"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            </div>
            <div className="grid grid-cols-[1fr_auto_1fr] gap-x-2 text-[11px] items-center">
              <div className="min-w-0">
                <div className="text-[10px] text-amber-400 truncate">{pinnedParcel.GPIN}</div>
                <div className="text-neutral-400 text-[10px] truncate">
                  {pinnedParcel.zoning ?? "—"} · {pinnedParcel.acres < 1 ? pinnedParcel.acres.toFixed(2) : pinnedParcel.acres.toFixed(1)} ac
                </div>
                <div className={`mt-1 text-2xl font-light ${legibilityColor(pinnedLegibility)}`}>
                  {pinnedLegibility}
                </div>
              </div>
              <div className="text-center text-neutral-600 text-[10px]">vs</div>
              <div className="min-w-0 text-right">
                <div className="text-[10px] text-amber-400 truncate">{scored.GPIN}</div>
                <div className="text-neutral-400 text-[10px] truncate">
                  {scored.zoning ?? "—"} · {scored.acres < 1 ? scored.acres.toFixed(2) : scored.acres.toFixed(1)} ac
                </div>
                <div className={`mt-1 text-2xl font-light ${legibilityColor(legibility)}`}>
                  {legibility}
                </div>
              </div>
            </div>
            <div className="mt-2 text-center text-[10px]">
              <span className="text-neutral-500">Δ Water Legibility: </span>
              <span className={legibility - pinnedLegibility > 0 ? "text-green-400" : legibility - pinnedLegibility < 0 ? "text-red-400" : "text-neutral-400"}>
                {legibility - pinnedLegibility > 0 ? "+" : ""}{legibility - pinnedLegibility}
              </span>
            </div>
          </div>
        )}

        {/* AI verdict */}
        {(verdict.text || verdict.isLoading) && !verdict.error && (
          <div className="border-b border-neutral-800 bg-gradient-to-b from-amber-950/20 to-transparent px-5 py-3">
            <div className="flex items-center gap-1.5 text-[9px] uppercase tracking-wider text-amber-400/80 mb-1.5">
              <span className={verdict.isLoading ? "animate-pulse" : ""}>◆</span>
              <span>Water Atlas verdict</span>
              {verdict.isLoading && <span className="text-neutral-600 normal-case tracking-normal">streaming…</span>}
            </div>
            <div className="text-[12px] leading-snug text-neutral-100">
              {verdict.text || "…"}
            </div>
          </div>
        )}

        {/* Water Legibility Score — TOP */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
            Water Legibility Score
          </div>
          <div className="flex items-baseline gap-3">
            <div className={`text-5xl font-light ${legibilityColor(legibility)} transition-colors duration-300`}>
              {legibility}
            </div>
            <div className="text-sm text-neutral-500">/ 100</div>
            <div className="ml-auto text-[10px] text-neutral-500 text-right relative">
              <button
                onClick={() => setDataDepthOpen((v) => !v)}
                className="block text-right hover:opacity-80 transition-opacity cursor-pointer"
                title="Click to see which data layers contributed and which are missing"
              >
                <div className="underline decoration-dotted decoration-neutral-600 underline-offset-2">
                  Data Depth
                </div>
                <div className="text-amber-400 text-base">{scored.conviction}</div>
              </button>
              {dataDepthOpen && (
                <div
                  className="absolute right-0 top-12 z-20 w-[360px] max-h-[440px] overflow-y-auto rounded-lg border border-neutral-700 bg-neutral-950 shadow-2xl p-3 text-left"
                  onMouseLeave={() => setDataDepthOpen(false)}
                >
                  {(() => {
                    const rows = convictionGaps(scored);
                    const { present, missing, totalContributed, totalPossible } = convictionSummary(rows);
                    const byGroup = rows.reduce<Record<string, typeof rows>>((acc, r) => {
                      (acc[r.group] ??= []).push(r);
                      return acc;
                    }, {});
                    return (
                      <>
                        <div className="flex items-baseline justify-between mb-2">
                          <div className="text-[10px] uppercase tracking-wider text-neutral-500">
                            Data depth audit
                          </div>
                          <button onClick={() => setDataDepthOpen(false)} className="text-neutral-500 hover:text-neutral-200 text-[10px]">
                            close
                          </button>
                        </div>
                        <div className="text-[11px] text-neutral-400 mb-3 leading-relaxed">
                          <span className="text-amber-300">{present.length}</span>
                          {" of "}
                          <span className="text-neutral-300">{rows.length}</span>
                          {" data layers contributed signal — "}
                          <span className="text-amber-300">{totalContributed}</span>
                          {" of "}
                          <span className="text-neutral-300">{totalPossible}</span>
                          {" possible points. "}
                          {missing.length === 0 ? (
                            <span className="text-green-400">Full coverage.</span>
                          ) : (
                            <span className="text-neutral-500">
                              {missing.length} layer{missing.length === 1 ? "" : "s"} returned no data for this parcel.
                            </span>
                          )}
                        </div>
                        {Object.entries(byGroup).map(([group, gRows]) => (
                          <div key={group} className="mb-2.5">
                            <div className="text-[9px] uppercase tracking-wider text-neutral-600 mb-1">
                              {group}
                            </div>
                            <div className="space-y-0.5">
                              {gRows.map((r) => (
                                <div key={r.label} className="flex items-start gap-1.5 text-[11px]">
                                  {r.present ? (
                                    <Check className="h-3 w-3 mt-0.5 text-green-500 shrink-0" />
                                  ) : (
                                    <Minus className="h-3 w-3 mt-0.5 text-neutral-600 shrink-0" />
                                  )}
                                  <div className="flex-1 min-w-0">
                                    <span className={r.present ? "text-neutral-200" : "text-neutral-600 line-through"}>
                                      {r.label}
                                    </span>
                                    {r.present && r.detail && (
                                      <span className="text-neutral-500 ml-1.5">— {r.detail}</span>
                                    )}
                                  </div>
                                  <span className={`shrink-0 text-[10px] ${r.present ? "text-amber-400/80" : "text-neutral-700"}`}>
                                    +{r.points}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        ))}
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          </div>
          <div className="mt-3 relative">
            <div className="h-1.5 rounded bg-neutral-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-red-500 via-yellow-500 to-green-500"
                style={{ width: `${legibility}%`, transition: "width 300ms ease" }}
              />
            </div>
          </div>
          <div className="mt-2 text-[11px] text-neutral-500 leading-relaxed">
            Weighted composite of 7 sub-scores measuring how much is knowable
            about this parcel&apos;s water relationship to data-center infrastructure
            — observable, inferable, or unresolved.
          </div>
        </div>

        {/* Sub-scores */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-3">
            Sub-scores
          </div>
          <div className="space-y-2">
            {ORDERED_SUBSCORES.map((k) => {
              const score = synthesized.subScores[k];
              const q = qualityBadge(synthesized.quality[k]);
              const weight = (subScoreWeights[k] * 100).toFixed(0);
              return (
                <div key={k} className="flex items-center gap-3 text-xs">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="text-neutral-200">
                        {SUBSCORE_LABELS[k]}
                      </span>
                      <span className={`rounded border px-1 text-[9px] uppercase tracking-wider ${q.className}`}>
                        {q.label}
                      </span>
                      <span className="text-[10px] text-neutral-600">
                        w={weight}%
                      </span>
                    </div>
                    <div className="mt-1 h-1 rounded bg-neutral-800 overflow-hidden">
                      <div
                        className={`h-full transition-all duration-300 ${
                          score >= 80 ? "bg-green-500" : score >= 60 ? "bg-yellow-500" : score >= 40 ? "bg-orange-500" : "bg-red-500"
                        }`}
                        style={{ width: `${score}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex items-baseline gap-1.5">
                    <span className={`text-sm tabular-nums transition-colors duration-300 ${legibilityColor(score)}`}>
                      {score}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Facility Dossier — only for parcels matched to a specific DC
            building or campus record. Every field here is either directly
            observed (a permit case number, a year built, a matched staff
            report) or explicitly marked "not on record" — this is the
            evidence-graph view of the facility, not a water-use estimate. */}
        {(buildingProfile || campusProfile) && (
          <div className="border-b border-neutral-800 px-5 py-4">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-3">
              Facility Dossier
            </div>
            {buildingProfile && (
              <div className="mb-3">
                <div className="text-neutral-200 text-sm font-medium">
                  {buildingProfile.name ?? "Unnamed building"}
                </div>
                <div className="mt-1.5 space-y-1">
                  <EvidenceRow label="Status" value={buildingProfile.status} />
                  <EvidenceRow label="Year built" value={buildingProfile.year_built} />
                  <EvidenceRow label="Building permit" value={buildingProfile.permit_case ? `${buildingProfile.permit_case} (${buildingProfile.permit_status})` : null} />
                </div>
              </div>
            )}
            {campusProfile && (
              <div className="mb-3">
                <div className="text-neutral-200 text-sm font-medium">
                  {campusProfile.name ?? "Unnamed campus"}
                </div>
                <div className="mt-1.5 space-y-1">
                  <EvidenceRow label="Rezoning case" value={campusProfile.case_number} />
                  <EvidenceRow label="Zoning district" value={campusProfile.zoning_district} />
                  <EvidenceRow
                    label="Remaining entitled GFA"
                    value={campusProfile.remaining_gfa_sqft ? `${campusProfile.remaining_gfa_sqft.toLocaleString()} sq ft` : null}
                  />
                  <EvidenceRow
                    label="Campus footprint"
                    value={campusProfile.gis_acreage ? `${campusProfile.gis_acreage.toFixed(0)} ac across ${campusProfile.n_parcels} parcels` : null}
                  />
                  <EvidenceRow
                    label="Built buildings on site"
                    value={campusProfile.built_buildings_on_site.length > 0 ? campusProfile.built_buildings_on_site.join(", ") : null}
                  />
                </div>
              </div>
            )}
            {allCases.length > 0 && (
              <div className="mt-2">
                <div className="text-[9px] uppercase tracking-wider text-neutral-600 mb-1.5">
                  Matched case history ({allCases.length})
                </div>
                <div className="space-y-1.5">
                  {allCases.slice(0, 6).map((c, i) => (
                    <CaseHistoryRow key={i} c={c} />
                  ))}
                </div>
              </div>
            )}
            {(() => {
              const swf = buildingProfile?.scope_water_footprint ?? campusProfile?.scope_water_footprint;
              if (!swf) return null;
              const { power, scope1_onsite_cooling: s1, scope2_electricity: s2, scope3_embodied: s3 } = swf;
              return (
                <div className="mt-3 rounded border border-neutral-800 bg-neutral-950/60 px-3 py-2.5">
                  <div className="text-[9px] uppercase tracking-wider text-neutral-400 mb-1.5">
                    Scope 1/2/3 Water Footprint (est.)
                  </div>
                  <div className="text-lg font-light text-neutral-100">
                    {swf.total_mgd_range[0].toFixed(2)}–{swf.total_mgd_range[1].toFixed(2)}{" "}
                    <span className="text-xs text-neutral-500 font-normal">MGD total</span>
                  </div>
                  <div className="text-[10px] text-neutral-600 mt-0.5 mb-2.5 leading-relaxed">
                    {swf.total_note}
                  </div>

                  <div className="text-[10px] text-neutral-500 mb-2.5 leading-relaxed border-b border-neutral-800 pb-2">
                    <span className="text-neutral-400">Power basis ({power.basis.replace("_", " ")}): </span>
                    {power.mw_range[0]}–{power.mw_range[1]} MW.{" "}{power.note}
                    {power.hv_plausibility && (
                      <div className="mt-1 text-amber-400/80">{power.hv_plausibility}</div>
                    )}
                  </div>

                  <ScopeRow
                    label="Scope 1 — on-site cooling"
                    tone="amber"
                    mgdRange={s1.mgd_range}
                    detail={`WUE envelope ${s1.wue_range_l_per_kwh[0]}–${s1.wue_range_l_per_kwh[1]} L/kWh — full published range; cooling technology undisclosed per facility.`}
                    methodology={s1.methodology}
                    climatePointMgd={s1.climate_weighted_point_mgd}
                    climateNote={s1.climate_note}
                  />
                  <ScopeRow
                    label="Scope 2 — electricity-driven"
                    tone="sky"
                    mgdRange={s2.mgd_range}
                    detail={`Dominion generation-mix-blended consumption factor: ${s2.blended_consumption_gal_per_mwh} gal/MWh at ${s2.assumed_utilization * 100}% assumed utilization.`}
                    methodology={s2.methodology}
                  />
                  <ScopeRow
                    label="Scope 3 — embodied / supply-chain"
                    tone="violet"
                    mgdRange={s3.mgd_range}
                    detail={`Proportional anchor: ${(s3.proportional_range[0] * 100).toFixed(0)}–${(s3.proportional_range[1] * 100).toFixed(0)}% of Scope 1+2. ${s3.note}`}
                    methodology={s3.methodology}
                  />
                </div>
              );
            })()}
            <div className="mt-2 text-[10px] text-neutral-600 italic leading-relaxed">
              Sourced from PWC Data Center Buildings/Projects, Use Permits, BZA,
              and Planning Pending Cases. Fields marked &quot;not on record&quot;
              are genuinely absent from public disclosure, not just unretrieved.
            </div>
          </div>
        )}

        {/* Policy corpus provenance */}
        {policy && (
          <div className="border-b border-neutral-800 px-5 py-4">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-3">
              Policy Context
            </div>
            <div className="text-[11px] text-neutral-400 leading-relaxed">
              <div className="mb-1">
                <span className="text-neutral-600">Policy corpus:</span>{" "}
                <span className="text-neutral-200">
                  {policy.docs.length} docs · {policy.docs.reduce((s, d) => s + d.length, 0).toLocaleString()} chars
                </span>
              </div>
            </div>
          </div>
        )}

        {/* LLM Q&A */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2 flex items-center gap-1.5">
            <MessageSquare className="h-3 w-3" />
            Ask about this parcel
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (!qaQuestion.trim() || qa.isLoading) return;
              qa.generate({
                gpin: scored.GPIN,
                mode: "qa",
                parcelContext: buildParcelContext(),
                question: qaQuestion.trim(),
              });
            }}
            className="flex gap-1.5"
          >
            <input
              type="text"
              value={qaQuestion}
              onChange={(e) => setQaQuestion(e.target.value)}
              placeholder="e.g. Is this parcel's water use disclosed anywhere?"
              className="flex-1 rounded border border-neutral-700 bg-neutral-900 px-3 py-2 text-xs text-neutral-100 placeholder:text-neutral-600 focus:outline-none focus:border-amber-500"
              disabled={qa.isLoading}
            />
            <button
              type="submit"
              disabled={!qaQuestion.trim() || qa.isLoading}
              className="rounded bg-amber-500 px-3 py-2 text-[11px] font-medium text-neutral-950 hover:bg-amber-400 disabled:bg-neutral-700 disabled:text-neutral-500"
            >
              {qa.isLoading ? <Loader2 className="h-3 w-3 animate-spin" /> : "Ask"}
            </button>
          </form>
          {qa.error && (
            <div className="mt-2 text-[10px] text-red-400 bg-red-950/40 border border-red-900/50 px-2 py-1 rounded leading-snug">
              {qa.error}
            </div>
          )}
          {(qa.text || qa.isLoading) && (
            <div className="mt-3 rounded border border-neutral-800 bg-neutral-900/40 px-3 py-2">
              <CitedText text={qa.text} citations={qa.citations} />
              {qa.isLoading && <Loader2 className="h-3 w-3 animate-spin text-amber-400 mt-2" />}
            </div>
          )}
        </div>

        {/* Diligence Memo */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500">
              Water Legibility Memo
            </div>
            <button
              onClick={() =>
                memo.generate({
                  gpin: scored.GPIN,
                  mode: "memo",
                  parcelContext: buildParcelContext(),
                })
              }
              disabled={memo.isLoading}
              title="Generate Memo — press G"
              className="rounded bg-amber-500 px-2 py-1 text-[10px] font-medium text-neutral-950 hover:bg-amber-400 disabled:bg-neutral-700 disabled:text-neutral-500 flex items-center gap-1"
            >
              {memo.isLoading ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  {memo.text ? "Regenerate" : "Generate Memo"}
                  <kbd className="ml-0.5 text-[8px] px-1 border border-neutral-900/40 text-neutral-900/60">G</kbd>
                </>
              )}
            </button>
          </div>
          {memo.error && (
            <div className="text-[10px] text-red-400 bg-red-950/40 border border-red-900/50 px-2 py-1 rounded leading-snug mb-2">
              {memo.error}
            </div>
          )}
          {memo.text ? (
            <CitedText text={memo.text} citations={memo.citations} />
          ) : !memo.isLoading ? (
            <p className="text-[11px] text-neutral-500 italic leading-relaxed">
              Click <em>Generate Memo</em> to produce a water-legibility
              narrative (observable / inferable / unresolved). Generated by
              Llama 3.3 70B (Groq) over the PWC water-policy corpus.
            </p>
          ) : (
            <div className="text-[11px] text-amber-400 flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              Retrieving relevant policy chunks + streaming from Groq...
            </div>
          )}
        </div>

        {/* Counter-memo */}
        <div className="border-b border-neutral-800 px-5 py-4 bg-red-950/10">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[10px] uppercase tracking-wider text-red-400">
              What&apos;s Unresolved
            </div>
            <button
              onClick={() =>
                counter.generate({
                  gpin: scored.GPIN,
                  mode: "counter",
                  parcelContext: buildParcelContext(),
                  sensitivity: sensitivityThresholds,
                })
              }
              disabled={counter.isLoading}
              className="rounded border border-red-700 px-2 py-1 text-[10px] font-medium text-red-300 hover:bg-red-900/40 disabled:opacity-50 flex items-center gap-1"
            >
              {counter.isLoading ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin" />
                  Generating...
                </>
              ) : counter.text ? (
                "Regenerate"
              ) : (
                "Generate"
              )}
            </button>
          </div>
          {counter.error && (
            <div className="text-[10px] text-red-400 bg-red-950/40 border border-red-900/50 px-2 py-1 rounded leading-snug mb-2">
              {counter.error}
            </div>
          )}
          {counter.text ? (
            <CitedText text={counter.text} citations={counter.citations} />
          ) : !counter.isLoading ? (
            <p className="text-[11px] text-neutral-500 italic leading-relaxed">
              What remains dark about this parcel&apos;s water relationship to
              data-center infrastructure? Same RAG corpus, adversarial framing.
            </p>
          ) : (
            <div className="text-[11px] text-red-300 flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              Stress-testing this parcel against the policy corpus...
            </div>
          )}
        </div>

        {/* Sensitivity */}
        {sensitivityThresholds.length > 0 && (
          <div className="border-b border-neutral-800 bg-amber-950/10 px-5 py-4">
            <div className="flex items-baseline justify-between mb-2">
              <div className="text-[10px] uppercase tracking-wider text-amber-300/90">
                What would have to be true
              </div>
              <div className="text-[9px] text-neutral-500 italic">
                target ≥ 60 per sub-score
              </div>
            </div>
            <div className="space-y-2 text-[11px]">
              {sensitivityThresholds.map((t) => {
                const plausibilityClass =
                  t.plausibility === "high"
                    ? "border-green-700/60 text-green-300"
                    : t.plausibility === "medium"
                      ? "border-amber-700/60 text-amber-300"
                      : "border-red-700/60 text-red-300";
                return (
                  <div key={t.id} className="rounded border border-neutral-800 bg-neutral-900/60 px-3 py-2">
                    <div className="flex items-baseline justify-between gap-2 mb-1">
                      <div className="flex items-baseline gap-1.5 min-w-0">
                        <span className="text-amber-400 text-[10px] shrink-0">[{t.id}]</span>
                        <span className="text-neutral-200 text-[11px] truncate">
                          {SUBSCORE_LABELS[t.subScore]}
                        </span>
                        <span className="text-neutral-600 text-[10px] shrink-0">
                          {t.currentScore} → ≥{t.targetScore}
                        </span>
                      </div>
                      <span className={`rounded border px-1 text-[9px] uppercase tracking-wider shrink-0 ${plausibilityClass}`}>
                        {t.plausibility}
                      </span>
                    </div>
                    <div className="text-neutral-300 leading-relaxed text-[11px]">
                      <span className="text-neutral-500">{t.lever}: </span>
                      <span className="text-neutral-200">{t.currentValue}</span>
                      <span className="text-neutral-600 mx-1">→</span>
                      <span className="text-amber-300">{t.targetValue}</span>
                      {t.byYear && <span className="text-neutral-500"> by {t.byYear}</span>}
                    </div>
                    <div className="text-neutral-400 leading-snug text-[10px] mt-1">
                      {t.rationale}
                    </div>
                    <div className="text-neutral-600 text-[10px] mt-1">
                      ← {t.source}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Source documentation */}
        <div className="px-5 py-4">
          <div className="flex items-baseline justify-between mb-2">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500">
              Source documentation
            </div>
            <div className="text-[9px] text-neutral-600 italic">
              ranked by impact on this parcel
            </div>
          </div>
          {topSources.length === 0 ? (
            <div className="text-[11px] text-neutral-600 italic">
              No high-impact sources detected for this parcel.
            </div>
          ) : (
            <div className="space-y-1.5 text-[11px]">
              {topSources.map((rs) => (
                <a
                  key={rs.source.key + "-" + rs.contribution}
                  href={rs.source.href}
                  target={rs.source.external ? "_blank" : "_self"}
                  rel={rs.source.external ? "noopener noreferrer" : undefined}
                  className="group block rounded border border-neutral-800 bg-neutral-900/40 px-2.5 py-1.5 hover:border-amber-700 hover:bg-neutral-900/80 transition"
                  title={rs.source.description ?? rs.contribution}
                >
                  <div className="flex items-start gap-1.5">
                    <ExternalLink className="h-3 w-3 mt-0.5 shrink-0 text-neutral-500 group-hover:text-amber-400" />
                    <div className="flex-1 min-w-0">
                      <div className="text-neutral-200 group-hover:text-amber-300 leading-tight">
                        {rs.source.title}
                      </div>
                      <div className="text-[10px] text-neutral-500 mt-0.5 leading-snug">
                        <span className={rs.direction === "+" ? "text-green-500" : "text-red-400"}>
                          {rs.direction === "+" ? "▲" : "▼"} {rs.impact}pt
                        </span>{" "}
                        · {rs.contribution}
                      </div>
                    </div>
                  </div>
                </a>
              ))}
            </div>
          )}
        </div>
      </div>
    </aside>
  );
}
