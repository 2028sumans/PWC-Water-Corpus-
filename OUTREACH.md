# Outreach — three emails, ready to send

**Look up the addresses yourself.** I'm not going to guess at them and have one bounce.
Find them on department pages or the papers' corresponding-author lines.

**Attach exactly one thing: `figures/F1_conventions.pdf`.** Nothing else. Not the
reading log, not the repo, not METHODOLOGY.md. Volume reads as noise; one figure and
one number read as rigour.

**Send them a few days apart, not all at once.** These people may know each other.

---

## EMAIL 1 — Landon Marston (Virginia Tech). Your best shot.

*Co-author of Siddik, Shehabi & Marston 2021, ERL — the closest prior work to yours.
Academic, in Virginia, no competing paper.*

**Subject:** Facility-level Scope 2 water for data centers — a question about your 2021 ERL paper

> Dear Professor Marston,
>
> I'm a high school student in Virginia. Building on your 2021 ERL paper with Siddik
> and Shehabi, I reconstructed Scope 1/2/3 water footprints for the 243 data-center
> buildings in Prince William County from public records — air permits, county GIS, and
> the USGS thermoelectric model — at building resolution rather than state averages.
>
> Scope 2 is 88% of the footprint. The result I'd value your view on is what happens
> when you vary the attribution convention: Lake Anna's share of that water runs from
> 43% under a Dominion utility-average mix to 0.9% under PJM short-run marginal
> shares — a factor of 50, for the same physical electricity. Your paper used a single
> convention, and I can't find anyone who has tested whether the choice matters.
>
> My argument is that this is different from the attributional–consequential debate in
> carbon accounting, because water is spatially indexed: the choice doesn't just change
> a number, it relocates the impact across a watershed boundary into a different
> regulator's jurisdiction.
>
> I have an AGU abstract accepted and a reproducible pipeline with 24 automated
> consistency checks. Before I write this up, would you have fifteen minutes to tell me
> whether that framing holds — and whether the delta over your paper is enough to be
> worth publishing?
>
> Figure attached.
>
> Suman Shah
> The Chapin School, Class of 2028

**Why this one works:** it engages his actual paper, names the specific gap, makes one
bounded ask, and doesn't pretend to be anything other than a student.

---

## EMAIL 2 — Privette et al. (AGU Advances 2026). A narrow technical question.

*Source of your Scope 3 range. Ask about that specifically — don't ask for mentorship.*

**Subject:** Question on embodied-vs-operational water ratios from your 2026 AGU Advances paper

> Dear Dr. Privette,
>
> I'm a high school student estimating water footprints for data centers in Prince
> William County, Virginia. I've used your embodied-vs-operational ratios as the anchor
> for a Scope 3 term (5–15% of Scope 1 + Scope 2), and I want to make sure I'm not
> misusing them.
>
> Two questions:
>
> 1. Is 5–15% still the range you'd apply to a facility-level estimate, or is it too
>    narrow? I'm aware at least one operator has disclosed embodied water above 90% of
>    its corporate total, which would put my anchor badly low.
> 2. Is there a better basis for a facility-scale supply-chain term than a proportion
>    of operational use?
>
> Scope 3 is about 9% of my total, so it doesn't drive my headline result — but it's
> the weakest number in the paper and I'd rather state its limits accurately than
> quietly hope nobody asks.
>
> Suman Shah
> The Chapin School, Class of 2028

**Why this one works:** it's a specific answerable question, it shows you already know
the weakness, and it costs them five minutes rather than a relationship.

---

## EMAIL 3 — ICPRB (A. Seck, cc Cherie Schultz). NOT a mentorship ask.

*They have a competing paper in preparation. This is deconfliction and courtesy. Send
it regardless of everything else — you do not want to be scooped or accused of
undisclosed overlap.*

**Subject:** Facility-level data-center water work in the Potomac basin — flagging overlap

> Dear Dr. Seck,
>
> I'm a high school student who has been working with your March 2026 fact sheet and
> the 2025 WMA Water Supply Study. I cite the fact sheet for the Scope 1/2/3 framing —
> which you published before I started — and the study for the WUP constants and the
> observed monthly factors in Table A.3-2.
>
> I've reconstructed facility-level Scope 1/2/3 water footprints for Prince William
> County's 243 data-center buildings, focusing on how the choice of electricity
> attribution convention changes which basin the Scope 2 water is assigned to.
>
> I noticed the study cites *"Will the Cloud Drain the River?"* as in preparation. I
> wanted to flag my work so we aren't unknowingly duplicating, and to ask whether
> there's anything you'd want me to be aware of before I submit. Happy to share
> methods or results if useful.
>
> With thanks — the WMA study has been the most useful document I've read on this.
>
> Suman Shah
> The Chapin School, Class of 2028

**Why this one works:** it's professional courtesy, it credits them properly, and it
protects you. If it turns into collaboration, good. If not, you've documented that you
disclosed.

---

## If nobody replies in three weeks

Expect roughly **1 reply in 5**. That's normal and not about you.

Then try, in order:
- **Md Abu Bakar Siddik** — first author on the 2021 paper, junior, usually more responsive
- **Arman Shehabi (LBNL)** — would know instantly whether your power ladder holds up
- **George Mason** — water policy / environmental science faculty. Local, in-basin, and
  the practical route to an affiliation. Less topically perfect, more likely to say yes
  to a nearby student.

---

## Three questions you will be asked. Have the answers loaded.

**"How is this different from attributional vs consequential LCA?"**
Water is spatially indexed; carbon isn't. A tonne of CO₂ is identical everywhere, so
the convention changes only a number. A gallon belongs to a basin and a regulator, so
the same choice relocates the impact geographically. That consequence doesn't exist in
the carbon literature.

**"How is this different from Siddik et al. 2021?"**
Building resolution instead of state averages, from air permits rather than modelled
allocation — and they used one convention where I test four and show the spread is 50×.

**"How do you validate ±60% power estimates?"**
Three ways. USGS thermoelectric factors, built independently, match my two key constants
to within 0.8% and 2.3%. JLARC's utility peak-load forecast — a completely different
measurement path — lands at 0.93× my vintage-matched fleet total. And every scope scales
with the same power estimate, so the uncertainty cancels in the shares I report, which
is why I lead with shares rather than volumes.
