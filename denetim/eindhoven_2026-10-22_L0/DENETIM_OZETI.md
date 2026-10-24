Editoryal hazır olma: %6 | Denetim kapsamı: L0, yerel paket denetimi, doğrulanan alt sınır (kısmi denetim); editoryal/görsel inceleme kart 0/409, fotoğraf 0/209, kritik iddia 0/2139; script kapsamı 772/772 dosya, 2069/2069 satır, 358/358 URL | Karar: DÜZELTME GEREKLİ (açık P1: ISS-001, ISS-002, ISS-003, ISS-004; önizleme ve Drive kontrolleri ayrı aşamada)
Teknik/panel ilerlemesi: ölçülmedi (panel/UAT erişimi yok; bu yerel paket denetimidir) | Açık P0: 0 | Açık P1: 4 (ISS-001, ISS-002, ISS-003, ISS-004) | P2 öneri: 3 (ISS-005, ISS-006, ISS-007)
İncelenen paket: CITY-039 / eindhoven / Excel SHA-256 01c130e64d683ba05cee94275aa52056f4eba1b1867d4408ab27df04dec25815 / 2026-10-22 / v001

> **Bu bir yayın onayı değildir.** L0 yalnız script kontrolüdür: LLM iddia denetimi ve görsel inceleme yapılmadı. %6 içerik kalitesi tahmini değil, script ile doğrulanabilen **alt sınırdır** (ham toplam 6.345941/100; puanın tamamı E kategorisinden). Kontrol edilmeyen kısım başarısız sayılmaz, ama puan da almaz.

## 1. Paket, şema ve tarih
- Excel: `CITY-039_eindhoven_v001.xlsx` · 704.057 bayt · değiştirilme 2026-10-22 22:38:07 · SHA-256 `01c130e64d683ba05cee94275aa52056f4eba1b1867d4408ab27df04dec25815`
- Şema: schema_version 1.0; acceptance_version 2026-10-13.1; medya şeması corteqs-media-provenance/7.0; 16 veri sekmesi (eksik 0).
- Paket: 772 dosya, 204.04 MB — kök 1 XLSX; Fotoğraflar 209; Lisans kanıtları 351; Teslimler 211.
- Sabitleme (K04): başta ve sonda 772 dosya; eklenen/silinen/değişen 0; SHA listesi özeti `1220f0912a742833b046ed3fe27dc0d59cb0276345461bdd8ceec08504e33752` her iki uçta aynı. Pakete hiçbir şey yazılmadı (validate_all yalnız `--mode audit`; check_delivery.py çalıştırılmadı).
- Denetim tarihi 2026-10-22; kademe L0; bağımsız denetçi; üretim notları (manifest, ACIK_KONULAR yorumları) kanıt sayılmadı.

## 2. Berlin minimum – hedef – fiilî matrisi

| Ölçü | Alt sınır | Hedef | Fiilî (ham/tekil) | Kullanılabilir (editoryal) | Sonuç |
|---|---|---|---|---|---|
| Pratik yanıt | 212 | 240 | 289 | ölçülmedi (L0) | hedef ✓ |
| Gerçek mekân | 92 | 120 | 104 | ölçülmedi (L0) | hedef ✗ (-16) → ISS-001 |
| Mahalle | 12 | 16 | 16 | ölçülmedi (L0) | hedef ✓ |
| Dolu konu | 12 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Tekil mekân fotoğrafı | 187 | 250 | 201 | ölçülmedi (L0) | hedef ✗ (-49) → ISS-002 |
| Farklı kapak | 6 | 8 | 8 | ölçülmedi (L0) | hedef ✓ |
| Rota | 9 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Sözlük | 48 | 60 | 60 | ölçülmedi (L0) | hedef ✓ |

Fotoğraf kapsamı: fotoğraflı mekân **44/104**, fotoğraflı mahalle **14/16** (ISS-003). Fotoğraf satırı 209 = 201 tekil mekân karesi + 8 kapak (kapaklar mekân kareleriyle aynı dosya; rol ayrı, kare tek sayıldı).

## 3. Kapsam matrisi

| Alan | Script (L0) | Editoryal / görsel |
|---|---|---|
| Tablo kayıtları | 2069/2069 satır, 16/16 sekme | kart 0/409 |
| Fotoğrafların gerçek baytları | 410/410 görsel dosya (209 JPEG + 201 WebP) çözüldü, SHA eşleşti | — |
| Fotoğrafların görsel eşleşmesi | paftalar üretildi (7 pafta, 30'lu), bakılmadı | 0/209 |
| Kaynak / hak zinciri | yapısal zincir 209/209 (dosya, hash, lisans etiketi-URL) | tamamlanan 0/209 (rights_status 209 'Bekliyor') |
| Kritik / değişken iddialar | 2139 envanter; 2116 dize eşleşmesi (doğrulama değil) | resmî kaynakta doğrulanan 0/2139 |
| Benzersiz URL'ler | 358/358 test edildi: 200 = 322; 3xx→200 = 36; 404/410/soft-404 = 0; diğer = 0; belirsiz = 0 | anlamsal hedef 0/358 |
| Zorunlu sayfa alanları | 23/23 (yapı, tür, referans) | — |
| Önizleme senaryoları | separate_stage | — |
| İnsan paket kararı | yok, bekliyor (Teslimat.reviewer boş; editorial_status 'Taslak'; 627 insan alanı 'Bekliyor'); sürüm v001 | — |

CHECK durumları (120): geçti 45, kısmi 13, kaldı 8, not_checked 41, uygulanmaz 3, separate_stage 10. Ayrıntı: `check-results.json`; puan tablosu: `score.md`.

## 4. Öncelikli bulgular

**P0** (0): yok

**P1** (4)

- **ISS-001 · P1 · K17 · Berlin kapsamı / mekân hedefi** — Mekânlar (satır: 8–111 (104 kayıt)); alan `kayıt sayısı (places)`. Mevcut: 104 Beklenen: hedef 120 (asgari 92 karşılandı) Kanıt: validation-audit.json → structure.counts.places / structure.target.places; _render/TESLIM_OZETI.txt (bağımsız yeniden hesap). Düzeltme: En az 16 gerçek, kaynaklı, şehir kapsamındaki mekân ekle; az dolu gruplara (Doğa ve açık hava 9, Müzeler 10, Yeme ve içme 10) öncelik ver; alt nesne/collection ile şişirme yapma (K108). Yeniden kontrol: validate_all structure.counts.places ≥ 120 ve yeni kayıtlar L1'de K42/K108 ile doğrulanmış.
- **ISS-002 · P1 · K17 · Berlin kapsamı / fotoğraf hedefi** — Fotoğraflar (satır: 8–216 (209 satır)); alan `tekil mekân karesi sayısı (photos)`. Mevcut: 201 Beklenen: hedef 250 (asgari 187 karşılandı) Kanıt: validation-audit.json → structure.counts.photos, media.different_files; dosya-envanteri.json findings.dup_sha (8); temas-sayfalari/dhash.json (8 çift, mesafe 0). Düzeltme: En az 49 yeni, tekil, gerçek ve ücretsiz-ticari lisanslı kare ekle; önce fotoğrafsız 60 mekân + 2 mahalleyi kapat. Yeniden kontrol: validate_all structure.counts.photos ≥ 250 (SHA/kaynak tekil) ve yeni kareler L1 görsel incelemesinden geçmiş.
- **ISS-003 · P1 · K22 · Fotoğraf kapsamı** — Mekânlar; Mahalleler (satır: Mekânlar!13,15,16,18,20,21,22,23,24,25,26,28,30,31,32,33,34,38,40,42,43,44,45,46,47,50,53,54,55,57,58,59,60,64,67,68,…); alan `Fotoğraflar.entry_id ilişkisi`. Mevcut: fotoğraflı mekân 44/104; fotoğraflı mahalle 14/16 Beklenen: Her fiziksel mekân ve mahalle en az bir doğru, gerçek fotoğrafla kapsanır (collection istisnası kullanılmamış: 104/104 'Hayır'). Kanıt: validation-audit.json → warning_classes ('Mekân / mahalleye bağlı gerçek fotoğraf eksik' 60 + 2); _analiz/capraz-kontroller.json → places_without_photo, districts_without_photo; _render/ACIK_KONULAR.txt. Düzeltme: Her kayda en az bir gerçek, tekil, ücretsiz-ticari lisanslı kare ekle; uygun kare yoksa kaydın kapsamda kalmasına editoryal karar ver (collection etiketiyle kaçma). Yeniden kontrol: validate_all uyarı sınıfı 'gerçek fotoğraf eksik' = 0; yeni kareler L1 görsel (K59–K61) ve hak (K67–K74) incelemesinden geçmiş.
- **ISS-004 · P1 · K84 · Teslim taşınabilirliği / dosya yolu** — FotoğrafKaynakları (+ Teslimler/photo-provenance-v7.json, Teslimler/fotograf-atiflari-v7.csv) (satır: 8–216 (209/209)); alan `web_file`. Mevcut: Teslimler\WebKopyalari\7c80a77a90fe71284b3cf5e9698bcae03d8b1c3a0c853dc1ffc02bf2ff701957.webp Beklenen: Teslimler/WebKopyalari/<sha>.webp ('/' ayırıcı; sözleşme özeti ve paketteki diğer tüm yol alanları gibi) Kanıt: _dump/FotoğrafKaynakları.jsonl (web_file); _analiz/capraz-kontroller.json → backslash_paths; araclar/arac/core/content_delivery/validation_context.py safe_file() Path(value) kullanır → Linux/macOS'ta 'Dosya bulunamadı' (kod okumasından çıkarım; Linux'ta fiilen çalıştırılmadı); photo-provenance-v7.json 209 ve CSV 209 '\' yol. Düzeltme: web_file değerlerini '/' ayırıcıya çevir; photo-provenance-v7.json ve fotograf-atiflari-v7.csv'yi aynı araçla yeniden üret. Yeniden kontrol: Paketteki tüm yol alanlarında '\' sayısı 0; validate_all --new-content POSIX ortamında medya hatası 0.

**P2** (3)

- **ISS-005 · P2 · K83 · Teslim özeti / ilerleme kaydı** — — (satır: —); alan `Paket boyutu satırı; son ilerleme kaydı`. Mevcut: TESLIM_OZETI: 'Paket: 763 dosya, 199.68 MB (ölçülen)'; ILERLEME_KAYDI son kayıt: 'Faz: photos … İndirilmiş fotoğraflar: 0 … Sonraki somut adım: commons_search -> … -> indirme' Beklenen: Özet teslim edilen paketi tarif eder: 772 dosya, 204.04 MB (ya da 'Teslimler çıktıları hariç' notu); son kayıt 209 satır / 201 dosyanın indirildiğini gösterir. Kanıt: dosya-envanteri.json (denetim) ↔ Teslimler/dosya-envanteri.json; _render/TESLIM_OZETI.txt. Düzeltme: TESLIM_OZETI ve ILERLEME_KAYDI'nı son paket durumundan yeniden üret veya sayım kapsamını açıkça yaz. Yeniden kontrol: TESLIM_OZETI dosya/MB değeri denetim envanteriyle eşleşir; ILERLEME_KAYDI son kaydı teslim durumunu gösterir.
- **ISS-006 · P2 · K14 · Teslim kaydı / tarih** — Teslimat (satır: 8); alan `updated_on; notes`. Mevcut: updated_on 2026-10-12; notes 'Çalışma dosyası; içerik üretilmedi; UAT durumu: Üretilecek. Katalog tarihleri kaynak kaydını gösterir; rehber doğrulaması değildir.' Beklenen: updated_on son güncellemeyi gösterir (içerik reviewed_on/checked_on 2026-10-22); notes teslim edilen içeriği doğru tarif eder. Kanıt: _dump/Teslimat.jsonl; şablon dökümü (xlsx_dump, ekler_eindhoven/CITY-039_eindhoven_v001.xlsx Teslimat). Düzeltme: updated_on ve notes'u güncelle; alan Atınç'a aitse ona bildir (reviewer boş kalmalı). Yeniden kontrol: Teslimat.updated_on ≥ son içerik tarihi ve notes içerik durumunu doğru yansıtıyor.
- **ISS-007 · P2 · K104 · Metin kalitesi / okuyucuya bırakılan doğrulama** — Yanıtlar (satır: 194); alan `summary; note`. Mevcut: summary: '… opstalverzekering … mülk sahipleri için zorunludur; sayfa bu kuralın yasal dayanağını göstermiyor.' note: 'Opstal zorunluluğu yalnız Holland Expat Center South sayfasında geçiyor; yasal dayanağı resmî bir … Beklenen: Kural resmî kaynakla doğrulanıp yazılır veya kesin olmayan kural kesin gibi sunulmaz; iç editoryal doğrulama notu kullanıcı metninde yer almaz (K104). Kanıt: text-quality.json → hedges.items, evasive_answers.items; _dump/Yanıtlar.jsonl satır 194. Düzeltme: Opstal zorunluluğunu resmî/hukuki kaynakla doğrula (yasal zorunluluk mu, ipotek şartı mı) ve metni buna göre yeniden yaz; iç notu kaldır. Yeniden kontrol: text_quality hedge bu kartta 0 ve L1 iddia denetiminde (K29/K35/K41) iddia 'supported'.

ISS-003'ün 62 kaydının tam listesi (entry_id ve satır) `issues.json` içindedir.

## 5. Yanlış görseller (pafta / slot)

L0'da paftalara bakılmadı; yanlış görsel tespiti yapılmadı (K59–K62 not_checked). Paftalar: `temas-sayfalari/sheet_01–07.jpg`. Yalnız script sinyalleri (karar değil, L1 için):
- 8 kapak = mekân karesiyle aynı dosya (dHash mesafe 0): kapak-01…08 → sheet_07 slot 22–29; eşleri: 18-septemberplein-02 (sheet_05/3), klokgebouw-03 (sheet_04/15), van-abbemuseum-03 (sheet_01/3), henri-dunantpark-01 (sheet_03/9), huize-de-laak-01 (sheet_05/10), philips-stadion-psv-02 (sheet_02/17), eindhoven-centraal-01 (sheet_05/7), strijp-s-01 (sheet_04/8).
- Fotoğraflar!60 `de-ontdekfabriek-02` (sheet_03/17): kaynak dosya adı 'Netherlands_Office_Philips_Eindhoven_Building.jpg', Pixabay kökenli CC0 — hedef yer ve köken L1'de bakılmalı.

## 6. İddia düzeltmeleri ve resmî kaynak

L0'da iddia denetimi yapılmadı (K29, K34, K35, K37, K40, K41 not_checked); düzeltme önerisi yok. L1 girdisi olarak script sinyalleri (23 'not_in_source'):
- 13 × '22 Ekim 2026' — IND ücret kartlarının cost alanındaki okuma tarihi notu (kaynakta beklenmez; içerik iddiası değil).
- 4 × '9 hafta' — `ebeveyn-izni-ve-evlat-edinme-izni` (summary/steps/timing/cost); kaynakta rakamla bulunamadı.
- 4 × DDW bilet fiyatı (84,50 / 104 / 91 euro) — `ddw-genc-ogrenci-aile-bileti`; kaynak snapshot'ında yok.
- 2 × '401 saatte' — `eindhoven-havalimani-toplu-tasima`; büyük olasılıkla otobüs hattı numarası ayrıştırması (yanlış pozitif adayı).
- Paketin `ACIK_KONULAR.txt` dosyası 4 açık P1 beyan ediyor (IND/SVB kaynak erişimi ve yorum); bağımsız denetimde kanıt sayılmadı, L1'de sınanmalı.

## 7. Bağlantı ve teknik hatalar (kök nedene göre)

- Kırık bağlantı: 0/358.
- Geçici ağ hatası (1): rotterdam-bk.mfa.gov.tr/Mission/ShowInfoNote/417062 TLS el sıkışma zaman aşımı (Bağlantılar!492, Kaynaklar!62); yeniden denemede 200.
- Alan adı taşınmış, çalışıyor (P2 bakım önerisi): consuwijzer.nl → consument.acm.nl (4 URL; Bağlantılar!91, !93, !99, !100, !101; Kaynaklar!85, !86, !87, !224); arnohuibers.nl → clownarno.nl (Bağlantılar!256, Kaynaklar!284); ijssportcentrum.nl/contact/ → ijssportcentrumeindhoven.sportfondsen.nl/ — iletişim sayfası yerine anasayfa (Bağlantılar!260, Kaynaklar!288).
- Yalnız anasayfa kaynak (L1'de K51/K53): delichttoren.nl (Kaynaklar!354), marienhage.com (!355), hartvaneindhoven.nl (!356); knmi.nl sağlayıcı (Şehir!8). defabriekeindhoven.com/en/home → /en (anasayfadan anasayfaya, sorun değil).
- Dosya yolu: web_file Windows '\' ayırıcısı — tek kök neden, 209 Excel satırı + photo-provenance-v7.json + atıf CSV (ISS-004).
- Teslim metaverisi: Teslimat satırı şablondan (ISS-006), teslim özeti/ilerleme kaydı son paketten önce üretilmiş (ISS-005).

## 8. Düzeltme sırası

1. **ISS-004** — web_file yollarını '/' ile yaz; photo-provenance-v7.json ve atıf CSV'sini yeniden üret. Kontrol: '\' = 0, POSIX'te validate_all medya hatası 0.
2. **ISS-003 + ISS-002** — fotoğrafsız 60 mekân + 2 mahalleye gerçek, ücretsiz-ticari lisanslı kare ekle (49 karelik açığı da kapatır). Kontrol: 'fotoğraf eksik' uyarısı 0; counts.photos ≥ 250.
3. **ISS-001** — az dolu gruplara 16+ gerçek mekân ekle (yeni mekânlara fotoğrafla). Kontrol: counts.places ≥ 120.
4. **ISS-007** — Yanıtlar!194 opstal zorunluluğunu resmî kaynakla çöz, iç notu kaldır.
5. **ISS-006, ISS-005** — Teslimat satırını ve teslim özetlerini son paket durumundan yeniden üret.
6. Yeni sürümle L0'ı yeniden çalıştır (yeni SHA), ardından **L1** (iddia denetçisi + tüm paftaların görsel incelemesi). L/V kontrolleri yapılmadan karar en iyi durumda 'KARAR İÇİN KANIT EKSİK' kalır.

## 9. Çalıştırılmayan / tamamlanamayan kontroller

- **not_checked (41)** — L (LLM+kaynak): K18, K19, K20, K25, K26, K28, K29, K31, K32, K34, K35, K37, K38, K39, K40, K41, K42, K44, K47, K48, K51, K53, K54, K55, K71, K72, K90, K91, K108; V (görsel): K59, K60, K61, K62, K65, K74, K105; script verisi yok: K64, K67, K107 (photo_candidates from-evidence 0 aday — paket `Lisans kanıtları/*.source-evidence.json` içermiyor, kanıt Excel Kanıtlar sekmesinde); script yok: K73, K81.
- **separate_stage (10)** — Drive: K01, K03, K109, K110; önizleme: K92, K93, K94, K103, K111, K112.
- **kısmi (13)** — K07, K24, K30, K33, K43, K66, K75, K76, K78, K79, K89, K106, K120 (eksik kısım her kaydın sınır_gerekçe alanında).
- **uygulanmaz (3)** — K36 (D7/D8 yalnız Portekiz), K99 ve K118 (önceki denetim yok).
- Karara etkisi: A–D kategorilerinin tamamı ölçülmedi (0 puan, 'kontrol edilemedi'/'kısmi'); yüzde yalnız E kategorisinden. Script'in kesin gösterdiği 4 P1 nedeniyle karar DÜZELTME GEREKLİ; bunlar kapansa bile L0'da karar en iyi durumda KANIT EKSİK olur.

## 10. Denetim çıktıları

`check-results.json` · `issues.json` · `criteria.json` · `score.json` / `score.md` · `url-checks.json` (Kaynaklar+Bağlantılar) · `url-checks-sehir-sayfa.json` (Şehir+SayfaAlanları) · `dosya-envanteri.json` / `_dosya-envanteri-son.json` · `validation-audit.json` · `text-quality.json` · `xlsx-fidelity.json` · `claims.jsonl` / `claim-script.json` · `kanitlar/snap/` (352 taze snapshot) · `_dump/` · `_foto/` (candidates 0, plan, decisions, items) · `temas-sayfalari/` (7 pafta, dhash.json) · `_render/` (bağımsız teslim özeti yeniden hesabı) · `_analiz/` (çapraz kontroller, K04, snapshot karşılaştırması, betikler) · `_cache/`.

Not (SKILL'e ek, paket dışı): url_check `--retry-transient` ile iki kez çalıştı (ikinci geçiş geçici hatayı yeniden denedi); Şehir+SayfaAlanları için ayrı url_check; KAPSAM eşlemesi için xlsx_fidelity (girdi şablonu ekler_eindhoven/CITY-039_eindhoven_v001.xlsx) ve render_summary (`_render/`); kaynak snapshot'larının taze indirmeyle karşılaştırması `_analiz/` altında. KAPSAM 'Kismi' varsayılanından sapmalar: K04, K05, K16 'geçti' (eksik kısım bu denetimde tamamlandı: K04 baş/son SHA karşılaştırması, K05 çoklu Excel kontrolü envanterden, K16 EkDetaylar 0 satır); K82 'kaldı' (bulgu var); K64, K67, K107 'not_checked' (aday verisi yok).
