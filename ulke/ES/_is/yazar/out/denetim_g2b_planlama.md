# ES ulusal paketi, "planlama" (8 kart): dar denetim, editör düzeltmesinden sonra (G2b)

Denetçi: bağımsız; kartları yazan ya da düzelten değil. Tarih: 2026-10-24. Kartlara ve depo dosyalarına dokunulmadı.
Yöntem: editörün eklediği/değiştirdiği her cümle, kartın kendi source_ids kaynak metniyle (snap_*/…txt) karşılaştırıldı. İlk denetimdeki (denetim_g2_planlama.md) ciddi/orta bulgular tek tek izlendi.
Derece: ciddi = yanlış/yanıltıcı; orta = eksik/kapsam hatası/eski; küçük = ifade/kural ihlali.

Özel soru (nakit eşiği): KAPANDI. Kart 4 özet, altbaşlık ve adım 1 "10.000 euro ya da üzeri / ve üzeri" yazıyor. Kaynak es:kaynak:102: "Se debe declarar toda cantidad igual o superior a 10.000€ o su contravalor en cualquier divisa por persona y viaje." Beyan "girişten önce" ve yazılıdır; kart bunu söylüyor, "sözlü beyan/kırmızı kanal" cümleleri kalkmış. Kaynak değişimi (101 yerine 102) kart başına 2 kaynak sınırına uyuyor.

---------------------------------------------------------------------
## Kart 1: tasinma-oncesi-vize-ve-ilk-oturum-izni (es:kaynak:040)
Editör cümleleri kaynakta karşılığıyla doğrulandı:
- "konsolosluk bölgesinde oturanlar için": kaynak "Esta Oficina Consular es competente para admitir las solicitudes de visado de las personas que residan en la demarcación consular."
- "BLS için ayrıca hizmet bedeli ödenir": "con cita previa… se deberá pagar la tasa por servicios prestados."
- "genelde şahsen (gerekçeli ve konsolosluğun uygun gördüğü istisnalarda temsilci)": "La presentación por representante podrá hacerse de forma excepcional, siempre que sea justificada y valorada por la Oficina Consular."
- Başlıktaki "çalışmayı içermeyen": kaynak başlığı "Visado de residencia no lucrativa".
Yeni bulgu: yok. Kaynağı aşan cümle yok.
Önceki bulgular: orta #1 (bölge kapsamı) KAPANDI. Küçük #2 başlık, #3 "şahsen", #4 BLS bedeli: KAPANDI.

## Kart 2: oturum-vizesi-basvurusunda-getirilecek-belgeler (es:kaynak:040)
Doğrulandı: apostil/çeviri, EX-01, pasaport 1 yıl + 2 boş sayfa + 10 yıl kuralı, sabıka (ceza ehliyeti yaşı, son 5 yıl), tıbbi rapor (2005 Uluslararası Sağlık Tüzüğü), modelo 790 kod 052 başlık 2.1, iki nüsha, internetten ödeme ("Esta tasa también se puede abonar por internet"), aile üyesi için ayrı set ("Para cada familiar será necesario presentar").
Bulgular:
1. ORTA, AÇIK. Kart: "asgari tutar IPREM'in %400'üne eşittir ve … her aile üyesi için IPREM'in %100'ü eklenir." Kaynak: "La cantidad mínima exigida equivale al 400% del IPREM. A esta cantidad hay que añadir el 100% el IPREM por cada familiar a cargo del solicitante." Kaynak tutar vermiyor; kartta IPREM açıklanmıyor ve euro tutarı yok, okuyucu eyleme geçemez (editör bunu gaps.md'ye "resmî IPREM kaynağı eklenirse" diye yazmış, kapatmamış). Öneri: ikinci kaynak olarak resmî IPREM (BOE/Ministerio) ekle ya da karta "IPREM: İspanya'nın her yıl belirlenen gösterge geliri; güncel tutarı için resmî sayfaya bak" yaz (tutarı kaynaksız yazma).
Önceki bulgular: orta #1 (IPREM) AÇIK; orta #2 (bölge kapsamı) KAPANDI (başlık dışında altbaşlık, özet, belge satırı "İstanbul konsolosluk bölgesinde ikamet kanıtı"). Küçük #3-#5 KAPANDI.

## Kart 3: ilk-gunlerde-nuss-ve-temel-odeme-hesabi (es:kaynak:107; es:kaynak:058)
Doğrulandı: "istediğin zaman" (kaynak: "Puedes solicitar el Número de la Seguridad Social en cualquier momento"), DNI/NIE + telefon + e-posta + domicilio habitual, Cl@ve yoksa iki yüz + selfie (reşit ya da emancipe küçük), küçük için anne/baba/vasi, Seguro Escolar, sağlık kartı, temel ödeme hesabı kapsamı (AB'de yasal ikamet, sabit adres şart değil, sığınmacı, sınır dışı edilemeyen) ve 3 ret gerekçesi.
Bulgular:
1. KÜÇÜK. Slug "ilk-gunlerde-…" kaldı; kaynak yalnız "en cualquier momento" diyor (gaps.md bunu bilerek bırakıldığını yazıyor). Öneri: slug "nuss-ve-temel-odeme-hesabi".
2. KÜÇÜK. Adım 2 ve belge satırı "DNI ya da NIE" diyor; Türk okuyucu için DNI (İspanyol vatandaşı belgesi) geçerli değil, NIE gerekir ve kart NIE'nin önce alınması gerektiğini söylemiyor. Kaynak: "Tus datos identificativos (DNI o NIE)." Öneri: "NIE'n olduktan sonra" ekle.
3. KÜÇÜK. Banka kısmı "AB'de yasal olarak oturuyorsan" diyor; ölçütün uyruk değil yasal ikamet olduğu yazılı değil (kaynak: "Residan legalmente en la Unión Europea"). Türk okuyucu "AB vatandaşı olmam gerek" diye okuyabilir. Öneri: "uyruk önemli değil, AB'de yasal ikamet yeter" de.
Önceki bulgular (hepsi küçüktü): #1 slug AÇIK (başlıktaki "vardığında" kalktı: KISMEN); #2 NIE AÇIK; #3 "bankalar" KAPANDI (altbaşlık "kredi kuruluşları"); #4 uyruk AÇIK; #5 reşit kapsamı KAPANDI (adım 3 ve not); documents etiketi KAPANDI ("NUSS başvurusu için:").

## Kart 4: ab-disindan-gelirken-esya-ve-nakit-gumruk-beyani (es:kaynak:102; es:kaynak:104)
Editörün eklediği her cümle kaynakta aranıp doğrulandı:
- Eşik/beyan: "igual o superior a 10.000 euros o su contravalor en moneda extranjera"; "por persona y viaje"; "las transferencias bancarias no son objeto de declaración"; yazılı: "Puede realizarse en papel impreso o por medios electrónicos"; E1: "deberá presentarse el modelo E1" (üçüncü ülke, eşlikli); tek hareket: "La declaración presentada será válida para realizar un único movimiento… en la fecha declarada"; gösterme: "será exhibida sin previo requerimiento ante los Servicios de Aduanas"; ceza: "infracción grave. La sanción mínima es de 600 euros… hasta el 50 por ciento".
- Ev eşyası: 12 ay / niyet / 6 ay sahiplik / aynı kullanım / DUA'da talep / 12 ay devir yasağı / dışlananlar / IGIC / taahhüt+teminat istisnası ("mediante el compromiso de establecerse efectivamente en él en un plazo de seis meses… acompañado de una garantía") / belgeler ("cualquier medio de prueba… en algunos casos podrá ser necesario aportar varios", "Justificante del domicilio fiscal") / TIE: "solicitud o tarjeta de identificación de extranjero (TIE)" üçüncü ülke vatandaşları için.
- Sayfa tarihleri 102: 2026-09-23, 104: 2026-05-12 (HTML "Página actualizada"), kartta doğru.
- Türk vatandaşı: TIE satırı AB/AEA dışı uyruklar için doğru yazılmış; AB vatandaşı kuralı uygulanır gibi cümle yok.
Bulgular:
1. KÜÇÜK. Kart "gümrükte" diyor ama yolcu bagajı rejimi (430/300/150 € muafiyeti, tütün/alkol sınırları, kırmızı/yeşil kanal) karttan çıkarılmış (gaps.md: ayrı kart önerilmiş). Okuyucu "başka bir şey beyan etmem gerekmez" sanabilir. Öneri: nota "Bagajdaki ticari olmayan mallar için ayrı yolcu muafiyet kuralları var; bu kart onları anlatmaz" (kaynaksız tutar yazma) ya da ayrı kart aç.
Önceki bulgular: ciddi #1 (eşik "fazla") KAPANDI; ciddi #2 (sözlü beyan, ön beyan yok) KAPANDI; orta #3 (tütün/alkol) KAPANDI (içerik karttan çıkarıldı, yanlış cümle kalmadı); orta #4 (12 ay istisnası) KAPANDI; küçük #5 (şartlar) KAPANDI ("başlıca şartlar" + aynı kullanım); #6 (belge örneği) KAPANDI; #7 (bölge) KISMEN (IGIC notu var, Ceuta/Melilla/Kanarya nakit rejimi yazılmadı, gaps.md'de kayıtlı).

## Kart 5: ab-disindan-evcil-hayvanla-ispanyaya-giris (es:kaynak:105)
Doğrulandı: mikroçip/dövme (3 Temmuz 2011), geçerli kuduz aşısı, Ek II dışı ülke için serolojik test, zoosanitario + beyan, "documento del laboratorio autorizado por la UE", Resguardo Fiscal, yetkili giriş noktası, 15 hafta açıklaması, 5 hayvan, karantina/iade/ötanazi, tarih 2026-09-23.
Bulgular:
1. ORTA. Kaynağı aşan kapsam taşıması. Altbaşlık, adım 4 ve notta "0,5 UI/ml, kan örneğinden 3 ay sonra giriş, en az 7 ay" kuralı doğrudan AB dışından ilk giriş kuralı gibi yazılı. Kaynakta bu üç cümle "¿Qué requisitos debe cumplir mi mascota al regreso a España de una estancia en un país tercero?" başlığı altında: "Si vas a viajar a un país no incluido en el anexo II (país con riesgo de rabia)… deberá ser igual o superior a 0.5 UI/ml. La entrada del animal sólo estará autorizada pasados 3 meses desde la fecha de extracción de la muestra de sangre… la edad mínima de un animal que proceda de un país con riesgo de rabia será de 7 meses." Yalnız özet bunu ("sayfa bu koşulları İspanya'ya dönüş bölümünde veriyor") açıkça belirtiyor; altbaşlık, adımlar ve not belirtmiyor. Başka sayfa bu kuralı ilk giriş için doğrulamıyor. Öneri: altbaşlık, adım 4 ve nottan dönüş-bölümü uyarısını çıkarma; ya "sayfa bu koşulları dönüş bölümünde veriyor" notunu adıma da ekle ya da MAPA/AB Tüzüğü 576/2013'ten ikinci kaynak al.
2. ORTA (güncellik, doğrulanamadı). Kart Reglamento (UE) 577/2013 Ek II'ye dayanıyor; keşif notu (kesif/planlama/selected.jsonl) MAPA sayfasının "2026/636" sayılı daha yeni bir düzenlemeye atıf yaptığını yazıyor, gaps.md de bunu kabul ediyor. Ek II'nin hâlâ yürürlükte olup olmadığı ve Türkiye'nin listede olup olmadığı bu denetimde kontrol edilemedi (aşağıda "Bakılamayanlar"). Öneri: güncel Tüzüğü doğrulayana kadar kartta "AEAT sayfası 577/2013 Ek II'ye atıf yapıyor; daha yeni düzenleme için MAPA'ya bak" uyarısı bırak ve valid_until doldur.
Önceki bulgular: orta #1 (serolojik test eşiği/bekleme/yaş) KISMEN (eklendi, ama yukarıdaki bulgu 1: kapsam uyarısı özette var, diğer alanlarda yok); küçük #2 (liste belirsiz) KAPANDI ("577/2013 Ek II" yazıldı); küçük #3 (resmî veteriner) KAPANDI.

## Kart 6: oturum-ve-ogrenci-vizesinde-saglik-sigortasi-sarti (es:kaynak:040; es:kaynak:106)
Doğrulandı: oturum vizesi sigortası ("público o privado… entidad aseguradora autorizada a operar en España… cubrir todos los riesgos asegurados por el sistema público de salud"), öğrenci vizesi ("prestaciones similares las concedidas por la cartera común básica de servicios asistenciales del Sistema Nacional de Salud, válido para la duración de la estancia prevista"), orijinal + kopya, konsolosluk bölgesi kapsamı.
Yeni bulgu: yok.
Önceki bulgular (küçük): #1 "farklıdır" karşılaştırması KAPANDI (altbaşlık artık yalnız öğrenci vizesinde ek şart diyor); #2 bölge kapsamı KAPANDI.

## Kart 7: ispanya-para-birimi-euro-ve-resmi-dil (es:kaynak:110; es:kaynak:108)
Doğrulandı: "Todas ellas son de curso legal en todos los países de la eurozona"; FNMT-RCM basar, Banco de España "pone en circulación y retira"; Anayasa m.3 (castellano resmî; diğer diller Statülere göre özerk bölgelerde resmî).
Bulgular:
1. KÜÇÜK. Başlık "para birimi … nedir?" diyor; kart "İspanya'nın para birimi euro" cümlesini yazmıyor (kaynakta da yok) ve euro banknotlar kartta/kaynakta yok. Okuyucu doğrudan cevap bulamıyor. Öneri: kaynaklı ifadeyle "İspanya eurobölgesindedir; euro madeni paralar eurobölgesinde yasal ödeme aracıdır" yaz ya da BdE banknot sayfasını ekleyip kartı bölmeden önce başlığı daralt ("Euro madeni paralar ve resmî dil").
Önceki bulgular (küçük): #1 "para birimi euro" kaynaksız cümle KAPANDI (iddia kaldırıldı); #2 altbaşlık cevap değil KISMEN (bulgu 1).

## Kart 8: ispanya-resmi-saat-ve-yaz-saati-kurali (es:kaynak:109)
Doğrulandı (RD 236/2002 m.2 ve m.3, gerekçe bölümü): son Mart pazarı 02:00 (Kanarya 01:00), 60 dk ileri, 23 saat; son Ekim pazarı 03:00 (Kanarya 02:00), 60 dk geri, 25 saat; "dos horas oficiales… Península y archipiélago balear / canario"; "el cambio horario se efectuará en el mismo instante en todo el territorio nacional". Kartın "aynı anda" cümleleri (özet ve adım 3) kaynaktan.
Bulgular:
1. KÜÇÜK. Ceuta/Melilla saati ve bu yılın bitiş tarihi (25 Ekim 2026) yazılmadı; kaynak Ceuta/Melilla'yı anmıyor. 2026 tarihi için Orden PCM/186/2022 okunmadı (gaps.md'de kayıtlı). Zaman duyarlı kartta valid_until null; kural yıllık olduğundan kabul edilebilir ama canlı doğrulama yapılamadı (aşağıda).
Önceki bulgular (küçük): #1 Kanarya "aynı an" KAPANDI (kaynakta Kanarya'nın kaç saat geride olduğu yok, yazılmaması doğru); #2 Ceuta/Melilla AÇIK (gaps.md'de kayıtlı); #3 2026 tarihi AÇIK (gaps.md'de kayıtlı).

---------------------------------------------------------------------
## Türk vatandaşına uygulanmayan kural uygulanır gibi gösterilen cümle (görev 4)
Net bir cümle yok. Kart 4 TIE satırı ("AB ve AEA dışı uyruklular için") doğru ayrılmış; kart 3 banka hakkı "AB'de yasal oturanlar" ölçütüyle yazılı (uyruk değil). Yalnız kart 3'te "DNI ya da NIE" (küçük bulgu 2) Türk için DNI'yi seçenek gibi gösteriyor.

## Bakılamayanlar (canlı kontrol)
Bu oturumda tüm canlı sayfalar açılamadı: WebFetch "getaddrinfo ENOTFOUND" (eur-lex.europa.eu, sede.agenciatributaria.gob.es, www.mapa.gob.es, www.boe.es, www.exteriores.gob.es); Bash/curl ile de proxy "CONNECT tunnel failed, response 403". Sertifika doğrulaması kapatılmadı, başka yol denenmedi. Dolayısıyla şunlar bakılamadı:
- Kart 4: nakit eşiği ve ev eşyası şartlarının canlı AEAT sayfalarında bugün aynı olduğu (yalnız 24 Ekim 2026 öncesi alınan kaynak kopyaları ve HTML "Página actualizada" tarihleri okundu).
- Kart 5: Reglamento 577/2013 Ek II'nin güncelliği, "2026/636" düzenlemesi, Türkiye'nin listede olup olmadığı, 0,5 UI/ml + 3 ay + 7 ay kuralının ilk giriş için geçerliliği.
- Kart 8: RD 236/2002'nin bugün yürürlükte olduğu ve AB'de yaz saati uygulamasının kaldırılmadığı.
- Kart 1, 2, 6: İstanbul Başkonsolosluğu sayfalarının bugünkü hâli (365 gün, IPREM %400, sigorta); IPREM'in 2026 tutarı.
Yapılan canlı kontrol sayısı: 0 başarılı (6 deneme, hepsi ağ hatası).

## Özet tablo
| Kart | Ciddi | Orta | Küçük | Önceki bulgular durumu |
|---|---|---|---|---|
| 1 vize ve ilk oturum izni | 0 | 0 | 0 | orta #1 KAPANDI; küçük #2-#4 KAPANDI |
| 2 belgeler | 0 | 1 | 0 | orta #1 IPREM AÇIK; orta #2 KAPANDI; küçük #3-#5 KAPANDI |
| 3 NUSS ve hesap | 0 | 0 | 3 | küçük #1 KISMEN, #2 AÇIK, #3 KAPANDI, #4 AÇIK, #5 KAPANDI |
| 4 gümrük | 0 | 0 | 1 | ciddi #1, #2 KAPANDI; orta #3, #4 KAPANDI; küçük #5, #6 KAPANDI, #7 KISMEN |
| 5 evcil hayvan | 0 | 2 | 0 | orta #1 KISMEN; küçük #2, #3 KAPANDI |
| 6 sağlık sigortası | 0 | 0 | 0 | küçük #1, #2 KAPANDI |
| 7 euro ve resmî dil | 0 | 0 | 1 | küçük #1 KAPANDI, #2 KISMEN |
| 8 resmî saat | 0 | 0 | 1 | küçük #1 KAPANDI, #2, #3 AÇIK |
| Toplam | 0 | 3 | 6 | İlk denetimdeki 2 ciddi ve 6 orta bulgudan: 2 ciddi KAPANDI; 4 orta KAPANDI, 1 orta AÇIK (K2 IPREM), 1 orta KISMEN (K5 serolojik test) |
