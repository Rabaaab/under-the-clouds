"""Run the whole pipeline on a SYNTHETIC event and export the web-map files.

    python scripts/run_demo.py --out app/data
"""

from __future__ import annotations

import argparse

import numpy as np

from .export_web import export_web
from .pipeline import run_pipeline
from .preprocess import lee_filter, to_db
from .synthetic import make_synthetic_event


def to_db_pair(scene: np.ndarray) -> np.ndarray:
    """(2,H,W) linear intensity -> speckle-filtered (2,H,W) dB."""
    return np.stack([to_db(lee_filter(band)) for band in scene])


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", default="app/data")
    p.add_argument("--size", type=int, default=512)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--checkpoint", default=None, help="optional trained U-Net checkpoint (.pt)")
    args = p.parse_args(argv)

    ev = make_synthetic_event(size=args.size, seed=args.seed)
    before, after = to_db_pair(ev["before"]), to_db_pair(ev["after"])
    result = run_pipeline(
        before,
        after,
        ev["transform"],
        ev["crs"],
        roads=ev["roads"],
        villages=ev["villages"],
        checkpoint=args.checkpoint,
        truth_new_water=ev["truth_new_water"],
    )
    meta = export_web(
        args.out,
        before,
        after,
        result,
        ev["transform"],
        ev["crs"],
        {
            "synthetic": True,
            "event_name": "SYNTHETIC DEMO (not a real event)",
            "note": "Simulated radar with a known flood. It shows the pipeline works; it says nothing about real accuracy.",
        },
    )
    s = result["summary"]
    print(f"wrote {meta}")
    print(f"method: {result['primary_method']}, metrics vs synthetic truth: {result['metrics']}")
    print(
        f"flooded {s['flooded_area_km2']:.2f} km2, roads {s['road_km_affected']:.1f}/{s['road_km_total']:.1f} km, "
        f"villages near flood: {s['village_names']}"
    )


if __name__ == "__main__":
    main()
