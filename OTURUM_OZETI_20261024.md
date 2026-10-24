# Oturum özeti: Bakersfield karşılaştırması, skill düzeltmeleri, İspanya planı (24.10.2026)

Bu belge başka bir oturuma bilgi olarak verilecek. Kararlar ve yapılanlar aşağıda; doğrulanmayanlar ayrıca işaretli.

## 1. Başlangıç durumu
- Bakersfield paketi (bizim, `bakersfield\bakersfield_UBT\`) ~7 saat, ~130 ajan, 6,9 M çıktı, 88 M yeni önbellek tokeni harcadı. Kullanıcı maliyet ve süreye çok kızdı. İlk skill optimizasyonu (Opus yok, ajan bütçesi, kural 15-17) önceki oturumda yapıldı.
- Atınç aynı şehri (CITY-450) Codex ile, alt ajansız, 3 sa 8 dk, 0,38 M çıktı ile üretti (`bakersfield\bakersfield_ATINC\`).
- Bağımsız denetimler (PDF, kök klasörde): bizim paket için `Bakersfield_Detayli_Denetim_20261023_UBT.pdf` (%24 "doğrulanan alt sınır"), Atınç'ın öz denetimi `Bakersfield_Tamamlama_Denetim_20261024_ATINC.pdf` ("%100 üretim hedefi") ve `Bakersfield_Sure_Token_Raporu_20261024_ATINC.pdf`.
- **İki yüzde aynı ölçü değil:** %24 kanıtlanamayan her şeye 0 veren sıkı bir alt sınır (site önizlemesi yapılmadığı için ~13 puan baştan 0). %100 yalnız miktar hedefleri ve öz denetim. Atınç paketi bağımsız denetlenmedi; onun için "daha doğru" denemez.

## 2. Karşılaştırma bulguları
| | Bizim | Atınç |
|---|---|---|
| Kart | 298 | 240 |
| Mekân | 94 | 120 |
| Mahalle | 6 | 16 |
| Fotoğraf dosyası | 38 (46 bağ) | 275 (Commons 186, Flickr 111) |
| Kaynak / kart başı | 798 / 3,6 | 337 / 1,7 |
| Foto kanıt dosyası | 0/46 | 297/297 |

Skill'in yapamama nedenleri (hepsi dosya kanıtlıydı):
1. Kapılar asgariye (212/92/12/187) bakıyordu, hedefe değil; asgarinin altı (mahalle 6, foto 38) "açık konu" diye teslim edildi.
2. Mekân fotoğraftan bağımsız seçildi (22 yeme-içme, 16 sahne, 49 kapalı alan); 70/94 mekân fotoğrafsız kaldı. Atınç foto-önce seçti, 30 mekân değiştirdi, 57 kaydı bölge gezisi/kent dışı olarak etiketledi.
3. Fotoğraf kaynağı yalnız Commons idi.
4. Kanıt düzeni: `package_sources` kopyaları `Lisans kanıtları\kaynaklar\` alt klasörüne yazıyordu, Drive klasörü düzleştirdi (798 yol bozuk); `photo_rows` foto kaynak/lisans snapshot alanlarını boş bırakıyordu (92 eksik, uygulamanın ready aşaması zorunlu tutuyor). Bizim "0 hata" kapısı taslak moduna göre ölçüyordu.
5. Numara: CITY-901 yazıldı, Drive klasör adında CITY-450 vardı.
6. Mahalle: 6 büyük bölge; Atınç 16 "…çevresi" semti.
7. İçerik: denetim 3 ciddi hata (DV'de 1 dolar ücret, CalFresh'te herkesten SSN, CPR) ve TK yaş eşiği gibi eski kurallar buldu; zincir bunları yakalamadı (denetçi kaynağı kendi içinde kontrol ediyor, daha yeni kural çıktıysa görmüyor; ben doğrulama turunu en çok bire indirmiştim).
8. Maliyet: 130 ajan bağlamı her seferinde yeniden yükledi; 798 kaynak KUR zincirini 2,4 kat şişirdi.

Atınç paketinin zayıf yanları (kopyalanmayacak): 120 mekânın 57'si kent dışı/bölge gezisi, 337 adresin 124'ü otomatik erişimde açılmıyor, atomik iddia kanıt tablosu yok, kartlar `İnceleme` durumunda (skill `Taslak` istiyor).

## 3. Yapılan değişiklikler (hepsi `corteqs-skills\` altında)
Yedekler: `city-pack\SKILL.md.atinc_karsilastirma_oncesi.bak` (bu tur), `SKILL.md.bakersfield_oncesi.bak` (önceki tur).

**Araçlar (`toolkit\scripts\`):**
- `package_sources.py`: kaynak kopyaları düz `Lisans kanıtları\` klasörüne; temizlik yalnız sha256 adlı dosyaları siler (foto kanıtlarına dokunmaz).
- `photo_rows.py`: `with_evidence_files` her foto için `<foto>.source-evidence.json` ve `.license-evidence.json` yazar, Kanıtlar'ın dört snapshot alanını doldurur; `delivery_url` ikinci kaynaklarda https özgün adresi aynen kullanır; atıf, değişiklik notu ve hak dayanağı sağlayıcı adını yazar (Commons için eski metin aynen).
- `photo_candidates.py`: adaylara `provider` alanı (varsayılan "Wikimedia Commons").
- `photo_previews.py`: ikinci kaynak adaylarının https önizlemesine izin verir.
- **Yeni `photo_sources.py`**: Commons'ta adayı <3 olan mekân/mahalle için sırayla Openverse (Flickr dahil; anahtarsız, `OPENVERSE_TOKEN` varsa kullanılır) ve Smithsonian (CC0; `DEMO_KEY`) arar; Europeana opt-in (`--sources`). Yalnız CC BY, BY-SA, CC0, PDM. Wikimedia sonuçları atılır. Tek kaynağın hatası ötekileri durdurmaz (3 hatadan sonra o kaynak bırakılır). Yeni satırlar `search.jsonl`'e `query_kind: alt:<kaynak>` ile eklenir; tekrar koşuda denenmiş kaynak atlanır. Ad eşleştirmesi sıkı (tek ayırt edici sözcüklü adlarda şehir adı da metinde geçmeli). Çıktıdaki `download_hosts` indirmede `--allow-host` olur.
- Library of Congress denendi: otomatik erişime 403, bot engeli aşılmadı. Mapillary ve Geograph anahtar gerektirdiği için eklenmedi.

**Testler:** yeni `tests\test_photo_sources.py` (11 test); `test_package_sources.py` ve `test_e2e_mini_city.py` düz klasöre göre güncellendi. Son çalıştırma: **2445 test geçti**. Not: bu makinede testler için `tzdata` ve `toolkit\requirements.txt` (jsonschema) kurulması gerekti; kuruldu.

**`city-pack\SKILL.md`:**
- Dosya düzeni ve `package_sources` açıklaması düz klasöre güncellendi; foto kanıt dosyaları anlatıldı.
- Numara: önce kullanıcının verdiği ya da Drive klasör/zip adından aranır (CITY-NNN), bulunmazsa 900+.
- Yeni kural 18 (hedef: 240/120/16/12/12/60/250/8; asgari altı teslim yok, kullanıcıya tek öneriyle sorulur; kart tavanı 260), kural 19 (mahalle: tanınan semt/cadde/yapı çevresi, ≥2 kaynak, 16'ya küçük semtlerle ulaş), kural 20 (kart başı ≤2 `source_ids`, tarihe duyarlı konularda güncellik taraması talimatı).
- Mekân seçimi: grup kontenjanı sabit 15 değil; Commons foto oranı <%30 olan grup en çok 8 mekân; gerekirse en çok 20 etiketli yakın çevre gezisi.
- Foto bölümü: `photo_sources` komutu ve geçiş kuralı, kaynak sınırları, `--allow-host <download_hosts>`.
- Skill testleri (250) geçiyor.

## 4. Doğrulanmayanlar (yeni oturum bunları bilmeli)
- `photo_sources` canlı denemesi yalnız arama ve aday üretme düzeyinde: Bakersfield'da Commons'ta <3 adayı olan 12 mekândan 2'sinde 6 aday buldu (Lengthwise Brewing: 5 gerçek Flickr karesi). Ticari yerlerde verim düşük. **İndirme, kanıt dosyası ve Excel'e giriş uçtan uca denenmedi.** Atınç'ın `download_media.py` aracının farklı bir alan adını `--allow-host` ile kabul edip etmediği bilinmiyor.
- Anonim Openverse limiti düşük (12 mekân = 24 istek); gerçek şehirde ücretsiz kayıt (`OPENVERSE_TOKEN`) gerekebilir. Limit rakamları üçüncü taraf kaynaktan, resmî sayfadan teyitsiz.
- Smithsonian ve Europeana adaptörleri canlı denenmedi (Smithsonian görselleri çoğunlukla uzantısız adres olduğundan elenir).
- Güncellik taraması (kural 20) yalnız talimat; otomatik ölçen script yok. Doğrulama turu en çok bire inmiş durumda (maliyet kararı); bu güncellik hatası yakalamayı azaltabilir.
- Flickr'a doğrudan API anahtarı gerekmedi (Openverse üzerinden gidiyor). Flickr'ın kendi anahtarı ücretsiz ama ticari kullanım için ticari anahtar/onay gerekir.
- Atınç şablonundaki ready kuralı ve resmî araç konumu: `araclar\arac\core\content_delivery\validation_media.py`.
- Bizim Bakersfield paketi (`bakersfield_UBT`) bu düzeltmelerle **yeniden üretilmedi**; yalnız skill ve araçlar değişti.

## 5. Sıradaki iş: İspanya şehirleri (plan hazır, onaylanmadı)
Kullanıcı 12 şehir verdi: Barcelona (zaten yapıldı, ~%90, `barcelona\CITY-009_barcelona_v001.xlsx`), Alicante, Bilbao, Madrid, Málaga, Marbella, Palma de Mallorca, Sevilla, Tarragona, Tenerife, Valensiya, Zaragoza. İstek: önce bir şehir yap, süresini ölç, sonra kullanıcı söyledikçe sırayla diğerleri; **amaç İspanya ön araştırmasının tekrarlanmaması**.

Plan dosyası: `C:\Users\baris-terzioglu\.claude\plans\linear-inventing-thacker.md` (kullanıcı onay penceresini kapattı; plan değiştirilmek istenebilir). Özet:
- İlk şehir önerisi **Sevilla** (Andalucía: Sevilla, Málaga, Marbella aynı bölge katmanını paylaşır).
- Üç katman: İspanya (ulusal, bir kez), bölge (comunidad autónoma, bölge başına bir kez), şehir (her şehirde). Bilbao (foral vergi) ve Tenerife (IGIC) ulusal kartları birebir kullanamaz.
- Mevcut engel: `SKILL.md` ~satır 158 "ülke paketi yalnız kullanıcı verdiyse; skill kurmaz". Yeni `country` fazı, `ROOT\ulke\ES\` paket biçimi (`pack.json`, kartlar, iddia defteri, kaynak kopyaları, erişim haritası, kartlar için `valid_until`), şehirde kullanım için yeni araç `country_apply.py` (kartları şehre kopyalar, ağsız kaynak kopyası, hash değişmemiş kart denetimi atlar), güncellik/sürüm takibi önerildi.
- Açık kararlar (varsayılanla): ilk şehir Sevilla; ulusal metin tekrarı için şehre uyarlanmış giriş + yerel adım şartı (11 şehirde aynı metin tekrar içerik riski); Barcelona kartları taslak olarak (yeniden kaynaklandırılıp tam denetimle; Barcelona Excel'inde yalnız 32 kaynak var); kaynak kopyalarının saklanması; Bilbao/Tenerife ayrı yazım.
- Ölçüm: ülke/bölge/şehir fazı süre ve token ayrı raporlanır; hedef Sevilla toplamı Bakersfield'dan (~7 sa) düşük, Málaga ve Marbella Sevilla'nın şehir fazının %60'ını aşmaz.

## 6. Kullanıcı tercihleri (bu oturumdan)
- Sade Türkçe, jargonsuz; kararlar tek öneriyle. Maliyet (token, süre) çok hassas: önce script, ajan son çare.
- Rapor istediğinde dürüst ol, kendi hatalarını kabul et, ölçülmeyeni ölçülmüş gibi sunma.
- Büyük işlerde "sen nasıl istersen" diyor; yine de kapsamı ve doğrulanmayanları açıkça söyle.
