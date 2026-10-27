# Rota, mahalle ve sayfa editörü — Sevilla (CITY-107), ikinci düzeltme turu

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra aynı klasördeki `editor.md`, `yer-yazari.md`, `mekan-yazari.md` (rota kuralları). Kayıtları sen yazmadın, denetimi de sen yapmadın.

## Değerler
- `<city_id>` = `sevilla`; `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`**
- Tur: **denetim turu, açık görevler 1, 2, 6, 7**. Kayıt ekleme/silme yok; `route_id`, `entry_id`, `field_id` değişmez.

## Bağlam
21 mekân paketten silindi (`<WORK>\_is\duzeltme2\cikan_mekanlar.txt`). Rotalarda duraktan çıkanlar: route:004 `muralla-de-la-macarena` (bilgisi `basilica-de-la-macarena` kartına taşınıyor), route:006 `museo-taurino-real-maestranza` (bilgisi `plaza-de-toros-de-la-maestranza` kartına taşınıyor), route:009 `bodega-gongora` ve `mercado-lonja-del-barranco`. Yeni mekânlar: `sevilla:jardines-de-cristina`, `sevilla:jardin-americano`, `sevilla:plaza-de-santa-cruz` (başka ajan yazıyor; durak olarak kullanabilirsin).

## İşler
1. **Rota durakları:** silinen durakları `stop_entry_ids`'ten çıkar; rotanın konusu bozulursa pakette var olan uygun mekânla değiştir (`<WORK>\_is\data\parcalar\Mekânlar.*.jsonl`'de olmalı); rota 2–8 durak kalır; rota metni (özet, adımlar, süre) duraklarla tutarlı olur.
2. **L1 bulguları** `<WORK>\_is\duzeltme2\rota_sayfa_bulgular.json`:
   - ISS-009: route:005'te Cartuja Center genel ziyarete açık değil → notta açık uyarı ya da durağı değiştir.
   - ISS-028: rotalarda pazar/pazartesi kapanış uyarıları (durak mekânlarının kartındaki saat bilgisine göre).
   - ISS-026/027: mahallelerin "Ulaşım" başlıklı içeriği (kaynaklı, somut hat/istasyon; kaynakta yoksa genel ifadeyle değil, kaynaktaki bilgiyle daralt).
   - ISS-029–031: şehir sayfası alanları ve acil numaralar (SayfaAlanları, Şehir).
   - SayfaAlanları'ndaki `place_groups` ya da başka alanlarda silinen mekân kimliği geçiyorsa çıkar.
- Düzenleyeceğin dosyalar: `<WORK>\_is\data\parcalar\Rotalar.rota.jsonl`, `Mahalleler.mahalle.jsonl`, `Mahalleler.mahalle2.jsonl`, `Bağlantılar.mahalle*.jsonl`, `SayfaAlanları.sayfa.jsonl`, `Şehir.sayfa.jsonl` ve ilgili defterler `<WORK>\_is\claims\rota.jsonl`, `mahalle*.jsonl`, `sayfa.jsonl`. Mekân dosyalarına dokunma. Şehir satırında `latitude`, `longitude`, `aliases` değişmez.

## Değişiklik kaydı
`<WORK>\_is\denetim\rota-d2_degisiklik.jsonl`, `mahalle-d2_degisiklik.jsonl`, `sayfa-d2_degisiklik.jsonl` (`editor.md` biçimi; `bulgu_claim_id` = ISS kimliği).

## Yeni kaynak ve erişim
Ortak kurallar §4 (`snap_<parça>-editor<sira>`), parça başına en çok 3. Erişim haritası `<WORK>\_is\kesif\KESIF_TALIMAT.md`. Engelli alan adlarını deneme (sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es).

## Bitirmeden
Ortak kurallar §8'deki `merge_package` kontrolü (çıktılar `<TMP>`'ye): rota/mahalle/sayfa parçalarını ilgilendiren bulgu 0. Yeni üç mekân henüz yazılmamışsa onları durak yapma (bulgu verir).

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız `<TMP>` = `C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\56c9766a-06a1-495c-9d57-190d48973e42\scratchpad\rs_w\`. Her işi bitirince dosyaya yaz. Bütçe 45 dakika / 130 araç çağrısı.

## Dönüş
Tek satır JSON: `{"rota":{...},"mahalle":{...},"sayfa":{...}}` (her biri `editor.md` dönüş biçiminde) ve `"open":[...]`.
