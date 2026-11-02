# Son yeniden denetim (d7) — Marbella

`D6_GOREV.md`'yi (ve onun gösterdiği `D5_GOREV.md`'yi) oku ve aynen uygula; yalnız şu farklarla:

- Tur adı **d7**. Girdi `W\denetim\<p>-d7_kartlar.txt`; çıktı `<p>-d7_iddia.jsonl`, `<p>-d7_karar.jsonl`, mekân (m1–m2) ve mahallede `<p>-d7_mekan-dogrulama.jsonl`. `-d5_`, `-d6_` ve tire'siz dosyalara YAZMA.
- Değişiklikler `W\denetim\<p>-d6_degisiklik.jsonl`'de, kapatılması beklenen bulgular `W\denetim\<p>-d6_iddia.jsonl`'de.
- Odak: d6 değişiklikleri kaynakla tutarlı mı, d6 bulgusunu kapatıyor mu, yeni yanlış eklemiş mi. Değişiklik kaydında `yeni=""` ve "kaynakta yok" gerekçeli satırlar bilinçli olarak yapılmadı: kaynakta gerçekten yoksa bulgu yazma.
- Bu son tur: bulgu yazarken `doğrusu` alanına doğrudan uygulanabilir metni (ya da "şu cümleyi çıkar") yaz.
