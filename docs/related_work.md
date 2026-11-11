# Related Work: Butler-Matrix Arrays, Series-Fed Columns and UAV Links

A survey of published work close to this project (5.8 GHz, 8×8 Butler matrix feeding 8 series-fed patch columns, 64-element planar aperture, UAV video-link ground station). It is based on openly accessible sources; several IEEE papers could only be read at title/abstract level, so the conclusions are "not found in the accessible literature", not a claim of novelty.

## Summary

Every building block of the project has been published separately, but the combination has not been found:

- **Butler + series-fed columns:** published only with 4×4 matrices at mm-wave (28 / 60 GHz). Structurally the closest work is Liu, Bshara, Tekin and Dandekar (2018): 60 GHz, 4×4 Butler, 4×10 series-fed array, two-hybrid crossover, simulation only.
- **8×8 Butler + antenna:** found at 1.9, 28, 60 and 77 GHz, always with each Butler output feeding a single element (linear 8×1 arrays), never a series-fed column per output.
- **5–6 GHz Butler arrays:** almost all are 4×4 Butler + 1×4 patch row, ~10 dBi.
- **Butler for UAVs:** one verified example (Kim et al. 2020): 1.96 GHz, 4×4, MCU-controlled RF switch, mounted on the UAV.
- **Butler + frequency scanning in the 5 GHz Wi-Fi band:** already published by Gil-Martínez et al. (IEEE OJAP, 2026), so 2D scanning in this band is not new. This project instead uses low-dispersion resonant columns so that the beam stays fixed across a video channel.

## 5–6 GHz Butler arrays

The common pattern at 5–6 GHz is a 4×4 Butler matrix, a single row of 4 inset-fed patches, RT/duroid 5880 or FR4, and beams around ±15° / ±40°. The only measured example found is Imani and Bayati (2021): 4.45–5.67 GHz, 10.2 ± 0.2 dB gain on FR4.

| Work | Year / venue | Frequency | Butler | Array / feed | Substrate | Gain | Beams | Status | Link |
|---|---|---|---|---|---|---|---|---|---|
| Eshaghi, Rashidzadeh | 2022, IEEE Sensors | 5.8 GHz | 4×4 | not accessible | not accessible | not accessible | not accessible | not accessible | [IEEE](https://ieeexplore.ieee.org/document/9967033) |
| Soualmi, Rouaba, Li | 2014, AMM 610 | 5.8 GHz | 4×4 (no crossover) | not stated | RT/duroid 5880, εr 2.2 | – | – | Simulation | [link](https://www.scientific.net/AMM.610.878) |
| "Smart Antenna ... WLAN" (authors not verified) | 2014, AMM 548–549 | 5.8 GHz | 4×4 | 1×4 microstrip | RT/duroid 5880, h 0.787 mm | – | – | Simulation | [link](https://www.scientific.net/AMM.548-549.1385) |
| Ihlou, Tizyi, El Abbassi | 2021, IJMOT 16(3) | 5.8 GHz | 4×4, 0 dB crossover | 1×4 inset patch | FR-4, h 1.6 mm | not stated | ±15°, ±39° | Simulation | [PDF](https://www.ijmot.com/ijmot/uploaded/9asNGXCFSic.pdf) |
| Imani, Bayati | 2021, AEU | 5.2 GHz | 4×4 | 1×4 patch | FR4 | 10.2 dB | ±15°, ±43° | **Fabricated, measured** | [link](https://www.sciencedirect.com/science/article/abs/pii/S1434841121002983) |
| Bhowmik, Srivastava | 2010, arXiv | 5.2 GHz | 4×4 | 1×4 inset patch | FR4, εr 4.9, h 1.6 mm | – | 4 beams in ~120° | Simulation | [arXiv](https://arxiv.org/pdf/1004.4821) |
| Moubadir et al. | 2015, WINCOM | 5.6 GHz | 8×8 in title, 4×4 in text | 1×4 inset patch, ~0.7λ | "FR4" εr 3.2, h 0.76 mm | "+6 dB" | ±15°, ±30° | Simulation | [Academia](https://www.academia.edu/98854220/Design_and_implementation_of_a_technology_planar_8_8_Butler_matrix_with_square_truncated_Edge_Fed_array_antenna_for_WLAN_networks_application) |
| 8×8 CMOS Butler | ~2011, IEEE | 5–6 GHz | 8×8 | no array (RFIC) | CMOS | – | – | not accessible | [IEEE](https://ieeexplore.ieee.org/document/5678820/) |

Gains in this band are ~10–11 dBi, as expected for a single row of 4 elements. The ~19–23 dBi of this project comes from a 64-element aperture, so gain comparisons must account for aperture size.

## 8×8 Butler matrices and Butler + series-fed columns

| Work | Year / venue | Frequency | Butler | Array / feed | Substrate | Gain | Beams | Status | Link |
|---|---|---|---|---|---|---|---|---|---|
| **Liu, Bshara, Tekin, Dandekar** | 2018, WAMICON (IEEE) | 60 GHz | 4×4 | **4×10 series-fed** Chebyshev patch lines | RO4003C 0.2 mm | 16.5 dBi | 4 beams within ±50° | Simulation (HFSS) | [NSF](https://par.nsf.gov/servlets/purl/10118260) |
| Simionato et al. | 2024, AEU 184 | 57–64 GHz | 4×4 | four 4-element series-fed arrays | nanoporous alumina (MnM) | not accessible | 4 H-plane beams + E-plane frequency scan | Prototype | [SD](https://www.sciencedirect.com/science/article/abs/pii/S1434841124002905) |
| Azari, Skrivervik | not verified | 28 GHz | Butler (7 beams) + BLC | 2×10 and 4×10 series-fed | RO4003C | 11.2–14.1 dBi | 13 beams, ±138° | unclear | [EPFL](https://graphsearch.epfl.ch/en/publication/301337) |
| Rahayu, Yamada, Syam | 2024, ISITIA | 28 GHz | 4×4 | series-fed | metadata only | metadata only | metadata only | metadata only | – |
| Park, Bang, Choi | 2020, Appl. Sci. | 60 GHz | **8×8** stripline | 1×4 dual-fed circular polarization | Taconic TLY, 3 layers | 10.18 dBi (measured) | ±11°, ±38° | Fabricated, measured | [MDPI](https://www.mdpi.com/2076-3417/10/7/2413) |
| Sakhiya, Chowdhury | 2023, Sensors | 77 GHz | **8×8** microstrip | 8×1 inset patch | HPFS glass, 200 µm | 20.3 dB (4×4 system) | ±15°, ±42° (4×4) | Simulation | [MDPI](https://www.mdpi.com/1424-8220/23/3/1418) |
| Adamidis et al. | 2019, IJAP | 1.9 GHz | **8×8**, single layer, no crossovers | 8 dipoles/monopoles (via coax) | FR4 1.5 mm | – | 8 orthogonal beams, ~2–3° error | Fabricated, measured | [Hindawi](https://www.hindawi.com/journals/ijap/2019/1645281/) |

Liu et al. (2018) uses the same components as this project (series-fed patch lines at the Butler outputs, two-hybrid crossover, simulation only) at 4×4 and 60 GHz. This project scales that pattern to 8×8 and 5.8 GHz.

## Switched beams for UAV links

| Work | Year / venue | Frequency | Architecture | Gain / beams | Location | Status | Link |
|---|---|---|---|---|---|---|---|
| **Kim, Kim, Dong, Cho, Lee** | 2020, Electronics 9(1):2 | 1.96 GHz | **4×4 Butler** + 1×4, MCU + RF switch | 9.98 dBi; −39°, −17°, 9°, 31° | on the UAV | Fabricated, measured (no link test) | [MDPI](https://www.mdpi.com/2079-9292/9/1/2) |
| Mu et al. (UPM) | ~2016 | 5.065 GHz | 8-element circular switched array | ~11 dB; 8 beams | on the UAV | Simulation | [PDF](https://oa.upm.es/46490/1/INVE_MEM_2016_250045.pdf) |
| Lee et al. | 2019, Electronics | 5.9 GHz | 4 switched J-poles | >7.4 dBi; 4 beams | on the UAV | Fabricated, measured | [MDPI](https://www.mdpi.com/2079-9292/8/11/1240) |
| Choi, Park, Lee | 2020, Electronics | 5–5.5 GHz | hybrid + SPDT | 5.8 dBi; 4 modes | on the UAV | Fabricated, measured | [MDPI](https://www.mdpi.com/2079-9292/9/6/980) |
| Wei et al. | 2025, Sensors | ~4.9–5.9 GHz | PIN-diode quasi-Yagi | 4.9 dBi; 8 azimuth + 5 elevation | on the UAV | Fabricated, measured | [MDPI](https://www.mdpi.com/1424-8220/25/23/7246) |
| Positano, Lizzi, Staraj | 2024, Front. Antennas Propag. | 868 MHz | ESPAR, PIN diodes | 3.95 dBi; 4 + omni | **ground station** | Field test with a drone, +5 dB RSSI | [Frontiers](https://www.frontiersin.org/journals/antennas-and-propagation/articles/10.3389/fanpr.2024.1429710/full) |
| Han, Jang | 2025, Sensors | 2.4 GHz | 6 patches + SP6T, RSSI-based angle of arrival | ~9 dBi/element | **ground receiver** | Indoor test with a DJI video signal | [MDPI](https://www.mdpi.com/1424-8220/25/8/2376) |

Kim et al. (2020) is a small-scale counterpart of the SP8T + STM32 control used here. Its measured 4.1 dB Butler insertion loss is a reminder that a fabricated 8×8 Butler matrix, with more hybrids and crossovers in each path, would reduce the simulated gain noticeably; the gains reported for this project are at the array ports and exclude Butler loss. No paper was found that receives a 5.8 GHz drone video link with an electronically switched or steered ground antenna. Positano et al. (2024) and Han and Jang (2025) are useful references for an RSSI-based beam-selection algorithm.

## Butler matrices with 2D or frequency scanning

| Work | Year / venue | Frequency | Butler | Element / second axis | Scan | Gain | Status | Link |
|---|---|---|---|---|---|---|---|---|
| **Gil-Martínez et al.** | 2026, IEEE OJAP 7(2) | 5.18–5.72 GHz | 4×4 microstrip | 4 half-width microstrip leaky-wave antennas, frequency scanning | ±60° (frequency) × ±45° (switching), 32 beams | not in abstract | not in abstract | [IEEE](https://ieeexplore.ieee.org/document/11214254/) |
| Pang, Geng, Wang | 2026, IEEE OJAP 7(1) | 3.8–4.9 GHz | SIW + phase-difference structure | LWA, frequency scanning | ±48° (29 beams) × −45°…+18° | – | – | – |
| Kaneda, Sanada, Kubo | 2006, IEICE Trans. Electron. | 10.25–10.7 GHz | Butler | CRLH LWA | −30…+25° × 4 discrete angles | – | Fabricated, measured | [IEICE](https://globals.ieice.org/en_transactions/electronics/10.1093/ietele/e89-c.12.1904/_p) |
| Tomura et al. | 2019, IEEE Access | 20 GHz | 64×64 2D (waveguide) | – | ~40 % of the hemisphere | >18.7 dBi directivity | Fabricated | – |
| Temga, Shiba, Suematsu | 2024, Sensors | 3–7 GHz | 4-way 2D, multilayer stripline | 2×2 patches | 4 quadrants, 30° | 9.1–9.9 dBi | Fabricated, measured | [MDPI](https://www.mdpi.com/1424-8220/24/2/714) |
| Orakwue, Ngah | 2019, Nigerian J. Technol. | 28 GHz | two cascaded 4×4 | – | ~±42° in two planes, 8 beams | 13.8 dBi | Fabricated, measured | [Academia](https://www.academia.edu/108471147/Cascaded_Butler_Matrix_with_Two_Dimensional_Beam_Scanning_Capability_at_28_GHz_for_5G_Wireless_System) |

The key difference from Gil-Martínez et al. is dispersion. Their leaky-wave antenna scans ~120° over 540 MHz (~22° per 100 MHz), using dispersion deliberately as a scanning mechanism. The resonant series columns of this project move by only ~3° per 100 MHz (~4–5° over the 150 MHz ISM band), so the beam stays fixed across a 20–40 MHz video channel. Their column squint is therefore not presented here as 2D scanning.

## Two-hybrid crossovers

Cascading two 90° hybrids into a 0 dB crossover is a standard planar Butler technique, so its use here is an established design choice rather than a contribution.

| Work | Year | Frequency | 8×8 structure | Crossover | Substrate | Crossover performance | Status | Link |
|---|---|---|---|---|---|---|---|---|
| Sakhiya, Chowdhury | 2023 | 77 GHz | single-layer microstrip | Type 1: two hybrids; Type 2: alternative | HPFS glass 200 µm | Type 1 IL −0.636 dB; Type 2 isolation −33.87 dB | Simulation | [MDPI](https://www.mdpi.com/1424-8220/23/3/1418) |
| Park, Bang, Choi | 2020 | 60 GHz | 3-layer stripline | two quadrature hybrids | Taconic TLY | < −15 dB | Fabricated | [MDPI](https://www.mdpi.com/2076-3417/10/7/2413) |
| Idrus et al. | 2019 | 28 GHz | single layer, 16 crossovers | type to be verified | NPC-F220A, εr 2.2, 0.254 mm | IL 0.4 dB; phase error ±10° | Network fabricated | [PLOS](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0226499) |
| Adamidis et al. | 2019 | 1.9 GHz | single layer | **no crossovers** | FR4 1.5 mm | ~2.7 dB extra loss | Fabricated, measured | [Hindawi](https://www.hindawi.com/journals/ijap/2019/1645281/) |
| Moubadir et al. | 2015 | 5.6 GHz | 8×8 in title / 4×4 in text | two hybrids (0 dB coupler) | "FR4" εr 3.2, h 0.76 mm | isolation > 25 dB | Simulation | [Academia](https://www.academia.edu/98854220/Design_and_implementation_of_a_technology_planar_8_8_Butler_matrix_with_square_truncated_Edge_Fed_array_antenna_for_WLAN_networks_application) |

No published isolation data was found for two-hybrid crossovers on εr ≈ 2.6 PTFE at 5–6 GHz, nor for the leakage accumulated through a full 8×8 matrix. In an 8×8 matrix a path crosses several crossovers, so per-crossover isolation matters more than in a 4×4. The network model in this project (Section 7 of the [technical summary](technical_summary.md)) quantifies this: −15 dB leakage scatters the beams, −25 dB keeps the column phase errors at a few degrees.

## Comparison with the closest works

| Work | Frequency | Butler | Aperture / feed | Substrate | Gain | Crossover | Application | Status | Main difference |
|---|---|---|---|---|---|---|---|---|---|
| **This project** | 5.8 GHz | **8×8** microstrip | **8×8 = 64 patches**, 8 series-fed columns | PTFE εr ≈ 2.65, 0.762 mm, single layer | 18.6–22.8 dBi | two hybrids | UAV video ground station, SP8T + STM32 | CST simulation, not fabricated | — |
| Liu et al. 2018 | 60 GHz | 4×4 | 4×10 series-fed | RO4003C, 2 layers | 16.5 dBi | two hybrids | 5G | Simulation | same architecture; 4×4 scale, different frequency and application |
| Gil-Martínez et al. 2026 | 5.18–5.72 GHz | 4×4 | 4 LWAs, frequency scanning | – | – | – | Wi-Fi 2D scanning | – | same band family; LWA ~7× more dispersive, 4×4 |
| Simionato et al. 2024 | 60 GHz | 4×4 | four 4-element series-fed | MnM alumina | – | broadband | 60 GHz WLAN | Prototype | Butler + series columns + E-plane scan; custom process |
| Kim et al. 2020 | 1.96 GHz | 4×4 | 1×4 | – | 9.98 dBi | – | on the UAV | Fabricated, measured | same control scheme (MCU + RF switch); low gain, UAV side |
| Imani, Bayati 2021 | 5.2 GHz | 4×4 | 1×4 | FR4 | 10.2 dB | yes | C band | Fabricated, measured | same band; ~10 dB lower gain, 1D array |
| Park et al. 2020 | 60 GHz | 8×8 stripline | 1×4 circular polarization | 3 layers | 10.18 dBi | two hybrids | 5G | Fabricated, measured | 8×8 but multilayer, small aperture |
| Sakhiya, Chowdhury 2023 | 77 GHz | 8×8 microstrip | 8×1 | glass | 20.3 dB (4×4) | two hybrids (Type 1) | radar | Simulation | 8×8 single layer but 1D array |
| Idrus et al. 2019 | 28 GHz | 8×8 single layer | no antenna | εr 2.2 | – | 16 crossovers | 5G base station | Network fabricated | feed network only |
| Adamidis et al. 2019 | 1.9 GHz | 8×8 single layer | 8 dipoles via coax | FR4 | – | none | general | Fabricated, measured | crossover-free alternative |

## Positioning and limitations

The project is best described as scaling a published architecture (Liu et al. 2018) to sub-6 GHz and 8×8, and applying it to a concrete UAV-link problem, with low-dispersion columns chosen deliberately so the beam is stable within a video channel. Its main weakness compared with the strongest works in this band (Imani 2021, Adamidis 2019, Kim 2020) is that it has not been fabricated or measured. The most valuable next step would be measurement: even port-to-port phase/amplitude data from a single fabricated 8×8 Butler network on PTFE would provide data not found in the accessible literature, and a simple RSSI-based drone test in the style of Positano et al. and Han and Jang would validate the application.
