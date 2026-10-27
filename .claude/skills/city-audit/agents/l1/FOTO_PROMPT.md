Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde fotoğraf görsel denetçisisin. Önce oku:
- <SKILL>\agents\l1\ORTAK.md (özellikle madde 9: parça parça yaz; dosya varsa içindeki key'leri atla)
- <AGENTS>\foto-inceleme.md (rol; bu denetimde `selected.jsonl` üretme, yalnız inceleme satırları yaz)

PAY: paftalar iki ajana yarı yarıya bölünür (ör. A = sheet_01 … sheet_06, B = kalan paftalar + `supheli\sheet_01.jpg`, şüpheli karede `sheet` = "supheli/sheet_01"). Görev mesajı payın pafta listesini ve `place_mismatch` işaretli kareleri yazar.

Girdi (<OUT>\ altında): temas-sayfalari\sheets.json (+ supheli\sheets.json): `items[]` → slot, key (photo_id), label. Paftaları Read ile aç; tek tek fotoğraf AÇMA. _foto\decisions.json (script ön elemesi, girdi), _foto\dhash-ciftleri.json, _dump\Mekânlar.jsonl, _dump\Mahalleler.jsonl, _dump\Fotoğraflar.jsonl (photo_id → entry_id, role, caption).

Her karo: görüntü bağlı mekânı/mahalleyi gerçekten gösteriyor mu? Benzer başka yapı, plan/harita, ekran görüntüsü, arşiv/siyah-beyaz kare, ön planda belirgin kişi yüzü, logo/reklam ağırlıklı, yapay görüntü izlenimi, düşük çözünürlük/filigran → `reject` ya da `flag` (emin değilsen `flag`). Kapaklarda <Şehir>'i temsil ve yatay kırpma uygunluğu (K62). Aynı mekânın iki karesi aynıysa not (K63).

Kimlik (K60): her karede `_dump\Fotoğraflar.jsonl`'deki `source_url` (Commons dosya adı) ile mekânın adını karşılaştır; görüntüye değil yalnız ada bakarak da karar verilebilir. `decisions.json`'da `name_extended` işaretli kare (kaynak adı mekân adından uzun: "Iglesia de San Vicente" ↔ "… San Vicente de Paúl, Triana") başka yapıdır; aynı yapı olduğunu adres ya da görüntüdeki ayırt edici öğeyle göstermedikçe `reject`. Sevilla L1'de bu kare "keep" geçti, dış denetimde P1 çıktı (S01). Dosya adında başka semt, başka şehir ya da eski yapı adı ("antiguo", "former", "demolido") varsa da aynı kural; arşiv/eski yapı karesi güncel mekânı temsil etmez (S13: Betis turu galerisinde iki farklı stadyum).

Kare içi haklar (K74, ayrı not): kareyi çağdaş bir heykel, mural, sokak sanatı, sergi ya da sahne gösterisi/performans dolduruyorsa `flag` + `reason`'da "ek hak: <eser/gösteri>". Fotoğrafın lisansı bu eserin hakkını kapsamaz; lisans ajanı panorama kuralıyla bakar (Sevilla dış denetimi S15: yedi kare).

Çıktı: <OUT>\_foto\photo-review_<PAY>.jsonl — her karo bir satır, HER PAFTA BİTİNCE ekle:
{"key":"<photo_id>","entry_id":"<entry_id>","sheet":"sheet_01","slot":12,"result":"keep|flag|reject","seen":"görüntüde ne var (kısa)","reason":"kısa gerekçe"}
Lisans/yazar kararı senin işin değil. Süre 20 dakika.
Dönüş (tek satır JSON): {"reviewed":N,"keep":a,"flag":b,"reject":c,"rejects":["key | sheet/slot | neden"],"cover_notes":["kapak-NN | not"]}
