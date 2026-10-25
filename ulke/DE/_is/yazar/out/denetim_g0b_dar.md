# Almanya ulusal paketi, grup 0 ("oturum" 15 kart + "resmi" 12 kart): editör sonrası DAR bağımsız denetim (G0b)

Tarih: 25.10.2026. Denetçi kartları yazmadı, editör değil; `gaps.md` yalnız başlık düzeyinde göz atıldı. Hiçbir kart dosyasına dokunulmadı.

## Özet
- Kart: 27 (oturum 15, resmi 12). Yeni bulgu: **ciddi 0, orta 2, küçük 15**. İlk denetimin ciddi bulgusu (oturum-belgesi-ucretleri, 67 Euro) ve resmi konusunun ciddi bulgusu (itiraz, dava süresi) **kapandı**.
- İlk bulgular (58 madde; resmi raporda bir kartın alt bulguları ayrı sayıldı): **kapandı 49, kısmen 8, açık 1**. Açık olan tek madde: oturum-belgesi-ucretleri Türk okuyucu uyarısı (editör "uygulanamaz" dedi; 2 kaynak sınırı).
- Editörün değiştirdiği/eklediği cümleler yedekle karşılaştırıldı (27 kartın tüm alanları + claims + Bağlantılar + valid_until). Kaynak metne karşı: yeni/değişen tüm claim alıntıları kaynak metinde birebir var (0 eksik alıntı); kart başına kaynak ≤2 (hepsi); Bağlantılar adreslerinin hepsi `kaynak_dizini.jsonl`'de; yeni kaynaklar de:kaynak:204 (PAuswGebV §1) ve 205 (SVBezGrV 2026 §4) kartlarla ve claim'lerle tutarlı. Şehir adı, "yaklaşık" eki, havale cümlesi, kaynak kimliği/slug sızıntısı yok (regex taraması). Altyazılar ≤160 karakter.
- **Yeni hata girişi (orta):** alman-vatandasligi-sartlari kartına editörün eklediği mutlak "ceza almış olmamalısın" cümlesi StAG §12a ile (canlı doğrulandı) çelişiyor: ≤90 Tagessatz para cezası, ≤3 ay (şartlı, bağışlanmış) hapis sayılmaz. Kartın kaynağı §10'da §12a'ya atıf yok.
- Çapraz tutarlılık: ücretler tutarlı (vize 75 Euro / uzatma 25 Euro [vize kartı]; 75 Euro ve çocuk 40 Euro [eş birleşimi]; 100/93/96/98/67 Euro [ücret kartı]; 46 / 27,60 Euro [Ortaklık Hukuku kartı]); kartlar arası çelişki yok. oturum/vize kartı ile resmi kartlar (evlilik "vize gerekir", doğum "vizesiz/vizeli kalış") çelişmiyor. Tekrar: ortaklik-hukuku kartı artık yalnız ücret; Aufenthaltserlaubnis ile belgeleme yükümlülüğü yalnız oturum-belgesi-turleri kartında (tekrar yok).

## Canlı açılanlar (25.10.2026, Python urllib; yalnız editörün eklediği/değiştirdiği bilgi için)
gesetze-im-internet.de: pauswgebv/__1 (27,60 / 46 Euro doğru), svbezgrv_2026/__4 (101 400 Euro doğru), aufenthv/__52a, stag/__12a (yeni bulgu için), vwvfg/__3a (nitelikli imza, elektronik form + eID doğru), aufenthg_2004/__16d (Anpassungsmaßnahme bağlamı). bundesjustizamt.de Führungszeugnis_node (13,00 Euro, 1 Ekim 2026 dijital sürüm, Gebührenbefreiung ve kanıt, BundID posta kutusu hepsi canlıda var; kayıtlı kopyadan fark yok). tuerkei.diplo.de: 1513838 (Aile Cüzdanı iki ifade, muafiyet listesi, Anerkennungsbescheid, "Fremdsprachige Urkunden" canlıda var), 05-visaeinreise/2729790 (Anpassungsmaßnahme 2–9 ay, yanlış kategori, 39,92), 05-visaeinreise/2728584 (Merkblatt 01F: belge listesi, barkod, 75,00 Euro).
Kayıtlı kopya (`text_file`) ile ayrıca karşılaştırıldı: AufenthG §8, §9, §21, §30 (tam yasa), §33, §51, §20a, 054 (FreizügG §1), 052 (StAG §10), 047 (AufenthV §45c), 039, 098, 094, 092, 095, 084.

## Bakılmayanlar
bmi.bund.de (kapalı; 2026 Mavi Kart euro eşikleri hâlâ yok), make-it-in-germany.com, auswaertiges-amt.de, bzr.bund.de (talimat gereği denenmedi). Türkiye tarafı (Türk apostil makamları, NVİ, e-Apostil) bağımsız doğrulanmadı. BMV i-Kfz-Dashboard (JavaScript, içerik kopyada yok). StAG §12a kayıtlı kaynak dizininde yok (yalnız canlı açıldı).

---

## 1. İlk bulgular kapanış tablosu

Kısaltma: K = kapandı, KS = kısmen, A = açık.

### Konu "oturum" (35 madde: 2 çapraz + 33 kart)
| # | Kart / ilk bulgu (derece) | Durum | Kanıt cümlesi |
|---|---|---|---|
| C1 | Ausländerbehörde "adı şehre göre değişir" (küçük) | K | mavi-kart adım 4, uzatma özeti, is-degistirince özeti, ab-vatandasi adım 1, yurt-disi özeti: "Ausländerbehörde (yabancılar dairesi; adı şehre göre değişir)" ilk geçişte var |
| C2 | Bağlantı etiketleri hepsi "Bilgi al" (küçük) | KS | "Randevu al / Tarifeyi gör / Başvur" geldi; "Başvur" etiketi yasa metnine gidiyor (aufenthg_2004/__81.html), 25 bağlantının çoğu hâlâ "Bilgi al" (zorunlu değildi) |
| 1 | turleri: özet/adım çelişkisi, Niederlassungserlaubnis istisnası (orta) | K | özet: "Ortaklık Anlaşması'ndan oturum hakkın varsa ve Niederlassungserlaubnis ya da AB uzun süreli oturum iznin yoksa, bu hakkı Aufenthaltserlaubnis ile belgelemen gerekir" (§4 Abs. 5 ile uyumlu) |
| 2 | turleri: başlık sorusu ilk cümlede (küçük) | K | "Yedi belge türü var: vize (Visum), …" |
| 3 | vize: "uyum önlemi" çevirisi (orta) | KS | terim değişti; ama "yabancı meslek yeterliliğinin tanınması için tamamlama eğitimi" açıklaması kartın iki kaynağında (041, 043) yok: 041 yalnız "Anpassungsmaßnahme: je nach Auslandsvertretung zwischen 2-9 Monaten" der (bkz. yeni bulgu) |
| 4 | vize: "güncel tarife", valid_until (küçük) | K | maliyet: "Güncel tarifeye göre ulusal vize (D) ücreti 75 Euro"; valid_until.json'da es-icin satırı (null) var |
| 5 | mavi-kart: eşik ilk cümlede, havale, yıl (orta) | K | özet: "Maaş eşiği … prim tavanının yüzdesidir: genel eşik %50'dir"; havale silindi; "Yıllık prim tavanı 2026 için … 101.400 Euro'dur" (canlı: "101 400 Euro jährlich") |
| 6 | mavi-kart: valid_until (küçük) | K | valid_until.json: "mavi-kart-ab-sartlari": "2026-12-31" |
| 7 | nitelikli: yeterlilik onayı/dil herkese değil (orta) | K | adım 5: "Puanla başvuruyorsan: …"; §20a Abs. 4 ile uyumlu |
| 8 | nitelikli: §18 şartları, Fachkraft, 45 yaş (orta) | K | adım 1-3 ve claim 21-27; "mindestens 55 Prozent der jährlichen Beitragsbemessungsgrenze" |
| 9 | nitelikli: Abschnitt çevirisi, Folge-Chancenkarte (küçük) | K | not: "yasanın 3. ya da 4. kısmı (Abschnitt 3 ve 4 …)"; "en çok iki yıl daha"; "Absatz 2 findet auf die Folge-Chancenkarte keine Anwendung" |
| 10 | ogrenci: geçim şartı (orta) | K | özet: "kural olarak geçimin de güvencede olması aranır"; claim 14 |
| 11 | ogrenci: terim, 140 gün cevabı sonda (küçük) | K | özet: "Yılda en çok 140 iş günü çalışabilirsin." |
| 12 | es-icin: §30 yalnız yabancı eş, Alman eş §28 (orta) | K | başlık "(yabancı uyruklu ya da Alman)"; özet "Alman eşin yanına gidenler için § 28, § 30'un 18 yaş ve basit Almanca şartlarını uygular" (§28 Abs. 1 S. 5 ile uyumlu) |
| 13 | es-icin: belge listesi eksik, "iki kopya" kapsamı (orta) | K | documents: Türk eşin nüfus kaydı, boşanma/ölüm belgeleri, barkod notu; "Bitte bringen Sie zusätzlich die folgenden Unterlagen im Original und in zweifacher Kopie mit" (liste Formül B'den başlıyor) ile adım 4 uyumlu |
| 14 | yerlesme: ilk cümle (küçük) | K | özet "Genel kuralda 5 yıl Aufenthaltserlaubnis, 60 ay …" |
| 15 | yerlesme: eş kolaylığı kapsamı (küçük) | K | adım 5; §9 Abs. 3 "Abs. 2 Satz 1 Nr. 3, 5 und 6" |
| 16 | vatandaşlık: geçim istisnaları, 1974 dil, sabıka (orta) | KS | istisnalar, dil, sabıka eklendi; ama adım 4'te "kusur" koşulu yok ve sabıka cümlesi mutlak (bkz. yeni bulgu) |
| 17 | vatandaşlık: çifte vatandaşlık notu (orta) | K | not ve kaynak 053 silindi; kartta çifte vatandaşlık hakkında hiçbir şey yok |
| 18 | vatandaşlık: "§16b ve §20a dahil" (orta) | K | adım 1: "Öğrenim (§ 16b), Chancenkarte (§ 20a) … verilmiş belgeler sayılmaz" |
| 19 | vatandaşlık: iç not (küçük) | K | not: "Hastalık, engel ya da yaş nedeniyle dil ve test şartlarından vazgeçilir." |
| 20 | uzatma: Fiktionsbescheinigung çalışma hakkı genel (orta) | K | özet/adım 2: "öğrenim ya da çalışma amaçlı" ile daraltıldı; §81 "Kapitel 2 Abschnitt 3 und 4" |
| 21 | uzatma: kurs notu (küçük) | K | not + "§ 25 Abs. 1, 2 ve 3 … uygulanmaz" (§8 Abs. 4 ile uyumlu) |
| 22 | ortaklik: tutar yok, kapsam dar (orta) | K | "46 Euro … 24 yaşını doldurmamış kişi için 27,60 Euro"; kapsam "§§ 44–45, § 45c Abs. 1, § 48 Abs. 1 Nr. 15" (canlı doğrulandı) |
| 23 | ucretleri: 67 Euro yanlış neden (CİDDİ) | K | özet: "pasaportun geçerlilik süresi dolduğu, kartın teknik kullanım süresi bittiği, verilerde değişiklik olduğu, kaybolduğu ya da çip bozulduğu için yeniden düzenlenirse (Neuausstellung) ücret 67 Euro'dur"; §45c Abs. 1 Nr. 1-4 ile birebir |
| 24 | ucretleri: Türk okuyucu uyarısı (orta) | **A** | editör "uygulanamaz": 048 üçüncü kaynak olamaz; kart hâlâ genel (bkz. yeni bulgu) |
| 25 | ucretleri: güncel tarife, başlık (küçük) | K | başlık "Aufenthaltserlaubnis, Mavi Kart AB ve ICT-Karte ücretleri …"; özet "(güncel tarife)" |
| 26 | is-degistirince: §18a/b işe bağlı değil (orta) | K | özet: "(§ 18a, § 18b) nitelikli her işte çalışmak için verilir" |
| 27 | is-degistirince: çeviri, işveren bildirimi (küçük) | K | cümle silindi |
| 28 | serbest: üç şart / serbest meslek (orta) | K | özet ikiye ayrıldı; §21 Abs. 5 "abweichend von Absatz 1" |
| 29 | ab-vatandasi: "yalnız", Alman eş yönlendirmesi (orta) | KS | "yalnız" kalktı, AEA/İngiliz/Alman serbest dolaşım kapsamı eklendi; Alman vatandaşının sıradan eşi için nereye bakılacağı yazılmadı (aynı konuda es-icin kartı §28'i anlatıyor ama çapraz atıf yok) |
| 30 | ab-vatandasi: "yaşam ortağı" (orta) | K | "kayıtlı hayat ortağı (Lebenspartner)"; §1 Abs. 2 Nr. 2 |
| 31 | ab-vatandasi: hak şartı (orta) | K | özet/adım 1: "serbest dolaşım hakkı olan" (küçük kalan, bkz. kart) |
| 32 | yurt-disi: kalıcı nedenle çıkış (orta) | K | özet/altyazı/adım 1; §51 Abs. 1 Nr. 6 |
| 33 | yurt-disi: askerlik notu (küçük) | K | "yalnızca kendi ülkendeki yasal askerlik görevi yüzünden …" |

Oturum toplamı: K 30, KS 4 (C2, 3, 16, 29), A 1 (24).

### Konu "resmi" (23 alt madde; ilk raporun "1 ciddi + 11 orta + 12 küçük" sayısı kart başına gruplanmıştı)
| Kart | İlk bulgu (derece) | Durum | Kanıt cümlesi |
|---|---|---|---|
| adres-kaydi | konut veren, gün sayımı (küçük) | K | başlık "konut verenden (Wohnungsgeber)"; adım 1 "Eve girişten sonraki iki hafta içinde" |
| adres-kayit-belgesi | "nach dem Auszug", ilk cümle, Meldebehörde notu (küçük) | K | özet: "evden çıktıktan sonraki iki hafta içinde Meldebehörde'de (adı şehre göre değişir) Abmeldung"; yazılı belge ücreti kaynakta yok, dokunulmadı (kabul) |
| vergi-kimlik | altyazı "yalnızca mektupla", "giriş formu" (orta) | K | altyazı: "Bulamazsan BZSt'den iste; numara yalnızca mektupla bildirilir."; adım 2 "BZSt'nin çevrim içi formuyla, mektupla ya da BZSt Online Portal" |
| sosyal-guvenlik | ilk cümle, ad, emir kipi (küçük) | K | başlık "(Versicherungsnummer, emeklilik sigortası numarası)"; adım 1 "sunmak zorunda değilsin" |
| online-kimlik | "kartsız", claim 6 (küçük) | K | adım 4 "kart kullanmak istemiyorsan ELSTER sertifikalı BundID'yi kullanabilirsin, BundID'ye eID/eAT doğrulamasıyla da girilebilir"; claim 6 artık 095 quote'una bağlı |
| apostil | B1 Türk/Alman temsilcilik çevirisi (orta) | K | documents: "Türk diplomatik ve konsüler temsilciliklerinin düzenlediği belgeler hariç"; canlı "Urkunden türkischer diplomatischer oder konsularischer Vertretungen" |
| apostil | B2 tercüme sorusu dar (orta) | KS | özet/adım 6 "evlenme için Standesamt'a bildirimde Almanca olmayan belgelere çeviri eklenmesi beklenir" eklendi; başka kullanım (diploma, mahkeme kararı) için kaynak yok, kart yalnız bu iki bağlamı söylüyor (kalan: küçük) |
| apostil | B3 mahkeme apostil makamı (küçük) | K | adım 3 + claim 15-16 |
| apostil | B4 "(örneğin avukat)" (küçük) | K | silindi |
| onayli-kopya | B1 BGB §129 istisnası (orta) | K | adım 4 "BGB §129 uyarınca resmî onay (öffentliche Beglaubigung) gerektiren imzalar kurumda onaylanmaz" |
| onayli-kopya | B2 federal çerçeve (orta) | K | özet: "Eyaletler bu yasanın yerine kendi idari usul yasasını koyduysa o yasa uygulanır; … eyalete ve şehre göre değişir" (kalan: claim 15 alıntısı kesik, bkz. kart) |
| onayli-kopya | B3 "soll nur" (küçük) | K | özet "imzayı kural olarak yalnızca …" |
| arac | başlık genel, her kurum katılmaz, 30 dk kapsamı (orta) | K | başlık "internetten (i-Kfz)"; özet "her kurum i-Kfz'ye katılmaz …"; 30 dk/10 gün kaynakta 5 akışta var (Neuwagen, Wiederzulassung, Umschreibung ±Halterwechsel, Tageszulassung) |
| dogum | başlık "nasıl", kann/wird (küçük) | K | altyazı "Bir ebeveynin izni varsa … resen verilebilir, ikisinin de varsa verilir (§33)"; §33 S. 1-2 ile birebir |
| evlilik | B1 Aile Cüzdanı çelişkisi (orta) | KS | iki ifade de yazıldı (artık tek yanlı değil), ama okuyucuya "Auswärtiges Amt sayfasının bir yerinde … başka yerinde" diye kaynak çelişkisi aktarılıyor (bkz. kart) |
| evlilik | B2 Anerkennungsbescheid (orta) | K | documents satırı eklendi; canlıda var |
| evlilik | B3 vatansız muafiyeti (küçük) | K | "yurt dışında olağan ikameti olan vatansızlara"; "muafiyet altı ay geçerlidir" (BGB §1309 birebir) |
| sabika | muafiyet, BundID, yasal temsilci (küçük) | K | maliyet: "Ücret muafiyeti (Gebührenbefreiung) için başvuru yapılabilir"; adım 4 BundID; not "yasal temsilcisi olan kişi adına temsilci başvurabilir" (BZRG §30 Abs. 1-2) |
| itiraz | B1 dava süresi, itiraz aşaması yoksa (CİDDİ) | K | timing/özet/adım 7/not: "İtiraz aşaması gerekmiyorsa iptal davası doğrudan işlemin bildiriminden sonra bir ay içinde açılır" (VwGO §74 Abs. 1 S. 2) |
| itiraz | B2 eyalet çerçevesi (orta) | KS | not: "Hangi işlemlerde itiraz aşaması bulunduğu ilgili yasaya bağlıdır." eyalet farkı açıkça söylenmedi (kaynak VwGO'da yok, editör yazmadı: kabul edilebilir) |
| itiraz | B3 elektronik biçim (orta) | K | VwVfG ikinci kaynak; "nitelikli elektronik imzalı elektronik belge … kurumun elektronik formu ve eID" (canlı §3a ile uyumlu) |
| itiraz | B4 VwGO kapsamı (orta) | KS | özet: "VwGO, uyuşmazlığı federal yasayla açıkça başka bir mahkemeye verilmiş alanlar için geçerli değildir" eklendi; hangi alanların bu gruba girdiği (vergi, sosyal yardım) okuyucuya anlaşılmıyor (kaynak yok; kalan: küçük) |
| itiraz | B5 bir yıl istisnaları (küçük) | K | "kural olarak bir yıl … mücbir sebeple imkânsızsa ya da bilgilendirme itiraz yolunun olmadığını söylemişse bu sınır uygulanmaz" |

Resmi toplamı: K 19, KS 4 (apostil B2, evlilik B1, itiraz B2, itiraz B4), A 0.

---

## 2. Yeni/kalan bulgular (kart kart)

Aşağıda yalnız bulgusu olan kartlar var. Listede olmayan 12 kart (mavi-kart-ab-sartlari, nitelikli-is-gucu-oturumu-ve-firsat-karti, ogrenci-oturumu-ve-calisma-hakki, oturum-izni-uzatma-ve-gecici-belge, is-degistirince-oturum-izni, serbest-calisan-oturumu, adres-kaydi-anmeldung-iki-hafta-konut-veren-onayi, adres-kayit-belgesi-meldebescheinigung-ve-abmeldung, vergi-kimlik-numarasi-steuer-id-bulma-ve-yeniden-talep, sosyal-guvenlik-numarasi-versicherungsnummer-ve-nachweis, online-kimlik-eid-eat-ausweisapp-ve-bundid, dogum-bildirimi-geburtsurkunde-ve-bebegin-oturum-izni): editör değişiklikleri kaynakla uyumlu, yeni hata yok.

### alman-vatandasligi-sartlari: orta
- Bulgu: Editörün eklediği "Bir suç nedeniyle ceza almış olmamalısın." (adım 5, claim 18) ve özetteki "ceza mahkûmiyetin yoksa" mutlak. Kanun kapsamı daha dar: küçük cezalar (≤90 Tagessatz para cezası, ≤3 ay şartlı ve bağışlanmış hapis, Jugendgericht tedbirleri) Einbürgerung'da sayılmaz. Kartın tek kaynağı §10 (§12a'ya atıf yok). Türk okuyucu küçük bir cezayla başvurmaktan vazgeçebilir.
- Kanıt: https://www.gesetze-im-internet.de/stag/__12a.html (canlı) "Bei der Einbürgerung bleiben außer Betracht: … 2. Verurteilungen zu Geldstrafe bis zu 90 Tagessätzen und 3. Verurteilungen zu Freiheitsstrafe bis zu drei Monaten, die zur Bewährung ausgesetzt und nach Ablauf der Bewährungszeit erlassen worden ist."
- Düzeltme: StAG §12a'yı `add_sources` ile al, kartın ikinci kaynağı yap; adım 5: "Ceza mahkûmiyetin olmamalı; para cezası 90 Tagessatz'a kadar, şartlı ve bağışlanmış 3 aya kadar hapis ve gençlik mahkemesi tedbirleri sayılmaz" (claim'li). Kaynak eklenmeyecekse mutlak cümleyi "kural olarak … mahkûmiyetin olmaması aranır" yap ve özetteki "ceza mahkûmiyetin yoksa"yı aynı kapsamla yumuşat.

### alman-vatandasligi-sartlari: küçük
- Bulgu: Adım 4 "1974 öncesi … geldiysen (ya da onların eşiysen) bu şart aranmaz" derken özetteki "(sosyal yardım almalarında kusurları yoksa)" koşulunu söylemiyor; kanunda "nicht zu vertreten hat" yalnız bu gruba bağlı. Ayrıca "birlikte gelen eşleri" kanunda "im zeitlichen Zusammenhang nachgezogen" (zamansal bağlantıyla sonradan gelen eş); DDR Vertragsarbeitnehmer (13.06.1990) ayağı yok.
- Kanıt: https://www.gesetze-im-internet.de/stag/__10.html "oder als dessen Ehegatte im zeitlichen Zusammenhang nachgezogen ist und die Inanspruchnahme von Leistungen nach dem Zweiten oder Zwölften Buch Sozialgesetzbuch nicht zu vertreten hat"
- Düzeltme: Adım 4'e "sosyal yardım almada kusurun yoksa" ekle; "birlikte gelen" yerine "sonradan yanına gelen".

### oturum-belgesi-ucretleri: orta (açık, ilk bulgunun devamı)
- Bulgu: Ortaklık Hukuku kapsamındaki Türk okuyucu için ücretin farklı olduğu bu kartta yok; 100/93/96 Euro'yu kendine uygular. Editör üçüncü kaynak (048) sınırı yüzünden yazmadı; neden doğru ama risk duruyor (46 Euro yerine 100 Euro hazırlar, ya da kartı kendisi için geçerli sanır).
- Kanıt: https://www.gesetze-im-internet.de/aufenthv/__52a.html "Für Assoziationsberechtigte sind die §§ 44 bis 50 mit der Maßgabe anzuwenden, dass … eine Gebühr in Höhe der für die Ausstellung von Personalausweisen an Deutsche erhobenen Gebühr zu erheben ist."
- Düzeltme: İki yoldan biri: (a) 047 (§45c, 67 Euro) içeriğini ayrı bir "yeniden düzenleme (Neuausstellung) ücreti" kartına taşı, bu karta 046 + 048 koy ve "Ortaklık Hukuku kapsamındakiler için ücret farklıdır" cümlesini ekle; (b) kabul et ve Bağlantılar'a ortaklik kartının adresini koyma (zaten dizinde) — derece orta kalır, karar orkestratörde.

### turk-vatandasi-ulusal-vize-basvurusu: küçük
- Bulgu: Editörün eklediği "yabancı meslek yeterliliğinin tanınması için tamamlama eğitimi (Anpassungsmaßnahme)" açıklaması kartın kaynaklarında (041, 043) yok; claim 11'in quote'u yalnız "Anpassungsmaßnahme: je nach Auslandsvertretung zwischen 2-9 Monaten" diyor, açıklamayı kanıtlamıyor. Açıklama içerik olarak makul (canlı §16d bağlamı: Anerkennung ausländischer Berufsqualifikationen) ama karta atanmış kaynakla desteklenmiyor.
- Kanıt: https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2729790-2729790 "Anpassungsmaßnahme: je nach Auslandsvertretung zwischen 2-9 Monaten" (tanım yok)
- Düzeltme: Açıklamayı sil, yalnız "Anpassungsmaßnahme (meslek yeterliliğinin tanınmasına bağlı kategori)" gibi kaynakta olmayan hiçbir şey ekleme; ya da §16d metnini ikinci kaynak yapıp claim ekle (043 yerine tam yasa 035 kartın kaynağı olamıyor: kaynak sayısı 2).

### oturum-belgesi-turleri: küçük
- Bulgu: Özet "… oturum hakkın varsa genel belge zorunluluğu uygulanmaz. Yine de … Aufenthaltserlaubnis ile belgelemen gerekir" diye art arda iki zıt cümle; kaynağa sadık ama okuyucu için kaba. Özet 6 cümle (kural 2–5).
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__4.html "Ein Ausländer, dem nach dem Assoziationsabkommen EWG/Türkei ein Aufenthaltsrecht zusteht, ist verpflichtet, das Bestehen des Aufenthaltsrechts durch den Besitz einer Aufenthaltserlaubnis nachzuweisen"
- Düzeltme: "AB hukuku ya da yönetmelik başka türlü belirlemişse belge gerekmez. AB–Türkiye Ortaklık Anlaşması'ndan oturum hakkın varsa (Niederlassungserlaubnis ya da AB uzun süreli oturum iznin yoksa) bu hakkı Aufenthaltserlaubnis ile belgelemen gerekir." ve belge türleri cümlesini kısalt.

### es-icin-aile-birlesimi-vizesi: küçük
- Bulgu: (a) Merkblatt'ta "falls zutreffend Anerkennung für den deutschen Rechtsbereich" (yabancı boşanmanın Almanya'da tanınması) var; kart boşanma kararını yazıp tanıma belgesini atlıyor, oysa resmi/evlilik kartı aynı belgeyi (Anerkennungsbescheid) zorunlu sayıyor: konular arası boşluk. (b) Nüfus Kayıt Örneği için "orijinal ve Almanca çeviri" yazıyor; resmi/apostil kartı aynı belgeyi "apostil ve yeminli tercümeyle tanınır" diyor; konsolosluk vizesi (Merkblatt apostil istemiyor) ile Alman makamları (apostil) ayrımı hiçbir kartta açık değil. (c) Bağlantı 2 (aufenthg_2004/__30.html) kartın kaynağı değil (038 kaynak listesinden çıktı); dizinde var, sorun yok ama kart–bağlantı uyumsuz.
- Kanıt: https://tuerkei.diplo.de/tr-de/service/05-visaeinreise/2728584-2728584 "falls zutreffend Anerkennung für den deutschen Rechtsbereich"
- Düzeltme: documents "Varsa önceki evliliklerin boşanma kararları … ve Almanya'da tanındığını gösteren belge" ekle (aynı claim); bağlantı 2'yi §30 yerine kartın kaynağına (035 tam yasa) çevir ya da 039'un tek bağlantısıyla bırak.

### yerlesme-izni-sartlari: küçük
- Bulgu: Özetin ilk cümlesi şartları söylüyor, 2. cümle "Yerleşme izni süresiz …", 3. cümle aynı şartları (5 yıl, 60 ay …) bir daha sayıyor; tekrar ve 840 karakter. "İşe özel gerekli izinler" kanunda "sonstige für eine dauernde Ausübung seiner Erwerbstätigkeit erforderliche Erlaubnisse"; "işe özel" biraz dar.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__9.html "er im Besitz der sonstigen für eine dauernde Ausübung seiner Erwerbstätigkeit erforderlichen Erlaubnisse ist"
- Düzeltme: İlk cümleden sonra "Genel kuralda (§ 9) şunlar aranır:" cümlesindeki tekrarlanan sayımı kısalt; "işe özel" yerine "çalışmak için gerekli diğer izinler".

### ortaklik-hukuku-oturum-belgesi: küçük
- Bulgu: Rule 6: ücret tarihe duyarlı ama "güncel tarife" ibaresi yok. Özette 24 yaş altı kuralı iki kez (2. ve 3. cümle) tekrar ediyor.
- Kanıt: https://www.gesetze-im-internet.de/pauswgebv/__1.html "46 Euro in allen anderen Fällen." (maddede yıl yok)
- Düzeltme: maliyet ve özete "Güncel tarifeye göre" ekle; 3. cümleyi sil.

### ab-vatandasi-turk-aile-uyesi-oturum-karti: küçük
- Bulgu: Claim 9'un quote'u "Freizügigkeitsberechtigten Familienangehörigen" (aile üyesinin serbest dolaşım hakkı) diyor; özet/adım 1 hakkı "serbest dolaşım hakkı olan bir AB vatandaşının" diye AB vatandaşına bağlıyor. Anlam yakın ama claim–kart tam örtüşmüyor. Alman vatandaşının sıradan eşi (kartın dışında kaldığı) okuyucuya nereye bakacağı söylenmiyor.
- Kanıt: https://www.gesetze-im-internet.de/freiz_gg_eu_2004/__5.html "Freizügigkeitsberechtigten Familienangehörigen, die nicht Unionsbürger sind, wird von Amts wegen innerhalb von sechs Monaten … eine Aufenthaltskarte für Familienangehörige von Unionsbürgern ausgestellt"
- Düzeltme: "Kart, serbest dolaşım hakkı olan (freizügigkeitsberechtigt) aile üyesine verilir" (claim ile aynı); Alman vatandaşının eşi için "oturum belgesi eş birleşimi kuralları (§ 28) çerçevesinde alınır; bkz. eş birleşimi kartı" cümlesi 035'ten ancak 3. kaynak olur → ya cümleyi yazma ya es-icin kartına yönlendiren Bağlantı koy.

### oturum-izninin-yurt-disinda-kalinca-sona-ermesi: küçük
- Bulgu: (a) "Kalıcı bir nedenle (ör. taşınma)" örneği kaynakta yok (kaynak yalnız "aus einem seiner Natur nach nicht vorübergehenden Grunde"). (b) 15 yıllık Niederlassungserlaubnis istisnası §51 Abs. 2'de Nr. 6 ve 7'nin ikisini birden kapsıyor; özet 4. cümlesi "bu nedenle" diyor, hangi nedene bağlı olduğu belirsiz. (c) Vize cümlesi kaynakta "Nummern 6 und 7" (kalıcı çıkış ve altı ay) ikisini kapsıyor; kart yalnız "altı ay kuralı" diyor.
- Kanıt: https://www.gesetze-im-internet.de/aufenthg_2004/__51.html "erlöschen nicht nach Absatz 1 Nr. 6 und 7, wenn deren Lebensunterhalt gesichert ist"
- Düzeltme: "(ör. taşınma)" sil; 4. cümleye "kalıcı çıkış ve altı ay kuralı nedeniyle" yaz.

### resmi: turkiye-belgesi-almanyada-apostil-ve-yeminli-tercume: küçük
- Bulgu: (a) documents satırı "Apostilli belge (Formül A, B ve C, … hariç)" okunaksız: apostil *gereken* belge demek istiyor. (b) Başlıktaki tercüme sorusu yalnız Nüfus Kayıt Örneği ve evlenme bildirimi için cevaplanıyor; diploma/mahkeme kararı gibi diğer belgeler için kaynak yok, kart bunu söylemiyor (okuyucu "tercüme gerekmez" sanabilir).
- Kanıt: https://tuerkei.diplo.de/tr-de/service/1513838-1513838 "Fremdsprachige Urkunden und Unterlagen sollten mit einer Übersetzung versehen sein." (kaynakta bağlam: Eheschließung in Deutschland)
- Düzeltme: documents "Apostil gereken belge (… bunlar apostilden muaf)" yaz; özete "Çeviri kuralı kaynakta yalnız Nüfus Kayıt Örneği ve evlenme bildirimi için yazıyor" yazma (havale olur): bunun yerine başlığı "… ve yeminli tercüme (Nüfus Kayıt Örneği, evlenme bildirimi) …" diye daralt.

### resmi: onayli-kopya-beglaubigung-noter-ve-kurum-yetkisi: küçük
- Bulgu: Claim 15'in quote'u 200 karakterde kesilmiş ("… landesrechtlich durch ein"); eyalet kendi idari usul yasasıyla düzenlediyse iddiasının kilit kısmı ("Verwaltungsverfahrensgesetz geregelt ist") alıntıda yok. Script geçer, anlam kanıtı eksik.
- Kanıt: https://www.gesetze-im-internet.de/vwvfg/BJNR012530976.html "Für die Ausführung von Bundesrecht durch die Länder gilt dieses Gesetz nicht, soweit die öffentlich-rechtliche Verwaltungstätigkeit der Behörden landesrechtlich durch ein Verwaltungsverfahrensgesetz geregelt ist"
- Düzeltme: quote'u "…soweit die öffentlich-rechtliche Verwaltungstätigkeit der Behörden landesrechtlich durch ein Verwaltungsverfahrensgesetz geregelt ist" (≤200) biçimine kısalt (başa "Für die Ausführung von Bundesrecht durch die Länder gilt dieses Gesetz nicht," sığmıyorsa başı at).

### resmi: arac-kaydi-i-kfz-evb-hu-ve-kfz-steuer-sepa: küçük
- Bulgu: Altyazı ve özetin başındaki "Burada internetten kayıt (i-Kfz) anlatılır" okuyucuya yönelik sayfa-üst dili ("bu kart/burada anlatılır" türü); başlık zaten "internetten (i-Kfz)" diyor, cümle gereksiz ve altyazıda yer harcıyor.
- Kanıt: kart özeti: "Burada internetten kayıt (i-Kfz) anlatılır: araç kaydı, tüm kayıt işleri gibi …" (ortak-kurallar §7: "bu kart" gibi sistem dili yasağı)
- Düzeltme: "Burada … anlatılır" ifadelerini sil; altyazı: "Portal yerel kayıt kurumuna bağlıdır; her kurum katılmaz. Gerekenler: eVB, duruma göre geçerli HU ve SEPA mandası."

### resmi: almanyada-evlilik-ehefahigkeitszeugnis-ve-turkiyedeki-evlilik: küçük
- Bulgu: Not alanına kaynağın iç çelişkisi okuyucuya yazılmış: "Auswärtiges Amt sayfasının bir yerinde Almanya'nın bunu tanımadığı, başka yerinde ise … ancak apostil ve yeminli tercümeyle tanındığı yazıyor". Bu, süreç/kaynak notu tonunda (ortak-kurallar §7); okuyucu için kesin bilgi değil. Ayrıca "uluslararası aile cüzdanı" ifadesi kaynakta ("internationales Familienbuch") var, sorun yok.
- Kanıt: https://tuerkei.diplo.de/tr-de/service/1513838-1513838 "Dieses Familienbuch wird durch die Bundesrepublik Deutschland jedoch nicht anerkannt." ve "so dass die Familienbücher in Deutschland nur mit Apostille (s.u.) und Übersetzung durch einen vereidigten Übersetzer anerkannt werden."
- Düzeltme: "Aile Cüzdanı, Almanya'nın katılmadığı bir sözleşmeye dayandığı için doğrudan kabul edilmez; en iyi ihtimalle apostil ve yeminli tercümeyle kabul edilir. Evlilik kanıtı olarak Formül B kullanılır." (iki claim de kalır, sayfa adı ve "bir yerinde/başka yerinde" gider).

### resmi: sabika-kaydi-fuhrungszeugnis-basvuru-ucret-dijital-ve-avrupa-belgesi: küçük
- Bulgu: Maliyet alanındaki "başvuruda muafiyet nedeninin kanıtı yüklenir" ifadesi kaynakta çevrim içi başvuru bölümünde ("Nachweis … hochzuladen"); Meldebehörde yolunda yükleme yok. Kart yolu ayırmıyor.
- Kanıt: https://www.bundesjustizamt.de/DE/Themen/ZentraleRegister/Fuehrungszeugnis/Fuehrungszeugnis_node.html "Sie einen Antrag auf Gebührenbefreiung stellen wollen. Hier ist ein Nachweis über das Vorliegen eines Grundes für die Gebührenbefreiung zu erbringen."
- Düzeltme: "Çevrim içi başvuruda muafiyet nedeninin kanıtı yüklenir." yaz.

### resmi: resmi-yaziya-itiraz-widerspruch-sure-ve-sonraki-yol: küçük
- Bulgu: (a) Özet 1139 karakter ve yaklaşık 8 cümle (kural 2–5 cümle); elektronik biçim, bir yıl istisnaları, itiraz aşaması, VwGO kapsamı tek paragrafta. (b) "VwGO, uyuşmazlığı federal yasayla açıkça başka bir mahkemeye verilmiş alanlar için geçerli değildir" cümlesi okuyucuya hangi yazının (vergi, sosyal yardım) kapsam dışı kalabileceğini söylemiyor; kaynak yok, bu yüzden "yazıdaki itiraz yolu bilgisine göre hareket et" (adım 1 zaten) yeterli kabul edilebilir.
- Kanıt: https://www.gesetze-im-internet.de/vwgo/BJNR000170960.html "soweit die Streitigkeiten nicht durch Bundesgesetz einem anderen Gericht ausdrücklich zugewiesen sind."
- Düzeltme: Özeti 5 cümleye indir (süre, biçim, bilgilendirme yoksa bir yıl, itiraz aşaması yoksa dava süresi, VwGO kapsamı); elektronik biçimin ayrıntısını adım 3'e bırak; kapsam cümlesine "Yazındaki itiraz yolu bilgisi (Rechtsbehelfsbelehrung) hangi yolun açık olduğunu gösterir" ekle (§58 claim'li, kaynak aynı).

### capraz-link-etiketi: küçük
- Bulgu: Etiketler artık işleme göre; ama oturum-izni-uzatma `__81.html` bağlantısı "Başvur" etiketini taşıyor, oysa adres yasa maddesi (başvuru sayfası değil). turk-vatandasi "Randevu al" bağlantısı randevu sistemi değil bilgi sayfası (iDATA kaydı anlatan Auswärtiges Amt sayfası). resmi konusunda 22 bağlantı hâlâ "Bilgi al".
- Kanıt: Bağlantılar.oturum.jsonl: oturum-izni-uzatma-ve-gecici-belge order 1 label "Başvur" url …/aufenthg_2004/__81.html
- Düzeltme: "Başvur" → "Yasa metni: § 81"; "Randevu al" → "Randevu ve ücret bilgisi"; zorunlu değil.

---

## 3. Yeni kaynaklar (204, 205) ve kart–claim–kaynak tutarlılığı
- ortaklik-hukuku-oturum-belgesi: kaynaklar 048 + 204; 029 çıkarıldı; ona dayanan claim'ler karttan kalktı (claims: 6 satır, 048/204 dışında kaynak yok). Bağlantılar 2 satır (048, 204) kaynak dizininde. Kart metni ile claim 7-9 birebir. İyi.
- mavi-kart-ab-sartlari: kaynaklar 033 + 205; claim 11 "101 400 Euro jährlich" quote'u 205'te var (canlı aynı); Bağlantılar 2 satır dizinde. İyi. (valid_until 2026-12-31.)
- es-icin-aile-birlesimi-vizesi: 038 çıkarıldı, 035 (tam yasa, 641 465 karakter) kaynak oldu; § 28/§ 30 claim'lerinin quote'ları 035'te var. Dikkat: iki claim (4 ve 5) quote'u 035'te iki yerde geçiyor (§29 Abs. 5 konut şartı için, §30 Abs. 1 S. 3 Nr. 5 dil için); anlam §30 için doğru ama quote tek başına bunu ayırt etmiyor. Öneri: quote'a "Satz 1 Nummer 2 ist … unbeachtlich, wenn" başlangıcını ekle. Bağlantı 2 (§30) kartın kaynağı değil.
- is-degistirince-oturum-izni: tek kaynak 035; bağlantılar 3 (033, 034, 035 adresleri), kaynak yalnız 035. Dizinde var; tutarlılık için bağlantıları kaynak listesine hizalamak önerilir (küçük, yukarıda ayrıca sayılmadı).
- ogrenci-oturumu-ve-calisma-hakki: 037 + 035; claim 14 doğru.
- Kart başına ≤2 kaynak: 27/27 kart uygun (alman-vatandasligi, is-degistirince, serbest-calisan, yurt-disi 1 kaynak; resto 2).

## 4. Dönüş satırı
`{"report":"C:\\temp_private\\corteqs\\0000_newera\\ulke\\DE\\_is\\yazar\\out\\denetim_g0b_dar.md","cards":27,"serious":0,"medium":2,"minor":15,"live_checked":[...],"not_checked":[...]}`
