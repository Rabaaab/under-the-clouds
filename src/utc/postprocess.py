"""Clean-up to reduce false alarms: remove tiny blobs and steep terrain."""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

# Heuristic default; flooding on steep slopes is unlikely, but tune per region.
DEFAULT_MAX_SLOPE_DEG = 10.0


def remove_small_objects(mask: np.ndarray, min_size: int = 20) -> np.ndarray:
    """Drop connected components smaller than `min_size` pixels (8-connectivity)."""
    mask = np.asarray(mask).astype(bool)
    labels, n = ndi.label(mask, structure=np.ones((3, 3), dtype=int))
    if n == 0:
        return mask
    counts = np.bincount(labels.ravel())
    keep = counts >= min_size
    keep[0] = False
    return keep[labels]


def slope_from_dem(dem: np.ndarray, pixel_size_m: float) -> np.ndarray:
    """Slope in degrees from a DEM with square pixels in a projected (metre) grid.

    If your DEM is in degrees (EPSG:4326), reproject it to a metric CRS first.
    """
    dem = np.asarray(dem, dtype=np.float32)
    gy, gx = np.gradient(dem, pixel_size_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def mask_steep(mask: np.ndarray, slope_deg: np.ndarray, max_slope_deg: float = DEFAULT_MAX_SLOPE_DEG) -> np.ndarray:
    """Remove detections on terrain steeper than `max_slope_deg` (radar shadow looks like water)."""
    mask = np.asarray(mask).astype(bool)
    if slope_deg.shape != mask.shape:
        raise ValueError("slope and mask shapes differ")
    return mask & (slope_deg <= max_slope_deg)


def clean_change(
    change: np.ndarray,
    min_size: int = 20,
    slope_deg: np.ndarray | None = None,
    max_slope_deg: float = DEFAULT_MAX_SLOPE_DEG,
) -> np.ndarray:
    out = np.asarray(change).astype(bool)
    if slope_deg is not None:
        out = mask_steep(out, slope_deg, max_slope_deg)
    return remove_small_objects(out, min_size)
