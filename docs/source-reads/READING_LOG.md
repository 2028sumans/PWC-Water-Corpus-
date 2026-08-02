# Cover-to-cover source read — all 83 files in data/water_raw

Started 31 Jul 2026. Every prose document read in full, not grepped.
For geospatial files: complete schema + full value distribution of every
attribute field (coordinate arrays are numeric geometry, not text, and are
reported as feature/vertex counts rather than transcribed).

Status legend: [FULL] read every word · [SCHEMA] complete attribute inventory

---

## 1. ICPRB.DataCentersandWaterUse.ICPRB_.March2026.pdf  [FULL] 2 pp / 11,079 chars

**What it is.** ICPRB public fact sheet, published March 2026, drawn from the
2025 WMA Water Supply Study. Authors A. Seck with R. Bourassa, C. Schultz,
M. Nardolilli.

**What I had been using it for:** the single claim that their assessment covers
on-site use only. I had established that by *term absence*. Reading it in full,
the document is a far larger asset than that, and several things in it bear
directly on claims I hedged or got wrong elsewhere.

### Findings I did not have

1. **"The Potomac basin is home to the largest concentration of data centers in
   the world to date."** I had spent a whole exchange hedging the "world's
   largest" claim down to "within the world's largest region" because I could not
   source it. ICPRB states it outright, about the *basin* — which is our host
   basin. Directly citable.

2. **The stakes sentence the paper is missing.** "The Potomac River provides 75%
   of the water supply for the region's three primary utilities (Fairfax Water,
   WSSC Water, and the Washington Aqueduct) supplying 5 million people.
   Furthermore, it is the sole source of drinking water for Washington, D.C., and
   Arlington County, supporting over 1 million residents and critical federal
   services in the National Capital." This is the water-stress overlay for the
   HOST basin, already sourced, no new analysis required.

3. **"These facilities are served by public water suppliers and, to date, hold no
   direct withdrawal permits."** Independent confirmation of the scale-comparison
   framing (METHODOLOGY 56.2) and corroboration of the 235/243 no-NPDES finding.

4. **REGULATORY GAP, in their words:** data centers "are typically supplied by
   public water utilities rather than self-supplied and therefore **do not fall
   under existing consumptive use regulations and mitigation requirements**."
   ICPRB recommends "updating policies to address low-flow mitigation for large
   utility-supplied facilities." This is a sourced regulatory-gap finding and is
   stronger than anything currently in our policy section.

5. **Reclaimed water is not a free fix.** "For evaporative cooling, reclaimed
   water is largely lost rather than returned to the river system, reducing
   return flows. If the reclaimed water is sourced upstream of the WMA intakes,
   this reduction in return flow can affect both water supply availability and
   downstream environmental flow targets." Directly relevant to the B3/reclaimed
   analysis that was downgraded to a literature bound.

6. **Cooling mix:** "about 40%" of facilities "exclusively rely on air cooling",
   many others hybrid with winter free-cooling. An external anchor for the
   cooling-type distribution the harvest never resolved.

7. **WUP range wider than our tiers.** "Nominal site-level water use intensity
   values can range between **100-1,600 gallons/day/MW** on average ... and can
   reach up to **8,500 gallons/day/MW at peak**." Our tiers are 150/309/800/1577
   with a 3,060 peak. Their peak ceiling is 2.8x ours. **Action: check whether
   the peak-day tail is under-represented.**

8. **Their own projections, to benchmark ours against:** WMA ~22 MGD average and
   >80 MGD peak by 2050; upstream ~5 MGD average, ~17 MGD peak. Basin currently
   >290 buildings, ~5,400 MW, 56 million sq ft; >100 million sq ft more planned.

9. **Growth driver, sourced:** PJM load forecasts to 2050 project +35% for
   Allegheny Power Service (MD/WV/PA) and **+135% for Dominion's service area**.

10. **Circularity confirmed verbatim:** current demand "established using
    utility-reported average and peak water use in the Loudoun Water and Prince
    William Water service areas, which was then linked to facility power
    capacities identified through a database developed by the Virginia Joint
    Legislative Audit and Review Commission (JLARC), using Virginia Department of
    Environmental Quality (VADEQ) air permits." Our inputs and theirs share the
    same JLARC/VADEQ lineage — the independence caveat is real and now quotable.

11. **Peak factors:** "Monthly use in summer can be close to three times the
    average annual demand while peak daily use can be as much as 10 times."

12. **Water-quality forward risk:** as facilities "move toward individual
    withdrawals and direct discharges, potential cumulative impacts related to
    increased temperature, salinity, minerals, and other contaminants of concern
    ... may require further study."

### How it enhances the paper
- Supplies the host-basin stakes (5M people, sole source for DC) that the
  water-stress critique asked for, with zero new analysis.
- Supplies a sourced regulatory gap: these facilities are outside consumptive-use
  regulation because they are utility-supplied.
- Gives an external 2050 benchmark to validate our growth scenarios against.
- Item 7 is an open question against our own WUP tiers and should be checked.

---

## 2. Dominion_LargeLoad_SCC_PUR-2026-00011.pdf  [FULL] 12 pp / 16,539 chars

**What it is.** Dominion's 2 Feb 2026 application to the Virginia SCC for approval
of its large-load connection queue process standards. Filed under directive from
the Nov 25 2025 Final Order in PUR-2025-00058.

### Findings
1. **The load-side queue, which dwarfs our pipeline.** "Approximately **70,000 MW**
   of large-load DP Requests are currently advancing through the Company's queue.
   This level of requested load is **nearly triple the Dominion Zone's current
   all-time peak of 24,678 MW, recorded on January 23, 2025.**" Split: 25,000 MW
   already assigned connection dates through 31 Dec 2031; ~45,000 MW assigned to
   batches and under study. Inflow ~10 new requests/month = 2,000-3,000 MW/month.
   Our county pipeline is ~1,970 MW. This is the zone-wide context we lacked.
2. **The DPE.** DP Requests are "submitted and tracked on the Company's online
   platform, the **Delivery Point Exchange ('DPE')**." This is the concrete home of
   `per_dp_contracted_load` — the acquisition our VOI analysis ranks #1 (-10pp).
   We now have its name, custodian and regulatory docket.
3. **Structural parameters:** Standards apply to loads **>=100 MW**; each DP Request
   **capped at 300 MW**; batches of ~10 requests = 2-3 GW each.
4. **Four stages** (Initiation / Feasibility / Development / Execution) with
   documented gating artifacts: zoning conformance letter, 30% engineering site
   plan, use or exception permit, federal/state/local permitting, 100% grading
   plan, construction one-line diagram.
5. **Energization is a tracked milestone** — Project Execution "encompasses final
   design, construction, and **energization**". Relevant to the completed-vs-
   operating problem (METHODOLOGY 57.1).

### How it enhances the paper
- Gives a zone-scale denominator (70 GW requested vs 24.7 GW historic peak) that
  makes the county number legible.
- Names the dataset and the docket for the #1 policy ask. "Require publication of
  per-DP contracted load from the DPE" is now a specific, addressable request
  rather than a generic call for transparency.

---

## 3. Dominion_GS-5_LargeLoad_RateClass.pdf  [FULL] 10 pp / 22,197 chars

**What it is.** Dominion Energy report, May 2026, on the new GS-5 large-load rate
class and the contracting process for data centers.

### Findings
1. **THE DISCLOSURE FINDING.** The customer's service request "will include
   proposals showing a site plan/building layout, schedule of construction,
   **load information (including a ramp schedule and total site load broken down
   by building, if applicable)**, and meter delivery method."
   **Per-building load is collected. By the utility. Today.** Our evidence ladder
   records tier 2 (stated critical load) as EMPTY because nothing is *published*.
   This changes the claim from "nobody measures this" to "**it is measured
   building by building and withheld**" — a far stronger policy statement, and it
   is Dominion's own description of its process.
2. **GS-5 rate class** approved by the SCC, effective **1 Jan 2027**. 14-year
   contract term (incl. 4-year ramp). Minimum demand charges at **85% of
   contracted demand** for transmission/distribution and **60%** for generation.
   Exit fees equal to minimum demand charges over the unexpired term.
3. **Capacity reassignment:** may reduce contracted demand 20% with 36 months'
   notice without exit fees, up to 50% if reallocatable. A quantified measure of
   how much headroom sits between contracted and actual load.
4. **Contracting chain:** ELOA ($250,000 at signing) -> CLOA (triggers deposits and
   100% cost reimbursement on cancellation) -> ESA (issued within one year of
   energization; collateral due before the meter is set).
5. **JLARC Rpt598 also covers energy cost fairness** — concluded (Dec 2024) that
   data centers do cover their contribution to system costs. We cite the same
   report only for water (p.80). Worth knowing it is a dual-purpose source.

### How it enhances the paper
- Converts the central disclosure argument from an absence to a **withholding**.
  That is the single most useful thing found so far for the policy section.
- The 85%/60% minimum-demand ratios are an empirical anchor on the gap between
  contracted and delivered load — the exact quantity our power model infers.

---

## 4. EconBulletin_LaunchCost_2022.pdf  [FULL] 15 pp / 33,834 chars

**Adilov, Alexander, Cunningham & Albertson (2022), "An analysis of launch cost
reductions for low Earth orbit satellites", Economics Bulletin 42(3):1561-1574.**

Per-kilogram launch costs to low Earth orbit, 2000-2020. Nothing to do with
water, data centers, Virginia, or electricity.

**It is indexed into the RAG corpus** (`build_rag_index.py`, `rag_chunks.json`),
so the assistant can retrieve satellite launch economics when answering questions
about data-center water. **Action: remove from the RAG index.** No effect on any
computed number — nothing in the estimator touches it.

---

## 5. LBNL_QueuedUp_2025.pdf  [FULL] 64 pp / 61,953 chars

**Rand et al., Lawrence Berkeley National Laboratory, December 2025.** Annual
snapshot of GENERATOR interconnection queues through end-2024. 7 ISO/RTOs + 49
non-ISO balancing areas, ~97% of US capacity.

### Findings
1. **The buildout-rate anchor we do not currently use.** "About **19% of projects
   (13% of capacity)** requesting interconnection from 2000-2019 reached commercial
   operations by the end of 2024." Our growth scenarios treat the pipeline as a
   buildout multiplier. This is an empirical completion rate, and it is low.
2. **Lead time is lengthening:** the typical project built in 2024 took **55 months**
   from request to commercial operation, vs 36 months in 2015 and 22 in 2008.
3. **Gas is the growth resource:** gas capacity in queues rose **+72%** in 2024 to
   136 GW, while solar (-12%), storage (-13%) and wind (-26%) all fell. Supports
   the marginal-gas framing forward in time.
4. **PJM active queue: 1,942 requests / 211.5 GW.** US total 2,290 GW active vs
   ~1,320 GW installed.
5. **Documented data gaps that matter to us:** no geospatial (lat/long)
   information in queue data at all; PJM's IA-date field is only **15% populated**,
   the worst of any region; commercial operation date unknown for ~24% of
   operational plants.
6. PJM paused review of new requests until 2026 (from 2022); transition to
   first-ready first-served cluster cycles.

### How it enhances the paper
- Item 1 is the strongest external constraint on our growth scenarios and should
  be used to bound the low case. It argues our full-buildout figure is an upper
  envelope, not a forecast — which we assert but do not currently source.
- **Caution to record:** this is the GENERATOR queue. Dominion's 70 GW (file 2) is
  the LOAD queue. Different processes, different datasets. The paper must not
  conflate them, and `pipeline_triangulation.py` should be checked for this.

---

## 6. 2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.pdf  [reading — 266 pp / 611,569 chars]
### Part 1 of N: front matter + Executive Summary + Ch.1 (through p. 1-2)

**What it is.** ICPRB Report ICP-596, December 2025. Ahmed, Bencala, Nummer,
Schultz & Seck. The **eighth** in a series of five-yearly studies required by the
Low Flow Allocation Agreement and the Water Supply Coordination Agreement.
Planning horizon 2050, extrapolated to 2060 (for Virginia 9VAC25-780) and 2085
(for a USACE secondary-source-backup feasibility study begun Sept 2024).

### THE FINDING THAT ANSWERS "WHY SHOULD ANYONE CARE"

> "An **unexpected outcome** of this study is the indication of **vulnerability of
> the WMA water supply system in the near term** ... Deficits are predicted in the
> event of extreme drought in **2030** for the Medium Flows and High Demands
> scenario and for all the Lower Flows scenarios. **In four out of nine of the
> modeled 2030 scenarios, combined water supply storage in Little Seneca and
> Jennings Randolph reservoirs is predicted to fall to zero** in the event of
> extreme drought, which would likely trigger emergency water allocations under
> the Low Flow Allocation Agreement."

The host basin — the Potomac, which our paper says average accounting exports 43%
of the burden *out of* — is projected by its own regional authority to **fail in
4 of 9 scenarios by 2030**, not 2050. And CO-OP entered the WSCA expressly to
"reduce or eliminate the possibility that the Emergency Stage of the LFAA will
ever be reached."

This is the water-stress overlay for the host basin, sourced, quantified, and
near-term. No new analysis required.

### Other findings

1. **A scope trap in comparing our numbers to theirs.** "Data center water use
   estimates ... **reflect only data centers located upstream of the WMA**."
   Prince William is served by Prince William Water, a Fairfax Water wholesale
   customer — i.e. **within** the WMA, not upstream. So ICPRB's headline
   data-center figures (4.7 MGD in 2050 upstream) **exclude most of our fleet**.
   Any comparison of our county total to their basin total must respect this.
   **Action: check that growth_scenarios.py's ICPRB cross-check is comparing
   like with like.**
2. **Upstream consumptive use:** ~100 MGD today, data centers <0.1% of it.
   Forecast 117 MGD in 2050 including **4.7 MGD from data centers** (Medium
   scenario) = ~4% of the total. "Comparable to the current upstream consumptive
   use shares of several established sectors, including commercial,
   thermoelectric, and public water supply."
3. **WMA demand is flat despite population growth.** Population 3.4M -> 5.0M
   (1990-2023, +47%) with "no clear trend" in annual, summer or peak-day
   production. Forecast 459 MGD (2023) -> 538 MGD (2050), +17%, uncertainty
   **±10.4% (one standard error)**. Useful precedent: their headline forecast
   carries a ±10% band; ours carries ±19% at 90%.
4. **They admit systematic over-prediction:** "Past studies by ICPRB have
   consistently over-predicted overall water demand."
5. **Climate inputs (NASA NEX-DCP30-CMIP6):** precipitation +10.2% (2040-69),
   +13.1% (2070-99); temperature +2.9 C / 5.2 F (2040-69), +4.0 C / 7.2 F
   (2070-99). Lower Flows scenario: **32% or greater decrease in extreme dry
   years** by 2050.
6. **Drought of record** is 1930, at percentile ~0.8 of the 123-year record. The
   binding constraint is the **100 MGD environmental flow-by at Little Falls Dam**.
7. **They evaluated ML for daily demand** (Ch. 4): neural nets, LSTM, GRU,
   XGBoost. "The machine learning models demonstrated improved accuracy in
   capturing nonlinear behavior, peak demands, and weather sensitivity" but the
   linear regression in PRRISM "remains effective." Directly comparable to our
   own LOO bake-off finding that trees lose at n=14 — different n, same question.
8. **Planned new resources:** Vulcan Quarry / Edgemon Reservoir (Fairfax Water,
   assumed operational 2040); Luck Stone Quarry A / Milestone Reservoir (Loudoun
   Water, 2028); Beaverdam Reservoir (Loudoun emergency supply).
9. **Acknowledgements confirm the data lineage:** David Guerra and Nathan Griffin
   of Prince William Water; Frank Hunt of Prince William County; **Scarlett
   Saunders of JLARC**; Weedon Cloe of VADEQ.

### How it enhances the paper
- Item "THE FINDING" gives the paper its stakes, in the host basin, from the
  regional authority, with a 2030 horizon. This is stronger and cheaper than the
  proposed water-stress overlay, and it is about the basin our accounting result
  actually concerns.
- Item 1 is a **correction risk** to check in our own code before publication.

### Part 2: Ch.1 (Introduction) + Ch.2 (System Overview) + Ch.3 start — lines 1158-2095

**Host-basin stress numbers, from the authority, for the basin our result concerns**

1. **"While withdrawals typically account for about five percent of the adjusted
   flow, they can surpass 50 percent during dry periods."** That is the stress
   metric for the Potomac, in ICPRB's words.
2. **Minimum recorded daily adjusted flow at Little Falls:** 505 MGD (1930),
   **388 MGD (1966, record low)**, 704 MGD (1999), 1,222 MGD (2002). Days at
   record-low flow: 41 / 110 / 17 / 42 respectively. Mean adjusted flow
   1930-2023 is **7.7 BGD (SD 4.0)** — so the record low is ~5% of the mean.
3. **The binding constraint:** 100 MGD environmental flow-by at Little Falls Dam
   (155 cfs daily average). Watershed to Little Falls = 11,560 sq mi, USGS gage
   01646500 (adjusted flow 01646502).
4. **Shared drought storage is 19.6 BG total:** Jennings Randolph 29.4 BG usable
   of which **13.1 BG is the CO-OP water-supply account** (200 miles upstream,
   >1 week travel time), Little Seneca 3.9 BG (~1 day travel), Savage ~6.3 BG.
   Releases have been needed three times ever: **1999, 2002, 2010**.

**The peak-factor contrast that makes our seasonal finding land**

| System | Peak-day / annual-average factor |
|---|---|
| WSSC Water | 1.6 |
| Washington Aqueduct | 1.7 |
| Fairfax Water | 1.9 |
| Combined CO-OP | 1.6 (Potomac 1.8) |
| Loudoun Water | 1.5 |
| **Data centers (ICPRB fact sheet)** | **~10** |
| **Our estimate (harness check 14)** | **9.9** |

Municipal demand peaks at ~1.6-1.9x annual average. Data centers peak at ~10x.
**Data-center demand is roughly six times peakier than the municipal demand the
system was engineered around** — and it peaks in the same months when flows are
lowest. Our own 9.9x reproduces ICPRB's ~10x independently. This is a cleaner
way to state the seasonal finding than the Broad Run ratio ever was, and it does
not require a scale-comparison caveat.

**Our county, in their system**

- Prince William Water is a **wholesale customer of Fairfax Water**, supplied
  from the **Occoquan Reservoir** via the Griffith WTP (8.2 BG usable, 592 sq mi
  drainage, 120 MGD plant capacity). Confirms host basin = Potomac and confirms
  our buildings sit **within the WMA**, not upstream — the scope trap flagged in
  Part 1.
- **Prince William Water demographics (MWCOG Round 10.0):** population 374,500
  (2020) -> 453,500 (2050) -> 493,067 (2085); households 121,600 -> 152,900;
  employees 129,200 -> 202,900 -> 271,700.
- CO-OP production 2019-2023 averaged **445 MGD** (WA 133 / FW 151 / WSSC 161);
  Potomac-sourced portion 331 MGD. Summer 501 MGD (+13%); peak day 630 MGD (2020).
  Fairfax Water draws **41%** of its supply from the Occoquan.

**Planned supply additions (the denominator for any "can the system absorb it"
argument)**

- **Milestone Reservoir** (Loudoun Water), 1.25 BG, by **2028**.
- **Edgemon Reservoir** (Fairfax Water), 1.7 BG by **2040**, 15 BG by 2085.
  Critically: without Griffith WTP upgrades (120 -> 160 MGD), the 2017
  alternatives study puts Edgemon Phase 1's regional benefit at only **5 MGD**,
  versus 25 MGD with upgrades. **The current study assumes no upgrades.**
  So the region is adding ~5 MGD of effective safe yield by 2040 while our
  county's data-center fleet alone is estimated at 10.4 MGD today.

### How it enhances the paper
- The peak-factor table (1.6-1.9 vs ~10) is the strongest, simplest framing of
  the seasonal result I have seen, and both numbers are externally sourced.
- The 5 MGD of new safe yield by 2040 against a 10.4 MGD existing fleet is a
  concrete supply-side counterpoint that needs no modelling.

### Part 3: Ch.3 (Annual Demand Forecast) + Ch.4 start — lines 2095-3262

**THE COMPARISON THE PAPER HAS BEEN MISSING**

ICPRB publishes a demand forecast for **Prince William Water specifically**
(Table 3-15): **26.8 MGD (2023) -> 32.3 MGD (2050) -> 37.9 MGD (2085)**. That is
the entire municipal water demand of our county's utility — every household,
every business, plus unmetered losses.

Against our own numbers for the same county:

| Our estimate | MGD | vs PWW municipal demand |
|---|---|---|
| On-site (Scope 1), 54 completed | 0.33 | **1.2%** of PWW 2023 |
| On-site (Scope 1), all 243 | 1.76 | **5.5%** of PWW 2050 |
| Total footprint, 54 completed | 10.49 | **39%** of PWW 2023 |
| **Total footprint, all 243** | **49.60** | **1.54x PWW's entire 2050 demand** |

**The displacement result in its most legible form:** the water footprint of
Prince William County's approved data centers is roughly **one and a half times
the entire municipal water demand of the county's water utility in 2050** — while
only about **5%** of it ever appears in that utility's system. The rest is at
generating stations, mostly in other basins.

Both numbers now have external denominators: ICPRB forecasts the municipal side;
we estimate the data-center side. No new analysis needed.

**A reconciliation to do carefully before publishing.** ICPRB forecasts ~22 MGD
average on-site consumptive for data centers **in the WMA** by 2050, and 4.7 MGD
**upstream**. Ours is 1.32 MGD consumptive on-site for 243 PWC buildings. These
are not comparable without care: theirs is the whole WMA (Loudoun dominates),
2050, with growth; ours is one county at current approved buildout. **Any table
placing them side by side must state fleet, geography, year and basis.**

**Other findings**

1. **WMA totals for context:** 465.3 MGD (2025) -> 537.9 (2050) -> 641.8 (2085).
   Forecast uncertainty **±8.5% (2025), ±10.4% (2050), ±12.8% (2085)** — a useful
   precedent for how a peer institution reports a forecast interval.
2. **They publish their own track record of failure:** "Past studies by ICPRB have
   consistently over-predicted overall water demand ... systematic errors ...
   associated with the inability of water planners to predict the technological
   and policy changes that have reduced per-household and per-employee water use."
   Worth citing when we say our buildout figure is an envelope, not a forecast.
3. **Efficiency policy is load-bearing and now uncertain:** removing forecast
   savings adds **10.5 MGD (households) + 1.4 MGD (employees)** by 2050. ICPRB
   flags the proposed termination of ENERGY STAR, and notes EPACT 1992's
   anti-backsliding provision would likely require congressional action to undo.
4. **A structural signal worth a sentence:** "For the first time in decades, the
   Washington Business Journal (2025) has reported that **no commercial office
   buildings are under construction anywhere in the WMA**." Data-center
   construction is not displacing ordinary commercial growth — it is replacing it.
5. **Prince William is the region's most single-family jurisdiction** (dwelling
   unit ratio 4.56 in 2020, highest in the WMA, falling to 3.13 by 2050) — i.e.
   the county absorbing the data-center build is also the one with the most
   outdoor summer demand.
6. **PWW unit use (2023):** SFH 168 gpd, MFH 184, employee 37.
7. **Ch.4 confirms the ML comparison:** ICPRB tested FNN, LSTM, GRU, CNN-LSTM,
   Random Forest and XGBoost against multiple linear regression + ARIMA for daily
   demand. Same structural question as our LOO bake-off, at much larger n.

### Part 4: Ch.4 (Modeling Daily Variations) — lines 3262-3681

**OUR SEASONAL DEMAND SHAPE IS NOW EXTERNALLY VALIDATED**

METHODOLOGY 56.3 lists as an open item that "the seasonal demand shape is
MODELLED (CDD-proportional, baseload swept 0.1/0.3/0.5); only the streamflow is
measured." That is no longer unvalidated:

| | July factor (x annual mean) | Peak-day factor |
|---|---|---|
| **Our modelled data-center shape** | **3.04** | **9.9** |
| **ICPRB published** | "close to **three times** the average annual demand" | "as much as **10 times**" |

Two independently constructed estimates of the same shape agree to within a few
percent on both the monthly and the peak-day factor. Ours comes from a
CDD-proportional model fitted to building-derived annual means; theirs from
utility-reported data-center use in the Loudoun Water and Prince William Water
service areas. **This is a genuine out-of-sample check on the one component of
the seasonal analysis I had flagged as unverified.**

**And the contrast with municipal demand is measured on both sides**

ICPRB's Table 4-3 gives monthly production factors from 11 years of daily
production data (2013-2023):

| Month | Fairfax | WSSC | Wash. Aqueduct | Loudoun | **Data centers** |
|---|---|---|---|---|---|
| January | 0.89 | 0.97 | 0.94 | 0.80 | **0.30** |
| July | 1.18 | 1.10 | 1.14 | 1.31 | **3.04** |

Municipal demand swings ~1.3x across the year. Data-center demand swings ~10x,
and peaks in the same month. The paper can now state this with a measured
municipal baseline rather than an assertion.

**Loudoun's growth rate is the data-center signal in municipal data**

Table 4-1, long-term trend in daily production 2013-2023:

| Supplier | Yearly growth rate |
|---|---|
| Loudoun Water | **+2.27%** |
| Fairfax Water | +0.51% |
| WSSC Water | -0.08% |
| Washington Aqueduct | -0.34% |

Every WMA supplier is flat or declining except the one whose service area holds
the world's largest data-center concentration. That is a clean natural
experiment sitting in ICPRB's own table, and neither they nor we have used it.
**Worth a figure.**

**Other methodological detail worth borrowing or citing**

- Demand response to temperature is **piecewise-linear with a breakpoint at 85 F**
  — separate coefficients above and below. Our CDD formulation assumes a single
  slope; theirs is empirically justified and we could adopt it.
- Precipitation is **capped** (0.2 in for WSSC, 0.3 in for the rest) to reflect
  the asymptotic relationship between rainfall and outdoor use.
- Model skill by season (R2): **summer 0.43-0.56**, spring/fall 0.23-0.34,
  **winter 0.06-0.15**. Weather explains little in winter.
- Honest limitation stated: "the regression models do a reasonable job predicting
  intermediate demands but **tend to under-predict the highest demands** and
  over-predict the lowest demands." Their peak-day estimates are conservative.
- ARIMA(2,d,1) on the pooled four-supplier residual; sigma 13.8 full-year, 15.7
  summer.

### Part 5: Ch.4.7-4.8 (Model evaluation + ML bake-off) + Ch.5 start — lines 3681-4100

**ICPRB RAN THE SAME BAKE-OFF WE DID AND GOT THE OPPOSITE ANSWER — BECAUSE OF n**

Their results (train 2013-2021, test 2022-2023, ~3,300 days, full system):

| Model | R2 | RMSE (MGD) |
|---|---|---|
| Feed-forward neural network | **0.894** | **14.06** |
| Bidirectional GRU | 0.889 | 14.20 |
| XGBoost | 0.827 | — |
| Random Forest | 0.827 | — |
| **Multiple linear regression** | **0.821** | **18.23** |
| CNN-LSTM | 0.760 | 20.85 |

Neural nets beat linear regression by 20-25% on RMSE at n ~ 3,300.
**We found the opposite at n = 14** — ridge beat RF (0.1079 vs 0.1551) and GBM
(0.1606), and trees lost outright.

Both results are correct. The difference is sample size, and stating that
explicitly is a stronger methods point than either result alone: the flexible
models are not wrong for water demand — the regional authority shows they win
with three thousand observations. They lose here because fourteen permit sites is
what the public record contains. That reframes our n=14 limitation from an
apology into a quantified statement about what disclosure buys.

**Every model under-predicts peaks — theirs and ours**

All six of their models show negative mean residuals (LR -2.4, XGBoost -1.7,
GRU -1.3, NN -1.0 MGD): "All models showed a tendency toward under-prediction ...
may reflect difficulty in fully capturing high-demand days." Combined with the
regression note in Part 4 ("tend to under-predict the highest demands"), **peak
estimates in this literature are systematically conservative** — including,
probably, the peak WUP figures we borrow from them.

**A clean natural experiment on behaviour vs weather**

The all-time WMA system peak, **642.6 MGD on 20 July 2020 at 99 F**, versus
**604.7 MGD on 25 July 2016 at 100 F** — a hotter day with **38 MGD less demand**.
ICPRB attributes the gap to pandemic work-from-home behaviour and excludes 2020
from evaluation (but keeps it in training). A useful demonstration that demand
models miss behavioural regime shifts — exactly the risk in projecting
data-center load.

**Seasonal skill, all models:** winter is hardest (best R2 0.41; LSTM goes
negative), summer best (GRU 0.745). Winter main breaks distort observed demand,
and temperature drives outdoor use that barely exists in winter.

**System peak-day factor:** actual 1.36; regression reproduces 1.30; ARIMA 1.35-1.36.

**PRRISM v4.1** rewritten in ExtendSim 10, database-driven inputs. Only two new
resources represented: Edgemon (2040) and Milestone (2028). Lake Manassas removed
at Fairfax Water's request. Simulates "cumulative upstream consumptive demands,
**including estimates for data centers**" at a daily time step — data-center
consumption is now an explicit term inside the region's operational planning model.

### Part 6: Ch.5 (System Resources) + Ch.6.1-6.2.2 — lines 4100-5387
### THIS IS THE SECTION EVERY CONSTANT IN OUR ESTIMATOR COMES FROM

**Section 6.2.2 verbatim — the full derivation of our WUP constants**

> "WUP values were derived using actual data center water use (based on utility
> reported data) and power demand (based on JLARC database) for data centers in
> the Loudoun Water, Fairfax Water and Prince William Water service areas ...
> In the Loudoun Water service area, data centers are reported to have used
> **4.5 MGD of water annually and 10.9 MGD on the peak day in 2024**. These
> figures include potable and reclaimed water use. In the Prince William Water
> service area, **0.42 MGD on average and 4.2 MGD for peak day were reported for
> 2023**. For Fairfax County, where direct data was not available, we estimated
> usage at **0.27 MGD** using square footage ... and an assumed usage rate of
> **90 gallons per day per 1,000 square feet** ... These data yielded WUP values
> of **1,145 gallons/day/MW in Fairfax County, 1,006 in Loudoun** for the annual
> average, and **2,435 for peak day**, and **309 for the average and 3,060 for
> peak day in Prince William**."

**A DISCREPANCY IN THE 800 CONSTANT WE USE.** They then write: "**Averaging the
Prince William Water and Loudoun Water service areas values, we estimate a
representative WUP across the basin of about 800 gallons/day/MW** for annual
average and about 3000 gallons/day/MW for peak day."

But the simple average of 309 and 1,006 is **658**, not 800. (The peak figure
does work: (3,060 + 2,435)/2 = 2,748 ~ "about 3000".) So the 800 is either
power-weighted toward Loudoun, or rounded upward, and the report does not say
which. **We ledger 800 as `wup_basin_800` with a verbatim quote, but the
derivation behind that quote does not reproduce.** Action: state in the paper
that the basin-representative WUP is 658 on a simple average and 800 as
published, and treat the gap as a documented uncertainty rather than reproducing
their number without comment.

**Prince William is a factor-of-3 outlier, and now we know exactly why**

| Service area | Annual WUP (gal/day/MW) | Peak WUP |
|---|---|---|
| Fairfax County | 1,145 | — |
| Loudoun Water | 1,006 | 2,435 |
| **Prince William Water** | **309** | **3,060** |

PWC's *annual* intensity is 3-4x lower than its neighbours, but its *peak* is the
**highest in the basin**. Peak-to-average ratio: PWC **9.9x**, Loudoun **2.4x**.
That is the empirical basis for the seasonal finding, and it is ICPRB's own data
— our county runs air-cooled/chiller-dominant most of the year and swings hardest
in summer.

**Other constants confirmed verbatim** (all as ledgered): consumptive use factor
0.75; redundancy 0.5 ("permitted generator capacity typically represents twice
the actual IT power load (i.e., 2N backup systems)"); utilization 0.8 ("based on
industry data (EPRI, 2024)"); Eq 6-2 and Eq 6-3 exactly as we implement them.

**New facts about the underlying dataset**

- The JLARC/VADEQ dataset contains "facility names, operators, addresses,
  locality, total backup generator power capacity, building size, number of
  buildings, and land area" and is public at
  deq.virginia.gov/permits/air/issued-air-permits-for-data-centers.
  **This is the re-download source for the missing `*_DC_Permit.txt` files.**
- "For centers without reported power capacity, we used a default value of
  **78 MW** based on the average in the Virginia dataset." A useful external
  check on our own per-site permit capacities.
- **Growth driver, sourced:** PJM forecasts APS peak load 8,700 -> 11,700 MW
  (+35%) and **Dominion 23,000 -> 54,000 MW (+135%)** between 2025 and 2050.

**Upstream consumptive use context (Ch.6.1) — the denominators**

- Upper Potomac (11,560 sq mi) total withdrawals **2,721.6 MGD**, consumptive use
  **125.8 MGD** annual / 149.5 summer. Excluding Mount Storm: 1,763.4 / 106.6 / 125.1.
- **Hydroelectric withdraws 1,184 MGD and consumes 0.00.** Thermoelectric
  once-through consumes ~**2%** of withdrawal. Removing PP and HYE leaves only
  ~400 MGD of upstream withdrawal.
- Irrigation is **97% consumptive**, livestock **76%** — the sectors that actually
  deplete are small in withdrawal and large in consumption. Exactly the
  withdrawal-vs-consumption distinction our own abstract had to fix.
- Upstream public water supply withdrawals grew **78 MGD (1990) -> 132 MGD (2019),
  +69%**.
- Upstream CU forecast (no data centers): 99.6 (2018) -> 113 (2050) -> 127 (2085)
  annual; summer 122.6 -> 140 -> 159.
- **96% of upper-basin withdrawals are surface water.**

**Reservoir and operations detail that bounds any "can the system absorb it" claim**

- Storage capacities with sedimentation (Table 5-1): Occoquan 8,170 MG (rate 0),
  Patuxent 10,284 -> 9,669 MG by 2050 (24.6 MG/yr), Little Seneca 3,843 -> 3,743,
  Jennings Randolph water supply 12,857 -> 12,356, Savage 5,881 -> 5,431.
- **Griffith WTP (which serves Prince William) is constrained to 45-120 MGD**, max
  change 40 MGD/day. Corbalis 60-225 MGD.
- Restriction triggers: **voluntary at <60% of combined Little Seneca + Jennings
  Randolph storage (5% summer demand cut), emergency at <5% (15% cut)**.
- Reclaimed water at Loudoun's Broad Run WRF rose **1.69 MGD (2019) -> 2.23 MGD
  (2023)**, July peak 2.69-3.65 MGD, and ICPRB notes it "**reduces discharge from
  the Broad Run WRF due to evaporative losses at data centers**" — reclaimed water
  is a return-flow loss, not a free substitution.
- **Environmental flow-by under active review:** ICPRB convened a Potomac River
  Environmental Flow-By Task Force in **June 2025** to decide whether the 1981
  100 MGD recommendation needs replacing. The binding constraint in our stress
  framing may change.

### Part 7: Ch.6.2.2-6.3 — lines 5387-5816
### THE POLICY SECTION OF THE PAPER IS SITTING IN 6.2.4

**ICPRB EXPLICITLY CALLS FOR THE PAPER WE WROTE — AND NAMES NUCLEAR**

Section 6.2.4, "Water-energy nexus", verbatim:

> "Air-cooled systems can reduce direct water use at data centers, but they often
> increase electricity demand. **This added electricity use can raise indirect
> water consumption through thermoelectric generation, including nuclear.** ...
> **To fully understand data center impacts, it is important to consider both
> direct and indirect water use.** Policymakers should evaluate these tradeoffs
> and support the development of cooling technologies that minimize both water
> and energy use under future climate conditions."

The regional authority states that the indirect footprint matters, names the
mechanism, and names nuclear specifically. Our paper is the execution of a
recommendation they published. That is the motivation paragraph, written for us.

**THE REGULATORY GAP, WITH STATUTE NUMBERS**

> "In Virginia, the **Virginia Water Protection Permit program (Va. Code
> § 62.1-44.15:5.02)** requires that non-municipal water users withdrawing more
> than **500,000 gallons per day** for consumptive use from the Potomac River or
> its tributaries (between the West Virginia border and Little Falls) implement
> low-flow protection measures ... These requirements apply to permits issued
> after **July 1, 2007** ...
>
> **Current state regulations often apply only to facilities withdrawing water
> directly from surface- or groundwater sources. In practice, however, data
> centers in the Potomac basin typically obtain water through municipal systems
> rather than direct withdrawals. As a result, data center cooling demand is
> generally met using existing, previously permitted municipal capacity, and the
> state consumptive use regulations do not apply directly to these facilities.**"

Maryland equivalent: **COMAR 26.17.07.02** (low-flow augmentation for
nonresidential consumptive surface withdrawals >1 MGD in the Potomac basin);
**COMAR 26.17.06.06** (MDE may impose minimum flow or curtailment).

Our 235/243 no-NPDES finding now has a named statute, a threshold, a date, and a
stated reason it does not bind. And a policy precedent exists: **New York's
Sustainable Data Centers Act would require operators to disclose projected water
use.**

**ICPRB ADMITS ITS OWN WMA METHOD MAY NOT CAPTURE DATA CENTERS**

> "This study assumes that data center water use within the WMA is implicitly
> captured in the current methodology ... through employee unit use (Chapter 3)
> and return flow assumptions (Chapter 5). However, this assumption may warrant
> re-evaluation ... **projected peak summertime use within the WMA reaches up to
> 140 MGD** based on the PJM energy forecasts. ... **The current methodology may
> not adequately capture the full scale of data center consumptive use within the
> WMA, especially for future years.**"

140 MGD peak summertime, against a CO-OP system whose all-time peak-day
production is 741 MGD. And the region's own demand forecast may not contain it.

**8,818 SQ FT/MW IS NOW SOURCED VERBATIM**

> "Holding the air-cooled WUP constant at 150 gallons/MW/day (value based on an
> estimate of **0.017 gallons/day/square foot**, provided by Loudoun Water and an
> **infrastructure density of 8,818 square feet per MW based on the JLARC
> database**), we calculated the implied WUPs for fully water-cooled systems as
> **1,577 gallons/MW/day** (annual average)."

`sqft_per_effective_mw = 8818` in our code has been unsourced. It is JLARC-derived
and stated here. And the 150 constant reproduces: 0.017 x 8,818 = 149.9.
**Action: add a ledger entry for 8,818 with this quote.**

**ICPRB's own scenario table (Table 6-5)** — our 150/309/800/1577 tiers in context:

| Scenario | Water-cooled share | Avg WUP | Max WUP |
|---|---|---|---|
| Low | 30% | 600 | 2,100 |
| Medium (observed) | ~60-70% | 800 | 2,900 |
| High | 90% | 1,400 | 5,200 |

Note the high-scenario max of **5,200**, not the 8,500 quoted in the fact sheet —
8,500 is the site-level ceiling for evaporative cooling, not a fleet scenario.
**That resolves the open question from file 1: our 3,060 peak is the PWC observed
value and is internally consistent; 8,500 is a per-facility maximum, not a fleet
average.**

**Their forecast, for our comparison table**

| | 2025 | 2050 |
|---|---|---|
| WMA data centers, average | 4.0 MGD | **22.2 MGD** |
| WMA data centers, peak day | 14.3 MGD | **80.5 MGD** |
| Upstream, average (medium) | — | 4.7 MGD |
| Upstream, peak (medium) | — | 16.8 MGD |
| Upstream, high scenario | — | 8.1 / 29 MGD |

Growth driver: **EPRI (2024) puts data centers at 0-5% of APS load and 25% of
Dominion's today**, rising to 27.5% and **68% by 2050** — a 14-fold and 2.7-fold
increase respectively. That is the source of the 25%/68% figures in our
METHODOLOGY.

**Three threats to our own method, stated by them**

1. **Off-grid power.** "as some new data centers explore off-grid energy solutions
   (hydrogen-powered systems, battery-backed microgrids, or on-site natural gas
   generation) traditional grid-based forecasts may not fully reflect future
   energy use ... especially where facilities operate outside of utility reporting
   systems." Our Scope 2 attribution assumes grid supply.
2. **Reclaimed water is not neutral.** "When reclaimed water is withdrawn from a
   treatment plant and used for evaporative cooling, it reduces return flows and
   effectively removes water from the system." Siting option they name: the
   **Noman M. Cole Jr. Pollution Control Plant (~40 MGD, discharges to the
   Occoquan estuary)** — downstream of intakes, so its reclaimed water would not
   reduce supply.
3. **Water quality, and it names our reservoir.** Salts, biocides and corrosion
   inhibitors in cooling-tower blowdown; salt drift onto soils; "salt pollution is
   already a growing issue in many freshwater ecosystems and **in certain water
   supply reservoirs, including the Occoquan**." The Occoquan is Prince William's
   source.

**One more timing detail with teeth:** the current study's 2050 October and
November upstream CU forecasts are **35-40 MGD higher** than the 2020 study's —
"significant because low flows and reservoir releases would occur in October and
November during a future drought resembling the 1930 drought of record."

### Part 8: Ch.7 (Meteorological Change) + Ch.8.1-8.3 — lines 5816-6674

**THE SYSTEM-FAILURE NUMBERS, CENTRAL CASE**

Reliability criteria (from Schultz et al. 2017): reliable = >=99.88% of years with
no Potomac deficit AND <=0.06% of years with emergency restrictions.

Medium Flows + Medium Demands — the central scenario:

| Year | Result |
|---|---|
| 2030 | reliable |
| **2045** | 98.77% no deficit -> **1.23% chance of an extreme drought with deficits up to 62 MGD over 5 days, both upstream reservoirs empty** |
| **2050** | 98.77% no deficit -> **1.23% chance of deficits up to 100 MGD over 10 days, reservoirs empty** |

Under **every** Lower Flows scenario, in **every** scenario year, Little Seneca and
Jennings Randolph are predicted empty on at least one day of an extreme drought.

**ICPRB NAMES DATA-CENTER CURTAILMENT AS A DROUGHT MEASURE**

> "the region may develop new strategies for implementation of water use
> restrictions during periods of drought that can help mitigate future increases
> in July demands, by curtailing outdoor water use and **potentially by managing
> daily water use fluctuations by data centers**."

The regional authority has already floated data-center demand management as a
drought-response lever. Our seasonal result (10x peak factor, peaking exactly when
flows are lowest) is the quantitative case for it.

**Climate inputs, all citable**

- **1 C of warming = 5.9% less annual flow** (stream flow response function
  Equation 7-1, beta1 = -0.059, R2 = 0.75, SE 0.176, all coefficients significant).
  Temperature-sensitivity scenarios are beta1 = -0.032 / -0.059 / -0.086 (+-1 SE).
- ~**35% of Potomac precipitation becomes stream flow**; the rest evapotranspires.
- **Historical trends are now statistically significant for the first time.**
  2010-2023 mean temperature 11.72 C vs 11.19 C baseline (Welch, p = 0.01).
  Mann-Kendall 1950-2023: precipitation rising (p = 0.044), temperature rising
  (p = 0.005), **no trend in mean flow**.
- Projected mean flow change: **-4.1% (2010-39), -4.9% (2040-69), -7.8% (2070-99)**.
- **100-year-drought flows fall 11% / 13% / 29%** across those periods (medium
  sensitivity, 0.01 quantile scaling factors 0.89 / 0.87 / 0.71).
- Meteorological change adds only **+4.6 to +7.4 MGD to annual WMA demand (1%)**
  but **+21 to +33 MGD to July demand (4%)** — the same summer-concentration
  pattern as data centers, stacking in the same months.

**Two candid methodological admissions worth citing**

1. **Their climate ensemble fits the past badly.** Of 54 CMIP6 members, 31 pass a
   KS test at p = 0.01 for 1950-1979; **at p = 0.05, none of the 54 pass** (versus
   145 of 231 CMIP5 members). They keep CMIP6 anyway for its improved physics and
   flag near-term (2010-2039) results as "preliminary and subject to further
   validation" — the projected 2010-2039 warming of 3.1 F is far above the 1 F
   actually observed.
2. **Their demand scenarios are deliberately narrow.** Low/High are Medium ±1
   standard error, i.e. a ~68% interval, "selected for this study rather than, for
   example, a 95 percent confidence interval, **to avoid demand scenarios that
   might be viewed as unrealistic by stakeholders**." An unusually frank statement
   that scenario width was set by audience tolerance, not statistics. Useful
   precedent when defending our own ±19% at 90%.

**PRRISM run design:** 80-year simulation = 29,302 days per run; 100 runs averaged
per scenario; 27 run sets (9 scenarios x 3 years) plus unaltered-historical runs.

### Part 9: Ch.8.3 (Results, Table 8-1) + Ch.9 (Conclusion) + Lit Cited start — lines 6674-7103

**TABLE 8-1 IN FULL — the system-performance grid**
(each cell: % years no deficit / % years emergency restrictions / days with
deficits / max Potomac deficit MGD / min combined Little Seneca + Jennings
Randolph storage BG)

**2030** — Higher Flows all reliable (9.9 / 7.8 / 5.4 BG remaining).
Medium Flows: Low 100%/0/0d/0/6.3 BG; Medium 99.91%/0/0d/1/**2.2 BG**;
**High 98.77%/2.50%/2d/54 MGD/0.0 BG**.
Lower Flows: **Low 98.77%/2.50%/3d/57/0.1**; **Medium 98.77%/2.50%/24d/102/0.0**;
**High 98.60%/2.50%/50d/142 MGD/0.0 BG**.

**2045** — Medium Flows: Low 99.81%/0.29%/0d/1/1.2; **Medium 98.77%/2.50%/5d/62/0.0**;
**High 98.35%/3.75%/27d/148/0.0**. Lower Flows: **95.06%/3.75%/103d/256 MGD/0.0** at
High Demands.

**2050** — Medium Flows: Low 99.05%/2.10%/1d/11/0.3; **Medium 98.77%/2.51%/10d/100/0.0**;
**High 97.63%/3.75%/38d/159/0.0**. Lower Flows: **95.06%/4.66%/117d/273 MGD/0.0**
at High Demands.

**THE FIVE-YEAR DETERIORATION IS THE HEADLINE**

Same central scenario (Medium Flows / Medium Demands), same target year (2050),
two consecutive studies:

| | 2020 study | **2025 study** |
|---|---|---|
| Likelihood of no deficit | 99.29% | **98.77%** |
| Max deficit | 21 MGD | **100 MGD** |
| Days in deficit | **1 day** | **10 days** |
| Worst-day storage (Higher Flows/Low Demands) | 8.6 BG | 7.3 BG |

**A five-fold increase in maximum deficit and a ten-fold increase in duration,
between two studies five years apart, for the same year.** ICPRB attributes it
to: +10 MGD higher demand forecast, +14 MGD higher summer upstream consumptive
use, and **+35-40 MGD higher October/November** consumptive use — the months that
bind during a 1930-type drought. Partly offset by slightly gentler flow
projections (-13% vs -16%).

This is the single most quotable fact in the document for a paper about
data-center water: **the region's own reliability assessment got dramatically
worse in one revision cycle, driven largely by revised consumptive-use accounting
— and data centers are the newly added component of that accounting.**

**Conclusion chapter, additional figures**
- 2050 upstream data-center consumptive use **4.6 MGD = 4%** of the 117 MGD total;
  **August 2050 total 151 MGD of which 8.2 MGD (5%)** is data centers.
- Demand forecast standard errors: **9.7% (2045), 10.0% (2050)**.
- **"To date, analyses of Potomac River flow data have not detected a long-term
  trend in average flow or in low flows"** — an important honest caveat: the
  deterioration is projected, not yet observed.

**References worth pulling for our literature section**
- **EPRI (2024)**, *Powering intelligence: Analyzing artificial intelligence and
  data center energy consumption* — the source of the 25%/68% Dominion load
  shares and of our 0.8 utilization factor.
- **Alissa et al. (2025), Nature 641:331-338**, "Using life cycle assessment to
  drive innovation for sustainable cool clouds" — a Nature paper on data-center
  LCA we do not currently cite.
- **Hogan (2015)**, "Data flows and water woes: The Utah data center", *Big Data
  & Society* — early critical work on data-center water.
- Siddik et al. (2021) and Mytton (2021) — already in our review.
- County of Fairfax (2024) data-centers report; Frederick County MD data-center
  zoning regulations (2024) — regional policy precedents.
- Schultz et al. (2017) water supply alternatives study — the source of the
  reliability thresholds (99.88% / 0.06%).

### Part 10: Ch.10 Literature Cited + Appendix A.1 — lines 7103-7532

**A PAPER IN PREPARATION THAT DIRECTLY OVERLAPS OURS — FROM THE SAME AUTHORS**

> **Seck, A. et al. (in preparation). "Will the Cloud Drain the River? Data
> Centers' Consumptive Water Use and Impacts on Regional Water Resources
> Resilience."**

A. Seck is the ICPRB author of the data-center chapter. The WMA study cites this
twice — once for "the footprint of data centers across the entire basin" (which
the WMA study explicitly does *not* cover) and once for methodological detail
behind the WUP derivation.

**This is the most important single item found in the whole read.** It means:
1. The institution whose constants we depend on is writing the basin-scale
   data-center water paper.
2. Our contribution must be positioned against it: theirs is basin-scale and
   (per the WMA study) on-site consumptive use; ours is facility-resolved,
   county-scale, and includes the electricity-related component they explicitly
   exclude. Those are complementary, but only if we know about it and say so.
3. **Action before submitting anywhere: contact ICPRB / A. Seck.** They
   acknowledge Prince William Water and JLARC staff by name in this report; a
   student doing facility-level work in their basin is a natural correspondent,
   and it de-risks a collision.

**Their published methods paper, which we should cite**

> **Schultz, C.L., Seck, A., Ahmed, S.N. (2025). "Is Hot Drought a Risk in the US
> Mid-Atlantic? A Potomac Basin Case Study." *Journal of the American Water
> Resources Association* 61:e70031.**

This is the peer-reviewed basis for the flow response function, the quantile
scaling, and the temperature-sensitivity scenarios. If we cite the 11%/13%/29%
drought-flow reductions, this is the citation.

**Data-center water literature in their bibliography we do not currently cite**

- **Ristic, B. (2015). "Water footprint of data centers." *Sustainability* 7(8),
  11260.**
- **Hogan, M. (2015). "Data flows and water woes: The Utah data center." *Big Data
  & Society* 2(2).**
- **Karimi et al. (2022). "Water-energy tradeoffs in data centers: A case study in
  hot-arid climates." *Resources, Conservation and Recycling* 181, 106194.**
- **Alissa et al. (2025). *Nature* 641:331-338** — data-center LCA.
- **Muller et al. (2024).** Cooling-tower blowdown treatment, *J. Env. Management*.
- **Masanet et al. (2020), *Science* 367:984-986**; **Shehabi et al. (2024)** US
  data center energy usage report.
- **Wallace et al. (2024), *JAWRA* 60:1008-1028** — reported vs unreported water
  use in the Potomac basin, the source of their unreported-use additions.
- Already in our review: Siddik et al. (2021), Mytton (2021), Li et al. (2023).

**Policy documents named**
- **New York State S.6394/A.9086, "New York State Sustainable Data Centers Act"**
  (2025-2026 session).
- County of Fairfax (2024) *Data centers: Report and recommendation*.
- Frederick County MD (2024) proposed data-center zoning regulations.
- **Va. Code § 62.1-44.15:5.02**; **COMAR 26.17.07.02** and **26.17.06.06**.

**Appendix A.1** is nine years (2015-2023) of monthly average and peak-day
production for each supplier. Fairfax Water annual average 152 MGD, July average
183, July peak-day record 241 MGD (2020). Washington Aqueduct 135 / 154 / 195.
WSSC 162 / 180 / 222. Useful if we ever need a municipal seasonal baseline at
daily resolution.

### Part 11: Appendix A.3 — lines 9485-9535
### CORRECTION TO PART 4 — OUR SEASONAL SHAPE IS *NOT* VALIDATED, IT IS ~70% TOO PEAKY

In Part 4 I recorded that our modelled data-center seasonal shape was
externally validated, matching ICPRB's published "close to three times the
average annual demand". **That was wrong, and Appendix A.3-2 shows why.**

Table A.3-2 gives ICPRB's monthly factors for data-center water use, derived
from **observed usage patterns in Loudoun and Prince William Counties**:

| Month | ICPRB (observed) | Ours (modelled) |
|---|---|---|
| Jan | 0.7 | **0.30** |
| Feb | 0.6 | 0.30 |
| Mar | 0.6 | 0.31 |
| Apr | 0.7 | 0.32 |
| May | 0.9 | 0.83 |
| Jun | 1.0 | 1.98 |
| **Jul** | **1.5** | **3.04** |
| **Aug** | **1.8** | **2.61** |
| Sep | 1.5 | 1.30 |
| Oct | 1.0 | 0.41 |
| Nov | 0.9 | 0.30 |
| Dec | 0.8 | 0.30 |

Both series are correctly normalised (mean 1.00). But:

- **Peak-to-trough: ICPRB 3.0x, ours 10.1x.**
- **Peak month: ICPRB 1.8 (August), ours 3.04 (July).** Our summer peak is
  ~70% higher than observed and lands a month early.
- **Winter: ICPRB 0.6-0.8, ours 0.30.** Our winter floor is less than half of
  observed.

**Where my Part 4 error came from.** The public fact sheet says "Monthly use in
summer can be close to three times the average annual demand." I matched that to
our 3.04x. But the technical appendix — observed data, normalised, from the two
counties that matter — caps the monthly factor at **1.8**. The fact sheet's
"three times" is almost certainly summer-versus-winter (1.8/0.6 = 3.0), not
summer-versus-annual-average. **The peak-day "as much as 10 times" claim is
separate and still stands; it is our monthly shape that is wrong.**

**What this means for the paper**

1. `seasonal_basin_surface.py` uses a CDD-proportional model with a swept
   baseload share (0.1/0.3/0.5). Even at a 0.5 baseload the July figure was
   22.8% of flow versus 33.7% at 0.1 — the sweep does not reach ICPRB's
   observed shape. **The baseload floor should be recalibrated to the observed
   0.6-0.8 winter factor, not swept over a guessed range.**
2. Every seasonal percentage we have reported is therefore **too high in summer
   and too low in winter**. The 17-25% of July flow figure — already cut from the
   abstract — would fall further on the observed shape.
3. This is the third instance of the same failure: a number that agreed with a
   *summary* document and disagreed with the *technical* source underneath it.
   The fact sheet was the only ICPRB document I had read in full before today.

**Action:** rerun `seasonal_basin_surface.py` with ICPRB's Table A.3-2 factors in
place of the CDD model, and report both. If the seasonal claim ever returns to
the paper it must use the observed shape.

**Also in A.3:** upstream data-center consumptive use forecast, all three
scenarios (MGD): 2025 0.0/0.1/0.1; 2030 1.0/1.3/2.3; 2035 2.3/3.1/5.4;
2040 2.8/3.7/6.5; 2045 3.1/4.1/7.2; **2050 3.5/4.7/8.1**.

### Part 12: Appendix A.1 (rest) + A.2.1-A.2.8 — lines 7532-8330

**ICPRB'S DEMAND FORECAST DOES NOT EXPLICITLY INCLUDE DATA CENTERS** (A.2.7)

> "Loudoun Water's June 2025 projections estimate **data center use at 7.8 MGD in
> 2030 and 11.5 MGD in 2035**, based on Loudoun County's permit and application
> data. These values are additional to the employee-based non-residential demands
> ... **The annual demand forecast used in this study was not adjusted to
> explicitly include projected data center water use.** While the forecast likely
> captures some of the associated increases through broader economic and
> development trends, **it does not fully represent the magnitude of expected data
> center expansion.** However, the high-demand scenario, which is 42.2 MGD above
> the baseline in 2030 and 82.2 MGD above the baseline in 2050, likely encompasses
> potential future data center growth. The estimated data center demand within the
> WMA ... is **approximately 30 MGD by 2050** ... Future studies should consider
> incorporating data center demands more explicitly."

Three things follow:
1. The region's water supply plan **does not model its fastest-growing water use
   explicitly**. It is absorbed into a high-demand scenario constructed for other
   reasons. That is a stronger and more specific version of the "assessment gap"
   claim in our abstract, and it is their own text.
2. **An internal inconsistency to be careful with:** Section 6.2 gives WMA
   data-center use as **22.2 MGD** average by 2050; A.2.7 says "approximately
   **30 MGD** by 2050". Do not quote either without saying which.
3. Loudoun Water's *own* county-permit-based projection (7.8 MGD in 2030) is an
   independent, jurisdiction-level number of the same kind we produce.

**CORRECTION TO PART 3 — I USED THE WRONG PRINCE WILLIAM DENOMINATOR**

Table 3-15's "Prince William Water" row (26.8 -> 32.3 MGD) is only the **Fairfax
Water purchased portion**. Table A.2-15 gives PWW's **total** demand, including
the City of Manassas purchase and Manassas Park sales:

**32.21 MGD (2023 actual) -> 36.97 (2050) -> 42.62 (2085)**

Corrected comparison:

| Our estimate | MGD | vs PWW **total** demand |
|---|---|---|
| On-site (Scope 1), all 243 | 1.76 | **4.8%** of PWW 2050 |
| Total footprint, 54 completed | 10.49 | **33%** of PWW 2023 |
| **Total footprint, all 243** | **49.60** | **1.34x** PWW 2050 (not 1.54x) |

The finding survives — the footprint still exceeds the county's entire municipal
demand — but the multiple is **1.34x, not 1.54x**. Use A.2-15, not 3-15.

**Prince William Water system detail we did not have**
- Four systems: **East, West, Hoadly Manor, Bull Run Mountain/Evergreen**. East,
  West and Hoadly Manor take Fairfax Water; West is also supplemented by **Lake
  Manassas**; Bull Run Mountain/Evergreen runs on **six groundwater wells**.
- **Purchase capacity: 62.4 MGD from Fairfax Water plus 5 MGD from the City of
  Manassas.** That is the contractual ceiling on the county's supply — worth
  comparing against any buildout scenario.
- PWW employee unit use fell from **46.4 gpd (2014) to 36.9 (2023)**; billed EMP
  covers "commercial, office, industrial", so data-center potable use sits inside
  it. All PWW meters are read monthly.
- Loudoun's employee unit use is **48.8 gpd** versus Fairfax retail 29 and PWC
  36.9 — and Loudoun explicitly notes "EMP includes industrial, e.g., data
  centers" with "Reclaimed Data Centers" reflecting potable use. **The
  data-center signal is visible in the employee unit-use series.**

**CO-OP system production (Table A.1-12), 2015-2023 averages:** annual 449 MGD;
July 516; peak 1-day July **630 MGD (2020)**; Jul-Oct average 489 MGD.
Loudoun Water total use grew 23 -> 28 MGD over the same period, peak-day 47 MGD.

### Part 13: Appendix A.2.9-A.2.19 — lines 8330-9485

**SECOND CORRECTION TO THE COUNTY DENOMINATOR**

Prince William County is served by **two** municipal suppliers, not one:

| | 2023 | 2050 |
|---|---|---|
| Prince William Water (A.2-15) | 32.21 | 36.97 |
| **VAWC Dale City** (A.2-22/23) — also in PWC | 4.94 | 5.16 |
| **County total** | **37.15** | **42.13** |

Final corrected comparison:

| Our estimate | MGD | vs county municipal demand |
|---|---|---|
| Total footprint, 54 completed | 10.49 | **28%** of county 2023 |
| **Total footprint, all 243** | **49.60** | **1.18x** county 2050 |

The claim survives all three revisions — the footprint still exceeds the county's
entire municipal water demand — but the multiple has fallen **1.54x -> 1.34x ->
1.18x** as I found the right denominator. **Use 1.18x, and cite Tables A.2-15 and
A.2-23, not Table 3-15.** This is the third time in this read that a headline
number moved because the summary table and the appendix table meant different
things.

**Other appendix findings**

- **Unmetered / non-revenue water varies enormously between suppliers:** DC Water
  **27-31%**, WSSC **17-23%** (their FY2017 Water Loss Reduction Plan reports
  15.7-20.9% since 2010), Arlington 10-14%, Prince William Water **10%**, Fairfax
  retail 7-10%. Any per-capita or per-employee comparison across suppliers is
  contaminated by this unless stated.
- **Employee unit use by service area (2023, gpd):** Loudoun **48.8**, Dale City
  66.2, Prince William 36.9, WSSC 41.5, DC Water 39.5, Fairfax retail 29,
  Vienna 23. Loudoun's figure is the one that contains data centers explicitly
  ("EMP includes industrial, e.g., data centers"), and Dale City's 66 is
  anomalously high for a residential area.
- Prince William Water's employee unit use **fell from 46.4 (2014) to 36.9
  (2023)** even as the county's data-center stock grew — consistent with
  data-center potable use being small relative to commercial employment, and with
  our own finding that on-site use is a few percent of the footprint.

### Part 14: Appendix A.4 (all 36 PRRISM tables) — lines 9535-11569
### DOCUMENT COMPLETE (11,569 lines)

Table 8-1 reports only the 80-year simulation average. A.4 gives three columns
per scenario: **1929-2009 (80-year), 1930 (drought of record replay), 1966
(record low-flow replay)**. The 1930 column is much worse and is not in the main
text.

**Days under emergency restriction in a 1930-drought replay** (not years — days):

| Scenario, 2050 | 80-yr avg | **1930 replay** |
|---|---|---|
| Medium Flows / Medium Demands | 2.51% | **25.95%** |
| Medium Flows / High Demands | 3.75% | **31.13%** |
| Lower Flows / Medium Demands | 3.75% | **35.12%** |
| Lower Flows / High Demands | 4.66% | **37.19%** |

And percent of days with no Potomac deficit in the same replay falls to
**72.50%** (2050 Lower/High) and **76.66%** (2050 Lower/Medium).

**If the 1930 drought repeated, the region would be under emergency water
restrictions roughly a quarter to a third of the time, even in the central 2050
scenario.** That is a far more legible statement of the stakes than "1.23%
likelihood of deficit", and it is in the appendix rather than the summary.

**1966 is not the binding event.** The record *low-flow* year produces deficits
only in the two most extreme 2045/2050 scenarios (-82 and -152 MGD). The 1930
*prolonged* drought binds everywhere. Duration, not depth, is what breaks the
system — which is why the October/November consumptive-use revision (+35-40 MGD,
Part 9) matters so much.

**Other A.4 facts not in the main text**
- **The Patuxent system runs short 18-22 times per 80-year simulation in every
  scenario, including the fully reliable ones.** It refills to 90% by June 1 in
  only ~82% of years, and **0% of the time in a 1966 replay**.
- Minimum average natural flow late summer: 691 MGD (80-yr), **456 (1930), 464
  (1966)**. Downstream of intakes this falls to **140-154 MGD** in the replays —
  against a 100 MGD flow-by requirement.
- One case (2045 Medium Flows / High Demands, 1930 replay) puts minimum average
  **fall** flow downstream of intakes at **60 MGD** — below the environmental
  flow-by.
- Climate change adds **+13 MGD to July demand** in the 2050 medium case
  (631 vs 618 MGD).
- Edgemon Quarry contributes only **0.14-0.19 BG** of minimum storage in any
  scenario — consistent with the 5 MGD regional benefit noted in Part 2.

---

## ICPRB WMA STUDY — READ COMPLETE. 266 pp / 11,569 lines / 611,569 chars.

---

## 7. PJM_SOM_2023_sec3_energy_market.pdf  [reading — 144 pp / 543,943 chars]
### Part 1: pp.123-201

### THE ABSTRACT'S "0%" IS FACTUALLY WRONG. NUCLEAR *IS* A PJM MARGINAL RESOURCE.

Our ledger entry `nuclear_never_marginal` states that "nuclear does not appear as
a marginal resource at all", sourced to the summary sentence on printed p.125
("coal units were 10.0 percent and natural gas units were 75.2 percent of
marginal resources"). That sentence simply does not enumerate every fuel.

**Table 3-69 (printed p.200), "Type of fuel used and technology (By real-time
marginal units): 2019 through 2023", lists Uranium/Steam explicitly:**

| Year | Nuclear share of real-time marginal resources |
|---|---|
| 2019 | **1.31%** |
| 2020 | **1.35%** |
| 2021 | **1.00%** |
| 2022 | **0.39%** |
| 2023 | **0.62%** |

And the accompanying text (p.201):

> "**The proportion of marginal nuclear units increased from 0.4 percent in 2022
> to 0.6 percent in 2023.** Most nuclear units are offered as fixed generation in
> the PJM market. **A small number of nuclear units were offered with a
> dispatchable range since 2015.** The dispatchable nuclear units do not always
> respond to dispatch instructions."

Corroborated by an MMU recommendation (printed p.132), open since 2016:

> "The MMU recommends that **PJM not allow nuclear generators which do not respond
> to prices or which only respond to manual instructions from the operator to set
> the LMPs in the real-time market.** (Priority: Low. First reported 2016.
> **Status: Not adopted.**)"

You do not recommend prohibiting something that never happens.

**Recomputed Lake Anna marginal attribution, with nuclear at its published share:**

| Marginal-mix year | Blended marginal intensity | Nuclear (= Lake Anna) share of marginal water |
|---|---|---|
| 2022 shares | 175.1 gal/MWh | **0.87%** |
| 2023 shares | 187.4 gal/MWh | **1.29%** |

**The correct statement is "approximately 1%", not "0%".**

### What this does and does not change

- **The headline survives.** 43% under average accounting versus ~1% under
  short-run marginal is still a relocation of essentially the entire attribution.
  The paper's thesis is unaffected.
- **The specific claim "0%" is false** and is falsifiable from Table 3-69 on page
  200 of the very document we cite page 125 of. A PJM-literate reviewer would
  find it immediately.
- **METHODOLOGY 54's framing improves.** We already conceded that the zero was
  definitional and that long-run marginal implicates nuclear. It turns out
  short-run marginal implicates nuclear too, just barely. The premise was not
  merely unproven — it was contradicted by the source.
- **Harness check 19** verifies that "York stays 0.00 across coal shares 0-15%".
  It tests robustness to the *coal* parameter while holding the nuclear term at
  zero by construction. It cannot detect this.

### Required actions
1. Change the abstract from "0% of electricity-related water use is attributed to
   Lake Anna" to **"under 2%"** or **"approximately 1%"**.
2. Rewrite ledger entry `nuclear_never_marginal` — the claim is false as stated.
   Replace with "nuclear is rarely marginal (0.4-1.4% of real-time marginal
   resources, 2019-2023)".
3. Add `PJM_MARGINAL_FUEL_MIX['nuclear'] = 0.006` (2023) or 0.0039 (2022) and
   re-run the basin attribution.
4. Extend harness check 19 to fail if the nuclear marginal share is set to zero.

### Other PJM findings so far
- **Full 2023 marginal mix (Table 3-69):** gas CC 69.20%, gas CT 11.01%, coal
  9.14%, wind 5.53%, gas steam 1.83%, gas RICE 1.09%, oil CT 0.91%, **uranium
  0.62%**, oil CC 0.19%, oil RICE 0.18%, municipal waste 0.12%, oil steam 0.06%.
  **Our 78:22 CC:CT gas split assumption is testable against this: the published
  split is 69.20 : 11.01 + 1.09 + 1.83, i.e. roughly 83:17, not 78:22.**
- **Day-ahead marginal resources are mostly financial, not physical:** in 2023
  UTCs 50.0%, INCs 16.7%, DECs 18.0%, and **generation only 15.0%**. Our use of
  real-time shares is the right choice, but the paper should say why.
- 2023 was a net-retirement year: 6,269 MW added, 6,728 MW retired.
- Real-time load-weighted LMP fell 61.2% ($80.14 -> $31.08/MWh), the largest
  annual decline since PJM markets began in 1999.
- Generation change 2023 vs 2022: coal **-27.9%**, gas +8.4%, oil -0.8%, wind
  -8.1%, solar +20.1%.
- Nuclear was **33.3% of PJM generation** in 2023 (273,488.6 GWh).

### Correction applied (code + ledger + harness), 31 Jul 2026

- **Abstract**: "0% ... attributed to Lake Anna" -> **"under 2%"**. 1965/2000.
- **`PJM_MARGINAL_FUEL_MIX` rebuilt from Table 3-69's published 2022 row**:
  gas CC 61.66%, gas steam 1.42%, gas CT 11.26%, gas RICE 0.86%, coal 10.02%,
  **nuclear 0.39%**, zero-water residual 14.39%. Sums to 1.0000.
  **The unsourced 78:22 CC:CT assumption is deleted** — the SOM publishes the
  split directly, so it was never needed. Blended marginal moves 165.7 -> **175.1
  gal/MWh**.
- **Ledger**: `nuclear_never_marginal` replaced by `nuclear_rarely_marginal`
  (external_data, verbatim quote verified on printed p.201 / PDF p.79);
  `pjm_marginal_gas_cc_ct_split` retyped `limitation` and marked superseded.
- **Check 19 rewritten.** The old version *enforced the error*: it built a
  synthetic mix with no nuclear term, confirmed York came out 0.00, and required
  the ledger to contain an entry called `nuclear_never_marginal`. It now uses the
  shipped mix, requires York to be **strictly non-zero and under 2%**, sweeps the
  nuclear share over its published five-year range, and fails if the abstract
  contains the false 0% or the ledger reverts.

**Sensitivity, and a live caveat on the new wording:**

| Nuclear marginal share | York share of Scope 2 |
|---|---|
| 0.39% (2022 — the year our cited sentence reports) | **0.87%** |
| 0.62% (2023) | **1.38%** |
| **1.31% (2019)** | **2.90%** |
| 0.00% (the old premise) | 0.00% |

**"Under 2%" is true for 2022 and 2023 shares but NOT for 2019-2021**, when
nuclear ran 1.00-1.35% of marginal resources and York would reach 2.2-2.9%. The
abstract says "using PJM marginal fuel shares" without naming a year. Either name
the year (2022) or widen to "under 3%". Flagged, not silently resolved.

### Part 2: pp.148-152 — THE MECHANISM BEHIND MARGINAL NUCLEAR, PRECISELY

Table 3-12, "Dispatchable status of day-ahead energy offers: 2023", nuclear row:

| Must Run | Eco Min | ($300)-$0 | $0-$25 | $25+ | **Dispatchable %** |
|---|---|---|---|---|---|
| **90.1%** | 6.6% | **2.4%** | 0.8% | 0.0% | **3.3%** |

So **3.3% of nuclear MW is offered as dispatchable**, and **2.4 of those 3.3
points are offered at NEGATIVE prices** (the $(300)-$0 band). That is the exact
mechanism by which a nuclear unit can end up marginal: a thin dispatchable
sliver, mostly bid negative to avoid cycling. It also explains why the share
moves year to year (1.35% in 2020, 0.39% in 2022) — it depends on how much of
that sliver is at the margin in a given year's price distribution.

This is a far better citation for the paper than the summary sentence: it gives
the magnitude, the mechanism, and the reason for variability, all in one table.

Corroborating: "**Solar units, wind units, run of river hydro units, and nuclear
units are currently not subject to parameter limits**" (p.153) — nuclear is
outside the parameter-limit regime entirely, which is why the MMU's 2016
recommendation to stop it setting LMP has never been implemented.

**Other PJM structural facts worth having**
- Day-ahead offers 2023: 23.2% must-run, 31.7% economic minimum, 44.6%
  dispatchable, 0.5% emergency.
- **2,257 MW on average (4,233 MW at the 90th percentile) failed the ICAP must-offer
  requirement in 2023** — "larger than the reserve shortages that trigger scarcity
  pricing and larger than most supply contingencies."
- PJM declared **cold weather alerts on 3 days and hot weather alerts on 21 days**
  in 2023. During those alerts **32.1% of unit hours** were committed on
  price-based schedules less flexible than their PLS schedules.
- 31.5% of unit hours for units failing the day-ahead TPS test were committed on
  price schedules less flexible than cost.

### Part 3: pp.144 (degree days) — THE SEASONAL ERROR, DIAGNOSED

PJM's Table 3-8 gives monthly heating and cooling degree days for the whole RTO.
2023 CDD: Jan-Mar 0, Apr 17.2, May 31.0, Jun 162.2, **Jul 387.8**, Aug 310.0,
Sep 144.0, Oct 29.8, Nov-Dec 0. Total 1,081.8; monthly mean 90.2.
**July carries 4.30x the monthly mean CDD.**

Our `seasonal_basin_surface.py` uses f = b + (1-b) * CDD/CDDbar with the baseload
share b swept over 0.1 / 0.3 / 0.5. Fitting b to ICPRB's *observed* monthly
factors (Part 11):

| baseload b | July factor | Aug | Jan | mean abs error vs ICPRB |
|---|---|---|---|---|
| 0.10 | 3.97 | 3.19 | 0.10 | 0.77 |
| 0.30 (our central) | **3.31** | 2.71 | 0.30 | 0.55 |
| 0.50 (our high) | 2.65 | 2.22 | 0.50 | 0.33 |
| **0.70** | **1.99** | 1.73 | 0.70 | **0.16** |
| **0.76** | **1.79** | 1.59 | 0.76 | **0.16** |

**The baseload share implied by observed data is ~0.70-0.76. Our swept range
(0.10-0.50) never reaches it.** That is the precise reason our July factor (3.04)
runs ~70% above ICPRB's observed 1.5-1.8: we assumed data-center cooling is
mostly weather-driven, when the observed data says it is mostly a constant load
with a weather-driven component of only ~25%.

Physically that is the right answer and we should have expected it: a data center
runs its IT load year-round and rejects heat year-round. Only the *incremental*
evaporative duty tracks temperature.

**Fix:** replace the guessed sweep with a baseload calibrated to ICPRB's Table
A.3-2, or simply use their published monthly factors directly. Then re-derive
every seasonal number. All of our reported seasonal percentages are too high in
summer and too low in winter by roughly this factor.

**Also useful:** the paper can now cite PJM CDD (Table 3-8) as the weather driver
and ICPRB Table A.3-2 as the observed response, which is a much better-sourced
seasonal treatment than what we built.

### PJM SOM — remaining content is market structure with no water relevance
Confirmed by exhaustive term search across all 10,673 lines: "water" appears only
as a fuel-type row (Hydro 0.0-0.1% of marginal units), a company name ("Water
Strider"), and in "ambient temperature changes in fuel consumption". There is no
consumptive-use, cooling-water or drought content in Section 3. The document's
value to this paper is entirely: (1) Table 3-69 marginal fuel shares, (2) Table
3-12 nuclear dispatchability, (3) Table 3-8 degree days.

---

## 8. Rpt598.pdf — JLARC, *Data Centers in Virginia* (Dec 2024)  [reading — 156 pp]
### Part 1: Summary + Recommendations (pp. i-xiv) + Ch.1 start

**THE "WORLD'S LARGEST" CLAIM, FINALLY SOURCED AND QUANTIFIED**

> "**Northern Virginia is the largest data center market in the world, constituting
> 13 percent of all reported data center operational capacity globally and 25
> percent of capacity in the Americas.**"

We spent an entire exchange hedging this down to "within the world's largest
region" because it could not be sourced. JLARC states it with percentages. Note
it is about **Northern Virginia**, while ICPRB's fact sheet says the **Potomac
basin** — two different, mutually consistent framings, both citable.

**JLARC RECOMMENDATION 6 IS OUR POLICY ASK, ALREADY DRAFTED**

> "The General Assembly may wish to consider amending the Code of Virginia to
> **expressly authorize local governments to (i) require proposed data center
> developments to submit water use estimates and (ii) consider water use when
> making rezoning and special use permit decisions** related to data center
> development. (Chapter 5)"

Virginia's own legislative audit commission has formally recommended exactly the
disclosure mechanism our VOI analysis quantifies. **The paper's policy section
should cite Recommendation 6 and supply the missing number: what that disclosure
would actually buy (-10pp on the county interval).** That converts our result
from a proposal into evidence for a pending legislative recommendation.

**Their water finding, and where it differs from ours**

> "**Data center water use is currently sustainable, but use is growing and could
> be better managed** ... Most data centers use about the same amount of water or
> less as an average large office building ... **while DEQ is responsible for
> ensuring water sustainability, there is less oversight over how available water
> should be shared across various uses in a locality.** Virginia as a whole is
> relatively water rich, but water is more limited for some localities."

JLARC assesses **on-site use only** and concludes it is sustainable. That is
consistent with our finding that on-site is ~2.4% of the footprint — and it
sharpens the paper's contribution: **both** authoritative Virginia assessments
(JLARC 2024, ICPRB 2025) scope to on-site use, and both conclude the direct
impact is modest. Neither assesses the 88%.

**Energy context, from an independent forecast**
- "**Unconstrained demand for power in Virginia would double within the next 10
  years**, with the data center industry being the main driver." State demand was
  flat 2006-2020.
- Meeting even **half** of unconstrained demand would need "one large 1,500 MW
  [gas] plant every two years for 15 consecutive years, equal to the busiest
  period of the last decade (2012-2018)."
- Both scenarios "**rely on energy from as yet unproven nuclear technologies**."
- Residential Dominion customers face **+$14 to $37/month** in real
  generation/transmission costs by 2040.
- Consultants: Weldon Cooper Center (UVA) for economic impact and the independent
  demand forecast; **Energy + Environmental Economics (E3)** for grid modelling.

**Industry structure numbers**
- A typical **250,000 sq ft data center has ~50 full-time workers**, half of them
  contract; **~1,500 construction workers at peak**; 12-18 months to build.
- Industry-wide: 74,000 jobs, $5.5B labor income, $9.1B GDP annually — "most of
  these economic benefits derive from the construction phase."
- **Sales tax exemption was worth $928 million in FY23** and is used by ~90% of
  the industry; expires 2035.
- Data center revenue is **<1% to 31% of total local revenue** in the five
  localities with mature markets.
- **One-third of data centers are currently located near residential areas.**
- Backup generators: nearly all Tier 2 diesel, run only for maintenance/emergency;
  **<4% of Northern Virginia NOx**, <=0.1% of CO and PM.

**Appendices flagged for close reading:** J (PUE ratios — directly tests our PUE
assumption), I (on-site generation — the off-grid threat ICPRB raised), K
(additional natural resource considerations), L (**planning and zoning changes in
Fairfax, Loudoun and Prince William**).

### Part 2: Ch.5 (Natural Resources) + Appendices I, J, K, L

**THE WITHDRAWAL-PERMIT FINDING, SOURCED**

> "**Only two data centers have their own DEQ withdrawal permits**, and any data
> centers that do make their own withdrawals are subject to the same regulations
> as water utilities."

Statewide. That is the authoritative version of our 235/243 no-permit finding,
and it means the pattern is not a Prince William anomaly — it is how the industry
is supplied everywhere in Virginia. Permit thresholds: **>10,000 gpd** non-tidal
surface, **2 MGD** tidal surface, **300,000 gal/month** groundwater in a
groundwater management area; renewed at least every 15 years.

**Scale context that reframes the on-site number**
- 2023 Virginia data-center industry total: **2.1 billion gallons** (~5.75 MGD),
  just over a third reclaimed; **<0.5% of total state withdrawals**.
- **"The state's largest industrial water user in 2023 used about 36.5 billion
  gallons"** — the entire data-center industry is **6%** of one industrial user.
- Industry share at the six utilities reviewed: **0.2% to 21%**; a data center was
  the single largest customer at only **two of six**.

Our all-243 on-site estimate (1.76 MGD delivered) is ~31% of the entire current
Virginia industry's on-site use (5.75 MGD) — plausible for a county holding a
large share of approved buildout, and a useful sanity check to state.

**PUE — Appendix J directly tests our assumption, and states our thesis**
- "large companies now report **fleetwide average PUEs of 1.1 to 1.4**" — brackets
  our OPERATOR_DISCLOSED_PUE values (Meta 1.08, Google 1.09, AWS 1.14, MS 1.16).
- "As recently as 10 years ago, **PUEs of 1.9 or above were common**."
- **The water-energy tradeoff, in policy terms:** a PUE mandate "could have two
  unintended consequences: (1) **it could encourage more water use by the
  industry, because water-dependent cooling uses less energy**, and could make it
  harder for companies that use dry cooling systems to comply." Germany has
  legislated PUE limits (1.2-1.3); **similar legislation has been proposed in
  Virginia**. This is our paper's argument arriving as a live legislative risk:
  an energy-accounting rule that would increase water use.

**Off-grid generation is not yet a threat to our method — Appendix I**
- "**only one data center site in Virginia appears to actively rely on on-site
  generation for a substantial share of its energy needs**"; only natural gas is
  currently viable; SMRs "will not realistically be available until 2035."
- So our grid-based Scope 2 attribution is safe today. ICPRB raised off-grid as a
  future risk (Part 7); JLARC quantifies it as n=1. **Cite both.**

**Appendix K — Scope 3 and discharge**
- Servers "are replaced **every three to five years**" — the turnover rate behind
  the embodied-water (Scope 3) term we take from Privette et al.
- Discharges "may contain relatively large concentrations of **salts, other
  dissolved solids, and chemical additives**"; most go to a wastewater utility,
  which "can require the data center to pretreat."

**Appendix L — the three counties**
- "**Sites in Loudoun, Prince William, and Fairfax account for 80 percent of data
  centers in the state.**"
- Prince William: data-center ordinance advisory workgroup created **28 Feb 2023**;
  Board of Supervisors votes on noise amendments spring 2025 and other policy
  changes later in 2025; further votes planned **2026**. Fairfax: comprehensive
  zoning update effective 1 Jul 2021, further changes 11 Sep 2024.
- **A live policy window in our own county, with a 2026 vote pending.**

**Also: DEQ's reclaimed-water regulatory review concludes September 2026** — and
"DEQ currently permits **only two water utilities**, including Loudoun Water, to
provide reclaimed water for evaporative cooling uses." Reclaimed water is not
generally available in Virginia; Prince William is not one of the two.
