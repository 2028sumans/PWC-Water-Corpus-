"use client";

/**
 * County-level analysis panel — the findings that are about the FLEET and the
 * BASINS rather than any one building (METHODOLOGY 31, 35, 37-38, 40-43, 46).
 *
 * Deliberately compact and collapsed by default: the app is facility-first, and
 * these are context for the table, not a competing dashboard. Each card states
 * the number and the caveat that makes it honest, because every one of these
 * results carries a framing condition (scale-comparison vs withdrawal;
 * modelled vs measured; perfect-information vs realistic disclosure).
 */
import { useState } from "react";
import { ChevronDown, ChevronRight } from "lucide-react";
import { useCountyAnalysis } from "@/lib/useCountyAnalysis";

function Card({
  label,
  value,
  detail,
  tone = "neutral",
}: {
  label: string;
  value: string;
  detail: string;
  tone?: "neutral" | "warn" | "good";
}) {
  const valueTone =
    tone === "warn" ? "text-amber-400/90" : tone === "good" ? "text-emerald-400/90" : "text-neutral-200";
  return (
    <div className="border-t border-neutral-800/80 pt-2">
      <div className="text-[9px] uppercase tracking-wider text-neutral-600">{label}</div>
      <div className={`text-[11px] font-medium ${valueTone} leading-snug mt-0.5`}>{value}</div>
      <div className="text-[10px] text-neutral-500 leading-relaxed mt-0.5">{detail}</div>
    </div>
  );
}

export function CountyAnalysis() {
  const a = useCountyAnalysis();
  const [open, setOpen] = useState(false);
  if (!a) return null;

  const cards: Array<React.ComponentProps<typeof Card>> = [];

  // Seasonal coincidence (§31)
  if (a.seasonal) {
    const pot = Object.values(a.seasonal.supply_streamflow)[0];
    cards.push({
      label: "Seasonal coincidence",
      value: `Demand peaks ${a.seasonal.demand_cdd.peak_month} · rivers at ${pot?.low_flow_pct_of_annual}% of mean flow`,
      detail:
        "Cooling demand and the streamflow minimum land in the same weeks (NOAA CDD × USGS gages). Both curves measured.",
      tone: "warn",
    });
  }

  // Seasonal × basin surface (§46)
  if (a.surface) {
    const b = a.surface.binding_condition;
    cards.push({
      label: "Where × when it binds",
      value: `${b.watershed} in ${b.month} — ${b.pct_of_monthly_flow}% of that month's flow`,
      detail:
        "Crossing season with basin: ~7× the flat annual figure. Scale comparison, not a withdrawal — supply is Occoquan/Potomac.",
      tone: "warn",
    });
  }

  // Basin peak-day (§41)
  if (a.basin) {
    const br = a.basin.basins["BROAD RUN"];
    if (br) {
      cards.push({
        label: "Basin peak-day stress",
        value: `Broad Run: ${br.pct_of_low_month_flow_PEAK_draw}% of lowest-month flow at full buildout`,
        detail: `${br.completed_only_pct_of_low_month_flow_PEAK}% for buildings completed today; ${
          br.downstream_gage_sensitivity?.pct_of_low_month_flow_PEAK_draw ?? "—"
        }% at the downstream gage (robust to gage choice).`,
        tone: "warn",
      });
    }
  }

  // Exposure & monitoring gap (§42)
  if (a.exposure) {
    const g = a.exposure.regulatory_monitoring_gap;
    cards.push({
      label: "Monitoring void",
      value: `Nearest state monitoring station is 1.5 mi from any facility`,
      detail: `${a.exposure.exposure.within_300ft_of_stream.n} sit within 300 ft of a stream and ${g.no_npdes.n} hold no operational-water permit. No facility has a DEQ station within a mile (median 4.1 mi) — descriptive of monitoring geography, not evidence of avoidance (§42.2a).`,
      tone: "warn",
    });
  }

  // Evidence ladder (§40)
  if (a.ladder) {
    const t = a.ladder.evidence_ladder.tiers;
    cards.push({
      label: "Evidence ladder",
      value: `Permit-observed ±${t["1"]?.ci_halfwidth_pct_median}% vs floor-area ±${t["4"]?.ci_halfwidth_pct_median}%`,
      detail: `A ${a.ladder.evidence_ladder.tier4_over_tier1_width_ratio}× wider interval for the same model — the gap is evidence, not method. Tier 2 (stated load) is empty: no building publishes one.`,
    });
    const pk = a.ladder.peak_day.all_243_buildings;
    cards.push({
      label: "Peak day vs annual",
      value: `${pk.peak_day_s1_mgd} MGD peak-day vs ${pk.annual_avg_s1_mgd} MGD annual (${pk.ratio}×)`,
      detail: "Utilities size to peak day, and the peak coincides with the flow minimum. Annual framing understates ~10×.",
    });
  }

  // Disclosure decomposition (§35)
  if (a.disclosure) {
    const m = a.disclosure.three_mechanisms_ci_width_pct;
    cards.push({
      label: "Transparency / standardization / verification",
      value: `±${Math.round(m.baseline / 2)}% → ±${Math.round(m.transparency_only / 2)}% → ±${Math.round(
        m.transparency_plus_standardization / 2,
      )}%`,
      detail:
        "Publishing alone buys ~nothing under a modelled standardization gap; standardization carries nearly all the facility-side value. Modelled, not measured.",
    });
  }

  // Value of information (§38)
  if (a.voi) {
    const top = a.voi.acquisitions[0];
    const NAMES: Record<string, string> = {
      per_dp_contracted_load: "Per-delivery-point contracted load",
      grid_water_intensity: "Grid water-intensity",
      utility_customer_water: "Utility customer water meters",
      operator_pue: "Operator PUE",
      cooling_permits: "Cooling-equipment permits",
    };
    cards.push({
      label: "Highest-value data to acquire",
      value: `${NAMES[top.dataset] ?? top.dataset.replace(/_/g, " ")} — ${top.delta_halfwidth_pp}pp narrower`,
      detail: `Held by ${top.holder} (${top.difficulty}). Grid water-intensity is the binding gap once power is resolved; the easy asks (PUE, cooling permits) move the county number ~0.`,
      tone: "good",
    });
  }

  // Growth scenarios (§37)
  if (a.growth) {
    const c = a.growth.scenarios["2050_central"];
    cards.push({
      label: "2050 scenarios",
      value: `${a.growth.baseline_today.total_mgd.toFixed(0)} → ~${c?.grid_today.total_mgd.toFixed(
        0,
      )} MGD (central buildout)`,
      detail: `Decarbonizing the grid cuts that to ~${c?.grid_decarbonized?.total_mgd.toFixed(
        0,
      )} MGD — a bigger lever than any facility measure. Scenarios, not forecasts.`,
    });
  }

  // Forward-load triangulation (§43)
  if (a.triangulation) {
    const t = a.triangulation;
    cards.push({
      label: "Forward load, triangulated",
      value: `${t.pjm_teac_forward.total_mw.toLocaleString()} MW committed for ${t.pjm_teac_forward.in_service}`,
      detail: `${t.comparisons.teac_forward_pct_of_model_stock}% of today's inventoried stock (~${t.this_model.grid_side_mw_all.toLocaleString()} MW grid-side). Three independent public records, mutually consistent.`,
    });
  }

  if (!cards.length) return null;

  return (
    <div className="mt-4">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-1.5 text-[10px] uppercase tracking-wider text-neutral-500 hover:text-neutral-300 transition"
      >
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        County analysis
        <span className="text-neutral-700">· {cards.length}</span>
      </button>
      {open && (
        <div className="mt-2 space-y-2 rounded border border-neutral-800 bg-neutral-900/40 p-3">
          {cards.map((c) => (
            <Card key={c.label} {...c} />
          ))}
          <div className="border-t border-neutral-800/80 pt-2 text-[9px] text-neutral-600 leading-relaxed italic">
            Fleet- and basin-scale findings from the analysis suite. Each carries its framing
            condition; see METHODOLOGY §31, §35, §37–38, §40–43, §46 for full derivations.
          </div>
        </div>
      )}
    </div>
  );
}
