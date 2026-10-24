# İspanya ulusal paketi: üçüncü bağımsız denetim (editörün yeniden yazdığı 10 kart)

Tarih: 2026-10-24. Denetçi kartları yazmadı; kartlara ve başka dosyalara dokunulmadı. Ölçü: kartın kendi `source_ids` kaynak metni (kaynak_dizini.jsonl > text_file).

**Özet: 0 ciddi, 2 orta, 22 küçük bulgu. Tamamen temiz: 1 kart (clave-pin-ve-permanente-farki).**
Sayılar, süreler, harçlar, yüzdeler ve hesaplar (28.800 / 7.200 / 34.188 / noter ölçeği / 16,40 + 19,30 + 81,54 / 21,87 / 12,00) kaynakla birebir doğrulandı; kartlarda yanlış sayı ya da yanlış hesap bulunmadı. Kalan bulgular eksik ya da muğlak anlatım, bir çeviri hatası ve kaynak seçimi zayıflığı.

| Kart | Derece |
|---|---|
| arraigo-kok-salma-oturumu | orta |
| kar-amaci-gutmeyen-oturum-vizesi | orta |
| dijital-gocebe-vizesi | küçük |
| noter-islemleri-ve-ucretleri | küçük |
| oturum-izni-yenileme | küçük |
| kalici-oturum-bes-yil | küçük |
| ispanyol-vatandasligi-basvurusu | küçük |
| brexit-sonrasi-ingiliz-oturumu | küçük |
| belge-ceviri-ve-apostil | küçük |
| clave-pin-ve-permanente-farki | temiz |

Havale cümlesi taraması: "resmî sayfada yazar" türü bir havale kalmamış. Tek havale benzeri ifadeler: noter kartında "tutarı noterlikte nüshadan görebilirsin" (kaynak Anexo II, Undécima; tutarlar zaten kartta, sorun değil), kalıcı oturumda gelir ölçüsünün "aile birleşimi kurallarına bağlı" olması (yüzdeler yazılmış, ayrıntı aşağıda), vatandaşlıkta "harç ödeme formu Adalet Bakanlığı sitesindedir" (tutar yok). Kartın içinde birbirini yalanlayan cümle bulunmadı.

---

## 1. dijital-gocebe-vizesi: küçük

Doğrulananlar: 3 ay ilişki, SMI yüzde 200 / ilk aile üyesi yüzde 75 / diğerleri yüzde 25, 18 yaş üstü altsoy-üstsoy bağımlılık şartı, sabıka (son 2 yıl + 5 yıl beyan), sigorta (seyahat sigortası geçersiz), diploma ya da 3 yıl deneyim, ikametgâh, 94 USD nakit ve tam tutar, pasaport 3 ay, NIE şartı: hepsi kaynak 010'da. SMI 1.221 euro/ay, 40,70 euro/gün, yıllık 17.094 euro: kaynak 039 (RD 126/2026 md. 1 ve md. 3.1). 17.094 x 2 = 34.188 doğru.

**K1 (küçük).** `steps` "yıllık 34.188 euro" diyor ve bunu kesin şart gibi yazıyor; İstanbul sayfası yalnız "200% del Salario Mínimo Interprofesional" diyor, tutar ya da hesap yöntemi yok. Hesap kartın kendi türetmesi (md. 3.1 aslında maaş mahsubunda karşılaştırma tabanı; "yıllık en az 17.094" cümlesi vize için yazılmamış). Kartın `summary` bölümü bunu dürüstçe söylüyor ("sayfa tutarı ya da hesap yöntemini göstermiyor"), ama `steps` ve `documents` bu çekinceyi taşımıyor. Önceki denetimin orta bulgusu kapandı (aylık 1.221 x 2 okuması kalktı).
- Kanıt: "queda fijado en 40,70 euros/día o 1 221 euros/mes" (md. 1); "sin que en ningún caso pueda considerarse una cuantía anual inferior a 17 094 euros" (md. 3.1); "Titular de la solicitud del visado de teletrabajo: 200% del Salario Mínimo Interprofesional" (010).
- Öneri: steps 2'ye "(hesap bizim; konsolosluk sayfası tutarı yazmıyor, aylığa çevrilince yaklaşık 2.849 euro)" ekle.

**K2 (küçük).** Kaynak 010'daki iki madde kartta yok: madde 12 (işe başlamadan önce Sosyal Güvenlik yükümlülüklerini yerine getirme taahhüdü beyanı) ve imzalı vize başvuru formu (madde 4); ayrıca NIE'nin "cog.estambul@maec.es" adresinden alındığı bilgisi. NIE şartı yazılı ama nasıl alınacağı yok.
- Kanıt: "Declaración responsable donde figure el compromiso de cumplimiento, con carácter previo al inicio de la actividad laboral o profesional, de las obligaciones en materia de seguridad social" (010 md. 12).
- Öneri: documents'a iki kalem ekle.

Sınır: Kaynak 010 sayfasının "Más información" bölümünde "Parte dispositiva del Auto de 12 de octubre de 2026 de la Sala Tercera del Tribunal Supremo" ve "Nuevas Tasas Consulares 2026" başlıkları var; ikisinin içeriği açılamadı (bkz. Bakılmayanlar). Kart not'ta ücretin değişmiş olabileceğini söylüyor; yeterli.

## 2. noter-islemleri-ve-ucretleri: küçük

Doğrulananlar (RD 1426/1989 birleşik metin, son güncelleme 17/11/2011): vekâlet 30,05; dava vekâleti 15,03; acta 36,06; vasiyet (otorgante başına) / evlilik sözleşmesi / medeni hâl 30,05; imza tasdiki 6,01 (+3,01); kopya 3,01 (12. folyodan yarısı); basit kopya 0,60; 90,15 (6.010,12'ye kadar); binde 4,5 / 1,50 / 1 / 0,5 / 0,3 basamakları ve sınırları; 6.010.121,04 üstü serbest; yüzde 5 indirim (md. Número 2.1 son paragraf); kredilerde yüzde 25; yüzde 50 listesi (a-f'den kamu, parti-sendika, kamu konut kredisi, korunan konutların sonraki devirleri). Önceki denetimin orta bulgusu (yüzde 5 indirim yok) kapandı; altı haneli rakamlar kuruşa yuvarlanıp bunun söylenmesi de yapılmış.

**K1 (küçük).** Kart noter tarifesine KDV ve diğer masraflar (tescil, vergi, suplidos) eklenip eklenmediğini hiç söylemiyor; kaynak da söylemiyor (BOE tarife metninde KDV yok). Önceki denetimin "KDV" notu hâlâ açık. Kart "ödeyeceğin tutar uygulanan indirimlere göre değişir" diyor; okuyucu tarifeyi toplam ödeme sanabilir. Kaynakta olmadığı için hata sayılmaz.
- Öneri: "Bu tutarlar yalnız noter tarifesidir; KDV ve başka masraflar ayrıca eklenebilir, noterlikten minuta (dökümlü ücret belgesi) iste" cümlesi; KDV oranı resmî kaynaktan teyit edilmeden yazılmamalı. Kaynak Anexo II Novena: noter ücreti, baz ve uygulanan tarife numaralarıyla minutada gösterilir.

**K2 (küçük).** "folio" kartta "sayfa" olarak geçiyor ("kopya sayfa başına 3,01"). İspanyolca "folio" yaprak demektir; aynı tarifenin Número 7'si matriz için "por cara escrita" (yazılı yüz başına) ayrımını yapıyor. Okuyucu "sayfa" = yüz sanıp iki katını hesaplayabilir. Ayrıca matriz yapraklarında 5. folyodan itibaren 3,005061 euro/yüz (Número 7) ve vekâletlerde 2'den fazla vekil veren için 6,01 euro eklemesi (Número 1.2) kartta yok; çok sayfalı bir senedin ücretini kart eksik gösterir.
- Kanıt: "Las copias ... devengarán 3,005061 euros por cada folio o parte de él. A partir del duodécimo folio inclusive, se percibirá la mitad"; "Los folios de matriz, a partir del quinto folio inclusive, devengarán 3,005061 euros por cada cara escrita."
- Öneri: "sayfa" yerine "yaprak (folio)"; matriz yaprakları için tek cümle.

**K3 (küçük).** `summary` sonu: "Bu indirimler yürürlükteki diğer indirimlere ek olarak uygulanır." Kaynakta "con carácter adicional a los demás descuentos" ifadesi yalnız yüzde 5 indirim için geçiyor; yüzde 25 ve yüzde 50 için böyle bir cümle yok. Cümle üçünü birden kapsıyor.
- Öneri: "yüzde 5 indirim diğer indirimlere ek olarak uygulanır" diye daralt.

## 3. oturum-izni-yenileme: küçük

Doğrulananlar: iki ay önce başvuru, üç ay sonra başvuru da uzatır ama yaptırım (md. 64.1, 80.1, 86.1; üçünde aynı); çalışmasızda yetkili yabancılar ofisi (64.1); karar 3 ay, sessizlik kabul (64.8, 80.9, 87.2); yenilenen izin çalışmasızda 2 yıl (64.7), ücretli 4 yıl (81.1), serbest 4 yıl (87.1); TIE bir ay içinde polis karakoluna (64.9); harç 16,40 (tarife 2.2.x), TIE 19,30 (4.3), çalışma izni yenilemesi 81,54 (3.2.2 ve 3.3.2), ücretli çalışmada işveren öder (Orden PJC/617/2025 md. 3.1). Önceki denetimin iki orta bulgusu (81,54 harcı; 2 yıl/4 yıl ayrımı) tam kapanmış.

**K1 (küçük, önceki denetimin 3. bulgusu kapanmadı).** Başlık "nasıl yenilenir" diyor ama yenileme şartı hiç yazılmamış; `documents` boş. Çalışmasız oturumda şart: takvim yılında fiilen 183 günden fazla İspanya'da kalmış olmak, yeterli kaynak, sağlık sigortası, çocukların okula kaydı (md. 64.2). Yılın çoğunu yurtdışında geçiren okuyucu için 183 gün kuralı reddedilme nedeni olabilir.
- Kanıt: "Haber residido de forma real y efectiva en España durante más de ciento ochenta y tres días durante el año natural." (md. 64.2.f)
- Öneri: üç satırlık şart listesi ve documents (pasaport kopyası, kaynak ve sigorta belgesi).

**K2 (küçük).** Kart yalnız çalışmasız, ücretli ve serbest izinleri anlatıyor; aynı tarifede yenilenen aile birleşimi izni (2.2.2), "çalışma izni muaf" (2.2.4) gibi türler var ve kart bunların bu kartın dışında olduğunu söylemiyor. Başlık "geçici oturum izni" genel.
- Öneri: summary'ye "bu kart çalışmasız, ücretli ve serbest çalışma izinleri içindir" cümlesi.

Küçük not: işveren çalışma izni harcını öderse bunu yabancıdan tahsil edemez (Orden md. 3.2); isteğe bağlı eklenebilir.

## 4. kalici-oturum-bes-yil: küçük

Doğrulananlar: beş yıl yasal kesintisiz; 6 ay/10 ay; çalışma nedeniyle 18 ay; usulsüz çıkış hoşgörü dışı (md. 176.a); öğrenci yüzde 50; iki ay önce başvuru, üç ay sonra uzatır; geçerli izni olup şartları zaten karşılayana iki ay penceresi uygulanmaz (177.2 son paragraf); ofis il yabancılar ofisi; belgeler (177.3); karar 3 ay, olumlu sessizlik; TIE bir ay (177.7); TIE yenileme 5/5/10 yıl, 30 yaş (178.1); harç 21,87 + 21,87 (tarife 2.6 ve 4.5); resen kontrol (177.4); kamu düzeni (177.5). Önceki denetimin orta bulgusu (iki ay istisnası) ve usulsüz çıkış bulgusu kapandı.

**K1 (küçük, önceki denetimin 2. bulgusu kısmen kapandı).** Gelir ölçüsü artık "hane iki kişiyse IPREM'in yüzde 150'si, her ek kişi için yüzde 50" diye yazılmış (md. 67.1 ile uyumlu), ama (a) IPREM'in tutarı kartın kaynaklarında yok, (b) md. 67.1 yüzdelerin aylık mı yıllık mı olduğunu söylemiyor, (c) tek başına başvuran için hangi rakamın aranacağı belli değil; kart bunu açıklamıyor. Okuyucu kendi durumunda ne kadar göstereceğini çıkaramaz.
- Kanıt: "Los términos y las cuantías para valorar el cumplimiento de este requisito serán los previstos en materia de reagrupación familiar" (md. 176.b); "al 150 % del IPREM, en unidades familiares que incluyan a la persona reagrupante y a un familiar reagrupado, y del 50 % del IPREM por cada miembro adicional" (md. 67.1).
- Öneri: "tek başına başvuranda tam rakamı yabancılar ofisinden teyit et" uyarısı.

**K2 (küçük).** Adım 4: "İspanya'da değilsen oturacağın bölgenin konsolosluğuna şahsen ver". Kaynak: "oficina consular en cuya demarcación residan" (şu an oturduğun yeri kapsayan konsolosluk), dosya oradan "oturacağın il" ofisine iletilir. Kart iki ayrı yeri karıştırıp "oturacağın" diyor; Türkiye'den başvuran biri "İspanya'daki bölgenin konsolosluğu" diye anlayabilir.
- Kanıt: "deberán presentar personalmente la solicitud ante la oficina consular en cuya demarcación residan, que dará traslado a la oficina de extranjería competente ..., que se corresponderá con la de la provincia en la que vayan a fijar su domicilio en España." (md. 177.1)
- Öneri: "İspanya dışındaysan oturduğun yeri kapsayan İspanyol konsolosluğuna şahsen ver; konsolosluk dosyayı, ileride yaşayacağın ilin yabancılar ofisine iletir."

## 5. arraigo-kok-salma-oturumu: orta

Doğrulananlar: beş tür (md. 125); bir yıl, aile arraigosunda beş yıl; iki yıl kesintisiz (126.b), aile arraigosunda asgari kalış yok; sabıka son beş yıl "İspanya'ya girişten önceki" ve 5 yıl kesintisiz bulunana üçüncü ülke sabıkası istenmez (126.d, 130.2); sosyal-çalışma 20 saat + asgari ücret (127.b); sosyal IPREM yüzde 100 + bağ ya da uyum raporu (127.c); ikinci fırsat iki yıl içinde olağanüstü dışı izin (127.a); aile arraigosu yalnız AB/AEA/İsviçre vatandaşı çocuğun ebeveyni/vasisi (127.e), Türk vatandaşı çocuk için kapalı; temsilci yalnız küçük ve destek gerektiren engelli (130.1); md. 126.h (RD 316/2026, 16.04.2026'dan itibaren); olağanüstü arraigo DA 21, başvuru 30.06.2026'ya kadar (DA 21.6). Önceki denetimin iki orta bulgusu (aile arraigosu koşulsuz cazibe; "documents" havalesi) kapandı.

**O1 (orta, yeni, çeviri hatası).** Adım 4: sosyal-eğitim arraigosu için "ortaöğretim sonrası eğitime ... kayıtlı olmalı". Kaynak "educación secundaria postobligatoria" diyor: zorunlu eğitimden sonraki ortaöğretim (lise düzeyi, bachillerato, orta dereceli meslek ciclo formativo de grado medio). Türkçede "ortaöğretim sonrası" yükseköğretim öncesi değil, ortaöğretimden SONRA anlamına gelir (üniversite/önlisans); 17-18 yaşında lise ya da mesleki lise okumak isteyen okuyucu kendini dışarıda sanabilir. Kaynak 52.1.b) ayrıca ciclo formativo de grado medio'yu kapsıyor; kart "tam bir mesleki sertifika programı" ve "yetişkin zorunlu eğitimi" diyor ama lise düzeyini açıkça saymıyor (yetişkin eğitimi için "yüz yüze" koşulu da yazılmamış).
- Kanıt: "Realización de estudios de educación secundaria postobligatoria en un centro de enseñanza autorizado en España" (md. 52.1.b, md. 127.d bu maddeye atıf yapıyor); "quedarán incluidos ... los ciclos formativos de grado medio".
- Öneri: "zorunlu eğitimden sonraki ortaöğretim (lise, orta dereceli meslek okulu)" yaz; "ortaöğretim sonrası" ifadesini kaldır.

**K1 (küçük, önceki 4. bulgu kapanmadı).** `cost` boş; kartta "790 kodu 012" harç belgesi var ama tutar yok. Tarife: arraigo için 38,28 euro (Orden PJC/617/2025, tarife 2.3.1). Bu Orden kartın source_ids'inde (004, 009) yok; eklenecekse kaynak 006 kartın kaynağına alınmalı.
- Öneri: cost: "Arraigo başvuru harcı 38,28 euro" ve 006'yı kaynak yap.

**K2 (küçük, kaynak seçimi).** Kartın EX10 + "790 kodu 012" cümlesi arraigo için. Kaynak 009 (polis sayfası) arraigo değil, polis/savcılık iş birliği ve ulusal güvenlik iznini anlatıyor; arraigo için EX10 ya da 790-012 geçmiyor (RD 1155/2024 metninde de form adı yok). Sayfanın menüsünde aynı "circunstancias excepcionales (EX10)" bağlantısı olduğu için büyük olasılıkla doğru, ama kartın kaynağıyla doğrulanamıyor. Kart "polis sayfasındaki olağanüstü durumlar başvurusunda kullanılan" diye dürüst çerçeveliyor; okuyucuyu yanıltmıyor.
- Öneri: arraigo için EX10'u gösteren resmî sayfa bul ya da cümleyi "büyük olasılıkla" ile yumuşat.

**K3 (küçük, önceki 3. bulgu kısmen).** Adım 6 "Başvuruyu şahsen yap; yasal temsilci yalnız küçükler ve engelliler adına" md. 130.1 ile uyumlu, ama aynı RD'nin md. 197.1 şahsen sunmayı elektronik sunumu da kapsayacak şekilde tanımlıyor ve 197.4 yetişkinin noter vekâleti ya da apud acta ile temsilciyle başvurmasına izin veriyor. Kartın cümlesi "yalnız şahsen" diye okunur.
- Kanıt: "se entenderá cumplida la exigencia de comparecencia personal, tanto si la presentación se realiza de forma presencial, como si realiza a través de medios electrónicos" (md. 197.1).
- Öneri: "şahsen ya da elektronik; vekil için noter vekâleti gerekir".

**K4 (küçük).** İkinci fırsat şartı eksik: md. 127.a "yenilenmemesi kamu düzeni, güvenlik ve sağlık dışındaki sebeplerle olmuş" koşulunu da arıyor; kart yalnız "iki yıl içinde izin sahibi olmuş olmak" diyor. Sosyal-eğitimde haftada en çok 30 saat çalışma sınırı (md. 131.b) kartta yok (önceki denetim de 131.b'yi saymıştı).
- Öneri: iki cümle ekle.

## 6. ispanyol-vatandasligi-basvurusu: küçük

Doğrulananlar: 10/5/2/1 yıl ve gruplar (CC md. 22.1-22.2); "legal, kesintisiz, hemen önceki" (22.3); iyi sivil davranış ve entegrasyon (22.4); DELE en az A2 + CCSE (RD 1004/2015 md. 6.1); vazgeçme beyanı ve istisna ülkeler (CC md. 23.b ve 24.1); 14 yaş üstü ve yemin (23.a); başvuru elektronik, form Adalet Bakanlığı sitesinde (md. 4.1); harç formu Bakanlık sitesinde, sınav ücretleri dahil değil (DA 1.ª); karar en çok 1 yıl, sessizlik ret (md. 11.3); 180 gün içinde Registro Civil'de beyan/yemin ve etkisizlik (md. 12.1 ve CC 21.4); carta de naturaleza RD ile takdire bağlı, bakan gerekçeli reddedebilir (CC md. 21.1-21.2). Önceki denetimin orta bulgusu (başvuru yolu yok) ve küçük bulgusu (dul eşi, "14 yaşından büyüksen") kapandı.

**K1 (küçük).** "DELE ve CCSE sınavlarını geçmelisin" mutlak yazılmış. RD 1004/2015 md. 6.5: daha önce en az A2 DELE diploması almış olan ve 19 İspanyolca konuşulan ülkenin vatandaşı DELE'den muaftır. Türk okuyucu için önemli olan kısım: daha önce DELE A2/B1/B2 almışsa yeniden girmez (ve Instituto Cervantes'ten sonuç resen sorgulanır, md. 6.4 ve md. 8).
- Kanıt: "Estarán dispensados de la prueba de examen DELE los interesados que hayan obtenido con anterioridad un diploma de español como lengua extranjera (DELE) como mínimo del nivel A2" (md. 6.5).
- Öneri: bir cümle ("daha önce DELE A2 ya da üstü aldıysan DELE tekrar gerekmez").

**K2 (küçük, önceki 3. bulgu açık).** Önceki uyrukluktan vazgeçme beyanının Türkiye tarafındaki sonuçları (Türk vatandaşlığı kaybı olup olmadığı, Mavi Kart) kartta yok; kaynakta da yok. Ayrıca `cost` başvuru harcının tutarını vermiyor (ödeme formu Bakanlık sitesinde diyor). Her ikisi kaynak dışı; hata değil ama Türk okuyucunun asıl sorduğu iki şey cevapsız.
- Öneri: "Türkiye'deki sonuçları için Türk makamlarına danış" uyarısı (kaynaksız tavsiye, yazar teyit etmeli); harç tutarı resmî kaynaktan teyitle eklenebilir (Ley 19/2015'te geçer, kartın kaynaklarında yok).

**K3 (küçük, çeviri).** `note`: "Ödüllendirme yoluyla (carta de naturaleza) vatandaşlık". Kaynak "carta de naturaleza ... otorgada discrecionalmente mediante Real Decreto, cuando concurran circunstancias excepcionales" der; ödül anlamı yok. Aynı cümlenin devamı (Hükümet takdiri, olağanüstü koşul) doğru.
- Öneri: "Olağanüstü durumlarda Hükümetin Real Decreto ile takdirle verdiği 'doğal vatandaşlık mektubu' (carta de naturaleza) yolu".

Küçük not: md. 23.b "naturales de" (o ülkede doğanlar) ifadesi kartta "uyruklularıyla" diye geçiyor; iki ifade hukuken aynı değil ama bu okuyucu için sonuç doğurmuyor.

## 7. brexit-sonrasi-ingiliz-oturumu: küçük

Doğrulananlar: 31 Ocak 2020 çıkış; 31 Aralık 2020 öncesi yerleşenler Çekilme Anlaşması hakları, yeni statü şart değil, md. 18.4 belgesi hakkı; üç sertifika durumunda tek adım ve EX23 + pasaport + 790-012 + fotoğraf (Instrucción Cuarta, a/b/c); sertifikasızda iki adım: ofise EX20 + pasaport + ikamet başlangıcı belgesi (+ Orden PRE/1490/2012 md. 3 belgeleri), karar en çok 3 ay, bir ay içinde polise EX23 (Cuarta d); geçici 5 yıl / kalıcı 10 yıl; "Temporal"/"Permanente"; üç aylık süre yalnız hakkı geçiş döneminden sonra doğanlar için, süre geçtiyse "plazo adicional" (Tercera.2); ön randevu (Tercera.3); 2 Temmuz 2020 tarihli ortak talimat (BOE 4 Temmuz 2020); harç 12,00 euro (polis tarife sayfası, kaynak 003). Önceki denetimin orta bulgusu (EX20 yolu yok) ve küçük bulgusu (aile üyeleri) kapandı; önceki ciddi 3 ay çelişkisi de kapalı.

**K1 (küçük).** `note` Türk dahil üçüncü ülke vatandaşı aile üyelerinin de belge isteyebileceğini söylüyor (doğru, Quinta.1), ama adımlar ve `documents` yalnız İngiliz vatandaşı yolunu anlatıyor. Aile üyesi için ofis formu EX20 değil EX21 ("Solicitud de documento de residencia art. 18.4 para familiares, NTP, de nacionales del Reino Unido") ve ofise bağ belgesi (evlilik/ortaklık, apostilli ve tercümeli), İngiliz yakının kayıt/ikamet belgesi, gerekiyorsa bağımlılık belgesi verilir. Türk eş okuyucu adımları izleyip EX20 ile gidebilir.
- Kanıt: "Impreso de solicitud -EX 21 Solicitud de documento de residencia art. 18.4 para familiares, NTP, de nacionales del Reino Unido" ve "Certificado de registro o documento de residencia del nacional del Reino Unido al que acompañan" (Quinta.d.i).
- Öneri: not'a bir cümle: "Aile üyeleri ofiste EX21 kullanır ve bağ belgesini (apostilli, tercümeli) ve İngiliz yakının belgesini ekler."

**K2 (küçük, önceki küçük not hâlâ açık).** Yenileme anlatılmamış: geçici belge dolunca 10 yıllık kalıcıya yenilenir; yenileme başvurusu belgenin bitiminden önceki ay içinde (üç ay sonrasına kadar yaptırımla) yapılır (Instrucción Sexta). Kart yalnız "beş yıl dolduysa kalıcı iste" diyor.
- Öneri: bir cümle.

## 8. clave-pin-ve-permanente-farki: temiz

Cl@ve Permanente tarifi (DNI/NIE, kullanıcı kodu, kendi şifresi, kayıt şart, yüksek güvenlikte SMS OTP): kaynak 024 ile birebir. Cl@ve uygulaması, Android 8 / iOS 15, Google Play / Apple Store, eski PIN kullanıcılarının güncellenmesi, Cl@ve Móvil ile kimlik doğrulama isteği, SMS kodu ya da sertifikayla etkinleştirme, kayıt yolları (sertifika, davet mektubu, yüz yüze, video): kaynak 038 ile birebir. DNIe seçeneğinin çıkarılması Türk okuyucu için isabetli. Başlıktaki "Cl@ve uygulaması (Cl@ve Móvil)" ifadesi eski "PIN = Móvil" eşitliğini artık kurmuyor; önceki denetimin her iki bulgusu kapandı. Havale yok, çelişki yok.
Not (hata değil): "davet mektubu" ve "yüz yüze kayıt"ın nereden/nasıl yapıldığı kaynakta da yok (kaynak "How can I register?" bölümüne havale ediyor); kart bu yolları saymakla yetinmiş, uydurma ayrıntı eklememiş.

## 9. belge-ceviri-ve-apostil: küçük

Doğrulananlar: yeminli tercümanın tercümesi resmî nitelikli, mahkemelere ve idari makamlara sunulabilir; imza ve mühürle onay; Dışişleri Bakanlığı atar, Oficina de Interpretación de Lenguas listeyi yayımlar, aracılık etmez; Katalanca/Galiçyaca/Baskça 1992'den beri özerk yönetimler (kaynak 026). Apostil tanımı, 5 Ekim 1961 Sözleşmesi, apostilli belge ek onay olmadan tanınır; adli/idari/noter belgeleri apostillenebilir; noter apostili yalnız Colegio de Notarios; diplomatik/konsolosluk ve ticari/gümrük belgeleri apostillenemez (kaynak 027). Önceki denetimin orta bulgusu (kurum adı yok, 027 kayıp) kapandı: 027 geri alınmış, Ministerio de Justicia ve Colegio de Notarios adıyla yazılmış, Türkiye'ye dair iddia kaldırılıp kart İspanya belgeleriyle sınırlanmış.

**K1 (küçük).** "İspanya'da düzenlenen adli ya da idari belge için başvuruyu İspanya Adalet Bakanlığı'nın apostil sayfasından yaparsın" cümlesi kaynakta bu kadar açık değil: sayfa adli, idari ve noter belgelerinin apostillenebileceğini sayıyor ve "Solicitud de Apostilla" bağlantıları veriyor; adli ve idari belgenin TEK mercisinin Bakanlık olduğunu söylemiyor (yalnız noter için "únicamente" var). Cümle "başvurunu şu sayfadan yap" olarak okunduğunda doğru; "tek merci" olarak okunduğunda kaynağı aşıyor.
- Kanıt: "Documentos judiciales / Documentos administrativos / Documentos notariales: Recuerde que la apostilla de los documentos notariales corresponde, únicamente, a los Colegio de Notarios" (027).
- Öneri: "başvuru sayfası" demekle yetin ya da kaynağa başka resmî bir madde ekle.

**K2 (küçük).** Başlık "Resmî belgeler nasıl tercüme ve apostil edilir?" genel; kart yalnız İspanya'da düzenlenen belgeleri anlatıyor ve bunu not'ta söylüyor (iyi), ama Türk okuyucunun en olası ihtiyacı (Türkiye'de düzenlenmiş belgenin İspanya'da kullanılması) için hangi kuruma gideceği yok; alt başlık yalnız "apostil belgenin düzenlendiği ülkede alınır" diyor. `cost` boş (apostil ve tercüman ücreti kaynakta yok).
- Öneri: başlığı "İspanya'da düzenlenen belgelerin apostili ve yeminli tercüme" diye daralt ya da Türkiye tarafı için resmî Türk kaynağıyla ayrı kart yaz.

## 10. kar-amaci-gutmeyen-oturum-vizesi: orta

Doğrulananlar: IPREM yüzde 400 ve yüzde 100 (md. 62.1; kaynak 040); 2026 için 2.400 ve 600 euro/ay (kaynak 012); 2.400 x 12 = 28.800, 600 x 12 = 7.200 hesabı doğru ve md. 62.2 ("cuantía global ... en relación con el tiempo de vigencia", md. 61.4 ilk izin 1 yıl) ile uyumlu; çocuk kapsamı (reşit olmayan evlenmemiş; reşit yalnız engelli/sağlık) kaynak 040 ve md. 61.3 ile birebir; çalışma izni vermez; pasaport 1 yıl, iki boş sayfa, 10 yıldan eski kabul edilmez; EX-01; 790-052 başlık 2.1; BLS ön randevu; sabıka 5 yıl; tıbbi rapor; konsolosluk bölgesi ikameti; vize 365 gün; TIE bir ay (kaynak 040). Önceki denetimin üç bulgusundan ikisi (toplam tutar; çocuk kapsamı) kapandı.

**O1 (orta, yeni).** `timing`: "Yasal karar süresi, oturum izninde olumlu karar alındıktan sonraki günden itibaren bir aydır." Bu cümle kaynak 040'ın bozuk Türkçe karşılığı ve okuyucuya "karar bir ay" izlenimi veriyor, ama anlamı daireseldir (karar süresi olumlu karardan sonra başlıyor?). Kaynaklar da birbirini tutmuyor: Delhi sayfası "yasal karar süresi başvurudan itibaren 3 ay, mülakat/ek belge istenirse uzar" diyor; RD 1155/2024 md. 63.4 ise oturum izni kararını konsolosluktan bildirimin alınmasından itibaren bir ay ve süre geçince ret sayılır diyor (bu madde kartın kaynaklarında yok). Kart tek bir cümleyle belirsiz bir süre veriyor ve ret-sessizliğini ya da diğer kaynağın 3 ayını anmıyor. Okuyucu sürecin bir ay süreceğini sanabilir.
- Kanıt: "El plazo legal para tomar una decisión es de un mes contado a partir del día siguiente a la recepción de la resolución favorable sobre la autroización de residencia." (040); "The legal period for reaching a decision is of 3 months from the day after the application submission date, but this period may be extended" (012).
- Öneri: "İstanbul sayfası karar süresini 'oturum izni kararı alındıktan sonra bir ay' diye yazıyor; başka bir konsolosluk sayfası 3 ay yazıyor. Toplam süre için başvuru merkezinden teyit al." diye yaz; kesin süre gibi sunma.

**K1 (küçük, önceki 3. bulgu kapanmadı).** `cost` boş; 790-052 harcı tutarı yok (Orden PJC/617/2025 tarife 2.1.1: 10,94 euro; kart kaynaklarında yok). BLS hizmet bedeli ("tasa por servicios prestados", kaynak 040) ve konsolosluk vize ücreti de yazılmamış.
- Öneri: "790-052 harcı 10,94 euro" (kaynak 006 eklenerek); BLS ve vize ücreti için "güncel tarifeden teyit et".

**K2 (küçük).** Hem özet hem adım 1 "maddi imkân ya da düzenli gelir" diyor ve hemen ardından "ilk yıl için başvuran 28.800 euro belgelemelidir" ekliyor. md. 62.1 iki ayrı yol sayıyor: yeterli maddi imkân (toplam, yani birikim) ya da düzenli gelir kaynağı. Düzenli geliri olan (ör. aylık 2.400 euro emekli maaşı) biri 28.800 euro birikim göstermek zorunda değil; kart ikisini karıştırıyor.
- Kanıt: "contar con medios económicos suficientes para el periodo de residencia de la autorización, o acreditar una fuente de percepción periódica de ingresos" (md. 62.1).
- Öneri: "birikimle başvuruyorsan toplam 28.800 euro, düzenli gelirle başvuruyorsan aylık en az 2.400 euro" diye ayır.

---

## Önceki denetimin (denetim_bagimsiz_2) bulgularının kapanma durumu (bu 10 kart)

| Kart | Önceki bulgu | Durum |
|---|---|---|
| dijital-gocebe | #1 aylık 1.221 x 2 yanıltıcı | kapandı (yıllık 34.188; kısmi çekince K1) |
| dijital-gocebe | #2 18 yaş üstü altsoy/üstsoy, madde 12, NIE adresi | altsoy/üstsoy kapandı; madde 12 ve NIE adresi açık (K2) |
| dijital-gocebe | #3 94 USD teyit | kapandı (cost ve not tarihli) |
| noter | #1 yüzde 5 indirim | kapandı |
| noter | #2 KDV | açık (kaynak yok; K1) |
| noter | #3 yuvarlama, başlık | kapandı |
| yenileme | #1 81,54 harcı | kapandı |
| yenileme | #2 2 yıl / 4 yıl | kapandı (64.7, 81.1, 87.1 doğrulandı) |
| yenileme | #3 şartlar, 183 gün | açık (K1) |
| kalıcı | #1 iki ay istisnası | kapandı |
| kalıcı | #2 gelir havalesi | kısmen (K1) |
| kalıcı | #3 usulsüz çıkış | kapandı |
| arraigo | #1 aile arraigosu kapsamı | kapandı |
| arraigo | #2 documents havalesi, eksik türler | kapandı (O1 yeni çeviri hatasıyla) |
| arraigo | #3 temsilci/sabıka | sabıka kapandı; temsilci kısmen (K3) |
| arraigo | #4 cost | açık (K1) |
| vatandaşlık | #1 başvuru yolu, süre, harç yapısı, 180 gün | kapandı |
| vatandaşlık | #2 dul eşi, yaş | kapandı |
| vatandaşlık | #3 Türkiye tarafı | açık (K2) |
| brexit | #1 EX20 yolu | kapandı |
| brexit | #2 üçüncü ülke aile | kapandı (EX21 eksiği K1) |
| clave | #1 kayıt yolları, DNIe | kapandı |
| clave | #2 PIN = Móvil | kapandı |
| belge | #1 kurum adı, 027 | kapandı (K1 çekince) |
| belge | #2 cost | açık (K2) |
| NLV | #1 toplam tutar | kapandı (K2 küçük karışıklık) |
| NLV | #2 çocuk kapsamı | kapandı |
| NLV | #3 cost, süre | cost açık (K1); süre bu denetimde O1 |

## Bakılmayanlar ve sınırlar

- Kaynak 010 ve 040 sayfalarındaki "Parte dispositiva del Auto de 12 de octubre de 2026 de la Sala Tercera del Tribunal Supremo" ve "Nuevas Tasas Consulares 2026" duyurularının içeriği okunamadı. Arama yalnız konsolosluk duyurularını buldu (Stuttgart, Havana, Bordeaux, Saraybosna sitelerinde de aynı başlık var; yani siteler arası genel bir duyuru, vize sayfalarına özgü görünmüyor) ve BOE PDF'ine bağlantı veriyor; kararın konusu doğrulanamadı. Dijital göçebe ve NLV kartlarıyla çelişkisi saptanmadı ama teyit edilmedi. Önerim: yazar BOE PDF'ini açıp konunun vize/harçla ilgisini bir kez kontrol etsin.
- Yargıtay 8 Temmuz 2026 ve 29 Temmuz 2026 kararlarının (BOE-A-2026-19632/19633) tüm iptal listesi okunmadı; yalnız RD 1155/2024 birleşik metnindeki işaretlere (md. 197.2: zorunlu elektronik başvuru iptali) bakıldı. İptal edilen md. 197.2 kartlardan hiçbirinde atıf yapılan bir hüküm değil. Kartlarda kullanılan maddeler (61-64, 67, 80-81, 86-87, 125-127, 130-132, 176-178, 197.1, 197.4, DA 21) metindeki güncel (22/09/2026) halleriyle okundu.
- Código Civil md. 22'nin 2026'da değişip değişmediği: kaynak anlık görüntüsünde md. 21-23 son güncelleme 03/09/2021 (md. 23: 01/10/2015); canlı BOE sayfası WebFetch ile kısmen açıldı, md. 22'ye gelmeden metin kesildi (belgenin genel son güncellemesi 03/01/2025 görünüyor, hangi maddeyi etkilediği teyit edilemedi).
- Yüzde 5 notar indirimi uygulama sırası (25/50 ile çarpımsal mı toplamsal mı) kaynakta açık değil; kart bunu iddia etmiyor.
- Noter KDV, vatandaşlık harcı tutarı, Türkiye'de apostil kurumu, Türk vatandaşlığına etkisi: kartların kaynaklarında yok; öneriler "yazar teyit etmeli" niteliğinde, tahmin olarak yazılmadı.
- claims.*.jsonl, Bağlantılar.*.jsonl, iddia_defteri satırları ve valid_until.json denetlenmedi; yalnız kart metinleri, kaynak metinleri ve değişiklik kaydı (degisiklik_editor2.jsonl) okundu. Görsel alanı (visual_json) bu kartlarda boş.
- Ücret ve IPREM 2026 tutarları (600 euro) yalnız kartın kaynağında (Yeni Delhi sayfası) doğrulandı; IPREM'in resmî BOE metni açılmadı.
