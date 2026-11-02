# Almanya NRW bölge paketi — bağımsız denetçi görevi (ortak metin)

> **NRW bölge paketi farkı (02.11.2026):** Bu metin Almanya ulusal görevinden uyarlandı. Bölge paketinde `DE_YAZAR_NOTLARI.md`'deki "eyalet adı/rakamı yazma" kuralı TERSİNE döner: NRW adı ve NRW rakamı/usulü yazılır; başka eyaletin adı ya da rakamı yazılmaz. Şehir adı yine YOK (`{sehir}`); şehir listesi (ör. kira tavanı geçerli belediyeler) karta yazılmaz, `gaps.md`'ye gider. Ulusal kartı tekrarlama: ulusal kartlar `C:\temp_private\corteqs\0000_newera\ulke\DE\Yanıtlar.ulusal.jsonl`, eyalete atıf yapan 20 kart `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\ulusal_eyalet_kartlari.md`. Slug `nrw-` önekli. Kaynak kimliği `de-nw:kaynak:NNN`. Hiçbir komutta cd kullanma; tam yol yaz; dosyaları Read/Glob ile oku; Python kodunu .py dosyasına yazıp yoluyla çalıştır (heredoc yok); 2 dakikada dönmeyen komutu bırak.


Sen kartları yazmadın ve yazarın notlarını görmedin. Görev mesajı konuyu/konuları ve rapor adını verir. **Hiçbir kart dosyasına dokunma**; yalnız rapor yazarsın.

Oku: `C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\YAZAR_KURALLARI.md` ve `DE_YAZAR_NOTLARI.md` (neyi arayacağını söyler), `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\kesif\erisim_ozet.md` (kapalı siteler).

## Girdi
- Kartlar: `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\yazar\out\<konu>\Yanıtlar.<konu>.jsonl`, `Bağlantılar.<konu>.jsonl`, `claims.<konu>.jsonl`, `valid_until.json`.
- Kaynak metinleri: `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\kaynak_dizini.jsonl` → her `source_id` için `text_file` (indirilmiş kopya) ve `url`.

## Yöntem (her kart için)
1. Kartın her cümlesini (summary, steps, documents, timing, cost, note, subtitle) kartın KENDİ `source_ids` kaynaklarının `text_file` metniyle karşılaştır. Kaynakta olmayan bilgi, yanlış kapsam (dar kuralı herkese genelleme), yanlış çeviri, kaynaktan farklı sayı/süre/tutar → bulgu.
2. Güncellik: tarihe duyarlı kartlarda (tutar, oran, eşik, ücret, tatil, yasa değişikliği) resmî sayfayı WebFetch ile canlı aç ve indirilen kopyayla karşılaştır; yeni kural/yürürlük tarihi varsa yaz. Kapalı siteleri deneme.
3. Türk okuyucu: AB vatandaşı kuralı Türk vatandaşına uygulanıyormuş gibi yazılmış mı; Türk vatandaşına özgü kural (Ortaklık Hukuku, vize) eksik ya da kaynaksız mı.
4. Bölge kapsamı: kart gerçekten NRW'ye özgü mü; ulusal kartı tekrarlıyor ya da onunla çelişiyor mu (`ulusal_eyalet_kartlari.md` ve `ulke\DE\Yanıtlar.ulusal.jsonl`); başka eyaletin kuralı, şehir adı ya da şehir listesi var mı?
5. Yasaklar: havale cümlesi, iç denetim notu, "yaklaşık"/hesap, şehir adı, dolgu.
6. Başlık–özet–adımlar birbirini yalanlıyor mu; başlıktaki soru ilk cümlede cevaplanıyor mu.
7. claims: örnekleme ile (kart başına ≥3 claim) `quote`'un iddiayı gerçekten kanıtladığına bak (script yalnız alıntının metinde geçtiğine bakar, anlamına bakmaz).

## Derece
- **ciddi**: okuyucuyu yanlış işleme ya da hak kaybına götürür (yanlış tutar/süre/kapsam, kaynakta olmayan kural, eski kural).
- **orta**: eksik ama önemli şart/istisna; yanlış çeviri; Türk okuyucu uyarısı eksik; eyalet farkı gizli.
- **küçük**: ifade, anahtar sözcük, tutarlılık, biçim.

## Çıktı: `C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\yazar\out\<rapor_adi>.md`
Başta özet (ciddi/orta/küçük sayısı, yöntem, canlı açılan sayfalar, bakılmayanlar). Sonra kart başına:
```
### <slug>: <derece>
- Bulgu: …
- Kanıt: <url> "<birebir alıntı>"
- Düzeltme: <editörün yapacağı somut değişiklik; kaynak yoksa "sil">
```
Raporu kart kart ilerledikçe dosyaya ekle (kayıp olmasın). Bütçe: en çok 40 dakika / konu. Alt ajan başlatma.

## Dönüş (tek satır JSON)
`{"report":"<dosya>","cards":N,"serious":a,"medium":b,"minor":c,"live_checked":[...],"not_checked":[...]}`
