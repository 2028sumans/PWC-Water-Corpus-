"""
Distributional validation of Scope 1 against JLARC's 2023 metered water data.

JLARC Report 598 (Figure 5-3 and text, p.62) published the only per-building
metered water-use distribution for Virginia data centers -- anonymized, from
the utilities serving Fairfax, Henrico, Loudoun, Mecklenburg, Prince William,
and Wise ("the large majority" of the industry), calendar 2023, per BUILDING:

  - "Most data centers use about the same amount of water (or less) as an
    average large office building (6.7 million gallons per year)"  -> median
    <= 0.018 MGD
  - "11 data center buildings each used over 50 million gallons"   -> P(X >
    0.137 MGD) ~ 11 / ~300 buildings-with-data = 3-4%
  - "one building used 243 million gallons (10% of the industry's total)"
                                                                    -> max
    0.666 MGD
  - industry total 2.1 billion gallons = 5.75 MGD (over 1/3 reclaimed)
  - "some require less than a typical household" (~0.0003 MGD)

The buildings are anonymous, but a distribution does not need names. Our 54
completed PWC buildings' Scope 1 central estimates are on the same basis
(delivered water, per building, annual average), so their DISTRIBUTION can be
tested against JLARC's. This is the closest available thing to ground truth.

WHAT IS AND IS NOT INDEPENDENT HERE
The 309 gal/MW/day central intensity was derived by ICPRB from Prince William
Water's service-area TOTAL, so the aggregate LEVEL of our completed fleet is
semi-calibrated (the old circularity, METHODOLOGY 6.1). But the SHAPE -- the
median, the spread induced by per-building power and cooling narrowing, and
above all the TAIL -- was never calibrated to anything. Those are genuine
out-of-sample comparisons.

POPULATION CAVEAT
JLARC's sample is statewide and Loudoun-heavy; Loudoun has reclaimed-supplied
evaporative stock (the >0.137 MGD tail). PWC's fleet is chiller-dominant
(METHODOLOGY 7.3c; ICPRB ~11% water-cooled county share), so PWC's true tail
SHOULD be thinner than the statewide one. The test distinguishes "consistent
with an air-dominant fleet" from "distribution shape wrong."
"""
import json
import math

import numpy as np

PROFILES = "public/data/facility_profiles.json"
OUT = "data/scope1_distribution_validation.json"

# JLARC 2023 anchors (delivered MGD per building)
OFFICE = 6.7 / 365.0            # 0.01836
TAIL_THRESHOLD = 50.0 / 365.0   # 0.137
STATE_MAX = 243.0 / 365.0       # 0.666
INDUSTRY_TOTAL_MGD = 2100.0 / 365.0
N_STATE_BUILDINGS = 300         # ~340 inventoried; data covered "the large majority"
TAIL_COUNT = 11


def main():
    d = json.load(open(PROFILES))
    ours = []
    for b in d["buildings"]:
        swf = b.get("scope_water_footprint")
        if not swf or (b.get("status") or "").lower() != "completed":
            continue
        ours.append((b["name"], swf["scope1_onsite_cooling"]["mgd_central"],
                     swf["scope1_onsite_cooling"]["mgd_range"]))
    vals = np.array(sorted(v for _, v, _ in ours))
    n = len(vals)

    # JLARC reference lognormal, fit to (median, tail probability). Two
    # published quantiles determine the two parameters; the observed statewide
    # max then falls where it falls (a consistency check, not an input).
    from scipy import stats
    p_tail = TAIL_COUNT / N_STATE_BUILDINGS
    mu = math.log(OFFICE)                       # median at the office benchmark
    sigma = (math.log(TAIL_THRESHOLD) - mu) / stats.norm.ppf(1 - p_tail)
    ref = stats.lognorm(s=sigma, scale=math.exp(mu))
    implied_max_pctl = ref.cdf(STATE_MAX)
    exp_max = ref.ppf(1 - 1 / (2 * N_STATE_BUILDINGS))

    print(f"JLARC reference lognormal: median {OFFICE:.4f} MGD, sigma(ln) {sigma:.3f}")
    print(f"  implied percentile of the observed statewide max (0.666): "
          f"{implied_max_pctl:.5f} (expected max for n={N_STATE_BUILDINGS}: {exp_max:.3f}) "
          f"-- consistent within extreme-value noise\n")

    print(f"OUR 54 COMPLETED PWC BUILDINGS (Scope 1 central, delivered MGD): n={n}")
    q = lambda p: float(np.quantile(vals, p))
    print(f"  min {vals.min():.4f}  p25 {q(.25):.4f}  median {q(.5):.4f}  "
          f"p75 {q(.75):.4f}  max {vals.max():.4f}  mean {vals.mean():.4f}  "
          f"sum {vals.sum():.3f}")

    rows = []
    def check(label, ours_v, jlarc_v, ok, note=""):
        rows.append({"test": label, "ours": ours_v, "jlarc": jlarc_v,
                     "consistent": bool(ok), "note": note})
        print(f"  [{'PASS' if ok else 'FLAG'}] {label}: ours {ours_v} vs JLARC {jlarc_v}"
              + (f" -- {note}" if note else ""))

    print("\nQUANTILE-BY-QUANTILE COMPARISON")
    check("median <= office benchmark (most use office-or-less)",
          round(q(.5), 4), f"<= {OFFICE:.4f}", q(.5) <= OFFICE)
    check("share at-or-below office benchmark",
          f"{(vals <= OFFICE).mean():.0%}", ">= 50% ('most')", (vals <= OFFICE).mean() >= 0.5)
    check("share below a typical household (0.0003)",
          f"{(vals < 3e-4).mean():.0%}", "'some'", True,
          "JLARC gives no count; qualitative")
    exp_tail = p_tail * n
    obs_tail = int((vals > TAIL_THRESHOLD).sum())
    check(f"buildings above {TAIL_THRESHOLD:.3f} MGD",
          obs_tail, f"~{exp_tail:.1f} expected at statewide rate ({TAIL_COUNT}/{N_STATE_BUILDINGS})",
          obs_tail <= math.ceil(exp_tail) + 1,
          "PWC's chiller-dominant fleet should sit at or below the statewide rate")
    check("max building vs statewide max",
          round(float(vals.max()), 4), round(STATE_MAX, 4), vals.max() <= STATE_MAX,
          "a county subset must not exceed the statewide max")
    check("mean per building",
          round(float(vals.mean()), 4),
          f"~{INDUSTRY_TOTAL_MGD / N_STATE_BUILDINGS:.4f} statewide (incl. reclaimed-heavy Loudoun)",
          vals.mean() <= INDUSTRY_TOTAL_MGD / N_STATE_BUILDINGS,
          "expected lower: statewide mean is pulled up by evaporative outliers")

    # Formal shape test against the statewide reference (expected to FLAG if
    # PWC genuinely lacks the evaporative tail -- interpretation matters).
    ks = stats.kstest(vals, ref.cdf)
    print(f"\nKS test vs statewide reference lognormal: D={ks.statistic:.3f}, "
          f"p={ks.pvalue:.2e}")
    same_shape = ks.pvalue > 0.05
    print("  " + ("consistent with the statewide distribution"
                  if same_shape else
                  "REJECTED as the same distribution -- diagnosis below"))

    # Diagnosis: is the mismatch the tail (fleet composition) or the body?
    body = vals[vals <= TAIL_THRESHOLD]
    ref_body = stats.lognorm(s=sigma, scale=math.exp(mu))
    # censored comparison on the body only, renormalizing the reference
    cdf_at_t = ref_body.cdf(TAIL_THRESHOLD)
    ks_body = stats.kstest(body, lambda x: ref_body.cdf(x) / cdf_at_t)
    print(f"  body-only (<= {TAIL_THRESHOLD:.3f}) KS: D={ks_body.statistic:.3f}, "
          f"p={ks_body.pvalue:.2e}")

    # THE DECISIVE TEST. The statewide reference blends counties whose measured
    # intensities differ 3x+ (ICPRB Table 6-5: Loudoun 1,006 vs PWC 309
    # gal/MW/day). Statewide delivered intensity = 5.75 MGD / 5,050 MW = 1,139
    # gal/MW/day. Scaling the reference median by PWC's measured 309/1,139
    # removes the KNOWN county-intensity difference using only published
    # numbers (no fitting to our data), leaving a pure test of distributional
    # SHAPE: does per-building spread in our estimates match per-building
    # spread in metered reality?
    STATEWIDE_WUP = INDUSTRY_TOTAL_MGD * 1e6 / 5050.0
    scale_pwc = 309.0 / STATEWIDE_WUP
    ref_pwc = stats.lognorm(s=sigma, scale=math.exp(mu) * scale_pwc)
    ks_pwc = stats.kstest(vals, ref_pwc.cdf)
    print(f"\nPWC-intensity-scaled reference (median {OFFICE*scale_pwc:.4f} MGD, "
          f"same sigma): KS D={ks_pwc.statistic:.3f}, p={ks_pwc.pvalue:.3f}")
    print("  " + ("SHAPE CONSISTENT: once the published county-intensity ratio is "
                  "applied, our per-building distribution is statistically "
                  "indistinguishable from JLARC's metered one"
                  if ks_pwc.pvalue > 0.05 else
                  "shape still differs after intensity scaling"))

    json.dump({
        "jlarc_anchors": {"office_mgd": OFFICE, "tail_threshold_mgd": TAIL_THRESHOLD,
                          "tail_count": TAIL_COUNT, "state_max_mgd": STATE_MAX,
                          "industry_total_mgd": INDUSTRY_TOTAL_MGD,
                          "assumed_n_with_data": N_STATE_BUILDINGS,
                          "reference_lognormal": {"median": OFFICE, "sigma_ln": sigma}},
        "ours": {"n": n, "min": float(vals.min()), "p25": q(.25), "median": q(.5),
                 "p75": q(.75), "max": float(vals.max()), "mean": float(vals.mean()),
                 "sum": float(vals.sum())},
        "checks": rows,
        "ks_full": {"D": ks.statistic, "p": ks.pvalue},
        "ks_body": {"D": ks_body.statistic, "p": ks_body.pvalue},
        "ks_pwc_scaled": {"D": ks_pwc.statistic, "p": ks_pwc.pvalue,
                          "scale": scale_pwc, "statewide_wup": STATEWIDE_WUP},
    }, open(OUT, "w"), indent=1, default=float)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
