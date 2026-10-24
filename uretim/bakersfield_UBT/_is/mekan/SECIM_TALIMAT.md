# Mekân seçimi talimatı (Bakersfield, Kaliforniya, ABD · CITY-901)

Görevin: verilen 2 grup için Bakersfield'da Türkçe konuşan yeni gelene önerilecek gerçek, bugün açık ve düzenli ziyarete açık mekânları seçmek; her mekân için mekânın **kendi resmî sitesinde** adres/ziyaret bilgisi veren derin sayfayı ve o sayfada birebir geçen adresi (`must_contain`) bulmak. Metin yazmıyorsun.

## Şartlar
- Gerçek, kalıcı, şehre özgü mekân; bugün açık ve düzenli ziyarete açık (kapanmış, taşınmış, yıkılmış, yalnız özel etkinlikte açılan yer yok). Kendi sitesinin varlığı açık olduğunun kanıtı sayılmaz; açıklık ayrıca denetlenecek, sen yine de kapalı olduğunu gördüğün yeri seçme.
- Konum: Bakersfield'da (posta adresi Bakersfield, CA) ve koordinatı şu kutunun içinde: enlem 35.1740–35.4680, boylam −119.2853 – −118.7527 (Census TIGERweb şehir sınırı kutusu + 0,02° pay). Kutu dışı (Shafter, Taft, Tehachapi, Kern Nehri kanyonu vb.) yok.
- Zincir eğlence işletmesi, AVM, sinema zinciri, otel, okul, hastane, mezarlık grup doldurmak için seçilmez. Tarih/mimari ağırlığı abartılmaz.
- Her grupta en az 1 "koleksiyon dışı" mekân (müze/galeri gibi koleksiyonu olmayan; ör. park, pazar, restoran, salon). `collection` alanını yazar sonra doldurur; sen `note`'ta "koleksiyon var/yok" belirt.
- Kaynak: mekânın **kendi** resmî sitesinin adres/ziyaret/iletişim sayfası (anasayfa adres taşıyorsa anasayfa olur ama derin sayfa tercih). Kamu parkları için Kern County Parks (kerncountyparks.org) ya da ilgili resmî kurum sayfası. Kullanma: Wikipedia, Yelp, TripAdvisor, Google Maps, Facebook/Instagram, blog, haber sitesi, rezervasyon siteleri. Şehir turizm bürosunun (visitbakersfield.com) mekân sayfası yalnız son çare (JS ile yüklenip ince metin verebilir) ve yine `must_contain` şartıyla.
- Bilinen engelli/erişilemeyen alan adları `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\kesif\KESIF_TALIMAT.md` "Bilinen erişim durumu" bölümünde (ör. bakersfieldcity.us). Bakersfield Museum of Art ve Buck Owens Crystal Palace siteleri keşifte 403/zaman aşımı verdi; yeniden dene, olmazsa başka resmî sayfa ya da başka mekân.
- Commons'ta fotoğrafı olması muhtemel mekânlar tercih edilir (Wikidata'da P18/P373 olanlar; havuzdaki `has_image`/`commons_category`). Fotoğrafı tek tek açma.

## Aday havuzu
`C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\mekan\wikidata_aday.jsonl` (74 öğe; alanlar `qid, name, lat, lon, types, district, website, has_image, commons_category`). Havuz zayıf: çoğu kapanmış sinema, mahalle, okul. Grubunun mekânlarının çoğunu WebSearch ile mekânın resmî sitesinden bulacaksın. Havuzda olmayan mekânın Wikidata öğesi varsa (WebSearch "site:wikidata.org <ad> Bakersfield") QID'ini yaz.

## Koordinat
- Yalnız iki kaynaktan: (1) mekânın Wikidata öğesindeki P625, (2) ABD resmî adres kaydı **US Census Geocoder** (mekânın resmî sitesindeki adresle):
  ```powershell
  & 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe' -c "import json,urllib.request,urllib.parse,sys; u='https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?'+urllib.parse.urlencode({'address':sys.argv[1],'benchmark':'Public_AR_Current','format':'json'}); m=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'corteqs-city-pack/1.0'}),timeout=30))['result']['addressMatches']; print(json.dumps([(x['matchedAddress'],x['coordinates']) for x in m]))" "3801 Chester Ave, Bakersfield, CA 93301"
  ```
  `x` = boylam, `y` = enlem. Eşleşme yoksa ve Wikidata koordinatı da yoksa `lat`/`lon` boş bırak (uydurma, haritadan okuma yok). `note`'a koordinat kaynağını yaz (`koordinat: wikidata` ya da `koordinat: census geocoder`).
- Wikidata koordinatı ile resmî adres çok farklıysa (≥1 km) Census'u esas al ve `note`'a yaz.

## Kanıt ifadesi ve ZORUNLU yerel deneme
- `must_contain` = mekânın sayfasındaki birebir adres satırı (ör. `"3801 Chester Ave"`), gerekirse ikinci ifade olarak sayfadaki saat/ziyaret cümlesi. Büyük/küçük harf ve boşluk önemsiz; kelimeler ve noktalama birebir.
- Listeye yazmadan önce bizim indiricimizle dene (WebFetch birebir metni garanti etmez):
  ```powershell
  & 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe' 'C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts\fetch_snapshot.py' --urls '<klasör>\urls.txt' --out-dir '<klasör>\snap_<n>' --cache-dir '<klasör>\cache' --must-contain '<klasör>\mc.jsonl'
  ```
  `urls.txt` satır başına adres; `mc.jsonl` satırları `{"url": "...", "must_contain": ["..."]}` (UTF-8). `<klasör>\snap_<n>\index.jsonl`'de yalnız `status` 200, `flags` içinde `fetch_failed`/`thin_text`/`soft_404` yok ve `evidence.missing` boş olan adresler listeye girer. İfade tutmadıysa `snap_<n>\<text_file>` metnini aç, adresi oradaki yazımıyla al (ör. "Ave." / "Avenue"), yeniden dene (yeni `snap_<n>`, aynı `cache`).

## Kimlik
- `slug`: mekân adından küçük harf ASCII ve tire (ör. `kern-county-museum`); Türkçe harf yok; özgül; en çok 60 karakter. `entry_id` = `bakersfield:<slug>`. Konu kartlarının slug'ları soru biçimindedir; mekân adından türeyen slug genelde çakışmaz. Aynı mekânı iki kez yazma.

## Çıktı
`C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\mekan\secim_<n>.jsonl` (n = görev mesajındaki numara), UTF-8, satır başına:
```json
{"url":"...","must_contain":["..."],"publisher":"<mekân/kurum adı>","why":"<Türkçe: neden yeni gelene değerli>","name":"<özgün ad>","group":"<grup adı, aşağıdaki listeden aynen>","qid":"<Q.. ya da boş>","lat":35.0,"lon":-119.0,"district":"<semt/bölge: Downtown, East Bakersfield, Northwest, Southwest, Northeast, Westchester, Oleander-Sunset, Rosedale … — adresten>","setting":"Kapalı alan|Açık hava|Karma","slug":"...","entry_id":"bakersfield:<slug>","commons_category":"<varsa>","note":"<koordinat kaynağı; koleksiyon var/yok; varsa kısa uyarı>"}
```
Grup adları (aynen): `Müzeler`, `Sanat ve sergiler`, `Sahne ve müzik`, `Spor`, `Doğa ve açık hava`, `Çocuklarla keşif`, `Yeme ve içme`, `Tarih ve mimari`. Koordinat yoksa `lat` ve `lon` alanlarını `""` yaz.

## Sayı
- Grup başına hedef 15. Şehirde şartları sağlayan 15 mekân yoksa daha az yaz (zorla doldurma; zayıf aday yok) ve eksiği `gaps`'e yaz. Diğer grubun zenginse oraya en çok 3 fazla ekleyebilirsin (o grupta en çok 18).
- Bir mekân yalnız bir gruba girer.

## Bütçe ve dönüş
- En çok 40 dakika / 120 araç çağrısı. Dolunca bulduklarınla dön.
- Yalnız kendi geçici klasörüne ve kendi `secim_<n>.jsonl` dosyana yaz.
- Son mesajın yalnız tek satır JSON: `{"n":<n>,"groups":{"<grup>":<sayı>,...},"with_qid":<n>,"with_coords":<n>,"tested_ok":<n>,"gaps":["<grup>: ..."]}`
