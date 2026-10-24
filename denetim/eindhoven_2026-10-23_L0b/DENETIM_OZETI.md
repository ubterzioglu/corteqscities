Editoryal hazır olma: %7 | Denetim kapsamı: L0, yerel paket denetimi, doğrulanan alt sınır (kısmi denetim); inceleme kapsamı kart 0/424, fotoğraf 0/226, kritik iddia 0/2139; script kapsamı 851/851 dosya, 2199/2199 satır, 401/401 URL | Karar: DÜZELTME GEREKLİ (açık P1: ISS-001, ISS-002, ISS-003; önizleme ve Drive kontrolleri ayrı aşamada)
Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: 0 | Açık P1: 3 (ISS-001, ISS-002, ISS-003) | P2 öneri: 4 (ISS-005, ISS-006, ISS-007, ISS-008)
İncelenen paket: CITY-039 / eindhoven / Excel SHA-256 18b0c295710b6fb4b15b49a409b03f333ace00fa07cb9ab9dd347a83bb9e135b / 2026-10-23 / v001

> **Bu bir yayın onayı değildir.** L0 yalnız script kontrolüdür: LLM iddia denetimi ve görsel inceleme yapılmadı. %7 içerik kalitesi tahmini değil, script ile doğrulanabilen **alt sınırdır** (ham toplam 7,030983/100; puanın tamamı E kategorisinden). Kontrol edilmeyen kısım başarısız sayılmaz, ama puan da almaz. İnsan inceleme alanları (metadata/pixel/rights, reviewer) tasarım gereği "Bekliyor"dur ve değerlendirme dışı bırakıldı.

## 1. Paket, şema ve tarih

- Excel: `CITY-039_eindhoven_v001.xlsx` · 732.389 bayt · değiştirilme 2026-10-23 04:56:51 · SHA-256 `18b0c295710b6fb4b15b49a409b03f333ace00fa07cb9ab9dd347a83bb9e135b`. Önceki denetlenen dosya aynı ad ve sürüm etiketini (v001) taşıyordu ama içeriği farklıydı (SHA `01c130e6…25815`); sürüm SHA ile ayırt edildi.
- Şema: schema_version 1.0; acceptance_version 2026-10-13.1; medya şeması corteqs-media-provenance/7.0; 16 veri sekmesi (eksik 0).
- Paket: 851 dosya, 224,97 MB. Kökte 1 XLSX, Fotoğraflar 226, Lisans kanıtları 396, Teslimler 228 (10 dosya + WebKopyalari 218).
- Sabitleme (K04): başta ve sonda 851 dosya; eklenen, silinen ve değişen 0. SHA listesi özeti iki uçta da `cdf86f6751cdfe9b4ba0d5b28356b14f068f353909fc65455935e3b39aee18c0` (05:06:35 → 05:30:00). Pakete hiçbir şey yazılmadı: validate_all yalnız `--mode audit` ile çalıştı, check_delivery.py ve üretim araçları çalıştırılmadı.
- Denetim tarihi 2026-10-23. Kademe L0, bağımsız denetçi. Üretim notları (DEVIR belgesi, manifest, ACIK_KONULAR yorumları) kanıt sayılmadı. Üretimin teslim günlüğüne yalnız paketin sabit olup olmadığını görmek için bakıldı.

## 2. Berlin minimum – hedef – fiilî matrisi

| Ölçü | Alt sınır | Hedef | Fiilî (ham/tekil) | Önceki L0 (22 Ekim) | Kullanılabilir (editoryal) | Sonuç |
|---|---|---|---|---|---|---|
| Pratik yanıt | 212 | 240 | 289 | 289 | ölçülmedi (L0) | hedef ✓ |
| Gerçek mekân | 92 | 120 | 119 | 104 | ölçülmedi (L0) | hedef ✗ (−1) → ISS-001 |
| Mahalle | 12 | 16 | 16 | 16 | ölçülmedi (L0) | hedef ✓ |
| Dolu konu | 12 | 12 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Tekil mekân fotoğrafı | 187 | 250 | 218 | 201 | ölçülmedi (L0) | hedef ✗ (−32) → ISS-002 |
| Farklı kapak | 6 | 8 | 8 | 8 | ölçülmedi (L0) | hedef ✓ |
| Rota | 9 | 12 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Sözlük | 48 | 60 | 60 | 60 | ölçülmedi (L0) | hedef ✓ |

Fotoğraf kapsamı: fotoğraflı mekân **55/119** (önceki 44/104), fotoğraflı mahalle **14/16** (ISS-003). 226 fotoğraf satırının 218'i tekil mekân karesi, 8'i kapak. Kapaklar mekân kareleriyle aynı dosya: rolleri ayrı, kare bir kez sayıldı.

## 3. Kapsam matrisi

| Alan | Script (L0) | Editoryal / görsel |
|---|---|---|
| Tablo kayıtları | 2199/2199 satır, 16/16 sekme | kart 0/424 |
| Fotoğrafların gerçek baytları | 444/444 görsel dosya (226 JPEG + 218 WebP) çözüldü, SHA eşleşti, web boyutları 226/226 | — |
| Fotoğrafların görsel eşleşmesi | 8 pafta üretildi (30'lu), bakılmadı | 0/226 |
| Kaynak / hak zinciri | Yapısal zincir 226/226 (dosya, hash, lisans etiketi ile URL). Commons kaydında AI işareti 0, izinsiz lisans 0, kısıt 0 | tamamlanan 0/226 (insan hak alanları tasarım gereği "Bekliyor", değerlendirme dışı) |
| Kritik / değişken iddialar | 2139 iddia envanterde; 2116'sı kaynakta dize olarak bulundu (bu doğrulama değildir); 23 "not_in_source", önceki denetimle birebir aynı | resmî kaynakta doğrulanan 0/2139 |
| Kaynak kopyaları (K76) | 397/397 SHA eşleşti; taze kopyayla 394/394 tutarlı (şüpheli 0); 3 kopya karşılaştırılamadı (429) | — |
| Benzersiz URL'ler | 401/401 test edildi: 200 = 360; 3xx→200 = 38; 404/410/soft-404 = 0; diğer = 0; belirsiz (429) = 3 | anlamsal hedef 0/401 |
| Zorunlu sayfa alanları | 23/23 (yapı, tür, referans) | — |
| Önizleme senaryoları | separate_stage | — |
| İnsan paket kararı | Karar yok, bekliyor: Teslimat.reviewer boş, editorial_status her sekmede "Taslak", 678 insan alanı "Bekliyor" (tasarım gereği, değerlendirme dışı). Sürüm v001 | — |

CHECK durumları (120): geçti 47, kısmi 19, kaldı 5, not_checked 38, uygulanmaz 1, separate_stage 10. Ayrıntı `check-results.json` dosyasında, puan tablosu `score.md` dosyasında.

## 4. Önceki L0 denetimiyle karşılaştırma (2026-10-22 → 2026-10-23)

Önceki denetim: `denetim/eindhoven_2026-10-22_L0` (Excel SHA `01c130e6…25815`, 772 dosya). Gerçek dosya farkı `impact.py --diff` ile ölçüldü (önceki Excel'in SHA'sı denetim kaydıyla aynı olan bir kopyası kullanıldı). Toplam 432 değişen, 130 eklenen, 0 silinen kayıt:

- Mekânlar: 15 eklendi, 6 değişti.
- Kaynaklar: 45 eklendi.
- Bağlantılar: 19 eklendi, 2 değişti.
- Fotoğraflar: 17 eklendi.
- Kanıtlar ve FotoğrafKaynakları: 209'ar satır değişti (retrieved_on/downloaded_on ve web_file yolu), 17'şer satır eklendi.
- Yanıtlar 3, Rotalar 2 (005 ve 009), Teslimat 1 kayıt değişti.

Golfbaan Welschap pakette yok: "Golfbaan" geçen hücre 0. "Welschap" yalnız Park Meerland kartında, eski hava üssünün adı olarak geçiyor.

### 4a. Önceki bulguların durumu

| Önceki bulgu | Öncelik · K | Önceki | Şimdi (ölçülen) | Durum | L0b'de açık mı | Kanıt |
|---|---|---|---|---|---|---|
| ISS-001 Mekân hedefi | P1 · K17 | 104/120 (−16) | 119/120 (−1); 15 mekân eklendi, çıkan yok | **sürüyor** | Evet (ISS-001) | validation-audit.json → counts.places; impact.json (Mekânlar added 15) |
| ISS-002 Fotoğraf hedefi | P1 · K17 | 201/250 (−49) | 218/250 (−32); 17 kare eklendi | **sürüyor** | Evet (ISS-002) | counts.photos 218; media.different_files 218 |
| ISS-003 Fotoğrafsız yerler | P1 · K22 | 62 (60 mekân + 2 mahalle) | 66 (64 + 2). Önceki 62'nin hiçbiri kapanmadı; yeni fotoğrafsız 4: Victoriapark, Park Meerland, Brasserie Bellevue, Café Barolo | **sürüyor** | Evet (ISS-003) | warning_classes 64 + 2; `_analiz/onceki-karsilastirma.json` → iss003 |
| ISS-004 web_file '\\' yolu | P1 · K84 | 209/209 '\\' (+JSON/CSV/HTML) | web_file 0/226; provenance JSON 0/452, atıf CSV 0/452, atıf HTML 0/226, normalized-tables 0/850; mutlak/geçici yol 0 | **kapandı** | Hayır | `_foto/hazirlik.json` → ters_egik_cizgi; `_analiz/capraz-kontroller.json` |
| ISS-005 Teslim özeti / ilerleme kaydı | P2 · K83 | TESLIM_OZETI 763 dosya ↔ 772; ILERLEME_KAYDI "fotoğraf 0" | TESLIM_OZETI ölçümle birebir aynı (satır farkı 0). ILERLEME_KAYDI son kaydı "fotoğraf 209 / resmî kaynak 352", aynı kayıt 4 kez tekrarlanmış; paket envanterinde ILERLEME_KAYDI.txt SHA'sı gerçek dosyayla tutmuyor | **değişti** (özet kısmı kapandı) | Evet (ISS-005) | `_analiz/k04-karsilastirma.json`; onceki-karsilastirma.json → iss005 |
| ISS-006 Teslimat tarihi/notu | P2 · K14 | updated_on 2026-10-12; notes şablon ("içerik üretilmedi") | notes doğru; updated_on 2026-10-22, oysa en son içerik tarihi 2026-10-23 | **değişti** (notes kısmı kapandı) | Evet (ISS-006) | `_dump/Teslimat.jsonl`; capraz-kontroller.json → dates |
| ISS-007 Opstal kartı (Yanıtlar!194) | P2 · K104 | "yasal dayanağını göstermiyor" + iç not | Uyarı ve iç not kaldırıldı (hedge 0). Kaynak aynı (yalnız kaynak:097, HEC South); "zorunludur" artık çekincesiz | **değişti** (kısmen kapandı) | Evet, P2 (kapanış L1 teyidine bağlı) | text-quality.json → hedges; impact.json; onceki-karsilastirma.json → iss007 |

Özet: **kapandı 1** (ISS-004), **sürüyor 3** (ISS-001, ISS-002, ISS-003), **değişti 3** (ISS-005, ISS-006, ISS-007). Değişen üç bulgu da düşük öncelikle (P2) açık kalıyor.

### 4b. Yeni bulgular

| Yeni bulgu | Öncelik · K | Yer | Gözlem | Kanıt |
|---|---|---|---|---|
| **ISS-008** İnceleme tarihi kaynaktan eski | P2 · K14 | Mekânlar!22, !44, !59, !75, !76, !83, !113, !116, !118; Rotalar!12 | 10 kayıt 23 Ekim'de kontrol edilen kaynaklara dayanıyor (kaynak:390–405, 407), ama kayıtlarda reviewed_on 2026-10-22 yazıyor. 6 kaydın metninde "23.10.2026" tarihli not var: POM taşınması, Happy Canoe sezonu, iki oyun bahçesi, Next Level Escape Rooms ve rota 005 | `_analiz/onceki-karsilastirma.json` → k14_review_before_source |

Bulgu sayılmayan, ilk kez görülen L1 girdileri:

- 9 yeni kaynak yalnız ana sayfaya gidiyor (yeni mekânların kendi siteleri).
- cafewilhelmina.nl'de 3 adres 429 verdi (erişim teyidi açık).
- Fotoğraf ön elemesi 4 kareyi işaretledi (iki kapak "place_mismatch").
- 23 Ekim'de değişen TAC/POM kartları ve rota 009 içerik olarak sınanmalı.

## 5. Öncelikli bulgular

**P0** (0): yok

**P1** (3)

- **ISS-001 · P1 · K17 · Mekân hedefi** (Mekânlar 8–126, 119 kayıt).
  - Mevcut 119, hedef 120 (asgari 92 karşılandı).
  - Gruplar: Sanat ve sergiler 16, Çocuklarla keşif 16, Sahne ve müzik 16, Spor 16, Yeme ve içme 16, Tarih ve mimari 15, Doğa ve açık hava 13, Müzeler 11.
  - Kanıt: validation-audit.json → structure.counts.places; `_render/TESLIM_OZETI.txt`.
  - Düzeltme: en az 1 gerçek, açık ve kaynaklı mekân ekle (öncelik Müzeler); collection ile şişirme yapma.
  - Yeniden kontrol: counts.places ≥ 120 ve L1'de K39/K42/K108.
- **ISS-002 · P1 · K17 · Fotoğraf hedefi** (Fotoğraflar 8–233).
  - Mevcut 218 tekil mekân karesi, hedef 250 (asgari 187 karşılandı).
  - Kanıt: counts.photos; media.different_files 218; dup_sha 8 (hepsi kapak↔mekân).
  - Düzeltme: en az 32 yeni, tekil ve ücretsiz-ticari lisanslı kare ekle; önce fotoğrafsız kayıtlara.
  - Yeniden kontrol: counts.photos ≥ 250 ve L1 görsel incelemesi.
- **ISS-003 · P1 · K22 · Fotoğraf kapsamı**.
  - Satırlar: Mekânlar!13, 15, 16, 18, 20–26, 28, 30–34, 38, 40, 42–47, 50, 53–55, 57–60, 64, 67–69, 73–87, 89–92, 94, 98, 108, 110, 112, 115, 120, 121; Mahalleler!13, 15.
  - Mevcut: fotoğraflı mekân 55/119, mahalle 14/16. Collection istisnası kullanılmamış (119/119 "Hayır").
  - Kanıt: validation-audit.json warning_classes (64 + 2); `_foto/decisions.json` entries_without_shortlist 66.
  - Düzeltme: her kayda en az bir gerçek, tekil ve lisanslı kare ekle; kare yoksa kaydın kapsamda kalmasına editoryal karar ver.
  - 66 kaydın tam listesi `issues.json` dosyasında.

**P2** (4)

- **ISS-005 · P2 · K83 · İlerleme kaydı / paket manifesti** (Teslimler/ILERLEME_KAYDI.txt; Teslimler/dosya-envanteri.json).
  - ILERLEME_KAYDI 5 kayıt içeriyor, son 4'ü birebir aynı. Son kayıtta "İndirilmiş fotoğraflar: 209" ve "Araştırılan resmî kaynaklar: 352" yazıyor; pakette 226 satır / 218 dosya ve 397 kaynak var.
  - Paket envanteri 851 yolu kapsıyor, ama ILERLEME_KAYDI.txt için yazdığı SHA gerçek dosyayla tutmuyor.
  - Düzeltme: kaydı son durumdan tek kayıtla üret; envanteri tüm özet dosyalarından sonra al.
- **ISS-006 · P2 · K14 · Teslimat.updated_on** (Teslimat!8).
  - updated_on 2026-10-22; en son içerik tarihi 2026-10-23 (Kaynaklar.checked_on 18 satır, Bağlantılar 2 satır). TESLIM_OZETI ise 2026-10-23 diyor.
  - Düzeltme: updated_on = 2026-10-23 (alan Atınç'a aitse ona bildir).
- **ISS-007 · P2 · K104 · Opstal zorunluluğu (Yanıtlar!194)**.
  - Okuyucuya bırakılan doğrulama metni ve iç not kaldırıldı. Kaynak yine yalnız Holland Expat Center South (kaynak:097); "mülk sahipleri için zorunludur" ifadesi artık çekincesiz.
  - Kapanış için L1'de resmî/hukuki kaynakla "supported" gerekir: yasal zorunluluk mu, ipotek/VvE şartı mı?
- **ISS-008 · P2 · K14 · reviewed_on < kaynak checked_on** (10 kayıt; bkz. 4b).
  - Düzeltme: reviewed_on değerlerini gerçek inceleme tarihine çek. Birleştirmeye "reviewed_on ≥ bağlı kaynakların en geç checked_on değeri" script kapısı ekle.

## 6. Yanlış görseller (pafta / slot)

L0'da paftalara bakılmadı; yanlış görsel tespiti yapılmadı (K59–K62 not_checked). Paftalar `temas-sayfalari/sheet_01–08.jpg` (226 kare). Aşağıdakiler yalnız script sinyalidir; karar değil, L1 girdisidir.

**8 kapak = mekân karesi (dHash mesafe 0, aynı bayt).** Kapaklar sheet_08 slot 9–16'da. Eşleri:

| Kapak | Mekân karesi | Pafta / slot |
|---|---|---|
| kapak-01 | 18-septemberplein-02 | sheet_05/3 |
| kapak-02 | klokgebouw-03 | sheet_04/15 |
| kapak-03 | van-abbemuseum-03 | sheet_01/3 |
| kapak-04 | henri-dunantpark-01 | sheet_03/9 |
| kapak-05 | huize-de-laak-01 | sheet_05/10 |
| kapak-06 | philips-stadion-psv-02 | sheet_02/17 |
| kapak-07 | eindhoven-centraal-01 | sheet_05/7 |
| kapak-08 | strijp-s-01 | sheet_04/8 |

**photo_prefilter "flag" (4 kare, "reject" 0):**

| Kare | Satır | Pafta / slot | İşaret |
|---|---|---|---|
| next-nature-museum-01 | Fotoğraflar!16 | sheet_01/13 | detail_interior (Evoluon iç mekânı) |
| dynamo-03 | Fotoğraflar!140 | sheet_02/15 | rights_review: konser, kişiler |
| kapak-05 | Fotoğraflar!230 | sheet_08/13 | place_mismatch |
| kapak-08 | Fotoğraflar!233 | sheet_08/16 | place_mismatch |

Ayrıca Fotoğraflar!60 `de-ontdekfabriek-02` (sheet_03/17) Pixabay kökenli bir CC0 dosyası. K71/K73 kapsamında L1'de bakılmalı.

## 7. İddia düzeltmeleri ve resmî kaynak

L0'da iddia denetimi yapılmadı (K29, K34, K35, K37, K40, K41 not_checked), bu yüzden düzeltme önerisi yok. L1 için script sinyalleri:

**23 "not_in_source".** Liste önceki denetimle birebir aynı; gece değişiklikleri yeni sayısal tutarsızlık getirmedi.

- 13 × "22 Ekim 2026": IND kartlarındaki okuma tarihi notu.
- 4 × "9 hafta": `ebeveyn-izni-ve-evlat-edinme-izni`.
- 4 × DDW bilet fiyatı (84,50 / 104 / 91 euro): `ddw-genc-ogrenci-aile-bileti`.
- 2 × "401 saatte": havalimanı otobüs hattı numarası, yanlış pozitif adayı.

**ISS-007.** Opstal zorunluluğu resmî/hukuki kaynakla sınanmalı.

**23 Ekim'de değişen kartlar.** Önceki sürüme göre 15 mekân eklendi (dosya farkı). 5 mekân kartında ve rota 005'te "23.10.2026" tarihli açık/kapalı notu var. Bu kartlar, TAC/POM adresleri ve rota 009 L1'de K39/K42/K47 örneklemine alınmalı.

**Paketin kendi beyanları.** `Teslimler/ACIK_KONULAR.txt` 6 P1 konu beyan ediyor (ATINC-DOWNLOAD-UTF8, FOTOSUZ-MEKAN, IND-STANDSTILL, IND-TURK-ESIK, SRC-ACCESS, SVB-ERISIM). Bağımsız denetimde kanıt sayılmadı; L1'de sınanmalı. SRC-ACCESS beyanındaki dört alan adının durumu:

- werk.nl, svb.nl, museumkaart.nl Excel'de geçmiyor.
- eindhoven.nl'nin 71 adresi bu denetimde çalışıyor (200 ya da yönlendirme→200).

## 8. Bağlantı ve teknik hatalar (kök nedene göre)

**Kırık bağlantı:** 0/401.

**Erişim teyidi açık (429, bozuk sayılmadı):** www.cafewilhelmina.nl'de 3 adres (yeni mekân Café Wilhelmina). Bir kez yeniden denendi, yine 429 döndü. L1'de ajan açar.

- `/` → Kaynaklar!379
- `/agenda` → Kaynaklar!380, Bağlantılar!335
- `/contact` → Kaynaklar!374, Bağlantılar!336

**Alan adı taşınmış ama çalışıyor (P2 bakım önerisi, önceki denetimle aynı, ayrı ISSUE açılmadı):**

- consuwijzer.nl → consument.acm.nl (4 URL): Bağlantılar!91, !93, !99, !100, !101; Kaynaklar!85, !86, !87, !224.
- arnohuibers.nl → clownarno.nl: Bağlantılar!256, Kaynaklar!284.
- ijssportcentrum.nl/contact/ → ijssportcentrumeindhoven.sportfondsen.nl/: iletişim sayfası yerine ana sayfaya gidiyor (Bağlantılar!260, Kaynaklar!288).

**Yalnız ana sayfaya giden kaynaklar (L1'de K51/K53):**

- Eski: delichttoren.nl (Kaynaklar!354), marienhage.com (!355), hartvaneindhoven.nl (!356); knmi.nl (Şehir!8).
- Yeni (mekânların kendi siteleri): de-vooruitgang.nl/nl/ (!365), wildemaneindhoven.nl (!366), 1910.nl (!367, Bağlantılar!330), cafebarolo.nl (!369, Bağlantılar!332), gaper.nl (!370, Bağlantılar!334), rugbyclubeindhoven.nl (!372), cafewilhelmina.nl (!379), escaperoomeindhoven.nl (!391; Next Level Escape Rooms kartının 23 Ekim'de eklenen kaynağı), speeltuinphilipsdorp.nl (!392).
- defabriekeindhoven.com/en/home → /en: ana sayfadan ana sayfaya, sorun değil.

**Taze kopya kesildi:** effenaar.nl/plan-je-bezoek boyut sınırına takıldı (bilgi).

**Dosya yolu:** '\\' ayırıcısı 0 (ISS-004 kapandı).

**Teslim metaverisi:** İlerleme kaydı ve envanter SHA'sı (ISS-005), Teslimat tarihi (ISS-006), reviewed_on sırası (ISS-008).

## 9. Düzeltme sırası

1. **ISS-003 + ISS-002**: Fotoğrafsız 64 mekân ve 2 mahalleye gerçek, ücretsiz-ticari lisanslı kare ekle (en az 32 yeni tekil kare). Kontrol: "fotoğraf eksik" uyarısı 0, counts.photos ≥ 250.
2. **ISS-001**: 1 gerçek, açık ve fotoğraflı mekân ekle. Kontrol: counts.places ≥ 120.
3. **ISS-008 + ISS-006**: 10 kaydın reviewed_on değerini ve Teslimat.updated_on'u gerçek tarihe çek. Birleştirmeye tarih sırası kapısı ekle.
4. **ISS-007**: Opstal zorunluluğunu resmî kaynakla çöz (L1'de teyit).
5. **ISS-005**: ILERLEME_KAYDI'nı tek ve güncel kayıtla üret; paket envanterini tüm Teslimler yazımlarından sonra al.
6. Yeni sürümle L0'ı yeniden çalıştır (yeni SHA), ardından **L1**: iddia denetçisi ve 8 paftanın tamamının görsel incelemesi; öncelik 6. ve 7. bölümlerdeki girdiler.

L/V kontrolleri yapılmadan karar en iyi durumda "KARAR İÇİN KANIT EKSİK" kalır.

## 10. Çalıştırılmayan / tamamlanamayan kontroller

**not_checked (38)**

- L (LLM + kaynak): K18, K19, K20, K25, K26, K28, K29, K31, K32, K34, K35, K37, K38, K39, K40, K41, K42, K44, K47, K48, K51, K53, K54, K55, K71, K72, K90, K91, K108.
- V (görsel): K59, K60, K61, K62, K65, K74, K105.
- Script yok: K73, K81.

**separate_stage (10)**

- Drive: K01, K03, K109, K110.
- Önizleme: K92, K93, K94, K103, K111, K112.

**kısmi (19):** K07, K24, K30, K33, K43, K50, K64, K66, K67, K75, K76, K78, K79, K89, K104, K106, K107, K118, K120. Her birinin eksik kısmı kendi sınır_gerekçe alanında. K64, K67 ve K107 bu kez aday verisiyle ölçüldü: 226 aday; AI işareti, izinsiz lisans ve kısıt 0. Önceki denetimde aday 0 olduğu için ölçülememişti.

**uygulanmaz (1):** K36 (D7/D8 yalnız Portekiz için).

**Karara etkisi:** A–D kategorilerinin tamamı ölçülmedi ("kontrol edilemedi" ya da "kısmi"); yüzde yalnız E kategorisinden geliyor. Script'in kesin gösterdiği 3 P1 nedeniyle karar DÜZELTME GEREKLİ. Bunlar kapansa bile L0'da karar en iyi durumda KANIT EKSİK olur.

## 11. Denetim çıktıları

Ana kayıtlar:

- `check-results.json` (120 CHECK)
- `issues.json` (7 açık ISSUE)
- `onceki-bulgu-durumu.json` (K99)
- `criteria.json`, `score.json` / `score.md`

Script çıktıları:

- `impact.json`
- `url-checks.json` (Kaynaklar, Bağlantılar, Şehir, SayfaAlanları; ilk koşu `_log/url-checks-kosu1.json`)
- `dosya-envanteri.json` / `_dosya-envanteri-son.json`
- `validation-audit.json`, `text-quality.json`, `xlsx-fidelity.json`
- `claims.jsonl` / `claim-script.json`
- `kanitlar/snap/` (394 taze kopya)

Klasörler:

- `_dump/`
- `_foto/`: candidates 226, plan, decisions, items, hazirlik, dhash-ciftleri
- `temas-sayfalari/` (8 pafta, dhash.json)
- `_render/` (bağımsız teslim özeti)
- `_analiz/`: capraz-kontroller, onceki-karsilastirma, snapshot-karsilastirma, k04-karsilastirma, betikler
- `_onceki/` (önceki Excel'in SHA ile doğrulanmış kopyası)
- `_cache/`

Notlar (SKILL'e ek):

- **Kullanılan girdiler:** xlsx_fidelity için girdi şablonu görevde verilmedi. Önceki denetimle karşılaştırılabilir olsun diye aynı şablon kullanıldı (`ekler_eindhoven/CITY-039_eindhoven_v001.xlsx`, salt okunur). Önceki Excel'in kopyası oturum çalışma alanından SHA eşleşmesiyle alındı.
- **Yeniden denemeler:** url_check ve fetch_snapshot `--retry-transient` ile ikişer kez çalıştı; 429'lar kaldı.
- **KAPSAM "Kismi" varsayılanından sapmalar:**
  - "geçti" (eksik kısım bu denetimde tamamlandı): K04 (baş/son SHA), K05 (çoklu Excel ve artık), K16 (EkDetaylar 0 satır).
  - KAPSAM'da "tam" olup burada "kısmi" kalanlar: K50 (3 adres 429 nedeniyle teyit edilemedi), K118 (impact.py çalıştı, önerdiği L/V kontrolleri L1'de).
  - K82 (KAPSAM kısmi) bulgu nedeniyle "kaldı" (ISS-005).
