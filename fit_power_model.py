"""
Fit the GFA -> IT-power fallback model on the permit-backed sites.

WHY THIS EXISTS
The estimator's root quantity is IT power (MW): both scopes are driven by it.
For 45 buildings, power is observed (VADEQ generator capacity x ICPRB Eq 6-3).
For the rest, the model must infer power from floor area. Until now that used
hand-set density bands (sqft/MW by operator/vintage). This script replaces the
bands with a FITTED relationship whose residual is measured, not assumed -- so
the fallback tier's uncertainty in the Monte Carlo is an empirical quantity.

THE LEAKAGE TRAP (why fitting is at SITE level)
Permit MW was apportioned to buildings BY GFA SHARE, so within a campus,
MW/GFA is constant by construction. A building-level fit would partly learn its
own apportionment back (artificially high R^2). The independent unit is the
PERMIT SITE: full site GFA (recovered as gfa_i / gfa_share_i) vs site IT MW
(generator capacity x 0.4). n = 14 independent sites.

MODEL SELECTION (ML where effective -- which, at n=14, it is not)
Candidates compared by leave-one-out CV in log10 space:
  A. pure density  log10(MW) = log10(GFA) - log10(density)   (slope fixed at 1)
  B. OLS           log10(MW) = a + b*log10(GFA)
  C. OLS + operator effects shrunk toward 0 (partial pooling, k=2)
  D. Ridge on [log10(GFA), operator dummies] (RidgeCV)
  E. RandomForest  (sklearn, default-ish, honest baseline)
  F. GradientBoosting
The winner's LOO-RMSE becomes the fallback tier's sigma; per-operator effects
transfer to unpermitted buildings of the same operator. Expectation stated in
advance: tree ensembles overfit 14 points and lose -- but we test, not assume.

Writes data/power_model.json consumed by indirect_water_footprint.py.
"""
import json
import math
from collections import defaultdict

import numpy as np

PROFILES = "public/data/facility_profiles.json"
OUT = "data/power_model.json"
PERMIT_FACTOR = 0.4   # ICPRB Eq 6-3: 0.5 redundancy x 0.8 utilization
SHRINK_K = 2.0        # operator-effect shrinkage: n/(n+k)


def operator_of(name):
    n = (name or "").lower()
    for k in ["iron mountain", "digital realty", "dlr", "amazon", "aws", "microsoft",
              "azure", "qts", "ntt", "stack", "corscale", "cloudhq", "compass",
              "vantage", "gainesville crossing"]:
        if k in n:
            return {"aws": "amazon", "dlr": "digital realty", "azure": "microsoft",
                    "gainesville crossing": "corscale"}.get(k, k)
    return "other"


def load_sites():
    d = json.load(open(PROFILES))
    sites = {}
    for b in d["buildings"]:
        swf = b.get("scope_water_footprint")
        if not swf:
            continue
        p = swf["power"]
        pm = p.get("permit")
        if p.get("basis") != "permit_generator_capacity" or not pm or not pm.get("gfa_share"):
            continue
        reg = pm["registration_no"]
        full_gfa = p["gfa_sqft"] / pm["gfa_share"]
        s = sites.setdefault(reg, {"gfa": full_gfa,
                                   "it_mw": pm["site_generator_mw"] * PERMIT_FACTOR,
                                   "ops": defaultdict(int)})
        s["ops"][operator_of(b["name"])] += 1
    rows = []
    for reg, s in sites.items():
        op = max(s["ops"], key=s["ops"].get)
        rows.append({"permit": reg, "gfa": s["gfa"], "it_mw": s["it_mw"], "operator": op})
    return sorted(rows, key=lambda r: -r["gfa"])


# ---------------------------------------------------------------------------
# candidate models, each exposing fit(train) -> predict(row) in log10(MW)
# ---------------------------------------------------------------------------
def fit_pure_density(train):
    # slope fixed at 1: single fleet density = geometric mean of GFA/MW
    logd = np.mean([math.log10(r["gfa"] / r["it_mw"]) for r in train])
    return lambda r: math.log10(r["gfa"]) - logd


def fit_ols(train):
    x = np.array([math.log10(r["gfa"]) for r in train])
    y = np.array([math.log10(r["it_mw"]) for r in train])
    b, a = np.polyfit(x, y, 1)
    return lambda r: a + b * math.log10(r["gfa"])


def fit_ols_operator(train):
    base = fit_ols(train)
    resid = defaultdict(list)
    for r in train:
        resid[r["operator"]].append(math.log10(r["it_mw"]) - base(r))
    eff = {op: (len(v) / (len(v) + SHRINK_K)) * float(np.mean(v)) for op, v in resid.items()}
    return lambda r: base(r) + eff.get(r["operator"], 0.0)


def _design(train, ops):
    X = []
    for r in train:
        row = [math.log10(r["gfa"])] + [1.0 if r["operator"] == o else 0.0 for o in ops]
        X.append(row)
    return np.array(X)


def fit_ridge(train):
    from sklearn.linear_model import RidgeCV
    ops = sorted({r["operator"] for r in train})
    X = _design(train, ops)
    y = np.array([math.log10(r["it_mw"]) for r in train])
    m = RidgeCV(alphas=np.logspace(-3, 2, 30)).fit(X, y)
    return lambda r: float(m.predict(_design([r], ops))[0])


def fit_rf(train):
    from sklearn.ensemble import RandomForestRegressor
    ops = sorted({r["operator"] for r in train})
    X = _design(train, ops)
    y = np.array([math.log10(r["it_mw"]) for r in train])
    m = RandomForestRegressor(n_estimators=500, random_state=0, min_samples_leaf=2).fit(X, y)
    return lambda r: float(m.predict(_design([r], ops))[0])


def fit_gbm(train):
    from sklearn.ensemble import GradientBoostingRegressor
    ops = sorted({r["operator"] for r in train})
    X = _design(train, ops)
    y = np.array([math.log10(r["it_mw"]) for r in train])
    m = GradientBoostingRegressor(n_estimators=200, max_depth=2, learning_rate=0.05,
                                  random_state=0).fit(X, y)
    return lambda r: float(m.predict(_design([r], ops))[0])


MODELS = {
    "pure_density": fit_pure_density,
    "ols_loglog": fit_ols,
    "ols_operator_pooled": fit_ols_operator,
    "ridge_operator": fit_ridge,
    "random_forest": fit_rf,
    "gradient_boosting": fit_gbm,
}


def loo_rmse(fit_fn, rows):
    errs = []
    for i in range(len(rows)):
        train = rows[:i] + rows[i + 1:]
        pred = fit_fn(train)(rows[i])
        errs.append(pred - math.log10(rows[i]["it_mw"]))
    return float(np.sqrt(np.mean(np.square(errs)))), errs


def main():
    rows = load_sites()
    print(f"training sites: {len(rows)}\n")
    y = np.array([math.log10(r["it_mw"]) for r in rows])

    results = {}
    for name, fitter in MODELS.items():
        try:
            rmse, errs = loo_rmse(fitter, rows)
            results[name] = rmse
            print(f"  {name:<22} LOO-RMSE(log10) = {rmse:.4f}   (x/ {10**rmse:.2f} factor)")
        except Exception as e:
            print(f"  {name:<22} FAILED: {e}")
    winner = min(results, key=results.get)
    print(f"\nwinner by LOO-CV: {winner}")

    # Fit the winner on ALL sites for deployment; report in-sample stats too.
    final = MODELS[winner](rows)
    yhat = np.array([final(r) for r in rows])
    ss_res = float(np.sum((y - yhat) ** 2))
    ss_tot = float(np.sum((y - np.mean(y)) ** 2))
    r2 = 1 - ss_res / ss_tot
    sigma = results[winner]  # honest sigma = LOO, not in-sample

    # Refit components for a portable JSON (winner is expected to be linear
    # family; if a tree model ever wins, fall back to ols_operator_pooled for
    # portability and say so).
    export_model = winner if winner in ("pure_density", "ols_loglog", "ols_operator_pooled") \
        else "ols_operator_pooled"
    if export_model != winner:
        print(f"note: exporting portable {export_model} (winner {winner} is not portable)")

    x = np.array([math.log10(r["gfa"]) for r in rows])
    b, a = np.polyfit(x, y, 1)
    base = lambda g: a + b * math.log10(g)
    resid = defaultdict(list)
    for r in rows:
        resid[r["operator"]].append(math.log10(r["it_mw"]) - base(r["gfa"]))
    op_eff = {op: (len(v) / (len(v) + SHRINK_K)) * float(np.mean(v)) for op, v in resid.items()}
    # coefficient covariance for the systematic MC draw
    X = np.column_stack([np.ones_like(x), x])
    dof = max(len(rows) - 2, 1)
    s2 = ss_res / dof
    cov = s2 * np.linalg.inv(X.T @ X)

    print(f"\nfinal (exported) model: log10(MW) = {a:.4f} + {b:.4f} * log10(GFA) + op_effect")
    print(f"  slope b = {b:.3f}  ({'economies of scale: bigger sites are DENSER' if b>1 else 'diseconomies: bigger sites are sparser'})")
    print(f"  in-sample R^2 = {r2:.3f}   LOO sigma(log10) = {sigma:.4f}  -> x/ {10**sigma:.2f}")
    print(f"  90% interval multiplier: x/ {10**(1.645*sigma):.2f}")
    print("  operator effects (shrunk):")
    for op, e in sorted(op_eff.items(), key=lambda kv: -kv[1]):
        print(f"    {op:<16} {e:+.4f}  (x{10**e:.2f})")
    # implied sqft/MW at reference sizes
    for g in (150_000, 300_000, 600_000, 1_200_000):
        mw = 10 ** base(g)
        print(f"  generic {g:>9,} sqft -> {mw:6.1f} MW  ({g/mw:7,.0f} sqft/MW)")

    # Held-out comparison: the one trade-permit stated critical load
    stated = {"gfa": 339_744, "mw_stated_critical": 60}
    pred = 10 ** base(stated["gfa"])
    print(f"\nheld-out check (MEC2025-01801, 339,744 sqft, 60 MW stated critical load):")
    print(f"  model predicts {pred:.1f} MW effective -- stated CRITICAL (design) load 60 MW; "
          f"effective demand at ICPRB's 0.8 utilization would be ~48 MW; prediction ratio "
          f"{pred/48:.2f}x of that")

    # Variance split for the Monte Carlo: systematic (coefficient uncertainty,
    # shared across buildings -- does not average away) vs idiosyncratic
    # (site-to-site residual after operator effects, independent per building).
    resid_after_op = [math.log10(r["it_mw"]) - (base(r["gfa"]) + op_eff.get(r["operator"], 0.0))
                      for r in rows]
    sigma_idio = float(np.std(resid_after_op, ddof=1))
    xbar = float(np.mean(x))
    sigma_syst = float(math.sqrt(cov[0][0] + 2 * xbar * cov[0][1] + xbar * xbar * cov[1][1]))
    print(f"  variance split: sigma_systematic={sigma_syst:.4f}  sigma_idiosyncratic={sigma_idio:.4f}")

    json.dump({
        "fitted": "site-level, leak-free (permit sites; building apportionment excluded)",
        "n_sites": len(rows),
        "winner_by_loo": winner,
        "exported_model": export_model,
        "loo_rmse_log10_all": results,
        "intercept": a, "slope": b,
        "coef_cov": cov.tolist(),
        "sigma_log10": sigma,
        "sigma_systematic_log10": sigma_syst,
        "sigma_idiosyncratic_log10": sigma_idio,
        "r2_insample": r2,
        "operator_effects": op_eff,
        "shrink_k": SHRINK_K,
        "training_sites": rows,
    }, open(OUT, "w"), indent=1)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
