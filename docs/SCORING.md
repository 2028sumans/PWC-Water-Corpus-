# Vira Readiness Index — Scoring Reference

The complete scoring logic for every Prince William County parcel.
Just the formulas, in tables.

The composite Vira Readiness Index is a weighted average of 9 sub-scores,
each 0–100. Default weights:

| Sub-score | Weight |
|---|---|
| Power Readiness | 20% |
| Regulatory Readiness | 20% |
| Environmental Viability | 15% |
| Water Sustainability | 10% |
| Time-to-Energization | 10% |
| Land Feasibility | 10% |
| Political Risk | 5% |
| Cooling Cost | 5% |
| Development Cost | 5% |

Composite = weighted sum, capped by Option B (see end), clipped to [0, 100].

---

## 1. Power Readiness — base from substation distance curve

Substation distance (`d_sub_mi`, piecewise linear; only IN SERVICE 230 kV+ substations count):

| Distance | Points |
|---|---|
| 0 mi | 100 |
| 0.5 mi | 98 |
| 1 mi | 94 |
| 2 mi | 88 |
| 3 mi | 80 |
| 5 mi | 68 |
| 8 mi | 50 |
| 20 mi | 25 |

Then add the 230 kV+ line adjustment (`d_230_mi`, only IN SERVICE):

| Distance | Adjust |
|---|---|
| 0–0.25 mi | +12 |
| 0.5 mi | +9 |
| 1 mi | +5 |
| 3 mi | 0 |
| 10+ mi | −15 |

DC corridor neighbors (`dc_bldgs_1mi` — DC buildings within 1 mi):

| Count | Adjust |
|---|---|
| ≥5 | +6 |
| 2–4 | +3 + 0.6 × (n−2) |
| 0–1 | 0 |

---

## 2. Regulatory Readiness — base 40

| Signal | Adjust |
|---|---|
| Inside DCOZ (Data Center Opportunity Zone overlay) | +30 |
| Zoning M-1 / M-2 / M/T | +20 |
| Zoning PBD / PMD | +15 |
| Zoning R-* / SR-1 / SR-5 / TWN / RPC | −25 |
| Zoning A-1 / A-1C | −5 |
| SUP precedent 6–30 within 1 mi | +5 |
| SUP precedent < 2 within 1 mi | −3 |
| BZA ≥ 10 within 1 mi | −8 |
| BZA ≥ 5 within 1 mi | −3 |
| MZP industrial (IND / I-3 / I-4 / M-2 / TECH) | +6 |
| Built DC on parcel — saturated < 15 ac/bldg | −22 |
| Built DC — 30 ac/bldg | −16 |
| Built DC — 60 ac/bldg | −10 |
| Built DC — ≥ 120 ac/bldg | −5 |
| Planned DC campus, ≤ 50 ac parcel | −13 |
| Planned DC campus, 200 ac | −10 |
| Planned DC campus, 500 ac | −6 |
| Planned DC campus, ≥ 2000 ac | −3 |
| Trifecta synergy (industrial + DCOZ + greenfield) | +5 |
| Orphan zoning (industrial − DCOZ + power > 6 mi) | −8 |
| Compounded friction (outside DCOZ + active SUP) | −4 |

**Hard-block override**: if any of {federal, state, county, protected, sfha, rpa, wetland} → final ≤ 25.

---

## 3. Environmental Viability — base 80, hard-block tier replaces it

| Tier (first match wins) | Final value |
|---|---|
| Federal / State / County / Protected Open Space (fee-simple or conservation easement) | 0 |
| FEMA SFHA centroid hit | 8 |
| Wetland centroid hit (Hydrological Features) | 12 |
| RPA centroid hit | 22 |
| None of the above | 80 |

Then modifiers (ERPO + stream only fire if floor > 25; dam-break fires unconditionally then clips at 0):

| Signal | Adjust |
|---|---|
| ERPO overlay | −8 |
| Dam-break HIGH hazard | −20 |
| Dam-break SIG | −10 |
| Dam-break LOW (or other) | −4 |
| Stream < 100 ft (RPA buffer trigger) | −10 |
| Stream < 300 ft | −3 |

---

## 4. Water Sustainability — base = `water_baseline_2026` from climate (~49 at PHDI −5.30)

| Signal | Adjust |
|---|---|
| HSG-D (poor drainage) | −6 |
| HSG-A (good drainage) | +4 |
| ERPO overlay | −4 |

Fallback base if `climate_baselines.json` hasn't loaded: 62.

---

## 5. Time-to-Energization — base 45

| Signal | Adjust |
|---|---|
| Inside DCOZ | +20 |
| Zoning M-1 / M-2 / M/T | +10 |
| Power proximity (`d_sub_mi`) — at 0 mi | +12 |
| at 1 mi | +11 |
| at 3 mi | +7 |
| at 5+ mi | 0 |
| Built DC on parcel — saturated < 15 ac/bldg | −20 |
| Built DC — 30 ac/bldg | −14 |
| Built DC — 60 ac/bldg | −8 |
| Built DC — ≥ 120 ac/bldg | −4 |
| Planned DC campus, ≤ 50 ac parcel | −10 |
| Planned DC campus, 200 ac | −8 |
| Planned DC campus, 500 ac | −5 |
| Planned DC campus, ≥ 2000 ac | −2 |
| Pending cases nearby — 1 | −3 |
| Pending cases nearby — 3 | −8 |
| Pending cases nearby — 10 | −12 |
| Trifecta unlock (industrial + DCOZ + power-close + greenfield) | +4 |

**Hard-block override**: if any hard-block flag → final ≤ 20.

---

## 6. Land Feasibility — base from acreage curve

| Acres | Base |
|---|---|
| 0 | 8 |
| 1 | 18 |
| 3 | 32 |
| 10 | 45 |
| 25 | 65 |
| 50 | 78 |
| 100 | 88 |
| 300+ | 95 |

**Hard-block ownership** (federal / state / county / protected) → 0 (overrides curve).

Then:

| Signal | Adjust |
|---|---|
| Soil cat I | +5 |
| Soil cat II | +2 |
| Soil cat III | −2 |
| Soil cat IV | −6 |
| Slope at 5% | 0 |
| Slope at 8% | −2 |
| Slope at 15% | −6 |
| Slope at 30% | −10 |
| Elev range (LiDAR) 10 ft | +2 |
| Elev range 40 ft | −3 |
| Elev range ≥ 80 ft | −8 |
| Easements on parcel | −4 |
| Stormwater segments ≥ 5 | −4 |
| Stormwater segments ≥ 2 | −1 |
| Stormwater facility (detention basin) inside parcel ≥ 1 | −6 |
| Stormwater structures ≥ 5 | −2 |
| Land cover: impervious / pavement / structure | −3 |
| Land cover: barren / non-woody | +3 |
| Land cover: tree / forest | −2 |
| Tree at centroid | −2 |
| Same owner holds ≥ 10 parcels (not excluded entity) | +4 |
| Same owner holds ≥ 3 parcels (not excluded entity) | +2 |

Owner-consolidation bonus is suppressed when the CAMA owner name matches WITHHELD / BOARD OF COUNTY / HOMEOWNERS / PARKS & REC / HOMES LLC / HOMES INC / HOMES CORP / ASSOC INC / ASSOC (these are not viable DC site assemblers).

---

## 7. Political Risk — base 50

| Signal | Adjust |
|---|---|
| Inside DCOZ | +12 |
| Residential zoning (R-*) | −15 |
| BZA ≥ 10 within 1 mi | −12 |
| BZA ≥ 5 within 1 mi | −5 |
| Pending cases ≥ 3 within 0.5 mi | −4 |

**Residential proximity (CAMA-derived)** — when available, replaces the generic building-density proxy below:

| Signal | Adjust |
|---|---|
| Residential parcels within 0.5 mi ≥ 100 | −18 |
| Residential parcels within 0.5 mi ≥ 30 | −10 |
| Residential parcels within 0.5 mi ≥ 10 | −4 |
| Zero residentials within 1 mi (truly isolated) | +6 |
| Nearest residential < 500 ft (line of sight) | −8 |
| Nearest residential < 1500 ft | −3 |
| Multifamily units within 1 mi ≥ 500 (urban core, ~22% of parcels) | −10 |
| Multifamily units within 1 mi 150-499 (suburban condo neighborhood, ~36%) | −6 |
| Multifamily units within 1 mi 30-149 (urban fringe, ~10%) | −3 |

**Generic building-density fallback** (only used when residential overlay data missing):

| Signal | Adjust |
|---|---|
| Building density 500 ft ≥ 30 | −8 |
| Building density 500 ft ≥ 10 | −3 |
| Building density 500 ft = 0 (isolated) | +4 |

**Schools + churches** (opposition multipliers — PTA networks + congregations attend PC hearings at higher rates than ordinary homeowners):

| Signal | Adjust |
|---|---|
| Schools within 1 mi ≥ 5 | −14 |
| Schools within 1 mi ≥ 3 | −10 |
| Schools within 1 mi ≥ 1 | −3 |
| Religious sites within 1 mi ≥ 10 | −8 |
| Religious sites within 1 mi ≥ 5 | −5 |
| Religious sites within 1 mi ≥ 2 | −2 |

**Documented opposition** (parsed from SUP staff-report narratives — currently only the Hornbaker case):

| Signal | Adjust |
|---|---|
| Opposition speakers at PC hearing ≥ 4 | −18 |
| Opposition speakers ≥ 2 | −10 |
| Opposition speakers ≥ 1 | −4 |
| Opposition topics ≥ 4 (breadth of concerns) | −4 |

---

## 8. Cooling Cost — base = `cooling_baseline_2026` from LOCA2 CDD (~80 today, fallback 60)

No per-parcel modifiers. Purely countywide. Live LOCA2-derived value
(~80 for PWC 2026 under SSP3-7.0) is used when `climate_baselines.json`
has loaded; constant 60 otherwise.

---

## 9. Development Cost — base 65

| Signal | Adjust |
|---|---|
| RPA | −18 |
| FEMA SFHA | → 12 (floor reset, replaces base) |
| Wetland | −15 |
| Acres < 5 | −10 |
| Acres 10 | −5 |
| Acres 25 | 0 |
| Acres 50 | +4 |
| Acres ≥ 100 | +8 |
| Soil cat IV | −8 |
| Soil cat I | +4 |
| Slope 5% | 0 |
| Slope 8% | −4 |
| Slope 15% | −10 |
| Slope 30% | −15 |
| Easements | −3 |
| Dam-break HIGH hazard | −8 |
| Tree at centroid | −4 |
| Land cover tree / forest | −3 |
| Land cover impervious / pavement | −5 |
| LiDAR elev range 10 ft | 0 |
| Elev range 40 ft | −5 |
| Elev range ≥ 80 ft | −12 |
| Stormwater segments at 2 | −2 |
| Stormwater segments at 5 | −5 |
| Stormwater segments at 20 | −8 |
| Stormwater facility inside parcel ≥ 1 | −6 |

---

## Composite caps (Option B)

After the weighted sum, the lowest applicable cap wins:

| Cap | When |
|---|---|
| 30 | No industrial zoning AND not in DCOZ |
| 38 | Substation ≥ 5 mi AND 230 kV line ≥ 5 mi |
| 35 | ≥ 1 built DC on parcel AND < 20 ac/building (FAR-saturated per PWC I-3 envelope) |

These don't subtract from sub-scores — they're a hard ceiling on the weighted composite (and rendered as a visible amber banner so the analyst sees why).

Saturation threshold of 20 ac/building is derived from PWC's Comprehensive Plan I-3 (Technology/Flex) Floor Area Ratio envelope of ≤ 0.57: a typical 500,000 sq ft hyperscale building consumes 500,000 / 0.57 ≈ 877,000 sq ft ≈ 20.1 acres of lot to stay within the County's density envelope. Source: SUP2025-00016 staff report, Nov 5 2025, p. 13.

---

## Time projection (2026 → 2050)

Five sub-scores decay over time; four are static. Formula:

```
decayed_score = base_score × (1 − decay_rate × years_from_2026 × ssp_multiplier)
```

| Sub-score | Decay rate / yr | Source |
|---|---|---|
| Power Readiness | 0.0085 | PJM queue depth + transmission congestion grow |
| Water Sustainability | 0.0095 (or LOCA2-derived if loaded) | Dry-days trajectory |
| Cooling Cost | 0.0072 (or LOCA2-derived if loaded) | CDD trajectory |
| Time-to-Energization | 0.0090 | Queue density grows |
| Development Cost | 0.0050 | Climate-adaptation premium |
| Regulatory / Environmental / Land / Political | 0 | Static |

SSP scenario multipliers:

| Scenario | Multiplier |
|---|---|
| SSP2-4.5 (moderate) | 0.6 |
| SSP3-7.0 (baseline) | 1.0 |
| SSP5-8.5 (high) | 1.4 |

Right panel renders P10 / P50 / P90 tick marks on the readiness bar — these are the lowest / selected / highest composite across the three SSP scenarios at the current year.

---

## Conviction (data-depth meta-score)

Separate 0–100 score per parcel, measuring how many of the ~30 contributing data layers actually produced signal. Tagged with `✓` (layer contributed) or strikethrough (no data) in the right-panel popover.

A high readiness with low Conviction means "best guess from sparse data — verify before acting." A high readiness with high Conviction means "every layer agrees."

Top-weighted contributors: CAMA owner (8), zoning (8), LRLU (6), nearest substation distance (6), nearest 230 kV line distance (6), soil category (5), active SUP application (5), DCOZ overlay (3), MZP landbay (4), residential overlay (4).

---

## Sensitivity ("What would have to be true")

For each binding sub-score (currently below target 60), the right panel renders a quantified threshold:

> *"For Water to recover from 38 to ≥ 60, countywide PHDI would need to climb from −5.30 to −3.10 by 2032 — roughly 7 years of normal-to-wet precipitation."*

Each threshold is tagged plausibility = **high** (within historical range) / **medium** (achievable with intervention) / **low** (outside historical baseline).

These thresholds are also injected into the counter-memo prompt with `[S#]` markers so the LLM cites the computed lever instead of inventing one.

---

## Quality flags

Every sub-score is tagged with one of three quality flags:

| Flag | Meaning |
|---|---|
| **M** Measured | Primary observational data — direct observation of the thing being scored. (HIFLD substation locations, Federal Land ownership shapefile, PWC zoning districts, parcel acreage, FEMA SFHA boundaries, RPA polygons, soil category from SSURGO, slope from LiDAR mass-points.) |
| **Md** Modeled | Derived from a model or projection — empirically grounded but with an uncertainty band. (LOCA2 climate projections from an 18-GCM ensemble, CDD trajectories, time-to-energization forecasts that combine measured queue data with assumed regulatory cycles.) |
| **I** Inferred | Pattern-extracted from proxies — weakest grounding, used when direct or modeled data is unavailable. (Political risk when no opposition is documented — inferred from BZA density and building density nearby. Development cost when soil/climate data are absent.) |

Per-sub-score rules:

| Sub-score | Quality |
|---|---|
| Power Readiness | M always |
| Regulatory | M if SUP + policy data present, else Md |
| Environmental | M if dam data present, else Md |
| Water | M if `climate_baselines.json` loaded, else Md |
| Land | M if soil + LiDAR present, else Md |
| Political | M if opposition documented, else Md if residential or bldg data, else I |
| Time-to-Energization | Md always |
| Cooling | M if climate loaded, else Md |
| Development Cost | Md if soil + climate present, else I |

---

## How to read a Vira Readiness number

A parcel scores `R = clip(0, 100, weighted_sum_of_sub_scores)`, then capped by Option B if any trigger fires.

Distribution across all 159,181 PWC parcels:

| Range | Count | % | Interpretation |
|---|---|---|---|
| 0–19 | 0 | 0% | (caps prevent anything from dropping below 20) |
| 20–39 | 152,257 | 95.7% | Unsuitable — modal PWC parcel (small residential, no power, no DCOZ) |
| 40–59 | 4,138 | 2.6% | Possible candidate with significant constraints |
| 60–79 | 2,779 | 1.7% | Real candidate — most boxes checked, some friction |
| 80–100 | 7 | 0.0% | Top tier — clear path to development |

The skew is correct, not a calibration error. The "average" PWC parcel is a 1-acre residential lot, not a DC candidate.

---

*This document covers commit `81951d0`. When scoring formulas, weights, or caps change, this doc should change with it. Companion docs: `Overlay_Specification.md` (engineering source-of-truth for every data file's role) and `POLARITY_AUDIT.md` (signal-by-signal polarity rationale).*
