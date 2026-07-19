"""
Monte Carlo uncertainty for the Scope 1/2/3 estimator.

The shipped range is an ENVELOPE -- the sum of each scope's independent min and
max. That is a conservative outer bound, not a probability. It cannot say "the
county total is very likely between X and Y", because it treats every parameter
as simultaneously at its worst, which never happens. This replaces it with a
proper distribution: sample every parameter from its own distribution many
times, propagate through the same arithmetic, and read off percentiles.

Two design choices make this honest rather than decorative:

1. FACILITY-CENTRIC PRIORS. Each building samples from a distribution keyed to
   its OWN evidence, not a shared average. A building whose power comes from a
   VADEQ permit samples a tight Equation 6-3 factor; one on floor area samples
   its operator's measured density band; one carrying an operator's published
   fleet PUE samples a narrow band while a vintage-classed one samples a wide
   one. Better evidence -> narrower prior -> narrower interval, per building.

2. CORRELATION. The parameters that are shared across buildings are drawn ONCE
   per iteration and applied to all -- the grid's water intensity (one grid),
   the ICPRB WUP calibration (one scale), the Scope 3 proportion (one
   assumption), and a per-operator / per-class density and PUE calibration
   offset. If these were drawn independently per building, 243 independent
   errors would cancel and the county interval would collapse to a spuriously
   tight number. Systematic uncertainty does not average away, and this keeps
   it from doing so. Idiosyncratic, building-specific variation is drawn
   independently and correctly does average down.

Writes per-facility p5/p50/p95 back into facility_profiles.json and a
county-level summary. Run AFTER build_facility_profiles.py.
"""
import json
import os

import numpy as np

import indirect_water_footprint as m

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_ROOT = os.environ.get("VIRA_OUT_ROOT", os.path.join(_SCRIPT_DIR, "public", "data"))
PROFILES = os.path.join(OUT_ROOT, "facility_profiles.json")
N = 40_000
HOURS = 24
rng = np.random.default_rng(20260719)


def tri(lo, mode, hi, n=N):
    """Triangular draw that degrades gracefully when the three collapse."""
    lo, mode, hi = float(lo), float(mode), float(hi)
    if hi - lo < 1e-9:
        return np.full(n, mode)
    mode = min(max(mode, lo), hi)
    return rng.triangular(lo, mode, hi, n)


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    # ---- systematic draws: one vector each, shared by every building ---------
    wup_scale = tri(0.90, 1.00, 1.10)            # ICPRB WUP scale calibration
    s3_frac = tri(0.05, 0.10, 0.15)              # one proportional assumption
    # ICPRB's Eq 6-3 factor (0.5 redundancy x 0.8 utilization = 0.40) is a shared
    # standard, so its uncertainty is systematic across every permit-backed
    # building, not independent. Plausible spans (redundancy 0.4-0.6, utilization
    # 0.7-0.9) give 0.28-0.54, i.e. a ratio of 0.70-1.35 about the 0.40 central.
    permit_factor = tri(0.70, 1.00, 1.35)

    # Consumption factors drawn from the estimator's own central + reanalysis
    # bounds, so the Monte Carlo can never drift from the deterministic constants.
    cfc, cfb = m.CONSUMPTION_FACTORS_GAL_PER_MWH, m.CONSUMPTION_FACTOR_BOUNDS_GAL_PER_MWH
    cf_nuc = tri(cfb["nuclear"][0], cfc["nuclear"], cfb["nuclear"][1])
    cf_gas = tri(cfb["natural_gas_cc"][0], cfc["natural_gas_cc"], cfb["natural_gas_cc"][1])
    cf_coal = tri(cfb["coal"][0], cfc["coal"], cfb["coal"][1])
    mix = m.DOMINION_GENERATION_MIX
    blended_avg = mix["natural_gas_cc"] * cf_gas + mix["nuclear"] * cf_nuc + mix["coal"] * cf_coal
    mm = m.PJM_MARGINAL_FUEL_MIX
    blended_marg = mm["natural_gas_cc"] * cf_gas + mm["coal"] * cf_coal + mm["natural_gas_ct"] * 20.0

    # per-group calibration offsets (drawn once per group, shared within it)
    dens_groups = {c: tri(0.92, 1.0, 1.08) for c in
                   {str(b["scope_water_footprint"]["power"].get("density_class")) for b in bs}}
    pue_groups = {c: tri(0.97, 1.0, 1.03) for c in
                  {b["scope_water_footprint"]["scope2_electricity"]["pue_class"] for b in bs}}

    county = np.zeros(N)
    county_marg = np.zeros(N)
    for b in bs:
        swf = b["scope_water_footprint"]
        pw = swf["power"]
        elo, ec, ehi = (pw["effective_it_mw_range"][0], pw["effective_it_mw_central"],
                        pw["effective_it_mw_range"][1])

        # POWER -- facility-centric, sampled in each basis's NATURAL parameter
        # space so the median tracks the deterministic central (sampling MW
        # directly over the skewed 1/density range would bias the mean up).
        gfa = pw.get("gfa_sqft")
        if pw["basis"] == "permit_generator_capacity" or not gfa or elo <= 0:
            # Systematic Eq 6-3 factor (shared) x small independent apportionment
            # of the site's generator capacity among co-permitted buildings.
            eff = ec * permit_factor * tri(0.90, 1.0, 1.10)
        else:
            # Uncertainty is on density (sqft/MW). ehi MW <-> densest (min
            # sqft/MW); elo MW <-> sparsest (max sqft/MW). Sampling density and
            # dividing keeps the median at gfa/central_d = central.
            central_d = pw.get("density_sqft_per_mw_used") or (gfa / ec)
            dens = tri(gfa / ehi, central_d, gfa / elo) * dens_groups[str(pw.get("density_class"))]
            eff = gfa / dens

        # SCOPE 1 -- facility's own WUP tier (narrowed if it has a cooling
        # commitment) times the shared ICPRB calibration.
        s1c = swf["scope1_onsite_cooling"]["wup_gal_per_mw_day"]
        wup = tri(s1c["low"], s1c["central"], s1c["high"]) * wup_scale
        s1 = eff * wup / 1e6

        # SCOPE 2 -- facility PUE (tight if operator-disclosed) x shared grid
        # intensity. Grid intensity is the dominant county-level correlation.
        s2e = swf["scope2_electricity"]
        pue = tri(s2e["pue_range"][0], sum(s2e["pue_range"]) / 2, s2e["pue_range"][1]) \
            * pue_groups[s2e["pue_class"]]
        s2 = eff * pue * HOURS * blended_avg / 1e6
        s2m = eff * pue * HOURS * blended_marg / 1e6

        s3 = (s1 + s2) * s3_frac
        total = s1 + s2 + s3
        county += total
        county_marg += s1 + s2m + (s1 + s2m) * s3_frac

        p5, p50, p95 = np.percentile(total, [5, 50, 95])
        swf["uncertainty"] = {
            "method": "monte_carlo",
            "iterations": N,
            "total_mgd_p5": round(float(p5), 4),
            "total_mgd_p50": round(float(p50), 4),
            "total_mgd_p95": round(float(p95), 4),
            "relative_width_pct": round(float((p95 - p5) / p50 * 100), 0) if p50 else None,
        }

    def pct(a):
        return [round(float(x), 2) for x in np.percentile(a, [5, 50, 95])]

    env_lo = sum(b["scope_water_footprint"]["total_mgd_range"][0] for b in bs)
    env_hi = sum(b["scope_water_footprint"]["total_mgd_range"][1] for b in bs)
    summary = {
        "method": "monte_carlo",
        "iterations": N,
        "county_total_mgd_p5_p50_p95": pct(county),
        "county_total_marginal_mgd_p5_p50_p95": pct(county_marg),
        "shipped_envelope_mgd": [round(env_lo, 2), round(env_hi, 2)],
        "note": (
            "Monte Carlo over facility-centric priors with systematic parameters "
            "(grid intensity, WUP calibration, Scope 3 fraction, per-group density/PUE "
            "offsets) drawn once per iteration and shared across buildings, so correlated "
            "uncertainty does not average away. The envelope is the min/max outer bound "
            "for comparison; the p5-p95 is the actual 90% credible interval."
        ),
    }
    d["monte_carlo_summary"] = summary
    with open(PROFILES, "w") as f:
        json.dump(d, f, separators=(",", ":"), default=str, allow_nan=False)

    c = summary["county_total_mgd_p5_p50_p95"]
    cm = summary["county_total_marginal_mgd_p5_p50_p95"]
    print(f"County total (average mix):  {c[1]:.1f} MGD   90% CI [{c[0]:.1f}, {c[2]:.1f}]"
          f"   (+/-{(c[2]-c[0])/2/c[1]*100:.0f}%)")
    print(f"County total (marginal mix): {cm[1]:.1f} MGD   90% CI [{cm[0]:.1f}, {cm[2]:.1f}]")
    print(f"Shipped envelope (min/max):  [{env_lo:.1f}, {env_hi:.1f}]  -- outer bound, not a CI")
    widths = [b["scope_water_footprint"]["uncertainty"]["relative_width_pct"] for b in bs]
    print(f"\nPer-facility 90% interval width (p95-p5)/p50:")
    print(f"  narrowest {min(widths):.0f}%   median {np.median(widths):.0f}%   widest {max(widths):.0f}%")
    perm = [b["scope_water_footprint"]["uncertainty"]["relative_width_pct"] for b in bs
            if b["scope_water_footprint"]["power"]["basis"] == "permit_generator_capacity"]
    gfa = [b["scope_water_footprint"]["uncertainty"]["relative_width_pct"] for b in bs
           if b["scope_water_footprint"]["power"]["basis"] != "permit_generator_capacity"]
    print(f"  permit-backed buildings:  median {np.median(perm):.0f}%   ({len(perm)} buildings)")
    print(f"  floor-area buildings:     median {np.median(gfa):.0f}%   ({len(gfa)} buildings)")
    print(f"\nWrote per-facility CIs + summary into {PROFILES}")


if __name__ == "__main__":
    main()
