# -*- coding: utf-8 -*-
"""Shared readers for CST exports used by the analysis scripts.

- read_touchstone(path): any .sNp file (MA, DB or RI format, GHz/MHz/Hz)
- read_farfield(path):   CST ASCII farfield export (E-field, spherical,
                         columns: theta, phi, |E|, |Etheta|, arg Etheta, |Ephi|, arg Ephi)
- read_butler_weights(path): butler_agirliklar_762.txt -> (8 inputs x 8 ports) complex
"""
import re
import numpy as np

ETA0 = 376.730313668  # free-space wave impedance (ohm)


def read_touchstone(path):
    nports = int(re.search(r"\.s(\d+)p", path.lower()).group(1))
    unit, fmt = 1.0, "MA"
    nums = []
    with open(path, errors="ignore") as fh:
        for line in fh:
            s = line.strip()
            if not s or s.startswith("!"):
                continue
            if s.startswith("#"):
                tok = s[1:].upper().split()
                unit = {"GHZ": 1.0, "MHZ": 1e-3, "KHZ": 1e-6, "HZ": 1e-9}.get(tok[0], 1.0)
                for t in ("MA", "DB", "RI"):
                    if t in tok:
                        fmt = t
                continue
            nums += [float(x) for x in s.split("!")[0].split()]
    per = 1 + 2 * nports * nports
    arr = np.array(nums).reshape(-1, per)
    f = arr[:, 0] * unit
    a, b = arr[:, 1::2], arr[:, 2::2]
    if fmt == "MA":
        v = a * np.exp(1j * np.deg2rad(b))
    elif fmt == "DB":
        v = 10 ** (a / 20) * np.exp(1j * np.deg2rad(b))
    else:
        v = a + 1j * b
    S = v.reshape(-1, nports, nports)
    if nports == 2:  # Touchstone 2-port order is S11 S21 S12 S22
        S = S.transpose(0, 2, 1)
    return f, S


def read_farfield(path):
    d = np.loadtxt(path, skiprows=2)
    th, ph = d[:, 0], d[:, 1]
    et = 10 ** (d[:, 3] / 20) * np.exp(1j * np.deg2rad(d[:, 4]))
    ep = 10 ** (d[:, 5] / 20) * np.exp(1j * np.deg2rad(d[:, 6]))
    return th, ph, et, ep


def read_butler_weights(path):
    txt = open(path, encoding="utf-8", errors="ignore").read()
    out = []
    for block in re.split(r"Giris \d+:", txt)[1:]:
        pairs = re.findall(r"genlik\s+([\d.]+)\s+faz\s+([-\d.]+)", block)
        out.append([float(m) * np.exp(1j * np.deg2rad(float(p))) for m, p in pairs])
    return np.array(out)


def realized_gain(weights, et_ports, ep_ports):
    """Realized gain of the weighted sum of per-port farfields.

    CST exports E at 1 m for 0.5 W stimulated power per port, so
    G = 4*pi*|sum a_i E_i|^2 / (eta0 * sum |a_i|^2).
    """
    et = weights @ et_ports
    ep = weights @ ep_ports
    return 4 * np.pi * (np.abs(et) ** 2 + np.abs(ep) ** 2) / (ETA0 * np.sum(np.abs(weights) ** 2))


def cut(theta, phi, values, phi0):
    """Signed-theta cut through the plane phi0 / phi0+180 (theta<0 is phi0+180)."""
    a, b = [], []
    for t in np.unique(theta):
        m = np.isclose(theta, t) & np.isclose(phi, phi0)
        if m.any():
            a.append(t)
            b.append(values[m][0])
        if 0 < t < 180:
            m = np.isclose(theta, t) & np.isclose(phi, (phi0 + 180) % 360)
            if m.any():
                a.append(-t)
                b.append(values[m][0])
    o = np.argsort(a)
    return np.array(a)[o], np.array(b)[o]


def beam_metrics(angle, gain_db):
    """Peak direction, -3 dB width and peak side-lobe level (dB) of a 1D cut."""
    x = np.arange(angle.min(), angle.max() + 0.05, 0.1)
    y = np.interp(x, angle, gain_db)
    c = int(np.argmax(y))
    pk = y[c]
    r = c
    while r < len(y) - 1 and y[r] > pk - 3:
        r += 1
    l = c
    while l > 0 and y[l] > pk - 3:
        l -= 1
    hpbw = x[r] - x[l]
    # main lobe ends at the first null on each side
    rr = c
    while rr < len(y) - 1 and y[rr + 1] < y[rr]:
        rr += 1
    ll = c
    while ll > 0 and y[ll - 1] < y[ll]:
        ll -= 1
    side = np.concatenate([y[:ll], y[rr + 1:]])
    sll = (side.max() - pk) if side.size else np.nan
    return x[c], pk, hpbw, sll
