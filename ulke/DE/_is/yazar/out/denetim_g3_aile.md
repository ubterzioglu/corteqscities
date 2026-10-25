# Denetim G3 — Almanya ulusal paketi, konu "aile" (8 kart)

Denetçi: bağımsız (kartları yazmadım, gaps.md okumadım). Tarih: 2026-10-25.

## Özet
- Kart: 8. Bulgu: 22 (ciddi 2, orta 10, küçük 10).
- En önemli iki bulgu kart 907'de (Unterhaltsvorschuss ve Kinderzuschlag): yabancı için kaynaktaki şartlar kart metninde yok ya da yanıltıcı kalmış.
- Orta bulguların çoğu "kaynakta olan şart karta girmemiş" türünden: Kindergeld'de geriye dönük 6 ay sınırı, Elterngeld'de yabancı şartı ve Partnermonate şartı, Kita'da Ganztag hakkının kapsamı, BAföG'da tutarın ne anlama geldiği ve oturum izni listesi.
- Sayılar (259, 297, 227/299/394, 475/380/59/442) kaynakla ve canlı yasayla uyumlu. Yanlış tutar bulunmadı. Havale cümlesi, şehir adı, eyalet adı/rakamı bulunmadı (regex ve elle tarandı). Dil sınıfı genellemesi yok.

## Yöntem
- Her kartın summary/steps/documents/timing/cost/note cümleleri, kartın kendi source_ids kaynaklarının `text_file` metniyle satır satır karşılaştırıldı (16 kaynak: 225, 245, 228, 229, 232, 233, 238, 236, 239, 240, 241, 242, 243, 244, 234, 141).
- claims.aile.jsonl'in 159 iddiasının tamamı (yalnız örnekleme değil) quote–iddia anlamı açısından okundu. Quote'lar iddiayı genelde kanıtlıyor; sorunlar aşağıda ilgili kartta.
- Canlı karşılaştırma (Python urllib, 2026-10-25): indirilmiş kopyalar ile canlı sayfalar cümle düzeyinde karşılaştırıldı; içerik farkı yok (yalnız menü/çerez metni farklı).
- Çapraz kontrol: resmi/209 (doğum kaydı) ve saglik/602 (aile sigortası) kartları okundu.

## Canlı açılan sayfalar
- gesetze-im-internet.de: EStG §62, EStG §66 ("Das Kindergeld beträgt monatlich für jedes Kind 259 Euro."), BEEG §1, BAföG §8, §13, SGB VIII §24, SGB V §10, UhVorschG §2, BKGG §1, §6a
- familienportal.de: Kindergeld/ausländische Eltern (124928), Elterngeld Dauer (124728), Elterngeld Antrag (124762), Unterhaltsvorschuss, Elternzeit-Übersicht
- arbeitsagentur.de: Kindergeld Anspruch/Höhe/Dauer, Kinderzuschlag Anspruch/Höhe/Dauer

## Bakılmayanlar
- 404 verenler: gesetze MindUntV (2026 Mindestunterhalt) ve arbeitsagentur "Kindergeld für Menschen im oder aus dem Ausland". Bu yüzden Unterhaltsvorschuss tutarlarının 2026 için değişip değişmediği canlı resmî kaynakla doğrulanamadı. Familienportal sayfası hâlâ "ab 1. Januar 2025" diyor, yani kart etiketi kaynağa uygun.
- bafög.de (bağlantı sıfırlandı); kapalı siteler (bmi.bund.de, make-it-in-germany.com, auswaertiges-amt.de) denenmedi.
- Elternzeit (iş güvencesi, süre) için ayrı kart yok; bu bir kart hatası değil, konu boşluğu (aşağıda not).
- Türkiye nüfus kaydı / konsolosluk bildirimi (908 için) kaynaksız olduğundan değerlendirilmedi.

---

### kindergeld-tutar-ve-yabanci-icin-hak-sartlari: orta
- Bulgu: "Eğitim amacıyla kalanlar ... Kindergeld alamaz" (summary, steps) koşulsuz yazılmış. Yasada öğrenim izni (§16b) ile kalan, çalışıyorsa, Elternzeit ya da SGB III parası alıyorsa dışlanmaz; yalnız bu üçünden hiçbiri yoksa dışlanır. Au-pair/mevsimlik/§16e gibi izinler ise koşulsuz dışlanır. Kaynak sayfa (225) da kısa yazıyor, ama kart "bazı izinlerde çalışma şartı" cümlesini bu istisnayla bağlamıyor. Öğrenci olarak çalışan Türk okuyucu hak kaybına gidebilir. Ayrıca summary'de Beschäftigungsduldung istisnası yok (steps'te var).
- Kanıt: https://www.gesetze-im-internet.de/estg/__62.html "nach § 16b des Aufenthaltsgesetzes zum Zweck eines Studiums, ... erteilt und er ist weder erwerbstätig noch nimmt er Elternzeit nach § 15 des Bundeselterngeld- und Elternzeitgesetzes oder laufende Geldleistungen nach dem Dritten Buch Sozialgesetzbuch in Anspruch"
- Düzeltme: "Eğitim amacıyla kalanlar alamaz" yerine: "Öğrenim amaçlı oturum izniyle kalıyorsan, aynı zamanda çalışmıyor, Elternzeit kullanmıyor ve işsizlik parası (SGB III) almıyorsan Kindergeld alamazsın." Summary'ye "Beschäftigungsduldung hariç" ekle.

### kindergeld-tutar-ve-yabanci-icin-hak-sartlari: orta
- Bulgu: Başvuru süresi/geriye dönük ödeme sınırı yok; kartın timing alanında yalnız "Tutar 1 Ocak 2026'dan itibaren" yazıyor. Kartın kendi "Başvur" bağlantısı olan Familienkasse sayfası geriye dönük ödemeyi 6 ayla sınırlıyor; geciken başvuru para kaybettirir. (Kaynak 245/225'te yok; 6 ay bilgisi için bu sayfa kaynak olarak eklenmeli, kart başına 2 kaynak sınırı için 245 yerine değiştirilebilir.)
- Kanıt: https://www.arbeitsagentur.de/familie-und-kinder/infos-rund-um-kindergeld/kindergeld-anspruch-hoehe-dauer "Die Frist zur rückwirkenden Zahlung von Kindergeld beträgt 6 Monate."
- Düzeltme: timing'e ekle: "Kindergeld geriye dönük en çok 6 ay ödenir; başvuruyu geciktirme." ve bu sayfayı source_ids'e al (claim ekle).

### kindergeld-tutar-ve-yabanci-icin-hak-sartlari: küçük
- Bulgu: "Türkiye vatandaşıysan Kindergeld için sosyal sigortalı çalışman ... gerekir" tek şartmış gibi okunuyor; kaynakta bu, diğer yollardan (Niederlassungserlaubnis vb.) bağımsız bir seçenek. Steps ilk satırı da aynı. Kesinleşmiş mülteci/sığınma hakkı yolu (kaynakta var) kartta yok. Claims 12 ("Eğitim amacıyla ... ödenmez") kaynak metni birebir ama yasa ayrıntısı eksik (yukarıdaki bulgu).
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/kindergeld/familiensituation/koennen-auch-auslaendische-eltern-kindergeld-bekommen--124928 "Sie haben die Staatsangehörigkeit eines der folgenden Staaten und sind sozialversicherungspflichtig beschäftigt oder beziehen Arbeitslosen- beziehungsweise Krankengeld: ... Türkei Oder:"
- Düzeltme: "gerekir" yerine "Türkiye vatandaşı olarak şu yollardan biri yeter: ..." yaz; mülteci yolunu tek cümleyle ekle ya da kapsam dışı bırakıyorsan başlığı "oturum izniyle" diye daralt.

### elterngeld-sure-ve-basvuru: orta
- Bulgu: Yabancı şartı yok. Elterngeld için de yabancıya (AB dışı, özelikle Türk vatandaşı) oturum izni türü şartı var (BEEG §1 Abs. 7: Niederlassungserlaubnis, Daueraufenthalt-EU, Mavi Kart AB, ICT, en az 6 ay çalışma izni veren Aufenthaltserlaubnis; öğrenim/mevsimlik/au-pair gibi izinler dışlanır). Kart "kaç ay, nereye başvurulur" diyor ve hak olup olmadığını hiç sormuyor; Türk okuyucu hak şartını Kindergeld kartından Elterngeld'e geçirmek zorunda kalır. Not: Elterngeld, BEEG §1(8) uyarınca önceki yıl vergilendirilen geliri (tek ebeveyn) 175 000 Euro üzerindeyse de düşer (kartta yok).
- Kanıt: https://www.gesetze-im-internet.de/beeg/__1.html "(7) Ein nicht freizügigkeitsberechtigter Ausländer oder eine nicht freizügigkeitsberechtigte Ausländerin ist nur anspruchsberechtigt, wenn diese Person 1. eine Niederlassungserlaubnis oder eine Erlaubnis zum Daueraufenthalt-EU besitzt,"
- Düzeltme: note'a (kaynağa BEEG §1 eklenerek) şunu yaz: "AB/AEA/İsviçre dışından geliyorsan Elterngeld için oturum izninin Kindergeld'dekine benzer şartları sağlaması gerekir: ..." Kaynak limiti için 228 ya da 229'dan biri çıkarılıp BEEG §1 alınabilir.

### elterngeld-sure-ve-basvuru: orta
- Bulgu: "Çiftler ve ayrı yaşayan ebeveynler 14 yaşam ayı Basiselterngeld'i paylaşır" (subtitle, summary, steps) koşulsuz. Kaynakta 14 ayın ancak şu şartla geçerli olduğu yazıyor: ebeveynlerden en az biri doğumdan sonra 2 yaşam ayında öncekinden az gelir elde etmeli (Partnermonate). Yazar bu şartı claims'e almış (claim 3) ama kart metninde yok. Aksi hâlde 12 ay.
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/elterngeld/faq/wie-lange-kann-ich-elterngeld-bekommen--124728 "Voraussetzung: mindestens einer der Elternteile hat in 2 Lebensmonaten nach der Geburt weniger Einkommen als davor. Diese 2 zusätzlichen Monate nennt man \"Partnermonate\"."
- Düzeltme: summary ve subtitle'da "çiftler 12 ay + (ebeveynlerden biri doğumdan sonra 2 yaşam ayında daha az kazanırsa) 2 Partnermonat = 14 yaşam ayı" biçiminde yaz; tek ebeveynde de aynı şart (kaynak: alleinerziehend de alabilir).

### elterngeld-sure-ve-basvuru: küçük
- Bulgu: (a) Başlık "kaç ay" diye soruyor ama summary'nin ilk cümlesi başvuruyu anlatıyor, ay sayısı üçüncü cümlede. (b) "her ebeveyn en az 2 yaşam ayı için başvurmalıdır" kaynakta "başvurduğunda en az 2 ay" anlamında asgari başvuru süresi; kart zorunluluk gibi yazmış. (c) "Geburten ab 1. April 2024 için" Almanca ifade Türkçe cümleye karışmış; aynı anda alma istisnaları (erken doğum, çoğul doğum, engelli çocuk) yok. (d) "Mutterschutz başlamadan önceki 12 ay": kaynak "Mutterschutz'un başladığı aydan önceki 12 ay".
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/elterngeld/faq/wie-kann-ich-elterngeld-beantragen--124762 "die Lohn- oder Gehaltsabrechnungen der letzten 12 Monate vor dem Monat, in dem Ihr Mutterschutz beginnt,"
- Düzeltme: ilk cümleyi "Çiftler toplam 12+2 yaşam ayı Basiselterngeld alır; başvuru ..." diye değiştir; "1 Nisan 2024 ve sonrasında doğan çocuklar için" yaz; (b)'yi "başvururken en az 2 yaşam ayı istemelisin" yap; (d)'yi kaynak gibi düzelt.
- Not (kart hatası değil, boşluk): Elternzeit (işveren izni, iş güvencesi, süre) kartı yok; anahtar kelimelerde de geçmiyor. İstenirse ayrı kart ve kaynak (familienportal Elternzeit sayfası, BEEG §15) gerekir.

### kita-hakki-1-yasindan-itibaren-ucret-ve-kayit: orta
- Bulgu: note'taki "2026/2027 okul yılında birinci sınıfa başlayan çocuğun ... işgünlerinde günde sekiz saat gündüz bakım hakkı da vardır" aşırı basit. Yasada hak, okul dersleri ve (açık) Ganztag okul programları kapsamında zaten "karşılanmış sayılıyor"; okul tatillerinde de gençlik hizmeti teklifleriyle karşılanmış sayılıyor; eyalet hukuku okul tatillerinde 4 haftaya kadar kapanma koyabilir. Okuyucu "okulun üstüne 8 saat kreş" anlar. Ayrıca "işgünü" yasada "Werktage" (Pazartesi–Cumartesi).
- Kanıt: https://www.gesetze-im-internet.de/sgb_8/__24.html "Der Anspruch des Kindes auf Förderung in Tageseinrichtungen gilt im zeitlichen Umfang des Unterrichts sowie der Angebote der Ganztagsgrundschulen, einschließlich der offenen Ganztagsgrundschulen, als erfüllt."
- Düzeltme: "... günde sekiz saat gündüz bakım hakkı da vardır; ders ve okulun Ganztag programı bu sekiz saatin içine sayılır, tatillerde eyalet hukuku 4 haftaya kadar kapanma koyabilir" yaz. "işgünlerinde" → "hafta içi ve cumartesi (Werktage)" veya yalnız "iş günü" kaldır.

### kita-hakki-1-yasindan-itibaren-ucret-ve-kayit: küçük
- Bulgu: Kesin dil: steps "kabul ve bakım süresine kreş ya da işletici karar verir" (kaynak "in der Regel"); cost "ücretler gelire ... göre kademelendirilir" (kaynak "meist"); cost "Kinderzuschlag, Wohngeld... alanlar veli payı ödemez" ile kart 907'deki "kreş ücretinden muaf tutulabilir" aynı olguyu iki biçimde yazıyor (kaynaklar farklı sözcük kullanıyor: 233 "Sie müssen keine Elternbeiträge bezahlen", 243 "befreien lassen können"). Bir de steps 1'de Jugendamt'ın "kreş listesi ve kayıt koşullarını" vereceği yazıyor; kaynak "Kita-Verzeichnisse oder Anmeldeformalitäten" diyor, ikisi uyumlu. 
- Kanıt: https://www.familienportal.de/familienportal/lebenslagen/ausbildung-beruf/kinderbetreuung/welche-angebote-zu-kinderbetreuung-gibt-es-und-was-kosten-sie--125510 "bestimmt in der Regel der Träger oder die Kita selbst."
- Düzeltme: "genelde kreş ya da işletici karar verir", "çoğunlukla gelire ... göre"; muafiyet cümlesini iki kartta aynı biçime getir (233'e göre "ödemezsin" ya da 243'e göre "başvurarak muaf olabilirsin"). 
- Canlı: SGB VIII §24 metni indirilmiş kopyayla aynı.

### okul-zorunlulugu-ve-okul-sistemi-cercevesi: orta
- Bulgu: steps 2 ve summary "Yeni gelen çocuğunun okula yerleştirilmesi için ilgili okul makamına (Schulbehörde) başvur" — kaynak yalnız kararı kimin verdiğini söylüyor, başvuru usulünü söylemiyor. Okul kaydı eyalette/belediyede farklı kapıdan (okul, Schulamt, kayıt merkezi) yürür; "başvur" kaynaksız usul. "Schulbehörde" adı da eyalete göre değişir.
- Kanıt: https://www.bamf.de/DE/Themen/MigrationAufenthalt/ZuwandererDrittstaaten/Bildung/SchueleraustauschSchulbesuch/schueleraustauschschulbesuch-node.html "Für die Entscheidung hinsichtlich der Einschulung von neuzugewanderten Kindern ist die jeweilige Schulbehörde zuständig."
- Düzeltme: steps 2'yi "Yeni gelen çocuğun hangi okula yerleştirileceğine ilgili okul makamı (Schulbehörde) karar verir; makamın adı ve kayıt yolu eyalete göre değişir" yap; "başvur" fiilini kaldır.

### okul-zorunlulugu-ve-okul-sistemi-cercevesi: küçük
- Bulgu: (a) cost/steps "Devlet okullarının çoğu ücretsizdir"; kaynak: "Okulların çoğunluğu devlet işletmesindedir ve ücretsizdir" (claim 5 doğru yazılmış, kart cümlesi kaymış). (b) steps 4 "Devlet okulunu tercih edebilirsin" kaynakta yok. (c) summary "okul türleri, kayıt ve takvim ... eyaletten eyalete değişir": kaynaklarda okul sistemi ve Schulpflicht ayrıntısı eyalete bağlı deniyor, "kayıt ve takvim" açık yazmıyor (Ferienregelung KMK Ländervereinbarung içinde geçiyor). Eyalet adı/rakamı yok, dil sınıfı genellemesi yok (olumlu).
- Kanıt: https://www.bamf.de/DE/Themen/MigrationAufenthalt/ZuwandererDrittstaaten/Bildung/SchueleraustauschSchulbesuch/schueleraustauschschulbesuch-node.html "Die Mehrheit der Schulen wird vom Staat betrieben und ist kostenlos."
- Düzeltme: "Okulların çoğu devlet okuludur ve ücretsizdir" yaz; steps 4'ü sil; summary'de "okul türleri ve okul düzeni eyaletten eyalete değişir" de.

### yabanci-lise-diplomasi-ile-universiteye-giris: küçük
- Bulgu: Cümleler kaynakla uyumlu (anabin, Zulassungsdatenbank, uni-assist, Studienkolleg, Feststellungsprüfung, 2–3 dönem, B1–B2/B2: hepsi 239/240'ta var; 14 claim quote'u iddiayı kanıtlıyor). Eksik istisnalar: "IB-Diploma ya da yurt dışındaki Alman okulundan Abitur" olanlar Studienkolleg/2–3 dönem şartından muaf; bazı sanat bölümlerinde yalnız yetenek sınavı yetiyor; HZB olmadan hazırlanıp Studienkolleg'siz harici Feststellungsprüfung de mümkün (kontenjan sınırlı). Summary "çoğunlukla" diyerek bunu kapatıyor ama istisna sayılmıyor. "Çoğu devlet Studienkolleg'ine" kaynakta "viele" (çoğu değil, birçok). Türk diploması için özel bir cümle yok; bu bir yanlış değil.
- Kanıt: https://www.daad.de/de/in-deutschland-studieren/voraussetzungen/ueberblick/ "Dies gilt übrigens nicht, wenn Sie ein IB-Diploma oder ein Abitur von einer deutschen Schule im Ausland haben."
- Düzeltme: note'a tek cümle: "IB diploması ya da yurt dışındaki Alman okulundan Abitur'u olanlar bu şartın dışındadır." "çoğu devlet" → "birçok devlet".

### bafog-yabanci-ogrenci-sartlari-ve-ihtiyac-tutari: orta
- Bulgu: Başlık/subtitle/cost "aylık ihtiyaç 475 Euro (+380/+59)" diyor; bu §13 uyarınca ihtiyaç (Bedarf) tutarı, ödenecek BAföG değil. Gerçek ödeme kendi ve ebeveyn gelirine göre azalır (kaynakta yok), sağlık/bakım sigortası eki ayrı. Kart note'u "Bedarf tutarlarıdır" diyor ama okuyucuya "bunu alırım" izlenimi riski kalıyor; "475+380=855" toplamı da yazılmamış. Ayrıca cost'taki "Tutarlar BAföG yasasının yayımlanan güncel metnindendir." iç not tadında; okuyucuya bilgi vermiyor.
- Kanıt: https://www.gesetze-im-internet.de/baf_g/__13.html "(1) Als monatlicher Bedarf gelten für Auszubildende in ... 2. Höheren Fachschulen, Akademien und Hochschulen 475 Euro."
- Düzeltme: summary ve cost'a açık cümle: "Bu tutar yardımın hesabında kullanılan ihtiyaç tutarıdır; ödenecek miktar senin ve ebeveynlerinin gelirine göre azalır." (bunun için BAföG §11 kaynağı eklenmeli, yoksa yalnız "ihtiyaç tutarı, ödenecek miktar değil" de). "Tutarlar ... güncel metnindendir" cümlesini sil.
- Canlı: §13 (442/475/59/380) ve §8 canlı metin, indirilmiş kopyayla birebir aynı.

### bafog-yabanci-ogrenci-sartlari-ve-ihtiyac-tutari: orta
- Bulgu: Oturum izni değerlendirmesi uygulanamaz: steps 2 "iznin yasada sayılan türlerden olup olmadığını karşılaştır" diyor ama §8 Abs. 2 listesi kartta hiç yok; okuyucu karşılaştıramaz. Listede olmayanlar özellikle önemli: çalışma izinleri (§18 vb.), Mavi Kart ve öğrenim izni (§16b) listede geçmiyor; bu izinlerle yalnız Abs. 3 (5 yıl / ebeveyn 3 yıl) yolu kalıyor. Kart bunu söylemiyor. Kayıp kalanlar: tanınmış mülteciler (Abs. 1 Nr. 6), Duldung için 15 ay (Abs. 2a).
- Kanıt: https://www.gesetze-im-internet.de/baf_g/__8.html "eine Aufenthaltserlaubnis nach den §§ 22, 23 Absatz 1, 2 oder 4, den §§ 23a, 25 Absatz 1 oder 2, den §§ 25a, 25b, 28, 37, 38 Absatz 1 Nummer 2, den §§ 104a, 104c"
- Düzeltme: Listedeki izin gruplarını Türkçe kısa ver (insani/siyasi koruma izinleri, Alman/yerleşme izinli yakınına aile birleşimi vb.) ve "Standart çalışma izni, Mavi Kart ve öğrenim izni bu listede yok; bu izinlerle yalnız Abs. 3'teki 5 yıl/ebeveyn şartı kalır" cümlesini ekle; mülteci ve Duldung satırı ekle.

### bafog-yabanci-ogrenci-sartlari-ve-ihtiyac-tutari: orta
- Bulgu: Türk okuyucu notu kesin dille "§ 8'de AB vatandaşları için sayılan gruplar Türk vatandaşı için geçerli değildir" diyor. §8 metni için doğru, ama aynı maddenin Abs. 5'i "başka yabancılara yardım veren hukuk ve idare düzenlemeleri saklıdır" diyor (ör. ortaklık hukuku kaynaklı haklar). Kart bu kapıyı tamamen kapatıyor. Yazar kuralı 8: kaynağın kanıtlamadığı yerde kesin konuşma.
- Kanıt: https://www.gesetze-im-internet.de/baf_g/__8.html "(5) Rechts- und Verwaltungsvorschriften, nach denen anderen Ausländern Ausbildungsförderung zu leisten ist, bleiben unberührt."
- Düzeltme: note'ta "geçerli değildir" yerine "bu gruplar doğrudan sayılmaz" yaz ve Abs. 5'e tek cümle ekle ("başka düzenlemelerden doğan haklar saklıdır; Türk vatandaşı için ek hak olup olmadığı BAföG dairesinde belirlenir" havale olmasın diye şu biçimde: "§ 8 Abs. 5: başka hukuk ve idare düzenlemeleri saklıdır").

### bafog-yabanci-ogrenci-sartlari-ve-ihtiyac-tutari: küçük
- Bulgu: (a) "Meslek yüksekokulu sınıfları (Fachschulklassen), Abendgymnasium ve Kolleg için 442 Euro": Fachschulklassen yalnız "tamamlanmış meslek eğitimi gerektiren" olanlar; "meslek yüksekokulu" çeviri yanlış anlam yaratıyor. 475 grubu "Höhere Fachschulen, Akademien, Hochschulen"; kart "üniversite öğrencisi" diyor. (b) Başlık "verilir mi?" sorusuna summary'nin ilk cümlesi evet/hayır vermiyor. (c) valid_until null; kart tutar içeriyor ve notlarda "BAföG tutarları" tarihe duyarlı sayılıyor; kaynak yıl vermediği için null kabul edilebilir ama kartta "kaynak tarihli" etiketi yok.
- Kanıt: https://www.gesetze-im-internet.de/baf_g/__13.html "Fachschulklassen, deren Besuch eine abgeschlossene Berufsausbildung voraussetzt, Abendgymnasien und Kollegs 442 Euro"
- Düzeltme: "meslek eğitimi tamamlanmış olmayı gerektiren Fachschule sınıfları, akşam lisesi ve Kolleg: 442; yüksekokul/Akademie/Hochschule: 475"; ilk cümleyi "Bazı yabancılara evet: ..." yap.

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag: ciddi
- Bulgu: Summary "Yabancı çocuk Unterhaltsvorschuss alabilir" koşulsuz. Kaynak AB dışı çocuk için şart koyuyor: kendisi ya da ebeveyni Niederlassungserlaubnis / Daueraufenthalt-EU / Mavi Kart AB / ICT / en az 6 ay çalışma izni veren Aufenthaltserlaubnis (ek kısıtlarla) sahibi olmalı; Aufenthaltsgestattung ve Duldung ile (Beschäftigungsduldung hariç) alınamaz. Bu şartlar claims 19-21'de var ama kart metninde yok. Türk okuyucu için yanlış umut ve yanlış işlem.
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/unterhaltsvorschuss "Mit einer Aufenthalts-Gestattung (also während eines Asylverfahrens) können Sie keinen Unterhaltsvorschuss für Ihr Kind bekommen." ve "Andere ausländische Kinder können Unterhaltsvorschuss bekommen, wenn Sie oder Ihr Kind eine Niederlassungs-Erlaubnis haben"
- Düzeltme: Summary'deki "Yabancı çocuk Unterhaltsvorschuss alabilir" cümlesini şu yap: "AB/AEA/İsviçre çocuğu genelde Alman çocukla aynı şartlarda alır; diğer ülkelerin çocuğu için kendisinin ya da ebeveyninin Niederlassungserlaubnis, Daueraufenthalt-EU, Mavi Kart AB/ICT ya da en az 6 ay çalışma izni veren Aufenthaltserlaubnis'i olmalı; Aufenthaltsgestattung ve Duldung (Beschäftigungsduldung hariç) ile alınamaz." Note'a da kısa karşılığını koy.

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag: ciddi
- Bulgu: Summary'nin son cümlesi "Familienkasse'nin Kinderzuschlag sayfasında yabancılar için AB, AEA ve İsviçre vatandaşları ile kesinleşmiş sığınma hakkı sahipleri sayılıyor" Türk okuyucuyu Kinderzuschlag'dan dışlanmış gibi gösteriyor ve Kindergeld kartıyla (901: Niederlassungserlaubnis, çalışma izni vb. ile Kindergeld alınır) çelişiyor. Yasa: Kinderzuschlag, Kindergeld hakkı olan kişiye verilir (BKGG §6a Abs. 1 Nr. 1); AB dışı için Kindergeld hakkı EStG §62 Abs. 2'ye bağlı. Kaynak 243'ün kendi şart listesi de "Kindergeld alıyorsun" diyor (claim 29) ve kart bunu yazmamış. Kinderzuschlag geriye ödenmediği için yanlış okuma doğrudan para kaybıdır.
- Kanıt: https://www.gesetze-im-internet.de/bkgg_1996/__6a.html "sie für diese Kinder nach diesem Gesetz oder nach dem X. Abschnitt des Einkommensteuergesetzes Anspruch auf Kindergeld oder Anspruch auf andere Leistungen im Sinne von § 4 haben," ; kart kaynağı https://www.arbeitsagentur.de/familie-und-kinder/kinderzuschlag-verstehen/kinderzuschlag-anspruch-hoehe-dauer "Sie erhalten Kindergeld (oder eine vergleichbare Leistung) für Ihr Kind."
- Düzeltme: Yabancı cümlesini sil; yerine: "Kinderzuschlag için Kindergeld alıyor olman gerekir; yabancıysan önce Kindergeld kartındaki oturum şartlarını sağlamalısın." (kaynak 243'ün "Kindergeld alıyorsunuz" maddesi). Kaynak sayfanın AB/sığınma listesini kartta hiç aktarma ya da "sayfa yalnız bu iki grubu sayıyor" gibi yarım bilgi bırakma.

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag: orta
- Bulgu: Kinderzuschlag şartları eksik: summary yalnız "geliri yetmeyen" diyor. Kaynakta (claims 28-30 yazılmış, karta girmemiş): çocuk evde yaşamalı, 25 yaşından küçük ve evli olmamalı; Kindergeld alınmalı; ailenin brüt geliri çiftlerde en az 900, tek ebeveynde en az 600 Euro olmalı (altındakiler Kinderzuschlag değil başka yardım yolu). Okuyucu "gelirim çok düşük, alırım" diye başvurabilir.
- Kanıt: https://www.arbeitsagentur.de/familie-und-kinder/kinderzuschlag-verstehen/kinderzuschlag-anspruch-hoehe-dauer "Das Bruttoeinkommen Ihrer Familie beträgt mindestens 900 Euro (Paare) beziehungsweise 600 Euro (Alleinerziehende)."
- Düzeltme: summary'ye üç şartı ekle: Kindergeld alıyor olmak, çocuk 25 yaşından küçük/evli değil/evde, ailenin brüt geliri çiftte en az 900, tek ebeveynde en az 600 Euro.

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag: küçük
- Bulgu: Etiket: cost'taki "Kinderzuschlag: çocuk başına ayda en çok 297 Euro" yıl etiketsiz; claim 24'ün period alanı boş. Kaynak 243 yıl vermiyor; yıl bilgisi 245'te ("Mitteilung vom 05.01.2026", "Bis zu 297 Euro Kinderzuschlag"). Rule 6: kaynakta yıl yoksa "güncel tarife" yaz. Unterhaltsvorschuss etiketi ("1 Ocak 2025'ten itibaren") kaynağa uygun ve doğru; canlı sayfa hâlâ aynı tarihi taşıyor (2026'da değişip değişmediği doğrulanamadı).
- Kanıt: https://www.arbeitsagentur.de/news/kindergeld-steigt-2026 "Der Höchstbetrag beim KiZ beläuft sich auf 297 Euro pro Kind und Monat."
- Düzeltme: cost'a "2026 için (Familienkasse duyurusu 5 Ocak 2026)" ekle (245'i source_ids'e al ya da "güncel tarife" yaz); claim 24 period doldur.

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag: küçük
- Bulgu: (a) "Bürgergeld" adı: aynı kartın kaynağı 243 canlı sayfada "Grundsicherungsgeld" kullanıyor, kaynak 244 "Bürgergeld"; YAZAR_NOTLARI "kaynaktaki adı kullan, tarihini yaz" diyor; kartta ad geçişi belirtilmemiş. (b) UV 12–17 yaş şartı üç alternatif (çocuk SGB II'ye muhtaç değil / UV ile muhtaç olmaz / Bürgergeld alıyorsan 600 Euro) yerine yalnız üçüncüsünü veriyor. (c) "birlikte yaşanan yeni eşe bağlı dışlamalar": kaynakta yeni eşle evli/hayat ortaklığı + birlikte yaşama dışlar; evli olmadan yeni partnerle aynı evde yaşamak dışlamaz; kart cümlesi bunu bulandırıyor.
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/unterhaltsvorschuss "Sie können für Ihr Kind jedoch weiterhin Unterhaltsvorschuss bekommen, wenn Sie mit Ihrer neuen Partnerin oder Ihrem neuen Partner nicht verheiratet oder verpartnert sind, auch wenn Sie in einem Haushalt zusammen leben."
- Düzeltme: (c) "Yeni eşinle evliysen ya da hayat ortaklığın varsa ve birlikte yaşıyorsanız alamazsın; evli olmadan yeni partnerle yaşamak engel değildir (diğer ebeveynle birlikte yaşamak engeldir)"; (b) üç alternatifi yaz; (a) "Bürgergeld (2026'dan itibaren Grundsicherungsgeld adı da kullanılıyor)" kaynak 243'e dayanarak.

### cocugun-saglik-guvencesi-ve-dogum-sonrasi-kayit-sirasi: küçük
- Bulgu: Başlık "sırayla ne yapmalıyım" diyor ama adımlar Standesamt → Krankenkasse'yle sınırlı; Kindergeld başvurusu (kart 901) ve bebeğin oturum izni (resmi/209, §33 AufenthG) yok; Türk okuyucu için ilk haftanın en kritik iki işi eksik. Çapraz kontrol: resmi/209 aynı bilgiyi (Standesamt, 1 hafta) farklı çerçevede veriyor: 209 "velayet sahibi ebeveyn olarak bildirmen gerekir; kurum da yazılı bildirir, senin hakkın etkilenmez" (PStG), 908 steps 1 "bir hafta içinde bildir... hastanede kurum bildirir". Çelişki yok, ama 908 okuyucuya hastane doğumunda kendisinin de bildirmesi gerekip gerekmediğini söylemiyor. Einwohnermeldeamt adı şehre göre değişir notu yok.
- Kanıt: https://www.familienportal.de/familienportal/lebenslagen/schwangerschaft-geburt/anmeldung-standesamt "Nach der Geburt müssen Sie Ihr Kind innerhalb 1 Woche beim Standesamt anmelden, das für den Geburtsort des Kindes zuständig ist."
- Düzeltme: Başlığı "Çocuğum doğunca Standesamt kaydı ve çocuğun sağlık sigortası nasıl yapılır?" diye daralt (ya da 2 kaynak sınırına uygun adım ekle); steps 1'de hastane doğumunda "kurum bildirimi iletir; sen adı kuruma söylersin" netleştir; "Einwohnermeldeamt (adı şehre göre değişir)" yaz.

### cocugun-saglik-guvencesi-ve-dogum-sonrasi-kayit-sirasi: küçük
- Bulgu: saglik/602 ile tekrar: aynı kaynak (141, SGB V §10) ve aynı içerik iki kartta: çocuk yaş sınırları (18/23/25) ve §10(3) "diğer ebeveyn üye değil + Jahresarbeitsentgeltgrenze" notu. İçerik çelişmiyor, ama 908 Almanca terimleri Türkçe karşılıksız bırakıyor (Jahresarbeitsentgeltgrenze, Bezugsgröße), 602 ise "yıllık sigorta zorunluluğu gelir sınırı" ve "aylık referans değer" diye açıklıyor. 602'de "bu iki koşul eş için aranır" ifadesi var; 908 aynı yedide bir koşulu çocuğa uyguluyor (yasaya göre doğru: aile üyesinin kendi geliri). Tutarsızlık yok.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "kein Gesamteinkommen haben, das regelmäßig im Monat ein Siebtel der monatlichen Bezugsgröße nach § 18 des Vierten Buches überschreitet."
- Düzeltme: 908 note'unda 602'deki Türkçe karşılıkları kullan; yaş sınırlarını 908'de tutup 602'de kalsın ya da biri diğerinden sadeleşsin (tekrarı azalt); "Aile sigortası kamu sigortası içindir" cümlesi summary'de zaten var, özel sigortalı ebeveynin çocuğu için bilgi eksik ama kaynağı yok (not).

---

## Çapraz kontrol özeti
- resmi/209 (order 209) ↔ aile/908: Standesamt 1 hafta bildirimi ortak; kaynaklar farklı (089/090 PStG, 234 Familienportal); çelişki yok; 908'de hastane doğumunda kimin bildirdiği belirsiz (yukarıda).
- saglik/602 ↔ aile/908: aynı SGB V §10; içerik tekrarı, çelişki yok; terimlerde tutarsız açıklama (yukarıda).
- aile içi: 903 (Kinderzuschlag alan veli payı ödemez) ↔ 907 (muaf tutulabilir) ifade farkı; 901 (Türk Kindergeld alabilir) ↔ 907 (KiZ yabancı listesi) tutarsız izlenim (ciddi bulgu).

## Güncellik sonucu
- Kindergeld 259 Euro (EStG §66) canlı doğrulandı. Kinderzuschlag 297 Euro (arbeitsagentur canlı) doğru, yıl etiketi eksik. Unterhaltsvorschuss 227/299/394 canlı Familienportal'da "ab 1. Januar 2025". BAföG 442/475/380/59 canlı yasada aynı. Elterngeld süre kuralları canlı sayfada aynı. Yeni yürürlük tarihi ya da değişmiş kural bulunmadı.
