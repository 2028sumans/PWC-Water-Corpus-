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

1. **Validate the bridge at campus scale. — DONE, see [`validate_density_bridge.py`](validate_density_bridge.py)**

   VADEQ permit site names enumerate the buildings each permit covers; interconnection.fyi carries a capacity bucket per facility and uses the *same legal-entity strings* as the DEQ site names. Joining them gives, per permit site, both a building set and a capacity bucket. Comparing this model's facility load (`effective_IT_MW × PUE`, since interconnection is sized for the whole facility) against the bucket is a genuine test — nothing in the chain was fitted to anything else in it.

   **12 sites matched; 10 with full building coverage.**

   | | result |
   |---|---|
   | Below the bucket floor | **8 of 10** |
   | Inside the bucket | 1 |
   | Over the ceiling | 1 (Digital Realty VA4: 36 MW vs a 10–25 MW bucket) |
   | Ratio to bucket floor | min 0.34, **median 0.82**, max 3.61 |

   **What this does and does not establish.** Interconnection capacity is an entitlement ceiling, generally sized for ultimate build-out, so a facility can be interconnected for 250 MW and draw 80. "Below floor" is therefore *expected* to some degree and is **not** proof the density constant is wrong. What the test genuinely bounds is the *direction and scale* of possible error: the model essentially never over-predicts (1 of 10, mildly), so it is more likely conservative than inflationary on water use. If true load sat at each bucket's midpoint, the model would be low by a median of **2.1×**.

   **Two findings that are solid regardless of the entitlement caveat:**

   - **The ±25% density tolerance is far too narrow.** Observed spread across sites is **10.6×** (0.34–3.61), against the model's stated 1.67×. Whatever the absolute calibration, facility-to-facility variation in the GFA→MW relationship is much larger than the model admits.
   - **The two external checks disagree on the direction of the error.** Matching the bucket floors implies a median **7,253 sqft/MW**; ICPRB's own Fairfax figures imply **12,722**. The shipped 8,818 sits between them. These are not reconcilable by tuning one number, which is itself evidence that a single fleet-average density cannot carry this much weight.

   Three join bugs were found and fixed while building this, all of which silently corrupted earlier runs: codenames are not unique across operators (`VA-10` is both NTT's and Iron Mountain's, which read a 561,000 sqft building as 4 MW); substring matching made `IAD-7` match IAD-74/73/77; and deduping on `gpin` collapsed four buildings into one, because GPIN is the *parcel* and IAD-100/101/102/103 all sit on `7695-62-8723`. The join now matches parsed codes for equality, requires the operator to agree, and dedupes on building `id`.
2. **Pull VADEQ air permits for genuine per-facility generator capacity.** This is ICPRB's own input, per-facility, public, and runs Eq. 6-3 in the validated direction — retiring the bridge rather than re-tuning it.

   **Status (attempted 2026-07-18):** The DEQ *Issued Air Permits for Data Centers* table was retrieved — 198 permits statewide, **32 in Prince William / Manassas**, saved to [`data/vadeq_air_permits_pwc.json`](data/vadeq_air_permits_pwc.json). The page blocks scripted clients (403 to both WebFetch and curl); a real browser session works.

   **The published table has no generator-capacity column.** Its fields are Air Site Name, Registration No, Issuance Date, Program Type, City/County, Regional Office. Capacity lives in the individual permit documents, which are not linked from that page. ICPRB's per-facility capacity came from a *JLARC consultant dataset* derived from those permits, not from this table.

   What the table does give — and this is genuinely new — is a **public regulatory join key at building granularity**. Site names frequently enumerate the buildings a permit covers: registration `74081-4` covers `IAD-73, IAD-74, IAD-602, IAD-193, IAD-194`. 54 distinct building codenames were parsed from the 32 permits, of which **26 join directly to building records** in this model (the misses are mostly 2025–26 permits for buildings not yet in the county's dataset).

   Two cautions for whoever picks this up. One permit typically covers **several** buildings, so any capacity read from a permit document is a *site* total that must be split across the listed buildings — the same aggregation trap that makes interconnection.fyi unusable per-building. And permitted generator capacity is an entitlement ceiling, so it is `inferable`, not `observable`.

   **Follow-up attempted 2026-07-18 — capacity is not publicly downloadable.** Every route was checked:

   | Route | Result |
   |---|---|
   | DEQ data-center permit table | No capacity column |
   | DEQ PEEP / Virginia Permit Transparency | Permit *processing metrics* only — no permit content |
   | DEQ "active air permit applications" document | 403 to scripted clients |
   | JLARC Report 598 full text | Prose only; no per-facility table |
   | JLARC study landing page | **Seven PDFs, zero data files** — no facility dataset published |

   ICPRB's per-facility capacity came from a **JLARC consultant dataset** compiled from VADEQ permits and never published. The two remaining routes are both requests, not downloads: a **FOIA to DEQ** (the data-center page explicitly invites one) or a direct request to **ICPRB or JLARC** for the compiled dataset. Statewide context for scale: roughly 9,000 permitted data-center generators at 2–4 MW each.

### 7.1a Permit capacity obtained — the constant's CENTRE is corroborated, its BAND is not

28 VADEQ permit documents were obtained and parsed ([`parse_air_permits.py`](parse_air_permits.py) → [`data/permit_capacity.json`](data/permit_capacity.json)). **9 parse cleanly; 21 are marked `needs_review` and excluded from every total.** Running the clean Prince William permits through ICPRB's Equation 6-3 and comparing to the GFA bridge ([`validate_density_vs_permits.py`](validate_density_vs_permits.py)):

| Reg | Operator | Coverage | Permit MW | GFA MW | Ratio |
|---|---|---|---|---|---|
| 74260 | NTT | 2/2 | 152.0 | 129.4 | 1.17 |
| 74081 | Amazon | 2/5 | 34.4 | 33.6 | **1.02** |
| 74224 | Stack | 1/1 | 76.5 | 31.9 | 2.40 |
| 74171 | Amazon | 2/4 | 32.7 | 46.4 | 0.70 |
| 73995 | Amazon | 3/5 | 28.9 | 41.6 | 0.70 |

**Median ratio 1.02 → implied density 8,613 sqft/MW against the shipped 8,818 — a 2.3% difference.**

This is not the result I expected, and it changes the diagnosis. The density constant has been treated throughout this document as the model's weakest link. Against the most direct evidence available — the same input ICPRB uses, run in the direction their equation validates — **its central value is very nearly right.** Permit 74081 is the cleanest case (our worked example, IAD-73/74) and lands at 1.02.

It also resolves the §7.1 contradiction. Interconnection floors implied 7,253 sqft/MW but compare against entitlement *ceilings*, biasing the ratio low; ICPRB's Fairfax figures implied 12,722 from a single locality's aggregate. Permits are per-site and definition-matched, and land at 8,613 — essentially on the shipped value.

**What remains wrong is the confidence band, not the centre.** Per-site ratios span 0.70–2.40 (3.4×) on n=5, against the model's stated ±25% (1.67×). The correct fix is therefore *not* a new central value — it is widening the density band and, where a clean permit exists, replacing the estimate with the permit-derived figure entirely.

Caveats that keep this provisional: n=5; three of five sites have partial building coverage, so the permit MW is scaled by the fraction of named buildings present; and permitted capacity is an entitlement, making it `inferable` rather than `observable`.

### 7.1c Matching permits to buildings — two tiers

**44 of 202 buildings now draw power from a permit** rather than the density bridge, and the density swing has fallen **64% → 55% → 46%**.

**Tier 1 — building codename (30 buildings).** Permit site names enumerate the buildings they cover (`IAD-73 IAD-74 IAD-602 ...`). Strict matching: operator must agree, codes are compared for equality, dedupe is on building id.

**Tier 2 — operator, for single-permit operators only (14 buildings).** Seven high-confidence permits name no buildings at all, stranding **902 MW**. Every one belongs to an operator holding exactly *one* Prince William permit, which makes operator a safe key for precisely those cases; Amazon (12 permits) and Microsoft (2) stay on codenames, where the key would be ambiguous.

Two guards make this safe, and both fired:

- **Coverage test.** One permit rarely covers an operator's whole portfolio. The permit's power must land within the range codename-matched permits actually showed against the GFA bridge (0.64–1.61, so 0.6–1.7 here). This tests *whether the permit covers this building set*, not the estimate's accuracy — a ratio far from 1 means the permit describes a different set of buildings. **CloudHQ was rejected at 0.13**: permit 74107 covers the MCC1/MCC6 halls at 61 MW while CloudHQ has 13 buildings totalling 475 MW, so applying it across all of them would have understated by ~8×.
- **No permit spent twice.** Iron Mountain's 74112 was already matched by codename to VA-1/2/3/6/7; the operator pass then applied the same 148 MW to five *further* Iron Mountain buildings. Permits consumed in Tier 1 are now excluded from Tier 2.

Accepted: QTS (0.94), Gainesville Crossing (1.13), Digital Realty (1.52). Rejected: CloudHQ (0.13), plus NTT / Iron Mountain / Stack as already-spent.

**What this does not reach.** 142 of the original 172 unbacked buildings carry no parseable codename (`QTS Manassas DC5`, `South Point Phase II Building A`), and operator matching only rescues those whose operator has a single permit and passes coverage. The remainder need either more permits (~29 buildings whose codenames appear on no permit we hold) or a facility-level name↔permit crosswalk that does not exist publicly. The permit header address does not supply it: it is the *applicant's mailing address*, which for QTS is the site but for CloudHQ is a corporate office and for Nova Mango a Delaware registered agent.

### 7.1b Why re-centring the density constant does not help

Three half-measures were quantified before concluding this. None works:

| Option | Effect |
|---|---|
| **A — widen the band** to the cross-source envelope (7,253–12,722) | Span goes 1.67× → 1.75×. The existing ±25% judgment already spans nearly the entire cross-source disagreement. **A 5% change — effectively a no-op.** |
| **B — recentre** on the geometric mean of the two checks (9,606) | Shifts every MW figure −8.2%; county total 33.17 → 30.45 MGD. But averaging two *contradictory* checks is not a principled estimate, it just splits a disagreement. |
| **C — clamp MW to the interconnection bucket** where one exists | Covers 26 of 202 buildings (13%), and 8 of 10 already sit *below* the bucket floor, so an upper clamp binds on almost nothing. |

The reason none works is structural: the disagreement is not noise around a true constant that better centring would find. Interconnection floors imply ~7,253 sqft/MW and ICPRB's own Fairfax figures imply 12,722 — a 1.75× spread between two independent sources, with the shipped 8,818 sitting between them. Meanwhile observed site-to-site spread is 10.6×. **A single fleet-average density is the wrong shape of object for this job**, and no choice of value fixes that. Only per-facility power does.

Note the ±25% tolerance is already contradicted by ICPRB's own Fairfax figures (§1.3), which imply 12,722 sqft/MW.

### 7.3 Cooling type — four routes tried, all closed

Cooling type is the third-largest swing factor (17%) and the only remaining one that is *physically real* rather than a modelling artifact. The 6.7× Prince William / Loudoun WUP spread is cooling type; it maps to roughly 11% vs 60–70% water-cooled share. Four routes were attempted.

**1. VADEQ air permits — one usable signal, and a trap.**

Twelve of thirty permits mention cooling-ish language. **In all thirty, every "closed loop" reference is closed-loop Selective Catalytic Reduction** — a NOx emissions control bolted to the diesel generators, not building cooling. Keying on that phrase would have misclassified at least four facilities (74262, 74171, 73180, 74260) as air-cooled on the strength of an exhaust treatment system, halving their Scope 1 in the wrong direction.

The only trustworthy positive signal is cooling equipment in a permit's own equipment list, since a cooling tower is a permitted emission unit in its own right. **Exactly one permit has it:** 74216 (Nova Mango Farms), 31 cooling towers at 6,000 gpm. That facility has no building in this dataset and no parcel in the county GIS, so it changes nothing today. Absence of cooling equipment is **not** evidence of air cooling — most data centre cooling needs no air permit and never appears.

**2. County staff reports — blocked.** 16 distinct `StaffReportLink` PDFs are referenced from the case records. All return **403 behind Cloudflare** to every available route: WebFetch, curl with browser user-agent and referer, and the in-app browser (which gets a download dialog rather than a render). These are downloadable by hand from a normal browser session.

**3. Mechanical permits — not attempted.** PWC Building Development issues them and they list HVAC equipment. 96 buildings carry a `PermitCase` (e.g. `BLD2017-00581`) that would key the request. This is a *county* records request, not a DEQ FOIA.

**4. Overhead imagery — feasible to fetch, not usable to classify.**

Esri World Imagery returns ~0.15 m/px over the county ([`fetch_facility_imagery.py`](fetch_facility_imagery.py)), and rooftop mechanical equipment is plainly visible: AWS IAD-74 shows long rows of small circular fan units plus a bank of larger housings along one edge.

**It still does not support classification.** An evaporative cooling tower and an air-cooled chiller both present from directly overhead as a rectangular housing with circular fan cowlings. The features that separate them — water basin, drift eliminators, sump piping, visible plume — are inside the housing or below this resolution. Worse, there is **no labelled Prince William facility to calibrate against**: the single permit documenting cooling towers maps to no parcel and no building, so a classifier could not be validated even in principle.

Imagery-derived cooling type would put a visual guess into a tool where every other input cites a document, with an unmeasured error rate. The fetch script is kept — imagery is useful for orientation, for confirming a building exists where its point geometry claims, and for change detection between vintages — but it is **not wired into the estimator**.

**Net effect on the model: none.** Cooling type remains at the technology envelope for 146 buildings and the operator-commitment narrowing for 56. What *did* change is §2.3's asymmetry (see below).

#### The asymmetry this exposed

The estimator could narrow a facility **down** toward the air-cooled floor on an operator commitment, but had no path for evidence pointing the other way — so every facility was implicitly presumed no-worse-than-average and evidence could only ever *lower* an estimate. A `disclosed_cooling_evaporative` basis now exists. For a 20 MW facility:

| Evidence | WUP low / central / high | Scope 1 |
|---|---|---|
| Operator closed-loop commitment | 150 / 150 / 309 | 0.0030 MGD |
| No evidence (technology envelope) | 150 / 309 / 1,577 | 0.0062 MGD |
| Permit lists cooling towers | 309 / 800 / 1,577 | 0.0160 MGD |

A 5.3× spread between the two evidence states — confirming cooling type as the dominant physical variable even though no tracked building currently sits in the third row.

Circulation rate (gpm) is recorded but deliberately **not** converted to a water figure: it is a design rating, and evaporative loss is a small, load- and weather-dependent fraction of it. Converting 31 × 6,000 gpm naively would yield a number larger than JLARC's measurement of the entire Virginia industry.

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
