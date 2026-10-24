# CorteQS Şehir Rehberi – Session Özeti (VS Code'a devir)

Tarih: 2026-10-22 · Hazırlayan: UBT (Umut Barış Terzioğlu) · Ekip: Atınç Akçayöz, Burak Akcakanat
Çalışma klasörü: `C:\temp_private\corteqs\0000_newera` (**yeni her dosya buraya yazılır**)

---

## 1. Amaç

1. Atanan şehirler için Berlin standardında (Corteqs v7) şehir rehberi paketi üretmek: Aberdeen (CITY-003), Alicante (CITY-004), Barcelona (CITY-009), Eindhoven (CITY-039).
2. Farklı yapay zekâ ve efor seviyeleriyle yerelde deneyip sonuçları karşılaştırmak; yalnız en iyisini Drive'a yüklemek.
3. **AMAÇ 1:** Token kullanımını azaltırken kaliteyi artırmak. **AMAÇ 2:** Uçtan uca süreci Claude Code skill'ine dönüştürmek (VS Code'da çalışacak).

## 2. Şu ana kadar yapılanlar

- Dört şehir için v7 üretim promptları hazırlandı (`AI_URETIM_PROMPTU_v7_<ŞEHİR>.txt`); Aberdeen, Barcelona ve Eindhoven için `_LOKAL.txt` varyantı da var (Drive/UAT/Monday/DB adımları çıkarıldı, çıktılar yerelde, "YEREL DENEME – Drive'a yüklenmedi" notu).
- Ek dosya paketleri hazırlandı: `ekler/`, `ekler_barcelona/`, `ekler_eindhoven/` (şehir xlsx, Berlin örneği, şablon, JSON şemaları, kontrol listesi). Alicante için `alicante_hazirlik/`.
- `results/` klasör sistemi kuruldu (README, RUN_LOG.csv, `_SABLON/`). Barcelona için üç koşu var: `barcelona_chatgpt_sol61_high`, `barcelona_gemini_argon_medium`, `barcelona_qwen37_plus`. Eindhoven Qwen çıktısı `eindhoven_qwen38_max/` altında.
- Qwen Eindhoven çıktısı, Miami token raporu ve Eindhoven denetim PDF'i (%55) incelendi. Ana rapor: `results\RAPOR_Token_ve_Kalite_Analizi_Qwen_Eindhoven_2026-10-22.md`.
- Resmî Corteqs v7 doğrulayıcısı (`araclar/`) Qwen paketinde bağımsız çalıştırıldı; denetimdeki sayılar yeniden üretildi. Salt-okunur çalıştırıcı: `araclar/kontrol_salt_okunur.py`.
- **Hata önleme listesi** yazıldı ve cihaza kaydedildi: `skill\hata-onleme-listesi.md` ve `skill\prompt-ek-blok.txt` (20 kural).

## 3. Ana bulgular

**Qwen'in Eindhoven hatası: miktar var, doğruluk yok.** Sayısal hedefler tutturulmuş ama içerik güvenilmez.

- Resmî doğrulayıcı: 363 hata, 822 uyarı. Qwen kendi QA'sında "0 hata, 0 uyarı" yazmış (öz-rapor şişirmesi).
- Hukuk, vergi ve destek bilgilerinde olgusal hatalar; mekân adres/ad karışıklıkları; yanlış veya alakasız fotoğraflar.
- Kanıt zinciri eksik (SHA-256, lisans, fotoğrafçı); şema ihlalleri (CC lisans URL biçimi, `compare_json`, `emergency.tel`, id biçimi, tekrarlı liste değerleri).
- İnsan inceleme alanları (`metadata_review_status`, `pixel_review_status`, `rights_status`) `Bekliyor` kalmalı; AI kendini onaylayamaz.

**Token ekonomisi (Miami/Codex raporu):**
- Girdinin ~%97'si önbellekli yeniden okunan bağlam; asıl maliyet önbelleksiz girdi + çıktı.
- En ağır kısımlar: fotoğraf işleri ve üretim dışı fazlar (aktarım, panel kontrolü, istatistik/PDF). Faz başına ~230K taban maliyet.

## 4. Önerilen mimari (skill için)

1. **Aşamalı boru hattı**, her aşamada temiz bağlam ve küçük `manifest.json`.
2. Deterministik işler betikle (doğrulama, indirme, sha256, eleme), modelle değil.
3. **Ülke paketleri**: ulusal bilgiler (ör. Hollanda) bir kez araştırılıp şehirler arasında yeniden kullanılır.
4. **İddia–kaynak tablosu**: yüksek riskli olgular (hukuk, vergi, ücret, sağlık, eğitim, taşınma) için `kart_id, iddia, sayı, kaynak_url, alıntı, kontrol_tarihi, yürürlük_yılı`.
5. **Fotoğraf hattı**: kimlik planı (resmî ad, belediye, tür) → deterministik filtre (GPS ≤1 km, painting/drawing/map/logo kelimeleri, kısa kenar ≥600 px, dHash benzerlik) → kontak sayfasıyla görsel inceleme → orijinalleri indirme.
6. **Resmî doğrulayıcı zorunlu kapı**; "0 hata" yalnız onun çıktısıyla yazılır.
7. **Bağımsız denetim** farklı bir modelle; efor yönlendirme (ucuz model toplama, güçlü model hukuk/olgu).

## 5. Teknik sözleşme (v7) hızlı referans

- 16 ana Excel sayfası + `FotoğrafKaynakları` (17); başlıklar satır 6, teknik anahtarlar satır 7, veri satır 8'den.
- Berlin asgari/hedef: cevap 212/240, mekân 92/120, mahalle 12/16, konu 12, mekân fotoğrafı 187/250, kapak 6/8, rota 9/12, sözlük 48/60.
- Fotoğraflar: gerçek, ücretsiz, ticari kullanıma uygun (CC0, CC BY, CC BY-SA, kamu malı); NC/ND, AI, Google/Pinterest/Instagram/stok yok. Fotoğrafçı + kaynak + lisans + SHA-256 zinciri zorunlu. `Fotoğraflar.file/sha256` = `FotoğrafKaynakları.original_file/original_sha256`; web kopyası `web_file/web_sha256`.
- Doğrulayıcı kuralları: CC lisans URL `https://creativecommons.org/licenses/<tür>/<sürüm>[/<yargı>]/` (sorgusuz); CC0 → `.../publicdomain/zero/1.0/`; `compare_json` ≥4 dolu metin çifti; `quick_links`/`facts` `{label, entry}`; `emergency.tel` `\+?[0-9*#]{2,20}`; rota 2–8 farklı durak; id'ler `[a-z0-9-_:]`; URL başına tek source_id; `;` listelerinde tekrar yok (okuyucuyu çökertir).

## 6. Kısıtlar ve bilinen sorunlar

- Bulut konteyner ve cihaz kabuğu Commons/resmî sitelere erişemiyor (proxy 403/000). Fotoğraf indirme ve kaynak doğrulama **ağın açık olduğu VS Code ortamında** çalışmalı.
- Resmî doğrulayıcı okuyucusu tekrarlı liste değerinde çöküyor; `kontrol_salt_okunur.py` bunu tolere edip sayıyor.
- Drive bağlayıcısı büyük dosyada (Berlin xlsx ~6 MB) düşüyor; dosyalar elle indirildi.
- Cihaz kabuğunda silme izni yok (`mv -n` ile taşı).
- `propose_skills` yalnız SKILL.md kaydeder; betikler skill klasöründe veya `araclar/` altında durmalı.
- Prompttaki araştırma başlangıç tarihi hâlâ 2026-10-15; güncellenmesi gerekebilir.

## 7. Dosya haritası (`0000_newera`)

| Yol | İçerik |
|---|---|
| `AI_URETIM_PROMPTU_v7_*.txt`, `*_LOKAL.txt` | Şehir promptları |
| `ekler*/`, `alicante_hazirlik/` | Prompt ekleri / şehir xlsx |
| `results/` | Koşu klasörleri, `RUN_LOG.csv`, ana rapor |
| `eindhoven_qwen38_max/` | Qwen çıktısı + `_work_eindhoven/` çalışma dosyaları |
| `araclar/` | Resmî teknik teslim araçları, `kontrol_salt_okunur.py` |
| `skill/` | `hata-onleme-listesi.md`, `prompt-ek-blok.txt` |
| `CITY-009_barcelona_v001.xlsx` | Barcelona çalışma dosyası |
| `Miami_...Token_Raporu_...pdf`, `Eindhoven_...Denetim_...pdf` | Girdi raporları |

## 8. VS Code / Claude Code için sonraki adımlar

1. Projeye `.claude/skills/corteqs-city-pipeline/` oluştur: `SKILL.md` + `references/` (hata-onleme-listesi.md, v7 sözleşme özeti) + `scripts/` (doğrulayıcı sarmalayıcı, `download_media.py`, aday eleme, sha256/manifest).
2. `skill/prompt-ek-blok.txt`'i LOKAL promptların sonuna ekle (henüz eklenmedi).
3. **İlk deneme şehrini seç** (cevaplanmadı): Eindhoven'ı yeniden düzeltmek (Qwen ile doğrudan kıyas) veya yeni şehir (Aberdeen/Barcelona) ile skill'i sıfırdan sınamak.
4. `RUN_LOG.csv`'yi doldur; Barcelona koşularını (ChatGPT/Gemini/Qwen) resmî doğrulayıcıyla kıyasla.
5. Ağın açık olduğu ortamda doğrulayıcıyı ve fotoğraf hattını gerçek veriyle dene; token/süre ölç ve rapora ekle.
6. Skill sonuçları iyiyse en iyi paketi Drive'a yükle.

## 9. Claude Code'a verilecek başlangıç komutu (öneri)

> `C:\temp_private\corteqs\0000_newera` içindeki `results\RAPOR_Token_ve_Kalite_Analizi_Qwen_Eindhoven_2026-10-22.md`, `skill\hata-onleme-listesi.md` ve bu özet dosyasını oku. Ardından `.claude/skills/corteqs-city-pipeline/` altında skill'i kur (SKILL.md, references, scripts). Yeni dosyaları her zaman `0000_newera` altına yaz. İnsan inceleme alanlarını `Bekliyor` bırak; "0 hata" yalnız resmî doğrulayıcı çıktısıyla yazılır.
