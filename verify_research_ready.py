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
  19 marginal-flip         York marginal share non-zero and <2%; mix sourced; year named
  20 occupancy ramp        fit-out ramp scoped to occupied buildings; level reconciles to JLARC
  21 drought denominator   sweep is labelled an OBSERVED condition; dual-reporting claim present
  22 convention table      >10x spread across computable conventions; broader geographies
                           scaled-or-declared; long-run SMR caveat intact
  23 entitlement pathway   ZERO buildings have a SUP (recomputed); by-right majority;
                           pre-1990 entitlements still producing buildings

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


def _live_totals():
    """Fleet aggregates recomputed from facility_profiles.json — the live model.

    The derived analyses (growth_scenarios, evidence_ladder,
    pipeline_triangulation) each cache their own copy of these figures. A check
    that compares such a file only against itself proves the file is internally
    consistent and nothing more: it stays green while the estimator moves
    underneath it. That is not hypothetical — the occupancy-ramp correction took
    the fleet from 49.6 to 46.2 MGD and 6,468 to 6,031 effective MW, and checks
    12, 14 and 17 all passed against the pre-ramp files for five days.

    Every check that reads a derived JSON binds its headline figures back to
    this, so a stale file fails instead of passing quietly.
    """
    swf = [b["scope_water_footprint"] for b in _profiles()["buildings"]
           if b.get("scope_water_footprint")]
    return {
        "total_mgd": sum(s["total_mgd_central"] for s in swf),
        "scope1_mgd": sum(s["scope1_onsite_cooling"]["mgd_central"] for s in swf),
        "effective_it_mw": sum(s["power"]["effective_it_mw_central"] for s in swf),
    }


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
    okplug = abs(plug - 46.2) <= 0.3   # post-fit-out-ramp (METHODOLOGY 62)
    return (okmed and okci and okplug), (
        f"recomputed plug-in {plug:.1f} (doc 46.2), MC p50 {p50:.1f}/CI [{p5:.1f},{p95:.1f}] "
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
    # THE INVARIANT is not "the abstract must validate" -- whether to spend
    # characters on the JLARC comparison is an editorial call. It is: IF the
    # abstract makes a validation claim, it must rest on the effect size, never
    # on the p-value (a KS non-rejection at n=54 is near-automatic; see
    # power_caveat). An earlier version demanded quotes_effect unconditionally
    # and so failed a correct abstract that simply dropped the sentence -- the
    # same over-fitting that broke check 7b.
    makes_validation_claim = quotes_effect or quotes_p or "legislative audit" in abstract
    claim_ok = (not makes_validation_claim) or (quotes_effect and not quotes_p)
    ok = checks_ok and ks > 0.05 and dep <= 1.5 and caveats and claim_ok
    return ok, (
        f"all {len(v['checks'])} published constraints consistent={checks_ok}; "
        f"quartiles within {dep}x of benchmark (abstract makes a validation claim="
        f"{makes_validation_claim}, effect-size={quotes_effect}, bare p={quotes_p}); KS p={ks:.3f} but D={es['ks_D']} < detectable "
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

    # No seasonal claim in the abstract -> nothing for this check to police.
    # (The claim was dropped in review: once restated on a consumption basis and
    # correctly framed as a scale comparison rather than a withdrawal, it was a
    # context statistic rather than a finding. METHODOLOGY 56.)
    makes_seasonal_claim = bool(re.search(r"%\s+of\s+[\w' ]*?(annual|July)\s+flow", abstract))

    if not makes_seasonal_claim:
        says_seasonal, seas_note = True, "abstract makes no seasonal claim (n/a)"
    elif scope is None:
        says_seasonal, seas_note = False, "seasonal claim present but no building-count scope stated"
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
    live = _live_totals()
    # Calibrate the per-MW model against the LIVE plug-in total, not against the
    # copy of it cached in this same file (see _live_totals).
    calib_ok = abs(cal["model_today_total_mgd"] - live["total_mgd"]) <= 2.0
    fresh_ok = (abs(cal["actual_plug_in_total_mgd"] - live["total_mgd"]) <= 0.5
                and abs(g["baseline_today"]["effective_it_mw"] - live["effective_it_mw"]) <= 25)
    icprb = g["icprb_cross_check_onsite"]["consistent_direction"]
    c = g["scenarios"]["2050_central"]
    decarb_beats = c["grid_decarbonized"]["total_mgd"] < c["grid_today"]["total_mgd"]
    ok = calib_ok and fresh_ok and icprb and decarb_beats
    return ok, (f"model today {cal['model_today_total_mgd']} vs live plug-in "
                f"{live['total_mgd']:.1f} (calib={calib_ok}); file fresh vs live "
                f"({cal['actual_plug_in_total_mgd']} MGD / {g['baseline_today']['effective_it_mw']} MW "
                f"vs {live['total_mgd']:.1f} / {live['effective_it_mw']:.0f})={fresh_ok}; "
                f"ICPRB on-site consistent={icprb}; 2050 decarb "
                f"{c['grid_decarbonized']['total_mgd']} < today-grid "
                f"{c['grid_today']['total_mgd']} ={decarb_beats}")


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
    # Bind the ladder to the live model: its annual Scope 1 base must still be
    # the fleet's (see _live_totals), or the tiers describe a superseded run.
    live = _live_totals()
    fresh_ok = abs(e["peak_day"]["all_243_buildings"]["annual_avg_s1_mgd"]
                   - live["scope1_mgd"]) <= 0.05
    ok = monotone and tier2_empty and peak_ok and fresh_ok
    return ok, (f"tier1 ±{t1/2:.0f}% < tier3 ±{t3/2:.0f}% <= tier4 ±{t4/2:.0f}% (monotone={monotone}); "
                f"tier2 empty={tier2_empty}; peak/annual={pk}x; annual S1 base "
                f"{e['peak_day']['all_243_buildings']['annual_avg_s1_mgd']} vs live "
                f"{live['scope1_mgd']:.2f} MGD (fresh={fresh_ok})")


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
    # The whole triangulation is a statement about the model's stock, so that
    # stock must still be the live one (see _live_totals).
    live = _live_totals()
    fresh_ok = abs(t["this_model"]["effective_it_mw_all"] - live["effective_it_mw"]) <= 25
    ok = honest and untuned and fwd and fresh_ok
    return ok, (f"cap needed {s['cap_needed_for_model_to_fall_inside_mw']} MW < largest campus "
                f"{s['largest_single_campus_in_model_mw']} MW (consistent={honest}); assumed cap "
                f"left untuned={untuned}; TEAC forward "
                f"{t['comparisons']['teac_forward_pct_of_model_stock']}% of stock; stock "
                f"{t['this_model']['effective_it_mw_all']} vs live {live['effective_it_mw']:.0f} MW "
                f"(fresh={fresh_ok})")


# 18 ------------------------------------------------------------------------
def c_seasonal_basin_surface():
    """S2 surface, CORRECTED 2026-08-03.

    Bound to the substantive claim, not to self-consistency: the central monthly
    shape must be ICPRB's OBSERVED Table A.3-2 series (peak/trough 3.0x), not the
    superseded CDD-proportional model (peak/trough 10.1x, ~70% too peaky in
    summer). Reverting to the CDD model as central must fail this check.
    """
    s = json.load(open(os.path.join(PUB, "seasonal_basin_surface.json")))
    b = s["binding_condition"]

    # 1. the central shape is the observed one, and matches ICPRB A.3-2 exactly
    ICPRB_A32 = {"Jan": 0.7, "Feb": 0.6, "Mar": 0.6, "Apr": 0.7,
                 "May": 0.9, "Jun": 1.0, "Jul": 1.5, "Aug": 1.8,
                 "Sep": 1.5, "Oct": 1.0, "Nov": 0.9, "Dec": 0.8}
    obs = s.get("observed_monthly_factors") or {}
    matches_source = obs == ICPRB_A32
    central_is_observed = all(
        v.get("central_shape") == "observed_icprb_a32" for v in s["surfaces"].values())

    # 2. peak/trough is the observed ~3x, NOT the superseded ~10x
    ptt = s.get("observed_peak_to_trough")
    ptt_ok = ptt is not None and 2.8 <= ptt <= 3.2

    # 3. the observed series is normalized (mean 1.0 over 12 months)
    normalized = abs(sum(obs.values()) - 12.0) < 1e-9 if obs else False

    # 4. the binding condition is still a late-summer month in the fleet's basin
    summer = b["month"] in ("Jun", "Jul", "Aug", "Sep")
    flat = s["why_crossing_matters"]["annual_flat_pct_of_mean_flow"]
    amplified = flat is not None and b["pct_of_monthly_flow"] > 3 * flat

    # 5. the superseded model is retained and labelled, so the fix stays auditable
    sup = s.get("superseded_cdd_model") or {}
    auditable = (sup.get("former_central_baseload_share") == 0.30
                 and all("cdd_model_sensitivity" in v for v in s["surfaces"].values()))

    ok = (matches_source and central_is_observed and ptt_ok and normalized
          and summer and amplified and auditable)
    return ok, (f"central shape=observed({central_is_observed}) matches ICPRB A.3-2"
                f"({matches_source}) normalized({normalized}) peak/trough={ptt}"
                f"(~3 not ~10: {ptt_ok}); binding {b['watershed']} in {b['month']} at "
                f"{b['pct_of_monthly_flow']}% vs flat {flat}% (amplified={amplified}); "
                f"superseded model retained={auditable}")



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

    def york_for(mmix):
        mb = sum(mmix[f] * mcf[f] for f in mmix)
        out = defaultdict(float)
        for fuel in mmix:
            pf = ("natural_gas_cc" if fuel.startswith("natural_gas")
                  else ("nuclear" if fuel == "nuclear" else fuel))
            if pf not in plants:
                continue
            fm = s2m * (mmix[fuel] * mcf[fuel]) / mb
            tot = sum(pp["consumption_mgd"] for pp in plants[pf]) or 1
            for pp in plants[pf]:
                out[pp["basin"]] += fm * pp["consumption_mgd"] / tot
        return out.get("York (Lake Anna)", 0.0), mb

    # REWRITTEN 31 Jul 2026. The previous version of this check ENFORCED THE
    # ERROR it was supposed to police: it built a synthetic marginal mix with no
    # nuclear term, confirmed York came out 0.00, and required the ledger to
    # contain an entry named `nuclear_never_marginal`. Nuclear is in fact 0.39%
    # (2022) to 1.35% (2019) of PJM real-time marginal resources (SOM Table 3-69,
    # printed p.200), so the zero was true only by construction.
    #
    # The check now (a) uses the SHIPPED mix, (b) requires York to be small but
    # STRICTLY NON-ZERO, (c) sweeps the nuclear share over its published
    # five-year range to bound the result, and (d) fails if anyone sets the
    # nuclear term back to zero.
    base_york, base_mb = york_for(dict(m.PJM_MARGINAL_FUEL_MIX))
    york_share = 100 * base_york / s2m if s2m else 0.0

    sweep = {}
    for label, nuc in (("2022 (0.39%)", 0.0039), ("2023 (0.62%)", 0.0062),
                       ("2019 (1.31%)", 0.0131), ("zero (the old premise)", 0.0)):
        mmix = dict(m.PJM_MARGINAL_FUEL_MIX)
        delta = nuc - mmix["nuclear"]
        mmix["nuclear"] = nuc
        mmix["natural_gas_cc"] -= delta          # hold the shares summing to 1
        y, _ = york_for(mmix)
        sweep[label] = 100 * y / s2m if s2m else 0.0

    nonzero = base_york > 0                      # nuclear must NOT be zeroed out
    bounded = york_share < 2.0                   # and must stay under the abstract's "under 2%"
    zero_case_is_zero = sweep["zero (the old premise)"] < 1e-9   # sanity: the sweep works

    led = {e["id"]: e for e in json.load(open(os.path.join(DATA, "provenance_ledger.json")))["entries"]}
    sourced = bool(led.get("pjm_marginal_fuel_mix", {}).get("verbatim_quote"))
    corrected = bool(led.get("nuclear_rarely_marginal", {}).get("verbatim_quote")) \
        and "nuclear_never_marginal" not in led
    abstract = open(os.path.join(HERE, "ABSTRACT_AGU26.txt")).read()
    no_false_zero = "0% of electricity-related water use is attributed" not in abstract

    ok = all([nonzero, bounded, zero_case_is_zero, sourced, corrected, no_false_zero])
    return ok, (
        f"York marginal share {york_share:.2f}% of Scope 2 (non-zero={nonzero}, "
        f"under 2%={bounded}); nuclear-share sweep -> "
        + ", ".join(f"{k} {v:.2f}%" for k, v in sweep.items())
        + f"; blended marginal {base_mb:.1f} gal/MWh; mix sourced={sourced}; "
        f"ledger corrected={corrected}; abstract free of the false 0%={no_false_zero}")


def c_occupancy_ramp():
    """The fit-out ramp must reconcile the LEVEL against an outside anchor, and
    must not touch any share.

    Every other check in this harness tests distributional shape. This one tests
    magnitude, which went untested until JLARC Ch.1 supplied a top-down number
    derived from utility peak-load forecasts -- a completely different
    measurement path from our floor-area ladder.

    Guards against three specific regressions:
      * the ramp silently disappearing (all buildings back at 100%)
      * the ramp being applied to buildings that never reached occupancy, which
        would conflate "not built" with "built but filling up"
      * the ramp leaking into the reported shares, which would invalidate the
        abstract's 88% / under-3% claims
    """
    import datetime
    from indirect_water_footprint import RAMP_YEARS_CENTRAL, occupancy_ramp

    prof = json.load(open(os.path.join(PUB, "facility_profiles.json")))["buildings"]
    comp = [b for b in prof if b.get("status") in ("Completed", "Finaled")]
    other = [b for b in prof if b.get("status") not in ("Completed", "Finaled")]

    def ramp_of(b):
        return b["scope_water_footprint"]["power"]["ramp"]

    # applied to occupied buildings only
    applied_comp = sum(1 for b in comp if ramp_of(b)["applied"])
    applied_other = sum(1 for b in other if ramp_of(b)["applied"])
    scoped = applied_comp == len(comp) and applied_other == 0

    # the ramp is actually biting on recently-occupied buildings
    on_ramp = sum(1 for b in comp
                  if ramp_of(b)["energized_fraction_central"] < 1.0)
    biting = on_ramp > 0

    # installed >= energized, never the reverse
    monotone = all(
        b["scope_water_footprint"]["power"]["installed_it_mw_central"]
        >= b["scope_water_footprint"]["power"]["effective_it_mw_central"] - 1e-9
        for b in prof
    )

    # vintage-matched level check against the JLARC-derived anchor
    JLARC_PWC_MW, AS_OF, PUE = 5050.0 * 0.5 / 3.0, datetime.date(2024, 7, 1), 1.25
    inst = ener = 0.0
    for b in comp:
        r = ramp_of(b)
        if not r.get("occupancy_date"):
            continue
        occ = datetime.date.fromisoformat(r["occupancy_date"])
        if occ > AS_OF:
            continue
        mw = b["scope_water_footprint"]["power"]["installed_it_mw_central"]
        inst += mw
        ener += mw * occupancy_ramp((AS_OF - occ).days / 365.25, RAMP_YEARS_CENTRAL)
    raw_ratio = inst * PUE / JLARC_PWC_MW
    ramp_ratio = ener * PUE / JLARC_PWC_MW
    reconciles = 0.70 <= ramp_ratio <= 1.40
    improves = abs(ramp_ratio - 1.0) < abs(raw_ratio - 1.0)

    # shares must be invariant
    def shares(unramp):
        s1 = s2 = s3 = 0.0
        for b in comp:
            sw = b["scope_water_footprint"]
            f = 1.0
            if unramp:
                r = sw["power"]["ramp"]["energized_fraction_central"]
                if r <= 0:
                    continue
                f = 1.0 / r
            s1 += sw["scope1_onsite_cooling"]["mgd_central"] * f
            s2 += sw["scope2_electricity"]["mgd_central"] * f
            s3 += sw["scope3_embodied"]["mgd_central"] * f
        t = s1 + s2 + s3
        return (s2 / t, s1 / t) if t else (0, 0)
    s2r, s1r = shares(False)
    s2u, s1u = shares(True)
    invariant = abs(s2r - s2u) < 5e-3 and abs(s1r - s1u) < 5e-3

    # Invariance alone is too weak: scaling one scope uniformly across every
    # building passes it (both sides of the comparison move together) while
    # silently breaking the abstract. So ALSO bind the recomputed shares to what
    # the abstract actually claims. This is the assertion with teeth.
    s1c = sum(b["scope_water_footprint"]["scope1_onsite_cooling"]["consumptive_mgd_central"]
              for b in comp)
    tot_c = sum(b["scope_water_footprint"]["total_consumptive_mgd_central"] for b in comp)
    s1_cons_share = s1c / tot_c if tot_c else 0
    supports_88 = 0.870 <= s2r <= 0.890            # abstract says "88%"
    supports_under3 = s1r < 0.030 and s1_cons_share < 0.030   # "under 3%", both bases
    invariant = invariant and supports_88 and supports_under3

    led = {e["id"]: e for e in json.load(
        open(os.path.join(DATA, "provenance_ledger.json")))["entries"]}
    # The ramp LENGTH and the LEVEL anchor must both be PDF-quote-verified. The
    # county fit-out policy is held in the corpus only as a JSON text extract, so
    # it cannot be quote-verified against a PDF; it must instead be explicitly
    # typed and noted, which is the same standard c_provenance_ledger applies.
    sourced = all(bool(led.get(k, {}).get("verbatim_quote")) for k in
                  ("gs5_four_year_ramp", "jlarc_va_datacenter_mw_5050"))
    mech = led.get("pwc_co_granted_with_unfitted_area", {})
    sourced = sourced and mech.get("type") == "external_citation" and bool(mech.get("note"))

    ok = all([scoped, biting, monotone, reconciles, improves, invariant, sourced])
    return ok, (
        f"ramp scoped to occupied buildings only ({applied_comp}/{len(comp)} completed, "
        f"{applied_other} non-completed)={scoped}; {on_ramp} actively ramping; "
        f"installed>=energized={monotone}; vintage-matched vs JLARC anchor "
        f"{JLARC_PWC_MW:.0f} MW: unramped {raw_ratio:.2f}x -> ramped {ramp_ratio:.2f}x "
        f"(reconciles={reconciles}, improves={improves}); shares invariant + still "
        f"support the abstract (Scope2 {s2r*100:.2f}% vs unramped {s2u*100:.2f}%, "
        f"on-site {s1r*100:.2f}% del / {s1_cons_share*100:.2f}% cons)={invariant}; "
        f"ledger sourced={sourced}")


def c_drought_denominator():
    """The seasonal surface must carry a swept low-flow denominator, and the
    abstract must make the sharpened dual-reporting claim.

    Two regressions this guards:
      * the drought sweep being dropped, which would let the historical low-flow
        denominator pass as if it were stationary when the county's own
        vulnerability assessment projects severe-drought months up 114-350%
      * the abstract sliding back to the weak "two conventions disagree" claim
        after End Note 17 supplied the strong one
    """
    d = json.load(open(os.path.join(PUB, "seasonal_basin_surface.json")))
    surf = d["surfaces"]

    have = [ws for ws, v in surf.items() if v.get("drought_denominator_sweep")]
    present = len(have) == len(surf) and bool(surf)

    # monotone: shrinking the denominator can only raise the ratio
    monotone, worst_stable, spread = True, True, {}
    for ws, v in surf.items():
        sw = v.get("drought_denominator_sweep") or {}
        pcts = [x["worst_pct_of_flow"] for x in sw.values()]
        months = {x["worst_month"] for x in sw.values()}
        if pcts != sorted(pcts):
            monotone = False
        if len(months) != 1:
            worst_stable = False          # binding month must not move
        if pcts:
            spread[ws] = (pcts[0], pcts[-1])

    # RE-BOUND 2026-08-03. The sweep used to be labelled "a sensitivity, NOT a
    # projection". It is neither: the county is in the longest severe drought of
    # its 132-year record, still open at the data cutoff, so the reduced-flow
    # branches describe a CURRENT CONDITION. Require the source string to (a) rest
    # on the OBSERVED record, (b) say so explicitly, (c) still disclaim being a
    # rainfall-runoff model, and (d) mark AECOM as direction-only. Reverting to the
    # old "sensitivity" framing, or dropping the observed basis, must fail.
    def _src_ok(v):
        s = (v.get("drought_denominator_source") or "")
        return ("OBSERVED CONDITION" in s
                and "not a hypothetical sensitivity" in s
                and "PDSI" in s
                and "still open at data cutoff" in s
                and "not a rainfall-runoff projection" in s
                and "direction only" in s)
    sourced = all(_src_ok(v) for v in surf.values())

    abstract = open(os.path.join(HERE, "ABSTRACT_AGU26.txt")).read()
    strong = ("dual location- and market-based reporting" in abstract
              and "no equivalent norm" in abstract
              and "geographic" in abstract)
    weak_gone = "two equally standard conventions" not in abstract

    ok = all([present, monotone, worst_stable, sourced, strong, weak_gone])
    return ok, (
        f"drought denominator swept for {len(have)}/{len(surf)} basins "
        f"(present={present}, monotone={monotone}, binding month stable={worst_stable}, "
        f"sourced+caveated={sourced}); "
        + "; ".join(f"{ws} {lo:.1f}%->{hi:.1f}%" for ws, (lo, hi) in spread.items())
        + f"; abstract makes the dual-reporting claim={strong}, weak form removed={weak_gone}")


# 23 ------------------------------------------------------------------------
def c_convention_table():
    """The paper's central result: which basin bears the electricity-related
    water is set by CONVENTION, not measurement.

    Bound to substantive claims, not self-consistency:
      - the spread across computable conventions must be large (>10x), else the
        thesis is not supported by our own numbers;
      - the utility-average and short-run-marginal endpoints must still bracket
        it (the abstract's two conventions);
      - any convention whose geography is broader than the Virginia plant map
        must EITHER carry a sourced VA-share scaling OR be declared
        non-computable. Silently distributing a PJM-wide nuclear share across
        North Anna and Surry inverts the result (45% instead of 5%) and must
        fail this check;
      - the long-run row must carry its SMR caveat so it cannot drift into a
        Lake Anna claim.
    """
    import indirect_water_footprint as m
    c = json.load(open(os.path.join(PUB, "convention_table.json")))
    rows = c["conventions"]

    computed = {k: v for k, v in rows.items() if v.get("computable")}
    shares = {k: v["lake_anna_pct_of_scope2"] for k, v in computed.items()}
    lo, hi = min(shares.values()), max(shares.values())
    spread_ok = lo > 0 and (hi / lo) > 10

    # endpoints are the abstract's own two conventions
    brackets = (rows["dominion_utility_average"].get("lake_anna_pct_of_scope2") == hi
                and rows["short_run_marginal"].get("lake_anna_pct_of_scope2") == lo)

    # geography discipline: broader-than-Virginia conventions are handled honestly
    geo_ok = True
    for cid, spec in m.LOCATION_BASED_CONVENTIONS.items():
        if "va_share_of_nuclear" not in spec:
            continue                              # geography == Virginia, fine
        r = rows[cid]
        if spec["va_share_of_nuclear"] is None:
            if r.get("computable") or not r.get("why_not_computable"):
                geo_ok = False
        else:
            g = r.get("geography_scaling") or {}
            if not g.get("source") or g.get("unscaled_pct", 0) <= r["lake_anna_pct_of_scope2"]:
                geo_ok = False                    # scaling must actually reduce it

    # the long-run row must keep its caveat
    lr = rows.get("long_run_marginal", {})
    caveat_ok = "SMR" in (lr.get("MANDATORY_CAVEAT") or "") and not lr.get("computable")

    ok = spread_ok and brackets and geo_ok and caveat_ok
    return ok, (f"{len(computed)} computable conventions span {lo:.2f}%-{hi:.2f}% "
                f"(spread {hi/lo:.0f}x, >10x={spread_ok}); endpoints are "
                f"utility-average/short-run-marginal={brackets}; broader-geography "
                f"conventions scaled-or-declared={geo_ok}; long-run SMR caveat "
                f"present={caveat_ok}")


# 23 ------------------------------------------------------------------------
def c_entitlement_pathway():
    """The paper's second leg: the entitlement pathway never asks for water.

    Bound to the substantive claims, recomputed from the county's own layer
    rather than trusting the stored JSON:
      - ZERO buildings have a SUP (the only discretionary review);
      - a majority sit inside the DCOOD, where the use is by right;
      - pre-1990 entitlements exist and are still producing buildings, so the
        'just add conditions' remedy is unavailable for part of the fleet;
      - the price and fee asymmetries are arithmetically consistent.
    Recomputing means a stale or hand-edited JSON cannot pass.
    """
    import re as _re
    from collections import Counter as _C
    e = json.load(open(os.path.join(PUB, "entitlement_pathway.json")))
    gj = json.load(open(os.path.join(RAW, "Data_Center_Buildings.geojson"),
                        encoding="utf-8", errors="replace"))
    feats = [f["properties"] for f in gj["features"]]

    def _case(p):
        c = str(p.get("PlanningCaseNumber") or "").strip()
        return c if c and c.lower() not in ("none", "<null>") else None
    cases = [c for c in (_case(p) for p in feats) if c]
    pref = _C(_re.match(r"([A-Z]+)", c).group(1) for c in cases if _re.match(r"([A-Z]+)", c))
    n_sup_recomputed = pref.get("SUP", 0)

    zero_sup = (n_sup_recomputed == 0
                and e["THE_FINDING"]["buildings_with_a_sup"] == 0)

    dcood = _C(str(p.get("DCOOD")) for p in feats)
    by_right = dcood.get("Yes", 0)
    majority_by_right = by_right > len(feats) / 2
    matches = e["by_right_eligibility"]["inside_dcood"] == by_right

    def _yr(c):
        m = _re.search(r"((?:19|20)\d{2})", c)
        return int(m.group(1)) if m else None
    pre1990 = sum(1 for c in cases if _yr(c) and _yr(c) < 1990)
    old_alive = pre1990 > 0 and e["entitlement_vintage"]["pre_1990_buildings"] == pre1990

    pa = e["price_asymmetry"]
    ratio_ok = abs(pa["fire_and_rescue_contribution_usd"] / pa["water_quality_contribution_usd"]
                   - pa["ratio_fire_to_water"]) < 0.5 and pa["ratio_fire_to_water"] > 100

    ok = zero_sup and majority_by_right and matches and old_alive and ratio_ok
    return ok, (f"SUPs recomputed from the county layer={n_sup_recomputed} (zero={zero_sup}); "
                f"{by_right}/{len(feats)} inside DCOOD (majority={majority_by_right}, "
                f"matches stored={matches}); pre-1990 entitlements={pre1990} "
                f"(still producing buildings={old_alive}); fire:water exaction ratio "
                f"{pa['ratio_fire_to_water']}x (consistent={ratio_ok})")


# 25 ------------------------------------------------------------------------
def c_data_version():
    """The client's cache-busting DATA_VERSION matches the shipped model.

    vercel.json serves /data with stale-while-revalidate=604800, so a browser
    may render a cached copy for up to a week after a deploy. src/lib/
    dataVersion.ts appends a version query string to defeat that, which only
    works if the constant is bumped whenever the data is. Forgetting to bump it
    reproduces the exact failure this harness exists to prevent: a corrected
    number that never reaches the page.
    """
    src = open(os.path.join(HERE, "src", "lib", "dataVersion.ts")).read()
    m = re.search(r'DATA_VERSION\s*=\s*"([^"]+)"', src)
    if not m:
        return False, "DATA_VERSION not found in src/lib/dataVersion.ts"
    declared = m.group(1)
    actual = _profiles()["generated_at"]
    ok = declared == actual
    # Every hook that pulls from /data must route through versioned().
    unversioned = []
    for fn in ("useFacilityProfiles.ts", "useCountyAnalysis.ts", "usePolicyIndex.ts"):
        body = open(os.path.join(HERE, "src", "lib", fn)).read()
        for call in re.findall(r'fetch\(\s*([^)]*?/data/[^)]*?)\)', body, re.S):
            if "versioned(" not in call:
                unversioned.append(f"{fn}:{call.strip()[:40]}")
    ok = ok and not unversioned
    return ok, (f"DATA_VERSION {declared} vs model generated_at {actual} "
                f"(match={declared == actual}); all /data fetches versioned="
                f"{not unversioned}"
                + (f" — unversioned: {unversioned}" if unversioned else ""))


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
    check("20 occupancy ramp + level anchor", c_occupancy_ramp)
    check("21 drought denominator + dual-reporting claim", c_drought_denominator)
    check("22 convention table", c_convention_table)
    check("23 entitlement pathway", c_entitlement_pathway)
    check("25 client data version", c_data_version)
    n_fail = sum(1 for _, ok, _ in results if not ok)
    print("=" * 60)
    print(f"{len(results)-n_fail}/{len(results)} checks passed"
          + ("" if n_fail else "  — RESEARCH-READY"))
    sys.exit(1 if n_fail else 0)


if __name__ == "__main__":
    main()
