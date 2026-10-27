---
name: city-audit
description: Corteqs v7 şehir paketini bağımsız ve salt okunur denetler (kılavuz 2.0, K01–K120), editoryal yüzde ve karar üretir. Kademeler L0 (yalnız script), L1 (riske göre LLM + görsel), L2 (tam). "paketi denetle", "CITY-NNN denetim", "city-audit", "paket hazır mı" isteklerinde kullan. Paketi üreten oturumda kullanma; temiz oturum gerekir.
---

# city-audit: bağımsız paket denetimi

Bu skill paketi **düzeltmez**; yalnız ölçer, kanıtlar ve karar verir. Sonuç insan yayın onayı değildir.

## Sabit yollar

```
ROOT    = C:\temp_private\corteqs\0000_newera
PY      = ROOT\.venv\Scripts\python.exe
TK      = ROOT\corteqs-skills\toolkit\scripts
CHECKS  = ROOT\corteqs-skills\toolkit\checks.yaml
KAPSAM  = ROOT\corteqs-skills\toolkit\KAPSAM.md   (hangi S kontrolü hangi script'te, tam/kısmi)
TOOLS   = ROOT\araclar\arac
DIGEST  = ROOT\corteqs-skills\city-pack\references\contract_digest.md
AGENTS  = ROOT\corteqs-skills\city-pack\agents\   (iddia-denetcisi.md, foto-inceleme.md, acik-mi.md)
KILAVUZ = ROOT\belgeler\kilavuz\analiz_2026-10-22\SEHIR_DENETIM_CHECKLIST_metin.txt   (kılavuz 2.0; yalnız ilgili bölüm okunur)
```

Girdi: `XLSX` (teslim Excel'i), `PKG` (paket kökü), `LEVEL` (L0/L1/L2; söylenmezse L1), varsa önceki denetim klasörü ve üretimin açık-mı klasörü `ACIKMI` (genelde `ROOT\uretim\<city_id>\_is\acik_mi`; beyandır, yalnız açık-mı örnekleminin önceliği için okunur). Çıktı: `OUT = ROOT\denetim\<city_id>_<YYYY-MM-DD>_<LEVEL>\` (**paket dışında**). Aynı gün aynı kademede yeni bir Excel sürümü denetlenirse klasör adının sonuna sürüm eklenir (ör. `_v002`), eski ajan çıktıları yeni denetime karışmaz.

Her PowerShell çağrısının başına (değişkenler ve ortam çağrılar arasında korunmaz):
```powershell
$env:PYTHONDONTWRITEBYTECODE=1; $env:PYTHONUTF8=1
$ROOT='C:\temp_private\corteqs\0000_newera'; $PY="$ROOT\.venv\Scripts\python.exe"; $TOOLS="$ROOT\araclar\arac"
$TK="$ROOT\corteqs-skills\toolkit\scripts"; $CHECKS="$ROOT\corteqs-skills\toolkit\checks.yaml"
$PKG='<paket kökü>'; $XLSX="$PKG\<teslim Excel'i>"; $OUT="$ROOT\denetim\<city_id>_<YYYY-MM-DD>_<LEVEL>"
$ACIKMI='<üretimin açık-mı klasörü; yoksa boş>'
```
`$env:PYTHONUTF8=1` her Python çağrısını `python -X utf8` gibi çalıştırır. Bu şart: yollar Türkçe (`Fotoğraflar`, `Lisans kanıtları`, `Kanıtlar.jsonl`); kodlama belirtmeyen Python kodu (Atınç'ın araçları, senin küçük betiklerin) Windows'ta cp1252 kullanır, dosya bulunamaz ya da `FotoÄŸraflar` gibi bozuk ad çıkar (pilotta oldu). `validate_all` kendini UTF-8 ile yeniden başlatır; diğerleri için bu değişken yeter, komutlara ayrıca `-X utf8` eklemek gerekmez.

## Değişmez kurallar

1. **Temiz bağlam:** Paketi üreten oturumun notlarını, manifest'teki "açık konu" yorumlarını, üretim raporlarını kanıt sayma. Yalnız paketin kendisi ve kaynaklar. Paketteki `Teslimler\ACIK_KONULAR.txt` bir beyandır: kanıt değil, L1'de sınanır.
2. **Salt okunur:** `PKG` içine hiçbir şey yazılmaz. `validate_all` yalnız `--mode audit`. `TOOLS\check_delivery.py` çalıştırılmaz (paket klasörüne yazar). PKG'den kopya almak serbesttir; kopya ve ara dosyalar yalnız `OUT` altına.
3. **Sabitleme (K04):** Başta ve sonda `inventory.py` çalışır; iki SHA listesi farklıysa denetim geçersiz, baştan.
4. Çalıştırılmayan kontrolü yapılmış gösterme; o kontrol `not_checked`. Üretilmeyen dosyayı listeleme.
5. Drive kontrolleri (`scope: drive-manual`: K01, K03, K109, K110) ve önizleme kontrolleri (`scope: preview-later`: K92–94, K103, K111, K112) → `separate_stage`. Rapor başlığında "yerel paket denetimi" etiketi.
6. İnsan alanları `Bekliyor` değilse ve insan girdisi kanıtı yoksa bu bir bulgudur (K97).
7. Ajan çıktılarındaki sayıları script çıktısıyla yeniden say; ajan özetine güvenme.
8. **Üretim araçları çalıştırılmaz:** `build_xlsx`, `merge_package`, `add_sources`, `package_sources`, `photo_rows`, `photo_previews`, `wikidata_places`, `commons_search`, `download_plan`, `run_log` ve `TOOLS\download_media.py` pakete ya da üretimin iş klasörüne yazar veya üretim kararı verir. Denetim yalnız bu dosyadaki komutları kullanır.

## L0: yalnız script (ağ hariç LLM yok)

```powershell
& $PY $TK\inventory.py $PKG --xlsx $XLSX --out $OUT\dosya-envanteri.json
& $PY $TK\xlsx_dump.py $XLSX --out-dir $OUT\_dump
& $PY $TK\validate_all.py $XLSX $PKG --tools $TOOLS --mode audit --new-content --out $OUT\validation-audit.json
& $PY $TK\render_summary.py --xlsx $XLSX --out-dir $OUT\_render --inventory $OUT\dosya-envanteri.json --validation $OUT\validation-audit.json
& $PY $TK\text_quality.py $XLSX --address-standard sen --out $OUT\text-quality.json
& $PY $TK\preview_checks.py warning-scan --xlsx $XLSX --out $OUT\uyari-tarama.json
& $PY $TK\url_check.py $XLSX --sheets Kaynaklar,Bağlantılar,Şehir,SayfaAlanları --cache-dir $OUT\_cache --out $OUT\url-checks.json --retry-transient
& $PY $TK\fetch_snapshot.py --xlsx $XLSX --out-dir $OUT\kanitlar\snap --cache-dir $OUT\_cache --retry-transient
& $PY $TK\claim_extract.py $XLSX --out $OUT\claims.jsonl
& $PY $TK\claim_check.py --claims $OUT\claims.jsonl --snapshots $OUT\kanitlar\snap --out $OUT\claim-script.json
& $PY $TK\kanit_kapsami.py --xlsx $XLSX --pkg $PKG --out $OUT\kanit-kapsami.json
```
- `kanit_kapsami`: paketin `Teslimler\` klasöründeki kanıtların (iddia defteri ve bağımsız denetim, rota planı, mekân doğrulama, foto inceleme, görsel kalite, resmî doğrulayıcı çıktıları, özetler) 25 ölçütü ne kadar kapattığı ve dış denetim modeliyle (ağırlık × kanıtlı/payda; kanıtsız ölçüt 0) **puan alt sınırı**. Raporun ilk bölümüne `alt_sinir`, `onizleme_ile_azami` ve `eksik` ölçütler yazılır. Bu bizim editoryal yüzdemiz değildir ve kararı değiştirmez; dış denetçinin pakette neyi bulamayacağını gösterir (Sevilla 25.10.2026: dış denetim %44,7, kaybın ~39 puanı kanıtı pakette olmayan ölçütlerden). `eksik` dolu ise her ölçüt için P2 bulgu (K83 kapsamında "kanıt teslimde yok"), düzeltme sırasına "city-pack teslim zinciri: kanıt dosyaları" yazılır. D5 ve E4 `onizleme`dir, eksik sayılmaz.
- `render_summary` paketin teslim özetini bağımsız yeniden hesaplar (K17, K22, K24, K66, K83). `--notes` ve `--manifest` verilmez (üretim notu kanıt değil). `_render\TESLIM_OZETI.txt`'teki Berlin satırları raporun minimum–hedef–fiilî matrisidir.
- `url_check` dört sekmenin adreslerini tek geçişte dener. "Erişim teyidi açık" (403/429/5xx/ağ ya da TLS hatası) bozuk sayılmaz. 429, 5xx ya da ağ/TLS hatası çıkarsa aynı komutu bir kez daha çalıştır; `--retry-transient` yalnız bunları yeniden dener. 403 yeniden denenmez: önbellekten aynen döner, ikinci koşu bir şey değiştirmez; o sayfayı L1'de ajan açar. Alan adı taşınmış ama çalışan adres (3xx → 200) P2 bakım önerisidir; yalnız anasayfaya giden kaynak L1'de K51/K53'e gider.
- `warning-scan` (K103, K104): `hits[]` içinde `check: K103` her satır P1 bulgusudur; `kart_bandi` = kartın bant alanında (`visit_status`, `overlay`, `status_note`, `venue_editorial`) metin var, sitede fotoğrafın üstüne basılır (Sevilla dış denetimi S06: dört `visit_status` kapanış notu). K104 satırları P2. Önizleme beklenmeden L0'da karar verilir: bantı görmek için sayfa gerekmez, alan doluysa bant vardır. K105 (`yilsiz_istisna`, `gecmis_tarihli_istisna`): yılı yazılmamış ya da geçmiş tarihli istisna cümlesi, P2 bulgu (K105, Sevilla S21).
- `claim_check` sonucu (`supported`, `not_in_source`, `no_snapshot`, `homepage_only_source`, `no_source`) yalnız tutarlılıktır, doğruluk değil.
- K76 (kısmi): paketteki kaynak kopyasını (`Kaynaklar.snapshot_file`) aynı adresin taze kopyasıyla (`kanitlar\snap\index.jsonl`, aynı `url`) başlık ve metin örtüşmesiyle karşılaştır; farklı başlık ve düşük örtüşme yanlış ya da uydurma kopya şüphesidir, L1'de bakılır.
- Teslimat satırı (`_dump\Teslimat.jsonl`): `updated_on` en son içerik tarihinden (`reviewed_on`/`checked_on`) eskiyse ya da `notes` şablon metni ("içerik üretilmedi") ise K14 bulgusu (pilot ISS-006).
- Atınç'ın girdi şablonu verildiyse K09 için `xlsx_fidelity` çalıştır: ilk argüman şablon, ikincisi `XLSX`, rapor `--report` ile `OUT\xlsx-fidelity.json`.

### Fotoğraf verisi (K05, K22, K63, K64, K67, K84, K107)

`photo_candidates from-evidence` kanıtı paketteki `Lisans kanıtları\*.source-evidence.json` dosyalarından okur. v7 paketinde bu dosyalar olmayabilir; kanıt Excel'in Kanıtlar sekmesindedir (`source_evidence_json` → `original_api_record` = Commons kaydı). Pilotta komut doğrudan `PKG` ile 0 aday verdi; K64, K67, K107 `not_checked` kaldı. Yol: `audit_prep hazirla` bu dosyaları `xlsx_dump` çıktısı `_dump\Kanıtlar.jsonl`'den `OUT\_foto\kanit` altında üretir; Excel'in kopyası yanına konur (entry_id ve rol için), `from-evidence` o klasörle çalışır. Aynı adım contact_sheet girdisini (`items.jsonl`), yol taramasını ve envanterdeki aynı SHA'lı dosyaların sınıflamasını da üretir; ayrıntı `_foto\hazirlik.json`'a yazılır. `_foto\kanit` ve `temas-sayfalari` her koşuda baştan kurulur: aynı klasörde ikinci koşuda eski kanıt dosyası, eski Excel kopyası (`photo_candidates` klasördeki ilk xlsx'i alır) ya da eski pafta kalmaz. `audit_prep` paketi yalnız okur; OUT paketin içindeyse çalışmaz. Çıkış 1 = bulgu adayı var (aşağıdaki maddeler; karar değil). Çıkış 2 iki durumda olur: girdi eksik ya da bozuk (önce `xlsx_dump` ve ilk `inventory` çalışmış olmalı) ya da OUT/PKG yanlış, bu durumda hiçbir şey silinmez; ya da eski çıktı silinemedi, çünkü içinde kilitli bir dosya var (ör. Excel'de açık; salt okunur dosyayı kendisi siler). Çıkış 2'de blok durur (`throw`), sonraki adımlar önceki koşunun dosyalarıyla çalışmaz: hatayı düzelt, bloğu baştan çalıştır.

```powershell
& $PY $TK\audit_prep.py hazirla $OUT $PKG
if ($LASTEXITCODE -eq 2) { throw 'audit_prep hazirla çıkış 2: hatayı düzelt, bloğu baştan çalıştır' }
Copy-Item -LiteralPath $XLSX -Destination $OUT\_foto\kanit\
& $PY $TK\photo_candidates.py from-evidence $OUT\_foto\kanit --out $OUT\_foto\candidates.jsonl
& $PY $TK\photo_candidates.py plan-from-xlsx $PKG --out $OUT\_foto\plan.jsonl
& $PY $TK\photo_prefilter.py --candidates $OUT\_foto\candidates.jsonl --plan $OUT\_foto\plan.jsonl --out $OUT\_foto\decisions.json
& $PY $TK\contact_sheet.py --items $OUT\_foto\items.jsonl --out-dir $OUT\temas-sayfalari --per-sheet 30
& $PY $TK\audit_prep.py ciftler $OUT
```
- **Ters eğik çizgi (K84):** `ters_egik_cizgi` her yol için `kötü/taranan` verir; ilk sayı 0 olmalı. Taranan: Excel'de `file` ve adı `_file` ile biten her sütun (`Kanıtlar.source_snapshot_file` ve `license_snapshot_file` dahil), `Teslimler`'deki JSON/CSV dosyalarında `Teslimler`, `Fotoğraflar` ya da `Lisans kanıtları` ile başlayan değerler ve HTML dosyalarındaki göreli `src`/`href` bağlantıları (bağlantıda `\` adreste `%5C` olur, ikisi de sayılır). `inventory` ve resmî doğrulayıcı Windows'ta `\`'i kabul eder, yani bu hatayı görmez; Linux'ta dosya bulunamaz. 0 değilse K84 P1 bulgusu, K15 `kaldı` (pilot ISS-004: `web_file` 209/209 `Teslimler\WebKopyalari\...`; aynı yol photo-provenance-v7.json ve atıf CSV'sinde, atıf önizleme HTML'sinde 209 `src="../Teslimler%5CWebKopyalari%5C…"`).
- `kanit_dosyasi` Kanıtlar satır sayısına eşit olmalı. `kanitsiz_foto` 0 değilse o kareler aday olmaz: K67 `kısmi` + gerekçe; hangi karenin neden kanıtsız kaldığı (JSON değil, JSON nesnesi değil, UzunAlanlar'da, `original_api_record` yok) `hazirlik.json`'dadır. Pakette `api_imageinfo` içeren `*.source-evidence.json` dosyaları varsa `from-evidence` doğrudan `PKG` ile de çalışır.
- `eksik_alanli_foto` (yalnız varsa): `photo_id` ya da `file` hücresi boş Fotoğraflar satırları; Excel satırı ve eksik alan `hazirlik.json`'dadır. Bu bir paket kusurudur, girdi hatası değil (çıkış 1): satır paftaya girmez, bulgu `validate_all` sonucuyla birlikte raporlanır.
- `photo_prefilter` çıkış 1 = `flag`/`reject` var: karar değil, L1 girdisi. Özetteki `entries_without_shortlist` fotoğrafsız kayıt sayısıdır; K22 sayısıyla tutmalı.
- **`decisions.json` → K64, K67, K107** (`decisions[]`: `candidate_id` = photo_id, `reasons` = neden kodları):
  - `ai_generated` → K64 P0 bulgusu (kaynak kaydında yapay görüntü işareti; L1'de kayıt metniyle teyit edilir).
  - `license_not_allowed` → K67 P0 bulgusu (Commons lisans alanı izinli listede değil). `restrictions` → L1 girdisi: Commons kısıt metni (ör. kişilik hakkı, marka) okunur, serbest kullanımı bozuyorsa K67 bulgusu.
  - K107: `photo_candidates` özetindeki `candidates` Fotoğraflar satır sayısına eşit olmalı (her teslim karesi bir aday; eksik kalan `kanitsiz_foto`'dur). Aday, ret/işaret (`decisions.json` → `summary`) ve teslim sayıları (`_render\TESLIM_OZETI.txt` "Fotoğraf:" satırı: ilişki, tekil mekân, tekil kapak) ayrı yazılır, birbirine eklenmez.
  - Bulgu yoksa üçü de KAPSAM gereği `kısmi`: script yalnız Commons kaydını ve etiketleri okur, görsel inceleme L1'dedir.
- **Aynı SHA'lı dosyalar (K05, K63):** `ayni_sha` envanterin `dup_sha` gruplarını ayırır (ayrıntı `hazirlik.json`):
  - `kapak_mekan`: iki dosya da `Fotoğraflar\` altında, biri Kapak öteki Mekân satırının dosyası. Zararsızdır: rol ayrı, kare tekil sayımda bir kez sayılır (pilotta 8).
  - `K05`: gruptaki bir dosya `Fotoğraflar\` dışında ya da hiçbir Fotoğraflar satırına bağlı değil (artık ya da fazla kopya). K05 P2 bulgusu. Pilot teslim denemesindeki 156 `dup_sha` ve 156 `ext_mismatch` `Teslimler\.download-cache` artığıydı.
  - `K63`: iki mekân karesi (ya da iki kapak) aynı dosya; gerçek tekrardır, K63 P1 bulgusu.
  - Tekil sayım `_render\TESLIM_OZETI.txt`'teki "tekil mekân karesi"dir.
- **dHash çiftleri (K63):** `audit_prep ciftler` `temas-sayfalari\dhash.json` → `pairs`'ı okur (`a`, `b` = photo_id, `distance`, `same_group` = aynı kayıt) ve `_foto\dhash-ciftleri.json`'a yazar. Aynı bayttaki kapak↔mekân çiftleri `kapak_mekan`'a düşer; kalanlar `K63_aday`'dır (varsa çıkış 1). Benzerlik tek başına karar değildir: `K63_aday` boş ve `ayni_sha` → `K63` 0 ise K63 `geçti`; değilse L0'da `kısmi` + çift listesi, karar L1'de foto ajanınındır.
- Pafta L0'da üretilir ama **bakılmaz**.

### Kapanış: sabitleme ve sayım karşılaştırmaları

```powershell
& $PY $TK\inventory.py $PKG --xlsx $XLSX --out $OUT\_dosya-envanteri-son.json
function fark($a, $b) { Compare-Object $a $b | ForEach-Object { "$($_.SideIndicator) $($_.InputObject)" } }
$bas = (Get-Content $OUT\dosya-envanteri.json -Raw | ConvertFrom-Json).files | ForEach-Object { "$($_.path) $($_.sha256)" }
$son = (Get-Content $OUT\_dosya-envanteri-son.json -Raw | ConvertFrom-Json).files | ForEach-Object { "$($_.path) $($_.sha256)" }
$k04 = @(fark $bas $son); "K04 fark: $($k04.Count)"; $k04   # 0 = paket değişmedi; değilse denetim geçersiz, baştan
'--- K83 özet (<= paket, => denetim)'; fark (Get-Content "$PKG\Teslimler\TESLIM_OZETI.txt") (Get-Content $OUT\_render\TESLIM_OZETI.txt)
$paket = (Get-Content "$PKG\Teslimler\dosya-envanteri.json" -Raw | ConvertFrom-Json).files | ForEach-Object path
'--- K83 yol (<= paket envanteri, => denetim envanteri)'; fark $paket ((Get-Content $OUT\dosya-envanteri.json -Raw | ConvertFrom-Json).files | ForEach-Object path)
```
- **K04:** `K04 fark` 0 olmalı. 0 değilse paket denetim sırasında değişmiştir (altındaki satırlar değişen dosyalar): denetim geçersiz, baştan.
- **TESLIM_OZETI ↔ ölçülen (K83):** "K83 özet" çıktısında yalnız iki fark beklenir: `Excel sürümü/tarihi` satırındaki tarih (paket özeti üretim gününü, `_render` denetim gününü yazar) ve `Paket:` satırında MB'nin son basamağı (±0,01; özet dosyaları sayımdan sonra yeniden yazılır). Dosya sayısı, sekme sayıları, Berlin ve fotoğraf satırları aynı olmalı. `Durum`, `Açık konu sayısı` ya da `Resmî doğrulayıcı` satırı tutmuyorsa paket özeti eski ya da başka bir doğrulamayla yazılmıştır (ör. paket "TEKNİK KONTROL GEÇTİ", denetim "DÜZELTME GEREKLİ"): K83 bulgusu. `render_summary` bu satırları yalnız Excel, envanter ve doğrulamadan hesaplar; `--notes` yalnız ACIK_KONULAR.txt'e satır ekler. `validate_all`'ın emit ve audit modu da aynı kontrolleri çalıştırır.
- "K83 yol" çıktısındaki `=>` satırları paketin kendi sayımından sonra yazılmış dosyalardır (pilot ISS-005: özet 763 dosya, ölçülen 772; 9 `Teslimler` çıktısı sayımdan sonra yazılmıştı). Yalnız dosya/MB satırı eskiyse P2; sekme, Berlin, `Durum`, `Açık konu sayısı` ya da `Resmî doğrulayıcı` satırı tutmuyorsa K83'ün kendi önceliği P1.
- `CHECKS`'te `exec: S` kontrolleri `KAPSAM`'daki eşlemeyle script çıktısından CHECK kaydına dönüşür. Kısmi kapsananlar (KAPSAM "Kismi") `kısmi`; eksik kısım bu dosyadaki bir komutla tamamlandıysa (ör. K04 baş/son karşılaştırması) `geçti`, gerekçe `sınır_gerekçe`'ye. K73, K81 `not_checked`.
- Önceki denetim varsa: `impact.py $XLSX --diff <önceki.xlsx> --checks $CHECKS --out $OUT\impact.json`; her eski bulgu Kapandı / Kısmen / Açık / Yeni (yalnız gerçek dosya farkıyla).
- L0'da `exec: L` ve `V` kontrolleri `not_checked`. Script'in kesin gösterdiği P0/P1 varsa (pilot: hedef eksikleri, fotoğrafsız kayıtlar, `\` yolları) karar **DÜZELTME GEREKLİ**; hepsi kapanınca L0 kararı en iyi ihtimalle **KANIT EKSİK**. Bu beklenen davranıştır.

## L1: riske göre LLM + görsel (varsayılan)

L0'ın tamamı aynı `OUT` içinde çalışır; son envanter (K04) ajanlar bittikten sonra alınır. Her ajana kendi geçici klasörü (`<scratchpad>\<görev>_w\`) verilir; ajana üretim notu verilmez.

### L1 iş düzeni (Sevilla L1, 25.10.2026: 32 ajan, ~7 M alt ajan tokeni, ~2 saat)

- **Hazır talimatlar ve betikler:** ajan talimatları `<bu skill>\agents\l1\` (yer tutucular ve ajan → girdi → çıktı tablosu `README.md`'de), girdi ve kayıt betikleri `<bu skill>\betikler\`. Yeni talimat yazma; yer tutucuları görev mesajında doldur. Betikler `& $PY -I -X utf8 <bu skill>\betikler\<ad>.py $OUT` ile çalışır, yalnız `OUT`'a yazar:
  - L0'dan sonra: `capraz.py`, `snapcmp.py`, `tarih.py` (çapraz sayımlar, K76 kopya karşılaştırması, K14 tarih sırası); `acik_mi_denetim orneklem`'den sonra `hazirla_l1.py` (iddia seçimi ve partiler, açık-mı ajan girdileri `_acikmi_girdi\`), `hazirla_l2.py` (mekân, mahalle, rota, bağlantı örneklemi, sayfa alanları), `hazirla_l3.py` (lisans zinciri).
  - Ajanlar bitince: `birlestir.py` (`claim-checks.json`, `photo-review.json`), son `inventory` + `betikler\k04.py` (argümanlar: OUT ve PKG), sonra kayıtlar (`check-results.json`, `issues.json`, `criteria.json`). Kayıt betiği şehre özgü değerlendirme metni taşır: `kayitlar_l1_ornek_sevilla.py`'yi `OUT\_analiz\betikler\`'e kopyala ve bulgu metinlerini bu şehrin ajan sonuçlarına göre yeniden yaz (sayılar dosyalardan okunur; Sevilla'ya özgü bulgu metni kalmaz). `editorial_score` E1 gibi "KALDI birim bulguya bağlanmadı" boşluğu verirse o kontrolün bulgusunu ölçütüne bağla; her `kaldı` CHECK'in `bulgu_IDleri` dolu olmalı.
- **Klasör kuralı:** `OUT\_acikmi\` içine yalnız `acik_mi_denetim`'in parti dosyaları ve ajanların `_dogrulama` dosyaları girer. Kapı oradaki her `*.jsonl`'i tarama satırı sayar: ajan girdisi oraya konursa her mekân `gecersiz_durum` verir (Sevilla'da 58 sahte bulgu). Girdiler `OUT\_acikmi_girdi\`'dedir.
- **Maliyet sorusu:** ajanları başlatmadan önce iş sayısını ve tahmini alt ajan tokenini kullanıcıya tek öneriyle sor (Sevilla ölçümü `agents\l1\README.md`'de; iddia partisi en pahalısı). Kapsamı daraltmak kritik iddia kapsamını düşürür, karar KANIT EKSİK'e kayabilir; bunu soruda yaz.
- **Model ve eşzamanlılık:** bütün L1 ajanları `general-purpose`, **Sonnet** (Opus yalnız kullanıcı isterse). **Aynı anda en çok 5 ajan**; biten ajanın yerine hemen sıradaki başlatılır. Sevilla'da 20 ajan birden başlatılınca oturum kilitlendi: 40 dk ilerleme olmadı, durdurulan ajanların yuvaları uzun süre boşalmadı.
- **Bekçi:** ajanlar çıktıyı parça parça yazar (`ORTAK.md` madde 9, 11). `betikler\bekci.ps1 <liste>` arka planda çalışır, listedeki dosyalardan biri 10 dakika büyümezse çıkar. Liste (`OUT\_ajan\izle.txt`, satır başına bir çıktı dosyası) her ajan başlatılıp bitince güncellenir; biten ajanın dosyası listeden çıkar, yoksa yanlış alarm verir. Uyarıda önce ajanın geçici klasörüne bak (hâlâ dosya indiriyor olabilir), sonra `SendMessage` ile "bitirdiğin kayıtları şimdi yaz" hatırlat; ancak hiç hareket yoksa durdurup aynı talimatla yenisini başlat (yeni ajan dosyadaki kayıtları atlar).
- **Arama özeti kanıt değildir:** WebFetch özeti ya da arama sonucuna dayanan `yanlış`/`eski`/`kaldı` kararı rapora "teyit gerekli" diye ayrı yazılır (Sevilla: havalimanı ücretleri). Görev mesajında bu kural (`ORTAK.md` madde 10) tekrarlanır.
- **Ülke paketi:** şehrin `Teslimat.notes`'u ya da kartların ortak ulusal metni ülke paketinden geldiklerini gösterir (`ROOT\ulke\<ISO>\pack.json`, `cards.<slug>.valid_until`). Denetim bu kartları da tam ölçer (paket beyanı kanıt değildir); `valid_until`'i kontrol tarihinden önce olan ya da 30 gün içinde dolan ülke kartı K35 bulgusudur (P1; geçmişse eski bilgi, yaklaşıyorsa P2 bakım). Raporda ülke paketinden gelen kart sayısı ayrı satırdır.

**İddialar:** `AGENTS\iddia-denetcisi.md` + `agents\l1\IDDIA_PROMPT.md` ile kartları yazmamış bağımsız alt ajanlar (Sonnet), ~11 kartlık partiler (`hazirla_l1.py`), en çok 5 paralel.
- Seçim: `claim-script.json` → `results` içinde `result` değeri `supported` olmayanların hepsi; sayısal olmayan kural içeren kartlar (ücret/şart/başvuru/yasak sözcükleri; `_dump\Yanıtlar.jsonl`); `text-quality.json` → `hedges.items` ve `evasive_answers.items` kartları (K104); `Teslimler\ACIK_KONULAR.txt`'te beyan edilen konuların kartları; P0/P1 konulardan (göç, sağlık, vergi, konut, çalışma) en az %20 `supported` örneklem.
- Ajana verilen: `results` satırları (her satır `sentence`, `values`, `sources[].url` ve `claim_record` = CLAIM kaydının script'in doldurduğu kısmını taşır), kartın tam metni (`_dump\<sekme>.jsonl`, aynı `entry_id`), taze kopya metni (`kanitlar\snap\` içinde `sources[].snapshot_id`). Kopya yoksa ya da inceyse ajan sayfayı kendisi açar; açamazsa `erişilemedi`.
- Çıktı: `OUT\_iddia\parti_NN.jsonl` (CLAIM kaydı) → birleşik `claim-checks.json`. `yanlış`/`eski` → ISSUE (K29, K34, K35…), `kaynak_yetersiz` → K30/K51.
- Pilotta `not_in_source`'ların bir kısmı yanlış pozitifti (kartın okuma tarihi notu, otobüs hattı numarası); kararı ajan verir, script değil.

**Fotoğraflar:** `AGENTS\foto-inceleme.md` + `agents\l1\FOTO_PROMPT.md` ile iki alt ajan (paftalar yarı yarıya); yalnız paftaları görür, tek tek fotoğraf açmaz.
- Girdi: `temas-sayfalari\sheets.json` (pafta → `slot` → `key`, `label`), tüm 30'lu `sheet_NN.jpg` (K66 için her kare taranır), `temas-sayfalari\dhash.json` (karar isteyen çiftler `_foto\dhash-ciftleri.json` → `K63_aday`), `_foto\decisions.json` (`flag`/`reject` gerekçeleri), mekân bilgisi (`_dump\Mekânlar.jsonl`, `Mahalleler.jsonl`: ad, adres, grup).
- Şüpheliler (`decisions.json`'da `flag`/`reject`) ayrıca 20'li paftada (şüpheli yoksa atla):
  ```powershell
  $supheli = ((Get-Content $OUT\_foto\decisions.json -Raw | ConvertFrom-Json).decisions | Where-Object decision -ne 'keep').candidate_id
  New-Item -ItemType Directory -Force $OUT\_foto\supheli | Out-Null
  Get-Content $OUT\_foto\items.jsonl | Where-Object { ($_ | ConvertFrom-Json).key -in $supheli } | Set-Content -Encoding utf8 $OUT\_foto\supheli\items.jsonl
  & $PY $TK\contact_sheet.py --items $OUT\_foto\supheli\items.jsonl --out-dir $OUT\temas-sayfalari\supheli --per-sheet 20
  ```
- Denetimde ajan yalnız `photo-review.jsonl` yazar (`{key, entry_id, sheet, slot, result, seen, reason}`); `selected.jsonl` üretim işidir, istenmez. Slot = karodaki büyük numara (`sheets.json` → `slot`); şüpheli paftada `sheet` = `supheli/sheet_NN.jpg`. Lisans kararı ajanın değil.
- Birleştirme `photo-review.json`'a (PHOTO kaydı): `reject` → ISSUE (K59–K62), rapora pafta ve slot yazılır.

**Bugün açık mı (K39; B15):** kılavuzun K39 yöntemi (mekânın kendi sitesi) yetmez: pilotta kapanmış golf sahasının sitesi yıllarca "© 2019" ile yayındaydı; seçim, yazım ve Opus denetimi üçü de geçirdi. K39 bu adımla yapılır. Kanıt kuralları `AGENTS\acik-mi.md` §2: sitenin açılması açık kanıtı değildir, açık kanıtı kontrol yılı ya da önceki yıl tarihli faaliyettir, kapanış araması yerel dilde ve Türkçe yapılır. Adımın bütün dosyaları `OUT` altındadır, `ACIKMI` yalnız okunur; sayılar elle değil `acik_mi` ve `acik_mi_denetim` çıktısından gelir (kural 7).
- Üretim beyanı (`ACIKMI` verildiyse; yoksa `$ACIKMI` boş kalır, yalnız ilk satır çalışır ve raporda "üretim açık-mı beyanı yok"): kapı teslim Excel'inin mekân listesiyle yeniden çalışır, üretimin kendi raporu okunmaz. Bulgular kanıt değil, örneklem önceliğidir (çıkış 1 olağan, çıkış 2 yol ya da girdi hatası). Kapı yalnız `--out`'a yazar; ilk satır önceki koşunun raporunu siler. Çıkış 2'de yalnız komut ya da yol düzeltilir, üretimin dosyası düzeltilmez (kural 2); dosya yine okunamıyorsa raporda "üretim beyanı okunamadı" ve kapının hata satırı yazılır, örneklem (a), (b) ve (d) öncelikleri olmadan seçilir (rapor yoksa örnekleyici `ACIKMI`'yi okumaz).
  ```powershell
  Remove-Item -LiteralPath $OUT\acik-mi-uretim.json -ErrorAction Ignore
  & $PY $TK\acik_mi.py $ACIKMI --mekanlar $OUT\_dump\Mekânlar.jsonl --kaynaklar $OUT\_dump\Kaynaklar.jsonl --out $OUT\acik-mi-uretim.json
  ```
- Örneklem: n = en az 8 ve en az mekân sayısının %10'u (yukarı yuvarlanır; mekân 8'den azsa hepsi). Önce öncelikliler, hepsi: (a) `acik-mi-uretim.json` bulgusu olan mekânlar; (b) üretimde `belirsiz` kalanlar (tarama `belirsiz` ve doğrulama satırı yok, ya da `onay` + `dokunma`); (c) kart metninde (`subtitle`, `summary`, `note`, `visit_status`) "… itibarıyla" tarihli notu olanlar, yılı ne olursa olsun; (d) çekişmeli kararlar: tarayıcı `kapalı` ya da `taşındı` dedi, doğrulayıcı `ret` + `dokunma` ile açık buldu. Sonra kalanlardan rastgele en az ⌈n/2⌉ mekân, öncelikliler n'yi doldursa da (üretimin işaretlemediği kapanışı yalnız bu kısım yakalar); toplam en az n. Rastgele sıra `sha256((excel_sha256 + entry_id).encode('utf-8'))` küçükten büyüğe; `excel_sha256` teslim Excel'inin SHA-256'sı, küçük harf onaltılık (envanterdeki değer). Aynı Excel, aynı `ACIKMI` ve aynı kontrol yılı aynı örneklemi verir ((a) kapının yılına bağlıdır). Komut `OUT\acik-mi-orneklem.jsonl`'i yazar (seçilen `_dump\Mekânlar.jsonl` satırları aynen + `neden`: öncelik harfleri, ör. `a+c`, ya da `rastgele`; önce öncelikliler Excel sırasıyla) ve `OUT\_acikmi`'yi her koşuda baştan kurar (eski parti ve ajan dosyaları ile sonraki adımların çıktıları silinir, adım baştan başlar): en çok 8 mekânlık `OUT\_acikmi\parti_NN.jsonl`, mekân başına bir tarama satırı (§3 anahtarları), `durum` = `belirsiz` (denetim açıklığı kanıtsız kabul etmez), kanıt alanları boş, `not` = "denetim örneklemi". Özetteki `oncelikli`, `rastgele` ve `oncelik` (harf başına) rapora gider. Çıkış 2 = girdi eksik ya da bozuk (hiçbir şey silinmez).
  ```powershell
  & $PY $TK\acik_mi_denetim.py orneklem $OUT --xlsx $XLSX --acik-mi $ACIKMI
  if ($LASTEXITCODE -eq 2) { throw 'açık-mı örneklemi kurulamadı: hatayı düzelt, adımı baştan çalıştır' }
  ```
- Doğrulama: kartları yazmamış yeni alt ajanlar (Sonnet; talimat `agents\l1\ACIKMI_PROMPT.md`), `AGENTS\acik-mi.md` §2 + §4 şüpheci rolü; parti başına bir ajan, en çok 5 paralel, ajan başına 25 dk. Ajan girdisi (kart, bağlantılar) `OUT\_acikmi_girdi\girdi_parti_NN.jsonl` (`hazirla_l1.py`), `OUT\_acikmi\`'ye konmaz. Ajana parti dosyasının satırları, kart (`title`, `location`, `district`, `group`, `summary`, `note`), kartın Bağlantılar adresleri, şehir, yerel dil ve kontrol tarihi verilir; üretimin açık-mı dosyaları verilmez. Ajan yalnız `OUT\_acikmi\parti_NN_dogrulama.jsonl` yazar, her mekâna bir §4 satırı: `ret` = durumu kanıtla belirledi (açık, kapalı, geçici kapalı, taşındı, inşaat), `onay` = belirsiz kaldı; tek kaynaklı kapanışta §4 gereği yine `onay` + `sil`. `sil`'de her ikinci kaynak `gerekce`'de `<tam adres> «<sayfadan birebir alıntı>»` biçiminde yazılır (kanıt kopyası bunu okur). §1'deki WORK yolları, §5 ve §6 denetimde geçmez.
- Kapı ajan satırlarını mekanik sınar (çıkış 0 temiz, 1 bulgu, 2 kullanım hatası). `--kaynaklar` verilmez: denetimin bulduğu kanıt kartın kaynaklarında olmak zorunda değildir.
  ```powershell
  & $PY $TK\acik_mi.py $OUT\_acikmi --mekanlar $OUT\acik-mi-orneklem.jsonl --out $OUT\acik-mi-denetim.json
  ```
- Kayıt kusuru, paket bulgusu değil: `tarama_yok`, `gecersiz_durum` → `_acikmi` örneklemden sonra elle değişmiştir, örneklem komutundan baştan; `dogrulama_yok` (ajan mekânı atladı; boş tarama satırı `bos_alinti` ve `bos_url` de verir), `gecersiz_sonuc`, `gecersiz_eylem`, `bos_alinti`, `bos_url`, `kimliksiz` → o mekân yeni ajana. Yeni ajan aynı `parti_NN_dogrulama.jsonl`'de yalnız o mekânın satırını yeniden yazar (satır yoksa ekler, `entry_id`'siz satırı siler), öteki satırlar aynen kalır; ana döngü dosyayı elle değiştirmez ve satırı başka dosyaya yazdırmaz (eski satır kalır, kapı bulguyu sürdürür); sonra kapı yeniden çalışır. İkinci denemede de kusur kalırsa mekân doğrulanamadı sayılır (`sayim` onu `dogrulanamadi` ya da `…_teyitsiz` yapar). `eski_kanit`, `footer_kanit`, `eylem_celiski`, `kaynak_izi_yok` bu kapıda çıkmaz (tarama satırı `belirsiz`, `--kaynaklar` yok); çıkarsa parti dosyası yanlıştır. Kapı doğrulama satırındaki açık kanıtının tarihine ve telif satırına bakmaz; onu aşağıdaki ikinci kapı sınar.
- Açık kanıtı ve kanıt kopyası (kayıt kusurları bitince; her yeni ajandan sonra kapıyla birlikte yeniden): `kanit` komutu `sil` ve `kartta belirt` dışındaki örneklem mekânlarını ikinci kapının tarama satırına çevirir: `ret` + `dokunma` → `durum` = `açık`, geri kalanı (`onay` + `dokunma`, satırı yok ya da geçersiz) → `belirsiz`; kanıt alanları ajanın satırından. Satırlar `OUT\_acikmi_acik\acik.jsonl`'e, mekânları `OUT\acik-mi-acik-liste.jsonl`'e yazılır; ikinci kapı `açık` satırında `eski_kanit` (kanıt kontrol yılı ya da önceki yıl tarihli faaliyet değil: tarihsiz, eski ya da tarihi footer, telif, erişim günü) ve `footer_kanit` (alıntı yalnız telif satırı), `belirsiz` satırında `dogrulama_yok` verir. Aynı komut `sil` ve `kartta belirt` satırlarının `kanit_url` + `kanit_alinti`'sini ve `sil`'in `gerekce`'sindeki her `adres «alıntı»`'yı `OUT\kanitlar\acikmi\kanit.jsonl` ve `urls.txt`'ye yazar; `fetch_snapshot` sayfaları oraya kaydeder ve alıntıyı sayfada arar (`evidence_missing` = alıntı sayfada yok). `sayim` mekân başına sınıfı ve sayıları `OUT\acik-mi-sayim.json`'a yazar; ikinci kapının raporu ya da kanıt kopyası `kanit`'ten eskiyse çıkış 2 verir. Klasörler ve listeler her koşuda baştan kurulur; liste boşsa ikinci kapı çıkış 2 verir (boş liste), `sayim` bunu bekler.
  ```powershell
  & $PY $TK\acik_mi_denetim.py kanit $OUT
  if ($LASTEXITCODE -eq 2) { throw 'açık-mı kanıt listesi kurulamadı: hatayı düzelt, bloğu baştan çalıştır' }
  & $PY $TK\acik_mi.py $OUT\_acikmi_acik --mekanlar $OUT\acik-mi-acik-liste.jsonl --out $OUT\acik-mi-acik.json
  & $PY $TK\fetch_snapshot.py --urls $OUT\kanitlar\acikmi\urls.txt --must-contain $OUT\kanitlar\acikmi\kanit.jsonl --out-dir $OUT\kanitlar\acikmi --cache-dir $OUT\_cache --retry-transient
  & $PY $TK\acik_mi_denetim.py sayim $OUT
  ```
- Kanıtı yetmeyen mekân (`acik-mi-sayim.json` → `yeni_ajan`: ikinci kapıdan bulgulu `ret` + `dokunma` satırı; alıntısı kopyada teyit edilemeyen ya da `gerekce`'sinde başka sitede `adres «alıntı»` olmayan `sil`/`kartta belirt`) bir kez yeni ajana gider (kayıt kusurundaki gibi), sonra kapı ve bu blok yeniden çalışır. İkinci denemeden sonra sınıf kesindir.
- Sınıflama (`acik-mi-sayim.json` → `mekanlar[].sinif`; ISSUE `check_id` K39, ölçüt B5; ISSUE'ya `_dump` satırının `_row`'u, ajanın kanıt adresi ve birebir alıntısı, `sil`'de `gerekce`'deki ikinci kaynak ve mekânın durak olduğu rota kartları (`_dump\Rotalar.jsonl` → `stop_entry_ids`'inde mekânın `entry_id`'si geçen satırların `route_id`'si ve `_row`'u) yazılır). `sil` ve `kartta belirt` satırının sınıfı `sonuc`'a bakmaz (kapı da bakmaz); `sonuc` yalnız `dokunma`'yı ayırır:
  - **P0** — `sil_listede`, `ikinci_kaynak_yok` olmadan, ve `kapanis_iki_kaynak` (kanıt kopyasında iki ayrı sitenin alıntısı teyitli): kalıcı kapalı ya da şehir dışına taşınmış mekân iki bağımsız kaynakla teyitli ama pakette. Gerekçe: kılavuzun P0'ı (kritik yanlış bilgi, yayın engeli: okur kapanmış yere gönderilir); kayıt artık gerçek mekân değildir, K42 (`sev` P0) de `kaldı`, ölçüt B1 de. Tek kapanış bile üretimin açık-mı kapısını şüpheli yapar: önerilen düzeltme yalnız bu kaydı ve rota durağını silmek değil, bütün listenin places fazında yeniden taranmasıdır (`acik-mi.md`).
  - **P1** — `sil_listede` + `kapanis_teyitsiz`: tek kaynaklı (`ikinci_kaynak_yok`) ya da kopyada iki sitenin alıntısı birlikte teyit edilemeyen kapanış (yeni ajandan sonra da); yayın engeli için kanıt yetmez, yayından önce insan teyidi gerekir (`acik-mi.md` §4).
  - **P1** — `not_yok` + `belirt_teyitli`: geçici, mevsimlik ya da kısmi kapanış, tadilat, inşaat ya da şehir içinde taşınma kartta tarihli notla yazılı değil (taşınmada adres, semt, koordinat ve harita bağlantısı aynı bulguda). Kartta aynı olgu önceki bir yılın tarihiyle yazılıysa P2 (notun tarihi yenilenir).
  - **P1** — `kartta belirt` kapıdan temiz geçti (kartta güncel not var), `belirt_teyitli`, ama ajanın `yeni_bilgi`'si nottan başka bir olgu söylüyor (süre, adres ya da kapsam değişmiş). Aynı olguysa bulgu değil.
  - **P2** — kart kapalı ya da taşındı diyor, ajan açık buldu (`ret` + `dokunma`, `acik_dogrulandi`): not eskimiş; okuru kapanmış yere göndermez.
  - Bulgu değil: `ret` + `dokunma` ve ikinci kapıdan (`acik-mi-acik.json`) bulgusuz → `acik_dogrulandi`, doğrulandı (açık kanıtı kontrol yılı ya da önceki yıl tarihli, telif satırı değil; bunu ana döngü değil ikinci kapı sınar). `dogrulanamadi` (ikinci kapı: `dogrulama_yok` = `onay` + `dokunma` ya da geçerli satırı yok; `eski_kanit`, `footer_kanit`, `bos_alinti`, `bos_url` = açık kanıtı bu şartı taşımıyor, ör. yalnız telif satırı ya da eski haber) ve `belirt_teyitsiz` → doğrulanamadı (kontrol edilemedi, raporda liste).
- CHECK: K39 bulgu varsa `kaldı`, yoksa `kısmi` (örneklemden bütün pakete `geçti` çıkmaz); `incelenen_kapsam` = örneklem/mekân sayısı (öncelikli ve rastgele ayrı), doğrulanan, doğrulanamayan: hepsi `acik-mi-sayim.json`'dan (`orneklem`, `oncelikli`, `rastgele`, `dogrulanan`, `dogrulanamayan`), elle sayılmaz. Kanıt yolu `acik-mi-denetim.json`, `acik-mi-acik.json`, `acik-mi-sayim.json`, `kanitlar\acikmi\` ve `OUT\_acikmi\`. Raporda örneklem listesi (seçilme nedeniyle) ve üretim beyanıyla fark (ör. üretim `açık` dedi, denetim kapalı buldu) ayrı satırdır.

**Diğer L kontrolleri:** `CHECKS`'te `exec: L`, `sev: P0/P1` olanlar; her biri için `KILAVUZ`'daki yöntem (yalnız ilgili K bölümü okunur). K39 bu yöntemle değil, yukarıdaki açık-mı adımıyla yapılır. P2 L kontrolleri `not_checked` + gerekçe "L1 kapsamı dışında".

## L2: tam

L1 + tüm iddialar, tüm `L` ve `V` kontrolleri, açık-mı doğrulaması örneklemle değil bütün mekânlarla (`acik_mi_denetim orneklem --tam`; K39 yalnız burada `geçti` olabilir: bulgu yok ve `acik-mi-sayim.json`'da `dogrulanamayan` 0), tüm URL'lerin anlamsal hedef kontrolü (sayfa gerçekten kartın konusunu mu anlatıyor), kapak/hero uyumu.

## Kayıt şablonları (kılavuz bölüm 16, birebir)

- **CHECK** → `check-results.json`: `check_id | durum | beklenen_kapsam | incelenen_kapsam | yöntem | kanıt_yolu_veya_URL | bulgu_IDleri | sınır_gerekçe | checked_on`
  `durum` ∈ `geçti | kaldı | kısmi | uygulanmaz | not_checked | separate_stage` (değerler birebir; `partial` yalnız `criteria.json`'daki ölçüt durumudur)
- **ISSUE** → `issues.json`: `issue_id | öncelik | kategori | check_id | tablo | Excel_satırı | entry_id/photo_id | dosya | alan | mevcut_değer | beklenen | somut_gözlem | kanıt | kullanıcı_etkisi | önerilen_düzeltme | tekrar_kontrol_koşulu | durum`
- **CLAIM** → `claim-checks.json` (iddia denetçisi çıktısı + script sonucu birleşik)
- **PHOTO** → `photo-review.json`: `photo_id | dosya | SHA256 | gerçek_format | width | height | bağlı_entry_id | hedef_mekân | görüntüde_görülen | eser_kaynak_eşleşmesi | gerçek_yazar | lisans_sürümü | lisans_URL | ek_hak_notu | kaynak_kanıtı | lisans_kanıtı | türev_grubu | görsel_sonuç | hak_zinciri_sonucu | incelenen_dosya_hashi` (bayt/format/SHA envanterden, görsel sonuç ajandan, lisans validate_all'dan)
- **URL** → `url-checks.json` (url_check çıktısı zaten bu alanları taşır)
- **COVERAGE** matrisi raporda: tablo kayıtları, foto baytları, foto görsel eşleşme, hak zinciri, kritik iddialar, benzersiz URL'ler (200/404/diğer/belirsiz), sayfa alanları x/23, önizleme `separate_stage`, insan kararı.

## Puan ve karar

1. `OUT\criteria.json` oluştur: 25 alt ölçüt `{code, passed, required, status, reason}`, `findings` (issues'tan `{id, priority, criteria}`), `coverage {cards, photos, critical_claims}` (her biri `[incelenen, toplam]`). Önizleme ölçütü (E4) `separate_stage`.
   - Kullanılabilirliği doğrulanmamış sayım ölçütü (L0'da A1, B1–B4, C1, C3, C5): script bir kısmını doğruladıysa `partial` + `passed: 0` (doğrulanan alt sınır), hiç bakılmadıysa `not_checked`; ham sayı `reason`'a. Ham sayıyı `ok` + `passed` diye yazma.
   - Her KALDI birim `findings[].criteria` ile bir bulguya bağlanır; bağlanmazsa script kararı KANIT EKSİK'e çeker.
2. **Hedef eksiği = P1.** Berlin hedefinin altındaki her sayım, alt sınır karşılansa bile (`_render\TESLIM_OZETI.txt`'te "hedefin altında" satırları; pilot: mekân 104/120, tekil foto 201/250), K17 P1 ISSUE olur ve ölçütüne bağlanır: A1 yanıt 240, B1 mekân 120, B2 mahalle 16, B3 rota 12, B4 sözlük 60, C1 foto 250, C5 kapak 8. Fotoğrafsız mekân/mahalle K22 P1 (C3); 12 konu ayrı karar kapısıdır. `editorial_score` açık P1'i **DÜZELTME GEREKLİ** yapar. A1, B1–B4 ve C1 sabit paydalıdır: ölçüt `ok` ve `passed` paydadan küçükse script bunu kendisi de "eksik hedef" sayar, karar aynıdır. Hedef eksiğini P2'ye düşürme, "alt sınır geçti" diye kapatma.
3. ```powershell
   & $PY $TK\editorial_score.py --input $OUT\criteria.json --out $OUT\score.json --format md
   ```
4. Karar script'ten gelir: HAZIR / DÜZELTME / KANIT EKSİK. Elle yükseltilmez.

## Rapor (`OUT\DENETIM_OZETI.html` veya `.md`)

İlk satır birebir: `Editoryal hazır olma: %X | Denetim kapsamı: <LEVEL>, yerel paket denetimi, ... | Karar: ...`. Kapsam kısmına `score.json` → `cover_line`'daki inceleme kapsamı (kart, fotoğraf, kritik iddia x/y) ve script kapsamı (dosya, satır, URL x/y) yazılır; kısmi denetimde "doğrulanan alt sınır" etiketi kalır.
İkinci satır: `Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: n | Açık P1: n (ID'ler) | P2 öneri: n`.
Sonra sırayla: paket/şema sürümü ve tarih + Excel SHA; Berlin minimum–hedef–fiilî matrisi; öncelikli bulgular (ID/satır/kanıt); yanlış görsellerin pafta numarası ve slot'u; açık-mı örneklemi (seçim kuralı, mekânlar ve seçilme nedeni, sonuç, üretim beyanıyla fark); iddia düzeltmeleri + resmî kaynak; bağlantı hataları kök nedene göre gruplu; düzeltme sırası (son adım her zaman: yeni sürümle L0, ardından L1); çalıştırılmayan kontroller listesi.

## Kullanıcıya

Sade Türkçe, 3–5 satır: yüzde, karar, en önemli 3 sorun, sonraki adım. "Bu bir yayın onayı değildir" notu.
Ayrıca bir satır: `RUN_LOG için: <OUT>\score.json` (OUT'un tam yoluyla). Üretim tarafı bu dosyayı `run_log --score` ile şehrin `RUN_LOG.csv`'sine ekler. Denetim `run_log`'u kendisi çalıştırmaz, çünkü o WORK klasörüne yazar.
