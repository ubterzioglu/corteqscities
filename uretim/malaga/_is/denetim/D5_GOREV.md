# Son tam denetim (d5) — denetçi görevi, Málaga (CITY-075)

Kayıtları sen yazmadın. Paketin teslimden önceki SON hâlini denetliyorsun; dış denetim paketi bu hâliyle okuyacak. Görev mesajı sana parçaları (`<p>`) verir.

## Oku
- `C:\temp_private\corteqs\0000_newera\.claude\skills\city-pack\agents\iddia-denetcisi.md` — yöntem maddeleri 1–9 geçerli; "Çıktı" ve "Dönüş" bölümleri ESKİ, geçersiz (çıktı aşağıda).
- Girdi (parça başına): `W\denetim\<p>-d5_kartlar.txt` (okunur hâli; aynı içerik `-d5_kartlar.jsonl`): her kayıt + kaynaklar (text_file) + BÜTÜN defter satırları (iddialar) + butonlar/adımlar (rotada plan ve bacaklar). Kaynak metinleri: text_file (Read). Yalnız bunları oku; internete çıkma. Metin yetmiyorsa sonuç `kaynak_yetersiz`.
- W = `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is`

## Ne yapacaksın — kayıtların HEPSİ, örneklem değil
- Her kaydın BÜTÜN defter satırlarını anlamıyla kaynak metnine karşı oku: kime uygulanır, koşul, istisna, zorunlu/yasak/hak, sayı-birim-dönem, anlamı daraltan/ters çeviren çeviri, kaynakta olmayan çıkarım, işlem aşaması karışıklığı (madde 7).
- Yanıt kartlarında K25 (ilk cümle başlığın cevabı) ve K26 (işlem kartında nereye — Málaga'daki ofis/kanal ve randevu yolu; ne getir; ne öder ya da "ücretsiz"; ne kadar sürer/son tarih, gün türüyle). Eksik öğeyi adıyla yaz.
- Mekân ve mahallede madde 9 satırı (kimlik, adres, koordinat, ziyaret).
- Ayrıca bulgu: turizm portalı ücret/saat/işlem kuralı kaynağı değil; yılsız ya da geçmiş tarihli istisna; okura iş bırakan cümle ("kurumdan doğrulayın", "siteye bak"); "siz" hitabı ya da sen/siz karışması; kayıtta iç süreç notu; mekânı tanıtmayan not (S08); bağlantı etiketi hedefle uyuşmuyor; aynı konuyu tekrar eden kart (K27/K28: hangi kartla, kısaca); kart başına 2'den fazla source_ids; `visit_status` dolu.
- `doğru` kararı yalnız kaynak metninde gördüğün birebir karşılığa dayanır.

## Çıktı (parça başına, yalnız bunlar)
1. `W\denetim\<p>-d5_iddia.jsonl` — doğru olmayan HER iddia + kayıt başına 2–4 doğru iddia:
   `{"claim_id","entry_id","iddia","ülke_şehir_statü","dönem","resmî_URL","kaynak_bölümü","yayın_yürürlük_tarihleri","kontrol_tarihi":"2026-10-29","hesap_varsa_girdiler","sonuç":"doğru|yanlış|eksik_koşul|kaynak_yetersiz|çelişkili_kaynak","ağırlık":"ciddi|orta|hafif|-","belirsizlik","alıntı":"birebir ≤200","doğrusu"}`
   entry_id: kaydın kimliği (sözlükte term_id, rotada route_id değeri). Defterde olmayan bilgi / kayıt düzeyi bulgu için claim_id `<kimliğin son kısmı>-K<n>` (ör. `-K26`, `-K25`, `-K27`).
2. `W\denetim\<p>-d5_karar.jsonl` — kayıt başına `{"entry_id","karar":"temiz|düzelt","en_agir","ozet","denetlenen_iddia":<kaydın defter satırı sayısı>,"dogru_ids":[...]}`.
3. Yalnız mekân (m1–m5) ve mahalle parçalarında: `W\denetim\<p>-d5_mekan-dogrulama.jsonl` — kayıt başına `{"entry_id","kimlik","adres","koordinat","ziyaret","sonuc":"geçti|kaldı","not"}` (madde 9; mahallede adres "tutar", notta "mahalle").
Başka dosyaya yazma; kayıtları değiştirme. Tire'siz eski tur dosyalarına (`<p>_iddia` vb.) yazma.

## Sınırlar
Kabuk kullanma (Bash ve PowerShell yok): yalnız Read, Glob, Grep, Write. Alt ajan başlatma. JSONL'leri Write ile yaz (UTF-8, satır başına bir JSON); her 5 kayıtta bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz. Bütçe: parça başına ~30 dakika.
