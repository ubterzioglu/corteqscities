# Mekân editörü — Sevilla (CITY-107), ikinci düzeltme turu

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra aynı klasördeki `editor.md`, `yer-yazari.md`, `mekan-yazari.md`. Kayıtları sen yazmadın, denetimi de sen yapmadın.

## Değerler
- `<city_id>` = `sevilla`; `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`**
- Tur: **denetim turu, açık görevler 1, 2, 6, 7** + aşağıdaki A ve B işleri. `entry_id`/slug değişmez.

## Bağlam
Bağımsız denetim (L1) bulgularından sonra 21 mekân kaydı ana döngü tarafından paketten silindi (18 fotoğrafsız + 3 alt nesne; liste `<WORK>\_is\duzeltme2\cikan_mekanlar.txt`). Silinen kayıtların eski satırları `<WORK>\_is\duzeltme2\yedek\` altında (yalnız okumak için). Bu kayıtları geri ekleme.

## A. Yeni 3 mekânı yaz (görev 4 yalnız bu üçü için açık)
Seçim satırları: `<WORK>\_is\mekan\secim_I.jsonl` (Jardines de Cristina, Jardín Americano, Plaza de Santa Cruz; `slug`, `entry_id`, `group`, `qid`, `lat`, `lon`, `district`, `setting`, `note` aynen kullanılır). Kaynakları: `sevilla:kaynak:495`, `496`, `497` (`<WORK>\_is\kaynak_dizini.jsonl` → `text_file`). Gerekirse mekân başına en çok 1 ek resmî kaynak (ortak kurallar §4, klasör `snap_mekan7-yazar<sira>`).
- Dosyalar (yeni): `<WORK>\_is\data\parcalar\Mekânlar.mekan7.jsonl`, `Bağlantılar.mekan7.jsonl`, `<WORK>\_is\claims\mekan7.jsonl`. Anahtar sırası ve alanlar var olan `Mekânlar.mekan1.jsonl` satırlarıyla aynı; `order` 7001–7003; `collection` = `Hayır`; `editorial_status` = `Taslak`; `media_key` var olan satırlardaki biçimle.
- Her mekâna ≥1 Bağlantılar satırı (harita bağlantısı tek bağlantı olamaz); ücret ve saat yalnız resmî kaynakta varsa (turizm portalı ücret/saat kaynağı değil). Mekân notu kalıplaşmaz.

## B. L1 mekân bulgularını kapat
Bulgular (17 alanlı kayıtlar): `<WORK>\_is\duzeltme2\mekan_bulgular.json` — ISS-005, 006, 007, 008, 020–025, 037. Silinmiş mekânlara ait kısımlar düşer.
- **ISS-005 (alt nesne birleştirme):** Alcázar Bahçeleri bilgisi `sevilla:real-alcazar-de-sevilla` kartına, Museo Taurino bilgisi `sevilla:plaza-de-toros-de-la-maestranza` kartına, Macarena surları bilgisi `sevilla:basilica-de-la-macarena` kartına (yoksa en yakın ilgili karta) kısa ve kaynaklı olarak eklenir; gereken defter satırları ana kartın `entry_id`'siyle yeniden yazılır (eski defter satırları yedekte).
- **ISS-006:** Maestranza tarifesi resmî sayfadan: https://visitaplazadetorosdesevilla.com/tarifas/ (genel 12 €, indirimli 7 €, 7–11 yaş 4 €; güreş günü kapanış saati sayfadaki gibi). Kaynak listede yoksa `add_sources`.
- **ISS-007:** Setas (Mercado de la Encarnación) seyir terası saati resmî siteye göre; San Jerónimo parkının adresi resmî kayda göre (ES resmî adres kaydı: CartoCiudad/IGN; sonuç kutu içinde ve adres kartla aynı olmalı).
- **ISS-008:** `sevilla:huevo-de-colon` koordinatı: yalnız Wikidata P625 ya da CartoCiudad; bulunamazsa boş kalır ve `open`'a yazılır.
- **ISS-020–025, 037:** bulgudaki önerilen düzeltme; "Bilet al" bağlantısı mekânın genel satış sayfasına gitmeli, satış yoksa etiket sayfanın gerçek işine göre ("Ziyaret bilgisi" vb.).
- Düzenleyeceğin dosyalar: bulgunun kaydının bulunduğu `Mekânlar.mekan<N>.jsonl`, `Bağlantılar.mekan<N>.jsonl`, `claims\mekan<N>.jsonl` (kaydı `<WORK>\_is\data\parcalar\` altında `entry_id` ile ara). Rotalar, Mahalleler, SayfaAlanları başka ajanın işidir; dokunma.

## Değişiklik kaydı
`<WORK>\_is\denetim\mekan-d2_degisiklik.jsonl` (dosya var, ana döngünün silme satırları başta; sonuna ekle). `bulgu_claim_id` = ISS kimliği; yeni mekânlar için `alan` = `kayit_eklendi`.

## Yeni kaynak ve erişim
Ortak kurallar §4. Erişim haritası: `<WORK>\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu". Engelli alan adlarını deneme (sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es). Ayna/yan alan adı kaynak olmaz.

## Bitirmeden
Ortak kurallar §8'deki `merge_package` kontrolü (çıktılar `<TMP>`'ye): kendi parçalarını ilgilendiren bulgu 0. Rotalarda silinen mekân duraklarından gelen bulgular başka ajanındır, say ama düzeltme.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız `<TMP>` = `C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\56c9766a-06a1-495c-9d57-190d48973e42\scratchpad\me_w\`. Her işi bitirince dosyaya yaz (A'yı bitir yaz, sonra B'yi bulgu bulgu). Bütçe 50 dakika / 150 araç çağrısı.

## Dönüş
Tek satır JSON: `{"part":"mekan-d2","yeni_mekan":["slug"],"birlestirilen":3,"uygulanan":a,"reddedilen":b,"degisen_kayit":d,"yeni_kaynak":e,"script_kontrol_hata":f,"open":["..."]}`
