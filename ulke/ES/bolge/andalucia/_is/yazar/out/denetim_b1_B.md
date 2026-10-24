# Bağımsız denetim B1, grup B: Endülüs bölge paketi (aile, ulasim, gunluk, resmi; 4 kart)

Denetim tarihi: 2026-10-24. Yöntem: kartın olgusal cümleleri kartın kendi kaynak metniyle (kaynak_dizini text_file) karşılaştırıldı; canlı kontroller: Junta escolarización SSS ve Calendario sayfaları, Junta normativa sayfası, BOJA 2020/34 (Decreto 21/2020), BOJA 2026/84 (Decreto 84/2026), ctagr.es interoperatividad, ctmam.es tarjeta, Junta Carpeta Ciudadana. Kartlara dokunulmadı. Ulusal kart karşılaştırması: ulke/ES/Yanıtlar.ulusal.jsonl.

## 1. aile: endulus-okul-kaydi-basvuru-donemi-ve-gec-gelen-ogrenci (kaynak 012, 013)

**1.1 ORTA, "1-31 Mart" 2026/27 tarihi olarak sunuluyor; aynı portalın canlı Calendario sayfası farklı süre veriyor ve süreç bitmiş.**
- Kart (özet): "kaynak sayfa 2026/2027 süreci için '1-31 Mart, ikisi dahil' diyor."
- Kaynak 012 (SSS): "Del 1 al 31 de marzo, ambos incluidos, está abierto el plazo para presentar solicitudes de admisión..." (doğru alıntı).
- Canlı Calendario (2026/27): "Presentación de solicitudes: Del 01 marzo 2026 al 07 abril 2026". Aynı portalın ana sayfası da "Abierto el plazo de escolarización del 1 al 31 de marzo" diyor; yani Junta'nın kendi sayfaları tutarsız. Bugün (24 Ekim 2026) 2026/27 başvuru süresi kapanmış; kart kapanmış bir dönemin tarihini sanki geçerli süre gibi veriyor ve 7 Nisan'a hiç değinmiyor.
- Düzeltme: "Başvuru her yıl Mart'ta açılır; 2026/27 için Junta takvimi 1 Mart-7 Nisan 2026 gösterdi (SSS 1-31 Mart diyor), sonraki yılın tarihi her yıl Orden ile ilan edilir" diye yaz; kaynak 012 yerine/yanında Calendario sayfasını kaynak yap.
- Okuyucu etkisi: genel kural (Mart) doğru; kesin gün sayısı yanıltabilir. Ciddi saymadım çünkü "genel kural" çerçevesi var.

**1.2 ORTA, kapsam: Mart başvurusu yalnız bazı kademeler için, kart "kamu ve concertado okullara" diye genelliyor; devam eden öğrencinin başvurmaması istisnası yok.**
- Kart: "Endülüs'te kamu ve devlet destekli özel (concertado) okullara başvuru Mart ayında yapılır"; step 1 "Mart ayındaki genel başvuru döneminde tek bir başvuru formu doldur".
- Kaynak 012: "...para las enseñanzas correspondientes al segundo ciclo de Educación Infantil, Educación Primaria, Educación Secundaria Obligatoria y Bachillerato." (0-3 yaş ve FP ayrı programlar; canlı portalda "0 a 3 años" ve "Formación Profesional Calendario" ayrı). Aynı SSS: "¿Qué alumnado no tiene que presentar solicitud de admisión durante el mes de marzo? El alumnado que ... esté matriculado en un centro ... y desee continuar en dicho centro".
- Düzeltme: özete "3 yaş (2. kademe Infantil), Primaria, ESO ve Bachillerato için" ekle; "aynı okulda devam edenler başvurmaz" cümlesi ekle.

**1.3 ORTA, "olağanüstü usulün işleyişi il eğitim organına göre değişir" kaynaksız; md. 51'in özel kaynak istisnası atlanmış.**
- Kart (note): "olağanüstü usulün işleyişi il eğitim organına göre değişir."
- Kaynak 013 md. 51: böyle bir ifade yok ("kaynakta yok"); madde tek usul tanımlıyor. Aynı maddenin 3. fıkrası: "Cuando el alumno o alumna requiera recursos específicos que resulten de difícil generalización solo se estimará la solicitud si el centro docente cuenta con ellos. En caso contrario, la solicitud será remitida al correspondiente órgano territorial provincial..." Kart "boş yer varsa müdür kabul eder" diyor, bu koşulu yazmıyor.
- Düzeltme: "il organına göre değişir" cümlesini sil; "özel destek gerektiren çocukta okul bu kaynaklara sahipse kabul eder, değilse il organı yer verir" ekle.

**1.4 KÜÇÜK, steps 3 "genel dönemi beklemeden" ve kapsam.**
- Kaynak 013 md. 51.2: başvurular "una vez finalizado el procedimiento ordinario de admisión ... para atender necesidades inmediatas de escolarización del alumnado de incorporación tardía, entre otras las que vengan motivadas por el traslado de la unidad familiar o por adopción o ...". "Genel dönemi beklemeden" ifadesi kaynakta yok; doğrusu "genel usul bittikten sonra".
- Düzeltme: "Genel usul bittikten sonra (taşınma, evlat edinme vb. acil ihtiyaçta) başvuruyu okula ya da il organına ver."

**1.5 KÜÇÜK, meta cümle ve valid_until.** "kaynak sayfa ... diyor" (YAZAR_KURALLARI md. 3'e yakın "sayfada yazar" kalıbı) ve valid_until null iken kart 2026/27 tarihli süreç veriyor (md. 6, 11). Öneri: kalıbı kaldır, valid_until'i bir sonraki sürecin açılışından önceki bir tarihe (ör. 2027-02-28) bağla.

**Güncellik, Decreto 21/2020 md. 51: BAKILAMADI (kısmen).** Canlı BOJA 2020/34 yayın metnindeki md. 51 kartın dayandığı metinle aynı (2 iş günü matrícula, Séneca, boş yer koşulu aynen). Ancak bu sayfa orijinal yayın metnidir, konsolide metin değil. Junta normativa sayfası Decreto-ley 2/2021 (5 Şubat 2021, admisión normativasını "con carácter urgente" değiştiriyor) ve Orden de 11 de enero de 2026 (Orden 20/02/2020 md. 4.2'yi değiştiriyor) kayıtlarını listeliyor; bunların md. 51'e dokunup dokunmadığını doğrulayamadım.

**Türk okuyucu / bölge farkı:** kartta oturum izni/AB vatandaşlığı iddiası yok; yabancı çocuk kaydı için belge/ikamet şartı da kaynaklarda yok (SSS'de "extranjer" geçmiyor), dolayısıyla karta eklenmesi gerekmez, gaps.md konusu. Bölge farkı: kart zaten Endülüs'e özgü; çelişki yok. Ulusal kart (egitim-sistemi-zorunlu-egitim...) "başvuru takvimi bölgene göre değişir" diyor, çelişki yok.

## 2. ulasim: endulus-metropol-ulasim-konsorsiyum-kartlari-ve-interoperabilite (kaynak 009, 010)

**Konsorsiyum belirleme:** kaynak 009 = ctagr.es = Consorcio de Transporte Metropolitano Área de Granada (sayfa: "Tarjeta de Granada utilizada en Málaga ...", "utilizada en Granada: ... 2 saltos"). Kaynak 010 = ctmam.es = Consorcio de Transporte Metropolitano Área de Málaga. Karttaki "sabit 2 salto", "varış sorulmaz/sorulur", "en az beş euro, tüm konsorsiyumların satış noktaları" cümleleri 009'dan (Granada) gelir; 010 (Málaga) yalnız "resto de Consorcios Andaluces (Interoperatividad) en el marco tarifario establecido por cada Consorcio" ve kendi 5 euro yüklemesini söyler.

**2.1 ORTA, Granada'ya ait kural adsız "bir metropol alanı" diye veriliyor; "kendi alanında" okuyucuya kendi şehri gibi okunuyor.**
- Kart (özet): "Bir metropol alanının konsorsiyumunun sayfasına göre, kendi alanında başka bir Endülüs konsorsiyumunun kartı kullanıldığında varış sorulmaz ve sabit 2 salto tutarı alınır; o alanın kartı başka bir konsorsiyumun alanında kullanılırsa varış sorulur ve ücret varışa göre alınır."
- Kaynak 009: "Tarjeta de cualquier consorcio Andaluz utilizada en Granada: No se pregunta destino y se cobra un importe fijo equivalente a 2 saltos." ve "Tarjeta de Granada utilizada en Málaga/Cádiz/...: Se pregunta destino y se cobra en función de éste." Yani her iki cümle de yalnız Granada merkezli; Málaga, Sevilla, Cádiz vb. alanlar için kaynak yok.
- Not satırı "tutarlar kaynaktaki konsorsiyum sayfasına aittir" diyor ama hangi sayfa olduğu belli değil. Bölge kartında Granada kuralı bölge geneli kural gibi okunabilir.
- Düzeltme: "Granada metropol alanı (Consorcio de Granada) sayfasına göre: herhangi bir Endülüs konsorsiyumunun kartı Granada alanında kullanılırsa varış sorulmaz, sabit 2 salto alınır; Granada kartı diğer sekiz alandan birinde kullanılırsa varış sorulur" diye adıyla yaz; diğer alanlar için "kendi tarife çerçevesi" ifadesini 010'a dayandır.

**2.2 KÜÇÜK, steps 3 "varışın sorulup sorulmadığı alana göre değişir" ve 5 euro/tüm satış noktaları genellemesi.**
- Kaynak 009 yalnız Granada merkezli iki yönü anlatıyor; "alana göre değişir" ifadesi 8 alanın tamamı için kanıt gibi. "Kartı tüm konsorsiyumların satış noktalarında en az beş euro ile yükleyebilirsin; kartın hangi konsorsiyumdan olduğu fark etmez" yalnız 009'da ("Podrá recargar su tarjeta por un mínimo de cinco euros en cualquier punto de la red de ventas de todos los Consorcios, siendo indiferente la procedencia de la tarjeta"); 010 yalnız kendi alanı için "importe mínimo de 5€" ve 500 euro bakiye tavanı diyor. Çelişki yok, ama kaynak tek konsorsiyum; kart "Granada konsorsiyumuna göre" çerçevesi koymalı.

**2.3 KÜÇÜK, "salto" tanımsız.** Kaynak 009 da tanımlamıyor; 010 "número de saltos (0,1,2 ó 3)" yalnız bazı Sierra de las Nieves hatları için kart konfigürasyonu olarak geçiyor, farklı bağlam. Okuyucu "2 salto"nun kaç euro olduğunu anlayamaz; rakam uydurmak yasak, o yüzden "ücret Granada tarifesinde 2 salto karşılığıdır" diye yaz ya da cümleyi çıkar.

**2.4 KÜÇÜK, md. 6 ve 11: tarihe duyarlı tarife için "güncel tarife" etiketi yok; valid_until null.** (ctmam sayfası 2026-04-21 tarihli; ctagr sayfasında tarih yok.)

**2.5 KÜÇÜK, "bu kaynaklarda Endülüs genelini kapsayan tek bir kart tanımlanmaz" üst-bilgi (meta) cümlesi.** Kaynak 009'da "Tarjeta de cualquier consorcio Andaluz" ifadesi var; kart iddiasını kaynak yokluğuna dayandırıyor (md. 3'e yakın). Sil ya da "kart ilgili konsorsiyumundur" olarak yaz.

**Canlı kontrol:** ctagr ve ctmam metinleri kaynak snapshot ile aynı (2 salto, beş euro, 1,50 euro kart bedeli, 500 euro tavan görüldü). Aktarma (transbordo) ve tavan rakamları karta alınmamış; kartta ücret/aktarma rakamı yok, sorun yok.

## 3. gunluk: endulus-2027-resmi-tatilleri (kaynak 014)

Kart listesi BOJA 2026/84 (Decreto 84/2026, 29/04/2026, BOJA 05/05/2026) ekiyle BİREBİR: 12 gün, tarih ve gün adları aynı (1 Oca Cuma, 6 Oca Çarşamba, 1 Mart Pzt, 25 Mart Jueves Santo, 26 Mart Viernes Santo, 1 May Cumartesi, 16 Ağu Pzt, 12 Eki Salı, 1 Kas Pzt, 6 Ara Pzt, 8 Ara Çarşamba, 25 Ara Cumartesi). Kayma gerekçesi (28 Şubat ve 15 Ağustos Pazar'a denk gelir, ertesi Pazartesi'ye) ve "iki yerel tatil" (md. segundo, ET md. 37.2 14 gün sınırı) kaynakla uyumlu. Canlı BOJA sayfası kaynakla aynı. valid_until 2027-12-31 uygun.

**Ulusal kartla (resmi-tatiller-2027) çelişki: YOK.** Ulusal kartın ortak günleri (1 Oca, 26 Mar, 1 May, 12 Eki, 1 Kas, 6 Ara, 8 Ara, 25 Ara) ve 6 Oca, Endülüs listesinde de var; ulusal kart 15 Ağustos'u listelemiyor (Pazar), Endülüs'ün 16 Ağustos'u bölge kaydırması olarak tutarlı; Jueves Santo ulusal kartta "bölgeye göre değişir", Endülüs'te 25 Mart.

**3.1 KÜÇÜK, steps 1 "2027 iş ve okul planına işle".** Decreto fiestas laborales (iş) takvimidir; okul tatilleri ayrı takvimle belirlenir, kaynakta yok. Öneri: "okul" sözcüğünü çıkar.

**3.2 KÜÇÜK, steps 3 ile note aynı cümleyi tekrar ediyor; 1 Mayıs ve 25 Aralık'ın Cumartesi'ye denk geldiği ve kaydırılmadığı belirtilmemiş.** Kaynak listede "(sábado)" yazıyor ama kaydırma hükmü yalnız Pazar için; kart "ücretli, telafisiz" diyor, Cumartesi'ye düşen günde ek izin hakkı iddiası yok, bu yüzden hata değil; yalnız açıklama eksik.

## 4. resmi: endulus-carpeta-ciudadana-junta-dijital-islemler (kaynak 011)

Kaynak 011 kısa tanıtım (1060 karakter). Kartın tüm olgusal cümleleri kaynağın içinde: "Toda la Junta en una app", belgeler/sertifikalar indir-yazdır ("Descarga e imprime títulos, certificados y otros documentos oficiales"), randevu ("Reserva, consulta o modifica tus citas"), bildirimler, kartlar ("Familia numerosa, carné joven, tarjeta 65, de discapacidad y sanitaria"), expedientes, "Identifícate con Cl@ve o certificado digital", "aplicación web" ve mağaza uygulaması. Kart kaynağı AŞMIYOR. Canlı Junta sayfası aynı yapıda (6263 karakterlik temiz metin; içerik değişmemiş görünüyor).

**4.1 KÜÇÜK, Türk/yeni gelen okuyucu için giriş önkoşulu belirtilmemiş.** Kart "Girişte kimliğini Cl@ve ya da dijital sertifika ile doğrularsın" diyor; Cl@ve ve dijital sertifika için İspanyol kimlik/NIE-TIE kaydı gerekir ama bu kaynak 011'de yok, kartı genişletmek de yasak. Öneri: bu bilgi kartın kendi kaynağında olmadığı için gaps.md'ye yazılsın; kartta "Cl@ve ya da dijital sertifikan yoksa giriş yapamazsın" gibi kesin dil kullanılmıyor, iyi.

Başlık sorusu ("nedir ve nasıl girilir") ilk cümlede "nedir" ile cevaplanıyor, "nasıl girilir" ikinci planda; yasak kalıp, şehir adı, hesap yok.

## Özet tablo

| kart | ciddi | orta | küçük |
|---|---|---|---|
| aile (endulus-okul-kaydi-basvuru-donemi-ve-gec-gelen-ogrenci) | 0 | 3 | 2 |
| ulasim (endulus-metropol-ulasim-konsorsiyum-kartlari-ve-interoperabilite) | 0 | 1 | 4 |
| gunluk (endulus-2027-resmi-tatilleri) | 0 | 0 | 2 |
| resmi (endulus-carpeta-ciudadana-junta-dijital-islemler) | 0 | 0 | 1 |
| TOPLAM | 0 | 4 | 9 |

Bakılamayan: Decreto 21/2020 md. 51'in konsolide/güncel hali (yalnız orijinal BOJA yayın metni açıldı; Decreto-ley 2/2021 etkisi doğrulanamadı); ctan/diğer konsorsiyum sayfaları (Sevilla, Cádiz vb., ctan.es 403 verdi) açılmadı.
