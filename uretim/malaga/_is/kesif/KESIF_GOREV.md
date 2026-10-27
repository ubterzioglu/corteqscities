# Kaynak keşfi görevi — Málaga (CITY-075, İspanya, Endülüs)

Okur: Málaga'ya taşınan Türkçe konuşan yeni gelen. Görevin yalnız **resmî kaynak adresi bulmak**; metin yazmıyorsun.

## Bağlam
- Ulusal (İspanya) ve bölge (Endülüs) kuralları zaten 105 kartlık ülke paketinde. Senin konularındaki hazır kart başlıkları şu dosyada (Read aracıyla oku): C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\kesif\ulke_kart_sorulari.md. Bunları TEKRAR kaynaklama.
- Senin işin **Málaga'ya özgü** bilgi: Málaga'daki ofisler, adresler, randevu yolu, şehir hizmetleri, yerel tarifeler, Málaga Belediyesi (malaga.eu) ve Junta'nın Málaga ili sayfaları, şehir şirketleri (EMASA, Limasam, EMT Málaga, Metro de Málaga, CTMAM, Promálaga), Málaga'daki hastaneler ve sağlık bölgeleri, Málaga'daki DGT/AEAT/SS/SEPE/Extranjería ofisleri.
- Her konunun "ilk 5 soru"su: `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\yazar\ilk5.json`. Her soruya en az bir kaynak bul; bulamazsan `gaps`'e yaz.
- **Erişim haritası:** `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\kesif\KESIF_TALIMAT.md`. Oradaki engelli alan adlarını (özellikle malaga.es, sede.malaga.eu, huvv.es, aena.es, sede.administracionespublicas.gob.es) DENEME; o bilgiyi başka resmî yayıncıdan bul ya da `gaps`'e yaz.

## Kurallar
- Yalnız resmî yayıncının (devlet, Junta de Andalucía, Málaga Belediyesi, belediye şirketi, kamu hastanesi, kamu üniversitesi, resmî anıt/müze yönetimi) **derin sayfası**. Wikipedia yok; tek başına anasayfa yok; blog, forum, expat portalı, rehber sitesi, ticari site yok.
- Konu başına **12–16** adres (en çok 18). Fazlası kapasiteyi şişirir; 12'nin altı fazın kapısını geçmez (kabul edilmeyen adres olacağı için 13–14 hedefle).
- Her adres için `must_contain`: sayfada bilginin geçtiğini kanıtlayan 1–3 **birebir** kısa ifade (sayfanın kendi dilinde, genelde İspanyolca; 3–8 kelime; menü/başlık değil, gövde metni). Sayfayı WebFetch ile açıp ifadeyi gerçekten gör. JS ile yüklenip metni boş gelen sayfayı ekleme.
- Birden çok konuya yarayan sayfayı her ilgili konunun dosyasına yaz.
- Uydurma adres yazma; açamadığın sayfayı ekleme.
- **Alt ajan başlatma.** Kendi geçici klasörün dışında dosya yazma (yalnız aşağıdaki çıktı dosyaları).

## Çıktı
Her konu için `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is\kesif\<konu>\selected.jsonl` (klasörü oluştur), satır başına bir JSON:
`{"url": "...", "must_contain": ["..."], "title": "...", "publisher": "...", "lang": "es", "why": "hangi ilk5 sorusuna / hangi bilgiye (Türkçe, kısa)"}`
UTF-8, BOM'suz. Yazmak için Write aracı ya da Python kullan.

## Bütçe
30 dakika / 120 araç çağrısı. Dolunca bulduklarınla dön.

## Dönüş
Tek satır JSON: `{"topics": {"<konu>": <adres sayısı>, ...}, "gaps": ["<konu>: <bulunamayan soru/bilgi>", ...]}`
