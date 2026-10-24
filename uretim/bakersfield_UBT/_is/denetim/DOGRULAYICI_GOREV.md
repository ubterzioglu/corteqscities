# Bağımsız doğrulayıcı görev dosyası (Bakersfield · CITY-901 · 23.10.2026)

Kayıtları sen yazmadın, denetlemedin, düzeltmedin. Görevin: editörün yaptığı her değişikliği kaynak metniyle karşılaştırmak ve değişiklik kaydı olmayan bulguları aramak. "Doğru", "onaylandı" gibi bir ilan yapmazsın; yalnız bulgu yazarsın.

## Sınırlar
- **Yalnız verilen dosyaları oku; internete çıkma (WebSearch/WebFetch YOK).** Hiçbir dosyayı değiştirme (yalnız kendi çıktı dosyanı yazarsın).
- Alt ajan başlatma.

## Girdiler (`<parça>` görev mesajında)
- Değişiklik kaydı: `C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\denetim\<parça>_degisiklik.jsonl` — satır başına `{entry_id, alan, eski, yeni, bulgu_claim_id, gerekce, alinti}`. `bulgu_claim_id` bir denetim bulgusunun kimliği (`D-<parça>-<n>`), `kural_gozden_gecirme`, `acik_mi:…` ya da `dogrulama` olabilir.
- Denetim bulguları: `...\_is\denetim\<parça>_iddia.jsonl` (`claim_id, entry_id, iddia, sonuç, ağırlık, alıntı, doğrusu, resmî_URL`) ve `...\_is\denetim\<parça>_karar.jsonl`.
- Kayıtların bugünkü hâli: görev mesajındaki `...\_is\data\parcalar\<Sekme>.<parça>.jsonl` dosyaları ve defter `...\_is\claims\<parça>.jsonl`.
- Kaynak metinleri: `...\_is\kaynak_dizini.jsonl` → her `source_id` için `text_file` (bizim kayıtlı kopyamız). Kaydın `source_ids` alanındaki kimliklerin metinlerine bak.

## Yöntem
1. Her değişiklik satırı için (defter satırı ekleme/silme `iddia_defteri:` satırlarını yalnız örnekle, hepsini değil; asıl odak okura giden alanlar: `summary`, `steps`, `documents`, `cost`, `timing`, `note`, `title`, `subtitle`, `location`, `compare.*`, `definition`, `value` ve `kayit_eklendi`/`kayit_silindi`):
   - `yeni` metin kaynakla tutarlı mı (kaynakta geçiyor mu, `alinti` kaynak metinde birebir var mı)?
   - Bulguyu gerçekten kapatıyor mu (denetçinin `doğrusu`/`iddia`'sıyla karşılaştır)?
   - Yeni bir yanlış, genelleme, statü/kapsam kayması, anlamı ters çeviren çeviri ya da kaynakta olmayan çıkarım eklemiş mi?
   - Bulgu reddedildiyse (`yeni` = `""`) gerekçe ve alıntı reddi destekliyor mu?
2. `sonuç` ≠ `doğru` olan her denetim bulgusu için değişiklik kaydında en az bir satır var mı? Yoksa ve kayıt hâlâ bulgudaki sorunu taşıyorsa: `eksik_kalan`.
3. Kayıtta değişiklik kaydı olmayan bir değişiklik fark edersen (eski hâliyle bulgu metni uyuşmuyor) yalnız not et.

## Çıktı
`C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\denetim\<parça>_dogrulama.jsonl` — UTF-8 JSONL (Python, `ensure_ascii=False`). Kontrol ettiğin her değişiklik grubu (aynı `entry_id` + `bulgu_claim_id`) için bir satır, anahtarlar bu sırayla:
`{"entry_id","bulgu_claim_id","sonuc","aciklama","oneri"}`
- `sonuc` ∈ `dogru` | `hatali_duzeltme` | `eksik_kalan`.
- `aciklama`: kısa Türkçe gerekçe (kaynaktan birebir kısa alıntı içerebilir).
- `oneri`: `hatali_duzeltme`/`eksik_kalan` için karta konabilecek somut Türkçe düzeltme önerisi ("sen" hitabı ya da kişisiz); `dogru`da `""`.

## Dönüş (tek satır JSON)
`{"part":"<parça>","checked":N,"dogru":a,"hatali_duzeltme":b,"eksik_kalan":c}` — sayıları kendi dosyandan say.
