# Event notes (Aya)

## Event
- Loukkos River / Ksar El Kebir and Gharb plain floods, Morocco, late January to February 2026.
- Radar scenes used by the team: Sentinel-1, before 21 Jan 2026, after 8 Feb 2026 (Path 147 / Frame 110).
- NISAR: no public data for these dates (searched by Ikram), so Sentinel-1 is used and we say so openly.

## Facts and status
| Fact | Value | Status |
|---|---|---|
| Flood onset | 28 Jan 2026 | Confirmed on GDACS (event 1103747) |
| GDACS alert level | Green (low humanitarian impact) | Confirmed on GDACS |
| Displaced (GDACS) | 20,000 (episodes 1-2), 50,000 (episode 3, 3 Feb) | Confirmed on GDACS |
| GDACS satellite window | 21 Jan to 10 Feb 2026 (observation window, not the end of the flood) | Confirmed on GDACS |
| Return of residents | 16 Feb 2026 | CHECK in Reuters article |
| Evacuated 188,000 / 143,164 (Interior Ministry) | | CHECK in AP / Reuters, delete if not found |
| Flooded area ~1,100 km2 (110,000 ha) | | CHECK source |
| Flooded area ~789 km2 at 8 Feb peak | | CHECK in the Springer study (a different measurement) |
| Dam release 372 million m3, 146% capacity, "Storm Leonardo", 3 billion MAD plan | | CHECK in AP / Reuters / Hespress, delete if not found |

## Sources
- GDACS: https://www.gdacs.org/Floods/report.aspx?detail=true&episodeid=1&eventid=1103747&eventtype=FL
- AP: https://apnews.com/article/f286b572a5f3029e99149b04c85b6c08
- Reuters: https://www.reuters.com/business/environment/morocco-residents-begin-returning-northwest-flood-waters-recede-2026-02-16/
- Hespress: https://en.hespress.com/130648-ksar-el-kebir-after-floods-damage-measures-and-whats-next.html

## Reference data
- SAR Morocco Flood Dataset, Zenodo, DOI 10.5281/zenodo.22964153, CC BY 4.0.
- 1,497 Sentinel-1 patches (256x256, VV+VH) with binary water masks; zone 1 Ksar El Kebir (102), zone 4 Gharb plain (887).
- Masks: HSBA + Otsu + morphology + visual QC (semi-automatic, not expert ground truth).
- Credit: Contains modified Copernicus Sentinel data 2024-2026, processed by Kzadri M., Begdouri A., El Fazazy K., Qjidaa H., Ouazzani Jamil M., Tairi H., Riffi J.
