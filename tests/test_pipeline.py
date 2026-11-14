import json

import numpy as np
import pytest
import torch

from utc.dataset import ChipDataset, list_chip_files, save_chips, split_files
from utc.export_web import export_web
from utc.infer import predict_scene
from utc.io import mask_to_gdf, read_geotiff, write_geotiff
from utc.model import bce_dice_loss, build_unet, load_model, save_checkpoint
from utc.pipeline import run_pipeline
from utc.preprocess import lee_filter, normalize_db, to_db
from utc.synthetic import make_synthetic_event


@pytest.fixture(scope="module")
def event():
    return make_synthetic_event(size=256, seed=3)


def to_db_pair(scene):
    return np.stack([to_db(lee_filter(b)) for b in scene])


def test_synthetic_event_has_expected_truth(event):
    assert event["truth_new_water"].sum() > 5000
    assert not (event["truth_new_water"] & event["water_before"]).any()


def test_geotiff_roundtrip_and_polygons(tmp_path, event):
    arr = to_db_pair(event["before"])
    p = tmp_path / "x.tif"
    write_geotiff(p, arr, event["transform"], event["crs"])
    back, tr, crs = read_geotiff(p)
    assert back.shape == arr.shape and np.allclose(back, arr)
    gdf = mask_to_gdf(event["truth_new_water"], tr, crs)
    assert len(gdf) >= 1 and gdf.geometry.is_valid.all()


def test_baseline_pipeline_finds_flood_and_impact(event):
    result = run_pipeline(
        to_db_pair(event["before"]),
        to_db_pair(event["after"]),
        event["transform"],
        event["crs"],
        roads=event["roads"],
        villages=event["villages"],
        truth_new_water=event["truth_new_water"],
    )
    assert result["primary_method"] == "baseline"
    assert result["metrics"]["baseline"]["iou"] > 0.8  # synthetic scene is easy; this only checks the code works
    s = result["summary"]
    assert s["flooded_area_km2"] > 0
    names = " ".join(result["affected_roads"]["name"])
    assert "Road 1" in names and "Road 2" in names and "Road 4" in names
    assert "Road 3" not in names
    assert "Village A (near flood)" in s["village_names"] and "Village C (in lake)" in s["village_names"]
    assert "Village B (far)" not in s["village_names"]
    assert 0 < s["road_km_affected"] < s["road_km_total"]


def test_loss_ignores_invalid_pixels():
    logits = torch.zeros(1, 1, 4, 4)
    target = torch.zeros(1, 1, 4, 4)
    valid = torch.ones(1, 1, 4, 4)
    base = bce_dice_loss(logits, target, valid)
    target[0, 0, 0, 0] = 1.0
    valid[0, 0, 0, 0] = 0.0  # the only positive pixel is ignored
    assert bce_dice_loss(logits, target, valid).item() == pytest.approx(base.item(), abs=1e-5)


def test_unet_forward_shape():
    model = build_unet("resnet34", in_channels=2, pretrained=False)
    out = model(torch.zeros(2, 2, 64, 64))
    assert out.shape == (2, 1, 64, 64)


def test_sliding_window_prediction_shape():
    model = build_unet("resnet34", in_channels=2, pretrained=False)
    scene = np.random.rand(2, 100, 90).astype(np.float32)  # smaller than the tile -> padding path
    prob = predict_scene(model, scene, size=64, overlap=16)
    assert prob.shape == (100, 90) and prob.min() >= 0 and prob.max() <= 1


def test_training_smoke_and_cnn_pipeline(tmp_path, event):
    """Tiny training run on synthetic chips. Checks the plumbing only; the model is not expected to be good."""
    from utc.train import fit

    x = normalize_db(to_db_pair(event["after"]))
    y = event["water_after"].astype(np.int8)
    n = save_chips(x, y, tmp_path / "chips", "synth", size=128, stride=128)
    assert n == 4
    train_f, val_f = split_files(list_chip_files(tmp_path / "chips"), val_fraction=0.25)
    item = ChipDataset(train_f, augment=True)[0]
    assert item[0].shape == (2, 128, 128) and item[1].shape == (1, 128, 128)

    ckpt = tmp_path / "m.pt"
    history, best = fit(train_f, val_f, epochs=1, batch_size=2, device="cpu", out_path=ckpt, pretrained=False, log=lambda *_: None)
    assert ckpt.exists() and len(history) == 1

    load_model(ckpt)  # loads without internet
    result = run_pipeline(
        to_db_pair(event["before"]),
        to_db_pair(event["after"]),
        event["transform"],
        event["crs"],
        roads=event["roads"],
        villages=event["villages"],
        checkpoint=str(ckpt),
        truth_new_water=event["truth_new_water"],
    )
    assert result["primary_method"] == "cnn" and set(result["metrics"]) == {"baseline", "cnn"}


def test_random_checkpoint_roundtrip(tmp_path):
    model = build_unet("resnet34", 2, pretrained=False)
    save_checkpoint(tmp_path / "r.pt", model, "resnet34", 2)
    loaded = load_model(tmp_path / "r.pt")
    x = torch.rand(1, 2, 64, 64)
    assert torch.allclose(model.eval()(x), loaded(x), atol=1e-5)


def test_export_web_writes_expected_files(tmp_path, event):
    before, after = to_db_pair(event["before"]), to_db_pair(event["after"])
    result = run_pipeline(before, after, event["transform"], event["crs"], event["roads"], event["villages"], truth_new_water=event["truth_new_water"])
    meta_path = export_web(tmp_path, before, after, result, event["transform"], event["crs"], {"synthetic": True})
    for f in ("before.png", "after.png", "change.png", "flood.geojson", "roads_affected.geojson", "villages_near.geojson", "meta.json"):
        assert (tmp_path / f).exists(), f
    meta = json.loads(meta_path.read_text())
    assert meta["synthetic"] is True and len(meta["bounds"]) == 2
    with pytest.raises(ValueError):
        export_web(tmp_path, before, after, result, event["transform"], "EPSG:32629")
