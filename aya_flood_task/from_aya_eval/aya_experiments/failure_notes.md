# Failure Cases: Otsu Threshold Baseline (Ksar El Kebir Scene, After VV)

## General Notes

- These five crops illustrate disagreements between the **Otsu threshold baseline** and the Zenodo reference water mask. They do not show CNN/U-Net failures.
- Red represents water detected by the Otsu threshold. Blue represents water labelled in the reference.
- The reference comes from the Zenodo SAR Morocco Flood Dataset. Its masks are semi-automatic (HSBA + Otsu + visual checks), rather than independently verified expert ground truth.
- The reference is a water mask, not a flood-change map. The acquisition dates of the reference patches could not be verified, so a date mismatch cannot be excluded.
- Therefore, "false alarm" and "missed water" describe disagreements with the reference, not necessarily confirmed classification errors. Some areas detected by Otsu but absent from the reference could be real water, while some reference-labelled areas could be uncertain.

## Case 1: False Alarm (y=768, x=1024)

The Otsu baseline detects extensive water-like areas across the tile, particularly a large, very dark patch in the lower-middle part and several irregular regions around the rectangular structures in the upper part. However, the reference mainly identifies thin river-like features and smaller scattered patches. It labels only limited portions of the large dark area detected by Otsu.

The large dark patch is clearly visible in the VV image, suggesting a strong radar response associated with a smooth or water-like surface. However, the image alone cannot establish whether it represents actual flooding, another type of dark surface, or a reference-label omission.

**Possible explanation:** Otsu may be detecting dark surfaces that are not included in the reference, potentially including flooded or smooth fields. A limitation or omission in the reference is also possible.

## Case 2: False Alarm (y=512, x=896)

This tile contains a pattern of agricultural-looking parcels and elongated, relatively straight features. Otsu identifies numerous dark regions across these areas, producing extensive red detections. In contrast, the reference labels more limited water features, including a winding feature on the left, scattered patches in the upper part, and a water-like feature along the right edge.

Many of the red detections follow the rectangular and elongated patterns visible in the radar image rather than clearly following continuous natural water channels.

**Possible explanation:** Otsu may be confusing dark agricultural surfaces, wet soil, or field boundaries with water. Some detections could also represent water that is not included in the reference. Their actual nature cannot be confirmed from this crop alone.

## Case 3: False Alarm (y=1024, x=1152)

A winding, river-like feature is visible in the upper part of the VV image. The reference identifies this feature with a relatively thin blue line extending towards the right side of the tile. Otsu detects some dark regions around the upper-left portion of the feature, but its red detections do not reproduce the reference water extent consistently.

Unlike the first two cases, most of the remaining tile is relatively uniform grey, with only a few isolated detections. The disagreement is concentrated around the river-like feature and its surrounding dark areas.

**Possible explanation:** The difference may be related to the threshold's difficulty in identifying narrow or irregular water features consistently. Differences in the labelled river extent and possible reference omissions may also contribute.

## Case 4: Missed Water (y=512, x=1152)

The VV image is mostly grey, with a dark feature entering from the left edge. Otsu detects some of the darker pixels near this edge, but its red detections cover only a small portion of the water identified by the reference.

The blue reference mask extends farther into the tile and includes several scattered, branching patches that are not detected by Otsu. These reference-labelled areas appear relatively subtle in the VV image and are not as dark as the strongest water-like regions.

**Possible explanation:** The threshold may miss relatively weak radar-darkening associated with shallow water or water mixed with vegetation. Reference uncertainty or incomplete correspondence between acquisition dates cannot be excluded.

## Case 5: Missed Water (y=1024, x=896)

This tile is predominantly uniform grey, with relatively weak variations in radar intensity. The reference identifies a diagonal group of water patches extending from the upper-right corner towards the centre of the tile.

Otsu detects only a few small, isolated regions and misses most of the blue reference-labelled area. The reference detections are relatively subtle in the VV image and do not consistently appear as strongly dark regions.

**Possible explanation:** The water features may have a weak radar response, making them difficult to separate from the surrounding surface using a single global threshold. Shallow or vegetation-covered water could contribute to this behaviour. A possible mismatch between the reference date and the SAR acquisition date also remains an uncertainty.

## Summary

1. **False alarms (Cases 1–3):** Otsu identifies several dark areas that are not labelled as water in the reference. These include extensive dark patches, agricultural-looking patterns, and regions around river-like features. They may represent non-water dark surfaces, actual water omitted from the reference, or differences in the spatial extent of the labels.

2. **Missed water (Cases 4–5):** Otsu fails to identify several reference-labelled water patches, particularly areas with relatively weak contrast against their surroundings in the VV image. This illustrates a limitation of relying on a single global intensity threshold.

3. **Reference uncertainty:** The Zenodo mask is semi-automatic and is not independently verified ground truth. Consequently, disagreements cannot automatically be interpreted as errors made by Otsu.

4. **Interpretation:** These five examples illustrate the limitations of the Otsu baseline in distinguishing water from other dark surfaces and detecting relatively subtle water features. They do not establish the causes of every disagreement, nor do they provide evidence about CNN/U-Net failure cases.
