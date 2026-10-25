# Almanya ulusal paketi, grup 2 (saglik, ev, planlama): editör sonrası DAR bağımsız denetim (g2b)

Tarih: 25.10.2026. Denetçi kartları yazmadı. Kart dosyalarına dokunulmadı. Karşılaştırma: güncel kartlar ↔ `yedek_g2_editor_oncesi` ↔ editör kayıtları ↔ kaynak metinleri (`kaynak_dizini.jsonl` → `text_file`).

## Özet
- Kart: 27 (saglik 601–609, ev 701–709, planlama 801–809).
- Yeni ya da kalan bulgu: **ciddi 0, orta 7, küçük 12**. İlk raporlardaki 3 ciddi bulgunun hepsi kapandı ya da orta düzeye indi (701 "iş günü", 704 ters istisna, 601 GKV genellemesi).
- Yöntem: (1) editörün değiştirdiği her alan yedekle satır satır karşılaştırıldı; (2) yeni/değişen tüm claim'ler (saglik ~95, ev ~35, planlama ~60) için quote'un kaynak metninde geçtiği script'le, iddiayı kanıtlayıp kanıtlamadığı elle kontrol edildi; (3) 27 kart için kart başına ≤2 kaynak, claim kaynağının kartın source_ids'inde olması, kartın her kaynağına en az bir claim, Bağlantılar, yasaklı sözcük taraması (şehir adı, "teyit et", "bu kartta yok", "anlatılır", "tarif edilir") script'le yapıldı: tüm kartlar ≤2 kaynak, hiçbir claim kart kaynağı dışında değil, editörün eklediği/değiştirdiği hiçbir quote "bulunamadı" vermedi. (saglik/603'teki iki eski claim'in (13, 17) quote'u birebir eşleşmiyor; editör dokunmadı, anlam doğru, küçük biçim sorunu.)
- Canlı açılan sayfalar (Python urllib, 25.10.2026), yalnız editörün eklediği yeni bilgi için: gesetze-im-internet.de BGB §556d (2029 bitişi), BGB §575 (kopyayla aynı), IfSG §33 (kopyayla aynı), VwVfG §23 (kopyayla aynı); bmj.de Mietrecht (hâlâ "Veröffentlicht am: 14. September 2022"). Fark yok.
- Bakılmayanlar: kapalı siteler (bmi.bund.de, make-it-in-germany.com, auswaertiges-amt.de); idata.com.tr; EUR-Lex DVO (AB) 2026/636 (Türkiye'nin Ek I/II'de olup olmadığı doğrulanamadı); SGB V tam metin kopyasının (2,36 M karakter, 3 MB'da kesik) kesildiği yer aranmadı: kartların dayandığı §5, §6, §9, §10, §193 bölümleri kopyada tam ve canlıyla uyumlu; BGH Werktag/Cumartesi kararı (resmî olmadığı için kaynak alınmadı).

---

## A. İlk bulgular kapanış tablosu

Derece = ilk raporun derecesi. Durum: kapandı / kısmen / açık. "Yeni" = editör müdahalesinden doğan yeni sorun (aşağıda ayrıntı).

### saglik
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| 601 | B1 ciddi, ücretli çalışan = zorunlu GKV genellemesi | **kapandı** (yeni orta: gönüllü GKV yok, bkz. B-601) | Özet/adım 1 "kural olarak"; JAEG, memur (Beihilfe/Heilfürsorge), hauptberuflich selbständig istisnaları kaynaklı (claim 14-18; 265: "Versicherungsfrei sind 1. Arbeiter und Angestellte, deren regelmäßiges Jahresarbeitsentgelt die Jahresarbeitsentgeltgrenze … übersteigt") |
| 601 | B2 orta, VVG §193 diğer muafiyetler | kapandı | Özet: Heilfürsorge, Beihilfe (kapsam ölçüsünde), Asylbewerberleistungsgesetz; claim 24-25 birebir |
| 601 | B3 orta, Türk okuyucu Nr.13/Abs.11 | kapandı | Adım 2: "AB, AEA ya da İsviçre vatandaşı değilsen…"; claim 19-23 birebir; Türkiye anlaşması yazılmamış |
| 601 | B4 küçük, öğrenci notu | kapandı | Not: 30 yaş sonrası istisna ve §5 Abs.7 (claim 26-28 birebir) |
| 602 | B1 orta, koşullar yalnız eşe özgü | kapandı | "Bu iki koşul eş için aranır" silindi; Nr.2-3 eklendi (claim 15-17 birebir) |
| 602 | B2 orta, ikamet sonucu | kapandı (yeni küçük, bkz. K-602) | Özet/adım 1: "Almanya'da ikametgâhı … olmayan … eş ya da çocuk aile sigortası kapsamında değildir" |
| 602 | B3 küçük, geringfügig çevirisi | kapandı | "geringfügige (düşük ücretli) çalışma", Geringfügigkeitsgrenze tanımlı |
| 603 | B1 küçük, Bürgergeld/Grundsicherungsgeld | **açık** (kabul edilebilir) | Kart BMG kaynağındaki adı koruyor; canlı SGB V §5 Abs.1 Nr.2a "Grundsicherungsgeld". Kaynak kuralıyla uyumlu, küçük |
| 604 | B1 orta, 116117 = Terminservicestelle çıkarımı | kapandı | Başlık/özet/adım ayrıldı: "SGB V §75 … tek ülke çapında numara" ve "116117.de'ye göre … randevu bulmada yardım"; eşitlik cümlesi yok |
| 604 | B2 orta, kapsam (GKV, diş, psikoterapi) | kapandı | Özet: "Bu garantiler … kamu sigortalıları içindir"; §28 Abs.2/§29 hariç; psikoterapide sevk yok; claim 15-17 birebir |
| 604 | B3 küçük, bir hafta/dört hafta | kapandı | Note ve adım 4 |
| 605 | B1 küçük, cost = kapsam | kapandı | cost yalnız "116117 araması … ücretsizdir"; cümle note'ta |
| 606 | B1 orta, Belastungsgrenze hesabı | kapandı | Adım 2-3: %15/%10 düşüm, çocuk için EStG §32 Abs.6, SGB XII/II Regelsatz/Regelbedarf (claim 12, 16-20; 147: "Hierbei sind die jährlichen Bruttoeinnahmen für den ersten … um 15 vom Hundert … zu vermindern") |
| 606 | B2 küçük | kapandı | "(Abgabepreis)" eklendi |
| 607 | B1 orta, §33 Nr.1-3 havalesi | **kısmen** (yeni orta: Heime, bkz. B-607) | Kurumlar adlandırıldı (kreş/çocuk kulübü, Kindertagespflege, okul); "Nr.1–3" havalesi yok |
| 607 | B2 orta, eyalet farkı (kanıtın kime verildiği) | kapandı | Adım 2: eyalet sağlık müdürlüğüne/başka makama; gündüz anneliğinde ruhsat makamı (claim 23-24 birebir) |
| 607 | B3 küçük, muayene çerçevesi | kapandı | "yaş sınırlarını ve sıklığını Federal Ortak Komite … belirler"; "teşvik eder" |
| 608 | B1 orta, Mutterschaftsgeld yok | **açık** | Başlık "hangi haklarım var?" hâlâ koruma süresinde ücret bilgisini vermiyor; editör "uygulanamaz" (2 kaynak sınırı). Gerekçe makul; çözüm ayrı kart (SGB V §24i, kaynak 156) |
| 608 | B2 küçük, subtitle | kapandı | "(sen açıkça istemedikçe)" |
| 608 | B3 küçük, iki ayrı danışmanlık | kapandı | "tıbbi danışmanlık" / "Schwangerschafts-Beratungsstellen danışmanlığı" ayrıldı |
| 609 | B1 orta, 1 hafta süresi koşulsuz | kapandı | timing: hospis/palyatif koşulsuz; hastane/rehab koşullu; evde bakım izni varsa 2 hafta (claim 26-29; 158 birebir) |
| 609 | B2 küçük, 70 Euro istisnası | kapandı | Note: tam yatılı bakım + en az Pflegegrad 2, 15 iş günü (158: "mindestens Pflegegrad 2", "spätestens innerhalb von 15 Arbeitstagen") |
| 609 | B3 küçük, valid_until | kapandı | valid_until.json "2026-12-31" |
| 609 | B4 küçük, aile içi bakım sınırı / Pflegegrad tanımı | **kısmen** | İki aylık sınır eklendi (159); "1–5" aralığı ve Fahrkosten/Verdienstausfall istisnası yok (K-609) |

### ev
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| 701 | B1 ciddi, "üçüncü iş günü" çevirisi | **kısmen** (yeni orta x2, bkz. B-701a, B-701b) | "iş günü" her yerde "Werktag" yapıldı ama terim açıklanmadı; ayrıca kaynaksız tavsiye eklendi |
| 701 | B2 orta, fesih biçimi (§568) | **açık** (kabul edilebilir) | Kaynak alınamadı (thin_text); "nasıl" başlıktan çıkarıldı, yazılı biçim iddiası yazılmadı. Kapsam artık başlıkla tutarlı |
| 701 | B3 orta, süreli sözleşme (§575) | kapandı | §575 (267) eklendi; üç neden + yazılı bildirim şartı + "süresiz sayılır" (claim 16-20 birebir; canlı BGB §575 kopyayla aynı) |
| 701 | B4 küçük, kiralayan temel süre | kapandı | "aynı başlangıç hesabıyla … haklı menfaati" (BMJ: "ist die ordentliche Kündigung … spätestens am dritten Werktag … zulässig") |
| 702 | temiz | n/a | Değişiklik yok |
| 703 | B1 orta, Mietpreisbremse istisnaları | **kısmen** (yeni küçük/orta, bkz. K-703) | 1.10.2014 sonrası konut ve son 3 yılda kapsamlı modernizasyon, Textform bildirimi, 30 ay geri talep eklendi (BMJ 180 birebir). Vormiete/§556e yok; 2029 ve "eyalet" çerçevesi çıktı |
| 703 | B2 küçük, §§559-560 cümlesi | kapandı | "Kappungsgrenze için" |
| 704 | B1 ciddi, §556 istisnası ters | **kapandı** | Özet: "yalnız gecikmeden kendisi sorumlu değilse isteyebilir"; claim 7 düzeltildi (067: "es sei denn, der Vermieter hat die verspätete Geltendmachung nicht zu vertreten"). 503 ile aynı anlam |
| 704 | B2 orta, 503 ile tekrar/çelişki | **kısmen** | İtiraz süresi, belge inceleme çıkarıldı. 12 aylık hesap bildirimi ve Nachforderung hâlâ iki kartta; ama artık çelişmiyor (karşılaştırıldı: 503 summary/steps ile aynı kural) |
| 704 | B3 küçük, kalem listesi | **kısmen** | Nr.15 (anten/geniş bant) ve "on yedi numara" çerçevesi eklendi (claim 30-32); Nr.5 yok (kabul) |
| 705 | küçük (§536b) | açık (kabul) | Kaynak yok, doğru karar |
| 706 | B1 orta, WBS eyalet çerçevesi | **kısmen** | "Gelir sınırı ve … uygun konut büyüklüğü eyalete göre değişebilir" (claim 18, 169 birebir). Özet hâlâ federal "WoFG kapsamındaki" çerçevede başlıyor; "sosyal konut hukuku eyalet yetkisinde" genel iddiası kaynaksız olduğu için yazılmamış (doğru) |
| 706 | B2 küçük, "2025 durumudur" tekrarı | kapandı | Subtitle ve note'tan silindi; summary'de bir kez |
| 707 | B1 orta, 201 ile tekrar / süre | kapandı (yeni orta: havale cümlesi, bkz. B-707) | Kart emlakçı ücretine odaklandı; teyit kısmı tek cümle |
| 707 | B2 küçük, "Bestellerprinzip" | kapandı | Cümle silindi; "kim öder" §2 Abs.5 Nr.2 ile (claim 17) |
| 708 | küçük, "bunu hiçbir zaman yapmaz" | kapandı | "gezme randevusu için ücret istemez" (174: "Seriöse Makler oder Vermieter tun dies niemals") |
| 709 | B1 orta, başlık kapsamdan geniş | kapandı | Başlık "…noterde mi yapılır; Grunderwerbsteuer oranını kim belirler?"; adım 2 "noter tasdiki zorunludur" |

### planlama
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| 801 | A orta, sigorta adımı kaynaksız sırada | **kısmen** (yeni orta, bkz. B-801) | "sonra sigorta" kalktı; ama yerine "sigortanı girişten önce ayarla" konmuş, bu da kaynaksız |
| 801 | B küçük, "yalnızca başvuru üzerine" | kapandı | "kural olarak"; claim 8 quote'u tam cümle ("…soweit nichts anderes bestimmt ist.") |
| 802 | A orta, 90 EUR / ulusal vize | **kısmen** | "Temsilciliğin güncel uyarı sayfasına göre en çok 90 EUR" olarak atfedildi (041: "Visumgebühr (max. 90 EUR)"). 75 EUR kartta yok (2 kaynak sınırı). Bkz. K-802 |
| 802 | D orta, 15-45 gün | kapandı | Cümle ve claim 24-25 silindi |
| 802 | E orta, çevrim içi başvuru | kapandı | Özet/adım 042'ye göre yeniden yazıldı (claim 32, 33, 35 birebir) |
| 802 | B/C/F/G/H küçük | kapandı (C kısmen: bkz. K-802) | "tek" kalktı; "39,92 ve/veya 12"; "yükseköğrenim (Studium)"; "güncel sayfaya göre"; kontrol listesi göndermesi silindi |
| 802 | I küçük, 102 ile tekrar | açık (kabul) | Editör bilerek korudu |
| 803 | A, B, C küçük | kapandı | "başvurmazsın" silindi; "konut ilk kez sana ait oluyorsa"; Steuer-ID yeri/11 hane cümleleri 203'e bırakıldı |
| 804 | A orta, documents/iş sözleşmesi | kapandı | "…süre daha kısaysa en az 12 ay AB dışında yaşama niyetini gösteren belge (örneğin iş sözleşmesi)" (187 birebir) |
| 804 | B küçük | kapandı | "aynı amaçlarla", Überwachungszollstelle, "tüketilemeyen eşyalar", "kural olarak girişte" (claim 31-32 birebir) |
| 805 | A, B küçük | kapandı | "uçak ve deniz yolculuğunda 430, diğer yolculuklarda 300"; valid_until null |
| 806 | A orta, Türkiye cümlesi | kapandı | Summary/claim 5/7 silindi; test koşullu (DVO Ek I/II) |
| 806 | B, C küçük | kapandı | "3 Temmuz 2011'den itibaren"; "daha fazla hayvan için AB ticaret şartları" |
| 807 | A orta, havale cümlesi | kapandı | İki cümle silindi; başlık Schengen + oturum belgesine daraltıldı |
| 807 | B küçük | kapandı | valid_until null |
| 808 | A, B küçük | açık (kabul) | Roma/Yaoundé kaynağı ve 1.091 EUR (2025) notu kartta tarihli duruyor |
| 808 | C küçük | kapandı | "Hayır, yalnız Sperrkonto ile sınırlı değil…" |
| 809 | A orta, VwVfG ulusal kural | kapandı | Kaynak 088; "federal makamlar", md. 1/3 eyalet istisnası (claim 11-12 birebir; canlı §23 kopyayla aynı) |
| 809 | B küçük, md. 23/4 ayrıntıları | kapandı | "bu sonucu hatırlatma", "devletlerarası anlaşmalar" (claim 13-14 birebir). İki konu tek kartta: açık, küçük |

---

## B. Editörün eklediği/değiştirdiği içerikte yeni ya da kalan bulgular

### B-601: saglik-sigortasi-zorunlulugu-kamu-ozel: orta
- Bulgu: Başlık "kamu mu özel mi" sorusu. Yeni subtitle "kamu sigortasına zorunlu girmeyenler, ör. geliri sınırı aşan çalışanlar ve serbest çalışanlar, özel sigorta (PKV) yaptırır" ve özetin son cümlesi ("Kamu sigortasında zorunlu sigortalı olmayan ve yukarıdaki istisnalara girmeyen kişi özel sigorta (PKV) yaptırır") özel sigortayı tek yol gibi sunuyor. Zorunlu sigortalılıktan çıkan kişi (JAEG'yi aşan çalışan) **gönüllü GKV üyeliğiyle (SGB V §9) kamu sigortasında kalabilir**; VVG §193 muafiyeti de "gesetzlich krankenversichert" olanları kapsıyor (kart özetin ilk yarısında bunu yazıyor, subtitle ve son cümle çelişiyor). Kaynak 265 §9'u içeriyor ama karta girmemiş. İlk raporun düzeltme önerisi ("PKV ya da gönüllü kamu sigortası") uygulanmadı.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__9.html (kopyada: "§ 9 Freiwillige Versicherung (1) Der Versicherung können beitreten 1. Personen, die als Mitglieder aus der Versicherungspflicht ausgeschieden sind …"); VVG §193: "in der gesetzlichen Krankenversicherung versichert oder versicherungspflichtig sind" (claim 2).
- Düzeltme: Subtitle: "…zorunlu girmeyenler (ör. geliri yasal sınırı aşan çalışanlar, serbest çalışanlar) özel sigorta (PKV) yaptırır ya da koşulları varsa gönüllü olarak kamu sigortasında kalır." Özetin son cümlesini ve adım 3'ü aynı şekilde "özel sigorta ya da gönüllü kamu sigortası" yap; gönüllü üyeliğin koşullarını (§9) yazma, yalnız varlığını söyle ve 265'ten bir claim ekle (kaynak sayısı değişmez).
- Not (kaynak 265): kopya 2,36 M karakter ve 3 MB'da kesik; kartın dayandığı §5, §6, §9, §11 kopyada tam. 28 claim'in hepsi kopyada birebir bulundu.

### B-607: cocuk-asilari-kizamik-zorunlulugu-cocuk-muayeneleri: orta
- Bulgu: Özet "bu kurumlarda ya da yurt ve bakım evlerinde (Heime) çalışacaksa" ve claim 22 "§33 Nr.4: yurtlar ve bakım evleri (Heime)". IfSG §33 Gemeinschaftseinrichtung'u "überwiegend minderjährige Personen betreut werden" diye tanımlıyor; Nr.4 "Heime" çocuk/genç yurtlarıdır, "bakım evi" (huzurevi/Pflegeheim) değildir. Okuyucu huzurevinde çalışmanın bu kapsamda olduğunu sanabilir. Ayrıca çalışanlara ilişkin yükümlülüğün gerçek kapsamı (§20 Abs.8: §23 Abs.3 Satz 1 = hastane/muayenehane vb., §33 Nr.1-4, §36 Abs.1 Nr.4) kartta yarım: "bu kurumlarda … çalışacaksa" cümlesi hastane ve muayenehaneleri hiç anmıyor. Başlık çocuk odaklı olduğundan çalışan kısmı için en güvenli yol kapsamı daraltmaktır.
- Kanıt: https://www.gesetze-im-internet.de/ifsg/__33.html "Einrichtungen, in denen überwiegend minderjährige Personen betreut werden; dazu gehören insbesondere: 1. Kindertageseinrichtungen und Kinderhorte, … 4. Heime und 5. Ferienlager." (canlı ve kopya aynı); §20 (claim 6): "Personen, die in Einrichtungen nach § 23 Absatz 3 Satz 1, § 33 Nummer 1 bis 4 oder § 36 Absatz 1 Nummer 4 tätig sind."
- Düzeltme: "yurt ve bakım evlerinde (Heime)" yerine "çocuk ve gençlerin kaldığı yurtlarda (Heime)" yaz; çalışanlar için "ya da hastane, muayenehane gibi sağlık kuruluşlarında (IfSG § 23 Abs. 3)" ekle ya da çalışan cümlesini kaldırıp kartı yalnız çocuk bakımına daralt. Claim 22'yi aynı şekilde düzelt.

### B-608: hamilelik-mutterpass-ebe-annelik-koruma-sureleri: orta (ilk raporun açık kalan bulgusu)
- Bulgu: Başlık "hangi haklarım var?" diyor; 6+8 haftalık koruma süresinde ücret (Mutterschaftsgeld) bilgisi hâlâ yok. Editör kaynak sınırı nedeniyle uygulamadı.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__24i.html "Es beträgt höchstens 13 Euro für den Kalendertag."
- Düzeltme: Ayrı kart (SGB V §24i + MuSchG §19) ya da başlıktan "hangi haklarım var" ifadesini kaldırıp "hangi süreler" yap.

### B-701a: kira-sozlesmesi-suresiz-kural-kiraci-fesih-suresi: orta (ilk ciddi bulgunun kalıntısı)
- Bulgu: "iş günü" doğru biçimde kaldırıldı, ama yerine açıklamasız "üçüncü Werktag" kondu (subtitle, summary, steps, timing). Türkçe okuyucu Almanca terimi "Pazartesi–Cuma iş günü" diye okuyabilir; kaynaklar (BMJ 180) terimi tanımlamıyor. Risk hâlâ var, yalnızca görünürlüğü azaldı. Tanım ("Pazar ve resmî tatil hariç günler") resmî bir yasa sayfasında var ama karta eklenemiyor (≤2 kaynak).
- Kanıt: https://www.bmj.de/DE/themen/kaufen_reisen_wohnen/mietrecht/mietrecht_node.html "…spätestens am dritten Werktag eines Kalendermonats zum Ablauf des übernächsten Monats zulässig (§ 573c Absatz 1 Satz 1 BGB)."
- Düzeltme: Kaynaksız tanım yazılamıyorsa en azından "Werktag (Almanca terim; 'iş günü' ile aynı olmayabilir, Cumartesi sayılıp sayılmadığını kontrol et)" gibi kaynaklı olmayan ama yanıltmayan bir uyarı da kural 2'ye aykırıdır; bu nedenle önerilen yol: kaynak 267 (§575) yerine/yanına ≤2 sınırı içinde BGB §573c ya da BurlG §3 Abs.2 sayfasını almak, ya da kartta "Werktag" için "yasadaki terim; Pazar ve resmî tatiller sayılmaz" cümlesini kaynakla yazmak. Editör kararı gerekir.

### B-701b: aynı kart: orta (kaynaksız tavsiye)
- Bulgu: Adım 2 "bildirimi ayın başında yapmak bu süreyi kaçırma riskini azaltır". Editör kaydı: "Ayın başında bildirim önerisi eklendi." Kaynakların hiçbirinde (BMJ 180, BGB §575) böyle bir öneri yok; "Zugang" şartı da kaynakta olmadığı için yazılmadı, yani öneri dayanaksız bir varsayıma bağlı. Kural 2 ("cümle yalnız kartın kendi kaynağında yazıyorsa yazılır").
- Kanıt: 180 ve 267 metinlerinde "Monatsanfang/Beginn des Monats" ile bildirim önerisi geçmiyor (arandı, bulunamadı).
- Düzeltme: Sil. (B-701a çözülürse risk zaten azalır.)

### B-707: konut-veren-teyidi-ve-emlakci-ucreti-kiralik-ev: orta (yeni havale cümlesi)
- Bulgu: Özetin son cümlesi "Teyidin süresi ve içeriği adres kaydı konusunda anlatılır." Kural 3'ün yasakladığı havale ("burada açıklanmıyor" türü); başka karta gönderme.
- Kanıt: kart metni; kaynak 172 (BMG §19) süreyi "innerhalb der in § 17 Absatz 1 genannten Frist" diye veriyor, 201 "iki hafta" yazıyor.
- Düzeltme: Cümleyi sil ya da "Teyit, eve girişten sonraki adres kaydı süresi içinde (iki hafta) verilir" diye kaynakla (172) yaz.

### B-801: tasinma-sirasi-vize-giris-adres-kaydi-sigorta-oturum: orta (kaynaksız sıra)
- Bulgu: Başlık "vize, sağlık sigortası, giriş, adres kaydı ve oturum belgesi" sırasını veriyor; özet "bu yüzden sigortanı girişten önce ayarla", adım 3 "Sağlık sigortanı girişten önce ayarla", visual 3. öğe "girişten önce ayarlanır". Kartın iki kaynağında (AufenthG 035, BMG §17 186) sigortanın girişten önce yapılacağı yok; 035 yalnız "Lebensunterhalt … einschließlich ausreichenden Krankenversicherungsschutzes" gerçeğini veriyor (Regelerteilungsvoraussetzung), zaman sırası vermiyor. İlk rapor aynı şeyi "sıra uydurması" diye işaretlemişti; editör sigortayı sonraya değil öne aldı, yine kaynaksız. (Girişten önce sigorta şartı yalnız Schengen/807 ve 185 kaynağında var; 801'in kaynağı değil.) "Çünkü" bağı da mantıksal olarak dayanaksız: oturum belgesinin geçim güvencesi şartı sigortanın giriş öncesi yapılmasını gerektirmez.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/BJNR195010004.html (§ 2 Abs. 3) "Der Lebensunterhalt eines Ausländers ist gesichert, wenn er ihn einschließlich ausreichenden Krankenversicherungsschutzes ohne Inanspruchnahme öffentlicher Mittel bestreiten kann."
- Düzeltme: "girişten önce" sıra iddiasını ve "bu yüzden" bağını sil; başlığı "Almanya'ya taşınırken vize, giriş, adres kaydı ve oturum belgesi işlemleri hangi sırayla yapılır?" yap; sigortayı sıradan çıkarıp "oturum belgesi için geçim güvencesi sağlık sigortasını da kapsar" tek cümlesine indir; visual'ı güncelle. (Kaynak sınırı elverirse 185'in "ulusal vizede kanıt başvuruda istenir" cümlesi ancak 186 çıkarılırsa eklenebilir.)

---

## C. Küçük bulgular (yeni/kalan)

- **K-602** (saglik/602): Summary ve adım 1 "örneğin Türkiye'de yaşayan eş ya da çocuk aile sigortası kapsamında değildir": ilk raporun önerisi genel ifadeydi; "Türkiye" adı kaynakta yok ve DE notu Türkiye–Almanya sosyal güvenlik anlaşmasını yalnız kaynakla yazdırıyor. Düzeltme: "Almanya dışında yaşayan eş ya da çocuk" yaz. Ayrıca summary "kendisi zorunlu sigortalı olmamalı… sigortadan muaf olmamalı" §10'daki istisnaları söylemiyor: Nr.2 yalnız §5 Abs.1 Nr.1–8, 11–12'yi dışlar; Nr.3'te §7 (geringfügig) muafiyeti aile sigortasını engellemez. Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "Die Versicherungsfreiheit nach § 7 bleibt bei de…". Düzeltme: "sigortadan muaf olmamalı"yı "(Minijob türü çalışma nedeniyle muaf olmak engel değildir)" ile sınırla ya da sil.
- **K-603** (saglik/603): "Bürgergeld" adı açık; 601'in kaynağı (SGB V tam metin) "Grundsicherungsgeld" diyor, 603'ün kaynağı (BMG) "Bürgergeld". Kart içinde çelişki yok; tek parantez yeterli: "Bürgergeld (yasada güncel adı Grundsicherungsgeld)".
- **K-609** (saglik/609): "Pflegegrad" derecelerinin 1–5 olduğu yok (yalnız "en az Pflegegrad 2 = önemli ölçüde kısıtlılık"); Verhinderungspflege aile içi sınırında ek masrafların (Fahrkosten, Verdienstausfall) aynı yıllık tutara kadar ödenebileceği cümlesi yok (159: "Wenn in diesem Fall notwendige Aufwendungen der Ersatzpflegeperson … nachgewiesen werden…"). İki kaynak sınırı içinde 159'dan eklenebilir.
- **K-701** (ev/701): (a) §568 yazılı fesih kuralı kartta yok (başlık daraltıldığı için tutarlı, kabul); (b) "Süreli sözleşme yalnız üç nedenden biri varsa kurulabilir" BGB §549 Abs.2-3 istisnalarını (öğrenci yurdu, geçici kullanım) kapsamıyor; kaynaklı olduğu için yazılabilir, sadece "kural olarak" eklenmeli.
- **K-703** (ev/703, kullanıcının sorusu): Kart yanlış kesinlik **vermiyor**: 2029 bitişi çıkarılması bir eksiltmedir, yanlış değil. Ama (1) canlı BGB §556d "Eine Rechtsverordnung nach Satz 1 muss spätestens mit Ablauf des 31. Dezember 2029 außer Kraft treten" hâlâ geçerli; kart bu önemli sınırı artık söylemiyor ve valid_until null; (2) Mietpreisbremse bölgeleri artık "yönetmeliğe bağlıdır" deniyor, "eyalete göre değişir" yalnız Kappungsgrenze için kaldı (DE notu: Mietpreisbremse'nin geçerli olduğu yerler bölge paketine gidecek ve ulusal kart "eyalete göre değişir" demeli); (3) adım 4 "son 30 ayını geri isteyebilirsin" koşulsuz, özette "genellikle", kaynakta "grundsätzlich"; (4) Vormiete/son üç yılda modernizasyon yoluyla %10'u aşabilme (§556e) yok; (5) claim 3'ün `value` alanında kalıntı "tarih 2029". Hepsi kartın tek BMJ (2022 tarihli) kaynağıyla tutarlı; kart "BMJ'nin 14 Eylül 2022 tarihli özetine göredir" diye tarihlendirmiş (iyi). Düzeltme: adım 4'e "genellikle"; Mietpreisbremse için "yönetmelik eyalet hükümetince çıkarılır, bölgeler eyalete göre değişir" (kaynak 166/180 bunu söylemiyorsa yalnız "bölgeye göre değişir"); claim 3 `value` temizle. 2029 yazılacaksa BMJ'de yok, §556d eklemek kaynak sınırını aşar: kabul edilebilir.
- **K-706** (ev/706): Özet hâlâ "WoFG kapsamındaki sosyal konut" diye federal çerçevede başlıyor; eyalet farkı sonradan söyleniyor. Sourced, kabul edilebilir; "eyalete göre değişir" ilk cümleye çekilebilir.
- **K-704** (ev/704 ↔ fatura/503): Hesap bildirme süresi ve Nachforderung iki kartta duruyor; kural aynı ve doğru (704 artık 503 ile uyumlu). Tekrar bilinçli ise sorun yok.
- **K-802a** (planlama/802 ↔ oturum/102, kullanıcının sorusu): **Açık çelişki yok**, ama okuyucu için tutarsızlık sürüyor. 102: "ulusal D vizesi 75 Euro" (AufenthV md. 46, kaynak 043); 802: "temsilciliğin güncel uyarı sayfasına göre vize ücreti en çok 90 EUR" (041: "Visumgebühr (max. 90 EUR)"). 802 ulusal vize bekleme sürelerini anlatan bir kart; 75 yerine "en çok 90" görmek okuyucuyu ulusal vizede 90 EUR ödeyeceğini düşündürebilir. 12 EUR randevu bedeli yalnız 802'de (042: "Servicegebühr 39,92 € und/oder Terminbuchungsgebühr von 12 €"); 102 (041 + 043) 12 EUR'yu anmıyor ve 041 "Terminbuchung kostenlos" diyor. 802'nin "ve/veya" yazımı kaynağa uygun. Düzeltme: 802 summary/cost'ta "(ulusal D vizesi için ücret 102 kartında)" gibi havale yazma (yasak); onun yerine 802'de ücreti hiç sayısal vermeyip bekleme/akış kartı yap ya da 802'nin kaynağını 043 ile genişlet (041 çıkarılırsa bekleme sürelerinin kaynağı gider). Kısa yol: subtitle ve cost'tan 90 EUR'yu çıkar, ücreti 102'ye bırak; 102'ye 042'den "12 EUR" claim ekle.
- **K-802b** (planlama/802): Cost'un son cümlesi "Randevu bedeli konusunda sayfalar ayrışır: güncel uyarı sayfası … ücretsiz yazar, ulusal vize sayfası 12 EUR'dan söz eder" iç denetim notu niteliğinde: okuyucu hangisine güveneceğini öğrenemiyor ve kural 3'ün ruhuna (kaynaklar arası çelişkiyi karta taşıma) aykırı. Düzeltme: sil; çelişki zaten gaps.md'de.
- **K-806** (planlama/806): Türkiye'nin DVO (EU) 2026/636 Ek I/II'de olup olmadığı yazılmıyor (kaynakta yok, EUR-Lex denendi, boş yanıt): Türk okuyucu kartı okuyunca testin kendisi için gerekip gerekmediğini öğrenemiyor. Eksik bilgi gaps.md'de, kart doğru. Açık, kaynak bulunana kadar kabul.
- **K-808** (planlama/808): A (tutar Roma/Yaoundé sayfalarından, Türkiye sayfasında yok) ve B (1.091 EUR 2025 tarihli) açık; kartta tarih ve "Alman dış temsilciliklerinin sayfalarına göre" ibaresi var, kabul edilebilir.
- **K-809** (planlama/809): Başlık hâlâ iki ilgisiz konuyu (resmî dil, saat) birleştiriyor; kabul.
- **K-valid_until**: planlama 802/804/806/809 ve saglik/ev kartlarının çoğu valid_until.json'da yok (yazar kuralı: tarihe duyarsız = yok). Tarihe duyarlı sayı içeren saglik/604 (süreler değişmez, sorun yok), ev/706 var. Sorun yok.

---

## D. Özel istenen kontroller (özet cevaplar)

1. **saglik/601 (265 SGB V tam metin)**: Kaynak–claim–kart tutarlı; 28 claim'in 28'i kopyada birebir; iddialar (§5 Abs.1 Nr.1, 2, 9, 13; Abs.5; Abs.7; Abs.11; §6 Abs.1 Nr.1-2) doğru okunmuş. Tek sorun B-601 (gönüllü GKV eksik). Kart başına 2 kaynak (139 + 265): uyuyor. Kopya kesikliği kartın dayandığı maddeleri etkilemiyor.
2. **saglik/607 (266 IfSG)**: 27 claim kopyada birebir. Sorun B-607 (Heime çevirisi ve çalışan kapsamı). Okul zorunluluğu istisnası ("Schulpflicht … in § 33 Nummer 3 betreut werden") doğru yazılmış.
3. **ev/701 (267 §575)**: §575 yansıması doğru (üç neden, yazılı bildirim, aksi hâlde süresiz). Sorunlar B-701a (Werktag açıklaması) ve B-701b (kaynaksız "ayın başında" önerisi). Kart başına 2 kaynak (180 + 267): uyuyor.
4. **ev/703 (BMJ 2022 özeti, 180)**: Kart BMJ özetini sadık yansıtıyor; yanlış kesinlik yok, eksiklikler K-703'te. 2029 bitişi canlı yasada hâlâ geçerli.
5. **planlama/809 (088)**: Kapsam artık doğru (federal makamlar; md. 1/3 eyalet istisnası); md. 23/4 ayrıntıları eksiksiz; 14 claim'in 14'ü birebir.
6. **Konular arası**: 802 ↔ 102: açık çelişki yok, tutarsız izlenim (K-802a). 801 ↔ 201/oturum 101: "2 hafta" tutarlı; 801 "kural olarak yalnızca başvuru üzerine" ile 101 "belge başvuru üzerine verilir" aynı kaynaktan, uyumlu; 801'in sigorta sırası kaynaksız (B-801). 704 ↔ 503: artık çelişmiyor, ortak kural doğru (503 summary: "Bu süre geçtikten sonra ev sahibi ek ödeme talep edemez; gecikmeden sorumlu olmadığı durumlar bunun dışındadır").

---

## E. Sayım
- ciddi 0
- orta 7: saglik/601 (B-601), saglik/607 (B-607), saglik/608 (B-608, ilk raporun açık kalanı), ev/701 (B-701a), ev/701 (B-701b), ev/707 (B-707), planlama/801 (B-801)
- küçük 12: K-602, K-603, K-609, K-701, K-703, K-706, K-802a, K-802b, K-806, K-808, K-809, K-704 (bilgi)
