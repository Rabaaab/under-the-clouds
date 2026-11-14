"""Write the files the web map reads: PNG overlays, GeoJSON layers and meta.json."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image

from .io import pixel_to_xy
from .preprocess import normalize_db


def _geojson_text(gdf) -> str:
    if gdf is None or len(gdf) == 0:
        return json.dumps({"type": "FeatureCollection", "features": []})
    return gdf.to_crs("EPSG:4326").to_json()


def _bounds_wgs84(transform, shape) -> list[list[float]]:
    h, w = shape
    west, north = pixel_to_xy(transform, 0, 0)
    east, south = pixel_to_xy(transform, w, h)
    return [[float(south), float(west)], [float(north), float(east)]]


def export_web(out_dir, before_db, after_db, result: dict, transform, crs, meta_extra: dict | None = None) -> Path:
    """Export a pipeline result for app/index.html. The scene must be in EPSG:4326."""
    if str(crs).upper() not in ("EPSG:4326", "OGC:CRS84"):
        raise ValueError(f"export_web expects EPSG:4326, got {crs}. Reproject the scene first.")
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for name, db in (("before", before_db), ("after", after_db)):
        gray = (normalize_db(db[0]) * 255).astype(np.uint8)
        Image.fromarray(gray, mode="L").save(out / f"{name}.png")

    mask = result["change_mask"]
    rgba = np.zeros((*mask.shape, 4), dtype=np.uint8)
    rgba[mask] = (255, 60, 60, 170)
    Image.fromarray(rgba, mode="RGBA").save(out / "change.png")

    (out / "flood.geojson").write_text(_geojson_text(result["flood"]), encoding="utf-8")
    (out / "roads_affected.geojson").write_text(_geojson_text(result["affected_roads"]), encoding="utf-8")
    (out / "villages_near.geojson").write_text(_geojson_text(result["near_villages"]), encoding="utf-8")

    meta = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "bounds": _bounds_wgs84(transform, mask.shape),
        "primary_method": result["primary_method"],
        "thresholds_db": result["thresholds_db"],
        "metrics": result["metrics"],
        "summary": result["summary"],
        "synthetic": False,
        "event_name": "TBD",
        "note": "",
    }
    if meta_extra:
        meta.update(meta_extra)
    (out / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return out / "meta.json"
