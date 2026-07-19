# Scope 1/2/3 Water Footprint Estimator — Methodology, Worked Example, and Known Gaps

**Status:** as-shipped.
**Source of truth:** [`indirect_water_footprint.py`](indirect_water_footprint.py). Every number below was read out of that module, recomputed from the built [`public/data/facility_profiles.json`](public/data/facility_profiles.json), or quoted directly from a source document in [`public/data/policy/`](public/data/policy/). None of it is written from memory.

This document exists to be attacked. Section 6 lists the errors and soft spots found so far — including one retraction, one circular validation, and one constant that the source document uses in the opposite direction from this tool.

---

## 0. What the model is, in one paragraph

Every estimate descends from a single physical input — **gross floor area** — converted to **effective electrical load** by one constant, then multiplied by scope-specific water intensities. There is no per-facility water measurement anywhere in the chain. Following the July 2026 USGS pull, the Scope 2 intensities are Virginia-specific measured values; the power spine is not, and it is now the only remaining dominant assumption.

```
GFA (sqft) ──÷ 8,818──> effective MW ──┬── × WUP (gal/MW/day) ─────────> Scope 1
                                       ├── × PUE × 24h × 198 gal/MWh ──> Scope 2
                                       └── (Scope 1 + Scope 2) × 5–15% ─> Scope 3
```

---

## 1. The power spine (upstream of all three scopes)

### 1.1 Equation

```
effective_MW_central = GFA_sqft / 8,818
effective_MW_low     = GFA_sqft / (8,818 × 1.25)
effective_MW_high    = GFA_sqft / (8,818 × 0.75)
```

### 1.2 What ICPRB actually did — and why this is backwards

ICPRB never derives megawatts from floor area. Their Equation 6-3 is:

> **Effective (IT) Power Demand = Total Generator Power Capacity × Redundancy × Utilization Factor**

with redundancy 0.5 ("permitted generator capacity typically represents twice the actual IT power load, i.e. 2N backup systems") and utilization 0.8 ("data centers do not operate at full load continuously," per EPRI 2024). Power comes from **backup generator capacity in VADEQ air permits**, never from square footage.

The 8,818 figure appears exactly once, as a unit bridge (WMA study, p. 6-14):

> Holding the air-cooled WUP constant at 150 gallons/MW/day (value based on an estimate of **0.017 gallons/day/square foot**, provided by Loudoun Water **and an infrastructure density of 8,818 square feet per MW** based on the JLARC database)

`0.017 × 8,818 = 149.9`. It was built to convert a per-square-foot rate *into* a per-MW rate. **This tool runs it in reverse, which no source validates.**

Two consequences:

- For air-cooled facilities the round trip cancels: `(GFA/8,818) × 150 ≡ GFA × 0.017`. The megawatt figure does no work — AWS IAD-74's Scope 1 is literally Loudoun Water's per-sqft rate applied to floor area.
- For every other tier and for all of Scope 2, the constant does real, unvalidated predictive work.

### 1.3 ICPRB's own data contains a second, incompatible density

From the same page: Fairfax was estimated at 0.27 MGD using 90 gal/day/1,000 sqft, and assigned a WUP of 1,145 gal/MW/day. Those imply 3.0M sqft and 235.8 MW → **12,722 sqft/MW, 44% above 8,818** and outside this model's ±25% tolerance. The source document contains two densities that disagree by more than the model's stated uncertainty.

### 1.4 Range shape

The tolerance is applied to the divisor, so the MW range is asymmetric: **−20% / +34%**. No central value in this tool is the midpoint of its own range.

---

## 2. Scope 1 — on-site cooling

### 2.1 Equations

```
Scope1_low     = MW_low     × WUP_low     / 1e6
Scope1_high    = MW_high    × WUP_high    / 1e6
Scope1_central = MW_central × WUP_central / 1e6
Scope1_peak    = MW_central × 3,060       / 1e6
```

### 2.2 The WUP scale (gal/day per effective MW)

| Tier | Value | Provenance |
|---|---|---|
| `air_cooled` | 150 | 0.017 gal/day/sqft (Loudoun Water) × 8,818 |
| `pwc_observed` | **309** | **0.42 MGD ÷ 1,359 MW, Prince William Water 2023** |
| `basin_medium` | 800 | ICPRB basin-wide representative |
| `loudoun_observed` | 1,006 | 4.5 MGD ÷ effective MW, Loudoun Water 2024 |
| `fully_water_cooled` | 1,577 | implied 100%-evaporative ceiling |

All verified present in WMA study §6.2, p. 6-13. The 6.7× Prince William / Loudoun spread is **not noise** — it is the water-cooled share. Inverting on the physical tiers, `(309−150)/(1577−150)` ≈ **11% water-cooled in PWC** against Loudoun's stated ~60–70%. Cooling technology is the dominant physical variable, and this spread quantifies it.

### 2.3 Narrowing precedence

1. **`disclosed_cooling`** — binding permit condition → WUP `150 / 150 / 225`. **Never fires** (see §6.9).
2. **`operator_closed_loop_commitment`** — public closed-loop commitment → `150 / 150 / 309`. **56 buildings.**
3. **`technology_envelope`** (default) → `150 / 309 / 1,577`. **146 buildings.**

A commitment maps onto ICPRB's measured air-cooled tier rather than substituting the operator's published WUE, because a global fleet WUE uses a different accounting boundary than ICPRB's per-effective-MW scale. Consequence: the model can never resolve below 150 gal/MW/day.

### 2.4 Consumptive-use factor

ICPRB's Equation 6-2 is `Consumptive Use = (Effective Power Demand × WUP) × Consumptive Use Factor`, with the factor at 0.75. This model computes `consumptive_mgd_central` but **does not apply it** to the headline. See §6.4.

---

## 3. Scope 2 — electricity-driven, at the generating plant

### 3.1 Equation

```
Scope2 = MW × PUE × 24 h/day × 197.6 gal/MWh / 1e6
```

### 3.2 Virginia-specific consumption factors (corrected July 2026)

Derived in [`usgs_va_factors.py`](usgs_va_factors.py) from USGS ScienceBase item `5f63be9a82ce38aaa23b0739` — *Water withdrawal and consumption estimates for thermoelectric power plants in the United States, 2015* (**ver. 1.2, July 2024**). USGS models withdrawal and consumption from a heat-and-water budget, so the estimates are independent of operator self-reporting. Units confirmed against the FGDC metadata: Mgal/d and annual MWh.

| Technology | Mix | **VA gal/MWh** | *(national median)* | Contribution | % of blend |
|---|---|---|---|---|---|
| Natural gas CC | 58% | **213** | *210* | 123.5 | 62.5% |
| Nuclear | 25% | **242** | *700* | 60.5 | 30.6% |
| Renewable | 14% | 0 | *0* | 0.0 | 0.0% |
| Coal | 3% | **451** | *687* | 13.5 | 6.8% |
| | | | | **197.6** | 100% |

**Blended factor: 317.4 → 197.6 gal/MWh (−38%). County-wide central total: 52.44 → 33.17 MGD (−37%).**

The nuclear correction is the substantive one. A single national median blended two Virginia plants with opposite profiles:

| Plant | EIA | USGS cooling type | Consumption | gal/MWh |
|---|---|---|---|---|
| Surry | 3806 | ONCE-THROUGH SALINE | 0.0 Mgal/d | **0** |
| North Anna | 6168 | COMPLEX (Lake Anna) | 18.6 Mgal/d | **417** |

Surry consumes nothing in USGS's model because heat discharges to a tidal estuary. Its withdrawal is 1,220 Mgal/d — enormous, non-consumptive, and **saline** rather than fresh. A national constant erases all three distinctions at once.

### 3.3 PUE ranges

```python
PUE_RANGE = {"modern": (1.08, 1.15),    # year_built >= 2020
             "standard": (1.20, 1.60),  # year_built < 2020
             "unknown": (1.10, 1.50)}   # year_built missing
```

As shipped: **146 `unknown`**, 34 `modern`, 22 `standard`.

### 3.4 Assumptions

| # | Assumption | Note |
|---|---|---|
| B1 | Location-based, system-average attribution | No marginal water-intensity dataset exists for PJM/Dominion (NREL Cambium is carbon-only). Honest constraint. |
| B2 | Renewables at 0 gal/MWh | A floor, not a measurement. Hydro has large evaporative consumption in NREL's tables; solar needs panel washing. |
| B3 | ×24 h/day on effective MW | **Correct, not an over-count.** ICPRB's 0.8 utilization factor is an explicit time-average ("do not operate at full load continuously"), so effective MW is already an average load. Both scopes inherit the same duty cycle from the shared input. |
| B4 | No market-based (PPA) accounting | See §6.7. |
| B5 | 2015 generation weights | The USGS release is 2015. Factors are intensities so this matters less than for absolute totals, but the weights are a decade old. |

---

## 4. Scope 3 — embodied / supply chain

```
Scope3_low     = (Scope1_low     + Scope2_low)     × 0.05
Scope3_high    = (Scope1_high    + Scope2_high)    × 0.15
Scope3_central = (Scope1_central + Scope2_central) × 0.10
```

**Not a physical estimate** — a proportional anchor to corporate disclosure ratios (Privette et al., *AGU Advances*, 2026). The code flags that one hyperscaler discloses embodied water at >99% of its corporate footprint, correctly characterising that as an accounting-boundary artifact rather than a per-facility ratio.

Structural consequences:

- Scope 3 **inherits and compounds** Scope 2's errors, since Scope 2 is ~87% of the base it multiplies. The errors multiply rather than add: an error in the density constant propagates into Scope 2, then again into Scope 3.
- The range compounds twice over: the low bound takes both scopes' lows *and* the low fraction, with nothing constraining the fraction to co-vary. The reported band is wider than any defensible joint distribution.

---

## 5. Worked example — Amazon AWS IAD-74 Manassas

GPIN `7596-17-3979` · Completed · built 2016 · GFA **148,580 sqft** (`REATaxedGFA`, quality `assessed`)

**Power**
```
148,580 / 8,818          = 16.8 MW   148,580 / (8,818×1.25) = 13.5 MW
148,580 / (8,818×0.75)   = 22.5 MW
```

**Scope 1** — `operator_closed_loop_commitment`, WUP 150 / 150 / 309
```
low     13.5 × 150   / 1e6 = 0.0020 MGD
central 16.8 × 150   / 1e6 = 0.0025 MGD
high    22.5 × 309   / 1e6 = 0.0070 MGD
peak    16.8 × 3,060 / 1e6 = 0.0514 MGD   ← see §6.3
```
Equivalently: `148,580 sqft × 0.017 gal/day/sqft = 2,526 gal/day`. The megawatt figure cancels entirely.

**Scope 2** — 2016 → `standard`, PUE 1.20–1.60, central 1.40
```
low     13.5 × 1.20 × 24 × 197.6 / 1e6 = 0.0768 MGD
central 16.8 × 1.40 × 24 × 197.6 / 1e6 = 0.1115 MGD
high    22.5 × 1.60 × 24 × 197.6 / 1e6 = 0.1707 MGD
```

**Scope 3**
```
low  (0.0020+0.0768)×0.05 = 0.0039    central (0.0025+0.1115)×0.10 = 0.0114
high (0.0070+0.1707)×0.15 = 0.0267
```

**Total** — envelope sum, *not* a confidence interval
```
low 0.0827   central 0.1254   high 0.2044   (2.47× wide)
```

Scope 2 is **88.9%** of the central estimate. The central is not the midpoint (0.1436).

**Benchmark:** S1 central 0.0025 < 0.0184 MGD (average large office building) → `typical_or_below`.

---

## 6. Known gaps, errors, and soft spots

### 6.1 🔴 The docstring validation is circular

The module claimed: `11,094,472 sqft / 8,818 = 1,258 MW × 309 = 0.389 MGD` vs PWC's measured 0.42 MGD, "within 7.4% of a measured number it was not fitted to."

But ICPRB derived 309 *from* that figure: `309 := 0.42 MGD ÷ 1,359 MW` (WMA p. 6-13, "WUP was then calculated by dividing utility reported data center water use by effective power demand"). Substituting, 0.42 cancels from both sides and the check reduces to `1,258 / 1,359` — **−7.4%, the identical number.**

The model was multiplied by a constant derived from the target and compared to the target. Its only real content is that GFA/8,818 lands 7.4% below ICPRB's generator-derived MW, for a *service area* whose boundary isn't the county. **It tests the power spine, not water use.** A genuine validation is available (§7) but requires a chain that never touches 309.

### 6.2 🔴 The methodology string contradicts the number it explains

`scope1_onsite_cooling()` emits "Central estimate uses the Prince William Water observed fleet average of 309 gal/MW/day" **regardless of basis**. On the 56 narrowed buildings the UI shows `central: 150` directly above prose asserting 309.

### 6.3 🔴 Peak-day ignores narrowing

`peak` always uses 3,060 gal/MW/day. For AWS IAD-74 that yields a 20× peak:average ratio where the documented ratio is 9.9×, and a peak **7.3× the facility's own Scope 1 upper bound**. A closed-loop facility cannot have an evaporation-driven peak day.

### 6.4 🟠 Withdrawal and consumption are summed

Scope 1 is water **delivered** (utility billing is what ICPRB divided). Scope 2 is water **consumed** at the plant. The model adds them. ICPRB's own Eq. 6-2 applies the 0.75 consumptive factor to reconcile; this model computes it and never uses it. Either apply it before summing or stop calling the total a footprint.

### 6.5 ✅ RETRACTED — the PUE multiplication is correct

Previously flagged as a probable 20–60% double-count, on the theory that ICPRB's effective MW was already whole-facility load. **Equation 6-3 disproves this**: ICPRB labels it "Effective **(IT)** Power Demand" and applies the 0.5 redundancy specifically because generator capacity "represents twice the actual IT power load." It is IT load by definition, so multiplying by PUE to reach facility load is right. Retained here as a record of the error.

### 6.6 ✅ RESOLVED — nuclear factor corrected

Was: ~49% of the headline traced to a 2011 national median for nuclear. Now Virginia-specific from USGS (§3.2). In the sensitivity sweep this constant fell from **54% swing to 12%**, because its span is now measured (189–289) rather than assumed (100–800).

### 6.7 🟠 No market-based Scope 2

The GHG Protocol requires both location-based and market-based accounting. Only location-based is implemented. Every major operator here holds renewable PPAs — this is the first thing a sophisticated operator will dispute, and they will be technically correct.

### 6.8 🟡 The reported range is still nearly insensitive to evidence

One-at-a-time sensitivity sweep ([`sensitivity_analysis.py`](sensitivity_analysis.py)), ranked by swing in the county-wide central total (base 33.18 MGD). Spans are measured where a source exists, assumed otherwise:

| Constant | Low | High | Swing | % of base |
|---|---|---|---|---|
| **Infrastructure density** | 23.00 | 44.24 | 21.24 | **64%** |
| PUE band | 28.41 | 37.94 | 9.54 | 29% |
| Scope 1 WUP central | 32.57 | 37.97 | 5.40 | 16% |
| Nuclear consumption factor | 31.04 | 35.07 | 4.02 | 12% |
| Scope 3 fraction | 31.67 | 34.68 | 3.02 | 9% |
| Gas CC factor | 32.90 | 34.30 | 1.40 | 4% |

Direct test — flipping **every** building between un-narrowed (309) and narrowed (150), i.e. the total value of all cooling evidence the tool collects:

**0.84 MGD — 2.5% of base.**

The disclosure audit, operator-commitment matching, and permit parsing together move the headline 2.5%, while the density constant moves it 64%. Collecting facility evidence is close to decorative until §7.1 lands.

### 6.9 🟡 Smaller items

- **44% of buildings (89/202) use `proffer_split` GFA** — a site entitlement divided evenly among buildings sharing an identical figure. Even division has no support.
- **`disclosed_cooling` is dead code.** Only `SUP2025-00016` carries cooling conditions, and its air/closed-loop item is a *menu* option (8 of 19 required), so `air_or_closed_loop` is hardcoded `False`. Conservative and correct, but the path has never executed.
- **`benchmark_check()` takes `total_central_mgd` and never uses it.**
- **The operator cross-check fires constantly** — portfolio spans vs single-building loads agree only 31% of the time by construction. A flag that always fires carries no information.
- **`year_built` missing for 72%** → PUE falls back to `unknown`.
- **No basin water-stress weighting.** A consumptive gallon in the Occoquan during drought is not equivalent to one at a tidal estuary — and after §3.2, this now matters *more*, since Surry's zero-consumption profile is precisely a "large withdrawal, no depletion, saline source" case.
- **PUE is vintage-proxied, not operator-proxied.** The model narrows Scope 1 on operator identity but ignores operator identity for Scope 2.

---

## 7. What would actually narrow the range

### 7.1 Density — the last dominant term (64%)

Two moves, in order:

1. **Validate the bridge at campus scale.** interconnection.fyi publishes per-facility MW buckets for PWC sites. Aggregate this model's GFA-derived MW to campus level and test whether it reproduces them. This does not replace the constant — it measures how wrong it is, and would convert the ±25% engineering judgment into an evidenced dispersion.
2. **Pull VADEQ air permits for genuine per-facility generator capacity.** This is ICPRB's own input, per-facility, public, and runs Eq. 6-3 in the validated direction — retiring the bridge rather than re-tuning it. The JLARC/VADEQ database carries "facility names, operators, addresses, locality, total backup generator power capacity, building size, number of buildings, and land area."

Note the ±25% tolerance is already contradicted by ICPRB's own Fairfax figures (§1.3), which imply 12,722 sqft/MW.

### 7.2 Everything else

| Priority | Action | Why |
|---|---|---|
| 3 | **Replace the circular validation** (§6.1) with a bottom-up sum that never touches 309 — air-permit MW × cooling-type WUP on the physical 150/1,577 tiers, compared to PWC's 0.42 MGD | Nothing cancels, so it is a real test — and a falsifiable test of the cooling-type assignments |
| 4 | **Per-building metered water use** via PWC Water FOIA | Only route to genuine ground truth; would re-anchor the WUP scale |
| 5 | **Cooling type per facility** — SUP conditions, air-permit equipment lists, operator disclosures, aerial imagery | The dominant *physical* variable (§2.2); worth collecting once §7.1 stops drowning it out |
| 6 | **Market-based Scope 2** from operator PPA disclosures | GHG Protocol conformance |
| 7 | **Tie peak-day to the selected WUP tier** (§6.3) | Removes an incoherent number currently on screen |
| 8 | **Facility-specific PUE** | Now the #2 swing factor at 29% |
| 9 | **Per-building GFA** replacing the 89 proffer-splits | Retires the even-split assumption |
| 10 | **Basin water-stress weighting** | Makes consumptive gallons comparable rather than merely summable |
