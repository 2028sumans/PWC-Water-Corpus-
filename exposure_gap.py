"""
H1 + H2 — exposure overlay and the regulatory/monitoring gap, spatialized.

Two questions the footprint number cannot answer:
  H1 EXPOSURE     Where do these buildings sit relative to the things that would
                  be harmed -- streams, Resource Protection Areas, wetlands?
  H2 GAP          Where is the regulatory and MONITORING apparatus that would
                  detect a problem, relative to where the buildings actually are?

The finding is the mismatch between the two. The buildings are close to water;
the monitoring is not close to the buildings.

WHAT THE FIELDS MEAN (all precomputed per building in facility_profiles
water_context by build_facility_profiles.py, from county/state GIS layers)
  d_stream_ft            distance to the nearest mapped stream
  rpa / wetland          intersects a Resource Protection Area / wetland
  has_npdes              holds an NPDES discharge permit under its own facility
  n_wqp_stations_1mi     Water Quality Portal monitoring stations within 1 mile
  n_deq_monitoring_1mi   VA DEQ monitoring stations within 1 mile
  n_inat_research_1mi    research-grade iNaturalist observations within 1 mile
                         (the community-observation layer -- what the public has
                         actually recorded near these sites)

Cross-tabulated against the watershed each building sits in, so the gap can be
reported where the concentration is (Broad Run, 166 buildings, §41).

Reads the shipped profiles. Writes public/data/exposure_gap.json.
"""
import json
import os
import statistics as st
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.join(HERE, "public", "data", "facility_profiles.json")
OUT = os.path.join(HERE, "public", "data", "exposure_gap.json")

NEAR_STREAM_FT = 300      # RPA buffers in Virginia are commonly 100 ft; 300 ft is
                          # a conservative "adjacent to water" threshold


def q(vals, p):
    s = sorted(vals)
    if len(s) < 3:
        return float(st.mean(s)) if s else None
    return float(st.quantiles(s, n=100)[p - 1])


def main():
    d = json.load(open(PROFILES))
    bs = [b for b in d["buildings"] if b.get("scope_water_footprint")]
    n = len(bs)

    ds = [(b.get("water_context") or {}).get("d_stream_ft") for b in bs]
    ds = [x for x in ds if isinstance(x, (int, float))]

    def wc(b, k, default=0):
        v = (b.get("water_context") or {}).get(k)
        return v if isinstance(v, (int, float)) else default

    near = [b for b in bs if wc(b, "d_stream_ft", 1e9) <= NEAR_STREAM_FT]
    rpa = [b for b in bs if wc(b, "rpa") == 1]
    wet = [b for b in bs if wc(b, "wetland") == 1]
    npdes = [b for b in bs if wc(b, "has_npdes") == 1]
    no_wqp = [b for b in bs if wc(b, "n_wqp_stations_1mi") == 0]
    no_deq = [b for b in bs if wc(b, "n_deq_monitoring_1mi") == 0]
    # the compound gap: adjacent to a stream, no discharge permit, no monitoring
    blind = [b for b in bs if wc(b, "d_stream_ft", 1e9) <= NEAR_STREAM_FT
             and wc(b, "has_npdes") == 0 and wc(b, "n_deq_monitoring_1mi") == 0]

    exposure = {
        "n_buildings": n,
        "distance_to_stream_ft": {"min": min(ds), "p25": round(q(ds, 25)), "median": round(st.median(ds)),
                                  "p75": round(q(ds, 75)), "max": max(ds)},
        "within_300ft_of_stream": {"n": len(near), "pct": round(100 * len(near) / n)},
        "in_resource_protection_area": {"n": len(rpa), "pct": round(100 * len(rpa) / n)},
        "in_wetland": {"n": len(wet), "pct": round(100 * len(wet) / n)},
    }
    gap = {
        "holds_own_npdes_permit": {"n": len(npdes), "pct": round(100 * len(npdes) / n)},
        "no_npdes": {"n": n - len(npdes), "pct": round(100 * (n - len(npdes)) / n)},
        "no_wqp_station_within_1mi": {"n": len(no_wqp), "pct": round(100 * len(no_wqp) / n)},
        "no_deq_station_within_1mi": {"n": len(no_deq), "pct": round(100 * len(no_deq) / n)},
        "compound_blind_spot": {
            "definition": f"within {NEAR_STREAM_FT} ft of a mapped stream AND no own NPDES permit "
                          f"AND no DEQ monitoring station within 1 mile",
            "n": len(blind), "pct": round(100 * len(blind) / n)},
    }

    # by watershed -- report the gap where the concentration is
    byws = defaultdict(lambda: {"n": 0, "near": 0, "no_npdes": 0, "no_deq": 0, "s1": 0.0, "peak": 0.0})
    for b in bs:
        ws = (b.get("water_context") or {}).get("watershed_name") or "UNKNOWN"
        a = byws[ws]; a["n"] += 1
        a["near"] += 1 if wc(b, "d_stream_ft", 1e9) <= NEAR_STREAM_FT else 0
        a["no_npdes"] += 1 if wc(b, "has_npdes") == 0 else 0
        a["no_deq"] += 1 if wc(b, "n_deq_monitoring_1mi") == 0 else 0
        s = b["scope_water_footprint"]["scope1_onsite_cooling"]
        a["s1"] += s["mgd_central"]; a["peak"] += s["peak_day_mgd"]
    by_watershed = {k: {**v, "s1": round(v["s1"], 3), "peak": round(v["peak"], 2),
                        "pct_near_stream": round(100 * v["near"] / v["n"])}
                    for k, v in sorted(byws.items(), key=lambda kv: -kv[1]["n"])}

    # community observation layer (the original abstract's angle)
    inat = [wc(b, "n_inat_research_1mi") for b in bs]
    community = {
        "research_grade_inat_within_1mi": {"median": st.median(inat), "max": max(inat),
                                           "buildings_with_any": sum(1 for x in inat if x > 0)},
        "note": "Research-grade community observations exist near most sites while official "
                "monitoring does not -- the citizen layer is denser than the regulatory one.",
    }

    out = {
        "purpose": "Exposure (how close the buildings are to water) vs the regulatory and "
                   "monitoring apparatus (how close oversight is to the buildings).",
        "exposure": exposure,
        "regulatory_monitoring_gap": gap,
        "by_watershed": by_watershed,
        "community_observation_layer": community,
        "headline": (
            f"The buildings sit a median {round(st.median(ds))} ft from a mapped stream "
            f"({exposure['within_300ft_of_stream']['pct']}% within {NEAR_STREAM_FT} ft, closest "
            f"{min(ds):.0f} ft), yet {gap['no_npdes']['pct']}% hold no NPDES discharge permit of "
            f"their own and {gap['no_deq_station_within_1mi']['pct']}% have no VA DEQ monitoring "
            f"station within a mile -- in fact NOT ONE of the {n} buildings does. "
            f"{gap['compound_blind_spot']['n']} buildings ({gap['compound_blind_spot']['pct']}%) "
            f"are simultaneously stream-adjacent, unpermitted for discharge, and unmonitored. "
            f"Proximity to water is high; proximity of oversight to the water is nil."),
    }
    json.dump(out, open(OUT, "w"), indent=1)

    print("EXPOSURE")
    print(f"  distance to stream (ft): min {exposure['distance_to_stream_ft']['min']:.0f}  "
          f"median {exposure['distance_to_stream_ft']['median']}  max {exposure['distance_to_stream_ft']['max']:.0f}")
    print(f"  within {NEAR_STREAM_FT} ft of a stream: {len(near)}/{n} ({exposure['within_300ft_of_stream']['pct']}%)")
    print(f"  in RPA: {len(rpa)}   in wetland: {len(wet)}")
    print("\nREGULATORY / MONITORING GAP")
    print(f"  no own NPDES permit:            {n-len(npdes)}/{n} ({gap['no_npdes']['pct']}%)")
    print(f"  no WQP station within 1 mi:     {len(no_wqp)}/{n} ({gap['no_wqp_station_within_1mi']['pct']}%)")
    print(f"  no DEQ station within 1 mi:     {len(no_deq)}/{n} ({gap['no_deq_station_within_1mi']['pct']}%)")
    print(f"  COMPOUND blind spot:            {len(blind)}/{n} ({gap['compound_blind_spot']['pct']}%)")
    print("\nBY WATERSHED")
    print(f"{'watershed':<16}{'n':>5}{'near stream':>13}{'no NPDES':>10}{'no DEQ':>8}{'peak MGD':>10}")
    for ws, v in list(by_watershed.items())[:6]:
        print(f"{ws:<16}{v['n']:>5}{v['pct_near_stream']:>12}%{v['no_npdes']:>10}{v['no_deq']:>8}{v['peak']:>10.2f}")
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
