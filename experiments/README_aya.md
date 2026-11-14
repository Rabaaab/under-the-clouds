# Aya evaluation files

The Zenodo SAR Morocco reference masks are semi-automatic HSBA+Otsu labels,
not expert ground truth. They may favour Otsu, cover only part of the scene,
have unknown patch dates, and show water on a date rather than flood change.

## Files in this folder

| File | Source / creation |
|---|---|
| `before.tif` | Ikram-provided real scene. Input only; do not commit. |
| `after.tif` | Ikram-provided real scene. Input only; do not commit. |
| `reference_mask.tif` | Notebook reference-mask output: 1 water, 0 not water, 255 no reference. Local raster input; not committed. |
| `reference_mask_info.json` | Notebook metadata for reference coverage, date filtering, and label source. |
| `reference_overview.png` | Notebook preview of the after scene and reference mask. |
| `predict_water.py` | CNN inference CLI; uses `utc.preprocess`, `utc.infer.predict_scene`, and the default small-component cleanup. |
| `score_event.py` | Otsu baseline scorer used on the real after scene and reference. |
| `event_metrics.json` | Output of `python experiments/score_event.py`; real Otsu metrics, CNN is null because the checkpoint is on Drive. |
| `eval_morocco_patches.py` | Zone 1/4 patch CNN-versus-Otsu evaluator with date filtering and circularity note. |
| `morocco_patches_metrics.json` | Output of the patch evaluator. Status is `not run on real data` because `data/SAR_Morocco/` is absent locally; its code was tested with fake patches. |
| `temporal_stack_NOTES.md` | States that the temporal-stack experiment is not done with only before/after scenes. |
| `HONEST_PARAGRAPH.md` | Written from `event_metrics.json`; does not claim a CNN score. |
| `README_aya.md` | This file. |

No `failure_notes_baseline.md` or `failures/` crops were present in this
`experiments/` folder during this run; none were overwritten.
The source scenes, reference raster, and preview are local evaluation data and
are not included in the code/report commit.

## Results and limitations

- The event Otsu score is water-mask agreement only on reference-covered pixels,
  not independent ground truth. Otsu is circular because it helped produce the
  reference masks.
- The reference is partial; patches without known dates may contribute, so date
  matching cannot be assumed for the mosaic.
- `run_event.py --truth` expects a **new-water/change** mask. Its truth reader
  also treats reference value 255 as positive. Do not interpret that CLI's
  metrics against this after-date water mask as valid accuracy.
- The CNN is not scored locally. Run the Colab command below with the real
  checkpoint in Colab; a random-model crop smoke test is only a code-path test.
- Zone patch results are not available locally: the requested
  `data/SAR_Morocco/` directory is missing and no 3 GB data was downloaded.

## Colab CNN command

After uploading/mounting the real checkpoint and the two scenes into the Colab
runtime, run from the cloned repository root:

```bash
PYTHONPATH=src:. python experiments/predict_water.py --tif experiments/after.tif --checkpoint outputs/unet.pt --out experiments/water_after_cnn.tif
PYTHONPATH=src:. python experiments/score_event.py --after experiments/after.tif --reference experiments/reference_mask.tif --cnn experiments/water_after_cnn.tif --out experiments/event_metrics.json
```

This scores after-date CNN water against the same partial reference as Otsu. The
reference remains semi-automatic, not expert ground truth, potentially favours
Otsu, has unknown patch dates, and is a water mask rather than a change map.
