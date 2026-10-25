# Editör görevi — Sevilla (CITY-107), tamamlama turu

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, sonra `...\agents\editor.md`. Kayıtları sen yazmadın, denetimi de sen yapmadın.

## Değerler
- `<city_id>` = `sevilla`; `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`
- `<TK>` = `C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>` = `C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
- `<tarih>` = `2026-10-25`; `<bbox>` = `37.30,37.45,-6.03,-5.89`; **hitap: `sen`**
- Tur: **tamamlama turu, açık görevler 1, 2, 3, 4, 5, 6, 7.**

## Her konu (`<konu>`) için
- Düzenlenecek dosyalar (yalnız bunlar): `<WORK>\_is\data\parcalar\Yanıtlar.<konu>.jsonl`, `Bağlantılar.<konu>.jsonl`, `<WORK>\_is\claims\<konu>.jsonl` (planlama'da ayrıca `Adımlar.planlama.jsonl`).
- Bulgular: `<WORK>\_is\denetim\<konu>_iddia.jsonl` ve `<konu>_karar.jsonl`.
- Değişiklik kaydı: `<WORK>\_is\denetim\<konu>_degisiklik.jsonl`.
- Kaynak metinleri: `<WORK>\_is\kaynak_dizini.jsonl` → `text_file`.

## ÜLKE PAKETİ KARTLARI
Dosyalarda `order` 9000–9104 olan satırlar ülke/Endülüs paketinden gelir ve ayrıca denetlenmiştir. **Bunlara dokunma** (silme, değiştirme) — tek istisna: denetim bulgusu doğrudan o karta aitse (`sevilla:yillik-izin-ve-resmi-tatiller-2026`, `sevilla:altin-vize-sona-erdi`). Görev 3 (kural gözden geçirmesi) ve 5 (değer) yalnız Sevilla kartlarında (`order` < 9000).

## Görev 4–5 (tamamlama)
- Konunun toplam kart sayısı (ülke + Sevilla) **18–26** aralığında kalsın; yeni kart `order`'ı görev mesajındaki aralıkta.
- `new_sources` (görev mesajında): bu kaynaklarla eksik bilgiyi var olan karta ekle ya da yeni kart yaz. Ayrıca `<WORK>\_is\yazar\ilk5.json`'daki cevapsız sorular (görev mesajında) kaynakla kapatılabiliyorsa kapat.
- Konunun başka kartıyla aynı işi anlatan tekrar kart varsa (görev mesajı söyler) birini Bağlantılar ve defter satırlarıyla birlikte sil (görev 5), kalanı tamamla.
- Kaynak yoksa yazma; "doğrulayın/siteye bakın" dolgusu yasak.
- Yeni kaynak gerekirse ortak kurallar §4 (`snap_<konu>-editor<sira>`), konu başına en çok 3. Erişilemez alan adları: sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es (kullanma).
- Kart başına ≤2 `source_ids`, ≤2 Bağlantılar satırı.

## Bitirmeden
`merge_package` kontrolü (ortak kurallar §8, çıktılar `<TMP>`'ye): kendi parçanı ilgilendiren bulgu 0. Hitap: kendi değiştirdiğin metinde "siz" biçimi yok.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız `<TMP>`'de. Bütçe 40 dakika.

## Dönüş
Konu başına `editor.md`'deki tek satır JSON; hepsi tek bir JSON nesnesinde: `{"<konu>": {...}, ...}`
