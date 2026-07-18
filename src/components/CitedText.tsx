"use client";

/**
 * Renders memo text where [N] markers are interpolated into clickable
 * citation chips that resolve to the source policy doc.
 *
 * Why a dedicated component: the LLM emits inline markers like
 *   "Hornbaker sits outside the DCOOD overlay [12], requiring an SUP [284]."
 * We want hover tooltips and click-through to the source file. Trying to do
 * this with dangerouslySetInnerHTML would skip React's escaping and force us
 * to template-string the title attribute — easy to break with apostrophes.
 */
import type { MemoCitation } from "@/lib/useMemoStream";
import { ExternalLink } from "lucide-react";

interface CitedTextProps {
  text: string;
  citations: MemoCitation[];
}

const CITATION_RE = /\[(\d+)\]/g;

export function CitedText({ text, citations }: CitedTextProps) {
  if (!text) return null;
  const byId = new Map<number, MemoCitation>(citations.map((c) => [c.id, c]));

  // Split on [N] markers, keep the marker tokens so we can swap them for chips.
  const parts: Array<{ kind: "text" | "cite"; value: string; id?: number }> = [];
  let lastIdx = 0;
  CITATION_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = CITATION_RE.exec(text)) !== null) {
    if (m.index > lastIdx) parts.push({ kind: "text", value: text.slice(lastIdx, m.index) });
    parts.push({ kind: "cite", value: m[0], id: Number(m[1]) });
    lastIdx = m.index + m[0].length;
  }
  if (lastIdx < text.length) parts.push({ kind: "text", value: text.slice(lastIdx) });

  return (
    <div className="text-[11px] text-neutral-300 leading-relaxed whitespace-pre-wrap">
      {parts.map((part, i) => {
        if (part.kind === "text") return <span key={i}>{part.value}</span>;
        const cite = part.id !== undefined ? byId.get(part.id) : undefined;
        if (!cite) {
          // Unknown citation — render as plain text so the LLM's marker isn't lost.
          return (
            <span key={i} className="text-neutral-600">
              {part.value}
            </span>
          );
        }
        return (
          <a
            key={i}
            href={`/data/policy/${encodeURIComponent(cite.doc_file)}`}
            target="_blank"
            rel="noopener noreferrer"
            title={`${cite.doc_title} — ${cite.section} (relevance ${cite.score})`}
            className="inline-flex items-baseline gap-0.5 rounded bg-amber-900/30 hover:bg-amber-800/50 text-amber-300 hover:text-amber-200 px-1 py-0 mx-0.5 text-[10px] leading-tight align-baseline"
          >
            {part.value}
            <ExternalLink className="h-2.5 w-2.5" />
          </a>
        );
      })}
    </div>
  );
}
