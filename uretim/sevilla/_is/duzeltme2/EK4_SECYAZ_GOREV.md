# Mekân seç + yaz (ek tur 4) — Sevilla (CITY-107), 120 hedefini tamamlama

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, aynı klasörde `yer-yazari.md`, `mekan-yazari.md`; seçim kuralları için `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\EK3_SECIM_GOREV.md` ("Ayrı mekân", "Ziyarete açık", "Kaynak", koordinat kuralları geçerli; kontenjan ve çıktı bölümleri bu dosyadaki gibi).

## Değerler
- `<city_id>` = `sevilla`; `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`**

## Neden
Pakette 102 mekân var, hedef 120: hedef eksiği denetimde P1. Her ajan **6 gerçek, ayrı, fotoğraflı, ziyaret edilebilir mekân + 1 yedek** seçer, kaynağını doğrular ve kartlarını yazar.

## Aday havuzu
`<WORK>\_is\mekan\ek3_aday_havuz.json` (Wikidata'da fotoğrafı olan, kutu içi adaylar; `commons_category` dolu olanları seç). Görev mesajı sana bir tür grubu verir; yalnız o türden seç. Pakette olanları ve onların parçalarını önerme (`<WORK>\_is\data\Mekânlar.jsonl`: `slug`, `title`; `<WORK>\_is\duzeltme2\cikan_mekanlar.txt`'tekiler de olmaz). Heykel, tek anıt taşı, köprü, kütüphane, ofis binası seçme.

## Şartlar
- **Fotoğraf:** `commons_category` dolu ve kategoride mekânın kendisini gösteren ≥3 dosya (Commons API'den kategori üyelerini sayabilirsin; Wikidata API 429 verebilir, Commons API çalışıyor).
- **Kaynak:** mekânın kendi resmî sayfası, Arzobispado/cofradía resmî sitesi ya da IAPH `guiadigital.iaph.es` kaydı (Junta'nın resmî miras rehberi). Turizm portalı yalnız son çare ve ücret/saat kaynağı değildir. Engelli: sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es.
- **Doğrulama ve kimlik:** adaylarını `<WORK>\_is\mekan\secim_<harf>.jsonl`'e yaz (satır biçimi `EK3_SECIM_GOREV.md` "Çıktı"daki gibi; `commons_category` zorunlu), sonra
  `& <PY> <TK>\add_sources.py <WORK>\_is --candidates <WORK>\_is\mekan\secim_<harf>.jsonl --subdir snap_<parça>-yazar1 --topic kesif --city-id sevilla`
  (klasör varsa sıra bir artar; `snap_kesif_` önekini kullanma). Reddedilen adayın yerine yedeği koy. Kart başına en çok 2 kaynak, toplam 8 yeni kaynağı geçme.
- **Ziyarete açık:** kilise ve meydan için de genel ziyaret/ibadet saatleri ya da açık kamusal alan; yalnız etkinlik günü açılan yer olmaz.

## Yazım
- Dosyalar (yeni): `<WORK>\_is\data\parcalar\Mekânlar.<parça>.jsonl`, `Bağlantılar.<parça>.jsonl`, `<WORK>\_is\claims\<parça>.jsonl`. Anahtar sırası ve alanlar `Mekânlar.mekan7.jsonl` ile aynı; `order` görev mesajındaki aralıkta; `collection` = `Hayır`; `editorial_status` = `Taslak`; `media_key` var olan satırlardaki biçimle; koordinat yalnız Wikidata (havuz `lat`/`lon`).
- Her mekâna ≥1 Bağlantılar satırı (harita tek bağlantı olamaz); ücret/saat yalnız resmî kaynakta varsa. Mekân notu kalıplaşmaz; ilk cümle mekânın ne olduğunu ve neden görülmeye değdiğini söyler. Her değişken iddia defterde birebir alıntıyla.

## Bitirmeden
Ortak kurallar §8 `merge_package` kontrolü (çıktılar `<TMP>`'ye): kendi parçanı ilgilendiren bulgu 0, `quote_miss` 0.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>`'de. Her doğrulanan mekânı hemen dosyaya yaz. Bütçe **40 dakika / 140 araç çağrısı**; dolunca bitirdiklerinle dön.

## Dönüş
Tek satır JSON: `{"part":"<parça>","yazilan":["slug"],"yedek_kullanildi":n,"reddedilen":n,"yeni_kaynak":n,"script_kontrol_hata":0,"open":[...]}`
