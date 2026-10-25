# para - yazar notları (25.10.2026)

Çıktı: 12 kart (order 301-312), 164 claim, 21 bağlantı. pack_check çıkış 0.

## Ana döngünün karar vermesi gereken noktalar (kart başına en çok 2 kaynak sınırı yüzünden)
- Kart 8 (maas-sosyal-sigorta-kesintileri-2026): kaynaklar DRV 02.01.2026 (de:kaynak:018) + BMG Beiträge und Tarife (de:kaynak:028). Kartta emeklilik %18,6 (işçi %9,3), işsizlik %2,6 (işçi %1,3), sağlık genel oranı %14,6, ortalama ek prim %2,9 (2026), yarı yarıya paylaşım var. SIĞMAYANLAR: bakım sigortası %3,6 / çocuksuz %4,2, işçi %1,8, "seit 1. Januar 2025" (de:kaynak:025) ve Solidaritätszuschlag %5,5 + muafiyet sınırı 20.350/40.700 euro (de:kaynak:010, 011). İstenirse bunlar ayrı bir kart olur (ör. bakım sigortası + Soli) ya da kart 8 için 3 kaynak izni verilir. Not: sağlık sigortası genel oranı artık kart 8'de 028 kaynağıyla yazıldı (SGB V §241 gerekmedi).
- Kart 9 (zorunlu-arac-sigortasi-ve-ozel-sorumluluk-sigortasi): kaynaklar PflVG §1 (012) + BaFin Haftpflicht (019). SIĞMAYAN: BaFin Hausratversicherung (020: Hausrat isteğe bağlı, Neuwert, Wohnflächenmodell vb.). Kfz-Haftpflicht teminat tutarları kaynakta yok, yazılmadı.
- Kart 10 (almanya-emeklilik-yasi-bekleme-suresi-turkiye-anlasmasi): kaynaklar SGB VI §35 (013) + DRV Verbindungsstelle Türkei (021). SIĞMAYANLAR: SGB VI §50 genel bekleme süresi 5 yıl (014) ve DRV Sozialversicherungsabkommen genel sayfası "Türkiye için kısıtlamalar" notu (022). Kartta "bekleme süresi (Wartezeit)" var ama 5 yıl rakamı yok. Kademeli yaş geçişi (SGB VI §235) kaynaklarda yok: kart yaşı "SGB VI §35'e göre 67" diye yazıyor, doğum yılı geçişlerini anlatmıyor (eski doğum yıllarında 67'den düşük yaş olabileceği kartta söylenmiyor). İstenirse 014 ile kart 10 değiştirilir ya da 3 kaynak izni verilir.

## Keşif notundan farklı çıkan nokta
- Kart 2: Lastschrift geri alma süresi talimat gereği yazılmadı. Ancak Bundesbank SEPA SSS metninde (de:kaynak:026) şu cümleler VAR: "Eine SEPA-Basislastschrift kann innerhalb von acht Wochen nach Belastung ohne Angabe von Gründen an den Einreicher zurückgegeben werden" ve "Ein Lastschrifteinzug ohne Mandat ... kann bei beiden Verfahren vom Zahler innerhalb von 13 Monaten nach der Kontobelastung zurückgegeben werden". Ana döngü isterse karta eklenir (kaynak zaten kartın source_ids'inde).

## Kart bazında yazılmayan bilgi
- Kart 1 (basiskonto): ücret tutarı yazılmadı (kaynak yalnız "angemessen" diyor).
- Kart 2 (iban-sepa): Echtzeitüberweisung zorunluluk tarihleri (09.01.2025 alma, 09.10.2025 gönderme) ve Empfängerüberprüfung pazar tarihleri kartta yok; ücret tutarı yok.
- Kart 3 (gelir vergisi): iki formüllü dilimin (12.349-17.799 ve 17.800-69.878 euro) hesap formülleri yazılmadı; "%42/%45" kanundaki 0,42 • x ve 0,45 • x formül katsayılarından alındı (kanun metni "oran" demiyor, formül veriyor). Soli ve vergi sınıfları ayrı kartlarda.
- Kart 4 (vergi sınıfı): sınıf değiştirme tarihi/süre kuralları, faktör yöntemi (EStG §39f), III/V seçim önerisi kaynakta yok; yazılmadı.
- Kart 5 (vergi beyannamesi): danışmanlı beyan uzatması (AO §149 Abs. 3, Şubat sonu) yazılmadı; ELSTER'in ücretsiz olduğu kanıtsız; EStG §46 (de:kaynak:006) 2 kaynak sınırı nedeniyle kullanılmadı (ELSTER sayfası zorunlu halleri özetliyor). valid_until null: ELSTER sayfası 2025 yılı rehberi, kartın tarih örneği 2025 vergi yılı.
- Kart 6 (KDV): yalnız %19 ve %7; Anlage 2 örnekleri ve 01.01.2026 restoran değişikliği yazılmadı; tüketici fiyatına dahil olup olmadığı kaynakta yok.
- Kart 7 (Kirchensteuer): oran (%8/%9), kimin ödediği ayrıntısı, üyelikten çıkış usulü kaynakta yok; kart yalnız çerçeve. "Oran ve çıkış usulü eyalete göre değişir" ifadesi için dayanak Art. 137 Abs. 8 WRV (uygulama ayrıntısı eyalet yasalarına aittir); çıkışa özel bir cümle kaynakta yok.
- Kart 11 (kredi bilgi kuruluşu): "yılda bir kez ücretsiz" kuralı yazılmadı. Kaynaklarda "Schufa" adı geçmiyor, yalnız "Auskunftei" geçiyor (BDSG §31); kart başlığı ve özeti "Schufa gibi kredi bilgi kuruluşları (Auskunftei)" diye yazıyor, Schufa'nın kendi hizmetlerine dair iddia yok.
- Kart 12 (hesap değiştirme): ücret tutarı yok (kaynak "angemessen" diyor).

## Kullanılmayan kaynaklar
- de:kaynak:006 (EStG §46), 010, 011 (SolzG), 014 (SGB VI §50), 020 (BaFin Hausrat), 022 (DRV Abkommen genel), 025 (BMG bakım sigortası), 027 (Bundesbank "Sepa einfach erklärt", 2014 tarihli). Ek not: 026'nın IBAN bölümü 027'den daha güncel ve yeterli.
- İkincil kaynak (verbraucherzentrale, handbookgermany) hiçbir kartta kullanılmadı.

## Dikkat notları
- Türk okuyucu: kart 1'de hakkın dayanağı AB'de hukuka uygun ikamet (ZKG §31); kart 10'da Türkiye-Almanya sosyal güvenlik anlaşması yalnız DRV Verbindungsstelle Türkei sayfasına dayanıyor; kart 12'de Almanya dışındaki bankayla yasal hesap değiştirme yardımı uygulanmıyor.
- valid_until.json: kart 3 ve kart 8 için 2026-12-31 (kaynaklar 2026 yılı değerleri); kart 5 null. Kart 7, 9, 10, 11, 12 yıla bağlı sayı içermiyor, listede yok. Kart 2'de anlık havale kuralları tarihsiz sayfaya dayanıyor, listede yok.
- Kart 8'deki BMG GKV sayfasında (028) "Stand: 3. September 2026" ibaresi var; oranlar sayfada 2026 olarak etiketli.
- Ana döngü kontrolü: kart 3'te EStG §32a metnindeki sayılar NBSP içeriyor; alıntılar kaynak metninden kopyalandı (pack_check geçti).
