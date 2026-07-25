"use client";

/**
 * "How this building compares" — places the selected facility inside the
 * county-level analyses (METHODOLOGY 40-42, 46) instead of leaving those results
 * as fleet aggregates the reader has to apply themselves.
 *
 * Four comparisons, each answering a question the per-facility numbers alone
 * cannot:
 *   EVIDENCE   which power-evidence tier is this building on, and how wide is
 *              its interval versus that tier's median and versus a
 *              permit-observed building? (§40.1)
 *   BASIN      what share of its watershed's draw does it carry, and what is
 *              that basin's peak-day stress? (§41)
 *   TIMING     when does its own draw bind hardest against local flow? (§46)
 *   OVERSIGHT  is it inside or outside the discharge-permit and monitoring
 *              networks, and how does that compare to the fleet? (§42)
 *
 * Renders nothing when the analyses have not loaded, so the dossier degrades to
 * exactly what it showed before rather than erroring.
 */
import type { FacilityWaterContext, ScopeWaterFootprint } from "@/lib/useFacilityProfiles";
import { useCountyAnalysis } from "@/lib/useCountyAnalysis";

function Row({
  label,
  value,
  detail,
  tone = "neutral",
}: {
  label: string;
  value: string;
  detail?: string;
  tone?: "neutral" | "warn" | "good";
}) {
  const t =
    tone === "warn" ? "text-amber-400/90" : tone === "good" ? "text-emerald-400/90" : "text-neutral-300";
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-[10px] uppercase tracking-wider text-neutral-600 shrink-0">{label}</span>
        <span className={`text-[11px] text-right ${t}`}>{value}</span>
      </div>
      {detail && <div className="mt-0.5 text-[10px] leading-relaxed text-neutral-500">{detail}</div>}
    </div>
  );
}

export function FacilityContext({
  swf,
  waterContext,
}: {
  swf: ScopeWaterFootprint | null;
  waterContext: FacilityWaterContext | null;
}) {
  const a = useCountyAnalysis();
  if (!a || !swf) return null;

  const rows: Array<React.ComponentProps<typeof Row>> = [];

  // ---- evidence tier (§40.1) ----------------------------------------------
  const tier = swf.power.evidence_tier;
  const ladder = a.ladder?.evidence_ladder;
  const myWidth = swf.uncertainty?.relative_width_pct;
  if (ladder && tier != null) {
    const t = ladder.tiers[String(tier)];
    const t1 = ladder.tiers["1"];
    if (t?.ci_halfwidth_pct_median != null) {
      const mine = myWidth != null ? `±${Math.round(myWidth / 2)}%` : "—";
      const vsObserved =
        tier === 1
          ? "This is the observed tier — the narrowest evidence class in the fleet."
          : `A permit-observed building sits at ±${t1?.ci_halfwidth_pct_median}%. The gap is evidence, not method: this building's power is inferred from floor area.`;
      rows.push({
        label: "Evidence tier",
        value: `Tier ${tier} · ${mine} (tier median ±${t.ci_halfwidth_pct_median}%)`,
        detail: `${t.label}. ${vsObserved}`,
        tone: tier === 1 ? "good" : "warn",
      });
    }
  }

  // ---- basin share + peak-day stress (§41) --------------------------------
  const ws = waterContext?.watershed_name ?? null;
  const basin = ws && a.basin?.basins?.[ws];
  if (ws && basin) {
    const share = basin.draw_peak_day_mgd
      ? (100 * swf.scope1_onsite_cooling.peak_day_mgd) / basin.draw_peak_day_mgd
      : null;
    rows.push({
      label: "Basin share",
      value:
        share != null
          ? `${share.toFixed(1)}% of ${ws} peak-day draw`
          : `${ws} · ${basin.n_buildings} buildings`,
      detail: `${ws} holds ${basin.n_buildings} data-center buildings. At full buildout the basin's peak-day on-site draw is ${basin.pct_of_low_month_flow_PEAK_draw}% of its lowest-month mean flow (${basin.flow_low_month}); ${basin.completed_only_pct_of_low_month_flow_PEAK}% for buildings completed today. Scale comparison, not a withdrawal — supply is Occoquan/Potomac.`,
      tone: basin.pct_of_low_month_flow_PEAK_draw > 50 ? "warn" : "neutral",
    });
  }

  // ---- when it binds (§46) -------------------------------------------------
  const surf = ws && a.surface?.surfaces?.[ws];
  if (ws && surf) {
    const c = surf.central;
    rows.push({
      label: "When it binds",
      value: `${c.worst_month} — basin draw hits ${c.worst_pct_of_flow}% of that month's flow`,
      detail:
        "Cooling demand is summer-concentrated and local flow bottoms in the same months, so this building's draw lands when the basin is driest (§46).",
      tone: "warn",
    });
  }

  // ---- oversight (§42) -----------------------------------------------------
  const wc = waterContext;
  const gap = a.exposure?.regulatory_monitoring_gap;
  if (wc && gap) {
    const d = typeof wc.d_stream_ft === "number" ? wc.d_stream_ft : null;
    const hasNpdes = wc.has_npdes === 1;
    const deqNear = typeof wc.n_deq_monitoring_1mi === "number" ? wc.n_deq_monitoring_1mi : 0;
    const parts: string[] = [];
    if (d != null) parts.push(`${Math.round(d)} ft from a mapped stream`);
    parts.push(hasNpdes ? "holds an NPDES permit" : "no NPDES permit");
    parts.push(deqNear > 0 ? `${deqNear} DEQ station(s) within 1 mi` : "no DEQ station within 1 mi");
    const blind = d != null && d <= 300 && !hasNpdes && deqNear === 0;
    rows.push({
      label: "Oversight",
      value: blind ? "In the compound blind spot" : parts[0],
      detail: `${parts.join(" · ")}. Fleet-wide: ${gap.no_npdes.n} of 243 hold no discharge permit and ${gap.no_deq_station_within_1mi.n} of 243 — every building — have no DEQ monitoring station within a mile (§42)${
        blind ? `. This building is one of the ${gap.compound_blind_spot.n} that are stream-adjacent, unpermitted and unmonitored at once.` : "."
      }`,
      tone: blind ? "warn" : "neutral",
    });
  }

  if (!rows.length) return null;

  return (
    <div className="border-b border-neutral-800 px-5 py-4">
      <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
        How this building compares
      </div>
      <div className="space-y-2.5">
        {rows.map((r) => (
          <Row key={r.label} {...r} />
        ))}
      </div>
      <div className="mt-2.5 border-t border-neutral-800/80 pt-2 text-[9px] italic leading-relaxed text-neutral-600">
        Places this facility inside the county-scale analyses (METHODOLOGY §40–42, §46). Each figure
        carries its framing condition; basin ratios are scale comparisons, not withdrawal
        attributions.
      </div>
    </div>
  );
}
