import json

import numpy as np

from utc.demo import to_db_pair
from utc.event import main as event_main
from utc.io import write_geotiff
from utc.synthetic import make_synthetic_event


def test_event_cli_on_synthetic_geotiffs(tmp_path):
    ev = make_synthetic_event(size=256, seed=5)
    for name in ("before", "after"):
        write_geotiff(tmp_path / f"{name}.tif", ev[name].astype(np.float32), ev["transform"], ev["crs"])
    write_geotiff(tmp_path / "truth.tif", ev["truth_new_water"].astype(np.float32), ev["transform"], ev["crs"])
    ev["roads"].to_file(tmp_path / "roads.geojson", driver="GeoJSON")
    ev["villages"].to_file(tmp_path / "villages.geojson", driver="GeoJSON")

    out = tmp_path / "web"
    event_main(
        [
            "--before", str(tmp_path / "before.tif"),
            "--after", str(tmp_path / "after.tif"),
            "--linear",
            "--roads", str(tmp_path / "roads.geojson"),
            "--villages", str(tmp_path / "villages.geojson"),
            "--truth", str(tmp_path / "truth.tif"),
            "--event-name", "test event",
            "--out", str(out),
        ]
    )
    meta = json.loads((out / "meta.json").read_text())
    assert meta["event_name"] == "test event" and meta["synthetic"] is False
    assert meta["metrics"]["baseline"]["iou"] > 0.8
    assert meta["summary"]["road_km_affected"] > 0
    assert to_db_pair(ev["before"]).shape == (2, 256, 256)
