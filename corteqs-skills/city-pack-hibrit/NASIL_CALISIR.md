# city-pack-hibrit: nasıl çalışır (Barış için kısa not)

**Ne:** `city-pack`'in kopyası. Basit yazım işlerini Qwen yapar; araştırma, denetim, düzeltme ve son karar Claude'da. Asıl `city-pack` ve `city-audit` değişmedi.

**Kim ne yapar:** `references\isci_dagilimi.json`. Bir işi Claude'a geri vermek için o satırda `"qwen"` yerine `"claude"` yaz (şehir ortasında değil, şehirler arasında).

| Qwen | Claude |
|---|---|
| sözlük, mahalle, mekân, rota, bilgi kartı (yanıt) yazımı | kaynak bulma, mekân seçimi, "bugün açık mı", sayfa yazımı, tam denetim, editör, doğrulayıcı, fotoğraf, birleştirme |

**Qwen nasıl çağrılır:** `betikler\qwen_isci.py`. Qwen'e görev mesajını ve kaynak metinlerini tek istekte gönderir, cevabı kontrol edip yalnız izin verilen dosyalara yazar. Qwen dosya okuyamaz, internete çıkamaz, komut çalıştıramaz. Bozuk ya da izinsiz cevapta hiçbir dosya yazılmaz.

**Bir kez yapılacak:** Qwen API anahtarını kullanıcı ortam değişkeni olarak koy (PowerShell, bir kez):
```powershell
[Environment]::SetEnvironmentVariable('QWEN_API_KEY', '<anahtar>', 'User')
```
Varsayılan adres ve model: token planı, `qwen3.8-max` (`isci_dagilimi.json` → `qwen`). DashScope'u kullanacaksan `base_url`'i `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`, `model`'i ör. `qwen3.7-plus` yap; anahtar o hesabın anahtarı olur.

**Çalıştırma:** yeni oturumda `<şehir> hibrit` yaz (ör. `Valencia hibrit`). Yalnız şehir adı yazarsan eski `city-pack` çalışır.

**Ölçüm:** places fazından sonra `betikler\duzelt_orani.py` Claude denetiminin ilk turda "düzelt" dediği kart oranını role göre verir. Sonnet tabanı (Sevilla / Málaga): yanıt %59,5 / %77,0, mekân %67,9, mahalle %62,5 / %43,8, rota %91,7, sözlük %15,0 / %6,5. Qwen bir rolde tabandan 15 puandan fazla kötüyse o rol sonraki şehirde Claude'a döner.

**Testler:** `.venv\Scripts\python.exe -m pytest corteqs-skills\city-pack-hibrit\betikler -q` (API'ye gitmez).
