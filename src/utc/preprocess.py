"""Radar preprocessing: decibels, speckle filtering, normalisation, tiling."""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi


def to_db(intensity: np.ndarray, eps: float = 1e-6) -> np.ndarray:
    """Convert linear backscatter intensity (sigma0) to decibels."""
    return 10.0 * np.log10(np.maximum(np.asarray(intensity, dtype=np.float32), eps))


def lee_filter(img: np.ndarray, size: int = 5) -> np.ndarray:
    """Simplified Lee speckle filter.

    Apply this to LINEAR intensity, then convert to dB afterwards. NaNs (no data)
    are kept as NaN in the output.
    """
    img = np.asarray(img, dtype=np.float32)
    nan_mask = ~np.isfinite(img)
    fill = float(np.nanmean(img)) if (~nan_mask).any() else 0.0
    work = np.where(nan_mask, fill, img)

    mean = ndi.uniform_filter(work, size)
    sq_mean = ndi.uniform_filter(work * work, size)
    var = np.maximum(sq_mean - mean * mean, 0.0)
    overall_var = float(np.var(work))
    weight = var / (var + overall_var + 1e-12)
    out = mean + weight * (work - mean)
    out[nan_mask] = np.nan
    return out.astype(np.float32)


# The same scaling is used for training chips and for inference. Changing it means retraining.
# The range (-50, 1) dB is the one used by the Sen1Floods11 authors' own training notebook.
DB_LO, DB_HI = -50.0, 1.0


def normalize_db(db: np.ndarray, lo: float = DB_LO, hi: float = DB_HI, fill: float = 1.0) -> np.ndarray:
    """Clip dB values to [lo, hi] and scale to [0, 1]. NaNs become `fill` (1.0 = bright, i.e. not water).

    Keep a separate validity mask for NaN pixels; `fill` only makes the array safe to feed a network.
    """
    db = np.asarray(db, dtype=np.float32)
    out = (np.clip(db, lo, hi) - lo) / (hi - lo)
    return np.nan_to_num(out, nan=fill).astype(np.float32)


def _starts(n: int, size: int, stride: int) -> list[int]:
    if n <= size:
        return [0]
    starts = list(range(0, n - size + 1, stride))
    if starts[-1] != n - size:
        starts.append(n - size)
    return starts


def tile_positions(height: int, width: int, size: int, stride: int) -> list[tuple[int, int]]:
    """Top-left (row, col) of tiles that cover the whole image, including the edges."""
    if size <= 0 or stride <= 0:
        raise ValueError("size and stride must be positive")
    return [(y, x) for y in _starts(height, size, stride) for x in _starts(width, size, stride)]


def extract_chips(arr: np.ndarray, size: int = 256, stride: int = 256):
    """Yield (row, col, chip) for a (C, H, W) array. The image must be at least `size` in both dims."""
    _, h, w = arr.shape
    if h < size or w < size:
        raise ValueError(f"image {h}x{w} is smaller than chip size {size}")
    for y, x in tile_positions(h, w, size, stride):
        yield y, x, arr[:, y : y + size, x : x + size]
