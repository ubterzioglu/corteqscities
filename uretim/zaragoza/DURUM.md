# Zaragoza (CITY-128): nerede kaldı (devir notu)

Yazıldı: 2 Kasım 2026, bulut oturumu `session_01CvxEJBe5keKSHuRVevDebw` (Marbella ile aynı oturum; kullanıcı kararı). Bütün iş GitHub'da **`zaragoza-uretim`** dalında (main'den açıldı, main'e birleştirilmedi).

## Kısaca
- **Bitti:** intake, sources, answers, places. Hepsinin kapısı temiz, `manifest_check` 0 bulgu.
- **Başlanmadı:** photos, assemble, deliver. `manifest.phase = places`, photos `pending`.
- **Photos neden burada yapılmadı:** bu bulut ağında Wikimedia (Commons, Wikidata) hız sınırı uyguluyor, Openverse saatlerce bekletiyor (Marbella'da ölçüldü). Fotoğraf fazı yerel makinede çalışmalı.

## Yeni oturumda ilk iş (yerel makine)
1. Dalı al:
   - `git fetch origin zaragoza-uretim`
   - `git checkout zaragoza-uretim`
2. **Ortam:** Windows'ta `_is/ortam.ps1` hazır (BBOX `41.559,41.76,-1.053,-0.777`). `manifest.json` (`paths.*`, `country_pack.path`, `gates[].report`, `open_items[].evidence`) ve `_is/kaynak_dizini.jsonl` → `text_file` alanları **Linux tam yolu** (`/home/user/corteqscities/...`). Windows'ta çalışmadan önce ROOT'a göre çevir: `/home/user/corteqscities` → `C:\temp_private\corteqs\0000_newera`, `/` → `\` (bir defalık betik).
3. **Kaynak metinleri:** `snap_*` klasörleri `.gitignore`'da. Ülke paketi kopyaları (`snap_ulke_es`, 133) git'te değil: `ulke/ES/kaynaklar`'dan kopyalanarak kurulur (Marbella'daki `uretim/marbella/_is/araclar/kaynak_geri_yukle_1_ulke.py` örnek). Geri kalan bütün kaynakların `.txt` dosyaları **git'e zorla eklendi** (~3,8 MB). HTML kopyaları, `_is/cache`, `_is/snap` git'te yok; KUR ilk çalışmada yeniden indirir.
4. `manifest_check` çalıştır; bu oturumu `_is/oturumlar.txt`'ye ekle (ilk satır bu bulut oturumu; kayıt dosyası yerelde yok: `run_log` gap verecek, kanıtıyla `open_items`'a yaz).

## Sayılar (2 Kasım 2026, places kapanışı)
| | Sayı | Asgari / hedef |
|---|---|---|
| Yanıtlar | 248 (152 Zaragoza + 96 ülke paketi) | 212 / 240 |
| Konular | 12 | 12 |
| Mekânlar | 108 | 92 / 120 |
| Mahalleler | 13 | 12 / 16 |
| Sözlük | 64 | 48 / 60 |
| Rotalar | 12 | 9 / 12 |
| Şehir + SayfaAlanları | 1 + 23 | — |
| Kaynaklar (pakette) | 458 | ≤500 |
| Fotoğraf | 0 | 187 / 250, kapak 6 / 8 |

Mekân grupları: Tarih ve mimari 27, Doğa ve açık hava 24, Spor 13, Müzeler 10, Sanat ve sergiler 10, Sahne ve müzik 10, Yeme ve içme 8, Çocuklarla keşif 6. Wikidata havuzu büyük (1.310 aday, 697 fotoğraflı): fotoğraf asgarisine ulaşmak Marbella'dan kolay olmalı.

Places kapısı: birleştirme bulgusu 0, alıntı uyuşmazlığı 0, kurulumda red 0, hitap 0, warning-scan 0, `validate_all` yapı 0 / medya 0 (123 uyarının hepsi fotoğraf eksiği), açık-mı 0 (108 mekân), rota bacakları 30/30 ölçüldü. Denetimsiz kayıt 0.

## Yapılanlar (özet)
- **intake:** Atınç'ın Drive şablonu (`ekler/zaragoza/CITY-128_zaragoza_v001.xlsx`; delivery_id büyük harf → yalnız kopyada küçültüldü, OI-002). Ülke paketi ES (96 kart, 133 kaynak); **Aragón bölge paketi yok** (OI-005). `pack_merge` tek paketle çalışmadığı için `ulke/ES` `_is/ulke_paketi`'ye kopyalandı (skill notu).
- **sources:** 4 keşif ajanı; 12 konu × 16–18 kaynak, red 0. Fazlası `kesif/<konu>/yedek.jsonl`.
- **answers:** 12 yazar. **Ucuz yol** (kullanıcı kararı, OI-006): 6 denetçi + 6 editör (2'şer konu) + 1 ek denetçi + 1 ek editör; ciddi bulgu 0, çürütme/doğrulayıcı gerekmedi. Ülke kartlarının 6'sı denetime girdi, 20 bulgu ülke kartı olduğu için uygulanmadı (OI-007).
- **places:** 4 seçim ajanı (117 aday → 108 mekân), 4 mekân + sayfa + mahalle + sözlük + rota yazarı; açık-mı: 2 tarayıcı + 2 doğrulayıcı + uygulama editörü (silme yok, 13 karta "2 Kasım 2026 itibarıyla" notu: Termas, Museo de Zaragoza, Pablo Gargallo geçici kapalı; Parque de Atracciones 2026'da açılmadı; CDM yaz havuzları; Galacho ziyaretçi merkezi; Baños Judíos yalnız sanal). Yer denetimi ucuz yol: 4 denetçi, 3 editör, 1 doğrulayıcı (m4). Canal de Aguas Bravas silindi (K108 + işletmede değil). Bütün ana döngü değişiklikleri `_is/denetim/kur-ana_degisiklik.jsonl`.
- **Maliyet:** 70 ajan (hedef 60; ucuz yol kararıyla).

## Sıradaki adımlar
1. **photos (yerel):** `mark photos start` → manifest `photos: running` → `photo_candidates plan-from-xlsx _is/ara --out _is/foto/venues.jsonl` → QID ekleme (`_is/mekan/final.jsonl`'deki `qid`, `entry_id` ile) → `commons_search` → `photo_sources --sources openverse,smithsonian,europeana` → `from-search` → tur1 … (SKILL faz 5). Marbella'daki `uretim/marbella/_is/foto/arama.sh` sırası örnek.
2. **assemble adım 0 (d5 son denetim):** ucuz yol kapsamı: yer parçaları (m1–m4, mahalle, rota, sözlük), **sayfa parçası (Şehir + SayfaAlanları hiç denetlenmedi; `denetim_girdi` bu parçayı desteklemiyor)**, değişen kartlar, ülke kartı bulguları (OI-007), ince mekân kartları (OI-010), mekân doğrulama satırları (`<parça>-d5_mekan-dogrulama.jsonl`; `kanit_teslim` her kaydın bir "geçti" satırını ister: m1 5, m2 10, m3 3, m4 13, mahalle 2 "kaldı" vardı, editörler düzeltti ama satırlar yeniden yazılmadı).
3. Teslim zinciri → deliver + RUN_LOG → yeni oturumda `city-audit` ("Zaragoza paketini denetle").

## Dikkat
- **OI-004 Tarih:** ülke paketindeki 6 kira kartı 5 Kasım 2026'da eskir (apply 2 Kasım'da kopyaladı). Teslimden önce ya `ulke/ES` yenilenmeli ya da bu kartlar d5'te yeniden doğrulanmalı. Marbella da aynı durumda: ülke paketini bir kez yenilemek iki şehri birden çözer.
- **OI-007:** ülke kartlarında 20 bulgu (dijital göçebe vizesi 7, NUSS/temel hesap 4, altın vize 3, gümrük 3, yıllık izin 2, taşınma öncesi vize 1). Ülke paketi güncellemesinde düzeltilmeli.
- **Kaynak kotası:** pakette 458/500. Yeni kaynak ancak "değiştir-boşalt" ile (`kaynak_kullanim.py`).
- **OI-010:** 12 ince mekân kartı (kaynak yalnız adres): bilinçli kabul edildi; d5'te S08 için bakılmalı, gerekirse fotoğraflı yedekle değiştirilmeli.
- **Erişim:** `_is/kesif/KESIF_TALIMAT.md` ve OI-001 (inclusion.gob.es, mivau, iass.aragon.es, dpz.es, cortesaragon.es (Aljafería), ecociudadzaragoza.es, basilicadelpilar.es, caixaforum.org engelli; tranviasdezaragoza.es JS).
- **Skill notları:** `_is/notlar_skill.md`.

## Dosya haritası
- `_is/kesif/` (KESIF_TALIMAT, KESIF_GOREV, ulke_kartlari, gaps), `_is/yazar/` (YAZAR_GOREV, YER_GOREV, ilk5, donus_zaragoza), `_is/mekan/` (SECIM_GOREV, gruplar/, secim_1-4, selected, final, plan_m1-4, cartociudad.json)
- `_is/araclar/` (hazirla_denetim.py, kartlar_txt.py, cevap_zinciri.js, yer_zinciri.js: Marbella'dan uyarlandı; görev metinleri bunlardan node ile üretildi)
- `_is/denetim/` bütün iddia/karar/değişiklik/doğrulama dosyaları; `_is/acik_mi/` tarama ve doğrulama; `_is/rota_plan.jsonl`, `_is/rota_mesafe.jsonl`
