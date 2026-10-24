# Yanıt yazarı görev dosyası (Bakersfield · CITY-901 · 23.10.2026)

Önce `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\yanit-yazari.md` oku. Dosya yolu, alan biçimi ve iddia defteri için ortak kurallar esastır (yanit-yazari.md'deki `data/Yanıtlar.<topic_id>.jsonl` ve `claims/<topic_id>.jsonl` yolları ve defter örneğindeki `field: body` GEÇERSİZ; doğru yollar aşağıda).

## Gerçek değerler (yer tutucular)
| Yer tutucu | Değer |
|---|---|
| `<city_id>` | `bakersfield` |
| `<WORK>` | `C:\temp_private\corteqs\0000_newera\uretim\bakersfield` |
| `<TK>` | `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts` |
| `<PY>` | `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe` |
| `<TMP>` | görev mesajında (yalnız sana ait geçici klasör) |
| `<gorev>` = `<konu>` | görev mesajındaki konu slug'ı |
| `<rol>` | `yazar` |
| `<tarih>` | `2026-10-23` |
| `<bbox>` | `35.1740,35.4680,-119.2853,-118.7527` (yanıtlarda koordinat yok; merge kontrolünde `--bbox=` ile ver) |

Şehir: Bakersfield, Kern County, California, Amerika Birleşik Devletleri. Para birimi USD (tutarlar "USD" ya da "$" ile, kapsamı ve dönemiyle). Kurallar üç düzeyde: federal (ABD), eyalet (California), yerel (Kern County / Bakersfield). Hangi düzeyin kuralı olduğunu karıştırma; başka eyaletin ya da genel ABD uygulamasının California'da da geçerli olduğunu kaynak söylemiyorsa yazma.

## Hitap (B16)
Okura **"sen"** diye hitap et (`<WORK>\_is\yazar\hitap.txt` = `sen`): "başvur", "seç", "kartını al". "Siz" yok; bir kayıtta biçim karışmaz. Bilgi cümlesi kişisiz olabilir. Okuyucu statüye göre ayrılır: ABD vatandaşı değil; çoğu Türk vatandaşı, statüsü vize sahibi (ör. H-1B, F-1), green card sahibi (kalıcı oturum) ya da başvuru sürecinde olabilir. Dar kuralı herkese genelleme.

## Kaynaklar
- Yalnız `<WORK>\_is\yazar\<konu>_kaynaklar.jsonl` dosyasındaki kaynaklar (her satır: `source_id`, `url`, `final_url`, `title`, `publisher`, `text_file`). Bilgiyi yalnız `text_file` metninden al. Bağlantı `url`'si bu dosyadaki `url` ya da `final_url` ile karakteri karakterine aynı olmalı.
- Ek kaynak gerekiyorsa ortak kurallar §4'teki `add_sources` komutuyla ekle (`--subdir snap_<konu>-yazar<sira>`, `--topic <konu>`). Erişimi engelli alan adları için `<WORK>\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu" bölümüne bak; engelli siteyi deneme. Ticari site, Wikipedia, blog, forum, emlak/avukat sitesi kaynak olmaz.
- Keşifte bu konu için kaynağı bulunamayan sorular `<WORK>\_is\kesif\gaps.json`'da; bu bilgileri uydurma, kaynağın yoksa `gaps`'e yaz.

## Sözleşme
`C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\references\contract_digest.md` §0 (genel kurallar) ve §2'nin Yanıtlar, Bağlantılar, Adımlar maddeleri. Anahtar sırası ortak kurallar §3'teki gibi.

## İş
- Kart sayısı 18–26 (hedef ~20). Önce görev mesajındaki 5 "ilk soru"nun her birini bir kartla cevapla. Hedefi değersiz kartla doldurma (aynı kaynaktan türetilmiş benzer kartlar, bir konuyu bölüp çoğaltmak yok).
- `order` görev mesajındaki aralıkta, kayıt sırasıyla artan tamsayı. `featured` en çok 2 kartta `Evet`.
- `stages` her kartta dolu (`before;planning;new;settled` alt kümesi).
- Her kartta 1–3 Bağlantılar satırı; en az biri işlem/bilgi sayfası (başvuru, form, randevu, tarife). "Haritada aç" tek bağlantı olamaz.
- `visual_json` yalnız gerçek süreç/karşılaştırmada; süreç şemasında öğe sayısı = `steps` satır sayısı, değilse `""`.
- Başlıklar (`title`) soru ya da iş adı biçiminde ve pakette benzersiz; mekân adını tek başına başlık yapma (mekân kayıtları ayrıca yazılacak).
- Her sayı, ücret, süre, yaş, tarih, telefon, adres ve kural için iddia defteri satırı (ortak kurallar §5; `field` = bilginin geçtiği sütun: `summary`, `steps`, `documents`, `timing`, `cost`, `note`, `subtitle`, `title`). `quote` = `text_file`'dan kopyala-yapıştır, en çok 200 karakter.
- Okura iş bırakan dolgu ("siteyi kontrol et", "kurumdan doğrula", "değişebilir") ve iç süreç notu yasak (ortak kurallar §6–7).

## Dosyaların (yalnız bunlar)
- `<WORK>\_is\data\parcalar\Yanıtlar.<konu>.jsonl`
- `<WORK>\_is\data\parcalar\Bağlantılar.<konu>.jsonl`
- `<WORK>\_is\claims\<konu>.jsonl`
- yalnız görev mesajı isterse `<WORK>\_is\data\parcalar\Adımlar.<konu>.jsonl`
- Geçici her şey `<TMP>` altında. Başka dosyaya, `_is\data\` altındaki birleşik dosyalara ve pakete yazma.

## Bitirmeden
Ortak kurallar §8: `merge_package` `--data-out <TMP>\birlesik --out <TMP>\birlestir_rapor.json --bbox=35.1740,35.4680,-119.2853,-118.7527` ile; `per_topic.<konu>` = Yanıtlar satır sayın; raporun `issues` ve `quote_miss_list` listelerinde kendi parçana ait bulgu 0. Başka parçaların bulguları seni ilgilendirmez.

## Dönüş (tek satır JSON)
`{"topic_id":"bakersfield:<konu>","cards":N,"links":L,"claims":M,"ilk5":{"1":"<slug>","2":"<slug>","3":"<slug>","4":"<slug>","5":"<slug ya da boş>"},"new_sources":K,"merge_own_issues":0,"gaps":["..."]}`
