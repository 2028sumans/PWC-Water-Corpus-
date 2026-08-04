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

/**
 * The convention table, rendered as bars rather than prose.
 *
 * This is the project's headline result and it is a COMPARISON, so a reader has
 * to see four numbers against each other to get it: the same physical
 * electricity, the same fleet, the same Lake Anna — and a share that moves from
 * 0.9% to 43.3% purely on which published convention you apply. Written out as a
 * sentence it reads as one more statistic. Drawn as bars sorted by the width of
 * the accounting boundary, the monotone fall is visible at a glance, which is
 * the actual argument.
 */
function ConventionBars({ c }: { c: NonNullable<ReturnType<typeof useCountyAnalysis>>["conventions"] }) {
  if (!c) return null;
  const rows = Object.values(c.conventions)
    .filter((v) => v.computable && v.lake_anna_pct_of_scope2 != null)
    .sort((x, y) => (y.lake_anna_pct_of_scope2 ?? 0) - (x.lake_anna_pct_of_scope2 ?? 0));
  const notComputable = Object.values(c.conventions).filter((v) => !v.computable);
  const max = Math.max(...rows.map((r) => r.lake_anna_pct_of_scope2 ?? 0));

  return (
    <div className="rounded border border-amber-500/25 bg-amber-500/[0.03] p-3">
      <div className="text-[9px] uppercase tracking-wider text-amber-500/70">
        Headline result · which basin gets charged
      </div>
      <div className="mt-1 text-[11px] font-medium leading-snug text-amber-400/90">
        Lake Anna&apos;s share of the same electricity-related water:{" "}
        {c.lake_anna_share_range_pct.min}% to {c.lake_anna_share_range_pct.max}% —{" "}
        a factor of {Math.round(c.lake_anna_share_range_pct.spread_factor)} across{" "}
        {c.n_computable} standard conventions.
      </div>

      <div className="mt-2.5 space-y-1.5">
        {rows.map((r) => {
          const pct = r.lake_anna_pct_of_scope2 ?? 0;
          return (
            <div key={r.label} className="grid grid-cols-[1fr_auto] items-baseline gap-2">
              <div className="min-w-0">
                <div className="truncate text-[10px] text-neutral-300">{r.label}</div>
                <div className="mt-0.5 h-1 w-full overflow-hidden rounded-sm bg-neutral-800">
                  <div
                    className="h-full rounded-sm bg-amber-500/70"
                    style={{ width: `${Math.max((pct / max) * 100, 1.5)}%` }}
                  />
                </div>
                <div className="mt-0.5 truncate text-[9px] text-neutral-600">{r.geography}</div>
              </div>
              <div className="tabular-nums text-[11px] font-medium text-amber-400/90">
                {pct.toFixed(1)}%
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-2.5 border-t border-amber-500/15 pt-2 text-[9px] leading-relaxed text-neutral-500">
        {c.the_ordering_is_the_point}
      </div>
      {notComputable.length > 0 && (
        <div className="mt-1.5 text-[9px] leading-relaxed text-neutral-600">
          <span className="text-neutral-500">
            {notComputable.length} further conventions are documented but not computable here:
          </span>{" "}
          {notComputable.map((v) => v.label).join("; ")}. Reported as unresolved rather than
          estimated.
        </div>
      )}
    </div>
  );
}

export function CountyAnalysis() {
  const a = useCountyAnalysis();
  // Open by default: the convention table is the headline result, and a result
  // behind a closed disclosure triangle is a result nobody reads.
  const [open, setOpen] = useState(true);
  if (!a) return null;

  const cards: Array<React.ComponentProps<typeof Card>> = [];

  // Drought state. This claim previously existed only as a hardcoded string in
  // the rotating ticker, typed by hand rather than read from climate_context
  // .json -- so the file shipped unread while the site asserted its contents
  // from memory. Reading it means the number cannot drift from its source.
  if (a.climate) {
    const p = a.climate.drought.PDSI;
    const rp = a.climate.drought_return_periods;
    const sev = rp.return_periods_full_record.pdsi_le_5?.return_period_years;
    cards.push({
      label: "Drought state",
      value: `PDSI ${p.latest_value} — driest ${p.percentile_of_record}% of ${p.n_months.toLocaleString()} months on record`,
      detail: `As of ${p.latest_month}, against a ${rp.record.n_years}-year record (${rp.record.first_year}–${rp.record.last_year}).${sev ? ` A PDSI at or below −5 recurs about every ${sev} years.` : ""} Record minimum is ${p.min_ever}.`,
      tone: "warn",
    });
  }

  // Seasonal coincidence (§31, as corrected)
  //
  // `demand_cdd.peak_month` is the cooling-degree-day peak (July). That is a
  // degree-day statistic, not the water shape, and the two do not fall in the
  // same month: measured utility data (ICPRB Table A.3-2) puts the on-site
  // water peak in August, which is also when the rivers bottom. Reporting the
  // CDD month here overstated the swing and, ironically, understated the
  // coincidence it was pointing at. Label the curve for what it is and lead
  // with the month that actually matters.
  if (a.seasonal) {
    const pot = Object.values(a.seasonal.supply_streamflow)[0];
    const lowMonth = pot?.low_flow_month ?? "Aug";
    cards.push({
      label: "Seasonal coincidence",
      value: `On-site water peaks ${lowMonth} · rivers at ${pot?.low_flow_pct_of_annual}% of mean flow the same month`,
      detail:
        `Measured utility data puts the water peak at 1.8× the mean month (ICPRB Table A.3-2), and the ${pot?.name ?? "Potomac"} bottoms in ${lowMonth} — demand and scarcity land together. The cooling-degree-day curve peaks a month earlier, in ${a.seasonal.demand_cdd.peak_month}; it is a temperature signal, not the water shape.`,
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

  // Entitlement pathway (§46) — the governance finding.
  if (a.entitlement) {
    const e = a.entitlement;
    cards.push({
      label: "Discretionary review",
      value: `${e.THE_FINDING.buildings_with_a_sup} of ${e.THE_FINDING.of_total} buildings went through a Special Use Permit`,
      detail: `${e.by_right_eligibility.inside_pct}% sit inside the Data Center Opportunity Overlay, where the use is by-right and the SUP — the county's only discretionary review, the one that can attach conditions — never triggers. ${e.planning_case.absent_pct}% have no planning case on record at all.`,
      tone: "warn",
    });
    const p = e.price_asymmetry;
    cards.push({
      label: "What the county priced",
      value: `Fire and rescue $${Math.round(p.fire_and_rescue_contribution_usd).toLocaleString()} vs water quality $${Math.round(p.water_quality_contribution_usd).toLocaleString()}`,
      detail: `A ${Math.round(p.ratio_fire_to_water)}× gap in the same proffer package (${p.case}). Both are real obligations; only one is priced as if it scales with the building.`,
      tone: "warn",
    });
  }

  // Broad Run (§41-42) — where the exposure concentrates.
  if (a.broadRun) {
    const b = a.broadRun;
    cards.push({
      label: "Broad Run concentration",
      value: `${b.concentration.pct_of_fleet}% of the fleet on ${b.concentration.pct_of_county_land}% of county land`,
      detail: `${b.concentration.buildings_in_basin} of ${b.concentration.buildings_total} buildings, a ${b.concentration.concentration_factor}× concentration. Water there warmed ${b.warming.theil_sen_slope_c_per_yr}°C/yr (Theil–Sen, p=${b.warming.p_value}), about ${b.warming.implied_change_c}°C over the record.`,
      tone: "warn",
    });
    cards.push({
      label: "The gage problem",
      value: `The flow denominator comes from a gage shut down in ${b.the_gage_problem.decommissioned}`,
      detail: `${b.the_gage_problem.gage} never observed a single data center. Every basin percentage on this site divides by a number no instrument has measured since then — the largest single uncertainty in the basin results, and not one more data could fix without a new gage.`,
      tone: "warn",
    });
  }

  // Growth envelope (§38) — the entitlement overhang.
  if (a.envelope) {
    const g = a.envelope;
    cards.push({
      label: "Entitlement overhang",
      value: `${g.county_entitlement.pct_unbuilt}% of entitled floor area is unbuilt`,
      detail: `${(g.county_entitlement.remaining_gfa_sqft / 1e6).toFixed(1)}M of ${(g.county_entitlement.planned_gfa_sqft / 1e6).toFixed(1)}M sq ft already approved and not yet built. Historically only ${g.empirical_completion_rates.lbnl_capacity_pct}–${g.empirical_completion_rates.pjm_capacity_weighted_pct}% of queued capacity reaches operation (LBNL), so the envelope is a ceiling, not a forecast.`,
    });
  }

  // Loudoun natural experiment (§40) — the untested outside signal.
  if (a.loudoun) {
    const l = a.loudoun;
    const rows = Object.entries(l.daily_production_trend_2013_2023_pct_per_yr).sort((x, y) => y[1] - x[1]);
    const [topName, topVal] = rows[0];
    cards.push({
      label: "Loudoun natural experiment",
      value: `${topName} +${topVal}%/yr — every other WMA supplier flat or falling`,
      detail: `${rows.slice(1).map(([n, v]) => `${n} ${v > 0 ? "+" : ""}${v}%`).join(", ")}. The one utility serving the world's largest data-center concentration is the one growing. Suggestive, not attributed — neither ICPRB nor this project has tested it.`,
      tone: "good",
    });
  }

  // Validation and its limits (§35) — the honesty card.
  if (a.validation) {
    const v = a.validation;
    const cmp = v.usgs_thermoelectric_validation.comparison;
    const worst = Math.max(...Object.values(cmp).map((x) => x.error_pct));
    cards.push({
      label: "External validation",
      value: `Within ${worst}% of USGS across ${v.usgs_thermoelectric_validation.n_plant_years} plant-years`,
      detail: `${Object.entries(cmp).map(([k, x]) => `${k.replace(/_/g, " ")} ${x.shipped} vs ${x.empirical} gal/MWh`).join("; ")}. Built by USGS independently of anything here. But ${Object.keys(v.INDEPENDENCE_LIMITS).length} named checks are NOT independent — ICPRB shares this model's power input, and the 309 gal/MW/day central is derived from the utility figure it is checked against.`,
      tone: "good",
    });
  }

  if (!cards.length && !a.conventions) return null;

  return (
    <div className="mt-4">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-1.5 text-[10px] uppercase tracking-wider text-neutral-500 hover:text-neutral-300 transition"
      >
        {open ? <ChevronDown className="h-3 w-3" /> : <ChevronRight className="h-3 w-3" />}
        County analysis
        <span className="text-neutral-700">· {cards.length + (a.conventions ? 1 : 0)}</span>
      </button>
      {open && (
        <div className="mt-2 space-y-2 rounded border border-neutral-800 bg-neutral-900/40 p-3">
          <ConventionBars c={a.conventions} />
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
