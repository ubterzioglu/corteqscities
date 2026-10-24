# CorteQS Özellik Kütüphanesi ve Şehir Zekâ Motoru Stratejisi

Oct 14, 2026 · @Someone

## Yönetici özeti

**Karar önerisi: Staging'i "Şehir Zekâ Motoru" etrafında büyütelim. Lovable CORTEQS+ ise bu motorun önüne dizilecek özelliklerin kütüphanesi olsun.** Lovable kodunda 6 üst menü ve 19 alt sekme altında 44 özellik var. Bunların 26'sı Staging'de yok, 15'i kısmen var. Lovable kurguda ve diaspora sezgisinde çok güçlü; ancak verisi büyük ölçüde demo, AI araması da veritabanına bağlı değil. Staging'in gücü ise gerçek, kaynaklı şehir verisi, güvenlik ve yasal olgunluk.

Bir şehri araştıran kişi ya orada yaşıyordur ya da oraya taşınmayı düşünüyordur. Bu iki niyeti ayırt eden bir motor; aramayı, profili ve davranışı hizmete, fırsata, indirime, etkinliğe ve ağa çevirebilir. CorteQS'in benzersiz verisi de burada oluşur: kimin nereden nereye taşındığı, ne aradığı ve neyi çözdüğü.

**İlk üç hamle:**

1. **Diaspora-first kimlik:** Onboarding'e rol, ikamet şehri ve "burada mı yaşıyorsun, taşınmayı mı düşünüyorsun?" sorusu eklensin. Telefon ve beyan ile erişim katmanları kurulsun; Köprü ortak alan olsun.
2. **Şehir sayfası + Taşınma Motoru + uzman talebi tek akış:** Lovable'daki 7 sekmeli Taşınma Motoru Staging'in 49 şehir verisi ve hizmet dizini üzerine kurulsun; araştırmalar sunucuya kaydedilsin.
3. **Erken nakit ve erken veri:** Kurucu 1000 (ön kayıt + manuel fatura) ve Evim-Evin anketi soft launch'ta açılsın.

Cadde, cafe'ler, etkinlikler ve Çarşı ikinci dalgada topluluk katmanını kurar. Reklam, AI Twin ve oyunlar trafik oluştuktan sonra gelir.

## Lovable CORTEQS+ menü haritası

Lovable'ın üst menüsü, gurbetçi hayatının altı temel ihtiyacına göre kurulmuş: konuşmak, alıp satmak, kazanmak, ait olmak, görünmek ve planlamak. Menü sırası (Cadde → Çarşı → İş → Sosyal → Kampanyalar → Araçlar) bilinçli olarak sosyali ticaretten önce koyuyor.

&#91;embedded content: Lovable CORTEQS+ üst menü · 6 menü, 19 alt sekme\]

Yeni yolculuk şehir verisiyle başlayacağı için, Lovable'da en sağda duran Araçlar menüsü (Taşınma Motoru, Harita, Rehberler) Staging'de öne alınmalı. Staging'in mevcut "Şehir rehberi" ve "Keşfet" sekmeleri bu kapının doğal yeri. Cadde ve Çarşı ise ikinci dalgada bu kapının etrafını doldurur.

## Tam özellik listesi: Lovable kütüphanesi vs Staging

Lovable CORTEQS+ projesinin kodundan çıkan 44 özellik aşağıda. Bunların 26'sı Staging'de yok, 15'i kısmen var. 3 alanda ise Staging önde: şehir rehberleri, kurulu back office ve Türkiye ile bağın. Lovable tarafındaki verilerin çoğu demo/mock; değerli olan kurgu, kurallar ve akışlar.

**Değer sütunu:** G = doğrudan gelir yaratır, V = birinci parti veri yaratır, A = ağ etkisi / tutundurma.

### Cadde (sosyal omurga)

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 1 | Cadde akışı: kıta/ülke/şehir çoklu filtre, @Şehir @Ülke etiketli paylaşım, foto/video | "Şehrimde ne oluyor, kim ne soruyor" | 49 şehir sohbeti (moderasyonlu) | Kısmi | A, V |
| 2 | TR kullanıcı kuralı: +90 telefon veya ülke=Türkiye ise yalnız @Türkiye, Köprü ve Global; yurt dışı paylaşımına yorum için bağlantı (connect) şart | Diaspora alanının diaspora olarak kalması | Yok | Yok | A |
| 3 | Dinamik global eşik: akış hızı ≥ 1 post/sn olunca sadece yeterli beğeni alanlar görünür | Gürültüsüz global akış | Yok | Yok | A |
| 4 | İlgi alanı hedefleme (bireysel ilgi alanları akışı yeniden sıralar) | "Bana uygun içerik" | Yok | Yok | V, G (reklam) |
| 5 | Story bandı + kişinin şehrinde yerel saat ve güneş/ay simgesi | Dağınık saat dilimlerinde bağ hissi | Yok | Yok | A |
| 6 | Cafe'ler: 2 saatlik geçici odalar (Premium 4 sa), günde en çok 3 açma; serbest/koşullu giriş, giriş sorusu, sahip onayı; Relocation ve Expo cafe; tema (IT, Hekimler, Profesyoneller…), kapasite barı | Aynı meslekten/şehirden insanla hemen buluşmak | Yok | Yok | A, G (Premium, Expo sponsoru) |
| 7 | Diasporada Ara (Bireysel/Profesyonel/İşletme/Kuruluş/Çarşı) | "Buralarda kim var?" | Üyeleri keşfet + dizin ayrı | Kısmi | V |
| 8 | Takip + "Tanıyor olabilirsin" (ülke, şehir, meslek, okul benzerliği) | Okul/meslek bağıyla ağ kurmak | Yok | Yok | A, V |
| 9 | Billboard ve akış içi sponsorlu kart (premium danışman, işletme kuponu, öne çıkan etkinlik, THY) | İndirim ve fırsatlar | Yok | Yok | G |
| 10 | Çarşı Global Ticker + kibar ilan CTA şeridi | Pazar yerine sürekli trafik | Yok | Yok | G |
| 11 | Cadde profil kapısı (profil tamamlanmadan sınırlı erişim) | Güvenli, gerçek kişiler | Giriş zorunlu | Kısmi | V |

### Çarşı (pazar yeri)

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 12 | Video hero'lu landing; ülke → şehir kademeli filtre; 14 kategori: ikinci el, oda, ev, ders, hizmet, araç, bilet, iş, takas, bedava, pet bakıcısı, depo, garaj, son dakika ücretsiz (geri sayımlı) | Taşınırken al/sat/devret, güvenilir Türk komşu | Keşfet: hizmet, market, iş, konut, ikinci el, rehber + sepet | Kısmi | G, V |
| 13 | Profil panelinden 5 ilan limiti, profilde vitrin | Kişiye bağlı güven | "İlan ekle" | Kısmi | G (limit aşımı) |
| 14 | Evim-Evin: ev takası ön kayıt anketi (niyet + en çok 3 ev, dönem: yaz, bayram, Noel…); havuz sayacı 50 evin altında gizli | Tatilde/memlekette ev değişimi | Yok | Yok | V (talep verisi) |

### İş

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 15 | Danışmanlar: kategori taksonomisi, fiyat etiketi, randevu, canlı görüşme, gönüllü mentör | Dilini konuşan, güvenilir uzman | 1.280 kaynaklı (OSM) işletme + ilan bazlı uzman hizmetleri | Kısmi | G |
| 16 | AI Twin: danışman ikizi; admin onayı + RAG eğitimi; AI Twin gelirinden %10 platform kesintisi | 7/24 ön görüşme | Yok (bilinçli) | Yok | G |
| 17 | İşletmeler: profil, kupon (ücretsiz 1 / Premium sınırsız), franchise vitrini | İndirim, Türk işletmesi bulmak | Dizin profilini sahiplenme | Kısmi | G |
| 18 | Venture Hub (yatırımcı + girişim vitrini) | Yurt dışında iş kurmak, fon bulmak | Yok | Yok | G (ileride) |
| 19 | İş İlanları + Kariyer sayfası | İş bulmak, eş için iş | Keşfet'te iş ilanı türü | Kısmi | G, V |
| 20 | Kuruluşlar: dernek profili, etkinlik, radyo şarkı isteği; Premium'da aidat tahsilatı ve üye paneli | Derneklerin dijitalleşmesi | Yok | Yok | G, A |

### Sosyal

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 21 | Kişiler: diaspora rehberi + kişi detay sayfası | Kimlerle aynı yoldan geçtim? | Üyeleri keşfet | Kısmi | A, V |
| 22 | Etkinlikler: biletli, canlı rozeti, boost, öne çıkan vitrin, etkinlik paneli | Bayram, konser, network | Yok | Yok | G, A |
| 23 | Dijital Gruplar: WhatsApp grup dizini + grup landing sayfası + moderasyon | Mevcut grupları bulmak | "Topluluğunu getir" | Kısmi | A |
| 24 | V/Blogger ekosistemi (detay sayfası, metrikler) | Diasporadan gerçek deneyim | Yok | Yok | A, G (işbirliği) |
| 25 | Global Medya: yerel + uluslararası haber, hava durumu, diaspora dergi/gazete/kitap, blog linkleri, şehirler arası kelime araması | Şehrimde ve diasporada ne oluyor | Şehir rehberi (haber yok) | Kısmi | A |

### Kampanyalar

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 26 | Liderlik tablosu ve ödüller (CQ Puan; kişi/şehir/ülke) | Görünürlük ve ait olma | Yok | Yok | A |
| 27 | Blogger yarışması ($1.000) | İçerik üreticisini çekmek | Yok | Yok | A, V |
| 28 | Vlogger yarışması | Video içerik | Yok | Yok | A |
| 29 | Kurucu 1000: ön kayıt + admin onayı (99 €, €399 Görünürlük Paketi) | Erken destekçi olmak | Yok | Yok | G |
| 30 | Oyunlar (Diaspora Olimpiyatları, Memleket Quiz, Cadde Savaşları) — Lovable'da da "Yakında" | Eğlence, memleket bağı | Yok | Yok | A |
| 31 | 19 Mayıs kampanyası + dünya haritası | Ortak milli an | Yok | Yok | A, V |

### Araçlar

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 32 | Taşınma Motoru: anket (hedef ülke/şehir, aile, eş mesleği, çocuk yaşları, meslek, tecrübe, ücretli/gönüllü mentör) → 7 sekme: checklist + maliyet, gerekli belgeler (7 ülkeye özel), yaşam masrafı + hane geliri, iş/danışman/dernek/WhatsApp-alumni/blog, okullar, Hoşgeldin Paketi, dökümanlarım; AI sohbet | Taşınma kararını ve planını tek yerde yapmak | /yerlesim + rehberler | Kısmi | G, V (en yüksek) |
| 33 | Hoşgeldin Paketi teklif formu (uçak, transfer, araç) | İlk gün lojistiği | "Türkiye ile bağın" talep akışı (farklı ama benzer) | Kısmi | G |
| 34 | Haritada Ara (OSM) | Yakınımda ne var | Keşfet harita/şehir | Kısmi | V |
| 35 | Araçlar dizini (3 grup, 14 araç, Aktif/Yakında) | Ne yapabileceğimi görmek | Yok | Yok | — |
| 36 | Rehberler: 8 konu + 8 ülkeye özel "kritik ilk 3 adım" + uzman/harita CTA | İlk hafta ne yapmalıyım | 49 şehir rehberi + yerleşim rehberleri | Staging önde | V |
| 37 | Hastane randevusu (Türkçe konuşan hastaneler) | Dil engeli olmadan sağlık | Klinik dizini + "Türkçe hizmet" filtresi | Kısmi | G |
| 38 | Vize & doküman takibi (Yakında) | Son tarih kaçırmamak | Yok | Yok | V |

### Genel katman ve altyapı

| # | Özellik (Lovable) | Diaspora ihtiyacı | Staging karşılığı | Durum | Değer |
| --- | --- | --- | --- | --- | --- |
| 39 | Onboarding: 6 hesap türü + rol seçilince Kurucu 1000 kutusu | Kendini doğru tanıtmak | Rol seçimi yok | Yok | V, G |
| 40 | AI Arama + CorBot asistan | Tek kutudan her şeyi bulmak | Yok | Yok | V |
| 41 | Fiyatlandırma: Danışman/Kuruluş/İşletme × Freemium / Premium Pro (€10/ay, yıllık €8) / Kurucu 1000; bireysel ücretsiz | — | Online tahsilat kapalı | Yok | G |
| 42 | İlan ver & reklam (bölge, yaş, cinsiyet, meslek hedefleme) | — | Yok | Yok | G |
| 43 | Admin: genel bakış, gelir, elçi, V/Blogger, Hoşgeldin Paketi, WhatsApp, AI Twin başvuruları (çoğu mock) | — | Kurulu back office | Staging önde | — |
| 44 | — (Staging'e özgü) Türkiye ile bağın: 7 talep türü (ürün, hediye, sağlık, para, aile, mülk, ziyaret) | Memleketteki işleri uzaktan çözmek | Var | Staging önde | G, V |

**Koddan çıkan üç kritik not:**

1. Lovable'daki AI Arama veritabanına bağlı değil. Model, gerçekçi görünen sonuçları kendisi üretiyor; bu bir uydurma riski. Staging'in kaynaklı verisiyle beslenen araştırma (RAG) bu riski çözer.
2. Taşınma Motoru araştırmaları tarayıcıda (localStorage) tutuluyor; maliyet verisi sadece Almanya ve Hollanda için var. Yani en değerli veri şu an sunucuya hiç ulaşmıyor.
3. /admin rotasında sayfa seviyesinde rol kontrolü görünmüyor; ayrıca Kurucu 1000 kartında başlangıç tarihi "29 Ekim 2027" yazıyor (2026 olmalı mı?).

## Diaspora-first erişim, Köprü ve 'yurt dışı yaşam' profili

Platform önce yurt dışında yaşayanlar içindir; Türkiye'den gelen kullanıcı bu dünyaya Köprü üzerinden girer. Lovable'da bu kuralın temeli zaten var: +90 telefonlu ya da ülkesi Türkiye olan kullanıcı yalnızca @Türkiye, Köprü ve Global akışlarını görüyor; yurt dışındaki bir paylaşıma yorum yazmak için önce bağlantı istiyor. Staging'de ise Twilio ile telefon doğrulama kurulu. İki parça birleşince erişim modeli neredeyse hazır.

### Erişim katmanları

| Kullanıcı | Nasıl tanınır | Neyi görür | Nereye yazar |
| --- | --- | --- | --- |
| Diaspora sakini | Yabancı numara doğrulanmış + ikamet beyanı (Türkiye dışı) | Tüm ülke ve şehir akışları, şehir sohbetleri, cafe'ler | Kendi şehri, ülkesi, Köprü, Global |
| Taşınacak aday | Türkiye'de yaşıyor + hedef şehir seçmiş (Taşınma Motoru) | Köprü, hedef şehrin okuma modu, Relocation cafe | Köprü; hedef şehre bağlantı veya davetle |
| Türkiye'de yaşayan (aile, iş yapmak isteyen) | +90 numara veya ikamet Türkiye | @Türkiye, Köprü, Global | @Türkiye ve Köprü; yurt dışına yorum için bağlantı şart |
| Doğrulanmış hizmet veren / işletme | Başvuru + back office onayı | Hizmet bölgesi + Köprü | Hizmet bölgesi ve Köprü'de ilan ve yanıt |
| Şehir elçisi | Davet + onay | Kendi şehri (moderatör) | Şehir, duyuru, sabit mesaj |

**Dikkat:** Telefon ülke kodu tek başına ikamet kanıtı değildir. Türkiye'deki biri yabancı hat alabilir; yurt dışındaki biri +90 hattını kullanmaya devam edebilir. Karar birden fazla sinyalle verilmeli: numaranın ülke kodu, kullanıcının beyanı, konum tutarlılığı ve isteğe bağlı elçi ya da üye daveti. Yanlış sınıflanan kullanıcı için tek tıkla itiraz yolu olmalı.

### Köprü'nün rolü

Köprü, Türkiye ile diasporanın buluştuğu ortak alan ve platformun en güçlü dönüşüm noktası. Burada dört başlık konuşulur:

- **Taşınma soruları:** "Berlin'e taşınıyorum" sorusu yerleşik diasporaya ve mentörlere ulaşır.
- **İş ve yatırım:** Türkiye'den diasporaya satmak ya da diasporadan Türkiye'ye yatırım yapmak isteyenler buluşur.
- **Türkiye ile bağın:** aile desteği, mülk, sağlık ve hediye talepleri.
- **Danışman yanıtları:** Köprü'deki her soru bir danışman için potansiyel müşteri (ileride ücretli lead).

Çarşı Köprü dışında kalır (Lovable CKS kuralı), çünkü ilanlar yereldir.

### İş, iş bulma ve iş yapma: doğru konumlandırma

| Persona | İhtiyaç | Giriş noktası | Önerilen yol |
| --- | --- | --- | --- |
| Yerleşik diaspora, iş arıyor | Şehrinde iş, kariyer değişimi | İş → İş İlanları | Şehir filtreli ilanlar + meslek cafe'leri (ör. Berlin IT Cafe) + mentör |
| Taşınacak aday | Taşınmadan iş bulmak | Taşınma Motoru → İş sekmesi | Meslek eşleşmeli ilanlar + vize uygunluğu + CV/LinkedIn aktarımı (Staging'de var) |
| Eş / partner | İkinci kariyer | Taşınma Motoru (eş mesleği alanı) + Rehber | Eş için ilanlar + Staging'deki "eşinle kariyer" rehberi |
| Diasporada iş kurmak isteyen | Şirketleşme, ilk müşteri | Rehber "İş Kurma" → Danışman | Danışman + İşletme profili + Venture Hub |
| Türkiye'den diasporaya satan | Pazara erişim | Köprü → İşletme | İşletme profili + kupon + Expo cafe |
| Diasporadan Türkiye'ye yatırım | Güvenilir fırsat | Köprü → Venture Hub | Doğrulanmış girişim vitrini + yatırımcı odası |

### Yurt dışı yaşam profili (isteğe bağlı, farkı yaratan)

Bu alanlar zorunlu değil; ama her biri eşleştirme, mentörlük ve güven için güçlü bir sinyal. Her alanın görünürlüğü ayrı ayarlanmalı ve varsayılan gizli kalmalı (Staging'deki "varsayılan özel profil" ilkesi korunur).

| Alan | Örnek | Ne işe yarar |
| --- | --- | --- |
| Yaşadığı şehir ve kaç yıldır | Berlin'de 7 yıl | Yeni gelen (0–12 ay) ve yerleşik ayrımı; mentör adaylığı |
| Daha önce yaşadığı ülke ve şehirler | Önceden Londra, Dubai | Göç rotası verisi; "Londra'dan Berlin'e taşınanlar" eşleşmesi ve içeriği |
| Geliş nedeni | İş, eğitim, aile, girişim | Doğru hizmet ve içerik önerisi |
| Meslek ve sektör | Yazılım, sağlık | İş ilanı, meslek cafe'si, "Tanıyor olabilirsin" |
| Konuştuğu diller | TR, DE, EN | Hizmet veren eşleşmesi |
| Mezun olduğu okul | ODTÜ, Boğaziçi | Alumni grupları (Taşınma Motoru'nda zaten var) |
| Yardım edebileceği konular | Anmeldung, ev bulma, okul kaydı | Gönüllü mentör havuzu |
| Hane bilgisi (kaba) | Çocuklu aile | Okul, aile etkinliği ve indirim önerileri |

Profilde bu alanlar "Berlin'de 7 yıl · Önceden Londra" gibi kısa rozetler olarak görünür. Bir sonraki bölümdeki motorun en değerli girdileri de bunlar.

## Şehir Zekâ Motoru

Bir şehri araştıran kişi ya orada yaşıyordur ya da oraya taşınmayı düşünüyordur; motorun ilk işi bu ikisini ayırmak. Aynı "Berlin + vergi danışmanı" araması, taşınacak biri için bir taşınma planına ve vize danışmanına; yerleşik biri içinse mali müşavir indirimine ve bir network etkinliğine dönüşmeli.

&#91;embedded content: Şehir Zekâ Motoru · 5 sinyal, 5 aşama, öneri yüzeyleri\]

Motor beş aşamayı ayırır. Her aşama farklı bir gelir kapısıdır: Araştıran ve Taşınan danışman talebi ile Welcome Pack üretir; Yeni gelen Çarşı ve hizmet; Yerleşik kupon, etkinlik ve reklam; Türkiye'den bağlı olan ise Köprü ve Türkiye ile bağın talepleri.

### Nasıl kurulur (üç adımda)

1. **Kural tabanlı başla.** İlk sürümde makine öğrenmesi gerekmez. Aşamayı belirleyen kurallar yeterlidir: "ikamet Türkiye + hedef şehir seçili + tarih 3 ay içinde = Taşınan" ya da "ikamet Berlin + 8 ay = Yeni gelen". Lovable'daki ilgi alanı hedefleme ve "Tanıyor olabilirsin" benzerlik mantığı bu katmana taşınabilir.
2. **Tek olay şeması.** Arama, şehir sayfası görüntüleme, talep, kayıt ve katılım tek bir olay tablosuna yazılır. Motor bu tablodan beslenir; admin ekranı da şehir ve kategori bazında talep ısı haritasını buradan gösterir.
3. **Güçlü arama + dosya.** Arama Staging'in kaynaklı verisi, rehberler ve kullanıcının kendi Taşınma dosyası üzerinde çalışır (RAG). Kullanıcının kaydettiği her araştırma, belge listesi ve teklif "Dosyam"da toplanır. Böylece arama bir tek seferlik sorgu olmaktan çıkar, kişisel bir proje dosyasına dönüşür.

**İş değeri:** Hangi şehirde hangi hizmete talep var, kim ne zaman taşınıyor, hangi göç rotası büyüyor? Bu veri hem danışman ve işletmeye satılabilir (toplu, anonim içgörü) hem de arz toplamayı yönlendirir: talebin olduğu yere uzman getirilir.

## Gelir ve veri yaratan özelliklerin stratejik değerlendirmesi

En yüksek değeri, hem gelir hem veri üreten üç özellik taşıyor: Şehir ve Taşınma Motoru, doğrulanmış uzman ile talep akışı, ve Welcome Pack ile Türkiye ile bağın talepleri. İlk fazda nakit akışını Kurucu 1000 sağlar. Reklam ve billboard ise trafik oluşmadan değer üretmez.

Puanlar 1–5 arası, ekibin tartışmasına zemin olacak bir ilk tahmindir. Efor: S = 1–2 hafta, M = 3–6 hafta, L = 6 haftadan fazla.

| Özellik | Gelir modeli | Gelir (1–5) | Veri (1–5) | Efor | Staging'de temel | Karar |
| --- | --- | --- | --- | --- | --- | --- |
| Şehir Zekâ + Taşınma Motoru (sunucuda kayıtlı) | Danışmana nitelikli talep, Welcome Pack komisyonu, sponsorlu öneri | 5 | 5 | L | Kısmi (/yerlesim, rehberler) | Çekirdek, hemen başla |
| Doğrulanmış Türk uzman + talep/teklif + randevu | Premium Pro abonelik, talep ücreti, randevu komisyonu | 5 | 4 | M | Var (dizin + talep) | Çekirdek |
| Kurucu 1000 | Tek seferlik 99 € | 4 | 2 | S | Yok | Soft launch'ta ön kayıt + manuel fatura |
| Türkiye ile bağın (7 talep türü) | Ortak komisyonu (transfer, sağlık, lojistik) | 4 | 4 | M | Var | Ortaklarla bağla |
| Welcome Pack | Uçak, transfer, SIM, sigorta ortak komisyonu | 4 | 4 | M | Kısmi | Taşınma Motoru ile birlikte |
| Etkinlikler + bilet + boost | Bilet komisyonu, boost ücreti | 3 | 4 | M | Yok | Sosyal çekirdekle |
| Cadde + cafe'ler | Premium cafe süresi, Expo sponsoru, hedefli reklam | 3 | 5 | L | Yok (sohbet var) | Sosyal çekirdekle |
| Çarşı | İlan limiti aşımı, öne çıkarma | 2 | 4 | S–M | Kısmi | Erken; "taşınıyorum, satıyorum" sinyali çok değerli |
| İş ilanları + kariyer | İşveren ilan ücreti, öne çıkarma | 3 | 4 | M | Kısmi | 2. dalga |
| Billboard, hedefli reklam, kupon | CPM, sponsor (THY vb.), kupon ortaklığı | 4 | 3 | M | Yok | Trafik oluşunca |
| Kuruluş aidat + bilet | Premium + işlem ücreti | 3 | 3 | M | Yok | 2. dalga; dernekler kullanıcı getirir |
| Sağlık / hastane randevusu | Klinik talep ücreti | 4 | 3 | M | Kısmi | Özel nitelikli veri; GDPR/KVKK tasarımıyla |
| AI Twin | %10 kesinti + Premium şartı | 3 | 3 | L | Yok | RAG altyapısından sonra |
| Evim-Evin anketi | Yok (talep doğrulama) | 1 | 4 | S | Yok | Ucuz ve hızlı veri; erken aç |
| CQ Puan + liderlik | Dolaylı (tutundurma, davet) | 1 | 3 | M | Yok | 2. dalga |
| Blogger / Vlogger yarışmaları | Sponsor | 2 | 3 | S | Yok | İçerik açığını kapatmak için |
| Venture Hub | Üyelik, başarı ücreti | 3 | 2 | L | Yok | Uzun vade |
| Oyunlar | — | 1 | 2 | L | Yok | Lansman sonrası |

**Okuma:** Gelir ve veri puanı toplamı 8 ve üstü olan beş özellik ilk iki dalgayı oluşturuyor. Kurucu 1000 ve Evim-Evin ise düşük eforla erken nakit ve erken veri getiren iki hızlı kazanım.

## Geliştirme sıralaması

Sıralama tek bir mantığa dayanıyor: motorun besleneceği veri oluşmadan üstüne özellik kurulmaz. Bu yüzden ilk dalga kimlik ve erişim; ikinci dalga şehir çekirdeği; topluluk ve reklam ise trafik oluştuktan sonra geliyor.

&#91;embedded content: Geliştirme sıralaması · 4 dalga, 4 kapı\]

### Dalga bazında gerekçe

| Dalga | Neden şimdi | Bağımlılık | Lovable'dan ne taşınır |
| --- | --- | --- | --- |
| D0 Kimlik ve erişim | Her yeni üyenin aşaması bilinmezse motor kör kalır; soft launch'ta toplanan ilk veri en değerlisi | Staging auth + Twilio (hazır) | 6 rol onboarding, TR kullanıcı kuralı, Köprü, Kurucu 1000 kutusu, Evim-Evin şeması |
| D1 Şehir çekirdeği | Yeni yolculuğun çıkış noktası; SEO ve gelir burada başlar | D0 verisi + Staging şehir rehberleri ve dizin | Taşınma Motoru'nun 7 sekmesi, Rehberlerdeki "kritik ilk 3 adım", Hoşgeldin Paketi formu |
| D2 Topluluk | Kullanıcı geldikten sonra kalması için sebep gerekir | D1 trafiği + elçiler | Cadde kural seti (CKS), cafe mantığı, Çarşı kategorileri, etkinlik paneli |
| D3 Büyüme ve lansman | Reklam ve puan ekonomisi ancak trafikle değer üretir | D2 aktifliği + ödeme altyapısı | Billboard, kupon, CQ Puan seviyeleri, yarışmalar, AI Twin başvuru akışı |

Her dalgadaki her özellik üç parçayla "bitti" sayılır: kullanıcı ekranı, sahibinin paneli ve back office ekranı.

## Yedi şapka: her rolden öneriler

Yedi bakış açısı aynı sonuca çıkıyor: önce şehir verisi ve güven, sonra topluluk, en son reklam. Aşağıda her rolün ilk 90 günde sahiplenmesi gereken işler var.

| Şapka | Ana soru | İlk 90 gün önerisi |
| --- | --- | --- |
| **CTO** | Lovable'ın kurgusunu Staging'e nasıl taşırız? | Lovable'ın `migration-bundle/full_schema.sql` şemasını referans al; rol, cafe, Çarşı kategori ve Evim-Evin tablolarını Staging'in Postgres modeline uyarla. Taşınma araştırmalarını tarayıcıdan sunucuya al. AI aramayı model üretiminden çıkarıp Staging verisi üzerinde RAG'a çevir. Tek bir "olay" (event) şeması kur: arama, görüntüleme, talep, kayıt, katılım. |
| **CBDO** | Kimlerle ortaklık gelir getirir? | Welcome Pack ortakları (havayolu, transfer, SIM, sigorta), "Türkiye ile bağın" için transfer, lojistik ve sağlık ortakları. THY sponsorluğu Lovable'da zaten kurgulanmış. Her ortak için ölçülebilir komisyon ve takip linki. |
| **CMO** | Kullanıcıyı nereden ve nasıl getiririz? | SEO'yu şehir sayfaları üzerinden kur (Staging sunucu tarafı render ediyor, bu büyük avantaj). "Berlin'e taşınma rehberi" gibi niyet aramalarını hedefle. Kurucu 1000 ve 19 Mayıs kampanyası ile ilk dalga. Blogger yarışmasıyla içerik açığını kapat. |
| **CEO** | Neyi şimdi, neyi sonra yaparız? | Tek kuzey yıldızı metriği seç (aşağıda). 19 ülke yerine önce 5 yoğun şehirde derinlik (Berlin, Londra, Amsterdam, Dubai, Toronto). Lovable'ı dondur; ürün kütüphanesi ve tasarım referansı olarak kalsın. |
| **Community** | Boş odayı nasıl dolu gösteririz? | Her ilk şehirde 1 elçi + 3 mevcut WhatsApp grubu taşıma ("Topluluğunu getir"). Haftalık sabit cafe saati (ör. Perşembe 20:00 Berlin IT Cafe). Yeni gelenler için "İlk 30 gün" karşılama ritüeli. |
| **Marketplace** | Arz mı, talep mi önce? | Arz önce: her şehirde en çok aranan 5 kategoride (vize, emlak, vergi, sağlık, dil) en az 10 doğrulanmış Türk uzman. Talep tarafı Taşınma Motoru ve Köprü'den gelir. Çarşı için "taşınıyorum" toplu ilan akışı (bir evin tüm eşyası tek seferde). |
| **Verimlilik** | Aynı işi iki kez yapmayalım | Tek kod tabanı (Staging); yeni her özellik için "kullanıcı ekranı + sahip paneli + admin ekranı" üçlüsü. Lovable tasarım ve akış prototipi için hızlı deney alanı olarak kullanılsın, üretim kodu Staging'de yazılsın. Tekrarlayan içerik (rehber, şehir verisi) şablonla ve kaynak tarihiyle üretilsin. |

## Ölçüm: kuzey yıldızı ve KPI seti

**Kuzey yıldızı önerisi: Ayda en az bir ihtiyacı çözülen aktif üye sayısı.** "Çözülen ihtiyaç" şunlardan biri olabilir: talep gönderip teklif almak, uzmanla görüşmek, etkinliğe katılmak, Çarşı'da alım/satım yapmak, cafe'ye katılıp yazmak. Bu metrik sosyal, ticaret ve hizmet katmanlarını tek sayıda birleştirir.

| Katman | KPI | İlk hedef (5 şehir, lansman öncesi) | Nereden ölçülür |
| --- | --- | --- | --- |
| Arz | Şehir başına doğrulanmış Türk uzman | 50 (5 kategori × 10) | Back office onay kaydı |
| Talep | Taşınma planı oluşturan kullanıcı / ay | Doğrulanmalı (ilk ay baz alınır) | Taşınma Motoru kaydı |
| Dönüşüm | Plan → uzman talebi oranı | %15 | Olay şeması |
| Topluluk | Şehir başına haftalık aktif yazan üye | 30 | Cadde + şehir sohbeti |
| Gelir | Ödeme yapan hesap (Kurucu 1000 + Premium) | 1.000 Kurucu hedefinin ilk %20'si | Ödeme kaydı |
| Veri | Yurt dışı yaşam alanlarından en az 3'ü dolu profil oranı | %40 | Profil tablosu |
| Güven | Talep yanıt süresi (medyan) | 24 saatin altında | Talep kaydı |

Hedef rakamlar ilk tahmindir; ilk 4 haftanın verisiyle CEO ve CTO birlikte kalibre etmeli.

## Riskler, açık kararlar ve kaynaklar

| Risk | Etki | Önlem |
| --- | --- | --- |
| AI'nın veritabanı dışı sonuç üretmesi (Lovable AI Arama) | Kullanıcı var olmayan uzmana yönlenir, güven kaybı | Yalnızca Staging verisinden yanıt (RAG); kaynağı olmayan sonuç gösterilmez |
| Şehir sinyallerinin kişisel veri olması | GDPR/KVKK ihlali, özellikle sağlık ve aile verisi | Amaç bazlı açık rıza, alan bazlı görünürlük, motor sadece toplu/anonim profillerle eğitilir |
| Telefonla ikamet tespitinin yanlış sınıflaması | Diaspora kullanıcısı dışarıda kalır | Çoklu sinyal + itiraz yolu + elçi daveti |
| Avrupa dışı şehirlerde veri yok (Staging'de 17 şehirde 0 kayıt) | Körfez, Kuzey Amerika ve Asya'da boş ürün | İlk 5 şehre Dubai ve Toronto'yu dahil et; elçi + manuel toplama |
| Lovable'daki mock veriler gerçek gibi görünüyor | Yatırımcı ve ekip yanılır | Demo veri her zaman "Demo" rozetli; back office'te gerçek/demo ayrımı |
| Kapsam genişliği (44 özellik) | Hiçbiri derinleşmez | Bu dokümandaki dalga sırasına sadakat; her dalga bir kapıyla kapanır |

### Karar bekleyenler

- [ ] İlk 5 şehir listesi (öneri: Berlin, Londra, Amsterdam, Dubai, Toronto)
- [ ] İkamet tespiti için hangi sinyaller zorunlu, hangileri isteğe bağlı?
- [ ] Köprü'deki soruların danışmanlara ücretli talep olarak satılıp satılmayacağı
- [ ] Kurucu 1000 başlangıç tarihi: Lovable'da "29 Ekim 2027" yazıyor; 2026 mı olmalı?
- [ ] Lovable'daki 10 CorteQS projesinden hangisi referans kabul edilecek (bu rapor CORTEQS+ üzerine)

### Kaynaklar

- Lovable projesi CORTEQS+ (yayın adresi [abroad-buddy-map.lovable.app](https://abroad-buddy-map.lovable.app)): `src/App.tsx`, `src/components/Navbar.tsx`, `src/pages/Feed.tsx`, `Carsi.tsx`, `RelocationEngine.tsx`, `Tools.tsx`, `Guides.tsx`, `CityNews.tsx`, `Pricing.tsx`, `Onboarding.tsx`, `AdminDashboard.tsx`, `src/data/carsiDemoItems.ts`, `diaspora-search` edge function, `roadmap.md`, `AGENTS.md`, `.lovable/plan` notları (14 Ekim 2026'da okundu)
- Staging: [corteqs-staging…run.app](https://corteqs-staging-671400279017.europe-west3.run.app/) ana sayfa, Keşfet, Hizmetler, Topluluklar, Şehir sohbetleri, Türkiye ile bağın, Katıl/koşullar (14 Ekim 2026)
- Önceki rapor: CorteQS Staging vs Lovable karşılaştırma ve yol haritası
