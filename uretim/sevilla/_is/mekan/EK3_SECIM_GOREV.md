# Mekân ek seçim turu 3 (ikinci düzeltme turu, 2026-10-25) — Sevilla (CITY-107)

Kurallar `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\SECIM_GOREV.md`, `EK_SECIM_GOREV.md` ve `EK2_SECIM_GOREV.md` ile aynı (üçünü de oku; aday havuzu ve "Neden" bölümleri burada değişir). Metin yazmıyorsun; mekân seçip resmî kaynak adresi ve kanıt ifadesi buluyorsun.

## Neden
Bağımsız denetim (L1): 18 mekân fotoğrafsız (Commons'ta da ikinci kaynaklarda da kare yok; çoğu tablao, bodega, galeri, minigolf, tırmanış salonu), 3 kayıt başka bir mekânın parçası (Alcázar Bahçeleri, Museo Taurino, Macarena surları). Bu 21 kayıt paketten çıkıyor; yerine **fotoğrafı kesin bulunan**, ayrı, gerçek, bugün ziyarete açık 21 mekân gerekiyor (mekân sayısı 120'de kalsın).

Çıkan 21 (yeniden önerme): bodega-gongora, cartuja-qanat, centro-nautico-alamillo, cerveceria-giralda, cicus-centro-iniciativas-culturales, espacio-primera-vuelta-al-mundo-nao-victoria, fundacion-cajasol-sevilla, galeria-rafael-ortiz, indoor-minigolf-sevilla, mercado-lonja-del-barranco, musan-museo-del-santo-angel, museo-de-las-ilusiones, museo-historia-de-la-farmacia-us, rock-and-wall-climbing, sala-cero-teatro, tablao-los-gallos, teatro-flamenco-sevilla, teatro-la-fundicion, muralla-de-la-macarena, real-alcazar-jardines, museo-taurino-real-maestranza.

## Fotoğraf şartı (bu turun asıl şartı)
Her aday için Wikidata öğesinde P18 (görüntü) **ya da** en az 3 dosyalı, mekânın kendisini gösteren bir Commons kategorisi (P373) olmalı. `commons_category` alanına kategori adını yaz (`Category:` öneki olmadan). Fotoğrafı belirsiz aday seçme. Ticari işletme (bar, tablao, galeri, salon) yalnız Commons kategorisi kesin varsa ve grup başına en çok 1.

## Aday havuzu
`C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\ek3_aday_havuz.json`: Wikidata'da fotoğrafı olan, kutu içindeki, pakette olmayan 244 aday (`qid, name, lat, lon, types, website, commons_category, group_guess`; `group_guess` tahmindir). Havuzda olmayan, fotoğrafı kesin mekânı da önerebilirsin (ör. Pabellón de la Navegación, Castillo de San Jorge, Hospital de la Caridad, Torre de Don Fadrique, Auditorio Rocío Jurado, Jardines de Cristina, Jardín Americano, Palacio de Deportes San Pablo — örnektir, her birinin şartları sağlaması gerekir).

## Ek kurallar (L1 dersleri)
- **Ayrı mekân (K108):** aynı adresi, gişeyi ya da bileti paylaşan bahçe, iç müze, sur parçası, salon ayrı mekân değildir. Pakettekilerin (`..\_is\data\Mekânlar.jsonl`) parçası olan yeri önerme.
- **Ziyarete açık:** düzenli genel ziyaret olmalı (yalnız etkinlik günü açılan, kulüp üyelerine özel, antrenman tesisi değil). Kanıtı sayfada (saat, ziyaret, bilet) ara; `note`'a kısa yaz.
- **Kaynak:** (1) mekânın kendi resmî sitesinde adres/ziyaret veren derin sayfa; (2) yoksa IAPH `guiadigital.iaph.es`, Junta müze/anıt sayfası, `museosdeandalucia.es`, Diputación, Üniversite (`us.es`), Arzobispado/cofradía resmî sitesi; adres için son çare `visitasevilla.es` mekân sayfası (ücret ve saat kaynağı değildir). Turizm portalı tek kaynaksa `note`'a "ücret/saat için resmî sayfa yok" yaz.
- Koordinat yalnız Wikidata'dan (havuz değeri ya da P625); kutu 37.30–37.45 / −6.03 – −5.89.
- Tarih ve mimari pakette 38 (en çok 42): bu turda en çok 3 tarih/mimari önerisi.

## Kontenjan (görev mesajı grubunu verir)
- **A**: Doğa ve açık hava 4 (+1 yedek), Müzeler 4 (+1), Tarih ve mimari 2 (+1) → 13 satır.
- **B**: Çocuklarla keşif 3 (+1), Spor 2 (+1), Sahne ve müzik 3 (+1), Sanat ve sergiler 2, Yeme ve içme 1 → 14 satır.
Bir grupta şartı sağlayan aday yoksa uydurma; eksik sayıyı `gaps`'e yaz, kendi öbür gruplarından birine en çok 2 fazla öner.

## Zorunlu doğrulama
`EK_SECIM_GOREV.md`'deki `fetch_snapshot --urls ... --must-contain ...` yöntemi: ifade bizim temiz kopyamızda geçmeli; `thin_text`/`soft_404`/kanıtsız aday çıkarılır.

## Çıktı
`C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\secim_<harf>.jsonl` (`<harf>` = görev mesajındaki: `I` ya da `J`), satır: `{"url","must_contain":["..."],"publisher","why","name","group","qid","lat","lon","district","setting","slug","entry_id","commons_category","note"}`; `entry_id` = `sevilla:<slug>`, `slug` paket genelinde benzersiz (`..\_is\data\*.jsonl`'de yok). Yedekleri `note`'un başına `YEDEK:` yazarak işaretle. UTF-8, BOM'suz, Python ile yaz; her doğrulanan adayı hemen dosyaya ekle.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>`'de. Bütçe **35 dakika / 110 araç çağrısı**; dolunca bulduklarınla dön.

## Dönüş
Tek satır JSON: `{"groups":{"<grup>":<sayı>},"yedek":<sayı>,"rejected":<doğrulamadan geçmeyen>,"gaps":[...]}`
