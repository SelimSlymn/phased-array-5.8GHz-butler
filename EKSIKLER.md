# Eksikler – 5.8 GHz Butler dizisi

## Tamamlananlar

- [x] Kayıp analiz kodları yeniden yazıldı: `scriptler/ortak.py`, `aktif_s11.py`, `butler_huzmeler.py`, `sutun_desen.py`. Final CST verilerinden README'deki değerleri yeniden üretiyorlar (kazanç 22.8 … 18.6 dBi, aktif S11 −6.2 … −14.1 dB).
- [x] `s-parametreleri/dizi_cst_762.s8p` final koşu (başlıkta L 15.74, Lc 15.01, wt 4.4, d1 17.8). Zip'siz hali eklendi; `dizi_cst_762.s8p.zip` silinebilir.
- [x] Final CST sonuç grafikleri ve hüzme tablosu (`sonuclar/cst/`).
- [x] README'deki özel claude.ai bağlantıları kaldırıldı. İngilizce `README.md` eklendi, Türkçe hali `README.tr.md`.
- [x] `LICENSE` (MIT) ve repoya özel `.gitignore`.
- [x] `butler_hesap.py` final dosyaları (`hibrit_762.s4p`, `crossover_762.s4p`) okuyacak şekilde düzeltildi; `butler_agirliklar_762.txt`'yi birebir üretiyor. İki s4p'nin zip'siz hali eklendi.

## Senin yapman gerekenler

- [ ] `cst/project2.cst`, `cst/deneme.cst` ve `s-parametreleri/dizi_cst_762.s8p.zip` dosyalarını sil.
- [ ] İstersen sunumları ve teknik özeti PDF olarak indirip `sunum/` ve `dokumanlar/` klasörlerine koy (zorunlu değil; görseller ve teknik_ozet.md zaten var).

## İsteğe bağlı

- [ ] Butler'ı CST'de tek devre olarak kurmak ve Butler + SP8T kaybıyla sistem kazancını hesaplamak.
- [ ] SP8T için somut parça seçimi.
- [ ] Devam projesi: 2.4 GHz hava boşluklu 4×4 dizi (ayrı repo).
