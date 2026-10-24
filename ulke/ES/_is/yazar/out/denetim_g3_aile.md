# Bağımsız denetim G3: ES ulusal paketi, konu "aile" (4 kart)

Denetim tarihi: 2026-10-24. Yöntem: kartın olgusal cümleleri kartın KENDİ kaynak metniyle (aile_kaynaklar.jsonl -> snap_kesif_aile/*.txt) karşılaştırıldı. Canlı kontrol: UNEDasiss publico_destino + FAQ, seg-social IMV, becaseducacion.gob.es (qué necesitas, cómo solicitarla). Kartlara dokunulmadı.

Derece: ciddi = yanlış/yanıltıcı, orta = eksik/kapsam/koşul atlama, küçük = ifade/kural ihlali.

## 1. egitim-sistemi-zorunlu-egitim-ve-okul-turleri (kaynak 117, LOE)

Doğrulananlar: 6–16 yaş, on yıl, "obligatoria y gratuita para todas las personas" (art. 4); ESO 4 sınıf 12–16 (art. 22); infantil 0–6 gönüllü (art. 12); temel eğitim = primaria+ESO+grado básico (art. 3.3); art. 84.2/84.3/84.5–84.7 ölçütleri, ayrımcılık, adscrito, taşınma tercihi; art. 108.6 okul seçme hakkı.

**1.1 ORTA, "Temel eğitim (6–16 yaş) herkes için ücretsizdir" (cost) ve özet "zorunludur ve herkes için ücretsizdir".**
- Kaynak: "La enseñanza básica ... es obligatoria y gratuita para todas las personas" (art. 4.1). Kart aynı sayfada özel okulları da sıralıyor; özel (concertado olmayan) okul ücretlidir ve kaynak bunu yasaklamıyor/ücretsiz saymıyor. Okuyucu "özel okul da bedava" anlayabilir. Kaynakta kamu/concertado için ücretsizlik ayrımı yok.
- Öneri: "Zorunlu temel eğitim yasal olarak ücretsizdir (LOE art. 4); okul türüne göre ek ücretler kaynakta açıklanmamıştır" yerine yalnız kaynağın dediğini yaz: "temel eğitim herkes için zorunlu ve ücretsiz bir eğitim olarak tanımlanır" ve özel okul cümlesini bundan ayır.

**1.2 KÜÇÜK, başlık/altbaşlık "kamu, özel ve concertado olarak ayrılır".**
- Kaynak art. 108.1/108.3: "Los centros docentes se clasifican en públicos y privados ... centros privados concertados los centros privados acogidos al régimen de conciertos". Concertado özel okulun alt türüdür; kart üçlü sınıf gibi sunuyor (özet gövdesi doğru: "özel okullar ve devletle sözleşmeli özel okullar").
- Öneri: altbaşlığı "kamu ve özel okullar; özel okulların bir kısmı devletle sözleşmeli (concertado)" yap.

Not (denetim notu, bulgu sayılmadı): yabancı çocuğun kaydında ikamet izni gerekip gerekmediği kartta yok; gaps.md'de kayıtlı. Kaynaktaki "todas las personas" ile çelişen bir şey yazılmamış.

## 2. yabanci-lise-diplomasi-ile-universiteye-giris (kaynak 112, 113)

Doğrulananlar: RD 534/2024 art. 6.1 a-c ve 6.2 (sınavsız + homologación gerekmez); UNEDasiss grup ve ülke listesi canlı sayfayla birebir aynı (36 sistem, Türkiye YOK); PCE en az 2 / en az 4; modalite/PAU benzeri/dil belgesi; özel üniversite farkı; "ayrı grup" cümlesi (DA 4).

**2.1 ORTA, başlıktaki "denklik (homologación) şart mı?" sorusuna AB dışı yol için net cevap yok.**
- Kart: "liseyi İspanyol bachillerato'suna homologación şartlarını karşılayacak biçimde bitirmiş olmak" (özet, adım 4); homologación "yaptırman gerekmez" yalnız sınavsız grup için.
- Kaynak 113: "Pueden acceder por esta vía las personas ... que cumplan con los requisitos para obtener la homologación de sus estudios al bachillerato español". Kartın kaynağı bu kadar. CANLI UNEDasiss FAQ (unedasiss.uned.es/faqs, madde 4 ve 11): "Uno de los trámites obligatorios es solicitar la HOMOLOGACIÓN de sus estudios al título de bachiller español" ve "si vienes de un sistema educativo fuera de la Unión Europea o fuera de un país con convenio, debes solicitar la Homologación del Título de Bachiller como trámite indispensable para obtener la acreditación UNEDasiss". Yani Türk lise diploması için homologación yapılmış olmalı; kart "şartlarını karşıla" diyerek bunu yumuşatıyor ve başlıktaki soruya (Türk okuyucunun asıl sorusu) ilk cümlede "AB dışı için evet, şart" demiyor.
- Öneri: Özetin başına "AB dışı sistemlerden (Türkiye dahil) gelenler için homologación gerekir; AB/karşılıklılık/Avrupa Okulları/IB grubu için gerekmez" ekle; FAQ'ı kaynak/claim olarak aç (kart başına 2 kaynak kotası: 112 yerine FAQ düşünülebilir).

**2.2 KÜÇÜK (Türk okuyucu), Türkiye'nin hangi yola girdiği kartta yazılı değil.**
- Canlı doğrulama: UNEDasiss grup listesinde Türkiye yok (36 sistem, canlı = kart). Dolayısıyla "AB dışı diğer ülkeler" yolu Türk diploması için mantıksal olarak doğru. ANCAK ülke bazlı sayfa (unedasiss.uned.es/1162707 "Información país por país") JS/ajax ile çalışıyor, ajax/ops.php oturum istiyor ("Tienes que volver a identificarte"); Türkiye seçimi canlı BAKILAMADI. Kartta "Türkiye listede yok, bu yola girer" cümlesi de yok; okuyucu notu kendisi taramak zorunda.
- Öneri: kaynakta açıkça yazan "listede olmayan = Otros países fuera de la UE" bağını bir cümleyle kur; "Türkiye listede yoktur" ancak listeden çıkarım, Türkiye'ye özel bir kural değil, böyle işaretle.

**2.3 KÜÇÜK, "UNEDasiss'in sınavsız grup listesi" (adım 4, özet) ifadesi.**
- Kaynak 113 listeyi "Sistemas Educativos incluidos en este apartado" diye veriyor, "sınavsız" demiyor; sınavsızlık RD art. 6'dan geliyor ve art. 6 Çin/Kolombiya/Andorra'yı adıyla saymıyor ("acuerdos ... reciprocidad"). Eşleştirme yazarın çıkarımı.
- Öneri: "UNEDasiss'in 'AB, EHEA, IB, Avrupa Okulları, Çin ve Kolombiya' grubu" de.

**2.4 KÜÇÜK, sınavsız grupta meslek lisesi şartı atlanmış.**
- Kaynak 113: "Estudios vocacionales o profesionales, siempre que estén incluidos en la Orden EFD/550/2025 u obtengan informe favorable del Ministerio". Kart genel lise koşulunu yazıyor, bu koşulu yazmıyor (gaps.md'de bilerek yazılmadı denmiş ama kart "diploma" diyerek kapsamı genelliyor).
- Öneri: "genel ortaöğretim (meslek diplomalarında ek koşul vardır)" diye sınırla ya da koşulu yaz.

## 3. ingreso-minimo-vital-ve-cocuk-destegi (kaynak 114, 115)

Canlı seg-social sayfası kaynak 114 ile uyumlu: 733,6 € (2026), 953,68 €, 115 / 80,50 / 57,50 €, 1 Ocak yaşı, %300/%150, 10 € eşiği, 23 yaş, 6 ay birim, 020, 1 yıl ikamet, hesap yöntemi, kimlik belgeleri, "residencia ... autorización de residencia, en cualquiera de sus modalidades". BOE Ley 19/2021 art. 10.1.a ile de uyumlu. valid_until 2026-12-31 uygun (2027 tutarları Ocak'ta değişir). Sayı hatası yok.

**3.1 ORTA, adım 6: "Çocuk başına aile yardımı ... alıyorsan IMV ile birlikte alamazsın; aralarından birini seçersin."**
- Kaynak: "incompatible con la percepción de la asignación económica por hijo o menor acogido a cargo, sin discapacidad o con discapacidad inferior al 33 por 100, cuando exista identidad de causante o beneficiarios". IMV daha yüksekse "se reconocerá el derecho a la prestación de IMV ... extinguirá el derecho a la asignación"; seçme yalnız IMV düşükse söz konusu ("Si optara por la asignación ... se denegará ... IMV").
- Kart iki koşulu (çocuğun engeli %33'ten az, aynı çocuk) atlıyor ve "seçersin"i genel kural yapıyor.
- Öneri: "Aynı çocuk için (çocuğun engel oranı %33'ün altındaysa) aile yardımıyla birlikte alınamaz; IMV daha yüksekse IMV tanınır ve aile yardımı sona erer" yaz.

**3.2 ORTA, "kimlere verilir" sorusunda varlık (patrimonio) şartı ve dışlama kuralları yok.**
- Kaynak 114: "No se considera en situación de vulnerabilidad económica ... patrimonio neto ... igual o superior a tres veces ... En 2026 esto equivale a 26.409,60 euros" ve aktif sınırı 52.819,20 €; ayrıca şirket yöneticisi dışlaması. Kart yalnız garantili geliri ve 10 € farkı yazıyor; varlık sınırı ancak çocuk eki notunda "%150" olarak dolaylı geçiyor, ana sınır hiç yok. Okuyucu geliri düşük ama birikimi olan bir aile için yanlış umutlanabilir.
- Öneri: tek cümleyle ana varlık sınırını (bireysel için 26.409,60 €, 2026) ve birim tablosuna atıf olmadan "birim büyüklüğüne göre artar" yaz.

**3.3 KÜÇÜK, bir yıl ikamet istisnası eksik ve "yabancı için" daraltması.**
- Kart: istisna listesi "doğum, evlat edinme, çocukların aile birleşimi, evlat edinme amaçlı koruma, kalıcı aile yanında bakım". Kaynak 3 madde: ayrıca "víctimas de trata ... y explotación sexual" ve "mujeres víctimas de violencia de género". Ayrıca kaynak (art. 10.1: "Todas las personas beneficiarias") şartı tüm yararlanıcılara koyuyor; kart "yabancı için" diyor.
- Öneri: "tüm yararlanıcılar için (İspanyollar dahil)" ve eksik iki istisnayı ekle.

**3.4 KÜÇÜK, özet: "oturum izninle ... ya da AB vatandaşı aile üyesi kartıyla kanıtlanır; Türk vatandaşı olarak bu gruptasın."**
- Kaynak doğru ("tarjeta de familiar de ciudadano de la Unión o autorización de residencia"). Fakat "bu gruptasın" AB vatandaşının eşi olan Türk için de geçerli; kart sadece izin tipi varmış gibi okutuyor. Hata değil, belirsizlik. Öneri: "(Türk vatandaşıysan genelde oturum izni; AB vatandaşının aile üyesiysen aile üyesi kartı)".

## 4. mec-burslari-ab-disi-sart-ve-basvuru-donemi (kaynak 118, 116)

Doğrulananlar (kaynak ve CANLI becaseducacion sayfası aynı): "menor de 18 años o permiso de residencia a 31 de diciembre de 2025; no es suficiente la autorización de estancia", AB vatandaşı için matrícula istisnası, 60 kredi, 5 puan, %65/%80/%90 oranları, 1.700 / 2.700 / 50–125 €, ejercicio 2025, RD 179/2026, 19 Mayıs.

**4.1 ORTA, başlıktaki "başvuru dönemi ne zaman?" üniversite bursu için cevaplanmamış; yıl yok.**
- Kart: "FP, bachillerato ve diğer üniversite dışı öğrenimler için başvuru süresi 19 Mayıs'ta sona erdi" (kaynak 116 = FP sayfası: "El plazo de solicitud terminó el 19 de mayo"). Kart başlığı üniversite bursu şartını soruyor ama dönem cevabı yalnız FP için. CANLI becaseducacion.gob.es/universidad-grado-master/como-solicitarla.html aynı cümleyi veriyor ("El plazo de solicitud terminó el 19 de mayo"), yani üniversite için de 19 Mayıs; bu kartın kaynağında (118) yok. İki sayfada da yıl yazmıyor; kart 2026-27 çağrısı bağlamında "bitti" diyor ama yıl/çağrı bağını kaynak vermiyor.
- Ayrıca adım 4-5 ve özetteki "Başvuru tamamen sede electrónica üzerinden" (Cl@ve, belge istenmez) FP sayfasından (116) alınmış; üniversite için kaynağı 118 değil.
- Öneri: üniversite "cómo solicitarla" sayfasını kaynak yap (116 yerine), "2026-2027 çağrısı için başvuru süresi 19 Mayıs'ta sona erdi" yaz; sonraki çağrı tarihi kaynakta yok, uydurma.

**4.2 ORTA, özet "bileşenleri" eşik koşulunu atlıyor.**
- Kart özet: "üniversiteye telafi edilen kayıt bursu, gelire göre en az 1.700 €, ... 2.700 €, 8 ve üzeri not için 50–125 € ve ... değişken tutar" (hepsi genel bileşen gibi).
- Kaynak: 1.700 € ve "en az" yalnız Umbral 1 ("Si tu renta familiar está en el umbral 1 o es inferior ... Como mínimo, recibirás 1.700 €"); Umbral 2'de 1.700 € yok; Umbral 3'te 2.700 € da yok, yalnız notlar için en çok 125 €; Umbral 3 üstünde hak yok. Cost alanı "gelir eşiği 1'de ve altında" diyor (doğru) ama özet ve altbaşlık eşiksiz.
- Öneri: özet cümlesine "gelir eşiği 1'de" koşulunu ekle ya da tutarları cost'a bırak.

**4.3 KÜÇÜK, note: "mühendislik ve fen bilimlerinde ... %65'ini geçmek gerekir".**
- Kaynak: "Ingenierías y arquitectura" ve "Ciencias" ayrı; "Aprobar, como mínimo, el 65 %" (en az %65'ini başarmak). Kartta mimarlık düştü ve "geçmek" "aşmak" gibi okunabilir; ayrıca önceki yıl aynı asgari krediye kayıt şartı yok (mühendislik/fen/sağlıkta var).
- Öneri: "en az %65'ini başarmış olmak" ve "mühendislik, mimarlık ve fen".

**4.4 KÜÇÜK (Türk okuyucu), "yalnız estancia izni yetmez" Türk öğrenci için ne anlama geldiğini söylemiyor.**
- Kaynak sade; kart "31 Aralık 2025 itibarıyla permiso de residencia" diyor. Öğrenim için gelenler tipik olarak estancia (öğrenci) iznindedir; kart bunu çıkarım olarak bırakıyor. Kaynakta "öğrenci estancia'sı" geçmez, o yüzden yazılmaz; yalnız ifade açık: "estancia izni (ör. kısa süreli kalış izni) yetmez" demek de kaynak dışı. Not niteliğinde, düzeltme zorunlu değil.

**4.5 KÜÇÜK, bölge farkı.** "Başvuru ... Bakanlığın şubesi" tüm İspanya için yazılmış; kaynak (MEC) kapsam sınırı (ör. bazı özerk bölgelerin kendi burs sistemi) vermiyor ve gaps.md bunu zaten "yok" diye not etmiş. Kartta "Bakanlık (MEC) bursu" çerçevesi var, hata yok; ancak "bölge bursları ayrı olabilir" diye çerçevelenmedi (Kural 1). Kaynaksız konu olduğu için yalnız not.

valid_until: IMV 2026-12-31 uygun. MEC null: kart 2026-2027 tutarlarını ve "31 Aralık 2025" tarihini sabitliyor; kaynak bitiş vermiyor, kural 11 gereği null kabul edilebilir.

## Özet tablo

| kart | ciddi | orta | küçük |
|---|---|---|---|
| egitim-sistemi-zorunlu-egitim-ve-okul-turleri | 0 | 1 | 1 |
| yabanci-lise-diplomasi-ile-universiteye-giris | 0 | 1 | 3 |
| ingreso-minimo-vital-ve-cocuk-destegi | 0 | 2 | 2 |
| mec-burslari-ab-disi-sart-ve-basvuru-donemi | 0 | 2 | 3 |
| TOPLAM | 0 | 6 | 9 |

## Bakılamayanlar
- UNEDasiss "Información país por país" ile Türkiye seçimi: sayfa ajax/ops.php'ye dayanıyor, oturum istiyor; Türkiye'ye özel içerik okunamadı. Yalnız genel "Otros países fuera de la UE" sayfası ve FAQ canlı doğrulandı.
- BOE 2026-2027 çağrı metni (convocatoria) ve RD 179/2026 açılmadı.
- Sede electrónica (IMV, MEC) formları açılmadı.
