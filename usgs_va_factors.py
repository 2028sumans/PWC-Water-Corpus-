"""
Derive Virginia-specific water consumption factors (gal/MWh) by generation type
from the USGS plant-level thermoelectric water use dataset.

This replaces the national medians (Macknick et al., NREL/TP-6A20-50900, 2011)
that the Scope 2 calculation previously used. The nuclear correction is the one
that matters: a single national "nuclear = 700 gal/MWh" constant blended two
Virginia plants with opposite water profiles (North Anna's cooling lake vs
Surry's once-through tidal saline discharge).

SOURCE (refreshed 19 July 2026)
-------------------------------
  Thermoelectric-power water use REANALYSIS for the 2008-2020 period by power
  plant, month, and year (Galanter and others, 2023). USGS ScienceBase item
  63adc826d34e92aad3ca5af4, DOI 10.5066/P9ZE2FVM.
    File: published_annual_thermoelectric_water_use_estimates_2008-2020.csv
    Vendored Virginia slice: data/usgs_te_water_2008-2020_VA.csv

  This supersedes the 2015 v1.2 release (ScienceBase 5f63be9a...) the model used
  through 18 July 2026. The reanalysis uses the FEWSR + TOWER heat-and-water
  budget models, is independent of operator self-reporting, and -- unlike a
  single-year snapshot -- lets factors be pooled over 2018-2020 for stability.

  The biggest change is nuclear: the reanalysis puts North Anna at ~737 gal/MWh
  (stable to +/-1% across all 13 years), where the old release implied ~417.
  Generation-weighted with Surry's zero, VA nuclear rises from 242 to 391.

UNITS (confirmed against the data-release README)
  cu_mgd / cu_lower_mgd / cu_upper_mgd  consumption, million gallons per day
  Net.Generation.Year.To.Date           MWh, annual, EIA-reported
  gal/MWh = cu_mgd x 365 d x 1e6 / net_generation_mwh

KNOWN GAP (a finding in its own right -- see METHODOLOGY.md section 18)
  Dominion's three largest modern combined-cycle plants -- Greensville (1,605
  MW), Warren County (1,350 MW), Brunswick County (1,376 MW) -- are ABSENT from
  the freshwater model because they run on reclaimed municipal water. So the gas
  factor derived here is for the older, fresh-water-consuming plants; the
  fleet-average FRESHWATER intensity of Dominion gas is lower, because a large
  and growing share of gas MWh comes from plants that touch no fresh basin water.

USAGE
  python3 usgs_va_factors.py [path/to/VA_slice.csv]
"""
import csv
import sys
from collections import defaultdict

DEFAULT_CSV = "data/usgs_te_water_2008-2020_VA.csv"
POOL_YEARS = {"2018", "2019", "2020"}


def _fuel_key(dom_fuel, mover):
    """Map the reanalysis fuel/prime-mover onto the estimator's fuel keys."""
    if dom_fuel == "nuclear":
        return "nuclear"
    if dom_fuel == "coal":
        return "coal"
    if mover == "NGCC" or dom_fuel == "gas":
        return "natural_gas_cc"
    return None


def _num(s):
    try:
        return float(str(s).replace(",", ""))
    except (TypeError, ValueError):
        return None


def load_va_plants(path):
    """Virginia plant-year rows for the pooled years, as dicts."""
    out = []
    for r in csv.DictReader(open(path, encoding="latin-1")):
        if r.get("State") != "VA" or r.get("YEAR") not in POOL_YEARS:
            continue
        out.append(r)
    return out


def gal_per_mwh(consumption_mgd, net_generation_mwh):
    if consumption_mgd is None or not net_generation_mwh:
        return None
    return consumption_mgd * 365 * 1e6 / net_generation_mwh


def derive_va_consumption_factors(path=DEFAULT_CSV):
    """Generation-weighted gal/MWh per fuel key, pooled over 2018-2020, with
    bounds from the reanalysis's own cu_lower / cu_upper columns."""
    agg = defaultdict(lambda: {"cons": 0.0, "gen": 0.0, "lo": 0.0, "hi": 0.0, "plants": {}})
    for p in load_va_plants(path):
        key = _fuel_key(p.get("Plant.level_dom_fuel"), p.get("general_mover"))
        if not key:
            continue
        gen = _num(p["Net.Generation.Year.To.Date"])
        cons = _num(p["cu_mgd"])
        if cons is None or not gen or gen <= 0:
            continue
        a = agg[key]
        a["cons"] += cons
        a["gen"] += gen
        a["lo"] += _num(p["cu_lower_mgd"]) or 0.0
        a["hi"] += _num(p["cu_upper_mgd"]) or 0.0
        # accumulate per plant across the pooled years
        pl = a["plants"].setdefault(p["Plant.Name"],
                                    {"cons": 0.0, "gen": 0.0, "cooling": p["coolingType"],
                                     "src": p["Name.of.Water.Source"]})
        pl["cons"] += cons
        pl["gen"] += gen

    return {
        key: {
            "gal_per_mwh": round(gal_per_mwh(a["cons"], a["gen"])),
            "bounds": (round(gal_per_mwh(a["lo"], a["gen"])),
                       round(gal_per_mwh(a["hi"], a["gen"]))),
            "net_generation_mwh": a["gen"],
            "plants": [(n, d["cooling"], d["src"], gal_per_mwh(d["cons"], d["gen"]))
                       for n, d in a["plants"].items()],
        }
        for key, a in agg.items()
    }


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    factors = derive_va_consumption_factors(path)

    print("Virginia consumption factors from USGS 2008-2020 reanalysis (pooled 2018-2020)\n")
    for key, f in sorted(factors.items(), key=lambda kv: -kv[1]["net_generation_mwh"]):
        print(f"{key:<16} {f['gal_per_mwh']:>5} gal/MWh  "
              f"(range {f['bounds'][0]}-{f['bounds'][1]})  "
              f"gen {f['net_generation_mwh']:>14,.0f} MWh")
        for name, cooling, src, gpm in sorted(f["plants"], key=lambda p: -(p[3] or 0)):
            print(f"    {name:<30} {cooling:<20} {gpm:>7.1f} gal/MWh  {src[:24]}")
        print()
