import numpy as np
import rasterio
from rasterio.transform import from_origin
import torch

import experiments.predict_water as predict_water
from experiments.predict_water import (
    mask_from_probabilities,
    prepare_radar_scene,
    predict_water_array,
    write_water_geotiff,
)


def test_prepare_radar_scene_converts_linear_and_tracks_invalid_pixels():
    scene = np.stack(
        [
            np.full((8, 8), 0.1, dtype=np.float32),
            np.full((8, 8), 0.01, dtype=np.float32),
        ]
    )
    scene[0, 0, 0] = np.nan

    db, valid, unit = prepare_radar_scene(scene)

    assert unit == "linear"
    assert db.shape == scene.shape
    assert not valid[0, 0]
    assert not np.isfinite(db[0, 0, 0])
    assert np.nanmin(db) < 0


def test_prediction_mask_applies_default_small_object_cleanup_and_validity():
    probabilities = np.zeros((12, 12), dtype=np.float32)
    probabilities[1:4, 1:4] = 0.9
    probabilities[6:11, 6:11] = 0.9
    valid = np.ones((12, 12), dtype=bool)
    valid[8, 8] = False

    mask = mask_from_probabilities(probabilities, valid)

    assert not mask[2, 2]
    assert mask[6, 6]
    assert not mask[8, 8]
    assert mask.dtype == np.bool_


def test_write_water_geotiff_preserves_source_grid(tmp_path):
    transform = from_origin(-6.0, 35.0, 0.01, 0.01)
    profile = {
        "driver": "GTiff",
        "height": 4,
        "width": 5,
        "count": 2,
        "dtype": "float32",
        "crs": "EPSG:4326",
        "transform": transform,
    }
    mask = np.zeros((4, 5), dtype=bool)
    mask[1:3, 2:4] = True
    out_path = tmp_path / "water.tif"

    write_water_geotiff(out_path, mask, profile)

    with rasterio.open(out_path) as result:
        assert result.shape == (4, 5)
        assert result.crs.to_string() == "EPSG:4326"
        assert result.transform == transform
        assert result.count == 1
        assert result.dtypes == ("uint8",)
        assert set(np.unique(result.read(1))) == {0, 1}
        assert "reference_limitation" in result.tags()


def test_predict_geotiff_preserves_grid_and_reports_water_count(tmp_path, monkeypatch, capsys):
    transform = from_origin(-6.0, 35.0, 0.01, 0.01)
    scene = np.full((2, 6, 6), -10.0, dtype=np.float32)
    scene[:, 0, 0] = np.nan
    source_path = tmp_path / "after.tif"
    output_path = tmp_path / "water.tif"
    with rasterio.open(
        source_path,
        "w",
        driver="GTiff",
        height=6,
        width=6,
        count=2,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
        nodata=np.nan,
    ) as source:
        source.write(scene)

    probabilities = np.zeros((6, 6), dtype=np.float32)
    probabilities[:5, :5] = 0.9
    monkeypatch.setattr(predict_water, "load_model", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(
        predict_water,
        "predict_scene",
        lambda *_args, **_kwargs: probabilities,
    )

    water_pixels = predict_water.predict_geotiff(
        source_path, "fake-checkpoint.pt", output_path, input_unit="db"
    )

    assert water_pixels == 24
    assert "water_pixels=24" in capsys.readouterr().out
    with rasterio.open(output_path) as result:
        assert result.shape == (6, 6)
        assert result.crs.to_string() == "EPSG:4326"
        assert result.transform == transform
        assert int(result.read(1).sum()) == 24


def test_random_tiny_model_runs_through_repo_sliding_window():
    model = torch.nn.Conv2d(2, 1, kernel_size=1)
    scene = np.random.default_rng(4).normal(-15.0, 3.0, (2, 12, 10)).astype(
        np.float32
    )

    mask, db, valid, unit = predict_water_array(scene, model, input_unit="db")

    assert mask.shape == (12, 10)
    assert db.shape == scene.shape
    assert valid.all()
    assert unit == "db"
