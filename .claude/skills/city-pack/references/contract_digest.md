# Corteqs v7 city package: contract digest

Load this file instead of the 58 KB prompt, the schemas and the Berlin xlsx. It was compiled from Corteqs_Sehir_Icerik_Sablonu_v7.xlsx, sharedschema.json, normalized-tables.schema.json, photo-provenance.schema.json, web-function-contract.json and the official checker in `araclar/arac` (delivery_validation + validation_* + delivery_tools.audit). Every `*` field is required. Enum values are verbatim.

## 0. Global rules
- Schema 1.0, acceptance 2026-10-13.1, provenance extension v7. Language is `tr`. Proper names and local terms keep their original spelling.
- Row 5 holds the note, row 6 the TR header, row 7 the machine key, and data starts at row 8. Keep sheet names, sheet order, rows 6 and 7, column order, DVs, fills and frozen panes unchanged. The reader fails if the row-7 keys differ or if any trailing header cell is non-empty.
- Sheet order: Özet, Teslimat, Şehir, Konular, Yanıtlar, Mekânlar, Mahalleler, Bağlantılar, Rotalar, Sözlük, Adımlar, Kaynaklar, Fotoğraflar, Kanıtlar, SayfaAlanları, EkDetaylar, Web işlevleri (doc only), FotoğrafKaynakları.
- Formula cells are read-only and must never be written: Özet!B,E,F; Konular!H (`used_count`); Fotoğraflar!S,T (`unique_venue_count`, `unique_hero_count`, formulas pre-filled down to row 607). The reader also rejects a formula in any input cell. A text value starting with `=` must not become a formula.
- Lists:
  - `id_list` is separated by `;`.
  - `text_list` puts one item per line inside the cell (`\n`).
  - Duplicate items inside one list cell make the reader fail (parse_list raises). Dedupe them.
- Dates are `YYYY-MM-DD` (an Excel date also works), real check dates only, never in the future. `capture_date` stays empty when unknown, and the download date must not stand in for it.
- Booleans are `Evet`/`Hayır`. Numbers must be real numbers, not text.
- JSON cells contain plain JSON text with double quotes. No code fences, no comments.
- A cell holds at most 32,767 characters. For longer values use the `UzunAlanlar` sheet plus `Teslimler/uzun-alanlar-v7.json`, chunked and SHA-verified. Never truncate.
- An empty field stays truly empty. Do not write null, None, bilinmiyor, `?`, `[[...]]` or any other placeholder.
- IDs: every `*_id` must match `^[a-z0-9][a-z0-9:_-]*$`, which means lowercase ASCII with no Turkish characters.
  - `city_id` is the slug (`eindhoven`).
  - `entry_id` must equal `{city_id}:{slug}` exactly. This applies to answers, places and neighborhoods, and IDs are unique across all three tables.
  - `topic_id` is `{city_id}:{slug}`.
  - The other IDs follow `{city}:{type}:{slug}`. Berlin uses `berlin:src:N`, `berlin:action:anmeldung-1`, `berlin:route:001`, `berlin:term:001`, `berlin:step:1`, `berlin:photo:venue-234`, `berlin:evidence:venue-234`, `berlin:field:facts` and `berlin:detail:x-1`. The prompt's `sehir:kaynak:…` and `sehir:kanit:…` forms are equally valid.
  - `delivery_id` is lowercase as well.
- `city_id` on every row must equal `Şehir.city_id`.
- Every `source_ids` item must exist in Kaynaklar.
- Titles: no duplicate title (casefold) across Yanıtlar + Mekânlar + Mahalleler.
- `order` must be unique within Adımlar, Rotalar, Sözlük and Konular. Photos use a unique `(role, entry_id, order)`.
- Editorial status (`Taslak` | `İnceleme` | `Düzeltme` | `Onaylandı`): AI writes `İnceleme` (Berlin) or `Taslak`, never `Onaylandı`. The ready mode fails on purpose until a human approves.

## 1. Counts (minimum / target)
| type | min | target |
|---|---|---|
| answers | 212 | 240 |
| places | 92 | 120 |
| neighborhoods | 12 | 16 |
| topics with ≥1 answer | 12 | 12 |
| distinct venue photos | 187 | 250 |
| distinct hero photos | 6 | 8 |
| routes | 9 | 12 |
| glossary | 48 | 60 |

- A distinct photo is a union-find group by SHA-256 OR by canonical source page. The same Commons `File:` page counts once, even at different sizes or crops.
- Role sets may overlap, so a hero can also be used as a venue photo.
- The Excel template has these sheet capacities:

| sheet | capacity |
|---|---|
| answers | 300 |
| places | 180 |
| neighborhoods | 40 |
| actions | 800 |
| routes | 30 |
| glossary | 100 |
| journey | 40 |
| sources | 500 |
| photos | 350 (DV to row 357) |
| evidence | 350 |
| page_fields | 120 |
| entry_details | 200 |

- Topics: exactly 12. Each topic needs at least one answer and answers must be spread across topics, not piled into the last one.

## 2. Sheets: keys in order (`*` = required; `[maxlen]`)
- **Teslimat** (1 row): `schema_version*`="1.0", `delivery_id*`, `city_id*`, `editor*`, `reviewer` (left empty for the AI; the ready mode requires it), `scope*` ∈ `Tam teslim`|`Kısmi örnek`, `updated_on*`, `editorial_status*`, `notes`.
- **Şehir** (1 row): `city_id*`, `name*[100]`, `country*[100]`, `country_code*` (^[A-Z]{2,3}$), `region*` ∈ `EU,AS,AF,NA,SA,OC`, `kind*` ∈ `city,region,island,country`, `title*[160]`, `intro*[350]`, `currency*` (^[A-Z]{3}$), `currency_symbol`¹, `currency_label`¹, `language*`, `timezone*` (valid IANA), `latitude*`, `longitude*`, `coordinate_source_url*`, `coordinate_checked_on*`, `coordinate_note`, `source_url*`, `source_checked_on*`, `source_position*`(int≥0), `reviewed_on*`, `priority*`(int≥0), `aliases`, `locality`, `tagline`, `directory_order`, `forecast_url`¹, `provider_url`¹, `forecast_label`¹, `hero_photo_id` (must point to a `Kapak` photo row; required in ready mode), `editorial_notes`, `editorial_status*`. ¹ means the web contract requires the field even though the schema lists it as optional.
- **Konular**: `topic_id*`, `city_id*`, `slug*`, `title*[100]`, `description*[180]`, `icon*` (Berlin icons: book, home, bolt, transfer, heart, briefcase, family, train, bag, shield, plane, people), `order*`, `used_count` (formula).
- **Yanıtlar**: `entry_id*`, `city_id*`, `slug*[120]`, `title*[180]`, `subtitle[160]`, `summary*`, `keywords`, `stages` (id_list ⊆ before;planning;new;settled), `source_ids*`, `reviewed_on*`, `order*`, `featured*`(Evet/Hayır), `editorial_status*`, `topic_id*`, `steps*`(text_list), `documents`(text_list), `timing`, `cost`, `note`, `visual_json` (JSON object).
  - Berlin example of `visual_json`: `{"kind":"zones","title":"…","note":"Şematik…","items":[{"key":"A","title":"Merkez","text":"…"}]}`. Use it only for a real process or comparison.
- **Mekânlar**:
  - Common fields as in Yanıtlar, minus topic/steps.
  - `group*` ∈ `Müzeler`|`Sanat ve sergiler`|`Sahne ve müzik`|`Spor`|`Doğa ve açık hava`|`Çocuklarla keşif`|`Yeme ve içme`|`Tarih ve mimari`. These map to museum, art, stage, sport, nature, family, food and history.
  - `district*`, `setting*` ∈ `Kapalı alan`|`Açık hava`|`Karma`, `location*` (address), `latitude`/`longitude` (both or neither), `visit_status`, `note`, `collection*`(Evet/Hayır), `media_key`.
  - All 8 groups need at least one non-collection place.
- **Mahalleler**:
  - Common fields, plus `location*`, `tags` (text_list) and `compare_json`.
  - `compare_json` is a JSON object with ≥4 keys. All keys and values are non-empty strings: no nesting, numbers or nulls. Use the same headings across the city.
  - Example: `{"Ulaşım":"…","Yaşam ritmi":"…","Konut tipi":"…","Yeşil alan":"…"}`.
  - `note`, `media_key`.
- **Bağlantılar**: `action_id*`, `city_id*`, `entry_id*` (an existing answer/place/neighborhood), `label*` (a Turkish action label, e.g. Başvur / Randevu al / Bilet al / Haritada aç; a Wikipedia URL must not be labelled "Resmî"), `url*` (http(s), no credentials or session tokens), `checked_on*`, `order*`. Every answer, place and neighborhood needs ≥1 action.
- **Rotalar**:
  - `route_id*`, `city_id*`, `title*`, `tag*` (e.g. `Yarım gün · Kültür`).
  - `stops*` (text_list of names) and `stop_entry_ids` (id_list of 2–8 DISTINCT `Mekânlar.entry_id`, same count and order as `stops`).
  - `entry_id*` = the first stop.
  - `note*` (transport, time and ticket assumptions), `reviewed_on*`, `source_ids*`, `order*`, `editorial_status*`.
- **Sözlük**: `term_id*`, `city_id*`, `term*`, `definition*`, `source_ids*` (Berlin's are missing, so do not copy that gap), `reviewed_on*`, `order*`, `editorial_status*`.
- **Adımlar** (≥4 rows): `step_id*`, `city_id*`, `entry_id*` (must exist), `title*[120]`, `when*[90]`, `description*[250]`, `order*`.
- **Kaynaklar**:
  - `source_id*`, `city_id*`, `title*[180]`, `publisher*[120]`, `url*` (each canonical URL at most once), `checked_on*`, `topic`, `summary` (Turkish research note).
  - `verified*`: `Evet` only if this run fetched and read the page. The ready mode requires it.
  - `snapshot_file` and `snapshot_sha256`: if set, the file must exist in the package with a matching hash.
- **Fotoğraflar**: `photo_id*`, `city_id*`, `role*` ∈ `Mekân`|`Kapak`, `entry_id`, `file*`, `sha256*`, `caption*[250]`, `author*`, `license*`, `license_url*`, `source_url*`, `capture_date`, `source_checked_on*`, `modifications*`, `evidence_id*`, `completion_credit*` (Evet/Hayır), `order*`, `editorial_status*`, then S and T (formulas).
  - `entry_id` must be a place or neighborhood for `Mekân` and empty for `Kapak`. It must never point to an answer.
  - `file` is a relative path like `Fotoğraflar/eindhoven_slug_01.jpg`: no `/` at the start, no `..`, no symlink, a real JPEG/PNG/WEBP that decodes.
  - `sha256` is 64 lowercase hex characters computed from the delivered bytes.
  - `author` is a real person or organisation. `Own work` is rejected in new-content mode, and the uploader is not assumed to be the author.
  - `completion_credit`: `Evet` for a delivered real photo. It counts towards quantity and is not an approval.
- **Kanıtlar** (1:1 with photos):
  - `evidence_id*`, `city_id*`, `photo_id*` (back-link both ways).
  - `source_url*`, `source_title*`, `author*`, `license*`, `license_url*`: these MUST equal the photo row exactly (`source_url` by canonical identity).
  - `usage_terms*` (e.g. `Creative Commons Attribution-Share Alike 4.0`), `attribution`, `restrictions`, `checked_on*`.
  - `metadata_review_status*` ∈ `Bekliyor`|`Doğrulandı`, `pixel_review_status*` ∈ `Bekliyor`|`Doğrulandı`, and `rights_status*` ∈ `Bekliyor`|`Bu kare için uygun`. The normalised values are pending/verified/reviewed-clear-for-exact-frame. The AI writes `Bekliyor`.
  - `pixel_review_file` (if set, it must equal `photo.file`), `pixel_review_note` (what the AI actually saw), `rights_basis`.
  - `source_snapshot_file`/`_sha256` and `license_snapshot_file`/`_sha256`: the files exist and the hashes match. They are required in ready mode.
  - `source_evidence_json`: a JSON object. Its author, license, license_url and source_url must equal the columns. The recommended shape follows `provenance.extract`: `{"source_url","author","license","license_url","original_api_record":{url, extmetadata…},"delivered_file":{"url":…},"retrieved_on":"YYYY-MM-DD"}`. If it is longer than 32,767 characters, use UzunAlanlar.
- **SayfaAlanları**: `field_id*`, `city_id*`, `key*` (unique), `label*`, `value_type*` ∈ `Metin`|`Sayı`|`Mantıksal`|`JSON`, `value*`, `reviewed_on*`.
  - Reserved keys, which are errors here: routes, glossary, directory, currency, currency_symbol, currency_label, reviewed_on, weather.
  - Never copy Berlin `_db_*` or `expansion_version`.
  - Required Metin keys, each with city-specific Turkish text: hero_kicker, hero_accent, hero_note, topic_title, topic_intro, journey_title, journey_intro, neighborhood_title, neighborhood_intro, explore_title, explore_intro, sources_note, photo_credit, arrival_note.
  - Required link and slug keys:
    - `emergency_url` (Metin): a public https URL of an official local or national page.
    - `pharmacy_url` (Metin): the same kind of URL, for finding a pharmacy.
    - `advice_entry` (Metin): an existing entry **slug**, not `city:slug`.
  - Required JSON keys (arrays of objects; text fields must be non-empty):
    - `facts`: ≥4 × `{"value","label","entry"}`.
    - `quick_links`: ≥3 × `{"label","entry"}`. Its key is `entry`, NOT `url`.
    - `timeline`: ≥4 × `{"title","note","offset"}`. `offset` is a JSON integer in −730..730 and an optional `entry` must be a valid slug.
    - `budget_fields`: exactly the 10 keys income, rent, bills, food, transport, health, leisure, other, deposit and moving, each once with a Turkish label and no amounts.
    - `place_groups`: exactly the 8 keys museum, art, stage, sport, nature, family, food and history, each once.
    - `emergency`: ≥1 × `{"tel","number","label","desc"}`. `tel` must match `^\+?[0-9*#]{2,20}$` (no spaces); `number` is the display form (e.g. "116 117").
  - Every `entry` in facts, quick_links and timeline is a slug that exists in this city's answers, places or neighborhoods.
- **EkDetaylar**: `detail_id*`, `city_id*`, `entry_id*` (must exist), `key*`, `label*`, `value_type*`, `value*`. Each `(entry_id, key)` pair occurs once.
  - Forbidden keys: coordinates, visual, compare, tags, group, district, setting, collection, location, media_key, note, steps, documents, timing, cost, status, actions.
  - The sheet may stay empty.
- **FotoğrafKaynakları** (one row per photo_id, join by photo_id; there must be no orphan or missing rows):
  - `photo_id`.
  - `author_url`: a verified profile, otherwise empty with a note.
  - `attribution_url`: the profile, otherwise the File page. Required for new content.
  - `original_file_url`: the full-resolution URL at the source. Required for new content.
  - `downloaded_file_url`: the URL of the bytes actually fetched, for example an upload.wikimedia.org thumb. Required for new content.
  - `downloaded_on`: the real download date. Required for new content.
  - `original_file` + `original_sha256`: these must EQUAL `Fotoğraflar.file` and `.sha256`, so the delivered photo IS the preserved downloaded file.
  - `web_file` + `web_sha256` + `web_width` + `web_height`: required. If the original is a WebP of at most 1600 px, `web_file` = `original_file`. Otherwise the tool's `--web-copies` writes `Teslimler/WebKopyalari/<sha>.webp`.
  - `derivation` (the conversion log), `provenance_status` (the tool uses `Kayıttan doğrulandı` | `Eksik alan var`), `provenance_note`.
  - The `original_file` and `web_file` paths must exist and decode, and their hashes must match.

## 3. Licence rules (validation_media + audit)
- Allowed labels: `CC BY|BY-SA {1.0|2.0|2.5|3.0|4.0}[ xx]` (xx is a jurisdiction such as `de` or `nl`), `CC0`/`CC0 1.0`, `Public domain`/`Kamu malı`, `FAL`/`Özgür Sanat Lisansı`, `Unsplash License` (only with an unsplash grant object). NC, ND, paid and unknown licences are rejected, and so are AI or generated images.
- `license_url`:
  - It must be `https://creativecommons.org/licenses/{by|by-sa}/{ver}[/{xx}][/deed.xx]/` with no query. Use https, never http, and never protocol-relative `//`. A ported label (`CC BY-SA 3.0 nl`) requires the `/nl/` path.
  - CC0 uses `https://creativecommons.org/publicdomain/zero/1.0/`.
  - Public domain needs a non-empty valid URL that shows the PD basis, such as the Commons File page or PD-mark.
  - FAL must be on `artlibre.org`.
- `source_url` must not be one of the 381 URLs in `core/data/media_rights.json`'s `blocked_sources`.

## 4. Package layout
`<pkg>/CITY-039_eindhoven_v001.xlsx`, `Fotoğraflar/`, `Lisans kanıtları/` (source and licence snapshots with matching hashes; a single ZIP is allowed but must be extracted before checking), and `Teslimler/` (`TESLIM_OZETI.txt`, `ACIK_KONULAR.txt`, `ILERLEME_KAYDI.txt`, `dosya-envanteri.json`, the attribution CSV and HTML, and `paket-kontrol-v7.json` from the tool). In local trial mode, Drive link fields read `YEREL DENEME - Drive'a yüklenmedi`.

## 5. Conflicts and pitfalls (prompt vs. files vs. tool)
1. **Review statuses.** The audit expected the normalised value `verified`, but Excel must hold the TR labels (`Doğrulandı`/`Bekliyor`). `Tamam` is invalid.
   - Berlin sets metadata to `Doğrulandı` (a DB export).
   - Prompt §04 says the AI must not mark human approval, so the safe default for new content is all three set to `Bekliyor`.
   - Draft mode only warns about this.
2. **original_file location.** Prompt §13 says the original is preserved. The tool requires `original_file == Fotoğraflar.file`.
   - Do NOT point to a separate `Lisans kanıtları/orijinaller/...` path that is never delivered (qwen T01).
   - Downloading a ≤1600 px thumb is allowed (prompt §23). Record `downloaded_file_url` as the thumb URL and `original_file_url` as the full-resolution URL.
3. **Example ID patterns.** The prompt (`sehir:kaynak:`, `sehir:kanit:`) and Berlin (`src`, `evidence`) differ, and both are valid. `entry_id = city:slug` is strict.
4. **Package proof files.** The prompt shows proof files as PDF or TXT, while Berlin uses `.source-evidence.json` and `.license-record.json`. The tool only checks that the file exists and the hash matches. However, `state.json` is not a source copy (qwen).
5. **place_groups and budget labels.** The prompt labels (`Sanat`, `Sahne` …) differ from Berlin's (`Sanat ve sergiler` …). Only the keys are validated.
6. **Template version text.** Özet says "Sürüm 6.0" and the Web işlevleri sheet says "v6.0", while the prompt says v7. This is cosmetic and should not be edited.
7. **Missing page fields in Berlin.** Berlin lacks quick_links, arrival_note, emergency_url, pharmacy_url and advice_entry. Do not use Berlin's page-field set as complete.
8. **Optional vs. required.** `stages`, `stop_entry_ids` and `compare_json` are optional in the schema, but the web contract or prompt requires them. Treat them as required.
9. **Ready mode.** It errors on any non-`Onaylandı` editorial_status, an empty `reviewer`, `verified≠Evet` and non-final reviews, which is expected. The AI target is **draft = 0 errors** plus `--new-content` media audit = 0 errors.
