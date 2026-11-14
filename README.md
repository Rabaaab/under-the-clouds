# Under the Clouds

**Seeing disasters through radar: AI change detection for floods and surface change, with road and village impact.**

Built for the NASA Space Apps Challenge 2026 (Meknès, Morocco), challenge *"Dancing with the SARs"* (observe changes on Earth's surface with radar data).

> **Status: hackathon prototype.** The model is trained and scored on a public benchmark, and it has been run on a real flood in Morocco (the Loukkos plain near Ksar El Kebir, January to February 2026). There is **no accuracy score for the Moroccan event yet**, because we have no reference flood map for it. The Moroccan numbers below are model estimates, not verified measurements. Items marked **TBD** are not done.

**Live map:** https://rabaaab.github.io/under-the-clouds/app/ opens on a spinning Earth built from NASA Blue Marble and Black Marble imagery. Click the orange marker (live case: Morocco 2026) or any white marker (benchmark floods in 10 other countries). Go straight to the map with https://rabaaab.github.io/under-the-clouds/app/#map

**Cloud test:** on the live map, press "Cloud test" to compare NASA's own optical satellite image of 8 Feb 2026 (MODIS Terra true colour, via NASA GIBS) with our Sentinel-1 radar and the flooded area the model finds. Over Ksar El Kebir the optical image is covered by cloud on that day, the radar is not. This is a visual comparison for one place and one date, not a measurement of how often clouds hide floods.

**Radar change (not only floods):** the optional "Radar change" layer shows how much the radar brightness moved between the two dates (blue: darker, gold: brighter), for any kind of surface change. It is not a flood map and is not classified by the model: wind on open water, crops and building work also change it. Only the flood classifier is flood-specific. Other disasters (landslides, wildfire, oil spills, deforestation) are the roadmap, not built and not tested, because they need labelled examples we do not have.

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
| NISAR L-band radar | Planned input. **Not used for the Morocco event**: a search of ASF Vertex found no NISAR data for Jan to Feb 2026 | NASA Earthdata / ASF DAAC |
| Sentinel-1 radar (IW GRD, VV+VH) | Training data (via Sen1Floods11) and the Morocco flood event, processed to RTC by ASF HyP3 | ASF DAAC / Copernicus (ESA) |
| Sen1Floods11 (hand-labelled subset) | Labeled water masks for training and testing | Public Google Cloud bucket (Bonafilia et al., 2020; check the dataset's terms before reuse) |
| Optical imagery (HLS / Sentinel-2) | Independent reference on cloud-free days | NASA Earthdata |
| NASADEM | Slope mask to reduce false alarms | NASA Earthdata |
| OpenStreetMap | Roads and villages for the impact layer | OpenStreetMap (not NASA data) |

**Important data note:** NISAR public data starts late in 2025, so it does not cover the January to February 2026 Moroccan flood. We therefore used Sentinel-1, which has the same VV and VH polarisations as our training data. The model has not been tested on real NISAR data.

## Results

**Water segmentation on the Sen1Floods11 hand-labelled test split (90 scenes, scored per pixel over valid pixels):**

| Method | IoU | F1 | Precision | Recall |
|---|---|---|---|---|
| Otsu threshold per scene, VV (naive) | 0.306 | 0.469 | 0.355 | 0.691 |
| Otsu threshold per scene, VH (naive) | 0.250 | 0.400 | 0.277 | 0.723 |
| One tuned threshold, VV | 0.464 | 0.634 | 0.771 | 0.538 |
| One tuned threshold, VH (**best simple baseline**) | 0.530 | 0.692 | 0.754 | 0.640 |
| **U-Net (ResNet-34)** | **0.687** | **0.814** | **0.837** | **0.793** |

How to read this:
- The tuned thresholds (-16.75 dB for VV, -23.75 dB for VH) were fitted on the 252 training scenes. The naive Otsu method gave an implausible threshold in 33 (VV) and 10 (VH) of the 90 scenes, so a fixed value was used there.
- **Caution:** the train, validation and test splits contain scenes from the same ten flood events, so this test is easier than a new region. The out-of-event Bolivia test below is the fairer check.
- Training settings of this run: best checkpoint at epoch 29 (validation IoU about 0.68, read from the saved model file); learning rate 1e-4 and batch size 16 (the notebook defaults); trained for 30 epochs in total.
- This is water segmentation on a benchmark dataset. The Moroccan event is described further down; it has no accuracy score yet.

**Out-of-event test: the held-out Bolivia flood (15 scenes, an event that appears in none of train, validation or test):**

| Method | IoU | F1 | Precision | Recall |
|---|---|---|---|---|
| Otsu threshold per scene, VV (naive) | 0.586 | 0.739 | 0.691 | 0.793 |
| Otsu threshold per scene, VH (naive) | 0.496 | 0.663 | 0.540 | 0.860 |
| One tuned threshold, VV | 0.441 | 0.612 | 0.880 | 0.469 |
| One tuned threshold, VH | 0.522 | 0.686 | 0.873 | 0.565 |
| **U-Net (ResNet-34)** | **0.601** | **0.751** | **0.837** | **0.681** |

On the new event the U-Net is still the best method, but its lead shrinks: it is only 0.015 IoU above the naive per-scene VV threshold, and 15 scenes are too few to call that a real difference. The CNN is clearly better than the single global thresholds (+0.08 IoU over the best one). The global thresholds transfer badly to a new event, and the CNN transfers better.

### Accuracy by flood, in 11 countries

Same model, scored per flood on the Sen1Floods11 hand-labelled scenes (90 test scenes from 10 floods, plus the held-out Bolivia flood). The model beats the best simple threshold on every flood. Pakistan is the weakest.

| Flood | Scenes | U-Net IoU | Best simple threshold IoU (VH) | U-Net F1 |
|---|---|---|---|---|
| Nigeria | 4 | 0.893 | 0.709 | 0.944 |
| Sri Lanka | 9 | 0.838 | 0.705 | 0.912 |
| Mekong Delta | 6 | 0.834 | 0.720 | 0.910 |
| Spain | 6 | 0.735 | 0.638 | 0.848 |
| India | 14 | 0.693 | 0.585 | 0.818 |
| Paraguay | 14 | 0.651 | 0.469 | 0.788 |
| Bolivia (held out of training) | 15 | 0.601 | 0.522 | 0.751 |
| USA | 14 | 0.595 | 0.387 | 0.746 |
| Somalia | 6 | 0.582 | 0.251 | 0.735 |
| Ghana | 11 | 0.559 | 0.450 | 0.717 |
| Pakistan | 6 | 0.274 | 0.148 | 0.430 |

The test scenes come from the same floods as the training scenes (different pictures), so the held-out Bolivia flood is the fairer check. The simple threshold is one global VH cut-off (-23.75 dB) fitted on the training scenes. The web app shows a typical scene (the median-scoring one) for each flood, not the best one.

### Real event: the Loukkos floods near Ksar El Kebir, Morocco (no accuracy score yet)

| Item | Value |
|---|---|
| Satellite | Sentinel-1 IW GRD, VV+VH, ascending, path 147 / frame 110 |
| Before | 21 January 2026 |
| After | 8 February 2026 |
| Processing | ASF HyP3 On Demand RTC (30 m, sigma0, power) |
| Area | longitude -6.25 to -5.75, latitude 34.90 to 35.25 (Larache to Ksar El Kebir) |
| Prepared scene | 1855 x 1299 pixels, EPSG:4326 |
| Roads and villages | OpenStreetMap: 10,092 road segments, 321 places |

Newly flooded area found by each method, and the effect of the clean-up step:

| Clean-up step | Threshold baseline (km²) | U-Net (km²) |
|---|---|---|
| None (raw) | 55.1 | 66.7 |
| Land mask with a 300 m coastal margin | 55.0 | 58.5 |
| Land mask with a 1 km margin, plus removal of shapes below about 120 m (vector test) | 46.0 | 48.9 |
| The same clean-up built into the pipeline (raster, below about 150 m) | - | 51.2 |

Most of the U-Net's extra raw area was false water on the sea and the coastline, plus some straight lines where image tiles meet. After clean-up the two methods give similar totals. The U-Net maps the northern flooded fields as solid shapes, while the baseline finds more flooding in the south, near Ksar El Kebir. Without a reference map we cannot say which is closer to reality.

Impact on roads and places (OpenStreetMap):

| Flood used | New water | Road length in flooded areas | Places within 500 m |
|---|---|---|---|
| Baseline, cleaned (vector) | 46.0 km² | 32.2 km | 33 |
| Baseline, cleaned in the pipeline (the "Threshold baseline" view on the web map) | 48.6 km² | 34.8 km (78 segments) | 34 |
| U-Net, cleaned (vector) | 48.9 km² | 21.3 km | 32 |
| U-Net, cleaned in the pipeline (shown on the web map) | 51.2 km² | 22.9 km (60 segments) | 35 |

We say "road in flooded areas" and "places within 500 m of new water". We do not say "roads cut" or "villages flooded", because we have not checked whether any road is actually impassable. About 1 to 2 of the 35 places sit next to known false alarms.

**What these Moroccan numbers are not:** they are model outputs, not measured accuracy. Taking out thin shapes also removes some real narrow flooding (ditches and channels), so the true flooded area is probably between the cleaned and the raw values.

Further validation plan: score the result against a reference flood map for the same dates (`--truth` in `scripts/run_event.py`), or against a cloud-free optical water mask from a nearby date, and show failure cases. **TBD**, waiting for a reference map.

### NISAR experiments (supplementary, not part of the main pipeline)

We ran two additional experiments with real NISAR L-band data after the main pipeline was complete. Full details are in [`experiments/`](experiments/README.md) and in `NISAR_Experiment_and_Mozambique_Ikram.pdf`.

**Experiment 1 — Ksar El Kebir, NISAR Oct 25 2026 (open-water workaround)**

Feeding NISAR HH/HV directly to the U-Net (trained on Sentinel-1 C-band VV/VH) finds no water. The cause is the much smaller radar contrast of water in L-band: about 4 dB darker in NISAR HV, versus 13 dB in Sentinel-1 VH. Fix without retraining: replace VH with a synthetic channel derived from HH plus a constant level shift. With this input the model finds the reservoirs around Ksar El Kebir with IoU 0.63 versus OpenStreetMap water polygons.

**Experiment 2 — Mozambique, Limpopo flood (Jan 2026), validated against Copernicus EMS**

| Item | Value |
|---|---|
| Satellite | NISAR (L-band HH/HV, pre-calibration / early release) |
| Before scene | 5 January 2026 |
| During scene | 17 January 2026 |
| Reference | Copernicus EMS EMSR857, AOI 06 (image date 18 Jan 2026) |
| Workaround | HH + synthetic VH, settings from Ksar El Kebir, **not tuned on Mozambique** |

| Metric | Value |
|---|---|
| Precision | **0.96** — almost everything the model marks as flood is confirmed by Copernicus |
| Recall | ~0.33 — finds about one third of the total flood extent |
| F1 | **0.51** |
| IoU | **0.34** |

Why recall is low: 11.5 km² of flood was already present on 5 January (change detection cannot recover it), and flooded vegetation is bright in L-band HV (not dark), so the model trained on C-band misses it.

**Honest framing:** this is a validated workaround, not a full solution. The 96 % precision shows the model is not generating random false alarms on a new sensor and a new continent. The low recall shows it misses a large part of the flood. The next step is retraining or fine-tuning with L-band labelled scenes, including flooded-vegetation examples.

> **Data note:** the NISAR products used here are early / pre-calibration releases. Absolute backscatter values may shift in the final product; treat these numbers as indicative.

## Limitations (stated up front)

- Training labels come from **C-band** (Sentinel-1) data, while NISAR is **L-band**. Open water is dark in both, but **flooded vegetation** is bright in L-band HV (double-bounce), so the model misses it. Tested on a real NISAR scene (Mozambique, Limpopo Jan 2026): precision 0.96 but recall only ~0.33. Full solution requires retraining on L-band labels. See [`experiments/`](experiments/README.md).
- Radar shadow on steep terrain can look like water. We mask steep slopes, but errors remain.
- Built during a hackathon (about 24 hours of build time), so scope is deliberately small: one event, one main model.
- The impact layer uses OpenStreetMap, whose coverage varies by region.
- **No accuracy score for Morocco.** The benchmark results above do not prove the same performance on the Moroccan flood.
- **Known false alarms on the Moroccan map:** a small blob near the top-right corner (about 35.24 N, -5.77 E) and a short coastal line near Larache. The land mask uses Natural Earth, which is only accurate to a few hundred metres, so we use a 1 km coastal margin.
- The clean-up settings (coastal margin and thin-shape removal) were chosen by looking at the result, not tuned against a reference.
- Flooded vegetation and very shallow water look grey, not black, in radar, so both methods can miss them.

## Repository structure

```
under-the-clouds/
  README.md
  requirements.txt
  pytest.ini
  src/utc/
    preprocess.py   # dB, speckle filter, normalisation, tiling
    baseline.py     # Otsu threshold water mask (the baseline to beat)
    model.py        # U-Net (ResNet-34) + BCE/Dice loss
    dataset.py      # chips and the PyTorch dataset
    sen1floods11.py # download, chips, scene-level evaluation (CNN vs baselines)
    osm.py          # roads and villages from OpenStreetMap
    prepare.py      # radar GeoTIFFs (e.g. HyP3) -> same-grid scenes for run_event
    train.py        # training loop
    infer.py        # sliding-window prediction over a scene
    change.py       # new water = after minus before
    postprocess.py  # remove small blobs, mask steep slopes
    metrics.py      # IoU, F1, precision, recall
    impact.py       # roads and villages affected (+ OSM loader, untested)
    pipeline.py     # end-to-end run
    synthetic.py    # fake radar scenes with a known flood (for tests/demo)
    export_web.py   # writes the files the web map reads
    demo.py, event.py
  scripts/          # run_demo.py, run_event.py, train.py, sen1floods11.py, fetch_osm.py, prepare_scene.py
  notebooks/        # train_colab.ipynb (Colab / Kaggle GPU training)
  app/              # web map: before/after slider, Sentinel-1 timeline, flood layer, roads and places
    data/baseline/  # threshold-baseline result for the "Threshold baseline" view
    earth/          # textures for the Earth first screen (generated from Natural Earth outlines)
  tests/
  docs/DATA.md      # how to get the real data (checklist)
  experiments/      # supplementary NISAR experiments (Ikram): nisar_ksar/, nisar_mozambique/
  data/, outputs/   # not committed
```

## How to run

```bash
pip install -r requirements.txt
python -m pytest                              # unit tests
python scripts/run_demo.py --out app/data     # end-to-end run on SYNTHETIC data
python -m http.server -d app 8000             # then open http://localhost:8000
```

For real data see [docs/DATA.md](docs/DATA.md). Training and real-event commands:

```bash
# 1. Training data: Sen1Floods11 hand-labelled set (about 650 MB), cut into chips
python scripts/sen1floods11.py download --root data/sen1floods11
python scripts/sen1floods11.py prepare  --root data/sen1floods11 --out data/chips

# 2. Train (use a GPU: see notebooks/train_colab.ipynb for Colab / Kaggle)
python scripts/train.py --train-dir data/chips/train --val-dir data/chips/valid --epochs 30 --out outputs/unet.pt

# 3. Compare the CNN with threshold baselines on the held-out test scenes
python scripts/sen1floods11.py evaluate --root data/sen1floods11 --split test --checkpoint outputs/unet.pt

# 3b. Harder test: a flood event (Bolivia) that is in none of train/valid/test
python scripts/sen1floods11.py download --root data/sen1floods11 --splits bolivia
python scripts/sen1floods11.py evaluate --root data/sen1floods11 --split bolivia --checkpoint outputs/unet.pt

# 4. Roads and villages for the event area (needs internet and `pip install osmnx`)
python scripts/fetch_osm.py --bbox WEST SOUTH EAST NORTH --out data/osm

# 4b. Turn per-polarisation radar GeoTIFFs (e.g. ASF HyP3 RTC) into same-grid scenes
python scripts/prepare_scene.py --before-vv B_VV.tif --before-vh B_VH.tif --after-vv A_VV.tif --after-vh A_VH.tif \
    --bbox WEST SOUTH EAST NORTH --res 30 --unit power --out data/event

# 5. Run an event
python scripts/run_event.py --before before.tif --after after.tif --linear --checkpoint outputs/unet.pt \
    --roads data/osm/roads.geojson --villages data/osm/villages.geojson --out app/data
```

### How the model is trained

We trained a U-Net with a ResNet-34 encoder (starting from ImageNet weights) on the public Sen1Floods11 dataset: 911 training chips of 256 x 256 pixels cut from 252 hand-labelled Sentinel-1 radar scenes, with the VV and VH radar bands as input and water / not-water labels as the target. Training ran for 30 epochs on a Google Colab GPU with the Adam optimiser (learning rate 1e-4, batch size 16), a combined cross-entropy and Dice loss to cope with the small share of water pixels, and flips and rotations as augmentation, and we kept the best checkpoint (epoch 29, validation IoU about 0.68). We then scored it on 90 held-out test scenes and on 15 scenes from a flood event it never saw (Bolivia), always against simple threshold baselines, and we report the results as they came out, including the smaller lead on the new event.

**Details:** U-Net with an ImageNet-pretrained ResNet-34 encoder, two input channels (VV and VH in dB, scaled from -50..1 dB to 0..1), BCE + Dice loss, Adam (learning rate 1e-4 by default), flips and rotations as augmentation, 256 x 256 chips. The best checkpoint is chosen by validation IoU, and the test split is used once at the end. Results are scored per scene, pooled over valid pixels, against two baselines: an Otsu threshold per scene, and one global threshold fitted on the training scenes (the strongest simple baseline).

### What has and has not been verified

- **Verified (35 unit tests pass):** preprocessing, threshold baselines, metrics, change logic, clean-up, the U-Net forward pass and loss, training, sliding-window prediction, the roads/villages impact layer, GeoTIFF reading, the web export, and the Sen1Floods11 chip and evaluation code.
- **Verified against the real dataset (small sample only):** the Sen1Floods11 file layout, units and label values were checked against the official repo and a few real chips. The downloader, chip preparation, a 2-epoch CPU training run and the evaluation script ran end to end on 3 real scenes per split. The numbers from that run are meaningless (tiny data, 2 epochs).
- **Verified:** the OpenStreetMap download worked on two areas (near Merzouga, and the Ksar El Kebir area for the Moroccan event).
- **Verified:** the full training run on a Colab GPU, the benchmark and Bolivia scoring, and an end-to-end run on a real Sentinel-1 pair for the Moroccan flood. The web map shows that real result.
- **Not yet done:** an accuracy score on the Moroccan event (needs a reference flood map), any test on real NISAR data, and a check of whether the flagged roads are actually impassable.

## Team

Team "Lunar", NASA Space Apps Challenge 2026, Meknès:

- **Rabab** (repo owner): the model, training, evaluation, the pipeline and this documentation.
- **Ikram**: the real Moroccan scenes, ASF processing, running the model on them, the coastal clean-up, the road and village impact, and the web map data.
- **Aya**: the reference flood map for validation (in progress).

## AI tools disclosure

AI tools were used during the project, as required by the NASA Space Apps submission form. Claude (Anthropic) was used for: research on challenges and datasets, writing and debugging code and tests, the Colab training notebook, drafting documentation such as this README, and Claude Design for the logo and interface mockups. The team ran the code, trained the model on a Colab GPU, ran the Moroccan scenes and checked the results. No NASA logos, insignia or branding were used or generated. All results, numbers and claims in this repository must be checked by the team.

## Acknowledgements and data attribution

- NISAR is a joint mission of NASA and ISRO. NISAR data is distributed through NASA Earthdata and the Alaska Satellite Facility (ASF) DAAC. We did not use NISAR data for the Moroccan event.
- Contains modified Copernicus Sentinel data (2026), processed by ASF DAAC HyP3.
- Land outline for the coastal mask: Natural Earth.
- Earth textures and the optional basemaps: NASA Blue Marble (Next Generation, with bathymetry), VIIRS Black Marble 2016, VIIRS Suomi NPP true colour of 8 Feb 2026 (the cloud layer on the Earth) and MODIS Terra true colour, via NASA GIBS (Global Imagery Browse Services) and NASA Visible Earth. We acknowledge the use of imagery provided by services from NASA's GIBS, part of NASA's Earth Science Data and Information System (ESDIS).
- Flood benchmark: Sen1Floods11 (Bonafilia et al., 2020), Sentinel-1 scenes with hand-labelled water.
- NASADEM and HLS are NASA Earth science data products.
- Road and village data: © OpenStreetMap contributors.
- Created for the NASA Space Apps Challenge. This is an independent team project, not an official NASA product.

## References

- NASA Space Apps Challenge: https://www.spaceappschallenge.org
- NASA Earthdata: https://www.earthdata.nasa.gov
- ASF Vertex data search: https://search.asf.alaska.edu
- Bonafilia, Tellman, Anderson, Issenberg (2020), *Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1*, CVPR Workshops. https://github.com/cloudtostreet/Sen1Floods11
- Daudt et al. (2018), *Fully Convolutional Siamese Networks for Change Detection* (background for change-detection CNNs)

## License

**TBD.** MIT is a simple choice for a hackathon project. Add a `LICENSE` file before submission.
