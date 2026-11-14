import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds

from utc.prepare import make_grid, prepare_pair
from utc.event import main as event_main


def write_utm(path, value, nodata_block=False, size=200):
    """A fake HyP3-style product: one band, UTM zone 30N, 30 m pixels, 0 = no data."""
    tr = from_origin(300000, 3880000, 30, 30)
    arr = np.full((size, size), value, dtype=np.float32)
    if nodata_block:
        arr[:, :50] = 0.0
    with rasterio.open(path, "w", driver="GTiff", height=size, width=size, count=1, dtype="float32",
                       crs="EPSG:32630", transform=tr, nodata=0.0) as dst:
        dst.write(arr, 1)
    return rasterio.coords.BoundingBox(300000, 3880000 - size * 30, 300000 + size * 30, 3880000)


def lonlat_bbox(b):
    return transform_bounds("EPSG:32630", "EPSG:4326", b.left, b.bottom, b.right, b.top)


def test_make_grid_rejects_bad_or_huge_boxes():
    with pytest.raises(ValueError):
        make_grid((1, 1, 0, 2), 30)
    with pytest.raises(ValueError):
        make_grid((-10, 30, 0, 40), 10)


def test_prepare_pair_shared_grid_nodata_and_units(tmp_path):
    b = write_utm(tmp_path / "b_vv.tif", 0.10, nodata_block=True)
    write_utm(tmp_path / "b_vh.tif", 0.02)
    write_utm(tmp_path / "a_vv.tif", 0.30)   # amplitude values
    write_utm(tmp_path / "a_vh.tif", 0.10)
    west, south, east, north = lonlat_bbox(b)
    inner = (west + 0.01, south + 0.01, east - 0.01, north - 0.01)

    rep = prepare_pair(tmp_path / "b_vv.tif", tmp_path / "b_vh.tif", tmp_path / "b_vv.tif", tmp_path / "b_vh.tif",
                       inner, tmp_path / "out_power", res_m=60, unit="power")
    assert rep["unit_written"] == "power" and rep["before_valid_fraction"] < 1.0  # the no-data block shows up
    with rasterio.open(tmp_path / "out_power" / "before.tif") as s, rasterio.open(tmp_path / "out_power" / "after.tif") as t:
        assert s.crs.to_string() == "EPSG:4326" and s.count == 2
        assert s.transform == t.transform and s.shape == t.shape  # same grid
        vv = s.read(1)
        assert np.isnan(vv).any()
        assert np.nanmean(vv) == pytest.approx(0.10, abs=0.01)

    prepare_pair(tmp_path / "a_vv.tif", tmp_path / "a_vh.tif", tmp_path / "a_vv.tif", tmp_path / "a_vh.tif",
                 inner, tmp_path / "out_amp", res_m=60, unit="amplitude")
    with rasterio.open(tmp_path / "out_amp" / "after.tif") as s:
        assert np.nanmean(s.read(1)) == pytest.approx(0.09, abs=0.005)  # 0.30 squared
        assert np.nanmean(s.read(2)) == pytest.approx(0.01, abs=0.002)


def test_prepared_scenes_feed_run_event(tmp_path):
    b = write_utm(tmp_path / "v.tif", 0.10)
    write_utm(tmp_path / "h.tif", 0.02)
    west, south, east, north = lonlat_bbox(b)
    inner = (west + 0.005, south + 0.005, east - 0.005, north - 0.005)
    prepare_pair(tmp_path / "v.tif", tmp_path / "h.tif", tmp_path / "v.tif", tmp_path / "h.tif",
                 inner, tmp_path / "scene", res_m=60)
    event_main(["--before", str(tmp_path / "scene" / "before.tif"), "--after", str(tmp_path / "scene" / "after.tif"),
                "--linear", "--event-name", "prep test", "--out", str(tmp_path / "web")])
    assert (tmp_path / "web" / "meta.json").exists()
