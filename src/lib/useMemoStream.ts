"use client";

/**
 * Hook for streaming a Vira memo (or counter-memo, or Q&A) from /api/memo.
 *
 * The endpoint returns a text/plain stream with this shape:
 *
 *   VIRA-CITATIONS:
 *   {"id":12,"doc_file":"SUP2025-00016.json","doc_title":"...","section":"page 17","score":7.34}
 *   {"id":284,"doc_file":"pwc_zoning_ordinance_ch32_excerpts.json",...}
 *   ...
 *   \n
 *   VIRA-CONTENT:
 *   <streamed memo text with [N] citation markers>
 *
 * We parse the header once when it arrives, then append each subsequent chunk
 * to `text`. The caller can read `citations` for the chunk metadata (used to
 * resolve [N] markers in the rendered output) and `text` for the live memo.
 *
 * Usage:
 *   const memo = useMemoStream();
 *   memo.generate({ gpin, mode: "memo", parcelContext });
 *   // memo.text grows incrementally; memo.citations populates after header parse
 */
import { useCallback, useRef, useState } from "react";

export interface MemoCitation {
  id: number;
  doc_file: string;
  doc_title: string;
  section: string;
  score: number;
}

export interface MemoRequest {
  gpin: string;
  mode: "memo" | "counter" | "qa" | "verdict";
  parcelContext: Record<string, unknown>;
  /**
   * Sensitivity thresholds computed by lib/sensitivity/findThresholds.ts.
   * Only consumed by the "counter" mode prompt; ignored otherwise.
   */
  sensitivity?: Array<{
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
  }>;
  question?: string;
}

export interface MemoState {
  text: string;
  citations: MemoCitation[];
  isLoading: boolean;
  error: string | null;
}

const HEADER_DIVIDER = "VIRA-CONTENT:\n";

export function useMemoStream() {
  const [state, setState] = useState<MemoState>({
    text: "",
    citations: [],
    isLoading: false,
    error: null,
  });
  const abortRef = useRef<AbortController | null>(null);

  const reset = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setState({ text: "", citations: [], isLoading: false, error: null });
  }, []);

  const generate = useCallback(async (req: MemoRequest) => {
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    setState({ text: "", citations: [], isLoading: true, error: null });

    try {
      const res = await fetch("/api/memo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(req),
        signal: controller.signal,
      });
      if (!res.ok) {
        const errBody = await res.text().catch(() => "");
        // Try to parse JSON error; fall back to raw text
        let msg = `HTTP ${res.status}`;
        try {
          const parsed = JSON.parse(errBody);
          msg = parsed.error ?? msg;
        } catch {
          if (errBody) msg = errBody.slice(0, 200);
        }
        throw new Error(msg);
      }
      if (!res.body) throw new Error("Empty response body");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let headerParsed = false;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        if (!headerParsed) {
          const dividerIdx = buffer.indexOf(HEADER_DIVIDER);
          if (dividerIdx === -1) continue; // wait for the rest of the header
          const headerBlock = buffer.slice(0, dividerIdx);
          buffer = buffer.slice(dividerIdx + HEADER_DIVIDER.length);
          headerParsed = true;

          // Parse the citations — one JSON object per line after "VIRA-CITATIONS:"
          const citations: MemoCitation[] = [];
          const lines = headerBlock.split("\n").slice(1); // skip "VIRA-CITATIONS:"
          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed) continue;
            try {
              citations.push(JSON.parse(trimmed) as MemoCitation);
            } catch {
              // ignore malformed lines
            }
          }
          setState((s) => ({ ...s, citations }));
        }

        if (headerParsed && buffer) {
          // Flush whatever we've accumulated as content text
          const flush = buffer;
          buffer = "";
          setState((s) => ({ ...s, text: s.text + flush }));
        }
      }

      setState((s) => ({ ...s, isLoading: false }));
    } catch (err) {
      // AbortError is expected when we cancel/restart — no need to surface it.
      if ((err as { name?: string })?.name === "AbortError") return;
      setState((s) => ({ ...s, isLoading: false, error: String(err) }));
    }
  }, []);

  return { ...state, generate, reset };
}
