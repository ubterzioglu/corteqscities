# Almanya ulusal paketi, konu "oturum": bağımsız denetim (G0)

Denetim tarihi: 25.10.2026. Denetçi kartları yazmadı; yazarın gaps.md dosyasını okumadı. Kart dosyalarına dokunulmadı.

## Özet
- Kart sayısı: 15. claims: 179 (hepsinin `quote` alıntısı kaynak metinde birebir geçiyor; anlam kontrolü örneklemle değil, 179 satırın tamamında yapıldı).
- Bulgu sayısı: ciddi 1, orta 20, küçük 14 (toplam 35; 2 küçük çapraz bulgu dahil).
- Genel sonuç: Kartlardaki sayılar (75 / 25 / 100 / 96 / 93 / 98 / 67 Euro, %50 / %45,3, 5 yıl / 60 ay / 36 ay / 27 / 21 ay, 140 iş günü, 6 / 12 ay) kaynak metinle ve CANLI sayfalarla uyuşuyor. Sorun sayılarda değil kapsamda: bazı kurallar herkese genelleniyor, bazı önemli şartlar ve istisnalar eksik, iki yerde çeviri/terim hatası var.
- Yöntem: 23 kaynağın `text_file` kopyası kartlarla cümle cümle karşılaştırıldı; sonra 23 kaynağın tamamı Python urllib ile canlı indirilip kopyayla satır satır karşılaştırıldı. Fark yok (HTML'den metne çıkarmadan doğan satır bölünmeleri dışında; ilgili anahtar cümleler canlı sayfada ayrıca tek tek arandı ve bulundu).
- Güncellik sonucu: AufenthG tam metni canlıda "zuletzt geändert durch Art. 13 G v. 22.7.2026 I Nr. 222" sürümünde. §4, §4a, §8, §9, §16b, §18c, §18g, §20a, §21, §30, §51, §81, AufenthV §45/§45c/§46/§52a, StAG §10, FreizügG/EU §1 ve §5 canlı ile kopya aynı. Yani 2024 Fachkräfte reformu (Chancenkarte, Mavi Kart %50 / %45,3, 27 / 21 ay) ve 2024 StAG reformu (5 yıl, B1, Mehrstaatigkeit) kartlarda doğru yansımış. StAG §10 Abs. 3 ("3 yıl hızlı yol") canlıda "(weggefallen)"; kart 3 yıl yazmıyor, doğru. Vize ve eAT ücretleri canlıda güncel.
- Canlı açılan sayfalar: gesetze-im-internet.de/aufenthg_2004/{__4,__4a,__8,__9,__16b,__18c,__18g,__20a,__21,__30,__51,__81,BJNR195010004}.html; aufenthv/{__45,__45c,__46,__52a}.html; stag/__10.html; freiz_gg_eu_2004/{__1,__5}.html; tuerkei.diplo.de (Merkblatt 01F Ehegattennachzug ve "Aktuelle Hinweise und Antragstellung"); bva.bund.de Beibehaltung sayfası; ek olarak gesetze-im-internet.de/svbezgrv_2026/__4.html (Beitragsbemessungsgrenze 2026) ve pauswgebv/__1.html (kimlik kartı ücreti).
- Bakılmayanlar: bmi.bund.de (kapalı) olduğu için 2026 Mavi Kart euro asgari maaşları (Bundesanzeiger ilanı) doğrulanamadı; make-it-in-germany.com ve auswaertiges-amt.de denenmedi. Türk vatandaşlığından çıkma / Türk hukukunda çifte vatandaşlık için açık bir resmî Alman kaynak bulunamadı (BVA ve BAMF sayfalarında aranan ifade yok). AB Adalet Divanı Dogan kararı (Türk işçilerin eşleri için A1 Almanca şartı) kartlarda yok ve denetlenen kaynaklarda da yok; editör açık bir resmî kaynakta var mı diye bakabilir, kaynak çıkmazsa karta yazılmaz.

## Çapraz bulgular (tüm kartlar)
- Türk okuyucu: Ortaklık Hukuku kartı kaynağı aşmıyor; "Assoziationsberechtigte" kim olduğunu tanımlamıyor ve kaynakta olmayan hiçbir hak iddia etmiyor. Bu kısım temiz.
- AB vatandaşı kartı Türk okuyucuyu uyarıyor ("Türk vatandaşı AB vatandaşı sayılmadığı için bu rejimden kendi başına yararlanmaz"), ama uyarı fazla kesin (aşağıda ab-vatandasi kartında).
- Eyalet farkı: eyalet rakamı, eyalet adı ya da şehir adı yok; §18c Abs. 3 "Landesregierung" ayrıntısı karta girmemiş. Temiz.
- Havale cümlesi: "resmî sayfada yazar" türü açık havale yok; yalnız mavi-kart kartındaki "Euro tutarlarını ... Bundesanzeiger'de ilan eder" cümlesi fiilen havale işlevi görüyor (aşağıda).
- ### capraz-ausländerbehörde: küçük
  - Bulgu: "Ausländerbehörde" kartlarda (mavi-kart, is-degistirince, ab-vatandasi, yurt-disi, uzatma, serbest vb.) kurum adı sanki ulusal tek addır; DE_YAZAR_NOTLARI "adı şehre göre değişir" denmesini ister. Hiçbir kartta bu cümle yok.
  - Kanıt: DE_YAZAR_NOTLARI.md "Kurum adı eyalete/şehre göre değişiyorsa (Bürgeramt, ...; Ausländerbehörde, Landesamt für Einwanderung) genel adı yaz ve "adı şehre göre değişir" de."
  - Düzeltme: Her kartta ilk geçtiği yerde "Ausländerbehörde (yabancılar dairesi; adı şehre ve eyalete göre değişir)" yaz.
- ### capraz-link-etiketi: küçük
  - Bulgu: Bağlantılar dosyasında 25 bağlantının hepsinin etiketi "Bilgi al". Mavi-kart ve serbest-calisan kartlarında tek bağlantı var. Bağlantılar yasa metnine gidiyor; kullanıcı için işlem sayfası değil (vize kartında iDATA/Auslandsportal bağlantısı yok, çünkü kaynak listesinde yok).
  - Kanıt: Bağlantılar.oturum.jsonl, tüm satırlar `"label": "Bilgi al"`.
  - Düzeltme: Etiketi içeriğe göre yaz ("Yasa metni: § 18g", "Vize bekleme süreleri ve randevu"). Zorunlu değil.

## Kart kart

### oturum-belgesi-turleri: orta
- Bulgu: Özet "AB hukuku, bir yönetmelik ya da AB–Türkiye Ortaklık Anlaşması'ndan doğan oturum hakkı varsa bu değişir" diyor (claim 2 daha da açık: "belge zorunluluğu uygulanmaz"). Aynı yasa maddesinin 2. fıkrası Ortaklık hakkı olan kişiye Aufenthaltserlaubnis ile belgeleme yükümlülüğü getiriyor; kartın kendi 2. adımı da bunu söylüyor. Özet ile adım birbirini yalanlıyor ve Türk okuyucu "benim belge almama gerek yok" sonucuna varabilir. Adımda da istisna (Niederlassungserlaubnis / Daueraufenthalt-EU sahibi) yok.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__4.html "Ein Ausländer, dem nach dem Assoziationsabkommen EWG/Türkei ein Aufenthaltsrecht zusteht, ist verpflichtet, das Bestehen des Aufenthaltsrechts durch den Besitz einer Aufenthaltserlaubnis nachzuweisen, sofern er weder eine Niederlassungserlaubnis noch eine Erlaubnis zum Daueraufenthalt – EU besitzt."
- Düzeltme: Özetteki cümleyi "AB hukuku ya da bir yönetmelik başka türlü belirlemişse belge gerekmez; AB–Türkiye Ortaklık Anlaşması'ndan doğan oturum hakkı varsa bu hakkı Aufenthaltserlaubnis ile belgelemek gerekir (Niederlassungserlaubnis ya da AB uzun süreli oturum izni olanlar hariç)" yap. 2. adıma aynı istisnayı ekle. Claim 2'yi bu kapsamla yeniden yaz.

### oturum-belgesi-turleri: küçük
- Bulgu: Başlıktaki soru ("hangi türler var") ilk cümlede cevaplanmıyor; ilk cümle "belge gerekir" diyor, liste ikinci cümlede. 1. adım "yukarıdaki listeden" diyor ama metinde madde işaretli liste yok, tek cümlelik sayım var.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__4.html "Die Aufenthaltstitel werden erteilt als"
- Düzeltme: Özeti "Yedi belge türü var: vize, Aufenthaltserlaubnis, ..." diye aç; "yukarıdaki listeden" yerine "yukarıdaki türlerden" yaz.

### turk-vatandasi-ulusal-vize-basvurusu: orta
- Bulgu: "Uyum önlemi" Anpassungsmaßnahme için yanlış/yanıltıcı karşılık. Almanca'daki terim, yabancı meslek yeterliliğinin tanınması için yapılan tamamlama/uyum eğitimi (§ 16d) demek. Türkçede "uyum" entegrasyon/uyum kursu çağrıştırır; okuyucu yanlış kategoride kayıt yaparsa kaynağa göre başvuru reddediliyor. Kartın 1. adımı kategori seçtiriyor, bu yüzden hata sonuç doğurur.
- Kanıt: https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2729790-2729790 "Es wird darauf hingewiesen, dass Visumanträge, die in einer unkorrekten Kategorie vorgenommen wurden, bei Antragstellung zurückgewiesen werden." ve https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html (§ 16d) "Einem Ausländer soll zum Zweck der Anerkennung seiner im Ausland erworbenen Berufsqualifikation eine Aufenthaltserlaubnis für die Durchführung einer Qualifizierungsmaßnahme einschließlich sich daran anschließender Prüfungen erteilt werden"
- Düzeltme: "uyum önlemi" yerine "meslek yeterliliğinin tanınması için tamamlama/uyum eğitimi (Anpassungsmaßnahme)" yaz; adım, zamanlama ve claim 18'de aynı düzeltme. (Not: § 16d metni kartın kaynaklarında yok; terimi açıklamak için üçüncü kaynak gerekirse tam yasa sayfası 035 zaten kaynak dizininde var. Kart başına en çok 2 kaynak kuralı için Almanca terimi parantezde bırakıp "tanınma" kelimesiyle yetinmek de yeterli.)

### turk-vatandasi-ulusal-vize-basvurusu: küçük
- Bulgu: Rule 6: ücret (75 Euro, 25 Euro, 39,92 EUR) ve bekleme süreleri tarihe duyarlı, ama kartta "güncel tarife / 25.10.2026 itibarıyla" ibaresi yok; valid_until null. Not cümlesi yalnız bekleme süreleri için uyarıyor. Ayrıca aynı 75 Euro ücreti taşıyan es-icin-aile-birlesimi-vizesi kartı valid_until.json'da hiç yok.
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__46.html "für die Erteilung eines nationalen Visums (Kategorie „D“), auch für mehrmalige Einreisen 75 Euro" (maddede yıl/tarih yok); https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2729790-2729790 "Diese ungefähren Wartezeiten können sich kurzfristig ändern"
- Düzeltme: Maliyet alanına "güncel tarife" ekle; es-icin-aile-birlesimi-vizesi için valid_until.json'a `null` satırı ekle.

### mavi-kart-ab-sartlari: orta
- Bulgu: Başlık "maaş eşiği neler?" diye soruyor; ilk cümle ("Mavi Kart akademik eğitimli uzmana verilir") eşiği söylemiyor, yüzde üçüncü cümlede. Okuyucuya euro tutarı verilmiyor; yerine "Euro tutarlarını İçişleri Bakanlığı ... ilan eder" deniyor, bu fiilen havale. Kart takvim yılına bağlı bir eşik veriyor ama yıl yazmıyor. Eşiğin hesabına temel olan 2026 prim tavanı açık resmî kaynakta var, ama kartta yok.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__18g.html "Das Bundesministerium des Innern und für Heimat gibt die Mindestgehälter nach den Absätzen 1 und 2 für jedes Kalenderjahr jeweils bis zum 31. Dezember des Vorjahres im Bundesanzeiger bekannt." ve https://www.gesetze-im-internet.de/svbezgrv_2026/__4.html "Die Beitragsbemessungsgrenze nach § 159 des Sechsten Buches Sozialgesetzbuch wird für das Jahr 2026 wie folgt festgesetzt" (devamı: "in der allgemeinen Rentenversicherung auf 101 400 Euro jährlich")
- Düzeltme: İlk cümle: "Genel maaş eşiği yıllık prim tavanının %50'sidir; belirli meslek gruplarında ve diplomadan en çok üç yıl sonra %45,3." Havale cümlesini sil. 2026 için "yıllık prim tavanı 101.400 Euro" bilgisini SVBezGrV 2026 § 4'ten claim'li olarak ekle (kaynak sayısı 2'yi geçmez: 033 + svbezgrv_2026/__4). Euro karşılıklarını (hesap) yazma; BMI ilanı kapalı olduğundan kaynak çıkmazsa yalnız yüzde + prim tavanı yeter.

### mavi-kart-ab-sartlari: küçük
- Bulgu: Eşik her takvim yılı yeniden ilan ediliyor ama valid_until.json null; DE_YAZAR_NOTLARI "Blaue Karte eşikleri"ni tarihe duyarlı sayıyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__18g.html "für jedes Kalenderjahr jeweils bis zum 31. Dezember des Vorjahres im Bundesanzeiger bekannt"
- Düzeltme: valid_until = 2026-12-31 (karta 2026 prim tavanı eklenirse).

### nitelikli-is-gucu-oturumu-ve-firsat-karti: orta
- Bulgu: 3. ve 4. adımlar ("yabancı yeterliliğini uzman bir kuruma onaylat", "basit Almanca ya da en az B2 İngilizce kanıtla") sıralama olarak herkese uygulanıyormuş gibi duruyor. Yasaya göre bu iki şart yalnız PUANLA verilen Chancenkarte için (§ 20a Abs. 3 Nr. 2 → Abs. 4 Satz 3). Uzman (Fachkraft) olarak başvuran için dil/B2 şartı yok. Dar kural genelleniyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__20a.html "Die Chancenkarte nach Absatz 3 Nummer 2 kann nur erteilt werden, wenn er" ... "mindestens einfache deutsche Sprachkenntnisse nachweist oder"
- Düzeltme: 3. ve 4. adımın başına "Puanla başvuruyorsan:" ekle; uzman olarak başvuranlar için bu iki adımı uygulama. Claim 41 ve 43-44'e aynı kapsamı yaz.

### nitelikli-is-gucu-oturumu-ve-firsat-karti: orta
- Bulgu: § 18a / § 18b anlatımı eksik. Kart "nitelikli bir iş bul" diyor; kaynak metindeki (035, kartın kendi kaynağı) § 18 şartları yok: somut iş teklifi, gerekli meslek icra izni, denklik/tanınmış diploma ve 45 yaş üstünde ilk verilişte yüksek maaş eşiği (ya da yaşlılık güvencesi). "Uzman" (Fachkraft) da tanımlanmamış; Chancenkarte "uzman olana" verilir deniyor ama uzmanın ne olduğu yok. 45 yaş kuralı Türk okuyucu için sık karşılaşılan bir engel.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html "ein konkretes Arbeitsplatzangebot vorliegt" ; "in den Fällen der erstmaligen Erteilung eines Aufenthaltstitels nach § 18a oder § 18b nach Vollendung des 45. Lebensjahres des Ausländers die Höhe des Gehalts mindestens 55 Prozent der jährlichen Beitragsbemessungsgrenze in der allgemeinen Rentenversicherung entspricht, es sei denn, der Ausländer kann den Nachweis über eine angemessene Altersversorgung erbringen" ; "Fachkraft im Sinne dieses Gesetzes ist ein Ausländer, der"
- Düzeltme: Özet ve adımlara şu üç cümleyi ekle: somut iş teklifi; yeterliliğin denkliğinin ya da diplomanın tanınmasının gerekmesi (§ 18 Abs. 2 Nr. 4) ve gerekiyorsa meslek icra izni; 45 yaşından sonra ilk verilişte maaş eşiği (prim tavanının %55'i) ya da yaşlılık güvencesi. "Uzman" için § 18 Abs. 3 tanımı (meslek eğitimi ya da üniversite diploması, yurt içi ya da denk/tanınmış) bir cümleyle.

### nitelikli-is-gucu-oturumu-ve-firsat-karti: küçük
- Bulgu: Çeviri: "Abschnitt 3 oder Abschnitt 4" kartta "3. veya 4. bölüm" (notta ve claim 52'de). Almanca hiyerarşide Kapitel = bölüm, Abschnitt = kısım. Ayrıca "iki yıla kadar uzatılabilir" ifadesi toplam süre gibi okunabilir; yasa "um bis zu zwei Jahre ... verlängert" diyor ve haftalık 20 saat sınırı uzatma (Folge-Chancenkarte) için uygulanmıyor, kart bunu belirtmiyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__20a.html "Absatz 2 findet auf die Folge-Chancenkarte keine Anwendung."
- Düzeltme: "3. veya 4. kısım (Abschnitt)" yaz; zamanlama satırında "uzatma en çok iki yıl daha" de.

### ogrenci-oturumu-ve-calisma-hakki: orta
- Bulgu: Başlık "nasıl alınır" diyor; kart yalnız "kabul + Aufenthaltserlaubnis" gibi anlatıyor. Kaynak (035, aynı yasa) genel şartları da koyuyor: kural olarak geçim güvencesi, doğru vizeyle giriş. Kartta hiçbir geçim/finansman şartı yok; okuyucu yalnız kabul mektubuyla yetinebileceğini düşünebilir.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html "Die Erteilung eines Aufenthaltstitels setzt in der Regel voraus, dass 1. der Lebensunterhalt gesichert ist"
- Düzeltme: Özete ve adımlara "Kural olarak geçimin güvencede olması da aranır (§ 5)" ekle ve claim yaz. Kaynak sayısı 2'yi aşmasın diye 035 tam yasa sayfasını 037'nin yanına koy.

### ogrenci-oturumu-ve-calisma-hakki: küçük
- Bulgu: "Öğrenci yardımcı işleri (studentische Nebentätigkeiten)" Türkçesi belirsiz; "yardımcı iş" her tür ek işi çağrıştırır, oysa kaynak terimi tanımlamıyor. Okuyucu "öğrenci olarak yaptığım her ek iş sayılmaz" diye yanlış okuyabilir. Ayrıca ilk cümle yalnız "nasıl alınır" kısmını cevaplıyor, "ne kadar çalışabilirsin" son cümlede.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__16b.html "Studentische Nebentätigkeiten werden nicht angerechnet."
- Düzeltme: Terimi yalnız Almanca bırak ("studentische Nebentätigkeiten; kaynak terimi açıklamıyor" yazma, havale olur) ya da cümleyi sil. Özetin başına "Yılda en çok 140 iş günü çalışabilirsin" cevabını da ekle.

### es-icin-aile-birlesimi-vizesi: orta
- Bulgu: Başlık ve özet "§ 30 eş birleşimi" diyor ama § 30 yalnız yabancı uyruklu eşin (Almanya'da yaşayan Ausländer) yanına gelen eş içindir. Belge listesi (Alman eşin pasaport/kimlik kopyası, Mavi Kart) Alman eşi de kapsıyor; Alman eş için kural § 28'dir (A1 şartı § 28 Abs. 1 Satz 5 ile § 30'a yollanır). Kapsam karışık: Alman bir kişiyle evli Türk okuyucu da başlığı kendisi sanır, ama özet yalnız § 30 istisnalarını (Mavi Kart sahibi eş vb.) sayar.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__30.html "Dem Ehegatten eines Ausländers ist eine Aufenthaltserlaubnis zu erteilen, wenn" ; https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html (§ 28) "Die Aufenthaltserlaubnis ist dem ausländischen 1. Ehegatten eines Deutschen" ve "§ 30 Abs. 1 Satz 1 Nr. 1 und 2, Satz 3 und Abs. 2 Satz 1 ist in den Fällen des Satzes 1 Nr. 1 entsprechend anzuwenden."
- Düzeltme: Başlık/özet kapsamını "yabancı uyruklu eş (§ 30)" yap ve Alman eş için "§ 28 aynı dil şartına yollar" cümlesi ekle (kaynak olarak 035 tam yasa sayfası). Kart başına 2 kaynak sınırı için 039 + 038 yerine 039 + 035 de olur.

### es-icin-aile-birlesimi-vizesi: orta
- Bulgu: Belge listesi kaynağa göre eksik ve bir yerde fazla genelleniyor. (a) "Pasaport, form, fotoğraf ve diğer belgeleri orijinal ve iki kopya götür": kaynakta "orijinal ve iki kopya" yalnız pasaport/form/foto sonrası sayılan "folgenden Unterlagen" için; foto 1 adet. (b) Almanya'daki eş Türk uyruklu ise onun da nüfus kayıt örneği (Tam Tekmil Vukuatlı) isteniyor; kartta yok. (c) "Falls zutreffend" belgeler yok: önceki evliliklerin boşanma kararları (kesinleşme şerhi, apostil, Almanca çeviri), ölüm belgesi (Formül C). (d) Barkodlu nüfus kayıt örneğinde orijinal gerekmez, kartta yok.
- Kanıt: https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2728584-2728584 "wenn Ihr in Deutschland lebender Ehepartner die türkische Staatsangehörigkeit besitzt:" ; "Bitte bringen Sie zusätzlich die folgenden Unterlagen im Original und in zweifacher Kopie mit." ; "Falls zutreffend: Vollständige Scheidungsurteile der letzten Ehen beider Ehegatten mit Rechtskraftvermerk, Apostille und mit deutscher Übersetzung"
- Düzeltme: Belgeler alanına bu üç maddeyi (Türk eşin nüfus kaydı, "varsa" boşanma/ölüm belgeleri, barkod notu) ekle ve "orijinal ve iki kopya" kapsamını "aşağıdaki belgeler" diye daralt; claim 75'i bu kapsamla düzelt. Not: Merkblatt "Formül B" için apostil gerekmez diyor; kart doğru aktarmış.

### yerlesme-izni-sartlari: küçük
- Bulgu: Başlık "süre, prim, dil ve geçim şartları neler" diye soruyor; özetin ilk cümlesi ("Yerleşme izni süresiz bir oturum belgesidir") soruyu cevaplamıyor, şartlar ikinci cümlede.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__9.html "Die Niederlassungserlaubnis ist ein unbefristeter Aufenthaltstitel."
- Düzeltme: İlk cümle: "Genel kuralda 5 yıl Aufenthaltserlaubnis, 60 ay emeklilik primi, yeterli Almanca, geçim ve konut aranır; uzmanlarda süre 3 yıl / 36 ay, Mavi Kart'ta 27 ay."

### yerlesme-izni-sartlari: küçük
- Bulgu: 5. adım "Evliysen prim, çalışma izni ve gerekli diğer izinler şartlarını eşlerden birinin karşılaması yeter": kaynakta bu kolaylık yalnız evlilik birliği içinde yaşayan eşler için ve yalnız prim, "Beschäftigung erlaubt" ve "sonstige Erlaubnisse" kalemleri için; geçim ve dil için değil. Kart "evlilik birliği içinde" koşulunu yazmıyor, "gerekli diğer izinler" ifadesi de belirsiz.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__9.html "Bei Ehegatten, die in ehelicher Lebensgemeinschaft leben, genügt es, wenn die Voraussetzungen nach Absatz 2 Satz 1 Nr. 3, 5 und 6 durch einen Ehegatten erfüllt werden."
- Düzeltme: "Evlilik birliği içinde yaşıyorsanız, emeklilik primi, çalışma izni ve işe özel gerekli izinler şartlarını eşlerden birinin karşılaması yeter; geçim, dil ve konut için bu kolaylık yok" yaz.

### alman-vatandasligi-sartlari: orta
- Bulgu: Önemli istisnalar ve şartlar eksik. (a) Geçim şartı sosyal yardımsız sağlanmalı diye yazılmış, ama kaynakta üç istisna var: 1974 öncesi işçi alım anlaşmasıyla gelenler ve eşleri, son 24 ayın en az 20 ayında tam zamanlı çalışanlar, bu çalışanın eşi/çocuklu ailesi. Claim 113 bu istisnayı içeriyor ama kart metninde yok. (b) Yine 1974 öncesi gelenler için dil şartı yalnız günlük sözlü anlaşma düzeyine iner (Abs. 4 Satz 3); kartta yok. (c) Sabıka şartı (hüküm giymemiş olma) hiçbir yerde sayılmıyor. Not: Türkiye'nin bu anlaşmaya taraf olduğu kaynakta yazmaz; "Türkiye" kelimesi yazılmamalı.
- Kanıt: https://www.gesetze-im-internet.de/stag/__10.html "in Vollzeit erwerbstätig ist und dies innerhalb der letzten 24 Monate mindestens 20 Monate war" ; "auf Grund eines Abkommens zur Anwerbung und Vermittlung von Arbeitskräften bis zum 30. Juni 1974 in das Gebiet der Bundesrepublik Deutschland nach dem Stand vom 2. Oktober 1990" ; "weder wegen einer rechtswidrigen Tat zu einer Strafe verurteilt noch gegen ihn auf Grund seiner Schuldunfähigkeit eine Maßregel der Besserung und Sicherung angeordnet worden ist,"
- Düzeltme: Özet ve adımlara "Sosyal yardım almama şartından muaf: son 24 ayın en az 20 ayında tam zamanlı çalışanlar ve 1974 öncesi işçi anlaşmasıyla gelenler (eşleri dahil)", "1974 öncesi gelenlerde dil şartı günlük sözlü anlaşmayla karşılanır" ve "ceza mahkûmiyeti olmamalı" ekle.

### alman-vatandasligi-sartlari: orta
- Bulgu: Türk okuyucunun asıl sorusu (Türk vatandaşlığından çıkmak gerekir mi, çifte vatandaşlık olur mu) cevaplanmıyor. Notta yalnız BVA'nın Almanların başka vatandaşlık edinmesine ilişkin cümlesi var; yani yön ters (Alman olup yabancı vatandaşlık alan), Almanya'ya naturalize olan yabancı için değil. Cümlenin kendisi bunu itiraf ediyor ("bu açıklama ... başka bir vatandaşlık edinmesini anlatan sayfada yer alıyor"), bu hem iç denetim notu hem kanıtın yetersiz olduğunun işareti. StAG § 10 metninde eski "Nr. 4 (weggefallen)" var ama ne olduğunu söylemiyor.
- Kanıt: https://www.bva.bund.de/DE/Services/Buerger/Ausweis-Dokumente-Recht/Staatsangehoerigkeit/Beibehaltung/Beibehaltung_node.html "Mehrstaatigkeit wird in Deutschland ab sofort generell hingenommen. Ein Verlust der deutschen Staatsangehörigkeit durch Annahme einer anderen nicht-deutschen Staatsangehörigkeit tritt nicht mehr ein."
- Düzeltme: Notu sil. Eğer Einbürgerung için çifte vatandaşlığı açıkça anlatan açık bir resmî sayfa bulunursa (BAMF/BVA/Bundesregierung; bu denetimde bulunamadı) oradan claim'li bir cümle yaz; bulunamazsa karta çifte vatandaşlık hakkında hiçbir şey yazma, gaps'e not düş.

### alman-vatandasligi-sartlari: orta
- Bulgu: 1. adım belirsiz ve yanlış okunabilir: "Mavi Kart ya da § 16b ve § 20a dahil yasada sayılan amaçlar dışında verilmiş bir oturum belgesi gerekir". "§ 16b ve § 20a dahil" ifadesi bu belgelerin kabul edildiğini düşündürür; oysa kaynakta tam tersi, § 16b (öğrenim) ve § 20a (Chancenkarte) ile verilmiş belgeler SAYILMAZ. Öğrenci oturumuyla kalan biri yanlış umutlanır.
- Kanıt: https://www.gesetze-im-internet.de/stag/__10.html "einen Aufenthaltstitel für andere als die in den §§ 16a, 16b, 16d, 16e, 16f, 17, 18f, 19, 19b, 19e, 20, 20a, 22, 23a, 24, 25 Absatz 3 bis 5 und § 104c des Aufenthaltsgesetzes aufgeführten Aufenthaltszwecke besitzt"
- Düzeltme: "Öğrenim (§ 16b), Chancenkarte (§ 20a) ve yasada sayılan diğer amaçlarla (ör. §§ 16a, 16d, 17, 19, 24) verilmiş belgeler sayılmaz; süresiz oturum hakkı, Mavi Kart ya da bunlar dışındaki bir amaçla verilmiş belge gerekir" yaz.

### alman-vatandasligi-sartlari: küçük
- Bulgu: Not cümlesi iç denetim/kaynak açıklaması içeriyor ("bu açıklama, Almanların başka bir vatandaşlık edinmesini anlatan sayfada yer alıyor"); kullanıcıya yönelik içerik değil.
- Kanıt: kart notu (yukarıdaki bulguyla aynı yer).
- Düzeltme: Sil.

### oturum-izni-uzatma-ve-gecici-belge: orta
- Bulgu: "Fiktionsbescheinigung'a gelecekteki belgenin izin verdiği çalışma hakkı yazılır" (özet, 2. adım) genel yazılmış. Kaynak yalnız Kapitel 2 Abschnitt 3 ve 4 belgeleri için (öğrenim/eğitim ve çalışma amaçlı belgeler) bu hükmü koyuyor; aile birleşimi vb. belgeler dışarıda. Dar kural herkese genelleniyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__81.html "gilt die in dem künftigen Aufenthaltstitel für einen Aufenthalt nach Kapitel 2 Abschnitt 3 und 4 beschriebene Erwerbstätigkeit ab Veranlassung der Ausstellung bis zur Ausgabe des Dokuments nach § 78 Absatz 1 Satz 1 als erlaubt"
- Düzeltme: "Öğrenim ve çalışma amaçlı belgelerde (yasanın 2. bölüm 3. ve 4. kısmı) Fiktionsbescheinigung'a gelecekteki belgede yazan çalışma izni de yazılır" de; 2. adımdaki "çalışma hakkın bu belgeye yazılır"ı aynı kapsamla daralt; claim 123-124'ü aynı kapsamla düzelt.

### oturum-izni-uzatma-ve-gecici-belge: küçük
- Bulgu: Not cümlesi kaynaktan dar: "yerine getirmeyen yabancının uzatması ... en çok bir yıl" diyor; kaynak "war oder ist verpflichtet ... solange er den Integrationskurs noch nicht erfolgreich abgeschlossen" diyor, yani kursa katılma yükümlüsü olup henüz bitirmemiş herkes (yükümlülüğü ihlal etmeyen de) için; kuralı "soll" (kural olarak). § 25 Abs. 1, 2, 3 ile verilmiş belgelerde bu madde uygulanmaz, kartta yok.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__8.html "War oder ist ein Ausländer zur Teilnahme an einem Integrationskurs nach § 44a Absatz 1 Satz 1 verpflichtet, soll die Verlängerung der Aufenthaltserlaubnis jeweils auf höchstens ein Jahr befristet werden"
- Düzeltme: "Entegrasyon kursuna katılma yükümlüsü olup kursu henüz bitirmediysen uzatma kural olarak en çok bir yıl süreyle yapılır" yaz.

### ortaklik-hukuku-oturum-belgesi: orta
- Bulgu: Başlık "ücret ne olur?" diyor, kart tutar vermiyor, yalnız "Alman kimlik kartı ücreti kadar" diyor. Okuyucu için işe yaramaz. Ayrıca kural kapsamı dar: § 52a Abs. 2 yalnız §§ 44-45, § 45c Abs. 1 ve § 48 Abs. 1 Satz 1 Nr. 15 için geçerli; kart "oturum belgesi ücreti" diyerek genel yazıyor (kaynak "Visum" ücretini kapsamıyor). Kartın Türk okuyucu dilinde kaynağı aşmama konusu temiz; sorun kapsam ve tutarsızlık.
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__52a.html "Für Assoziationsberechtigte sind die §§ 44 bis 50 mit der Maßgabe anzuwenden, dass für Aufenthaltstitel nach den §§ 44 bis 45, 45c Absatz 1 und § 48 Absatz 1 Satz 1 Nummer 15 jeweils eine Gebühr in Höhe der für die Ausstellung von Personalausweisen an Deutsche erhobenen Gebühr zu erheben ist." ; https://www.gesetze-im-internet.de/pauswgebv/__1.html (canlı, 25.10.2026) "46 Euro in allen anderen Fällen." (24 yaş altı için aynı paragrafta ayrı tutar var)
- Düzeltme: Tutarı ekle: kimlik kartı ücreti kaynağı olarak PAuswGebV § 1 Abs. 1'i ikinci kaynak yap (24 yaş üstü 46 Euro; 24 yaş altı aynı fıkradaki düşük tutar; editör metinden birebir okusun) ve ücretin yalnız Aufenthaltserlaubnis/Niederlassungserlaubnis ve yeniden düzenleme için geçerli olduğunu yaz. Kaynak ikisine sığmıyorsa 029'u kaynak listesinden çıkar.

### oturum-belgesi-ucretleri: ciddi
- Bulgu: Altyazı ve özet "kayıp ya da süresi dolan kartın yenilenmesi 67 Euro" ve "belge süresi dolduğu ... için yeniden düzenlenirse 67 Euro" diyor. Yanlış: 67 Euro (Neuausstellung) PASAPORTUN süresi dolduğunda, kartın TEKNİK kullanım süresi dolduğunda, veri değiştiğinde, kayıp ya da çip bozulduğunda ödenir. Oturum izninin kendi geçerlilik süresi dolunca yapılan işlem uzatmadır (93 ya da 96 Euro). Okuyucu süresi dolan izni için 67 Euro hazırlar, gerçek tutar farklıdır. Claim 141 de "süre bitimi" diye aynı yanlışı taşıyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__45c.html "des Ablaufs der Gültigkeitsdauer des bisherigen Pass- oder Passersatzpapiers," ; "des Ablaufs der technischen Kartennutzungsdauer oder einer sonstigen Änderung der in § 78 Absatz 1 Satz 3 Nummer 1 bis 18 des Aufenthaltsgesetzes aufgeführten Angaben," ve https://www.gesetze-im-internet.de/aufenthv/__45.html "für einen weiteren Aufenthalt von mehr als drei Monaten" (93 Euro)
- Düzeltme: Altyazı: "kayıp, veri değişikliği ya da çip arızası nedeniyle yeniden düzenleme 67 Euro". Özet/adım/maliyet/claim 141'de "belge süresi dolduğu" yerine "pasaportun süresi dolduğu ya da kartın teknik kullanım süresi bittiği" yaz; oturum izninin kendi süresi dolunca uzatma (93/96 Euro) uygulanır diye ayır.

### oturum-belgesi-ucretleri: orta
- Bulgu: Türk okuyucu uyarısı yok. Ortaklık Hukuku kapsamındaki Türk vatandaşları bu tutarları ödemez; aynı paketteki ortaklik-hukuku kartı bunu söylüyor ama bu kartta tek cümle yok. Başlık "ücretleri" genel ve okuyucu 100 Euro'yu kendine uygular.
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__52a.html "Assoziationsberechtigte im Sinne dieser Vorschrift sind Ausländer, für die das Assoziationsrecht EU-Türkei auf Grund des Abkommens vom 12. September 1963 zur Gründung einer Assoziation zwischen der Europäischen Wirtschaftsgemeinschaft und der Türkei (BGBl. 1964 II S. 509, 510) Anwendung findet."
- Düzeltme: Özetin sonuna "AB–Türkiye Ortaklık Hukuku kapsamındakiler için ücret farklıdır" cümlesi ekle (kaynak 048; 046/047'den biri çıkmalıysa 047'yi koru). Tutarı yazma, ortaklik-hukuku kartına yönlendirme havale olur; kapsamı söylemek yeter.

### oturum-belgesi-ucretleri: küçük
- Bulgu: Rule 6: tarihe duyarlı ücret, kartta "güncel tarife" ibaresi yok; valid_until null. Kart yalnız Aufenthaltserlaubnis, Mavi Kart, ICT-Karte ücretini veriyor; Niederlassungserlaubnis ücreti (§ 44) kartta olmadığı hâlde başlık "oturum belgesi" genel.
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__45.html "An Gebühren sind zu erheben" (maddede yıl yok)
- Düzeltme: "güncel tarife" ekle; başlığı "Aufenthaltserlaubnis ve Mavi Kart AB ücretleri" olarak daralt ya da yerleşme izni ücretini ayrı kartta ver.

### is-degistirince-oturum-izni: orta
- Bulgu: Kart iki durumu karşılaştırıyor (Mavi Kart / belirli işe bağlı belge), ama en yaygın durumu söylemiyor: § 18a ve § 18b (meslek eğitimi ya da diplomayla uzman) belgeleri "jeder qualifizierten Beschäftigung" için verilir, yani belirli işe bağlı değildir. Okuyucu hangi belgenin "belirli işe bağlı" olduğunu kartta bulamaz; uzman belgesi taşıyan biri "izin almam gerek" diye yanlış sonuca varabilir. Başlık "iş değiştirince ne olur" genel soruyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html "Einer Fachkraft mit Berufsausbildung wird eine Aufenthaltserlaubnis zur Ausübung jeder qualifizierten Beschäftigung erteilt." ; https://www.gesetze-im-internet.de/aufenthg_2004/__4a.html "Wurde ein Aufenthaltstitel zum Zweck der Ausübung einer bestimmten Beschäftigung erteilt, ist die Ausübung einer anderen Erwerbstätigkeit verboten, solange und soweit die zuständige Behörde die Ausübung der anderen Erwerbstätigkeit nicht erlaubt hat."
- Düzeltme: Özet ve adımlara "§ 18a / § 18b belgesi her nitelikli işte çalışmaya izin verir; belgenin üzerindeki kısıtlamaya bak" cümlesi ekle ve claim yaz (kaynak olarak 035 tam yasa sayfasını kullan).

### is-degistirince-oturum-izni: küçük
- Bulgu: Çeviri: "oturum yasasının 2. kısım 4. bölümü" ters; kaynak "Kapitel 2 Abschnitt 4" = 2. bölüm 4. kısım (claim 150 de). "ab Kenntnis" (öğrenme tarihinden itibaren) eksik. Ayrıca bildirim yükümlülüğü işverene ait; kart çalışan okuyucuya yönelik, bu cümle gereksiz.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__4a.html "der zuständigen Ausländerbehörde innerhalb von vier Wochen ab Kenntnis mitteilen, dass die Beschäftigung, für die ein Aufenthaltstitel nach Kapitel 2 Abschnitt 4 erteilt wurde, vorzeitig beendet wurde"
- Düzeltme: Cümleyi sil ya da "yasanın 2. bölüm 4. kısmı ... öğrenmesinden itibaren 4 hafta" olarak düzelt.

### serbest-calisan-oturumu: orta
- Bulgu: Özet "üç şart birlikte aranır" diyor ve serbest meslek (freiberuflich) için "meslek icra izni" ayrı bir ek şart gibi sunuyor. Kaynakta serbest meslek için belge "Absatz 1'den farklı olarak" (abweichend von Absatz 1) verilir; yani freiberufler için üç şart aranmaz, yerine meslek icra izni gelir. Okuyucu serbest meslek sahibi ise gereksiz şartlara boğulur ya da vazgeçer.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__21.html "Einem Ausländer kann eine Aufenthaltserlaubnis zur Ausübung einer freiberuflichen Tätigkeit abweichend von Absatz 1 erteilt werden."
- Düzeltme: Özeti ikiye ayır: "Ticari serbest çalışmada üç şart aranır ...; serbest meslekte (freiberuflich) bu üç şart yerine meslek icra izni verilmiş ya da verilecek olmalıdır." 1.-3. adımların başına "Serbest meslek dışında:" ekle.

### ab-vatandasi-turk-aile-uyesi-oturum-karti: orta
- Bulgu: Türk okuyucu uyarısı "yalnız bir AB vatandaşının aile üyesi olarak kapsama girebilir" fazla kesin ve eksik. Kaynağa göre yasa AEA (EWR) vatandaşlarını, Çıkış Anlaşması kapsamındaki İngiliz vatandaşlarını ve serbest dolaşım hakkını sürekli kullanmış Almanların aile üyelerini de kapsıyor. Öte yandan sıradan Alman vatandaşıyla evli Türk için bu kart değil (kartın hiçbir yerinde yok); Alman eşli okuyucu başlığa bakıp kendini yanlış yerde arar. Başlık "AB vatandaşının Türk eşi" olduğundan bu okuyucuyu yönlendirmek gerekir.
- Kanıt: https://www.gesetze-im-internet.de/freiz_gg_eu_2004/__1.html "Staatsangehörigen der EWR-Staaten, die nicht Unionsbürger sind," ; "Staatsangehörigen des Vereinigten Königreichs Großbritannien und Nordirland nach dessen Austritt aus der Europäischen Union" ; "Familienangehörigen und nahestehenden Personen von Deutschen, die von ihrem Recht auf Freizügigkeit nach Artikel 21 des Vertrages über die Arbeitsweise der Europäischen Union nachhaltig Gebrauch gemacht haben."
- Düzeltme: "yalnız" kelimesini kaldır; "Bu rejim AB ve AEA vatandaşlarını, (çıkış anlaşması kapsamındaki) İngiliz vatandaşlarını ve aile üyelerini kapsar; Türk vatandaşı bunlardan biri değildir, ancak bunlardan birinin aile üyesi olarak kapsama girebilir" yaz. Alman vatandaşının Türk eşi için ayrı kural olduğunu bir cümleyle söyle ("sıradan Alman vatandaşının eşi bu kartı değil AufenthG kapsamında oturum alır"; kaynak 035 § 28 ile).

### ab-vatandasi-turk-aile-uyesi-oturum-karti: orta
- Bulgu: Yanlış çeviri: "yaşam ortağı" Lebenspartner için. Yasada Lebenspartner = Lebenspartnerschaftsgesetz'e göre ya da başka bir AB/AEA devletinde kayıtlı ortaklık (eingetragene Partnerschaft); resmî kaydı olmayan beraberlik (Lebensgefährte) ayrı "nahestehende Person" sayılır ve aynı aile üyesi tanımına girmez. Türkçede "yaşam ortağı" kayıtsız beraberliği de çağrıştırır.
- Kanıt: https://www.gesetze-im-internet.de/freiz_gg_eu_2004/__1.html "ein Lebenspartner im Sinne des Lebenspartnerschaftsgesetzes sowie" ; "eine Lebensgefährtin oder ein Lebensgefährte, mit der oder dem die Person eine glaubhaft dargelegte, auf Dauer angelegte Gemeinschaft eingegangen ist,"
- Düzeltme: "yaşam ortağı" yerine "kayıtlı yaşam ortağı (eingetragene Lebenspartnerschaft)" yaz (özet, adım, claim 168).

### ab-vatandasi-turk-aile-uyesi-oturum-karti: orta
- Bulgu: Başlık "nasıl alınır?" diyor ama kart yalnız yakınlık derecesini ve süreci (bilgi ver, 6 ay) anlatıyor. Kartın kendi kaynağına göre kart "freizügigkeitsberechtigte" aile üyesine verilir; yani AB vatandaşının kendisinin serbest dolaşım hakkı olması gerekir. 1. adım "AB vatandaşı yakınının aile üyesi sayıldığını kontrol et" yetersiz, hak şartı yok.
- Kanıt: https://www.gesetze-im-internet.de/freiz_gg_eu_2004/__5.html "Freizügigkeitsberechtigten Familienangehörigen, die nicht Unionsbürger sind, wird von Amts wegen innerhalb von sechs Monaten, nachdem sie die erforderlichen Angaben gemacht haben, eine Aufenthaltskarte für Familienangehörige von Unionsbürgern ausgestellt, die fünf Jahre gültig sein soll."
- Düzeltme: Özet ve 1. adıma "Kart, serbest dolaşım hakkı olan bir AB vatandaşının aile üyesine verilir" ekle ve claim yaz. (§ 2 koşulları kaynakta olmadığı için sayma; yalnız "hakkı olması gerekir" de.)

### oturum-izninin-yurt-disinda-kalinca-sona-ermesi: orta
- Bulgu: Başlık "yurt dışında ne kadar kalırsan" diye soruyor; kart tek kural olarak 6 ay (veya daha uzun süre) diyor. Kaynağa göre belge, doğası gereği geçici olmayan bir nedenle ülkeden çıkıldığında ALTI AYI BEKLEMEDEN, çıkış anında da sona erer. Kartta bu yok; okuyucu "altı ay hakkım var" diye taşınıp izin kaybeder.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__51.html "6. wenn der Ausländer aus einem seiner Natur nach nicht vorübergehenden Grunde ausreist,"
- Düzeltme: Özetin başına "Kalıcı bir nedenle (ör. taşınma) çıkarsan belge altı ayı beklemeden sona erer; geçici bir nedenle çıkarsan altı ay ya da Ausländerbehörde'nin belirlediği daha uzun süre" ekle; claim yaz.

### oturum-izninin-yurt-disinda-kalinca-sona-ermesi: küçük
- Bulgu: Not cümlesi "Yalnızca yasal askerlik görevi nedeniyle ..." diyor: (a) "yalnızca" yanlış, aynı maddede başka istisnalar var (daha uzun süre belirlenmesi, 15 yıl kuralı); (b) kaynak "im Heimatstaat" (kendi ülkende) diyor, kart "yasal askerlik" demekle ülke bağını kaybediyor, Türk okuyucu için doğrudan ilgili bir ayrıntı; (c) istisna yalnız altı ay kuralı (Nr. 7) içindir.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__51.html "wenn die Frist lediglich wegen Erfüllung der gesetzlichen Wehrpflicht im Heimatstaat überschritten wird und der Ausländer innerhalb von drei Monaten nach der Entlassung aus dem Wehrdienst wieder einreist"
- Düzeltme: "Altı aylık süre yalnızca kendi ülkendeki yasal askerlik görevi yüzünden aşılırsa ve askerlikten çıktıktan sonra üç ay içinde dönersen belge sona ermez" yaz; baştaki "Yalnızca"yı kaldır.

## Doğrulanan ve temiz çıkanlar (bulgu yok)
- Ücret sayıları: 75 / 25 Euro (AufenthV § 46), 100 / 96 / 93 / 98 Euro (§ 45), 67 Euro tutarı (§ 45c), iDATA 39,92 EUR, A1 sertifikası sağlayıcıları ve 12 ay şartı: kaynak ve canlı sayfayla aynı.
- Mavi Kart %50, %45,3, ISCO grupları, 6 ay iş teklifi, 12 ay / 30 gün kuralı; Niederlassungserlaubnis 5 yıl / 60 ay / 36 ay / 27 ay / 21 ay / 2 yıl / 24 ay; Chancenkarte 6 puan, 20 saat, 2 hafta, 1 yıl + 2 yıl; öğrenci 140 iş günü ve 2 yıl; StAG 5 yıl ve B1; FreizügG 6 ay ve 5 yıl; § 51 altı ay / 12 ay / 15 yıl: kaynak ve canlı sayfayla aynı.
- Federal yapı, şehir adı, eyalet rakamı: yok.
- Havale cümlesi: yok (mavi-kart'taki "ilan eder" cümlesi hariç, yukarıda).
- Ortaklık Hukuku kartı kaynağı aşmıyor.
