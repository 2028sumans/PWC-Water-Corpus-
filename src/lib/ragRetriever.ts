/**
 * BM25 retriever over the precomputed RAG chunk index.
 *
 * Why BM25 (not embeddings) for this corpus: the 22 PWC policy docs use
 * exact technical terminology (M-2, §32-509, DCOOD, SUP2025-00016). BM25
 * nails these matches; semantic embeddings would need fine-tuning to
 * outperform on legal text at this scale. Total runtime cost: <5 ms per
 * query against ~1,500 chunks. Zero extra storage.
 *
 * Hot path runs server-side in the /api/memo route. The chunk index is
 * loaded once on first call and cached in module memory.
 */
import fs from "node:fs";
import path from "node:path";

export interface RagChunk {
  id: number;
  doc_file: string;
  doc_title: string;
  section: string;
  text: string;
  tf: Record<string, number>;
  n_tokens: number;
}

interface RagIndex {
  meta: {
    n_chunks: number;
    n_docs: number;
    avg_chunk_len: number;
    idf: Record<string, number>;
    bm25_k1: number;
    bm25_b: number;
    built_at: string;
  };
  chunks: RagChunk[];
}

let _cache: RagIndex | null = null;
const STOPWORDS = new Set(
  "a an the and or but if then else of in on at to for from with without by as is are was were be been being have has had do does did this that these those it its their there here which who what when where how why i you he she we they me him her us them my your our his hers theirs all any each every some such no not".split(
    " ",
  ),
);

function tokenize(text: string): string[] {
  // Mirror the Python tokenizer in build_rag_index.py exactly so the query
  // tokens line up with the indexed tokens. §-handling + hyphen preservation
  // are what make BM25 over zoning text actually work.
  const t = text.replace(/§/g, "section ").toLowerCase();
  const raw = t.match(/[a-z0-9][a-z0-9\-]*[a-z0-9]|[a-z0-9]/g) ?? [];
  const out: string[] = [];
  for (const tok of raw) {
    if (tok.length < 2 || tok.length > 40) continue;
    if (STOPWORDS.has(tok)) continue;
    out.push(tok);
  }
  return out;
}

function loadIndex(): RagIndex {
  if (_cache) return _cache;
  const p = path.join(process.cwd(), "public", "data", "rag_chunks.json");
  const raw = fs.readFileSync(p, "utf8");
  _cache = JSON.parse(raw) as RagIndex;
  return _cache;
}

/**
 * Score every chunk against the query tokens using BM25+. Returns top-K
 * chunks with their scores, sorted descending. Empty array if no chunks
 * matched at all (very rare in practice — the corpus is broad).
 *
 * The `maxPerDoc` parameter caps how many chunks any single source file
 * can contribute. Without it, a long doc like the 73-page Hornbaker SUP
 * file dominates retrieval for any Hornbaker-adjacent question, starving
 * the LLM of Comp Plan / PJM / climate / methodology context. Default 2
 * forces useful breadth for memo/counter modes; pass a large value (or 0)
 * to disable for pure QA where the question dictates one source naturally.
 */
/**
 * Doc files that are part of the corpus but should NEVER appear as a memo
 * citation. These are self-referential / internal docs — citing them is
 * meta-noise ("our memo says X because our methodology says X is good"),
 * not the external authority an analyst wants to verify against.
 */
const NON_CITABLE_DOC_FILES = new Set([
  "vira_methodology.json",
]);

export function retrieveTopChunks(
  query: string,
  k: number = 10,
  maxPerDoc: number = 2,
): Array<{ chunk: RagChunk; score: number }> {
  const index = loadIndex();
  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) return [];

  const k1 = index.meta.bm25_k1;
  const b = index.meta.bm25_b;
  const avgLen = index.meta.avg_chunk_len;
  const idf = index.meta.idf;

  // De-dupe query tokens; if a query has "data center data center" the IDF
  // already captures it. Helps small bias toward distinctive tokens.
  const uniqQ = Array.from(new Set(queryTokens));

  const scored: Array<{ chunk: RagChunk; score: number }> = [];
  for (const chunk of index.chunks) {
    // Skip self-referential / non-citable docs so they never make it into
    // either the LLM prompt or the citation appendix.
    if (NON_CITABLE_DOC_FILES.has(chunk.doc_file)) continue;
    const lenNorm = 1 - b + b * (chunk.n_tokens / avgLen);
    let score = 0;
    for (const qt of uniqQ) {
      const tf = chunk.tf[qt];
      if (!tf) continue;
      const idfScore = idf[qt] ?? 0;
      if (idfScore <= 0) continue;
      // BM25 saturation curve: more occurrences help but with diminishing returns.
      const numerator = tf * (k1 + 1);
      const denominator = tf + k1 * lenNorm;
      score += idfScore * (numerator / denominator);
    }
    if (score > 0) scored.push({ chunk, score });
  }

  scored.sort((a, b) => b.score - a.score);

  // If diversification disabled (maxPerDoc <= 0), return raw top-K.
  if (maxPerDoc <= 0) return scored.slice(0, k);

  // Walk the sorted list, taking each chunk only if its doc_file still has
  // budget. This is a single-pass O(N) version of the round-robin diversity
  // strategy: highest-relevance chunks win when there's budget, but any one
  // doc tops out at `maxPerDoc`. If we run out of budget but still need more
  // chunks to hit K, fall through with a second pass that ignores the cap.
  const perDoc = new Map<string, number>();
  const picked: Array<{ chunk: RagChunk; score: number }> = [];
  for (const r of scored) {
    if (picked.length >= k) break;
    const used = perDoc.get(r.chunk.doc_file) ?? 0;
    if (used >= maxPerDoc) continue;
    perDoc.set(r.chunk.doc_file, used + 1);
    picked.push(r);
  }
  // Backfill if diversification was too aggressive (e.g., only 3 docs matched)
  if (picked.length < k) {
    const pickedSet = new Set(picked.map((p) => p.chunk.id));
    for (const r of scored) {
      if (picked.length >= k) break;
      if (pickedSet.has(r.chunk.id)) continue;
      picked.push(r);
    }
  }
  return picked;
}

/** Convenience: format a chunk for inclusion in an LLM prompt. */
export function formatChunkForPrompt(chunk: RagChunk, score?: number): string {
  const scoreTag = score !== undefined ? ` (relevance ${score.toFixed(2)})` : "";
  return `[${chunk.id}] ${chunk.doc_title} — ${chunk.section}${scoreTag}\n${chunk.text}`;
}
