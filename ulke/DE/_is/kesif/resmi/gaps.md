# resmi — boşluklar ve notlar (keşif 25.10.2026)

Tüm 12 kartın en az 1 kaynağı var; 21 adres. Tüm `must_contain` ifadeleri sayfa metninde birebir doğrulandı (düz HTML indirme + metin ayıklama).

## Kısmi kartlar (kanıtsız kalan bilgi)
- Kart 1 (Anmeldung): yalnız BMG tam metni. Randevu, hangi belgelerin istendiği (pasaport, kira sözleşmesi) ve ofis adı şehre göre değişir; federal sayfa bulunamadı. Wohnungsgeberbestätigung içeriği ve 2 hafta süresi kanıtlı (§17, §19).
- Kart 2: Abmeldung ve Meldebescheinigung kanıtlı (§17 Abs.2, §18). Şehir içi taşınma bildiriminin ayrıntısı §17'de sadece "Wohnung bezieht" çerçevesi; Meldebescheinigung ücreti federal yasada yok (Länder).
- Kart 3 (Steuer-ID): tanım, bulunma yeri, kayıpta yeniden talep kanıtlı. "Almanya'ya gelince ilk IdNr mektubu ne zaman gelir" ifadesi bu sayfada yok.
- Kart 4: Versicherungsnummer yapısı ve Versicherungsnummernachweis kanıtlı. "Renteninformation" yazıları ve yeni gelen biri için numaranın nasıl alındığı (işveren/DRV) kanıtsız; DRV'nin ilgili sayfası bulunamadı (URL tahminleri ana sayfaya düşüyor).
- Kart 5 (eID): eAT'nin eID işlevi (§78 Abs.5 AufenthG), PAuswG §10, i-Kfz sayfasında eAT/BundID. BundID kuruluşunun adımları kanıtsız: id.bund.de JavaScript ile yükleniyor (thin), digitale-verwaltung.de PDF, personalausweisportal.de ve personenstandsrecht.de bu ağdan HTTP 400 veriyor (bmi.bund.de ile aynı engel). AusweisApp (ausweisapp.bund.de, BSI) açılıyor ama içerik İngilizce sayfada; Almanca derin adres (`/das-brauchen-sie`) denenmedi.
- Kart 6: apostil (Türkiye–Almanya, 29.09.1985) ve çok dilli belge istisnası kanıtlı (tuerkei.diplo.de). Almanya'da düzenlenen belgeye Türkiye için apostil veren makam (Länder iç idaresi/mahkeme başkanı/Bundesamt für Auswärtige Angelegenheiten) kanıtsız: auswaertiges-amt.de JavaScript, personenstandsrecht.de 400. Yeminli tercümanın yetkisi için justiz-dolmetscher.de ana sayfası var (portal tanımı); "beglaubigte Übersetzung" hukuki tanımı kanıtsız.
- Kart 7: noter (BeurkG §40, §42) ve kamu kurumu onayı (VwVfG §33) kanıtlı. "Hangi durumda hangisi gerekir" ve noter ücreti federal yasada/bu sayfalarda yok; eyalete göre değişir.
- Kart 8: eVB, HU, SEPA/Kfz-Steuer (bmv.de, zoll.de, KraftStG §1). Zulassungsstelle ve tescil ücreti yerel/eyalet katmanı, kasten dışarıda. HU periyotları (FZV/StVZO) için gesetze-im-internet adresi bulunamadı (`fzv`, `fzv_2011` index 404); StVZO §29 denenmedi. Kfz-Steuer tutarı kartta yazılmaz (zoll.de Steuerhöhe sayfası denenmedi).
- Kart 9: PStG §18 (1 hafta), §21; AufenthG §33; Türk Formül A belgesi (diplo.de). PStG §59 Geburtsurkunde içeriği tam metinde var ama ayrı doğrulanmadı. Standesamt ücreti kanıtsız (yerel). Not: §33 "kann" (Ermessen) ile "wird ... von Amts wegen erteilt" (iki ebeveyn izinli) ayrımı yazarın dikkatine.
- Kart 10: BGB §1309 (Ehefähigkeitszeugnis, 6 ay). Yabancı evliliğin tanınması: yalnız tuerkei.diplo.de (Aile Cüzdanı tanınmıyor, Formül B). "Almanya'da resmî tanıma prosedürü yok / Nachbeurkundung" ifadesi için federal resmî sayfa bulunamadı (personenstandsrecht.de ve bva.bund.de PDF bu ağda denenmedi/engelli). Türk tarafının evlenme ehliyet belgesi (Türkiye'den) kanıtsız. tuerkei.diplo.de/tr-de/service/1890586-1890586 (Ehefähigkeitszeugnis) Almanlar için olduğundan seçilmedi.
- Kart 11: BZRG §30, §30b ve BfJ ücret 13,00 EUR + BfJ SSS. Dijital Führungszeugnis için eID gerekliliği BfJ ana sayfasında geçiyor ama ayrı ifade seçilmedi. Avrupa belgesinin Türk vatandaşı için içeriği (üçüncü ülke vatandaşları dahil §30b Abs.1 Nr.2) yasada var. Teslim süresi kanıtsız (resmî rakam yok).
- Kart 12: VwGO §70 (1 ay) ve §58 (1 yıl). Alan bazında farklar: sosyal güvenlik (SGG §84), vergi (AO §355), Widerspruchsverfahren'in birçok eyalette kaldırılması; bunlar kanıtsız ve ulusal kart genel çerçeve olmalı. VwVfG §79 eklenmedi.

## Erişim engeli
- personalausweisportal.de, personenstandsrecht.de: HTTP 400 (bot engeli). bmi.bund.de zaten kapalı.
- id.bund.de: sayfa yükleniyor ama içerik JavaScript (5 KB, ince).
- deutsche-rentenversicherung.de: tahmin edilen derin adresler ana sayfaya düşüyor; yalnız Glossareintraege (Rentenlexikon) adresleri çalıştı.
- justiz-dolmetscher.de: ilk istek "connection forcibly closed"; `www.` ile açıldı (2,5 KB, ince ama 500 karakter eşiğini geçiyor).

## Dikkat notları
- Tarihe duyarlı: Kart 11 ücreti (13,00 EUR, JVKostG Nr. 1130; sayfa tarihsiz, BfJ Fragen sayfasında "Kreditkarte" ödeme notu). Diğer kartlarda tutar yok.
- Kart 1/2: BMG §19 Wohnungsgeber teyidi elektronik olarak da verilebilir (Zuordnungsmerkmal, Abs.4). Meldebehörde adı şehre göre değişir.
- Kart 5: PAuswG §10 Abs.2: 16 yaş altı için eID kapalı; eAT için §78 Abs.5 AufenthG ile eşdeğer uygulanır. Kurum Ausländerbehörde (adı şehre göre).
- Kart 6/9/10: tuerkei.diplo.de sayfası Türkiye'deki Alman temsilciliklerinin; 2018 tarihli parçalar içerir, güncelliği yazarın kontrolüne bağlı. Aile Cüzdanı tanınmıyor ifadesi bu sayfanın ifadesidir.
- Kart 7/12: Federal çerçeve; eyalet farkı var, ulusal kart yalnız çerçeve yazmalı.
- Kart 8: Kfz ücret/HU/Zulassungsstelle katmanı bölge paketine.
