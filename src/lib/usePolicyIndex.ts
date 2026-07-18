"use client";

/**
 * Loads the pre-computed policy-document index produced by
 * /preprocess_score_parcels.py. Provides:
 *   - The list of 22 policy docs in the corpus (title, file, length)
 *   - Per-zoning mention counts (how thoroughly each zoning is addressed)
 *   - Per-watershed mention counts
 *   - GPINs explicitly referenced by the Hornbaker SUP file
 *
 * Used by the right panel to show "this parcel is cited in N policy docs"
 * and (later) by the LLM RAG memo to surface citation links.
 */
import { useEffect, useState } from "react";

export interface PolicyDoc {
  file: string;
  title: string;
  length: number;
}

export interface OppositionRecord {
  speakers: number;
  topics: string[];
  source_doc: string;
}

export interface PolicyIndex {
  docs: PolicyDoc[];
  zoning_mentions: Record<string, number>;
  watershed_mentions: Record<string, number>;
  hornbaker_gpins: string[];
  /** GPIN → { speakers, topics, source_doc } for parcels with documented opposition. */
  opposition?: Record<string, OppositionRecord>;
}

let _cache: PolicyIndex | null = null;

export function usePolicyIndex() {
  const [policy, setPolicy] = useState<PolicyIndex | null>(_cache);

  useEffect(() => {
    if (_cache) return;
    let cancelled = false;
    fetch("/data/policy_index.json")
      .then((r) => (r.ok ? r.json() : null))
      .then((data: PolicyIndex | null) => {
        if (cancelled || !data) return;
        _cache = data;
        setPolicy(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, []);

  return policy;
}

export function getCachedPolicyIndex(): PolicyIndex | null {
  return _cache;
}
