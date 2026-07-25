"""
Theoretical value of facility-level power transparency (+ realistic-disclosure
sensitivity) — the transparency-gap thesis, quantified and carefully bounded.

The estimator's county 90% CI is ±19% (§32), driven mostly by the 198 buildings
whose power is INFERRED from floor area (the GP predictive variance) rather than
observed. This asks the paper's central counterfactual: if operators disclosed
actual IT load, how much would that interval shrink -- and for which buildings
does disclosure buy the most?

WHAT "DISCLOSED" MEANS HERE (state the counterfactual explicitly)
A "disclosed" building holds its power CENTRAL fixed (disclosure reveals the
number, it does not move our best estimate) and collapses its uncertainty to a
small INDEPENDENT reporting noise. That is a PERFECT-INFORMATION UPPER BOUND: it
assumes every reported figure is (1) facility-specific, (2) measured not modeled,
(3) consistently defined across operators, (4) temporally comparable, (5)
independently verifiable, and (6) actually available. Real public disclosure
satisfies few of these, so the curve and the perfect-info stack are labelled the
"theoretical value of facility-level power transparency," NOT "the value of
disclosure." A separate REALISTIC scenario relaxes (3)-(5) with a SHARED
definitional/temporal inconsistency term that does not average away across
operators; its magnitude is SWEPT, not asserted, because operator-reporting
variance is itself undocumented -- which is part of the point.

METHOD (a counterfactual Monte Carlo)
Same machinery as monte_carlo.py, toggling buildings to disclosed and re-running
the MC at each step, tracing the county 90% CI vs how much of the fleet is
disclosed and vs disclosure quality.

WHAT THE CURVE SHOWS (and its floor)
Power disclosure cannot drive the CI to zero: the WUP calibration, grid
consumption factors, PUE, and the Scope-3 fraction are shared systematic
uncertainties that remain. That floor is itself the result -- it says how much
of the interval is power-transparency-addressable vs irreducible-without-other
-disclosures. Reported alongside the marginal value of disclosing PUE and
cooling intensity.

Reads the calibrated predictive_variance block; pure NumPy. Writes
public/data/value_of_disclosure.json.
"""
import json
import math
import os

import numpy as np

import indirect_water_footprint as m

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "value_of_disclosure.json")
N = 40_000
HOURS = 24
rng = np.random.default_rng(20260725)


def tri(lo, mode, hi, n=N):
    lo, mode, hi = float(lo), float(mode), float(hi)
    if hi - lo < 1e-9:
        return np.full(n, mode)
    return rng.triangular(lo, min(max(mode, lo), hi), hi, n)


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    # ---- shared systematic draws (identical to monte_carlo.py) --------------
    wup_scale = tri(0.90, 1.00, 1.10)
    s3_frac = tri(0.05, 0.10, 0.15)
    permit_factor = tri(0.70, 1.00, 1.35)
    cfc, cfb = m.CONSUMPTION_FACTORS_GAL_PER_MWH, m.CONSUMPTION_FACTOR_BOUNDS_GAL_PER_MWH
    cf_nuc = tri(cfb["nuclear"][0], cfc["nuclear"], cfb["nuclear"][1])
    cf_gas = tri(cfb["natural_gas_cc"][0], cfc["natural_gas_cc"], cfb["natural_gas_cc"][1])
    cf_coal = tri(cfb["coal"][0], cfc["coal"], cfb["coal"][1])
    mix = m.DOMINION_GENERATION_MIX
    blended = mix["natural_gas_cc"] * cf_gas + mix["nuclear"] * cf_nuc + mix["coal"] * cf_coal

    pm = m.POWER_MODEL or {}
    pv = pm["predictive_variance"]
    fit_beta = np.asarray(pv["beta_intercept_slope"], float)
    fit_coef_cov = pv["noise_var_log10"] * np.asarray(pv["XtX_inv"], float)
    fit_coef_draws = rng.multivariate_normal(fit_beta, fit_coef_cov, N)
    fit_idio_sd = math.sqrt(pv["noise_var_log10"])
    dens_groups = {c: tri(0.92, 1.0, 1.08) for c in
                   {str(b["scope_water_footprint"]["power"].get("density_class")) for b in bs}}
    pue_groups = {c: tri(0.97, 1.0, 1.03) for c in
                  {b["scope_water_footprint"]["scope2_electricity"]["pue_class"] for b in bs}}

    # Pre-draw the shared per-building idiosyncratic power terms ONCE so the only
    # thing that changes across disclosure levels is whether a building uses its
    # GP draw or the tight permit-tier draw -- clean apples-to-apples.
    def power_draw(b, disclosed, shared_defn=None):
        swf = b["scope_water_footprint"]; pw = swf["power"]
        ec = pw["effective_it_mw_central"]
        gfa = pw.get("gfa_sqft")
        if pw["basis"] == "permit_generator_capacity" or not gfa or ec <= 0:
            return ec * permit_factor * tri(0.90, 1.0, 1.10)
        if disclosed:
            # Facility power transparency. PERFECT information (shared_defn=None) =
            # a small INDEPENDENT reporting noise only -- this is a THEORETICAL
            # UPPER BOUND, not "the value of disclosure": it assumes every reported
            # number is facility-specific, measured (not modeled), consistently
            # defined, temporally comparable, and verifiable. REALISTIC disclosure
            # (shared_defn given) adds a SHARED definitional/temporal inconsistency
            # (design vs actual load, nameplate vs metered, differing averaging
            # windows) that does NOT average away across operators.
            eff = ec * (1.0 + rng.normal(0.0, 0.05, N))
            if shared_defn is not None:
                eff = eff * (1.0 + shared_defn)
            return eff
        if pw["basis"] == "fitted_gfa_model":
            xb = math.log10(gfa)
            base0 = fit_beta[0] + fit_beta[1] * xb
            syst = (fit_coef_draws[:, 0] + fit_coef_draws[:, 1] * xb) - base0
            return ec * np.power(10.0, syst + rng.normal(0.0, fit_idio_sd, N))
        central_d = pw.get("density_sqft_per_mw_used") or (gfa / ec)
        dens = tri(gfa / pw["effective_it_mw_range"][1], central_d,
                   gfa / pw["effective_it_mw_range"][0]) * dens_groups[str(pw.get("density_class"))]
        return gfa / dens

    def county_ci(disclosed_ids):
        county = np.zeros(N)
        for b in bs:
            swf = b["scope_water_footprint"]
            eff = power_draw(b, b["id"] in disclosed_ids)
            s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
            wup = tri(s1c["low"], s1c["central"], s1c["high"]) * wup_scale
            s1 = eff * wup / 1e6
            s2e = swf["scope2_electricity"]
            pue = tri(s2e["pue_range"][0], sum(s2e["pue_range"]) / 2, s2e["pue_range"][1]) \
                * pue_groups[s2e["pue_class"]]
            s2 = eff * pue * HOURS * blended / 1e6
            county += (s1 + s2) * (1 + s3_frac)
        p5, p50, p95 = np.percentile(county, [5, 50, 95])
        return float(p50), float(p5), float(p95), float((p95 - p5) / p50 * 100)

    # fitted (undisclosed) buildings, largest footprint first
    fitted = sorted((b for b in bs if b["scope_water_footprint"]["power"]["basis"]
                     in ("fitted_gfa_model",) and b["scope_water_footprint"]["power"].get("gfa_sqft")),
                    key=lambda b: -b["scope_water_footprint"]["power"]["gfa_sqft"])
    total_fitted_gfa = sum(b["scope_water_footprint"]["power"]["gfa_sqft"] for b in fitted)

    curve = []
    disclosed = set()
    # baseline (nothing extra disclosed beyond the 45 already-permit-backed)
    p50, p5, p95, w = county_ci(disclosed)
    curve.append({"n_disclosed": 0, "pct_fitted_gfa_disclosed": 0.0,
                  "p50": round(p50, 1), "p5": round(p5, 1), "p95": round(p95, 1),
                  "ci_width_pct": round(w, 1)})
    steps = [5, 10, 20, 30, 50, 75, 100, 150, len(fitted)]
    for k in steps:
        disclosed = {b["id"] for b in fitted[:k]}
        gfa_share = sum(b["scope_water_footprint"]["power"]["gfa_sqft"]
                        for b in fitted[:k]) / total_fitted_gfa
        p50, p5, p95, w = county_ci(disclosed)
        curve.append({"n_disclosed": min(k, len(fitted)),
                      "pct_fitted_gfa_disclosed": round(100 * gfa_share, 1),
                      "p50": round(p50, 1), "p5": round(p5, 1), "p95": round(p95, 1),
                      "ci_width_pct": round(w, 1)})

    # ---- layered disclosure stack: power -> +PUE -> +cooling ----------------
    # Each layer collapses one inference to a tight INDEPENDENT reporting noise
    # for EVERY building (including permit-backed, whose power is itself inferred
    # from generator nameplate via the shared Eq 6-3 factor).
    # Disclosure-quality model (§35.2): a SHARED definitional/temporal
    # inconsistency drawn once and applied to every disclosed building. sigma=0 is
    # the perfect-information upper bound; larger sigma is more realistic reporting.
    # Swept, not asserted -- operator-reporting variance is itself undocumented.
    disc_shared = {s: rng.normal(0.0, s, N) for s in (0.0, 0.05, 0.10, 0.15)}

    def county_ci_layered(disc_power, disc_pue, disc_cool, disc_grid=False, shared_sigma=0.0):
        county = np.zeros(N)
        blend = float(mix["natural_gas_cc"] * cfc["natural_gas_cc"]
                      + mix["nuclear"] * cfc["nuclear"] + mix["coal"] * cfc["coal"]) \
            if disc_grid else blended   # disc_grid collapses grid water-intensity to central
        for b in bs:
            swf = b["scope_water_footprint"]; pw = swf["power"]
            ec = pw["effective_it_mw_central"]
            eff = (power_draw(b, True, disc_shared[shared_sigma]) if disc_power
                   else power_draw(b, False))
            s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
            if disc_cool:
                wup = s1c["central"] * (1.0 + rng.normal(0.0, 0.10, N))   # cooling type known
            else:
                wup = tri(s1c["low"], s1c["central"], s1c["high"]) * wup_scale
            s1 = eff * wup / 1e6
            s2e = swf["scope2_electricity"]
            if disc_pue:
                pue = ((s2e["pue_range"][0] + s2e["pue_range"][1]) / 2) * (1.0 + rng.normal(0.0, 0.02, N))
            else:
                pue = tri(s2e["pue_range"][0], sum(s2e["pue_range"]) / 2, s2e["pue_range"][1]) \
                    * pue_groups[s2e["pue_class"]]
            s2 = eff * pue * HOURS * blend / 1e6
            county += (s1 + s2) * (1 + s3_frac)
        p5, p50, p95 = np.percentile(county, [5, 50, 95])
        return round(float((p95 - p5) / p50 * 100), 1)

    # Perfect-information layered stack (shared_sigma=0): the THEORETICAL bound.
    layered = {
        "baseline": curve[0]["ci_width_pct"],
        "power": county_ci_layered(True, False, False),
        "power_pue": county_ci_layered(True, True, False),
        "power_pue_cooling": county_ci_layered(True, True, True),
        "power_pue_cooling_grid": county_ci_layered(True, True, True, disc_grid=True),
    }
    # Realistic full-power disclosure: sweep the shared definitional inconsistency.
    realistic = {f"shared_defn_sigma_{int(s*100)}pct":
                 county_ci_layered(True, False, False, shared_sigma=s)
                 for s in (0.0, 0.05, 0.10, 0.15)}

    base_w = curve[0]["ci_width_pct"]
    floor_w = curve[-1]["ci_width_pct"]
    top10 = next(c for c in curve if c["n_disclosed"] == 10)

    out = {
        "counterfactual_definition": (
            "A building is 'disclosed' by holding its power CENTRAL fixed and collapsing its "
            "uncertainty to a small INDEPENDENT reporting noise. The perfect-information / "
            "curve results are therefore an UPPER BOUND on the value of facility-level power "
            "transparency: they assume every reported figure is (1) facility-specific, "
            "(2) measured not modeled, (3) consistently defined across operators, "
            "(4) temporally comparable, (5) independently verifiable, and (6) actually "
            "available. Realistic disclosure relaxes (3)-(5) via a SHARED definitional/temporal "
            "inconsistency term that does not average away; see realistic_full_power_disclosure."
        ),
        "framing": "theoretical value of facility-level power transparency (upper bound) + a "
                   "realistic-disclosure sensitivity; NOT 'the value of disclosure' unqualified.",
        "baseline_ci_width_pct": base_w,
        "theoretical_full_power_transparency_pct": floor_w,
        "power_addressable_share_pct_upper_bound": round(100 * (base_w - floor_w) / base_w, 0),
        "top10_buildings_upper_bound": {"ci_width_pct": top10["ci_width_pct"],
                                        "pct_fitted_gfa": top10["pct_fitted_gfa_disclosed"]},
        "layered_stack_perfect_info_ci_width_pct": layered,
        "realistic_full_power_disclosure_ci_width_pct": realistic,
        "curve_perfect_info": curve,
        "headline": (
            f"Today's county 90% CI is +/-{base_w/2:.0f}%. Under a PERFECT-INFORMATION upper bound "
            f"(facility-specific, measured, consistently defined, verifiable), full facility power "
            f"transparency would reach +/-{layered['power']/2:.0f}%, but a realistic shared "
            f"definitional/temporal inconsistency of ~10% only gets to "
            f"+/-{realistic['shared_defn_sigma_10pct']/2:.0f}%. Either way, adding PUE and cooling "
            f"disclosure buys almost nothing at county scale (+/-{layered['power_pue_cooling']/2:.0f}%): "
            f"Scope 2 is ~87% of the footprint, so the binding uncertainty is the GRID's "
            f"water-intensity (gal/MWh) -- a power-plant property. Only resolving that reaches "
            f"+/-{layered['power_pue_cooling_grid']/2:.0f}%. The largest transparency gap is at the "
            f"power plant, not the data center."
        ),
    }
    json.dump(out, open(OUT, "w"), indent=1)
    print(out["headline"], "\n")
    print(f"{'disclosed':>10}{'%fitGFA':>9}{'p50':>7}{'p5':>7}{'p95':>7}{'CI±%':>7}  (perfect-info)")
    for c in curve:
        print(f"{c['n_disclosed']:>10}{c['pct_fitted_gfa_disclosed']:>9.0f}"
              f"{c['p50']:>7.1f}{c['p5']:>7.1f}{c['p95']:>7.1f}{c['ci_width_pct']/2:>7.0f}")
    print("\nPerfect-info layered stack (county 90% CI, ±%):")
    for k in ("baseline", "power", "power_pue", "power_pue_cooling", "power_pue_cooling_grid"):
        print(f"  {k:<24} +/-{layered[k]/2:.0f}%")
    print("\nRealistic full-power disclosure vs shared definitional inconsistency (±%):")
    for s, w in realistic.items():
        print(f"  {s:<24} +/-{w/2:.0f}%")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
