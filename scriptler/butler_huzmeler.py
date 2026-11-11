# -*- coding: utf-8 -*-
"""Combine the 8 per-port CST farfields with the Butler weights.

For each Butler input: realized gain, beam direction, -3 dB width and
side-lobe level in the scan plane (phi = 0/180). The column (elevation)
plane is analysed by sutun_desen.py.

Inputs : <ff_dir>/ff_5p80_port1.txt ... port8.txt  (cst-makrolar/cst_farfield_aktar.bas)
         s-parametreleri/butler_agirliklar_762.txt
Outputs: sonuclar/cst/huzme_tablosu.csv, huzmeler_tarama.png, huzmeler_polar.png

Run:  python scriptler/butler_huzmeler.py C:\\CST\\ff_dizi
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import read_farfield, read_butler_weights, realized_gain, cut, beam_metrics  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF_DIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\CST\ff_dizi"
FREQ = sys.argv[2] if len(sys.argv) > 2 else "5p80"
WTS = os.path.join(ROOT, "s-parametreleri", "butler_agirliklar_762.txt")
OUT = os.path.join(ROOT, "sonuclar", "cst")
os.makedirs(OUT, exist_ok=True)

ports = [read_farfield(os.path.join(FF_DIR, f"ff_{FREQ}_port{p}.txt")) for p in range(1, 9)]
th, ph = ports[0][0], ports[0][1]
ET = np.array([p[2] for p in ports])
EP = np.array([p[3] for p in ports])
W = read_butler_weights(WTS)

rows, scan_cuts = [], []
for i, a in enumerate(W):
    g_db = 10 * np.log10(realized_gain(a, ET, EP))
    ang, val = cut(th, ph, g_db, 0.0)                  # scan plane
    d, pk, bw_s, sll_s = beam_metrics(ang, val)
    scan_cuts.append((ang, val))
    rows.append((i + 1, d, pk, bw_s, sll_s))

with open(os.path.join(OUT, f"huzme_tablosu_{FREQ}.csv"), "w") as fh:
    fh.write("butler_input,direction_deg,realized_gain_dBi,hpbw_scan_deg,sll_scan_dB\n")
    for r in rows:
        fh.write(",".join(f"{v:.2f}" if isinstance(v, float) else str(v) for v in r) + "\n")

print(" in | dir (deg) | gain (dBi) | HPBW scan | SLL scan")
for r in rows:
    print(f" {r[0]:2d} | {r[1]:8.1f} | {r[2]:9.1f} | {r[3]:8.1f} | {r[4]:7.1f}")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    cmap = plt.cm.viridis(np.linspace(0, 0.95, 8))
    fig, ax = plt.subplots(figsize=(8, 4.2))
    for i, (ang, val) in enumerate(scan_cuts):
        ax.plot(ang, val, color=cmap[i], lw=1.2, label=f"input {i + 1} ({rows[i][1]:+.0f}°)")
    ax.set_xlim(-90, 90)
    ax.set_ylim(-10, 32)
    ax.set_xlabel("Angle from broadside in the scan plane (deg)")
    ax.set_ylabel("Realized gain (dBi)")
    ax.set_title(f"Butler beams, {FREQ.replace('p', '.')} GHz (CST, at array ports)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=4, loc="upper center")
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"huzmeler_tarama_{FREQ}.png"), dpi=150)

    fig = plt.figure(figsize=(5.5, 5.5))
    axp = fig.add_subplot(projection="polar")
    for i, (ang, val) in enumerate(scan_cuts):
        axp.plot(np.radians(ang), np.clip(val, -10, None), color=cmap[i], lw=1.1)
    axp.set_theta_zero_location("N")
    axp.set_theta_direction(-1)
    axp.set_thetamin(-90)
    axp.set_thetamax(90)
    axp.set_rlim(-10, 25)
    axp.set_title("Scan-plane beams (realized gain, dBi)", fontsize=10)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, f"huzmeler_polar_{FREQ}.png"), dpi=150)
except ImportError:
    pass
