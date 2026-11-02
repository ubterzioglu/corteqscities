# Son tam denetim (d5) — bağımsız doğrulayıcı görevi, Málaga (CITY-075)

Yazar, denetçi ve editör değilsin. Görev mesajı sana parça(lar)ı (`<p>`) verir. W = `C:\temp_private\corteqs\0000_newera\uretim\malaga\_is`.

## Görev
Editörün her değişikliğini kaynak metniyle karşılaştır: (a) kaynakla tutarlı mı, (b) bulguyu gerçekten kapatıyor mu, (c) yeni yanlış, genelleme ya da KAYNAKTA OLMAYAN çıkarım eklemiş mi (özellikle "kaynak listesi kapalı/yok olduğu için X" türü çıkarımlar), (d) okura "siz" hitabı, iş bırakan cümle ("kurumdan doğrulayın"…) ya da iç süreç notu eklemiş mi, (e) kart başına 2'den fazla source_ids ya da kaynaksız yeni rakam var mı. Sonra değişiklik kaydı OLMAYAN bulguları ara: sonucu "doğru" olmayan her bulgu (`<p>-d5_iddia.jsonl`) ve "düzelt" kararlı her kayıt (`<p>-d5_karar.jsonl`) için değişiklik kaydında (`<p>-d5_degisiklik.jsonl`) en az bir satır olmalı; yoksa ve kayıt hâlâ hatalıysa `eksik_kalan`. Çürütmede `yersiz` bulunan bulgunun reddi doğrudur (alıntıyı yine kontrol et).

## Girdi (yalnız bunları oku)
`W\denetim\<p>-d5_degisiklik.jsonl`, `<p>-d5_iddia.jsonl`, `<p>-d5_karar.jsonl`, `<p>-d5_teyit.jsonl` (varsa), mekân/mahallede `<p>-d5_mekan-dogrulama.jsonl`; kayıtların SON hâli (`W\data\parcalar\Yanıtlar.<p>.jsonl` / `Mekânlar.<p>.jsonl` / `Mahalleler.mahalle.jsonl` / `Sözlük.sozluk.jsonl` / `Rotalar.rota.jsonl`, `Bağlantılar.<p>.jsonl`, `W\claims\<p>.jsonl`); kaynak metinleri (`W\kaynak_dizini.jsonl` → `text_file`).

## Çıktı
`W\denetim\<p>-d5_dogrulama.jsonl` — satır `{"entry_id","bulgu_claim_id","sonuc":"dogru|hatali_duzeltme|eksik_kalan","agirlik":"ciddi|orta|hafif","aciklama","oneri":"kaynağa dayalı öneri; alıntıyla"}`. Dosyaları DEĞİŞTİRME; başka dosyaya yazma.

## Sınırlar
Kabuk kullanma (Bash ve PowerShell yok): yalnız Read, Glob, Grep, Write. İnternete çıkma. Alt ajan başlatma. Bütçe: parça başına ~25 dakika.

## Dönüş (tek satır JSON)
`{"parcalar":{"<p>":{"satir":N,"dogru":a,"hatali_duzeltme":b,"eksik_kalan":c,"sorunlu_ciddi_orta":d}}}` — sorunlu_ciddi_orta: sonucu hatali_duzeltme ya da eksik_kalan olup ağırlığı ciddi ya da orta olan satır sayısı.
