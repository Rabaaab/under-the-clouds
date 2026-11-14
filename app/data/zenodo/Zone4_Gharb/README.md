# Zone 4 — Gharb plain (Sebou basin, lower)

**February 2026 flood — largest event covered in the dataset**

---

## Overview

This subfolder contains the Sentinel-1 SAR patches and binary water masks for **Zone 4 — Gharb plain**, located in the lower Sebou basin between Kenitra and Sidi Kacem in northwestern Morocco. Zone 4 covers the largest hydrological event in the dataset: the extensive Gharb flood of February 2026, which affected approximately 85,000 hectares of agricultural land in the region (Moroccan Ministry of Agriculture, 27 February 2026).

Zone 4 is the largest zone in the dataset both in geographic extent (~88.8 × 44.5 km) and in number of patches (887 out of 1,497 total).

## Geographic context

| Attribute | Value |
|-----------|-------|
| Location | Gharb plain, Kenitra / Sidi Kacem Provinces, Morocco |
| Basin | Sebou (lower) |
| AOI bounds | [-6.5501°, -5.7499°] E, [34.1999°, 34.6007°] N |
| AOI size | ~88.8 × 44.5 km |
| Central coordinates | 6.150°W, 34.400°N |

## Hydrological event

The Gharb plain is a low-lying alluvial region drained by the Sebou river and its tributaries, historically prone to flooding due to its low elevation, poor drainage, and dense hydrographic network. The rainfall event of late January – early February 2026 caused the Sebou river to overflow, submerging extensive agricultural areas including rice fields, sugar beet plantations, and vegetable crops. According to the Moroccan Ministry of Agriculture (statement of 27 February 2026), approximately 85,000 hectares of agricultural land were affected in the Gharb region alone.

The Atlantic coastline in the western portion of the AOI was masked prior to HSBA processing to exclude ocean pixels and prevent bias in the global Otsu threshold.

## Sentinel-1 acquisition parameters

| Parameter | Value |
|-----------|-------|
| Platforms | Sentinel-1A + Sentinel-1C |
| Number of scenes | 6 |
| Acquisition window | 2 – 4 February 2026 (peak flood extent) |
| Product type | GRD (Ground Range Detected) |
| Mode | IW (Interferometric Wide swath) |
| Polarizations | VV, VH |
| Relative orbits (Asc) | 74, 147 |
| Relative orbits (Desc) | 81, 154 |
| Incidence angle range | 37.8° – 42.5° |
| Nominal pixel spacing | 10 m |

The very short acquisition window (3 days, from 2 to 4 February 2026) was chosen to capture the peak flood extent, taking advantage of the multi-orbit coverage provided by both Sentinel-1A and Sentinel-1C.

## Dataset composition

| Water class | Water fraction | Patches |
|-------------|:--------------:|:-------:|
| no_water | < 1% | 356 |
| low_water | 1% – 10% | 321 |
| medium_water | 10% – 30% | 80 |
| high_water | ≥ 30% | 130 |
| **Total** | | **887** |

**Class balance note**: Zone 4 shows a moderate class imbalance in favor of water-containing patches (531 out of 887 patches, i.e. 59.9%, contain at least 1% water), reflecting the actual severity of the February 2026 flood. This is different from other zones where non-water patches dominate. Users targeting a strictly balanced training set may apply additional rebalancing strategies (weighted loss, oversampling of no_water patches, etc.).

## Files in this folder

```
Zone4_Gharb/
├── README.md                                   ← This file
├── metadata_zone4.csv                          ← 887 patches metadata (25 columns)
├── raw/
│   ├── S1_Zone4_Gharb_FLOOD2026.tif                  ← Full-scene VV+VH median composite
│   └── WaterMask_Zone4_Gharb_FLOOD2026.tif           ← Full-scene binary water mask
└── patches/
    ├── images/       ← 887 SAR patches (256 × 256, VV+VH, GeoTIFF)
    └── masks/        ← 887 binary water masks (256 × 256, uint8, GeoTIFF)
```

## Processing parameters

- **Random seed for class-aware sampling**: `46`
- **HSBA parameters**: min tile size 64 px, max depth 5, BC threshold 0.55
- **Morphological cleaning**: opening (disk r=1) + closing (disk r=2) + remove small components (< 50 px) + fill small holes (< 50 px)
- **Patch stride**: 192 pixels (25% overlap between adjacent patches)
- **Special preprocessing**: Atlantic coastline masking before HSBA to exclude ocean pixels.
- **Class-aware sampling exception**: unlike the other zones, all eligible water-containing patches (water fraction ≥ 1%) were retained without sub-sampling to preserve the spatial coverage of the flood event.

## Quality control history

Zone 4 required the most intensive quality control in the dataset, due to the heterogeneous SAR signatures resulting from the mixture of true flood water, saturated soils, ploughed fields, and agricultural areas.

### Pass 1 — Visual pattern check (14 patches removed)

14 patches exhibiting atypical **diagonal ripple SAR patterns**, characteristic of ploughed agricultural fields, were identified and removed. These patterns produce false water detections that are visually recognizable as regular linear structures rather than actual flood signatures.

**Zone 4 evolution**: 909 → 895 patches.

### Pass 2 — Component-level SAR signal analysis (8 patches removed)

A component-level analysis was performed on all remaining patches with water content: for each connected component in a mask, the mean VV backscatter was computed and compared to the expected range for surface water (< -15 dB). Components with mean backscatter above -13 dB were flagged as potential false positives.

Flagged patches were then visually inspected, and 8 additional patches were identified and removed:
- Patches where the mask predominantly covered urban structures (villages, small towns).
- Patches where the mask covered ploughed or dry agricultural fields rather than flood water.
- Patches where connected components displayed backscatter values inconsistent with actual water bodies.

**Removed patches (Pass 2)**: `patch_0004`, `patch_0078`, `patch_0146`, `patch_0158`, `patch_0175`, `patch_0176`, `patch_0247`, `patch_0294`.

**Zone 4 final**: 895 → 887 patches.

### Overall Zone 4 evolution

`909 (initial extraction) → 895 (after Pass 1) → 887 (after Pass 2)` — total of 22 patches removed.

## Recommended usage

Given the size and class distribution of Zone 4, it can be used as:

- A **primary training zone** for flood segmentation models targeting Mediterranean and North African agricultural regions.
- A **standalone benchmark** for models trained on other datasets (Sen1Floods11, S1S2-Water) to evaluate their generalization to Moroccan conditions.
- A **cross-validation zone** in combination with other zones of the dataset, provided that spatially disjoint splitting strategies are applied (avoid random patch-level splits due to 25% overlap).

## Citation

**Dataset DOI:** [10.5281/zenodo.22964153](https://doi.org/10.5281/zenodo.22964153)

If you use data from this zone, please cite the full dataset:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.22964153

See the top-level `README.md` and `CITATION.cff` for the full citation format.
