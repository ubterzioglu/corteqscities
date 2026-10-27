# Alt ajan: fotoğraf görsel kontrolü (temas paftası)

Numaralı temas paftalarına bakarak her karenin bağlı mekânı gerçekten gösterip göstermediğine karar veriyorsun. Tek tek fotoğraf açma; yalnız paftaları gör (token tasarrufu: 272 fotoğraf tek tek ~626K, paftayla ~16–26K).

## Girdi
- `sheets.json` (contact_sheet çıktısı): her pafta için `slot → key, path, label`
- Pafta görüntüleri: `sheet_NN.jpg` (genel 30'lu; şüpheliler 20'li)
- `decisions.json` (photo_prefilter): her adayın `keep / flag / reject` ve gerekçesi
- `dhash.json`: yakın kopya çiftleri
- Mekân bilgisi: ad, kategori, adres (label'da)

## Her kare için bak
1. Görüntü bağlı mekânı mı gösteriyor? Cephe, tabela, bilinen siluet. Aynı şehirde benzer yapı (ör. başka su kulesi, başka kilise) = **ret**.
2. Arşiv / siyah-beyaz / tarihî kare güncel mekân fotoğrafı yerine kullanılmaz.
3. Belirgin kişi yüzü ön planda, logo/reklam ağırlıklı, iç mekân yerine plan/harita, ekran görüntüsü, AI görünümü → ret veya işaret.
4. Düşük çözünürlük, aşırı kırpma, filigran → ret.
5. dHash çiftinden yalnız biri seçilir (K63).
5a. **Ad kontrolü:** label'daki Commons dosya adını mekân adıyla karşılaştır. `decisions.json`'da `name_extended` (kaynak adı mekân adından uzun: "Iglesia de San Vicente" ↔ "… San Vicente de Paúl, Triana") ya da dosya adında başka semt, başka şehir veya eski yapı adı varsa kare **ret**; aynı yapı olduğunu görüntüdeki ayırt edici öğe ya da adresle göstermedikçe. Sevilla'da bu kare seçildi, dış denetimde P1 çıktı (S01).
5b. **Kare içi eser/gösteri:** kareyi çağdaş heykel, mural, sokak sanatı, sergi ya da sahne gösterisi dolduruyorsa `flag` + `reason`'da "ek hak: <eser>"; fotoğraf lisansı eserin hakkını kapsamaz (Sevilla S15: yedi kare). Mekânın başka karesi varsa onu seç.
6. Mekân başına en iyi 1–3 kare; kapak adayları ayrıca işaretlenir.

## Sınırlar
- Lisans ve yazar kararı senin işin değil (script + insan). Lisans alanına dokunma.
- `pixel_review_status` ve `rights_status` = `Bekliyor`; "onaylandı" yazma.
- Emin değilsen `flag`; tahminle `keep` deme.

## Çıktı
- `photo-review.jsonl`: `{"key":"...","entry_id":"...","sheet":"sheet_03","slot":12,"result":"keep|flag|reject","seen":"görüntüde ne var (kısa)","reason":"..."}`
- `selected.jsonl`: yalnız `keep` olanlar, `{photo_id, entry_id, slug, original_url}` (download_plan girdisi)

## Dönüş
`{"reviewed":N,"keep":a,"flag":b,"reject":c,"venues_without_photo":[...]}`
