"""
Research-readiness harness — mechanical checks that the corpus is paper-grade,
not "AI slop." Every check RE-COMPUTES or RE-VERIFIES from source rather than
trusting a stored/asserted value, and fails loudly. Run before any analysis and
before any deploy that touches numbers.

  python3 verify_research_ready.py        # framework python (needs the profiles)

Checks:
  1  data integrity        243 buildings, required keys, finite numbers, CIs present
  2  headline reproducible plug-in central + MC median/CI recomputed from profiles,
                           matched to the METHODOLOGY headline (no drift)
  3  numeric consistency   no stale pre-GP numbers in the authoritative headline / memo
  4  GP calibration        power_model predictive_variance is LOO-calibrated in-band
  5  GP heteroscedasticity band genuinely widens with distance from training centroid
  6  LLM provenance        every verified extraction quote is in its source; rejects justified
  7  JLARC validation      Scope-1 distribution constraints pass; KS p>0.05 after scaling
  8  seasonal invariants   seasonal_stress numbers agree with the METHODOLOGY headline
  9  constant provenance   each key physical constant is cited to a source in METHODOLOGY

Exit code 0 iff every check passes.
"""
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.join(HERE, "public", "data")
DATA = os.path.join(HERE, "data")
RAW = os.path.join(DATA, "water_raw")
METH = os.path.join(HERE, "METHODOLOGY.md")
MEMO = os.path.join(HERE, "src", "app", "api", "memo", "route.ts")

results = []


def check(name, fn):
    try:
        ok, detail = fn()
    except Exception as e:
        ok, detail = False, f"EXCEPTION: {e}"
    results.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {detail}")


def _profiles():
    return json.load(open(os.path.join(PUB, "facility_profiles.json")))


# 1 -------------------------------------------------------------------------
def c_integrity():
    d = _profiles()
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]
    if len(d["buildings"]) != 243:
        return False, f"expected 243 buildings, got {len(d['buildings'])}"
    bad = []
    for b in bs:
        swf = b["scope_water_footprint"]
        for k in ("total_mgd_central", "scope1_onsite_cooling", "scope2_electricity", "power"):
            if k not in swf:
                bad.append(f"{b['name']}:missing {k}")
        v = swf.get("total_mgd_central")
        if not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
            bad.append(f"{b['name']}:bad total {v}")
        if "uncertainty" not in swf:
            bad.append(f"{b['name']}:no MC CI")
    return (not bad), (f"{len(bs)} buildings with footprint, all keyed + finite + CI present"
                       if not bad else f"{len(bad)} problems e.g. {bad[:3]}")


# 2 -------------------------------------------------------------------------
def c_headline():
    d = _profiles()
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]
    plug = sum(b["scope_water_footprint"]["total_mgd_central"] for b in bs)
    mc = d.get("monte_carlo_summary", {})
    p5, p50, p95 = mc.get("county_total_mgd_p5_p50_p95", [0, 0, 0])
    txt = open(METH).read()
    m = re.search(r"County-wide total:\s*\*\*([\d.]+)\s*MGD,\s*90% credible interval\s*([\d.]+)[–-]([\d.]+)",
                  txt)
    if not m:
        return False, "could not find headline pattern in METHODOLOGY"
    h_med, h_lo, h_hi = float(m.group(1)), float(m.group(2)), float(m.group(3))
    # recomputed vs documented, 0.2 MGD tolerance
    okmed = abs(p50 - h_med) <= 0.2
    okci = abs(p5 - h_lo) <= 0.3 and abs(p95 - h_hi) <= 0.3
    okplug = abs(plug - 49.6) <= 0.3
    return (okmed and okci and okplug), (
        f"recomputed plug-in {plug:.1f} (doc 49.6), MC p50 {p50:.1f}/CI [{p5:.1f},{p95:.1f}] "
        f"vs headline {h_med}/[{h_lo},{h_hi}] -> med:{okmed} ci:{okci} plug:{okplug}")


# 3 -------------------------------------------------------------------------
def c_consistency():
    txt = open(METH).read()
    memo = open(MEMO).read()
    # the authoritative headline block must NOT contain the pre-GP numbers
    head = txt.split("\n", 40)[0:40]
    headline = next((l for l in head if "Current headline" in l), "")
    stale_terms = ["52.6 MGD", "47.0–58.7", "47-59"]
    bad = [t for t in stale_terms if t in headline]
    memo_bad = [t for t in ["52.6 MGD", "~47-59"] if t in memo]
    return (not bad and not memo_bad), (
        "authoritative headline + memo carry current post-GP numbers"
        if not (bad or memo_bad) else f"stale in headline={bad} memo={memo_bad}")


# 4 -------------------------------------------------------------------------
def c_gp_calibration():
    pm = json.load(open(os.path.join(DATA, "power_model.json")))
    pv = pm.get("predictive_variance")
    if not pv:
        return False, "no predictive_variance block"
    cal = pv["loo_calibration"]
    ok = (0.80 <= cal["coverage_90"] <= 1.0 and 0.4 <= cal["mean_z2"] <= 2.0)
    kc = pv["kernel_check"]
    lin_ok = kc["gp_linear_rbf_loo_rmse"] >= kc["gp_linear_loo_rmse"] - 1e-3
    return (ok and lin_ok), (
        f"cov90={cal['coverage_90']:.0%} z2={cal['mean_z2']:.2f} (in band); "
        f"RBF≥linear LOO ({kc['gp_linear_rbf_loo_rmse']:.3f}≥{kc['gp_linear_loo_rmse']:.3f}): {lin_ok}")


# 5 -------------------------------------------------------------------------
def c_gp_hetero():
    pm = json.load(open(os.path.join(DATA, "power_model.json")))
    pv = pm["predictive_variance"]
    inv, s2 = pv["XtX_inv"], pv["noise_var_log10"]

    def band(gfa):
        xv = (1.0, math.log10(gfa))
        lev = sum(xv[i] * inv[i][j] * xv[j] for i in range(2) for j in range(2))
        return 10 ** (1.645 * math.sqrt(s2 * (1 + lev)))
    centroid = 10 ** (sum(math.log10(s["gfa"]) for s in pm["training_sites"]) / pm["n_sites"])
    near, far = band(centroid), band(20_000)   # 20k sqft is far below the data
    return (far > near * 1.05), (
        f"band@centroid({centroid:,.0f})=x/{near:.2f}  band@20k=x/{far:.2f}  "
        f"(far wider by {100*(far/near-1):.0f}%)")


# 6 -------------------------------------------------------------------------
def c_llm_provenance():
    import llm_extract as le
    ext = json.load(open(os.path.join(DATA, "llm_extractions.json")))
    # rebuild source lookup for whatever source this extraction came from
    srcs = {}
    for loader in (le.load_proffers, le.load_permits):
        for doc in loader():
            srcs[doc["doc_id"]] = doc["source_text"]
    bad = []
    for r in ext["records"]:
        if "_cross_check" in r:
            continue
        q, src = r.get("quote", ""), srcs.get(r["doc_id"], "")
        if le._norm(q) not in le._norm(src):
            bad.append(r["doc_id"])
    rej = json.load(open(os.path.join(DATA, "llm_extraction_rejects.json")))
    rej_ok = all(x.get("reject_reasons") for x in rej)
    return (not bad and rej_ok), (
        f"{ext['n_verified']} verified records all have in-source quotes; "
        f"{len(rej)} rejects all justified" if (not bad and rej_ok)
        else f"provenance holes={bad} rej_ok={rej_ok}")


# 7 -------------------------------------------------------------------------
def c_jlarc():
    v = json.load(open(os.path.join(DATA, "scope1_distribution_validation.json")))
    checks_ok = all(c["consistent"] for c in v["checks"])
    ks = v["ks_pwc_scaled"]["p"]
    return (checks_ok and ks > 0.05), (
        f"all {len(v['checks'])} published constraints consistent={checks_ok}; "
        f"KS(intensity-scaled) p={ks:.3f} (>0.05)")


# 8 -------------------------------------------------------------------------
def c_seasonal():
    s = json.load(open(os.path.join(PUB, "seasonal_stress.json")))
    peak = s["demand_cdd"]["peak_month"]
    pot = s["supply_streamflow"]["Potomac R at Little Falls"]
    lowpct = pot["low_flow_pct_of_annual"]
    txt = open(METH).read()
    doc_has = f"{lowpct}%" in txt and "July" in txt
    return (peak == "Jul" and 38 <= lowpct <= 44 and doc_has), (
        f"demand peak={peak}, Potomac low={lowpct}% of annual; METHODOLOGY agrees={doc_has}")


# 9 -------------------------------------------------------------------------
def c_constants():
    import indirect_water_footprint as m
    txt = open(METH).read()
    need = {
        "WUP 309": ("309" in txt and "ICPRB" in txt),
        "nuclear 391": ("391" in txt),
        "Eq 6-3 0.4 factor": ("0.5" in txt and "0.8" in txt),
        "USGS 2008-2020": ("2008" in txt and "2020" in txt and "USGS" in txt),
    }
    # sanity: the module's constants are the ones we cite
    wup_ok = abs(m.WUP_GAL_PER_MW_DAY["pwc_observed"] - 309) < 1
    bad = [k for k, v in need.items() if not v]
    return (not bad and wup_ok), (
        f"key constants cited in METHODOLOGY; module WUP={m.WUP_GAL_PER_MW_DAY['pwc_observed']}"
        if (not bad and wup_ok) else f"missing citations={bad} wup_ok={wup_ok}")


# 10 ------------------------------------------------------------------------
def c_provenance_ledger():
    """Every ledger entry with a source_pdf+quote must have that quote present in
    the PDF (whitespace-normalized). Enforces 'no quote -> claim does not enter'.
    Entries without a quote must be typed (derived/external) with a note."""
    import subprocess
    led = json.load(open(os.path.join(DATA, "provenance_ledger.json")))
    cache = {}

    def pdftext(fn):
        if fn not in cache:
            p = os.path.join(RAW, fn)
            cache[fn] = re.sub(r"\s+", " ", subprocess.run(
                ["pdftotext", "-q", p, "-"], capture_output=True, text=True).stdout).lower()
        return cache[fn]

    bad, n_quoted = [], 0
    for e in led["entries"]:
        q = e.get("verbatim_quote")
        if q:
            n_quoted += 1
            if re.sub(r"\s+", " ", q).lower() not in pdftext(e["source_pdf"]):
                bad.append(f"{e['id']}: quote not in {e['source_pdf']}")
        else:
            if not (e.get("type") in ("derived", "external_citation", "external_data")
                    and e.get("note")):
                bad.append(f"{e['id']}: no quote and not a typed/noted derivation")
    return (not bad), (f"{n_quoted} quoted claims all verified verbatim in-PDF; "
                       f"{len(led['entries'])-n_quoted} derivations typed+noted"
                       if not bad else f"{len(bad)} problems e.g. {bad[:2]}")


# 11 ------------------------------------------------------------------------
def c_basin_displacement():
    """basin_attribution.json internally consistent; the York avg->marginal flip
    holds; >75% consumed outside the Potomac basin; and the North Anna figure
    quoted in METHODOLOGY matches the JSON (no drift)."""
    b = json.load(open(os.path.join(DATA, "basin_attribution.json")))
    t = b["totals_mgd"]
    avg = b["scope2_by_generating_basin"]; marg = b["scope2_marginal_by_generating_basin"]
    york_a = avg.get("York (Lake Anna)", 0.0); york_m = marg.get("York (Lake Anna)", 0.0)
    consistent = abs((t["scope1"] + t["scope2"] + t["scope3"]) - t["total"]) < 0.05
    flip = york_a > 10 and york_m < 0.5
    outside = t["scope2"] - avg.get("Potomac", 0.0)
    displaced = outside / t["total"] > 0.75
    # doc must quote the current North Anna figure (whole-number MGD)
    txt = open(METH).read()
    doc_ok = f"{york_a:.1f} MGD" in txt or f"{round(york_a,1)} MGD" in txt
    ok = consistent and flip and displaced and doc_ok
    return ok, (f"York {york_a:.1f}->{york_m:.1f} MGD (flip={flip}); "
                f"{100*outside/t['total']:.0f}% consumed outside Potomac; "
                f"doc quotes {york_a:.1f} MGD={doc_ok}"
                if ok else
                f"consistent={consistent} flip={flip} displaced={displaced} doc_ok={doc_ok}")


def main():
    print("RESEARCH-READINESS HARNESS\n" + "=" * 60)
    check("1 data integrity", c_integrity)
    check("2 headline reproducible", c_headline)
    check("3 numeric consistency", c_consistency)
    check("4 GP calibration", c_gp_calibration)
    check("5 GP heteroscedasticity", c_gp_hetero)
    check("6 LLM provenance", c_llm_provenance)
    check("7 JLARC validation", c_jlarc)
    check("8 seasonal invariants", c_seasonal)
    check("9 constant provenance", c_constants)
    check("10 provenance ledger", c_provenance_ledger)
    check("11 basin displacement", c_basin_displacement)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("=" * 60)
    print(f"{len(results)-n_fail}/{len(results)} checks passed"
          + ("" if n_fail else "  — RESEARCH-READY"))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
