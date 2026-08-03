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

---

## Part 15 — JLARC Rpt598, the chapters I had NOT read line-by-line
*(Ch. 1, 2, 3, 4, 6, 7 and Appendices A–H, read in full 2026-08-02.
Ch. 5 and Appendices I–L were already logged in Parts 12–14; re-read here and
nothing in them changed.)*

This part exists because the previous reading report admitted these chapters were
skipped. They were skipped on the assumption that a report chapter titled "Energy
Costs" or "Economic and Fiscal Impacts" could not contain anything a water paper
needs. **That assumption was wrong three times over.** The most important
external cross-check on our county power estimate, the only quantified long-run
marginal number available anywhere in the corpus, and the fact that most
incremental data-center energy is *imported out of Virginia entirely* are all in
the chapters that were skipped.

### 15.1 Chapter 1 — an independent top-down anchor for PWC total load

Three sentences, none of them in a water context, combine into a genuine
out-of-sample check on our fleet power estimate:

- p.5: "There are approximately **150 data center sites** in Virginia, which
  collectively house around **340 data center buildings**."
- p.5: "In total, Virginia data center sites use approximately **5,050 megawatts**
  of power. (This is based on the 2024 peak load forecast by Dominion Energy and
  Mecklenburg, Northern Virginia, and Rappahannock electric cooperatives in
  August 2023.)"
- p.5: "**Loudoun County alone accounts for approximately half** of the state's
  data center industry in terms of number of sites, building square footage, and
  estimated energy usage."
- p.16: "Loudoun collects substantially more revenue from data centers primarily
  because its data center market size is **three times larger than Prince
  William's**."

Chained: Loudoun ~= 2,525 MW; **Prince William ~= 840 MW** of operating
data-center load as of the Aug-2023 forecast for 2024.

This is derived from *utility peak-load forecasts*, i.e. metered demand — a
completely different measurement path from our floor-area/permit-capacity ladder.
**ACTION: compare our 54-building total MW against ~840 MW.** If they agree to
within the +/-60% band this is a far stronger validation than the JLARC
distributional check we already have, because it validates the *level*, not the
shape. If they disagree, we need to know before submitting. Note the vintage
mismatch (JLARC's 840 MW is 2024 operating; our 54 "completed" is a construction
status) and the site-vs-building mismatch below.

**Site count cross-check (Appendix B, Table B-1, p.102):** Prince William =
**24 data center sites**; Loudoun 71; Fairfax 20; total across 8 localities 131.
Our 54 completed *buildings* across ~24 sites is 2.25 buildings/site — plausible
against the statewide 340/150 = 2.27. **The two independent counts agree.** This
is the first external corroboration of our building inventory that does not come
from the county's own GIS.

Other Ch.1 numbers worth having:
- 63 million sq ft of data-center space statewide on 7,200 acres.
- Smallest VA site ~1 MW; larger campuses 200+ MW.
- "over a quarter of the state's existing data center square footage built in
  2022 and 2023" — the fleet is very young, which matters for our PUE and
  cooling-technology assumptions.
- 80% of the industry is in Loudoun + Prince William + Fairfax; PWC is "the
  fastest-growing locality."

### 15.2 Chapter 3 — the long-run marginal number we have been asserting without one

Our abstract says "**short-run** marginal accounting," and `build_submission.py`
carries a coupling note saying long-run marginal "implicates North Anna far
more." Until now that was a qualitative hedge with no number behind it. JLARC's
E3 grid model supplies one, in Appendix H.

**Table H-4 (Scenario 1, unconstrained demand, no VCEA) vs Table H-6 (Scenario 3,
no new data center demand), Virginia nuclear energy in TWh:**

| Year | S1 unconstrained | S3 no new DC | DC-attributable |
|------|-----------------:|-------------:|----------------:|
| 2025 | 32 | 32 | 0 |
| 2030 | 32 | 32 | 0 |
| 2035 | 32 | 32 | 0 |
| 2040 | 56 | 32 | **+24** |
| 2045 | 74 | 32 | +42 |
| 2050 | 116 | 32 | +84 |

Under half-unconstrained demand (Table H-5) 2040 is 56 vs 32 — also +24.

So under JLARC's own capacity-expansion model, data-center growth is responsible
for **the entire projected increase in Virginia nuclear generation**, +24 TWh/yr
by 2040 — a 75% increase over the 32 TWh baseline that persists flat forever
without data centers. Nuclear *capacity* goes 3,708 MW (all scenarios, through
2035) to 6,388 MW in 2040 and 13,356 MW in 2050 under S1, but stays at 3,708 MW
in S3 (no VCEA).

**Why this matters for the paper, precisely:** it is the quantitative
justification for the word "short-run" in the abstract. Short-run marginal
dispatch gives Lake Anna ~1% because nuclear is 90.1% must-run and almost never
sets price (SOM Table 3-12, Part 9). Long-run marginal — which is what a
capacity-expansion model computes — attributes *all* of the nuclear build to data
centers. The two conventions do not merely differ by a little; they differ by the
entire nuclear increment. This is the strongest possible support for the paper's
central claim that the convention, not the physics, decides which basin is
implicated.

**Caveat that must travel with it:** the model "assumes that new nuclear
generation will not be available until 2035," and the new capacity is presumably
SMRs at unspecified sites, not North Anna uprates. So this quantifies
*long-run marginal nuclear*, not *long-run marginal Lake Anna*. Do not let it
drift into a North Anna claim. It is still the right number for the
short-run/long-run contrast.

**The bigger finding — most incremental energy leaves Virginia's basins entirely.**
Same tables, net imports (TWh):

| Year | S1 unconstrained | S3 no new DC | DC-attributable |
|------|-----------------:|-------------:|----------------:|
| 2025 | 50 | 38 | +12 |
| 2040 | 112 | 21 | **+91** |
| 2050 | 90 | 24 | +66 |

Table 3-1 (p.29) states this directly: data-center share of imported energy is
**+79 TWh (no VCEA) / +92 TWh (VCEA)** by 2040, and it exceeds the net increase
because "without data center demand, imported energy would decline" (-17 TWh).

Compare: +24 TWh of new in-state nuclear vs +79 to +92 TWh of new imports. **Under
the long-run convention, roughly three-quarters of the incremental data-center
energy — and therefore its water — is generated outside Virginia altogether.**
Neither the Potomac nor the York is the receiving basin for most of it.

This does not change any number in the current abstract (which is about today's
54 completed buildings under two *attributional* conventions). It is the natural
extension for the paper: a third convention, forward-looking and
capacity-expansion-based, that displaces the burden not just to another basin but
out of the state.

**Utility-territory problem — a real limitation in our Scope 2 attribution.**
p.26: Virginia's co-ops are a "significant portion" of the state; NOVEC is the
largest and, unlike the others, "purchases its own generation and operates one
power plant." p.121 (App. G): VCEA's renewable requirements "do not apply to
electric cooperatives," and "**a majority of future data center growth (~60
percent) is expected to occur in co-op service territories**." p.35: "Most co-ops
plan to purchase energy for data center customers **from the PJM market** rather
than building generation."

Prince William is served by both Dominion and NOVEC. Our average-accounting
attribution uses `DOMINION_GENERATION_MIX`. **If a material share of the 54
buildings are NOVEC customers, the Dominion mix is the wrong average mix for
them** — a NOVEC customer's average is closer to a PJM-market mix, which has less
North Anna in it and would *lower* the 40% Lake Anna figure. This is a genuine
methodological exposure and is not currently ledgered.
**ACTION: determine the serving utility for the 54, or add an explicit limitation.**

Other Ch.3 items:
- p.27: PJM forecast 5.5% year-over-year growth in the Dominion zone by 2024.
- p.27: JLARC's independent forecast has VA unconstrained demand **doubling
  within 10 years**, almost all in the Dominion transmission zone.
- p.33: solar needs 5-10 acres/MW (avg 7.5); 73,000-165,000 additional acres by
  2040. Land, not water, but it is the competing-resource story.
- p.39: "**Data center companies in Virginia do not currently participate in
  demand response programs**," because "energy use is driven by computing
  activity." Directly supports our flat-load / high-baseload assumption — and is
  independent confirmation of the ~0.76 baseload we back-calculated from PJM
  degree days in Part 11, against the 0.10-0.50 our `seasonal_basin_surface.py`
  currently sweeps.
- p.41: "at the end of the day, a 200 MW data center is going to be a 200 MW data
  center" — efficiency gains are re-spent on computing. Supports treating
  installed capacity, not efficiency trajectory, as the driver.

### 15.3 Chapter 7 + Appendix J — the energy-water tradeoff is a named policy risk

App. J, p.132, on a legislated PUE requirement: it "could have two unintended
consequences: (1) it could **encourage more water use by the industry, because
water-dependent cooling uses less energy**, and could make it harder for
companies that use dry cooling systems to comply."

This is JLARC stating, in its own voice, the exact coupling our scope framework
formalises: **Scope 1 and Scope 2 trade off against each other.** An
energy-efficiency mandate pushes water use *up* on site; a water-efficiency
mandate pushes energy use up, and with it Scope 2 water somewhere else. A
regulator optimising either scope alone will move the burden rather than reduce
it. This is the single best policy hook in the whole report for our paper, and it
is in an appendix about a ratio.

Also App. J: PUEs of 1.9+ were common 10 years ago; hyperscalers now report
fleetwide **1.1 to 1.4**. Germany legislated 1.2-1.3. Our PUE assumption should
sit in the 1.1-1.4 band and be cited here.

Ch. 7, Table 7-1, p.91: every policy lever JLARC proposes is attached to the
**sales and use tax exemption** ($928.6M in FY23 savings; ~90% of the industry by
MW uses it; expires 2035). Note for the policy paragraph: **Virginia has one
lever that reaches ~90% of the industry, and water is not currently attached to
it.** Recommendation 6 (water use estimates for rezoning) is the only water
recommendation, and it is permissive local authority, not a condition of the
exemption. That gap is a concrete, citable policy finding.

### 15.4 Chapter 2 + Appendix D — structural support for the Scope 3 term

Our Scope 3 is a literature range (5-15%, Privette et al.) with no PDF in the
corpus, ledgered as not machine-verifiable. JLARC does not give a water number,
but it gives the expenditure structure that makes a large, non-local Scope 3
plausible:

- Fig. 2-2, p.13: capital investment is **68% IT and mechanical equipment**, 20%
  construction, 6.1% land, 6.1% other. Table D-1 confirms: $39,957M exempt
  equipment of $58,600M total FY21-23.
- p.12: "**there are no major computer server manufacturers in Virginia**" —
  servers "are sourced from outside the state or the country."
- App. D, p.110: electricity is **~40% of data center operating expenditures**
  (industry reports, and independently "data center representatives also
  estimated energy accounts for about 40 percent of their operating costs during
  structured interviews").

So: two-thirds of the capital is equipment made elsewhere, and 40% of the
operating cost is electricity. A footprint that is overwhelmingly off-site is
what this cost structure predicts. Our 88% Scope 2 share is consistent with a
40%-of-opex electricity bill in a way that is worth one sentence in the paper.

App. D also documents that data centers have **no NAICS code of their own**
(518210 is only ~15% data centers in VA), and that "only 41 percent of data
center jobs were classified under data processing, hosting, and related
services." Useful precedent: **the reason nobody has facility-level data is
partly that the industry is not a statistical category.** That is a better
framing of our disclosure argument than "operators decline to report."

### 15.5 Chapter 4 and Chapter 6 — read in full, nothing load-bearing for water

Ch. 4 (Energy Costs): cost-of-service, retail choice, stranded-cost risk,
co-op solvency. Residential generation+transmission charges +$14/month by 2040
under half-unconstrained, +$33 to +$37 under unconstrained. Table 4-1 shows E3's
independent cost allocations matching Dominion's. Nothing water-relevant; logged
so the record shows it was read, not skipped.

One transferable idea: p.50, Dominion "will only build new transmission to serve
1,000 MW if that is the **forecasted metered load**," even when customers have
requested 2,000 MW. **Requested capacity and metered load differ by roughly 2x in
the utility's own planning.** That is an independent, non-water corroboration of
the redundancy x utilization = 0.4 derating in ICPRB Eq 6-3 that our estimator
applies. Worth a ledger entry.

Ch. 6 (Local Residential Impacts): siting, noise, zoning. 29% of VA data center
sites are within 200 ft of residential zoning; Prince William 21% within both 200
and 500 ft (Table B-1). Noise 40-59 dBA, below the 55-60 dBA local limits, but
A-weighting misses the low-frequency drone; Recommendation 8 asks for C-weighted
authority. No water content. Read in full.

Appendix A is the study resolution; note clause (ii) directs JLARC to "assess
impacts of the data center industry on Virginia's natural resources" — water is
in scope by resolution, and Chapter 5 is the entire response to it. That is the
provenance of the "regional/legislative assessment is limited to Scope 1" claim.

Appendix B (methods) confirms the water dataset: 2023 usage from utilities
serving **Fairfax, Henrico, Loudoun, Mecklenburg, and Prince William counties and
the town of Wise**, "typically reported for anonymous, individual data center
buildings," two utilities annual, three monthly, one daily. **Prince William
buildings are in JLARC's distribution.** Our distributional validation is
therefore partly in-sample for our own county — a caveat the validation writeup
must state.

Appendix C: only SCC and VEDP submitted response letters; SCC reviewed
"Sections 3 and 4, and Appendices F, G, I, and J" and offered only high-level
verbal feedback. **DEQ did not submit a written response**, so Chapter 5's water
findings carry no agency counter-signature.

Appendices E, F, G, H: sales-tax-exemption map; generation/transmission siting
and CPCN criteria; VCEA RPS schedule (Dominion 26% in 2025 to 100% in 2045, co-ops
exempt); and the E3 capacity/energy tables mined in 15.2 above.

---

## Part 16 — PJM 2023 State of the Market, Section 3, read cover to cover
*(All 144 printed pages / 9,404 extracted lines, 2026-08-02. Previously only the
water-relevant sections had been read in full; the rest was covered by term
search. Reading the whole thing surfaced three things term search could not,
because none of them contain the words "water", "nuclear", or "Anna".)*

### 16.1 The Market Monitor attributes Dominion Zone congestion to data centers

Printed p.162, in a passage about *up-to-congestion virtual trading* — a section
with no obvious connection to this paper:

> "Congestion in the Dominion Zone in the first six months of 2023 resulted from
> the continuing increase in **data center load in Northern Virginia**."

Supporting numbers, Table 3-28:
- The DOMINION HUB -> DOM_RESID_AGG up-to-congestion path cleared **37,091,596
  MWh in 2023**, up from 12,926,796 MWh in 2022 — a **2.9x increase in one year**.
- That single path was **21.2% of all cleared UTC MW** in PJM and produced
  **55.3% of all UTC profits** ($22.7M of $41.1M PJM-wide).
- Figure 3-36 note: "In 2023, the most profitable UTC transactions were
  concentrated in the **Dominion Zone** and on dates with high real-time
  congestion in the Dominion Zone, which occurred primarily in January through
  May, 2023."

This is the independent market monitor, in its own voice and for its own
purposes, saying that Northern Virginia data-center load is now a first-order
driver of price formation in the Dominion zone. It is the single best citation in
the corpus for "this is already large enough to move the system," and it is
completely independent of ICPRB, JLARC, and the county.

Zonal price corroboration (Table 3-53): DOM real-time load-weighted average LMP
was **$99.52/MWh in 2022** — the highest of any PJM zone — and $37.50 in 2023,
still second only to BGE.

### 16.2 The Dominion Zone is already a net importer of 18% of its load

Table 3-62, real-time generation less real-time load by zone (GWh):

| Zone | 2023 generation | 2023 load | net |
|------|----------------:|----------:|----:|
| DOM  | 92,891 | 113,612 | **−20,721** |

2022 was −20,041 on 112,103. So **18.2% of Dominion-zone electricity consumption
is already met by generation outside the zone**, today, measured — not forecast.

This matters because it is the *present-tense*, independently-sourced version of
the claim JLARC's E3 model makes about the future (+79 to +92 TWh of
data-center-attributable imports by 2040, Part 15.2). Two different documents,
two different methods, same direction. The paper can now say the displacement is
observed, not projected.

It is also a caution on our own attribution: our Scope 2 assigns water to
generators using a *Dominion* mix, but nearly a fifth of the zone's energy
physically comes from elsewhere in PJM.

### 16.3 There is more than one "average" — and the choice may be ours by accident

Table 3-63, PJM-wide 2023 generation: Nuclear 273,489 GWh (**33.3%**), Gas
363,660 (44.3%), Coal 120,876 (14.7%), Wind 28,937 (3.5%), Solar 11,098 (1.4%),
Hydro 15,489 (1.9%). Table 3-66 gives the series back to 2008.

Our average-accounting result — ">40% of electricity-related water to Lake Anna"
— is computed on `DOMINION_GENERATION_MIX`. But PJM-wide nuclear is 33.3%
spread across the entire RTO, of which North Anna is a small part. **Under a
PJM-market average mix, Lake Anna's share would be far below 40%.**

Which average is correct is not a modelling preference — it depends on *who sells
the building its electricity*, and JLARC (Part 15.2) says Prince William is
served by both Dominion and NOVEC, that co-ops "purchase most energy for their
data center customers **from the PJM market**," and that ~60% of future
data-center growth is in co-op territory.

So there are at least **three** conventions, not two:
1. utility-average (Dominion mix) -> Lake Anna >40%
2. market-average (PJM mix) -> Lake Anna far lower
3. short-run marginal (PJM real-time marginal fuel shares) -> Lake Anna ~1%

This does **not** weaken the paper. It is the paper's thesis, with a third data
point and a sharper edge: the convention is not even a free choice, it is
determined by a contractual fact (which utility serves the meter) that is itself
not in our dataset. **ACTION: determine the serving utility for the 54, or state
the Dominion-mix assumption explicitly as a limitation.** Not currently ledgered.

### 16.4 Marginal-share details that firm up the "short-run" framing

**Table 3-69, real-time marginal resources, now with the 2023 row:**

| Fuel/Tech | 2019 | 2020 | 2021 | 2022 | 2023 |
|---|---:|---:|---:|---:|---:|
| Gas CC | 62.13% | 64.33% | 59.75% | **61.66%** | 69.20% |
| Gas CT | 5.97% | 5.89% | 10.06% | **11.26%** | 11.01% |
| Coal Steam | 24.37% | 17.53% | 14.15% | **10.02%** | 9.14% |
| **Uranium Steam** | 1.31% | 1.35% | 1.00% | **0.39%** | **0.62%** |
| Gas Steam | 1.29% | 2.12% | 1.17% | **1.42%** | 1.83% |
| Gas RICE | 0.00% | 0.29% | 0.67% | **0.86%** | 1.09% |

Our `PJM_MARGINAL_FUEL_MIX` uses the 2022 column — matches exactly. The 2023
column would give York ~1.38% instead of 0.87%; both are under 2%. The
"under 2%" claim survives 2022 and 2023 and fails only for 2019-21, exactly as
the couplings block in `build_submission.py` already records.

**Nuclear is never marginal in the day-ahead market.** Table 3-71: Uranium Steam
is **0.0% of day-ahead marginal resources in 2021, 2022, and 2023** (0.1% in
2019, 0.2% in 2020). So a day-ahead marginal convention gives Lake Anna ~0%.

But day-ahead marginal shares are *unusable* for a physical water calculation:
Table 3-71 shows marginal resources in day-ahead are **84.8% virtual
transactions** in 2023 (UTC 50.1%, DEC 18.0%, INC 16.7%), with physical
generation only 15.0%. Virtual transactions burn no fuel and consume no water.
**Using the real-time marginal mix is therefore the correct methodological
choice, and this table is the citation for why.** Worth one sentence in the
methods and a ledger entry — it converts an unexplained choice into a defended
one.

Supporting: "In general, **fuel costs make up between 80 percent and 90 percent
of short run marginal cost**" (p.202) — the reason marginal units are gas.
And nuclear dispatch (Table 3-12, logged in Part 9): 90.1% must-run, 6.6% at
economic minimum, only 3.3% dispatchable.

### 16.5 Read in full, nothing load-bearing (logged so the record is honest)

Aggregate/day-ahead supply and demand curves and duration tables (3-2 to 3-11);
generator offer behavior, ICAP must-offer, emergency maximum MW, parameter
limited schedules and unit-specific exceptions (3-12 to 3-19); virtual offers,
INC/DEC/UTC volumes, ownership, profitability and the MLSA manipulation cases
(3-20 to 3-30, 3-46 to 3-52); LMP levels, DLMP-vs-PLMP fast-start pricing, price
convergence, and all inflation-adjusted price series (3-31 to 3-45, 3-53, 3-54);
transmission constraint penalty factors and control-limit reductions (3-55 to
3-61); fuel prices and LMP components (3-72 to 3-79); shortage pricing, ORDCs,
reserve shortage intervals, SMP capping (3-80 to 3-90); HHI, pivotal suppliers,
merger reviews, TPS testing and offer capping (3-91 to 3-112); markup indices,
fuel cost policies, cost-based offer penalties, VOM and Manual 15 issues
(3-113 to 3-143).

Two incidental items worth keeping:
- **Nuclear costs, p.254:** "The fuel costs for nuclear plants are fixed in the
  short run... **The short run marginal cost of fuel for nuclear plants is
  zero.**" This is the mechanism behind the 0.39-0.62% marginal share, stated
  outright. Better citation than the dispatch-status table alone.
- **Heating/cooling degree days, Table 3-8** (already used in Part 11 to
  back-calculate a ~0.76 baseload against our swept 0.10-0.50) — re-read, values
  confirmed: 2023 CDD 1,081.8 vs 2022 1,273.0, −15.0%.

---

## Part 17 — a new external check on the fleet, and a 2x discrepancy

Chaining JLARC Chapter 1 (Part 15.1) gives an independent top-down estimate of
Prince William's data-center load: **~840-855 MW** (5,050 MW statewide from
utility peak-load forecasts; Loudoun ~half; Loudoun 3x Prince William — and the
"3x" is corroborated by JLARC's own site counts, Loudoun 71 vs PWC 24, ratio
2.96).

Recomputed from the shipped model today:

| | effective IT MW | x PUE = site load |
|---|---:|---:|
| 54 completed | 1,358.5 | **1,699.1 MW** |
| all 243 | 6,468.5 | 8,000 MW |

**Our 54 completed buildings imply ~1,700 MW against JLARC's ~845 MW. We are
about 2x high on the point estimate.**

What this does and does not affect:

- **It does not touch any share in the abstract.** Re-ran the totals: Scope 2 is
  87.7% delivered / 88.5% consumptive, on-site 3.2% delivered / 2.4%
  consumptive, all 243 = 49.60 MGD, 54 = 10.49 MGD. Every headline number
  reproduces exactly. Because all three scopes scale with the same power
  estimate, a uniform factor cancels out of 88%, "under 3%", ">40%", and
  "under 2%". The abstract already says this in as many words.
- **It does affect the plain-language summary's absolute volumes** — "10 million
  gallons per day" and "could reach 50 million" would be ~5 and ~25 on the JLARC
  anchor.
- **It is inside our own stated uncertainty.** +/-60% on 1,699 MW is
  [680, 2,718], which contains 845. So this is not an inconsistency with what we
  have published; it is the external anchor landing near the low edge of our band.

Candidate explanations, not yet resolved:
1. **Vintage.** JLARC's 5,050 MW is the *2024* forecast made in *August 2023*.
   Our inventory is current county records, and JLARC calls Prince William "the
   fastest-growing locality," with statewide space having "more than doubled"
   since 2020 and 1,500 MW under construction. Some of the gap is real growth.
2. **The 0.4 derating (redundancy 0.5 x utilization 0.8) may be too generous**,
   or permitted backup generator capacity may overstate IT load more than ICPRB
   Eq 6-3 assumes. Note the independent hint from JLARC p.50: Dominion "will only
   build new transmission to serve 1,000 MW if that is the forecasted metered
   load" even when customers request 2,000 MW — a ~2x request-to-metered ratio in
   the utility's own planning, which is the same order as this discrepancy.
3. **"Completed" is a construction status, not energization** — already a known
   coupling. Buildings finaled but not yet at full IT load would push our
   estimate above metered reality.

**ACTION (paper, not AGU):** run this down properly. It is the strongest external
check on the *level* we have found — every prior validation tested distributional
shape, not magnitude. Until it is resolved, absolute volumes should carry the
JLARC anchor as a stated comparison, and the PLS's "10 million gallons" should
either gain a range or be re-scoped.

---

## Part 18 — the five PDFs I had never opened

### 18.1 `ICPRB.DataCentersandWaterUse.ICPRB_.March2026.pdf` — READ THIS FIRST

**This is the single most important document in the corpus and I had never opened
it.** Two pages, published **March 2026**, by A. Seck with R. Bourassa, C. Schultz
and M. Nardolilli — the "overlapping paper" flagged as an open item. It is not
forthcoming; it is published, and it has been for five months.

**It names our framework, in our terms, and explicitly excludes it:**

> "While this study focuses on direct, on-site consumption, data centers also
> have an **'indirect' water footprint (often referred to as Scope 2 and 3)**
> through the water required to generate the electricity they consume and the
> water used in the lifecycle of their hardware."

Two consequences, opposite in sign:

1. **Our abstract's central comparison is now verified in the source's own
   words.** "The regional water authority's own assessment of the host Potomac
   basin is nonetheless limited to Scope 1" is no longer an inference from what
   ICPRB's tables contain — ICPRB says it. Quotable verbatim.
2. **We cannot claim the scope framing as our own contribution.** ICPRB got to
   the Scope 1/2/3 framing first, in public, in March 2026. Our contribution is
   that we *compute* Scopes 2 and 3 at facility level and show the
   accounting-convention flip. That is still novel and still worth publishing —
   but the framing must be cited, not presented as new. **ACTION: cite this in
   the abstract or at minimum in the paper; do not let a reviewer find it first.**

**It resolves the 800 gal/MW/day open item, verbatim:**

> "Nominal site-level water use intensity values can range between
> **100-1,600 gallons/day/MW** on average, depending on cooling technology, and
> can reach up to **8,500 gallons/day/MW at peak** for facilities using
> evaporative cooling. The estimated **regional average WUP for all existing data
> centers in the basin is 800 gallons/day/MW with an assumed consumptive-use
> factor of 75%.**"

So 800 is a *regional fleet average*, not a technology tier and not an average of
309 and 1,006. That closes the discrepancy. The 0.75 consumptive factor is
confirmed. **But their peak is 8,500 gal/MW/day; ours is 3,060.** That is a 2.8x
gap on the peak tier and is not yet reconciled. **ACTION.**

**It contradicts its own technical appendix on seasonality.** The fact sheet says
"Monthly use in summer can be **close to three times** the average annual demand
while peak daily use can be as much as **10 times**." The 2025 WMA Study Appendix
A.3-2 caps the observed monthly factor at **1.8** (logged in Part 11, where I
corrected my own earlier claim). Our seasonal shape is 3.04x. **The fact sheet
supports our 3.04x; the technical table does not.** This is the same
summary-vs-table failure mode that produced three earlier errors — except this
time the summary agrees with us. Do not simply take the win: state that the two
ICPRB documents disagree and that we follow the fact sheet.

**Scale numbers for the whole Potomac basin (their Figure 1 / FAQ):**
- "over **290 individual buildings** in the basin"
- total power demand "estimated at about **5,400 MW**"
- total floor space "estimated at **56 million square feet**"
- "**Over 100 million square feet** of additional data center development is
  currently planned"
- "about **40%** [of facilities] exclusively rely on air cooling"
- data centers "hold **no direct withdrawal permits**" (corroborates JLARC's
  "only two")

**5,400 MW / 56M sq ft = 10,370 sq ft per MW.** Our estimator uses **8,818**.
Independent corroboration of the floor-area-to-power conversion within 15% —
and ours is the denser (higher-power) end.

**Current impact, their numbers:**
- Upstream of WMA intakes: <0.1 MGD average, ~0.3 MGD peak
- Within WMA: ~4 MGD average 2025, ~15 MGD peak
- Data centers = **1% of WMA withdrawals, 9% of annual consumptive use, up to
  12% of summer consumptive use**
- Basin-wide: **0.3% of withdrawals, 3% of consumptive use**
- Projected 2050: WMA ~22 MGD avg / >80 MGD peak; upstream ~5 MGD / ~17 MGD peak

**Methodology — and a circularity we must disclose:** they derived facility power
from "a database developed by the Virginia Joint Legislative Audit and Review
Commission (JLARC), using **Virginia Department of Environmental Quality (VADEQ)
air permits**." That is *our* power source too. ICPRB is therefore **not an
independent check on our power estimates** — we share the input. What *is*
independent is their calibration against utility-reported actual water use in
Loudoun Water and Prince William Water service areas. **ACTION: state this
non-independence explicitly; it is the same trap as the 309 circularity.**

And it sharpens Part 17: if we and ICPRB use the same permits but differ ~2x,
**the difference is in the derating, not the data.**

**Their policy findings, directly usable:**
> "Data centers in the Potomac Basin are typically supplied by public water
> utilities rather than self-supplied and therefore **do not fall under existing
> consumptive use regulations and mitigation requirements**."

> "lower-water cooling approaches often **increase energy use**" — the same
> Scope 1 / Scope 2 tradeoff JLARC Appendix J names.

### 18.2 `Dominion_GS-5_LargeLoad_RateClass.pdf` (May 2026) and `Dominion_LargeLoad_SCC_PUR-2026-00011.pdf` (filed 2 Feb 2026)

- **70,000 MW of large-load delivery-point requests in Dominion's queue**:
  25,000 MW with assigned energization dates through 2031, plus 45,000 MW batched
  and under study. "**nearly triple the DOM Zone's current all-time peak of
  24,678 MW, recorded on January 23, 2025**." ~10 new requests/month = 2,000-3,000
  MW/month. Each request capped at 300 MW; batches ~10 requests / 2-3 GW.
- **The GS-5 rate class takes effect 1 January 2027.** 14-year contract term with
  a 4-year ramp; exit fees equal to unexpired minimum demand charges.
- **Minimum demand charges: 85% of *contracted* demand for transmission and
  distribution, 60% for generation.** Customers may shed 20% of contracted demand
  with 36 months' notice, or up to 50% if reallocated.

That last bullet is the second independent hint that **contracted/permitted
capacity systematically exceeds metered load** — the utility prices in a 15-40%
gap and lets customers hand back up to half. Together with JLARC p.50 (Dominion
builds for 1,000 MW against 2,000 MW requested), that is three separate sources
pointing the same direction as our 2x overestimate.

**DOM Zone all-time peak 24,678 MW** is a hard dated anchor. Our 54 completed
buildings at ~1,700 MW would be 6.9% of the entire Dominion Zone peak, from one
county — and 31% of ICPRB's 5,400 MW for the *entire Potomac basin*, which ICPRB
says is "predominantly located within Loudoun County." That is not credible. The
2x (or more) overestimate is now corroborated by a second independent source.

### 18.3 `LBNL_QueuedUp_2025.pdf` (December 2025, data through end-2024)

Generator interconnection, not load — so indirect, but it lands on the long-run
marginal argument hard.

- **PJM active queue: 1,942 requests, 211.5 GW.** Active **nuclear in PJM: 44 MW.**
  US-wide active nuclear is only ~5.3 GW, almost all in the non-ISO Southeast and
  West.
- Gas is the only category growing: **+72% year-over-year to 136 GW** active,
  while solar -12%, storage -13%, wind -26%.
- **Only 13% of capacity (19% of projects) that requested interconnection
  2000-2019 had reached commercial operations by end-2024; 77% withdrew.**
- Even after signing an interconnection agreement, **36% of IAs (43% of capacity)
  signed 2000-2021 had withdrawn**.
- Median request-to-operation is now **55 months**; 200+ MW projects ~56 months.

**The tension this creates, which is worth a paragraph in the paper:** JLARC's E3
capacity-expansion model attributes +24 TWh/yr of new Virginia *nuclear* to data
centers by 2040 (Part 15.2). LBNL's *observed* queue has **44 MW of nuclear
active in all of PJM** and gas as the only growing category. The long-run
marginal answer therefore depends on whether you believe a capacity-expansion
model or the interconnection queue — and they disagree about which fuel responds,
which means they disagree about water intensity and about which basin. Gas CC and
nuclear have very different water profiles and very different locations.

The 13% completion rate is also the closest available empirical base rate for
"most approved things don't get built" — relevant to how the 243-building
full-buildout scenario should be framed, with the caveat that generator
interconnection and data-center construction are different processes.

### 18.4 `EconBulletin_LaunchCost_2022.pdf` — read cover to cover, confirmed irrelevant

"An analysis of launch cost reductions for low Earth orbit satellites," Adilov,
Alexander, Cunningham & Albertson, *Economics Bulletin* 42(3):1561-1574. Per-kg
LEO launch costs, 2000-2020, UCS satellite database, Newey-West regressions.
Zero connection to water, data centers, or Virginia. **Confirmed: remove from the
RAG index.**

---

## Part 19 — the county policy documents, and the mechanism behind the 2x

### 19.1 `PP-NewStructure-DataCenterBuildings.json` — this explains Part 17

Prince William County Development Services, Building Development Division,
"New Structure - Data Center Buildings," effective **5 April 2021**. Four pages.
The operative passage:

> "A New Structure - Data Center Building will be permitted as one Building
> Permit resulting in one Certificate of Occupancy... **The building areas that
> are not intended for immediate use will be designed to meet the Storage (S-1)
> Use Group's minimum requirements.** The designer may also include the Business
> (B) Use Group in the area not intended for immediate use.
>
> **After the Certificate of Occupancy is issued, an Alteration/Repair Building
> Permit will be issued to convert or "fit-out" the unused Storage (S-1) Use
> Group and Business (B) Use Group areas.**"

**This is the mechanism behind the 2x discrepancy, in the county's own written
policy.** A data-center building receives its Certificate of Occupancy — and
therefore `BuildingStatus = Completed/Finaled` in the records we use — **while an
arbitrary fraction of its floor area is still permitted as empty storage.** The
data halls are populated later, under separate Alteration/Repair permits.

Our estimator applies a full IT power density (8,818 sq ft/MW) to the whole
assessed floor area of every "Completed" building. By county policy, part of that
floor area is, at CO, explicitly *not* data-center space yet.

This upgrades the existing "completed ≠ operating" coupling in
`build_submission.py` from "no field indicates energization" to something much
stronger: **the county affirmatively states that CO is granted with unfitted-out
area, and defines a separate permit type for the fit-out.**

**And it points at a fix.** The `eportal_cooling_permits` field already carries
Mechanical Commercial permits (e.g. VA1 has `MEC2025-00404`). Those
Alteration/Repair and mechanical permits are plausibly the *fit-out signal* — a
way to estimate how much of each building is actually built out, rather than
assuming 100%. **ACTION: test whether MEC/ALT permit counts or dates predict the
gap. This is the most promising route to fixing the level error.**

Also from the same policy, the county's own definitional threshold: a Data Center
Building houses equipment managing "**at least one megawatt** of capacity of
electrical power and cooling."

### 19.2 `prince_william_cesmp_full.json` — Community Energy and Sustainability Master Plan, October 2023, 199 pages

Read pages 1-70 in full (Glossary through Appendix A start) plus Appendix D/E
(pp. 130-134). **Pages 71-129 and 135-199 are Appendix A's action table, Appendix
B implementation roadmaps and budget tables, Appendix C mapping tables, and
Appendix F/G — not read line by line. Stated plainly rather than claimed.**

What matters for this paper:

**PWC is served by BOTH Dominion and NOVEC — from the county's own plan.** Action
E.1 (Community Choice Aggregation): "further legal review is needed to determine
if a CCA could be formed **in Dominion Energy's territory and NOVEC's
territory**." Chapter 5 repeats it: the low action scenario assumes a CCA "is
only enacted in Dominion territory," the high scenario "for both Dominion and
NOVEC territory." **This settles the open question from Part 15.2: the
Dominion-only generation mix is definitely incomplete for this county.**

**Market-based Scope 2 is already live here — a fourth convention.** Page 26,
"Impact of Data Centers": "**some existing data centers in the county are already
procuring 100% clean electricity for their operations.**" Action E.4: "**Both
Dominion and NOVEC offer 100% renewable electricity options.**" Chapter 5 lists
VPPAs and Green-e certified unbundled RECs as county tools.

Our `scope2_electricity.accounting_basis` is `'location_based'` with
`market_based: None`. The GHG Protocol requires *both* be reported. So the
convention count is now at least four:

| # | Convention | Lake Anna share of Scope 2 |
|---|---|---|
| 1 | Location-based, utility-average (Dominion mix) | >40% |
| 2 | Location-based, market-average (PJM mix, 33.3% nuclear RTO-wide) | far lower |
| 3 | **Market-based** (PPAs/VPPAs/RECs — already in use here) | ~0 for operators at 100% clean |
| 4 | Short-run marginal (PJM real-time marginal fuel shares) | ~1% |

Four standard conventions, spanning >40% to ~0%, for the same physical
electricity. That is a substantially stronger version of the paper's thesis than
the two-convention version in the current abstract.

**The county counts nuclear as renewable.** Glossary and Table 2 footnote:
"renewable electricity is being defined as electricity coming from any non-fossil
fuel energy source, such as solar, wind, hydro, geothermal, **and nuclear**." So
the county's "100% renewable by 2035" goal can be met *with more North Anna* —
which would *increase* Lake Anna water. Another energy-water tradeoff, and a
sharp one: the county's decarbonisation goal and its water exposure point in
opposite directions.

Other items:
- 2018 county emissions: 37% transportation, **30% commercial energy**, 23%
  residential. Commercial building electricity forecast to be "**roughly 28% of
  county-wide emissions by 2030**" (Action E.3, whose named Primary Partners are
  "**Businesses and Data Centers**").
- Business-as-usual forecast explicitly includes "**Digital Gateway growth**."
- Action **B.2 Green Zoning** proposes regulations "to encourage **energy- and
  water-efficient** buildings" — water named in a zoning action.
- Board **Directive January 2023** created a Data Center Ordinance Advisory Group.
- Emissions forecast to rise 37% (2005-2030) and 57% (2005-2050) BAU.
- Appendix D p.132: "The Prince William County Service Authority (PWCSA) and
  **Virginia American Water** is in coordination with **Fairfax Water** to secure
  supply." Confirms the two-supplier structure behind the 1.18x PWW denominator
  correction.

### 19.3 `Res No 20-773`, `PP-AddressValidationRequirements.json`

Res. 20-773 (17 Nov 2020, adopted 5-3): endorses MWCOG's 50%-below-2005-by-2030
goal and directs the Comprehensive Plan to carry 100% renewable county-wide by
2035, county government 100% renewable by 2030 and carbon neutral by 2050. This
is the authorising resolution behind the CESMP. Ayes: Angry, Bailey, Boddye,
Franklin, Wheeler. Nays: Candland, Lawson, Vega.

Address Validation Requirements (eff. 2013, rev. 2021): administrative; GTS
assigns addresses before building permits issue. Relevant only in that it
confirms address/GPIN provenance for the building inventory.

### 19.4 `README.txt`

iNaturalist export header for `observations-759582.csv`. Query:
`quality_grade=research&identifications=any&place_id=744&taxon_id=20978&d1=2020-01-01&d2=2026-07-16`,
exported 2026-07-16. Documents 40 columns. Establishes that the biodiversity
layer is research-grade observations of one taxon in one place over 2020-2026.

---

## Part 20 — the fit-out correction, implemented

The mechanism found in Part 19.1 is now in the model.

**What was wrong.** Every rung of the power ladder measures *installed capacity*.
PWC's building policy grants a Certificate of Occupancy with unfitted floor area
permitted as Storage (S-1), deferring data-hall fit-out to a separate
Alteration/Repair permit. So `BuildingStatus = Completed` marks the START of
fit-out. The model was applying full IT density to floor area that is, by the
county's own policy, not yet data-center space.

**What I tried first and abandoned.** The obvious fix was to use the
`eportal_cooling_permits` (MEC/ALT) already in the profiles as a per-building
fit-out signal. It does not work: only **10 of 54** occupied buildings carry any,
and those are **site-level duplicates** (IAD73 and IAD74 share an identical
list). Recorded here so nobody spends the afternoon on it again.

**What works.** `OCCDate` in `Data_Center_Buildings.geojson` — the actual
Certificate of Occupancy timestamp, populated for all 54. **22 of 54 (41%)
received their CO in 2024-2026.** Ramp length comes from Dominion's own contract
structure for these customers: GS-5 runs a 14-year term "inclusive of a
**four-year ramp period**." Linear to full load over 4 years, bounds at 3 and 5.

**Scoping rules, both deliberate:** only buildings that reached a CO are ramped
(no CO = nothing to ramp; ramping an unbuilt building would conflate "not built"
with "filling up"), and a missing date means no ramp, so a data gap can only make
the estimate larger.

**Result — the level now reconciles.** Vintage-matched to JLARC's 2024 snapshot:

| | site load | vs JLARC ~842 MW |
|---|---:|---:|
| unramped | 1,033 MW | 1.23x |
| **ramped** | **779 MW** | **0.93x** |

The apparent "2x" was two things compounding: 20 of 54 buildings were occupied
*after* JLARC's snapshot (vintage mismatch), and the rest was fit-out.

ICPRB cross-check: PWC as a share of the 5,400 MW Potomac basin falls from
**31.4% to 21.3%**, now consistent with ICPRB's "predominantly Loudoun."

**What moved and what didn't:**

| | pre | post |
|---|---:|---:|
| 54 occupied, energized IT | 1,358.5 MW | **920.8 MW** (68%) |
| 54 occupied, total | 10.49 MGD | **7.09 MGD** |
| all 243, total | 49.60 MGD | **46.19 MGD** |
| MC median / 90% CI | 53.6 / 44.5-64.9 | **49.9 / 41.4-60.5** |
| Scope 2 share (54) | 87.7 / 88.5% | 88.0 / 88.7% |
| on-site share (54) | 3.2 / 2.4% | 2.9 / 2.2% |

**The abstract needed no numeric change** — it quotes only shares, and the ramp
multiplies IT power which every scope is proportional to. "88%", "under 3%",
">40%", "under 2%", "±60%" all hold. "Under 3%" is now true on *both* the
delivered and consumptive basis, where before it held only on consumptive.

The plain summary did change (it quotes volumes): 10 -> **7** million gal/day
today, 50 -> **45** million at full buildout, with one clause explaining why.
197/200 words.

**Shipped:** ramp + provenance in `indirect_water_footprint.py`; `_occupancy_date`
in `build_facility_profiles.py`; `validate_occupancy_ramp.py` (6 steps, all pass);
harness **check 20**; 6 ledger entries (27 total); METHODOLOGY **62**; couplings
and NUMBERS blocks in `build_submission.py`.

**Fault-injected, three ways, all caught:** ramp silently removed; ramp leaking
into one scope (uniform scaling — the first version of the check MISSED this, so
the share test was rebound to the abstract's actual claims rather than to
ramped-vs-unramped self-consistency); ramp wrongly applied to unbuilt buildings.

**Harness 21/21.**

**What this does not fix, stated in METHODOLOGY 62.6:** the ramp is a shape
assumption, not a measurement — real fit-out is likely stepwise, not linear. The
ICPRB comparison is not fully independent (shared VADEQ permit input). And the
residual is well inside the ±60% band, so this removes a systematic bias without
narrowing the interval. Only load disclosure does that.

---

## Part 21 — CESMP, pages 71-143 (continuing; 143-199 still to read)

### 21.1 A FIFTH grid convention — and it is the county's own

Appendix F.2, "Electric Grid Resource Mix," p.139. The county does its GHG
accounting on **EPA eGRID data for the SERC Virginia/Carolina subregion**:

| Year | Coal | Oil | Gas | Other fossil | **Nuclear** | Hydro | Biomass | Wind | Solar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2018 | 19.1% | 0.6% | 34.6% | 0.1% | **37.8%** | 2.3% | 2.8% | 0.4% | 2.2% |
| 2021 | 13.4% | 0.2% | 38.1% | 0.2% | **38.8%** | 1.9% | 2.3% | 0.4% | 4.7% |

Our Scope 2 uses a **Dominion** mix. The county uses **eGRID SERC VA/Carolina**,
which is a different geography again — it spans Virginia *and* the Carolinas, so
its 38.8% nuclear includes Duke's North Carolina fleet, not just North Anna and
Surry. More nuclear in total, but spread across far more plants and two states.

So the convention count is now **five**, not four:

| # | Convention | Nuclear basis | Lake Anna share of Scope 2 |
|---|---|---|---|
| 1 | Dominion utility-average (ours) | Dominion fleet | >40% |
| 2 | PJM RTO-wide average | 33.3% RTO | far lower |
| 3 | **eGRID SERC Virginia/Carolina** (the county's own) | 38.8% two-state | different again |
| 4 | Market-based (PPAs/VPPAs/RECs) | contractual | ~0 for 100%-clean buyers |
| 5 | Short-run marginal (PJM real-time) | 0.39-0.62% marginal | ~1% |

Convention 3 has *official local standing*: it is what Prince William uses to
measure progress against its own Board-adopted goals. A paper arguing that
accounting convention decides which basin is implicated now has a case where the
regulator's own chosen convention is a third distinct answer. **ACTION: compute
Lake Anna under eGRID SERC VA/Carolina; it belongs in the convention table.**

### 21.2 The county's only water-demand action is rated Low

Appendix A, p.81. Of 60 CESMP actions, exactly one targets commercial/industrial
water demand:

> **A.21: Encourage Businesses to Reduce Water Usage.** "Develop incentives,
> training and technical assistance programs for significant water use reductions
> including rainwater and greywater harvesting and onsite blackwater treatment
> **with a focus on industrial and commercial properties.**" — Priority: **LOW**.

Low priority is defined in the plan as actions that "address emissions sources
within the county and fill in potential policy/programmatic gaps, but have much
lower GHG reduction or climate risk reduction impacts" or "were not favored (or
were disfavored) by stakeholder groups."

Water-adjacent actions that *did* rank High: A.2 stormwater flooding, A.5 stream
restoration, A.6 (residential retrofits, mentions "reduce water use"). B.2 Green
Zoning proposes "energy- **and water-** efficient buildings" — Medium.

**The county's climate plan ranks industrial water-demand reduction at the bottom
of a 60-action list, in the county with the fastest-growing data-center water
demand in the basin.** That is a concrete, citable policy gap, and it pairs
exactly with ICPRB's finding that utility-supplied data centers "do not fall under
existing consumptive use regulations."

### 21.3 The county already knows it cannot get the data

Action E.3 implementation steps, p.94 — the plan's own text:

> "Collaborate with data center companies/developers to discuss… **Request
> disclosure** of clean energy generation/purchasing, emissions and offset
> information… **NOTE: There may be limitations on obtaining energy use and/or
> equipment information from data centers**"

> "Develop a **voluntary** reporting program to communicate data center clean
> energy development/usage and emissions reduction progress to the public"

And its performance indicator (p.95) is literally:

> "**% of data centers disclosing energy or emissions information**"

This is the disclosure argument, made by the county about itself, in advance: the
mechanism is voluntary, the county flags up front that it may not work, and it
proposes to measure the non-disclosure rate. Also p.94: "**Data centers are
already granted expedited plan reviews/inspections by County as they are targeted
industry/priority development**" — the county's existing lever is an accelerator,
not a condition.

### 21.4 Scale and structure

- Table F.1, 2018 inventory (total **5,044,135 MTCO2e**): **commercial
  electricity 1,359,354 MTCO2e = 27%** of all county emissions; residential
  electricity 14%. Electricity is **41%** of the county total. On-road transport
  32%.
- 2005 baseline 4,190,056 MTCO2e; 2018 is **+20%** against a goal of −26% by
  2018 to stay on track. The county states plainly it is "not currently on track."
- Appendix F.3: "92% clean electricity" alone supplies **57%** of all reductions
  needed by 2030 — by far the largest single lever, and the one data centers
  dominate.
- Appendix F.4: Virginia RPS requires 30% renewables by 2030 (Phase I) / 41%
  (Phase II). External forces supply ~32% of needed reductions.
- CCA (E.1) budget $4-5M, start-up $3.7M referenced from Loudoun's feasibility
  study; E.3 (the data-center action) budget **$1M-$10M**, the widest range in the
  plan. Total high-priority programme 2025-2050: **$432M-$862M**.

### 21.5 Water items in the existing-actions appendix

- p.127: "**Plant effluent water reuse is utilized within the water treatment
  plant which helps to reduce potable water usage by 1.5 million gallons per
  day.**" The county already recycles 1.5 MGD internally — useful scale reference
  against a 7.09 MGD fleet estimate.
- p.129: "Our county landfill currently captures methane and uses it to produce
  approximately **6.7 MW of electricity to NOVEC** annually." Second confirmation
  of the NOVEC relationship.
- p.132: PWCSA + **Virginia American Water** coordinating with **Fairfax Water**
  to secure supply — the two-supplier structure behind the 1.18x PWW denominator.
  PWCSA runs 1,150 miles of sanitary sewer and is rebuilding the **H.L. Mooney
  Advanced Water Reclamation Facility** headworks for higher peak flow.

### 21.6 Read but not load-bearing

Appendix B.3 implementation roadmaps for E.1-E.5, B.1-B.5, T.1-T.7, N.1, A.1-A.7
(pp. 89-122): lead departments, steps, budgets, performance indicators. Appendix C
mapping tables to Comprehensive/Strategic Plan strategies (pp. 123-126). Appendix D
existing actions (pp. 127-132). Appendix E stakeholder rosters (pp. 133-135).
Appendix F.1/F.3/F.4 (pp. 137-141). Read in full; only the items above bear on
this paper.

**STILL TO READ in this file: pages 143-199, Appendix G Vulnerability Assessment
Report.**

---

## Part 22 — CESMP pages 143-199 (Vulnerability Assessment + End Notes). FILE COMPLETE.

Appendix G is a separate consultant report: **AECOM, "FINAL Vulnerability
Assessment Report, Prince William County," 9 January 2023**, 47 numbered pages.
Method is FHWA's VAST framework (exposure x sensitivity x adaptive capacity),
future conditions from AECOM's FLEx tool over 32 LOCA-downscaled GCMs, RCP4.5 and
RCP8.5, horizons 2050 and 2075 against a 1950-2005 baseline.

### 22.1 End Note 17 — the county states this paper's thesis, for carbon

Page 198, End Note 17, in full:

> "Currently, MWCOG uses a **location-based method** to calculate electricity
> emissions, which uses an average electricity emissions factor that reflects
> energy sources used throughout the regional grid. Alternatively, the
> **market-based method** allocates electricity emissions from energy generators
> to consumers based on '**contractual instruments**.' The emissions reduction
> impact of any clean electricity purchasing recommendation in the CESMP, such as
> community choice aggregation or purchasing RECs, **would not be reflected
> through the location-based accounting method, but would be reflected through
> the market-based method.** The County will work with MWCOG to determine if the
> market-based electricity emissions can be calculated along with location-based
> emissions in the future."

The county is saying, about its own flagship climate action: **the same physical
electricity produces a different accounted answer depending on the convention,
and its entire CCA/REC programme is invisible under one and visible under the
other.** That is this paper's argument, stated by the regulator, in a footnote,
about carbon.

**Why this is a gift rather than a scoop.** Carbon accounting has already
absorbed the problem: the GHG Protocol requires **dual reporting** of
location-based and market-based Scope 2, and the county here commits to doing
exactly that. **Water has no equivalent norm.** So the framing for the paper is
no longer "look, conventions differ" — it is "carbon solved this with mandatory
dual reporting; water has not, and for water the divergence is *geographic*, not
just numeric, because it decides which basin and therefore which regulator." That
is a sharper and more defensible contribution than the current abstract claims.

**ACTION: rewrite the closing move around this.** Cite End Note 17 and the GHG
Protocol dual-reporting requirement.

End Note 23 confirms the eGRID source for Appendix F.2 (Part 21.1). End Note 5
reconfirms nuclear counted as renewable.

### 22.2 Drought: the numbers behind "Medium"

Table 7, change in average months per year in drought:

| PDSI class | RCP4.5 2050 | RCP4.5 2075 | RCP8.5 2050 | RCP8.5 2075 |
|---|---:|---:|---:|---:|
| Mild (-1 to -2) | +2% | +1% | +3% | -4% |
| Moderate (-2 to -3) | **+43%** | **+56%** | **+39%** | **+67%** |
| Severe (-3 to -4) | **+114%** | **+182%** | **+151%** | **+350%** |
| Extreme (< -4) | **+201%** | **+434%** | **+393%** | **+1534%** |

Mechanism, in the report's own words: "large increases in extreme precipitation
indicators combined with relatively small increases in average annual
precipitation indicators suggest that **precipitation will fall in more intense
bursts followed by longer dry periods**."

**This bears directly on `seasonal_basin_surface.py`.** Our Broad Run July figure
(28.3% of low-month flow) is computed against a *historical* low-flow denominator.
Severe-drought months rising 114-350% means that denominator shrinks in exactly
the season our demand peaks. **ACTION: at minimum state this; ideally sweep the
low-flow denominator.**

And the demand side moves the same way: Table 6 has days >=95 F rising **+13 to
+15 by 2050** (+296% to +351%) and **+21 to +32 by 2075**. More CDD is more
evaporative cooling. Both blades of the scissors close.

### 22.3 Water supply is rated HIGH sensitivity — to drought and to heat

Section 4.3.3: Food, Water and Shelter gets a **High** sensitivity rating for
drought — "water resources are significantly impacted by drought conditions.
When drought conditions persist for extended periods, drinking water restrictions
may be triggered." Section 4.3.2 gives it **High** sensitivity to extreme
temperature — "extended periods of extreme temperature can make **drinking water
resource management significantly more challenging**." Adaptive capacity is
capped at Medium because these assets "lack significant redundancy and have
inherent limitations to their ability to adapt (e.g., **reservoir storage**)."

The category still lands at **Medium overall** only because *exposure* is scored
Low (2050) / Medium (2075). So: high sensitivity, limited adaptive capacity,
saved by an exposure score. Set that against Part 21.2 — the county's only
industrial water-demand action is rated **Low priority**.

Socially Vulnerable Populations get **High** drought sensitivity for a reason
worth quoting: they "have fewer resources available to alleviate drinking water
restrictions and may have **increased water demand** due to increased exposure to
extreme temperatures." 24 of 26 Equity Emphasis Areas are exposed to the
precipitation hazard.

### 22.4 Data centers are classified as "Communications" — and rated Low

Section 3, Communications: the category "will focus on the infrastructure
components of communication including radio towers, **data centers**, financial
service locations, cable systems and broadcast facilities, and wireless service
towers." Communications scores **Low combined vulnerability in both 2050 and
2075** — the joint-lowest of eight categories.

The assessment is strictly one-directional: it asks what climate threatens the
asset, never what the asset does to other assets. So in the county's own risk
framework a data center is a low-vulnerability communications node, while the
water supply it draws on is a separately-assessed high-sensitivity asset. **The
framework cannot see the link this paper is about.** That is a clean, citable
statement of the institutional gap.

### 22.5 Physical inventory numbers worth keeping

From Tables 21-22 and Section 3 — the county's own counts for layers we also hold:

| Asset | Count / extent | % exposed to precipitation hazard 2050 / 2075 |
|---|---|---|
| Streams | **1,040 miles** | 59% / 59% |
| Resource Protection Areas | **50 sq mi** | 42% / 43% |
| Tree cover | **187 sq mi** (54% of county) | 10% / 11% |
| Agricultural areas | 36 sq mi | 14% / 15% |
| Dams | 10 (of 21 in DCR inventory) | 90% / 90% |
| Building footprints | **200,310** | 2% / 4% |
| Apartments | 534 | 5% / 6% |

RPAs are defined as land within 100 ft of a perennial stream bank or adjacent
wetland edge — the same definition behind our `water_context.rpa` flag. **Streams
at 1,040 mi and RPAs at 50 sq mi are direct cross-checks on `Stream.geojson` and
`Resource_Protection_Areas_(RPA).geojson`** when I get to them.

Other: population 482,000 (2020 census). 21 dams in the DCR Dam Safety Inventory,
5 with significant hazard potential; Upper Occoquan Dam (Fairfax County Water
Authority) is used for hydroelectric generation *and* water supply. Drinking water
comes from **Virginia American Water or PWCSA**, or private wells — the
two-supplier structure again. **Dominion's Possum Point facility** is named as a
coastal asset near the shoreline — a generating station inside the county.
Lake Jackson Dam was damaged in the 2011 Mineral earthquake ($900k repair).

### 22.6 Read, not load-bearing

Sections 2.5-2.7 (coastal flooding, SLR projections to 2100, earthquakes, wind/
tornadoes), Section 3 asset definitions for all eight categories, Section 4's
per-hazard vulnerability narratives for Safety and Security, Health and Medical,
Communications, Transportation, Energy and Hazardous Materials, Natural Resources
and Socially Vulnerable Populations, Section 6 rating tables 24-28, and Section 7
references. Read in full.

**`prince_william_cesmp_full.json` is now COMPLETE — all 199 pages.**

---

## Part 23 — acted on Parts 21-22 (harness 22/22)

**1. Abstract closing rewritten to the strong claim.** Was: "two equally standard
conventions disagree about which watersheds are implicated." Now:

> "Water-management frameworks must therefore reach beyond on-site use to the
> electricity supply chain. Carbon accounting already requires dual location- and
> market-based reporting; water has no equivalent norm, and here the divergence
> is geographic, moving which basin, and which regulator, is implicated. Which
> basin is held responsible is set by convention, not measurement."

1990/2000 excl. spaces, 10 spare. Better because it is falsifiable (a
dual-reporting norm for water exists or does not), constructive (names the
remedy), and rests on the regulator's own End Note 17 plus the GHG Protocol
rather than only on our arithmetic. METHODOLOGY 63.1.

**2. Low-flow denominator now swept, not assumed stationary.**
`DROUGHT_FLOW_SWEEP = (1.00, 0.90, 0.80, 0.70)` on the observed monthly flow:

| watershed | x1.00 | x0.90 | x0.80 | x0.70 |
|---|---:|---:|---:|---:|
| **Broad Run (Jul)** | **28.3%** | 31.4% | 35.3% | **40.4%** |
| Bull Run (Jul) | 2.6% | 2.9% | 3.2% | 3.7% |
| Quantico Creek (Jul) | 1.2% | 1.3% | 1.5% | 1.7% |

Broad Run goes from about a quarter of low-month flow to over a third. Binding
month stays July throughout, so the *condition* is robust and only its severity
moves. Cited to AECOM Table 7 and explicitly labelled a sensitivity, not a
hydrologic projection — AECOM give months-in-drought, not a flow multiplier, and
converting needs a rainfall-runoff model this project does not have.

**3 and 4** documented in METHODOLOGY 63.3 (High sensitivity + Medium adaptive
capacity vs the lone Low-priority water action) and 63.4 (data centers filed
under "Communications," rated Low; the framework only ever asks what threatens an
asset, never what an asset threatens — "the county has a water-supply risk
assessment and a data-center inventory, and no instrument that joins them").

**Harness check 21** added: asserts the drought sweep is present for every basin,
monotone, binding-month-stable, sourced and caveated; and that the abstract makes
the dual-reporting claim and no longer carries the weak form. **22/22.**

---

## Part 24 — `SUP2025-00016.json` (Hornbaker Road), pages 1-13 of 73

A live data-center entitlement, not a policy document. Planning Commission
Resolution 25-xxx, **recommended for approval 5 November 2025**, subject to SUP
conditions dated 15 October 2025. Runs concurrently with Rezoning REZ2025-00014.
±40.02 acres, GPIN **7596-81-5396**, Brentsville District, immediately west of
Prince William Parkway / south of Wellington Road / east of Hornbaker Road.
Rezoning A-1 Agricultural + PBD -> **M-2 Light Industrial**. Max FAR 0.5. Data
center buildings up to **80 ft** including rooftop mechanical.

Case planner Christopher Perez. Owners/applicants MJV Parcel A, LLC and
PWC - Parcel B, LLC. Plan by IMEG (11 Oct 2024); elevations by Gensler
(15 Oct 2025).

### 24.1 Condition 3.c — the prohibition that misses

> **"Data Center Cooling: Groundwater, surface water withdrawals, or surface
> water discharges shall not be used to cool the data center buildings on the
> Property."**

Added in the October revision, in direct response to Planning Commission
pressure — the staff report lists it as one of five changes made between the
September tie votes and the November approval.

Read it against ICPRB (March 2026): data centers in the basin "are served by
public water suppliers and, to date, **hold no direct withdrawal permits**." And
JLARC: "**Only two data centers have their own DEQ withdrawal permits.**"

**So the condition prohibits the supply pathway essentially nobody uses, and is
silent on the one everybody uses — treated potable water bought from PWCSA or
Virginia American Water and evaporated in a cooling tower.** A facility can
comply with 3.c in full and still be the county's largest consumptive water user.

This is the strongest policy finding in the corpus so far, because it is not a
gap in the abstract sense — it is a live, negotiated, enforceable condition,
drafted specifically to address water, that does not reach the actual mechanism.
It is also exactly the failure the paper's scope argument predicts: an
instrument aimed at the on-site withdrawal boundary, where the water is not.

**ACTION: this belongs in the paper's policy paragraph, quoted.** It is more
concrete than "frameworks need to reach beyond on-site use."

### 24.2 The two measures that would bound water use are electives

Condition 3.d requires the applicant to adopt **a minimum of 8** sustainability
measures from a **19-item menu**, in consultation with the County's Environmental
and Energy Sustainability Officer, documented before each building's occupancy
permit. The menu includes:

- xii. "Use of **reclaimed water** for non-potable use"
- xvi. "Design the data center building to operate below an **annualized 1.5 PUE**"
- xvii. "Use of **air or closed loop cooling** rather than water-cooled alternatives"

alongside items like LED interior lighting (vii), LED exterior lighting (viii),
two EV charging stations per building (vi), heat-reflective roofing (x), and
recycling construction waste (ix).

**8 of 19, applicant's choice.** The three items that would actually bound water
or energy intensity carry the same weight as swapping light fixtures, and an
applicant can satisfy the condition without picking any of them.

This matters directly to the estimator: `pue_cap` and
`cooling_disclosure.air_or_closed_loop` are populated from exactly this class of
instrument. **A menu item is not a binding cap**, and the model should not treat
one as evidence unless the specific measure was actually elected and documented.
**ACTION: check whether any building's `pue_cap` or cooling disclosure traces to
a menu-style condition rather than an elected-and-documented one.**

### 24.3 Everything else in conditions 1-4

- **2.b** data center use limited to the northern building on Sheet C200, may
  split into **max two buildings** within the same footprint.
- **2.c.i Noise**, by receiving district, measured per Chapter 14:
  day (7am-10pm wk / 9am-10pm wknd+hol) **60 dBA** residential/mixed-use,
  **65** commercial/office, **79** industrial; night **55 / 60 / 72**. Most
  restrictive classification governs when a source spans districts. Construction
  and utility repair exempt during daytime hours.
- **2.c.ii** emergency generator operation exempt from noise limits; "emergency"
  defined as sudden, unforeseen, beyond the facility's control, requiring
  immediate generator use to restore normal operation.
- **2.c.iii** if an acoustical analysis shows exceedance, applicant must bring
  the property into compliance.
- **3.g Power**: permanent distribution lines underground, routed beneath
  Hornbaker Road from the west, "notwithstanding the existing overhead
  distribution lines or any proposed permanent overhead transmission lines
  pursuant to **PUR-2025-00046**." (Another live SCC transmission case.)
- **4** applicant must meet DED and GMU on apprenticeship/training partnerships
  before certificate of occupancy.

### 24.4 Site is OUTSIDE the Data Center Opportunity Zone Overlay

The SUP exists because the parcel sits outside the **DCOZOD**. Site history,
staff report section G: the overlay was amended by **DPA2019-00002, adopted
18 June 2019**, which "specifically took this parcel and others out of the
overlay" for "removal of areas that are desirable for high visibility employment
uses." The staff report at the time said the revised map "better represents the
locations the County would like to promote data center development."

So: the county deliberately removed this parcel from its data-center overlay in
2019, and in 2025 approved a data center on it anyway, by SUP. The Technology
Overlay District subdistricts here (EH and EO) are ones where staff note data
centers are "**permitted but not preferred**." Several Commissioners "expressed a
preference for non-data center employment uses consistent with the Innovation
Small Area Plan," and the September vote deadlocked twice.

That is a documented instance of the JLARC finding (Ch. 6) that elected officials
approve data centers in locations their own long-range plans do not favour.

**STILL TO READ in this file: pages 14-73** (the remainder of the 38-page staff
report and its attachments).

### 24.5 (pages 14-29) Staff found it INCONSISTENT with the Environment chapter and recommended approval

Part I, "Summary of Comprehensive Plan Consistency," page 10 of the staff report.
**Staff Recommendation: APPROVAL.** The table behind that recommendation:

| Comprehensive Plan section | Consistent? |
|---|---|
| Long-Range Land Use | Yes |
| **Community Design** | **No** |
| Cultural Resources | Yes |
| Economic Development | Yes |
| Electrical Utility Services | Yes |
| **Environment** | **No** |
| Fire and Rescue | Yes |
| Police | Yes |
| **Potable Water** | **Yes** |
| Sanitary Sewer | Yes |
| Transportation | Yes |

Two of eleven chapters fail, and the recommendation is still approval. The
Community Design failure is worked through at length (pp.17-21: setback reduced
from 100 ft to a variable ~50 ft average, 41-73 ft in front of the buildings;
Hornbaker's required 50 ft becomes a 10 ft strip; "the building maintains a
predominantly data center appearance, characterized by extensive concrete
facades, limited glazing, and minimal architectural variation"). **Environment is
listed as No in the summary table and its analysis section is further into the
report — still to read.**

Note the pairing that matters for this paper: **Potable Water = Yes, Environment
= No.** A data center that will buy treated water from a public supplier and
evaporate it satisfies the plan's Potable Water chapter. Whatever fails the
Environment chapter, it is not the water demand.

### 24.6 The county prices water quality at $75/acre and water quantity at zero

Level of Service monetary contributions, Proffer Statement 15 Oct 2025 (p.8):

| Item | Rate | Amount |
|---|---|---:|
| **Water Quality** | $75.00 per acre | **$3,001.14** |
| Fire & Rescue | $0.61 per SF of new floor area (871,518 SF at 0.5 FAR) | $531,234.13 |
| **TOTAL** | | **$534,235.27** |

Water quality is **0.56%** of the total and **1/177th** of the fire-and-rescue
contribution. There is **no water quantity contribution at all** — no line item
for consumptive use, none for peak-day demand, none for low-flow mitigation.

The county has a per-acre price for water *quality* and no price whatsoever for
water *quantity*, on a use whose defining environmental characteristic is
quantity. That is the fiscal expression of the same scope boundary Condition 3.c
draws physically.

### 24.7 The public raised water; the response could not reach it

Community input (p.9): the 5 June 2025 virtual community meeting "was not
attended by any members of the public." At the 24 September Planning Commission
hearing there were "four speakers, **all in opposition**. Key concerns included
electricity demand and cost, **water usage for cooling**, and potential health
impacts."

Condition 3.c — the groundwater/surface-water prohibition — was added in the
October revision, after those hearings. So the sequence is documented: public
raises water use for cooling -> county adds a binding water condition -> the
condition addresses withdrawals the facility was never going to make, and leaves
utility-supplied potable water untouched.

### 24.8 Other items, pages 14-29

- LOS analysis notes the development "generates substantial tax revenue without
  adding strain on schools, housing, or libraries."
- Staff strengths list includes "**Existing Utility Infrastructure**: The site's
  adjacency to power infrastructure supports data center development" — the site
  is west-adjacent to an existing substation and an approved substation.
- TeOD allows 90 ft height / 0.50 FAR; proposal is 80 ft (data center) and 75 ft
  (non-data center), both inclusive of rooftop mechanical. 30% open space.
- Innovation Town Center across the Parkway is planned at 45 ft townhomes and
  55 ft stacked multifamily — the scale contrast staff repeatedly flag.
- Planning Commission had until **23 December 2025** (90 days from first hearing)
  to act.
- Attachment list includes an **Environmental Constraints Analysis (ECA)** —
  water content likely; still to read.
- Proffer 18 carries cultural-resources language agreed with the County
  Archaeologist; Proffer 30 is the landscaping commitment staff call "minimal
  assurance."
- Condition 3.g references **PUR-2025-00046**, another live SCC transmission case.

**STILL TO READ in this file: pages 30-73** — including the Environment chapter
analysis, the Potable Water analysis, and the ECA attachment.

### 24.9 The Potable Water chapter review contains no water quantity. At all.

Staff report pages 30-31, "Potable Water Plan Analysis," **in its entirety**:

- the site is in Prince William County Service Authority (**d/b/a Prince William
  Water**) service area and "is thereby required to utilize public water"
- "Prince William Water has existing **16-inch water mains** on site near Braden
  Drive and Robertson Drive. The Applicant should connect to these mains with a
  minimum **12-inch water main** to provide a looped supply, with potential
  upsizing to 16-inch to be determined during plan review."
- connections must comply with Prince William Water's USM requirements
- the Applicant will connect and pay for on- and off-site improvements and
  easements "at no public cost"

**Strengths: "Water Connection & Service."
Weaknesses: "None identified."
Consistency Recommendation: consistent.**

That is the whole analysis. **There is not one number describing how much water
this facility will use.** No gallons per day, no peak-day figure, no cooling
demand, no consumptive fraction, no seasonal profile. The Potable Water chapter
review of a data center consists of **pipe diameter and who pays for the
connection**.

For scale on what went unquantified: the Traffic Impact Analysis in the same
report states full build-out by 2027 of "up to **571,000 square feet of data
center space** and 300,000 square feet of office space." At this model's
8,818 sqft/MW that is roughly **65 MW** of IT load; at ICPRB's regional average
WUP of 800 gal/MW/day that is about **0.05 MGD average**, and materially more at
their 8,500 gal/MW/day evaporative peak.

So the traffic chapter models three background developments, two horizon years
and peak-hour trip generation to arrive at 500 AM / 470 PM trips. The water
chapter records that the pipe should be twelve inches.

**This is the best single piece of evidence in the corpus for the paper's policy
claim**, and it is stronger than the argument the abstract currently makes,
because it is not about *authority*. JLARC Recommendation 6 asks the General
Assembly to authorize localities to require water-use estimates. This document
shows what the review looks like in the absence of that authority: not a weak
estimate, **no estimate**, and "Weaknesses: None identified."

Pair it with 24.6 (water quality priced at $75/acre, water quantity at $0) and
24.1 (Condition 3.c prohibits withdrawals nobody makes) and the three together
describe one coherent boundary: **the county's instruments engage water where the
pipe is and where the discharge is, and nowhere in between.**

### 24.10 Environment chapter — inconsistent, on trees, not water

Pages 25-27. Staff find the application **inconsistent with the Environment
Plan**. The stated reasons are entirely land-surface:

- "approximately **87% tree clearing** across the site," leaving "minimal tree
  save areas and limited natural resource preservation"
- Parkway setback cut from 100 ft to a variable ~50 ft average (41-73 ft in front
  of the buildings)
- Hornbaker setback cut "from the required 50 feet to as little as **10 feet**"
- Proffer 30 landscaping gives "minimal assurance"

Water appears in the Environment analysis in exactly two places, both
qualitative: the **$75/acre water quality contribution** ("for water quality
monitoring, drainage improvements, and/or stream restoration projects"), and a
paragraph headed "Enhanced Sustainability and Datacenter Cooling Commitments"
that restates the 8-of-19 sustainability menu and Condition 3.c.

**The Environment chapter of a data-center rezoning review contains no
quantification of water demand either.** The chapter fails — on trees.

Strengths credited include soil remediation in landscaped areas and delineated
Limits of Disturbance. Fire and Rescue notes hydrant flow of **2,500 GPM**
minimum — the only volumetric water figure anywhere in the staff report, and it
is a fire-flow requirement.

### 24.11 Remaining chapters, pages 22-32

Cultural Resources — consistent (Phase I/II investigation proffered, curation
with the County, no recorded cemeteries). Economic Development — consistent, no
weaknesses; DED supports the second building becoming non-data-center M-2 to
attract life sciences; Board "recognizes data centers as a targeted industry."
Electrical Utility Services — consistent; **no substation requested**, the site
"plans to utilize excess power available from the substation from across
Hornbaker Road"; Condition 3(g) undergrounds distribution notwithstanding
PUR-2025-00046. Fire and Rescue — consistent; Station #25 is outside the 4-minute
BLS travel time but inside 8-minute ALS; 3,655 incidents in FY2023 against 4,000
capacity. Police — consistent, no weaknesses. Sanitary Sewer — consistent;
existing 8-inch gravity main, "capacity to be confirmed at plan submission."
Transportation — TIA assumes 2027 build-out, 571,000 sqft data center +
300,000 sqft office, ~500 AM / 470 PM peak-hour trips, 3,583 (daily, cut off).

**STILL TO READ in this file: pages 41-73** (rest of Transportation, the
Environmental Constraints Analysis attachment, elevations, line-of-sight
exhibits, Historical Commission resolution, 9-24-25 PC resolutions).

### 24.12 The Environmental Constraints Analysis has no water in it

The ECA is not a narrative report — it is **two plan sheets**, pages 54-55.

Sheet 1: tree preservation schedule, limits of clearing and grading, four
specimen trees (Southern Red Oak, White Oak, Pin Oak) with condition ratings,
steep slopes (15-24% and 25%+), contours, treelines.

Sheet 2: soils map and tables — Haymarket Silt Loam (28C), Jackland Silt Loam
(30B), Jackland-Haymarket Complex (31B, 31C), Sycoline-Kelly Complex (53B),
Waxpool Silt Loam (56A); federally listed species (**Northern Long-eared Bat**
potential habitat); **56% pervious / 44% impervious**; **87% disturbed / 13%
undisturbed**; existing vegetation tabulation (oak-hickory-pine-redcedar).

**No streams, no wetlands, no RPA, no floodplain, no water demand, no cooling
water.** The document the county calls an "Environmental Constraints Analysis"
for a 571,000 sqft data center analyses trees, slopes, soils and one bat species.

Some of that absence is genuine — this parcel appears to carry no mapped stream
or RPA. But nothing in the ECA's *structure* would have captured water demand
even on a site that did.

**So there are four instruments on this application that touch water, and all
four stop at the same boundary:**

| instrument | what it does | what it misses |
|---|---|---|
| SUP Condition 3.c | bans groundwater/surface-water cooling | utility potable water |
| Potable Water chapter | sizes the pipe (12" min, maybe 16") | any quantity of demand |
| Water Quality proffer | $75/acre = $3,001 | any quantity contribution |
| Environmental Constraints Analysis | trees, slopes, soils, bat | water entirely |

Agency Comments (p.38 of the report) confirm this is not an oversight of
consultation: **PWC Service Authority (d/b/a Prince William Water)** and
**PWC Public Works - Arborist / Environmental Services / Watershed Management**
both reviewed the application, as did **Dominion Energy** and **NOVEC** (a fourth
confirmation both utilities serve this area). The water utility reviewed it and
the review produced a pipe diameter.

### 24.13 The vote: 4-4 twice, and a closed-loop condition that was never adopted

Pages 66-73, the 24 September resolutions, all recorded:

- **Res. 25-083, recommend DENIAL** — Ayes: Carroll, Justice, Moses-Nedd,
  Scheufler. Nays: McPhail, Brown, Ross, Sheikh. **MOTION FAILED 4-4.**
- **Res. 25-084, recommend APPROVAL** — exact mirror. Ayes: McPhail, Brown, Ross,
  Sheikh. Nays: Carroll, Justice, Moses-Nedd, Scheufler. **MOTION FAILED 4-4.**
- **Res. 25-085 / 25-086, deferral to 29 Oct** — carried 8-0.

The approval motion that deadlocked carried a condition the eventual approval did
not:

> "With a condition that the Applicant works with the County for **the best
> possible closed loop coolant system** for the datacenter and the applicant
> works with the County for a modern design of the datacenter building."

**Closed-loop cooling was proposed as a binding condition, the motion failed on a
tie, and what survived into the November approval was Condition 3.c** — the
groundwater/surface-water prohibition — plus closed-loop cooling as *item xvii of
nineteen* on an optional sustainability menu (24.2).

So the record shows the one instrument that would actually have bounded this
facility's water use being raised, tied, and replaced by one that does not reach
utility supply. That is the single most legible sequence in the corpus for the
paper's argument, and it is fully minuted.

### 24.14 Remainder, pages 41-65

Transportation: TIA 3,583 daily trips; Hornbaker/Robertson projected LOS F,
mitigated by signalisation; proffered turn lanes, 10-ft shared-use path (or
**$41,410** in lieu), signal if warranted, bicycle parking, right-of-way
dedication, Construction Management Plan. Consistent, no weaknesses.
Strategic Plan alignment: Goals 5 and 8. "Materially Relevant Issues: None."
Proffer deficiencies: inconsistent building labelling across sheets; Sheet C400
mislabels the metroduct and construction easements' plantability.
Four waivers/modifications under Proffer #35 — staff **do not support** A
(Parkway setback 100 ft -> ~50 ft) or D (waiving Type C landscaping at service
areas); staff are "less concerned" with B and C on Hornbaker.
Plan set: C000 cover, C100 existing conditions (notes an existing **16" waterline
easement** on site), C200 site layout, C300 road improvement, C301 sight
distance, C302 Hornbaker ultimate, C400 landscape. **No utility plan sheet and no
water demand sheet in the index.**
Gensler elevations: 76 ft parapet with 80 ft screen wall; materials MP-1/2/3,
PC-1/2/3, GL-1, GL1-S. Renderings at planting and at 20-year growth. Cross
sections 1, 2, 3, 3A, 4. Project team: Cooley LLP (land use), IMEG (civil),
Gorove Slade (transportation), Gensler (architecture).

**`SUP2025-00016.json` COMPLETE — all 73 pages.**

---

## Part 25 — `FY2026 Application Package for Special Use Permits` (July 2025). COMPLETE, 16 pp.

This is the blank form every data-center SUP applicant in Prince William fills
out, effective **1 July 2025**. It turns the Hornbaker finding (Part 24.9) from an
anecdote into a structural fact.

### 25.1 The form has no field for water. Or power.

Page 4, "Special Use Permit Application Supplemental Information," is the only
page that collects quantities. It asks for:

**Land Information** — Total Area, Disturbed Area, Open Space Area, Impervious
Area, Recreational Area (acres).
**Structure & Lot Information** — single family / townhouse / multi-family /
affordable / non-residential / open space lots; institutional or educational,
telecomm cabinet, commercial, industrial, retail, recreational, office square
footage; accessory structures; landbays; total allowed units.
**Miscellaneous Improvements** — HAZMAT checkbox, Proposed Depth (feet), Proposed
Width (feet), Proposed Lot Reduction (acres), Excess Building Height (feet),
Proposed District Reduction (acres), Tower Height (feet), **Number of Beds**,
Automotive Bays, **Maximum # of Children**, Number of Signs.
**Proposed Uses** — use and acreage, up to five rows.

**There is no field for water use. None for electricity or power demand. None for
cooling technology.**

The county's application form asks a data-center applicant for the maximum number
of children and the number of automotive bays, and has nowhere to write gallons
per day or megawatts.

So the Hornbaker Potable Water review (24.9) did not omit a water estimate
through oversight or applicant reticence — **the form provides no place to put
one**, and therefore the review had nothing to review. This is precisely the gap
**JLARC Recommendation 6** targets: "expressly authorize local governments to
(i) require proposed data center developments to submit water use estimates and
(ii) consider water use when making rezoning and special use permit decisions."

### 25.2 The county already classifies data centers as its most intense use

Fee Schedule, effective 1 July 2025. **"Data Center" sits in Category I** — the
top tier — defined as:

> "Industrial-type uses, which may involve HAZMAT; including commercial uses that
> have **potential environmental hazards** and significant traffic impacts to
> surrounding area"

**Fee: $17,209.06.** Its listed companions are asphalt/concrete plants, heavy
industry, HAZMAT storage facilities, motor vehicle graveyards, sawmills,
extraction of mineral resources, and racetracks.

This matters because it forecloses the obvious rebuttal. The county has not
misclassified data centers as benign — it puts them in the **highest**
environmental-hazard category it has, charges the **highest** fee, and *still*
collects no water quantity on the form.

For contrast, Category F ("technology-related uses that have little to no
impact") holds electric substations and telecom towers at $9,977.

### 25.3 What the county charges to review each impact

From the "Other Fees" schedule:

| review | fee |
|---|---:|
| SUP application, Category I (Data Center) | **$17,209.06** |
| Traffic Impact Study, first submission | $2,059.13 |
| Cultural Resources Study, Phase III | $2,454.58 |
| Cultural Resources Study, Phase II | $920.20 |
| Cultural Resources Study, Phase I | $306.02 |
| **Prince William Water Review Fee** | **$86.25** |

"Prince William Water Review Fee - (**Required for most Special Use Permit
applications**) $86.25."

**The water utility's review of the county's highest-intensity industrial use
costs $86.25 — half a percent of the application fee.** The county charges 24x
more to review traffic than water, and 28x more for a Phase III archaeological
excavation. On the Hornbaker case that $86.25 review produced a pipe diameter.

Pair this with Part 24.6 (water quality proffered at $75/acre = $3,001; water
quantity at $0) and the pricing is consistent end to end: **the county has a
price for reviewing water, a price for water quality, and no price at all for
water quantity.**

### 25.4 Rest of the package

Instructions (p.2); application form (p.3); fee calculation worksheet (p.5,
carries the Prince William Water Review Fee line "Only if located within service
area", TIA first/third submission fees, and a note that VDOT 527 fees go direct
to VDOT); waiver/modification request form (pp.6-7, per ZO 32-700.25(1) requiring
written justification tied to "unique characteristics of the specific property");
Interest Disclosure Affidavit (p.8, 10% interest threshold for Planning
Commission / BOCS members); Special Power of Attorney (p.9); Adjacent Property
Owners Affidavit (p.10 — notification radius **500 feet**, or **1,320 feet for
projects seeking height modifications**, plus adjacent localities within half a
mile, military installations within 3,000 ft, public-use airports within
3,000 ft); fee schedule categories A-I (pp.11-15); refunds and other fees (p.16 —
25% refund if withdrawn before advertisement, none after; concurrent SUP+REZ
processing $92.08; administrative SUP modification $1,465.51).

Note for the Hornbaker case: it sought height modifications, so the **1,320-foot**
notification radius applied — and the June 2025 community meeting still drew no
public attendance (Part 24.7).

---

## Part 26 — `Reference Manual for Rezoning, SUP and Proffer Amendment Applications` (July 2025). COMPLETE, 16 pp.

The instruction manual behind the form in Part 25. It is where the asymmetry
becomes explicit, because the county writes out its narrative requirements
chapter by chapter, in parallel, in one document.

### 26.1 The Potable Water guideline, next to the Transportation guideline

Section A, Written Narrative, page 9-10. Verbatim, complete:

> "**Potable Water** - Describe how water will be **provided to the site**:
> • Relationship of the proposed development to supportive public utilities.
> • Improvements proposed, especially if the proposal lies on groundwater or
>   recharge areas."

And, on the facing page:

> "**Transportation** - Describe measures to achieve **level of Service 'D' or
> better**: • **Impacts of the proposal on established LOS standards.**
> • Improvements proposed, both motorized and non-motorized. • **Traffic Impact
> Analysis (TIA)** as determined by PWC Department of Transportation..."

Transportation gets a performance standard, an impact assessment against that
standard, and a mandatory quantitative study. **Potable Water gets "describe how
water will be provided to the site."** Supply-side delivery only — how it gets
there, not how much leaves.

**Fire and Rescue, Police, Parks/Open Space/Trails, and Schools each get
"Impacts of the proposal on established LOS standards."** Potable Water and
Sanitary Sewer are the only service chapters with **no LOS standard at all** —
their guidelines ask only about "relationship to supportive public utilities" and
"improvements proposed."

This is the same finding as Part 24.9, but now shown to be by design rather than
by omission: the Hornbaker Potable Water review consisted of pipe diameter and
who pays because **that is exactly, and only, what the manual asks for.**

### 26.2 Three mandatory pre-submission studies. Water's is a presence check.

Page 3, "Pre-Submission Requirements," all three Required:

1. **Application for Deferral of Traffic Impact Analysis** — either an authorized
   deferral or a full TIA must accompany the application.
2. **Cultural Resources Assessment** — record check, and a Phase I archaeological
   survey if warranted; scopes of work approved by the County Archaeologist.
3. **Perennial Flow Determination (PFD)** — completed with Watershed Management;
   "the form with either a PFD or a **statement of no stream prevalence** is
   required."

So the county does require a mandatory water study before an application is
accepted — and it determines **whether a perennial stream exists on the parcel**,
for RPA delineation. Traffic gets a demand study; culture gets a resource survey;
**water gets a presence check.** The question the PFD answers is "is there water
on this site," never "how much water will this site consume."

### 26.3 The ECA specification — every item is receiving-environment

Pages 5 and 12-14 give the full ECA spec: 15%+ slopes; highly erodible, highly
permeable and marine clay soils; wetland and Chesapeake Bay RPA delineation
including the PFD; limits of disturbance; areas remaining undisturbed; pervious
and impervious surfaces in tabular form; existing drainage patterns and non-tidal
wetlands; 100-year floodplain from FEMA maps; endangered/threatened species from
the Natural Heritage Resource map; ERPO acreage (**residential applications
only**); all specimen trees by species and dbh at 4.5 ft; and forest cover types
named strictly from the Society of American Foresters classification — the manual
even lists the 14 valid names for Prince William and warns that "mixed hardwoods"
or "old field succession" "are not valid… probably indicates that the applicant
has not assessed the site's existing forest cover types."

**Not one item in the ECA specification concerns the development's resource
demand.** Every item describes what is already on the land and what will happen
to it physically. The Hornbaker ECA (trees, slopes, six soil series, one bat —
Part 24.12) was fully compliant.

The contrast is sharp: the manual specifies forest stand age classes to the inch
of trunk diameter (Seedling/Sapling, Young, Medium-Aged, Mature, Very Mature) and
prescribes a national classification system for naming tree communities — and has
no field anywhere for gallons per day.

### 26.4 The impact-identification requirement exempts data centers

Mandatory item 8, page 5:

> "**SB 549 Justification Narrative**: Identify impacts (**for residential
> rezonings and proffer amendments only**)."

It then requires the applicant to "specifically identify **all** the impacts,"
propose "specific and detailed mitigation strategies," demonstrate their
sufficiency "using professional best accepted practices and criteria, including
all data, records, and information used," per Va. Code §15.2-2303.4.

That is the county's most rigorous impact-analysis requirement, and by its own
terms it **does not apply to non-residential rezonings.** A data-center rezoning
is not required to identify its impacts at all.

### 26.5 Process facts worth keeping

Review takes **9 to 12 months**. Pre-application meetings are Thursday
afternoons, virtual, mandatory for planned districts. A post-submission meeting
follows 5-7 weeks after acceptance. Applicants "should" hold a Community
Engagement Meeting before the PC hearing (Hornbaker's drew nobody — Part 24.7).
The Planning Office distributes the application "for comment to various federal,
state, and local agencies whose services may be impacted."

Written-narrative Environment guidance (p.9): "Identify how the proposal will
preserve, protect, and/or enhance environmental resources… See Environmental
Constraints Analysis." So the Environment narrative is defined by reference to
the ECA — which, per 26.3, contains no demand element. The chain closes on
itself.

The only water-adjacent item anywhere in the Land Use narrative guidance is
"a commitment to landscaping with indigenous, **drought tolerant** species."

Proffer guidance (Section C, pp.15-16): proffers grouped under Comprehensive Plan
chapter headings, or "MATERIALLY RELEVANT" if they fit no chapter; monetary
proffers must state purpose and payee; **"A proffer that attempts to restate or
reduce existing state or county standards is not an acceptable proffer"**; and an
**Escalator Clause** indexing contributions to CPI-U after 18 months.

That penultimate rule is worth noting against Hornbaker Condition 3.c: a proffer
may not merely restate an existing standard. Since no county or state standard
governs a data center's utility-supplied cooling water, a proffer bounding it
would have been *new*, and therefore acceptable. Nothing in the manual prevented
it.

### 26.6 Summary of the instrument chain

| stage | instrument | what it captures for water |
|---|---|---|
| pre-submission | Perennial Flow Determination | is there a stream on the parcel |
| application form | Supplemental Information (Pt 25.1) | nothing — no field exists |
| plans | Environmental Constraints Analysis | wetlands, RPA, floodplain, soils, trees |
| narrative | Potable Water guideline | how water will be *provided to* the site |
| narrative | SB 549 impact identification | n/a — residential only |
| review | Prince William Water Review, $86.25 | pipe diameter |
| approval | proffers / SUP conditions | $75/acre quality; quantity unpriced |

**Seven instruments touch water across a nine-to-twelve month review, and none of
them asks how much.**

---

## Part 27 — the 8 NWIS gage records. A real problem with the basin-stress denominator.

Read all eight `.rdb` files. Full inventory, from their own headers:

| file | station | record | n months | lowest month (cfs) |
|---|---|---|---:|---|
| 01646500 | POTOMAC RIVER NEAR WASH, DC LITTLE FALLS | 1930-03..**2026-03** | 1153 | 538.10 (1966-08) |
| 01656500 | **BROAD RUN AT BUCKLAND, VA** | 1950-10..**1986-12** | 422 | **0.89** (1954-09) |
| 01656650 | BROAD RUN NEAR BRISTOW, VA | 1974-10..**1986-12** | 147 | 1.42 (1986-10) |
| 01657000 | **BULL RUN NEAR MANASSAS, VA** | 1950-10..**1981-08** | 371 | **0.24** (1954-09) |
| 01657500 | OCCOQUAN RIVER NEAR OCCOQUAN, VA | 1913-04..**1956-03** | 287 | 3.66 (1941-11) |
| 01657895 | POWELLS CREEK NEAR DALE CITY, VA | 1995-02..**1996-06** | **17** | 0.51 (1995-08) |
| 01658500 | S F QUANTICO CREEK NR INDEPENDENT HILL | 1951-05..**2026-01** | 897 | **0.00** (1964-09) |
| 01663500 | HAZEL RIVER AT RIXEYVILLE, VA | 1942-10..**2026-03** | 884 | 5.85 (1966-08) |

### 27.1 The two basins holding 227 of 243 buildings use gages that stopped recording before data centers existed

`basin_stress.json` assigns:

- **Broad Run — "Broad Run at Buckland" (01656500), record ends December 1986**, 166 buildings
- **Bull Run — "Bull Run near Manassas" (01657000), record ends August 1981**, 61 buildings
- Quantico Creek — S F Quantico Creek (01658500), current through 2026, **2 buildings**

**227 of 243 buildings sit in basins whose flow denominator comes from a gage that
was decommissioned 40-45 years ago.** The only station with a live record covers
two buildings.

This is not fatal — a long-period historical mean is a defensible denominator, and
the framing has always been a scale comparison rather than an attribution. But it
must be stated, because the denominator:

- predates every data center in the county
- predates ~40 years of upstream development (JLARC Ch.5: data centers alone were
  20-30% of land development in Loudoun and Prince William 2013-2021)
- cannot reflect any recent hydrologic trend, in either direction
- is being swept forward for future drought (Part 23) while already being stale
  backward

**ACTION: declare the gage vintage wherever the basin-stress figure appears.**
Currently `basin_stress.json` has no `gage_note` and no record-period field.

### 27.2 Against the observed July minimum, Broad Run is 363%

The headline 28.3% divides by the **mean** July flow. The same record contains the
**minimum** July flow. Both are observed; neither is a projection:

| basin | July draw (all 243) | July draw (completed only) | mean July | min July | % of mean | **% of MIN** |
|---|---:|---:|---:|---:|---:|---:|
| **Broad Run** | 4.245 MGD | 0.848 MGD | 15.00 | **1.17** (1966) | 28.3% / 5.7% | **362.9%** / 72.5% |
| Bull Run | 0.941 | 0.164 | 36.20 | 1.31 (1954) | 2.6% / 0.5% | 71.7% / 12.5% |
| Quantico Ck | 0.022 | 0.000 | 1.76 | 0.04 (1963) | 1.2% / 0.0% | 60.8% / 0.0% |

Read carefully:

- **Full buildout against the lowest July on record: 363% of Broad Run's flow.**
  The modelled draw is 3.6x the entire river.
- **Completed fleet against the lowest July on record: 72.5%.** Today's built
  fleet alone would take about three-quarters of the lowest July flow the gage
  ever measured.
- Broad Run's 5th-lowest July is 1.98 MGD (1985), so 1966 is not a lone outlier.

The existing 28.3% figure is the same quantity measured against a 37-year average.
The mean/minimum spread is 13x, and that spread is invisible in the current
headline.

**ACTION: report the binding figure against mean July AND minimum-observed July.**
This is strictly stronger than the drought sweep added in Part 23, because the
sweep multiplies a mean by an assumed factor whereas this uses flows the gage
actually recorded. The drought sweep bottoms out at x0.70 (10.5 MGD); the observed
record reaches 1.17 MGD — far below anything the sweep contemplates.

### 27.3 S F Quantico Creek recorded 0.00 cfs

September 1964. The creek went dry. That is the only fully-current gage in the
county set, and its record contains a zero-flow month. Any framing that treats
low flow as a bounded perturbation of a mean is wrong for these streams.

### 27.4 Other notes from the records

- **Little Falls (01646500)** is the long Potomac record, 1930-2026, 1,153 months,
  and it is the gage behind the WMA/ICPRB comparisons. Minimum monthly mean
  538 cfs (Aug 1966) — 1966 is the low year in both this and Broad Run.
- **Hazel River at Rixeyville (01663500)**, 1942-2026, minimum 5.85 cfs, also
  Aug 1966. Three independent gages agree 1966 was the drought of record.
- **Powells Creek (01657895)** has 17 months total (Feb 1995 - Jun 1996) and is
  unusable for any statistic; it should not be relied on anywhere.
- **Occoquan River (01657500)** ends March 1956 — it predates the Occoquan
  Reservoir's role in WMA supply and is of historical interest only.
- All series are parameter 00060, discharge in cubic feet per second, monthly
  means of approved daily means. USGS caveat in every header: "The statistics
  generated are based on approved daily-mean data and may not match those
  published by the USGS in official publications."

---

## Part 28 — the NOAA/NCEI series. And a correction to my own Part 22.2.

Fifteen files, two families.

**Ten county-level NCEI monthly series**, each **1,576 months, 189501 to 202604 —
January 1895 to April 2026, a 131-year record for Prince William County**:
PDSI, Palmer Z-Index, PMDI, PHDI, Precipitation (inches), Minimum / Average /
Maximum Temperature (deg F), Heating Degree Days, Cooling Degree Days
(Fahrenheit degree-days). Schema `{description:{title,units}, data:{YYYYMM:{value}}}`.

**Five station files** with daily data: Vienna VA **USC00448737** (from
1925-12-23, five dataTypes incl. SNOW/TMIN) and Manassas **US1VAPW0022** (from
2020-01-21, three dataTypes SNOW/SNWD). Note the three `VIENNA_VA_US_*.json`
files are byte-identical in structure and dataTypes, as are the two Manassas
files — **the same download saved under different names.** Five files, two
stations.

### 28.1 CORRECTION to Part 22.2 and METHODOLOGY 63.2

I reported AECOM's projected drought changes as "+114% to +350% severe, +201% to
+1534% extreme" and treated the size of those percentages as the striking fact.
**That was a mistake: I quoted a percentage without checking its base.**

Back out AECOM's implied baseline from their own Table 7 (change in months/yr
alongside percent change): severe +0.289 months = +114% implies a baseline of
**0.25 severe months/yr**; extreme +0.114 = +201% implies **0.057 extreme
months/yr**.

The observed county record, 1895-2026, computed from `PDSI.json`:

| PDSI class | observed months/yr | % of all months | AECOM implied baseline |
|---|---:|---:|---:|
| mild (-1 to -2) | 2.12 | 17.7% | — |
| moderate (-2 to -3) | 1.16 | 9.6% | ~1.07 |
| **severe (-3 to -4)** | **0.66** | 5.5% | **~0.25** |
| **extreme (< -4)** | **0.38** | 3.2% | **~0.057** |

**AECOM's baseline is 2.6x lower than observed for severe drought and 6.7x lower
for extreme.** Their baseline is 1950-2005 from downscaled GCM output, not
observations. The eye-catching "+1534%" is arithmetic off a near-zero modelled
base, not a statement that extreme drought becomes fifteen times more common than
the county has actually experienced.

The drought denominator sweep built in Part 23 is unaffected — it never used
AECOM's percentages, only their direction. But the *narrative* in METHODOLOGY 63.2
leans on those percentages and should be rewritten around the observed record
instead. **ACTION: revise 63.2.**

### 28.2 The observed trend is real, and better evidence than the projection

Severe-or-worse drought months per year, by 30-year epoch, from the observed
county PDSI record:

| epoch | severe+extreme months | per year |
|---|---:|---:|
| 1896-1925 | 7 | **0.23** |
| 1926-1955 | 25 | 0.83 |
| 1956-1985 | 18 | 0.60 |
| **1986-2015** | **40** | **1.33** |

A **5.8x increase** from the first epoch to the most recent — in observations, no
model involved. That is a far more defensible sentence than any percentage from a
downscaled ensemble, and it is a county-specific record.

### 28.3 Cooling demand has already risen a third

Mean annual cooling degree days, same source, same county:

| epoch | CDD/yr |
|---|---:|
| 1896-1925 | 946 |
| 1926-1955 | 1,052 |
| 1956-1985 | 989 |
| 1986-2015 | 1,165 |
| **1996-2025** | **1,257** |

**+33% against 1896-1925 and +27% against 1956-1985.** This matters directly:
`seasonal_basin_surface.py` distributes the cooling-variable share of demand in
proportion to CDD, so the demand shape this model uses is itself tied to a
quantity that has already moved a third over the record.

Combine with Part 27: the demand side is indexed to a CDD series that has risen
27-33%, while the supply side is divided by gage records that stopped in 1981 and
1986. **Both sides of the basin-stress ratio are anchored to different and
mutually inconsistent periods.** That is the sharpest methodological statement
available about this figure and it should be in the paper.

### 28.4 What else these series unlock

The county now has, in hand and unused:
- **131 years of monthly PDSI, PMDI, PHDI and Palmer Z** — enough to compute
  observed drought return periods directly rather than citing projections.
- **131 years of monthly precipitation and min/avg/max temperature.**
- **131 years of HDD and CDD** — the CDD series already drives the seasonal shape;
  HDD is unused.
- **Daily Vienna records from 1925** (USC00448737) — a century of daily
  temperature and precipitation about 25 km from the county.

**ACTION: the observed PDSI record should replace the AECOM projection as the
primary drought evidence**, with AECOM retained only as the forward-looking
statement. Observed beats modelled where both exist, and here both exist.

---

## Part 28.5 — observed drought return periods, computed. And the county is in the worst drought of its record RIGHT NOW.

The user asked that the return-period opportunity be logged. Better: it is computed.
Source `data/water_raw/PDSI.json`, 1,576 monthly values, 1895-2026. Method:
annual worst monthly PDSI, empirical exceedance over 132 years. **No model, no
downscaling, no RCP.**

### Return periods, Prince William County, observed

| threshold | years with event | P(any year) | **return period** |
|---|---:|---:|---:|
| any drought (<= -1) | 109 | 82.6% | 1 in 1.2 yr |
| moderate (<= -2) | 66 | 50.0% | 1 in 2.0 yr |
| **severe (<= -3)** | 34 | 25.8% | **1 in 3.9 yr** |
| **extreme (<= -4)** | 16 | 12.1% | **1 in 8.2 yr** |
| <= -5 | 6 | 4.5% | 1 in 22 yr |
| <= -6 | 3 | 2.3% | 1 in 44 yr |

Sustained (years with >= N severe-or-worse months): >=3 mo 1 in 6.0 yr;
>=6 mo 1 in 13.2 yr; >=9 mo 1 in 33 yr; **>=12 mo once in 132 years.**

**Non-stationarity, measured not projected.** Splitting the record:
severe drought is **1 in 3.9 yr** over the full record but **1 in 2.5 yr** since
1976; extreme is **1 in 8.2 yr** full-record but **1 in 4.6 yr** since 1976.
The return period has roughly halved. This replaces AECOM's percentages entirely
(28.1) — same conclusion, observational basis, defensible interval.

### 28.6 The finding that changes the framing

Ranking all 132 years by minimum monthly PDSI, the top five include **2025 (1st or
3rd depending on metric), 2024, and 2026**:

| year | min monthly PDSI | severe+ months |
|---|---:|---:|
| 1931 | -6.96 | 9 |
| 1930 | -6.54 | 6 |
| **2025** | **-6.13** | **12 of 12** |
| **2024** | -5.46 | 7 |
| **2026** (4 mo) | -5.30 | 4 of 4 |

**2025 is the only year in 132 years in which every single month was severe
drought or worse.**

And the run is unbroken:

> **Longest unbroken run of severe-or-worse (<= -3) months in the 132-year
> record: 23 months, 202406 through 202604 — and it does not end, the data
> does.** Latest value on record, April 2026: **-5.30**.

Monthly PDSI 2023-2026 shows no recovery month since mid-2024; the last twelve
values run -4.66, -3.60, -3.13, -3.53, -3.82, -3.98, -4.64, -5.32, -5.06, -4.71,
-4.80, -5.30.

### 28.7 What this does to the model

1. **The drought sweep is no longer hypothetical.** `seasonal_basin_surface.py`
   documents `DROUGHT_FLOW_SWEEP = (1.00, 0.90, 0.80, 0.70)` as "a sensitivity,
   not a projection." It is neither — **the county is in an unprecedented drought
   as of the data cutoff.** The 0.70 branch should be presented as the current
   condition, not a hypothetical tail.
2. **It sharpens Part 27 into an indictment.** Broad Run and Bull Run denominators
   come from gages decommissioned in **1986 and 1981**. Those gages never observed
   any part of a 23-month run, and stopped before the two most extreme years in
   the record bar 1930-31. The basin-stress percentages divide a 2026 demand by a
   pre-1986 flow, during the worst drought since 1931.
3. **It is a real-time hook for the abstract.** Not "drought is projected to
   increase" but: this fleet reached its present scale during the longest severe
   drought in the county's instrumental record, and the flow denominators used to
   assess it predate that drought by forty years.

**ACTIONS:** (a) rewrite METHODOLOGY 63.2 on observed return periods, drop the
AECOM percentages to a secondary forward-looking note; (b) re-label the drought
sweep as observed-condition, not sensitivity; (c) add the 23-month run and the
1-in-2.5 / 1-in-4.6 post-1976 return periods to the abstract's motivation;
(d) ledger entries for the return-period table and the 23-month run.

---

## Part 29 — the CSVs, part 1. EPA ICIS independently confirms the regulatory gap, statewide and nationally.

### 29.1 `Prince_William_Water_FAQ_Extract.csv` (11 rows) — already logged, still unreconciled
Read in full. The load-bearing row is the utility's own 2025 statement: data centers
were **3.8% of average daily demand and 10.1% of maximum daily demand** in the PWW
service area (peak/avg = 2.7x on a demand-share basis). Already captured at
METHODOLOGY:1341 and flagged there as unreconciled against the model's 2023
"0.42 MGD" anchor and its 3,060/309 = 9.9x intensity-derived peak. **Still open.**
Other rows confirm supply routing (West: Fairfax Water Corbalis on the Potomac,
wastewater to UOSA then Occoquan Reservoir; East: Griffith WTP on the Occoquan),
that public supply is surface water not groundwater, and that reuse was
**"studied for Digital Gateway; found not currently viable there"** — which
constrains plan item B3 (reclaimed offset) to a literature bound locally.

### 29.2 `NPDES_NAICS_DATACENTER.csv` (40 rows) — the national picture

Every NPDES permit in the United States coded to NAICS **518210** ("Computing
Infrastructure Providers, Data Processing, Web Hosting"): **40 rows, 39 unique
permits.** Twenty-two carry it as the primary industry.

By state: TX 16, KS 6, **VA 4**, AL/GA/KY/MS 2 each, AK/AR/FL/ND/NV/OK 1 each.
Virginia's four: `VA0093301` Amazon Northeast Creek Tech Campus (Louisa),
`VAG250128` Anthem CDC 3, `VAG250162` Microsoft IAD11 Campus, `VAG830615` Birchwood.

**Thirty-nine NPDES permits for data centers in the entire country.**

### 29.3 `ICIS_FACILITIES_VA.csv` (18,244 rows) — and the NAICS code is nearly useless

Columns: ICIS_FACILITY_INTEREST_ID, NPDES_ID, FACILITY_UIN, FACILITY_TYPE_CODE,
FACILITY_NAME, LOCATION_ADDRESS, SUPPLEMENTAL_ADDRESS_TEXT, CITY, COUNTY_CODE,
STATE_CODE, ZIP, GEOCODE_LATITUDE, GEOCODE_LONGITUDE, IMPAIRED_WATERS.
Fill rates: geocodes 99%, but **COUNTY_CODE only 14%** and demonstrably wrong where
present (an Alexandria VA facility carries `DC001`) — do not join on it.
IMPAIRED_WATERS is populated for 3,190 rows (17%), single value "303(D) Listed".

Name-matching operator and data-center patterns over all 18,244 rows returns
**124 data-center facilities in Virginia.** The NAICS-coded set found only 4.
**The industry code captures 3% of them.** You cannot locate data centers in EPA's
own database by industry classification — a concrete, demonstrable disclosure
failure independent of anything the county does.

**What the 124 permits actually are:**

| permit family | n | share | what it regulates |
|---|---:|---:|---|
| **VAR10** construction stormwater GP | 80 | 65% | construction-phase runoff; lapses at completion |
| **VAR05** industrial stormwater GP | 29 | 23% | site runoff |
| other general permits (VAG..) | 13 | 10% | — |
| **VA0.. individual VPDES** | **2** | 2% | actual discharge limits |

Of the two individual permits, one (`VA0024031` Shawsville WWTP) is a name-pattern
false positive. **So: exactly one data center in the Commonwealth of Virginia holds
an individual VPDES permit — `VA0093301`, Amazon Northeast Creek Tech Campus,
Louisa County.**

Every other data center in Virginia is covered only by a **stormwater** general
permit. Stormwater permits regulate what runs off the roof and parking lot. **None
of them regulate cooling-water withdrawal, consumption, or thermal discharge.**

### 29.4 Why this matters more than the 235/243 number

Part 12's finding was that 235 of 243 PWC buildings have no NPDES permit. This is
the same conclusion reached from a completely independent direction — EPA's national
ICIS extract rather than county records — and it is **stronger**, because it shows
the eight that *do* have permits mostly hold construction-stormwater coverage that
says nothing about water use. The gap is not that data centers are unpermitted;
it is that **the permits they hold are the wrong instrument**, and the one
instrument that would capture water use is held by one facility in the state.

Incidentally, data-center facilities sit on 303(d) impaired waters at **10%**,
*below* the 17% base rate for all Virginia facilities — so the siting is not
preferentially on already-impaired streams. Worth stating to forestall the
obvious reviewer question.

**ACTIONS:** (a) ledger `icis_va_one_individual_permit` and
`icis_naics_captures_3pct`; (b) this belongs in the abstract — it generalizes the
regulatory claim from one county to a state and, via 29.2, to the nation;
(c) do NOT join ICIS on COUNTY_CODE.

---

## Part 30 — the CSVs, part 2. ECHO, iNaturalist, and one corrupt file.

### 30.1 `echo_loadings_34919817.csv` — read in full, 163 rows / 32 facilities

EPA ECHO custom download. Search criteria line is explicit and worth keeping:
**"Year = 2026; State = Virginia; County = 51153; Non-detects equal to zero;
Estimation function: On; Parameter grouping: On; Nutrient aggregation: On;
Data for Loading Calculations: DMR data only."** Note the file has a 3-line
preamble — `csv.DictReader` on the raw file yields one column. Header is line 3.

METHODOLOGY:1457 already records this file and Possum Point's 58 rows. Four things
in it are **not** yet recorded:

**(a) Every NPDES discharger in the county, and none of them is a data center.**
32 distinct permitted facilities in Prince William in 2026. Exhaustive name check
for DATA/AMAZON/MICROSOFT/IAD/DIGITAL/CLOUD/VANTAGE/EQUINIX/QTS/STACK returns
**NONE**. This is EPA's own county-filtered discharge-monitoring extract, a third
independent confirmation of Parts 12 and 29.

**(b) One facility is 99.92% of the county's permitted discharge.**

| watershed | facilities | actual avg flow |
|---|---:|---:|
| Tank Creek-Potomac River | 5 | **300.045 MGD** |
| Rocky Branch-Broad Run | 11 | 0.192 |
| Neabsco Creek | 5 | 0.000 |
| Middle/Upper Bull Run | 5 | 0.000 |
| Belmont Bay-Occoquan | 2 | 0.000 |
| Quantico / Kettle Run / Powells / Occoquan Bay | 4 | 0.000 |
| **county total** | **32** | **300.237 MGD** |

Dominion Possum Point (VA0002071) alone is **300 MGD**. The entire rest of the
county's permitted discharge is **0.237 MGD**. For scale: the whole 243-building
fleet's Scope 1 is ~7 MGD delivered today, ~45 at buildout. **The largest water
flow in Prince William County is a power station** — the Scope 2 activity — and it
is permitted, metered and monitored, while the load driving new generation is not.
That is the paper's thesis restated in EPA's own numbers.

**(c) Possum Point's permit expired on 2018-04-02.** Effective 2013-04-03,
expiration **04/02/2018** — eight years administratively continued, on a Major
permit, `Listed for Impairment = Y`, discharging to "ASH POND E, INTERNAL OUTFALL -
SEAL BASIN, POTOMAC RIVER, QUANTICO CREEK" across 27 pollutants including arsenic,
mercury, selenium, thallium and hexavalent chromium (coal-ash legacy; the station
is now gas). Peak outfall flow 313 MGal/yr. **No wastewater-temperature values are
populated** — so thermal discharge cannot be assessed from this file.

**(d) ECHO carries EJ screening fields I have not used.**
`Percent People of Color (3 mi)` and `Percent Low Income (3 mi)`, populated for 31
of 32 facilities. County-facility means: **54.6% people of color, 19.8% low
income.** Possum Point sits at **67.8% / 18.9%** — the largest discharge in the
county is in a markedly more people-of-color area than the county's permitted-
facility average. This is a ready-made, EPA-sourced input for plan item H1
(exposure overlay) that needs no construction on my part.

### 30.2 `ICIS_MASTER_GENERAL_PERMITS.csv` (2,838 rows) — national, structural
Master general-permit registry, all states. 27 columns including
TOTAL_DESIGN_FLOW_NMBR, ACTUAL_AVERAGE_FLOW_NMBR, STATE_WATER_BODY_NAME,
MASTER_EXTERNAL_PERMIT_NMBR, RAD_WBD_HUC12S. This is the lookup that explains what
the VAR10/VAR05/VAG prefixes in Part 29.3 *are*; it is a dictionary, not evidence.

### 30.3 `observations-759582.csv` (3,055 rows) — iNaturalist, PWC
40 columns; research-grade and casual citizen-science species observations with
lat/lon, `iconic_taxon_name`, `quality_grade`, `coordinates_obscured`. Backs the
`water_context` iNaturalist counts already in the facility profiles. Caveat for any
use: `coordinates_obscured` and the `private_latitude`/`private_longitude` columns
mean some points are deliberately displaced — do not treat positions as exact, and
do not publish the private columns.

### 30.4 `rt_hrl_lmps.csv` is CORRUPT — 15 bytes, contents `[object Object]`
A failed browser fetch that stringified a JS object instead of writing CSV. It was
meant to hold PJM real-time hourly LMPs. **There is no LMP data in this repo.**
Any analysis assuming marginal-price data exists must be re-scoped or the file
re-fetched. **ACTION: delete or re-fetch; do not let it sit looking like data.**

**RESOLVED 2 Aug 2026 — deleted.** Re-fetch was checked first and is not possible:
`GET https://api.pjm.com/api/v1/rt_hrl_lmps` returns **401 Unauthorized** with no
anonymous path (Data Miner 2 requires an `Ocp-Apim-Subscription-Key`; the only keys
in this repo are `GROQ_API_KEY` and `VERCEL_OIDC_TOKEN`). No values were fabricated.
Dependency sweep across `*.py`, `*.ts/tsx`, `*.json`, `*.md` and `docs/` found
**nothing reading the file** — the `lmp`/`marginal` hits in `src/` are
`gal_per_mwh` water-intensity fields, not prices. The marginal-generation argument
(§16) rests on **SOM 2023 Table 3-69 fuel shares**, not LMPs, and is unaffected.
One doc does assume LMP data: `docs/Overlay_Specification.md` — see 30.4a.

### 30.4a `da_hrl_lmps.csv` — assumed by the Overlay Spec, never present
Separate from the above (DA = day-ahead, not RT). `docs/Overlay_Specification.md`
lists `Data Center Intelligence/da_hrl_lmps.csv` ("345k DA hourly") as a live input
to the **Estimated Development Cost** sub-score (opex basis for amortization), to
**Power Readiness** ("Queue depth + LMP basis"), to a "Recent LMP $/MWh" terminal
column, and to two rows of the timeline simulation ("LMP forward"). **That file has
never existed in this repo, nor has the `Data Center Intelligence/` folder** — the
spec describes the Vira Systems Decision Terminal, a broader product scope than the
water atlas that was actually built. Those four sub-score inputs are unbacked as
written and must be re-scoped before the spec is used as a build source of truth.

### 30.5 `station.csv` (75 rows) — the monitoring network
2 USGS + 32 VA DEQ (`21VASWCB`) + 41 Chesapeake Monitoring Cooperative volunteer
sites. DEQ IDs encode stream and river mile: `1ABRU001.59` and `1ABRU011.57` are
**Broad Run** at RM 1.59 and 11.57; also Bull Run (`1ABUL`), Occoquan (`1AOCC`),
Quantico (`1AQUA`), Neabsco (`1ANEA`), Cedar Run (`1ACER`), Powells (`1APOW`),
Catharpin (`1ACAA`), Hooes (`1AHOO`), South Fork Quantico (`1ASOQ`). **Broad Run —
the basin carrying 166 of 243 buildings, whose flow gage died in 1986 (Part 27) —
has two active DEQ water-quality stations.** These are quality not discharge
stations, but they establish that the basin is currently monitored for *something*,
which sharpens rather than softens the Part 27 point: the county measures Broad
Run's chemistry today and its flow only up to 1986.

---

## Part 31 — the TE-model CSVs. An independent validation of the two Scope 2 constants, and a new headline comparison.

### 31.1 `Version_1.2_2015_TE_Model_Estimates.csv` — not data
1,124 rows, 2 columns. A ScienceBase **metadata/readme** stub for the USGS 2015
thermoelectric model release. No estimates in it. Catalogued, nothing to extract.

### 31.2 `usgs_te_water_2008-2020_VA.csv` — 302 plant-years, 33 Virginia plants
Columns: Plant.Code, **huc_12**, YEAR, Plant.Name, County, State,
Name.of.Water.Source, coolingType, ModelType, Plant.level_dom_fuel, general_mover,
Net.Generation.Year.To.Date, **cu_mgd / cu_lower_mgd / cu_upper_mgd**,
**wd_mgd / wd_lower_mgd / wd_upper_mgd**. Consumption *and* withdrawal, each with
uncertainty bounds, at HUC12, per plant, per year, 2008-2020.

Cooling types: Recirculating Tower 207, Once-through fresh 50, Once-through saline
33, Complex 12. Fuels: coal 122, gas 68, biomass 55, multi-fuel 30, nuclear 26,
oil 1.

### 31.3 VALIDATION — my two most important Scope 2 constants, checked out-of-sample

Pooling every Virginia plant-year (consumption / generation):

| fuel | n | **empirical gal/MWh** | lower | upper | **model uses** | error |
|---|---:|---:|---:|---:|---:|---:|
| **nuclear** | 26 | **387.9** | 302.6 | 473.2 | **391** | **+0.8%** |
| **gas** | 68 | **191.5** | 155.8 | 232.8 | **196** | **+2.3%** |
| coal | 122 | 340.4 | 278.1 | 402.7 | — | — |
| biomass | 55 | 763.9 | 626.4 | 901.5 | — | — |
| multi-fuel | 30 | 110.6 | 87.1 | 134.0 | — | — |

**Both constants land inside 2.5% of an independently constructed USGS model over
302 Virginia plant-years, and well inside its uncertainty band.** This is a genuine
out-of-sample check — the USGS TE model was not used to set these factors. It
belongs in the robustness appendix (plan item R1).

By cooling type: once-through fresh 449.8, recirculating tower 332.4, complex
115.5, **once-through saline 0.0** gal/MWh.

### 31.4 The nuclear number needs a caveat I did not have

North Anna alone, 13 consecutive years, is **735.6 to 741.2 gal/MWh** — extra-
ordinarily stable (2020: cu 31.84 MGD, wd 1,692.35 MGD, gen 15.8 TWh -> 735.6).
The pooled nuclear figure is 387.9 only because **Surry consumes 0.00 MGD** —
once-through saline on the tidal James. The 391 in the model is therefore a
*two-plant fleet average*, and it reproduces the right total only because North
Anna happens to be ~53% of Virginia nuclear generation.

METHODOLOGY:906 already states that the whole nuclear share lands on Lake Anna.
That is right, and the arithmetic works, but the two facts must be stated together
or the factor looks wrong by 2x to anyone who checks North Anna directly.
**ACTION: state 391 = fleet average of North Anna 738 and Surry 0.**

### 31.5 Virginia's entire thermoelectric fleet consumes 49.40 MGD

Summing all 18 plants reporting in 2020: **consumption 49.40 MGD, withdrawal
3,431.80 MGD** (consumption is 1.4% of withdrawal — the withdrawal/consumption gap
this project keeps insisting on, in Virginia's own generation data).

Against the model, rolled up by build status:

| | n | eff. IT MW | Scope 1 | Scope 2 | Scope 3 | total | **Scope 2 vs all-VA thermo** |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Completed (today)** | 54 | 921 | 0.21 | **6.23** | 0.64 | **7.09** | **13%** |
| Completed + under constr. | 85 | 2,230 | 0.60 | 15.04 | 1.56 | 17.20 | 30% |
| **All 243 (full buildout)** | 243 | 6,031 | 1.64 | **40.35** | 4.20 | **46.19** | **82%** |

**This confirms the labelling is right.** The 7.09 MGD completed-only figure is
exactly the "about 7 million gallons per day today" in PLAIN_SUMMARY_AGU26.txt, and
46.19 is the "rising toward 45 million at full buildout" / METHODOLOGY plug-in
central. No error. Worth recording explicitly because the 46.19 headline reads as a
present-day number until you check, and 120 of the 243 buildings are **Planned** —
`occupancy_ramp` returns 1.0 when `occupancy_date is None`, so planned buildings are
correctly counted as fully energized *at buildout*, which is what that column means.

**The new result:** at full buildout, Prince William County's data centers alone
would need Scope 2 cooling water equal to **~82% of what Virginia's entire
thermoelectric fleet consumed in 2020** — and today's completed fleet is already at
13%. Same caveat as every basin number here: PWC draws on PJM, so this is a
**scale comparison, not an attribution**; the generation and its water need not be
in Virginia. Stated that way it is defensible and it is the most legible number
the project has produced.

### 31.6 Possum Point — reconciling ECHO against USGS
USGS 2020: Possum Point, gas, **Recirculating Tower**, cu **1.76 MGD**, wd **2.46
MGD**, HUC12 020700110106, Potomac River. ECHO (Part 30.1) reports "actual average
facility flow" **300 MGD**. These are not in conflict — the ECHO figure is a
permitted/reported facility flow carrying legacy once-through capacity, not
consumption. **Qualifies Part 30.1(b): Possum Point is the largest permitted *flow*
in the county, but consumes 1.76 MGD.** The 300 MGD must never be set beside the
fleet's consumptive numbers. **ACTION: annotate 30.1(b).**

`huc_12` in this file is also a ready-made, citable plant->basin lookup covering
every Virginia plant 2008-2020 — better provenance than the hand-built map flagged
as a risk in the analysis plan (B1).

---

## Part 32 — `PlanningQueues.xlsx`. The JLARC-vs-LBNL nuclear tension, resolved.

Not county planning cases as the filename suggests — this is the **PJM
interconnection queue**, 9,263 projects, 43 columns, plus a 45-row
`Definitions-Mapping` sheet read verbatim (defines MFO = Maximum Facility Output,
MW Energy = winter net, MW Capacity = summer net, the study sequence
Feasibility -> System Impact -> Facilities -> ISA/GIA -> CSA, and the withdrawal
codes CIW/CMN/QNR/WBSD).

Queue-wide status: Withdrawn 6,180; In Service 1,238; Active 898; Engineering and
Procurement 264; Confirmed 224; Retracted 131; Suspended 98; Under Construction 96;
Deactivated 80. **Two-thirds of everything ever proposed was withdrawn** — the base
rate against which any pipeline claim must be discounted.

### 32.1 There is no new nuclear in Virginia. None.

All 78 nuclear projects in the entire PJM queue were enumerated. Virginia has
**nine**, and every one is either an existing unit or dead:

| project | county | status | MW |
|---|---|---|---:|
| S108/S109 | Louisa | **In Service** | North Anna uprates, **20 MW each** |
| S110/S112 | Louisa | **In Service** | North Anna uprates, **65 MW each** |
| S111/S113 | Surry | **In Service** | Surry uprates, **15 MW each** |
| S114/S115 | Surry | **In Service** | Surry uprates, **75 MW each** |
| **Q65** | **Louisa** | **WITHDRAWN** | **1,594 — North Anna Unit 3** |

> **CORRECTED 2026-08-03 (see Part 34.1).** The MW figures above were originally
> transcribed from PJM's `MFO` field, which is *Maximum Facility Output* -- the
> **total** output of the facility after the request, not the increment. LBNL's
> `mw_1` gives the incremental capacity, and it is what belongs in a table about
> what was *added*. Virginia's nuclear queue history since 2007 is therefore
> **350 MW of uprates at existing units**, not ~7,900 MW of anything. The
> conclusion is unchanged and in fact sharper: zero new nuclear units, and North
> Anna 3 (Q65, 1,594 MW, proposed online 2024) withdrawn.

The five *Active* nuclear projects anywhere in PJM are Three Mile Island (PA,
restart), Braidwood, Byron, LaSalle (IL) and Salem (NJ) — all uprates or restarts
of existing plants, **none in Virginia, none new-build**.

**JLARC's model assumes +24 TWh of new nuclear generation. The PJM interconnection
queue is the only physical pathway by which new generation connects to the grid,
and it contains zero new nuclear in Virginia — with the one proposed unit, North
Anna 3, formally withdrawn.** This closes the tension flagged after the LBNL read
(44 MW active nuclear in PJM) and closes it decisively, from PJM's own register.

Consequence for this project: the Scope 2 **marginal** case is the defensible one.
New data-center load in Virginia cannot be served by nuclear that is not in the
queue. It is served by what *is* queued.

### 32.2 What Virginia actually has queued (229 active projects, 41,105 MW MFO)

| fuel | projects | MW Energy | **MFO** |
|---|---:|---:|---:|
| **Natural Gas** | 26 | 608 | **13,422** |
| **Storage** | 83 | 8,068 | **11,113** |
| **Solar** | 97 | 6,782 | **10,645** |
| Natural Gas; Other | 3 | 1,552 | 3,078 |
| Offshore Wind | 2 | 1,653 | 1,653 |
| Solar; Storage | 15 | 690 | 1,017 |
| Wind | 2 | 78 | 156 |
| Other | 1 | 20 | 20 |
| **nuclear** | **0** | **0** | **0** |

Gas is the single largest queued category by MFO. Storage and solar are large but
storage generates nothing — it shifts. This is the empirical basis for the
marginal-gas assumption in the Scope 2 module, sourced to PJM rather than assumed.

### 32.3 Prince William County: 30 projects, and the active set is gas + batteries

Twelve active/under-construction, **1,218 MW MFO total**:
- **668 MW Natural Gas** (AH1-696, Possum Point 230kV, Active)
- **550 MW Storage** across 11 projects — eight of them at Possum Point
  (60, 60, 100, 100, 30, 30, 55, 55 MW) plus three under construction at
  Vint Hill and Railroad (20 MW each)

Confirms METHODOLOGY:1491's note about battery storage clustering at Possum Point,
now with the exact register. **Every new generation project in Prince William County
is either gas or batteries.** Batteries consume no water; the gas does, and it
lands in the Potomac basin — the same basin the buildings sit in. The county's own
marginal generation is therefore in-basin, which is the one place where the
displacement thesis reverses.

Historical PWC entries also record the withdrawn 960 MW Burches Hill 500kV, an
806 MW oil unit at Possum Point, and 690 MW at Gainesville 230kV.

**ACTIONS:** (a) ledger `pjm_queue_zero_new_nuclear_va` and
`pjm_queue_va_active_fuel_mix`; (b) cite the withdrawn North Anna 3 (Q65) directly
against JLARC's nuclear assumption; (c) the 67% queue-wide withdrawal rate is the
discount any forward-pipeline claim needs (plan item G3).

---

## Part 33 — the four EIA-861M distributed-generation workbooks.

`net_metering2026.xlsx`, `net_metering2025.xlsx`, `net_metering_2024.xlsx`,
`non_netmetering_2024.xlsx`. EIA-861M. Four-row header: technology block
(Photovoltaic / Battery / Wind / Other / All Technologies) x metric (Capacity MW,
Customers, Energy Sold Back MWh, Virtual Capacity above/below 1 MW, PV-Paired and
Not-PV-Paired battery capacity/installations/energy) x sector (Residential,
Commercial, Industrial, Transportation, Total). 117 columns. Six sheets each:
Utility_Level-States, Utility_Level-Ter, Utility_State-TPO, Utility_Total-TPO,
Monthly_Totals-States, Monthly_Totals-US. The 2026 file is partial — **January and
February 2026 only**.

### 33.1 NOVEC does not report. The Dominion/NOVEC split cannot be closed from here.
Only **eight** Virginia entities appear: A & N Electric Coop, Appalachian Power,
Kentucky Utilities, Shenandoah Valley Electric Coop, **Virginia Electric & Power
(Dominion)**, Virginia Tech Electric Service, Rappahannock Electric Coop, and a
state "Adjustment" row. **Northern Virginia Electric Cooperative is absent**,
though it serves a substantial part of Prince William County. The open NOVEC/
Dominion Scope 2 question cannot be resolved from this dataset — record that and
stop treating it as a lead.

### 33.2 Distributed solar cannot offset this load, quantitatively
Virginia, December 2025, all net-metered distributed generation:
**Photovoltaic 725.6 MW, Wind 0.3, Other 0.8 — total 727.7 MW nameplate.**
Dominion alone is 513-563 MW of that; every co-op and municipal is the remainder.

Against the model's **6,031 MW** of effective IT load at full buildout:
- **12.1% on a nameplate basis**
- on an *energy* basis, applying a ~14% Virginia solar capacity factor against a
  data center's ~100% duty cycle, **roughly 1.7%**

Both bases should be quoted together; the nameplate figure alone flatters solar by
about 7x. Either way the conclusion is the same and it is worth one sentence in the
paper: **all net-metered distributed generation in the Commonwealth of Virginia
produces on the order of 2% of the electricity one county's data centers would
consume at full buildout.** Rooftop solar is not a lever on this problem.

### 33.3 The backup-generator reporting gap — 2,000x

`non_netmetering_2024.xlsx` covers utility-scale-adjacent distributed generation
by prime mover: Photovoltaic, Battery, Wind, Hydroelectric, Fuel Cells, **Internal
Combustion**, **Combustion Turbine**, Steam, Other, with a dedicated
**"Capacity Back-up Only"** column. Only four Virginia entities report at all.
December 2024 totals: Dominion **11.07 MW**, Appalachian 1.637, Rappahannock 1.55,
State Adjustment 0.312 — about **14.6 MW statewide**. Of Dominion's 11.07,
**"Capacity Back-up Only" is 1.855 MW.**

Prince William County's data centers hold **3,795 MW of permitted backup generator
capacity** across 14 VA DEQ air permits — the tier-1 evidence this whole model is
built on.

> **3,795 MW of permitted backup generation in one county, against 1.855 MW of
> "backup only" capacity reported for the whole of Dominion Virginia in EIA's
> distributed-generation survey. A factor of ~2,000.**

Data-center backup generation is essentially **invisible to EIA**. It is visible to
the state air-permit program, because it is regulated as an air-emissions source
rather than as generation. This is the same structural finding as Part 29 in a
different register: **the facility is captured by whichever agency has a reason to
look, and no agency has a reason to look at it as an energy or water system.**
Three independent instances now — NPDES (wrong instrument), NAICS (wrong code),
EIA-861M (not surveyed).

**ACTIONS:** (a) ledger `eia_dg_va_total_727mw` and
`eia_backup_gap_3795mw_vs_1p855mw`; (b) 33.3 is a third leg for the disclosure
argument and is stronger than either existing leg because the ratio is enormous
and both numbers are official; (c) close the NOVEC lead as unresolvable here.

---

## Part 34 — `LBNL_Ix_Queue_Data_File_thru2025.xlsx`. Confirms Part 32, and corrects it.

Rand, Cheyette, Gorman, Wiser, Seel, Kahrl (LBNL) with Talley and Zhang
(Interconnection.fyi), **May 2026**, DE-AC02-05CH11231. 43 sheets. Narrative sheets
(Introduction, 00. Background + Methods, 01. Balancing Areas, 04. Data Codebook)
read verbatim. Coverage: **7 ISO/RTOs + 50 non-ISO balancing areas, ~98% of US
installed capacity**, requests through end-2025, transmission-connected only —
explicitly **"Does not include load interconnection"**, so data centers as *load*
are absent by construction; only co-located transmission-connected generation
appears. Header is on **row 2**, not row 1.

**38,201 requests.** Status: withdrawn 24,221, active 8,513, operational 4,789,
suspended 668, unknown 10.

### 34.1 CORRECTION to Part 32.1 — MFO is not new capacity

PJM's own file reports **MFO = Maximum Facility Output**, the *total* output of the
facility after the request. LBNL's `mw_1` is the **incremental** capacity. For
uprates of existing plants these differ enormously, and I used MFO:

| unit | Part 32 (PJM MFO) | **LBNL mw_1 (actual new MW)** |
|---|---:|---:|
| S108 North Anna | 1,023 | **20** |
| S109 North Anna | 1,030 | **20** |
| S110 North Anna | 1,023 | **65** |
| S112 North Anna | 1,030 | **65** |
| S111/S113 Surry | 932 each | **15 each** |
| S114/S115 Surry | 932 each | **75 each** |

So Virginia's nuclear queue history since 2007 is **350 MW of uprates at existing
units**, not ~7,900 MW of anything. Part 32's table read as though those were
capacity events; they were not. **The conclusion is unchanged and in fact sharper:
zero new nuclear units, 350 MW of uprates, and North Anna 3 (Q65, 1,594 MW,
proposed online 2024) withdrawn.** Same correction applies to PWC: AA2-079 at
Possum Point is **28 MW** incremental, not 668 MW.

**ACTION: fix the Part 32.1 table and any ledger entry built on MFO.**

### 34.2 Virginia's active queue, on LBNL's cleaned basis

271 active requests, **28,814 MW** (vs the 41,105 MW MFO figure in Part 32 — the
gap is exactly the uprate/replacement double-count):

| type | projects | MW |
|---|---:|---:|
| Solar | 143 | 12,200 |
| Battery | 96 | 9,907 |
| **Gas** | **6** | **2,729** |
| Offshore Wind | 3 | 2,489 |
| Solar+Battery | 19 | 1,250 |
| Wind | 3 | 218 |
| Other | 1 | 20 |
| **Nuclear** | **0** | **0** |

Prince William's active set on LBNL's basis is **entirely batteries** — 670 MW
across 12 projects, ten of them at Possum Point. LBNL (through 2025) does not carry
the 668 MW Possum Point gas request that appears as Active in the PJM file; that is
a **snapshot-vintage difference**, not a contradiction — record it, do not reconcile
it away.

### 34.3 The completion rate — the discount every pipeline claim needs

Sheets 23-25 read verbatim. Capacity-weighted historical outcomes:

| region | operational MW | withdrawn MW | **completion rate** |
|---|---:|---:|---:|
| **PJM** | 83,242 | 486,990 | **14.6%** |
| CAISO | 37,233 | 345,081 | 9.7% |
| ERCOT | 83,610 | 196,414 | 29.9% |
| MISO | 70,954 | 381,790 | 15.7% |
| Southeast | 47,436 | 340,576 | 12.2% |

By generator type: **Nuclear 19.2%** (12,540 operational vs 52,837 withdrawn),
**Gas 17.6%**, Solar 13.5%, Wind 16.8%, Battery 9.7%.

**Only about one MW in seven that enters the PJM queue ever reaches operation.**
Any statement in this paper about a "pipeline" of forward capacity must carry that
discount explicitly, and the plan's G3 triangulation should compare
withdrawal-adjusted figures, not raw queue totals. The 2025 request cohort alone is
441,917 MW active — a number that is meaningless without the 14.6%.

Note also the trend in sheet 23: operational capacity from recent request years is
collapsing (2022 cohort: 3,586 MW operational vs 366,353 withdrawn; 2024: 110 MW
operational). Partly maturity, but the direction is unmistakable — queues are
lengthening and clearing less.

---

## Part 35 — the GeoJSON layers, part 1. `Data_Center_Buildings.geojson` — the spine.

27 GeoJSON files, ~1.7 GB. Scope note, stated plainly: I am reading **every
property of every feature** exhaustively — the semantic content — and
characterising geometry structurally. The bulk of those bytes are coordinate
floats; I am not transcribing 1.7 GB of decimal degrees and will not pretend to.

### 35.1 Structure
`FeatureCollection`, **243 features, all `Point`** — no CRS member, so WGS84 per
spec. **The buildings have no footprint polygons.** Every floor-area number in this
project therefore comes from an *attribute*, never from geometry. 27 property keys.

Status: **Planned 120, Completed 54, Pending 36, Under Construction 31, Under
Review 2** — matching the model's rollup exactly (Part 31.5).
`DCOOD` (Data Center Opportunity Overlay District): **Yes 172 / No 71** — 29% of
the fleet sits outside the overlay district.

### 35.2 Five different floor-area fields, none complete

| field | nonzero | sum sq ft |
|---|---:|---:|
| `GFA` | 202 | 79,057,679 |
| `ApprovedGFA` | 108 | 132,213,255 |
| `BPGFA` | 86 | 21,961,627 |
| `REATaxedGFA` | 74 | 17,046,382 |
| `PermittedGFA` | 12 | 3,732,326 |

`ApprovedGFA` sums to **1.7x** `GFA` and has a max of 3.5M sq ft against `GFA`'s
1.7M — it is a **campus/case-level** entitlement figure, not a building figure.
Anyone summing `ApprovedGFA` across features double-counts. `GFASource` is also
dirty: **"Proffer" 87 and "Proffers" 3** are the same category split by spelling,
alongside Site Plan 67, Building Permit 20, Estimated 16, Real Estate Assessments 11.

### 35.3 41 buildings have GFA = 0, and 34 of them are built and running

`GFA` min is **0**, not null — 41 features. Thirty-four are **Completed**, seven
Under Construction. They are not obscure: Iron Mountain VA-1 to VA-7 and VA-10,
Amazon IAD-73, IAD-74, IAD-55, IAD-64, IAD-64 Ext, IAD-84, Bethlehem DC18/19/20/23,
Thomasson Barn 1-2, QTS Manassas DC1/2/3/5/6, Stack NVA02A-G, CloudHQ Manassas 1-2,
Equinix DC14, Verizon Manassas, Village Place 1-4.

**The county's own authoritative data-center building layer records zero floor area
for 34 operating data centers.** `GFASource` is blank for nearly all of them —
the field was never populated, not estimated and zeroed.

**How the model survives this:** the GFA ladder falls through to `REATaxedGFA`, the
tax assessor's figure, for all 41. Verified end to end — every one resolves, and
**no building in the model has zero effective IT MW**. Eighteen still reach tier-1
`permit_generator_capacity`; 23 fall to tier-3 `fitted_gfa_model`. Together they
carry **780 MW, 13% of the fleet's effective IT load**.

That dependency should be stated in the paper: **without the real-estate assessment
layer, an eighth of the county's data-center capacity would be unestimable from the
county's own data-center dataset.** It is a fourth instance of the Part 33 pattern —
the facility is legible only to the agency that has its own reason to look, here the
tax assessor.

### 35.4 `YearBuilt` = 0 — checked, does not bite
`YearBuilt` is populated for 72/243, and **17 carry the sentinel 0** (mean 1543 is
the giveaway). All 17 are **Planned with `OCCDate` = None** — Iron Mountain VA-8/9,
CloudHQ MCC 3/4/5/6B/6C, Iron Mountain Manassas Point DC1-3, Microsoft Azure
MNZ02/04/05/06, Corscale Gainesville Crossing 4-5, NTT VA12, Gainesville RLC.
`_occupancy_date` in `build_facility_profiles.py` is status-gated to
Completed/Finaled, so `datetime.date(0, 7, 1)` — which would raise — is never
reached. **No bug. The gate added during the fit-out work is load-bearing; do not
remove it.**

`OCCDate` is populated for only **56/243** (epoch-ms), which is why the ramp
falls back to `YearBuilt` for completed buildings lacking it.

### 35.5 Multiple buildings per parcel, confirmed
`GPIN` populated 203/243 with **125 distinct** — up to 8 buildings on one parcel
(7496-63-4453). Forty features carry **no GPIN at all**. Parcel-level joins will
therefore silently drop 40 buildings and over-aggregate the rest; the
building-level design of this project is the right one and this is the evidence for
saying so.

---

## Part 36 — `Data_Center_Projects` and `SURFACE_WATER_TEMPERATURE`.

### 36.1 `Data_Center_Projects.geojson` — 81% of entitled floor area is unbuilt

51 campus polygons (43 Polygon, 8 MultiPolygon), CRS84, 20 properties.
Status: Under Construction 18, Planned 14, Completed 14, Pending 5.
Magisterial district: **Brentsville 29, Gainesville 14, Coles 7, Potomac 1**.
Zoning: PBD 17, M-2 14, M-1 8, plus mixed designations. DCOOD Yes 40 / No 11.
Acreage 7.3 to 884, total **5,308 acres**.

The two fields that matter are `PlannedGFA` and **`RemainingGFA`** — entitled floor
area not yet built, straight from the county:

| status | campuses | PlannedGFA | **RemainingGFA** |
|---|---:|---:|---:|
| Completed | 14 | 7,833,818 | **0** |
| Under Construction | 18 | 28,576,096 | 25,128,643 |
| Planned | 14 | 43,405,088 | 38,648,713 |
| Pending | 5 | 5,317,980 | 5,317,980 |
| **total** | **51** | **85,132,982** | **69,095,336** |

Completed campuses correctly carry zero remaining — the field is maintained, not
stale. Implied built floor area is **16.0M sq ft of 85.1M entitled: 18.8%.**

> **ARITHMETIC CORRECTION 2026-08-03.** This line originally read "17.8M sq ft ...
> 21%", and the unbuilt share was quoted as 79% throughout. 85,132,982 −
> 69,095,336 = **16,037,646**, not 17.8M. The correct unbuilt share is
> **81.2%**, not 79%. Every downstream use has been updated; the direction and
> the argument are unchanged.

**81.2% of entitled data-center floor area in Prince William County is not yet
built** — a 5.3x multiple on floor area, from the county's own layer, with no
modelling. It independently corroborates the buildout framing in Part 31.5
(7.09 MGD today -> 46.19 at buildout, a 6.5x multiple on water; the water multiple
is larger because newer buildings are denser per square foot). **This is the
cleanest available anchor for the growth scenarios (plan item G1) and it should
replace any assumed buildout multiplier.**

### 36.2 `SURFACE_WATER_TEMPERATURE.geojson` — a DEQ trend analysis, not raw data

413 point stations statewide. `Variable` = **CTEMP**, `Parameter` = SURFACE WATER
TEMPERATURE, one value each of `Tau` (Kendall), `TheilSen_slope`, `Intercept`,
`Pvalcovs`, `Number_obs`, `Year1`, `Year2`. Period **2002/2003 to 2022**, median
113 observations per station. Waterbody: STREAM 257, ESTUARY 130, RESERVOIR 26.
These are **fitted trends**, not observations — do not treat as a temperature series.

Statewide: mean slope **+0.0329 C/yr** (~**+0.66 C over the 20-year record**).
Only **49 of 413 stations (12%) are significant at p<0.05** — but of those 49,
**47 are warming and 2 are cooling**. Significant warming slopes have a median of
**+0.104 C/yr**. State the 12% honestly; the 47:2 split carries the inference, not
the individual stations.

### 36.3 Broad Run, again

Seventeen stations fall in the Prince William / Occoquan group. **Fifteen of seventeen
have positive slopes**, one is exactly 0.000 (Catoctin Creek) and one is negative
(Pohick Creek, -0.025). A sign test on the 16 non-ties gives 15 of 16, two-tailed
**p = 0.0005** — significant even though most individual stations are underpowered.

> **CORRECTED 2026-08-03.** This paragraph first read "16 of 17 positive ... p ~
> 0.0001". Recounted from `SURFACE_WATER_TEMPERATURE.geojson`: 15 positive, not 16,
> and the correct two-tailed sign-test p is 0.0005. Caught while building Figure 4,
> which computes the counts rather than restating them.

Exactly one is individually significant:

> **`1ABRB002.15`, Broad Run: +0.094 C/yr, p = 0.030, n = 111 — about +1.9 C over
> the record. It is the only Prince William stream with a statistically significant
> warming trend.** The second Broad Run station, `1ABRU001.59`, is +0.090 C/yr at
> p = 0.09.

Broad Run now carries four independent findings from four unrelated sources:
1. **166 of 243 buildings** drain to it (basin attribution).
2. Its flow denominator comes from a gage **decommissioned in 1986** (Part 27).
3. It is the **only county stream with significant warming**, +0.094 C/yr (here).
4. It is in the **worst drought of the 132-year county record** (Part 28.6).

Warmer water holds less oxygen, has less assimilative capacity for any thermal
load, and reduces cooling efficiency at the intake — so all four point the same
way. **Broad Run is the paper's binding case and should be named as such rather
than left as one row in a basin table.**

**ACTIONS:** (a) ledger `pwc_remaining_entitled_gfa_69m` and
`broadrun_ctemp_trend_0094`; (b) use RemainingGFA as the G1 buildout anchor;
(c) promote Broad Run to a named case in the abstract.

---

## Part 37 — the hydrology layers. Broad Run's concentration, quantified.

### 37.1 `Watersheds.geojson` — the county's own basin denominators

222 sub-watershed polygons, CRS84, 18 properties (four audit fields —
CreatedUser/Date, LastEditedUser/Date — are **entirely empty**, 0/222).
`ACRES`, `ShapeSTArea`, `gisdbPUBLICWORKSWatershedHUC10AREA` and `PERIMETER`/
`ShapeSTLength` are duplicate pairs. 34 distinct `WMPlanNumber` watershed-
management-plan units.

Total **230,709 acres = 360 sq mi**, consistent with Prince William's ~348 sq mi
land area plus tidal fringe. Ten named watersheds; **eight polygons (5,764 acres)
carry no `WatershedName` at all**:

| watershed | sub-basins | acres | sq mi | share of county |
|---|---:|---:|---:|---:|
| **BULL RUN** | 61 | 52,791 | 82.5 | **22.9%** |
| **BROAD RUN** | 50 | 45,997 | 71.9 | **19.9%** |
| OCCOQUAN RIVER | 28 | 31,390 | 49.0 | 13.6% |
| CEDAR RUN | 22 | 30,055 | 47.0 | 13.0% |
| QUANTICO CREEK | 21 | 25,640 | 40.1 | 11.1% |
| NEABSCO CREEK | 12 | 14,210 | 22.2 | 6.2% |
| POWELLS CREEK | 8 | 11,534 | 18.0 | 5.0% |
| CHOPAWAMSIC CREEK | 7 | 9,549 | 14.9 | 4.1% |
| (unnamed) | 8 | 5,764 | 9.0 | 2.5% |
| MARUMSCO CREEK | 3 | 2,741 | 4.3 | 1.2% |
| FARM CREEK / MARUMSCO | 2 | 1,038 | 1.6 | 0.4% |

### 37.2 The concentration number the basin table was missing

Crossing this against `basin_stress.json`:

| watershed | buildings | % of buildings | % of county land | **concentration** |
|---|---:|---:|---:|---:|
| **BROAD RUN** | **166** | **72.5%** | 19.9% | **3.64x** |
| BULL RUN | 61 | 26.6% | 22.9% | 1.16x |
| QUANTICO CREEK | 2 | 0.9% | 11.1% | 0.08x |

**Broad Run holds 72.5% of the county's data centers on 19.9% of its land — a
3.6x concentration.** Bull Run, the *larger* watershed, is at parity. Every other
basin is essentially empty. This is the missing sentence in the basin analysis:
the exposure is not merely uneven, it is concentrated 3.6-fold into the single
basin that is simultaneously ungaged since 1986, significantly warming, and in the
worst drought of the instrumental record.

### 37.3 A suspicion I checked and dropped

I suspected Broad Run had been dropped from DEQ's **current** ambient monitoring
plan, because my first PWC bounding box returned no Broad Run station. **That was
my filter, not the data.** `Water_Quality_Monitoring_Plan_Stations_(Current)` does
contain Broad Run: `1ABRU001.59` (lat 38.6920, in the county) and `1ABRB002.15`
(lat 39.0467, the upper reach in Loudoun, above my bbox). No finding. Recording the
false lead so it is not re-chased.

What is true: Broad Run has **exactly two** ambient stations in the current
statewide plan, and `1ABRB002.15` is the one carrying the significant warming trend
from Part 36.3.

### 37.4 `Water_Quality_Monitoring_Plan_Stations_(Current).geojson`

**1,305 point stations statewide** (not PWC-only), 38 properties. Station types:
STREAM 906, ESTUARY 186, RESERVOIR 100, **WELL 13, SPRING 10**. Purpose:
`AMBNT` ambient 1,257 vs `TRGTED` targeted 16. Program codes carry explicit
parameter lists — TR = "Nutrients, Solids, Hardness, Ions, Chlorophyll, Turbidity,
Bacteria" (275 stations), AW = "Nutrients, Bacteria, Field_Parameters" (226),
RB = "Field_Parameters" only (142), FP = benthic macroinvertebrates (78),
IM = benthic stressors (60).

**Note what is absent from every parameter list: flow, withdrawal, consumption, and
temperature as a monitored quantity.** The commonwealth's ambient network measures
water *chemistry* comprehensively and water *quantity* not at all. That is the
same structural point as Part 27 (gages decommissioned 1981/1986) arriving from the
monitoring-design side rather than the instrument side, and it is worth one line in
the paper: **the state monitors what is in the water, not how much of it there is.**

84 stations statewide carry the `1A` northern-Virginia prefix; the county's share
of the current plan is roughly two dozen.

---

## Part 38 — the regulatory layers, part 1. NOVEC is building substations right now.

### 38.1 `Planning_Pending_Cases.geojson` — 145 live cases

124 Polygon + 21 MultiPolygon, CRS84, 16 properties (`EnergovID` is **entirely
empty**, 0/145). Case types: **REZ 67, SUP 45, PRA 15, CPA 11, PFR 7**.
Magisterial district: **Brentsville 52**, Coles 25, Potomac 21, Gainesville 15,
Neabsco 11, Woodbridge 11, Occoquan 10. Total **14,823 acres** pending, largest
single case 5,717.75 acres. Every feature carries a live
`StaffReportLink` to `eservice.pwcgov.org/planning/documents/<CASE>.pdf` — **145
staff reports, individually addressable, currently unread by this project.**

Nine cases match data-center or grid-infrastructure names, **302 acres**:

| case | type | acres | district | name |
|---|---|---:|---|---|
| SUP2023-00005 | SUP | 58.5 | Brentsville | Gainesville West Data Center |
| SUP2023-00006 | SUP | 58.5 | Brentsville | Gainesville East Data Center |
| REZ2022-00015 | REZ | 51.7 | Potomac | Potomac Technology Park |
| SUP2022-00016 | SUP | 51.7 | Potomac | Potomac Technology Park |
| SUP2025-00009 | SUP | 23.4 | Brentsville | Vint Hill Substation |
| **PFR2026-00007** | PFR | 19.3 | Brentsville | **NOVEC Javelin Substation** |
| **PFR2026-00002** | PFR | 15.2 | Brentsville | **NOVEC Mudel Substation** |
| **SUP2026-00004** | SUP | 15.2 | Brentsville | **NOVEC Mudel Substation** |
| **PFR2025-00013** | PFR | 9.0 | Gainesville | **NOVEC Freedom I-66 Substation** |

### 38.2 This partly reopens the NOVEC question I closed in Part 33.1

Part 33.1 concluded the Dominion/NOVEC split was unresolvable because NOVEC does
not report to EIA-861M. That remains true for *quantities*. But **NOVEC has three
distinct substations in the county's live planning queue right now** — Javelin and
Mudel in Brentsville, Freedom I-66 in Gainesville, all filed 2025-2026, two of them
this year.

Brentsville is simultaneously the district with the most pending cases (52 of 145)
and the most data-center campuses (29 of 51, Part 36.1). **A cooperative does not
file for three substations in the district where the data centers are unless it is
serving a materially growing share of that load.**

So: the split cannot be *quantified* from the sources in hand, but treating the
county's Scope 2 as wholly Dominion is now demonstrably an approximation with a
known direction of error, and the model should say so rather than pass over it.
**ACTION: add a stated limitation; do not silently attribute 100% to Dominion.**

### 38.3 `State_Land.geojson` — 197 parcels
185 Polygon + 12 MultiPolygon, 6 properties only (OBJECTID, GPIN, `owner_cur`,
plus shape fields). Owners: **Commonwealth of Virginia 127**, Virginia Outdoors
Foundation 14, Commonwealth Transportation Commission 8, Commonwealth State Board
7, VDOT 4, and 24 further owner strings. Thin layer — ownership only, no area
attribute, no protection status. Useful for the exposure overlay (H1) as a
constraint mask, nothing more.

### 38.4 Running tally
GeoJSON read so far (8 of 27): Data_Center_Buildings, Data_Center_Projects,
SURFACE_WATER_TEMPERATURE, Watersheds, Water_Quality_Monitoring_Plan_Stations,
Planning_Pending_Cases, State_Land, plus the `.bak` still to diff.
**Remaining (19):** Parcel (481 MB), Stream (124 MB), Stormwater_Segments (111 MB),
Tidal_flow_paths (76 MB), Soil (56 MB), Hydrological_Features (40 MB),
Stormwater_Management_Structures (40 MB), Zoning_Districts (28 MB),
Dam_Break_Inundation (27 MB), Resource_Protection_Areas (26 MB),
Protected_Open_Space (25 MB), Use_Permits (23 MB), Springs_Groundwater (11 MB),
LRLU_Developable_Areas (5 MB), Zoning_Appeals_and_Variances (2 MB),
Virginia_Power_Transmission_Lines_HIFLD (2 MB), Power_Lines_150kv (0.3 MB),
High_Voltage_Transmission_Lines (0.2 MB), Data_Center_Buildings.bak.

---

## Part 39 — RPA, Zoning, Use Permits. The land-side constraint, measured.

### 39.1 `Resource_Protection_Areas_(RPA).geojson` — 13.8% of the county

2,744 Polygon + 3 MultiPolygon, CRS84. **Only 10 properties and almost all are
empty or constant**: `RPA` is the literal string "RPA" on 2,745 of 2,747 (two are
null), `UpdateDate` populated 783/2,747, `created_user` 32/2,747. **There is no
area attribute and no ShapeSTArea** — unlike every other county layer here. Area
had to be computed from geometry.

Reprojected to EPSG:2283 (VA State Plane North, ft); two polygons were invalid and
required `buffer(0)` repair:

> **RPA dissolved area 31,871 acres = 13.8% of the county's 230,709 acres.**
> Raw sum 31,872 ac — the polygons are essentially non-overlapping.

**Building overlay** (note: the buildings layer is *points*, Part 35.1, so these are
centroid distances and therefore **upper bounds on separation** — a footprint can
touch an RPA whose centroid is hundreds of feet away):

| separation | buildings | share |
|---|---:|---:|
| inside an RPA | **2** | 1% |
| within 100 ft | 4 | 2% |
| within 250 ft | 19 | 8% |
| **within 500 ft** | **67** | **28%** |
| **within 1,000 ft** | **149** | **61%** |
| within 2,000 ft | 224 | 92% |

Median distance to the nearest RPA is **822 ft**. The two inside are
**Amazon AWS IAD-11 (Completed)** and **CloudHQ Manassas Corporate Center 7
(Under Review)**.

The honest reading: siting is *not* preferentially in protected riparian buffers —
the ordinance works. But **61% of the fleet sits within 1,000 ft of a protected
stream corridor**, which is the relevant number for the exposure argument (plan
item H1) and is far more defensible than the two-building overlap.

### 39.2 `Zoning_Districts.geojson` — and the headroom is nearly gone

2,208 features (1,995 Polygon, 213 MultiPolygon), 31 districts, **230,595 acres** —
within 114 acres of the watershed layer's 230,709, an independent cross-check that
both layers tile the county.

| district | polys | acres | share |
|---|---:|---:|---:|
| **A-1 agricultural** | 203 | **101,016** | **43.8%** |
| FED federal | 12 | 41,022 | 17.8% |
| RPC planned residential | 64 | 16,965 | 7.4% |
| R-4 | 367 | 12,485 | 5.4% |
| PMR | 109 | 9,609 | 4.2% |
| ... 26 more districts | | | |

The county remains **44% agriculturally zoned** and 18% federal (Quantico, the
Battlefield). `PROFFERS` = Yes on 1,318 polygons / **49,618 acres (21.5%)** — a
fifth of the county carries negotiated conditions, which is the mechanism the PUE
and cooling proffers in the model ride on.

**The number that matters.** Data-center-capable industrial zoning is
M-1 4,799 + M-2 3,146 + PBD 4,108 + PMD 1,559 + M/T 557 = **14,169 acres, 6.1% of
the county**. Against it, `Data_Center_Projects` campuses cover **5,308 acres**
(Part 36.1).

> **Data-center campuses already occupy ~37% of all industrially zoned land in
> Prince William County.**

Combine with Part 36.1 — 81.2% of *entitled* floor area still unbuilt — and the
growth picture sharpens: the sector has secured over a third of the county's
industrial land and built only a fifth of what it is entitled to build on it.
Further expansion runs through rezoning of A-1, which is exactly what the 67
pending REZ cases in Part 38.1 are. **This is the structural reason the buildout
scenario is not speculative.**

### 39.3 `Use_Permits.geojson` — 5,654 permits, and a dirty date column

5,363 Polygon + 291 MultiPolygon, 15 properties. Type: **NCU 4,106**
(nonconforming use), **SUP 1,490**, PUP 50, and **8 blank**. Status: ACTIVE 4,427,
SUPERSEDED 709, VOIDED 223, EXPIRED 186, AMENDED 48, CLOSED 19, ABANDONED 10,
PENDING 1, REVOKED 1.

Data-quality flags, both real:
- **`UsePermitStatus` contains junk categories**: `check` (28), `GRAND` (1), and
  **`SUPSERSEDED` (1) — a misspelling of SUPERSEDED that will silently escape any
  exact-match filter.**
- **`DateApproved` has 27 records at `1899-12-30`** — the Excel/Access zero-date
  sentinel, not a real approval date. Any min()/date-range analysis over this
  column is wrong unless they are excluded. `DateExpired` is populated for only
  1,073 of 5,654.

**ACTIONS:** (a) ledger `rpa_13pct_of_county`, `dc_campuses_37pct_industrial_land`;
(b) use the 61%-within-1000ft figure for H1, not the 2-building overlap;
(c) filter `1899-12-30` and normalise `SUPSERSEDED` before any Use_Permits join.

---

## Part 40 — the large hydrology layers, streamed.

`ijson` is not installed, so I wrote a brace-matching streaming parser
(`scratchpad/stream_gj.py`) that reads **every byte** of each file and parses one
feature at a time without holding the collection in memory. Character counts below
match the on-disk sizes exactly, which is the proof the whole file was consumed.

### 40.1 `Hydrological_Features.geojson` — 40,209,463 chars

**3,979 waterbody polygons** (1 MultiPolygon), **859,708 vertices**, 11 properties.
`ShapeSTArea` sums to 6.368e8 sq ft = **14,619 acres of mapped open water**, the
largest single feature 2.636e8 sq ft (6,051 ac — the Occoquan Reservoir).

**Only 613 of 3,979 features carry a `HydrographicFeatureName` (15%).**
`HydrographicFeatureType` is an **uncoded integer** — values 1, 2, 3, 4, 6, 7, 99
(1,959 are type 2) **with no lookup table anywhere in the corpus**. `DataSource` is
likewise coded (10025, 10016, 10012, 10006) and undocumented. Vintage is visible in
`LastEditDate`: 2,102 features last touched 2023-04-10, 633 in 2018, 387 in 2012,
**106 still carrying 2002-02-01**.

### 40.2 `Stream.geojson` — 124,017,864 chars

**107,424 LineString segments, 1,885,460 vertices.** `ShapeSTLength` sums to
23,754,500 ft:

> **4,499 miles of mapped stream in Prince William County.**

Set that against Part 27: **the county currently gages none of it for flow.** The
Broad Run and Bull Run gages were decommissioned in 1986 and 1981. Four and a half
thousand miles of mapped channel, comprehensively digitised to nearly two million
vertices, and no operating flow measurement on the two basins that carry 99% of the
data centers.

**Only 7,037 of 107,424 segments (6.5%) have a `StreamName`** — 93.5% of the
network is unnamed. Named segments concentrate in Neabsco Creek (500), Powells
Creek (433), Bull Run (425), Lake Occoquan (398), Quantico Creek (387).
`StreamType` is again an **uncoded integer** (2, 3, 4, 5, 6) with no lookup —
almost certainly Strahler order or perennial/intermittent class, but the corpus
does not say, so it **must not be used to classify perennial vs intermittent**
without the county's data dictionary. **ACTION: request the dictionary; do not
guess.** 24,821 segments still carry a 2002-02-01 edit date.

### 40.3 `Stormwater_Segments.geojson` — 111,412,241 chars

**83,673 conveyance segments**, 40 properties — by far the richest schema in the
corpus. `AsBuiltLength` sums to 5,879,940 ft (**1,114 miles** of built stormwater
conveyance); `EasementLength` 7,227,960 ft (1,369 mi). Pipe materials: RCP 27,484,
SRCP 18,419, CRCP 14,707, RR 5,648, CHDP 3,798, and 52 more. Full invert-elevation
and structure-depth fields are populated for ~83,650 segments — this is a real
hydraulic network, not a cartoon.

**Three data-quality findings, all consequential:**

1. **`SegmentCondition` is meaningless.** `BEST` on **83,650** segments, `BAD` on
   **3**. 99.996% identical is a default value, not an assessment. Any "stormwater
   condition" claim built on this field is vacuous. **Do not use it.**
2. **Only 1,474 of 83,655 segments (1.8%) are field-surveyed** (`FieldSurvey = Y`).
   The other 98.2% are from plans and mylar — one COMMENTS value is literally
   "DATA TAKEN FROM MYLAR INVENTORY SHEETS" (1,949 segments).
3. **`PIPESIZE` is 0 on 14,827 segments (18%)** — missing, not zero-diameter.

`InventoryDate` reaches back to **1993-04-01**; `Maintenance` responsibility splits
P 39,013 / C 23,950 / S 20,476 (uncoded again). `GASB` (capital-asset reporting
flag) is Y on 82,124.

### 40.4 The pattern across all three
Every large county hydrology layer shares the same shape: **geometry is excellent,
attribution is coded without a dictionary, and the fields that would carry
condition or classification are either unpopulated or defaulted.** The county knows
precisely *where* its water infrastructure is and records almost nothing about
*what state it is in* or *how much water moves through it* — the same finding as
Part 37.4 (chemistry monitored, quantity not) and Part 27 (gages retired), now in a
third form.

---

## Part 41 — transmission layers, and a groundwater file that is not about this county.

### 41.1 The two county power layers are nearly unattributed
`Power_Lines_(150kv_and_higher).geojson` — **60 LineStrings, 8 properties, and not
one of them records voltage, owner, or name.** `CreateUser`, `CreateDate`,
`LastEditUser` are entirely empty; 51 of 60 were last edited **2009-03-13**.
It is a picture of wires, nothing more.

`High_Voltage_Transmission_Lines.geojson` — 291 LineString + 7 MultiLineString.
Better in principle, empty in practice: **`Owner` blank on 262/298 (88%),
`LineCapacity` blank on 280/298 (94%), `Name` blank on 279/298 (94%)**. Where
`Owner` is populated: **Dominion Energy 29, NOVEC 7** — directionally consistent
with a roughly 80/20 split, but on a 12% sample this is a hint, not a number.
Capacities present: 230kV x9, 115kV x5, 500kV x4.

### 41.2 `Virginia_Power_Transmission_Lines_HIFLD.geojson` — and what it says about NOVEC

1,730 LineString + 119 MultiLineString, 17 properties, EPSG:4326, statewide.
Properly attributed: TYPE (AC;OVERHEAD 1,419), STATUS (IN SERVICE 1,671),
NAICS 221121 on all, SOURCE strings citing IMAGERY / OpenStreetMap / pjm.com /
EIA 860 / EIA 861, VAL_METHOD (IMAGERY 1,780, UNVERIFIED 51).
**`VOLTAGE` carries the sentinel `-999999` on 410 of 1,849 records (22%)** —
filter before any voltage analysis. Real values: 115kV 511, 230kV 441, 138kV 288,
69kV 114, 500kV 62, 161kV 8, 765kV 6.

`OWNER` across all 1,849 Virginia transmission lines: Virginia Electric & Power
1,018, Appalachian Power 483, NOT AVAILABLE 285, City of Manassas 10, Potomac
Edison 8, A&N Coop 8, Kentucky Utilities 8, Kingsport 7, Duke Progress 6, TVA 4,
Southside Coop 4, Delmarva 3, Glen Lyn 2, Monongahela 1, Dominion Energy 1.

> **NOVEC does not appear once.** It owns no bulk transmission in Virginia.

That reframes the open question from Parts 33.1 and 38.2. NOVEC is a **distribution
cooperative** — it owns no transmission (HIFLD), reports no net metering
(EIA-861M), and appears in no generation dataset in this corpus. It therefore does
not *generate* the power it delivers; it purchases wholesale. **The Scope 2
generation mix for NOVEC-served load is its wholesale supplier's portfolio, not
Dominion's.** Virginia's distribution co-ops are generally supplied by ODEC
(Old Dominion Electric Cooperative) — **but no file in this corpus states that, so
it must be verified before it is written down.** **ACTION: confirm NOVEC's wholesale
supplier from a primary source; if ODEC, its generation mix differs materially from
Dominion's and the Scope 2 factor for NOVEC-served buildings is wrong today.**

### 41.3 `Springs_Groundwater_Layers.geojson` is Shenandoah Valley data

2,916 Points, **226 properties** — a full groundwater geochemistry suite (major
ions, 30+ trace metals, nutrients, dissolved gases, radionuclides incl. Ra-226/228,
tritium, K-40), some digitised from **Collins et al. 1930**. Sentinels everywhere:
`SITENUM` = -9999 on 623, `COLLTIME` = -9999 on 357.

**It is not Prince William County data.**

| field | what it says |
|---|---|
| `CNTYSDB` | **Clarke 651, Page 559, Rockingham 286, Rappahannock 203, Warren 193, Augusta 153, Frederick 133** |
| `GPROV` | **Valley and Ridge 1,648, Blue Ridge 1,091**, Coastal Plain 110, **Piedmont 48** |
| `BASIN` | Upper Potomac/**Shenandoah** 2,038 (70%) |
| `HUC` | Hawksbill Creek 533, Shenandoah River/Spout Run 396, Lower Shenandoah 130 |
| `ALTITUDE` | mean **1,578 ft**, max 3,960 — Prince William tops out near 640 ft |
| geometry | **1 of 2,916 points falls inside the PWC bounding box** |

**`preprocess_score_parcels.py:299-306` already documents the geography** ("a
STATEWIDE VA DEQ ambient monitoring dataset ... only ~2 fall inside PWC") and
METHODOLOGY:1537 marks the layer as quality-not-quantity. Credit where due — this
was caught.

**What was not caught is the part that matters.** The code attaches the nearest
point's `PH`, `SPCOND`, `NO3NO2`, `HARD` and `COLLDATE` to each parcel as "the last
documented reading." But the nearest point is typically tens of miles away in
**Valley and Ridge karst** — carbonate aquifers (LITH: C-O-CARBONATES 467,
O-BEEKMANTOWN 341, C-DOLOMITES 340) — whereas Prince William is **Piedmont
crystalline** (PC-IGMET). Hardness, specific conductance and pH in a dolomite
aquifer say nothing whatever about a Piedmont saprolite parcel. Attaching that
chemistry is not conservative; it is **misleading in a specific, directional way**
(karst water is far harder and more conductive).

`d_spring_ft` is geometrically valid but semantically empty — it measures distance
to the Shenandoah Valley.

**ACTION: drop the spring-chemistry attachment entirely, or restrict it to the 48
Piedmont / 110 Coastal Plain points. Do not ship karst chemistry as a Prince
William parcel attribute.** Note this lives in `preprocess_score_parcels.py`, the
parcel-centric path that the facility-first rewrite superseded — check whether it
still feeds anything shipped before spending effort on it.

**RESOLVED 2 Aug 2026 — dropped. Two things above were wrong, and the correction
makes the case for removal stronger, not weaker.**

1. **`preprocess_score_parcels.py` is not superseded.** It is live: it writes
   `public/data/parcels_scored.json`, which `build_facility_profiles.py` reads at
   load to build every facility's water context. The parcel file itself is not
   served (both ignore-files exclude it, 1.08 GB), but its fields reach production
   through `facility_profiles.json`. `d_spring_ft` was in `WATER_CONTEXT_FIELDS`
   and shipped. The chemistry columns were not in that list, so they stopped at
   the local intermediate.

2. **"The nearest point is typically tens of miles away in Valley and Ridge
   karst" is not what the join did.** Run against all 159,181 parcels, it never
   reached the karst — it collapsed onto one well. 158,790 parcels (99.8%)
   resolved to the single PWC point (GPROV PIEDMONT, LITH MPT), sampled
   **24 Jun 1980**; 391 resolved to one Caroline County Coastal Plain point.
   `PH` and `SPCOND` resolved for **zero** parcels; `NO3NO2` for 391, all at the
   −0.01 below-detection sentinel (the code scrubbed −9999, not −0.01). `HARD`
   attached **260 mg/L, that one 1980 number, to all 158,790** — confirmed
   against the shipped `parcels_scored.json`, where `spring_hardness` is 260.0
   and `spring_sample_date` is 24 Jun 1980 on every record sampled.

   So the defect was not karst chemistry leaking in; it was one 46-year-old
   hardness reading broadcast countywide as a per-parcel attribute, next to two
   permanently empty columns. The province mismatch is still the reason the
   layer cannot be repaired — it is why no usable local point exists.

**The proposed restriction was tested and is a verified no-op.** Filtering the
source to GPROV in ("PIEDMONT", "COASTAL PLAIN") leaves all 159,181 parcels with
byte-identical distance and hardness, because both points the join lands on
already pass the filter. Of the 158 Piedmont/Coastal Plain points statewide only
70 carry any of PH/SPCOND/HARD, at a median 93 mi from PWC; the nearest with a pH
or specific-conductance value at all is a Westmoreland Coastal Plain well 30.6 mi
away in a different aquifer system. There is no local subset to restrict *to*.

`d_spring_ft` was dropped as well — not because it measures distance to the
Shenandoah Valley (it does not; median 13.1 mi, max 23.2 mi, all of it distance
to that one 1980 well) but because a radius around a single arbitrary point was
being carried in the facility dossier as groundwater-monitoring proximity.

Removed from `preprocess_score_parcels.py` (layer no longer read; chemistry join,
`d_spring_ft`, output columns, and both entries in `DEPTH_FIELDS` gone),
`build_facility_profiles.py` (`WATER_CONTEXT_FIELDS`), and
`src/lib/useFacilityProfiles.ts`. METHODOLOGY:1537 rewritten. No source in this
corpus supplies Piedmont groundwater chemistry for PWC at parcel resolution, so
the model now reports none.

---

## Part 42 — the land-constraint layers.

### 42.1 `LRLU_Developable_Areas.geojson` (4,840,650 chars) — the county's own buildout model

753 polygons (716 + 37 MultiPolygon), **110 properties** — Long Range Land Use
developable-capacity estimates with Low/Avg/High GFA bands and Min/Mid/Max dwelling
units for both residential and non-residential. 22 LRLU categories.
`SpecialPlanningAreaType`: Countywide 267, Small Area Plan 188, Activity Center 187,
Redevelopment Corridor 64, Hamlet 28, Village 19.

Non-residential development capacity by category (Avg GFA):

| LRLU | polys | dev. acres | Avg NonRes GFA |
|---|---:|---:|---:|
| MU-6 | 13 | 120 | 13,855,451 |
| MU-4 | 108 | 283 | 12,018,380 |
| **I-4** | 19 | 242 | **10,291,997** |
| **I-3** | 47 | 539 | **9,393,261** |
| MU-5 | 27 | 115 | 9,200,080 |
| **I-2** | 27 | 1,283 | **6,984,291** |

> **Industrial (I-*) total: 93 polygons, 2,064 developable acres,
> 26,669,549 sq ft Avg / 40,803,626 sq ft High non-residential GFA.**

Set beside Part 36.1's **69.1M sq ft of already-entitled but unbuilt** campus floor
area, the outer envelope for data-center growth in this county is roughly
**69M entitled + 27-41M further industrial capacity**. Both numbers are the
county's own; neither is modelled here. **This is the ceiling the growth scenarios
(G1) should be bounded by.**

Good-practice note worth recording: **the 20 industrial polygons flagged
`EnvironmentalResource = Yes` carry exactly 0 developable acres.** The county
already zeroes capacity where environmental resources are mapped — the constraint
is applied upstream, in the plan, not left to site review.

### 42.2 `Protected_Open_Space.geojson` (25,607,610 chars) — and who actually holds it

1,512 Polygon + 260 MultiPolygon, 37 properties, 526,503 vertices.
**52,326 acres = 22.7% of the county.**

| field | breakdown |
|---|---|
| `OpenSpaceCategory` | **Proffered or Platted Open Space 1,358 (77%)**, Local Government 232, Conservation Orgs 79, State 26, Federal 17 |
| `ManagingAgenyLevel` | **Private 1,432 (81%)**, Local 254, State 43, Federal 17, VOF 16 |
| `PublicAccess` | **Private 1,239**, Undeveloped 211, Open to the Public 148, Closed 62 |
| `ProtectedStatusType` | **Null 1,126**, Fee Simple 272, Zoning 164, Stormwater Mgmt Easement 101, Conservation Easement 69 |

> **`H2OQuality = Yes` on 645 features covering 34,060 acres — 14.8% of the county
> is protected open space designated for water quality.**

The governance finding: **77% of Prince William's protected open space exists as a
byproduct of the proffer system**, is **privately managed (81%)**, and is
**not publicly accessible (74% Private or Closed)**. It is not parkland the county
bought; it is land developers were required to set aside. `ProtectedStatusType` is
null on 64% of it, so the legal durability of most of that protection is not
recorded in this layer at all. Anyone treating the 22.7% as secure conservation
land would be overstating it — which matters for the exposure overlay (H1).

`EasementHolder` is blank on 1,457 of 1,772; named holders are VA Dept of Historic
Resources 33, Northern Virginia Conservation Trust 22, Virginia Outdoors Foundation
11, PWC Board of County Supervisors 4, NPS 3, American Battlefield Trust 3.

### 42.3 `Dam_Break_Inundation.geojson` — 28 zones, 11% of the county
28 features. `SHAPESTArea` sums to 1.11009e9 sq ft = **25,484 acres = 11.0% of the
county**; the largest single zone is 3.31632e8 sq ft (**7,613 acres**). Thin
attribution, last edited 2025-11-04. Relevant to siting risk, not to water
accounting.

### 42.4 `Zoning_Appeals_and_Variances.geojson` (1,863,491 chars) — thin
1,069 Polygon + 6 MultiPolygon, 12 properties, of which **`BZACaseName` is entirely
empty (0/1,075)**. Only `BZACaseType` (2 values), `BZACaseNumber` (1,071 distinct)
and shape fields carry content. Total area 1.045e8 sq ft. Effectively a case-number
index with geometry; no substantive content for this project.

---

## Part 43 — the last four layers, and the backup diff. GeoJSON reading COMPLETE (27/27).

### 43.1 `Soil.geojson` (56,180,317 chars) — usable, and unused

20,587 Polygons, 1,010,034 vertices, 143 distinct soil map units. `ShapeSTArea`
sums to 1.00484e10 sq ft = **230,681 acres** — a **third independent confirmation**
of the county's extent (watersheds 230,709; zoning 230,595).

The hydrologically load-bearing field is **`HydrologicSoilGroup`**:
**B 8,081 (39%), D 4,553 (22%), C 3,771 (18%), A 2,060 (10%), C/D 1,426, B/D 248,
A/D 8, blank 440.** Group D is lowest-infiltration / highest-runoff; **D plus the
dual groups is 6,235 polygons, 30% of the county**. Also carries
`ErosionSusceptibility` (K factor, 0.10-0.49), `Permeability` (9 values),
`SlopePercentage` (0-38, mean 8.0), and `SoilConstructionCategory` (II 8,019,
III 7,161, I 3,575, MIL 1,510, WTR 322). All four audit columns are empty.

This is a complete, clean infiltration/runoff dataset that **nothing in the model
currently uses.** It is the natural denominator for any recharge or
imperviousness argument. Noted, not scoped.

### 43.2 `Stormwater_Management_Structures.geojson` (40,128,092 chars)

**80,673 Points** — the node layer matching Part 40.3's 83,673 segments, with
`TopElevation`, `BottomElevation`, `DEPTH` (mean 4.0 ft, max 379.8), and
`OUTFALL` (104 distinct). Sparse where it matters: **`DrainageArea` populated on
21,349/80,673 (26%), `LandUse` on 3,390 (4%), `MS4RegOutfall` on 967 (1.2%)**.
`FieldSurvey` again binary and again mostly N. **Only 967 MS4-regulated outfalls
are identified across the whole county network** — the regulatory subset is 1% of
the infrastructure.

### 43.3 `Tidal_flow_paths_(WQS).geojson` (76,640,898 chars) — 97% irrelevant here

**66,953 LineStrings** carrying Virginia's **Water Quality Standards** designations:
`CLASS` (II on 66,952 — estuarine), `SPSTDS` special standards (a 41,878;
"a, aa" 8,935; PWS 411), `PWS` public-water-supply (441 total), **`TIER_III`
exceptional state waters — only 21 segments statewide**, `ZONE` (Estuarine 41,245,
Transition 17,707, Tidal Fresh 8,001).

`BASIN_CODE`: Small Coastal 27,418, James-Lower 16,197, York 12,439,
Rappahannock 5,456, Chowan-Albermarle 2,820, **Potomac-Lower 1,974 (3%)**,
Chowan-Dismal 473, Appomattox 176.

**This is a statewide tidal-waters file, and Prince William is almost entirely
non-tidal.** Only the Potomac frontage (Occoquan Bay, and the mouths of Neabsco,
Powells and Quantico creeks) is in scope — at most 3% of the file. **Broad Run,
Bull Run and Cedar Run — the basins carrying every data center — are non-tidal
freshwater and appear nowhere in it.** Second file after
`Springs_Groundwater_Layers` (Part 41.3) that is statewide and largely off-study-
area. Neither is wrong to hold; both must be clipped before use.

### 43.4 `Parcel.geojson` (481,766,719 chars) — the largest file, read in full

**159,181 parcels** (158,720 Polygon + 461 MultiPolygon), **7,488,010 vertices**,
31 properties. Two defects that matter for joins:

1. **`GPIN` has 156,470 distinct values across 159,181 features — 2,711 duplicate
   GPINs.** GPIN is the key the buildings layer joins on (Part 35.5). Any
   parcel join must be de-duplicated or it silently fans out.
2. **`Acreage` sums to 213,431 ac but `ShapeSTArea` sums to 227,588 ac — a
   14,157-acre (6.2%) disagreement** between the attribute and its own geometry,
   with 2,789 parcels carrying no `Acreage` at all. **Use the geometry, not the
   attribute.**

`ParcelType` 7 values; `RecordedDate` populated on 156,463; deed references on
about 58% (`DeedInstrument` 92,765, `DeedBook`/`DeedPage` ~63,800).

### 43.5 `Data_Center_Buildings.geojson.bak-2026-07-19` — the fleet grew 20% in ~10 months

| | backup 2026-07-19 | current | change |
|---|---:|---:|---:|
| features | **203** | **243** | **+40 (+20%)** |
| Completed | 55 | 54 | -1 |
| Under Construction | 31 | 31 | 0 |
| **Planned** | 104 | **120** | **+16** |
| **Pending** | 13 | **36** | **+23** |
| Under Review | 0 | 2 | +2 |

Schema identical — no property keys added or removed. 58 building names added,
18 removed; most removals are renames rather than deletions (Devlin Technology
Park 1-8 became Devlin Technology Park A-H). Genuine disappearances include
**Google Bristow 1-5** and Amazon Colchester Industrial Park 3.

**All of the growth is in the pre-construction pipeline** — Pending nearly tripled
and Planned rose 15%, while Completed and Under Construction did not move. This is
a direct, dated measurement of how fast the forward pipeline is filling, and it
supports the buildout framing independently of the entitlement figures in
Parts 36.1 and 42.1. **It also means any figure in the paper must state its
vintage: the fleet grew 20% between two snapshots ten months apart.**

Three buildings are named simply "A", "B", "C" — placeholder names in the current
layer.

---

# GeoJSON reading complete: 27 of 27 files, ~1.7 GB.

---

## Part 44 — corpus reading CLOSED. What was read, and the one source that cannot be.

### 44.1 Local corpus: complete
Every file in the repository has now been read. Verified inventory:

| class | count | status |
|---|---:|---|
| PDFs | 8 | read (JLARC `Rpt598`, ICPRB March 2026, ICPRB WMA Dec 2025, Dominion GS-5, Dominion SCC PUR-2026-00011, LBNL QueuedUp 2025, PJM SOM 2023 sec 3, EconBulletin 2022) |
| NWIS gage records (`.rdb`) | 8 | read (Part 27) |
| NOAA/NCEI series | 15 | read (Part 28) |
| CSVs | 20 | read (Parts 29-31) |
| XLSX workbooks (60 sheets) | 6 | read (Parts 32-34) |
| GeoJSON layers | 27 | read (Parts 35-43), ~1.7 GB |

No unread file remains in `data/`, `public/data/` or `docs/`.

### 44.2 The 145 planning staff reports are NOT retrievable

Part 38.1 identified 145 live `StaffReportLink` URLs in
`Planning_Pending_Cases.geojson`, each pointing at
`https://eservice.pwcgov.org/planning/documents/<CASE>.pdf`. These are the single
largest body of unread primary source relevant to this project — including
SUP2023-00005/00006 (Gainesville West/East Data Center), REZ2022-00015 and
SUP2022-00016 (Potomac Technology Park), and the four NOVEC substation filings.

**They cannot be fetched.** A test request for `SUP2023-00005.pdf` returned
**HTTP 403, 4,828 bytes of `text/html`** — a Cloudflare interstitial reading
"Sorry, you have been blocked / You are unable to access pwcgov.org", with a Ray ID
and a bot-detection notice.

**No attempt was made to circumvent this.** Retrying through a browser session
specifically to defeat an explicit bot block is evasion, not access, and the choice
of who may bulk-download the county's planning documents belongs to the county.

**Consequence for the paper:** the staff reports are cited-but-unread. Any claim
that would depend on their contents — proffer conditions, water-supply commitments,
cooling-technology statements in individual cases — **must not be made** on the
basis of this corpus. The `StaffReportLink` field should be described as an
available-but-unexercised evidence source, and the reason stated.

**Routes that remain open, in order of cost:**
1. The user downloads the PDFs manually (browser session, no automation) and drops
   them into `data/water_raw/staff_reports/`; reading then proceeds normally.
2. Request bulk access or an FOIA-style data request from PWC Planning.
3. Drop the line of inquiry and rely on `Use_Permits.geojson` +
   `Planning_Pending_Cases.geojson` attributes, which are already read and which
   carry case number, type, name, acreage, district and date — enough to
   characterise the pipeline, not enough to characterise conditions.

### 44.3 Standing deferred items, now unblocked
Reading is finished, so the items held back during it are ready to act on:
1. Cite ICPRB's **March 2026** Scope 1/2/3 framing; do not present it as novel.
2. Reconcile ICPRB's **8,500 gal/MW/day** peak against this model's **3,060**.
3. Rewrite METHODOLOGY 63.2 on **observed** drought return periods (Part 28.5),
   demoting AECOM's percentages (Part 28.1).
4. Fix the **Part 32.1 MFO-vs-incremental** error per Part 34.1.
5. Re-label the drought sweep as **observed condition**, not sensitivity (28.7).
6. Verify **NOVEC's wholesale supplier** from a primary source (41.2).
7. Compute Lake Anna under the **eGRID SERC Virginia-Carolina** convention.
8. State the **391 gal/MWh = North Anna 738 + Surry 0** fleet-average caveat (31.4).
9. Promote **Broad Run** to a named case (36.3, 37.2).
10. Use **RemainingGFA 69.1M sq ft** + LRLU industrial capacity as the G1 anchor.
11. Remove `EconBulletin_LaunchCost_2022.pdf` from the RAG index.
12. Declare **gage vintage** and add the observed-minimum-July comparator (27.1/27.2).

---

## Part 45 — THE STAFF REPORTS. SUP2023-00006, Amazon Gainesville East. The mechanism, found.

First real staff reports obtained (user downloaded them manually; Cloudflare block
per Part 44.2 stands). **SUP2023-00006, Gainesville East Data Center — Applicant
and Owner: Amazon Data Services, Inc.** GPIN 7497-41-7199, 5945 Wellington Rd,
±58.5382 acres, Brentsville. Planning Commission recommended **approval
2024-12-11**; conditions dated 2024-11-10. Planner: Reza Ramyar. Site is the
**brownfield of the former Atlantic Research Corporation**.

### 45.1 The county's entire water ask for a 1.3-million-sq-ft data center is $4,390

From the staff report's own **Level of Service (LOS)** table, page 4 — the complete
set of monetary contributions mitigating this development:

| item | rate | quantity | **total** |
|---|---|---:|---:|
| **Water Quality** | **$75.00 per acre** | 58.54 acres | **$4,390.50** |
| Fire and Rescue | $0.61 / sq ft building | 1,297,200 sf | $791,292.00 |
| | | **Total** | **$795,682.50** |

> **Fire and rescue is charged at 180x the water-quality contribution. Water is
> 0.55% of the total exaction.**

Condition 10.A specifies the $75/acre is "for water quality monitoring, drainage
improvements and/or stream restoration" — a one-time payment, **not tied to water
use in any way**. Condition 10.B requires connection to public water and sewer at
the applicant's cost "to meet the demand generated by its uses," and that "any
water well found on the property shall be properly abandoned."

**That is the whole of "Public Sewer and Water" in a 12-page condition set.**

### 45.2 What the conditions DO regulate, versus what they do not

Regulated, in detail and enforceably:
- **Noise** — 60 dBA day / 55 dBA night at residential boundaries, **explicitly
  naming "heating and cooling system(s)"** as a source; a **Sound Study** by a
  licensed acoustical consultant is required **before each building permit** *and
  again one month after each occupancy permit*, with mandatory mitigation.
- Building height (100', +20' rooftop mechanical = 120' max), FAR 0.55, setbacks,
  facade articulation, fenestration percentages, materials, screening, 12' fence
  around the substation, lighting, landscaping, native species, tree save, topsoil
  depth and composition, bike racks, graffiti removal.

**Not regulated at all — no condition exists on any of these:**
- water consumption or withdrawal, in any units
- **cooling technology** (evaporative vs air-cooled vs closed-loop) — the single
  largest source of Scope 1 uncertainty in this model
- water-use metering, reporting or disclosure
- reclaimed or recycled water
- drought-period curtailment
- electricity consumption or Scope 2 anything

**The asymmetry is the finding.** The county requires a licensed acoustical study
of the cooling system *twice per building* — before permit and after occupancy —
and requires nothing whatsoever about how much water that same cooling system
consumes. Sound is measured because it crosses the property line audibly; water
is not, because it arrives through a pipe the county already sold.

### 45.3 Why no water review happens: the use is BY RIGHT

Stated twice in the staff report:

> "Data centers **shall be permitted by right** in the Data Center Opportunity Zone
> Overlay District in the O(L), O(H), O(M), O(F), M-1, M-2, and M/T zoning
> districts and in designated office or industrial land bays in the PBD and PMD
> district."

**The SUP was required only for building height (75'->100') and FAR (0.5->0.55).**
Not for the data center use, which needs no permit at all in the DCOOD. So the only
lever that produced *any* conditions here was a request for extra height and
density. **A data center built to 75 feet at 0.5 FAR inside the DCOOD generates no
SUP, no conditions, no staff report, and no water discussion of any kind.**

This is the mechanism behind every regulatory-gap finding in this log — Part 29
(NPDES is the wrong instrument), Part 33.3 (backup generation invisible to EIA),
Part 35.3 (county records zero floor area for 34 operating buildings). **It is not
that water review is done badly. It is that the entitlement pathway never triggers
one.** This belongs in the abstract.

Corroborating: the Comprehensive Plan Consistency table marks **"Potable Water:
Yes"** and **"Environment: Yes"** as satisfied — checkboxes, with no supporting
water analysis anywhere in the report.

### 45.4 Hard numbers now available

- **Entitled building area: 1,297,200 sq ft** on 58.5382 acres (the LOS table's own
  figure — use this, not FAR x area).
- Standards changed: height 75'->100'; **FAR 0.5 -> 0.55**; minimum open space
  15% -> 20%; **maximum lot coverage 80% -> 60%**; setback 20' -> >20'.
- I-4 / T-4 intended density is **0.57-1.38 FAR** — so 0.55 is *below* the
  Comprehensive Plan's own target range for the designation.
- On-site **electric substation is part of the permitted use** ("uses secondary and
  ancillary to a data center, such as offices and electric power substation"),
  height capped at 75', 150' setback from Wellington Road.
- Site sits **within the RPA Overlay District**.

### 45.5 A discrepancy in the county's own documents
SUP conditions page 2 of 12, section 1.D: "**maximum site coverage shall not exceed
65%**". Staff report background table, page 2: maximum lot coverage "**60% (as
conditioned)**". These cannot both be right. Minor, but it is the operative
development standard and the two documents in the same PDF disagree. **Flag; do not
cite either figure without checking the adopted BOCS version.**

### 45.6 CORRECTION to Part 38.1
Part 38.1 presented all nine data-center/substation cases as **live pending cases**.
The ePortal records show otherwise:
- **SUP2023-00005** (Gainesville West, Amazon Data Services) — **WITHDRAWN**. Its
  staff-report URL returns a one-page placeholder: "The staff report for this case
  is currently unavailable."
- **REZ2022-00015** (Potomac Technology Park) — **WITHDRAWN**, completion 2026-04-29.

So the "145 pending cases" layer contains withdrawn cases. **`Planning_Pending_Cases`
is not a live-case list and must not be described as one.** Status must be checked
per case in ePortal. **ACTION: revise Part 38.1 and any pipeline count derived
from it.**

### 45.7 New case not in the GeoJSON: Stinger Substation
ePortal shows **PFR, Stinger Substation, APPROVED 2025-09-10** (applied 2025-03-06,
IVR 892829), GPIN 7497-32-5305, 13255 Skylark View Way, Gainesville, M-1 / I-4,
in the DCOOD — described as **"A request for a Utility substation for a future data
center."** It does not appear in `Planning_Pending_Cases.geojson`.

Two consequences: (a) the substation pipeline is **larger** than the four NOVEC
cases in Part 38.2; (b) the county's own language — "substation **for a future data
center**" — is direct documentary evidence that substation applications are a
leading indicator of data-center load, which is the missing link for the forward
pipeline (plan item G3) and for the NOVEC question (41.2).

---

## Part 46 — SUP2023-00005 ePortal record. A validation, and three empty fields.

Full ePortal detail for **SUP2023-00005, Gainesville West Data Center, AMAZON DATA
SERVICES** (IVR 791366, applied 2022-09-23, **Withdrawn**), GPIN 7497-32-5206,
5845 Wellington Rd, Brentsville. Type: "Special Use - **Modification to Development
Standards**". Overlays: RPA, Airport Safety, DCOOD, and the **Wellington Study
Area** — a named study area not previously encountered in this corpus.

### 46.1 The two Amazon parcels, side by side

| | Gainesville **West** (00005) | Gainesville **East** (00006) |
|---|---:|---:|
| GPIN | 7497-32-5206 | 7497-41-7199 |
| acres | 58.53 | 58.5382 |
| **entitled floor area** | **708,446 sf** | **1,297,200 sf** |
| implied **FAR** | **0.278** | **0.509** |
| SUP asked for | height only (75'->100') | height **and** FAR (0.5->0.55) |
| outcome | **WITHDRAWN** | **recommended approval** |

Two adjacent parcels of near-identical size, same applicant. **East carries 1.83x
the floor area of West.** West at FAR 0.278 sat well under the by-right 0.5, so it
needed only the height modification — the structured field reads
**"Excess Building Height: 25"**. East at 0.509 crossed 0.5, which is the only
reason an FAR condition set exists at all. This is Part 45.3's mechanism visible in
a single pair of cases: **the conditions a data center receives depend on how far
past the by-right envelope it reaches, not on what it consumes.**

### 46.2 Validation of the model's building-level GFA

`Data_Center_Buildings.geojson` on **GPIN 7497-41-7199** (Gainesville East):

| building | status | GFA | source |
|---|---|---:|---|
| Amazon AWS IAD A | Under Construction | 258,716 | Building Permit |
| Amazon AWS IAD B | Under Construction | 248,483 | Building Permit |
| Amazon AWS IAD C | Under Construction | 218,391 | Building Permit |
| Amazon AWS IAD D | Planned | 218,391 | Building Permit |
| **total** | | **943,981** | |

Against the SUP's entitled **1,297,200 sf**, the buildings layer captures
**72.8%**; the residual **353,219 sf** is entitled-but-not-yet-permitted floor area
on that parcel alone. Independent confirmation of the buildout gap measured
county-wide in Part 36.1 (81.2% of entitlement unbuilt), now at parcel resolution and
from a different document class.

Consistency check passed: the SUP conditions state "**Buildings C and D** may be
100 feet" — and the layer holds exactly IAD C and IAD D at that parcel.

**GPIN 7497-32-5206 (West) returns zero buildings** — correct, the case was
withdrawn and nothing was built. The model is not carrying withdrawn entitlement.

### 46.3 Three structured fields the county leaves blank

The ePortal intake captures, as named fields: Total Area, **Disturbed Area**,
**Impervious Area**, **Open Space Area**, Recreational Area. For a 58.53-acre data
center application:

> **Total Area: 58.53. Disturbed Area: blank. Impervious Area: blank. Open Space
> Area: blank. Recreational Area: blank.**

Only `Industrial Sq Ft` (708,446) is populated. **The county's own application
record has a field for impervious area and does not fill it in** — for a use whose
entire site is roof, pad and parking. Given Part 43.1 (30% of county soils are
high-runoff hydrologic groups C/D) and Part 40.3 (stormwater condition data is
defaulted), this is the third independent instance of the same shape: **the field
exists, the data does not.**

Also inconsistent within the same record: the header reads **"Square Feet: 0.00"**
while the detail section reads **708,446**. Do not read the header field.

### 46.4 Wellington-area campuses in the projects layer, for context
`Data_Center_Projects.geojson` nearby entries: Wellington Glen Technology Park
(REZ2024-00018, Planned, 673,198 sf / 53.0 ac), Amazon Wellington South
(REZ1989-0069, Completed, 297,160 sf / 23.5 ac, RemainingGFA 0), NTT Grove at
Gainesville (REZ2021-00001, 2,248,452 sf / 90.9 ac, **all remaining**), CorScale
Gainesville Crossing (REZ2018-00008, 1,981,643 sf, 1,499,420 remaining), Microsoft
Azure Gainesville Tech Park (REZ2020-00011, 1,245,499 sf, **all remaining**).

Note **REZ1989-0069** — Amazon Wellington South is entitled under a **1989**
rezoning. Entitlements in this county are long-lived, which is why the unbuilt
69.1M sq ft in Part 36.1 should not be discounted as speculative.

---

## Part 47 — Is reading all 145 staff reports worth it? No. And the reason is the finding.

Tested directly against `Data_Center_Buildings.geojson`, all 243 buildings:

> **Zero of 243 data-center buildings in Prince William County has a Special Use
> Permit as its planning case.**

`PlanningCaseNumber` is populated on 104 of 243 (43%). Every one is **REZ** (92) or
**PLN** (12) — rezonings and plans. **Not one SUP.** The remaining **139 buildings
(57%) carry no planning case at all.** 172 of 243 sit inside the DCOOD, where the
use is by right (Part 45.3).

**So the 145 staff reports document an exception path that no building in the
fleet actually took.** Both data-center SUPs obtained so far (Gainesville West and
East) were *withdrawn* or attach to a parcel whose buildings are permitted under
building permits, not the SUP. Reading the remaining ~136 would characterise cases
that are mostly not data centers at all (130 of 145 are tier-4: schools, churches,
residential) and would not touch the fleet.

**This converts the Part 44.2 limitation into the result.** The correct sentence is
not "staff reports were unavailable" but:

> **Prince William County's 243 data-center buildings were entitled without a
> single special use permit. The discretionary review that could have imposed
> water conditions was never invoked, because the use is permitted by right inside
> the Data Center Opportunity Overlay District.**

### 47.1 Entitlement vintage — and 1958

**Nineteen buildings trace to `REZ1958-0021`** — a rezoning adopted in **1958**.
Others trace to 1969, 1985, 1989. Amazon Wellington South is REZ1989-0069
(Part 46.4).

Data centers are being built today under land-use approvals granted before the
integrated circuit was commercialised. No water condition could have been
contemplated, and none can now be retrofitted: the entitlement runs with the land.
This is the strongest available answer to "why doesn't the county just condition
them?" — for a large share of the fleet, **there is no open approval to condition.**

### 47.2 What is still worth obtaining (~20 documents, not 145)
1. The **9 tier-1/tier-2** cases (data centers + substations) — for the substation/
   NOVEC link and any cooling-technology language.
2. **5-10 arbitrary others**, solely to confirm the **$75/acre water-quality LOS
   rate is a standard countywide schedule**, not case-negotiated. If standard, it
   should be citable from the ordinance or LOS policy directly — **check that
   first; it may make the sample unnecessary.**
3. **`REZ1958-0021` and `REZ1989-0069`** proffers, if any survive, to confirm that
   old entitlements carry no water conditions.

Everything else is confirmatory. **ACTION: do not pursue the full 145.**

---

## Part 48 — PFR2025-00012, Stinger Substation. The NOVEC/Dominion question is ANSWERED.

The county's mislinked URL (Part 44/46: the `PFR2025-00013` Freedom I-66 record
points at `PFR2025-00012.pdf`) turns out to serve **Stinger Substation** — the very
case that is missing from `Planning_Pending_Cases.geojson` (Part 45.7). The data
error handed over the file I could not locate.

Document: **S2 Review packet, PFR2025-00012, Stinger Substation, 2025-06-17**,
Brentsville, case planner Reza Ramyar, comments due 2025-07-01 to Aisha Medina.
Circulated to County Archaeologist, Crime Prevention Police, DoIT Radio Services,
Historical Commission, Transportation, **Watershed Management (DS930)**, Zoning
Administrator. Includes the sealed Kimley-Horn engineering exhibit (Ross Stevens,
PE, Lic. 047498), 1st submission 2025-06-02.

### 48.1 BOTH utilities build on the same Amazon parcel

Engineering Sheet 1 is unambiguous. On a single site — **Owner: AMAZON DATA
SERVICES INC**, GPIN **7497-32-5305**, total site **58.301 acres** (PFR area
8.436 ac) — the plan shows **two separate substations**:

> **Note 21: "MAXIMUM STRUCTURE HEIGHT WITHIN DOMINION SWITCHING STATION IS 110'.
> MAXIMUM STRUCTURE HEIGHT WITHIN NOVEC SUBSTATION IS 75'."**

Both are drawn, labelled and dimensioned: a **DOMINION SUBSTATION** (avg finished
grade ~316', max height 110') and a **NOVEC SUBSTATION** (avg grade ~316', max
height 75'), on a shared **6.25-acre gravel pad**, with a **proposed 100' Dominion
transmission easement** crossing the site.

**This settles the question left open in Parts 33.1, 38.2 and 41.2.** NOVEC and
Dominion are not serving separate territories that must be apportioned — they are
building **side by side on the same data-center campus**. Attributing 100% of
Prince William's data-center Scope 2 to Dominion's generation mix is therefore
wrong at the *facility* level, not merely at the county level, and the error is
documented in the county's own approved engineering exhibit.

**ACTION:** the Scope 2 module must carry an explicit stated limitation, and the
`facility_profiles` for GPIN 7497-32-5305 should record dual-utility service.
The apportionment still cannot be quantified — neither substation's capacity is
given — but the *fact* of dual service is now evidenced, not inferred.

### 48.2 The substation serves buildings already in the model

`Data_Center_Buildings.geojson` on **GPIN 7497-32-5305**:

| building | status | GFA | address |
|---|---|---:|---|
| Amazon AWS IAD A | Planned | 244,166 | 13235 Skylark View Way |
| Amazon AWS IAD B | Planned | 316,065 | 13225 Skylark View Way |

The PFR exhibit shows **Buildings A, B and C** on this parcel under site plan
**SPR2023-00176** — so a third building exists on the approved site plan that the
buildings layer does not carry. Combined with Part 46.2 (72.8% capture on the
neighbouring parcel), the buildings layer is again **under**-counting relative to
approved plans, in the same direction.

Note the naming collision: "Amazon AWS IAD A" and "IAD B" appear on **both**
GPIN 7497-32-5305 (Skylark View Way) and GPIN 7497-41-7199 (Deacon Falls Drive).
**`BuildingName` is not unique and must never be used as a join key** — this is
the concrete case that proves it.

### 48.3 Substations consume no water — usefully confirmed

> **Note 17: "THE UTILITY SUBSTATION WILL NOT REQUIRE PUBLIC WATER OR SEWER."**

Worth recording explicitly: the substation build-out that dominates the county's
active generation-interconnection pipeline (Parts 32.3, 38.1) adds **no Scope 1
demand of its own**. Substations are a *signal* of coming IT load, not a water use.
The forward-pipeline argument should use them as a leading indicator only.

Corroborating the negligible-footprint framing, Note 12: "UPON COMPLETION THE
SUBSTATION WILL TYPICALLY ONLY REQUIRE SEMI-MONTHLY INSPECTIONS. NEGLIGIBLE TRAFFIC
IMPACT IS EXPECTED. FOUR (4) VEHICLES PER MONTH..." and Note 13: one parking space.

### 48.4 Environmental context on the parcel
The exhibit maps **Resource Protection Area** (per ASP2024-00040) and **Flood
Hazard Area** (instrument 202403070011778) along the eastern edge, an **edge of
proposed stream under SPR2022-00050**, three separate stormwater-management access
easements, a 12" sanitary line, and a relocated 20' sanitary sewer easement.
Review correspondence shows staff negotiating a **6' minimum berm** (final: 60'
overall width to achieve 6' height), a 15' Type A buffer plus a **supplemental 15'
evergreen strip — a 30' vegetated strip between Wellington Road and the
substation** — and a 12' chain-link fence with 5/8" wire mesh.

**Every negotiated condition in this packet is visual or acoustic screening.**
Same pattern as Part 45.2: the county bargains hard over what the facility looks
like and not at all over what it consumes.
