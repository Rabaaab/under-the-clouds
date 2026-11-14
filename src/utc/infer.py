"""Run the model over a full scene with overlapping tiles."""

from __future__ import annotations

import numpy as np
import torch

from .preprocess import tile_positions


@torch.no_grad()
def predict_scene(
    model,
    scene: np.ndarray,
    size: int = 256,
    overlap: int = 32,
    device: str = "cpu",
    batch_size: int = 8,
) -> np.ndarray:
    """Return a water-probability map (H, W) for a normalised (C, H, W) scene.

    Overlapping tiles are averaged. Scenes smaller than `size` are edge-padded and cropped back.
    """
    if overlap >= size:
        raise ValueError("overlap must be smaller than size")
    model = model.to(device).eval()
    c, h, w = scene.shape
    pad_h, pad_w = max(0, size - h), max(0, size - w)
    x = np.pad(scene, ((0, 0), (0, pad_h), (0, pad_w)), mode="edge") if (pad_h or pad_w) else scene
    _, hp, wp = x.shape

    positions = tile_positions(hp, wp, size, size - overlap)
    prob = np.zeros((hp, wp), dtype=np.float32)
    count = np.zeros((hp, wp), dtype=np.float32)
    for i in range(0, len(positions), batch_size):
        batch_pos = positions[i : i + batch_size]
        batch = np.stack([x[:, y : y + size, xx : xx + size] for y, xx in batch_pos])
        out = torch.sigmoid(model(torch.from_numpy(batch).float().to(device))).cpu().numpy()[:, 0]
        for (y, xx), p in zip(batch_pos, out):
            prob[y : y + size, xx : xx + size] += p
            count[y : y + size, xx : xx + size] += 1.0
    return (prob / np.maximum(count, 1.0))[:h, :w]
