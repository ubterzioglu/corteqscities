# İspanya ulusal paketi v1 — açık konular (2026-10-24)

Kapsam: 27 kart (oturum 14, resmi 13). Üç bağımsız denetim turundan sonra: 0 ciddi, 2 orta (kapatıldı), 22 küçük bulgu açık.
Kural: şehir yazarı bu boşlukları kendi bilgisinden doldurmaz; kaynaklı ek kart ya da bölge/şehir katmanı yazar.

## Pakette olmayan kart
- NIE/TIE randevusu: ulusal resmî sayfalar bot engeli veriyor, usul ofise göre değişiyor → şehir katmanı.

## Kaynak bulunamadığı için kartlarda olmayan bilgi
- Apostil ücreti; Türkiye'deki apostil makamının adı (kart yalnız İspanya'da düzenlenen belgeleri kapsar).
- Noter ücretine KDV ve diğer masraflar; noter ölçeğinde matriz yaprağı ek ücreti.
- Vatandaşlık başvuru harcı; vatandaşlığın Türk vatandaşlığına etkisi; önceden DELE A2 almış olanın muafiyeti (RD 1004/2015 md. 6.5).
- Oturum yenilemede yenileme şartları ve 183 gün kuralı.
- Cl@ve için yabancıdan istenen belgeler.
- Arraigo harcı (38,28), NLV harcı (10,94), vize ücretleri (kaynak 2 kaynak sınırına takıldı; ikisi de Orden PJC/617/2025'te).
- IPREM 2026 (600 euro) resmî sayfada yalnız Yeni Delhi konsolosluk sayfasında; kartlarda euro tutarı olarak kullanılmadı.
- Ehliyet harç tutarı: DGT sayfasında yer tutucu (XX,XX).

## Canlı doğrulanamayan noktalar (denetçiler)
- İstanbul Başkonsolosluğu sayfası 503 verdi; "Nuevas Tasas Consulares 2026" ve "Auto de 12 de octubre de 2026" duyuruları okunmadı. Dijital göçebe, NLV ve apostil kartları anlık görüntüye dayanıyor.
- Yargıtay 2026 kararlarının tüm iptal listesi okunmadı.
- Código Civil md. 22'nin 2026'da değişip değişmediği canlı doğrulanmadı (anlık görüntüde son güncelleme 2021).
- claims, Bağlantılar ve valid_until dosyaları satır satır insan ya da model gözüyle denetlenmedi; yalnız script denetiminden geçti (alıntı kaynak metninde, kimlikler tutarlı).

## Bilinen küçük kusurlar
- dijital-gocebe: 34.188 euro kartın kendi türetmesi (yıllık SMI × yüzde 200), `steps`'te çekincesiz.
- kar-amaci-gutmeyen: karar süresi cümlesi çıkarıldı; Delhi sayfası 3 ay, RD md. 63.4 bir ay + sessizlik = ret diyor, kart bu çelişkiyi söylemiyor. `cost` boş.
- arraigo: EX10 / 790-012 kaynağı zayıf; "yalnız şahsen" cümlesi md. 197 ile tam örtüşmüyor; ikinci fırsatta yenilememe nedeni ve sosyal-eğitimde 30 saat sınırı eksik.
- brexit: Türk aile üyesi için form (EX21) ve belge yenileme anlatılmıyor.
- belge-ceviri: "Adalet Bakanlığı adli ve idari belgelerin tek mercii" kaynakta açık değil (yalnız noter için "únicamente").
- noter: "folio" sayfa diye çevrilmiş; "ek olarak uygulanır" cümlesi yüzde 5 dışındaki indirimleri de kapsıyor gibi okunur.

## Güncellik
- valid_until yazılan kartlar: dijital-gocebe-vizesi ve kar-amaci-gutmeyen-oturum-vizesi (2026-12-31). Diğer harç kartlarında kaynak yıl etiketi yok (polis harç sayfası 24.10.2026'da güncel, Orden PJC/617/2025 ile aynı); Ocak'ta yeniden bakılmalı.

---
# Grup 1 eki (paket v2: 59 kart, para + iş + fatura eklendi) — 2026-10-24

Süreç: kaynak keşfi → yazar → bağımsız denetim → düzeltme editörü. Editör sonrası ikinci bir bağımsız denetim YAPILMADI (v1'de yapılmıştı, 0 ciddi çıkmıştı). Editörün yeniden yazdığı cümleler yalnız script denetiminden geçti (alıntı kaynak metninde var).

## Kartlara yazılmayan bilgiler (resmî kaynak bulunamadı ya da 2 kaynak sınırı)
- para: bankadan NIE/pasaport şartı; "gestor ne zaman gerekir" yargısı; Türkiye-İspanya sosyal güvenlik düzeni; Baskiya/Navarra foral IRPF ve mukim olmayan (IRNR) rejimi; Beckham başvuru yolu ve süresi; Türkiye havalesinin SEPA dışı sayıldığı; işsizlik/FOGASA/meslek eğitimi prim oranları; Renta 2026 kampanya tarihleri; IVA geçici elektrik/gaz oranı.
- is: SMI için "14 ödeme" ve 14×1.221 hesabı (RD metninde yok); otonom aylık euro cuota ve alta süresi; paro 2026 üst/alt tutar sınırları; finiquito içeriği; meslek bazlı tanıma; yabancı için otonom çalışma izni şartı; 2027 tatil listesi (BOE-A-2026-21254, kart 2 kaynak sınırında).
- fatura: güncel IVA, güç değişikliği ücreti, TUR tutarları, taahhüt cezası hesabı ve numara taşıma; 2.0TD tanımı (kart kaynaklarında yok); borç nedeniyle elektrik kesintisi; gaz şikâyet yolu; Katalonya için yedek fon dışındaki apartman kuralları (çağrı süresi, devir sorumluluğu).

## Doğrulanmayan ya da dikkat isteyen noktalar
- Renta kartı: 2025 gelirinin kampanyası kapandı; kart geçmiş kampanyayı tarihli anlatıyor, sonraki kampanya tarihi yayımlanınca güncellenmeli.
- IBAN kartı: alıcı adı kontrolü "9 Ekim 2025'ten beri" — resmî sayfa yılı yazmıyor (yıl sayfa tarihinden çıkarım).
- Bizum kartı: kaynak 20.07.2021 tarihli; güncel resmî sayfa yok, cümleler tarihli yazıldı.
- İş kazası kartı: LGSS 169-172 maddeleri 1 Aralık 2026'da değişiyor (RDL 31/2026); kart bu maddelere dayanmıyor.
- Fatura kart 9 (apartman): Katalonya dışı genel kural (Ley 49/1960) olarak çerçevelendi; Katalonya için yalnız yedek fon (BOE Ley 5/2006 md. 553-6). Navarra/Bask özel rejimleri araştırılmadı.
- mites.gob.es sertifika hatası verdi; hiçbir iş kartı o siteye dayanmıyor.

## Güncellik (2027'ye girerken)
- valid_until 2026-12-31 olan 7 kart 1 Ocak 2027'de yeniden doğrulanmalı: dijital göçebe, NLV, SMI 2026, yıllık izin ve tatiller 2026, bordro, otonom prim tablosu, bono social. country_apply bunları bayat sayıp yeniden denetime alıyor (denendi).

## v3 notu (editör sonrası dar denetim + son düzeltme turu)
- Editör sonrası bağımsız denetim yapıldı (para 0 ciddi/1 orta, iş 0/0, fatura 0/4); orta bulgular ve seçili küçükler son turda kapatıldı. Kalan küçük bulgular raporlarda: yazar\out\denetim_g1b_*.md.
- Bono social kartı: kWh sınırları BOE Anexo I'e göre hane bileşimiyle yazıldı; kaynak sınırı yüzünden şikâyet adımı karttan çıktı (şikâyet kart "elektrik-ve-telekom-sikayet-yollari" kartında).
- Elektrik aboneliği kartı: MITECO "her an cezasız çıkar" cümlesi çıkarıldı (CNMC'nin şartlı cezası ile uzlaştırılamadı).
- Bizum kartı: güncel resmî sayfa yok; cümleler 2021 tarihli kaynağa bağlı.
- Doğrulama ölçüsü: v3'te editör sonrası ikinci denetimden sonra yapılan son düzeltmeler yalnız script denetiminden geçti.

---
# Grup 2 eki (paket v4: 80 kart, saglik + ev + planlama eklendi) — 2026-10-24

Süreç: kaynak keşfi → yazar → bağımsız denetim → düzeltme editörü. Editör sonrası ikinci bir bağımsız denetim YAPILMADI; düzeltmeler yalnız script denetiminden geçti (alıntı kaynak metninde var).

## Kartlarda olmayan, önemli boşluklar
- **Türk okuyucuya AB rejimi uyarısı yok (sağlık):** "AB serbest dolaşım rejimi Türk vatandaşına uygulanmaz; AB vatandaşının Türk aile üyesi için ayrı kural var" cümlesi kaynaksız bulundu ve kartlardan çıkarıldı. Kaynak (RD 240/2007 art. 2, es:kaynak:005) kart başına 2 kaynak sınırına sığmadı. Çözüm: bu uyarı için ayrı bir "AB vatandaşı olmayanlar için sağlık erişimi" kartı ya da şehir fazında not.
- **Yolcu bagajı gümrük muafiyeti kartı yok:** gümrük kartı (planlama kart 4) kaynak sınırı yüzünden yalnız ev eşyası ve nakit beyanını anlatıyor. Yolcu sayfasındaki 430/300/150 € muafiyeti ve tütün/alkol kotaları ayrı bir kart olabilir (kaynak es:kaynak:101; sayfanın "10.000 €'dan fazla" ifadesi AEAT nakit beyan sayfasıyla ("ve üzeri") çelişiyor, 101 kullanılırken dikkat).
- **Katalonya, Andalucía vb. bölge bilgisi ulusal karta girmedi:** fianza'nın yatırıldığı kurum (Katalonya'da INCASÒL; MIVAU sayfası 403 verdi), gergin bölge ilanları (belediye bazlı), özerk bölgenin sağlık kartı ve aşı takvimi uygulaması → bölge ve şehir fazı.

## Kira mevzuatı (ev) — acil güncelleme gerekir
- RDL 29/2026 (7 Ekim) Meclis onayı ~6 Kasım'da doluyor; RDL 28/2026 15 Kasım'da md. 10'u değiştiriyor. Altı ev kartının valid_until değeri 2026-11-05; country_apply 6 Kasım'da bunları yeniden denetime alıyor (denendi). Yeniden yazılacak: kira sözleşmesi ve uzama, depozito/fianza, kira artışı (IRAV), onarım, evden çıkış, dolandırıcılık.
- Evden çıkış kartı: md. 11.1 çekirdeği (6 ay, 30 gün); geçici konut md. 11.2 RDL 29/2026'ya dayanıyor ve kartta bu şekilde işaretli.

## Doğrulanamayan ya da dikkat isteyen noktalar
- İstanbul Başkonsolosluğu sayfaları (planlama kart 1, 2, 6) aralıklı 503/504 verdi, tarihsiz; kartlar "İstanbul konsolosluk bölgesinde oturanlar için" diye sınırlı.
- Evcil hayvan kartı: MAPA sayfası sertifika hatası verdi (açılmadı); AEAT sayfasına dayanıyor, yönetmelik numarası yazılmadı; Türkiye'nin 577/2013 Ek II listesinde olup olmadığı doğrulanmadı.
- IPREM euro tutarı resmî sayfada doğrulanamadı; kartlarda yalnız yüzde olarak yazıldı.
- Saat kartı: yaz saati bu yıl 25 Ekim 2026'da bitiyor; kart tarih değil kuralı (Mart/Ekim son pazarı) yazıyor.
- Sağlık kart 7 (bağımlılık): Ley 39/2006 art. 5, Ley 4/2026 ile 23/10/2026'da değişti; kart bu tarihe göre yazıldı.


## G2b denetiminden kalanlar (2026-10-24)
- saglik / kamu-saglik-sistemine-erisim-hak-sahipleri: convenio especial için 1 yıl kesintisiz ikamet ve padrón koşulu kartın kaynaklarında (091, 092) yok, yalnız 093'te (kart 2); kart başına 2 kaynak sınırı nedeniyle bu karta eklenmedi.
- saglik / saglik-sigortasi-sarti-ve-convenio-especial: RD 557/2011 ile RD 1155/2024'ün hangisinin hangi konuda geçerli olduğu kaynaklarda yok; Türkiye-İspanya sosyal güvenlik sözleşmesinin sağlığı kapsayıp kapsamadığı kaynakta yok.
- saglik / recete-ilac-katilim-payi-copago: "asegurado activo" tanımı (öğrenci, işsiz gibi grupların satırı) ve ATC azaltılmış grup 4,98 € tavanının ölçü birimi kaynakta yok. (Denetimin "adım 3 kaynaksız" bulgusu yersizdi: cümle art. 101.3'te var, kaynağa göre netleştirildi.)
- saglik / acil-durumda-112: kaynak RD 903/1997 özgün metni; güncel mevzuat karşılaştırması kaynakta yok.
- saglik / ulusal-asi-takvimi: hangi aşı, hangi yaş, ücret bilgisi kaynak sayfada yok (takvim PDF'i kaynak değil).
- saglik / hamilelik-dogum-ve-cocuk-sagligi-haklari: hamilelik hizmetleri için ikamet/çalışma izni koşulu kaynakta yok; doğum tarihi yerine evlat edinme/koruma kararı tarihinin de yaş ölçütü olduğu denetimde söylendi, kartta düzeltilmedi.
- saglik / ruh-sagligi-ve-yasli-bakimi-dependencia: Türk vatandaşının LO 4/2000, antlaşma ve menşe ülke sözleşmeleri uyarınca fiilen hak sahibi olup olmadığı kaynakta yok (kart yalnız havaleyi yazar).
- ev / kira-sozlesmesi-suresi-ve-uzama: md. 9 bis.2 (12 ayı gerekçesiz aşan geçici sözleşmenin ana konut sayılması) kartta yok; kaynak metninin tam koşulu okunmadan yazılmadı.
- ev / kira-depozitosu-fianza-ve-iade: Katalonya/Bask gibi bölgelerde fianza depozito yükümlülüğü kaynakta yok; RDL 29/2026'nın Meclis onayı kaynakta yok.
- ev / kira-artisi-siniri-irav: gergin bölge ilanının belediye/bölge bazlı olduğu kaynakta yok; INE tablosunda 2,54'ün sütunu (yıllık değişim mi) metinden kesin değil; md. 18.1'in RDL 29/2026 öncesi metni kaynakta yok (neyin yeni olduğu yazılamadı).
- ev / kirada-onarim-ve-hasar-sorumlulugu: md. 21.5 (15 günlük usul) kartta yok; RDL 29/2026'nın Meclis onayı kaynakta yok.
- ev / kiralik-evden-cikis-ve-ihbar-suresi: RDL 28/2026 ve 29/2026 için Meclis onay/oylama sonucu kaynakta yok; 15 Kasım 2026 sonrası tazminat tutarı hesabı ve a-e istisnalarının ayrıntısı karta yazılmadı; md. 11'in 15 Kasım'dan sonra değişip değişmediği kaynakta belirtilmiyor.
- planlama / oturum-vizesi-basvurusunda-getirilecek-belgeler: IPREM'in euro tutarı ve birimi kaynakta (es:kaynak:040) yok; yazılmadı.
- planlama / ilk-gunlerde-nuss-ve-temel-odeme-hesabi: slug "ilk-gunlerde-..." kaldı (slug değişirse paket kimliği kayar); kaynak NUSS için süre sınırı koymaz. "Türk vatandaşı olarak NIE" ifadesi kaynaktaki "DNI o NIE" sayımının yorumudur; kaynak DNI/NIE farkını açıklamaz.
- planlama / ab-disindan-gelirken-esya-ve-nakit-gumruk-beyani: yolcu bagajı muafiyet kuralları (kaynak 101) kart başına 2 kaynak sınırı nedeniyle karta girmedi; ayrı kart önerilir. Ceuta/Melilla/Kanarya nakit rejimi kaynakta yok.
- planlama / ab-disindan-evcil-hayvanla-ispanyaya-giris: "2026/636" sayılı daha yeni düzenleme ve Ek II'nin güncelliği kaynak 105'te yok (yazılmadı); 0,5 UI/ml, 3 ay, 7 ay kuralı kaynakta yalnız İspanya'ya dönüş bölümünde var, AB dışından ilk giriş için ayrıca doğrulayan kaynak yok.
- planlama / ispanya-para-birimi-euro-ve-resmi-dil: euro banknotlar ve "İspanya'nın para birimi euro" cümlesi kaynaklarda doğrudan yok.
- planlama / ispanya-resmi-saat-ve-yaz-saati-kurali: Ceuta/Melilla saati ve 2026 yaz saati bitiş tarihi (25 Ekim 2026) kaynakta yok.

## G2c canlı kontrolden kalanlar (2026-10-24)
Rapor: `_is/yazar/out/denetim_g2c_canli.md`.
- planlama / ab-disindan-evcil-hayvanla-ispanyaya-giris: kart 2026/131 (es:kaynak:111) ile düzeltildi. Türkiye'nin 2026/636 Ek I ve Ek II listelerinde OLMADIĞI denetçi tarafından okundu, ama "listede yok" birebir alıntılanamadığı için kartta koşullu yazıldı. AEAT sayfası (23.9.2026) hâlâ 577/2013'e atıf yapıyor. 0,5 UI/ml ve 3 ay koşulu 2020/692 Ek XXI'de; kartta yalnız AEAT'in "dönüş" bölümünden. mapa.gob.es açılmadı.
- planlama / ilk-gunlerde-nuss-ve-temel-odeme-hesabi: "Türk vatandaşı olarak NIE" eki geri alındı (kaynak 107'de yok; kart 2 kaynak sınırında). Destekleyen resmî kaynaklar bulundu: LO 4/2015 md. 8 (BOE-A-2015-3442), RD 1553/2005 (BOE-A-2005-21163), Policía NIE sayfası. Ayrı bir kimlik kartında kullanılabilir.
- saglik / kamu-saglik-sistemine-erisim-hak-sahipleri: convenio especial koşulları (1 yıl ikamet, padrón, başka güvence olmaması; 60 €/157 €) RD 576/2013 md. 3'te bulundu (BOE-A-2013-8190); karta eklenmedi (kaynak sınırı), ayrı kart ya da kaynak değişimi gerekir.
- ev: RDL 28/2026 ve 29/2026 için 24.10.2026'ya kadar BOE'de convalidación/derogación yayımı yok; congreso.es 403. LAU canlı metni 7.10.2026 sürümüyle kartlarla uyuşuyor. 5.11.2026 sonrası yeniden kontrol.
- planlama / oturum-vizesi: IPREM 2026 tutarı için birincil kaynak bulunamadı (son açık belirleme 2023: 600 €/ay).
- Yolcu bagajı muafiyeti için AEAT sayfası canlı doğrulandı (430/300/150 €; tütün/alkol sınırları); ayrı kart önerisi sürüyor.
