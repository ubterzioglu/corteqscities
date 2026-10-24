# Eindhoven yanıt yazarı: ortak talimat (CITY-039, v7)

Önce şu dosyayı oku ve uy: `C:\temp_private\corteqs\0000_newera\corteqs-skills\city-pack\agents\yanit-yazari.md`

Okuyucu: Eindhoven'a taşınan veya yeni taşınmış, Türkçe konuşan kişi (çoğu Türk vatandaşı; AB vatandaşı ve diğerleri de var). Dil: sade, doğal Türkçe. Yerel terimler özgün yazımıyla, ilk geçişte kısa Türkçe karşılığıyla: "huisarts (aile hekimi)".

## Girdi dosyaların
- Kaynakların: `_is\yazar\<konu>_kaynaklar.jsonl` (satır başına: source_id, url, final_url, title, publisher, text_file, why). `text_file` = sayfanın temiz metni. **Yalnız bu metinlerden yaz.**
- Bütün kökler: `C:\temp_private\corteqs\0000_newera\uretim\eindhoven\`

## Yazacağın dosyalar (kök altında)
1. `_is\data\parcalar\Yanıtlar.<konu>.jsonl`
2. `_is\data\parcalar\Bağlantılar.<konu>.jsonl`
3. `_is\claims\<konu>.jsonl` (iddia defteri)
4. (yalnız planlama) `_is\data\parcalar\Adımlar.planlama.jsonl`

## Yanıtlar satırı: anahtarlar BU SIRAYLA
```
entry_id, city_id, slug, title, subtitle, summary, keywords, stages, source_ids, reviewed_on, order, featured, editorial_status, topic_id, steps, documents, timing, cost, note, visual_json
```
- `slug`: küçük harf ASCII, tire ile, Türkçe karakter yok, ≤120. Konunun önekini KOYMA ama özgül ol (ör. `bsn-numarasi-alma`, `huurtoeslag-basvurusu`). `entry_id` = `eindhoven:<slug>`.
- `city_id` = `eindhoven`; `topic_id` = `eindhoven:<konu>`.
- `title` ≤180, soru veya iş adı ("BSN numarası nasıl alınır?"). Başka kartla aynı başlık olmaz.
- `subtitle` ≤160 (isteğe bağlı).
- `summary`: 2–5 cümle, kartın asıl cevabı. Somut: kim, ne zaman, nereye, ne kadar.
- `keywords`: virgülle 3–8 arama sözcüğü (Türkçe + yerel terim).
- `stages`: `;` ile, yalnız `before`, `planning`, `new`, `settled` değerlerinden (ör. `planning;new`).
- `source_ids`: `;` ile, yalnız senin kaynak dosyandaki `source_id`'ler; kartın her bilgisi bu kaynaklarda olmalı. Tekrar yok.
- `reviewed_on` = `2026-10-22`. `editorial_status` = `Taslak`. `featured`: konu başına en çok 2 kart `Evet`, diğerleri `Hayır`.
- `order`: tamsayı; senin aralığın verilecek (ör. 701–799), kart sırasına göre artan.
- `steps`: adımlar, **satır başına bir adım** (`\n` ile ayrılmış tek metin), 2–7 adım, her biri eylem cümlesi. Tekrar eden satır olmaz.
- `documents`: gerekli belgeler, satır başına bir tane (`\n`); yoksa boş string `""`.
- `timing`: süre/zamanlama (kaynakta varsa); yoksa `""`.
- `cost`: ücret (kaynakta varsa, tarih/dönemle); yoksa `""`. ASLA `-`, `bilinmiyor`, `?` yazma.
- `note`: kartı tamamlayan özel uyarı (ör. Türk vatandaşlarına özel kural); yoksa `""`. Kalıp cümle yazma.
- `visual_json`: yalnız gerçek bir süreç/karşılaştırma varsa JSON nesnesi METNİ, ör. `{"kind":"steps","title":"…","note":"Şematik","items":[{"key":"1","title":"…","text":"…"}]}`; yoksa `""`.
- Boş alan `""` olur; `null` yazma.

## Bağlantılar satırı
```
action_id, city_id, entry_id, label, url, checked_on, order
```
- `action_id` = `eindhoven:action:<slug>-1` (ikinci varsa `-2`). Her karta en az 1, en çok 3.
- `label`: Türkçe eylem: Başvur, Randevu al, Formu doldur, Hesapla, Kayıt ol, Bilgi al, Bilet al. Wikipedia yok; harita tek bağlantı olamaz.
- `url`: kaynak dosyandaki bir `url` (kartın en işlevsel sayfası). `checked_on` = `2026-10-22`. `order` 1, 2, 3.

## İddia defteri satırı
```json
{"claim_id":"C-<slug>-1","entry_id":"eindhoven:<slug>","field":"cost","claim":"...","value":"...","unit":"EUR","period":"2026","source_id":"eindhoven:kaynak:012","url":"...","quote":"kaynak metinden BİREBİR alıntı (≤200 karakter)"}
```
Kartta geçen HER sayı, ücret, süre, yaş, tarih, yüzde, telefon numarası ve kural için bir satır. `quote` text_file içinde harfi harfine geçmeli (kopyala-yapıştır; çeviri değil).

## Yasaklar
- Kaynak metinde olmayan bilgi. Bellekten "genelde şöyledir" yok.
- "Kurumdan doğrulayın", "güncel bilgi için siteye bakın", "değişebilir" gibi dolgu cümleleri.
- Kartlar arasında aynı cümle kalıbı (ör. her notun "Başvuru öncesi..." ile başlaması).
- Bir konuyu tek kartta geçiştirip diğer kartı onun kopyası yapmak.
- Başka konunun dosyalarına yazmak.

## Dönüş (tek satır JSON)
`{"topic":"<konu>","cards":N,"actions":M,"claims":K,"gaps":["kaynakta olmadığı için yazılamayan ama okuyucu için önemli konu", ...]}`
