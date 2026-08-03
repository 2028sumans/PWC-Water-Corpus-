"""
The entitlement pathway — why nobody ever asks how much water.

The convention analysis (convention_table.py) answers WHERE the water lands. This
answers WHETHER ANYONE ASKS. They are independent findings and together they are
the paper's two legs.

THE RESULT, stated up front because it is one number:

    ZERO of 243 data-center buildings in Prince William County has a Special Use
    Permit as its planning case.

Every populated planning case is a REZ (rezoning) or PLN (plan). Not one SUP. That
matters because the SUP is the county's only DISCRETIONARY review -- the point at
which conditions can be attached. Inside the Data Center Opportunity Overlay
District the use is permitted BY RIGHT, so no discretionary review is triggered at
all, and a facility can be built without any water question ever being posed.

This reframes the regulatory finding. It is not that water review is done badly.
It is that the entitlement pathway never invokes one. And for a substantial share
of the fleet there is no open approval left to condition: 32 buildings are
entitled under pre-1990 approvals, and 20 of them under rezonings adopted in 1958
(19 under REZ1958-0021, 1 under REZ1958-0034) -- before the integrated circuit was
commercialised.

Reads Data_Center_Buildings.geojson (the county's own layer). Writes
public/data/entitlement_pathway.json.
"""
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "water_raw")
PUB = os.path.join(HERE, "public", "data")
SRC = os.path.join(RAW, "Data_Center_Buildings.geojson")
OUT = os.path.join(PUB, "entitlement_pathway.json")

# Prince William planning case prefixes. SUP is the only discretionary one that
# attaches conditions to a specific proposed use.
CASE_TYPES = {
    "SUP": "Special Use Permit -- DISCRETIONARY; conditions can be attached",
    "REZ": "Rezoning -- changes the district; conditions via proffers, often decades old",
    "PLN": "Plan case",
    "PFR": "Public Facilities Review",
    "CPA": "Comprehensive Plan Amendment",
    "PRA": "Proffer Amendment",
}


def main():
    gj = json.load(open(SRC, encoding="utf-8", errors="replace"))
    feats = [f["properties"] for f in gj["features"]]
    n = len(feats)

    def case(p):
        c = str(p.get("PlanningCaseNumber") or "").strip()
        return c if c and c.lower() not in ("none", "<null>") else None

    cases = [case(p) for p in feats]
    with_case = [c for c in cases if c]

    def prefix(c):
        m = re.match(r"([A-Z]+)", c)
        return m.group(1) if m else "?"

    by_type = Counter(prefix(c) for c in with_case)
    n_sup = by_type.get("SUP", 0)

    # entitlement vintage: the year embedded in the case number
    def year(c):
        m = re.search(r"((?:19|20)\d{2})", c)
        return int(m.group(1)) if m else None

    vintage = Counter()
    by_case = defaultdict(list)
    for p, c in zip(feats, cases):
        if not c:
            continue
        y = year(c)
        if y:
            vintage[y] += 1
        by_case[c].append(p)

    pre1990 = sum(v for y, v in vintage.items() if y < 1990)

    # the DCOOD cross-tab: by-right eligibility
    dcood = Counter(str(p.get("DCOOD")) for p in feats)
    in_overlay = dcood.get("Yes", 0)

    status = Counter(str(p.get("BuildingStatus")) for p in feats)

    # the oldest entitlements, and what is still being built under them
    oldest = sorted(
        ({"case": c, "n_buildings": len(v), "year": year(c),
          "status_mix": dict(Counter(str(x.get("BuildingStatus")) for x in v)),
          "total_gfa": sum((x.get("GFA") or 0) for x in v),
          "examples": [str(x.get("BuildingName"))[:44] for x in v[:4]]}
         for c, v in by_case.items() if year(c) and year(c) < 1990),
        key=lambda r: (r["year"], -r["n_buildings"]))

    out = {
        "purpose": ("Whether the entitlement pathway ever asks how much water a "
                    "data center will use. It does not, and this quantifies why."),
        "n_buildings": n,
        "planning_case": {
            "populated": len(with_case),
            "absent": n - len(with_case),
            "absent_pct": round(100 * (n - len(with_case)) / n, 1),
            "by_type": dict(by_type.most_common()),
            "case_type_meanings": CASE_TYPES,
        },
        "THE_FINDING": {
            "buildings_with_a_sup": n_sup,
            "of_total": n,
            "statement": (
                f"{n_sup} of {n} data-center buildings in Prince William County has a "
                f"Special Use Permit as its planning case. The SUP is the county's only "
                f"discretionary review -- the instrument through which conditions are "
                f"attached to a specific proposed use. It was never invoked."),
            "mechanism": (
                "Data centers are permitted BY RIGHT in the Data Center Opportunity "
                "Overlay District in the O(L), O(H), O(M), O(F), M-1, M-2 and M/T zoning "
                "districts, and in designated office or industrial land bays in PBD and "
                "PMD. A SUP is triggered only by exceeding the by-right envelope -- "
                "height or floor-area ratio -- not by the use itself. A data center built "
                "to 75 feet at 0.5 FAR inside the overlay generates no SUP, no conditions, "
                "no staff report, and no water discussion of any kind."),
            "source": ("PWC Planning Office staff report, SUP2023-00006 Gainesville East "
                       "Data Center (Dec 2024), Comprehensive Plan Consistency Analysis; "
                       "PWC Zoning Ordinance Sec. 32-509.02"),
        },
        "by_right_eligibility": {
            "inside_dcood": in_overlay,
            "outside_dcood": n - in_overlay,
            "inside_pct": round(100 * in_overlay / n, 1),
        },
        "building_status": dict(status.most_common()),
        "entitlement_vintage": {
            "by_year": dict(sorted(vintage.items())),
            "pre_1990_buildings": pre1990,
            "pre_1990_pct": round(100 * pre1990 / n, 1),
            "oldest_entitlements": oldest,
            "why_it_matters": (
                "An entitlement runs with the land. Where the approval predates the "
                "industry, no water condition could have been contemplated and none can "
                "now be retrofitted -- there is no open approval to condition. This is "
                "the answer to the obvious question 'why doesn't the county just attach "
                "water conditions?': for a substantial share of the fleet, it cannot."),
        },
        "instrument_chain": [
            {"stage": "pre-submission", "instrument": "Perennial Flow Determination",
             "captures": "whether a perennial stream exists on the parcel"},
            {"stage": "application form", "instrument": "SUP Supplemental Information",
             "captures": "NOTHING -- the form has no field for water use or power. It "
                         "asks for maximum number of children and automotive bays."},
            {"stage": "plans", "instrument": "Environmental Constraints Analysis",
             "captures": "wetlands, RPA, floodplain, soils, specimen trees"},
            {"stage": "narrative", "instrument": "Potable Water guideline",
             "captures": "how water will be PROVIDED TO the site -- supply, not demand"},
            {"stage": "narrative", "instrument": "SB 549 impact identification",
             "captures": "n/a -- residential rezonings only"},
            {"stage": "review", "instrument": "Prince William Water review ($86.25)",
             "captures": "pipe diameter"},
            {"stage": "approval", "instrument": "proffers / SUP conditions",
             "captures": "$75/acre water QUALITY; water QUANTITY unpriced"},
        ],
        "price_asymmetry": {
            "case": "SUP2023-00006, Amazon Data Services, Gainesville East",
            "building_area_sqft": 1_297_200,
            "water_quality_contribution_usd": 4390.50,
            "fire_and_rescue_contribution_usd": 791292.00,
            "ratio_fire_to_water": round(791292.00 / 4390.50, 1),
            "water_share_of_total_exactions_pct": round(
                100 * 4390.50 / (4390.50 + 791292.00), 2),
            "note": ("The county requires a licensed acoustical study of the cooling "
                     "system TWICE per building -- before each building permit and again "
                     "one month after each occupancy permit -- and imposes no condition "
                     "whatsoever on how much water that same cooling system consumes."),
            "source": "PWC staff report SUP2023-00006, Level of Service table, p.4",
        },
        "review_fee_asymmetry": {
            "sup_application_data_center_category_I_usd": 17209.06,
            "traffic_impact_study_first_submission_usd": 2059.13,
            "prince_william_water_review_usd": 86.25,
            "traffic_to_water_ratio": round(2059.13 / 86.25, 1),
            "note": ("Data centers sit in fee Category I -- the county's HIGHEST "
                     "environmental-hazard tier, alongside asphalt plants, HAZMAT "
                     "storage and motor vehicle graveyards. The county has not "
                     "misclassified them as benign; it charges the top fee and still "
                     "collects no water quantity."),
            "source": "PWC FY2026 Application Package for Special Use Permits (July 2025), fee schedule",
        },
    }

    json.dump(out, open(OUT, "w"), indent=1)

    F = out["THE_FINDING"]
    print("THE ENTITLEMENT PATHWAY\n")
    print(f"  buildings                      {n}")
    print(f"  with a planning case           {len(with_case)} ({100*len(with_case)/n:.0f}%)")
    print(f"  planning case types            {dict(by_type.most_common())}")
    print(f"  *** WITH A SPECIAL USE PERMIT  {n_sup} ***")
    print(f"  inside the DCOOD (by right)    {in_overlay} ({100*in_overlay/n:.0f}%)")
    print()
    print(f"  entitled under pre-1990 approvals: {pre1990} buildings")
    for r in oldest[:4]:
        print(f"     {r['case']:<16} {r['n_buildings']:>3} buildings  {r['status_mix']}")
    print()
    print(f"  fire & rescue is charged at {out['price_asymmetry']['ratio_fire_to_water']}x "
          f"the water-quality contribution")
    print(f"  traffic review costs {out['review_fee_asymmetry']['traffic_to_water_ratio']}x "
          f"what water review costs")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
