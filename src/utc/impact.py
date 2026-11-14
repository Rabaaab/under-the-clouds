"""Impact layer: how much road and how many villages are affected by the detected change."""

from __future__ import annotations

import geopandas as gpd
import pandas as pd


def _empty_summary() -> dict:
    return {
        "flooded_area_km2": 0.0,
        "road_km_affected": 0.0,
        "road_km_total": 0.0,
        "road_segments_affected": 0,
        "villages_near_flood": 0,
        "village_names": [],
        "village_buffer_m": 0.0,
    }


def impact_summary(
    flood: gpd.GeoDataFrame,
    roads: gpd.GeoDataFrame | None = None,
    villages: gpd.GeoDataFrame | None = None,
    village_buffer_m: float = 500.0,
):
    """Intersect flood polygons with roads and villages.

    Returns (summary dict, affected roads GeoDataFrame in EPSG:4326, nearby villages GeoDataFrame in EPSG:4326).
    Lengths and distances are computed in a metric UTM CRS chosen from the flood polygons.
    """
    summary = _empty_summary()
    summary["village_buffer_m"] = float(village_buffer_m)
    empty = gpd.GeoDataFrame({"geometry": []}, geometry="geometry", crs="EPSG:4326")
    if flood is None or flood.empty:
        return summary, empty, empty

    metric = flood.estimate_utm_crs()
    union = flood.to_crs(metric).geometry.union_all()
    summary["flooded_area_km2"] = float(union.area / 1e6)

    affected_roads = empty
    if roads is not None and not roads.empty:
        r = roads.to_crs(metric)
        summary["road_km_total"] = float(r.geometry.length.sum() / 1000.0)
        summary["road_km_affected"] = float(r.geometry.intersection(union).length.sum() / 1000.0)
        hit = r[r.geometry.intersects(union)]
        summary["road_segments_affected"] = int(len(hit))
        affected_roads = hit.to_crs("EPSG:4326")

    near_villages = empty
    if villages is not None and not villages.empty:
        v = villages.to_crs(metric)
        near = v[v.geometry.distance(union) <= village_buffer_m]
        summary["villages_near_flood"] = int(len(near))
        if "name" in near.columns:
            summary["village_names"] = [str(n) for n in near["name"].tolist() if pd.notna(n)]
        near_villages = near.to_crs("EPSG:4326")

    return summary, affected_roads, near_villages


def load_osm(bbox_wgs84: tuple[float, float, float, float]):
    """Download roads and villages for (west, south, east, north) from OpenStreetMap.

    UNTESTED (needs internet and `pip install osmnx`). Written for osmnx 2.x, where `features_from_bbox`
    takes (west, south, east, north). Older versions use a different argument order.
    """
    try:
        import osmnx as ox
    except ImportError as exc:  # pragma: no cover
        raise ImportError("Install osmnx to download OpenStreetMap data: pip install osmnx") from exc

    ox.settings.cache_folder = "data/osm_cache"  # keep osmnx's cache inside the git-ignored data/ folder
    roads = ox.features_from_bbox(bbox=bbox_wgs84, tags={"highway": True}).reset_index(drop=True)
    roads = roads[roads.geometry.geom_type.isin(["LineString", "MultiLineString"])]
    places = ox.features_from_bbox(
        bbox=bbox_wgs84, tags={"place": ["village", "hamlet", "town", "suburb"]}
    ).reset_index(drop=True)
    places = places.copy()
    places["geometry"] = places.geometry.centroid
    return roads, places
