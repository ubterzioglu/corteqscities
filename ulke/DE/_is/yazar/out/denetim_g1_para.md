# Almanya ulusal paketi, konu "para": bağımsız denetim (g1)

Denetçi: yazarı olmayan oturum. Kart dosyalarına dokunulmadı. Yazarın gaps.md dosyası okunmadı.

## Özet
- Kart sayısı: 12. Bulgu sayısı: ciddi 1, orta 15, küçük 20.
- Ciddi: emeklilik kartında "67 yaş" genellemesi (1963 ve öncesi doğumlular için yanlış).
- Yöntem: her kartın summary/steps/documents/timing/cost/note cümleleri kartın kendi `source_ids` metniyle (`text_file`) satır satır karşılaştırıldı. Tarihe duyarlı kaynaklar Python urllib ile canlı indirilip anahtar sayı ve cümleler kopyada aranarak karşılaştırıldı. Claims dosyası 6 kart için (gelir-vergisi, vergi-sınıfı, kdv, kilise, maaş, emeklilik) tek tek okundu; diğer 6 kartın claims'i okunmadı.
- Canlı doğrulanan (kopyayla aynı çıktı): EStG §32a, EStG §38b, AO §149, UStG §12, PflVG §1, SGB VI §35, BDSG §31, DRV Sozialversicherungsrechengrößen 2026, BMG beitraege-und-tarife (Stand 3. September 2026), BaFin Basiskonto, BaFin Kontenwechsel, BaFin Haftpflicht, DRV Verbindungsstelle Türkei, BfDI Auskunftsrecht, Bundesbank SEPA ve Echtzeitüberweisung sayfaları. Ek olarak kaynakta olmayan ama kartı etkileyen SGB VI §235 ve §50 canlı açıldı.
- Canlı açılamayan / bakılmayan: ELSTER Anleitung sayfası (kopya 460 KB, yalnız kopyada arandı; canlı karşılaştırma yapılmadı), kapalı siteler (bmi.bund.de, make-it-in-germany.com, auswaertiges-amt.de) denenmedi. Pflegeversicherung oranı yalnız genel web aramasıyla görüldü (resmî kaynakla doğrulanmadı). III/V kaldırılması: genel web aramasında yasalaşma kanıtı bulunmadı; EStG §38b canlı metni hâlâ I-VI sınıflarını sayıyor.
- Yazarın sorulan noktaları: (1) 2026 tarife/Grundfreibetrag/dilim sınırları kaynakla ve canlı sayfayla birebir doğru. (2) %42/%45 kaynakta yüzde olarak geçmiyor, formül katsayısı (`0,42 • x – 11 135,63`); yazar yüzdeye çevirmiş, bulgu (gelir vergisi kartı). (3) SV oranları (%18,6 / %9,3 / %2,6 / %1,3 / %14,6 / %14,0 / ortalama Zusatzbeitrag %2,9 / BBG 8.450 ve 5.812,50) kaynak ve canlıyla doğru; Pflegeversicherung eksik. (4) III/V kaldırılması kartta hiç yok, kaynak da hiç söylemiyor; bu sessizlik doğru, bulgu değil. (5) Basiskonto kapsamı kaynakla uyumlu, ret nedenleri ve belge kapsamı eksik. (6) Emeklilik yaşı: §235 geçişi atlanmış, ciddi. (7) Türkiye-Almanya anlaşması cümleleri DRV sayfasıyla sınırlı, yalnız küçük kapsam notları var. (8) Kirchensteuer: federal çerçeve doğru, ama "oran ve üyelikten çıkış eyalete göre değişir" cümlesi kartın iki kaynağında yazmıyor. (9) Havale cümlesi (resmî sayfaya yönlendirme) bulunmadı; "yaklaşık" ve şehir adı bulunmadı; kaynakta olmayan sayı yok.

---

### basiskonto-temel-hesap-hakki: orta
- Bulgu 1 (orta): Başlık "banka beni reddedebilir mi?" diye soruyor, kart "yasal bir ret nedeni varsa" diyor ama ret nedenlerinin hiçbirini saymıyor. BaFin sayfasında dört neden sayılı (Almanya'da zaten ödeme hesabı olması, son 3 yılda bankaya/çalışanlarına/müşterilerine karşı kasıtlı suç mahkûmiyeti, aynı bankada hesabın ödeme gecikmesi/yasak kullanım nedeniyle feshedilmiş olması, kara para/kredi hukuku yükümlülüğü ihlali).
  - Kanıt: https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/basiskonto/basiskonto_node.html "Die Bank darf den Abschluss eines Basiskontovertrags nur in bestimmten Fällen verweigern:"
  - Düzeltme: summary'ye dört ret nedenini kısa madde olarak ekle (aynı sayfa). Subtitle'daki "yalnızca yasal bir ret nedeni varsa" cümlesinin yanına "(örneğin Almanya'da zaten bir ödeme hesabın varsa)" ekle.
- Bulgu 2 (orta): steps/documents'ta "pasaport, kimlik ya da kimlik yerine geçen belge" yazıyor. Kaynak "fotoğraflı resmî ve Almanya'da pasaport/kimlik zorunluluğunu karşılayan, yabancılar hukukunca tanınan pasaport, kimlik, pasaport/kimlik yerine geçen belge" diyor ve Duldung, Ankunftsnachweis, Aufenthaltsgestattung'u da sayıyor. Türk okuyucu "kimlik" sözcüğünü nüfus cüzdanı diye okuyabilir; kaynakta Türk kimliğinin kabulüne dair bir şey yok.
  - Kanıt: aynı URL "Gültige amtliche Ausweise mit Lichtbild, die die Pass- und Ausweispflicht in Deutschland erfüllen. Dazu zählen deutsche oder ausländerrechtlich anerkannte Pässe, Personalausweise sowie Pass- oder Ausweisersatzpapiere."
  - Düzeltme: "geçerli, fotoğraflı resmî kimlik belgesi (Almanya'nın pasaport ve kimlik zorunluluğunu karşılayan pasaport, kimlik ya da bunların yerine geçen belge)" yaz; "kimlik" tek başına kalmasın.
- Bulgu 3 (küçük): "Türk vatandaşı da bu ikamet şartıyla hak sahibidir" kaynakta yok. Kaynak "alle Verbraucher, die sich rechtmäßig in der EU aufhalten" diyor, uyruk sözü yok. Ayrıca kaynak "aufhalten" (bulunmak) diyor, kart "ikamet" yazıyor; kaynak evsizleri ve Duldung'u da kapsadığını söylüyor, "ikamet" daha dar çağrışım yapar.
  - Kanıt: aynı URL "Alle Verbraucherinnen und Verbraucher, die sich rechtmäßig in der Europäischen Union aufhalten, haben grundsätzlich Anspruch auf ein Basiskonto"
  - Düzeltme: "Türk vatandaşı da ..." cümlesini "Hakkın şartı uyruk değil, AB'de hukuka uygun bulunmaktır" biçimine çevir; "ikamet" yerine "hukuka uygun bulunma".
- Bulgu 4 (küçük): "Bankadan başvurunun alındığını sana yazılı onaylamasını iste" cümlesinde "yazılı" kaynakta yok. ZKG §31(2): "den Eingang des Antrags unter Beifügung einer Abschrift des Antrags zu bestätigen".
  - Düzeltme: "yazılı" sözcüğünü sil, "başvurunun alındığını başvuru örneğiyle birlikte onaylamak zorundadır" yaz.
- Bulgu 5 (küçük): Ret halinde kaynak üç yol sayıyor (BaFin idari işlemi, hukuk mahkemesinde dava, tüketici tahkim kuruluşu); kart yalnız BaFin'i veriyor.
  - Kanıt: aynı URL "Wurde Ihr Antrag abgelehnt, haben Sie drei Möglichkeiten, dagegen vorzugehen:"
  - Düzeltme: son adıma iki yolu ekle.
- Bulgu 6 (küçük): documents'ta "Basiskonto başvuru formu" belge olarak sayılmış, steps'te "formu kullanmak zorunlu değil" deniyor; çelişki gibi okunur.
  - Düzeltme: documents'tan formu çıkar ya da "isteğe bağlı" ekle.

### iban-sepa-havale-anlik-havale-lastschrift: orta
- Bulgu 1 (orta): steps'te "Lastschrift (alacaklının hesabından tahsilat)" yanlış çeviri. Lastschrift, alacaklının ödeyenin hesabından çektiği tahsilattır; "alacaklının hesabından" ifadesi tersini söylüyor.
  - Kanıt: https://www.bundesbank.de/dynamic/action/de/aufgaben/unbarer-zahlungsverkehr/serviceangebot/sepa/613964/fragen-und-antworten-zu-sepa "Zustimmung des Zahlers zum Einzug der Zahlung per SEPA-Lastschrift an den Zahlungsempfänger"
  - Düzeltme: "Lastschrift (alacaklının, senin hesabından senin onayınla çektiği tahsilat)".
- Bulgu 2 (orta): Başlıkta Lastschrift "nasıl işler?" diye geçiyor ama kart yalnız mandat veriyor. Kaynakta tüketici için temel hak var ve kartta yok: SEPA-Basislastschrift'te borçlandırmadan sonra 8 hafta içinde gerekçesiz iade, yetkisiz (mandatsız) Lastschrift için 13 ay.
  - Kanıt: aynı URL "Eine SEPA-Basislastschrift kann innerhalb von acht Wochen nach Belastung ohne Angabe von Gründen an den Einreicher zurückgegeben werden" ve "kann bei beiden Verfahren vom Zahler innerhalb von 13 Monaten nach der Kontobelastung zurückgegeben werden."
  - Düzeltme: not'a iki cümle ekle (8 hafta gerekçesiz iade; yetkisiz tahsilat için 13 ay), claims'e ekle.
- Bulgu 3 (orta, Türk okuyucu): Başlık "Almanya'da para gönderme"; Türk okuyucunun ilk sorusu Türkiye'ye gönderim. Kaynaktaki SEPA ülke listesinde Türkiye yok, kart bunu söylemiyor; "başka para birimi için dış havale gerekir" cümlesi yeterince açık değil.
  - Kanıt: aynı URL "Dieser besteht aus den 27 EU‑Staaten, den weiteren EWR‑Ländern Island, Liechtenstein und Norwegen sowie der Schweiz, Albanien, Andorra, Moldau, Monaco, Montenegro, Nordmazedonien, San Marino, Serbien, dem Staat Vatikanstadt und dem Vereinigten Königreich."
  - Düzeltme: not'a "Türkiye SEPA ülkeleri arasında değildir; Türkiye'ye gönderim SEPA havalesi değil dış havaledir (Auslandsüberweisung)" ekle (bu iki dayanak SEPA listesi ve "Zahlungen in anderen europäischen Währungen sind weiterhin nur mit einer Auslandsüberweisung möglich" cümlesidir).
- Bulgu 4 (küçük): Summary ve steps "banka alıcı adı ile IBAN'ı karşılaştırır" diyor, kapsam yok. Kaynakta: yalnız Euro bölgesinde yerleşik bankalar zorunlu (9 Ekim 2025'ten), AB geneline 9 Temmuz 2027'de genişliyor; yalnız Zahlungskonto (Girokonto) için, tasarruf/vadeli hesaplar dışında.
  - Kanıt: https://www.bundesbank.de/dynamic/action/de/aufgaben/unbarer-zahlungsverkehr/veroeffentlichungen/fragen-und-antworten-zu-echtzeitueberweisungen-und-empfaengerueberpruefung/963980/fragen-und-antworten-zu-echtzeitueberweisungen-und-empfaengerueberpruefung- "Sparkonten wie beispielsweise Ihr Tages- oder Festgeldkonto sowie weitere Kontenarten ... fallen nicht unter den Anwendungsbereich der Regelung."
  - Düzeltme: note'a "Bu kontrol cari hesap (Girokonto) türü ödeme hesaplarında yapılır; vadeli/tasarruf hesaplarında yapılmaz" ekle.
- Bulgu 5 (küçük): Subtitle "Euro bölgesinde havale IBAN ile yapılır" diyor, summary ve kaynak "AEA içi" diyor (BIC gerekmemesi AEA'da geçerli, Euro bölgesinde değil).
  - Düzeltme: subtitle'da "Euro bölgesinde" yerine "Avrupa Ekonomik Alanı'nda".

### gelir-vergisi-2026-grundfreibetrag-dilimler: orta
- Rakamlar (12.348, 17.799, 69.878, 277.825, Splitting, "volle Euro abgerundet") kaynak ve canlı EStG §32a ile birebir doğru. Başlık, summary ve note'taki "2026" ifadesi kaynağın "ab dem Veranlagungszeitraum 2026" ifadesine uyuyor.
- Bulgu 1 (orta): "%42" ve "%45" yüzde olarak kaynakta geçmiyor. Kaynakta formül katsayısı var: `0,42 • x – 11 135,63` ve `0,45 • x – 19 470,38`. Subtitle "üst dilimlerde %42 ve %45 uygulanır" ve summary "69.879-277.825 euro (%42)" yazarın yaptığı türetme; ayrıca "(%42)" ifadesi tüm gelire düz %42 uygulanıyormuş gibi okunuyor, oysa formül sabit çıkarır (11.135,63) ve vergi tüm gelirin %42'si değildir. Subtitle iki üst oranı verip ilk iki dilimi (formül) anmadığı için tarifenin yalnız iki oranı varmış izlenimi veriyor. Aynı kartın claims dosyası doğru yazıyor ("0,42 katsayısı"), kartın kendisi yüzdeye çevirmiş; claims ile kart tutarsız.
  - Kanıt: https://www.gesetze-im-internet.de/estg/__32a.html "von 69 879 Euro bis 277 825 Euro: 0,42 • x – 11 135,63;"
  - Düzeltme: subtitle: "2026 için vergilendirilecek gelirin ilk 12.348 euro'su vergiden muaftır; üstündeki dört dilim kanunda formülle verilir." Summary'de "(%42)" ve "(%45)" ifadelerini sil, "69.879-277.825 euro (formülde 0,42 katsayısı) ve 277.826 euro ve üstü (formülde 0,45 katsayısı)" yaz. Not'taki cümle zaten doğru.
- Bulgu 2 (küçük): valid_until 2026-12-31 verilmiş; kaynak "ab dem Veranlagungszeitraum 2026" diyor, bitiş tarihi vermiyor (sonraki yıl tarifesi gelecek ama kaynakta yok). Kural 11: bitiş kaynakta yazmıyorsa null.
  - Düzeltme: valid_until'i kaynak bitiş vermediği için null yap ya da editör kararıyla bırak.

### vergi-sinifi-lohnsteuerklasse-1-6: orta
- III/V kaldırılması kartta hiç geçmiyor ve kaynak (EStG §38b, canlı aynı) da hiçbir değişiklik söylemiyor; bu sessizlik doğru, bulgu değil. Canlı sayfada sınıflar I-VI hâlâ geçerli.
- Bulgu 1 (orta): steps "Evliysen ... IV. sınıftasın; eşin maaş almıyorsa da bu geçerlidir." yazıyor. Kaynakta koşul var: "kein Antrag nach Nummer 3 Buchstabe a gestellt worden ist" (III için başvuru yapılmamışsa). Claims dosyasında bu koşul var, kartta düşmüş. Tek gelirli çiftler normalde III/V başvuru yapar; kart bunu IV zannettirir.
  - Kanıt: https://www.gesetze-im-internet.de/estg/__38b.html "dies gilt auch, wenn einer der Ehegatten keinen Arbeitslohn bezieht und kein Antrag nach Nummer 3 Buchstabe a gestellt worden ist;"
  - Düzeltme: "eşin maaş almıyorsa ve III için ortak başvuru yapılmamışsa da bu geçerlidir."
- Bulgu 2 (küçük): I. sınıf tarifi eksik: kaynakta "beschränkt einkommensteuerpflichtig" (sınırlı vergi yükümlüsü) çalışanlar da I. sınıfta.
  - Kanıt: aynı URL "b) beschränkt einkommensteuerpflichtig sind;"
  - Düzeltme: summary'ye "Almanya'da sınırlı vergi yükümlüsü çalışanlar da I. sınıftadır" ekle.
- Bulgu 3 (küçük): "Sınıf değişikliği başvurularını resmî formla yap ve elle imzala" kapsamı kaynaktan geniş. Kaynakta form ve el imzası zorunluluğu §38b Abs. 3 başvuruları (daha elverişsiz sınıf istemek, III/V'den IV'e geçiş) için; III/V birleşimi başvurusunun (Abs. 1 Nr. 3a) biçimi bu maddede yok.
  - Kanıt: aynı URL "Diese Anträge sind nach amtlich vorgeschriebenem Vordruck zu stellen und vom Antragsteller eigenhändig zu unterschreiben."
  - Düzeltme: cümleyi "III veya V'ten IV'e geçiş ve daha elverişsiz sınıf istemek için başvuruyu resmî formla yap ve elle imzala" biçimine daralt; documents'taki "Resmî başvuru formu"nu aynı kapsamla yaz.

### yillik-vergi-beyannamesi-elster-son-tarih: orta
- Bulgu 1 (orta): Summary/timing "genel son tarih yedi ay" diyor. Kartın kendi kaynağı AO §149'da vergi danışmanı (Steuerberater) ve benzerleri aracılığıyla verilen beyannameler için çok daha geç süre var: ikinci takvim yılının Şubat ayının son günü (2025 vergi yılı için 28 Şubat 2027). Kart yalnız "genel" kuralı veriyor, ama danışmanla çalışan okuyucu (çok yaygın) için süre yanlış okunur. Üstelik bugün (25.10.2026) kartın örnek tarihi 31 Temmuz 2026 geçmiş; danışmanı olanlar için süre hâlâ açık.
  - Kanıt: https://www.gesetze-im-internet.de/ao_1977/__149.html "so sind diese Erklärungen ... spätestens bis zum letzten Tag des Monats Februar ... des zweiten auf den Besteuerungszeitraum folgenden Kalenderjahres abzugeben."
  - Düzeltme: summary ve timing'e "Vergi danışmanı (Steuerberater) aracılığıyla verilen beyannamelerde süre ikinci yılın Şubat ayının son günüdür (AO §149 Abs. 3)" ekle. Kart bugün için tarihi geçmiş örnek veriyor: ELSTER 2026 yılı sayfası yayımlandığında 2026 yılı için (31 Temmuz 2027) güncelle.
- Bulgu 2 (orta, yanlış çeviri): "gecikme zammı" yazılmış. Kaynak "Verspätungszuschlag" diyor; Türkçede gecikme zammı ödeme gecikmesinin faizini çağrıştırır. Verspätungszuschlag geç beyan için ek ödemedir.
  - Kanıt: https://www.elster.de/eportal/helpGlobal?themaGlobal=help_est_ufa_10_2025 "kann Ihr Finanzamt einen Verspätungszuschlag und, falls erforderlich, Zwangsgelder festsetzen."
  - Düzeltme: "gecikme zammı" yerine "geç beyan zammı (Verspätungszuschlag)".
- Bulgu 3 (orta): Başlık "yıllık gelir vergisi beyannamesi vermek zorunda mısın?" genel soru; kart yalnız çalışanlar (Arbeitnehmer) için cevap veriyor. Kaynak ayrıca "Personen, die keinen Arbeitslohn bezogen haben ... haben deshalb ebenfalls eine Einkommensteuererklärung abzugeben" ve vergi kesilmemiş sermaye gelirleri ile önceki yıldan Verlustvortrag için beyanname zorunluluğunu söylüyor. Maaş dışı geliri olan okuyucu "yalnızca belirli durumlarda" cümlesini kendine uygular.
  - Kanıt: https://www.elster.de/eportal/helpGlobal?themaGlobal=help_est_ufa_10_2025 "Personen, die keinen Arbeitslohn bezogen haben, werden mit ihren steuerpflichtigen Einkünften zur Einkommensteuer veranlagt und haben deshalb ebenfalls eine Einkommensteuererklärung abzugeben."
  - Düzeltme: başlığı "Maaşlı çalışan olarak ... vermek zorunda mısın?" yap ya da summary'ye "Maaş almayanlar ve vergi kesilmemiş sermaye geliri olanlar da beyanname verir" cümlesini ekle.
- Bulgu 4 (küçük): Tarihe duyarlı (31 Temmuz 2026, 31 Aralık 2029) olduğu hâlde valid_until null.
  - Düzeltme: editör kararı: 2025 yılı sayfasına dayandığı için 2026-12-31 ya da güncel yıl sayfası çıkınca yenile.

### kdv-umsatzsteuer-oranlari-19-ve-7: orta
- Rakamlar (%19, %7, §12 Abs. 1 ve 2, Anlage 2) kaynak ve canlı UStG §12 ile doğru.
- Bulgu 1 (orta): Kart indirimli oranın hangi günlük kalemlere uygulandığını hiç söylemiyor; steps üçüncü madde ("Mal teslimlerinde %7 ...") ikinci maddenin tekrarı. Aynı kaynakta okuyucuyu ilgilendiren kalemler açık: restoran ve yemek hizmeti (içecek hariç), 50 km'ye kadar/belediye içi şehir içi taşıma ve raylı taşıma, kısa süreli konaklama, tiyatro/konser/müze girişi.
  - Kanıt: https://www.gesetze-im-internet.de/ustg_1980/__12.html "15. die Restaurant- und Verpflegungsdienstleistungen, mit Ausnahme der Abgabe von Getränken."
  - Düzeltme: summary'ye bu dört-beş kalemi §12 Abs. 2 numaralarıyla ekle; tekrar eden steps maddesini sil.
- Bulgu 2 (küçük): Subtitle "kanunun saydığı işlemlerde indirimli oran %7" diyor; §12 Abs. 3 ayrıca %0 oranını (belirli güneş paneli teslimleri) veriyor, kart "indirimli oran yalnız %7" gibi okunuyor.
  - Düzeltme: not'a tek cümle: "Küçük fotovoltaik sistemlerin teslimi ve kurulumu için oran %0'dır (§12 Abs. 3)."

### kilise-vergisi-kirchensteuer-cerceve: orta
- Federal çerçeve (Anayasa md. 140, WRV md. 137 Abs. 6 üzerinden "landesrechtliche Bestimmungen", eyalet rakamı yok) doğru kurulmuş; eyalet oranı ya da eyalet adı yazılmamış.
- Bulgu 1 (orta): Başlık, subtitle, summary, steps ve note "oran ve üyelikten çıkış usulü eyalete göre değişir" diyor. İki kaynakta (GG md. 140 / WRV md. 137 ve EStG §51a) ne oran ne üyelikten çıkış geçiyor. WRV md. 137(6) yalnız vergi toplama yetkisini "landesrechtlichen Bestimmungen" a bağlıyor; §51a(2b) ise oranı "Kirchensteuersatz der Religionsgemeinschaft" (dini topluluğun oranı) diye anıyor, yani kartın kendi kaynağına göre oran dini topluluğun belirlediği orandır. Claims dosyasında da bu iddia için claim yok. Step 3 "oranını ve üyelikten çıkış usulünü ilgili eyaletin yasası belirler" kaynaksız.
  - Kanıt: https://www.gesetze-im-internet.de/gg/art_140.html "sind berechtigt, auf Grund der bürgerlichen Steuerlisten nach Maßgabe der landesrechtlichen Bestimmungen Steuern zu erheben." ve https://www.gesetze-im-internet.de/estg/__51a.html "nach dem Kirchensteuersatz der Religionsgemeinschaft, der der Kirchensteuerpflichtige angehört"
  - Düzeltme: "oran ... eyalete göre değişir" ve "üyelikten çıkış usulü" ifadelerini başlıktan, subtitle'dan, summary'den, step 3'ten ve note'tan sil; yerine "Vergiyi toplama yetkisi eyalet hukukuna göre kullanılır (WRV md. 137/6); oran üyesi olduğun dini topluluğun oranıdır (EStG §51a)" yaz. Oran ve çıkış usulü için kaynak ancak eyalet paketi/kanun sayfası olabilir, ulusal kartta sil. Başlık: "Kilise vergisi (Kirchensteuer) nedir? Kim alabilir ve nasıl hesaplanır?"
- Not (bulgu değil): Okuyucunun bu vergiye tabi olup olmadığı (üyelik) kartta yalnız "üyesi olduğun bir dini topluluk varsa" diye geçiyor; kaynak başka bir şey söylemediği için yazarın sınırı doğru.

### maas-sosyal-sigorta-kesintileri-2026: orta
- Rakamlar (RV %18,6/%9,3, ALV %2,6/%1,3, KV %14,6, indirimli %14,0, ortalama Zusatzbeitrag %2,9, BBG aylık 5.812,50 ve 8.450, Sonderkündigungsrecht, Familienversicherung) kaynak ve canlı sayfalarla birebir doğru. valid_until 2026-12-31 uygun.
- Bulgu 1 (orta): Başlık "Maaşından hangi sosyal sigorta primleri kesilir?" ve summary/steps yalnız emeklilik, işsizlik, sağlık sayıyor. Bordroda bakım sigortası (Pflegeversicherung) da kesilir; kartta ve iki kaynakta yok. Okuyucu bordroda göreceği kalemi bulamaz, başlık eksik cevap verir.
  - Kanıt: kartın kaynaklarında yok; resmî kaynak eklenmeli: https://www.gesetze-im-internet.de/sgb_11/__55.html (bu denetimde açılıp metni okunmadı; genel aramada 2026 oranı %3,6 çıktı, doğrulanmadı).
  - Düzeltme: bakım sigortası oranı ve işçi payını resmî kaynaktan (BMG ya da SGB XI §55) ekle ve bordro adımına "Pflegeversicherung" kalemini yaz; eklenemezse başlığı "emeklilik, işsizlik ve sağlık" kapsamına daralt ve bakım sigortasının ayrıca kesildiğini tek cümleyle belirt.
- Bulgu 2 (küçük): "her birinde primi işveren ile sen yarı yarıya ödersin" kaynakta emeklilik, işsizlik ve sağlık için geçiyor (kaynak 018 ve 028); kapsam sınırı kartta yok (Azubi/geringverdiener için kaynak 028'de ayrı "durchschnittlicher Zusatzbeitragssatz" kuralı var).
  - Düzeltme: not'a "Bu paylaşım normal çalışan içindir; çok düşük maaşlı çalışanlar ve stajyerler için ayrı hesap vardır" yazmak yerine kaynaksız genelleme olmaması için "kural olarak" ekle.

### zorunlu-arac-sigortasi-ve-ozel-sorumluluk-sigortasi: orta
- Bulgu 1 (orta): Başlık "Almanya'da hangi sigorta zorunlu?" genel soru; kart yalnız araç sahibinin sorumluluk sigortasını anlatıyor ve özel sorumluluk sigortasının zorunlu olmadığını söylüyor. Yeni gelen biri başlıktan "zorunlu tek sigorta araç sigortası" sonucunu çıkarır; sağlık sigortası zorunluluğu kartta yok. Kural 12: başlık yalnız kaynağın kapsadığı yönü kapsamalı.
  - Kanıt: https://www.gesetze-im-internet.de/pflvg/__1.html "ist verpflichtet, für sich, den Eigentümer und den Fahrer sowie weitere Personen ... eine Haftpflichtversicherung ... abzuschließen und aufrechtzuerhalten."
  - Düzeltme: başlığı "Araç sahibi için sorumluluk sigortası (Kfz-Haftpflicht) zorunlu mu? Özel sorumluluk sigortası (Privathaftpflicht) ne işe yarar?" yap. "Hangi sigorta zorunlu?" sorusu sağlık kartında karşılanıyorsa oraya yönlendirme yazma, sadece başlığı daralt.
- Kaynakla uyumlu doğrulanan cümleler: "Araçla yapılan bir kazada yalnızca Kfz-Haftpflicht devreye girer" (BaFin: "greift ausschließlich die Kfz-Haftpflichtversicherung"), Versicherungssumme, zararın bildirimi, eş ayrılığı, eş/çocukları koruma ve karşılıklı zarar istisnası.

### almanya-emeklilik-yasi-bekleme-suresi-turkiye-anlasmasi: ciddi
- Bulgu 1 (ciddi): Kart 67 yaşı herkese genelliyor (başlık, subtitle, summary, timing). SGB VI §235 geçiş kuralına göre 1 Ocak 1964'ten önce doğanlar için Regelaltersgrenze 65 yıl 1 aydan 66 yıl 10 aya kadar kademeli yükselir (1958: 66 yıl, 1959: 66 yıl 2 ay, 1960: 66 yıl 4 ay, 1961: 66 yıl 6 ay, 1962: 66 yıl 8 ay, 1963: 66 yıl 10 ay). 2026'da emeklilik yaşına en yakın okuyucular tam bu kuşak; kart onlara yanlış yaş veriyor ve §35'in kendisi (kartın tek yasal kaynağı) bu istisnayı içermiyor.
  - Kanıt: https://www.gesetze-im-internet.de/sgb_6/__235.html "Versicherte, die vor dem 1. Januar 1964 geboren sind, haben Anspruch auf Regelaltersrente, wenn sie ... Die Regelaltersgrenze wird frühestens mit Vollendung des 65. Lebensjahres erreicht." ve "1960 16 66 4"
  - Düzeltme: başlıktan, subtitle'dan, summary'den ve timing'den "67" genellemesini kaldır; "1964 ve sonrası doğumlular için 67; daha önce doğanlar için yaş doğum yılına göre 65 yıl 1 aydan 66 yıl 10 aya kadar kademeli artar (SGB VI §235)" yaz. Kaynak olarak §235 eklenmeli (kart 2 kaynak sınırında: §35 ile DRV sayfası var; §35 yerine §235 ya da DRV sayfasından birini çıkar, kuralı editör seçsin). Claims'e §235 satırı ekle.
- Bulgu 2 (orta): Başlık "bekleme süresi" vaat ediyor; kart süreyi (5 yıl) hiçbir yerde vermiyor. Summary yalnız "genel bekleme süresinin dolması" diyor.
  - Kanıt: https://www.gesetze-im-internet.de/sgb_6/__50.html "Die Erfüllung der allgemeinen Wartezeit von fünf Jahren ist Voraussetzung für einen Anspruch auf 1. Regelaltersrente"
  - Düzeltme: summary'ye "genel bekleme süresi 5 yıldır" ekle (kaynak olarak §50; kaynak sınırı için yukarıdaki seçimle birlikte karar ver).
- Bulgu 3 (küçük): Subtitle "anlaşma Alman ve Türk sigorta sürelerini birleştirir" geniş. Kaynak süreleri "bekleme süresi ve diğer şartlar incelenirken" toplanır diyor; aylık hesabında birleştirme söylemiyor.
  - Kanıt: https://www.deutsche-rentenversicherung.de/DRV/DE/Rente/Ausland/Ansprechpartner-und-Verbindungsstellen/Tuerkei/Tuerkei-deutsch/Verbindungsstelle_Tuerkei.html "zusammengerechnet werden, wenn die Wartezeit und die sonstigen Anspruchsvoraussetzungen ... geprüft werden."
  - Düzeltme: subtitle: "anlaşma Alman ve Türk sigorta sürelerini hak şartları incelenirken toplar".
- Bulgu 4 (küçük): Dil hatası: "Türkiye'deki tam adresini ile kimlik numaranı bildir".
  - Düzeltme: "tam adresini ve kimlik numaranı bildir".
- Bulgu 5 (küçük): "Başvuruyu oturduğun ülkenin yetkili kurumuna yap" kaynakta "grundsätzlich"; kaynak ayrıca Türkiye'de oturanlar için Almanya'da noter vekâletli temsilciyle başvuru istisnasını veriyor. Kart "grundsätzlich" ile sınırı düşürmüş.
  - Düzeltme: "kural olarak" ekle.
- Bulgu 6 (küçük): Prim iadesi (note) kimin başvurabileceğini söylemiyor; kaynakta yalnız "türkische Staatsangehörige bei Aufenthalt im Ausland" formundan anlaşılıyor, koşullar yok. Okuyucu herkes için serbest sanabilir.
  - Düzeltme: "Prim iadesi anlaşmada düzenlenmiştir; hak koşulları için ilgili form: Türk vatandaşları için yurt dışında ikamet halinde" gibi kaynağın verdiği kadarla daralt ya da cümleyi sil.
- Türk okuyucu: Türkiye-Almanya anlaşması cümleleri kaynak (DRV Verbindungsstelle Türkei) ile sınırlı, ek iddia yok; olumlu.

### kredi-bilgi-kurulusu-bilgi-hakki-dsgvo-md-15-skor: küçük
- Bulgu 1 (küçük): Başlık ve summary "Schufa" adını veriyor. Kartın iki kaynağında (BfDI sayfası ve BDSG §31) "Schufa" geçmiyor; yalnız "Auskunftei" geçiyor. Marka adı kaynaksız ek.
  - Kanıt: https://www.bfdi.bund.de/DE/Buerger/Inhalte/Allgemein/Betroffenenrechte/Betroffenenrechte_Auskunftsrecht.html (metinde "Schufa" yok)
  - Düzeltme: "Schufa gibi" ifadesini sil, "kredi bilgi kuruluşlarında (Auskunftei)" yaz.
- Rakamlar ve şartlar doğrulandı: iki yazılı ihtar, ilk ihtardan dört hafta, önceden bildirim, borcun itirazsız olması, yalnız adres verisiyle skor yasağı (BDSG §31 canlı aynı); gerekçesiz ve kural olarak ücretsiz, yalnız ilk kopya ücretsiz (BfDI).

### hesap-degistirme-yardimi-kontenwechselhilfe: küçük
- Süreler (iki iş günü, beş iş günü, beş iş günü), ücretsiz kalemler, istisnalar (yabancı banka, farklı para birimi) BaFin sayfasıyla birebir doğru.
- Bulgu 1 (küçük): Summary "ödeme hesabı sunan tüm kuruluşlar" diyor; kaynak "tüketicilere" ödeme hesabı sunan kuruluşlar diyor.
  - Kanıt: https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/kontenwechsel/kontenwechsel.html "Alle Zahlungsdienstleister, die Verbraucherinnen und Verbrauchern Zahlungskonten anbieten, sind zur Unterstützung verpflichtet."
  - Düzeltme: "tüketicilere ödeme hesabı sunan tüm kuruluşlar".
- Bulgu 2 (küçük): Son step özne karışık ve yanlış okunur: "Bir banka yükümlülüğünü ihlal ederse zararını mahkemede talep edebilir, BaFin'e şikâyet edebilir ya da ... başvurabilirsin". Kaynak: bankalar müteselsil sorumlu, zararı mahkemede istersin.
  - Düzeltme: "Bir banka yükümlülüğünü ihlal ederse zararını mahkemede isteyebilir, BaFin'e şikâyet edebilir ya da tüketici tahkim kuruluşuna başvurabilirsin."
- Bulgu 3 (küçük): Kaynakta olan iki önemli bilgi kartta yok: eski bankanın kalan bakiyeyi yeni hesaba aktarıp hesabı kapatması; yeni bankanın gelen havale ve Lastschrift bilgilerini son 13 ay için istemesi.
  - Kanıt: aynı URL "Ab dem von Ihnen festgelegten Zeitpunkt darf er keine Zahlungen (Daueraufträge/Lastschriften) mehr ausführen, muss den Restsaldo auf das neue Konto überweisen und das alte Konto schließen."
  - Düzeltme: summary ya da steps'e bakiyenin aktarıldığı cümleyi ekle.

---

## Claims notu
Okunan claims'te (gelir-vergisi, vergi-sınıfı, kdv, kilise, maaş, emeklilik) alıntılar iddiayı kanıtlıyor; iki tutarsızlık: gelir-vergisi claims "katsayısı" yazıyor ama kart "%" yazıyor; vergi-sınıfı claims'te "III için başvuru yapılmamışsa" koşulu var, kartın steps'inde düşmüş. Kilise kartında "oran/çıkış eyalete göre" için hiç claim yok. KDV kartında yalnız 3 claim var (kural ≥3, sınırda). Diğer 6 kartın claims'i okunmadı.
