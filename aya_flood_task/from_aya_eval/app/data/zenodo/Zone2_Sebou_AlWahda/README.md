# Zone 2 — Al Wahda reservoir (Sebou basin)

**Summer 2024 + Winter 2025 — two contrasting seasonal states**

---

## Overview

This subfolder contains the Sentinel-1 SAR patches and binary water masks for **Zone 2 — Al Wahda reservoir**, the largest dam in Morocco, located in the Sebou hydrological basin. Zone 2 is unique in the dataset because it captures the same area at **two contrasting seasonal states**:

- **Summer 2024** (September–October 2024): reservoir at lower filling after the dry season.
- **Winter 2025** (February–March 2025): reservoir at higher filling after winter rainfall.

This dual acquisition allows model evaluation on temporal variations of the same water body under different hydrological regimes.

## Geographic context

| Attribute | Value |
|-----------|-------|
| Location | Al Wahda reservoir, Ouazzane / Taounate Provinces, Morocco |
| Basin | Sebou |
| AOI bounds | [-5.3200°, -4.9999°] E, [34.5000°, 34.7001°] N |
| AOI size | ~35.5 × 22.2 km |
| Central coordinates | 5.160°W, 34.600°N |

## Hydrological event

Al Wahda is Morocco's largest reservoir by capacity (~3.7 billion m³), created by the Al Wahda dam on the Ouergha river (a major tributary of the Sebou). The reservoir plays a central role in flood regulation, agricultural irrigation, and hydropower generation in the Sebou basin. Its filling level varies substantially between seasons, making it an ideal target for benchmarking water segmentation models across contrasting conditions.

## Sentinel-1 acquisition parameters

### Summer 2024

| Parameter | Value |
|-----------|-------|
| Platform | Sentinel-1A |
| Number of scenes | 16 |
| Acquisition window | 16 September – 11 October 2024 |
| Incidence angle range | 44.5° – 46.2° |

### Winter 2025

| Parameter | Value |
|-----------|-------|
| Platform | Sentinel-1A |
| Number of scenes | 13 |
| Acquisition window | 15 February – 11 March 2025 |
| Incidence angle range | 41.3° – 43.1° |

### Common parameters

| Parameter | Value |
|-----------|-------|
| Product type | GRD (Ground Range Detected) |
| Mode | IW (Interferometric Wide swath) |
| Polarizations | VV, VH |
| Relative orbits (Asc) | 74, 147 |
| Relative orbits (Desc) | 81, 154 |
| Nominal pixel spacing | 10 m |

**Note**: Both acquisition periods rely exclusively on Sentinel-1A because Sentinel-1C was launched only in December 2024, and Sentinel-1B was no longer operational.

## Dataset composition

| Water class | Water fraction | Patches |
|-------------|:--------------:|:-------:|
| no_water | < 1% | 146 |
| low_water | 1% – 10% | 59 |
| medium_water | 10% – 30% | 25 |
| high_water | ≥ 30% | 62 |
| **Total** | | **292** |

The two seasons (summer, winter) are combined into a single set of 292 patches. Each patch's `source_image` and `season` metadata columns indicate which acquisition it originates from.

## Files in this folder

```
Zone2_Sebou_AlWahda/
├── README.md                                     ← This file
├── metadata_zone2.csv                            ← 292 patches metadata (27 columns)
├── raw/
│   ├── S1_Zone2_Dam_SUMMER2024.tif                     ← Summer 2024 composite
│   ├── S1_Zone2_Dam_WINTER2025.tif                     ← Winter 2025 composite
│   ├── WaterMask_Zone2_Dam_SUMMER2024.tif              ← Summer 2024 mask
│   └── WaterMask_Zone2_Dam_WINTER2025.tif              ← Winter 2025 mask
└── patches/
    ├── images/       ← 292 SAR patches (256 × 256, VV+VH, GeoTIFF)
    └── masks/        ← 292 binary water masks (256 × 256, uint8, GeoTIFF)
```

## Processing parameters

- **Random seeds for class-aware sampling**: `43` (Summer 2024), `44` (Winter 2025)
- **HSBA parameters**: min tile size 64 px, max depth 5, BC threshold 0.55
- **Morphological cleaning**: opening (disk r=1) + closing (disk r=2) + remove small components (< 50 px) + fill small holes (< 50 px)
- **Patch stride**: 192 pixels (25% overlap between adjacent patches)

## Special metadata columns

Zone 2 metadata CSV includes two additional columns compared to the other zones:

- `source_image`: identifies the source composite (`SUMMER2024` or `WINTER2025`).
- `season`: human-readable season label (`Summer 2024` or `Winter 2025`).

These columns allow users to easily separate the two seasonal acquisitions for training/testing splits, for example using Summer 2024 for training and Winter 2025 for testing to evaluate temporal generalization.

## Quality control

Zone 2 passed the two-pass quality control procedure applied to the full dataset without any patches being removed. The reservoir's smooth open water surface produces very clean SAR signatures (mean VV backscatter < -18 dB under water pixels), making the HSBA + Otsu pipeline particularly effective on this zone.

## Citation

**Dataset DOI:** [10.5281/zenodo.22964153](https://doi.org/10.5281/zenodo.22964153)

If you use data from this zone, please cite the full dataset:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.22964153

See the top-level `README.md` and `CITATION.cff` for the full citation format.
