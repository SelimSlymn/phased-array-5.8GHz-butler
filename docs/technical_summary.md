# 5.8 GHz 8×8 Butler-Matrix Array – Technical Summary

Selim Süleyman Hüthüt · October 2026

## Project summary and status

A 64-patch (8×8) antenna array was designed for 5.8 GHz. The beam is switched to 8 fixed directions in the horizontal plane by an 8×8 Butler matrix, an SP8T RF switch and an STM32. The final design targets JLCPCB's ZYF265D (0.762 mm) laminate, and all 64 elements were simulated full-wave in commercial CST Studio Suite: the best beam reaches 22.8 dBi in the scan plane, and the column beam points exactly at broadside.

Signal chain: **STM32 (3 GPIO bits) → SP8T switch → 8×8 Butler matrix → 8 series-fed columns → 64 patches.**

| Quantity | Value |
| --- | --- |
| Frequency | 5.80 GHz (ISM band 5.725–5.875 GHz), λ₀ = 51.7 mm |
| Substrate | ZYF265D (JLCPCB), εr = 2.65 ± 0.04, tanδ = 0.0019, h = 0.762 mm, 35 µm copper |
| Array | 8 × 8 patches (19.1 × 15.74 mm), column spacing 25.9 mm (λ₀/2), in-column pitch 30.75 mm (0.59 λ₀) |
| Beams | 8 beams: +7°, −6°, ±21°, ±37°, +55° / −56° (horizontal plane); broadside in the column plane (tilt ≤ 0.4°) |
| Realized gain (scan plane, Butler loss excluded) | 22.8 dBi (inner beams) … 18.6 dBi (±55°) |
| 3 dB beamwidth | 12° (near broadside) … 20° (±55°) in the scan plane; ~10° in the column plane |
| Side-lobe level | −6.9 … −12.9 dB in the scan plane; −12.5 / −14.5 dB in the column plane |
| Passive S11 (each port) | −15 dB at 5.80 GHz; −10 dB band 5.757–5.834 GHz |
| Worst active S11 at 5.80 GHz | inner 6 beams −11.9 … −14.1 dB; ±55° beams −6.2 … −6.8 dB (average mismatch loss 0.65 dB) |
| Operating band of the inner 6 beams | ≈ 5.78–5.82 GHz (~40 MHz) |
| Tools | CST Studio Suite 2025 (time domain, 30 cells/λ, 8.8 million cells), openEMS 0.37 (pre-design), Python (Butler network and farfield combination) |

Open issue: the beam cannot be steered in the vertical plane (y axis). The reason and possible solutions are in Section 11.

## 1. Substrate choice: why ZYF265D (0.762 mm)

The final substrate is JLCPCB's ZYF265D PTFE laminate: εr = 2.65, tanδ = 0.0019, h = 0.762 mm. The first design was for F4BM265 (0.8 mm); it was moved to JLCPCB's standard thickness so that the board can actually be ordered.

| Material | εr (tolerance) | tanδ | Resonance shift from εr tolerance | Note |
| --- | --- | --- | --- | --- |
| FR4 | ~4.3–4.6 | ~0.02 | hundreds of MHz | ~1.75 dB/100 mm on a 50 Ω line; not suitable for the Butler path |
| **ZYF265D (selected)** | 2.65 ± 0.04 | 0.0019 | ±44 MHz | ~0.13 dB/100 mm; 0.76 / 1.52 mm at JLCPCB, max. 590 × 438 mm |
| F4BM265 (first design) | 2.65 | 0.001 | – | 0.8 mm |
| Rogers RT/duroid 5880, TLY-5 | 2.2 ± 0.02 | 0.0009 | ±26 MHz | best tolerance, most expensive |

- **Thickness change:** going from 0.8 to 0.762 mm, line widths were scaled by 0.9525 (50 Ω: 2.20 → 2.10 mm). εeff stays almost the same, so lengths were not changed.
- **Why loss matters:** in the Butler matrix the signal passes through 3 hybrids, several crossovers and long delay lines. On FR4 this path would add several dB of loss; on PTFE it stays small.
- **Tolerance:** the band in which all beams work is ~40 MHz, while the εr tolerance shifts the resonance by ±44 MHz (Δf/f ≈ Δεr / 2εr). A single-column test board would be needed before fabricating the full array.

## 2. Single patch design

The patch dimensions were calculated with the transmission-line model and then tuned in CST together with the series-fed column: **W = 19.1 mm, L = 15.74 mm.**

Width (for efficient radiation):

```latex
W = \frac{c}{2 f_0}\sqrt{\frac{2}{\varepsilon_r + 1}} = \frac{3\times10^8}{2 \cdot 5.8\times10^9}\sqrt{\frac{2}{3.65}} \approx 19.1\ \text{mm}
```

Effective permittivity (smaller than εr because part of the field is in air):

```latex
\varepsilon_{eff} = \frac{\varepsilon_r + 1}{2} + \frac{\varepsilon_r - 1}{2}\left(1 + 12\frac{h}{W}\right)^{-1/2} \approx 2.50
```

Fringing-field extension and resonant length:

```latex
\Delta L = 0.412\,h\,\frac{(\varepsilon_{eff}+0.3)(W/h+0.264)}{(\varepsilon_{eff}-0.258)(W/h+0.8)} \approx 0.40\ \text{mm}
```

```latex
L = \frac{c}{2 f_0 \sqrt{\varepsilon_{eff}}} - 2\Delta L \approx 16.36 - 0.81 \approx 15.5\ \text{mm}
```

- The formula gives about 15.5 mm. The final L = 15.74 mm was tuned together with the column match and beam direction (Section 5).
- The radiating edges are the two ends of L. Current flows along L (column direction); polarization is linear, along the column.
- 50 Ω line width is 2.10 mm (εeff ≈ 2.19, λg ≈ 34.9 mm).

## 3. Array geometry: element spacing

The column spacing is **d = 25.9 mm = λ₀/2**, so no second main beam (grating lobe) appears at any scan angle.

Grating-lobe-free condition (θ₀ = scan angle):

```latex
\frac{d}{\lambda_0} < \frac{1}{1 + |\sin\theta_0|}
```

- For d = λ₀/2 this holds up to 90°.
- A smaller spacing would increase coupling; the patch is already 19.1 mm wide, leaving a gap of only 6.8 mm.
- A larger spacing would increase gain slightly, but grating lobes would appear on the ±56° beams.

The in-column pitch is **p = L + Lc = 15.74 + 15.01 = 30.75 mm ≈ 0.59 λ₀**. Since there is no scanning along the column (fixed column beam), a pitch larger than λ/2 is acceptable. It is not enough if vertical scanning is wanted (Section 11).

Maximum directivity expected from the physical aperture:

```latex
D_{max} \approx \frac{4\pi A}{\lambda_0^2} = \frac{4\pi\,(8 \cdot 25.9)(8 \cdot 30.75)\ \text{mm}^2}{(51.7\ \text{mm})^2} \approx 240 \;\Rightarrow\; 23.8\ \text{dBi}
```

The simulated 22.8 dBi is 1 dB below this limit. The difference comes from series-line loss and from the Butler matrix not delivering perfectly equal amplitudes to the columns.

## 4. Column feed: why series feeding

The 8 patches of each column are fed in series along one line. The reason is space: a parallel (corporate) feed tree does not fit into the 25.9 mm column width.

- **Parallel feed:** 1-to-8 T-junctions and λ/4 transformers; needs about 42 mm of width for 8 elements and does not fit into the 25.9 mm cell.
- **Series feed:** patches are connected end-to-end on one line; the width is only that of the patch (19.1 mm).

Series feeding relies on phase summation. Passing through a patch the wave turns by ~180°, and on the connecting line (Lc) by another ~180°. With 360° in total, all patches radiate in phase and the beam points at broadside:

```latex
\phi_{cell} = \phi_{patch} + \beta\,L_c \approx 180^\circ + 180^\circ = 360^\circ, \qquad \beta = \frac{2\pi\sqrt{\varepsilon_{eff}}}{\lambda_0}
```

**The cost of this choice:** each column has a single input and the phase between patches is fixed by line length, so the beam cannot be steered in the vertical plane. Because the phase depends on line length, the structure is frequency-sensitive and narrowband.

## 5. Tuning the series column: mesh, beam tilt and matching

Final values: **L = 15.74 mm, Lc = 15.01 mm; transformer at d1 = 17.80 mm from the patch, wt = 4.40 mm, lt = 6.00 mm.** Single column (CST, 30 cells/λ): S11 = −15.5 dB at 5.80 GHz, −10 dB band 5.755–5.834 GHz, gain 15.1 dBi, beam tilt +0.1°, column side lobes −12.9 / −14.3 dB.

**Mesh: why openEMS was off.** The same column was solved in CST with two meshes. The resonance moves up as the mesh is refined; openEMS's coarse 0.88 mm cells amplified this effect and placed the resonance ~110 MHz too low. The single column and a column inside the 8×8 array gave the same frequency on the same mesh, so tuning was done on the single column (20–30 minute runs). The reference mesh is 30 cells/λ.

| Solver, mesh (L 15.04 / Lc 18.0 mm) | Cells | S11 minimum |
| --- | --- | --- |
| openEMS, λ/30 (0.88 mm) | – | 5.755 GHz |
| CST, 20 cells/λ, single column | 0.85 M | 5.848 GHz |
| CST, 20 cells/λ, 8×8 array | 4.07 M | 5.849 GHz |
| CST, 30 cells/λ, single column | 1.95 M | 5.868 GHz |

**Beam tilt.** To pull the resonance to 5.80 GHz, L and Lc were lengthened together by 1.2 % (15.22 / 18.22 mm) and S11 was centred. However, the 8×8 farfield showed that the column beam was tilted by 5.5° at 5.80 GHz, and the broadside gain was 4.5 dB below the peak. The cause was a cell phase exceeding 360° by ~22°:

```latex
\phi_{cell} - 360^\circ = 360^\circ\,\frac{p}{\lambda_0}\,\sin\theta_y = 360^\circ \cdot 0.647 \cdot \sin 5.5^\circ \approx 22^\circ
```

L sets the resonance and Lc sets the cell phase, but each affects both. Using the measured sensitivities (Lc: −50 MHz/mm and 8.7°/mm; L: −310 MHz/mm) the two equations were solved together:

| Run | L / Lc (mm) | S11 at 5.80 GHz | Tilt at 5.80 | Column side lobe | Outcome |
| --- | --- | --- | --- | --- | --- |
| 0 | 15.22 / 18.22 | −21 dB | +5.5° | −6.3 dB | 4.5 dB of broadside gain lost |
| 1 | 15.22 / 16.05 | −4.6 dB | +0.9° | −9.4 dB | tilt fixed, resonance moved to 5.95 GHz |
| 2 | 15.74 / 15.01 | −3.1 dB | 0.0° | −12.2 dB | radiation correct, match poor |
| 3 | 15.74 / 15.01 + new transformer | −15.5 dB | +0.1° | −12.9 dB | final |

**Matching.** After the length change, the impedance at the first patch edge dropped to ≈ 17.7 Ω at 5.80 GHz. This value was obtained from CST's S11 by de-embedding the feed lines with an ideal-line model. d1, wt and lt were optimized to minimize the worst reflection over 5.765–5.835 GHz:

```latex
Z_t \approx \sqrt{Z_0\,R} = \sqrt{50 \cdot 17.7} \approx 30\ \Omega \;\rightarrow\; \text{optimum: } 29\ \Omega,\ w_t = 4.40\ \text{mm},\ l_t = 6.00\ \text{mm},\ d_1 = 17.80\ \text{mm}
```

The calculation predicted −15.9 dB and 5.757–5.840 GHz; CST gave −15.5 dB and 5.755–5.834 GHz. The trade-off: the passive band shrank from 102 MHz to 79 MHz, in exchange for +4.5 dB of broadside gain and ~6 dB lower column side lobes.

## 6. 90° branch-line hybrid

The basic building block of the Butler matrix is the 4-port 90° hybrid. It splits the power entering one port equally between two outputs (−3 dB) with a 90° phase difference; the fourth port is isolated.

| Branch | Impedance | Width (0.762 mm) | Length (λg/4) |
| --- | --- | --- | --- |
| Series branches | Z₀/√2 = 35.4 Ω | 3.44 mm | 9.643 mm |
| Shunt branches | Z₀ = 50 Ω | 2.10 mm | 9.811 mm |

```latex
S = \frac{-1}{\sqrt{2}}\begin{pmatrix} 0 & j & 1 & 0 \\ j & 0 & 0 & 1 \\ 1 & 0 & 0 & j \\ 0 & 1 & j & 0 \end{pmatrix}
```

- The wider line has a higher εeff, so the quarter wavelength of the 35 Ω branch is slightly shorter than that of the 50 Ω branch.
- Branch lengths were tuned in CST with a parametric sweep. The S-parameters were exported to `s-parameters/hybrid_762.s4p` and used directly in the Butler calculation.
- The hybrid has about 10 % bandwidth; the narrow system band comes from the antenna, not the hybrid.

## 7. Crossover: why two hybrids

In a Butler matrix lines must cross. On a single-layer board this is done by a **crossover**, which passes the signal to the diagonal port at 0 dB. The final design is two 90° hybrids in cascade: leakage to the straight-through port is **−25.0 dB (0.762 mm; −26.6 dB on 0.8 mm)**.

**First attempt: three-branch crossover.** An 18-point parameter sweep was run and the leakage never went below −25 dB, so this design was dropped.

**Why −25 dB is required:** a network model of the whole Butler matrix was built and the effect of crossover leakage on the beams was calculated:

| Crossover leakage | Column phase error | Result |
| --- | --- | --- |
| −15 dB | ±40…220° | beams break up |
| −25 dB and below | a few degrees | beams in the right place |

The leakage looks small, but the signal passes through many crossovers and the stray part at each one accumulates and corrupts the phase.

**How the two-hybrid crossover works:** the first hybrid splits the signal into two paths (90° apart) and the second hybrid recombines them. The phases add so that all power goes to the diagonal port and cancels at the straight port. Hybrid-to-hybrid distance dx = a + w50 + 2·Lf ≈ 31.84 mm.

## 8. Butler matrix

The 8×8 Butler matrix is a passive network: whichever of its 8 inputs is driven, it distributes the signal to the 8 columns with **equal amplitude (−9.03 dB)** and a **constant phase step**. Mathematically it is an analogue FFT: each input corresponds to a spatial frequency, i.e. a beam direction.

```mermaid
flowchart LR
    A[STM32<br/>3 GPIO bits] --> B[SP8T<br/>switch]
    B --> C[Stage 1<br/>4 hybrids]
    C --> D[Stage 2<br/>4 hybrids]
    D --> E[Stage 3<br/>4 hybrids]
    E --> F[8 columns<br/>64 patches]
```

Fixed delay lines and crossovers sit between the stages (not shown).

| Part | Count |
| --- | --- |
| Main hybrids (3 stages × 4) | 12 |
| Crossovers (minimum-count planar layout) | 16 (2 hybrids each → 32 hybrids) |
| Total hybrids | 44 |
| Fixed delay lines | stage 1–2: 90/45°, stage 2–3: 90°, column outputs: 0/22.5/45/67.5° |

**Phase steps and beam angles.** For input m the phase difference between columns is ±22.5°, ±67.5°, ±112.5° or ±157.5°. The beam angle is:

```latex
\sin\theta_m = \frac{\Delta\phi_m\,\lambda_0}{2\pi d} = \frac{\Delta\phi_m}{180^\circ} \quad (d = \lambda_0/2)
```

| Phase step | Theoretical angle | Simulation (full array, CST) |
| --- | --- | --- |
| 22.5° | 7.2° | +7° / −6° |
| 67.5° | 22.0° | ±21° |
| 112.5° | 38.7° | ±37° |
| 157.5° | 61.0° | +55° / −56° |

- The outermost beam sits at 55–56° instead of 61°: the single-patch pattern falls off at wide angles, which pulls the peak of the total pattern inwards.
- Choosing the input order [1, 5, 3, 7, 2, 6, 4, 8] reduced the number of crossovers from 26 to 16.
- **Equal-length rule:** compensation lines give the same phase to paths that do not pass through a crossover. Line lengths must be held to ±0.3 mm; 0.3 mm ≈ 3° of phase error (λg = 34.9 mm).
- The Butler matrix was evaluated with `scripts/butler_network.py` using the real hybrid and crossover S-parameters from CST; all 8 beams came out with equal amplitude and the correct phase step.
- **Switch control:** the 3 control lines of the SP8T go to 3 GPIOs of the STM32. The binary value of (input number − 1) is written (e.g. input 4 = 011).

## 9. Full-array simulation and results

All 64 elements were simulated in CST including inter-column coupling, and the Butler weights were applied. All 8 beams point in the theoretical directions; the inner beams reach 22.5–22.8 dBi in the scan plane.

**Method:** CST time-domain solver, 30 cells/λ, 8.76 million cells; each port was excited until the energy in the structure decayed to −40 dB (8 ports, ~6.5 hours on CPU). For each port the S-matrix column and the embedded farfield (amplitude and phase) were exported over 5.70–5.90 GHz. The Butler weights (from the CST hybrid and crossover S-parameters) were applied in Python and the patterns summed. Calibration: at each port the radiated power is 71 % of the accepted power (radiation efficiency; the loss is mostly in the long series lines).

| Butler input | Direction | Realized gain (scan plane) | 3 dB width | Side lobe | Worst active S11 at 5.80 GHz |
| --- | --- | --- | --- | --- | --- |
| 1 / 8 | +7° / −6° | 22.8 / 22.8 dBi | 12.3° / 12.4° | −11.7 / −12.9 dB | −13.9 / −14.1 dB |
| 2 / 7 | +21° / −21° | 22.5 / 22.6 dBi | 13.0° / 13.5° | −9.6 / −12.9 dB | −13.0 / −12.8 dB |
| 3 / 6 | +37° / −37° | 21.6 / 21.5 dBi | 15.5° / 15.5° | −10.1 / −9.4 dB | −11.9 / −11.9 dB |
| 4 / 5 | +55° / −56° | 18.8 / 18.6 dBi | 20.0° / 20.0° | −7.6 / −6.9 dB | −6.8 / −6.2 dB |

- **Gain:** single column 15.1 dBi + 10·log(8) = 9 dB ≈ 24.1 dBi; with the Butler matrix's unequal amplitudes (0.5–1.0) and losses this becomes 22.8 dBi. The aperture limit is 23.8 dBi. In the first tuning (tilted column) the same beam had 17.7 dBi in the scan plane.
- **Over frequency:** the inner beams give 21.0–22.8 dBi over 5.70–5.85 GHz, with column tilt −1.1° … +1.7°. At 5.90 GHz the tilt grows to 4.5° and the gain drops to 16.7 dBi.
- **Column plane:** 3 dB width ~10–11°, side lobes −12.5 / −14.5 dB, front-to-back ratio 31 dB.
- **Coupling:** −19 dB between adjacent columns. Active S11 is the power returning to a port while all columns are driven together and includes coupling. On the ±55° beams the waves coupled from neighbouring columns return in phase and the worst port rises to −6…−7 dB; the average mismatch loss over the 8 ports is still 0.65 dB.
- **Butler loss not included:** these gains are at the array ports. Butler insertion loss and SP8T loss must be subtracted separately in the link budget.
- **Verification:** mesh convergence (20 / 30 cells/λ), the single column and the in-array column giving the same frequency (5.848 / 5.849 GHz), reciprocity (|Sij − Sji| < −67 dB), energy balance (radiated power ≤ accepted power), and beam directions matching theory.

## 10. Limitations

The design has two known limitations: narrow bandwidth and horizontal-only scanning.

**Narrow band.** The series column is a resonant structure and the cell phase changes with frequency. The band where the inner 6 beams have active S11 < −10 dB is ≈ 5.78–5.82 GHz; the ±55° beams stay at −7 dB at 5.80 GHz (ideal phases, worst port):

| Frequency | ±7° beam | ±21° | ±37° | ±55° |
| --- | --- | --- | --- | --- |
| 5.76 GHz | −12.9 dB | −10.6 dB | −8.2 dB | −4.3 dB |
| 5.78 GHz | −15.5 dB | −12.4 dB | −10.2 dB | −5.5 dB |
| 5.80 GHz | −15.1 dB | −12.6 dB | −11.6 dB | −7.2 dB |
| 5.82 GHz | −10.8 dB | −10.1 dB | −10.1 dB | −8.3 dB |
| 5.84 GHz | −7.8 dB | −7.4 dB | −7.5 dB | −7.3 dB |

If fabricated, the εr tolerance (±0.04) can shift the resonance by ±44 MHz, plus etching tolerance. Mitigation: build a single-column test board first, or tune the transmitter to the measured best frequency.

**Horizontal scanning only.** The Butler matrix changes phase only between columns; since each column has a single input, the beam is fixed (broadside) in the vertical direction. Because the Butler phases are fixed, the beams are limited to 8 directions; intermediate angles and amplitude tapering (side-lobe suppression) are not possible.

## 11. Steering along the y axis: problem and possible solutions

Vertical scanning requires access to each patch individually and a vertical pitch reduced to λ/2. Then 64 feed lines and the vertical beamforming networks no longer fit on the antenna layer.

**Why the current structure is not enough:**

1. **Single-input column:** with series feeding the phase between patches is fixed and cannot be changed externally.
2. **Pitch:** the in-column pitch is 30.75 mm = 0.59 λ₀. From the grating-lobe condition, vertical scanning is limited to sinθ < 1/0.59 − 1 = 0.68, i.e. ~43°. Full scanning needs 25.9 mm.
3. **Space:** in a 25.9 × 25.9 mm cell the patch takes 19.1 × 15.74 mm, leaving 6.8 mm horizontally and 10.2 mm vertically. 64 separate lines and 8 vertical beamformers do not fit on the same layer.

**Possible solutions:**

| Solution | How | Pros | Cons |
| --- | --- | --- | --- |
| Multilayer board + probe feed | Patches on the top layer, feed network below the ground; each patch reached by a via/probe | Antenna surface stays clear, lines move to a lower layer | Multilayer PTFE boards are expensive; alternative: two 2-layer boards back to back |
| Switched 2D Butler | Horizontal Butler → 8 SP8T → a separate vertical Butler per column; 3 horizontal + 3 vertical bits = 64 beams | Stays true to the original idea: passive, no phase shifters | 9 Butler matrices (~108 hybrids), vertical Butlers on boards perpendicular to the antenna ("brick"), 64 phase-matched cables |
| Per-element phase shifters (phased array) | 1:64 divider + 64 digital phase-shifter ICs, SPI from the STM32 | Continuous 2D scanning + amplitude tapering for side-lobe suppression | Cost (64 ICs), multilayer board |
| Reduced 4×4 2D Butler | Five 4×4 Butlers (20 hybrids), 5 SP4T, 4 control bits, 16 beams | Can be drawn on one board; the feed network spreads around the array | Gain drops to ~17 dBi, beams widen |
| Frequency scanning | The series column steers with frequency: −1° at 5.70 GHz, +4.5° at 5.90 GHz | No extra hardware | Only a few degrees, match degrades; not a real solution |

**Most practical next step in simulation:** simulate an 8×8 array with individually (probe-) fed patches full-wave once. With the resulting element patterns and the 64×64 coupling matrix, a phased array, amplitude tapering and a 2D Butler can all be applied and compared in Python on the same data.

## 12. Design FAQ

| Question | Short answer |
| --- | --- |
| Why 5.8 GHz? | Licence-free ISM band (5.725–5.875 GHz) used by Wi-Fi and drone video links; with λ = 51.7 mm an 8×8 array fits in ~21 × 25 cm. |
| Why patch antennas? | Planar, made as a PCB, on the same board as the feed network, and easy to array. |
| Why a Butler matrix instead of phase shifters? | The Butler matrix is passive: no power, control software or 64 ICs; one SP8T and 3 GPIOs are enough. The cost is 8 fixed beams and no amplitude control. |
| Why d = λ/2? | Scanning to ±90° without grating lobes. Smaller spacing increases coupling; larger spacing produces a second beam at wide angles. |
| Why is the outermost beam at 55° instead of 61°? | Total pattern = array factor × element pattern. The patch pattern falls off at wide angles, so the peak moves inwards. |
| Why are the side lobes not better than −13 dB? | The Butler matrix gives equal amplitudes; the theoretical limit of a uniform array is −13.2 dB. Lower side lobes need amplitude tapering (Taylor, Chebyshev), which a Butler matrix cannot do. |
| Why must crossover leakage be −25 dB? | From the network model: at −15 dB the column phases are off by ±40…220° and the beams break up; at −25 dB the error is a few degrees. |
| Why series feeding? | A parallel feed tree needs ~42 mm of width while the column spacing is 25.9 mm; a series feed stays within the patch width. |
| Was the column beam tilted, and how was it fixed? | In the first tuning the cell phase exceeded 360° by ~22°: the beam was tilted 5.5° and 4.5 dB of broadside gain was lost. L and Lc were tuned together using measured sensitivities and the transformer was redesigned: tilt 0.1°, broadside gain 17.7 → 22.8 dBi. |
| Why is the band narrow? | In the series column the cell phase depends on line length; when the frequency changes, phases and match degrade. The thin substrate (0.762 mm) also raises Q. |
| What is active S11? | The wave returning to a port while all columns are driven together, including power coupled from neighbours: Γ_act,i = Σ_j S_ij·a_j / a_i. |
| Why is active S11 −7 dB on the edge beams? | When scanning to ±55°, the waves coupled from neighbouring columns (−19 dB) add in phase at the port. The average loss over the 8 ports is 0.65 dB; this is common for wide-angle scanning. |
| Why trust the results? | Mesh convergence (20 → 30 cells/λ), the single column and the in-array column giving the same frequency, the difference between the two solvers explained by mesh, reciprocity (< −67 dB), energy balance, and gain consistent with the aperture limit (23.8 dBi). |
| Why both openEMS and CST? | Pre-design was done in openEMS (CST Learning Edition was limited to 100 000 cells). The final design was verified in commercial CST at 30 cells/λ; openEMS's coarse mesh placed the resonance ~110 MHz too low. |
| Are Butler losses included? | Phase and amplitude errors are (CST S-parameters). Hybrid insertion loss is not added to the gain; line loss on ZYF265D is ~0.13 dB/100 mm. |
| Where do adjacent beams cross? | Butler beams are orthogonal; adjacent beams cross at about −4 dB, so gain drops by that much at intermediate angles. |

## 13. Physical layout and connections

The product is a single two-layer ZYF265D board (~23 cm wide; ~55–70 cm long with the Butler matrix and switch). On the top side, from bottom to top: SMA and switch, Butler matrix, column feeds and the 64 patches. The whole bottom side is ground.

| Region (bottom to top) | Contents |
| --- | --- |
| Switch | J1 SMA (bottom edge), U1 SP8T, J2 5-pin header (5V, GND, A, B, C) |
| Butler matrix | 3 stages × 4 hybrids, 7 crossover layers (16 crossovers), 2 delay layers, column delays |
| Feed | λ/4 transformer per column (4.40 × 6.00 mm, 17.8 mm from the patch) |
| Antenna | 8 columns × 8 patches, column spacing 25.9 mm |

**Signal path:** transmitter → J1 SMA → common port (RFC) of the SP8T. The STM32 writes a 3-bit code to lines A, B, C and the switch connects one of RF1…RF8. The RF outputs are connected, left to right, to Butler inputs 1, 5, 3, 7, 2, 6, 4, 8. Butler output position k feeds column k through its transformer. In receive mode the same path works in reverse.

| RF port | Butler input | Beam | Code (C B A, typical) |
| --- | --- | --- | --- |
| RF1 | 1 | +7° | 000 |
| RF2 | 5 | −56° | 001 |
| RF3 | 3 | +37° | 010 |
| RF4 | 7 | −21° | 011 |
| RF5 | 2 | +21° | 100 |
| RF6 | 6 | −37° | 101 |
| RF7 | 4 | +55° | 110 |
| RF8 | 8 | −6° | 111 |

The code table must be checked against the switch datasheet; some SP8Ts use a different order.

## 14. Components and what they do

| Component | What it does | In this project |
| --- | --- | --- |
| Microstrip line | Copper strip above a ground plane; the "cable" carrying the RF signal. Its width sets the characteristic impedance. | 50 Ω = 2.10 mm; all interconnects |
| 50 Ω standard | If source, cable, connector and load have the same impedance, power passes without reflection (small S11). | SMA, switch, Butler ports |
| λ/4 transformer | A quarter-wave line transforms a load R at its end into Z₀²/R. A section of impedance Zt = √(Z₀·R) matches two different impedances. | Column input 17.7 Ω → 50 Ω (~29 Ω, 4.40 × 6.00 mm) |
| Delay line | Extra line length = extra phase, Δφ = 360°·Δl/λg. Acts as a fixed, frequency-dependent phase shifter. | 45° / 90° inside the Butler, 22.5–67.5° at the column outputs |
| 90° hybrid (branch-line) | 4-port square structure; splits the input equally between two outputs with 90° difference; the fourth port is isolated. | 12 Butler hybrids + 32 inside the crossovers |
| Crossover | Lets two lines "bridge" over each other on one layer; the signal passes to the diagonal port at 0 dB. | 16, each made of two hybrids |
| Butler matrix | Passive network of hybrids, delays and crossovers. Whichever of the N inputs is driven, it delivers equal amplitude and a constant phase step to N outputs; an analogue FFT. | 8×8, 8 beams |
| SP8T switch | Electronically connects the single input (RFC) to one of 8 outputs, selected by a 3-bit digital code. | Beam selector, controlled by the STM32 |
| Series feed | Patches connected end-to-end on one line; phase fixed by line length, compact. | 8 patches per column, Lc = 15.01 mm |
| Patch antenna | Half-wavelength copper rectangle over ground; radiates from its two edges. | 64 patches, 19.1 × 15.74 mm |

## 15. System context: range, board size, literature

The antenna is intended for a UAV video-link ground station: the gain extends range and beam switching tracks the UAV in azimuth.

- **Range (Friis, free space):** +6 dB of gain doubles the range. Baseline scenario ~2.6 km; with a 27 dBm transmitter, an 8 dBi antenna on the UAV and the lowest-rate coding (MCS0), theoretically ~18 km. Receive gain does not count towards EIRP. At 5 km the Fresnel-zone radius is ~8 m, so antenna height must be chosen accordingly.
- **Comparison with a NanoStation M2:** the M2 gives 10.4–11.2 dBi and a 55° beam at 2.4 GHz. Path loss at 5.8 GHz is 7.7 dB higher; the net difference is ±2 dB, i.e. similar range. The advantages of this antenna are the narrow beam, a cleaner band and electronic steering.
- **Board size:** array ~23 × 28 cm, ~23 × 55–70 cm with Butler matrix and switch. JLCPCB's PTFE limit is 590 × 438 mm. Options for fabrication: split the array and the Butler matrix onto two connected boards, or a 4×4 array + 4×4 Butler (~12.5 × 30 cm, ~17 dBi).

**Literature.** No published work with the same architecture (5.8 GHz, 8×8 Butler + 64-element series-fed array) was found (IEEE and ResearchGate access was limited). The closest:

| Work | Frequency | Architecture | Difference from this project |
| --- | --- | --- | --- |
| [Liu et al. 2018](https://par.nsf.gov/servlets/purl/10118260) | 60 GHz | 4×4 Butler + 4×10 series-fed array, two-hybrid crossover | same structure, 4×4 scale, mm-wave |
| [Simionato et al. 2024](https://www.sciencedirect.com/science/article/abs/pii/S1434841124002905) | 60 GHz | 4×4 Butler + series-fed columns, frequency-steered elevation | custom fabrication process, 4×4 |
| [Gil-Martínez et al. 2026](https://ieeexplore.ieee.org/document/11214254/) | 5.18–5.72 GHz | 4×4 Butler + leaky-wave, 2D scanning with Wi-Fi channels (32 beams) | Butler + Wi-Fi-channel 2D scanning is no longer new |
| [Eshaghi & Rashidzadeh 2022](https://ieeexplore.ieee.org/document/9967033) | 5.8 GHz | 4×4 Butler + array | same frequency, smaller scale |

What distinguishes this project: 8×8 scale at 5.8 GHz, tilt-corrected (broadside) series columns, and the UAV ground-station application.

## Formula summary

| Purpose | Formula | Value in this project |
| --- | --- | --- |
| Wavelength | λ₀ = c / f₀ | 51.7 mm |
| Guided wavelength | λg = λ₀ / √εeff | 34.9 mm (50 Ω line) |
| Patch width | W = c / (2f₀) · √(2 / (εr + 1)) | 19.1 mm |
| Patch length | L = c / (2f₀√εeff) − 2ΔL | 15.5 mm → 15.74 mm (CST, tuned with the column) |
| Cell phase / column tilt | φ_cell − 360° = 360° · (p / λ₀) · sinθ_y | 22° in the first tuning → 5.5° tilt; final ≈ 0° |
| Shift from εr tolerance | Δf / f ≈ Δεr / (2εr) | ±0.04 → ±44 MHz |
| Quarter-wave transformer | Zt = √(Z₀·R) | 17.7 Ω load → ~29 Ω, 4.40 × 6.00 mm |
| Hybrid series branch | Z₀ / √2 | 35.4 Ω (3.44 mm) |
| Grating-lobe condition | d / λ₀ < 1 / (1 + \|sinθ₀\|) | d = λ₀/2 → satisfied at all angles |
| Beam angle | sinθ = Δφ·λ₀ / (2πd) | ±7.2°, ±22°, ±38.7°, ±61° (theoretical) |
| Array factor | AF(θ) = Σ aₙ · e^{j n (k d sinθ + Δφ)} | N = 8 |
| 3 dB beamwidth | θ₃dB ≈ 0.886 λ₀ / (N d cosθ₀) | 12.7° (broadside), 22° (55°) |
| Aperture directivity | D ≈ 4πA / λ₀² | 23.8 dBi |
| Active reflection | Γ_act,i = Σ_j S_ij a_j / a_i | inner beams < −11.9 dB at 5.80 GHz |
| Line phase / length error | Δφ = 360° · Δl / λg | 0.3 mm ≈ 3° |
