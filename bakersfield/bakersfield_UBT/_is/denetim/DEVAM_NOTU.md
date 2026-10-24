# Yarıda kalan görevi devralma notu (23.10.2026, 17:10)

Bu görevi daha önce başka bir ajan başlattı; Sonnet oturum kotası dolduğu için yarıda kaldı. Senin işin aynı görevi **kaldığı yerden** bitirmek.

1. Önce görev mesajındaki dosyaları ve (editörsen) `<parça>_degisiklik.jsonl`, (doğrulayıcıysan) `<parça>_dogrulama.jsonl` dosyasını oku. Bu dosyalarda önceki ajanın yaptıkları olabilir; yarım kalmış da olabilir.
2. Kayıt dosyalarının (JSONL) geçerli olduğunu doğrula: her satır geçerli JSON, anahtar sırası doğru, satır sayısı makul. Bozuksa ya da yarım yazılmışsa, önceki ajanın geçici klasöründeki yedeklere bak (görev mesajındaki `<TMP>` klasörü; altında `yedek`, `backup` ya da benzeri). Yedekten geri yüklediysen bunu dönüşte `open`'a yaz.
3. Editörsen: değişiklik kaydındaki her satırın kayıt dosyasında gerçekten uygulanmış olduğunu kontrol et; uygulanmamış ya da yarım kalanı tamamla. Değişiklik kaydında satırı olmayan "doğru" olmayan bulguları uygula. Aynı değişikliği iki kez kaydetme; değişiklik kaydına önceki satırları silmeden ekle.
4. Doğrulayıcıysan: `<parça>_dogrulama.jsonl` varsa ve eksikse baştan, tam yaz (önceki yarım dosyanın üzerine).
5. Görev mesajındaki kurallar ve dönüş biçimi aynen geçerlidir. Alt ajan başlatma.
