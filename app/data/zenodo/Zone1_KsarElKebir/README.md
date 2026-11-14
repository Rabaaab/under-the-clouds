# Zone 1 — Ksar El Kebir (Loukkos basin)

**January–February 2026 flood event**

---

## Overview

This subfolder contains the Sentinel-1 SAR patches and binary water masks for **Zone 1 — Ksar El Kebir**, located in the Loukkos hydrological basin in northern Morocco. The zone covers the flooded plain around the city of Ksar El Kebir during the intense rainfall event of January–February 2026.

## Geographic context

| Attribute | Value |
|-----------|-------|
| Location | Ksar El Kebir, Larache Province, Morocco |
| Basin | Loukkos |
| AOI bounds | [-6.0201°, -5.7899°] E, [34.9000°, 35.1001°] N |
| AOI size | ~25.6 × 22.2 km |
| Central coordinates | 5.905°W, 35.000°N |

## Hydrological event

The Loukkos basin experienced sustained heavy rainfall during late January and early February 2026, leading to the overflow of the Loukkos river and its tributaries. The Ksar El Kebir plain, historically prone to flooding due to its low elevation and proximity to the Atlantic coast, was one of the most affected areas.

## Sentinel-1 acquisition parameters

| Parameter | Value |
|-----------|-------|
| Platforms | Sentinel-1A + Sentinel-1C |
| Number of scenes | 9 |
| Acquisition window | 27 January – 4 February 2026 |
| Product type | GRD (Ground Range Detected) |
| Mode | IW (Interferometric Wide swath) |
| Polarizations | VV, VH |
| Relative orbits (Asc) | 74, 147 |
| Relative orbits (Desc) | 81, 154 |
| Incidence angle range | 30.5° – 30.8° |
| Nominal pixel spacing | 10 m |

Note: The relatively low incidence angle range (30–31°) reduces water/land backscatter contrast compared to other zones with higher angles. See the associated Data in Brief article for a discussion of the implications.

## Dataset composition

| Water class | Water fraction | Patches |
|-------------|:--------------:|:-------:|
| no_water | < 1% | 51 |
| low_water | 1% – 10% | 32 |
| medium_water | 10% – 30% | 13 |
| high_water | ≥ 30% | 6 |
| **Total** | | **102** |

## Files in this folder

```
Zone1_KsarElKebir/
├── README.md                             ← This file
├── metadata_zone1.csv                    ← 102 patches metadata (25 columns)
├── raw/
│   ├── S1_Zone1_KsarElKebir_FLOOD2026.tif      ← Full-scene VV+VH median composite
│   └── WaterMask_Zone1_KsarElKebir.tif         ← Full-scene binary water mask
└── patches/
    ├── images/       ← 102 SAR patches (256 × 256, VV+VH, GeoTIFF)
    └── masks/        ← 102 binary water masks (256 × 256, uint8, GeoTIFF)
```

## Processing parameters

- **Random seed for class-aware sampling**: `42`
- **HSBA parameters**: min tile size 64 px, max depth 5, BC threshold 0.55
- **Morphological cleaning**: opening (disk r=1) + closing (disk r=2) + remove small components (< 50 px) + fill small holes (< 50 px)
- **Patch stride**: 192 pixels (25% overlap between adjacent patches)

## Quality control

Zone 1 passed the two-pass quality control procedure applied to the full dataset:
- **Pass 1** (visual pattern check): No patches removed.
- **Pass 2** (component-level SAR signal analysis): 11 patches were initially flagged for having connected components with mean VV backscatter above -13 dB. After visual inspection, all 11 patches were confirmed as legitimate detections of small irrigated fields and narrow channels typical of the Loukkos agricultural plain, and were retained in the final dataset.

## Zone-specific note

Zone 1 presents a **lower average water/land backscatter contrast** compared to the other zones, due to two factors:

1. The **low incidence angle range** (30.5°–30.8°) reduces specular reflection contrast between smooth water surfaces and rough land surfaces.
2. The **predominantly agricultural landscape** is composed of narrow irrigation channels, small streams, and irrigated fields rather than large open water bodies.

Users should note that the water masks in this zone reliably capture the dominant water structures but may under-represent very narrow features. This is documented as one of the limitations of the dataset.

## Related JRC layer

The `auxiliary/JRC_occurrence_Zone1_KsarElKebir.tif` layer at the dataset root provides the Global Surface Water occurrence for this zone, derived from the Landsat archive (1984–2021). This is included as **contextual information only**, not as an independent validation reference for the 2026 flood masks.

## Citation

**Dataset DOI:** [10.5281/zenodo.22964153](https://doi.org/10.5281/zenodo.22964153)

If you use data from this zone, please cite the full dataset:

> Kzadri, M., Begdouri, A., El Fazazy, K., Qjidaa, H., Ouazzani Jamil, M.,
> Tairi, H., & Riffi, J. (2026). *SAR Morocco Flood Dataset: A georeferenced
> Sentinel-1 SAR dataset for water and flood segmentation in five Moroccan
> hydrological zones (2024–2026)* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.22964153

See the top-level `README.md` and `CITATION.cff` for the full citation format.
