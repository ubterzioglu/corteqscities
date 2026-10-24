# Denetim b1 / Grup A (saglik, para x2, ev, is) - Endülüs bölge paketi

Yöntem: 5 kartın cümleleri kendi kaynak metinleriyle (kaynak_dizini) karşılaştırıldı; canlı kontrol: BOE Ley 5/2021 (md. 23), Junta ITP sayfası (polit-social), Junta IRPF 2025 sayfası, AVRA fianza sayfası, SAE kayıt sayfası (curl 200, 24.10.2026). Ley 5/2025 DA 6 için BOJA/BOE ilk metni doğrudan açılamadı (bakılamadı); yalnız AVRA sayfası ve web araması (BOJA 24.12.2025 yayını, yürürlük 24.01.2026) ile teyit edildi.

## saglik / endulus-saglik-karti-tarjeta-sanitaria-ve-aile-hekimi-secimi
Olgusal cümleler kaynakla uyumlu (45 gün, 3 ay, TSV 26.03.2026, belgeler, Cl@ve/e-DNI). Ulusal kartla çelişki yok.
- KÜÇÜK: documents "Başvuru sahibinin DNI'ı". Kaynak: "DNI del titular." Kaynak DNI diyor; DNI'ı olmayan yabancı (NIE/TIE) için kapsam açık değil. Öneri: "DNI (yabancıysa kaynak NIE/TIE'den söz etmiyor)" gibi eklemeden "kaynak yalnız DNI sayıyor" çerçevesi ya da gaps.md notu.
- KÜÇÜK: TSV'de "18 yaş altı için Cl@ve gerekir" atlanmış. Kaynak: "sí es necesario para menores de 18 años disponer del sistema Cl@ve." Öneri: note'a bir cümle.
- KÜÇÜK: Sağlık merkezinde "ilk kart çevrim içi alınamaz" doğru; ancak kaynak çevrim içi yenilemeyi (kayıp/çalıntı/hasarlı) anlatıyor, kart bunu vermiyor (eksik, kural ihlali değil).
Derece özeti: ciddi 0, orta 0, küçük 3.

## para / endulus-gelir-vergisi-irpf-bolge-dilimleri-ve-indirimleri
Dilimler canlı BOE md. 23 ile birebir (9,5/12/15/18,5/22,5; eşikler 13.000/21.100/35.200/60.000). Canlı BOE: md. 23 son güncelleme 21/09/2022, yürürlük 22/09/2022, etki 01/01/2022; sonradan değişiklik yok (31/12/2025 güncellemeleri 23 bis/diğer maddelerde). Gelir yılı (Renta 2025, 8 Nisan-30 Haziran 2026) Junta sayfasıyla uyumlu. valid_until 2026-12-31 makul.
- ORTA: note "Endülüs, gelir vergisi tahsilatının %50'sinin devredildiği bölgedir". Kaynak: "se encuentra cedido a las Comunidades Autónomas, el 50 % de su recaudación" (ortak rejimdeki tüm özerk bölgeler için genel kural; Endülüs'e özgü değil). Öneri: "gelir vergisi tahsilatının %50'si özerk bölgelere devredilmiştir; Endülüs de bunlardandır" diye yaz.
- KÜÇÜK: summary/subtitle "%9,5 ile %22,5 arası" tek başına toplam oran gibi okunabilir; "yalnız bölgesel pay" uyarısı yalnız note'ta. Öneri: summary'nin ilk cümlesine "devlet ölçeğine ek olarak" ekle.
- KÜÇÜK: steps 1 "dilimlerine göre yerleştir" kademeli (marjinal) uygulamayı belirtmiyor; kaynakta cuota íntegra sütunu var. Öneri: "her dilim yalnız kendi aralığındaki tutara uygulanır" (kaynak tablosu "Resto base liquidable" ile destekli).
- KÜÇÜK: kimin için geçerli (Endülüs'te ikamet) kartta yok; Türk okuyucu (vergi mukimi olmayan) için kapsam belirsiz. Kaynakta yok; gaps.md.
Derece özeti: ciddi 0, orta 1, küçük 3.

## para / endulus-ikinci-el-konut-alimi-itp-indirimli-oranlar
Canlı Junta sayfası kart sürümüyle aynı (6% / 3,5% / 150.000-250.000, 2026 listesi).
- ORTA: Başlık "ITP" ve "ikinci el" diyor; kartın tek kaynağı (es-an:kaynak:005, "Tipo reducido para promover una política social de vivienda") metninde "ITP", "Transmisiones Patrimoniales Onerosas" ve "segunda mano/usada" geçmiyor (grep: kaynak:005 ve canlı sayfada yalnız menüde "Impuestos sobre transmisiones patrimoniales" bağlantısı ve "Transmisiones realizadas en 2026"). Kaynak yalnız "adquirente/inmueble/vivienda habitual" diyor. ITP (TPO) adı BOE Ley 5/2021 önsözünde var ("para la modalidad de transmisiones patrimoniales onerosas se establece un tipo reducido del 6%") ama bu kartın kaynağı değil. "İkinci el" kaynakta hiçbir yerde yok. Öneri: başlığı kaynağın dilinde yaz ("konut alımında indirimli devir vergisi oranları") ya da 003'ü ikinci kaynak yapıp "TPO" claim'ini oradan al; "ikinci el"i çıkar.
- ORTA: subtitle/summary "%6 ve %3,5" ve note "indirimli oranın dışındaki alımlar için oran bu kaynakta yoktur" kapsamı eksik: aynı kaynakta Decreto-ley 1/26 (borrasca hasarı) için "0% a las transmisiones de inmuebles destinados a constituir la vivienda habitual ... que sustituya a otra ..." ve 3,5% (konut dışı) var; kart bunları sessizce atlıyor. Öneri: bir cümleyle bu istisnayı (belirli hasar bölgesi için %0) ekle ya da "bu kart bu istisnayı kapsamıyor" yerine kapsamı kapat.
- KÜÇÜK: summary "%3,5 oranı üç durumda geçerlidir" ama ardından beş koşul sayılıyor (35 yaş altı, mağdur, belediye; engelli; büyük aile). Kaynakta üç madde (3,5%) var, yaş/mağdur/belediye tek madde. Öneri: "üç ayrı maddede" ya da "şu koşullardan biri".
- KÜÇÜK: genel oran (%7, Ley 5/2021 önsözü) kartta yok; ama kaynak 005'te de yok; kural ihlali değil.
Derece özeti: ciddi 0, orta 2, küçük 2.

## ev / endulus-kira-depozitosu-fianza-avra-yatirma-zorunlulugu
24.01.2026 rejimi canlı AVRA sayfasıyla birebir: "Fecha: 24/01/2026 inclusive", "se mantiene la obligación ... hasta el 23/01/2026, inclusive", DA Sexta Ley 5/2025, iade "conforme dichos contratos se vayan extinguiendo y a solicitud", "un mes". Web araması: DA 6, BOJA 24.12.2025, yürürlük 24.01.2026 (kaynak: legaltoday, economistjurist; BOE/BOJA birincil metni doğrudan açılamadı, bakılamadı). Ulusal kartla çelişki yok (ulusal kart depozitonun kendisini anlatıyor).
- KÜÇÜK: Kart "yatırma zorunluluğu yok" diyor; depozitonun kiraya verene ödenmesi zorunluluğu kalkmadı ama bu kartta ve kaynakta söylenmiyor, okuyucu "depozito yok" diye anlayabilir. Öneri: summary'ye "depozito kiraya verene ödenmeye devam eder, yalnız AVRA'ya yatırma kalktı" ancak bu kaynakta yoksa yalnız "AVRA'ya yatırma zorunluluğu" ifadesini sıkı tut (şu an zaten sıkı; sadece risk notu).
- Bölge: kart Endülüs'e sınırlı, doğru. valid_until null uygun (rejim süresiz).
Derece özeti: ciddi 0, orta 0, küçük 1.

## is / endulus-sae-is-arayan-kaydi-demandante-de-empleo
Kayıt adımları, Cl@ve/dijital sertifika ve randevu telefonu (955 625 695, 8-20, pazartesi-cuma) kaynakla uyumlu. Canlı SAE sayfası hâlâ "06/03/2025".
- "Türk vatandaşı ... bu izin şartı sana uygulanır" çıkarımı: kaynak 007 "nacional de algún país miembro de la UE, o ... personas extranjeras no comunitarias, contar con una autorización administrativa"; Türkiye AB üyesi değil, mantık doğru. Ama kaynakta "Türk" yok; sonuç doğru fakat kaynağı aşan açık ifade. Ayrıca "AEA/İsviçre" ve AB vatandaşı aile üyesi istisnaları kaynakta yok.
- ORTA: note "AB dışı vatandaş için sıra: önce çalışma izni (Ministerio de Inclusión ... başvurulur), izin alındıktan sonra SAE'ye demanda" genel kural gibi. Kaynak 008 bunu "yurt dışından gelip çalışmak isteyen" için söylüyor ("necesitan obtener un visado antes de viajar"; "Una vez que dispongas de la autorización administrativa, puedes acceder ... demanda"). Kaynak 007 ise yalnız "inscripción'a izin veren autorización administrativa" diyor (çalışma izni olması şart olmayabilir; ör. başka türden izin). Öneri: "çalışma izni" yerine kaynak 007'deki "kayda izin veren idari izin" ifadesini kullan; 008'i sadece yurt dışından gelenler için bağla.
- KÜÇÜK: note "Hangi iş bürosuna bağlandığın oturduğun yere göre değişir" kaynakta yok. Öneri: sil.
- KÜÇÜK: Uyruk koşulu AB içi ise kart "AB üyesi ülke vatandaşı" der, AEA/İsviçre kapsamı kaynakta yok; sorun değil, yalnız eksik.
Derece özeti: ciddi 0, orta 1, küçük 2.

## Özet tablo
| kart | ciddi | orta | küçük |
|---|---|---|---|
| saglik / aile hekimi | 0 | 0 | 3 |
| para / IRPF dilimleri | 0 | 1 | 3 |
| para / ITP indirimli oranlar | 0 | 2 | 2 |
| ev / fianza AVRA | 0 | 0 | 1 |
| is / SAE | 0 | 1 | 2 |
| TOPLAM | 0 | 4 | 11 |

Bakılamayanlar: Ley 5/2025 DA 6'nın BOJA/BOE birincil metni (yalnız AVRA sayfası + web araması); WebFetch kullanılmadı.
