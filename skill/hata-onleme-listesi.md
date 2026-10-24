# Şehir paketi: hata önleme listesi (v1)

Kaynak: Corteqs v7 resmî doğrulayıcının (`Corteqs_v7_Teknik_Teslim_Araclari.zip`) Qwen/Eindhoven paketinde verdiği 363 yapı hatası, 822 uyarı ve 323 medya hatası, ayrıca 21 Ekim 2026 Eindhoven denetimi (B/M/F/T bulguları).
Kullanım: (1) skill referansı, (2) prompta eklenecek blok için kaynak (`prompt-ek-blok.txt`).
Not: Doğrulayıcı yalnız biçim, kimlik, sayı ve dosya tutarlılığını ölçer. Bölüm C ve D (içerik ve fotoğraf doğruluğu) denetimden gelir ve araçla yakalanmaz.

---

## A. Doğrulayıcının yakaladığı hata sınıfları (Eindhoven sayıları)

| # | Mesaj (kısaltılmış) | Adet | Kural | Qwen ne yaptı | Önleme |
| --- | --- | --- | --- | --- | --- |
| A1 | Kanıtlar: kaynak bilgisi incelemesi tanımsız seçim içeriyor | 272 | `metadata_review_status` ve `pixel_review_status` yalnız `Bekliyor` veya `Doğrulandı` olabilir. AI yalnız `Bekliyor` yazar. | `metadata_review_status` = "Tamam" yazdı (geçersiz) | Üç durum alanını da `Bekliyor` bırak; "Tamam", "Evet", "Onaylandı" yazma |
| A2 | Medya: ana fotoğraf kaydı ile kaynak dosyası uyuşmuyor | 269 | `Fotoğraflar.file` ve `Fotoğraflar.sha256`, `FotoğrafKaynakları.original_file` ve `original_sha256` ile **birebir aynı** olmalı. Web kopyası yalnız `web_file`/`web_sha256` alanına gider. | Ana kayda WebP'yi, `original_file` alanına JPG'yi yazdı; ikisi farklı | `Fotoğraflar.file` = korunan özgün dosya yolu ve hash'i. WebP ayrı alanda. İndirdiğin dosyayı "özgün" diye adlandırırsan ana kayıt onu göstermeli |
| A3 | Lisans etiketi ve resmî sürüm URL uyuşmuyor / CC0 resmî sürüm bağlantısı gerekli | 23 | CC lisans bağlantısı `https://creativecommons.org/licenses/by-sa/3.0/` biçiminde, **https**, sorgu parametresi yok, sürüm ve yetki alanı etikete uyar (`CC BY-SA 3.0 nl` → `.../3.0/nl/`). CC0 → `https://creativecommons.org/publicdomain/zero/1.0/` | CC0 için `http://` kullandı; 6 CC kaydında etiket-bağlantı uyuşmadı | Lisans URL'sini Commons metadata'sından al, `http`→`https` yap, `?` sonrasını sil, etiket ve sürümü karşılaştır |
| A4 | Kamu malı dayanak bağlantısı eksik / Lisans bağlantısı zorunlu | 28 | `Public domain` etiketli satırda da geçerli bir dayanak URL'si gerekir | 14 kamu malı satırında `license_url` boş | Kamu malı dayanağı için kaynak sayfa veya telif durumu sayfası URL'si yaz; boş bırakma |
| A5 | Kanıtlar: kaynak lisans bağlantısı zorunlu | 14 | Kanıt satırında lisans bağlantısı zorunlu | Fotoğraflar'daki boşluk Kanıtlar'a da taştı | A4 çözülünce kapanır |
| A6 | SayfaAlanları: `quick_links` gerekli alanlar label, entry | 10 | Her hızlı bağlantı `{label, entry}`; `entry` aynı şehirdeki içerik slug'ı. Dış `url` yok. | `{label, url}` yazdı | Önce slug listesini çıkar, `quick_links` ve `facts` içindeki `entry` değerlerini bu listeden seç |
| A7 | SayfaAlanları: `emergency.tel` geçerli arama numarası gerekli | 4 | `tel` yalnız `+?[0-9*#]{2,20}` | Boşluk, tire veya metin içeren numara yazdı (tahmin) | `tel` alanına yalnız rakam (`112`, `0900-8844`→ boşluksuz); okunur biçim `number` alanına |
| A8 | Mahalleler: karşılaştırma başlık ve değerleri dolu metin olmalı | 16 | `compare_json` en az 4 çift; her anahtar ve değer **dolu metin** (sayı/boş/liste değil) | Değerler boş veya metin dışı | Tüm değerleri string yaz; en az 4 anahtar; boş değer varsa anahtarı çıkar |
| A9 | Mahalleler: başka kartla yinelenen başlık | 2 | Mahalle başlıkları kartlar arasında benzersiz | Strijp-S ve Leenderheide başlıkları yinelenmiş | Başlıkları yazdıktan sonra betikle yineleme kontrolü |
| A10 | Kaynaklar: aynı URL için birden çok kaynak kimliği | 4 | Bir URL = bir `source_id` | 4 URL için yeni kimlik üretti | Kaynak eklemeden önce URL var mı bak; varsa mevcut kimliği kullan |
| A11 | Kimlik yalnız küçük ASCII harf, sayı, `-`, `_`, `:` içermeli | 4 | Tüm `*_id` ve `entry_id` değerlerinde Türkçe karakter, boşluk, büyük harf yok | `tv-akış` gibi ve teslimat kimliği | Kimlik üretirken ç/ğ/ı/ö/ş/ü → c/g/i/o/s/u, küçük harf. Teslimat kimliği `city-039-v001` biçimi |
| A12 | Rotalarda 2–8 farklı mekân kimliği gerekli (uyarı) | 2 | Rota 2–8 durak, tekrarsız; `stops` adları ve `stop_entry_ids` aynı sırada; ana kart ilk durak | 2 rota 9 duraklı | Rota yazarken durak sayısını betikle say; 9 ise ikiye böl |
| A13 | SayfaAlanları: `arrival_note`, `emergency_url`, `pharmacy_url`, `advice_entry` eksik (uyarı) | 4 | Bu alanlar dolu ve ülkeye özgü resmî bağlantı | Eksik bıraktı | 17 zorunlu metin alanının tamamını kontrol listesiyle doldur |
| A14 | Okuyucu: "Listede yinelenen değer var" | çökme | `;` ayraçlı listelerde tekrar yok | 2 hücrede aynı `source_id` iki kez | Liste hücrelerini yazmadan önce tekilleştir. Bu hata okuyucuyu **çökertir**, tüm kontrolü durdurur |
| A15 | Uyarı: 816 kanıt incelemesi açık (metadata, pixel, rights) | 816 | Beklenen davranış | – | Bunlar hata değil; insan onayı bekliyor. AI "Doğrulandı" yapmaz |

---

## B. Aracın ölçmediği içerik hataları (denetimden)

| # | Sınıf | Eindhoven örneği | Önleme kuralı |
| --- | --- | --- | --- |
| B1 | Eski/yanlış yasal değer | WW 36 haftada 26 hafta; 2026 kira artışı %4,4/%6,1; devir vergisi %8; KVK €85,15 | Tarihe duyarlı her sayıda **yürürlük yılı** ve birincil kaynak alıntısı iste; sayıyı kaynak sayfasından kopyala, bellekten yazma |
| B2 | Genelleme | "Her çocuk için koşulsuz", "€50 tavan", "26 hafta/5 yıl" | Koşul, istisna ve kapsamı ayrı cümle yaz; "genel kural" demeden önce kaynakta istisna listesine bak |
| B3 | Kurum yetkisi | Huurcommissie depozito hakemi gibi anlatıldı | Kurumun resmî "ne yapar/ne yapmaz" sayfasını oku |
| B4 | Yerel uygulama | Posta etiketi (ja-sticker), alışveriş akşamı, pazar günü | Belediye/şehir tanıtım sitesinden doğrula, ulusal kuralı şehre taşıma |
| B5 | Kaynak niteliği | 72 Wikipedia kaynağı; 21 bağlantı "resmî" etiketli ama Wikipedia'ya gidiyor | Wikipedia resmî kaynak değildir; işlem ve hukuk için yalnız kurum sitesi. Etiket gerçeği yansıtmalı |
| B6 | Öz-beyan | 233 kaynak `verified=Evet` | `verified=Evet` yalnız kaynak sayfasında iddia bulunup iddia tablosuna yazıldıysa |
| B7 | Mekân adresi | 12 yanlış adres/semt (Muziekgebouw, Wilhelmina, Ton Smits, MU…) | Adres yalnız mekânın resmî ziyaret sayfasından; bulunamazsa boş bırak, tahmin ve `?` yazma |
| B8 | Mekân tarihçesi | W-Hal "Philips fabrikası", Auditorium 1950'ler | Tarih/köken kurum arşivinden; belirsizse yazma |
| B9 | Aynı yapı iki kart | Hoogenband/Tongelreep iki semt | Aynı kompleks tek kayıt, alt tesisler ayrı notlanır |
| B10 | Grup dengesi | 93 mekânın 53'ü tarih/mimari (%57) | Seçimi fotoğraf bulunabilirliği belirlemesin: tarih ≤ yaklaşık %35; diğer 7 gruba asgari |
| B11 | Mekân sayısı | 93/120 | Hedefin altında kalırsan `ACIK_KONULAR`'a gerekçeyle yaz; sayı için uydurma ekleme yapma |
| B12 | Rota gerçekçiliği | Strijp kısa yürüyüş, ayrı semtlerdeki duraklar | Gerçek yürüme/bisiklet süresini harita kaynağından al |
| B13 | Yer tutucu metin | `5621?`, `[[Hoogstraat` | Bilinmeyen alanı temiz boş bırak, `ACIK_KONULAR`'a yaz |

---

## C. Fotoğraf hataları (denetimden; araç görsel anlamı ölçmez)

| # | Sınıf | Örnek | Önleme kuralı |
| --- | --- | --- | --- |
| C1 | Yanlış şehir | Zweeloo çiftliği "Türk çarşısı" yerine | Kaynak sayfasının adres/koordinatını mekânla karşılaştır; farklı yerleşim adı geçiyorsa ele |
| C2 | Yanlış nesne | Farklı su kulesi, meydan yerine kilise içi | Kaynak başlığı/açıklaması mekân adını açıkça içersin; iç/dış mekân farkı |
| C3 | Fotoğraf olmayan görsel | Tablo, gravür, çizim, harita | Başlık/açıklamada `painting`, `drawing`, `engraving`, `map`, `plan`, `logo`, `oil on canvas` varsa ele |
| C4 | Ürün/ayrıntı | Bira şişesi, sokak levhası, mezar yakın planı | Kapak ve mahalle için mekânı tanıtan genel görünüm; yakın plan ayrıntı yardımcı kare |
| C5 | GPS uyuşmazlığı | Seattle GPS'li kare; 2–5 km farklar | Commons koordinatı varsa mekâna uzaklığı hesapla (>1 km işaretle, kaynak kaydını kontrol et) |
| C6 | Benzer kadraj | Siyah-beyaz/renk varyantları | Perceptual hash ile yakın kopyayı eşle, tek tut; farklı SHA yeni fotoğraf değil |
| C7 | Küçük boyut | Kısa kenar <600 px (13 kare) | Kapakta ve kartta kullanılacak karelerde asgari boyut; dar panorama gerekçeyle |
| C8 | Arşiv tarihi | 1945, 1964, 1992, 1966 | Başlıkta tarih yaz; güncel görüntü gibi sunma |
| C9 | Hak bağlamı | GLOW yerleştirmeleri, duvar resimleri, tanınabilir kişiler | Sanat/etkinlik/kişi olan karelere hak incelemesi notu; `rights_status` = Bekliyor |
| C10 | Zincir eksiği | Korunan özgün dosyalar teslimde yok, `author_url` boş | Özgün dosyayı indir ve teslim et; yazar profili varsa ekle; yoksa hayali link yazma |
| C11 | Boyut yanlış beyanı | "~0 MB" | Gerçek boyutu betikle ölç (`du`), rapora ölçüm sonucunu yaz |

---

## D. Öz-rapor kuralları (modelin kendi iddiaları)

1. "0 hata" yalnız **resmî doğrulayıcı çıktısı** sonucuysa yazılabilir; kendi betiğiyle değil.
2. "Tamam", "doğrulandı" denmeden önce ölçüm betiği çıktısı rapora yapıştırılır.
3. Görsel kontrol sayısı gerçek sayıda yazılır ("10 kare incelendi"), "272 doğrulandı" denmez.
4. Çözülemeyen konu `ACIK_KONULAR`'a açık yazılır; hedef sayı tutturmak için eksik gizlenmez.
5. İnsan onayı alanları (`pixel_review_status`, `rights_status`, `metadata_review_status`) AI tarafından doldurulmaz.

---

## E. Bu listenin sınırları

- Doğrulayıcı yalnız yapıyı ölçer. Çalışmadan geçmesi içeriğin doğru olduğunu göstermez.
- A2'nin nedeni (ana kayıt ile özgün kayıt eşleşmesi) kodu okuyarak çıkardım; v7 sözleşmesi değişirse yeniden kontrol edilmeli.
- Qwen'in yerel klasöründe `Lisans kanıtları/orijinaller/*.jpg` dosyaları var; denetim bunları Drive'daki teslimde bulamamış. Eksiğin yükleme aşamasında mı, üretimde mi olduğunu bilmiyorum.
- Sınıf sayıları Eindhoven/Qwen içindir; başka model veya şehirde farklı çıkabilir.
