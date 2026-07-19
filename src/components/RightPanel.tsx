"use client";

/**
 * Facility dossier panel. Every number here traces to exactly one place:
 * indirect_water_footprint.py's Scope 1/2/3 estimator, as baked into
 * facility_profiles.json by build_facility_profiles.py. There is no parcel
 * legibility score, no sub-score weighting, no separate readiness index —
 * the methodology module IS the scoring system, and this panel is a direct
 * rendering of its output plus the evidence-checklist facility dossier.
 */
import { useEffect, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { usePolicyIndex } from "@/lib/usePolicyIndex";
import { useMemoStream, type MemoRequest } from "@/lib/useMemoStream";
import {
  useFacilityProfiles,
  findBuildingByGpin,
  findCampusByGpin,
  type BuildingProfile,
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
  central,
  detail,
  methodology,
  climatePointMgd,
  climateNote,
}: {
  label: string;
  tone: "amber" | "sky" | "violet";
  mgdRange: [number, number];
  central: number;
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
          {central.toFixed(3)}{" "}
          <span className="text-[9px] text-neutral-500 font-normal">MGD central</span>
        </span>
      </div>
      <div className="text-right text-[9px] text-neutral-500">
        range {mgdRange[0].toFixed(3)}–{mgdRange[1].toFixed(3)}
      </div>
      <div className="mt-1 text-[10px] text-neutral-500 leading-relaxed">{detail}</div>
      <div className="mt-1 text-[9px] text-neutral-600 leading-relaxed italic">{methodology}</div>
      {climatePointMgd != null && (
        <div className={`mt-1.5 pt-1.5 border-t ${c.border} text-[10px] ${c.text} leading-relaxed`}>
          Summer peak-day direct draw: <span className="font-medium">{climatePointMgd.toFixed(3)} MGD</span>
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

// Thresholds calibrated to JLARC's measured per-building figures: 0.666 MGD
// was the single largest data center building in Virginia (2023), 0.137 MGD
// put a building in the top 11 statewide, 0.018 MGD is an average office.
function footprintColor(centralMgd: number): string {
  if (centralMgd >= 0.666) return "text-red-400";
  if (centralMgd >= 0.137) return "text-orange-400";
  if (centralMgd >= 0.018) return "text-yellow-400";
  return "text-green-400";
}

/**
 * The disclosure audit. Every item is derived deterministically from this
 * facility's own record + the fields indirect_water_footprint.py emits —
 * NOT from an LLM. The gaps in data-center water disclosure are structural
 * and already fully known to the pipeline; making an analyst wait on a RAG
 * round-trip to re-derive them (and risk a loose paraphrase of numbers we
 * computed exactly) would be strictly worse than just stating them.
 *
 * severity:
 *   structural — dark by regulatory design; no public path to resolving it today
 *   high       — materially widens THIS facility's estimate
 *   moderate   — bounded or second-order effect
 */
interface UnresolvedItem {
  id: string;
  title: string;
  severity: "structural" | "high" | "moderate";
  onRecord: string;
  gap: string;
  impact: string | null;
  wouldResolve: string;
}

function unresolvedItems(
  swf: ScopeWaterFootprint,
  wc: FacilityWaterContext | null,
  building: BuildingProfile | undefined,
): UnresolvedItem[] {
  const items: UnresolvedItem[] = [];
  const s1 = swf.scope1_onsite_cooling;
  const s2 = swf.scope2_electricity;
  const pw = swf.power;

  // ── U1. The structural gap: nobody meters or reports this ──────────────
  const dmr = wc?.dmr_flow_mgd;
  items.push({
    id: "U1",
    title: "Actual metered water withdrawal and consumption",
    severity: "structural",
    onRecord:
      wc?.has_npdes === 1
        ? `NPDES discharge permit on file${dmr != null ? `, reporting ${dmr} MGD of discharge flow` : " (no DMR flow figure reported)"}${wc?.has_deq_permit === 1 ? "; DEQ permit also on record" : ""}.`
        : `No NPDES water discharge permit on record${wc?.has_deq_permit === 1 ? ", though a DEQ permit is on file" : ", and no DEQ permit on file"}.`,
    gap: "NPDES regulates what a facility discharges to surface water — not what it consumes. Data centers lose water primarily to evaporation from municipal supply, which produces no permitted discharge and triggers no reporting duty. Even a permit-holding facility does not report the consumption figure this page estimates. The gap is structural rather than a matter of operators declining to answer: the county's own land-use review has no field for water quantity. Every data center staff report contains a Potable Water Plan Analysis, and across all of them it evaluates only whether public water is available and who pays to connect — never how much will be used. The Environment Plan Analysis treats water solely as a quality and habitat question (Resource Protection Areas, stream disturbance, buffers). A facility can be approved, conditioned and built without any public document stating its water demand.",
    // The old text here claimed this model "reproduces [PWC's 0.42 MGD] to
    // within 7% in aggregate". That was the circular validation: ICPRB derived
    // the 309 gal/MW/day intensity BY DIVIDING that same 0.42 MGD by its own
    // power estimate, so the comparison cancels the water figure and tests the
    // power spine instead. Withdrawn — see METHODOLOGY.md 6.1.
    impact: `No per-facility measurement exists to check the ${swf.total_mgd_central.toFixed(3)} MGD central estimate against. Prince William Water reports only a service-area total (0.42 MGD across all data center customers in 2023) — a wider boundary than the county, and not an independent check, since the intensity this model uses was itself derived from that figure.`,
    wouldResolve:
      "A facility-level water-use disclosure requirement, or large-customer withdrawal reporting from Prince William Water.",
  });

  // ── U2. Cooling technology — still the widest Scope 1 driver, unless
  //        an operator commitment or a binding permit condition has
  //        narrowed it. A published operator WUE is used only as a
  //        qualitative signal of which technology CLASS the facility likely
  //        uses (narrowed onto ICPRB's own PWC-calibrated scale below) — a
  //        global fleet-average WUE and ICPRB's local WUP are measured under
  //        different accounting boundaries, so the two numbers are not
  //        interchangeable and the WUE is never substituted in directly.
  if (s1.basis === "operator_closed_loop_commitment") {
    items.push({
      id: "U2",
      title: "Cooling technology — narrowed by a public operator commitment",
      severity: "moderate",
      onRecord: `${s1.narrowed_by} That commitment narrows this facility onto ICPRB's own air-cooled tier (${s1.wup_reference_tiers.air_cooled} gal/MW/day) rather than the full ${s1.wup_reference_tiers.air_cooled}–${s1.wup_reference_tiers.fully_water_cooled} regional span.`,
      gap: "This is a fleet-wide commitment, not a measurement at this address, and the operator's own headline WUE figure is measured on a different accounting boundary than the ICPRB scale this tool is calibrated against — so it is used only as a signal of technology class, not substituted in as a number.",
      impact: `Narrows Scope 1 to ${s1.mgd_range[0].toFixed(3)}–${s1.mgd_range[1].toFixed(3)} MGD — materially tighter than the unnarrowed default.`,
      wouldResolve: "A site-level water-use disclosure for this specific building, on the same accounting basis ICPRB used to calibrate the local scale.",
    });
  } else if (s1.basis === "disclosed_cooling") {
    items.push({
      id: "U2",
      title: "Cooling technology — constrained by a binding permit condition",
      severity: "moderate",
      onRecord: s1.narrowed_by ?? "A permit condition constrains cooling technology at this site.",
      gap: "The condition constrains the technology class but does not report actual consumption, and compliance documentation is filed at occupancy rather than published as an ongoing metered figure.",
      impact: `Pins Scope 1 near the air-cooled tier (${s1.wup_reference_tiers.air_cooled} gal/MW/day), giving ${s1.mgd_range[0].toFixed(3)}–${s1.mgd_range[1].toFixed(3)} MGD.`,
      wouldResolve: "Published post-occupancy compliance documentation confirming which cooling system was actually installed.",
    });
  } else {
    items.push({
      id: "U2",
      title: "Cooling technology (dry/closed-loop vs. evaporative)",
      severity: "high",
      onRecord: `No PWC dataset — building permit, use permit, or rezoning case — discloses this facility's cooling system type, and this operator publishes no WUE figure.${building?.permit_case ? ` Building permit ${building.permit_case} is on record but carries no mechanical-system detail in the GIS attributes.` : ""}`,
      gap: `Scope 1 therefore spans the full measured technology range for the region: ${s1.wup_reference_tiers.air_cooled} gal/MW/day for air-cooled/closed-loop up to ${s1.wup_reference_tiers.fully_water_cooled} for fully evaporative (ICPRB 2025). The central estimate uses Prince William Water's observed fleet average of ${s1.wup_reference_tiers.pwc_observed} gal/MW/day.`,
      impact: `Leaves Scope 1 at ${s1.mgd_range[0].toFixed(3)}–${s1.mgd_range[1].toFixed(3)} MGD around a ${s1.mgd_central.toFixed(3)} MGD central estimate — an unavoidable ~10x technology span.`,
      wouldResolve:
        "An operator WUE disclosure for this site (as Amazon and Microsoft publish fleet-wide), or mechanical-system detail in the building permit — either collapses this to a single technology band.",
    });
  }

  // ── U3. Power draw — permit-measured, or floor-area derived ─
  const xc = pw.operator_cross_check;
  const isPermitPower = pw.basis === "permit_generator_capacity";
  const densityUsed = pw.density_sqft_per_mw_used ?? pw.sqft_per_effective_mw;
  items.push({
    id: "U3",
    title: isPermitPower
      ? "Facility power is measured from a permit, not floor area"
      : "Facility power draw is inferred from floor area, not metered",
    severity: isPermitPower ? "moderate" : xc && !xc.agrees ? "high" : "moderate",
    onRecord: isPermitPower
      ? `${swf.power.note}`
      : `${pw.gfa_sqft.toLocaleString()} sqft (${pw.gfa_quality ?? "unknown"} source: ${pw.gfa_field_used ?? "n/a"}) ÷ ${densityUsed.toLocaleString()} sqft per effective MW = ${pw.effective_it_mw_central} MW effective IT load. ${pw.density_source ?? "Density is ICPRB's fleet average."}${xc ? ` ${xc.note}` : ""}`,
    gap: isPermitPower
      ? "Power is apportioned from the site's permitted backup-generator capacity by floor-area share; the split assumes generators are sized in proportion to each building's floor area."
      : pw.gfa_quality === "proffer_split"
        ? "This building has no assessed or permitted floor area of its own — only a site-wide proffered entitlement, divided evenly across the buildings sharing it. The split is even, but real buildings on a site are not equally sized."
        : "A density band is not a site measurement. Actual rack density and mechanical layout vary building to building, and no metered load figure is published for any individual facility.",
    impact: isPermitPower
      ? "Power for this building rests on measured generator capacity, so it carries no density uncertainty — only the floor-area apportionment among buildings on the same permit."
      : `Propagates proportionally into both Scope 1 and Scope 2. Density is the single largest driver of the range (~52% of the county-wide swing).`,
    wouldResolve:
      "The per-facility backup-generator capacity in the VADEQ air permit for this site, or a utility load filing — either replaces the floor-area inference with a facility-specific figure.",
  });

  // ── U4. PUE — disclosed at fleet level by some operators, inferred otherwise ──
  items.push({
    id: "U4",
    title: "Actual PUE (energy overhead above IT load)",
    // Still "moderate" even when disclosed: a published fleet average is much
    // better evidence than a vintage guess, but it remains a global figure
    // rather than a measurement at this address.
    severity: "moderate",
    onRecord: s2.pue_capped_by_proffer
      ? `PUE bounded above by a binding proffer commitment (${s2.pue_range[1]}), with ${s2.pue_range[0]} as the modern-build floor.`
      : s2.pue_class === "operator_disclosed"
        ? `${s2.pue_source}. Applied as ${s2.pue_range[0]}–${s2.pue_range[1]} to allow for site-versus-fleet variation.`
        : s2.pue_class === "new_build"
          ? `Not yet built, so there is no build year — PUE is taken as current design practice (${s2.pue_range[0]}–${s2.pue_range[1]}), between hyperscaler best practice and Uptime Institute's 1.54 industry average.`
          : `PUE inferred from a ${building?.year_built ?? s2.pue_class} build vintage (${s2.pue_class} class, ${s2.pue_range[0]}–${s2.pue_range[1]}).`,
    gap:
      s2.pue_class === "operator_disclosed"
        ? "The disclosed figure is a GLOBAL FLEET average across every climate the operator runs in, not a measurement at this address. Northern Virginia's cooling load is above that fleet mean."
        : "No PWC facility discloses a measured PUE. It is a benchmark assumption keyed to build status or year, not a site measurement.",
    impact: `Scales Scope 2 linearly across a ${(s2.pue_range[1] / s2.pue_range[0]).toFixed(2)}x band.`,
    wouldResolve: "Operator PUE disclosure at site rather than fleet granularity, or a proffered PUE cap made enforceable and reported.",
  });

  // ── U5. Scope 2 attribution — average, not marginal ────────────────────
  items.push({
    id: "U5",
    title: "Which generators actually serve this load (Scope 2 attribution)",
    severity: "structural",
    onRecord: `Scope 2 uses Dominion's system-average generation mix, blended to ${s2.blended_consumption_gal_per_mwh} gal/MWh (NREL Macknick et al. 2011).`,
    gap: "A new large load is served at the margin, not by the system average — but no published dataset gives marginal water intensity for the PJM/Dominion system (NREL's Cambium marginal dataset is carbon-only). Using the average is the defensible choice, and it is stated as such rather than presented as attribution.",
    impact: "If this load is served disproportionately by water-cooled thermal generation, real Scope 2 sits above the range shown; if by renewables, below it.",
    wouldResolve: "A published marginal water-intensity dataset for PJM, or utility disclosure of the generation actually dispatched against this interconnection.",
  });

  // ── U6. Scope 3 — proportional anchor, not physical ────────────────────
  items.push({
    id: "U6",
    title: "Facility-specific embodied / supply-chain water (Scope 3)",
    severity: "structural",
    onRecord: `Modeled as ${(swf.scope3_embodied.proportional_range[0] * 100).toFixed(0)}–${(swf.scope3_embodied.proportional_range[1] * 100).toFixed(0)}% of the Scope 1+2 operational total → ${swf.scope3_embodied.mgd_range[0].toFixed(3)}–${swf.scope3_embodied.mgd_range[1].toFixed(3)} MGD.`,
    gap: "This is a proportional anchor from corporate disclosure ratios, not a physical estimate. The semiconductor fabs, server assembly, and construction supply chains behind this building are entirely outside Virginia and outside every PWC dataset.",
    impact: "At least one hyperscaler has disclosed embodied water above 99% of its corporate total under a different accounting boundary — evidence the 5–15% anchor used here is a floor, not a ceiling.",
    wouldResolve: "Facility-level embodied-water accounting from the operator, or fab-level water disclosure traceable to this site's hardware.",
  });

  // ── U7. Monitoring density — would anyone notice? ──────────────────────
  const wqp = wc?.n_wqp_stations_1mi ?? 0;
  const deqMon = wc?.n_deq_monitoring_1mi ?? 0;
  if (wqp + deqMon === 0) {
    items.push({
      id: "U7",
      title: "No independent water monitoring within one mile",
      severity: "high",
      onRecord: "No WQP stations and no DEQ monitoring sites within a 1-mile radius of this facility.",
      gap: `Even if this facility's actual draw or discharge departed sharply from the modeled envelope, there is no nearby independent instrumentation that would register it${wc?.watershed_name ? ` in the ${wc.watershed_name} watershed` : ""}.`,
      impact: "Removes the one external check that could otherwise contradict a modeled figure.",
      wouldResolve: "Placement of a WQP or DEQ monitoring station within the facility's immediate watershed.",
    });
  } else {
    items.push({
      id: "U7",
      title: "Monitoring coverage exists but is not facility-attributable",
      severity: "moderate",
      onRecord: `${wqp} WQP station${wqp === 1 ? "" : "s"} and ${deqMon} DEQ monitoring site${deqMon === 1 ? "" : "s"} within 1 mile.`,
      gap: "Ambient monitoring measures the receiving water, not this facility's contribution to it. Nearby stations cannot separate this site's signal from every other draw and discharge in the basin.",
      impact: "Provides a watershed-level sanity check only — it cannot confirm or refute this facility's specific footprint.",
      wouldResolve: "Point-of-service metering at the facility, rather than ambient monitoring downstream of it.",
    });
  }

  return items;
}

const SEVERITY_STYLES: Record<UnresolvedItem["severity"], { label: string; className: string }> = {
  structural: { label: "structural gap", className: "border-red-700/60 text-red-300" },
  high: { label: "widens this estimate", className: "border-amber-700/60 text-amber-300" },
  moderate: { label: "bounded effect", className: "border-neutral-600 text-neutral-400" },
};

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

  // Cheap pure derivation over already-loaded data — no memo needed (and the
  // inputs come from a module-level cache, which React Compiler can't treat
  // as a reactive dependency anyway).
  const unresolved = swf ? unresolvedItems(swf, waterContext, buildingProfile) : [];

  // LLM streaming state — one stream instance per output. All of this state
  // is per-facility; AppShell keys this component on the selected GPIN so a
  // new selection remounts it fresh, rather than resetting via an effect.
  const memo = useMemoStream();
  const qa = useMemoStream();
  const verdict = useMemoStream();
  const [qaQuestion, setQaQuestion] = useState("");
  const [methodologyOpen, setMethodologyOpen] = useState(false);

  function buildFacilityContext(): MemoRequest["facilityContext"] | null {
    if (!facility || !swf) return null;
    const flags: string[] = [];
    if (waterContext?.has_npdes) flags.push("Holds an NPDES water discharge permit (rare)");
    else flags.push("No NPDES water discharge permit on record — the norm, not the exception, for evaporative-cooling water use");
    if (waterContext?.watershed_name) flags.push(`Watershed: ${waterContext.watershed_name}${waterContext.n_dc_in_watershed ? ` (${waterContext.n_dc_in_watershed} DCs sharing basin)` : ""}`);
    if (waterContext?.rpa) flags.push("Resource Protection Area (RPA) buffer");
    if (waterContext?.d_stream_ft != null && waterContext.d_stream_ft < 300) flags.push(`${waterContext.d_stream_ft.toFixed(0)} ft from nearest stream`);
    if (swf.power.hv_plausibility) flags.push(swf.power.hv_plausibility);
    if (swf.scope1_onsite_cooling.narrowed_by) flags.push(`Scope 1 narrowed: ${swf.scope1_onsite_cooling.narrowed_by}`);
    flags.push(swf.benchmark.verdict);
    return {
      name: facility.name ?? "Unnamed facility",
      kind: facility.kind,
      status: buildingProfile?.status ?? null,
      yearBuilt: buildingProfile?.year_built ?? null,
      gfaSqft: buildingProfile?.gfa_sqft ?? null,
      effectiveMw: swf.power.effective_it_mw_central,
      scope1Central: swf.scope1_onsite_cooling.mgd_central,
      scope1Range: swf.scope1_onsite_cooling.mgd_range,
      scope2Central: swf.scope2_electricity.mgd_central,
      scope3Central: swf.scope3_embodied.mgd_central,
      totalCentral: swf.total_mgd_central,
      totalRange: swf.total_mgd_range,
      peakDayMgd: swf.scope1_onsite_cooling.peak_day_mgd,
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
      memo.generate({ facilityId: selectedGpin!, mode: "memo", facilityContext: ctx, unresolved });
    };
    window.addEventListener("vira:generate-memo", onGenerate);
    return () => window.removeEventListener("vira:generate-memo", onGenerate);
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
            No Scope 1/2/3 estimate could be produced for this facility — no
            floor-area figure exists to derive an effective power load from.
          </div>
        ) : (
          <>
            {/* Hero: central estimate, with the envelope beneath it */}
            <div className="border-b border-neutral-800 px-5 py-4">
              <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
                Est. Scope 1+2+3 Water Footprint
              </div>
              <div className="flex items-baseline gap-3">
                <div className={`text-4xl font-light ${footprintColor(swf.total_mgd_central)} transition-colors duration-300`}>
                  {swf.total_mgd_central.toFixed(3)}
                </div>
                <div className="text-sm text-neutral-500">MGD</div>
                <div
                  className="text-[10px] text-neutral-500 leading-tight"
                  title={swf.total_basis_note}
                >
                  delivered
                  <br />
                  <span className="text-neutral-600">
                    {swf.total_consumptive_mgd_central.toFixed(3)} consumptive
                  </span>
                </div>
                <div className="ml-auto text-[10px] text-neutral-500 text-right relative">
                  <button
                    onClick={() => setMethodologyOpen((v) => !v)}
                    className="block text-right hover:opacity-80 transition-opacity cursor-pointer"
                    title="Click to see how this estimate was derived"
                  >
                    <div className="underline decoration-dotted decoration-neutral-600 underline-offset-2">
                      Methodology
                    </div>
                    <div className="text-amber-400 text-[11px] uppercase tracking-wider">
                      {swf.scope1_onsite_cooling.basis === "technology_envelope" ? "ICPRB default" : "narrowed"}
                    </div>
                  </button>
                  {methodologyOpen && (
                    <div
                      className="absolute right-0 top-12 z-20 w-[380px] max-h-[460px] overflow-y-auto rounded-lg border border-neutral-700 bg-neutral-950 shadow-2xl p-3 text-left"
                      onMouseLeave={() => setMethodologyOpen(false)}
                    >
                      <div className="flex items-baseline justify-between mb-2">
                        <div className="text-[10px] uppercase tracking-wider text-neutral-500">Derivation audit</div>
                        <button onClick={() => setMethodologyOpen(false)} className="text-neutral-500 hover:text-neutral-200 text-[10px]">
                          close
                        </button>
                      </div>
                      <div className="space-y-1.5">
                        <EvidenceRow
                          label="Floor area"
                          value={`${swf.power.gfa_sqft.toLocaleString()} sqft (${swf.power.gfa_quality ?? "unknown"}, ${swf.power.gfa_field_used ?? "n/a"})`}
                        />
                        <EvidenceRow
                          label="Effective IT load"
                          value={
                            swf.power.basis === "permit_generator_capacity" && swf.power.permit
                              ? `${swf.power.effective_it_mw_central} MW from VADEQ permit ${swf.power.permit.registration_no}`
                              : `${swf.power.effective_it_mw_central} MW @ ${swf.power.sqft_per_effective_mw.toLocaleString()} sqft/MW`
                          }
                        />
                        <EvidenceRow
                          label="Cooling intensity used"
                          value={`${swf.scope1_onsite_cooling.wup_gal_per_mw_day.central} gal/MW/day (${swf.scope1_onsite_cooling.basis.replace(/_/g, " ")})`}
                        />
                        <EvidenceRow label="Narrowed by a disclosure" value={swf.scope1_onsite_cooling.narrowed_by} />
                        <EvidenceRow
                          label="Operator interconnection cross-check"
                          value={swf.power.operator_cross_check ? `${swf.power.operator_cross_check.operator}: ${swf.power.operator_cross_check.agrees ? "consistent" : "outside range"}` : null}
                        />
                        <EvidenceRow label="HV transmission plausibility" value={swf.power.hv_plausibility} />
                      </div>
                      <div className="mt-2.5 pt-2.5 border-t border-neutral-800 text-[10px] text-neutral-500 leading-relaxed">
                        {swf.power.note}
                      </div>
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-1.5 text-[11px] text-neutral-400">
                Range <span className="tabular-nums">{swf.total_mgd_range[0].toFixed(3)}–{swf.total_mgd_range[1].toFixed(3)}</span> MGD
                <span className="text-neutral-600"> · </span>
                summer peak-day direct draw{" "}
                <span className="text-amber-300 tabular-nums">{swf.scope1_onsite_cooling.peak_day_mgd.toFixed(3)}</span> MGD
              </div>

              {/* Reality check against JLARC's measured per-building figures */}
              <div
                className={`mt-2.5 rounded border px-2.5 py-1.5 text-[10px] leading-relaxed ${
                  swf.benchmark.flag === "exceeds_largest_measured"
                    ? "border-red-800/60 bg-red-950/20 text-red-300"
                    : swf.benchmark.flag === "large"
                      ? "border-amber-800/60 bg-amber-950/20 text-amber-300"
                      : "border-neutral-800 bg-neutral-900/40 text-neutral-400"
                }`}
              >
                <span className="uppercase tracking-wider text-[9px] opacity-80">Reality check · </span>
                {swf.benchmark.verdict}
              </div>

              <div className="mt-2 text-[11px] text-neutral-500 leading-relaxed">{swf.total_note}</div>
            </div>

            {/* Scope breakdown */}
            <div className="border-b border-neutral-800 px-5 py-4">
              <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-1">Scope Breakdown</div>
              <div className="text-[10px] text-neutral-500 leading-relaxed mb-1">
                Effective IT load {swf.power.effective_it_mw_central} MW (range {swf.power.effective_it_mw_range[0]}–
                {swf.power.effective_it_mw_range[1]}),{" "}
                {swf.power.basis === "permit_generator_capacity" && swf.power.permit ? (
                  <span className="text-emerald-400/90">
                    from VADEQ air permit {swf.power.permit.registration_no} —{" "}
                    {swf.power.permit.site_generator_mw.toLocaleString()} MW of permitted generator
                    capacity across {swf.power.permit.n_buildings_on_permit} building
                    {swf.power.permit.n_buildings_on_permit === 1 ? "" : "s"}, apportioned by floor
                    area. The 8,818 sqft/MW density assumption is not used for this building.
                  </span>
                ) : (
                  <>from floor area at {swf.power.sqft_per_effective_mw.toLocaleString()} sqft/MW.</>
                )}
              </div>
              <ScopeRow
                label="Scope 1 — on-site cooling"
                tone="amber"
                mgdRange={swf.scope1_onsite_cooling.mgd_range}
                central={swf.scope1_onsite_cooling.mgd_central}
                detail={`${swf.scope1_onsite_cooling.wup_gal_per_mw_day.low}–${swf.scope1_onsite_cooling.wup_gal_per_mw_day.high} gal/MW/day (central ${swf.scope1_onsite_cooling.wup_gal_per_mw_day.central}). Reference tiers: ${swf.scope1_onsite_cooling.wup_reference_tiers.air_cooled} air-cooled, ${swf.scope1_onsite_cooling.wup_reference_tiers.pwc_observed} PWC observed, ${swf.scope1_onsite_cooling.wup_reference_tiers.fully_water_cooled} fully evaporative.`}
                methodology={swf.scope1_onsite_cooling.methodology}
                climatePointMgd={swf.scope1_onsite_cooling.peak_day_mgd}
                climateNote={swf.scope1_onsite_cooling.note}
              />
              <ScopeRow
                label="Scope 2 — electricity-driven"
                tone="sky"
                mgdRange={swf.scope2_electricity.mgd_range}
                central={swf.scope2_electricity.mgd_central}
                detail={`PUE ${swf.scope2_electricity.pue_range[0]}–${swf.scope2_electricity.pue_range[1]} (${
                  swf.scope2_electricity.pue_class === "operator_disclosed"
                    ? "operator-disclosed fleet PUE"
                    : swf.scope2_electricity.pue_class === "new_build"
                      ? "new build, current design practice"
                      : `${swf.scope2_electricity.pue_class} vintage`
                }) × ${swf.scope2_electricity.blended_consumption_gal_per_mwh} gal/MWh Dominion generation-mix-blended consumption factor.`}
                methodology={swf.scope2_electricity.methodology}
              />
              {swf.scope2_electricity.market_based && (
                <div className="mt-1 ml-3 border-l border-neutral-800 pl-3 py-1.5">
                  <div className="flex items-baseline gap-2 text-[11px]">
                    <span className="text-neutral-500">Market-based Scope 2</span>
                    <span className="tabular-nums text-neutral-300">
                      {swf.scope2_electricity.market_based.mgd_central.toFixed(3)} MGD
                    </span>
                    <span className="text-neutral-600">
                      vs {swf.scope2_electricity.mgd_central.toFixed(3)} location-based
                    </span>
                  </div>
                  <div className="mt-1 text-[10px] leading-relaxed text-neutral-500">
                    {swf.scope2_electricity.market_based.claim}. The GHG Protocol requires both
                    figures. This one is contractual, not physical —{" "}
                    {(
                      swf.scope2_electricity.mgd_central -
                      swf.scope2_electricity.market_based.mgd_central
                    ).toFixed(3)}{" "}
                    MGD of real Virginia-basin consumption is netted away by annual renewable
                    matching. The water was still consumed at the plant that actually served this
                    building.
                  </div>
                </div>
              )}
              {swf.scope2_electricity.marginal_based && (
                <div className="mt-1 ml-3 border-l border-neutral-800 pl-3 py-1.5">
                  <div className="flex items-baseline gap-2 text-[11px]">
                    <span className="text-neutral-500">Marginal-mix Scope 2</span>
                    <span className="tabular-nums text-neutral-300">
                      {swf.scope2_electricity.marginal_based.mgd_central.toFixed(3)} MGD
                    </span>
                    <span className="text-neutral-600">
                      ({swf.scope2_electricity.marginal_based.marginal_gal_per_mwh} gal/MWh)
                    </span>
                  </div>
                  <div className="mt-1 text-[10px] leading-relaxed text-neutral-500">
                    The water a <em>new</em> load actually causes: served by the marginal gas
                    unit, not the nuclear baseload. The total barely moves, but it reallocates
                    consumption off the York basin (North Anna, ~never marginal) and onto the
                    James gas fleet — see methodology §16.
                  </div>
                </div>
              )}
              <ScopeRow
                label="Scope 3 — embodied / supply-chain"
                tone="violet"
                mgdRange={swf.scope3_embodied.mgd_range}
                central={swf.scope3_embodied.mgd_central}
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
                if (ctx) memo.generate({ facilityId: selectedGpin!, mode: "memo", facilityContext: ctx, unresolved });
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

        {/* What's Unresolved — the disclosure audit. Deterministic, always
            visible: these gaps are known to the pipeline, not discovered by
            an LLM, so there is nothing to "generate" and wait for. */}
        {unresolved.length > 0 && (
          <div className="border-b border-neutral-800 bg-red-950/10 px-5 py-4">
            <div className="flex items-baseline justify-between gap-2 mb-1">
              <div className="text-[10px] uppercase tracking-wider text-red-400">What&apos;s Unresolved</div>
              <div className="text-[9px] text-neutral-600">
                {unresolved.filter((u) => u.severity === "structural").length} structural ·{" "}
                {unresolved.filter((u) => u.severity === "high").length} widening
              </div>
            </div>
            <p className="text-[10px] text-neutral-500 italic leading-relaxed mb-2.5">
              Derived from this facility&apos;s own record and the estimator&apos;s
              inputs — not model-generated. Each item names what is on record,
              what is dark, and what would close the gap.
            </p>
            <div className="space-y-2 text-[11px]">
              {unresolved.map((u) => {
                const sev = SEVERITY_STYLES[u.severity];
                return (
                  <div key={u.id} className="rounded border border-neutral-800 bg-neutral-900/60 px-3 py-2">
                    <div className="flex items-baseline justify-between gap-2 mb-1.5">
                      <div className="flex items-baseline gap-1.5 min-w-0">
                        <span className="text-amber-400 text-[10px] shrink-0">[{u.id}]</span>
                        <span className="text-neutral-100 text-[11px] leading-snug">{u.title}</span>
                      </div>
                      <span className={`rounded border px-1 text-[9px] uppercase tracking-wider shrink-0 ${sev.className}`}>
                        {sev.label}
                      </span>
                    </div>
                    <div className="space-y-1 text-[10px] leading-relaxed">
                      <div>
                        <span className="text-green-500/80 uppercase tracking-wider text-[9px]">On record: </span>
                        <span className="text-neutral-300">{u.onRecord}</span>
                      </div>
                      <div>
                        <span className="text-red-400/80 uppercase tracking-wider text-[9px]">Dark: </span>
                        <span className="text-neutral-400">{u.gap}</span>
                      </div>
                      {u.impact && (
                        <div>
                          <span className="text-amber-400/80 uppercase tracking-wider text-[9px]">Effect on estimate: </span>
                          <span className="text-neutral-400">{u.impact}</span>
                        </div>
                      )}
                      <div>
                        <span className="text-sky-400/80 uppercase tracking-wider text-[9px]">Would resolve: </span>
                        <span className="text-neutral-400">{u.wouldResolve}</span>
                      </div>
                    </div>
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
