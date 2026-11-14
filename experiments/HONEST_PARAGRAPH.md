# Moroccan event evaluation

On the pixels covered by the available reference, the Otsu baseline has IoU
**0.442415** and F1 **0.613436** (`experiments/event_metrics.json`). These are
agreement scores against a partial reference, not independent accuracy. There
is **no CNN accuracy for the Moroccan event**: the CNN was not scored there.

The reference mask comes from the Zenodo SAR Morocco Flood Dataset and is
semi-automatic (HSBA + Otsu), not expert ground truth. Its Otsu-derived labels
may favour the Otsu baseline, so the baseline comparison is circular. The mask
covers **26.33%** of the scene (`experiments/reference_mask_info.json`) and
represents water, not a flood-change map.

The reference dates are unverified. The dataset README for Zone 1 lists GRD
10 m scenes from 27 January to 4 February 2026; the event scene is HyP3 RTC
30 m from 8 February 2026. The patch metadata lists 103 patches, all 103
without a readable date, so date agreement with the event scene cannot be
confirmed. No temporal-stack experiment was run; only before and after dates
are available.

For context only, not as Moroccan results: the model owner's summary reports
test-split IoU **0.687** for the U-Net versus **0.530** for the best threshold,
and Bolivia IoU **0.601** versus **0.586** for the naive threshold on 15 scenes.
These are other-dataset results, not independently checked here: the named
`eval_test.json` and `eval_bolivia.json` files were not present in this
checkout. The same values appear in the repository `README.md`. The test split
shares flood events with training; Bolivia is the fairer check, and its reported
lead is small.

The team also reports cleaned new-water area estimates of **51.2 km²** for the
CNN and **46.0 km²** for the baseline. These are model estimates after coastal
and thin-shape cleanup, not accuracy measurements.

Do not use `run_event.py --truth` with this reference: that command expects a
new-water change mask and treats reference value 255 as positive.
