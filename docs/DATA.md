# Getting the data

Everything below is a checklist for you to run. None of it has been executed against the real archives yet,
so treat product names and file layouts as things to confirm.

## 1. Accounts

- Free **NASA Earthdata** login: https://urs.earthdata.nasa.gov (needed for NISAR, Sentinel-1 at ASF, NASADEM, HLS).
- Do not put your password or tokens in the repo. `.gitignore` already excludes `.env` and `.netrc` files.

## 2. Find scenes (do this first, it decides the event)

1. Open **ASF Vertex**: https://search.asf.alaska.edu
2. Draw an area over your region of interest (for example a Moroccan basin) and pick a date range.
3. Look for **NISAR** products. Confirm there is a scene **before** and one **after** your event.
   NISAR only began operating in mid-2025, so it cannot cover earlier events.
4. For earlier events, search **Sentinel-1** (GRD) instead.
5. Note the exact scene names and dates. They go in the README and the submission.

## 3. What to download

| Need | Product to look for | Notes |
|---|---|---|
| NISAR backscatter | GCOV (geocoded backscatter), check the exact names in Vertex | Check which polarizations your scene has |
| Sentinel-1 | GRD, VV + VH | Same grid issues apply |
| Training labels | Sen1Floods11 (hand-labelled subset) | `python scripts/sen1floods11.py download` (about 650 MB); check the dataset's terms |
| Terrain | NASADEM | Used to mask steep slopes |
| Roads and villages | OpenStreetMap | `python scripts/fetch_osm.py --bbox WEST SOUTH EAST NORTH --out data/osm` (worked on one small area; keep the box small and check coverage) |

## 4. Important caveats

- **Polarization mismatch.** The training data (Sen1Floods11) is Sentinel-1 **VV + VH**. NISAR scenes are often
  **HH + HV**. The model expects two channels; feeding it HH/HV is a domain shift, and results may be weaker.
  Say this in the write-up and compare against the threshold baseline.
- **Preparation is on you.** `scripts/run_event.py` expects two 2-band GeoTIFFs on the **same grid and CRS (EPSG:4326)**
  for before and after. Converting a raw NISAR or Sentinel-1 product into that form (reading the HDF5/GeoTIFF,
  calibration, geocoding, co-registration, reprojection) is not automated here.
- **Units.** Use `--linear` if your values are linear intensity (the speckle filter and dB conversion are applied);
  omit it if they are already in dB.
- **Sen1Floods11 is handled by `scripts/sen1floods11.py`.** Its layout (VV then VH in dB, labels -1/0/1, header-less split
  CSVs) was checked against the official repo and a few real chips. Only a small part has been run: the full download
  and a GPU training run have not been done yet.

## 5. After you have data

```bash
# Make training chips, then train (on a GPU: notebooks/train_colab.ipynb)
python scripts/sen1floods11.py download --root data/sen1floods11
python scripts/sen1floods11.py prepare  --root data/sen1floods11 --out data/chips
python scripts/train.py --train-dir data/chips/train --val-dir data/chips/valid --epochs 30 --out outputs/unet.pt

# Run an event
python scripts/run_event.py --before before.tif --after after.tif --linear \
    --roads roads.geojson --villages villages.geojson --checkpoint outputs/unet.pt \
    --event-name "My event" --out app/data
```
