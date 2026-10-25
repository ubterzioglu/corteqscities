# ev konusu — boşluklar ve dikkat notları (keşif 25.10.2026)

Tüm 9 kartın en az 1 kaynağı var. Kaynak sayısı 27 (hedeften fazla): yazar kart başına en çok 2 tanesini seçsin. Tüm `must_contain` ifadeleri indirilen metinde birebir doğrulandı.

## Kart bazında
- Kart 1 (kira sözleşmesi, süresiz kural, Staffel/Index, kiracı fesih): TAM. BGB §542 (süresiz/fesih), §573c (süre), §557a Staffelmiete, §557b Indexmiete; BMJ Mietrecht özeti hepsini tek sayfada verir (tarih 14.09.2022). Öneri: §573c + BMJ özeti ya da §573c + §557a/§557b.
- Kart 2 (Kaution): KISMİ. Üst sınır, 3 taksit, ayrı hesap: §551 TAM. İade süresi ve koşulu yasada yazılı değil (içtihat); resmî sayfa bulunamadı, rakam YAZILMAZ. §548 yalnız kiralayanın hasar taleplerinin 6 ay zamanaşımını verir (dolaylı).
- Kart 3 (Mietpreisbremse + Kappungsgrenze): TAM. Mietpreisbremse eyalet yönetmeliğine bağlı; §556d: yönetmelikler en geç 31.12.2029'da sona erer (BMJ sayfası: Mayıs 2025'te kabinede uzatma, sayfa güncellemesi 22.07.2025; §556d metni 2029'u içeriyor). Eyalet listesi YOK (bölge paketi). Kappungsgrenze %20, gerilimli bölgede %15 (eyalet yönetmeliği). Ulusal kart rakamı yalnız federal kanun metninden alsın.
- Kart 4 (Betriebskosten): TAM. §556 (yıllık hesap, 12 ay + 12 ay itiraz), BetrKV §2 (kalem listesi). Not: §556 Abs. 3a (Glasfaserbereitstellungsentgelt) yeni, kartta gerekmez.
- Kart 5 (Mietminderung, küçük onarım, Schönheitsreparaturen): KISMİ. Mietminderung (§536) ve Mängelanzeige (§536c), kiralayanın bakım yükümlülüğü (§535) TAM. Küçük onarım (Bagatellreparatur) tavanı ve Schönheitsreparaturen kuralı kanunda yok (mahkeme içtihadı: BGH); resmî açık sayfa bulunamadı, kart bu iki alt konuyu "sözleşmeye ve içtihada bağlı, hukuki destek al" diye yazsın; tutar/oran yazılmasın. Kanunda Minderung yüzdesi de yok.
- Kart 6 (WBS + Wohngeld): KISMİ. WBS: §27 WoFG (zorunluluk, 1 yıl geçerli), §9 WoFG (federal gelir sınırı: 1 kişi 12.000 €, 2 kişi 18.000 €, +4.100 €/kişi, +500 €/çocuk). DİKKAT: bu rakamlar federal TABAN ve kanunun eski metni; eyaletler farklı sınır belirler (uygulamada çoğu yerde daha yüksek). Ulusal kart bu rakamı yazarsa "federal çerçeve, eyalete göre değişir" demeli ya da hiç yazmamalı. Wohngeld: bmwsb "Wohngeld-Plus" sayfası (2025 durumu, son artış 01.01.2025; kanun 2 yılda bir uyarlar, 01.01.2027 artışı gündemde olabilir); WoGG §3 (kimin hakkı var). Wohngeld tutar tablosu ve gelir sınırları bulunamadı (tutar tabloları PDF/hesaplayıcı/Anlage; wohngeldrechner sayfası dinamik): kartta tutar YAZILMASIN, valid_until = 31.12.2026 önerilir.
- Kart 7 (Übergabeprotokoll, Wohnungsgeberbestätigung, Bestellerprinzip): KISMİ. Wohnungsgeberbestätigung §19 BMG TAM. Bestellerprinzip WoVermRG §2 TAM (kiralama), §656c BGB (satış). Übergabeprotokoll için yasa/resmî sayfa yok (yasal zorunluluk değil, uygulama); kartta "yasada zorunlu değil, uygulamada önerilir" diyorsa kaynaksız kalır → bu kısım yazılmasın ya da kaynaklı cümleyle sınırlansın.
- Kart 8 (sahte ilan): TAM ama tek sayfa. polizei-beratung.de Vorkassebetrug sayfasının "Auch bei der Wohnungssuche lauern Gefahren" bölümü (kendi ilan sayfası yok); ilan sahtekarlığı (anzeigenbetrug-ad-scams) sayfasında konut yok. Sayfa tarihsiz.
- Kart 9 (ev satın alma çerçevesi): TAM (çerçeve). §311b BGB (noter şartı), §873 BGB (Grundbuch tescili), Art. 105 GG (Grunderwerbsteuer oranını eyalet belirler), GrEStG §1 (alımın vergiye tabi olması). Not: GrEStG §11 (federal taban oran %3,5) tek madde sayfası 315 karakter olduğu için elendi; oran ulusal kartta zaten yazılmaz (eyalete göre değişir). §656c BGB (satışta emlakçı komisyonu eşit paylaşım) kart 9'a da yarar.

## Erişim
- Engelli alan adı yok. bmj.de ana sayfası ve alt sayfaları açıldı (bmjv.de adresine yönlendiren menü bağlantıları var; kaynakta bmj.de adresleri kullanıldı). bmwsb.bund.de'de tahmin edilen eski yol 404 verdi; doğru adres `/DE/wohnen/wohngeld/wohngeld-plus/wohngeld-plus_artikel.html`.
- verbraucherzentrale.de kullanılmadı (konu sayfaları bulunamadı, ikincil kaynak gerekmedi).

## Tarihe duyarlı
- Kart 3: Mietpreisbremse yönetmeliklerinin son tarihi 31.12.2029 (§556d). Yazar valid_until = 2029-12-31.
- Kart 6: Wohngeld, WBS gelir sınırı (bkz. üstte); valid_until yıl sonu.
