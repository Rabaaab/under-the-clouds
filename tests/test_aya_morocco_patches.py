import datetime as dt
import csv
import json

import numpy as np
import rasterio
import torch
from rasterio.transform import from_origin

from experiments.eval_morocco_patches import (
    evaluate_zone,
    is_in_event_window,
    main as patches_main,
    parse_dates,
    score_patch,
)


class ConstantWaterModel(torch.nn.Module):
    def forward(self, batch):
        return torch.full(
            (batch.shape[0], 1, batch.shape[2], batch.shape[3]),
            10.0,
            device=batch.device,
        )


def test_parse_dates_reads_metadata_date_intervals():
    dates = parse_dates("2026-01-27_to_2026-02-05")

    assert dates == [dt.date(2026, 1, 27), dt.date(2026, 2, 5)]
    assert not parse_dates("date unavailable")


def test_event_window_accepts_dates_near_either_scene():
    assert is_in_event_window("2026-01-27_to_2026-02-05")
    assert is_in_event_window("2026-01-31_2026-02-08")
    assert not is_in_event_window("2025-12-01")
    assert not is_in_event_window(None)


def test_score_patch_uses_same_valid_pixels_for_both_methods():
    scene = np.stack(
        [
            np.full((16, 16), -20.0, dtype=np.float32),
            np.full((16, 16), -25.0, dtype=np.float32),
        ]
    )
    scene[:, 0, 0] = np.nan
    label = np.zeros((16, 16), dtype=np.float32)
    label[4:12, 4:12] = 1
    label[1, 1] = 255

    result = score_patch(scene, label, ConstantWaterModel())

    assert result["input_unit"] == "db"
    assert (
        result["cnn"]["tp"]
        + result["cnn"]["fp"]
        + result["cnn"]["fn"]
        + result["cnn"]["tn"]
        == 254
    )
    assert result["cnn"]["fn"] == 0
    assert (
        result["otsu"]["tp"]
        + result["otsu"]["fp"]
        + result["otsu"]["fn"]
        + result["otsu"]["tn"]
        == 254
    )
    assert result["valid_pixels"] == 254


def test_evaluate_fake_patches_pools_zone_metrics(tmp_path):
    zone_dir = tmp_path / "Zone1_KsarElKebir"
    image_dir = zone_dir / "patches" / "images"
    mask_dir = zone_dir / "patches" / "masks"
    image_dir.mkdir(parents=True)
    mask_dir.mkdir(parents=True)
    image_rel = "Zone1_KsarElKebir/patches/images/patch.tif"
    mask_rel = "Zone1_KsarElKebir/patches/masks/patch.tif"
    image_path = tmp_path / image_rel
    mask_path = tmp_path / mask_rel
    transform = from_origin(-6.0, 35.0, 0.01, 0.01)
    image = np.stack(
        [
            np.full((16, 16), -20.0, dtype=np.float32),
            np.full((16, 16), -25.0, dtype=np.float32),
        ]
    )
    label = np.zeros((16, 16), dtype=np.uint8)
    label[4:12, 4:12] = 1
    for path, data, count in (
        (image_path, image, 2),
        (mask_path, label[None], 1),
    ):
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=16,
            width=16,
            count=count,
            dtype=data.dtype,
            crs="EPSG:4326",
            transform=transform,
        ) as dst:
            dst.write(data)
    with (zone_dir / "metadata_zone1.csv").open(
        "w", newline="", encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["acquisition_date", "image_path", "mask_path", "patch_id"],
        )
        writer.writeheader()
        writer.writerow(
            {
                "acquisition_date": "2026-02-02",
                "image_path": image_rel,
                "mask_path": mask_rel,
                "patch_id": "fake_patch",
            }
        )
        writer.writerow(
            {
                "acquisition_date": "",
                "image_path": "no-date.tif",
                "mask_path": "no-date-mask.tif",
                "patch_id": "no-date",
            }
        )

    result = evaluate_zone(tmp_path, 1, ConstantWaterModel())

    assert result["patches_available"] == 2
    assert result["patches_scored"] == 1
    assert result["patches_without_date"] == 1
    assert result["cnn"]["counts"]["tp"] == 64


def test_missing_real_dataset_writes_not_run_report_without_checkpoint(
    tmp_path, capsys
):
    out = tmp_path / "metrics.json"

    patches_main(
        [
            "--data-root",
            str(tmp_path / "missing"),
            "--checkpoint",
            str(tmp_path / "unavailable.pt"),
            "--out",
            str(out),
        ]
    )

    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["status"] == "not run on real data"
    assert "Otsu" in report["otsu_circularity"]
    assert "semi-automatic" in report["reference_limitation"]
    assert "not run on real data" in capsys.readouterr().out
