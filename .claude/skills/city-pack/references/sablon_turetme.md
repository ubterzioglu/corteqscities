# Şablon türetme (make_template)

**Ne zaman:** Atınç'ın şehir şablonu (`ROOT\ekler\<city_id>\CITY-NNN_<city_id>_v001.xlsx` ya da `ROOT\ekler\CITY-NNN_<city_id>_v001.xlsx`; ör. Aberdeen `ekler\`, Eindhoven `ekler\eindhoven\` içinde) varsa **onu kullan**. Yoksa (Tilburg, Dortmund …) şablonu Berlin örneğinden türet. Atınç'ın şablonu sonradan gelirse ona geç; ikisi eşdeğerdir (aşağıda "Güvence").

## Komut (Tilburg; katalog numarası bilinmiyor → 901)

```powershell
. ROOT\uretim\tilburg\_is\ortam.ps1
& $PY $TK\make_template.py --base $ROOT\ekler\CITY-000_berlin_ornek_v001.xlsx `
  --out $WORK\_is\sablon_kaynak\CITY-901_tilburg_v001.xlsx --report $WORK\_is\sablon_kaynak\make_template.json `
  --city-id tilburg --city-name Tilburg --country Hollanda --country-code NL --region EU --city-number 901 --tools $TOOLS
```

- **Çıktı adı kuralı:** `CITY-<NNN>_<city_id>_v001.xlsx`. `<NNN>` = `--city-number` üç haneye tamamlanır (901 → `901`, 39 → `039`), `<city_id>` = `--city-id`; örnekte `CITY-901_tilburg_v001.xlsx`. Intake `CITY-NNN`'i ve teslim adını (`EXCEL`) bu addan okur. Bu dosya SKILL.md intake'teki şablonun aslıdır (`manifest.paths.template_xlsx`); `_is\sablon.xlsx` ondan kopyalanır. Araç uymayan adı reddetmez: dosyayı yazar, çıkış 0 verir, ama özetteki `open_items`'a "Çıktı adı CITY-901_tilburg_v001.xlsx değil" düşer. Bu uyarıda yanlış adlı dosya `sablon_kaynak\`'tan silinir ve komut doğru adla yeniden çalıştırılır. Dosya kalırsa intake'i yanıltır: intake yerel deneme numarasını bu klasördeki adlardan seçer, şablonun aslını da buradan alır.
- `--updated-on` verilmezse bugün yazılır (gelecek tarih reddedilir). `--editor` varsayılanı `Claude Code city-pack`.
- Yollar her şeyden önce denetlenir:
  - Örneğin klasörü ve `--tools` klasörü salt okunur. `--out` ve `--report` bunların içinde ya da altında olamaz.
  - `--out` `.xlsx`, `--report` `.json` olmalı. İkisi de `--base` olamaz, `--report` `--out` olamaz, ikisi de klasör olamaz.
  - Var olan çıktı `--overwrite` olmadan korunur.
  - Yol hatasında rapor da yazılmaz; hata yalnız ekrandaki tek satır JSON'dadır.
- Çıkış: `0` şablon yazıldı · `1` öz denetim bulgusu, dosya yazılmadı (rapordaki `self_check`) · `2` komut, yol ya da örnek hatası. Okunamayan/bozuk örnek de `2` verir; hata dökümü basılmaz, ekranda tek satır JSON çıkar.

## Kod

Araç üç dosyadır. Komutta yalnız ilki çağrılır; öteki ikisi onun yardımcısıdır ve aynı klasörde (`$TK`) durur. Kod 23 Ekim'de üçe bölündü; komut, bayraklar, çıktı ve çıkış kodları değişmedi (kanıt: "Güvence").

- `make_template.py` (çağrılan dosya): komut satırı, sözleşme (`base-schema.json`) ve seçenek denetimi, yol korumaları, türetme akışı, öz denetim, rapor.
- `make_template_sheets.py`: veri sayfaları (satır 8+ değerleri, tablo kapasitesi, satır yüksekliği, satır 8 kimlik yazımı), Özet notları, formül aralıkları ve önbellek değerleri, çalışma kitabı (silinen sekmeler, tanımlı adlar, paylaşımlı metinler).
- `make_template_zip.py`: zip/XML katmanı, ilişkiler, parça silme ve Atınç'ın adlarıyla yeniden numaralama, paket denetimi (`[Content_Types].xml`, ilişkiler), hücre/aralık yardımcıları.

## Ne korunur, ne atılır

- **Korunur:** 17 sekme (base-schema.json'daki 15 tablo + Özet + FotoğrafKaynakları), satır 1–7 başlıkları, Excel tabloları ve stilleri, açılır listeler (x14 dahil), koşullu biçimler (extLst dahil), birleşik hücreler, dondurma, sütun genişlikleri, hücre biçimleri, formüller (Konular H, Fotoğraflar S/T, Özet sayım tablosu).
- **Atılır:** Berlin'e özgü DBKayıtları ve FotoAlbümü sekmeleri (çizim + 187 görsel dahil), bu parçaların `[Content_Types].xml` kayıtları, satır 8 ve altındaki bütün değerler, Özet'teki Berlin notları (A35, A39 ve birleşimleri).
- **Düzeltilir:** EkDetaylar tablosu kapasiteye iner (374 → 200 satır, A7:G207); Konular H formülü Yanıtlar tablo sonuna bakar (`$N$8:$N$307`); veri satırı yüksekliği 54; formül önbellekleri boş şablona göre (Özet'te "kalan" = asgari/hedef).
- **Yazılır:** Özet A3 = `Tilburg · Hollanda · CITY-901`. Teslimat satır 8: `1.0`, `city-901-v001` (daima küçük harf), `tilburg`, editor, `Tam teslim`, updated_on, `Taslak`, not = `Berlin örneğinden türetildi (make_template); içerik üretilmedi.` (900+ ise sonuna `YEREL DENEME; resmî katalog numarası değil.` eklenir); reviewer boş.

## Öz denetim (dosya yazılmadan önce)

Bulgu varsa dosya yazılmaz (çıkış `1`). Bakılanlar:

- 17 sekme; satır 7 anahtarları sözleşmeyle aynı; tablo aralıkları kapasiteye uygun; veri satırlarında değer kalmamış.
- Aracın kendi yazdığı Teslimat notu dışında hiçbir hücrede ve parçada örnek belirteci yok: Berlin, CITY-013, CITY-000, silinen sekme adları. Tarama harf ve aksan duyarsızdır; Türkçe büyük `İ` de yakalanır (`BERLİN`).
- Medya, çizim ya da hiçbir yere bağlı olmayan parça yok.
- Paket kuralları: `[Content_Types].xml`'de her ad tek kez kayıtlı, her kayıt var olan bir parçayı gösteriyor, her parçanın içerik türü var, her ilişkinin hedefi var. Biri bozuksa Excel ve .NET dosyayı açmaz.
- openpyxl dosyayı açıyor.

## Şehir satırı

Araç yalnız `city_id, name, country, country_code, region, kind = city, source_position = NNN` yazar. Gerisi Şehir yazarınındır; kaynaklı yazılır, **koordinat uydurulmaz**. Zorunlu olup boş kalanlar (rapordaki `city_required_blank`): `title, intro, currency, language, timezone, latitude, longitude, coordinate_source_url, coordinate_checked_on, source_url, source_checked_on, reviewed_on, priority, editorial_status`. `latitude`, `longitude`, `aliases` build_xlsx'te kimlik alanıdır: şablonda boş geldikleri için yazar bir kez doldurur, sonra değişmez.

## Katalog numarası

- `source_position` = Atınç kataloğundaki sıra numarası (421 şehir). Atınç'ın şablonlarında Aberdeen 3, Barcelona 9, Eindhoven 39; yani CITY-NNN ile aynı.
- Numara bilinmiyorsa **900+** ver (katalogla çakışmaz). Teslimat notu "YEREL DENEME" yazar, rapordaki `open_items`'a düşer. Resmî numara gelince şablonu aynı komutla yeniden türet.
- Sözleşme yalnız "tam sayı, en az 0" der. 900+ resmî doğrulayıcıdan geçer ama katalogda yoktur. Örneğin kendi numarası (013) reddedilir.

## Açık konu: priority

- Sözleşmede zorunlu tam sayı (en az 0); anlamı tanımlı değil. Araç boş bırakır ve `open_items`'a yazar.
- Şehir yazarı faz 4'te `priority` = 3 yazar (Atınç'ın üç şablonundaki değer: Aberdeen, Barcelona, Eindhoven); kullanıcıya sorulmaz (city-pack SKILL.md intake, kural 12).
- Anlam sorusu `manifest.open_items`'a bilgi olarak `owner: atinc` ile yazılır; aynı maddede `source_url`'nin (Kapsam kaynağı) anlamı da sorulur.
- **Teslimden önce dolu olmalı.** Boş kalırsa resmî doğrulayıcıda "Öncelik zorunlu." hatası kalır ve "yapı hatası 0" kapısı geçmez.

## Kontrol: boş şablon + resmî doğrulayıcı

```powershell
& $PY $TK\validate_all.py $WORK\_is\sablon_kaynak\CITY-901_tilburg_v001.xlsx $PKG --tools $TOOLS --mode audit --out $WORK\_is\val_sablon.json
```

Beklenen: çıkış `1` (şablon boş), `media.errors` 0 ve **tam 16 yapı hatası**, hepsi Şehir satırında:

- **SKILL.md B10'daki 8** (Atınç'ın şablonunda da var): Rehber başlığı (`title`), Rehber giriş metni (`intro`), Para birimi kodu ×2 (`currency`: "zorunlu" ve "3 büyük ASCII harf olmalı"), Yerel dil (`language`), Saat dilimi ×2 (`timezone`: "zorunlu" ve "geçerli IANA saat dilimi gerekli"), Rehber kontrol tarihi (`reviewed_on`).
- **Türetilen şablona özgü 8** (Atınç bunları kendi kataloğundan dolduruyor): Enlem (`latitude`), Boylam (`longitude`), Konum kaynağı (`coordinate_source_url`), Konum kontrol tarihi (`coordinate_checked_on`), Kapsam kaynağı (`source_url`), Kapsam kontrol tarihi (`source_checked_on`), Öncelik (`priority`), Editör durumu (`editorial_status`).

Bu 16 hata şablon kusuru değildir: `open_items`'a şablon hatası olarak (`owner: atinc`) **yazılmaz**. Hepsini faz 4'te Şehir yazarı kaynaklı doldurur. SKILL.md bunlara **şablon Şehir hataları** der: Atınç şablonunda 8, türetilen şablonda 16 (B10, "KUR temiz", faz 3 kapısı).

Dur ve şablonu bozuk say: Teslimat hatası (ör. "Teslimat kimliği …"), bu listede olmayan herhangi bir hata ya da çıkış `2`.

Ölçüm: Tilburg-901 ve Eindhoven-039 türetmelerinde aynı 16 hata çıktı. Atınç'ın Eindhoven şablonunda 9 hata var: B10'un 8'i + büyük harf `delivery_id`.

## Atınç'ın şablonuyla kabul edilen farklar (gerekçeli)

Eindhoven (039), Aberdeen (003) ve Barcelona (009) türetmeleri Atınç'ın şablonlarıyla karşılaştırıldı. Üçünde de yalnız şu farklar çıktı:

1. **Teslimat satır 8, 3 hücre (beklenen):**
   - `delivery_id` küçük harf (`city-039-v001`). Atınç büyük harf yazmış; resmî doğrulayıcı onu reddediyor.
   - `editor` = `Claude Code city-pack`.
   - `notes` = türetme notu.
2. **Şehir satır 8, 9 hücre boş (beklenen):** `latitude`, `longitude`, `coordinate_source_url`, `coordinate_checked_on`, `source_url`, `source_checked_on`, `priority`, `aliases`, `editorial_status`. Atınç bunları kendi kataloğundan dolduruyor; araçta kaynak yok, uydurulmaz. Şehir yazarı doldurur.
3. **İlişki kimlikleri farklı** (`rId…`): dosya içindeki rastgele etiketler. Her dosya kendi içinde tutarlı, hedefler aynı. Ekranda görünmez.
4. **XML yazım farkları:** ad alanı bildiriminin yeri ve öznitelik sırası. XML'in anlamı aynı. Ekranda görünmez.
5. **Stil tablosu Berlin'inki:** hücrelerdeki stil numaraları farklı. Ama her hücrenin çözülmüş biçimi aynı: sayı biçimi, yazı tipi, dolgu, kenarlık, hizalama, koruma. Koşullu biçim renkleri (157) de aynı. Silinen sekmelerden kalan 25 stil kaydı hiçbir hücrede kullanılmıyor. Ekranda görünmez.
6. **Özet'te `<mergeCells count="8">`:** Atınç'ın dosyasında `count` yok. İsteğe bağlı bir öznitelik; değeri doğru.
7. **Teslimat notu pakete geçebilir:** `Teslimat.jsonl` yoksa `build_xlsx` notu ve editörü şablondan alır; not "Berlin" ve "içerik üretilmedi" der. Atınç'ın notu da resmî Eindhoven paketine aynen geçmişti; yeni bir durum değil. city-pack faz 6'da `Teslimat.jsonl` ile `notes`'u günceller.
8. **x14/extLst koruması gerçek dosyada denenemedi:** Berlin'de ve Atınç'ın şablonlarında bu öğeler yok. Koruma yalnız sentetik testte doğrulandı. Berlin örneği bu öğelerle değişirse öz denetim ve testler yine geçmeli.

Bunların dışında fark yok: 17 sekme, 56 parça (adlar ve sıra), `[Content_Types].xml` (bayt bayt aynı, 38 kayıt), 52.419 hücrenin değeri ve biçimi, 16 tablo, açılır listeler, koşullu biçimler, birleşik hücreler, dondurma, sütun genişlikleri, satır yükseklikleri ve formüller (Konular H `$N$307`'ye kadar, Fotoğraflar S/T 1.200, Özet 24).

## Güvence

- `toolkit\tests\test_make_template.py` (23 Ekim'de 47 test, ~20 sn; test eklendikçe sayı değişir, güncelini toolkit klasöründe `pytest --collect-only -q tests\test_make_template.py` verir. Sentetik örnek ve zip/XML inceleme yardımcıları `tests\make_template_helpers.py`'de):
  - Sentetik örnekle: x14 uzantıları, bozuk/okunamayan örnek (docx, kesik XML, UTF-8 olmayan parça, eksik parça), yol korumaları, paket kuralları, Türkçe büyük `İ` taraması.
  - Gerçek dosyalarla: Berlin'den türetilen Eindhoven, Atınç'ın Eindhoven şablonuyla karşılaştırılır. Sekme listesi, satır 1–7, tablolar, DV, CF, birleşik hücreler, dondurma, Özet, formüller, `[Content_Types].xml` kayıt listesi (sırası dahil), xlsx_fidelity (0 fark) ve 52.419 hücrenin biçimi aynı.
  - Bölme: eski adlar (`Package`, `TemplateError`, `find_tokens`, `Sheet`, `Book`, `Stats`) `make_template`'ten aynı nesneyle erişilir; üç dosya, test dosyası ve yardımcısı 800 satırın altında.
- **Bölme sonrası Kabul A (23 Ekim):** kod bölündükten sonra türetme yeniden koşuldu, çıktılar bölme öncesiyle bayt bayt aynı (SHA-256): Eindhoven 039 (`--updated-on 2026-10-12`) `7a257ab7…`; Tilburg 901 `f67abd57…` ve Dortmund 902 `a1791973…` (`--updated-on 2026-10-23`; `uretim\eindhoven\_is\yedek_2026-10-23\08_sablon_turetme_kanit\` ile aynı; Tilburg yukarıdaki komutla). Atınç'ın Eindhoven şablonuyla fark yine yalnız beklenen 12 hücre (Teslimat B8/D8/I8; Şehir N8, O8, P8, Q8, S8, T8, W8, X8, AG8); `[Content_Types].xml` bayt bayt aynı, 56 parça aynı sırada.
- **Excel'de açılır:** Kopya, ayrı ve gizli bir Excel'de açıldı (17 sekme); .NET paket okuyucusu da açıyor. Düzeltmeden önceki çıktı ikisinde de açılmıyordu (`[Content_Types].xml`'de iki yinelenen kayıt).
- **Aberdeen ve Barcelona:** fark sınıfları Eindhoven'la aynı; `[Content_Types].xml` bayt bayt aynı; xlsx_fidelity 0 fark.
- **Resmî doğrulayıcı:** yukarıdaki 16 hata; başka hata yok.
- **build_xlsx (KUR bloğu)** türetilen şablonu sorunsuz kullanır (test).
