# Moroccan check: U-Net vs Otsu threshold

Scene: Ksar El Kebir, Sentinel-1 VV/VH, 8 Feb 2026. Reference: Zenodo SAR Morocco Flood Dataset (DOI 10.5281/zenodo.22964153).
Both methods were scored on the same 634,522 pixels (26.33% of the scene, only where the reference exists). Source: event_metrics.json, diagnostics.json.

| Method | TP | FP | FN | TN | IoU | F1 | Precision | Recall |
|---|---|---|---|---|---|---|---|---|
| Otsu threshold (-14.4 dB) | 26,494 | 28,697 | 4,694 | 574,637 | 0.442 | 0.613 | 0.480 | 0.849 |
| U-Net (ResNet-34) | 10,682 | 10,611 | 20,506 | 592,723 | 0.256 | 0.407 | 0.502 | 0.343 |

Reference water is about 5% of the scored pixels (31,188 pixels), so overall pixel accuracy is not informative.

## What it shows
- The U-Net does not beat the threshold on this reference, and we do not claim it does.
- Precision is similar. The difference is recall: the U-Net finds 34% of the reference water, Otsu finds 85%.
- The U-Net acts like a stricter dark-pixel rule. Water both agree on has a median of -23.6 dB; the reference water the U-Net missed has a median of -19.5 dB. The U-Net's extra detections are very dark (median -22.6 dB), so some may be real water the reference does not label (not confirmed).

## Why the reference probably favours the threshold
- The dataset documentation says the masks were made with HSBA and Otsu thresholding plus visual checks.
- In our scene, 85.1% of the reference water is darker than the scene's Otsu line (about -14.4 dB), and 95.2% of the reference non-water is brighter than it. A threshold at that level reproduces the reference closely, which is what Otsu recall of 0.849 shows.
- This is consistent with a threshold-based reference, but it does not prove how large the bias is: real water is also dark, and the dataset's own Otsu thresholds were computed on other images and dates.

## What it does not show
- It is not independent accuracy: the labels are semi-automatic, not expert ground truth.
- It is a water mask, not a flood-change map, and it covers only part of the scene.
- Patch dates are unverified (no readable dates; the Zone 1 README lists 10 m GRD scenes from 27 Jan to 4 Feb 2026, our scene is from 8 Feb 2026), so the reference may not match the flood day.
- It says nothing about the benchmark results (IoU 0.687 on the Sen1Floods11 test split, 0.601 on Bolivia), which are separate datasets.
- The cleaned new-water estimates (46.0 km2 baseline, 51.2 km2 U-Net) come from a different output (run_event.py, before-after change with clean-up) and are estimates, not accuracy.