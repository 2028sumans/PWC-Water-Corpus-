/**
 * Tile-serving route with explicit HTTP Range support + no-cache headers.
 *
 * Background: PMTiles uses HTTP Byte Serving — issuing `Range: bytes=N-M` requests
 * to read just the bytes it needs out of the single .pmtiles file. The pmtiles
 * JS client (FetchSource) throws "no content-length header or content-length
 * exceeding request" if it ever gets a `200 OK` whose Content-Length is larger
 * than the requested byte slice. That's the failure mode you hit in dev: the
 * browser cache short-circuits a Range request and returns a stale `200 OK`
 * with the full 24MB Content-Length, tripping the safety check.
 *
 * Fix: serve the file through a route handler that
 *   1. Honors `Range:` by returning `206 Partial Content` with `Content-Range`
 *      and a Content-Length matching the requested slice exactly.
 *   2. Sets `Cache-Control: no-store` so the browser never tries to satisfy
 *      a Range request from cache.
 *
 * Performance note: in dev this reads from disk on every request, which is
 * fine for the 24MB pmtiles. In production on Vercel, swap this route out for
 * a static asset on a CDN that supports Range natively (Cloudflare R2, Vercel
 * Blob, S3) — `Cache-Control: public, max-age=31536000, immutable` is safe
 * because each new bake produces a new file path.
 */
import { type NextRequest } from "next/server";
import fs from "node:fs";
import path from "node:path";

const TILES_DIR = path.join(process.cwd(), "public", "tiles");

// Whitelist tile filenames to prevent traversal. Anything other than these
// returns 404 — we don't want this route to expose arbitrary public files.
const ALLOWED = new Set([
  "parcels.pmtiles",
  // Spatial layers baked by bake_map_layers.py — matches src/lib/mapLayerRegistry.ts
  "watersheds.pmtiles",
  "streams.pmtiles",
  "hydrology.pmtiles",
  "rpa.pmtiles",
  "springs.pmtiles",
  "surface_temp.pmtiles",
  "cedar_run_gage.pmtiles",
  "gw_well.pmtiles",
  "tidal_flow.pmtiles",
  "stormwater_seg.pmtiles",
  "stormwater_struct.pmtiles",
  "dam.pmtiles",
  "soil.pmtiles",
  "npdes_facilities.pmtiles",
  "dc_buildings.pmtiles",
  "dc_projects.pmtiles",
  "wqp_stations.pmtiles",
  "deq_monitoring.pmtiles",
  "inat_obs.pmtiles",
  "transmission.pmtiles",
  "zoning.pmtiles",
  "use_permits.pmtiles",
  "bza.pmtiles",
  "pending.pmtiles",
  "lrlu.pmtiles",
  "protected.pmtiles",
  "state_land.pmtiles",
]);

// In-memory cache of the tile-file bytes. PMTiles is only ~24 MB and changes
// only when we re-bake; keeping it resident means every Range request is a
// constant-time Buffer slice instead of a disk read + stream. ~100× faster
// per request, which makes the initial map paint go from "slow" to instant.
// Keyed by absolute path. Invalidates if mtime changes (so re-bakes are picked
// up without a server restart).
interface CachedFile {
  buffer: Buffer;
  size: number;
  mtimeMs: number;
}
const cache = new Map<string, CachedFile>();

function notFound() {
  return new Response("Not found", { status: 404 });
}

function badRange() {
  return new Response("Range Not Satisfiable", { status: 416 });
}

function noStoreHeaders(extra: Record<string, string> = {}): HeadersInit {
  return {
    "Cache-Control": "no-store",
    "Content-Type": "application/octet-stream",
    "Accept-Ranges": "bytes",
    ...extra,
  };
}

async function resolveFile(filename: string) {
  if (!ALLOWED.has(filename)) return null;
  const full = path.join(TILES_DIR, filename);
  // Guard against ../ traversal even though ALLOWED is the real defense.
  if (!full.startsWith(TILES_DIR)) return null;
  try {
    const stat = await fs.promises.stat(full);
    if (!stat.isFile()) return null;
    // Check cache: serve from RAM if buffer is fresh, else reload.
    const cached = cache.get(full);
    if (cached && cached.mtimeMs === stat.mtimeMs && cached.size === stat.size) {
      return { full, size: cached.size, buffer: cached.buffer };
    }
    // First request (or post-rebake) — load the whole file into memory once.
    const buffer = await fs.promises.readFile(full);
    cache.set(full, { buffer, size: stat.size, mtimeMs: stat.mtimeMs });
    return { full, size: stat.size, buffer };
  } catch {
    return null;
  }
}

export async function HEAD(
  _req: NextRequest,
  ctx: { params: Promise<{ file: string }> },
) {
  const { file } = await ctx.params;
  const resolved = await resolveFile(file);
  if (!resolved) return notFound();
  return new Response(null, {
    status: 200,
    headers: noStoreHeaders({ "Content-Length": String(resolved.size) }),
  });
}

export async function GET(
  req: NextRequest,
  ctx: { params: Promise<{ file: string }> },
) {
  const { file } = await ctx.params;
  const resolved = await resolveFile(file);
  if (!resolved) return notFound();

  const { size, buffer } = resolved;
  const rangeHeader = req.headers.get("range");

  // No Range header — return the whole file (first metadata read, or a non-
  // pmtiles client GETing the URL). 200 OK + full body, served from the
  // cached buffer in one shot.
  if (!rangeHeader) {
    // Buffer is a Node.js Buffer (Uint8Array subclass); cast its underlying
    // bytes to a fresh Uint8Array so the Response treats it as a body.
    return new Response(new Uint8Array(buffer), {
      status: 200,
      headers: noStoreHeaders({ "Content-Length": String(size) }),
    });
  }

  // Parse "bytes=N-M" — only support a single closed range. pmtiles only ever
  // asks for closed ranges so we don't need to handle multipart or open-ended.
  const match = /^bytes=(\d+)-(\d*)$/.exec(rangeHeader.trim());
  if (!match) return badRange();
  const start = Number.parseInt(match[1], 10);
  const end = match[2] ? Number.parseInt(match[2], 10) : size - 1;
  if (
    Number.isNaN(start) ||
    Number.isNaN(end) ||
    start < 0 ||
    end >= size ||
    start > end
  ) {
    return badRange();
  }

  // Slice the cached buffer (zero-copy view) instead of reading from disk.
  // This is the hot path — every map tile request goes through here.
  const chunk = buffer.subarray(start, end + 1);
  return new Response(new Uint8Array(chunk), {
    status: 206,
    headers: noStoreHeaders({
      "Content-Length": String(chunk.length),
      "Content-Range": `bytes ${start}-${end}/${size}`,
    }),
  });
}
