"""Training chips: saving, listing, loading, and a PyTorch dataset."""

from __future__ import annotations

import random
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset

from .preprocess import extract_chips


def save_chips(
    x: np.ndarray,
    y: np.ndarray,
    out_dir: str | Path,
    prefix: str,
    size: int = 256,
    stride: int = 256,
    min_valid_fraction: float = 0.5,
) -> int:
    """Cut a scene into .npz chips. x: (C,H,W) float32 in [0,1]; y: (H,W) with 1 water, 0 land, -1 ignore."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for r, c, chip in extract_chips(x, size, stride):
        lab = y[r : r + size, c : c + size]
        if (lab >= 0).mean() < min_valid_fraction:
            continue
        np.savez_compressed(out / f"{prefix}_{r}_{c}.npz", x=chip.astype(np.float32), y=lab.astype(np.int8))
        count += 1
    return count


def list_chip_files(chips_dir: str | Path) -> list[Path]:
    return sorted(Path(chips_dir).glob("*.npz"))


def split_files(files: list[Path], val_fraction: float = 0.2, seed: int = 0) -> tuple[list[Path], list[Path]]:
    files = list(files)
    rng = random.Random(seed)
    rng.shuffle(files)
    n_val = max(1, int(round(len(files) * val_fraction))) if len(files) > 1 else 0
    return files[n_val:], files[:n_val]


class ChipDataset(Dataset):
    """Each item: (x, target, valid) with shapes (C,H,W), (1,H,W), (1,H,W)."""

    def __init__(self, files: list[Path], augment: bool = False):
        self.files = list(files)
        self.augment = augment

    def __len__(self) -> int:
        return len(self.files)

    def __getitem__(self, idx: int):
        d = np.load(self.files[idx])
        x, y = d["x"], d["y"]
        if self.augment:
            k = random.randint(0, 3)
            x, y = np.rot90(x, k, axes=(1, 2)), np.rot90(y, k)
            if random.random() < 0.5:
                x, y = x[:, :, ::-1], y[:, ::-1]
        valid = (y >= 0).astype(np.float32)[None]
        target = (y == 1).astype(np.float32)[None]
        return (
            torch.from_numpy(np.ascontiguousarray(x, dtype=np.float32)),
            torch.from_numpy(np.ascontiguousarray(target)),
            torch.from_numpy(np.ascontiguousarray(valid)),
        )

