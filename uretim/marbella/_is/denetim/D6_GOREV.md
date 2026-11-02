# Yeniden denetim (d6) — Marbella

`D5_GOREV.md`'yi oku ve aynen uygula; yalnız şu farklarla:

- Tur adı **d6**. Girdi `W\denetim\<p>-d6_kartlar.txt`; çıktı `W\denetim\<p>-d6_iddia.jsonl`, `<p>-d6_karar.jsonl`, mekân (m1–m3) ve mahallede `<p>-d6_mekan-dogrulama.jsonl`. `-d5_` ve tire'siz dosyalara YAZMA.
- Girdideki kayıtlar d5 son denetiminden sonra editörce değiştirildi. Önce `W\denetim\<p>-d5_degisiklik.jsonl`'i oku (editörün her değişikliği: eski, yeni, gerekçe, alıntı) ve `W\denetim\<p>-d5_iddia.jsonl`'deki doğru olmayan bulguları gör.
- Odak: (1) her değişiklik kaynak metniyle tutarlı mı, bulguyu kapatıyor mu, yeni yanlış/genelleme/okura iş bırakan cümle eklemiş mi; (2) d5 bulgusu olup değişiklik kaydı olmayan ya da kapanmamış bulgu var mı (claim_id'yi d5'teki gibi yaz, sonuç `eksik_koşul`/`kaynak_yetersiz`); (3) kaydın değişmeyen kısmı d5'te denetlendi, yeniden ayrıntılı okumaya gerek yok, yalnız değişen alanlarla çelişki varsa yaz.
- Mekân ve mahallede madde 9 satırını kaydın SON hâline göre yeniden yaz (her kayıt için bir satır).
- `karar.jsonl`'de `denetlenen_iddia` = kaydın girdideki defter satırı sayısı; `dogru_ids` doğru bulduğun defter satırları.
- Kaynakta bulunmayan bir bilgi editörce zaten çıkarıldıysa (bilgi yok) bu bulgu değildir; bilgi eksikliği K26 ise ve kaynakta yoksa `hafif` yaz.
- Bütçe: parça başına ~15 dakika.
