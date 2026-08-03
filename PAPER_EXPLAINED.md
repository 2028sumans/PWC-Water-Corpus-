# The paper, explained from zero

**Who this is for:** you, in six months, when a reviewer asks "where does 43% come
from?" and you need to answer without opening the code. Everything here is
first-principles. No prior knowledge assumed. Every number traces to a file.

---

# PART I — THE QUESTION

## 1. What problem does this paper solve?

A data center is a warehouse full of computers. Computers turn electricity into
heat. If you don't remove the heat, they fail. Most large data centers remove it
by evaporating water — the same physics as sweating.

So a data center uses water two ways:

1. **Directly**, on site, evaporating it in a cooling tower.
2. **Indirectly**, at the power plant that generates its electricity — because
   thermal power plants (nuclear, coal, gas) also evaporate water to condense
   steam.

Almost every public assessment of data-center water counts only #1. This paper
counts both, at the level of individual buildings, for one county — and shows that
**#2 is roughly seven times larger than #1, and lands in a different river basin.**

Then it shows two further things that make that awkward:

- **Which** basin gets blamed depends on an accounting choice, not on measurement.
- **Nobody in the permitting process ever asks how much water a data center will use.**

## 2. Why Prince William County, Virginia?

Because it is the extreme case. Northern Virginia is **the largest data-center
market in the world** — 13% of global operational capacity (JLARC Rpt598, p.5).
Prince William is the fastest-growing part of it, and the county publishes a
building-by-building GIS layer, which almost nowhere else does.

## 3. The one-sentence thesis

> The water footprint of data centers is invisible twice over: because of **where
> it lands** (mostly at power plants, in a basin chosen by accounting convention),
> and because of **how it was permitted** (by right, with no water question ever
> asked).

---

# PART II — VOCABULARY

Learn these eleven terms and the whole paper opens up.

| Term | Means | Why it matters here |
|---|---|---|
| **MGD** | Million Gallons per Day | The unit everything is reported in |
| **MW** | Megawatt — a *rate* of energy use, not an amount | A 10 MW data center draws 10 MW continuously |
| **MWh** | Megawatt-hour — an *amount* of energy | 10 MW running for 1 hour = 10 MWh |
| **IT load** | Power drawn by the computers themselves | The thing that actually does work |
| **PUE** | Power Usage Effectiveness = total facility power ÷ IT power | 1.3 means 30% overhead for cooling, lights, losses |
| **GFA** | Gross Floor Area, in square feet | Our main observable — we can see buildings, not meters |
| **WUP** | Water Use per unit of Power (gal/day per MW) | The core intensity constant |
| **Withdrawal** | Water taken from a river | Most of it goes back |
| **Consumption** | Water that does *not* come back (evaporated) | **This is what the paper measures** |
| **Scope 1/2/3** | On-site / electricity / supply-chain | Borrowed from carbon accounting |
| **Basin** | The area draining to one river | Determines *whose* water it is |

**The withdrawal-vs-consumption distinction is the single most important one.**
A once-through-cooled power plant might withdraw 300 MGD and consume 2 MGD — it
returns 298 MGD, warmer. If you report withdrawal you overstate impact by 100×.
This paper reports **consumption** throughout, and says so.

---

# PART III — THE SCOPE FRAMEWORK

## 4. Where the idea comes from

Carbon accounting has used this for two decades (the GHG Protocol):

- **Scope 1** — emissions you make yourself
- **Scope 2** — emissions from electricity you buy
- **Scope 3** — everything else in your supply chain

Applying it to *water* is the framing this paper uses. **Important for honesty:
ICPRB published this framing first**, in a two-page fact sheet in March 2026:

> "While this study focuses on direct, on-site consumption, data centers also have
> an **'indirect' water footprint (often referred to as Scope 2 and 3)** through the
> water required to generate the electricity they consume and the water used in the
> lifecycle of their hardware."

**We must cite them for the framing.** Our contribution is that we *compute* Scopes
2 and 3 at building level and show the convention flip — not that we thought of it.

## 5. The three scopes here

| Scope | What it is | Where the water physically is |
|---|---|---|
| **1** | Evaporated in cooling towers | Prince William County |
| **2** | Evaporated at generating stations | Lake Anna, the James, out of state |
| **3** | Embodied in servers, construction | Wherever chips are made — not Virginia |

---

# PART IV — THE MODEL, EQUATION BY EQUATION

Everything flows from **one quantity: effective IT power in megawatts.** Get that,
and all three scopes follow by multiplication.

## 6. Step 1 — estimating power (the hard part)

We cannot measure any building's electricity. Nobody publishes it. So we infer it,
using the best evidence available per building. This is the **evidence ladder** —
four rungs, best first.

### Rung 1 (best): air-permit generator capacity

Data centers keep diesel backup generators, and generators are an **air pollution
source**, so Virginia DEQ permits them and publishes the permits. Permitted
generator capacity is a real, measured number.

But generators are oversized — you install roughly twice what you need (redundancy),
and you don't run at 100% (utilization). ICPRB's Equation 6-3 handles this:

```
Effective IT MW  =  Permitted generator MW  ×  0.5  ×  0.8
                                              ↑      ↑
                                       redundancy  utilization
```

**Where 0.5 and 0.8 come from** — ICPRB 2025 WMA Study §6.2.2, verbatim: permitted
capacity "typically represents twice the actual IT power load (i.e., 2N backup
systems)", and utilization 0.8 "based on industry data (EPRI, 2024)."

**Combined derating factor = 0.4.** In code: `PERMIT_FACTOR_CENTRAL = 0.5 * 0.8`.
Low and high bounds are `0.4 × 0.7 = 0.28` and `0.6 × 0.9 = 0.54`.

When several buildings share one permit, the site total is split by floor-area share.

### Rungs 2–4: floor area

For buildings with no permit, we use floor area and a density constant:

```
Effective IT MW  =  GFA (sq ft)  ÷  8,818
```

**Where 8,818 comes from** — ICPRB, quoting the JLARC database: *"an infrastructure
density of 8,818 square feet per MW based on the JLARC database."* Independently
corroborated: ICPRB's fact sheet gives 5,400 MW across 56 million sq ft basin-wide
= **10,370 sq ft/MW**, within 15% of ours.

Rung 2 is a model fitted to that specific *operator's* buildings; rung 3 a generic
fitted model; rung 4 the bare constant. Uncertainty widens down the ladder:
**±26% at rung 1, ±60% at rung 4.**

### The fit-out ramp — a correction that mattered

A building marked "Completed" is **not** running at full power. Prince William's own
building policy (eff. 2021-04-05) says a Certificate of Occupancy is granted with
unfitted floor area permitted as **Storage (S-1)**, with the data halls fitted out
later under separate permits.

So "Completed" marks the *start* of fill-up, not the end. Dominion's GS-5 contract
for these customers runs 14 years "inclusive of a **four-year ramp period**." We
model that linearly:

```
energized fraction = min(1, years since occupancy ÷ 4)
Effective IT MW    = Installed IT MW × energized fraction
```

**Why this mattered:** before the ramp, our fleet estimate was **1.23×** JLARC's
independent figure. After: **0.93×**. It removed a systematic ~2× overestimate.

## 7. Step 2 — Scope 1 (on-site cooling)

```
Scope 1 (MGD)  =  Effective IT MW  ×  WUP (gal/MW/day)  ÷  1,000,000
```

`WUP` = Water Use per unit of Power. Its value depends on cooling technology:

| tier | gal/MW/day | what it is |
|---|---:|---|
| air-cooled | **150** | dry/closed-loop floor |
| **PWC observed** | **309** | ← **our central value.** Prince William Water's *actual* reported 2023 fleet use ÷ JLARC power |
| basin average | 800 | ICPRB regional average |
| fully water-cooled | **1,577** | 100%-evaporative ceiling |

We use **150–1,577 as the range and 309 as the central estimate**, narrowing only
when a binding permit condition or a public operator commitment says otherwise.

**Worked example.** A 12 MW building:
`12 × 309 ÷ 1,000,000 = 0.0037 MGD` — about 3,700 gallons a day.

## 8. Step 3 — Scope 2 (electricity)

Three multiplications:

```
Site power (MW)   =  Effective IT MW  ×  PUE
Energy (MWh/day)  =  Site power       ×  24
Scope 2 (MGD)     =  Energy           ×  water intensity (gal/MWh)  ÷  1,000,000
```

Or in one line:

```
Scope 2 (MGD)  =  IT MW  ×  PUE  ×  24  ×  gal/MWh  ÷  1,000,000
```

### Term 1: PUE

Total facility power ÷ IT power. Ranges by building vintage:

| class | PUE range |
|---|---|
| new_build (under construction / planned) | 1.15 – 1.35 |
| modern (completed 2020+) | 1.15 – 1.40 |
| standard (2010–2019) | 1.30 – 1.55 |
| legacy (pre-2010) | 1.45 – 1.80 |

Where an operator publishes a fleet PUE (AWS 1.14, Microsoft 1.16) we use it —
that covers 57 buildings.

### Term 2: water intensity of electricity — the heart of the paper

Different generators evaporate different amounts of water per MWh:

| fuel | gal/MWh | source |
|---|---:|---|
| nuclear | **391** | USGS thermoelectric model, Virginia plants 2008–2020 |
| natural gas (combined cycle) | **196** | same |
| coal | **474** | same |
| wind / solar / hydro | **0** | no thermal cycle |

> ### ⚠ The 391 caveat you must always state
> **391 is a two-plant fleet average, not a plant intensity.**
> North Anna alone runs **735.6–741.2 gal/MWh**, rock-stable across 13 years.
> Surry consumes **0.00** — it is once-through-cooled on the tidal James, so its
> water is borrowed, not consumed. The fleet figure is 391 only because North Anna
> is ~53% of Virginia nuclear generation.
> **Anyone who looks up North Anna and compares it to 391 concludes we are 2× wrong
> unless we say this.**

Now weight those by what's on the grid. Dominion's mix is 58% gas / 25% nuclear /
14% renewable / 3% coal, giving:

```
0.58×196 + 0.25×391 + 0.14×0 + 0.03×474  =  225.6 gal/MWh
```

**Worked example.** Same 12 MW building, PUE 1.25:
`12 × 1.25 × 24 × 225.6 ÷ 1,000,000 = 0.081 MGD` — **22× its Scope 1.**

That ratio is the paper's opening result.

## 9. Step 4 — Scope 3 (supply chain)

We have no Virginia data on chip fabrication or construction water, so Scope 3 is a
**proportional anchor**, not a physical estimate:

```
Scope 3  =  (Scope 1 + Scope 2)  ×  5% to 15%
```

Sourced to corporate embodied-vs-operational disclosure ratios (Privette et al.
2026). **Say plainly that this is an anchor.** At least one hyperscaler has
disclosed embodied water exceeding 99% of its corporate total, so the true tail
could be far larger.

## 10. Step 5 — uncertainty (Monte Carlo)

Every constant above is a range, not a point. To get a real confidence interval we
run **40,000 simulations**. Each draw:

1. picks a value for each *systematic* parameter (grid intensity, WUP calibration,
   Scope 3 fraction) **once, shared across all buildings** — because if the grid
   mix is wrong, it's wrong for everyone simultaneously;
2. picks per-building values for building-specific parameters;
3. recomputes the county total.

Sorting the 40,000 totals gives the interval.

**Why shared draws matter:** if you drew every parameter independently per building,
errors would cancel by averaging and you'd report a falsely narrow interval. This is
called *common random numbers* and it is the difference between an honest CI and a
flattering one.

**Result:** county total **49.9 MGD, 90% credible interval 41.4 – 60.5**.

---

# PART V — THE RESULTS

## 11. Result 1: Scope 2 dominates — 88%

For the **54 completed buildings** (today's operating fleet):

| scope | MGD | share |
|---|---:|---:|
| Scope 1 — on site | 0.21 | 2.9% |
| **Scope 2 — electricity** | **6.23** | **88.0%** |
| Scope 3 — supply chain | 0.64 | 9.1% |
| **total** | **7.09** | |

**Why it's so lopsided:** cooling water is ~309 gal per MW-day. Electricity water is
225.6 gal per MWh × 24 h × 1.25 PUE ≈ **6,768 gal per MW-day**. Twenty-two times as
much, for the same building.

**The comparison that makes it land:** the regional water authority's own assessment
of this basin covers only Scope 1 — under 3% of what we estimate.

## 12. Result 2: the convention table — **the paper's central result**

**FIGURE 1.** Scope 2 water is consumed at power plants. *Which* power plants, and
therefore which basin, depends on how you assign electricity to consumers. There are
six standard ways. All are legitimate. They disagree by a factor of 50.

| # | convention | what it assumes | Lake Anna share |
|---|---|---|---:|
| 1 | **Dominion utility-average** | you consume your utility's average mix | **43.32%** |
| 2 | **PJM RTO-wide average** | you consume the whole market's average mix | **5.31%** |
| 3 | eGRID SERC VA/Carolina | EPA's regional subgrid — **the county's own basis** | *not computable* |
| 4 | Market-based | you consume what you contracted for (PPAs/RECs) | *≈0 for clean buyers* |
| 5 | **Short-run marginal** | a *new* load turns on the *next* plant in the stack | **0.87%** |
| 6 | Long-run marginal | new load causes new plants to be built | *entire +24 TWh nuclear build* |

### Understanding the two extremes

**Average accounting (43%)** says: 25% of Dominion's *electricity* is nuclear — but
nuclear is twice as water-intensive as gas (391 vs 196 gal/MWh), so that 25% of the
energy is **43% of the water**:

| fuel | share of energy | × gal/MWh | share of **water** |
|---|---:|---:|---:|
| gas | 58% | 196 | 50.4% |
| **nuclear** | **25%** | **391** | **43.3%** |
| renewable | 14% | 0 | 0.0% |
| coal | 3% | 474 | 6.3% |

And because Surry consumes 0.00 (§8), *all* of that nuclear water is at North Anna —
Lake Anna, in the **York basin, 80 km from the buildings**.

> **Do not say "25% nuclear, so 25% of the water."** That was an error in an earlier
> draft of this document. The energy share and the water share are different numbers,
> and the gap between them is the entire reason Lake Anna's figure is as large as it is.

**Marginal accounting (0.87%)** says: North Anna runs flat out regardless of whether
you plug in. Adding a data center doesn't make it produce more. What *does* respond
is a gas plant. So the water attributable to *your* load is gas-plant water, in the
**James basin** — and nuclear's share collapses.

Both are standard. Both are defensible. **They implicate different rivers, and
therefore different regulators.** That is the finding.

### Two things I got wrong and fixed — learn from these

**(a) The geography trap.** My first attempt applied PJM's RTO-wide nuclear share
(33.3%) to a **Virginia-only** plant map, and got **45.4%** — *higher* than Dominion,
which is backwards. The error: most PJM nuclear is in Pennsylvania, New Jersey,
Illinois and Maryland, not at North Anna. Fixed by scaling by Virginia's share of PJM
nuclear generation:

```
32 TWh (Virginia, JLARC App.H)  ÷  273,489 GWh (PJM 2023, SOM Table 3-63)  =  11.7%
45.41%  ×  0.117  =  5.31%
```

**(b) What we cannot compute, we declare.** For eGRID SERC VA/Carolina, no source
splits its nuclear between Virginia and the Carolinas (it includes Duke's NC fleet).
The direction is certain — Lake Anna's share falls — but the magnitude isn't
computable. We say so rather than estimate it.

## 13. Result 3: the entitlement pathway — nobody asks

**FIGURE 2.**

> **0 of 243 data-center buildings has a Special Use Permit.**

Every populated planning case is a **REZ** (rezoning, 92) or **PLN** (plan, 12).
139 buildings (57%) have no case at all.

**Why that's the finding.** The SUP is the county's *only discretionary review* —
the one moment where an official can attach conditions to a specific proposal.
Inside the **Data Center Opportunity Overlay District**, data centers are permitted
**by right**. A SUP is triggered only by exceeding the by-right envelope — height or
floor-area ratio — never by the use itself.

**A data center built to 75 feet at 0.5 FAR inside the overlay generates no SUP, no
conditions, no staff report, and no water discussion of any kind.**

172 of 243 buildings sit inside that overlay.

### The 1958 problem

**32 buildings are entitled under pre-1990 approvals. Twenty of them under rezonings
adopted in 1958.** Under `REZ1958-0021` alone: 9 Planned, 6 Pending, 3 Under
Construction, 1 Completed — **still being built today, under a 1958 approval.**

An entitlement runs with the land. Where the approval predates the industry, no water
condition could have been contemplated and none can be retrofitted. This answers the
obvious objection — *why not just attach water conditions?* — for a large share of the
fleet, **you can't. There is no open approval to condition.**

### The price of water, in the county's own schedules

From the one data-center SUP in the record (Amazon Gainesville East, 1,297,200 sq ft):

| item | rate | total |
|---|---|---:|
| **Water Quality** | $75.00 / acre | **$4,390.50** |
| Fire and Rescue | $0.61 / sq ft | $791,292.00 |

**Fire and rescue is 180× the water contribution.** Water is 0.55% of total exactions.
Meanwhile the same conditions require a **licensed acoustical study of the cooling
system twice per building** — and impose nothing on what that cooling system consumes.

Review fees run the same way: SUP application **$17,209.06**, traffic study
**$2,059.13**, **Prince William Water review $86.25.** Traffic review costs **24×**
what water review costs.

## 14. Result 4: timing — demand peaks when water is scarcest

**FIGURE 3.**

| system | peak-day ÷ annual-average |
|---|---:|
| WSSC / Aqueduct / Fairfax / Loudoun | **1.5 – 1.9** |
| **data centers (ICPRB)** | **~10** |
| **our independent estimate** | **9.9** |

Municipal water systems were engineered around a 1.6× peak. **Data-center demand is
about six times peakier** — and it peaks in the months rivers run lowest.

Our 9.9× and ICPRB's ~10× are built from completely different data (ours from
building-derived annual means; theirs from utility-reported use). Agreeing to ~1% is
a genuine **out-of-sample check**.

### The 70% error I found and fixed — worth understanding

The model originally computed the monthly shape from **cooling degree days**,
assuming water use tracks temperature. That gave July at **3.04×** the annual mean.

ICPRB's technical appendix publishes the **observed** monthly factors from actual
utility data in Loudoun and Prince William: July **1.5×**, August **1.8×**.

**We were ~70% too peaky in summer, and less than half the observed winter floor.**

The physical reason is obvious in hindsight: a data center runs its IT load
year-round and rejects heat year-round. Only the *incremental* evaporative duty
tracks temperature. JLARC confirms independently — Virginia data centers *"do not
currently participate in demand response programs"* because *"energy use is driven by
computing activity."*

**What changed when we fixed it:** the binding condition on Broad Run moved from
**July at 28.3%** of monthly flow to **September at 15.8%**. The sharp July spike was
an artifact of the model, not a feature of the world.

> **An honest complication we disclose rather than exploit:** ICPRB's public
> *fact sheet* says summer use is "close to three times the average annual demand" —
> which matches our *old wrong* number. Their *technical appendix* caps it at 1.8×.
> Two documents from the same institution disagree. We follow the appendix, because
> it's observed data rather than a summary sentence, and we say so.

## 15. Result 5: Broad Run — four sources, one basin

**FIGURE 4.** Four independent datasets converge on a single watershed:

| finding | number | source |
|---|---|---|
| concentration | **72.5% of the fleet on 19.9% of the land — 3.6×** | county watershed layer |
| the gage | flow record **ends 1986** | USGS NWIS |
| warming | **+0.094 °C/yr, p = 0.03** — the county's only significant trend | VA DEQ Theil-Sen |
| drought | **23 unbroken months** of severe drought, still open | NOAA/NCEI PDSI |

**On the statistics, stated carefully:** of 17 stations in the group, 15 have positive
slopes, 1 is exactly zero, 1 negative. A sign test on the 16 non-ties gives 15 of 16,
**two-tailed p = 0.0005**. Only Broad Run is individually significant. Statewide, only
49 of 413 stations are significant — but **47 of those 49 are warming and 2 cooling**,
and that split carries the inference, not any single station.

**Why the gage matters:** we divide today's demand by a flow record that stopped in
1986. Demand is indexed to a cooling-degree-day series that has risen 27–33%; supply
is divided by a gage that stopped forty years ago. **Both sides of the ratio are
anchored to different, mutually inconsistent periods.** That's a limitation we state,
not one a reviewer should have to find.

---

# PART VI — WHY YOU SHOULD BE BELIEVED

## 16. The validation that worked

The USGS thermoelectric water-use model covers 302 Virginia plant-years, built
independently of anything we used:

| fuel | USGS empirical | bounds | our constant | error |
|---|---:|---:|---:|---:|
| nuclear | 387.9 | 302.6 – 473.2 | 391 | **+0.8%** |
| gas | 191.5 | 155.8 – 232.8 | 196 | **+2.3%** |

Both inside 2.5%, well within the published uncertainty. Plus:

- **JLARC site count** — 24 PWC sites; our 2.25 buildings/site vs 2.27 statewide
- **Floor-area density** — ICPRB 10,370 sq ft/MW vs our 8,818 (15%)
- **Peak factor** — ICPRB ~10× vs our 9.9×
- **Level anchor** — JLARC's ~842 MW for PWC vs our vintage-matched **0.93×**
- **Parcel level** — on one Amazon parcel, 943,981 sq ft modelled against 1,297,200
  entitled = 72.8% captured, the rest unbuilt

## 17. The limits — state these before a reviewer does

**ICPRB is not an independent check on our power estimates.** Both derive facility
power from the **same JLARC/VADEQ air-permit database**. What *is* independent is
their calibration against utility-reported water use.

**The JLARC validation is partly in-sample.** JLARC's water distribution *includes*
Prince William buildings (Rpt598 App. B).

**The 309 WUP is circular.** It's derived by ICPRB from Prince William Water's
reported use ÷ JLARC permit capacity — our two inputs. It's an anchor, not a test.

**NOVEC/Dominion dual service.** A single Amazon parcel carries **both** a Dominion
switching station (110 ft) and a NOVEC substation (75 ft) on a shared pad
(PFR2025-00012). Attributing 100% of Scope 2 to Dominion's mix is wrong at *facility*
level. We can't quantify it — neither substation's capacity is published — so it's a
**stated limitation with a known direction of error.**

**±60% on inferred power.** Every scope scales with the same power estimate, so this
uncertainty **cancels in the shares** (88%, <3%, 43%, 0.87%) but **not in the absolute
volumes.** Say that explicitly — it is why the paper leads with shares.

---

# PART VII — WHERE EVERY NUMBER LIVES

| you want | file |
|---|---|
| every constant, with a verbatim source quote | `data/provenance_ledger.json` (32 entries) |
| the full narrative + all derivations | `METHODOLOGY.md` |
| what every source document says | `docs/source-reads/READING_LOG.md` (48 parts) |
| the convention table | `public/data/convention_table.json` |
| the entitlement analysis | `public/data/entitlement_pathway.json` |
| Broad Run | `public/data/broad_run_case.json` |
| validation + limitations | `public/data/validation_and_independence.json` |
| the model itself | `indirect_water_footprint.py` |
| the figures | `figures.py` → `figures/` |

**To check nothing is broken:**
```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3 verify_research_ready.py
```
24 checks. All must pass. Each **recomputes** from source rather than trusting a
stored value, and several are deliberately fault-injected to prove they'd catch a
regression.

---

# PART VIII — FIVE QUESTIONS YOU WILL BE ASKED

**"Isn't 43% versus 0.87% just you picking whichever number you like?"**
No — it's the opposite. We compute *all* of them and show the spread *is* the result.
Both conventions are standard and defensible; that's precisely why the choice
matters. Carbon accounting solved this by *requiring* dual location- and market-based
reporting. Water has no equivalent norm.

**"Your power estimates have ±60% uncertainty. Why should I believe anything?"**
Because every scope scales with the same power estimate, so it cancels in the shares.
88% Scope 2 is stable whether the fleet is 900 MW or 1,500 MW. We lead with shares and
say the absolute volumes are loosely constrained until load data is disclosed.

**"Aren't you just double-counting the power plant's water?"**
No. The power plant's water is *its* Scope 1 and the data center's Scope 2. That's how
the GHG Protocol handles carbon. The point isn't to add them — it's that nobody
currently assigns it to anyone.

**"Why does this county matter to anyone else?"**
Because the regulatory gap is national. Across the entire United States there are
**39 NPDES permits** coded to the data-center industry code. In Virginia, name-matching
finds **124 data-center facilities** but only **one** individual discharge permit. The
industry code captures 3% of them.

**"So what should change?"**
JLARC **Recommendation 6** already asks the General Assembly to authorize localities
to require water-use estimates. Our value-of-information analysis supplies the missing
number: what that disclosure would actually buy. And the disclosure argument is
stronger than "nobody measures this" — Dominion's GS-5 process **already collects
total site load broken down by building.** It is measured and withheld, not absent.

---

# PART IX — THE FASTEST PATH TO FLUENCY

If you read nothing else, read these in order:

1. **§8** — the Scope 2 equation. It generates the entire paper.
2. **§12** — the convention table. It *is* the thesis.
3. **§13** — zero SUPs. The second leg.
4. **§17** — the limitations. What a reviewer attacks first.

Then look at the four figures. If you can explain each one out loud in two sentences,
you can defend the paper.
