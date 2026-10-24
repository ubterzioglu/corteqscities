# Alt ajan: yer ve sayfa yazarı

Mekânlar, Mahalleler, Sözlük, SayfaAlanları, Şehir ve Rotalar satırlarını yazıyorsun. Ana döngü sana bir parça verir (ör. iki mekân grubu, mahalleler, sözlük, sayfa alanları ile şehir satırı, rotalar); yalnız onu yaz. Önce aynı klasördeki `ortak-kurallar.md`'yi oku: yer tutucular, alan biçimleri, Bağlantılar biçimi, iddia defteri, kaynak kuralları, yasaklar ve iç denetim notu yasağı aynen geçerli. `mekan-yazari.md`'deki genel kurallar da geçerli; yol veya biçim çelişirse bu dosya ile ortak kurallar esastır.

## Girdi (ana döngü verir)
- Görev: sekme(ler), adet, `order` aralığı, `<gorev>` (ör. `m1`, `mahalle`, `sozluk`, `sayfa`, `rota`), `<konu>`.
- Mekân planı (mekân yazarına): satır başına `name, group, qid, lat, lon, district, setting, official_url, slug, entry_id, source_id`. `slug`, `entry_id`, `group`, `district`, `setting`, `lat`/`lon` plandaki gibi AYNEN kullanılır (fotoğraf araması bu kimliklere bağlı).
- Kaynak dizini `<WORK>\_is\kaynak_dizini.jsonl` (`source_id`, `url`, `final_url`, `title`, `publisher`, `text_file`).
- Mevcut kayıtlar: `<WORK>\_is\data\` altındaki birleşik `Yanıtlar.jsonl`, `Mekânlar.jsonl`, `Mahalleler.jsonl` (varsa) ve `<WORK>\_is\data\parcalar\` altındaki öteki parçalar; slug/başlık çakışması, rota durakları ve sayfa alanı bağları için.

## Yazacağın dosyalar
- Satırlar: `<WORK>\_is\data\parcalar\<Sekme>.<gorev>.jsonl`, yalnız görevindeki sekmeler (ör. `Mekânlar.m1.jsonl`).
- Mekân ve mahalle için: `<WORK>\_is\data\parcalar\Bağlantılar.<gorev>.jsonl`, her kayda en az 1 satır.
- İddia defteri: `<WORK>\_is\claims\<gorev>.jsonl`.
- Şehir satırı ve SayfaAlanları pakette bir kez bulunur; yalnız bu görev verilen ajan yazar.

## Mekânlar
Anahtar sırası (Mekânlar):
```text
entry_id, city_id, slug, title, subtitle, summary, keywords, stages, source_ids, reviewed_on, order, featured, editorial_status, group, district, setting, location, latitude, longitude, visit_status, note, collection, media_key
```
- `group`: `Müzeler` | `Sanat ve sergiler` | `Sahne ve müzik` | `Spor` | `Doğa ve açık hava` | `Çocuklarla keşif` | `Yeme ve içme` | `Tarih ve mimari`.
- `setting`: `Kapalı alan` | `Açık hava` | `Karma`.
- `title`: yerin gerçek/resmî adı, özgün yazımıyla. `subtitle` (en çok 160): ne olduğu ve nerede, kısa. `summary`: o yere özgü 2–4 cümle; ne olduğu, adres veya semt, açık günler ve saatler, ücret, kimlere uygun (kaynakta ne varsa).
- `district`: semt veya ilçe (plandaki). `location`: kaynaktaki açık adres (sokak, numara, posta kodu).
- `latitude`/`longitude`: plandaki sayılar (Wikidata ya da ülkenin resmî adres kaydı), AYNEN; ikisi birlikte sayı ya da ikisi `""`; `<bbox>` içinde. Uydurma koordinat yok; iki mekâna kendin aynı koordinatı verme. Plan iki mekâna aynı koordinatı veriyorsa (aynı bina ya da meydan) ya da kendi kontrolünde bir kaydında `coord_range` çıkıyorsa koordinatı değiştirme, kaydırma ya da silme: plandaki gibi bırak ve `open`'a yaz.
- `visit_status`: `""`. Yalnız kaynak yerin şu an kapalı, tadilatta veya taşınmış olduğunu söylüyorsa kısa durum ("Yenileme nedeniyle kapalı") ve defter satırı. "Ziyaret durumunu kontrol et" gibi kalıp yazılmaz.
- `note`: yalnız o yere ait pratik bilgi (ücretsiz gün, çanta kuralı, erişilebilirlik, geçici sergi veya tadilat); yoksa `""`. Her mekânın notu kendinedir.
- `collection` = `Hayır` (tek, gerçek yer). `Evet` yalnız ana döngünün istediği derleme/dizin kaydında; her grupta en az bir `Hayır` mekân şart.
- `media_key` = `""` (fotoğraf bağı Fotoğraflar sekmesinde kurulur).
- Kapanmış veya taşınmış yer yazılmaz; `gaps`'e gider.

Mekân seçimi veya yedek (ana döngü isterse):
- Bugün açık, gerçek, şehir sınırları içinde; kendi resmî sitesinde adres/ziyaret bilgisi veren alt sayfası var; Commons'ta fotoğrafı olması muhtemel (Wikidata P18/P373). Fotoğrafsız kalacak yeri seçme.
- Denge: 8 grubun her biri; büyük ve küçük; ücretli ve ücretsiz; merkez ve farklı semtler; aile ve yetişkin; kapalı ve açık. Sayıyı restoran veya anıtla doldurma; zincir ya da ticari eğlence işletmesini yalnız grupta başka seçenek yoksa al.
- Kaynağı reddedilen yer için önce yerin kendi sitesinde başka sayfa ara (`must_contain` = adres satırı) ve `add_sources` ile ekle; olmazsa aynı gruptan yedek yer seç (yeni slug, mevcutlarla çakışmasın) ve kararı dönüşte `open`'da bildir.

## Mahalleler
Anahtar sırası (Mahalleler):
```text
entry_id, city_id, slug, title, subtitle, summary, keywords, stages, source_ids, reviewed_on, order, featured, editorial_status, location, tags, compare_json, note, media_key
```
- `location`: bölgenin kapsamı sözle (hangi semtler, hangi sınırlar), kaynaktan. `tags`: 3–5 belirgin özellik, satır başına bir tane.
- `compare_json`: JSON nesnesi metni, en az 4 başlık; değerler boş olmayan düz metin (iç içe nesne, sayı, `null` yok). Şehrin BÜTÜN mahallelerinde aynı başlıklar kullanılır (ana döngü verir), ör. `{"Ulaşım":"…","Yaşam ritmi":"…","Konut tipi":"…","Yeşil alan":"…"}`. Her değer kaynaklıdır; defterde `field` = `compare.<Başlık>`.
- Resmî kaynak bir başlığı karşılamıyorsa o başlığı kaynaklı başka somut bilgiyle doldur (ulaşım işletmecisinin hat sayfası, belediyenin park sayfası gibi); ticari siteye başvurma.
- Güvenlik, gelir veya etnik köken hakkında kanıtsız genelleme, "en iyi mahalle", kira tahmini veya garantisi yok; öznel izlenim ölçülmüş bilgi gibi sunulmaz.
- `note`: o mahallede yaşam veya ev seçimiyle ilgili özgül not, yoksa `""`. `media_key` = `""`.

## Sözlük
Anahtar sırası (Sözlük):
```text
term_id, city_id, term, definition, source_ids, reviewed_on, order, editorial_status
```
- `term_id` = `<city_id>:term:001` … (3 hane, ana döngünün verdiği başlangıçtan); `order` 1..N, sekmede benzersiz.
- `term`: okuyucunun konut, kayıt, ulaşım, sağlık, eğitim ve günlük yaşamda karşılaşacağı gerçek yerel terim, yerel yazımıyla. Genel sözlük kelimesiyle sayı doldurulmaz; aynı terimin iki yazılışı tek maddedir.
- `definition`: 1–3 cümle Türkçe; ne olduğu ve okuyucunun onunla nerede karşılaşacağı. `source_ids` boş olamaz; tanımdaki her kural ve sayı defterde (`term_id` sahipli).

## SayfaAlanları
Anahtar sırası (SayfaAlanları):
```text
field_id, city_id, key, label, value_type, value, reviewed_on
```
- Aşağıdaki 23 anahtar, her biri bir kez. `field_id` = `<city_id>:field:<key>`. `value_type` ∈ `Metin` | `Sayı` | `Mantıksal` | `JSON`; `JSON` değeri JSON dizisinin METNİDİR.
- Ayrılmış anahtarlar yazılmaz: `routes`, `glossary`, `directory`, `currency`, `currency_symbol`, `currency_label`, `reviewed_on`, `weather`. Berlin'in `_db_*` ve `expansion_version` alanları kopyalanmaz.
- `entry` ve `advice_entry` değerleri slug'dır (`<city_id>:` öneki yok) ve bu şehrin Yanıtlar, Mekânlar veya Mahalleler kayıtlarında bulunur.
- Metinler şehre özgü Türkçedir; Berlin'in ya da başka şehrin metni, acil numarası, para birimi kopyalanmaz. Metindeki her sayı, süre ve numara defterde (`field_id` sahipli, `field` = `value`).

| key | value_type | label | İçerik |
|---|---|---|---|
| `hero_kicker` | Metin | Üst küçük başlık | kısa üst satır (ülke · şehir rehberi) |
| `hero_accent` | Metin | Ana başlığın vurgu metni | kısa vurgu cümlesi |
| `hero_note` | Metin | Kapak altı kısa açıklama | rehberin ne sunduğu, tek cümle |
| `topic_title` | Metin | Bilgi bölümü başlığı | bölüm başlığı |
| `topic_intro` | Metin | Bilgi bölümü açıklaması | bölümün kısa tanıtımı |
| `journey_title` | Metin | İlk adımlar başlığı | bölüm başlığı |
| `journey_intro` | Metin | İlk adımlar açıklaması | yol haritasıdır, zorunlu sıra değildir; yasal süre varsa kaynaklı |
| `neighborhood_title` | Metin | Mahalleler başlığı | bölüm başlığı |
| `neighborhood_intro` | Metin | Mahalleler açıklaması | semtlerin neye göre karşılaştırıldığı |
| `explore_title` | Metin | Keşif başlığı | bölüm başlığı |
| `explore_intro` | Metin | Keşif açıklaması | keşif bölümünün kısa tanıtımı |
| `sources_note` | Metin | Kaynak ve kontrol açıklaması | bilgilerin hangi tür kurumlardan derlendiği; kişisel danışmanlığın yerine geçmediği |
| `photo_credit` | Metin | Fotoğraf bölümü genel atıf notu; kare atıflarının yerine geçmez | atıfların her karenin altında olduğu |
| `arrival_note` | Metin | Kişisel takvimin yasal süre yerine geçmediğini açıklayan yerel not | yasal süreler kaynaklı ve defterde |
| `emergency_url` | Metin | Yerel resmî acil yardım açıklamasına bağlantı | resmî https sayfası (kaynak dizininde) |
| `pharmacy_url` | Metin | Yerel resmî nöbetçi eczane/eczane bulma bağlantısı | resmî https sayfası (kaynak dizininde) |
| `advice_entry` | Metin | Danışma kartının bu şehirdeki içerik slugı | yeni gelenin ilk başvuracağı danışma kartının slug'ı |
| `facts` | JSON | En az 4 kısa bilgi; her biri aynı şehirde bir içerik slugına gider | en az 4 × `{"value","label","entry"}`; her `value` defterde ve `entry` kartında da yazılı |
| `quick_links` | JSON | En az 3 hızlı bağlantı; aynı şehirde içerik slugına gider | en az 3 × `{"label","entry"}`; anahtar `entry`, `url` DEĞİL |
| `timeline` | JSON | En az 4 kişisel hazırlık hatırlatıcısı; offset taşınma tarihine göre gün | en az 4 × `{"title","note","offset"}` (+ isteğe bağlı `entry`); `offset` tamsayı, -730..730; kişisel hatırlatıcıdır, yasal süre değil |
| `budget_fields` | JSON | Bütçe hesaplayıcısının 10 alanı; tutar değil Türkçe başlıklar | tam şu 10 anahtar birer kez: `income`, `rent`, `bills`, `food`, `transport`, `health`, `leisure`, `other`, `deposit`, `moving`; `{"key","label"}`, tutar yok |
| `place_groups` | JSON | Keşif filtresinin 8 sabit anahtarı ve Türkçe etiketleri | tam şu 8 anahtar birer kez: `museum`, `art`, `stage`, `sport`, `nature`, `family`, `food`, `history`; `{"key","label"}` |
| `emergency` | JSON | Yerel resmî kaynaktan doğrulanmış acil telefon kayıtları | en az 1 × `{"tel","number","label","desc"}`; `tel` boşluksuz (`^\+?[0-9*#]{2,20}$`), `number` görünen biçim; numara yalnız resmî kaynaktan |

- `place_groups` etiketleri Mekânlar grup adlarıdır: museum = Müzeler, art = Sanat ve sergiler, stage = Sahne ve müzik, sport = Spor, nature = Doğa ve açık hava, family = Çocuklarla keşif, food = Yeme ve içme, history = Tarih ve mimari.
- Yapı örneği (içerik değil): `[{"value":"…","label":"…","entry":"kart-slugi"}]`.

## Şehir (tek satır)
Anahtar sırası (Şehir):
```text
city_id, name, country, country_code, region, kind, title, intro, currency, currency_symbol, currency_label, language, timezone, latitude, longitude, coordinate_source_url, coordinate_checked_on, coordinate_note, source_url, source_checked_on, source_position, reviewed_on, priority, aliases, locality, tagline, directory_order, forecast_url, provider_url, forecast_label, hero_photo_id, editorial_notes, editorial_status
```
- Şablondaki mevcut satırı dök:
  ```powershell
  & <PY> <TK>\xlsx_dump.py <WORK>\_is\sablon.xlsx --out-dir <TMP>\sablon --sheets Şehir
  ```
  `<TMP>\sablon\Şehir.jsonl` yalnız dolu alanları ve `_row`'u içerir. Satırı 33 anahtarın tamamıyla, yukarıdaki sırayla yeniden kur: dökümdeki değerleri AYNEN al (şablonu hazırlayanın verisi; sorunlu görürsen `open`'a yaz), `_row`'u at.
- Boş alanlar için:
  - `title` (en çok 160) ve `intro` (en çok 350): şehre özgü Türkçe; `title`, `intro` ve `tagline` aynı metni tekrarlamaz.
  - `currency` ISO kodu (`^[A-Z]{3}$`); `currency_symbol` ve `currency_label` dolu; `language` yerel dilin Türkçe adı; `timezone` geçerli IANA adı (ör. `Europe/Berlin`).
  - `forecast_url`: şehrin resmî ya da güvenilir hava tahmini sayfası; `provider_url`: tahmini yayınlayan kurum; `forecast_label`: bağlantı metni. Anlık hava değeri yazılmaz.
  - `hero_photo_id` = `""` (fotoğraf fazı bir `Kapak` fotoğrafına bağlar); `editorial_notes` = `""`; `editorial_status` = `Taslak`; `reviewed_on` = `<tarih>`; geri kalan isteğe bağlı alanlar kaynağın yoksa `""`.
- `latitude`/`longitude` sayı; `source_position`, `priority` tamsayı (en az 0); `directory_order` tamsayı ya da `""`; tarihler `YYYY-MM-DD`.
- Defter: `intro`, `tagline` gibi alanlardaki olgular için `entry_id` = `<city_id>` sahipli satır (`field` = Şehir sütunu).

## Rotalar
Anahtar sırası (Rotalar):
```text
route_id, city_id, title, tag, stops, stop_entry_ids, entry_id, note, reviewed_on, source_ids, order, editorial_status
```
- `route_id` = `<city_id>:route:001` …; `order` 1..N, sekmede benzersiz.
- `stop_entry_ids`: `;` ile 2–8 FARKLI gerçek Mekânlar `entry_id`'si (`<WORK>\_is\data\parcalar\Mekânlar.*.jsonl`). `stops`: aynı sırayla durakların başlıkları, satır başına bir tane. `entry_id` = ilk durak.
- "Kahve molası", "dönüş" gibi genel duraklar durak sayılmaz; gerekiyorsa `note`'a yazılır.
- `tag`: `<süre> · <tema>` (ör. `Yarım gün · Kültür`). `title`: rotayı ayırt eden Türkçe ad.
- `note`: başlangıç ve bitiş, yürüyüş veya toplu taşıma, mesafe ve süre varsayımı, açık günler, bilet ihtiyacı; yalnız durak kayıtlarındaki ve kaynaklardaki bilgiyle (defterde `route_id` sahipli, `field` = `note`).
- Uygulanabilirlik: ardışık duraklar arası mesafeyi koordinatlardan hesapla (haversine, betik `<TMP>`'de). Yürüyüş rotasında ardışık iki durak 3 km'den yakın; rota bir durağın kapalı olduğu günü önermez; haritada uzak iki yeri komşu gibi bağlamaz.
- Çeşitlilik: ilk gün tanışma, kültür ve tarih, sanat ve müze, açık hava, aile, yeme-içme ve mahalle, spor, yağmurlu gün, ücretsiz keşif; farklı semtler.
- `source_ids`: nottaki bilgilerin kaynakları (durak kayıtlarının kaynakları); boş olamaz.

## Kaynak (yer yazarına özgü)
- Mekân bilgisinin kaynağı mekânın KENDİ resmî sitesindeki alt sayfa (ziyaret, iletişim, bilet) ya da belediye veya resmî kurum sayfasıdır.
- Şehir turizm portalı (şehrin tanıtım sitesi: `visit<şehir>`, `thisis<şehir>`, `<şehir>365` türü) mekân ve mahalle kaynağı olarak kullanılmaz: sayfaları çoğu zaman JavaScript ile yüklenir, kopyada yalnız menü kalır (pilotta reddedilen 19 mekân kaynağının 15'i ince metindi, çoğu bu tür portal sayfasıydı) ve tanıtım dilindedir. Tek istisna: yerin kendi sitesi ve belediye sayfası yoksa ve ana döngü görev mesajında açıkça izin verdiyse; o zaman da `add_sources` `must_contain` kanıtıyla kabul etmeden kullanılmaz.
- Ticari siteler hiçbir alanda kaynak değildir (ortak kurallar §4); pilotta mahalle kartlarında expat portalları kullanıldı ve açık konu oldu. Bilet üçüncü taraf bir sitede satılıyorsa yerin resmî sitesindeki bilet sayfasını bağla.
- Yeni adres: ortak kurallar §4'teki `add_sources` komutu (`--subdir snap_<gorev>-<rol><sira>`: yazarsan `<rol>` = `yazar`, her koşu yeni klasör; `--topic <konu>`). `source_urls` bırakılmaz.

## Bitirmeden
- Ortak kurallar §8'deki `merge_package` kontrolü (çıktılar `<TMP>`'ye).
- Ayrıca kendin say: her mekân ve mahallede en az 1 bağlantı; `compare_json` başlıkları bütün mahallelerde aynı; SayfaAlanları 23 anahtar; rotalarda durak sayısı, sırası ve ardışık mesafeler.

## Dönüş (tek satır JSON)
`{"part":"<gorev>","rows":{"<Sekme>":N},"actions":M,"claims":K,"new_sources":a,"rejected_sources":b,"own_issues":c,"gaps":["kaynakta bulunamayan ama okuyucu için önemli bilgi"],"open":["ana döngünün karar vermesi gereken konu"]}`
