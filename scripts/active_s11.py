# -*- coding: utf-8 -*-
"""Active S11 of the 8 array ports for each Butler input.

Gamma_act,i = sum_j S_ij a_j / a_i

Inputs : s-parameters/array_8x8_762.s8p(.zip), s-parameters/butler_weights_762.txt
Outputs: results/cst/active_s11.csv, results/cst/active_s11.png

Run from the project folder:  python scripts/active_s11.py
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_touchstone, read_butler_weights  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S8P = os.path.join(ROOT, "s-parameters", "array_8x8_762.s8p")
WTS = os.path.join(ROOT, "s-parameters", "butler_weights_762.txt")
OUT = os.path.join(ROOT, "results", "cst")
F0 = 5.80

os.makedirs(OUT, exist_ok=True)
f, S = read_touchstone(S8P)
W = read_butler_weights(WTS)

gam = np.einsum("fij,kj->fki", S, W) / W[None, :, :]   # (freq, input, port)
act_db = 20 * np.log10(np.abs(gam))
worst = act_db.max(axis=2)                              # worst port per input

k0 = int(np.argmin(np.abs(f - F0)))
passive = 20 * np.log10(np.abs(np.diagonal(S, axis1=1, axis2=2)))

with open(os.path.join(OUT, "active_s11.csv"), "w") as fh:
    fh.write("butler_input," + ",".join(f"port{p}_dB" for p in range(1, 9)) + ",worst_dB\n")
    for i in range(8):
        fh.write(f"{i + 1}," + ",".join(f"{v:.2f}" for v in act_db[k0, i]) + f",{worst[k0, i]:.2f}\n")

print(f"Frequency: {f[k0]:.3f} GHz")
print("Passive S11 (dB), ports 1-8:", " ".join(f"{v:.1f}" for v in passive[k0]))
for i in range(8):
    print(f"Butler input {i + 1}: worst active S11 {worst[k0, i]:6.2f} dB")

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    for i in range(8):
        ax.plot(f, worst[:, i], lw=1.1, label=f"input {i + 1}")
    ax.plot(f, passive.max(axis=1), "k--", lw=1, label="passive (worst port)")
    ax.axhline(-10, color="gray", lw=0.7, ls=":")
    ax.axvline(F0, color="gray", lw=0.7, ls=":")
    ax.set_xlim(5.6, 6.0)
    ax.set_ylim(-30, 0)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Worst-port active |S11| (dB)")
    ax.set_title("Active reflection per Butler input (CST)")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7, ncol=3)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, "active_s11.png"), dpi=150)
except ImportError:
    pass
