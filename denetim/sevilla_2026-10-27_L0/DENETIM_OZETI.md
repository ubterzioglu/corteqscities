# Sevilla (CITY-107) — yerel paket denetimi, L0

Denetim kapsamı: L0 (yalnız script, ağ hariç LLM yok), yerel paket denetimi | Karar: **KANIT EKSİK** (script'in kesin gösterdiği P0/P1 yok; L0'ın en iyi sonucu)
Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: 0 | Açık P1: 0 | P2 öneri: 6

Editoryal yüzde hesaplanmadı: bu koşuda yalnız L0 bölümleri ve kapanış uygulandı (`criteria.json` / `editorial_score` çalıştırılmadı). Bu bir yayın onayı değildir.

- Denetim tarihi: 2026-10-27 · denetçi: bağımsız oturum (paketi üretmedi)
- Paket: `C:\temp_private\corteqs\0000_newera\uretim\sevilla\paket` (salt okunur; PKG'ye yazılmadı)
- Excel: `CITY-107_sevilla_v001.xlsx`, şema 1.0, sürüm/tarih v001 · 2026-10-27, SHA-256 `556343a623a674241fa1519e64d7c23ee8903a00667a535ede360bedd5adb663`
- Önceki denetim: `denetim\sevilla_2026-10-26_L1` (L2; Excel SHA `6fefa38b…`) — Excel değişti.
- Paket: 1949 dosya, 407,18 MB, 765 görüntü; eksik 0, SHA uyuşmazlığı 0, uzantı hatası 0, artık 0, `dup_sha` 21.
- Temiz bağlam: `_is\`, manifest ve üretim notları okunmadı. `Teslimler\ACIK_KONULAR.txt` beyan olarak okundu, kanıt sayılmadı.

## 1. Kanıt kapsamı (dış denetim modeli, `kanit-kapsami.json`)

| | Değer |
|---|---|
| Puan alt sınırı | **%93,78** |
| Önizlemeyle azami | %98,78 (D5, E4 önizleme aşamasında) |
| Eksik ölçütler | **B1** (mekân doğrulama 110/120), **B5** (136'nın 126'sı), **C4** (görsel kalite 284/334, "kırpma + netlik; kesin sonuç önizlemede") |

Bu bizim editoryal yüzdemiz değil; dış denetçinin pakette bulamayacağı kanıtı gösterir. Eksik her ölçüt bir P2 bulgusudur (K83 kapsamında "kanıt teslimde yok"). Düzeltme sırası: city-pack teslim zinciri, kanıt dosyaları.

## 2. Berlin hedefleri (minimum – hedef – fiilî; `_render\TESLIM_OZETI.txt`)

| Ölçü | Alt sınır | Hedef | Fiilî | Durum |
|---|---|---|---|---|
| Pratik yanıt | 212 | 240 | 241 | hedef karşılandı |
| Gerçek mekân | 92 | 120 | 120 | hedef karşılandı |
| Mahalle | 12 | 16 | 16 | hedef karşılandı |
| Dolu konu | 12 | 12 | 12 | hedef karşılandı |
| Tekil mekân fotoğrafı | 187 | 250 | 326 | hedef karşılandı |
| Tekil kapak | 6 | 8 | 8 | hedef karşılandı |
| Rota | 9 | 12 | 12 | hedef karşılandı |
| Sözlük | 48 | 60 | 60 | hedef karşılandı |

Hedef eksiği yok (K17 P1 yok). Fotoğraflı mekân 120/120, fotoğraflı mahalle 16/16 (K22 P1 yok).

## 3. Script'in kesin gösterdiği bulgular

### P0: yok · P1: yok

### P2 (6)

| ID | Kontrol | Bulgu | Kanıt |
|---|---|---|---|
| L0-P2-01 | K83 / ölçüt B1 | Mekân doğrulama kanıtı 110/120; 10 mekânın kaydı teslimde yok | `kanit-kapsami.json` (`mekan-dogrulama-v7.jsonl`) |
| L0-P2-02 | K83 / ölçüt B5 | Mekân+mahalle doğrulama kanıtı 126/136 | `kanit-kapsami.json` |
| L0-P2-03 | K83 / ölçüt C4 | Görsel kalite kanıtı 284/334 | `kanit-kapsami.json` (`gorsel-kalite-v7.json`) |
| L0-P2-04 | K05 | 14 aynı SHA'lı grup `Fotoğraflar\` dışında: hepsi `Lisans kanıtları\` içinde kapak↔mekân çiftinin aynı kaynak/lisans kanıt dosyaları (kapak-01…08 ↔ plaza-de-espana-01, catedral-de-sevilla-giralda-01, puente-de-triana-01, parque-de-maria-luisa-01, metropol-parasol-antiquarium-01, palacio-de-san-telmo-01, alameda-de-hercules-cevresi-01). Aynı kare kapakta ve mekânda kullanıldığı için içerik aynı; artık kopya değil, düşük öncelikli tekilleştirme önerisi | `_foto\hazirlik.json` → `ayni_sha.K05` |
| L0-P2-05 | URL bakım | `https://casadelaguitarra.es/` → `https://flamencoensevilla.com/` başka alan adına yönleniyor (Bağlantılar!302, Kaynaklar!343) | `url-checks.json` (`cross_host_redirect`) |
| L0-P2-06 | URL bakım | `https://www.aussa.es/` → `https://aussa.com/` (Kaynaklar!178) | `url-checks.json` |

## 4. Kontrol sonuçları (script çıktısı)

| Kontrol | Sonuç |
|---|---|
| `validate_all --mode audit --new-content` | yapı hatası **0**, uyarı 1002 (334 Kanıtlar satırı × 3 insan inceleme alanı: metadata/pixel/rights incelemesi açık, beklenen), medya hatası **0**, `technically_complete=True`, `minimum_gaps` boş. Ek kontrol (resmî sayıya dahil değil): `shared_coordinates` 2 (mercado-de-la-encarnacion ↔ metropol-parasol-antiquarium; estadio-benito-villamarin-tur ↔ estadio-la-cartuja → K108 için L1 girdisi), `history_share` 57/120 = %47,5 > %35 eşik (öneri) |
| `url_check` (Kaynaklar, Bağlantılar, Şehir, SayfaAlanları) | 503 tekil URL / 1085 ilişki. 1. koşu: 4 ağ hatası + 2×403. `--retry-transient` ile 2. koşu: **çalışıyor 501, bozuk 0, erişim teyidi açık 2** (www.spain.info 403: `teatro-maestranza-sevilla`, `moneda-billetes`; L1'de ajan açar). `homepage_only` 17 (L1 → K51/K53), `cross_host_redirect` 2 (P2 yukarıda), `redirected_to_homepage` 0, Wikipedia 0 |
| `preview_checks warning-scan` | **K103 0, K104 0, K105 0**; 2574 kayıt, 2196 değer; bant alanında 4 değer (SayfaAlanları hero alanları), uyarı yok |
| `text_quality` (hitap sen) | bulgu 0; kaçamak 0, temkin 0, yer tutucu 0; hitap karışık 0; 1 kısa tekrar grubu (`cost` = "Ücretsiz" ×3, zararsız) |
| Ters eğik çizgi (K84) | **0** her yolda (Fotoğraflar.file 0/334, FotoğrafKaynakları 0/334+0/334, Kanıtlar üç sütun 0/334, Kaynaklar.snapshot_file 0/499, Teslimler JSON/CSV/HTML hepsi 0) → K84 bulgusu yok |
| Kanıt dosyası | 334 = Kanıtlar satırı 334; `kanitsiz_foto` 0; `eksik_alanli_foto` yok |
| K107 aday sayısı | `photo_candidates` aday **334** = Fotoğraflar satırı 334. Ön eleme: keep 304, flag 27, reject 3 (L1 girdisi, karar değil; reject: palacio-de-las-duenas-03 ve la-macarena-02 `art_not_photo`, la-cartuja-02 `name_extended+detail_interior`). Teslim: 334 ilişki, tekil mekân karesi 326, tekil kapak 8. `entries_without_shortlist` 0 = K22 sayısı (0) ile tutarlı |
| K64 | `ai_generated` 0 → bulgu yok; KAPSAM gereği `kısmi` (görsel inceleme L1) |
| K67 | `license_not_allowed` 0, `restrictions` 0 → bulgu yok; `kısmi` |
| K63 | `ayni_sha.K63` 0, dHash çifti 7 (hepsi `kapak_mekan`), `K63_aday` boş → **geçti** |
| K05 | `kapak_mekan` 7 (zararsız), `K05` 14 → P2 (L0-P2-04) |
| K14 Teslimat | `updated_on` 2026-10-27 = en son içerik tarihi (Yanıtlar `reviewed_on` 2026-10-27); `notes` şablon değil → bulgu yok |
| K76 kopya karşılaştırması (kısmi) | 499 kaynak, 495 karşılaştırıldı (4 taze kopya yok: kaynak:008, 127, 227, 374 — 2 zaman aşımı, 2×403). Başlık eşleşen 492, örtüşme medyanı 1,0. Başlık farklı + düşük örtüşme **2**: kaynak:081 (Kaynaklar!84) ve kaynak:106 (Kaynaklar!108), seg-social.es — paket kopyası İspanyolca, taze kopya İngilizce sürüm ("Benefits / Pensions for Workers"); dil sürümü farkı görünüyor, uydurma işareti değil; L1'de bakılır. kaynak:064 başlık farkı yalnız sayfa başlığı uzunluğu (örtüşme 1,0) |
| `fetch_snapshot` | 499 URL, 495 kopya, 4 başarısız (yukarıdaki 4), soft-404 0, ince metin 0 |
| `claim_extract` / `claim_check` | 2562 iddia, 196 kayıt; supported 1065, not_in_source 1497, no_snapshot 0, homepage_only_source 0, no_source 0. Yalnız tutarlılık; doğruluk L1'de |
| K83 özet | paket `Teslimler\TESLIM_OZETI.txt` ↔ denetimin `_render\TESLIM_OZETI.txt`: **fark yok** (Durum, Açık konu sayısı, Resmî doğrulayıcı, sekme, Berlin, fotoğraf, dosya/MB satırları aynı) |
| K83 yol | paket envanteri ↔ denetim envanteri: **fark yok** |
| K04 sabitleme | baş ve son envanter: **fark 0** → paket denetim sırasında değişmedi, denetim geçerli |
| `render_summary` | "TEKNİK KONTROL GEÇTİ — insan paket incelemesi bekliyor"; engelleyici 0, bilgi 3 |

## 5. Önceki denetime göre etki (`impact.json`, `impact-eski-bulgular.json`)

`impact.py` önceki Excel kopyasıyla (`denetim\sevilla_2026-10-26_L1\_foto\kanit\CITY-107_sevilla_v001.xlsx`, SHA 6fefa38b…) çalıştı: 1076 değişen, 78 eklenen, 73 silinen kayıt; etkilenen 1472; etkilenen kontrol 36 (K12, K19, K22, K23, K25, K26, K29, K30, K32, K35, K42–K51, K53, K55, K57–K62, K67, K69, K70, K76, K77, K80, K86, K87).

Eski 44 bulgunun dosya farkına göre durumu (L0 içerik kapanışını teyit etmez; "Kapandı?" ve "Kısmen" L1'de doğrulanır):

| Eski öncelik | Kısmen (kayıt değişti) | Kapandı? (kayıt silindi) | Açık (kayıtta fark yok) |
|---|---|---|---|
| P1 (15) | 13 | 1 (ISS-034) | 1 (ISS-033, K19 Konular: Konular sekmesinde fark yok) |
| P2 (29) | 14 | 7 | 8 |

## 6. Çalıştırılmayan kontroller

- L1/L2 yok: `exec: L` ve `V` kontrollerinin hepsi `not_checked` (iddia doğruluğu, K39 bugün açık mı, fotoğraf görsel incelemesi ve paftalar, K108 alt nesne, anlamsal URL hedefi). Temas sayfaları (12 pafta) üretildi, bakılmadı.
- K73, K81 `not_checked`.
- K09 `xlsx_fidelity`: Atınç girdi şablonu verilmedi, çalıştırılmadı.
- Drive (K01, K03, K109, K110) ve önizleme (K92–K94, K111, K112; K103'ün sayfa kısmı) → `separate_stage`. D5, E4 önizlemede.
- Açık-mı üretim beyanı: `ACIKMI` verilmedi ("üretim açık-mı beyanı yok"); L0'da açık-mı adımı yok.
- Editoryal puan (`criteria.json`, `editorial_score`) bu görevin kapsamında değildi.

## 7. Düzeltme sırası

1. city-pack teslim zinciri, kanıt dosyaları: B1 (10 mekân), B5 (10 kayıt), C4 (50 kare) kanıtlarını teslime ekle.
2. P2 bakım: iki alan adı yönlendirmesini güncelle (casadelaguitarra.es, aussa.es); isteğe bağlı `Lisans kanıtları` tekilleştirmesi.
3. L1 girdileri: 2 adet 403 (spain.info), 17 ana sayfa kaynağı, K76'daki 2 seg-social.es dil sürümü, `shared_coordinates` 2 çift, ön elemedeki 3 reject + 27 flag, eski P1'lerin kapanış teyidi.
4. Son adım: yeni sürümle L0, ardından L1.

## Çıktılar

`dosya-envanteri.json`, `_dosya-envanteri-son.json`, `_dump\`, `validation-audit.json`, `_render\`, `text-quality.json`, `uyari-tarama.json`, `url-checks.json` (2. koşu; 1. koşu `url-checks.ilk.json`), `kanitlar\snap\`, `claims.jsonl`, `claim-script.json`, `kanit-kapsami.json`, `_foto\` (hazirlik, candidates, plan, decisions, dhash-ciftleri), `temas-sayfalari\`, `_analiz\snapshot-karsilastirma.json`, `impact.json`, `impact-eski-bulgular.json`.
