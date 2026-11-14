"""Run the pipeline on a REAL before/after scene pair (GeoTIFFs) and export the web-map files.

Inputs are 2-band GeoTIFFs (band 1 = VV, band 2 = VH) on the same grid in EPSG:4326.
Use --linear if the values are linear intensity (the speckle filter and dB conversion are then applied);
omit it if they are already in dB.

    python scripts/run_event.py --before before.tif --after after.tif --event-name "My event" \
        --roads roads.geojson --villages villages.geojson --out app/data

Status: tested only on synthetic GeoTIFFs. Real NISAR / Sentinel-1 products need their own preparation
(calibration, terrain correction, co-registration, reprojection) before this step.
"""

from __future__ import annotations

import argparse
import json

import geopandas as gpd
import numpy as np

from .export_web import export_web
from .io import read_geotiff
from .pipeline import run_pipeline
from .preprocess import lee_filter, to_db


def _prepare(arr: np.ndarray, linear: bool) -> np.ndarray:
    if arr.shape[0] < 2:
        raise ValueError("expected a 2-band GeoTIFF (VV, VH)")
    arr = arr[:2]
    return np.stack([to_db(lee_filter(b)) for b in arr]) if linear else arr


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--linear", action="store_true")
    p.add_argument("--roads", default=None, help="GeoJSON/Shapefile of roads")
    p.add_argument("--villages", default=None, help="GeoJSON/Shapefile of villages (points)")
    p.add_argument("--truth", default=None, help="optional GeoTIFF mask of new water, for IoU/F1")
    p.add_argument("--checkpoint", default=None)
    p.add_argument("--event-name", default="TBD")
    p.add_argument("--note", default="")
    p.add_argument("--out", default="app/data")
    args = p.parse_args(argv)

    b, tr_b, crs_b = read_geotiff(args.before)
    a, tr_a, crs_a = read_geotiff(args.after)
    if b.shape != a.shape or tr_b != tr_a or crs_b != crs_a:
        raise SystemExit("before and after must be on the same grid (shape, transform, CRS). Co-register them first.")

    truth = None
    if args.truth:
        truth = read_geotiff(args.truth)[0][0] > 0.5

    result = run_pipeline(
        _prepare(b, args.linear),
        _prepare(a, args.linear),
        tr_b,
        crs_b,
        roads=gpd.read_file(args.roads) if args.roads else None,
        villages=gpd.read_file(args.villages) if args.villages else None,
        checkpoint=args.checkpoint,
        truth_new_water=truth,
    )
    meta = export_web(
        args.out,
        _prepare(b, args.linear),
        _prepare(a, args.linear),
        result,
        tr_b,
        crs_b,
        {"synthetic": False, "event_name": args.event_name, "note": args.note},
    )
    print(f"wrote {meta}")
    # ensure_ascii keeps Arabic village names from crashing consoles that cannot print them
    print(json.dumps(result["summary"], ensure_ascii=True))
    if result["metrics"]:
        print(json.dumps(result["metrics"]))


if __name__ == "__main__":
    main()
