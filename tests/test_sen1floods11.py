import numpy as np
import pytest

from utc.dataset import ChipDataset, list_chip_files
from utc.model import build_unet, save_checkpoint
from utc.s1f11_cli import main as cli_main
from utc.sen1floods11 import Paths, SPLIT_FILES, evaluate_split, load_scene, prepare_chips, read_split_csv
from utc.io import write_geotiff
from utc.synthetic import make_synthetic_event
from utc.preprocess import to_db


def build_fake_dataset(root, n_train=3, n_valid=1, n_test=1, size=256, n_bolivia=0):
    """Create files with the same names, bands, units and label values as the real Sen1Floods11 hand-labelled set."""
    paths = Paths.from_root(root)
    for d in (paths.s1_dir, paths.label_dir, paths.splits_dir):
        d.mkdir(parents=True, exist_ok=True)
    plan = {"train": n_train, "valid": n_valid, "test": n_test}
    if n_bolivia:
        plan["bolivia"] = n_bolivia
    k = 0
    for split, n in plan.items():
        rows = []
        for _ in range(n):
            ev = make_synthetic_event(size=size, seed=100 + k)
            db = np.stack([to_db(b) for b in ev["after"]]).astype(np.float32)
            db[:, :3, :3] = np.nan  # a few no-data pixels
            lab = ev["water_after"].astype(np.int16)
            lab[:3, :3] = -1
            name = f"Fake_{k}"
            write_geotiff(paths.s1_dir / f"{name}_S1Hand.tif", db, ev["transform"], ev["crs"])
            write_geotiff(paths.label_dir / f"{name}_LabelHand.tif", lab, ev["transform"], ev["crs"])
            rows.append(f"{name}_S1Hand.tif,{name}_LabelHand.tif")
            k += 1
        (paths.splits_dir / SPLIT_FILES[split]).write_text("\n".join(rows) + "\n")
    return paths


def test_read_split_csv_headerless_two_columns(tmp_path):
    p = tmp_path / "s.csv"
    p.write_text("A_S1Hand.tif,A_LabelHand.tif\n\nB_S1Hand.tif,B_LabelHand.tif\n")
    assert read_split_csv(p) == [("A_S1Hand.tif", "A_LabelHand.tif"), ("B_S1Hand.tif", "B_LabelHand.tif")]


def test_load_scene_marks_nodata_as_ignore(tmp_path):
    paths = build_fake_dataset(tmp_path)
    s1, lab = read_split_csv(paths.splits_dir / SPLIT_FILES["train"])[0]
    db, y = load_scene(paths.s1_dir / s1, paths.label_dir / lab)
    assert db.shape == (2, 256, 256) and y.shape == (256, 256)
    assert set(np.unique(y)) <= {-1, 0, 1} and (y[:3, :3] == -1).all()


def test_prepare_chips_makes_one_folder_per_split(tmp_path):
    paths = build_fake_dataset(tmp_path / "raw")
    report = prepare_chips(paths, tmp_path / "chips", size=128)
    assert report["train"] == {"scenes": 3, "chips": 12, "skipped": 0}
    assert report["valid"]["chips"] == 4 and report["test"]["chips"] == 4
    files = list_chip_files(tmp_path / "chips" / "train")
    x, target, valid = ChipDataset(files)[0]
    assert x.shape == (2, 128, 128) and 0.0 <= float(x.min()) and float(x.max()) <= 1.0
    assert set(np.unique(target.numpy())) <= {0.0, 1.0}


def test_evaluate_baseline_and_cnn_run_on_same_scenes(tmp_path):
    paths = build_fake_dataset(tmp_path / "raw")
    res = evaluate_split(paths, "test")
    assert res["n_scenes"] == 1
    assert set(res) == {
        "baseline_vv", "baseline_vh", "tuned_vv", "tuned_vh", "n_scenes", "tuned_thresholds_db", "naive_baseline_fallback_scenes",
    }
    assert res["baseline_vv"]["iou"] > 0.8  # easy synthetic scene; checks the plumbing, not real accuracy
    assert res["tuned_vv"]["iou"] > 0.8 and -22 < res["tuned_thresholds_db"]["vv"] < -10

    model = build_unet("resnet34", 2, pretrained=False)
    save_checkpoint(tmp_path / "m.pt", model, "resnet34", 2)
    res = evaluate_split(paths, "test", checkpoint=str(tmp_path / "m.pt"))
    assert "cnn" in res and 0.0 <= res["cnn"]["iou"] <= 1.0


def test_evaluate_survives_a_scene_with_no_valid_pixels(tmp_path):
    """Regression: on the real test split one scene is all no-data, which used to crash with 'no finite values'."""
    paths = build_fake_dataset(tmp_path / "raw", n_test=2)
    s1_name, label_name = read_split_csv(paths.splits_dir / SPLIT_FILES["test"])[0]
    ev = make_synthetic_event(size=256, seed=999)
    write_geotiff(paths.s1_dir / s1_name, np.full((2, 256, 256), np.nan, dtype=np.float32), ev["transform"], ev["crs"])
    write_geotiff(paths.label_dir / label_name, np.full((256, 256), -1, dtype=np.int16), ev["transform"], ev["crs"])

    model = build_unet("resnet34", 2, pretrained=False)
    save_checkpoint(tmp_path / "m.pt", model, "resnet34", 2)
    res = evaluate_split(paths, "test", checkpoint=str(tmp_path / "m.pt"))
    assert res["n_scenes"] == 2
    assert res["naive_baseline_fallback_scenes"]["vv"] >= 1  # the empty scene counts as a fallback
    assert 0.0 <= res["baseline_vv"]["iou"] <= 1.0


def test_out_of_event_bolivia_split_can_be_evaluated(tmp_path):
    paths = build_fake_dataset(tmp_path / "raw", n_bolivia=2)
    res = evaluate_split(paths, "bolivia")
    assert res["n_scenes"] == 2 and "tuned_vh" in res  # thresholds are still fitted on the training split


def test_water_mask_threshold_handles_all_nan():
    from utc.baseline import water_mask_threshold

    mask, thr = water_mask_threshold(np.full((8, 8), np.nan, dtype=np.float32))
    assert not mask.any() and thr == -18.0


def test_cli_prepare_and_evaluate(tmp_path, capsys):
    build_fake_dataset(tmp_path / "raw")
    cli_main(["prepare", "--root", str(tmp_path / "raw"), "--out", str(tmp_path / "chips"), "--size", "128"])
    assert (tmp_path / "chips" / "train").is_dir()
    out = tmp_path / "eval.json"
    cli_main(["evaluate", "--root", str(tmp_path / "raw"), "--split", "valid", "--out", str(out)])
    assert out.exists()


def test_train_cli_with_separate_train_and_val_dirs(tmp_path):
    from utc.train import main as train_main

    paths = build_fake_dataset(tmp_path / "raw")
    prepare_chips(paths, tmp_path / "chips", size=128)
    train_main(
        [
            "--train-dir", str(tmp_path / "chips" / "train"),
            "--val-dir", str(tmp_path / "chips" / "valid"),
            "--epochs", "1", "--batch-size", "4", "--no-pretrained",
            "--out", str(tmp_path / "unet.pt"),
        ]
    )
    assert (tmp_path / "unet.pt").exists()
    with pytest.raises(SystemExit):
        train_main([])
