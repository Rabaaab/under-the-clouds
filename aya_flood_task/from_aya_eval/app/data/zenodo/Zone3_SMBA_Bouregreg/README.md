# Zone 3 — Sidi Mohammed Ben Abdellah reservoir (Bouregreg basin)

**March 2026 post-drought filling event**

---

## Overview

This subfolder contains the Sentinel-1 SAR patches and binary water masks for **Zone 3 — Sidi Mohammed Ben Abdellah (SMBA) reservoir**, located in the Bouregreg hydrological basin approximately 60 km southeast of Rabat. Zone 3 captures the reservoir at high filling during the March 2026 recovery period, following several years of drought in central Morocco.

## Geographic context

| Attribute | Value |
|-----------|-------|
| Location | SMBA reservoir, Khemisset Province, Morocco |
| Basin | Bouregreg |
| AOI bounds | [-6.8001°, -6.4500°] E, [33.7800°, 34.0502°] N |
| AOI size | ~38.9 × 30.0 km |
| Central coordinates | 6.625°W, 33.915°N |

## Hydrological event

The SMBA reservoir is a strategic water infrastructure supplying drinking water to the Rabat-Casablanca metropolitan area. Central Morocco experienced severe drought conditions from 2022 to 2025, leading to critically low filling levels at SMBA. The winter 2025–2026 rainfall season brought partial recovery, and Zone 3 captures the reservoir at post-drought filling during the March 2026 acquisition window.

## Sentinel-1 acquisition parameters

| Parameter | Value |
|-----------|-------|
| Platforms | Sentinel-1A + Sentinel-1C |
| Number of scenes | 6 |
| Acquisition window | 22 March – 4 April 2026 |
| Product type | GRD (Ground Range Detected) |
| Mode | IW (Interferometric Wide swath) |
| Polarizations | VV, VH |
| Relative orbits (Asc) | 147 |
| Relative orbits (Desc) | 154 |
| Incidence angle range | 35.9° – 38.2° |
| Nominal pixel spacing | 10 m |

## Dataset composition

| Water class | Water fraction | Patches |
|-------------|:--------------:|:-------:|
| no_water | < 1% | 88 |
| low_water | 1% – 10% | 46 |
| medium_water | 10% – 30% | 29 |
| high_water | ≥ 30% | 13 |
| **Total** | | **176** |

## Files in this folder

```
Zone3_SMBA_Bouregreg/
├── README.md                             ← This file
├── metadata_zone3.csv                    ← 176 patches metadata (25 columns)
├── raw/
│   ├── S1_Zone3_SMBA.tif                       ← Full-scene VV+VH median composite
│   └── WaterMask_Zone3_SMBA.tif                ← Full-scene binary water mask
└── patches/
    ├── images/       ← 176 SAR patches (256 × 256, VV+VH, GeoTIFF)
    └── masks/        ← 176 binary water masks (256 × 256, uint8, GeoTIFF)
```

## Processing parameters

- **Random seed for class-aware sampling**: `45`
- **HSBA parameters**: min tile size 64 px, max depth 5, BC threshold 0.55
- **Morphological cleaning**: opening (disk r=1) + closing (disk r=2) + remove small components (< 50 px) + fill small holes (< 50 px)
- **Patch stride**: 192 pixels (25% overlap between adjacent patches)

## Quality control

Zone 3 passed the two-pass quality control procedure applied to the full dataset without any patches being removed. The reservoir produces very clean SAR signatures (mean VV backscatter < -18 dB under water pixels), making the HSBA + Otsu pipeline particularly effective on this zone.

## Citation

**Dataset DOI:** [10.5281/zenodo.22964153](https://doi.org/10.5281/zenodo.22964153)

If you use data from this zone, please cite the full dataset:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.22964153

See the top-level `README.md` and `CITATION.cff` for the full citation format.
