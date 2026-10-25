# Almanya ulusal paketi, grup 1 (para, is, fatura): editör sonrası DAR bağımsız denetim (g1b)

Tarih: 25.10.2026. Denetçi kartları yazmadı, editör değildi; kart dosyalarına dokunulmadı. Yazarın gaps.md dosyası yalnız kaynak sınırını anlamak için, ilgili yerde okundu.

## Özet
- Kart: 32 (para 12, is 11, fatura 9). Ciddi 0, orta 6, küçük 19. Orta 6'dan biri grup dışı ev/704 kartında (konular arası tutarlılık bulgusu).
- İlk raporların 1 ciddi + 44 orta bulgusundan 1 ciddi + 41 orta tam kapandı, 3 orta kısmen kapandı (para/maas, is/isten-cikarma, is/burgergeld). Açık ciddi yok. Editörün düzeltmesinden doğan yeni hatalar ayrı bulgu olarak aşağıda (kdv, isten-cikarma, burgergeld, is-sozlesmesi).
- Yöntem: (1) 32 kartın güncel hali ile editör öncesi yedek alan alan karşılaştırıldı (title, subtitle, summary, steps, documents, timing, cost, note, source_ids, claims); değişen ya da eklenen her cümle kartın kendi kaynak metniyle (kaynak_dizini -> text_file) okundu. (2) Tüm claim quote'ları kaynak metinde arandı (yumuşak tire U+00AD silinerek): biri hariç hepsi var (is/isten-cikarma claim 25: yalnız büyük/küçük harf, "hat" / kaynakta "Hat"). (3) Editörün yeni ya da değiştirdiği 186 claim'in (para 53, is 63, fatura 70) quote'u canlı sayfalarda tek tek arandı. (4) Kart başına kaynak sayısı (en çok 2), Bağlantılar'ın kart kaynaklarından gelmesi, şehir adı ve "yaklaşık / teyit / sayfasında / burada / bölge paketi" taraması script ile yapıldı: sorun çıkmadı (tek istisna: is/bordro "bu karttaki tutarlar", küçük, editör değişikliği değil).
- Canlı açılan sayfalar (Python urllib): gesetze-im-internet.de EStG §38b, AO §149 ve §138, UStG §12 ve §19, SGB II §7, SGB III §153, SGB V §47, SGB VI (tam metin), NachwG §2, TzBfG §14, BUrlG, ArbZG, GewO §108, EntgFG, KSchG, StromGVV §2, EnWG §20a, §40b, §41, §41f, §41g, BGB §556, HeizkostenV §7, BetrKV §2, TKG §58, §59, §60; BaFin (Basiskonto, Kontenwechsel); Bundesbank (SEPA, Empfängerüberprüfung); elster.de help_est_ufa_10_2025 (help_est_ufa_10_2026: sayfa yok, 66 karakter); bundesregierung.de (Mindestlohn, neue-grundsicherung); arbeitsagentur.de ALG; minijob-zentrale.de; anerkennung-in-deutschland.de; rundfunkbeitrag.de (zahlung, empfaenger-von-sozialleistungen); bundesnetzagentur.de (Wechsel, Internetgeschwindigkeit); deutsche-rentenversicherung.de (Türkei). Sonuç: editörün yazdığı hiçbir cümle canlı metinle çelişmiyor. Script'in "LIVE-MISS" dediği 9 claim'in hepsi HTML boşluk/noktalama farkı çıktı; tek tek canlı sayfada açılıp doğrulandı.
- Denenmeyenler: bmi.bund.de, make-it-in-germany.com, auswaertiges-amt.de (kapalı/ince).

## İlk bulgular kapanış tablosu
K = kapandı, KS = kısmen kapandı, A = açık. "Yeni" = düzeltmenin getirdiği ayrı bulgu (aşağıda).

### para (1 ciddi + 15 orta)
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| almanya-emeklilik-yasi... | CİDDİ 67 yaş genellemesi | K | Başlık, subtitle, summary, timing, steps doğum yılına göre. Tablo SGB VI §235 ile birebir: 1957=65y11a, 1958=66y0a, 1959=66y2a, 1960=66y4a, 1961=66y6a, 1962=66y8a, 1963=66y10a (kaynak 203: "1957 11 65 11 1958 12 66 0 … 1963 22 66 10"). |
| almanya-emeklilik-yasi... | orta bekleme süresi 5 yıl yok | K | Summary/timing "genel bekleme süresi 5 yıl (SGB VI §50)"; claim 28 quote kaynak 203'te var. |
| basiskonto | orta ret nedenleri sayılmamış | K | Summary'de 4 neden, BaFin ile aynı; claim 20-23. (Yeni küçük: yazım hatası.) |
| basiskonto | orta "kimlik" tek başına | K | "fotoğraflı resmî … pasaport ve kimlik zorunluluğunu karşılayan" = BaFin cümlesi. |
| iban-sepa | orta Lastschrift ters çeviri | K | "alacaklının, senin hesabından senin onayınla çektiği tahsilat". |
| iban-sepa | orta 8 hafta / 13 ay | K | Note'ta; kaynak 026 quote'ları var. |
| iban-sepa | orta Türkiye SEPA dışı | K | Liste ve "Türkiye SEPA ülkeleri arasında sayılmaz" kaynak listesinden; "Auslandsüberweisung" yalnız "başka para birimi için" kuralına bağlı, uydurma yok. |
| gelir-vergisi | orta %42/%45 formül katsayısı | K | "formülde 0,42 / 0,45 katsayısı"; EStG §32a canlı ile uyumlu. |
| vergi-sinifi | orta "eşi maaş almıyorsa IV" koşulu | K | "ve III için ortak başvuru yapılmamışsa" (EStG §38b Abs.1 Nr.4 ile aynı). |
| yillik-vergi-beyannamesi | orta danışmanlı beyanda süre | K | AO §149 Abs.3 Şubat sonu eklendi; canlı ve kopya aynı. (Örnek tarih kısmı için bkz. yeni orta.) |
| yillik-vergi-beyannamesi | orta "gecikme zammı" çeviri | K | "geç beyan zammı (Verspätungszuschlag)". |
| yillik-vergi-beyannamesi | orta başlık genel soru | K | Başlık/subtitle/summary "maaşlı çalışan"; maaş almayanlar, sermaye geliri, Verlustvortrag cümleleri ELSTER canlı metniyle aynı. |
| kdv | orta günlük kalemler yok | K (yeni orta var) | Nr. 1, 7, 10, 11, 15 eklendi; Nr. 10 cümlesi yanlış kapsamlı. |
| kilise-vergisi | orta "oran/çıkış eyalete göre" kaynaksız | K | Silindi; yerine WRV 137/6, 137/8, EStG §51a Abs.2b (claim 1, 2, 5) ile birebir. Eyalet adı/rakamı yok. |
| maas-sosyal-sigorta | orta Pflegeversicherung eksik | KS | Başlık "emeklilik, işsizlik ve sağlık"a daraltıldı (denetçinin alternatifi); bakım sigortasının ayrıca kesildiği yazılmadı (küçük bulgu). |
| zorunlu-arac-sigortasi | orta başlık genel soru | K | Başlık Kfz-Haftpflicht + Privathaftpflicht'a daraltıldı; subtitle "zorunludur / zorunlu değildir" cevaplıyor. |

### is (17 orta)
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| is-sozlesmesi | orta önceki iş ilişkisi mutlak, takvim tarihli, istisnalar | K (yeni orta var) | "takvim tarihli", Tarifvertrag, 4 yıl, 5 yıl, BVerfG 6.6.2018 eklendi; TzBfG §14 ile uyumlu. |
| is-sozlesmesi | orta "haklı sebep" çeviri | K | "nesnel gerekçe (sachlicher Grund)" her yerde. |
| asgari-ucret | orta istisna listesi kapalı | K | "Örneğin …", claim 3 tam cümle; valid_until 2027-12-31. |
| calisma-suresi | orta 24 iş günü | K | "24 Werktag (Pazar ve yasal tatil dışındaki tüm günler, Cumartesi dahil)" = BUrlG §3. |
| calisma-suresi | orta Teilurlaub koşulları | K | timing §5/1 a-c; claim 18-20 ayrı quote. |
| calisma-suresi | orta ArbZG §18 / §7 | K | Summary + note + claim 22-24. |
| hastalik-bildirimi | orta GKV için §5/1a | K | Summary, adım 2-3 ayrıldı; EntgFG §5/1a ile aynı. |
| hastalik-bildirimi | orta Krankengeld üst sınır; sıra | K | "prim üst sınırına kadar … %70"; başlık "tutarı nasıl belirlenir". SGB V §47 canlı aynı. |
| hastalik-bildirimi | orta "tam ücret" | K | cost "normal çalışma süresine göre (fazla mesai hariç)"; EntgFG §4. |
| isten-cikarma | orta tazminat tavanı 12 ay | K | 15 ve 18 ay, yaş ve süre koşullarıyla; KSchG §10/2. |
| isten-cikarma | orta küçük işyeri sayımı | KS | Çıraklar, 0,5/0,75 doğru; "on çalışan" cümlesi yanlış kapsamda (yeni orta). |
| issizlik-parasi | (orta yok; küçükler) | K | 12 ay tabanı, 5 yıl çerçevesi, Türk cümlesi, "aksi bir beyanın yoksa". SGB III §153 canlı: Pauschale %20 (BA sayfasıyla aynı). |
| burgergeld | orta kimin alabileceği yok | KS | SGB II §7 (kaynak 120) eklendi; 5 yıl istisnasının kapsamı belirsiz (yeni orta). |
| burgergeld | orta eski ad/563 Euro açıkta | K | 563 Euro ve 2 claim silindi, karta tutar kalmadı. |
| serbest-calisma | orta Finanzamt "isterse" | K | "bildirimle birlikte … iletmek zorundasın; zor durum başvurusuyla vazgeçilebilir" (AO §138 canlı aynı). |
| serbest-calisma | orta Türk okuyucu oturum izni | K (kapsam daraltma) | Başlık "vergi açısından"; kaynak olmadığı için bilgi eklenmemiş (doğru). |
| minijob-midijob | orta hane Minijob %13,6 | K | Gewerbe %3,6, özel hane %13,6; claim 22 tam cümle, canlı aynı. |
| yabanci-diploma | orta ZAB ön koşulları | K | anabin'de kayıt yoksa ve en az Bachelor; claim 23-24; kaynak 116 ile uyumlu. |

### fatura (12 orta): hepsi K
| Kart | İlk bulgu | Durum | Kanıt |
|---|---|---|---|
| elektrik-faturasi | orta "en az 3 yıl" vaadi | K | Adım 5 + claim 14 "mindestens … drei Jahre, längstens … seit Beginn" (EnWG §40b canlı aynı). |
| elektrik-faturasi | orta "tarihe kadar fesih bildir" | K | Son tarih silindi; "yürürlüğe girdiği tarihte sona erecek şekilde, bekleme süresi ve ayrı ücret olmadan" (EnWG §41). |
| isitma-ve-yan-gider | orta %50-%70 genel kural | K | %70 istisnası (1994 WSVO, yağ/gaz, yalıtımlı borular) HeizkostenV §7/1 ile birebir; claim 12, 13. |
| isitma-ve-yan-gider | orta BGB §556 notu | K | Abs.1, Abs.2 S.2, Abs.3'e daraltıldı (§556/5 ile aynı). |
| yayin-katki-payi | orta açık uçlu muafiyet | K | ALG I, Wohngeld, Übergangsgeld "hakkı yoktur"; claim 25 canlı aynı. |
| yayin-katki-payi | orta belge şartı | K | Ad, yardım türü, dönem; claim 20, 22, 23. |
| yayin-katki-payi | orta çevrimiçi başvuru | K | Doldur, yazdır, imzala, belgeyle gönder; claim 21, 24. |
| numara-tasima | orta not tüm kartı kapsıyor | K | Not Weiterversorgung/ücret yarısına sınırlı; taşınmada tazminat BNetzA metniyle aynı. |
| numara-tasima | orta tazminat cümlesi | K | cost: "ilk günden sonraki her ek iş günü", eski operatörden, sabit aylık ücretli, "gecikmeyi sen yapmadıysan"; TKG §59/4 ve §59/6 ile birebir. |
| elektrik-kesme | orta kabulden sonra kesme yasağı | K | "taksitleri … yerine getirmezsen kesme hakkını geri kazanır"; EnWG §41g. |
| elektrik-kesme | orta sosyal yardım kurumuna bildirim | K | Onaysız bildirim koşulları; claim 35-38 kaynakla uyumlu. |
| elektrik-kesme | orta itiraz edilen alacak | K | "mahkeme kararıyla kesinleşmemiş (nicht titulierte) … biçim ve süre kurallarına uygun, gerekçeli"; "yazılı" silindi (EnWG §41f). |

## Yeni kaynak kontrolü
- para / almanya-emeklilik-yasi...: kaynaklar de:kaynak:203 (SGB VI tam metin, https://www.gesetze-im-internet.de/sgb_6/BJNR122610989.html) + de:kaynak:021 (DRV Verbindungsstelle Türkei). Kart başına 2 kaynak: tamam. Bağlantılar yalnız kartın kaynaklarından (013 kalmamış). Claim 1-3 ve 18-28 quote'ları kaynak 203'te var (§35, §50, §235 aynı dosyada), claim 29-30 kaynak 021'de. Kaynak–claim–kart tutarlı. Tek zayıflık küçük (bkz. emeklilik): claim 21-27 quote'ları başlıksız tablo satırı.
- is / burgergeld...: kaynaklar de:kaynak:118 + de:kaynak:120 (SGB II §7, https://www.gesetze-im-internet.de/sgb_2/__7.html; canlı metin kopyayla aynı). 2 kaynak: tamam; 119 çıkarıldı, Regelsatz karttan silindi, tutarlı. Claim 15-23 quote'ları kaynakta var ve iddiayı kanıtlıyor. Bulgular aşağıda (5 yıl istisnası, eksik koşullar).

## Kart bulguları

### kdv-umsatzsteuer-oranlari-19-ve-7: orta
- Bulgu: Summary "demiryolu ile yolcu taşımacılığı ile tarifeli otobüs, taksi, teleferik, vapur ve feribot taşımacılığı, bunlarda taşıma aynı belediye içinde ya da en çok 50 kilometre ise (Nr. 10)". "Bunlarda" demiryolunu da kapsıyor. Kanunda belediye/mesafe şartı yalnız b) bendindeki taşımalar için; a) demiryolu şartsız. Okuyucu uzun mesafe tren biletinin %19 olduğunu sanar. Claim 6 (demiryolu) ve 7-8 (şart) ayrı ve doğru; kartın cümlesi bunları birleştirip bozuyor.
- Kanıt: https://www.gesetze-im-internet.de/ustg_1980/__12.html "10. die Beförderungen von Personen a) im Schienenbahnverkehr, b) im Verkehr mit Oberleitungsomnibussen, im genehmigten Linienverkehr mit Kraftfahrzeugen, im Verkehr mit Taxen, mit Drahtseilbahnen und sonstigen mechanischen Aufstiegshilfen aller Art und im genehmigten Linienverkehr mit Schiffen sowie die Beförderungen im Fährverkehr aa) innerhalb einer Gemeinde oder bb) wenn die Beförderungsstrecke nicht mehr als 50 Kilometer beträgt;"
- Düzeltme: "demiryolu ile yolcu taşımacılığı (mesafe şartı yok); tarifeli otobüs, taksi, teleferik, tarifeli vapur ve feribotta ise yalnız aynı belediye içindeki ya da en çok 50 km'lik taşımalar (Nr. 10)". Steps'teki "tarifeli şehir içi taşıma" demiryolunu kapsamıyorsa öyle kalsın.

### yillik-vergi-beyannamesi-elster-son-tarih: orta
- Bulgu 1 (orta, ilk raporun kalan kısmı): Kart bugün (25.10.2026) için tarihi geçmiş örnek veriyor: steps "2025 yılı için bu gün 31 Temmuz 2026'dır", summary/timing aynı. Editör valid_until'i 2026-07-31 yaptı: kart kendi kuralına göre 25.10.2026'da süresi dolmuş. Editör 2026 yılı sayfasının kaynak dizininde olmadığını yazdı; canlı: help_est_ufa_10_2026 sayfası yok, help_est_ufa_10_2025 hâlâ 31 Temmuz 2026 diyor.
- Kanıt: https://www.elster.de/eportal/helpGlobal?themaGlobal=help_est_ufa_10_2025 "Die Frist … der Einkommensteuererklärung 2025 … läuft bis zum 31. Juli 2026."
- Düzeltme: "bu gün 31 Temmuz 2026" ve tarihli cümleleri sil; genel kuralı AO §149 Abs.2 ile tarihsiz yaz ("takvim yılının bitiminden en geç yedi ay sonra"); danışman kuralını "vergilendirme dönemini izleyen ikinci takvim yılının Şubat ayının son günü" diye yaz; valid_until: null. Tarihli örnek yalnız yeni yıl sayfası kaynak olursa eklenir.
- Bulgu 2 (küçük): "ikinci takvim yılının Şubat ayının son günü" hangi yıla göre ikinci olduğunu söylemiyor (kanun: "des zweiten auf den Besteuerungszeitraum folgenden Kalenderjahres"). Okuyucu bir sonraki yılın Şubat'ını sanabilir. Düzeltme: "vergilendirme dönemini izleyen ikinci takvim yılı".
- Bulgu 3 (küçük): Summary'deki "EStG §46 Abs. 2 Nr. 8 uyarınca verilen beyannameler bunun dışındadır" okuyucuya bir şey söylemiyor (Nr. 8 nedir, hangi süre geçerli?); kaynak yalnız "hariç" diyor. Düzeltme: cümleyi ve claim 13'ü sil, ya da Nr. 8'in ne olduğunu kaynakla yaz; kaynak yoksa sil.

### isten-cikarma-fesih-sureleri-ve-kschg-korumasi: orta
- Bulgu 1 (orta, yeni yanlış kapsam): Summary "on çalışanlık kuralında 31 Aralık 2003'ten sonra işe başlayanlar on çalışana kadar sayıya katılmaz (md. 23)" ve claim 30. Kanunda bu cümle on çalışan kuralını değil, beş çalışan kuralını (Satz 2) anlatır: 2003 sonrası başlayanlar, "Satz 2'ye göre" çalışan sayılırken işyerinde olağan olarak on çalışana kadar sayıya katılmaz. Kart yanlış eşiği veriyor.
- Kanıt: https://www.gesetze-im-internet.de/kschg/BJNR004990951.html "diese Arbeitnehmer sind bei der Feststellung der Zahl der beschäftigten Arbeitnehmer nach Satz 2 bis zur Beschäftigung von in der Regel zehn Arbeitnehmern nicht zu berücksichtigen"
- Düzeltme: "31 Aralık 2003'ten sonra işe başlayanlar, beş çalışan sınırı (md. 23/1 cümle 2) hesaplanırken işyerinde olağan olarak on çalışana kadar sayıya katılmaz" yaz, claim 30'u aynı şekilde düzelt; emin olunmazsa cümleyi sil (bir önceki cümle on çalışan kuralını zaten doğru veriyor).
- Bulgu 2 (küçük): Claim 25 quote'u "hat der Arbeitnehmer das fünfzigste Lebensjahr …" kaynakta "Hat der Arbeitnehmer …" (büyük H). pack_check büyük/küçük harfe duyarlıysa claim düşer. Düzeltme: quote'u kaynaktaki yazımla yaz.

### burgergeld-grundsicherungsgeld-temmuz-2026: orta
- Bulgu 1 (orta, yeni belirsizlik): "Almanya'da en az beş yıldır olağan ikametin varsa (süre adres kaydıyla başlar) bu son dışlama uygulanmaz." Önceki cümle üç dışlamayı sayıyor (oturum hakkı olmayanlar; yalnız iş/eğitim aramaya dayananlar; Asylbewerberleistungsgesetz kapsamındakiler); "bu son" AsylbLG'yi de kapsıyormuş gibi okunur. Kanunda beş yıl istisnası yalnız Satz 2 Nr. 2 içindir, Nr. 3 (AsylbLG) için değil; serbest dolaşım hakkının kaybı tespit edildiyse istisna işlemez; Nr. 2 b'de "AufenthG §20a oturum izni" de var, kartta yok.
- Kanıt: https://www.gesetze-im-internet.de/sgb_2/__7.html "Abweichend von Satz 2 Nummer 2 erhalten Ausländerinnen und Ausländer und ihre Familienangehörigen Leistungen nach diesem Buch, wenn sie seit mindestens fünf Jahren ihren gewöhnlichen Aufenthalt im Bundesgebiet haben; dies gilt nicht, wenn der Verlust des Rechts nach § 2 Absatz 1 des Freizügigkeitsgesetzes/EU festgestellt wurde."
- Düzeltme: "Almanya'da en az beş yıldır olağan ikametin varsa (süre adres kaydıyla başlar), oturum hakkı olmayanlar ve oturum hakkı yalnız iş/eğitim yeri aramaya dayananlar için dışlama uygulanmaz; Asylbewerberleistungsgesetz kapsamındakiler için bu istisna yoktur. Serbest dolaşım hakkının kaybı tespit edildiyse de uygulanmaz." Nr. 2 b'ye "ya da AufenthG §20a'ya göre oturum izninden doğan" ekle (terimi kaynakta açıklanmadığı için çevirme).
- Bulgu 2 (küçük): "AB serbest dolaşım hakkı Türk vatandaşları için geçerli değildir" claim'siz (Kural 7 bu cümleyi bir cümleyle şart koşuyor, doğru; ama kaynakta Türk vatandaşı geçmiyor). "AufenthG Bölüm 2 Kısım 5" kriptik. valid_until 2026-12-31 artık gereksiz (karta tarihe duyarlı tutar kalmadı). Düzeltme: Türk cümlesini "serbest dolaşım hakkı olmayan yabancılar" cümlesine bağlayan kısa bir claim yaz ya da cümleyi tutarlı kısalt; "Kapitel 2 Abschnitt 5 AufenthG" ifadesini açıkla ya da çıkar; valid_until null olabilir.

### is-sozlesmesi-yazili-sartlar-belirli-sure: orta
- Bulgu 1 (orta, yeni eksik şart): Summary "52 yaşını doldurmuş ve başlangıçtan önce en az dört ay işsiz kalmış kişilerde beş yıla kadar". Kanunda "unmittelbar vor Beginn" (hemen öncesi) dört ay işsizlik ya da Transferkurzarbeitergeld ya da kamu destekli istihdam tedbiri. Kart "hemen" demiyor, alternatifleri yazmıyor (claim 24'te var, summary'de yok): iki yıl önce dört ay işsiz kalan okuyucu hakkı olduğunu sanır.
- Kanıt: https://www.gesetze-im-internet.de/tzbfg/__14.html "und unmittelbar vor Beginn des befristeten Arbeitsverhältnisses mindestens vier Monate beschäftigungslos im Sinne des § 138 Absatz 1 Nummer 1 des Dritten Buches Sozialgesetzbuch gewesen ist, Transferkurzarbeitergeld bezogen oder an einer öffentlich geförderten Beschäftigungsmaßnahme nach dem Zweiten oder Dritten Buch Sozialgesetzbuch teilgenommen hat"
- Düzeltme: "52 yaşını doldurmuş ve başlangıçtan hemen önce en az dört ay işsiz kalmış (ya da Transferkurzarbeitergeld almış ya da kamu destekli istihdam tedbirine katılmış) kişilerde".
- Bulgu 2 (küçük): "bu kural, Anayasa Mahkemesi'nin 6 Haziran 2018 tarihli kararındaki koşullarla Anayasa'ya uygundur" içerik vermiyor (hangi koşul?). Kaynak dipnotu yalnız "Nach Maßgabe der Entscheidungsformel mit GG vereinbar" diyor. Düzeltme: "Anayasa Mahkemesi (6 Haziran 2018) bu kuralı yalnız belirli koşullarla Anayasa'ya uygun buldu" (dipnotun söylediği kadar) ya da cümleyi "yasa metnine göre" ile bırakıp BVerfG kısmını sil.

### ev/yan-giderler-betriebskosten-kalemler-yillik-hesap-itiraz: orta (konular arası tutarlılık, grup dışı)
- Bulgu: Note son cümlesi "Bu kurallardan kiracı aleyhine sapan anlaşma geçersizdir." kartın tüm kurallarını (Hauswart içeriği, ekonomiklik, kısmi hesap dahil) kapsıyormuş gibi; BGB §556/5 yalnız Abs.1, Abs.2 S.2, Abs.3 ve Abs.3a için. Aynı hata fatura/503'te ilk raporda orta bulgu olarak yazılmış ve editör daraltmış; ev/704 hâlâ eski haliyle.
- Kanıt: https://www.gesetze-im-internet.de/bgb/__556.html "Eine zum Nachteil des Mieters von Absatz 1, Absatz 2 Satz 2, Absatz 3 oder Absatz 3a abweichende Vereinbarung ist unwirksam."
- Düzeltme: fatura/503 note'unu esas al: "Yan giderlerin kiracıya yüklenmesine, avansın makul olmasına, hesap süresine ve itiraz süresine ilişkin BGB §556 kuralları kiracı aleyhine değiştirilemez." (Hauswart ve kısmi hesap cümleleri bu kapsamın dışında kalsın.) Küçük: fatura/503 "ev sahibi", ev/704 "kiralayan" diyor; terim birleşebilir.

### basiskonto-temel-hesap-hakki: küçük
- Bulgu 1 (küçük, editörün yeni yazım hatası): Summary "aynı bankadaki Basiskonton ödeme gecikmesi ya da yasak kullanım yüzünden". Düzeltme: "Basiskontonun" (ya da "Basiskonton" yerine "temel hesabın").
- Bulgu 2 (küçük): "Banka yalnızca şu durumlarda reddedebilir" + dört neden. BaFin aynı sayfada geçerli kimlik sunulamazsa da reddedilebileceğini söylüyor ve birinci nedende "hesabın kapatıldıysa/kapatılacağı bildirildiyse bankaya bildir" notunu veriyor. "Yalnızca" tam liste gibi okunuyor.
- Kanıt: https://www.bafin.de/DE/verbraucherinnen-verbraucher/themen-finanzprodukte/konten-zahlungen/konten/basiskonto/basiskonto_node.html "Können Sie sich nicht mit einem geeigneten Dokument ausweisen oder ist es abgelaufen, darf die Bank Ihren Antrag ablehnen."
- Düzeltme: "yalnızca" yerine "şunlar yasal ret nedenidir"; geçerli kimlik sunamamayı bir cümleyle ekle (steps'te kimlik zaten var).

### iban-sepa-havale-anlik-havale-lastschrift: küçük
- Bulgu (küçük): Note 9 cümleye çıktı; "Zorunluluk 9 Ekim 2025'ten itibaren …" cümlesi öznesiz (hangi zorunluluk: alıcı kontrolü). Claim 24 quote'u listenin yalnız sonunu içeriyor ("Island, Liechtenstein und Norwegen sowie der Schweiz …"), "Türkiye listede yok"u tek başına kanıtlamıyor (27 AB ülkesi cümlesi yok). Düzeltme: "Alıcı kontrolü 9 Ekim 2025'ten itibaren …" yaz; claim 24 quote'unu "Dieser besteht aus den 27 EU-Staaten, den weiteren EWR-Ländern …" ile başlat (en çok 200 karakter).

### gelir-vergisi-2026-grundfreibetrag-dilimler: küçük
- Bulgu (küçük, yazar notuyla çelişme): valid_until null yapıldı (ilk rapor önerisi). DE_YAZAR_NOTLARI "Grundfreibetrag ve vergi dilimleri"ni tarihe duyarlı sayıyor ve "Kaynak yıl veriyorsa o yılın 31 Aralık'ı" diyor; kaynak "ab dem Veranlagungszeitraum 2026" yılını veriyor, başlık/summary "2026". Null kalırsa kart 2027'de sessizce bayatlar. Düzeltme: 2026-12-31 geri konabilir (editör kararı; ilk rapor ve yazar notu çelişiyor, ikincisi geçerli). Rakamlar ve formül katsayıları EStG §32a ile birebir; sorun yok.

### kilise-vergisi-kirchensteuer-cerceve: küçük
- Bulgu (küçük): Federal çerçeve ve kaynak uyumu doğru. Ama başlık "nasıl hesaplanır?" diyor; maaş kilise vergisinin oranı yok (ücret vergisi matrah, oran verilmiyor), oran yalnız sermaye geliri için "dini topluluğun oranı". Step 1 ve 3 "bil" dolgusu (eylem değil). Kaynak oran vermediği için rakam yazılamaz. Düzeltme: başlıkta "nasıl hesaplanır" yerine "neye göre hesaplanır"; step 1 ve 3'ü summary'ye birleştir ya da sil.

### maas-sosyal-sigorta-kesintileri-2026: küçük
- Bulgu (küçük, KS): Başlık daraldı (ilk bulgu kısmen kapandı). Konular arası: is/bordro "sağlık ve bakım sigortası üst sınırı" yazıyor, saglik/603 bakım sigortası oranını (%3,6, çocuksuz %4,2) veriyor; para/308 bordroda bakım sigortası kalemi olduğunu hiç söylemiyor. Okuyucu bordrodaki "Pflegeversicherung" satırını bu kartta bulamaz. Kaynaklar 018 ve 028 bunu kanıtlamıyor, yeni kaynak eklenemez (2 sınır). Düzeltme: kaynaksız cümle yazma; başlığın "… emeklilik, işsizlik ve sağlık …" daralması yeterli kabul edilebilir (editör kararı); kalan boşluk gaps.md'de dursun. Rakamlar ve "kural olarak" eklemesi doğru.

### almanya-emeklilik-yasi-bekleme-suresi-turkiye-anlasmasi: küçük
- Bulgu (küçük): Ciddi bulgu kapandı. Claim 21-27 quote'ları yalnız sayı satırı ("1958 12 66 0" gibi); başlıksız sayı dizisi tek başına iddiayı kanıtlamaz. Düzeltme: tabloyu tanıtan cümleyle birleştir ("Für Versicherte, die nach dem 31. Dezember 1946 geboren sind, wird die Regelaltersgrenze wie folgt angehoben:" ile birlikte tek satır; 200 karakteri aşıyorsa yılları iki claim'e böl).
- Not (bulgu değil): §235 Abs.2 son cümledeki Altersteilzeit/Anpassungsgeld istisnası (1955 öncesi) kartta yok; çok dar grup, yazılması gerekmez.

### kredi-bilgi-kurulusu-bilgi-hakki-dsgvo-md-15-skor: küçük
- Bulgu (küçük, A): "Schufa" adı başlık ve summary'de duruyor; kartın iki kaynağında (BfDI, BDSG §31) geçmiyor. Editör orkestratör kararıyla ("Schufa gibi") bıraktı; durum ilk rapordaki gibi. Düzeltme: "Schufa gibi" ifadesini sil ya da kararı gaps.md'de belgele.

### maas-bordrosu-haklari-ve-2026-prim-ust-sinirlari: küçük
- Bulgu (küçük, editör değişikliği değil): Note "bu karttaki tutarlar 1 Ocak 2026'dan itibaren geçerli olanlardır" kart hakkında meta cümle. Düzeltme: "Tutarlar 1 Ocak 2026'dan itibaren geçerlidir."

### yayin-katki-payi-rundfunkbeitrag-tutar-ve-muafiyet: küçük
- Bulgu (küçük): Summary "daireyi kendi adına kullanan kişi (Inhaber) öder"; kaynak "im eigenen Namen nutzt oder in deren Namen die Betriebsstätte/Wohnung genutzt wird". İkinci yarı (adına kullanılan kişi) yok; claim 31 quote'u "nutzt"ta kesik. Canlı sayfa aynı tanımı veriyor. Düzeltme: "daireyi kendi adına kullanan ya da adına kullanılan kişi (Inhaber)" yaz, quote'u tamamla.

### elektrik-temel-tedarik-ve-saglayici-degistirme ve elektrik-kesme-ve-odeme-guclugu: küçük
- Bulgu (küçük): "Werktag" iki kartta açıklamasız ("her Werktag'ta", "8 Werktag"); is/calisma kartı terimi BUrlG §3'e dayanarak "Pazar ve yasal tatil dışındaki tüm günler, Cumartesi dahil" diye tanımlıyor. Türk okuyucu 8 Werktag'ı 8 iş günü sayabilir. EnWG kaynaklarında tanım yok, bu yüzden karta tanım eklenemez. Düzeltme: gerekmez; gaps.md'ye not düşülür (tanım için BUrlG §3/2 başka kartın kaynağıdır).

### internet-ve-mobil-sozlesme-suresi-ve-fesih: küçük
- Bulgu (küçük): Claim 10 metni "Sağlayıcı yeni adreste hizmeti yalnız orada sunuyorsa …"; kaynakta "yalnız" yok ("soweit er diese dort anbietet" = orada sunuyorsa). Düzeltme: "yalnız"ı sil.

### numara-tasima-ve-operator-degistirme: küçük
- Bulgu (küçük): Claim 32 metni "alternatif olarak aylık ücretin %20'si istenebilir" içeriyor; quote ("Die Höhe der Entschädigung ist gesetzlich begrenzt auf 10 Euro pro Arbeitstag beziehungsweise pro versäumten Termin.") bu yarısını kanıtlamıyor. Sonraki cümle ("Alternativ können Sie 20 Prozent des vertraglich vereinbarten Monatsentgelts verlangen, falls dieser Betrag höher als 10 Euro ist.") kaynakta ve canlıda var; kartın cümlesi doğru. Düzeltme: quote'u iki cümleyi kapsayacak biçimde genişlet (en çok 200 karakter) ya da claim'i ikiye böl.

### saglik/603 (konular arası): küçük
- Bulgu (küçük): Adım 5 "Bürgergeld alıyorsan çocuksuzluk zammı ödemezsin" eski adı kullanıyor; is/burgergeld ve fatura/505 "Grundsicherungsgeld (eski adıyla Bürgergeld)" diyor. DE_YAZAR_NOTLARI "kaynaktaki adı kullan, kaynağın tarihini yaz" der; kaynak 025'in tarihi/adlandırması bu karta bakılarak teyit edilmeli. Düzeltme: kaynağın adı neyse onu yaz ve gerekirse "(2026'dan itibaren Grundsicherungsgeld)" ekle.

### Temiz kartlar (değişen cümleler kaynak ve canlı metinle uyumlu)
- para: vergi-sinifi-lohnsteuerklasse-1-6 (Abs.3 Satz 3 kapsamı, I. sınıfta sınırlı vergi yükümlüleri), zorunlu-arac-sigortasi..., hesap-degistirme-yardimi-kontenwechselhilfe (13 ay ve Restsaldo cümleleri BaFin ile aynı).
- is: asgari-ucret-2026-2027, calisma-suresi-mola-yillik-izin-resmi-tatil, hastalik-bildirimi-rapor-ucret-surmesi-krankengeld, issizlik-parasi-alg-1..., serbest-calisma-bildirimi-ve-kleinunternehmer-siniri, minijob-midijob-2026..., yabanci-diploma-ve-meslek-tanima-anerkennung (Erzieher açıklaması kaynak 117'de: "landesrechtlich geregelten Berufen (z.B. Erzieher, Lehrer oder auch Ingenieure)").
- fatura: elektrik-faturasi-donemleri..., isitma-ve-yan-gider-hesabi..., su-ve-atik-su-gideri..., internet-hizi-dusuk-ve-ariza-haklari.

## Konular arası tutarlılık
- para/308 (maas-sosyal-sigorta) ile saglik/603: sayılar tutarlı (%14,6; indirimli %14,0; ortalama ek prim %2,9; aylık 5.812,50 / yıllık 69.750; yarı yarıya paylaşım). Çelişki yok. Eksik/uyum: bakım sigortası yalnız saglik/603'te ve is/bordro'nun üst sınır cümlesinde (yukarıdaki iki küçük bulgu).
- is/asgari-ucret ile is/minijob: tutarlı (13,90 Euro 2026; 14,60 Euro 1 Ocak 2027; Minijob 603 Euro/ay, 7.236 Euro/yıl; 603/13,90 = 43,38 saat). valid_until 2026-12-31 (minijob) ve 2027-12-31 (asgari) çelişki değil.
- is/bordro ile para/308: RV 8.450 ve GKV 5.812,50 (aylık) iki kartta aynı; valid_until aynı.
- fatura/503 ile ev/704: yıllık hesap kuralı (avans ödeyene, dönem bitiminden sonraki 12. ayın sonu, geç kalınca ek ödeme yok, "vertreten" istisnası) aynı. Çelişki: ev/704 note'u BGB §556/5 kapsamını genişletiyor (yukarıdaki orta bulgu).

## Sayılar
- Ciddi 0.
- Orta 6: kdv, yillik-vergi, isten-cikarma, burgergeld, is-sozlesmesi, ev/704.
- Küçük 19: basiskonto 2, iban 1, gelir-vergisi 1, yillik-vergi 2 (Bulgu 2, 3), kilise 1, maas 1, emeklilik 1, kredi 1, bordro 1, is-sozlesmesi 1, isten-cikarma 1 (Bulgu 2), burgergeld 1 (Bulgu 2), Werktag 1 (iki kart), yayin 1, internet-ve-mobil 1, numara-tasima 1, saglik/603 1.
- Bakılmayanlar: kapalı üç site; editörün dokunmadığı eski claim'lerin anlamsal okuması (yalnız quote'un metinde varlığı script ile bakıldı); ev ve saglik kartlarının 704 ve 603 dışındaki içeriği; Rundfunkbeitrag zam tartışması (ilk rapor aynı gün baktı, tutar 18,36 Euro canlıda geçerli); BVerfG 6.6.2018 kararının kendi metni açılmadı.
