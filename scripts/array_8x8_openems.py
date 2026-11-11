# -*- coding: utf-8 -*-
"""
5.8 GHz 8x8 series-fed patch array - openEMS full-wave simulation (pre-design)
(the same series 1x8 column as designed in CST, 8 side by side)

USAGE (in a command prompt, in the folder of this file):

  python array_8x8_openems.py show          -> open the geometry in AppCSXCAD (check)
  python array_8x8_openems.py column        -> single column only (quick test, comparison with CST)
  python array_8x8_openems.py run           -> all 8 columns, 4 runs (using symmetry)
  python array_8x8_openems.py run full      -> 8 runs without symmetry (verification)
  python array_8x8_openems.py results       -> produce all plots and the table

If runs are interrupted, repeat the same command: finished runs are skipped.
Results: .npz files and .png plots in RESULTS_DIR.

Environment variables: PROFILE (762 / 800), CELLS_PER_LAMBDA, LC, END_CRITERIA.
"""
import os, sys, time, shutil
import numpy as np

# ------------------------------------------------------------------ settings
RESULTS_DIR = r"C:\CST\openems_results" if os.name == "nt" else os.path.expanduser("~/openems_results")
WORK_DIR = r"C:\openems_tmp" if os.name == "nt" else os.path.expanduser("~/openems_tmp")
N_THREADS = 0             # 0 = all cores
CELLS_PER_LAMBDA = int(os.environ.get('CELLS_PER_LAMBDA', 30))   # cells per wavelength (20 did not converge, use 30)

# ------------------------------------------------------------------ design (same as CST, mm)
f0 = 5.8e9
fc = 1.2e9                # Gaussian half bandwidth (4.6 - 7.0 GHz)
# PROFILE: 800 = F4BM265 0.8 mm (first design), 762 = JLCPCB ZYF265D 0.762 mm (production)
PROFILE = os.environ.get('PROFILE', '762')
if PROFILE == '800':
    h, er, tand = 0.8, 2.65, 0.001
    W, L = 19.1, 15.02
    _w50, _wt, _SUFFIX, _S4P = 2.2, 3.92, "", ""
else:
    h, er, tand = 0.762, 2.65, 0.0019
    W, L = 19.1, 15.04
    _w50, _wt, _SUFFIX, _S4P = 2.10, 3.73, "_k762", "_762"
Lc = float(os.environ.get('LC', 18.0))    # line between patches (in a command prompt: set LC=18)
p = L + Lc                # patch pitch (along the column)
w50 = _w50
d1, lt, wt = 10.73, 8.55, _wt   # distance to transformer, transformer length, transformer width
Lport = 20.0              # MSL port line (instead of 5 mm in CST; being 50 ohm it only shifts the phase reference)
d = 25.9                  # column spacing
END_CRITERIA = float(os.environ.get("END_CRITERIA", 1e-3))   # energy end criterion: 1e-3 = -30 dB, 1e-4 = -40 dB
_END_TAG = "" if END_CRITERIA >= 1e-3 else f"_e{round(-10*np.log10(END_CRITERIA))}"
TAG_COLUMN = f"column_Lc{Lc:g}_t2_h{CELLS_PER_LAMBDA}{_SUFFIX}{_END_TAG}"
TAG_ARRAY = f"array_Lc{Lc:g}_t2_h{CELLS_PER_LAMBDA}{_SUFFIX}{_END_TAG}"
N_COLS = 8
margin = 13.0              # substrate edge margin
air_gap = 30.0               # air between substrate and PML

def column_x(n_cols):
    return [(c - (n_cols - 1) / 2) * d for c in range(n_cols)]

y0b = -3.5 * p - L / 2                 # lower edge of the first patch
y_tr_top = y0b - d1
y_tr_bot = y0b - d1 - lt
y_port = y_tr_bot - Lport           # port (board) edge
y_board_top = 3.5 * p + L / 2 + margin


def build_model(n_cols, excite_port):
    """excite_port: index of the column to excite (0..n_cols-1)"""
    from CSXCAD import ContinuousStructure
    from openEMS import openEMS
    from openEMS.physical_constants import C0, EPS0

    FDTD = openEMS(NrTS=300000, EndCriteria=END_CRITERIA)   # 1e-3 = -30 dB
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond(['PML_8'] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)

    fmax = f0 + fc
    res = C0 / fmax / 1e-3 / np.sqrt(er) / CELLS_PER_LAMBDA   # ~1.35 mm (for 20)
    res_air = C0 / fmax / 1e-3 / 20                 # ~2.2 mm

    xs = column_x(n_cols)
    x_min = xs[0] - W / 2 - margin
    x_max = xs[-1] + W / 2 + margin

    kappa = 2 * np.pi * f0 * EPS0 * er * tand
    sub = CSX.AddMaterial('F4BM265', epsilon=er, kappa=kappa)
    sub.AddBox([x_min, y_port, 0], [x_max, y_board_top, h], priority=0)

    gnd = CSX.AddMetal('gnd')
    gnd.AddBox([x_min, y_port, 0], [x_max, y_board_top, 0], priority=10)

    cu = CSX.AddMetal('copper')
    for xc in xs:
        for k in range(8):
            yc = (k - 3.5) * p
            cu.AddBox([xc - W / 2, yc - L / 2, h], [xc + W / 2, yc + L / 2, h], priority=10)
            if k < 7:
                cu.AddBox([xc - w50 / 2, yc + L / 2, h], [xc + w50 / 2, yc + L / 2 + Lc, h], priority=10)
        cu.AddBox([xc - w50 / 2, y_tr_top, h], [xc + w50 / 2, y0b, h], priority=10)
        cu.AddBox([xc - wt / 2, y_tr_bot, h], [xc + wt / 2, y_tr_top, h], priority=10)

    # --- mesh
    mesh.AddLine('x', [x_min - air_gap, x_max + air_gap])
    mesh.AddLine('y', [y_port - air_gap, y_board_top + air_gap])
    mesh.AddLine('z', np.linspace(0, h, 5))
    mesh.AddLine('z', [-20, h + 45])
    for xc in xs:
        mesh.AddLine('x', xc)
    FDTD.AddEdges2Grid(dirs='xy', properties=cu, metal_edge_res=res / 3)
    mesh.AddLine('x', [x_min, x_max])
    mesh.AddLine('y', [y_port, y_port + 2, y_board_top])
    mesh.SmoothMeshLines('x', res, 1.4)
    mesh.SmoothMeshLines('y', res, 1.4)
    mesh.SmoothMeshLines('z', res_air, 1.4)

    # --- ports (all terminated in 50 ohm, only one excited)
    ports = []
    for c, xc in enumerate(xs):
        ports.append(FDTD.AddMSLPort(c + 1, cu,
                                       [xc - w50 / 2, y_port, h], [xc + w50 / 2, y_tr_bot, 0],
                                       'y', 'z', excite=1 if c == excite_port else 0,
                                       FeedShift=2.0, MeasPlaneShift=Lport / 2, Feed_R=50,
                                       priority=5))

    nf2ff = FDTD.CreateNF2FFBox(frequency=F_PATTERN)
    return FDTD, CSX, ports, nf2ff


FREQS = np.linspace(4.8e9, 6.8e9, 401)
F_PATTERN = [5.70e9, 5.75e9, 5.8e9, 5.85e9, 5.9e9]
THETA = np.arange(-90.0, 90.5, 0.5)
PHI = [0.0, 90.0]


def run_port(n_cols, i, tag):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out_file = os.path.join(RESULTS_DIR, f"{tag}_port{i + 1}.npz")
    if os.path.exists(out_file):
        print(f"[skipped] {out_file} already exists")
        return
    work_path = os.path.join(WORK_DIR, f"{tag}_port{i + 1}")
    os.makedirs(work_path, exist_ok=True)
    FDTD, CSX, ports, nf2ff = build_model(n_cols, i)
    g = CSX.GetGrid()
    nx, ny, nz = len(g.GetLines('x')), len(g.GetLines('y')), len(g.GetLines('z'))
    print(f"\n=== {tag}: port {i + 1} excited | mesh {nx}x{ny}x{nz} = {nx * ny * nz / 1e6:.2f} M cells ===")
    t0 = time.time()
    FDTD.Run(work_path, cleanup=True, numThreads=N_THREADS, verbose=1)
    print(f"time: {(time.time() - t0) / 60:.1f} min")

    uinc, uref = [], []
    for pt in ports:
        pt.CalcPort(work_path, FREQS, ref_impedance=50)
        uinc.append(pt.uf_inc)
        uref.append(pt.uf_ref)
    uinc, uref = np.array(uinc), np.array(uref)

    r = nf2ff.CalcNF2FF(work_path, F_PATTERN, THETA, PHI, center=[0, 0, h * 1e-3])
    np.savez(out_file, f=FREQS, uinc=uinc, uref=uref, i=i, n=n_cols,
             f_or=np.array(F_PATTERN), theta=THETA, phi=np.array(PHI),
             Eth=np.array(r.E_theta), Eph=np.array(r.E_phi), Prad=np.array(r.Prad))
    s = uref[i] / uinc[i]
    k = np.argmin(abs(FREQS - f0))
    print(f"saved: {out_file} | S{i + 1}{i + 1}(5.8 GHz) = {20 * np.log10(abs(s[k])):.1f} dB")
    shutil.rmtree(work_path, ignore_errors=True)


# ------------------------------------------------------------------ post-processing
def load_runs(tag, n_cols, symmetry):
    """For each run: S-matrix column and farfield normalized to a 1 V incident wave."""
    S = np.zeros((len(FREQS), n_cols, n_cols), complex)
    Eth = Eph = None
    for i in range(n_cols):
        fn = os.path.join(RESULTS_DIR, f"{tag}_port{i + 1}.npz")
        mirrored = False
        if not os.path.exists(fn):
            if symmetry and os.path.exists(os.path.join(RESULTS_DIR, f"{tag}_port{n_cols - i}.npz")):
                fn = os.path.join(RESULTS_DIR, f"{tag}_port{n_cols - i}.npz"); mirrored = True
            else:
                raise FileNotFoundError(fn)
        z = np.load(fn)
        inc = z['uinc'][z['i']]
        Si = z['uref'] / inc                     # (port, frequency)
        kf = [np.argmin(abs(z['f'] - fo)) for fo in z['f_or']]
        eth = z['Eth'] / inc[kf][:, None, None]  # (frequency, theta, phi)
        eph = z['Eph'] / inc[kf][:, None, None]
        if mirrored:                                 # mirror x -> -x
            Si = Si[::-1]
            eth = eth[:, ::-1, :].copy(); eph = eph[:, ::-1, :].copy()
            eth[:, :, 0] *= -1                   # phi=0 plane: E_theta changes sign
            eph[:, :, 1] *= -1                   # phi=90 plane: E_phi changes sign
            eth[:, :, 1] = eth[:, ::-1, 1]; eph[:, :, 1] = eph[:, ::-1, 1]  # at phi=90, theta is not mirrored
        S[:, :, i] = Si.T
        if Eth is None:
            Eth = np.zeros((n_cols,) + eth.shape, complex); Eph = np.zeros_like(Eth)
        Eth[i], Eph[i] = eth, eph
    return S, Eth, Eph, z


def realized_gain_db(w, Eth, Eph, kf):
    """w: incident wave amplitudes at the columns. Realized gain (dBi)."""
    eta0 = 376.73
    et = np.tensordot(w, Eth[:, kf], axes=1)
    ep = np.tensordot(w, Eph[:, kf], axes=1)
    Pinc = np.sum(abs(w) ** 2) / (2 * 50)
    U = (abs(et) ** 2 + abs(ep) ** 2) / (2 * eta0)   # r = 1 m
    return 10 * np.log10(4 * np.pi * U / Pinc + 1e-30)


def butler_weights():
    """Butler column weights (columns x inputs) from s-parameters/butler_weights_762.txt
    (written by butler_network.py). Only available for the 0.762 mm profile."""
    wf = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                      's-parameters', 'butler_weights_762.txt')
    if PROFILE != '762' or not os.path.exists(wf):
        print("[warning] Butler weights not found, Butler beams skipped")
        return None
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from common import read_butler_weights
    return read_butler_weights(wf).T


def beam_info(G, theta):
    i = np.argmax(G); peak = theta[i]
    local_max = [G[k] for k in range(1, len(G) - 1) if G[k] > G[k - 1] and G[k] > G[k + 1]]
    sll = sorted(local_max)[-2] - G[i] if len(local_max) > 1 else np.nan
    above = G >= G[i] - 3
    j = i
    while j > 0 and above[j - 1]: j -= 1
    k = i
    while k < len(G) - 1 and above[k + 1]: k += 1
    return peak, G[i], theta[k] - theta[j], sll


def array_results():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    tag = TAG_ARRAY
    S, Eth, Eph, z = load_runs(tag, N_COLS, symmetry=True)
    theta = z['theta']; kf = list(z['f_or']).index(5.8e9)
    k0 = np.argmin(abs(FREQS - f0))
    dB = lambda x: 20 * np.log10(abs(x) + 1e-30)

    # S-parameters
    fig, ax = plt.subplots(figsize=(9, 5))
    for i in range(4):
        ax.plot(FREQS / 1e9, dB(S[:, i, i]), label=f'S{i+1},{i+1}')
    ax.plot(FREQS / 1e9, dB(S[:, 4, 3]), 'k--', label='S5,4 (adjacent coupling)')
    ax.plot(FREQS / 1e9, dB(S[:, 5, 3]), 'k:', label='S6,4 (second neighbour)')
    ax.set_xlabel('Frequency (GHz)'); ax.set_ylabel('dB'); ax.set_ylim(-50, 0); ax.grid(alpha=.3); ax.legend()
    ax.set_title('8x8 array - column reflections and coupling (openEMS)')
    fig.savefig(os.path.join(RESULTS_DIR, 's_parameters.png'), dpi=130, bbox_inches='tight')

    print("\nS-matrix at 5.8 GHz (dB), row = receiving port, column = excited port")
    print(np.round(dB(S[k0]), 1))

    # beams
    cases = []
    for m, dphi in enumerate([-22.5, -67.5, -112.5, -157.5, 157.5, 112.5, 67.5, 22.5]):
        cases.append((f'ideal {dphi:+.1f}', np.exp(1j * np.deg2rad(dphi) * np.arange(N_COLS))))
    M = butler_weights()
    if M is not None:
        for g in range(8):
            cases.append((f'Butler input {g+1}', M[:, g]))

    rows = []
    fig, axs = plt.subplots(1, 2 if M is not None else 1, figsize=(14, 5), squeeze=False)
    for n, (name, w) in enumerate(cases):
        G = realized_gain_db(w, Eth, Eph, kf)[:, 0]
        peak, gmax, width, sll = beam_info(G, theta)
        Gact = (S[k0] @ w) / w
        act_db = dB(Gact)
        rows.append((name, gmax, peak, width, sll, act_db.max()))
        ax = axs[0][0 if name.startswith('ideal') else 1]
        ax.plot(theta, G, label=name)
    for ax, t in zip(axs[0], ['Ideal phases', 'Butler matrix (CST hybrid + crossover)']):
        ax.set_ylim(-10, 26); ax.set_xlim(-90, 90); ax.grid(alpha=.3); ax.set_xlabel('theta (deg), phi = 0')
        ax.set_ylabel('Realized gain (dBi)'); ax.set_title(t); ax.legend(fontsize=7, ncol=2)
    fig.savefig(os.path.join(RESULTS_DIR, 'beams_5p8GHz.png'), dpi=130, bbox_inches='tight')

    print("\n5.8 GHz | case | gain (dBi) | direction | 3 dB width | side lobe | worst active S11")
    with open(os.path.join(RESULTS_DIR, 'results_table.txt'), 'w', encoding='utf-8') as fo:
        for s in rows:
            line = f"{s[0]:18s} | {s[1]:5.1f} dBi | {s[2]:6.1f} | {s[3]:5.1f} | {s[4]:6.1f} dB | {s[5]:6.1f} dB"
            print(line); fo.write(line + "\n")
    print(f"\nPlots and table: {RESULTS_DIR}")


def column_results():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    z = np.load(os.path.join(RESULTS_DIR, TAG_COLUMN + '_port1.npz'))
    s11 = z['uref'][0] / z['uinc'][0]
    kf = list(z['f_or']).index(5.8e9)
    inc = z['uinc'][0][[np.argmin(abs(z['f'] - fo)) for fo in z['f_or']]]
    Eth = z['Eth'][None] / inc[None, :, None, None]; Eph = z['Eph'][None] / inc[None, :, None, None]
    G = realized_gain_db(np.array([1.0]), Eth, Eph, kf)
    k = np.argmin(abs(z['f'] - f0))
    band = (z['f'] > 5.4e9) & (z['f'] < 6.2e9)
    kmin = np.argmin(np.where(band, abs(s11), 9))
    t90 = beam_info(G[:, 1], z['theta'])
    print(f"S11 @5.8 GHz = {20*np.log10(abs(s11[k])):.1f} dB | minimum {20*np.log10(abs(s11[kmin])):.1f} dB @ {z['f'][kmin]/1e9:.3f} GHz")
    print(f"phi=90 (column plane): gain {t90[1]:.1f} dBi, direction {t90[0]:.1f}, width {t90[2]:.1f}, side lobe {t90[3]:.1f} dB")
    print("CST (reference): S11 -28 dB @ 5.80 GHz, 15.4 dBi, direction 3.0, width 9.8, side lobe -9.7 dB")
    print(f"--- Lc = {Lc} mm, cells/lambda = {CELLS_PER_LAMBDA} ---")
    print(" freq    |  S11  | beam dir.  | side lobe")
    for j, fo in enumerate(z['f_or']):
        Gj = realized_gain_db(np.array([1.0]), Eth, Eph, j)
        tj = beam_info(Gj[:, 1], z['theta'])
        sj = 20 * np.log10(abs(s11[np.argmin(abs(z['f'] - fo))]))
        print(f"  {fo/1e9:.2f}  | {sj:5.1f} | {tj[0]:6.1f}     | {tj[3]:5.1f} dB")
    fig, ax = plt.subplots()
    ax.plot(z['f'] / 1e9, 20 * np.log10(abs(s11))); ax.grid(alpha=.3); ax.set_xlabel('GHz'); ax.set_ylabel('S11 (dB)')
    fig.savefig(os.path.join(RESULTS_DIR, 'column_s11.png'), dpi=130)


if __name__ == '__main__':
    command = sys.argv[1] if len(sys.argv) > 1 else ''
    if command == 'show':
        FDTD, CSX, _, _ = build_model(N_COLS, 0)
        os.makedirs(WORK_DIR, exist_ok=True)
        fn = os.path.join(WORK_DIR, 'array.xml'); CSX.Write2XML(fn)
        from CSXCAD import AppCSXCAD_BIN
        os.system(AppCSXCAD_BIN + ' "{}"'.format(fn))
    elif command == 'column':
        run_port(1, 0, TAG_COLUMN); column_results()
    elif command == 'run':
        full = len(sys.argv) > 2 and sys.argv[2] == 'full'
        for i in (range(N_COLS) if full else range(N_COLS // 2)):
            run_port(N_COLS, i, TAG_ARRAY)
        array_results()
    elif command == 'results':
        array_results()
    else:
        print(__doc__)
