# Vira June 1 Demo — Rehearsal Script

A 2-minute walkthrough that maps to the 6-step plan in
`/Users/2028sumans/.claude/plans/while-tahts-running-can-virtual-wall.md`.
The screen-by-screen flow below gives the demoer exact words, click targets,
and fallback patter for when the LLM is slow.

---

## Pre-flight (5 min before)

1. In **Terminal**, run `cd "/Users/2028sumans/Desktop/Vira Systems UI/vira-ui" && npm run dev`. Wait for `✓ Ready in …`. Leave this window open in the background.
2. In another terminal, sanity-check Groq:
   ```bash
   curl -s "http://localhost:3000/api/memo" -X POST -H "Content-Type: application/json" \
     -d '{"gpin":"7596-81-5396","mode":"qa","parcelContext":{"acres":40,"zoning":"M-2","dcoz":0,"readiness":65,"conviction":100,"activeSup":1,"oppSpeakers":4},"question":"warmup"}' | head -3
   ```
   Should see `VIRA-CITATIONS:` in the first line. If not, fix the env var
   or Groq key before proceeding.
3. Open Chrome → `http://localhost:3000`. Confirm:
   - Decision Terminal loads with `156,469 parcels`
   - Timeline reads "2026", SSP3-7.0 active
   - No row selected, search empty
4. **Close all Chrome tabs except this one.** Mute your mac. Hide Slack /
   notifications. Cmd-Q anything that pops badges.

---

## The walkthrough

### Step 1 — Land + filter (15 seconds)

> "This is the Decision Terminal — a Bloomberg-style view of every parcel
> in Prince William County, ranked by Vira's Readiness Index. 156,469 rows.
> The strongest siting candidates surface first."

- Point at the top 5 rows (all scoring 95+, all M-1/M-2 in DCOZ)
- In the left rail, click **Inside DCOZ** + **≥50 acres** filter checkboxes
- Table tightens to ~60 rows — the actually-buildable DC pipeline

> "These filters compose. I can also search by GPIN, street, zoning code,
> LRLU designation, or subdivision name."

- Type `Hornbaker` in the search box → table filters to ~1-2 rows

### Step 2 — Read a row (20 seconds)

> "I'm going to click the Hornbaker parcel. This is a live diligence case
> — there's an active Special Use Permit application in front of the
> Planning Commission right now."

- Click row GPIN `7596-81-5396`
- Right panel slides in showing **Readiness 65 / 100, Conviction 100 / 100**

> "Readiness 65 — amber, decent-but-real-friction. Conviction 100 — we
> have data from every layer for this parcel. Nine sub-scores below break
> down where the score comes from. Power is 100 because there's a
> substation under a mile away. Regulatory is dragged down because it's
> outside the DCOZ Overlay, so this parcel requires an SUP."

### Step 3 — Drill into the score (25 seconds)

> "Every claim has a citation. Look at these tags."

- Point at the chip row: `M-2 zoning`, `In DC campus: Devlin Technology Park`,
  `Active SUP application`, `4 opposition speakers`, etc.

> "The opposition data isn't hand-coded. We extracted '4 speakers, all in
> opposition' from page 17 of the live PC staff report. The system
> parsed the SUP narrative automatically."

- Click the **Conviction 100** number in the header
- Audit popover opens

> "Conviction is a separate score that says 'how much data do we actually
> have here?' Twenty-six layers contributed signal for this parcel — every
> single one. This is the honesty layer; a 78 readiness with conviction 95
> is meaningfully more trustworthy than an 85 readiness with conviction 40."

- Close the popover. Scroll down to the **Source Documentation** block.

> "These are the top 6 sources that actually drove the score for this
> specific parcel. The Hornbaker SUP staff report is here, the PWC Zoning
> Districts dataset, the HIFLD substations layer. Each link opens the
> source. Total transparency."

### Step 4 — Switch to the map (20 seconds)

> "Same parcel, spatial view."

- Click **Spatial Map** toggle in the top bar
- Camera flies to Hornbaker at zoom 15. Surrounding parcels dim to ~38%

> "The parcel is highlighted, surroundings dimmed. Color = readiness across
> the whole county."

- Click **Layers** (top right) → click **Hard blockers** preset

> "Federal land, state land, RPA, ERPO, FEMA flood, dam inundation — all
> the things that disqualify a parcel for hyperscale data center."

- Click the **DCOZ Overlay** toggle

> "And here's the DCOZ. Hornbaker visibly sits OUTSIDE the purple. That's
> the regulatory friction in one image — every approved data center campus
> in PWC is inside that polygon. This one isn't."

### Step 5 — Generate the memo (45 seconds)

> "Now the LLM. Single click."

- Click the amber **Generate Memo** button
- Wait ~2 seconds, tokens start streaming

> "Llama 3.3 70B running on Groq Cloud. It's reading the parcel context
> plus the top 12 most relevant chunks from our policy corpus —
> 22 PWC and Virginia documents totaling 3 million characters. Comprehensive
> Plan, CESMP, the Hornbaker staff report itself, the zoning ordinance,
> PJM Manuals, the JLARC report on Virginia's data center industry. Every
> claim is cited."

- Memo finishes in ~10-15 seconds (Groq is fast)
- Point at one of the amber `[N]` citation chips

> "Click any citation, the source file opens in a new tab. This is the
> diligence trail."

- Now scroll down to the **Adversarial Counter-Memo** block. Click **Generate**

> "Same corpus, flipped prompt. We don't sell parcels, we audit them. This
> is what could kill the deal."

- Counter-memo streams in (~10s)

### Step 6 — Move through time (30 seconds)

> "And finally — the timeline."

- Drag the bottom slider from 2026 → 2042
- Sub-score bars + composite readiness + map color all recalibrate live

> "Readiness 65 today, 56 in 2042 under SSP3-7.0. Power and Water decay
> hardest because PJM queue depth keeps growing and PWC's PHDI is already
> at -5.3 — we're in severe drought. The P10 and P90 tick marks above the
> bar show the ensemble spread across the other emission scenarios."

- Toggle SSP buttons left and right (SSP2-4.5, SSP5-8.5)

> "SSP2-4.5 — moderate emissions, 2.7°C warming — the optimistic case. The
> bands tighten. SSP5-8.5 — fossil-fueled, 4.4°C, worst case — readiness
> drops to 51 in 2042 because cooling load is 27% higher and water stress
> deepens."

- Drag back to 2026

> "Two minutes. Twenty-two policy documents indexed. 156,000 parcels scored.
> Every claim cited."

---

## Recovery patter

| Failure | Pivot |
|---|---|
| **LLM stream stalls** (rare on Groq) | "Let's flip to the counter-memo while it warms up" — click Generate on the red block. Both buttons call independent endpoints. |
| **Map tile doesn't paint a layer** | Toggle the layer off and on; if still bad, switch to the Decision Terminal — the score table never depends on tiles. |
| **The chosen parcel scores weirdly** | "The number isn't the point — the audit is. Click Conviction." Pivots to the data-depth narrative. |
| **Groq returns rate-limit (429)** | Wait 5s, retry. If sustained: switch to the **TOGETHER_API_KEY** fallback by removing GROQ_API_KEY from `.env.local` and restarting (Together's key is still wired but needs credit). |
| **Browser console floods with PMTiles range errors** | Hard refresh (Cmd+Shift+R). The route handler's in-memory buffer needs the cache cleared if it got stale. |

---

## What you're showing them

This is the wedge in 2 minutes:

1. **Hyper-local + comprehensive.** 80 datasets, one parcel-by-parcel view,
   every PWC overlay + policy doc + climate baseline informing the same
   ranking.
2. **Transparent provenance.** Every score has a citation chain. Every
   factual claim in the LLM memo has a clickable source.
3. **Adversarial honesty.** The counter-memo is built in by default —
   we're auditing parcels, not selling them.
4. **Forward simulation.** Real LOCA2 trajectories drive a 24-year
   readiness projection with P10/P90 bands. No competitor does this.
5. **Workflow, not report.** Two minutes from cold start to defensible
   investment narrative. CBRE / DCByte / JLL publish quarterly snapshots;
   we are continuously queryable.
