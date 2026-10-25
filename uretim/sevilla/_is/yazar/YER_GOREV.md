# Yer ve sayfa yazarı görevi — Sevilla (CITY-107)

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\yer-yazari.md` (yalnız görevine ait bölümler). Alanlar: `...\references\contract_digest.md` §2.

## Değerler
- `<city_id>` = `sevilla`; Sevilla, İspanya (Endülüs, Sevilla ili); Wikidata `Q8717`; yerel dil `es`; saat dilimi `Europe/Madrid`; para birimi `EUR`
- `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`; `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`** ("siz" yok)
- Mevcut kaynaklar: `<WORK>\_is\kaynak_dizini.jsonl` (`text_file`). Yeni kaynak: ortak kurallar §4 (`add_sources`, klasör `snap_<gorev>-yazar<sira>`), yalnız resmî yayıncının derin sayfası.
- Erişilemez (deneme): sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es; femas.es KULLANMA (belediye sunucusunun festival alan adı — yan kapı).
- Kaynak bütçesi: kayıt başına ≤2 `source_ids`; bağlantı ≤2.
- Mevcut slug'lar: `<WORK>\_is\data\Yanıtlar.jsonl` (başlık ve slug çakışmasın).

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>`'de. Bitirmeden ortak kurallar §8 `merge_package` kontrolü (çıktılar `<TMP>`'ye): kendi parçanda bulgu 0. Dönüş: `yer-yazari.md`'deki tek satır JSON.
