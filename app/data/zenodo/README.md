# SAR Morocco Flood Dataset

**A georeferenced Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan hydrological zones (2024–2026)**

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.22964153-blue.svg)](https://doi.org/10.5281/zenodo.22964153)
[![Data in Brief](https://img.shields.io/badge/Article-Data%20in%20Brief-orange.svg)]()

---

## Overview

The **SAR Morocco Flood Dataset** is a curated collection of **1,497 georeferenced Sentinel-1 SAR patches** (256 × 256 pixels, dual-polarization VV+VH) with corresponding **binary water masks**, distributed across **five hydrological zones** in northern-central Morocco. It captures recent hydrological events documented between September 2024 and April 2026, including major floods, reservoir states at contrasting seasons, and a post-drought reservoir filling.

The dataset was developed to support the training and evaluation of deep learning models targeting SAR-based water body and flood segmentation in Mediterranean and North African contexts, addressing the current under-representation of this region in publicly available flood datasets such as Sen1Floods11 and S1S2-Water.

## Highlights

- **1,497 co-registered patches** (256 × 256 pixels)
- **Dual-polarization Sentinel-1** imagery (VV + VH, in decibels)
- **Binary water masks** aligned pixel-per-pixel with SAR patches
- **Four water classes** (no_water / low / medium / high) based on water fraction
- **Five hydrological zones** covering floodplains, reservoirs, agricultural lowlands, and mountainous terrain
- **Four hydrological basins** (Loukkos, Sebou, Bouregreg, Oum Er-Rbia)
- **Two-pass visual quality control** applied systematically to all zones
- **Fully reproducible pipeline** with accompanying GEE and Python scripts

## Dataset composition

| Zone | Location | Basin | Event / Period | Patches |
|:----:|----------|-------|----------------|:-------:|
| Z1 | Ksar El Kebir | Loukkos | Jan–Feb 2026 flood | 102 |
| Z2 | Al Wahda reservoir | Sebou | Summer 2024 + Winter 2025 | 292 |
| Z3 | SMBA reservoir | Bouregreg | March 2026 post-drought filling | 176 |
| Z4 | Gharb plain | Sebou (lower) | Feb 2026 flood | 887 |
| Z5 | Bin El Ouidane reservoir | Oum Er-Rbia | Winter 2026 | 40 |
| **Total** | **5 zones** | **4 basins** | | **1,497** |

### Water class distribution

| Class | Water fraction | Count | % |
|-------|----------------|:-----:|:--:|
| no_water | < 1% | 649 | 43.4% |
| low_water | 1% ≤ f < 10% | 471 | 31.5% |
| medium_water | 10% ≤ f < 30% | 153 | 10.2% |
| high_water | f ≥ 30% | 224 | 14.9% |

## Repository structure

```
SAR_Morocco_Dataset/
├── README.md                       ← You are here
├── LICENSE                         ← CC BY 4.0 license text
├── CHANGELOG.md                    ← Version history
├── CITATION.cff                    ← Machine-readable citation
├── metadata_global.csv             ← Consolidated metadata (1,497 patches)
│
├── auxiliary/
│   └── JRC_occurrence_Zone1_KsarElKebir.tif   ← JRC Global Surface Water (contextual)
│
├── Zone1_KsarElKebir/
│   ├── README.md                       ← Zone-specific documentation
│   ├── metadata_zone1.csv              ← 102 patches metadata
│   ├── raw/
│   │   ├── S1_Zone1_KsarElKebir_FLOOD2026.tif  ← Full-scene VV+VH composite
│   │   └── WaterMask_Zone1_KsarElKebir.tif     ← Full-scene binary mask
│   └── patches/
│       ├── images/     ← 102 SAR patches (256×256, VV+VH)
│       └── masks/      ← 102 binary water masks
│
├── Zone2_Sebou_AlWahda/     ← Same structure (292 patches)
├── Zone3_SMBA_Bouregreg/    ← Same structure (176 patches)
├── Zone4_Gharb/             ← Same structure (887 patches)
├── Zone5_BinElOuidane/      ← Same structure (40 patches)
│
└── scripts/
    ├── GEE_download_S1.js              ← Google Earth Engine acquisition
    ├── generate_water_masks.ipynb      ← HSBA + Otsu + morphology
    ├── extract_patches.ipynb           ← Patch tiling and sampling
    └── quality_control.ipynb           ← Component-level SAR analysis
```

## File format specifications

### Image patches (`patches/images/*.tif`)

- **Format**: GeoTIFF
- **Dimensions**: 256 × 256 pixels
- **Bands**: 2 (VV, VH) in decibels
- **Data type**: Float32
- **Coordinate Reference System**: WGS84 geographic (EPSG:4326)
- **Pixel spacing**: 8.98 × 10⁻⁵ degrees (approximately 8.16–8.44 m East-West and 9.97 m North-South)

### Mask patches (`patches/masks/*.tif`)

- **Format**: GeoTIFF
- **Dimensions**: 256 × 256 pixels
- **Bands**: 1
- **Data type**: uint8
- **Values**: 0 (non-water) / 1 (water)
- **CRS**: WGS84 (EPSG:4326), aligned with image patches

Image and mask files share the same filename between the `images/` and `masks/` folders (e.g., `Zone1_KsarElKebir_patch_0000.tif`), ensuring one-to-one correspondence for direct use in supervised learning pipelines.

### Metadata CSV (`metadata_*.csv`)

Each patch is documented by 25 standardized fields (Zone 2 includes two additional columns: `source_image` and `season` to distinguish Summer 2024 and Winter 2025 acquisitions):

| Category | Fields |
|----------|--------|
| Identifiers | `patch_id`, `zone_id`, `zone_name` |
| Context | `basin`, `country`, `event`, `acquisition_date` |
| Sensor | `satellite`, `product`, `polarization`, `mode`, `resolution_m` |
| Dimensions | `patch_width_px`, `patch_height_px` |
| Geolocation | `center_lon`, `center_lat`, `bounds_west`, `bounds_east`, `bounds_south`, `bounds_north` |
| Water | `n_water_pixels`, `n_total_pixels`, `water_fraction`, `water_class` |
| Provenance | `annotation_method`, `image_path`, `mask_path` |

## Quick start

### Load a patch pair in Python

```python
import rasterio
import numpy as np

# Load Sentinel-1 image (VV + VH)
with rasterio.open('Zone4_Gharb/patches/images/Zone4_Gharb_patch_0100.tif') as src:
    vv = src.read(1)   # VV backscatter (dB)
    vh = src.read(2)   # VH backscatter (dB)
    bounds = src.bounds

# Load corresponding water mask
with rasterio.open('Zone4_Gharb/patches/masks/Zone4_Gharb_patch_0100.tif') as src:
    mask = src.read(1)   # 0 = non-water, 1 = water

print(f"Patch shape: {vv.shape}")
print(f"Water fraction: {100 * mask.mean():.2f}%")
```

### Load metadata with pandas

```python
import pandas as pd

# Load the consolidated metadata
df = pd.read_csv('metadata_global.csv')

# Filter high-water patches from the Gharb flood
high_water_gharb = df[
    (df['zone_id'] == 'Zone4') &
    (df['water_class'] == 'high_water')
]
print(f"{len(high_water_gharb)} high-water patches in Zone 4")
```

### Reproject to UTM (for isotropic metric pixels)

```python
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling

src_path = 'Zone1_KsarElKebir/patches/images/Zone1_KsarElKebir_patch_0050.tif'
dst_path = 'patch_utm.tif'
dst_crs = 'EPSG:32629'   # UTM zone 29N for western Morocco

with rasterio.open(src_path) as src:
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    profile = src.profile.copy()
    profile.update({'crs': dst_crs, 'transform': transform,
                     'width': width, 'height': height})

    with rasterio.open(dst_path, 'w', **profile) as dst:
        for i in range(1, src.count + 1):
            reproject(
                source=rasterio.band(src, i),
                destination=rasterio.band(dst, i),
                src_transform=src.transform, src_crs=src.crs,
                dst_transform=transform, dst_crs=dst_crs,
                resampling=Resampling.bilinear)
```

## Data processing pipeline

The dataset was constructed through four successive steps (see the accompanying Data in Brief article for full details):

1. **Sentinel-1 acquisition** via Google Earth Engine (temporal median composites, 3–26 day windows per zone).
2. **Semi-automatic water mask generation** using the Hierarchical Split-Based Approach (HSBA) combined with Otsu thresholding.
3. **Morphological post-processing** (opening, closing, small component removal, hole filling).
4. **Patch extraction with class-aware sampling**, followed by **two-pass visual quality control** (14 + 8 patches removed from Zone 4).

Fig. 5 of the associated article provides the complete workflow diagram; Fig. 6 illustrates the pipeline output on Zone 5.

## Recommended usage

### Training / evaluation splits

Because adjacent patches overlap by 25%, **avoid random patch-level splitting** when constructing training and evaluation subsets. We recommend using **spatially disjoint, scene-level, or zone-level partitions** to prevent information leakage. For example:

- **Zone-level split**: use Zones 1, 2, 3 for training; Zone 4 for validation; Zone 5 for testing.
- **Event-level split within Zone 2**: use Summer 2024 for training and Winter 2025 for testing.

### Class balancing

Zone 4 exhibits a moderate class imbalance towards water-containing patches (531 out of 887 patches, i.e. 59.9%, contain at least 1% water), reflecting the actual severity of the February 2026 Gharb flood. Users targeting a strictly balanced training set may apply rebalancing strategies (weighted loss, oversampling of no_water patches, etc.).

## Known limitations

Please refer to the Limitations section of the associated Data in Brief article for a full discussion. In summary:

- Water masks are semi-automatically generated and may contain classification errors along narrow water boundaries.
- 10 m nominal pixel spacing limits detection of very narrow water bodies (< 20–30 m).
- Zone 4 shows moderate class imbalance towards water-containing patches (59.9%).
- Zone 1 presents lower average water/land backscatter contrast due to its low incidence angle range and predominantly agricultural landscape.
- Coverage limited to events between September 2024 and April 2026.
- SAR-only data (SAR-optical fusion requires additional acquisition).
- 25% patch overlap requires spatially disjoint splitting strategies.
- WGS84 geographic CRS produces slightly rectangular pixels; re-project to UTM for isotropic grids.

## Citation

If you use this dataset, please cite both the dataset and the associated article:

**Dataset:**
```
Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
Tairi, H., & Riffi, J. (2026). SAR Morocco Flood Dataset: A georeferenced
Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
hydrological zones (2024–2026) [Data set]. Zenodo.
https://doi.org/10.5281/zenodo.22964153
```

**Article:**
```
Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
Tairi, H., & Riffi, J. (2026). A georeferenced Sentinel-1 SAR dataset for
water and flood segmentation in five Moroccan hydrological zones
(2024–2026). Data in Brief, [manuscript in preparation].
```

A machine-readable citation is available in `CITATION.cff`.

## License

This dataset is released under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**. See `LICENSE` for the full text.

**Third-party data licensing:**
- **Sentinel-1 imagery**: Copernicus Programme, free and open data policy. Required attribution: *"Contains modified Copernicus Sentinel data 2024-2026, processed by Kzadri M., Begdouri A., El Fazazy K., Qjidaa H., Ouazzani Jamil M., Tairi H., and Riffi J."*
- **JRC Global Surface Water layer** (auxiliary): © European Union, 1984–2021.

## Contact

**Marwane Kzadri** (corresponding author)
Laboratory of Computer Science, Innovation and Artificial Intelligence (L3IA), FSDM, USMBA, Fez, Morocco
Intelligent Systems, Energy and Sustainable Development Laboratory (SIEDD), UPF, Fez, Morocco
Email: marwane.kzadri@usmba.ac.ma
ORCID: [0009-0007-1307-0242](https://orcid.org/0009-0007-1307-0242)

**Co-authors:**

- **Ahlame Begdouri** — Intelligent Systems and Applications Laboratory (LISA), FST-Fez, USMBA, Morocco
- **Khalid El Fazazy** — L3IA, FSDM, USMBA, Fez, Morocco
- **Hassan Qjidaa** — SIEDD, UPF, Fez, Morocco
- **Mohammed Ouazzani Jamil** — SIEDD, UPF, Fez, Morocco
- **Hamid Tairi** — L3IA, FSDM, USMBA, Fez, Morocco
- **Jamal Riffi** — L3IA, FSDM, USMBA, Fez, Morocco / SIEDD, UPF, Fez, Morocco

## Acknowledgements

This work was carried out at the L3IA Laboratory (FSDM, USMBA), the SIEDD Laboratory (UPF), and the LISA Laboratory (FST-Fez, USMBA), Fez, Morocco. The authors acknowledge the European Space Agency and the Copernicus Programme for providing free Sentinel-1 imagery, Google Earth Engine for providing access to the imagery archive and computational resources, and the European Commission Joint Research Centre for the Global Surface Water dataset used as contextual reference.

## Funding

This research did not receive any specific grant from funding agencies in the public, commercial, or not-for-profit sectors.

---

**Last updated:** 2026-09-27
**Dataset version:** 1.0.0
