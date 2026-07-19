/**
 * Memo generation endpoint. Two narrative modes plus a one-line verdict:
 *   - "memo":    Scope 1/2/3 water-footprint narrative for a single facility,
 *                grounded entirely in indirect_water_footprint.py's output
 *                (WUE envelope, grid-mix consumption factor, proportional
 *                Scope 3 anchor) — no parcel scoring of any kind. Receives
 *                the client's deterministic disclosure audit and must
 *                restate it verbatim rather than re-deriving the gaps.
 *   - "qa":      free-form question against the facility + corpus.
 *   - "verdict": one-sentence summary.
 *
 * Note there is deliberately no adversarial "counter" mode: the disclosure
 * gaps are fully known to the pipeline and rendered directly in the panel,
 * so routing them through an LLM would only risk paraphrasing exact numbers.
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

type Mode = "memo" | "qa" | "verdict";

interface UnresolvedItemPayload {
  id: string;
  title: string;
  severity: "structural" | "high" | "moderate";
  onRecord: string;
  gap: string;
  impact: string | null;
  wouldResolve: string;
}

interface FacilityContext {
  name: string;
  kind: "building" | "campus";
  status?: string | null;
  yearBuilt?: number | null;
  gfaSqft?: number | null;
  effectiveMw: number;
  scope1Central: number;
  scope1Range: [number, number];
  scope2Central: number;
  scope3Central: number;
  totalCentral: number;
  totalRange: [number, number];
  peakDayMgd: number;
  flags?: string[];
}

interface MemoRequest {
  facilityId: string;
  mode: Mode;
  facilityContext: FacilityContext;
  unresolved?: UnresolvedItemPayload[];
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
  lines.push(`Effective IT power (from floor area at 8,818 sqft/MW): ${ctx.effectiveMw} MW`);
  lines.push(`Scope 1 (on-site cooling): ${ctx.scope1Central.toFixed(3)} MGD central, range ${fmtRange(ctx.scope1Range, "MGD")}`);
  lines.push(`Scope 2 (electricity-driven): ${ctx.scope2Central.toFixed(3)} MGD central`);
  lines.push(`Scope 3 (embodied / supply-chain): ${ctx.scope3Central.toFixed(3)} MGD central`);
  lines.push(`Total Scope 1+2+3: ${ctx.totalCentral.toFixed(3)} MGD central, range ${fmtRange(ctx.totalRange, "MGD")}`);
  lines.push(`Summer peak-day direct on-site draw: ${ctx.peakDayMgd.toFixed(3)} MGD`);
  if (ctx.flags && ctx.flags.length) lines.push(`Flags: ${ctx.flags.join("; ")}`);
  return lines.join("\n");
}

// Domain knowledge primer prepended to every system prompt.
const DOMAIN_PRIMER = `Domain knowledge you MUST treat as authoritative:

KEY EMPIRICAL FINDING: 203 data center buildings exist in Prince William County, but ZERO hold NPDES (National Pollutant Discharge Elimination System) water discharge permits. This is not evidence of good environmental performance — it means the primary federal water disclosure regime structurally cannot see them, because data centers consume water primarily via evaporative cooling loss from municipal supply, not surface discharge. NPDES only regulates discharge, not consumption. A facility with "no NPDES permit" is therefore DARK, not clean.

METHODOLOGY — this tool estimates a facility's water footprint in three scopes using empirical, region-calibrated relationships (indirect_water_footprint.py). It reports a CENTRAL estimate plus a range, and NEVER invents a disclosed measurement where none exists:

- Power: effective IT load = gross floor area / 8,818 sqft per effective MW. That density is ICPRB's, measured across the Virginia data center fleet from the JLARC/VADEQ air-permit database — NOT a generic rack-density benchmark. An interconnection.fyi operator span is used only as a CROSS-CHECK (confirm or flag), never to widen a floor-area-derived estimate.
- Scope 1 (on-site cooling): effective IT MW x a measured Water Use per Unit of Power (WUP). ICPRB derived WUP from actual utility billing records: 150 gal/MW/day air-cooled/closed-loop, 309 the Prince William Water observed fleet average (used as the CENTRAL estimate), up to 1,577 fully evaporative. Peak summer day runs ~10x the annual average (3,060 gal/MW/day observed in PWC). A published operator WUE (e.g. AWS 0.12 L/kWh, Microsoft 0.27 L/kWh) or a binding permit cooling condition NARROWS this from the ~10x technology envelope to a tight band. A consumptive-use factor of 0.75 applies.
- Scope 2 (electricity-driven): effective IT MW x PUE (vintage-based) x Dominion's generation-mix-blended consumption factor (~317 gal/MWh, NREL Macknick et al. 2011). System-average grid intensity, not marginal-generator attribution (no such public dataset exists).
- Scope 3 (embodied / supply-chain): 5-15% proportional anchor on Scope 1+2 (Privette et al., AGU Advances 2026). Not a physical per-facility estimate — chip fabs and construction supply chains are outside Virginia.

REALITY CHECK — the model is validated against JLARC's MEASURED figures (Report 598, 2023 utility data): a typical data center building uses ~0.018 MGD (like a large office); only 11 buildings statewide exceeded 0.137 MGD; the single largest in Virginia used 0.666 MGD; the ENTIRE Virginia industry used 5.75 MGD. Summing this model over PWC's completed buildings reproduces Prince William Water's reported 0.42 MGD to within 7%. If a facility's central estimate exceeds the largest measured building, say so plainly.

OBSERVABLE / MODELED / UNRESOLVED taxonomy:
- OBSERVABLE: directly in a record (GFA, permit status, year built, NPDES/DEQ status, watershed).
- MODELED: derived via the empirical relationships above (the MGD figures).
- UNRESOLVED: dark under current disclosure — actual cooling technology (unless the operator publishes WUE), actual metered withdrawal, actual PUE, facility-specific embodied water.

GOLDEN RULE: quote the CENTRAL estimate as the headline figure, always with its range. The central uses Prince William Water's own observed intensity. NEVER frame "no NPDES permit" as good news.`;

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
- The "What's Unresolved" section MUST be built from the supplied DISCLOSURE AUDIT items, cited by their [U#] markers. These were computed deterministically from the facility record — restate them faithfully; do NOT invent additional gaps or alter their numbers.
- Total length: 500-800 words. No fluff.`,
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

function unresolvedBlock(items: UnresolvedItemPayload[] | undefined): string {
  if (!items || items.length === 0) return "";
  return items
    .map((u) =>
      [
        `[${u.id}] ${u.title} (${u.severity})`,
        `  On record: ${u.onRecord}`,
        `  Dark: ${u.gap}`,
        u.impact ? `  Effect on estimate: ${u.impact}` : null,
        `  Would resolve: ${u.wouldResolve}`,
      ]
        .filter(Boolean)
        .join("\n"),
    )
    .join("\n\n");
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
  } else if (req.mode === "qa") {
    task = `User's question: ${req.question ?? "(no question)"}`;
  }

  const audit = unresolvedBlock(req.unresolved);
  const auditSection = audit
    ? `\n\nDISCLOSURE AUDIT (computed deterministically from the facility record — restate faithfully, cite as [U#] in the "What's Unresolved" section, do not invent additional gaps):\n${audit}`
    : "";

  const user = `FACILITY CONTEXT:
${ctxBlock}

RETRIEVED POLICY CHUNKS (cite by [id]):
${chunksBlock}${auditSection}

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
    tokens.push("water supply consumption disclosure monitoring watershed unresolved undisclosed withdrawal gap");
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
