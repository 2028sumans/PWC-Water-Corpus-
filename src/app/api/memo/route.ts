/**
 * Verdict endpoint. One mode:
 *   - "verdict": one-sentence summary of what is modeled and what remains
 *                unresolved about a facility's water footprint.
 *
 * Everything else the panel shows is deterministic. The long-form memo, the
 * free-form Q&A box, and the adversarial "counter" mode were all removed: the
 * disclosure gaps are fully known to the pipeline and rendered directly in the
 * panel, so routing them through an LLM only risks paraphrasing exact numbers.
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

type Mode = "verdict";

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
  lines.push(`Effective IT power (permit-observed or fitted GFA->MW model; see evidence tier): ${ctx.effectiveMw} MW`);
  lines.push(`Scope 1 (on-site cooling): ${ctx.scope1Central.toFixed(3)} MGD central, range ${fmtRange(ctx.scope1Range, "MGD")}`);
  lines.push(`Scope 2 (electricity-driven): ${ctx.scope2Central.toFixed(3)} MGD central`);
  lines.push(`Scope 3 (embodied / supply-chain): ${ctx.scope3Central.toFixed(3)} MGD central`);
  lines.push(`Total Scope 1+2+3: ${ctx.totalCentral.toFixed(3)} MGD central, range ${fmtRange(ctx.totalRange, "MGD")}`);
  lines.push(`Summer peak-day direct on-site draw: ${ctx.peakDayMgd.toFixed(3)} MGD`);
  if (ctx.flags && ctx.flags.length) lines.push(`Flags: ${ctx.flags.join("; ")}`);
  return lines.join("\n");
}

const SYSTEM_PROMPTS: Record<Mode, string> = {
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

function buildPrompt(req: MemoRequest, chunks: Array<{ chunk: RagChunk; score: number }>): { system: string; user: string } {
  const system = SYSTEM_PROMPTS[req.mode];
  const ctxBlock = facilityContextBlock(req.facilityContext);
  const chunksBlock = chunks
    .map(({ chunk, score }) => formatChunkForPrompt(chunk, score))
    .join("\n\n---\n\n");

  const user = `FACILITY CONTEXT:
${ctxBlock}

RETRIEVED POLICY CHUNKS (cite by [id]):
${chunksBlock}`;

  return { system, user };
}

function buildQuery(req: MemoRequest): string {
  const ctx = req.facilityContext;
  const tokens: string[] = [];
  tokens.push(ctx.kind === "building" ? "data center building" : "data center campus rezoning");
  tokens.push("NPDES water discharge permit data center");
  tokens.push("data center water use evaporative cooling WUE PUE electricity generation mix");
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
  const topChunks = retrieveTopChunks(query, 4, 2);

  const { system, user } = buildPrompt(body, topChunks);

  const maxTokens = 80;
  const temperature = 0.2;

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
