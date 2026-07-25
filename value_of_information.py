"""
Value of information — which SPECIFIC, REAL dataset acquisition shrinks the
county water estimate most, and how feasible each is to obtain.

§35 established the three mechanisms abstractly (transparency / standardization /
verification) and that the grid dominates. This turns that into a decision table:
for each *named* dataset a regulator or researcher could actually pursue, what is
the marginal reduction in the county 90% CI, and who holds it / how hard is it?

Each acquisition maps to collapsing one uncertainty in the shipped Monte Carlo
(common random numbers, as in value_of_disclosure.py, so the deltas are clean):

  ACQUISITION                         collapses                         knob
  Grid water-intensity (plant+marginal) blended gal/MWh uncertainty     grid
  Per-DP contracted load (SCC queue)  facility power (std+verified)      power
  Utility large-customer water meters on-site Scope 1 (measured)         scope1
  Operator PUE disclosures            PUE band                           pue
  Cooling-equipment permits/tonnage   cooling type -> WUP band           cool

Each is scored ALONE (marginal value from today's baseline), then annotated with
who holds it and acquisition difficulty. The ranking is the finding: the
low-effort asks (PUE, cooling permits) barely move the number; the high-value
asks (grid water-intensity; standardized, verified facility load) are the harder
ones -- so a disclosure policy optimized for ease would target the wrong data.

Reads the shipped model. Writes public/data/value_of_information.json.
"""
import json
import math
import os

import numpy as np

import indirect_water_footprint as m

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "value_of_information.json")
SEED = 20260725
N = 40_000
HOURS = 24
VERIFIED = 0.05   # std+verified reporting noise (independent)

# who holds each dataset + how hard to obtain (qualitative, documented)
FEASIBILITY = {
    "grid_water_intensity": {"holder": "USGS (annual) + PJM/EIA dispatch",
        "difficulty": "hard", "note": "plant-level annual water is public; the "
        "marginal/hourly water-intensity that the causal question needs is not"},
    "per_dp_contracted_load": {"holder": "Dominion / SCC (PUR-2026-00011)",
        "difficulty": "medium", "note": "filed at the SCC but usually aggregated "
        "or confidential per delivery point; needs standardized definitions"},
    "utility_customer_water": {"holder": "Prince William Water / Fairfax Water",
        "difficulty": "medium-hard", "note": "metered per-customer use exists but "
        "is not public per facility; the only path to measured on-site Scope 1"},
    "operator_pue": {"holder": "operators (voluntary)",
        "difficulty": "easy", "note": "several publish fleet-wide PUE already"},
    "cooling_permits": {"holder": "PWC ePortal (public)",
        "difficulty": "easy", "note": "public but sparse/redacted (§30)"},
}


def _tri(r, lo, mode, hi):
    lo, mode, hi = float(lo), float(mode), float(hi)
    if hi - lo < 1e-9:
        return np.full(N, mode)
    return r.triangular(lo, min(max(mode, lo), hi), hi, N)


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    srng = np.random.default_rng(SEED)
    wup_scale = _tri(srng, 0.90, 1.00, 1.10)
    s3_frac = _tri(srng, 0.05, 0.10, 0.15)
    permit_factor = _tri(srng, 0.70, 1.00, 1.35)
    cfc, cfb = m.CONSUMPTION_FACTORS_GAL_PER_MWH, m.CONSUMPTION_FACTOR_BOUNDS_GAL_PER_MWH
    cf_nuc = _tri(srng, cfb["nuclear"][0], cfc["nuclear"], cfb["nuclear"][1])
    cf_gas = _tri(srng, cfb["natural_gas_cc"][0], cfc["natural_gas_cc"], cfb["natural_gas_cc"][1])
    cf_coal = _tri(srng, cfb["coal"][0], cfc["coal"], cfb["coal"][1])
    mix = m.DOMINION_GENERATION_MIX
    blended = mix["natural_gas_cc"] * cf_gas + mix["nuclear"] * cf_nuc + mix["coal"] * cf_coal
    blended_central = float(mix["natural_gas_cc"] * cfc["natural_gas_cc"]
                           + mix["nuclear"] * cfc["nuclear"] + mix["coal"] * cfc["coal"])
    pm = m.POWER_MODEL or {}
    pv = pm["predictive_variance"]
    fit_beta = np.asarray(pv["beta_intercept_slope"], float)
    coef_draws = srng.multivariate_normal(fit_beta, pv["noise_var_log10"] * np.asarray(pv["XtX_inv"], float), N)
    fit_idio_sd = math.sqrt(pv["noise_var_log10"])
    pue_groups = {c: _tri(srng, 0.97, 1.0, 1.03) for c in
                  {b["scope_water_footprint"]["scope2_electricity"]["pue_class"] for b in bs}}

    def bvar(i, b):
        r = np.random.default_rng([SEED, 1000 + i])
        swf = b["scope_water_footprint"]
        s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]; pr = swf["scope2_electricity"]["pue_range"]
        return {"z_idio": r.standard_normal(N), "apport": _tri(r, 0.90, 1.0, 1.10),
                "wup_tri": _tri(r, s1c["low"], s1c["central"], s1c["high"]),
                "pue_tri": _tri(r, pr[0], (pr[0] + pr[1]) / 2, pr[1]),
                "z_pwr": r.standard_normal(N), "z_wup": r.standard_normal(N), "z_pue": r.standard_normal(N)}

    def power_undisclosed(b, bv):
        pw = b["scope_water_footprint"]["power"]; ec = pw["effective_it_mw_central"]; gfa = pw.get("gfa_sqft")
        if pw["basis"] == "permit_generator_capacity" or not gfa or ec <= 0:
            return ec * permit_factor * bv["apport"]
        xb = math.log10(gfa); base0 = fit_beta[0] + fit_beta[1] * xb
        return ec * np.power(10.0, (coef_draws[:, 0] + coef_draws[:, 1] * xb) - base0 + fit_idio_sd * bv["z_idio"])

    def county_ci(power=False, scope1=False, pue=False, cool=False, gridv=False):
        blend = blended_central if gridv else blended
        county = np.zeros(N)
        for i, b in enumerate(bs):
            bv = bvar(i, b); swf = b["scope_water_footprint"]; ec = swf["power"]["effective_it_mw_central"]
            eff = ec * (1.0 + VERIFIED * bv["z_pwr"]) if power else power_undisclosed(b, bv)
            s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
            if scope1:      wup = s1c["central"] * (1.0 + VERIFIED * bv["z_wup"])   # measured on-site water
            elif cool:      wup = s1c["central"] * (1.0 + 0.10 * bv["z_wup"])       # cooling type known
            else:           wup = bv["wup_tri"] * wup_scale
            s1 = eff * wup / 1e6
            s2e = swf["scope2_electricity"]; pr = s2e["pue_range"]
            pue_v = ((pr[0] + pr[1]) / 2) * (1.0 + 0.02 * bv["z_pue"]) if pue else bv["pue_tri"] * pue_groups[s2e["pue_class"]]
            county += (s1 + eff * pue_v * HOURS * blend / 1e6) * (1 + s3_frac)
        p5, p50, p95 = np.percentile(county, [5, 50, 95])
        return round(float((p95 - p5) / p50 * 100), 1)

    base = county_ci()
    acquisitions = {
        "grid_water_intensity":  county_ci(gridv=True),
        "per_dp_contracted_load": county_ci(power=True),
        "utility_customer_water": county_ci(scope1=True),
        "operator_pue":          county_ci(pue=True),
        "cooling_permits":       county_ci(cool=True),
    }
    ranked = sorted(((k, base - v, v) for k, v in acquisitions.items()), key=lambda t: -t[1])
    # CONDITIONAL value: grid water-intensity ALONE barely helps (power still
    # dominates), but it is the binding gap ONCE power is resolved -- the §35
    # result. Report both so "biggest single acquisition" (power) and "binding
    # floor" (grid) are reconciled rather than contradictory.
    ci_power = county_ci(power=True)
    ci_power_grid = county_ci(power=True, gridv=True)
    grid_conditional = {"ci_after_power_pct": ci_power,
                        "ci_after_power_and_grid_pct": ci_power_grid,
                        "grid_delta_once_power_resolved_halfwidth_pp": round((ci_power - ci_power_grid) / 2, 1)}

    out = {
        "baseline_ci_width_pct": base,
        "note": "Each acquisition scored ALONE (marginal reduction from today's baseline), "
                "common random numbers. delta_ci_pct is the reduction in the full 90% CI width "
                "(halve for +/- reduction).",
        "acquisitions": [{"dataset": k, "ci_width_after_pct": after,
                          "delta_ci_pct": round(delta, 1),
                          "delta_halfwidth_pp": round(delta / 2, 1),
                          **FEASIBILITY[k]} for k, delta, after in ranked],
        "grid_conditional_value": grid_conditional,
        "headline": (
            f"Scored ALONE from today's +/-{base/2:.0f}%: the single highest-value acquisition is "
            f"standardized, verified facility load (per-DP), -{ (base-ci_power)/2:.0f}pp to "
            f"+/-{ci_power/2:.0f}%, because power is the current dominant uncertainty. Grid "
            f"water-intensity helps little alone (-{(base-acquisitions['grid_water_intensity'])/2:.0f}pp) "
            f"but is the BINDING gap once power is resolved "
            f"(-{grid_conditional['grid_delta_once_power_resolved_halfwidth_pp']:.0f}pp, to "
            f"+/-{ci_power_grid/2:.0f}%). On-site water metering, PUE, and cooling permits move the "
            f"county number ~0 (Scope 1 is only ~4% of the footprint). The high-value data are the "
            f"hard-to-obtain ones; a policy optimized for ease targets the wrong datasets."),
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(f"baseline county 90% CI: +/-{base/2:.0f}%\n")
    print(f"{'acquisition':<26}{'CI after':>10}{'-halfwidth':>12}{'difficulty':>14}")
    for k, delta, after in ranked:
        print(f"{k:<26}+/-{after/2:>6.0f}%{delta/2:>11.1f}pp{FEASIBILITY[k]['difficulty']:>14}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
