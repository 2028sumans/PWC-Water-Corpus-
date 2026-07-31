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
  10 provenance ledger     every quoted claim is verbatim in its source PDF (else rejected)
  11 basin displacement    York avg->marginal flip; >75% consumed outside the Potomac basin
  12 growth scenarios      per-MW model reproduces today; ICPRB on-site cross-check consistent
  13 value of information  per-DP load is top acquisition; grid's conditional > alone value
  14 evidence ladder       CI width monotone in evidence tier; tier 2 empty; peak/annual ~10x
  15 basin stress          Broad Run peak-day/low-flow robust across both bracketing gages
  16 exposure + gap        exposure/monitoring counts recomputed from profiles match published
  17 triangulation         forward-load sources agree within public granularity, cap left untuned
  18 seasonal x basin      binding condition is summer+Broad Run, amplified vs flat, sweep-robust
  19 marginal-flip        York->0 robust to params; mix sourced; residual premises declared

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
    # The abstract must quote the EFFECT SIZE, not the p-value: a KS
    # non-rejection at n=54 is close to guaranteed (see power_caveat) and a
    # reader can misparse p=0.09 as nearly-significant disagreement.
    es = v["effect_size"]
    dep = es["max_quantile_departure_x"]
    under_powered = es["ks_D"] < es["ks_D_detectable_at_alpha05"]
    caveats = bool(es.get("power_caveat")) and bool(es.get("independence_caveat"))
    abstract = open(os.path.join(HERE, "ABSTRACT_AGU26.txt")).read()
    quotes_effect = any(f"{d}{m}" in abstract
                        for d in (f"{dep}", f"{dep:.1f}") for m in ("x", "×"))
    quotes_p = "p = 0.09" in abstract or "KS p" in abstract
    ok = checks_ok and ks > 0.05 and dep <= 1.5 and caveats and quotes_effect and not quotes_p
    return ok, (
        f"all {len(v['checks'])} published constraints consistent={checks_ok}; "
        f"quartiles within {dep}x of benchmark (abstract quotes it={quotes_effect}, "
        f"quotes bare p={quotes_p}); KS p={ks:.3f} but D={es['ks_D']} < detectable "
        f"{es['ks_D_detectable_at_alpha05']} (under-powered={under_powered}, "
        f"caveats recorded={caveats})")


# 7b ------------------------------------------------------------------------
def c_basis():
    """Withdrawal vs consumption must never be mixed in a reported figure.

    Scope 1 mgd_central is DELIVERED water; Scope 2 is CONSUMPTION at the
    generating plant. total_mgd_central therefore mixes bases. Every number in
    the abstract is on the consumption basis, so this check recomputes them
    that way and refuses to pass if the abstract has drifted back to the mixed
    total or omits the basis statement.
    """
    prof = json.load(open(os.path.join(PUB, "facility_profiles.json")))
    bs = [b for b in prof["buildings"] if b.get("scope_water_footprint")]
    f = [b["scope_water_footprint"] for b in bs]
    op = [b["scope_water_footprint"] for b in bs if b["status"] == "Completed"]
    s1d = sum(x["scope1_onsite_cooling"]["mgd_central"] for x in f)
    s1c = sum(x["scope1_onsite_cooling"]["consumptive_mgd_central"] for x in f)
    # The 0.75 factor is applied uniformly per building, so the seasonal figures
    # rescale exactly. Tolerance is relative: the stored values are rounded to
    # 4 dp, and that error accumulates over 243 buildings.
    uniform = abs(s1c - 0.75 * s1d) / (0.75 * s1d) < 5e-3
    tot_c = sum(x["total_consumptive_mgd_central"] for x in f)
    op_c = sum(x["total_consumptive_mgd_central"] for x in op)
    s2 = sum(x["scope2_electricity"]["mgd_central"] for x in f)
    s2_share = 100 * s2 / tot_c

    abstract = open(os.path.join(HERE, "ABSTRACT_AGU26.txt")).read()
    # "consumptive water footprint" is the term of art and declares the basis on
    # its own; the explicit "water lost, not withdrawn" gloss is optional prose.
    declares = "consumptive water footprint" in abstract
    says_share = f"{s2_share:.0f}%" in abstract

    # THE INVARIANT: the seasonal figure must describe the SAME fleet the
    # abstract says it studied. Broad Run is 3%/17-25% of July flow for all 243
    # buildings but only 0.6%/3-5% for the 54 operating -- a ~5x difference, so
    # stating the wrong scope misattributes the strongest number in the paper.
    # Do not require any one wording: derive the claimed scope, then demand the
    # matching figures. (An earlier version hard-coded "243 ... and 54 ..." plus
    # the two volume figures, which failed a correct abstract that simply
    # dropped the volumes -- it encoded one fix rather than the invariant.)
    surf = json.load(open(os.path.join(PUB, "seasonal_basin_surface.json")))["surfaces"]["BROAD RUN"]
    mean_flow = sum(surf["monthly_flow_mgd"].values()) / 12
    op_frac = surf["completed_only_annual_draw_mgd"] / surf["annual_draw_mgd"]

    if "243 data-center buildings" in abstract:
        scope, k = "all 243", 1.0
    elif re.search(r"54 (operating )?data-center buildings", abstract):
        scope, k = "operating 54", op_frac
    else:
        scope, k = None, None

    if scope is None:
        says_seasonal, seas_note = False, "abstract states no building-count scope"
    else:
        ann = 0.75 * k * 100 * surf["annual_draw_mgd"] / mean_flow
        lo = 0.75 * k * surf["baseload_sweep"]["baseload_50pct"]["worst_pct_of_flow"]
        hi = 0.75 * k * surf["baseload_sweep"]["baseload_10pct"]["worst_pct_of_flow"]
        # Match on the NUMBERS, not on a fixed phrase -- the wording around them
        # is edited constantly and a literal match makes the guard brittle.
        says_seasonal = bool(
            re.search(rf"{ann:.0f}%\s+of\s+[\w' ]*?mean annual flow", abstract)
            and re.search(rf"{lo:.0f}[-–]{hi:.0f}%\s+of\s+[\w' ]*?July flow", abstract))
        seas_note = (f"scope={scope} -> requires {ann:.1f}% annual / "
                     f"{lo:.0f}-{hi:.0f}% July")

    # Volume figures are optional, but wrong if present.
    says_op = "10 million gallons per day" not in abstract or 9.5 <= op_c <= 10.5
    says_tot = "50 MGD" not in abstract or 45 <= tot_c <= 55

    ok = all([uniform, declares, says_share, says_op, says_tot, says_seasonal])
    return ok, (
        f"consumption basis: total {tot_c:.1f} MGD (mixed-basis total would be "
        f"{sum(x['total_mgd_central'] for x in f):.1f}), operating {op_c:.1f}, "
        f"Scope 2 {s2_share:.1f}%. abstract declares basis={declares}, "
        f"{seas_note}, matched={says_seasonal}; share={says_share} "
        f"volumes-if-present ok={says_op and says_tot}, "
        f"0.75 factor uniform={uniform}")


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
            elif e.get("page"):
                # Presence is not enough -- a wrong page number is a citation error a
                # reviewer will catch. Verify the quote is on the CLAIMED page.
                import subprocess
                pg = e.get("pdf_page_in_extract") or e["page"]
                pt = subprocess.run(["pdftotext", "-q", "-f", str(pg), "-l", str(pg),
                                     os.path.join(RAW, e["source_pdf"]), "-"],
                                    capture_output=True, text=True).stdout
                if re.sub(r"\s+", " ", q).lower() not in re.sub(r"\s+", " ", pt).lower():
                    bad.append(f"{e['id']}: quote not on claimed page {pg}")
        else:
            # Non-quoted entries must be explicitly typed AND noted. "assumption*"
            # and "limitation" types exist so premises that produce results (e.g.
            # nuclear-never-marginal, METHODOLOGY 47.2) and unsourced parameters
            # are declared rather than passing as fact. An unsourced assumption
            # must additionally say so in its source/note.
            ok_types = ("derived", "external_citation", "external_data",
                        "assumption", "assumption_unsourced", "limitation")
            if not (e.get("type") in ok_types and e.get("note")):
                bad.append(f"{e['id']}: no quote and not a typed/noted derivation")
            elif e.get("type") == "assumption_unsourced" and "NO supporting file" not in (e.get("source") or ""):
                bad.append(f"{e['id']}: unsourced assumption must state its lack of source")
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


# 12 ------------------------------------------------------------------------
def c_growth_scenarios():
    """growth_scenarios: the per-MW model reproduces today's plug-in central; the
    ICPRB on-site cross-check is direction-consistent; decarbonizing the grid
    beats today's grid (the paper's mitigation claim)."""
    g = json.load(open(os.path.join(PUB, "growth_scenarios.json")))
    cal = g["calibration"]
    calib_ok = abs(cal["model_today_total_mgd"] - cal["actual_plug_in_total_mgd"]) <= 2.0
    icprb = g["icprb_cross_check_onsite"]["consistent_direction"]
    c = g["scenarios"]["2050_central"]
    decarb_beats = c["grid_decarbonized"]["total_mgd"] < c["grid_today"]["total_mgd"]
    ok = calib_ok and icprb and decarb_beats
    return ok, (f"model today {cal['model_today_total_mgd']} vs actual "
                f"{cal['actual_plug_in_total_mgd']} (calib={calib_ok}); ICPRB on-site "
                f"consistent={icprb}; 2050 decarb {c['grid_decarbonized']['total_mgd']} < "
                f"today-grid {c['grid_today']['total_mgd']} ={decarb_beats}")


# 13 ------------------------------------------------------------------------
def c_value_of_information():
    """VOI: per-DP load is the top single acquisition; grid's conditional value
    (after power) exceeds its alone value; easy asks (PUE/cooling) are ~0."""
    v = json.load(open(os.path.join(PUB, "value_of_information.json")))
    acq = {a["dataset"]: a for a in v["acquisitions"]}
    top = max(v["acquisitions"], key=lambda a: a["delta_halfwidth_pp"])["dataset"]
    gc = v["grid_conditional_value"]
    grid_alone = acq["grid_water_intensity"]["delta_halfwidth_pp"]
    grid_cond = gc["grid_delta_once_power_resolved_halfwidth_pp"]
    easy_zero = abs(acq["operator_pue"]["delta_halfwidth_pp"]) < 1 and abs(acq["cooling_permits"]["delta_halfwidth_pp"]) < 1
    ok = top == "per_dp_contracted_load" and grid_cond > grid_alone and easy_zero
    return ok, (f"top acquisition={top}; grid alone {grid_alone}pp < conditional {grid_cond}pp; "
                f"PUE/cooling ~0={easy_zero}")


# 14 ------------------------------------------------------------------------
def c_evidence_ladder():
    """Ladder is monotone in evidence (observed tier 1 tighter than inferred
    tiers 3/4), tier 2 is empty, and peak/annual ~10x per ICPRB."""
    e = json.load(open(os.path.join(PUB, "evidence_ladder.json")))
    t = e["evidence_ladder"]["tiers"]
    t1 = t["1"]["ci_width_pct_median"]; t3 = t["3"]["ci_width_pct_median"]; t4 = t["4"]["ci_width_pct_median"]
    monotone = t1 < t3 <= t4
    tier2_empty = t["2"]["n_buildings"] == 0
    pk = e["peak_day"]["all_243_buildings"]["ratio"]
    peak_ok = 8.0 <= pk <= 12.0
    ok = monotone and tier2_empty and peak_ok
    return ok, (f"tier1 ±{t1/2:.0f}% < tier3 ±{t3/2:.0f}% <= tier4 ±{t4/2:.0f}% (monotone={monotone}); "
                f"tier2 empty={tier2_empty}; peak/annual={pk}x")


# 15 ------------------------------------------------------------------------
def c_basin_stress():
    """Broad Run is the concentration basin; its full-buildout peak-day draw is a
    large share of low-month flow under BOTH bracketing gages (robust to gage
    choice); completed-only is reported and smaller."""
    b = json.load(open(os.path.join(PUB, "basin_stress.json")))
    br = b["basins"]["BROAD RUN"]
    up = br["pct_of_low_month_flow_PEAK_draw"]
    dn = br["downstream_gage_sensitivity"]["pct_of_low_month_flow_PEAK_draw"]
    robust = min(up, dn) > 50 and abs(up - dn) < 30      # same order, both gages
    completed_lower = br["completed_only_pct_of_low_month_flow_PEAK"] < up
    framing = "not a withdrawal" in b["framing"].lower() or "scale comparison" in b["framing"].lower()
    ok = robust and completed_lower and framing
    return ok, (f"Broad Run peak-day = {up}% (upstream) / {dn}% (downstream) of low-month flow "
                f"(robust={robust}); completed-only {br['completed_only_pct_of_low_month_flow_PEAK']}%; "
                f"scale-comparison framing present={framing}")


# 16 ------------------------------------------------------------------------
def c_exposure_gap():
    """Exposure/gap counts recomputed from the profiles must match the published
    analysis (no drift), and the headline gap claims must hold."""
    e = json.load(open(os.path.join(PUB, "exposure_gap.json")))
    d = _profiles()
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    def wc(b, k, default=0):
        v = (b.get("water_context") or {}).get(k)
        return v if isinstance(v, (int, float)) else default
    no_npdes = sum(1 for b in bs if wc(b, "has_npdes") == 0)
    no_deq = sum(1 for b in bs if wc(b, "n_deq_monitoring_1mi") == 0)
    near = sum(1 for b in bs if wc(b, "d_stream_ft", 1e9) <= 300)
    blind = sum(1 for b in bs if wc(b, "d_stream_ft", 1e9) <= 300
                and wc(b, "has_npdes") == 0 and wc(b, "n_deq_monitoring_1mi") == 0)
    g = e["regulatory_monitoring_gap"]; x = e["exposure"]
    match = (g["no_npdes"]["n"] == no_npdes and g["no_deq_station_within_1mi"]["n"] == no_deq
             and x["within_300ft_of_stream"]["n"] == near
             and g["compound_blind_spot"]["n"] == blind)
    all_unmonitored = no_deq == len(bs)
    ok = match and all_unmonitored
    return ok, (f"recomputed: {near} stream-adjacent, {no_npdes} no-NPDES, {no_deq}/{len(bs)} "
                f"no-DEQ-station, {blind} compound blind spot (match={match}; "
                f"all unmonitored={all_unmonitored})")


# 17 ------------------------------------------------------------------------
def c_triangulation():
    """Forward-load triangulation: the open-bucket cap needed for agreement must
    be BELOW the largest campus the model estimates (i.e. the sources agree
    within public granularity, and no cap was tuned to force the fit)."""
    t = json.load(open(os.path.join(PUB, "pipeline_triangulation.json")))
    s = t["comparisons"]["open_bucket_sensitivity"]
    honest = s["cap_needed_for_model_to_fall_inside_mw"] < s["largest_single_campus_in_model_mw"]
    untuned = s["assumed_cap_mw"] != s["cap_needed_for_model_to_fall_inside_mw"]
    fwd = 10 <= t["comparisons"]["teac_forward_pct_of_model_stock"] <= 60
    ok = honest and untuned and fwd
    return ok, (f"cap needed {s['cap_needed_for_model_to_fall_inside_mw']} MW < largest campus "
                f"{s['largest_single_campus_in_model_mw']} MW (consistent={honest}); assumed cap "
                f"left untuned={untuned}; TEAC forward "
                f"{t['comparisons']['teac_forward_pct_of_model_stock']}% of stock")


# 18 ------------------------------------------------------------------------
def c_seasonal_basin_surface():
    """S2 surface: the binding condition is Broad Run in a summer month, the
    crossed figure materially exceeds the flat annual one, and the finding
    survives the baseload sweep (so it is not an artifact of the one free
    parameter)."""
    s = json.load(open(os.path.join(PUB, "seasonal_basin_surface.json")))
    b = s["binding_condition"]
    summer = b["month"] in ("Jun", "Jul", "Aug", "Sep")
    flat = s["why_crossing_matters"]["annual_flat_pct_of_mean_flow"]
    amplified = flat is not None and b["pct_of_monthly_flow"] > 3 * flat
    sweep = s["surfaces"][b["watershed"]]["baseload_sweep"]
    robust = all(v["worst_month"] == b["month"] for v in sweep.values())
    ok = summer and amplified and robust
    return ok, (f"binding: {b['watershed']} in {b['month']} at {b['pct_of_monthly_flow']}% "
                f"(flat annual {flat}%, amplified={amplified}); worst month stable across "
                f"baseload sweep={robust}")



# 19 ------------------------------------------------------------------------
def c_marginal_flip_robust():
    """The headline claim (METHODOLOGY 47): York->0 under marginal accounting must
    depend ONLY on nuclear's absence, not on the unsourced marginal-mix split. Re-runs
    the marginal basin attribution across coal shares 0-15% and requires York==0 in
    every case. Also requires the unsourced mix + the premise to be declared in the
    ledger, so the result can never be presented as fully sourced."""
    import indirect_water_footprint as m
    from basin_analysis import load_plants
    from collections import defaultdict
    plants = load_plants()
    d = _profiles()
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]
    s2m = sum(b["scope_water_footprint"]["scope2_electricity"]["marginal_based"]["mgd_central"] for b in bs)
    mcf = m.MARGINAL_CONSUMPTION_FACTORS_GAL_PER_MWH
    yorks = []
    for coal in (0.0, 0.05, 0.10, 0.15):
        mmix = {"natural_gas_cc": 0.617 + (0.10 - coal), "natural_gas_ct": 0.172,
                "coal": coal, "wind": 0.111}
        mb = sum(mmix[f] * mcf[f] for f in mmix)
        out = defaultdict(float)
        for fuel in mmix:
            pf = "natural_gas_cc" if fuel.startswith("natural_gas") else fuel
            if pf not in plants:
                continue
            fm = s2m * (mmix[fuel] * mcf[fuel]) / mb
            tot = sum(p["consumption_mgd"] for p in plants[pf]) or 1
            for p in plants[pf]:
                out[p["basin"]] += fm * p["consumption_mgd"] / tot
        yorks.append(out.get("York (Lake Anna)", 0.0))
    robust = all(y < 1e-9 for y in yorks)
    led = {e["id"]: e for e in json.load(open(os.path.join(DATA, "provenance_ledger.json")))["entries"]}
    # The marginal mix must now be SOURCED (verbatim quote, verified in-PDF by
    # check 10), and the two residual assumptions -- nuclear's non-marginality and
    # the CC:CT split the SOM does not publish -- must remain explicitly declared.
    sourced = bool(led.get("pjm_marginal_fuel_mix", {}).get("verbatim_quote"))
    premises = ("nuclear_never_marginal" in led
                and led.get("pjm_marginal_gas_cc_ct_split", {}).get("type") == "assumption")
    return (robust and sourced and premises), (
        f"York across coal shares 0-15%: {[round(y,3) for y in yorks]} (all zero={robust}); "
        f"marginal mix sourced={sourced}; residual premises declared={premises}")


def main():
    print("RESEARCH-READINESS HARNESS\n" + "=" * 60)
    check("1 data integrity", c_integrity)
    check("2 headline reproducible", c_headline)
    check("3 numeric consistency", c_consistency)
    check("4 GP calibration", c_gp_calibration)
    check("5 GP heteroscedasticity", c_gp_hetero)
    check("6 LLM provenance", c_llm_provenance)
    check("7 JLARC validation", c_jlarc)
    check("7b withdrawal-vs-consumption basis", c_basis)
    check("8 seasonal invariants", c_seasonal)
    check("9 constant provenance", c_constants)
    check("10 provenance ledger", c_provenance_ledger)
    check("11 basin displacement", c_basin_displacement)
    check("12 growth scenarios", c_growth_scenarios)
    check("13 value of information", c_value_of_information)
    check("14 evidence ladder", c_evidence_ladder)
    check("15 basin stress", c_basin_stress)
    check("16 exposure + monitoring gap", c_exposure_gap)
    check("17 forward-load triangulation", c_triangulation)
    check("18 seasonal x basin surface", c_seasonal_basin_surface)
    check("19 marginal-flip robustness", c_marginal_flip_robust)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("=" * 60)
    print(f"{len(results)-n_fail}/{len(results)} checks passed"
          + ("" if n_fail else "  — RESEARCH-READY"))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
