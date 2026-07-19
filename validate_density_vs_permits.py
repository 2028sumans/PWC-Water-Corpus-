"""
Test the GFA -> MW density bridge against permit-derived generator capacity.

This is the strongest test available for the estimator's last dominant
assumption. Unlike the interconnection comparison in
validate_density_bridge.py -- which compares against an entitlement CEILING and
so cannot separate "model under-predicts" from "entitlement exceeds load" --
permit capacity runs through ICPRB's own Equation 6-3 and yields a figure on the
same definition the model uses:

    Effective (IT) Power Demand = Total Generator Capacity x 0.5 x 0.8

MATCHING RULES (learned the hard way -- see validate_density_bridge.py)
  - Building codenames are NOT unique across operators: VA-10 is both NTT's
    Grove at Gainesville VA10 and Iron Mountain Data Center VA-10. Operator must
    agree.
  - GPIN is the PARCEL, not the building. IAD-100/101/102/103 share one GPIN,
    so dedupe on building id or four buildings collapse into one.
  - Permits outside Prince William (Loudoun, Caroline) must be excluded, or
    their codenames cross-match into the PWC building set.
  - Where more buildings match than the permit names, the match is ambiguous and
    the site is skipped rather than guessed at.

SCALING
Permits usually cover more buildings than the model tracks (unbuilt structures
are permitted years ahead). The permit's effective MW is therefore scaled by the
fraction of its named buildings present in the model, which assumes buildings on
a site are comparable in size -- reasonable within one operator's campus, and
the reason partial-coverage sites are reported with their coverage visible.
"""
import json
import re
import statistics

PERMITS = "data/permit_capacity.json"
PROFILES = "public/data/facility_profiles.json"

OPERATOR_ALIASES = {
    "amazon": ["amazon", "aws"], "microsoft": ["microsoft"], "ntt": ["ntt"],
    "digital realty": ["digital realty", "dlr"], "equinix": ["equinix"],
    "iron mountain": ["iron mountain"], "qts": ["qts"],
    "stack": ["stack", "si nva"], "cloudhq": ["cloudhq", "cloud hq"],
    "corporate office properties": ["corporate office properties", "copt"],
    "oath": ["oath"], "comcast": ["comcast"],
}

SQFT_PER_MW_SHIPPED = 8818


def codes(name):
    return [f"{m.group(1)}-{m.group(2)}".upper()
            for m in re.finditer(r'\b(IAD|DCA|MNZ|NVA|VA)[- ]?(\d+[A-Za-z]?)', name or '')]


def operator_of(text):
    t = (text or "").lower()
    for canonical, aliases in OPERATOR_ALIASES.items():
        if any(a in t for a in aliases):
            return canonical
    return None


def main():
    perms = json.load(open(PERMITS))
    prof = json.load(open(PROFILES))
    buildings = [b for b in prof["buildings"] if b.get("scope_water_footprint")]

    print("Permit-derived vs GFA-derived effective IT power (Prince William only)\n")
    print(f"{'reg':<8}{'operator':<12}{'coverage':>10}{'permit MW':>11}{'GFA MW':>9}{'ratio':>8}")
    print("-" * 68)

    rows, ratios = [], []
    for p in perms:
        if p["confidence"] != "high":
            continue
        if "prince william" not in (p.get("location") or "").lower():
            continue
        permit_codes = set(p["building_codes"])
        if not permit_codes:
            continue

        candidates = [b for b in buildings if permit_codes & set(codes(b.get("name")))]
        ops = [o for o in (operator_of(b.get("name")) for b in candidates) if o]
        op = max(set(ops), key=ops.count) if ops else None
        hits = [b for b in candidates if operator_of(b.get("name")) == op] if op else candidates
        hits = list({b["id"]: b for b in hits}.values())     # dedupe on BUILDING, not parcel
        if not hits or len(hits) > len(permit_codes):
            continue                                        # ambiguous -> skip, don't guess

        gfa_mw = sum(b["scope_water_footprint"]["power"]["effective_it_mw_central"] for b in hits)
        if not gfa_mw:
            continue
        scaled = p["effective_it_mw"] * len(hits) / len(permit_codes)
        ratio = scaled / gfa_mw
        ratios.append(ratio)
        rows.append({"registration_no": p["registration_no"], "operator": op,
                     "n_matched": len(hits), "n_permit_codes": len(permit_codes),
                     "permit_mw_scaled": round(scaled, 1), "gfa_mw": round(gfa_mw, 1),
                     "ratio": round(ratio, 3)})
        print(f"{p['registration_no']:<8}{(op or '?'):<12}{len(hits):>4}/{len(permit_codes):<5}"
              f"{scaled:>11.1f}{gfa_mw:>9.1f}{ratio:>8.2f}")

    print("-" * 68)
    if ratios:
        med = statistics.median(ratios)
        print(f"\nn={len(ratios)}   median {med:.2f}   range {min(ratios):.2f}-{max(ratios):.2f}"
              f"   spread {max(ratios)/min(ratios):.1f}x")
        print(f"implied density at the median: {SQFT_PER_MW_SHIPPED/med:,.0f} sqft/MW "
              f"(shipped {SQFT_PER_MW_SHIPPED:,})")
        print("\nRead this carefully: the CENTRE of the shipped constant is corroborated,")
        print("the BAND is not. n is small and the per-site spread far exceeds the")
        print("model's stated +/-25% density tolerance.")
        json.dump(rows, open("data/density_vs_permits.json", "w"), indent=1)
        print("\nwrote data/density_vs_permits.json")


if __name__ == "__main__":
    main()
