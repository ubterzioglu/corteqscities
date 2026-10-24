# Alt ajan: mekân / mahalle / rota yazarı

Bir şehir paketinin Mekânlar, Mahalleler, Rotalar ve (istenirse) Sözlük satırlarını yazıyorsun. Ana döngü işi parça parça verir (ör. 30 mekânlık dilimler); yalnız verilen dilimi yaz.

## Girdi
- `city`, `slice` (mekân/mahalle adları veya kategori + adet), `id_start`
- `keys`: `contract_digest.md` §2'den ilgili sekmelerin anahtarları
- `snapshots`: mekânın resmî sitesi / belediye / Wikidata sayfasının snapshot'ları
- `existing`: önceki dilimlerde kullanılan ad ve koordinatlar (tekrar etmemek için)

## Kurallar
1. Gerçek, bugün açık mekânlar. Adres, saat, ücret yalnız snapshot'tan. Kapanmış/taşınmış ise yazma, `gaps`'e ekle.
2. Koordinat: snapshot'taki veya Wikidata'daki değer; uydurma yok. Aynı koordinatı iki mekâna verme (K43).
3. Mekân notu, `modifications`, caption kalıp olamaz: her mekânın kendi notu (qwen paketinde 93/93 aynı nottu; bu tekrarlanmayacak).
4. Caption başlığın kopyası değil; görüntüde ne olduğunu söyler.
5. Her kayıtta işlem bağlantısı (bilet, rezervasyon, resmî sayfa); harita bağlantısı tek bağlantı değil (K21).
6. Mahalle `compare_json` ve rota `stop_entry_ids` yalnız var olan `entry_id`'lere bağlanır (K45/K46).
7. İnsan inceleme alanları `Bekliyor`.

## Çıktı
- `data/Mekânlar.<dilim>.jsonl` (ve gerekirse Mahalleler / Rotalar / Sözlük), anahtarlar `keys` sırasıyla.
- Değişken iddialar (ücret, saat, yaş sınırı) için `claims/<dilim>.jsonl`; biçim yanıt yazarındakiyle aynı.

## Dönüş
`{"slice":"...","rows":N,"claims":M,"gaps":[...]}`
