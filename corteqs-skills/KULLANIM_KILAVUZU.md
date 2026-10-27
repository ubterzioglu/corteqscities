# Corteqs şehir skill'leri — kullanım rehberi

25 Ekim 2026 · Okuyucu: Barış ve ekip. Teknik bilgi gerekmez.

## Bir bakışta

| Skill | Ne yapar | Nasıl başlatılır |
|---|---|---|
| **city-pack** | Bir şehrin paketini üretir (17 sekmeli Excel, fotoğraflar, kaynak kopyaları); denetimden sonra düzeltme turunu da yapar | Yeni oturumda yalnız şehir adı: `Málaga` |
| **city-audit** | Paketi bağımsız denetler; puan ve karar verir | Yeni oturumda: `Málaga paketini denetle` |
| **city-preview** | Drive'a yüklenen paketi ve web önizlemesini yerel paketle karşılaştırır | Yeni oturumda: `Málaga önizlemesini kontrol et` |

**Bir şehrin tam yolu:**

1. `city-pack`: üret
2. `city-audit` L0: hızlı, ucuz denetim
3. Düzeltme turu: `city-pack`, gerekirse
4. `city-audit` L1: asıl denetim
5. Karar HAZIR değilse 3. adıma dön
6. Paketi Drive'a elle yükle
7. `city-preview`
8. Yayın kararı ekipte

Her adım **ayrı, yeni bir oturumda** yapılır.

## Sıra ve ülke paketleri

- **Şehirler tek tek yapılır.** İki şehir aynı anda yürütülmez; bir şehir bitmeden yenisine başlanmaz.
- **Ülke sırası (Barış, 25.10.2026):** önce İspanya şehirleri, sonra Almanya.
- **Ülke paketi:** bir ülkenin bütün şehirlerinde aynı olan kartlar (vize, vergi, sağlık sistemi, kira yasası) bir kez yazılıp `ulke\<ülke>\` altında tutulur. city-pack şehrin ülkesini bulunca paketi **kendisi kullanır**; senin ayrıca söylemen gerekmez.
  - **İspanya** (`ulke\ES`, v9) ve Endülüs bölge paketi (`ulke\ES\bolge\andalucia`). Endülüs şehirleri (Málaga, Granada, Córdoba, Cádiz…) ikisini birlikte kullanır; başka bölgelerde yalnız ülke paketi kullanılır.
  - **Almanya** (`ulke\DE`, v1). Eyalet paketi henüz yok; eyalete göre değişen bilgiyi şehir yazarı yazar.
  - **Eskime:** paketlerde tarihi geçen kartlar şehre kopyalanmaz. Paket eskiyse skill "önce ülke paketini güncelleyeyim mi?" diye sorar. İspanya'da 6 kira kartının süresi 5 Kasım 2026'da doluyor.
  - **Ayrıntı:** `belgeler\tarifler\ISPANYA_YENI_SEHIR.md`, `ALMANYA_YENI_SEHIR.md`. Yepyeni bir ülke için `YENI_ULKE_SEHIR.md`: 1–2 şehir olacaksa doğrudan city-pack; 3 ve üstüyse önce ülke paketi kurulur.

## Başlamadan önce

- **Klasör:** `C:\temp_private\corteqs\0000_newera` (VS Code'da açık olsun).
- **İnternet gerekir:** resmî siteler ve Wikimedia Commons.
- **Bilgisayar uykuya geçmesin.** Uyku sırasında iş durur; sonradan kaldığı yerden devam edilir ama zaman kaybolur.
- **Kurulum hazır:**
  - Python ortamı: `.venv`
  - Atınç'ın resmî araçları: `araclar\arac`
  - Berlin örneği ve Atınç'ın şehir şablonları: `ekler\`, `ekler\<şehir>\`
- **Google Drive bağlantısı açık olsun:** skill Atınç'ın şehir şablonunu Drive'da kendisi arar.

## Klasörler

| Klasör | İçerik |
|---|---|
| `uretim\<şehir>\` | Şehrin üretimi: `paket\` (teslim), `_is\` (çalışma dosyaları), `manifest.json`, `RUN_LOG.csv` |
| `denetim\<şehir>_<tarih>_<kademe>\` | Denetim sonuçları (`DENETIM_OZETI.md`, `issues.json`, `score.json`) |
| `ulke\` | Ülke ve bölge paketleri |
| `corteqs-skills\` | Skill'ler, araç kutusu ve testleri, bu rehber |
| `araclar\`, `ekler\` | Atınç'ın araçları ve şablonları (salt okunur) |
| `belgeler\tarifler\` | Ülkeye göre "yeni şehir nasıl yapılır" notları |
| `belgeler\devir\` | Eski devir ve oturum notları (yalnız geçmişe bakmak için) |
| `belgeler\kilavuz\` | Kılavuz PDF'leri, denetim kılavuzu, eski promptlar |
| `arsiv\` | Eski şehir denemeleri (Bakersfield, Barcelona, Eindhoven qwen) ve geçici dosyalar |

---

## 1. city-pack — şehir paketi üretmek

### Başlatma

Yeni bir oturum aç ve yalnız şehir adını yaz:

```
Málaga
```

### Skill ne yapar

1. **Hazırlık:**
   - Şehri tanır: kimlik, ülke, dil, saat dilimi.
   - Atınç'ın şablonunu önce Drive'da arar; yoksa Berlin örneğinden kendisi türetir.
   - Ülke ve bölge paketi varsa onu bağlar.
   - Ne bulduğunu sana tek satırda söyler.
2. **Kaynaklar:** konulara göre resmî kaynakları bulur ve kopyalarını alır.
3. **Bilgi kartları:** 12 konuda yaklaşık 240 kart yazar. Her sayı ve kural kaynaktan birebir alıntıya dayanır; her kart bağımsız bir denetimden geçer. İşlem kartlarında dört öğe zorunludur: **nereye** (şehirdeki ofis ya da kanal), **ne getirilir** (belgeler), **ne ödenir** (tutar), **ne kadar sürer** (süre, son tarih).
4. **Mekânlar, mahalleler, rotalar, sözlük, şehir sayfası:** 120 mekân, 16 mahalle, 12 rota, 60 terim. Her mekânda "bugün açık mı" kontrolü yapılır; sitenin hâlâ yayında olması kanıt sayılmaz. Fiyat ve saat mekânın kendi resmî sayfasından alınır, turizm sitesinden alınmaz. Aynı yerin parçası (bahçe, iç müze) ayrı mekân sayılmaz.
5. **Fotoğraflar:** Commons ve diğer açık kaynaklardan lisanslı fotoğraflar seçilir. Maket, etkinlik karesi ve yüzü seçilen kişi kareleri reddedilir. Kaynağı doğrulanamayan Flickr/PxHere dosyası seçilmez. **Fotoğrafsız mekân teslim edilmez:** fotoğrafı bulunamayan mekânın yerine fotoğraflı başka bir mekân konur.
6. **Birleştirme:** Excel kurulur ve Atınç'ın resmî doğrulayıcısından geçirilir.
7. **Teslim:** paket klasörü, özet dosyaları ve token kaydı yazılır.

### Senden ne ister

- Yalnız gerçek kararları sorar, her seferinde tek bir öneriyle ("aksini söylemezsen böyle yapıyorum").
- Maliyet kararlarını sorar: ajan bütçesinin yarısı aşılırsa "ucuz yol mu?" der.
- Arada kısa durum raporu verir. İstediğin zaman `durum raporu` yazabilirsin.

### Süre ve maliyet (ölçülen)

- **Sevilla ilk üretim:** 5 sa 13 dk, 3,66 M çıktı tokeni.
- **Almanya ülke paketi:** 2 sa 21 dk, 3,9 M çıktı tokeni, 52 ajan.
- **Kurallar:** aynı anda en çok 5 ajan çalışır (fazlası oturumu kilitliyor). Ajanlar Sonnet ile çalışır; Opus yalnız sen istersen.

### Oturum kesilirse

Yeni bir oturum aç, yine şehir adını yaz. Skill nerede kaldığını iki üç cümleyle özetler ve devam etmeyi önerir. `devam` yazman yeter.

### Bittiğinde nerede ne var

| Yol | İçerik |
|---|---|
| `uretim\<şehir>\paket\` | Teslim paketi: Excel, `Fotoğraflar\`, `Lisans kanıtları\`, `Teslimler\` |
| `uretim\<şehir>\paket\Teslimler\TESLIM_OZETI.txt` | Sayılar ve genel durum |
| `uretim\<şehir>\paket\Teslimler\ACIK_KONULAR.txt` | İnsanın bakması gerekenler |
| `uretim\<şehir>\RUN_LOG.csv` | Faz faz token, süre ve ajan sayısı |
| `uretim\<şehir>\_is\notlar_skill.md` | Üretim sırasında görülen skill/araç sorunları |

### Bilmen gerekenler

- **Skill kendi işini onaylamaz.** Hiçbir yere "hazır" ya da "onaylandı" yazmaz; insan inceleme alanları "Bekliyor" kalır.
- **Drive'a yüklemez;** yüklemeyi sen yaparsın.
- **Hitap "sen"**, Berlin örneği gibi.
- **Her şehir bir ölçüm koşusudur.** Üretim sırasında skill değiştirilmez; görülen sorunlar not dosyasına yazılır ve şehir bitince ayrı bir oturumda düzeltilir.
- **Şehir zaten üretilmişse sıfırdan başlamaz.** Duruma göre devam etmeyi, denetimi ya da düzeltme turunu önerir.

---

## 2. city-audit — paketi denetlemek

### Başlatma

Paket bittikten sonra **yeni** bir oturum aç:

```
Málaga paketini denetle
```

İstersen kademe de ekle, örneğin `Málaga paketini denetle, L0`:

| Kademe | Ne yapar | Maliyet | Ne zaman |
|---|---|---|---|
| **L0** | Yalnız script'ler çalışır: sayılar, bağlantılar, dosyalar, fotoğraf kanıtları | Düşük (ajan yok) | Üretimden hemen sonra; bariz hataları görmek için. Karar en iyi ihtimalle "KANIT EKSİK" olur |
| **L1** (varsayılan) | L0 + ajanlar: iddialar kaynakla karşılaştırılır, bütün fotoğraflara paftadan bakılır, mekânlar ve rotalar kontrol edilir, lisans zinciri incelenir, mekânlardan örneklemle "açık mı" doğrulanır | Yüksek: Sevilla'da 32 ajan, ~7 M alt ajan tokeni, ~2 saat | L0 temiz çıktıktan sonra asıl denetim |
| **L2** | Her şey: bütün iddialar, bütün mekânlar, bütün bağlantıların anlamı | Çok yüksek | Yayından önce son denetim (henüz denenmedi) |

L1 ajanları başlatmadan önce sana iş sayısını ve tahmini maliyeti sorar.

### Çıktı

- **Klasör:** `denetim\<şehir>_<tarih>_<kademe>\`.
- **`DENETIM_OZETI.md`:** ilk satırda editoryal hazır olma yüzdesi ve karar yer alır; ardından bulgular, yanlış fotoğrafların pafta numarası ve düzeltme sırası gelir.
- **`issues.json`:** her bulgu Excel satırıyla birlikte (P0 = yayın engeli, P1 = düzeltilmeli, P2 = bakım önerisi).
- **`score.json`:** puan. Denetimin sonunda verilen "RUN_LOG için" satırındaki dosyadır.
- **Karar:** **HAZIR**, **DÜZELTME GEREKLİ** ya da **KANIT EKSİK**. Kararı script verir; tek bir açık P0 ya da P1 bulgusu bile kararı DÜZELTME GEREKLİ yapar.
- **Denetim pakete hiçbir şey yazmaz.**

---

## 3. Düzeltme turu — denetimden sonra

Karar **DÜZELTME GEREKLİ** ise yeni bir oturum aç ve yalnız şehir adını yaz (`Sevilla`). Skill denetimin sonucunu görür ve düzeltme turunu önerir.

- **Girdi:** denetimin `issues.json` dosyası ve düzeltme sırası.
- **Bulgular ilgili fazda düzeltilir:**
  - Fotoğraf bulguları: fotoğraf fazında.
  - Mekân, rota ve açık-mı bulguları: mekân fazında.
  - Kart bulguları: yanıt fazındaki editör turunda.
- **Değişen her kart** yeniden bağımsız denetimden geçer.
- **Paket aynı klasörde ve aynı Excel adıyla** yeniden kurulur; yalnız içerik değişir.
- **Sonra:** yeni bir oturumda `<Şehir> paketini denetle`. Önce L0, temizse L1.
- **Hedef:** karar HAZIR. Sevilla'da editoryal yüzde L0'da %7 idi, birinci düzeltme turundan sonra L1'de %74 oldu; ikinci tur hedefi 90+.

---

## 4. city-preview — Drive ve web önizlemesini kontrol etmek

### Başlamadan önce

1. Paketi Drive'daki şehir klasörüne **elle yükle**. Skill hiçbir şey yüklemez.
2. Chrome'da yönetim ekranına **kendi hesabınla gir**: `https://corteqs-staging-671400279017.europe-west3.run.app/yonetim/uretim/`. Skill parola girmez, istemez.
3. Claude'un Chrome uzantısı ve Google Drive bağlantısı açık olsun. Biri yoksa skill o kısmı "kontrol edilemedi" diye yazar, gerisini yapar.

### Başlatma

```
Málaga önizlemesini kontrol et
```

Drive klasörünün linkini mesaja eklersen ("…kontrol et, Drive: <link>") soru sormaz.

### Senden onay isteyeceği şeyler

Hepsini tek mesajda, ayrı ayrı evet/hayır diye sorar:
- **«Bu şehri yenile»:** yönetim ekranında ölçümü yeniler.
- **Kayıt bırakan denemeler:** «Tamamladım», «♡ kaydet», «Rotayı planıma ekle», «Hesapla ve kaydet», «Takvimimi oluştur». Yalnız sahte test verisiyle yapılır, sonunda geri alınır.
- **Takvim (ICS) dosyasını indirmek.**

### Çıktı

- **Klasör:** `denetim\<şehir>_<tarih>_ONIZLEME\`.
- **`ONIZLEME_OZETI.md`:** neye bakıldığı ve madde madde sonuç.
- **Ekran görüntüleri:** `ekran\` klasörü.
- **Karar vermez:** "yayına hazır" demez, yalnız kanıt toplar. Yayın kararı ekibindir.

---

## Kısa tarif: bir İspanya şehrini baştan sona yapmak

| Adım | Oturum | Yazacağın | Sonuç |
|---|---|---|---|
| 1 | yeni | `Málaga` | Paket `uretim\malaga\paket\` |
| 2 | yeni | `Málaga paketini denetle, L0` | Bariz hataların listesi |
| 3 | yeni (L0'da P0/P1 varsa) | `Málaga` → düzeltme turu | Yeni paket |
| 4 | yeni | `Málaga paketini denetle` (L1) | Yüzde ve karar |
| 5 | yeni (karar HAZIR değilse) | `Málaga` → düzeltme turu, sonra 4. adım | Hedef: HAZIR |
| 6 | — | Paketi Drive'a yükle | — |
| 7 | yeni | `Málaga önizlemesini kontrol et` | Önizleme raporu |
| 8 | — | Yayın kararı (ekip) | — |

Puanı token kaydına eklemek için denetimden sonra: `Málaga RUN_LOG'una denetim puanını ekle`.

## Sık sorulanlar

- **Skill başlamadı ya da başka bir şey yaptı.** `city-pack ile Málaga paketi üret` yaz.
- **"Bu şehir zaten var" dedi.** Önerisine bak: devam, denetim ya da düzeltme turu.
- **Ajanlar duruyor gibi.** `durum raporu` yaz. Skill her ajanın dosyasını izler; 10 dakika hiç yazmayan ajanı uyarır, gerekirse yenisini başlatır. Bazı ajanlar sonuçlarını en sonda yazar, o yüzden önce kısa bir uyarı gönderilir.
- **Çok uzun sürüyor.** Uzun işler 5'erli dalgalarla yürür. Wikimedia ya da bir site "çok yoğun" derse skill bekleyip yeniden dener.
- **Bilgisayarı kapatabilir miyim?** Kapatırsan iş durur. Sonra yeni oturumda şehir adını yazıp devam edersin.
- **Hitabı ya da bir kuralı değiştirmek istiyorum.** Şehir üretilirken değil; şehir bitince ayrı bir geliştirme oturumunda.
- **Ne kadar token harcandı?** `uretim\<şehir>\RUN_LOG.csv`.
- **Skill'de ne düzeltildi, ne açık kaldı?** `corteqs-skills\IYILESTIRME_LISTESI.md`.
- **city-preview "kontrol edilemedi" dedi.** Chrome uzantısı ya da Drive bağlantısı kapalıdır, ya da yönetim ekranına giriş yapılmamıştır. Bağlayıp yeniden iste.

## Yapmaman gerekenler

- Aynı oturumda hem üretmek hem denetlemek. Denetim, üreten oturumun bilgisinden etkilenmemeli.
- İki şehri aynı anda yürütmek.
- Üretim sürerken skill dosyalarını değiştirmek ya da değiştirtmek.
- `ekler\`, `araclar\`, `ulke\` ya da başka bir şehrin paketine elle dokunmak.
