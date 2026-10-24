# İspanya ulusal paketi, konu "ev": dar yeniden denetim (G2b), 2026-10-24

Kapsam: 6 kart (order 501-506), editör düzeltmesinden sonra. Kartlara ve depo dosyalarına dokunulmadı. Kaynaklar: es:kaynak:088 (BOE konsolide LAU, snapshot), 089 (INE IRAV), 090 (INCIBE); hepsi yerel metinden Python/grep ile tek tek okundu.
Sayım: ciddi 0, orta 2, küçük 11. Önceki denetimin 2 ciddi + 12 orta bulgusunun hepsi KAPANDI.

## Canlı kontrol (WebFetch/WebSearch)
- WebFetch: www.boe.es ve www.garrigues.com için 3 deneme `getaddrinfo ENOTFOUND` ile BAKILAMADI (BOE LAU canlı sayfası, RDL 29/2026 ve RDL 28/2026 BOE sayfaları açılamadı). Bu yüzden "Última actualización 07/10/2026" satırı canlıda yeniden doğrulanamadı; yalnız 24/10 tarihli yerel snapshot'a dayanıyor.
- WebSearch (ikincil kaynaklar, resmî değil): RDL 28/2026 (6 Ekim, BOE 7 Ekim, BOE-A-2026-20822) art. 10 LAU'daki örtülü yıllık uzamayı zorunlu uzamaya çeviriyor, yürürlük 15 Kasım 2026 (Garrigues); kiraya verenin yenilememesi için 6 ay ihbar ve tazminat öngörüyor (Garrigues özeti; art. 10'un kesin metni okunamadı, rakamlar RDL 27/2026 metninden geliyor, kesin sayılmamalı). RDL 28/2026 ve 29/2026 hâlâ onay (convalidación) bekliyor; Cortes feshedilmiş olduğundan karar Diputación Permanente'de. 18 Ekim tarihli bir rehber ikisinin de onay beklediğini yazıyor; oylama sonucu bulunamadı. RDL 26/2026 aynı içerikle 2 Ekim'de iptal edildi (snapshot'taki BOE notlarında da var).
- Sonuç: kartlar onay bekleyen RDL 29/2026'ya dayanan maddeler içeriyor (md. 2.3, 9.4, 9 bis, 11.2/11.3, 18.1, 21 bis, 36.5, 36.7; snapshot notlarından ölçüldü). Kartlar bunu "kararname olduğu için ileride değişebilir" diye işaretliyor (md. 18.1 hariç); "onay bekliyor" demiyor. valid_until 2026-11-05 altı kartta da var (valid_until.json okundu), yani onay süresinden (~6 Kasım) önce; bu tutarlı ve yeterli.

## Bölge farkı
Kartlar ulusal LAU kuralı verirken bölge farkı olan bir şeyi tüm İspanya için doğru gibi sunmuyor. Kart 2 (fianza depozito yükümlülüğü) ve kart 3 (gergin bölge ilanı) "bölgeye göre değişir" diyor. Yeni eklenen RDL 29/2026 hükümleri devlet kanunudur. Tek zayıflık: "bölgeye göre" ifadesi gergin bölge ilanının belediye/bölge bazlı olduğunu söylemiyor (küçük, aşağıda 3.b). Katalonya/Bask için kaynak dışı doğrulama yapılmadı.

## Kart 1: kira-sozlesmesi-suresi-ve-uzama
Editörün yeni cümleleri kaynakla karşılaştırıldı: md. 9.3 (gerçek kişi, birinci derece/evlat edinme, ayrılık/boşanma/iptal kararı hâlinde eş, ilk yıldan sonra, neden belirterek 2 ay) birebir; md. 2.3 geçici konut tanımı ve 9 bis (31 günden uzun, kural olarak 12 ay) birebir; "md. 2.3, 9.4, 9 bis RDL 29/2026" doğru. Kaynağı aşan cümle yok.
- 1.a KÜÇÜK (eksik): özet md. 9.3'ün sonucunu vermiyor. Kaynak: "Si transcurridos tres meses ... no hubieran procedido el arrendador o sus familiares ... a ocupar esta por sí, ... el arrendatario podrá optar ... entre ser repuesto en el uso y disfrute ... o ser indemnizado". Öneri: "Ev 3 ay içinde kullanılmazsa kiracı eve dönmeyi ya da tazminat istemeyi seçebilir" ekle.
- 1.b KÜÇÜK (eksik): "Geçici konut ... 12 ayı aşmaz" cümlesi md. 9 bis.2'yi atlıyor. Kaynak: "el primero se entenderá celebrado como un contrato de arrendamiento de vivienda habitual, ... incluido el plazo mínimo". Öneri: "12 ayı gerekçesiz aşan ya da üçüncü ardışık geçici sözleşme olursa ana konut sayılır" ekle.
- 1.c KÜÇÜK (güncellik): "ileride değişebilir" ifadesi onay bekleme durumunu ve RDL 26/2026'nın 2 Ekim'de iptal edildiğini söylemiyor. Öneri: "Meclis (Diputación Permanente) onayı bekleniyor" ekle.

## Kart 2: kira-depozitosu-fianza-ve-iade
md. 36.1, 36.2, 36.4, 36.5, 36.7 ve DA 3 ifadeleri kaynakla uyuşuyor; "iki aylık / geçici bir aylık" ve "aksi ispatlanmadıkça uygun durumda teslim" birebir.
- 2.a KÜÇÜK (ifade): "kira ödememe sigortası ya da benzeri bir teminat senden istenemez". Kaynak: "En ningún caso podrá exigirse al arrendatario la contratación de seguros de impago de renta u otras coberturas análogas." Aynı cümlede ek güvence serbest olduğundan "teminat" çelişkili okunur. Öneri: "benzeri bir sigorta/kapsam" yaz.
- 2.b KÜÇÜK (güncellik): 1.c ile aynı (md. 36.5 ve 36.7 onay bekleyen kararnameye bağlı).
- Önceki K.1 (Katalonya, "zorunluysa" yönlendirmesi): AÇIK ama küçük, kabul edilebilir; şehir sayfalarına bırakılmalı.

## Kart 3: kira-artisi-siniri-irav
INE cümlesi ("Los contratos de alquiler firmados con posterioridad al 26 de mayo de 2023 se revisarán en base al IRAV") ve md. 18.1/18.2 uyuşuyor. "bu kart bu sözleşmeler içindir" kaynağı aşmıyor, kapsamı daraltıyor (doğru).
- 3.a ORTA (güncellik): md. 18.1 snapshot notuna göre RDL 29/2026 art. 3.11 ile değişmiş ("Se modifica el apartado 1 por el art. 3.11 del Real Decreto-ley 29/2026"). Kart bu kararnameyi ve onay beklediğini hiç anmıyor (diğer kartların aksine). Önceki denetim "iptalde kart bozulmaz" demişti; ben md. 18.1'in kararname öncesi metnini okuyamadım, hangi cümlelerin (özellikle "endeks yazmıyorsa IRAV") yeni olduğu doğrulanamadı. Öneri: karta "güncelleme kuralı RDL 29/2026 ile değişti, onay bekliyor" notu ekle.
- 3.b KÜÇÜK (bölge): "ilanın olup olmadığı bölgeye göre değişir" belediye bazlı ilanı karşılamıyor (önceki K.2, AÇIK). Öneri: "belediye/bölge bazında ilan edilir".
- 3.c KÜÇÜK (ölçüm): INE metninde "Variación anual (%) / Índice / 2,54" tek değer var; sütun metinden kesin değil. IRAV oran olduğundan %2,54 yıllık değişim olarak makul ama kaynaktan teyit edilemiyor. Öneri: "INE tablosunda 2,54" diye yaz ya da canlı INE sayfasında sütunu doğrula. Canlı INE bu turda yeniden açılmadı.

## Kart 4: kirada-onarim-ve-hasar-sorumlulugu
md. 21.1, 21.3, 21.4 ve 21 bis ("cinco días hábiles", "descontando su importe ... renta del mes siguiente") kaynakla uyuşuyor; "5 iş günü", geçici konutta küçük onarımın ev sahibine ait olması doğru.
- 4.a KÜÇÜK (ifade): adım 6 "tutarı hemen ev sahibinden isteyebilir ya da ... ertesi ayın kirasından düşebilirsin". Kaynak: "exigiendo de inmediato su importe al arrendador o, en su defecto, previa justificación ..., descontando". "En su defecto" = ödenmezse; özet doğru yazmış, adım "ya da" ile eşdeğer seçenek gibi veriyor. Öneri: "ödemezse, gerekçeni bildirip düşebilirsin".
- 4.b KÜÇÜK (güncellik): 1.c ile aynı (md. 21 bis).
- Önceki 4.4 (md. 21.5, 15 gün usulü yazılmamış): AÇIK ama küçük ve güvenli.

## Kart 5: kiralik-evden-cikis-ve-ihbar-suresi
md. 11.1, 11.2, 9.1, 10.1 (kiracı 2 ay; "con un mes de antelación ... de cualquiera de las anualidades"), 36.4 kaynakla uyuşuyor. "Tazminat doğurmaz" cümlesi kaldırılmış.
- 5.a ORTA (güncellik): özet ve adım 3 md. 10.1'i (örtülü yıllık uzama, "yıllık uzamaların bitişinde 1 ay") güncel kural gibi veriyor. RDL 28/2026 bu rejimi 15 Kasım 2026'da değiştiriyor (ikincil kaynak: örtülü yıllık uzama yerine zorunlu uzama; kiraya veren için 6 ay ihbar). Kart bunu söylemiyor; valid_until 2026-11-05 onu örtse de metin sessiz. Öneri: "md. 10.1, 15 Kasım 2026'da RDL 28/2026 ile değişiyor (onay bekliyor)" notu ekle ya da 5 yıl sonrası cümleyi çıkar.
- 5.b KÜÇÜK (güncellik): md. 11 RDL 29/2026 art. 3.9 ile değişmiş; 1.c ile aynı eksik. Ek: kararname düşerse md. 11.1'deki eski tazminat şartı geri gelebilir; kart bunu iddia etmiyor (iyi), yalnız "onay bekliyor" yok.
- 5.c KÜÇÜK (ifade): altyazı "konut kiracısı ... altı ay ... 30 gün" geçici konutu anmıyor; özet ve adımlar anıyor.

## Kart 6: kiralik-ilan-dolandiriciligini-tanima
Tüm işaretler INCIBE metninde birebir: "precios muy bajos", "marcas de agua", "residen en el extranjero ... no pueden enseñarte el piso en persona", "intermediarios para la entrega de las llaves o el contrato", "Airbnb", "domino GRATUITO", "prisas", "MoneyGram o Western Union", "banco que no sea de la misma nacionalidad que el presunto propietario", "buscar la dirección del piso en Google". Peşin kira/fianza iddiası kaldırılmış. Yeni ya da kalan bulgu yok. Not satırı elektronik ödemeyi "dolandırıcılık ölçütü değildir" diye açıkça etiketliyor; LAU md. 17.3 alıntısı birebir. Bölge sorunu yok.

## Önceki denetim bulgularının durumu
| Bulgu | Durum |
|---|---|
| 5.1 CİDDİ (tazminat cümlesi, valid_until) | KAPANDI (cümle çıkarıldı, valid_until 2026-11-05; "onay bekliyor" notu eksik, 5.b) |
| 6.1 CİDDİ (peşin kira/fianza ölçütü) | KAPANDI |
| G.1 valid_until | KAPANDI (6 kartta 2026-11-05) |
| 1.1 geçici konut | KAPANDI |
| 1.2 md. 9.3 istisnası | KAPANDI (sonuç hükmü eksik, 1.a) |
| 2.1 ek güvence | KAPANDI |
| 2.2 çıkış belgesi/iade | KAPANDI |
| 3.1 ilk cümlede cevap | KAPANDI |
| 4.1 geçici konut onarım | KAPANDI |
| 4.2 "Medeni Kanun" | KAPANDI (İspanyol Código Civil) |
| 4.3 başlıkta hasar | KAPANDI (başlık daraltıldı) |
| 5.2 geçici konut çıkış | KAPANDI |
| 5.3 30 gün kapsamı | KAPANDI (ilk 5/7 yılla sınırlı, md. 10.1 eklendi) |
| 6.2 elektronik ödeme ölçüt | KAPANDI (ölçüt değil diye etiketli) |

## Bakılamayanlar
- www.boe.es ve garrigues.com WebFetch ile açılamadı (DNS hatası); BOE canlı LAU, RDL 28/2026 ve 29/2026 sayfaları okunamadı, 15 Kasım değişikliğinin kesin metni (md. 10 yeni hâli, tazminat rakamları) doğrulanamadı.
- RDL 28/2026 ve 29/2026 onay oylamasının sonucu bulunamadı.
- md. 18.1'in RDL 29/2026 öncesi metni okunamadı.
- INE canlı sayfası ve INCIBE canlı hâli bu turda açılmadı.

## Özet tablo
| kart | ciddi | orta | küçük | önceki bulgular durumu |
|---|---|---|---|---|
| kira-sozlesmesi-suresi-ve-uzama | 0 | 0 | 3 | 1.1, 1.2 KAPANDI |
| kira-depozitosu-fianza-ve-iade | 0 | 0 | 2 | 2.1, 2.2 KAPANDI; K.1 AÇIK (küçük) |
| kira-artisi-siniri-irav | 0 | 1 | 2 | 3.1 KAPANDI; K.2 AÇIK (küçük) |
| kirada-onarim-ve-hasar-sorumlulugu | 0 | 0 | 2 | 4.1-4.3 KAPANDI |
| kiralik-evden-cikis-ve-ihbar-suresi | 0 | 1 | 2 | 5.1 (ciddi), 5.2, 5.3 KAPANDI |
| kiralik-ilan-dolandiriciligini-tanima | 0 | 0 | 0 | 6.1 (ciddi), 6.2 KAPANDI |
| Toplam | 0 | 2 | 11 | G.1 KAPANDI |
