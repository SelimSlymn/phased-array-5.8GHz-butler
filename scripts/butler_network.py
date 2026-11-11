# -*- coding: utf-8 -*-
"""
8x8 Butler matrix network calculation (planar layout with 16 crossovers).

Inputs : s-parameters/hybrid_762.s4p and s-parameters/crossover_762.s4p
         (if the crossover file is missing, the crossover is computed from
         two hybrids in cascade).
Outputs: column amplitude/phase for each input -> s-parameters/butler_weights_762.txt,
         printed beam angle and side-lobe level of the array factor,
         results/cst/butler_array_factor.png (if matplotlib is installed).

Run from the project folder:
    python scripts/butler_network.py          (5.80 GHz)
    python scripts/butler_network.py 5.75     (other frequency)
Requires: Python 3 + numpy (matplotlib optional, for the plot)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_touchstone  # noqa: E402

F0 = float(sys.argv[1]) if len(sys.argv) > 1 else 5.8
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPAR_DIR = os.path.join(ROOT, "s-parameters")
OUT_DIR = os.path.join(ROOT, "results", "cst")


def crossover_from_two_hybrids(SA, SB, line_deg=90.0):
    """Ports 3,4 of hybrid A connected to ports 1,2 of hybrid B by ideal 50 ohm lines."""
    S = np.zeros((8, 8), complex)
    S[:4, :4] = SA
    S[4:, 4:] = SB
    t = np.exp(-1j * np.deg2rad(line_deg))
    ext, inner = [0, 1, 6, 7], [2, 3, 4, 5]
    C = np.zeros((4, 4), complex)
    C[0, 2] = C[2, 0] = t
    C[1, 3] = C[3, 1] = t
    See = S[np.ix_(ext, ext)]
    Sei = S[np.ix_(ext, inner)]
    Sie = S[np.ix_(inner, ext)]
    Sii = S[np.ix_(inner, inner)]
    return See + Sei @ C @ np.linalg.solve(np.eye(4) - Sii @ C, Sie)


fh, Sh = read_touchstone(os.path.join(SPAR_DIR, "hybrid_762.s4p"))
k = np.argmin(abs(fh - F0))
H = Sh[k]
xfile = os.path.join(SPAR_DIR, "crossover_762.s4p")
if os.path.exists(xfile) or os.path.exists(xfile + ".zip"):
    fx, Sx = read_touchstone(xfile)
    X = Sx[np.argmin(abs(fx - F0))]
    source = "crossover_762.s4p (CST)"
else:
    X = crossover_from_two_hybrids(H, H, 90 * F0 / 5.8)
    source = "computed from two hybrids"


def db(x):
    return 20 * np.log10(abs(x))


print("Frequency: %.3f GHz" % fh[k])
print("Hybrid   : S31 %.2f dB, S41 %.2f dB, phase difference %.1f deg" %
      (db(H[2, 0]), db(H[3, 0]), (np.angle(H[2, 0] / H[3, 0], deg=True))))
print("Crossover (%s): through %.2f dB, straight leakage S31 %.1f dB, S11 %.1f dB" %
      (source, db(X[3, 0]), db(X[2, 0]), db(X[0, 0])))

# ---------------------------------------------------------------- layout plan
S1 = [(0, 4), (1, 5), (2, 6), (3, 7)]
S2 = [(0, 2), (1, 3), (4, 6), (5, 7)]
S3 = [(0, 1), (2, 3), (4, 5), (6, 7)]
INPUT_ORDER = [0, 4, 2, 6, 1, 5, 3, 7]          # physical input order, left to right
PLAN = [  # (stage name, hybrid pairs, crossover layers placed before this stage)
    ("stage1", S1, []),
    ("stage2", S2, [[1, 3, 5], [2, 4], [3]]),     # position indices (from 0): p <-> p+1
    ("stage3", S3, [[1, 5]]),
    ("output", None, [[1, 3, 5], [2, 4], [1, 3, 5]]),
]
DELAY_12 = np.array([90, 90, 0, 0, 0, 45, 0, 45.])    # delay by line label (deg)
DELAY_23 = np.array([90, 0, 0, 0, 90, 0, 0, 0.])
DELAY_COL = np.array([0, 22.5, 45, 67.5, 0, 22.5, 45, 67.5])


def butler(H, X, f=F0):
    T = H[2:, :2]
    Xc = X[2:, :2]
    comp = np.exp(1j * np.angle(X[3, 0]))           # equal phase on lines that skip a crossover
    M = np.zeros((8, 8), complex)
    for inp in range(8):
        v = np.zeros(8, complex)
        lab = list(INPUT_ORDER)
        v[lab.index(inp)] = 1
        for name, pairs, layers in PLAN:
            for sw in layers:
                nv = v * comp
                nl = lab[:]
                for p in sw:
                    a, b = v[p], v[p + 1]
                    nv[p] = Xc[0, 0] * a + Xc[0, 1] * b
                    nv[p + 1] = Xc[1, 0] * a + Xc[1, 1] * b
                    nl[p], nl[p + 1] = lab[p + 1], lab[p]
                v, lab = nv, nl
            if pairs is None:
                break
            idx = {lbl: i for i, lbl in enumerate(lab)}
            for p, q in pairs:
                a, b = idx[p], idx[q]
                x, y = v[a], v[b]
                v[a] = T[0, 0] * x + T[0, 1] * y
                v[b] = T[1, 0] * x + T[1, 1] * y
            g = {"stage1": DELAY_12, "stage2": DELAY_23, "stage3": np.zeros(8)}[name]
            v = v * np.exp(-1j * np.deg2rad(np.array([g[lbl] for lbl in lab]) * f / 5.8))
        M[:, inp] = v * np.exp(-1j * np.deg2rad(DELAY_COL * f / 5.8))
    return M


M = butler(H, X)

# ---------------------------------------------------------------- results
th = np.linspace(-90, 90, 3601)
n = np.arange(8)


def beam(w):
    af = np.abs(np.exp(1j * np.pi * np.outer(np.sin(np.deg2rad(th)), n)) @ w)
    af = 20 * np.log10(af / af.max() + 1e-12)
    peak = th[np.argmax(af)]
    local = [af[i] for i in range(1, len(af) - 1) if af[i] > af[i - 1] and af[i] > af[i + 1]]
    sll = sorted(local)[-2] if len(local) > 1 else -99
    return peak, sll, af


print("\nInput | amplitude range (dB) | mean phase step | phase deviation | beam | side lobe")
curves = []
for i in range(8):
    w = M[:, i]
    a = db(w)
    d = np.diff(np.angle(w, deg=True))
    d = (d + 180) % 360 - 180
    peak, sll, af = beam(w)
    curves.append(af)
    print("  %d   | %6.2f .. %6.2f      | %7.1f         | +/-%5.1f         | %6.1f | %5.1f dB"
          % (i + 1, a.min(), a.max(), d.mean(), np.abs(d - d.mean()).max(), peak, sll))

# ---------------------------------------------------------------- weights file
lines = [
    "Butler weights (0.762 mm, hybrid_762 + crossover_762, %.2f GHz)" % fh[k],
    "CST: Post-Processing > Combine Results. For each Butler input enter the",
    "amplitude and phase of the 8 ports as below (Port n = column n, left to right).",
    "Input 1 ~ +7 deg, 2 ~ +22, 3 ~ +39, 4 ~ +61, 5 ~ -61, 6 ~ -39, 7 ~ -22, 8 ~ -6",
    "",
]
for i in range(8):
    w = M[:, i]
    a = abs(w) / abs(w).max()
    p = np.angle(w, deg=True)
    p = (p - p[0] + 180) % 360 - 180
    lines.append("Input %d:" % (i + 1))
    for c in range(8):
        lines.append("   Port %d  amplitude %.3f  phase %7.1f" % (c + 1, a[c], p[c]))
wfile = os.path.join(SPAR_DIR, "butler_weights_762.txt" if abs(F0 - 5.8) < 1e-6 else "butler_weights_762_%.2fGHz.txt" % F0)
with open(wfile, "w") as fo:
    fo.write("\n".join(lines) + "\n")
print("\nWeights written:", wfile)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 5))
    for i, af in enumerate(curves):
        plt.plot(th, af, label="input %d" % (i + 1))
    plt.ylim(-40, 2)
    plt.xlim(-90, 90)
    plt.grid(alpha=.3)
    plt.xlabel("Angle from broadside (deg)")
    plt.ylabel("Normalized array factor (dB)")
    plt.title("8x8 Butler matrix, 16 crossovers, %.2f GHz (CST hybrid + crossover)" % fh[k])
    plt.legend(ncol=4, fontsize=8)
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "butler_array_factor.png")
    plt.savefig(out, dpi=130, bbox_inches="tight")
    print("Plot saved:", out)
except ImportError:
    print("(matplotlib not installed, no plot)")
