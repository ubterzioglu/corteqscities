# Yer yazarı görev dosyası (Bakersfield · CITY-901 · 23.10.2026)

Önce `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\yer-yazari.md`, sonra `...\agents\mekan-yazari.md` oku. Yol ve biçim çelişirse ortak kurallar ve yer-yazari.md esastır (mekan-yazari.md'deki `data/Mekânlar.<dilim>.jsonl` yolu GEÇERSİZ; doğru yollar aşağıda).

## Gerçek değerler
| Yer tutucu | Değer |
|---|---|
| `<city_id>` | `bakersfield` |
| `<WORK>` | `C:\temp_private\corteqs\0000_newera\uretim\bakersfield` |
| `<TK>` | `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts` |
| `<PY>` | `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe` |
| `<TMP>` | görev mesajında |
| `<gorev>` | görev mesajında (ör. `m1`, `sozluk`) |
| `<konu>` | `kesif` (mekân), `sozluk` (sözlük), `mahalle`, `sayfa`, `rota` — görev mesajında |
| `<rol>` | `yazar` |
| `<tarih>` | `2026-10-23` |
| `<bbox>` | `35.1740,35.4680,-119.2853,-118.7527` (Census şehir sınırı kutusu + pay; `ortam.ps1`'deki `$BBOX` ile aynı) |

Şehir: Bakersfield, Kern County, California, ABD. Para birimi USD. Hitap: okura **"sen"** (`<WORK>\_is\yazar\hitap.txt` = `sen`); "siz" yok, kayıt içinde biçim karışmaz; bilgi cümlesi kişisiz olabilir.

## Mekân yazarları için
- Plan: görev mesajındaki `<WORK>\_is\mekan\plan_<gorev>.jsonl`. Satır alanları: `name, group, qid, lat, lon, district, setting, official_url, slug, entry_id, source_id, source_text_file, source_publisher, turizm_burosu_kaynagi, secim_notu, secim_nedeni, must_contain`. `slug`, `entry_id`, `group`, `district`, `setting`, `lat`/`lon` AYNEN (boşsa `""`; uydurma, haritadan okuma yok). `title` = `name` (özgün yazım; gerekirse resmî ada göre düzelt ama `slug` değişmez).
- `source_ids` en az plandaki `source_id`. Bilgiyi yalnız `source_text_file` metninden ve eklediğin kaynaklardan al.
- **Turizm bürosu izni (ana döngü, açık izin):** `turizm_burosu_kaynagi: true` olan mekânlarda mekânın kendi sitesi ya da belediye sayfası bu ortamda kullanılamadığı (adres yok, indirilemiyor, belediye sitesi bot engelli) için Visit Bakersfield (şehrin turizm bürosu) sayfası kaynaktır; `add_sources` kanıtıyla zaten kabul edildi. Tanıtım dilini aktarma, yalnız olguları (adres, saat, ücret, ne olduğu) yaz. Diğer mekânlarda turizm bürosu sayfası ekleme.
- **Tarihî yerler:** bazı tarih/mimari satırlarının kaynağı California OHP Kern County listesidir (adres yok, yapının adı ve landmark numarası var). `location` için kaynakta adres yoksa kaynaktaki konum bilgisini yaz (ör. "Bakersfield şehir merkezi, …"); daha iyi adres için yapının sahibinin ya da resmî kurumun sayfasını `add_sources` ile ekleyebilirsin. `secim_notu`'ndaki "dışarıdan görülebilir" bilgisini karta yansıt (içi ziyarete açık demeden).
- **Kern River Parkway parkları** aynı Kern River Parkway Foundation sayfasını paylaşıyor; her parkın kartını o sayfadaki kendi bölümünden yaz, kartlar birbirinin kopyası olmasın.
- `location` zorunlu ve boş kalamaz: kaynaktaki açık adres; adres yoksa kaynaktaki konum tarifi. `visit_status` = `""` (kaynak kapalı/tadilat diyorsa kısa durum + defter). `collection` = `Hayır`. `media_key` = `""`.
- Her mekâna 1–3 Bağlantılar satırı (`label` ör. "Ziyaret bilgisi", "Bilet al", "Rezervasyon yap", "Menüyü gör" yalnız sayfa öyleyse); `url` kaynak dizinindeki bir `url`/`final_url` ile birebir aynı ve `https://`. Kaynağın adresi `http://` ise ve `final_url` `https://` değilse o mekân için başka resmî https sayfası ekle ya da `open`'a yaz.
- Her adres, saat, ücret, yaş sınırı ve kural için defter satırı (`field` = `location`, `summary`, `note` …; `quote` birebir).
- Notlar ve özetler kalıplaşmaz; her mekânın notu kendine özgüdür ya da `""`.
- Kapanmış/taşınmış görünen yer: yazma, `gaps`'e yaz (ayrıca "bugün açık mı" denetimi yapılacak).
- Kart başlığı (`title`) Yanıtlar, Mekânlar, Mahalleler'in tamamında benzersiz olmalı (`<WORK>\_is\data\parcalar\` altındaki öteki parçalara bak).

## Dosyaların
`<WORK>\_is\data\parcalar\<Sekme>.<gorev>.jsonl` (yalnız görevindeki sekmeler; mekân/mahallede ayrıca `Bağlantılar.<gorev>.jsonl`), `<WORK>\_is\claims\<gorev>.jsonl`. Geçici her şey `<TMP>`'de.

## Bitirmeden
Ortak kurallar §8: `merge_package` `--data-out <TMP>\birlesik --out <TMP>\birlestir_rapor.json --bbox=35.1740,35.4680,-119.2853,-118.7527`; kendi satırlarının okunduğunu doğrula, kendi parçana ait `issues`/`quote_miss_list` 0. yer-yazari.md "Bitirmeden" sayımları.

## Dönüş
yer-yazari.md'deki tek satır JSON.
