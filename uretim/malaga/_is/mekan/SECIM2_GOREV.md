# Mekân seçimi 2. tur — Málaga (ek kurallar)

1. turda 100 mekân seçildi, 88'inin resmî sayfası bizim kopyamızda kanıtla kabul edildi. Hedef 120 mekân. Bu turda eksik grupları tamamlıyorsun. `SECIM_GOREV.md`'deki bütün seçim kuralları (1–9) geçerli; aşağıdakiler onu değiştirir ya da ekler.

## Neyi seçme
- Zaten seçilmiş mekânlar: `<WORK>\_is\mekan\secim_durum.jsonl` (her satır: slug, group, name, url, source_id, ret). `source_id` dolu olanlar KABUL edildi — bunları tekrar seçme. `source_id` boş olanlar REDDEDİLDİ (`ret` nedeni yazılı): senin grubundaysa önce bunları kurtarmayı dene (aynı mekânın başka derin sayfası ya da sayfada birebir geçen başka ifade).
- Başka 2. tur ajanının grubundaki mekânı seçme.

## Yeni: kaynağı sen doğrularsın (add_sources)
Her aday için sayfanın BİZİM kopyamızda kanıt ifadesiyle kabul edildiğini kendin gör:
1. Adayları `<TMP>\aday_<k>.jsonl` dosyasına yaz (k = 1, 2, 3 …; satır biçimi `SECIM_GOREV.md` Çıktı bölümündeki gibi; `title`, `publisher`, `lang`, `why` zorunlu). 3–6 adayı bir dosyada topla.
2. Çalıştır (tek komut, PowerShell):
   `& '<PY>' -X utf8 '<TK>\add_sources.py' '<WORK>\_is' --candidates '<TMP>\aday_<k>.jsonl' --subdir <SNAP>-<k> --topic kesif --city-id malaga`
   Her koşuda YENİ klasör (`<SNAP>-1`, `<SNAP>-2` …); önce Test-Path ile bak, varsa k'yi artır.
3. Sonucu oku: `<WORK>\_is\<SNAP>-<k>\eklenen.json` → `map` (url → source_id) kabul; `rejected` (url, neden). Reddedilen için: "kopya yok/ince" → sayfa JS ile yükleniyor, başka sayfa dene; "kanit metinde yok" → `must_contain` ifaden bizim kopyada yok; aynı sayfayı yeni klasörde, sayfada birebir geçen başka ifadeyle (ör. yalnız posta kodlu satır ya da sokak adı) dene. Bir mekân için en çok 3 deneme; sonra bırak, `gaps`'e yaz.
4. Kabul edilen her mekânı çıktı dosyana `source_id` alanıyla birlikte yaz.

## Ek kaynak izinleri (yalnız mekânın kendi sitesi yoksa ya da sitesi okunamıyorsa)
- Belediye çarşıları: `malaga.eu` altındaki çarşı/mercado sayfası (Área de Comercio).
- Belediye müze ve kültür merkezleri: `malaga.eu` ya da belediye kültür alanı sayfası.
- Kiliseler: piskoposluk parish sayfası (adres satırı kopyada geçmeli).
- Liman alanları (Muelle Uno, La Farola): `puertomalaga.com` sayfası.
- Spor tesisleri: belediye spor alanının (`deporte.malaga.eu`) ya da işletmecinin sayfası.
- Endülüs bölge kurumu tesisleri: `juntadeandalucia.es` / `museosdeandalucia.es`.
Turizm portalı, Wikipedia, TripAdvisor ve rezervasyon siteleri yine kaynak OLMAZ.

## Çıktı
`<WORK>\_is\mekan\secim2_<n>.jsonl` — YALNIZ kabul edilen mekânlar; satır `SECIM_GOREV.md` biçiminde + `"source_id":"malaga:kaynak:NNN"` + `"rol":"ana"`. Write aracıyla ya da `<TMP>`'deki bir .py dosyasıyla yaz (UTF-8, satır başına bir JSON); her kabul edilen 3 mekânda bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz.

## Komut kuralı
cd yok, Bash yok. Komutları PowerShell aracıyla, her çağrıda TEK komut, tam yolla çalıştır (bileşik komut yok). Python gerekirse önce `.py` dosyasını `<TMP>`'ye yaz, sonra `& '<PY>' -I -X utf8 '<dosya>'`; `python -c` ve heredoc yok. Dosyaları Read/Glob/Grep ile oku. `<TMP>` klasörünü ilk iş `New-Item -ItemType Directory -Force` ile oluştur. Alt ajan başlatma. Bir komut 3 dakikadan uzun yanıtsız kalırsa bekleme, o adayı `gaps`'e yaz.
