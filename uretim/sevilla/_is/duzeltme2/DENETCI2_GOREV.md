# Bağımsız iddia denetimi — Sevilla (CITY-107), ikinci düzeltme turu

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\iddia-denetcisi.md` (yalnız "Yöntem" bölümü geçerli; **çıktı adı ve biçimi bu dosyadaki gibidir**, oradaki eski çıktı bölümü geçersiz).

Kartları sen yazmadın, düzeltmeleri de sen yapmadın. Görevin: verilen kartların **bütün** satırlarını (örneklem değil) kaynak metniyle karşılaştırmak ve her kartta dört kart ölçütünü yargılamak. Okur: Sevilla'ya taşınan Türkçe konuşan kişi (çoğu Türk vatandaşı).

## Girdi (yalnız bunlar)
- `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\denetim\<parça>_kartlar.jsonl` (`<parça>` = `<konu>-d2`): kart alanları + `sources` (her kaynağın `text_file` temiz metni) + `claim_check_kalan` (script'in kart metnindeki sayıyı kaynakta birebir bulamadığı yerler; çoğu biçim farkı: "09:00" ↔ "9.00", "1 Mart" ↔ "1 de marzo"; her birine bak).
- İddia defteri: `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\claims\<konu>.jsonl` (yalnız senin kartlarının `entry_id`'li satırları).
- Editörün değişiklik kaydı: `...\_is\denetim\<konu>-d2_degisiklik.jsonl` (neyin değiştiğini görmek için; değişen cümlelere özellikle bak).
- **İnternete çıkma, WebFetch/WebSearch kullanma.** Yalnız verilen `text_file` metinlerini oku. Verilen metin yetmiyorsa sonuç `kaynak_yetersiz`. Kartları ve başka dosyaları DEĞİŞTİRME. Alt ajan başlatma.

## Odak 1: kural ve anlam
Sayılar script'le bakıldı; senin odağın **kural ve anlam**: kime uygulanır (Türk vatandaşı / AB vatandaşı / herkes), koşul, istisna, zorunlu/yasak/hak, yanlış genelleme (Endülüs ya da İspanya kuralını Sevilla'ya özgü gibi yazmak ya da tersi), anlamı ters çeviren çeviri, kaynakta olmayan çıkarım, eski dönem bilgisini güncel gibi sunma. Kart başına 2–4 iddia.

## Odak 2: dört kart ölçütü (her kartta)
- **K25**: ilk cümle başlıktaki soruyu doğrudan cevaplıyor mu?
- **K26** (işlem anlatan kartta): nereye (Sevilla'daki ofis ya da kanal, randevu yolu), ne getir (belge listesi), ne öder (tutar ya da "ücretsiz"), ne kadar sürer / son tarih (gün türüyle). Eksik öğe varsa adıyla yaz. Bilgi kartında `uygulanmaz`.
- **K31**: işi yapan yerel/yetkili kurum doğru ve güncel mi?
- **K40**: süre ve son tarih belirsiz değil mi?
Ölçütlerden biri kalırsa kartın `karar`'ı `düzelt`, `ozet`'te ölçüt ve eksik öğe adıyla (ör. "K26: belge listesi yok").

## Çıktı (`...\_is\denetim\` altında; UTF-8, satır başına bir JSON, Python ile yaz; her kartı bitirince ekle)
**Dosya adları yalnız `<konu>-d2_iddia.jsonl` ve `<konu>-d2_karar.jsonl`.** Tire'siz `<konu>_iddia.jsonl` / `<konu>_karar.jsonl` ilk turun kayıtlarıdır: onlara yazma.
1. `<parça>_iddia.jsonl`, iddia başına:
   `{"claim_id","entry_id","iddia","ülke_şehir_statü","dönem","resmî_URL","kaynak_bölümü","yayın_yürürlük_tarihleri","kontrol_tarihi":"2026-10-25","hesap_varsa_girdiler","sonuç","ağırlık","belirsizlik","alıntı","doğrusu"}`
   - `claim_id`: `D2-<slug>-<n>`
   - `sonuç` ∈ `doğru` | `yanlış` | `eksik_koşul` | `kaynak_yetersiz` | `çelişkili_kaynak`
   - `ağırlık` ∈ `ciddi` | `orta` | `hafif`; `doğru`da `-`
   - `alıntı`: kaynaktan birebir (≤200 karakter); `doğrusu`: doğru olmayanda karta konabilecek Türkçe öneri ("sen" hitabıyla).
2. `<parça>_karar.jsonl`, kart başına: `{"entry_id","karar","en_agir","ozet","K25","K26","K31","K40"}`; `karar` ∈ `temiz` | `düzelt`; `en_agir` ∈ `ciddi` | `orta` | `hafif` | `-`; ölçüt alanları ∈ `geçti` | `kaldı` | `uygulanmaz`.
   Her kartın bir karar satırı olmalı.

## Bütçe
45 dakika. Dolarsa bitirdiğin kartlarla dön, kalanları `gaps`'e yaz.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"parts":{"<parça>":{"cards":N,"claims":M,"dogru":a,"duzelt_kart":b,"ciddi":c,"orta":d,"hafif":e,"olcut_kalan":{"K25":x,"K26":y,"K31":z,"K40":w}}},"gaps":[]}`
