#!/usr/bin/env python3
"""
Compute the Water Legibility Score inputs for every parcel in Prince William
County — how knowable each parcel's water relationship to data-center
infrastructure is from public data.

Spatial-joins Parcel.geojson against watershed / hydrology / drought /
disclosure / monitoring / stormwater layers, then writes the per-parcel
attribute bag that synthesizeSubScores.ts (TypeScript, client-side) turns
into the 7 sub-scores. This script does NOT compute the sub-scores itself —
it only produces the raw joined attributes + a sort-bootstrap hint.

Outputs:
  - public/data/parcels_scored.geojson  (full geometry + attrs, for tippecanoe)
  - public/data/parcels_scored.json     (lightweight per-parcel records for the Terminal;
                                          gzip -k -f this afterward per README.md)

Raw source data lives flat in data/water_raw/ (see .gitignore — not committed,
~1.2 GB). Override via PWC_DATA_ROOT / VIRA_OUT_ROOT env vars if your layout
differs.
"""
import csv
import io
import json
import math
import os
import time
import warnings
import zipfile

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_ROOT = os.environ.get("PWC_DATA_ROOT", os.path.join(_SCRIPT_DIR, "data", "water_raw"))
OUT_ROOT = os.environ.get("VIRA_OUT_ROOT", os.path.join(_SCRIPT_DIR, "public", "data"))
os.makedirs(OUT_ROOT, exist_ok=True)


def t(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def p(name):
    return os.path.join(DATA_ROOT, name)


# -- Helpers (kept from Vira's preprocessing — same battle-tested patterns) --

def centroid_join(parcels, layer, agg="any", val_col=None):
    """For each parcel, find whether its centroid falls within any feature of
    `layer`, or the value of a column from the first matching feature."""
    if len(layer) == 0:
        return pd.Series(False, index=parcels.index) if agg == "any" else pd.Series(None, index=parcels.index)
    parcel_centroids = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    joined = gpd.sjoin(parcel_centroids, layer, how="inner", predicate="within")
    if agg == "any":
        matched = pd.Series(False, index=parcels.index)
        matched.loc[joined["_pidx"].unique()] = True
        return matched
    elif agg == "first" and val_col:
        result = joined.groupby("_pidx")[val_col].first()
        return parcels.index.map(result)
    return None


def count_nearby(parcels, layer, radius_mi):
    """Count features of `layer` within `radius_mi` of each parcel centroid."""
    if len(layer) == 0:
        return pd.Series(0, index=parcels.index, dtype="int32")
    buf = layer[["geometry"]].copy()
    buf["geometry"] = layer.geometry.buffer(radius_mi * 1609.344)
    parcel_pts = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    joined = gpd.sjoin(parcel_pts, buf, how="left", predicate="within")
    matches = joined.dropna(subset=["index_right"])
    counts = matches.groupby("_pidx").size()
    return counts.reindex(parcels.index, fill_value=0).astype("int32")


def nearest_distance_ft(parcels, layer):
    """Distance in feet from each parcel centroid to the nearest feature of `layer`."""
    if len(layer) == 0:
        return pd.Series(None, index=parcels.index, dtype="float64")
    parc_pts = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    simple = layer[["geometry"]].copy()
    nearest = gpd.sjoin_nearest(parc_pts, simple, how="left", distance_col="_dist_m")
    dist_per_parcel = nearest.groupby("_pidx")["_dist_m"].min()
    return (parcels.index.map(dist_per_parcel) * 3.28084).round(0)


def points_from_latlon(df, lat_col, lon_col, crs="EPSG:4326"):
    """Build a GeoDataFrame of points from lat/lon columns, dropping bad rows."""
    df = df.copy()
    df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
    df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")
    df = df.dropna(subset=[lat_col, lon_col])
    geom = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
    return gpd.GeoDataFrame(df, geometry=geom, crs=crs).to_crs("EPSG:5070")


def latest_value(json_path):
    """NOAA-style time series JSON: {"data": {"YYYYMM": {"value": X}, ...}}.
    Returns the most recent numeric value, or None. Correct for point-in-time
    indices (Palmer drought indices, monthly temperature) — NOT for
    cumulative metrics like degree-days or precipitation, where a single
    month's value is not comparable to an annual threshold/normal. Use
    trailing_12mo_sum() for those."""
    if not os.path.exists(json_path):
        return None
    with open(json_path) as f:
        d = json.load(f)
    data = d.get("data", {})
    if not data:
        return None
    latest_key = max(data.keys())
    v = data[latest_key].get("value")
    try:
        v = float(v)
    except (TypeError, ValueError):
        return None
    # NOAA uses -99.99 / -999 as missing-data sentinels for some series.
    if v <= -99:
        return None
    return v


def trailing_12mo_sum(json_path):
    """Same NOAA JSON shape as latest_value(), but sums the most recent 12
    monthly values — the right aggregation for cumulative annual metrics
    (cooling/heating degree days, precipitation, snowfall). Taking a single
    month's CDD (e.g. "29" in April) against an annual threshold like 1500
    silently makes every CDD-based adjustment a no-op; summing gives the
    actual trailing-year total the plan's thresholds were calibrated against."""
    if not os.path.exists(json_path):
        return None
    with open(json_path) as f:
        d = json.load(f)
    data = d.get("data", {})
    if not data:
        return None
    keys = sorted(data.keys())[-12:]
    total, n = 0.0, 0
    for k in keys:
        v = data[k].get("value")
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        if v <= -99:
            continue
        total += v
        n += 1
    return round(total, 2) if n > 0 else None


def latest_csv_time_series_value(csv_path, value_col_candidates):
    """USGS NWIS-style time series CSV. Returns the last non-null numeric
    value found in the first matching column name."""
    if not os.path.exists(csv_path):
        return None
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return None
    for col in value_col_candidates:
        if col in df.columns:
            series = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(series):
                return float(series.iloc[-1])
    return None


t("=== PWC Water Atlas — parcel preprocessing ===")
t(f"DATA_ROOT={DATA_ROOT}")


# -- 1. Load parcels ------------------------------------------------------

t("Loading Parcel.geojson (159k features)...")
parcels = gpd.read_file(p("Parcel.geojson"))
t(f"  loaded {len(parcels):,} parcels")
parcels = parcels.to_crs("EPSG:5070")
parcels["centroid"] = parcels.geometry.centroid
parcels["acres_calc"] = parcels.geometry.area / 4046.8564224


# -- 2. Data center context (kept from Vira — same source files) ---------

t("Loading DC buildings + projects...")
dc_buildings = gpd.read_file(p("Data_Center_Buildings.geojson")).to_crs("EPSG:5070")
dc_projects = gpd.read_file(p("Data_Center_Projects.geojson")).to_crs("EPSG:5070")
t(f"  dc_buildings={len(dc_buildings)} dc_projects={len(dc_projects)}")

t("Computing DC campus membership...")
parcels["_inside_dc_campus"] = centroid_join(parcels, dc_projects[["geometry"]], agg="any")
name_col = "CaseName" if "CaseName" in dc_projects.columns else None
if name_col:
    parcels["dc_campus_name"] = centroid_join(parcels, dc_projects[[name_col, "geometry"]], agg="first", val_col=name_col)
else:
    parcels["dc_campus_name"] = None
t(f"  {parcels['_inside_dc_campus'].sum():,} parcels inside a planned DC campus polygon")

t("Computing parcel ∩ DC building polygon (point-in-parcel)...")
parc_geom = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels.geometry, crs="EPSG:5070")
bj = gpd.sjoin(dc_buildings[["BuildingName", "geometry"]], parc_geom, how="inner", predicate="within")
n_bldgs_lookup = bj.groupby("_pidx").size().to_dict()
parcels["n_dc_buildings"] = parcels.index.map(n_bldgs_lookup).fillna(0).astype("int16")
parcels["_inside_dc_building"] = parcels["n_dc_buildings"] > 0
name_lookup_dcb = bj.groupby("_pidx")["BuildingName"].first().to_dict()
parcels["dc_building_name"] = parcels.index.map(name_lookup_dcb)
t(f"  {int(parcels['_inside_dc_building'].sum()):,} parcels with built DCs (max {int(parcels['n_dc_buildings'].max())} on one parcel)")


# -- 3. Watershed join (spatial join, not nearest-distance) --------------

t("Loading Watersheds.geojson...")
watersheds = gpd.read_file(p("Watersheds.geojson")).to_crs("EPSG:5070")
t(f"  {len(watersheds)} watershed polygons")

t("Computing watershed membership...")
ws_cols = ["WatershedID", "WatershedName", "ACRES", "geometry"]
major_shed_col = "MajorShed" if "MajorShed" in watersheds.columns else None
if major_shed_col:
    ws_cols.insert(-1, major_shed_col)
wm_plan_col = "WMPlanNumber" if "WMPlanNumber" in watersheds.columns else None
if wm_plan_col:
    ws_cols.insert(-1, wm_plan_col)
parc_pts_ws = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
ws_join = gpd.sjoin(parc_pts_ws, watersheds[ws_cols], how="left", predicate="within")
ws_join = ws_join.drop_duplicates(subset="_pidx")
watershed_id_map = ws_join.set_index("_pidx")["WatershedID"]
watershed_name_map = ws_join.set_index("_pidx")["WatershedName"]
watershed_acres_map = ws_join.set_index("_pidx")["ACRES"]
parcels["watershed_id"] = parcels.index.map(watershed_id_map)
parcels["watershed_name"] = parcels.index.map(watershed_name_map)
parcels["watershed_acres"] = parcels.index.map(watershed_acres_map)
if major_shed_col:
    parcels["watershed_major_basin"] = parcels.index.map(ws_join.set_index("_pidx")[major_shed_col])
else:
    parcels["watershed_major_basin"] = None
# A lead, not a document: WMPlanNumber references the specific PWC Watershed
# Management Plan section covering this basin. No fetchable URL exists in
# this corpus to resolve it to actual plan text (same class of problem as
# the permit-PDF StaffReportLink, at smaller scale) — exposed as a citable
# reference for manual lookup, not integrated content.
if wm_plan_col:
    parcels["watershed_mgmt_plan_number"] = parcels.index.map(ws_join.set_index("_pidx")[wm_plan_col])
else:
    parcels["watershed_mgmt_plan_number"] = None
t(f"  {parcels['watershed_id'].notna().sum():,} parcels matched to a watershed")

t("Computing n_dc_in_watershed (cumulative DC stress per basin) + n_dc_in_major_basin (cross-watershed rollup)...")
dc_watershed = parcels.loc[parcels["_inside_dc_building"], "watershed_id"].value_counts()
parcels["n_dc_in_watershed"] = parcels["watershed_id"].map(dc_watershed).fillna(0).astype("int32")
dc_basin = parcels.loc[parcels["_inside_dc_building"], "watershed_major_basin"].value_counts()
parcels["n_dc_in_major_basin"] = parcels["watershed_major_basin"].map(dc_basin).fillna(0).astype("int32")
t(f"  max DCs sharing one watershed: {int(parcels['n_dc_in_watershed'].max())}; max sharing one major basin: {int(parcels['n_dc_in_major_basin'].max())}")


# -- 4. Hydrology proximity (nearest-distance) ----------------------------

t("Loading stream / hydrology / surface-temp / RPA layers...")
stream = gpd.read_file(p("Stream.geojson")).to_crs("EPSG:5070")
hydro = gpd.read_file(p("Hydrological_Features.geojson")).to_crs("EPSG:5070")
surftemp = gpd.read_file(p("SURFACE_WATER_TEMPERATURE.geojson")).to_crs("EPSG:5070")
rpa = gpd.read_file(p("Resource_Protection_Areas_(RPA).geojson")).to_crs("EPSG:5070")
t(f"  stream={len(stream)} hydro={len(hydro)} surftemp={len(surftemp)} rpa={len(rpa)}")

t("Computing distance to nearest stream (RPA buffer trigger ~100ft)...")
parcels["d_stream_ft"] = nearest_distance_ft(parcels, stream)
t(f"  median {parcels['d_stream_ft'].median():.0f} ft")

# StreamType (a numeric order/classification code, values 2-6 observed) was
# never read in the original pass — distance alone can't distinguish a
# low-order headwater ditch from a higher-order river, but the two have very
# different assimilative capacity for any discharge. Attach it (+ the named
# StreamName where present) from the nearest segment alongside the distance
# already computed above.
stream_cols = [c for c in ["StreamType", "StreamName"] if c in stream.columns]
if stream_cols:
    parc_pts_str = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    str_nearest = gpd.sjoin_nearest(parc_pts_str, stream[stream_cols + ["geometry"]], how="left", distance_col="_d")
    str_nearest = str_nearest.drop_duplicates(subset="_pidx")
    if "StreamType" in stream_cols:
        parcels["stream_order"] = pd.to_numeric(parcels.index.map(str_nearest.set_index("_pidx")["StreamType"]), errors="coerce")
    if "StreamName" in stream_cols:
        parcels["stream_name"] = parcels.index.map(str_nearest.set_index("_pidx")["StreamName"])

t("Computing distance to nearest hydrological feature...")
parcels["d_hydro_ft"] = nearest_distance_ft(parcels, hydro)

# Springs_Groundwater_Layers.geojson is deliberately NOT joined here — neither
# its chemistry nor a distance-to-spring. Both were attached by an earlier pass
# and have been removed.
#
# The layer is a statewide VA ambient groundwater-geochemistry archive (2,916
# points, median sample date 2002, oldest 1928), and it is not merely "mostly
# outside PWC" — it is a different hydrogeologic province:
#
#   GPROV    Valley and Ridge 1,648 · Blue Ridge 1,091 · Coastal Plain 110 ·
#            Piedmont 48
#   CNTYSDB  Clarke 651 · Page 559 · Rockingham 286 · Rappahannock 203 · Warren 193
#   LITH     C-O-CARBONATES 467 · O-BEEKMANTOWN 341 · C-DOLOMITES 340
#   ALTITUDE mean 1,578 ft (Prince William tops out near 640 ft)
#
# That is Shenandoah Valley carbonate karst. Prince William is Piedmont
# crystalline/saprolite and Triassic-basin sediment. Hardness, specific
# conductance and pH from a dolomite aquifer are not just uninformative about a
# PWC parcel, they are biased high in a known direction, so labelling them "the
# last documented reading" for that parcel is misleading rather than cautious.
#
# The join's actual behaviour is worse than the province mismatch suggests.
# Measured against Parcel.geojson (159,181 parcels), nearest-neighbour never
# reaches the karst — it collapses onto a single well:
#
#   158,790 parcels (99.8%) resolve to ONE point, the lone PWC well
#           (GPROV PIEDMONT, LITH MPT), sampled 24 Jun 1980
#       391 parcels  (0.2%) resolve to one Caroline County Coastal Plain point
#   PH and SPCOND resolve to a non-null value for 0 parcels; NO3NO2 for 391,
#           all of them the -0.01 below-detection sentinel (which the old code
#           scrubbed -9999 but not -0.01, so it shipped as a nitrate reading)
#   HARD    attaches 260 mg/L — that one 1980 number — to all 158,790
#
# So the shipped "chemistry" was a single 46-year-old hardness value broadcast
# countywide as a per-parcel attribute, flanked by two permanently empty columns.
#
# Restricting the source to GPROV in ("PIEDMONT", "COASTAL PLAIN") was tested
# and is a verified no-op: both points the join lands on already pass that
# filter, so all 159,181 parcels keep an identical distance and an identical
# hardness. Restriction cannot fix this; only removal can. Of the 158
# Piedmont/Coastal Plain points statewide just 70 carry any of PH/SPCOND/HARD,
# at a median 93 mi from the county, so there is no local subset to fall back to.
#
# d_spring_ft went with the chemistry. With 99.8% of parcels resolving to that
# one 1980 well it is a radial coordinate around a single arbitrary point
# (0.2-23.2 mi), not proximity to a monitored groundwater feature — and it read
# as the latter in the facility dossier, where it was carried as water context.
#
# Nothing in this corpus supplies Piedmont groundwater chemistry for PWC at
# parcel resolution. The honest output is no column. Do not re-add either
# feature from this layer.

t("Computing distance to nearest surface-water-temperature station + its warming trend...")
parcels["d_surftemp_ft"] = nearest_distance_ft(parcels, surftemp)
# VA DEQ pre-computes a Mann-Kendall / Theil-Sen trend test per monitoring
# station (Tau = correlation strength, TheilSen_slope = deg F/year, Trend =
# DEGRADING/NO TREND/IMPROVING label, Pvalcovs = significance). This is a
# real, already-tested climate-warming signal per stream — attach the
# NEAREST station's trend fields, not just its distance.
parc_pts_st = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
st_cols = [c for c in ["Trend", "Tau", "TheilSen_slope", "Pvalcovs", "Stream", "Station"] if c in surftemp.columns]
st_nearest = gpd.sjoin_nearest(parc_pts_st, surftemp[st_cols + ["geometry"]], how="left", distance_col="_d")
st_nearest = st_nearest.drop_duplicates(subset="_pidx")
for c in st_cols:
    parcels[f"surftemp_{c.lower()}"] = parcels.index.map(st_nearest.set_index("_pidx")[c])
n_degrading = (parcels["surftemp_trend"] == "DEGRADING").sum() if "surftemp_trend" in parcels.columns else 0
t(f"  {n_degrading:,} parcels' nearest gauged stream shows a DEGRADING (statistically tested warming) trend")

t("Computing RPA + wetland (Hydrological_Features) centroid membership...")
parcels["_rpa"] = centroid_join(parcels, rpa[["geometry"]], agg="any")
parcels["_wetland"] = centroid_join(parcels, hydro[["geometry"]], agg="any")
t(f"  rpa={int(parcels['_rpa'].sum()):,} wetland={int(parcels['_wetland'].sum()):,}")

t("Loading tidal flow paths...")
tidal = gpd.read_file(p("Tidal_flow_paths_(WQS).geojson")).to_crs("EPSG:5070")
t(f"  {len(tidal)} tidal flow path segments")
d_tidal = nearest_distance_ft(parcels, tidal)
parcels["_in_tidal_flow_path"] = d_tidal.fillna(1e9) < 100
# This is a STATEWIDE Virginia Water Quality Standards layer (segments as
# far away as the James/Blackwater/Nansemond show up in an unfiltered
# sample) — the boolean above is the geometrically valid part. Where a
# parcel actually is within the 100ft trigger, attach the segment's real
# VA WQS CLASS/ZONE rather than leaving it a bare flag: CLASS governs how
# much thermal/blowdown load the segment can legally accept, i.e. whether a
# Scope-1 discharge is even permittable there. PWC is mostly non-tidal, so
# this only resolves to a real value for the county's Potomac-adjacent
# parcels — elsewhere it's correctly null.
tidal_cols = [c for c in ["CLASS", "ZONE"] if c in tidal.columns]
if tidal_cols:
    parc_pts_td = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    td_nearest = gpd.sjoin_nearest(parc_pts_td, tidal[tidal_cols + ["geometry"]], how="left", distance_col="_d")
    td_nearest = td_nearest.drop_duplicates(subset="_pidx")
    in_range = parcels["_in_tidal_flow_path"]
    for c in tidal_cols:
        vals = parcels.index.map(td_nearest.set_index("_pidx")[c])
        parcels[f"tidal_{c.lower()}"] = pd.Series(vals, index=parcels.index).where(in_range, None)


# -- 5. Dam-break + soil (kept from Vira, centroid_join) ------------------

t("Loading dam-break + soil layers...")
dam = gpd.read_file(p("Dam_Break_Inundation.geojson")).to_crs("EPSG:5070")
soil = gpd.read_file(p("Soil.geojson")).to_crs("EPSG:5070")
t(f"  dam={len(dam)} soil={len(soil)}")

t("Computing dam-break inundation membership + hazard tier...")
# The file carries a native HAZ_CLASS field (HIGH/SIGNIFICANT) — an earlier
# pass assumed it didn't exist and reconstructed a tier from PMF_VALUE
# instead. Use the county's own classification directly rather than a
# derived proxy.
parcels["_dam"] = centroid_join(parcels, dam[["geometry"]], agg="any")
if "HAZ_CLASS" in dam.columns:
    parcels["dam_haz_class"] = centroid_join(parcels, dam[["HAZ_CLASS", "geometry"]], agg="first", val_col="HAZ_CLASS")
else:
    dam = dam.copy()
    dam["_haz"] = dam["PMF_VALUE"].apply(lambda v: "HIGH" if pd.to_numeric(v, errors="coerce") == 1 else "SIG")
    parcels["dam_haz_class"] = centroid_join(parcels, dam[["_haz", "geometry"]], agg="first", val_col="_haz")
t(f"  {int(parcels['_dam'].sum()):,} parcels inside dam-inundation zones")

t("Computing soil construction category + hydrologic group + erosion/permeability...")
parcels["soil_cat"] = centroid_join(parcels, soil[["SoilConstructionCategory", "geometry"]], agg="first", val_col="SoilConstructionCategory")
# HydrologicSoilGroup (A=high infiltration/low runoff ... D=low infiltration/
# high runoff), ErosionSusceptibility, and Permeability were extracted by
# the original Vira preprocessing but dropped in the first water-tool pass —
# all three are real, unused signal for stormwaterBurden (a D-group,
# high-erosion parcel sheds more runoff/sediment to receiving streams).
parcels["hsg"] = centroid_join(parcels, soil[["HydrologicSoilGroup", "geometry"]], agg="first", val_col="HydrologicSoilGroup")
parcels["erosion_susceptibility"] = centroid_join(parcels, soil[["ErosionSusceptibility", "geometry"]], agg="first", val_col="ErosionSusceptibility")
parcels["soil_permeability"] = centroid_join(parcels, soil[["Permeability", "geometry"]], agg="first", val_col="Permeability")
# No standalone land-cover layer in this export; impervious-cover proxy comes
# from stormwater burden signals computed below instead. Leave land_cover
# null unless a future pass adds Land_Cover_2017.geojson.
parcels["land_cover"] = None


# -- 6. Stormwater (kept from Vira — segments/facilities/structures) ------

t("Loading stormwater layers...")
sw_segments = gpd.read_file(p("Stormwater_Segments.geojson")).to_crs("EPSG:5070")
sw_structures = gpd.read_file(p("Stormwater_Management_Structures.geojson")).to_crs("EPSG:5070")
t(f"  sw_segments={len(sw_segments)} sw_structures={len(sw_structures)}")

t("Counting stormwater segments intersecting each parcel...")
ew_col = "EasementWidth" if "EasementWidth" in sw_segments.columns else None
sw_buf = sw_segments[["geometry"]].copy()
half_width_m = (pd.to_numeric(sw_segments[ew_col], errors="coerce").fillna(25) if ew_col else 25) * 0.3048 / 2.0
sw_buf["geometry"] = sw_segments.geometry.buffer(half_width_m)
parc_geom2 = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels.geometry, crs="EPSG:5070")
sj = gpd.sjoin(parc_geom2, sw_buf[["geometry"]], how="left", predicate="intersects")
parcels["sw_segments"] = sj.dropna(subset=["index_right"]).groupby("_pidx").size().reindex(parcels.index, fill_value=0).astype("int32")

t("Counting stormwater management structures inside each parcel...")
struct_pts = gpd.GeoDataFrame({"_sidx": sw_structures.index}, geometry=sw_structures.geometry, crs="EPSG:5070")
parc_geom3 = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels.geometry, crs="EPSG:5070")
sjs = gpd.sjoin(struct_pts, parc_geom3, how="inner", predicate="within")
parcels["sw_structures"] = sjs.groupby("_pidx").size().reindex(parcels.index, fill_value=0).astype("int32")

# No standalone stormwater FACILITIES (detention-basin polygon) layer in this
# export — approximate with high-density structure clusters (5+ structures on
# a parcel behaves like a basin site for the stormwaterBurden sub-score).
parcels["sw_facilities"] = (parcels["sw_structures"] >= 5).astype("int32")
t(f"  segments: {(parcels['sw_segments']>0).sum():,} parcels; structures: {(parcels['sw_structures']>0).sum():,} parcels")


# -- 7. Community monitoring: WQP stations + DEQ monitoring + iNaturalist -

t("Loading WQP stations, DEQ monitoring stations, iNaturalist observations...")
station_df = pd.read_csv(p("station.csv"), low_memory=False)
station_df = station_df[(station_df["StateCode"].astype(str) == "51")]
wqp_stations = points_from_latlon(station_df, "LatitudeMeasure", "LongitudeMeasure")
t(f"  WQP VA stations: {len(wqp_stations)}")

deq_monitoring = gpd.read_file(p("Water_Quality_Monitoring_Plan_Stations_(Current).geojson")).to_crs("EPSG:5070")
t(f"  DEQ monitoring stations: {len(deq_monitoring)}")

inat_df = pd.read_csv(p("observations-759582.csv"), low_memory=False)
lat_col = "latitude" if "latitude" in inat_df.columns else [c for c in inat_df.columns if "lat" in c.lower()][0]
lon_col = "longitude" if "longitude" in inat_df.columns else [c for c in inat_df.columns if "lon" in c.lower()][0]
inat_pts = points_from_latlon(inat_df, lat_col, lon_col)
t(f"  iNaturalist observations: {len(inat_pts)}")

t("Counting monitoring coverage within 1 mile of each parcel...")
parcels["n_wqp_stations_1mi"] = count_nearby(parcels, wqp_stations, 1.0)
parcels["n_deq_monitoring_1mi"] = count_nearby(parcels, deq_monitoring, 1.0)
parcels["n_inat_1mi"] = count_nearby(parcels, inat_pts, 1.0)

# The DEQ monitoring layer's station count alone treats every station as
# equally capable — it isn't. STA_LV4_CODE='GAGE' flags an actual stream
# flow-measurement point (the only lead to a real low-flow statistic in the
# corpus); BENTHIC_N is a benthic-macroinvertebrate sample count, a second
# literature-established bioindicator (state stream biomonitoring is built
# on benthic community health) independent of the amphibian signal below.
if "STA_LV4_CODE" in deq_monitoring.columns:
    gage_stations = deq_monitoring[deq_monitoring["STA_LV4_CODE"] == "GAGE"]
    parcels["n_deq_gage_1mi"] = count_nearby(parcels, gage_stations, 1.0)
else:
    parcels["n_deq_gage_1mi"] = 0
if "BENTHIC_N" in deq_monitoring.columns:
    parc_pts_bn = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
    bn_nearest = gpd.sjoin_nearest(parc_pts_bn, deq_monitoring[["BENTHIC_N", "geometry"]], how="left", distance_col="_d")
    bn_nearest = bn_nearest.drop_duplicates(subset="_pidx")
    parcels["nearest_benthic_n"] = pd.to_numeric(parcels.index.map(bn_nearest.set_index("_pidx")["BENTHIC_N"]), errors="coerce")

# Research-grade-only amphibian density: iNaturalist observation effort is
# not uniform (denser near trails/population than near facilities), and
# unverified ("casual") IDs add species-level noise. quality_grade='research'
# is iNaturalist's own community-verified tier — filter to it before using
# density as a water-quality bioindicator signal (amphibians' permeable
# skin/eggs and cutaneous respiration make them USGS/EPA-documented water
# quality sentinels, not just a generic biodiversity count).
if "quality_grade" in inat_df.columns:
    inat_research = inat_pts[inat_pts["quality_grade"] == "research"]
    parcels["n_inat_research_1mi"] = count_nearby(parcels, inat_research, 1.0)
else:
    parcels["n_inat_research_1mi"] = parcels["n_inat_1mi"]

t(f"  wqp>0: {(parcels['n_wqp_stations_1mi']>0).sum():,}  deq>0: {(parcels['n_deq_monitoring_1mi']>0).sum():,}  "
  f"deq_gage>0: {(parcels['n_deq_gage_1mi']>0).sum():,}  inat>0: {(parcels['n_inat_1mi']>0).sum():,}  "
  f"inat_research>0: {(parcels['n_inat_research_1mi']>0).sum():,}")


# -- 8. NPDES / DEQ disclosure -------------------------------------------

t("Loading NPDES facility registry (VA-filtered) + NAICS crosswalk + violations...")
icis_va = pd.read_csv(p("ICIS_FACILITIES_VA.csv"), low_memory=False)
icis_pts = points_from_latlon(icis_va, "GEOCODE_LATITUDE", "GEOCODE_LONGITUDE")
t(f"  ICIS VA facilities with valid geocode: {len(icis_pts)}")

naics_dc = pd.read_csv(p("NPDES_NAICS_DATACENTER.csv"), low_memory=False)
dc_npdes_ids = set(naics_dc["NPDES_ID"])
t(f"  NPDES IDs nationally coded as data-center NAICS (518210): {len(dc_npdes_ids)}")

general_permits = pd.read_csv(p("ICIS_MASTER_GENERAL_PERMITS.csv"), low_memory=False)
permit_name_col = "EXTERNAL_PERMIT_NMBR"
deq_permit_ids = set(general_permits[permit_name_col].dropna()) if permit_name_col in general_permits.columns else set()

violations = pd.read_csv(p("VA_NPDES_EFF_VIOLATIONS.csv"), low_memory=False)
violation_counts = violations.groupby("NPDES_ID").size()
nodi_by_npdes = violations.dropna(subset=["NODI_CODE"]).groupby("NPDES_ID")["NODI_CODE"].last()

icis_pts["has_npdes"] = 1
icis_pts["has_deq_permit"] = icis_pts["NPDES_ID"].isin(deq_permit_ids).astype(int)
icis_pts["n_npdes_violations"] = icis_pts["NPDES_ID"].map(violation_counts).fillna(0).astype(int)
icis_pts["dmr_nodi_code"] = icis_pts["NPDES_ID"].map(nodi_by_npdes)
icis_pts["frs_id"] = icis_pts.get("FACILITY_UIN")

t("Joining NPDES facilities to their host parcel (point-in-parcel, 200ft fallback)...")
parc_geom4 = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels.geometry, crs="EPSG:5070")
npdes_within = gpd.sjoin(icis_pts, parc_geom4, how="inner", predicate="within")
# Facilities that don't land inside any parcel polygon (geocode imprecision)
# still count within 200ft of a parcel boundary.
unmatched = icis_pts.loc[~icis_pts.index.isin(npdes_within.index)]
if len(unmatched):
    near = gpd.sjoin_nearest(unmatched, parc_geom4, how="left", distance_col="_d", max_distance=60.96)  # 200ft in meters
    near = near.dropna(subset=["_pidx"])
    npdes_within = pd.concat([npdes_within, near], ignore_index=True)

for col in ["has_npdes", "has_deq_permit", "n_npdes_violations", "dmr_nodi_code", "frs_id"]:
    lookup = npdes_within.groupby("_pidx")[col].first()
    parcels[col] = parcels.index.map(lookup)
parcels["has_npdes"] = parcels["has_npdes"].fillna(0).astype(int)
parcels["has_deq_permit"] = parcels["has_deq_permit"].fillna(0).astype(int)
parcels["n_npdes_violations"] = parcels["n_npdes_violations"].fillna(0).astype(int)

# CRITICAL: a data-center PARCEL landing inside/near an NPDES-covered facility
# does NOT mean the data center itself is the covered facility — large DC
# parcels frequently co-host an unrelated permit holder (a construction
# stormwater permit, an adjacent tenant, a monitoring point). For parcels
# with a built data center, only credit has_npdes/has_deq_permit when the
# CO-LOCATED facility's own NPDES_ID is itself coded under the data-center
# NAICS code (518210) — i.e., the disclosed facility IS the data center, not
# just something else on the same lot. This is what makes the tool's headline
# finding ("0 of 203 DC buildings hold NPDES permits") an honest per-facility
# read rather than an artifact of parcel-level co-location.
has_dc_naics_facility = (
    npdes_within.assign(_is_dc_naics=npdes_within["NPDES_ID"].isin(dc_npdes_ids))
    .groupby("_pidx")["_is_dc_naics"].any()
)
dc_naics_map = parcels.index.map(has_dc_naics_facility).to_series(index=parcels.index).fillna(False)
is_dc_building = parcels["_inside_dc_building"].astype(bool)
parcels.loc[is_dc_building, "has_npdes"] = dc_naics_map[is_dc_building].astype(int)
parcels.loc[is_dc_building, "has_deq_permit"] = (dc_naics_map[is_dc_building] & (parcels.loc[is_dc_building, "has_deq_permit"] == 1)).astype(int)

t(f"  {int(parcels['has_npdes'].sum())} parcels host an NPDES-registered facility")
t(f"  headline check: DC buildings with NPDES coverage = {int(((parcels['_inside_dc_building']) & (parcels['has_npdes']==1)).sum())} of {int(parcels['_inside_dc_building'].sum())}")

t("Loading ECHO facility loadings (already PWC-filtered)...")
echo_df = pd.read_csv(p("echo_loadings_34919817.csv"), skiprows=2, low_memory=False)
if "NPDES Permit Number" in echo_df.columns:
    echo_by_npdes = echo_df.drop_duplicates("NPDES Permit Number").set_index("NPDES Permit Number")
    parcels["compliance_status"] = parcels["_dam"].map(lambda _: None)  # placeholder, filled below by NPDES_ID
    npdes_id_lookup = npdes_within.groupby("_pidx")["NPDES_ID"].first()
    parcels["_npdes_id_for_echo"] = parcels.index.map(npdes_id_lookup)
    parcels["echo_facility_name"] = parcels["_npdes_id_for_echo"].map(echo_by_npdes.get("Facility Name", pd.Series(dtype=object)))
    dmr_flow = pd.to_numeric(echo_by_npdes.get("Average Daily Flow (MGD)", pd.Series(dtype=float)), errors="coerce")
    parcels["dmr_flow_mgd"] = parcels["_npdes_id_for_echo"].map(dmr_flow)
    parcels.drop(columns=["_npdes_id_for_echo"], inplace=True)
else:
    parcels["echo_facility_name"] = None
    parcels["dmr_flow_mgd"] = None

# General-permit type + compliance status, keyed the same way
gp_lookup = general_permits.dropna(subset=[permit_name_col]).drop_duplicates(permit_name_col).set_index(permit_name_col)
npdes_id_lookup2 = npdes_within.groupby("_pidx")["NPDES_ID"].first()
parcels["general_permit_type"] = parcels.index.map(npdes_id_lookup2).map(gp_lookup.get("PERMIT_NAME", pd.Series(dtype=object)))
parcels["compliance_status"] = parcels["has_npdes"].map({1: "registered", 0: None})


# -- 9. Drought / climate (countywide constants) --------------------------

t("Loading Palmer drought indices + NOAA climate series (countywide)...")
pdsi = latest_value(p("PDSI.json"))
phdi = latest_value(p("PHDI.json"))
pmdi = latest_value(p("PMDI.json"))
palmer_z = latest_value(p("Palmer_Z.json"))
avg_temp_f = latest_value(p("Average Temp.json"))
max_temp_f = latest_value(p("Maximum Temp.json"))
min_temp_f = latest_value(p("Minimum Temp.json"))
# Cumulative annual metrics — trailing-12-month sum, not a single month's value.
cdd = trailing_12mo_sum(p("Cooling Degree Days.json"))
hdd = trailing_12mo_sum(p("Heating Degree Days.json"))
precip_in = trailing_12mo_sum(p("Precipitation.json"))
precip_manassas_in = trailing_12mo_sum(p("Manassas Precipitation.json"))
snowfall_manassas_in = trailing_12mo_sum(p("Manassas Snowfall.json"))
precip_vienna_in = trailing_12mo_sum(p("VIENNA_VA_US_Precipitation.json"))
snowfall_vienna_in = trailing_12mo_sum(p("VIENNA_VA_US_Snowfall.json"))
min_temp_vienna_f = latest_value(p("VIENNA_VA_US_Min_Temp.json"))
t(f"  PDSI={pdsi} PHDI={phdi} PMDI={pmdi} PalmerZ={palmer_z} CDD(trailing 12mo)={cdd} precip(trailing 12mo)={precip_in}")

# 30-year normal precipitation for PWC (NOAA 1991-2020 climate normal,
# Manassas Airport station) — used as the deficit baseline for droughtExposure.
PRECIP_NORMAL_IN = 42.0

for col, val in [
    ("pdsi", pdsi), ("phdi", phdi), ("pmdi", pmdi), ("palmer_z", palmer_z),
    ("avg_temp_f", avg_temp_f), ("max_temp_f", max_temp_f), ("min_temp_f", min_temp_f),
    ("cdd", cdd), ("hdd", hdd), ("precip_in", precip_in), ("precip_normal_in", PRECIP_NORMAL_IN),
    ("precip_manassas_in", precip_manassas_in), ("snowfall_manassas_in", snowfall_manassas_in),
    ("precip_vienna_in", precip_vienna_in), ("snowfall_vienna_in", snowfall_vienna_in),
    ("min_temp_vienna_f", min_temp_vienna_f),
]:
    parcels[col] = val


# -- 10. Municipal supply + power/grid context (countywide constants) ----

t("Setting PW Water aggregate + power/grid countywide constants...")
# Sourced from Prince_William_Water_FAQ_Extract.csv: "2025: data centers
# consumed ~3.8% of average daily demand and 10.1% of maximum daily demand."
parcels["pw_water_pct_avg"] = 3.8
parcels["pw_water_pct_peak"] = 10.1
parcels["utility_aggregate_available"] = 1

n_queued = 0
try:
    lbnl = pd.read_excel(p("LBNL_Ix_Queue_Data_File_thru2025.xlsx"))
    state_col = next((c for c in lbnl.columns if str(c).strip().lower() in ("state", "q_state", "state_poi")), None)
    if state_col:
        n_queued = int((lbnl[state_col].astype(str).str.upper() == "VA").sum())
except Exception as e:
    t(f"  (LBNL queue file unavailable: {e})")
parcels["n_queued_projects_nearby"] = n_queued
t(f"  n_queued_projects_nearby (VA, countywide constant) = {n_queued}")

pjm_growth = None
try:
    with open(p("pjm_load_report_full.json")) as f:
        pjm = json.load(f)
    # Best-effort: look for a top-level growth/pct field; else leave null.
    if isinstance(pjm, dict):
        for k, v in pjm.items():
            if "growth" in str(k).lower() and isinstance(v, (int, float)):
                pjm_growth = float(v)
                break
except Exception as e:
    t(f"  (PJM load report unavailable: {e})")
parcels["pjm_zone_load_growth_pct"] = pjm_growth


# -- 11. Transmission distance + LRLU/state land/use-permit context ------

t("Loading transmission line layers (merged) + LRLU + state land + regulatory context...")
tl_frames = []
for fn in ["High_Voltage_Transmission_Lines.geojson", "Virginia_Power_Transmission_Lines_HIFLD.geojson", "Power_Lines_(150kv_and_higher).geojson"]:
    fp = p(fn)
    if os.path.exists(fp):
        try:
            tl_frames.append(gpd.read_file(fp).to_crs("EPSG:5070")[["geometry"]])
        except Exception as e:
            t(f"  (skipping {fn}: {e})")
if tl_frames:
    transmission = pd.concat(tl_frames, ignore_index=True)
    transmission = gpd.GeoDataFrame(transmission, geometry="geometry", crs="EPSG:5070")
    parcels["d_transmission_ft"] = nearest_distance_ft(parcels, transmission)
else:
    parcels["d_transmission_ft"] = None

# The blind 3-layer merge above discards real attributes the HIFLD layer
# carries: VOLTAGE (with a -999999 sentinel for unknown), STATUS (IN SERVICE
# vs NOT AVAILABLE — includes decommissioned lines), and named substation
# endpoints (SUB_1/SUB_2). A raw "nearest line of any kind" distance can't
# distinguish a live 230kV+ circuit from a decommissioned 69kV spur, and a
# 100MW+ hyperscale load needs proximate HIGH-voltage in-service service —
# so compute a second, filtered distance plus the serving substation name(s)
# as a power-plausibility check on the Scope-2 estimate.
hifld_fp = p("Virginia_Power_Transmission_Lines_HIFLD.geojson")
if os.path.exists(hifld_fp):
    hifld = gpd.read_file(hifld_fp).to_crs("EPSG:5070")
    if "VOLTAGE" in hifld.columns:
        hifld["_voltage"] = pd.to_numeric(hifld["VOLTAGE"], errors="coerce").replace(-999999, None)
    else:
        hifld["_voltage"] = None
    in_service = hifld["STATUS"] == "IN SERVICE" if "STATUS" in hifld.columns else pd.Series(True, index=hifld.index)
    hv = hifld[in_service & (hifld["_voltage"] >= 230)].copy()
    t(f"  HIFLD in-service >=230kV lines: {len(hv)} of {len(hifld)}")
    if len(hv):
        parcels["d_hv_transmission_ft"] = nearest_distance_ft(parcels, hv)
        sub_cols = [c for c in ["SUB_1", "SUB_2"] if c in hv.columns]
        if sub_cols:
            parc_pts_hv = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels["centroid"].values, crs="EPSG:5070")
            hv_nearest = gpd.sjoin_nearest(parc_pts_hv, hv[sub_cols + ["geometry"]], how="left", distance_col="_d")
            hv_nearest = hv_nearest.drop_duplicates(subset="_pidx")
            for c in sub_cols:
                parcels[f"nearest_hv_{c.lower()}"] = parcels.index.map(hv_nearest.set_index("_pidx")[c])
    else:
        parcels["d_hv_transmission_ft"] = None
else:
    parcels["d_hv_transmission_ft"] = None

lrlu = gpd.read_file(p("LRLU_Developable_Areas.geojson")).to_crs("EPSG:5070")
parcels["_in_lrlu_developable"] = centroid_join(parcels, lrlu[["geometry"]], agg="any")

state_land = gpd.read_file(p("State_Land.geojson")).to_crs("EPSG:5070")
parcels["_is_state_land"] = centroid_join(parcels, state_land[["geometry"]], agg="any")

# Protected_Open_Space was baked as a map tile layer but never joined as a
# per-parcel attribute — a real gap, since conservation/easement adjacency
# is a meaningful ecological-buffer signal for facilityWaterContext.
protected = gpd.read_file(p("Protected_Open_Space.geojson")).to_crs("EPSG:5070")
parcels["_near_protected_open_space"] = centroid_join(parcels, protected[["geometry"]], agg="any")
# The layer carries a purpose flag (H2OQuality=Yes/No) distinguishing land
# protected specifically for water quality from land protected for
# wildlife habitat or recreation — adjacency to the former carries a
# materially different ecological-consequence reading than a proximity
# boolean alone.
if "H2OQuality" in protected.columns:
    h2o_protected = protected[protected["H2OQuality"] == "Yes"]
    parcels["_near_h2oquality_protected_land"] = centroid_join(parcels, h2o_protected[["geometry"]], agg="any")
else:
    parcels["_near_h2oquality_protected_land"] = False

use_permits = gpd.read_file(p("Use_Permits.geojson")).to_crs("EPSG:5070")
parc_geom5 = gpd.GeoDataFrame({"_pidx": parcels.index}, geometry=parcels.geometry, crs="EPSG:5070")
up_j = gpd.sjoin(parc_geom5, use_permits[["geometry"]], how="left", predicate="intersects")
parcels["n_use_permits_on_parcel"] = up_j.dropna(subset=["index_right"]).groupby("_pidx").size().reindex(parcels.index, fill_value=0).astype("int32")

bza = gpd.read_file(p("Zoning_Appeals_and_Variances.geojson")).to_crs("EPSG:5070")
parcels["n_bza_1mi"] = count_nearby(parcels, bza, 1.0)

pending = gpd.read_file(p("Planning_Pending_Cases.geojson")).to_crs("EPSG:5070")
parcels["n_pending_nearby"] = count_nearby(parcels, pending, 0.5)

t(f"  lrlu_developable={int(parcels['_in_lrlu_developable'].sum()):,} state_land={int(parcels['_is_state_land'].sum()):,} protected_open_space={int(parcels['_near_protected_open_space'].sum()):,}")


# -- 12. Cedar Run gage height + groundwater well depth --------------------

# The two source directory names are swapped relative to their actual
# content (confirmed by reading each file's own monitoring-location
# metadata, not by name): "cedar_run_gage/" is USGS site VA087-…, a
# Fauquier County GROUNDWATER WELL (site_type_code=GW, parameter "Water
# level, depth LSD", ft) with ~4 months of local record; "groundwater_well/"
# is USGS-01656000 "CEDAR RUN NEAR CATLETT, VA" (site_type_code=ST, an
# actual stream gage) reporting GAGE HEIGHT (parameter 00065, ft) — not
# discharge (cfs). A prior pass read the folder names at face value and fed
# the well's depth reading into a field called "cedar_run_discharge_cfs"
# while the real Cedar Run gage height went into "gw_depth_ft" — swapped in
# both source and unit. Corrected by reading the metadata-confirmed content:
t("Loading Cedar Run stream-gage height + groundwater well depth (USGS time series)...")
cedar_run_gage_height = latest_csv_time_series_value(
    p(os.path.join("groundwater_well", "primary-time-series.csv")),  # actually USGS-01656000, Cedar Run
    ["value", "Value"],
)
gw_depth_val = latest_csv_time_series_value(
    p(os.path.join("cedar_run_gage", "primary-time-series.csv")),  # actually VA087-…, the well
    ["value", "Value"],
)
# Cedar Run gage height is a watershed-scoped signal — only attach it to
# parcels whose watershed name references Cedar Run. Groundwater well depth
# is treated as a countywide constant (single well, no dense well network
# in this corpus). We deliberately do NOT compute a 7Q10 low-flow statistic
# here: this is stage (ft), not discharge (cfs) — converting requires a
# rating curve this corpus doesn't have — and the locally extracted record
# spans roughly one year, far short of the ≥10yr continuous daily record
# 7Q10 requires (the full USGS period of record for this gage runs back to
# 2007, but only ~1yr was pulled into this extraction). Reporting a 7Q10
# from this data would look rigorous while being neither — so it's left as
# a stated gap rather than a fabricated statistic.
is_cedar_run_ws = parcels["watershed_name"].astype(str).str.contains("Cedar Run", case=False, na=False)
parcels["cedar_run_gage_height_ft"] = None
parcels.loc[is_cedar_run_ws, "cedar_run_gage_height_ft"] = cedar_run_gage_height
parcels["gw_depth_ft"] = gw_depth_val
t(f"  cedar_run gage height={cedar_run_gage_height}ft (applied to {int(is_cedar_run_ws.sum())} parcels), gw_depth={gw_depth_val}ft (countywide) — 7Q10 not computed, see comment above")


# -- 13. Zoning + address fields (kept from Vira) --------------------------

t("Loading zoning districts + computing zoning per parcel...")
zoning = gpd.read_file(p("Zoning_Districts.geojson")).to_crs("EPSG:5070")
zoning_col = "ZoningDistrict" if "ZoningDistrict" in zoning.columns else zoning.columns[0]
parcels["zoning"] = centroid_join(parcels, zoning[[zoning_col, "geometry"]], agg="first", val_col=zoning_col)
# PROFFERS=Yes flags a rezoning with attached proffered conditions —
# frequently including water-service or stormwater commitments. Not a
# water-volume input on its own (no volume is encoded in this boolean),
# but a siting/context lead: a facility on proffered land has more public
# record attached to it than a by-right build.
if "PROFFERS" in zoning.columns:
    parcels["_has_proffers"] = centroid_join(parcels, zoning[["PROFFERS", "geometry"]], agg="first", val_col="PROFFERS") == "Yes"
else:
    parcels["_has_proffers"] = False

parcels["lrlu"] = None
if "LRLU" in lrlu.columns:
    parcels["lrlu"] = centroid_join(parcels, lrlu[["LRLU", "geometry"]], agg="first", val_col="LRLU")


# -- 14. Save outputs -------------------------------------------------------

t("Selecting output columns + reprojecting to WGS84 for serialization...")
out_cols = [
    "GPIN", "Acreage", "acres_calc", "StreetNumber", "StreetName", "StreetType",
    "City", "ZipCode", "SubdivisionName", "zoning", "lrlu",
    "_inside_dc_campus", "_inside_dc_building", "dc_campus_name", "dc_building_name", "n_dc_buildings",
    "watershed_id", "watershed_name", "watershed_acres", "watershed_major_basin", "watershed_mgmt_plan_number", "n_dc_in_watershed", "n_dc_in_major_basin",
    "d_stream_ft", "d_hydro_ft", "d_surftemp_ft", "_rpa", "_wetland", "_in_tidal_flow_path",
    "stream_order", "stream_name", "tidal_class", "tidal_zone",
    "surftemp_trend", "surftemp_tau", "surftemp_theilsen_slope", "surftemp_pvalcovs", "surftemp_stream",
    "_dam", "dam_haz_class", "soil_cat", "hsg", "erosion_susceptibility", "soil_permeability", "land_cover",
    "sw_segments", "sw_structures", "sw_facilities",
    "n_wqp_stations_1mi", "n_deq_monitoring_1mi", "n_deq_gage_1mi", "nearest_benthic_n", "n_inat_1mi", "n_inat_research_1mi",
    "has_npdes", "has_deq_permit", "n_npdes_violations", "dmr_nodi_code", "dmr_flow_mgd",
    "echo_facility_name", "general_permit_type", "compliance_status", "frs_id",
    "pdsi", "phdi", "pmdi", "palmer_z", "avg_temp_f", "max_temp_f", "min_temp_f", "cdd", "hdd",
    "precip_in", "precip_normal_in", "precip_manassas_in", "snowfall_manassas_in",
    "precip_vienna_in", "snowfall_vienna_in", "min_temp_vienna_f",
    "pw_water_pct_avg", "pw_water_pct_peak", "utility_aggregate_available",
    "n_queued_projects_nearby", "pjm_zone_load_growth_pct",
    "d_transmission_ft", "d_hv_transmission_ft", "nearest_hv_sub_1", "nearest_hv_sub_2",
    "_in_lrlu_developable", "_is_state_land", "_near_protected_open_space", "_near_h2oquality_protected_land",
    "n_use_permits_on_parcel", "n_bza_1mi", "n_pending_nearby", "_has_proffers",
    "cedar_run_gage_height_ft", "gw_depth_ft",
    "geometry",
]
out_cols = [c for c in out_cols if c in parcels.columns]
out = parcels[out_cols].copy()
out = out.set_geometry("geometry").to_crs("EPSG:4326")
_cent = out.geometry.centroid
out["cx"] = _cent.x.round(5)
out["cy"] = _cent.y.round(5)
out["acres_calc"] = out["acres_calc"].round(2)
for c in ["d_stream_ft", "d_hydro_ft", "d_surftemp_ft", "d_transmission_ft", "d_hv_transmission_ft"]:
    if c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce").round(0)
for c in ["surftemp_tau", "surftemp_theilsen_slope", "surftemp_pvalcovs", "erosion_susceptibility", "soil_permeability"]:
    if c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce").round(3)

out = out.rename(columns={
    "acres_calc": "acres",
    "_inside_dc_campus": "in_dc_campus",
    "_inside_dc_building": "in_dc_building",
    "_rpa": "rpa",
    "_wetland": "wetland",
    "_in_tidal_flow_path": "in_tidal_flow_path",
    "_dam": "dam",
    "_in_lrlu_developable": "in_lrlu_developable",
    "_is_state_land": "is_state_land",
    "_near_protected_open_space": "near_protected_open_space",
    "_near_h2oquality_protected_land": "near_h2oquality_protected_land",
    "_has_proffers": "has_proffers",
})

for c in ["in_dc_campus", "in_dc_building", "rpa", "wetland", "in_tidal_flow_path", "dam",
          "in_lrlu_developable", "is_state_land", "near_protected_open_space", "near_h2oquality_protected_land",
          "has_proffers", "has_npdes", "has_deq_permit"]:
    if c in out.columns:
        out[c] = out[c].fillna(False).astype(int)
for c in ["n_dc_buildings", "n_dc_in_watershed", "n_dc_in_major_basin", "sw_segments", "sw_structures", "sw_facilities",
          "n_wqp_stations_1mi", "n_deq_monitoring_1mi", "n_deq_gage_1mi", "n_inat_1mi", "n_inat_research_1mi", "n_npdes_violations",
          "n_queued_projects_nearby", "n_use_permits_on_parcel", "n_bza_1mi", "n_pending_nearby", "stream_order"]:
    if c in out.columns:
        out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype("int32")

# Sort-bootstrap hints — a cheap Data Depth proxy (fraction of the key
# scoring-relevant fields populated) and a neutral 50 for readiness (the
# real Water Legibility Score is computed client-side by synthesizeSubScores.ts).
# Dropping the two spring fields took this from 19 fields to 17 and raises every
# parcel's conviction slightly. Both were constants, not signal: spring_ph was
# null for 100% of parcels (a fixed drag on the numerator) and d_spring_ft was
# non-null for 100% (a fixed lift), so each cancelled to noise in the ratio.
DEPTH_FIELDS = [
    "watershed_id", "d_stream_ft", "d_hydro_ft", "soil_cat",
    "sw_segments", "sw_structures", "dam_haz_class", "has_npdes", "has_deq_permit",
    "n_wqp_stations_1mi", "n_inat_1mi", "phdi", "d_surftemp_ft",
    "hsg", "erosion_susceptibility", "surftemp_trend", "watershed_major_basin",
]
present = out[[c for c in DEPTH_FIELDS if c in out.columns]].notna().sum(axis=1)
out["conviction"] = ((present / len(DEPTH_FIELDS)) * 100).round(0).astype("int32")
out["readiness"] = 50

t("Writing parcels_scored.geojson (for tippecanoe)...")
out.to_file(f"{OUT_ROOT}/parcels_scored.geojson", driver="GeoJSON")
size_mb = os.path.getsize(f"{OUT_ROOT}/parcels_scored.geojson") / 1024 / 1024
t(f"  wrote {size_mb:.0f} MB")

t("Writing parcels_scored.json (lightweight, for the Terminal table)...")
def _clean(rec):
    return {k: (None if (isinstance(v, float) and math.isnan(v)) else v) for k, v in rec.items()}
out_records = [_clean(r) for r in out.drop(columns=["geometry"]).to_dict(orient="records")]
with open(f"{OUT_ROOT}/parcels_scored.json", "w") as f:
    json.dump(out_records, f, separators=(",", ":"), allow_nan=False)
size_mb = os.path.getsize(f"{OUT_ROOT}/parcels_scored.json") / 1024 / 1024
t(f"  wrote {size_mb:.0f} MB, {len(out_records):,} records")

t("DONE.")
