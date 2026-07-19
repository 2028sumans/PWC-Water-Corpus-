# Getting per-facility generator capacity — where to go and what to grab

**Why:** the GFA → MW density bridge (`GFA / 8,818`) is the last dominant assumption in the estimator — a **64% swing** in the county total, and the one constant that cannot be repaired by tuning (see [METHODOLOGY.md §7.1b](METHODOLOGY.md)). Per-facility generator capacity retires it, because it is the input ICPRB actually used, run in the direction their Equation 6-3 validates.

Try the routes in this order. The first two are asks for a dataset that already exists; only the third involves reading permits one at a time.

---

## Route 1 — ICPRB (best odds, smallest effort)

They compiled effective power demand per facility for the 2025 WMA study. Asking for their working table skips all permit parsing.

- **Contact page:** https://www.potomacriver.org/about-icprb/contact-us/
- **Staff directory:** https://www.potomacriver.org/about-icprb/staff/
- Phone: 301.984.1908 · 401 N. Washington Street, Ste 300, Rockville, MD 20850

**What to ask for, specifically:** the per-facility table behind **Section 6.2** of the *2025 Washington Metropolitan Area Water Supply Study* — facility name, locality, total backup generator capacity, and the derived **Effective Power Demand** (their Equation 6-3). Mention that the study cites **Seck et al. (in preparation)** for additional methodological detail; that paper's authors are the people who hold the table.

Also worth asking, since it costs nothing extra: **the Prince William Water figure behind the 309 gal/MW/day WUP** — specifically what effective MW they divided 0.42 MGD by, and whether the service-area boundary matches the county. That number is load-bearing and we can't currently reproduce it.

## Route 2 — JLARC

The VADEQ-derived facility database was built by JLARC's consultants for Report 598 and **was never published** — the study page carries seven PDFs and zero data files. So this is a request, not a download.

- **Study landing page:** https://jlarc.virginia.gov/landing-2024-data-centers-in-virginia.asp
- **JLARC FOIA info:** https://jlarc.virginia.gov/pdfs/other/jlarc_foia.pdf

**What to ask for:** the consultant-compiled data center database used in Report 598 — the one with *facility names, operators, addresses, locality, total backup generator power capacity, building size, number of buildings, and land area*. That phrasing is ICPRB's description of it, so quoting it will be recognised.

## Route 3 — DEQ FOIA (the fallback; yields PDFs to parse)

- **FOIA portal:** https://vadeq.nextrequest.com/
- **Check already-released records FIRST — free and instant:** https://vadeq.nextrequest.com/requests
  Since 28 May 2026, fulfilled requests and their records are public and searchable. Someone may already have pulled these.
- **DEQ FOIA page:** https://www.deq.virginia.gov/news-info/freedom-of-information-act
- **Named DEQ data-center contact:** Stanley Faggert (listed on the data-center permits page — worth an email before filing, he may just send them)

**Portal settings:** choose Department = **Northern Regional Office** (all 32 PWC/Manassas permits are Northern). Use Central Office only for a statewide ask.

**Cost:** no charge if the request takes under 30 minutes of staff time; otherwise $53.29/hr non-management. **Name the registration numbers** — a narrow request is far more likely to land under the free threshold than "all data center permits."

**The 32 registration numbers** are in [`data/vadeq_air_permits_pwc.json`](data/vadeq_air_permits_pwc.json), with the building codenames each covers. The highest-value ones (permits covering buildings already in the model):

| Registration | Buildings covered |
|---|---|
| `74081-4` | IAD-73, IAD-74, IAD-602, IAD-193, IAD-194 |
| `74129-3` | IAD-100, IAD-101, IAD-102, IAD-103 |
| `74240-3` | IAD-104, IAD-105, IAD-106 |
| `73741-23` | IAD-7, IAD-11, IAD-24 |
| `73995-5` | IAD-14, IAD-52, IAD-59 |
| `74052-9` | IAD-55, IAD-64, IAD-84 |
| `74115-4` | IAD-75, IAD-85, IAD-95, IAD-96 |
| `74171-4` | IAD-130, IAD-131, IAD-313, DCA-072 |
| `74224-3` | NVA02D (Stack) |
| `74236-1` | MNZ03 (Microsoft Gainesville) |
| `74237-1` | MNZ01 (Microsoft Manassas) |
| `74260-2` | VA10 (NTT Grove at Gainesville) |
| `73180-4` | VA4 (Digital Realty) |

Source table (register numbers, all 198 statewide): https://www.deq.virginia.gov/permits/air/issued-air-permits-for-data-centers
*Note: that page 403s scripted clients — open it in a normal browser.*

---

## What to look for inside a permit document

Air permits are structured similarly. You want the **equipment / emission units table**, usually near the front under a heading like *Facility Information*, *Emission Units*, *Equipment List*, or as **Condition 1**.

**Grab these three things:**

1. **Number of generator units** — e.g. "twenty (20) emergency generators"
2. **Rating per unit** — e.g. "each rated at 3,000 kW" or "2,500 kW (3,353 bhp)"
3. **Whether units are emergency or non-emergency** — newer permits distinguish them; note it, don't filter

**Units:** ratings appear as kW, MW, or brake horsepower. If bhp, convert: **kW = bhp × 0.7457**.

**Site total generator capacity (MW) = count × rating per unit**, summed over all generator groups in the permit.

**Then the conversion the model needs** (ICPRB Equation 6-3):

```
Effective (IT) Power Demand (MW) = total generator capacity (MW) × 0.5 × 0.8
                                 = total generator capacity × 0.4
```

The 0.5 is redundancy (permitted capacity is ~2N, i.e. twice actual IT load); the 0.8 is utilization (data centers don't run at full load continuously, per EPRI 2024).

**Sanity check as you go:** individual data center generators are typically **2–4 MW** each, and Virginia has permitted roughly 9,000 of them statewide. A permit covering four buildings will plausibly list 40–80 units. If you see a rating outside 1–5 MW per unit, re-read the units column.

---

## One trap that will bite if ignored

**A permit covers a SITE, not a building.** Registration `74081-4` covers five buildings. Its generator total is the whole site's — it must be **split across those five**, not assigned to each.

This is the same aggregation error that made interconnection.fyi's operator ranges unusable, one level finer. If capacity is assigned per-building, campus totals inflate by the building count — for the Amazon permits that is a 3–5× overstatement.

The splitting rule isn't obvious either, since buildings differ in size. The most defensible approach is to split **in proportion to each building's GFA**, which uses floor area only to *apportion* a measured site total rather than to *generate* power from scratch — a much weaker use of the number than the current bridge makes.

## What to send back

Any of these works — raw is fine, I'll parse:

- The permit PDFs themselves (name them by registration number if possible)
- A spreadsheet with `registration_no, building_codes, n_generators, kW_each, total_MW`
- Or just the ICPRB/JLARC table if either route pans out — that's the cleanest outcome and skips all of the above

Once the capacity is in, the plan is: add an MW-source precedence (`permit_derived` > `gfa_derived`), report per building which basis was used, and re-run [`sensitivity_analysis.py`](sensitivity_analysis.py) — the density swing should collapse for every facility backed by a real number, the way nuclear fell from 54% to 12% once the USGS data landed.
