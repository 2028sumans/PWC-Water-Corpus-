# Advisor review request — 3 judgment calls

**Context.** Facility-level Scope 1/2/3 water estimator for 243 data-center buildings in Prince William County, VA, built entirely from public records. Targeting an AGU26 abstract (deadline **5 Aug 2026**). All arithmetic has been machine-verified (19 automated checks; every physical constant carries a verbatim source quote confirmed on its cited page). **What I need from you is judgment on interpretation, not on the numbers** — that's where the risk is concentrated.

Estimated reading time: **20 minutes** (METHODOLOGY §47, §49.4, §48).

---

## Call 1 — Is the headline claim honestly framed? (§47)

**The result.** Under average-mix (location-based) accounting, 18.8 MGD — 43% of the fleet's indirect water — is attributed to one out-of-basin reservoir (Lake Anna / North Anna). Under marginal-dispatch accounting, that attribution is **zero**.

**What's verified:**
- Surry reports **0.0** consumptive use (once-through, tidal James), so *all* Virginia nuclear water consumption is at North Anna (95.21 Mgal/d pooled 2018–20, USGS)
- North Anna → York basin, from USGS's own `Name.of.Water.Source` field
- PJM's published market data: coal 10.0% / gas 75.2% of marginal resources, 2022; **nuclear does not appear as a marginal resource at all**

**What's assumed:** that nuclear is never marginal. This is standard dispatch reasoning, and it is what drives the zero **by construction**. Verified robust — York stays 0.00 under every alternative marginal-mix parameterization tested (coal share 0–15%).

**Known limits, deliberately not claimed:** we do *not* claim where the marginal water goes. The destination is parameter-sensitive (Roanoke swings 0.00–11.11 MGD) and geographically under-determined (marginal generation is attributed to Virginia plants only, but PJM is a 13-state RTO).

> **Question:** Is *"the water at the reservoir does not change; the accounting convention does"* a defensible framing, or does presenting a construction-driven zero as a finding overstate it?

---

## Call 2 — How should the point estimate be reported? (§49.4)

The York figure scales with Dominion's generation mix. The model uses the 2025 IRP figure (nuclear 25%). Alternative conventions give:

| Mix convention | York (MGD) |
|---|---|
| 2025 generation mix (as used) | **18.8** |
| 2023 delivered-to-customers, ex-purchases | 28.4 |
| all-Virginia generation (coal 11%) | 21.0 |

York remains **0.00 under marginal accounting in every case**.

> **Question:** Report 18.8 as the headline with a sensitivity range, or lead with the *ratio* (43% → 0%) and treat the level as secondary? The ratio is more robust; the level is more concrete.

---

## Call 3 — Is the novelty claim correctly narrowed? (§48)

Literature checked: Siddik/Shehabi/Marston 2021; Mytton 2021; Li et al. 2023/2025; **Guidi & Dominici 2026** (arXiv:2607.02531 — 472 US hyperscale facilities, both pathways, different hotspot geographies, *location-based only*, "marginal": 0 occurrences); arXiv:2605.25854 (dispatch-aware water, but optimization on synthetic IEEE test buses); Privette et al. 2026 (*AGU Advances* commentary).

**Current position:** the displacement finding is *not* novel (Guidi & Dominici published it at national scale in June 2026). Neither the method (attributional vs consequential accounting) nor the concepts are novel. What was not found is an **empirical, basin-resolved demonstration on a real fleet that switching between two standard conventions relocates the largest attributed basin to zero.**

**Separate regional contribution:** ICPRB's own March 2026 study of this basin covers **on-site consumption only** (full-text: "power plant" 0, "electricity generation" 0, "off-site" 0). So ~87% of the footprint falls outside the boundary the regional water authority assessed.

> **Question:** Is this narrow enough to survive review, and is the regional gap or the convention-sensitivity the stronger lead?

---

## Known weaknesses (already documented, not hidden)

1. **n = 14** permit sites underpin the power model; it beats a single density constant by only 13.5% (slope ≈ 1.0). Framed as a *result*: floor area supports little more than a constant-density law.
2. **The 309 gal/MW/day intensity is circular for level validation** — ICPRB derived it from the local utility's own total. We validate distribution *shape* (JLARC metered data, KS p = 0.09), never *level*.
3. **87% of the footprint is an electricity calculation** (MW × PUE × published water factors), not a facility water measurement.
4. **~31% of Virginia electricity is net imports** from other PJM states, whose basins the model does not attribute at all — a second, larger displacement channel left uncounted.
5. Broad Run/Bull Run stream gages were discontinued (1986, 1981); climatologies used as stationary references.

## What is machine-verified (you should not need to re-check these)
13 source quotes confirmed verbatim **on their cited pages**; USGS consumption factors (391/196/474 gal/MWh) recomputed exactly from raw data by independently written code; JLARC source PDF SHA-256-identical to the official jlarc.virginia.gov copy; 19/19 automated checks passing, gating every deploy.
