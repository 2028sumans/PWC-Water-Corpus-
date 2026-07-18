/**
 * Determine the most impactful sources for a given parcel's Water Legibility
 * Score. Each contributing signal carries an "impact magnitude" (how many
 * points it added or subtracted). We rank sources by absolute magnitude and
 * surface the top N — only sources that actually drove THIS parcel's number.
 */
import type { ScoredParcel } from "@/lib/useScoredParcels";
import { SOURCES, type SourceCitation } from "@/lib/sourceRegistry";

interface RankedSource {
  source: SourceCitation;
  impact: number;
  contribution: string;
  direction: "+" | "-";
}

export function topSourcesForParcel(p: ScoredParcel, limit = 6): RankedSource[] {
  const ranked: RankedSource[] = [];
  const push = (key: string, impact: number, contribution: string, direction: "+" | "-") => {
    const src = SOURCES[key];
    if (!src) return;
    ranked.push({ source: src, impact: Math.abs(impact), contribution, direction });
  };

  // ===== Disclosure — the headline finding =====
  if (p.has_npdes) {
    push("epa:icis-npdes", 40, "Holds an NPDES water discharge permit — rare (4 in all of VA): +40 legibility", "+");
  } else if (p.in_dc_building) {
    push("epa:icis-npdes", 40, "Data center building present, NO NPDES permit on record — the headline dark spot", "-");
  }
  if (p.has_deq_permit) push("va-deq:permits", 25, "Holds a Virginia DEQ water permit: +25 legibility", "+");
  if (p.dmr_nodi_code) push("epa:npdes-dmr", 10, `DMR NODI code: ${p.dmr_nodi_code}`, p.dmr_nodi_code === "C" ? "-" : "+");
  if ((p.n_npdes_violations ?? 0) > 0) push("epa:echo-exporter", 5, `${p.n_npdes_violations} recorded NPDES violation(s) — facility IS monitored`, "+");
  if (p.frs_id) push("epa:frs", 3, "Linked to EPA Facility Registry Service ID", "+");

  // ===== Watershed / hydrology =====
  if (p.watershed_name) {
    const n = p.n_dc_in_watershed ?? 0;
    push("spatial:watersheds", n >= 5 ? 12 : 4, `${p.watershed_name} watershed${n > 0 ? ` — ${n} data center(s) sharing this basin` : ""}`, n >= 5 ? "-" : "+");
  }
  const dStream = p.d_stream_ft ?? null;
  if (dStream !== null && dStream < 300) {
    push("spatial:stream", dStream < 100 ? 30 : 15, `${dStream.toFixed(0)} ft from nearest stream`, "-");
  }
  if (p.rpa) push("spatial:rpa", 15, "Inside Resource Protection Area buffer", "-");
  const dSpring = p.d_spring_ft ?? null;
  if (dSpring !== null && dSpring < 3000) {
    push("spatial:springs", dSpring < 1000 ? 10 : 5, `${dSpring.toFixed(0)} ft from nearest spring/groundwater feature`, "-");
  }

  // ===== Drought / climate =====
  if (p.phdi != null) {
    const sev = p.phdi <= -4 ? "severe drought" : p.phdi <= -2 ? "moderate drought" : p.phdi >= 2 ? "wet" : "near-normal";
    push("noaa:palmer", 20, `PHDI = ${p.phdi.toFixed(2)} (${sev}, countywide)`, p.phdi < 0 ? "-" : "+");
  }
  if (p.cdd != null && p.cdd > 1500) {
    push("noaa:climate-normals", p.cdd > 2000 ? 10 : 5, `Cooling degree days = ${p.cdd} — elevated cooling-water demand season`, "-");
  }

  // ===== Community monitoring =====
  const nWqp = p.n_wqp_stations_1mi ?? 0;
  if (nWqp > 0) push("wqp:stations", nWqp >= 3 ? 10 : 5, `${nWqp} Water Quality Portal station(s) within 1 mi`, "+");
  if ((p.n_deq_monitoring_1mi ?? 0) > 0) push("pwc:deq-monitoring", 5, `${p.n_deq_monitoring_1mi} DEQ monitoring station(s) within 1 mi`, "+");
  if ((p.n_inat_1mi ?? 0) > 0) push("inat:observations", 3, `${p.n_inat_1mi} community iNaturalist observation(s) within 1 mi`, "+");

  // ===== Municipal supply =====
  if (p.pw_water_pct_peak != null) {
    push("pw-water:faq", 10, `Data centers = ${p.pw_water_pct_peak}% of PW Water peak demand (countywide)`, "-");
  }
  if ((p.n_queued_projects_nearby ?? 0) > 10) {
    push("pjm:load-report", (p.n_queued_projects_nearby ?? 0) > 20 ? 10 : 5, `${p.n_queued_projects_nearby} queued interconnection projects nearby`, "-");
  }

  // ===== Stormwater / hazard =====
  if ((p.sw_facilities ?? 0) >= 1) push("spatial:stormwater-seg", 25, `${p.sw_facilities} stormwater detention basin(s) on parcel`, "-");
  if ((p.sw_segments ?? 0) >= 2) push("spatial:stormwater-seg", (p.sw_segments ?? 0) >= 5 ? 20 : 8, `${p.sw_segments} stormwater segment(s) crossing parcel`, "-");
  if ((p.sw_structures ?? 0) >= 5) push("spatial:stormwater-struct", 10, `${p.sw_structures} stormwater structures within range`, "-");
  if (p.dam) {
    const haz = (p.dam_haz_class ?? "").toUpperCase();
    push("spatial:dam", haz === "HIGH" ? 20 : haz === "SIG" ? 10 : 4, `Inside ${haz || "unclassified"} dam-break inundation zone`, "-");
  }

  // De-duplicate by source key, take max impact per source.
  const dedup = new Map<string, RankedSource>();
  for (const r of ranked) {
    const existing = dedup.get(r.source.key);
    if (!existing || r.impact > existing.impact) dedup.set(r.source.key, r);
  }
  return Array.from(dedup.values())
    .sort((a, b) => b.impact - a.impact)
    .slice(0, limit);
}
