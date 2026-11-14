# Failure cases: Otsu threshold baseline (Ksar El Kebir scene, after VV)

- These crops show failures of the **Otsu baseline**, not of the CNN. The CNN is not scored yet; new crops will be added when it is.
- The reference is the Zenodo SAR Morocco Flood Dataset. Its masks are semi-automatic (HSBA + Otsu + visual checks), not expert ground truth, and they may favour the Otsu baseline. They are water masks, not a flood-change map. Patch dates were not readable, so the reference may mix dates.
- So "false alarm" and "missed water" mean "disagrees with this reference". In several crops the reference itself may be the one that is wrong or incomplete. The causes below are what the images suggest, not proven.

## case1 (false alarm) y=768, x=1024
The baseline marks large dark areas as water: a big dark patch in the lower middle and wide areas around rectangular field parcels in the upper part. The reference only labels thin river lines and some smaller patches, and covers just part of the big dark patch. The dark patch is clearly dark in radar, so it may be real water (flooded fields) that the reference missed, or smooth wet or bare fields. We cannot tell which from the image alone. Likely: label gap or flooded fields.

## case2 (false alarm) y=512, x=896
This tile is a striped pattern of agricultural parcels. The baseline marks many dark, straight-edged field stripes as water. The reference labels only the river bend, a large water body on the right, and a few bits. The straight edges point to field boundaries (wet, flooded or smooth ploughed fields), not natural water. Likely: dark fields, with the reference not counting them.

## case3 (false alarm) y=1024, x=1152
The river with its meanders is dark and both methods mark it. The baseline also marks a wider, dark block with straight edges next to the river, where the reference only covers part. The rest of the tile is uniform grey with almost no false alarms. At the river edges the red region is thicker than the thin blue line. Likely: disagreement on the dark block and on river width, more a label question than a model mistake.

## case4 (missed water) y=512, x=1152
Both methods agree on the dark patch at the left edge. The reference also labels scattered patches to the right that are only slightly darker than the surroundings in VV, and the baseline misses them because they are not dark enough to pass the threshold. Likely: shallow water or flooded vegetation (grey, not black, in radar), or label noise.

## case5 (missed water) y=1024, x=896
The tile is almost uniformly grey. The reference marks a diagonal band of water patches from the top right towards the centre, but in VV they show only faint darkening, and the baseline finds only a few small spots. Likely: weak radar signal (shallow or vegetated flooding) or a reference from a different date. Because dates are unknown, a date mismatch cannot be ruled out.

## Summary
1. False alarms (cases 1 to 3) are mostly large dark areas that look like flooded or smooth fields; the reference does not label them. This may partly be a reference limit.
2. Missed water (cases 4 and 5) are patches with only a weak darkening in VV, which a single threshold cannot catch.
3. None of the 5 crops clearly shows steep terrain, a city or the sea, so we do not claim those failure types here.
