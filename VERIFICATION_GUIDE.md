# Independent verification guide — AGU26 abstract

Every claim in `ABSTRACT_AGU26.txt`, with what it means, where it comes from, and how to check it yourself. Ordered so the **checks that require no trust in my code come first**.

## Before you start

**Two Python interpreters are required** (they have different libraries):

| Alias | Path | Has |
|---|---|---|
| `PY_SK` | `/usr/bin/python3` | scikit-learn, scipy (for model fitting) |
| `PY_GEO` | `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` | geopandas, numpy (for everything else) |

```bash
cd ~/Desktop/Water/water-atlas
export PY_GEO=/Library/Frameworks/Python.framework/Versions/3.13/bin/python3
export PY_SK=/usr/bin/python3
```

You also need `pdftotext` (from poppler) — already installed if `pdftotext -v` prints a version.

---

# TIER A — Check the sources themselves (no trust in my code required)
**~40 minutes. Do this first. If anything here fails, stop and tell me.**

## A0. Are the source PDFs the genuine publications?

**What this checks:** that the documents in the corpus weren't altered.

```bash
# JLARC — already confirmed identical to the official copy
curl -sL "https://jlarc.virginia.gov/pdfs/reports/Rpt598.pdf" | shasum -a 256
shasum -a 256 data/water_raw/Rpt598.pdf
```
**Expect:** both `d794e060d2697b41ac69aa6133cf73ea0473433736e4e1ab85d26df219383322`

```bash
# ICPRB — potomacriver.org connections are INTERMITTENT. Download to a file first so
# a failure is visible; piping curl -s straight into shasum silently hashes nothing.
curl -L --max-time 240 --retry 3 \
  "https://www.potomacriver.org/wp-content/uploads/2025/12/2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.pdf" \
  -o /tmp/wma.pdf -w "http=%{http_code} bytes=%{size_download}\n"

# only hash it if the download actually produced a file
[ -s /tmp/wma.pdf ] && shasum -a 256 /tmp/wma.pdf || echo "DOWNLOAD FAILED — retry, do not interpret this as a mismatch"
shasum -a 256 data/water_raw/2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.pdf
```
**Expect:** `http=200 bytes=12425557`, then both hashes `2ee07c17d80fb962d9399408677522914f666bac69eaa7c739ff0cb31fb99d45`

> ⚠️ **If you see `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, that is the SHA-256 of an EMPTY file** — the download returned zero bytes. It is a network failure, **not** a hash mismatch. Retry.

---

## A1. "utility-reported 2023 data compiled by Virginia's legislative audit commission"

**Plain meaning:** our validation benchmark is real metered water data that Virginia's legislature collected from water utilities — not something we modelled.

**Where:** JLARC Report 598, **page 80** (Figure 5-3 and its source line).

```bash
pdftotext -q -f 80 -l 80 data/water_raw/Rpt598.pdf - | tr '\n' ' ' | fold -w 100
```

**Look for, verbatim:**
- "an average large office building (**6.7 million gallons per year**)"
- "In 2023, **11 data center buildings each used over 50 million gallons**"
- "one building that used **243 million gallons**"
- "**2.1 billion gallons** of water, with just over a third coming from reclaimed"
- Source line: "JLARC staff analysis of **data provided by water utilities** serving Fairfax, Henrico, Loudoun, Mecklenburg, and **Prince William** counties and the Town of Wise"

**What to notice:** the source line says **Prince William is included**. That is why the abstract says "partially, not fully, independent" — our own county is inside the benchmark. Also note "Water use is on a **per building, not per campus**, basis," which is why we compare per building.

---

## A2. The Scope 1 water intensity (309 gal/MW/day) — and its circularity

**Plain meaning:** the number converting a data center's electricity use into on-site water use. It comes from ICPRB, who got it by dividing Prince William's reported water use by their own estimate of its power.

**Where:** ICPRB 2025 WMA Water Supply Study, **pages 125–127**.

```bash
pdftotext -q -f 125 -l 127 data/water_raw/2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.pdf - | tr '\n' ' ' | fold -w 100
```

**Look for:**
- "In the Prince William Water service area, **0.42 MGD on average and 4.2 MGD for peak day** were reported for 2023"
- "**309 for the average and 3,060 for peak day in Prince William**"
- "WUP was then calculated by **dividing utility reported data center water use by effective power demand**" ← **this is the circularity.** It means we can never claim our county *total* was validated — only the distribution's *shape*.
- "a **redundancy factor of 0.5 is assumed**… a **utilization factor of 0.8** is applied based on industry data (EPRI, 2024)"

**Do this arithmetic yourself:** 4.2 ÷ 0.42 = **10.0×** (PWC peak-to-average). Compare Loudoun: 10.9 ÷ 4.5 = **2.4×**. The abstract's July claim rests on PWC's unusually high ratio — which is ICPRB's reported data, not ours.

**Judgment call for you:** ICPRB gives 0.5 and 0.8 as **bare numbers with no uncertainty range**. Our model puts a ±range around them that ICPRB does not publish. That's our assumption, not theirs.

---

## A3. "the marginal generator is never nuclear"

**Plain meaning:** when demand rises, the power plant that ramps up is gas or coal — never the nuclear plant, which already runs flat out.

**Where:** Monitoring Analytics, *2023 State of the Market Report for PJM*, Section 3, **printed page 125** (= page 3 of the section-3 PDF).

```bash
pdftotext -q -f 3 -l 3 data/water_raw/PJM_SOM_2023_sec3_energy_market.pdf - \
  | tr '\n' ' ' | grep -oE "In 2022, coal units were.{0,90}"
```

**Look for:** "In 2022, **coal units were 10.0 percent and natural gas units were 75.2 percent of marginal resources**."

**What to notice:** **nuclear does not appear in that list at all.** That is the entire basis for "assigns none." Confirm the page footer reads "2023 State of the Market Report for PJM 125."

**Judgment call for you:** is a fuel's *absence* from a published list strong enough evidence? I think yes (it matches standard dispatch theory), but the zero follows from this **by construction** — it is a premise, not a discovery. The abstract concedes this with "neither is incorrect."

---

## A4. "the regional authority's own assessment covers on-site use only"

**Plain meaning:** ICPRB's own data-center study ignores the electricity-related water entirely.

```bash
pdftotext -q data/water_raw/ICPRB.DataCentersandWaterUse.ICPRB_.March2026.pdf - \
  | tr '\n' ' ' | grep -oiE "power plant|electricity generation|off-site|marginal" | sort | uniq -c
```
**Expect:** **no output** (zero matches). That's the claim.

---

## A5. "within the world's largest data-center region"

**Plain meaning:** Northern Virginia hosts more data centers than anywhere on earth.

**How to check:** search for "Northern Virginia 35% of world's data centers" and "Loudoun data center capital of the world."

**Important nuance:** **Loudoun County**, not Prince William, is the single largest *county*. PWC has ~10M sq ft operating and ~90M planned, and is projected to overtake. The abstract says "**within** the world's largest **region**" — which is accurate. Don't let it drift to "PWC is the world's largest."

---

# TIER B — Recompute from raw data (checks my arithmetic)
**~30 minutes.**

## B1. "243 data-center buildings… 54 operate today (10.5 MGD)… full-buildout 49.6 MGD"

**Plain meaning:** we cover 243 buildings, but only 54 exist now. The big number is what happens if everything approved gets built.

```bash
$PY_GEO -c "
import json
d=json.load(open('public/data/facility_profiles.json'))
bs=[b for b in d['buildings'] if b.get('scope_water_footprint')]
from collections import Counter
print('n buildings:', len(bs))
print('status:', dict(Counter(b.get('status') for b in bs)))
tot=sum(b['scope_water_footprint']['total_mgd_central'] for b in bs)
done=sum(b['scope_water_footprint']['total_mgd_central'] for b in bs if (b.get('status') or '').lower()=='completed')
print(f'full buildout: {tot:.1f} MGD | completed only: {done:.1f} MGD')
"
```
**Expect:** 243 buildings · Completed 54, Planned 120, Pending 36, Under Construction 31, Under Review 2 · **49.6** and **10.5** MGD.

**What it means:** 49.6 is *not* current water use. It is ~4.7× current. The abstract must always pair them.

---

## B2. "indirect water dominates (87%)"

**Plain meaning:** 87% of the water is used at power plants, not at the data centers.

```bash
$PY_GEO -c "
import json
d=json.load(open('public/data/facility_profiles.json'))
bs=[b for b in d['buildings'] if b.get('scope_water_footprint')]
s=lambda k: sum(b['scope_water_footprint'][k]['mgd_central'] for b in bs)
s1,s2,s3=s('scope1_onsite_cooling'),s('scope2_electricity'),s('scope3_embodied')
t=s1+s2+s3
print(f'on-site {s1:.2f} ({100*s1/t:.1f}%) | electricity {s2:.2f} ({100*s2/t:.1f}%) | supply-chain {s3:.2f} ({100*s3/t:.1f}%)')
"
```
**Expect:** on-site 1.76 (**3.6%**) · electricity 43.32 (**87.4%**) · supply chain 4.51 (9.1%)

**Note:** the plain-language summary's "on-site is 4% of the total" refers to the **3.6%**. Do *not* use 13% — that would be on-site + supply chain.

---

## B3. The power-plant water factors (391 / 196 / 474 gal per MWh)

**Plain meaning:** how much water evaporates to make one megawatt-hour, by fuel — computed from federal data, not assumed.

```bash
$PY_GEO -c "
import csv
from collections import defaultdict
def f(s):
    try: return float(str(s).replace(',',''))
    except: return None
agg=defaultdict(lambda:{'cu':0.0,'gen':0.0})
for r in csv.DictReader(open('data/usgs_te_water_2008-2020_VA.csv',encoding='latin-1')):
    if r.get('State')!='VA' or r.get('YEAR') not in {'2018','2019','2020'}: continue
    fu,mv=r.get('Plant.level_dom_fuel'),r.get('general_mover')
    k='nuclear' if fu=='nuclear' else 'coal' if fu=='coal' else ('natural_gas_cc' if (mv=='NGCC' or fu=='gas') else None)
    if not k: continue
    cu,gen=f(r.get('cu_mgd')),f(r.get('Net.Generation.Year.To.Date'))
    if cu is not None and gen and gen>0: agg[k]['cu']+=cu; agg[k]['gen']+=gen
for k,v in agg.items(): print(f'{k}: {(v[\"cu\"]*1e6*365)/v[\"gen\"]:.0f} gal/MWh')
"
```
**Expect:** nuclear **391** · natural_gas_cc **196** · coal **474**

**The formula:** (water consumed per day × 1,000,000 gal × 365 days) ÷ (electricity generated per year in MWh). Data: USGS Thermoelectric Water Use 2008–2020, Virginia plants, 2018–20 pooled.

---

## B4. "a reservoir 80 km outside the host basin" — and why it's Lake Anna

**Plain meaning:** all Virginia nuclear water consumption happens at one lake, ~50 miles from the data centers, in a different river basin.

```bash
$PY_GEO -c "
import csv
from collections import defaultdict
agg=defaultdict(lambda:{'cu':0.0,'src':None})
for r in csv.DictReader(open('data/usgs_te_water_2008-2020_VA.csv',encoding='latin-1')):
    if r.get('State')!='VA' or r.get('YEAR') not in {'2018','2019','2020'}: continue
    if r.get('Plant.level_dom_fuel')!='nuclear': continue
    try: c=float(str(r.get('cu_mgd')).replace(',',''))
    except: c=0.0
    agg[r['Plant.Name']]['cu']+=c; agg[r['Plant.Name']]['src']=r['Name.of.Water.Source']
for k,v in agg.items(): print(k, ':', round(v['cu'],2), 'cu_mgd, source =', v['src'])
"
```
**Expect:** Surry **0.00** (James River) · North Anna **95.21** (North Anna River)

**Why this matters:** Surry is cooled by tidal river water that returns to the river, so it consumes nothing. **Every drop of Virginia's nuclear water consumption is at North Anna → Lake Anna → York basin.** The 80 km is the straight-line distance from the data-center corridor (38.75, −77.53) to North Anna (38.06, −77.79) — check it in any mapping tool; ≈50 miles.

---

## B5. "over 40% of electricity-related water" and "assigns none"

```bash
$PY_GEO basin_analysis.py 2>&1 | tail -25
```
**Expect:** York (Lake Anna) **18.77** MGD average → **0.00** marginal; 80% consumed outside the Potomac basin.

**Do the share yourself:** 18.77 ÷ 43.32 = **43.3%**. The abstract says "over 40%" because this share ranges **42–55%** depending on which generation-mix convention you use — check that sensitivity in METHODOLOGY §49.4.

**Note:** 18.77 is a **full-buildout** figure. Today's operating fleet attributes ≈4.0 MGD to Lake Anna. The *share* (43%) is identical either way — which is why the abstract uses the share, not the volume.

---

## B6. "4% of mean annual flow but 23–34% of July"

```bash
$PY_GEO -c "
import json
b=json.load(open('public/data/basin_stress.json'))['basins']['BROAD RUN']
s=json.load(open('public/data/seasonal_basin_surface.json'))['surfaces']['BROAD RUN']
print('annual draw as % of mean flow:', b['pct_of_annual_mean_flow_annual_draw'])
print('July, central (30% baseload):', s['central']['worst_pct_of_flow'])
print('sweep:', {k:v['worst_pct_of_flow'] for k,v in s['baseload_sweep'].items()})
print('gage:', b['gage'], '| record:', b['record'])
"
```
**Expect:** 4.22% annual · 28.3% July central · sweep 33.7 / 28.3 / 22.8 (→ the 23–34% range)

**What's measured vs modelled:** the river flow is measured (USGS gage). The *monthly shape* of water demand is **modelled** — we spread annual water across months in proportion to cooling-degree-days over a baseload, and the baseload share (10/30/50%) is the swept assumption. **Caveat to note:** the Broad Run gage (01656500, Buckland) was discontinued in **1986**, so the flow climatology is historical.

---

# TIER C — Re-run the models (checks reproducibility)
**~1 hour. Optional unless Tier A or B failed.**

## C1. Rebuild everything from scratch
```bash
$PY_SK  fit_power_model.py        # needs scikit-learn
$PY_SK  gp_power_model.py         # calibration + kernel check
$PY_GEO build_facility_profiles.py
$PY_GEO monte_carlo.py
$PY_GEO verify_research_ready.py  # 19 automated checks
```
**Expect:** `19/19 checks passed — RESEARCH-READY`, and county total **53.6 MGD, 90% CI [44.5, 64.9]**.

## C2. "leave-one-out calibrated (90% coverage 0.86)"

**Plain meaning:** we tested our uncertainty ranges by hiding one site at a time and predicting it. If we say "90% confident," we should be right ~90% of the time. We were right 86% — close enough to be honest.

**In `$PY_SK gp_power_model.py` output, expect:** coverage_90 = **0.857**, coverage_50 = 0.500, mean z² = **1.10**, and "RBF adds nothing → linear justified."

**How to read it:** mean z² near 1.0 means the uncertainty is neither exaggerated nor understated. Below 1 = too cautious; above 1 = overconfident.

**Caveat:** this is fitted on **n = 14 sites**. That is a small sample and the single biggest technical weakness.

## C3. "±60% intervals" and "the tier… is empty"
```bash
$PY_GEO evidence_ladder.py
```
**Expect:** tier 1 (permit, n=45) **±26%** · tier 2 (disclosed load) **n = 0** · tier 3 (n=57) ±57% · tier 4 (generic, n=141) **±60%**

**Important:** the abstract leads with **±60%** because that one is *calibrated* (C2). The ±26% depends on an uncertainty range **we** put around ICPRB's factors, which ICPRB does not publish — see A2. Under different but equally defensible spans the tier-1 number moves between ±18% and ±37%. **Do not quote the 26:60 ratio as if measured.**

## C4. "all six published constraints hold… KS p = 0.09"
```bash
$PY_SK validate_scope1_distribution.py
```
**Expect:** 6/6 PASS, KS D=0.165, **p=0.093**

**Plain meaning:** a Kolmogorov–Smirnov test asks "could these two distributions have come from the same underlying process?" p = 0.09 is above 0.05, so we **cannot reject** that ours matches the metered one. That is *consistency*, not proof of correctness.

---

# What you should conclude

| If… | Then… |
|---|---|
| Tier A all passes | The external facts are real and correctly cited. This is the most important tier |
| Tier B matches | My arithmetic on top of those facts is right |
| Tier C reproduces | The pipeline is deterministic and the numbers aren't stale |
| Anything fails | Tell me which check and what you saw |

**What none of this can verify:** whether the *interpretation* is sound — whether comparing the two accounting conventions is a fair comparison, and whether the framing overclaims. Every error found in this project has been interpretive, not arithmetic. That needs your advisor: see `ADVISOR_REVIEW.md` and METHODOLOGY §47, §49.4, §52.
