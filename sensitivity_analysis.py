"""
One-at-a-time sensitivity sweep over the Scope 1/2/3 estimator.

Varies each constant across its plausible range, holds all others fixed, and
ranks by the resulting swing in the county-wide central total. Answers the
question the range bands cannot: which assumption actually drives the number?
"""
import json
import indirect_water_footprint as m

PROFILES = "public/data/facility_profiles.json"


def county_total(density=None, wup_pwc=None, wup_air=None, wup_water=None,
                 nuclear_cf=None, gas_cf=None, pue_scale=None, s3_frac=None):
    """Recompute the county-wide central total with one constant overridden."""
    density = density or m.SQFT_PER_EFFECTIVE_MW
    wup_pwc = wup_pwc or m.WUP_GAL_PER_MW_DAY["pwc_observed"]
    wup_air = wup_air or m.WUP_GAL_PER_MW_DAY["air_cooled"]
    nuclear_cf = nuclear_cf if nuclear_cf is not None else m.CONSUMPTION_FACTORS_GAL_PER_MWH["nuclear"]
    gas_cf = gas_cf if gas_cf is not None else m.CONSUMPTION_FACTORS_GAL_PER_MWH["natural_gas_cc"]
    pue_scale = pue_scale or 1.0
    s3_frac = s3_frac if s3_frac is not None else 0.10

    mix = m.DOMINION_GENERATION_MIX
    cf = dict(m.CONSUMPTION_FACTORS_GAL_PER_MWH)
    cf["nuclear"] = nuclear_cf
    cf["natural_gas_cc"] = gas_cf
    blended = sum(mix[f] * cf[f] for f in mix)

    data = json.load(open(PROFILES))
    s1_tot = s2_tot = 0.0
    for b in data["buildings"]:
        swf = b.get("scope_water_footprint")
        if not swf:
            continue
        # Buildings whose power comes from a VADEQ permit do not depend on the
        # density constant at all -- their MW is generator capacity x ICPRB's
        # Equation 6-3 factors. Varying density must leave them untouched, or
        # the sweep reports a sensitivity the model no longer has.
        if swf["power"].get("basis") == "permit_generator_capacity":
            mw = swf["power"]["effective_it_mw_central"]
        else:
            mw = swf["power"]["gfa_sqft"] / density

        basis = swf["scope1_onsite_cooling"]["basis"]
        wup = wup_air if basis == "operator_closed_loop_commitment" else wup_pwc
        s1_tot += mw * wup / 1e6

        pue_lo, pue_hi = swf["scope2_electricity"]["pue_range"]
        # Perturb by evidence quality, not uniformly. A building carrying its
        # operator's own published fleet PUE is not as uncertain as one assigned
        # a vintage class, so applying the same +/-15% to both would report a
        # sensitivity the model no longer has -- the same mistake the nuclear
        # factor showed when an assumed 100-800 span was replaced by a measured
        # 189-289 one. Disclosed figures get the +/-0.06 site-vs-fleet tolerance.
        s = pue_scale
        if swf["scope2_electricity"].get("pue_class") == "operator_disclosed" and pue_scale != 1.0:
            mid = (pue_lo + pue_hi) / 2
            s = 1.0 + (pue_scale - 1.0) * (0.06 / mid) / 0.15
        pue = ((pue_lo + pue_hi) / 2) * s
        s2_tot += mw * pue * 24 * blended / 1e6

    s3_tot = (s1_tot + s2_tot) * s3_frac
    return s1_tot + s2_tot + s3_tot


BASE = county_total()

# (label, low-case kwargs, high-case kwargs, justification for the span)
CASES = [
    ("Infrastructure density (sqft/MW)",
     {"density": 12722}, {"density": 8818 * 0.75},
     "8,818 (JLARC) vs 12,722 implied by ICPRB's own Fairfax figures; low end -25%"),
    ("Nuclear consumption factor (gal/MWh)",
     {"nuclear_cf": 189}, {"nuclear_cf": 289},
     "USGS MIN/MAX_CONSUMPTION for Surry + North Anna, generation-weighted "
     "(was an assumed 100-800 span before the USGS pull)"),
    ("PUE band (scale factor)",
     {"pue_scale": 0.85}, {"pue_scale": 1.15},
     "+/-15% on vintage-classed buildings; +/-0.06 (site vs fleet) on the 61 "
     "carrying an operator's own published fleet PUE"),
    ("Scope 3 proportional fraction",
     {"s3_frac": 0.05}, {"s3_frac": 0.15},
     "the shipped 5-15% band"),
    ("Gas CC consumption factor (gal/MWh)",
     {"gas_cf": 210}, {"gas_cf": 225},
     "USGS MIN/MAX_CONSUMPTION across the 4 VA NGCC plants, generation-weighted "
     "(was an assumed 130-300 dry-vs-wet-cooling span before the USGS pull)"),
    ("Scope 1 WUP central (gal/MW/day)",
     {"wup_pwc": 150}, {"wup_pwc": 1577},
     "full measured technology envelope, air-cooled to fully evaporative"),
]

print(f"BASE county-wide central total: {BASE:.2f} MGD\n")
print(f"{'Constant':<40}{'Low':>9}{'High':>9}{'Swing':>10}{'% of base':>11}")
print("-" * 79)

rows = []
for label, lo_kw, hi_kw, _ in CASES:
    lo, hi = county_total(**lo_kw), county_total(**hi_kw)
    rows.append((label, lo, hi, abs(hi - lo)))

for label, lo, hi, swing in sorted(rows, key=lambda r: -r[3]):
    print(f"{label:<40}{lo:>9.2f}{hi:>9.2f}{swing:>10.2f}{100*swing/BASE:>10.0f}%")

print("\nJustification for each span:")
for label, _, _, note in CASES:
    print(f"  {label}\n    {note}")

# The specific claim in METHODOLOGY.md 6.8, tested directly.
print("\n" + "=" * 79)
print("Does Scope 1 evidence move the headline? (METHODOLOGY.md 6.8)")
all_env = county_total(wup_pwc=309, wup_air=309)   # no narrowing at all
all_narrow = county_total(wup_pwc=150, wup_air=150)  # every building narrowed
print(f"  every building un-narrowed (309): {all_env:.2f} MGD")
print(f"  every building narrowed  (150):   {all_narrow:.2f} MGD")
print(f"  total spread from ALL Scope 1 evidence: {abs(all_env-all_narrow):.2f} MGD "
      f"({100*abs(all_env-all_narrow)/BASE:.1f}% of base)")
