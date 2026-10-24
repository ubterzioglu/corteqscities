# ES planlama: boşluklar ve notlar (2026-10-24)

Bu dosya `selected.jsonl` ile birlikte okunur. 14 satır var, 13 ayrı adres (Estambul "residencia no lucrativa" sayfası iki satırda: kart 1-2 ve kart 6). Her satırın `must_contain` ifadeleri canlı sayfada tek tek doğrulandı (HTML ve PDF).

## Kart bazında durum
| Kart | Durum | Kaynaklar |
|---|---|---|
| 1 Taşınma planı ve sıra | Kısmi | Estambul Başkonsolosluğu vize sayfası (vize + ilk oturum izni birlikte, vize 365 gün, İspanya'da 1 ay içinde TIE) |
| 2 Getirilecek belgeler | Dolu (vize/oturum için) | Aynı Estambul sayfası (apostil/yasallaştırma, çeviri, sabıka, sağlık raporu, pasaport) |
| 3 İlk günler | Kısmi | Seguridad Social NUSS sayfası, Banco de España temel ödeme hesabı sayfası |
| 4 Eşya taşıma ve gümrük | Dolu (AB dışı) / boş (AB içi eşya) | AEAT: bilgi, medios de pago, franquicias, traslado de residencia |
| 5 Evcil hayvan | Dolu | AEAT mascotas sayfası |
| 6 Sağlık sigortası | Dolu (vize türüne bağlı) | Estambul: no lucrativa + estudios |
| 7 Kısa bilgiler | Dolu | BdE euro, BOE Anayasa m.3, BOE RD 236/2002, IGN saat makalesi |

## Boşluklar ve dikkat edilecekler

### Kart 1 (plan ve sıra)
- Genel "taşınma sırası" anlatan tek resmî sayfa yok. Yalnız vize, ilk oturum izni ve TIE sırası resmî sayfayla kanıtlı. AB vatandaşı için kayıt belgesi (policia.es) bu görevde aranmadı; pakette oturum konusunda var.
- Estambul sayfaları tarihsiz. Başvuru öncesi konsolosluk sayfasından teyit notu düşülmeli.
- Bu sayfalar aralıklı 503 (gateway timeout) veriyor. Arka arkaya hızlı isteklerde oluyor, tekrar denemede açılıyor. Bot engeli değil; ama otomatik denetimde yeniden deneme gerekir.

### Kart 3 (ilk günler)
- Sıra (önce hangisi) için resmî tek sayfa yok. Resmî sayfası bulunan adımlar: TIE (kart 1'deki Estambul sayfası, "1 ay içinde"), sosyal güvenlik numarası (NUSS), banka (temel ödeme hesabı).
- NIE ve empadronamiento pakette var; yeni kanıt aranmadı. Padrón belediye işi, ulusal tek resmî sayfa seçilmedi.
- Kart başına 2 kaynak sınırı yüzünden TIE kaynağı kart 3 satırına yazılmadı.
- NUSS sayfası: "Plazos: Puedes solicitar el Número de la Seguridad Social en cualquier momento" diyor, yani zorunlu süre yok. Kartta "ilk günlerde mutlaka" gibi yazılmamalı.
- Banka sayfası: temel ödeme hesabı ("cuenta de pago básica") hakkı; normal hesap için resmî sayfa yok.

### Kart 4 (eşya ve gümrük)
- AB içinden taşınma (ev eşyası) için özel resmî sayfa bulunamadı. AEAT "medios de pago" sayfası AB içi nakit için S1 modelini kapsıyor (kanıtlı). Eşya için "AB içinde gümrük kontrolü yoktur" cümlesi resmî sayfayla kanıtlanamadı; kartta yazılacaksa kaynaksız kalır.
- Ev eşyası muafiyeti (traslado de residencia) sayfası güncel: "Página actualizada: 12/mayo/2026". Koşullar: 12 ay AB dışında ikamet, eşyanın en az 6 ay sahipliği, ikamet yerleştikten sonra 12 ay içinde beyan. Sayfada Estados Unidos örneği geçer, ama kural AB dışındaki tüm ülkeler (Türkiye dahil) için aynı.
- Ek aday (doğrulanmadı, kullanılmadı): NI 08/2026 not bilgilendirici PDF, `https://sede.agenciatributaria.gob.es/static_files/AEAT_Intranet/Aduanas/Normativa/notas_inf/Ni_08_2026.pdf`.
- Yolcu muafiyeti 430 euro (hava/deniz) ve 300 euro (kara), 15 yaş altı 150 euro. Ceuta, Melilla ve Kanarya Adaları farklı rejimde, kartta tek cümleyle "ayrı kurallar" denmeli.
- Nakit eşiği: 10.000 euro ve üstü giriş/çıkışta önceden beyan. AB dışı için E1, AB içi için S1 modeli.

### Kart 5 (evcil hayvan)
- MAPA sayfası daha güncel ama koyulmadı: `https://www.mapa.gob.es/es/ganaderia/temas/comercio-exterior-ganadero/desplazamiento-animales-compania/viajar-perros-gatos-hurones`. Python sertifika doğrulaması `self-signed certificate in certificate chain` hatası verdi (Windows PowerShell ile açıldı). Kuralın gereği sertifika hatalı sayfa yok, o yüzden listeye girmedi.
- MAPA sayfası Reglamento (UE) 2026/636 (Anexo I ve II) ve "Modelo de certificado válido a partir del 22/04/2026" yazıyor. AEAT mascotas sayfası ("Página actualizada: 23/septiembre/2026") hâlâ Reglamento (UE) 577/2013 Anexo II'ye atıf yapıyor. Karta yönetmelik numarası yazılmamalı. Temel kurallar iki sayfada aynı: mikroçip (ya da 03/07/2011 öncesi tatuaj), geçerli kuduz aşısı, listede olmayan ülke için serolojik test, pasaport yoksa zoosanitario sertifika + beyan, belirlenmiş yolcu giriş noktasından giriş.
- Türkiye'nin "kuduz listesinde" olup olmadığı İspanyol resmî sayfada ülke adıyla geçmiyor (liste EUR-Lex'te, izin verilen kaynak değil). Kartta "listede olmayan ülkelerden gelirken serolojik test gerekir; Türkiye'den gelenler için veterinerle ve giriş noktasında teyit edin" gibi yazılmalı, "Türkiye'den test şart" diye kesin yazılmamalı.
- AEAT sayfasında giriş noktaları listesi tarihi 15 Haziran 2021 görünüyor; kartta liste yerine "yetkili giriş noktası" denmeli.
- Ek bilgi: 15 haftadan küçük köpek/kedi/ferret (hurón) girişi yasak; 5 hayvandan fazlası ticari sayılır (AEAT sayfası).

### Kart 6 (sağlık sigortası)
- Sigorta şartı vize türüne bağlı. Estambul sayfalarına göre: residencia no lucrativa ve estudios için şart var; trabajo por cuenta ajena sayfasında sigorta kalemi yok (çalışan Seguridad Social kapsamına girer); teletrabajo (nómada digital) sayfasında şart var, kamu SGK kapsamı kanıtlanırsa gerekmiyor (kullanılmadı, kart başına 2 sınırı).
- "Muafiyet/katkı payı/bekleme süresi olmayacak" şartı Estambul sayfasında YOK (bazı başka konsolosluklar yazıyor). Kartta yazılmamalı.
- Öğrenci vizesi sigortası: "con prestaciones similares las concedidas por la cartera común básica ... válido para la duración de la estancia prevista". Oturum vizesi sigortası: "debe cubrir todos los riesgos asegurados por el sistema público de salud en España". İkisi aynı değil.
- Sayfalar tarihsiz; "Nuevas Tasas Consulares 2026" bağlantısı görünüyor, tutarlar kartta verilmemeli.
- Ek aday (kullanılmadı): Ankara Büyükelçiliği sayfaları ve inclusion.gob.es (403 verebilir).

### Kart 7 (kısa bilgiler)
- Para birimi: BdE sayfası "euro" dolaşımını ve İspanya'daki basım/dolaşım rolünü söylüyor; "İspanya'nın para birimi euro'dur" cümlesi tek başına açık geçmiyor (dolaylı). Ek aday: BOE'de euro'ya geçiş kanunu, aranmadı.
- Saat dilimi: "CET, UTC+1" ifadesi yalnız IGN Anuario makalesinde (PDF, bilimsel makale) var; BOE'de "UTC+1" ifadesi bulunamadı. BOE RD 236/2002: "en España existen dos horas oficiales, una para la Península y archipiélago balear y otra para el archipiélago canario" (Kanarya bir saat geride). PDF metin çıkarımı yazıcıya bağlı (ligatür); `hora de Europa central` ve `que corresponde al huso horario número +1` pypdf ile doğrulandı.
- Yaz saati takvimi: Orden PCM/186/2022 yalnız 2022-2026 kapsıyor (BOE-A-2022-4026). Bugün 2026-10-24; bu yıl 25 Ekim 2026 pazar günü sona eriyor. 2027 sonrası için İspanyol Orden bulunamadı. Kartta tarih yerine kural yazılmalı: son Mart pazarı / son Ekim pazarı.
- Dil: Anayasa m.3 (BOE konsolide metin): Kastilyaca devlet dili; diğer İspanyol dilleri ilgili özerk bölgelerde Statüleri uyarınca resmî. Hangi bölgede hangi dil, şehir sekmesinde.
