"""Clean-up to reduce false alarms: sea/coast, thin artefacts, steep terrain, tiny blobs."""

from __future__ import annotations

import numpy as np
from scipy import ndimage as ndi

# Heuristic default; flooding on steep slopes is unlikely, but tune per region.
DEFAULT_MAX_SLOPE_DEG = 10.0
NE_LAND_URL = "https://naciscdn.org/naturalearth/10m/physical/ne_10m_land.zip"


def remove_small_objects(mask: np.ndarray, min_size: int = 20) -> np.ndarray:
    """Drop connected components smaller than `min_size` pixels (8-connectivity)."""
    mask = np.asarray(mask).astype(bool)
    labels, n = ndi.label(mask, structure=np.ones((3, 3), dtype=int))
    if n == 0:
        return mask
    counts = np.bincount(labels.ravel())
    keep = counts >= min_size
    keep[0] = False
    return keep[labels]


def remove_thin(mask: np.ndarray, radius_px: int = 2) -> np.ndarray:
    """Morphological opening: removes strips and lines narrower than about 2*radius_px+1 pixels
    (coastline strips, tile-seam lines). Also removes real but very narrow flooding: report it."""
    mask = np.asarray(mask).astype(bool)
    if radius_px <= 0:
        return mask
    y, x = np.ogrid[-radius_px:radius_px + 1, -radius_px:radius_px + 1]
    disk = (x * x + y * y) <= radius_px * radius_px
    return ndi.binary_opening(mask, structure=disk)


def land_mask_for_grid(transform, shape, crs="EPSG:4326", coastal_margin_m: float = 1000.0,
                       land_source: str = NE_LAND_URL) -> np.ndarray:
    """True on land at least `coastal_margin_m` from the sea, on the scene grid.

    Uses Natural Earth 1:10m land (coastline accurate to a few hundred metres, hence the margin)."""
    import geopandas as gpd
    from rasterio.features import rasterize
    from rasterio.transform import array_bounds
    from shapely.geometry import box

    h, w = shape
    west, south, east, north = array_bounds(h, w, transform)
    aoi = gpd.GeoDataFrame(geometry=[box(west, south, east, north)], crs=crs)
    land = gpd.read_file(land_source, bbox=tuple(aoi.to_crs(4326).total_bounds)).to_crs(crs)
    land = gpd.clip(land, aoi)
    if land.empty:
        return np.zeros(shape, dtype=bool)
    utm = aoi.estimate_utm_crs()
    geoms = land.to_crs(utm).buffer(-coastal_margin_m)
    geoms = geoms[~geoms.is_empty].to_crs(crs)
    if geoms.empty:
        return np.zeros(shape, dtype=bool)
    return rasterize([(g, 1) for g in geoms], out_shape=shape, transform=transform,
                     fill=0, dtype="uint8").astype(bool)


def slope_from_dem(dem: np.ndarray, pixel_size_m: float) -> np.ndarray:
    """Slope in degrees from a DEM with square pixels in a projected (metre) grid.

    If your DEM is in degrees (EPSG:4326), reproject it to a metric CRS first.
    """
    dem = np.asarray(dem, dtype=np.float32)
    gy, gx = np.gradient(dem, pixel_size_m)
    return np.degrees(np.arctan(np.hypot(gx, gy)))


def mask_steep(mask: np.ndarray, slope_deg: np.ndarray, max_slope_deg: float = DEFAULT_MAX_SLOPE_DEG) -> np.ndarray:
    """Remove detections on terrain steeper than `max_slope_deg` (radar shadow looks like water)."""
    mask = np.asarray(mask).astype(bool)
    if slope_deg.shape != mask.shape:
        raise ValueError("slope and mask shapes differ")
    return mask & (slope_deg <= max_slope_deg)


def clean_change(
    change: np.ndarray,
    min_size: int = 20,
    slope_deg: np.ndarray | None = None,
    max_slope_deg: float = DEFAULT_MAX_SLOPE_DEG,
    land_mask: np.ndarray | None = None,
    thin_radius_px: int = 0,
) -> np.ndarray:
    """Defaults keep the old behaviour. Order: land mask -> steep slopes -> thin shapes -> tiny blobs."""
    out = np.asarray(change).astype(bool)
    if land_mask is not None:
        if land_mask.shape != out.shape:
            raise ValueError("land mask and change shapes differ")
        out = out & land_mask
    if slope_deg is not None:
        out = mask_steep(out, slope_deg, max_slope_deg)
    if thin_radius_px > 0:
        out = remove_thin(out, thin_radius_px)
    return remove_small_objects(out, min_size)
