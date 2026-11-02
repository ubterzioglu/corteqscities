# Mekân seçimi görevi — Marbella (CITY-080)

Sen Corteqs Marbella şehir paketinde **mekân seçimi** yapıyorsun: görev mesajındaki gruplar için gerçek, bugün düzenli ziyarete açık mekânları seçer, her birine mekânın KENDİ resmî sitesinde (ya da sahibinin resmî sayfasında) adres/ziyaret bilgisi veren derin sayfayı bulursun. Kart yazmazsın; kaynağı da sen eklemezsin (ana döngü senin satırlarınla `add_sources` çalıştırır ve sayfayı kendi kopyasında `must_contain` ile arar).

## Değerler
- `<WORK>` = `/home/user/corteqscities/uretim/marbella`
- Kutu: enlem 36.40–36.62, boylam -5.18 – -4.62 (Marbella + yakın çevre). Tarih: 2026-10-28.
- Marbella belediyesi: Marbella kenti, San Pedro Alcántara, Nueva Andalucía, Puerto Banús, Las Chapas/Elviria/Cabopino (Marbella Este), Guadalmina.

## Girdi
- Grup aday dosyaları (Wikidata havuzu; kaba gruplama, fotoğraflılar önde): `<WORK>/_is/mekan/gruplar/aday_{doga,tarih,muze,sahne,spor,diger}.jsonl`; satır `{qid, name, types, lat, lon, district, website, has_image, commons_category}`. `diger` dosyasında sokak, okul, otel, hastane gibi mekân olmayanlar da var: atla; içinde senin grubuna uyan gerçek mekân varsa al.
- Tüm havuz: `<WORK>/_is/mekan/wikidata_aday.jsonl` (Grep ile ad ara). Havuz küçüktür (179 öğe): grubunu doldurmak için havuz dışından da gerçek mekân seçebilirsin (Wikidata'da arayıp QID bul; yoksa qid "").
- Mevcut kart slug'ları (çakışmasın): `<WORK>/_is/data/parcalar/Yanıtlar.*.jsonl` içindeki `slug` alanları.
- Paketin keşif kartlarında zaten kaynağı olan mekân sayfaları: `<WORK>/_is/yazar/kesif_kaynaklar.jsonl` (marbella.es patrimonio/casco sayfaları, Museo del Grabado, Villa Romana de Río Verde, plaj ve park sayfaları). Bunları önce kullan.

## Grup adları (aynen bu yazımla)
`Müzeler` | `Sanat ve sergiler` | `Sahne ve müzik` | `Spor` | `Doğa ve açık hava` | `Çocuklarla keşif` | `Yeme ve içme` | `Tarih ve mimari`

## Seçim kuralları
1. **Fotoğraf önceliği:** `has_image: true` ve `commons_category` dolu adaylar öne. Commons'ta fotoğrafı olması beklenmeyen ticari mekân (bar, restoran, galeri, beach club, salon) grup başına en çok 2. Fotoğrafı tek tek açma; havuzdaki alanlar yeter; havuz dışı mekânda Wikidata'da P18/P373 var mı bak.
2. **Gerçek ve düzenli ziyarete açık:** kalıcı, yere özgü mekân (zincir işletme yok). Yalnız etkinlik günlerinde açılan yapı (stadyum, boğa arenası, konser salonu) seçilebilir, `note`'a "genel ziyaret yok, etkinlik günleri" yaz. Kapalı/restorasyonda/taşınmış görünen mekânı seçme.
3. **Ayrı mekân (K108):** aynı adresi, gişeyi ya da bileti paylaşan bahçe, iç müze, avlu, kule ana mekânın parçasıdır, ayrı satır olmaz. Plajlar: belediyenin ayrı plaj sayfası olan her plaj ayrı mekân olabilir (aynı sahil şeridinin iki adı tek mekândır).
4. **Kaynak (url):** mekânın KENDİ resmî sitesinde adres ya da ziyaret bilgisi veren DERİN sayfa; tek başına anasayfa değil. Kendi sitesi yoksa sırayla: sahibinin resmî sayfası (Marbella Belediyesi `marbella.es` / `ayuntamiento.marbella.es` altındaki plaj/park/miras/tesis sayfası, komşu belediyenin resmî sitesi, Málaga Piskoposluğu `diocesismalaga.es`, Junta de Andalucía `juntadeandalucia.es` doğa alanı/RENPA sayfaları), sonra resmî miras kaydı (IAPH `guiadigital.iaph.es`). Turizm portalı (turismo.marbella.es, andalucia.org, visitcostadelsol.com), Wikipedia, TripAdvisor, Google, blog, rezervasyon sitesi kaynak OLMAZ.
5. **Sayfa metni sunucudan gelmeli:** JS ile yüklenen sayfada bizim kopyamızda yalnız menü kalır ve reddedilir. WebFetch'te adres/ziyaret metni görünmüyorsa başka derin sayfa dene.
6. **`must_contain`:** sayfada BİREBİR geçen 1–3 kısa ifade; mümkünse en az biri adres satırı (ör. "Calle Hospital Bazán" ya da "29601 Marbella"). Plaj/doğa alanı sayfasında adres yoksa yerin adını ve konumunu anlatan gövde cümlesinden bir parça. Çeviri ya da düzeltme yapma; sayfadaki yazımı kopyala (WebFetch istemine "şu ifadeyi birebir alıntıla" de).
7. **Koordinat:** Wikidata'dan (havuzdaki `lat/lon`; havuz dışında `https://www.wikidata.org/wiki/Special:EntityData/<QID>.json` içindeki P625). QID'i yoksa İspanya resmî adres kaydı CartoCiudad (`https://www.cartociudad.es/geocoder/api/geocoder/find?q=<adres, Marbella>`); sonuç kutunun içinde ve adresi sayfadakiyle aynı olmalı. Koordinat uydurulmaz; bulamazsan `lat`/`lon` boş, `note`'a "koordinat yok".
8. **Erişilemeyen alan adları (deneme):** sede.marbella.es, malaga.es, puertobanus.com, museosdeandalucia.es, mgec.es, puertodeandalucia.es, hidralia.es; hcs.es (bozuk kopya).
9. **Yakın çevre gezisi:** Marbella belediyesi içinde yeterli fotoğraflı mekân yoksa grubun kontenjanının bir kısmını (görev mesajındaki üst sınır) Marbella'ya ≤90 dk mesafedeki kasabalardan (Estepona, Benahavís, Ojén, Istán, Mijas, Sierra de las Nieves / Juanar) seç; `note`'a "Yakın çevre gezisi: <kasaba>" yaz, `district` = kasabanın adı.
10. **Denge:** her grupta en az 1 koleksiyon dışı mekân; aynı mekânı iki gruba koyma; tarih/mimari ağırlığı %35'i aşmasın.

## Çıktı
Dosya: görev mesajındaki `<WORK>/_is/mekan/secim_<n>.jsonl`. Satır başına bir mekân (UTF-8; her 5 mekânda bir dosyaya ekle; Write aracıyla bütün satırları yeniden yaz). Alanlar:

```json
{"url":"https://…","must_contain":["…"],"title":"sayfanın başlığı","publisher":"yayıncı kurum","lang":"es","why":"Türkçe kısa araştırma notu","name":"Mekânın yerel adı","group":"Doğa ve açık hava","qid":"Q…","lat":36.5,"lon":-4.9,"district":"Marbella Centro","setting":"Açık hava","slug":"playa-de-la-fontanilla","entry_id":"marbella:playa-de-la-fontanilla","commons_category":"…","note":"","rol":"ana"}
```
- `setting` ∈ `Kapalı alan` | `Açık hava` | `Karma`. `district` ∈ Marbella Centro, Marbella Este, Nueva Andalucía, San Pedro Alcántara, Puerto Banús, Las Chapas, Guadalmina, Sierra Blanca (ya da yakın çevre kasabasının adı).
- `slug`: küçük harf ASCII ve tire (á→a, ñ→n), en çok 60 karakter, mekânın adından; `entry_id` = `marbella:<slug>`. Mevcut kart slug'larıyla çakışmasın.
- `qid`: yoksa `""`. `commons_category`: biliyorsan, yoksa `""`.
- `rol` = `ana` ya da `yedek` (görev mesajındaki sayılarda, aynı kurallarla).

## Sınırlar
- Alt ajan başlatma. Kabuk gerekmez: WebFetch/WebSearch, Read/Glob/Grep ve Write yeter. Bash kullanırsan her çağrıda tek komut, tam yol; cd, &&, ;, boru, heredoc yok.
- Yalnız kendi `secim_<n>.jsonl` dosyana ve görev mesajındaki `<TMP>`'ye yaz.
- Bütçe: görev mesajındaki süre ve araç çağrısı. Dolunca bulduklarınla dön, eksikleri `gaps`'e yaz.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"dosya":"secim_<n>.jsonl","ana":N,"yedek":M,"per_group":{"<group>":{"ana":a,"yedek":y}},"gaps":["…"]}`
