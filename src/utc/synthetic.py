"""Synthetic radar scenes with a known flood, for testing the code. NOT real data.

The numbers (about -10 dB land, -22 dB water, gamma speckle) are illustrative. A pipeline that works
here proves the code runs end to end; it says nothing about accuracy on real radar.
"""

from __future__ import annotations

import geopandas as gpd
import numpy as np
from rasterio.transform import from_bounds
from scipy import ndimage as ndi
from shapely.geometry import LineString, Point

from .io import pixel_to_xy

# Arbitrary bounding box (west, south, east, north), only used to place the demo on the map.
DEFAULT_BBOX = (-5.60, 30.00, -5.40, 30.20)


def _speckled(mean_linear: np.ndarray, rng: np.random.Generator, looks: int) -> np.ndarray:
    return rng.gamma(shape=looks, scale=mean_linear / looks).astype(np.float32)


def make_synthetic_event(size: int = 512, seed: int = 0, looks: int = 4, bbox=DEFAULT_BBOX) -> dict:
    """Build a before/after radar pair (linear intensity), ground truth, roads and villages."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:size, 0:size]

    centre = size * 0.5 + 60.0 * np.sin(xx / size * 2 * np.pi * 1.5)
    river = np.abs(yy - centre) < 6
    lake = (xx - 0.25 * size) ** 2 + (yy - 0.8 * size) ** 2 < 50**2
    water_before = river
    water_after = (np.abs(yy - centre) < 40) | lake | river

    texture = ndi.gaussian_filter(rng.standard_normal((size, size)), 12)
    texture = (texture - texture.mean()) / (texture.std() + 1e-9)
    land_vv = 10 ** (-10.0 / 10) * (1 + 0.15 * texture)
    land_vh = 10 ** (-17.0 / 10) * (1 + 0.15 * texture)
    water_vv, water_vh = 10 ** (-22.0 / 10), 10 ** (-26.0 / 10)

    def scene(water):
        vv = np.where(water, water_vv, land_vv)
        vh = np.where(water, water_vh, land_vh)
        return np.stack([_speckled(vv, rng, looks), _speckled(vh, rng, looks)])

    west, south, east, north = bbox
    transform = from_bounds(west, south, east, north, size, size)

    def px(col, row):
        return pixel_to_xy(transform, col, row)

    roads = gpd.GeoDataFrame(
        {
            "name": ["Road 1 (crosses flood)", "Road 2 (crosses flood)", "Road 3 (dry)", "Road 4 (crosses lake)"],
            "geometry": [
                LineString([px(0.30 * size, 0), px(0.30 * size, size)]),
                LineString([px(0.80 * size, 0), px(0.80 * size, size)]),
                LineString([px(0, 0.10 * size), px(size, 0.10 * size)]),
                LineString([px(0, 0.80 * size), px(0.5 * size, 0.80 * size)]),
            ],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )
    villages = gpd.GeoDataFrame(
        {
            "name": ["Village A (near flood)", "Village B (far)", "Village C (in lake)"],
            "geometry": [
                # just below the flood edge; the offset is a fixed fraction of the scene so it is ~250 m at any size
                Point(px(0.50 * size, 0.50 * size - 60 + 40 + 0.01 * size)),
                Point(px(0.78 * size, 0.12 * size)),
                Point(px(0.25 * size, 0.80 * size)),
            ],
        },
        geometry="geometry",
        crs="EPSG:4326",
    )

    return {
        "before": scene(water_before),
        "after": scene(water_after),
        "water_before": water_before,
        "water_after": water_after,
        "truth_new_water": water_after & ~water_before,
        "transform": transform,
        "crs": "EPSG:4326",
        "roads": roads,
        "villages": villages,
    }
