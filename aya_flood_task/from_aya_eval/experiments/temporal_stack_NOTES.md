# Temporal-stack experiment: not done

No temporal-stack experiment was run, and no temporal-stack accuracy is claimed.

Why:
- The Moroccan event has two processed Sentinel-1 dates so far: before (21 January 2026) and after (8 February 2026). A temporal stack needs 4 to 6 dates.
- The existing model expects a two-channel VV/VH image from one date. Stacking dates would change the model input and need a separately designed, trained and validated model.
- We have no labelled time series to train or check such a model. Sen1Floods11 has one image per place, and the Zenodo dataset has composites, not repeat passes.

What the team does instead (Step 5 of the plan): the same 2D U-Net is run on each Sentinel-1 pass to plot flooded area over time. This is a time-lapse of a single-date model, not a temporal-stack model. It is only shown if at least 6 passes are processed by Sunday 12:00.

Moroccan scoring (single date, 8 February 2026): the U-Net was run on the after scene in Colab and scored against the Zenodo reference (IoU 0.256, F1 0.407; Otsu baseline IoU 0.442, F1 0.613). The reference limitations are listed in the evaluation text.

Future work: build a data cube from the repeat passes, make labels, train a 3D CNN or ConvLSTM, and compare it fairly with the 2D model. Claim it only if it wins.
