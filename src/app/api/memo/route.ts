/**
 * Memo generation endpoint. Three narrative modes plus a one-line verdict:
 *   - "memo":    Scope 1/2/3 water-footprint narrative for a single facility,
 *                grounded entirely in indirect_water_footprint.py's output
 *                (WUE envelope, grid-mix consumption factor, proportional
 *                Scope 3 anchor) — no parcel scoring of any kind.
 *   - "counter": adversarial "what's unresolved" — same RAG, flipped framing,
 *                required to cite the client-computed uncertainty drivers.
 *   - "qa":      free-form question against the facility + corpus.
 *   - "verdict": one-sentence summary.
 *
 * Architecture: BM25 retrieves top-K chunks from /data/rag_chunks.json,
 * we build a structured prompt with the facility context + retrieved
 * chunks, stream the response back to the client.
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

interface UncertaintyDriverPayload {
  id: string;
  title: string;
  detail: string;
  plausibility: "high" | "medium" | "low";
}

interface FacilityContext {
  name: string;
  kind: "building" | "campus";
  status?: string | null;
  yearBuilt?: number | null;
  gfaSqft?: number | null;
  powerMwRange: [number, number];
  powerBasis: string;
  scope1MgdRange: [number, number];
  scope2MgdRange: [number, number];
  scope3MgdRange: [number, number];
  totalMgdRange: [number, number];
  flags?: string[];
}

interface MemoRequest {
  facilityId: string;
  mode: Mode;
  facilityContext: FacilityContext;
  uncertaintyDrivers?: UncertaintyDriverPayload[];
  question?: string;
}

function fmtRange(r: [number, number], unit: string, digits = 3): string {
  return `${r[0].toFixed(digits)}–${r[1].toFixed(digits)} ${unit}`;
}

function facilityContextBlock(ctx: FacilityContext): string {
  const lines: string[] = [];
  lines.push(`Facility: ${ctx.name} (${ctx.kind})`);
  if (ctx.status) lines.push(`Status: ${ctx.status}`);
  if (ctx.yearBuilt) lines.push(`Year built: ${ctx.yearBuilt}`);
  if (ctx.gfaSqft) lines.push(`Gross floor area: ${ctx.gfaSqft.toLocaleString()} sqft`);
  lines.push(`Estimated facility power: ${fmtRange(ctx.powerMwRange, "MW", 1)} (basis: ${ctx.powerBasis.replace("_", " ")})`);
  lines.push(`Scope 1 (on-site cooling): ${fmtRange(ctx.scope1MgdRange, "MGD")}`);
  lines.push(`Scope 2 (electricity-driven): ${fmtRange(ctx.scope2MgdRange, "MGD")}`);
  lines.push(`Scope 3 (embodied / supply-chain): ${fmtRange(ctx.scope3MgdRange, "MGD")}`);
  lines.push(`Total Scope 1+2+3 envelope: ${fmtRange(ctx.totalMgdRange, "MGD")}`);
  if (ctx.flags && ctx.flags.length) lines.push(`Flags: ${ctx.flags.join(", ")}`);
  return lines.join("\n");
}

// Domain knowledge primer prepended to every system prompt.
const DOMAIN_PRIMER = `Domain knowledge you MUST treat as authoritative:

KEY EMPIRICAL FINDING: 203 data center buildings exist in Prince William County, but ZERO hold NPDES (National Pollutant Discharge Elimination System) water discharge permits. This is not evidence of good environmental performance — it means the primary federal water disclosure regime structurally cannot see them, because data centers consume water primarily via evaporative cooling loss from municipal supply, not surface discharge. NPDES only regulates discharge, not consumption. A facility with "no NPDES permit" is therefore DARK, not clean.

METHODOLOGY — this tool estimates a facility's water footprint in three scopes, exactly as defined by indirect_water_footprint.py, and NEVER invents a single-point water-consumption number:

- Scope 1 (on-site cooling): water evaporated at the facility itself via cooling towers / adiabatic humidification. Governed by Water Usage Effectiveness (WUE, L water per kWh of IT equipment energy; The Green Grid). Cooling technology (dry/closed-loop vs. hybrid vs. open evaporative) is NOT disclosed per facility in any PWC public dataset, so Scope 1 is always reported as the FULL published WUE envelope (0.0-2.4 L/kWh), never narrowed by an unstated assumption. A "climate-weighted point" (from trailing cooling-degree-days) may accompany the range as a plausibility signal for evaporative/hybrid systems specifically — it never replaces the range.
- Scope 2 (electricity-driven): water consumed at the power plants generating the facility's electricity, computed from estimated facility power draw x Dominion's generation-mix-blended consumption factor (~318 gal/MWh, NREL Macknick et al. 2011) x assumed 90% utilization. This is a system-average grid factor, not marginal-generator attribution (no such public dataset exists).
- Scope 3 (embodied / supply-chain): water used to fabricate chips, servers, and construction materials before the facility ever draws power. NOT attributable to a specific PWC facility (chip fabs are not in Virginia) — modeled as a 5-15% proportional anchor on top of the Scope 1+2 operational total, per corporate embodied-vs-operational disclosure ratios (Privette et al., AGU Advances 2026). This is a floor-level anchor, not a physical per-facility estimate — at least one hyperscaler has disclosed embodied water exceeding 99% of its corporate total under a different accounting boundary, which is evidence the 5-15% anchor is conservative, not a contradiction.

POWER ESTIMATION: two independent methods are cross-checked — (A) GFA-based: floor area x IT power density benchmark x PUE range selected by building vintage; (B) operator-keyword match against interconnection.fyi's public interconnection-queue MW ranges. When both exist and overlap, the range narrows to their intersection (the strongest evidence this tool can produce). When they disagree, both bounds are kept and the disagreement is flagged rather than silently resolved. When only one exists, that one is reported alone.

OBSERVABLE / MODELED / UNRESOLVED taxonomy — every claim about a facility's water footprint falls into one of three buckets:
- OBSERVABLE: directly present in an institutional record (GFA, permit status, year built, NPDES/DEQ permit status, watershed membership).
- MODELED: derived from the methodology above using observable inputs (Scope 1/2/3 MGD ranges, facility power range) — defensible but not a disclosed measurement.
- UNRESOLVED: dark under current disclosure — actual cooling technology, actual metered water withdrawal, actual disclosed PUE, actual facility-specific embodied-water footprint. This is the largest bucket for data center facilities specifically.

GOLDEN RULE: the total Scope 1+2+3 envelope is the sum of each scope's independent minimum and maximum — a conservative bound, not a statistical confidence interval (the three scopes are not assumed to co-vary). NEVER report a single point water-consumption figure for any facility — none is disclosed, and this tool's job is to make that gap visible, not paper over it. NEVER frame "no NPDES permit" as good news.`;

const SYSTEM_PROMPTS: Record<Mode, string> = {
  memo: `You are a water-risk analyst estimating data-center water footprints in Prince William County, Virginia, using the Scope 1/2/3 methodology below. You categorize each attribute as observable (directly present in institutional records), modeled (derived via the stated methodology), or unresolved (dark under current disclosure). Use the retrieved policy documents to ground your analysis. Be neutral — assess, don't advocate.

${DOMAIN_PRIMER}

Generate a Scope 1/2/3 water-footprint narrative for the facility described below.

Output structure (use these exact headers):
  Executive Summary
  Power & Scope 2 Basis
  Scope 1 — On-Site Cooling
  Scope 3 — Embodied / Supply-Chain
  What's Observable
  What's Modeled
  What's Unresolved
  Recommendation for Further Diligence

Rules:
- Cite every factual claim with [N] where N is a chunk ID from the retrieved context.
- If you cannot cite a source for a claim, omit the claim.
- Use the facility's actual attributes verbatim, including the exact MGD ranges given.
- Never state a single-point water-consumption number — always the range, with its basis.
- Total length: 500-800 words. No fluff.`,
  counter: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia, writing the adversarial "what's unresolved" companion to the main Scope 1/2/3 memo.

${DOMAIN_PRIMER}

Identify the 3-5 most significant unresolved or dark aspects of this facility's ACTUAL water footprint versus this tool's modeled estimate.

Output structure:
  Top Unresolved Questions (3-5 enumerated, ranked by significance)
  Disclosure Gaps (what regulatory regime SHOULD but doesn't capture this)
  What Would Narrow This Estimate — REQUIRED to integrate the uncertainty drivers listed under "UNCERTAINTY DRIVERS" using their [U#] markers. Lead with the highest-likelihood-of-resolution driver.
  Verdict (one paragraph: how legible is this facility's actual water footprint, honestly?)

Rules:
- Cite every policy/document claim with [N] for chunk ID.
- Cite every uncertainty driver with its [U#] marker — do NOT invent numbers; use the supplied detail verbatim.
- Be rigorous but honest — surface what genuinely cannot be known from public data today.
- Total length: 400-600 words.`,
  qa: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia.
Answer the user's question about the facility using ONLY the facility context and retrieved policy chunks below.

${DOMAIN_PRIMER}

Rules:
- Cite every claim with [N] for chunk ID.
- If the question cannot be answered from the provided context, say so explicitly — that itself is often the answer ("this is unresolved under current disclosure").
- Be direct. No filler.`,
  verdict: `You are a water-risk analyst for data center infrastructure in Prince William County, Virginia.
Produce exactly ONE sentence (no more) summarizing what is modeled and what remains unresolved about this facility's water footprint.

Format: "<what's modeled/observable>; <what's unresolved>."
Examples:
  "Est. 0.8-1.6 MGD total footprint from a GFA-and-operator-agreeing power estimate, but actual cooling technology and metered withdrawal remain undisclosed."
  "Power estimate rests on GFA alone with no operator cross-check, and Scope 1 spans the full WUE envelope — this facility's real footprint could sit anywhere in a wide range."

Rules:
- ONE SENTENCE. No bullets, no headers, no citations.
- Never frame "no NPDES permit" as a positive.
- Maximum 35 words.`,
};

function uncertaintyBlock(drivers: UncertaintyDriverPayload[] | undefined): string {
  if (!drivers || drivers.length === 0) return "";
  const lines = drivers.map((d) => `[${d.id}] ${d.title}: ${d.detail} Likelihood of resolution: ${d.plausibility}.`);
  return lines.join("\n");
}

function buildPrompt(req: MemoRequest, chunks: Array<{ chunk: RagChunk; score: number }>): { system: string; user: string } {
  const system = SYSTEM_PROMPTS[req.mode];
  const ctxBlock = facilityContextBlock(req.facilityContext);
  const chunksBlock = chunks
    .map(({ chunk, score }) => formatChunkForPrompt(chunk, score))
    .join("\n\n---\n\n");

  let task = "";
  if (req.mode === "memo") {
    task = "Generate the Scope 1/2/3 water-footprint narrative for this facility.";
  } else if (req.mode === "counter") {
    task = "Generate the 'what's unresolved' companion for this facility.";
  } else if (req.mode === "qa") {
    task = `User's question: ${req.question ?? "(no question)"}`;
  }

  const uncBlock = req.mode === "counter" ? uncertaintyBlock(req.uncertaintyDrivers) : "";
  const uncertaintySection = uncBlock
    ? `\n\nUNCERTAINTY DRIVERS (computed; cite as [U#] in the "What Would Narrow This Estimate" section):\n${uncBlock}`
    : "";

  const user = `FACILITY CONTEXT:
${ctxBlock}

RETRIEVED POLICY CHUNKS (cite by [id]):
${chunksBlock}${uncertaintySection}

TASK:
${task}`;

  return { system, user };
}

function buildQuery(req: MemoRequest): string {
  const ctx = req.facilityContext;
  const tokens: string[] = [];
  tokens.push(ctx.kind === "building" ? "data center building" : "data center campus rezoning");
  tokens.push("NPDES water discharge permit data center");
  tokens.push("data center water use evaporative cooling WUE PUE electricity generation mix");
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

  if (!body.facilityId || !body.mode || !body.facilityContext) {
    return new Response(JSON.stringify({ error: "Missing facilityId/mode/facilityContext" }), {
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
