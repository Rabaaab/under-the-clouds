# Under the Clouds

**Seeing disasters through radar: AI change detection for floods and surface change, with road and village impact.**

Built for the NASA Space Apps Challenge 2026 (Meknès, Morocco), challenge *"Dancing with the SARs"* (observe changes on Earth's surface with radar data).

> **Status: work in progress.** This README describes the plan and design. Items marked **TBD** are filled in as the project is built. Nothing here is a claimed result until it appears in the Results section with numbers.

---

## The problem

Floods, landslides and earthquakes cut roads and isolate villages. The first days matter most, but heavy cloud and rain often hide the affected area from ordinary optical satellites, and radar images are noisy and hard for non-experts to read.

## What it does

1. The user picks a real event and a location.
2. The tool loads a radar image from **before** and **after** the event.
3. A **CNN (U-Net)** labels water on each date, and the **difference** shows newly flooded land.
4. A web map shows a **before/after slider** with the detected change in color.
5. An **impact panel** reports how much road length and how many villages are affected, using OpenStreetMap.

*Pitch line: when clouds hide the disaster, radar still sees it, and AI reads it in seconds.*

## Why radar

SAR (Synthetic Aperture Radar) satellites send their own radio pulses and measure what comes back, so they work **day and night, through clouds, rain and smoke**. NISAR (NASA-ISRO) carries an **L-band** radar, a longer wavelength that reaches deeper into vegetation, and revisits the same place about every 12 days, which suits before/after comparison.

## How it works

```
before + after radar images
        |
  preprocess (speckle filter, decibels, 256x256 chips)
        |
  U-Net water segmentation on each date
        |
  change = water after, minus water before
        |
  clean-up (slope mask from NASADEM, remove tiny blobs)
        |
  intersect with OpenStreetMap roads and villages
        |
  web map: before/after slider + change layer + impact panel
```

### The model

- **Architecture:** U-Net with a **ResNet-34 encoder**, ImageNet-pretrained, first layer adapted to 2 radar channels (VV and VH).
- **Task:** per-pixel water segmentation (semantic segmentation).
- **Loss:** binary cross-entropy + Dice loss.
- **Baseline to beat:** a simple threshold on dark (water) radar values, for example Otsu's method.
- **Metrics:** IoU and F1 on a held-out set, reported for the CNN **and** the baseline.

## Data

| Data | Use | Source |
|---|---|---|
| NISAR L-band radar | Core demo input | NASA Earthdata / ASF DAAC |
| Sentinel-1 radar | Training and events before NISAR operated | ASF DAAC / Copernicus |
| Sen1Floods11 | Labeled water masks for training | Public dataset (**TBD**: confirm license and access) |
| Optical imagery (HLS / Sentinel-2) | Independent reference on cloud-free days | NASA Earthdata |
| NASADEM | Slope mask to reduce false alarms | NASA Earthdata |
| OpenStreetMap | Roads and villages for the impact layer | OpenStreetMap (not NASA data) |

**Important data note:** NISAR began operating in mid-2025, so it has no images of earlier events. Older events use Sentinel-1. The chosen event(s) and exact scenes are **TBD**.

## Results

**TBD.** Filled in after training and evaluation.

| Method | IoU | F1 | Notes |
|---|---|---|---|
| Threshold baseline | TBD | TBD | TBD |
| U-Net (ResNet-34) | TBD | TBD | TBD |

Validation plan: compare against the baseline, against a cloud-free optical water mask from a nearby date (or official emergency maps where available), and show failure cases.

## Limitations (stated up front)

- Training labels come from **C-band** (Sentinel-1) data, while NISAR is **L-band**. Open water is dark in both, but **flooded vegetation** looks different in L-band, so results there may be weaker.
- Radar shadow on steep terrain can look like water. We mask steep slopes, but errors remain.
- Built during a hackathon (about 24 hours of build time), so scope is deliberately small: one event, one main model.
- The impact layer uses OpenStreetMap, whose coverage varies by region.

## Repository structure

*Planned. Update as the code lands.*

```
under-the-clouds/
  README.md
  data/        # not committed (large files); see download notes
  notebooks/   # exploration and training
  src/         # preprocessing, model, evaluation
  app/         # web map (slider, change layer, impact panel)
  docs/        # slides, figures, notes
```

## How to run

**TBD.** Setup, data download and run commands will be added here once the code exists. Planned tools: Python, PyTorch, segmentation-models-pytorch, rasterio, geopandas, osmnx, and a web map library.

## Team

TBD (names and roles).

## AI tools disclosure

AI tools were used during the project, as required by the NASA Space Apps submission form. Specifically: an AI assistant (Claude) was used for research on challenges, for planning and design discussion, and for drafting this README. **TBD:** list any further use (for example code assistance) accurately before submitting. All results, numbers and claims in this repository must be checked by the team.

## Acknowledgements and data attribution

- NISAR is a joint mission of NASA and ISRO. NISAR data is distributed through NASA Earthdata and the Alaska Satellite Facility (ASF) DAAC.
- Contains modified Copernicus Sentinel data (**TBD**: add the year(s) used).
- NASADEM and HLS are NASA Earth science data products.
- Road and village data: © OpenStreetMap contributors.
- Created for the NASA Space Apps Challenge. This is an independent team project, not an official NASA product.

## References

- NASA Space Apps Challenge: https://www.spaceappschallenge.org
- NASA Earthdata: https://www.earthdata.nasa.gov
- ASF Vertex data search: https://search.asf.alaska.edu
- Daudt et al. (2018), *Fully Convolutional Siamese Networks for Change Detection* (background for change-detection CNNs)

## License

**TBD.** MIT is a simple choice for a hackathon project. Add a `LICENSE` file before submission.
