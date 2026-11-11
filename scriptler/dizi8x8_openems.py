# -*- coding: utf-8 -*-
"""
5.8 GHz 8x8 seri beslemeli patch dizisi - openEMS tam dalga simulasyonu
(CST'de tasarlanan seri 1x8 sutunun birebir aynisi, yan yana 8 adet)

KULLANIM (Komut Istemi'nde, bu dosyanin oldugu klasorde):

  python dizi8x8_openems.py goster          -> geometriyi AppCSXCAD ile ac (kontrol)
  python dizi8x8_openems.py sutun           -> sadece 1 sutun (hizli test, CST ile karsilastirma)
  python dizi8x8_openems.py calistir        -> 8 sutunun tamami, 4 kosu (simetri ile)
  python dizi8x8_openems.py calistir tam    -> 8 kosu, simetri kullanmadan (dogrulama)
  python dizi8x8_openems.py sonuc           -> tum grafikleri ve tabloyu uret

Kosular kesilirse ayni komutu tekrar ver: biten kosular atlanir.
Sonuclar: SONUC_KLASORU icinde .npz dosyalari ve .png grafikler.
"""
import os, sys, time, shutil
import numpy as np

# ------------------------------------------------------------------ ayarlar
SONUC_KLASORU = r"C:\CST\openems_sonuc" if os.name == "nt" else os.path.expanduser("~/openems_sonuc")
CALISMA_KLASORU = r"C:\openems_tmp" if os.name == "nt" else os.path.expanduser("~/openems_tmp")
IS_PARCACIGI = 0          # 0 = tum cekirdekler
HUCRE_LAMBDA = int(os.environ.get('HUCRE_LAMBDA', 30))   # dalga boyu basina hucre (20 yakinsamadi, 30 kullan)

# ------------------------------------------------------------------ tasarim (CST ile ayni, mm)
f0 = 5.8e9
fc = 1.2e9                # gauss bant yarisi (4.6 - 7.0 GHz)
# PROFIL: 800 = F4BM265 0.8 mm (ilk tasarim), 762 = JLCPCB ZYF265D 0.762 mm (uretim)
PROFIL = os.environ.get('PROFIL', '762')
if PROFIL == '800':
    h, er, tand = 0.8, 2.65, 0.001
    W, L = 19.1, 15.02
    _w50, _wt, _PEK, _S4P = 2.2, 3.92, "", ""
else:
    h, er, tand = 0.762, 2.65, 0.0019
    W, L = 19.1, 15.04
    _w50, _wt, _PEK, _S4P = 2.10, 3.73, "_k762", "_762"
Lc = float(os.environ.get('LC', 18.0))    # patchler arasi hat (komut isteminde: set LC=18)
p = L + Lc                # patch adimi (sutun boyunca)
w50 = _w50
d1, lt, wt = 10.73, 8.55, _wt   # transformatore uzaklik, trafo boyu, trafo genisligi
Lport = 20.0              # MSL port hatti (CST'deki 5 mm yerine; 50 ohm oldugu icin sadece faz referansini kaydirir)
d = 25.9                  # sutun araligi
BITIS = float(os.environ.get("BITIS", 1e-3))   # enerji bitis kriteri: 1e-3 = -30 dB, 1e-4 = -40 dB
_EK = "" if BITIS >= 1e-3 else f"_e{round(-10*np.log10(BITIS))}"
ETIKET_SUTUN = f"sutun_Lc{Lc:g}_t2_h{HUCRE_LAMBDA}{_PEK}{_EK}"
ETIKET_DIZI = f"dizi_Lc{Lc:g}_t2_h{HUCRE_LAMBDA}{_PEK}{_EK}"
NSUTUN = 8
kenar = 13.0              # alt tas kenar payi
hava = 30.0               # alt tas ile PML arasi hava

def sutun_x(n_sutun):
    return [(c - (n_sutun - 1) / 2) * d for c in range(n_sutun)]

y0b = -3.5 * p - L / 2                 # ilk patch'in alt kenari
y_trafo_ust = y0b - d1
y_trafo_alt = y0b - d1 - lt
y_port = y_trafo_alt - Lport           # port (kart) kenari
y_kart_ust = 3.5 * p + L / 2 + kenar


def model_kur(n_sutun, uyar_port):
    """uyar_port: uyarilacak sutun indeksi (0..n_sutun-1)"""
    from CSXCAD import ContinuousStructure
    from openEMS import openEMS
    from openEMS.physical_constants import C0, EPS0

    FDTD = openEMS(NrTS=300000, EndCriteria=BITIS)   # 1e-3 = -30 dB
    FDTD.SetGaussExcite(f0, fc)
    FDTD.SetBoundaryCond(['PML_8'] * 6)
    CSX = ContinuousStructure()
    FDTD.SetCSX(CSX)
    mesh = CSX.GetGrid()
    mesh.SetDeltaUnit(1e-3)

    fmax = f0 + fc
    res = C0 / fmax / 1e-3 / np.sqrt(er) / HUCRE_LAMBDA   # ~1.35 mm (20 icin)
    res_hava = C0 / fmax / 1e-3 / 20                 # ~2.2 mm

    xs = sutun_x(n_sutun)
    x_min = xs[0] - W / 2 - kenar
    x_max = xs[-1] + W / 2 + kenar

    kappa = 2 * np.pi * f0 * EPS0 * er * tand
    sub = CSX.AddMaterial('F4BM265', epsilon=er, kappa=kappa)
    sub.AddBox([x_min, y_port, 0], [x_max, y_kart_ust, h], priority=0)

    gnd = CSX.AddMetal('gnd')
    gnd.AddBox([x_min, y_port, 0], [x_max, y_kart_ust, 0], priority=10)

    cu = CSX.AddMetal('bakir')
    for xc in xs:
        for k in range(8):
            yc = (k - 3.5) * p
            cu.AddBox([xc - W / 2, yc - L / 2, h], [xc + W / 2, yc + L / 2, h], priority=10)
            if k < 7:
                cu.AddBox([xc - w50 / 2, yc + L / 2, h], [xc + w50 / 2, yc + L / 2 + Lc, h], priority=10)
        cu.AddBox([xc - w50 / 2, y_trafo_ust, h], [xc + w50 / 2, y0b, h], priority=10)
        cu.AddBox([xc - wt / 2, y_trafo_alt, h], [xc + wt / 2, y_trafo_ust, h], priority=10)

    # --- mesh
    mesh.AddLine('x', [x_min - hava, x_max + hava])
    mesh.AddLine('y', [y_port - hava, y_kart_ust + hava])
    mesh.AddLine('z', np.linspace(0, h, 5))
    mesh.AddLine('z', [-20, h + 45])
    for xc in xs:
        mesh.AddLine('x', xc)
    FDTD.AddEdges2Grid(dirs='xy', properties=cu, metal_edge_res=res / 3)
    mesh.AddLine('x', [x_min, x_max])
    mesh.AddLine('y', [y_port, y_port + 2, y_kart_ust])
    mesh.SmoothMeshLines('x', res, 1.4)
    mesh.SmoothMeshLines('y', res, 1.4)
    mesh.SmoothMeshLines('z', res_hava, 1.4)

    # --- portlar (hepsi 50 ohm ile sonlandirilmis, sadece biri uyarilmis)
    portlar = []
    for c, xc in enumerate(xs):
        portlar.append(FDTD.AddMSLPort(c + 1, cu,
                                       [xc - w50 / 2, y_port, h], [xc + w50 / 2, y_trafo_alt, 0],
                                       'y', 'z', excite=1 if c == uyar_port else 0,
                                       FeedShift=2.0, MeasPlaneShift=Lport / 2, Feed_R=50,
                                       priority=5))

    nf2ff = FDTD.CreateNF2FFBox(frequency=F_ORUNTU)
    return FDTD, CSX, portlar, nf2ff


FREKANS = np.linspace(4.8e9, 6.8e9, 401)
F_ORUNTU = [5.70e9, 5.75e9, 5.8e9, 5.85e9, 5.9e9]
THETA = np.arange(-90.0, 90.5, 0.5)
PHI = [0.0, 90.0]


def kos(n_sutun, i, etiket):
    os.makedirs(SONUC_KLASORU, exist_ok=True)
    cikti = os.path.join(SONUC_KLASORU, f"{etiket}_port{i + 1}.npz")
    if os.path.exists(cikti):
        print(f"[atlandi] {cikti} zaten var")
        return
    yol = os.path.join(CALISMA_KLASORU, f"{etiket}_port{i + 1}")
    os.makedirs(yol, exist_ok=True)
    FDTD, CSX, portlar, nf2ff = model_kur(n_sutun, i)
    g = CSX.GetGrid()
    nx, ny, nz = len(g.GetLines('x')), len(g.GetLines('y')), len(g.GetLines('z'))
    print(f"\n=== {etiket}: port {i + 1} uyariliyor | mesh {nx}x{ny}x{nz} = {nx * ny * nz / 1e6:.2f} M hucre ===")
    t0 = time.time()
    FDTD.Run(yol, cleanup=True, numThreads=IS_PARCACIGI, verbose=1)
    print(f"sure: {(time.time() - t0) / 60:.1f} dk")

    uinc, uref = [], []
    for pt in portlar:
        pt.CalcPort(yol, FREKANS, ref_impedance=50)
        uinc.append(pt.uf_inc)
        uref.append(pt.uf_ref)
    uinc, uref = np.array(uinc), np.array(uref)

    r = nf2ff.CalcNF2FF(yol, F_ORUNTU, THETA, PHI, center=[0, 0, h * 1e-3])
    np.savez(cikti, f=FREKANS, uinc=uinc, uref=uref, i=i, n=n_sutun,
             f_or=np.array(F_ORUNTU), theta=THETA, phi=np.array(PHI),
             Eth=np.array(r.E_theta), Eph=np.array(r.E_phi), Prad=np.array(r.Prad))
    s = uref[i] / uinc[i]
    k = np.argmin(abs(FREKANS - f0))
    print(f"kaydedildi: {cikti} | S{i + 1}{i + 1}(5.8 GHz) = {20 * np.log10(abs(s[k])):.1f} dB")
    shutil.rmtree(yol, ignore_errors=True)


# ------------------------------------------------------------------ son islem
def yukle(etiket, n_sutun, simetri):
    """Her kosu icin: S sutunu ve 1 V gelen dalgaya normalize uzak alan."""
    S = np.zeros((len(FREKANS), n_sutun, n_sutun), complex)
    Eth = Eph = None
    for i in range(n_sutun):
        fn = os.path.join(SONUC_KLASORU, f"{etiket}_port{i + 1}.npz")
        ayna = False
        if not os.path.exists(fn):
            if simetri and os.path.exists(os.path.join(SONUC_KLASORU, f"{etiket}_port{n_sutun - i}.npz")):
                fn = os.path.join(SONUC_KLASORU, f"{etiket}_port{n_sutun - i}.npz"); ayna = True
            else:
                raise FileNotFoundError(fn)
        z = np.load(fn)
        inc = z['uinc'][z['i']]
        Si = z['uref'] / inc                     # (port, frekans)
        kf = [np.argmin(abs(z['f'] - fo)) for fo in z['f_or']]
        eth = z['Eth'] / inc[kf][:, None, None]  # (frekans, theta, phi)
        eph = z['Eph'] / inc[kf][:, None, None]
        if ayna:                                 # x -> -x aynasi
            Si = Si[::-1]
            eth = eth[:, ::-1, :].copy(); eph = eph[:, ::-1, :].copy()
            eth[:, :, 0] *= -1                   # phi=0 duzlemi: E_theta isaret degistirir
            eph[:, :, 1] *= -1                   # phi=90 duzlemi: E_phi isaret degistirir
            eth[:, :, 1] = eth[:, ::-1, 1]; eph[:, :, 1] = eph[:, ::-1, 1]  # phi=90'da theta yansimaz
        S[:, :, i] = Si.T
        if Eth is None:
            Eth = np.zeros((n_sutun,) + eth.shape, complex); Eph = np.zeros_like(Eth)
        Eth[i], Eph[i] = eth, eph
    return S, Eth, Eph, z


def kazanc(w, Eth, Eph, kf):
    """w: sutunlara gelen dalga genlikleri. Realized gain (dBi)."""
    eta0 = 376.73
    et = np.tensordot(w, Eth[:, kf], axes=1)
    ep = np.tensordot(w, Eph[:, kf], axes=1)
    Pinc = np.sum(abs(w) ** 2) / (2 * 50)
    U = (abs(et) ** 2 + abs(ep) ** 2) / (2 * eta0)   # r = 1 m
    return 10 * np.log10(4 * np.pi * U / Pinc + 1e-30)


def butler_agirliklari():
    """butler_hesap.py ile ayni hesap (hibrit.s4p + crossover2h.s4p, C:\\CST)."""
    kl = os.path.dirname(SONUC_KLASORU)
    bh = os.path.join(kl, 'butler_hesap.py')
    if not os.path.exists(bh) or not os.path.exists(os.path.join(kl, f'hibrit{_S4P}.s4p')):
        print(f"[uyari] hibrit{_S4P}.s4p bulunamadi, Butler agirliklari hesaplanmadi")
        return None
    ns = {}
    src = open(bh, encoding='utf-8').read()
    src = src.split('# ---------------------------------------------------------------- Sonuclar')[0]
    src = src.replace("os.path.dirname(os.path.abspath(__file__))", repr(kl)).replace("sys.argv", "['x']")
    src = src.replace("'hibrit.s4p'", f"'hibrit{_S4P}.s4p'").replace("'crossover2h.s4p'", f"'crossover{_S4P or '2h'}.s4p'")
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        exec(src, ns)
    return ns['M']


def huzme_bilgi(G, theta):
    i = np.argmax(G); tepe = theta[i]
    yer = [G[k] for k in range(1, len(G) - 1) if G[k] > G[k - 1] and G[k] > G[k + 1]]
    yl = sorted(yer)[-2] - G[i] if len(yer) > 1 else np.nan
    ust = G >= G[i] - 3
    j = i
    while j > 0 and ust[j - 1]: j -= 1
    k = i
    while k < len(G) - 1 and ust[k + 1]: k += 1
    return tepe, G[i], theta[k] - theta[j], yl


def sonuc():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    etiket = ETIKET_DIZI
    S, Eth, Eph, z = yukle(etiket, NSUTUN, simetri=True)
    theta = z['theta']; kf = list(z['f_or']).index(5.8e9)
    k0 = np.argmin(abs(FREKANS - f0))
    dB = lambda x: 20 * np.log10(abs(x) + 1e-30)

    # S parametreleri
    fig, ax = plt.subplots(figsize=(9, 5))
    for i in range(4):
        ax.plot(FREKANS / 1e9, dB(S[:, i, i]), label=f'S{i+1},{i+1}')
    ax.plot(FREKANS / 1e9, dB(S[:, 4, 3]), 'k--', label='S5,4 (komsu kuplaj)')
    ax.plot(FREKANS / 1e9, dB(S[:, 5, 3]), 'k:', label='S6,4 (2. komsu)')
    ax.set_xlabel('Frekans (GHz)'); ax.set_ylabel('dB'); ax.set_ylim(-50, 0); ax.grid(alpha=.3); ax.legend()
    ax.set_title('8x8 dizi - sutun yansimalari ve kuplaj (openEMS)')
    fig.savefig(os.path.join(SONUC_KLASORU, 'S_parametreleri.png'), dpi=130, bbox_inches='tight')

    print("\n5.8 GHz S matrisi (dB), satir = cikan port, sutun = uyarilan port")
    print(np.round(dB(S[k0]), 1))

    # hüzmeler
    senaryolar = []
    for m, dphi in enumerate([-22.5, -67.5, -112.5, -157.5, 157.5, 112.5, 67.5, 22.5]):
        senaryolar.append((f'ideal {dphi:+.1f}', np.exp(1j * np.deg2rad(dphi) * np.arange(NSUTUN))))
    M = butler_agirliklari()
    if M is not None:
        for g in range(8):
            senaryolar.append((f'Butler giris {g+1}', M[:, g]))

    satirlar = []
    fig, axs = plt.subplots(1, 2 if M is not None else 1, figsize=(14, 5), squeeze=False)
    for n, (ad, w) in enumerate(senaryolar):
        G = kazanc(w, Eth, Eph, kf)[:, 0]
        tepe, gmax, gen, yl = huzme_bilgi(G, theta)
        Gact = (S[k0] @ w) / w
        akt = dB(Gact)
        satirlar.append((ad, gmax, tepe, gen, yl, akt.max()))
        ax = axs[0][0 if ad.startswith('ideal') else 1]
        ax.plot(theta, G, label=ad)
    for ax, t in zip(axs[0], ['Ideal fazlar', 'Butler matrisi (CST hibrit + crossover)']):
        ax.set_ylim(-10, 26); ax.set_xlim(-90, 90); ax.grid(alpha=.3); ax.set_xlabel('theta (derece), phi = 0')
        ax.set_ylabel('Realized gain (dBi)'); ax.set_title(t); ax.legend(fontsize=7, ncol=2)
    fig.savefig(os.path.join(SONUC_KLASORU, 'huzmeler_5p8GHz.png'), dpi=130, bbox_inches='tight')

    print("\n5.8 GHz | senaryo | kazanc (dBi) | yon | 3dB genislik | yan lob | en kotu aktif S11")
    with open(os.path.join(SONUC_KLASORU, 'sonuc_tablosu.txt'), 'w', encoding='utf-8') as fo:
        for s in satirlar:
            line = f"{s[0]:18s} | {s[1]:5.1f} dBi | {s[2]:6.1f} | {s[3]:5.1f} | {s[4]:6.1f} dB | {s[5]:6.1f} dB"
            print(line); fo.write(line + "\n")
    print(f"\nGrafikler ve tablo: {SONUC_KLASORU}")


def sutun_sonuc():
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    z = np.load(os.path.join(SONUC_KLASORU, ETIKET_SUTUN + '_port1.npz'))
    s11 = z['uref'][0] / z['uinc'][0]
    kf = list(z['f_or']).index(5.8e9)
    inc = z['uinc'][0][[np.argmin(abs(z['f'] - fo)) for fo in z['f_or']]]
    Eth = z['Eth'][None] / inc[None, :, None, None]; Eph = z['Eph'][None] / inc[None, :, None, None]
    G = kazanc(np.array([1.0]), Eth, Eph, kf)
    k = np.argmin(abs(z['f'] - f0))
    bant = (z['f'] > 5.4e9) & (z['f'] < 6.2e9)
    kmin = np.argmin(np.where(bant, abs(s11), 9))
    t90 = huzme_bilgi(G[:, 1], z['theta'])
    print(f"S11 @5.8 GHz = {20*np.log10(abs(s11[k])):.1f} dB | minimum {20*np.log10(abs(s11[kmin])):.1f} dB @ {z['f'][kmin]/1e9:.3f} GHz")
    print(f"phi=90 (sutun duzlemi): kazanc {t90[1]:.1f} dBi, yon {t90[0]:.1f}, genislik {t90[2]:.1f}, yan lob {t90[3]:.1f} dB")
    print("CST: S11 -28 dB @ 5.80 GHz, 15.4 dBi, yon 3.0, genislik 9.8, yan lob -9.7 dB")
    print(f"--- Lc = {Lc} mm, hucre/lambda = {HUCRE_LAMBDA} ---")
    print(" frekans |  S11  | huzme yonu | yan lob")
    for j, fo in enumerate(z['f_or']):
        Gj = kazanc(np.array([1.0]), Eth, Eph, j)
        tj = huzme_bilgi(Gj[:, 1], z['theta'])
        sj = 20 * np.log10(abs(s11[np.argmin(abs(z['f'] - fo))]))
        print(f"  {fo/1e9:.2f}  | {sj:5.1f} | {tj[0]:6.1f}     | {tj[3]:5.1f} dB")
    fig, ax = plt.subplots()
    ax.plot(z['f'] / 1e9, 20 * np.log10(abs(s11))); ax.grid(alpha=.3); ax.set_xlabel('GHz'); ax.set_ylabel('S11 (dB)')
    fig.savefig(os.path.join(SONUC_KLASORU, 'sutun_S11.png'), dpi=130)


if __name__ == '__main__':
    komut = sys.argv[1] if len(sys.argv) > 1 else ''
    if komut == 'goster':
        FDTD, CSX, _, _ = model_kur(NSUTUN, 0)
        os.makedirs(CALISMA_KLASORU, exist_ok=True)
        fn = os.path.join(CALISMA_KLASORU, 'dizi.xml'); CSX.Write2XML(fn)
        from CSXCAD import AppCSXCAD_BIN
        os.system(AppCSXCAD_BIN + ' "{}"'.format(fn))
    elif komut == 'sutun':
        kos(1, 0, ETIKET_SUTUN); sutun_sonuc()
    elif komut == 'calistir':
        tam = len(sys.argv) > 2 and sys.argv[2] == 'tam'
        for i in (range(NSUTUN) if tam else range(NSUTUN // 2)):
            kos(NSUTUN, i, ETIKET_DIZI)
        sonuc()
    elif komut == 'sonuc':
        sonuc()
    else:
        print(__doc__)
