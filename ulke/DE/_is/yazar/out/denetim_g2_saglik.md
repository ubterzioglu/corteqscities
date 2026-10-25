# Almanya ulusal paketi: "saglik" konusu bağımsız denetim (g2)

Tarih: 25.10.2026. Denetçi yazarın gaps.md dosyasını okumadı. Kart dosyalarına dokunulmadı.

## Özet
- Kart sayısı: 9 (order 601–609). Bulgu sayısı: ciddi 1, orta 11, küçük 12 (sayım bulgu başınadır, kart başına değil).
- Kart başına en yüksek derece: 601 ciddi; 602, 604, 606, 607, 608, 609 orta; 603, 605 yalnız küçük.
- Yöntem: Her kartın summary/steps/documents/timing/cost/note/subtitle cümleleri kartın kendi source_ids kaynaklarının `text_file` metniyle satır satır karşılaştırıldı. 154 claim'in tamamı okundu (kart başına en az 3 değil, hepsi): alıntı iddiayı kanıtlıyor mu diye bakıldı. Bağlantılar ve valid_until.json kontrol edildi. Yasaklı sözcük taraması (yaklaşık, teyit, resmî sayfa, şehir/eyalet adı, havale) yapıldı: ihlal yok.
- Canlı açılan sayfalar (Python urllib, 25.10.2026; indirilen kopyayla cümle düzeyinde karşılaştırıldı, sayı/oran/tarih farkı YOK): bundesgesundheitsministerium.de/beitraege (Stand 3. September 2026), bundesgesundheitsministerium.de/…/die-pflegeversicherung/finanzierung (Stand 14. September 2026), …/pflegebeduerftig-was-nun, …/pflege-zu-hause (Stand 14. September 2026), 116117.de/de/aerztlicher-bereitschaftsdienst.php, gesetze-im-internet.de: sgb_5 §5, §6, §10, §24i, §61, §62, §75; ifsg §20, §33; vvg_2008 §193; muschg_2018 §3. Yeni yürürlük ya da değişiklik bulunmadı.
- Doğrulananlar (sorun yok): GKV genel oran %14,6, indirimli %14,0, ortalama ek prim %2,9 (2026), BBG aylık 5.812,50 / yıllık 69.750 (BMG canlı: "Stand: 2026"); PV %3,6, çocuksuz %4,2 (BMG: "Seit dem 1. Januar 2025"), 0,25 puan indirim ikinci–beşinci çocuk; Zuzahlung %10, en az 5, en çok 10 Euro; Belastungsgrenze %2 / %1; 25 iş günü, 70 Euro; Pflegegeld 347/599/800/990; ortak yıllık tutar 3.539 (2026); MuSchG 6+8 hafta, 12 hafta istisnaları; IfSG §20 31.12.1970 sonrası doğanlar, 1 ve 2 aşı; ApBetrO §23 ilanı; 116117 önek yok, ücretsiz, 24/7.
- Çapraz kontrol para 308 ↔ saglik 603: Çelişki YOK. İkisi de GKV %14,6 + ortalama ek prim %2,9, BBG 5.812,50, yarı yarıya paylaşım, Sonderkündigungsrecht, aile sigortasında prim yok diyor; değerler birebir aynı. Tek fark: 308 bordro kalemlerini sayarken bakım sigortasını (işçi payı 1,8 / çocuksuz 2,4) hiç anmıyor; bordroda kesilen bir kalem eksik kalıyor (308 için orta bulgu, aşağıda "Çapraz kontrol" bölümünde).
- Bakılmayanlar: kapalı siteler (bmi.bund.de, make-it-in-germany.com, auswaertiges-amt.de) denenmedi; GKV-Spitzenverband kasa-bazlı ek prim listesi açılmadı; Türkiye–Almanya sosyal güvenlik anlaşması konusunda kaynak aranmadı (kartlar da anmıyor); ApBetrO için eyalet düzeyi nöbet düzenlemeleri bakılmadı.
- Türk okuyucu: Hiçbir kartta Türkiye'ye ya da Türk vatandaşına dair kaynaksız iddia yok. Eksik olan: 601'de SGB V §5 Abs.1 Nr.13 / Abs.11 (AB dışı ülke vatandaşları için oturum izni koşulu); 602'de ikametgâh koşulunun açık yazılmaması.

---

### saglik-sigortasi-zorunlulugu-kamu-ozel: ciddi
- Bulgu 1 (ciddi): GKV/PKV ayrımı kapsamı yanlış çerçevelenmiş. Adım 1 ("ücretli çalışansan ya da işsizlik parası alıyorsan kamu sigortasına (GKV) zorunlu girersin") ve claim 10 ("Ücretli çalışanlar kamu sigortasına zorunlu girer") dar kuralı bütün ücretli çalışanlara genelliyor. Yıllık geliri Jahresarbeitsentgeltgrenze'yi aşan çalışan zorunlu sigortalı DEĞİLDİR (SGB V §6), hauptberuflich selbständig kişi §5 Abs.5 gereği §5 Abs.1 Nr.1 kapsamında değildir, memurlar da dışındadır. Kartın başlığındaki asıl soru (kamu mu, özel mi, kim hangisini seçer) cevapsız kalıyor: "Kamu sigortasının dışında kalan kişi özel sigorta yaptırır" cümlesi kimin dışarıda kaldığını söylemeden döngüsel. Yüksek maaşlı bir okuyucu "zorunluyum" sanır. Kartta JAEG hiç geçmiyor (rakamsız olması doğru, ama çerçeve eksik).
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__5.html "Nach Absatz 1 Nr. 1 oder 5 bis 12 ist nicht versicherungspflichtig, wer hauptberuflich selbständig erwerbstätig ist." ; https://www.gesetze-im-internet.de/sgb_5/__6.html "Arbeiter und Angestellte, deren regelmäßiges Jahresarbeitsentgelt die Jahresarbeitsentgeltgrenze nach den Absätzen 6 oder 7 übersteigt" (versicherungsfrei).
- Düzeltme: Adım 1 ve summary'de "zorunlu girersin" yerine "kural olarak zorunlu girersin; yıllık geliri yasal sınırı (Jahresarbeitsentgeltgrenze, her yıl değişir) aşan ücretli çalışan ve hauptberuflich selbständig çalışan zorunlu sigortalı değildir, bunlar özel sigorta (PKV) ya da gönüllü kamu sigortası seçer" yaz; rakam verme. Bu cümle için SGB V §6 kaynağı gerekir (kaynak sayısı 2'yi aşıyorsa kartı bölün ya da 139/140'tan birini çıkarmadan 3. kaynağa izin verin; editör karar versin). §5 Abs.5 cümlesi mevcut 140'tan yazılabilir.

- Bulgu 2 (orta): "Almanya'da ikametgâhı olan herkes" (subtitle/summary) deyip muafiyet olarak yalnız GKV'yi yazıyor; VVG §193 Abs.3 Satz 2'deki diğer muafiyetler (serbest Heilfürsorge/Beihilfe hakkı olanlar, Asylbewerberleistungsgesetz hakkı olanlar, SGB XII/IX belirli yardım alanlar) eksik. Kural 8: kaynağın kapsamıyla sınırla.
- Kanıt: https://www.gesetze-im-internet.de/vvg_2008/__193.html "Die Pflicht nach Satz 1 besteht nicht für Personen, die … Anspruch auf freie Heilfürsorge haben, beihilfeberechtigt sind … oder Anspruch auf Leistungen nach dem Asylbewerberleistungsgesetz haben"
- Düzeltme: Summary'ye tek cümle: "Serbest sağlık hizmeti (Heilfürsorge) ya da Beihilfe hakkı olanlar ve Asylbewerberleistungsgesetz hakkı olanlar bu özel sigorta yükümlülüğünden muaftır." (yalnız kaynakta olduğu kadar).

- Bulgu 3 (orta): Türk okuyucu için kritik kural kartta yok. SGB V §5 Abs.1 Nr.13 (başka sigortası olmayan, daha önce kamu sigortalısı olmuş ya da hiç sigortalı olmamış kişiler zorunlu GKV) ve Abs.11: AB/AEA/İsviçre dışı ülke vatandaşı, geçim güvencesi şartı aranmadan verilmiş Niederlassungserlaubnis ya da 12 aydan uzun süreli Aufenthaltserlaubnis sahibiyse Nr.13 kapsamındadır. Kart 140'ı kaynak gösteriyor ama bu hükmü kullanmıyor; "kamu sigortasının dışında kalan özel yaptırır" cümlesi bu gruba yanlış yön verebilir.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__5.html "Ausländer, die nicht Angehörige eines Mitgliedstaates der Europäischen Union, … sind, werden von der Versicherungspflicht nach Absatz 1 Nr. 13 erfasst, wenn sie eine Niederlassungserlaubnis oder eine Aufenthaltserlaubnis mit einer Befristung auf mehr als zwölf Monate nach dem Aufenthaltsgesetz besitzen und für die Erteilung dieser Aufenthaltstitel keine Verpflichtung zur Sicherung des Lebensunterhalts nach § 5 Abs. 1 Nr. 1 des Aufenthaltsgesetzes besteht."
- Düzeltme: Note'a ya da steps'e: "AB/AEA/İsviçre dışı vatandaşlar için: geçim güvencesi şartı olmadan verilmiş yerleşme izni ya da 12 aydan uzun süreli oturum izni olan ve başka sağlık güvencesi olmayanlar da kamu sigortasına zorunlu girer (SGB V §5 Abs.1 Nr.13, Abs.11)." Kaynak dışı ekleme yapma (Türkiye anlaşması vb.).

- Bulgu 4 (küçük): Öğrenci notu: "en çok 30 yaşına kadar" doğru ama aynı hükümdeki istisna (30 yaşından sonra eğitimin türü, ailevi/kişisel nedenler yaş aşımını haklı kılıyorsa devam) ve §5 Abs.7 (zaten başka zorunlu sigortası/aile sigortası olan öğrenci hariç) yok; not tek yönlü okunabilir.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__5.html "Studenten nach Vollendung des dreißigsten Lebensjahres sind nur versicherungspflichtig, wenn die Art der Ausbildung oder familiäre sowie persönliche Gründe … die Überschreitung der Altersgrenze rechtfertigen"
- Düzeltme: Note'a: "30 yaşından sonra yalnız eğitimin türü ya da ailevi/kişisel nedenler yaş aşımını haklı kılıyorsa zorunlu sigortalıdır; başka zorunlu sigortası ya da aile sigortası olan öğrenci bu kapsama girmez." (ya da notu sadeleştir).

Doğrulananlar: bir aylık süre, prim zammı (bir aylık prim / altıncı aydan sonra altıda biri / en az beş yıl / bir defalık), Selbstbehalt 5.000 Euro, en az ayakta ve yatarak tedavi masrafı: kaynakla birebir.

---

### aile-sigortasi-es-cocuk-prim-ucreti: orta
- Bulgu 1 (orta): Adım 2 "bu iki koşul eş için aranır" yanlış kapsam: hauptberuflich selbständig olmama ve gelirin Bezugsgröße'nin 1/7'sini aşmaması (Nr.4 ve Nr.5) eşle birlikte çocuklar ve tüm aile üyeleri için aranır; yalnız eşe özgü değil. Ayrıca summary ve adımlar Nr.2 ve Nr.3'ü hiç yazmıyor: aile üyesi kendisi zorunlu sigortalıysa (örn. çalışan eş) ya da gönüllü üyeyse ya da sigortadan muafsa aile sigortasında olmaz. Okuyucu "eşim çalışıyor ama geliri düşük" durumunda yanlış sonuca varabilir.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "wenn diese Familienangehörigen … 2. nicht nach § 5 Absatz 1 Nummer 1 bis 8, 11 bis 12 oder nicht freiwillig versichert sind, 3. nicht versicherungsfrei … sind, 4. nicht hauptberuflich selbständig erwerbstätig sind und 5. kein Gesamteinkommen haben, das regelmäßig im Monat ein Siebtel der monatlichen Bezugsgröße … überschreitet."
- Düzeltme: Adım 2'deki "bu iki koşul eş için aranır" cümlesini sil; "gelir ve serbest çalışma koşulları eş ve çocuklar dahil tüm aile üyeleri için aranır" yaz; summary'ye "aile üyesinin kendisi zorunlu sigortalı (örn. ücretli çalışan) ya da gönüllü üye olmaması" koşulunu ekle.

- Bulgu 2 (orta): Türk okuyucu: koşul 1 (ikametgâh/olağan oturma yeri Almanya'da) yazılmış ama sonucu açık değil: eş ya da çocuk Türkiye'de yaşıyorsa aile sigortası kapsamı yok. Bu en sık düşülen yanlış beklentidir; kartın yazdığı koşuldan çıkan sonuç bir cümleyle söylenmeli (kaynak 141 Nr.1 bunu destekler; Türkiye anlaşması YAZMA).
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "ihren Wohnsitz oder gewöhnlichen Aufenthalt im Inland haben"
- Düzeltme: Summary ya da note'a: "Eşin ya da çocuğun Almanya'da ikametgâhı ya da olağan oturma yeri yoksa aile sigortası kapsamı yoktur."

- Bulgu 3 (küçük): Çeviri: note'taki "Düşük gelirli kısmi istihdamda (geringfügige Beschäftigung)" yanlış: geringfügige Beschäftigung kısmi (Teilzeit) istihdam değildir, "geringfügige" = marjinal/düşük gelirli istihdam (Minijob). "Geringfügigkeitsgrenze" açıklanmamış ve çevrilmemiş (rakam vermemek doğru; en azından "geringfügigkeitsgrenze (geringfügig çalışma gelir sınırı)" denmeli).
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "Für Familienangehörige, die eine geringfügige Beschäftigung nach § 8 Absatz 1 Nummer 1 des Vierten Buches … ausüben, ist ein regelmäßiges monatliches Gesamteinkommen … bis zur Geringfügigkeitsgrenze zulässig."
- Düzeltme: "kısmi istihdam" yerine "geringfügige (düşük gelirli, Minijob türü) çalışma"; Geringfügigkeitsgrenze'yi kısaca tanımla.

JAEG notu (kullanıcının sorusu): Bu kartta Jahresarbeitsentgeltgrenze yalnız §10 Abs.3'ün (eş üye değilse çocuk) bağlamında, rakamsız ve doğru çerçevede geçiyor; BMG 142 canlı sayfasındaki 77.400 Euro (2026) yazılmamış, bu uygun. "yıllık sigorta zorunluluğu gelir sınırı" çevirisi anlaşılır.

---

### saglik-ve-bakim-sigortasi-primi-2026-oranlari: küçük
- Bulgu 1 (küçük): "Bürgergeld alıyorsan çocuksuzluk zammı ödemezsin" kaynak 025'teki sözcüğü aynen kullanıyor, ama 25.10.2026'da güncel SGB V §5 canlı metninde bu yardımın adı "Grundsicherungsgeld" (§5 Abs.1 Nr.2a). BMG 142 sayfası da aynı sayfada iki adı birlikte kullanıyor. Yazar kuralı: kaynaktaki adı yaz, tarihini belirt. Okuyucu eski adı arayabilir.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__5.html "Personen in der Zeit, für die sie Grundsicherungsgeld nach § 19 Absatz 1 Satz 1 des Zweiten Buches beziehen" ; https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/die-pflegeversicherung/finanzierung "Bezieherinnen und Bezieher von Bürgergeld nach dem SGB II"
- Düzeltme: "Bürgergeld (BMG sayfasındaki ad; yasada güncel adı Grundsicherungsgeld)" gibi tek parantez ya da "SGB II yardımı (Bürgergeld/Grundsicherungsgeld) alıyorsan".

Doğrulananlar (canlı, BMG): genel %14,6, indirimli %14,0 ("kein Krankengeldanspruch"), ek prim ortalaması %2,9 ("Für das Jahr 2026"), BBG 5.812,50 / 69.750 ("Stand: 2026"), PV %3,6 / %4,2 ("Seit dem 1. Januar 2025"), yarı yarıya paylaşım, çocuksuz zammını çalışanın tek başına ödemesi, 0,25 puan indirim, Sonderkündigungsrecht. Bir eyalette farklılık (Sachsen) adsız ve rakamsız yazılmış: kurala uygun. valid_until 2026-12-31 uygun. "BMG … 3 Eylül 2026 tarihlidir" kaynak tarihine uyuyor (iç denetim notu değil, kaynak tarihi).

---

### uzman-hekim-randevusu-116117-randevu-servisi: orta
- Bulgu 1 (orta): 116117 ile yasal Terminservicestelle özdeşleştirilmiş ama iki kaynağın hiçbiri bunu söylemiyor. §75 Abs.1a "bundesweit einheitliche Telefonnummer" diyor, 116117'yi anmıyor; 116117.de sayfası (kopya ve canlı) "Terminservicestelle" sözcüğünü geçirmiyor (canlıda yalnız menüde "Terminservice"), yalnız "Wir helfen Ihnen, einen Termin in einer ärztlichen oder psychotherapeutischen Praxis zu finden." diyor. Kart "116117'yi ara … Servis, sigortalıya bir hafta içinde randevu aktarmakla yükümlüdür" diyerek bir hafta/dört hafta garantisini 116117 aramasına bağlıyor. İki kaynağın birleşiminden çıkarım; kural 2/8'e göre kaynakla sınırlı değil.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__75.html "richten Terminservicestellen ein, die spätestens zum 1. Januar 2020 für 24 Stunden täglich an sieben Tagen in der Woche unter einer bundesweit einheitlichen Telefonnummer erreichbar sein müssen" ; https://www.116117.de/de/aerztlicher-bereitschaftsdienst.php "Wir helfen Ihnen, einen Termin in einer ärztlichen oder psychotherapeutischen Praxis zu finden."
- Düzeltme: İki ayrı cümle yaz: "116117 ekibi hekim ya da psikoterapi muayenehanesinde randevu bulmana yardım eder (116117.de)" ve "Yasa, hekim birliklerinden bir hafta içinde randevu aktaran Terminservicestelle'ler ister (SGB V §75)"; ikisinin aynı numara olduğunu yazacaksan bunu açıkça söyleyen üçüncü bir resmî kaynak (KBV/116117.de'nin Terminservice sayfası) ekle, yoksa başlıktan "116117 ve" bağını çıkar.

- Bulgu 2 (orta): Kapsam. (a) §75 hakları "Versicherte" (kamu sigortalısı) içindir; kart "sigortalı" diyor, özel sigortalı okuyucu bir hafta/dört hafta garantisini kendine uygular. (b) Satz 2–12, §28 Abs.2 (diş tedavisi) ve §29 (ortodonti) için geçerli değil: diş randevusunda bu garanti yok. (c) Psikoterapi görüşmesi için sevk gerekmez ve akut psikoterapide bekleme iki haftadır; kart "uzman randevusu için sevk gerekir" genel kuralını bu istisnasız veriyor.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__75.html "Die Sätze 2 bis 12 gelten nicht für Behandlungen nach § 28 Absatz 2 und § 29." ; "Die Wartezeit auf eine psychotherapeutische Akutbehandlung darf zwei Wochen nicht überschreiten."
- Düzeltme: Summary/note'a: "Bu garantiler kamu sigortalıları içindir; diş tedavisi ve ortodonti için geçerli değildir. Psikoterapi görüşmesinde sevk gerekmez."

- Bulgu 3 (küçük): "bir hafta içinde randevu aktarmak" ile "bekleme süresi dört hafta" iki ayrı süre; kart ikisini yan yana veriyor ama farkı söylemiyor, okuyucu "randevu bir hafta içinde olur" anlar. Kaynağa göre bir hafta aktarma (Vermittlung) süresi, dört hafta randevuya kadar bekleme üst sınırı. Adım 4 de "dört hafta içinde bulamazsa" diyor.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__75.html "Versicherten innerhalb einer Woche einen Behandlungstermin … zu vermitteln" ; "Die Wartezeit auf einen Behandlungstermin darf vier Wochen nicht überschreiten"
- Düzeltme: "Servis bir hafta içinde sana bir randevu bulur; bu randevu en geç dört hafta sonra (radyolojide üç hafta) olmalıdır."

Doğrulananlar: 116117 önek/ücret/24-7 (116117.de), sevk istisnaları göz/kadın doğum/akut, hastane teklifi, makul mesafe, Bagatell istisnası ve çocuk muayeneleri: kaynakla uyumlu.

---

### acil-durum-112-116117-hastane-acili-nobetci-eczane: küçük
- Bulgu 1 (küçük): `cost` alanı maliyet değil kapsam yazıyor ("Nöbetçi hekim hizmeti kamu ya da özel sigortalı herkesi kapsar"). Kaynak 143 "Egal ob gesetzlich oder privat versichert" diyor; bu tutar/ücret bilgisi değil. Maliyet olarak yalnız 116117 aramasının ücretsizliği doğru. Sigortasız kişi için kaynak sessiz: cümle kimin kapsandığını "sigortalı herkes" diye sınırlamış, kural 8'e uygun.
- Kanıt: https://www.116117.de/de/aerztlicher-bereitschaftsdienst.php "Egal ob gesetzlich oder privat versichert - der ärztliche Bereitschaftsdienst versorgt Sie schnell und unkompliziert."
- Düzeltme: Cümleyi `note`'a taşı (ya da `summary`); `cost`ta yalnız "116117 araması ücretsizdir" kalsın.

Doğrulananlar: 112 örnekleri, 116117'nin üç koşulu, Notaufnahme "vor allem für lebensbedrohliche Notfälle", Bereitschaftspraxis→Notaufnahme yönlendirmesi, ApBetrO §23: "Apotheken sind zur ständigen Dienstbereitschaft verpflichtet", muafiyet saatleri (gece, pazar, resmî tatil) ve "Hinweis auf die nächstgelegenen dienstbereiten Apotheken" ilanı kaynağa uygun. Eczane ilanı dışında nöbetçi eczane bulma yolu (çevrimiçi/telefon) yazılmamış: kaynak yok, doğru.

---

### recete-ilac-katilim-payi-yillik-muafiyet-siniri: orta
- Bulgu 1 (orta): Belastungsgrenze hesabı eksik anlatılmış. Adım 2 ve claim 88 "katılım payları ile brüt gelirleri birlikte hesaplanır" diyor; §62 Abs.2 aile üyeleri için brüt gelirden yasal düşüm yapılır (ilk aile üyesi için Bezugsgröße'nin %15'i, her ek üye için %10'u; çocuk başına vergi Freibetrag'ı), SGB XII/II yardımı alanlarda tüm Bedarfsgemeinschaft için yalnız Regelsatz/Regelbedarf esas alınır. Ayrıca birlikte hesap yalnız "gemeinsamer Haushalt"ta yaşayanlar için; kart yalnız çocuk için "aynı evde" diyor, eş için demiyor. Okuyucu %2'yi düz brüt toplam gelirden hesaplarsa sınırı yüksek bulur ve belgeyi geç ister.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__62.html "Hierbei sind die jährlichen Bruttoeinnahmen für den ersten in dem gemeinsamen Haushalt lebenden Angehörigen des Versicherten um 15 vom Hundert und für jeden weiteren … um 10 vom Hundert der jährlichen Bezugsgröße … zu vermindern."
- Düzeltme: Adım 2'ye: "Aile üyeleri ortak hanede yaşıyorsa gelirler toplanır, ancak yasa aile üyeleri için brüt gelirden belirli düşümler yapar (ilk aile üyesi için yıllık Bezugsgröße'nin %15'i, her ek üye için %10'u; çocuklar için vergi çocuk muafiyeti); SGB II/XII yardımı alanlarda sabit Regelsatz esas alınır." Rakam vermeyeceksen "düşüm yapılır" demek yeter; "brüt" tek başına bırakılmasın.

- Bulgu 2 (küçük): 2026 euro tutarı sorusu: Kartta Belastungsgrenze için euro tutarı YOK (doğru: yasa oran veriyor, %2/%1); 5/10 Euro kanunda sabit, yıl belirtmeye gerek yok. valid_until null uygun. Kayıt amaçlı: `cost`'taki "bedelin %10'u" kaynakta "Abgabepreis" (satış fiyatı); summary bunu doğru yazıyor. Kart "SGB V § 61" ve "§ 62" atıflarında doğru.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__61.html "10 vom Hundert des Abgabepreises, mindestens jedoch 5 Euro und höchstens 10 Euro; allerdings jeweils nicht mehr als die Kosten des Mittels"
- Düzeltme: Değişiklik gerekmez (kayıt amaçlı). Dilersen `summary`'ye "Satış fiyatı (Abgabepreis)" parantezi eklenebilir.

Doğrulananlar: %2 / %1, kronik hasta 1 Nisan 1972 / 2008 / strukturiertes Behandlungsprogramm, belge gelir içermez, Heilmittel %10 + 10 Euro/Verordnung, makbuz: kaynakla birebir.

---

### cocuk-asilari-kizamik-zorunlulugu-cocuk-muayeneleri: orta
- Bulgu 1 (orta): Kızamık yükümlülüğünün kapsadığı kurumlar kartta adlandırılmamış; yalnız "IfSG § 33 Nr. 1–3'te sayılan" deniyor. Okuyucu Nr.1–3'ün ne olduğunu bilemez (Kita/Kinderhort, Kindertagespflege, okullar ve diğer eğitim kurumları) ve soru zaten "çocuğum için zorunlu mu". §33 metni iki kaynakta da yok, yani cümle kart kaynaklarıyla doğrulanamaz; fiilen yasa numarasına havale. Summary'nin "bazı toplu bakım ve eğitim kurumları" ifadesi de belirsiz.
- Kanıt: https://www.gesetze-im-internet.de/ifsg/__33.html "1. Kindertageseinrichtungen und Kinderhorte, 2. die nach § 43 Absatz 1 des Achten Buches Sozialgesetzbuch erlaubnispflichtige Kindertagespflege, 3. Schulen und sonstige Ausbildungseinrichtungen, 4. Heime und 5. Ferienlager."
- Düzeltme: §33'ü kaynak olarak ekle (ya da 151'in yerine kullan) ve metni "kreş/gündüz bakım ve çocuk kulübü, gündüz anneliği, okullar ve diğer eğitim kurumları" olarak adlandır; "Nr.1–3" havalesini kaldır.

- Bulgu 2 (orta): Eyalet farkı gizli. Adım 1, summary ve claim 100 kanıtın "kurum yönetimine" verileceğini kesin söylüyor. IfSG §20 Abs.9: eyaletin üst sağlık makamı kanıtın kurum yönetimi yerine sağlık müdürlüğüne ya da başka bir devlet makamına verilmesini belirleyebilir; gündüz anneliğinde (Kindertagespflege) ruhsat veren makam kanıtın kendisine verilmesini belirleyebilir. Not alanı yalnız ücretsiz aşıdaki eyalet farkını söylüyor.
- Kanıt: https://www.gesetze-im-internet.de/ifsg/__20.html "Die oberste Landesgesundheitsbehörde oder die von ihr bestimmte Stelle kann bestimmen, dass 1. der Nachweis nach Satz 1 nicht der Leitung der jeweiligen Einrichtung, sondern dem Gesundheitsamt oder einer anderen staatlichen Stelle gegenüber zu erbringen ist"
- Düzeltme: Adım 1/timing: "Kanıt kural olarak kurum yönetimine verilir; eyalet bunu sağlık müdürlüğüne ya da başka bir makama verilecek şekilde değiştirebilir (eyalete göre değişir)." Eyalet adı yazma.

- Bulgu 3 (küçük): Muayene hakkı çerçevesi. Subtitle/summary "sigortalı çocuk 18 yaşına kadar … muayene hakkına sahiptir" sürekli yıllık kontrol izlenimi verir; yasa Früherkennung hakkını verir, yaş sınırlarını ve sıklığı G-BA yönergesi belirler (§26 Abs.2). Eyalet farkı cümlesi ("sigorta kuruluşları … eyalet makamlarıyla birlikte çalışır") yasadaki "auf eine Inanspruchnahme … hinzuwirken" (muayene kullanımını teşvik) anlamını vermiyor, bulanık.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__26.html "Der Gemeinsame Bundesausschuss bestimmt in den Richtlinien nach § 92 … die Altersgrenzen und die Häufigkeit dieser Untersuchungen." ; "Die Krankenkassen haben im Zusammenwirken mit den … Stellen der Länder auf eine Inanspruchnahme der Leistungen nach Absatz 1 hinzuwirken."
- Düzeltme: "Muayenelerin yaşları ve sıklığı Federal Ortak Komite yönergesiyle belirlenir"; ikinci cümleyi "Sigorta kuruluşları eyaletlerin belirlediği makamlarla birlikte muayenelerin kullanılmasını teşvik eder; bu işleyiş eyalete göre değişir" biçiminde yaz.

Doğrulananlar: 31.12.1970 sonrası doğanlar, ≥1. yaştan 1 aşı, ≥2. yaştan 2 aşı, bağışıklık/kontrendikasyon belgesi, her hekimin aşı yetkisi, 1 yaştan sonra kanıtsız bakılamama, STIKO/RKI: IfSG §20 ile birebir. "Kısmen evet" ilk cümlesi iyi.

---

### hamilelik-mutterpass-ebe-annelik-koruma-sureleri: orta
- Bulgu 1 (orta): Başlık "hangi haklarım var?" diyor ama koruma süresinde ücret/ödeme bilgisi (Mutterschaftsgeld) hiç yok. Okuyucu altı+sekiz haftanın ücretsiz olduğunu sanabilir. Kaynak dizininde SGB V §24i (de:kaynak:156, topic saglik) var ve kullanılmamış; yasada rakam da var (kalendertäglich en çok 13 Euro, fazlasını işveren öder).
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__24i.html "Es beträgt höchstens 13 Euro für den Kalendertag. … Übersteigt das durchschnittliche Arbeitsentgelt 13 Euro kalendertäglich, wird der übersteigende Betrag vom Arbeitgeber … gezahlt."
- Düzeltme: Bir cümle ekle: "Çalışan kamu sigortalı kadın koruma süresinde annelik parası (Mutterschaftsgeld) alır; kasa günlük en çok 13 Euro öder, ortalama günlük net ücret bunu aşıyorsa farkı işveren öder (SGB V §24i)." Kaynak sayısı sınırı için 154'ten ya da yeni bir kartla çöz; kural 6'ya göre kaynakta yıl yok, tarih yazma. Özel sigortalılar için kaynak yok: yazma.

- Bulgu 2 (küçük): Subtitle "işveren doğumdan önceki son altı hafta ve doğumdan sonra sekiz hafta seni çalıştıramaz" doğum öncesi için kesin konuşuyor; doğum öncesi yasak, kadın açıkça çalışmaya hazır olduğunu bildirirse uygulanmaz (summary bunu doğru yazıyor). Başlık/özet tutarsızlığı, kural 8.
- Kanıt: https://www.gesetze-im-internet.de/muschg_2018/__3.html "soweit sie sich nicht zur Arbeitsleistung ausdrücklich bereit erklärt."
- Düzeltme: Subtitle: "… doğumdan önceki son altı haftada (sen açıkça istemedikçe) ve doğumdan sonra sekiz hafta seni çalıştıramaz."

- Bulgu 3 (küçük): `cost`/summary "muayenelerin ve danışmanlığın masraflarını kamu ve özel sigortalar öder" kaynakta "ausreichende medizinische Untersuchung und Beratung" için; okuyucu bunu kartın sonundaki Beratungsstelle/Hilfetelefon danışmanlığı sanabilir (o danışmanlık "in der Regel kostenlos", sigorta ödemez). Aynı alanda iki ayrı "danışmanlık" var.
- Kanıt: https://familienportal.de/familienportal/lebenslagen/schwangerschaft-geburt/gesundheit-und-beratung "Jede Schwangere hat auch einen Anspruch auf ausreichende medizinische Untersuchung und Beratung. Die gesetzlichen und die privaten Krankenkassen übernehmen hierfür die Kosten."
- Düzeltme: "Hamilelik muayenelerinin ve tıbbi danışmanlığın masraflarını …"; danışma merkezi cümlesini ayrı yaz ("genellikle ücretsiz, istersen anonim" kaynakla uyumlu).

Doğrulananlar: 6 + 8 hafta, 12 hafta (erken doğum, çoklu doğum, engel ve yalnız başvuruyla), beyanın geleceğe dönük geri alınması, beklenen doğum tarihi belgesi, Hilfetelefon 0800/40 40 020, 19 dil, ebe hakkı (kamu sigortalı) ve özel sigortalıya "önce sor": kaynakla birebir.

---

### bakim-sigortasi-pflegegrad-basvurusu-pflegegeld: orta
- Bulgu 1 (orta): `timing` ve claim 141, bir haftalık kısaltılmış değerlendirme süresini koşulsuz yazıyor ("hastanede ya da rehabilitasyon tesisinde, hospiste veya ambulant palyatif bakımda değerlendirme bir hafta içinde yapılır"). Kaynakta hastane/rehabilitasyonda bir hafta yalnız "zur Sicherstellung der weiteren Versorgung erforderlich" ise ya da bakım veren kişi PflegeZG/FPfZG kapsamında izin aldı/duyurduysa geçerli; evdeyken (palyatif değilse) bakım veren izin aldıysa süre iki haftadır; yalnız hospis ve ambulant palyatif bakımda koşulsuz bir hafta. Kural 8 ihlali, hak/süre beklentisi yanlış.
- Kanıt: https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/pflegebeduerftig-was-nun "bei einem Aufenthalt im Krankenhaus oder in einer stationären Rehabilitationseinrichtung, wenn dies zur Sicherstellung der weiteren Versorgung erforderlich ist" ; "ist eine Begutachtung innerhalb von zwei Wochen nach Antragseingang durchzuführen."
- Düzeltme: Timing: "Karar için yasal süre 25 iş günüdür. Hospiste ya da ambulant palyatif bakımda değerlendirme bir hafta içinde yapılır; hastane ya da rehabilitasyon tesisindeyken de, taburculuk sonrası bakımın sağlanması için gerekliyse ya da bakım veren kişi bakım izni aldıysa/duyurduysa süre bir haftadır; evde ve bakım veren izin aldıysa iki haftadır."

- Bulgu 2 (küçük): `note` 70 Euro cümlesinde iki istisnadan yalnız "gecikmeden sorumluysa" yazılmış; tam yatılı bakımda ve en az Pflegegrad 2 olan kişiye ödeme yapılmaz (claim 144'te var, kartta yok). Ayrıca ödeme süresi ("fristablauf … spätestens innerhalb von 15 Arbeitstagen") yazılmamış.
- Kanıt: https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/pflegebeduerftig-was-nun "Dies gilt nicht, wenn die Pflegekasse die Verzögerung nicht zu vertreten hat oder wenn sich die Antragstellerin oder der Antragsteller in vollstationärer Pflege befindet und mindestens … (mindestens Pflegegrad 2)."
- Düzeltme: Note'a "tam yatılı bakımdaki ve en az Pflegegrad 2 olan kişiye bu ödeme yapılmaz" ekle.

- Bulgu 3 (küçük): valid_until null; ama kartta 2026'ya ait iki tutar var (Pflegegeld tablosu "Stand: 14. September 2026", ortak yıllık tutar 3.539 "im Jahr 2026"). Kaynak yıl veriyor: kural 11 ve DE notu (tarihe duyarlı listesi) 2026-12-31 ister.
- Kanıt: https://www.bundesgesundheitsministerium.de/pflege-zu-hause "Er beträgt im Jahr 2026 insgesamt bis zu 3.539 Euro im Kalenderjahr."
- Düzeltme: valid_until.json'da bu kartın değerini "2026-12-31" yap.

- Bulgu 4 (küçük): Verhinderungspflege cümlesi aile içi bakımda yanıltıcı: 3.539 Euro "en çok" doğru, ama ayni yakınlar ya da aynı evde yaşayanlar yedek bakımı ticari olmadan yapıyorsa kasa yılda en çok iki aylık Pflegegeld öder (Pflegegrad'e göre iki katı tutar); kart hedef okuyucusu tam bu kişi. Ayrıca "Pflegegrad" kavramı (1–5, Begutachtungsinstrument) hiç tanımlanmamış; başlıkta "Pflegegrad" var. §15 SGB XI (kaynak dizininde 157) kullanılmamış.
- Kanıt: https://www.bundesgesundheitsministerium.de/pflege-zu-hause "dürfen die Aufwendungen der Pflegekasse im Kalenderjahr dagegen grundsätzlich den Betrag des Pflegegeldes für bis zu zwei Monate, also den zweifachen Betrag des Pflegegeldes des festgestellten Pflegegrades, nicht überschreiten."
- Düzeltme: Note'a "yedek bakımı yakının ya da aynı evde yaşayan biri ücretsiz yapıyorsa kasa yılda en çok iki aylık bakım parası öder" ekle; summary'ye "Pflegegrad, bakım ihtiyacının ağırlığına göre 1–5 arası verilen derecedir" (SGB XI §15) ekle.

Doğrulananlar: başvuru telefonla, Pflegekasse Krankenkasse bünyesinde, yetki belgesi, Medicproof, danışmanlık iki hafta, 25 iş günü, 70 Euro/hafta, 10 yıl içinde 2 yıl şartı, Pflegegeld 347/599/800/990 (canlı, Stand 14. September 2026), Pflegegeld için en az Pflegegrad 2, yarım yılda bir danışmanlık (yalnız Pflegegeld alanlar): kaynakla birebir.

---

## Çapraz kontrol: para 308 (maas-sosyal-sigorta-kesintileri-2026) ↔ saglik 603
- Aynı olanlar (çelişki yok): GKV genel oran %14,6; ortalama ek prim %2,9 (2026); indirimli %14,0 (308 note, 603 summary); BBG sağlık aylık 5.812,50 (iki kart); primi işveren/çalışan yarı yarıya (ek prim dahil); Sonderkündigungsrecht; aile sigortasında eş/çocuk için prim yok. Canlı BMG sayfasıyla ikisi de uyumlu.
- 308 için bulgu (orta, para denetçisine/editöre): Başlık/özet bordro kesintilerini "emeklilik, işsizlik ve sağlık" diye sayıyor; bakım sigortası (%3,6, işçi payı 1,8; çocuksuzda 2,4) bordroda ayrı bir kalem ve 603'te var, 308'de yok. Bordro kalemlerini bulmaya çalışan okuyucu bir kalemi eksik bırakır; ya 308'e bir cümle ya da 603'e atıf eklenmeli. Kaynak: https://www.bundesgesundheitsministerium.de/themen/pflege/online-ratgeber-pflege/die-pflegeversicherung/finanzierung "Arbeitnehmerinnen beziehungsweise Arbeitnehmer und Arbeitgeber tragen den Beitrag … grundsätzlich zur Hälfte, also jeweils 1,8 Prozent."
- 308 küçük: note'ta "ermäßigter Beitragssatz (indirimli oran)" Almanca terim iç içe; kart dili Türkçe olmalı.
- 603 tarafında tutarsızlık yok; 603'ün "5.812,50" ve 308'in "5.812,50" aynı BMG sayfasından.
