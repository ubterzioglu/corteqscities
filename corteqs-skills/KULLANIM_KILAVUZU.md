# Corteqs şehir skill'leri — kullanım kılavuzu

23 Ekim 2026 · Okuyucu: Barış ve ekip. Teknik bilgi gerekmez.

## Bir bakışta

| Skill | Ne yapar | Nasıl başlatılır | Durum |
|---|---|---|---|
| **city-pack** | Bir şehrin paketini sıfırdan üretir (17 sekmeli Excel, fotoğraflar, kaynak kopyaları) | Yeni oturumda yalnız şehir adı: `Tilburg` | Hazır |
| **city-audit** | Paketi bağımsız denetler; puan ve karar verir | Yeni oturumda: `Tilburg paketini denetle` | Hazır |
| **city-preview** | Drive'a yüklenen paketi, yönetim ekranındaki ölçümü ve staging şehir sayfasını yerel paketle karşılaştırır | Yeni oturumda: `Tilburg önizlemesini kontrol et` | Hazır |

Üç skill de arka planda aynı araç kutusunu kullanır (script'ler ve 2.400'ü aşkın otomatik test). Araç kutusu doğrudan kullanılmaz.

**Bir şehrin tam yolu:** `city-pack` (üret) → `city-audit` (yerel paketi denetle) → paketi Drive'a elle yükle → `city-preview` (Drive ve web önizlemesini kontrol et) → yayın kararı ekipte.

## Başlamadan önce

- **Klasör:** `C:\temp_private\corteqs\0000_newera` (VS Code'da açık olsun).
- **Her iş ayrı bir Claude Code oturumunda yapılır:** üretim bir oturumda, denetim başka bir oturumda. Böylece denetim üreten oturumun bilgisinden etkilenmez ve token ölçümü karışmaz.
- **İnternet gerekir** (resmî siteler, Wikimedia Commons).
- **Bilgisayar uykuya geçmesin.** Uyku sırasında iş durur; sonradan kaldığı yerden devam edilebilir ama zaman kaybolur.
- Kurulum hazır: Python ortamı (`.venv`), Atınç'ın resmî araçları (`araclar\arac`), Berlin örneği (`ekler\`). Bir şey kurman gerekmez.

---

## 1. city-pack — şehir paketi üretmek

### Başlatma

Yeni bir oturum aç ve yalnız şehir adını yaz:

```
Tilburg
```

"Tilburg paketi" ya da "Tilburg şehir paketi üret" de olur.

### Skill ne yapar

1. **Hazırlık:** Şehri tanır: kimlik, ülke, dil, saat dilimi. Atınç'ın şablonu varsa onu kullanır; yoksa Berlin örneğinden şablonu kendisi türetir. Atınç'ın numarası yoksa 901'den başlayan bir yerel deneme numarası verir. Ne bulduğunu sana tek satırda söyler.
2. **Kaynaklar:** Konulara göre resmî kaynakları bulur, kopyalarını alır.
3. **Bilgi kartları:** 12 konuda kartları yazar. Her sayı ve kural kaynaktan birebir alıntıya dayanır. Her kart ayrıca bağımsız bir denetimden geçer.
4. **Mekânlar, mahalleler, rotalar, sözlük, şehir sayfası.** Her mekân için "bugün açık mı" kontrolü yapılır; mekânın kendi sitesinin hâlâ yayında olması yeterli kanıt sayılmaz.
5. **Fotoğraflar:** Wikimedia Commons'tan lisanslı fotoğraflar seçilir. Bir görsel kontrol yapılır, ardından bağımsız bir ikinci göz bakar.
6. **Birleştirme:** Excel kurulur ve Atınç'ın resmî doğrulayıcısından geçirilir.
7. **Teslim:** Paket klasörü, özet dosyaları ve token kaydı yazılır.

### Senden ne ister

- Yalnız gerçek kararları sorar, her seferinde tek bir öneriyle ("aksini söylemezsen böyle yapıyorum"). Cevabını bekler.
- Arada kısa durum raporları verir. İstediğin zaman `durum raporu` yazabilirsin.

### Süre

Birkaç saat. Eindhoven pilotunda fazlar toplam yaklaşık 7 saat sürdü; yeni hız kurallarıyla daha kısa sürmesi bekleniyor.

### Oturum kesilirse

Örneğin 5 saatlik oturum sınırı dolarsa: yeni bir oturum aç, yine şehir adını yaz. Skill şehrin klasörünü tanır, nerede kaldığını iki üç cümleyle özetler ve devam etmeyi önerir. `devam` yazman yeterli.

### Bittiğinde nerede ne var

| Yol | İçerik |
|---|---|
| `uretim\<şehir>\paket\` | Teslim paketi: Excel, `Fotoğraflar\`, `Lisans kanıtları\`, `Teslimler\` |
| `uretim\<şehir>\paket\Teslimler\TESLIM_OZETI.txt` | Sayılar ve genel durum |
| `uretim\<şehir>\paket\Teslimler\ACIK_KONULAR.txt` | İnsanın ya da uzmanın bakması gerekenler |
| `uretim\<şehir>\RUN_LOG.csv` | Token, süre ve ajan sayısı, faz faz |
| `uretim\<şehir>\_is\notlar_skill.md` | Üretim sırasında görülen skill/araç sorunları |
| `uretim\<şehir>\_is\` | Çalışma dosyaları (pakete girmez) |

### Bilmen gerekenler

- **Skill kendi işini onaylamaz.** Hiçbir yere "hazır" ya da "onaylandı" yazmaz. İnsan inceleme alanları "Bekliyor" kalır; onayı insan verir.
- **Drive'a yüklemez.** Yüklemeyi sen yaparsın.
- **Hitap "sen"**, Berlin örneği gibi. Sözlük ve konu açıklamaları kişisiz olabilir.
- **Her şehir bir ölçüm koşusudur.** Üretim sırasında skill değiştirilmez. Skill bir sorun görürse not dosyasına yazar; düzeltmeler şehir bitince ayrı bir oturumda yapılır.
- **Şehir zaten üretilmişse sıfırdan başlamaz.** Duruma göre devam etmeyi, denetimi ya da yeni bir sürümü önerir.
- **Atınç'ın resmî numarası sonradan gelirse** skill'e söylemen yeterli ("Tilburg'un resmî numarası CITY-NNN"); şablon aynı araçla yeniden türetilir.

---

## 2. city-audit — paketi denetlemek

### Başlatma

Paket bittikten sonra **yeni** bir oturum aç ve şunu yaz:

```
Tilburg paketini denetle
```

İstersen sonuna kademe ekle, örneğin `Tilburg paketini denetle, L0`:

| Kademe | Ne yapar | Ne zaman |
|---|---|---|
| **L0** | Yalnız script'ler çalışır; hızlı ve ucuz | Bariz hataları hızlıca görmek için. İçerik okunmadığı için karar en iyi ihtimalle "KANIT EKSİK" olur |
| **L1** (varsayılan) | L0'a ek olarak riskli kartlar ve iddialar okunur, fotoğraflara görsel kontrol yapılır, mekânlardan örneklemle "açık mı" diye bakılır | Normal denetim |
| **L2** | Her şey: bütün iddialar, bütün mekânlar, bütün bağlantıların anlamı | Yayından önce son denetim |

### Çıktı

- Klasör: `denetim\<şehir>_<tarih>_<kademe>\`
- `DENETIM_OZETI.md`: İlk satırda editoryal hazır olma yüzdesi ve karar yer alır, ardından bulgular ve düzeltme sırası gelir.
- `issues.json` (bulgular) ve `score.json` (puan).
- **Karar** üç seçenekten biridir: **HAZIR**, **DÜZELTME GEREKLİ** ya da **KANIT EKSİK**. Kararı script verir; skill elle yükseltmez.
- Denetim pakete hiçbir şey yazmaz.

### Denetimden sonra

- **"DÜZELTME GEREKLİ" çıkarsa:** Yeni bir oturumda şehir adını yaz; skill yeni bir sürüm önerir. Bu yeni sürüm akışı henüz tam tanımlı değil; şimdilik ne düzeltileceğini birlikte konuşuruz.
- **Puanı token kaydına eklemek için:** Denetim sonunda puan dosyasının yolunu yazar ("RUN_LOG için: …score.json"). Bu adım şimdilik kendiliğinden olmuyor: yeni bir oturumda `Tilburg RUN_LOG'una denetim puanını ekle` yazman gerekiyor.

---

## 3. city-preview — Drive ve web önizlemesini kontrol etmek

### Başlamadan önce
1. Paketi Drive'daki şehir klasörüne **elle yükle**. Skill hiçbir şey yüklemez.
2. Chrome'da yönetim ekranına **kendi hesabınla gir**: `https://corteqs-staging-671400279017.europe-west3.run.app/yonetim/uretim/`. Skill parola girmez, istemez.
3. Claude'un Chrome uzantısı ve Google Drive bağlantısı açık olsun. Biri yoksa skill o kısmı "kontrol edilemedi" diye yazar, gerisini yapar.

### Başlatma

Yeni bir oturum aç ve şunu yaz:

```
Tilburg önizlemesini kontrol et
```

Drive klasörünün linkini mesaja eklersen ("…kontrol et, Drive: <link>") hiç soru sormaz. Eklemezsen önce üretim notlarında arar, bulamazsa linki sorar.

### Senden onay isteyeceği şeyler

Hepsini tek mesajda, ayrı ayrı evet/hayır diye sorar:
- **Yönetim ekranında «Bu şehri yenile»:** Ortak ekranda ölçümü yeniler, herkes görür.
- **Şehir sayfasında kayıt bırakan denemeler:** «Tamamladım», «♡ kaydet», «Rotayı planıma ekle», «Hesapla ve kaydet», «Takvimimi oluştur». Yalnız sahte test verisi kullanılır ve deneme sonunda geri alınır.
- **Takvim (ICS) dosyasını indirmek.**

Onay vermezsen o kısım "onay yok" diye yazılır; diğer kontroller sürer. Hiçbir sitede başvuru, ödeme ya da üyelik formu gönderilmez.

### Ne kontrol eder

| Yer | Neye bakar |
|---|---|
| **Drive** (salt okunur) | Doğru şehir klasörü mü; kökte tek Excel ve tam üç klasör var mı; buluttaki dosyalar yereldekilerle aynı mı. Excel'in gerçek içeriği indirilip özet değeriyle karşılaştırılır. Drive fotoğraflar için özet değeri vermediğinden fotoğraflarda "ad ve boyut" eşitliği yazılır, "içerik doğrulandı" denmez |
| **Yönetim ekranı** | Şehir kartındaki 8 sayı paketteki sayılarla aynı mı; son tarama Excel'den yeni mi. Paneldeki aşama bir görev durumudur, yayın değildir |
| **Şehir sayfası** (staging) | Masaüstü ve mobil görünüm; arama, kart, işlem düğmesi, rota, adımlar, kısayollar; her fotoğrafın atfı Excel'le aynı mı ve bağlantıları çalışıyor mu; fotoğraf üstünde uyarı bandı var mı; kaydetme, mahalle karşılaştırma, gezi listesi, bütçe toplamı, takvim. Şehir sayfası yoksa bu maddeler "kontrol edilemedi" olur; yine de Excel'deki uyarı bandı metinleri taranır |

### Çıktı

- Klasör: `denetim\<şehir>_<tarih>_ONIZLEME\`
- `ONIZLEME_OZETI.md`: İlk satırda neye bakıldığı ve kaç maddenin geçtiği, kaldığı ya da bakılamadığı yazılır. Ardından madde madde sonuç ve kanıtlar gelir.
- Ekran görüntüleri: `ekran\` klasörü.
- **Karar vermez.** "Yayına hazır" ya da "yayımlandı" demez; yalnız kanıt toplar. Yayın kararı ekibindir.

---

## Sık sorulanlar

- **Skill başlamadı ya da başka bir şey yaptı.** `city-pack ile Tilburg paketi üret` yaz.
- **"Bu şehir zaten var" dedi.** Ne istediğini seç: devam, denetim ya da yeni sürüm.
- **Çok uzun sürüyor.** `durum raporu` yaz. Uzun işler paralel yürür. Wikimedia ya da bir site "çok yoğun" derse skill bekleyip yeniden dener.
- **Bilgisayarı kapatabilir miyim?** Kapatırsan iş durur. Sonra yeni bir oturumda şehir adını yazıp devam edebilirsin.
- **Hitabı ya da başka bir kuralı değiştirmek istiyorum.** Şehir üretilirken değil; ayrı bir geliştirme oturumunda değiştirilir.
- **Ne kadar token harcandı?** `uretim\<şehir>\RUN_LOG.csv` dosyasına bak.
- **city-preview "araç yok" ya da "kontrol edilemedi" dedi.** Claude'un Chrome uzantısı ya da Google Drive bağlantısı kapalıdır, ya da yönetim ekranına giriş yapılmamıştır. Bağlayıp yeniden iste.
- **city-preview "Drive'daki Excel yereldekinden farklı" dedi.** Drive'da eski bir sürüm duruyordur. Excel'i yeni sürüm olarak yükle, sonra yeniden kontrol ettir.

## Yapmaman gerekenler

- Aynı oturumda hem üretmek hem denetlemek.
- Üretim sürerken skill dosyalarını değiştirmek ya da değiştirtmek.
- `ekler\`, `araclar\` ya da başka bir şehrin paketine elle dokunmak. Bunlar salt okunurdur.
