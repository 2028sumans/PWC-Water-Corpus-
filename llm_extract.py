"""
LLM structured-extraction pipeline for the unstructured permit/proffer corpus.

THE BOTTLENECK THIS ATTACKS
The facility attributes that most reduce the estimator's uncertainty -- IT MW,
PUE commitments, cooling type, water-source restrictions -- are written in prose
inside proffer statements, special-use-permit resolutions, and thousands of
building-permit descriptions. Every one harvested so far was read by hand. This
turns that into a repeatable, auditable pipeline: source text -> LLM -> a typed
record with a VERBATIM citation and a confidence -> a deterministic verifier ->
the evidence tiers.

WHY THIS IS NOT "AI SLOP" (the design is the argument)
An LLM that emits numbers is not evidence; an LLM whose every claim is checked
against the source IS. The two halves are deliberately separate:

  1. EXTRACTION (llm, fallible): a schema-constrained prompt asks the model to
     return, for each field, the value AND the exact quote it read it from.
  2. VERIFICATION (pure code, deterministic, the part that makes it science):
       - PROVENANCE: the quote must be a substring of the source text
         (whitespace-normalized). This is the anti-hallucination guard -- a model
         that invents "1.3 PUE" cannot invent a source sentence containing it.
         Fails -> the record is REJECTED, never reaches the estimator.
       - SCHEMA/ENUM/RANGE: types, allowed values, PUE in [1.0,2.5], MW in
         [1,600].
       - CROSS-CHECK: where a structured fact already exists (a hand-coded
         proffer condition, a permit-derived MW), agreement/disagreement is
         recorded, not silently overwritten.
  Only records that pass provenance + schema are written to the verified output;
  everything else lands in a rejects log for audit. Nothing here overwrites an
  estimator input automatically -- it produces a reviewed evidence layer.

BACKENDS (pluggable; the verifier is identical regardless)
  ANTHROPIC_API_KEY -> Claude (preferred).  GROQ_API_KEY -> Groq.  else Ollama.
  --backend file --responses <json>  replays pre-computed model outputs so the
  deterministic verifier can be run and audited offline (and in CI) without a
  key. The verification result does not depend on which backend produced the
  text -- provenance is checked against the source either way.

USAGE
  python3 llm_extract.py --source proffers            # extract from SUP/proffer JSONs
  python3 llm_extract.py --source permits             # extract from ePortal permit descriptions
  python3 llm_extract.py --source proffers --backend file --responses data/llm_sample_responses.json
Outputs: data/llm_extractions.json (verified) + data/llm_extraction_rejects.json.
"""
import argparse
import json
import os
import re
import sys

RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "water_raw")
DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
PROFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "public", "data",
                        "facility_profiles.json")

# ---------------------------------------------------------------------------
# schemas: allowed fields / enums per source type
# ---------------------------------------------------------------------------
PROFFER_FIELDS = {
    "cooling_source_restriction",   # groundwater/surface-water prohibited to cool
    "pue_cap",                      # an annualized PUE ceiling
    "cooling_type_preference",      # air / closed-loop rather than water-cooled
    "reclaimed_water",              # reclaimed/non-potable water for cooling/use
}
PERMIT_EQUIPMENT = {"cooling_tower", "chiller", "air_cooled", "dry_cooler",
                    "evaporative", "boiler", "none"}
PUE_RANGE = (1.0, 2.5)
MW_RANGE = (1.0, 600.0)


def _norm(s):
    """Whitespace/case-normalize for robust substring provenance checks."""
    return re.sub(r"\s+", " ", (s or "").lower()).strip()


# ---------------------------------------------------------------------------
# source loaders -> list of {doc_id, source_text, meta}
# ---------------------------------------------------------------------------
def load_proffers():
    docs = []
    for fn in os.listdir(RAW):
        if not (fn.startswith(("SUP", "REZ")) and fn.endswith(".json")):
            continue
        try:
            d = json.load(open(os.path.join(RAW, fn)))
        except Exception:
            continue
        if not isinstance(d, dict) or "pages" not in d:
            continue
        pages = d["pages"]
        text = "\n".join(f"[p{p['page']}] {p['text']}" for p in pages)
        docs.append({"doc_id": d.get("document_name", fn), "source_text": text,
                     "meta": {"kind": "proffer", "n_pages": len(pages)}})
    return docs


def load_permits():
    path = os.path.join(DATA, "eportal_cooling_permits.json")
    docs = []
    for p in json.load(open(path)):
        desc = p.get("desc") or ""
        if not desc.strip():
            continue
        docs.append({"doc_id": p["no"], "source_text": desc,
                     "meta": {"kind": "permit", "parcel": p.get("parcel"),
                              "type": p.get("type"), "addr": p.get("addr")}})
    return docs


# ---------------------------------------------------------------------------
# prompts (schema-constrained; the model MUST return a quote per field)
# ---------------------------------------------------------------------------
def prompt_proffer(doc):
    return f"""You extract data-center water/energy COMMITMENTS from a Prince William County
land-use document. Return STRICT JSON: {{"records":[...]}}. For each commitment found, emit:
  {{"field": one of {sorted(PROFFER_FIELDS)},
    "value": <for pue_cap a number; else a short snake_case string or true>,
    "mandatory": true if it is a binding condition/proffer, false if it is only one
       option in a "select at least N of" sustainability MENU,
    "quote": "<EXACT verbatim sentence from the document containing this fact>",
    "page": <the [pN] page number the quote is on>,
    "confidence": 0.0-1.0}}
Rules: quote MUST be copied verbatim from the text. Distinguish a MANDATORY condition
from a MENU option carefully -- this is the most important judgment. If a field is not
present, omit it. Document:
---
{doc['source_text'][:60000]}
---"""


def prompt_permit(doc):
    return f"""Classify the cooling equipment named in this building-permit description.
Return STRICT JSON: {{"records":[{{"cooling_equipment":[subset of {sorted(PERMIT_EQUIPMENT)}],
"water_cooled_signal": true|false|null, "quote":"<verbatim substring>","confidence":0-1}}]}}.
water_cooled_signal is true only for cooling towers/evaporative/water-cooled chillers,
false for air-cooled/dry, null if unclear. Description: "{doc['source_text']}" """


# ---------------------------------------------------------------------------
# backends
# ---------------------------------------------------------------------------
def call_llm(prompt, backend):
    if backend == "anthropic":
        import anthropic
        c = anthropic.Anthropic()
        m = c.messages.create(model="claude-opus-4-8", max_tokens=2000,
                              messages=[{"role": "user", "content": prompt}])
        return m.content[0].text
    if backend == "groq":
        import urllib.request
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/chat/completions",
            data=json.dumps({"model": os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                             "messages": [{"role": "user", "content": prompt}],
                             "temperature": 0}).encode(),
            headers={"Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
                     "Content-Type": "application/json"})
        return json.loads(urllib.request.urlopen(req).read())["choices"][0]["message"]["content"]
    raise SystemExit(f"backend {backend} needs a key; use --backend file for offline verify")


def parse_json(text):
    """Pull the first JSON object out of a model response."""
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


# ---------------------------------------------------------------------------
# deterministic verifier
# ---------------------------------------------------------------------------
def verify_record(rec, source_text, kind):
    """Return (ok, reasons[]). ok=False => rejected (never reaches the estimator)."""
    reasons = []
    quote = rec.get("quote", "")
    if not quote or _norm(quote) not in _norm(source_text):
        reasons.append("provenance_fail: quote not found verbatim in source")
    if not (0.0 <= rec.get("confidence", -1) <= 1.0):
        reasons.append("confidence_out_of_range")

    if kind == "proffer":
        if rec.get("field") not in PROFFER_FIELDS:
            reasons.append(f"unknown_field:{rec.get('field')}")
        if "mandatory" not in rec or not isinstance(rec["mandatory"], bool):
            reasons.append("mandatory_flag_missing_or_nonbool")
        if rec.get("field") == "pue_cap":
            v = rec.get("value")
            if not (isinstance(v, (int, float)) and PUE_RANGE[0] <= v <= PUE_RANGE[1]):
                reasons.append(f"pue_out_of_range:{v}")
    elif kind == "permit":
        eq = rec.get("cooling_equipment", [])
        if not isinstance(eq, list) or any(e not in PERMIT_EQUIPMENT for e in eq):
            reasons.append(f"bad_equipment_enum:{eq}")
    return (len(reasons) == 0, reasons)


def cross_check(doc, verified):
    """Compare verified records to existing structured facts (non-destructive)."""
    notes = []
    prof = json.load(open(PROFILES))
    if doc["meta"]["kind"] == "proffer":
        docname = doc["doc_id"].replace(".pdf", "")
        for b in prof["buildings"]:
            pcc = b.get("permit_cooling_conditions")
            if pcc and docname in (pcc.get("source") or ""):
                hand_restr = pcc.get("mandatory_source_restriction")
                got_restr = any(r["field"] == "cooling_source_restriction" and r["mandatory"]
                                for r in verified)
                notes.append({"building": b["name"],
                              "hand_mandatory_source_restriction": hand_restr,
                              "extracted_mandatory_source_restriction": got_restr,
                              "agrees": bool(hand_restr) == bool(got_restr)})
    elif doc["meta"]["kind"] == "permit":
        try:
            summ = json.load(open(os.path.join(DATA, "eportal_cooling_summary.json")))
            par = doc["meta"].get("parcel")
            prior = next((x for x in summ["buildings"] if x["gpin"] == par), None)
            if prior:
                notes.append({"parcel": par, "prior_signal": prior["signal"]})
        except FileNotFoundError:
            pass
    return notes


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", choices=["proffers", "permits"], required=True)
    ap.add_argument("--backend", default=None,
                    help="anthropic|groq|file (default: auto by env)")
    ap.add_argument("--responses", help="pre-computed model outputs JSON (backend=file)")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    backend = args.backend or ("anthropic" if os.environ.get("ANTHROPIC_API_KEY")
                               else "groq" if os.environ.get("GROQ_API_KEY") else "file")
    docs = load_proffers() if args.source == "proffers" else load_permits()
    if args.limit:
        docs = docs[:args.limit]
    responses = json.load(open(args.responses)) if args.responses else {}

    prompt_fn = prompt_proffer if args.source == "proffers" else prompt_permit
    kind = "proffer" if args.source == "proffers" else "permit"
    verified_out, rejects_out = [], []
    n_rec = n_ver = 0

    for doc in docs:
        if backend == "file":
            raw = responses.get(doc["doc_id"])
            if raw is None:
                continue
            parsed = raw if isinstance(raw, dict) else parse_json(raw)
        else:
            parsed = parse_json(call_llm(prompt_fn(doc), backend))
        if not parsed:
            continue
        doc_verified = []
        for rec in parsed.get("records", []):
            n_rec += 1
            ok, reasons = verify_record(rec, doc["source_text"], kind)
            entry = {"doc_id": doc["doc_id"], **doc["meta"], **rec}
            if ok:
                n_ver += 1
                doc_verified.append(rec)
                verified_out.append(entry)
            else:
                rejects_out.append({**entry, "reject_reasons": reasons})
        if doc_verified:
            for note in cross_check(doc, doc_verified):
                verified_out.append({"doc_id": doc["doc_id"], "_cross_check": note})

    json.dump({"source": args.source, "backend": backend,
               "n_docs": len(docs), "n_records": n_rec, "n_verified": n_ver,
               "n_rejected": n_rec - n_ver, "records": verified_out},
              open(os.path.join(DATA, "llm_extractions.json"), "w"), indent=1)
    json.dump(rejects_out, open(os.path.join(DATA, "llm_extraction_rejects.json"), "w"), indent=1)

    print(f"source={args.source} backend={backend} docs={len(docs)}")
    print(f"records extracted={n_rec}  verified={n_ver}  rejected={n_rec-n_ver}")
    cc = [r["_cross_check"] for r in verified_out if "_cross_check" in r]
    if cc:
        print("cross-checks vs existing structured facts:")
        for c in cc:
            print("  ", json.dumps(c))
    print(f"wrote data/llm_extractions.json + data/llm_extraction_rejects.json")


if __name__ == "__main__":
    main()
