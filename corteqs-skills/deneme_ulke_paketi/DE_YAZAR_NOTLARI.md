# Almanya ulusal paketi — ülkeye özgü yazar ve keşif notları

`YAZAR_KURALLARI.md` (ülkeden bağımsız 12 kural) ve `city-pack\agents\ortak-kurallar.md` geçerlidir; bu dosya yalnız Almanya'ya özgü ekleri verir. Çelişirse YAZAR_KURALLARI geçer.

## Kimlikler
- `city_id` = `de`; `entry_id` = `de:<slug>`; `topic_id` = `de:<konu>`; `action_id` = `de:action:<slug>-<n>`; kaynak `de:kaynak:NNN` (yalnız `add_sources` verir).
- Şehir adı yerine `{sehir}`. `pack_check` şu adları yakalar: Berlin, München/Münih, Hamburg, Köln, Frankfurt, Stuttgart, Düsseldorf, Dortmund, Essen, Leipzig, Bremen, Dresden, Hannover, Nürnberg, Duisburg, Bochum, Augsburg, Ulm, Bielefeld, Heilbronn, Mannheim, Karlsruhe, Wiesbaden, Münster, Bonn, Aachen, Freiburg, Kiel, Mainz, Erfurt, Potsdam, Magdeburg, Saarbrücken, Schwerin. Örnek vermek için bile şehir adı yazma.

## Federal yapı (en önemli fark)
- Eyalet (Land) yetkisindeki konularda ulusal kart yalnız federal çerçeveyi yazar ve "eyalete göre değişir" der; eyalet rakamı, eyalet adı ve eyalet örneği YAZMAZ. Bunlar bölge paketine gider: eyalet tatilleri, Kirchensteuer oranı, Grunderwerbsteuer oranı, Mietpreisbremse'nin geçerli olduğu yerler, okul sistemi ve tatil takvimi, Kita ücretleri, eyalet aile ödemeleri, Zulassung/HU ücretleri.
- Kurum adı eyalete/şehre göre değişiyorsa (Bürgeramt, Bürgerbüro, Einwohnermeldeamt, KVR; Ausländerbehörde, Landesamt für Einwanderung) genel adı yaz ve "adı şehre göre değişir" de.

## Türk okuyucu
- AB serbest dolaşımı Türk vatandaşına uygulanmaz; AB vatandaşını anlatan kart bunu bir cümleyle söyler.
- Türk vatandaşlarının Ortaklık Hukuku'ndan (ARB 1/80, Katma Protokol md. 41 "standstill") gelen hakları yalnız kaynakta açıkça yazıyorsa yazılır; bellekten "Türkler muaf" denmez.
- Türkiye–Almanya sosyal güvenlik anlaşması (emeklilik, sağlık) yalnız kaynakla.
- Türkiye'deki Alman temsilcilikleri (tuerkei.diplo.de) vize kaynağı olarak resmîdir; "Türkiye'den başvuru" cümleleri bu sayfalara dayanır.

## Çeviri dikkati
- Aufenthaltstitel = oturum belgesi (genel ad); Aufenthaltserlaubnis = süreli oturum izni; Niederlassungserlaubnis = yerleşme izni (süresiz); Blaue Karte EU = Mavi Kart AB; Fiktionsbescheinigung = geçici oturum belgesi.
- Anmeldung = adres kaydı (oturum değil); Abmeldung = adres kaydının silinmesi (yalnız yurt dışına çıkışta); Meldebescheinigung = adres kayıt belgesi; Wohnungsgeberbestätigung = konut veren teyidi.
- Kaution = depozito; Nebenkosten/Betriebskosten = yan giderler; Kaltmiete/Warmmiete = yan gidersiz/yan giderli kira; Kündigung = fesih; Kündigungsfrist = fesih süresi; Widerspruch = itiraz.
- Abschlag = aylık ön ödeme (kesin tüketim değil); Grundpreis = sabit ücret; Arbeitspreis = birim fiyat.
- Freibetrag = muafiyet tutarı (vergiden düşülen); Grundfreibetrag = temel muafiyet; Steuerklasse = vergi sınıfı; Lohnsteuer = ücret vergisi (gelir vergisinin kesinti biçimi).
- Krankmeldung/AU = hastalık bildirimi/raporu; Entgeltfortzahlung = ücret ödemesinin sürmesi; Krankengeld = hastalık parası (sigortadan).
- gesetzliche Krankenversicherung (GKV) = kamu sağlık sigortası; private (PKV) = özel; Zusatzbeitrag = ek prim; Familienversicherung = aile sigortası.
- "Bürgergeld" 2026 reformuyla ad değiştirebilir ("Neue Grundsicherung"); kaynaktaki adı kullan, kaynağın tarihini yaz.

## Kaynak öncelikleri (resmî yayıncı)
- Kural için birincil: `gesetze-im-internet.de` (konsolide federal yasa; madde sayfası), Bundesministerium siteleri (bmi, bmas, bmf, bmg, bmwsb, bmj, bmdv, bmbf, bmfsfj), BAMF, Bundesagentur für Arbeit, Deutsche Rentenversicherung, Zoll, BZSt, Bundesnetzagentur, BaFin, Bundesbank, KBA, RKI/STIKO, Bundesverwaltungsamt, Bundesjustizamt, Auswärtiges Amt ve `*.diplo.de` temsilcilikler, `make-it-in-germany.com` (federal portal), `familienportal.de` (BMFSFJ), `rundfunkbeitrag.de` (ARD/ZDF/DR resmî servis), `116117.de` (KBV), `anerkennung-in-deutschland.de` (BIBB), `kmk.org`, `deutschlandticket.de` ve `bahn.de` (yalnız bilet kuralı için).
- İkincil, yalnız birinci kaynak resmî olduğunda ve o bilgi resmî sayfada yoksa: `verbraucherzentrale.de` (kamu kaynaklı tüketici kuruluşu), `handbookgermany.de` (federal destekli). Her kullanımı `gaps.md`'de söyle.
- Kaynak olmaz: Wikipedia, expat portalları, emlak/sigorta/karşılaştırma siteleri, hukuk büroları, blog/forum, AI özetleri.
- PDF `add_sources`'ta elenir; yasanın HTML madde sayfasını ya da bakanlığın HTML sayfasını seç.
- Sayfa dili Almanca; `must_contain` ve claim `quote` Almanca birebir. İngilizce resmî sayfa (make-it-in-germany EN, BAMF EN) yalnız Almanca sürüm yoksa.

## Tarihe duyarlı (valid_until)
Asgari ücret, Minijob sınırı, Kindergeld, Elterngeld, Kinderzuschlag, Deutschlandticket, Grundfreibetrag ve vergi dilimleri, sosyal sigorta oranları, Blaue Karte eşikleri, Sperrkonto tutarı, BAföG tutarları, Wohngeld, Kleinunternehmer sınırı, eAT ve vize ücretleri, resmî tatiller, Rundfunkbeitrag tutarı, reçete katılım payı sınırları. Kaynak yıl veriyorsa o yılın 31 Aralık'ı; kaynakta açık bitiş tarihi varsa o; bilinmiyorsa `null`.

## Bilinen erişim durumu
Keşif öncesi 50 resmî adres yoklandı; sonuç `ulke\DE\_is\kesif\erisim_ozet.md`. Kapalı alan adını deneme; o bilgiyi başka resmî sayfadan bul ya da `gaps`'e yaz.
