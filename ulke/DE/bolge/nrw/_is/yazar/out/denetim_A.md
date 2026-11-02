# NRW bölge paketi — bağımsız denetim A (gunluk, aile, saglik; 8 kart)

Tarih: 02.11.2026. Denetçi yazarın gaps.md dosyalarını okumadı; hiçbir kart dosyasına dokunmadı.

## Özet
- Ciddi: 0. Orta: 6. Küçük: 17.
- Yöntem: her kartın her cümlesi kendi source_ids kaynaklarının indirilmiş metniyle (kaynak_dizini.jsonl → text_file) karşılaştırıldı; claims'ten kart başına ≥3 (çoğunda tümü) quote anlam kontrolü yapıldı; ulusal kartlarla (resmi-tatiller-3-ekim-ve-eyalet-farki, magaza-acilis-saatleri-pazar-kapali-federal-kural, kita-hakki-1-yasindan-itibaren-ucret-ve-kayit, okul-zorunlulugu-ve-okul-sistemi-cercevesi, cocuk-asilari-kizamik-zorunlulugu-cocuk-muayeneleri) çakışma/çelişki baktı. Ulusal kartı tekrarlayan ya da onunla çelişen NRW kartı yok; başka eyalet adı, şehir adı, şehir listesi yok.
- Tarih, hesap, "yaklaşık" araştırması: tatil kartında kaynakta olmayan tarih/hesap YOK (okul tatili tarihlerinin hepsi BASS tablosuyla birebir; resmî tatil kartında tarih hesabı yok). Kita kartı yalnız KiBiz metnine dayanıyor ve 01.08.2026 sürümü doğru. HSU kartında kaynakta olmayan katılım şartı ya da başvuru usulü UYDURULMAMIŞ (kayıt usulü hiç anlatılmıyor; kaynak da anlatmıyor). U muayenesi kartında kurum adı (LfGA NRW) ve bütün süreler kaynakla aynı.
- Canlı açılan sayfalar (WebFetch, 02.11.2026): recht.nrw.de Feiertagsgesetz (tek sürüm 01.01.2000, § 2/§ 6 Abs. 2 doğrulandı); recht.nrw.de LÖG NRW (sürümler 30.03.2018 / 18.05.2013 / 21.11.2006; 30.03.2018 en yeni; § 4, 5, 6 doğrulandı); bass.schule.nrw/191.htm (tatil tarihleri, 3 hareketli gün, karne tarihleri; Eingearbeitet 14.10.2024); recht.nrw.de KiBiz (sürümler 01.08.2027 / 01.08.2026 güncel, geçerli 31.07.2027'ye kadar / 01.08.2022 / 01.08.2020; 01.08.2027 sürümünün § 50 Abs. 1'i canlı sayfada aynı içerikte görünüyor); recht.nrw.de SchulG (en yeni 01.08.2026, sonraki sürüm yok); bass.schule.nrw/16253.htm (HSU, yürürlükte); bass.schule.nrw/18425.htm (neu zugewandert, Eingearbeitet 6.12.2023); lzg.nrw.de Zentrale Stelle (telefon, saat, tablo aynı; e-posta lfga.nrw.de); recht.nrw.de UTeilnahmeDatVO (en yeni 02.07.2025).
- Bakılmayanlar: schulministerium.nrw Türkçe sayfası (008) ayrıca canlı açılmadı (indirilmiş kopya okundu); KiBiz 01.08.2027 sürümünün tamamı (yalnız § 50/51 canlı bakıldı); SchulG § 37 (okul zorunluluğu süresi) kaynağa girmediği için bakılmadı.
- Genel claims notu: script yalnız alıntının metinde geçtiğine bakar; şu quote'lar iddiayı tam kanıtlamıyor (küçük): tatiller-14 ("§ 6 Stille Feiertage" başlığı Allerheiligen'i anmıyor; § 6 Abs. 2 cümlesi alıntılanmalı), kita-5 (alıntı "…durch Kinder," diye yarım kalıyor, ücretsizlik koşulunu göstermiyor), okul-sistemi-8 (quote "Schuleinzugsbereich oluşturmamışsa" kısmını kanıtlamıyor; metinde var ama claim yok), u-muayene-1 (quote yalnız amaç cümlesi).

---

### nrw-resmi-tatiller: küçük
- Bulgu (T1): Not "yasanın Absatz 1'de saydığı etkinlikler yasaktır" diyor ama Absatz 1'in ne olduğunu söylemiyor; okur hangi etkinliklerin yasak olduğunu anlayamaz (kaynakta: pazar/gösteri/spor/eğlence/dans, bahis salonu, gaststätte müziği vb., Volkstrauertag için 5-13 ve 5-18 karışık; Allerheiligen için hepsi 5-18). Bunun dışında kart kaynakla uyumlu: 11 tatil birebir, Volkstrauertag/Totensonntag anma günü, valid_until null (yasada bitiş yok) doğru, ulusal 3 Ekim kartıyla çelişki yok.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01012000-bekanntmachung-der-neufassung-des-gesetzes-ueber-die-sonn-und-feiertage/ "(2) Am Allerheiligentag und am Totensonntag sind zusätzlich verboten: alle in Absatz 1 genannten Veranstaltungen von 5 Uhr bis 18 Uhr." ; "(1) … 2. sportliche und ähnliche Veranstaltungen einschließlich Pferderennen … Volksfeste … 5. alle anderen der Unterhaltung dienenden öffentlichen Veranstaltungen einschließlich Tanz von 5 Uhr bis 18 Uhr."
- Düzeltme: Notta "Absatz 1'de saydığı etkinlikler" yerine kaynaktaki türleri yaz: "pazar yeri/ticari fuar, spor ve benzeri etkinlikler, halk şenlikleri, bahis ve oyun salonları, lokallerde müzik ve eğlence, dans". claim 14 quote'unu § 6 Abs. 2 cümlesiyle değiştir.

### nrw-magaza-acilis-saatleri-ve-acik-pazar: orta
- Bulgu (M1): Başlık "açık pazar (verkaufsoffener Sonntag) kaç gün?" diye soruyor, kart yalnız "bir mağaza yılda en çok sekiz" diyor. Kaynaktaki belediye sınırı (bir belediyede yılda en çok 16 Pazar/tatil; tüm belediye alanı için yalnız bir Advent Pazarı; belirli bölge/sektör için en çok iki Advent Pazarı) kartta YOK; oysa claims 13 (16 gün) ve 14 (Advent) bu kart için yazılmış ve karta girmemiş (claim–kart tutarsızlığı). Ayrıca § 6 Abs. 5 uyarınca serbest bırakılamayan günler (sessiz tatiller, Ostersonntag, Pfingstsonntag, 1.–2. Noel günü, 1 Mayıs, 3 Ekim, Pazar'a düşen 24 Aralık) yok; "Pazar ve tatilde yalnızca yasada sayılan dükkânlar" cümlesi § 5 Abs. 1 Nr. 2'yi (kültür/spor etkinliği ve müze alanındaki dükkânlar) atlıyor ve kaynaktaki Kurort/turizm yerleri istisnasını (§ 6 Abs. 2: yılda en çok 40 gün, 8 saat) hiç anmıyor. Okur "kaç gün" sorusuna eksik cevap alır.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/30032018-gesetz-zur-regelung-der-ladenoeffnungszeiten-ladenoeffnungsgesetz-loeg-nrw/ "Innerhalb einer Gemeinde dürfen nach Absatz 1 insgesamt nicht mehr als 16 Sonn- und Feiertage je Kalenderjahr freigegeben werden." ; "Erfolgt eine Freigabe nach Absatz 1 für das gesamte Gemeindegebiet, darf dabei nur ein Adventssonntag freigegeben werden." ; "Von der Freigabe der Tage nach Absatz 1 und 4 sind ausgenommen: 1. die stillen Feiertage …" ; "2. Verkaufsstellen von themenbezogenen Waren oder Waren zum sofortigen Verzehr auf dem Gelände oder im Gebäude einer Kultur- oder Sport-Veranstaltung oder in einem Museum" ; "an jährlich höchstens 40 Sonn- oder Feiertagen bis zur Dauer von acht Stunden geöffnet sein."
- Düzeltme: Özete ekle: "Bir belediye yılda en çok 16 Pazar ya da tatili serbest bırakabilir; tüm belediye için yalnız bir Advent Pazarı serbest olabilir. Paskalya ve Pfingsten Pazarı, 1.–2. Noel günü, 1 Mayıs, 3 Ekim ve sessiz tatiller serbest bırakılamaz." Sayılan dükkân listesine "kültür/spor etkinliği ve müze alanındaki dükkânlar, etkinlik süresince" ekle ya da "yalnızca" sözcüğünü kaldır. Kurort istisnası şehir listesi gerektirdiği için karta yazılmayacaksa tek cümle "turizmin yoğun olduğu kimi yerlerde farklı kural vardır" bile yazılmasın (kaynaksız genelleme olmasın); bu durumda gaps'e gider. claims 13/14 ya karta girmeli ya claims'ten çıkarılmalı.

### nrw-magaza-acilis-saatleri-ve-acik-pazar: küçük
- Bulgu (M2): Özet ve alt başlık "Pazar ve resmî tatil dışındaki günlerde açılış saati sınırı yoktur" diyor; kaynakta 24 Aralık Werktag'a düşerse 14:00 sınırı var. Not bunu söylüyor, ama özet kesin konuşuyor (Kural 8).
- Kanıt: https://recht.nrw.de/lrgv/gesetz/30032018-gesetz-zur-regelung-der-ladenoeffnungszeiten-ladenoeffnungsgesetz-loeg-nrw/ "2. am 24. Dezember an Werktagen bis 14 Uhr geöffnet sein"
- Düzeltme: Özete "(24 Aralık hariç; o gün 14:00'e kadar)" ekle.

### nrw-okul-tatilleri-2026-27-ve-2027-28: küçük
- Bulgu (O1): Tüm tatil tarihleri, haftanın günleri, Pfingsten 18 Mayıs 2027, "2027/28 Pfingsten yok", karne tarihleri BASS tablosuyla birebir (canlı da doğrulandı). Tek sorun: özet "Her okul ayrıca bu iki okul yılında üç hareketli tatil günü kullanır" — kaynakta okul yılı başına üç; cümle "iki yılda toplam üç" diye de okunabilir.
- Kanıt: https://bass.schule.nrw/191.htm "Der einzelnen Schule stehen in den Schuljahren 2026/27 und 2027/28 drei und in den Schuljahren 2028/29 und 2029/30 vier bewegliche Ferientage zur Verfügung."
- Düzeltme: "Her okul bu iki okul yılının her birinde üç hareketli tatil günü kullanır."

### nrw-okul-tatilleri-2026-27-ve-2027-28: küçük
- Bulgu (O2): Karne tarihi kaynakta "Berufsschule bildungsgang hariç" kısıtıyla veriliyor; kart kısıtı yazmıyor (Berufskolleg'in Berufsschule kolu da kart okuru için gelir). Ayrıca 02.11.2026 itibarıyla 2026/27 yaz ve sonbahar tatilleri geçmiş durumda; kart "planning" aşamasına da etiketli, hata değil ama özetin ilk cümlesi geçmiş tarihle başlıyor (editör isterse en yakın tatilleri öne alabilir).
- Kanıt: https://bass.schule.nrw/191.htm "Berufskollegs (mit Ausnahme des Bildungsgangs Berufsschule)"
- Düzeltme: Notun sonuna "Berufsschule eğitim kolunda bu tarih geçerli değildir" ekle. valid_until 2028-04-22 doğru.

### nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem: orta
- Bulgu (K1): Ücretsizlik kuralı "aynı takvim yılında başlayan Kindergartenjahr'ın başından" diyor, ama Kindergartenjahr'ın 1 Ağustos'ta başladığı (yasada tanımlı) hiçbir yerde yazılmıyor. Okur "30 Eylül'e kadar 4 yaşını dolduracak" çocuğun hangi tarihten itibaren ücretsiz olduğunu hesaplayamaz; Türkçe okur için "Kindergartenjahr" terimi de açıklanmamış.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/ "Ein Kindergartenjahr entspricht dem Schuljahr, es beginnt am 1. August und endet am 31. Juli des folgenden Jahres." ; "Kinder, die bis zum 30. September das vierte Lebensjahr vollendet haben werden, ist ab Beginn des im selben Kalenderjahr beginnenden Kindergartenjahres bis zur Einschulung beitragsfrei."
- Düzeltme: Özet ve timing'e "Kindergartenjahr 1 Ağustos'ta başlar (okul yılıyla aynıdır)" ekle; claim ekle.

### nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem: orta
- Bulgu (K2): Adım 4 "yemek dışında ek katılım ücreti alınamaz" diyor. Kaynakta bu yasak yalnız KiBiz ile bezuschusste edilen Kita'lar ve § 23 SGB VIII Kindertagespflege için geçerli ve "Jugendamt'ın belirlediği Elternbeitrag" dışındaki "weitere Teilnahmebeiträge" için; Elterninitiativen'in Mitgliederbeiträge'si açıkça kapsam dışı. Kart kapsamı bilmeden genelleştiriyor ve ücretli dönemde (Jugendamt Elternbeitrag alırken) "ek ücret alınamaz" cümlesi okuru yanıltabilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/ "Für die Betreuung in Kindertageseinrichtungen, die nach diesem Gesetz finanziell bezuschusst werden … sind mit Ausnahme von möglichen Entgelten für Mahlzeiten weitere Teilnahmebeiträge der Eltern ausgeschlossen." ; "Mitgliederbeiträge für Elterninitiativen gemäß § 36 Absatz 2 Nummer 3 sind keine Teilnahme- oder Kostenbeiträge im Sinne dieser Vorschrift."
- Düzeltme: Adım 4'ü "KiBiz ile desteklenen bir Kita'da, Jugendamt'ın belirlediği Elternbeitrag ve yemek ücreti dışında başka katılım ücreti alınamaz; ebeveyn girişimi (Elterninitiative) Kita'larında üyelik aidatı bu yasağın dışındadır" diye daralt.

### nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem: küçük
- Bulgu (K3): (a) Özetin ilk cümlesi "ücretini … yalnızca Jugendamt belirler" diyor; yemek ücretini işletmeci isteyebiliyor (cost alanı bunu söylüyor, özet söylemiyor). (b) "Jugendamt ücreti gelire göre kademelendirir" kaynakta koşullu: Jugendamt Elternbeitrag ALIRSA kademelendirmek zorunda; kart bunu "ücret alır ve kademelendirir" gibi yazıyor.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/ "Erhebt das Jugendamt Elternbeiträge für die Inanspruchnahme von Kindertageseinrichtungen oder Kindertagespflege, hat es eine soziale Staffelung vorzusehen" ; "Der Träger der Kindertageseinrichtung kann ein Entgelt für Mahlzeiten verlangen."
- Düzeltme: "Elternbeitrag'ı (yemek hariç) yalnızca Jugendamt belirler" ve "Jugendamt ücret alıyorsa gelire göre kademelendirmek zorundadır".

### nrw-kita-ucreti-jugendamt-ve-ucretsiz-donem: küçük
- Bulgu (K4): Kardeş indirimi adımı eksik bırakıyor: kaynağa göre ücretsiz çocuk kardeş indiriminde ücret ödüyormuş gibi sayılır ve aile hem kardeş indiriminden hem ücretsizlikten tam yararlanmalıdır (okur için somut hak). Ayrıca kita-5 claim quote'u yarım ("…durch Kinder,").
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-gesetz-zur-fruehen-bildung-und-foerderung-von-kindern-kinderbildungsgesetz/ "Bei Ermäßigungsregelungen für Geschwister ist sicherzustellen, dass die Familie sowohl in vollem Umfang von diesen Ermäßigungen als auch von der Elternbeitragsbefreiung nach § 50 profitiert."
- Düzeltme: Adım 5'e bu cümleyi ekle; claim 5 quote'unu "ist ab Beginn des im selben Kalenderjahr beginnenden Kindergartenjahres bis zur Einschulung beitragsfrei" ile tamamla.
- Güncellik notu: 01.08.2026 sürümü şu an geçerli; kaynak sayfa 01.08.2027 sürümünü de listeliyor (Art. 2, 21.07.2026 yasası); § 50 Abs. 1 oradaki canlı metinde aynı içerikte, yani valid_until 2027-07-31 uygun, 01.08.2027 sonrası için yeniden bakılmalı.

### nrw-okul-sistemi-ve-yeni-gelen-cocugun-okula-yerlesmesi: küçük
- Bulgu (S1): "Gymnasium (10. sınıfa kadar)" kaynağın yarısı: yasa Gymnasium'un Sekundarstufe I'de 9. sınıfa kadar da yürütülebileceğini söylüyor. Ayrıca başlık "okul zorunlu mu" diye soruyor ama zorunluluğun süresi (kaynak § 34'te değil, § 37'de; kartın kaynağında yok) verilmiyor; ulusal kart "en az dokuz yıl" diyor, NRW kartı sessiz — çelişki yok, eksik.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "Die Sekundarstufe I umfasst die Hauptschule, die Realschule, die Sekundarschule sowie die Gesamtschule und das Gymnasium bis Klasse 10. Das Gymnasium kann in der Sekundarstufe I auch bis Klasse 9 geführt werden."
- Düzeltme: "Gymnasium (Sekundarstufe I'de 10. sınıfa, bazı okullarda 9. sınıfa kadar)". Süre için § 37 kaynak olarak eklenirse yazılır; yoksa yazılmaz.

### nrw-okul-sistemi-ve-yeni-gelen-cocugun-okula-yerlesmesi: küçük
- Bulgu (S2): 01.08.2026 SchulG sürümünde § 36 Abs. 3 yeni: kayıtta okul Almanca düzeyini saptar ve yetersizse bir önceki okul yılında okulun Vorkurs'una katılmayı zorunlu kılar; Abs. 6'ya göre bu yükümlülük 1 Ağustos 2029'dan önce okul zorunlusu olacak çocuklar için uygulanmaz. Kart yalnız Abs. 2'yi (Schulamt, iki yıl önce, Sprachförderkurs) yazıyor; Abs. 2 doğru, ama 2026 sürümüyle gelen yeni usulden hiç söz edilmiyor. Şimdilik uygulanmadığı için küçük.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "Die Verpflichtung nach § 36 Absatz 3 Satz 2 gilt nicht für Kinder, die vor dem 1. August 2029 schulpflichtig werden."
- Düzeltme: Ya sil/yalnız geçiş notunu ekle ("2029'dan itibaren okul kayıtta saptayıp Vorkurs zorunlu kılacak") ya da gaps'e yaz.

### nrw-okul-sistemi-ve-yeni-gelen-cocugun-okula-yerlesmesi: küçük
- Bulgu (S3): Adım 2'deki "Schulträger Schuleinzugsbereich oluşturmamışsa geçerlidir" şartı doğru (§ 46 Abs. 3) ama hiçbir claim bunu kanıtlamıyor (claim 7-8 quote'ları o kısmı içermiyor).
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "soweit der Schulträger keinen Schuleinzugsbereich gebildet hat"
- Düzeltme: Claim 8 quote'unu bu cümleyle genişlet.

### nrw-turkce-anadil-dersi-hsu: orta
- Bulgu (H1): YANLIŞ ÇEVİRİ. Adım 5'te "eksik bir yabancı dil notunu telafi edebilir" yazıyor. Kaynaktaki "mangelhafte Leistung" 5 numaralı yetersiz nottur; "eksik" Türkçede eksik/boş not anlamı verir (not alınmamış gibi). Doğrusu "yetersiz (mangelhaft) bir yabancı dil notu". Ayrıca hangi mezuniyetler: Hauptschulabschluss 9. ve 10. sınıf sonrası ile Mittlerer Schulabschluss (kart "bazı mezuniyetlerde" diyor, doğru ama belirsiz).
- Kanıt: https://bass.schule.nrw/16253.htm "Schülerinnen und Schüler können mit einer mindestens guten Leistung in der Sprachprüfung bei der Vergabe der Abschlüsse nach §§ 40 bis 42 APO-S I (Hauptschulabschluss nach Klasse 9, Hauptschulabschluss nach Klasse 10, Mittlerer Schulabschluss) eine mangelhafte Leistung in einer Fremdsprache ausgleichen."
- Düzeltme: "en az iyi bir Sprachprüfung notu, 9. ya da 10. sınıf sonrası Hauptschulabschluss ile Mittlerer Schulabschluss verilirken yetersiz (mangelhaft) bir yabancı dil notunu dengeleyebilir."

### nrw-turkce-anadil-dersi-hsu: orta
- Bulgu (H2): Not "HSU'yu Sekundarstufe I sonundaki sınavla başarıyla bitirenler … gymnasiale Oberstufe'de Türkçeye devam edebilir" diyor. Kaynak 007'ye göre koşul daha dar: Mittlerer Schulabschluss anspruch düzeyinde sınavda en az "ausreichend" not. Hauptschul düzeyinde sınava girenler bu hakkı kazanmaz; veli için önemli şart eksik. (008 sayfası genel konuşuyor; 007 ayrıntıyı veriyor ve kartın kendi kaynağı.)
- Kanıt: https://bass.schule.nrw/16253.htm "Bei Erreichen einer mindestens ausreichenden Note in der Sprachprüfung im Herkunftssprachlichen Unterricht auf dem Anspruchsniveau des Mittleren Schulabschlusses kann diese Sprache in der gymnasialen Oberstufe als fortgeführte Fremdsprache belegt werden, sofern ein entsprechendes Angebot besteht."
- Düzeltme: "Sprachprüfung'u Mittlerer Schulabschluss düzeyinde en az 'yeterli' (ausreichend) notla geçenler, okulda teklif varsa Oberstufe'de Türkçeyi sürdürebilir."

### nrw-turkce-anadil-dersi-hsu: küçük
- Bulgu (H3): Özet "Sekundarstufe I'de … en az 18 öğrencilik grup kurulabilirse açılır" der; kaynak "kann stattfinden" (yapılabilir), ilkokulda ise "wird angeboten". Kart iki düzeyi aynı kesinlikte yazıyor (Kural 8).
- Kanıt: https://bass.schule.nrw/16253.htm "kann stattfinden, wenn in der Sekundarstufe I mindestens 18 Schülerinnen und Schüler gleicher Herkunftssprache dauerhaft teilnehmen"
- Düzeltme: "Sekundarstufe I'de … en az 18 öğrenci kalıcı katılırsa ders yapılabilir."

### nrw-turkce-anadil-dersi-hsu: küçük
- Bulgu (H4): Altbaşlık ve not "not karneye yazılır / Bemerkungen" diyor; kaynakta bu ara karne ve genel durum. Mezuniyet belgesinde (Abschlusszeugnis) not "Leistungen" bölümünde ve Sprachprüfung'a dayandığı Bemerkungen'de belirtilir; Grundschule Schuleingangsphase'te not yerine öğrenme gelişimi açıklaması yazılır; sınavı geçemeyen katılım belgesi alır.
- Kanıt: https://bass.schule.nrw/16253.htm "Die Note wird im Abschlusszeugnis unter „Leistungen“ bescheinigt." ; "In den Zeugnissen der Schuleingangsphase der Grundschule wird statt der Leistungsnote eine Aussage über die Lernentwicklung … aufgenommen."
- Düzeltme: Altbaşlığı "katılım ve not karneye işlenir" yap; nota bir cümle ekle ("Abschlusszeugnis'te not 'Leistungen' bölümüne yazılır; sınav geçilmezse katılım belgesi verilir").

### nrw-turkce-anadil-dersi-hsu: küçük
- Bulgu (H5): Türk okur için kaynakta olan ama kartta olmayan bilgi: konsolosluğun kendi dersi (Konsulatsunterricht) izin gerektirmez; NRW müfredatına göre verilmiş ve düzenli katılınmışsa öğrenci NRW Sprachprüfung'una girebilir (konsolosluk belgesi şartıyla). HSU'ya bir seçenek olarak okura yararlı; eksiklik olarak not edilir. Uydurulmuş katılım şartı ya da başvuru usulü bulunmadı.
- Kanıt: https://bass.schule.nrw/16253.htm "Der Herkunftssprachliche Unterricht eines ausländischen Konsulats bedarf keiner Genehmigung." ; "Voraussetzung ist die Vorlage einer Bescheinigung durch das Konsulat an die Schulaufsicht."
- Düzeltme: İstenirse nota iki cümle ekle; eklenmeyecekse gaps'e.

### nrw-u-muayeneleri-takip-sistemi-zentrale-stelle: küçük
- Bulgu (U1): Timing'de "beş iş günü" yazıyor; kaynak "Werktage" (Pazartesi-Cumartesi). Kurum adı (LfGA NRW), telefon, saat, Toleranz tablosu, 14 gün/10 gün/6 hafta, 4 ay saklama hepsi kaynak ve canlı sayfayla aynı.
- Kanıt: https://recht.nrw.de/lrgv/rechtsverordnung/02072025-verordnung-zur-datenmeldung-der-teilnahme/ "innerhalb von fünf Werktagen die folgenden Daten"
- Düzeltme: "beş Werktag (Pazartesi–Cumartesi) içinde".

### nrw-u-muayeneleri-takip-sistemi-zentrale-stelle: küçük
- Bulgu (U2): Kart "Jugendamt bilgilendirilir" diyor; yönetmelik "örtlicher Träger der öffentlichen Jugendhilfe", kaynak 010 ise "Kommune" diyor. Eşdeğerlik makul ama iki kaynakta da "Jugendamt" sözcüğü geçmiyor; ayrıca Jugendamt'ın o aşamada yalnız aileyi Jugendhilfe hizmetleri konusunda bilgilendirdiği ve kendi yetkisiyle karar verdiği (kaynak 010: temas kurup kurmayacağına belediye karar verir) not'ta var ama özet "bilgilendirilir" ile yetinirken okuru gerçek sonuç konusunda belirsiz bırakabilir.
- Kanıt: https://www.lzg.nrw.de/ges_foerd/kindergesundheit/zentrale-stelle/index.html "informiert die Zentrale Stelle die Kommune … Die Kommune wird dann in eigener Zuständigkeit prüfen und entscheiden, ob sie mit den Eltern/Sorgeberechtigten Kontakt aufnimmt."
- Düzeltme: Özete "yerel gençlik yardımı makamı (Jugendamt) bilgilendirilir; o, aileyle iletişime geçip geçmeyeceğine kendisi karar verir" ekle.

### nrw-u-muayeneleri-takip-sistemi-zentrale-stelle: küçük
- Bulgu (U3): Adım 4 "doktorun bildirimini sağla" diyor; bildirimi doktor yapar, veli sağlayamaz. Ayrıca yönetmelik § 3 Abs. 4 ciddi tıbbi gerekçede süreleri uzatma/çocuğu usulden çıkarma imkânı veriyor (kartta yok, küçük).
- Kanıt: https://recht.nrw.de/lrgv/rechtsverordnung/02072025-verordnung-zur-datenmeldung-der-teilnahme/ "Bei Vorliegen gewichtiger medizinischer Gründe kann die Zentrale Stelle die Fristen nach Absatz 3 und § 4 Absatz 1 entsprechend anpassen oder im Einzelfall die Daten eines Kindes aus dem Verfahren nehmen."
- Düzeltme: "muayeneyi yaptırdığında doktorun bildirim yaptığından emin ol (gerekirse Zentrale Stelle'den sor)".

### nrw-okul-girisi-saglik-muayenesi-ve-saglik-nedeniyle-erteleme: orta
- Bulgu (G1): Başlık "okula başlarken sağlık muayenesini kim yapar" diyor; kartın kendi kaynağı muayeneye katılmanın ZORUNLU olduğunu söylüyor, kart bunu yazmıyor. Okur muayeneye katılıp katılmamayı seçebileceğini düşünebilir.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "Die Schülerinnen und Schüler sind verpflichtet, sich bei schulärztlichen und schulzahnärztlichen Reihenuntersuchungen, insbesondere zur Einschulung, untersuchen zu lassen."
- Düzeltme: Özete "Einschulung toplu muayenesi ve okul diş muayenesine katılmak yasal yükümlülüktür" ekle; adımlara yansıt; claim ekle.

### nrw-okul-girisi-saglik-muayenesi-ve-saglik-nedeniyle-erteleme: küçük
- Bulgu (G2): Başlıktaki ikinci soru ("sağlık nedeniyle erteletebilir miyim") ilk cümlede cevaplanmıyor; cevap özetin sonunda ve koşullu: karar okul müdürünün; veli yalnız incelemeyi isteyebilir. İlk cümle "Evet ama karar sende değil" tonunda olmalı (Kural 4).
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "Die Entscheidung trifft die Schulleiterin oder der Schulleiter auf der Grundlage des amtsärztlichen Gutachtens. … Die Prüfung kann auch auf Antrag der Eltern erfolgen."
- Düzeltme: Özeti "Okul doktorunu sağlık makamı atar ve toplu muayene o hizmete girer; ciddi sağlık gerekçesiyle bir yıl erteleme mümkündür ama kararı okul müdürü amtsärztliches Gutachten'e dayanarak verir, veli incelemeyi isteyebilir" biçiminde yeniden sırala.

### nrw-okul-girisi-saglik-muayenesi-ve-saglik-nedeniyle-erteleme: küçük
- Bulgu (G3): "alt düzey sağlık makamları (untere Gesundheitsbehörden)" Türkçe okura hiçbir şey söylemiyor; hangi kurumun (Gesundheitsamt) muayeneyi yaptığı kaynakta açık yazılı değil. Uydurmamak doğru; ama "makam" sözcüğü okuru bir işlem yapamaz bırakıyor.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01082026-schulgesetz-nrw-schulg/ "Die Aufgaben der Schulgesundheitspflege nehmen die unteren Gesundheitsbehörden in Zusammenarbeit mit der Schule und den Eltern wahr."
- Düzeltme: Kaynakta bulunmayan "Gesundheitsamt" ifadesi eklenecekse ÖGDG NRW gibi resmî kaynak eklenip claim yazılmalı; aksi halde "yerel sağlık makamı (kreis/şehir düzeyinde)" gibi kaynaksız tanım yazılmamalı, olduğu gibi bırakılıp gaps'e not düşülmeli.
