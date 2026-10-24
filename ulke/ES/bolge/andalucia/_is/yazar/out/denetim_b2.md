# Denetim b2 (dar, editör sonrası): Endülüs bölge paketi

Tarih: 2026-10-24. Kartlara ve depo dosyalarına dokunulmadı. Yöntem: editörün eklediği/değiştirdiği her cümle kartın KENDİ source_ids metninde arandı (kaynak_dizini text_file). Canlı kontrol 3 (curl, sertifika doğrulaması açık): Junta ITP sayfası (polit-social), BOJA 2026/38 (Decreto-ley 1/2026), Junta escolarización ana sayfa + calendario. Ulusal kart karşılaştırması: ulke/ES/Yanıtlar.ulusal.jsonl (95 kart, ilgili slug'lar tek tek okundu). Değişmeyen kartlar (ev, resmi) ve saglik/gunluk için yalnız değişen cümleler denetlendi.

## 1. para / endulus-ikinci-el-konut-alimi-itp-indirimli-oranlar (kaynak 005 + 003)

ITP adı bağı: KAPANDI. 003 (Ley 5/2021, konsolide, son güncelleme 31/12/2025) md. 43 "En la modalidad de transmisiones patrimoniales onerosas del impuesto sobre transmisiones patrimoniales y actos jurídicos documentados, los tipos de gravamen reducidos ... 6% ... 3,5%" diyor; kartın "Devir vergisinin ... Transmisiones Patrimoniales Onerosas (ITP) modalitesinde" cümlesi buna dayanıyor. Başlıktan "ikinci el" çıkarılmış (kaynakta yok, doğru). 6 / 3,5 / 150.000 / 250.000 rakamları 003 md. 43.1 ile birebir.

Decreto-ley 1/26 cümleleri: 0% (vivienda habitual, kısmen/tamamen yıkılma, ruin, yıkım zorunluluğu) ve konut dışı 3,5% kaynak 005'in iki maddesiyle uyumlu; "kapsadığı bölge kartın kaynaklarında yer almaz" cümlesi doğru (005'te ámbito yok).

**1.1 ORTA, nüfus kaybı belediyesi koşulu 003'e göre yanlış kurulmuş (editör 003'ü bağlayınca ortaya çıktı).**
- Kart (summary): "alıcı 35 yaşından küçükse, aile içi şiddet ya da terör mağduruysa veya nüfus kaybı riski taşıyan bir belediyedense, konut yerleşik konutu olmalı ..."; steps: "nüfus kaybı riski taşıyan belediye durumunda 150.000 euro".
- 003 md. 43.1.g: "Se aplicará el tipo del 3,5% siempre que el inmueble que se adquiere radique en un municipio con problemas de despoblación, que destine el inmueble a su vivienda habitual y que el valor de la misma no sea superior a 150.000 euros." (Koşul alıcının değil TAŞINMAZIN belediyesi.) 005 ise belirsiz: "el adquirente sea menor de 35 años, víctima de violencia doméstica o de terrorismo o de municipio en riesgo de despoblación".
- Etki: okuyucu "benim belediyem" diye okuyabilir. Öneri: "taşınmaz nüfus kaybı riski taşıyan bir belediyede bulunuyorsa" yaz (003 md. 43.1.g), 35 yaş / mağdur koşullarından ayrı say.

**1.2 ORTA, Decreto-ley 1/26 istisnasında zaman sınırı kartın okunur metninde yok; kapsam dar.**
- Kart: "Decreto-ley 1/26 ... ayrıca %0 oran getirir", subtitle "borrasca hasarı için ayrı %0 oranı". Kartın kaynakları (005, 003) süreyi vermiyor ("kaynakta yok").
- Canlı BOJA 2026/38, md. 3: "serán aplicables a los hechos imponibles cuyo devengo se produzca desde el día 23 de enero hasta el 31 de diciembre de 2026, ambos inclusive." md. 2: kapsam, Consejo de Gobierno kararıyla listelenen belediyeler (ya da belediyenin bir kısmı), fırtınalar 23 Ocak-16 Şubat 2026. Yani bugün (24 Ekim 2026) iki ay kala biten, belirli belediyelere özgü bir önlem.
- valid_until 2026-12-31 bunu dolaylı karşılıyor, ama okuyucu metninde "2026 sonunda biter / yalnız listedeki belediyeler" yok. Öneri: BOJA 2026/38'i üçüncü kaynak yap ya da "süre ve belediye listesi Decreto-ley'de belirlenir, kaynağımızda yok; işlemden önce kontrol et" de.

**1.3 ORTA, steps 4 editörün eklediği ek koşul: "Yerleşik konutunu borrasca hasarı yüzünden yitirdiysen".**
- Kaynak 005: "vivienda habitual del contribuyente, que sustituya a otra situada dentro del ámbito territorial ... " ("otra" = yerine geçilen konut; habitual olması istenmiyor). Canlı BOJA 2026/38 md. 8.1 aynı: yalnız YENİ konut yerleşik konut olmalı.
- Kart yeni konutu yerleşik diye doğru yazmış (summary) ama steps eski konutun da yerleşik olduğunu şart koşuyor. Öneri: "Hasar nedeniyle onarılamayan bir konutun yerine yerleşik konut alıyorsan ..." diye yaz.

**1.4 KÜÇÜK, steps 4 parantezi:** "(yıkılmış, ruin ilan edilmiş ya da yıkılması gereken)" kaynaktaki "derruido total o parcialmente" içindeki "kısmen" ifadesini düşürüyor. Ayrıca summary "borrasca hasarı için mali destek": kaynak "apoyo fiscal" (vergi desteği). Öneri: "tamamen ya da kısmen yıkılmış" ve "vergi desteği".
**1.5 KÜÇÜK, cost "%6 ya da %3,5 oranı (şarta göre)" karttaki %0'ı anmıyor.** Öneri: "%6, %3,5 ya da (Decreto-ley 1/26 kapsamında) %0".
**1.6 KÜÇÜK, slug/entry_id hâlâ "ikinci-el"** ("kaynakta yok" dediğiniz kavram). Öneri: slug değişimi yapılamıyorsa kayıtta not; yoksa "konut-alimi" olarak yeniden adlandır.
**1.7 KÜÇÜK, Türk okuyucu:** reduced ITP yeni yapı alımına (IVA/AJD) uygulanmaz; başlıktan "ikinci el" çıkınca kart "konut alımı" genel okunuyor. Kaynakta yok: gaps.md'ye yaz, kartta kesin dil kurma. 003 md. 43.3 (garaj/ek bölümlerin değeri toplamı) kartta yok, kaynakta var.

Önceki bulgular: ORTA "ITP/ikinci el kaynakta yok" KAPANDI; ORTA "Decreto-ley 1/26 sessizce atlanmış" KAPANDI (ama 1.2 ve 1.3 doğdu); KÜÇÜK "üç durum / beş koşul" KAPANDI ("üç ayrı maddede"); KÜÇÜK "genel oran yok" KAPANDI (not açık yazıyor).
Derece: ciddi 0, orta 3, küçük 4.

## 2. para / endulus-gelir-vergisi-irpf-bolge-dilimleri-ve-indirimleri (kaynak 003 + 004)

Değişen note, kaynak 004 ile birebir: "se encuentra cedido a las Comunidades Autónomas, el 50 % de su recaudación" + "Ley 22/2009 ... Comunidades Autónomas de régimen común" -> "ortak rejimdeki özerk bölgelere devredilmiştir (Endülüs'e özgü değil)" doğru. "Ley 5/2021 md. 9–23 bis" ve "mínimos personal y familiar ... artículo 23 bis" 004'te ve 003 dizininde var. "Gelir vergisi devlet vergisidir": 004 "impuesto estatal". Ulusal IRPF kartıyla (régimen común, bölgesel ölçeği bölge onaylar) çelişki ya da tekrar yok.
Önceki ORTA ("Endülüs'e özgü %50"): KAPANDI.
Önceki küçükler (steps marjinal dilim uyarısı, Endülüs'te mukim olma kapsamı): değişmedi, AÇIK (küçük, gaps.md'de mukim notu var).
Yeni bulgu: yok. Derece: ciddi 0, orta 0, küçük 0 (yeni); 2 önceki küçük açık.

## 3. is / endulus-sae-is-arayan-kaydi-demandante-de-empleo (kaynak 007 + 008)

- Summary'den "Türk vatandaşı ... bu izin şartı sana uygulanır" çıkarılmış: iyi (kaynakta "Türk" yok). Ulusal paro kartı Türk'ü AB dışı sayıyor, çelişki yok.
- Sınırlandırılan sıra cümlesi: kaynak 008 bağlamına UYUYOR. 008 başlığı "Soy de fuera de la UE y quiero trabajar en Andalucía"; "Para poder trabajar en España necesitas una autorización administrativa que debes solicitar ante el Ministerio de Inclusión, Seguridad Social y Migraciones"; "necesitan obtener un visado antes de viajar a España ... en los países de procedencia, acudiendo a los consulados"; "Una vez que dispongas de la autorización administrativa, puedes acceder a los servicios públicos de empleo presentando una solicitud o demanda". Kart bunu "yurt dışından gelip çalışmak isteyen" kişiyle sınırlamış; vize-konsolosluk ve izin->demanda sırası kaynakla uyumlu.

**3.1 KÜÇÜK, ikinci cümle kaynak dışı iki-yollu ayrım:** "Zaten Endülüs'te oturan AB dışı kişi için SAE'nin kayıt şartı yalnızca kayda izin veren idari izindir."
- 007: "contar con una autorización administrativa que te permita la inscripción en un servicio público de empleo" (hangi izin olduğu yok). 008'in Ukrayna bölümü ikamet edenlerin farklı belgeyle kayıt olabildiğini gösteriyor ("Resguardo de ... protección temporal", TIE) ama bu kartın konusu değil. "Yalnızca" ve "zaten oturan" ayrımı iki kaynakta da yok; okuyucu çalışma izni gerekmediğini anlayabilir. Öneri: cümleyi "SAE kayıt sayfası (007) yalnızca 'kayda izin veren idari izin' diyor; hangi iznin yettiği sayfada sayılmıyor" biçiminde yaz ya da sil (gaps.md zaten bunu "kaynakta yok" diyor).

Önceki ORTA (çalışma izni genel kural): KAPANDI. KÜÇÜK "iş bürosu oturduğun yere göre" kaldırıldı: KAPANDI. KÜÇÜK AEA/İsviçre: gaps.md'ye alındı, KAPANDI.
Derece: ciddi 0, orta 0, küçük 1.

## 4. aile / endulus-okul-kaydi-basvuru-donemi-ve-gec-gelen-ogrenci (kaynak 012 + 013)

Kapsam ve istisna: 012 "para las enseñanzas correspondientes al segundo ciclo de Educación Infantil, Educación Primaria, Educación Secundaria Obligatoria y Bachillerato" ve "segundo ciclo ... (3, 4 ó 5 años)" ile kartın dört kademesi birebir. "Aynı okulda devam edecek öğrenci Mart'ta başvurmaz": 012 "esté matriculado en un centro docente público o privado concertado en un curso sostenido con fondos públicos y desee continuar en dicho centro" ile uyumlu. "Genel usul bittikten sonra" ve "taşınma, evlat edinme": 013 md. 51.2 ("una vez finalizado el procedimiento ordinario ... traslado de la unidad familiar o por adopción") birebir. "Il organı yer gösterirse 2 iş günü" md. 51.4 birebir. "il eğitim organına göre değişir" silinmiş: iyi.

**4.1 ORTA, özel destek kaynağı cümlesi koşulu tersine çevirip kaynağın niteleyicisini düşürüyor.**
- Kart (summary/steps/note, üç yerde): "Özel destek kaynağı gerektiren çocukta okul bu kaynaklara sahipse başvuruyu kabul eder; sahip değilse başvuru il organına gider ve il organı gerekli kaynaklara sahip bir okulda yer verir."
- 013 md. 51.3: "Cuando el alumno o alumna requiera recursos específicos que resulten de difícil generalización solo se estimará la solicitud si el centro docente cuenta con ellos." Kaynak: (a) kaynaklar "genelleştirilmesi zor" olanlar (her destek ihtiyacı değil), (b) kaynağa sahip olmak kabulün gerekli koşulu ("solo ... si"), yeterli koşulu değil; boş yer şartı (md. 51.3 ilk paragraf) da geçerli. Kart "sahipse kabul eder" diyor, summary'de boş yer cümlesinden ayrı durduğu için "kaynağı olan okul her halükârda kabul eder" okunabilir.
- Öneri: "genelleştirilmesi zor özel kaynaklar gerektiren çocukta, boş yer olsa bile okul ancak bu kaynaklara sahipse başvuruyu kabul eder; sahip değilse il organına gönderir" diye yaz.

**4.2 KÜÇÜK, ikinci muafiyet atlanmış:** 012: "alumnado que ... esté matriculado en el último curso de alguna de las etapas ... y vaya a cursar el primer curso de la etapa siguiente en el centro al que esté adscrito ... salvo adscripción múltiple" Mart'ta başvurmaz. Kart yalnız "aynı okulda devam"ı sayıyor; 6. sınıf -> adscrito IES çocuğunun ailesi gereksiz başvuru düşünebilir. Öneri: tek cümle ekle.
**4.3 KÜÇÜK, "1-31 Mart" ile Junta'nın kendi takvimi çelişiyor (canlı, bugün):** escolarización ana sayfası "Del 1 al 31 de marzo, ambos inclusive ... 2026/27"; aynı portalın Calendario'su "Presentación de solicitudes: Del 01 marzo 2026 al 07 abril 2026". Kart "kesin tarihler yıldan yıla değişebilir" diyerek yumuşatmış ve "genel kural Mart" çerçevesi doğru; ancak bilinen farkı (7 Nisan) söylemiyor. gaps.md bunu "kaynakta yok" diye yazıyor. Kabul edilebilir; yalnız kalan risk.
**4.4 KÜÇÜK, "kaynakta dönem ... diye geçer" meta kalıbı sürüyor ve valid_until null** (tarihe duyarlı süreç; sonraki dönem açılmadan önce bir tarih bağlanması önerilmişti). Öneri: "Dönem genellikle 1-31 Mart olarak ilan edilir" gibi kaynak-atıfsız yaz; valid_until = 2027-02-28.

Önceki bulgular: 1.1 ORTA (1-31 Mart) KISMEN (hedge eklendi, 7 Nisan farkı yok; 4.3'e düştü); 1.2 ORTA (kapsam/muafiyet) KAPANDI (4.2 küçük artık); 1.3 ORTA (il organına göre değişir + md. 51 özel kaynak) KAPANDI silme açısından, ama eklenen cümle 4.1'i doğurdu; 1.4 KÜÇÜK ("genel dönemi beklemeden") KAPANDI; 1.5 KÜÇÜK (meta kalıp, valid_until) AÇIK (4.4).
Türk okuyucu: kartta oturum/AB iddiası yok; yabancı çocuk belge şartı kaynaklarda yok (gaps.md'de).
Derece: ciddi 0, orta 1, küçük 3.

## 5. ulasim / endulus-metropol-ulasim-konsorsiyum-kartlari-ve-interoperabilite (kaynak 009 + 010)

Tek konsorsiyuma özgü rakam/kural kaldı mı: rakam YOK (2 salto, 5 euro, 1,50, 500 euro, varış sorusu, tüm satış noktaları hepsi çıkarılmış). Kalan cümleler:
- "Endülüs'te birden çok metropol konsorsiyumu var, her biri kendi tarife çerçevesini belirler": 010 "en el marco tarifario establecido por cada Consorcio" + 009 dokuz konsorsiyum listesi. Ortak, tamam.
- "Başka bir konsorsiyumun alanında o konsorsiyumun belirlediği tarifeler geçerlidir": 010 ile birebir; 009 ile uyumlu (Granada'da sabit tutar Granada kuralı).
- "Evet, kartlar birbirinin alanında kullanılabilir": 009 (Granada kartı her yerde, her kart Granada'da) ve 010 (Málaga kartı "resto de Consorcios") iki kaynakta da var.

**5.1 KÜÇÜK, "Kartı kendi konsorsiyumunda kullanırken mevcut koşullar aynı kalır" (summary + steps 1) yalnız 009'a dayanıyor.** 009: "Para utilizar la tarjeta en su Consorcio habitual, las condiciones serán las mismas que las existentes actualmente." 010'da karşılığı yok; ayrıca tarihsiz sayfada "mevcut" göreli. İçeriksiz bir cümle; zararı düşük. Öneri: sil ya da "kendi alanında kendi konsorsiyumunun kuralları geçerlidir" yap.
**5.2 KÜÇÜK, "Kartlar birbirinin alanında" (title/subtitle/summary) genellemesi iki kaynakta yalnız Granada ve Málaga kartı için doğrulanıyor;** Sevilla/Cádiz vb. kartlar için karşılıklı kullanım iki sayfada da açıkça yok. Öneri: "Granada ve Málaga konsorsiyumlarının sayfalarına göre" çerçevesi ya da gaps.md notu.
Tarih etiketi/valid_until: kart null, timing boş (009 tarihsiz, 010 21.04.2026). Önceki 2.4 KÜÇÜK AÇIK; küçük risk (tarife ayrıntısı yok, bu yüzden zayıf).

Önceki bulgular: 2.1 ORTA (Granada kuralı adsız genel) KAPANDI (karttan çıkarıldı, gaps.md'ye taşındı); 2.2 KÜÇÜK KAPANDI; 2.3 KÜÇÜK ("salto" tanımsız) KAPANDI (kaldırıldı); 2.4 KÜÇÜK AÇIK; 2.5 KÜÇÜK (meta cümle) KAPANDI.
Derece: ciddi 0, orta 0, küçük 2.

## 6. Değişen ama kapsam dışı kartlar (yalnız değişen cümle)

- saglik: eklenen "TSV için yaş sınırı yoktur, ancak 18 yaş altı için Cl@ve gerekir" kaynak 001 ile birebir ("No hay límite de edad para obtenerla, pero sí es necesario para menores de 18 años disponer del sistema Cl@ve"). Önceki küçük (18 yaş) KAPANDI. Yeni bulgu 0.
- gunluk: "Yıllık sınır on dört gündür; ikisi yerel tatildir" 014 ile birebir ("límite anual de catorce días festivos, de los cuales dos serán locales"); "her belediyenin en çok iki yerel tatil önerisi Consejería'ya bildirilir" 014 md. segundo ile uyumlu; "okul" kaldırıldı, tekrar giderildi. Önceki küçükler (3.1, 3.2) KAPANDI. Yeni bulgu 0.
- ev, resmi: değişmedi, denetlenmedi.

## 7. Ulusal kart çelişkisi / tekrarı

Çelişki YOK, tekrar YOK. Ulusal kartlarda ITP, SAE, Endülüs ya da konsorsiyum geçmiyor (anahtar kelime taraması: ITP, Transmisiones, SAE, Servicio Andaluz, Consorcio, Endülüs, Andaluc, devir vergisi; yalnız "demandante" ulusal paro kartında).
- IRPF: ulusal "gelir-vergisi-irpf-devlet-dilimleri" devlet ölçeği + "bölgesel ölçeği özerk bölge onaylar"; bölge kartı yalnız Endülüs payını ve %50 devir notunu veriyor, rakamlar çakışmıyor.
- Okul: ulusal "egitim-sistemi-zorunlu-egitim-ve-okul-turleri" "başvuru takvimi ve puanlama bölgene göre değişir" diyor, tarih vermiyor; bölge kartı Mart/Anexo III/Séneca ile bunu dolduruyor. Ulusal "0-6 yaş okul öncesi" ile bölge "2. kademe Infantil 3-5 yaş" uyumlu.
- SAE: ulusal "issizlik-maasi-paro-sepe-basvurusu" "demandante olarak kayıt ol" ve "Türk vatandaşı AB dışı" diyor; bölge kartı kaydın nasıl yapılacağını anlatıyor, çelişmiyor.
- Gunluk: ulusal "resmi-tatiller-2027" ile bölge listesi önceki raporda doğrulandı, değişmedi.

## Özet tablo

| kart | ciddi | orta | küçük | önceki bulgular durumu |
|---|---|---|---|---|
| para / ITP indirimli oranlar | 0 | 3 | 4 | orta 2/2 KAPANDI (yeni orta 1.1, 1.2, 1.3 doğdu); küçük 2/2 KAPANDI |
| para / IRPF bölge dilimleri | 0 | 0 | 0 (2 önceki küçük açık) | orta KAPANDI; küçük 2 AÇIK (değişmedi) |
| is / SAE | 0 | 0 | 1 | orta KAPANDI; küçük KAPANDI |
| aile / okul kaydı | 0 | 1 | 3 | orta: 1.1 KISMEN, 1.2 KAPANDI, 1.3 KAPANDI (yeni orta 4.1); küçük 1.5 AÇIK |
| ulasim / konsorsiyum | 0 | 0 | 2 | orta KAPANDI; küçük 2.4 AÇIK |
| saglik (yalnız değişen cümle) | 0 | 0 | 0 | 18 yaş küçüğü KAPANDI |
| gunluk (yalnız değişen cümle) | 0 | 0 | 0 | 2 küçük KAPANDI |
| TOPLAM | 0 | 4 | 10 | AÇIK orta yok; KISMEN: aile 1.1 |

Bakılamayan: Decreto-ley 1/2026 md. 2 kapsamındaki belediye listesi (Consejo de Gobierno kararı, 18/02/2026) açılmadı; Decreto 21/2020 md. 51'in sonraki değişikliklerle (Decreto-ley 2/2021, Orden 11/01/2026) ilişkisi önceki gibi doğrulanamadı; ev ve resmi kartları bu turda yeniden okunmadı.
