"use client";

import { useEffect, useMemo, useState, useRef } from "react";
import {
  Map as MapView,
  NavigationControl,
  Popup,
  Source,
  Layer,
  type MapRef,
  type MapMouseEvent,
} from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";
import "maplibre-gl/dist/maplibre-gl.css";
import { useViraStore } from "@/store/useViraStore";
import { findScoredParcel, useScoredParcels } from "@/lib/useScoredParcels";
import { parcelReadinessAt } from "@/lib/parcelReadiness";
import { MAP_LAYERS, type LayerGroup } from "@/lib/mapLayerRegistry";
import { Layers } from "lucide-react";

// Register the pmtiles:// protocol once, globally, the moment this module loads.
if (typeof window !== "undefined") {
  const protocol = new Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);
}

// PWC roughly centered on Manassas
const INITIAL_VIEW = {
  longitude: -77.5,
  latitude: 38.72,
  zoom: 9.4,
};

const OPENFREEMAP_STYLE = "https://tiles.openfreemap.org/styles/positron";
const PARCELS_PMTILES = "pmtiles:///api/tiles/parcels.pmtiles";

function markerColorForLegibility(score: number) {
  if (score >= 80) return "#7dd3c0";
  if (score >= 60) return "#e0b96a";
  if (score >= 40) return "#c9a9a0";
  return "#8b5e5e";
}

// Derive the toggle-panel structure from the central registry.
const LAYER_GROUPS: Array<{
  group: LayerGroup;
  layers: Array<{ id: string; label: string }>;
}> = (() => {
  const groupOrder: LayerGroup[] = ["Hydrology", "Hazard & Stormwater", "Disclosure", "Monitoring", "Power & Land"];
  return groupOrder.map((g) => ({
    group: g,
    layers: MAP_LAYERS.filter((l) => l.group === g).map((l) => ({ id: l.id, label: l.label })),
  }));
})();

const PARCEL_LAYER_ID = "parcels";

const PRESETS = [
  { id: "hardBlockers" as const, label: "Hard blockers" },
  { id: "powerReady" as const, label: "Power-ready" },
  { id: "politicallyWarm" as const, label: "Politically warm" },
];

export function SpatialMap() {
  const selectedParcelId = useViraStore((s) => s.selectedParcelId);
  const setSelectedParcel = useViraStore((s) => s.setSelectedParcel);
  const activeLayers = useViraStore((s) => s.activeLayers);
  const toggleLayer = useViraStore((s) => s.toggleLayer);
  const setLayers = useViraStore((s) => s.setLayers);
  const preset = useViraStore((s) => s.preset);
  const setPreset = useViraStore((s) => s.setPreset);
  const subScoreWeights = useViraStore((s) => s.subScoreWeights);

  const [layerPanelOpen, setLayerPanelOpen] = useState(false);
  const mapRef = useRef<MapRef | null>(null);
  const [mapReady, setMapReady] = useState(false);

  // Hover-preview popup state.
  const [hoveredParcel, setHoveredParcel] = useState<
    | { gpin: string; lng: number; lat: number; acres: number; zoning: string | null; legibility: number }
    | null
  >(null);
  const hoverTimerRef = useRef<number | null>(null);
  const lastHoverGpinRef = useRef<string | null>(null);

  const selectedParcel = useMemo(
    () => (selectedParcelId ? findScoredParcel(selectedParcelId) : undefined),
    [selectedParcelId]
  );
  const selectedLegibility = useMemo(() => {
    if (!selectedParcelId) return null;
    return parcelReadinessAt({ GPIN: selectedParcelId }, subScoreWeights);
  }, [selectedParcelId, subScoreWeights]);

  const handleMapClick = (e: MapMouseEvent) => {
    const features = e.features ?? [];
    const f = features.find(
      (ft) => ft.layer?.id === "pwc-parcels-fill" || ft.layer?.id === "pwc-parcels-outline"
    );
    if (f && f.properties?.GPIN) {
      setSelectedParcel(String(f.properties.GPIN));
    }
  };

  const handleMouseMove = (e: MapMouseEvent) => {
    const map = mapRef.current?.getMap();
    if (!map) return;
    const features = e.features ?? [];
    const f = features.find(
      (ft) => ft.layer?.id === "pwc-parcels-fill" || ft.layer?.id === "pwc-parcels-outline"
    );
    map.getCanvas().style.cursor = f ? "pointer" : "";

    const gpin = f?.properties?.GPIN ? String(f.properties.GPIN) : null;
    if (gpin !== lastHoverGpinRef.current) {
      lastHoverGpinRef.current = gpin;
      if (hoverTimerRef.current !== null) {
        window.clearTimeout(hoverTimerRef.current);
        hoverTimerRef.current = null;
      }
      if (gpin) {
        const lng = e.lngLat.lng;
        const lat = e.lngLat.lat;
        hoverTimerRef.current = window.setTimeout(() => {
          const scored = findScoredParcel(gpin);
          if (!scored) return;
          const projected = parcelReadinessAt(scored, subScoreWeights);
          setHoveredParcel({
            gpin,
            lng,
            lat,
            acres: scored.acres,
            zoning: scored.zoning,
            legibility: projected ?? scored.readiness,
          });
        }, 200);
      } else {
        setHoveredParcel(null);
      }
    }
  };

  const handleMouseLeaveMap = () => {
    if (hoverTimerRef.current !== null) {
      window.clearTimeout(hoverTimerRef.current);
      hoverTimerRef.current = null;
    }
    lastHoverGpinRef.current = null;
    setHoveredParcel(null);
  };

  // Generate the diagonal-stripe sprite once on map load — used by the
  // "site taken" DC projects overlay pattern.
  useEffect(() => {
    const map = mapRef.current?.getMap();
    if (!map || !mapReady) return;
    if (map.hasImage("vira-taken-hatch")) return;
    const SIZE = 12;
    const canvas = document.createElement("canvas");
    canvas.width = canvas.height = SIZE;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;
    ctx.strokeStyle = "rgba(255, 255, 255, 0.55)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(-2, SIZE + 2); ctx.lineTo(SIZE + 2, -2);
    ctx.moveTo(-2, SIZE / 2); ctx.lineTo(SIZE / 2, -2);
    ctx.moveTo(SIZE / 2, SIZE + 2); ctx.lineTo(SIZE + 2, SIZE / 2);
    ctx.stroke();
    const imgData = ctx.getImageData(0, 0, SIZE, SIZE);
    map.addImage("vira-taken-hatch", {
      width: SIZE,
      height: SIZE,
      data: new Uint8Array(imgData.data),
    });
  }, [mapReady]);

  // MAP COLOR SOURCE — canonical parcelReadinessAt() via feature-state, so
  // the choropleth shows real per-parcel Water Legibility variation instead
  // of the flatter Python-baked hint.
  const { parcels: allScoredParcels } = useScoredParcels();
  useEffect(() => {
    const map = mapRef.current?.getMap();
    if (!map || !mapReady || !allScoredParcels) return;
    const timer = setTimeout(() => {
      const t0 = performance.now();
      let updates = 0;
      for (const p of allScoredParcels) {
        if (!p.GPIN || p.GPIN === "9999-99-9999") continue;
        const projected = parcelReadinessAt(p, subScoreWeights);
        if (projected === null) continue;
        map.setFeatureState(
          { source: "pwc-parcels", sourceLayer: "pwc-parcels", id: p.GPIN },
          { proj: projected },
        );
        updates++;
      }
      const elapsed = Math.round(performance.now() - t0);
      // eslint-disable-next-line no-console
      console.log(`[Water Atlas] feature-state synced for ${updates.toLocaleString()} parcels in ${elapsed}ms`);
    }, 150);
    return () => clearTimeout(timer);
  }, [allScoredParcels, subScoreWeights, mapReady]);

  // Fly the camera to the selected parcel's centroid.
  useEffect(() => {
    if (!mapReady || !selectedParcelId) return;
    const map = mapRef.current?.getMap();
    if (!map) return;
    const scored = findScoredParcel(selectedParcelId);
    if (!scored || scored.cx == null || scored.cy == null) return;
    map.flyTo({
      center: [scored.cx, scored.cy],
      zoom: 15,
      duration: 900,
      essential: true,
    });
  }, [selectedParcelId, mapReady]);

  const applyPreset = (p: typeof preset) => {
    setPreset(p);
    const baseOff = Object.fromEntries(Object.keys(activeLayers).map((k) => [k, false]));
    if (p === "hardBlockers") {
      setLayers({
        ...baseOff,
        [PARCEL_LAYER_ID]: true,
        rpa: true,
        damInundation: true,
        protectedOpenSpace: true,
        stateLand: true,
      });
    } else if (p === "powerReady") {
      setLayers({
        ...baseOff,
        [PARCEL_LAYER_ID]: true,
        transmissionLines: true,
        dcBuildings: true,
        npdesPermits: true,
      });
    } else if (p === "politicallyWarm") {
      setLayers({
        ...baseOff,
        [PARCEL_LAYER_ID]: true,
        dcProjects: true,
        pendingCases: true,
        watersheds: true,
      });
    }
  };

  const parcelsActive = activeLayers.parcels ?? true;
  const isSelectedFromTiles = !!selectedParcelId;

  return (
    <div className="relative h-full w-full">
      <MapView
        ref={mapRef}
        initialViewState={INITIAL_VIEW}
        mapStyle={OPENFREEMAP_STYLE}
        attributionControl={{ compact: true }}
        interactiveLayerIds={["pwc-parcels-fill", "pwc-parcels-outline"]}
        onClick={handleMapClick}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeaveMap}
        onLoad={() => setMapReady(true)}
      >
        <NavigationControl position="top-left" />

        {/* All-PWC parcel polygons from the local PMTiles file (no token). */}
        <Source id="pwc-parcels" type="vector" url={PARCELS_PMTILES} />
        {parcelsActive && (
          <>
            <Layer
              id="pwc-parcels-fill"
              source="pwc-parcels"
              source-layer="pwc-parcels"
              type="fill"
              paint={{
                // Color each parcel by its Water Legibility Score
                // (blue/teal = legible, muted red = dark/unresolved).
                "fill-color": [
                  "interpolate",
                  ["linear"],
                  ["coalesce", ["feature-state", "proj"], ["to-number", ["get", "readiness"]], 0],
                  0, "#8b5e5e",
                  30, "#c9a9a0",
                  50, "#e0b96a",
                  70, "#4fa3d1",
                  100, "#7dd3c0",
                ],
                "fill-opacity": selectedParcelId
                  ? [
                      "interpolate", ["linear"], ["zoom"],
                      9,  ["case", ["==", ["get", "GPIN"], selectedParcelId], 0.78, 0.32],
                      12, ["case", ["==", ["get", "GPIN"], selectedParcelId], 0.88, 0.38],
                      14, ["case", ["==", ["get", "GPIN"], selectedParcelId], 0.92, 0.42],
                      16, ["case", ["==", ["get", "GPIN"], selectedParcelId], 0.94, 0.45],
                    ]
                  : [
                      "interpolate", ["linear"], ["zoom"],
                      9, 0.55, 12, 0.72, 14, 0.78, 16, 0.82,
                    ],
              }}
            />
            <Layer
              id="pwc-parcels-outline"
              source="pwc-parcels"
              source-layer="pwc-parcels"
              type="line"
              paint={{
                "line-color": "#0a1929",
                "line-width": [
                  "interpolate", ["linear"], ["zoom"],
                  11, 0.1, 14, 0.4, 16, 0.8,
                ],
                "line-opacity": 0.4,
              }}
            />
          </>
        )}

        {isSelectedFromTiles && (
          <Layer
            id="pwc-parcels-selected"
            source="pwc-parcels"
            source-layer="pwc-parcels"
            type="line"
            paint={{
              "line-color": "#4fa3d1",
              "line-width": 3,
              "line-opacity": 1,
            }}
            filter={["==", ["get", "GPIN"], selectedParcelId]}
          />
        )}

        {/* Overlay layers from the central registry. */}
        {MAP_LAYERS.map((spec) => {
          if (!activeLayers[spec.id]) return null;
          const sourceId = `water-atlas-${spec.id}`;
          const url = `pmtiles:///api/tiles/${spec.pmtilesFile}`;
          if (spec.kind === "fill") {
            return (
              <Source key={sourceId} id={sourceId} type="vector" url={url}>
                <Layer
                  id={`${sourceId}-fill`}
                  source={sourceId}
                  source-layer={spec.sourceLayer}
                  type="fill"
                  paint={{
                    "fill-color": spec.color,
                    "fill-opacity": spec.fillOpacity ?? 0.25,
                  }}
                />
                {spec.patternImage && (
                  <Layer
                    id={`${sourceId}-pattern`}
                    source={sourceId}
                    source-layer={spec.sourceLayer}
                    type="fill"
                    paint={{ "fill-pattern": spec.patternImage, "fill-opacity": 0.7 }}
                  />
                )}
                {spec.outline && (
                  <Layer
                    id={`${sourceId}-outline`}
                    source={sourceId}
                    source-layer={spec.sourceLayer}
                    type="line"
                    paint={{
                      "line-color": spec.color,
                      "line-width": spec.lineWidth ?? 1,
                      "line-opacity": 0.85,
                    }}
                  />
                )}
              </Source>
            );
          }
          if (spec.kind === "line") {
            return (
              <Source key={sourceId} id={sourceId} type="vector" url={url}>
                <Layer
                  id={`${sourceId}-line`}
                  source={sourceId}
                  source-layer={spec.sourceLayer}
                  type="line"
                  paint={{
                    "line-color": spec.color,
                    "line-width": spec.lineWidth ?? 1.2,
                    "line-opacity": 0.85,
                  }}
                />
              </Source>
            );
          }
          const r14 = spec.circleRadiusBase ?? 7;
          const strokeColor = spec.circleStrokeColor ?? "#0a1929";
          const strokeWidth = spec.circleStrokeWidth ?? 1.2;
          return (
            <Source key={sourceId} id={sourceId} type="vector" url={url}>
              <Layer
                id={`${sourceId}-circle`}
                source={sourceId}
                source-layer={spec.sourceLayer}
                type="circle"
                paint={{
                  "circle-color": spec.color,
                  "circle-radius": [
                    "interpolate", ["linear"], ["zoom"],
                    9, (r14 * 3) / 7,
                    12, (r14 * 5) / 7,
                    14, r14,
                    16, (r14 * 9) / 7,
                  ],
                  "circle-stroke-color": strokeColor,
                  "circle-stroke-width": strokeWidth,
                  "circle-opacity": 0.95,
                }}
              />
            </Source>
          );
        })}

        {/* Popup for the selected parcel (from table or map click). */}
        {selectedParcel && selectedLegibility != null && (
          <Popup
            longitude={selectedParcel.cx ?? INITIAL_VIEW.longitude}
            latitude={selectedParcel.cy ?? INITIAL_VIEW.latitude}
            anchor="top"
            offset={16}
            closeButton={false}
            closeOnClick={false}
            className="vira-popup"
          >
            <div className="text-xs text-neutral-100 min-w-[200px]">
              <div className="text-[10px] text-amber-400">{selectedParcel.GPIN}</div>
              <div className="font-medium mt-0.5">
                {selectedParcel.SubdivisionName ?? selectedParcel.watershed_name ?? "Parcel"}
              </div>
              <div className="text-[10px] text-neutral-400 mt-1">
                {selectedParcel.acres.toFixed(1)} ac · {selectedParcel.zoning ?? "—"}
              </div>
              <div className="mt-1.5 flex items-center gap-1.5">
                <span className="text-[10px] text-neutral-400">Water Legibility:</span>
                <span
                  className="rounded px-1.5 py-0.5 text-[10px] font-medium"
                  style={{ backgroundColor: markerColorForLegibility(selectedLegibility), color: "#0a1929" }}
                >
                  {selectedLegibility}
                </span>
              </div>
            </div>
          </Popup>
        )}

        {/* Hover-preview popup. */}
        {hoveredParcel && hoveredParcel.gpin !== selectedParcelId && (
          <Popup
            longitude={hoveredParcel.lng}
            latitude={hoveredParcel.lat}
            anchor="bottom"
            offset={12}
            closeButton={false}
            closeOnClick={false}
            className="vira-popup vira-popup-hover"
          >
            <div className="text-xs text-neutral-100 min-w-[180px] pointer-events-none">
              <div className="text-[10px] text-amber-400">{hoveredParcel.gpin}</div>
              <div className="text-[10px] text-neutral-400 mt-1">
                {hoveredParcel.acres < 1 ? `${hoveredParcel.acres.toFixed(2)} ac` : `${hoveredParcel.acres.toFixed(1)} ac`}
                {" · "}
                {hoveredParcel.zoning ?? "—"}
              </div>
              <div className="mt-1.5 flex items-center gap-1.5">
                <span className="text-[10px] text-neutral-400">legibility:</span>
                <span
                  className="rounded px-1.5 py-0.5 text-[10px] font-medium"
                  style={{ backgroundColor: markerColorForLegibility(hoveredParcel.legibility), color: "#0a1929" }}
                >
                  {hoveredParcel.legibility}
                </span>
              </div>
            </div>
          </Popup>
        )}
      </MapView>

      {/* Water Legibility legend (bottom-right) */}
      <div className="absolute bottom-4 right-4 z-10 rounded border border-neutral-800 bg-neutral-950/85 backdrop-blur px-3 py-2 text-[10px] text-neutral-300">
        <div className="uppercase tracking-wider text-neutral-500 mb-1.5">
          Water Legibility
        </div>
        <div className="h-2 w-32 rounded bg-gradient-to-r from-[#8b5e5e] via-[#e0b96a] to-[#7dd3c0]" />
        <div className="mt-0.5 flex justify-between text-[9px] text-neutral-500 w-32">
          <span>0</span>
          <span>50</span>
          <span>100</span>
        </div>
      </div>

      {/* Floating layer control */}
      <div className="absolute top-4 right-4 z-10">
        <button
          onClick={() => setLayerPanelOpen(!layerPanelOpen)}
          className="flex items-center gap-1.5 rounded border border-neutral-700 bg-neutral-900/95 backdrop-blur px-3 py-2 text-xs text-neutral-200 hover:border-amber-500"
        >
          <Layers className="h-3.5 w-3.5" />
          Layers
        </button>

        {layerPanelOpen && (
          <div className="absolute top-12 right-0 w-72 rounded-lg border border-neutral-800 bg-neutral-950/97 backdrop-blur shadow-2xl p-3 max-h-[70vh] overflow-y-auto">
            <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-2">
              Smart Presets
            </div>
            <div className="flex flex-wrap gap-1 mb-4">
              {PRESETS.map((p) => (
                <button
                  key={p.id}
                  onClick={() => applyPreset(p.id)}
                  className={`rounded px-2 py-1 text-[11px] transition ${
                    preset === p.id
                      ? "bg-amber-500 text-neutral-950"
                      : "border border-neutral-700 text-neutral-300 hover:border-amber-500"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>

            {LAYER_GROUPS.map((g) => (
              <div key={g.group} className="mb-3">
                <div className="text-[10px] uppercase tracking-wider text-neutral-500 mb-1">
                  {g.group}
                </div>
                {g.layers.map((l) => (
                  <label
                    key={l.id}
                    className="flex items-center gap-2 py-0.5 text-xs text-neutral-300 hover:text-neutral-100 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={activeLayers[l.id] ?? false}
                      onChange={() => toggleLayer(l.id)}
                      className="accent-amber-500"
                    />
                    {l.label}
                  </label>
                ))}
              </div>
            ))}
            <div className="mt-2 pt-2 border-t border-neutral-800 text-[10px] text-neutral-500 italic leading-relaxed">
              Parcels color-code by Water Legibility. Toggle any overlay above
              to paint it on top — vector tiles load on demand from the
              local PMTiles cache (no external service, no API key).
            </div>
          </div>
        )}
      </div>

      {/* PWC label */}
      <div className="absolute bottom-4 left-4 z-10 rounded border border-neutral-800 bg-neutral-950/85 backdrop-blur px-3 py-2 text-[11px] text-neutral-300">
        <div className="text-[10px] uppercase tracking-wider text-neutral-500">
          Region
        </div>
        <div>Prince William County, VA</div>
        <div className="text-[10px] text-neutral-500 mt-1">
          Basemap: OpenFreeMap · Tiles: local PMTiles · No token required
        </div>
      </div>
    </div>
  );
}
