# Yanıt yazarı görevi — Málaga (CITY-075)

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\yanit-yazari.md`. Alan anahtarları ve uzunluklar: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\references\contract_digest.md` §2 (Yanıtlar, Bağlantılar, Adımlar). Yol ve biçimde ortak kurallar esastır.

## Değerler
- `<city_id>` = `malaga`; şehir: Málaga, İspanya (Endülüs, Málaga ili)
- `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\malaga`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`
- `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `36.57,36.87,-4.60,-4.28`
- **Hitap: `sen`** (okura 2. tekil; "siz" yok; bir kayıtta biçim karışmaz).
- `<gorev>` = `<konu>` = görev mesajındaki konu slug'ı; `topic_id` = `malaga:<konu>`.

## Dosyalar (yalnız bunlar)
- `<WORK>\_is\data\parcalar\Yanıtlar.<konu>.jsonl`
- `<WORK>\_is\data\parcalar\Bağlantılar.<konu>.jsonl`
- `<WORK>\_is\claims\<konu>.jsonl`
- (yalnız planlama) `<WORK>\_is\data\parcalar\Adımlar.planlama.jsonl`: ≥4 taşınma yolculuğu adımı.

## ÜLKE PAKETİ KARTLARI — ÇOK ÖNEMLİ
Bu üç dosyada (keşif konusu hariç) ülke ve Endülüs paketinden gelmiş kartlar ZATEN VAR (`order` 9000–9104, `featured` = `Hayır`). Bunlar `country_cards`'tır:
- Bu satırları **SİLME ve DEĞİŞTİRME** (Yanıtlar, Bağlantılar ve claims satırlarının hiçbiri). Dosyayı baştan yazma: mevcut satırları oku, kendi satırlarını **SONUNA ekle**.
- Ülke kartıyla aynı konuyu tekrar yazma. Ulusal/bölge kuralı orada; sen **Málaga'ya özgü** olanı yaz: Málaga'daki ofis, adres, randevu yolu, yerel hizmet, yerel tarife, yerel kurum. Bir ülke kartını "Málaga'da nasıl yapılır" diye tamamlayan ayrı kart yazabilirsin (farklı slug, farklı başlık).
- Slug'ın ülke kartlarının slug'larıyla çakışmasın.
- `featured`: konunun en çok 2 kartı `Evet` olabilir; bunları **kendi Málaga kartlarından** seç (ülke kartlarına dokunma), geri kalan `Hayır`.

## Kapsam
- `order`: görev mesajındaki aralık (konu sırası × 100 ile başlar), kendi kartlarında artan.
- Kart sayısı: görev mesajındaki hedef (yalnız SENİN ekleyeceğin Málaga kartları). Kaynak desteklemiyorsa daha az yaz; hedefi değersiz kartla doldurma. Konunun toplamı (ülke + sen) 26'yı geçmesin.
- Keşifte bulunamayanlar (ek kaynak gerektiren, tekrar arama): `<WORK>\_is\kesif\gaps.json` (senin konunun anahtarı). Bunları `gaps`e taşıyabilirsin; uydurma.
- `ilk5.json`'daki 5 soru (`<WORK>\_is\yazar\ilk5.json`, senin konunun anahtarı): her biri bir kartla (ülke kartı ya da senin kartın) cevaplanmalı; kaynağı yoksa `gaps`'e yaz.
- Kaynakların: `<WORK>\_is\yazar\<konu>_kaynaklar.jsonl` (`text_file` = kopyanın temiz metni; yalnız bunları oku). Ülke kartlarının kaynaklarını kendi kartında kullanman gerekirse `source_id`'leri o kartlardaki gibi kullanabilirsin.
- Kart başına **en çok 2** `source_ids`; iddiayı desteklemeyen kaynak bağlanmaz. Kart başına en çok 2 Bağlantılar satırı (en az 1 işlem bağlantısı; harita tek bağlantı olamaz).
- Yeni kaynak gerekirse ortak kurallar §4 ile `add_sources` (klasör `snap_<konu>-yazar<sira>`), **konu başına en çok 4 yeni kaynak**. Yalnız resmî yayıncının derin sayfası.
- **Erişim:** `<WORK>\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu". malaga.es, sede.malaga.eu (JS), deportes.malaga.eu (JS), sede.administracionespublicas.gob.es, inclusion.gob.es, mivau.gob.es, huvv.es, aena.es, bibliotecas.malaga.eu, gmu.malaga.eu ERİŞİLEMEZ: deneme; o bilgi yoksa `gaps`.
- Tarihe duyarlı bilgi (ücret, tarife, süre, yaş eşiği, 2026 kural değişikliği): kaynağın tarihinden sonra yeni kural çıktı mı, kısa bir arama yap; çelişki varsa `gaps`'e yaz.
- Bellekten bilgi yok; her değişken iddia defterde birebir alıntıyla.

## Sınırlar
- **Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>` klasöründe.
- Bütçe: 35 dakika / 100 araç çağrısı. Dolunca yazdıklarını tutarlı bırak ve dön.
- Kartları parça parça yaz: her 3–4 kartta bir dosyaya ekle (sonda toplu yazma; ana döngü 10 dk büyümeyen dosyayı takılmış sayar).
- Kabuk: PowerShell aracını kullan (python komutları için `& '<PY>' ...`). Bir komut 2 dakikadan uzun yanıtsız kalırsa bekleme; dosyaları Read/Write ile oku-yaz, add_sources gerekiyorsa o kaynağı `gaps`e yaz.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"topic_id":"malaga:<konu>","cards":<SENİN eklediğin kart>,"country_cards_kept":<dosyadaki ülke kartı>,"claims":<senin iddiaların>,"new_sources":<add_sources ile eklenen>,"ilk5_covered":[true,...],"gaps":[...]}`
