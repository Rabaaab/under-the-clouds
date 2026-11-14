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
| Sen1Floods11 (hand-labelled subset) | Labeled water masks for training and testing | Public Google Cloud bucket (Bonafilia et al., 2020; check the dataset's terms before reuse) |
| Optical imagery (HLS / Sentinel-2) | Independent reference on cloud-free days | NASA Earthdata |
| NASADEM | Slope mask to reduce false alarms | NASA Earthdata |
| OpenStreetMap | Roads and villages for the impact layer | OpenStreetMap (not NASA data) |

**Important data note:** NISAR began operating in mid-2025, so it has no images of earlier events. Older events use Sentinel-1. The chosen event(s) and exact scenes are **TBD**.

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
- Training settings of this run (epochs, best epoch): **TBD, team to fill in from the training log.**
- This is water segmentation on a benchmark dataset. Results on a real Moroccan NISAR or Sentinel-1 event are **TBD**.

**Out-of-event test: the held-out Bolivia flood (15 scenes, an event that appears in none of train, validation or test):**

| Method | IoU | F1 | Precision | Recall |
|---|---|---|---|---|
| Otsu threshold per scene, VV (naive) | 0.586 | 0.739 | 0.691 | 0.793 |
| Otsu threshold per scene, VH (naive) | 0.496 | 0.663 | 0.540 | 0.860 |
| One tuned threshold, VV | 0.441 | 0.612 | 0.880 | 0.469 |
| One tuned threshold, VH | 0.522 | 0.686 | 0.873 | 0.565 |
| **U-Net (ResNet-34)** | **0.601** | **0.751** | **0.837** | **0.681** |

On the new event the U-Net is still the best method, but its lead shrinks: it is only 0.015 IoU above the naive per-scene VV threshold, and 15 scenes are too few to call that a real difference. The CNN is clearly better than the single global thresholds (+0.08 IoU over the best one). The global thresholds transfer badly to a new event, and the CNN transfers better. Results on a Moroccan event are **TBD**.

Further validation plan: compare against a cloud-free optical water mask from a nearby date (or official emergency maps where available) for the real event, and show failure cases.

## Limitations (stated up front)

- Training labels come from **C-band** (Sentinel-1) data, while NISAR is **L-band**. Open water is dark in both, but **flooded vegetation** looks different in L-band, so results there may be weaker.
- Radar shadow on steep terrain can look like water. We mask steep slopes, but errors remain.
- Built during a hackathon (about 24 hours of build time), so scope is deliberately small: one event, one main model.
- The impact layer uses OpenStreetMap, whose coverage varies by region.

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
  app/              # web map (before/after slider, change layer, impact panel)
  tests/
  docs/DATA.md      # how to get the real data (checklist)
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

U-Net with an ImageNet-pretrained ResNet-34 encoder, two input channels (VV and VH in dB, scaled from -50..1 dB to 0..1), BCE + Dice loss, Adam (learning rate 1e-4 by default), flips and rotations as augmentation, 256 x 256 chips. The best checkpoint is chosen by validation IoU, and the test split is used once at the end. Results are scored per scene, pooled over valid pixels, against two baselines: an Otsu threshold per scene, and one global threshold fitted on the training scenes (the strongest simple baseline).

### What has and has not been verified

- **Verified (29 unit tests pass):** preprocessing, threshold baselines, metrics, change logic, clean-up, the U-Net forward pass and loss, training, sliding-window prediction, the roads/villages impact layer, GeoTIFF reading, the web export, and the Sen1Floods11 chip and evaluation code.
- **Verified against the real dataset (small sample only):** the Sen1Floods11 file layout, units and label values were checked against the official repo and a few real chips. The downloader, chip preparation, a 2-epoch CPU training run and the evaluation script ran end to end on 3 real scenes per split. The numbers from that run are meaningless (tiny data, 2 epochs).
- **Verified:** the OpenStreetMap download worked on one small area (roads and villages near Merzouga).
- **Verified in a browser:** the web map loads the synthetic demo and the before/after slider works.
- **Not yet done:** the full training run on a GPU, the pretrained-weights path (needs internet; it has not been run here), any real NISAR or Sentinel-1 event scene, and any real accuracy numbers. The synthetic demo numbers only show that the code runs.

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
- Bonafilia, Tellman, Anderson, Issenberg (2020), *Sen1Floods11: a georeferenced dataset to train and test deep learning flood algorithms for Sentinel-1*, CVPR Workshops. https://github.com/cloudtostreet/Sen1Floods11
- Daudt et al. (2018), *Fully Convolutional Siamese Networks for Change Detection* (background for change-detection CNNs)

## License

**TBD.** MIT is a simple choice for a hackathon project. Add a `LICENSE` file before submission.
