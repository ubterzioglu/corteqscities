# NRW bölge paketi: bağımsız denetim B (para, ev, resmi), 02.11.2026

**Özet:** 6 kart denetlendi. ciddi: 1, orta: 7, küçük: 10.

**Yöntem:** Her kartın summary/steps/documents/timing/cost/note cümleleri kartın kendi kaynak metniyle (kaynak_dizini.jsonl, text_file) karşılaştırıldı; kart başına en az 3 claim'in quote'u anlam açısından okundu (hepsi kaynakta birebir geçiyor ve iddiayı kanıtlıyor; claim düzeyinde sorun bulunmadı). Ulusal kart `resmi-yaziya-itiraz-widerspruch-sure-ve-sonraki-yol` (Yanıtlar.ulusal.jsonl satır 27) ile NRW resmi kartı karşılaştırıldı. gaps.md dosyaları okunmadı, kart dosyalarına dokunulmadı.

**Canlı açılan sayfalar (02.11.2026):**
- recht.nrw.de Mieterschutzverordnung (07.11.2025 sürümü "aktuelle Seite", 2 sürüm var, §3 Abs. 2 ve §1 Abs. 2 aynı)
- mhkbd.nrw/themenportal/wohnberechtigungsschein (tablo aynı: 23.540 / 28.350 / 38.011 / 51.777; sayfada yıl yok)
- recht.nrw.de/mbnrw/2025-88 (EEWo NRW, "ab dem 1. Januar 2025", yenilenme notu yok)
- justiz.nrw Kirchenaustritt (30 EUR, 14/12 yaş, aynı)
- finanzamt.nrw.de/steuer-abc (Kirchensteuer %9, aynı)
- finanzamt.nrw.de Grunderwerbsteuer sayfası (%6,5, 1.1.2015, bir ay, Stundung yok, aynı)
- recht.nrw.de JustG NRW (güncel sürüm 24.12.2024, sonrası yok; §110 metni canlıda kesildi, indirilmiş kopya aynı sürüm)
- recht.nrw.de BauO NRW 2018 (güncel sürüm 01.09.2026; §47 metni canlıda kesildi, indirilmiş kopya aynı sürüm ve §47 Abs. 2 kartla örtüşüyor)

**Bakılamayanlar:** 2026 için yeni WBS gelir sınırı/Runderlass olup olmadığı (canlıda görünmedi ama yokluğu kanıtlanamadı); WFNG NRW §18 yasa metni (Türk vatandaşı için "außereuropäisch" yorumu); BGB §556d/§556f/§558, VwGO §74, SGG §78, AO §347 (karta eklenmesi önerilen federal kaynaklar); JustG §110 ve BauO §47 canlı tam metin (WebFetch kesti).

---

### nrw-kilise-vergisi-orani-ve-kiliseden-cikis: orta
- Bulgu 1 (orta): Kart "kilise vergisi gelir vergisinin yüzde 9'udur ve Finanzamt tarafından toplanır" diyor ama bunun kimi bağladığını söylemiyor. Kaynakta vergi "Religionsgemeinschaften bei ihren Mitgliedern" (üyelerden) alınır ve Finanzamt tahsilatı evangelische, römisch-katholische ve jüdisch-israelitische kilise için yazılıdır. Türk okuyucu (çoğunlukla üye olmayan) kendisinin %9 ödediğini sanabilir; "Finanzamt tarafından toplanır" ifadesi de tüm dinî topluluklara genelleniyor.
- Kanıt: https://www.finanzamt.nrw.de/steuer-abc "Die Kirchensteuer wird von verschiedenen Religionsgemeinschaften bei ihren Mitgliedern erhoben." ve "Die Kirchensteuern für beispielsweise die evangelische, römisch katholische und jüdisch israelitische Kirche werden in Nordrhein-Westfalen durch die Finanzämter eingezogen"
- Düzeltme: Özet ve subtitle'a "yalnız kilisenin (ya da ilgili dinî topluluğun) üyesi olanlar öder; evangelische, katolik ve Yahudi cemaatlerinin vergisini NRW'de Finanzamt toplar" ekle; "(Finanzamt NRW'ye göre)" parantezini sil.
- Bulgu 2 (küçük): Adım 5 "Çıkıştan önce ödediğin kilise vergisini ... Sonderausgabe" diyor; kaynak "çıkıştan önce" demiyor, "im Jahr gezahlte Kirchensteuer" diyor. Düzeltme: "Yıl içinde ödediğin kilise vergisini ..." yaz.
- Bulgu 3 (küçük): note'ta "geschäftsunfähig" için "iş göremez" kullanılmış; hukuki karşılığı fiil ehliyeti olmayan kişidir. Ayrıca kaynaktaki "yasal temsilcinin iradesine rağmen de kendisi bildirebilir" cümlesi yok. Düzeltme: "fiil ehliyeti olmayan (geschäftsunfähig)" yaz.
- Doğru bulunanlar: %9, 30 EUR, Amtsgericht, 14/12 yaş, geçerlilik anı, Personalausweis/Meldebescheinigung (canlı teyitli). valid_until null kabul.

### nrw-emlak-alim-vergisi-grunderwerbsteuer-orani-ve-odeme: orta
- Bulgu 1 (orta): Adım 2 ve cost "Matrah kural olarak noter sözleşmesindeki satış bedelidir" diyor. Kaynak matrahı "unter anderem" ile sayıyor: satış bedeli, üstlenilen borçlar (ör. kalan ipotek) ve arsa+bina tek sözleşme (einheitliches Vertragswerk) ise bina yapım bedeli. Yeni bina alanlar için vergiyi eksik hesaplatır. (Notarkosten matraha girmez kısmı doğru.)
- Kanıt: https://www.finanzamt.nrw.de/steuerinfos/privatpersonen/haus-und-grund/grunderwerbsteuer-wissenswertes-beim-grundstuecks-oder "die übernommenen Verbindlichkeiten (zum Beispiel Hypotheken in noch offener Höhe, Rentenschuld)" ve "die Gebäudeerrichtungskosten, sofern Gegenstand eines Erwerbsvorgangs das Grundstück im bebauten (noch zu bebauendem) Zustand ist"
- Düzeltme: "Matrah satış bedeli artı üstlenilen borçlardır; arsa ve bina tek sözleşmeyle alınıyorsa bina yapım bedeli de matraha girer; Notarkosten ve miras alınan mobilya/mutfak gibi eşyanın bedeli girmez" yaz.
- Bulgu 2 (küçük): Vergi muafiyetleri (miras, eşler arası, doğrudan akraba, 2.500 Euro'ya kadar) kartta yok. Kart yalnız "satın alma" için olduğundan hata değil; başlığı "satın almada" diye daraltmak yeterli.
- Doğru bulunanlar: %6,5; 1 Ocak 2015; noter sözleşmesiyle doğuş; bir ay; Stundung yok; Unbedenklichkeitsbescheinigung; Gesamtschuldner; evli çiftler ayrı Steuerbescheid. Canlıda 2026'da oran değişikliği görünmedi. Yasa sürümü 01.01.2015 güncel.

### nrw-kira-tavani-ve-kira-artis-siniri-mieterschutzverordnung: orta
- Bulgu 1 (orta): Basın bildirisi ile yönetmelik çelişiyor ve kart bunu sessizce çözüyor. Bildiri (29.01.2025) Mietpreisbremse'nin geçerliliğinin "31 Aralık 2025" ile sınırlanacağını söylüyor; yönetmelik 28.10.2025 değişikliğiyle (7.11.2025) §1 Abs.1 için 31.12.2029'a uzatıldı. Kart bitiş tarihlerini doğru olarak yönetmelikten alıyor (31.12.2029 / 28.02.2030), ama %10 ve %15 için dayanak olarak yalnız bu eskimiş bildiriyi gösteriyor ve "Bilgi al" bağlantısı 2 okuyucuyu "31. Dezember 2025" yazan sayfaya götürüyor. %10 ve %15 yönetmelik metninde yok; BGB §556d ve §558 Abs. 3'ten geliyor.
- Kanıt: https://www.land.nrw/pressemitteilung/ministerin-scharrenbach-aus-18-werden-57-nordrhein-westfalen-weitet "ist die Geltungsdauer für die zulässige Miethöhe bei Mietbeginn auf den 31. Dezember 2025 zu begrenzen" ; https://recht.nrw.de/lrgv/rechtsverordnung/07112025-mieterschutzverordnung-nrw-mietschvo-nrw/ "(2) § 1 Absatz 1 tritt mit Ablauf des 31. Dezember 2029 außer Kraft."
- Düzeltme: %10 ve %15 için BGB §556d Abs. 1 ve §558 Abs. 3 (gesetze-im-internet.de) kaynağı ekle ya da bildiri bağlantısını çıkar; bildiriye yapılan atfı "29 Ocak 2025 bildirisine göre" yerine yönetmelik/BGB'ye bağla.
- Bulgu 2 (orta): Adım 2 "kiranın yerel emsal kiranın yüzde 10 üzerini aşmamasına dikkat et" kesin konuşuyor; Mietpreisbremse'nin yasadaki istisnaları (ör. 1 Ekim 2014'ten sonra ilk kez kiraya verilen yeni binalar, kapsamlı modernizasyon, önceki kiracıya uygulanan daha yüksek kira) kaynakta yok ve kartta "genel kural" çerçevesi verilmemiş.
- Kanıt: kaynakların (yönetmelik, bildiri) istisna içermemesi; istisnalar BGB §556e ve §556f.
- Düzeltme: BGB §556e/§556f kaynağı ekleyip "kural olarak" ve istisnaları yaz; kaynak eklenmeyecekse "kural olarak" ifadesiyle sınırla.
- Bulgu 3 (küçük): Adım 1 "yönetmelik ekindeki belediye listesine bak" havale cümlesidir (YAZAR_KURALLARI 3). Şehir listesi karta yazılamaz (doğru) ama havale de yazılmaz. Düzeltme: adımı sil; özetteki "yalnız yönetmelik ekinde sayılan belediyelerde" cümlesi yeter.
- Şehir adı/listesi: karta yazılmamış (iyi). 57 belediye sayısı da yazılmamış.
- Doğru bulunanlar: 1 Mart 2025, 31.12.2029, 28.02.2030, 8 yıl, §2 geçiş (9 Haziran 2020, 5 yıldan 8 yıla uzamaz), %10/%15 ve 3 yıl bildiride birebir. valid_until 2029-12-31 doğru (en erken bitiş). Canlıda 07.11.2025 sürümü güncel.

### nrw-wbs-gelir-siniri-2025-ve-basvuru: orta
- Bulgu 1 (orta): Başlık, subtitle ve özet "gelir sınırı 23.540 Euro / 28.350 Euro" diyor ama bunun yıllık olduğunu ve karşılaştırmanın brüt maaşla değil, ilgili kesintiler (ör. vergi ve sigorta primi için pauschal indirim) düşüldükten sonraki "maßgebendes Einkommen" ile yapıldığını söylemiyor. Okuyucu bunu aylık ya da brüt maaş sınırı sanabilir; tek ipucu note'taki 38.011 brüt örneği.
- Kanıt: https://recht.nrw.de/mbnrw/2025-88/ "Die für die Wohn- und Förderberechtigung maßgebliche Einkommensgrenze beträgt ab dem 1. Januar 2025" ; https://www.mhkbd.nrw/themenportal/wohnberechtigungsschein "Mögliches Einkommen im Jahr (brutto) in Euro"
- Düzeltme: Subtitle ve özetteki tüm tutarlara "yıllık" ekle (23.540 Euro/yıl); özete "bu sınır brüt maaş değil, kesintiler sonrası yıllık hane geliri içindir; brüt karşılık örneği aşağıda" ekle.
- Bulgu 2 (orta): Türk okuyucu: "Avrupa dışı bir ülkeden geliyorsan en az bir yıl kalma hakkın olmalı." Kaynak "außereuropäisches Ausland" diyor; Türkiye'nin bu gruba girip girmediği belirsiz ve kart bunu tahmine bırakıyor. Kaynak AB/AEA ayrımı yapmıyor; yorum eklenmemeli.
- Kanıt: https://www.mhkbd.nrw/themenportal/wohnberechtigungsschein "Kommen Sie aus dem außereuropäischen Ausland, müssen Sie sich mindestens ein Jahr in der Bundesrepublik Deutschland und damit in Nordrhein-Westfalen aufhalten dürfen."
- Düzeltme: WFNG NRW (§18) metninden Türk vatandaşı için hangi grup olduğunu doğrula; kaynak bulunmazsa cümleyi "Aufenthaltstitel'in Almanya'da en az bir yıl kalma hakkı vermesi gerekir (AB dışı geliş)" yerine kaynağın dediği biçimde bırak ve Türk okuyucu için uyarıyı kaldır ya da gaps'e taşı.
- Bulgu 3 (küçük): "Aufenthaltsbescheinigung" için "oturum belgesi" çevirisi; DE_YAZAR_NOTLARI'na göre oturum belgesi Aufenthaltstitel'dir. Düzeltme: "ikamet belgesi (Aufenthaltsbescheinigung)" yaz.
- Bulgu 4 (küçük): Yıllık güncellenen sınır ve kart Kasım 2026'da 2025 tutarını veriyor. Canlıda daha yeni sınır görünmedi (sayfalarda yıl yok; MBl.NRW 2026'da yeni Runderlass olup olmadığını kontrol edemedim). Editör recht.nrw.de/mbnrw altında "Einkommensgrenzen 2026"ya bakmalı.
- Doğru bulunanlar: 23.540 / 28.350 / +6.530 / +860 (ab 1.1.2025; Runderlass 2.9.2025, yürürlük 1.10.2025), 38.011 / 51.777, başvuru yeri, belgeler, Zweitwohnung, Jobcenter notu, ücret cümlesi.

### nrw-duman-dedektoru-rauchwarnmelder-odalar-ve-sorumlu: küçük
- BauO NRW §47 Abs. 2 (01.09.2026 sürümü, güncel) kartla üç cümlede birebir örtüşüyor; kart metni aşmıyor.
- Bulgu 1 (küçük): "oturma odalarından (Aufenthaltsräume)" çevirisi dar. Aufenthaltsraum = "nicht nur vorübergehenden Aufenthalt" için odalar (§2 Abs. 7), yatak odası da dahil. Düzeltme: "ikamet edilen odalardan (Aufenthaltsräume) kaçış yollarına giden koridorlar" yaz.
- Kanıt: https://recht.nrw.de/lrgv/gesetz/01092026-landesbauordnung-2018-bauo-nrw-2018/ "Aufenthaltsräume sind Räume, die zum nicht nur vorübergehenden Aufenthalt von Menschen bestimmt oder geeignet sind."
- Bulgu 2 (küçük): "evi doğrudan elinde bulunduran kişi" (unmittelbare besitzhabende Person) Türk okuyucu için anlaşılmaz; kaynak "kiracı" demiyor, bu yüzden yorum eklenmemeli. Düzeltme: terimi parantezle bırak, kaynak bulunursa (BauO yorumu) "kiralık evde genellikle oturan kişi" ekle, bulunmazsa şimdiki hâli yeterli.
- Doğru bulunanlar: odalar, "frühzeitig erkannt und gemeldet", malik üstlenirse malike geçer. valid_until yok (kaynakta bitiş yok): kabul.

### nrw-resmi-islemde-widerspruch-yok-dogrudan-dava: ciddi
- Bulgu 1 (ciddi): Kart "NRW'de resmî bir işleme karşı önce itiraz gerekir mi?" sorusuna "Hayır" diyor ama kuralın yalnız idare mahkemesine (VwGO, Anfechtungs-/Verpflichtungsklage) giden işlemler için geçerli olduğunu söylemiyor. JustG §110 yalnız VwGO §68'den sapar. Jobcenter/Bürgergeld, emeklilik/sağlık sigortası, Agentur für Arbeit işlemlerinde sosyal mahkeme yolu (önce Widerspruch zorunlu, SGG §78) ve Finanzamt işlemlerinde mali mahkeme yolu (önce Einspruch zorunlu, AO §347) NRW'de de geçerlidir. Okuyucu süreyi kaçırıp hak kaybedebilir. Aynı paketin ulusal kartı bu sınırı yazıyor; NRW kartında yok.
- Kanıt: https://www.justiz.nrw/BS/lebenslagen/verwaltungsrecht/klageverfahren/vorverfahren_07 "Vor Erhebung einer Anfechtungs- oder Verpflichtungsklage muss die ergangene Behördenentscheidung grundsätzlich in einem behördlichen Vorverfahren überprüft werden (§ 68 VwGO)." Ulusal kart: "Anlatılan yol idare mahkemesinin baktığı işlemler içindir; VwGO, uyuşmazlığı federal yasayla açıkça başka bir mahkemeye verilmiş alanlar için geçerli değildir."
- Düzeltme: Başlıkta ve özetin ilk cümlesinde kapsamı daralt ("İdare mahkemesine götürülecek idari işlemlerde ..."), özete ulusal kartın aynı kaynakla yazdığı "federal yasanın başka mahkemeye verdiği alanlar (ör. sosyal haklar, vergi) için bu kural geçerli değildir" cümlesini ekle (kaynak 088/093 ya da SGG §78 / AO §347 kaynağı ekle).
- Bulgu 2 (orta): Süre yok. Adım 1 "itiraz süresi orada yazılıdır" ile Rechtsbehelfsbelehrung'a havale ediyor; kaynak 022'de süre var ("Monatsfrist ab Bekanntgabe"). Adım 2 "doğrudan iptal davasını aç" diyor ama dava süresi (bir ay, VwGO §74; kaynak 022/023'te yok) hiç yazılmıyor. Düzeltme: Widerspruch için "bildirimden sonra bir ay" yaz (kaynak 022 satır 6); dava süresini ulusal kartın kaynağıyla (VwGO §74) ekle.
- Kanıt: https://www.justiz.nrw/BS/lebenslagen/verwaltungsrecht/klageverfahren/vorverfahren_07 "es gilt eine Monatsfrist ab Bekanntgabe des Bescheids (§ 69 VwGO und § 70 VwGO)."
- Bulgu 3 (küçük): §110 Abs. 2/3 listesi eksiksiz ve doğru (12 madde, Satz 2 üst makam istisnası, Satz 3 yan hükümler, Abs. 3'ün 9 maddesi, Abs. 4; hepsi indirilmiş metinle karşılaştırıldı). İki okunabilirlik sorunu: (a) Abs. 3 Satz 2 maddeleri yalnız üçüncü kişi istisnasına bağlı; kart "yine geçerlidir" diyor ama "üçüncü kişi olsan bile" demeli. (b) Adım 2 "aşağıdaki notta sayılan alanlardan" diye alan sıralamasına havale ediyor. Düzeltme: Abs. 3 cümlesini netleştir; havaleyi kaldır, listenin başına kısaca "okul, belediye harçları, Wohngeld, WBS (WFNG §18), yayın ücreti (WDR/Beitragsservice), çocuk-gençlik yardımı" gibi okuyucuya tanıdık alanları özete al.
- Bulgu 4 (küçük): "Rechtsbehelfsbelehrung" için "yasal başvuru bilgisi"; ulusal kart "itiraz yolu bilgisi" diyor. Düzeltme: iki kartta aynı terimi kullan.
- Not: Abs. 2 Nr. 12 (WFNG §9 Abs. 1 Nr. 4, §§13-15, §18) WBS kararlarını kapsıyor (kaynak 019: "Erteilung von Wohnberechtigungsscheinen nach § 18 WFNG NRW"); kartta WBS'nin açıkça anılması okuyucuya yarar.
- Doğru bulunanlar: §110 Abs. 1 (24.12.2024 sürümü, canlıda güncel), Verpflichtungsklage, Feststellungs-/Leistungsklage, Beamten istisnası (kaynak 022), kabul edilmeme ve masraf cümlesi.
