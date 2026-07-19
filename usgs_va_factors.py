"""
Derive Virginia-specific water consumption factors (gal/MWh) by generation type
from the USGS plant-level thermoelectric water use dataset.

This replaces the national medians (Macknick et al., NREL/TP-6A20-50900, 2011)
that the Scope 2 calculation previously used. The nuclear correction is the one
that matters: a single national "nuclear = 700 gal/MWh" constant blended two
Virginia plants with opposite water profiles.

SOURCE
------
  Water withdrawal and consumption estimates for thermoelectric power plants in
  the United States, 2015 (ver. 1.2, July 2024). USGS ScienceBase item
  5f63be9a82ce38aaa23b0739.
    https://www.sciencebase.gov/catalog/item/5f63be9a82ce38aaa23b0739
  File: Version_1.2_2015_TE_Model_Estimates.csv

  USGS models withdrawal and consumption from a heat-and-water budget, so the
  estimates are independent of operator self-reporting -- which is exactly the
  property we want for a Scope 2 factor.

UNITS (confirmed against the FGDC metadata, not assumed)
  WITHDRAWAL / CONSUMPTION  million gallons per day (Mgal/d), annual average
  NET_GENERATION            megawatt-hours (MWh), annual, EIA-reported

  gal/MWh = CONSUMPTION (Mgal/d) x 365 d x 1e6 / NET_GENERATION (MWh)

VINTAGE CAVEAT
  Generation is 2015. Dominion's mix has shifted since (more gas and solar, less
  coal), so the per-technology intensities are current-ish but the plants' output
  weights are a decade old. The factors are intensities, not totals, so this
  matters less than it would for an absolute figure -- but it should be restated
  if a newer USGS release lands.

USAGE
  python3 usgs_va_factors.py path/to/Version_1.2_2015_TE_Model_Estimates.csv
"""
import csv
import sys
from collections import defaultdict

DEFAULT_CSV = "Version_1.2_2015_TE_Model_Estimates.csv"

# Map USGS GENERATION_TYPE onto the fuel keys the estimator's Dominion mix uses.
GENERATION_TYPE_MAP = {
    "NUCLEAR": "nuclear",
    "NGCC": "natural_gas_cc",
    "COAL": "coal",
}


def _num(s):
    try:
        return float(str(s).replace(",", ""))
    except (TypeError, ValueError):
        return None


def load_va_plants(path):
    """Return Virginia plant rows as dicts, from the USGS estimates CSV.

    The file carries two title lines before the real header, so the header is
    row index 2 rather than 0.
    """
    rows = list(csv.reader(open(path, encoding="latin-1")))
    header = rows[2]
    idx = {c: i for i, c in enumerate(header)}
    out = []
    for r in rows[3:]:
        if len(r) <= idx["NET_GENERATION"] or r[idx["STATE"]] != "VA":
            continue
        out.append({c: r[i] for c, i in idx.items() if i < len(r)})
    return out


def gal_per_mwh(consumption_mgd, net_generation_mwh):
    if consumption_mgd is None or not net_generation_mwh:
        return None
    return consumption_mgd * 365 * 1e6 / net_generation_mwh


def derive_va_consumption_factors(path=DEFAULT_CSV):
    """Generation-weighted gal/MWh per fuel key, with min/max bounds.

    Weighting by generation (not a plain mean across plants) is what makes the
    nuclear number come out at 242 rather than ~209: North Anna both consumes
    more and generates more than Surry, so it carries more of the weight.
    """
    agg = defaultdict(lambda: {"cons": 0.0, "gen": 0.0, "lo": 0.0, "hi": 0.0, "plants": []})
    for p in load_va_plants(path):
        key = GENERATION_TYPE_MAP.get(p["GENERATION_TYPE"])
        if not key:
            continue
        gen = _num(p["NET_GENERATION"])
        cons = _num(p["CONSUMPTION"])
        if cons is None or not gen or gen <= 0:
            continue
        a = agg[key]
        a["cons"] += cons
        a["gen"] += gen
        a["lo"] += _num(p["MIN_CONSUMPTION"]) or 0.0
        a["hi"] += _num(p["MAX_CONSUMPTION"]) or 0.0
        a["plants"].append((p["PLANT_NAME"], p["EIA_PLANT_ID"], p["COOLING_TYPE"],
                            gal_per_mwh(cons, gen)))

    return {
        key: {
            "gal_per_mwh": round(gal_per_mwh(a["cons"], a["gen"])),
            "bounds": (round(gal_per_mwh(a["lo"], a["gen"])),
                       round(gal_per_mwh(a["hi"], a["gen"]))),
            "net_generation_mwh": a["gen"],
            "plants": a["plants"],
        }
        for key, a in agg.items()
    }


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    factors = derive_va_consumption_factors(path)

    print("Virginia consumption factors from USGS 2015 v1.2\n")
    for key, f in sorted(factors.items(), key=lambda kv: -kv[1]["net_generation_mwh"]):
        print(f"{key:<16} {f['gal_per_mwh']:>5} gal/MWh  "
              f"(range {f['bounds'][0]}-{f['bounds'][1]})  "
              f"gen {f['net_generation_mwh']:>14,.0f} MWh")
        for name, eia, cooling, gpm in sorted(f["plants"], key=lambda p: -(p[3] or 0)):
            print(f"    {name:<22} EIA {eia:<6} {cooling:<22} {gpm:>7.1f} gal/MWh")
        print()
