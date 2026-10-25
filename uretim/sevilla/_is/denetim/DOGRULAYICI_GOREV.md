# Bağımsız doğrulayıcı + ek kart denetimi — Sevilla (CITY-107)

Kartları sen yazmadın, denetlemedin, düzeltmedin. İki işin var. **Yalnız verilen dosyaları oku; internete çıkma (WebFetch/WebSearch yok); hiçbir dosyayı değiştirme** (yalnız aşağıdaki çıktı dosyalarını yaz). Alt ajan başlatma.

Yollar: `<WORK>` = `C:\temp_private\corteqs\0000_newera\uretim\sevilla`; kaynak metinleri `<WORK>\_is\kaynak_dizini.jsonl` → `text_file`.

## İş 1 — Doğrulama (her `<konu>` için)
Girdi: `<WORK>\_is\denetim\<konu>_iddia.jsonl` (denetçi bulguları), `<konu>_degisiklik.jsonl` (editörün değişiklik kaydı: `entry_id, alan, eski, yeni, bulgu_claim_id, gerekce, alinti`), güncel kart dosyası `<WORK>\_is\data\parcalar\Yanıtlar.<konu>.jsonl` (kartın şimdiki hâli).
- Her değişiklik satırını kaynak metniyle karşılaştır: kaynakla tutarlı mı, bulguyu kapatıyor mu, yeni yanlış/genelleme eklemiş mi? `alinti` kaynakta birebir geçiyor mu?
- Değişiklik kaydı olmayan "doğru dışı" bulgu var mı (bulgunun `claim_id`'si hiçbir satırın `bulgu_claim_id`'sinde yoksa) → `eksik_kalan`.
- Reddedilen bulgularda (`yeni` = "") gerekçe kaynakla tutarlı mı?
- Okura "sen" hitabı; değişen metinde "siz" biçimi varsa `hatali_duzeltme`.

Çıktı `<WORK>\_is\denetim\<konu>_dogrulama.jsonl`, satır: `{"entry_id","bulgu_claim_id","sonuc","aciklama","oneri"}`; `sonuc` ∈ `dogru` | `hatali_duzeltme` | `eksik_kalan`. Her değişiklik satırı (aynı bulgu için birden çok satır varsa bulgu başına bir satır yeter) ve her eksik bulgu için bir satır.

## İş 2 — Ek kart denetimi (yalnız görev mesajında `-ek` verilen konular)
Girdi: `<WORK>\_is\denetim\<konu>-ek_kartlar.jsonl` (editörün eklediği kartlar, `sources[].text_file` ile) ve `<WORK>\_is\claims\<konu>.jsonl` (o kartların defter satırları).
Yöntem ve çıktı biçimi `<WORK>\_is\denetim\DENETCI_GOREV.md` ile aynı (kural ve anlam odağı, kart başına 2–4 iddia). Çıktılar: `<konu>-ek_iddia.jsonl`, `<konu>-ek_karar.jsonl`.

Bütçe 40 dakika. Dosyaları Python ile yaz (UTF-8, satır başına bir JSON).

## Dönüş (tek satır JSON; dosyadan say)
`{"dogrulama":{"<konu>":{"satir":N,"dogru":a,"hatali_duzeltme":b,"eksik_kalan":c}},"ek":{"<konu>":{"cards":N,"claims":M,"dogru":a,"duzelt_kart":b,"ciddi":c,"orta":d,"hafif":e}}}`
