# Almanya ulusal paketi v1 — açık konular (2026-10-25)

Kapsam: 113 kart, 11 konu, 2120 iddia, 193 kaynak. Süreç: keşif → add_sources → yazar → pack_check → bağımsız denetim → editör → dar denetim → kısa editör. Son dar denetimlerde ciddi bulgu 0 (grup 0: 0/2/15, grup 1: 0/6/19, grup 2: 0/7/12, grup 3: 0/5/13 ciddi/orta/küçük); kısa editör turlarından sonra kalan orta bulgular aşağıda konu başlıklarında.
Kural: şehir yazarı bu boşlukları kendi bilgisinden doldurmaz; kaynaklı ek kart ya da bölge/şehir katmanı yazar.

## Tarihe duyarlı kartlar (valid_until)
- 2026-10-31: ab-disi-paket-gumruk-ve-kdv-150-euro-muafiyeti-kalkti
- 2026-12-31: mavi-kart-ab-sartlari
- 2026-12-31: gelir-vergisi-2026-grundfreibetrag-dilimler
- 2026-12-31: maas-sosyal-sigorta-kesintileri-2026
- 2026-12-31: maas-bordrosu-haklari-ve-2026-prim-ust-sinirlari
- 2026-12-31: minijob-midijob-2026-sinirlari-ve-sigorta
- 2026-12-31: saglik-ve-bakim-sigortasi-primi-2026-oranlari
- 2026-12-31: bakim-sigortasi-pflegegrad-basvurusu-pflegegeld
- 2026-12-31: wbs-sosyal-konut-belgesi-ve-wohngeld-kira-yardimi
- 2026-12-31: ogrenci-vizesi-sperrkonto-992-euro-2026
- 2026-12-31: deutschlandticket-fiyat-kapsam-iptal
- 2026-12-31: almanca-kursu-integrationskurs-ucret-ve-berufssprachkurs
- 2027-12-31: asgari-ucret-2026-2027

## Erişim ve kaynak sınırları
- Kapalı siteler (bu ağdan): bmi.bund.de (HTTP 400), bund.de ve bzr.bund.de (TLS), bmftr.bund.de (bağlantı). make-it-in-germany.com ve auswaertiges-amt.de içeriği JavaScript ile yüklediği için kopyada metin kalmıyor; kullanılmadı. eur-lex bot korumalı (AB tüzük metinleri kanıtsız). Ayrıntı: _is/kesif/erisim_ozet.md
- 2026 Mavi Kart euro maaş eşikleri hiçbir açık resmî HTML sayfada bulunamadı (Bundesagentur bülteni soft-404); kartta yalnız yüzdeler var.
- de:kaynak:265 (SGB V tam metin) 3 MB gövde sınırında kesik; kullanılan §5/§6/§9 kopyada var.
- Kart başına 2 kaynak sınırı yüzünden yazılamayan bilgiler, v2 için ayrı kart adayı: Abschlag (aylık ön ödeme), Mutterschaftsgeld, Pflegegrad 1–5, Elternzeit, Elterngeld yabancı ebeveyn şartı, Wohngeld yabancı hakkı, §656c satışta emlakçı komisyonu, Bürgergeld/Grundsicherung aylık tutarı, EStG §62 eğitim istisnası, euro ve yaz saati, ilk hafta banka ve sağlık kasası seçimi, Türkiye'de doğan çocuğun kaydı, Werktag/Cumartesi açıklaması.

## Bölge (eyalet) paketine giden konular
Eyalet tatilleri, Kirchensteuer oranı ve çıkış usulü, Grunderwerbsteuer oranı, Mietpreisbremse geçerlilik alanı, okul sistemi ve tatil takvimi, Kita ücretleri ve kayıt yolu, mağaza açılış saatleri (eyalet yasaları), WBS gelir sınırları, eyalet aile ödemeleri, Zulassung/HU ücretleri, U muayenesi zorunluluğu, Widerspruch'un kaldırıldığı eyaletler. Şehir katmanı: Ausländerbehörde/Bürgeramt randevu ve adres, Verkehrsverbund tarifeleri, belediye atık ve su tarifeleri, Kita portalı.

## Orkestratör kararları
## para (yazar sonrası, 25.10.2026)
- Kart başına 2 kaynak sınırı korunur (İspanya kuralı). Kart 8/9/10'da sığmayan bilgiler (bakım sigortası oranı, Soli, Hausrat, 5 yıl bekleme süresi) karta eklenmez; `acik_konular.md`'ye gider.
- Kart 2: de:kaynak:026 metninde Lastschrift geri alma süreleri (8 hafta Basislastschrift, 13 ay yetkisiz) VAR; editör turunda kaynak zaten kartın listesinde → eklenebilir (claim ile).
- Kart 3: %42 ve %45 formül katsayısından alındı (0,42 • x). Denetçi bunu değerlendirsin; kaynakta oran yüzde olarak yazılmıyorsa "formüle göre" ifadesiyle kalabilir ya da çıkarılır.
- Kart 11: başlık "Schufa gibi kredi bilgi kuruluşları"; kaynakta Schufa adı yok. Kabul.

## resmi (yazar sonrası)
- Kart 9/10 kaynağı 098 (tuerkei.diplo.de) 2018 tarihli parçalar içeriyor ve Aile Cüzdanı konusunda kendi içinde çelişiyor; denetçi canlı sayfayla güncelliğe baksın.
- Türkiye'de doğan çocuğun kaydı (098) ayrı kart adayı; v2'de düşünülür.

## fatura / is (yazar sonrası)
- 2 kaynak sınırı korunur. Fatura: Abschlag (StromGVV §13) kart 502'ye girmedi → v2'de "aylık ön ödeme (Abschlag) nedir" ayrı kart adayı. Rundfunk muafiyet ayrıntıları (tireli cümleler) açık konu.
- İş: Kart 3'te "federal düzeyde yalnız 3 Ekim" cümlesi kaynak sınırına takıldı; kart 4 Lohnsteuer ve işsizlik primi oranını içermiyor; kart 8 yabancı hak şartı (SGB II §7) yok → açık konular. eAU anlatılmadı.

## ev (yazar sonrası)
- Yabancıların Wohngeld hakkı (WoGG §3, kaynak 171) karta girmedi → v2 aday: ayrı Wohngeld kartı ya da editörde 169 yerine 171.
- §656c (satışta emlakçı komisyonu) ayrı kart adayı. Mietpreisbremse muafiyetleri/30 ay iade açık konu.
- Kart 4 (Betriebskosten) ile fatura/503 (Nebenkostenabrechnung) örtüşme riski: birleştirmede denetçi/editör bakacak.

## para (editör sonrası)
- Yıllık beyanname kartı valid_until 2026-07-31 (geçmiş): şehre uygulamada "stale" sayılır. ELSTER 2026 yılı sayfası eklenip kart yenilenmeli (v2).
- de:kaynak:202 (SGB VI §235 tek madde) hiçbir kartta kullanılmıyor; pack_build yalnız kullanılan kaynakları alır, sorun yok.
- Emeklilik kartına 5 yıl bekleme süresi girdi (203 ile sığdı); kabul.

## planlama (yazar sonrası)
- Kart 9'da euro (199) ve yaz saati dönemi (198) sığmadı; kart 3'te Basiskonto/Krankenkasse seçimi sığmadı; kart 7'de GKV'ye geçiş yok → v2 aday kartlar: "ilk hafta: banka ve sağlık kasası seçimi", "euro ve yaz saati".

## ev (editör sonrası)
- 701'e "ayın başında bildir" önerisi kaynaksız eklendi → dar denetimde bakılacak (kaynaksız tavsiye ise silinir).
- 703 Mietpreisbremse: §556d yerine BMJ 2022 özeti; 31.12.2029 bitişi karttan çıktı, valid_until null. v2'de §556d geri alınıp 2029 tarihi yazılabilir.

## is (editör sonrası)
- Bürgergeld/Neue Grundsicherung kartında Regelsatz tutarı yok (563 Euro kaynağı 2 kaynak sınırına takıldı; 1.7.2026 sonrası tutar zaten doğrulanmamıştı) → v2'de ayrı "aylık tutar" kartı. Kabul.

## saglik (editör sonrası)
- de:kaynak:265 (SGB V tam metin) 3 MB gövde sınırında kesildi (truncated); kullanılan §5/§6 baştaki bölümde, alıntılar kopyada var. Kopya tam yasa değil; açık konuya yazılır.
- Mutterschaftsgeld (§24i) ve Pflegegrad 1-5 (§15) ayrı kart adayı (v2). para/308'de bakım sigortası kalemi eksik → dar denetim g1b bakacak.

---
# Konu: oturum (yazar ve editör notları)

# oturum konusu: yazar boşlukları (25.10.2026)

15 aday kartın 15'i yazıldı (order 101-115). Kart 10 (Ortaklık Hukuku) yalnız kaynağın söylediği kadar yazıldı (kademe ve standstill yok), ertelenmedi.

## Kart bazında yazılmayan bilgi
- Kart 2 (Türk vatandaşı ulusal vize): başvurudan karara işlem süresi yazılmadı. 041 sayfasındaki "mindestens 15 Tage (in Einzelfällen bis zu 45 Tage)" ifadesi aynı sayfada Schengen başvuru akışı içinde geçiyor ve ulusal vize için ayrılmadığından alınmadı. Yazılan süre yalnız randevu bekleme süresidir (kayıttan başvuruya). Ücret 75 Euro (AufenthV md. 46); sayfadaki "max. 90 EUR" ibaresi yazılmadı. iDATA 12 Euro randevu bedeli (042) kart başına 2 kaynak sınırı nedeniyle alınmadı. Tarihe duyarlı (ücret, bekleme): valid_until null (kaynakta bitiş yok).
- Kart 3 (Mavi Kart): 2026 euro eşikleri elimizdeki kaynaklarda yok (Bundesagentur 03-2026 bülteni listede değil, BMI sayfası kapalı). Tutar yazılmadı; yalnız yasadaki yüzdeler (%50 ve %45,3) ve Bundesanzeiger ilanı kuralı yazıldı. Eşik euro olarak bulunursa karta eklenmeli ve valid_until 2026-12-31 yapılmalı. Şimdilik null.
- Kart 4 (Chancenkarte puan tablosu): tam metin sayfasındaki Anlage tablosu satır satır bölünmüş geldiği için ölçüt başına puan değerleri yazılmadı; yalnız asgari puan (6) ve puan veren ölçütlerin kendisi yazıldı. Puan değerleri istenirse tablo sayfası ayrıca düzenlenmeli.
- Kart 6 (aile birleşimi): Türk vatandaşına özgü Almanca muafiyeti kaynakta yok, yazılmadı. Konsolosluğun 12 aylık sertifika kuralı, A1 ve 75 Euro Merkblatt 01F'den. 040 (A1 sağlayıcı sınırlaması) ve AufenthV md. 46 kart başına 2 kaynak sınırı nedeniyle kullanılmadı. Ücret tarihe duyarlı: valid_until null.
- Kart 8 (vatandaşlık): eski vatandaşlıktan çıkma şartının kalktığı StAG md. 10(1) Nr. 4 "weggefallen" olarak görünüyor ama hükmün içeriği metinde yok; yazılmadı. Çoklu vatandaşlık yalnız BVA ifadesiyle ve "Almanların başka vatandaşlık edinmesi" bağlamı belirtilerek yazıldı. Türkiye'nin çifte vatandaşlık kuralı kapsam dışı. 3 yıllık hızlı yolun kaldırıldığı bilgisi (haber özeti) kullanılmadı.
- Kart 10 (Ortaklık Hukuku): ARB 1/80 kademeleri, Katma Protokol md. 41 standstill ve hakkın kimde doğduğu kaynakta yok, yazılmadı. Yazılan: AufenthG md. 4(1)-(2) (hak varsa Aufenthaltserlaubnis ile belgeleme, başvuru üzerine) ve AufenthV md. 52a (ücret Alman kimlik kartı ücreti düzeyinde; 24 yaş altında o yaşa ait kimlik ücreti). Kimlik kartı ücretinin euro tutarı kaynakta yok.
- Kart 11 (oturum belgesi ücretleri): eAT'nin PIN mektubu ve Express ücreti (md. 45a: +35 Euro) kaynak listesinde yok, yazılmadı. BAMF eAT sayfası (049) ve md. 52a (048) kart başına 2 kaynak sınırı nedeniyle bu kartta kullanılmadı; 048 kart 10'da kullanıldı. Kart eAT'yi adıyla değil "oturum belgesi" olarak anlatıyor (md. 45c metni "Dokument nach § 78 Absatz 1" diyor). Ücretler tarihe duyarlı: valid_until null.
- Kart 13 (serbest çalışan): başvuru belge listesi kaynakta yok, yazılmadı. 250.000/500.000 Euro ve 5-10 kişi istihdam eşikleri güncel md. 21'de yok, yazılmadı.
- Kart 14 (AB vatandaşı aile üyesi): kart başına 2 kaynak sınırı nedeniyle 056 (md. 2a: AB'li olmayan aile üyesi için vize gerekir, vize ücretsiz, Aufenthaltskarte sahibi vizeden muaf) kullanılmadı; kartın pratik değeri için ana döngü kart kaynaklarını 055+056 ya da 3 kaynağa çıkarmayı değerlendirebilir.
- Kart 12 (iş değişikliği): çalışanın kendi bildirim yükümlülüğü kaynakta yok; yalnız işverenin 4 haftalık bildirimi (md. 4a(5)) yazıldı.
- Kart 15 (§ 51): Türk vatandaşına özgü Ortaklık Hukuku (ARB 1/80 md. 7) kapsamındaki daha uzun yokluk tanımı kaynakta yok, yazılmadı.

## Kullanılmayan kaynaklar
- 040 (de:kaynak:040, Merkblatt: A1 sağlayıcıları), 042 (de:kaynak:042, Türk vatandaşı iDATA yolu), 056 (de:kaynak:056, FreizügG md. 2a), 049 (de:kaynak:049, BAMF eAT), kart başına 2 kaynak sınırı nedeniyle claim için kullanılmadı. 030 (AufenthG md. 7) de kullanılmadı (kart 1'de 029 ve 031 tercih edildi; "Aufenthaltserlaubnis süreli" bilgisi karta yazılmadı).

## Dikkat notları
- Karta yazılan 15 kartın 4'ü tarihe duyarlı (kart 2, 3, 6, 11); kaynaklarda bitiş tarihi olmadığı için valid_until.json'da null.
- Kart 4: puan veren ölçütler özetlendi; puan değerleri ve ölçüt başına ayrıntı kartta yok.
- Kart 1 ve 10: AB–Türkiye Ortaklık Anlaşması yalnız md. 4'ün metniyle anıldı.
- Kart 5: haftalık iş günü hesabı (2,5 gün) md. 16b(3) Nr. 2 metnine göre özetlendi; ayrıntılı yorum yok.

## Editör turu (G0, 25.10.2026)
- Yeni kaynaklar (snap_oturum-editor1): de:kaynak:204 (PAuswGebV § 1: kimlik kartı ücreti 46 Euro / 24 yaş altı 27,60 Euro; Ortaklık kartı), de:kaynak:205 (SVBezGrV 2026 § 4: yıllık prim tavanı 101.400 Euro; Mavi Kart kartı).
- Mavi Kart (kart 3): 2026 euro eşikleri hâlâ elimizdeki kaynaklarda yok; yalnız yüzdeler ve 2026 prim tavanı yazıldı. Euro karşılığı hesaplanmadı.
- Ortaklık Hukuku (kart 10): kart başına 2 kaynak sınırı için AufenthG § 4 (de:kaynak:029) karttan çıkarıldı; "hakkı Aufenthaltserlaubnis ile belgele" bilgisi oturum-belgesi-turleri kartında duruyor. oturum-belgesi-ucretleri kartında Ortaklık Hukuku ücret uyarısı, üçüncü kaynak (de:kaynak:048) gerektirdiği için eklenemedi.
- Vatandaşlık (kart 8): Almanya'ya naturalize olan yabancı için çifte vatandaşlık (Türk vatandaşlığından çıkma gerekir mi) açıkça anlatan bir resmî Alman sayfası kaynak dizininde yok; karta yazılmadı. BVA notu ters yönlü olduğu için silindi (de:kaynak:053 kartta kullanılmıyor).
- Eş birleşimi (kart 6): AB Adalet Divanı Dogan kararı (Türk işçilerin eşleri için A1 şartı) kaynak dizininde yok; yazılmadı.
- AB vatandaşı aile üyesi (kart 14): sıradan Alman vatandaşının yabancı eşi için ayrı kural (§ 28) üçüncü kaynak gerektirdiği için bu kartta anlatılmadı; yalnız Alman serbest dolaşım hakkını kullananların aile üyelerinin kapsama girdiği yazıldı.
- Çalışanın kendi bildirim yükümlülüğü ve işveren bildirimi: iş değiştirme kartından işveren bildirimi cümlesi çıkarıldı (okuyucuya yönelik değil).

## Editör turu G0b (25.10.2026) - açık kalanlar
- oturum-belgesi-ucretleri: Ortaklık Hukuku (Assoziationsberechtigte) kapsamındaki okuyucu için ücretin farklı olduğu (AufenthV §52a: Alman kimlik kartı ücreti) uyarısı bu kartta yok. Kartın kaynakları 046 ve 047 (2 kaynak sınırı); 047 çıkarılırsa 67 Euro bilgisi düşer, §45c bilgisinin ayrı karta taşınması karar gereği yapılmadı. Çözüm yolu: ana döngü kararıyla kaynak değişikliği.
- ab-vatandasi-turk-aile-uyesi-oturum-karti: Alman vatandaşının sıradan eşi için nereye bakılacağı (AufenthG §28) bu kartın kaynaklarında yok; es-icin-aile-birlesimi-vizesi kartı §28'i anlatıyor.
- es-icin-aile-birlesimi-vizesi: Nüfus Kayıt Örneği için konsolosluk (apostil istemeyen Merkblatt) ile Alman makamları (apostil) ayrımı kaynakta açık değil.
- alman-vatandasligi-sartlari: StAG §12a (de:kaynak:269) eklendi; yabancı mahkeme kararlarının değerlendirilmesi (§12a Abs. 2) kartta yazılmadı.

---
# Konu: resmi (yazar ve editör notları)

# resmi: yazılmayan bilgiler, kullanılmayan kaynaklar, dikkat notları (yazar, 2026-10-25)

12 kart, kart başına en çok 2 kaynak. Tarihe duyarlı kart: yalnız Führungszeugnis (ücret; kaynakta bitiş tarihi yok, valid_until null).

## Kart bazında yazılmayan bilgi
- Kart 1 (adres kaydı): randevu usulü, kayıtta istenen belgeler (pasaport, kira sözleşmesi) ve ofisin adı kaynakta yok; yalnız "adı şehre göre değişir" yazıldı.
- Kart 2 (Meldebescheinigung/Abmeldung): yazılı belgenin ücreti federal yasada yok (eyalet). Şehir içi taşınma için ayrı bildirim usulü yok; yalnız "Wohnung bezieht" çerçevesi var.
- Kart 3 (Steuer-ID): Almanya'ya gelince ilk IdNr mektubunun ne zaman geldiği kaynakta yok; başlık "nasıl gelir" yerine "bulma ve yeniden talep" olarak daraltıldı. BZSt telefon numarası ve saatleri kasten yazılmadı.
- Kart 4 (Versicherungsnummer): "Renteninformation" yazıları ve yeni gelen biri için numaranın nasıl alındığı (işveren/DRV) kaynakta yok.
- Kart 5 (eID): BundID kuruluş adımları kaynakta yok (id.bund.de JavaScript). 16 yaş altı için eID kapalı kuralı PAuswG §10'da var (86 numaralı kaynak, kart 5 listesinde) ama eAT'ye "entsprechend" uygulanması açık yazılmadığı ve kart başına 2 kaynak sınırı olduğu için yazılmadı.
- Kart 6 (apostil/tercüme): Almanya'da düzenlenen belgeye Türkiye için apostil veren Alman makamı kaynakta yok. "beglaubigte Übersetzung" hukuki tanımı ve tercüman ücreti yok. Türkiye tarafında apostil makamı (Kaymakam/Vali) tuerkei.diplo.de sayfasında VAR olduğu için yazıldı (görev notu bunu kaynakta yok sanıyordu).
- Kart 7 (Beglaubigung/noter): hangi durumda noter hangisinde kurum onayı gerektiği ve noter ücreti yok. Kurumların yetkisi "Landesrecht" diye geçtiği için yalnız bu ifade kullanıldı.
- Kart 8 (araç): Zulassungsstelle adı, tescil ücreti, HU periyotları, Kfz-Steuer tutarı yazılmadı (yerel/eyalet; HU periyodu için kaynak yok, tutar için Zoll Steuerhöhe sayfası denenmedi).
- Kart 9 (doğum): Standesamt ücreti yerel. Türkiye'de doğan çocuğun Alman doğum kaydı (Auslandsgeburt; Formül A tanınır, nachträgliche Beurkundung zorunlu değil, 60 EUR imza onayı vb.) tuerkei.diplo.de sayfasında var ama bu kart Almanya'da doğuma ayrıldığı ve kart başına 2 kaynak olduğu için yazılmadı; ayrı bir kart (Türkiye'de doğan çocuğun kaydı) olabilir.
- Kart 10 (evlilik): Türk tarafında Ehefähigkeitszeugnis'in Türkiye'den nasıl alınacağı kaynakta yok (belge "ülkesinin makamından" diye yazıldı). Görev notu "evlilik tanıma usulü kaynakta yok" demişti; tuerkei.diplo.de sayfasında Türkiye'de yapılan medeni nikâhın usul gerekmeden tanındığı ve Nachbeurkundung'un zorunlu olmadığı açıkça yazıyor, kaynağa dayanarak yazıldı.
- Kart 11 (Führungszeugnis): geçerlilik süresi (099: "Es gibt keine Vorschriften zur Dauer der Gültigkeit") ve teslim süresi (resmî rakam yok) yazılmadı. Gebührenbefreiung koşulları Merkblatt'ta (kaynakta yok). Banka hesabı/IBAN gibi yurt dışı havale ayrıntıları kasten yazılmadı.
- Kart 12 (Widerspruch): alan bazlı farklar (sosyal güvenlik SGG §84, vergi AO §355), Widerspruchsverfahren'in birçok eyalette kaldırılması ve VwVfG §79 kaynakta yok; kart yalnız VwGO çerçevesini anlatıyor ve "VwGO'ya göre" diye sınırlandı.

## Kullanılmayan kaynaklar
- de:kaynak:086 (PAuswG): kart 5'e atanmıştı; yukarıdaki nedenle kullanılmadı.
- de:kaynak:096 (KraftStG §1): kart 8 için en kapsayıcı iki kaynak 095 (bmv.de) ve 100 (Zoll) seçildi; 096 ve 101 (Zoll "Beginn und Ende der Steuerpflicht") kullanılmadı.
- de:kaynak:099 (BfJ SSS): kart 11'de 094 ve 092 seçildi (Avrupa belgesi için BZRG §30b gerekli).
- de:kaynak:098 kart 9'da kullanılmadı (kart 6 ve 10'da kullanıldı).
- İkincil kaynak (verbraucherzentrale/handbookgermany) kullanılmadı.

## Dikkat notları
- tuerkei.diplo.de sayfası (098) Türkiye'deki Alman temsilciliklerinin; sayfa içinde 05.04.2018 tarihli bir alt makale var, ana metin tarihsiz. Kart 6 ve 10 tarihe duyarlı sayılmadı (valid_until'a konmadı) ama güncelliği editör gözüyle kontrol edilmeli.
- 098 kendi içinde çelişiyor: Aile Cüzdanı için bir yerde "Almanya tanımıyor", başka yerde "yalnızca apostil ve yeminli tercümeyle tanınır" deniyor. Kart 10 yalnızca "tanınmıyor" ifadesini alıntıladı; kart 6'da Aile Cüzdanı anılmadı.
- Kart 11 ücreti (13,00 EUR) BfJ sayfasında tarihsiz; "güncel tarifeye göre" diye yazıldı. Sayfa "1 Ekim 2026'dan beri dijital sürüm" diyor (bu karttaki tek tarihli iddia).
- Kart 11 notu "Türk vatandaşları dahil" ibaresi: BZRG §30b "Drittstaatsangehörige" der; Türkiye AB üyesi olmadığı için bu gruba girer (kaynağın kendisi Türkiye'yi anmıyor).
- Kart 8: ZB I/ZB II tarihleri (01.01.2015 / 01.01.2018) bmv.de'nin i-Kfz koşullarıdır, bitiş tarihi değildir.
- Kart 6/9/10/12: eyalet adı veya şehir adı yazılmadı; Oberlandesgericht ve Amtsgericht genel mahkeme adı olarak geçiyor.

## Editör turu (2026-10-25, denetim G0)
- Kart 10 (evlilik): Aile Cüzdanı için 098'in iki ifadesi de artık kartta (atıfla). Anerkennungsbescheid belge listesine eklendi; kararı hangi eyalet idaresinin vereceği sayfada yalnız "zuständige deutsche Landesjustizbehörde" diye geçiyor.
- Kart 12 (Widerspruch): "birçok eyalette itiraz aşamasının kalktığı", vergi (AO) ve sosyal yardım (SGG) işlemlerinin ayrı usulü VwGO metninde yok; kapsam cümlesi yalnız VwGO §40'a (federal yasayla başka mahkemeye verilmiş alanlar) dayandı. Dava süresi (itiraz gerekmiyorsa işlemin bildiriminden bir ay, §74) ve VwVfG §3a elektronik biçim (088 ikinci kaynak yapıldı) eklendi.
- Kart 7 (Beglaubigung): BGB §129 istisnası karta yazıldı; bu tür imzada hangi makamın yetkili olduğu (noter) kaynaklarda yok, yazılmadı.
- Kart 11 (Führungszeugnis): Gebührenbefreiung'un hangi durumlarda verildiği (örneğin gönüllü çalışma) karttaki iki kaynakta yok; yalnız muafiyet başvurusu ve kanıt şartı yazıldı. Yazılı Meldebescheinigung'un ücreti yok (kart 2).
- Kart 6 (apostil): sayfanın tarihi belirsiz olduğundan valid_until konmadı (kaynakta bitiş tarihi yok).
- Kart 5 (eID): eID'nin genel çevrim içi hizmetlerdeki kapsamı karttaki kaynaklarda yalnız i-Kfz ile sınırlı; kart eID'nin tanımını verir, ek daraltma yapılmadı.

## Editör turu G0b (25.10.2026) - açık kalanlar
- turkiye-belgesi-almanyada-apostil-ve-yeminli-tercume: tercüme kuralı kaynakta yalnız Nüfus Kayıt Örneği ve evlenme bildirimi için var; diploma, mahkeme kararı gibi belgeler için kaynak yok.
- resmi-yaziya-itiraz-widerspruch-sure-ve-sonraki-yol: VwGO'nun kapsamadığı alanların (ör. hangi yazılar) listesi kaynakta yok; itiraz aşamasının hangi işlemlerde bulunduğu ilgili yasaya bağlı, eyalet farkı kaynakta yok.

---
# Konu: para (yazar ve editör notları)

# para - yazar notları (25.10.2026)

Çıktı: 12 kart (order 301-312), 164 claim, 21 bağlantı. pack_check çıkış 0.

## Ana döngünün karar vermesi gereken noktalar (kart başına en çok 2 kaynak sınırı yüzünden)
- Kart 8 (maas-sosyal-sigorta-kesintileri-2026): kaynaklar DRV 02.01.2026 (de:kaynak:018) + BMG Beiträge und Tarife (de:kaynak:028). Kartta emeklilik %18,6 (işçi %9,3), işsizlik %2,6 (işçi %1,3), sağlık genel oranı %14,6, ortalama ek prim %2,9 (2026), yarı yarıya paylaşım var. SIĞMAYANLAR: bakım sigortası %3,6 / çocuksuz %4,2, işçi %1,8, "seit 1. Januar 2025" (de:kaynak:025) ve Solidaritätszuschlag %5,5 + muafiyet sınırı 20.350/40.700 euro (de:kaynak:010, 011). İstenirse bunlar ayrı bir kart olur (ör. bakım sigortası + Soli) ya da kart 8 için 3 kaynak izni verilir. Not: sağlık sigortası genel oranı artık kart 8'de 028 kaynağıyla yazıldı (SGB V §241 gerekmedi).
- Kart 9 (zorunlu-arac-sigortasi-ve-ozel-sorumluluk-sigortasi): kaynaklar PflVG §1 (012) + BaFin Haftpflicht (019). SIĞMAYAN: BaFin Hausratversicherung (020: Hausrat isteğe bağlı, Neuwert, Wohnflächenmodell vb.). Kfz-Haftpflicht teminat tutarları kaynakta yok, yazılmadı.
- Kart 10 (almanya-emeklilik-yasi-bekleme-suresi-turkiye-anlasmasi): kaynaklar SGB VI §35 (013) + DRV Verbindungsstelle Türkei (021). SIĞMAYANLAR: SGB VI §50 genel bekleme süresi 5 yıl (014) ve DRV Sozialversicherungsabkommen genel sayfası "Türkiye için kısıtlamalar" notu (022). Kartta "bekleme süresi (Wartezeit)" var ama 5 yıl rakamı yok. Kademeli yaş geçişi (SGB VI §235) kaynaklarda yok: kart yaşı "SGB VI §35'e göre 67" diye yazıyor, doğum yılı geçişlerini anlatmıyor (eski doğum yıllarında 67'den düşük yaş olabileceği kartta söylenmiyor). İstenirse 014 ile kart 10 değiştirilir ya da 3 kaynak izni verilir.

## Keşif notundan farklı çıkan nokta
- Kart 2: Lastschrift geri alma süresi talimat gereği yazılmadı. Ancak Bundesbank SEPA SSS metninde (de:kaynak:026) şu cümleler VAR: "Eine SEPA-Basislastschrift kann innerhalb von acht Wochen nach Belastung ohne Angabe von Gründen an den Einreicher zurückgegeben werden" ve "Ein Lastschrifteinzug ohne Mandat ... kann bei beiden Verfahren vom Zahler innerhalb von 13 Monaten nach der Kontobelastung zurückgegeben werden". Ana döngü isterse karta eklenir (kaynak zaten kartın source_ids'inde).

## Kart bazında yazılmayan bilgi
- Kart 1 (basiskonto): ücret tutarı yazılmadı (kaynak yalnız "angemessen" diyor).
- Kart 2 (iban-sepa): Echtzeitüberweisung zorunluluk tarihleri (09.01.2025 alma, 09.10.2025 gönderme) ve Empfängerüberprüfung pazar tarihleri kartta yok; ücret tutarı yok.
- Kart 3 (gelir vergisi): iki formüllü dilimin (12.349-17.799 ve 17.800-69.878 euro) hesap formülleri yazılmadı; "%42/%45" kanundaki 0,42 • x ve 0,45 • x formül katsayılarından alındı (kanun metni "oran" demiyor, formül veriyor). Soli ve vergi sınıfları ayrı kartlarda.
- Kart 4 (vergi sınıfı): sınıf değiştirme tarihi/süre kuralları, faktör yöntemi (EStG §39f), III/V seçim önerisi kaynakta yok; yazılmadı.
- Kart 5 (vergi beyannamesi): danışmanlı beyan uzatması (AO §149 Abs. 3, Şubat sonu) yazılmadı; ELSTER'in ücretsiz olduğu kanıtsız; EStG §46 (de:kaynak:006) 2 kaynak sınırı nedeniyle kullanılmadı (ELSTER sayfası zorunlu halleri özetliyor). valid_until null: ELSTER sayfası 2025 yılı rehberi, kartın tarih örneği 2025 vergi yılı.
- Kart 6 (KDV): yalnız %19 ve %7; Anlage 2 örnekleri ve 01.01.2026 restoran değişikliği yazılmadı; tüketici fiyatına dahil olup olmadığı kaynakta yok.
- Kart 7 (Kirchensteuer): oran (%8/%9), kimin ödediği ayrıntısı, üyelikten çıkış usulü kaynakta yok; kart yalnız çerçeve. "Oran ve çıkış usulü eyalete göre değişir" ifadesi için dayanak Art. 137 Abs. 8 WRV (uygulama ayrıntısı eyalet yasalarına aittir); çıkışa özel bir cümle kaynakta yok.
- Kart 11 (kredi bilgi kuruluşu): "yılda bir kez ücretsiz" kuralı yazılmadı. Kaynaklarda "Schufa" adı geçmiyor, yalnız "Auskunftei" geçiyor (BDSG §31); kart başlığı ve özeti "Schufa gibi kredi bilgi kuruluşları (Auskunftei)" diye yazıyor, Schufa'nın kendi hizmetlerine dair iddia yok.
- Kart 12 (hesap değiştirme): ücret tutarı yok (kaynak "angemessen" diyor).

## Kullanılmayan kaynaklar
- de:kaynak:006 (EStG §46), 010, 011 (SolzG), 014 (SGB VI §50), 020 (BaFin Hausrat), 022 (DRV Abkommen genel), 025 (BMG bakım sigortası), 027 (Bundesbank "Sepa einfach erklärt", 2014 tarihli). Ek not: 026'nın IBAN bölümü 027'den daha güncel ve yeterli.
- İkincil kaynak (verbraucherzentrale, handbookgermany) hiçbir kartta kullanılmadı.

## Dikkat notları
- Türk okuyucu: kart 1'de hakkın dayanağı AB'de hukuka uygun ikamet (ZKG §31); kart 10'da Türkiye-Almanya sosyal güvenlik anlaşması yalnız DRV Verbindungsstelle Türkei sayfasına dayanıyor; kart 12'de Almanya dışındaki bankayla yasal hesap değiştirme yardımı uygulanmıyor.
- valid_until.json: kart 3 ve kart 8 için 2026-12-31 (kaynaklar 2026 yılı değerleri); kart 5 null. Kart 7, 9, 10, 11, 12 yıla bağlı sayı içermiyor, listede yok. Kart 2'de anlık havale kuralları tarihsiz sayfaya dayanıyor, listede yok.
- Kart 8'deki BMG GKV sayfasında (028) "Stand: 3. September 2026" ibaresi var; oranlar sayfada 2026 olarak etiketli.
- Ana döngü kontrolü: kart 3'te EStG §32a metnindeki sayılar NBSP içeriyor; alıntılar kaynak metninden kopyalandı (pack_check geçti).

## Editör turu g1b (25.10.2026) notları
- Kart 8 (maas-sosyal-sigorta-kesintileri-2026): bordroda ayrıca kesilen bakım sigortası (Pflegeversicherung) kalemi karta EKLENMEDİ. Kartın iki kaynağı (018, 028) bakım sigortasını kapsamıyor ve kart başına 2 kaynak sınırı dolu. Başlık ve özet "emeklilik, işsizlik ve sağlık" kapsamıyla tutarlı. Bakım sigortası oranı saglik konusundaki karttadır; ayrı bir kart ya da 3. kaynak izni gerekir.
- Kart 5 (yillik-vergi-beyannamesi-elster-son-tarih): kart yıldan bağımsız yazıldı (AO §149 Abs. 2 ve 3). ELSTER 2025 örnekleri ("31 Temmuz 2026", "31 Aralık 2029") yalnız "örneğin 2025 yılı için" diye duruyor. valid_until null. EStG §46 Abs. 2 Nr. 8 cümlesi kaynakta açıklanmadığı için silindi.
- Kart 3 (gelir vergisi): valid_until 2026-12-31 geri konuldu (kaynak "ab dem Veranlagungszeitraum 2026").
- Kart 10 (emeklilik): §235 tablosu kaynakta başlıksız satır dizisi; satırlar bitişik olmadığı için tek quote 200 karaktere sığmıyor. Tabloyu tanıtan cümle + başlık ayrı claim olarak eklendi; satır claim'leri sütun anlamını söylüyor.
- Kart 11 (kredi bilgi kuruluşu): "Schufa" adı başlık ve özetten çıkarıldı (kaynaklarda geçmiyor); yalnız arama terimi olarak keywords'te kaldı.
- Kart 1 (basiskonto): BaFin sayfasındaki "hesap kapatıldıysa/kapatılacağı bildirildiyse bankaya bildir" notu yazılmadı (kart summary'si ret nedenlerine odaklı).

---
# Konu: is (yazar ve editör notları)

# DE / is — yazar boşlukları (25.10.2026)

11 kart yazıldı (order 401-411), kart başına en çok 2 kaynak. Aşağıda kart bazında yazılmayan bilgiler, kullanılmayan kaynaklar ve dikkat notları var.

## Kart bazında yazılmayan bilgi
- Kart 1 (iş sözleşmesi): Deneme süresinin üst sınırı (6 ay) ve deneme süresinde 2 haftalık fesih süresi BGB md. 622 (de:kaynak:104) sayfasında; kart başına 2 kaynak sınırı yüzünden kart 1'e alınmadı, kart 6'da fesih süreleri içinde yer alıyor. TzBfG md. 15/3 toplanmadı. Kart 1 yalnız NachwG md. 2 ve TzBfG md. 14'e dayanıyor.
- Kart 2 (asgari ücret): MiLoG md. 1'deki 12 Euro eski tutar, yazılmadı. de:kaynak:107 kullanılmadı (güncel tutar MiLoV5 sayfasında). 2027 için Minijob sınırı (633 Euro) de:kaynak:111'de geçiyor ama bu karta konu dışı olduğundan yazılmadı.
- Kart 3 (çalışma süresi, izin): Resmî tatil günleri ve "eyalete göre değişir" cümlesi karttan çıkarıldı (ArbZG ve BUrlG yalnız "gesetzliche Feiertage" kavramını kullanıyor, kaynakta eyalet çerçevesi yok). "Federal düzeyde yalnız 3 Ekim belirlenir" cümlesi de:kaynak:132 (Einigungsvertrag Art. 2) ile ancak gunluk konusunun tatil kartında yazılır (kart başına 2 kaynak sınırı). Federal 9 günlük liste kaynakta yok. 5 günlük haftada 24 Werktag'ın kaç iş gününe denk geldiği hesabı kaynakta yok, yazılmadı. SGB V md. 49 (Krankengeld'in ücret ödemesinden sonra başlaması) bu konuda kullanılmadı.
- Kart 4 (bordro): EStG md. 38 (Lohnsteuer'i işveren keser, de:kaynak:129) ve SGB III md. 341 (işsizlik primi yüzde 2,6, de:kaynak:130) 2 kaynak sınırı yüzünden kullanılmadı; kart GewO md. 108 ve 2026 prim üst sınırlarına (de:kaynak:131) dayanıyor. RV, KV, PV, Soli oranları kaynakta yok, yazılmadı. Lohnsteuer kesintisi karta girmedi.
- Kart 5 (hastalık): eAU için KBV (de:kaynak:136) ve Bundesärztekammer (de:kaynak:137) hiç kullanılmadı; kartta eAU anlatılmadı. SGB V md. 44 (Krankengeld hakkı ve istisnaları, de:kaynak:127) ve md. 48 (78 hafta süre, de:kaynak:126) 2 kaynak sınırı yüzünden kullanılmadı: kartta Krankengeld'in tutarı (md. 47) var, 78 haftalık süre ve hakkın kimlere verilmediği yok. 6 hafta ücret ödemesinden sonra Krankengeld'e geçiş sırası kaynakta açıkça yazılı olmadığı için kartta "sonrasında" bağı kurulmadı.
- Kart 6 (işten çıkarma): Fesihte yazılı şekil şartı (BGB md. 623) toplanmadı; kart "yazılı feshin sana ulaşması" ifadesini yalnız KSchG md. 4 metninden alıyor. Gebelik, işyeri konseyi görüşü gibi özel fesih korumaları kaynakta yok.
- Kart 7 (ALG I): SGB III md. 137 (de:kaynak:122) ve md. 147 (süre tablosu, de:kaynak:124) kullanılmadı; süre bilgisi Bundesagentur sayfasından (de:kaynak:121) alındı. Arbeitslosengeld hesabındaki Soli ve yüzde 20 paushal oranı kaynak sayfada olduğu gibi yazıldı; Steuerklasse etkisi karta alınmadı.
- Kart 8 (Bürgergeld / Grundsicherungsgeld): Editör turunda kaynaklar de:kaynak:118 (1.7.2026 geçişi, yükümlülükler, yaptırımlar) ve de:kaynak:120 (SGB II md. 7, hak sahipleri ve yabancılar için şartlar) oldu; Regelsatz kaynağı de:kaynak:119 (563 Euro, 1 Ocak 2026 tarihli sayfa) 2 kaynak sınırı yüzünden çıkarıldı, kartta Regelsatz tutarı yok. 2027 Regelsatz tutarı karara bağlanmadığı için yazılmadı. Arbeitsverweigerer-Regelung (en az 1, en çok 2 ay Regelbedarf'ın kesilmesi) ve kira gideri tavanı yazılmadı. SGB II md. 7'nin ayrıntıları (Aufenthaltsgesetz'deki oturum izni türleri) yalnız atıfla anıldı.
- Kart 9 (serbest çalışma): Gewerbe ile Freiberuf ayrımının tanımı (EStG md. 18, de:kaynak:135) ve GewO md. 14 (Gewerbeanmeldung, de:kaynak:138) 2 kaynak sınırı yüzünden kullanılmadı; bildirim yolu AO md. 138 (de:kaynak:134) ile yazıldı, Kleinunternehmer sınırı UStG md. 19 (de:kaynak:133) ile. Finanzamt'ın bir faaliyeti Gewerbe mi Freiberuf mu saydığını açıklayan sayfa yok. UStG md. 19 metnindeki "25 000 Euro" boşluk karakteriyle yazılıdır; alıntı metinden olduğu gibi alındı. Sayfada yıl belirtilmediği için valid_until null.
- Kart 10 (Minijob/Midijob): Midijob indirimli prim oranı rakamı kaynakta yok, yazılmadı. SGB IV md. 8 ve md. 20 (de:kaynak:114, 115) kullanılmadı (tutar DRV ve Minijob-Zentrale sayfalarında). Özel hane (Privathaushalt) Minijob'unun çalışan payı (13,6 Prozent) ile Gewerbe payı (3,6 Prozent) Minijob-Zentrale sayfasında ayrı bölümlerde veriliyor; ikisi de kartta, çelişki yok. Kaza sigortası cümlesi yalnız hane bölümünde geçtiği için yazılmadı.
- Kart 11 (tanıma): Anerkennungs-Finder'daki belge listesi ve yetkili kurumlar eyalete/mesleğe göre değişir; kartta yazılmadı. anabin sayfasının kendisi açılmadı (KMK/ZAB sayfası ve Anerkennungsportal'daki atıflar kullanıldı).

## Kullanılmayan kaynaklar (kart başına 2 kaynak sınırı)
de:kaynak:107, 114, 115, 119, 122, 124, 126, 127, 129, 130, 132, 135, 136, 137, 138.

## İkincil kaynak kullanımı
Yok. KBV (de:kaynak:136) ve Bundesärztekammer (de:kaynak:137) kullanılmadı.

## Dikkat notları
- ArbZG tam metin sayfasında satırlar sert kırılmış (cümle ortasında satır sonu); alıntılar boşluk normalizasyonuyla eşleşiyor.
- Kart 8 Bundesregierung'un 1 Temmuz 2026 tarihli sayfasına ve SGB II md. 7'nin gesetze-im-internet metnine göre yazıldı; sonraki değişiklikler kartta yok. valid_until 2026-12-31.
- Kart 4'teki prim üst sınırları 2026 içindir. 2027 sınırları Kabine kararı aşamasında (Bundesrat onayı bekleniyor), kartta yok.
- valid_until.json: asgari ücret 2027-12-31 (14,60 Euro 2027 için MiLoV5'te belirli); bordro, Bürgergeld, Minijob kartları 2026-12-31; serbest çalışma (Kleinunternehmer sınırı) ve tanıma (Zeugnisbewertung ücreti) null.

## Editör turu g1b (25.10.2026) notları
- burgergeld: 5 yıl istisnası yalnız SGB II §7 Abs. 1 Satz 2 Nr. 2 için yazıldı (Nr. 3 Asylbewerberleistungsgesetz için yok); hak kaybı tespiti (FreizügG/EU md. 2/1) istisnası ve AufenthG §20a izni (kaynak 120'de var) eklendi. Kaynak "Kapitel 2 Abschnitt 5 AufenthG"nin içeriğini açıklamıyor; terim açıklanmadan bırakıldı. "AB serbest dolaşım hakkı Türk vatandaşlarına uygulanmaz" cümlesi YAZAR_KURALLARI 7 gereği duruyor; kaynak Türk vatandaşı anmıyor, hukuki koşul (serbest dolaşım hakkı) claim 17'dedir. valid_until null (karta tarihe duyarlı tutar kalmadı).
- isten-cikarma: KSchG §23/1 Satz 3 cümlesi beş çalışan sınırına (Satz 2) bağlandı.
- is-sozlesmesi: 52 yaş kuralına "hemen önce" ve iki alternatif eklendi. BVerfG kararının kendi metni kaynak olarak yok; yalnız yasa metninin dipnotu kadar yazıldı.

---
# Konu: fatura (yazar ve editör notları)

# fatura — yazar notları ve yazılmayan bilgi (25.10.2026)

Kart başına en çok 2 kaynak sınırı nedeniyle seçim yapıldı; yazılmayan bilgi ve kullanılmayan kaynaklar aşağıda.

## Kart bazında
- 501 elektrik-temel-tedarik-ve-saglayici-degistirme (kaynak 080 + 059): Grundversorger tanımı (EnWG §36: ağda en çok haneyi besleyen şirket, kaynak 058) ve temel tedarik sözleşmesinin 2 haftalık fesih süresi / fesih için ek ücret alınamaması (StromGVV §20, kaynak 060) yazılmadı; kart 1'e düşen 4 adresten en kapsayıcı ikisi (sözleşmenin elektrik çekişiyle kurulması + tedarikçi değişim süreci) seçildi.
- 502 elektrik-faturasi-donemleri-ve-fiyat-artisinda-fesih (061 + 062): Abschlag (StromGVV §13, kaynak 063) yazılmadı. Neden: kart 2'ye 3 adres düşmüştü (061, 062, 063), sınır 2; ayrıca §13 yalnız temel tedarik (Grundversorgung) için geçerli, ulusal kartta genellenemez. Öneri: gerekirse kart 501'e (temel tedarik) ya da ayrı kart olarak eklenir. "Arbeitspreis / Grundpreis" terimleri yasa metinlerinde geçmediği için kullanılmadı. Kart, yıllık fatura (EnWG §40b) ve fiyat artışında özel fesih (EnWG §41) üzerine kuruldu; başlık buna göre "fiyat artışında fesih + fatura sıklığı".
- 503 isitma-ve-yan-gider-hesabi-nebenkostenabrechnung (066 + 067): HeizkostenV §8 (sıcak su), §§1-3 ve 6 (hesap zorunluluğu) yazılmadı. Editör turu: §7'deki %70 istisnası (eski yapı, yağ/gaz, yalıtımlı borular) karta eklendi; BGB §556 Abs. 5 notu kapsamıyla sınırlandı.
- 504 su-ve-atik-su-gideri-kiraciya-nasil-yansir (068 + 067): tarife / Gebühr-Beitrag ayrıntısı kaynakta yok; kartta tarife iddiası ve rakam yazılmadı (editör turunda "belediyeye göre değişir" cümlesi kaldırıldı). Kimin hangi tarifeyle fatura kestiği (doğrudan belediye/Stadtwerke ya da kiralayan üzerinden) için federal kaynak bulunamadı. Kiracı olmayanlar (mülk sahibi) için kural yazılmadı.
- 505 yayin-katki-payi-rundfunkbeitrag-tutar-ve-muafiyet (074 + 076): Editör turunda eklendi: Widerspruch süresi (1 ay), Säumniszuschlag (%1, en az 8 Euro), Arbeitslosengeld I / Wohngeld / Übergangsgeld muafiyet vermez, belge şartı (ad, yardım türü, dönem), formu yazdırıp imzalayıp gönderme. Hâlâ yazılmadı: eş ve 25 yaşına kadar çocukların muafiyet kapsamı, Härtefall muafiyeti, Ratenzahlung/Stundung ayrıntıları. Kaynak 075 (Wohnung anmelden) kullanılmadı; kayıt formu bu kartta bağlantı olarak da yok. Sayfalar tarihsiz ve kaynakta yıl/bitiş yok: tutar "güncel tutar" olarak yazıldı, valid_until null. Sosyal yardımın adı kaynakta "Grundsicherungsgeld (früher Bürgergeld)".
- 506 internet-ve-mobil-sozlesme-suresi-ve-fesih (069 + 070): TKG §57 (tek taraflı sözleşme değişikliğinde ücretsiz fesih, kaynak 071) ve BNetzA taşınma sayfası (077) kullanılmadı (kart 8 ve 7'de ayrı ele alındı). TKG §56 Abs.3 Satz 2 (uzamadan önce sağlayıcının bilgilendirme yükümlülüğü), §56 Abs.4 (erken fesihte cihaz bedeli sınırı), §56 Abs.5 (e-posta erişimi) ve sözleşme özeti / Kündigungsbutton (BGB §312k) yazılmadı.
- 507 internet-hizi-dusuk-ve-ariza-haklari (072 + 078): Mobil ve sabit hat ölçüm eşikleri ve ölçüm sayıları (30 ölçüm, 14 gün, yüzdeler; Allgemeinverfügung 35/2026, 20.04.2026'dan geçerli) tarihe duyarlı olduğu için yazılmadı. Schlichtung ayrıntıları (kaynak 079: gönüllü katılım, bekleme süresi 2026 verisi, ücretsizlik) ve TKG §57 Abs.4 (kaynak 071) kullanılmadı; kartta Schlichtung yalnız 078'de geçtiği kadar. BNetzA şikayet formu sayfası açılmadı.
- 508 numara-tasima-ve-operator-degistirme (077 + 073): Sözleşme sonrası taşıma süresinin operatör şartlarında daha uzun olabileceği ("häufig 90 Tage") yazılmadı. TKG §59 Abs.3/5/7/8 (portlama kuralları, fiyat düzenlemesi) ayrıntıya girilmedi.
- 509 elektrik-kesme-ve-odeme-guclugu (064 + 065): StromGVV §19 (kaynakta yok, kart için kullanılmadı). §41f Abs.6 (tehdit içeriği), §41g Abs.5-6 (izinsiz bilgi paylaşımı ve veri listesi) yazılmadı. Abwendungsvereinbarung'un tam içeriği ve standart cevap formu ayrıntısı yazılmadı. Kural, konut aboneleri (Haushaltskunden) için; Abwendungsvereinbarung yalnız temel tedarikte.

## Kullanılmayan kaynaklar
058 (§36 EnWG), 060 (§20 StromGVV), 063 (§13 StromGVV), 071 (§57 TKG), 075 (Rundfunkbeitrag kayıt formu), 079 (BNetzA Schlichtung). Hepsi kart başına 2 kaynak sınırı yüzünden; içerik çelişkisi yok.

## Dikkat notları
- Kart 502'nin başlığı ve içeriği, görev mesajındaki "Abschlag" beklentisinden sapıyor (2 kaynak sınırı); karar ana döngüde: 063 kart 501'e eklenebilir (o zaman 501'den 080 ya da 059 çıkar) ya da Abschlag ayrı kart olur.
- Kart 505: "Grundsicherungsgeld (früher Bürgergeld)" kaynakta bu şekilde geçiyor; sayfa tarihsiz.
- Kart 507: "Minderleistung" ve ölçüm kuralları BNetzA sayfasına göre; sayfa 2026 Allgemeinverfügung'una atıf yapıyor.
- İkincil kaynak (verbraucherzentrale vb.) kullanılmadı.
- Tüm kartlarda şehir adı ve eyalet bilgisi yok; "belediyeye göre değişir" yalnız kart 504'te çerçeve cümlesi olarak geçiyor.

## Editör turu g1b (25.10.2026) notları
- elektrik-temel-tedarik-ve-saglayici-degistirme ve elektrik-kesme-ve-odeme-guclugu: "Werktag" terimi iki kartta açıklamasız. EnWG kaynaklarında tanımı yok; "Pazar ve yasal tatil dışındaki tüm günler, Cumartesi dahil" tanımı BUrlG §3'tedir (is konusundaki calisma-suresi kartının kaynağı), bu konunun kaynak listesinde değil. Karta tanım eklenmedi; tanımı kaynağa koymak için BUrlG §3 sayfasının bu iki karta eklenmesi ya da ayrı bir sözlük girdisi gerekir.
- numara-tasima: %20 alternatifi ayrı claim olarak kuruldu (quote iki cümleye sığmıyordu).
- yayin-katki-payi: Inhaber tanımı kaynaktaki iki yarısıyla yazıldı.

---
# Konu: saglik (yazar ve editör notları)

# saglik - yazar gaps (25.10.2026)

9 kart, kart başına 2 kaynak. valid_until.json: kart 3 = 2026-12-31; kart 1, 6, 9 = null (tutar/eşik var, kaynakta bitiş tarihi yok).
Not: de:kaynak:142 ile de:kaynak:028 aynı BMG /beitraege metni; listedeki 142 kullanıldı.

## Kart bazında yazılmayan bilgi
- Kart 1 (zorunluluk): Jahresarbeitsentgeltgrenze (SGB V §6) kartta yok (yalnız BMG beitraege sayfasında 77.400 Euro geçiyor, kart 3'ün 2. kaynağı değil); serbest meslek, §5 Abs.1 Nr.13 (başka güvencesi olmayanlar) ve istisnaları, Basistarif ayrıntısı yazılmadı. Türkiye-Almanya sosyal güvenlik anlaşması sağlık kısmı için kaynak yok.
- Kart 2 (aile sigortası): gelir sınırı rakamsız (SGB IV §18 atfı); "ücretsiz" ifadesi BMG beitraege cümlesine ("Familienversicherte zahlen keinen Beitrag") dayanır.
- Kart 3 (prim): SGB XI §55 (eski %3,4) kullanılmadı. Gönüllü sigortalı (serbest meslek/yüksek gelir) asgari-azami aylık prim tablosu, bakım primi çocuk sayısına göre tablo (2-5 çocuk) yalnız kural cümlesi olarak yazıldı, işveren/çalışan paylarının eyalete göre farkı rakamsız çerçevelendi. Bakım sigortası oranı sayfasında "2026" ibaresi yok ("seit 1. Januar 2025").
- Kart 4 (hekim/randevu): 144 (SGB V §75) + 143 (116117) seçildi; Hausarztprogramm (de:kaynak:145, SGB V §73b: kasa sunar, katılım gönüllü, katılımda yalnız seçilen aile hekimi ve sevkle uzman, göz/kadın doğum hariç, 2 hafta cayma, en az 1 yıl bağlılık) kullanılmadı, kart 4'e sığmadı. Genel "sevk zorunluluğu / aile hekimi birincil temas" kuralı kaynakta yok, yazılmadı; yalnız randevu servisi aktarımındaki sevk şartı (SGB V §75) yazıldı. 116117 randevu servisi alt sayfası (terminservice.php) 403.
- Kart 5 (acil): nöbetçi eczane arama servisi adı ve 22833 numarası yazılmadı (resmî kaynak yok). Notaufnahme/Bereitschaftspraxis farkı yalnız 116117.de cümleleriyle.
- Kart 6 (reçete): 2 kaynak sınırı nedeniyle de:kaynak:148 (BMG e-Rezept: 01.01.2024'ten beri zorunlu; eGK, uygulama, CardLink veya kağıt çıktıyla eczanede; çevrimiçi eczane) kartta yok; editör turunda eklenmesi önerilir. Çocukların (18 yaş altı) katılım payından muafiyeti kaynakta alınmadı. 2026 euro muafiyet tutarı kaynakta yok.
- Kart 7 (aşı/çocuk muayenesi): 150 (IfSG §20) + 151 (SGB V §26) seçildi. de:kaynak:149 (RKI Impfkalender 2026, Epid. Bull. 4/2026, 10 dil; tabloda aşı yok) ve de:kaynak:152 (BMG: U1-U9 ve J1 adları) kullanılmadı. U1-U9 yaşları ve "U" adı kartta yok (anahtar kelimede yalnız "U-Untersuchung"). Muayene katılım zorunluluğu/davet eyaleteydi, yazılmadı. IfSG §33'ün kurum listesi (Kita, okul vb.) metinde yok, "§ 33 Nr. 1-3'te sayılan kurumlar" diye yazıldı.
- Kart 8 (hamilelik): 154 + 155 seçildi. Mutterschaftsgeld (de:kaynak:156, SGB V §24i: günlük en çok 13 Euro, fark işveren) ve §24d/24f ebelik hakkı kartta yok; editör turunda eklenebilir (kart 8'e 3. kaynak gerekir). Yabancı/geçici izinli çalışanlar için Mutterschutz ayrıntısı kaynakta yok.
- Kart 9 (bakım): de:kaynak:157 (SGB XI §15: Pflegegrad puan eşikleri 12,5/27/47,5/70/90) kartta yok. Pflegegeld tutarları 159'daki tabloda var (Stand 14.09.2026), tablo yıl etiketi yok.

## Kullanılmayan kaynaklar
145, 148, 149, 152, 156, 157 (kartlara sığmadı; üstte nedenleri).

## Dikkat
- Kart 8'de Hilfetelefon numarası 0800/40 40 020 yazıldı; "19 dil" içinde Türkçenin olduğu kaynakta belirtilmiyor, yazılmadı.
- Kart 3 notunda bir eyalette farklı pay "eyalet adı verilmeden" çerçevelendi.
- Kart 4: "116117 = Terminservicestelle numarası" eşlemesi iki kaynağın birlikte okunmasına dayanır (144 "bundesweit einheitliche Telefonnummer", 143 "116117 ... Termin finden"); karta açık eşitlik cümlesi yazılmadı.

## Editör turu g2 (25.10.2026)
- Kart 601: kaynak 140 (SGB V §5) yerine SGB V tam metin (de:kaynak:265) kullanıldı; sayfa 3 MB gövde sınırında kesildi (§5 ve §6 başta, tam), kart kaynakları 139 + 265. 140 hiçbir kartta kullanılmıyor. JAEG rakamı (BMG de:kaynak:142'deki 77.400 Euro, 2026) kartlara yazılmadı. Basistarif, gönüllü GKV (SGB V §9) ve Türkiye-Almanya sosyal güvenlik anlaşması yazılmadı.
- Kart 603: Kartta 'Bürgergeld' adı BMG kaynağındaki (de:kaynak:025) haliyle duruyor. Canlı yasada (SGB V §5 Abs.1 Nr.2a, 25.10.2026) yardımın adı 'Grundsicherungsgeld'; ad değişikliği not edilmeli, kaynak güncellenince kart yenilenmeli.
- Kart 604: 116117 numarası ile yasal Terminservicestelle'nin aynı numara olduğunu açıkça söyleyen resmî kaynak (KBV/116117.de Terminservice sayfası, 116117.de/terminservice.php 403) yok; kartta iki bilgi ayrı yazıldı. Hausarztprogramm (de:kaynak:145) hâlâ kullanılmıyor.
- Kart 607: IfSG tam metin (de:kaynak:266) 150 yerine kullanıldı (150 artık kartlarda yok). §23 Abs.3 ve §36 kurum listeleri yazılmadı.
- Kart 608: Mutterschaftsgeld (SGB V §24i, de:kaynak:156: günlük en çok 13 Euro, fark işveren) 2 kaynak sınırına sığmadığı için yazılmadı; ayrı bir kartla (örn. annelik parası) eklenebilir. Özel sigortalı için kaynak yok.
- Kart 609: Pflegegrad 1-5 aralığı ve puan eşikleri (SGB XI §15, de:kaynak:157) yazılmadı; kaynak sınırı.
- Kullanılmayan kaynaklar (güncel): 140, 145, 148, 149, 150, 152, 156, 157.
- Çapraz not (para 308): Bordro kesintisi sayan kartta bakım sigortası kalemi eksik (denetim notu); para konusunun işi.

## g2b editör turu (25.10.2026)
- Kart 608: Mutterschaftsgeld (koruma süresinde ücret) kartta yok; kaynak sınırı (kart başına 2 kaynak). Ayrı kart gerekir: SGB V §24i (kaynak 156: 'Es beträgt höchstens 13 Euro für den Kalendertag.') + MuSchG §19. Başlık kartın kapsamına (Mutterpass, ebe, koruma süreleri) daraltıldı.
- Kart 601: gönüllü kamu sigortası (SGB V §9) yalnız varlığıyla yazıldı; koşulları (Vorversicherungszeit vb.) ve diğer katılım grupları yazılmadı.
- Kart 603: 'Bürgergeld' adı BMG kaynağındaki gibi duruyor; yasada güncel adı 'Grundsicherungsgeld' (265'te var) kartın kaynaklarında olmadığı için eklenmedi.
- Kart 607: § 36 Abs. 1 Nr. 4 (çalışan yükümlülüğü kapsamındaki bir başka kurum grubu) adlandırılmadı; § 23 Abs. 3 Satz 1'den hastane/ayakta ameliyat/muayenehane yazıldı.
- Kart 609: Pflegegrad derecelerinin tam tanımı (1-5) kartta yok.

---
# Konu: ev (yazar ve editör notları)

# ev - yazar notları (25.10.2026)

Çıktı: 9 kart (order 701-709), 128 claim, 17 bağlantı, 2 tarihe duyarlı kart. Tüm claim alıntıları kaynak metninde birebir doğrulandı.

## Kart bazında yazılmayan bilgi
- Kart 2 (depozito): depozito iade süresi ve koşulu yazılmadı (kaynakta yok, içtihat). §548 (kiralayanın hasar taleplerinin 6 ay zamanaşımı) kullanılmadı: 2 kaynak sınırı ve depozito iadesi için dolaylı.
- Kart 3 (Mietpreisbremse): hangi eyalet/şehirde geçerli olduğu yazılmadı ("eyalet yönetmeliğine bağlı"). Muafiyetler (2014 sonrası ilk kiralanan yeni konut, kapsamlı modernizasyon) ve 30 aylık iade hakkı yalnızca bmj.de Mietrecht özeti (180) ve Mietpreisbremse sayfasında (181) var; 2 kaynak sınırı yüzünden yazılmadı. valid_until 2029-12-31 (§556d: yönetmelikler en geç bu tarihte sona erer).
- Kart 5 (Mietminderung): küçük onarım (Bagatellreparatur) tavanı, Schönheitsreparaturen kuralı ve kira indirimi yüzdesi yazılmadı (kanunda yok, içtihat). §535 (kiralayanın bakım yükümlülüğü, 168) ve §548 (184) kullanılmadı: 2 kaynak sınırı.
- Kart 6 (WBS + Wohngeld): gelir sınırı rakamları (WoFG §9: 12.000/18.000/4.100/500 euro) yazılmadı; federal taban ve eskimiş, eyaletler farklı belirliyor. Wohngeld tutar tablosu ve gelir sınırları yazılmadı (kaynakta yok). Yabancıların Wohngeld hakkı koşulu (WoGG §3 Abs. 5: Aufenthaltstitel vb., Chancenkarte/arbeitsplatzsuche izinlerinde genelde hak yok; kaynak 171) kullanılmadı: 2 kaynak sınırı (169 + 179 seçildi). Yabancı okuyucu için önemli olduğundan, ana döngü isterse 171 ile ayrı bir Wohngeld kartı ya da 169 yerine 171 düşünülebilir. valid_until 2026-12-31: kaynak (179) 2025 durumu, son artış 1.1.2025 ve iki yıllık düzen; bir sonraki uyarlama 1.1.2027.
- Kart 7 (Wohnungsgeberbestätigung + Bestellerprinzip): Übergabeprotokoll için kaynak yok, yazılmadı; başlıkta da geçmiyor. Kayıt süresinin kendisi (§17 BMG, 2 hafta) 172'de yok, yazılmadı (adres kaydı kartı konusu: `resmi` topic'inde `adres-kaydi-anmeldung-iki-hafta-konut-veren-onayi` kartı Wohnungsgeberbestätigung'u da kapsıyor, kısmi örtüşme var).
- Kart 8 (sahte ilan): tek kaynak (polizei-beratung.de Vorkassebetrug, tarihsiz); kendi ilan sayfası yok. Kaynaktaki "sichere Bezahlmethoden, Kreditkarte" önerisi ürün satın almaya yönelik olduğu için kiralık konuta uyarlanmadı.
- Kart 9 (ev satın alma): Grunderwerbsteuer oranı yazılmadı. 2 kaynak sınırı yüzünden §873 BGB (176: mülkiyet devri için Einigung + Grundbuch tescili), GrEStG §1 (178: alım vergiye tabidir) ve §656c BGB (173: satışta emlakçı komisyonu eşit paylaşım, tek taraf için ücretsiz çalışırsa diğerinden alamaz) kullanılmadı. Karttaki Grundbuch bilgisi yalnız §311b'nin ikinci cümlesine dayanıyor. İstenirse §656c ayrı bir "satışta emlakçı komisyonu" kartı olabilir.

## Kullanılmayan kaynaklar
161 (§542), 162 (§557a), 163 (§557b), 168 (§535), 170 (WoFG §9), 171 (WoGG §3), 173 (§656c), 176 (§873), 178 (GrEStG §1), 181 (bmj Mietpreisbremse), 184 (§548). Kart 1'de §542, §557a ve §557b yerine aynı içeriği veren bmj Mietrecht özeti (180) seçildi; §557a'ya özgü "kiracının fesih hakkı en çok 4 yıl dışlanabilir" kuralı bu yüzden yazılmadı.
Diğer 16 kaynak kartlarda kullanıldı.

## Dikkat notları
- bmj.de Mietrecht özeti (180) 14.09.2022 tarihli; yalnız kart 1 ve 2'de kullanıldı, tarihli sayfa olarak karta yıl yazıldı (kart 1 notu). Kuralın BGB karşılığı (§573c, §551) ikinci kaynak olarak aynı kartta.
- Kart 4 (Betriebskosten) `fatura` konusundaki `isitma-ve-yan-gider-hesabi-nebenkostenabrechnung` kartıyla konu olarak örtüşebilir; bu kart BGB §556 + BetrKV §2 (kalem listesi, 12 ay + 12 ay süresi) üzerine kurulu, ısınma gideri paylaşımını anlatmıyor. Ana döngü kopya/örtüşme taramasında bakabilir.
- Kart 6 Wohngeld bilgisi bmwsb sayfasının 2025 durumuna göre; Wohngeld 1.1.2027'de yeniden uyarlanabilir.
- Hiçbir kartta eyalet adı, eyalet rakamı ya da şehir adı yok; eyalete bağlı konular (Mietpreisbremse bölgeleri, Wohngeld gelir sınırı, Grunderwerbsteuer oranı, WBS sınırı) "eyalete göre değişir" olarak çerçevelendi.

## Editör turu (25.10.2026, G2) - güncel durum
Bu bölüm yukarıdaki satırlarla çelişirse bu geçerlidir. Güncel sayılar: 9 kart, 129 claim, 17 bağlantı, 2 tarihe duyarlı kart (703 bitiş tarihi null, 706 2026-12-31).
- Kart 1 (701): fesihin yazılı biçim şartı (§ 568 BGB) yazılamadı; sayfa kopya olarak 'thin_text' (482 karakter) diye reddedildi ve başka resmî sayfa bulunamadı. Zugang (bildirimin ulaşması) şartı ve Werktag'ın Cumartesi'yi içerdiği kaynak metinlerde yok (BGH kararı kaynak değil), yazılmadı. Kaynaklar: BMJ özeti (180) + § 575 BGB (267); § 573c (160) çıkarıldı.
- Kart 3 (703): kaynaklar Kappungsgrenze (§ 558, 166) + BMJ özeti (180). § 556d (165) çıkarıldığı için Mietpreisbremse yönetmeliklerinin eyalet hükümetince ve en geç 31.12.2029'da sona ermesi karttan çıktı; Vormiete ve modernizasyon sonrası üst sınır (§ 556e) ve § 556f ayrıntısı yazılmadı. İstenirse ayrı bir 'Mietpreisbremse istisnaları' kartı bu kaynaklarla (165, 181) kurulabilir.
- Kart 4 (704): itiraz süresi, belge inceleme ve elektronik belge cümleleri `fatura` konusundaki kartta kaldığı için buradan çıkarıldı.
- Kart 6 (706): 'sosyal konut hukuku eyalet yetkisindedir' genel çerçevesi kaynakta olmadığı için yazılmadı; yalnız WoFG § 27 Abs. 3-4'ün söylediği (gelir sınırı ve konut büyüklüğü eyalete göre) yazıldı.
- Kart 7 (707): konut veren teyidinin süresi/içeriği `resmi` konusundaki adres kaydı kartında; burada tek cümle kaldı. 'Bestellerprinzip' terimi kaynak metinde geçmediği için cümleden çıkarıldı.
- Kart 9 (709): tapu sicili kaydının işleyişi ve verginin kime/ne zaman düştüğü kaynaklarda yok, başlıktan çıkarıldı.
- Yeni kaynak: de:kaynak:267 (§ 575 BGB, snap_ev-editor2). snap_ev-editor1 klasörü reddedilen § 568 denemesinden kalan boş denemedir.
- 160 (§ 573c), 165 (§ 556d) bu turdan sonra kartlarda kullanılmıyor.

## g2b editör turu (25.10.2026)
- Kart 701: Werktag/Cumartesi açıklaması için kaynak gerekir. 'Werktag' kartta açıklamasız kaldı; Pazar ve resmî tatillerin sayılmadığı, Cumartesi'nin sayılıp sayılmadığı kartın kaynaklarında (180, 267) yok. Resmî kaynak (ör. BGB §573c ile ilgili yasa metni) ya da başka bir resmî yorum sayfası bulunursa karta eklenebilir; BGH kararı kaynak alınmadı.
- Kart 701: 'Fesih biçimi' (§568 yazılı biçim) hâlâ yok (önceki tur: thin_text).
- Kart 703: BGB §556d'ye göre yönetmeliklerin 2029 sonuna kadar yürürlükte kalabileceği bilgisi kartın BMJ kaynağında yok; kart tarihli özete (14 Eylül 2022) dayanıyor.
- Kart 704: BGB §556 Abs. 5 kapsamı (Abs. 1, 2 Satz 2, 3, 3a) not alanında bu kapsamla yazıldı.
- Kart 707: Wohnungsgeberbestätigung süresi (iki hafta) 201/186 kaynaklarında; 707'nin kaynağı 172 yalnız '§ 17 Abs. 1'deki süre' diyor, karta yazılmadı.

---
# Konu: planlama (yazar ve editör notları)

# Planlama konusu: yazılmayan bilgiler ve notlar (yazar, 25.10.2026)

9 kart, order 801-809. Kullanılmayan kaynaklar: de:kaynak:172 (BMG md. 19), 140 (SGB V md. 5), 195 (SGB V md. 175), 139 (VVG md. 193), 198 (EinhZeitG md. 5), 199 (BBankG md. 14), 201 (ZKG md. 31). Hepsi "kart başına en çok 2 kaynak" kuralı yüzünden dışarıda kaldı (aşağıya bak).

## Kart bazında

### Kart 1 (taşınma sırası), kaynaklar 035 + 186
- Sıra AufenthG md. 6(3), md. 5(2), md. 2(3), md. 81(1) ve BMG md. 17'den kuruldu. Randevu bilgisi kartta yok (kart 2'de). Konut veren teyidi (BMG md. 19, kaynak 172) 2 kaynak sınırı nedeniyle yazılmadı.
- Vize muafiyeti olan uyruklar ve AB hukukundan doğan oturum hakkı bu kaynakların kapsamı dışında; kart "gerekli vize" ve "kural olarak" diyor.
- Bağlantı olarak kaynak 042 (tuerkei.diplo.de ulusal vize sayfası) da verildi; kartın source_ids'inde değil.

### Kart 2 (vize başvurusu), kaynaklar 041 + 042
- Belge listesi yazılmadı: sayfa belgeleri vize amacına göre kontrol listelerine, Auslandsportal'a ve Merkblatt'lara taşıyor; tek ortak liste yok. Kartta yalnız "amaca göre kontrol listesi vardır, eksik belge ret nedenidir, belge kendiliğinden gönderilmez" yazıldı. documents alanı bilerek boş.
- Vize ücreti sayfada "max. 90 EUR"; tür bazlı kesin tutar yok. Yıl yok, bu yüzden valid_until null.
- Çelişki: 041 "Terminbuchung kostenlos" diyor; 042 ulusal vize için duruma göre 12 EUR randevu bedeli (ve 39,92 EUR hizmet bedeli) sayıyor. Kartta "randevu ücretsiz" cümlesi yazılmadı, 12 EUR atıfla (ulusal vize sayfasına göre) yazıldı.
- 59 ay parmak izi kuralı sayfada "Schengen-Visaanträge" bölümünde; kartta Schengen vizesi olarak sınırlandı. Ulusal vize için parmak izi kuralı kaynakta ayrıca yok.
- Başvuru-öncesi/sonrası genel akış cümleleri (randevuda belge verme, fotoğraf, işlem süresi 15-45 gün) sayfanın genel "Antragstellung" bölümünden alındı; bu bölüm Schengen ağırlıklı yazılmış. Ulusal vize için ayrı işlem süresi sayfada yok.
- "Yıl" bilgisi: bekleme süreleri ve ücretler tarihsiz; sayfa 2026 güncellemeli ama metinde yıl yok (042'deki tek tarih 15.06.2026 Auslandsportal haberi). Kartta yıl yazılmadı.
- Vize kategorisini yanlış seçmenin ret nedeni olması yalnız Schengen bölümünde; yazılmadı.

### Kart 3 (ilk günler), kaynaklar 193 + 194
- Kaynak sınırı (en çok 2) yüzünden kart yalnız Steuer-ID ve Rundfunk'u kapsıyor. Aday listedeki Anmeldung (kaynak 186/172, kart 1'de ve resmi konusundaki kartlarda), Basiskonto (kaynak 201, para konusunda kart var) ve Krankenkasse seçimi (kaynak 195) bu kartta yok. Editör dikkatine: kart 3 başlığı "ilk günler" yerine daha dar; gerekirse editör turunda ek kart ya da kaynak genişletme kararı gerekir.
- Rundfunkbeitrag tutarı yazılmadı (konu görevinde yasak). Not: 194 metninin sözlük kısmında üç aylık 55,08 Euro, yıllık 220,32 Euro yazıyor; bu konu için kullanılmadı.
- eGK (sigorta kartı) süreci kaynakta yok.
- Steuer-ID'nin posta ile mi geldiği yetişkin için kaynakta açık değil; kartta "bildirilir" ve "teslimat için soyadı posta kutusunda yazılı olmalı" yazıldı.

### Kart 4 (ev eşyası, araç), kaynaklar 187 + 200
- Türkiye'ye özgü bir muafiyet kaynakta yok; yazılmadı. Kart "AB dışından" diye çerçevelendi.
- Sayfa tarihsiz; valid_until verilmedi.

### Kart 5 (nakit ve yolcu bagajı), kaynaklar 188 + 189
- Sayfalar tarihsiz; tutarlar için yıl yazılmadı, valid_until verilmedi (aday listede de yok).
- AB üyesi ülkeden girişte "abweichende Reisefreimengen" (Genussmittel, Energieerzeugnisse) 188'de adı geçiyor ama değerler bu sayfada yok; yazılmadı.
- "Türkiye AB dışıdır" bilgisi kartta kaynak atfı olmadan yazılmadı; kart "AB dışından" diyor.

### Kart 6 (evcil hayvan), kaynak 190
- Sayfa Türkiye'yi adıyla yalnız "kuduz görülen ya da salgın durumu bilinmeyen AB dışı ülkelere tatil yolculuğu" cümlesinde sayıyor. Türkiye'nin DVO (EU) 2026/636 Ek I ve II'de listelenip listelenmediği kaynakta yok, bu yüzden Türkiye'den gelen hayvan için antikor testinin kesin zorunlu olduğu yazılmadı; kart cümleyi atıfla veriyor. Kritik bir kart: editör Ek I/II listesinden Türkiye'nin durumunu başka resmî sayfadan (BMLEH/EU) eklemeyi değerlendirebilir.
- bmleh.de Heimtiere sayfası (giriş noktaları listesi) kaynak listesinde yok; onaylı giriş yerleri adları yazılmadı.
- "Gelincik" yerine "ferret (Frettchen)" kullanıldı.

### Kart 7 (sağlık sigortası şartı), kaynaklar 185 + 035
- Ulusal vize için asgari kapsam/tutar kaynakta yok; yazılmadı. 30.000 Euro yalnız Schengen vizesine bağlandı.
- Seyahat sigortasından GKV'ye geçiş: kaynakta adım adım süreç yok ve yasal çerçeve kaynakları (140, 139, 195) 2 kaynak sınırı nedeniyle kullanılmadı. Aday listedeki bu alt başlık karta girmedi.
- eGK ve GKV/PKV ayrımı yazılmadı.

### Kart 8 (Sperrkonto), kaynaklar 191 + 192
- İki kaynak da başka ülkelerdeki Alman temsilciliklerinin sayfaları (aynı federal içerik); kartta "Alman dış temsilcilikleri" denildi, ülke adı yok. Sayfalardaki ülkeye özgü içerik (yerel banka durumu, belirli bir büyükelçiliğin randevu ve işlem ücreti, yerel sağlayıcı önerileri, ülkeye özgü kimlik belgeleri) yazılmadı.
- Kaynak 191 sayfası 01.07.2025 tarihli; 992 Euro 192'de "Stand 2026". 1.091 Euro (Fırsat Kartı/araştırmacı) yalnız 191'de ve 2025 tarihli; kartta bu tarihle atıfla yazıldı. Bu tutar için 2026 doğrulaması kaynakta yok.
- valid_until: 2026-12-31 (992 Euro "Stand 2026").
- Ticari sağlayıcı adları (Fintiba, Expatrio vb.) yazılmadı.

### Kart 9 (resmî dil ve saat), kaynaklar 196 + 197
- 2 kaynak sınırı: euro (199, BBankG md. 14) ve yaz saati dönemi (198, EinhZeitG md. 5: 1 Mart-31 Ekim arası, pazar günü başlar/biter) karta girmedi. Aday listede para birimi de vardı; kartta yok. Editör ek kart ya da kaynak değişikliği düşünebilir: 198 ve 199 zaten hazır, 197 ile 198 birlikte bir "saat" kartı, 199 ile bir "euro" kartı olabilir.
- VwVfG md. 23'ün yalnız federal makamları mı yoksa eyalet makamlarını da kapsadığı kaynakta yok; kart "idari usul yasası (VwVfG md. 23)" diye yazıldı, kapsam genellemesi yok.
- Türkiye ile saat farkı hesabı yazılmadı.

## Genel dikkat notları
- Kart başına en çok 2 kaynak kuralı 3, 7 ve 9. kartlarda bilgi sınırladı (yukarıda).
- Alıntıların tamamı kaynak metninde birebir doğrulandı; pack_check çıkışı için bkz. dönüş.
- İkincil kaynak (verbraucherzentrale, handbookgermany) kullanılmadı.
- Kart 1 ve 2 işlem sırası ve randevu için tuerkei.diplo.de sayfalarına dayanır; bu sayfalar hızlı değişir (bekleme süreleri, ücretler).


## Editör turu (G2, 25.10.2026): bağımsız denetim bulgularının uygulanması

- 801: Kaynak (AufenthG, BMG md. 17) sağlık sigortasını giriş ve Anmeldung'a göre sıralamıyor. Kartta yalnız kaynaklı sıra kaldı: ulusal vize girişten önce; oturum belgesi vizeyle giriş ve vize başvurusunda verilmiş bilgileri ister; adres kaydı taşındıktan sonra 2 hafta içinde. Sigorta, geçim güvencesinin parçası olarak (AufenthG md. 2/3, md. 5) girişten önceki adımlara alındı. Oturum başvurusunun adres kaydından önce ya da sonra yapılacağı kaynakta yok; kartta sıra iddiası yok. Başlık "hangi sırayla" sorusunu koruyor, slug değişmedi.
- 802: Ulusal D vizesi ücreti (75 EUR, AufenthV md. 46, kaynak 043) karta alınamadı: kart başına 2 kaynak sınırında 041 (bekleme süreleri, parmak izi, uyarılar) ve 042 (Auslandsportal çevrim içi başvuru, 12 EUR) birlikte vazgeçilmez. Kart "temsilciliğin güncel uyarı sayfasına göre en çok 90 EUR" der; 90 EUR'nun Schengen tavanı olduğu 041 metninde açık yazmıyor, bu yüzden "Schengen" etiketi kullanılmadı. Ulusal vize ücreti (75 EUR) oturum konusundaki ulusal vize kartında.
- 802: Çelişki: 041 "Terminbuchung kostenlos", 042 "Je nach Konstellation ... Servicegebühr 39,92 € und/oder Terminbuchungsgebühr von 12 €". Kart ikisini de sayfa atfıyla veriyor. Çelişkinin hangi randevu türünde geçerli olduğu iki sayfada da yok.
- 802: İşlem süresi (en az 15 gün, bazı durumlarda 45 gün) ve bayram/Noel uzaması 041'de Schengen başvuru bölümünde; ulusal vize için ayrı işlem süresi kaynakta yok. Kartın zamanlama alanından çıkarıldı.
- 802: Belge listesi yok (041 belgeleri vize amacına göre listelere taşıyor); documents boş kaldı. Dış hizmet sağlayıcı: 041 "ausschließlich iDATA", 042 "iDATA und IOM-FAP"; kart yalnız iDATA'nın online randevu sistemini ve üçüncü kişilerin erişimi olmadığını söylüyor.
- 806: Türkiye'nin DVO (EU) 2026/636 Ek I ve II'de listelenip listelenmediği kaynakta yok (EUR-Lex metni açılamadı). Türkiye cümlesi kaldırıldı: kaynakta Türkiye, AB'den Türkiye'ye seyahat edenlerin çıkış öncesi testi bağlamında geçiyor. Girişte "AB onaylı laboratuvar" şartı kaynakta yok (yalnız çıkış öncesi bağlamda); karttan çıkarıldı.
- 807: Ulusal vize için somut sigorta şartı kaynakta yok (185 yalnız Auslandsportal ve Merkblatt'a yönlendiriyor); ilgili cümleler silindi, başlık Schengen sigortası ve oturum belgesindeki geçim güvencesi ile sınırlandı.
- 809: Kart kaynağı 196 (VwVfG md. 23) yerine 088 (VwVfG tam metin; md. 1 ve md. 23 aynı metinde) oldu; böylece kapsam kaynaklı: VwVfG federal makamlar için, federal hukuku uygulayan eyalet makamlarında eyaletin kendi usul yasası varsa o uygulanır (md. 1/3). Eyalet usul yasalarının içeriği kaynakta yok, yazılmadı. Bağlantı satırı md. 23 sayfasında kaldı.
- 803: Steuer-ID ayrıntıları (nerede bulunur, 11 hane, kalıcılık) resmi konusundaki Steuer-ID kartında; bu karttan çıkarıldı.
- 805: valid_until.json'a null girişi eklendi (kaynak sayfa tarihsiz). 807 için de null eklendi.
- 808: Tutar Roma ve Yaoundé temsilcilik sayfalarından; Türkiye'deki temsilcilik sayfasında (Bildungsaufenthalte) tutar yok. 1.091 Euro (Fırsat Kartı/araştırmacı) 01.07.2025 tarihli sayfadan, kartta tarihiyle duruyor; 2026 değeri kaynaklarda yok.

## g2b editör turu (25.10.2026)
- Kart 801: Sağlık sigortasının girişten önce yapılması gerektiği 035 (AufenthG) ve 186 (BMG §17) kaynaklarında yok; yalnız 'geçim güvencesi yeterli sağlık sigortasını da kapsar' (AufenthG §2 Abs.3) yazıldı. Giriş öncesi sigorta şartı Schengen/807 kaynağında var; 801 kartının kaynağı değil. Adres kaydı ile oturum başvurusunun zaman sırası iki kaynakta da verilmiyor; kart bu iki adımı sıra iddiası olmadan anlatıyor.
- Kart 802: 'Randevu almak ücretsiz' (041, uyarı sayfası) ile '12 EUR randevu bedeli' (042, ulusal vize sayfası) çelişkisi sürüyor; kartta iki ifade de kaynak atfıyla duruyor, iç not kaldırıldı.

---
# Konu: aile (yazar ve editör notları)

# aile — yazar notları (DE, 2026-10-25)

8 kart, order 901–908. Her kartta en çok 2 `source_ids`; kullanılan kaynaklar aşağıda.

## Kart bazında seçim ve yazılmayan bilgi
- 901 Kindergeld (kaynak 225 + 245): 225 yabancı şartı (Türkiye adıyla sayılıyor, oturum belgesi yolları, eğitim amaçlı kalış ve Gestattung/Duldung hariç); 245 "ab Januar 2026 259 Euro" ve yeni başvuru gerekmez. Başvuru bağlantısı olarak 246 (Kindergeld online beantragen) yalnız bağlantıda kullanıldı, karttaki hiçbir cümle ona dayanmıyor. Yazılmayanlar (246'da var, 2 kaynak sınırı yüzünden): gelirden bağımsızlık, geriye dönük 6 ay sınırı, Bund-ID ile imzasız başvuru, "Kindergeld'i tek kişi alır". EStG §62 Abs. 2 kaynak listesinde yok.
- 902 Elterngeld (228 + 229): süre (14 ay / Plus / Partnerschaftsbonus / 32. yaşam ayı) ve başvuru (3 yaşam ayı, Elterngeldstelle, belgeler). Yazılmayanlar: Elterngeld tutarı (300–1.800 / 150–900 Euro, kaynak listesinde yok), yabancı ebeveyn için oturum belgesi şartı (231: Niederlassungserlaubnis, Mavi Kart AB, 6 ay çalışma izni olan Aufenthaltserlaubnis vb. var; Aufenthaltsgestattung ve Duldung yok), Elternzeit (230: çocuk başına 3 yıla kadar, ücretsiz izin, işçi/işveren). Bu üçü 2 kaynak sınırı nedeniyle çıktı. Ana döngü isterse kart 902'yi 229 + 231'e çevirebilir ya da Elternzeit için ayrı kart açabilir; kart 1'de Elterngeld'in yabancı şartı kaynak sınırı yüzünden yer almıyor.
- 903 Kita (232 + 233): federal hak ve eyalet/belediye çerçevesi. Ücret rakamı, kayıt takvimi, eyalet adı yazılmadı (233'te geçen iki şehir adı da yazılmadı). Ek: §24 Abs. 4 Ganztag hakkı (2026/2027 ilk sınıf) nota girdi.
- 904 Okul (238 + 236): zorunluluk, eyalet yetkisi, yerleşimi Schulbehörde belirler, yıl ortasında kayıt, devlet okulu ücretsiz. Yeni gelen çocuk için dil sınıfı (Willkommens-/Vorbereitungsklasse) YAZILMADI: tek kanıt 237 (Ukrayna 2022 KMK açıklaması) ve kartta kullanılmadı. Okul türleri, okul kaydı takvimi, eyalete özgü yaş sınırı yazılmadı.
- 905 Yabancı diploma (239 + 240): Türkiye diplomasının hangi gruba girdiği kaynakta yok, yazılmadı. 239'daki Sperrkonto (992 Euro/ay, 11.904 Euro/yıl, 1 Ocak 2025'ten) bu kartın konusu değil, kullanılmadı. Kartta vize/Sperrkonto yok.
- 906 BAföG (241 + 242): §8 uyruk/oturum şartı ve §13 ihtiyaç tutarları. Başvuru yolu (Amt für Ausbildungsförderung, BAföG Digital) kaynakta yok, yazılmadı. Öğrenci vizasıyla gelen Türk öğrencinin BAföG durumu hakkında açık cümle kaynakta yok, yorum katılmadı. Tutarlar yasa metninin güncel sürümünden; sayfada yıl/bitiş tarihi olmadığından valid_until null. §13 tutarının ödenecek aylık destekle ilişkisi (gelir/servet hesabı) yazılmadı. §8 Abs. 2'deki bütün oturum izni paragrafları sayılmadı (yalnız Niederlassungserlaubnis'li birinin eşi/çocuğu örneği).
- 907 Unterhaltsvorschuss + Kinderzuschlag (243 + 244): Unterhaltsvorschuss tutarları "ab 1. Januar 2025" etiketiyle yazıldı (2026 tutarı kaynak listesinde yok). Kinderzuschlag 297 Euro: 243'te yıl yok; 2026 tarihli teyit 245'te (kart 7'ye 3. kaynak olamadığı için kullanılmadı). valid_until 2026-12-31, görev mesajındaki talimata göre verildi; kaynak sayfa kendisi bitiş tarihi söylemiyor. Yabancı için Kinderzuschlag: 243 yalnız AB/AEA/İsviçre vatandaşları ile kesinleşmiş sığınma hakkı sahiplerini sayıyor, bu atıfla yazıldı; Kindergeld'e bağlı oturum izni gruplarıyla ilişkisi kaynakta açık değil, yorum katılmadı. Yazılmayanlar: Kinderzuschlag servet sınırları (55.000/70.000 Euro), UV'de Halbwaisenrente ve gelir mahsubu ayrıntıları.
- 908 Doğum sonrası sıra ve çocuğun sağlık güvencesi (234 + 141): Standesamt 1 hafta, ad bildirimi 1 ay, Geburtsurkunde, Familienversicherung yaş sınırları (18/23/25) ve §10 dışlamaları. Aile sigortasının "beitragsfrei" olduğu 235'te var, kart 2 kaynak sınırı nedeniyle 141'i seçtiği için yazılmadı. Gelir sınırı tutarı (Bezugsgröße'nin 1/7'si) yıla bağlı ve kaynakta tutar yok, yazılmadı. Yabancı ebeveynin çocuğu için oturum izni (AufenthG §33) ve Türk konsolosluğu kaydı kaynakta yok, yazılmadı. Doğum kaydı ayrıntıları (de:resmi, order 209) tekrar edilmedi; kart 908 yalnız sıra ve sağlık güvencesini anlatıyor.

## Kullanılmayan kaynaklar
- 226 (EStG §66, 259 Euro; yıl etiketi yok), 227 (Was ist Kindergeld; "derzeit 259"), 230 (Elternzeit), 231 (Elterngeld yabancı), 235 (Familienversicherung Familienportal), 237 (KMK Ukrayna 2022): kart başına 2 kaynak sınırı ve zayıf kanıt nedeniyle. 246 yalnız bağlantı olarak kullanıldı.

## Dikkat notları
- Kart 901'in bağlantılarından biri (246) kartın source_ids'inde yok; pack_check yalnız adresin kaynak dizininde olmasını arıyor. İstenirse 246 bağlantısı çıkarılıp yalnız 225'e bırakılabilir.
- Kart 902 başlığındaki "Elternzeit" ve yabancı şartı yok; aday plan satırı "Elterngeld ve Elternzeit" idi, Elternzeit çıktı (yukarıda).
- Kart 905'te Studienkolleg başvuru adımı, kaynağın "doğrudan başvuru çoğu devlet Studienkolleg'inde mümkün değil; üniversiteye ya da uni-assist üzerinden" ifadesine dayanır.
- Tarihe duyarlı kart: 901 (2026-12-31), 907 (2026-12-31; UV kısmı 1 Ocak 2025 etiketli). 902 ve 906 null (kaynakta bitiş yok).

## Editör turu (G3) — güncel durum ve boşluklar
- 901 Kindergeld: kaynaklar 225 + 246 oldu (245 çıkarıldı; 246 geriye dönük 6 ay sınırı, gelirden bağımsızlık, Bund-ID, tek kişi kuralını veriyor). 245'e dayanan "Ocak 2026" etiketi ve "yeni başvuru gerekmez" cümlesi kalktı; tutar "güncel tarife" etiketli, valid_until null. Yazılamayanlar: EStG §62 Abs. 2'deki ayrıntı (öğrenim izni §16b ile kalan kişi çalışıyorsa, Elternzeit ya da SGB III parası alıyorsa dışlanmaz); bu metin üçüncü kaynak olacağından eklenemedi, kart cümlesi Familienportal'a atfedildi. İstenirse 901 için ayrı bir "Kindergeld ve öğrenim izni" kartı + EStG §62 kaynağı gerekir.
- 902 Elterngeld: yabancı ebeveyn için oturum izni şartı (kaynak 231 hazır: Niederlassungserlaubnis, Daueraufenthalt-EU, Mavi Kart AB, ICT, en az 6 ay çalışma izni olan Aufenthaltserlaubnis, Beschäftigungsduldung; Gestattung ve Duldung hariç) 2 kaynak sınırına sığmadı. Öneri: ayrı kart "Elterngeld yabancı ebeveyn için kim alabilir" (kaynak 231 + BEEG §1 Abs. 7/8, gelir üst sınırı 175.000 Euro BEEG §1 Abs. 8 için yeni kaynak). Ayrı Elternzeit kartı da gerekli (kaynak 230: çocuk başına 3 yıla kadar ücretsiz izin; iş güvencesi ve süre ayrıntısı için BEEG §15 kaynağı eklenmeli).
- 903 Kita: kart 907 (Kinderzuschlag/kreş muafiyeti) ve bu kart aynı konuyu iki kaynağın sözcüğüyle yazıyor (233 "veli payı ödemezsin", 243 "muaf olabilir"); kaynaklar farklı olduğu için sözcükler ayrı bırakıldı.
- 906 BAföG: ödenecek aylık tutar için gelir/servet hesabı (BAföG § 11) kaynakta yok; yazılmadı. Başvuru yolu (Amt für Ausbildungsförderung, BAföG Digital) kaynakta yok.
- 907: Unterhaltsvorschuss tutarları "1 Ocak 2025'ten itibaren" etiketiyle kaldı; 2026 tutarı doğrulanamadı (MindUntV sayfası erişilemedi). valid_until null. Kinderzuschlag 297 Euro yıl etiketsiz ("güncel tarife"); 2026 tarihli teyit kaynak 245'te var ama 3. kaynak olamaz.
- 908: bebeğin oturum izni (AufenthG §33) ve Kindergeld başvurusu adımları bu kartın 2 kaynağında yok; Kindergeld için kart 901, doğum kaydı için resmi/209 var. Aile sigortası kart 602 ile aynı SGB V §10 metnine dayanıyor, içerik çelişmiyor.
- Kullanılmayan kaynaklar (güncel): 226, 227, 230, 231, 235, 237, 245.

## Editör turu (G3b, dar denetim sonrası)
- 901: eğitim amaçlı kalış cümlesi kaynak 225'in "Kindergeld verilmeyen haller" listesine bağlandı ("alamazsın" kalktı). EStG §62 istisnası (öğrenim izniyle kalıp çalışan, Elternzeit ya da SGB III parası alan kişi dışlanmaz) hâlâ yazılamadı: ayrı "Kindergeld ve öğrenim izni" kartı + EStG §62 kaynağı gerekir.
- 902: yabancı ebeveyn oturum izni şartı (BEEG §1 Abs. 7, kaynak 231) uygulanamadı: 228 çıkarsa süre/Partnermonate (15 claim), 229 çıkarsa başvuru yeri/belgeler (14 claim) çöker. Ayrı kart notu geçerli: "Elterngeld yabancı ebeveyn için kim alabilir" (kaynak 231 + BEEG §1 Abs. 7/8).
- 907: yabancı Kinderzuschlag cümlesi kaynak 243'ün kendi listesiyle yazıldı (AB/AEA/İsviçre vatandaşları ve kesinleşmiş sığınma hakkı sahipleri + genel şartlar). 243 bu listede Türk vatandaşı için Kindergeld yolunu saymıyor; 901 ile ilişki kaynakta açık olmadığından yorum katılmadı (bölge/ek kart: BKGG §6a kaynağı gerekir). Kreş muafiyeti ifadesi 903 (233 "ödemezsin") ile 907 (243 "muaf olabilir") kaynak sözcüklerine bağlı kaldı.
- 908: SGB V §10 Abs. 3 kapsamı "çocuğun anne ya da babası olan eş ya da hayat ortağı" olarak 602 ile aynı yazıldı. Evli/hayat ortaklığı olmayan ebeveyn için kuralın uygulanmadığı kaynakta açık yazmıyor, yazılmadı.

---
# Konu: ulasim (yazar ve editör notları)

# ulasim yazar boşlukları (25.10.2026)

## Kart yapısı (aday listeden sapmalar)
- Aday 7 kart, çıktı 10 kart. Kart 2 ikiye bölündü (bilet iptali / gecikme ve şikâyet; her biri ayrı soru, kaynaklar ayrık). Kart 4 üçe bölündü (hız / alkol / Probezeit ve puan sistemi), her kart ≤2 kaynak. Sıra: 1001 Deutschlandticket, 1002 bilet iptali, 1003 tren gecikmesi, 1004 Türk ehliyeti, 1005 hız, 1006 alkol, 1007 Probezeit ve puan, 1008 HU ve Kfz-Steuer, 1009 uçuş, 1010 e-scooter ve bisiklet.
- Kart 4 kaynakları editör turunda değişti: de:kaynak:221 (BMV) ve de:kaynak:208 (FeV § 29); de:kaynak:209 (Anlage 11) karttan çıkarıldı.

## Kart bazında yazılmayan bilgi
- Kart 1 (Deutschlandticket): Verbund-Abo'ya geçiş, Deutschlandsemesterticket (1 Haziran 2027'den fiyat), DB Benefits/BahnBonus, 60 yüzde ICE/IC Mehrfahrtenticket kampanyası yazılmadı (yan konu). Onay/iptal koşulları yalnız Deutsche Bahn (DB Regio) için; başka şirketlerin süreci kaynakta "bu şirketlere başvurun" diye geçiyor, yazılmadı. valid_until 2026-12-31 (63 Euro'nun bitişi).
- Kart 2 (bilet iptali): Sparpreis Gruppe (online 19 Euro, Reisezentrum 5 Euro), Fahrradkarte ve 1. Klasse-Upgrade iptal koşulları, Sitzplatzreservierung iptali yazılmadı. Sebep: sayfada "3 saat içinde iptal edilebilir" ile "yer ayırtma iptal ya da yeniden ayırtma mümkün değil" iki ayrı yerde farklı söyleniyor; çelişkiyi çözecek ek metin yok. Ücretler (10/19/30 Euro) tarihsiz sayfa; valid_until null. AB 2021/782 metni kaynakta yok.
- Kart 3 (gecikme): Infotelefon Fahrgastrechte numarası ve saatleri yazılmadı (metin bir eyaletin tatil günlerini ayırıyor; eyalet adı kuralı). EBA ve Schlichtungsstelle posta adresleri yazılmadı (şehir adı içerir). Deutschlandticket için gecikme tazminatı yazılmadı: bahn.de sayfası Zeitfahrkarte listesinde Deutschlandticket'ı adıyla anmıyor. BahnCard 100, Interrail/Eurail, Eurostar, AJC anlaşması, uluslararası bilet, DB Gepäckservice bölümleri yazılmadı. Diğer tanınmış uzlaştırma kurumlarının (SRUV, SNUB, Streitbeilegungsstelle, Universalschlichtungsstelle) ayrıntıları yazılmadı; yalnız Schlichtungsstelle Reise & Verkehr e.V. adı verildi. AB 2021/782 tüzük metni kaynakta yok; haklar yalnız bahn.de ve EBA sayfalarının dediği kadar.
- Kart 4 (Türk ehliyeti): "Türkiye için tam sınav" ve "Türkiye Anlage 11'de yok" cümleleri hiçbir kaynakta açık yazılı olmadığı için YAZILMADI (editör turunda Anlage 11 cümlesi silindi). Alman ehliyeti başvuru belgeleri, ücreti, sınav kapsamı (FeV § 30, § 31 metni listede yok) yazılmadı. BMV'nin Ocak 2026 taslağı (Anlage 11 değişikliği) doğrulanmadığı için yazılmadı. Sayfa tarihi 02.03.2026.
- Kart 5 (hız): Otoyol Richtgeschwindigkeit 130 km/h kaynakta yok, yazılmadı. 7,5 ton üstü ve ayakta yolcu taşıyan otobüs için 60 km/h, 3,5-7,5 ton arası araçlar yazılmadı (alıntı uzunluk sınırı ve kart sadelik). Hız ihlali para cezaları ve Fahrverbot (Bußgeldkatalog) kaynakta yok.
- Kart 6 (alkol): "0,0 promil" ifadesi §24c metninde geçmez; kart "alkollü içecek içmek yasak" diye yazıldı. Bisiklet için alkol sınırı, § 316 StGB (suç sınırı) kaynakta yok. § 24c ihlalinde para cezası tutarı kaynakta yok.
- Kart 7 (Probezeit/puan): "Flensburg" adı kaynak metinlerde yok, kartta kullanılmadı (ana döngü anahtar sözcük olarak eklemek isterse ekleyebilir). Hangi ihlalin kaç puan getirdiği (Anlage 13 FeV), puan silme süreleri (Tilgungsfristen), KBA sayfası kaynakta yok. EU/AEA ehliyetli kişiler için Probezeit uygulaması yazılmadı (Türk okuyucu odağı).
- Kart 8 (HU/Kfz-Steuer): HU/AU ücretleri eyalet ve kuruluşa bağlı, yazılmadı; muayene kuruluşu adı kaynakta yok. Taksi/ambulans 12 ay, otobüs, motosiklet vergisi (1,84 Euro/25 cm³), Wohnmobil, römork, Oldtimer, 2009 öncesi araç tarifeleri yazılmadı. Vergi sayfası tarihsiz: valid_until null. Çakışma: resmi konusundaki "arac-kaydi-i-kfz-evb-hu-ve-kfz-steuer-sepa" kartı HU ve Kfz-Steuer SEPA'dan söz ediyor; bu kart HU süreleri ve vergi hesabı üzerine, editör turunda çakışma gözden geçirilsin.
- Kart 9 (uçuş): Uçağa alınmama (Nichtbeförderung) için tazminat tutarları (kaynak yalnız "mesafeye göre" diyor), düşük sınıfa alma iadeleri (30/50/75 yüzde), Betreuungsleistungen ayrıntısı (otel, transfer), söp ve Bundesamt für Justiz iletişim bilgileri yazılmadı. Online dava hizmeti (service.justiz.de) kaynak listesinde yok. AB 261/2004 tüzük metni kaynakta yok; haklar yalnız LBA sayfalarının dediği kadar.
- Kart 10 (e-scooter/bisiklet): "Kask zorunlu değil" iddiası kanıtlanamadığı için yazılmadı. Bisiklet için alkol sınırı yok. Fren, aydınlatma, tabela teknik ayrıntıları, yabancı plakalı e-scooter (§ 2a), Ordnungswidrigkeit tutarları yazılmadı. Sürücüsüz 500 Watt güç sınırı (özel dengeleme için 1.400) kartta yok.

## Dikkat notları
- valid_until.json: yalnız Deutschlandticket (2026-12-31); bilet iptal ücretleri ve Kfz-Steuer tarifeleri tarihe duyarlı ama kaynak tarihsiz, null.
- Deutschlandticket 63 Euro yalnız 31.12.2026'ya kadar; 1.1.2027'den 66,80 Euro (bahn.de, Stand Ekim 2026). Kartta iki tutar da tarihiyle yazıldı.
- Kart 9'da LBA sayfaları tarihsiz; kart 4'te BMV sayfası 02.03.2026.
- Eyalet kuralı: kartlarda eyalet adı ve rakamı yok; HU/AU ücretleri ve yerel ulaşım birliği tarifeleri şehir/bölge katmanına bırakıldı.
- pack_check çıkış 0 (10 kart, 202 claim, 18 bağlantı).

## Editör turu (25.10.2026)
- Kart 6 (alkol): sınırın altı için güvence verilmez; alkole bağlı sürüş suçu maddeleri (StGB) kaynak listesinde olmadığı için yazılmadı.
- Kart 10 (e-scooter): sigorta pulunun nasıl edinileceği (FZV § 56) yazılmadı; kaynak gerekir.
- Kart 8 (HU/Kfz-Steuer): Zoll sayfası tarihsiz olduğu için "güncel tarife" ibaresi kondu; valid_until null kalır.
- Kart 3 (gecikme): Deutschlandticket için gecikme hakkı yazılmadı; kaynak süreli bilet örnekleri arasında adıyla saymıyor.

## Editör turu (G3b, dar denetim sonrası)
- Yalnız küçük metin düzeltmeleri (1002 note cümlesi silindi, 1003/1005/1009 ifade, 1004 adım 3 BMV "auf Antrag" cümlesiyle tamamlandı). Yeni bilgi boşluğu yok.

---
# Konu: gunluk (yazar ve editör notları)

# gunluk - yazar gaps (25.10.2026)

9 kart (adayda 7; kart 6 kaynak sınırı yüzünden üçe bölündü), 128 claim, kart başına en çok 2 kaynak. order 1101-1109, tarih 2026-10-25.
valid_until.json: kart 1 = null (tarih iddiası yok, tutar yok); kart 4 ve 7 = 2026-12-31 (kaynakta bitiş tarihi yok; ücret/uygulama 2026 dönemi).

## Kart yapısı kararı
- Aday kart 6 (110, 112, 116117, 115, kadın hattı) dört ayrı kaynaktan geliyor; 2 kaynak sınırına sığmadığı için üç karta ayrıldı: 1106 (112 + 116117, kaynaklar 259 + 143), 1108 (Hilfetelefon 116 016, kaynak 261), 1109 (115, kaynak 260). Gerekirse 1108 ve 1109 birleştirilebilir/atılabilir; 1101-1107 aday tablosuyla birebir.

## Kart bazında yazılmayan bilgi
- Kart 1 (tatil): tarih listesi (Karfreitag, Ostermontag, Christi Himmelfahrt vb.), "8 ortak gün" ve "tek federal tatil" cümlesi kaynakta yok, yazılmadı. Art. 140 GG (Pazar ve tatil anayasal korumada) 2 kaynak sınırı yüzünden kart 2'ye taşındı (kaynak 008); kart 1 kaynakları 132 (Einigungsvertrag Art. 2) + 262 (Destatis).
- Kart 2 (mağaza saatleri): "eyaletler kendi yasasını çıkardı / saatler eyalete göre değişir" cümlesi kaynakta açık değil, yazılmadı. Art. 125a GG (kaynak 264) maddede "Ladenschluss" geçmediği ve çıkarım gerektirdiği için kullanılmadı; kart yalnız "federal Ladenschlussgesetz §3 genel saatleri" olarak çerçevelendi. DİKKAT: okuyucu kuralı ülke geneli sanabilir; eyalet düzeyi saatler bölge paketine/ek kaynağa gider (LadSchlG §27 gibi derin sayfa, 500 karakter altı olduğu için elenmişti).
- Kart 3 (Pfand/ElektroG): atık ayrımı (sarı torba/kutu) kartta yok (kaynak 250 ve belediye farkı kanıtsız, 2 kaynak sınırı); kaynak 248 (ElektroG §17: aynı türden cihaz 1:1, her cihaz türünden en çok 3 cihaz, teslimatta evden alma) kullanılmadı, kaynak 249 (UBA) özetiyle yetinildi. UBA'daki 2.400 toplama noktası rakamı (2022 durumu) yazılmadı. VerpackG §31 değil VerpackDG §46 kullanıldı. Alkol/spirit ve karton ambalaj istisnaları ayrıntılandırılmadı.
- Kart 4 (AB dışı paket): işlem ücretinin (Abfertigungspauschale) tutarı yalnız Zoll'un örneğindeki 2 Euro ile verildi, "planlanan/şu anki duruma göre" ifadesiyle; kategori başı kural tutarı sayfada ayrıca yazmıyor. "Mal kalemi" değil kaynağın "Warenkategorie" terimi kullanıldı. 150 Euro üstü paket hesabı, 45-700 Euro arası hediye sadeleştirilmiş oranları, alkol/tütün/parfüm/kahve hediye miktar sınırları yazılmadı (kart dışı/ayrıntı). Türkiye'ye özgü bir gümrük kuralı kaynakta yok, yazılmadı.
- Kart 5 (posta): Einschreiben tanımı/ücreti, Nachsendeauftrag ücreti kaynakta yok. Schlichtungsstelle Post (kaynak 258: ücretsiz, 10-2.500 Euro uyuşmazlık değeri, önce şirkete başvuru şartı) 2 kaynak sınırı yüzünden kullanılmadı; kartta yalnız "arabuluculuk söz konusu olabilir" denildi (kaynak 257). PostG §18 (kaynak 255) aynı sayıları taşıyan kaynak 256 seçildiği için kullanılmadı. "Werktag" kaynakta iş günü olarak karşılanmadı; kart "iş günü (Werktag)" yazıyor.
- Kart 6 (112/116117): 110'un ne olduğu (polis) ve ücretsiz olduğu kaynakta yok; yalnız "110 veya 112'ye Notruf-Fax" cümlesi yazıldı. Bundesnetzagentur Notruf sayfası elendiği için 110 için başka kaynak yok.
- Kart 7 (Almanca kursu): Integrationskurs muafiyetinde gelir eşiği tutarı kaynakta yok (başvuru formunda), yazılmadı; Berufssprachkurs için kaynağın yüzde 33 (prim tavanı) ifadesi tutarsız hesap yapılmadan verildi. AB vatandaşı/Alman/Spätaussiedler alt sayfaları ve "2005 öncesi" varyantı kullanılmadı; kart yalnız 2005 sonrası oturum belgesi sahipleri için. 01.08.2022 öncesi kayıt ücreti (2,20 Euro / 1 540 Euro) yazılmadı. Fahrtkosten (5 km) yazılmadı.
- Kart 8 (Hilfetelefon): 18 dilin listesi kaynakta yok (Türkçe dahil mi bilinmiyor), yazılmadı. Acil tehlikede 112 yönlendirmesi bu kaynakta yok.
- Kart 9 (115): arama ücreti kaynakta yok, yazılmadı. Hizmet dilleri kaynakta yok.

## Kullanılmayan kaynaklar
- de:kaynak:248 (ElektroG §17), 250 (UBA Verpackungen), 255 (PostG §18), 258 (Schlichtungsstelle), 264 (Art. 125a GG): kart başına 2 kaynak sınırı ve yukarıdaki gerekçeler.

## Dikkat notları
- Kart 2 kapsamı: "federal Ladenschlussgesetz'in genel saatleri" olarak sınırlı; eyalet farkı cümlesi eklenmedi (kaynak açık değil).
- Kart 4 ve 7 sayfaları 2026 durumunu yansıtıyor; 1 Kasım 2026 işlem ücreti henüz yürürlükte değil (bugün 25.10.2026).
- Kart 5 teslim süreleri yıllık ortalama içindir; tek gönderi için hak yoktur (kartta belirtildi).
- Kart 9'da 115'in "tüm eyaletlerde" kullanılabilirliği kaynak 260'a göre; eyalet adı yazılmadı.

## Editör turu (g3, 25.10.2026)
- Kart 2 (mağaza saatleri) yeniden çerçevelendi: kaynaklar GG md. 74 (de:kaynak:268, editör ekledi) + GG md. 125a (264). LadSchlG md. 3 saatleri, 24 Aralık 14:00 ve fırın 05:30 kuralı ile GG md. 140 (Pazar/tatil koruması) karttan çıktı (2 kaynak sınırı); eyalet saatleri ve rakamları bölge paketine gider. Kaynak 263 ve 008 bu kartta artık kullanılmıyor.
- Kart 4 (AB dışı paket): valid_until 2026-10-31 (1 Kasım 2026 işlem ücreti cümlesi sonrasında güncellenmeli). Postacı/kurye hediye muafiyetini isteme şartı ve %7 KDV'nin uygulama alanı kaynak metninde yok, yazılmadı.
- Kart 3: ElektroG md. 17/1 "cihaz türü başına en çok üç cihaz" sınırı karta alınmadı (kaynak 248 kullanılmıyor).
- Kart 6 ve saglik/605 büyük ölçüde aynı soruyu cevaplıyor; birleştirme/sadeleştirme kararı ana döngüde.

## Editör turu (G3b, dar denetim sonrası)
- 1102: "mağaza saatleri eyalete göre değişir" sonucu kaynak 268/264 (GG md. 74, 125a) ile kanıtlanamadığı için çıkarıldı; kart yalnız yetkinin federal alanın dışında olduğunu ve eski federal düzenlemenin eyalet hukukuyla değiştirilebildiğini söylüyor. Eyalet Ladenöffnungsgesetze ve Pazar/tatil koruması (GG md. 140) için bölge paketi ya da yeni kaynak gerekir.
- 1107: "BSK için oturum belgesi şartı yok" cümlesi kaynaksız olduğundan silindi. A2/B1 hedefli BSK'nın Integrationskurs'a rağmen B1'e ulaşamama şartı eklendi (kaynak 254).
- 1104: "belirli gönderiler" hangi paketleri kapsıyor, Zoll sayfası söylemiyor; kart "gönderiye göre" diye nötr bıraktı.
- 1106 ↔ saglik/605 tekrarı editoryal paket kararı olarak açık.
