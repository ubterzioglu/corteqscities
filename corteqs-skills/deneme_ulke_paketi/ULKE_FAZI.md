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

## İkinci ülke: Almanya (`ROOT\ulke\DE`, v1, 25.10.2026)
- Aynı akış, tek Windows oturumunda, ölçümlü: 113 kart / 11 konu / 2120 iddia / 193 kaynak; 2 sa 21 dk duvar saati, 3,9 M çıktı token, 15,6 M önbellek dışı girdi, 52 Sonnet ajanı (11 keşif, 11 yazar, 11 denetçi, 11 editör, 4 dar denetim, 4 kısa editör). Kayıt: `ulke\DE\_is\phase_usage.csv`, `phase_log.jsonl` (fazlar gerçekte paralel çalıştı; log ardışık pencerelere indirildi).
- Ülkeye özgü dosyalar: `DE_aday_kartlar.md` (108 aday → 113 kart), `DE_YAZAR_NOTLARI.md` (federal yapı, Türk okuyucu, çeviri, kaynak öncelikleri), görev metinleri `ulke\DE\_is\kesif\KESIF_GOREV.md`, `ulke\DE\_is\yazar\{YAZAR,DENETCI,EDITOR}_GOREV.md` (ülkeden bağımsız; sonraki ülkede kopyalanıp kimlikler değiştirilir).
- `pack_check` şehir adı taraması ülkeye göre (`CITIES_BY_COUNTRY`, yol `ulke\<ISO>` ile seçilir). `pack_check` ve `merge_package` alıntı karşılaştırması yumuşak tireyi (U+00AD) ve sıfır genişlikli karakterleri yok sayar (Alman resmî sayfalarında tireleme yaygın).
- Keşifte ders: ajanlar sayfayı WebFetch değil düz indirme + etiket ayıklama ile okuyup `must_contain`'i öyle doğruladı; 11 konuda 264 adayın 261'i `add_sources`'ta kabul edildi. Windows sertifika deposu bazı Alman sitelerinin ara sertifikasını ilk denemede tanımadı (`tls` hatası); `curl` ile bir kez açılınca Python da açtı → `--retry-transient` ile ikinci deneme yeter.
- Editör kuralı genişletildi: ciddi/orta bulgu için editör `add_sources` ile kaynak ekleyebilir (kart başına 2 sınırı korunarak); küçük bulgu için eklemez.
- Bölge (eyalet) paketi yok; şehir sırası ve eyalet dağılımı `ROOT\ALMANYA_YENI_SEHIR.md`.

## Bölge paketi (`ROOT\ulke\ES\bolge\<ad>\`)
- Aynı düzen ve aynı akış (keşif → `add_sources` → yazar → `pack_check` → bağımsız denetim → editör). Çalışma klasörü `bolge\<ad>\_is\`; kaynak kimliği `add_sources --city-id es-<kısa>` ile (ör. `es-an:kaynak:001`), ulusal kimliklerle çakışmaz.
- Kartlarda kimlik biçimi ulusalla aynı (`entry_id es:<slug>`, `topic_id es:<konu>`, `action_id es:action:...`); slug ulusal paketle çakışmamalı (`endulus-` öneki). Yalnız bölgeye özgü bilgi; ulusal kartı tekrarlama.
- Kurulum: `pack_build.py <bolge\<ad>> --country ES --version N --topics saglik,para,... --region <ad>`.
- Şehre uygulama: `country_apply` bir iş klasörüne TEK paket uygular ve `merge_package` her konu için tek parça dosyası bekler. Bu yüzden önce birleşik paket kurulur, sonra o uygulanır:
```powershell
& $PY $DU\pack_merge.py --pack $ROOT\ulke\ES --pack $ROOT\ulke\ES\bolge\andalucia --out $WORK\_is\ulke_paketi
& $PY $DU\country_apply.py apply $WORK\_is --pack $WORK\_is\ulke_paketi --city-id <sehir> --city-name <Şehir> --order-start <N>
& $PY $DU\country_apply.py audit-scope $WORK\_is --pack $WORK\_is\ulke_paketi --out $WORK\_is\ulke_denetim_kapsami.json
```
- `pack_merge` her paketin kartlarını kendi hash'iyle doğrular; slug ve kaynak kimliği tekrarını, farklı ülke kodunu reddeder. Testler: `test_pack_merge.py`.

## city-pack ile birlikte kullanım (ilk gerçek şehir: Sevilla) — adım sırası
Skill'e dokunulmaz; skill zaten `manifest.country_pack` ve yazara `country_cards` girdisini tanır (SKILL.md "Ülke paketi", `agents/yanit-yazari.md`). Bu deneme yalnız dosyaları hazırlar.
1. Kullanıcı ülke paketini verir: intake'te `manifest.country_pack` = `$WORK\_is\ulke_paketi` (birleşik paket yolu) yazılır; RUN_LOG notunda bu yol geçer.
2. Intake'ten sonra, YAZARLARDAN ÖNCE (klasörler ve boş `kaynak_dizini/kaynak_taslak` hazırken) `pack_merge` + `country_apply apply` çalıştırılır (yukarıdaki komutlar; `--order-start 9000`, şehir yazarlarının `konu × 100` aralığıyla çakışmaz). `apply` hedef dosya varsa durur: yazarlar başlamadan çalıştırılmalı.
3. `apply` her konunun `data\parcalar\Yanıtlar.<konu>.jsonl`, `Bağlantılar.<konu>.jsonl`, `claims\<konu>.jsonl` dosyasını ülke+bölge kartlarıyla yazar. Şehir yazarı AYNI dosyayı yazar: yazara bu dosyalar `country_cards` olarak verilir ve talimata eklenir: "Bu dosyadaki satırları SİLME ve değiştirme; kendi kartlarını dosyanın SONUNA ekle; ülke kartıyla aynı konuyu tekrar yazma, şehre özgü olanı ayrı kart yap." (Ülke kartı değişirse `audit-scope` onu tam denetime alır; değişmeyen kart claim denetimini atlar — tasarruf buradan gelir.)
4. Yazarlardan sonra: `country_apply audit-scope` → `audit_reasons` içinde "kart şehirde yok" çıkarsa bir yazar ülke kartını silmiştir (geri alınır). `skip` kartları claim denetiminden çıkarılır; `audit` kartları ve şehir kartları tam denetimden geçer.
5. `merge_package` ülke+bölge kartlarıyla bulut ortamında denendi: 105 kart, 2039 claim, 0 bulgu (2026-10-24). Kartlar `featured` 'Hayır' gelir; konu başına en çok 2 öne çıkan kartı şehir seçer.
6. Ölçüm: ülke/bölge fazı (bir kez) ile şehir fazı ayrı raporlanır; `apply` + `audit-scope` süresi şehir fazına yazılır.
7. Tarih: `apply` geçerliliği bitmiş kartı kopyalamaz (`stale`); 5.11.2026'dan sonra 6 kira kartı `stale` olur — paket güncellenmeden şehir başlarsa bu kartlar şehir yazarına kalır.
