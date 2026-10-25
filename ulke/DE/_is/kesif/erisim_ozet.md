# Almanya ulusal paketi — erişim yoklaması (25.10.2026)

75 resmî adres `fetch_snapshot` ile bu ağdan denendi (`erisim_snap\index.jsonl`, `erisim_snap_2\index.jsonl`). Kural: kapalı alan adı aşılmaz (sertifika doğrulaması kapatılmaz, tarayıcı taklidi yapılmaz); bilgi başka resmî sayfadan bulunur ya da `gaps`'e yazılır.

## Açık (indirme ve kanıt ölçümü çalışır)
gesetze-im-internet.de, bamf.de, tuerkei.diplo.de, bzst.de, elster.de, bafin.de, arbeitsagentur.de, bmas.de, anerkennung-in-deutschland.de, kba.de, bundesgesundheitsministerium.de, gkv-spitzenverband.de, rundfunkbeitrag.de, bahn.de, deutschlandticket.de, bafa.de, integrationsbeauftragte.de, bundesregierung.de, kfw.de, destatis.de, hochschulkompass.de, daad.de, feiertage-deutschland.de (ticari değil ama resmî de değil; yalnız yardımcı), zoll.de, bmdv.bund.de, bmwsb.bund.de, bundesjustizamt.de, dvka.de, kmk.org, bmfsfj.de, bmbf.de, polizei-beratung.de, bundesverwaltungsamt.de, kbv.de, bundesnetzagentur.de, verbraucherzentrale.de (ikincil).
İlk turda sertifika hatası veren familienportal.de, deutsche-rentenversicherung.de, make-it-in-germany.com, auswaertiges-amt.de, bundesfinanzministerium.de, bundesbank.de, 116117.de ikinci denemede açıldı (Windows sertifika deposu ara sertifikayı sonradan aldı). Bir sayfa ilk denemede `tls` hatası verirse `add_sources --retry-transient` ile bir kez daha dene; ikinci kez de verirse kapalı say.

## Kapalı (kullanma)
- bmi.bund.de: her istekte HTTP 400 (bot engeli). Göç mevzuatı için gesetze-im-internet.de ve bamf.de kullan.
- bund.de: sertifika zinciri doğrulanamıyor. Portal zaten derin bilgi taşımıyor.
- bzr.bund.de (Bundeszentralregister): TLS el sıkışması başarısız. Führungszeugnis için bundesjustizamt.de (açık) kullan.
- bmftr.bund.de: bağlantı sıfırlanıyor; eski adres bmbf.de açılıyor.

## İnce sayfa uyarısı (`thin_text`)
- make-it-in-germany.com ve auswaertiges-amt.de sayfaları içeriği JavaScript ile yüklüyor; indirilen kopyada yalnız menü kalıyor. Bu iki sitede kanıt (`must_contain`) büyük olasılıkla kopyada bulunmaz → kaynak elenir. Yalnız kopyada metin kalan sayfaları seç; emin değilsen bakanlık ya da yasa sayfasını tercih et.
- gesetze-im-internet.de'de tek madde sayfası (`__18a.html`) kısa kalabiliyor ve ince sayılabiliyor. **Yasanın tam metin sayfasını** (`/<yasa>/BJNR….html`, sayfanın "Gesamtausgabe/Nichtamtliches Inhaltsverzeichnis" bağlantısı) ya da uzun madde sayfasını seç; `must_contain` yine madde cümlesinin birebiri olur.
- bundesnetzagentur.de giriş sayfaları ince; konu alt sayfalarını seç.

## 404 verenler
Yalnız tahmin edilen adresler 404 verdi (zoll Reisefreimengen, bmdv Führerschein, rki Impfkalender, bmwsb Mietrecht, bundesjustizamt Apostille, dvka Touristen, kmk Schulferien, bundesbank Basiskonto, bmf Lohnsteuer, bmj). Alan adları açık; doğru sayfayı sitenin kendi aramasıyla bul.
