# -*- coding: utf-8 -*-
"""
8x8 Butler matrisi hesabi (16 crossover'li duzlemsel yerlesim)
Girdi : s-parametreleri/hibrit_762.s4p ve s-parametreleri/crossover_762.s4p
        crossover dosyasi yoksa, crossover iki hibritin arka arkaya baglanmasiyla hesaplanir.
Cikti : her giris icin sutun genlik/faz tablosu (s-parametreleri/butler_agirliklar_762.txt
        ile ayni degerler), hüzme acisi ve yan lob seviyesi;
        (matplotlib varsa) sonuclar/cst/butler_dizi_carpani.png

Calistirma (proje klasorunden):
             python scriptler/butler_hesap.py          (5.8 GHz)
             python scriptler/butler_hesap.py 5.75     (baska frekans)
Gerekenler:  Python 3 + numpy   (grafik icin matplotlib, istege bagli)
"""
import sys, os
import numpy as np

F0 = float(sys.argv[1]) if len(sys.argv) > 1 else 5.8
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KLASOR = os.path.join(ROOT, 's-parametreleri')
CIKTI = os.path.join(ROOT, 'sonuclar', 'cst')

# ---------------------------------------------------------------- Touchstone
def oku_s4p(dosya):
    f, S, sayilar = [], [], []
    birim = 1.0
    for satir in open(dosya):
        if satir.strip().startswith('#'):
            u = satir.upper()
            birim = 1.0 if 'GHZ' in u else 1e-3 if 'MHZ' in u else 1e-9 if 'HZ' in u else 1.0
            continue
        satir = satir.split('!')[0].strip()
        if satir:
            sayilar += [float(x) for x in satir.split()]
    for i in range(0, len(sayilar), 33):
        r = sayilar[i:i + 33]
        f.append(r[0] * birim)
        v = np.array(r[1:]).reshape(16, 2)
        S.append((v[:, 0] * np.exp(1j * np.deg2rad(v[:, 1]))).reshape(4, 4))
    return np.array(f), np.array(S)

def iki_hibritten_crossover(SA, SB, hat_derece=90.0):
    """A'nin 3,4 portlari -> B'nin 1,2 portlarina ideal 50 ohm hatla bagli."""
    S = np.zeros((8, 8), complex); S[:4, :4] = SA; S[4:, 4:] = SB
    t = np.exp(-1j * np.deg2rad(hat_derece))
    dis, ic = [0, 1, 6, 7], [2, 3, 4, 5]
    C = np.zeros((4, 4), complex); C[0, 2] = C[2, 0] = t; C[1, 3] = C[3, 1] = t
    See = S[np.ix_(dis, dis)]; Sei = S[np.ix_(dis, ic)]
    Sie = S[np.ix_(ic, dis)]; Sii = S[np.ix_(ic, ic)]
    return See + Sei @ C @ np.linalg.solve(np.eye(4) - Sii @ C, Sie)

fh, Sh = oku_s4p(os.path.join(KLASOR, 'hibrit_762.s4p'))
k = np.argmin(abs(fh - F0)); H = Sh[k]
xdosya = os.path.join(KLASOR, 'crossover_762.s4p')
if os.path.exists(xdosya):
    fx, Sx = oku_s4p(xdosya); X = Sx[np.argmin(abs(fx - F0))]; kaynak = 'crossover_762.s4p (CST)'
else:
    X = iki_hibritten_crossover(H, H, 90 * F0 / 5.8); kaynak = 'iki hibritten hesaplandi'

db = lambda x: 20 * np.log10(abs(x))
print("Frekans: %.3f GHz" % fh[k])
print("Hibrit : S31 %.2f dB, S41 %.2f dB, faz farki %.1f derece" %
      (db(H[2, 0]), db(H[3, 0]), (np.angle(H[2, 0] / H[3, 0], deg=True))))
print("Crossover (%s): capraz %.2f dB, duz sizinti S31 %.1f dB, S11 %.1f dB" %
      (kaynak, db(X[3, 0]), db(X[2, 0]), db(X[0, 0])))

# ---------------------------------------------------------------- Yerlesim plani
S1 = [(0, 4), (1, 5), (2, 6), (3, 7)]
S2 = [(0, 2), (1, 3), (4, 6), (5, 7)]
S3 = [(0, 1), (2, 3), (4, 5), (6, 7)]
GIRIS_SIRASI = [0, 4, 2, 6, 1, 5, 3, 7]          # soldan saga fiziksel giris sirasi
PLAN = [  # (kat adi, hibrit ciftleri, o katmandan once yapilacak crossover katmanlari)
    ("kat1", S1, []),
    ("kat2", S2, [[1, 3, 5], [2, 4], [3]]),        # pozisyon indeksleri (0'dan) : p <-> p+1
    ("kat3", S3, [[1, 5]]),
    ("cikis", None, [[1, 3, 5], [2, 4], [1, 3, 5]]),
]
GEC12 = np.array([90, 90, 0, 0, 0, 45, 0, 45.])     # hat etiketine gore gecikme (derece)
GEC23 = np.array([90, 0, 0, 0, 90, 0, 0, 0.])
GEC_SUTUN = np.array([0, 22.5, 45, 67.5, 0, 22.5, 45, 67.5])

def butler(H, X, f=F0):
    T = H[2:, :2]; Xc = X[2:, :2]
    telafi = np.exp(1j * np.angle(X[3, 0]))          # crossover'dan gecmeyen hatlara esit faz
    M = np.zeros((8, 8), complex)
    for giris in range(8):
        v = np.zeros(8, complex); lab = list(GIRIS_SIRASI)
        v[lab.index(giris)] = 1
        for ad, ciftler, katmanlar in PLAN:
            for sw in katmanlar:
                nv = v * telafi; nl = lab[:]
                for p in sw:
                    a, b = v[p], v[p + 1]
                    nv[p] = Xc[0, 0] * a + Xc[0, 1] * b
                    nv[p + 1] = Xc[1, 0] * a + Xc[1, 1] * b
                    nl[p], nl[p + 1] = lab[p + 1], lab[p]
                v, lab = nv, nl
            if ciftler is None:
                break
            idx = {l: i for i, l in enumerate(lab)}
            for p, q in ciftler:
                a, b = idx[p], idx[q]; x, y = v[a], v[b]
                v[a] = T[0, 0] * x + T[0, 1] * y; v[b] = T[1, 0] * x + T[1, 1] * y
            g = {"kat1": GEC12, "kat2": GEC23, "kat3": np.zeros(8)}[ad]
            v = v * np.exp(-1j * np.deg2rad(np.array([g[l] for l in lab]) * f / 5.8))
        M[:, giris] = v * np.exp(-1j * np.deg2rad(GEC_SUTUN * f / 5.8))
    return M

M = butler(H, X)

# ---------------------------------------------------------------- Sonuclar
th = np.linspace(-90, 90, 3601); n = np.arange(8)
def huzme(w):
    af = np.abs(np.exp(1j * np.pi * np.outer(np.sin(np.deg2rad(th)), n)) @ w)
    af = 20 * np.log10(af / af.max() + 1e-12)
    tepe = th[np.argmax(af)]
    yerel = [af[i] for i in range(1, len(af) - 1) if af[i] > af[i - 1] and af[i] > af[i + 1]]
    yl = sorted(yerel)[-2] if len(yerel) > 1 else -99
    return tepe, yl, af

hedef = {0: 22.5, 1: 67.5, 2: 112.5, 3: 157.5, 4: -157.5, 5: -112.5, 6: -67.5, 7: -22.5}
print("\nGiris | genlik araligi (dB) | ort. faz adimi | faz sapmasi | huzme | yan lob")
egriler = []
for i in range(8):
    w = M[:, i]; a = db(w)
    d = np.diff(np.angle(w, deg=True)); d = (d + 180) % 360 - 180
    tepe, yl, af = huzme(w); egriler.append(af)
    print("  %d   | %6.2f .. %6.2f     | %7.1f        | +/-%5.1f     | %6.1f | %5.1f dB"
          % (i + 1, a.min(), a.max(), d.mean(), np.abs(d - d.mean()).max(), tepe, yl))

print("\nCST Farfield Array 'Userdefined' icin sutun genlik/faz degerleri")
print("(X = (sutun-1)*25.9 mm, Y = 0, Z = 0; genlik en buyuge gore normalize)")
for i in range(8):
    w = M[:, i]; a = abs(w) / abs(w).max(); p = np.angle(w, deg=True); p = p - p[0]
    p = (p + 180) % 360 - 180
    print("Giris %d:" % (i + 1))
    for c in range(8):
        print("   sutun %d  X=%6.1f  genlik %.3f  faz %7.1f" % (c + 1, c * 25.9, a[c], p[c]))

try:
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    plt.figure(figsize=(9, 5))
    for i, af in enumerate(egriler):
        plt.plot(th, af, label='giris %d' % (i + 1))
    plt.ylim(-40, 2); plt.xlim(-90, 90); plt.grid(alpha=.3)
    plt.xlabel('aci (derece)'); plt.ylabel('normalize dizi carpani (dB)')
    plt.title('8x8 Butler, 16 crossover, %.2f GHz' % fh[k]); plt.legend(ncol=4, fontsize=8)
    os.makedirs(CIKTI, exist_ok=True); cikti = os.path.join(CIKTI, 'butler_dizi_carpani.png'); plt.savefig(cikti, dpi=130, bbox_inches='tight')
    print("\nGrafik kaydedildi:", cikti)
except ImportError:
    print("\n(matplotlib yok, grafik cizilmedi)")
