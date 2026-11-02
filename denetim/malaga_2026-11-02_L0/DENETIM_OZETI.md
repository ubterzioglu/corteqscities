Editoryal hazır olma: %6 (doğrulanan alt sınır, kısmi denetim) | Denetim kapsamı: L0, yerel paket denetimi, kart 0/244, fotoğraf 0/334, kritik iddia 0/2559; script kapsamı dosya 1812/1812, URL 443/443 | Karar: DÜZELTME GEREKLİ
Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: 2 (ISS-001, ISS-002) | Açık P1: 3 (ISS-003, ISS-004, ISS-005) | P2 öneri: 3

# Málaga (CITY-075) — L0 denetimi, 02.11.2026

- Excel: `CITY-075_malaga_v001.xlsx`, şema 1.0, SHA-256 `cd6a6392fd97b09b197f8edc432515b536b1652d43b5533a5ab98d995212baac` (dış denetimle aynı dosya).
- K04 sabitleme: başta ve sonda 1.812 dosya, fark 0. Teslim özeti ölçümle birebir (K83 sayı farkı yok).
- Dış denetim (Atınç, aynı SHA): %70, YAYINA HAZIR DEĞİL. Bu L0 onun bulgularını script ile sınadı; L1 çalıştırılmadı.
- Kanıt kapsamı alt sınırı (dış denetim modeli): %91,62; eksik ölçütler A1–A5, B1, B5, C4 (dış denetim bu modeli değil, editoryal düzeyi kullandı).

## Berlin matrisi (minimum / hedef / fiilî)

Yanıt 212/240/244 · Mekân 92/120/120 · Mahalle 12/16/16 · Konu 12/12/12 · Rota 9/12/12 · Sözlük 48/60/62 · Tekil mekân fotoğrafı 187/250/334 · Kapak 6/8/8. Hedef eksiği yok.

## Öncelikli bulgular

| ID | Öncelik | Kontrol | Yer | Bulgu | Kanıt |
|---|---|---|---|---|---|
| ISS-001 | P0 | K35 | Yanıtlar!39 | Turistik daire kartı 43 mahalle kuralını güncel anlatıyor; 23.08.2025'ten beri bütün şehirde yeni turistik daire en çok 3 yıl askıda | malaga.eu duyurusu (ANUDocumentDisplayer/178062), BOP 22.08.2025; dış denetim R01 |
| ISS-002 | P0 | K26 | Yanıtlar!129 | Aile birleşimi kartında çocuklu aile gelir istisnası (IMV %110 + çocuk başına %10) ve izin sonrası adımlar yok | İspanya ülke paketi bu hatayı 26.10'da düzeltti; şehre gelmedi (`_analiz\paket-duzeltme.json`); dış denetim R02 |
| ISS-003 | P1 | K118 | Yanıtlar!128–131, 133, 197, 198 | Ülke paketinin 26.10 düzeltmeleri 7 kartta, 60 alanda yok (ISS-002 dahil). Şehir paketin 25.10 kopyasıyla kurulmuş | `betikler\paket_duzeltme.py` |
| ISS-004 | P1 | K62/K95 | Şehir!8 | `hero_photo_id` boş. Taslak doğrulama 0 hata, hazır kip: 1.825 insan alanı + 1 engel | `validation-ready.json` |
| ISS-005 | P1 | K83 | Teslimler, Teslimat!8 | Özet "TEKNİK KONTROL GEÇTİ / 0 engelleyici"; "Drive'a yüklenmedi"; Hazırlayan Atınç | TESLIM_OZETI.txt; dış denetim MAL-007 |
| ISS-006 | P2 | K74 | Kanıtlar | `rights_basis` her karede aynı genel cümle; kareye özgü ek hak `foto-inceleme-v7.jsonl`'de kalmış | dış denetim MAL-004, D4 |
| ISS-007 | P2 | K80 | FotoğrafKaynakları | 325/342 kare Commons küçültmesi; `derivation` "özgün dosya korundu" diyor | photo-provenance-v7.json; MAL-005 |
| ISS-008 | P2 | K52 | Kaynaklar/Bağlantılar | 9 adres erişim teyidi açık (bozuk 0) | url-checks.json |

Dış denetimin MAL-006'sı (15 CSV satırı kaymış) **bulgu değil**: Python'un standart okuyucusu iki CSV'de 0 bozuk satır veriyor; kayma yalnız ters eğik çizgiyi kaçış sayan okuyucuda çıkıyor (alıntıda çift tırnak). Yeni araçla CSV'lerin yanına JSONL ikizi yazılıyor.

## Fotoğraf (L0)
Ters eğik çizgili yol 0; kanıtsız kare 0; aynı SHA: 8 kapak↔mekân (zararsız); dHash karar isteyen çift 0. Ön eleme: 334 keep, 8 flag (iç mekân/eser 4, GPS 2, yer uyuşmazlığı 1, ad 1) → L1 girdisi. Paftalar `temas-sayfalari\` (bakılmadı).

## Düzeltme sırası
1. city-pack düzeltme turu: ISS-003 (ülke paketini yeniden uygula, şehir değişiklikleriyle birleştir) → ISS-002 kendiliğinden kapanır; ISS-001 kuralı 21 ile (askı kararının kaynak kopyası).
2. ISS-004 `hero_photo_id`; ISS-006/007 için foto adım 6–7 yeni `photo_rows` ile.
3. Teslim zinciri yeni araçlarla (`--ready-scan`, yeni `iddia_defteri` ve `render_summary`) → ISS-005.
4. Yeni oturumda L0, ardından L1.

## Çalıştırılmayan kontroller
L ve V kontrollerinin hepsi (iddia ajanları, foto paftaları, açık-mı örneklemi); önizleme (K92–94, K103, K111, K112) ve Drive (K01, K03, K109, K110) ayrı aşama.
