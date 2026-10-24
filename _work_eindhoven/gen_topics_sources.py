# Konular + Kaynaklar üretim scripti
import json, os, glob

CITY = "eindhoven"

TOPICS = [
 ("planlama","Taşınmadan önce plan","İlk kararlar, belge dosyası, bütçe ve zamanlama","book",0),
 ("oturum","Vize, oturum ve çalışma hakkı","IND, oturum türleri, kennismigrant, aile ve öğrenci","plane",1),
 ("resmi","Kayıt ve resmî işlemler","BRP kaydı, BSN, DigiD, belge ve bildirimler","shield",2),
 ("ev","Ev ve yerleşim","Konut arama, sözleşme, depozito, kiracı hakları","home",3),
 ("fatura","Elektrik, su, ısınma ve internet","Abonelikler, sayaç, taşıma ve kapanış","bolt",4),
 ("para","Banka, vergi, sigorta ve destekler","Hesap, iDEAL, aangifte, toeslag, zorgverzekering","transfer",5),
 ("saglik","Sağlık ve bakım","Huisarts, hastane, acil, eczane, diş, psikoloji","heart",6),
 ("is","İş ve kariyer","Brainport iş piyasası, sözleşme, haklar, ağ kurma","briefcase",7),
 ("aile","Aile, eğitim ve çocuk","Okul, kreş, üniversite, çocuk destekleri","family",8),
 ("ulasim","Ulaşım","Havalimanı, tren, otobüs, bisiklet, araç ve park","train",9),
 ("gunluk","Günlük yaşam ve topluluk","Alışveriş, atık, güvenlik, dil, Türk toplumu","bag",10),
 ("kesif","Keşif, kültür, sanat ve spor","Müzeler, sahne, parklar, rotalar, etkinlikler","people",11),
]

# cache_id -> (TR başlık, yayıncı, konu, TR araştırma notu)
SRC = {
 "gemeente-inschrijven-buitenland": ("Yurt dışından Eindhoven'a taşınma: kayıt süreci","Gemeente Eindhoven","resmi","Yurt dışından gelenler varıştan sonra 5 gün içinde Inwonersplein'de şahsen kayıt yaptırmalı; randevu online veya 14 040 (yurt dışından +31 40 2386000) ile alınıyor. 4 aydan kısa kalışlar için RNI kaydı geçerli. Kayıt sonrası 4 hafta içinde teyit mektubu geliyor."),
 "gemeente-verhuizen-binnen": ("Hollanda içinde veya şehir içi taşınma bildirimi","Gemeente Eindhoven","resmi","Taşınma, 4 hafta öncesinden 5 gün sonrasına kadar DigiD ile dijital bildirilebiliyor; veriler BRP'ye işleniyor ve Belastingdienst, DUO, SVB, UWV gibi kurumlara otomatik iletiliyor. Balie ve posta seçenekleri de var."),
 "gemeente-verhuizen-keuze": ("Taşınma senaryosu seçim sihirbazı","Gemeente Eindhoven","resmi","Gemeente'nin 'Verhuizen? Dit moet je doen' akışı; şehir içi, başka belediye, yurt dışı ve RNI senaryolarını ayırıyor."),
 "gemeente-brp-uittreksel": ("BRP kayıt örneği (uittreksel) başvurusu","Gemeente Eindhoven","resmi","Uittreksel DigiD ile online isteniyor, ücret online ödeniyor, 5 iş günü içinde postayla geliyor. Konut korporasyonuna kayıt için gereken belge bu."),
 "gemeente-woning-huren": ("Eindhoven'da konut kiralama rehberi","Gemeente Eindhoven","ev","Sosyal konut için korporasyonlar ('thuis, Trudo, Woonbedrijf, Wooninc) ve Wooniezie platformu; acil durumda SGE urgentie rejimi; özel kirada Huurteam Eindhoven ve Meldpunt Goed Verhuurderschap; sosyal kirada Huurcommissie."),
 "wooniezie-inschrijven": ("Wooniezie sosyal konut kaydı","Wooniezie","ev","Eindhoven-Helmond bölgesinin sosyal konut portalı; kayıt ücretsiz, 18+ ve Hollanda'da oturma hakkı şart; gelir beyanı (inkomensverklaring) eklenmesi öneriliyor."),
 "sge-urgentie": ("Stedelijk Gebied Eindhoven urgentie rejimi","Stedelijk Gebied Eindhoven","ev","9 belediyede tek urgentie düzeni; koşullar stedelijkgebiedeindhoven.nl'de."),
 "goedverhuurderschap": ("İyi ev sahipliği bildirim noktası","Gemeente Eindhoven","ev","Özel kirada kötü muamele, ayrımcılık, çift komisyon, aşırı depozito bildirimleri buraya yapılıyor."),
 "huurteam-eindhoven": ("Huurteam Eindhoven kiracı danışmanlığı","Huurteam Eindhoven","ev","Özel kiralık konutta kiracıya ücretsiz danışmanlık ve destek."),
 "huurcommissie": ("Huurcommissie kira uyuşmazlıkları","Huurcommissie","ev","Kira fiyatı, hizmet bedeli ve bakım uyuşmazlıklarında resmi hakem kurum."),
 "gemeente-studenten": ("Öğrenciler için konut bilgisi","Gemeente Eindhoven","ev","Öğrenci odası/konutu arama kanalları ve kuralları."),
 "trudo": ("Trudo konut korporasyonu","Trudo","ev","Eindhoven'daki sosyal konut korporasyonlarından biri."),
 "woonbedrijf": ("Woonbedrijf konut korporasyonu","Woonbedrijf","ev","Eindhoven'ın en büyük sosyal konut korporasyonlarından."),
 "thuisthuis": ("Woonstichting 'thuis","Woonstichting 'thuis","ev","Eindhoven sosyal konut korporasyonu."),
 "gemeente-verblijfsvergunning": ("Oturum izni ve IND başvuru noktaları","Gemeente Eindhoven","oturum","En yakın IND loketi Den Bosch; randevu 088 043 04 30. EU vatandaşları için oturum izni gerekmiyor. Hollanda'da 3 aydan uzun kalacak yabancılar IND'ye başvuruyor."),
 "ind-residence-permits": ("Oturum izni türleri genel bakış","IND","oturum","Kısa kalış, çalışma, eğitim, aile, AB vatandaşı ve uzun dönem EU statüsü izin türlerinin resmi listesi."),
 "ind-hsm": ("Kennismigrant (yüksek nitelikli göçmen) izni","IND","oturum","Yalnız IND tarafından tanınmış sponsor işverenin başvurabildiği, gelir kriterine bağlı hızlı prosedür."),
 "ind-eu-stay": ("AB/AEA/İsviçre vatandaşlarının kalışı","IND","oturum","EU vatandaşları için oturum izni gerekmez; belirli durumlarda kayıt/kart seçenekleri var."),
 "ind-study": ("Öğrenci oturum izni","IND","oturum","Üniversite/HBO öğrencileri için sponsorlu oturum izni prosedürü."),
 "ind-orientation-year": ("Zoekjaar (oryantasyon yılı) izni","IND","oturum","Mezuniyet sonrası 1 yıl iş arama izni."),
 "ind-desks": ("IND loketleri ve hizmet noktaları","IND","oturum","Eindhoven için: Holland Expat Center South (IND Service Point, Stadhuisplein 10) ve en yakın IND desk Den Bosch."),
 "rijksoverheid-inburgering": ("Wet inburgering 2021 entegrasyon sistemi","Rijksoverheid","oturum","2022'den itibaren belediye yönetiminde entegrasyon; B1-route, onderwijsroute, zelfredzaamheidsroute; 3 yıl süre."),
 "rijksoverheid-inburgeren-qa": ("Kimler inburgeren zorunlusu?","Rijksoverheid","oturum","EU/EEA/İsviçre vatandaşları muaf; Türk vatandaşları yeni sistemle yükümlü grupta; 18 yaş altı ve bazı gruplar hariç; DUO mektup gönderiyor."),
 "rijksoverheid-bsn": ("BSN nedir, nasıl alınır?","Rijksoverheid","resmi","BSN, BRP kaydında verilen 9 haneli kişisel numara; pasaport/ehliyet üzerinde görünür."),
 "digid": ("DigiD dijital kimlik","Logius / Rijksoverheid","resmi","Kamu hizmetlerine giriş için resmi dijital kimlik; BRP kaydı ve BSN ile alınır."),
 "gemeente-openingstijden": ("Inwonersplein adres ve açılış saatleri","Gemeente Eindhoven","resmi","Pzt 8.30-19.00, Sal-Cum 8.30-17.00, Cmt 9.00-12.00 (sınırlı ürünler); randevu şart; belge teslimi randevusuz."),
 "gemeente-contact": ("Belediye iletişim kanalları","Gemeente Eindhoven","resmi","Telefon 14 040 (yurt dışı +31 40 2386000), posta adresi Postbus 90150, 5600 RB; chat ve form seçenekleri."),
 "gemeente-geboorte": ("Doğum bildirimi","Gemeente Eindhoven","resmi","Doğum 3 gün içinde doğumun olduğu belediyede bildirilir; DigiD ile dijital mümkün; BSN birkaç gün içinde postayla gelir; bildirim ücretsiz."),
 "gemeente-erkenning": ("Çocuğun tanınması (erkenning) ve evlat edinme","Gemeente Eindhoven","aile","Evlilik dışı doğan çocukta babanın/mee-moeder'ın tanıma işlemi."),
 "gemeente-nederlander-worden": ("Hollanda vatandaşlığına geçiş","Gemeente Eindhoven","oturum","Naturalisatie ve optie prosedürlerinin belediye sayfası."),
 "gemeente-paspoort": ("Pasaport ve kimlik kartı başvurusu","Gemeente Eindhoven","resmi","Seyahat belgeleri belediyeden randevuyla alınır."),
 "gemeente-rijbewijs-omwisselen": ("Yabancı ehliyetin Hollanda ehliyetiyle değişimi","Gemeente Eindhoven","ulasim","Hangi ülke ehliyetlerinin değişebileceği ve 30% rejimi istisnaları belediye prosedüründe."),
 "gemeente-parkeervergunning": ("Park izinleri ve 2026 tarifeleri","Gemeente Eindhoven","ulasim","1. bewonersvergunning: schilwijk €4,72/ay, centrum €11,79/ay; 2. araç daha pahalı; E9 bölgesi ayrı rejim; başvuru e-loket."),
 "gemeente-afval": ("Atık toplama bilgisi","Gemeente Eindhoven","gunluk","Atık ve eski kağıt toplamayı Cure Afvalbeheer yürütüyor; milieustraat bilgisi cure-afvalbeheer.nl'de."),
 "cure-afval": ("Cure Afvalbeheer toplama takvimi ve milieustraat","Cure Afvalbeheer","gunluk","Eindhoven ve çevresinin atık kurumu; toplama günleri, konteynerler, milieustraat adres ve ücretleri."),
 "gemeente-overlast": ("Rahatsızlık/hasar bildirimi","Gemeente Eindhoven","gunluk","Kamu alanında rahatsızlık, zarar ve kirlilik bildirim kanalı."),
 "gemeente-belastingen-inwoners": ("Belediye vergileri (inwoners)","Gemeente Eindhoven","para","OZB, afvalstoffenheffing, rioolheffing, hondenbelasting ve ödeme/kwijtschelding bilgileri."),
 "gemeente-hondenbelasting": ("Köpek vergisi kaydı","Gemeente Eindhoven","para","Köpek sahipleri belediyeye köpeği bildirmek ve vergi ödemek zorunda."),
 "gemeente-belastingen-en": ("Municipal taxes (İngilizce özet)","Gemeente Eindhoven","para","Belediye vergilerinin İngilizce açıklaması: OZB, atık, köpek vergisi, ödeme ve indirim."),
 "belastingdienst-aangifte": ("Gelir vergisi beyanı (aangifte)","Belastingdienst","para","Beyan dönemi 1 Mart'tan itibaren; mektup gelmediyse ve ödeme çıkacaksa 14 Temmuz'a kadar beyan zorunlu; 5 yıl geriye dönük beyan mümkün."),
 "belastingdienst-tarieven": ("2026 gelir vergisi dilimleri","Belastingdienst","para","Box 1 tarifeleri: 2026'da ilk dilim %35,75; AOW yaşında farklı; box 3 %36."),
 "belastingdienst-expatregeling": ("Expatregeling (30%-regeling) koşulları","Belastingdienst","para","2026 gelir normu: €48.013 (30 yaş üstü master için €36.497); 150 km kuralı; işverenle ortak başvuru; karar 8 hafta."),
 "toeslagen": ("Toeslagen genel bakış","Dienst Toeslagen","para","Zorgtoeslag, huurtoeslag, kinderopvangtoeslag, kindgebonden budget; proefberekening ve Mijn Toeslagen."),
 "toeslagen-huurtoeslag": ("Huurtoeslag (kira desteği)","Dienst Toeslagen","para","Koşullar, rekenhuur sınırları, başvuru ve 31 Aralık son başvuru kuralı."),
 "toeslagen-zorgtoeslag": ("Zorgtoeslag (sağlık sigortası desteği)","Dienst Toeslagen","para","Gelire bağlı sağlık primi desteği; başvuru DigiD ile."),
 "toeslagen-kinderopvang": ("Kinderopvangtoeslag (kreş desteği)","Dienst Toeslagen","para","Çalışan/eğitim gören ebeveynler için kreş masrafı desteği."),
 "rijksoverheid-kinderbijslag": ("Kinderbijslag (çocuk parası)","Rijksoverheid","para","SVB tarafından ödenen çocuk desteği; kayıt BRP üzerinden otomatik işler."),
 "rijksoverheid-minimumloon": ("Asgari ücret","Rijksoverheid","is","Yasal asgari saat ücreti ve yaş basamakları."),
 "uwv-ww-aanvragen": ("WW işsizlik ödeneği başvurusu","UWV","is","İlk işsizlik gününden 1 hafta önce ila 1 hafta sonra Mijn UWV üzerinden başvuru; karar 4 hafta; DigiD, son loonstrook ve sözleşme gerekir."),
 "gemeente-bijstand2": ("Bijstandsuitkering (sosyal yardım)","Gemeente Eindhoven","para","Geliri olmayanlara Participatiewet kapsamında destek; başvuru kanalı ve şartlar."),
 "gemeente-inkomensondersteuning": ("Düşük gelirliler için destekler","Gemeente Eindhoven","para","Meedoenbijdrage ve Individuele Inkomenstoeslag genel çerçevesi."),
 "gemeente-meedoenbijdrage": ("Meedoenbijdrage başvurusu","Gemeente Eindhoven","para","1 Şubat-31 Aralık arasında online başvuru; 120% (2025-26'da 130%) sociaal minimum'a kadar; ücretsiz otobüs, indirimli kütüphane, 6+ çocuklara ücretsiz yüzme diploması A."),
 "rijksoverheid-zorgverzekering": ("Sağlık sigortası sistemi","Rijksoverheid","saglik","Basisverzekering zorunluluğu, sigortalı olma süreleri, çok dilli bilgilendirme."),
 "rijksoverheid-eigen-risico": ("Eigen risico 2026: €385","Rijksoverheid","saglik","Zorunlu eigen risico 2026'da €385; huisarts muayenesi eigen risico dışında; 18 yaş altı için yok."),
 "rijksoverheid-basispakket-2026": ("2026 temel paket değişiklikleri","Rijksoverheid","saglik","Sigara bırakma desteği 3 kez; axSpA egzersiz terapisi pakette; meekijkconsult eigen risico dışında."),
 "zorgverzekeringslijn": ("Sağlık sigortası bağımsız bilgi hattı (SKGZ)","SKGZ / Zorgverzekeringslijn","saglik","Sigorta seçimi ve itirazlarda bağımsız destek."),
 "huisartsenpost-eindhoven": ("Huisartsenpost Eindhoven (nöbetçi aile hekimi)","Huisartsenposten Oost-Brabant","saglik","Akşam/gece/hafta sonu acil olmayan ama bekleyemeyen durumlar için 088 876 5151; adres Michelangelolaan 2 (Catharina Ziekenhuis yanı); randevusuz gidilmez; hayati tehlikede 112."),
 "ggd-youth-en": ("GGD Brabant-Zuidoost çocuk sağlığı (JGZ)","GGD Brabant-Zuidoost","saglik","0-18 yaş gelişim takibi, aşı programı, danışma; başka ülkeden gelenler form doldurarak kayıt olur; ücretsiz."),
 "wijeindhoven": ("WIJeindhoven: Wmo ve gençlik destek kapısı","WIJeindhoven","saglik","Belediye adına tüm bakım/destek taleplerinin ilk kapısı; hulpmiddelen, evde yardım, jeugdzorg."),
 "gemeente-zorg-geregeld": ("Bakım sistemi nasıl işliyor?","Gemeente Eindhoven","saglik","Wmo/Jeugdwet kapsamı, ZIN-PGB farkı, 2026 Wmo eigen bijdrage €21,80/ay."),
 "gemeente-huishoudelijke-hulp": ("Evde temizlik desteği (Wmo)","Gemeente Eindhoven","saglik","Başvuru WIJeindhoven üzerinden; aylık €21,80 eigen bijdrage; düşük gelirde Gemeentepolis ile kısmi geri ödeme."),
 "catharina": ("Catharina Ziekenhuis","Catharina Ziekenhuis","saglik","Eindhoven'ın genel hastanelerinden; acil servis (SEH) Michelangelolaan tarafında."),
 "mmc": ("Máxima Medisch Centrum","Máxima MC","saglik","Bölgenin ikinci büyük hastanesi (Veldhoven lokasyonu ana merkez)."),
 "rijksoverheid-112": ("112 acil numarası","Rijksoverheid","gunluk","Hayati tehlike, yangın, kaza ve suç durumunda 112; hayati olmayan polis için 0900-8844."),
 "politie-contact": ("Polis iletişim numaraları","Politie","gunluk","Acil olmayan ihbar ve bilgi için 0900-8844; suç duyurusu ve randevu."),
 "ns-en": ("NS tren yolculuğu ve biletler","NS","ulasim","Tren biletleri, NS Flex, tek yön bilet ve ek ücretler."),
 "ns-tickets-en": ("NS tek yön bilet ve supplement","NS","ulasim","Tek yön bilet fiyat mantığı, kağıt bilet farkı, yoğunluk supplementi."),
 "ns-abonnementen": ("NS abonmanları (NS Flex)","NS","ulasim","Dal Voordeel vb. indirim abonmanları."),
 "ovchipkaart": ("OV-chipkaart","OV-chipkaart","ulasim","Toplu taşımada ulusal kart sistemi; kişisel ve anonim kart."),
 "ovpay": ("OVpay banka kartıyla check-in","OVpay","ulasim","Otobüs/trende banka kartıyla temassız ödeme; OV-chipkaart yerini alan OV-pas geçişi."),
 "hermes": ("Hermes (Bravo) otobüs işletmesi","Hermes / Transdev","ulasim","Zuidoost-Brabant otobüsleri Bravo markasıyla Hermes tarafından işletiliyor; Airport Shuttle ve P+R Eindhoven dahil."),
 "bravo-home": ("Bravo toplu taşıma bilgisi","Bravo (Provincie Noord-Brabant)","ulasim","Brabant otobüs markası; bilet, tarife ve hat bilgileri."),
 "9292": ("9292 seyahat planlayıcı","9292","ulasim","Tüm toplu taşıma için ulusal rota planlayıcı."),
 "eindhoven-airport": ("Eindhoven Havalimanı","Eindhoven Airport","ulasim","Şehrin kendi havalimanı; terminale otobüs bağlantısı ve otopark bilgileri."),
 "eindhoven-airport-parking": ("Eindhoven Havalimanı otoparkları","Eindhoven Airport","ulasim","Kiss & ride, kısa/uzun süreli otopark seçenekleri."),
 "gemeente-fietsen": ("Eindhoven'da bisiklet","Gemeente Eindhoven","ulasim","Bisiklet yolları, park yerleri, kurallar ve şehir bisiklet politikası."),
 "enexis-vestigingen": ("Enexis hizmet bölgesi (Eindhoven dahil)","Enexis Netbeheer","fatura","Eindhoven, Enexis Brabant Zuid-Oost bölgesinde; elektrik/gaz şebeke operatörü."),
 "brabantwater": ("Brabant Water içme suyu","Brabant Water","fatura","Noord-Brabant içme suyu şirketi; abonelik ve fatura."),
 "duo-studiefinanciering": ("Studiefinanciering (öğrenci finansmanı)","DUO","aile","Yükseköğrenim öğrencileri için devlet desteği: temel burs, ek burs, seyahat ürünü, kredi."),
 "ise": ("International School Eindhoven","ISE","aile","Oirschotsedijk 14b kampüsü; IB programlı, 60+ milletten öğrenci; ilkokul (uluslararası ve iki dilli) ve ortaokul."),
 "tue": ("Eindhoven University of Technology","TU/e","aile","Şehrin teknik üniversitesi; programlar ve kampüs."),
 "designacademy": ("Design Academy Eindhoven","Design Academy","aile","Dünyaca ünlü tasarım okulu; Witte Dame binasında."),
 "konsolosluk-rotterdam": ("T.C. Rotterdam Başkonsolosluğu","T.C. Dışişleri Bakanlığı","gunluk","Görev bölgesi Zuid-Holland, Zeeland ve Noord-Brabant (Eindhoven dahil); işlemler konsolosluk.gov.tr randevusuyla; acil nöbet hattı +31 6 41024588."),
 "weeronline-eindhoven-city": ("Eindhoven hava durumu tahmini","Weeronline","planlama","Şehre özel güncel ve 14 günlük tahmin sayfası."),
 "knmi-verwachtingen": ("KNMI hava beklentileri","KNMI","planlama","Resmî meteoroloji kurumu uyarı ve beklenti sayfası."),
 "wiki-eindhoven-nl": ("Eindhoven şehir profili","Wikipedia (NL)","planlama","Şehrin tarihçe, nüfus, ekonomi ve Philips/Brainport bağlamı; ansiklopedik doğrulama kaynağı."),
 "wiki-wijken": ("Eindhoven mahalle ve semt listesi","Wikipedia (NL)","planlama","7 stadsdeel, 19 wijk, 109 buurt resmi bölünümü; CBS kodları."),
 "wiki-rijksmonumenten-eindhoven": ("Eindhoven ulusal anıt listesi (rijksmonumenten)","Wikipedia (NL)","kesif","151 kayıtlı anıt: adres, koordinat, yapım yılı ve Commons kategorileri."),
 "vanabbemuseum": ("Van Abbemuseum resmî site","Van Abbemuseum","kesif","Modern ve çağdaş sanat müzesi; koleksiyon, sergiler, ziyaret bilgisi."),
 "philipsmuseum": ("Philips Museum resmî site","Philips Museum","kesif","Gerard Philips'in 1891 ilk fabrikasında şirket tarihi müzesi; Emmasingel 31."),
 "dafmuseum-info": ("DAF Museum ziyaret bilgisi","DAF Museum","kesif","Tongelresestraat 27; Sal-Paz 10.00-17.00; kamyon-otomobil koleksiyonu."),
 "nextnature": ("Next Nature Museum (Evoluon)","Next Nature","kesif","Evoluon binasında teknoloji-kültür müzesi ve etkinlik mekânı."),
 "evoluon-http": ("Evoluon binası","Next Nature / Evoluon","kesif","1966'da Philips'in şehre hediyesi olarak açılan ikonik UFO biçimli bina."),
 "muziekgebouw": ("Muziekgebouw Eindhoven","Muziekgebouw Eindhoven","kesif","Klasik-pop-caz konser salonu; yılda ~240 bin ziyaretçi."),
 "parktheater": ("Parktheater Eindhoven","Parktheater","kesif","Şehrin ana tiyatro ve gösteri sahnesi."),
 "effenaar": ("Poppodium Effenaar","Effenaar","kesif","Şehrin önde gelen pop/rock konser mekânı."),
 "natlab": ("NatLab","NatLab","kesif","Strijp-S'te sinema, tiyatro, kafe ve restoran."),
 "mu-arthouse": ("MU Hybrid Art House","MU","kesif","Güncel sanat sergi alanı."),
 "tonsmitshuis": ("Ton Smits Huis","Ton Smits Huis","kesif","Karikatürist Ton Smits'in evinden dönüştürülmüş küçük müze."),
 "strijp-s": ("Strijp-S","Strijp-S / gemeente","kesif","Eski Philips fabrika sahasından yaratıcı mahalleye dönüşen bölge."),
 "hightechcampus": ("High Tech Campus Eindhoven","High Tech Campus","kesif","Açık inovasyon kampüsü; The Strip ortak tesisi."),
 "bibliotheek-eindhoven": ("Bibliotheek Regio Eindhoven","Bibliotheek Eindhoven","gunluk","Witte Dame'daki merkez kütüphane; üyelik, Taalhuis, IDO dijital devlet yardım noktası."),
 "psv": ("PSV resmî site","PSV","kesif","Kulüp, Philips Stadion ve bilet bilgileri."),
 "kazerne-org": ("Kazerne - home of design ziyaret bilgisi","Kazerne Foundation","kesif","Paradijslaan 2-8 / Grote Berg 9; tasarım sergileri (Design Lab), restoran, bar ve otel bir arada; giriş ücretsiz, her gün 7.30'dan itibaren açık."),
 "huisartsenpost-zo-werkt": ("Huisartsenpost çalışma düzeni","Huisartsenposten Oost-Brabant","saglik","Akşam 17.00-sabah 08.00 ve hafta sonu 24 saat; önce telefon triajı."),
}

def build_sources():
    rows = []
    cache_meta = {}
    for f in glob.glob(os.path.join("cache", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        cache_meta[os.path.basename(f)[:-5]] = d
    order = 0
    for cid, (title, pub, topic, note) in SRC.items():
        m = cache_meta.get(cid)
        if not m or m.get("status") != 200:
            print("WARN cache missing/failed:", cid)
            continue
        rows.append({
            "source_id": f"eindhoven:kaynak:{cid}",
            "city_id": CITY,
            "title": title,
            "publisher": pub,
            "url": m.get("final_url") or m["url"],
            "checked_on": "2026-10-20",
            "topic": topic,
            "summary": note,
            "verified": "Evet",
            "order": order,
        })
        order += 1
    json.dump(rows, open("data_sources.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("sources:", len(rows))

def build_topics():
    rows = []
    for slug, title, desc, icon, o in TOPICS:
        rows.append({"topic_id": f"eindhoven:{slug}", "city_id": CITY, "slug": slug,
                     "title": title, "description": desc, "icon": icon, "order": o})
    json.dump(rows, open("data_topics.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("topics:", len(rows))

if __name__ == "__main__":
    build_topics()
    build_sources()
