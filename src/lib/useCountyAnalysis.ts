"use client";

/**
 * Loads the county-level analysis outputs produced by the Python analysis suite
 * (METHODOLOGY 31, 35, 37-38, 40-43, 46). These are county/basin-scale findings
 * rather than per-facility evidence, so they live beside the facility table
 * rather than inside a facility dossier.
 *
 * Each file is optional: the panel renders whatever is present, so adding a new
 * analysis to the pipeline surfaces it here without a UI change, and a missing
 * file degrades to a hidden row rather than an error.
 */
import { useEffect, useState } from "react";

export interface SeasonalStress {
  demand_cdd: { peak_month: string; jun_sep_share_pct: number };
  supply_streamflow: Record<string, { low_flow_month: string; low_flow_pct_of_annual: number; name?: string }>;
  coincidence_index: { peak_month: string; monthly: Record<string, number> };
  headline: string;
}

export interface ValueOfDisclosure {
  three_mechanisms_ci_width_pct: Record<string, number>;
  facility_vs_grid_ci_width_pct_perfect_info: Record<string, number>;
  standardization_gap_sensitivity_ci_width_pct_MODELED: Record<string, number>;
  headline: string;
}

export interface ValueOfInformation {
  baseline_ci_width_pct: number;
  acquisitions: Array<{
    dataset: string; ci_width_after_pct: number; delta_halfwidth_pp: number;
    holder: string; difficulty: string; note: string;
  }>;
  grid_conditional_value: Record<string, number>;
  headline: string;
}

export interface GrowthScenarios {
  baseline_today: { effective_it_mw: number; total_mgd: number; onsite_s1_mgd: number };
  pipeline_mw_grid: number;
  scenarios: Record<string, {
    effective_it_mw: number;
    grid_today: { scope1_onsite_mgd: number; scope2_mgd: number; total_mgd: number };
    grid_decarbonized?: { total_mgd: number };
  }>;
  icprb_cross_check_onsite: Record<string, number | string | boolean>;
  headline: string;
}

export interface EvidenceLadder {
  evidence_ladder: {
    tiers: Record<string, {
      label: string; n_buildings: number; effective_it_mw: number;
      ci_width_pct_median?: number; ci_halfwidth_pct_median?: number; note?: string;
    }>;
    tier4_over_tier1_width_ratio: number | null;
    headline: string;
  };
  peak_day: {
    all_243_buildings: { annual_avg_s1_mgd: number; peak_day_s1_mgd: number; ratio: number };
    completed_only: { annual_avg_s1_mgd: number; peak_day_s1_mgd: number; ratio: number | null; n: number };
    why_it_matters: string;
  };
}

export interface BasinStress {
  framing: string;
  basins: Record<string, {
    gage: string; n_buildings: number; draw_annual_mgd: number; draw_peak_day_mgd: number;
    flow_low_month: string; flow_low_month_mgd: number;
    pct_of_low_month_flow_PEAK_draw: number;
    completed_only_pct_of_low_month_flow_PEAK: number;
    downstream_gage_sensitivity?: { pct_of_low_month_flow_PEAK_draw: number };
  }>;
  headline: string;
}

export interface ExposureGap {
  exposure: {
    distance_to_stream_ft: { min: number; median: number; max: number };
    within_300ft_of_stream: { n: number; pct: number };
  };
  regulatory_monitoring_gap: {
    no_npdes: { n: number; pct: number };
    no_deq_station_within_1mi: { n: number; pct: number };
    compound_blind_spot: { n: number; pct: number; definition: string };
  };
  community_observation_layer: { research_grade_inat_within_1mi: { median: number; max: number } };
  headline: string;
}

export interface SeasonalBasinSurface {
  surfaces: Record<string, {
    n_buildings: number;
    central: { monthly_pct_of_flow: Record<string, number>; worst_month: string; worst_pct_of_flow: number };
  }>;
  binding_condition: { watershed: string; month: string; pct_of_monthly_flow: number };
  why_crossing_matters: Record<string, string | number | null>;
}

export interface PipelineTriangulation {
  this_model: { grid_side_mw_all: number; grid_side_mw_completed: number };
  interconnection_fyi: { n_sites: number; band_sum_low_mw: number; band_sum_high_mw: number };
  pjm_teac_forward: { total_mw: number; n_delivery_points: number; in_service: string };
  comparisons: { teac_forward_pct_of_model_stock: number };
  headline: string;
}

export interface CountyAnalysis {
  seasonal?: SeasonalStress;
  disclosure?: ValueOfDisclosure;
  voi?: ValueOfInformation;
  growth?: GrowthScenarios;
  ladder?: EvidenceLadder;
  basin?: BasinStress;
  exposure?: ExposureGap;
  surface?: SeasonalBasinSurface;
  triangulation?: PipelineTriangulation;
}

const FILES: Array<[keyof CountyAnalysis, string]> = [
  ["seasonal", "seasonal_stress"],
  ["disclosure", "value_of_disclosure"],
  ["voi", "value_of_information"],
  ["growth", "growth_scenarios"],
  ["ladder", "evidence_ladder"],
  ["basin", "basin_stress"],
  ["exposure", "exposure_gap"],
  ["surface", "seasonal_basin_surface"],
  ["triangulation", "pipeline_triangulation"],
];

let _cache: CountyAnalysis | null = null;

export function useCountyAnalysis() {
  const [data, setData] = useState<CountyAnalysis | null>(_cache);

  useEffect(() => {
    if (_cache) return;
    let cancelled = false;
    Promise.all(
      FILES.map(([key, file]) =>
        fetch(`/data/${file}.json`)
          .then((r) => (r.ok ? r.json() : null))
          .then((v) => [key, v] as const)
          .catch(() => [key, null] as const),
      ),
    ).then((pairs) => {
      if (cancelled) return;
      const out: CountyAnalysis = {};
      for (const [key, value] of pairs) {
        if (value) (out as Record<string, unknown>)[key] = value;
      }
      _cache = out;
      setData(out);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return data;
}
