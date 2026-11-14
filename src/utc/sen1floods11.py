"""Sen1Floods11 hand-labelled subset: download, training chips, and scene-level evaluation.

Verified against the official repo and public bucket (v1.1): S1Hand files are 512x512 Sentinel-1 in dB
(band 1 = VV, band 2 = VH, NaN = no data), LabelHand files hold -1 (no data) / 0 (land) / 1 (water), and the
split CSVs (flood_train_data.csv, flood_valid_data.csv, flood_test_data.csv) have no header and two columns:
the S1 file name and the label file name.

Our local layout (made by `download`):
    <root>/S1Hand/*.tif   <root>/LabelHand/*.tif   <root>/splits/*.csv
If you copied the bucket yourself, build `Paths(s1_dir, label_dir, splits_dir)` directly.
"""

from __future__ import annotations

import csv
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .baseline import water_mask_threshold
from .dataset import save_chips
from .io import read_geotiff
from .metrics import confusion, scores_from_counts
from .preprocess import normalize_db

BUCKET_URL = "https://storage.googleapis.com/sen1floods11/v1.1"
SPLIT_FILES = {
    "train": "flood_train_data.csv",
    "valid": "flood_valid_data.csv",
    "test": "flood_test_data.csv",
}


@dataclass
class Paths:
    s1_dir: Path
    label_dir: Path
    splits_dir: Path

    @classmethod
    def from_root(cls, root) -> "Paths":
        root = Path(root)
        return cls(root / "S1Hand", root / "LabelHand", root / "splits")


def read_split_csv(path) -> list[tuple[str, str]]:
    """(s1_file_name, label_file_name) pairs from a header-less two-column CSV."""
    pairs = []
    with open(path, newline="") as f:
        for row in csv.reader(f):
            if len(row) >= 2 and row[0].strip():
                pairs.append((row[0].strip(), row[1].strip()))
    return pairs


def _fetch(url: str, dest: Path, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            urllib.request.urlretrieve(url, dest)
            return
        except Exception:  # network hiccup: retry, then give up loudly
            if attempt == retries:
                raise
            time.sleep(2 * attempt)


def download(root, splits=("train", "valid", "test"), limit: int | None = None, log=print) -> Paths:
    """Download the split CSVs and the S1 + label chips they list (about 650 MB for all three splits).

    `limit` keeps only the first N pairs of each split (handy for a quick test).
    """
    paths = Paths.from_root(root)
    for split in splits:
        csv_name = SPLIT_FILES[split]
        csv_path = paths.splits_dir / csv_name
        if not csv_path.exists():
            _fetch(f"{BUCKET_URL}/splits/flood_handlabeled/{csv_name}", csv_path)
        pairs = read_split_csv(csv_path)[:limit]
        for i, (s1_name, label_name) in enumerate(pairs, 1):
            s1_dest, lab_dest = paths.s1_dir / s1_name, paths.label_dir / label_name
            if not s1_dest.exists():
                _fetch(f"{BUCKET_URL}/data/flood_events/HandLabeled/S1Hand/{s1_name}", s1_dest)
            if not lab_dest.exists():
                _fetch(f"{BUCKET_URL}/data/flood_events/HandLabeled/LabelHand/{label_name}", lab_dest)
            if i % 25 == 0 or i == len(pairs):
                log(f"{split}: {i}/{len(pairs)}")
    return paths


def load_scene(s1_path, label_path) -> tuple[np.ndarray, np.ndarray]:
    """Return (db (2,H,W) float32 with NaN for no data, y (H,W) int8: 1 water, 0 land, -1 ignore)."""
    db, _, _ = read_geotiff(s1_path)
    lab, _, _ = read_geotiff(label_path)
    y = np.nan_to_num(lab[0], nan=-1.0).astype(np.int8)
    y[~np.isfinite(db[:2]).all(axis=0)] = -1
    return db[:2], y


def prepare_chips(paths: Paths, out_dir, size: int = 256, splits=("train", "valid", "test")) -> dict:
    """Cut scenes into normalised .npz chips, one folder per split so test data never leaks into training."""
    out_dir = Path(out_dir)
    report = {}
    for split in splits:
        scenes = chips = skipped = 0
        for s1_name, label_name in read_split_csv(paths.splits_dir / SPLIT_FILES[split]):
            s1_path, lab_path = paths.s1_dir / s1_name, paths.label_dir / label_name
            if not (s1_path.exists() and lab_path.exists()):
                skipped += 1
                continue
            db, y = load_scene(s1_path, lab_path)
            if y.shape[0] < size or y.shape[1] < size:
                skipped += 1
                continue
            chips += save_chips(
                normalize_db(db), y, out_dir / split, s1_name.replace("_S1Hand.tif", ""), size=size, stride=size
            )
            scenes += 1
        report[split] = {"scenes": scenes, "chips": chips, "skipped": skipped}
    return report


_BIN_EDGES = np.arange(-60.0, 20.25, 0.25)


def fit_global_thresholds(paths: Paths, split: str = "train", limit: int | None = None) -> dict:
    """Best single dB threshold per band (VV, VH), chosen to maximise IoU on the training scenes.

    This is the strongest *simple* baseline: one fixed cut-off learned from labelled data, no CNN. The
    CNN has to beat it to be worth using. Scores are pooled over all valid pixels.
    """
    n_bins = len(_BIN_EDGES) - 1
    water = [np.zeros(n_bins), np.zeros(n_bins)]
    land = [np.zeros(n_bins), np.zeros(n_bins)]
    n_scenes = 0
    for s1_name, label_name in read_split_csv(paths.splits_dir / SPLIT_FILES[split])[:limit]:
        s1_path, lab_path = paths.s1_dir / s1_name, paths.label_dir / label_name
        if not (s1_path.exists() and lab_path.exists()):
            continue
        db, y = load_scene(s1_path, lab_path)
        for band in (0, 1):
            v = np.clip(db[band], _BIN_EDGES[0], _BIN_EDGES[-1] - 1e-3)
            water[band] += np.histogram(v[y == 1], bins=_BIN_EDGES)[0]
            land[band] += np.histogram(v[y == 0], bins=_BIN_EDGES)[0]
        n_scenes += 1
    if n_scenes == 0:
        raise ValueError(f"no scenes of split '{split}' found under {paths.s1_dir}")

    out = {"n_scenes": n_scenes}
    for band, name in ((0, "vv"), (1, "vh")):
        tp = np.cumsum(water[band])
        fp = np.cumsum(land[band])
        fn = water[band].sum() - tp
        iou = tp / np.maximum(tp + fp + fn, 1.0)
        k = int(np.argmax(iou))
        out[name] = float(_BIN_EDGES[k + 1])  # pixels below this value are called water
        out[f"{name}_train_iou"] = float(iou[k])
    return out


def evaluate_split(
    paths: Paths,
    split: str = "test",
    checkpoint: str | None = None,
    device: str = "cpu",
    limit: int | None = None,
) -> dict:
    """Scene-level IoU/F1 for the baselines and, if a checkpoint is given, the trained CNN.

    Methods: `baseline_vv` / `baseline_vh` (Otsu threshold per scene, the naive approach) and
    `tuned_vv` / `tuned_vh` (one global threshold fitted on the training split, the strongest simple
    baseline). All are scored on the same scenes and the same valid pixels (label != -1), pooled over pixels.
    """
    methods = {"baseline_vv": {}, "baseline_vh": {}}
    thresholds = None
    try:
        thresholds = fit_global_thresholds(paths, "train")
        methods.update({"tuned_vv": {}, "tuned_vh": {}})
    except (ValueError, FileNotFoundError):
        pass  # no training scenes available: skip the tuned baselines
    model = None
    if checkpoint:
        from .infer import predict_scene
        from .model import load_model

        model = load_model(checkpoint, device)
        methods["cnn"] = {}
    counts = {name: {"tp": 0, "fp": 0, "fn": 0, "tn": 0} for name in methods}

    pairs = read_split_csv(paths.splits_dir / SPLIT_FILES[split])[:limit]
    n_scenes = 0
    for s1_name, label_name in pairs:
        s1_path, lab_path = paths.s1_dir / s1_name, paths.label_dir / label_name
        if not (s1_path.exists() and lab_path.exists()):
            continue
        db, y = load_scene(s1_path, lab_path)
        truth, valid = y == 1, y >= 0
        preds = {
            "baseline_vv": water_mask_threshold(db[0])[0],
            "baseline_vh": water_mask_threshold(db[1], sane_range=(-35.0, -15.0), fallback=-21.0)[0],
        }
        if thresholds is not None:
            preds["tuned_vv"] = np.isfinite(db[0]) & (db[0] < thresholds["vv"])
            preds["tuned_vh"] = np.isfinite(db[1]) & (db[1] < thresholds["vh"])
        if model is not None:
            preds["cnn"] = predict_scene(model, normalize_db(db), device=device) > 0.5
        for name, pred in preds.items():
            for k, v in confusion(pred, truth, valid).items():
                counts[name][k] += v
        n_scenes += 1

    out = {name: scores_from_counts(c) for name, c in counts.items()}
    out["n_scenes"] = n_scenes
    if thresholds is not None:
        out["tuned_thresholds_db"] = {"vv": thresholds["vv"], "vh": thresholds["vh"], "fit_scenes": thresholds["n_scenes"]}
    return out
