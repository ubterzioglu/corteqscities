# Mekân ek seçim turu — Sevilla (CITY-107)

Kurallar `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\SECIM_GOREV.md` ile aynı (oku). Bu turdaki fark: **kanıtı bizim aracımızla sınayacaksın.**

## Neden
İlk turda 19 mekânın adres ifadesi ajanın kendi indirmesinde vardı ama bizim temiz metin kopyamızda yoktu (adres alt bilgide ya da JS'de; çoğu ana sayfa). Bizim araç yalnız sayfanın **ana metnini** (menü/alt bilgi atılmış) arar.

## Doğrulama (her aday için ZORUNLU)
Adaylarını `<TMP>\aday.jsonl` dosyasına yaz (`{"url": "...", "must_contain": ["..."]}`), sonra:
```powershell
$env:PYTHONDONTWRITEBYTECODE='1'; $env:PYTHONUTF8='1'
& 'C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe' 'C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts\fetch_snapshot.py' --urls <TMP>\urls.txt --must-contain <TMP>\aday.jsonl --out-dir <TMP>\snap --cache-dir 'C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\cache'
```
(`urls.txt` = satır başına bir URL.) Sonra `<TMP>\snap\index.jsonl`'de her satırın `evidence` alanına bak: ifadesi bulunmayan, `thin_text` ya da `soft_404` olan adayı çıkar ya da başka sayfa/ifade dene. Çıktı dosyasına **yalnız bu kontrolden geçenleri** yaz. Gerekirse ifadeyi `<TMP>\snap` içindeki `.txt` temiz metinden birebir kopyala.

İpucu: Turismo de Sevilla (`visitasevilla.es`) mekân sayfalarında adres gövde metninde geçiyor ve ilk turda çoğu geçti; ana sayfa yerine mekânın kendi sitesinde "contacto/cómo llegar/visita" sayfası dene.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız `<TMP>`'de. Bütçe **40 dakika / 120 araç çağrısı**. Slug'lar `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\selected.jsonl` ve `...\data\Yanıtlar.jsonl` ile çakışmasın; aynı mekânı iki kez önerme (`selected.jsonl`'de olan mekânlar zaten seçili — `reddedilen.jsonl`'dekiler hariç).

## Dönüş
Tek satır JSON: `{"duzeltilen":<n>,"yeni":{"<grup>":<n>},"gaps":[...]}`
