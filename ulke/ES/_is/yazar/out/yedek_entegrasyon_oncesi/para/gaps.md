# ES ulusal paketi, konu "para": boşluklar

Genel: 12 kart (order 201-212), kaynak başına en çok 2 source_id, tüm alıntılar kaynak metninde doğrulandı. Kartlar şehir-nötr.

## Yazılmayanlar (kaynak kanıtlamadığı için)
- #1 Banka hesabı: hangi belgenin (NIE/pasaport) istendiği yazılmadı; Banco de España yalnız "bankanın kara para aklama kuralları gereği istediği bilgi" diyor.
- #7 Gestor: "ne zaman gerekir" yargısı yazılmadı; yalnız beyanı kişinin kendisinin de verebildiği ve gestor/asesörün (colaborador social ya da vekâletle) isteğe bağlı temsilci olduğu yazıldı.
- #8 Sigorta: "ev/hayat sigortası zorunlu değil" yazılmadı; yalnız araç sigortası zorunluluğu ve hipotekte bankanın sigorta koşulu koyabildiği yazıldı. Banco de España sayfası yangın/multirriesgo sigortasını "hipotek alırken zorunlu" diyor, DGSFP ise yasal zorunluluk olmadığını söylüyor; çelişki karta taşınmadı.
- #9 Emeklilik: Türkiye-İspanya sosyal güvenlik anlaşması yazılmadı (resmî kaynakta yok).
- #10 Bizum: tutar ve işlem sayısı limitleri yazılmadı (BdE blog yazısı 20/07/2021 tarihli, bankaya göre düşük olabilir).
- #4 KDV: "süper azaltılmış" adı kullanılmadı; AEAT oran sayfasının adlandırması (genel %21, azaltılmış %10 ve %4, belirli işlemlerde %0) kullanıldı. 2026'da elektrik/gaz için geçici oran değişikliği doğrulanmadı, yazılmadı. Hangi ürünün hangi orana girdiği AEAT yıllık PDF tablolarında (bu çalışmada okunmadı), karta yazılmadı.

## Tarihe duyarlı kartlar (valid_until.json)
- #5 Renta: kaynak Renta 2025 kampanyasını 8 Nisan - 30 Haziran 2026 veriyor; bu tarih 24.10.2026 itibarıyla geçmiş. Kart artık geçmiş kampanyayı tarif ediyor, valid_until null (kaynakta ileriye dönük bitiş yok). Bir sonraki kampanyanın (Renta 2026) tarihleri kaynakta yok; yayımlandığında kart güncellenmeli.
- #9 Emeklilik: yaş tablosu ve prim oranları 2026 satırı için; 2027 satırı da kartta var. valid_until null (kaynakta açık bitiş yok; prim oranları BOE emrinde 'ejercicio 2026').
- #3 IRPF: dilimler Renta 2025 kılavuzundan (2025 geliri); 2026 geliri için ayrı kılavuz yok. null.
- #4 KDV, #11 banka ücretleri (temel hesap tavanı 3 EUR/ay, BdE iki yılda bir güncelleyebilir), #12 Beckham (Renta 2025 kılavuzu): kaynakta açık bitiş yok, null.
- #10 Bizum: kaynak 20/07/2021 tarihli, null; kartta tüm cümleler 2021 tarihiyle yazıldı, limitler (0,50-1.000 euro, ayda 60 alma) tarihli eklendi.

## Diğer notlar
- #3 Bölgesel IRPF ölçeği rakamları kaynakta özerk bölge başına ayrı tabloda; karta rakam yazılmadı (bölgeye göre değişir).
- #5/#6: "Renta WEB" adı AEAT sayfalarında vekil/colaborador social ve iade sorgusu bağlamında geçiyor; kişinin kendi beyanı için "elektronik merkezdeki taslak/beyan işlem hizmeti" olarak yazıldı.
- #7: AEAT colaboración social sayfası 19/junio/2023 güncellemesi taşıyor (sayfa metninde tarih yok, keşif notundan).
- #12 Beckham: rejime nasıl ve ne zamana kadar başvurulacağı (seçenek bildirimi) bu iki sayfada yok, yazılmadı. İsim "Beckham yasası" kaynakta geçmiyor, yalnız başlıkta yaygın ad olarak kullanıldı; kaynağın adı "régimen fiscal especial aplicable a los trabajadores desplazados".
- Türk okuyucu: AB/AEA serbest dolaşım rejimi Türk vatandaşına uygulanmaz. Kartlardan hiçbiri AB vatandaşlığına dayalı bir hak anlatmıyor; #1'deki temel ödeme hesabı ölçütü AB'de yasal oturumdur (uyruk değil).

## G1 editör turu (2026-10-24) - yazılmayanlar
- #2 IBAN: Türkiye'nin SEPA dışı olduğu ve Türkiye ile havalenin uluslararası havale sayıldığı yazılmadı (064 AEA dışı ülke listesini vermiyor; BdE 'Transferencia internacional' sayfası kaynak olarak eklenmedi). Kart başına 2 kaynak sınırı için 063 yerine 087 (BdE 19.02.2026) kullanıldı; 'açıklama (concepto) alıcıya mesajdır' cümlesi 063'e bağlıydı, kaldırıldı.
- #3 IRPF: Baskiya/Navarra foral sistemi kaynakta yok, yazılmadı; IRNR (mukim olmayan) ayrımı kaynakta yok, yazılmadı.
- #5 Renta: sonraki kampanya (Renta 2026) tarihi yayımlanmadığı için yazılmadı.
- #8 Sigorta: DGSFP'nin 'yasal zorunluluk değil' görüşü ve BdE'nin 'yangın sigortası zorunlu' hükmü çelişki gibi; kartta yalnız BdE'ye atfen yazıldı. Türk plakalı araç için gümrük kuralının geçerli olup olmadığı kaynakta yok (Acuerdo üyeliği), yazılmadı.
- #9 Emeklilik: işsizlik/FOGASA/meslek eğitimi prim oranları rakam olarak yazılmadı (genel rejim satırı okunmadı); yalnız ayrı düzenlendikleri yazıldı. Türkiye-İspanya sosyal güvenlik düzeni yazılmadı.
- #12 Beckham: rejime başvuru yolu/süresi yine kaynakta yok.
