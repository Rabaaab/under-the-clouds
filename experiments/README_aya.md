# Aya evaluation files and limits

On the part of the Ksar El Kebir scene covered by the reference (634,522 pixels),
the Otsu baseline scores IoU 0.442 and F1 0.613, and the U-Net scores IoU 0.256
and F1 0.407. The U-Net does not beat the threshold on this reference. These are
agreement scores against a partial, semi-automatic reference, not independent
accuracy.

## Files in `aya_experiments/`

| File | What it is / what creates it |
|---|---|
| `before.tif`, `after.tif` | Sentinel-1 scene inputs (team Drive, `event/`). Not committed. |
| `reference_mask.tif` | Reference raster: 1 water, 0 not water, 255 no reference. Built from the Zenodo patches in the notebook. Not committed. |
| `reference_mask_info.json` | Reference source, date filtering and coverage metadata. |
| `reference_overview.png` | After scene with the reference overlaid. |
| `predict_water.py` | CNN prediction CLI (repository preprocessing, inference and cleanup). Run in Colab on the after scene. |
| `score_event.py` | Scores Otsu and, with `--cnn`, the U-Net against the reference. |
| `event_metrics.json` | Output of `score_event.py`: Otsu and U-Net results on the reference. |
| `water_after_cnn.tif` | U-Net water map of the after scene (276,857 water pixels). Not committed if over 20 MB. |
| `diagnostics.json` | dB statistics of agreement and disagreement, and how closely the reference follows the Otsu threshold. |
| `failure_notes.md`, `failures_otsu/`, `failures_cnn/` | Failure crops and notes for the Otsu baseline and the U-Net. |
| `eval_morocco_patches.py` | Script for CNN and Otsu scores on dated Zone 1 and Zone 4 patches. Not run on real data. |
| `morocco_patches_metrics.json` | Status output of the patch evaluator. No real-data evaluation was run. |
| `temporal_stack_NOTES.md` | Notes that a temporal-stack experiment was not done. |
| `HONEST_PARAGRAPH.md`, `NOTES.md`, `CREDITS.txt` | Result summary with limits, event facts and sources, and the dataset credit. |
| `README_aya.md` | This file. |

## How the Moroccan scores were produced (Colab, 14 Nov 2026)

    PYTHONPATH=src:. python experiments/predict_water.py --tif outputs/after.tif --checkpoint outputs/unet.pt --out experiments/water_after_cnn.tif
    PYTHONPATH=src:. python experiments/score_event.py --after outputs/after.tif --reference experiments/reference_mask.tif --cnn experiments/water_after_cnn.tif --out experiments/event_metrics.json

`predict_water.py` used small-object removal at 20 pixels and no coastal cleanup.
The Otsu threshold on the after VV was -14.40 dB.

## Model (as described by its owner)

According to the model owner, the checkpoint is a U-Net with a ResNet-34
encoder, two dB input channels (VV then VH), and one water-probability output
channel. It has about 24.4 million parameters (about 98 MB), and its best
checkpoint is from epoch index 29. The stored score is 0.676; its
interpretation as validation IoU is unconfirmed. The owner says it was trained
on the hand-labelled Sen1Floods11 subset in Google Colab, with 252 training
scenes in that split. The checkpoint was loaded and run on the Moroccan after
scene for this report; the architecture details above were not checked here.

The owner's summary reports test-split IoU 0.687 (U-Net) versus 0.530 (best
threshold) and Bolivia IoU 0.601 versus 0.586 (naive threshold, 15 scenes).
Those are other-dataset results, not Moroccan results. The `eval_valid.json`,
`eval_test.json` and `eval_bolivia.json` files were not present in this
checkout, so these values could not be checked against those files. The same
values appear in the repository `README.md`. The test split shares flood events
with training; Bolivia is the fairer check, and the reported lead there is
small. On the Moroccan reference this advantage did not carry over.

## Moroccan event results and limitations

| Method | IoU | F1 | Precision | Recall |
|---|---|---|---|---|
| Otsu baseline | 0.442 | 0.613 | 0.480 | 0.849 |
| U-Net | 0.256 | 0.407 | 0.502 | 0.343 |

Both were scored on the same 634,522 pixels (`event_metrics.json`). The U-Net
acts like a stricter dark-pixel rule: the water it shares with the reference
has a median of -23.6 dB, and the reference water it missed has a median of
-19.5 dB. Its extra detections are very dark (median -22.6 dB), so some may be
water the reference does not label; this is not confirmed (`diagnostics.json`).

The reference is from the Zenodo SAR Morocco Flood Dataset (DOI
10.5281/zenodo.22964153). It is semi-automatic (HSBA + Otsu), not expert ground
truth. 85.1% of its water pixels lie below the scene's Otsu threshold, so it
likely favours the Otsu baseline and the comparison is partly circular. It
covers 26.33% of the scene (`reference_mask_info.json`) and is a water mask,
not a flood-change map.

Reference dates are unverified. The dataset README for Zone 1 lists GRD 10 m
scenes from 27 January to 4 February 2026; the event scene is HyP3 RTC 30 m
from 8 February 2026. The reference metadata records 103 patches (check this
count against the metadata CSV), all without a readable date, so a date match
cannot be confirmed. No temporal-stack experiment was run. The Zone 1 and
Zone 4 patch evaluator was not run on real data.

The team-reported cleaned new-water estimates are 51.2 km² for the CNN and
46.0 km² for the baseline. They come from `run_event.py` (after-minus-before
change maps with coastal and thin-shape cleanup), a different output from the
scored water-after map. They are model estimates, not accuracy.

Do not use `run_event.py --truth` with this reference. That option expects a
new-water change mask and treats 255 as positive.
