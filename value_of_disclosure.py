"""
Value of facility power information — decomposed into three DISTINCT mechanisms.

A reviewer rightly pressed that "disclosure" is not one thing. This analysis
separates the three interventions that a naive "value of disclosure" conflates:

  TRANSPARENCY   Is the number published at all?
  STANDARDIZATION Do facilities report the SAME quantity, defined and time-
                 windowed the same way? (design vs actual load, nameplate vs
                 metered, annual vs peak)
  VERIFICATION   Can the reported number be independently checked against
                 permits, meters, or utility records?

They enter the model as separate knobs:
  - TRANSPARENCY moves a building from its inferred power (GP predictive variance,
    §32, or the Eq 6-3 permit factor) to a reported number.
  - lack of STANDARDIZATION = a SHARED definitional/temporal error term that hits
    the whole fleet the same way and therefore does NOT average down.
  - lack of VERIFICATION = a larger INDEPENDENT reporting error (and, in reality,
    room for systematic mis-reporting; we model only the independent part, so the
    value of verification here is a LOWER bound).

The headline finding survives and sharpens: transparency WITHOUT standardization
and verification has sharply diminishing value. At the county scale the dominant
facility-side lever is standardization (its error does not average away), while
the single largest gap of all is not a facility attribute at all -- it is the
grid's water-intensity (Scope 2 ~87% of the footprint).

MODELED, NOT MEASURED
The standardization-gap magnitude is a MODELED parameter (swept 0-15%), not an
empirical one -- operator-reporting variance is undocumented, which is itself
part of the finding. It is labelled "modeled" throughout.

COMMON RANDOM NUMBERS (clean scenario comparison)
Every scenario is evaluated on the SAME underlying random draws: shared
systematic variates are drawn once; each building's variates are drawn from a
deterministic per-building seed and are byte-identical across scenarios. Only the
TRANSFORMATION (which knob is on) differs between scenarios, so a difference in
the county interval is the intervention's effect, not Monte Carlo noise.

Reads the shipped model; pure NumPy. Writes public/data/value_of_disclosure.json.
"""
import json
import math
import os

import numpy as np

import indirect_water_footprint as m

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "value_of_disclosure.json")
SEED = 20260725
N = 40_000
HOURS = 24

# verification quality = independent reporting-noise sigma (averages down)
VERIFIED_NOISE = 0.05
UNVERIFIED_NOISE = 0.10
# standardization gap = shared definitional/temporal sigma (does NOT average down)
MODELED_STD_GAP = 0.10


def _tri(r, lo, mode, hi):
    lo, mode, hi = float(lo), float(mode), float(hi)
    if hi - lo < 1e-9:
        return np.full(N, mode)
    return r.triangular(lo, min(max(mode, lo), hi), hi, N)


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    # ---- shared systematic variates: drawn ONCE, reused by every scenario -----
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
    fit_coef_cov = pv["noise_var_log10"] * np.asarray(pv["XtX_inv"], float)
    coef_draws = srng.multivariate_normal(fit_beta, fit_coef_cov, N)
    fit_idio_sd = math.sqrt(pv["noise_var_log10"])
    z_shared = srng.standard_normal(N)          # ONE standardization-gap variate
    pue_groups = {c: _tri(srng, 0.97, 1.0, 1.03) for c in
                  {b["scope_water_footprint"]["scope2_electricity"]["pue_class"] for b in bs}}

    # ---- per-building variates: deterministic per-building seed => identical
    #      across every scenario (common random numbers). Drawn in a FIXED order.
    def bvar(i, b):
        r = np.random.default_rng([SEED, 1000 + i])
        swf = b["scope_water_footprint"]
        s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
        pr = swf["scope2_electricity"]["pue_range"]
        return {
            "z_idio": r.standard_normal(N),
            "apport": _tri(r, 0.90, 1.0, 1.10),
            "wup_tri": _tri(r, s1c["low"], s1c["central"], s1c["high"]),
            "pue_tri": _tri(r, pr[0], (pr[0] + pr[1]) / 2, pr[1]),
            "z_pwr": r.standard_normal(N),
            "z_wup": r.standard_normal(N),
            "z_pue": r.standard_normal(N),
        }

    def power_undisclosed(b, bv):
        pw = b["scope_water_footprint"]["power"]
        ec = pw["effective_it_mw_central"]; gfa = pw.get("gfa_sqft")
        if pw["basis"] == "permit_generator_capacity" or not gfa or ec <= 0:
            return ec * permit_factor * bv["apport"]
        xb = math.log10(gfa); base0 = fit_beta[0] + fit_beta[1] * xb
        syst = (coef_draws[:, 0] + coef_draws[:, 1] * xb) - base0
        return ec * np.power(10.0, syst + fit_idio_sd * bv["z_idio"])

    def county(disclosed, indep, std_gap, disc_pue=False, disc_cool=False, disc_grid=False):
        """disclosed: 'all', a set of ids, or 'none'. indep=verification noise;
        std_gap=standardization-gap sigma (shared). Returns (p50,p5,p95,width%)."""
        blend = blended_central if disc_grid else blended
        county = np.zeros(N)
        for i, b in enumerate(bs):
            bv = bvar(i, b); swf = b["scope_water_footprint"]
            ec = swf["power"]["effective_it_mw_central"]
            show = disclosed == "all" or (disclosed != "none" and b["id"] in disclosed)
            if show:
                eff = ec * (1.0 + indep * bv["z_pwr"]) * (1.0 + std_gap * z_shared)
            else:
                eff = power_undisclosed(b, bv)
            s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
            wup = s1c["central"] * (1.0 + 0.10 * bv["z_wup"]) if disc_cool else bv["wup_tri"] * wup_scale
            s1 = eff * wup / 1e6
            s2e = swf["scope2_electricity"]; pr = s2e["pue_range"]
            pue = ((pr[0] + pr[1]) / 2) * (1.0 + 0.02 * bv["z_pue"]) if disc_pue \
                else bv["pue_tri"] * pue_groups[s2e["pue_class"]]
            s2 = eff * pue * HOURS * blend / 1e6
            county += (s1 + s2) * (1 + s3_frac)
        p5, p50, p95 = np.percentile(county, [5, 50, 95])
        return float(p50), float(p5), float(p95), float((p95 - p5) / p50 * 100)

    def w(disclosed, indep, std_gap, **kw):
        return round(county(disclosed, indep, std_gap, **kw)[3], 1)

    base_w = w("none", 0, 0)

    # ---- the three mechanisms, as distinct scenarios (full-fleet power) --------
    mechanisms = {
        "baseline": base_w,
        "transparency_only":                 w("all", UNVERIFIED_NOISE, MODELED_STD_GAP),
        "transparency_plus_standardization": w("all", UNVERIFIED_NOISE, 0.0),
        "transparency_std_verification":     w("all", VERIFIED_NOISE, 0.0),
    }

    # ---- standardization-gap sensitivity (MODELED, swept) ---------------------
    std_gap_sweep = {f"std_gap_{int(s*100)}pct": w("all", UNVERIFIED_NOISE, s)
                     for s in (0.0, 0.05, 0.10, 0.15)}

    # ---- facility vs grid, under full transparency+std+verification -----------
    facility_vs_grid = {
        "power":              w("all", VERIFIED_NOISE, 0.0),
        "power_pue":          w("all", VERIFIED_NOISE, 0.0, disc_pue=True),
        "power_pue_cooling":  w("all", VERIFIED_NOISE, 0.0, disc_pue=True, disc_cool=True),
        "power_pue_cooling_grid": w("all", VERIFIED_NOISE, 0.0, disc_pue=True, disc_cool=True, disc_grid=True),
    }

    # ---- which buildings first (perfect info = T+S+V), largest footprint ------
    fitted = sorted((b for b in bs if b["scope_water_footprint"]["power"]["basis"] == "fitted_gfa_model"
                     and b["scope_water_footprint"]["power"].get("gfa_sqft")),
                    key=lambda b: -b["scope_water_footprint"]["power"]["gfa_sqft"])
    tot_gfa = sum(b["scope_water_footprint"]["power"]["gfa_sqft"] for b in fitted)
    curve = [{"n": 0, "pct_gfa": 0.0, "ci_pct": base_w}]
    for k in (5, 10, 20, 30, 50, 75, 100, 150, len(fitted)):
        ids = {b["id"] for b in fitted[:k]}
        share = sum(b["scope_water_footprint"]["power"]["gfa_sqft"] for b in fitted[:k]) / tot_gfa
        curve.append({"n": min(k, len(fitted)), "pct_gfa": round(100 * share, 1),
                      "ci_pct": w(ids, VERIFIED_NOISE, 0.0)})

    out = {
        "counterfactual_definition": (
            "A 'disclosed' building holds its power central fixed and replaces its inferred-power "
            "uncertainty with reported-number uncertainty. Three mechanisms are separated: "
            "TRANSPARENCY (published at all), STANDARDIZATION (same definition/time-window across "
            "facilities -> removes a SHARED error that does not average down), and VERIFICATION "
            "(independently checkable -> smaller INDEPENDENT error). The standardization gap is a "
            "MODELED parameter (swept), not measured. Scenarios use common random numbers."),
        "three_mechanisms_ci_width_pct": mechanisms,
        "standardization_gap_sensitivity_ci_width_pct_MODELED": std_gap_sweep,
        "facility_vs_grid_ci_width_pct_perfect_info": facility_vs_grid,
        "which_buildings_first_perfect_info": curve,
        "headline": (
            f"Separating the mechanisms: today's county 90% CI is +/-{base_w/2:.0f}%. TRANSPARENCY "
            f"alone (published but with a modeled ~{int(MODELED_STD_GAP*100)}% standardization gap, "
            f"unverified) reaches only +/-{mechanisms['transparency_only']/2:.0f}%. Adding "
            f"STANDARDIZATION -> +/-{mechanisms['transparency_plus_standardization']/2:.0f}%; adding "
            f"VERIFICATION -> +/-{mechanisms['transparency_std_verification']/2:.0f}%. So most of the "
            f"value is in standardization+verification, not the act of publishing. And even perfect "
            f"facility disclosure stalls at +/-{facility_vs_grid['power_pue_cooling']/2:.0f}% because "
            f"Scope 2 (~87% of the footprint) is bound by the GRID's water-intensity, not a facility "
            f"attribute; resolving that reaches +/-{facility_vs_grid['power_pue_cooling_grid']/2:.0f}%. "
            f"The largest gap is at the power plant, not the data center."),
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print(out["headline"], "\n")
    print("THREE MECHANISMS (county 90% CI, ±%):")
    for k, v in mechanisms.items():
        print(f"  {k:<34} +/-{v/2:.0f}%")
    print("\nStandardization-gap sensitivity (MODELED, transparency+unverified, ±%):")
    for k, v in std_gap_sweep.items():
        print(f"  {k:<20} +/-{v/2:.0f}%")
    print("\nFacility vs grid, perfect info (±%):")
    for k, v in facility_vs_grid.items():
        print(f"  {k:<26} +/-{v/2:.0f}%")
    print("\nWhich buildings first (perfect info):")
    for c in curve:
        print(f"  n={c['n']:>3}  {c['pct_gfa']:>5.0f}% GFA  +/-{c['ci_pct']/2:.0f}%")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
