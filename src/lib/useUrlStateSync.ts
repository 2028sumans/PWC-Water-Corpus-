"use client";

/**
 * Bidirectional sync between the Zustand store and the URL hash, so
 * refreshing preserves the selected facility and links are shareable.
 *
 * Format: `#gpin=7596-81-5396`
 */
import { useEffect, useRef } from "react";
import { useViraStore } from "@/store/useViraStore";

function parseHash(): URLSearchParams {
  const raw = typeof window === "undefined" ? "" : window.location.hash.replace(/^#/, "");
  return new URLSearchParams(raw);
}

function applyHashToStore(p: URLSearchParams) {
  const gpin = p.get("gpin");
  if (gpin) useViraStore.getState().setSelectedGpin(gpin);
}

function buildHashFromStore(): string {
  const s = useViraStore.getState();
  const p = new URLSearchParams();
  if (s.selectedGpin) p.set("gpin", s.selectedGpin);
  const s2 = p.toString();
  return s2 ? `#${s2}` : "";
}

export function useUrlStateSync(): void {
  const hydratedRef = useRef(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    applyHashToStore(parseHash());
    hydratedRef.current = true;
    const onHashChange = () => applyHashToStore(parseHash());
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;
    let pending: number | null = null;
    const flush = () => {
      if (!hydratedRef.current) return;
      const next = buildHashFromStore();
      const current = window.location.hash || "";
      if (next !== current) {
        window.history.replaceState(null, "", next || window.location.pathname + window.location.search);
      }
    };
    const unsubscribe = useViraStore.subscribe(() => {
      if (pending !== null) window.clearTimeout(pending);
      pending = window.setTimeout(flush, 200);
    });
    return () => {
      if (pending !== null) window.clearTimeout(pending);
      unsubscribe();
    };
  }, []);
}
