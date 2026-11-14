"""Change detection from two water masks."""

from __future__ import annotations

import numpy as np


def flood_change(water_before: np.ndarray, water_after: np.ndarray) -> dict[str, np.ndarray]:
    """Compare two water masks.

    new_water        : water after, not water before (newly flooded)
    receded          : water before, not water after
    permanent_water  : water on both dates (rivers, lakes: not counted as flooding)
    """
    b = np.asarray(water_before).astype(bool)
    a = np.asarray(water_after).astype(bool)
    if a.shape != b.shape:
        raise ValueError(f"shape mismatch: {b.shape} vs {a.shape}")
    return {"new_water": a & ~b, "receded": b & ~a, "permanent_water": a & b}
