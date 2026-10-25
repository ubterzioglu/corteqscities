# Almanya'dan yeni bir şehir: hangi skill, hangi sırayla

Yazıldı: 25.10.2026 (Almanya ulusal paketi v1 kurulduğu gün). Her adım **ayrı, yeni bir oturumda**. İspanya karşılığı: `ISPANYA_YENI_SEHIR.md`.

## Paket
`ROOT\ulke\DE` v1 (25.10.2026): 113 kart, 11 konu, 2120 iddia, 193 kaynak, 13 tarihli kart. Açık konular: `ulke\DE\acik_konular.md`. Sahte şehirde `country_apply apply` (113 kart) + `merge_package` (0 bulgu, 0 alıntı kaybı) denendi.
**Bölge (eyalet) paketi henüz yok.** Almanya federal; eyalete göre değişen bilgi (tatiller, Kirchensteuer oranı, Grunderwerbsteuer, Mietpreisbremse alanı, okul/Kita, mağaza saatleri) ulusal kartta yalnız "eyalete göre değişir" çerçevesiyle duruyor.

## Drive kataloğundaki Almanya şehirleri (33) ve eyaletleri
- Nordrhein-Westfalen: Aachen, Bielefeld, Bochum, Bonn, Dortmund, Duisburg, Düsseldorf, Essen, Köln
- Bayern: Augsburg, Ingolstadt, Münih, Nürnberg, Regensburg
- Baden-Württemberg: Freiburg, Heidelberg, Heilbronn, Karlsruhe, Mannheim, Stuttgart, Ulm
- Hessen: Darmstadt, Frankfurt, Kassel, Wiesbaden (Wiesbaden-Mainz ikili: Mainz Rheinland-Pfalz)
- Niedersachsen: Hannover, Wolfsburg · Sachsen: Dresden, Leipzig · Rheinland-Pfalz: Trier
- Şehir-eyaletler: Berlin, Bremen, Hamburg
Öneri: ilk şehir NRW'den (9 şehir) olsun; bölge paketi önce NRW için kurulur, sonra Bayern ve Baden-Württemberg.

## 1. `city-pack` — paketi üretir
Yalnız şehir adını yazma; ülke paketini açıkça ver (skill ülke paketini yalnız kullanıcı verirse kullanır).

- **Bölge paketi yokken** (şimdiki durum):
  > <Şehir> paketi. Ülke paketi var: `ROOT\ulke\DE` (v1). `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md`'deki "city-pack ile birlikte kullanım" adımlarını uygula (tek paket: `pack_merge` gerekmez, `country_apply apply --pack ROOT\ulke\DE`). Atınç'ın Drive'ındaki şablonu ara. Eyalete göre değişen bilgiler şehir yazarına kalır. Ülke ve şehir fazının süre ve token'ını ayrı ölç.
- **Bölge paketi kurulduktan sonra** (ör. `ROOT\ulke\DE\bolge\nrw`): İspanya'daki gibi önce `pack_merge --pack ulke\DE --pack ulke\DE\bolge\<ad>`, sonra `apply`. Bölge paketi bir skill değil; `ULKE_FAZI.md` "Bölge paketi" adımlarıyla elle kurulur (Endülüs'te 9 kart ≈ yarım gün). Almanya için bölge kart adayları `ulke\DE\acik_konular.md` "Bölge (eyalet) paketine giden konular" bölümünde.

## 2. `city-audit` — bağımsız denetim
Paket bitince yeni, temiz bir oturumda yalnız: **<Şehir> paketini denetle**.

## 3. `city-preview` — Drive yükleme ve önizleme

## Dikkat
- **Sırayla:** iki şehir aynı anda yürütülmez.
- **Tarih:** AB dışı paket gümrük kartı 31.10.2026'da (1 Kasım işlem ücreti), 11 kart 31.12.2026'da, asgari ücret kartı 31.12.2027'de eskir. `apply` eskiyen kartı kopyalamaz (`stale`); önce paketi güncellemek daha ucuz.
- **Erişim:** bmi.bund.de, bund.de, bzr.bund.de bu ağdan kapalı; make-it-in-germany.com ve auswaertiges-amt.de kopyada metin bırakmıyor. Şehir belediyesi sitesi de kapalı olabilir; intake'teki erişim yoklaması gösterir.
- **Dil:** kaynaklar Almanca; `must_contain` ve claim alıntıları Almanca birebir. Yumuşak tire (U+00AD) artık alıntı karşılaştırmasında yok sayılıyor (`merge_package` ve `pack_check`).
- **Şehir adı kontrolü:** `pack_check` Almanya şehir adlarını tanır (`CITIES_BY_COUNTRY["DE"]`); şehir yazarı için kural aynı: şehre özgü kartı ayrı yaz, ülke kartını silme.
