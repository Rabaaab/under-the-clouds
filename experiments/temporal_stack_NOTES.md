# Temporal-stack experiment: not done

The current Moroccan event input has two Sentinel-1 dates: before (21 January 2026)
and after (8 February 2026). A temporal-stack experiment has therefore not been
run; there are only two dates.

The existing model expects a two-channel VV/VH image. Stacking additional dates
would change the model input and require a separately designed, trained, and
validated experiment. No temporal-stack accuracy is claimed here.

Any comparison against the Zenodo SAR Morocco masks must keep the limitations
visible: the labels are semi-automatic HSBA+Otsu masks, not expert ground truth,
may favour Otsu, cover only part of the scene, have unknown patch dates, and
represent water masks rather than a flood-change map.

CNN not run on real data locally: `outputs/unet.pt` is on Drive and was not
available in this checkout.
