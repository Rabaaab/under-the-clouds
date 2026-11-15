# Experiments

Supplementary experiments run during the NASA Space Apps 2026 weekend.
These are **not part of the main pipeline** — they are exploratory work documented here for transparency.

| Folder | What it is |
|---|---|
| [`nisar_ksar/`](nisar_ksar/README.md) | NISAR HH/HV on Ksar El Kebir (Morocco, Oct 25, 2026): why direct input fails, and an HH + synthetic-VH workaround (IoU 0.63 vs OSM water) |
| [`nisar_mozambique/`](nisar_mozambique/README.md) | NISAR on the Limpopo flood (Jan 2026), validated against Copernicus EMS EMSR857: precision 0.96, recall ~0.33, F1 0.51, IoU 0.34 |
| [`morocco_check.md`](morocco_check.md), [`validation.md`](validation.md), [`event_metrics.json`](event_metrics.json), [`diagnostics.json`](diagnostics.json) | Aya's check of the U-Net and an Otsu threshold against the Zenodo SAR Morocco masks (U-Net IoU 0.256, threshold 0.442): the threshold wins on this reference, which was itself made with Otsu |

Data files are in the shared Drive folder `under_the_clouds_ikram/` (not committed to this repo).  
Full write-up: `NISAR_Experiment_and_Mozambique_Ikram.pdf`.

