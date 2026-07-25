"""
Per-building predictive variance for the GFA -> IT-power fallback.

WHAT THIS CHANGES, AND WHY
fit_power_model.py selected a log-log GFA->MW model and exported a SINGLE
systematic sigma (coefficient uncertainty evaluated at the mean GFA). Every
unpermitted building then carried the same systematic width regardless of how
far its floor area sat from the 14 permit sites we actually fit on. That is
wrong in the direction that matters for a transparency-gap paper: a 2.4 M sqft
hyperscale campus, far larger than anything in the training set, should carry a
WIDER power interval than a 200k sqft building sitting in the middle of the data.

THE FIX (textbook, deliberately not fancy)
Bayesian linear regression in log10 space -- equivalently a Gaussian process
with a linear (dot-product) kernel plus white noise. Its posterior predictive
variance for a NEW observation at floor area x* is the ordinary least-squares
prediction-interval variance

    Var[log10 MW | x*] = s^2 * (1 + [1,x*] (X'X)^-1 [1,x*]^T)

  - the "1" is irreducible site-to-site scatter (IDIOSYNCRATIC, independent per
    building -> averages down across the fleet);
  - the leverage term [1,x*](X'X)^-1[1,x*]^T grows quadratically as x* leaves
    the training centroid (SYSTEMATIC coefficient uncertainty, shared across
    buildings -> does NOT average away).
That split is exactly what the Monte Carlo needs, and it makes the interval
"wider where we extrapolate, narrower near the data" by construction.

WHY NO SEPARATE OPERATOR-VARIANCE TERM
The operator effect stays in the MEAN (the deployed prediction adds the shrunk
operator offset), but it gets no separate variance term: the between-operator
dispersion tau^2 estimates to ~0 at n=14 (operator identity is not
statistically distinguishable from noise -- the same reason pure density rivals
ridge+operator in LOO). Adding an operator-variance term would re-inject
idiosyncratic scatter on only 5 residual dof and over-widen the interval. The
pooled residual (dof = n-2 = 12) is the honest total predictive scatter.

RESEARCH-READINESS GATE
A predictive-variance model is science only if its intervals are CALIBRATED. We
validate THE EXACT DEPLOYED FORM (operator-adjusted mean + pooled prediction
variance) by leave-one-out: ~90% of held-out truths must fall in the 90%
interval and mean squared standardized residual must be ~1. We also confirm via
sklearn GPs that an added RBF kernel does not improve LOO (linear is right).
Nothing is exported unless the deployed form passes.

Run with an interpreter that has sklearn (e.g. /usr/bin/python3). Outputs are
portable (beta, noise variance, (X'X)^-1); the pure-numpy Monte Carlo consumes
them with no sklearn dependency.
"""
import json
import math
from collections import defaultdict

import numpy as np
from scipy import stats

from fit_power_model import load_sites, SHRINK_K, OUT


def design(rows):
    x = np.array([math.log10(r["gfa"]) for r in rows])
    y = np.array([math.log10(r["it_mw"]) for r in rows])
    return x, y


def blr_predictor(rows, op_in_mean):
    """OLS / GP-linear predictor. Returns predict(row)->(mean,var,dof) and params.

    Variance is the OLS prediction-interval variance (pooled, dof=n-2). The
    operator effect, when used, shifts only the MEAN -- never the variance.
    """
    x, y = design(rows)
    X = np.column_stack([np.ones_like(x), x])
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    n, p = len(rows), 2
    s2 = float(resid @ resid) / (n - p)          # pooled noise variance, dof=12

    op_eff = {}
    if op_in_mean:
        r_by = defaultdict(list)
        for r, rb in zip(rows, resid):
            r_by[r["operator"]].append(rb)
        op_eff = {o: (len(v) / (len(v) + SHRINK_K)) * float(np.mean(v))
                  for o, v in r_by.items()}

    def predict(row):
        xv = np.array([1.0, math.log10(row["gfa"])])
        mean = float(beta @ xv) + (op_eff.get(row["operator"], 0.0) if op_in_mean else 0.0)
        var = s2 * (1.0 + float(xv @ XtX_inv @ xv))   # noise + leverage
        return mean, var, (n - p)

    return predict, {"beta": beta.tolist(), "s2": s2, "XtX_inv": XtX_inv.tolist(),
                     "op_eff": op_eff}


def loo_calibration(rows, op_in_mean):
    inside90 = inside50 = 0
    z, sqerr = [], []
    for i in range(len(rows)):
        train = rows[:i] + rows[i + 1:]
        predict, _ = blr_predictor(train, op_in_mean)
        mean, var, dof = predict(rows[i])
        truth = math.log10(rows[i]["it_mw"])
        sd = math.sqrt(var)
        z.append((truth - mean) / sd)
        sqerr.append((truth - mean) ** 2)
        inside90 += abs(truth - mean) <= stats.t.ppf(0.95, dof) * sd
        inside50 += abs(truth - mean) <= stats.t.ppf(0.75, dof) * sd
    z = np.array(z)
    return {"rmse_log10": float(np.sqrt(np.mean(sqerr))),
            "coverage_90": inside90 / len(rows),
            "coverage_50": inside50 / len(rows),
            "mean_z2": float(np.mean(z ** 2))}


def sklearn_gp_loo(rows, add_rbf):
    from sklearn.gaussian_process import GaussianProcessRegressor
    from sklearn.gaussian_process.kernels import (DotProduct, WhiteKernel, RBF,
                                                  ConstantKernel as C)
    x, y = design(rows)
    xn = ((x - x.mean()) / x.std()).reshape(-1, 1)
    kernel = C(1.0) * DotProduct(sigma_0=1.0) + WhiteKernel(0.1)
    if add_rbf:
        kernel = kernel + C(0.5) * RBF(1.0)
    sq = []
    for i in range(len(rows)):
        tr = np.delete(np.arange(len(rows)), i)
        gp = GaussianProcessRegressor(kernel=kernel, normalize_y=True,
                                      n_restarts_optimizer=3, random_state=0)
        gp.fit(xn[tr], y[tr])
        sq.append((gp.predict(xn[i:i + 1])[0] - y[i]) ** 2)
    return float(np.sqrt(np.mean(sq)))


def main():
    rows = load_sites()
    print(f"sites: {len(rows)}\n")

    print("LEAVE-ONE-OUT CALIBRATION (OLS prediction interval = GP linear kernel)")
    print(f"{'model':<34}{'RMSE':>8}{'cov90':>8}{'cov50':>8}{'mean z^2':>10}")
    cal = {}
    for label, opm in [("pooled mean (no operator)", False),
                       ("operator-adjusted mean [DEPLOYED]", True)]:
        c = loo_calibration(rows, opm)
        cal[opm] = c
        print(f"{label:<34}{c['rmse_log10']:>8.4f}{c['coverage_90']:>8.0%}"
              f"{c['coverage_50']:>8.0%}{c['mean_z2']:>10.3f}")
    print(f"{'target':<34}{'~min':>8}{'90%':>8}{'50%':>8}{'~1.00':>10}")

    print("\nKERNEL CHECK (sklearn GP LOO-RMSE; RBF must NOT beat linear):")
    lin = sklearn_gp_loo(rows, add_rbf=False)
    rbf = sklearn_gp_loo(rows, add_rbf=True)
    print(f"  linear (dot-product) kernel : {lin:.4f}")
    print(f"  linear + RBF kernel         : {rbf:.4f}   "
          f"({'RBF adds nothing -> linear justified' if rbf >= lin - 1e-3 else 'RBF helps -- investigate'})")

    # Deploy the operator-adjusted-mean form (matches indirect_water_footprint's
    # effective_power_from_fitted). Gate on calibration; over-coverage (z^2<1) is
    # the safe direction -- we must not understate uncertainty.
    chosen = cal[True]
    verdict = (0.80 <= chosen["coverage_90"] <= 1.0 and 0.4 <= chosen["mean_z2"] <= 2.0)
    print(f"\ndeployed form: operator-adjusted mean + pooled prediction variance")
    print(f"calibration verdict: {'PASS' if verdict else 'FAIL'} "
          f"(cov90={chosen['coverage_90']:.0%}, cov50={chosen['coverage_50']:.0%}, "
          f"mean z^2={chosen['mean_z2']:.2f})")

    if not verdict:
        print("\nNOT exporting -- deployed form is not calibrated. Investigate first.")
        return

    _, params = blr_predictor(rows, op_in_mean=True)
    doc = json.load(open(OUT))
    doc["predictive_variance"] = {
        "method": "OLS prediction interval (GP linear kernel), operator-adjusted "
                  "mean, LOO-calibrated",
        "beta_intercept_slope": params["beta"],
        "noise_var_log10": params["s2"],
        "XtX_inv": params["XtX_inv"],
        "variance_formula": "Var[log10 MW|x] = s2 * (1 + [1,x] (XtX)^-1 [1,x]^T); "
                            "'1'=idiosyncratic (per building), leverage term="
                            "systematic (shared coefficient draw)",
        "no_operator_variance_term": "tau2 (between-operator dispersion) ~ 0 at "
                                     "n=14; operator effect adjusts the mean only",
        "loo_calibration": chosen,
        "kernel_check": {"gp_linear_loo_rmse": lin, "gp_linear_rbf_loo_rmse": rbf},
    }
    json.dump(doc, open(OUT, "w"), indent=1)
    print(f"\nwrote predictive_variance block into {OUT}")


if __name__ == "__main__":
    main()
