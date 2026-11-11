# -*- coding: utf-8 -*-
"""Single 1x8 series-fed column: gain, beam tilt, -3 dB width and side lobes
in the column plane (phi = 90/270) and the scan plane (phi = 0/180).

Input : <ff_dir>/ff_5p80_port1.txt  (cst-makrolar/cst_farfield_sutun.bas)
Output: sonuclar/cst/sutun_desen.png, printed table

Run:  python scriptler/sutun_desen.py C:\\CST\\ff_sutun
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ortak import read_farfield, realized_gain, cut, beam_metrics  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF_DIR = sys.argv[1] if len(sys.argv) > 1 else r"C:\CST\ff_sutun"
OUT = os.path.join(ROOT, "sonuclar", "cst")
os.makedirs(OUT, exist_ok=True)

th, ph, et, ep = read_farfield(os.path.join(FF_DIR, "ff_5p80_port1.txt"))
g_db = 10 * np.log10(realized_gain(np.array([1.0]), et[None, :], ep[None, :]))

res = {}
for name, phi0 in (("column plane (phi=90)", 90.0), ("scan plane (phi=0)", 0.0)):
    ang, val = cut(th, ph, g_db, phi0)
    res[name] = (ang, val)
    d, pk, bw, sll = beam_metrics(ang, val)
    extra = f", SLL {sll:6.1f} dB" if phi0 == 90.0 else ""
    print(f"{name:24s} peak {pk:5.1f} dBi at {d:+5.1f} deg, HPBW {bw:5.1f} deg{extra}")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for (name, (ang, val)), c in zip(res.items(), ("#1f4e79", "#c55a11")):
        ax.plot(ang, val, color=c, lw=1.2, label=name)
    ax.set_xlim(-90, 90)
    ax.set_ylim(-15, 20)
    ax.set_xlabel("Angle from broadside (deg)")
    ax.set_ylabel("Realized gain (dBi)")
    ax.set_title("Single 1x8 column at 5.80 GHz (CST)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "sutun_desen.png"), dpi=150)
except ImportError:
    pass
