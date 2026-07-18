/**
 * Memo generation endpoint. Three modes:
 *   - "memo":    water-legibility narrative (observable / inferable /
 *                unresolved taxonomy for this parcel's water relationship
 *                to data-center infrastructure)
 *   - "counter": adversarial "what's unresolved" — same RAG, flipped framing
 *   - "qa":      free-form question against the parcel + corpus
 *
 * Architecture: BM25 retrieves top-K chunks from /data/rag_chunks.json,
 * we build a structured prompt with the parcel context + retrieved chunks,
 * stream the response back to the client via SSE-style text/event-stream.
 *
 * Backend selection (set via env, priority order):
 *   1. GROQ_API_KEY → Groq Cloud (default, FREE tier no card, fastest).
 *      Llama 3.3 70B Versatile via OpenAI-compatible SSE.
 *   2. TOGETHER_API_KEY → Together AI ($5 signup credit, then paid).
 *   3. Otherwise → local Ollama at OLLAMA_HOST.
 */
import { type NextRequest } from "next/server";
import { retrieveTopChunks, formatChunkForPrompt, type RagChunk } from "@/lib/ragRetriever";

// --- Backend config (Groq → Together → Ollama priority chain) --------------
const GROQ_API_KEY = process.env.GROQ_API_KEY ?? "";
const GROQ_MODEL = process.env.GROQ_MODEL ?? "llama-3.3-70b-versatile";
const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";

const TOGETHER_API_KEY = process.env.TOGETHER_API_KEY ?? "";
const TOGETHER_MODEL = process.env.TOGETHER_MODEL ?? "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free";
const TOGETHER_URL = "https://api.together.xyz/v1/chat/completions";

const OLLAMA_HOST = process.env.OLLAMA_HOST ?? "http://localhost:11434";
const OLLAMA_MODEL = process.env.OLLAMA_MODEL ?? "qwen2.5:7b-instruct-q4_K_M";

type Backend = "groq" | "together" | "ollama";
const BACKEND: Backend = GROQ_API_KEY ? "groq" : TOGETHER_API_KEY ? "together" : "ollama";

type Mode = "memo" | "counter" | "qa" | "verdict";

interface SensitivityThresholdPayload {
  id: string;
  subScore: string;
  currentScore: number;
  targetScore: number;
  lever: string;
  currentValue: string;
  targetValue: string;
  byYear: number | null;
  rationale: string;
  source: string;
  pointsRecovered: number;
  plausibility: "high" | "medium" | "low";
}

interface MemoRequest {
  gpin: string;
  mode: Mode;
  parcelContext: {
    address?: string;
    acres: number;
    zoning?: string | null;
    watershed?: string | null;
    hasNpdes?: 0 | 1;
    inDcBuilding?: 0 | 1;
    inDcCampus?: 0 | 1;
    nDcBuildings?: number;
    waterLegibility: number;
    dataDepth: number;
    /** Per-sub-score breakdown */
    subScores?: Record<string, number>;
    /** Free-text summary of badges/flags */
    flags?: string[];
  };
  sensitivity?: SensitivityThresholdPayload[];
  question?: string;
}

function parcelContextBlock(ctx: MemoRequest["parcelContext"]): string {
  const lines: string[] = [];
  if (ctx.address) lines.push(`Address: ${ctx.address}`);
  lines.push(`Acreage: ${ctx.acres.toFixed(2)} acres`);
  lines.push(`Zoning: ${ctx.zoning ?? "—"}`);
  if (ctx.watershed) lines.push(`Watershed: ${ctx.watershed}`);
  if (ctx.inDcBuilding) {
    const n = ctx.nDcBuildings ?? 1;
    lines.push(`Data center building(s) on parcel: ${n}.`);
    lines.push(
      ctx.hasNpdes
        ? "NPDES water discharge permit: ON FILE — this is one of only a handful of data centers in Virginia with a federal water discharge permit."
        : "NPDES water discharge permit: NONE ON RECORD — this is the norm, not the exception. Data centers consume water primarily via evaporative cooling loss from municipal supply, which the NPDES surface-discharge regime does not capture.",
    );
  } else if (ctx.inDcCampus) {
    lines.push("Inside a planned/under-construction data center campus footprint — no building placed on this specific parcel yet.");
  }
  lines.push(`Water Legibility Score: ${ctx.waterLegibility}/100 (Data Depth ${ctx.dataDepth}/100)`);
  if (ctx.subScores) {
    const subs = Object.entries(ctx.subScores).map(([k, v]) => `${k}=${v}`).join(", ");
    lines.push(`Sub-scores (0-100): ${subs}`);
  }
  if (ctx.flags && ctx.flags.length) {
    lines.push(`Flags: ${ctx.flags.join(", ")}`);
  }
  return lines.join("\n");
}

// Domain knowledge primer prepended to every system prompt.
const DOMAIN_PRIMER = `Domain knowledge you MUST treat as authoritative:

KEY EMPIRICAL FINDING: 203 data center buildings exist in Prince William County, but ZERO hold NPDES (National Pollutant Discharge Elimination System) water discharge permits. This is not evidence of good environmental performance — it means the primary federal water disclosure regime structurally cannot see them, because data centers consume water primarily via evaporative cooling loss from municipal supply, not surface discharge. NPDES only regulates discharge, not consumption. A parcel with "no NPDES permit" is therefore DARK, not clean.

OBSERVABLE / INFERABLE / UNRESOLVED taxonomy — every claim about a parcel's water relationship falls into one of three buckets:
- OBSERVABLE: directly present in an institutional record (NPDES permit status, DEQ permit, watershed membership, stormwater infrastructure, dam-break hazard classification).
- INFERABLE: recoverable from a public proxy (Palmer drought indices as a countywide stress signal, cooling-degree-days as a demand proxy, PW Water's disclosed percentage of peak demand attributable to data centers).
- UNRESOLVED: dark under current disclosure — actual water consumption per facility, actual withdrawal volumes, actual return-flow characteristics. This is the largest bucket for data center parcels specifically.

Watershed Vulnerability: higher score = more vulnerable (cumulative stress from multiple data centers sharing a small basin, worsened by drought).
Facility–Water Proximity: higher score = more water-proximate risk (closer to streams/springs/RPA, especially when a built data center is nearby).
Drought Exposure: countywide Palmer drought index severity — same for every parcel, because that is honestly what the data supports (no parcel-level drought data exists).
Disclosure Legibility: higher score = MORE legible / better disclosed. This is the inverse of "risk" — a parcel with an NPDES permit is MORE legible, not more dangerous. A built data center with no NPDES coverage scores near zero here specifically because almost nothing about its water use is disclosed.
Community Observation Density: higher score = more independent monitoring coverage (WQP/DEQ stations, iNaturalist observations) nearby — a proxy for how quickly an anomaly would be noticed.
Municipal Supply Headroom: higher score = more slack in the utility's peak capacity relative to data-center draw — countywide constant from Prince William Water's own disclosure.
Stormwater Burden: higher score = more stormwater infrastructure burden (segments, detention basins, structures, dam-break hazard, impervious cover).

NEVER frame "no NPDES permit" as good news. Never invent a specific water-consumption number for any facility — none is disclosed. Assess, don't advocate.

GOLDEN RULE: the headline Water Legibility Score always equals the weighted sum of the visible sub-score bars. There are no hidden adjustments.`;

const SYSTEM_PROMPTS: Record<Mode, string> = {
  memo: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia. You assess what is knowable about each parcel's water relationship to data center development from public data. You categorize each attribute as observable (directly present in institutional records), inferable (recoverable from public proxies), or unresolved (dark under current disclosure). Use the retrieved policy documents to ground your analysis. Be neutral — assess, don't advocate.

${DOMAIN_PRIMER}

Generate a water-legibility narrative for the parcel described below.

Output structure (use these exact headers):
  Executive Summary
  Site & Watershed Context
  Disclosure Status
  What's Observable
  What's Inferable
  What's Unresolved
  Recommendation for Further Diligence

Rules:
- Cite every factual claim with [N] where N is a chunk ID from the retrieved context.
- If you cannot cite a source for a claim, omit the claim.
- Use the parcel's actual attributes verbatim.
- Total length: 500-800 words. No fluff.`,
  counter: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia, writing the adversarial "what's unresolved" companion to the main memo.

${DOMAIN_PRIMER}

Identify the 3-5 most significant unresolved or dark aspects of this parcel's water relationship to data-center infrastructure.

Output structure:
  Top Unresolved Questions (3-5 enumerated, ranked by significance)
  Disclosure Gaps (what regulatory regime SHOULD but doesn't capture this)
  What Would Resolve This — REQUIRED to integrate the sensitivity thresholds listed under "SENSITIVITY THRESHOLDS" using their [S#] markers (e.g. [S1], [S2]). Lead with the highest-plausibility lever.
  Verdict (one paragraph: how legible is this parcel's actual water footprint, honestly?)

Rules:
- Cite every policy/document claim with [N] for chunk ID.
- Cite every sensitivity threshold with its [S#] marker — do NOT invent numbers; use the supplied current/target values verbatim.
- Be rigorous but honest — surface what genuinely cannot be known from public data today.
- Total length: 400-600 words.`,
  qa: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia.
Answer the user's question about the parcel using ONLY the parcel context and retrieved policy chunks below.

${DOMAIN_PRIMER}

Rules:
- Cite every claim with [N] for chunk ID.
- If the question cannot be answered from the provided context, say so explicitly — that itself is often the answer ("this is unresolved under current disclosure").
- Be direct. No filler.`,
  verdict: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia.
Produce exactly ONE sentence (no more) summarizing what is and isn't knowable about this parcel's water relationship to data-center infrastructure.

Format: "<what's observable>; <what's unresolved>."
Examples:
  "NPDES permit on file and DEQ-monitored, but actual withdrawal volumes remain undisclosed."
  "Built data center with zero NPDES coverage — nothing about its water consumption is publicly legible."
  "Outside any watershed under cumulative DC stress, but no community monitoring station sits within a mile."

Rules:
- ONE SENTENCE. No bullets, no headers, no citations.
- Never frame "no NPDES permit" as a positive.
- Maximum 35 words.`,
};

function sensitivityBlock(thresholds: SensitivityThresholdPayload[] | undefined): string {
  if (!thresholds || thresholds.length === 0) return "";
  const lines = thresholds.map((t) => {
    const yearStr = t.byYear ? ` by ${t.byYear}` : "";
    return `[${t.id}] ${t.subScore} (${t.currentScore} → ≥${t.targetScore}): ${t.lever} from ${t.currentValue} → ${t.targetValue}${yearStr}. Plausibility ${t.plausibility}. Source: ${t.source}. Rationale: ${t.rationale}`;
  });
  return lines.join("\n");
}

function buildPrompt(req: MemoRequest, chunks: Array<{ chunk: RagChunk; score: number }>): { system: string; user: string } {
  const system = SYSTEM_PROMPTS[req.mode];
  const ctxBlock = parcelContextBlock(req.parcelContext);
  const chunksBlock = chunks
    .map(({ chunk, score }) => formatChunkForPrompt(chunk, score))
    .join("\n\n---\n\n");

  let task = "";
  if (req.mode === "memo") {
    task = "Generate the water-legibility narrative for this parcel.";
  } else if (req.mode === "counter") {
    task = "Generate the 'what's unresolved' companion for this parcel.";
  } else if (req.mode === "qa") {
    task = `User's question: ${req.question ?? "(no question)"}`;
  }

  const senseBlock = req.mode === "counter" ? sensitivityBlock(req.sensitivity) : "";
  const sensitivitySection = senseBlock
    ? `\n\nSENSITIVITY THRESHOLDS (computed; cite as [S#] in the "What Would Resolve This" section):\n${senseBlock}`
    : "";

  const user = `PARCEL CONTEXT:
${ctxBlock}

RETRIEVED POLICY CHUNKS (cite by [id]):
${chunksBlock}${sensitivitySection}

TASK:
${task}`;

  return { system, user };
}

function buildQuery(req: MemoRequest): string {
  const ctx = req.parcelContext;
  const tokens: string[] = [];
  if (ctx.zoning) tokens.push(ctx.zoning);
  if (ctx.watershed) tokens.push(ctx.watershed);
  tokens.push("NPDES water discharge permit data center");
  if (ctx.inDcBuilding) tokens.push("data center building water use cooling");
  if (req.mode === "memo") {
    tokens.push("water supply consumption disclosure monitoring watershed");
  } else if (req.mode === "counter") {
    tokens.push("unresolved unknown undisclosed withdrawal consumption gap");
  }
  if (req.question) tokens.push(req.question);
  return tokens.join(" ");
}

export async function POST(req: NextRequest) {
  let body: MemoRequest;
  try {
    body = (await req.json()) as MemoRequest;
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!body.gpin || !body.mode || !body.parcelContext) {
    return new Response(JSON.stringify({ error: "Missing gpin/mode/parcelContext" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const query = buildQuery(body);
  const topChunks =
    body.mode === "qa"
      ? retrieveTopChunks(query, 10, 4)
      : body.mode === "verdict"
        ? retrieveTopChunks(query, 4, 2)
        : retrieveTopChunks(query, 12, 2);

  const { system, user } = buildPrompt(body, topChunks);

  const maxTokens = body.mode === "verdict" ? 80 : 1200;
  const temperature = body.mode === "verdict" ? 0.2 : 0.3;

  let llmRes: Response;
  try {
    if (BACKEND === "groq") {
      llmRes = await fetch(GROQ_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${GROQ_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: GROQ_MODEL,
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
          stream: true,
          temperature,
          max_tokens: maxTokens,
        }),
      });
    } else if (BACKEND === "together") {
      llmRes = await fetch(TOGETHER_URL, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${TOGETHER_API_KEY}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          model: TOGETHER_MODEL,
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
          stream: true,
          temperature,
          max_tokens: maxTokens,
        }),
      });
    } else {
      llmRes = await fetch(`${OLLAMA_HOST}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: OLLAMA_MODEL,
          messages: [
            { role: "system", content: system },
            { role: "user", content: user },
          ],
          stream: true,
          keep_alive: "2m",
          options: { temperature, num_ctx: 4096, num_predict: maxTokens },
        }),
      });
    }
  } catch (err) {
    const errMsg =
      BACKEND === "groq"
        ? `Couldn't reach Groq. Check your GROQ_API_KEY in .env.local. (${String(err)})`
        : BACKEND === "together"
          ? `Couldn't reach Together AI. Check your TOGETHER_API_KEY in .env.local. (${String(err)})`
          : `Couldn't reach Ollama at ${OLLAMA_HOST}. Is it running? Try \`ollama serve\`. (${String(err)})`;
    return new Response(JSON.stringify({ error: errMsg }), {
      status: 502,
      headers: { "Content-Type": "application/json" },
    });
  }

  if (!llmRes.ok || !llmRes.body) {
    const text = await llmRes.text().catch(() => "");
    const label = BACKEND === "groq" ? "Groq" : BACKEND === "together" ? "Together AI" : "Ollama";
    return new Response(
      JSON.stringify({ error: `${label} returned ${llmRes.status}: ${text.slice(0, 300)}` }),
      { status: 502, headers: { "Content-Type": "application/json" } },
    );
  }

  const citationAppendix = topChunks
    .map(({ chunk, score }) =>
      JSON.stringify({
        id: chunk.id,
        doc_file: chunk.doc_file,
        doc_title: chunk.doc_title,
        section: chunk.section,
        score: Number(score.toFixed(3)),
      }),
    )
    .join("\n");

  const transformed = new ReadableStream({
    async start(controller) {
      const reader = llmRes.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const header = `VIRA-CITATIONS:\n${citationAppendix}\n\nVIRA-CONTENT:\n`;
      controller.enqueue(new TextEncoder().encode(header));

      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          buffer += decoder.decode(value, { stream: true });

          if (BACKEND === "together" || BACKEND === "groq") {
            const events = buffer.split("\n\n");
            buffer = events.pop() ?? "";
            for (const ev of events) {
              for (const line of ev.split("\n")) {
                if (!line.startsWith("data: ")) continue;
                const payload = line.slice(6).trim();
                if (payload === "[DONE]") continue;
                try {
                  const obj = JSON.parse(payload);
                  const token: string | undefined = obj?.choices?.[0]?.delta?.content;
                  if (typeof token === "string" && token.length > 0) {
                    controller.enqueue(new TextEncoder().encode(token));
                  }
                } catch {
                  // Skip malformed lines.
                }
              }
            }
          } else {
            const lines = buffer.split("\n");
            buffer = lines.pop() ?? "";
            for (const line of lines) {
              if (!line.trim()) continue;
              try {
                const obj = JSON.parse(line);
                const token = obj?.message?.content;
                if (typeof token === "string" && token.length > 0) {
                  controller.enqueue(new TextEncoder().encode(token));
                }
              } catch {
                // Skip.
              }
            }
          }
        }
      } catch (err) {
        controller.enqueue(new TextEncoder().encode(`\n\n[stream error: ${String(err)}]`));
      } finally {
        controller.close();
      }
    },
  });

  return new Response(transformed, {
    status: 200,
    headers: {
      "Content-Type": "text/plain; charset=utf-8",
      "Cache-Control": "no-store",
      "X-Vira-Backend": BACKEND,
      "X-Vira-Model": BACKEND === "groq" ? GROQ_MODEL : BACKEND === "together" ? TOGETHER_MODEL : OLLAMA_MODEL,
    },
  });
}
