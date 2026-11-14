"""Threshold baseline: water is dark in radar, so mark very low backscatter as water."""

from __future__ import annotations

import warnings

import numpy as np

# Heuristic defaults for VV backscatter in dB. Tune per scene: they are NOT validated values.
SANE_RANGE_DB = (-30.0, -10.0)
FALLBACK_THRESHOLD_DB = -18.0


def otsu_threshold(values: np.ndarray, bins: int = 256) -> float:
    """Otsu's threshold for a 1-D collection of values (NaNs ignored)."""
    v = np.asarray(values, dtype=np.float64).ravel()
    v = v[np.isfinite(v)]
    if v.size == 0:
        raise ValueError("no finite values")
    hist, edges = np.histogram(v, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2.0
    w0 = np.cumsum(hist)
    w1 = w0[-1] - w0
    sum0 = np.cumsum(hist * centers)
    mu0 = sum0 / np.maximum(w0, 1)
    mu1 = (sum0[-1] - sum0) / np.maximum(w1, 1)
    between = w0 * w1 * (mu0 - mu1) ** 2
    return float(centers[int(np.argmax(between))])


def water_mask_threshold(
    vv_db: np.ndarray,
    threshold: float | None = None,
    sane_range: tuple[float, float] = SANE_RANGE_DB,
    fallback: float = FALLBACK_THRESHOLD_DB,
) -> tuple[np.ndarray, float]:
    """Return (water_mask, threshold_used) for a backscatter image in dB (VV by default).

    If no threshold is given, Otsu is used. If Otsu lands outside `sane_range`
    (for example when water is a tiny share of the scene), `fallback` is used instead.
    For a VH band pass a lower range and fallback, for example sane_range=(-35, -15), fallback=-21.
    """
    vv_db = np.asarray(vv_db, dtype=np.float32)
    if not np.isfinite(vv_db).any():  # a scene with no valid pixels at all: nothing can be water
        return np.zeros(vv_db.shape, dtype=bool), float(fallback if threshold is None else threshold)
    if threshold is None:
        threshold = otsu_threshold(vv_db)
        lo, hi = sane_range
        if not (lo <= threshold <= hi):
            warnings.warn(
                f"Otsu threshold {threshold:.1f} dB outside {sane_range}; using fallback {fallback} dB",
                stacklevel=2,
            )
            threshold = fallback
    mask = np.isfinite(vv_db) & (vv_db < threshold)
    return mask, float(threshold)
