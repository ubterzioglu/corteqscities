# Marbella (CITY-080): nerede kaldı (devir notu)

Güncellendi: 2 Kasım 2026, ikinci bulut oturumu (`session_01CvxEJBe5keKSHuRVevDebw`). Bütün iş GitHub'da **`marbella-uretim`** dalında; main'e birleştirilmedi.

## Kısaca
- **Bitti:** intake, sources, answers, **places** (2 Kasım'da kapandı; kapı temiz).
- **Yarıda:** photos. Faz açıldı (`mark photos start`, manifest `photos: running`). Plan ve QID adımı yapıldı. **Arama yapılamadı:** Wikimedia bu bulut ağında hız sınırı uyguluyor (30–60 sn bekletme, `cirrussearch-too-busy`). Openverse 60.481 sn bekleme istedi. 110 kaydın yalnız 1'i arandı (Playa de la Fontanilla, 25 aday).
- **Başlanmadı:** assemble, deliver.
- `manifest_check`: 0 bulgu.

## Yeni oturumda ilk iş (yerel makine)
1. Dalı al:
   - `git fetch origin marbella-uretim`
   - `git checkout marbella-uretim` (ya da `git pull`)
2. **Ortam:** Windows'ta `_is/ortam.ps1`. `manifest.json` içindeki `paths.*`, `country_pack.path`, `gates[].report` ve `kaynak_dizini.jsonl` → `text_file` alanları **Linux yolu** (`/home/user/corteqscities/...`). Windows'ta çalışılacaksa bunlar ROOT'a göre çevrilmeli: `/home/user/corteqscities` → `C:\temp_private\corteqs\0000_newera`, `/` → `\`. Bir defalık küçük betikle yapılır. Not: `kaynak_dizini.jsonl`'de `text_file` **mutlak** yol (önceki not "göreli" diyordu; yanlıştı).
3. **Kaynak metinleri:** `snap_*` klasörleri `.gitignore`'da. İlk bulut makinesi kapanınca 429 kaynak metninin hepsi kaybolmuştu; bu oturumda geri kuruldu:
   - Ülke paketi kopyaları (`snap_ulke_es`, 147): `ulke/ES/kaynaklar` ve `ulke/ES/bolge/andalucia/kaynaklar`'dan kopyalandı. **Git'te değil.** Yerelde `_is/araclar/kaynak_geri_yukle_1_ulke.py` ile yeniden kurulur (yolları düzelt).
   - Kalan 282: yeniden indirildi. **`.txt` dosyaları git'e zorla eklendi** (`git add -f`, ~16 MB). HTML'ler git'te yok.
   - Kayıt: `_is/kaynak_geri_yukleme.json`. Yeniden indirilen sayfaların çoğu 28–29 Ekim kopyasından bayt düzeyinde farklı (yalnız 16 sayfa aynı; dinamik içerik). Yine de birleştirmede alıntı uyuşmazlığı 0. Kaynak 246 (seg-social) İngilizce geliyordu, `?lang=es` ile alındı. Kaynak 242 (AEAT) ikinci denemede alındı.
   - `_is/cache` ve `_is/snap` (KUR'un snapshot klasörü) de git dışı. KUR ilk çalışmada bunları yeniden indirir (~10 dk).
4. `manifest_check` çalıştır. Bu oturumu `_is/oturumlar.txt`'ye ekle (şu an 2 bulut satırı var; ikisinin kaydı da yerelde yok, faz 7'de `run_log` gap verecek: kanıtıyla `open_items`'a yaz).

## Sayılar (2 Kasım 2026, KUR sonrası)
| | Sayı | Asgari / hedef |
|---|---|---|
| Yanıtlar | 229 | 212 / 240 |
| Mekânlar | **98** (m1 47, m2 30, m3 21) | 92 / 120 |
| Mahalleler | 12 | 12 / 16 |
| Sözlük | **59** | 48 / 60 |
| Rotalar | 12 | 9 / 12 |
| Bağlantılar | 501 | — |
| Kaynaklar (pakette) | 402 | ≤500 |
| Fotoğraf | 0 | 187 / 250, kapak 6 / 8 |

Gruplar: Doğa ve açık hava 33, Tarih ve mimari 28, Spor 9, Çocuklarla keşif 7, Müzeler 7, Sanat 6, Sahne 6, Yeme ve içme 2.

Places kapısı (manifest `phases.places.gates`): birleştirme bulgusu 0, alıntı uyuşmazlığı 0, kurulumda red 0, `text_quality` hitap 0, warning-scan 0, `acik_mi` 0, `validate_all` yapı 0 / medya 0 (112 uyarının hepsi fotoğraf eksiği). `kart_tutarlilik` çıkış 1: 11 sözlük-çapalı grup; farklı işlemlerin değerlerini topluyor, d5'te bakılır.

## Bu oturumda yapılanlar
- **m3 editör turu:** 42 bulgu, 38 uygulandı, 4 reddedildi (kaynakta adres yok, koordinat değişmedi). 19 kayıt değişti. Capilla de San Juan de Dios kartına kaynak:272 bilgisi eklendi (Hospital Real ile aynı yapı). Castillo de San Luis grubu Müzeler → Tarih ve mimari.
- **m3 doğrulayıcı:** 46 satır; hatalı düzeltme 0, ciddi/orta 0, 9 hafif eksik (OI-011). Doğrulama turu gerekmedi.
- **Kararlar (kullanıcı onayı):**
  - `parque-del-mediterraneo` silindi (K108). Bilgisi `playa-el-pinillo` kartına taşındı (16 voleybol sahası, saatler; defter satırları da). Rota 009'un son durağı El Pinillo oldu (aynı nokta, `rota_mesafe` bacağı aynı).
  - Sözlük `term:054 Cercanías` silindi.
  - `parque-vigil-de-quinones` / `polideportivo-paco-cantos` aynı koordinat: CartoCiudad Cánovas del Castillo 31 = Vigil'in adresi, doğru. Paco Cantos'un adresi "s/n", resmî portal yok; kural gereği değişmedi → OI-010 (OSM'de ~170 m güneyde).
- **Açık-mı kapısı:** yer denetim editörleri 7 kartın "… itibarıyla" notunu kaldırmış ya da biçimini değiştirmişti, kapı 7 `not_yok` verdi. Ana döngü notları kapı biçimine getirdi; editörlerin kaynakla düzelttiği içerik korundu.
- Bütün ana döngü değişiklikleri: `_is/denetim/kur-ana_degisiklik.jsonl`.

## Sıradaki adımlar
1. **photos, adım 1 (yerel makinede):** `venues.jsonl` hazır (110 satır, 57 QID; silinen 3 mekân yok). Plan yeniden üretilmez; mekân değişirse `plan-from-xlsx` + QID adımı tekrarlanır. Arama: `_is/foto/arama.sh` sırası (Windows'ta SKILL komutları): `commons_search` (önbellek `_is/foto/cache`, devam eder) → `photo_sources --sources openverse,smithsonian,europeana` → `photo_candidates from-search`. Sonra SKILL'deki tur1 → inceleme → ikinci göz → kapak → seçim → indirme.
   - 15 mekânın koordinatı yok. Fotoğrafsız mekân teslim edilmez (K22): bulunamazsa places yeniden açılır (`mark places start/end`).
2. **assemble adım 0, d5 son denetim** (ucuz yol, OI-009): yalnız yer parçaları (m1, m2, m3, mahalle, rota, sözlük, Şehir), değişen kartlar ve 5 ülke kartı (OI-007). Bu denetim:
   - B5 `<parça>-d5_mekan-dogrulama.jsonl` satırlarını yazmalı: değişen 87 yer kaydı (OI-012). `kanit_teslim` her kayıtta bir "geçti" satırı ister.
   - Ana döngünün denetlenmemiş cümlelerini kapsamalı: 7 açık-mı notu, El Pinillo özeti, rota 009.
   - OI-011'deki 9 hafif eksiği kapatmalı.
3. Teslim zinciri → deliver + RUN_LOG → yeni oturumda `city-audit` ("Marbella paketini denetle").

## Dikkat
- **Tarih:** ülke paketindeki 6 kira kartı (`kira-sozlesmesi-suresi-ve-uzama`, `kira-depozitosu-fianza-ve-iade`, `kira-artisi-siniri-irav`, `kirada-onarim-ve-hasar-sorumlulugu`, `kiralik-evden-cikis-ve-ihbar-suresi`, `kiralik-ilan-dolandiriciligini-tanima`) **5 Kasım 2026**'da, 8 kart 31 Aralık 2026'da eskir. Marbella teslimi 5 Kasım'dan sonraya kalacak. Bu kartlar Marbella'ya intake'te kopyalandı. Teslimden önce ya ülke paketi (`ulke/ES`) yenilenmeli (kaynak yeniden doğrulama + bağımsız denetim, ULKE_FAZI kural 4) ya da bu 6 kartın kaynağı d5'te yeniden doğrulanmalı. Bu oturumda yapılmadı.
- **Maliyet:** places'e bu oturumda 2 ajan daha (m3 editör, m3 doğrulayıcı). Toplam: intake–answers 82, places ~27.
- **Erişim haritası:** `_is/kesif/KESIF_TALIMAT.md`. Ek: marbella.es toplu indirmede geçici 500 veriyor, yeniden deneme yetiyor.
- **Açık konular:** `manifest.json` → `open_items` OI-001 … OI-012.
- **Skill notları** (teslimden sonra ayrı geliştirme turu): (a) `snap_*` git dışı olduğu için bulut oturumu kapanınca kaynak metinleri kayboluyor; `.txt`'lerin git'e alınması ya da `ulke` kopyalarının yeniden kurulması skill'e yazılmalı. (b) Yer denetim editörü açık-mı notlarını silebiliyor; editör görev mesajına "… itibarıyla notunu koru" eklenmeli. (c) `kaynak_dizini` mutlak yolları makine değişince kırılıyor.

## Dosya haritası (bu oturumda eklenenler)
- `_is/kaynak_geri_yukleme.json`, `_is/araclar/kaynak_geri_yukle_{1_ulke,2_yerlestir}.py` (`GERI` ortam değişkeni = indirme klasörü)
- `_is/denetim/m3_degisiklik.jsonl`, `m3_dogrulama.jsonl`
- `_is/snap_*/*.txt` (ülke kopyaları hariç)
- `_is/foto/venues.jsonl` (yeni plan), `search.jsonl` / `candidates.jsonl` (yalnız 1 mekân), `cache/`
