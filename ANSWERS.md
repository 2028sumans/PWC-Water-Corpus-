# Nineteen questions, answered

Two of these caught real errors. Those are marked **⚠ YOU WERE RIGHT** and are fixed.

---

## 1. Is there a better way than "everything flows from IT power"?

**Better, yes. Available, no.**

The ideal is a **water meter on each building**. That's Scope 1 measured directly, no
model. Then an **electricity meter**, which gives Scope 2 exactly. Neither is public.

The chain we use — power → water — is forced by what exists. But notice it's not
arbitrary: it's the *same* chain ICPRB uses, the *same* one JLARC uses, and the same
one every published data-center water study uses. Because power is the only quantity
with any public trace at all (through air permits, which exist for a completely
unrelated reason — diesel generators emit pollutants).

**The honest framing for the paper:** we don't estimate water from power because it's
the best method. We do it because a data center's only publicly observable property
is the pollution permit for its backup generators.

---

## 2. What is permitted generator capacity, and how does it give IT power?

**What it is.** Data centers can't lose power — an outage costs millions. So they
install diesel generators as backup. Diesel engines emit NOx and particulates, so
**Virginia DEQ requires an air permit**, and permits are public records listing total
generator megawatts.

**Why it's a good proxy.** You size backup for the load you need to back up. A site
with 100 MW of IT load doesn't install 5 MW of generators — it installs enough to
carry the whole facility. So generator capacity and IT load are physically coupled by
engineering necessity.

**Why it needs adjustment.** They're deliberately oversized (see Q3).

**The one weakness to state:** it's a *permit*, not an installation. A site can be
permitted for more than it builds. That's part of why the derating range is wide.

---

## 3. Why are generators oversized? Two separate reasons.

### Redundancy (the 0.5)

Data centers are built to **N+1** or **2N** standards.

- **N** = exactly what you need
- **N+1** = one spare unit, so any single failure is survivable
- **2N** = a complete duplicate system

**Why:** a backup generator that fails during an outage is worthless. The whole point
is that it works on the one day you need it. So you buy two.

ICPRB's exact words: permitted capacity *"typically represents twice the actual IT
power load (i.e., 2N backup systems)."* Hence **0.5**.

### Utilization (the 0.8)

A data center's servers are not all working flat out. Racks are partly filled,
customers haven't grown into their space, workloads vary.

**Why:** you build capacity ahead of demand, because you can't add a substation in a
weekend. So the facility draws less than its design maximum. ICPRB uses **0.8**,
sourced to EPRI (2024).

**These are independent effects.** One is about hardware you bought and hope never to
use. The other is about hardware you're using below capacity.

---

## 4. What "combined derating factor = 0.4" means

It's just the two multiplied:

```
0.5  ×  0.8  =  0.4
↑        ↑
half is  and you use 80%
spare    of the rest
```

**Worked:** a site permitted for 100 MW of generators.
- Half is redundant spare → 50 MW of real capacity
- You run at 80% of that → **40 MW of actual IT load**

So `PERMIT_FACTOR_CENTRAL = 0.5 * 0.8` in code is written that way **deliberately** —
so the two assumptions stay visible and separately citable, instead of a bare `0.4`
that nobody can trace.

**The bounds** are the same calculation with pessimistic and optimistic values:

| | redundancy | × | utilization | = | factor |
|---|---:|---|---:|---|---:|
| low | 0.4 | × | 0.7 | = | **0.28** |
| central | 0.5 | × | 0.8 | = | **0.40** |
| high | 0.6 | × | 0.9 | = | **0.54** |

That range — 0.28 to 0.54, nearly 2× — is where much of your ±26% tier-1 uncertainty
comes from.

---

## 5. Rungs 2, 3, and 4 explained properly

All three use floor area. They differ in **how much you know about who built it.**

Think of estimating a person's weight from their height:

| rung | analogy | here |
|---|---|---|
| **2** | You have 5 people from this specific family, measured. Fit a line to *them*. | Operator has other buildings with air permits. Fit GFA→MW on **that operator's** buildings only. Amazon builds denser than Iron Mountain. |
| **3** | You have 14 people generally, measured. Fit a line to all of them. | Fit GFA→MW across **all 14 permitted sites** in the county, regardless of operator. |
| **4** | You have no measurements. Use the population average from a textbook. | Apply the flat constant: **GFA ÷ 8,818**. No fitting at all. |

**Why the ladder is ordered this way:** rung 2 captures operator-specific design
practice; rung 3 captures county-wide practice; rung 4 captures nothing
building-specific.

That's why uncertainty widens: **±26% (rung 1) → ±57% (rung 3) → ±60% (rung 4)**.

**Only 14 sites have permits**, which is the whole reason rungs 2–4 exist — and the
reason the interval is as wide as it is. This is also your value-of-information
argument: the ladder collapses to rung 1 for everyone if load data is published.

---

## 6. Evidence for the 4-year ramp

Ledgered as `gs5_four_year_ramp`. Two independent sources:

**The length** — Dominion Energy, GS-5 Large-Load Rate Class Report (May 2026),
verbatim: *"an extended, 14-year contract term (inclusive of a **four-year ramp
period**)."*

This is Dominion's own contract structure **for these exact customers**. They wrote a
four-year ramp into the tariff because that's how fast these facilities actually fill.

**The mechanism** — PWC Development Services, "New Structure - Data Center Buildings"
(effective 2021-04-05), verbatim: the Certificate of Occupancy is issued with unfitted
area *"designed to meet the Storage (S-1) Use Group's minimum requirements,"* and
*"after the Certificate of Occupancy is issued, an Alteration/Repair Building Permit
will be issued to convert or 'fit-out' the unused ... areas."*

So the county **explicitly states** that a building gets its CO with data halls not yet
built. "Completed" marks the *start* of fill-up.

**What's assumed, not sourced:** that the ramp is **linear**. Real fit-out is probably
stepwise (hall by hall). Bounded at 3 and 5 years. State this as a shape assumption.

---

## 7. Why closed-loop and air-cooled are the same Scope 1 tier

Because for *water*, they behave identically.

| system | how heat leaves | water lost |
|---|---|---|
| **evaporative / cooling tower** | water evaporates, carrying heat away | **large — this is consumption** |
| **air-cooled (dry)** | heat blown to outside air | ~none |
| **closed-loop** | water circulates in a sealed loop, dumps heat to air | ~none — the same water goes round |

Closed-loop still *contains* water, but it's the **same water forever**. Losses are
only leaks and occasional flushes. There's no evaporation, so no consumption.

**Both are grouped at the 150 gal/MW/day floor** — not zero, because there's still
humidification, domestic use, and occasional makeup.

**The tradeoff you must state:** both use *more electricity* than evaporative cooling,
because evaporation is thermodynamically cheap. So a facility that saves Scope 1 by
going dry **increases Scope 2** — and JLARC flags exactly this risk for a legislated
PUE mandate.

---

## 8. Evidence for the Scope 1 equation

The equation itself is trivial:

```
water/day = (MW) × (gallons per MW per day)
```

That's just unit multiplication — no physics assumed. **The content is entirely in
the WUP constant**, and that comes from ICPRB §6.2.2, verbatim:

> "In the Prince William Water service area, **0.42 MGD on average and 4.2 MGD for
> peak day were reported for 2023** ... These data yielded WUP values of ... **309 for
> the average and 3,060 for peak day in Prince William**."

So 309 = (Prince William Water's actually reported data-center use) ÷ (JLARC permitted
power). It is **measured water divided by measured power, for our county.** Not
modelled.

The tier bounds: **150** from Loudoun Water's 0.017 gal/day/sq ft × 8,818 sq ft/MW =
149.9; **1,577** is ICPRB's implied 100%-evaporative ceiling.

---

## 9. Can the 150–1,577 range be narrowed? Yes — three ways.

You're right that 10× is huge. It exists because **cooling technology is not
disclosed**, and it's the single largest Scope 1 uncertainty.

**What would close it, in order of feasibility:**

**(a) Air-permit descriptions — partly available now.** Cooling equipment sometimes
appears in mechanical permits. We tried this (`eportal_cooling_permits`) and it
failed — only 10 of 54 buildings had any, and they were site-level duplicates. But a
targeted records request to DEQ or Development Services for cooling-system type per
building would work, and it's a finite ask.

**(b) ICPRB's own split.** Their fact sheet says **~40% of basin facilities rely
exclusively on air cooling.** That's a *fleet-level* prior you're not currently using.
Applying it as a mixture rather than a flat range would tighten the county estimate
substantially — worth doing.

**(c) Operator disclosure.** Already used where public — it narrows 57 buildings.

**The honest note:** Prince William's observed 309 is already close to the air-cooled
floor of 150, and far below Loudoun's 1,006. **That is itself evidence** that this
county's fleet is air/chiller-dominant. You could argue the effective range is 150–800,
not 150–1,577 — but say it's an inference from the observed fleet average, not a
measurement.

---

## 10. Where the Scope 2 equation and the 24 come from

```
Scope 2 (MGD) = IT MW × PUE × 24 × gal/MWh ÷ 1,000,000
```

**The 24 is just hours in a day.** It's a unit conversion, nothing more:

- `IT MW × PUE` = megawatts the facility draws (a *rate*)
- `× 24` = megawatt-**hours** per day (an *amount*)
- `× gal/MWh` = gallons per day
- `÷ 1,000,000` = million gallons per day

The physics is entirely in `gal/MWh`. That comes from the **USGS Thermoelectric Water
Use model**, Virginia plants 2008–2020: nuclear 391, gas 196, coal 474, renewables 0 —
weighted by Dominion's generation mix to give **225.6 gal/MWh**.

**Implicit assumption to state:** `× 24` assumes the facility runs flat 24 hours. For
data centers that's very nearly true — JLARC confirms they don't demand-respond
because "energy use is driven by computing activity."

---

## 11. The 391 caveat, plainly

**Virginia has two nuclear plants and they behave completely differently.**

| plant | cooling | water consumed |
|---|---|---:|
| **North Anna** | closed-cycle — evaporates from Lake Anna | **~738 gal/MWh** |
| **Surry** | once-through on the tidal James — takes water, returns it | **0.00 gal/MWh** |

North Anna's figure is stable at 735.6–741.2 across all 13 years.

**391 is their generation-weighted average.** North Anna is ~53% of Virginia nuclear
output, so:

```
0.53 × 738  +  0.47 × 0  ≈  391
```

**Why you must say this:** a reviewer who knows nuclear plants will look up North Anna,
see ~738, see your 391, and conclude you're wrong by half. You're not — but only if you
state that 391 is a **fleet average across a consuming plant and a non-consuming one.**

**And here's the twist that matters:** because Surry consumes nothing, *all* of the
nuclear water is at North Anna. So when you attribute nuclear water to a basin, **100%
of it goes to Lake Anna / York.** That's why the York number is as large as it is.

---

## 12. Where 5–15% for Scope 3 comes from

**Privette et al. (2026), AGU Advances** — corporate disclosure ratios of embodied
(supply-chain) versus operational water.

**Be honest about what this is: it is the weakest number in your paper.**

- It's a **proportion**, not a physical estimate. No chip fab was modelled.
- The source is corporate self-disclosure, which is sparse and inconsistent.
- The ledger marks it `not machine-verifiable` — no PDF in the corpus.
- **At least one hyperscaler has disclosed embodied water exceeding 99% of its
  corporate total.** If that's representative, 5–15% is drastically too low.

**How to handle it:** report Scope 3 as an anchor with an explicit caveat, and make
sure **your headline results don't depend on it.** They don't — the 88% Scope 2 share
and the convention flip are both robust to Scope 3 being anywhere in 0–20%. Say so.

---

## 13. Monte Carlo, explained from scratch

**The problem.** Every constant is a range: PUE 1.15–1.35, WUP 150–1,577, derating
0.28–0.54. If you just multiply the middles you get one number and no idea how wrong
it could be.

**The naive fix (wrong).** Multiply all the lows for a low bound, all the highs for a
high bound. This gives an absurdly wide interval, because it assumes *everything* is
simultaneously at its worst — vanishingly unlikely.

**Monte Carlo.** Instead, do this 40,000 times:

1. Randomly pick a value for each parameter from its range
2. Compute the county total with those values
3. Write it down

You end up with 40,000 plausible totals. Sort them. The 5th percentile and 95th
percentile are your 90% interval: **41.4 – 60.5 MGD**.

**The subtle part — why "common random numbers" matters.**

Some parameters are **per-building** (this building's PUE). Some are **systematic**
(the grid's water intensity — if that's wrong, it's wrong for *every* building
simultaneously).

If you drew the grid intensity independently for each building, the errors would
average out across 243 buildings and you'd report a falsely narrow interval.

**So systematic parameters are drawn ONCE per iteration and shared across all
buildings.** That's the correct treatment and it's why your interval is honest rather
than flattering.

---

## 14. ⚠ YOU WERE RIGHT — why 43% and not 25%

**My explainer was wrong.** I wrote "25% of your electricity is nuclear, so 25%-worth
of your water." That's not how it works, and you caught it.

**Nuclear is 25% of the ENERGY but 43% of the WATER**, because nuclear is twice as
water-intensive as gas:

| fuel | share of energy | × gal/MWh | = water contribution | **share of water** |
|---|---:|---:|---:|---:|
| gas | 58% | 196 | 113.68 | 50.4% |
| **nuclear** | **25%** | **391** | **97.75** | **43.3%** |
| renewable | 14% | 0 | 0.00 | 0.0% |
| coal | 3% | 474 | 14.22 | 6.3% |
| | | | **225.6** | 100% |

`0.25 × 391 ÷ 225.6 = 43.3%` — and the convention table computes 43.32%.

Then, because **Surry consumes zero (Q11)**, all of that nuclear water is at North
Anna. Hence 43.3% at Lake Anna.

**I've noted the fix; correct it in `PAPER_EXPLAINED.md` §12.**

---

## 15. Cutting the entitlement result — I think you're half right

**Your objection is fair for AGU.** It's a land-use governance finding at a
geophysics conference. It may read as off-genre, and "our county doesn't regulate
this" does risk sounding parochial.

**But it isn't NIMBY.** NIMBY is *"don't build it near me."* Your finding is
*"nobody asks the question anywhere"* — and the mechanism (by-right zoning + no water
field on the form) exists in every jurisdiction with a data-center overlay. Loudoun,
Fairfax, Mesa, Hillsboro. Prince William is where it's *documented*, not where it's
unique.

**Its real job is to answer "so what?"** for leg 1. Without it, a reviewer asks: *if
the accounting is wrong, why doesn't someone fix it?* The answer is that the process
where it would be fixed never runs. Zero of 243.

**My recommendation:** keep **one sentence** in the abstract, move the full analysis
to the paper's discussion. Something like:

> Neither convention currently enters permitting: none of the 243 buildings underwent
> discretionary review at which a water condition could attach.

That preserves the "so what" without turning an AGU abstract into a zoning paper.
**Your call — it's a venue judgement, not a correctness one.**

---

## 16. ⚠ YOU WERE RIGHT — peakiness is NOT independently reproduced

**How 9.9 was computed:**

```
3,060 gal/MW/day (peak)  ÷  309 gal/MW/day (annual)  =  9.90
```

**Both of those constants are ICPRB's.** Both come from the same sentence, describing
the same source: Prince William Water's reported 2023 use of **0.42 MGD average and
4.2 MGD peak day** → ratio **10.0**.

**So our 9.9 and ICPRB's ~10 are the same number.** We divided their two figures by
each other. I described this as an "independent out-of-sample reproduction." **It is
not.** It's a consistency check on our own arithmetic.

**Fixed** in `seasonal_basin_surface.py` — the field is now
`NOT_AN_INDEPENDENT_REPRODUCTION` with the explanation.

### What IS genuinely independent — the coincidence

This part survives, and it's the claim that actually matters:

- **Demand peak (Jul–Sep)** — from ICPRB / utility water records
- **Flow minimum (Aug)** — from **USGS gage records**: Potomac at Little Falls drops
  to **41% of annual mean** in August; Cedar Run to **47%**

Two completely unrelated measurement systems. **"Demand peaks when flow bottoms" is
supported.** "We independently reproduced the peak factor" is not — drop that claim.

---

## 17. What Broad Run is for — and it's smaller than I implied

**Honest answer: Broad Run is about Scope 1, which is 2.9% of the footprint.** So it
cannot be a headline. You're right to question its weight.

**What it legitimately does:** it's the answer to *"fine, but is the local part at
least small and well-managed?"* And the answer is: small, but **concentrated and
unmeasured**.

- 72.5% of the fleet on 19.9% of the land (3.6× concentration)
- Flow denominator from a gage that **stopped in 1986**
- The only county stream with a significant warming trend
- Currently in the worst drought of the 132-year record

**Its real function is methodological honesty:** it shows that even the 3% you *can*
localise sits in a basin nobody has gaged for forty years. That supports your
disclosure argument.

**My recommendation:** demote it from "leg" to **one figure in the results**, framed as
a limitation on local measurement rather than a finding about harm. Given we've
established the paper is about accounting and not about damage, Broad Run should not
carry an impact claim.

---

## 18. Why NOVEC/Dominion dual service matters

**Your whole Scope 2 calculation assumes one thing: that these buildings buy Dominion
electricity, so Dominion's fuel mix applies.**

The Stinger Substation engineering plan (PFR2025-00012) shows a **single Amazon
parcel** with **both** a Dominion switching station (max 110 ft) **and** a NOVEC
substation (max 75 ft) on a shared 6.25-acre pad.

**Why that breaks the assumption:** NOVEC is a distribution cooperative. It owns no
generation and no transmission (it appears zero times in HIFLD's Virginia transmission
ownership). **It buys wholesale from the PJM market.** So NOVEC-served load has a
*PJM-market* fuel mix, not Dominion's.

**The direction of error, which you can state:** PJM-wide is 33.3% nuclear but spread
across plants in PA, NJ, IL and MD — very little of it at North Anna. So NOVEC-served
buildings have **less** Lake Anna exposure than we assign them.

**We are overstating the Lake Anna share.** We can't say by how much — neither
substation's capacity is published — so it's a limitation with a **known direction**,
which is far better than an unbounded one.

---

## 19. What "the 309 is circular" means

**Circular reasoning is when your test uses the same information as your model, so
agreement is guaranteed and proves nothing.**

Here's the loop:

```
ICPRB computed 309  =  PWW's reported water use  ÷  JLARC permitted power
                              ↑                            ↑
we use ─────────────────── this ────────────── and ─────── this
```

So if we used 309 to compute our water estimate and then "validated" it against
ICPRB's estimate, **we'd be checking whether A ÷ B × B = A.** It always agrees. It
tests nothing.

**What 309 actually is: an anchor.** It calibrates our model to observed county reality
— which is good and correct. It just isn't *evidence that the model works.*

**What IS a real test** (uses information we didn't use):
- **USGS thermoelectric water factors** — built by USGS from plant data, nothing to do
  with us. Nuclear +0.8%, gas +2.3%. **Genuine.**
- **JLARC's ~842 MW level anchor** — from *utility peak-load forecasts*, a completely
  different measurement path. We land at 0.93×. **Genuine.**

**The rule:** if a check shares an input with the model, call it an anchor. Only call
it validation if it's built from information the model never saw.

---

# What changed as a result of these questions

| # | outcome |
|---|---|
| **14** | Error in `PAPER_EXPLAINED.md` §12 — 25% is the *energy* share, 43.3% is the *water* share. Needs correcting. |
| **16** | **Fixed in code.** The "independent reproduction" claim was false; both figures are ICPRB's. The Aug flow-minimum coincidence *is* independent and survives. |
| **15** | Venue judgement — recommend one sentence in the abstract, full analysis in discussion. |
| **17** | Recommend demoting Broad Run from a leg to a limitations figure. |
| **9** | Actionable: apply ICPRB's "~40% air-cooled" as a mixture prior to narrow the Scope 1 range. |
| **12** | Scope 3 is your weakest number — verify no headline depends on it. (None does.) |
