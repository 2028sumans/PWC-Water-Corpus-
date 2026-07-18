"""
Reconstruct parcels_scored.geojson without running the full geopandas
preprocessing pipeline. The two ingredients survived the deletion:
  - Parcel.geojson — has the geometry, keyed by GPIN
  - parcels_scored.json — has every scoring attribute, also keyed by GPIN

We just inner-join on GPIN, replace each feature's properties with the
scored record, and write back. Peak memory ~3 GB (both files held in RAM
+ Python overhead) which is fine on any modern Mac.
"""

import json
import os
import time

SCORED_JSON = "/Users/2028sumans/Desktop/Vira Systems UI/vira-ui/public/data/parcels_scored.json"
PARCEL_GEOJSON = "/Users/2028sumans/Desktop/Vira Systems UI/Prince William County/Enviro + Permitting Risk/Parcel.geojson"
OUT_GEOJSON = "/Users/2028sumans/Desktop/Vira Systems UI/vira-ui/public/data/parcels_scored.geojson"

t0 = time.time()

print(f"[{time.time()-t0:5.1f}s] Loading parcels_scored.json ({os.path.getsize(SCORED_JSON)/1024/1024:.0f} MB)...")
with open(SCORED_JSON) as f:
    scored = json.load(f)
print(f"[{time.time()-t0:5.1f}s]   {len(scored):,} scored records")

scored_by_gpin = {p["GPIN"]: p for p in scored if p.get("GPIN")}
print(f"[{time.time()-t0:5.1f}s]   {len(scored_by_gpin):,} unique GPINs in lookup")
del scored  # free the list, keep the dict

print(f"[{time.time()-t0:5.1f}s] Loading Parcel.geojson ({os.path.getsize(PARCEL_GEOJSON)/1024/1024:.0f} MB) — this takes ~30s...")
with open(PARCEL_GEOJSON) as f:
    geo = json.load(f)
feats = geo["features"]
print(f"[{time.time()-t0:5.1f}s]   {len(feats):,} features")

print(f"[{time.time()-t0:5.1f}s] Joining scored attributes by GPIN...")
matched = 0
missing = 0
for feat in feats:
    gpin = (feat.get("properties") or {}).get("GPIN")
    rec = scored_by_gpin.get(gpin)
    if rec is not None:
        # Replace the entire properties dict with the scored record — this
        # mirrors what preprocess_score_parcels.py writes (the GeoDataFrame
        # carries the joined attributes, not the original parcel-layer ones).
        feat["properties"] = rec
        matched += 1
    else:
        missing += 1
print(f"[{time.time()-t0:5.1f}s]   matched={matched:,}  unmatched={missing:,}")

print(f"[{time.time()-t0:5.1f}s] Writing {OUT_GEOJSON}...")
with open(OUT_GEOJSON, "w") as f:
    json.dump(geo, f, separators=(",", ":"))  # compact, no whitespace — saves ~30 MB
size_mb = os.path.getsize(OUT_GEOJSON) / 1024 / 1024
print(f"[{time.time()-t0:5.1f}s]   wrote {size_mb:.1f} MB")
print(f"[{time.time()-t0:5.1f}s] DONE")
