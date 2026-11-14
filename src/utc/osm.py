"""Fetch roads and villages from OpenStreetMap and save them as GeoJSON for the pipeline.

    python scripts/fetch_osm.py --bbox WEST SOUTH EAST NORTH --out data/osm

Needs internet and `pip install osmnx` (written for osmnx 2.x). Keep the box small (a few tens of km):
large boxes make the Overpass server slow or refuse the request.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import geopandas as gpd

from .impact import load_osm

ROAD_COLUMNS = ["name", "highway"]
VILLAGE_COLUMNS = ["name", "place"]


def _keep(gdf: gpd.GeoDataFrame, columns: list[str]) -> gpd.GeoDataFrame:
    """Keep a few columns as plain strings so the GeoJSON writer never chokes on OSM's messy tags."""
    out = gdf[[c for c in columns if c in gdf.columns] + ["geometry"]].copy()
    for c in out.columns:
        if c != "geometry":
            out[c] = out[c].astype("string").fillna("")
    return gpd.GeoDataFrame(out, geometry="geometry", crs="EPSG:4326")


def fetch_osm(bbox_wgs84: tuple[float, float, float, float], out_dir) -> dict:
    """Download roads and villages for (west, south, east, north) and write roads.geojson / villages.geojson."""
    roads, villages = load_osm(bbox_wgs84)
    roads, villages = _keep(roads, ROAD_COLUMNS), _keep(villages, VILLAGE_COLUMNS)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    roads.to_file(out / "roads.geojson", driver="GeoJSON")
    villages.to_file(out / "villages.geojson", driver="GeoJSON")
    return {"roads": len(roads), "villages": len(villages), "out_dir": str(out)}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--bbox", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH"), required=True)
    p.add_argument("--out", default="data/osm")
    args = p.parse_args(argv)
    print(fetch_osm(tuple(args.bbox), args.out))
    print("Open the files and check them: OpenStreetMap coverage varies, and 0 villages means the area is untagged.")


if __name__ == "__main__":
    main()
