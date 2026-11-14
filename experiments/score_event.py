"""Score the after-date Otsu water mask and CNN mask against the event reference."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for import_path in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from utc.baseline import otsu_threshold
from utc.metrics import confusion, scores_from_counts
from utc.preprocess import to_db

REFERENCE_LIMITATION = (
    "Reference: Zenodo SAR Morocco Flood Dataset, HSBA + Otsu semi-automatic "
    "masks; not expert ground truth, may favour Otsu, covers only part of the "
    "scene, has unknown patch dates, and is a water mask rather than a change map."
)
CNN_NOTE = "CNN not scored locally: unet.pt is on Drive, will be scored in Colab"


def read_grid(path: str | Path) -> tuple[dict, np.ndarray, np.ndarray]:
    with rasterio.open(path) as src:
        array = src.read(1)
        grid = {
            "shape": (src.height, src.width),
            "crs": src.crs,
            "transform": src.transform,
        }
        nodata = src.nodata
    valid = np.isfinite(array)
    if nodata is not None:
        if np.isnan(nodata):
            valid &= np.isfinite(array)
        else:
            valid &= array != nodata
    return grid, np.asarray(array, dtype=np.float32), valid


def score_event_arrays(vv: np.ndarray, reference: np.ndarray) -> dict:
    """Return Otsu water-mask metrics on reference-covered valid pixels."""
    vv = np.asarray(vv, dtype=np.float32)
    reference = np.asarray(reference)
    if vv.ndim != 2 or reference.ndim != 2:
        raise ValueError("VV and reference arrays must be two-dimensional")
    if vv.shape != reference.shape:
        raise ValueError(f"shape mismatch: VV {vv.shape} vs reference {reference.shape}")

    finite = np.isfinite(vv)
    finite_values = vv[finite]
    if not finite_values.size:
        raise ValueError("after VV has no finite pixels")
    linear_power = bool(np.all(finite_values >= 0))
    vv_db = to_db(vv) if linear_power else vv
    valid_scene = finite & np.isfinite(vv_db)
    if linear_power:
        valid_scene &= vv_db > -60.0
    valid = valid_scene & np.isfinite(reference) & (reference != 255)
    if not valid.any():
        raise ValueError("reference has no valid pixels overlapping after VV")

    threshold = otsu_threshold(vv_db[valid_scene])
    baseline = valid_scene & (vv_db < threshold)
    truth = reference == 1
    counts = confusion(baseline, truth, valid)
    metrics = scores_from_counts(counts)
    return {
        "unit_detected": "linear_power" if linear_power else "dB",
        "otsu_threshold_db": float(threshold),
        "pixels_scored": int(valid.sum()),
        "baseline": {**metrics, **counts},
    }


def _clean_json(value):
    if isinstance(value, dict):
        return {key: _clean_json(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_clean_json(item) for item in value]
    if isinstance(value, (float, np.floating)) and not np.isfinite(value):
        return None
    if isinstance(value, np.generic):
        return value.item()
    return value


def score_event(
    after_path: str | Path,
    reference_path: str | Path,
    out_path: str | Path,
    after_date: str = "2026-02-08",
    cnn_path: str | Path | None = None,
) -> dict:
    after_grid, vv, vv_valid = read_grid(after_path)
    reference_grid, reference, reference_valid = read_grid(reference_path)
    for key in ("shape", "crs", "transform"):
        if after_grid[key] != reference_grid[key]:
            raise ValueError(
                f"after/reference grid mismatch for {key}: "
                f"{after_grid[key]} vs {reference_grid[key]}"
            )
    reference[~reference_valid] = np.nan
    vv[~vv_valid] = np.nan
    result = score_event_arrays(vv, reference)
    report = {
        "reference": "Zenodo SAR Morocco Flood Dataset (semi-automatic masks)",
        "reference_limitation": REFERENCE_LIMITATION,
        "after_date": after_date,
        "otsu_threshold_db": result["otsu_threshold_db"],
        "input_unit_detected": result["unit_detected"],
        "pixels_scored": result["pixels_scored"],
        "baseline": result["baseline"],
        "cnn": None,
        "cnn_note": CNN_NOTE,
    }
    if cnn_path is not None:
        cnn_grid, cnn_prediction, cnn_valid = read_grid(cnn_path)
        for key in ("shape", "crs", "transform"):
            if after_grid[key] != cnn_grid[key]:
                raise ValueError(
                    f"after/CNN grid mismatch for {key}: "
                    f"{after_grid[key]} vs {cnn_grid[key]}"
                )
        cnn_valid &= np.isfinite(cnn_prediction)
        score_valid = vv_valid & reference_valid & (reference != 255) & cnn_valid
        if not score_valid.any():
            raise ValueError("CNN prediction has no valid pixels in the reference mask")
        cnn_counts = confusion(cnn_prediction > 0, reference == 1, score_valid)
        report["cnn"] = {**scores_from_counts(cnn_counts), **cnn_counts}
        report["cnn_note"] = f"CNN scored from {cnn_path}"
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(_clean_json(report), indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print("Method  IoU       F1        Precision  Recall")
    baseline = report["baseline"]
    print(
        "Otsu    "
        f"{baseline['iou']:.6f}  {baseline['f1']:.6f}  "
        f"{baseline['precision']:.6f}    {baseline['recall']:.6f}"
    )
    if report["cnn"] is None:
        print("CNN     not scored locally")
    else:
        cnn = report["cnn"]
        print(
            "CNN     "
            f"{cnn['iou']:.6f}  {cnn['f1']:.6f}  "
            f"{cnn['precision']:.6f}    {cnn['recall']:.6f}"
        )
    print(f"after VV input unit: {result['unit_detected']}")
    print(f"Otsu threshold: {result['otsu_threshold_db']:.6f} dB")
    print(f"pixels scored: {result['pixels_scored']}")
    print(f"wrote {out_path}")
    print(REFERENCE_LIMITATION)
    return report


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--after", default="experiments/after.tif")
    parser.add_argument("--reference", default="experiments/reference_mask.tif")
    parser.add_argument("--out", default="experiments/event_metrics.json")
    parser.add_argument(
        "--cnn",
        default=None,
        help="optional same-grid 0/1 CNN water-mask GeoTIFF to score",
    )
    parser.add_argument("--after-date", default="2026-02-08")
    args = parser.parse_args(argv)
    score_event(args.after, args.reference, args.out, args.after_date, args.cnn)


if __name__ == "__main__":
    main()
