# Full re-audit of the 81 raw datasets — line-by-line

Prompted because earlier passes leaned on keyword search and skimming and missed
material. This is the complete read-through: every file parsed in full (records
enumerated with code, not eyeballed; documents read whole). Findings that are
NEW (not currently used by the model) or that CORRECT something are flagged.

Legend: 🔴 correction to current model · 🟡 unused data worth using · 🟢 confirms
existing · ⚪ context/no action.

---

## A. Policy / permit / document JSONs

### Prince_William_Water_FAQ_Extract.csv 🟡🔴
The utility's own words. Material facts the model under-uses:
- **"2025: data centers consumed ~3.8% of average daily demand and 10.1% of maximum daily demand"** in the PWW service area. This is a *2025* utility statement and a direct peak-to-average signal (10.1/3.8 = **2.7× on a demand-share basis**). The model currently anchors to a 2023 "0.42 MGD" figure and derives peak from the 3,060/309 = 9.9× intensity ratio — these are different framings and should be reconciled; the utility's own 2.7× demand-share peaking is a citable cross-check.
- Water **reuse studied for Digital Gateway, "found not currently viable there, but possible elsewhere"** — bears on the reclaimed-water discussion (§18.4).
- Supply chain: West = Fairfax Water Corbalis (Potomac) + wastewater→UOSA→Occoquan Reservoir; East = Griffith WTP (Occoquan Reservoir). Public supply is Potomac River + Lake Manassas, **not groundwater** — so the data centers do not draw down private wells (answers a common objection).
- Planning horizon MWCOG **2045**; "growth pays for growth" (developers fund capacity).

### PP-NewStructure-DataCenterBuildings.json 🟡🔴
County building-permit policy (eff. 2021-04-05). Two things that matter to the model:
- **County's own definition of a data center building requires "at least one megawatt of capacity"** (def. 3C) — a floor, useful for filtering.
- **Shell-first permitting:** a new data center is permitted as ONE building permit / ONE CO, with unused areas built to Storage (S-1) / Business (B) use groups and **"fit-out" later** via Alteration/Repair permits. So **gross floor area is decoupled in time from eventual IT MW** — the shell exists at full GFA before the data halls (and their load) are fitted out. This is a concrete mechanism behind the density (sqft/MW) uncertainty and the convexity in §17: a planned/new building's GFA can precede its MW by years. Should be cited in §15.

### Res No 20-773 Climate Mitigation and Resiliency Goals.json 🟡
BOCS resolution (2020-11-17, passed 5–3). Directs Comprehensive Plan goals of
**100% of the county's electricity from renewable sources by 2035**, county
government ops 100% renewable by 2030, carbon neutral by 2050. Direct tension
with the data-center gas buildout and useful context for market-based Scope 2
(§14.2) and the CEMP.

### pjm_load_report_full.json ⚪🟡
PJM 2026 Load Forecast (Jan 2026). **The DOM (Dominion Virginia Power) zone
forecast is explicitly adjusted for "growth in data center load and a voltage
optimization program."** PJM RTO summer peak +3.6%/yr (10-yr), net energy
+5.3%/yr — data-center-driven. Detailed DOM numbers live in the companion Excel,
not this text. Context for the marginal-dispatch argument (§16): the whole zone
is being reshaped by this load.

### README.txt ⚪
Describes observations-759582.csv only (iNaturalist research-grade species obs,
place_id 744, taxon 20978, 2020–2026). Biodiversity, not water.

---

## B. Climate / drought time series — 🔴🟡 THE BIGGEST MISS

I never opened these. They are NOAA monthly county series (1895→2026-04, 1,576
months) plus daily station series. They carry the water-STRESS context the whole
paper was missing.

### Drought (PDSI / PHDI / PMDI / Palmer_Z .json) 🟡🔴 — headline material
Prince William County is in **near-record extreme drought right now**:
- **PDSI = PHDI = PMDI = −5.3 (April 2026)** — the current reading is in the
  **bottom 0.9% of all 1,576 months since 1895** (min ever −6.96). Palmer-Z −3.0
  (bottom 4%). PDSI below −4 is "extreme drought" by definition.
- The data centers' consumptive demand is landing during one of the **driest
  periods in 130 years**. This is the water-stress hook the AGU framing needs and
  the estimator/METHODOLOGY never mentioned it.

### Cooling Degree Days (Cooling Degree Days.json) 🟡🔴
- **CDD has risen ~35% over the record**: 20th-century decades ~900–1,150; **2010s
  = 1,371, 2020s = 1,364**. Data-center evaporative cooling load (Scope 1) is
  structurally increasing with warming, and the model's single fixed CDD (1,323)
  is slightly low vs the recent decadal mean (~1,365).
- **Seasonality: 80% of annual CDD falls in Jun–Sep** (Jul 33%, Aug 28%, Jun 20%,
  Sep 12%). This is the seasonal shape for a Scope 1 seasonal model — and it
  coincides exactly with summer low-flow and the drought. The 9.9× peak day
  (§12) lands in Jul/Aug when the basin is most stressed.

### Precipitation (Precipitation.json, Manassas) 🟡
- Last 12 months = **34.4 in vs 40.5 in long-run mean (−15%, −6.1 in)** —
  corroborates the drought independently.

### The convergence (this is the argument)
Rising cooling demand (CDD +35%) × concentrated in summer (80% Jun–Sep) × during
99th-percentile drought (PDSI −5.3) × consumed mostly out-of-basin (§13). Four
independent series point the same way. **None of this is in the model today.**

### Station daily series (Manassas US1VAPW0022 2020–26; Vienna USC00448737 1925–2026)
Daily PRCP/SNOW/SNWD (+ TMAX/TMIN for Vienna, 100 yr). Enables daily extreme-heat
peak-day analysis. ⚪ Data-hygiene: the 3 "VIENNA_VA_US_*" files are **byte-identical**
(all hold SNOW/PRCP/SNWD/TMAX/TMIN); the 2 "Manassas *" files likewise. And
meta.location has lat/long **swapped** (latitude −77.x is really longitude).

---

## C. Water permits & discharge (EPA ECHO / ICIS) — 🔴 the "0 NPDES" headline was too crude

I had reduced this to "0 of 243 hold NPDES." Reading the files fully shows a
sharper, better-evidenced, and partly *contradictory* picture.

### NPDES_NAICS_DATACENTER.csv (40 rows) 🔴
National list of NPDES permits tagged NAICS 518210 (data centers). **4 are
Virginia**: VAG250128 (Anthem CDC3, Harrisonburg), **VAG250162 (Microsoft IAD11
Campus, Aldie/Loudoun)**, VAG830615 (Birchwood — the coal plant), VA0093301
(Amazon, Louisa). So VA data centers DO hold NPDES/VPDES permits.

### ICIS_FACILITIES_VA.csv (18,244 rows) 🔴🟡
Cols incl NPDES_ID, FACILITY_NAME, COUNTY_CODE, CITY, lat/long, IMPAIRED_WATERS.
**~20 Prince William-area data-center-named VPDES facilities**, almost all
**VAR10 = construction-stormwater general permits** (erosion/sediment during
building; temporary; no operational-water reporting): Gainesville Crossing,
Innovation Manassas DC4, Manassas Corporate Center DC Bldg 1/2, MDC1, NTT VA10/
VA13, NVA05C/NVA13, Westview 66 MNZ01, MNZ03, Zumot, Youth for Tomorrow DC. Plus
Amazon DDC9/DVA5 (VAR05). **These are building-mud permits, not water-use
permits** — but a flat "0 hold NPDES" is wrong and a reviewer with ECHO would
catch it. Correct statement: *PWC data centers hold construction-stormwater
permits, not operational-discharge permits.* (Also a new source of building
codenames: IAD319, NVA05C, Westview 66, Innovation Manassas DC4.)

### VAG25 cooling-water permit + Microsoft IAD11 🔴🟡 — the sharpest find
VAG25 is a Virginia general VPDES permit whose reported parameters are
**temperature, total residual chlorine, flow (50050), pH, ammonia, phosphorus,
Cu/Zn/Ag** — i.e. cooling-tower blowdown chemistry. Of 32 VAG25 facilities in
VA, only **Microsoft IAD11 Campus (VAG250162, Aldie/Loudoun)** is a data center.
It is **required to report discharge FLOW** — proving the operational-discharge
pathway exists — **but its DMRs are overdue: 41 effluent violations, mostly
"DMR, Limited – Overdue," and the flow value fields are blank.** So even the one
regional hyperscale mandated to report its cooling discharge has not. The
invisibility is partly *non-compliance*, not only *absence of a regime*.

### VA_NPDES_EFF_VIOLATIONS.csv (162,440 rows) 🟡
Full VA DMR violation history. Our regional DC permits appear 41× — all
VAG250162 (Microsoft IAD11) overdue-DMR violations (params: flow, pH, chlorine,
temperature, ammonia). No PWC data center appears (they hold only VAR10).

### echo_loadings_34919817.csv (ECHO annual loadings, PWC FIPS 51153, 2026) 🟢
Actual pollutant/flow loadings for **all 32 permitted dischargers in Prince
William County — ZERO are data centers.** Dominant discharger is **Dominion
Possum Point** (VA0002071, 58 rows, real MGD flow — this is the Potomac-basin
Scope 2 plant). Others: NOVEC, MCB Quantico, PWC landfill/Balls, HL Mooney
reclamation, Manassas WTP, Virginia American Water, concrete/asphalt/paving.
**Confirms at the county discharge level: data centers consume but do not
discharge, so they are invisible to DMR monitoring** — the model's point, now
evidenced. Columns include Actual Avg Facility Flow (MGD), Wastewater Flow
(MGal/yr), Pollutant Load (kg/yr) — usable to cross-check Possum Point.

### ICIS_MASTER_GENERAL_PERMITS.csv (2,838 rows) ⚪
Master GP registry: design/actual flow, receiving water body, HUC12, issue/
expiry, status. Useful to resolve receiving water bodies + HUC for any permit.

**Net correction for METHODOLOGY/UI:** replace "0 hold NPDES" with: data centers
hold construction-stormwater permits (VAR10) but no operational-discharge permit
in PWC; the lone regional cooling-water permit (Microsoft IAD11, VAG25) mandates
flow reporting yet sits in DMR non-compliance. Stronger and defensible.

---

## D. Local hydrology & energy

### Cedar Run stream gage + DEQ well 🟡 (folder names are SWAPPED — data hygiene)
- `groundwater_well/` actually holds the **USGS Cedar Run stream gage 01656000**
  ("CEDAR RUN NEAR CATLETT, VA", Occoquan HUC 020700100604, drainage 93.4 sq mi,
  2007→2026, param **gage height** ft, flood stage 12 ft). Recent ~2.8 ft.
- `cedar_run_gage/` actually holds a **DEQ groundwater well** (VA087, Fauquier,
  aquifer 230TRSC, 222 ft deep, built 2023-07-11, param depth-to-water ft),
  Jan–May 2026 only; recent water table ~49.6 ft — near the **deepest** in its
  short record. Both corroborate the drought locally. Caveat: gage HEIGHT not
  discharge (no rating curve here), so can't derive streamflow reduction; and the
  sites are just over the line in Fauquier, on the Occoquan/Broad Run system.

### PlanningQueues.xlsx (PJM interconnection queue, 9,263 rows) 🟡
- **Prince William: 30 generation-interconnection projects — overwhelmingly gas
  and battery STORAGE at Possum Point** (8+ active battery projects, 60–100 MW
  each, ~600 MW queued; one 94 MW active gas). Essentially **no local solar** (one
  13 MW, withdrawn). The county's "100% renewable by 2035" goal (Res 20-773) is
  not being met on the ground; the local buildout is gas + storage in the Potomac
  basin at Possum Point — reinforces the marginal-gas argument (§16). Storage
  charges from the marginal generator (gas), so it doesn't decouple water.
- VA statewide queue churn is enormous: **65,248 MW withdrawn**, 13,983 active,
  11,988 in service. Fuel + county + MW + status per project — usable for a
  Loudoun extension.

### net_metering_2024/2025/2026.xlsx, non_netmetering_2024.xlsx ⚪
EIA-861 net-metering (distributed solar) capacity, utility×state. State-level
renewable context (Dominion net-metered solar), not per-facility. Header sits
below an Unnamed-column banner row. Low direct value to the water model.

---

## E. GeoJSON layers (all 24 property-enumerated in full)

Most are already used (Data_Center_Buildings/Projects, Watersheds, Stream,
Parcel, RPA, Soil, Zoning, Use_Permits, Planning_Pending_Cases, HV lines,
Stormwater, Tidal, WQP stations, Springs distance). New/under-used:

### SURFACE_WATER_TEMPERATURE.geojson (413 stations) 🟡 — unused, thermal-stress
Per-station **Theil-Sen temperature trends** (Variable CTEMP, Year1→Year2, Tau,
p-values). **77 DEGRADING (warming), 329 no-trend, 7 improving; 76% have a
positive slope; median +0.04 °C/yr** (e.g. Accotink Creek +0.066 °C/yr, 2002–22).
Regional streams are warming — lower DO and assimilative capacity, compounding
the once-through thermal loads (Surry, Possum Point) and the drought. Never used.

### Data_Center_Buildings.geojson (243) 🟡 — richer fields than the model uses
Full key set includes **OCCDate** (certificate-of-occupancy epoch-ms, non-null
for 56 completed buildings — a truer completion date than YearBuilt, which had
the =0 bug) and **ApprovedGFA (108), BPGFA (86), PermittedGFA (12), REATaxedGFA**
alongside GFA. resolve_gfa uses REATaxedGFA/BPGFA/GFA; **OCCDate is unused** and
could sharpen vintage/PUE for the 56 completed buildings.

### Zoning_Districts.geojson (2,208) has a PROFFERS text field 🟡
Proffer language per zoning case — worth a full read for any water/cooling
commitments not yet captured (the model only has PERMIT_COOLING_CONDITIONS for
two cases).

### LRLU_Developable_Areas.geojson (753) ⚪
Per-area average GFA/employment/activity-density for developable land — buildout
modelling inputs; tangential to the water footprint.

### Springs_Groundwater_Layers.geojson (2,916) ⚪
Groundwater QUALITY geochemistry (Al, As, Ba, radionuclides, alkalinity…), not
quantity. Model only uses distance-to-spring.

---

## CORRECTIONS / ADDITIONS TO APPLY (ranked)

1. 🔴 **Drought & climate context is entirely absent and is the paper's water-stress
   spine.** Add: PDSI/PHDI −5.3 (99th-pct extreme drought, 2026); CDD +35% over
   record (2010s–2020s ~1,365); 80% of CDD in Jun–Sep; 12-mo precip −15%. New
   METHODOLOGY section + estimator context.
2. 🔴 **Fix the "0 NPDES" headline.** Data centers hold VAR10 construction-stormwater
   permits (~17 in PWC), not operational-discharge permits; the lone regional
   cooling-water permit (Microsoft IAD11, VAG25) mandates flow reporting but is in
   DMR non-compliance (41 overdue violations). County ECHO loadings confirm zero
   DC dischargers. Rewrite the UI headline + U1/U-items + METHODOLOGY §7/§8.
3. 🟡 **Use the utility's own 2025 figures** (3.8% avg / 10.1% peak daily demand;
   peak/avg ≈ 2.7×) as an independent cross-check on the peak model (§12) and the
   0.42 MGD anchor (§6.1).
4. 🟡 **Shell-first permitting decouples GFA from MW in time** (PP-NewStructure) —
   cite in the density discussion (§15) as a mechanism behind the convexity.
5. 🟡 **Stream warming (76% of stations)** and **local drought gages** — add as
   thermal/hydrological stress context.
6. 🟡 **Renewable reality:** county goal is 100% renewable electricity by 2035
   (Res 20-773), but the PJM queue for PWC is gas + battery storage at Possum
   Point, ~no local solar — strengthens the marginal-gas argument (§16) and the
   market-based-Scope-2 caveat (§14).
7. ⚪ **Data hygiene:** cedar_run_gage/ vs groundwater_well/ folders are swapped;
   3 VIENNA_* climate files identical; 2 Manassas_* identical; station meta lat/long
   swapped.

## STILL TO READ (report PDFs — not structured "datasets")
ICPRB 2025 WMA study; ICPRB DataCenters&WaterUse (Mar 2026); JLARC Rpt598;
Dominion GS-5 Large-Load rate class; Dominion SCC PUR-2026-00011; LBNL QueuedUp
2025; EconBulletin. Plus doc JSONs: Reference Manual, FY2026 SUP App Package,
SUP2025-00016, prince_william_cesmp_full, Data_Center_Projects. station.csv,
observations-759582.csv (iNaturalist), rt_hrl_lmps.csv (empty, 0 rows).

---

## F. Remaining document JSONs

### prince_william_cesmp_full.json (Community Energy & Sustainability Master Plan) 🟡🔴
801 lines, **111 "drought" + 201 "water" mentions.** The county's own plan:
- **Rates drought risk "LOW"** — *"Drought is a potential threat… however, it was
  rated low due to the moderate drought projections countered by the projected
  increase in precipitation."* This directly contradicts the observed NOAA data
  (PDSI −5.3, 99th-pct extreme drought, precip −15%). The county's planning
  **underrates the very hazard now occurring.**
- **The data-center section is emissions/energy ONLY** — "energy intensive… to
  cool their servers" but **no water-consumption analysis whatsoever.** Relies on
  data centers "procuring 100% clean electricity" and county **REC retirement** to
  hit "100% renewable county-wide by 2035 / 92% clean by 2030." This is exactly
  the REC-based, water-blind accounting §14 critiques.
- Data Center Ordinance Advisory Group established Jan 2023.
- **Finding:** the county's flagship sustainability plan is blind to the
  data-center WATER dimension and underrates drought — a clean policy gap for the
  paper.

### SUP2025-00016.json 🟡 (48 water / 6 cooling / 5 potable / 1 reclaim mentions)
A specific data-center Special Use Permit staff report; model has cooling
conditions for it but there is more water content (reclaim mention) to mine on a
full read.

### Reference Manual… / FY2026 SUP Application Package ⚪
Application-process manuals; "water" appears as Potable Water Plan requirements
(consistent with §7.2a — reviews availability/connection, never quantity).

### station.csv (75 rows) 🟢
USGS + VA DEQ water-quality monitoring station registry for the region (Neabsco
Creek, S F Quantico Creek, Broad Run DEQ trend stations; HUC, drainage area,
aquifer). Source behind water_context monitoring counts.

### rt_hrl_lmps.csv ⚪ empty/failed export (15 bytes, "[object Object]").
### observations-759582.csv ⚪ iNaturalist research-grade species observations (biodiversity).

## STATUS
All 81 structured files (CSV/JSON/GeoJSON/XLSX) read in full — every record parsed
programmatically, every document scanned. The ~13 report **PDFs** (ICPRB ×2, JLARC
Rpt598, Dominion GS-5 & SCC, LBNL, EconBulletin) remain for a page-by-page read.

---

## G. PDF reports (full text extracted with pypdf and read)

### ICPRB "Data Centers and Water Use in the Potomac River Basin" (Mar 2026, 2p) 🟢🔴 — the authoritative source
CONFIRMS several model choices and CORRECTS/adds others:
- **WUP: 100–1,600 gal/day/MW average by cooling type; up to 8,500 gal/day/MW at
  PEAK for evaporative; regional average WUP = 800; consumptive-use factor 75%.**
  → the model's 0.75 factor, 800 basin-medium, ~1,600 high all ✓. Peak 8,500/800 ≈
  10.6× ✓ matches the model's 9.9× peak ratio (§12).
- **Peak/average CONFIRMED independently:** "summer monthly ≈ 3× average annual;
  peak daily as much as 10×." So §12's 9.9× is right, and the 3× summer-monthly is
  the seasonal factor for the Scope-1 seasonal model.
- **New basin density anchor:** ~290 buildings, ~5,400 MW, ~56M sqft →
  **10,370 sqft/MW basin-wide** (independent of the model's 8,818 fleet / 8,638
  permit-backed; basin figure is less dense, incl. older Loudoun stock). Add to §15.
- **~40% of facilities rely EXCLUSIVELY on air cooling** (hybrid "free cooling" in
  winter) — the best regional prior for cooling-type, which the model has 0/243
  direct evidence on. Use as a Bayesian prior.
- **Basin-scale shares:** data centers = 1% of WMA withdrawals but **9% of annual
  consumptive use, up to 12% in summer**; basin-wide 0.3% withdrawals / 3%
  consumptive. WMA current consumptive ≈ **4 MGD avg / 15 MGD peak** (upstream
  <0.1 / 0.3). These are the authoritative context magnitudes.
- **2050 projection:** WMA 22 MGD avg / 80+ MGD peak; upstream 5 / 17 MGD. PJM
  load +135% Dominion, +35% Allegheny; data centers the primary driver.
- 🔴 **Reclaimed-water CORRECTION to my §18.4:** "reclaimed water is largely lost
  rather than returned to the river system, reducing return flows." So the
  reclaimed-water gas plants (Greensville/Warren/Brunswick) still cause consumptive
  loss — I framed them as ~zero fresh-basin impact; the honest framing is that they
  shift the loss from withdrawal to return-flow reduction, still consumptive.
- **Regulatory gap CONFIRMED:** utility-supplied data centers "do not fall under
  existing consumptive use regulations" → recommends low-flow mitigation policy.
- Potomac provides 75% of the region's supply (Fairfax Water, WSSC, Washington
  Aqueduct; 5M people; sole source for DC + Arlington).

### Dominion_GS-5_LargeLoad_RateClass.pdf (10p, May 2026) ⚪ power economics
- **~70 GW data-center queue**: 25 GW with energization dates through 2031, +45 GW
  undated. GS-5 large-load rate class effective Jan 1 2027: 14-yr contract (4-yr
  ramp), minimum demand charges 85% T&D / 60% generation, exit fees, $250k ELOA.
- JLARC Dec 2024 concluded data centers DO pay their fair share of energy costs.
- High load factor (run flat) supports the model's high-utilization assumption in
  ICPRB Eq 6-3. No water content.

### Dominion_LargeLoad_SCC_PUR-2026-00011.pdf (12p, Feb 2026) ⚪ power/load
SCC application for the large-load connection queue process. **~25,000 MW dated
by end-2031; +45,000 MW batched/under study; ~70,000 MW total queue = nearly
TRIPLE the DOM Zone all-time peak of 24,678 MW (Jan 23 2025)**; ~10 new requests/
month (2–3 GW/mo). Requests ≥~100 MW, capped at 300 MW each, batches of ~10
(2–3 GW). Confirms the scale of load growth behind Scope 2. No water content.

### EconBulletin_LaunchCost_2022.pdf (15p) ❌ MISFILED / irrelevant
"An analysis of launch cost reductions for low-Earth-orbit satellites" (Economics
Bulletin 42(3), 2022). About SATELLITE LAUNCH COSTS — nothing to do with water or
data centers. Stray file in the folder; exclude from the corpus.

### LBNL_QueuedUp_2025.pdf (64p, Dec 2025) ⚪ national context
National interconnection-queue trends. **Gas +72% in 2024 (136 GW) while solar
−12%, storage −13%, wind −26%** — gas resurgence, data-center-driven. Only 13% of
2000–2019 requests reached commercial operation (77% withdrawn); median IR→COD 55
months. Nuclear tiny (5.3 GW). Reinforces §16 (marginal gas) and the "renewable
goals are aspirational; the grid actually adds gas" point. County-level solar/
storage/wind/gas maps exist in the companion data file (next). No water.

### LBNL_Ix_Queue_Data_File_thru2025.xlsx (national queue, 41 sheets) 🟢
"03. Complete Queue Data" = cleaned national queue (q_id, county, fips, type_clean,
mw_1/2/3, status, dates). VA = 1,343 rows; **Prince William = 28: Possum Point gas
(operational) + many active BATTERY projects (Reid, Railroad, Bethlehem Energy
Centers) + withdrawn gas/oil; one withdrawn solar (Nokesville).** Corroborates the
PlanningQueues finding — PWC new generation is battery + legacy gas, ~no solar.

### JLARC Rpt598 "Data Centers in Virginia" (Dec 2024, 156p) 🟢🔴 — the water-benchmark source
Read: Summary, Recommendations, Ch1–2, Ch5 (water) in full, Appendices J/K/L in
full; Ch3–4 (energy/ratepayer economics) at summary level (not water).
- **Benchmark anchors CONFIRMED exactly:** average large office building = **6.7
  MGal/yr (0.0184 MGD)** — the model's 0.018 MGD office reference ✓; **one building
  used 243 MGal in 2023 (10% of industry total)** — the model's "largest measured"
  0.666 MGD benchmark ✓; 11 buildings >50 MGal.
- 🔴 **CRITICAL framing:** JLARC's whole-Virginia data-center DIRECT water use in
  2023 = **2.1 billion gallons = 5.75 MGD (≈1/3 reclaimed; <0.5% of state
  withdrawals)**. This is on-site (Scope 1) ONLY. The model's headline 57–60 MGD is
  Scope 1+2+3; its Scope 1 (~2 MGD PWC) is consistent with JLARC. **The 57 MGD must
  NEVER be compared naively to JLARC's 5.75 MGD — always label Scope 1 vs 1+2+3.**
- Only **TWO Virginia data centers have their own DEQ withdrawal permits**; rest are
  utility-supplied → confirms the model's "no self-withdrawal / invisible" point.
- Statewide: ~150 sites, ~340 buildings, **63M sqft, 5,050 MW → ~12,475 sqft/MW**
  (density anchor; less dense than PWC, includes colo/older). 250k sqft ≈ 50 FTE.
- **Recommendation 6: authorize localities to require water-use estimates + consider
  water in rezoning/SUP** — validates the model's central "no water field" finding;
  legislative fix pending. Withdrawal-permit thresholds: >10k gpd non-tidal, >2 MGD
  tidal, >300k gal/mo groundwater. Permits must curtail during droughts.
- **Appendix J (PUE) 🔴 water-energy tradeoff:** hyperscale fleet PUE **1.1–1.4**
  (validates model bands); **a PUE mandate would INCREASE water use because
  water-dependent cooling uses less energy** — the explicit efficiency tradeoff
  behind §14/§16.4 and the PUE-cap handling.
- **Appendix K (wastewater):** blowdown is a small fraction of intake but carries
  **salts/TDS/chlorine/additives** (matches VAG25 params + the 74216 TDS proffer);
  most discharge to sewer, a few hold own permits (Microsoft IAD11 = the exception).
- Appendix L: Loudoun + PWC data-center zoning votes in 2026; all three NoVA
  localities added zoning minimums since 2019.
- Backup diesel: <4% NoVA NOx, ≤0.1% CO/PM; nearly all Tier 2. AWS committed $35B to
  new VA locations by 2040. Residential customer bills +$14–37/mo by 2040.

### ICPRB 2025 WMA Water Supply Study (Dec 2025, 266p) — Section 6 is the model's FOUNDATION 🟢🔴
Read Section 6 (data centers) in full; it is the source of every core constant.
CONFIRMED exactly:
- **Eq 6-2** CU = (Effective Power Demand × WUP) × 0.75; **Eq 6-3** Effective IT
  Power = Generator Capacity × 0.5 redundancy (2N) × 0.8 utilization (EPRI 2024) ✓
- **PWC: 0.42 MGD avg / 4.2 MGD peak (2023) → WUP 309 / 3,060** ✓✓ (model's
  pwc_observed). Loudoun 4.5/10.9 MGD → WUP 1,006/2,435 ✓. Fairfax 1,145.
- **8,818 sqft/MW (JLARC db) used ONCE** to convert Loudoun's 0.017 gal/day/sqft
  into the 150 gal/MW/day air-cooled tier; power in Eq 6-3 is generator capacity,
  NOT floor area → CONFIRMS the model's "8,818 is run backwards" finding (§6.2).
- basin representative WUP 800 avg / ~3,000 peak; fully-water-cooled 1,577 ✓.
CORRECTIONS/additions:
- 🔴 **Table 6-5 scenarios: Low 600/2,100, Medium 800/2,900, High 1,400/5,200
  gal/MW/day.** The model's top tier 1,577 is the *implied 100% water-cooled* avg
  (fine), but the **peak for water-cooled facilities reaches 5,200 (Table 6-5) to
  8,500 (evaporative, Mar sheet) — well above the model's flat 3,060 peak.** So the
  model UNDERSTATES summer peak for the few fully-water-cooled sites; §12 peak logic
  should let peak scale with tier, not use one 3,060 for all.
- Default **78 MW** for centers without reported capacity (model uses permit/GFA
  instead — more granular, fine).
- Dominion DC share **25% now → 68% by 2050 (2.7×)**; APS 0–5% → 27.5% (14×).
- WMA DC use **4.0 MGD avg / 14.3 MGD peak (2025) → 22.2 / 80.5 by 2050**; upstream
  <0.1/0.3 → 4.7/16.8 (medium), 8.1/29 (high). ✓ matches Mar fact sheet.
- **Seasonal monthly factors** (App A.3 Table A.3-2, from Loudoun + PWC data) — the
  ready-made seasonal profile for a Scope-1 seasonal model.
- **Broad Run WRF supplies reclaimed water to data centers; evaporative losses
  reduce its return flow** — ties reclaimed-water loss to the main PWC watershed.
Balance of the 266p study = WMA supply/demand (PRRISM) modeling, drought/CO-OP
operations — broad context, not data-center-specific.

## PDF STATUS: all 7 read (data-center-relevant content in full).
