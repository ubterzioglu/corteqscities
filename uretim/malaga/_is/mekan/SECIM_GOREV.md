# Mekân seçimi görevi — Málaga (CITY-075)

Sen Corteqs Málaga şehir paketinde **mekân seçimi** yapıyorsun: görev mesajındaki gruplar için gerçek, bugün düzenli ziyarete açık mekânları seçer, her birine mekânın KENDİ resmî sitesinde adres/ziyaret bilgisi veren derin sayfayı bulursun. Kart yazmazsın; kaynağı da sen eklemezsin (ana döngü senin satırlarınla `add_sources` çalıştırır ve sayfayı kendi kopyasında `must_contain` ile arar).

## Değerler
- `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\malaga`
- `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- Kutu (bbox): enlem 36.57–36.87, boylam -4.60 – -4.28. Kutu dışındaki mekân seçilmez (yakın çevre gezisi yok).
- Tarih: 2026-10-27.

## Girdi
- Grup aday dosyaları: `<WORK>\_is\mekan\gruplar\aday_<grup>.jsonl` (Wikidata havuzu; satır `{qid, name, types, lat, lon, district, website, has_image, commons_category}`; fotoğraflılar önde). Gruplama kaba bir script işidir: dosyada mekân olmayan satır (mahalle, sokak, heykel, çeşme) varsa atla; başka grubun dosyasında senin grubuna uyan mekân varsa alabilirsin.
- Tüm havuz: `<WORK>\_is\mekan\wikidata_aday.jsonl` (Grep ile ad ara). Havuzda olup gruba düşmemiş önemli adaylar: Centre Pompidou Málaga (Q16545730, Sanat), Colección del Museo Ruso (Q20016787, Sanat), Museo Alborania-Aula del Mar (Q5711821, Çocuk — bugün açık mı dikkat), Muelle Uno (Q117477770, Doğa ve açık hava), Estadio La Rosaleda (Q695879, Spor), Mercado de Atarazanas (Q106989774, Yeme ve içme).
- Mevcut slug'lar (çakışmasın): `<WORK>\_is\data\parcalar\Yanıtlar.*.jsonl` içindeki `slug` alanları.

## Grup adları (aynen bu yazımla) ve kontenjan
| grup anahtarı | `group` değeri | ana | yedek |
|---|---|---|---|
| tarih | Tarih ve mimari | 28 | 4 |
| doga | Doğa ve açık hava | 24 | 3 |
| muze | Müzeler | 18 | 2 |
| sanat | Sanat ve sergiler | 12 | 2 |
| sahne | Sahne ve müzik | 10 | 2 |
| spor | Spor | 10 | 2 |
| cocuk | Çocuklarla keşif | 10 | 2 |
| yeme | Yeme ve içme | 8 | 2 |

Hedefe ulaşamazsan uydurma ya da zayıf mekânla doldurma: bulduğun kadar yaz, eksiği `gaps`'e koy.

## Seçim kuralları
1. **Fotoğraf önceliği:** `has_image: true` ve `commons_category` dolu adaylar öne. Commons'ta fotoğrafı olması beklenmeyen ticari mekân (bar, tablao, galeri, salon, restoran) grup başına en çok 2. Fotoğrafı tek tek açma; havuzdaki alanlar yeter.
2. **Gerçek ve düzenli ziyarete açık:** kalıcı, şehre özgü mekân (zincir işletme yok). Yalnız etkinlik günlerinde açılan yapı (stadyum, boğa güreşi arenası, konser salonu) seçilebilir, `note`'a "genel ziyaret yok, etkinlik günleri" yaz. Kapalı/restorasyonda/taşınmış görünen mekânı seçme.
3. **Ayrı mekân (K108):** aynı adresi, gişeyi ya da bileti paylaşan bahçe, iç müze, avlu, kule ana mekânın parçasıdır, ayrı satır olmaz (ör. Katedral ile Katedral bahçesi/müzesi tek mekân; Alcazaba'nın Plaza de Armas'ı, Torre del Homenaje'si ayrı değil). Ayrı bileti ve ayrı girişi olan komşu yapı (ör. Teatro Romano ile Alcazaba) ayrı olabilir.
4. **Kaynak (url):** mekânın KENDİ resmî sitesinde adres ya da ziyaret bilgisi veren DERİN sayfa (iletişim, "visita", "horarios", "cómo llegar", "información práctica"); tek başına anasayfa değil. Kendi sitesi yoksa sırayla: sahibinin resmî sayfası (Belediye `malaga.eu` altındaki park/plaj/tesis sayfası, Málaga Piskoposluğu `diocesismalaga.es` parish sayfası, Junta de Andalucía `juntadeandalucia.es` / `museosdeandalucia.es` sayfası, liman `puertomalaga.com`), sonra resmî miras kaydı (IAPH `guiadigital.iaph.es`). Turizm portalı (visita.malaga.eu, malagaturismo.com, andalucia.org), Wikipedia, TripAdvisor, Google, blog, rezervasyon sitesi kaynak OLMAZ.
5. **Sayfa metni sunucudan gelmeli:** JS ile yüklenen sayfada bizim kopyamızda yalnız menü kalır ve reddedilir. WebFetch'te adres görünmüyorsa başka derin sayfa dene.
6. **`must_contain`:** sayfada BİREBİR geçen 1–3 kısa ifade; en az biri adres satırı (ör. "Calle San Agustín, 8" ya da posta kodlu satır "29015 Málaga"). Çeviri ya da düzeltme yapma; sayfadaki yazımı kopyala.
7. **Koordinat:** Wikidata'dan (havuzdaki `lat/lon`; havuzda yoksa `https://www.wikidata.org/wiki/Special:EntityData/<QID>.json` içindeki P625). QID'i yoksa İspanya resmî adres kaydı CartoCiudad (`https://www.cartociudad.es/geocoder/api/geocoder/find?q=<adres, Málaga>`); sonuç kutunun içinde olmalı ve sonuçtaki adres sayfadaki adresle aynı olmalı. Koordinat uydurulmaz; bulamazsan `lat`/`lon` boş, `note`'a "koordinat yok".
8. **Erişilemeyen alan adları (deneme):** malaga.es, sede.malaga.eu, deportes.malaga.eu (JS), sede.administracionespublicas.gob.es, mivau.gob.es, huvv.es, aena.es, bibliotecas.malaga.eu, gmu.malaga.eu, visita.malaga.eu, tributosmalaga.eu.
9. **Denge:** her grupta en az 1 koleksiyon dışı mekân; aynı mekânı iki gruba koyma.

## Çıktı
Dosya: görev mesajındaki `<WORK>\_is\mekan\secim_<n>.jsonl`. Satır başına bir mekân (Python ile UTF-8, `json.dumps(satir, ensure_ascii=False)`; her 5 mekânda bir dosyaya ekle). Alanlar:

```json
{"url":"https://…","must_contain":["…"],"title":"sayfanın başlığı","publisher":"yayıncı kurum","lang":"es","why":"Türkçe kısa araştırma notu (neden bu mekân, sayfada ne var)","name":"Mekânın yerel adı","group":"Müzeler","qid":"Q…","lat":36.7,"lon":-4.4,"district":"Centro","setting":"Kapalı alan","slug":"museo-picasso-malaga","entry_id":"malaga:museo-picasso-malaga","commons_category":"…","note":"","rol":"ana"}
```
- `setting` ∈ `Kapalı alan` | `Açık hava` | `Karma`. `district` = Málaga'nın resmî ilçe adı (Centro, Este, Ciudad Jardín, Bailén-Miraflores, Palma-Palmilla, Cruz de Humilladero, Carretera de Cádiz, Churriana, Campanillas, Puerto de la Torre, Teatinos-Universidad).
- `slug`: küçük harf ASCII ve tire, Türkçe/İspanyolca harf yok (á→a, ñ→n), en çok 60 karakter, mekânın adından; `entry_id` = `malaga:<slug>`. Mevcut kart slug'larıyla çakışmasın.
- `qid`: yoksa `""`. `commons_category`: havuzdaki değer, yoksa `""`.
- `rol` = `ana` ya da `yedek` (yedekler kontenjan tablosundaki sayıda, aynı kurallarla).

## Sınırlar
- Alt ajan başlatma. cd yok, Bash yok; PowerShell'le tek komut, tam yol; Python için önce `.py` dosyasını görev mesajındaki `<TMP>`'ye yaz, sonra `& '<PY>' -I '<dosya>'`; `python -c` ve heredoc yok. Dosyaları Read/Glob/Grep ile oku.
- Yalnız kendi `secim_<n>.jsonl` dosyana ve `<TMP>`'ye yaz.
- Bütçe: görev mesajındaki süre ve araç çağrısı. Dolunca bulduklarınla dön, eksikleri `gaps`'e yaz.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"dosya":"secim_<n>.jsonl","ana":N,"yedek":M,"per_group":{"<group>":{"ana":a,"yedek":y}},"gaps":["…"]}`
