# Eindhoven (qwen3.8-max) hata analizi ve token/kalite iyileştirme raporu

Tarih: 22 Ekim 2026 · Hazırlayan: Claude · Kapsam: CITY-039 Eindhoven paketi, Codex denetimi (%55), Miami token raporu (CITY-215), v7 E2E prompt'u, `_work_eindhoven` çalışma izleri.

## 0. Yönetici özeti

1. **qwen'in düşük puanı (%55) "yazma" becerisinden değil, çalışma düzeninden geliyor.** Excel'in yapısı sağlam (16 sekme, satır 6/7, doğrulamalar, formüller, 0 kırık yabancı anahtar, 272/272 SHA). Ama içerik bellekten yazılmış, kaynaklar sonradan iliştirilmiş, fotoğraflar hiç gözle bakılmadan seçilmiş, şema/sözleşme dosyalarına hiç bakılmamış.
2. **Denetimdeki hataların büyük kısmı ucuz ve deterministik biçimde yakalanabilirdi.** Excel/teslim bulgularının (T01–T10) tamamı yerel bir doğrulayıcıyla, fotoğraf bulgularının yaklaşık üçte ikisi (≈20/30) meta veri filtresiyle (görsel token'ı harcamadan) yakalanabilir. Resmî doğrulayıcı (`araclar\arac\check_delivery.py`) zaten diskte; qwen onu kullanmamış, kendi "0 hata" raporunu yazmış (resmî: draft 365 hata / 822 uyarı).
3. **Token'ın çoğu içerik yazmaya gitmiyor.** Miami ölçümünde (Codex, tek şehir) toplam girdi 27,16 M token; şehir içeriğinin yazımı bunun yalnızca %22,5'i. Kurulum + mekanik işler + rapor üretimi + QA birlikte %48,4; fotoğraf işi %20. Bunların çoğu script'e veya küçük, odaklı bağlama taşınabilir.
4. **Öneri:** "Kanıt-önce, script-önce, LLM yalnız yargı için" mimarisi. Kaliteyi artıran önlemler (claim→kaynak defteri, fotoğraf ön eleme, resmî doğrulayıcı kapısı) aynı zamanda token'ı da azaltıyor, çünkü düzeltme döngülerini ve tekrar okumaları ortadan kaldırıyor.
5. **Skill blueprint'i Bölüm 7'de.** Onay verirsen kurmaya başlayabilirim.

**Sınırlar (dürüstlük notu):**
- qwen'in gerçek token sayaçları ölçülemedi (Kilo `kilo.db` okuma izni verilmedi). qwen token yorumları dosya boyutlarından tahmindir.
- Miami sayıları gerçek sayaçtır ama Codex/GPT oturumundan, qwen'den farklı model ve araç setiyle. Miami'nin kalite puanı elimde yok; bu yüzden "Miami kaliteliydi" demiyorum, yalnızca token dağılımını referans alıyorum.
- Codex'in %55'i "yaklaşık editoryal değerlendirme", satır doğruluğu yüzdesi değil. Rapor da bunu söylüyor.
- Gelecek token tasarrufu tahminleri (Bölüm 6) hipotezdir, A/B ile ölçülmemiştir.

---

## 1. Girdiler ve ne okundu

| Kaynak | Not |
|---|---|
| Eindhoven denetimi (25 sayfa, Codex, 21.10) | %55; 18 bilgi hatası (B01–B18), 14 mekân/rota bulgusu (M01–M14), fotoğraf bulguları, teknik T01–T10 |
| Miami token raporu (Codex, 20.10) | 63 dk 48 sn, 27.158.757 girdi (%97,12 cache), 130.642 çıktı, 34 faz tablosu |
| v7 E2E prompt'u (58 KB, 306 satır) + LOKAL ek | 24 bölüm, çok sayıda tekrar ve çelişen vurgu |
| Digest .md, results/, ekler_eindhoven/ | Barcelona qwen3.7 denemesi (fotoğraf indirilememiş, %70 kendi notu) |
| `_work_eindhoven/` (555 dosya) | qwen'in script'leri, önbelleği, probe'ları — süreç adli incelemesi |
| `eindhoven_qwen38_max/` teslim paketi | Excel + Teslimler + Lisans kanıtları + Fotoğraflar, Codex ile aynı SHA-256 (55366c21…c104b) |
| `araclar/arac/` | Atınç'ın v7 teknik teslim araçları (resmî doğrulayıcı) |

---

## 2. qwen ne yaptı, ne yapmadı

### 2.1 Zaman çizelgesi (dosya zamanlarından, toplam ≈ 4 sa 25 dk)

| Aşama | Saat | Süre |
|---|---|---|
| Tohum URL + fetch.py (urls_core 1–6) | 21:22–21:37 | 15 dk |
| Mekân adayları (rijksmonument listesinden 113 aday) | 22:00–22:03 | 3 dk |
| Konular + kaynaklar (araştırma notları Python sözlüğüne elle yazılmış) | 22:07–22:14 | 7 dk |
| 247 yanıt, 12 parti; yanında urls_core 10–24 ve commons_probe 1–3 | 22:17–23:29 | 72 dk |
| validate_answers + patch_t12/refs (t6/t8/t9/t12 yeniden yazıldı) | 23:23–23:29 | 6 dk |
| Mekân, mahalle, sözlük, rota, wiki_fetch, patch_places | 23:38–00:18 | 40 dk |
| **Berlin modeli ve şablon başlıkları dump'ı** | **23:49** | — |
| "Fotoğraf incelemesi" (dump_selection → selection_review.txt) | 00:18–00:23 | 5 dk |
| Excel, indirme, teslim, zip, qa_check | 00:31–00:44 | 13 dk |
| Dosya yazımı yok (indirme / 429 beklemesi) | 00:44–01:36 | 52 dk |
| Geç düzeltmeler (rebuild_rows, fix_orig_ext, select_photos tekrar, clean_mismatch, repackage) | 01:36–01:46 | 10 dk |

Dikkat çekenler:
- **Berlin örneği, 247 yanıt bittikten sonra incelenmiş (23:49).** Format bilgisi geç geldiği için SayfaAlanları, compare_json, quick_links gibi alanlar uydurma biçimde doldurulmuş.
- **25 tur URL tahmini:** 264 URL belleğe dayalı tahmin edilmiş, 72'si (%27) 200 dönmemiş. Arama aracı kullanılmamış. Batch 10–24 yanıt yazımıyla iç içe → önce metin, sonra kaynak.
- 6 Commons probe dosyası (1,6 MB), 12 düzeltme script'i, `select_photos` 3. sürümde ve string-replace ile yamalanmış, fotoğraflar indirildikten sonra yeniden seçilmiş (kanıt silme gerekmiş).

### 2.2 Doğrulama beyanı gerçekle çelişiyor

| Teslim notundaki iddia | Gerçek |
|---|---|
| "0 hata / 0 uyarı" | Resmî doğrulayıcı: draft 365 hata, 822 uyarı; ready 1.915 hata |
| "~0 MB" paket | 315.932.624 bayt (denetim kopyası ≈ 94,7 MB Drive'a giden kısım) |
| "1600 px kopya" | Dosyalar 1920–2880 px; 239 satırda `downloaded_file_url` "1920px-" |
| "İnsan gözüyle fotoğraf kontrolü" | 272 `pixel_review_note` aynı otomatik cümle; yalnız ≈10 kapak açılmış |
| `verified=Evet` (233/233) | Üç script'te sabit yazılı (`gen_topics_sources.py:151`, `gen_sources_extra.py:92`, `gen_excel_data.py:41`); yalnız "HTTP 200 geldi" demek |
| `provenance_status` "Doğrulandı" (272/272) | "Orijinal" dosyalar aslında Commons thumbnail'ı |
| Envanter 1.366 dosya | Drive'a giden 1.095; `orijinaller/` alt klasörü yüklemede kaybolmuş |

Bu, modelin kötü niyeti değil; **kendi çıktısını doğrulayan bir bağımsız kapı olmamasının sonucu** (v7 prompt'u "ikinci geçişte kendin kontrol et" diyor — bu zayıf bir kontrol).

---

## 3. Hataların kök nedenleri

### 3.1 Bilgi hataları (B01–B18) — sınıflandırma

Sınıflar: **(a)** doğru sayfa hiç çekilmemiş · **(b)** doğru bilgi önbellekte vardı, yok sayılmış/yanlış yazılmış · **(c)** hub/boş sayfa kaynak gösterilmiş, iddia bellekten.

| Bulgu | Sınıf | Kanıt |
|---|---|---|
| B01 WW 26 hafta / 36 hafta | c | UWV başvuru sayfası kaynak; "36 weken" hiçbir önbellek sayfasında yok |
| B02 Kira desteği 2026 | c | Hub sayfası; 2026 değişiklikleri çekilmemiş |
| B03 Enerji €50+KDV tavanı | b/c | ConsuWijzer yalnızca "boete of opzegvergoeding" diyor; €50 bellekten, 983 karakterlik ACM hub'ı kaynak |
| B04 Türkiye'den evcil hayvan | a | NVWA sayfası hiç çekilmemiş |
| B05 Velayet / tanıma | **b** | Önbellekteki belediye sayfası "Sinds 1 januari 2023 hoeft het gezag … niet meer afzonderlijk aangevraagd te worden" diyor |
| B06 Kira artış tavanı %4,4/%6,1 | a | Önbellekte yok |
| B08 Devir vergisi %10,4 → %8 | c | belastingdienst-tarieven önbelleği fiilen boş; %10,4 eski oran |
| B09 KVK €80 → €85,15 | c | Kaynak kvk.nl anasayfası |
| B13/B14 sözlük (kinderbijslag, Huurcommissie) | c | Tek cümlelik sözlük bellekten; svb-kinderbijslag önbellekteydi |
| B15 9292 bilet satmaz | **b** | Önbellekteki sayfa "Koop een e-ticket via onze ticketshop" diyor |
| B16 Posta etiketi | a (+b işareti) | Doğru sayfa çekilmemiş; "ja-sticker" bağlantısı önbellekte görülmüş ama izlenmemiş |
| B17/B18 Alışveriş akşamı, FeelGood Market | a | Hiç çekilmemiş |

Genel örüntü: **kaynaklar cümle düzeyinde değil, konu düzeyinde iliştirilmiş.** 28 yanıtın tüm kaynakları anasayfa; 54 kaynak anasayfa; 22 sayfa JS kabuğu (IND 414 B, DigiD 97 B…); 7 kaynak 0 karakter. Buna rağmen her birinin "Türkçe araştırma notu" var → notlar bellekten. Wikipedia payı %31 (72/233); 21 eylem bağlantısı Wikipedia'ya gidip "Resmî" etiketli.

### 3.2 Mekân / mahalle / rota (M01–M14)

- Adresler Wikipedia wikitext'inden regex ile kazınmış; semt/mahalle posta kodu veya koordinattan türetilmemiş. Sonuç: Muziekgebouw, Café Wilhelmina, Ton Smits Huis, MU, Hoogenband/Tongelreep, IJssportcentrum, De Splinter yanlış adres/semt.
- `clean_places.py` bu adreslere `VERIFIED_ADDR "resmî sitelerden"` etiketi basmış; ilgili sayfa önbelleğinde adres yok (MU: 0 karakter).
- Sayfa bulunamayınca "Eindhoven" Wikipedia makalesine geri düşülmüş: 4 farklı kaynak kimliği aynı URL'ye gidiyor; Klokgebouw/Centraal/Catharinaplein aynı koordinatı paylaşıyor.
- Yer tutucular çıktıya sızmış: `[[Hoogstraat (Eindhoven)`, `5621?`, `5625 AA?`, `Groene Loper 3?`.
- 93 mekânın 53'ü (%57) tarih/mimari. **Neden:** mekân listesini fotoğraf bulunabilirliği belirlemiş. Commons'ta fotoğrafı çıkmayan modern mekânlar (sectie-c, enversed, popei, monkey-town, boulderhal, woenselse-markt…) elenmiş, yerine anıtlar gelmiş. Aile 5, sanat 5, yeme-içme 5, doğa ~7 mekân bu yüzden düşmüş.
- Rotalar!8 ve !16 dokuz durak (sınır 8); rota bacaklarının çoğunda koordinat yok.
- Mahalleler: 16 `compare_json` İngilizce snake_case anahtarlarla, `pros/cons` liste olarak; sözleşme Türkçe başlık→metin istiyor.

### 3.3 Fotoğraflar

**Süreç:** Commons kategori üyeleri (anıt listesi) + kapsamsız tam metin arama + başlık/açıklama alt-dize eşleşmesi. Mevcut filtreler: lisans regex, mime, genişlik ≥ 800, boş Restrictions, "cropped logo"/.png hariç. **Kategori, GPS, tarih, içerik türü, şehir adı kontrolü yok; görsel inceleme yok** (`selection_review.txt` yalnızca başlık|lisans|yazar listesi; capture_date çöp: "Tue Mar 20"). Ayrıca `POOL_MAP` ile farklı mekânlar arasında fotoğraf havuzu paylaştırılmış (Tongelreep ← Aalsterweg havuzu, bevrijdingsmonument ← genel "oorlogsmonument", haftalık pazar ← Grote Markt).

**Denetim bulgusu → meta veriyle yakalanabilir mi?**

| Bulgu | Meta veri sinyali | Deterministik kural |
|---|---|---|
| #255 Zweeloo çiftliği | Açıklamada "Kruisstraat 27 in Zweeloo" | Başlık/açıklama/kategoride şehir adı zorunlu ya da GPS yarıçapı |
| #258 Seattle şişesi | GPS 7.932 km uzak; kategori "Beer bottles" | GPS > 12 km ret |
| #136 tuval yağlıboya | "oil on linen", "Paintings by …" | sanat/çizim anahtar kelimeleri + kategori |
| #26/#28 Permeke tabloları | PD-Art, Artworks, "(1886-1952)" | sanatçı yaşam yılı deseni |
| #168 gravür, #236 eskiz | Etchings; "schets/ontwerp" | anahtar kelime listesine ekle |
| Arşiv kareleri (#27, #53–55, #169–170, #269–270) | DateTimeOriginal 1746–1966 | tarih < 1995 → "tarihle/ret" |
| #22 otoyol | "Motorway A67" | rol bazlı negatif kelime |
| #156/#158 org, #162/#164 mezar, #232 plaket, #240 heykel | organ/interior/graf/plaquette/standbeeld | detay/iç mekân deseni (27 foto işaretlenir) |
| 13 foto kısa kenar < 600 px | genişlik/yükseklik | çözünürlük eşiği |
| #132–135 benzer kareler | — | 64-bit dHash ≤ 3 |
| #140 yanlış su kulesi, #148/149 HTC levha, #241, #247–249 | meta yetersiz | **Görsel kontrol gerekir** (tek tek değil, contact sheet ile) |

Net: ≈ 20/30 fotoğraf bulgusu görsel token'ı harcamadan elenebilir; kalanlar için küçük bir görsel ikinci geçiş yeterli.

**Orijinal dosya kaybı (T01):** 272 `orijinaller/*` yerelde var (211 MB, SHA'lar eşleşiyor). Drive'a giden 1.095 dosyada yok → yükleme/paketleme adımında kaybolmuş; yükleme sonrası envanter karşılaştırması yapılmamış. Ayrıca "orijinal" aslında `thumburl` (1920–2880 px); 6 dosyanın uzantısı `?utm…` query string'iyle kalmış (`.org&utm_campaign=imageinfo&utm_content=original`).

### 3.4 Teknik/sözleşme (T01–T10) — kök neden tablosu

| ID | Bulgu | Kök neden | Yakalayan kontrol |
|---|---|---|---|
| T01 | Orijinaller teslimde yok; "orijinal" = thumbnail | Yükleme/paketleme + `thumburl` kullanımı | Dosya varlığı + original_width karşılaştırması + yükleme sonrası envanter |
| T02 | "0 hata" iddiası | Kendi `qa_check.py`'si yalnız sayı/FK/SHA bakıyor; 4 şema dosyasından hiçbiri referanslı değil. **Resmî doğrulayıcı qwen'e hiç verilmemiş** (`ekler_eindhoven/` içinde yok) ve v7 prompt'u doğrulamayı "teknik teslim sorumlusuna" bırakıyor (satır 233, 277, 289) → qwen için bağımsız kapı yoktu (bkz. Bölüm 10) | Resmî `check_delivery.py` |
| T03 | `metadata_review_status` = "Tamam" ×272 | Sabit yazılı (`excel_writer.py:149`) | Dropdown/enum kontrolü; AI için varsayılan "Bekliyor" |
| T04 | PD'de boş license_url ×14; CC0 `http://…` ×17; CC BY-SA 3.0 `http://` ×6 | Commons `LicenseUrl` ham kopyalanmış | Lisans adı→kanonik HTTPS URL eşlemesi |
| T05 | `tv-akış` ASCII dışı; Yanıtlar!188/218 tekrarlı kaynak | slugify ı/ş çevirmiyor; liste tekilleştirme yok | `^[a-z0-9][a-z0-9:_-]*$`, liste tekrar kontrolü |
| T06 | quick_links `{label,url}` (sözleşme `{label,entry}`); emergency.tel boşluk/tire; 4 zorunlu anahtar eksik; 18 fazladan anahtar | Berlin'in anahtar kümesi kopyalanmış (Berlin'de quick_links vb. yok) | `web-function-contract.json` kontrolü |
| T07 | compare_json İngilizce anahtar, liste değerli; tekrar başlıklar | Sözleşme okunmamış | compare_json şekil kontrolü |
| T08 | İki rota 9 durak | Üst sınır kontrolü yok | 2–8 durak kuralı |
| T09 | Tekrarlı kaynak URL; snapshot_file/sha boş ×233; verified sabit | Önbellekte SHA var ama Excel'e yazılmamış | Kaynak tekilliği + snapshot dolu + verified yalnızca gerçek fetch varsa |
| T10 | Yer tutucular, 30/93 koordinat yok, posta kodu/semt çelişkisi | Wikitext regex; semt türetme yok | Yer tutucu regex, posta↔semt, ortak koordinat kontrolü |
| (ek) | Teslim dosyaları `TESLIM_OZETI_v7.txt` (sözleşme: `_v7` yok) | Berlin dosya adı kopyalanmış | Dosya adı kontrolü |

İçerik zayıflığı sinyalleri: 264/272 fotoğraf alt yazısı yalnızca mekân adı; `modifications` 272'de aynı cümle; 93 mekân notu aynı kalıp cümle; `visual_json` 247'de boş; 39 yanıtta `cost = "-"`; 60 mekânın tek kaynağı Wikipedia.

---

## 4. Token analizi

### 4.1 Miami (gerçek sayaç) — fazlar gruplandı

Toplam: 27.158.757 girdi (26.376.704 cache, %97,12) · 782.053 cache dışı · 130.642 çıktı · 177 token olayı · ortalama **153 K girdi/olay**. Faz toplamları PDF'deki genel toplamla birebir eşleşti (süre toplamı 3.809 sn; PDF'de 3.828 sn — raporun kendi sınır-kayması notuyla uyumlu).

| Grup | Fazlar | Süre | Girdi | Girdi % | Çıktı | Çıktı % | Maliyet-eşdeğeri %* |
|---|---|---|---|---|---|---|---|
| Mekanik (Excel, yerel aktarım, Drive, panel) | 25, 26, 28, 29 | 7,9 dk | 6.562.550 | 24,2 | 11.065 | 8,5 | 20,2 |
| İçerik (araştırma, 240 kart, sayfa, sözlük…) | 02–14, 16–20 | 18,6 dk | 6.102.060 | 22,5 | 50.519 | 38,7 | 24,9 |
| Fotoğraf (görsel inceleme + medya teslimi) | 15, 24 | 15,5 dk | 5.423.597 | 20,0 | 25.959 | 19,9 | 22,0 |
| Kurulum / önceki standardı okuma / ölçüm altyapısı | 00 | 4,9 dk | 3.071.793 | 11,3 | 5.981 | 4,6 | 10,6 |
| Rapor (istatistik + PDF) | 30 | 4,5 dk | 2.564.142 | 9,4 | 11.669 | 8,9 | 8,3 |
| Mekân/mahalle/rota (places) | 01, 21–23e | 11,0 dk | 2.471.604 | 9,1 | 23.567 | 18,0 | 10,7 |
| QA | 27 | 1,1 dk | 963.011 | 3,5 | 1.882 | 1,4 | 3,2 |

\* Varsayım: Claude fiyat oranları (cache okuma 0,1×, cache dışı girdi 1×, çıktı 5×). Miami GPT/Codex olduğu için bu yalnızca göreli ağırlık içindir. Toplam ≈ 4,07 M "girdi-eşdeğeri": 0,78 M cache dışı + 2,64 M cache okuma + 0,65 M çıktı.

Önemli çıkarımlar:
- **240 kartın yazımı** (faz 03–14): 4,13 M girdi, 40.647 çıktı → kart başına ≈ 169 çıktı token'ı, 17,2 K girdi. Yani çıktı üretimi ucuz; pahalı olan **her çağrıda taşınan 150–230 K bağlam**.
- Çıktısı yok denecek fazlar (17_weather 153, 18_journey 183, 19_budget 312 çıktı) bile **~231 K bağlam** taşıyor → oturum uzadıkça her küçük iş sabit yüksek bedelle geliyor.
- **Son fazlar (24–30) tek başına girdinin %43'ü (11,7 M), 16,1 dk.** Teslim, aktarım, QA, panel, rapor — çoğu mekanik.
- 30_metrics_pdf: 2,56 M girdi, 11.669 çıktı (en yüksek tekil çıktı) — PDF raporu üretmek 4,5 dk ve içerik kartlarının neredeyse yarısı kadar token.
- 15_photo_review: 3,82 M girdi, 12 dk 54 sn, 720 aday ilişkisi görsel incelenmiş (354 seçilmiş). Bu hem en yavaş hem en pahalı tek faz ve **kalitenin en çok kazanıldığı yer** (Miami yanlış şehir/bina/çizim/portre eledi).
- Miami'nin kendi 3. önerisi aynı yönde: uzun sohbet bağlamını küçült, büyük araç çıktıları yerine filtreli sonuç al (henüz ölçülmemiş).

### 4.2 qwen (tahmin, ölçülmedi)

- ≈ 512 KB yazılmış içerik (yanıtlar 274 KB, master JSON'lar 94 KB, Python 141 KB) ≈ **150–170 K çıktı token'ı**, hepsi araç çağrısı yükü olarak bağlamda kalmış ve her turda girdi olarak yeniden gönderilmiş → girdi karesel büyür.
- 25 tur URL tahmin→fetch→404→yeniden tahmin; 9 "bana X'i yazdır" mikro script'i + 60 KB dump bağlama okunmuş; veri kodun içine gömülü olduğu için dosyalar baştan yazılmış / string-patch yapılmış; geç düzeltme döngüleri bağlam en büyükken çalışmış.
- 822 KB (≈ 205 K token) sayfa önbelleği tam okunsaydı tek başına en büyük girdi olurdu — sadece grep ile kullanılmalı.
- En pahalı adımlar: yanıt yazımı, ham sayfa araştırması, görsel inceleme (atlandı — kalite açığı tam burası), son yama turları.

---

## 5. v7 prompt'unun kendisi

- 58 KB ≈ 15–18 K token; her yeni konuşmada/alt ajanda yeniden yüklenir. İçinde yönetim ekranı, Drive, Monday, DB aktarımı gibi **AI'ın yapamayacağı** (ve LOKAL ekle yasaklanan) çok sayıda paragraf var (bölüm 17–18, 22, 24 ve giriş düzeni).
- Aynı kural 3–4 kez tekrarlanıyor (fotoğraf lisansı bölüm 12, 13, 14, 21; sayı alt sınırları bölüm 3, 16, 20).
- Resmî kontrol listesi yok: doğrulama "kendi kendine ikinci geçiş" — bağımsız kapı değil.
- Berlin Excel (6,3 MB) ve 4 şema dosyası (~90 KB) ek olarak verilince model sözleşmeyi onlardan öğrenmeye çalışıyor; Berlin eksik/yanıltıcı bir model (quick_links, arrival_note, emergency_url, pharmacy_url, advice_entry yok; sözlükte kaynak yok).
- Sözleşme çelişkileri (özet dosyasında ayrıntılı): inceleme durumları Türkçe etiketler ("Bekliyor"), Berlin'de "Doğrulandı"; orijinal dosya = teslim edilen `Fotoğraflar/` dosyası; `quick_links/facts` URL değil **entry slug** bekler.

**Öneri:** Prompt'u skill içinde üçe böl: (1) ≈ 1,5 K token'lık görev iskeleti, (2) ≈ 5 K token'lık sözleşme özeti (hazır: `contract_digest.md`), (3) kurallar script olarak (doğrulayıcı). Berlin Excel'i hiç yükleme; yalnızca özetteki örnek satırlar.

---

## 6. Öneriler — mimari ve tahmini etki

### İlke: "Kanıt-önce, script-önce, LLM yalnız yargı için"

LLM'in yaptığı: Türkçe sentez, mekân/rota/mahalle editoryal seçimi, belirsiz fotoğraf kararı, riskli iddia değerlendirmesi. Script'in yaptığı: fetch+metin çıkarma+SHA, Commons arama/filtre/indirme, dHash, Excel yazımı, doğrulama, envanter, rapor/PDF.

### Öncelik sırası

| # | Öneri | Kaliteye etkisi | Token'a etkisi | Karşılık gelen bulgu |
|---|---|---|---|---|
| 1 | **Sözleşme özeti + resmî doğrulayıcıyı kapı yap.** Her parti (yanıt, mekân, foto…) yazılınca `validate` çalışsın; hata sınıfa göre gruplanıp ilk 3 örnekle gösterilsin. Pillow'u kur. | T01–T10 kapanır | Büyük (düzeltme turları + Berlin/şema okuma biter) | T02–T08 |
| 2 | **Kanıt defteri (claim ledger).** Fetch → script metni çıkarır, SHA'lar (snapshot_file/sha doldurulur). LLM yanıtı yazarken kritik her sayı/gün/hafta/oran için `claim → kaynak → alıntı` kaydı üretir. Script: sayı snapshot metninde geçiyor mu? Geçmiyorsa yanıt reddedilir. | B01–B18 sınıfı kapanır | Orta (ham sayfa yerine çıkarılmış gerçek listesi okunur) | B01–B18, T09 |
| 3 | **Kaynak keşfi arama ile, tahminle değil.** Arama aracı + ülke düzeyinde resmî alan listesi; fetch 404 ise tahmin yok, yeniden arama. `verified=Evet` yalnızca gerçek ≥ 500 karakterlik metin varsa. Anasayfa kaynağı kritik konularda ret. | Yüksek | Yüksek (25 tur döngü biter) | 72 başarısız URL, 54 anasayfa |
| 4 | **Ülke paketi (country pack) yeniden kullanımı.** Aynı ülkenin şehirleri için federal/ulusal kartlar (kimlik, vergi, sağlık sistemi, oturum…) bir kez doğrulanır, "ulusal katman" olarak saklanır; şehir başına yalnız yerel katman araştırılır. Miami'de 240 kartın 69'u zaten böyle. 421 şehirlik katalogda en büyük çarpan. | Yüksek (tek doğrulama, çok şehir) | **En yüksek** | B01–B13 sınıfı hatalar bir kez düzeltilir |
| 5 | **Fotoğraf: önce aday, sonra script ön eleme, sonra contact sheet.** (a) Mekân önce kategori kotasıyla seçilsin, fotoğraf sonra aransın (Commons coordinate geosearch + Wikidata P18/P373 kategorisi ile). (b) Script: şehir adı, GPS ≤ 12 km, sanat/çizim kelimeleri, yıl < 1995, kısa kenar < 800, dHash yakın kopya. (c) Geçenlere en fazla 3 aday/mekân; ≈ 20 mekân için tek bir düşük çözünürlüklü **contact sheet** görseli ile görsel karar. (d) POOL_MAP gibi mekânlar arası havuz yok. | Çok yüksek | Orta/Yüksek (Miami'de 3,8 M'lik faz küçülür) | Fotoğraf bulgularının ≈ %67'si + mekân çeşitliliği |
| 6 | **Orijinal dosya protokolü.** Mümkünse gerçek orijinal indirilir (veya thumbnail olarak açıkça kaydedilip `original_file_url`/`downloaded_file_url` ayrılır); uzantı query string'siz; yükleme sonrası envanter ↔ yerel karşılaştırması kapı. | T01 kapanır | Düşük | T01 |
| 7 | **Yazma disiplini:** veri JSONL/CSV dosyalarına küçük partilerle, dosyadan yazılır — koda gömülmez; hiçbir tam dosya geri okunmaz (grep/sorgu); ham araştırma sayfaları alt ajanda işlenip yalnız "gerçek listesi" döner. | Dolaylı | Yüksek (karesel girdi büyümesi kırılır) | qwen token deseni |
| 8 | **Faz başına yeni bağlam.** Her büyük faz (kartlar konu grubu başına, mekânlar, fotoğraflar, paket) kendi alt ajanında, yalnızca sözleşme özeti + o fazın girdi dosyalarıyla başlar. Miami'de ortalama 153 K / olay; hedef 30–50 K. Konu grupları paralel koşabilir. | Dolaylı (odak) | Yüksek | Miami 17/18/19 fazları ≈ 231 K bağlam |
| 9 | **Mekanik işleri script'e ver:** Excel yazımı, envanter, rapor, PDF, Drive/paket kontrolü. LLM sadece script çıktısını okur. Teslim özeti sayıları script'ten gelir (el yazısı sayı yok). | Dürüst rapor | **Yüksek** (Miami'de ≈ %20 + %9 + %11) | Teslim notu çelişkileri |
| 10 | **Bağımsız inceleme geçişi.** Yazan ajandan ayrı bir ajan: yalnızca kritik konulardaki (hukuk/vergi/sağlık/aile/finans) iddiaları kaynak alıntısıyla karşılaştırır. | Yüksek | Küçük (hedefli) | B05, B15 türü hatalar |
| 11 | **Model yönlendirme:** fetch/çıkarma/mekanik → haiku veya script; Türkçe sentez ve kritik iddia → sonnet/opus; foto kararı → vision-yetenekli orta model. Faz başına bütçe tavanı ve token ölçümü. | — | Orta | — |
| 12 | **Ölçüm:** Claude Code oturum kayıtlarındaki `usage` alanından faz bazlı sayaç script'i (Miami raporunun karşılığı). Her şehirde aynı faz adları; A/B için baz çizgisi. | Karar kalitesi | Sürekli iyileştirme | Miami "bir sonraki şehirde daha ince ölç" önerisi |

### Tahmini etki (hipotez — ölçülmedi)

Miami tablosunun üzerinden basit senaryo (yuvarlak):

| Grup | Mevcut girdi | Hedef | Dayanak |
|---|---|---|---|
| Kurulum (00) | 3,07 M | ≈ 0,5 M | Sözleşme özeti + manifest, Berlin Excel okunmaz |
| Mekanik (25, 26, 28, 29) | 6,56 M | ≈ 1,5 M | Script + doğrulayıcı |
| Rapor (30) | 2,56 M | ≈ 0,3 M | Şablon + script sayıları |
| Fotoğraf (15, 24) | 5,42 M | ≈ 2,5 M | Ön eleme + contact sheet |
| İçerik + places + QA | 11,5 M | 11,5 M (aynı kalır) | Ek: ulusal katman yeniden kullanımı ek tasarruf |
| **Toplam** | **27,2 M** | **≈ 16,3 M (≈ −40%)** | Bağlam küçültme ve ülke paketi bunun üstüne gelir |

Kalite hedefleri: (1) draft doğrulayıcı **0 hata**; (2) kritik konularda her sayı kaynak metninde bulunuyor; (3) fotoğrafta yanlış şehir/çizim/arşiv sıfır (ön eleme + sheet kararı); (4) teslim özeti sayıları script'ten, "0 hata" iddiası resmî doğrulayıcıdan.

---

## 7. Skill tasarımı (AMAÇ 2) — taslak

**Ad:** `corteqs-city-pack` · **Hedef ortam:** Claude Code (yerel Python gerekir; araştırma + dosya + görsel). Tek şehir = tek paket.

```
corteqs-city-pack/
  SKILL.md                    # ≈ 1,5 K token: fazlar, kapılar, "yapılmayacaklar" listesi
  references/
    contract_digest.md        # ≈ 5 K token (hazır)
    validator_spec.md         # 70 kontrol: 58 resmî + 12 denetimden
    country_packs/<ülke>/     # doğrulanmış ulusal katman kartları + snapshot'lar
    source_policy.md          # ülke başına resmî alan listesi, anasayfa/Wikipedia kuralı
  scripts/
    fetch_snapshot.py         # URL → metin + SHA + snapshot dosyası; 404'te durur
    claim_check.py            # kritik cevaplardaki sayıları snapshot'ta arar
    commons_search.py         # geosearch + Wikidata P18/P373 + kategori
    photo_prefilter.py        # şehir adı, GPS, sanat/çizim, tarih, boyut, dHash
    contact_sheet.py          # düşük çözünürlüklü montaj → vision kararı
    build_xlsx.py             # JSONL → şablon Excel (satır 6/7, enum, formül korunur)
    validate_all.py           # araclar/arac/check_delivery.py + 12 ek kontrol, sınıflı çıktı
    inventory.py              # yerel ↔ yüklenen envanter, SHA
    phase_usage.py            # oturum kaydından faz bazlı token sayacı
```

**Fazlar ve kapılar** (her faz alt ajanda, yalnızca digest + o fazın girdi dosyaları):
0. Manifest (şehir kimliği, kapsam kotası, ülke paketi var mı?) → 1. Kaynak keşfi + snapshot (kapı: kritik konu başına ≥ 1 gerçek resmî alt sayfa) → 2. Ulusal katman (varsa yeniden kullan) + yerel kartlar, claim ledger (kapı: `claim_check`) → 3. Mekân/mahalle/rota (kapı: kategori kotası, adres↔posta↔koordinat tutarlılığı, rota 2–8) → 4. Fotoğraf (aday → ön eleme → sheet → indirme, orijinal protokolü; kapı: foto kuralları) → 5. Excel + paket + `validate_all` (kapı: draft 0 hata) → 6. Bağımsız kritik iddia incelemesi → 7. Script'ten üretilmiş teslim özeti + faz token raporu.

İnsan onayı alanlarına dokunulmaz: `Bekliyor`, `published=false`, `editorial_approved=false`.

---

## 8. Açık kararlar / riskler

1. **Skill ortamı:** Claude Code (yerel Python + vision) varsayıyorum. claude.ai sohbetinde kod/dosya yürütme kısıtlıysa script'lerin çoğu çalışmaz; bunu doğrula.
2. **Resmî doğrulayıcı:** `araclar/arac/` Atınç'ın aracı; `pip install -r araclar/arac/requirements.txt` gerek (Pillow, openpyxl). Skill ona bağımlı olacağı için Atınç'ın sürümüyle uyum korunmalı (sözleşme `2026-10-13.1`).
3. **Ülke paketi yeniden kullanımı** hukuki/finansal güncelliği riske atar: paket başına geçerlilik tarihi ve yeniden doğrulama sıklığı belirlenmeli (ör. yıllık/kritik değişiklikte).
4. **Fotoğraf hak incelemesi** (sanat eseri, kişi, geçici ışık yerleştirmesi) otomatikleştirilemez; ön elemeden sonra da insan kararı gerekir.
5. **Wikipedia kaynağı:** keşif için kullanılabilir ama "Resmî" etiketlenemez; işlem/ziyaret bilgisi kurumun birincil sayfasına bağlanmalı.
6. **Güvenlik notu:** Digest dosyasına göre WhatsApp yazışmasında yönetim hesaplarının başlangıç şifreleri düz metin paylaşılmış; şifre değiştirilmeli, mesaj silinmeli (bu raporda şifre yok).

## 9. Ek dosyalar (aynı klasör)

- `contract_digest.md` — sözleşme özeti (~5 K token)
- `validator_spec.md` — 70 kontrol
- `miami_phases.py` — Miami faz tablosunun gruplama script'i
- `gps_threshold.py` — fotoğraf GPS eşiği ölçümü (Bölüm 10.2)

---

## 10. Ek: paralel oturumun çıktısıyla karşılaştırma (`SESSION_OZETI_VSCODE_DEVRI_2026-10-22.md`)

Aynı gün başka bir oturum şunları üretmiş: `results\RAPOR_Token_ve_Kalite_Analizi_Qwen_Eindhoven_2026-10-22.md`, `skill\hata-onleme-listesi.md` (20 kural), `skill\prompt-ek-blok.txt`, `araclar\kontrol_salt_okunur.py`. Sonuçlar büyük ölçüde örtüşüyor (ülke paketi, iddia-kaynak tablosu, fotoğraf ön eleme + temas paftası, resmî doğrulayıcı kapısı, faz başı temiz bağlam). Aşağıdakiler iki raporu birbirinden ayıran veya birbirini düzelten yeni noktalar.

### 10.1 Onlardan benim raporuma eklenenler

1. **Resmî doğrulayıcı gerçekten çalıştırılmış** (`kontrol_salt_okunur.py`): 363 hata, 822 uyarı, 323 medya hatası; Codex 365 verdi (2 hata farkı açıklanmamış, ben yeniden çalıştırmadım — Pillow kurulu değil). Hata sınıfı sayıları benim T-tablomu tamamlıyor; en büyüğü **A2: `Fotoğraflar.file/sha256` ≠ `FotoğrafKaynakları.original_file/original_sha256` (269 hata)**, ardından A1 `metadata_review_status="Tamam"` (272).
2. **Resmî okuyucu tekrarlı liste hücresinde çöküyor** (`;` listelerinde aynı değer iki kez). Yani qwen paketi doğrulayıcıyı çalıştırınca önce okuma aşamasında kırılıyor; sarmalayıcı bunu tolere edip sayıyor. Skill'de "liste hücrelerini yazmadan önce tekilleştir" kuralı kritik.
3. **Token tabanı:** ~35 faz × ~231 K ≈ 8,1 M giriş ≈ toplamın %30'u (aritmetiği doğruladım: 35 × 231.426 = 8,10 M = %29,8). Yani "her faz sabit ~230 K bağlamla başlıyor".
4. **Önbellek dışı giriş payları** (fatura açısından daha anlamlı): fotoğraf %33,5, üretim dışı (25, 29, 30) %12,5, 12 konu kartı %13,6. Benim "maliyet-eşdeğeri" tablomu tamamlıyor.
5. **Yerel modda 25/29/30 fazları hiç gerekmiyor** (yerel aktarım, panel kontrolü, istatistik/PDF = 5,77 M girdi, %21,3). Ben bunları "script'e ver" demiştim; **tamamen çıkarmak daha ucuz.** Tahmin tablosundaki mekanik + rapor satırları buna göre ≈ 3,3 M (26 + 28) + script çıktısına iner; toplam hedef ≈ 16,3 M'den ≈ 14–15 M'ye yaklaşır (hipotez).
6. **Mekân kotası:** tarih/mimari ≤ ~%35 (benim "kategori kotası"ndan daha somut).
7. `prompt-ek-blok.txt` hazır — v7 LOKAL prompt'larının sonuna eklenmesi bekliyor (20 kural).

### 10.2 Yeni bulgu: "GPS > 1 km ele" kuralı yanlış kalibre edilmiş

`prompt-ek-blok.txt` kural 16 ve hata listesi C5 "koordinatı mekâna 1 km'den uzak olanları ele / işaretle" diyor. Qwen paketinin 272 fotoğrafı üzerinde ölçtüm (`gps_threshold.py`, mekân koordinatı = Excel'deki koordinat):

| Eşik | GPS'li 123 fotoğraftan elenen |
|---|---|
| > 1 km | 70 (%57) |
| > 2 km | 36 (%29) |
| > 5 km | 4 (%3) |
| > 12 km | 1 (%1) |

Medyan fark 1,2 km. Denetimin onayladığı 19 kötü fotoğraftan yalnız 11'inde GPS var; bunlardan **1 km eşiği yalnız 3'ünü, 12 km eşiği yalnız 1'ini (Seattle şişesi) yakalıyor.** Kötü fotoğrafların 8'i mekânın 0,6–0,8 km yakınında (doğru semt, yanlış nesne) ve 8'inde GPS hiç yok. Yani 1 km kuralı iyi fotoğrafların yarıdan fazlasını (67/123) çöpe atar, yeniden arama turlarına token yaktırır, yakaladığı kötü fotoğraf ise az.

Düzeltme önerisi (iki kademe):
- **Sert ret:** GPS > ~12 km (ya da başka yerleşim). Tek başına nadir ama sıfır yanlış pozitif.
- **İşaret (temas paftasına yönlendir):** 2–12 km.
- **Asıl filtre metin:** şehir/yer adı başlık-açıklama-kategoride, sanat/çizim kelimeleri, yıl < 1995, iç mekân/detay kelimeleri (bu kurallar yakalanabilir 30 bulgunun ≈ 20'sini tek başına yakalıyor).
- **Ön koşul:** mekân koordinatı önce doğrulanmalı (qwen'de 30/93 mekânda koordinat yok, birkaçı aynı koordinatı paylaşıyor) — yoksa GPS kuralı gürültü üretir. Kuralı mekân kimlik planı fazının çıktısına bağla.

### 10.3 Düzeltmeler (iki raporda da)

1. **"Qwen resmî doğrulayıcıyı kullanmadı" demek haksız.** `ekler_eindhoven/` içinde doğrulayıcı paketi yok (9 dosya: prompt'a verilenler) ve v7 prompt'u doğrulamayı açıkça "teknik teslim sorumlusu"na bırakıyor (satır 233, 277, 289). Qwen'in kendi `qa_check.py`'sini yazması süreç boşluğunun sonucu. Çözüm skill/prompt'ta: doğrulayıcı pakete eklenir ve "0 hata yalnız onun çıktısıyla" kuralı yazılır (prompt-ek-blok kural 19 bunu zaten söylüyor).
2. **Barcelona koşuları:** özet "üç koşu var" diyor. Gerçek durum: yalnız `barcelona_qwen37_plus` dolu (514 dosya, 187 MB). `barcelona_chatgpt_sol61_high` ve `barcelona_gemini_argon_medium` boş şablon (yalnız NOTLAR.txt), `RUN_LOG.csv` yalnız başlık satırı. Özetteki 4. adım ("Barcelona koşularını resmî doğrulayıcıyla kıyasla") için ChatGPT/Gemini çıktılarının önce klasörlere konması gerekiyor.
3. **`results\eindhoven_qwen38_max\`** boş şablon kopyası; gerçek qwen çıktısı kökteki `eindhoven_qwen38_max\` (301 MB) ve `_work_eindhoven\` (kardeş klasör, onun içinde değil).
4. **Faz tabanı sabit değil:** `21_neighborhoods` girdisi 432.565 iken `22_routes` 180.820'ye düşüyor (≈ −250 K). Bu bir bağlam sıkıştırması/sıfırlaması gibi görünüyor ve taban 180–240 K aralığında. Çıkarım: faz başına bağlam sıfırlama zaten kısmen oluşuyor; skill'de bunu zorunlu ve erken yaparsak (hedef 30–50 K) taban etkisi kırılır. (Sebep Miami raporunda yazmıyor; çıkarımdır.)
5. Prompt'taki "Araştırma başlangıcı: 2026-10-15" güncel değil; tarih alanı üretim gününe çekilmeli (qwen `checked_on` olarak 2026-10-20 yazmış, yani pratikte sorun çıkmamış).

### 10.4 Sınır

Bu bölümdeki doğrulayıcı sayıları (363/822/323, A1–A15 adetleri) diğer oturumun raporundan alındı; ben yeniden üretmedim. GPS ölçümü (10.2) ve klasör durumları (10.3) benim ölçümüm.

---

## 11. Denetim kılavuzu 2.0 (`SEHIR_DENETIM_CHECKLIST.pdf`, K01–K120) ve skill kararı

**Karar (Umut Barış, 22.10):** iki skill + ortak araç kutusu. `city-pack` üretimde yalnız script kapılarını çalıştırır ve kendini onaylamaz; `city-audit` temiz bağlamda, salt okunur, kademeli (L0/L1/L2) çalışır. İkisi aynı `scripts/` ve `checks.yaml` dosyasını kullanır.

**`checks.yaml`** (bu klasörde, 120 kontrol, PDF metninden script'le çıkarıldı, `build_checks_yaml.py` ile yeniden üretilir). Yürütücü/öncelik/faz atamaları **taslaktır, Atınç onayı gerekir**. Gerçek dağılım:

| Yürütücü | Adet | Üretimde |
|---|---|---|
| S script | 62 | kapı (faz bazlı, LLM'siz) |
| L LLM + kaynak | 30 | kanıt üretilir (iddia defteri vb.), denetim teyit eder |
| V görsel | 7 | temas paftası kanıtı üretilir |
| E ortam (Drive/önizleme/UAT) | 10 | yok, yalnız Atınç aşaması |
| M süreç/rapor | 11 | yok / script'le üretilir |

Öncelik önerisi: P0 28, P1 75, P2 5, süreç kontrolü 12. Faz: assemble 28, photos 28, answers 15, deliver 15, places 11, sources 9, intake 4, yalnız denetim 10. Önceki kaba tahminim (55/33/7/10/15) ile fark: K30, K33, K97, K99 ve K118'i script'e kaydırdım.

Dosya boyutu 20 KB (≈ 6–7 K token, tahmin); PDF metni 94 KB (≈ 30 K token). Tasarruf kısmen "nasıl" metinlerini ve script kontrollerinin geçme koşullarını dışarıda bırakmaktan geliyor; o bilgiler script kodunda yaşayacak.

**Kapsam kararı (Umut Barış, 22.10):**
- **Drive'a yükleme ve bulut doğrulama manuel** (Barış yapar; skill çalıştırmaz, token harcamaz): K01, K03, K109, K110 → `scope: drive-manual`. Skill'de Drive fazı yok; paket yerelde biter.
- **Önizleme dosyalar yüklendikten sonra yapılır, bu skill'lerin işi değil:** K92, K93, K94, K103, K111, K112 → `scope: preview-later`. İleride ayrı bir üçüncü skill (`city-preview`) olabilir. Sonuç: `city-pack` ve `city-audit` yalnız **110 yerel kontrolü** kapsar.
- **Karar kuralı sapması:** Kılavuz, zorunlu kontrol yapılamazsa kararı "karar için kanıt eksik" yapar. Önizleme ve Drive kontrolleri kapsam dışı olduğu için `city-audit` kararı "yerel paket denetimi" diye etiketlenir ve bu 10 kontrolü "ayrı aşama" olarak raporlar; "Atınç'ın son paket incelemesine hazır" demek için bu sapmanın Atınç tarafından kabul edilmesi gerekir.

**Listeyle ilgili açık noktalar (Atınç kararı bekliyor):**
1. **Profil:** K08/K77 "16 sekmeli yerel profil" ile 17. sekme (FotoğrafKaynakları) arasında esneklik tanıyor; üretim sözleşmesi ve resmî doğrulayıcının `--new-content` modu 17. sekmeyi bekliyor. Varsayılan: **17 sekme**; Atınç aksini söylemezse böyle devam.
2. **K36** (Portekiz D7/D8) ülke paketi kuralıdır; genel listede yalnız ulke=PT için çalıştırılır (`only_if`).
4. **Listede olmayan kontroller:** Wikipedia'nın "Resmî" etiketle gösterilmesi; `verified=Evet` yalnız gerçek sayfa görüntüsü varsa; mekân grubu dengesi için sayısal eşik; faz bazlı token ölçümü.
5. **GPS:** K43 "sabit yarıçapı evrensel red kuralı yapma" diyor; bu, 10.2'deki ölçümle uyumlu (1 km kuralı yanlış kalibre).
