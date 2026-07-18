# Vira Polarity Audit

Every signal that contributes to the Vira Readiness Index, audited against
the framing question: **"Can a NEW data center investor build here?"**

Polarity column reads:
- **➕** = signal raises readiness (more attractive for new DC siting)
- **➖** = signal lowers readiness
- **🚫** = hard-block (parcel returns a score in the 3–18 range, can't be developed)

If you disagree with any polarity below, the fix is one edit each in
`preprocess_score_parcels.py` (the heuristic that powers the score in
`parcels_scored.json`) and `vira-ui/src/lib/synthesizeSubScores.ts` (the
sub-score derivation that powers the right panel + table).

---

## Tier 0 — Hard blocks (parcel returns 3-18, no further math)

| Signal | Polarity | Returned score | Why |
|---|---|---|---|
| `federal` (Federal Land) | 🚫 | 3 | Federal ownership; cannot acquire for private development |
| `state_land` (State Land) | 🚫 | 5 | State ownership; similar |
| `protected` (Protected Open Space) | 🚫 | 6 | Conservation easements + fee-simple parks; legally prohibited from non-conservation use |
| `county_land` (County Land) | 🚫 | 8 | County-owned; not on the market for hyperscale |
| `sfha` (FEMA SFHA Zone A/AE/VE) | 🚫 | 12 | Floodplain; insurance, regulatory, and physical reasons rule out hyperscale |
| `wetland` (Hydrological Features centroid) | 🚫 | 14 | Wetland; CWA §404 permit gauntlet, ~100% denial for hyperscale |
| `rpa` (Resource Protection Area) | 🚫 | 18 | Chesapeake Bay Preservation Act; soft hard-block (can build in non-RPA portion if parcel straddles, but for centroid-in-RPA this is effectively blocking) |

---

## Tier 1 — Fundamental enablers (raise readiness most)

| Signal | Polarity | Max contribution | Why |
|---|---|---|---|
| Acreage ≥ 100 ac | ➕ | +16 | Hyperscale campuses need ≥ 50 ac; ≥ 100 ac gives expansion runway |
| Acreage 50-99 | ➕ | +12 | Single-building hyperscale viable |
| Acreage 20-49 | ➕ | +8 | Single-building DC (sub-hyperscale) viable |
| Acreage 10-19 | ➕ | +4 | Colo / edge facility viable |
| Acreage 5-9 | ➕ | +2 | Niche use cases only |
| Acreage 3-5 | (neutral, capped at 35) | — | Too small for most DC builds; soft penalty via cap |
| Acreage < 3 | ➖ | (returns ≤ 35) | Too small for hyperscale; effectively excluded |
| Acreage < 1 | ➖ | (returns ≤ 20) | Not a DC parcel |
| Zoning **M-2** (Light Industrial) | ➕ | +16 | THE canonical by-right DC zone under §32-509 |
| Zoning **M/T** (Mixed Technology) | ➕ | +14 | Tech-friendly hybrid zone |
| Zoning **M-1** (Heavy Industrial) | ➕ | +12 | Industrial zone, DC allowed by SUP or by-right depending on overlay |
| Zoning **PBD / PMD** (Planned Business / Mixed) | ➕ | +9 | Can include DC in master plan |
| Zoning **O(…)** (Office overlay variants) | ➕ | +4 | Office-to-DC conversion possible with SUP |
| Zoning **A-1 / A-1C** (Agricultural) | ➖ | −2 | Requires rezoning; multi-step process |
| Zoning **B-1 / B-2 / B-3** (Commercial) | ➖ | −8 | Commercial-to-DC is uncommon, requires rezone + SUP |
| Zoning **R-* / SR-1 / SR-5 / TWN / RPC** (Residential) | ➖➖ | −25 | Residential-to-DC is nearly impossible (community resistance + comp plan mismatch + rezoning complexity) |
| `dcoz == 1` (Inside Data Center Opportunity Zone Overlay, §32-509) | ➕ | +12 | By-right DC use; no SUP required; saves ~12 months and ~20% denial risk |
| `lrlu == "I-4"` (LRLU: heaviest industrial) | ➕ | +7 | Comprehensive Plan blesses industrial use |
| `lrlu == "I-3"` | ➕ | +5 | Industrial designation |
| `lrlu == "I-2"` | ➕ | +3 | Light-industrial designation |

---

## Tier 2 — Power proximity (the #1 binding constraint for hyperscale)

| Signal | Polarity | Contribution | Why |
|---|---|---|---|
| Substation < 0.5 mi | ➕ | +13 | Practically instantly interconnectable |
| Substation 0.5–1 mi | ➕ | +11 | Very close |
| Substation 1–2 mi | ➕ | +8 | Strong |
| Substation 2–3 mi | ➕ | +6 | OK, modest tap-line cost |
| Substation 3–5 mi | ➕ | +3 | Marginal |
| Substation > 8 mi | ➖ | −4 | Remote — major buildout cost |
| 230 kV+ line < 0.25 mi | ➕ | +7 | Dual-feed potential = redundancy |
| 230 kV+ line 0.25–0.5 mi | ➕ | +6 | Strong dual-feed candidate |
| 230 kV+ line 0.5–1 mi | ➕ | +4 | Good |
| 230 kV+ line 1–2 mi | ➕ | +2 | Acceptable |
| 230 kV+ line > 5 mi | ➖ | −3 | Hyperscale-impractical |

---

## Tier 3 — Environmental / site-condition modifiers

| Signal | Polarity | Contribution | Why |
|---|---|---|---|
| `dam` + `dam_haz_class == "HIGH"` (high-hazard inundation) | ➖ | −12 | VA-DCR rules + insurance risk |
| `dam` + `dam_haz_class == "SIG"` | ➖ | −6 | Significant hazard |
| `dam` + `dam_haz_class == "LOW"` | ➖ | −3 | Low hazard |
| `erpo == 1` (Environmental Resource Protection Overlay, watershed protection) | ➖ | −3 | Stricter permitting, not a block |
| `easement == 1` (any easement intersects parcel) | ➖ | −2 | Buildable-footprint encumbrance |
| `soil_cat == "I"` (best constructibility) | ➕ | +3 | Lowest foundation cost |
| `soil_cat == "II"` | ➕ | +2 | Good |
| `soil_cat == "III"` | ➖ | −1 | Middling |
| `soil_cat == "IV"` (worst) | ➖ | −3 | Highest grading + foundation cost |
| `slope_pct ≥ 15%` | ➖ | −4 | Major grading cost |
| `slope_pct 8–14%` | ➖ | −1 | Moderate grading |
| `slope_pct < 3%` | ➕ | +1 | Nearly flat |
| `hsg == "D"` (poor drainage hydrologic soil group) | ➖ | −1 | Stormwater complications |
| `d_stream_ft < 100` (RPA buffer trigger zone) | ➖ | −4 | 100 ft setback typically applies |
| `d_stream_ft < 300` | ➖ | −1 | Mild buffer concern |
| `_centroid_in_tree == 1` (tree polygon at centroid) | ➖ | −2 | Clearing cost |
| `land_cover == "Open Water"` | ➖➖ | −8 | Can't build on water (✱ fixed in audit) |
| `land_cover == "Impervious Surface"` | ➖ | −1 | Existing structure — demolition cost |
| `land_cover == "Non-woody Vegetation" / "Bare Land"` | ➕ | +2 | Cleared, ready |
| `land_cover == "Woody Vegetation" / "Forest"` | ➖ | −1 | Clearing required (✱ "Woody Vegetation" missed before audit) |
| LiDAR `elev_range ≥ 80 ft` | ➖ | −5 | Severe grading required |
| LiDAR `elev_range 40–79 ft` | ➖ | −2 | Notable grading |
| LiDAR `elev_range < 10 ft` | ➕ | +1 | Very flat |
| `sw_segments ≥ 5` (many stormwater segments cross parcel) | ➖ | −3 | Utility easement encumbrance |
| `sw_segments 2–4` | ➖ | −1 | Some encumbrance |
| `sw_facilities ≥ 1` (detention basin INSIDE parcel) | ➖ | −4 | Major footprint loss |
| `sw_structures ≥ 5` (drainage inlets in parcel) | ➖ | −2 | Drainage-heavy site |

---

## Tier 4 — Market signals

| Signal | Polarity | Contribution | Why |
|---|---|---|---|
| `in_dc_campus == 1` (parcel sits INSIDE a planned/built DC project polygon) | ➖➖ | **−15** | **Site control already taken** — another applicant holds this parcel. You CANNOT build a new competing DC on land already committed to someone else's project. (✱ this was +10 before audit; **flipped to −15**) |
| `dc_bldgs_1mi ≥ 5` (5+ DC buildings within 1 mi) | ➕ | +4 | DC corridor — grid already built out, peer parcels precedented |
| `dc_bldgs_1mi 2–4` | ➕ | +2 | Some DC activity nearby |
| `dc_bldgs_1mi == 0` | (neutral) | — | Not a corridor, not a problem |
| `mzp_use` matches IND / I-3 / I-4 / M-2 / TECH (MZP landbay industrial) | ➕ | +4 | Master Zoning Plan blesses industrial use |
| `mzp_use == "COM"` | ➕ | +1 | Commercial-zoned within MZP — possible DC under SUP |
| `owner_n_parcels ≥ 10` (CAMA owner consolidates many parcels) | ➕ | +4 | Easy site assembly — but excludes WITHHELD/government/HOAs/residential developers (✱ exclusion added in audit) |
| `owner_n_parcels 3–9` | ➕ | +2 | Modest consolidation |

---

## Tier 5 — Regulatory friction + policy

| Signal | Polarity | Contribution | Why |
|---|---|---|---|
| `sup_1mi 6–30` (moderate historical SUP density) | ➕ | +2 | Familiar regulatory pathway, staff/PC have seen DC asks before |
| `sup_1mi > 30` (saturated SUP density) | ➕ | +1 | Diminishing returns; mostly informational |
| `bza_1mi ≥ 10` (many BZA variances within 1 mi) | ➖ | −3 | High neighborhood friction historically |
| `bza_1mi 5–9` | ➖ | −1 | Some friction |
| `pending_05mi ≥ 3` (3+ pending cases within 0.5 mi) | ➖ | −2 | Competitive pressure + staff workload |
| `pending_05mi 1–2` | ➖ | −1 | Mild |
| `bldg_500ft ≥ 30` (dense neighbor buildings within 500 ft) | ➖ | −4 | High community-opposition risk |
| `bldg_500ft 10–29` | ➖ | −1 | Moderate |
| `bldg_500ft == 0` | ➕ | +2 | Isolated parcel, low neighbor exposure |
| `active_sup == 1` (live SUP application on this parcel) | ➖ | −6 | Regulatory uncertainty + uncertain timeline |
| `opp_speakers ≥ 4` (4+ speakers in documented opposition) | ➖ | −8 | Strong organized opposition (the Hornbaker case) |
| `opp_speakers 2–3` | ➖ | −4 | Documented but smaller opposition |
| `opp_speakers == 1` | ➖ | −1 | Minimal opposition signal |
| `opp_topics_n ≥ 4` (breadth of distinct concerns) | ➖ | −4 | Suggests organized resistance across multiple dimensions |
| `policy_mentions > 500` (zoning code mentioned heavily in policy corpus) | ➕ | +1 | Well-defined regulatory pathway |
| `policy_mentions < 5` | ➖ | −1 | Untracked / uncommon zoning category |

---

## What changed in this audit

| Fix | Before | After |
|---|---|---|
| `in_dc_campus` polarity | +10 (treated as positive: "already entitled") | **−15** (treated as negative: "site already taken by another applicant") |
| `land_cover == "Woody Vegetation"` | missed (no penalty) | −1 (clearing required) |
| `land_cover == "Open Water"` | missed (no penalty) | −8 (can't build on water) |
| `owner_n_parcels` bonus | applied unconditionally | excludes WITHHELD, BOARD OF COUNTY, HOMES LLC, HOAs, PARKS & REC |
| LLM system prompt | called `in_dc_campus` "positive signal" | now correctly explains "site control taken by another applicant" |
| Right panel badge for `in_dc_campus` | green "In DC campus" | red "Site taken by …" |

---

## Things we deliberately KEPT, but that a sharp reviewer might question

1. **`sup_1mi` moderate density treated as positive.** A skeptic could argue "lots of SUP history = contested area." We treat it as "familiar regulatory pathway." Defensible either way; we went with familiarity since SUP precedent helps PWC staff act predictably.

2. **`bldg_500ft == 0` treated as positive.** Argues "isolated = fewer neighbors to object." Could also be read as "no infrastructure neighbors = greenfield premium." We chose the political-risk framing.

3. **`land_cover == "Impervious Surface"` treated as mildly negative.** Could be argued positive ("already disturbed = less environmental review"). We went negative because hyperscale demolition cost usually dominates the regulatory savings.

4. **No magnitude difference between dam-break hazard classes for development cost.** All three classes (HIGH/SIG/LOW) carry the same modifier through the Development Cost sub-score, only differing in the headline composite. Fine for MVP but a deeper model would tier it.

5. **The composite formula uses equal default weights (20/20/15/10/10/10/5/5/5) but the user can drag any sub-score weight to 100%.** This is intentional per the plan's "transparent provenance with user reweighting" pillar.

---

## How to read a Vira Readiness number

A parcel scores `R = max(0, min(100, base + sum(modifiers)))`:

- **Base** = 25 (after passing all hard-block filters)
- **Modifiers** = the contributions in this audit, summed
- **Hard-block override** = if any Tier-0 signal fires, the score is forced to 3–18

So a parcel scoring 80 means: passed all hard blocks, then earned ~+55 net
across modifiers. The largest single positive achievable is `+16 acreage + 16
zoning + 12 DCOZ + 13 substation + 7 transmission + 7 LRLU + 4 corridor + 4
MZP + 3 soil + 2 land-cover + 2 SUP precedent + 4 owner` = 90 points of
positive headroom over the 25 base = a theoretical 100+ that caps at 100.
The largest single negative achievable (after passing hard blocks) is
~−60 from residential zoning + dam-HIGH + opposition + sw_facilities +
in_dc_campus + steep slope, which would crater the score to ~0–10.

The actual distribution lands almost entirely in 20–39 because the modal
PWC parcel is small (~1 acre), residential or agricultural, far from
substations, and not in DCOZ. That's the correct denominator.
