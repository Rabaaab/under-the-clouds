# Aya evaluation files and limits

There is **no CNN accuracy for the Moroccan event**: the CNN was not scored
there. The available Moroccan number is the Otsu baseline's agreement with a
partial, semi-automatic reference, not independent accuracy.

## Files in `experiments/`

| File | What it is / what creates it |
|---|---|
| `before.tif` | Local before-event Sentinel-1 scene input. Not committed. |
| `after.tif` | Local after-event Sentinel-1 scene input. Not committed. |
| `reference_mask.tif` | Local notebook reference raster: 1 water, 0 not water, 255 no reference. Not committed. |
| `reference_mask_info.json` | Notebook-generated reference source, date-filtering, and coverage metadata. |
| `reference_overview.png` | Notebook-generated visualization of the after scene and reference. |
| `predict_water.py` | CNN prediction CLI; uses the repository preprocessing, inference, and cleanup code. It was not run on the Moroccan scene for this report. |
| `score_event.py` | Scores the Otsu baseline against the event reference; supports optional CNN input, which was not used for this report. |
| `event_metrics.json` | Output of `python experiments/score_event.py`; contains the Moroccan Otsu result and `"cnn": null`. |
| `eval_morocco_patches.py` | Script for CNN/Otsu scores on dated Zone 1 and Zone 4 patches. |
| `morocco_patches_metrics.json` | Patch-evaluation status output; real-data evaluation was not run because the local `data/SAR_Morocco/` directory was absent. |
| `temporal_stack_NOTES.md` | Notes that a temporal-stack experiment was not done. |
| `HONEST_PARAGRAPH.md` | Human-readable event result and limitations, including results from other datasets clearly marked as such. |
| `README_aya.md` | This inventory and summary of model details and evaluation limits. |
| `__pycache__/eval_morocco_patches.cpython-312.pyc` | Runtime-generated Python bytecode cache; not a report or source deliverable. |
| `__pycache__/predict_water.cpython-312.pyc` | Runtime-generated Python bytecode cache; not a report or source deliverable. |
| `__pycache__/score_event.cpython-312.pyc` | Runtime-generated Python bytecode cache; not a report or source deliverable. |

`failure_notes_baseline.md` and the `failures/` crops were not present in this
checkout's `experiments/` inventory, so they are not described or modified here.

## Model (as described by its owner)

The checkpoint itself is not available in this checkout and was not loaded or
run. According to the model owner, it is a U-Net with a ResNet-34 encoder,
two dB input channels (VV then VH), and one water-probability output channel.
It has about 24.4 million parameters (about 98 MB), and its best checkpoint is
from the 30th epoch (epoch index 29). The stored score is 0.676; its
interpretation as validation IoU is unconfirmed.

The owner says the model was trained on the hand-labelled Sen1Floods11 subset
in Google Colab, with 252 training scenes in that split. The owner's summary
reports test-split IoU 0.687 (U-Net) versus 0.530 (best threshold) and Bolivia
IoU 0.601 versus 0.586 (naive threshold, 15 scenes). Those are other-dataset
results, not Moroccan results. The named `eval_valid.json`, `eval_test.json`,
and `eval_bolivia.json` files were not present in this checkout, so these
summary values could not be checked against those files. The same test and
Bolivia values appear in the repository `README.md`. The test split shares
flood events with training; Bolivia is the fairer check, and the reported lead
there is small.

## Moroccan event results and limitations

`event_metrics.json` reports Otsu baseline IoU **0.442415** and F1 **0.613436**
on its reference-covered evaluation pixels. It reports `"cnn": null`: there is
no CNN accuracy on this event.

The reference is from the Zenodo SAR Morocco Flood Dataset (DOI
10.5281/zenodo.22964153). It is semi-automatic (HSBA + Otsu), not expert ground
truth, and may favour the Otsu baseline; therefore the Otsu score is circular.
It covers **26.33%** of the scene (`reference_mask_info.json`) and is a water
mask, not a flood-change map.

Reference dates are unverified. The dataset README for Zone 1 lists GRD 10 m
scenes from 27 January to 4 February 2026; the event scene is HyP3 RTC 30 m
from 8 February 2026. The reference metadata records 103 patches, all 103
without a readable date, so a date match cannot be confirmed. No
temporal-stack experiment was run; only before and after dates are available.
The Zone 1/4 patch evaluator did not run on real data locally because
`data/SAR_Morocco/` was absent.

The team-reported cleaned new-water estimates are 51.2 km² for the CNN and
46.0 km² for the baseline. They are model estimates, not accuracy.

Do not use `run_event.py --truth` with this reference. That option expects a
new-water change mask and treats 255 as positive.
