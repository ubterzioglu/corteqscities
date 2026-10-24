# Ülke paketi denemesi (İspanya) — ana skill'den bağımsız

Durum: DENEME. `city-pack` ve `city-audit` skill dosyalarına, `manifest.schema.json`'a ve mevcut testlere dokunulmaz.
Plan: `C:\Users\baris-terzioglu\.claude\plans\linear-inventing-thacker.md`.

## Kurallar
1. Şehirler SIRAYLA yapılır. İki şehir aynı anda yürütülmez (kalite düşüyor). Kullanıcı bir şehir adı verince o şehir bitmeden diğerine geçilmez.
2. Deneme, ana akışın yerine geçmez: şehir paketi her zamanki `city-pack` zinciriyle üretilir; bu belge yalnız ülke/bölge paketini kurmayı ve şehre uygulamayı anlatır.
3. Ülke paketi kendi küçük manifest'iyle kurulur (`ROOT\ulke\ES\pack.json`); şehir manifest'ine faz eklenmez.

## Paket düzeni (`ROOT\ulke\ES\`, bölge için `bolge\<ad>\` altında aynısı)
- `pack.json`: `{country, version, built, cards: {slug: {sha256, valid_until}}}`
- `Yanıtlar.ulusal.jsonl`, `Bağlantılar.ulusal.jsonl`, `claims\ulusal.jsonl`
- `kaynak_dizini.jsonl` + `kaynaklar\` (kopyalar)
- Kartlar şehir-nötr: şehir adı yerine `{sehir}`, `entry_id = es:<slug>`, `source_id = es:kaynak:NNN`.
- Tarihe duyarlı kartta (SMI, vergi dilimi, ITP, vize ücreti, tatil) `valid_until` yazılır.
- `sha256` = `country_apply.card_hash` (kimlik alanları hariç kart + claim'ler).

## Şehirde kullanım (`deneme_ulke_paketi\country_apply.py`; toolkit'e dosya eklenmez)
```powershell
$DU = "<corteqs-skills>\deneme_ulke_paketi"
& $PY $DU\country_apply.py apply $WORK\_is --pack $ROOT\ulke\ES --city-id <sehir> --city-name <Şehir> --order-start <N>
& $PY $DU\country_apply.py audit-scope $WORK\_is --pack $ROOT\ulke\ES --out $WORK\_is\ulke_denetim_kapsami.json
```
- `apply` yalnız `valid_until` geçmemiş kartları kopyalar; `stale` listesi yazara gider (yeniden doğrulanır).
- Yazarlara yalnız şehre özgü kartlar yazdırılır; her kartta şehre uyarlanmış giriş cümlesi ve yerel adım şart (tekrar içerik riski).
- Claim denetiminde `audit-scope` çıktısındaki `skip` kartlar atlanır; `audit` kartları ve şehir kartları tam denetimden geçer.

## Ölçüm
Ülke, bölge, şehir fazları ayrı süre/token olarak `RUN_LOG`'a yazılır. Taban: Bakersfield ~7 sa / 6,9 M çıktı / ~130 ajan.
