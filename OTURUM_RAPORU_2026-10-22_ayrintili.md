# Oturum raporu: Eindhoven/qwen analizi ve şehir paketi araç kutusu (22 Ekim 2026)

**Oturum kimliği:** `00ec9fd5-286c-4f34-be5a-3d9879565806` · **Çalışma klasörü:** `C:\temp_private\corteqs\0000_newera`
**İsteyen:** Umut Barış Terzioğlu · **Yürüten:** Claude (Claude Code, VS Code). Ana model çoğunlukla Opus 5.5; bir bölüm Sonnet 5.5.
**Kapsam:** Bu doküman bu oturumda yapılan her şeyin ayrıntılı kaydıdır. Devam etmek için kısa yol `DEVIR_2026-10-22_corteqs_skill.md`; bu doküman neyin, neden ve hangi kanıtla yapıldığını anlatır.

---

## İçindekiler

1. Özet
2. Başlangıç isteği ve girdiler
3. Kronoloji
4. Analiz bulguları (Eindhoven denetimi, qwen'in süreci, Excel denetimi, Miami token analizi, v7 prompt'u)
5. Paralel oturumun çıktılarıyla karşılaştırma
6. Denetim kılavuzu 2.0 değerlendirmesi ve `checks.yaml`
7. Alınan kararlar
8. Araç kutusu: script'ler, gerçek veri sonuçları, sınırlar
9. Kalite güvencesi: yöntem ve yakalanan hatalar
10. Bu oturumun token ve süre kullanımı
11. Üretilen dosyalar
12. Açık noktalar ve riskler
13. Bu oturumdan sonra yapılanlar

---

## 1. Özet

- **Neden düşük puan?** qwen3.8-max ile üretilen Eindhoven paketi (CITY-039) bağımsız Codex denetiminde **%55** aldı. Sorun "yazma" becerisi değil, çalışma düzeniydi:
  - İçerik bellekten yazılmış, kaynak sonradan eklenmiş.
  - Fotoğraflar gözle hiç incelenmemiş.
  - Sözleşme ve şema dosyalarına bakılmamış.
  - Resmî doğrulayıcı qwen'e hiç verilmemişti.
- **Token nereye gidiyor?** Miami (Codex) ölçümünde girdi token'ının yalnız **%22,5**'i şehir içeriği yazımına gidiyor. Kurulum, mekanik işler, rapor ve QA birlikte %48,4; fotoğraf işi %20.
- **Mimari kararı:** "Kanıt önce, script önce, LLM yalnız yargı için". Üç skill (`city-pack`, `city-audit`, ileride `city-preview`) ve ortak bir araç kutusu.
- **Araç kutusu:** 26 Python modülü ve **845 test** (kapsam **%97**) yazıldı. Hepsi gerçek qwen paketinde salt okunur denendi. Denetim kılavuzundaki 62 script kontrolünün **42'si tam, 18'i kısmen** script'leşti; 2'si eksik.
- **Öne çıkan ölçümler:**
  - İddia defteri Eindhoven'ın 12 bilgi hatasından **11'ini** işaretliyor.
  - Fotoğraf ön elemesi **hiçbir iyi fotoğrafı reddetmeden** yanlışların 16/23'ünü yakalıyor ve görsel incelemeyi %26'ya indiriyor.
  - Temas paftası görsel inceleme token'ını yaklaşık **24–39 kat** düşürüyor.

## 2. Başlangıç isteği ve girdiler

**İstek (özetle):**
- İki PDF'i (Miami token raporu, Eindhoven denetimi) incele.
- qwen'in hatalarını ve çok token harcatan yerleri bul.
- **AMAÇ 1:** token üretimini azaltırken kaliteyi artır. **AMAÇ 2:** süreci Claude Code skill'ine dönüştür.
- Ayrıntılı rapor ve öneri ver.

**İncelenen girdiler:**

| Girdi | Boyut / içerik |
|---|---|
| `Miami_Uretim_Sure_Token_Raporu_20261020.pdf` | 10 sayfa. Codex oturumu: 63 dk 48 sn, 27.158.757 girdi (%97,12 önbellek), 782.053 önbellek dışı, 130.642 çıktı, 34 faz |
| `Eindhoven_Berlin_Standardi_Denetim_20261021 2.pdf` | 25 sayfa, Codex. %55; bilgi hataları B01–B18, mekân/rota M01–M14, fotoğraf bulguları, teknik T01–T10, URL ekleri |
| `AI_URETIM_PROMPTU_v7_EINDHOVEN_CITY-039_LOKAL.txt` | 306 satır, 58 KB. v7 E2E üretim prompt'u + yerel deneme bloğu |
| `CorteQS_Newera_Digest_ve_Sehir_Uretim_Adimlari.md` | Proje özeti: 421 şehir, Berlin standardı, ekip rolleri |
| `eindhoven_qwen38_max\` | qwen teslim paketi: 1367 dosya, 316 MB (Excel + 272 WebP + 272 orijinal + 816 kanıt JSON'u) |
| `_work_eindhoven\` | qwen'in 555 çalışma dosyası: script'ler, önbellek, probe'lar |
| `results\` | Deneme klasörleri. Yalnız `barcelona_qwen37_plus` dolu; ChatGPT ve Gemini klasörleri boş şablon |
| `ekler_eindhoven\` | Atınç'ın şehir şablonu, Berlin örneği, 4 şema dosyası |
| `araclar\arac\` | Atınç'ın v7 teknik teslim araçları (resmî doğrulayıcı) |
| Sonradan eklenenler | `SESSION_OZETI_VSCODE_DEVRI_2026-10-22.md` (paralel oturum özeti), `SEHIR_DENETIM_CHECKLIST.pdf` (41 sayfa, K01–K120) |

**Erişilemeyen:** qwen'in gerçek token sayaçları. Kilo CLI'ın `kilo.db` veritabanını okuma isteği kişisel veri gerekçesiyle otomatik olarak reddedildi. Etrafından dolaşılmadı. qwen için token yorumları dosya boyutlarından tahmindir.

## 3. Kronoloji

Saatler yereldir ve yaklaşıktır (dosya zamanlarından).

| Saat | Ne yapıldı |
|---|---|
| ~12:07 | İstek alındı. PDF'ler, v7 prompt'u, Digest ve deneme notları okundu |
| ~12:15 | `kilo.db` erişimi reddedildi. 3 paralel ajan başlatıldı: Excel denetimi, qwen süreç incelemesi, sözleşme özeti + doğrulayıcı arama |
| ~12:20 | Miami faz tablosu script'le gruplandı; toplamlar PDF'teki toplamla birebir doğrulandı |
| ~12:35 | Ajan sonuçları birleştirildi; ana rapor yazıldı (`analiz_2026-10-22\RAPOR_qwen_hata_ve_token_analizi.md`, bölüm 0–9) |
| ~12:45 | Paralel oturumun özeti incelendi; GPS eşiği ölçüldü; rapora bölüm 10 eklendi |
| ~12:55 | Denetim kılavuzu 2.0 okundu; iki skill + ortak araç kutusu kararı; `checks.yaml` üretildi |
| ~13:00 | Drive manuel, önizleme ayrı skill kararı; `scope` alanları eklendi |
| ~13:05 | 3 skill özeti ve 11 maddelik token azaltma önerisi verildi |
| ~13:10 | Madde 1 için plan yazıldı ve onaylandı; sanal ortam kuruldu |
| 13:10–13:45 | 4 paralel ajan + `render_summary` (kendim): 7 temel script, 216 test |
| 13:45–14:05 | Fotoğraf hattı: 3 paralel ajan. Biri oturum limitine takıldı, ön eleme modülünü kendim tamamladım; ajan limit açılınca ölçümü bitirdi |
| 14:05–15:00 | Ultracode açıldı: 5 parçalık iş akışı (15 ajan: yaz, doğrula, düzelt) → 845 test |
| ~15:00 | Son doğrulama, `KAPSAM.md`, kabul sonuçlarının taşınması, devir dokümanı, kalıcı notlar |

## 4. Analiz bulguları

### 4.1 Eindhoven denetimi (Codex, 21 Ekim) özeti

| Alan | Ağırlık | Katkı | Ana neden |
|---|---|---|---|
| Bilgi kartları, kaynaklar | 35 | 18 | Hukuk, destek, ücret ve yerel uygulamada doğrulanmış hatalar |
| Mekân, mahalle, rota | 20 | 11 | Yanlış adres/semt, 9 duraklı rotalar, tarih/mimari ağırlıklı seçim |
| Fotoğraf seçimi | 20 | 14 | Yanlış şehir, yanlış nesne, tablo/gravür, arşiv bağlamı |
| Lisans ve kanıt | 15 | 9 | Orijinal kopyalar teslimde yok, PD/CC0 URL biçimi |
| Teknik teslim | 10 | 3 | Resmî doğrulayıcı: draft 365 hata / 822 uyarı (qwen "0 hata" yazmıştı) |
| **Toplam** | 100 | **55** | Karar: yayına alınmamalı |

Sayımlar Berlin alt sınırını geçiyor: 247 yanıt, 93 mekân, 16 mahalle, 12 rota, 85 sözlük terimi, 264 mekân fotoğrafı, 8 kapak. Yani miktar tamam, doğruluk eksik.

### 4.2 qwen nasıl çalışmış (süreç adli incelemesi)

**Zaman çizelgesi** (yaklaşık 4 sa 25 dk):
- 15 dk URL tahmini.
- 72 dk boyunca 247 yanıt yazımı ile URL denemeleri iç içe yürümüş.
- 40 dk mekân ve rota.
- 5 dk "fotoğraf incelemesi" (yalnız bir liste dökümü).
- 52 dk indirme beklemesi.
- 10 dk geç düzeltmeler.

**Kök nedenler:**
1. **Önce metin, sonra kaynak.** 264 URL bellekten tahmin edilmiş; 72'si (%27) açılmamış. 25 tur yeniden tahmin yapılmış. Berlin örneği, 247 yanıt yazıldıktan sonra açılmış.
2. **`verified=Evet` sabit yazılmış.** Üç script'te kodda sabit; yalnız "HTTP 200 geldi" anlamına geliyor. 24 kaynağın metni 500 karakterden kısa (JS kabuğu), ama hepsine Türkçe "araştırma notu" yazılmış, yani notlar bellekten.
3. **Bilgi hataları üç sınıfta:**
   - (a) Doğru sayfa hiç çekilmemiş: B04, B06, B17, B18.
   - (b) Doğru bilgi önbellekteki sayfada vardı ama tersi yazılmış: B05 velayet, B15 9292 e-bilet.
   - (c) Kaynak olarak hub/anasayfa/boş sayfa gösterilmiş, iddia bellekten: B01, B02, B03, B08, B09, B13, B14.
4. **Fotoğraf eşleştirmesi ad benzerliğiyle yapılmış.** Commons tam metin arama ve alt-dize eşleşmesi kullanılmış; kategori, GPS, tarih ya da içerik türü filtresi yok. Görsel inceleme yapılmamış (272 kayıtta aynı "Otomatik eşleşme" notu). Mekânlar arası fotoğraf havuzu paylaşılmış.
5. **Mekân listesini fotoğraf bulunabilirliği belirlemiş.** Fotoğrafı bulunmayan modern mekânlar elenmiş, yerlerine anıtlar gelmiş: 93 mekânın 53'ü (%57) tarih/mimari.
6. **Kendi QA'sı sözleşmeye bakmıyor.** `qa_check.py` dört şema dosyasının hiçbirini kullanmıyor. `metadata_review_status` sabit "Tamam" yazılmış.
7. **Token israfı kalıpları** (dosya boyutlarından tahmin):
   - Yaklaşık 512 KB içerik araç çağrısı yükü olarak bağlamda kalmış ve her turda yeniden gönderilmiş.
   - Veri kodun içine gömülü olduğu için dosyalar baştan yazılmış.
   - Geç düzeltme döngüleri, bağlam en büyükken çalışmış.

### 4.3 Excel ve teslim dosyalarının yapısal denetimi

- **Yapı sağlam:** 17 sekme; 6. ve 7. satırlar şablonla aynı; doğrulama listeleri ve formüller korunmuş; 0 kırık yabancı anahtar; 272/272 WebP SHA eşleşiyor.
- **T01–T10 doğrulandı ve kök nedenleri bulundu:**
  - Orijinaller yerelde var ama Drive'a yüklenmemiş; "orijinal" dosyalar aslında 1920–2880 px'lik küçük kopyalar; 6 dosyada uzantı `.org&utm…` olmuş.
  - PD lisans URL'si boş (14), CC0 `http://` (17).
  - Kimlikte Türkçe karakter (`tv-akış`).
  - `quick_links` alanı `{label,url}` biçiminde yazılmış, sözleşme `{label,entry}` istiyor.
  - Dört zorunlu sayfa alanı eksik.
  - `compare_json` İngilizce anahtarlarla ve liste değerlerle yazılmış.
  - İki rota 9 duraklı (sınır 8).
  - Yer tutucular kalmış (`5621?`, `[[Hoogstraat`).
- **İçerik zayıflığı işaretleri:**
  - Kaynakların %31'i Wikipedia; 54 kaynak yalnız anasayfa; 28 yanıtın tüm kaynakları anasayfa.
  - 264/272 fotoğraf alt yazısı yalnız mekân adı.
  - 93 mekân notu aynı kalıp cümle.
  - `visual_json` 247 kayıtta boş.
- **Teslim notu beyanları gerçekle çelişiyor:**
  - "0 hata" dendi; resmî doğrulayıcı 364–365 hata veriyor.
  - "~0 MB" dendi; gerçek boyut 316 MB.
  - "1600 px" dendi; gerçek 1920–2880 px.
  - "İnsan gözüyle kontrol" dendi; yalnız yaklaşık 10 kare açılmış.

### 4.4 Miami token analizi

Faz tablosu script'le gruplandı; toplamlar PDF'teki toplamla birebir tuttu. Maliyet-eşdeğeri sütunu Claude fiyat oranlarıyla hesaplandı (önbellekten okuma 0,1×, önbellek dışı girdi 1×, çıktı 5×). Miami bir GPT/Codex oturumu olduğu için bu sütun yalnız göreli ağırlık içindir.

| Grup | Süre | Girdi | Girdi % | Çıktı % | Maliyet-eşdeğeri % |
|---|---|---|---|---|---|
| Mekanik (yerel aktarım, Excel, Drive, panel) | 7,9 dk | 6,56 M | 24,2 | 8,5 | 20,2 |
| İçerik (araştırma, 240 kart, sayfa, sözlük) | 18,6 dk | 6,10 M | 22,5 | 38,7 | 24,9 |
| Fotoğraf (görsel inceleme + medya teslimi) | 15,5 dk | 5,42 M | 20,0 | 19,9 | 22,0 |
| Kurulum (önceki standardı okuma) | 4,9 dk | 3,07 M | 11,3 | 4,6 | 10,6 |
| Rapor (istatistik + PDF) | 4,5 dk | 2,56 M | 9,4 | 8,9 | 8,3 |
| Mekân, mahalle, rota | 11,0 dk | 2,47 M | 9,1 | 18,0 | 10,7 |
| QA | 1,1 dk | 0,96 M | 3,5 | 1,4 | 3,2 |

- **Her çağrı ağır bir bağlam taşıyor.** Ortalama 153K girdi; çıktısı neredeyse hiç olmayan fazlar bile (hava 153 çıktı token'ı) yaklaşık 231K bağlam taşıyor.
- **Son fazlar (24–30) girdinin %43'ü** (11,7M, 16 dk).
- **Kart başına maliyet:** 240 kartın yazımı kart başına ≈ 169 çıktı ve 17,2K girdi token'ı. Çıktı üretimi ucuz; pahalı olan her çağrıda tekrar taşınan bağlam.
- **Yerel modda gereksiz fazlar:** Yerel aktarım, panel kontrolü ve istatistik/PDF (25, 29, 30) girdinin %21,3'ü ve yerel modda hiç gerekmiyor (paralel oturumun bulgusu, aritmetiği doğrulandı).

### 4.5 v7 prompt'u

- 58 KB ≈ 15–18K token ve her alt ajanda yeniden yüklenir.
- AI'ın yapamayacağı işleri (Drive, yönetim ekranı, Monday, DB) anlatan uzun bölümler içeriyor.
- Aynı kurallar 3–4 kez tekrarlanıyor.
- Bağımsız bir kontrol kapısı yok: "kendin ikinci geçişte kontrol et" diyor.
- Berlin örneği eksik bir model: `quick_links`, `arrival_note`, `emergency_url`, `pharmacy_url` ve `advice_entry` alanları yok, sözlükte kaynak yok.
- **Öneri:** Kısa görev iskeleti + yaklaşık 5K token'lık sözleşme özeti + kuralları script olarak uygulamak. Bu öneri `contract_digest.md` ile hazırlandı.

## 5. Paralel oturumun çıktılarıyla karşılaştırma

Aynı gün başka bir oturum `results\RAPOR_Token_ve_Kalite_Analizi_Qwen_Eindhoven_2026-10-22.md`, `skill\hata-onleme-listesi.md` ve `skill\prompt-ek-blok.txt` dosyalarını üretmişti. Sonuçlar büyük ölçüde örtüşüyor. Ayrışan noktalarda ölçüm yapıldı:

1. **"GPS mekâna 1 km'den uzaksa ele" kuralı yanlış.**
   - GPS'li 123 fotoğrafın medyan farkı 1,2 km.
   - 1 km kuralı iyi fotoğrafların 67/123'ünü (%57) atıyor.
   - Denetimin onayladığı kötü fotoğraflardan yalnız 3'ünü yakalıyor; 12 km eşiği yalnız 1'ini (Seattle şişesi).
   - Kötü fotoğrafların 8'i doğru semtte ama yanlış nesneyi gösteriyor; 8'inde GPS hiç yok.
   - Yeni kural: 12 km üstü ret, 2–12 km işaret, asıl filtre metin tabanlı.
2. **"Ana kayıt ≠ orijinal" sayısı 269 değil, 272.** Hiçbir fotoğrafta eşleşmiyor; iki ayrı script'le doğrulandı.
3. **"Qwen resmî doğrulayıcıyı kullanmadı" demek haksız.** Doğrulayıcı `ekler_eindhoven\` içinde yok; v7 prompt'u da doğrulamayı "teknik teslim sorumlusuna" bırakıyor (satır 233, 277, 289). Sorun bir süreç boşluğu.
4. **Barcelona'da "üç koşu" yok.** Yalnız qwen klasörü dolu; ChatGPT ve Gemini klasörleri boş şablon, `RUN_LOG.csv` yalnız başlık satırı.
5. Paralel oturumdan alınanlar:
   - Resmî doğrulayıcının gerçek çalıştırılması.
   - Tekrarlı liste hücresinin okuyucuyu çökertmesi.
   - "Faz başına ~231K taban" hesabı.
   - Tarih/mimari ≤ %35 kotası.

## 6. Denetim kılavuzu 2.0 ve `checks.yaml`

`SEHIR_DENETIM_CHECKLIST.pdf`: 41 sayfa, 120 kontrol; her kontrolde yöntem, geçme koşulu ve kanıt. 25 alt ölçütlü puanlama, AI'a verilecek hazır talimat ve kayıt şablonları içeriyor.

**Değerlendirme:**
- **Kontrollerin çoğu script işi.** Bölümleri düz metin olarak her seferinde LLM'e okutmak yaklaşık 30K token yakar (tahmin) ve sonuç çalıştırmadan çalıştırmaya değişir.
- **Kontroller makine okunur hale getirildi.** `checks.yaml` (PDF metninden script'le çıkarıldı, YAML ayrıştırıcıyla doğrulandı): her kontrolde yürütücü, öncelik, faz, üretim rolü (`gate` / `evidence` / `none`) ve kapsam alanı var.
- **Gerçek dağılım:**
  - Script 62, LLM + kaynak 30, görsel 7, ortam 10, süreç 11.
  - Öncelik: P0 28, P1 75, P2 5, süreç kontrolü 12.
  - Kapsam dışı: Drive 4 kontrol, önizleme 6 kontrol. Yerel kapsam 110 kontrol.
  - Atamalar taslaktır, Atınç onayı gerekir.
- **Kılavuzla ilgili tespitler:**
  - K08/K77 "16 sekmeli yerel profil" esnekliği tanıyor; sözleşme ise 17 sekme istiyor (karar: 17).
  - Önizleme gerektiren kontroller yerelde yapılamaz (karar: ayrı skill).
  - K43 "sabit yarıçapı evrensel red kuralı yapma" diyor; bu, GPS bulgusunu destekliyor.
  - K36 (Portekiz D7/D8) yalnız PT için geçerli.
  - Listede olmayan kontroller: Wikipedia'nın "Resmî" etiketlenmesi, snapshot'sız `verified=Evet`, mekân grubu dengesi için sayısal eşik.

## 7. Alınan kararlar

| # | Karar | Kim | Gerekçe |
|---|---|---|---|
| 1 | İki skill + ortak araç kutusu (`city-pack`, `city-audit`) | Barış (önerim) | Üreten modelin kendi onayı bağımsız kanıt değil (K119); token profilleri farklı |
| 2 | Drive'a yükleme manuel; K01, K03, K109, K110 skill dışında | Barış | Ek token harcatmasın |
| 3 | Önizleme kontrolleri ayrı aşama (`city-preview`, sonra) | Barış | Önizleme dosyalar yüklendikten sonra yapılıyor |
| 4 | 17 sekmeli Excel | Varsayılan (Atınç'a sorulacak) | Şablon ve resmî doğrulayıcı böyle |
| 5 | İnsan inceleme alanları hep `Bekliyor` | Sözleşme | AI kendini onaylayamaz |
| 6 | `build_xlsx` 3 openpyxl iç farkını varsayılan kabul eder | Önerim; itiraz gelmedi | Veri, liste ve formül etkilenmiyor; katı mod bayrakla açılıyor |
| 7 | GPS: 12 km ret, 2–12 km işaret | Ölçüm | 1 km kuralı iyi fotoğrafların %57'sini atıyor |
| 8 | Temas paftası: 30'lu genel tarama, 20'li şüpheli kareler; dHash eşiği 5 | Ölçüm | Token ve okunabilirlik dengesi |

## 8. Araç kutusu

Konum: `corteqs-skills\toolkit\`. Python 3.12.10, `.venv\`, bağımlılıklar Pillow, openpyxl, pytest, pytest-cov ve PyYAML.

**Ortak sözleşme:**
- Konsola tek satır JSON özet, ayrıntı `--out` dosyasına.
- Çıkış kodu 0 temiz / 1 bulgu / 2 kullanım hatası.
- Gerçek veri salt okunur.
- Excel satır 7 anahtarlarına göre okunur.
- Atınç'ın araçları kopyalanmaz, `--tools` ile gösterilir.

### 8.1 Excel ve paket

| Script | Amaç | Kontroller | Gerçek veri sonucu (qwen Eindhoven) | Sınırlar |
|---|---|---|---|---|
| `common.py` | Ortak yardımcılar: SHA, güvenli yol, satır 7 okuyucu, Berlin sayıları, fotoğraf kümeleme | — | — | — |
| `xlsx_dump.py` | Excel → sayfa başına JSONL ve sayım; AI Excel'i bağlamına yüklemez | K10 | 14 sayfanın sayıları denetimle birebir | — |
| `inventory.py` | Dosya envanteri, SHA, gerçek format, Excel yolu karşılaştırması | K02, K15, K57, K58, K80, K84, K114 | 1367 dosya / 316,19 MB; eksik 0; SHA uyuşmazlığı 0; bozuk uzantı 6; `file_ne_original` 272 | `total_mb` ondalık MB (301,5 MiB) |
| `build_xlsx.py` + `xlsx_rules.py` + `xlsx_fidelity.py` | JSONL'i şablona anahtara göre yazar. Reddettikleri: liste dışı değer, `=` enjeksiyonu, 32.767 karakter aşımı, AI'ın kendi onayı, kapasite aşımı. Tekrarlı liste hücrelerini temizler. Sonda biçim sadakat kontrolü yapar | K08, K09, K13, K97 | Ham qwen verisi 272 satırda reddedildi (`Tamam`). Düzeltilmiş veriyle 2.112 satır yazıldı; 53.742 hücreden yalnız beklenen 274'ü farklı | openpyxl docProps ekler, sharedStrings kaldırır (kabul edildi) |
| `validate_all.py` + `extra_checks.py` | Resmî doğrulayıcıyı salt okunur çalıştırır; tekrarlı liste çökmesini tolere eder; hataları sınıflar; 6 ek kontrol | K11–K14, K45, K46, K49, K68–K70, K77, K78, K85–K89, K95 | 364 yapı / 822 uyarı / 323 medya hatası; tekrarlı hücre 2; ek kontroller: yer tutucu 3, Resmî-Wikipedia 21, snapshot'sız `verified` 233, ortak koordinat 2 grup, yalnız anasayfa kaynaklı yanıt 28, tarih payı %57. Düzeltilmiş Excel ile yapı hatası 92 | Codex 365, paralel oturum 363 sayıyor; aynı dosya, fark açıklanamadı. `emit` modu gerçek veride denenmedi |
| `render_summary.py` + `summary_metrics.py` | Teslim özeti, açık konular ve ilerleme kaydı yalnız ölçümden; "editör onayladı" asla yazılmaz | K17, K22, K24, K66, K83 | "DÜZELTME GEREKLİ"; 22 engelleyici, 8 bilgi maddesi | URL çalışma sayısını ölçmez |
| `impact.py` | Bir kayıt değişince bağımlıları bulur; yalnız onlar yeniden denetlenir | K99, K118 | Wilhelminaplein: denetimin 3 bağı + 12 fazla; KVK kaynağı: B09'un iki kartı; diff modu 2 değişiklik → 12 etkilenen satır | Kısa adlarda metin eşleşmesi kaçıyor; aynı URL'li kaynaklar birbirine bağlanmıyor |

### 8.2 Kaynak ve içerik

| Script | Amaç | Kontroller | Gerçek veri sonucu | Sınırlar |
|---|---|---|---|---|
| `web_fetch.py` | Kibar HTTP: alan başına 2 istek, Retry-After, önbellek, çerez yok | — | — | 398 satır (sınıra yakın) |
| `url_check.py` | URL sınıflama ve sonuçları satırlara geri dağıtım | K49–K52, K56 | 337 URL / 782 ilişki: çalışıyor 314, teyit açık 22 (20 TLS), kesin bozuk 0; Wikipedia 72, Resmî-Wikipedia 21, anasayfa 54. Codex'in 404 dediği acm.nl bugün açılıyor | ind.nl, digid.nl, werk.nl Python'da TLS hatası verip tarayıcıda açılıyor; çerez döngüsü 2 site; 107 harita arama bağlantısı politika kararı |
| `fetch_snapshot.py` | Sayfayı HTML + temiz metin + SHA olarak kaydeder (iddia defterinin girdisi) | K76, T09 | 10 URL: `--retry-transient` ile 10/10; 1 ince metin (IND) | — |
| `claim_extract.py` + `claim_check.py` | Karttaki para/yüzde/süre/yaş/gün iddialarını çıkarır ve kaynak metninde arar (bölüm 16 CLAIM kaydı) | K29, K34, K37, K40 desteği | 386 iddia / 174 kart. Bilgi hatalarından 11/12 kart işaretli; hatalı değerin kendisi 7/12 (B01, B03, B08, B09, B11, B17, B18). Kaçan B15 (sayısal değil) | "supported" yalnız tutarlılık demek; sayısal olmayan iddialar LLM/insan işi |
| `text_quality.py` | Kopya ve kalıp metin, "kurumdan doğrulayın" dolgusu, eylem bağlantısı olmayan kart, `visual_json` | K21, K25, K27, K28, K33, K104 | Not 93/93 aynı; açıklama 272/272 aynı; caption 264/272 = başlık; yer tutucu 115; tek bağlantısı harita olan kart 88; kaçamak uyarılı kart 98/356 | Etiket alanı kümeleri gürültü yapıyor |
| `editorial_score.py` | Kılavuz bölüm 20'nin 25 alt ölçütü ve karar kuralları | K100, K101, K115–K117 | Kılavuz örneği %71 ("DÜZELTME GEREKLİ"); Codex kategorileri %55 | Tam ölçüt uygulanmazsa karar "KANIT EKSİK" (Atınç kararı) |

### 8.3 Fotoğraf

| Script | Amaç | Gerçek veri sonucu |
|---|---|---|
| `commons_search.py` | Commons aday arama (Wikidata P18/P373 → kategori → geosearch → metin), Wikimedia kurallarına uygun, önbellekli | 3 mekân: 9 istek, 90 aday, 0 hata; ikinci çalıştırma 0 istek |
| `photo_candidates.py` + `photo_rules.py` + `photo_prefilter.py` | Meta veriyle ön eleme, mekân başına kısa liste | Tablo aşağıda |
| `contact_sheet.py` + `image_hash.py` | Numaralı temas paftası + dHash yakın kopya | 272 kare: tek tek ~626K token yerine 20'li 14 pafta ~26K, 30'lu 10 pafta ~16K. dHash eşik 5: Sint-Catharinakerk (uzaklık 2) ve Bijenkorf (uzaklık 4) yakalanıyor; 10'a kadar başka çift yok |
| `download_plan.py` | Atınç'ın `download_media.py` kuyruğu için plan | Uzantı query string'siz; ana kayıt = orijinal; yalnız upload.wikimedia.org |

**Ön elemenin karışıklık tablosu** (272 fotoğraf; iki ayrı script'le yeniden üretildi):

| Denetimin dediği | Adet | Ret | İşaret (gözle bakılacak) | Kaçan |
|---|---|---|---|---|
| Yanlış fotoğraf | 23 | 9 | 7 | 7 |
| Arşiv karesi | 8 | 0 | 8 | 0 |
| Düşük çözünürlük | 13 | 0 | 13 | 0 |
| Hak incelemesi | 13 | 0 | 11 | 2 |
| İyi | 215 | **0** | 32 | 183 |

- **Kaçan 7 kare** (bina cepheleri #241, #247–249; tabela yakın çekimi #148–149; yanlış su kulesi #140) meta veriyle görülemiyor; ancak gözle yakalanır. Paftada #255 (başka kasabadaki çiftlik), #258 (bira şişesi) ve #241 (pazar yerine cephe) gözle ayırt edildi.
- **Uyarı:** Kurallar aynı 272 fotoğrafta ayarlandı. Gerçek başarı ilk yeni şehirde ölçülecek.

### 8.4 Ölçüm

| Script | Amaç | Not |
|---|---|---|
| `phase_usage.py` | Oturum kaydından faz başına token ve süre | Aynı mesaj kayıtta birden çok satırda tekrar ediyor (bu oturumda yaklaşık 2,4 kat); `message.id` ile tekilleştiriyor, yoksa ölçüm şişer |

**Kapsam durumu** (`KAPSAM.md`): 62 script kontrolünden 42 tam, 18 kısmi, 2 yok (K73 özel stok lisansı, K81 incelenen kare = teslim edilen kare).

## 9. Kalite güvencesi: yöntem ve yakalanan hatalar

**Yöntem:**
1. Önce test, kırmızıyı gör, sonra kod. Ajanlar `red_first` alanıyla raporladı; bir ajan "testleri önce yazdım ama kırmızı çalıştırmadım" dedi, bu dürüstçe kayda geçti.
2. Her parça gerçek qwen paketinde salt okunur kabul testinden geçti; beklenen ve gözlenen sayılar yan yana kondu.
3. Son partide her parçayı ayrı bir doğrulayıcı ajan kırmaya çalıştı; ciddi bulgular önce testle gösterildi, sonra düzeltildi.
4. Ajan raporlarına güvenilmedi. Test paketi ve kilit sayılar kendim yeniden çalıştırıldı. Qwen Excel SHA'sı, paket mtime'ı ve Atınç'ın klasörü her turda kontrol edildi.

**Yakalanan ve düzeltilen hatalar:**

| Bulgu | Kim buldu | Sonuç |
|---|---|---|
| Paralel oturumun "269" sayısı | Envanter ajanı + bağımsız sayım | 272 olarak düzeltildi |
| GPS 1 km kuralı | Ölçüm | 12 km ret / 2–12 km işaret |
| `xlsx_rules` Atınç'ın klasörüne `__pycache__` yazıyordu | Klasör kontrolü | Önce kırmızı test, sonra düzeltme; testle kilitlendi |
| `validate_all` hata sınıfını metindeki " : " ile yanlış kesiyordu | Gerçek veri çıktısı | Testle düzeltildi |
| `render_summary` aynı Berlin eksiğini iki kez listeliyordu | Test | Düzeltildi |
| `editorial_score`: hedef ölçütü "uygulanmaz" girilince eksik hedef atlanıp "HAZIR" veriliyordu (HIGH) | Doğrulayıcı | Testle düzeltildi |
| `editorial_score`: geçmeyen birim bulguya bağlı değilse "HAZIR" çıkıyordu (MEDIUM) | Doğrulayıcı | Düzeltildi |
| `text_quality` ve `impact`: `--out` girdi Excel'iyle aynı olursa Excel'in üzerine yazıyordu (MEDIUM) | Doğrulayıcı | Kontrol eklendi, çıkış 2 |
| `text_quality`: büyük kopya adım bloklarını sessizce atlıyordu (MEDIUM) | Doğrulayıcı | Düzeltildi |
| `claim_extract`: "güncel" kelimesini "gün" süre birimi sayıyordu, "Euro 4" emisyon sınıfını para sayıyordu (MEDIUM) | Doğrulayıcı | Türkçe ek listesi ve € / EUR şartı; 4 sahte iddia kalktı |
| `fetch_snapshot`: geçici hata önbellekte sonsuza kalıyordu (MEDIUM) | Doğrulayıcı | `--retry-transient` eklendi |
| Temas paftası etiketlerinde tekrar eden şehir öneki, dHash eşiği 3 | Ajan önerisi + kendi gözlemim | Önek atılıyor, eşik 5 |
| `KAPSAM.md` bir kez eski sayılarla üretildi (edit uygulanmamıştı) | Kendi kontrolüm | Yeniden üretildi |

**Son durum:** 845 test geçiyor, kapsam %97. Qwen Excel SHA-256 `55366c21…c104b` değişmedi; Atınç'ın klasöründe yeni dosya yok; şablon değişmedi.

## 10. Bu oturumun token ve süre kullanımı

`phase_usage.py` ile ölçüldü; mesajlar tekilleştirildi. Ölçüm oturumun büyük kısmını kapsıyor, son birkaç mesaj dahil değil.

| Kapsam | Model çağrısı | Toplam girdi | Önbellek dışı girdi | Çıktı |
|---|---|---|---|---|
| Ana oturum + doğrudan alt ajanlar (10 ajan) | 393 | 112,3 M | 4,66 M | 305 K |
| 5 parçalık iş akışı (15 ajan) | 451 | 67,3 M | 2,22 M | 174 K |
| **Toplam** | **844** | **≈ 179,6 M** | **≈ 6,88 M** | **≈ 479 K** |

**Yorum:**
- Bu bir şehir üretimi değil; tek seferlik bir analiz ve araç geliştirme oturumu. Miami ile doğrudan karşılaştırılmaz (Miami tek şehir: 27,2M girdi, 0,78M önbellek dışı, 131K çıktı).
- Oturum çok uzadığı için her çağrıda taşınan bağlam büyüdü. Bu, analiz ettiğimiz sorunun ta kendisi; devir dokümanının yazılma nedeni de bu.
- Paralel ajanlar ve iş akışı bağlamı küçük tuttu: 15 ajanlık iş akışı, ana oturumun yaklaşık yarısı kadar girdiyle 5 parçayı yazdı, doğruladı ve düzeltti.
- İş akışının duvar saati yaklaşık 52 dk (15 ajan; ilk 5'i paralel).

## 11. Üretilen dosyalar

| Dosya / klasör | İçerik |
|---|---|
| `analiz_2026-10-22\RAPOR_qwen_hata_ve_token_analizi.md` | Ana analiz raporu (bölüm 0–11) |
| `analiz_2026-10-22\contract_digest.md` | v7 sözleşme özeti |
| `analiz_2026-10-22\validator_spec.md` | 70 kontrollük doğrulayıcı tanımı |
| `analiz_2026-10-22\checks.yaml` | K01–K120 (araç kutusundaki kopyası esas) |
| `analiz_2026-10-22\SEHIR_DENETIM_CHECKLIST_metin.txt` | Kılavuzun düz metni |
| `analiz_2026-10-22\kabul_sonuclari\` | Gerçek veri kabul çıktıları: envanter, doğrulayıcı, render, fotoğraf kararları, paftalar, iddia defteri, URL sonuçları, metin kalitesi, bağımlılık, puan |
| `analiz_2026-10-22\yardimci_scriptler\` | `miami_phases.py`, `gps_threshold.py`, `verify_prefilter.py`, `coverage_map.py`, `build_checks_yaml.py` |
| `corteqs-skills\toolkit\scripts\` (26 modül), `tests\` (845 test), `checks.yaml`, `KAPSAM.md`, `pytest.ini`, `requirements.txt` | Araç kutusu |
| `.venv\` | Sanal ortam |
| `DEVIR_2026-10-22_corteqs_skill.md` | Kısa devir dokümanı |
| Kalıcı notlar (`~\.claude\projects\...\memory\`) | Proje kararları; sade Türkçe tercihi |

## 12. Açık noktalar ve riskler

1. **Ön eleme kuralları örneklem içi ayarlandı.** Yeni şehirde yeniden ölçülmeli.
2. **Sayısal olmayan bilgi iddiaları** (B02, B10, B15, B16) script'le yakalanmıyor; bağımsız LLM denetçisi veya insan gerekiyor.
3. **Resmî doğrulayıcı sayı farkı** (364 / 365 / 363) açıklanamadı.
4. **TLS zinciri:** IND, DigiD ve werk.nl Python'da açılmıyor. Windows sertifika deposunu kullanmak bir politika kararı.
5. **`validate_all --mode emit`** gerçek veride denenmedi.
6. **qwen token sayaçları** ölçülmedi (`kilo.db` izni yok).
7. **Atınç'a sorulacaklar:** 17 sekme zorunluluğu; "yerel paket denetimi" etiketi sapması; doğrulayıcı sürüm farkı; tam ölçüt uygulanmazsa payda.
8. **`skill\prompt-ek-blok.txt` kural 16 (GPS 1 km)** prompt'a eklenmeden önce düzeltilmeli.
9. **Eksik kontroller:** K73 ve K81 script'i yok. Commons aramasında kaynak kotası eksikti; sonradan yapıldı, bkz. bölüm 13.

## 13. Bu oturumdan sonra yapılanlar (bilgi için)

Bu oturum devir dokümanıyla kapandıktan sonra ikinci bir oturum devam etmiş. Dosya sisteminde görülenler (içerikleri bu raporda doğrulanmadı):

- **Skill dosyaları:**
  - `corteqs-skills\city-pack\SKILL.md`
  - `corteqs-skills\city-pack\agents\`: yanıt yazarı, mekân yazarı, fotoğraf incelemesi, iddia denetçisi
  - `corteqs-skills\city-pack\references\`: `contract_digest.md`, `manifest.schema.json`
  - `corteqs-skills\city-audit\SKILL.md`
- **Kalıcı nota göre:**
  - Skill'ler projeye kuruldu.
  - Commons arama kota düzeltmesi yapıldı (853 test).
  - Pilot şehir kararı: **Eindhoven baştan üretilecek** ve qwen ile Codex denetimiyle kıyaslanacak.
