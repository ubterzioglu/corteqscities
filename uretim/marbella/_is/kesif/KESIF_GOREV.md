# Kaynak keşfi görevi — Marbella (CITY-080, İspanya, Endülüs, Málaga ili)

Okur: Marbella'ya taşınan Türkçe konuşan yeni gelen. Görevin yalnız **resmî kaynak adresi bulmak**; metin yazmıyorsun.

## Bağlam
- Ulusal (İspanya) ve bölge (Endülüs) kuralları zaten 105 kartlık ülke paketinde. Senin konularındaki hazır kart başlıkları: /home/user/corteqscities/uretim/marbella/_is/kesif/ulke_kart_sorulari.md (Read ile oku). Bunları TEKRAR kaynaklama.
- Senin işin **Marbella'ya özgü** bilgi: Marbella'daki ofisler, adresler, randevu yolu, belediye hizmetleri (marbella.es; San Pedro Alcántara belediye şubesi dahil), yerel tarifeler ve vergiler, belediye/ilçe şirketleri (su: Acosol ve Marbella'nın su hizmeti; çöp/temizlik; şehir otobüsü), Junta'nın Málaga ili ve Costa del Sol sağlık bölgesi sayfaları (Hospital Costa del Sol, Marbella sağlık merkezleri), Marbella'daki ya da en yakın DGT/AEAT/SS/SEPE/Extranjería/Policía ofisleri, Málaga metropol ulaşım konsorsiyumu (ctmam.es) hatları. Marbella'da bir hizmet yoksa en yakın resmî ofis (çoğu Málaga şehrinde) kabul.
- Her konunun "ilk 5 soru"su: /home/user/corteqscities/uretim/marbella/_is/yazar/ilk5.json. Her soruya en az bir kaynak bul; bulamazsan `gaps`'e yaz.
- **Erişim haritası:** /home/user/corteqscities/uretim/marbella/_is/kesif/KESIF_TALIMAT.md. Oradaki engelli alan adlarını DENEME; o bilgiyi başka resmî yayıncıdan bul ya da `gaps`'e yaz.

## Kurallar
- Yalnız resmî yayıncının (devlet, Junta de Andalucía, Marbella Belediyesi, belediye şirketi, kamu hastanesi, kamu üniversitesi, resmî anıt/müze yönetimi) **derin sayfası**. Wikipedia yok; tek başına anasayfa yok; blog, forum, expat portalı, rehber sitesi, ticari site yok. Turizm portalı (turismo.marbella.es) ücret, saat ve işlem kuralı kaynağı değildir.
- Konu başına **12–16** adres (en çok 18). 12'nin altı fazın kapısını geçmez (kabul edilmeyen adres olacağı için 13–15 hedefle).
- Her adres için `must_contain`: sayfada bilginin geçtiğini kanıtlayan 1–3 **birebir** kısa ifade (sayfanın kendi dilinde, genelde İspanyolca; 3–8 kelime; menü/başlık değil, gövde metni). Sayfayı WebFetch ile açıp ifadeyi gerçekten gör. JS ile yüklenip metni boş gelen sayfayı ekleme. WebFetch özet verir; ifadeyi özetten değil sayfa metninden birebir al (WebFetch isteminde "şu ifadeyi birebir alıntıla" de).
- Birden çok konuya yarayan sayfayı her ilgili konunun dosyasına yaz.
- Uydurma adres yazma; açamadığın sayfayı ekleme.
- **Alt ajan başlatma.** Yalnız aşağıdaki çıktı dosyalarını yaz.

## Çıktı
Her konu için /home/user/corteqscities/uretim/marbella/_is/kesif/<konu>/selected.jsonl (klasörü oluştur), satır başına bir JSON:
`{"url": "...", "must_contain": ["..."], "title": "...", "publisher": "...", "lang": "es", "why": "hangi ilk5 sorusuna / hangi bilgiye (Türkçe, kısa)"}`
UTF-8, BOM'suz. Write aracıyla yaz; her 4–5 adreste dosyayı güncelle (parça parça yaz).

## Bütçe
30 dakika / 120 araç çağrısı. Dolunca bulduklarınla dön.

## Dönüş
Tek satır JSON: `{"topics": {"<konu>": <adres sayısı>, ...}, "gaps": ["<konu>: <bulunamayan soru/bilgi>", ...]}`
