# NISAR experiment — Mozambique flood (Limpopo, January 2026)

**Investigator:** Ikram  
**Date run:** Nov 2026  
**Data:** NISAR HH/HV (L-band, pre-calibration / early release), Limpopo River basin  
**Reference:** Copernicus EMS flood map, EMSR857, AOI 06, image date 18 January 2026

---

## Setup

| Item | Value |
|---|---|
| Satellite | NISAR (L-band, HH + HV) |
| Before scene | 5 January 2026 |
| During scene | 17 January 2026 |
| Reference map | Copernicus EMS EMSR857, AOI 06, 18 Jan 2026 |
| Workaround used | HH + synthetic VH (settings from Ksar El Kebir, **not tuned on Mozambique**) |

---

## Results

| Metric | Value |
|---|---|
| Precision | **0.96** (96 % of flagged pixels confirmed as flood by Copernicus EMS) |
| Recall | ~0.33 (finds about one third of the total flood extent) |
| F1 | **0.51** |
| IoU | **0.34** |

---

## Why recall is low

1. **Pre-existing water:** 11.5 km² of the flooded area was already water on the January 5 before-scene. Change detection cannot recover it.
2. **Flooded vegetation:** L-band HV backscatter increases (double-bounce), so flooded vegetation appears *brighter* than land, not darker. The model was trained to find dark pixels and misses this class.
3. **Model not tuned for Mozambique:** the level-shift workaround was locked to Ksar El Kebir settings.

---

## Honest framing

> This is a **validated workaround, not a full solution.** The 96 % precision shows the approach is not generating random false alarms. The low recall shows it misses a large part of the flood, particularly flooded vegetation and water that was present before the event.

**Next step:** retrain (or fine-tune) with L-band labelled scenes, including flooded-vegetation examples.

---

## Important data note

The NISAR products used here are **early / pre-calibration releases**. Absolute backscatter values may shift in the final product, so results should be treated as indicative.

---

## Files

Data and full output are in the shared Drive folder `under_the_clouds_ikram/nisar_mozambique/`.  
Full write-up in `NISAR_Experiment_and_Mozambique_Ikram.pdf` (section 5 and tables).

