"""Segmentation metrics for binary masks."""

from __future__ import annotations

import numpy as np


def confusion(pred: np.ndarray, truth: np.ndarray, valid: np.ndarray | None = None) -> dict[str, int]:
    pred = np.asarray(pred).astype(bool)
    truth = np.asarray(truth).astype(bool)
    if pred.shape != truth.shape:
        raise ValueError(f"shape mismatch: {pred.shape} vs {truth.shape}")
    if valid is not None:
        valid = np.asarray(valid).astype(bool)
        pred, truth = pred[valid], truth[valid]
    tp = int(np.sum(pred & truth))
    fp = int(np.sum(pred & ~truth))
    fn = int(np.sum(~pred & truth))
    tn = int(np.sum(~pred & ~truth))
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn}


def scores_from_counts(c: dict[str, int]) -> dict[str, float]:
    """Precision, recall, F1 and IoU. If both prediction and truth are empty, all scores are 1.0."""
    tp, fp, fn = c["tp"], c["fp"], c["fn"]
    if tp + fp + fn == 0:
        return {"precision": 1.0, "recall": 1.0, "f1": 1.0, "iou": 1.0}
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * tp / (2 * tp + fp + fn)
    iou = tp / (tp + fp + fn)
    return {"precision": precision, "recall": recall, "f1": f1, "iou": iou}


def evaluate(pred: np.ndarray, truth: np.ndarray, valid: np.ndarray | None = None) -> dict[str, float]:
    return scores_from_counts(confusion(pred, truth, valid))
