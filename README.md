# Vira — Hyper-Local Data Center Diligence

MVP for Prince William County, VA. Bloomberg-density terminal + spatial map +
RAG-backed memo generation over a 22-doc policy corpus. Internal review build,
target ship June 1, 2026.

## What's in here

| Surface | Backed by |
|---|---|
| **Decision Terminal** — 156k-row virtualized table sorted by Vira Readiness | `parcels_scored.json` (147 MB, pre-computed nightly by `preprocess_score_parcels.py`) |
| **Spatial Map** — color-coded parcels + 15 toggleable overlay layers | `parcels.pmtiles` + 14 layer PMTiles (40 MB total), MapLibre + OpenFreeMap |
| **Right Panel** — 9 sub-scores, P10/P90 timeline projection, Conviction audit, dynamic source citations | `synthesizeSubScores.ts` + `climate_baselines.json` + `policy_index.json` |
| **LLM Memo / Counter-Memo / Q&A** — streamed Llama 3.3 70B output with BM25-retrieved citations | `/api/memo` → Groq Cloud + `rag_chunks.json` (1,523 chunks from 23 policy docs) |

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

The static data files (`parcels_scored.json`, the 15 PMTiles, 22 policy JSONs,
`climate_baselines.json`, `policy_index.json`, `rag_chunks.json`) live under
`public/data/` and `public/tiles/`. To rebuild them from the source GeoJSONs:

```bash
# 1. Download the PWC raw data (~8.6 GB) into a sibling directory:
#    ../Prince William County/{Data Center Intelligence,Enviro + Permitting Risk,
#    Natural and Environmental,Public and Political}/...
#    Source: https://gisdata-pwcgov.opendata.arcgis.com/
#    Override with PWC_DATA_ROOT env var if your layout differs.
#    See docs/Overlay_Specification.md for the full file inventory.

# 2. From the repo root (vira-ui/):
python3 preprocess_score_parcels.py    # ~12 min — parcel scoring (159k parcels)
python3 bake_map_layers.py             # ~30s — overlay PMTiles
python3 build_rag_index.py             # ~5s — RAG BM25 index
gzip -k -f public/data/parcels_scored.json   # compress the table-feed JSON

# 3. Bake the parcel PMTiles (after preprocess regenerates the GeoJSON):
cd public
tippecanoe -o tiles/parcels.pmtiles --layer=pwc-parcels \
  --minimum-zoom=8 --maximum-zoom=14 \
  --drop-densest-as-needed --extend-zooms-if-still-dropping --force \
  --include=GPIN --include=readiness --include=conviction \
  data/parcels_scored.geojson
```

The Python pipeline is excluded from Vercel deploys via `.vercelignore` — it
runs locally before deploy. Documentation (this README + `docs/`) is included
in the deploy context but not served by the Next.js app.

## Vercel deployment

```bash
# From vira-ui/
npm i -g vercel
vercel login
vercel link      # link to a project (create new if needed)

# Set the LLM API key as a Vercel env var so it's available in production:
vercel env add GROQ_API_KEY production
# (paste the same key from .env.local when prompted)

# Deploy
vercel --prod
```

`vercel.json` configures: function max-duration (60s for `/api/memo` to cover
slow Groq runs, 15s for `/api/tiles/[file]`), cache headers for static data,
and pins to `iad1` (us-east) to minimize round-trip latency to Groq's
east-coast endpoints.

Static assets larger than serverless body limits (the 147 MB
`parcels_scored.json` and 18-24 MB PMTiles files) are served by Vercel's CDN
directly, not through serverless functions, so the 4.5 MB function-response
ceiling doesn't apply.

## Demo walkthrough (6 steps, ~2 minutes)

1. **Open Decision Terminal** (the default view). 156,469 parcels listed,
   sorted by Vira Readiness Index descending. Search "MANASSAS 20110" or
   any Innovation Park address.
2. **Click the Hornbaker row** (GPIN `7596-81-5396`, Brentsville). Right
   panel opens: readiness 65/100, conviction 100/100, sub-score bars with
   per-quality badges (Measured / Modeled / Inferred), tag chips for every
   spatial flag, a "documented opposition" callout citing 4 speakers from
   the September 24 2025 Planning Commission meeting.
3. **Click the Conviction number** in the panel header. Audit popover shows
   all 26 data layers that contribute to the conviction score, grouped by
   category, with `✓` / strikethrough indicating which produced data for
   this specific parcel.
4. **Switch to Spatial Map** via the top toggle. Camera flies to Hornbaker
   at zoom 15 within ~1 second; surrounding parcels dim to ~38% opacity so
   the selected one pops. Click "Hard blockers" preset to see RPA / ERPO /
   Federal / FEMA / Dam zones light up. Toggle the DCOZ Overlay — Hornbaker
   visibly sits OUTSIDE it, explaining the SUP requirement.
5. **Click Generate Memo** in the right panel. Llama 3.3 70B streams a
   9-section planner-grade narrative (Executive Summary, Zoning Context,
   Overlay Districts, Comp Plan Consistency, Staff Concerns, Community
   Considerations, Sustainability Commitments, Recommendation). Each
   factual claim has a `[N]` citation chip linking back to the actual
   policy JSON page that supports it. Click "Generate" in the red
   Adversarial Counter-Memo block — same RAG corpus, flipped prompt,
   listing the strongest 3-5 reasons NOT to invest.
6. **Drag the timeline slider** from 2026 → 2042. Sub-scores recompute
   live (Power, Water, Cooling, Time-to-Energization, Dev Cost all decay
   under LOCA2 SSP3-7.0). P10 / P90 tick marks appear above the readiness
   bar showing the ensemble spread across SSP2-4.5 / SSP5-8.5. Toggle SSP
   buttons to see the curve shift.

## What the score is computed from

80 of 87 datasets in the source corpus actively contribute to the readiness
index. Categories:

- **30 spatial layers** (PWC GIS, HIFLD federal, FEMA NFHL): parcels, zoning,
  overlays (DCOZ, RPA, ERPO), hard-blocks (federal/state/county/protected/SFHA),
  hydrology (streams, wetlands, watersheds, dam-break inundation), soils,
  LiDAR Mass Points, easements, Cultural Polygons (building footprints),
  Stormwater (segments, facilities, structures), tree cover, land cover,
  Use Permits, BZA Variances, Planning Pending Cases, Data Center Projects,
  Data Center Buildings, CAMA Parcel Ownership.
- **24 climate JSONs** (LOCA2 SSP2-4.5/3-7.0/5-8.5 ensembles, PHDI/PDSI/PMDI/
  Palmer Z drought indices, county-level CDD/HDD/temp/precip monthly):
  drive the Water and Cooling baselines + the timeline-projection decay rates.
- **23 policy JSONs** (Comp Plan, CESMP, Hornbaker SUP, Reference Manual,
  PP213, FY2026 SUP Package, Ch32 zoning ordinance, JLARC 2024, PJM Manuals
  14B/14G/14H, VA Clean Economy Act, plus the Vira Methodology synthetic
  reference): per-parcel `policy_mentions` count + `active_sup` flag +
  opposition speaker extraction. Also serves as the RAG corpus for memo
  generation.

The 7 unused datasets are duplicates of HIFLD transmission layers, generic
PWC contours covered by Mass Points LiDAR, and minor utility data (culverts,
control points) with negligible signal for hyperscale DC siting.

## Demo prep checklist

Before any live demo session:

- [ ] `npm run dev` is running in a Terminal window the demoer controls
      directly (don't rely on a backgrounded process)
- [ ] `.env.local` has `GROQ_API_KEY=gsk_…`
- [ ] One trial memo + counter-memo + Q&A generated end-to-end against
      Hornbaker — confirms the LLM round-trip is warm
- [ ] Browser opened to `http://localhost:3000`
- [ ] Search bar starts cleared, no rows pre-selected (clean slate)
- [ ] Timeline slider at 2026, SSP3-7.0
- [ ] Devtools / Console closed, terminal in another window or hidden
- [ ] Chrome window in a clean profile (no extension popups, no autofill
      suggestions)

During the demo, the 6-step walkthrough above takes ~2 minutes total. If
the LLM stream stalls (rare with Groq), say "let's flip to the adversarial
view while it warms up" — the counter-memo button works independently and
gives you a second LLM call against the same corpus.
