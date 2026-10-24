# Bağımsız denetim G3: ES ulusal paketi, konu "ulasim" (6 kart)

Denetim tarihi: 2026-10-24. Yöntem: kartın olgusal cümleleri kartın KENDİ kaynak metniyle (kaynak_dizini text_file) karşılaştırıldı; canlı kontroller curl ile yapıldı (BOE RD 1428/2003 konsolide, RD 518/2026 metni, Ley 17/2012 DA 13ª, RD 920/2017 sayfa tarihi, DGT, AESA, renfe.com x2). Kartlara dokunulmadı.
Derece: ciddi = yanlış/yanıltıcı; orta = eksik/kapsam/eski; küçük = ifade/kural ihlali.

## Canlı kontrol özeti (öncelikli üç soru)
- RD 1428/2003 canlı konsolide metin: "Última actualización 26/06/2026". RD 518/2026 (BOE-A-2026-13889) 1 Ekim 2026'dan itibaren yürürlükte (bugün 24/10/2026). Art. 20 (alkol) DEĞİŞMEDİ (0,5 g/l, 0,25 mg/l; 0,3/0,15 grupları aynı). Art. 50 (şehir içi) DEĞİŞMEDİ (son redaksiyon 11/05/2021: 20/30/50, travesía 50, otoyol içi 80). Art. 48 yalnız 1. fıkra b bendi değişti. Art. 48.1.a tablosu (120/90, 90/80, 100/90) kartla birebir. Yani kart yürürlükteki metni veriyor ama art. 48.1.b'yi anlatmıyor (bkz. 3.1).
- Yerleşik indirimi Türk vatandaşı: kart Canarias için Ley 19/1994 art. 6'yı doğru aktarıyor (redaksiyon 07/11/2018, hâlâ son) ama "yalnız larga duración" diyerek aile üyesi yolunu atlıyor; Baleares/Ceuta/Melilla için belirsiz bırakıyor, oysa canlı Ley 17/2012 DA 13ª.Uno dört bölge için aynı kuralı koyuyor (bkz. 6.1, 6.2).
- Renfe: 2 saat masrafsız iptal, 50 €, %30/%25, %5/%20, Prémium yok AVE Internacional canlı sayfayla UYUŞUYOR. Eksik olan, canlı sayfadaki bilet türü tablosu (Básico/Elige iptal-değişiklik koşulları; bkz. 1.1).

## 1. renfe-bilet-iptal-degisiklik-genc-indirimi (kaynak 127, 129)

**1.1 ORTA, başlıktaki "iptal ve değişiklik nasıl işler" sorusuna somut koşul verilmemiş.**
- Kart yalnız "2 saat içinde masrafsız iptal; daha fazla esneklik için Elige/Prémium" diyor. Kaynak snapshot'ı (127, 2628 karakter) tabloyu içermiyor; canlı sayfa (renfe.com .../todos-los-billetes, sayfaya gömülü ürün verisi) şunu veriyor: Básico "Cambios: Un cambio con un coste de 10 €, más la diferencia de precio"; "Anulación: No incluida"; Elige Estándar "Primer cambio gratuito; se abona la diferencia" ve "Anulación: Devolución del 70 % del importe".
- Sonuç: Básico alan okuyucu 2 saat sonrası iptalin tamamen kapalı olduğunu kartta göremiyor.
- Öneri: kaynak 127'yi tablo içeren güncel snapshot ile yenileyip Básico (1 değişiklik 10 €, iptal yok) ve Elige (ilk değişiklik ücretsiz, iptalde %70 iade) için claim ekle. (Prémium satırını okumadım, bakılamadı.)

**1.2 KÜÇÜK, valid_until "2026-12-31" kaynaksız (Kural 11).**
- Kaynak 127/129'da bitiş tarihi yok ("diciembre de 2026" aranan iki metinde geçmiyor). Öneri: null.

**1.3 KÜÇÜK, steps 4: "14-25 yaşındaysan ... Carné Joven de AVE ve Larga Distancia'da %5, Avant ve Media Distancia'da %20".**
- Kaynak: "El Carné Joven, expedido por tu Comunidad, ... 20% ... Avant, Media Distancia y Regionales de la red de Feve. En trenes Ave y Larga Distancia ... 5%". Yaş aralığı yalnız Más Renfe Joven için yazılı; Carné Joven yaşı kaynakta yok ve Feve Regionales atlanmış. Öneri: cümleyi yaşa bağlama, "Feve Regionales" ekle.

**1.4 KÜÇÜK, summary son cümle "Renfe'nin güncel ürün sayfalarındaki bilgidir."** Meta cümle, bilgi taşımıyor (Kural 3 ruhu). Öneri: sil ya da tarih yaz.

Doğrulananlar: 4 bilet türü, AVE Internacional'de Prémium yok, ekstraların yalnız satın alırken alınması ve Básico'da olmaması, kimlik belgeleri listesi, Más Renfe Joven 50 €/1 yıl/%30-%25, ISIC/EYCA geçerliliği, Carné Joven için "cambios y anulaciones ... sujeto a gastos".

## 2. otobus-yolcu-haklari-rotar-bagaj-engelli (kaynak 136, 137)

**2.1 ORTA, başlıktaki "bagaj zarar görürse" sorusu özette cevapsız; cevap yalnız note'ta ve dar.**
- Özet bagajdan hiç söz etmiyor. Note: "otobüs kazası sonucu bagaj kaybı ya da hasarında tazminat". Kaynak md. 7.1: "pérdida o daño del equipaje, debidos a accidentes resultantes del uso del autobús o autocar". Yani olağan (kaza dışı) bagaj hasarı Tüzük kapsamında değil; kart bunu açıkça söylemiyor, okuyucu "evet hakkım var" sanabilir (Kural 4, 12).
- Öneri: özete "Bagaj için Tüzük yalnız otobüs kazasından doğan kayıp/hasarı kapsar" ekle.

**2.2 ORTA, İspanya'nın ulusal düzenli hatlarda muafiyet kullanıp kullanmadığı belirsiz, özet kesin konuşuyor.**
- Kaynak md. 2.4: "los Estados miembros podrán eximir ... los servicios regulares nacionales ... por un período no superior a cuatro años, que podrá renovarse una sola vez". Kartın note'u bunu genel olarak anıyor; özet "Evet: ... hak tanır" diyor. İspanya'nın muafiyeti kullanıp kullanmadığı iki kaynakta da yok ve ben ayrıca doğrulamadım (bakılamadı). İç hat kullanan okuyucu için kritik.
- Öneri: İspanya'nın durumu kaynaklı doğrulanana kadar özeti "uluslararası ve (muafiyet kapsamında olmayan) ulusal hatlar" diye sınırla ya da gaps.md'ye yaz.

**2.3 KÜÇÜK, steps 4: engelli yardımı "en az 36 saat önce bildir".**
- Kaynak md. 14.1: bildirim 36 saat + yolcunun belirlenen noktada belirlenen saatte hazır bulunması (b bendi). İkinci şart yok. Ayrıca taşıyıcı yanıt vermezse başvurulacak ulusal kurum (md. 27-28) kartta yok. Öneri: "belirlenen noktada zamanında bulun" ekle.

Doğrulananlar: 250 km, 120 dk, 90 dk + 3 saat, %50 ve 1 ay, 14 gün iade, 80 €/2 gece (ulaşım hariç), 1.200 €/parça, 3 ay şikâyet/1 ay/3 ay yanıt, ayrımcılık yasağı, aşırı hava istisnası (137).

## 3. hiz-siniri-alkol-ehliyet-puani (kaynak 131, 132)

**3.1 ORTA, RD 518/2026 ile 1 Ekim 2026'da yürürlüğe giren art. 48.1.b kartta yok; otobüs sınırı koşulsuz.**
- Canlı metin: "En el supuesto de que en un autobús viajen pasajeros de pie porque así esté autorizado o en caso de que el autobús no esté dotado de cinturón de seguridad, la velocidad máxima, cualquiera que sea el tipo de vía fuera de poblado, será de 80 kilómetros por hora." ve okul taşımacılığı/tehlikeli madde için "se reducirá en 10 kilómetros por hora". Kart steps 2: "otobüsler için 100 ve 90". Kart "son güncelleme 26/06/2026" diyor (doğru) ama değişikliğin yürürlük tarihini ve içeriğini vermiyor.
- Öneri: "Ayakta yolcu taşıyan ya da emniyet kemeri olmayan otobüs: her şehir dışı yolda 80; okul servisi ve tehlikeli madde: 10 km/h daha düşük (md. 48.1.b, 01/10/2026'dan beri)" ekle.

**3.2 ORTA, konvansiyonel yol 90 km/h istisnasız yazılmış.**
- Kaynak md. 48.1.a notu: "En carreteras convencionales con separación física de los dos sentidos de circulación, el titular de la vía podrá fijar un límite máximo de 100 km/h para turismos, motocicletas y autocaravanas ...". Altyazı ve özet "konvansiyonel yolda 90" diyor. Öneri: "fiziksel ayrımlı konvansiyonel yolda yol sahibi 100 koyabilir" ekle (bölgesel/yol bazlı değişim, Kural 8).

**3.3 KÜÇÜK, özet: "puan sıfırlanırsa ehliyet geçerliliğini yitirir".**
- DGT (22/09/2026): "se procederá a tramitar la perdida de vigencia"; "La prohibición de conducir se iniciará tras recibir dicha resolución, por lo que hasta entonces podrás conducir." Steps bunu doğru yazıyor, özet kısaltarak yanlışlıyor (Kural 12). Öneri: özete "bildirim gelince" ekle.

Doğrulananlar: art. 20 (0,5/0,25; 0,3/0,15 grupları; 2 yıl yeni sürücü), art. 50 tüm fıkralar, 12/8 puan, +2/+1/en çok 15, yeni sürücü 2 yıl→12, 2/3/4/6 puan, günde 8 puan ve istisnalar, 3-6 ay/12-24 ay/31-90 gün. valid_until null uygun; ancak hız maddesi yakın zamanda değişti, tarih duyarlı: yazar 518/2026'yı izlemeli.

## 4. itv-arac-muayene-periyotlari (kaynak 133)

**4.1 KÜÇÜK, özet "ticari araç ... periyot farklıdır" ama note yalnız N1 veriyor.**
- Kaynak md. 6.1: N2/N3 (>3,5 t) ve O2(karavan dışı)/O3/O4 "Hasta 10 años: Anual; más de 10: Semestral", tarım araçları, özel araçlar, tarihi araçlar (30+ yıl bienal... 60 yıl üstü muaf) kartta yok. Başlık "ITV kaç yılda bir" otomobil odaklı olduğundan kapsam sorunu küçük. Öneri: özetten "ticari araç" ifadesini "hafif ticari (N1)" yap.

Doğrulananlar: M1 4/2/1, ciclomotor 3 yıl, diğer L 4 yıl, M2/M3 5 yıl yıllık sonra 6 aylık, N1 2/6/10, O2 karavan 6 yıl, taksi/ambulans/okul 5 yıl yıllık, sürücü kursu 2/5, 30 gün kuralı, 10 gün + baja, kaza sonrası muayene. Canlı BOE: son güncelleme hâlâ 18/09/2024, kart güncel. valid_until null uygun.

## 5. ucus-gecikme-iptal-aesa-sikayet (kaynak 135, 134)

**5.1 ORTA, tazminat "olağanüstü durum" istisnası atlanmış.**
- Özet/altyazı: "varışta 3 saat ve üzeri gecikmede 250-600 € tazminat hakkın doğar". Kaynak 134: "La aerolínea alega 'circunstancias extraordinarias' ... La compañía aérea debe probarlo para justificar que no abona la compensación que pudiera generarse" (örnek: kontrolör grevi, kötü hava; kendi personel grevi/teknik sorun genelde sayılmaz). Kart bunu hiç anmıyor; tazminat koşulsuz görünüyor. Ayrıca iptal tazminatının 3 saat şartına bağlı olmadığı belirsiz kalıyor.
- Öneri: "Havayolu olağanüstü durumu kanıtlarsa tazminat ödenmeyebilir; bakım/yeniden yönlendirme hakları yine sürer" ekle.

**5.2 KÜÇÜK, AESA kapsamı eksik.** Kaynak 135: yolcular "un aeropuerto situado en un país que no sea miembro de la UE, con destino ... España, cuando participe ... una compañía aérea comunitaria" da kapsıyor; kart yalnız İspanya'dan kalkışı yazıyor (başlık da öyle olduğundan tutarlı). Öneri: başlıkla sınırlı kaldığı kabul edilebilir; isterse ekle.

**5.3 KÜÇÜK, steps 3: "dijital sertifika, Cl@ve ya da yabancılar için e4F".** Kaynak: "El sistema Cl@ve PIN no permite la presentación ... será necesario su posterior impresión y envío por correo"; e4F "previo registro" ve 1 yılda sona erer. Öneri: "Cl@ve Permanente (Cl@ve PIN imza veremez)" yaz.

Doğrulananlar: 5 yıl, 1 ay yanıt, 1 yıl AESA, 02/06/2023 ve sonrası, 90 gün karar, 1 ay uyma, ücretsiz, kapsam dışı konular, mahkeme önce ise inadmisión, 10 gün yarı yüz yüze, PMR 2 ekipman. Canlı AESA sayfası: "Última modificación 18/09/2026", yapı ve gecikme uyarısı aynı.

## 6. ada-ceuta-melilla-yerlesik-ucus-indirimi (kaynak 138, 139)

**6.1 ORTA (ciddiye yakın), Baleares/Ceuta/Melilla için Türk vatandaşı şartı belirsiz bırakılmış; canlı yasa dört bölgeye aynı kuralı koyuyor.**
- Kart note: "RD 949/2018 metni Illes Balears, Ceuta ve Melilla sakinleri için 'ciudadanos residentes' demektedir"; özet ve steps üçüncü ülke şartını yalnız Canarias'a bağlıyor. Canlı Ley 17/2012 DA 13ª.Uno (BOE-A-2012-15651, RD 949/2018'in atıf yaptığı hüküm): "... y los ciudadanos nacionales de terceros países residentes de larga duración, que acrediten su condición de residente en las Comunidades Autónomas de Canarias e Illes Balears y en las Ciudades de Ceuta y Melilla." Yani şart dört bölge için aynı; kimlik kanıtı "tarjeta ... de identidad de extranjero en la que debe constar su condición de residente de larga duración", ikamet kanıtı "certificado de empadronamiento en vigor" (DA 13ª.Cuatro).
- Öneri: kaynak 138 yanına DA 13ª'yı koy (2 kaynak sınırı için 139 yerine ya da 138'i değiştir) ve "Dört bölge için de üçüncü ülke vatandaşı uzun dönem oturumlu olmalı" yaz.

**6.2 CİDDİ, "yalnız residentes de larga duración" yanlış dışlama; AB vatandaşının üçüncü ülke aile üyeleri atlanmış.**
- Kart özeti: "Ley 19/1994 art. 6, üçüncü ülke vatandaşlarından yalnız 'residentes de larga duración' ... olanlara bu indirimi tanır." Kartın kendi kaynağı 139 art. 6.1: "los ciudadanos españoles y de los demás Estados miembros ..., sus familiares nacionales de terceros países beneficiarios del derecho de residencia o del derecho de residencia permanente y los ciudadanos nacionales de terceros países residentes de larga duración, que acrediten su condición de residente en las Islas Canarias". (DA 13ª.Uno canlı metin de aynı.) AB/AEA/İsviçre vatandaşının Türk eşi/çocuğu, uzun dönem oturum olmadan da (aile oturum kartıyla) yararlanır. Steps 3 ve documents de aynı yanlış "yalnız".
- Öneri: "Türk vatandaşı: ya uzun dönem oturum sahibisin ya da AB/AEA/İsviçre vatandaşının aile üyesi olarak oturum hakkın var (Kural 7); geçici/öğrenci/çalışma oturumu bu iki gruba girmiyor" yaz.

**6.3 KÜÇÜK, meta ifadeler (Kural 3).** Özet: "Bu sayımda geçici, öğrenci ya da çalışma oturumu ayrıca anılmaz"; note: "bu iki kaynakta yalnız Canarias için yazılıdır". Okuyucuya bilgi değil kaynak-içi gözlem. Öneri: doğrudan "geçici/öğrenci/çalışma oturumu sahipleri listede yok" yaz.

Doğrulananlar: %75, indefinido, doğrudan yolculuk tanımı (12 saat), Ley 21/2003 art. 68.2 d,e,f kesintisi, Canarias interinsular hava %75. Canlı: Ley 19/1994 art. 6 hâlâ 07/11/2018 redaksiyonu; Ley 17/2012 DA 13ª'de %75 ve 12 saat aynı. valid_until null uygun (süresiz).

## Özet tablo

| kart | ciddi | orta | küçük |
|---|---|---|---|
| renfe-bilet-iptal-degisiklik-genc-indirimi | 0 | 1 | 3 |
| otobus-yolcu-haklari-rotar-bagaj-engelli | 0 | 2 | 1 |
| hiz-siniri-alkol-ehliyet-puani | 0 | 2 | 1 |
| itv-arac-muayene-periyotlari | 0 | 0 | 1 |
| ucus-gecikme-iptal-aesa-sikayet | 0 | 1 | 2 |
| ada-ceuta-melilla-yerlesik-ucus-indirimi | 1 | 1 | 1 |
| TOPLAM | 1 | 7 | 9 |

Bakılamayanlar: İspanya'nın 181/2011 ulusal hat muafiyetini kullanıp kullanmadığı; Renfe Prémium satırı ve tablonun görünür HTML hâli (veri sayfa içi gömülü JSON'dan okundu); Carné Joven yaş/uygunluk koşulu (özerk topluluğa göre); BOE-A-2012-15651 sonrası olası ek değişiklik (sayfa son güncelleme 20/10/2022 gösteriyor).
