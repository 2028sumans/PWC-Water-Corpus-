#!/usr/bin/env python3
"""
Build the RAG retrieval index for the Water Atlas memo pipeline.

Reads the 14-doc water policy corpus from data/water_raw/ (7 PDFs + 7
pre-parsed JSONs), chunks at ~500 tokens with 100-token overlap, and writes
a single rag_chunks.json containing:
  - chunks[]:   list of {id, doc_file, doc_title, section, text, tf, n_tokens}
  - meta:       {n_chunks, avg_chunk_len, idf: {token: score}, doc_count}

At query time /api/memo computes BM25 scores in JS using this precomputed
IDF + per-chunk term-frequency bags. No vector DB, no embedding model.

Run: python3 build_rag_index.py
"""
import json
import math
import os
import re
import time
from collections import Counter

import pdfplumber

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("PWC_DATA_ROOT", os.path.join(_SCRIPT_DIR, "data", "water_raw"))
OUT_PATH = os.environ.get("VIRA_RAG_OUT", os.path.join(_SCRIPT_DIR, "public", "data", "rag_chunks.json"))

CHUNK_TOKENS = 500
OVERLAP_TOKENS = 100

STOPWORDS = set("""
a an the and or but if then else of in on at to for from with without by as is are was were be been being
have has had do does did this that these those it its their there here which who what when where how why
i you he she we they me him her us them my your our his hers theirs all any each every some such no not
""".split())

# The 14-document water policy corpus. PDFs get page-by-page text extraction
# (pdfplumber); JSONs are pre-parsed {"pages": [...]}/{"sections": [...]}
# documents already in the same shape Vira's corpus used.
RAG_DOCS = [
    "Rpt598.pdf",
    "2025_WMA_Water_Supply_Study_ICPRB_Dec-2025.pdf",
    "ICPRB.DataCentersandWaterUse.ICPRB_.March2026.pdf",
    "Dominion_GS-5_LargeLoad_RateClass.pdf",
    "LBNL_QueuedUp_2025.pdf",
    "Dominion_LargeLoad_SCC_PUR-2026-00011.pdf",
    # REMOVED 2026-08-03: "EconBulletin_LaunchCost_2022.pdf" -- Adilov et al. (2022),
    # "An analysis of launch cost reductions for low Earth orbit satellites",
    # Economics Bulletin 42(3):1561-1574. Per-kilogram satellite launch costs,
    # 2000-2020. Nothing to do with water, data centers, Virginia or electricity;
    # it was indexed by mistake and the assistant could retrieve satellite launch
    # economics when answering questions about data-center water. No computed
    # number depends on it. See READING_LOG Part 4 / 18.4.
    "prince_william_cesmp_full.json",
    "Res No 20-773 Climate Mitigation and Resiliency Goals.json",
    "FY2026 Application Package for Special Use Permits.pdf.json",
    "PP-AddressValidationRequirements.json",
    "PP-NewStructure-DataCenterBuildings.json",
    "SUP2025-00016.json",
    "Reference Manual for Rezoning, Special Use Permit, and Proffer Amendment Applications.json",
    # pjm_load_report_full.json turned out to be a page-structured narrative
    # PJM load report (same {"pages": [...]} shape as the other JSON docs
    # here), not tabular data — it was originally slated for structured
    # extraction into scoring fields, but there's nothing to extract; it
    # belongs in the RAG corpus instead, where its actual content (grid
    # load growth narrative) is retrievable for memo generation.
    "pjm_load_report_full.json",
]


def t(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def tokenize(text: str) -> list[str]:
    """Lowercase + split on non-alphanumeric, preserving hyphens (M-2) and §."""
    text = text.replace("§", "section ")
    raw = re.findall(r"[a-z0-9][a-z0-9\-]*[a-z0-9]|[a-z0-9]", text.lower())
    out = []
    for tok in raw:
        if len(tok) < 2 or len(tok) > 40:
            continue
        if tok in STOPWORDS:
            continue
        out.append(tok)
    return out


def flatten_pdf(path: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Extract page text from a PDF via pdfplumber."""
    file_name = os.path.basename(path)
    title = os.path.splitext(file_name)[0].replace("_", " ").replace(".", " ").strip()
    units: list[tuple[str, str]] = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            txt = (page.extract_text() or "").strip()
            if txt:
                units.append((f"page {i}", txt))
    return file_name, title, units


def flatten_json(path: str) -> tuple[str, str, list[tuple[str, str]]]:
    """Vira-format policy JSON: {"pages": [...]}/{"sections": [...]}."""
    with open(path) as f:
        d = json.load(f)
    title = d.get("document_name") or d.get("document_title") or os.path.basename(path)
    file_name = os.path.basename(path)
    units: list[tuple[str, str]] = []
    if "pages" in d:
        for p in d["pages"]:
            if not isinstance(p, dict):
                continue
            n = p.get("page", p.get("page_number"))
            txt = p.get("text", "").strip()
            if txt:
                units.append((f"page {n}", txt))
    elif "sections" in d:
        for s in d["sections"]:
            if not isinstance(s, dict):
                continue
            sid = s.get("section_id", "")
            heading = s.get("heading", "")
            label = f"§{sid} {heading}".strip()
            txt = s.get("text", "").strip()
            if txt:
                units.append((label, txt))
    return file_name, title, units


def chunk_text(tokens: list[str], target: int = CHUNK_TOKENS, overlap: int = OVERLAP_TOKENS) -> list[list[str]]:
    if len(tokens) <= target:
        return [tokens]
    step = target - overlap
    chunks = []
    i = 0
    while i < len(tokens):
        chunk = tokens[i: i + target]
        if len(chunk) < overlap and i > 0:
            break
        chunks.append(chunk)
        i += step
    return chunks


def main() -> None:
    t(f"Loading {len(RAG_DOCS)}-doc water policy corpus from {DATA_ROOT}")

    all_chunks: list[dict] = []
    chunk_id = 0
    for fn in RAG_DOCS:
        path = os.path.join(DATA_ROOT, fn)
        if not os.path.exists(path):
            t(f"  SKIP {fn}: not found")
            continue
        if fn.lower().endswith(".pdf"):
            file_name, title, units = flatten_pdf(path)
        else:
            file_name, title, units = flatten_json(path)
        n_chunks_doc = 0
        for section_label, raw_text in units:
            tokens = tokenize(raw_text)
            if not tokens:
                continue
            for chunk_tokens in chunk_text(tokens):
                all_chunks.append({
                    "id": chunk_id,
                    "doc_file": file_name,
                    "doc_title": title,
                    "section": section_label,
                    "text": " ".join(chunk_tokens),
                    "tokens": chunk_tokens,
                    "n_tokens": len(chunk_tokens),
                })
                chunk_id += 1
                n_chunks_doc += 1
        t(f"  {fn}: {len(units)} pages/sections -> {n_chunks_doc} chunks")

    t(f"Built {len(all_chunks):,} chunks total (avg {sum(c['n_tokens'] for c in all_chunks) // max(1, len(all_chunks))} tokens/chunk)")

    doc_count = len(all_chunks)
    df: Counter = Counter()
    for c in all_chunks:
        for tok in set(c["tokens"]):
            df[tok] += 1

    idf: dict[str, float] = {}
    for tok, freq in df.items():
        idf[tok] = math.log((doc_count - freq + 0.5) / (freq + 0.5) + 1)

    avg_chunk_len = sum(c["n_tokens"] for c in all_chunks) / max(1, doc_count)
    t(f"  vocabulary: {len(idf):,} unique tokens · avg chunk len: {avg_chunk_len:.1f}")

    for c in all_chunks:
        tf = Counter(c["tokens"])
        c["tf"] = dict(tf)
        del c["tokens"]

    out = {
        "meta": {
            "n_chunks": doc_count,
            "n_docs": len(RAG_DOCS),
            "avg_chunk_len": avg_chunk_len,
            "idf": idf,
            "bm25_k1": 1.5,
            "bm25_b": 0.75,
            "built_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "chunks": all_chunks,
    }

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    size_mb = os.path.getsize(OUT_PATH) / 1024 / 1024
    t(f"  wrote {OUT_PATH} ({size_mb:.1f} MB)")
    t("DONE.")


if __name__ == "__main__":
    main()
