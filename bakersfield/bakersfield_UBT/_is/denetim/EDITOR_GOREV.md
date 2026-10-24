# Editör görev dosyası (Bakersfield · CITY-901 · 23.10.2026)

Önce `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\editor.md` oku (mekân/mahalle/sözlük/sayfa/rota parçasında ayrıca `...\agents\yer-yazari.md`). Kayıtları sen yazmadın, denetimi de sen yapmadın.

## Gerçek değerler
| Yer tutucu | Değer |
|---|---|
| `<city_id>` | `bakersfield` |
| `<WORK>` | `C:\temp_private\corteqs\0000_newera\uretim\bakersfield` |
| `<TK>` | `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts` |
| `<PY>` | `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe` |
| `<TMP>` | görev mesajında |
| `<gorev>` | görev mesajındaki parça adı |
| `<konu>` | yanıt parçasında `<gorev>`; diğerlerinde görev mesajında |
| `<rol>` | `editor` (`add_sources --subdir snap_<gorev>-editor<sira>`, her koşu yeni sıra) |
| `<tarih>` | `2026-10-23` |
| `<bbox>` | `35.1740,35.4680,-119.2853,-118.7527` |

Hitap: okura **"sen"** (`<WORK>\_is\yazar\hitap.txt` = `sen`); "siz" yok; bir kayıtta biçim karışmaz; bilgi cümlesi kişisiz olabilir. Para birimi USD. Kurallar federal / California / Kern / Bakersfield düzeyinde ayrılır.

## Girdiler
- Düzenleyeceğin dosyalar (yalnız bunlar): görev mesajındaki `<WORK>\_is\data\parcalar\<Sekme>.<gorev>.jsonl` dosyaları ve `<WORK>\_is\claims\<gorev>.jsonl`.
- Denetim bulguları: `<WORK>\_is\denetim\<gorev>_iddia.jsonl` (`claim_id, entry_id, iddia, …, sonuç, ağırlık, alıntı, doğrusu`) ve kart kararları `<WORK>\_is\denetim\<gorev>_karar.jsonl`.
- Kaynak metinleri: `<WORK>\_is\kaynak_dizini.jsonl` → `text_file`.
- Erişim engelli alan adları: `<WORK>\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu" (engelli siteyi deneme; bot engeli aşılmaz).

## Turlar (görev mesajı hangisi olduğunu ve açık görev numaralarını yazar)
- **tamamlama turu**: `editor.md` görev 1–7 açık. `new_sources`: bu şehirde hedefli kaynak keşfi yapılmadı (eksiklerin çoğu bot engelli resmî sitelerden: uscis.gov, bakersfieldcity.us, kerncountylibrary.org …). Görev mesajındaki `gaps` listesindeki bir eksik için erişilebilir resmî kaynak bulursan `add_sources` ile ekleyip bilgiyi var olan karta ekle ya da yeni kart yaz (görev 4); bulamazsan `open`'a yaz. Kart aralığı görev mesajında; eklediğin kartlar `order` aralığında, slug ve başlık pakette benzersiz, en az 1 Bağlantılar satırı, her yeni sayı/kural defterde.
- **denetim turu**: görev 1, 2, 6, 7 açık; kural gözden geçirmesi kapalı; kart eklenmez/silinmez.
- **doğrulama turu**: görev 8 (+ uyguladığın düzeltmede 2, 6, 7).

## Ek iş listesi
Görev mesajı varsa şunları da verir: metin kalitesi bulguları (hitap karışması vb.: kaydı anlamı ve sayıları değişmeden tek biçimde "sen"le yeniden yaz), iddia kontrolünde kalan biçim farkları, başka parçalarla örtüşme notları.

## Değişiklik kaydı
`<WORK>\_is\denetim\<gorev>_degisiklik.jsonl` (`editor.md` biçimi; dosya varsa sonuna ekle). "doğru" olmayan her bulgu için en az bir satır (uygulandı ya da gerekçeli reddedildi).

## Bitirmeden
Ortak kurallar §8: `merge_package` `--data-out <TMP>\birlesik --out <TMP>\birlestir_rapor.json --bbox=35.1740,35.4680,-119.2853,-118.7527`; kendi satırlarının okunduğunu doğrula; kendi parçana ait `issues`/`quote_miss_list` 0. Ayrıca hitap kontrolü:
```powershell
& <PY> <TK>\merge_package.py <WORK>\_is --city-id bakersfield --bbox=35.1740,35.4680,-119.2853,-118.7527 --data-out <TMP>\birlesik --out <TMP>\birlestir_rapor.json
```
(text_quality ana döngüde çalışır; sen kayıtlarında "siz" biçimi bırakma.)

## Dönüş
`editor.md`'deki tek satır JSON.
