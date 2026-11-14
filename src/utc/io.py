"""GeoTIFF reading/writing and mask-to-polygon conversion."""

from __future__ import annotations

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


def read_geotiff(path):
    """Return (array (bands,H,W) float32 with nodata as NaN, transform, crs)."""
    with rasterio.open(path) as src:
        arr = src.read().astype(np.float32)
        if src.nodata is not None:
            arr[arr == src.nodata] = np.nan
        return arr, src.transform, src.crs


def write_geotiff(path, array: np.ndarray, transform, crs, nodata: float | None = None) -> None:
    arr = array if array.ndim == 3 else array[None]
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[1],
        width=arr.shape[2],
        count=arr.shape[0],
        dtype=arr.dtype,
        crs=crs,
        transform=transform,
        nodata=nodata,
    ) as dst:
        dst.write(arr)


def pixel_to_xy(transform, col: float, row: float) -> tuple[float, float]:
    """Map pixel corner (col, row) to (x, y) in the CRS. Works with any `affine` version."""
    return (
        transform.a * col + transform.b * row + transform.c,
        transform.d * col + transform.e * row + transform.f,
    )


def mask_to_gdf(mask: np.ndarray, transform, crs) -> gpd.GeoDataFrame:
    """Vectorise a boolean mask into polygons (one row per connected region)."""
    mask = np.asarray(mask).astype(bool)
    geoms = [shape(g) for g, v in shapes(mask.astype(np.uint8), mask=mask, transform=transform) if v == 1]
    return gpd.GeoDataFrame({"geometry": geoms}, geometry="geometry", crs=crs)
