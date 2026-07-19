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
OPERATOR_DISCLOSED_PUE = {"META": 1.08, "GOOGLE": 1.09, "AWS": 1.14, "MICROSOFT": 1.16}
DISCLOSED_PUE_TOLERANCE = 0.06          # site-vs-fleet spread

PUE_RANGE = {"new_build": (1.15, 1.35), # unbuilt: current design practice
             "modern":    (1.15, 1.40), # completed 2020+
             "standard":  (1.30, 1.55), # completed 2010-2019
             "legacy":    (1.45, 1.80), # completed pre-2010
             "unknown":   (1.15, 1.54)} # floor to the Uptime industry average
```

Anchored on the Uptime Institute 2025 survey (industry weighted average **1.54**, flat six years) and 2024–25 operator fleet disclosures. As shipped: **115 `new_build`, 61 `operator_disclosed`, 19 `modern`, 4 `standard`, 3 `legacy`, 0 `unknown`.**

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

### 7.2a The county's review process has no field for water quantity

Reading the staff reports in full — rather than grepping them — produced a finding the keyword scan had entirely missed, and it goes to the tool's central premise.

Every data centre staff report contains a **Potable Water Plan Analysis**: the section explicitly dedicated to water. Across all of them it evaluates exactly two things — *is public water available at the site*, and *will the applicant pay to connect*. Representative, from SUP2023-00006 (Gainesville East Data Center) and REZ2026-00022:

> *"The Prince William Water has a project permitted 12-inch water main located on the western portion of the site... the site shall be connected to public water, with the Applicant bearing all costs associated with providing onsite and offsite facilities to meet the demand generated by its uses."*

> *"Proposal's Weaknesses — None identified."*

**There is no water demand figure anywhere.** No gallons per day, no MGD, no consumption estimate, in any staff report reviewed. The phrase "the demand generated by its uses" is as close as the process comes, and it is never quantified.

The **Environment Plan Analysis** sections confirm the pattern from the other side. They cover brownfield remediation, perennial stream disturbance, Chesapeake Bay Resource Protection Areas, buffers and parking-lot landscaping. Water appears throughout — but only ever as a matter of **quality and habitat**, never of **quantity**.

This is a stronger statement of the disclosure gap than "no operator publishes a site PUE." It is not that facilities decline to report consumption; it is that **the county's land-use review framework has no place to record it**. A data centre can be approved, conditioned, and built without any public document ever stating how much water it will use. That is why this tool has to estimate at all, and it is the structural fact the estimate exists to make visible.

Two incidental facts worth carrying: the Gainesville East site is the **Atlantic Research Corporation brownfield**, where clearing has already disturbed two perennial streams as part of remediation and staff record the cleanup status as *"unclear to staff"*. And Planning Commission packets interleave unrelated cases, so a section must be attributed to its own case — a "private well" provision and playground equipment in the same PDF as a data centre item belong to a residential application, not to the data centre.

### 7.1e A permit states floor area AND load for the same building

Reading every permit description in full — not keyword-matching them — turned up the thing this project has looked for all along: **an applicant stating a data centre's floor area and its electrical load in the same sentence.**

`MEC2025-01801`, parcel 7596-55-9338, Issued:

> *"THE PROJECT IS A TWO-STORY DATA CENTER AND OFFICE BUILDING AT AN APPROXIMATE **339,744 SF GROSS** AREA... AND ROOF EQUIPMENT PLATFORM TO SUPPORT THE **60 MW CRITICAL LOAD** PLANNED"*

**339,744 ÷ 60 = 5,662 sqft per MW**, against the **8,818** this model uses.

"Critical load" is IT load — the same quantity ICPRB's *Effective (IT) Power Demand* denotes — so these are directly comparable. Taken at face value, the constant **understates this building's power by 1.56×**.

A second statement, `MEC2025-01881` on the NTT parcel: *"A NEW TWO-STORY **96 MW** DATA CENTER BUILDING THAT CONSISTS OF 12 DATA SERVER VAULTS"*. Which of the four NTT buildings there it refers to is not stated, so it cannot be assigned — but for scale, the model's permit-derived figures are 74.7 MW (VA10) and 77.3 MW (VA11), while a GFA-derived VA10 would be 63.6 MW. **The permit-derived path is the closer of the two to a stated 96 MW**, which is a further point for §7.1a.

Also captured: a 270,000 SF data centre building (`MEC2023-01041`), and — usefully — the white-space ratio stated outright in `MEC2025-00037`: *"Approx. 26,000 SF Data Hall with associated Mechanical and Electrical Gallery spaces (additional 12,000 SF)"*, i.e. roughly 68% of fitted-out area is hall.

All four are recorded in [`data/eportal_density_statements.json`](data/eportal_density_statements.json).

**Nothing is recalibrated on this.** One building is not a fleet, the 5,662 figure is a *planned* load on a *gross* area including office, and ICPRB's 8,818 is a fleet average across a Virginia estate that includes far older and less dense buildings — so a 2025 new build coming in denser is expected rather than contradictory. What it does establish is that the direction of §7.2b's substation flag and the direction of this figure **disagree**: the substation suggested campus power might be overstated, this suggests per-building power is understated. Both are single observations. The honest reading is that the density constant remains the largest unresolved term, and now has credible evidence pulling in both directions.

### 7.3c Harvested: data centres permit chillers, not cooling towers

The ePortal harvest is done. **185 records** captured across the keyword set (`chiller`, `igloo`, `cooling tower`, `dry cooler`, `evaporative`, `condenser water`), joined on `MainParcel` and saved to [`data/eportal_cooling_permits.json`](data/eportal_cooling_permits.json). **76 land on data centre parcels**, covering 75 parcels overall, and are attached per building as `eportal_cooling_permits`.

The distribution is the finding:

| Equipment | On data-centre parcels | On other parcels |
|---|---|---|
| **Cooling towers** | **1** | **38** |
| **Chillers / "igloo" containers** | **33** | 22 |

Cooling towers in Prince William are permitted at **hospitals** (2300 Opitz Blvd), **schools** (Panther Pride Dr), **county buildings** (1 County Complex Ct) and **Dominion's Possum Point** power station. They are almost entirely absent from data centre parcels, which instead permit chillers and containerised cooling units:

> `PLB2020-00815` — *"IGLOO/CHILLER ADDITIONS - IAD 52"*
> `MEC2025-00404` — *"IMDC VA1 CHILLER ADDITON"* (Iron Mountain VA-1)
> `PLB2019-00827` — *"BACKFLOW PREVENTER IN THE CHILLER PLANT SPRINKLER ROOM"* (Innovation/Power Loft)

Ten data centre buildings now carry a chiller or igloo record: AWS IAD-52, IAD-55, IAD-73, IAD-74, IAD-77, Bethlehem DC18/19/20/23, and Iron Mountain VA-1.

**The single exception is worth naming.** `LND2023-00088` — *"SITE DEVELOPMENT PERMIT FOR INNOVATION - POWER LOFT - MINOR SITE PLAN FOR COOLING TOWER ADDITION"*, 9651 Hornbaker Rd. One cooling-tower addition across the entire data centre estate.

**Why this matters.** It is the first independent corroboration of ICPRB's Prince William WUP. Inverting 309 gal/MW/day on the physical tiers implies roughly **11% water-cooled share** in this county, against Loudoun's ~60–70% at 1,006 gal/MW/day (§2.2). That was a number this model consumed on trust. The county's own trade-permit record, assembled from a completely different regulatory system, points the same way: Prince William data centres are overwhelmingly not evaporatively cooled.

**What it is not.** This is attached as **evidence only and does not narrow any estimate.** A chiller is the cold-side machine; what determines water use is how heat is finally rejected, and a chiller permit does not say whether that is a cooling tower or a dry cooler. Absence of a cooling-tower permit is also not proof of absence — rooftop equipment replaced in kind may not generate a separately searchable record. The signal is strong because the county clearly *does* permit cooling towers when they exist, 38 times, just not at these facilities.

### 7.3b County trade permits DO carry cooling equipment — route reopened

The cooling-type search was closed in §7.3 on the basis that air permits name equipment only once and imagery cannot be validated. That conclusion was **too early**: it never tested the county's trade-permit system.

Prince William's ePortal (`egcss.pwcgov.org`, Tyler EnerGov) exposes a public search over Permit, Plan, Inspection, Code Case, Request and Project records. Every record carries `MainParcel`, which joins directly to the parcels already in this dataset. Mechanical (`MEC`), plumbing (`PLB`), electrical (`ELE`) and fire-protection (`FPP`/`FPR`) permits are all public.

**Permit descriptions contain equipment-level detail**, which the air permits' project-level descriptions do not:

> `MEC2026-01982` — *"THERE WILL BE TWO NEW CHILLERS WITH ASSOCIATED PUMPS AND A MATCHING COOLING TOWER"*
> `MEC2023-02299` — *"JC-1 Cooling tower, pump and piping"*
> `MEC2026-00947` — *"(1) DOAS1 - Dedicated Outdoor Air Unit (1) CT1..."*

**And data centre cooling equipment is in there, named by building code:**

| Permit | Parcel | Description |
|---|---|---|
| `PLB2020-00815`, `PLB2020-00742` | 7597-42-1456 | *"IGLOO/CHILLER ADDITIONS - IAD 52"* |
| `PLB2020-00775` | 7298-51-5907 | *"IGLOO/CHILLER ADDITIONS - IAD 55"* |
| `PLB2020-00480` | **7596-17-3979** | *"THREE NEW IGLOO CONTAINERS"* |
| `PLB2020-00478` | **7596-17-3979** | *"TWO NEW IGLOO CONTAINERS"* |

7596-17-3979 is **AWS IAD-74**, this document's worked example. Note these are **plumbing** permits, not mechanical — chillers with water connections are permitted through PLB, so a mechanical-only search would have missed them.

Corpus size: **345 records matching "chiller", 51 matching "cooling tower"** across all permit types.

**Access notes for whoever harvests this.** The API (`POST /SelfService/api/energov/search/search`) rejects reconstructed payloads with HTTP 500 even on verbatim replay, so it requires headers the Angular client adds; results are instead readable from the rendered DOM, which parses cleanly into permit number, type, status, parcel, address and description. The UI pages 10 at a time and programmatic `.click()` does not advance it — real clicks do. Sorting descending by permit number surfaces recent records first, which is where data centre activity is.

**What this does not yet establish.** Whether "IGLOO/CHILLER" units are air-cooled or evaporative is not stated, and a chiller alone does not settle cooling type — the question is whether heat is finally rejected through a cooling tower or dry cooler. But this is the first source that names cooling equipment per data-centre building, and it is public, joinable and unharvested.

### 7.3a The only enforceable water condition in the entire corpus is a TDS limit

Reading every permit condition — 109 distinct types across 30 permits, not just the equipment tables — produced one genuinely water-relevant regulatory provision, and its character is the finding.

Permit **74216**, Conditions 14 and 22:

> *"The Total Dissolved Solid (TDS) concentration in the process water in each cooling tower (Ref. Nos. CT1 through CT31) shall not exceed 2,500 ppm TDS."*
>
> *"Once per calendar year, the permittee shall sample and analyze the process water from one cooling tower..."*

This is the **only enforceable condition touching data centre water anywhere in the corpus** — county proffers, staff reports and state air permits combined. Three things about it matter:

1. **It regulates chemistry, not volume.** No permit or proffer anywhere caps how much water a facility may use.
2. **It nonetheless bounds consumption indirectly.** A TDS ceiling limits cycles of concentration, which sets the blowdown rate — a real component of cooling-tower water loss. So the one binding water condition constrains consumption only as a side effect of an air-quality concern.
3. **It exists in an *air* permit.** The regulatory instrument that comes closest to governing data centre water in Prince William is administered by DEQ's air programme, for drift and emissions purposes, and appears at exactly one site.

It also confirms the cooling-type search is exhausted: the cooling-tower *conditions* appear only in 74216, the same permit whose equipment list names them. No additional evaporatively-cooled facility is identifiable from the permit corpus.

### 7.1d Non-emergency generators break ICPRB's redundancy rationale

Reading the permits **in full**, rather than parsing only their equipment tables, surfaced a problem with the permit-derived power path itself.

ICPRB's Equation 6-3 applies a 0.5 redundancy factor, and states exactly why:

> *"A redundancy factor of 0.5 is assumed to reflect that permitted generator capacity typically represents twice the actual IT power load (i.e. 2N backup systems)"*

That rationale is specific to **emergency backup**. Several permits here list large **non-emergency** fleets, and the permits themselves treat the two classes differently — hour limits apply only to the emergency units:

> 74342: *"Each emergency diesel engine gen-set (Ref. Nos. 53, 54, 99 through 101, T1 and T2) shall not operate more than 500 hours per year"* — while Ref. Nos. 1–52 and 55–98, the non-emergency units, carry no equivalent cap.

Non-emergency capacity by permit:

| Reg | Non-emergency share | Affects |
|---|---|---|
| 74262 | **100%** | DLR IAD-50, IAD-51, Digital Realty VA4 |
| 74333 | 93% | IAD-45 |
| 74342 | 52% | IAD-110/111/112/113 |

A fleet that is 100% non-emergency is not 2N redundancy — it is generation, permitted to run. **Halving its capacity is not supported by the reason the halving exists.**

The factor is **not changed**. What those units actually serve — peak shaving, grid services, primary supply — is not something these documents establish, and guessing would replace a stated assumption with an unstated one. The exposure is recorded per building as `non_emergency_share` and `redundancy_assumption_note` so it is visible wherever the figure is used. Three buildings currently carry a 100% flag.

### 7.2c Floor Area Ratio — a physical check on campus entitlements

Reading the staff reports in full supplied something no dataset had: a **physical constraint on floor area**. Prince William's transects cap FAR, and approved data centres cluster tightly just below the cap.

| Source | FAR |
|---|---|
| REZ2026-00022 | **0.50** — proffered as a binding maximum |
| REZ2022-00031 | 0.52 proposed |
| SUP2023-00006 | 0.55 |
| I-3, transect 3 | **0.57 maximum** |
| T-4 (highest in county) | **1.38 maximum** |

Dividing each campus's entitlement GFA by its acreage gives an implied FAR, now emitted as `implied_far` with a `far_flag`:

| | Campuses |
|---|---|
| Plausible (≤0.57) | **41 of 51** |
| Above the I-3 transect | 8 |
| **Above every transect in the county** | **2** |

**Median implied FAR is 0.35** — *below* the observed approved range. This is an important correction to §7.2b: campus entitlements are **not** systematically inflated. Most are conservative. The substation discrepancy is specific, not structural, and is at least as likely to reflect a substation built for one phase as an error in the model.

The two impossible cases share a root cause:

| Campus | Acres | Implied FAR | Shares its GFA with |
|---|---|---|---|
| Manassas Point PRA | 39.9 | **3.34** | BOCS (234.4 ac, FAR 0.57) |
| Battlefield Business Park | 7.3 | **2.68** | Manassas Corporate Center 8 (23.0 ac, FAR 0.86) |

In each pair a site-wide entitlement figure has been repeated onto a **smaller** campus it does not describe — the campus-level form of the proffer duplication that `resolve_gfa()` already fixes for buildings, and which campus records never went through because they use `coalesce_gfa()`.

The figures are **flagged, not silently corrected**. A wrong number that announces itself is more useful than a quietly adjusted one, and capping them would change the headline campus ordering on the strength of an inference rather than a source. Manassas Point PRA currently carries 5.8M sqft of entitlement it cannot physically hold; anyone quoting that row should see the flag first.

### 7.2b A substation figure that questions the CAMPUS estimates

A Public Facility Review staff report (SUP2026-00011, NOVEC) states twice:

> *"a 300-MW electric utility substation with a collocated Dominion Energy switching station... intended to provide reliable electric service to data center development on the subject parcel and adjacent parcel to the west"* — 13301 Casey Lane, **GPIN 7496-43-8199**

This model's campus entitlement estimates on that same GPIN:

| Campus | Effective IT MW |
|---|---|
| Hunter Property Rezoning (REZ2020-00022) | **454.8** |
| Devlin Technology Park (REZ2022-00022) | **400.3** |

Either campus alone exceeds the substation built to serve the parcel — and effective *IT* load still has to be multiplied by PUE to reach facility load, so 454.8 MW IT implies roughly 570 MW at the meter against a 300 MW substation. That is about 1.9× over.

**Why this does not contradict §7.1a.** The permit comparison that corroborated the density constant at a median ratio of 1.02 was run on **buildings**, whose floor area is assessed or permit-derived. Campus figures use **entitlement** GFA — the full proffered build-out, the weakest GFA tier in the model — and this is the first external check ever run against them. The two results are consistent: the constant looks sound where floor area is measured, and the *campus inputs* look inflated where it is an entitlement ceiling.

**Caveats that keep this a flag rather than a correction.** The report does not say which campus the substation serves, and both share the GPIN; a site may draw from more than one substation; and a substation is often built for a phase rather than for full entitlement, which would explain much of the gap without any error in the model.

No value is changed on the strength of one data point of uncertain scope. It is recorded because it is the only independent check on campus entitlement figures that exists, and because it points the same direction as ICPRB's Fairfax density (§1.3): campus-level power may be overstated.

### 7.3 Cooling type — four routes tried, all closed

Cooling type is the third-largest swing factor (17%) and the only remaining one that is *physically real* rather than a modelling artifact. The 6.7× Prince William / Loudoun WUP spread is cooling type; it maps to roughly 11% vs 60–70% water-cooled share. Four routes were attempted.

**1. VADEQ air permits — one usable signal, and a trap.**

Twelve of thirty permits mention cooling-ish language. **In all thirty, every "closed loop" reference is closed-loop Selective Catalytic Reduction** — a NOx emissions control bolted to the diesel generators, not building cooling. Keying on that phrase would have misclassified at least four facilities (74262, 74171, 73180, 74260) as air-cooled on the strength of an exhaust treatment system, halving their Scope 1 in the wrong direction.

The only trustworthy positive signal is cooling equipment in a permit's own equipment list, since a cooling tower is a permitted emission unit in its own right. **Exactly one permit has it:** 74216 (Nova Mango Farms), 31 cooling towers at 6,000 gpm. That facility has no building in this dataset and no parcel in the county GIS, so it changes nothing today. Absence of cooling equipment is **not** evidence of air cooling — most data centre cooling needs no air permit and never appears.

**2. County staff reports — retrieved, and mostly empty.**

All 16 `StaffReportLink` PDFs were obtained by hand (they return 403 behind Cloudflare to every scripted route). Two findings:

**Ten of the sixteen are placeholder pages.** They are 1-page PDFs reading *"The staff report for this case is currently unavailable."* The county's own case records link to reports that were never posted or have since been withdrawn — so the `StaffReportLink` field is not a reliable indicator that a report exists. Only five distinct reports carry real content.

**One of the five mentions cooling: REZ2025-00003** ("Project Industry" / Aura Development), and it repeats the pattern already seen in SUP2025-00016 rather than breaking it:

> *"15. Use of air or closed loop cooling rather than water-cooled alternatives; or"*

That is item **15 of 16** in a sustainability menu from which the applicant must implement **at least 8**. Item 14 is the 1.5 annualized PUE. Neither is guaranteed, so neither narrows the estimate.

A separate **mandatory** proffer is more interesting but still does not bind cooling type:

> *"D. Noise Mitigation: All air-cooled chiller equipment installed on the Property, whether ground-mounted or roof-mounted, shall include ... low noise emission fans ... magnetic bearing compressors"*

This governs air-cooled chillers **if installed**; it does not require that cooling be air-cooled. An applicant does not usually write a noise proffer for equipment it has no plan to install, so it is real evidence of intent — recorded as `anticipates_air_cooled_chillers`, treated as inferable, and not used to narrow.

**A bug this surfaced.** Campus profiles never ran `permit_conditions_for()`, so a cooling condition attached to a **rezoning case** was silently dropped for all 51 campuses. REZ2025-00003 sits on the Aura Development *campus* record, not on any building, and so would never have surfaced no matter what the report said. Campuses now run the same condition matching as buildings; two campuses (Aura Development, Hornbaker Road) carry conditions as a result.

The two remaining routes for the ten missing reports: the county ePortal case pages, or the Planning Office directly (703-792-7615 / planning@pwcgov.org), which the placeholder page itself suggests.

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

---

## 8. Findings ledger

Every substantive finding, in one place. Sections 6–7 grew chronologically and their numbering is out of order; this is the index.

### 8.1 Errors found in this model (all fixed or flagged)

| # | Finding | Status |
|---|---|---|
| 1 | **The validation was circular.** ICPRB derived 309 gal/MW/day *by dividing* PWC's 0.42 MGD by its own power estimate, so comparing back to 0.42 cancels the water figure and returns −7.4% either way. It tested the power spine, not water use. | Withdrawn from the module docstring, the UI headline, the U1 audit item and the `/api/memo` prompt |
| 2 | **8,818 sqft/MW is run backwards.** ICPRB uses it once, to convert Loudoun's 0.017 gal/day/sqft into the 150 gal/MW/day tier. Power in their Eq. 6-3 comes from air-permit generator capacity, never floor area. | Documented; largest remaining swing |
| 3 | **Scope 2 used national medians.** Nuclear at 700 gal/MWh blended Surry (once-through saline, 0 consumption) with North Anna (Lake Anna, 417). | Fixed — VA-specific USGS values; swing 54% → 12% |
| 4 | **Campus profiles never ran `permit_conditions_for()`**, silently dropping proffer cooling conditions for all 51. | Fixed |
| 5 | **Campus entitlement GFA duplicated onto smaller campuses.** Manassas Point PRA implied FAR 3.34, Battlefield Business Park 2.68 — both share a GFA with a larger campus. | Flagged via `implied_far` / `far_flag`, not silently corrected |
| 6 | **Suspected PUE double-count.** | **Retracted** — Eq. 6-3 says "Effective **(IT)** Power Demand", so multiplying by PUE is right |
| 7 | **`unknown` PUE applied to 147 unbuilt buildings.** Their vintage is not unknown; they are being built now. | Fixed — `new_build` class; `unknown` now empty |
| 8 | **Withdrawal and consumption are summed.** Scope 1 is delivered water, Scope 2 is consumed water. The 0.75 factor exists to reconcile them and is computed but unused. | Open |
| 9 | **Peak-day ignores narrowing** — always uses 3,060 gal/MW/day, giving a 20× peak:average ratio on narrowed facilities. | Open |
| 10 | **The estimator could only narrow one way.** Evidence could lower Scope 1 but never raise it. | Fixed — `disclosed_cooling_evaporative` basis added |
| 11 | Three join bugs: codenames not unique across operators (`VA-10`), substring matching (`IAD-7` → `IAD-74`), dedupe on `gpin` when GPIN is the **parcel**. | All fixed |
| 12 | **Non-emergency generator fleets break ICPRB's 0.5 redundancy rationale**, which assumes 2N emergency backup. 74262 is 100% non-emergency. | Flagged per building, factor unchanged |

### 8.2 Findings about the world (the paper's material)

| Finding | Evidence |
|---|---|
| **The county's land-use review has no field for water quantity.** Every data centre staff report contains a *Potable Water Plan Analysis*; across all of them it asks only whether public water is available and who pays to connect. No gallons anywhere. | §7.2a |
| **Cooling type is never made enforceable.** It appears only as a menu item — 15 of 16 with 8 required (REZ2025-00003), 17 of 19 with 8 required (SUP2025-00016). The 1.5 PUE cap is the same. | §7.3, §7.2a |
| **The only enforceable water condition in the entire corpus is a TDS limit** in an *air* permit (74216, 2,500 ppm), regulating chemistry for drift purposes and bounding consumption only as a side effect. | §7.3a |
| **Prince William data centres permit chillers, not cooling towers** — 1 vs 38 on other parcels, against 33 chiller/igloo records. Independently corroborates ICPRB's ~11% water-cooled share for this county. | §7.3c |
| **10 of 16 published staff-report links are placeholders** reading "currently unavailable". | §7.2a |
| **Applicants do state load and floor area** — just in trade permits, not in land-use review. | §7.1e |

### 8.3 What the model still cannot see

| | Count |
|---|---|
| Buildings with power from a document | 44 / 202 |
| Buildings with PUE from an operator report | 61 / 202 |
| Buildings with cooling type from evidence | **0 / 202** |
| Buildings with metered water | **0 / 202** |

---

## 9. Resolving density — a concrete route

Density is 46% of the swing and now has evidence pointing **both ways** (§7.1e vs §7.2b). It is the one term whose resolution would materially change the tool. The route below is demonstrated, not speculative — every step has been executed at least once.

### 9.1 The insight

ICPRB's 8,818 sqft/MW is a **fleet average** across the whole Virginia estate, including older, lower-density buildings. Modern new builds are far denser. Three independent readings now cluster together:

| Source | sqft/MW |
|---|---|
| `MEC2025-01801` — both figures stated, one building | **5,662** |
| 96 MW attributed to NTT VA10 (560,942 sqft) | 5,843 |
| 96 MW attributed to NTT VA11 (580,498 sqft) | 6,047 |
| *ICPRB fleet average* | *8,818* |
| *ICPRB Fairfax-implied* | *12,722* |

That spread is not noise — it is **vintage**. The constant should not be single-valued.

### 9.2 The harvest

Applicants state building load in county trade permits. The searches that surface them, all confirmed working on `egcss.pwcgov.org`:

- `"critical load"` → 4 records, one building
- `"data hall"` → 5 records, two buildings at 84 MW and 96 MW
- `"data server vaults"` → the same building family
- `"MW data center"` → 4 records

Each hit gives a stated MW. Pairing it with the assessed GFA already in this model yields one density point. **A dozen such pairs would replace the single fleet constant with a vintage-banded distribution** — and unlike every other route tried, this data is public, free, and already reachable.

Two further handles found in the same corpus: **"data server vault"** appears to be a roughly consistent unit (6.0 and 8.0 MW per vault across two buildings), and `MEC2025-00037` states the white-space ratio outright — 26,000 SF hall to 12,000 SF mechanical/electrical gallery, so ~68% of fitted-out area is hall.

### 9.3 What to change once the pairs exist

1. **Band the constant by vintage** rather than using one value: a modern-build density near 5,700–6,000 and a legacy density above 8,818, selected on `year_built` / build status exactly as PUE now is.
2. **Keep permit-derived power first.** It already beats the bridge — against a stated 96 MW, the permit path gives 74.7 MW where the bridge gives 63.6.
3. **Widen the band honestly.** The current ±25% is contradicted from both directions and understates real uncertainty.

### 9.4 Method note

None of §9.1's figures are reachable by keyword search over the fields a normal query returns. They sit mid-paragraph inside permits whose stated subject is HVAC or electrical scope. They surfaced only from reading every record.

---

## 10. Density banding — implemented

§9 proposed banding the density constant by build era. That is now shipped.

### 10.1 What changed

`SQFT_PER_EFFECTIVE_MW = 8818` is no longer applied to every building. Density is selected from a band keyed on the same era judgement that already drives PUE:

| Class | Central | Range | Source |
|---|---|---|---|
| `new_build` (unbuilt) | **7,070** | 5,200–8,818 | PWC trade permits for 2025–26 builds state 5,662–6,047 |
| `modern` (2020+) | **7,070** | 5,200–8,818 | same |
| `standard` (2010–19) | 8,818 | 6,500–11,000 | ICPRB fleet average |
| `legacy` (pre-2010) | 11,000 | 8,818–12,722 | ICPRB's Fairfax-implied figure (§1.3) |
| `unknown` | 8,818 | 5,662–12,722 | spans the full evidenced range |

Buildings whose power comes from a VADEQ permit **bypass density entirely** and are unaffected.

### 10.2 Why 7,070 and not 5,662

The permit measurement is 5,662 sqft/MW. Adopting it outright moves the county total ~30%, on a **single building's planned load stated over gross area including office space**. That is too much weight for n=1.

7,070 is the geometric mean of that measurement and ICPRB's fleet average — it keeps the direction the evidence indicates without pretending the magnitude is settled. The range spans both endpoints so the uncertainty stays visible rather than being hidden in a point estimate.

**This is a hedge, and it is labelled as one in the code.** Once §9.2's harvest yields a dozen pairs, the central should come from the distribution instead.

### 10.3 Literature cross-check

Published density figures are quoted over **white space**, not gross area — the same distinction that broke this module's first version. White space is 40–50% of gross internal area. At 45%:

| | sqft/MW gross | W/sqft gross | W/sqft white space |
|---|---|---|---|
| PWC permit, 2025 build | 5,662 | 177 | **392** |
| ICPRB fleet average | 8,818 | 113 | **252** |
| *Published range, modern data centres* | | | *200–400* |

Both land inside the published range — the new build at the top, the fleet average mid. **The permit evidence and the literature agree once the gross/white-space distinction is respected**, which is the strongest support the modern band has beyond the single measurement itself.

### 10.4 Effect

County-wide central total: **32.51 → 37.84 MGD (+16%)**. Density remains the top swing factor at 48%, essentially unchanged — banding relocated the central estimate but did not narrow the uncertainty, because the band still spans the full evidenced range.

Distribution: 132 `new_build`, 18 `modern`, 6 `standard`, 2 `legacy`, 44 permit-backed (no density).

### 10.5 Honest status

This is **not** density resolved. It is density *correctly framed*: the constant is no longer a single fleet average applied to buildings it does not describe, and each building now reports which band it used and why. The evidence base for the modern band is one solid measurement plus two ambiguous attributions plus a literature consistency check.

The headline moved 16% on that. Anyone quoting the total should know the number is now era-adjusted and that the adjustment rests on thin evidence pending §9.2.

---

## 11. The building dataset was stale — refreshed 19 July 2026

Chasing more density pairs led somewhere more consequential than density. Querying the county's **live** Data Center Buildings layer to find floor area for a permit-stated building revealed that the snapshot this model had been running on was materially out of date.

### 11.1 What was wrong

| | Snapshot | Live layer |
|---|---|---|
| Buildings | 203 | **243** |
| Name-matched with >5% GFA difference | — | **40 of 148** |
| Total GFA (matched names) | 36.4M sqft | 38.5M sqft (+5.7%) |

Individual divergences were far larger than the aggregate:

| Building | Snapshot | Live | |
|---|---|---|---|
| Microsoft Azure MNZ04 / MNZ05 | 82,618 | 310,856 | **3.76×** |
| NTT Grove at Gainesville VA12 | 184,855 | 580,498 | **3.14×** |
| NTT Grove at Gainesville VA13 | 184,855 | 557,012 | 3.01× |
| Microsoft Azure 1–6 | 425,459 | 633,333 | 1.49× |
| Amazon AWS IAD A / B | 634,891 | ~246,000 | **0.39×** |
| Aligned Data Centers IAD05 | 1,275,141 | 432,742 | 0.34× |

**59 buildings existed in the live layer and not in the snapshot at all** — entire campuses including Devlin Technology Park (A–H) and Project Well.

Every figure this model produced before 19 July 2026 was computed on that snapshot.

### 11.2 A bug the refresh introduced

The live layer encodes "not built" as **`YearBuilt = 0`**, where the old snapshot used null. Taken literally, `0 < 2010`, so **17 Planned buildings were classed `legacy`** — handed the least dense density band (11,000 sqft/MW) and the worst PUE band (1.45–1.80) when they are the newest structures in the dataset.

`_vintage_class` now treats zero and negatives as missing. Fixed before any figure was published.

### 11.3 Effect

| | MGD |
|---|---|
| Stale data, single 8,818 density | 32.51 |
| Stale data, banded density | 37.84 |
| **Refreshed data, banded density** | **51.42** |

Roughly **+36% from the data refresh alone**, on top of +16% from banding. The refresh matters more than any modelling change made this session.

Completed-building Scope 1 is now **0.3518 MGD** across 54 completed buildings, against Prince William Water's reported 0.42 MGD service-area total — closer than the 0.298 the stale data gave, though that comparison remains **not independent** (§6.1).

Density is now **52%** of the swing, up from 48%, because the refresh added 40 buildings that mostly lack permit-derived power and therefore lean on the constant.

### 11.4 The standing lesson

The county updates this layer continuously — GFA is revised as buildings move from planned to permitted to assessed. A snapshot is a point-in-time read of a moving dataset, and nothing in the pipeline was checking its age. **`build_facility_profiles.py` should re-pull from the live endpoint rather than a vendored file**, or at minimum record and surface the snapshot date.

Live endpoint: `https://gisweb.pwcva.gov/arcgis/rest/services/Planning/Build_Out_Analysis/MapServer/9/query`

---

## 12. The peak-day figure ignored every narrowing — fixed 19 July 2026

Found while computing §13, because peak day is the number the basin analysis turns on.

`WUP_PEAK_GAL_PER_MW_DAY["pwc_observed"] = 3,060` gal/MW/day is Prince William Water's **observed system peak day (2023)**, a fleet-wide figure. The estimator applied it flat to every building — including the buildings the Scope 1 logic had just narrowed to the 150 gal/MW/day air-cooled tier on the strength of an operator closed-loop commitment.

Two things were wrong with that:

1. It implied a **20× peak-to-average ratio** for those buildings, where the observed county ratio is 3,060 / 309 = **9.9×**.
2. It put their peak day at roughly **7× their own Scope 1 upper bound**. A closed-loop site has no evaporative peak to have; the whole point of the narrowing is that its consumption is nearly weather-independent.

The peak is now derived as a **ratio applied to whatever central WUP the building actually earned**:

```python
peak_ratio = (WUP_PEAK_GAL_PER_MW_DAY["pwc_observed"]
              / WUP_GAL_PER_MW_DAY["pwc_observed"])      # 3060 / 309 = 9.9
peak = mgd(eff_mw, wup_central * peak_ratio)
```

A building narrowed to 150 now peaks at 1,485 gal/MW/day, not 3,060. The county-wide summer peak drops from **23.36 MGD (11.3× annual)** to **20.50 MGD (9.9× annual)**, which is now the observed ratio by construction rather than an artefact of mixing a fleet peak with a per-building average.

This is the same class of error as §6.5 and the nuclear factor: a fleet-level constant applied where a building-level one was already available. Worth a standing check — **any constant sourced from a system-wide observation must be asked whether it survives being pushed down to a single building.**

---

## 13. Where the water actually comes from — basin displacement

This is the analysis with the clearest hydrological claim in the project, and the one that most justifies treating the work as water science rather than infrastructure accounting.

`basin_analysis.py` asks a question the per-facility totals cannot: **which basin gives up the water?** Scope 1 is withdrawn locally, from the Occoquan and Potomac headwater streams the buildings sit on. Scope 2 is consumed hundreds of kilometres away, at the generating plants — which sit in the James, York, Roanoke and Rappahannock basins. Since Scope 2 is ~87% of the total, almost the entire footprint is displaced out of the county's own watersheds.

### 13.1 Method

Scope 1 is assigned to receiving watershed by the building's own `water_context.watershed_name` (county watershed layer). Scope 2 is split by fuel using the same blended-intensity arithmetic as §3, then each fuel's share is distributed across Virginia's actual plants of that type **in proportion to their reported consumption**, and each plant is assigned a basin from the USGS dataset's own `NAME_OF_WATER_SOURCE` field. Attribution therefore uses one source end to end — no external basin lookup, no plant-siting assumption of mine.

Two source strings resolve to no basin and are recorded as such rather than guessed: `Municipality` (the plant buys treated water; the dataset does not name the supplier) and `Wells`. Together they carry 19.3% of Scope 2, which is a real limit on the precision of the claim and is stated as one.

### 13.2 Scope 1 — the local draw, all within the Potomac basin

| Receiving watershed | Buildings | IT MW | Annual avg (MGD) | Summer peak (MGD) | Watershed acres | Peak gal/acre/day |
|---|---|---|---|---|---|---|
| Broad Run | 166 | 6,117 | 1.651 | 16.35 | 2,476 | **6,604** |
| Bull Run | 61 | 1,160 | 0.344 | 3.40 | 1,716 | 1,983 |
| Powells Creek | 14 | 328 | 0.066 | 0.66 | 1,781 | 371 |
| Quantico Creek | 2 | 29 | 0.009 | 0.09 | 1,316 | 67 |

The concentration is the finding. **Broad Run carries 80% of the county's local data-centre draw** — 166 of 243 buildings — and on a summer peak day that is 6,604 gallons per watershed acre per day, 3.3× Bull Run and 18× Powells Creek. Whatever the county-wide number is, the stress is not county-wide.

### 13.3 Scope 2 — consumed in basins the county has no standing in

| Basin | MGD | % of Scope 2 |
|---|---|---|
| James | 19.35 | 43.3% |
| **York (Lake Anna / North Anna)** | **13.68** | **30.6%** |
| *unresolved — purchased municipal water* | 8.60 | 19.2% |
| Roanoke | 2.49 | 5.6% |
| Rappahannock | 0.27 | 0.6% |
| Tennessee/Clinch | 0.23 | 0.5% |
| *unresolved — groundwater* | 0.04 | 0.1% |
| New/Kanawha | 0.02 | 0.0% |

The James total is gas combined cycle — chiefly Tenaska (11.89 MGD) and Bear Garden (7.44 MGD). The York total is essentially **North Anna alone**: Virginia's other nuclear station, Surry, reports zero consumption because it is once-through cooled on the tidal James, so the entire nuclear share of Prince William's electricity lands on Lake Anna.

### 13.4 The headline

| | MGD | % of total |
|---|---|---|
| Total footprint | 51.42 | — |
| Consumed **in** the Potomac basin | 2.07 | **4.0%** |
| Consumed in **other** basins | 44.68 | **86.9%** |
| Scope 3, basin not locatable | 4.67 | 9.1% |

**About 96% of the consumptive water footprint of Prince William County's data centres is consumed outside the basin the buildings occupy.**

Two consequences follow, and they are the paper's argument:

1. **North Anna alone gives up 13.68 MGD to serve these buildings — 6.6× the entire local Scope 1 draw of 2.07 MGD.** A reservoir in a different basin, in a different county, is the single largest water body affected by Prince William's data centres, and it is affected roughly seven times more than the streams the buildings actually sit on.

2. **The reviewing body and the affected basin do not overlap.** Every one of these facilities was approved through Prince William County land-use review — rezonings, special use permits, site plans, all Potomac-basin instruments. That process has authority over the 4% and none whatsoever over the 96%. The Lake Anna shoreline had no standing in any of the hearings recorded in §8.

This is why the local-versus-total framing common to data-centre water reporting is not merely incomplete but misdirected: it scrutinises the small share that is visible to the permitting authority and is silent on the large share that is not.

### 13.5 What would sharpen it

- **19.2% of Scope 2 is unattributed** (`Municipality` / `Wells`). Resolving which utilities supply Hopewell and the other purchased-water plants would move ~8.6 MGD onto a named basin — likely James, which would push that basin past 60%.
- The plant-level split uses **2015** USGS consumption as the allocation weight. Dominion's fleet has changed since; a newer EIA-923/860 pull would re-weight it.
- Marginal versus average dispatch. The attribution here is average-mix. A **marginal** analysis — which plant actually turns up when a Loudoun/Prince William data centre adds load — would plausibly shift weight toward gas and away from nuclear, since nuclear runs baseload regardless. That is the single most defensible improvement available and is the natural next piece of work.
