# Bağımsız iddia denetimi — Sevilla (CITY-107)

Önce oku: `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\iddia-denetcisi.md` (yalnız "Yöntem" bölümü geçerli; **çıktı adı ve biçimi bu dosyadaki gibidir**, oradaki eski çıktı bölümü geçersiz).

Kartları sen yazmadın. Görevin: verilen kartların **bütün** satırlarını (örneklem değil) kaynak metniyle karşılaştırmak. Okur: Sevilla'ya taşınan Türkçe konuşan kişi (çoğu Türk vatandaşı).

## Girdi (yalnız bunlar)
- `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\denetim\<konu>_kartlar.jsonl`: kart alanları + `sources` (her kaynağın `text_file` temiz metni) + `claim_check_kalan` (script'in kart metnindeki sayıyı kaynakta birebir bulamadığı yerler; çoğu biçim farkı: "09:00" ↔ "9.00", "1 Mart" ↔ "1 de marzo"; her birine bak).
- İddia defteri (yazarın alıntıları): `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\claims\<konu>.jsonl` (yalnız senin kartlarının `entry_id`'li satırları).
- **İnternete çıkma, WebFetch/WebSearch kullanma.** Yalnız verilen `text_file` metinlerini oku. Verilen metin yetmiyorsa sonuç `kaynak_yetersiz`. Kartları ve başka dosyaları DEĞİŞTİRME. Alt ajan başlatma.

## Odak
Sayılar script'le bakıldı; senin odağın **kural ve anlam**: kime uygulanır (Türk vatandaşı / AB vatandaşı / herkes), koşul, istisna, zorunlu/yasak/hak, yanlış genelleme (Endülüs ya da İspanya kuralını Sevilla şehrine özgü gibi yazmak ya da tersi; il geneli kurumu şehir için yetkili gibi yazmak), anlamı ters çeviren çeviri, kaynakta olmayan çıkarım, eski dönem bilgisini güncel gibi sunma. Kart başına 2–4 iddia.

## Çıktı (her konu için iki dosya, `...\_is\denetim\` altında; UTF-8, satır başına bir JSON, Python ile yaz)
1. `<konu>_iddia.jsonl`, iddia başına:
   `{"claim_id","entry_id","iddia","ülke_şehir_statü","dönem","resmî_URL","kaynak_bölümü","yayın_yürürlük_tarihleri","kontrol_tarihi":"2026-10-25","hesap_varsa_girdiler","sonuç","ağırlık","belirsizlik","alıntı","doğrusu"}`
   - `claim_id`: `D-<slug>-<n>`
   - `sonuç` ∈ `doğru` | `yanlış` | `eksik_koşul` | `kaynak_yetersiz` | `çelişkili_kaynak`
   - `ağırlık` ∈ `ciddi` | `orta` | `hafif`; `doğru`da `-`
   - `alıntı`: kaynaktan birebir (≤200 karakter); `doğrusu`: doğru olmayanda karta konabilecek Türkçe öneri ("sen" hitabıyla).
2. `<konu>_karar.jsonl`, kart başına: `{"entry_id","karar","en_agir","ozet"}`; `karar` ∈ `temiz` | `düzelt`; `en_agir` ∈ `ciddi` | `orta` | `hafif` | `-`.
   Her kartın bir karar satırı olmalı.

## Bütçe
40 dakika. Dolarsa bitirdiğin kartlarla dön, kalanları `gaps`'e yaz.

## Dönüş (tek satır JSON; sayıları dosyadan say)
`{"parts":{"<konu>":{"cards":N,"claims":M,"dogru":a,"duzelt_kart":b,"ciddi":c,"orta":d,"hafif":e}},"gaps":[]}`
