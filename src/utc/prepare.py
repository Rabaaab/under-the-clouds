"""Turn per-polarisation radar GeoTIFFs (for example ASF HyP3 Sentinel-1 RTC products) into the two
2-band, same-grid, EPSG:4326 GeoTIFFs that `scripts/run_event.py` expects.

    python scripts/prepare_scene.py \
        --before-vv B_VV.tif --before-vh B_VH.tif --after-vv A_VV.tif --after-vh A_VH.tif \
        --bbox WEST SOUTH EAST NORTH --res 30 --unit power --out data/event

HyP3 RTC products come as one GeoTIFF per polarisation in a UTM zone, with 0 meaning no data (checked against
ASF's product guide, not against a real download yet). The script warps all four files onto ONE shared
lon/lat grid so before and after line up pixel for pixel.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import Resampling, reproject

from .io import write_geotiff

MAX_PIXELS = 25_000_000  # guard against a huge bbox at a fine resolution


def make_grid(bbox: tuple[float, float, float, float], res_m: float):
    """Shared EPSG:4326 grid covering (west, south, east, north) with square pixels of about `res_m` metres."""
    west, south, east, north = bbox
    if not (west < east and south < north):
        raise ValueError("bbox must be WEST SOUTH EAST NORTH with west < east and south < north")
    res = res_m / 111_320.0  # degrees per metre of latitude; fine for a small area
    width = max(1, int(round((east - west) / res)))
    height = max(1, int(round((north - south) / res)))
    if width * height > MAX_PIXELS:
        raise ValueError(f"{width}x{height} pixels is too many: use a smaller bbox or a coarser --res")
    return from_origin(west, north, res, res), width, height


def warp_band(path, transform, width: int, height: int, unit: str = "power", nodata: float | None = 0.0) -> np.ndarray:
    """Warp the first band of `path` onto the shared grid. No-data becomes NaN. Amplitude is squared to power."""
    dst = np.full((height, width), np.nan, dtype=np.float32)
    with rasterio.open(path) as src:
        reproject(
            source=rasterio.band(src, 1),
            destination=dst,
            src_transform=src.transform,
            src_crs=src.crs,
            src_nodata=None if unit == "db" else nodata,
            dst_transform=transform,
            dst_crs="EPSG:4326",
            dst_nodata=np.nan,
            resampling=Resampling.average,
        )
    return dst**2 if unit == "amplitude" else dst


def prepare_pair(before_vv, before_vh, after_vv, after_vh, bbox, out_dir, res_m: float = 30.0, unit: str = "power") -> dict:
    """Write before.tif and after.tif (band 1 = VV, band 2 = VH) on one shared grid and report coverage."""
    if unit not in ("power", "amplitude", "db"):
        raise ValueError("unit must be power, amplitude or db")
    transform, width, height = make_grid(tuple(bbox), res_m)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    report = {"width": width, "height": height, "unit_written": "db" if unit == "db" else "power"}
    for name, vv, vh in (("before", before_vv, before_vh), ("after", after_vv, after_vh)):
        stack = np.stack([warp_band(vv, transform, width, height, unit), warp_band(vh, transform, width, height, unit)])
        write_geotiff(out / f"{name}.tif", stack, transform, "EPSG:4326", nodata=float("nan"))
        report[f"{name}_valid_fraction"] = float(np.isfinite(stack).all(axis=0).mean())
    return report


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    for k in ("before-vv", "before-vh", "after-vv", "after-vh"):
        p.add_argument(f"--{k}", required=True)
    p.add_argument("--bbox", nargs=4, type=float, metavar=("WEST", "SOUTH", "EAST", "NORTH"), required=True)
    p.add_argument("--res", type=float, default=30.0, help="pixel size in metres (default 30)")
    p.add_argument("--unit", choices=["power", "amplitude", "db"], default="power")
    p.add_argument("--out", default="data/event")
    a = p.parse_args(argv)

    rep = prepare_pair(a.before_vv, a.before_vh, a.after_vv, a.after_vh, a.bbox, a.out, a.res, a.unit)
    print(rep)
    flag = "" if a.unit == "db" else " --linear"
    print(f"Next: python scripts/run_event.py --before {a.out}/before.tif --after {a.out}/after.tif{flag} --event-name \"...\"")
    for k in ("before", "after"):
        if rep[f"{k}_valid_fraction"] < 0.9:
            print(f"WARNING: only {rep[f'{k}_valid_fraction']:.0%} of the {k} grid has valid pixels. Check that the scene covers your bbox.")


if __name__ == "__main__":
    main()
