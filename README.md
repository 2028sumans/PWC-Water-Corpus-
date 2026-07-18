# PWC Water Atlas — Data Center Scope 1/2/3 Water Footprint Estimator

Facility-centric water-footprint tool for Prince William County, VA data
centers. One view: every named DC building (203) and campus (51), ranked by
its estimated Scope 1/2/3 water footprint. There is no parcel browsing, no
parcel legibility score, and no spatial map — the product is the facility
dossier and the water-footprint estimate, full stop.

## What's in here

| Surface | Backed by |
|---|---|
| **Facilities view** — virtualized table of every DC building/campus, sorted by total Scope 1+2+3 MGD descending | `facility_profiles.json` |
| **Right Panel** — Scope 1/2/3 breakdown, power-estimate audit, facility dossier (permits/BZA/pending cases), water & site context | `build_facility_profiles.py` + `indirect_water_footprint.py` |
| **What's Unresolved** — the disclosure audit: a per-facility, deterministically computed list of what's on record, what's dark, its effect on the estimate, and what would close it | computed client-side in `RightPanel.tsx` from the facility record — **no LLM** |
| **LLM Memo / Q&A / Verdict** — streamed Llama 3.3 70B output with BM25-retrieved citations | `/api/memo` → Groq Cloud + `rag_chunks.json` (871 chunks, 15 docs) |

## The methodology

Every water number in this app traces to exactly one module,
`indirect_water_footprint.py` — read its docstring for the full citation
list. Summary:

- **Power estimate**: two independent methods, cross-checked. (A) GFA-based
  — floor area (coalesced across `GFA`/`BPGFA`/`ApprovedGFA`/`REATaxedGFA`/
  `PermittedGFA`) × an IT power density benchmark (100–200 W/sqft standard,
  250–450 W/sqft modern AI-class) × a PUE range selected by building
  vintage. (B) Operator-keyword match against interconnection.fyi's public
  interconnection-queue MW ranges. Where both exist and overlap, the range
  narrows to their intersection; where they disagree, both bounds are kept
  and the disagreement is flagged.
- **Scope 1 — on-site cooling**: facility power × the full published Water
  Usage Effectiveness envelope (0.0–2.4 L/kWh) — never narrowed to a single
  cooling technology, because no PWC dataset discloses which one any given
  facility uses.
- **Scope 2 — electricity-driven**: facility power × Dominion's
  generation-mix-blended consumption factor (~318 gal/MWh, NREL Macknick et
  al. 2011) at 90% assumed utilization.
- **Scope 3 — embodied/supply-chain**: a 5–15% proportional anchor on the
  Scope 1+2 operational total (Privette et al., AGU Advances 2026) — not a
  physical per-facility estimate, since chip fabrication is entirely outside
  Virginia and outside any PWC dataset.
- **Total**: the envelope sum of each scope's independent minimum and
  maximum — a conservative bound, not a statistical confidence interval.

### The disclosure audit is deterministic, not generated

"What's Unresolved" is computed in code from the facility's own record and
the estimator's inputs (`power.basis`, `pue_class`, `has_npdes`,
`n_wqp_stations_1mi`, the scope range widths, …). It is always visible —
there is no "Generate" button and no RAG round-trip — because these gaps
are structural and already fully known to the pipeline. Routing them
through an LLM would add latency and risk paraphrasing numbers we computed
exactly. Each item states four things: what is **on record**, what is
**dark**, its **effect on the estimate**, and what **would resolve** it.

The memo endpoint receives this same audit and is instructed to restate it
verbatim under `[U#]` markers rather than re-derive it. For the same
reason there is deliberately no adversarial "counter-memo" mode.

## Local dev

```bash
# 1. Get a Groq API key (free, no card) at https://console.groq.com/keys
# 2. Copy the env template and paste your key
cp .env.local.example .env.local
# Edit .env.local — replace PASTE_YOUR_GROQ_KEY_HERE with the key

# 3. Install + run
npm install
npm run dev
# → http://localhost:3000
```

The static data files the app actually serves (`facility_profiles.json`,
the 15 policy JSONs/PDFs under `public/data/policy/`, `rag_chunks.json`)
live under `public/data/`. To rebuild them from the source GeoJSONs:

```bash
# 1. Download the PWC raw data (~8.6 GB) into a sibling directory:
#    ../Prince William County/{Data Center Intelligence,Enviro + Permitting Risk,
#    Natural and Environmental,Public and Political}/...
#    Source: https://gisdata-pwcgov.opendata.arcgis.com/
#    Override with PWC_DATA_ROOT env var if your layout differs.
#    See docs/Overlay_Specification.md for the full file inventory.

# 2. From the repo root:
python3 preprocess_score_parcels.py    # ~12 min — parcel-level water/disclosure
                                        # context. LOCAL INTERMEDIATE ONLY: writes
                                        # public/data/parcels_scored.json, which
                                        # build_facility_profiles.py reads below but
                                        # the Next.js app never serves (.vercelignore
                                        # + .gitignore both exclude it).
python3 build_facility_profiles.py     # facility dossiers + Scope 1/2/3 estimates
                                        # -> public/data/facility_profiles.json (the
                                        # only one of these three the app fetches)
python3 build_rag_index.py             # ~5s — RAG BM25 index -> rag_chunks.json
```

The Python pipeline is excluded from Vercel deploys via `.vercelignore` — it
runs locally before deploy. Documentation (this README + `docs/`) is included
in the deploy context but not served by the Next.js app.

## Vercel deployment

```bash
npm i -g vercel
vercel login
vercel link      # link to a project (create new if needed)

# Set the LLM API key as a Vercel env var so it's available in production:
vercel env add GROQ_API_KEY production
# (paste the same key from .env.local when prompted)

# Deploy
vercel --prod
```

`vercel.json` configures: a 60s function max-duration for `/api/memo` (to
cover slow Groq runs), cache headers for the static data files, and pins to
`iad1` (us-east) to minimize round-trip latency to Groq's east-coast
endpoints.

## Walkthrough (5 steps, ~90 seconds)

1. **Open the app.** The Facilities view lists all 254 buildings + campuses,
   sorted by total estimated Scope 1+2+3 MGD descending — the tool's
   headline finding is the top row, not something you have to search for.
2. **Click a facility.** Right panel opens: the Scope 1+2+3 hero range,
   a "Methodology" popover (click it) showing exactly which of the two
   independent power methods contributed and why, a per-scope breakdown
   with each scope's own methodology line, the facility dossier (status,
   year built, permits, matched case history), and water/site context
   badges (watershed, NPDES status, RPA/wetland/dam flags).
3. **Scroll to "What's Unresolved."** No button, no waiting — the
   disclosure audit is already there, computed for this specific facility:
   `[U1]` no metered withdrawal anywhere in the record, `[U2]` undisclosed
   cooling technology and the exact share of the range width it accounts
   for, `[U3]` whether the power estimate was cross-checked by two methods
   or rests on one, and so on. This is the argument the tool exists to
   make, so it is stated rather than generated.
4. **Click Generate Memo.** Llama 3.3 70B streams an 8-section narrative
   (Executive Summary through Recommendation for Further Diligence) — every
   factual claim carries a `[N]` citation chip linking back to the actual
   policy document that supports it, and its "What's Unresolved" section
   restates the audit above under `[U#]` markers rather than improvising.
5. **Ask a question** in the Q&A box — free-form, grounded in the same
   facility context and policy corpus.

## Demo prep checklist

Before any live demo session:

- [ ] `npm run dev` is running in a Terminal window the demoer controls
      directly (don't rely on a backgrounded process)
- [ ] `.env.local` has `GROQ_API_KEY=gsk_…`
- [ ] One trial memo + Q&A generated end-to-end against a built data
      center — confirms the LLM round-trip is warm
- [ ] Browser opened to `http://localhost:3000`
- [ ] Search bar starts cleared, no rows pre-selected (clean slate)
- [ ] Devtools / Console closed, terminal in another window or hidden
- [ ] Chrome window in a clean profile (no extension popups, no autofill
      suggestions)

During the demo, the 5-step walkthrough above takes under two minutes. If
the LLM stream stalls (rare with Groq), fall back to step 3 — "What's
Unresolved" needs no network call at all, and it carries the argument on
its own.
