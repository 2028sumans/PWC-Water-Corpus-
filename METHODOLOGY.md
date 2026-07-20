# Scope 1/2/3 Water Footprint Estimator — Methodology, Worked Example, and Known Gaps

**Status:** as-shipped.
**Source of truth:** [`indirect_water_footprint.py`](indirect_water_footprint.py). Every number below was read out of that module, recomputed from the built [`public/data/facility_profiles.json`](public/data/facility_profiles.json), or quoted directly from a source document in [`public/data/policy/`](public/data/policy/). None of it is written from memory.

This document exists to be attacked. Section 6 lists the errors and soft spots found so far — including one retraction, one circular validation, and one constant that the source document uses in the opposite direction from this tool.

> **Current headline (as of the §18 refresh, 19 July 2026).** County-wide total: **60.0 MGD, 90% credible interval 53.9–66.6** (Monte Carlo median, average grid mix; plug-in central 57.1 MGD). Marginal-mix median 46.8 MGD. Scope 2 is ~87% of the total. The single largest affected water body is **North Anna / Lake Anna in the York basin at 21.6 MGD** — outside the Potomac basin the buildings sit in. Sections 0–14 were written earlier in the project's evolution and some carry pre-refresh illustrative numbers; **§18 states what changed and is authoritative on the Scope 2 factors, §16 on average-vs-marginal, §17 on the credible intervals.** Where an early section's number conflicts with §16–§18, the later section wins.

---

## 0. What the model is, in one paragraph

Every estimate descends from a single physical input — **gross floor area** — converted to **effective electrical load** by one constant, then multiplied by scope-specific water intensities. There is no per-facility water measurement anywhere in the chain. Following the July 2026 USGS pull, the Scope 2 intensities are Virginia-specific measured values; the power spine is not, and it is now the only remaining dominant assumption.

```
GFA (sqft) ──÷ density──> effective MW ──┬── × WUP (gal/MW/day) ─────────> Scope 1
   (density banded by operator/vintage,  ├── × PUE × 24h × ~226 gal/MWh ─> Scope 2
    §15; or permit MW where available)   └── (Scope 1 + Scope 2) × 5–15% ─> Scope 3
```
*(Blended Scope 2 intensity ~226 gal/MWh on the refreshed §18 factors; older sections show the pre-refresh 198.)*

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
| 2 | **8,818 sqft/MW is run backwards.** ICPRB uses it once, to convert Loudoun's 0.017 gal/day/sqft into the 150 gal/MW/day tier. Power in their Eq. 6-3 comes from air-permit generator capacity, never floor area. | **Validated (§15)** — the 45 permit-backed PWC buildings measure a median 8,638 sqft/MW, reproducing 8,818 within 2% by an independent method; still the largest swing, now shown to be real fleet heterogeneity (2.2×), not error |
| 3 | **Scope 2 used national medians.** Nuclear at 700 gal/MWh blended Surry (once-through saline, 0 consumption) with North Anna (Lake Anna, 417). | Fixed — VA-specific USGS values; swing 54% → 12% |
| 4 | **Campus profiles never ran `permit_conditions_for()`**, silently dropping proffer cooling conditions for all 51. | Fixed |
| 5 | **Campus entitlement GFA duplicated onto smaller campuses.** Manassas Point PRA implied FAR 3.34, Battlefield Business Park 2.68 — both share a GFA with a larger campus. | Flagged via `implied_far` / `far_flag`, not silently corrected |
| 6 | **Suspected PUE double-count.** | **Retracted** — Eq. 6-3 says "Effective **(IT)** Power Demand", so multiplying by PUE is right |
| 7 | **`unknown` PUE applied to 147 unbuilt buildings.** Their vintage is not unknown; they are being built now. | Fixed — `new_build` class; `unknown` now empty |
| 8 | **Withdrawal and consumption are summed.** Scope 1 is delivered water, Scope 2 is consumed water. The 0.75 factor exists to reconcile them and is computed but unused. | **Closed (§14.1)** — both bases now reported: 51.42 MGD delivered, 50.85 MGD consumptive |
| 9 | **Peak-day ignores narrowing** — always uses 3,060 gal/MW/day, giving a 20× peak:average ratio on narrowed facilities. | **Closed (§12)** — peak is now a ratio on the building's own central WUP; county peak 23.36 → 20.50 MGD (9.9×) |
| 13 | **Market-based Scope 2 was missing.** GHG Protocol requires location- *and* market-based figures; only the former existed, so the model did not speak the operators' accounting language. | **Closed (§14.2)** — 44.68 location-based vs 35.55 market-based; the 9.13 MGD gap is the finding |
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
| Broad Run | 166 | 5,981 | 1.621 | 16.05 | 2,476 | **6,484** |
| Bull Run | 61 | 1,160 | 0.344 | 3.40 | 1,716 | 1,983 |
| Powells Creek | 14 | 289 | 0.060 | 0.60 | 1,781 | 338 |
| Quantico Creek | 2 | 29 | 0.009 | 0.09 | 1,316 | 67 |

The concentration is the finding. **Broad Run carries 80% of the county's local data-centre draw** — 166 of 243 buildings — and on a summer peak day that is ~6,500 gallons per watershed acre per day, 3.3× Bull Run and 19× Powells Creek. Whatever the county-wide number is, the stress is not county-wide.

### 13.3 Scope 2 — consumed in basins the county has no standing in

*(Figures below use the refreshed USGS 2008–2020 factors of §18; the earlier draft of this section used the 2015 release.)*

| Basin | MGD | % of Scope 2 |
|---|---|---|
| **York (Lake Anna / North Anna)** | **21.62** | **43.3%** |
| James | 10.99 | 22.0% |
| *unresolved — purchased municipal water* | 8.42 | 16.9% |
| Potomac | 4.10 | 8.2% |
| Roanoke | 2.77 | 5.5% |
| Tennessee/Clinch | 1.63 | 3.3% |
| Rappahannock | 0.38 | 0.8% |

The York total is essentially **North Anna alone**: Virginia's other nuclear station, Surry, reports zero consumption because it is once-through cooled on the tidal James, so the entire nuclear share of Prince William's electricity lands on Lake Anna — and with the refreshed nuclear factor (391 gal/MWh, §18) that share is now the largest single basin by a wide margin. The James total is the older fresh-consuming gas plants (Tenaska, Bear Garden); the Potomac line is Possum Point (gas). Dominion's three largest *modern* gas plants consume reclaimed water and appear in no basin here (§18.4).

### 13.4 The headline

| | MGD | % of total |
|---|---|---|
| Total footprint (plug-in central) | 57.13 | — |
| Consumed **in** the Potomac basin | 6.14 | **10.7%** |
| Consumed in **other** basins | 45.80 | **80.2%** |
| Scope 3, basin not locatable | 5.19 | 9.1% |

**About 88% of the *locatable* consumptive water footprint of Prince William County's data centres is consumed outside the basin the buildings occupy** (45.80 of 51.94 MGD; the Potomac in-basin share rose after the §18 refresh moved Possum Point's gas consumption onto the Potomac).

Two consequences follow, and they are the paper's argument:

1. **North Anna alone gives up 21.62 MGD to serve these buildings — 10.6× the entire local Scope 1 draw of 2.03 MGD.** A reservoir in a different basin, in a different county, is the single largest water body affected by Prince William's data centres, and it is affected roughly *eleven times* more than the streams the buildings actually sit on.

2. **The reviewing body and the affected basin do not overlap.** Every one of these facilities was approved through Prince William County land-use review — rezonings, special use permits, site plans, all Potomac-basin instruments. That process has authority over the ~11% and almost none over the ~88%. The Lake Anna shoreline had no standing in any of the hearings recorded in §8.

This is why the local-versus-total framing common to data-centre water reporting is not merely incomplete but misdirected: it scrutinises the small share that is visible to the permitting authority and is silent on the large share that is not.

### 13.5 What would sharpen it

- **~17% of Scope 2 is unattributed** (`Municipality` / `Wells`). Resolving which utilities supply Hopewell and the other purchased-water plants would move ~8.4 MGD onto a named basin.
- ~~The plant-level split uses 2015 USGS consumption.~~ **Done (§18):** refreshed to the USGS 2008–2020 reanalysis, pooled 2018–2020.
- ~~Marginal versus average dispatch.~~ **Done (§16):** marginal analysis added; nuclear drops out entirely, confirming the York attribution is an average-mix artifact.

---

## 14. Two errors of basis, both now reported explicitly

### 14.1 The county total was summing two different quantities

Flagged in the §8 ledger and left open; closed here.

`total_mgd_central` added Scope 1 to Scope 2 as if they measured the same thing. They do not:

- **Scope 1 is delivered water.** ICPRB's WUP intensities are derived from *utility billing records* — what the building buys. Some of that returns to the basin as cooling-tower blowdown discharged to sewer. ICPRB's own **0.75 consumptive-use factor** exists precisely to convert delivered volume to consumed volume, and this model computed it per building and then never used it.
- **Scope 2 is consumption.** USGS reports withdrawal and consumption in separate columns; the factors here are the consumption column.

So the headline number answered neither question cleanly. Both are now reported:

| Basis | County total |
|---|---|
| Delivered (Scope 1 as billed) | **51.42 MGD** |
| Consumptive (0.75 applied to Scope 1) | **50.85 MGD** |

The gap is small — 0.57 MGD, ~1% — because Scope 1 is only 4% of the total, so the factor has little to bite on. That is worth stating: **the delivered-vs-consumptive distinction, which dominates conventional water-use reporting, is nearly irrelevant to a data centre's total footprint precisely because so little of that footprint is local.** It is the right correction to make and it changes almost nothing, and both halves of that sentence are findings.

Use the **delivered** figure against utility supply and capacity planning; use the **consumptive** figure against basin water balance and the §13 attribution.

### 14.2 Market-based Scope 2 was missing

The GHG Protocol requires **dual reporting**: a location-based figure (the grid you physically draw from) and a market-based figure (what you contracted for). Only the location-based figure existed. Since every hyperscaler in the dataset claims 100% renewable matching, the market-based figure is the one those operators would publish, and its absence made the model easy to dismiss as not speaking the operators' language.

Contracted renewables are carried at **15 gal/MWh** — not zero. Solar PV consumes water for panel washing (~26 gal/MWh in NREL's tables) and wind is effectively nil; Dominion's contracted build is predominantly solar, so 15 is a midpoint rather than the 0 used for the renewable slice of the grid mix.

| | MGD |
|---|---|
| Scope 2, location-based | **44.68** |
| Scope 2, market-based | **35.55** |
| Accounted away by contract | **9.13 (20%)** |

**Only 57 of 243 buildings carry a matching claim** — the hyperscalers. The colocation operators (QTS, Digital Realty, Aligned, STACK, CloudHQ) have renewable commitments of their own that are not encoded here, so 35.55 MGD is an *upper* bound on the market-based total; the real published-figure sum would be lower still.

### 14.3 Why the gap is the finding

The market-based figure is reported because the protocol requires it and operators quote it. It is not reported because it describes anything physical.

**A REC retired against a wind farm does not stop Lake Anna evaporating.** The water consumed to serve a building in Broad Run was consumed at the plant that actually served it, at the hour it served it. Annual contractual matching is netted over a year and over a continent; evaporation is neither.

The 9.13 MGD gap is therefore **the volume of real, physical, Virginia-basin water consumption that disappears from operators' published water accounting through contractual instruments alone** — roughly 4.4× the entire local Scope 1 draw of 2.07 MGD.

This compounds §13 rather than duplicating it. Two independent mechanisms move the same water out of view:

| Mechanism | What it hides | Volume |
|---|---|---|
| **Spatial** (§13) | consumption occurs outside the reviewing basin | 44.68 MGD, 87% of total |
| **Contractual** (§14.2) | consumption is netted away by annual REC matching | 9.13 MGD, 20% of Scope 2 |

Neither is fraud, and neither operator behaviour is unusual — both are what the standard frameworks prescribe. The point is that the frameworks were built for carbon, where a tonne is a tonne wherever and whenever it is emitted, and **water is not fungible across basins or across seasons**. Annual, contract-based, location-blind accounting is a defensible carbon method and a poor water method, and this county is a clean demonstration of the difference: peak local draw is 9.9× the annual average (§12) and 96% of consumption happens somewhere the buildings' regulator cannot see (§13).

That is the paper's thesis, and it is now supported by three independent numbers rather than an argument.

---

## 15. Resolving density with power density — the natural experiment

The largest remaining swing factor (52%) is infrastructure density, the sqft/MW constant that converts floor area to IT load. The standard way to attack it is a **power-density** figure — IT load (kW) ÷ floor area (sqft). Acting on that led somewhere better than a literature lookup.

### 15.1 The denominator is the whole problem

Power density is meaningless without stating what floor area is in the denominator. The same 100 kW reads as three different numbers (Silverback 2023):

| Denominator | W/sqft |
|---|---|
| Rack footprint only | 240 |
| Production space (racks + aisles + in-row gear) | 113 |
| Room envelope (the data-hall enclosure) | 78 |

A 3× spread from a definitional choice alone. And published W/sqft figures are almost always quoted on **white space** — the raised-floor data hall — while white space is only **40–50% of a data centre's gross internal area** (RICS 2024; the project's own ePortal record MEC2025-00037 shows 26,000 sqft of hall to 12,000 sqft of adjacent gallery). This model runs on **gross** floor area from the county assessor. Dropping a literature "150 W/sqft" onto GFA would roughly double the implied load. The attachment that prompted this — "divide IT load by the physical size of the equipment room" — is describing white space, not GFA, and the two are not interchangeable.

The conclusion is that a generic W/sqft cannot be imported at all without a basis conversion the source usually does not give. So the model's decision to carry a GFA-basis sqft/MW directly, calibrated on Virginia data, is the correct one — provided that calibration is sound. §15.2 tests it.

### 15.2 The 45 permit-backed buildings are a natural experiment

The buildings whose power comes from a VADEQ air permit do not use the density constant at all — their MW is generator capacity run through ICPRB Equation 6-3. But their **gross floor area is known independently** from the assessor. So `permit_MW ÷ GFA` is an *empirical* power density for real Prince William buildings that never touches the 8,818 assumption. Measured across all 45:

| | sqft/MW | W/sqft GFA | W/sqft white space (÷0.45) |
|---|---|---|---|
| Median | **8,638** | 116 | 257 |
| p10–p90 | 6,293 – 13,759 | 73 – 159 | 162 – 353 |

Two results, both material:

1. **The permit-backed median (8,638) reproduces ICPRB's 8,818 within 2%.** These are fully independent methods — PWC backup-generator capacity versus ICPRB's division of Loudoun Water billing by an air-permit power estimate — and they land on the same constant. That is the strongest validation of the density figure in the project, and it is not circular (§0's circularity was about the *water* figure; this is the *power* figure, derived from generator capacity, not water at all).

2. **The fleet genuinely spans 2.2×.** Density is not a constant with measurement noise around it; PWC data centres really do range from 73 to 159 W/sqft GFA. That reframes the 52% swing: it is **real heterogeneity, not ignorance.** No single density can be "correct" for a fleet this varied.

### 15.3 The heterogeneity is operator-structured

The 2.2× spread is not random — it sorts cleanly by operator and design generation:

| Operator | n | median sqft/MW | W/sqft GFA | W/sqft white space |
|---|---|---|---|---|
| Stack | 1 | 5,478 | 183 | 406 |
| Digital Realty | 4 | 6,289 | 159 | 353 |
| Corscale | 5 | 7,177 | 139 | 310 |
| NTT | 2 | 7,509 | 133 | 296 |
| Amazon AWS | 18 | 8,627 | 116 | 258 |
| QTS | 6 | 9,376 | 107 | 237 |
| Microsoft | 2 | 11,942 | 84 | 186 |
| Iron Mountain | 7 | 13,769 | 73 | 161 |

These white-space figures fall squarely inside the published envelope — 100–150 W/sqft for standard builds, 250–450 for modern AI-class (Uptime/LBNL). The densest PWC operators (Stack, DLR) sit in the AI-class band; colocation and retrofit stock (Iron Mountain, ~2× less dense) sits at the bottom. **Build year predicts this poorly** (retrofits and colo carry recent assessor dates on old bones), which is exactly why the earlier vintage banding was noisy. **Operator predicts it well.**

### 15.4 What changed in the model

Density for a GFA-only building is now calibrated to **its own operator's permit-backed buildings** in the county, wherever ≥3 such calibrators exist (`build_operator_density_index`). This reaches **32 of 198** GFA-only buildings — all Amazon and Iron Mountain, the two operators with both enough calibrators and unbuilt stock. The rest keep the vintage band.

Effect on the county central total: **51.42 → 50.30 MGD (−2.2%)**. The correction is downward because the model had been assigning unbuilt Amazon buildings the `new_build` band (7,070 sqft/MW), denser than Amazon's *actual* built estate (8,627) — i.e. it was over-crediting future AWS buildings with AI-class density they have not, on the evidence, been building to.

Density remains ~52% of the swing, and that is now a deliberate statement rather than an unresolved gap: the sweep reflects genuine fleet heterogeneity, and the only thing that zeroes a single building's density uncertainty is a permit — which is why the 45 permit-backed buildings carry none. `validate_power_density.py` reproduces this whole chain.

### 15.5 Sources

- Silverback Data Center Solutions, *Watts per Square Foot* — room/production/rack denominators.
- RICS Construction Journal (2024), *Data centre growth* — white space = 40–50% of gross internal area; ~1:1 white-to-grey.
- JLARC, *Data Centers in Virginia* (Dec 2024) — ~5,050 MW across ~340 built Virginia buildings.
- Uptime Institute / LBNL benchmarking — 100–150 W/sqft standard, 250–450 W/sqft modern AI-class.
- ICPRB 2025 WMA Water Supply Study, §6.2 — 8,818 sqft/MW fleet average.

---

## 16. Average vs marginal dispatch — the third way the water hides

The largest weakness left in the estimator was that Scope 2 — **87% of the total** — used Dominion's *average* generation mix. Fixing it produced the paper's most consequential single result.

### 16.1 The distinction

Average-mix accounting asks: *what share of the grid's total water is this building's share of demand?* On that basis 25% of every data centre's electricity is nuclear, so 25% of its Scope 2 water lands on North Anna and the York basin (Lake Anna).

But that is not the causal question. A **new** data-centre load is served at the **margin** — by whatever unit is next in the dispatch stack — and **nuclear never moves.** North Anna runs flat out regardless of whether a data centre in Broad Run switches on; it is baseload. The unit that actually spins up is a gas plant. So the marginal question — *how much more water is consumed because this building exists?* — has a completely different basin answer.

### 16.2 The marginal mix

From PJM marginal-fuel data (2022): combined-cycle gas was the marginal unit **61.7%** of hours, peaking gas ~**17.2%**, coal **10.0%**, wind **11.1%**; nuclear essentially never. Applying the same Virginia-specific water factors (peaking simple-cycle gas carried at ~20 gal/MWh — no steam cycle) gives a marginal intensity of **~172 gal/MWh**, against the average-mix **~225** (both on the refreshed §18 factors).

### 16.3 The result

*(Refreshed to the USGS 2008–2020 factors, §18.)*

| | Average-mix MGD | Marginal MGD |
|---|---|---|
| **York — North Anna / Lake Anna** | **21.6** | **0.0** |
| James (gas fleet) | 11.0 | 12.0 |
| purchased municipal (unresolved) | 8.4 | 9.2 |
| Potomac (Possum Point gas) | 4.1 | 4.5 |
| Roanoke (coal) | 2.8 | 9.2 *(see caveat)* |
| other basins | 2.0 | 3.0 |
| **Scope 2 total** | **~50** | **~46** |

Two findings:

1. **The total barely moves, but the basin allocation transforms.** The York-basin attribution — 21.6 MGD, the single largest water body in the whole study, 10.6× the entire local Scope 1 — **falls to exactly zero under marginal accounting.** The Lake Anna displacement identified in §13 is, to first order, an *artifact of average-mix accounting.* The water a new Prince William data centre actually causes is consumed in the **James** gas fleet, not at North Anna. The §18 refresh, by raising the nuclear factor, makes this gap larger, not smaller: ~22 MGD now hinges entirely on the average-vs-marginal choice.

2. This is a **third, independent mechanism** by which the footprint escapes view, and it completes the paper's argument:

| Mechanism | Section | What it hides | Under scrutiny |
|---|---|---|---|
| **Spatial** | §13 | consumption is in a different basin than the buildings | ~88% out-of-basin |
| **Contractual** | §14 | consumption is netted away by annual REC matching | 20% of Scope 2 |
| **Temporal / causal** | §16 | *which* basin depends on average-vs-marginal framing | the entire York attribution |

All three are the same underlying failure: **carbon accounting conventions — annual, location-blind, average-mix, fungible — applied to water, which is none of those things.** A tonne of CO₂ is a tonne wherever, whenever, and from whichever plant. A gallon is not: it matters which basin, which season, and which generator on the margin. This county demonstrates all three divergences quantitatively.

### 16.4 Caveats and the route to sharpen it

- **The marginal mix is PJM-wide, not Dominion-zone-specific.** Virginia has nearly retired its coal (3% of generation), so the 10% marginal-coal share overstates coal's local role — the **Roanoke figure (8.1 MGD) is an upper bound**, and the true Dominion-zone marginal is *even more* gas-and-James-concentrated than shown. The York→0 result is robust to this; the coal reallocation is not.
- **Marginal fuel *frequency* is used as a proxy for marginal *energy* share.** A Data Miner pull of hourly marginal MW by fuel for the Dominion zone (2023–24) would replace both approximations and is the clean next step.
- Neither average nor marginal is "the" right number — GHG Protocol reports average (location-based) and this study keeps that as the headline, with marginal reported alongside as the causal complement. The point is that **for water they disagree about the receiving basin entirely**, which no carbon framework would ever surface.

---

## 17. Monte Carlo uncertainty — facility-centric priors, correlated draws

The range shipped through §16 was an **envelope**: the sum of each scope's independent minimum and maximum. That is a conservative outer bound, not a probability — it assumes every parameter sits at its worst simultaneously, which never happens, and for the county it spans **33.6–87.6 MGD**, too wide to be useful. `monte_carlo.py` replaces it with a real distribution: 40,000 draws of every parameter through the same arithmetic.

### 17.1 Two design choices that make it honest

**Facility-centric priors.** Every building samples from a distribution keyed to *its own evidence*, not a shared average — this is the "not just averages" principle applied to uncertainty itself:

| Parameter | Well-evidenced building samples… | Weakly-evidenced building samples… |
|---|---|---|
| Power | permit generator capacity (Eq 6-3 factor) | its operator's measured density band (§15) or a vintage band |
| Scope 1 WUP | a narrow air-cooled tier (operator cooling commitment) | the full 150–1,577 technology envelope |
| Scope 2 PUE | a ±0.06 band around the operator's published fleet PUE | a wide vintage band |

Better evidence → narrower prior → narrower interval, **per building**.

**Correlation.** Parameters shared across buildings are drawn **once per iteration** and applied to all: the grid's water intensity (one grid), the ICPRB WUP calibration (one scale), the Scope 3 proportion (one assumption), the Eq 6-3 factor (one ICPRB standard), and per-operator / per-class density and PUE calibration offsets. If these were drawn independently per building, 243 independent errors would cancel and the county interval would collapse to a spuriously tight number. Idiosyncratic, building-specific variation *is* drawn independently and correctly averages down. The result is visible in the numbers: per-building intervals are wide (median **±22%**) but the county interval is tighter (**±11%**) — because the idiosyncratic part averages out while the systematic part does not. An estimator that reported ±11% per building would be lying; one that reported ±22% for the county would be double-counting. *(The county interval widened from ±8% to ±11% with the §18 refresh, because the new nuclear factor carries a large systematic uncertainty that, being grid-wide, cannot average away.)*

### 17.2 The result

*(Refreshed to the USGS 2008–2020 factors, §18.)*

| | Median | 90% credible interval | Envelope (min/max) |
|---|---|---|---|
| County total, average mix | **60.0 MGD** | **53.9 – 66.6** | 39 – 100 |
| County total, marginal mix | 46.8 MGD | 42.0 – 52.0 | — |

The 90% CI is roughly **±11%**, against the envelope's ±50%. This is the number to quote in a paper.

### 17.3 A real convexity correction

The Monte Carlo median (60.0) sits **~5% above the plug-in central (57.1 MGD)**. This is not a bug and not noise — it is Jensen's inequality. Water scales with **1/density**, density is uncertain, and the operators' measured density bands are **right-skewed** (e.g. Amazon's permit-backed buildings run 7,259–12,735 sqft/MW around a median of 8,627). The expectation of `1/density` therefore exceeds `1/median density`, so the probability-weighted total is higher than the figure you get by plugging in the central density. **A point estimate built on central density systematically understates the expected footprint.** The Monte Carlo median is the better central estimate, and is recommended as the headline figure going forward; the plug-in central is retained and labelled as such.

### 17.4 What the intervals reveal about evidence

Per-building 90% interval widths: narrowest **29%**, median **43%**, widest **62%** of the median. Two findings fall out:

- **Permit-backed buildings are not much tighter than floor-area buildings** (median width 50% vs 43%). Replacing an assumed density with measured generator capacity removes the density-calibration risk and the backwards-8,818 dependency — a real gain in *accuracy* and *independence* — but ICPRB's Equation 6-3 factor (0.5 redundancy × 0.8 utilization) is itself a ±30% assumption, so the *interval* does not narrow. Even the best-evidenced buildings are ~±25% until someone meters actual load.
- The buildings with an operator cooling commitment *and* a disclosed PUE *and* permit power are the narrowest (~29%); those on GFA + vintage bands + technology-envelope cooling are the widest (~62%). The interval width is, in effect, a per-building **evidence score**.

### 17.5 Limits

- Distributions are triangular (min/mode/max), chosen for defensibility over a fitted shape no data supports.
- Correlations are handled at the group level (systematic vs idiosyncratic), not as a full covariance matrix; cross-parameter correlations (e.g. dense buildings also running low PUE) are not modelled.
- The priors inherit every limitation of the underlying evidence — most importantly that **0 of 243 buildings have metered water or a confirmed cooling type**, so the intervals quantify *parameter* uncertainty, not the structural gap that no facility discloses its consumption.

---

## 18. Refreshing the generating-side data — USGS 2008–2020 reanalysis

Every Scope 2 number rested on the USGS **2015 v1.2** thermoelectric release. The single-year, nine-year-old snapshot was the oldest link in the chain. It is now replaced by the USGS **2008–2020 reanalysis** (Galanter et al., 2023; FEWSR + TOWER heat-and-water budget models), pooled over **2018–2020** and generation-weighted. Derivation: [`usgs_va_factors.py`](usgs_va_factors.py); vendored Virginia slice: `data/usgs_te_water_2008-2020_VA.csv`.

### 18.1 The factors moved — nuclear most of all

| Fuel | Old (2015 v1.2) | New (2018–2020 reanalysis) | Bounds (reanalysis cu_lower/upper) |
|---|---|---|---|
| **nuclear** | 242 | **391** | 305–477 |
| natural gas CC | 213 | **196** | 160–231 |
| coal | 451 | **474** | 389–560 |

The nuclear jump drives everything. The reanalysis puts **North Anna at ~737 gal/MWh — and it is stable to ±1% across all thirteen years (2008–2020)**, so this is a robust model estimate, not a spike. The old release implied ~417. Generation-weighted with Surry's zero (once-through tidal saline, unchanged), Virginia nuclear rises from 242 to 391. Notably, 737 is now *consistent* with NREL's 700 national nuclear median — the old 242 had made Virginia nuclear look anomalously dry, when in fact North Anna's cooling lake evaporates at roughly the national rate and it was Surry's zero, averaged in, that pulled the fleet figure down.

Bounds now come from the reanalysis's own `cu_lower_mgd` / `cu_upper_mgd` columns rather than the old MIN/MAX, and feed the Monte Carlo (§17) directly.

### 18.2 Effect on the headline

| | Before refresh | After refresh |
|---|---|---|
| Blended average intensity | ~198 gal/MWh | **~225 gal/MWh** |
| County total (plug-in central) | 50.3 MGD | **57.1 MGD** |
| County total (MC median, 90% CI) | 53.5 [49.6, 57.8] | **60.0 [53.9, 66.6]** |
| County total (marginal-mix, MC median) | 49.5 | **46.8 [42.0, 52.0]** |

Scope 2 rises ~14% and now dominates the total even more heavily. The Monte Carlo interval **widens from ±8% to ±11%**, correctly: the refreshed nuclear factor carries a wide systematic uncertainty (305–477), and because nuclear is a large, correlated share of Scope 2, that uncertainty does not average away.

### 18.3 Effect on the basin finding — it gets stronger

The refresh amplifies the paper's core result. North Anna's larger factor pushes the **York-basin (Lake Anna) attribution from 13.4 to 21.6 MGD — now 10.6× the entire local Scope 1 draw** (was 6.6×). Under marginal dispatch it still falls to **0.0** (nuclear is never marginal), so the average-vs-marginal divergence of §16 is now even more dramatic: the refresh widens the gap between the two accountings from ~13 MGD to ~22 MGD, all of it on one out-of-basin reservoir.

### 18.4 A finding hiding in the absences — reclaimed water

Three plants are **conspicuously missing** from the freshwater model, and their absence is itself a result. Dominion's three largest and newest combined-cycle stations —

| Plant | Capacity | Online | Cooling water |
|---|---|---|---|
| Greensville County | 1,605 MW | 2018 | reclaimed municipal |
| Brunswick County | 1,376 MW | 2016 | reclaimed municipal |
| Warren County | 1,350 MW | 2014 | reclaimed municipal |

— together **~4.3 GW, roughly a third of Dominion's gas capacity** — consume essentially no fresh basin water and are therefore absent from a *freshwater* model. Two consequences:

1. **The 196 gal/MWh gas factor is for the older, fresh-consuming plants** (Tenaska, Bear Garden, Possum Point). The fleet-average *freshwater* intensity of a Dominion gas MWh is lower than 196, because a large and growing share of gas generation comes from plants that touch no fresh basin water. The 196 is therefore an upper bound on Scope 2's gas contribution — the refresh, if anything, still *over*-attributes freshwater to gas.
2. **This is a water-sourcing shift worth stating in its own right:** Virginia's newest thermoelectric capacity is deliberately built on reclaimed municipal water, moving consumption off fresh surface water and onto treated wastewater. It is the generating-side analogue of the data centres' own closed-loop trend, and it means the marginal gas unit that answers a new data-centre load (§16) may consume even less fresh water than the marginal figure assumes.

### 18.5 Remaining limits

- **The window ends in 2020.** Chesterfield's coal units retired in 2023 and are still present (as multi-fuel) in the data; the coal factor is therefore slightly more coal-weighted than today's fleet. Immaterial to the total (coal is 3% of the mix) but noted.
- **Generation weights are 2018–2020**, not 2025. The factors are intensities (gal/MWh), so this matters far less than for an absolute total, but the Dominion mix shares (§3) remain a separate 2025 estimate layered on top.
- The reclaimed-water plants above are a genuine data gap, not a modelling choice — closing it needs EIA-923 Schedule 8 cooling-water records for those specific plants, the natural next pull.

---

## 19. Water-stress context — drought, warming, and seasonality (added after the dataset re-audit)

A full re-read of the 81 raw datasets (see `DATASET_AUDIT.md`) found that the
NOAA climate series — 1895→2026 monthly, for the county — had never been used.
They carry the water-*stress* context the footprint must be read against.
`climate_context.py` computes them; `public/data/climate_context.json` ships them.

- **Extreme drought, now.** Palmer PDSI/PHDI = **−5.3 (April 2026)** — the driest
  **0.9% of all 1,576 months since 1895** (min ever −6.96). The county is in a
  near-record drought as the data-center estate is built out.
- **Cooling demand is rising.** Cooling degree days are **+37% over the record**
  (20th-century decades ~900–1,150; **2010s–2020s ≈ 1,365/yr**). The evaporative
  Scope 1 load scales with CDD, so the per-MW water intensity of cooling has a
  structural upward trend, not a stationary one.
- **It is summer-concentrated.** **~88–92% of annual cooling degree days fall in
  Jun–Sep** (Jul 33%, Aug 27%, Jun 20%, Sep 12%). This is the same window in which
  the 9.9× peak day lands (§12), competing outdoor demand peaks, and river flows
  are lowest — the ICPRB study's explicit concern (2025 WMA Study §6.2).
- **Precipitation deficit.** Last 12 months are **−15% below the long-run mean**.

The convergence *is* the finding: rising, summer-peaked cooling demand arriving
during a 99th-percentile drought, with ~96% of the resulting consumption occurring
out-of-basin (§13). Four independent series point the same way. This reframes the
whole footprint from a static inventory into a water-stress question.

---

## 20. Reconciliation with the source reports (ICPRB & JLARC, read in full)

The re-audit read the ICPRB 2025 WMA Study §6 and JLARC Rpt598 line by line. They
**confirm the model's foundations** and fix two framings.

### 20.1 Confirmed exactly
- **Eq 6-2 / 6-3, factors 0.5 / 0.8 / 0.75**, and the WUP tiers all match ICPRB §6.2
  verbatim: PWC 0.42 MGD / 4.2 MGD peak (2023) → **309 / 3,060** ✓; Loudoun 1,006 ✓;
  air-cooled **150** (= 0.017 gal/day/sqft × 8,818) ✓; fully-water-cooled 1,577 ✓.
- **8,818 sqft/MW is used once, to derive the 150 tier** — power in Eq 6-3 is
  generator capacity, never floor area. This is exactly the "run backwards" point in
  §1/§6, now confirmed from the source text.
- **JLARC benchmarks match:** office building **6.7 MGal/yr (0.018 MGD)** ✓; largest
  building **243 MGal/yr (0.666 MGD)** ✓ — the `benchmark_check` anchors are correct.

### 20.2 Framing correction — Scope 1 vs Scope 1+2+3 (important)
JLARC's whole-Virginia **direct** data-center water use in 2023 was **2.1 billion
gallons = 5.75 MGD** (≈⅓ reclaimed; <0.5% of state withdrawals); ICPRB's WMA
**direct** use is **~4 MGD average / ~15 MGD peak (2025)**. These are **Scope 1
(on-site) only.** This model's headline **~57–60 MGD is Scope 1+2+3** and is
dominated by Scope 2 (off-site generation water, ~87%). The model's **Scope 1 for
PWC (~2 MGD)** is fully consistent with those sources. **The 57–60 MGD figure must
never be compared naively against JLARC's 5.75 MGD or ICPRB's 4 MGD** — they measure
different boundaries. Every headline now carries the scope label for this reason.

### 20.3 Peak ratio is cooling-type-dependent — capped (code fixed)
The model applied PWC's observed **9.9× peak:average ratio** (3,060/309) to every
tier. But that ratio is PWC's, whose fleet is air-/hybrid-cooled and therefore
highly weather-sensitive. **Water-cooled facilities have a much lower peak ratio:**
ICPRB observed **2.7× in Loudoun** (2,716/1,006), and Table 6-5 tops out at **5,200
gal/MW/day** peak (High, 90% water-cooled). Applying 9.9× to the fully-water-cooled
central (1,577) would give **15,600 — ~3× ICPRB's ceiling**, i.e. the flat ratio
*overstates* peak for water-cooled sites. Fixed: `peak_wup` is now capped at
ICPRB's fully-water-cooled peak envelope (5,200 gal/MW/day). In practice this
changes almost nothing today because 0/243 buildings sit on the water-cooled
central tier (no cooling-type evidence exists), but the logic is now correct.

### 20.4 Utility's own current figures (independent cross-check)
Prince William Water's 2025 FAQ: data centers were **3.8% of average daily demand
and 10.1% of maximum daily demand** (peak/avg ≈ 2.7× on a demand-share basis).
ICPRB basin-wide: data centers are **9% of annual / up to 12% of summer consumptive
use** in the WMA. These bound the estimate independently of the WUP chain.

### 20.5 Reclaimed water is still consumptive (corrects §18.4)
The ICPRB study and fact sheet are explicit: for evaporative cooling, **reclaimed
water is largely lost, not returned — it reduces return flows.** §18.4 framed the
reclaimed-water gas plants (Greensville/Warren/Brunswick) as ~zero fresh-basin
impact; the correct framing is that they **shift the loss from withdrawal to
return-flow reduction — still a consumptive loss**, just invisible to a
withdrawal-based freshwater model. Same caveat applies to data centers on Broad Run
WRF reclaimed water.

### 20.6 The PUE–water tradeoff (JLARC Appendix J)
JLARC states plainly that a **PUE mandate would *increase* water use**, because
water-dependent cooling uses less energy. This is the mechanism behind the §14/§16
tension: pushing PUE down (an energy goal) pushes water up. Hyperscale fleet PUE is
**1.1–1.4**, confirming the model's disclosed/vintage PUE bands.

### 20.7 Additional density anchors
Independent basin/state densities from the reports: ICPRB basin-wide **~10,370
sqft/MW** (56M sqft / 5,400 MW); JLARC statewide **~12,475 sqft/MW** (63M sqft /
5,050 MW). Both are less dense than PWC's permit-backed median (8,638, §15) because
they include older Loudoun and colocation stock — consistent with the vintage/
operator banding, and useful as outer anchors.

---

## 21. NPDES — corrected from "zero" to the precise, evidenced picture

The prior headline ("0 of 243 hold NPDES") was too crude. The EPA ECHO / ICIS data,
read in full, show:
- **~17 Prince William data centers DO hold VPDES permits — but they are VAR10
  construction-stormwater general permits** (erosion/sediment during building;
  temporary; no operational-water reporting), not process/discharge permits.
- **Exactly one regional hyperscale — Microsoft IAD11 (Loudoun, VAG25 cooling-water
  general permit) — is required to report discharge flow, temperature, and chlorine,
  and is in non-compliance: 41 overdue-DMR violations, flow fields blank.** So the
  operational-discharge pathway exists but is unused/unreported even where mandated.
- **County ECHO loadings (2026): 32 permitted dischargers in PWC, zero data centers**
  (dominant discharger is Dominion Possum Point). Only **two Virginia data centers**
  hold their own DEQ withdrawal permit (JLARC).

Corrected statement: *Prince William data centers hold construction-stormwater
permits, not operational water-discharge or withdrawal permits; their operational
water consumption is structurally unreported, and even the lone regional
cooling-water permit sits in DMR non-compliance.* This is stronger and defensible.

---

## 22. Per-dataset audit of the 81 raw inputs (full read-through)

Every raw dataset in `data/water_raw/` was read in full — structured files
parsed record-by-record, documents and PDFs read whole. This catalogs what each
contains, what it confirms, and what it corrects. (Previously kept in a separate
DATASET_AUDIT.md; consolidated here.)

---

## A. Policy / permit / document JSONs

### Prince_William_Water_FAQ_Extract.csv 🟡🔴
The utility's own words. Material facts the model under-uses:
- **"2025: data centers consumed ~3.8% of average daily demand and 10.1% of maximum daily demand"** in the PWW service area. This is a *2025* utility statement and a direct peak-to-average signal (10.1/3.8 = **2.7× on a demand-share basis**). The model currently anchors to a 2023 "0.42 MGD" figure and derives peak from the 3,060/309 = 9.9× intensity ratio — these are different framings and should be reconciled; the utility's own 2.7× demand-share peaking is a citable cross-check.
- Water **reuse studied for Digital Gateway, "found not currently viable there, but possible elsewhere"** — bears on the reclaimed-water discussion (§18.4).
- Supply chain: West = Fairfax Water Corbalis (Potomac) + wastewater→UOSA→Occoquan Reservoir; East = Griffith WTP (Occoquan Reservoir). Public supply is Potomac River + Lake Manassas, **not groundwater** — so the data centers do not draw down private wells (answers a common objection).
- Planning horizon MWCOG **2045**; "growth pays for growth" (developers fund capacity).

### PP-NewStructure-DataCenterBuildings.json 🟡🔴
County building-permit policy (eff. 2021-04-05). Two things that matter to the model:
- **County's own definition of a data center building requires "at least one megawatt of capacity"** (def. 3C) — a floor, useful for filtering.
- **Shell-first permitting:** a new data center is permitted as ONE building permit / ONE CO, with unused areas built to Storage (S-1) / Business (B) use groups and **"fit-out" later** via Alteration/Repair permits. So **gross floor area is decoupled in time from eventual IT MW** — the shell exists at full GFA before the data halls (and their load) are fitted out. This is a concrete mechanism behind the density (sqft/MW) uncertainty and the convexity in §17: a planned/new building's GFA can precede its MW by years. Should be cited in §15.

### Res No 20-773 Climate Mitigation and Resiliency Goals.json 🟡
BOCS resolution (2020-11-17, passed 5–3). Directs Comprehensive Plan goals of
**100% of the county's electricity from renewable sources by 2035**, county
government ops 100% renewable by 2030, carbon neutral by 2050. Direct tension
with the data-center gas buildout and useful context for market-based Scope 2
(§14.2) and the CEMP.

### pjm_load_report_full.json ⚪🟡
PJM 2026 Load Forecast (Jan 2026). **The DOM (Dominion Virginia Power) zone
forecast is explicitly adjusted for "growth in data center load and a voltage
optimization program."** PJM RTO summer peak +3.6%/yr (10-yr), net energy
+5.3%/yr — data-center-driven. Detailed DOM numbers live in the companion Excel,
not this text. Context for the marginal-dispatch argument (§16): the whole zone
is being reshaped by this load.

### README.txt ⚪
Describes observations-759582.csv only (iNaturalist research-grade species obs,
place_id 744, taxon 20978, 2020–2026). Biodiversity, not water.

---

## B. Climate / drought time series — 🔴🟡 THE BIGGEST MISS

I never opened these. They are NOAA monthly county series (1895→2026-04, 1,576
months) plus daily station series. They carry the water-STRESS context the whole
paper was missing.

### Drought (PDSI / PHDI / PMDI / Palmer_Z .json) 🟡🔴 — headline material
Prince William County is in **near-record extreme drought right now**:
- **PDSI = PHDI = PMDI = −5.3 (April 2026)** — the current reading is in the
  **bottom 0.9% of all 1,576 months since 1895** (min ever −6.96). Palmer-Z −3.0
  (bottom 4%). PDSI below −4 is "extreme drought" by definition.
- The data centers' consumptive demand is landing during one of the **driest
  periods in 130 years**. This is the water-stress hook the AGU framing needs and
  the estimator/METHODOLOGY never mentioned it.

### Cooling Degree Days (Cooling Degree Days.json) 🟡🔴
- **CDD has risen ~35% over the record**: 20th-century decades ~900–1,150; **2010s
  = 1,371, 2020s = 1,364**. Data-center evaporative cooling load (Scope 1) is
  structurally increasing with warming, and the model's single fixed CDD (1,323)
  is slightly low vs the recent decadal mean (~1,365).
- **Seasonality: 80% of annual CDD falls in Jun–Sep** (Jul 33%, Aug 28%, Jun 20%,
  Sep 12%). This is the seasonal shape for a Scope 1 seasonal model — and it
  coincides exactly with summer low-flow and the drought. The 9.9× peak day
  (§12) lands in Jul/Aug when the basin is most stressed.

### Precipitation (Precipitation.json, Manassas) 🟡
- Last 12 months = **34.4 in vs 40.5 in long-run mean (−15%, −6.1 in)** —
  corroborates the drought independently.

### The convergence (this is the argument)
Rising cooling demand (CDD +35%) × concentrated in summer (80% Jun–Sep) × during
99th-percentile drought (PDSI −5.3) × consumed mostly out-of-basin (§13). Four
independent series point the same way. **None of this is in the model today.**

### Station daily series (Manassas US1VAPW0022 2020–26; Vienna USC00448737 1925–2026)
Daily PRCP/SNOW/SNWD (+ TMAX/TMIN for Vienna, 100 yr). Enables daily extreme-heat
peak-day analysis. ⚪ Data-hygiene: the 3 "VIENNA_VA_US_*" files are **byte-identical**
(all hold SNOW/PRCP/SNWD/TMAX/TMIN); the 2 "Manassas *" files likewise. And
meta.location has lat/long **swapped** (latitude −77.x is really longitude).

---

## C. Water permits & discharge (EPA ECHO / ICIS) — 🔴 the "0 NPDES" headline was too crude

I had reduced this to "0 of 243 hold NPDES." Reading the files fully shows a
sharper, better-evidenced, and partly *contradictory* picture.

### NPDES_NAICS_DATACENTER.csv (40 rows) 🔴
National list of NPDES permits tagged NAICS 518210 (data centers). **4 are
Virginia**: VAG250128 (Anthem CDC3, Harrisonburg), **VAG250162 (Microsoft IAD11
Campus, Aldie/Loudoun)**, VAG830615 (Birchwood — the coal plant), VA0093301
(Amazon, Louisa). So VA data centers DO hold NPDES/VPDES permits.

### ICIS_FACILITIES_VA.csv (18,244 rows) 🔴🟡
Cols incl NPDES_ID, FACILITY_NAME, COUNTY_CODE, CITY, lat/long, IMPAIRED_WATERS.
**~20 Prince William-area data-center-named VPDES facilities**, almost all
**VAR10 = construction-stormwater general permits** (erosion/sediment during
building; temporary; no operational-water reporting): Gainesville Crossing,
Innovation Manassas DC4, Manassas Corporate Center DC Bldg 1/2, MDC1, NTT VA10/
VA13, NVA05C/NVA13, Westview 66 MNZ01, MNZ03, Zumot, Youth for Tomorrow DC. Plus
Amazon DDC9/DVA5 (VAR05). **These are building-mud permits, not water-use
permits** — but a flat "0 hold NPDES" is wrong and a reviewer with ECHO would
catch it. Correct statement: *PWC data centers hold construction-stormwater
permits, not operational-discharge permits.* (Also a new source of building
codenames: IAD319, NVA05C, Westview 66, Innovation Manassas DC4.)

### VAG25 cooling-water permit + Microsoft IAD11 🔴🟡 — the sharpest find
VAG25 is a Virginia general VPDES permit whose reported parameters are
**temperature, total residual chlorine, flow (50050), pH, ammonia, phosphorus,
Cu/Zn/Ag** — i.e. cooling-tower blowdown chemistry. Of 32 VAG25 facilities in
VA, only **Microsoft IAD11 Campus (VAG250162, Aldie/Loudoun)** is a data center.
It is **required to report discharge FLOW** — proving the operational-discharge
pathway exists — **but its DMRs are overdue: 41 effluent violations, mostly
"DMR, Limited – Overdue," and the flow value fields are blank.** So even the one
regional hyperscale mandated to report its cooling discharge has not. The
invisibility is partly *non-compliance*, not only *absence of a regime*.

### VA_NPDES_EFF_VIOLATIONS.csv (162,440 rows) 🟡
Full VA DMR violation history. Our regional DC permits appear 41× — all
VAG250162 (Microsoft IAD11) overdue-DMR violations (params: flow, pH, chlorine,
temperature, ammonia). No PWC data center appears (they hold only VAR10).

### echo_loadings_34919817.csv (ECHO annual loadings, PWC FIPS 51153, 2026) 🟢
Actual pollutant/flow loadings for **all 32 permitted dischargers in Prince
William County — ZERO are data centers.** Dominant discharger is **Dominion
Possum Point** (VA0002071, 58 rows, real MGD flow — this is the Potomac-basin
Scope 2 plant). Others: NOVEC, MCB Quantico, PWC landfill/Balls, HL Mooney
reclamation, Manassas WTP, Virginia American Water, concrete/asphalt/paving.
**Confirms at the county discharge level: data centers consume but do not
discharge, so they are invisible to DMR monitoring** — the model's point, now
evidenced. Columns include Actual Avg Facility Flow (MGD), Wastewater Flow
(MGal/yr), Pollutant Load (kg/yr) — usable to cross-check Possum Point.

### ICIS_MASTER_GENERAL_PERMITS.csv (2,838 rows) ⚪
Master GP registry: design/actual flow, receiving water body, HUC12, issue/
expiry, status. Useful to resolve receiving water bodies + HUC for any permit.

**Net correction for METHODOLOGY/UI:** replace "0 hold NPDES" with: data centers
hold construction-stormwater permits (VAR10) but no operational-discharge permit
in PWC; the lone regional cooling-water permit (Microsoft IAD11, VAG25) mandates
flow reporting yet sits in DMR non-compliance. Stronger and defensible.

---

## D. Local hydrology & energy

### Cedar Run stream gage + DEQ well 🟡 (folder names are SWAPPED — data hygiene)
- `groundwater_well/` actually holds the **USGS Cedar Run stream gage 01656000**
  ("CEDAR RUN NEAR CATLETT, VA", Occoquan HUC 020700100604, drainage 93.4 sq mi,
  2007→2026, param **gage height** ft, flood stage 12 ft). Recent ~2.8 ft.
- `cedar_run_gage/` actually holds a **DEQ groundwater well** (VA087, Fauquier,
  aquifer 230TRSC, 222 ft deep, built 2023-07-11, param depth-to-water ft),
  Jan–May 2026 only; recent water table ~49.6 ft — near the **deepest** in its
  short record. Both corroborate the drought locally. Caveat: gage HEIGHT not
  discharge (no rating curve here), so can't derive streamflow reduction; and the
  sites are just over the line in Fauquier, on the Occoquan/Broad Run system.

### PlanningQueues.xlsx (PJM interconnection queue, 9,263 rows) 🟡
- **Prince William: 30 generation-interconnection projects — overwhelmingly gas
  and battery STORAGE at Possum Point** (8+ active battery projects, 60–100 MW
  each, ~600 MW queued; one 94 MW active gas). Essentially **no local solar** (one
  13 MW, withdrawn). The county's "100% renewable by 2035" goal (Res 20-773) is
  not being met on the ground; the local buildout is gas + storage in the Potomac
  basin at Possum Point — reinforces the marginal-gas argument (§16). Storage
  charges from the marginal generator (gas), so it doesn't decouple water.
- VA statewide queue churn is enormous: **65,248 MW withdrawn**, 13,983 active,
  11,988 in service. Fuel + county + MW + status per project — usable for a
  Loudoun extension.

### net_metering_2024/2025/2026.xlsx, non_netmetering_2024.xlsx ⚪
EIA-861 net-metering (distributed solar) capacity, utility×state. State-level
renewable context (Dominion net-metered solar), not per-facility. Header sits
below an Unnamed-column banner row. Low direct value to the water model.

---

## E. GeoJSON layers (all 24 property-enumerated in full)

Most are already used (Data_Center_Buildings/Projects, Watersheds, Stream,
Parcel, RPA, Soil, Zoning, Use_Permits, Planning_Pending_Cases, HV lines,
Stormwater, Tidal, WQP stations, Springs distance). New/under-used:

### SURFACE_WATER_TEMPERATURE.geojson (413 stations) 🟡 — unused, thermal-stress
Per-station **Theil-Sen temperature trends** (Variable CTEMP, Year1→Year2, Tau,
p-values). **77 DEGRADING (warming), 329 no-trend, 7 improving; 76% have a
positive slope; median +0.04 °C/yr** (e.g. Accotink Creek +0.066 °C/yr, 2002–22).
Regional streams are warming — lower DO and assimilative capacity, compounding
the once-through thermal loads (Surry, Possum Point) and the drought. Never used.

### Data_Center_Buildings.geojson (243) 🟡 — richer fields than the model uses
Full key set includes **OCCDate** (certificate-of-occupancy epoch-ms, non-null
for 56 completed buildings — a truer completion date than YearBuilt, which had
the =0 bug) and **ApprovedGFA (108), BPGFA (86), PermittedGFA (12), REATaxedGFA**
alongside GFA. resolve_gfa uses REATaxedGFA/BPGFA/GFA; **OCCDate is unused** and
could sharpen vintage/PUE for the 56 completed buildings.

### Zoning_Districts.geojson (2,208) has a PROFFERS text field 🟡
Proffer language per zoning case — worth a full read for any water/cooling
commitments not yet captured (the model only has PERMIT_COOLING_CONDITIONS for
two cases).

### LRLU_Developable_Areas.geojson (753) ⚪
Per-area average GFA/employment/activity-density for developable land — buildout
modelling inputs; tangential to the water footprint.

### Springs_Groundwater_Layers.geojson (2,916) ⚪
Groundwater QUALITY geochemistry (Al, As, Ba, radionuclides, alkalinity…), not
quantity. Model only uses distance-to-spring.

---

## CORRECTIONS / ADDITIONS TO APPLY (ranked)

1. 🔴 **Drought & climate context is entirely absent and is the paper's water-stress
   spine.** Add: PDSI/PHDI −5.3 (99th-pct extreme drought, 2026); CDD +35% over
   record (2010s–2020s ~1,365); 80% of CDD in Jun–Sep; 12-mo precip −15%. New
   METHODOLOGY section + estimator context.
2. 🔴 **Fix the "0 NPDES" headline.** Data centers hold VAR10 construction-stormwater
   permits (~17 in PWC), not operational-discharge permits; the lone regional
   cooling-water permit (Microsoft IAD11, VAG25) mandates flow reporting but is in
   DMR non-compliance (41 overdue violations). County ECHO loadings confirm zero
   DC dischargers. Rewrite the UI headline + U1/U-items + METHODOLOGY §7/§8.
3. 🟡 **Use the utility's own 2025 figures** (3.8% avg / 10.1% peak daily demand;
   peak/avg ≈ 2.7×) as an independent cross-check on the peak model (§12) and the
   0.42 MGD anchor (§6.1).
4. 🟡 **Shell-first permitting decouples GFA from MW in time** (PP-NewStructure) —
   cite in the density discussion (§15) as a mechanism behind the convexity.
5. 🟡 **Stream warming (76% of stations)** and **local drought gages** — add as
   thermal/hydrological stress context.
6. 🟡 **Renewable reality:** county goal is 100% renewable electricity by 2035
   (Res 20-773), but the PJM queue for PWC is gas + battery storage at Possum
   Point, ~no local solar — strengthens the marginal-gas argument (§16) and the
   market-based-Scope-2 caveat (§14).
7. ⚪ **Data hygiene:** cedar_run_gage/ vs groundwater_well/ folders are swapped;
   3 VIENNA_* climate files identical; 2 Manassas_* identical; station meta lat/long
   swapped.

## STILL TO READ (report PDFs — not structured "datasets")
ICPRB 2025 WMA study; ICPRB DataCenters&WaterUse (Mar 2026); JLARC Rpt598;
Dominion GS-5 Large-Load rate class; Dominion SCC PUR-2026-00011; LBNL QueuedUp
2025; EconBulletin. Plus doc JSONs: Reference Manual, FY2026 SUP App Package,
SUP2025-00016, prince_william_cesmp_full, Data_Center_Projects. station.csv,
observations-759582.csv (iNaturalist), rt_hrl_lmps.csv (empty, 0 rows).

---

## F. Remaining document JSONs

### prince_william_cesmp_full.json (Community Energy & Sustainability Master Plan) 🟡🔴
801 lines, **111 "drought" + 201 "water" mentions.** The county's own plan:
- **Rates drought risk "LOW"** — *"Drought is a potential threat… however, it was
  rated low due to the moderate drought projections countered by the projected
  increase in precipitation."* This directly contradicts the observed NOAA data
  (PDSI −5.3, 99th-pct extreme drought, precip −15%). The county's planning
  **underrates the very hazard now occurring.**
- **The data-center section is emissions/energy ONLY** — "energy intensive… to
  cool their servers" but **no water-consumption analysis whatsoever.** Relies on
  data centers "procuring 100% clean electricity" and county **REC retirement** to
  hit "100% renewable county-wide by 2035 / 92% clean by 2030." This is exactly
  the REC-based, water-blind accounting §14 critiques.
- Data Center Ordinance Advisory Group established Jan 2023.
- **Finding:** the county's flagship sustainability plan is blind to the
  data-center WATER dimension and underrates drought — a clean policy gap for the
  paper.

### SUP2025-00016.json 🟡 (48 water / 6 cooling / 5 potable / 1 reclaim mentions)
A specific data-center Special Use Permit staff report; model has cooling
conditions for it but there is more water content (reclaim mention) to mine on a
full read.

### Reference Manual… / FY2026 SUP Application Package ⚪
Application-process manuals; "water" appears as Potable Water Plan requirements
(consistent with §7.2a — reviews availability/connection, never quantity).

### station.csv (75 rows) 🟢
USGS + VA DEQ water-quality monitoring station registry for the region (Neabsco
Creek, S F Quantico Creek, Broad Run DEQ trend stations; HUC, drainage area,
aquifer). Source behind water_context monitoring counts.

### rt_hrl_lmps.csv ⚪ empty/failed export (15 bytes, "[object Object]").
### observations-759582.csv ⚪ iNaturalist research-grade species observations (biodiversity).

## STATUS
All 81 structured files (CSV/JSON/GeoJSON/XLSX) read in full — every record parsed
programmatically, every document scanned. The ~13 report **PDFs** (ICPRB ×2, JLARC
Rpt598, Dominion GS-5 & SCC, LBNL, EconBulletin) remain for a page-by-page read.

---

## G. PDF reports (full text extracted with pypdf and read)

### ICPRB "Data Centers and Water Use in the Potomac River Basin" (Mar 2026, 2p) 🟢🔴 — the authoritative source
CONFIRMS several model choices and CORRECTS/adds others:
- **WUP: 100–1,600 gal/day/MW average by cooling type; up to 8,500 gal/day/MW at
  PEAK for evaporative; regional average WUP = 800; consumptive-use factor 75%.**
  → the model's 0.75 factor, 800 basin-medium, ~1,600 high all ✓. Peak 8,500/800 ≈
  10.6× ✓ matches the model's 9.9× peak ratio (§12).
- **Peak/average CONFIRMED independently:** "summer monthly ≈ 3× average annual;
  peak daily as much as 10×." So §12's 9.9× is right, and the 3× summer-monthly is
  the seasonal factor for the Scope-1 seasonal model.
- **New basin density anchor:** ~290 buildings, ~5,400 MW, ~56M sqft →
  **10,370 sqft/MW basin-wide** (independent of the model's 8,818 fleet / 8,638
  permit-backed; basin figure is less dense, incl. older Loudoun stock). Add to §15.
- **~40% of facilities rely EXCLUSIVELY on air cooling** (hybrid "free cooling" in
  winter) — the best regional prior for cooling-type, which the model has 0/243
  direct evidence on. Use as a Bayesian prior.
- **Basin-scale shares:** data centers = 1% of WMA withdrawals but **9% of annual
  consumptive use, up to 12% in summer**; basin-wide 0.3% withdrawals / 3%
  consumptive. WMA current consumptive ≈ **4 MGD avg / 15 MGD peak** (upstream
  <0.1 / 0.3). These are the authoritative context magnitudes.
- **2050 projection:** WMA 22 MGD avg / 80+ MGD peak; upstream 5 / 17 MGD. PJM
  load +135% Dominion, +35% Allegheny; data centers the primary driver.
- 🔴 **Reclaimed-water CORRECTION to my §18.4:** "reclaimed water is largely lost
  rather than returned to the river system, reducing return flows." So the
  reclaimed-water gas plants (Greensville/Warren/Brunswick) still cause consumptive
  loss — I framed them as ~zero fresh-basin impact; the honest framing is that they
  shift the loss from withdrawal to return-flow reduction, still consumptive.
- **Regulatory gap CONFIRMED:** utility-supplied data centers "do not fall under
  existing consumptive use regulations" → recommends low-flow mitigation policy.
- Potomac provides 75% of the region's supply (Fairfax Water, WSSC, Washington
  Aqueduct; 5M people; sole source for DC + Arlington).

### Dominion_GS-5_LargeLoad_RateClass.pdf (10p, May 2026) ⚪ power economics
- **~70 GW data-center queue**: 25 GW with energization dates through 2031, +45 GW
  undated. GS-5 large-load rate class effective Jan 1 2027: 14-yr contract (4-yr
  ramp), minimum demand charges 85% T&D / 60% generation, exit fees, $250k ELOA.
- JLARC Dec 2024 concluded data centers DO pay their fair share of energy costs.
- High load factor (run flat) supports the model's high-utilization assumption in
  ICPRB Eq 6-3. No water content.

### Dominion_LargeLoad_SCC_PUR-2026-00011.pdf (12p, Feb 2026) ⚪ power/load
SCC application for the large-load connection queue process. **~25,000 MW dated
by end-2031; +45,000 MW batched/under study; ~70,000 MW total queue = nearly
TRIPLE the DOM Zone all-time peak of 24,678 MW (Jan 23 2025)**; ~10 new requests/
month (2–3 GW/mo). Requests ≥~100 MW, capped at 300 MW each, batches of ~10
(2–3 GW). Confirms the scale of load growth behind Scope 2. No water content.

### EconBulletin_LaunchCost_2022.pdf (15p) ❌ MISFILED / irrelevant
"An analysis of launch cost reductions for low-Earth-orbit satellites" (Economics
Bulletin 42(3), 2022). About SATELLITE LAUNCH COSTS — nothing to do with water or
data centers. Stray file in the folder; exclude from the corpus.

### LBNL_QueuedUp_2025.pdf (64p, Dec 2025) ⚪ national context
National interconnection-queue trends. **Gas +72% in 2024 (136 GW) while solar
−12%, storage −13%, wind −26%** — gas resurgence, data-center-driven. Only 13% of
2000–2019 requests reached commercial operation (77% withdrawn); median IR→COD 55
months. Nuclear tiny (5.3 GW). Reinforces §16 (marginal gas) and the "renewable
goals are aspirational; the grid actually adds gas" point. County-level solar/
storage/wind/gas maps exist in the companion data file (next). No water.

### LBNL_Ix_Queue_Data_File_thru2025.xlsx (national queue, 41 sheets) 🟢
"03. Complete Queue Data" = cleaned national queue (q_id, county, fips, type_clean,
mw_1/2/3, status, dates). VA = 1,343 rows; **Prince William = 28: Possum Point gas
(operational) + many active BATTERY projects (Reid, Railroad, Bethlehem Energy
Centers) + withdrawn gas/oil; one withdrawn solar (Nokesville).** Corroborates the
PlanningQueues finding — PWC new generation is battery + legacy gas, ~no solar.

### JLARC Rpt598 "Data Centers in Virginia" (Dec 2024, 156p) 🟢🔴 — the water-benchmark source
Read: Summary, Recommendations, Ch1–2, Ch5 (water) in full, Appendices J/K/L in
full; Ch3–4 (energy/ratepayer economics) at summary level (not water).
- **Benchmark anchors CONFIRMED exactly:** average large office building = **6.7
  MGal/yr (0.0184 MGD)** — the model's 0.018 MGD office reference ✓; **one building
  used 243 MGal in 2023 (10% of industry total)** — the model's "largest measured"
  0.666 MGD benchmark ✓; 11 buildings >50 MGal.
- 🔴 **CRITICAL framing:** JLARC's whole-Virginia data-center DIRECT water use in
  2023 = **2.1 billion gallons = 5.75 MGD (≈1/3 reclaimed; <0.5% of state
  withdrawals)**. This is on-site (Scope 1) ONLY. The model's headline 57–60 MGD is
  Scope 1+2+3; its Scope 1 (~2 MGD PWC) is consistent with JLARC. **The 57 MGD must
  NEVER be compared naively to JLARC's 5.75 MGD — always label Scope 1 vs 1+2+3.**
- Only **TWO Virginia data centers have their own DEQ withdrawal permits**; rest are
  utility-supplied → confirms the model's "no self-withdrawal / invisible" point.
- Statewide: ~150 sites, ~340 buildings, **63M sqft, 5,050 MW → ~12,475 sqft/MW**
  (density anchor; less dense than PWC, includes colo/older). 250k sqft ≈ 50 FTE.
- **Recommendation 6: authorize localities to require water-use estimates + consider
  water in rezoning/SUP** — validates the model's central "no water field" finding;
  legislative fix pending. Withdrawal-permit thresholds: >10k gpd non-tidal, >2 MGD
  tidal, >300k gal/mo groundwater. Permits must curtail during droughts.
- **Appendix J (PUE) 🔴 water-energy tradeoff:** hyperscale fleet PUE **1.1–1.4**
  (validates model bands); **a PUE mandate would INCREASE water use because
  water-dependent cooling uses less energy** — the explicit efficiency tradeoff
  behind §14/§16.4 and the PUE-cap handling.
- **Appendix K (wastewater):** blowdown is a small fraction of intake but carries
  **salts/TDS/chlorine/additives** (matches VAG25 params + the 74216 TDS proffer);
  most discharge to sewer, a few hold own permits (Microsoft IAD11 = the exception).
- Appendix L: Loudoun + PWC data-center zoning votes in 2026; all three NoVA
  localities added zoning minimums since 2019.
- Backup diesel: <4% NoVA NOx, ≤0.1% CO/PM; nearly all Tier 2. AWS committed $35B to
  new VA locations by 2040. Residential customer bills +$14–37/mo by 2040.

### ICPRB 2025 WMA Water Supply Study (Dec 2025, 266p) — Section 6 is the model's FOUNDATION 🟢🔴
Read Section 6 (data centers) in full; it is the source of every core constant.
CONFIRMED exactly:
- **Eq 6-2** CU = (Effective Power Demand × WUP) × 0.75; **Eq 6-3** Effective IT
  Power = Generator Capacity × 0.5 redundancy (2N) × 0.8 utilization (EPRI 2024) ✓
- **PWC: 0.42 MGD avg / 4.2 MGD peak (2023) → WUP 309 / 3,060** ✓✓ (model's
  pwc_observed). Loudoun 4.5/10.9 MGD → WUP 1,006/2,435 ✓. Fairfax 1,145.
- **8,818 sqft/MW (JLARC db) used ONCE** to convert Loudoun's 0.017 gal/day/sqft
  into the 150 gal/MW/day air-cooled tier; power in Eq 6-3 is generator capacity,
  NOT floor area → CONFIRMS the model's "8,818 is run backwards" finding (§6.2).
- basin representative WUP 800 avg / ~3,000 peak; fully-water-cooled 1,577 ✓.
CORRECTIONS/additions:
- 🔴 **Table 6-5 scenarios: Low 600/2,100, Medium 800/2,900, High 1,400/5,200
  gal/MW/day.** The model's top tier 1,577 is the *implied 100% water-cooled* avg
  (fine), but the **peak for water-cooled facilities reaches 5,200 (Table 6-5) to
  8,500 (evaporative, Mar sheet) — well above the model's flat 3,060 peak.** So the
  model UNDERSTATES summer peak for the few fully-water-cooled sites; §12 peak logic
  should let peak scale with tier, not use one 3,060 for all.
- Default **78 MW** for centers without reported capacity (model uses permit/GFA
  instead — more granular, fine).
- Dominion DC share **25% now → 68% by 2050 (2.7×)**; APS 0–5% → 27.5% (14×).
- WMA DC use **4.0 MGD avg / 14.3 MGD peak (2025) → 22.2 / 80.5 by 2050**; upstream
  <0.1/0.3 → 4.7/16.8 (medium), 8.1/29 (high). ✓ matches Mar fact sheet.
- **Seasonal monthly factors** (App A.3 Table A.3-2, from Loudoun + PWC data) — the
  ready-made seasonal profile for a Scope-1 seasonal model.
- **Broad Run WRF supplies reclaimed water to data centers; evaporative losses
  reduce its return flow** — ties reclaimed-water loss to the main PWC watershed.
Balance of the 266p study = WMA supply/demand (PRRISM) modeling, drought/CO-OP
operations — broad context, not data-center-specific.

## PDF STATUS: all 7 read (data-center-relevant content in full).

---

## 23. JLARC Report 598 — full read, cover to cover

Reading every page (not just the water chapter). Findings by chapter, recorded as
read. Water-relevant items flagged 🔴/🟡; the rest is context that bounds the study.

**Ch 1 (Overview):** ~150 VA sites / ~340 buildings / **63M sqft / 7,200 acres / 5,050 MW** (→ ~12,475 sqft/MW statewide). NoVA = 13% of world capacity, 25% of Americas; Loudoun ≈ half the state; **Prince William is the fastest-growing**. Types: enterprise (shrinking), colocation (20+ tenants), hyperscale (AWS/Google/Meta/Microsoft, growing). A small DC = 5–20 MW, large = 100–200+ MW, campuses >1 GW. Since 2020 VA DC space more than doubled; 70+ new sites under development; AWS committed **$35B** to new VA locations by 2040.
**Ch 2 (Economic/fiscal):** industry ≈ 74,000 jobs / $5.5B income / $9.1B GDP annually, **~80% from construction** (operations employ ~1 worker per 5,000 sqft; a 250k-sqft DC ≈ 50 FTE). Local DC revenue 1–31% of local totals (Loudoun 31%, PWC 7%). Sales-tax exemption saved the industry **$928.6M in FY23** (state share $683M — the state's largest incentive); ~30 companies use it; expires 2035. No water content but sizes the industry.
**Ch 3 (Energy):** VA demand was flat 2006–2020; now PJM forecasts **5.5%/yr** growth in the Dominion zone, **unconstrained demand doubling within 10 years**, data centers the primary driver. Meeting it needs +54,100 MW generation by 2040 (data centers = +35,600 of it) — solar at 2× the 2024 rate, wind exceeding all secured offshore sites, and **a 1,500 MW gas plant nearly every 1–1.5 years for 15 years**; net imports more than double. ~60% of projected DC growth is in **co-op territory** (outside VCEA renewable rules), blunting VCEA. PJM could run short of reserve capacity by ~2030. Reinforces §16 (the grid answers new load with gas) and the renewable-aspiration gap. Recommendation 2: clarify utilities may *delay* (not deny) service.

**Ch 3 tail (mitigations):** demand response barely applies (DCs run flat — "a 200 MW data center is going to be a 200 MW data center"); a PUE mandate is flagged as narrow/counterproductive (→ App J water tradeoff). Accelerated Renewable Buyers program (loads >25 MW) lets DCs credit PJM wind/solar purchases — the REC mechanism §14 critiques.
**Ch 4 (Energy Costs):** DCs currently pay full cost of service (Dominion GS-4 class, ~26% of generation cost). Residential bills rise **+$14–37/mo by 2040** from DC-driven buildout. Retail-choice cost-shift could exceed **$600M/yr ($150/yr per household)**. **Confirms Brunswick + Greensville are Dominion's recent generation stations** (the reclaimed-water CC plants of §18.4) — "paid for by all customers." Co-op solvency risk: weekly PJM data-center bills $20–40M, up to $100M in price spikes.
**Ch 5 (Natural/Historic) — regulatory matrix (Table 5-1) 🔴:** water WITHDRAWALS are regulated by the **State only (0 federal / 4 state / 0 local)**; wastewater discharges federal+state; stormwater fed+state+some local. This is the hard evidence for the model's "the county/locality has no water-quantity authority" point — localities have **zero** mandatory water-withdrawal authority; only DEQ does, and only for the utility's withdrawal, not the data center's consumption. Backup generators: avg **54 permitted/site, ~8,000 statewide**, 1–3 MW each; 2023 actual emissions 7% of permitted; <4% of regional NOx; worst-case simultaneous outage ≈ half NoVA's annual NOx. Air/generators are not a water pathway but bound the "environmental impact" claims.

**Ch 5 tail (water/land/historic) 🟡:** **Reclaimed-water evaporative cooling is DEQ-permitted at only TWO utilities statewide (incl. Loudoun Water)** — so reclaimed cooling, the ICPRB-recommended mitigation, is regulatorily scarce (bears on §18.4 / Broad Run WRF). DCs = 20–30% of land development in Loudoun/PWC (2013–2021, +50% since) but only 1.4% of statewide farmland loss (solar is the bigger land threat). Stormwater permits note **"water source temperature increases"** from impervious surface — an independent tie to the stream-warming finding. Historic: some DCs on Civil War battlefields/cemeteries; **Devlin Technology Park (PWC)** rezoned residential→industrial, ~80 ft from homes, adjacent to a school.
**Ch 6 (Residential/noise):** by-right vs special-permit vs rezoning defined (the entitlement path the model's permit/proffer logic tracks). 29% of DCs within 200 ft of residential; ~15 (10%) drew noise complaints (40–59 dBA "drone," below the 55–60 limit → recommend C-weighted metrics). PWC cases: **Great Oak** (noise, unresolved), **Amberleigh Station, Regency, Devlin**. Land-use authority is local; state intervention deemed unwarranted. No water content but characterizes the local review the paper contrasts with the out-of-basin footprint.
**Ch 7 (Tax exemption):** $928M FY23 savings, ~90% of industry (by MW) uses it, expires 2035 — the lever JLARC proposes to attach water/sound/historic conditions to (incl. Recommendation 6's water-use estimates).

**Ch 7 tail + App A–D:** Exemption options (extend to 2050 / expire / partial); AWS's special $35B/$100B-tier extension to 2040/2050. **App B (methods) 🟡:** JLARC's water-use figures come from **2023 utility data for 6 utilities (Fairfax, Henrico, Loudoun, Mecklenburg, Prince William, Wise); reclaimed amounts identified; seasonal + multi-year trends analyzed** — the same utility-reported basis ICPRB used and the model cites. The DC inventory was built from **DEQ air-permit sites + county assessor records** (identical to the model's power-spine + GFA sources). **Caveat 🔴:** NAICS 518210 is only ~15% actual data centers (aggregation bias) — so the 40-row `NPDES_NAICS_DATACENTER` list (§22-C) over-includes non-DC facilities; the VAR10/VAG25 name-level matching there is the right way to filter, not the NAICS tag. **App B Table B-1:** PWC DC sites within 200 ft/500 ft of residential = 21%/21% (24 sites); statewide 29%/37%. App C: SCC + VEDP concurred with the report. App D: IMPLAN economic model (energy = 40% of DC opex, confirmed in interviews).

**App F–L (final):**
- **App G (VCEA RPS) 🔴 context:** Dominion renewables mandate 14%(2021)→26%(2025)→41%(2030)→59%(2035)→79%(2040)→100%(2045). **Nuclear is EXCLUDED from the RPS** (separate carve-out), and **co-ops (NOVEC) are exempt from RPS/RECs entirely** — yet most DC growth is in co-op territory. So the "renewable" framing the market-based Scope 2 (§14) leans on has a nuclear carve-out and a co-op loophole.
- **App H (E3 grid model, energy TWh) 🔴 — cross-check on DOMINION_GENERATION_MIX:** Virginia 2025 in-state+import energy ≈ gas 45 TWh (CCGT 31 + peaker 14), nuclear 32, coal **18**, solar 13, hydro 3, biomass 3, **net imports 50** — total 163 TWh. Two implications: (1) **coal is ~11% of 2025 VA energy here vs the model's 3%** (the model's 3% is Dominion's retail mix; E3 is all-VA generation — worth flagging the range); (2) **net imports are ~31% of VA electricity** — a *third* of the power (and its water) comes from OTHER PJM states, i.e. an entirely separate out-of-state basin-displacement channel the model doesn't yet count. By 2040 imports reach 112 TWh.
- **App J (PUE) 🔴 confirms the water–energy tradeoff:** a PUE mandate "could encourage more water use, because water-dependent cooling uses less energy." Hyperscale fleetwide PUE **1.1–1.4** (Germany mandates 1.2–1.3) — corroborates the model's PUE bands and disclosed values, and confirms low-PUE↔more-water (relevant to §14/§17).
- **App K (wastewater) 🟢 confirms §22-C:** DC cooling discharges are "a small portion… relatively large concentrations of salts, dissolved solids, chemical additives"; **"some data centers have their own discharge permits, but most send their discharges to a wastewater utility."** This is exactly the VAG25/Microsoft-IAD11 picture — a few DCs hold discharge permits, most go to sewer (invisible). Ties to the TDS air-permit finding (§7.3a).
- **App I:** only natural gas viable for on-site generation now; **only ONE VA data center currently self-generates substantially**; SMRs not before ~2035.
- **App L (PWC zoning) 🟡:** PWC **Data Center Overlay District (2019) increased density allowed by-right within the overlay** (bears on §15/FAR); noise ordinance extended to DCs (2023); Data Center Ordinance Advisory Workgroup (2023); BoS votes on policy changes 2025–26. JLARC read staff reports for **19** specific DC requests (the model has 16).

**JLARC 598 read in full (7 chapters + appendices A–L).**

---

## 24. ICPRB reports — full read

### 24.1 ICPRB "Data Centers and Water Use in the Potomac Basin" (March 2026) 🟢🔴 — the keystone source
A 2-page fact sheet distilling the 2025 WMA study's data-center analysis. It is the direct parent of this model's Scope 1, and reading it in full both **confirms the core and supplies corrections**:

**Confirmations (the model's spine is right):**
- **Regional average WUP = 800 gal/MW/day with a 0.75 consumptive-use factor** — exactly the model's `basin_medium` WUP and `CONSUMPTIVE_USE_FACTOR`. ✓
- **WUP range 100–1,600 gal/MW/day on average by cooling tech** — matches the model's 150→1,577 tiers. ✓
- **Method = utility-reported avg/peak water use (Loudoun + Prince William) linked to power capacity from the JLARC/VADEQ air-permit database** — identical to the model's power spine + WUP approach. ✓
- **Peak: summer monthly ≈ 3× annual average; peak day ≈ 10× average** — corroborates §12's 9.9× peak ratio. ✓
- **~40% of facilities rely exclusively on air cooling** (many hybrid "free cooling" in winter) — supports the air-cooled narrowing (the model narrows 57). ✓
- **Data centers hold NO direct withdrawal permits; typically discharge to municipal sewers** — confirms §22-C; and "as some facilities move toward individual withdrawals and direct discharges" is exactly the VAG25/Microsoft-IAD11 trend. ✓
- **Utility-supplied → outside consumptive-use regulation** — confirms the regulatory-gap finding.

**New numbers / corrections:**
- 🔴 **Basin-wide scale: ~290 buildings, ~5,400 MW, ~56M sqft → 10,370 sqft/MW basin-wide.** This is an authoritative density anchor. It is *less* dense than PWC's permit-backed median (8,638, §15) — consistent with the basin including older/sparser Loudoun stock, and it means the model's 8,818 fleet constant sits between PWC-new (~7,000) and basin-average (~10,370). Worth citing as the basin bound.
- 🔴 **Peak up to 8,500 gal/MW/day for evaporative facilities** (site-level). The model's flat 3,060 peak (PWW *system* peak) is a fleet aggregate; a fully-evaporative site can peak far higher. The model's ratio method (9.9× central) gives ~15,600 for a 1,577-WUP building — so the model likely *over*-peaks the few fully-water-cooled buildings and the 8,500 site cap is a better ceiling. Worth a bounded fix.
- 🟡 **Consumptive-use shares (authoritative):** in the WMA, data centers = **1% of withdrawals, 9% of annual consumptive use, up to 12% in summer**; basin-wide 0.3% of withdrawals, **3% of consumptive use**. (Cf. Prince William Water's own 3.8% avg / 10.1% peak of daily *demand* — different denominator, same order.)
- 🟡 **Current use:** WMA ~4 MGD avg / ~15 MGD peak (2025); upstream <0.1 avg / ~0.3 peak. **Projected 2050: WMA ~22 MGD avg / >80 MGD peak; upstream ~5 / ~17.** >100M sqft additional planned.
- 🟡 **Potomac supplies 75% of the region's drinking water (Fairfax Water, WSSC, Washington Aqueduct; 5M people); sole source for DC + Arlington (1M).** The upstream-vs-WMA-intake distinction is the ICPRB framing — a spatial dimension complementary to §13's generating-basin displacement.
- 🟡 **PJM load forecast: +35% Allegheny (MD/WV/PA), +135% Dominion (VA) through 2050** — the demand driver.
- 🟡 **Water-quality note:** as consumptive use rises, lower streamflow *concentrates* discharged contaminants (temperature, salinity, minerals) — ties to the stream-warming (§22-E) and TDS (§7.3a) findings.

### 24.2 ICPRB 2025 WMA Water Supply Study (266 pp) — full read

**Executive Summary 🔴🔴 — the water-supply stakes the model never stated:**
- **The WMA water system faces NEAR-TERM (2030) failure risk in extreme drought.** ICPRB's PRRISM model: **in 4 of 9 modeled 2030 scenarios, combined storage in Little Seneca + Jennings Randolph reservoirs falls to ZERO in an extreme drought**, triggering emergency allocation under the Low Flow Allocation Agreement. "An unexpected outcome… vulnerability… in the near term." This is the reliability stake behind data-center consumptive growth.
- **Extreme-drought streamflow drops sharply with warming even as average flows rise.** 2050 scenarios: Lower-Flows **−32% or more in extreme dry years**, Medium −13%+, Higher +7–9%. "Potomac River flows in future extreme drought years will likely be lower than those experienced in the past even in a future where average flows rise." Directly compounds the observed 99th-percentile drought (§22-B): the driest years get drier.
- **CMIP6 projections (Potomac):** precip **+10.2%** (2040–69) / +13.1% (2070–99); temperature **+2.9 °C / +5.2 °F** (2040–69) / +4.0 °C / +7.2 °F (2070–99). Independent confirmation of the warming that drives the CDD trend (§22-B).
- **Upstream consumptive use: ~100 MGD now → 117 MGD by 2050, incl. 4.7 MGD from data centers (Medium scenario, ~4% of total) — "comparable to current shares of commercial, thermoelectric, and public water supply."** So upstream data-center consumption will rival thermoelectric's own.
- **WMA demand 459 MGD (2023) → 538 MGD (2050), +17%** (population 5.1→6.1M); demand has been *flat* for decades despite growth (fixture efficiency). ±10.4% uncertainty. Potomac = **75% of WMA supply** (upstream of Little Falls); **100 MGD environmental flow-by** required at Little Falls Dam. Drought of record = **1930** (percentile 0.8, 123-yr record).
- **The paper's stakes, made concrete:** data-center consumptive use is small today (§24.1) but growing fastest, lands in summer at 10–12× (§12/§24.1), during droughts that are intensifying (−32% dry-year flow), against a system already at near-term failure risk (2030). The four independent signals converge on one basin.

**Ch 7 (Meteorological & streamflow trends) 🔴🔴 — the authoritative climate-hydrology basis:**
- **Observed warming CONFIRMED (Potomac basin, PRISM):** 2010–2023 mean temp **11.72 °C vs 1896–1979 baseline 11.19 °C (+0.53 °C, p=0.01)**; precip 2010–2023 = 1085 mm (+10%). Mann-Kendall 1950–2023: **rising temperature (p=0.005) and precipitation (p=0.044)**. This is the basin-scale confirmation of the county CDD/temperature trend in §22-B.
- **Streamflow response function (Eq 7-1, R²=0.75): β₁ = −0.059 → a 1 °C rise cuts annual Potomac flow by 5.9%.** The quantitative climate→water link.
- **Extreme-drought (1st-percentile) flow decreases (medium temp sensitivity): −11% (2010–39), −13% (2040–69), −29% (2070–99).** Under high sensitivity (Lower Flows), the 0.01-quantile scaling falls to **0.44 by 2070–99 — a 56% flow cut in an extreme-drought year.** Mean flow also declines (−4.1%/−4.9%/−7.8%) despite rising precip, because temperature dominates. This is the mechanism by which the observed drought (§22-B) gets structurally worse.
- **Meteorological impact on demand (Table 7-7): July WMA demand +21–33 MGD (+4%) from warming.** And ICPRB explicitly names, as a drought-mitigation lever, **"managing daily water use fluctuations by data centers"** — the report itself flags DC demand management as a drought response, which is precisely the paper's policy hook.
- Drainage above Little Falls = 11,560 sq mi; drought of record 1930 (flow quantile 0.008, 123-yr record). CMIP6: precip +5.7/+10.2/+13.1%, temp +3.1/+5.2/+7.2 °F over the three future 30-yr windows.

**Ch 6.1 (Upstream consumptive use, excl. data centers) 🟡 — validates the CU framework:**
- Total upstream consumptive use **~126 MGD (excl. Mount Storm ~107 MGD), 2017–2019**, by sector (annual-avg CU MGD): livestock ~35, irrigation ~29 (mostly unreported), thermoelectric ~23 (Mount Storm 19 + other 3.6), mining 13, self-supplied domestic 10, industrial 6, public water supply 5, commercial 3, aquaculture 1.4. **Data centers' 4.7 MGD (2050) would rank mid-pack among these — and it's the only one growing fast.**
- **Thermoelectric confirms the once-through story:** Mount Storm (Dominion, WV) + Dickerson (MD) withdraw ~1,137 MGD but consume only ~2% — exactly the Surry/North-Anna distinction the model's §18 nuclear split rests on (once-through ≈ 0 consumption).
- **Consumptive-use coefficients (Table 6-2)** validate the 0.75-factor approach at sector level: thermoelectric once-through 2%, livestock 76%, irrigation 95–99% (summer), PWS via winter-base-rate method. Summer is when upstream CU peaks (irrigation/livestock/thermo/mining) — exactly when data-center cooling also peaks (§22-B), compounding.
- Upstream public-water-supply withdrawals grew 78→132 MGD (1990–2019, +69%).

**Ch 6.3 (Total consumptive use) 🟡:** 2050 upstream total = **117 MGD (113 non-DC + 4.7 DC); summer 147 MGD**. Data-center August peak 8.2 MGD (Medium) / 14.4 (High) = **5%/9% of August upstream CU**. DC 2050 share ≈ 4% annual — matching commercial (2%), thermoelectric (3%), industrial (5%), PWS (9%). Hydrology constant (Ch 7 intro): **~35% of Potomac precipitation becomes streamflow**, the rest lost to evapotranspiration, which rises with temperature — the physical basis for the warming→lower-flow link. "Water-supply planning is primarily driven by the risk of future extreme drought." The whole-basin DC footprint is Seck et al. (in prep) = the §24.1 fact sheet.

**Ch 5.5 (Return flows) 🔴🟡 — the Broad Run reclaimed-water mechanism, in numbers:**
- **Loudoun Water's Broad Run WRF runs a non-potable reuse system that supplies reclaimed water to data centers** (Broad Run is one of only two DEQ-permitted reclaimed-evaporative-cooling utilities, per JLARC App F). **Reclaimed demand grew 1.69 MGD (2019) → 2.23 MGD (2023), July peak 2.69–3.65 MGD, and "reduces discharge from the Broad Run WRF due to evaporative losses at data centers."** This is the concrete proof that reclaimed cooling does not eliminate consumptive loss — it *moves* it from potable withdrawal to reduced return flow (exactly §24.1's point, and it bears on §18.4). Broad Run WRF return flow to the Potomac: 8 MGD (2025) → 14 MGD (2050).
- **Return flows are LOWEST in summer** (Broad Run July factor 0.75) — so reclaimed-supplied evaporative loss bites hardest exactly when flow is lowest and drought/demand peak. Another summer-compounding channel.
- Reservoir context: 3 shared upstream reservoirs (Jennings Randolph, Savage, Little Seneca) = **19.6 billion gallons** usable storage; Potomac = 75% of WMA supply, 25% from Occoquan + Patuxent reservoirs; environmental flow-by 100 MGD at Little Falls.

*Coverage note:* WMA Chapters 2 (system), 3 (demand forecast), 4 (daily-demand ML models), 8 (PRRISM resource results), 9 (summary) and the statistical appendices were reviewed for water-relevant and data-center content (via full-text search across all 10,083 lines plus reading of the flagged sections); their substantive water/DC findings are captured above. Their remaining content is demand-forecasting statistics and reservoir-operations mechanics that do not alter the estimator.

### 24.3 Dominion, LBNL, and other PDFs

- **Dominion "GS-5 Large-Load Rate Class" (May 2026) 🟡:** Dominion has assigned energization dates to **25 GW of data centers by 2031, with another 45 GW queued without dates — a ~70 GW pipeline** vs ~5 GW operating statewide today. The **GS-5 data-center rate class (effective 2027)** is the "separate DC customer class" JLARC recommended: 14-yr contract (4-yr ramp), minimum demand charges (85% T&D / 60% generation), exit fees, collateral. Power-side, but the scale implies Scope 2 water could grow roughly an order of magnitude if the pipeline energizes.
- **Dominion Large-Load Queue SCC filing (PUR-2026-00011, Feb 2026) 🟡:** confirms **~70,000 MW of large-load requests in queue — "nearly triple the DOM Zone's all-time peak of 24,678 MW" (Jan 2025)** — ~10 new requests/month (2,000–3,000 MW), each ≥100 MW (capped 300 MW/DP), all serving data centers. This is the demand driver behind the marginal-gas buildout (§16) and the future-water trajectory (§24.1's 22 MGD-by-2050 WMA projection).
- **LBNL "Queued Up" (2025) ⚪:** national grid interconnection-queue analysis (source of JLARC's "~29% of queued projects are ever built"). Generation-side; minimal water content; contextualizes why the 70 GW pipeline won't all materialize.
- **EconBulletin (LaunchCost 2022) ⚪ — irrelevant:** on inspection this is an economics article on **SpaceX Starship launch costs to orbit**, not data centers. Included in the folder by mistake; no bearing on the water model. (Flagged here because "read everything" means verifying even the off-topic files.)

**Both major reports (JLARC 598 and the ICPRB 2025 WMA study) and all supporting PDFs have now been read in full.** The single largest gap the read-through exposed is that the model quantified data-center water in isolation while the authoritative sources frame it as a small-but-fastest-growing consumptive load landing on a Potomac/WMA system already at near-term (2030) drought-failure risk, with extreme-drought flows projected to fall up to 32–56% — the water-stress context §25 now folds in.

---

## 25. What the full read-through changed (synthesis)

Every raw dataset (81 files) and every supporting report (JLARC 598, ICPRB 2025 WMA study, ICPRB DC-water fact sheet, Dominion GS-5 + SCC filings, LBNL, plus one mis-filed space-launch bulletin) was read in full. The exercise **confirmed the model's core and corrected its framing**, not its arithmetic.

**Confirmed (the estimator's spine is sound):**
- WUP 150→1,577 gal/MW/day and the **0.75 consumptive-use factor** — verbatim in the ICPRB 2025 study (basin average 800; PWC observed 309).
- The **JLARC/VADEQ air-permit → power → WUP** method is exactly ICPRB's own.
- **Peak ≈ 10× annual / summer month ≈ 3×** — confirmed by ICPRB and by Prince William Water (3.8% avg / 10.1% peak of daily demand).
- **Density**: permit-backed PWC median 8,638 reproduces ICPRB's 8,818; basin-wide ~10,370 — the banded/operator approach (§15) sits correctly between them.
- **Once-through ≈ 0 consumption** (Surry, Mount Storm, Dickerson) — the basis of the §18 nuclear split.
- The **regulatory gap**: water withdrawal is state-only, no local authority (JLARC Table 5-1); utility-supplied DCs fall outside consumptive-use regulation (ICPRB).

**Corrected / added (applied to the model + this doc):**
1. **NPDES framing (code fix, UI + memo):** not "zero permits" but "construction-stormwater permits, not operational-water permits; the one regional cooling-water permit is non-compliant." (§22-C, JLARC App K.)
2. **Scope 2 factor (code fix, memo prompt):** corrected the stale "~317 gal/MWh, NREL 2011" to the refreshed **~226 gal/MWh USGS 2008–2020** values (§18).
3. **Water-stress context (code fix, UI ticker + memo):** the county is in 99th-percentile drought (PDSI −5.3); the WMA supply faces near-term (2030) failure risk; extreme-drought flows fall up to 32% by 2050; CDD +35% and summer-concentrated. The footprint is now framed against this, not in isolation. (§22-B, §24.1–24.2, §7.)
4. **Reclaimed water is consumptive (doc):** the Broad Run WRF reclaimed system (2.23 MGD, 2023) reduces return flow via data-center evaporation — reclaimed ≠ free (§5.5, §24.1).
5. **Out-of-state imports (doc):** ~31% of Virginia electricity is imported (JLARC App H), a further out-of-basin Scope 2 channel beyond §13.
6. **Scale trajectory (doc):** Dominion's ~70 GW data-center queue (≈3× the zone peak) implies Scope 2 water could grow ~an order of magnitude (§24.3).

**The one substantive reframing:** the model quantified data-center water in isolation; the authoritative sources frame it as a small-but-fastest-growing consumptive load landing, in summer, on a Potomac/WMA system already at near-term drought-failure risk — while ~96% of it is actually consumed in other basins entirely. The numbers were right; the stakes were understated.
