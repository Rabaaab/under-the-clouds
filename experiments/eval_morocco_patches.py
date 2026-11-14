"""Score the CNN and Otsu on dated Zone 1 and Zone 4 SAR Morocco patches."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import warnings
from pathlib import Path

import numpy as np
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for import_path in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from experiments.predict_water import REFERENCE_LIMITATION, predict_water_array
from utc.baseline import water_mask_threshold
from utc.metrics import confusion, scores_from_counts
from utc.model import load_model

EVENT_DATES = (dt.date(2026, 1, 21), dt.date(2026, 2, 8))
DATE_WINDOW_DAYS = 6
OTSU_CIRCULARITY = (
    "The reference masks were produced using HSBA plus Otsu and morphological "
    "cleaning. Otsu is therefore not an independent comparator and may agree "
    "with the labels by construction; these are not expert-ground-truth scores."
)


def parse_dates(value: str | None) -> list[dt.date]:
    """Parse compact YYYY-MM-DD or YYYYMMDD dates from a metadata value."""
    if not value:
        return []
    tokens = re.findall(r"(?<!\d)20\d{2}[-_/]?\d{2}[-_/]?\d{2}(?!\d)", str(value))
    parsed = []
    for token in tokens:
        normalized = re.sub(r"[-_/]", "", token)
        try:
            parsed.append(dt.datetime.strptime(normalized, "%Y%m%d").date())
        except ValueError:
            continue
    return parsed


def is_in_event_window(value: str | None, window_days: int = DATE_WINDOW_DAYS) -> bool:
    """Include a patch if its date or date interval overlaps either event window."""
    dates = parse_dates(value)
    if not dates:
        return False
    first, last = min(dates), max(dates)
    return any(
        first <= target + dt.timedelta(days=window_days)
        and last >= target - dt.timedelta(days=window_days)
        for target in EVENT_DATES
    )


def score_patch(
    scene: np.ndarray,
    label: np.ndarray,
    model,
    device: str = "cpu",
) -> dict:
    """Score one image/mask pair with common valid pixels for both methods."""
    label = np.asarray(label)
    if label.ndim != 2:
        raise ValueError("expected a 2-D water mask")
    cnn_mask, db, image_valid, unit = predict_water_array(
        scene, model, device=device, input_unit="auto"
    )
    if label.shape != image_valid.shape:
        raise ValueError(f"image/mask shape mismatch: {image_valid.shape} vs {label.shape}")

    label_valid = np.isfinite(label) & (label != 255) & (label != -1)
    valid = image_valid & label_valid
    if not valid.any():
        raise ValueError("patch has no valid pixels to score")
    truth = label > 0

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        otsu_mask, threshold = water_mask_threshold(db[0])
    fallback = any("using fallback" in str(item.message) for item in caught)

    return {
        "cnn": confusion(cnn_mask, truth, valid),
        "otsu": confusion(otsu_mask, truth, valid),
        "valid_pixels": int(valid.sum()),
        "input_unit": unit,
        "otsu_threshold_db": float(threshold),
        "otsu_fallback": fallback,
    }


def _empty_counts() -> dict[str, int]:
    return {"tp": 0, "fp": 0, "fn": 0, "tn": 0}


def _add_counts(target: dict[str, int], values: dict[str, int]) -> None:
    for key in target:
        target[key] += values[key]


def _zone_metadata(root: Path, zone_number: int) -> Path:
    candidates = sorted(root.glob(f"Zone{zone_number}*/metadata_zone{zone_number}.csv"))
    if len(candidates) != 1:
        raise FileNotFoundError(
            f"expected one Zone {zone_number} metadata CSV under {root}, found {len(candidates)}"
        )
    return candidates[0]


def _read_band_first(path: Path) -> tuple[np.ndarray, np.ndarray]:
    with rasterio.open(path) as src:
        data = src.read().astype(np.float32)
        valid = src.read_masks() > 0
        if src.nodata is not None and not np.isnan(src.nodata):
            data[data == src.nodata] = np.nan
    return data, valid


def evaluate_zone(root: Path, zone_number: int, model, device: str = "cpu") -> dict:
    metadata_path = _zone_metadata(root, zone_number)
    counts = {"cnn": _empty_counts(), "otsu": _empty_counts()}
    patches_without_date = 0
    patches_outside_window = 0
    patches_scored = 0
    otsu_fallbacks = 0
    units: dict[str, int] = {}

    with metadata_path.open(newline="", encoding="utf-8-sig") as metadata_file:
        rows = list(csv.DictReader(metadata_file))
    for row in rows:
        acquisition = row.get("acquisition_date") or ""
        date_text = acquisition or row.get("image_path") or row.get("patch_id")
        if not parse_dates(date_text):
            patches_without_date += 1
            continue
        if not is_in_event_window(date_text):
            patches_outside_window += 1
            continue

        image_path = root / row["image_path"]
        mask_path = root / row["mask_path"]
        image, image_valid_bands = _read_band_first(image_path)
        label_bands, label_valid_bands = _read_band_first(mask_path)
        if image.shape[0] < 2 or label_bands.shape[0] < 1:
            raise ValueError(f"expected two image bands and one mask band: {image_path}")
        if not image_valid_bands[:2].all(axis=0).any():
            raise ValueError(f"image patch has no valid pixels: {image_path}")
        label = label_bands[0]
        label[~label_valid_bands[0]] = np.nan
        scored = score_patch(image, label, model, device=device)
        _add_counts(counts["cnn"], scored["cnn"])
        _add_counts(counts["otsu"], scored["otsu"])
        units[scored["input_unit"]] = units.get(scored["input_unit"], 0) + 1
        otsu_fallbacks += int(scored["otsu_fallback"])
        patches_scored += 1

    if patches_scored == 0:
        raise ValueError(
            f"no dated Zone {zone_number} patches fall within +/-{DATE_WINDOW_DAYS} "
            "days of either event date"
        )
    return {
        "patches_available": len(rows),
        "patches_scored": patches_scored,
        "patches_without_date": patches_without_date,
        "patches_outside_date_window": patches_outside_window,
        "input_units": units,
        "otsu_fallback_patches": otsu_fallbacks,
        "cnn": {**scores_from_counts(counts["cnn"]), "counts": counts["cnn"]},
        "otsu": {**scores_from_counts(counts["otsu"]), "counts": counts["otsu"]},
    }


def resolve_data_root(value: str | None) -> Path:
    if value:
        root = Path(value)
        return root if root.is_absolute() else PROJECT_ROOT / root
    return PROJECT_ROOT / "data" / "SAR_Morocco"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data-root",
        default=None,
        help="Zenodo dataset root (default: data/SAR_Morocco)",
    )
    parser.add_argument("--checkpoint", default="outputs/unet.pt")
    parser.add_argument("--out", default="experiments/morocco_patches_metrics.json")
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)

    data_root = resolve_data_root(args.data_root)
    checkpoint = Path(args.checkpoint)
    if not checkpoint.is_absolute():
        checkpoint = PROJECT_ROOT / checkpoint
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = PROJECT_ROOT / out_path

    if not data_root.is_dir():
        report = {
            "status": "not run on real data",
            "reason": f"dataset directory does not exist: {data_root}",
            "reference_limitation": REFERENCE_LIMITATION,
            "otsu_circularity": OTSU_CIRCULARITY,
            "cnn_status": "not scored locally: outputs/unet.pt is on Drive",
            "zones": {},
        }
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            json.dumps(report, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        print(report["status"])
        print(report["reason"])
        print(f"wrote {out_path}")
        print(f"Reference limitation: {REFERENCE_LIMITATION}")
        print(f"Otsu circularity: {OTSU_CIRCULARITY}")
        return

    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"checkpoint not found: {checkpoint}; patch CNN evaluation requires unet.pt"
        )
    model = load_model(str(checkpoint), device=args.device)
    zones = {
        f"Zone{zone_number}": evaluate_zone(data_root, zone_number, model, args.device)
        for zone_number in (1, 4)
    }
    report = {
        "dataset": "SAR Morocco Flood Dataset, Zenodo 10.5281/zenodo.22964153",
        "reference_limitation": REFERENCE_LIMITATION,
        "otsu_circularity": OTSU_CIRCULARITY,
        "comparison": (
            "Water-mask IoU/F1 pooled over valid patch pixels; not a flood-change score."
        ),
        "event_dates": [date.isoformat() for date in EVENT_DATES],
        "date_window_days": DATE_WINDOW_DAYS,
        "unknown_date_policy": "Patches with no readable date are excluded and counted.",
        "data_root": str(data_root),
        "checkpoint": str(checkpoint),
        "zones": zones,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    for zone_name, result in zones.items():
        print(
            f"{zone_name}: patches={result['patches_scored']}, "
            f"without_date={result['patches_without_date']}, "
            f"outside_window={result['patches_outside_date_window']}"
        )
        for method in ("cnn", "otsu"):
            scores = result[method]
            print(f"  {method}: IoU={scores['iou']:.4f}, F1={scores['f1']:.4f}")
    print(f"wrote {out_path}")
    print(f"Reference limitation: {REFERENCE_LIMITATION}")
    print(f"Otsu circularity: {OTSU_CIRCULARITY}")


if __name__ == "__main__":
    main()
