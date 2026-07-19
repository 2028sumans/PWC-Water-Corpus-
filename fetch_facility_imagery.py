"""
Fetch overhead imagery for a facility from Esri World Imagery.

WHAT THIS IS FOR -- AND WHAT IT IS NOT FOR
------------------------------------------
This was written while chasing cooling type, the third-largest swing factor in
the estimator. It works: imagery comes back at roughly 0.15 m/px over Prince
William, and rooftop mechanical equipment is plainly visible.

It is NOT wired into the estimator, deliberately. See METHODOLOGY.md 7.3 for
the full reasoning; the short version is that an evaporative cooling tower and
an air-cooled chiller both present from directly overhead as a rectangular
housing with circular fan cowlings. The features that separate them -- water
basin, drift eliminators, sump piping, visible plume -- are either inside the
housing or not resolvable at this scale. There is also no labelled Prince
William facility to calibrate against: the one permit that documents cooling
towers (74216, Nova Mango Farms, 31 units) has no parcel in the county GIS and
no building in this dataset.

Producing cooling-type labels from it would mean feeding a visual guess into a
tool where every other input cites a document. The script is kept because the
imagery is genuinely useful for orientation, for confirming a building exists
where the point geometry says it does, and for change detection between
imagery vintages -- none of which require classifying equipment.

USAGE
  python3 fetch_facility_imagery.py <lat> <lon> [half_width_m] [out.png]
"""
import math
import subprocess
import sys

WORLD_IMAGERY = (
    "https://services.arcgisonline.com/ArcGIS/rest/services/"
    "World_Imagery/MapServer/export"
)


def to_web_mercator(lat, lon):
    x = lon * 20037508.34 / 180
    y = math.log(math.tan((90 + lat) * math.pi / 360)) / (math.pi / 180)
    return x, y * 20037508.34 / 180


def fetch(lat, lon, half_width_m=350, out="facility.png", px=1200):
    """Fetch a square overhead image centred on (lat, lon).

    half_width_m ~350 frames a whole building and its surroundings; ~90 resolves
    individual rooftop units.
    """
    x, y = to_web_mercator(lat, lon)
    bbox = f"{x - half_width_m},{y - half_width_m},{x + half_width_m},{y + half_width_m}"
    cmd = [
        "curl", "-sG", "--max-time", "90", "-A", "Mozilla/5.0", WORLD_IMAGERY,
        "--data-urlencode", f"bbox={bbox}",
        "--data-urlencode", "bboxSR=3857",
        "--data-urlencode", "imageSR=3857",
        "--data-urlencode", f"size={px},{px}",
        "--data-urlencode", "format=png",
        "--data-urlencode", "f=image",
        "-o", out,
    ]
    subprocess.run(cmd, check=True)
    return out


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(1)
    lat, lon = float(sys.argv[1]), float(sys.argv[2])
    hw = float(sys.argv[3]) if len(sys.argv) > 3 else 350
    out = sys.argv[4] if len(sys.argv) > 4 else "facility.png"
    print("wrote", fetch(lat, lon, hw, out))
