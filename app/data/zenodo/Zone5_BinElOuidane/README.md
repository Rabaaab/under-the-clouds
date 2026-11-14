# Zone 5 — Bin El Ouidane reservoir (Oum Er-Rbia basin)

**Winter 2026 — High Atlas mountain reservoir**

---

## Overview

This subfolder contains the Sentinel-1 SAR patches and binary water masks for **Zone 5 — Bin El Ouidane reservoir**, a large mountain reservoir located in the High Atlas mountains, part of the Oum Er-Rbia hydrological basin. Zone 5 captures the reservoir at high winter filling in early 2026, representing a mountainous hydrological context distinct from the other zones of the dataset.

Zone 5 is the smallest zone in the dataset in geographic extent and number of patches (40), but it is essential for representing the mountainous terrain and providing a challenging benchmark due to SAR shadow and layover effects on steep slopes.

## Geographic context

| Attribute | Value |
|-----------|-------|
| Location | Bin El Ouidane reservoir, Azilal Province, Morocco |
| Basin | Oum Er-Rbia |
| Terrain | High Atlas mountains |
| AOI bounds | [-6.5000°, -6.3400°] E, [32.0399°, 32.1400°] N |
| AOI size | ~17.8 × 11.1 km |
| Central coordinates | 6.420°W, 32.090°N |
| Elevation | ~800–1,500 m above sea level |

## Hydrological event

Bin El Ouidane is one of Morocco's largest mountain reservoirs (~1.5 billion m³), created by the Bin El Ouidane dam on the El Abid river. The reservoir plays a central role in irrigation, hydropower generation, and drinking water supply for the Beni Mellal-Khenifra region and beyond. Its filling level varies seasonally with snowmelt and rainfall in the High Atlas. Zone 5 captures the reservoir at high winter filling in early 2026.

## Sentinel-1 acquisition parameters

| Parameter | Value |
|-----------|-------|
| Platforms | Sentinel-1A + Sentinel-1C |
| Number of scenes | 7 |
| Acquisition window | 21 February – 6 March 2026 |
| Product type | GRD (Ground Range Detected) |
| Mode | IW (Interferometric Wide swath) |
| Polarizations | VV, VH |
| Relative orbits (Asc) | 147 |
| Relative orbits (Desc) | 81, 154 |
| Incidence angle range | 45.2° – 46.2° |
| Nominal pixel spacing | 10 m |

## Dataset composition

| Water class | Water fraction | Patches |
|-------------|:--------------:|:-------:|
| no_water | < 1% | 8 |
| low_water | 1% – 10% | 13 |
| medium_water | 10% – 30% | 6 |
| high_water | ≥ 30% | 13 |
| **Total** | | **40** |

## Files in this folder

```
Zone5_BinElOuidane/
├── README.md                                     ← This file
├── metadata_zone5.csv                            ← 40 patches metadata (25 columns)
├── raw/
│   ├── S1_Zone5_BinElOuidane_WINTER2026.tif            ← Full-scene VV+VH median composite
│   └── WaterMask_Zone5_BinElOuidane_WINTER2026.tif     ← Full-scene binary water mask
└── patches/
    ├── images/       ← 40 SAR patches (256 × 256, VV+VH, GeoTIFF)
    └── masks/        ← 40 binary water masks (256 × 256, uint8, GeoTIFF)
```

## Processing parameters

- **Random seed for class-aware sampling**: `47`
- **HSBA parameters**: min tile size 64 px, max depth 5, BC threshold 0.55
- **Morphological cleaning**: opening (disk r=1) + closing (disk r=2) + remove small components (< 50 px) + fill small holes (< 50 px)
- **Patch stride**: 192 pixels (25% overlap between adjacent patches)

## AOI reduction history

An initial processing was performed on a **larger AOI (~50 × 50 km)** covering a broader mountainous area around the reservoir. This wider AOI led to HSBA misclassifications due to **SAR shadow and layover effects on steep slopes**: some shadowed slopes displayed backscatter values similar to water (very low VV signal), causing false water detections in non-water areas.

The AOI was therefore **reduced to a focused ~17.8 × 11.1 km window centered on the reservoir itself**, minimizing the influence of mountainous terrain artifacts on the HSBA global threshold. This reduction increased the number of retained patches from 32 (initial processing on wider AOI) to 40 (focused AOI), because the local backscatter distribution became more clearly bimodal.

## Quality control

Zone 5 passed the two-pass quality control procedure applied to the full dataset without any patches being removed. Fig. 6 of the associated Data in Brief article uses Zone 5 as the illustrative example of the semi-automatic water mask generation pipeline (VV composite → HSBA + Otsu raw output → final mask after morphological cleaning).

## Zone-specific note

Zone 5 is particularly valuable for testing model **robustness to mountainous terrain** and **SAR shadow / layover artifacts**. The reservoir's smooth surface provides a clear water signature (mean VV backscatter around -18 dB), but the surrounding steep terrain introduces context that is not present in the other zones.

Users interested specifically in mountain reservoir monitoring should note that this zone is best suited for **evaluation** rather than **training**, given its small size (only 40 patches).

## Citation

**Dataset DOI:** [10.5281/zenodo.22964153](https://doi.org/10.5281/zenodo.22964153)

If you use data from this zone, please cite the full dataset:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.22964153

See the top-level `README.md` and `CITATION.cff` for the full citation format.
