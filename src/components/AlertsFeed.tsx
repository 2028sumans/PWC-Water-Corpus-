"use client";

/**
 * Header bell + dropdown for the in-app alerts feed. Driven by
 * useViraStore().alerts which is fed by lib/portfolio/useAlerts.ts.
 *
 * Behavior:
 *   - Bell shows a count badge for unread alerts (red when > 0).
 *   - Click opens a dropdown with the most recent N alerts.
 *   - Opening the dropdown marks all alerts read.
 *   - Each alert has a "✕" to dismiss individually; bottom button clears all.
 */
import { useEffect, useRef, useState } from "react";
import { useViraStore } from "@/store/useViraStore";
import { Bell, X, TrendingUp, TrendingDown, Filter } from "lucide-react";

function relativeTime(ts: number): string {
  const dt = Date.now() - ts;
  const sec = Math.round(dt / 1000);
  if (sec < 60) return `${sec}s`;
  const min = Math.round(sec / 60);
  if (min < 60) return `${min}m`;
  const hr = Math.round(min / 60);
  if (hr < 24) return `${hr}h`;
  return `${Math.round(hr / 24)}d`;
}

function iconFor(kind: string) {
  if (kind === "score_rise") return <TrendingUp className="h-3.5 w-3.5 text-green-400" />;
  if (kind === "score_drop") return <TrendingDown className="h-3.5 w-3.5 text-red-400" />;
  if (kind === "match_count_change") return <Filter className="h-3.5 w-3.5 text-purple-300" />;
  return <Bell className="h-3.5 w-3.5 text-neutral-400" />;
}

export function AlertsFeed() {
  const alerts = useViraStore((s) => s.alerts);
  const markAllRead = useViraStore((s) => s.markAllAlertsRead);
  const markRead = useViraStore((s) => s.markAlertRead);
  const clearAlerts = useViraStore((s) => s.clearAlerts);

  const [open, setOpen] = useState(false);
  const wrapRef = useRef<HTMLDivElement | null>(null);

  const unread = alerts.filter((a) => !a.read).length;

  useEffect(() => {
    if (!open) return;
    // Mark read on the next tick so the badge fades after the dropdown paints.
    const id = window.setTimeout(() => markAllRead(), 250);
    return () => window.clearTimeout(id);
  }, [open, markAllRead]);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    };
    window.addEventListener("mousedown", onClick);
    return () => window.removeEventListener("mousedown", onClick);
  }, [open]);

  return (
    <div ref={wrapRef} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="relative rounded p-1 text-neutral-400 hover:text-amber-300 hover:bg-neutral-900"
        aria-label={`Alerts (${unread} unread)`}
        title={`Portfolio activity · ${unread} unread`}
      >
        <Bell className="h-4 w-4" />
        {unread > 0 && (
          <span className="absolute -top-0.5 -right-0.5 rounded-full bg-red-500 text-white text-[8px] leading-none px-1 py-0.5 min-w-[14px] text-center">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </button>
      {open && (
        <div className="absolute right-0 top-7 z-30 w-[380px] max-h-[500px] overflow-y-auto rounded-lg border border-neutral-700 bg-neutral-950 shadow-2xl">
          <div className="sticky top-0 flex items-center justify-between border-b border-neutral-800 bg-neutral-950 px-3 py-2">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500">
              Portfolio activity
            </div>
            {alerts.length > 0 && (
              <button
                onClick={() => clearAlerts()}
                className="text-[10px] text-neutral-500 hover:text-amber-300 normal-case"
              >
                clear all
              </button>
            )}
          </div>
          {alerts.length === 0 ? (
            <div className="px-3 py-6 text-[11px] text-neutral-500 leading-relaxed text-center">
              No activity yet. Add parcels to a portfolio or save a search — alerts will fire when scores or match counts shift.
            </div>
          ) : (
            <div className="divide-y divide-neutral-900">
              {alerts.map((a) => (
                <div
                  key={a.id}
                  className={`group flex items-start gap-2 px-3 py-2 text-[11px] ${
                    a.read ? "bg-neutral-950" : "bg-amber-950/15"
                  }`}
                >
                  <div className="mt-0.5 shrink-0">{iconFor(a.kind)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="text-neutral-200 leading-snug">{a.message}</div>
                    <div className="mt-0.5 text-[9px] text-neutral-600">
                      {relativeTime(a.ts)} ago
                    </div>
                  </div>
                  <button
                    onClick={() => markRead(a.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity text-neutral-600 hover:text-red-400 shrink-0"
                    aria-label="Dismiss"
                    title="Mark read"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
