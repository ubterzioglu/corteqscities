# Son tam denetim (d5) — editör görevi, Marbella (CITY-080)

Kayıtları sen yazmadın, denetimi de sen yapmadın. Görev mesajı sana parça(lar)ı (`<p>`) verir.

## Oku (bu sırayla)
- `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md`, `...\editor.md` (mekân/mahalle/sözlük/rota için `...\yer-yazari.md` de; mekân ve rotada `...\mekan-yazari.md` de). Açık görevler: 1, 2, 6, 7 (editor.md numaraları). Kayıt ekleme/silme YOK (kapanmış görünen mekânı silme, `open`'a yaz). `slug`/`entry_id`/`term_id`/`route_id` değişmez.
- W = `C:\temp_private\corteqs\0000_newera\uretim\marbella\_is`; `<TK>`=`C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts`; `<PY>`=`C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`; `<tarih>`=2026-11-02; `<bbox>`=36.40,36.62,-5.18,-4.62; `<TMP>` görev mesajında. Hitap: sen (okura 2. tekil; "siz" yok).

## Girdi
- Bulgular: `W\denetim\<p>-d5_iddia.jsonl` (doğru olmayan satırlar), `W\denetim\<p>-d5_karar.jsonl` (kayıt kararları; "düzelt" olanlar), mekân/mahallede `W\denetim\<p>-d5_mekan-dogrulama.jsonl` ("kaldı" satırları: tutmayan öğe de bulgudur; `bulgu_claim_id` = `mekan-dogrulama:<slug>`).
- Çürütme turu bu şehirde yalnız ciddi bulguda yapılır; bu turda ciddi bulgu yok. Her bulguyu kaynakla KENDİN doğrula; kaynak bulguyu desteklemiyorsa uygulama, reddedildi diye kaydet (yeni = "", gerekçe ve kaynaktan alıntıyla).
- Kaynak metinleri: `W\kaynak_dizini.jsonl` → `text_file` (Read).

## Kurallar
- Açık-mı notları: bazı mekân notlarındaki "28.10.2026 itibarıyla …" / "28 Ekim 2026 itibarıyla …" cümlesi ZORUNLUDUR (açık-mı kapısı bu biçimi arar). İçeriği kaynağa göre düzelt ama cümleyi silme ve "<tarih> itibarıyla" başlangıcını koru. Kaynak bugünkü durumu söylemiyorsa kaynağın tarihini yaz ("… Haziran 2026 tarihli belediye haberine göre …") ve kaynakta olmayan durum iddiasını çıkar.
- Koordinatı kaynaksız mekân (bulgu "kaynaksız koordinat"): koordinat yalnız Wikidata'dan ya da resmî adres kaydından (CartoCiudad) gelir; uydurma. Mekânın QID'i `W\mekan\selected.jsonl` ya da `W\mekan\plan_m*.jsonl`'de varsa ve Wikidata koordinatı kayıttakiyle aynıysa, Wikidata öğesini kaynak olarak ekleyebilirsin (aşağıdaki kaynak kuralıyla). Boş koordinatı doldurmak için kaynak yoksa boş bırak.
- K26 / eksik bilgi (saat, ücret, rezervasyon) kaynakta varsa ekle; yoksa uydurma, kaynağın dediğine daralt ("doğrulanamadı" notu yazma; ortak kurallar §7). Okura iş bırakan cümleyi ("ara öğren", "danış") sil ya da bilgiyle değiştir.
- Ücret, saat ve işlem kuralı turizm portalından değil mekânın/kurumun kendi resmî sayfasından.
- Kayıt başına en çok 2 `source_ids`: fazlası varsa iddiası olmayan ya da zayıf kaynağı çıkar (defterde o kaynağa dayanan satır kalmasın). Yeni resmî kaynak, aynı kaydın zayıf kaynağının YERİNE geçer ("değiştir-boşalt"). Kaynağı ancak `add_sources` ile ekle (klasör `snap_<p>-editor<sira>`, sıra için önce Test-Path; `-X utf8`, `-I` KULLANMA). Parça başına en çok 3 yeni kaynak (şu an 402/500).
- Aynı konuyu tekrar eden kayıtlar (K27/K28): ayırt eden somut farkı yaz ya da tekrar eden cümleyi tek kayda indir.
- Hitap, iç süreç notu, iş bırakan cümle yok. `visit_status` ""; `editorial_status` "Taslak".
- Değişiklik kaydı: `W\denetim\<p>-d5_degisiklik.jsonl` (editor.md biçimi: `entry_id, alan, eski, yeni, bulgu_claim_id, gerekce, alinti`; her "doğru" olmayan bulgunun ve her "kaldı" satırının en az bir satırı; alinti zorunlu).
- Defter (`W\claims\<p>.jsonl`): her yeni/değişen sayı ve kural için birebir alıntılı satır; çıkardığın bilginin satırını sil.
- Dosyaları aynı biçimde baştan yaz (aynı anahtar sırası, satır başına bir JSON, UTF-8; Python ile; önce yedeği `<TMP>`'ye).

## Bitirmeden
`& '<PY>' -X utf8 '<TK>\merge_package.py' 'W' --city-id marbella --bbox=36.40,36.62,-5.18,-4.62 --data-out '<TMP>\birlesik' --out '<TMP>\birlestir_rapor.json'` (W yerine tam yol; `--data-out`, `--out` ŞART; `-I` yok). Kendi parçanı ilgilendiren bulgu 0.

## Dosyalar (parçaya göre)
- Mekân (m1–m3): `W\data\parcalar\Mekânlar.<p>.jsonl`, `Bağlantılar.<p>.jsonl`, `W\claims\<p>.jsonl`. Mahalle: `Mahalleler.mahalle.jsonl`, `Bağlantılar.mahalle.jsonl`, `W\claims\mahalle.jsonl`. Sözlük: `Sözlük.sozluk.jsonl`, `W\claims\sozluk.jsonl`. Rota: `Rotalar.rota.jsonl`, `W\claims\rota.jsonl` (+ `W\rota_plan.jsonl`, `W\rota_mesafe.jsonl` değişirse). Yanıt konuları: `Yanıtlar.<p>.jsonl`, `Bağlantılar.<p>.jsonl`, `W\claims\<p>.jsonl`.
- Başka parçanın dosyasına yazma.

## Sınırlar
Komut: cd yok, Bash yok; PowerShell tek komut, tam yol; Python için önce `.py`'yi `<TMP>`'ye yaz, `& '<PY>' -X utf8 '<dosya>'`; `python -c`/heredoc yok. Alt ajan başlatma. Bütçe: parça başına ~35 dakika; her 5 kayıtta bir ara dosyaları yaz.

## Dönüş (tek satır JSON)
`{"parcalar":{"<p>":{"bulgu_toplam":N,"uygulanan":a,"reddedilen":b,"degisen_kayit":c,"yeni_kaynak":d,"script_kontrol_hata":e,"open":["kısa not"]}}}`
