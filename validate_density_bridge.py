"""
Validate the GFA -> MW density bridge against site-level interconnection capacity.

WHY THIS IS POSSIBLE
--------------------
The estimator derives power as GFA / 8,818 sqft-per-MW. That constant is run
BACKWARD relative to its source: ICPRB used it once to convert Loudoun Water's
0.017 gal/day/sqft into the 150 gal/MW/day air-cooled tier, and takes power from
air-permit generator capacity, never from floor area. The bridge is the single
largest swing factor in the model (64%), and nothing published validates it in
the direction we use it.

Two public datasets can be joined to test it:

  1. VADEQ "Issued Air Permits for Data Centers" -- permit site names enumerate
     the buildings each permit covers ("IAD-73 IAD-74 IAD-602 IAD-193 IAD-194").
  2. interconnection.fyi -- carries a capacity BUCKET per facility, and its
     facility names are the same legal-entity strings as the DEQ site names.

Joining them yields, for a given permit site, both a set of named buildings AND
an interconnection capacity bucket. Summing this model's GFA-derived power over
those buildings and comparing to the bucket is a genuine test of the bridge --
nothing in the chain was fitted to anything else in it.

WHAT IS AND IS NOT BEING COMPARED
---------------------------------
Interconnection capacity is grid service sized for the WHOLE facility, so the
right comparison is facility load, not IT load:

    facility_load_MW = effective_IT_MW x PUE

using the same PUE this model already assigns per building. Two caveats that
both push the same way:

  - An interconnection request is an entitlement CEILING, generally sized for
    ultimate build-out, so the bucket should sit at or above actual load.
  - Where a permit covers buildings absent from the county dataset (mostly
    2025-26 permits for unbuilt structures), our sum covers only part of the
    site and will read low. Coverage is reported per site so this is visible.

A site therefore "agrees" if our facility-load estimate falls at or below the
top of the bucket. Falling far below is expected where coverage is partial;
falling ABOVE the ceiling is the informative failure.
"""
import json
import re
import sys

PROFILES = "public/data/facility_profiles.json"
PERMITS = "data/vadeq_air_permits_pwc.json"

# interconnection.fyi capacity buckets -> (low, high) MW. "250+" has no stated
# ceiling; 400 is used only for display and never for an agreement test.
BUCKETS = {
    "< 10 MW": (0, 10),
    "10-25 MW": (10, 25),
    "25-50 MW": (25, 50),
    "50-100 MW": (50, 100),
    "100-250 MW": (100, 250),
    "250+ MW": (250, None),
}


def building_codes(name):
    """Same parser as build_vadeq_permits.py -- handles both the space-separated
    form and the slash-continued form where a prefix is stated once."""
    codes = []
    for m in re.finditer(r'\b(IAD|DCA|MNZ|NVA|VA)[- ]?(\d+[A-Za-z]?)((?:\s*/\s*\d+[A-Za-z]?)*)', name):
        prefix, first, rest = m.group(1), m.group(2), m.group(3)
        codes.append(f"{prefix}-{first}".upper())
        for tail in re.findall(r'\d+[A-Za-z]?', rest or ''):
            codes.append(f"{prefix}-{tail}".upper())
    return list(dict.fromkeys(codes))


def norm(s):
    return re.sub(r'[^a-z0-9]', '', (s or '').lower())


# Building codenames are NOT unique across operators: "VA-10" is both NTT's
# Grove at Gainesville VA10 and Iron Mountain Data Center VA-10. Matching on the
# code alone silently picks whichever appears first in the file, which produced a
# 4 MW reading for a 561,000 sqft building. The join must therefore be
# operator-aware -- permit site names always carry the operator.
OPERATOR_ALIASES = {
    "amazon": ["amazon", "aws"],
    "microsoft": ["microsoft"],
    "ntt": ["ntt"],
    "digital realty": ["digital realty", "dlr"],
    "equinix": ["equinix"],
    "iron mountain": ["iron mountain"],
    "qts": ["qts"],
    "stack": ["stack", "si nva"],
    "cloudhq": ["cloudhq", "cloud hq"],
    "corporate office properties": ["corporate office properties", "copt"],
    "oath": ["oath"],
    "comcast": ["comcast"],
}


def site_operator(site_name):
    s = (site_name or "").lower()
    for canonical, aliases in OPERATOR_ALIASES.items():
        if any(a in s for a in aliases):
            return canonical
    return None


def match_buildings(code, buildings, operator=None):
    """Return every building record carrying this exact codename.

    Matching is on the codename PARSED OUT of the building name, compared for
    equality -- not on substring. Substring matching silently made "IAD-7" match
    IAD-74, IAD-73 and IAD-77 as well, inflating a three-building site.

    A code can legitimately map to more than one record (IAD-64 and IAD-64 Ext
    are separate structures on one permit), and both draw from the same
    interconnection, so all matches are returned and summed by the caller.
    """
    if not code:
        return []
    aliases = OPERATOR_ALIASES.get(operator or "", [])
    out = []
    for b in buildings:
        name = b.get("name") or ""
        if code.upper() not in building_codes(name):
            continue
        if aliases and not any(norm(a) in norm(name) for a in aliases):
            continue
        out.append(b)
    return out


def main():
    profiles = json.load(open(PROFILES))
    buildings = [b for b in profiles["buildings"] if b.get("scope_water_footprint")]
    icfyi = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/icfyi.json"))

    print("Density bridge validation: GFA-derived facility load vs interconnection capacity\n")
    print(f"{'permit site':<46}{'bucket':>12}{'bldgs':>7}{'IT MW':>8}{'fac MW':>8}  verdict")
    print("-" * 100)

    rows, over, under, partial = [], 0, 0, 0
    for site_name, bucket in icfyi:
        codes = building_codes(site_name)
        if not codes:
            continue
        op = site_operator(site_name)
        codes_hit, by_id = [], {}
        for c in codes:
            found = match_buildings(c, buildings, op)
            if found:
                codes_hit.append(c)
            for b in found:
                # Dedupe on the BUILDING id, not gpin. GPIN is the parcel, and a
                # campus routinely puts several buildings on one -- IAD-100/101/
                # 102/103 all sit on 7695-62-8723. Keying by gpin collapsed four
                # buildings into one and under-read the site by 4x.
                by_id[b["id"]] = b
        hits = list(by_id.values())
        if not hits:
            continue

        it_mw = sum(b["scope_water_footprint"]["power"]["effective_it_mw_central"] for b in hits)
        fac_mw = 0.0
        for b in hits:
            p = b["scope_water_footprint"]
            pue_lo, pue_hi = p["scope2_electricity"]["pue_range"]
            fac_mw += p["power"]["effective_it_mw_central"] * (pue_lo + pue_hi) / 2

        lo, hi = BUCKETS[bucket]
        coverage = len(codes_hit) / len(codes)
        if hi is not None and fac_mw > hi:
            verdict, flag = "OVER ceiling", "over"
            over += 1
        elif fac_mw < lo:
            verdict = "below floor" + (f" (only {len(codes_hit)}/{len(codes)} bldgs)" if coverage < 1 else "")
            flag = "under"
            under += 1
        else:
            verdict, flag = "in bucket", "in"
            under += 0
        if coverage < 1:
            partial += 1

        short = (site_name[:43] + "...") if len(site_name) > 46 else site_name
        print(f"{short:<46}{bucket:>12}{len(codes_hit):>3}/{len(codes):<3}{it_mw:>8.0f}{fac_mw:>8.0f}  {verdict}")
        rows.append({"site": site_name, "bucket": bucket, "n_matched": len(codes_hit), "n_buildings": len(hits),
                     "n_codes": len(codes), "it_mw": round(it_mw, 1),
                     "facility_mw": round(fac_mw, 1), "flag": flag})

    print("-" * 100)
    print(f"{len(rows)} permit sites tested | {over} exceed the interconnection ceiling "
          f"| {partial} have partial building coverage")

    full = [r for r in rows if r["n_matched"] == r["n_codes"]]
    if full:
        print(f"\nSites with FULL building coverage ({len(full)}) -- the clean comparisons:")
        for r in full:
            lo, hi = BUCKETS[r["bucket"]]
            ratio = r["facility_mw"] / lo if lo else float("inf")
            print(f"  {r['site'][:52]:<54} {r['facility_mw']:>6.0f} MW vs {r['bucket']:>10}"
                  f"   {ratio:.2f}x the bucket floor")

    json.dump(rows, open("data/density_bridge_validation.json", "w"), indent=1)
    print("\nwrote data/density_bridge_validation.json")


if __name__ == "__main__":
    main()
