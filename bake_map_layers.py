#!/usr/bin/env python3
"""
Bake PMTiles for every water-relevant PWC spatial overlay the map renders.

Tippecanoe converts each GeoJSON to a single-file vector tile archive served
through /api/tiles/[file]. Layer set matches src/lib/mapLayerRegistry.ts —
hydrology (watersheds/streams/hydrology/rpa/springs/surface temp/tidal flow/
Cedar Run gage/groundwater well), hazard & stormwater (segments/structures/
dam/soil), disclosure (NPDES facilities/DC buildings/DC projects), monitoring
(WQP/DEQ/iNaturalist), and power & land (transmission/zoning/use permits/
BZA/pending/LRLU/protected/state land).

The main parcels.pmtiles layer is baked separately (see README.md) once
parcels_scored.geojson exists, because it needs the --include= attribute
whitelist from the scoring pipeline, not this script's generic path.

Run: python3 bake_map_layers.py
"""
import csv
import io
import json
import os
import subprocess
import time
import zipfile

import pandas as pd

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("PWC_DATA_ROOT", os.path.join(_SCRIPT_DIR, "data", "water_raw"))
OUT_DIR = os.environ.get("VIRA_TILES_ROOT", os.path.join(_SCRIPT_DIR, "public", "tiles"))
TMP_DIR = os.path.join(_SCRIPT_DIR, "data", "_tile_tmp")

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)


def t(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def rp(name: str) -> str:
    return os.path.join(DATA_ROOT, name)


def bake(layer_name: str, geojson_path: str) -> None:
    output = f"{OUT_DIR}/{layer_name}.pmtiles"
    t(f"  baking {layer_name} from {os.path.basename(geojson_path)} -> {output}")
    subprocess.run(
        [
            "tippecanoe", "-o", output, "--layer", layer_name,
            "--minimum-zoom", "8", "--maximum-zoom", "14",
            "--drop-densest-as-needed", "--extend-zooms-if-still-dropping", "--force",
            geojson_path,
        ],
        check=True,
        stderr=subprocess.DEVNULL,
    )
    size_mb = os.path.getsize(output) / 1024 / 1024
    t(f"    {layer_name}.pmtiles -> {size_mb:.2f} MB")


# Layers that need no conversion — bake the raw water_raw GeoJSON directly.
DIRECT_LAYERS: list[tuple[str, str]] = [
    ("watersheds",        rp("Watersheds.geojson")),
    ("streams",           rp("Stream.geojson")),
    ("hydrology",         rp("Hydrological_Features.geojson")),
    ("rpa",                rp("Resource_Protection_Areas_(RPA).geojson")),
    ("springs",           rp("Springs_Groundwater_Layers.geojson")),
    ("surface_temp",      rp("SURFACE_WATER_TEMPERATURE.geojson")),
    ("tidal_flow",        rp("Tidal_flow_paths_(WQS).geojson")),
    ("stormwater_seg",    rp("Stormwater_Segments.geojson")),
    ("stormwater_struct", rp("Stormwater_Management_Structures.geojson")),
    ("dam",               rp("Dam_Break_Inundation.geojson")),
    ("soil",              rp("Soil.geojson")),
    ("dc_buildings",      rp("Data_Center_Buildings.geojson")),
    ("dc_projects",       rp("Data_Center_Projects.geojson")),
    ("deq_monitoring",    rp("Water_Quality_Monitoring_Plan_Stations_(Current).geojson")),
    ("zoning",            rp("Zoning_Districts.geojson")),
    ("use_permits",       rp("Use_Permits.geojson")),
    ("bza",               rp("Zoning_Appeals_and_Variances.geojson")),
    ("pending",           rp("Planning_Pending_Cases.geojson")),
    ("lrlu",              rp("LRLU_Developable_Areas.geojson")),
    ("protected",         rp("Protected_Open_Space.geojson")),
    ("state_land",        rp("State_Land.geojson")),
]


def csv_latlon_to_geojson(csv_path, lat_col, lon_col, out_path, keep_cols=None, filter_fn=None):
    """Convert a lat/lon CSV to a Point GeoJSON FeatureCollection."""
    df = pd.read_csv(csv_path, low_memory=False)
    if filter_fn is not None:
        df = filter_fn(df)
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    cols = keep_cols or [c for c in df.columns if c not in (lat_col, lon_col)]
    features = []
    for _, row in df.iterrows():
        props = {c: (None if pd.isna(row[c]) else row[c]) for c in cols if c in df.columns}
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [row[lon_col], row[lat_col]]},
            "properties": props,
        })
    with open(out_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)
    return len(features)


def bake_wqp_stations() -> None:
    t("Converting WQP stations (VA) -> GeoJSON...")
    out_path = f"{TMP_DIR}/wqp_stations.geojson"
    n = csv_latlon_to_geojson(
        rp("station.csv"), "LatitudeMeasure", "LongitudeMeasure", out_path,
        keep_cols=["MonitoringLocationIdentifier", "MonitoringLocationName", "MonitoringLocationTypeName"],
        filter_fn=lambda df: df[df["StateCode"].astype(str) == "51"],
    )
    t(f"  {n} WQP stations")
    bake("wqp_stations", out_path)


def bake_inat_observations() -> None:
    t("Converting iNaturalist observations -> GeoJSON...")
    df_head = pd.read_csv(rp("observations-759582.csv"), nrows=1)
    lat_col = "latitude" if "latitude" in df_head.columns else [c for c in df_head.columns if "lat" in c.lower()][0]
    lon_col = "longitude" if "longitude" in df_head.columns else [c for c in df_head.columns if "lon" in c.lower()][0]
    keep = [c for c in ["scientific_name", "common_name", "observed_on", "iconic_taxon_name"] if c in df_head.columns]
    out_path = f"{TMP_DIR}/inat_observations.geojson"
    n = csv_latlon_to_geojson(rp("observations-759582.csv"), lat_col, lon_col, out_path, keep_cols=keep or None)
    t(f"  {n} iNaturalist observations")
    bake("inat_obs", out_path)


def bake_npdes_facilities() -> None:
    t("Converting NPDES facilities (PWC-filtered) -> GeoJSON...")
    out_path = f"{TMP_DIR}/npdes_facilities.geojson"
    n = csv_latlon_to_geojson(
        rp("ICIS_FACILITIES_VA.csv"), "GEOCODE_LATITUDE", "GEOCODE_LONGITUDE", out_path,
        keep_cols=["NPDES_ID", "FACILITY_NAME", "FACILITY_TYPE_CODE", "CITY"],
        filter_fn=lambda df: df[df["COUNTY_CODE"].astype(str) == "VA153"],
    )
    t(f"  {n} PWC NPDES facilities")
    bake("npdes_facilities", out_path)


def bake_single_point_layer(layer_name, metadata_csv, out_path):
    """Cedar Run gage / groundwater well — single-station USGS monitoring
    locations. metadata CSV has x/y (lon/lat) columns."""
    df = pd.read_csv(metadata_csv)
    row = df.iloc[0]
    feature = {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(row["x"]), float(row["y"])]},
        "properties": {
            "id": row.get("id"),
            "monitoring_location_name": row.get("monitoring_location_name"),
            "site_type": row.get("site_type"),
        },
    }
    with open(out_path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": [feature]}, f)
    bake(layer_name, out_path)


def main() -> None:
    t(f"Baking {len(DIRECT_LAYERS)} direct layers -> {OUT_DIR}")
    for name, path in DIRECT_LAYERS:
        if not os.path.exists(path):
            t(f"  SKIP {name}: source file not found at {path}")
            continue
        bake(name, path)

    bake_wqp_stations()
    bake_inat_observations()
    bake_npdes_facilities()
    bake_single_point_layer("cedar_run_gage", rp(os.path.join("cedar_run_gage", "monitoring-location-metadata.csv")), f"{TMP_DIR}/cedar_run_gage.geojson")
    bake_single_point_layer("gw_well", rp(os.path.join("groundwater_well", "monitoring-location-metadata.csv")), f"{TMP_DIR}/gw_well.geojson")

    total_mb = sum(
        os.path.getsize(os.path.join(OUT_DIR, f)) for f in os.listdir(OUT_DIR) if f.endswith(".pmtiles")
    ) / 1024 / 1024
    t(f"DONE. Total tiles size: {total_mb:.1f} MB")


if __name__ == "__main__":
    main()
