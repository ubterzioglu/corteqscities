# L1 alt ajan talimatları (Sevilla L1'den, 25.10.2026)

Bu klasördeki dosyalar şehirden bağımsızdır. Ana döngü bir dosyayı ajana vermeden önce yer tutucuları doldurur ya da görev mesajında açıkça değerini yazar:

| Yer tutucu | Değer |
|---|---|
| `<OUT>` | denetim klasörü (`ROOT\denetim\<city_id>_<YYYY-MM-DD>_<LEVEL>`) |
| `<SKILL>` | `ROOT\corteqs-skills\city-audit` |
| `<AGENTS>` | `ROOT\corteqs-skills\city-pack\agents` |
| `<ROOT>` | `C:\temp_private\corteqs\0000_newera` |
| `<Şehir>`, `<CITY-NNN>`, `<city_id>`, `<ülke>`, `<bölge>`, `<yerel_dil>` | şehrin değerleri |
| `<kontrol_tarihi>` | denetim günü (YYYY-MM-DD) |
| `<şehir merkezi enlem, boylam>` | `Şehir` sekmesindeki koordinat |
| `NN`, `<PAY>` | parti numarası, pay harfi |

Kısa görev mesajı kalıbı: `Görev talimatın şu dosyada: <SKILL>\agents\l1\<DOSYA> — onu oku ve aynen uygula. Yer tutucular: <OUT>=…, <Şehir>=…, … Senin partin: NN = 07. Geçici klasörün: <scratchpad>\<görev>_w\`

| Dosya | İş | Girdi hazırlayan | Çıktı |
|---|---|---|---|
| `ORTAK.md` | bütün ajanların ortak kuralları | — | — |
| `IDDIA_PROMPT.md` | iddia partisi (~11 kart) | `betikler\hazirla_l1.py` → `_iddia\girdi\parti_NN\` | `_iddia\parti_NN.jsonl`, `kart_NN.jsonl` |
| `ACIKMI_PROMPT.md` | açık-mı partisi (≤8 mekân) | `acik_mi_denetim orneklem` + `hazirla_l1.py` → `_acikmi_girdi\` | `_acikmi\parti_NN_dogrulama.jsonl` |
| `FOTO_PROMPT.md` | pafta incelemesi (iki pay) | L0 foto bloğu (`temas-sayfalari\`) | `_foto\photo-review_<PAY>.jsonl` |
| `MEKAN_PROMPT.md` | mekân kartları (iki pay) | `betikler\hazirla_l2.py` → `_l\girdi\mekan_<PAY>.jsonl` | `_l\mekan_<PAY>.jsonl` |
| `MAHALLE_ROTA_PROMPT.md` | mahalle + rota + K20 | `hazirla_l2.py` | `_l\mahalleler.jsonl`, `rotalar.jsonl`, `k20_gruplar.json` |
| `LISANS_PROMPT.md` | K71/K72 hak zinciri | `hazirla_l3.py` → `_l\girdi\lisans_zinciri.jsonl` | `_l\lisans.jsonl`, `lisans_ozet.json` |

Bağlantı + sayfa alanları ajanı (K51/K53/K90/K91) Sevilla'da ayrı talimat dosyası olmadan çalıştı; çıktı biçimi `_l\baglanti.jsonl` (`action_id, _row, entry_id, label, url, son_url, sayfa_basligi, K51, K53, K54, gozlem, alinti`) ve `_l\sehir_sayfa.jsonl` (`anahtar, deger_ozet, K91, kanit_url, alinti, bulgular`).

Sevilla ölçümü (32 ajan, Sonnet, en çok 5 eşzamanlı): iddia partisi ~210–310 K, açık-mı partisi ~100–160 K, foto payı ~130 K, mekân payı ~315–360 K, mahalle+rota ~270 K, lisans ~160 K alt ajan tokeni; toplam ~7 M.
