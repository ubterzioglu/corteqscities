Editoryal hazır olma: %7 | Denetim kapsamı: L0, yerel paket denetimi, doğrulanan alt sınır (kısmi denetim); inceleme kapsamı kart 0/354, fotoğraf 0/258, kritik iddia 0/1880; script kapsamı 1450/1450 dosya, 2187/2187 satır, 420/420 URL | Karar: DÜZELTME GEREKLİ (açık P1: ISS-001, ISS-002, ISS-003, ISS-004; önizleme ve Drive kontrolleri ayrı aşamada)
Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: 0 | Açık P1: 4 (ISS-001, ISS-002, ISS-003, ISS-004) | P2 öneri: 4 (ISS-005, ISS-006, ISS-007, ISS-008)
İncelenen paket: CITY-107 / sevilla / Excel SHA-256 8c8b454ba24832e9a7c8566a9126f021010b13502bfd1f65ddf23daac9af34ba / 2026-10-25 / v001

> **Bu bir yayın onayı değildir.** L0 yalnız script kontrolüdür: LLM iddia denetimi ve görsel inceleme yapılmadı. %7 içerik kalitesi tahmini değil, script ile doğrulanabilen **alt sınırdır** (ham toplam 7,433333/100; puanın tamamı E kategorisinden). Kontrol edilmeyen kısım başarısız sayılmaz, ama puan da almaz. İnsan inceleme alanları (metadata/pixel/rights, reviewer) tasarım gereği "Bekliyor"dur ve değerlendirme dışı bırakıldı.

## 1. Paket, şema ve tarih

- Excel: `CITY-107_sevilla_v001.xlsx` · 781.986 bayt · SHA-256 `8c8b454ba24832e9a7c8566a9126f021010b13502bfd1f65ddf23daac9af34ba`. Bu şehrin ilk denetimi; önceki denetim ve önceki Excel yok.
- Şema: schema_version 1.0; acceptance_version 2026-10-13.1; medya şeması corteqs-media-provenance/7.0; 16 veri sekmesi (eksik 0), 2187 satır. Girdi şablonuyla yapı farkı 0 (xlsx_fidelity; şablon `uretim/sevilla/_is/sablon_orijinal_kopya.xlsx`, salt okunur).
- Paket: 1450 dosya, 285,62 MB. Kökte 1 XLSX, Fotoğraflar 258 (JPEG), Lisans kanıtları 931, Teslimler 260 (10 dosya + WebKopyalari 250 WebP).
- Sabitleme (K04): başta ve sonda 1450 dosya; eklenen, silinen ve değişen 0. SHA listesi özeti iki uçta da `7c2ad63a057f5d60…`. Pakete hiçbir şey yazılmadı: validate_all yalnız `--mode audit`, check_delivery.py ve üretim araçları çalıştırılmadı.
- Denetim tarihi 2026-10-25. Kademe L0, bağımsız denetçi, temiz oturum. Üretim notları (manifest, `Teslimler/ACIK_KONULAR.txt` yorumları, RUN_LOG) kanıt sayılmadı; ACIK_KONULAR yalnız sayısal tutarlılık için okundu.

## 2. Berlin minimum – hedef – fiilî matrisi

| Ölçü | Alt sınır | Hedef | Fiilî (ham/tekil) | Kullanılabilir (editoryal) | Sonuç |
|---|---|---|---|---|---|
| Pratik yanıt | 212 | 240 | 239 | ölçülmedi (L0) | hedef ✗ (−1) → ISS-001 |
| Gerçek mekân | 92 | 120 | 100 | ölçülmedi (L0) | hedef ✗ (−20) → ISS-002 |
| Mahalle | 12 | 16 | 15 | ölçülmedi (L0) | hedef ✗ (−1) → ISS-003 |
| Dolu konu | 12 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Tekil mekân fotoğrafı | 187 | 250 | 250 | ölçülmedi (L0) | hedef ✓ |
| Farklı kapak | 6 | 8 | 8 | ölçülmedi (L0) | hedef ✓ |
| Rota | 9 | 12 | 12 | ölçülmedi (L0) | hedef ✓ |
| Sözlük | 48 | 60 | 60 | ölçülmedi (L0) | hedef ✓ |

Fotoğraf kapsamı: fotoğraflı mekân **81/100**, fotoğraflı mahalle **10/15** (ISS-004). 258 fotoğraf satırının 250'si tekil mekân karesi, 8'i kapak. Kapaklar mekân kareleriyle aynı dosya: rolleri ayrı, kare bir kez sayıldı. Mekân başına kare: 3 kare 74, 2 kare 11, 1 kare 6.

Grup dağılımı (100 mekân): Tarih ve mimari 32, Doğa ve açık hava 14, Müzeler 12, Sahne ve müzik 12, Sanat ve sergiler 10, Yeme ve içme 8, Çocuklarla keşif 7, Spor 5. Tarih payı %32 (eşik %35'in altında). 13 mekân collection=Evet (ISS-007).

## 3. Kapsam matrisi

| Alan | Script (L0) | Editoryal / görsel |
|---|---|---|
| Tablo kayıtları | 2187/2187 satır, 16/16 sekme | kart 0/354 |
| Fotoğrafların gerçek baytları | 508/508 görsel dosya (258 JPEG + 250 WebP) çözüldü, SHA eşleşti, web boyutları 258/258 | — |
| Fotoğrafların görsel eşleşmesi | 9 pafta üretildi (30'lu), bakılmadı | 0/258 |
| Kaynak / hak zinciri | Yapısal zincir 258/258 (dosya, hash, lisans etiketi ile URL). Commons kaydında AI işareti 0, izinsiz lisans 0, kısıt 0 | tamamlanan 0/258 (insan hak alanları tasarım gereği "Bekliyor", değerlendirme dışı) |
| Kritik / değişken iddialar | 1880 iddia envanterde (181 kart); 802'si kaynak kopyasında dize olarak bulundu (bu doğrulama değildir); 1078 "not_in_source" | resmî kaynakta doğrulanan 0/1880 |
| Kaynak kopyaları (K76) | 416/416 SHA eşleşti; taze kopyayla 416/416 karşılaştırıldı: başlık eşleşmesi 415, örtüşme medyanı 1,0; şüpheli 1 (dil varyantı, bkz. bölüm 7) | — |
| Benzersiz URL'ler | 420/420 test edildi: 200 = 381; 3xx→200 = 39; 404/410/soft-404 = 0; 403/429 = 0; belirsiz = 0 (ilk koşuda 6 zaman aşımı, ikinci koşuda hepsi 200) | anlamsal hedef 0/420 |
| Zorunlu sayfa alanları | 23/23 (yapı, tür, referans) | — |
| Önizleme senaryoları | separate_stage | — |
| İnsan paket kararı | Karar yok, bekliyor: Teslimat.reviewer boş, editorial_status her sekmede "Taslak", 774 insan alanı "Bekliyor" (tasarım gereği, değerlendirme dışı). Sürüm v001 | — |

CHECK durumları (120): geçti 49, kısmi 15, kaldı 5, not_checked 38, uygulanmaz 3, separate_stage 10. Ayrıntı `check-results.json` dosyasında, puan tablosu `score.md` dosyasında.

## 4. Öncelikli bulgular

**P0** (0): yok

**P1** (4)

- **ISS-001 · P1 · K17 · Yanıt hedefi** (Yanıtlar 8–246, 239 kayıt).
  - Mevcut 239, hedef 240 (asgari 212 karşılandı). Konu başına 18–22 yanıt, 12/12 konu dolu.
  - Kanıt: validation-audit.json → structure.counts.answers; `_render/TESLIM_OZETI.txt`.
  - Düzeltme: 1 gerçek ihtiyaca cevap veren, resmî kaynaklı yanıt ekle (en az dolu konu: aile 18). Paketin kendi beyanına göre (OI-008) belediye sitesine erişilemediği için cevapsız kalan sorular var; bunlardan biri kapatılabilir.
- **ISS-002 · P1 · K17 · Mekân hedefi** (Mekânlar 8–107, 100 kayıt).
  - Mevcut 100, hedef 120 (asgari 92 karşılandı); en büyük hedef açığı (−20).
  - Zayıf gruplar: Spor 5, Çocuklarla keşif 7, Yeme ve içme 8.
  - Düzeltme: en az 20 gerçek, açık, kaynaklı ve fotoğraflı mekân ekle; collection ile şişirme yapma (K108).
- **ISS-003 · P1 · K17 · Mahalle hedefi** (Mahalleler 8–22, 15 kayıt).
  - Mevcut 15, hedef 16. Paket beyanı (OI-010): 16. semt için iki resmî kaynak bulunamadı — beyan, kanıt değil.
  - Düzeltme: 1 mahalle ekle (iki kaynak, aynı compare_json başlıkları, fotoğraflı).
- **ISS-004 · P1 · K22 · Fotoğraf kapsamı**.
  - Satırlar: Mekânlar!34, 36, 39, 40, 44, 51, 54, 64, 69, 70, 74, 76, 83, 85, 86, 88, 89, 98, 99; Mahalleler!13, 18, 19, 20, 21.
  - Mevcut: fotoğraflı mekân 81/100, mahalle 10/15; fotoğrafsız 24 (19 mekân + 5 mahalle). Resmî doğrulayıcı 20 sayıyor: 4 fotoğrafsız müze collection=Evet olduğu için uyarıdan muaf (ISS-007).
  - Grup bazında fotoğrafsız mekân: Müzeler 5, Çocuklarla keşif 4, Yeme ve içme 3, Sahne ve müzik 3, Spor 2, Doğa ve açık hava 1, Sanat ve sergiler 1.
  - Rota durağı olan fotoğrafsız mekânlar: centro-ceramica-triana (rota 002), mercado-de-la-encarnacion, bodega-gongora, mercado-lonja-del-barranco (rota 009), guadalquivir-paseo-de-las-delicias (rota 012).
  - Kanıt: validation-audit.json warning_classes (15 + 5); `_foto/decisions.json` entries_without_shortlist 24.
  - Düzeltme: her kayda en az bir gerçek, tekil, ücretsiz-ticari lisanslı kare; kare yoksa kaydın kapsamda kalmasına editoryal karar ver. 24 kaydın tam listesi `issues.json` dosyasında.

**P2** (4)

- **ISS-005 · P2 · K05 · Tekrar kanıt dosyaları** (Lisans kanıtları/, 16 dosya).
  - 8 kapak↔mekân çiftinin kaynak ve lisans kanıtı JSON'ları ikişer kez yazılmış (kapak-NN.*-evidence.json = <mekân>-NN.*-evidence.json). Envanter dup_sha 24 = 8 foto çifti (zararsız) + 16 kanıt dosyası. Artık dosya yok.
  - Düzeltme: kapak satırını mekân karesinin kanıt dosyasına bağla ya da tekrarı Teslimler'de gerekçelendir.
- **ISS-006 · P2 · K43 · Koordinatsız mekânlar** (28/100; Mekânlar!31, 49, 51, 54, 57, 63, 64, 69, 70, 74–89, 93, 98, 99).
  - 28 mekânda latitude/longitude boş; paketin hiçbir mekânında harita bağlantısı yok (haritalama yalnız koordinatla). Adres metni hepsinde dolu. Sözleşme koordinatı isteğe bağlı sayıyor; önceki şehirde (Eindhoven) 119/119 doluydu.
  - Koordinatı olan 72 mekân aralıkta; aynı koordinatlı 1 çift (estadio-la-cartuja / estadio-benito-villamarin-tur) kart notuyla tutarlı: Betis turu yenileme süresince La Cartuja'da (L1'de K39/K42 teyidi).
  - Düzeltme: 28 mekâna doğrulanabilir koordinat ekle ya da "Haritada aç" bağlantısı.
- **ISS-007 · P2 · K22 (K108 ile) · collection etiketi** (Mekânlar!35–44, 52, 72, 87; 13 kayıt).
  - Müzeler grubunun 10/12'si collection=Evet: Museo de Bellas Artes, Museo Arqueológico, Museo de Artes y Costumbres Populares, Museo del Baile Flamenco, Casa Fabiola, Centro Cerámica Triana, Museo Taurino, Museo Histórico Militar, Museo Marítimo Torre del Oro, Museo Historia de la Farmacia; ayrıca Convento de Santa Paula, Sánchez-Pizjuán turu, Casa de la Ciencia. Bunlar bağımsız adresli, kendi giriş ve saatleri olan tesisler.
  - Etki: resmî doğrulayıcı collection=Evet kayıtları fotoğraf uyarısından muaf tutar; 4 fotoğrafsız müze bu yüzden sayıya girmedi. Etiketin anlamsal doğruluğu K108 (L) kapsamında; L0 yalnız veri desenini raporlar.
  - Düzeltme: bağımsız müze/tesislerde collection=Hayır; etiketi yalnız gerçek alt nesneler için bırak.
- **ISS-008 · P2 · K14 · reviewed_on < bağlantı checked_on** (Yanıtlar!82, feria-de-abril-ulasim-park-ve-erisilebilirlik).
  - Kartın bağlantısı 2026-10-25'te kontrol edilmiş, kart reviewed_on 2026-10-24. Kaynak tarihleriyle çakışma 0 kayıt. Teslimat.updated_on 2026-10-25 = en son içerik tarihi; notes doğru.
  - Düzeltme: reviewed_on = 2026-10-25; birleştirmeye tarih sırası kapısı ekle.

## 5. Yanlış görseller (pafta / slot)

L0'da paftalara bakılmadı; yanlış görsel tespiti yapılmadı (K59–K62 not_checked). Paftalar `temas-sayfalari/sheet_01–09.jpg` (258 kare). Aşağıdakiler yalnız script sinyalidir; karar değil, L1 girdisidir.

**8 kapak = mekân karesi (dHash mesafe 0, aynı bayt).** Kapaklar sheet_09 slot 11–18'de (Fotoğraflar!258–265). Eşleri: kapak-01 = plaza-de-espana-03, kapak-02 = catedral-de-sevilla-giralda-01, kapak-03 = puente-de-triana-01, kapak-04 = parque-de-maria-luisa-01, kapak-05 = triana-02, kapak-06 = plaza-de-toros-de-la-maestranza-01, kapak-07 = palacio-de-san-telmo-02, kapak-08 = alameda-de-hercules-02.

**photo_prefilter "flag" (11 kare, "reject" 0):**

| Kare | Satır | Pafta / slot | İşaret |
|---|---|---|---|
| basilica-del-gran-poder-03 | Fotoğraflar!24 | sheet_01/18 | detail_interior |
| parque-infanta-elena-01/02/03 | !66–68 | sheet_03/3–5 | detail_interior (üçü de) |
| museo-del-baile-flamenco-03 | !216 | sheet_03/20 | rights_review (kişiler/sahne) |
| real-academia-bellas-artes-sevilla-03 | !221 | sheet_04/7 | detail_interior |
| auditorio-cartuja-sevilla-02/03 | !225–226 | sheet_05/9–10 | detail_interior |
| huevo-de-colon-01/02 | !151–152 | sheet_06/14–15 | statue_subject |
| kapak-06 | !263 | sheet_09/16 | place_mismatch |

Ayrıca: 52 karede bağımsız fotoğrafçı profil URL'si yok (provenance_note ile açıklanmış; K71 L1); CC0 12 + Public domain 4 dosya, 4'ünde license_url = source_url (K72 L1); 44 karede çekim tarihi boş, en eski çekim 2006 (K105 V).

## 6. Açık-mı örneklemi

L0'da yapılmaz (K39 not_checked). L1 için öncelikli adaylar: tarihli "itibarıyla" notu olan 4 mekân (Mekânlar!36 museo-arqueologico-de-sevilla, !56 teatro-lope-de-vega, !71 isla-magica, !73 estadio-benito-villamarin-tur — tur La Cartuja'da); paketin kendi beyanına göre (OI-011) 57 mekân "belirsiz" kaldı ve Pabellón de la Navegación iki kaynakla silindi — beyan kanıt değil, L1'de sınanır. Üretimin açık-mı klasörü `uretim/sevilla/_is/acik_mi` mevcut (L1'de yalnız örneklem önceliği için okunur).

## 7. İddia düzeltmeleri ve resmî kaynak

L0'da iddia denetimi yapılmadı (K29, K34, K35, K37, K40, K41 not_checked), bu yüzden düzeltme önerisi yok. L1 için script sinyalleri:

**1078 "not_in_source" (1880 iddianın %57'si).** Tür dağılımı: süre 435/445, tarih 295/397, hafta günü 106/111, yaş 91/96, para 77/394, yüzde 57/215, saat 17/222. claim_check "unit" modunda Türkçe birim ve gün adlarını (hafta, gün, Pazartesi…) İspanyolca kaynak metninde dize olarak aramaktadır; süre/gün/yaş türlerindeki yoğunluk büyük olasılıkla dil farkıdır, para ve saat türleri (sayı ağırlıklı) %80+ bulunmuştur. Karar L1 ajanının; para ve yüzde türündeki 134 "not_in_source" öncelikli.

**K76 şüpheli 1:** kaynak:106 (Kaynaklar!113, seg-social.es emeklilik sayfası): paket kopyası İspanyolca başlık, taze kopya İngilizce sürüm (başlık farklı, metin örtüşmesi 0,07). Dil varyantı; uydurma kopya işareti değil, L1'de sayfa açılır.

**Paketin kendi beyanları (`Teslimler/ACIK_KONULAR.txt`, 14 OI).** Bağımsız denetimde kanıt sayılmadı; L1'de sınanacaklar: OI-001/007/008 belediye (sevilla.org) erişimi ve bu yüzden eksik kalan konular (nüfus kaydı, IBI/araç vergisi, çöp vergisi, TUSSAM tarifesi, ZBE, Oficina de Extranjería…); OI-006 ülke paketi kartlarının geçerlilik tarihleri (6 kira kartı 2026-11-05); OI-009 EMVISESA çelişkisi, SAS randevu, Katedral indirimi; OI-013 üç ana sayfa kaynağı. Not: Excel'de sevilla.org'a giden 4 adres var ve bu denetimde hepsi çalıştı.

## 8. Bağlantı ve teknik hatalar (kök nedene göre)

**Kırık bağlantı:** 0/420.

**Geçici hata (ilk koşu, ikinci koşuda çözüldü):** 6 adres zaman aşımı/bağlantı koptu — sede.dgt.gob.es ×2 (Bağlantılar!463, !453; Kaynaklar!267, !150), www.dgt.es ×2 (Bağlantılar!454, !507; Kaynaklar!37, !122), www.boe.es BOE-A-2004-18911 (Bağlantılar!385, Kaynaklar!53), madrid-emb.mfa.gov.tr (Bağlantılar!371, Kaynaklar!276). `--retry-transient` ile ikinci koşuda hepsi 200. Kaynak kopyaları da ikinci koşuda 416/416 tamamlandı.

**Farklı alan adına yönlenen (P2 bakım önerisi, ayrı ISSUE açılmadı):**

- casadelaguitarra.es → flamencoensevilla.com (Bağlantılar!308, Kaynaklar!384; yalnız ana sayfa).
- www.aussa.es → aussa.com (Bağlantılar!527, Kaynaklar!191; yalnız ana sayfa).
- www.auditorionissancartuja.com/contacto → auditoriocartuja.com/contacto/ (Bağlantılar!282, Kaynaklar!356).

**Yalnız ana sayfaya giden kaynaklar (15; L1'de K51/K53):** alcazarsevilla.org (Kaynaklar!306, !345), casadelaguitarra.es (!384), minigolfsevilla.com (!388, Bağlantılar!313), palaciodelebrija.com (!308), rockandwallclimbing.com (!397), teatroflamencosevilla.com (!383), acuariosevilla.es (!362), alcazarsevilla.org, bodegagongora.com (!359), casadelaprovincia.es (!337), elpatiosevillano.com (!353), islamagica.es (!398), lasduenas.es (!307), aussa.es (!191); Şehir!8 aemet.es (hava sağlayıcısı). Paket OI-013'te 3'ünü beyan ediyor.

**Hiçbir karta bağlı olmayan kaynak (6, bilgi):** kaynak:142 (BOE Ley 28/2022), :143 (DGT canje), :188 (DGT ZBE veri seti), :439 (Alcázar iletişim), :440 (Lebrija iletişim), :445 (Acuario erişilebilirlik). İki Junta adresi aynı sayfayı taşıyor (kaynak:178 ve :259, tarjeta-transporte).

**Taze kopya kesildi:** 2 sayfa boyut sınırına takıldı (bilgi).

**Dosya yolu:** '\\' ayırıcısı 0 (Excel yol sütunları ve Teslimler dosyaları). Teslimat.notes serbest metninde `Teslimler\ACIK_KONULAR.txt` yazımı var (yol sütunu değil, bilgi).

**Teslim metaverisi:** TESLIM_OZETI, envanter ve ILERLEME_KAYDI ölçümle birebir aynı (K82/K83 geçti). Tarih sırası tek kayıt (ISS-008).

## 9. Düzeltme sırası

1. **ISS-004**: Fotoğrafsız 19 mekân ve 5 mahalleye gerçek, ücretsiz-ticari lisanslı kare ekle. Kontrol: entries_without_shortlist 0, "fotoğraf eksik" uyarısı 0.
2. **ISS-002**: 20 gerçek, açık, fotoğraflı mekân ekle (Spor, Çocuklarla keşif, Yeme ve içme öncelikli). Kontrol: counts.places ≥ 120.
3. **ISS-001 + ISS-003**: 1 yanıt ve 1 mahalle ekle. Kontrol: counts.answers ≥ 240, counts.neighborhoods ≥ 16.
4. **ISS-007**: Bağımsız müze/tesislerde collection=Hayır yap (L1'de K108 teyidi).
5. **ISS-006**: 28 mekâna koordinat (ya da harita bağlantısı) ekle.
6. **ISS-005 + ISS-008**: Tekrar kanıt dosyalarını bağla/gerekçelendir; Yanıtlar!82 reviewed_on'u düzelt; birleştirmeye tarih sırası kapısı ekle.
7. Yeni sürümle L0'ı yeniden çalıştır (yeni SHA; `impact.py --diff` ile bu Excel'e karşı), ardından **L1**: iddia denetçisi (öncelik para/yüzde "not_in_source" ve ülke paketi kartları), 9 paftanın görsel incelemesi (11 işaretli kare, kapak-06), açık-mı örneklemi (bölüm 6), K108 collection kararı.

L/V kontrolleri yapılmadan karar en iyi durumda "KARAR İÇİN KANIT EKSİK" kalır.

## 10. Çalıştırılmayan / tamamlanamayan kontroller

**not_checked (38)**

- L (LLM + kaynak): K18, K19, K20, K25, K26, K28, K29, K31, K32, K34, K35, K37, K38, K39, K40, K41, K42, K44, K47, K48, K51, K53, K54, K55, K71, K72, K90, K91, K108.
- V (görsel): K59, K60, K61, K62, K65, K74, K105.
- Script yok: K73, K81.

**separate_stage (10)**

- Drive: K01, K03, K109, K110.
- Önizleme: K92, K93, K94, K103, K111, K112.

**kısmi (15):** K07, K24, K30, K33, K64, K66, K67, K75, K76, K78, K79, K89, K106, K107, K120. Her birinin eksik kısmı kendi sınır_gerekçe alanında.

**kaldı (5):** K05 (ISS-005), K14 (ISS-008), K17 (ISS-001/002/003), K22 (ISS-004/007), K43 (ISS-006).

**uygulanmaz (3):** K36 (D7/D8 yalnız Portekiz), K99 ve K118 (ilk denetim; önceki sürüm yok).

**Yetenek kaydı (K06):** XLSX okuma, bayt/SHA, HTTP erişimi ve kod çalıştırma fiilen kullanıldı; görsel inceleme ve LLM iddia denetimi L0 dışı (yapılmadı, GEÇTİ sayılmadı).

**Karara etkisi:** A–D kategorilerinin tamamı ölçülmedi ("kontrol edilemedi" ya da "kısmi"); yüzde yalnız E kategorisinden geliyor. Script'in kesin gösterdiği 4 P1 nedeniyle karar DÜZELTME GEREKLİ. Bunlar kapansa bile L0'da karar en iyi durumda KANIT EKSİK olur.

## 11. Denetim çıktıları

Ana kayıtlar: `check-results.json` (120 CHECK), `issues.json` (8 açık ISSUE), `criteria.json`, `score.json` / `score.md`.

Script çıktıları: `url-checks.json` (2. koşu; ilk koşu `_analiz/url-checks-kosu1.json`), `dosya-envanteri.json` / `_dosya-envanteri-son.json`, `validation-audit.json`, `text-quality.json`, `xlsx-fidelity.json`, `claims.jsonl` / `claim-script.json` (2. koşu; ilk koşu `_analiz/claim-script-kosu1.json`), `kanitlar/snap/` (416 taze kopya).

Klasörler: `_dump/`, `_foto/` (candidates 258, plan, decisions, items, hazirlik, dhash-ciftleri), `temas-sayfalari/` (9 pafta, dhash.json), `_render/` (bağımsız teslim özeti), `_analiz/` (capraz-kontroller, snapshot-karsilastirma, k04-karsilastirma, betikler), `_cache/`.

Notlar (SKILL'e ek):

- url_check ve fetch_snapshot `--retry-transient` ile ikişer kez çalıştı; claim_check 416 kopya tamamlandıktan sonra yeniden koşuldu (no_snapshot 15 → 0).
- KAPSAM "Kismi" varsayılanından sapmalar: "geçti" (eksik kısım bu denetimde tamamlandı): K04, K16, K50 (ikinci koşuda tüm adresler teyit edildi). "kaldı" (bulgu): K05 (ISS-005), K43 (ISS-006).
- Yardımcı betikler önceki Eindhoven denetiminden alındı (`capraz.py`, `k04.py`, `snapcmp.py`; yalnız tarih ve dosya adı değiştirildi); `kayitlar.py` bu denetim için yazıldı.
