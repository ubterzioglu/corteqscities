# Son tam denetim (d5) — editör görevi, Málaga (CITY-075)

Kayıtları sen yazmadın, denetimi de sen yapmadın. Görev mesajı sana parça(lar)ı (`<p>`) verir.

## Oku (bu sırayla)
- `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, `...\editor.md` (mekân/mahalle/sözlük/rota için `...\yer-yazari.md` de). Açık görevler: 1, 2, 6, 7 (editor.md numaraları). Kayıt ekleme/silme YOK (kapanmış görünen mekânı silme, open'a yaz). `slug`/`entry_id`/`term_id`/`route_id` değişmez.
- W = `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is`; `<TK>`=`C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>`=`C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`; `<tarih>`=2026-10-30; `<bbox>`=36.57,36.87,-4.60,-4.28; `<TMP>` görev mesajında. Hitap: sen (okura 2. tekil; "siz" yok).

## Girdi
- Bulgular: `W\denetim\<p>-d5_iddia.jsonl` (doğru olmayan satırlar), `W\denetim\<p>-d5_karar.jsonl` (kayıt kararları; "düzelt" olanlar), mekân/mahallede `W\denetim\<p>-d5_mekan-dogrulama.jsonl` ("kaldı" satırları: tutmayan öğe de bulgudur; `bulgu_claim_id` = `mekan-dogrulama:<slug>`).
- Çürütme: `W\denetim\<p>-d5_teyit.jsonl` (varsa). `yersiz` bulguyu UYGULAMA — reddedildi diye kaydet (yeni = "", gerekçe ve teyitteki alıntıyla). `kismen` bulguda teyitteki `dogrusu`'na göre uygula. `gercek` bulguyu kaynakla KENDİN doğrula, uygula.
- Notlar: `W\denetim\D5_NOTLARI.md` yoksa `W\d5_notlari.md` (`W\d5_notlari.md`'de bu parçaya ait satırlar görevdir; örn. NIE/TIE harçları kaynak 004'ten, Libro de familia 30.4.2021 kuralı, okul başvuru dönemi atıflı dil, kart çiftleri).
- Kaynak metinleri: `W\kaynak_dizini.jsonl` → `text_file`.

## Kurallar
- K26 eksiği (nereye/ne getir/ne öder/ne kadar sürer) kaynakta varsa karta ekle; kaynakta yoksa uydurma, bilgiyi çıkar ya da kaynağın dediğine daralt ("doğrulanamadı" notu yazma; ortak kurallar §7).
- Kart başına en çok 2 `source_ids`: yeni resmî kaynak, aynı kartın zayıf (turizm portalı) kaynağının YERİNE geçer ("değiştir-boşalt"); kaynağı ancak `add_sources` ile ekle (klasör `snap_<p>-editor<sira>`, önce Test-Path; `-X utf8`, `-I` KULLANMA). Kaynaklar sayfası 500 sınırında: parça başına en çok 2 yeni kaynak (şu an ≈433).
- Aynı konuyu tekrar eden kart çifti (K27/K28): ikisini ayırt eden somut farkı (kim/nerede/hangi işlem) yaz ya da tekrar eden cümleleri tek yere indir; slug başka sekmede kullanılıyorsa silme.
- Hitap, iç süreç notu, iş bırakan cümle yok. `visit_status` ""; `editorial_status` "Taslak".
- Değişiklik kaydı: `W\denetim\<p>-d5_degisiklik.jsonl` (editor.md biçimi; her "doğru" olmayan bulgunun en az bir satırı; alinti zorunlu).
- Defter (`W\claims\<p>.jsonl`): her yeni/değişen sayı ve kural için birebir alıntılı satır; çıkardığın bilginin satırını sil.
- Dosyaları aynı biçimde baştan yaz (aynı anahtar sırası, satır başına bir JSON, UTF-8; Python ile; yedek `<TMP>`'ye).

## Bitirmeden
`& '<PY>' -X utf8 '<TK>\merge_package.py' 'W' --city-id malaga --bbox=36.57,36.87,-4.60,-4.28 --data-out '<TMP>\birlesik' --out '<TMP>\birlestir_rapor.json'` (W yerine tam yol; `--data-out`, `--out` ŞART; `-I` yok). Kendi parçanı ilgilendiren bulgu 0.

## Dosyalar (parçaya göre)
- Yanıt konuları: `W\data\parcalar\Yanıtlar.<p>.jsonl`, `Bağlantılar.<p>.jsonl`, `W\claims\<p>.jsonl` (planlama: `Adımlar.planlama.jsonl` de).
- Mekân (m1–m5): `Mekânlar.<p>.jsonl`, `Bağlantılar.<p>.jsonl`, `W\claims\<p>.jsonl`. Mahalle: `Mahalleler.mahalle.jsonl`. Sözlük: `Sözlük.sozluk.jsonl`. Rota: `Rotalar.rota.jsonl` (+ `W\rota_plan.jsonl`, `W\rota_mesafe.jsonl` değişirse).

## Sınırlar
Komut: cd yok, Bash yok; PowerShell tek komut, tam yol; Python için önce `.py`'yi `<TMP>`'ye yaz, `& '<PY>' -X utf8 '<dosya>'`; `python -c`/heredoc yok. Alt ajan başlatma. Bütçe: parça başına ~35 dakika.

## Dönüş (tek satır JSON)
`{"parcalar":{"<p>":{"bulgu_toplam":N,"uygulanan":a,"reddedilen":b,"degisen_kayit":c,"yeni_kaynak":d,"script_kontrol_hata":e,"open":["kısa not"]}}}`
