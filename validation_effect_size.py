"""Effect sizes for the JLARC distributional check.

A KS p-value is a failure-to-reject, not evidence of agreement, and at n=54 the
test has little power -- non-rejection is close to expected whatever the truth.
So report HOW CLOSE the distributions are, not whether a test fired:

  - ratio of our median to the benchmark median (and at p25/p75)
  - KS D itself (max CDF gap) alongside the D the test could actually detect
  - the minimum D detectable at alpha=0.05 for this n, so the reader can see
    how much of the non-rejection is power rather than agreement

There is no paired per-building comparison available -- JLARC publishes summary
statistics for the state, not building-level records -- so MAPE against reported
values is not computable. These are distributional effect sizes.

Run with /usr/bin/python3 (needs scipy).
"""
import json
import math

import numpy as np
from scipy import stats

PROFILES = "public/data/facility_profiles.json"
OUT = "data/scope1_distribution_validation.json"

OFFICE = 6.7e6 / 365 / 1e6           # JLARC large-office benchmark, MGD
TAIL_THRESHOLD = 50e6 / 365 / 1e6    # JLARC ">50 MGY" tail threshold, MGD
TAIL_COUNT = 11
N_STATE_BUILDINGS = 300
STATEWIDE_WUP = 1139.2920113929201   # implied statewide gal/MW/day
PWC_WUP = 309.0


def main():
    d = json.load(open(PROFILES))
    vals = np.array(sorted(
        b["scope_water_footprint"]["scope1_onsite_cooling"]["mgd_central"]
        for b in d["buildings"]
        if b.get("scope_water_footprint")
        and (b.get("status") or "").lower() == "completed"
    ))
    n = len(vals)

    p_tail = TAIL_COUNT / N_STATE_BUILDINGS
    mu = math.log(OFFICE)
    sigma = (math.log(TAIL_THRESHOLD) - mu) / stats.norm.ppf(1 - p_tail)
    scale_pwc = PWC_WUP / STATEWIDE_WUP
    ref = stats.lognorm(s=sigma, scale=math.exp(mu) * scale_pwc)

    ks = stats.kstest(vals, ref.cdf)
    # One-sample KS critical value at alpha=.05 (asymptotic, fully specified ref)
    d_crit = 1.358 / math.sqrt(n)

    quantiles = {}
    for p in (0.25, 0.50, 0.75):
        ours = float(np.quantile(vals, p))
        bench = float(ref.ppf(p))
        quantiles[f"p{int(p * 100)}"] = {
            "ours_mgd": round(ours, 5),
            "benchmark_mgd": round(bench, 5),
            "ratio": round(ours / bench, 3),
        }

    med_ratio = quantiles["p50"]["ratio"]
    # Largest quantile-ratio departure from 1.0 across the three quantiles
    worst = max(abs(math.log(q["ratio"])) for q in quantiles.values())

    res = {
        "basis": "Scope 1 delivered MGD, 54 operating buildings",
        "benchmark": (
            "JLARC statewide lognormal (median = large-office 6.7 MGY, sigma from "
            "the 11/300 >50 MGY tail), rescaled by PWC's measured intensity "
            f"{PWC_WUP}/{STATEWIDE_WUP:.0f} = {scale_pwc:.4f}"
        ),
        "n": n,
        "quantile_ratios": quantiles,
        "median_ratio": med_ratio,
        "max_quantile_departure_x": round(math.exp(worst), 3),
        "ks_D": round(float(ks.statistic), 4),
        "ks_p": round(float(ks.pvalue), 4),
        "ks_D_detectable_at_alpha05": round(d_crit, 4),
        "power_caveat": (
            f"At n={n} the smallest CDF gap a KS test can reject at alpha=0.05 is "
            f"D={d_crit:.3f}. The observed D={ks.statistic:.3f} is below that, so "
            f"non-rejection (p={ks.pvalue:.3f}) reflects limited power as much as "
            f"agreement. Report the quantile ratios, not the p-value."
        ),
        "independence_caveat": (
            "Prince William is one of the six localities inside JLARC's own dataset, "
            "so this benchmark is partially, not fully, independent of our county."
        ),
    }

    print(f"n = {n}   benchmark scale = {scale_pwc:.4f}")
    print(f"{'':>6}{'ours':>12}{'benchmark':>12}{'ratio':>8}")
    for k, q in quantiles.items():
        print(f"{k:>6}{q['ours_mgd']:>12.5f}{q['benchmark_mgd']:>12.5f}{q['ratio']:>8.2f}")
    print(f"\nmedian ratio            {med_ratio:.2f}x")
    print(f"largest quantile gap    {res['max_quantile_departure_x']:.2f}x")
    print(f"KS D = {res['ks_D']:.3f}  p = {res['ks_p']:.3f}   "
          f"(detectable at alpha=.05: D >= {d_crit:.3f})")
    print(f"\n{res['power_caveat']}")

    existing = json.load(open(OUT))
    existing["effect_size"] = res
    json.dump(existing, open(OUT, "w"), indent=1)
    print(f"\nwrote effect_size block -> {OUT}")


if __name__ == "__main__":
    main()
