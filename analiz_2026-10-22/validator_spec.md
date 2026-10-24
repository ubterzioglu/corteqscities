# Local validator spec (mirrors Atınç's v7 checker, plus audit-derived extras)

The official toolkit exists at `C:\temp_private\corteqs\0000_newera\araclar\arac\`. Its entry point is `check_delivery.py <xlsx> <pkg> --new-content [--web-copies]`, which writes `Teslimler/paket-kontrol-v7.json`.

For a read-only run, use `araclar\kontrol_salt_okunur.py <xlsx> <pkg>`. It tolerates duplicate list items and prints summary counts and error classes only.

Prerequisites:
- Python 3.11+ with `Pillow>=11,<13` and `openpyxl>=3.1,<4`. **Pillow is currently NOT installed on this machine**, so the run fails with ImportError.
- Run it with `python -X utf8`.

How the skill should use it:
- Run the OFFICIAL tool first.
- Add a thin local pre-check (below) for fast failures and for the audit-derived checks the tool lacks.
- Summarise the tool output by error class (`Sheet!row: message` → group by message) instead of reading the JSON dumps. That keeps tokens low.

Severity:
- **E**: error in draft mode, so it blocks delivery.
- **W**: warning in draft mode and error in ready mode.
- **X**: extra check the official tool does not have (from the Codex audit). Treat X as a blocking error for AI delivery unless noted.

## A. Reader / structure (read_delivery_v7)
1. E: All 16 main sheets plus FotoğrafKaynakları are present. Row-7 keys equal the schema order exactly, and no extra header cells are filled.
2. E: No formula in any non-readonly data cell. Readonly cells: Konular.H, Fotoğraflar.S and T, and all of Özet.
3. E: Every id_list or text_list cell parses with no duplicate items (`;` for id_list, newline for text_list). Example of a failure: a source_ids cell that repeats an ID.
4. E: Each value parses to its type: date as `YYYY-MM-DD` or an Excel date; integer or number as a finite real number; boolean as `Evet`/`Hayır`; object as a JSON dict.
5. E: Any UzunAlanlar chunks are complete (index 0..n), consistent, and SHA-matched.
6. X: The workbook opens in openpyxl and keeps the template's data validations. Compare the DV count and sqref with the template.

## B. Field rules (validation_fields)
7. E: Each required field is non-empty. See the digest for the `*` list.
8. E: Each enum or choice value is in the allowed list. Excel holds the TR labels; the tool maps them through choice_map.
9. E: Dates are valid and not later than today.
10. E: Numbers fall within min/max: lat ±90, lon ±180, integers ≥0 where defined.
11. E: URL fields use the http(s) scheme, have a host, and contain no userinfo.
12. E: String lengths stay within max_length (title, intro, slug, caption, description, when, publisher, …).
13. E: Every `*_id` value matches `^[a-z0-9][a-z0-9:_-]*$`. That rules out uppercase, Turkish characters and spaces.
14. E: Every `*sha256` value is 64 lowercase hex characters.
15. E: Primary keys are unique per table (the first column).
16. E: Teslimat and Şehir have exactly 1 row each. `schema_version` is "1.0".
17. E: Şehir.timezone is a valid IANA zone. `country_code` matches ^[A-Z]{2,3}$ and `currency` matches ^[A-Z]{3}$. Latitude and longitude are both set or both empty.
18. W: The ready-only checks are expected to fail for AI output and do not block it: scope = `Tam teslim`, `reviewer` is set, and every `editorial_status` = `Onaylandı`.

## C. Graph (validation_graph)
19. E: `city_id` on every row equals Şehir.city_id.
20. E: Every `source_ids` item exists in Kaynaklar.
21. E: An entry_id is unique across answers, places and neighborhoods together, and `entry_id == city_id + ":" + slug`.
22. E: No two titles repeat, compared case-insensitively, across answers, places and neighborhoods.
23. E: Each answer's `topic_id` exists. Each `topic_id == city_id:slug`.
24. E: `order` is unique within Adımlar, Rotalar, Sözlük and Konular.
25. E: Each canonical URL appears in Kaynaklar only once. W in ready mode: `verified` must be Evet.
26. E: If Kaynaklar.snapshot_file is set, the file exists inside the package, is not a symlink, and its SHA matches.
27. E: In actions, routes, journey_steps and entry_details, `entry_id` exists. Each route stop ID exists.
28. E: Each EkDetaylar (entry_id, key) pair is unique. Each SayfaAlanları/EkDetaylar value decodes as its value_type.
29. E: No SayfaAlanları key is reserved (routes, glossary, directory, currency*, reviewed_on, weather), and no SayfaAlanları key is duplicated. No EkDetaylar key is an owned key.
30. W: Every answer, place and neighborhood has at least one Bağlantılar row.
31. W: Every non-collection place and every neighborhood has at least one Mekân photo with `completion_credit=Evet`.

## D. Media (validation_media + delivery_tools.audit --new-content)
32. E: Photo `file` is a safe relative path. The file exists, is a real JPEG/PNG/WEBP, decodes, and has SHA-256 equal to `sha256`.
33. E: For a `Mekân` photo, `entry_id` points to a place or neighborhood, never to an answer. For a `Kapak` photo, `entry_id` is empty.
34. E: Each (role, entry_id, order) combination is unique.
35. E: The evidence row exists and links back both ways, by photo_id and by evidence_id.
36. E: author, license and license_url are equal between photo and evidence, and source_url matches by canonical identity. The same holds inside source_evidence_json.
37. E: The license label is allowed, and the label and URL agree:
    - a CC label needs the https creativecommons.org path, including the jurisdiction;
    - CC0 needs the official zero/1.0 URL;
    - a Public domain row needs a valid URL;
    - FAL needs artlibre.org;
    - Unsplash needs the grant object.
    - NC, ND, unknown and generated images are rejected.
38. E: source_url is not in `media_rights.json` blocked_sources (381 URLs).
39. E: The evidence snapshot files, when set, exist and their hashes match (required in ready mode). If `pixel_review_file` is set, it equals `photo.file`.
40. E: If Şehir.hero_photo_id is set, it points to a `Kapak` row. W in ready mode: hero_photo_id is required.
41. E: FotoğrafKaynakları has one row per photo_id, with no missing, duplicate or orphan rows.
42. E: The four provenance link fields are valid URLs when present. For new content, original_file_url, downloaded_file_url, downloaded_on and attribution_url are required.
43. E: author is not the literal `Own work`.
44. E: original_file and web_file are both present, exist, decode, and match their SHA. `original_file == photo.file` and `original_sha256 == photo.sha256`.
45. W: All three review statuses ≠ final. This is expected; the AI leaves them at `Bekliyor`.
46. W: Derivatives of one source page earn no extra completion credit.
47. Counts: distinct photo groups are formed by union-find over SHA OR canonical source page, separately per role.

## E. Web contract (web_contract)
48. W: All 14 Metin page keys are non-empty.
49. W: emergency_url and pharmacy_url are public https links (the host contains a dot).
50. W/E:
    - facts needs ≥4 objects with value, label and entry (W). quick_links needs ≥3 with label and entry. timeline needs ≥4 with title, note and offset.
    - budget_fields must hold exactly the 10 keys and place_groups exactly the 8 keys, each once.
    - emergency needs ≥1 object with tel, number, label and desc.
    - A missing object field or an empty text field is an error (E).
51. W: Every entry in facts, quick_links, timeline and advice_entry is an existing slug.
52. E: timeline.offset is a JSON integer in −730..730.
53. E: emergency.tel matches `^\+?[0-9*#]{2,20}$`.
54. W: Every route has 2–8 distinct stop IDs, `len(stops) == len(stop_entry_ids)`, every stop is in places, and `entry_id` = the first stop.
55. W: compare_json has ≥4 keys. E: every compare_json key and value is a non-empty string.
56. W: There are at least 4 journey steps. Every place group key has at least one non-collection place.
57. W: Şehir currency_symbol, currency_label and forecast_label are non-empty. forecast_url and provider_url are public links.

## F. Counts (check_minimum)
58. W: answers ≥212, places ≥92, neighborhoods ≥12, used topics ≥12, distinct venue photos ≥187, distinct heroes ≥6, routes ≥9, glossary ≥48. The skill also reports the gap to target (240/120/16/12/250/8/12/60).

## G. Extras from the Eindhoven audit (not in the official tool) — X
59. X placeholders: no cell contains `?` inside an address or postcode, `[[`, `]]`, `TODO`, `TBD`, `bilinmiyor`, `null`, `None`, `N/A`, `lorem`, `örnek` or `YEREL_NUMARA`. Also flag `RESMI-KURUM` and the template example strings copied verbatim.
60. X provenance: no Fotoğraflar or FotoğrafKaynakları path points outside `Fotoğraflar/` or `Teslimler/WebKopyalari/`. No Kanıtlar snapshot is `state.json`; the snapshot file must contain the source page or API record.
61. X Wikipedia: a Bağlantılar label containing "Resmî" may not point to *.wikipedia.org. Report the share of Wikipedia URLs among Kaynaklar (warn if above 10%) and among place source_ids (warn if a place's only source is Wikipedia).
62. X place mix: report the share of each place group, and warn if any group exceeds 35% or is below 3 rows (Eindhoven had 57% history). Count food rows whose location is a street or axis rather than a single business.
63. X routes geography: when stop coordinates exist, flag consecutive stops more than 3 km apart for walking routes and any route spanning more than 2 districts without a transfer note.
64. X geo-consistency: place.district must be consistent with its coordinates (point-in-district, or the nearest district centroid within a threshold). Flag photo EXIF/Commons GPS more than 1.5 km from the place's coordinates, and GPS outside the city's bounding box (the Seattle case). Flag postcode prefixes inconsistent with the district.
65. X photo semantics: check the Commons categories and description of the source file and warn on these keywords:
    - non-photo: painting, drawing, engraving, map, plan, poster, logo, coat of arms, `PD-Art`
    - archive: a year more than 20 years before today in the title or date, so the caption must carry the date
    - wrong place: a different municipality in the title or categories, such as `Zweeloo`
    - object or detail: interior, organ, grave, plaque, bottle
    - Also list near-duplicates with dHash Hamming ≤6 within one gallery.
66. X image size: report a short side under 600 px and an aspect ratio above 2.5 (panorama).
67. X evidence chain: report any Kaynaklar row with verified=Evet but no recorded fetch (cache entry or snapshot) during the run. Report any Bağlantılar URL whose last HTTP check was 404.
68. X consistency: the same fact (fee, percentage, date) is not stated with different values across answers, glossary and page fields. Example: KVK €80 in two cards.
69. X Teslimler: TESLIM_OZETI counts equal the recomputed counts. dosya-envanteri.json lists every file with its real size and SHA, and the size total matches (the "~0 MB" error). ACIK_KONULAR is non-empty or uses the mandated sentence.
70. X high-risk claims: for answers tagged legal, benefits, tax, health, education or housing, require ≥1 source on an official domain (gov, overheid, the city's own domain, or the agency list per country) and a `reviewed_on` from this run. Output a list of claim cells with numbers or percentages for targeted primary-source re-verification (B01–B18 class).

The output format should keep tokens low: one JSON summary per run, `{counts, gaps, errors_by_class: {msg: n, examples: [3 locations]}, warnings_by_class, extras_by_class}`, capped at about 3 examples per class.
