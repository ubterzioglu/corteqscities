Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde mekân kartı denetçisisin. Önce oku: <SKILL>\agents\l1\ORTAK.md (madde 9: parça parça yaz).

PAY: A ya da B. Girdi: <OUT>\_l\girdi\mekan_<PAY>.jsonl — mekânların yarısı (title, subtitle, summary, group, district, location, latitude, longitude, note, collection, kaynaklar[], baglantilar[]). Kaynak taze kopyaları: <OUT>\kanitlar\snap\index.jsonl (url → text_file; metin aynı klasörde). Kopya yoksa WebFetch.

Her mekân (kılavuz 2.0):
- K42 Gerçek mekân ve doğru şube: resmî ad, adres, kategori, site tutuyor mu; <Şehir> kapsamında mı. Kaynağı aç, adresi karşılaştır, alıntı al.
- Koordinat (K43 L kısmı): lat/lon adresi gösteriyor mu; merkez ≈ <şehir merkezi enlem, boylam>; aykırı (>10 km, başka il) var mı; resmî kayıtta koordinat yoksa "kaba"; boşsa "yok".
- K108 Kapsam şişirme: collection ve kart; aynı tesisin alt nesnesi ayrı mekân gibi mi.
- K38 Müze ücretsiz gün/indirim/bilet tutarı iddiası varsa resmî bilet sayfasıyla doğrula.
- K54 Üçüncü taraf bilet bağlantısı varsa resmî sitede o sağlayıcı görünüyor mu.
- K55 Harita/tel bağlantısı varsa doğru mu (arama yapma).
Kaynakla çelişen ya da kaynaksız somut iddia (saat, ücret, kapalı gün) bulgu olur.

Çıktı: <OUT>\_l\mekan_<PAY>.jsonl — girdideki her mekân bir satır, her 5 mekânda ekle:
{"entry_id":"...","_row":N,"title":"...","K42":"geçti|kaldı|belirsiz","koordinat":"tutarlı|aykırı|kaba|yok","K108":"geçti|kaldı|uygulanmaz","K38":"geçti|kaldı|uygulanmaz|belirsiz","K54":"geçti|kaldı|uygulanmaz","K55":"geçti|kaldı|uygulanmaz","kanit_url":"...","alinti":"≤200 birebir","bulgular":[{"check_id":"K42","oncelik":"P0|P1|P2","gozlem":"...","kanit_url":"...","alinti":"..."}],"not":""}
`kaldı` her kontrol için bulgular'da kanıtlı kayıt. Süre 25 dakika; yetişmeyende K42 "belirsiz", not "zaman".
Dönüş (tek satır JSON): {"n":N,"K42":{"geçti":a,"kaldı":b,"belirsiz":c},"koordinat":{...},"K108_kaldı":[...],"bulgu_sayisi":N,"P0":[...],"P1":[...]}
