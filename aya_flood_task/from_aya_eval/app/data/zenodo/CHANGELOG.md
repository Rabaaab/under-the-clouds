# Changelog

All notable changes to the **SAR Morocco Flood Dataset** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-09-27

### Initial release

**Version 1.0.0** is the first public release of the SAR Morocco Flood Dataset,
associated with the Data in Brief manuscript:

> Kzadri M., Begdouri A., El Fazazy K., Qjidaa H., Ouazzani Jamil M., Tairi H.,
> & Riffi J. (2026). *A georeferenced Sentinel-1 SAR dataset for water
> and flood segmentation in five Moroccan hydrological zones (2024–2026)*.
> Data in Brief, [manuscript in preparation].

### Added

- **1,497 georeferenced Sentinel-1 SAR patches** (256 × 256 pixels, dual-polarization VV+VH)
  distributed across five hydrological zones in northern-central Morocco.
- **1,497 binary water masks** (256 × 256 pixels, uint8) co-registered with the SAR patches.
- **Per-zone metadata CSV files** with 25 standardized fields per patch
  (Zone 2 includes two additional columns: `source_image` and `season` to distinguish
  the Summer 2024 and Winter 2025 acquisitions).
- **Consolidated metadata_global.csv** containing all 1,497 patches.
- **Per-zone README Markdown files** documenting acquisition dates, hydrological context,
  and processing parameters.
- **Raw Sentinel-1 GRD median composites** (VV+VH) and full-scene water masks per zone.
- **Auxiliary JRC Global Surface Water occurrence layer** (contextual reference only).
- **Processing scripts** (Google Earth Engine JavaScript + Python Colab notebooks)
  under the `scripts/` folder.

### Dataset composition

| Zone | Location | Basin | Patches |
|------|----------|-------|:-------:|
| Z1 | Ksar El Kebir | Loukkos | 102 |
| Z2 | Al Wahda (Summer 2024 + Winter 2025) | Sebou | 292 |
| Z3 | SMBA | Bouregreg | 176 |
| Z4 | Gharb plain | Sebou (lower) | 887 |
| Z5 | Bin El Ouidane | Oum Er-Rbia | 40 |
| **Total** | **5 zones** | **4 basins** | **1,497** |

### Quality control history

The dataset underwent a two-pass systematic quality control before release,
applied to all 1,519 patches produced by the initial extraction:

- **Pass 1** — Visual pattern check applied to all 5 zones.
  Only Zone 4 revealed problematic patches: 14 patches with atypical diagonal
  ripple SAR patterns consistent with ploughed agricultural fields were identified
  and removed.

- **Pass 2** — Component-level SAR signal analysis applied to all 5 zones.
  For each connected component in a mask, the mean VV backscatter was computed
  and compared to the expected range for surface water (< -15 dB). Components
  with mean backscatter above -13 dB were flagged as potential false positives
  for visual inspection:
  - **Zone 4**: 8 additional patches removed (urban structures or agricultural
    fields misclassified as water).
  - **Zones 2, 3, 5**: 0 flagged patches — all masks validated.
  - **Zone 1**: 11 flagged patches inspected and confirmed as legitimate
    detections of small irrigated fields and narrow channels (see Zone 1 README
    for context on the low incidence angle and agricultural landscape).

**Zone 4 evolution**: 909 → 895 (after Pass 1) → 887 (after Pass 2) patches.
**Total dataset evolution**: 1,519 → 1,497 patches.

### Data format

- All raster files are provided as **GeoTIFF** in **WGS84 geographic coordinates (EPSG:4326)**.
- Pixel spacing: 8.98 × 10⁻⁵ degrees (approximately 8.16–8.44 m East-West and 9.97 m North-South
  depending on latitude), corresponding to the Google Earth Engine 10 m nominal
  sampling of Sentinel-1 GRD IW products.
- Users requiring an isotropic metric grid should re-project to a local UTM zone
  (EPSG:32629 or EPSG:32630 depending on longitude).

### License

- **CC BY 4.0** — Creative Commons Attribution 4.0 International License.
- Sentinel-1 data are used under the free and open Copernicus data policy.
- JRC Global Surface Water layer is used under its open license (© European Union, 1984–2021).

---

## Planned for future releases

Potential updates for future versions may include:

- Additional Moroccan hydrological zones covering complementary geographic contexts
  (arid oueds in the south, glacial lakes in the High Atlas).
- Integration of new flood events occurring after March 2026.
- Optional pre-computed splits (train / validation / test) with spatially disjoint partitions.
- UTM-reprojected versions of the patches for users requiring isotropic metric pixels.

---

## Citation

Please cite this dataset as:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22964153

See `CITATION.cff` for the machine-readable citation format.
