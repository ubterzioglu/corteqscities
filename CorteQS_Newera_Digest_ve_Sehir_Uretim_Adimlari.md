# CorteQS Newera: Belge Özeti ve Tek Şehir Üretim Adımları

Hazırlanma tarihi: 15 Ekim 2026
Kaynaklar: WhatsApp yazışması (12–15 Ekim), 3 ekran görüntüsü, İçerik Hazırlama Kılavuzu v6, AI Üretim Promptu v6, Monday Ekip Kullanım Kılavuzu (14 Ekim), Özellik Kütüphanesi ve Şehir Zekâ Motoru Stratejisi.

Not: Atınç 15 Ekim'de şablon, doküman ve promptların v7 sürümünü yayınladı. Burada okunan PDF'ler v6'dır. Başlamadan önce Drive'daki v7 dosyalarını kontrol et.

---

# BÖLÜM 1: ÖZET

## Genel durum

CorteQS, yurt dışındaki Türklere yönelik bir platform. Ekip şu an 421 şehirlik bir katalog için şehir içeriği üretiyor. Ekip: Atınç (teknik lider, proje sahibi), Umut Barış ve Burak.

Atınç'ın hedefi: 1 ayda üç kişi birlikte 367 şehri üretmek ve şehir sayısını 400'lü banda çıkarmak. Özellik geliştirmeyi en az 1,5–2 ay sonraya bıraktı.

## Şehir üretimi

- **Dağılım:** 49 mevcut rehber ve 5 bekletilen şehir (Riyad, Cidde, Kuveyt, Maskat, Manama) kapsam dışı. Kalan 367 şehir paylaştırıldı: Atınç 123, Umut Barış 122, Burak 122.
- **Hız:** Berlin kalitesinde günde 4–5 şehir gerekiyor. Atınç tek başına Prag'a 6 saat harcadı.
- **Berlin standardı:**

| Kapsam | Asgari | Hedef |
| --- | --- | --- |
| Pratik yanıt | 212 | 240 |
| Keşif mekânı | 92 | 120 |
| Mahalle / semt | 12 | 16 |
| Rehber konusu | 12 | 12 |
| Farklı mekân fotoğrafı | 187 | 250 |
| Kapak fotoğrafı | 6 | 8 |
| Rota | 9 | 12 |
| Sözlük | 48 | 60 |

- **Fotoğraf kuralı:** Gerçek, ücretsiz ticari kullanıma uygun fotoğraflar. AI görseli yok. Fotoğrafçı ve lisans kaydı zorunlu. Şehir başına 200'den fazla fotoğraf gerekiyor. Kaynak çoğunlukla Wikimedia Commons, indirme kısıtı olduğu için en çok vakit alan iş bu.
- **Kabul zinciri:** Yönetim ekranındaki yüzde yalnızca sayıyı ölçer. Sonra teknik doğrulama, insan incelemesi, özel DB taslağı ve ayrı yayın kararı gelir. AI kendi çıktısını onaylı işaretleyemez.
- **Model notu:** Bir promptta en fazla 5 şehir öneriliyor, ancak bu Atınç'ın kullandığı üst düzey modelle geçerli. Önce tek şehirle dene.

## Monday

- Atınç genel proje takibi için Monday'i kurdu: proje planı ve backlog, test senaryoları (61 senaryo, hepsi "test bekliyor"), hata takibi, UAT yayınları, riskler/kararlar, haftalık toplantı tutanakları (12 Ekim dahil).
- Standard plan kişi başı yaklaşık 15 €/ay. Önce deneme, beğenilirse ücretli plan.
- Şehir üretimi Monday'de değil, yönetim ekranı ve Drive'da yürür.
- Roller: Atınç koordinasyon ve yazılım. Umut Barış test, kabul/yeniden test, deneyim kontrolü ve şehir üretimi. Burak içerik doğruluğu, fotoğraf/lisans incelemesi, hukuk/bütçe kararları ve şehir üretimi.
- 21 Ekim'de pilot kontrol var. Hız ve kalite ölçülecek. Hedef tutmazsa kaliteyi düşürmek yerine kapsam, kapasite veya tarih kararı alınacak.

## Özellik stratejisi (Burak'ın dokümanı)

- **Karar önerisi:** Staging'i "Şehir Zekâ Motoru" etrafında büyütmek, Lovable CORTEQS+'ı özellik kütüphanesi olarak kullanmak. Lovable'da 44 özellik var: 26'sı Staging'de yok, 15'i kısmen var. Lovable verisi büyük ölçüde demo, AI araması veritabanına bağlı değil, Taşınma Motoru araştırmaları sunucuya kaydedilmiyor.
- **Motor:** Şehir arayanı "orada yaşıyor" ve "taşınmayı düşünüyor" diye ayırır, hizmet, indirim, etkinlik ve danışman talebine yönlendirir.
- **İlk üç hamle:** Diaspora-first kimlik ve onboarding; şehir sayfası + Taşınma Motoru + uzman talebi akışı; Kurucu 1000 (99 €) ve Evim-Evin anketi.
- **Dalgalar:** D0 kimlik ve erişim; D1 şehir çekirdeği; D2 topluluk (Cadde, cafe'ler, Çarşı); D3 reklam, puan ekonomisi, AI Twin.
- **Kuzey yıldızı metriği:** Ayda en az bir ihtiyacı çözülen aktif üye. Önerilen ilk 5 şehir: Berlin, Londra, Amsterdam, Dubai, Toronto.
- **Açık kararlar:** İlk 5 şehir; ikamet tespiti sinyalleri; Köprü sorularının danışmanlara satılıp satılmayacağı; Kurucu 1000 başlangıç tarihi (Lovable'da "29 Ekim 2027" yazıyor, 2026 mı?); hangi Lovable projesinin referans alınacağı.
- **Atınç'ın yanıtı:** Bunlar Monday backlog'una bölünecek, ama önce şehir üretimi.

## Yazışmadan diğer notlar

- Dil çözümü `/en`, `/de` gibi alt yollar. SEO sonrası netleşecek. Burak platformlar arası gelir modeli (indirim, affiliate, diaspora bazlı reklam) için mimari vizyon istedi.
- 49 şehirlik dünya versiyonu staging'de yayında.
- Ekran görüntülerinden ikisi WhatsApp grup listesi (CorteQS Türk Team 111 ile 101–107 numaralı gruplar). Üçüncüsü admin geri bildirimlerinde 7 Ağustos'tan kalan bir LinkedIn kaynaklı öğrenci mesajı.

## Güvenlik uyarısı

WhatsApp yazışmasında yönetim hesaplarının başlangıç şifreleri düz metin olarak paylaşılmış. Kılavuz şifrelerin belgelere yazılmamasını söylüyor. İlk girişte şifreyi değiştir ve mesajı sil. Bu dosyaya şifreleri bilerek koymadım.

---

# BÖLÜM 2: TEK ŞEHİR İÇİN ÜRETİM ADIMLARI

## A. Hazırlık (bir kez)

1. Yönetim ekranına gir: `https://corteqs-staging-671400279017.europe-west3.run.app/yonetim/uretim/`. Kendi e-postanla ve başlangıç şifrenle giriş yap, şifreyi değiştir.
2. "Google Drive'a bağlan" düğmesine bas, paylaşılan klasöre yetkili Gmail hesabını seç ve salt okuma iznini ver. Yönetim girişi ile Drive bağlantısı ayrı adımlardır. Yetki hatasında Atınç'a haber ver.
3. Drive'daki "Şehir İçerik Merkezi"ni aç. `00 · Başlangıç ve kullanım kılavuzu` altındaki kılavuz, prompt ve şema dosyalarını (en güncel sürüm) indir.
4. `CITY-000 · Berlin · Örnek paket` klasörünü incele. Salt okunurdur, değiştirme.

## B. Şehri seç ve doğrula

1. Yönetim ekranında "Benim şehirlerim"i aç.
2. Listendeki şehirlerden birini seç, başkasının şehrine girme.
3. CITY kodunu, `city_id` slug'ını, ülkeyi ve tam adı not et.
4. Aşamayı "Hazırlanıyor" yap.
5. Drive'da `01 · Üretilecek şehirler` altındaki şehir klasörüne git. İçinde tek etkin `.xlsx` (`CITY-NNN_sehir-slug_v001.xlsx`) ile `Fotoğraflar`, `Lisans kanıtları`, `Teslimler` alt klasörleri olmalı.
6. `.xlsx` dosyasını indir. Aynı dosyayı çevrimdışı birden fazla kişi düzenlemesin.

## C. AI'a verilecekler

AI aracı web araştırması yapabilmeli ve dosya yazıp indirebilmeli.

1. Prompt PDF'inin tamamını yapıştır.
2. Köşeli parantezli alanları doldur: şehir adı, `city_id`, CITY kodu, ülke, Drive klasör bağlantısı, çalışma dosyası adı, hazırlayan, bugünün tarihi (YYYY-MM-DD), Berlin referans dosyası.
3. Aynı konuşmaya ekle: atanmış şehir `.xlsx`, Berlin tam örnek `.xlsx` ve şema dosyaları. Yalnız prompt veya yalnız boş şablon yetmez.
4. AI ilk cevabında okuduğu ekleri, şehir kimliğini, araştırma/indirme imkânını ve planını özetlemeli. Sonra işe başlamalı.
5. Kendi modelinde tek şehirle başla.

## D. İçerik üretimi (Excel)

Her minimum sayı karşılanmalı. Bir alandaki fazla kayıt başka alandaki açığı kapatmaz (bkz. Bölüm 1 tablosu).

1. AI şu aşamalarla ilerlemeli: kapsam planı, konu ve yanıtlar, yerler/mahalleler/rotalar, sözlük ve yerleşim adımları, fotoğraf ve kanıtlar, son kalite kontrolü.
2. Excel yapısı korunur:
   - 16 ana sekme: Özet, Teslimat, Şehir, Konular, Yanıtlar, Mekânlar, Mahalleler, Bağlantılar, Rotalar, Sözlük, Adımlar, Kaynaklar, Fotoğraflar, Kanıtlar, SayfaAlanları, EkDetaylar.
   - 6. satır başlıklar, 7. satır teknik anahtarlar, veri 8. satırdan başlar.
   - Formüller, açılır listeler ve sekme sırası korunur. Formül sütunlarına değer yazılmaz.
3. 12 konu dolu olmalı: taşınma öncesi, vize/oturum, resmî kayıt, ev, faturalar, banka/vergi/sigorta, sağlık, iş, aile/eğitim, ulaşım, günlük yaşam, keşif/kültür/spor.
4. Her yanıtta: kısa ilk cevap, adımlar, belgeler, süre, maliyet (para birimiyle), statü istisnası, kaynak, doğrudan işlem linki. Hukuk, vize, vergi ve sağlık için güncel resmî kaynak zorunlu.
5. Her kaynak `Kaynaklar` sekmesine kaydedilir: `source_id`, başlık, yayıncı, URL, gerçek kontrol tarihi, Türkçe not. Gelecek tarih yazılmaz.
6. Mekânlarda 8 grup dolu olmalı: müze, sanat, sahne, spor, doğa, aile, yeme-içme, tarih. Kapanmış yer ve uydurma adres olmamalı.
7. Rotalar gerçek mekân kimliklerinden oluşur: 2–8 durak, `stop_entry_ids` içinde `;` ile ayrılır, `stops` aynı sırada yazılır.
8. Mahalle `compare_json` alanında en az 4 somut başlık olmalı.
9. `SayfaAlanları` sekmesinde şehre özgü doldur: 14 metin anahtarı, `facts` (en az 4), `quick_links` (en az 3), `timeline` (en az 4), `budget_fields` (10 alan), `place_groups` (8 alan), `emergency`, `emergency_url`, `pharmacy_url`.
10. Berlin'e özgü bilgiyi (acil numara, para birimi, yasa, süreç) kopyalama. `_db_` ile başlayan Berlin ham arşiv alanlarını alma.
11. `Şehir` sekmesinde para birimi, koordinat, saat dilimi ve hava durumu linklerini doldur.

## E. Fotoğraf ve lisans

1. Önce en zor mekânlar için fotoğraf ihtiyaç matrisi çıkar (modern müze, spor, sanat, iç mekân). Kolay parklar sona.
2. Kaynak sırası: Wikimedia Commons tekil "File" sayfaları, kamu malı/CC0, CC BY ve CC BY-SA, koşulları kontrol edilmiş ücretsiz stok (Unsplash gibi).
3. Kabul edilmeyenler: AI üretimi görsel, Google görsel sonucu, Pinterest, Instagram, blog, otel/TripAdvisor fotoğrafı, NC/ND lisans, filigranlı veya ücretli görsel, hak zinciri belirsiz kare.
4. Dosyaları gerçekten indir (JPG, PNG veya WebP), aç ve gözle kontrol et. Yanlış yer, bozuk, düşük çözünürlüklü veya tekrar kareleri ele.
5. Commons indirme kısıtı için bekleyip tekrar çekmek gerekebilir.
6. Her mekâna en az bir gerçek fotoğraf, kapağa 6 farklı kare. Aynı karenin kırpımı veya küçültülmüşü yeni fotoğraf sayılmaz.
7. `Fotoğraflar` sekmesi her kare için: `photo_id`, `entry_id`, göreli yol (`Fotoğraflar/sehir_yer_01.jpg`), `sha256`, Türkçe açıklama, fotoğrafçı, lisans, lisans URL'si, tekil kaynak sayfa URL'si, kontrol tarihi, değişiklik notu.
8. `Kanıtlar` sekmesine kanıt kaydını gir. Kaynak sayfası ve lisans metninin PDF/ekran kaydını `Lisans kanıtları` klasörüne koy.
9. SHA-256 indirilen gerçek dosyadan hesaplanır, rastgele değer yazılmaz.
10. `metadata_review_status`, `pixel_review_status`, `rights_status` alanlarını AI "Evet/Onaylandı" yapmaz. İnsan inceleyip doldurur.

## F. Kendi kontrolün

1. Excel'i Microsoft Excel'de aç. Bozuk formül, kayıp açılır liste veya okunmayan yazı varsa teslim etme.
2. Sayıları kendin yeniden say. AI'ın "tam" beyanı yeterli değil.
3. Birkaç kritik yanıtı kaynağında kontrol et. Birkaç fotoğrafı dosya, kaynak ve atıf eşleşmesiyle doğrula.
4. Tüm linkler açılmalı, göreli yollar gerçek dosyalara çözülmeli.
5. Berlin eksiklerini tekrarlama: kaynaksız sözlük, metin olarak yazılmış rota durakları.

## G. Drive'a yükleme

1. Fotoğrafları `Fotoğraflar` klasörüne yükle.
2. Kaynak ve lisans kanıtlarını `Lisans kanıtları` klasörüne yükle (tek kanıt ZIP'i olabilir).
3. Excel'i aynı dosyanın yeni sürümü olarak yükle: sağ tık, "Sürümleri yönet", "Yeni sürüm yükle". İkinci dosya veya yeni klasör açma. Google Sheets'e dönüştürme.
4. `Teslimler` klasörüne koy: `TESLIM_OZETI.txt`, `ACIK_KONULAR.txt`, `ILERLEME_KAYDI.txt`, `dosya-envanteri.json`. Açık konu yoksa ACIK_KONULAR.txt'ye "Araştırmada saptanan açık konu yok; editör/hak kabulü ayrıca gereklidir" yaz.
5. Bulunamayan fotoğraf veya çözülemeyen hak konusunu açıkça raporla. Başka mekânın fotoğrafını koyma.

## H. Ölçüm ve teslim

1. Yönetim ekranında, Drive bağlantısı açıkken şehir kartında "Bu şehri yenile" düğmesine bas. Sayfayı yenilemek Drive taraması başlatmaz.
2. Adetleri ve yüzdeyi kontrol et. 8 alanın hepsi asgari düzeye ulaşmalı. Yüzde yalnızca sayıyı gösterir, kaliteyi veya yayın onayını göstermez.
3. "Erişim sorunu" varsa kontrol et: Google hesabı doğru mu, dosya doğru şehir klasöründe mi, Excel yeni sürüm olarak mı yüklendi.
4. Aşamayı "İnceleme bekliyor" yap ve Atınç'a haber ver. İlk şehirleri birlikte kontrol edeceksiniz.
5. "İnceleme tamamlandı" yalnız gerçek insan incelemesinden sonra seçilir.

## I. Sonrası (senin yapmadığın adımlar)

1. Editör ve hak incelemesi: kaynak doğruluğu, Türkçe, şehre özgülük, fotoğraf-mekân eşleşmesi, lisanslar.
2. Teknik sorumlu doğrulama aracıyla Excel'den JSON üretir.
3. Onaylanan paket özel DB taslağı olarak aktarılır. Mevcut rehberin üzerine yazılmaz.
4. Ekran testi yapılır, ardından Atınç ve proje sahibi ayrı yayın kararı verir. Görev aşaması yayın izni değildir.

## Pratik ipuçları

- Excel'de yanlış ama sistem doğru gösteriyorsa bu içerik düzeltmesidir. Doğru Excel yüklenmiş ama ölçüm yanlışsa Monday'de "Hatalar ve Yeniden Test"e CITY kodu, dosya sürümü ve kanıtla kayıt aç.
- Monday'de şehir üretim kartı açma, şehir Excel'i veya fotoğraf yükleme.
- Fotoğraf araştırmasını içerik üretimiyle paralel yürüt. En uzun ve en riskli kısım bu.
