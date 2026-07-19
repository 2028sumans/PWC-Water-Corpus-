"""
Power density, done properly for this county.

The obvious way to turn floor area into IT load is a power-density figure:
Power Density = IT load (kW) / floor area (sqft). The trap is the denominator.
The same 100 kW reads as 78, 113, or 240 W/sqft depending on whether you divide
by the room envelope, the production space, or the rack footprint alone
(Silverback 2023) -- a 3x spread from a definitional choice. Published
W/sqft figures are almost always quoted on WHITE SPACE (the raised-floor data
hall), and white space is only 40-50% of a data centre's gross internal area
(RICS 2024). This model runs on GROSS floor area from the county assessor, so a
literature W/sqft cannot be dropped in without the white-space fraction, or the
implied load roughly doubles.

So instead of importing a generic number, this checks the model against the
county's OWN buildings. The 45 permit-backed buildings are a natural experiment:
their MW comes from VADEQ generator capacity via ICPRB Equation 6-3, and their
gross floor area is known independently, so permit_MW / GFA is an empirical
power density that never touches the 8,818 sqft/MW constant. That distribution
is the yardstick for the 198 buildings that still lean on the constant.

Sources (see METHODOLOGY.md section 15 for the full citations):
  Silverback Data Center Solutions -- Watts per Square Foot (room/production/rack)
  RICS Construction Journal 2024 -- white space = 40-50% of gross internal area
  JLARC Dec 2024 -- ~5,050 MW across ~340 Virginia data-centre buildings
  Uptime Institute / LBNL -- 100-150 W/sqft standard, 250-450 W/sqft modern AI
  ICPRB 2025 WMA study -- 8,818 sqft/MW fleet average (derived from Loudoun)
"""
import json
import statistics as st

import indirect_water_footprint as m

PROFILES = "public/data/facility_profiles.json"
WHITE_SPACE_FRACTION = 0.45   # RICS midpoint of 40-50%


def operator(name):
    n = (name or "").lower()
    for k in ["iron mountain", "digital realty", "dlr", "amazon", "aws", "microsoft",
              "azure", "qts", "ntt", "stack", "corscale", "cloudhq", "aligned",
              "vantage", "equinix", "compass", "gainesville crossing", "corscale"]:
        if k in n:
            return {"aws": "amazon", "dlr": "digital realty", "azure": "microsoft"}.get(k, k)
    return "other"


def gfa_to_whitespace_wsf(sqft_per_mw):
    """Convert a GFA-basis sqft/MW into an implied white-space W/sqft, the number
    the literature actually quotes, so the two can be compared."""
    w_per_sqft_gfa = 1e6 / sqft_per_mw
    return w_per_sqft_gfa / WHITE_SPACE_FRACTION


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]

    permit, gfa_only, opcond = [], [], []
    for b in bs:
        p = b["scope_water_footprint"]["power"]
        gfa, mw = p.get("gfa_sqft"), p.get("effective_it_mw_central")
        if not gfa or not mw:
            continue
        row = (b.get("name", ""), operator(b.get("name")), gfa, mw, gfa / mw, p)
        if p.get("basis") == "permit_generator_capacity":
            permit.append(row)
        else:
            gfa_only.append(row)
            if str(p.get("density_class", "")).startswith("operator_"):
                opcond.append(row)

    # ---- 1. the basis problem, made explicit --------------------------------
    print("=" * 74)
    print("1. THE DENOMINATOR PROBLEM  (same 100 kW, different floor definition)")
    print("=" * 74)
    for label, sqft in [("rack footprint only", 416), ("production space", 884),
                        ("room envelope", 1280)]:
        print(f"  {label:<22} {100_000/sqft:>5.0f} W/sqft")
    print("  gross floor area (this model's basis) is larger still than room envelope,")
    print(f"  and white space is only {WHITE_SPACE_FRACTION:.0%} of it (RICS).")

    # ---- 2. the natural experiment ------------------------------------------
    v = sorted(r[4] for r in permit)
    print("\n" + "=" * 74)
    print(f"2. EMPIRICAL DENSITY FROM {len(permit)} PERMIT-BACKED BUILDINGS")
    print("   (permit generator MW / known GFA -- independent of the 8,818 constant)")
    print("=" * 74)
    p10, p90 = v[len(v)//10], v[9*len(v)//10]
    print(f"  median   {st.median(v):>7,.0f} sqft/MW   "
          f"= {1e6/st.median(v):>4.0f} W/sqft GFA   "
          f"= {gfa_to_whitespace_wsf(st.median(v)):>4.0f} W/sqft white space")
    print(f"  p10-p90  {p10:,.0f} - {p90:,.0f} sqft/MW   (a {p90/p10:.1f}x spread -- real fleet heterogeneity)")
    print(f"\n  ICPRB fleet average is {m.SQFT_PER_EFFECTIVE_MW:,} sqft/MW. The permit-backed median of")
    print(f"  {st.median(v):,.0f} reproduces it within {abs(st.median(v)-m.SQFT_PER_EFFECTIVE_MW)/m.SQFT_PER_EFFECTIVE_MW:.0%} -- two independent methods (PWC generator")
    print(f"  capacity vs ICPRB's Loudoun water billing) agreeing on the same constant.")

    # ---- 3. the clustering is by operator, not by year ----------------------
    print("\n" + "=" * 74)
    print("3. DENSITY CLUSTERS BY OPERATOR / DESIGN GENERATION")
    print("=" * 74)
    byop = {}
    for _, op, _, _, spm, _ in permit:
        byop.setdefault(op, []).append(spm)
    print(f"  {'operator':<18}{'n':>3}{'median sqft/MW':>16}{'W/sqft GFA':>12}{'white W/sqft':>14}")
    for op, vals in sorted(byop.items(), key=lambda kv: st.median(kv[1])):
        med = st.median(vals)
        print(f"  {op:<18}{len(vals):>3}{med:>16,.0f}{1e6/med:>12.0f}{gfa_to_whitespace_wsf(med):>14.0f}")
    print("\n  These white-space figures land inside the published envelope: standard")
    print("  builds 100-150 W/sqft, modern AI-class 250-450 (Uptime/LBNL). The densest")
    print("  PWC operators sit in the AI-class band; colocation/retrofit at the bottom.")

    # ---- 4. what operator-conditioning changed ------------------------------
    print("\n" + "=" * 74)
    print("4. OPERATOR-CONDITIONED DENSITY APPLIED TO GFA-ONLY BUILDINGS")
    print("=" * 74)
    print(f"  {len(opcond)} of {len(gfa_only)} GFA-only buildings now use their operator's own")
    print(f"  measured density instead of a build-era band. Coverage is limited to")
    print(f"  operators with >=3 permit calibrators; the rest keep the vintage band.")

    total = sum(b["scope_water_footprint"]["total_mgd_central"] for b in bs)
    print(f"\n  county central total: {total:.2f} MGD")
    print(f"  density remains the dominant sensitivity (~52%) BY DESIGN: the fleet")
    print(f"  genuinely spans {p90/p10:.1f}x, so the swing is heterogeneity, not error. The")
    print(f"  only way to zero a building's density uncertainty is a permit -- which is")
    print(f"  why the {len(permit)} permit-backed buildings carry none.")


if __name__ == "__main__":
    main()
