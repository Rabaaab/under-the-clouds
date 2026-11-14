# Honest event evaluation

On the reference-covered pixels of the after scene, the Otsu baseline scored
IoU **0.442415** and F1 **0.613436**. These values come from
`event_metrics.json` and measure agreement with the available reference labels,
not independent accuracy.

The CNN was **not scored locally** because `outputs/unet.pt` is on Drive and was
not available in this checkout. A randomly initialized model was used only for
a small crop smoke test; that output is not a CNN result.

The reference comes from the Zenodo SAR Morocco Flood Dataset and uses
semi-automatic HSBA + Otsu masks. It is not expert ground truth and may favour
the Otsu baseline. The mask covers only part of the scene; patch dates are
unknown; and it represents water on a date, not a flood-change map. The Otsu
score is therefore circular and should not be read as an independent
validation result.
