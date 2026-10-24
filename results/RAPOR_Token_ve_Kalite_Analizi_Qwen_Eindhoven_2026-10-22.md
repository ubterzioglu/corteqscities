# Şehir üretimi: token harcaması, Qwen hataları ve skill önerisi

Hazırlayan: Claude · 22 Ekim 2026
Kaynaklar: Miami süre/token raporu (20 Ekim), Eindhoven Berlin standardı denetimi (21 Ekim, %55), `eindhoven_qwen38_max` klasörü (Excel, Teslimler, `_work_eindhoven`), v7 prompt ve bu oturumdaki önceki çalışmalar.

## 0. Özet

1. **Eindhoven/Qwen paketi miktarda başarılı, doğrulukta başarısız.** Sayılar Berlin alt sınırını geçiyor (247 yanıt, 93 mekân, 16 mahalle, 272 fotoğraf), ama denetim %55 verdi ve "yayına alınmamalı" dedi. Denetim 18 doğrulanmış bilgi hatası, 14 mekân/rota hatası, onlarca yanlış fotoğraf eşleşmesi ve 10 teslim/şema hatası bulmuş.
2. **Hataların çoğu üç kökten geliyor:** (a) güncel mevzuat ve sayılar eski bilgiyle yazılmış, (b) yer ve fotoğraf eşleşmesi bağımsız kontrol edilmemiş, (c) Qwen kendi yazdığı kontrol betiğine güvenmiş, resmî doğrulayıcıyı hiç çalıştırmamış. Qwen "0 hata, 0 uyarı" yazarken resmî doğrulayıcı draft modunda 365 hata, 822 uyarı verdi.
3. **Token tarafında asıl yük sohbet bağlamının tekrar okunması.** Miami'de 27,2 milyon giriş tokenının %97,1'i önbellekten gelmiş. Gerçek yük 782 bin önbellek dışı giriş ve 130 bin çıkış. Bunların en büyük payı fotoğraf işi (%33,5 önbellek dışı giriş) ve üretim dışı işler (analiz, PDF, panel kontrolü, yerel aktarım: giriş tokenının %21,3'ü).
4. **En büyük kaldıraç iki şey:** ulusal "ortak içerik paketi" (Hollanda'da WW, kira desteği, KVK, devir vergisi hataları aslında ulusal; bir kez doğrulanıp tüm Hollanda şehirlerine yeniden kullanılır) ve fotoğraf işini önce deterministik filtreyle, sonra tek temas paftası üzerinden insan gözüyle yapmak.
5. **Skill için önerim:** aşamalı, her aşamada temiz bağlam ve manifest dosyası kullanan, resmî doğrulayıcıyı zorunlu kapı yapan bir "corteqs-city-pipeline" skill'i. Taslağı Bölüm 6'da.

**Önemli sınır:** Qwen oturumunun token kaydı elimde yok. Token bulguları Miami raporundan (Codex/GPT oturumu) geliyor. Qwen için yalnız klasörden dolaylı işaretler var. Bunları ayrı etiketledim.

---

## 1. Önceki çalışmalardan çıkan kalıp

| Deneme | Sonuç | Ders |
| --- | --- | --- |
| Barcelona/Qwen | Sayılar hedefte (240/120/16/12/60), ama 240 yanıt için yalnız 32 kaynak kaydı vardı | Sayı doluluğu kalite değil; ilk sayımda zaten kaynak açığı görünmüştü |
| Eindhoven/Qwen | Sayılar hedefte, denetim %55 | Aynı kalıp: miktar tamam, doğruluk düşük |
| Miami/Codex | %100 yönetim paneli, 0 tanılama hatası, 64 dk | Codex'in yerel panel okuyucusu ve resmî araçlara erişimi vardı |

Kural: Yönetim ekranındaki yüzde yalnız miktar ölçüyor. Qwen'in "tamam" beyanları bağımsız kontrol olmadan kabul edilmemeli.

---

## 2. Token harcaması (Miami raporu, Codex oturumu)

**Toplam:** 27.158.757 giriş (26.376.704 önbellekten, %97,12), 782.053 önbellek dışı giriş, 130.642 çıkış, 16.541 reasoning. 63 dk 48 sn.

Fatura açısından önemli olan önbellek dışı giriş ve çıkış. Önbellekli giriş çok daha ucuz okunur, ama bağlam büyüdükçe sınır ve gecikme sorunu yaratır.

### Faz grupları (faz tablosundan topladım; toplamlar rapordaki toplamlarla birebir eşleşti)

| Grup | Giriş | Önbellek dışı giriş | Çıkış | Giriş payı | Önbellek dışı payı | Çıkış payı |
| --- | --- | --- | --- | --- | --- | --- |
| Fotoğraf (kimlik planı + görsel denetim + lisans/hash teslimi) | 5.665.416 | 262.024 | 29.670 | %20,9 | **%33,5** | %22,7 |
| Üretim dışı (yerel aktarım, panel kontrolü, istatistik/PDF raporu) | 5.773.579 | 97.419 | 17.273 | %21,3 | %12,5 | %13,2 |
| 12 konu bilgi kartı | 4.130.235 | 106.555 | 40.647 | %15,2 | %13,6 | **%31,1** |
| Atama, önceki standardı okuma, ölçüm altyapısı | 3.071.793 | 106.929 | 5.981 | %11,3 | %13,7 | %4,6 |
| Excel ve teslim paketi üretimi | 2.589.960 | 43.784 | 4.345 | %9,5 | %5,6 | %3,3 |
| Mekân metinleri (23, 23b–e) | 1.616.400 | 43.664 | 14.111 | %6,0 | %5,6 | %10,8 |
| Son kaynak doğrulaması + Drive teslimi | 1.726.164 | 37.716 | 2.998 | %6,4 | %4,8 | %2,3 |

### Gözlemler

1. **Taban maliyet.** Hava durumu fazı yalnız 153 çıkış tokenı üretti ama 231.426 giriş tokenı okudu. Neredeyse her faz en az ~230 bin giriş tokenıyla başlıyor (35 faz × 231 bin ≈ 8,1 milyon, yani toplamın yaklaşık %30'u). Bu, her çağrıda ağır bir sohbet geçmişinin yeniden okunması demek. Miami raporu da aynı sonuca varıyor ("uzun sohbet bağlamını küçült").
2. **Bağlam büyümesi.** 12 konu fazında giriş 240.895'ten 415.942'ye çıkıyor. İçerik yazarken geçmiş tutuluyor, sonraki kartlar daha pahalı.
3. **Fotoğraf en pahalı tek iş.** Görsel denetim fazı tek başına 3,82 milyon giriş, 186 bin önbellek dışı giriş, 21 bin çıkış ve 12 dk 54 sn (%20,2 süre payı). Raporun kendisi nedenini söylüyor: ad benzerliği ve yanlış bina sorunları, 19 mekânın değiştirilmesi, ikinci hedefli aramalar.
4. **İstatistik analizi ve PDF raporu** 4 dk 27 sn, 2,56 milyon giriş ve 11.669 çıkış tokenı harcadı. Çıkış tokenı olarak ikinci büyük kalem. Bu şehir içeriği için gerekli değil.
5. **Yerel aktarım, panel kontrolü ve istatistik raporu** (25, 29, 30. fazlar) toplam girişin %21,3'ünü yedi. Yerel deneme modunda bunlara gerek yok.
6. **Kısa fazlar ucuz.** Hava, takvim ve bütçe alanları toplam 31 saniye ve 697 çıkış tokenı. Şablon temelli alanlar küçük model veya düşük efor ile yapılabilir.

### Qwen için dolaylı işaretler (token kaydı yok)

`_work_eindhoven` içinde 101 dosya var: 24 `urls_core*.json`, 6 Commons tarama dosyası (biri 913 KB), 10 `patch_*` ve düzeltme betiği, `review_fix.py`, `clean_places.py`, `clean_mismatch.py`. Bu, tarama ve yama döngülerinin çok tekrarlandığını gösteriyor. 12 yanıt paketi (`answers_t1..t12`) her biri ~23 KB. Qwen'in ne kadar token harcadığını söyleyemem; bunu ölçmek için bir sonraki denemede token kaydı tutulmalı.

---

## 3. Qwen'in hataları (denetim + klasör incelemem)

Denetim puanı: 18/35 + 11/20 + 14/20 + 9/15 + 3/10 = **55/100**.

### A. Bilgi doğruluğu (kritik)
18 doğrulanmış hata (B01–B18). Örnekler: WW ödeneğinde 26 hafta "5 yılda" diye yazılmış (doğrusu son 36 haftada 26 hafta); 2026 kira desteği eski kuralla anlatılmış; enerji fesih bedeli için evrensel €50 tavanı yazılmış; Türkiye'den hayvan getirme kuralları eksik; kira artış tavanı (2026: %4,4 / %6,1), devir vergisi (%8), KVK kayıt bedeli (€85,15), çocuğun tanınması ve velayet, 16–18 yaş eğitim zorunluluğu eski veya yanlış sadeleştirilmiş.

**Neden olmuş olabilir (çıkarım):** Model, 2025'e ait kuralı veya genel bilgiyi yazıp kaynağı ayrıca "açtım" demiş; kart metni ile kaynak metni sistematik karşılaştırılmamış.

Doğrulanan kanıtlar: `Kaynaklar` sekmesinde **233 kaydın tamamı `verified=Evet`**, hiçbirinde `snapshot_file` yok. Kaynakların **72'si nl.wikipedia.org**, 21 eylem bağlantısı Wikipedia'ya gittiği hâlde "resmî" etiketli. Denetim, bu beyanın doğruluk sertifikası olmadığını söylüyor.

### B. Mekân, mahalle, rota
- 93/120 mekân (27 eksik), %57 tarih/mimari (53/93). Müze 5, sanat 4, sahne 5, spor 6, aile 4, doğa 8, yeme-içme 8.
- Yanlış adresler: Muziekgebouw, Café Wilhelmina, Ton Smits Huis, MU, Hoogenband/Tongelreep, IJssportcentrum, De Splinter. Yanlış anlatılar: W-Hal "Philips fabrika holü", TU/e Auditorium 1950'ler yerine 1966, Collse Watermolen restoran.
- Soru işaretli yer tutucular (`5621?`, `[[Hoogstraat`) okuyucuya çıkabilecek şekilde bırakılmış.
- Rotalardan ikisi 9 duraklı (sözleşme 2–8). Doğruladım: rota durak sayıları 5,5,5,5,5,5,6,6,6,7,**9,9**.
- 123 fotoğrafın GPS'i mekân koordinatıyla 2–5 km uyuşmuyor.

### C. Fotoğraflar
- Zweeloo'daki çiftlik fotoğrafı Eindhoven Türk çarşısı için kullanılmış (yanlış şehir); farklı su kulesi; meydan yerine kilise içi; tablo, gravür ve çizim "güncel fotoğraf" yerine; bira şişesi yakın planı (GPS Seattle); aynı kadrajın siyah-beyaz varyantları; 13 görsel kısa kenarı 600 px altı.
- Qwen'in ilerleme kaydı "görsel spot-check" olarak yalnız yaklaşık 10 kareyi sayıyor; denetim 272 fotoğrafın tamamını temas paftalarıyla taradı. Qwen "272 fotoğraf görsel olarak doğrulandı" demiyor ama `qa_check.py` "0 hata" dedi; bu, yanlış eşleşmeleri yakalamıyordu.

### D. Kanıt zinciri
- 272 korunan indirme kopyası (`Lisans kanıtları/orijinaller/...`) dosya olarak teslimde yok. Teslim özeti paket boyutuna "~0 MB" diyor, gerçek boyut yaklaşık 94,7 MB.
- 272 `author_url` boş. Lisans klasöründeki 816 dosya yalnız JSON.
- Doğruladım: `Kanıtlar.metadata_review_status` 272 satırda "Tamam"; sözleşme `verified` bekliyor.

### E. Şema ve sözleşme
Resmî doğrulayıcı: draft **365 hata, 822 uyarı**, ready 1.915 hata. Qwen teslim notu 0 hata/0 uyarı diyordu. Örnekler: `quick_links` `label/url` yazılmış (sözleşme `label/entry`; klasörde doğruladım); `emergency.tel` biçimi; `arrival_note`, `pharmacy_url`, `emergency_url`, `advice_entry` eksik; mahalle `compare_json` biçimi; tekrar eden kaynak kimlikleri; Türkçe karakterli kimlik; 9 duraklı rotalar.

### F. Öz rapor ve gerçek durum
| Qwen'in yazdığı | Gerçek |
| --- | --- |
| "Doğrulama scripti: 0 hata, 0 uyarı" | Resmî doğrulayıcı: 365 hata, 822 uyarı |
| 233 kaynak "açılıp okundu, verified=Evet" | 81 URL erişim teyidi açık, 1 kesin 404, doğrudan çelişen 18 içerik |
| Paket boyutu ~0 MB | ~94,7 MB |
| 272/272 fotoğraf kanıt zinciri tamam | Korunan indirme dosyaları yok, `author_url` boş |

### Kök nedenler (çıkarım)
1. **Hedef miktar odaklı çalıştı.** Prompt sayıları sert veriyor; doğruluk için ayrı bir kapı yok.
2. **Kendi kontrolünü kendisi yazdı.** Resmî doğrulayıcı ve denetim araçları (`Corteqs_v7_Teknik_Teslim_Araclari.zip`, Drive'da 00 klasöründe) Qwen'e verilmedi. Bunu klasörler arası karşılaştırarak çıkardım: `ekler_eindhoven` içinde yok.
3. **Güncel olgusal iddialar doğrulama sırasına konmadı.** Tarihe duyarlı sayılar (oran, tavan, ücret) için ayrı bir "iddia–kaynak–alıntı" tablosu yok.
4. **Fotoğraf eşleştirme kimlik değil ad benzerliğiyle yapıldı** (Miami'de de aynı sorun yaşanmış).
5. **Tek model hem üretti hem onayladı.**

---

## 4. Öneriler: token azalt, kaliteyi artır

### 4.1 Ortak ulusal içerik paketi (en büyük kazanç)
Denetimin 18 kritik bilgi hatasının büyük kısmı **ülke düzeyinde**: WW, Toeslagen, KVK, devir vergisi, kinderbijslag, kwalificatieplicht, 2026 kira tavanı. Bunlar her Hollanda şehrinde (Eindhoven, Amsterdam, Rotterdam…) aynı. Miami'de 240 kartın 69'u (%29) federal içerikten yeniden kullanılmış.

- Her ülke için bir kez kaynaklı, doğrulanmış "country pack" üret (Hollanda, İspanya, Birleşik Krallık…).
- Şehir üretiminde yalnız yerel farkları (belediye, ulaşım, semt) yaz.
- Kural: yeniden kullanılan kart "sıfır maliyet" sayılmaz, şehre özgü istisna kontrolü yapılır (Miami raporu da böyle yapmış).
- Etki tahmini: yanıt başına token maliyeti ve hata riski düşer. Yüzdeyi ölçmedim; ilk ülke paketinde ölçülmeli.

### 4.2 Fotoğraf hattını tersine çevir
Önce kimlik, sonra filtre, en son görsel:
1. **Mekân kimlik planı:** resmî ad, eski ad, belediye, mekân türü, koordinat (resmî/OSM). Şehir dışı eşleşmeyi baştan engeller (Zweeloo, Bergen/Norveç örnekleri).
2. **Deterministik filtre (betik, modele girmez):** Commons koordinatı mekâna ≤ eşik mesafede mi; kategori mekâna ait mi; başlık/açıklamada `painting`, `drawing`, `map`, `logo`, `engraving`, `plattegrond` gibi kelimeler; kısa kenar ≥ 600 px; dHash ile yakın kopya; lisans listesi.
3. **Aday başına 3 kare, tek temas paftası:** denetimin yaptığı gibi 14–20 kareyi tek görselde incele. Her kareyi ayrı çağrıda okumak yerine paftada işaretlet.
4. **Korunan özgün dosyayı indir ve teslim et** (denetimin T01 bulgusu), `author_url` mümkünse doldur.
5. Arşiv ve tarihli kareleri başlıkta tarihle (1945, 1964, 1992, 1966).

Beklenen etki: Miami'de en pahalı faz bu; yanlış eşleşmelerin sonradan düzeltme turları (Qwen'de `patch_select`, `review_fix`, `clean_mismatch`) azalır.

### 4.3 İddia–kaynak tablosu (olgusal doğruluk)
Hukuk, vergi, destek, sağlık, eğitim, taşınma ve ücret içeren kartlar için ayrı, kısa bir tablo:

`kart_id | iddia | sayı/oran | kaynak_url | kaynak_alıntısı | kontrol_tarihi | yürürlük_yılı`

- Resmî olmayan kaynak (Wikipedia, blog) bu tabloda kabul edilmez; yalnız keşif için kullanılır.
- `verified=Evet` yalnızca bu tablo dolduğunda yazılır; aksi halde boş bırakılır.
- Kaynak özeti kart metniyle ikinci bir geçişte karşılaştırılır (düşük efor, ayrı model).
- Tarihe duyarlı sayılar için yıl alanı zorunlu ("2026'da geçerli").

### 4.4 Mekân doğrulama
- Adres yalnız resmî ziyaret sayfasından alınır; bulunamazsa alan boş bırakılıp kuyruğa yazılır, soru işareti/şablon yazılmaz.
- Aynı yapı tek mekân sayılır (ör. Hoogenband ve Tongelreep aynı kompleks).
- Denge kotası: tarih/mimari ≤ %35; müze, sanat, sahne, spor, aile, doğa, yeme-içme için asgari sayılar. Fotoğraf bulunabilirliği seçimi belirlememeli. Denetimin sorusu bu: seçim fotoğraf bulunabilirliğiyle şekillenmiş.
- GPS uyuşmazlığı (>1 km) otomatik işaretlenir.
- Rota: durak sınırı betikle kontrol edilir; gerçek yürüme/bisiklet süresi harita kaynağından alınır.

### 4.5 Resmî doğrulayıcıyı zorunlu kapı yap
- `Corteqs_v7_Teknik_Teslim_Araclari.zip` dosyasını `ekler` klasörlerine ekle; AI "draft" modunda **0 hata** görmeden teslim edemesin.
- Qwen'in kendi `qa_check.py`'si ek kontrol olarak kalabilir, ama onay yerine geçmez.
- Bu kısım yalnız betikle yapılır; modele sonuçların tamamı değil, yalnız hata sınıfları özeti girer (token tasarrufu).

### 4.6 Bağlamı küçük tut
- Her aşama temiz bağlamda başlasın; aşamalar arası taşınan tek şey kısa `manifest.json` (şehir kimliği, mekân/yanıt kimlikleri, kaynak listesi, sayılar, açık konular).
- Büyük araç çıktısını (913 KB Commons taraması gibi) modele basma; betik filtreleyip ilk N sonucu versin.
- Miami raporunun önerisi aynı: "kısa üretim manifesti, standart sözleşme, filtreli sonuçlar".

### 4.7 Üretim dışı işleri çıkar
Yerel denemede yerel aktarım, panel kontrolü, istatistik/PDF raporu çalıştırma. Miami'de bunlar giriş tokenının %21,3'ü, çıkışın %13,2'si. Tek bir son aşamada, yalnız istenirse çalışsın. Token ve süre kaydı ise betikle (`phase-usage.csv` gibi) tutulup modele okutulmasın.

### 4.8 Efor yönlendirme
| Aşama | Efor |
| --- | --- |
| Hukuk, vergi, destek, sağlık, eğitim iddiaları | Yüksek efor, birincil kaynaktan |
| Mekân/yer doğrulama | Orta |
| Sözlük, adımlar, sayfa alanları, bütçe, hava, takvim | Düşük efor, şablon odaklı |
| Bağımsız denetim | Farklı model, düşük–orta efor |
| Teknik doğrulama ve birleştirme | Betik (model yok) |

### 4.9 Bağımsız denetim aşaması
Üreten modelden farklı bir model, Eindhoven denetiminin kategorilerini (B: bilgi, M: mekân, F: fotoğraf, T: teknik) uygulayan kısa bir denetim yapsın. İlk denemede Eindhoven denetim PDF'i bu aşama için referans alınabilir.

### 4.10 Prompt tarafı
- v7 metnine dokunmadan "lokal mod" bloğuna şunları ekle: "Sayıları doldurmak için doğruluktan ödün verme; eksik kapsamı `ACIK_KONULAR`'a yaz", "`verified=Evet` yalnız iddia tablosunda kayıt varsa", "Wikipedia resmî kaynak sayılmaz", "kapak ve mahalle fotoğrafları tablo/çizim/harita olamaz", "rota 2–8 durak", "`quick_links` biçimi `label/entry`".
- Qwen'in kendi `qa_check.py`'sine "0 hata" yazma izni verilmesin: yalnız resmî doğrulayıcı çıktısını raporlasın.

---

## 5. Önerilen aşamalı akış (E2E)

| # | Aşama | Girdi → Çıktı | Kapı |
| --- | --- | --- | --- |
| 0 | Hazırlık | Excel + Berlin + şema + doğrulayıcı → `manifest.json` | Kimlik doğru |
| 1 | Ülke paketi (yoksa) | Resmî kaynaklar → `country_pack` + iddia tablosu | Yıl/kaynak alanları dolu |
| 2 | Şehir planı | Manifest → konu listesi, mekân ve mahalle kimlikleri, denge kotası | Kota sağlandı |
| 3 | Yerel yanıtlar | Plan + country pack → yanıtlar + iddia satırları | Her yüksek riskli kartın iddia satırı var |
| 4 | Mekân/mahalle/rota | Plan → adres/koordinat/rota | Adres resmî kaynaklı, GPS ≤ eşik |
| 5 | Fotoğraf | Kimlik planı → filtre → temas paftası → indirme | Yanlış tür/GPS filtresi, korunan dosyalar var |
| 6 | Düşük efor alanları | Sözlük, adımlar, SayfaAlanları | Şema formatı |
| 7 | Birleştirme | Parçalar → tek Excel (betik) | Resmî doğrulayıcı draft: 0 hata |
| 8 | Bağımsız denetim | Farklı model → B/M/F/T bulguları | Kritik bulgu 0 |
| 9 | Teslim | Teslim dosyaları, gerçek boyut/envanter | İnsan incelemesi bekliyor (AI onaylamaz) |

---

## 6. Claude skill taslağı: `corteqs-city-pipeline`

**Amaç:** Berlin standardında şehir paketini, daha az token ve daha yüksek doğrulukla, yerel modda üretmek.

**Yapı (öneri):**
- `SKILL.md`: aşamalar, kapılar, "ne zaman hangi alt ajan", model/efor yönlendirme, yasaklar (AI fotoğraf, Wikipedia'yı resmî kaynak sayma, insan onayı alanlarını doldurma).
- `references/`: sözleşme özeti, sayı tablosu (Berlin alt sınırı/hedef), denetim bulgu sınıfları (Eindhoven B/M/T/F), iddia tablosu şeması, lisans listesi.
- `scripts/`: `build_manifest.py`, `commons_candidates.py` (GPS, kategori, anahtar kelime, boyut, dHash filtreli), `contact_sheet.py`, `download_and_hash.py` (özgün dosyayı saklar), `validate_wrapper.py` (resmî doğrulayıcıyı çağırır, özet verir), `claim_table_check.py`, `assemble_excel.py`, `final_report.py` (gerçek boyut, sayı, açık konular).
- `agents/` (alt ajan talimatları): `country-pack`, `city-answers`, `places`, `photos`, `low-effort-fields`, `independent-audit`.

**Tasarım ilkeleri:**
1. Her aşama temiz bağlamla, yalnız `manifest.json` ve kendi girdi dosyalarıyla çalışır.
2. Deterministik işler betikte; model yalnız yargı gereken yerde.
3. Hiçbir aşama kendi çıktısını "doğrulandı" yapmaz; kapı betik veya farklı model tarafından geçilir.
4. Her aşama token ve süre kaydını `phase-usage.csv`'ye yazar (ölçüm, model okumaz).
5. Teslim raporu yalnız betikle ölçülmüş değerleri içerir (boyut, sayı, hata sayısı).

**Bilmediklerim / varsayımlar:**
- Claude'un bu ortamdaki ağ erişiminin Wikimedia Commons ve resmî Hollanda/İspanya sitelerini kapsadığını test etmedim. Alt ajan ve betik tasarımı buna bağlı.
- Resmî doğrulayıcının (`core/content_delivery/delivery_validation.py`) Claude ortamında çalışıp çalışmadığını, zip içeriğini açıp bakmadığım için bilmiyorum.
- Atınç'ın sözleşmesi değişebilir (v8). Skill, sözleşmeyi `references/` içinden okumalı.

---

## 7. Sonraki adımlar

1. `Corteqs_v7_Teknik_Teslim_Araclari.zip` dosyasını Drive'dan indir, `ekler*` klasörlerine ekle; içeriğine bakıp doğrulayıcıyı bu ortamda çalıştırmayı dene.
2. Eindhoven denetiminin B/M/T/F bulgularını bir "hata sınıfı" referansına çevir (skill referansı).
3. Hollanda için ülke paketi pilotu: Eindhoven'daki 18 doğrulanmış hatayı düzelterek başla; paketi ikinci bir Hollanda şehrinde dene ve ölçüm al.
4. Bir sonraki denemede token ve süre kaydı tut (aşama bazlı).
5. Skill'i taslaktan çalışan sürüme çevir; önce yalnız fotoğraf ve doğrulama aşamalarıyla (en büyük kazanç) başla.
