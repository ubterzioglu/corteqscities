# Oturum kartları: açık konular (gaps)

14 kart, #3 (randevu) şehir katmanına bırakıldı. Kart numaraları aday listedeki numaralardır.

## Genel
- Bu kaynak setinde İspanya için ulusal işlem sayfası olmayan kartlarda (#4, #7, #9, #12, #14) bağlantı BOE metni ya da resmî bilgi sayfasıdır; başvuru/işlem sayfası yok.
- Kartlardaki bütün harçlar polis sitesindeki güncel tabloya dayanıyor; tabloda yıl etiketi yok, bu yüzden "güncel resmî tarifeye göre" yazıldı. Tablonun yürürlük bitişi bilinmiyor.

## Kart bazında
- #1 NIE: "beyaz NIE / yeşil NIE" renk adları kaynak metinde geçmiyor; başlıkta kullanılmadı, yalnız anahtar sözcükte. NIE harcı (9,84 euro, tasas sayfası) kartta yok (kart 2 kaynak sınırı: 001 + 002). Ret sonrası ayrıntılı itiraz usulü yok.
- #2 Yeşil NIE (AB kayıt sertifikası): "yeşil NIE" adı kaynakta yok (başlık resmî adla). Başvuruda hangi belgelerin istendiği RD 240/2007 madde 7'ye bağlı; madde 7 şart listesi bu kartın kaynaklarında yok (005'te var). valid_until: harç tablosunda yıl yok, null.
- #4 TIE: TIE başvurusu için genel belge listesi yok (yalnız uzun süreli ikamet TIE'sinin listesi başka sayfada: pasaport, fotoğraf, harç). Randevu/ofis şehir katmanı. valid_until: harç tablosunda yıl yok, null.
- #5 AB vatandaşı çalışma izni: "ayrı çalışma izni gerekmez" cümlesi açıkça yok; metin "İspanyollarla aynı koşullarda her faaliyete erişim hakkı" diyor; kartta "teyit et" notu var. AB Antlaşması m.39.4 sınırlamasının içeriği kaynakta açıklanmıyor.
- #6 Oturum izni yenileme: yenileme başvurusunun kendi harcı (16,40 euro) 006 numaralı kaynakta (kart 7'ye atanmış), bu karta alınmadı; yalnız yenileme TIE'si harcı (19,30) var. Ücretli çalışma izninin yenilemesinde karar süresi/sessizlik kuralı (madde 80) okunmadı; 3 aylık karar ve olumlu sessizlik yalnız çalışmasız oturum (madde 64) için yazıldı. Yenileme için gereken belge listesi yok. valid_until: null (tablo yılsız).
- #7 Aile birleşimi: IPREM'in güncel euro tutarı kaynakta yok (kartta "teyit et"); başvuru formu/yeri ve belge listesi yok; ücret Orden PJC/617/2025 (13.6.2025) dayanaklı, RD 316/2026 buna atıf yapıyor, daha yeni tarife bulunamadı; valid_until: null (bitiş tarihi bilinmiyor).
- #8 Kalıcı oturum: beş yıllık sürenin ayrıntılı şartları (yönetmelik), karar süresi ve harç kaynakta yok.
- #9 Arraigo: arraigo için ayrı polis sayfası yok; EX10 sayfası "olağanüstü durumlar" başlığında (arraigo bu başlık altında, RD 1155/2024 m.125-127). Arraigo harcı tutarı kaynakta yok. Socioformativo ve familiar arraigonun özel şartları okunmadı/yazılmadı.
- #10 Dijital göçebe: 2026 SMI (asgari ücret) rakamı kaynakta yok, kartta "teyit et" notu var. Şart listesi İstanbul Başkonsolosluğu'nun 7 Ocak 2025 tarihli sayfasından (Türkiye'ye özgü ayrıntılar kartta yok). Ley 28/2022 metni gerekçe (preamble) düzeyinde alındı; güncel Ley 14/2013 madde 74 metni okunmadı. valid_until: null (SMI yılı belirsiz, sayfa tarihi 2025).
- #11 Kar amacı gütmeyen vize: tek kaynak İngilizce, Yeni Delhi Büyükelçiliği sayfası; randevu ve teslim ayrıntıları o konsolosluğa özgü olduğu için yazılmadı. 2.400 euro/ay (başvuran) ve 600 euro/ay (aile bireyi) kaynakta "2026" etiketiyle var; valid_until 2026-12-31 (kaynağın yıl sonu). Vize harcı tutarı kaynakta yok.
- #12 Altın vize: yürürlük bitişi yok (kalıcı kaldırma), valid_until null. Başka yatırım türlerinde (örneğin startup) geçiş ayrıntısı yazılmadı.
- #13 Öğrenci çalışma hakkı: eğitim türüne göre ayrıntı (madde 52.1.b ve sonrası) ve izin süresi (madde 57.4) yazılmadı; işveren başvuru belgeleri yok.
- #14 Vatandaşlık: başvuru formu, harç, dil/kültür sınavları (DELE/CCSE) ve işlem süresi kaynakta yok; kart yalnız ikamet süresi kurallarını verir. Türkiye'nin 2 yıllık gruba girmediği listeden anlaşılır ama kartta ayrıca söylenmedi.
- #15 Brexit: süreç 2 Temmuz 2020 tarihli ortak talimata dayanıyor; güncel uygulama/randevu sayfası kaynakta yok. Belge harcı (12,00 euro) yılsız tablodan.

## valid_until.json
- #2, #4, #6, #7, #10, #12: null (yıl etiketi ya da bitiş tarihi bilinmiyor).
- #11: "2026-12-31" (kaynak tutarı "In 2026" diyor).
