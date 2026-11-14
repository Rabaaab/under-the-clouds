import numpy as np
import pytest

from utc.baseline import otsu_threshold, water_mask_threshold
from utc.change import flood_change
from utc.metrics import evaluate, scores_from_counts
from utc.postprocess import clean_change, mask_steep, remove_small_objects, slope_from_dem
from utc.preprocess import extract_chips, lee_filter, normalize_db, tile_positions, to_db


def test_to_db_known_values():
    assert to_db(np.array([1.0]))[0] == pytest.approx(0.0)
    assert to_db(np.array([0.1]))[0] == pytest.approx(-10.0, abs=1e-4)


def test_lee_filter_keeps_nan_and_reduces_noise():
    rng = np.random.default_rng(0)
    img = rng.gamma(4, 0.25, size=(64, 64)).astype(np.float32)
    img[5, 5] = np.nan
    out = lee_filter(img)
    assert np.isnan(out[5, 5])
    assert np.nanstd(out) < np.nanstd(img)


def test_normalize_db_range():
    out = normalize_db(np.array([-60.0, -50.0, -24.5, 1.0, 10.0, np.nan]))
    assert out.min() >= 0.0 and out.max() <= 1.0
    assert out[0] == 0.0 and out[3] == 1.0
    assert out[2] == pytest.approx(0.5)
    assert out[5] == 1.0  # NaN becomes "bright" (not water)


def test_tiles_cover_image_including_edges():
    pos = tile_positions(300, 300, 256, 256)
    covered = np.zeros((300, 300), bool)
    for y, x in pos:
        covered[y : y + 256, x : x + 256] = True
    assert covered.all()


def test_extract_chips_shapes_and_small_image_error():
    arr = np.zeros((2, 300, 300), np.float32)
    chips = list(extract_chips(arr, 256, 256))
    assert all(c.shape == (2, 256, 256) for _, _, c in chips)
    with pytest.raises(ValueError):
        list(extract_chips(np.zeros((2, 100, 100)), 256, 256))


def test_otsu_separates_two_modes():
    rng = np.random.default_rng(1)
    vals = np.concatenate([rng.normal(-22, 2, 5000), rng.normal(-10, 2, 5000)])
    t = otsu_threshold(vals)
    assert -19 < t < -13


def test_water_mask_uses_fallback_when_otsu_is_insane():
    rng = np.random.default_rng(2)
    img = rng.normal(5, 0.2, (50, 50)).astype(np.float32)  # no sensible dB range
    with pytest.warns(UserWarning):
        mask, thr = water_mask_threshold(img)
    assert thr == -18.0 and not mask.any()


def test_flood_change_logic():
    before = np.array([[1, 1, 0, 0]], bool)
    after = np.array([[1, 0, 1, 0]], bool)
    c = flood_change(before, after)
    assert c["new_water"].tolist() == [[False, False, True, False]]
    assert c["receded"].tolist() == [[False, True, False, False]]
    assert c["permanent_water"].tolist() == [[True, False, False, False]]


def test_metrics_match_hand_calculation():
    # 100 true water pixels; model says 90, of which 80 are right (the Darija doc example)
    truth = np.zeros(1000, bool)
    truth[:100] = True
    pred = np.zeros(1000, bool)
    pred[:80] = True
    pred[500:510] = True
    s = evaluate(pred, truth)
    assert s["precision"] == pytest.approx(80 / 90)
    assert s["recall"] == pytest.approx(0.8)
    assert s["iou"] == pytest.approx(80 / 110)
    assert s["f1"] == pytest.approx(2 * 80 / (2 * 80 + 10 + 20))


def test_metrics_empty_vs_empty_is_perfect():
    assert scores_from_counts({"tp": 0, "fp": 0, "fn": 0, "tn": 10})["iou"] == 1.0


def test_remove_small_objects():
    m = np.zeros((20, 20), bool)
    m[0:2, 0:2] = True  # 4 px
    m[10:15, 10:15] = True  # 25 px
    out = remove_small_objects(m, min_size=10)
    assert not out[0, 0] and out[12, 12]


def test_slope_and_steep_mask():
    x = np.arange(50, dtype=np.float32)
    dem = np.tile(x * 10.0, (50, 1))  # rises 10 m per 10 m pixel -> 45 degrees
    slope = slope_from_dem(dem, 10.0)
    assert slope[25, 25] == pytest.approx(45.0, abs=1.0)
    mask = np.ones((50, 50), bool)
    assert not mask_steep(mask, slope, 10.0).any()
    assert clean_change(mask, min_size=1, slope_deg=np.zeros((50, 50)), max_slope_deg=10).all()
