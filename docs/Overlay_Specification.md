# Vira Systems — Overlay Specification

**Companion to the UI Plan** (`~/.claude/plans/while-tahts-running-can-virtual-wall.md`)

**Purpose:** The engineering source-of-truth that maps every data file in the project to its role in the Decision Terminal, the Spatial Map, the Vira Readiness Index, the LLM corpus, and the timeline simulation. When a developer asks *"what do I do with `Soil.geojson`?"* this doc is the answer.

**Scope:** Prince William County only (per the approved MVP scope). Architecture obviously extends to all 92 VA PJM counties, but this spec is calibrated to what's loaded.

---

## How to read this doc

Every data file plays one or more of these roles:

| Role | What it means |
|---|---|
| **MAP** | Renders as a layer on the Spatial Map. Includes geometry style. |
| **TABLE** | Feeds a column in the Decision Terminal parcel intelligence table. |
| **SCORE** | Inputs to one or more of the 9 Vira Readiness Index sub-scores. Comes with a role (`hard-block` / `modifier` / `enabler` / `measurement`) and a quality flag (`M`easured / `Md`odeled / `I`nferred). |
| **LLM** | Chunked into the RAG corpus. The LLM retrieves from these to ground the one-line verdict. |
| **TIMELINE** | Drives forward-state recomputation as the timeline slider moves 2026 → 2050. |
| **JOIN** | Hidden infrastructure — used to spatially join other layers to parcels but doesn't render itself. |
| **CONVICTION** | Counts toward a parcel's data-depth meta-score (the Conviction badge). |

Almost every file has a `JOIN` role on **GPIN** (the universal parcel key) or **spatial intersection** with the Parcel layer. That's how everything ladders up to the single parcel row in the Terminal.

---

## The 9 sub-scores — file inputs and formulas

Each sub-score is computed per parcel as a 0–100 number. Defaults shown; user reweighting in Onboarding Tier 2 changes the composite weight, not the sub-score formula itself.

### 1. Power Readiness (quality: **M**easured)

Inputs:
- `Data Center Intelligence/Virginia_Power_Transmission_Lines_HIFLD.geojson` → distance to nearest 230 kV+ line, dual-feed availability via SUB_1/SUB_2 graph
- `Data Center Intelligence/Virginia_Electric_Substations_HIFLD.geojson` → distance to nearest substation, MAX_VOLT class
- `Data Center Intelligence/High_Voltage_Transmission_Lines.geojson` → named Dominion/NOVEC circuit context (overlays the HIFLD lines)
- `Enviro + Permitting Risk/Data_Center_Buildings.geojson` → distance to nearest operating data center (proxy for "infrastructure rich" zone)
- `Data Center Intelligence/net_metering*.xlsx` → utility-level DER context
- `Data Center Intelligence/non_netmetering*.xlsx` → behind-the-meter generation tracking

Heuristic (MVP):
```
power_readiness = 100 - clamp(d_to_230kV / 5_miles, 0, 1) * 60
                      - clamp(d_to_substation / 2_miles, 0, 1) * 40
                + 10 if dual-feed available else 0
```

Caveat: 30% of HIFLD VA substations have MAX_VOLT = -999999. Fall back to MIN_VOLT, then to LINES count.

### 2. Regulatory Readiness (quality: **mixed M + Md**)

Inputs (the wedge):
- `Enviro + Permitting Risk/Zoning_Districts.geojson` → base entitlement (M-1, M-2, M/T, PBD, PMD, etc.)
- `Enviro + Permitting Risk/Planned_Districts.geojson` → MZP landbay use designation + GFA caps
- `Enviro + Permitting Risk/Data_Center_Opportunity_Zone_Overlay_District.geojson` → **CRITICAL**: inside = by-right, outside = requires SUP (~12 months added)
- `Enviro + Permitting Risk/Use_Permits.geojson` → empirical approval rate + median time for similar zoning conversions
- `Enviro + Permitting Risk/Zoning_Appeals_and_Variances.geojson` → friction signal (variance density)
- `Data Center Intelligence/Planning_Pending_Cases.geojson` → live pipeline density nearby
- `Public and Political/pwc_zoning_ordinance_ch32_excerpts.json` → LLM-grounded answer to "is this use permitted"
- `Public and Political/pwc_compplan_land_use.json` → Long-Range Land Use designation consistency
- `Public and Political/SUP2025-00016.json` → Hornbaker as case-law reference

Heuristic (MVP):
```
if zoning in {'A-1', 'R-*', 'B-2', 'B-3', 'V'}: hard_block = True  # § 32-509.06
base = 100 if inside_DCOZ else 60   # SUP penalty
base -= 5 * variance_density_500ft    # friction
base -= empirical_denial_rate * 30    # historical
```

### 3. Environmental Viability (quality: **M**easured)

Inputs:
- `Enviro + Permitting Risk/Resource_Protection_Areas_(RPA).geojson` → **hard-block** for RPA overlap
- `Enviro + Permitting Risk/Environmental_Resource_Protection_Overlay.geojson` → modifier (Comp Plan ERPO)
- `Enviro + Permitting Risk/Protected_Open_Space.geojson` → **hard-block** for fee-simple/easement-protected
- `Enviro + Permitting Risk/Dam_Break_Inundation.geojson` → modifier (PMF flood zones)
- `Enviro + Permitting Risk/FEMA_Flood_Hazard_Zones_PWC.geojson` → **hard-block** for SFHA (Zone A/AE/VE); pass-through for Zone X
- `Enviro + Permitting Risk/Soil.geojson` → buildability (K-factor + slope + construction category)
- `Enviro + Permitting Risk/Tree_Cover.geojson` + `Land_Cover_2017.geojson` → clearing cost contribution
- `Enviro + Permitting Risk/Hydrological_Features.geojson` + `Stream.geojson` → wetlands + RPA-trigger streams
- `Public and Political/pwc_compplan_environment.json` → LLM context for "Environmental consistency"
- `Public and Political/pwc_compplan_cultural_resources.json` → cultural / historic concerns
- `Public and Political/jlarc_2024_data_centers_full.json` → state-level environmental impact framing

Score:
```
if intersects(RPA, parcel) > 5%: hard_block = True
score = 100
- 30 * (intersects(ERPO) > 25%)
- 100 * (intersects(SFHA) > 10%)   # FEMA Zone A/AE/VE
- 20 * (intersects(Dam_Inundation))
- 20 * (avg_slope > 15%)
- 15 * (tree_cover_pct > 70%)
```

### 4. Water Sustainability (quality: **M + Md**)

Inputs:
- `Natural and Environmental/LOCA2_Ensemble_SSP370_Precipitation_Totals_*.geojson` → forward dry-day projection
- `Natural and Environmental/LOCA2_Ensemble_SSP585_Precipitation_Totals_*.geojson` → high-emissions scenario
- `Natural and Environmental/LOCA2_Ensemble_SSP245_Precipitation_Totals_*.geojson` → moderate scenario
- `Natural and Environmental/PHDI.json` + `PMDI.json` + `PDSI.json` + `Palmer Z-Index.json` → drought trajectory (monthly 1895–present)
- `Natural and Environmental/Manassas Precipitation.json` + `Vienna Precipitation.json` → fine-grained local trend
- `Natural and Environmental/Discharge and Gage Height - Cedar Run Near Catlett, VA.zip` → real-time stream stage
- `Natural and Environmental/Water Depth - 49T 107 Sow 259 - VA087-383951077415001.zip` → groundwater depth trajectory
- `Enviro + Permitting Risk/Watersheds (1).geojson` → which HUC the parcel drains to (jurisdiction)
- `Public and Political/pwc_compplan_environment.json` → policy framing for water restrictions
- `Public and Political/Res No 20-773 Climate Mitigation and Resiliency Goals.json` → renewable mandate context

Score uses the **current PHDI value (-5.0 in PWC, April 2026)** as the modifier — every PHDI point below 0 deducts 10 from the score. Forward-projected via LOCA2 dry-day trend.

### 5. Time-to-Energization (quality: **Md**)

Inputs:
- `Data Center Intelligence/PlanningQueues.xlsx` → PJM interconnection queue depth at nearest substation; **withdrawal rate** (65% in DOM zone) used as risk modifier
- `Data Center Intelligence/Virginia_Electric_Substations_HIFLD.geojson` → substation graph for queue routing
- `Data Center Intelligence/pjm_load_report_full.json` → zonal growth pressure (PJM 2026 forecast Table B-9)
- `Enviro + Permitting Risk/Use_Permits.geojson` → empirical PWC permit-cycle distribution
- `Enviro + Permitting Risk/Planning_Pending_Cases.geojson` → live competition for review staff time
- `Public and Political/pjm_manual_14g_generation_interconnection.json` → LLM-grounded explanation of where the parcel sits in the PJM process
- `Public and Political/pjm_manual_14b_transmission_planning.json` → RTEP context

Score combines:
```
interconnection_months = median(queue_lag at nearest substation) + zone_growth_pressure
regulatory_months = 9 if inside DCOZ else 12   # PWC baseline
withdrawal_risk = withdrawal_rate_at_substation * 25   # penalty
```

### 6. Land + Construction Feasibility (quality: **M**)

Inputs:
- `Enviro + Permitting Risk/Parcel.geojson` → the GPIN spine; size + acreage cutoffs
- `Enviro + Permitting Risk/Parcel_Ownership_Table.geojson` → CAMA tax data, owner outreach
- `Enviro + Permitting Risk/LRLU_Developable_Areas.geojson` → planned-use ceiling (I-2/I-3/I-4 industrial GFA caps)
- `Enviro + Permitting Risk/County_Land.geojson` + `State_Land.geojson` + `Federal_Land.geojson` → **hard-block** ownership
- `Enviro + Permitting Risk/Easements.geojson` + `Stormwater_Segments.geojson` → buildable-footprint constraint (drainage easements eat usable area)
- `Enviro + Permitting Risk/Mass_Points.geojson` → cut/fill volume estimate via LiDAR
- `Enviro + Permitting Risk/Contours_-_Central.geojson` + `Contours_-_Western.geojson` + `Contours_Grid.geojson` → topography for grading-cost modeling
- `Enviro + Permitting Risk/Cultural_Polygons_-_Building_Footprints_and_Paved_Areas.geojson` → competitive density + line-of-sight modeling
- `Enviro + Permitting Risk/Impervious.geojson` (partial, 10%) → pre-development runoff baseline
- `Data Center Intelligence/Culverts.geojson` → drainage infrastructure proximity

### 7. Political / Community Risk (quality: **I**nferred)

Inputs:
- `Enviro + Permitting Risk/Zoning_Appeals_and_Variances.geojson` → historical friction density
- `Data Center Intelligence/Planning_Pending_Cases.geojson` → competitive pressure
- `Public and Political/SUP2025-00016.json` → Hornbaker is the seed case for public opposition signal extraction
- `Public and Political/prince_william_cesmp_full.json` → policy alignment indicator
- `Public and Political/Res No 20-773 Climate Mitigation and Resiliency Goals.json` → political climate context
- `Public and Political/jlarc_2024_data_centers_full.json` → state-level political climate

Inferred from text patterns in SUP staff reports: count of community speakers in opposition, number of PC deferrals, BOCS vote margins. Hornbaker exemplifies what to extract.

### 8. Cooling Cost (quality: **Md**)

Inputs:
- `Natural and Environmental/LOCA2_Ensemble_SSP370_Energy_Indicators_*.geojson` → forward CDD projection
- `Natural and Environmental/Cooling Degree Days.json` → historical CDD baseline (monthly 1895–present)
- `Natural and Environmental/Maximum Temp.json` → peak temperature trajectory
- `Natural and Environmental/Average Temp.json` → mean temperature trend
- `Natural and Environmental/LOCA2_Ensemble_SSP*_Hot_Days_*.geojson` → days >86°F, >95°F, >100°F per decade

Score derived from PUE-adjusted opex projection over 20-year facility life.

### 9. Estimated Development Cost (quality: **Md**)

Inputs:
- `Enviro + Permitting Risk/Soil.geojson` → grading multiplier (K-factor + construction category)
- `Enviro + Permitting Risk/Tree_Cover.geojson` + `Land_Cover_2017.geojson` → clearing cost ($/acre)
- `Enviro + Permitting Risk/Easements.geojson` + `Resource_Protection_Areas_(RPA).geojson` → engineering complexity premium
- `Enviro + Permitting Risk/Mass_Points.geojson` → cut/fill volume → grading cost
- `Data Center Intelligence/da_hrl_lmps.csv` → opex basis for amortization
- `Data Center Intelligence/hrl_load_metered.csv` → actual-vs-forecast load delta (signals if PJM forecast is optimistic)

---

## The Conviction score (meta-score, quality: **M**)

Counts data depth per parcel. Range 0–100.

```
conviction = (
    20 * (parcel_has_CAMA_owner_data)
  + 15 * (zoning_district_with_proffer_text)
  + 10 * (within_DCOZ or has_TeOD_subdistrict_assignment)
  + 10 * (has_LRLU_designation)
  + 10 * (has_LiDAR_coverage)   # always true for PWC
  +  5 * (has_FEMA_classification)
  +  5 * (has_soil_data)
  +  5 * (has_RPA_classification)
  +  5 * (any_pending_planning_case_within_500ft)
  +  5 * (transmission_line_within_1mi)
  + 10 * (substation_within_5mi)
  -  5 * (any_layer_with_stale_last_edit > 5_years)
)
```

Visible as a small dot beside every Readiness Index. Click → gap list. This is the **honest-broker** feature — tells the analyst exactly what we know about this parcel and where we're guessing.

---

## Map render z-order (bottom → top)

The order layers stack on Mapbox. Default opacity in parens.

1. **Mapbox satellite or light basemap** (100%)
2. `Land_Cover_2017.geojson` (15%) — only when "Climate / Environmental" macro group is active
3. `Soil.geojson` (15%) — same
4. `Watersheds (1).geojson` (10%) — outlines only
5. `Stream.geojson` + `Hydrological_Features.geojson` (60%) — blue
6. **FEMA_Flood_Hazard_Zones_PWC.geojson** (40%) — light blue for Zone X, **red 60%** for SFHA (A/AE/VE)
7. `Dam_Break_Inundation.geojson` (50%) — dark red, hatched
8. `Tree_Cover.geojson` (25%) — only when zoomed in past 14
9. `Resource_Protection_Areas_(RPA).geojson` (40%) — green hatch
10. `Environmental_Resource_Protection_Overlay.geojson` (30%) — green diagonal
11. `Protected_Open_Space.geojson` (45%) — solid green by ProtectedStatusType
12. `Federal_Land.geojson` + `State_Land.geojson` + `County_Land.geojson` (40%) — cross-hatched
13. `Easements.geojson` (35%) — yellow hatched, hidden by default
14. **Parcel.geojson** (50% outline, transparent fill) — always visible above zoom 12
15. `LRLU_Developable_Areas.geojson` (30%) — categorical fill by LRLU code
16. `Planned_Districts.geojson` (30%) — textured fill where MZP applies
17. `Zoning_Districts.geojson` (35%) — categorical fill by ZoningDistrict
18. `Zoning_Appeals_and_Variances.geojson` (40%) — heatmap, hidden by default
19. **Data_Center_Opportunity_Zone_Overlay_District.geojson** (35%) — bold purple diagonal hatch
20. `Use_Permits.geojson` (40%) — filtered to data-center-eligible, dotted outline
21. `Planning_Pending_Cases.geojson` (50%) — orange outline
22. `Stormwater_Facilities.geojson` (50%) — small blue dots, zoom > 15
23. `Cultural_Polygons_-_Building_Footprints_and_Paved_Areas.geojson` (30%) — gray fill, only when "competitive density" preset active
24. `Data_Center_Projects.geojson` (60%) — categorical by ProjectStatus (Built / Under Construction / Planned / Pending)
25. **Data_Center_Buildings.geojson** (75%) — operator-color-coded points
26. `Power_Lines_(150kv_and_higher).geojson` (60%) — thin gold lines (geometry only)
27. `Virginia_Power_Transmission_Lines_HIFLD.geojson` (70%) — gold lines weighted by VOLT_CLASS (500 kV thickest)
28. **Virginia_Electric_Substations_HIFLD.geojson** (85%) — gold squares sized by MAX_VOLT
29. `High_Voltage_Transmission_Lines.geojson` (75%) — labeled circuit names from PWC GIS
30. **Selected parcel highlight** (100%) — bright orange outline, 3px
31. **PJM Withdrawn Project heatmap** (toggleable; 50%) — generated from `PlanningQueues.xlsx` filtered to Withdrawn=Y; red density

`Mass_Points.geojson`, `Contours_*.geojson`, `Control_Points.geojson` — **NOT** rendered directly. Used in preprocessing only to compute slope, cut/fill, and grading rasters that feed sub-scores.

`Stormwater_Management_Structures.geojson` (80k points), `Stormwater_Segments.geojson` (83k lines), `Culverts.geojson` (51k points) — **JOIN-only**. Used to compute EasementWidth + drainage adjacency per parcel. Not rendered (would clutter the map).

`Control_Points.geojson` — JOIN-only, for georeferencing verification.

---

## Smart presets (3 one-click filters)

Per the UI plan's "Floating top-right control":

### `Hard blockers only`
Show: `Federal_Land` + `State_Land` + `County_Land` + `Resource_Protection_Areas_(RPA)` + `Environmental_Resource_Protection_Overlay` + `Protected_Open_Space` (ProtectedStatusType in {Fee Simple, Conservation Easement, Historic Easement}) + `Dam_Break_Inundation` + FEMA SFHA polygons + `Soil` where SlopePercentage > 15%.
Hide everything else.
Recolor parcels: any parcel that intersects any of these > 5% turns red. Others stay neutral.

### `Power-ready only`
Show: `Virginia_Power_Transmission_Lines_HIFLD` filtered to VOLT_CLASS ≥ 220 + `Virginia_Electric_Substations_HIFLD` filtered to MAX_VOLT ≥ 230 + 1-mile buffer rings.
Hide everything else.
Recolor parcels: green if within 1 mile of a 230 kV+ line AND within 5 miles of a 230 kV+ substation. Otherwise gray.

### `Politically warm`
Show: `Data_Center_Opportunity_Zone_Overlay_District` (the gold standard) + `Use_Permits` filtered to data-center-related approved cases + `Data_Center_Projects` (Built or Under Construction).
Hide: `Zoning_Appeals_and_Variances` clustered as warning heatmap, but with lower opacity.
Recolor parcels: green inside DCOZ AND outside high-BZA-density clusters; red outside DCOZ AND inside BZA hot zones.

---

## LLM RAG corpus assembly recipe

The RAG pipeline indexes the **22 policy JSONs** in `Public and Political/` plus structured per-parcel cards generated from the spatial layers.

### Document corpus chunking (Day 5 of the build sequence)

```python
chunk_size = 500  # tokens, with 100-token overlap
embedding_model = "BAAI/bge-small-en-v1.5"
reranker = "bge-reranker-base"
vector_store = "ChromaDB (local file)"
```

Each policy JSON's `pages[]` or `sections[]` array is iterated. Each page/section becomes one or more chunks (depending on length), tagged with:
- `doc_id`: filename
- `doc_title`: from JSON metadata
- `section_id`: from sections array (e.g., "Sec. 32-509.02") if present
- `page_number`: from pages array if present
- `chunk_idx`: ordinal within doc

### Parcel "structured record cards" (Day 4 of build)

For each of the 10 demo parcels (and on-demand for any parcel a user clicks), generate a synthetic markdown record:

```markdown
# Parcel {GPIN}

## Identification
- GPIN: ...
- Address: {StreetNumber} {StreetName} {StreetType}, {City} {ZipCode}
- Acreage: ...
- Magisterial District: ...

## Ownership (from CAMA)
- Current Owner: {CAMA_OWNER_CUR}
- Mailing Address: ...
- Use Code: {CAMA_USECODE}

## Zoning & Land Use
- Base Zoning: {ZoningDistrict} (Case {ZoningCaseNumber})
- Has Proffers: {PROFFERS}
- LRLU Designation: {LRLU} ({SpecialPlanningAreaName})
- Inside DCOZ Overlay: {DCOOD}
- Inside TeOD: {if applicable, with subdistrict}
- Inside Airport Safety Overlay: {if applicable, with zone APA/APH/APC/APT}

## Environmental Profile
- RPA Intersect: {pct}
- FEMA SFHA: {Zone}
- Predominant Soil: {SoilMapUnitName}
- Slope: {avg, max}
- Tree Cover: {pct}

## Power Infrastructure
- Nearest 230 kV+ Line: {Name} ({Owner}), {distance} miles
- Nearest Substation: {Name}, MAX_VOLT={MAX_VOLT} kV, {distance} miles
- Dual-feed Available: {boolean}

## Regulatory History
- Use Permits within parcel boundary: {list}
- BZA cases on parcel: {list}
- Active Planning Pending Cases within 500ft: {list}

## Comparable Cases
- 3 most similar Data_Center_Projects by zoning + size: {list with status + acreage + GFA}
```

This card is **also** indexed in ChromaDB alongside the policy chunks. When the LLM gets a question about a parcel, retrieval pulls both:
- (a) policy chunks relevant to the question
- (b) the parcel's record card

### Retrieval prompt template

```
You are Vira's diligence assistant. Use only the provided sources. If you cannot cite a source for a claim, omit the claim. Every claim must reference [source_id]. Format the memo as a planner would, with these sections in order:
1. Site location & overview
2. Zoning context
3. Overlay districts
4. Surrounding land use
5. Comprehensive Plan consistency
6. Staff concerns (mirror PWC SUP staff-report patterns)
7. Community considerations
8. Sustainability commitments precedent
9. Recommendation

[parcel_card]
{the markdown card}

[retrieved_policy_chunks]
{top 8 chunks from ChromaDB}

[user_question]
{parcel-grounded query, e.g. "Generate diligence memo"}
```

### Adversarial counter-memo

Identical retrieval, prompt flipped:

```
You are Vira's adversarial reviewer. Argue why this parcel is a BAD investment, citing only the same sources. List the strongest 3-5 risks.
```

---

## Timeline simulation (2026 → 2050)

Five sub-scores are time-varying. The slider's current year drives:

| Sub-score | Time-varying input | File |
|---|---|---|
| Power Readiness | Queue depth + LMP basis | `PlanningQueues.xlsx` (extrapolated) + `da_hrl_lmps.csv` |
| Water Sustainability | LOCA2 dry-day projection + PHDI trend | LOCA2 GeoJSONs + Palmer JSONs |
| Cooling Cost | LOCA2 CDD projection | `LOCA2_Ensemble_SSP*_Energy_Indicators_*.geojson` + CDD.json |
| Time-to-Energization | Forward queue density | `PlanningQueues.xlsx` |
| Estimated Development Cost | LMP forward + climate-adjusted | DA LMPs + LOCA2 |

Three SSP scenarios available (user toggle): SSP2-4.5 (moderate), SSP3-7.0 (baseline), SSP5-8.5 (high). Default: SSP3-7.0.

Forward projections show **P10 / P50 / P90 bands** with source citation on hover (e.g., "LOCA2 ensemble, SSP3-7.0, n=18 GCMs").

---

## Master file table

Every file in the project, with its UI role.

### `Data Center Intelligence/`

| File | MAP | TABLE | SCORE | LLM | TIMELINE | Notes |
|---|---|---|---|---|---|---|
| `Virginia_Power_Transmission_Lines_HIFLD.geojson` | ✅ gold by VOLT_CLASS | "Power Readiness" col | **Power Readiness** (M, enabler) | ❌ | ❌ | SUB_1/SUB_2 graph for dual-feed |
| `Virginia_Electric_Substations_HIFLD.geojson` | ✅ gold squares by MAX_VOLT | distance metric | **Power Readiness** (M, enabler) | ❌ | ❌ | 30% missing MAX_VOLT; fallback chain |
| `High_Voltage_Transmission_Lines.geojson` | ✅ thin labeled lines | ❌ | Power Readiness (M, enabler) | ❌ | ❌ | PWC GIS, has circuit names |
| `Power_Lines_(150kv_and_higher).geojson` | hidden by default | ❌ | redundant w/ HIFLD | ❌ | ❌ | Geometry-only backup |
| `Data_Center_Buildings.geojson` | ✅ operator-color points | ❌ | Power Readiness (M, modifier) + Market Activity | ❌ | ❌ | 122M sq ft approved vs 23M permitted gap |
| `Data_Center_Projects.geojson` (also in Enviro folder) | ✅ status-colored polygons | "Adjacent operators" | Market Activity (M) | ❌ | ❌ | 51 campuses |
| `Planning_Pending_Cases.geojson` | ✅ orange outlines | "Live pipeline within 500ft" | Regulatory (M, modifier) + Time-to-Energization (M, modifier) + Political (I) | ✅ via StaffReportLink scrape | ❌ | 145 active cases |
| `Culverts.geojson` | hidden | ❌ | Construction Feasibility (M, modifier) | ❌ | ❌ | JOIN-only |
| `PlanningQueues.xlsx` | ⚙️ derives **Withdrawn heatmap** layer | "Queue position", "Queue lag" | **Time-to-Energization** (Md) + Power Readiness | ❌ | ✅ extrapolate forward | 9,251 records, 65% DOM withdrawal |
| `da_hrl_lmps.csv` | ❌ | "Recent LMP $/MWh" | **Estimated Dev Cost** (Md) + Power Cost | ❌ | ✅ forward project | 345k DA hourly |
| `hrl_load_metered.csv` | ❌ | ❌ | Validates PJM forecast | ❌ | ✅ | Actual vs forecast delta |
| `inst_load (1).csv` | ❌ | ❌ | Validation only | ❌ | ❌ | 50-row snapshot |
| `net_metering*.xlsx` (6 years) | ❌ | "DER capacity in utility" | Power Readiness (M, context) | ❌ | ✅ time series | EIA 861M |
| `non_netmetering*.xlsx` (4 years) | ❌ | "Behind-meter capacity" | Power Readiness (M, context) | ❌ | ✅ time series | EIA 861M |
| `pjm_load_report_full.json` | ❌ | "Zonal load forecast" | Time-to-Energization (Md, modifier) | ✅ chunked | ✅ source for trajectory | PJM 2026 forecast |

### `Enviro + Permitting Risk/`

| File | MAP | TABLE | SCORE | LLM | TIMELINE | Notes |
|---|---|---|---|---|---|---|
| `Parcel.geojson` | ✅ outline @ zoom>12 | row spine | foundational JOIN key | ❌ | ❌ | GPIN universal key, 159k features |
| `Parcel_Ownership_Table.geojson` | ❌ (same geom as Parcel) | "Owner", "Use Code", "Deed Inst" | Construction Feasibility (M) + Outreach | ❌ | ❌ | CAMA tax data |
| `Zoning_Districts.geojson` | ✅ categorical fill | "Zoning", "Has Proffers" | **Regulatory Readiness** (M, enabler) | ❌ | ❌ | 2,208 cases |
| `Planned_Districts.geojson` | ✅ textured fill | "MZP landbay", "GFA cap" | **Regulatory Readiness** (M, enabler) | ❌ | ❌ | 1,151 MZP landbays |
| `Zoning_Appeals_and_Variances.geojson` | ✅ heatmap, off-default | "BZA density 500ft" | Regulatory (M, modifier) + Political (I) | ❌ | ❌ | Friction signal |
| `Use_Permits.geojson` | ✅ dotted outlines | "Historical SUPs" | **Regulatory Readiness** (M) + Time-to-Energization | ❌ | ❌ | 5,654 historical SUPs |
| `Planning_Pending_Cases.geojson` (also Data Center folder) | (see above) | (see above) | (see above) | ✅ | ❌ | Same file |
| `LRLU_Developable_Areas.geojson` | ✅ categorical fill | "LRLU code", "Remaining GFA" | **Land Feasibility** (M, ceiling) + Regulatory | ❌ | ❌ | 753 polygons, 56 undeveloped industrial |
| `Data_Center_Opportunity_Zone_Overlay_District.geojson` | ✅ **bold purple diagonal hatch** | "Inside DCOZ" | **Regulatory Readiness** (M, the wedge field) | ❌ | ❌ | The decisive overlay |
| `Data_Center_Projects.geojson` | (see above) | (see above) | Market Activity (M) | ❌ | ❌ | Same |
| `Data_Center_Buildings.geojson` | (see above) | (see above) | (see above) | ❌ | ❌ | Same |
| `Resource_Protection_Areas_(RPA).geojson` | ✅ green hatch | "RPA intersect %" | **Environmental Viability** (M, hard-block) | ❌ | ❌ | 2,747 CBPA polygons |
| `Environmental_Resource_Protection_Overlay.geojson` | ✅ green diagonal | "ERPO intersect %" | Environmental Viability (M, modifier) | ❌ | ❌ | 10 watersheds, 45,506 ac |
| `Protected_Open_Space.geojson` | ✅ green solid by type | "Conservation status" | **Environmental Viability** (M, hard-block for fee-simple) | ❌ | ❌ | 1,772 polygons |
| `FEMA_Flood_Hazard_Zones_PWC.geojson` | ✅ blue X / red SFHA | "FEMA Zone" | **Environmental Viability** (M, hard-block for A/AE/VE) | ❌ | ❌ | 3,038 polygons, 49% SFHA |
| `Dam_Break_Inundation.geojson` | ✅ red 50% hatched | "PMF flag" | Environmental Viability (M, modifier) | ❌ | ❌ | 28 high-hazard dams |
| `Federal_Land.geojson` | ✅ cross-hatched | "Federal ownership" | **Land Feasibility** (M, hard-block) | ❌ | ❌ | 212, ~16,447 ac (PW Forest Park + Quantico) |
| `State_Land.geojson` | ✅ cross-hatched | "State ownership" | **Land Feasibility** (M, hard-block) | ❌ | ❌ | 197 features |
| `County_Land.geojson` | ✅ cross-hatched | "County ownership" | **Land Feasibility** (M, hard-block) | ❌ | ❌ | 908 features incl. Service Authority |
| `Easements.geojson` | ✅ yellow hatch, off-default | "Easement intersect" | Construction Feasibility (M, modifier) | ❌ | ❌ | 2,894 polygons, only 20% w/ deed ref |
| `Soil.geojson` | ✅ low-opacity color | "Hydrologic Group" | **Land Feasibility** (M, modifier) + Dev Cost | ❌ | ❌ | 20,587 SSURGO units |
| `Tree_Cover.geojson` | ✅ green @ zoom>14 | "% canopy" | Environmental + Dev Cost (M, modifier) | ❌ | ❌ | 71,807 polygons |
| `Land_Cover_2017.geojson` (85%) | ✅ 5-class low-opacity fill | "Predominant class" | Environmental + Dev Cost (M, modifier) | ❌ | ❌ | 252k of 298k features |
| `Stream.geojson` | ✅ blue lines | "Stream within 100ft" | Environmental (M, RPA trigger) | ❌ | ❌ | 107,424 lines |
| `Hydrological_Features.geojson` | ✅ blue fill | "Wetlands intersect" | Environmental (M, RPA trigger) | ❌ | ❌ | 3,979 polygons |
| `Watersheds (1).geojson` | ✅ outlines | "HUC name" | Water Sustainability (M, jurisdiction) | ❌ | ❌ | 222 sub-areas |
| `Stormwater_Facilities.geojson` | ✅ blue dots @ zoom>15 | "SWM adjacency" | Construction Feasibility (M, modifier) | ❌ | ❌ | 2,510 SWMPs |
| `Stormwater_Management_Structures.geojson` | hidden | ❌ | JOIN-only for drainage adjacency | ❌ | ❌ | 80,673 points |
| `Stormwater_Segments.geojson` | hidden | ❌ | JOIN-only for EasementWidth | ❌ | ❌ | 83,673 pipes |
| `Cultural_Polygons_-_Building_Footprints_and_Paved_Areas.geojson` | ✅ gray, preset-only | "Adjacent building density" | Construction + Political (M, modifier) | ❌ | ❌ | 197,628 footprints w/ height |
| `Mass_Points.geojson` | preprocessing only | "Cut/fill volume" | Construction Feasibility (M, modifier) | ❌ | ❌ | 818k LiDAR — convert to DEM |
| `Contours_-_Central.geojson` + `Contours_-_Western.geojson` + `Contours_Grid.geojson` | preprocessing only | "Slope" | Construction Feasibility + Environmental | ❌ | ❌ | Derive 2-ft DEM |
| `Control_Points.geojson` | ❌ | ❌ | Georeferencing verification | ❌ | ❌ | Hidden infrastructure |
| `Impervious.geojson` (10% partial) | ❌ | "% impervious" | Environmental + Dev Cost (M, modifier) | ❌ | ❌ | Weak sample, use with caveats |
| `FY2026 Fee Schedule Special Use Permits.pdf` | ❌ | "Estimated SUP fees" | Regulatory Readiness (M, modifier) | ✅ chunk for memo "fees" | ❌ | Already archived |

### `Natural and Environmental/`

| File | MAP | TABLE | SCORE | LLM | TIMELINE | Notes |
|---|---|---|---|---|---|---|
| `LOCA2_Ensemble_SSP370_Precipitation_Totals_*.geojson` | choropleth (slider-driven) | "2046 dry days" | **Water Sustainability** (Md) | ❌ | ✅ | Baseline scenario |
| `LOCA2_Ensemble_SSP370_Temperature_Variables_*.geojson` | choropleth | "2046 avg max temp" | Cooling Cost (Md) | ❌ | ✅ | |
| `LOCA2_Ensemble_SSP370_Hot_Days_*.geojson` | choropleth | "Days >95°F by 2046" | Cooling Cost (Md) | ❌ | ✅ | |
| `LOCA2_Ensemble_SSP370_Energy_Indicators_*.geojson` | choropleth | "CDD by decade" | **Cooling Cost** (Md) | ❌ | ✅ | |
| `LOCA2_Ensemble_SSP245_*` (3 chapters) | scenario toggle | (parallel) | (parallel) | ❌ | ✅ | Moderate scenario |
| `LOCA2_Ensemble_SSP585_Precipitation_Totals_*.geojson` | scenario toggle | (parallel) | (parallel) | ❌ | ✅ | High scenario |
| `PHDI.json` | ❌ | "Current PHDI" | **Water Sustainability** (M, modifier) | ❌ | ✅ historical baseline | Monthly 1895–2026 |
| `PMDI.json`, `PDSI.json`, `Palmer Z-Index.json` | ❌ | drought variants | Water Sustainability (M) | ❌ | ✅ | |
| `Cooling Degree Days.json`, `Heating Degree Days.json` | ❌ | "CDD historical" | Cooling Cost (M, baseline) | ❌ | ✅ | |
| `Maximum Temp.json`, `Minimum Temp.json`, `Average Temp.json` | ❌ | "Avg temp baseline" | Cooling Cost (M) + Water (M) | ❌ | ✅ | |
| `Precipitation.json` | ❌ | "Precip baseline" | Water Sustainability (M) | ❌ | ✅ | |
| `Manassas Precipitation.json`, `Manassas Snowfall.json` | ❌ | ❌ | Water Sustainability (M, hyperlocal) | ❌ | ❌ | Local station |
| `VIENNA, VA US *.json` (4 files) | ❌ | ❌ | Water Sustainability + Cooling (M) | ❌ | ❌ | Long historical series 1925+ |
| `Discharge and Gage Height - Cedar Run Near Catlett, VA.zip` | ❌ | "Cedar Run stage" | Water Sustainability (M) | ❌ | ✅ real-time | USGS gage |
| `Water Depth - 49T 107 Sow 259 - VA087-383951077415001.zip` | ❌ | "Groundwater depth" | Water Sustainability (M) | ❌ | ✅ real-time | VA DEQ well |

### `Public and Political/` (LLM corpus — none renders on the map)

| File | LLM chunk role | Demo memo section it grounds |
|---|---|---|
| `prince_william_cesmp_full.json` | County sustainability strategy | Sustainability commitments precedent + policy alignment |
| `Reference Manual for Rezoning, SUP, Proffer Amendment Applications.json` | Procedural backbone | Time-to-Energization explanation + procedural delay |
| `pwc_zoning_ordinance_ch32_excerpts.json` | The wedge — DCOZ + TeOD + Article VII + Airport Safety | Zoning context + Overlay districts + every memo answer to "is this permitted" |
| `SUP2025-00016.json` | The anchor case file (Hornbaker) | Mirror its structure when generating any new memo |
| `PP213.json` | Building permit phasing | Construction phasing + occupancy guidance |
| `PP-NewStructure-DataCenterBuildings.json` | Commercial DC building procedures | Same as above |
| `PP-AddressValidationRequirements.json` | Address validation gating | Procedural step in workflow |
| `FY2026 Application Package for Special Use Permits.pdf.json` | SUP application requirements + fees | Estimated SUP fees + submission requirements |
| `Res No 20-773 Climate Mitigation and Resiliency Goals.json` | 2050 carbon neutrality goals | Policy alignment language + sustainability proffer context |
| `pwc_compplan_community_design.json` | Community Design chapter | Memo section: "Compliance with Community Design Plan" |
| `pwc_compplan_technology_connectivity.json` | Tech infrastructure chapter | Fiber + technology infrastructure references |
| `pwc_compplan_electrical_utility_service.json` | Electrical utility plan | Power readiness narrative + utility coordination |
| `pwc_compplan_open_space.json` | Open Space chapter | Open space requirements + buffer planning |
| `pwc_compplan_environment.json` | Environment chapter | Memo section: "Environmental Plan consistency" |
| `pwc_compplan_cultural_resources.json` | Cultural Resources plan | Cultural/historic concerns (Phase I/II) |
| `pwc_compplan_land_use.json` | Long-Range Land Use plan (most-cited) | LRLU consistency, I-3/I-4 designation context |
| `va_clean_economy_act_hb1526_2020.json` | State statute (VCEA) | Renewable procurement context for sustainability commitments |
| `pjm_manual_14b_transmission_planning.json` | RTEP process | Time-to-Energization narrative |
| `pjm_manual_14g_generation_interconnection.json` | Interconnection request process | Queue position explanation |
| `pjm_manual_14h_new_service_request_cycle.json` | Cluster cycle | Cluster timing explanation |
| `jlarc_2024_data_centers_full.json` | State analysis (Dec 2024) | Macro framing — load growth, NoVa share |
| `jlarc_2024_data_centers_summary.json` | JLARC executive summary | 1-pager citations |

---

## What this spec deliberately excludes

- **No file in `Public and Political/` renders on the map.** That folder is purely the LLM corpus.
- **No Mass_Points / Contours / Control_Points / Stormwater_Structures rendering.** Those are preprocessing inputs — they generate derived layers (DEM, slope, drainage adjacency) that *are* used, but the raw files would crush the map UI.
- **No live PJM ISO data refresh in MVP.** `inst_load`, `da_hrl_lmps`, `hrl_load_metered` are snapshots; the production version refreshes daily, but for the demo they're static.
- ⚠️ **NO LMP DATA IS PRESENT — added 2 Aug 2026.** `da_hrl_lmps.csv` has never existed in this repo, nor has the `Data Center Intelligence/` folder. The only LMP file that ever landed here, `data/water_raw/rt_hrl_lmps.csv`, was a corrupt 15-byte `[object Object]` stub and was deleted. Re-fetch is blocked: PJM Data Miner 2 returns **401** without an `Ocp-Apim-Subscription-Key`, which this project does not have. **Every LMP-dependent claim in this spec is therefore unbacked and must be re-scoped before use** — the "Recent LMP $/MWh" table column; the `da_hrl_lmps` input to **Estimated Development Cost** (§9, opex basis for amortization); the "LMP basis" half of **Power Readiness**; and the "LMP forward" rows of the timeline simulation. Note this spec describes the Vira Systems Decision Terminal, a wider scope than the water atlas actually built; nothing shipped reads LMPs.
- **No comp transaction prices.** Deed instruments + dates exist in `Parcel_Ownership_Table.geojson` but $ amounts don't. Land Cost sub-score for v1.5.
- **No fiber routes.** Post-MVP.

---

## Build-order implication

Following this spec, the engineering work decomposes into:

1. **Data prep (Day 1-2):**
   - Convert all map-rendered GeoJSONs to vector tiles via tippecanoe.
   - Run preprocessing on Mass_Points / Contours to generate a 2-ft DEM raster + slope raster.
   - Pre-compute the 10 demo parcels' record cards (markdown).
   - Run pre-compute readiness scores for the 10 demo parcels (no live JOINs).

2. **RAG pipeline (Day 5):**
   - Chunk all 22 Public-and-Political JSONs into ChromaDB.
   - Append per-parcel record cards as additional chunks.
   - Build retrieval prompt template + adversarial prompt template.

3. **Frontend (Day 2-4):**
   - Next.js scaffold + Tailwind + Mapbox GL + Zustand state.
   - Render layers in the z-order above; smart presets as one-click filters.
   - Toggle between Terminal and Map views with shared state.

4. **Wire it together (Day 6):**
   - Terminal table row click → expand right panel → call LLM → render memo + adversarial counter-memo.
   - Map parcel click → highlight + auto-toggle relevant layers + sync to Terminal.
   - Timeline slider → recompute the 5 time-varying sub-scores from LOCA2 + PJM Queue + Palmer.

5. **Polish + Vercel deploy (Day 7).**

---

## Open items for the founder

1. **Confirm the demo anchor.** Hornbaker is exemplary friction but also a live case. If you'd rather demo against a completed campus (e.g., Compass Datacenters PWC = 884 acres, 11.5M sq ft planned, status=Planned), the spec doesn't change — just the seeded record card.
2. **Approve the SSP3-7.0 baseline scenario** vs SSP2-4.5 vs SSP5-8.5 as default for the timeline slider.
3. **Confirm Llama 3.1 8B for the RAG memo.** Open-source, runs locally via Ollama; aligns with the plan's "no API calls" constraint.
