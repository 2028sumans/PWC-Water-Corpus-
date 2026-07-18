"use client";

/**
 * Facility dossier panel. Every number here traces to exactly one place:
 * indirect_water_footprint.py's Scope 1/2/3 estimator, as baked into
 * facility_profiles.json by build_facility_profiles.py. There is no parcel
 * legibility score, no sub-score weighting, no separate readiness index —
 * the methodology module IS the scoring system, and this panel is a direct
 * rendering of its output plus the evidence-checklist facility dossier.
 */
import { useEffect, useMemo, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { usePolicyIndex } from "@/lib/usePolicyIndex";
import { useMemoStream, type MemoRequest } from "@/lib/useMemoStream";
import {
  useFacilityProfiles,
  findBuildingByGpin,
  findCampusByGpin,
  type FacilityCaseRecord,
  type FacilityWaterContext,
  type ScopeWaterFootprint,
} from "@/lib/useFacilityProfiles";
import { CitedText } from "./CitedText";
import { X, ExternalLink, MessageSquare, Loader2, Check, Minus, FileText } from "lucide-react";

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

function footprintColor(hiMgd: number): string {
  if (hiMgd >= 2) return "text-red-400";
  if (hiMgd >= 0.75) return "text-orange-400";
  if (hiMgd >= 0.2) return "text-yellow-400";
  return "text-green-400";
}

// Deterministic "what would narrow this estimate" list — every line traces
// to a specific, real uncertainty axis in indirect_water_footprint.py, not
// an LLM guess. This is the Scope 1/2/3 analog of the old sub-score
// sensitivity panel: same UI slot, methodology-grounded content.
interface UncertaintyDriver {
  id: string;
  title: string;
  detail: string;
  plausibility: "high" | "medium" | "low";
}

function uncertaintyDrivers(swf: ScopeWaterFootprint): UncertaintyDriver[] {
  const rows: UncertaintyDriver[] = [];
  rows.push({
    id: "U1",
    title: "Cooling technology undisclosed",
    detail:
      "Scope 1 uses the full published WUE envelope (0.0–2.4 L/kWh, dry/closed-loop through open-evaporative) because no PWC dataset discloses which cooling technology this facility uses. A disclosed cooling type would collapse this to a single-technology range.",
    plausibility: "low",
  });
  if (swf.power.basis === "gfa_only") {
    rows.push({
      id: "U2",
      title: "Power estimate has only one independent source",
      detail: `${swf.power.note} A matching interconnection.fyi operator listing would provide a second, cross-checkable estimate.`,
      plausibility: "medium",
    });
  } else if (swf.power.basis === "operator_only") {
    rows.push({
      id: "U2",
      title: "Power estimate has only one independent source",
      detail: `${swf.power.note} A disclosed GFA figure would provide a second, cross-checkable estimate.`,
      plausibility: "medium",
    });
  } else if (swf.power.basis === "disagreement") {
    rows.push({
      id: "U2",
      title: "GFA-based and operator-match power estimates disagree",
      detail: swf.power.note,
      plausibility: "high",
    });
  } else if (swf.power.basis === "intersection") {
    rows.push({
      id: "U2",
      title: "Power estimate already narrowed by two agreeing methods",
      detail: swf.power.note,
      plausibility: "low",
    });
  }
  if (swf.power.hv_plausibility) {
    rows.push({
      id: "U3",
      title: "High-voltage transmission proximity flag",
      detail: swf.power.hv_plausibility,
      plausibility: "medium",
    });
  }
  rows.push({
    id: "U4",
    title: "Scope 3 is a proportional anchor, not a physical estimate",
    detail: `${swf.scope3_embodied.methodology} ${swf.scope3_embodied.note}`,
    plausibility: "low",
  });
  return rows;
}

const METHODOLOGY_SOURCES: Array<{ title: string; note: string }> = [
  { title: "Mytton, D. — \"Data centre water consumption\" (npj Clean Water, 2021)", note: "WUE definition and full published envelope" },
  { title: "Privette et al. — AGU Advances (2026)", note: "WUE envelope; Scope 3 proportional-anchor ratio and embodied-water outlier disclosure" },
  { title: "The Green Grid — WUE metric", note: "Water Usage Effectiveness definition (L water / kWh IT energy)" },
  { title: "Uptime Institute / LBNL data center benchmarking surveys", note: "IT power density benchmarks (100–200 W/sqft standard; 250–450 W/sqft modern AI-class)" },
  { title: "Open Compute Project — \"Diablo\" rack power spec", note: "50–135 kW/rack GPU racks, up to 1 MW/rack roadmap" },
  { title: "LBNL — \"Queued Up\" (2025)", note: "AI-driven step-change in PWC-area interconnection requests" },
  { title: "Hyperscaler fleet PUE disclosures (Google, Microsoft, Meta, 2023–2025) vs. Uptime Institute global survey", note: "PUE ranges (1.08–1.15 modern hyperscale; 1.20–1.60 standard/enterprise)" },
  { title: "Macknick, J. et al. — NREL/TP-6A20-50900 (2011)", note: "Generation-technology water consumption factors" },
  { title: "EIA \"Today in Energy\" / Virginia generation-mix reporting; Dominion Energy Virginia 2025 generation mix", note: "Blended grid consumption intensity" },
  { title: "interconnection.fyi", note: "Public data-center interconnection-queue MW ranges (accessed 2026)" },
];

export function RightPanel() {
  const selectedGpin = useViraStore((s) => s.selectedGpin);
  const closeRightPanel = useViraStore((s) => s.closeRightPanel);
  const setSelectedGpin = useViraStore((s) => s.setSelectedGpin);
  const policy = usePolicyIndex();
  useFacilityProfiles();

  const buildingProfile = selectedGpin ? findBuildingByGpin(selectedGpin) : undefined;
  const campusProfile = selectedGpin ? findCampusByGpin(selectedGpin) : undefined;
  const facility = buildingProfile ?? campusProfile;
  const swf = facility?.scope_water_footprint ?? null;
  const waterContext: FacilityWaterContext | null = facility?.water_context ?? null;

  const allCases = [
    ...(buildingProfile?.use_permits ?? []),
    ...(buildingProfile?.bza_cases ?? []),
    ...(buildingProfile?.pending_cases ?? []),
    ...(campusProfile?.use_permits ?? []),
    ...(campusProfile?.bza_cases ?? []),
    ...(campusProfile?.pending_cases ?? []),
  ];

  const drivers = useMemo(() => (swf ? uncertaintyDrivers(swf) : []), [swf]);

  // LLM streaming state — one stream instance per output.
  const memo = useMemoStream();
  const counter = useMemoStream();
  const qa = useMemoStream();
  const verdict = useMemoStream();
  const [qaQuestion, setQaQuestion] = useState("");
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  useEffect(() => {
    memo.reset();
    counter.reset();
    qa.reset();
    verdict.reset();
    setQaQuestion("");
    setMethodologyOpen(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedGpin]);

  function buildFacilityContext(): MemoRequest["facilityContext"] | null {
    if (!facility || !swf) return null;
    const flags: string[] = [];
    if (waterContext?.has_npdes) flags.push("Holds an NPDES water discharge permit (rare)");
    else flags.push("No NPDES water discharge permit on record — the norm, not the exception, for evaporative-cooling water use");
    if (waterContext?.watershed_name) flags.push(`Watershed: ${waterContext.watershed_name}${waterContext.n_dc_in_watershed ? ` (${waterContext.n_dc_in_watershed} DCs sharing basin)` : ""}`);
    if (waterContext?.rpa) flags.push("Resource Protection Area (RPA) buffer");
    if (waterContext?.d_stream_ft != null && waterContext.d_stream_ft < 300) flags.push(`${waterContext.d_stream_ft.toFixed(0)} ft from nearest stream`);
    if (swf.power.hv_plausibility) flags.push(swf.power.hv_plausibility);
    return {
      name: facility.name ?? "Unnamed facility",
      kind: facility.kind,
      status: buildingProfile?.status ?? null,
      yearBuilt: buildingProfile?.year_built ?? null,
      gfaSqft: buildingProfile?.gfa_sqft ?? null,
      powerMwRange: swf.power.mw_range,
      powerBasis: swf.power.basis,
      scope1MgdRange: swf.scope1_onsite_cooling.mgd_range,
      scope2MgdRange: swf.scope2_electricity.mgd_range,
      scope3MgdRange: swf.scope3_embodied.mgd_range,
      totalMgdRange: swf.total_mgd_range,
      flags,
    };
  }

  // Auto-fire the one-sentence AI verdict the moment a facility is selected.
  useEffect(() => {
    if (!facility || !swf) return;
    const ctx = buildFacilityContext();
    if (!ctx) return;
    const id = window.setTimeout(() => {
      if (verdict.isLoading || verdict.text) return;
      verdict.generate({ facilityId: selectedGpin!, mode: "verdict", facilityContext: ctx });
    }, 60);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedGpin]);

  // Listen for the global "g" keyboard shortcut (dispatched by AppShell).
  useEffect(() => {
    const onGenerate = () => {
      if (!facility || !swf || memo.isLoading) return;
      const ctx = buildFacilityContext();
      if (!ctx) return;
      memo.generate({ facilityId: selectedGpin!, mode: "memo", facilityContext: ctx });
    };
    window.addEventListener("vira:generate-memo", onGenerate);
    return () => window.removeEventListener("vira:generate-memo", onGenerate);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  });

  if (!facility) return null;

  const displayName = facility.name ?? (facility.kind === "building" ? "Unnamed building" : "Unnamed campus");

  return (
    <aside className="flex h-full w-[440px] shrink-0 flex-col border-l border-neutral-800 bg-neutral-950">
      {/* Header */}
      <div className="border-b border-neutral-800 px-5 py-3">
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="text-[11px] text-amber-400">{selectedGpin}</div>
            <h3 className="mt-0.5 text-sm font-medium text-neutral-100 leading-tight">{displayName}</h3>
            <div className="mt-1 text-[11px] text-neutral-400 capitalize">
              {facility.kind}
              {buildingProfile?.status ? ` · ${buildingProfile.status}` : ""}
            </div>
          </div>
          <button
            onClick={() => {
              setSelectedGpin(null);
              closeRightPanel();
            }}
            className="rounded p-1 text-neutral-500 hover:bg-neutral-800 hover:text-neutral-200"
            aria-label="Close panel"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Water & site context badges */}
        <div className="mt-3 flex flex-wrap gap-1.5 text-[10px]">
          {waterContext?.watershed_name && (
            <span className="rounded bg-sky-900/60 px-1.5 py-0.5 text-sky-200">
              {waterContext.watershed_name} watershed
            </span>
          )}
          {waterContext?.has_npdes === 1 ? (
            <span className="rounded bg-emerald-900/60 px-1.5 py-0.5 text-emerald-200" title="Holds an NPDES water discharge permit — rare">
              NPDES permit on file
            </span>
          ) : (
            <span className="rounded bg-red-900/60 px-1.5 py-0.5 text-red-200" title="No NPDES water discharge permit on record">
              No NPDES coverage
            </span>
          )}
          {waterContext?.has_deq_permit === 1 && (
            <span className="rounded bg-emerald-900/60 px-1.5 py-0.5 text-emerald-200">DEQ permit on file</span>
          )}
          {waterContext?.rpa === 1 && <span className="rounded bg-teal-900/60 px-1.5 py-0.5 text-teal-200">RPA buffer</span>}
          {waterContext?.wetland === 1 && <span className="rounded bg-teal-900/60 px-1.5 py-0.5 text-teal-200">Wetlands</span>}
          {waterContext?.dam === 1 && (
            <span className={`rounded px-1.5 py-0.5 ${waterContext.dam_haz_class === "HIGH" ? "bg-red-900/60 text-red-200" : "bg-amber-900/60 text-amber-200"}`}>
              Dam-break {waterContext.dam_haz_class ?? "zone"}
            </span>
          )}
          {waterContext?.d_stream_ft != null && waterContext.d_stream_ft < 300 && (
            <span className="rounded bg-amber-900/60 px-1.5 py-0.5 text-amber-200">
              {waterContext.d_stream_ft.toFixed(0)}ft from stream
            </span>
          )}
          {waterContext?.in_tidal_flow_path === 1 && (
            <span className="rounded bg-cyan-900/60 px-1.5 py-0.5 text-cyan-200">Tidal flow path</span>
          )}
          {(waterContext?.n_wqp_stations_1mi ?? 0) > 0 && (
            <span className="rounded bg-neutral-800 px-1.5 py-0.5 text-neutral-300">
              {waterContext!.n_wqp_stations_1mi} WQP station{(waterContext!.n_wqp_stations_1mi ?? 0) > 1 ? "s" : ""} / 1mi
            </span>
          )}
          {(waterContext?.sw_facilities ?? 0) > 0 && (
            <span className="rounded bg-amber-900/60 px-1.5 py-0.5 text-amber-200" title="Detention/retention basins on-site">
              {waterContext!.sw_facilities} SW basin{(waterContext!.sw_facilities ?? 0) > 1 ? "s" : ""}
            </span>
          )}
        </div>
      </div>

      {/* Scroll area */}
      <div className="flex-1 overflow-y-auto">
        {/* AI verdict */}
        {(verdict.text || verdict.isLoading) && !verdict.error && (
          <div className="border-b border-neutral-800 bg-gradient-to-b from-amber-950/20 to-transparent px-5 py-3">
            <div className="flex items-center gap-1.5 text-[9px] uppercase tracking-wider text-amber-400/80 mb-1.5">
              <span className={verdict.isLoading ? "animate-pulse" : ""}>◆</span>
              <span>Water Atlas verdict</span>
              {verdict.isLoading && <span className="text-neutral-600 normal-case tracking-normal">streaming…</span>}
            </div>
            <div className="text-[12px] leading-snug text-neutral-100">{verdict.text || "…"}</div>
          </div>
        )}

        {!swf ? (
          <div className="border-b border-neutral-800 px-5 py-4 text-[11px] text-neutral-500 italic leading-relaxed">
            No Scope 1/2/3 estimate could be produced for this facility — neither
            a GFA figure nor an interconnection.fyi operator match exists to
            derive a power estimate from.
          </div>
        ) : (
          <>
            {/* Hero: Total Scope 1+2+3 footprint */}
            <div className="border-b border-neutral-800 px-5 py-4">
              <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
                Est. Scope 1+2+3 Water Footprint
              </div>
              <div className="flex items-baseline gap-3">
                <div className={`text-4xl font-light ${footprintColor(swf.total_mgd_range[1])} transition-colors duration-300`}>
                  {swf.total_mgd_range[0].toFixed(2)}–{swf.total_mgd_range[1].toFixed(2)}
                </div>
                <div className="text-sm text-neutral-500">MGD</div>
                <div className="ml-auto text-[10px] text-neutral-500 text-right relative">
                  <button
                    onClick={() => setMethodologyOpen((v) => !v)}
                    className="block text-right hover:opacity-80 transition-opacity cursor-pointer"
                    title="Click to see how this estimate was derived"
                  >
                    <div className="underline decoration-dotted decoration-neutral-600 underline-offset-2">
                      Methodology
                    </div>
                    <div className="text-amber-400 text-[11px] uppercase tracking-wider">{swf.power.basis.replace("_", " ")}</div>
                  </button>
                  {methodologyOpen && (
                    <div
                      className="absolute right-0 top-12 z-20 w-[360px] max-h-[440px] overflow-y-auto rounded-lg border border-neutral-700 bg-neutral-950 shadow-2xl p-3 text-left"
                      onMouseLeave={() => setMethodologyOpen(false)}
                    >
                      <div className="flex items-baseline justify-between mb-2">
                        <div className="text-[10px] uppercase tracking-wider text-neutral-500">Power estimate audit</div>
                        <button onClick={() => setMethodologyOpen(false)} className="text-neutral-500 hover:text-neutral-200 text-[10px]">
                          close
                        </button>
                      </div>
                      <div className="space-y-1.5">
                        <EvidenceRow
                          label="GFA-based estimate"
                          value={swf.power.gfa_estimate ? `${swf.power.gfa_estimate.gfa_sqft.toLocaleString()} sqft (${swf.power.gfa_field_used}) → ${swf.power.gfa_estimate.facility_mw_range[0]}–${swf.power.gfa_estimate.facility_mw_range[1]} MW` : null}
                        />
                        <EvidenceRow
                          label="interconnection.fyi operator match"
                          value={swf.power.operator_match ? `${swf.power.operator_match.operator} → ${swf.power.operator_match.mw_range[0]}–${swf.power.operator_match.mw_range[1]} MW` : null}
                        />
                        <EvidenceRow
                          label="Climate-weighted seasonal point"
                          value={swf.scope1_onsite_cooling.climate_weighted_point_mgd != null ? `${swf.scope1_onsite_cooling.climate_weighted_point_mgd.toFixed(3)} MGD` : null}
                        />
                        <EvidenceRow label="Cooling technology disclosed" value={null} />
                        <EvidenceRow label="HV transmission plausibility check" value={swf.power.hv_plausibility} />
                      </div>
                      <div className="mt-2.5 pt-2.5 border-t border-neutral-800 text-[10px] text-neutral-500 leading-relaxed">
                        {swf.power.note}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-2 text-[11px] text-neutral-500 leading-relaxed">{swf.total_note}</div>
            </div>

            {/* Scope breakdown */}
            <div className="border-b border-neutral-800 px-5 py-4">
              <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-1">Scope Breakdown</div>
              <div className="text-[10px] text-neutral-500 leading-relaxed mb-1">
                Power basis ({swf.power.basis.replace("_", " ")}): {swf.power.mw_range[0]}–{swf.power.mw_range[1]} MW.
              </div>
              <ScopeRow
                label="Scope 1 — on-site cooling"
                tone="amber"
                mgdRange={swf.scope1_onsite_cooling.mgd_range}
                detail={`WUE envelope ${swf.scope1_onsite_cooling.wue_range_l_per_kwh[0]}–${swf.scope1_onsite_cooling.wue_range_l_per_kwh[1]} L/kWh — full published range; cooling technology undisclosed per facility.`}
                methodology={swf.scope1_onsite_cooling.methodology}
                climatePointMgd={swf.scope1_onsite_cooling.climate_weighted_point_mgd}
                climateNote={swf.scope1_onsite_cooling.climate_note}
              />
              <ScopeRow
                label="Scope 2 — electricity-driven"
                tone="sky"
                mgdRange={swf.scope2_electricity.mgd_range}
                detail={`Dominion generation-mix-blended consumption factor: ${swf.scope2_electricity.blended_consumption_gal_per_mwh} gal/MWh at ${swf.scope2_electricity.assumed_utilization * 100}% assumed utilization.`}
                methodology={swf.scope2_electricity.methodology}
              />
              <ScopeRow
                label="Scope 3 — embodied / supply-chain"
                tone="violet"
                mgdRange={swf.scope3_embodied.mgd_range}
                detail={`Proportional anchor: ${(swf.scope3_embodied.proportional_range[0] * 100).toFixed(0)}–${(swf.scope3_embodied.proportional_range[1] * 100).toFixed(0)}% of Scope 1+2. ${swf.scope3_embodied.note}`}
                methodology={swf.scope3_embodied.methodology}
              />
            </div>
          </>
        )}

        {/* Facility Dossier */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-3">Facility Dossier</div>
          {buildingProfile && (
            <div className="mb-3 space-y-1">
              <EvidenceRow label="Status" value={buildingProfile.status} />
              <EvidenceRow label="Year built" value={buildingProfile.year_built} />
              <EvidenceRow label="Gross floor area" value={buildingProfile.gfa_sqft ? `${buildingProfile.gfa_sqft.toLocaleString()} sqft (${buildingProfile.gfa_field_used})` : null} />
              <EvidenceRow label="Building permit" value={buildingProfile.permit_case ? `${buildingProfile.permit_case} (${buildingProfile.permit_status})` : null} />
            </div>
          )}
          {campusProfile && (
            <div className="mb-3 space-y-1">
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
        </div>

        {/* Policy corpus provenance */}
        {policy && (
          <div className="border-b border-neutral-800 px-5 py-4">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-3">Policy Context</div>
            <div className="text-[11px] text-neutral-400 leading-relaxed">
              <span className="text-neutral-600">Policy corpus:</span>{" "}
              <span className="text-neutral-200">
                {policy.docs.length} docs · {policy.docs.reduce((s, d) => s + d.length, 0).toLocaleString()} chars
              </span>
            </div>
          </div>
        )}

        {/* LLM Q&A */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2 flex items-center gap-1.5">
            <MessageSquare className="h-3 w-3" />
            Ask about this facility
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const ctx = buildFacilityContext();
              if (!qaQuestion.trim() || qa.isLoading || !ctx) return;
              qa.generate({ facilityId: selectedGpin!, mode: "qa", facilityContext: ctx, question: qaQuestion.trim() });
            }}
            className="flex gap-1.5"
          >
            <input
              type="text"
              value={qaQuestion}
              onChange={(e) => setQaQuestion(e.target.value)}
              placeholder="e.g. Why is Scope 1 reported as a range instead of a number?"
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

        {/* Water Footprint Memo */}
        <div className="border-b border-neutral-800 px-5 py-4">
          <div className="flex items-center justify-between mb-2">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500">Water Footprint Memo</div>
            <button
              onClick={() => {
                const ctx = buildFacilityContext();
                if (ctx) memo.generate({ facilityId: selectedGpin!, mode: "memo", facilityContext: ctx });
              }}
              disabled={memo.isLoading || !swf}
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
              Click <em>Generate Memo</em> to produce a Scope 1/2/3 water-footprint
              narrative grounded in the methodology above. Generated by Llama 3.3
              70B (Groq) over the PWC water-policy corpus.
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
            <div className="text-[10px] uppercase tracking-wider text-red-400">What&apos;s Unresolved</div>
            <button
              onClick={() => {
                const ctx = buildFacilityContext();
                if (ctx) counter.generate({ facilityId: selectedGpin!, mode: "counter", facilityContext: ctx, uncertaintyDrivers: drivers });
              }}
              disabled={counter.isLoading || !swf}
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
              What remains dark about this facility&apos;s actual water footprint?
              Same RAG corpus, adversarial framing.
            </p>
          ) : (
            <div className="text-[11px] text-red-300 flex items-center gap-2">
              <Loader2 className="h-3 w-3 animate-spin" />
              Stress-testing this estimate against the policy corpus...
            </div>
          )}
        </div>

        {/* What would narrow this estimate */}
        {drivers.length > 0 && (
          <div className="border-b border-neutral-800 bg-amber-950/10 px-5 py-4">
            <div className="text-[10px] uppercase tracking-wider text-amber-300/90 mb-2">
              What Would Narrow This Estimate
            </div>
            <div className="space-y-2 text-[11px]">
              {drivers.map((d) => {
                const plausibilityClass =
                  d.plausibility === "high"
                    ? "border-green-700/60 text-green-300"
                    : d.plausibility === "medium"
                      ? "border-amber-700/60 text-amber-300"
                      : "border-red-700/60 text-red-300";
                return (
                  <div key={d.id} className="rounded border border-neutral-800 bg-neutral-900/60 px-3 py-2">
                    <div className="flex items-baseline justify-between gap-2 mb-1">
                      <div className="flex items-baseline gap-1.5 min-w-0">
                        <span className="text-amber-400 text-[10px] shrink-0">[{d.id}]</span>
                        <span className="text-neutral-200 text-[11px] truncate">{d.title}</span>
                      </div>
                      <span className={`rounded border px-1 text-[9px] uppercase tracking-wider shrink-0 ${plausibilityClass}`}>
                        {d.plausibility} likelihood of resolution
                      </span>
                    </div>
                    <div className="text-neutral-400 leading-snug text-[10px]">{d.detail}</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Methodology sources */}
        <div className="px-5 py-4">
          <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">Methodology Sources</div>
          <div className="space-y-1.5 text-[11px]">
            {METHODOLOGY_SOURCES.map((s) => (
              <div key={s.title} className="rounded border border-neutral-800 bg-neutral-900/40 px-2.5 py-1.5">
                <div className="flex items-start gap-1.5">
                  <ExternalLink className="h-3 w-3 mt-0.5 shrink-0 text-neutral-500" />
                  <div className="flex-1 min-w-0">
                    <div className="text-neutral-200 leading-tight">{s.title}</div>
                    <div className="text-[10px] text-neutral-500 mt-0.5 leading-snug">{s.note}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
}
