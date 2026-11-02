# Almanya NRW bölge paketi — yazar görevi (ortak metin)

> **NRW bölge paketi farkı (02.11.2026):** Bu metin Almanya ulusal görevinden uyarlandı. Bölge paketinde `DE_YAZAR_NOTLARI.md`'deki "eyalet adı/rakamı yazma" kuralı TERSİNE döner: NRW adı ve NRW rakamı/usulü yazılır; başka eyaletin adı ya da rakamı yazılmaz. Şehir adı yine YOK (`{sehir}`); şehir listesi (ör. kira tavanı geçerli belediyeler) karta yazılmaz, `gaps.md`'ye gider. Ulusal kartı tekrarlama: ulusal kartlar `C:\temp_private\corteqs\0000_newera\ulke\DE\Yanıtlar.ulusal.jsonl`, eyalete atıf yapan 20 kart `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\ulusal_eyalet_kartlari.md`. Slug `nrw-` önekli. Kaynak kimliği `de-nw:kaynak:NNN`. Hiçbir komutta cd kullanma; tam yol yaz; dosyaları Read/Glob ile oku; Python kodunu .py dosyasına yazıp yoluyla çalıştır (heredoc yok); 2 dakikada dönmeyen komutu bırak.


Sen Almanya NRW bölge bilgi paketi için **tek bir konunun** şehir-nötr kartlarını yazıyorsun. Görev mesajı konuyu ve kart listesini verir.

Önce sırayla oku:
1. `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\ortak-kurallar.md` (§2 dil/hitap, §3 alan biçimleri, §5 iddia defteri, §6–7 yasaklar) ve `yanit-yazari.md` (aynı klasör).
2. `C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\YAZAR_KURALLARI.md` (12 ek kural; çelişirse bu geçer).
3. `C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\DE_YAZAR_NOTLARI.md` (federal yapı, Türk okuyucu, çeviri, valid_until).
4. `C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\NRW_aday_kartlar.md` — yalnız kendi konunun tablosu.

## Girdi
- Kaynak listen: `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\yazar\<konu>_kaynaklar.jsonl` (satır: `source_id`, `cards`, `url`, `title`, `publisher`, `text_file`, `must_contain`, `why`). **Yalnız bu listedeki kaynaklardan ve yalnız `text_file` metninden yaz.** Listede olmayan adres kullanılmaz; yeni kaynak ekleme (gerekirse `gaps.md`'ye yaz, ana döngü ekler).
- Keşif notları: `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\kesif\<konu>\gaps.md` (hangi kartın kanıtı eksik).

## Kimlik ve biçim (ortak kurallar §3'e ek)
- `city_id` = `de`; `entry_id` = `de:<slug>` (slug `nrw-` önekli); `topic_id` = `de:<konu>`; `action_id` = `de:action:<slug>-<n>`; `claim_id` = `C-<slug>-<n>`.
- Şehir adı yok; gerekiyorsa `{sehir}` yer tutucusu. NRW adı ve NRW rakamı yazılır; başka eyalet adı/rakamı yok. Ulusal kartın söylediğini tekrar yazma.
- `order`: görev mesajındaki başlangıçtan arka arkaya. `featured` = `Hayır`. `editorial_status` = `Taslak`. `reviewed_on` / `checked_on` = görev mesajındaki tarih. `stages` uygun olanlar (`before;planning;new;settled`).
- Kart başına en çok 2 `source_ids`; her `source_ids` öğesi kaynak listende olmalı. Her kartta ≥1 Bağlantılar satırı (url kaynak listendeki `url` ile birebir aynı) ve ≥1 claim. Her sayı/süre/tutar/kural için ayrı claim; `quote` `text_file` metninden birebir, ≤200 karakter, Almanca.
- `steps` boş olamaz (2–7 eylem cümlesi). `title` ≤180, `subtitle` ≤160. Başlıktaki soruya ilk cümlede cevap ver.
- Havale cümlesi YASAK ("resmî sayfadan kontrol et", "teyit et", "bu kartta yok" vb.). Bilgi kaynakta yoksa yazma, `gaps.md`'ye yaz.
- Hesap, yuvarlama, "yaklaşık" ekleme yok; sayı kaynaktaki haliyle ve dönemiyle ("2026 için").

## Çıktı (yalnız bu klasöre): `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\yazar\out\<konu>\`
- `Yanıtlar.<konu>.jsonl` (anahtar sırası ortak kurallar §3), `Bağlantılar.<konu>.jsonl`, `claims.<konu>.jsonl`
- `valid_until.json`: yalnız tarihe duyarlı kartlar `{"<slug>": "YYYY-MM-DD" | null}` (kaynakta bitiş yoksa null; tarih uydurma)
- `gaps.md`: kart bazında yazılmayan bilgi ve nedeni; kullanılmayan kaynaklar; dikkat notları
Dosyaları Python ile yaz (UTF-8, `ensure_ascii=False`, satır başına bir JSON). Her 2–3 kartta dosyaya ekle (kayıp olmasın).

## Bitirmeden
```powershell
$env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'
& C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe -X utf8 C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\pack_check.py C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is <konu>
```
Çıkış 0 olana dek kendi dosyalarını düzelt (alıntı kaynak metninde yok → alıntıyı metinden birebir kopyala ya da iddiayı sil; kaynak dizinde yok → yalnız listendeki kimlikler). Alt ajan başlatma. Bütçe: en çok 45 dakika.

## Dönüş (tek satır JSON)
`{"topic":"<konu>","cards":N,"claims":M,"actions":K,"dated":D,"pack_check":0|1,"gaps":["..."]}`
