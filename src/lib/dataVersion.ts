/**
 * Cache-busting version for everything served out of /public/data.
 *
 * Why this exists. `vercel.json` serves the data assets with
 * `stale-while-revalidate=604800`, which licenses a browser to keep showing a
 * cached copy for up to seven days after a deploy. That is good for load times
 * and actively harmful for correctness: after the fit-out ramp corrected the
 * fleet from 49.6 to 46.2 MGD, the CDN served the new file while returning
 * visitors' browsers went on rendering the old numbers. A plain fetch and a
 * `no-store` fetch of the same URL in the same tab disagreed.
 *
 * Appending this as a query string makes each data revision a distinct cache
 * key, so a corrected number reaches every client on their next load instead of
 * up to a week later, while unchanged deploys still hit cache normally.
 *
 * MUST equal `generated_at` in public/data/facility_profiles.json. Check 25 in
 * verify_research_ready.py asserts exactly that — bumping the data without
 * bumping this constant fails the harness rather than silently shipping a stale
 * page, which is the same class of defect recorded in METHODOLOGY §64.
 */
export const DATA_VERSION = "2026-08-03T01:45:10";

/** Append the data version to a /data URL. */
export function versioned(path: string): string {
  return `${path}?v=${encodeURIComponent(DATA_VERSION)}`;
}
