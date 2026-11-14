import json

import numpy as np
import rasterio
from rasterio.transform import from_origin

from experiments.score_event import score_event, score_event_arrays


def test_score_event_arrays_converts_linear_and_masks_no_reference():
    vv = np.array(
        [
            [0.01, 0.01, 0.1, 0.1],
            [0.01, 0.01, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.1],
        ],
        dtype=np.float32,
    )
    reference = np.zeros((4, 4), dtype=np.uint8)
    reference[:2, :2] = 1
    reference[3, 3] = 255

    result = score_event_arrays(vv, reference)

    assert result["unit_detected"] == "linear_power"
    assert result["pixels_scored"] == 15
    assert result["baseline"]["tp"] == 4
    assert result["baseline"]["fp"] == 0
    assert result["baseline"]["fn"] == 0
    assert result["baseline"]["iou"] == 1.0
    assert result["baseline"]["f1"] == 1.0


def test_score_event_writes_null_cnn_and_real_grid_metrics(tmp_path, capsys):
    transform = from_origin(-6.0, 35.0, 0.01, 0.01)
    vv = np.array([[0.01, 0.01, 0.1, 0.1]] * 4, dtype=np.float32)
    reference = np.array(
        [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 255], [0, 0, 0, 0]],
        dtype=np.uint8,
    )
    after_path = tmp_path / "after.tif"
    ref_path = tmp_path / "reference.tif"
    out_path = tmp_path / "event_metrics.json"
    for path, data, dtype, nodata in (
        (after_path, vv[None], "float32", np.nan),
        (ref_path, reference[None], "uint8", 255),
    ):
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=4,
            width=4,
            count=1,
            dtype=dtype,
            crs="EPSG:4326",
            transform=transform,
            nodata=nodata,
        ) as dst:
            dst.write(data)

    report = score_event(after_path, ref_path, out_path)
    persisted = json.loads(out_path.read_text(encoding="utf-8"))

    assert report["cnn"] is None
    assert "CNN not scored locally" in report["cnn_note"]
    assert persisted["cnn"] is None
    assert set(("iou", "f1", "precision", "recall", "tp", "fp", "fn")) <= set(
        persisted["baseline"]
    )
    assert "semi-automatic" in persisted["reference_limitation"]
    assert "Method  IoU" in capsys.readouterr().out


def test_score_event_scores_same_grid_cnn_prediction(tmp_path):
    transform = from_origin(-6.0, 35.0, 0.01, 0.01)
    vv = np.array([[0.01, 0.01, 0.1, 0.1]] * 4, dtype=np.float32)
    reference = np.array(
        [[1, 1, 0, 0], [1, 1, 0, 0], [0, 0, 0, 255], [0, 0, 0, 0]],
        dtype=np.uint8,
    )
    prediction = reference.copy()
    prediction[2, 3] = 0
    after_path = tmp_path / "after.tif"
    ref_path = tmp_path / "reference.tif"
    cnn_path = tmp_path / "cnn.tif"
    out_path = tmp_path / "event_metrics.json"
    for path, data, dtype, nodata in (
        (after_path, vv[None], "float32", np.nan),
        (ref_path, reference[None], "uint8", 255),
        (cnn_path, prediction[None], "uint8", None),
    ):
        with rasterio.open(
            path,
            "w",
            driver="GTiff",
            height=4,
            width=4,
            count=1,
            dtype=dtype,
            crs="EPSG:4326",
            transform=transform,
            nodata=nodata,
        ) as dst:
            dst.write(data)

    report = score_event(after_path, ref_path, out_path, cnn_path=cnn_path)

    assert report["cnn"]["iou"] == 1.0
    assert report["cnn"]["f1"] == 1.0
    assert "CNN scored from" in report["cnn_note"]
