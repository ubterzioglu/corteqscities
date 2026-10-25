# Kaynak keşfi görevi — Sevilla (CITY-107, İspanya, Endülüs)

Okur: Sevilla'ya taşınan Türkçe konuşan yeni gelen. Görevin yalnız **resmî kaynak adresi bulmak**; metin yazmıyorsun.

## Bağlam
- Ulusal (İspanya) ve bölge (Endülüs) kuralları zaten 105 kartlık ülke paketinde. Senin konularındaki hazır kart soruları:
  `& 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe' -c "import json,sys;[print(json.loads(l)['question']) for l in open(sys.argv[1],encoding='utf-8')]" "C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\data\parcalar\Yanıtlar.<konu>.jsonl"`
  (dosya yoksa o konuda ülke kartı yok). Bunları TEKRAR kaynaklama.
- Senin işin **Sevilla'ya özgü** bilgi: Sevilla'daki ofisler, adresler, randevu yolu, şehir hizmetleri, yerel tarifeler, belediye/Diputación/Junta'nın Sevilla ili sayfaları, şehir şirketleri (EMASESA, Metro de Sevilla, Sevilla Activa, Turismo de Sevilla), Sevilla'daki hastaneler ve sağlık bölgeleri, Sevilla'daki DGT/AEAT/SS/SEPE/Extranjería ofisleri.
- Her konunun "ilk 5 soru"su: `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\yazar\ilk5.json`. Her soruya en az bir kaynak bul; bulamazsan `gaps`'e yaz.
- **Erişim haritası:** `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\kesif\KESIF_TALIMAT.md`. Oradaki engelli alan adlarını (özellikle sevilla.org, tussam.es, consorciotransportes-sevilla.com, lipasam.es) DENEME; o bilgiyi başka resmî yayıncıdan bul ya da `gaps`'e yaz.

## Kurallar
- Yalnız resmî yayıncının (devlet, Junta de Andalucía, Diputación de Sevilla, belediye şirketi, kamu hastanesi, kamu üniversitesi, resmî anıt/müze yönetimi) **derin sayfası**. Wikipedia yok; tek başına anasayfa yok; blog, forum, expat portalı, rehber sitesi, ticari site yok.
- Konu başına **8–14** adres (kesif konusunda 12–18). Fazlası kapasiteyi şişirir.
- Her adres için `must_contain`: sayfada bilginin geçtiğini kanıtlayan 1–3 **birebir** kısa ifade (sayfanın kendi dilinde, genelde İspanyolca; 3–8 kelime; menü/başlık değil, gövde metni). Sayfayı WebFetch ile açıp ifadeyi gerçekten gör. JS ile yüklenip metni boş gelen sayfayı ekleme.
- Birden çok konuya yarayan sayfayı her ilgili konunun dosyasına yaz.
- Uydurma adres yazma; açamadığın sayfayı ekleme.
- **Alt ajan başlatma.** Kendi geçici klasörün dışında dosya yazma (yalnız aşağıdaki çıktı dosyaları).

## Çıktı
Her konu için `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\kesif\<konu>\selected.jsonl` (klasörü oluştur), satır başına bir JSON:
`{"url": "...", "must_contain": ["..."], "title": "...", "publisher": "...", "lang": "es", "why": "hangi ilk5 sorusuna / hangi bilgiye (Türkçe, kısa)"}`
UTF-8, BOM'suz. Yazmak için Write aracı ya da Python kullan.

## Bütçe
30 dakika / 120 araç çağrısı. Dolunca bulduklarınla dön.

## Dönüş
Tek satır JSON: `{"topics": {"<konu>": <adres sayısı>, ...}, "gaps": ["<konu>: <bulunamayan soru/bilgi>", ...]}`
