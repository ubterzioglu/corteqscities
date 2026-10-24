# Eindhoven yer/sayfa yazarları: ortak talimat (CITY-039, v7)

Önce `C:\temp_private\corteqs\0000_newera\uretim\eindhoven\_is\yazar\ORTAK_TALIMAT.md`'yi oku: dil, iddia defteri biçimi, yasaklar, `stages`/`reviewed_on`/`editorial_status`/`featured` kuralları AYNEN geçerli. Kök: `C:\temp_private\corteqs\0000_newera\uretim\eindhoven\`. Kendi geçici klasörün: `C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\3dadd8be-f0d2-423f-acbe-036dd2504ce8\scratchpad\<görev_adın>\`.

## Kaynak kuralı
- Mevcut kaynaklar: `_is\kaynak_dizini.jsonl` (source_id, url, text_file). Bunlardan yazıyorsan `source_ids`'e source_id yaz.
- YENİ kaynak gerekiyorsa (mahalle/mekân): WebFetch ile resmî sayfayı aç, yalnız sayfada yazanı yaz. `source_ids` YERİNE satıra `"source_urls": "url1;url2"` alanı koy (`source_ids` boş string). İddia defterinde `source_id` yerine `"url"` doldur ve `quote` sayfadan BİREBİR olsun. Biz bu adresleri kendi script'imizle indirip alıntıları doğrulayacağız; uymayan satır geri döner.
- Wikipedia yok. Anasayfa tek başına kaynak değil.

## Anahtar sıraları (birebir; satır başına bir JSON)
- **Mekânlar**: entry_id, city_id, slug, title, subtitle, summary, keywords, stages, source_ids, reviewed_on, order, featured, editorial_status, group, district, setting, location, latitude, longitude, visit_status, note, collection, media_key (+ gerekiyorsa source_urls)
  - group ∈ Müzeler | Sanat ve sergiler | Sahne ve müzik | Spor | Doğa ve açık hava | Çocuklarla keşif | Yeme ve içme | Tarih ve mimari; setting ∈ Kapalı alan | Açık hava | Karma; location = açık adres; latitude/longitude ikisi birlikte sayı veya ikisi boş; collection = "Hayır"; visit_status ve media_key = "".
- **Mahalleler**: entry_id, city_id, slug, title, subtitle, summary, keywords, stages, source_ids, reviewed_on, order, featured, editorial_status, location, tags, compare_json, note, media_key (+ source_urls)
  - tags = satır başına bir etiket; compare_json = JSON nesnesi METNİ, ≥4 anahtar, değerler boş olmayan düz metin, TÜM mahallelerde AYNI başlıklar (ör. {"Ulaşım":"…","Yaşam ritmi":"…","Konut tipi":"…","Yeşil alan":"…"}); media_key = "".
- **Sözlük**: term_id, city_id, term, definition, source_ids, reviewed_on, order, editorial_status — term_id = `eindhoven:term:<n>` (001…), order 1..N.
- **SayfaAlanları**: field_id, city_id, key, label, value_type, value, reviewed_on — field_id = `eindhoven:field:<key>`; value_type ∈ Metin | Sayı | Mantıksal | JSON.
- **Şehir** (tek satır; yalnız boş alanları doldur, dolu alanlara dokunma): mevcut satır `_is\sablon_dump_full\Şehir.jsonl`.
- entry_id = `eindhoven:<slug>`, slug küçük harf ASCII; slug ve başlık TÜM pakette benzersiz (`_is\data\Yanıtlar.jsonl` ile çakışmasın).
- Her mekân ve mahalle için `_is\data\parcalar\Bağlantılar.<görev>.jsonl`'e en az 1 işlem satırı (ORTAK_TALIMAT biçimi; label ör. "Bilet al", "Ziyaret bilgisi", "Haritada aç" tek başına olamaz).
