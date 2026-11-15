# Validity: We Checked, and Here Is What It Showed

## What We Checked

We evaluated our U-Net model against a simple thresholding method (Otsu) using an independent Moroccan reference dataset from Zenodo, containing **634,522 pixels around Ksar El Kebir**.

## Results

| Method | IoU | F1-Score | Precision | Recall |
|:---|---:|---:|---:|---:|
| Otsu Threshold | 0.44 | 0.61 | 0.48 | 0.85 |
| U-Net | 0.26 | 0.41 | 0.50 | 0.34 |

## What the Results Show

The U-Net model is more conservative (stricter) in its predictions. It successfully detects the darkest water areas but misses medium-dark water pixels.

In this evaluation, the U-Net does **not outperform the Otsu thresholding method**.

## Limitations of This Evaluation

- The reference mask was generated using Otsu thresholding, which naturally favours the threshold-based method in the comparison.
- The reference is a water mask, not a verified flood map.
- The acquisition dates of the reference data have not been independently verified.
- The reference covers only part of the scene.

Therefore, these results should be interpreted as a limited evaluation of water detection rather than definitive evidence of flood-detection performance.

## Where the Model Performs Better

On the independent Sen1Floods11 benchmark, the U-Net achieves a higher Intersection over Union (IoU):

- **U-Net:** 0.687
- **Otsu Threshold:** 0.530

This indicates that the model performs better on the Sen1Floods11 benchmark, even though it does not outperform Otsu on the Moroccan reference.