"""End-to-end pipeline: before/after radar in dB -> change mask -> impact."""

from __future__ import annotations

import numpy as np

from .baseline import water_mask_threshold
from .change import flood_change
from .impact import impact_summary
from .io import mask_to_gdf
from .metrics import evaluate
from .postprocess import clean_change
from .preprocess import normalize_db


def run_pipeline(
    before_db: np.ndarray,
    after_db: np.ndarray,
    transform,
    crs,
    roads=None,
    villages=None,
    checkpoint: str | None = None,
    truth_new_water: np.ndarray | None = None,
    slope_deg: np.ndarray | None = None,
    min_size: int = 20,
    device: str = "cpu",
) -> dict:
    """Run baseline (always) and CNN (if a checkpoint is given) on a (2,H,W) VV/VH dB pair.

    The CNN result is used for the impact layer when available; otherwise the baseline is used.
    `truth_new_water` is optional: if given, IoU/F1 are reported for each method.
    """
    if before_db.shape != after_db.shape:
        raise ValueError(f"shape mismatch: {before_db.shape} vs {after_db.shape}")

    wb, t_before = water_mask_threshold(before_db[0])
    wa, t_after = water_mask_threshold(after_db[0])
    methods = {"baseline": clean_change(flood_change(wb, wa)["new_water"], min_size, slope_deg)}

    if checkpoint:
        from .infer import predict_scene
        from .model import load_model

        model = load_model(checkpoint, device)
        pb = predict_scene(model, normalize_db(before_db), device=device)
        pa = predict_scene(model, normalize_db(after_db), device=device)
        methods["cnn"] = clean_change(flood_change(pb > 0.5, pa > 0.5)["new_water"], min_size, slope_deg)

    primary = "cnn" if "cnn" in methods else "baseline"
    metrics = {}
    if truth_new_water is not None:
        metrics = {name: evaluate(mask, truth_new_water) for name, mask in methods.items()}

    flood = mask_to_gdf(methods[primary], transform, crs)
    summary, affected_roads, near_villages = impact_summary(flood, roads, villages)
    return {
        "primary_method": primary,
        "methods": methods,
        "change_mask": methods[primary],
        "thresholds_db": {"before": t_before, "after": t_after},
        "metrics": metrics,
        "flood": flood,
        "summary": summary,
        "affected_roads": affected_roads,
        "near_villages": near_villages,
    }
