"""Predict a water mask for one two-band Sentinel-1 GeoTIFF."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import rasterio

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for import_path in (PROJECT_ROOT, PROJECT_ROOT / "src"):
    if str(import_path) not in sys.path:
        sys.path.insert(0, str(import_path))

from utc.infer import predict_scene
from utc.model import load_model
from utc.postprocess import clean_change
from utc.preprocess import normalize_db, lee_filter, to_db

REFERENCE_LIMITATION = (
    "Zenodo labels are semi-automatic HSBA+Otsu masks, not expert ground truth; "
    "they may favour Otsu, cover only part of the scene, have unknown patch dates, "
    "and represent water, not a change map."
)


def prepare_radar_scene(
    scene: np.ndarray, input_unit: str = "auto"
) -> tuple[np.ndarray, np.ndarray, str]:
    """Return dB bands, a joint validity mask, and the input unit used."""
    data = np.asarray(scene, dtype=np.float32)
    if data.ndim != 3 or data.shape[0] < 2:
        raise ValueError("expected at least two bands with shape (bands, height, width)")
    data = data[:2].copy()
    valid = np.isfinite(data).all(axis=0)

    if input_unit not in {"auto", "linear", "db"}:
        raise ValueError("input_unit must be 'auto', 'linear', or 'db'")
    if input_unit == "auto":
        finite = data[np.isfinite(data)]
        unit = "linear" if finite.size and np.all(finite >= 0) else "db"
    else:
        unit = input_unit

    if unit == "linear":
        db = np.stack([to_db(lee_filter(band)) for band in data])
    else:
        db = data
    return db.astype(np.float32, copy=False), valid, unit


def mask_from_probabilities(
    probabilities: np.ndarray,
    valid: np.ndarray,
    min_size: int = 20,
) -> np.ndarray:
    """Threshold and apply run_event's default small-component cleanup."""
    probabilities = np.asarray(probabilities)
    valid = np.asarray(valid, dtype=bool)
    if probabilities.shape != valid.shape:
        raise ValueError(
            f"probability and validity shapes differ: {probabilities.shape} vs {valid.shape}"
        )
    raw_mask = (probabilities > 0.5) & np.isfinite(probabilities) & valid
    return clean_change(raw_mask, min_size=min_size)


def predict_water_array(
    scene: np.ndarray,
    model,
    device: str = "cpu",
    input_unit: str = "auto",
    min_size: int = 20,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, str]:
    """Predict one water mask using utc preprocessing and sliding-window inference."""
    db, valid, unit = prepare_radar_scene(scene, input_unit)
    normalized = normalize_db(db)
    normalized[:, ~valid] = 1.0
    probabilities = predict_scene(model, normalized, device=device)
    mask = mask_from_probabilities(probabilities, valid, min_size=min_size)
    return mask, db, valid, unit


def write_water_geotiff(
    out_path: str | Path, mask: np.ndarray, source_profile: dict
) -> None:
    """Write a one-band uint8 mask using the source GeoTIFF's grid."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    profile = source_profile.copy()
    profile.update(driver="GTiff", count=1, dtype="uint8", nodata=None)
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(np.asarray(mask, dtype=np.uint8), 1)
        dst.update_tags(
            water_mask="1=water, 0=not water; this is not a water-change map",
            reference_limitation=REFERENCE_LIMITATION,
            cleanup="remove connected components smaller than 20 pixels; coastal cleanup off",
        )


def predict_geotiff(
    tif_path: str | Path,
    checkpoint: str | Path,
    out_path: str | Path,
    device: str = "cpu",
    input_unit: str = "auto",
) -> int:
    """Run prediction from a GeoTIFF and return the number of water pixels."""
    with rasterio.open(tif_path) as src:
        if src.count < 2:
            raise ValueError(f"{tif_path} must contain VV and VH bands")
        scene = src.read().astype(np.float32)
        if src.nodata is not None:
            if np.isnan(src.nodata):
                scene[~np.isfinite(scene)] = np.nan
            else:
                scene[scene == src.nodata] = np.nan
        profile = src.profile.copy()

    model = load_model(str(checkpoint), device=device)
    mask, _, _, unit = predict_water_array(
        scene, model, device=device, input_unit=input_unit
    )
    write_water_geotiff(out_path, mask, profile)
    count = int(mask.sum())
    print(
        f"wrote {out_path}; water_pixels={count}; input_unit={unit}; "
        "cleanup=min_size_20, coastal_cleanup=off"
    )
    print(f"Reference limitation: {REFERENCE_LIMITATION}")
    return count


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tif", required=True, help="Two-band VV/VH GeoTIFF")
    parser.add_argument("--checkpoint", required=True, help="Trained U-Net checkpoint")
    parser.add_argument("--out", required=True, help="Output one-band water GeoTIFF")
    parser.add_argument(
        "--unit",
        choices=("auto", "linear", "db"),
        default="auto",
        help="Input units; auto treats nonnegative data as linear power (default: auto)",
    )
    parser.add_argument("--device", default="cpu")
    args = parser.parse_args(argv)
    predict_geotiff(args.tif, args.checkpoint, args.out, args.device, args.unit)


if __name__ == "__main__":
    main()
