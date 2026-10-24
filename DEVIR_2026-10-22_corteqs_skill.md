# Devir: Corteqs şehir paketi skill'leri (22 Ekim 2026)

Bu doküman yeni bir Claude Code oturumunun, önceki oturumun sohbet geçmişini okumadan kaldığı yerden devam etmesi için yazıldı. Önceki oturum çok büyüdüğü için kapatılıyor.

**Sahibi:** Umut Barış Terzioğlu (UBT). Ekip: Atınç Akçayöz (teknik lider, resmî araçların sahibi), Burak Akcakanat.
**Çalışma klasörü:** `C:\temp_private\corteqs\0000_newera` (yeni her dosya buraya).
**İletişim tercihi:** Barış'la sade Türkçe konuş; teknik terimle karar sorma (profil, fidelity, SHA, openpyxl gibi). Önce ne olduğunu 2–3 cümleyle anlat, sonra tek net öneri ver ("aksini söylemezsen böyle yapıyorum").

---

## 1. Amaç

- **AMAÇ 1:** Şehir paketini (Berlin standardı, Corteqs v7 sözleşmesi) **en az token ile en yüksek kalitede** üretmek.
- **AMAÇ 2:** Süreci Claude Code skill'lerine dönüştürmek (VS Code içinde çalışacak).

Neden: qwen3.8-max ile üretilen Eindhoven paketi (CITY-039) bağımsız Codex denetiminde **%55** aldı ve "yayına alınmamalı" kararı çıktı. Miami (Codex) token raporu, girdi token'ının yalnız %22,5'inin içerik yazımına gittiğini gösterdi; kurulum + mekanik işler + rapor + QA %48,4, fotoğraf işi %20.

## 2. Alınan kararlar (değiştirme, sorgulama)

1. **Üç skill + ortak araç kutusu:**
   - `city-pack`: üretim. Yalnız script kapıları çalışır, kendini asla onaylamaz.
   - `city-audit`: bağımsız denetim. Temiz bağlamda, salt okunur çalışır; kademeler L0 (yalnız script), L1 (riske göre LLM + görsel), L2 (tam).
   - `city-preview`: **sonra yazılacak.** Dosyalar Drive'a yüklendikten sonraki web önizleme kontrolleri.
2. **Drive'a yükleme manuel** (Barış yapar, skill çalıştırmaz, token harcamaz): K01, K03, K109, K110.
3. **Önizleme ayrı aşama:** K92, K93, K94, K103, K111, K112 → `city-preview`. Yerel kapsam **110 kontrol**.
4. **Excel 17 sekme** (FotoğrafKaynakları dahil); Atınç'ın şehir dosyası zaten böyle.
5. **İnsan inceleme alanları** (`metadata_review_status`, `pixel_review_status`, `rights_status`) AI tarafından hep `Bekliyor`. "0 hata" yalnız resmî doğrulayıcı çıktısıyla yazılır.
6. `build_xlsx` openpyxl'in 3 iç zip farkını (docProps ekleme, sharedStrings kalkma) **varsayılan olarak kabul eder**; `--strict-parts` ile kapanır. Veri, liste, formül etkilenmiyor.
7. Fotoğrafta **GPS 1 km ret kuralı YANLIŞ** (iyi fotoğrafların %57'sini atar). Kullanılan kural: 12 km üstü ret, 2–12 km işaret; asıl filtre metin tabanlı.

## 3. Nerede ne var

| Yol | İçerik |
|---|---|
| `corteqs-skills\toolkit\scripts\` | 26 Python modülü (aşağıda) |
| `corteqs-skills\toolkit\tests\` | 845 test, kapsam %97 |
| `corteqs-skills\toolkit\checks.yaml` | K01–K120 makine okunur: yürütücü (S script / L LLM / V görsel / E ortam / M süreç), öncelik, faz, `scope` (drive-manual / preview-later) |
| `corteqs-skills\toolkit\KAPSAM.md` | Hangi script kontrolü hangi script'te (62 S kontrolünden 42 tam, 18 kısmi, 2 yok) |
| `.venv\` | Python 3.12.10 + Pillow, openpyxl, pytest, pytest-cov, PyYAML |
| `analiz_2026-10-22\RAPOR_qwen_hata_ve_token_analizi.md` | Ana analiz raporu (bölüm 0–11) |
| `analiz_2026-10-22\contract_digest.md` | v7 sözleşme özeti (~5K token); 58 KB prompt + şemalar + Berlin Excel yerine okunur |
| `analiz_2026-10-22\validator_spec.md` | 70 kontrollük doğrulayıcı tanımı |
| `analiz_2026-10-22\SEHIR_DENETIM_CHECKLIST_metin.txt` | Denetim kılavuzu 2.0'ın düz metni (bölüm 16 kayıt şablonları, bölüm 20 puanlama) |
| `analiz_2026-10-22\kabul_sonuclari\` | Gerçek veride kabul testi çıktıları (her script için) |
| `analiz_2026-10-22\yardimci_scriptler\` | Ölçüm script'leri (Miami fazları, GPS eşiği, ön eleme doğrulaması, kapsam tablosu, checks.yaml üretici) |
| `araclar\arac\` | **Atınç'ın resmî v7 doğrulayıcısı.** Kopyalanmaz, `--tools` ile gösterilir. `check_delivery.py` paket klasörüne yazar; denetimde kullanma, `validate_all.py --mode audit` kullan |
| `eindhoven_qwen38_max\` + `_work_eindhoven\` | qwen çıktısı ve çalışma izleri (test verisi, **salt okunur**) |
| `ekler_eindhoven\` | Atınç'ın şehir şablonu ve şemalar (**salt okunur**) |
| `skill\hata-onleme-listesi.md`, `skill\prompt-ek-blok.txt` | Paralel oturumun yazdığı 20 kural. **Kural 16 (GPS 1 km) yanlış**, prompt'a eklemeden düzelt |

Kalıcı notlar: `C:\Users\baris-terzioglu\.claude\projects\c--temp-private-corteqs-0000-newera\memory\` (2 not: proje kararları, sade Türkçe tercihi).

## 4. Araç kutusu: script'ler ve doğrulanmış sonuçlar

Her script: konsola **tek satır JSON özet**, ayrıntı `--out` dosyasına; çıkış 0 temiz / 1 bulgu / 2 kullanım hatası. Hepsi gerçek qwen paketinde salt okunur denendi. Paket ve şablon değişmedi (qwen Excel SHA-256 `55366c21…c104b`, Codex'in denetlediği dosyayla aynı).

**Excel ve paket**
| Script | Ne yapar | Gerçek veride doğrulanan |
|---|---|---|
| `xlsx_dump.py` | Excel → sayfa başına JSONL + sayım | 14 sayfa sayısı denetimle birebir (247/93/16/549/12/85/10/233/272/272/37/0/272) |
| `inventory.py` | Dosya, SHA, gerçek format, Excel yolları | 1367 dosya, 316,19 MB (qwen "~0 MB" demişti); 6 bozuk uzantı; `file_ne_original` **272/272** (diğer oturumun "269"u yanlış) |
| `build_xlsx.py` (+ `xlsx_rules.py`, `xlsx_fidelity.py`) | JSONL → şablona yazım, liste dışı değer / `=` / AI kendi onayı reddi, biçim sadakat kontrolü | qwen verisi geri yazılınca 272 `Tamam` reddedildi; düzeltilmiş veriyle 53.742 hücrede yalnız beklenen 274 fark |
| `validate_all.py` (+ `extra_checks.py`) | Resmî doğrulayıcıyı paketi değiştirmeden çalıştırır, hataları sınıflar | 364 yapı hatası / 822 uyarı / 323 medya hatası; düzeltilmiş Excel ile yapı hatası **92**'ye iniyor. (Codex 365, diğer oturum 363: aynı dosya, fark açıklanamadı) |
| `render_summary.py` (+ `summary_metrics.py`) | TESLIM_OZETI / ACIK_KONULAR / ILERLEME_KAYDI yalnız ölçümden | qwen'in beyanlarıyla farklar listelendi |
| `impact.py` | Bir kayıt değişince bağımlıları (yalnız onları yeniden denetlemek için) | Wilhelminaplein: denetimin 3 bağı + 12 fazlası; KVK kaynağı: B09'un iki kartı bulundu |

**Kaynak ve içerik**
| Script | Ne yapar | Gerçek veride doğrulanan |
|---|---|---|
| `web_fetch.py`, `url_check.py` | Kibar HTTP (alan başına 2 istek, Retry-After, önbellek), URL sınıflama, satırlara geri dağıtım | 337 URL / 782 ilişki: 314 çalışıyor, 22 erişim teyidi açık (20 TLS: ind.nl, digid, werk.nl), 0 kesin bozuk. Wikipedia 72, "Resmî" etiketli Wikipedia 21, anasayfa 54 (denetimle aynı). Codex'in 404 dediği acm.nl bugün 200 |
| `fetch_snapshot.py` | Sayfa → HTML + temiz metin + SHA (iddia defterinin girdisi) | 10 URL'lik örnek; `--retry-transient` ile 10/10 |
| `claim_extract.py`, `claim_check.py` | Karttaki sayı/süre/ücret/yaş kaynak metninde geçiyor mu | 386 iddia; Eindhoven bilgi hatalarından **11/12 kart işaretlendi**, hatalı değerin kendisi 7/12 (B01, B03, B08, B09, B11, B17, B18). Kaçan: B15 (sayısal değil) |
| `text_quality.py` | Kopya/kalıp metin, "kurumdan doğrulayın" dolgusu, eylem bağlantısı olmayan kart, visual_json | Mekân notu 93/93 aynı, `modifications` 272/272 aynı, caption 264/272 = başlık, `cost '-'` 39; 88 kartın tek bağlantısı harita |
| `editorial_score.py` | Kılavuz bölüm 20 puanı ve karar | Kılavuz örneği %71; Codex kategorileri %55 |

**Fotoğraf**
| Script | Ne yapar | Gerçek veride doğrulanan |
|---|---|---|
| `commons_search.py` | Commons aday arama (Wikidata P18/P373 → kategori → geosearch → metin), önbellek, istek tavanı | 3 mekân: 9 istek, 90 aday; ikinci çalıştırma 0 istek |
| `photo_candidates.py`, `photo_rules.py`, `photo_prefilter.py` | Meta veriyle ön eleme, mekân başına kısa liste | 272 fotoğraf: **0 iyi fotoğraf reddedildi**; yanlış 23'ün 9'u ret, 7'si işaret, 7'si kaçtı (cephe kimliği, tabela, yanlış su kulesi: yalnız gözle); arşiv 8/8, düşük çözünürlük 13/13; görsel incelemeye %26 |
| `contact_sheet.py`, `image_hash.py` | Numaralı temas paftası + dHash yakın kopya | 272 fotoğraf: tek tek ~626K token yerine 14 pafta ~26K (20'li) veya 10 pafta ~16K (30'lu). dHash eşik 5: Bijenkorf ve Sint-Catharinakerk çiftleri yakalanıyor |
| `download_plan.py` | Atınç'ın `download_media.py` kuyruğu için plan | Dosya adı `Fotoğraflar/<şehir>_<slug>_NN.<ext>`, query string'siz uzantı; ana kayıt = orijinal |

**Ölçüm**
| Script | Ne yapar | Not |
|---|---|---|
| `phase_usage.py` | Oturum kaydından faz başına token/süre (`mark` + `report`) | Aynı mesaj kayıtta ~2,4 kez tekrar ediyor; script `message.id` ile tekilleştiriyor. Bu oturumun ilk ölçümü: 46M toplam girdi, 1,44M önbellek dışı, 172K çıktı (o ana kadar) |

Testleri çalıştırma:
```powershell
Set-Location C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit
& C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --cov=scripts
```
Beklenen: 845 passed, kapsam %97.

## 5. Sıradaki işler (öncelik sırasıyla)

1. **Skill dosyaları** (`corteqs-skills\` altında):
   - `city-pack\SKILL.md`: fazlar (manifest → kaynak keşfi + snapshot → yanıtlar + iddia defteri → mekân/mahalle/rota → fotoğraf → birleştirme + doğrulama → teslim özeti), her fazda hangi script, hangi alt ajan, kapılar, faz başına `phase_usage mark`.
   - `city-audit\SKILL.md`: L0 / L1 / L2, `checks.yaml`'a göre yürütme, bölüm 16 kayıt şablonları (CHECK / ISSUE / CLAIM / PHOTO / URL), `editorial_score` ile karar.
   - `manifest.json` şeması (fazlar arası taşınan tek dosya).
   - Alt ajan talimatları: yanıt yazarı (iddia defteri formatında), mekân, fotoğraf görsel kontrolü (temas paftası, 30'lu genel / 20'li şüpheli), bağımsız iddia denetçisi.
   - Referans: `contract_digest.md` ve `checks.yaml` skill klasörüne alınır. Berlin Excel'i ve 58 KB prompt okunmaz.
2. **Ülke paketi yapısı:** Hollanda ulusal kartları (WW, kira desteği, KVK, devir vergisi, kinderbijslag, kwalificatieplicht…) bir kez doğrulanır, geçerlilik tarihiyle saklanır, şehirlerde yeniden kullanılır. 421 şehirlik katalogda en büyük token kazancı.
3. **Küçük düzeltmeler:**
   - ~~`commons_search`: kaynak başına kota.~~ **YAPILDI (22.10, 2. oturum):** sıra Wikidata → kategori → isim → geosearch; geosearch `--geo-max` (varsayılan 5); planda QID yoksa adla Wikidata araması, yalnız koordinatı ≤2 km olan kabul. Aynı 3 mekânda: eski 88 geosearch + 2 isim → yeni 2 P18 + 66 kategori + 22 isim + 0 geosearch; 3 QID de doğru. Not: müze kategorisi içerideki sanat eserlerinin fotoğraflarını da getiriyor (ek hak riski; ön eleme + görsel kontrol). Testler 853.
   - Eksik 2 script kontrolü: K73 (özel stok lisansı, ör. Unsplash), K81 (incelenen kare = teslim edilen kare).
   - `skill\prompt-ek-blok.txt` kural 16'yı (GPS 1 km) düzelt.
4. **Pilot şehir:** Uçtan uca bir deneme, `phase_usage` ile ölçüp Miami raporuyla yan yana koy. **Barış'a sorulacak:** Eindhoven'ı baştan mı üretelim (qwen ve Codex denetimiyle doğrudan kıyas), yoksa yeni şehir mi (Aberdeen / Alicante / Barcelona)?

## 6. Bilinen sınırlar ve açık noktalar

- **Ön eleme kuralları aynı 272 fotoğrafta ayarlandı** (örneklem içi). Gerçek başarı ilk yeni şehirde ölçülecek.
- **`claim_check` "supported" doğruluk değil, tutarlılık demek.** Sayısal olmayan iddialar (B15 "9292 bilet satmaz", B16 posta etiketi, B02/B10 kurallar) script'le yakalanmıyor; LLM veya insan gerekir. Uzun sayfalarda küçük sayılar ilgisiz eşleşebilir (örnekte 1/10).
- **TLS:** ind.nl, digid.nl, werk.nl Python'da sertifika zinciri hatası veriyor (tarayıcıda ve curl'de açılıyor). Doğrulama kapatılmadı; bu URL'ler "erişim teyidi açık" kalıyor. Windows sertifika deposunu kullanmak bir politika kararı.
- natlab.nl ve parktheater.nl çerez isteyen yönlendirme döngüsü (çerez gönderilmiyor). 107 Google Maps arama bağlantısı bulgu sayılmıyor, bu bir politika kararı.
- `impact.py`: aynı URL'li yinelenen kaynaklar birbirine bağlanmıyor; kısa adlar (ör. "Tongelreep") metin eşleşmesinde kaçıyor.
- `editorial_score`: bir hedef dışı ölçütün tamamı "uygulanmaz" ise karar "KANIT EKSİK" (kılavuz bunu Atınç kararına bırakıyor).
- `validate_all --mode emit` (resmî teslim dosyalarını üretme) yalnız sahte araçlarla test edildi, gerçek veride denenmedi.
- qwen'in gerçek token sayaçları ölçülmedi: Kilo `kilo.db` okuma izni verilmedi. **O dosyayı açma.**
- Birkaç modül 400 satır sınırına yakın (`web_fetch.py` 398); bazılarında PEP8 çift boş satır yerine tek boş satır var.

## 7. Atınç'a sorulacaklar

1. Yeni şehirlerde 17 sekme zorunlu mu? (Varsayılan: evet.)
2. Önizleme ve Drive kontrolleri ayrı aşamada; `city-audit` kararı "yerel paket denetimi" etiketiyle verilecek. Bu sapma kabul mü?
3. Resmî doğrulayıcı aynı Excel'de 364 hata verirken Codex 365 raporladı: hangi sürüm/ayar?
4. Bir ölçütün tamamı uygulanamazsa puan paydası nasıl olacak (bölüm 20)?

## 8. Çalışma kuralları (yeni oturum için)

- Gerçek veri salt okunur: `eindhoven_qwen38_max\`, `_work_eindhoven\`, `ekler_*\`, `araclar\`. Kabul çıktıları `analiz_*\kabul_sonuclari\` veya geçici klasöre.
- `araclar\` içinden import ederken `sys.dont_write_bytecode = True` (oraya `__pycache__` yazılmasın; bir kez oldu, temizlendi ve testle kilitlendi).
- Yeni script: önce test (kırmızıyı gör), sonra kod; tek satır JSON özet; çıkış kodları 0/1/2; kapsam ≥ %80.
- Ajan raporlarına güvenme; sayıları kendin yeniden üret (bu oturumda iki rapor düzeltildi: 269 → 272, B05/B15 sınıfı).
- Barış'a sade Türkçe; tek net öneri.

## 9. Yeni oturuma ilk mesaj (kopyala-yapıştır)

> `C:\temp_private\corteqs\0000_newera\DEVIR_2026-10-22_corteqs_skill.md` dosyasını oku. Sonra `corteqs-skills\toolkit` içindeki testleri çalıştırıp 845 testin geçtiğini doğrula. Ardından bölüm 5'teki 1. işe başla: `city-pack` ve `city-audit` SKILL.md dosyalarını, `manifest.json` şemasını ve alt ajan talimatlarını yaz. Mevcut script'leri kullan, yeniden yazma. Bana sade Türkçe yaz.
