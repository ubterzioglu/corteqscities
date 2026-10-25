# Denetim G3b (dar, editör sonrası) — Almanya ulusal paketi: aile (8), ulasim (10), gunluk (9)

Denetçi: bağımsız (kartları yazmadım, editör değilim, kart dosyalarına dokunmadım). Tarih: 2026-10-25.

## Özet
- Kart: 27. Bu turdaki bulgu: **ciddi 0 / orta 5 / küçük 13**.
- Önceki ciddi (3) ve orta (23) bulgunun durumu: 3 ciddi bulgunun 2'si kapandı, 1'i kısmen (aile/907 Kinderzuschlag; editörün yerine yazdığı cümle yeni sorun doğurdu); 23 ortanın 20'si kapandı, 2'si kısmen, 1'i açık (aşağıdaki tablo, 26 satır).
- Editörün eklediği ya da değiştirdiği 104 claim ve tüm kart alanları yedekle karşılaştırıldı. 2 durumda kaynakla çelişen ya da kaynağın ötesine geçen yeni cümle var (aile/907 Kinderzuschlag yabancı cümlesi, gunluk/1107 BSK oturum belgesi cümlesi). 1 eski kapsam hatası editör notuna dokunulduğu hâlde kalmış (aile/908).
- Şehir/eyalet adı, havale cümlesi ("teyit et", "resmî sayfada yazar"), "yaklaşık" (kaynakta "ca." olan tek yer hariç), kart başına >2 kaynak: yok. Her kartta kaynak–claim–bağlantı tutarlı: claim'lerin kaynak kümesi kartın source_ids kümesiyle birebir, bağlantılar kartın kaynaklarından.
- Mağaza saatleri kartı (gunluk/1102): doğru ve eyalet çerçevesine uygun, LadSchlG saatleri tamamen çıktı; ama pratik değeri düşük ve başlıktaki "kesin hayır" sonucu claim'lerle kanıtlanmıyor (küçük bulgular).

## Yöntem
1. İlk 3 raporun (denetim_g3_aile/ulasim/gunluk.md) her ciddi ve orta bulgusu için güncel kart alanları okundu; kapanma kanıtı kaynak metniyle (kaynak_dizini.jsonl → text_file) bağlandı.
2. `yedek_g3_editor_oncesi` ile güncel kartlar alan alan karşılaştırıldı (title, subtitle, summary, steps, documents, timing, cost, note, keywords, source_ids); eklenen/silinen claim'ler ve bağlantı/valid_until farkları çıkarıldı. Editör kayıtları (degisiklik_g3_*_editor.jsonl, 83 satır) kartlarla karşılaştırıldı: kayıtta "uygulandı" denen her değişikliğin kartta olduğu doğrulandı.
3. Editörün eklediği 104 claim'in her biri için `quote` CANLI sayfada arandı (Python urllib, 35 sayfa). Sonuç: 104'ün 98'i ilk denemede birebir bulundu; kalan 6'sı yalnız boşluk/noktalama farkından (ör. "Monat ." , "( EG )") ya da yönlendirmeden dolayı bulunamadı ve elle canlı sayfada doğrulandı. Hiçbir quote canlıda değişmiş değil. Bir sayfa (bundesnetzagentur Vportal/Post/Info) ilk istekte meta-refresh yönlendirmesi döndürdü; yönlendirilen adreste (`?r=1`) iki quote da bulundu.
4. Editörün eklediği yeni hukuk bilgisi için ayrıca canlı kontrol: BKGG §6a (aile/907), GG md. 74 ve 125a (gunluk/1102), BAföG §8 tam metin (aile/906), StVG §2a Abs. 5 ve StVO §3 Abs. 3 tam metin, FeV §29 tam metin, SGB V §10 Abs. 3.
5. Konular arası: gunluk/1106 ↔ saglik/605, gunluk/1101 ↔ is/403, aile/908 ↔ saglik/602 ve resmi/209, ulasim/1008 ↔ resmi/208 (araç kaydı) kart metinleri yan yana okundu.

## Canlı açılan sayfalar
gesetze-im-internet.de: baf_g/__8, baf_g/__13, sgb_8/__24, bkgg_1996/__6a, fev_2010/__29 (yerel kopya + canlı quote), stvg/__2a, stvo_2013/__2 ve __3, verpackdg/__46, gg/art_74, gg/art_125a; arbeitsagentur.de: kindergeld-anspruch-hoehe-dauer, kinderzuschlag-anspruch-hoehe-dauer; familienportal.de: unterhaltsvorschuss, elterngeld (iki sayfa), kindergeld ausländische Eltern, Kinderbetreuung/Kosten; daad.de: ueberblick, studienkollegs; bamf.de: Titelab2005, DeutschBeruf, Schulbesuch; lba.de: FAQ_DeniedBoarding, Schlichtung; bahn.de: deutschland-ticket, umtausch-stornierung, fahrgastrechte/rechtliche-regelungen; bmv.de ehliyet sayfası; zoll.de: Steuerhöhe; bundesnetzagentur.de Post FAQ; 115.de; hilfetelefon.de; bbk.bund.de.
Kapalı siteler denenmedi.

## Bakılmayanlar
- zoll.de Internetbestellungen ve Geschenksendungen sayfalarının canlı karşılaştırması claim-quote düzeyinde yapıldı (tümü bulundu); sayfanın "Nach jetzigem Stand ... 1. November 2026" cümlesi bugün de aynı.
- Eyalet Ladenöffnungsgesetze, EStG §62, ElektroG §17, FZV §56, StGB §315c/§316 açılmadı (kart kaynakları değil; bulgularda "kaynak eklenirse" diye belirtildi).
- saglik/605 ve resmi/209 kartlarının kaynaklarına gidilmedi; yalnız kart metinleri okundu.

---

# 1. İlk bulgular kapanış tablosu (yalnız ciddi ve orta)

Durum: **kapandı** = düzeltme kartta ve kaynakla uyumlu; **kısmen** = düzeltme var ama kalan risk ya da yeni küçük kusur; **açık** = düzeltilmedi.

| # | Kart | İlk derece | İlk bulgu | Durum | Kanıt |
|---|------|-----------|-----------|-------|-------|
| 1 | aile/901 Kindergeld | orta | Eğitim amaçlı kalış koşulsuz "alamaz" | **kısmen** | Cümle artık "Familienportal'a göre" diye atfedilmiş ve Beschäftigungsduldung istisnası summary'ye girmiş. Ama okuyucuya yine koşulsuz "alamazsın" deniyor; yasadaki çalışma/Elternzeit/SGB III istisnası kartta yok (kaynak sınırı dolu). Aşağıda orta olarak yeniden yazıldı. |
| 2 | aile/901 | orta | Geriye dönük 6 ay sınırı yok | **kapandı** | Kaynak 245 çıkarıp 246 (arbeitsagentur Kindergeld) alınmış; timing + steps + claim var; canlı: "Die Frist zur rückwirkenden Zahlung von Kindergeld beträgt 6 Monate." |
| 3 | aile/902 Elterngeld | orta | Yabancı için oturum izni şartı (BEEG §1 Abs. 7) yok | **açık** | Editör "kaynak sınırı" diyerek uygulamadı, gaps.md'ye yazdı. Kartta yabancı koşulu hâlâ yok (aşağıda orta). |
| 4 | aile/902 | orta | 14 ay koşulsuz (Partnermonate şartı) | **kapandı** | subtitle ve summary: "bu 14 ayın 2'si Partnermonate'dir ve ... en az birinin ... daha az gelir elde etmesini gerektirir; tek başına yetiştiren de alabilir" (228 ile birebir). |
| 5 | aile/903 Kita | orta | Ganztag hakkı okulun üstüne 8 saat gibi | **kapandı** | note, SGB VIII §24 Abs. 4 üç cümlesine göre (ders/Ganztag süresi karşılanmış sayılır, tatillerde gençlik çalışması, 4 hafta kapanma). Canlı §24 aynı. |
| 6 | aile/904 Okul | orta | "Okul makamına başvur" kaynaksız usul | **kapandı** | "başvur" fiili kalktı; "yerleşime okul makamı karar verir; işleyiş eyalete göre farklı". |
| 7 | aile/906 BAföG | orta | 475 Euro ihtiyaç tutarı, ödenecek tutar sanılır | **kapandı** | summary + cost: "ihtiyaç hesabında kullanılır; ödenecek miktar değildir". İç not cümlesi silindi. |
| 8 | aile/906 | orta | Oturum izni listesi (§ 8 Abs. 2) kartta yok | **kapandı** | Adım 2-3-4'te listeler var; canlı §8 ile satır satır karşılaştırıldı: Abs. 2 Nr. 1 (22, 23/1-2-4, 23a, 25/1-2, 25a, 25b, 28, 37, 38/1/2, 104a, 104c; NE yakını için 30, 32-34, 36/2), Nr. 2 (25/3, 25/4 S.2, 25/5, 31; Aufenthaltserlaubnis yakını için 30, 32-34, 36/2, 36a; 15 ay), Abs. 2a Duldung 15 ay: hepsi doğru. |
| 9 | aile/906 | orta | Not "AB grupları Türk için geçerli değildir" fazla kesin (Abs. 5) | **kapandı** | "doğrudan sayılmaz" + "§ 8 Abs. 5: başka hukuk ve idare düzenlemeleri saklıdır". |
| 10 | aile/907 | ciddi | Unterhaltsvorschuss'ta yabancı çocuk koşulsuz | **kapandı** | Summary 244 ile uyumlu: AB/AEA/İsviçre genelde Alman çocukla aynı; diğerleri için NE, Daueraufenthalt-AB, Mavi Kart/ICT (6 ay çalışma), Aufenthaltserlaubnis (6 ay çalışma, "ek kısıtlar var"), Gestattung/Duldung yok, Beschäftigungsduldung var. |
| 11 | aile/907 | ciddi | Kinderzuschlag cümlesi Türk okuyucuyu yanlış dışlıyor, 901 ile çelişiyor | **kısmen** | Eski cümle silindi, "Kindergeld alıyor olman gerekir" eklendi (243 ile uyumlu). Ama yerine yazılan "Yabancıysan ... Kindergeld alma şartlarını (uyruk ve oturum belgesi) sağlamalısın" kartın kendi kaynağı 243'te yok ve 243'ün yabancı listesiyle (yalnız AB/AEA/İsviçre + kesinleşmiş sığınma hakkı sahipleri) örtüşmüyor. Aşağıda yeni orta bulgu. |
| 12 | aile/907 | orta | Kinderzuschlag şartları (Kindergeld, çocuk koşulları, 900/600) yok | **kapandı** | Summary üç şartı 243 ile aynı yazıyor; canlı sayfa aynı. |
| 13 | ulasim/1003 | orta | Kapsam: ulaşım birliği/eyalet tarifesi, metro/tramvay | **kapandı** | summary ve note'ta var, claim'ler birebir. |
| 14 | ulasim/1003 | orta | Süreli bilet: 60 dk koşulu, 4 Euro altı ödenmez, 20 dk toplama | **kapandı** | summary + adım 4 (yeni); BahnCard 100 istisnası ve geçerlilik süresi şartı da var. |
| 15 | ulasim/1004 | orta | Geçici kalış (Wohnsitz yok) ana cevap eksik | **kapandı** | subtitle, summary, adım 1: geçici kalışta geçerli; okul/üniversite Wohnsitz sayılmaz (BMV). Kaynak 209 → 208 (FeV §29) değişmiş, "6 ay + 6 ay uzatma, en çok 12 ay" §29 Abs. 1 ile uyumlu. |
| 16 | ulasim/1004 | orta | Anlage 11 "Türkiye listede yok" çıkarımı | **kapandı** | Cümle, kaynak 209 ve ilgili 4 claim silindi. |
| 17 | ulasim/1005 | orta | Römorklu/ağır araç hız sınıfları | **kapandı** | StVO §3 Abs. 3 Nr. 2 a/b/c ile satır satır doğrulandı (80, 60, 100 sınıfları ve otobüs ayakta yolcu). |
| 18 | ulasim/1006 | orta | "0,5 altında tut" imajı, alkol suçu kaynak yok | **kapandı** | Adım 1 "0,5 ve üzeri ... § 24a kabahat sayar"; başlık "kabahat sınırı". İlk raporun (b) yolu uygulanmış; yeni suç kaynağı eklenmediği için "0,5 altı güvenli" ima edilmiyor. |
| 19 | ulasim/1009 | orta | Nichtbeförderung (uçağa alınmama) yok | **kapandı** | summary + cost + note (check-in geç = Nichtbeförderung değil); LBA ile uyumlu. |
| 20 | ulasim/1009 | orta | Olağanüstü koşul niteleyicisi | **kapandı** | "tüm makul önlemler alınsa bile önlenemeyecek", "her olay ayrıca incelenir" var. (Yeni küçük: "kanıtlarsa" eklentisi, aşağıda.) |
| 21 | ulasim/1009 | orta | Üçüncü ülke kapsamı | **kapandı** | summary: AB dışından AB'ye uçuşta yalnız AB havayolu; iki AB dışı ise uygulanmaz. Ülke/havayolu adı yok. |
| 22 | gunluk/1102 mağaza saatleri | ciddi | LadSchlG md. 3 ülke geneli kural gibi | **kapandı** | Kart yeniden çerçevelendi; kaynak 263/008 çıktı, 268 (GG md. 74) + 264 (GG md. 125a). Ayrıntı ve kalan küçük kusurlar 3. bölümde. |
| 23 | gunluk/1104 Zoll | orta | 3 Euro "tüm paketlere" genel; 150 Euro üstü yok | **kapandı** | "belirli gönderilerde", "diğer 150 Euro altı: Regelzollsatz", "150 Euro ve üzeri: posta masrafı dahil toplam tutar" — üçü de 251'in cümleleri. |
| 24 | gunluk/1104 | orta | valid_until 2026-12-31, 1 Kasım cümlesi yanlışlaşır | **kapandı** | valid_until 2026-10-31. |
| 25 | gunluk/1107 Integrationskurs | orta | Hak olmayan haller + ilk oturum izni + BSK ön şartı eksik | **kapandı** (küçük kalıntı) | Okul eğitimi, düşük entegrasyon ihtiyacı, yeterli Almanca, "ilk oturum izni", BSK için Integrationskurs/B1: 253/254 ile uyumlu. Kalıntı: A2/B1 hedefli BSK'nın ek şartı (aşağıda küçük). |
| 26 | gunluk/1107 | orta | Not "oturum belgesi sahibi yabancılar içindir" BSK için yanlış | **kısmen** | BSK'nın AB vatandaşı ve göçmen kökenli Almanlara açık olduğu doğru yazıldı; ama editör "oturum belgesi şartı yalnız Integrationskurs hakkı içindir" cümlesini ekledi — kaynakta yok (aşağıda orta). |

Küçük bulguların durumu: aile 10, ulasim 18, gunluk 9 küçük bulgunun hepsi ya uygulandı ya da "kaynak yok/uygulanamaz" diye gerekçeli kapatıldı; gerekçeleri kaynak metniyle kontrol ettim ve haklı buldum (ElektroG 3 cihaz sınırı, FZV §56 sigorta pulu, KDV %7 kapsamı, çalışan gelir eşiği, Türkiye posta karinesi: kartın kaynağında yok → yazılmaması doğru). İki istisna: "saglik/605 ile tekrar" (gunluk/1106, açık, editoryal karar) ve "903↔907 muafiyet ifade farkı" (kısmen, aşağıda).

---

# 2. Kart kart yeni ve kalan bulgular

## aile

### kindergeld-tutar-ve-yabanci-icin-hak-sartlari (901): orta
- Bulgu: Eğitim amaçlı kalış cümlesi "Familienportal'a göre ... alamaz" diye atfedildi; atıf doğru (225'te: "Wenn Sie sich zum Zweck der Aus- oder Weiterbildung in Deutschland aufhalten" kein Kindergeld) ama okuyucu için hâlâ koşulsuz. Öğrenim izniyle (§ 16b) kalıp çalışan ya da Elternzeit/SGB III parası alan kişi yasada dışlanmıyor (ilk raporda EStG §62 Abs. 2 Nr. 3 ile kanıtlandı). Kart 2 kaynak sınırında olduğu için EStG eklenemedi. Atıf cümleyi doğru kılar ama hak kaybı riskini kaldırmaz. Kalan risk: orta.
- Kanıt: https://www.familienportal.de/familienportal/familienleistungen/kindergeld/familiensituation/koennen-auch-auslaendische-eltern-kindergeld-bekommen--124928 "Sie erhalten kein Kindergeld: Wenn Sie sich zum Zweck der Aus- oder Weiterbildung in Deutschland aufhalten." ; https://www.gesetze-im-internet.de/estg/__62.html "weder erwerbstätig noch nimmt er Elternzeit ... oder laufende Geldleistungen nach dem Dritten Buch Sozialgesetzbuch in Anspruch"
- Düzeltme: İki yoldan biri. (a) Cümleyi tamamen sil (kart yine eksiksiz kalır: hak olan yollar sayılmış, Duldung/Gestattung cümlesi ayrı). (b) Kaynak 246'yı çıkarmadan EStG §62'yi kullanmak mümkün değilse: "Yalnız eğitim amacıyla kalıyorsan Familienportal Kindergeld yok diyor" yerine "Eğitim amacıyla kalış izninde (§ 16b) çalışıyor, Elternzeit kullanıyor ya da SGB III parası alıyorsan bu dışlama uygulanmaz" ancak EStG §62 kaynağı eklenirse yazılır; eklenemiyorsa (a).

### elterngeld-sure-ve-basvuru (902): orta
- Bulgu: İlk rapordaki yabancı oturum izni şartı (BEEG §1 Abs. 7) hâlâ yok; editör bilerek eklemedi ("kaynak sınırı"). Kart AB dışından gelen Türk okuyucuya "Elterngeld alırsın, 14 ay" izlenimi veriyor; Kindergeld kartı (901) bu şartları anlatıyor ama Elterngeld kartı anlatmıyor. Kaynakta (228/229) yabancı şartı da yok, yani kaynak sınırı gerekçesi doğru; sorun kart tasarımında. Kart kapsamı olarak makul olabilir ama başlık yabancıya hitap eden bir paketin parçası.
- Kanıt: https://www.gesetze-im-internet.de/beeg/__1.html "(7) Ein nicht freizügigkeitsberechtigter Ausländer oder eine nicht freizügigkeitsberechtigte Ausländerin ist nur anspruchsberechtigt, wenn diese Person 1. eine Niederlassungserlaubnis oder eine Erlaubnis zum Daueraufenthalt-EU besitzt,"
- Düzeltme: Ya source_ids'ten 229'u (belgeler/başvuru) çıkarıp BEEG §1 ya da familienportal "ausländische Eltern" sayfasını (kaynak 231) alıp tek cümle: "AB/AEA/İsviçre dışından geliyorsan Elterngeld için oturum izninin türü de aranır (NE, Daueraufenthalt-AB, Mavi Kart AB, ICT, en az 6 ay çalışma izni veren Aufenthaltserlaubnis ...)". Ya da yabancı koşulunu ayrı bir kart olarak planla ve bu karta kısa cümle koyma. Karar editoryal; ben "açık" sayıyorum.

### kita-hakki-1-yasindan-itibaren-ucret-ve-kayit (903): küçük
- Bulgu: (a) note'ta "Werktage'de günde sekiz saat" Almanca sözcük çevrilmeden kalmış (ilk rapor "hafta içi ve cumartesi (Werktage)" önermişti). (b) Muafiyet ifadesi 903'te "veli payı ödemezsin" (233), 907'de "muaf olabilir; Jugendamt'tan bilgi al" (243); editör iki kaynak sözcüğü farklı diye ikisini bıraktı. Okuyucu iki kartı birlikte okursa farklı kesinlik görür.
- Kanıt: https://www.gesetze-im-internet.de/sgb_8/__24.html "Der Anspruch besteht an Werktagen im Umfang von acht Stunden täglich." ; 233: "Sie müssen keine Elternbeiträge bezahlen, wenn Sie Kinderzuschlag, Wohngeld ... erhalten." ; 243: "können Sie sich von den Gebühren für den Kita-Platz befreien lassen. Informieren Sie sich beim zuständigen Jugendamt."
- Düzeltme: (a) "Pazartesi–Cumartesi (Werktage) günde sekiz saat". (b) 907 notuna 903 ile uyumlu ifade: "Kinderzuschlag alıyorsan kreş veli payından muafsın; muafiyet için Jugendamt'a başvur" — ya da iki kartta da "muaf olabilirsin; Jugendamt'tan bilgi al". Biri seçilmeli.

### bafog-yabanci-ogrenci-sartlari-ve-ihtiyac-tutari (906): küçük
- Bulgu: Adım 4 "Bu listelerde standart çalışma izinleri, Mavi Kart ve öğrenim izni (§ 16b) yoktur; bu izinlerle yalnız şu yol kalır" — "yalnız" kesin; aynı kart note'unda § 8 Abs. 5 (başka düzenlemeler saklıdır) var. Liste tespiti doğru (canlı §8 Abs. 2 ile kontrol edildi); "yalnız" ise Abs. 5 ile çelişir görünüyor. İlk rapordaki öneri de "yalnız Abs. 3 kalır" demişti; ben bunu fazla kesin buluyorum.
- Kanıt: https://www.gesetze-im-internet.de/baf_g/__8.html "(5) Rechts- und Verwaltungsvorschriften, nach denen anderen Ausländern Ausbildungsförderung zu leisten ist, bleiben unberührt."
- Düzeltme: "bu izinlerle doğrudan yol yoktur; § 8 Abs. 3'teki beş yıl/ebeveyn şartı kalır" (yalnız → doğrudan).

### tek-ebeveyn-ve-dusuk-gelir-destegi-unterhaltsvorschuss-kinderzuschlag (907): orta
- Bulgu: Summary'nin son cümlesi "Yabancıysan Kinderzuschlag için önce Kindergeld alma şartlarını (uyruk ve oturum belgesi) sağlamalısın." Kartın kaynağı 243 yabancılar için başka bir şey söylüyor: "Personen ohne deutsche Staatsangehörigkeit können Kinderzuschlag bekommen, wenn sie zu einer dieser Gruppen gehören: [AB/AEA/İsviçre; kesinleşmiş sığınma hakkı sahipleri]. Zudem müssen sie die grundsätzlichen Voraussetzungen ... erfüllen." Yani kart, kendi kaynağının listesiyle örtüşmeyen yeni bir kural yazıyor. Canlı BKGG §6a ("Anspruch auf Kindergeld") editörün sonucunu hukuken destekliyor, ama bu kartın kaynağı değil; claim yok, quote yok (script yakalamaz). Kaynak–claim–kart tutarsız. Okuyucuya zarar riski düşük (Türk okuyucu için doğru yönde), ama kural 2 ("cümle yalnız kartın kendi kaynağında yazıyorsa yazılır") ihlali.
- Kanıt: https://www.arbeitsagentur.de/familie-und-kinder/kinderzuschlag-verstehen/kinderzuschlag-anspruch-hoehe-dauer "Personen ohne deutsche Staatsangehörigkeit können Kinderzuschlag bekommen, wenn sie zu einer dieser Gruppen gehören ... Zudem müssen sie die grundsätzlichen Voraussetzungen für Kinderzuschlag erfüllen." ; https://www.gesetze-im-internet.de/bkgg_1996/__6a.html "sie für diese Kinder nach diesem Gesetz oder nach dem X. Abschnitt des Einkommensteuergesetzes Anspruch auf Kindergeld oder Anspruch auf andere Leistungen im Sinne von § 4 haben,"
- Düzeltme: Son cümleyi sil. "Kindergeld alıyor olman gerekir" (243'te var, claim var) cümlesi tek başına yeterli ve doğru. Yabancı bilgisi gerekiyorsa BKGG §6a'yı 244 yerine ya da 243 yerine kaynak yapıp claim ekle.

### cocugun-saglik-guvencesi-ve-dogum-sonrasi-kayit-sirasi (908): orta
- Bulgu: note: "Aile sigortası, çocuğun diğer ebeveyni hiçbir Krankenkasse'ye üye değilse ve düzenli aylık geliri ... on ikide birini aşıp üyenin gelirinden de yüksekse çocuğu kapsamaz." SGB V §10 Abs. 3 yalnız üyenin **eşi ya da hayat ortağı** olan, çocukla akraba ebeveyn için aranır. Evli/hayat ortaklığı olmayan diğer ebeveyn için bu kural uygulanmaz. Kart "diğer ebeveyn" diyerek kapsamı genişletiyor; saglik/602 ise doğru yazıyor ("Çocuğun anne ya da babası olan eş"). Editör bu notu Türkçeleştirirken kapsamı düzeltmedi; evli olmayan çift çocuğun aile sigortası dışında kaldığını sanıp başvurmayabilir.
- Kanıt: https://www.gesetze-im-internet.de/sgb_5/__10.html "(3) Kinder sind nicht versichert, wenn der mit den Kindern verwandte Ehegatte oder Lebenspartner des Mitglieds nicht Mitglied einer Krankenkasse ist und sein Gesamteinkommen regelmäßig im Monat ein Zwölftel der Jahresarbeitsentgeltgrenze übersteigt und regelmäßig höher als das Gesamteinkommen des Mitglieds ist;"
- Düzeltme: "çocuğun diğer ebeveyni" → "üyenin eşi ya da kayıtlı hayat ortağı olan diğer ebeveyn" (602 ile aynı ifade).

### cocugun-saglik-guvencesi-ve-dogum-sonrasi-kayit-sirasi (908): küçük
- Bulgu: resmi/209 ile ton farkı: 209 "velayet sahibi ebeveyn olarak bildirimi sen yaparsın; kurum da yazılı bildirir, senin bildirim hakkın etkilenmez"; 908 hastane doğumunda yalnız "kurum Standesamt'ı bilgilendirir". 908'i tek okuyan hastane doğumunda kendi bildirim yükümlülüğü olmadığını sanabilir. Çelişki yok (kaynak 234 hastane doğumunu böyle anlatıyor), ama cümle pasif ("bildirilmesi gerekir") kimin bildireceğini söylemiyor.
- Kanıt: https://www.familienportal.de/familienportal/lebenslagen/schwangerschaft-geburt/anmeldung-standesamt "Nach der Geburt müssen Sie Ihr Kind innerhalb 1 Woche beim Standesamt anmelden" ; "Wenn Ihr Kind in einem Krankenhaus, Geburtshaus oder einer Geburtsklinik geboren wurde, benachrichtigt die Einrichtung das zuständige Standesamt und übermittelt die Geburtsbescheinigung."
- Düzeltme: Adım 1: "Çocuğu doğumdan sonra bir hafta içinde doğum yerine bakan Standesamt'a bildirmen gerekir; hastane, doğum evi ya da doğum kliniğinde doğduysa kurum Standesamt'ı bilgilendirir ve Geburtsbescheinigung'u iletir" (özne "sen" olsun). 234 "müssen Sie" diyor.

## ulasim

### tren-bileti-iptali-sparpreis-flexpreis-super-sparpreis (1002): küçük
- Bulgu: İlk bulguyu kapatmak için eklenen note cümlesi ("Uzun mesafe Flexpreis'te Deutsche Bahn bu ücreti 'Stornierung & Umtausch' (iptal ve değişim) başlığıyla verir: ... 30 Euro") kaynak etiketinin açıklaması; okuyucuya işlem sağlamıyor ve summary'deki "değişim mümkün değil" ile aynı kartta çelişir görünüyor (30 Euro karşılığında "Umtausch" yapılabilir gibi okunur). Summary'nin ilk cümlesi değişmedi.
- Kanıt: https://www.bahn.de/service/informationen-buchung/umtausch-stornierung "Der Umtausch gebuchter Tickets ist nicht möglich. Sie können Ihre gekauften Tickets aber stornieren und eine neue Reise buchen." ; "Stornierung & Umtausch im Fernverkehr (ICE, IC/EC) bis 1 Tag vor dem 1. Geltungstag der Hinfahrt: kostenlos ... Ab dem 1. Geltungstag der Hinfahrt: 30 Euro pro Fahrkarte"
- Düzeltme: Note'taki son cümleyi sil (30 Euro zaten cost ve adım 4'te). Summary'nin ilk cümlesi "Deutsche Bahn'a göre alınmış biletin başka tarihe değişimi (Umtausch) mümkün değil; bileti iptal edip yeni sefer alırsın" kalsın.

### tren-gecikmesi-tazminat-ve-sikayet-yolu (1003): küçük
- Bulgu: summary'de okuyucu metnine kaynak dili sızmış: "Süreli biletlerde (Zeitfahrkarte; kaynak haftalık ya da aylık kartı, Länder-Ticket'i ve Quer-durchs-Land-Ticket'i sayıyor)". "kaynak ... sayıyor" iç not tadında. İçerik doğru (D-Ticket sayılmıyor; kaynak listesi aynen).
- Kanıt: https://www.bahn.de/service/informationen-buchung/fahrgastrechte/rechtliche-regelungen "Zeitfahrkarten des Nah- und Fernverkehrs (z.B. Wochen- oder Monatskarten, Länder-Tickets, Quer-durchs-Land-Ticket)"
- Düzeltme: "Süreli biletlerde (Zeitfahrkarte; örneğin haftalık ya da aylık kart, Länder-Ticket, Quer-durchs-Land-Ticket)".

### turk-ehliyetiyle-surus-suresi-ve-alman-ehliyeti (1004): küçük
- Bulgu: Kaynak 209→208 (FeV §29) değişimi, geçici kalış cümlesi ve çeviri listesi kaynakla uyumlu (BMV ve §29 canlı doğrulandı). Kalan: adım 2 "Fahrerlaubnisbehörde ile iletişime geç; Alman ehliyetinin verilme şartları ehliyetin alındığı devlete göre değişir" başlıktaki "süre bittiğinde ne yapmam gerekir?" sorusuna cevap vermiyor; yalnız "git sor" diyor. BMV aynı sayfada cevabı veriyor: ehliyet geçersizse ya da süre dolacaksa **başvuru üzerine** Alman ehliyeti verilir.
- Kanıt: https://www.bmv.de/SharedDocs/DE/Artikel/StV/Strassenverkehr/gueltigkeit-auslaendischer-fahrerlaubnisse-in-deutschland.html "Droht Ihre ausländische Fahrerlaubnis abzulaufen oder ist sie nicht mehr gültig, erhalten Sie auf Antrag eine deutsche Fahrerlaubnis der entsprechenden Klasse."
- Düzeltme: Adım 2: "Süre dolmadan oturduğun yerin Fahrerlaubnisbehörde'sine başvur; başvuru üzerine Alman ehliyeti verilir. Verilme şartları ehliyetin alındığı devlete göre değişir." Ayrıca summary ilk cümlesi "geçerli bir ulusal ya da uluslararası ehliyet olarak ... geçerlidir" tekrarlı: "Türk ehliyetin, ulusal ya da uluslararası olarak geçerliyse, üzerinde yazılı sınıflar için geçerlidir" gibi sadeleştirilebilir.

### hiz-sinirlari-sehir-ici-sehir-disi (1005): küçük
- Bulgu: Subtitle "Otoyolda bu madde sınırı yoktur" — "madde" okuyucu için anlamsız (StVO §3 maddesi kastediliyor). İçerik StVO §3 Abs. 3 ile birebir doğru.
- Kanıt: https://www.gesetze-im-internet.de/stvo_2013/__3.html "Diese Geschwindigkeitsbeschränkung gilt nicht auf Autobahnen (Zeichen 330.1)"
- Düzeltme: "Otoyolda şehir dışı için konan bu sınırlar uygulanmaz; araç yine de kontrol altında tutulur."

### ucus-gecikme-iptal-tazminati-ve-uzlastirma (1009): küçük
- Bulgu: Summary'ye "olağanüstü bir koşulu **kanıtlarsa** tazminat ödemez" yazılmış. LBA metninde ispat yükü ifadesi yok ("entfällt die Verpflichtung ..."). Hukuken doğru olabilir ama kaynakta olmayan bilgi (kural 2/8). Ayrıca LBA'nın iptal cümlesi (Annullierung) gecikme için de aynı kalıpla uygulanıyor; geçiş kaynakta var ("Ein Anspruch ... besteht nicht, wenn die große Verspätung auf außergewöhnliche Umstände zurückgeht"), sorun yok.
- Kanıt: https://www.lba.de/DE/Fluggastrechte/FAQFluggastrechte/FAQ_DeniedBoarding/FAQ_node.html "Ist die Annullierung auf außergewöhnliche Umstände zurückzuführen, die sich auch dann nicht hätten vermeiden lassen, wenn alle zumutbaren Maßnahmen durch das Luftfahrtunternehmen ergriffen worden wären, entfällt die Verpflichtung des Luftfahrtunternehmens zur Zahlung der Ausgleichsleistung."
- Düzeltme: "Havayolu, tüm makul önlemler alınsa bile önlenemeyecek olağanüstü bir koşulu kanıtlarsa" → "Gecikme ya da iptal, havayolunun tüm makul önlemlerine rağmen önlenemeyecek olağanüstü bir koşuldan kaynaklanıyorsa tazminat ödenmez".

### Diğer ulasim kartları (1001, 1005 içerik, 1006, 1007, 1008, 1010)
Kapanma kanıtı tabloda. Yeni kusur bulmadım. 1008: "Zoll'un güncel tarifesine göre", motosiklet 1,84 Euro, "itibaren" düzeltmesi kaynakla uyumlu; resmi/208 ile tekrar/çelişki yok (aşağıda). 1007: 3 ay ve Aufbauseminar kanıtı StVG §2a Abs. 5 tam metniyle doğrulandı (Nr. 3 Entziehung için 3 ay; Probezeit ihlali ve Abs. 3 emre uymama için seminer kanıtı). 1010: 8 yaş/yapısal bisiklet yolu/gözetmen (en az 16 yaş "insbesondere") StVO §2 ile uyumlu.

## gunluk

### magaza-acilis-saatleri-pazar-kapali-federal-kural (1102): küçük (ciddi bulgu kapandı)
- Bulgu — doğruluk: Kartın dayandığı iki hukuki cümle doğru ve canlı metinle birebir: GG md. 74 Abs. 1 Nr. 11 "ohne das Recht des Ladenschlusses" ve md. 125a Abs. 1 "gilt als Bundesrecht fort. Es kann durch Landesrecht ersetzt werden." Eyalet adı/saati yok; LadSchlG saatleri tamamen çıktı; "mağaza saati 06:00–20:00" gibi ulusal kural izlenimi kalmadı. İlk raporun ciddi bulgusu kapandı. Kaynak sayısı 2, claim'ler kaynak/quote uyumlu, bağlantılar md. 74 ve md. 125a.
- Bulgu — kalan kusurlar (küçük): (1) Başlıktaki sorunun cevabı "Hayır, ülke genelinde tek bir mağaza saati yoktur" ve "mağaza saatleri eyalete göre değişir" claim'lerle kanıtlanmıyor: 268 ve 264 yalnız yetkinin eyalette olduğunu ve eski federal hukukun eyalet hukukuyla **değiştirilebileceğini** söylüyor; eyaletlerin fiilen değiştirdiğini söylemiyor. Gerçekte doğru ama kaynaksız bir sonuç; summary için ayrı claim de yok. (2) "federal çerçeve" ve "125a maddesi" okuyucu için tanımsız: kartta Ladenschlussgesetz adı ve onun bu "devam eden federal hukuk" olduğu hiç geçmiyor, yani 125a cümlesi neyi anlattığını söylemiyor; ayrıca "sade Türkçe, jargonsuz" tercihine uymuyor. (3) İki adım okuyucuya bilgi vermiyor ("eyaletin düzenlemesine göre planla", "taşınırsan yeniden planla": dolgu, ikincisi kaynaksız tavsiye). (4) Pratik değer: kart Pazar günü alışveriş sorusunu cevaplamıyor (GG md. 140 koruması ve LadSchlG saatleri çıktı), yalnız yetkinin kimde olduğunu söylüyor. Kartı tutmak zararsız ama Türk okuyucuya yararı sınırlı; bölge paketinde asıl cevap verilecek.
- Kanıt: https://www.gesetze-im-internet.de/gg/art_74.html "das Recht der Wirtschaft (Bergbau, Industrie, Energiewirtschaft, Handwerk, Gewerbe, Handel, Bank- und Börsenwesen, privatrechtliches Versicherungswesen) ohne das Recht des Ladenschlusses, der Gaststätten, der Spielhallen, der Schaustellung von Personen, der Messen, der Ausstellungen und der Märkte;" ; https://www.gesetze-im-internet.de/gg/art_125a.html "Recht, das als Bundesrecht erlassen worden ist, aber wegen der Änderung des Artikels 74 Abs. 1 ... nicht mehr als Bundesrecht erlassen werden könnte, gilt als Bundesrecht fort. Es kann durch Landesrecht ersetzt werden."
- Düzeltme: Summary'yi kaynak sınırında kısa tut: "Almanya'da mağaza açılış-kapanış saatlerini düzenleme yetkisi eyaletlerdedir (Ana Yasa md. 74). Eski federal Ladenschlussgesetz yalnız eyalet kendi düzenlemesini koymadığı yerde yürürlüktedir; bu yüzden ülke genelinde tek bir saat kuralı varsayma." ("değişir" yerine "varsayma"). Adım 2'yi sil. Pazar/tatil koruması için kaynak 008 (GG md. 140) kart başına 2 kaynak kuralına takıldıysa bölge paketine bırakmak yerinde; kart tamamen bölge paketine de taşınabilir.

### resmi-tatiller-3-ekim-ve-eyalet-farki (1101): küçük
- Bulgu: Kart iki cümleye indi; her cümle 132 ve 262 ile kanıtlı (2 claim). Dolgu ve 2026 rakamları çıktı, valid_until gereksiz kalktı. is/403 ile çelişki yok (403 "yasal tatil günleri Werktag sayılmaz" diyor, 1101 sayım yapmıyor). Tek kusur: adım 1 "alışveriş planını buna göre yap" 3 Ekim'de mağazaların kapalı olduğunu ima ediyor; bu bilgi kartın kaynaklarında yok ve 1102 artık mağaza saatlerinin eyalet konusu olduğunu söylüyor.
- Kanıt: https://www.gesetze-im-internet.de/einigvtr/art_2.html "Der 3. Oktober ist als Tag der Deutschen Einheit gesetzlicher Feiertag"
- Düzeltme: "seyahat ve resmî işlem planını buna göre yap" ("alışveriş" çıkar).

### ab-disi-paket-gumruk-ve-kdv-150-euro-muafiyeti-kalkti (1104): küçük
- Bulgu: Düzeltmeler 251/252 ile uyumlu (canlı: "Bei bestimmten Sendungen ...", "Regelzollsatz", "ab 150 Euro ... inklusive der Portokosten", alkol/tütün "Höchstmengen"). Kalan: (1) Zoll sayfası kendi içinde iki biçimde söylüyor (üst kutu: "Paketsendungen bis zu 150 Euro ... für jede Warenkategorie 3 Euro"; alt bölüm: "bestimmte Sendungen"). Kart dar olanı seçmiş; "belirli gönderiler" hangileri, kaynak da söylemiyor, okuyucu kendi paketinin hangisi olduğunu anlayamıyor. Kaynak sınırı, kartın hatası değil; adım 2 "olabileceğini hesaba kat" bilgi vermiyor. (2) Not alanındaki "25.10.2026 tarihinde okunan sayfalarına dayanır" iç not tadında ama kural 6 gereği tarih yazmak istenmişti; "Zoll sayfalarına göre (25.10.2026)" biçimi daha doğal. valid_until 2026-10-31 doğru.
- Kanıt: https://www.zoll.de/DE/Privatpersonen/Postsendungen-Internetbestellungen/Sendungen-aus-einem-Nicht-EU-Staat/Zoll-und-Steuern/Internetbestellungen/internetbestellungen_node.html "Bei bestimmten Sendungen mit einem Wert bis 150 Euro wird seit dem 1. Juli 2026 ein Pauschalzollbetrag von drei Euro je Ware (das bedeutet pro Position der Zollanmeldung) erhoben."
- Düzeltme: Adım 2'yi "150 Euro'ya kadar paketlerde Zoll mal kategorisi başına 3 Euro sabit gümrük uygulayabiliyor; bazı gönderilerde normal tarife geçerli" biçiminde nötr yaz; not: "Zoll sayfalarına göre (25.10.2026 itibarıyla)".

### almanca-kursu-integrationskurs-ucret-ve-berufssprachkurs (1107): orta
- Bulgu: Not'a eklenen "oturum belgesi şartı yalnız Integrationskurs hakkı içindir" cümlesi BAMF BSK sayfasında yok. Sayfa BSK'nın kime açık olduğunu söylüyor (Drittstaaten, EU, Deutsche mit Migrationshintergrund) ve sprachliche Voraussetzungen sayıyor; oturum durumu için hüküm kurmuyor. Cümle BSK'ya girmek için oturum belgesi aranmadığı izlenimi veriyor. Kaynaksız kural; okuyucu (ör. Duldung/Gestattung durumundaki biri) yanlış beklenti kurabilir.
- Kanıt: https://www.bamf.de/DE/Themen/Integration/ZugewanderteTeilnehmende/DeutschBeruf/deutsch-beruf-node.html "BSK richten sich an Zugewanderte aus Drittstaaten, Bürgerinnen und Bürger aus der EU und Deutsche mit Migrationshintergrund."
- Düzeltme: Note'u "BSK; üçüncü ülkelerden gelenlere, AB vatandaşlarına ve göçmen kökenli Almanlara açıktır." ile bitir; "oturum belgesi şartı yalnız ..." kısmını sil.

### almanca-kursu-integrationskurs-ucret-ve-berufssprachkurs (1107): küçük
- Bulgu: Kartın BSK ön şartı "Integrationskurs'u bitirmiş olman ya da en az B1" diyor ve "kurs hedefine göre daha düşük düzeyler de kabul edilebilir". Aynı BAMF sayfası A2 ve B1 hedefli BSK için ters yönde ek şart koyuyor: bu kurslara yalnız Integrationskurs'a rağmen B1'e ulaşamayanlar girebilir. Okuyucu "B1 belgemi gösteririm, B1 hedefli BSK'ya girerim" diye anlayabilir. Ayrıca A2 hedefli BSK şu an verilemiyor (not'ta var).
- Kanıt: https://www.bamf.de/DE/Themen/Integration/ZugewanderteTeilnehmende/DeutschBeruf/deutsch-beruf-node.html "Für die Kurse mit Ziel A2 und B1 gelten bestimmte Zugangsvoraussetzungen. Sie können diese Kurse nur besuchen, wenn Sie trotz Teilnahme am Integrationskurs nicht das Sprachniveau B1 erreicht haben."
- Düzeltme: Adım 7'ye: "A2 ve B1 hedefli BSK'ya yalnız Integrationskurs'a katılıp B1'e ulaşamadıysan girebilirsin".

### acil-durum-112-ve-nobetci-doktor-116117 (1106): küçük
- Bulgu: Düzeltmeler doğru ("110 veya" ve "konuşmayı sen bitirme" çıktı, sıra duruma bağlı). saglik/605 ile hâlâ büyük ölçüde aynı soru: 112 ücretsiz, 116117 ön eksiz/ücretsiz/24 saat/kamu ve özel sigortalı, "nereye gideceğini söyler, gerekirse doktoru evine gönderir" iki kartta da var; çelişki yok (112 hayati tehlike, 116117 muayenehane kapalı ve ertesi güne bekleyemeyen). 605 ek olarak hastane acili ve nöbetçi eczane, 1106 ek olarak Notruf-Fax/nora. Editör "paket kararı" diye bıraktı.
- Kanıt: https://www.116117.de/de/aerztlicher-bereitschaftsdienst.php (1106 kaynağı 143) ve 605 summary: "Muayenehaneler kapalıyken ... nöbetçi hekim hizmeti (ärztlicher Bereitschaftsdienst) devrededir: 116117'yi ara"
- Düzeltme: Orkestratör kararı: ya 1106'yı "112'de ne söylenir + Notruf-Fax/nora" ile sınırla ve 116117'yi 605'e bırak, ya iki kartı birleştir. İçerik hatası yok.

## Çalışma, sağlık ve resmî kartlarla çapraz kontrol özeti
- gunluk/1106 ↔ saglik/605: olgusal çelişki yok; tekrar sürüyor (yukarıda).
- gunluk/1101 ↔ is/403: çelişki yok, tekrar yok (1101 artık sayım/Werktag anlatmıyor).
- aile/908 ↔ saglik/602: yaş sınırları (18/23/25) ve Bezugsgröße/Jahresarbeitsentgeltgrenze karşılıkları artık aynı; **tek fark** §10 Abs. 3 kapsamı (908 "diğer ebeveyn", 602 "çocuğun anne/babası olan eş"): 908'de hata (yukarıda orta).
- aile/908 ↔ resmi/209: Standesamt 1 hafta, hastane doğumunda kurum bildirimi ortak; çelişki yok; 908'de özne eksikliği (küçük).
- ulasim/1008 ↔ resmi/208 (araç kaydı kartı): ortak yalnız "Kfz-Steuer bir yıl peşin"; ikisi kaynakla tutarlı. 208 "duruma göre geçerli HU"; 1008 HU aralıkları (36/24; motosiklet 24) farklı konu. Çelişki yok.

## Claims notu
Editörün eklediği claim'lerde quote–iddia uyumu: tamamı iddiayı kanıtlıyor. İstisnalar: aile/907 "Bürgergeld'in yeni adı Grundsicherungsgeld" claim'i (quote yalnız "Grundsicherungsgeld ergänzen (aufstocken)"; "Bürgergeld'in adı" eşleştirmesi kaynakta yok; karttaki ifade "bu yardım Grundsicherungsgeld adıyla da geçiyor", kabul edilebilir ama claim metni kanıtın ötesinde); aile/906 "ödenecek miktar değildir" (quote "Als monatlicher Bedarf gelten" ihtiyaç kavramını kanıtlıyor, 'ödenecek değil' sonucunu kanıtlamıyor; yasa mantığına uygun, kabul edilebilir). gunluk/1102 summary'nin "saatler eyalete göre değişir" cümlesi için claim yok.
