# Almanya ulusal paketi — editör görevi (ortak metin)

Sen bağımsız denetim raporundaki bulguları kartlara uyguluyorsun. Görev mesajı konuyu/konuları, rapor dosyasını ve yedek klasör adını verir.

Oku: `C:\temp_private\corteqs\0000_newera\ulke\DE\_is\yazar\YAZAR_GOREV.md` (yazar kuralları sana da uygulanır; içindeki 4 dosyayı da oku), sonra denetim raporunu.

## Adımlar
1. Başlamadan yedek: `C:\temp_private\corteqs\0000_newera\ulke\DE\_is\yazar\out\<konu>\` klasörünü `…\out\<yedek_adi>\<konu>\` altına kopyala (görev mesajındaki ad).
2. Her bulgu için karar: **uygula** (kaynak metni destekliyorsa), **sil** (iddia kaynakta yoksa cümleyi/claim'i çıkar), ya da **uygulanamaz** (nedenini yaz: ör. kaynak sınırı, kaynak yok). Yeni bilgi eklemek için yeni kaynak gerekiyorsa: yalnız **ciddi** ve **orta** bulgular için, raporun gösterdiği resmî sayfayı `add_sources` ile ekleyebilirsin (ortak kurallar §4 komutu; `--subdir snap_<konu>-editor<sira>`, `--topic <konu>`, `--city-id de`, `--cache-dir C:\temp_private\corteqs\0000_newera\ulke\DE\_is\cache`; `<sira>` için önce klasörün var olup olmadığına bak). Kart başına 2 kaynak sınırı korunur: gerekirse kartın daha az kullanılan kaynağını çıkar ve ona dayanan claim'leri yeni kaynaktan yeniden kur ya da sil. Kaynak eklenemiyorsa "uygulanamaz, kaynak gerekir" yaz. Küçük bulgu için kaynak eklenmez. Yalnız kart kaynaklarının `text_file` metninden yaz.
3. Kartı değiştirince claims ve Bağlantılar dosyasını da uyumlu tut: yeni sayı/kural → yeni claim (quote birebir); silinen cümle → claim'i sil. `valid_until.json`'u güncelle.
4. Değişiklik kaydı: `C:\temp_private\corteqs\0000_newera\ulke\DE\_is\yazar\out\<degisiklik_dosyasi>.jsonl` — satır: `{"topic":"…","slug":"…","severity":"ciddi|orta|küçük","finding":"…","action":"uygulandı|silindi|uygulanamaz","note":"…"}`.
5. Bitirmeden `pack_check` çıkış 0 olana dek:
```powershell
$env:PYTHONUTF8='1'; $env:PYTHONDONTWRITEBYTECODE='1'
& C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe -X utf8 C:\temp_private\corteqs\0000_newera\corteqs-skills\deneme_ulke_paketi\pack_check.py C:\temp_private\corteqs\0000_newera\ulke\DE\_is <konu>
```
6. Slug'ları değiştirme (paket kimliği kayar). Dosyaları Python ile yaz (UTF-8, `ensure_ascii=False`). Alt ajan başlatma. Bütçe: en çok 40 dakika / konu.

## Dönüş (tek satır JSON)
`{"topic":"<konu>","applied":a,"deleted":d,"not_applicable":n,"pack_check":0|1,"notes":["..."]}`
