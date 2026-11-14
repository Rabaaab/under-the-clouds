import geopandas as gpd
from shapely.geometry import LineString

from utc.osm import _keep


def test_keep_makes_messy_osm_tags_writable(tmp_path):
    """OSM tags can be lists, None or non-ASCII; the cleaned frame must still write to GeoJSON and read back."""
    gdf = gpd.GeoDataFrame(
        {
            "name": ["طريق", None],
            "highway": [["track", "path"], "primary"],
            "other": [{"a": 1}, None],
            "geometry": [LineString([(0, 0), (1, 1)]), LineString([(1, 1), (2, 2)])],
        },
        crs="EPSG:4326",
    )
    clean = _keep(gdf, ["name", "highway"])
    assert list(clean.columns) == ["name", "highway", "geometry"]
    clean.to_file(tmp_path / "r.geojson", driver="GeoJSON")
    back = gpd.read_file(tmp_path / "r.geojson")
    assert len(back) == 2 and back["name"].iloc[0] == "طريق"
