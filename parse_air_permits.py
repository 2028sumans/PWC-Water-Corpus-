"""
Extract per-site backup generator capacity from VADEQ air permit documents.

This is the input that retires the GFA -> MW density bridge -- the last dominant
assumption in the estimator (64% of the variance in the county total). Permits
give generator capacity per SITE, which ICPRB's Equation 6-3 converts to
effective IT power:

    Effective (IT) Power Demand = Total Generator Capacity x 0.5 x 0.8

The 0.5 is redundancy (permitted capacity is ~2N, i.e. twice actual IT load);
the 0.8 is utilization (data centers do not run at full load continuously).

WHY THE PARSER IS DEFENSIVE
---------------------------
Permit layout is not standardised across two decades of issuance:

  - Ratings appear as "2,750 kW", "1,000 ekW", "1500 ekW" (no comma), and are
    usually paired with a bhp figure that must NOT be double-counted.
  - Counts appear as "Twenty-two (22)", "Eight (8)", or a bare "(13)".
  - Older scanned permits are OCR'd badly: "Fnumment to be Constructed",
    "Eaumment Dermitted prior to the date of this permit".
  - Permits list non-generator equipment too (natural gas heaters rated in
    MMBtu/hr) which must be excluded.
  - pdftotext scrambles multi-column table rows, so a rating and its count can
    land several lines apart.

Rather than silently guessing, every row records the confidence basis and the
raw source line. Rows outside a plausible per-unit band are flagged, not
dropped, so they can be checked by eye against the PDF.
"""
import json
import os
import re
import sys

# Per-unit sanity band. Data center gen-sets run roughly 0.6-4 MW; anything
# outside this is far more likely a parsing error than a real machine.
MIN_UNIT_KW = 400
MAX_UNIT_KW = 5000

REDUNDANCY = 0.5
UTILIZATION = 0.8

SECTION_PATTERNS = [
    # (regex, canonical section) -- tolerant of the OCR mangling seen in older permits
    (re.compile(r'to\s+be\s+construct', re.I), "to_be_constructed"),
    (re.compile(r'previously\s+permitted|permitted\s+prior|D?ermitted\s+prior', re.I), "previously_permitted"),
    (re.compile(r'transitory', re.I), "transitory"),
]

# "2,750 kW" / "1,000 ekW" / "1500 ekW" / "3,000 kWe". Excludes bhp by requiring
# the kW unit, which always accompanies the bhp figure on the same row.
RATING_RE = re.compile(r'([\d,]{3,7})\s*(?:e?kW|kWe)\b', re.I)
# "Twenty-two (22)" or a bare "(13)"
COUNT_RE = re.compile(r'\((\d{1,3})\)')
# Equipment we must not count as generators
NON_GENSET_RE = re.compile(r'MMBtu|Btu/hr|heating unit|water heater|space heater|boiler|cooling tower|storage tank', re.I)

# Older permits spell counts out with no digits at all -- "Three Caterpillar
# model 3516B ... 2000 ekW, each". Without this the row parses as a single unit
# and the site reads 3x low.
_ONES = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
         "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
         "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18,
         "nineteen": 19}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
         "seventy": 70, "eighty": 80, "ninety": 90}
WORD_COUNT_RE = re.compile(
    r'\b((?:' + "|".join(_TENS) + r')(?:[-\s](?:' + "|".join(_ONES) + r'))?|(?:' + "|".join(_ONES) + r'))\b',
    re.I)


def word_to_int(s):
    s = s.lower().replace("-", " ").strip()
    parts = s.split()
    if len(parts) == 2 and parts[0] in _TENS and parts[1] in _ONES:
        return _TENS[parts[0]] + _ONES[parts[1]]
    if len(parts) == 1:
        return _TENS.get(parts[0]) or _ONES.get(parts[0])
    return None


def _int(s):
    return int(str(s).replace(",", ""))


def equipment_section(lines):
    """Return only the index range covering equipment tables.

    Ratings also appear in permit CONDITIONS ("operating at >=90 percent of
    their rated capacity (3,000 ekW)"), which are not equipment and would be
    counted twice. Bounding the scan to the equipment list removes them.
    """
    start = None
    for i, l in enumerate(lines):
        if re.search(r'Equipment\s+List|F\w+ment\s+to\s+be', l, re.I):
            start = i
            break
    if start is None:
        return 0, len(lines)
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if re.search(r'Specifications\s+included|do\s+not\s+form\s+enforceable', lines[j], re.I):
            end = j
            break
    return start, end


def find_section(line, current):
    for rx, name in SECTION_PATTERNS:
        if rx.search(line):
            return name
    return current


def parse_permit(path):
    """Parse one permit's equipment list into gen-set rows."""
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")

    reg = None
    m = re.search(r'Registration\s+N(?:o|umber)[.:]*\s*([\d]+)', "\n".join(lines), re.I)
    if m:
        reg = m.group(1)

    loc = None
    m = re.search(r'Location:\s*(.+)', "\n".join(lines))
    if m:
        loc = m.group(1).strip()

    # Building codenames disclosed in the document (the cover letter usually
    # names the data centers a permit covers).
    #
    # "VA" is dangerous here: Virginia ZIP codes and state-abbreviated addresses
    # ("Herndon, VA 20171", "Richmond, VA 23218") match a naive pattern and
    # polluted the first run with VA-20171, VA-23218, VA-22193 on every permit.
    # Real building codes are 1-2 digits (VA4, VA10), so 3+ digit VA matches are
    # rejected outright.
    codes = []
    for mm in re.finditer(r'\b(IAD|DCA|MNZ|NVA|VA)[- ]?(\d+[A-Za-z]?)((?:\s*/\s*\d+[A-Za-z]?)*)', "\n".join(lines)):
        p, f, rest = mm.group(1), mm.group(2), mm.group(3)
        if p.upper() == "VA" and len(re.sub(r'\D', '', f)) > 2:
            continue                      # ZIP code or street number, not a building
        codes.append(f"{p}-{f}".upper())
        for t in re.findall(r'\d+[A-Za-z]?', rest or ''):
            if p.upper() == "VA" and len(re.sub(r'\D', '', t)) > 2:
                continue
            codes.append(f"{p}-{t}".upper())
    codes = list(dict.fromkeys(codes))

    rows = []
    section = None
    sec_start, sec_end = equipment_section(lines)
    for i in range(sec_start, sec_end):
        # Older permits wrap a single table cell across lines, splitting the
        # value from its unit: "... horsepower or 2000" / "ekW, each". Matching
        # on the line alone misses these entirely (permit 73200 read as zero
        # generators).
        #
        # The join must be NARROW. Joining every line with its successor and
        # matching the result double-counted every rating in the corpus -- once
        # via the joined probe at line i, then again on its own line at i+1,
        # inflating a hand-verified 287 MW site to 574 MW. So the join only
        # applies when the number genuinely dangles at the end of this line and
        # the unit genuinely opens the next.
        line = lines[i]
        probe = line
        if i + 1 < sec_end and re.search(r'[\d,]{3,7}\s*$', line) and re.match(r'\s*(?:e?kW|kWe)\b', lines[i + 1], re.I):
            probe = line + " " + lines[i + 1]
        section = find_section(line, section)

        for rm in RATING_RE.finditer(probe):
            kw = _int(rm.group(1))

            # Window around the rating: table rows get split across lines by
            # pdftotext, so the count and description may not share a line.
            lo, hi = max(sec_start, i - 6), min(sec_end, i + 4)
            window = " ".join(lines[lo:hi])

            if NON_GENSET_RE.search(window):
                continue

            # Prefer a parenthesised count nearest the rating line.
            best, best_d = None, 1e9
            for j in range(lo, hi):
                for cm in COUNT_RE.finditer(lines[j]):
                    d = abs(j - i)
                    if d < best_d:
                        best, best_d = _int(cm.group(1)), d
            if best is not None:
                n, basis = best, "count_in_window"
            else:
                # Fall back to a spelled-out count ("Three Caterpillar ...").
                wn, wd = None, 1e9
                for j in range(lo, hi):
                    for wm in WORD_COUNT_RE.finditer(lines[j]):
                        v = word_to_int(wm.group(1))
                        d = abs(j - i)
                        if v and d < wd:
                            wn, wd = v, d
                if wn:
                    n, basis = wn, "spelled_count"
                else:
                    n, basis = 1, "assumed_single"

            flags = []
            if not (MIN_UNIT_KW <= kw <= MAX_UNIT_KW):
                flags.append("unit_kw_out_of_band")
            if basis == "assumed_single":
                flags.append("no_explicit_count")
            if section is None:
                flags.append("no_section_header")

            rows.append({
                "section": section or "unknown",
                "n_units": n,
                "kw_each": kw,
                "mw": round(n * kw / 1000, 3),
                "basis": basis,
                "flags": flags,
                "source_line": line.strip()[:150],
            })

    # NO de-duplication on (section, count, rating).
    #
    # An earlier version deduped on that key to guard against a rating being
    # listed twice. It silently destroyed real data: permit 72374 lists two
    # separate 1,500 ekW gen-sets as reference numbers 3 and 4, identical in
    # every parsed field, and the dedup collapsed them into one -- halving the
    # site. Distinct table rows with identical specifications are the norm, not
    # an error. Double-counting is instead prevented structurally, by bounding
    # the scan to the equipment section (see equipment_section) so that ratings
    # quoted in permit conditions are never reached.
    deduped = rows

    return {
        "file": os.path.basename(path),
        "registration_no": reg,
        "location": loc,
        "building_codes": codes,
        "rows": deduped,
    }


def detect_alternative_models(rows):
    """Spot rows offering ALTERNATIVE engine models for the same physical units.

    Permit 74262 lists a group of 60 gen-sets twice -- once at 3,000 ekW and
    once at 3,250 ekW for a different manufacturer's engine, with a condition
    elsewhere limiting output to 3,000. Summing both counts the same 60 machines
    twice and inflated that site to 1,539 MW, three times the next largest in
    the county. Any permit where one unit count recurs with several distinct
    ratings is therefore not safe to total automatically.
    """
    by_count = {}
    for r in rows:
        by_count.setdefault(r["n_units"], set()).add(r["kw_each"])
    return sorted(n for n, kws in by_count.items() if n >= 2 and len(kws) > 1)


def summarise(p):
    by_section = {}
    for r in p["rows"]:
        by_section.setdefault(r["section"], 0.0)
        by_section[r["section"]] += r["mw"]
    total = sum(by_section.values())
    permanent = total - by_section.get("transitory", 0.0)
    p["mw_by_section"] = {k: round(v, 2) for k, v in by_section.items()}
    p["total_generator_mw"] = round(total, 2)
    p["permanent_generator_mw"] = round(permanent, 2)
    p["effective_it_mw"] = round(permanent * REDUNDANCY * UTILIZATION, 2)
    p["n_units"] = sum(r["n_units"] for r in p["rows"])
    p["flagged_rows"] = sum(1 for r in p["rows"] if r["flags"])

    alt = detect_alternative_models(p["rows"])
    reasons = []
    if alt:
        reasons.append(f"alternative_engine_models(counts={alt})")
    if p["flagged_rows"]:
        reasons.append(f"{p['flagged_rows']}_flagged_rows")
    if not p["rows"]:
        reasons.append("no_equipment_rows_parsed")
    # A site whose mean unit is outside the physical band for data centre
    # gen-sets is a parsing artefact, not a machine.
    if p["n_units"]:
        mean_kw = p["total_generator_mw"] * 1000 / p["n_units"]
        if not (MIN_UNIT_KW <= mean_kw <= MAX_UNIT_KW):
            reasons.append(f"mean_unit_{mean_kw:.0f}kW_out_of_band")

    p["confidence"] = "high" if not reasons else "needs_review"
    p["review_reasons"] = reasons
    return p


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else "."
    out = []
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".txt"):
            continue
        out.append(summarise(parse_permit(os.path.join(d, fn))))

    # Collapse duplicate downloads of the same registration, keeping the one
    # with the most extracted capacity (usually the latest amendment).
    best = {}
    for p in out:
        k = p["registration_no"]
        if k not in best or p["total_generator_mw"] > best[k]["total_generator_mw"]:
            best[k] = p
    out = sorted(best.values(), key=lambda p: -(p["total_generator_mw"] or 0))

    hi = [p for p in out if p["confidence"] == "high"]
    lo = [p for p in out if p["confidence"] != "high"]

    print(f"USABLE ({len(hi)} permits)\n")
    print(f"{'reg':<8}{'units':>6}{'total MW':>10}{'eff IT MW':>11}   buildings")
    print("-" * 92)
    for p in hi:
        codes = ",".join(p["building_codes"][:5]) or "(none named)"
        print(f"{p['registration_no']:<8}{p['n_units']:>6}{p['total_generator_mw']:>10.1f}"
              f"{p['effective_it_mw']:>11.1f}   {codes}")
    print(f"\n  subtotal: {sum(p['total_generator_mw'] for p in hi):,.0f} MW generator, "
          f"{sum(p['effective_it_mw'] for p in hi):,.0f} MW effective IT")

    print(f"\n\nNEEDS REVIEW ({len(lo)} permits) -- excluded from any total\n")
    print(f"{'reg':<8}{'units':>6}{'total MW':>10}   reasons")
    print("-" * 92)
    for p in lo:
        print(f"{p['registration_no']:<8}{p['n_units']:>6}{p['total_generator_mw']:>10.1f}   {'; '.join(p['review_reasons'])}")

    json.dump(out, open("permit_capacity.json", "w"), indent=1)
    print(f"\n{len(out)} distinct permits -> permit_capacity.json")
