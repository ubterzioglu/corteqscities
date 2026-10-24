# Bağımsız iddia denetçisi görev dosyası (Bakersfield · CITY-901 · kontrol tarihi 2026-10-23)

Önce `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\iddia-denetcisi.md`'yi oku: "Yöntem" bölümü geçerli. O dosyadaki **"Girdi", "Çıktı" ve "Dönüş" bölümleri GEÇERSİZ**; çıktı adı ve biçimi bu dosyadaki gibidir.

## Sınırlar
- Kartları sen yazmadın, yazarın gerekçesini (iddia defterini) görmüyorsun. Kart dosyasını DEĞİŞTİRME.
- **Yalnız verilen dosyaları oku; internete çıkma (WebSearch/WebFetch YOK).** Verilen kaynak metni bir iddiayı karşılamıyorsa sonuç `kaynak_yetersiz`.
- Sayılar araçla zaten tek tek kontrol edildi; senin odağın **kural ve anlam**: kime uygulanır (ABD vatandaşı / green card sahibi / vize sahibi / statüsüz; California / Kern / Bakersfield / federal), koşul, istisna, zorunlu/yasak/hak, yanlış genelleme, anlamı ters çeviren ya da daraltan/genişleten çeviri, kaynakta olmayan çıkarım, başka eyaletin ya da genel ABD kuralının California'ya yanlış uygulanması, dönemi yazılmamış tutar.

## Girdi
- `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\denetim\<parça>_kartlar.jsonl`: satır başına bir kayıt `{sheet, entry_id, fields{…kartın bütün alanları…}, links[{label,url}], sources[{source_id,url,publisher,text_file}]}`. Kaynak metni `text_file` yolundaki dosyadır (bizim kayıtlı kopyamız).
- Parçanın BÜTÜN kayıtlarını denetle (örneklem değil). Kayıt başına 2–4 iddia seç: kartın en önemli kural/koşul/hak cümleleri ve okuru yanıltabilecek genellemeler.

## Çıktı (yalnız bu iki dosya, UTF-8 JSONL, Python ile `ensure_ascii=False`)
1. `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\denetim\<parça>_iddia.jsonl` — iddia başına bir satır, anahtarlar bu sırayla:
   `{"claim_id","entry_id","iddia","ülke_şehir_statü","dönem","resmî_URL","kaynak_bölümü","yayın_yürürlük_tarihleri","kontrol_tarihi","hesap_varsa_girdiler","sonuç","ağırlık","belirsizlik","alıntı","doğrusu"}`
   - `claim_id` = `D-<parça>-<n>` (dosyada benzersiz, 1'den artan).
   - `sonuç` ∈ `doğru` | `yanlış` | `eksik_koşul` | `kaynak_yetersiz` | `çelişkili_kaynak`.
   - `ağırlık` ∈ `ciddi` | `orta` | `hafif`; `sonuç` = `doğru` ise `-`.
   - `kontrol_tarihi` = `2026-10-23`. `resmî_URL` = dayanılan kaynağın `url`'si. Bilinmeyen alan `""`.
   - `alıntı`: kaynak metninden birebir, en çok 200 karakter (çeviri/özet değil).
   - `doğrusu`: `doğru` olmayanda karta konabilecek Türkçe öneri ("sen" hitabıyla ya da kişisiz); `doğru`da `""`.
2. `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\denetim\<parça>_karar.jsonl` — kayıt başına bir satır: `{"entry_id","karar","en_agir","ozet"}`; `karar` ∈ `temiz` | `düzelt`; `en_agir` ∈ `ciddi` | `orta` | `hafif` | `-`; `ozet` kısa Türkçe.
- Kart dosyasındaki her `entry_id` karar dosyasında tam bir kez bulunmalı.

## Dönüş (tek satır JSON)
`{"part":"<parça>","cards":N,"claims":M,"dogru":a,"duzelt_kart":b,"ciddi":c,"orta":d,"hafif":e}` — sayıları kendi iki dosyandan say.
