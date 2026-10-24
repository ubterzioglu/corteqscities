# Script kapsami (checks.yaml 'S' kontrolleri)

Uretim: coverage_map.py (analiz_2026-10-22\yardimci_scriptler); atamalar yazarin yorumudur. 23 Ekim'de elle guncellendi: K05, K15, K63, K84 satirlarina city-audit'in audit_prep adimi, sona "Not" bolumu (K39, K32; S disi) eklendi. Dosya yeniden uretilirse satirlar coverage_map.py'nin IMPL tablosuna islenmeli, Not bolumu elle geri konmali; yoksa kaybolur.

- Toplam script kontrolu: 62 | tam: 42 | kismi: 18 | henuz yok: 2

## Tam kapsanan (42)

| Kontrol | Baslik | Oncelik | Script |
|---|---|---|---|
| K02 | Fiilî dosyaya erişim | P1 | inventory |
| K08 | Sekmeler, başlıklar ve teslim profili | P1 | build_xlsx fidelity + validate_all |
| K09 | Formül, biçim ve doğrulama alanları | P1 | xlsx_fidelity + xlsx_dump |
| K10 | Ham kayıtların doğru sayımı | P1 | xlsx_dump |
| K100 | Denetim kapsamını sayısal raporlama | - | editorial_score + render_summary |
| K104 | Okuyucuya denetim işi bırakan genel metinler | P1 | text_quality |
| K11 | Kimlik ve adres adı eşleşmesi | P1 | validate_all (resmi) |
| K114 | Orijinal dosya beyanının doğruluğu | P0 | inventory + validate_all |
| K115 | Rapor başında editoryal yüzde ve karar | - | editorial_score |
| K118 | Düzeltmenin bütün bağımlı kayıtlara yayılması | P1 | impact |
| K12 | Yabancı anahtar ilişkileri | P1 | validate_all (resmi) |
| K13 | Veri türleri ve izinli değerler | P1 | validate_all + build_xlsx DV |
| K14 | Tarihler ve sıralar | P1 | validate_all (resmi) |
| K15 | Dosya yolları ve arşiv güvenliği | P0 | inventory + validate_all + audit_prep hazirla (ters_egik_cizgi: ilk sayi 0 degilse K15 `kaldı`; K84'le ayni tarama) |
| K17 | Berlin alt sınırı ile güncel üretim hedefi | P1 | render_summary (resmi sayim) |
| K21 | Yanıt/mekân/mahalle işlem bağlantısı kapsamı | P1 | text_quality |
| K22 | Mekân ve mahalle fotoğraf kapsamı | P1 | render_summary (varlik; dogruluk degil) |
| K23 | Fotoğraf tekilliği ve kredi | P1 | common.group_unique_photos |
| K27 | Birebir metin tekrarı | P1 | text_quality |
| K45 | Mahalle compare_json yapısı | P1 | validate_all |
| K46 | Rota veri ilişkileri | P1 | validate_all |
| K49 | URL biçimi ve güvenli hedef | P1 | validate_all (URL bicimi) |
| K50 | Fiilî HTTP erişimi | P1 | url_check + web_fetch |
| K52 | 403/429 ve geçici hata | P2 | url_check + web_fetch |
| K56 | Kapsam ve bağlantı sonuçlarının raporlanması | P2 | url_check |
| K57 | Dosyanın görüntü olarak açılması | P0 | inventory + validate_all |
| K58 | Hash ve boyut doğruluğu | P0 | inventory |
| K63 | Türevler ve yakın görsel tekrarları | P1 | image_hash + contact_sheet (dHash) + audit_prep (hazirla: ayni_sha.K63; ciftler: K63_aday) |
| K68 | Proje tarafından reddedilen kullanım koşulları | P0 | validate_all |
| K69 | Lisans adı, sürümü ve URL | P1 | validate_all |
| K70 | Gerçek fotoğrafçı | P1 | validate_all --new-content |
| K77 | Fotoğraf kaynak zincirinin tekil eşleştirmesi | P1 | validate_all |
| K80 | Orijinal ve web türevi | P0 | inventory + validate_all |
| K83 | Teslim özeti ve açık konular | P1 | render_summary |
| K84 | Kayıpsız ve taşınabilir teslim | P1 | inventory + audit_prep hazirla (ters_egik_cizgi; inventory Windows'ta ters egik cizgili yolu gormez) |
| K85 | Zorunlu 23 SayfaAlanları anahtarı | P1 | validate_all |
| K86 | facts, quick_links, advice_entry | P1 | validate_all |
| K87 | timeline ve Adımlar ayrı kontroller | P1 | validate_all |
| K88 | Bütçe alanları | P1 | validate_all |
| K95 | Resmî doğrulayıcıyı tam paketle çalıştırma | P0 | validate_all |
| K97 | AI kontrolü ile insan kararını ayırma | P0 | build_xlsx + render_summary |
| K99 | Düzeltmeden sonra hedefli yeniden kontrol | P1 | impact |

## Kismi (18)

| Kontrol | Baslik | Oncelik | Script |
|---|---|---|---|
| K04 | Paketi denetim süresince sabitleme | P1 | inventory (SHA'lar; onceki/sonraki karsilastirma elle) |
| K05 | Klasör düzeni ve dosya artıkları | P2 | inventory (artik/orphan; coklu Excel yok) + audit_prep hazirla (ayni_sha.K05) |
| K106 | Ücretsiz ve gerçek fotoğraf şartının kesin uygulanması | P0 | validate_all (lisans) + photo_rules (AI etiketi) |
| K107 | Aday fotoğraf sayısı ile teslim fotoğrafı ayrımı | P1 | photo_prefilter (aday/kisa liste) |
| K16 | EkDetaylar ve uzun alanlar | P1 | validate_all (uzun deger geri yukleme sayisi) |
| K24 | Eşiklerin işlevsel tamamlanması | P1 | render_summary |
| K30 | Toplu genel kaynak atama | P1 | extra_checks.homepage_only_sources |
| K33 | Süreç görselinin doğruluğu | P1 | text_quality (visual_json) |
| K43 | Koordinatların anlamlı olması | P1 | validate_all (aralik) + extra_checks.shared_coordinates |
| K64 | Yapay/yer tutucu görsel işaretleri | P0 | photo_rules (AI etiketi; piksel analizi yok) |
| K66 | Fotoğraf incelemesi sonrası yeniden sayım | P1 | render_summary |
| K67 | Tekil esere ait lisans | P0 | photo_candidates + photo_rules (Commons lisans alani) |
| K75 | Atıf ve değişiklik bildirimi | P1 | validate_all --mode emit (atif CSV/HTML) |
| K76 | Kanıtın kendisinin gerçek olması | P0 | fetch_snapshot (snapshot hash) |
| K78 | Beş farklı kaynak adresi | P1 | validate_all |
| K79 | Çekim, indirme ve kontrol tarihleri | P1 | validate_all (kismi) |
| K82 | Kanıt ve manifestlerde tek doğruluk | P1 | validate_all (kismi) |
| K89 | Keşif grupları ve filtreler | P1 | validate_all (kismi) |

## Henuz script yok (2)

| Kontrol | Baslik | Oncelik | Script |
|---|---|---|---|
| K73 | Özel açık/ücretsiz stok lisansları | P1 | - |
| K81 | İncelenen karenin teslim edilen kare olması | P1 | - |

## Not: S disi kontroller (sayima girmez)

Asagidaki iki kontrol checks.yaml'da `exec: L`; KAPSAM yalniz S kontrollerini sayar, bu yuzden ustteki tablolarda yoklar. Script destegi kanit ya da girdi uretir; CHECK kaydi L kuraliyla verilir.

| Kontrol | Baslik | Oncelik | Script destegi |
|---|---|---|---|
| K39 | Açık/kapalı bilgisi ve erişim | P1 | acik_mi (B15): ajanlarin "bugun acik mi" tarama ve dogrulama satirlarinin tamligini ve kurallarini denetler; mekanin acik oldugunu kendisi kanitlamaz. Uretimde city-pack places kapisi; girdi uretimin is klasoru (`_is\acik_mi`). city-audit L1/L2'de iki kosu: `$ACIKMI` (uretimin klasoru) yalniz beyandir, bulgusu orneklem onceligi olur (`acik-mi-uretim.json`); asil kanit `$OUT\_acikmi` dogrulamasidir (L1 orneklem, L2 butun mekanlar): denetim ajanlarinin satirlari, kapi bunlari mekanik sinar (`acik-mi-denetim.json`). L1: bulgu varsa `kaldı`, yoksa `kısmi`; `geçti` yalniz L2'de (bulgu yok, dogrulanamayan 0). L0'da `not_checked` (exec L). |
| K32 | Dil, tutarlılık ve desteklenmeyen vaat | P2 | text_quality --address-standard sen (B16 hitap olcumu; standart "sen", Berlin ornegi gibi; city-pack intake'te `hitap.txt`): ozet `address` kayitlari hitap bicimine gore sayar (hitapsiz/siz/sen/karisik; karisik = ayni kayitta hem "siz" hem "sen"); bulgu standart disi ("sen" standardinda "siz") ve karisik kayittir, kisisiz kayit bulgu degildir (`address.findings`; varsa cikis 1). Bayraksiz (varsayilan `off`) yalniz sayar, bulgu vermez. K32 P2 ve `exec: L`: city-audit L0/L1'de `not_checked` (L1 yalniz P0/P1 L kontrollerini yapar), hitap denetime yalniz L2'de girer. Kilavuz hitabi ayrica anmaz, B16 proje karari; dilin geri kalani ve desteklenmeyen vaat L'de. |

