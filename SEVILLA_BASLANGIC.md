# Sevilla — ilk İspanya şehri: başlangıç notu (Windows oturumu için)

Hazırlayan: bulut oturumu, 24.10.2026. Ayrıntılı geçmiş: `OTURUM_OZETI_20261024_BULUT.md`. Adımların aslı: `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md` ("city-pack ile birlikte kullanım").

## 0. Önce
- `git pull` (main, en az `7cf50d5`).
- `ROOT\uretim\sevilla\manifest.json` olmamalı (yoksa skill devam/yeni sürüm sorar).

## 1. Oturuma yazılacak mesaj
Skill ülke paketini yalnız kullanıcı verirse kullanır. Yalnız "Sevilla" yazma; şunu yaz:

> Sevilla paketi. Ülke paketi var: `ROOT\ulke\ES` (v9) + bölge `ROOT\ulke\ES\bolge\andalucia` (v2). `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md`'deki "city-pack ile birlikte kullanım" adımlarını uygula. Ülke, bölge ve şehir fazının süre ve token'ını ayrı ölç.

## 2. Akış (özet)
1. Intake her zamanki gibi (klasörler, şablon, `ortam.ps1`). `manifest.country_pack` = `$WORK\_is\ulke_paketi`.
2. Yazarlardan ÖNCE:
```powershell
. $ROOT\uretim\sevilla\_is\ortam.ps1
$DU = "$ROOT\corteqs-skills\deneme_ulke_paketi"
& $PY $DU\pack_merge.py --pack $ROOT\ulke\ES --pack $ROOT\ulke\ES\bolge\andalucia --out $WORK\_is\ulke_paketi
& $PY $DU\country_apply.py apply $WORK\_is --pack $WORK\_is\ulke_paketi --city-id sevilla --city-name Sevilla --order-start 9000
```
   Beklenen: `copied 105`, `stale []` (5.11.2026'dan önce). `stale` doluysa o kartlar şehir yazarına kalır.
3. Şehir yazarlarına ek talimat: "`data\parcalar\Yanıtlar.<konu>.jsonl`'daki ülke/bölge satırlarını SİLME ve değiştirme; kendi kartlarını SONA ekle; aynı konuyu tekrar yazma." Ülke kartları `featured` 'Hayır' gelir; öne çıkan kartları (konu başına ≤2) şehir seçer.
4. Yazarlardan sonra:
```powershell
& $PY $DU\country_apply.py audit-scope $WORK\_is --pack $WORK\_is\ulke_paketi --out $WORK\_is\ulke_denetim_kapsami.json
```
   `"kart şehirde yok"` çıkarsa bir yazar ülke kartını silmiştir → geri al. `skip` kartları claim denetiminden çıkar.
5. Sonrası skill'in normal akışı (mekân, mahalle, foto, merge_package, teslim).

## 3. Bilinenler
- Bulut ortamında aynı adımlar sahte Sevilla klasöründe denendi: `merge_package` 105 kart / 2045 claim / 0 bulgu.
- Ulaşım: konsorsiyum ücretleri bölge paketinde YOK (bilerek): Sevilla metropol konsorsiyumunun kartı ve tarifesi şehir kartı olarak yazılmalı.
- Ülke paketi şehir kartlarının ~105'ini karşılar; mekân (120), mahalle (16), foto ve şehre özgü kartlar her şehirde yine yapılır.
- Açık konular: `ulke\ES\acik_konular.md`, `ulke\ES\bolge\andalucia\acik_konular.md`.
- Tarihli kartlar: 6 kira kartı 5.11.2026, 8 kart 31.12.2026'da biter.
- Ölçüm hedefi: Sevilla toplamı Bakersfield'dan (~7 sa) düşük; Málaga/Marbella şehir fazı Sevilla'nınkinin %60'ını geçmesin.
