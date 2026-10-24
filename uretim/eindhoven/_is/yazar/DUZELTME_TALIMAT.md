# Editör talimatı: bilgi kartı düzeltme turu (Eindhoven, CITY-039)

Kartları sen yazmadın. Görevin: kaynaklara sadık, okuyucuyu yanıltmayan kartlar. Önce oku:
1. `C:\temp_private\corteqs\0000_newera\uretim\eindhoven\_is\yazar\ORTAK_TALIMAT.md` (alan biçimi, iddia defteri, yasaklar — hepsi geçerli)
2. Konu görev dosyan: `_is\yazar\duzeltme\<konu>.json` — içinde: denetçi bulguları (`audit`), yeni kaynaklar (`new_sources`), ek kaynaklar (`extra_sources`), özel görevler (`special`), order aralığı.

Kök: `C:\temp_private\corteqs\0000_newera\uretim\eindhoven\`. Kendi geçici klasörün: `C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\3dadd8be-f0d2-423f-acbe-036dd2504ce8\scratchpad\duz_<konu>\` (başka yere geçici dosya yazma).

## Düzenleyeceğin dosyalar (yalnız kendi konuların)
- `_is\data\parcalar\Yanıtlar.<konu>.jsonl`
- `_is\data\parcalar\Bağlantılar.<konu>.jsonl`
- `_is\claims\<konu>.jsonl`
Dosyayı baştan yaz (aynı biçim, aynı anahtar sırası). Mevcut kartların `entry_id`/`slug`'ını DEĞİŞTİRME. Kaynak metinleri: `_is\kaynak_dizini.jsonl` içindeki `text_file` (yeni ve ek kaynakların text_file yolu görev dosyanda).

## Görevler (sırayla)
1. **Denetçi bulguları** (`audit`): `sonuç` yanlış / eksik_koşul / çelişkili_kaynak / kaynak_yetersiz olan her iddiayı kaynak metinle KENDİN doğrula, kartı düzelt. Denetçinin `doğrusu` önerisi bir öneridir; kaynağa uymuyorsa kaynağa göre yaz. Çelişkili kaynakta: resmî devlet kurumu (rijksoverheid/government.nl, IND, RDW, Belastingdienst…) esas; diğer görüşü karttan silme, "X'e göre … ; Y ise … diyor" biçiminde ayır ve okuyucuya ne yapması gerektiğini söyle.
2. **Eksikleri kapat** (`new_sources`, `extra_sources`): her kaynağın `gap` açıklamasındaki bilgiyi ilgili karta ekle; uygun kart yoksa yeni kart yaz (order aralığında, slug tüm pakette benzersiz — `_is\data\Yanıtlar.jsonl`'deki slug ve başlıklarla çakışmasın). Her yeni kartın en az 1 Bağlantılar satırı olur.
3. **Kural gözden geçirmesi** (konudaki BÜTÜN kartlar): kural/koşul içeren her cümleyi kaynağıyla karşılaştır:
   - Kapsam: kime uygulanır (AB vatandaşı / Türk vatandaşı / bilgi göçmeni / statü sahibi / öğrenci / herkes)? Kart dar kuralı herkese genellemiş mi?
   - Koşul ve istisna: kaynaktaki önemli koşul (süre, yaş, gelir, belge, "yalnız … ise") eksik mi?
   - Anlam: çeviri anlamı tersine çeviriyor mu? Kaynakta olmayan çıkarım var mı?
   Yanlışı düzelt, eksik önemli koşulu ekle. Her yeni/değişen sayı ve kural için iddia defterine birebir alıntılı satır ekle; silinen bilginin defter satırını sil.
4. **Değer**: konu başına 18–26 kart. Okuyucunun ilk soracağı konular önce. Düşük değerli/tekrar kartı silebilirsin (Bağlantılar ve defter satırlarıyla birlikte); silineni raporla.
5. `visual_json`: adımları değişen kartta şema adım sayısı `steps` satır sayısına eşit değilse şemayı `""` yap.

Bitirmeden önce kendi betiğinle kontrol et: her `quote` text_file içinde birebir (boşluk normalleştirilmiş), anahtar sırası doğru, slug/başlık tekrarı yok, her kartta ≥1 bağlantı, bağlantı url'leri kaynak dizininde.

## Dönüş (konu başına bir satır JSON)
`{"topic":"<konu>","cards_before":N,"cards_after":M,"audit_fixed":a,"gap_added":b,"gap_updated":c,"rule_fixes":d,"removed":["slug",...],"open":["kaynakla çözülemeyen kısa not",...]}`
