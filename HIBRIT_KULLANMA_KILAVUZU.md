# Hibrit şehir paketi: kullanma kılavuzu

*Son güncelleme: 31.10.2026 · skill: `corteqs-skills\city-pack-hibrit`*

Bu kılavuz, şehir paketini "Qwen yazar, Claude denetler" düzeniyle üretmeyi anlatır. Eski düzen (`city-pack`, her şeyi Claude yapar) aynen duruyor; ikisi yan yana kullanılabilir.

> **Durum:** Sistem kuruldu ve testleri geçiyor, ama Qwen'e henüz gerçek bir istek gönderilmedi. İlk kullanımda aşağıdaki "İlk deneme" adımlarını atlamadan yap.

---

## 1. Ne yapar, ne yapmaz

Şehir paketinde iki tür iş var: **yazmak** ve **doğruluğunu kontrol edip düzeltmek**. Hibrit düzende basit yazım Qwen'e gider, geri kalan her şey Claude'da kalır.

| İş | Kim yapar |
|---|---|
| Sözlük (60 terim) | Qwen |
| Mahalleler (16) | Qwen |
| Mekân kartları (120) | Qwen |
| Rotalar (12) | Qwen |
| Bilgi kartları / yanıtlar (12 konu, ~240 kart) | Qwen |
| Kaynak bulma, mekân seçimi, "bugün açık mı" kontrolü | Claude |
| Şehir sayfası (Şehir + SayfaAlanları) | Claude |
| Her kartın tam denetimi, editör, doğrulayıcı | Claude |
| Fotoğraf seçimi ve inceleme | Claude |
| Birleştirme, Excel, kapılar, teslim | Script + Claude |

**Önemli:** Qwen'in yazdığı her kart, Sonnet'in yazdığı gibi aynı script kapılarından ve aynı **tam** Claude denetiminden geçer. Hibrit hiçbir kontrolü atlatmaz; yalnız ilk taslağı kimin yazdığı değişir.

**Qwen'in yapamadıkları** (bilerek kapalı):
- dosya okuyamaz, internete çıkamaz, komut çalıştıramaz;
- yeni kaynak ekleyemez: verilen kaynaklarda olmayan bilgiyi "eksik" listesine yazar, Claude tamamlar;
- izin verilmeyen bir dosyaya yazamaz: cevabında tek bir izinsiz dosya bile varsa **hiçbir dosya yazılmaz**.

---

## 2. Bir kez yapılacak kurulum

### 2.1 Qwen API anahtarını kaydet

PowerShell'i aç ve bir kez çalıştır (anahtarı kendi Qwen hesabından al):

```powershell
[Environment]::SetEnvironmentVariable('QWEN_API_KEY', '<anahtarın>', 'User')
```

Sonra **VS Code'u tamamen kapatıp yeniden aç** (yeni ortam değişkenini ancak öyle görür). Kontrol:

```powershell
if ($env:QWEN_API_KEY) { 'anahtar var' } else { 'anahtar YOK' }
```

Anahtar hiçbir dosyaya yazılmaz; yalnız bu ortam değişkeninden okunur.

### 2.2 Hangi Qwen hesabı ve modeli

Ayar dosyası: `corteqs-skills\city-pack-hibrit\references\isci_dagilimi.json` → `"qwen"` bölümü.

| Seçenek | `base_url` | `model` |
|---|---|---|
| **Token planı** (varsayılan) | `https://token-plan.maas.qwencloudapi.com/compatible-mode/v1` | `qwen3.8-max` |
| DashScope, kullandıkça öde | `https://dashscope-intl.aliyuncs.com/compatible-mode/v1` | `qwen3.7-plus` |

Anahtar hangi hesaba aitse o adresi kullan. İş yerinin (adesso) yapay zekâ merkezini bu iş için kullanma.

Öteki ayarlar (genelde dokunmana gerek yok):

| Ayar | Anlamı | Varsayılan |
|---|---|---|
| `max_tokens` | Qwen'in tek cevapta yazabileceği en fazla uzunluk | 32000 |
| `zaman_asimi_sn` | Tek isteğin bekleme süresi | 900 (15 dk) |
| `eszamanli` | Aynı anda en çok kaç Qwen işi | 4 |
| `temperature` | Yaratıcılık (düşük = daha tutarlı) | 0.3 |

### 2.3 Kurulumu sına (API'ye gitmez, ücretsiz)

```powershell
C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe -m pytest C:\temp_private\corteqs\0000_newera\corteqs-skills\city-pack-hibrit\betikler -q -p no:cacheprovider
```

Beklenen: `13 passed`.

---

## 3. İlk deneme (ilk gerçek şehirden önce bir kez)

Tam şehre başlamadan önce Qwen'in gerçekten cevap verdiğini ve Türkçesinin nasıl olduğunu küçük bir işte gör. Yeni bir Claude oturumunda şunu yazman yeterli:

> Hibrit için ilk denemeyi yap: Qwen'e sözlükten 10 terimlik küçük bir görev ver, sonucu göster. Málaga dosyalarına yazma, çıktıyı geçici klasöre al.

Claude şunlara bakıp sana özetler: istek gitti mi, cevap biçimi doğru mu, Türkçe ve "sen" hitabı nasıl, alıntılar kaynakla birebir tutuyor mu, kaç token harcadı. Sonuç iyi değilse tam şehre geçmeden konuşuruz.

---

## 4. Bir şehri hibrit üretmek

Yeni bir Claude oturumunda yalnız şunu yaz:

```
Valencia hibrit
```

- **"hibrit" kelimesi şart.** Yalnız `Valencia` yazarsan eski düzen (`city-pack`, her şey Claude) çalışır.
- Gerisi eski düzenle aynı: Claude şehri tanır, şablonu hazırlar, fazları sırayla yürütür, her adımda bir iki cümle durum yazar, karar gerekirse tek öneriyle sorar.
- Şehrin klasörü aynı yerde açılır: `uretim\<şehir>\`.

### Üretim sırasında neler olur

1. **intake / sources:** Claude kaynakları bulur ve indirir. Rol dağılımı `uretim\<şehir>\_is\isci_dagilimi.json`'a kopyalanır; şehir bitene kadar bu kopya geçerlidir.
2. **answers (bilgi kartları):** Claude her konu için görev mesajını hazırlar, Qwen kartları yazar (aynı anda en çok 4 konu). Sonra script kapıları → Claude tam denetim → Claude editör → Claude doğrulayıcı.
3. **places (mekân, mahalle, sözlük, rota):** mekân seçimini Claude yapar, yazımı Qwen; sonra yine aynı denetim zinciri.
4. **photos, assemble, deliver:** eskisi gibi, Claude.

### Qwen hata verirse ne olur (kendiliğinden)

| Durum | Ne yapılır |
|---|---|
| Qwen'in cevabı bozuk ya da yarım | Hata notuyla Qwen'e **bir kez** daha verilir |
| İkinci kez de olmadı | Aynı iş Claude'a (Sonnet) geçer, not düşülür |
| Script kapısı Qwen'in kartlarında sorun buldu | Sorunlu satırlar Qwen'e bir kez geri döner; düzelmezse Claude editörü düzeltir |
| Cevap uzunluk sınırında kesildi | Konu ikiye bölünüp yeniden verilir |

Senin bir şey yapman gerekmez; yalnız rapor bunları söyler.

---

## 5. Nereden takip edersin

| Ne görmek istiyorsun | Nereye bak |
|---|---|
| Qwen her görevde ne döndü, kaç token harcadı, ne kadar sürdü | `uretim\<şehir>\_is\qwen\<görev>.donus.json` |
| Qwen'in ham cevabı (sorun olursa) | `uretim\<şehir>\_is\qwen\<görev>.ham.txt` |
| Claude'a gönderilen görev mesajı | `uretim\<şehir>\_is\qwen\<görev>.mesaj.md` |
| Skill ile ilgili notlar, Qwen'den Claude'a geçen işler | `uretim\<şehir>\_is\notlar_skill.md` |
| Qwen ne kadar iyi yazdı (aşağıda) | `uretim\<şehir>\_is\qwen\duzelt_orani.json` |

---

## 6. Qwen iyi mi yazıyor? Ölçüm

places fazı bitince Claude şu ölçümü çalıştırır (istersen sen de çalıştırabilirsin):

```powershell
C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe C:\temp_private\corteqs\0000_newera\corteqs-skills\city-pack-hibrit\betikler\duzelt_orani.py C:\temp_private\corteqs\0000_newera\uretim\<şehir>\_is\denetim
```

Bu, Claude denetiminin **ilk turda "düzelt" dediği kartların yüzdesini** rol başına verir. Düşük = iyi. Karşılaştırma tabanı, Sonnet'in yazdığı şehirler:

| Rol | Sevilla | Málaga |
|---|---|---|
| Bilgi kartı (yanıt) | %59,5 | %77,0 |
| Mekân | %67,9 | – |
| Mahalle | %62,5 | %43,8 |
| Rota | %91,7 | – |
| Sözlük | %15,0 | %6,5 |

**Kural:** Qwen bir rolde iki tabanın kötüsünden **15 puandan fazla** kötüyse, o rol sonraki şehirde Claude'a döner. Claude bunu şehir sonu raporunda öneri olarak söyler; şehir ortasında değiştirilmez.

---

## 7. Bir işi Qwen'den Claude'a (ya da tersine) almak

`corteqs-skills\city-pack-hibrit\references\isci_dagilimi.json` dosyasında, `"roller"` altında ilgili satırı değiştir:

```json
"yanit-yazari": "claude",
```

- `"qwen"` = Qwen yazar, `"claude"` = Claude (Sonnet) yazar.
- **Yalnız şehirler arasında değiştir.** Süren bir şehir kendi kopyasını (`uretim\<şehir>\_is\isci_dagilimi.json`) kullanır; ana dosyadaki değişiklik bir sonraki şehirde geçerli olur.
- Denetim rollerini (`iddia-denetcisi`, `editor`, `dogrulayici`) `"qwen"` yapma; sistem bunlar için Qwen çağrısı içermez.

Hibriti tamamen bırakmak istersen: şehir adını "hibrit" demeden yaz; eski `city-pack` çalışır.

### Asıl skill (`city-pack`) değişince

Hibrit bir kopya olduğu için asıl skill'e eklenen dersler kendiliğinden gelmez. Her hibrit şehirden önce (üretim sürerken değil) şunu çalıştır ya da Claude'a "hibriti eşitle" de:

```powershell
C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe C:\temp_private\corteqs\0000_newera\corteqs-skills\city-pack-hibrit\betikler\esitle.py
```

Asıl skill'in güncel halini alır, hibrit eklerini üstüne yeniden koyar. `"skill_degisti": false` = zaten eşit. Çıkış 1 = asıl skill'de hibritin bağlandığı bir satır değişmiş; Claude'a göster, script'teki eşleşme güncellenir.

---

## 8. Sorun giderme

| Belirti | Neden | Çözüm |
|---|---|---|
| `API anahtari yok: ortam degiskeni QWEN_API_KEY` | Anahtar kayıtlı değil ya da VS Code yeniden açılmadı | 2.1'i yap, VS Code'u kapatıp aç |
| `HTTP 401` / `HTTP 403` | Anahtar yanlış ya da başka hesabın adresi | Anahtarın ait olduğu hesabın `base_url`'ini yaz (2.2) |
| `HTTP 429` | Qwen kotası / hız sınırı | Script 30 sn ve 90 sn bekleyip kendisi tekrar dener; sürerse `eszamanli`'yı 2'ye indir |
| `HTTP 404` ya da model bulunamadı | Model adı o hesapta yok | `model`'i hesabındaki adla değiştir |
| `yanit max_tokens sinirinda kesildi` | Konu tek cevaba sığmadı | Claude konuyu böler; sık oluyorsa `max_tokens`'ı artır |
| `girdi cok buyuk` | Kaynak metinleri 600 bin karakteri aştı | Claude parçayı böler (kaynak metni kırpılmaz) |
| `izinsiz_yol` / `dosya_var` | Qwen yanlış dosyaya yazmak istedi ya da dosya zaten var | Hiçbir şey yazılmadı; Claude görevi düzeltip tekrar verir |
| Qwen çok fazla "eksik" bildiriyor | Kaynaklar o bilgiyi içermiyor | Normal; Claude'un tamamlama turu kapatır |

Çıkış kodları (script'in son satırı tek satır JSON'dur):
- **0:** dosyalar yazıldı;
- **1:** Qwen'in cevabı kullanılamadı, hiçbir dosya yazılmadı;
- **2:** komut ya da ayar hatası.

---

## 9. Yapılmaması gerekenler

- **Kilo Code içinde bu skill'i çalıştırma.** Projedeki `kilo.json` `corteqs-skills` klasörünü Kilo'ya da tanıtıyor, yani Kilo `city-pack-hibrit`'i görür. Ama bu skill Claude'un ana akışı için yazıldı: Claude yönetir, Qwen'i script'le çağırır. Kilo'da çalıştırırsan denetimi de Qwen yapmaya çalışır.
- `kilo run --auto` ile Qwen'e iş verme: Qwen'e komut çalıştırma dahil sınırsız yetki verir. Script yolu bunun için var.
- Üretim sürerken skill dosyalarını (`SKILL.md`, `agents\`, `betikler\`, `isci_dagilimi.json`) değiştirme. Görülen sorun `notlar_skill.md`'ye yazılır, şehir bitince düzeltilir.
- Qwen'in yazdığı dosyaları elle "onaylı" yapma; onay yalnız `city-audit`'in yeni oturumdaki kararıdır.

---

## 10. Dosya haritası

```
corteqs-skills\city-pack-hibrit\
├─ SKILL.md                         Claude'un talimatı (başta "Hibrit iş bölümü")
├─ NASIL_CALISIR.md                 1 sayfalık özet
├─ references\isci_dagilimi.json    kim ne yapar + Qwen ayarları
├─ agents\qwen-ek-kurallar.md       Qwen'e özel kurallar (ortak kuralların önüne eklenir)
├─ agents\...                       öteki rol talimatları (city-pack'ten kopya)
└─ betikler\
   ├─ qwen_isci.py                  Qwen'i çağırır, cevabı denetleyip dosyaya yazar
   ├─ duzelt_orani.py               Qwen'in yazım kalitesini ölçer
   └─ test_qwen_isci.py             testler (API'ye gitmez)

.claude\skills\city-pack-hibrit     → yukarıdaki klasöre kısayol
CLAUDE.md                           "<şehir> hibrit" kuralı (madde 4)
```

**Ek not (Kilo komut satırı):** Kilo'nun komut satırı aracı şu an `C:\Users\baris-terzioglu\.config\kilo\kilo.jsonc` dosyasını geçersiz sayıyor. Sebepleri: 5 Qwen modelinde `"modalities"` içinde `"output": ["text"]` eksik, ayrıca `web_search` ve `indexing` anahtarlarını tanımıyor. Hibrit sistem Kilo'yu kullanmadığı için bu onu etkilemiyor. VS Code eklentisi de çalışıyor. Yalnız `kilo` komutunu terminalde kullanmak istersen o dosyanın düzeltilmesi gerekir.
