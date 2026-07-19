import json, re, os

RAW = json.load(open('/tmp/deq_raw.json'))

def building_codes(name):
    """Pull building codenames out of a DEQ air-site name.

    Two forms appear: space-separated ("IAD-73 IAD-74 IAD-602") and
    slash-continued ("IAD-104/105/106", "IAD-205/307/317/612/612x"), where the
    prefix is stated once and subsequent numbers inherit it.
    """
    codes = []
    for m in re.finditer(r'\b(IAD|DCA|MNZ|NVA|VA)[- ]?(\d+[A-Za-z]?)((?:\s*/\s*\d+[A-Za-z]?)*)', name):
        prefix, first, rest = m.group(1), m.group(2), m.group(3)
        codes.append(f"{prefix}-{first}".upper())
        for tail in re.findall(r'\d+[A-Za-z]?', rest or ''):
            codes.append(f"{prefix}-{tail}".upper())
    return list(dict.fromkeys(codes))

permits = [{**r, "building_codes": building_codes(r["site_name"])} for r in RAW]

os.makedirs('data', exist_ok=True)
json.dump({
    "source": "Virginia DEQ, Issued Air Permits for Data Centers, as of 7/13/2026",
    "source_url": "https://www.deq.virginia.gov/permits/air/issued-air-permits-for-data-centers",
    "retrieved": "2026-07-18",
    "note": (
        "The published DEQ table carries NO generator capacity column -- capacity lives in the "
        "individual permit documents, which are not linked from that page. This file is the key "
        "for that follow-up: registration numbers plus, where the site name discloses them, the "
        "specific building codenames each permit covers. Note that one permit typically covers "
        "SEVERAL buildings, so any capacity obtained from a permit document is a site total that "
        "must be split across the buildings listed here, not assigned to each of them."
    ),
    "permits": permits,
}, open('data/vadeq_air_permits_pwc.json','w'), indent=1)

codes = {c for p in permits for c in p['building_codes']}
print(f"{len(permits)} permits, {len(codes)} distinct building codenames")

# Can these codenames join to our building records?
prof = json.load(open('public/data/facility_profiles.json'))
names = [(b.get('name') or '', b['gpin']) for b in prof['buildings']]
matched, unmatched = [], []
for c in sorted(codes):
    hit = [n for n, g in names if re.search(r'\b' + re.escape(c.replace('-', '[- ]?')) + r'\b', n, re.I)
           or c.replace('-', '') in n.upper().replace('-', '').replace(' ', '')]
    (matched if hit else unmatched).append((c, hit[0] if hit else None))

print(f"joinable to a building record: {len(matched)}/{len(codes)}")
for c, n in matched[:12]:
    print(f"   {c:<10} -> {n}")
print(f"unmatched: {[c for c, _ in unmatched]}")
