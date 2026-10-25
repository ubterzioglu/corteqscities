# Mekân seçimi — Sevilla (CITY-107)

Görev: senin gruplarında Sevilla'daki gerçek, bugün açık, düzenli ziyarete açık mekânları seç ve her biri için resmî kaynak adresi bul. Metin yazmıyorsun.

## Girdi
- Havuz (Wikidata, şehir sınırı içi): `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\havuz_<grup>.jsonl` (`qid, name, lat, lon, types, district, website, has_image, commons_category`). Fotoğraflılar (`has_image: true`) önce sıralı; **fotoğraflı mekânları öne al.**
- Erişim haritası: `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\kesif\KESIF_TALIMAT.md`. Engelli: sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es (kullanma).
- Paketteki mevcut slug'lar (çakışmasın): `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\data\Yanıtlar.jsonl` (`slug` alanı).

## Şartlar
- Gerçek, şehir sınırında (koordinat kutusu 37.30–37.45 K, −6.03 – −5.89 D), şehre özgü, kalıcı mekân. Zincir işletme yok. Kapanmış/taşınmış/yalnız özel etkinlikte açık olan yok.
- **Kaynak sırası:** (1) mekânın **kendi resmî sitesindeki** adres veya ziyaret bilgisi veren derin sayfa; (2) kendi sitesi yoksa: Endülüs Tarihî Miras Enstitüsü rehberi `guiadigital.iaph.es/bien/inmueble/...` sayfası, Junta'nın müze/anıt sayfası (`juntadeandalucia.es/cultura/...`, `museosdeandalucia.es`), ya da Turismo de Sevilla'nın (belediye turizm konsorsiyumu) `visitasevilla.es` mekân sayfası. Blog, TripAdvisor, ticari rehber, Wikipedia yok.
- `must_contain`: sayfada **birebir** geçen 1–3 ifade; en az biri **adres** (sokak adı + numara ya da sayfadaki adres satırı). Sayfayı açıp ifadeyi gerçekten gör (betikle indirip metinde ara); JS ile boş gelen sayfayı ekleme.
- Koordinat yalnız Wikidata'dan (havuzdaki `lat`/`lon`; havuzda yoksa Wikidata'da mekânın öğesini bul, P625). Koordinat bulunamıyorsa `lat`/`lon` boş bırak, uydurma.
- Her grupta en az 1 koleksiyon dışı mekân (ör. tarih grubunda müze olmayan bir anıt) — `note`'a "koleksiyon dışı" yaz.
- `slug`: küçük harf ASCII, tire; `entry_id` = `sevilla:<slug>`; bütün pakette benzersiz.
- `setting` ∈ `Kapalı alan` | `Açık hava` | `Karma`. `group` Türkçe adıyla (aşağıda). `district`: semt/ilçe adı (havuzdaki ya da kaynaktaki).

## Çıktı
`C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\secim_<harf>.jsonl` (görev mesajındaki harf), satır başına:
`{"url","must_contain":["..."],"publisher","why","name","group","qid","lat","lon","district","setting","slug","entry_id","commons_category","note"}`
UTF-8, BOM'suz, Python ile yaz. `qid` havuzdan (yoksa ""); `commons_category` havuzdan.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki klasörde. Bütçe **40 dakika / 120 araç çağrısı**; dolunca bulduklarınla dön, eksik kalanı `gaps`'e yaz. Kontenjana ulaşamazsan uydurma, eksik bırak.

## Dönüş
Tek satır JSON: `{"groups":{"<grup>":<sayı>},"photo_share":<fotoğraflı oranı>,"gaps":[...]}`
