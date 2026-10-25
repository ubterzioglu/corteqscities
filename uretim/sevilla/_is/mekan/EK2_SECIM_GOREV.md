# Mekân ek seçim turu 2 (düzeltme turu, 2026-10-25) — Sevilla (CITY-107)

Kurallar `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\SECIM_GOREV.md` ve `EK_SECIM_GOREV.md` ile aynı (ikisini de oku). Metin yazmıyorsun; mekân seçip resmî kaynak adresi ve kanıt ifadesi buluyorsun.

## Neden
Bağımsız denetim pakette 100 mekân saydı; hedef 120. Spor 5, Çocuklarla keşif 7, Yeme ve içme 8, Sanat 10, Müzeler 12, Sahne 12 zayıf; Tarih ve mimari 32 (toplamın %35'ini aşmamalı: 120'de en çok 42).

## Aday havuzu (önce buradan)
`C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\ek2_aday_havuz.json`: Wikidata'da **fotoğrafı olan**, kutu içindeki, henüz seçilmemiş adaylar (`qid, name, lat, lon, types, website, commons_category, group_guess`). Fotoğraflı aday öncelikli (fotoğrafsız kalacak yer seçme). `group_guess` tahmindir; doğru grubu sen yaz.
Önceki turda kanıtı doğrulanıp paket dışı kalan 5 aday (adres ifadesi sayfada bulunmuştu; yeniden sına): Fundación Cajasol – Sala Murillo (`https://fundacioncajasol.com/salas/`, "Sala Murillo Acceso por c/ Chicarreros, nº 1"), CICUS (`https://cicus.us.es/visitas-guiadas-expo-escuela`, "C/ Madre de Dios, nº 1"), Espacio Eslava (`https://espacioeslava.com/contacto/`, "CALLE ESLAVA Nº 3"), Museo del Sevilla FC / Stadium Tour (`https://visitasevilla.es/sevilla-fc-stadium-club-tour/`, "Calle Sevilla Fútbol Club, s/n, 41005 Sevilla"; pakette `estadio-sanchez-pizjuan-tur` var — aynı tesis mi bak, aynıysa önerme), Castillo de San Jorge (`https://visitasevilla.es/castillo-de-san-jorge/`, "Plaza del Altozano, s/n, 41010 Sevilla"; Mercado de Triana pakette var, kale ayrı ziyaret yeri — Wikidata Q5757560).
Havuzda olmayan mekânı da önerebilirsin (Spor/Çocuk/Yeme'de gerekecek): gerçek, kalıcı, şehre özgü; zincir yok; kapanmış/geçici yok.

## Zorunlu doğrulama (her aday)
`EK_SECIM_GOREV.md`'deki `fetch_snapshot --urls ... --must-contain ...` yöntemi: ifade bizim temiz kopyamızda geçmeli; `thin_text`/`soft_404`/kanıtsız aday çıkarılır. Kaynak sırası: (1) mekânın kendi resmî sitesinde adres/ziyaret veren derin sayfa; (2) yoksa IAPH `guiadigital.iaph.es`, Junta müze/anıt sayfası, `museosdeandalucia.es`, Diputación `dipusevilla.es`, Üniversite (`us.es`) ya da `visitasevilla.es` mekân sayfası (belediye turizm konsorsiyumu; belediye sitesi erişilemez). Blog, TripAdvisor, ticari rehber, Wikipedia yok. Erişilemez: sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es (yan kapı, kullanma).

## Çakışma
Pakette olan mekânları yeniden önerme: `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\data\Mekânlar.jsonl` (`slug`, `title`) ve `..\_is\mekan\selected.jsonl` + `selected_ek.jsonl`. Aynı tesisin salonu/duvarı/ayrı açısı ayrı mekân değildir (K108). `slug` paket genelinde benzersiz (`..\_is\data\Yanıtlar.jsonl` ve `Mahalleler.jsonl` dahil).

## Çıktı
`C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\mekan\secim_<harf>.jsonl` (görev mesajındaki harf), satır: `{"url","must_contain":["..."],"publisher","why","name","group","qid","lat","lon","district","setting","slug","entry_id","commons_category","note"}`. `lat`/`lon` yalnız Wikidata'dan (havuzdaki değer ya da öğenin P625'i); yoksa boş. UTF-8, BOM'suz, Python ile yaz.

## Sınırlar
**Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>`'de. Bütçe **35 dakika / 110 araç çağrısı**; dolunca bulduklarınla dön, eksik grubu `gaps`'e yaz. Kontenjana ulaşamazsan uydurma, eksik bırak.

## Dönüş
Tek satır JSON: `{"groups":{"<grup>":<sayı>},"photo_share":<fotoğraflı oranı>,"rejected":<doğrulamadan geçmeyen>,"gaps":[...]}`
