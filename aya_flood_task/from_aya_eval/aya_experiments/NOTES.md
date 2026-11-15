# Event notes (Aya)

## Event
- Loukkos River / Ksar El Kebir and Gharb plain floods, northwest Morocco, late January to February 2026.
- Radar scenes used by the team: Sentinel-1, before 21 Jan 2026, after 8 Feb 2026 (Path 147 / Frame 110, HyP3 RTC 30 m).
- NISAR: no public data over this area for these dates (searched by Ikram), so Sentinel-1 is used and we say so openly.

## Confirmed facts
| Fact | Value | Source |
|---|---|---|
| Flood onset | 28 Jan 2026 | GDACS (event 1103747); Anadolu (6 Feb) |
| GDACS alert level | Green (low humanitarian impact) | GDACS |
| Displaced (GDACS) | 20,000, later 50,000 (3 Feb) | GDACS |
| GDACS satellite window | 21 Jan to 10 Feb 2026 (observation window, not the end of the flood) | GDACS |
| Ksar El Kebir, 30 Jan | Loukkos River overflowed overnight; water about 1 m in some low-lying neighbourhoods; proximity hospital evacuated; no casualties reported as of that morning | Hespress (30 Jan) |
| Rainfall and dam, 30 Jan | More than 600 mm since September in Larache province; Oued El Makhazine dam at a 100% filling rate; controlled releases | Hespress (30 Jan) |
| Evacuated, 2 to 3 Feb | More than 50,000 | AFP via Arab News (Interior Ministry) |
| Evacuated, 4 Feb | About 108,000 | Interior Ministry via The New Arab / TimesLive |
| Evacuated, 5 Feb | 143,164 (Interior Ministry, Thursday); officials said up to 85% of Ksar El Kebir was evacuated | AP (5 Feb) |
| Dam release | More than 372 million m3 discharged from the Oued Al Makhazine dam | AP (5 Feb) |
| Dam at 146% of capacity | Reported as a water ministry statement, 4 to 5 Feb. Different date and measure from the 100% filling rate above: do not mix them | TimesLive (5 Feb) |
| Storm name | "Storm Leonardo" is used by Al-Monitor only | Al-Monitor |
| Return of residents | From Monday 16 Feb 2026, gradual return; most residents allowed back except a few neighbourhoods | Reuters (16 Feb) |

## Not used (no source found, do not put in slides, README or form)
- 188,000 evacuated
- 3 billion MAD recovery program
- 110,000 ha (about 1,100 km2) flooded area
- 789 km2 flooded at the 8 Feb peak (comes from a Springer study that has not been opened; use only if it is checked and named)
- "Dozens of rural homes collapsed", "landslides", "95% relocated in Gharb villages"
- Total number of casualties (not checked)

Note: our scene is a small crop (lon -6.25 to -5.75, lat 34.90 to 35.25). The team's 46 to 51 km2 of new water covers only that crop and cannot be compared with regional totals.

## Sources
- GDACS: https://www.gdacs.org/Floods/report.aspx?detail=true&episodeid=1&eventid=1103747&eventtype=FL
- AP (5 Feb 2026): https://apnews.com/article/f286b572a5f3029e99149b04c85b6c08
- AP text copy: https://wtop.com/news/2026/02/morocco-evacuates-140000-people-as-torrential-rains-and-dam-releases-trigger-floods
- Reuters (16 Feb 2026): https://www.reuters.com/business/environment/morocco-residents-begin-returning-northwest-flood-waters-recede-2026-02-16/
- Hespress (30 Jan 2026): https://en.hespress.com/130648-ksar-el-kebir-after-floods-damage-measures-and-whats-next.html
- AFP via Arab News (50,000 evacuated): https://www.arabnews.pk/node/2631594
- TimesLive (108,000 evacuated, 146%): https://www.timeslive.co.za/news/africa/2026-02-05-watch-moroccans-urged-to-leave-floodrisk-areas-as-evacuations-exceed-108000/
- Anadolu (6 Feb 2026): https://aa.com.tr/en/middle-east/morocco-continues-evacuations-as-floods-hit-northern-provinces-for-10th-day/3822499
- Al-Monitor (storm name): https://www.al-monitor.com/originals/2026/02/storm-leonardo-displaces-140000-heavy-floods-hit-northern-morocco

## Reference data
- SAR Morocco Flood Dataset, Zenodo, DOI 10.5281/zenodo.22964153, CC BY 4.0.
- 1,497 Sentinel-1 patches (256x256, VV+VH) with binary water masks. Zone 1 Ksar El Kebir / Loukkos: 102 patches on the Zenodo page; use the number your metadata CSV shows. Zone 4 Gharb plain: 887.
- Masks: HSBA + Otsu + morphology + visual QC (semi-automatic, not expert ground truth).
- Patch dates are unverified: the metadata has no readable dates, and the Zone 1 README lists 10 m GRD scenes from 27 Jan to 4 Feb 2026, while our event scene is from 8 Feb 2026.
- Credit: Contains modified Copernicus Sentinel data 2024-2026, processed by Kzadri M., Begdouri A., El Fazazy K., Qjidaa H., Ouazzani Jamil M., Tairi H., Riffi J.
