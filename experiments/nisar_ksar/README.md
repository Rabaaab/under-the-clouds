# NISAR experiment — Ksar El Kebir, Morocco (Oct 25, 2026)

**Investigator:** Ikram  
**Date run:** Nov 2026  
**Data:** NISAR HH/HV (L-band), Ksar El Kebir area, scene date 25 October 2026  
**Reference:** OSM water polygons (reservoirs)

---

## Problem: direct NISAR HH/HV input fails

When NISAR HH/HV are fed directly to the U-Net (which was trained on Sentinel-1 VV/VH, C-band), the model finds **no water**.

**Root cause:** In NISAR HV (L-band), open water is only **~4 dB darker** than surrounding land. In Sentinel-1 VH (C-band) the same contrast is **~13 dB**. The model's learned weights expect a strong dark signal in the VH channel; with only 4 dB of contrast, the classifier never fires.

## Workaround (no retraining)

Synthesise a pseudo-VH from the available HH channel:

```
pseudo_VH = HH + level_shift_dB
```

where `level_shift_dB` is a small constant chosen to match the typical HH–VH offset in Sentinel-1 training data. The two-channel input becomes `[HH_dB, pseudo_VH_dB]`.

**Result vs OSM water (reservoirs):**

| Input to U-Net | IoU vs OSM water |
|---|---|
| Raw HH/HV (direct) | ~0.00 (no detections) |
| HH + synthetic VH | **0.63** |

## Caveats

- The level shift was chosen by inspection on this one scene, not optimised on a held-out set.
- OSM water is a proxy reference, not a flood map.
- The fix works for open water. Flooded vegetation is bright in L-band HV (not dark), so it will still be missed.
- **Full solution:** retrain (or fine-tune) on L-band labelled scenes.

## Files

Data and full output are in the shared Drive folder `under_the_clouds_ikram/nisar/`.  
Full write-up in `NISAR_Experiment_and_Mozambique_Ikram.pdf` (sections 1–4).

