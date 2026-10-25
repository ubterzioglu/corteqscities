# oturum konusu: yazar boşlukları (25.10.2026)

15 aday kartın 15'i yazıldı (order 101-115). Kart 10 (Ortaklık Hukuku) yalnız kaynağın söylediği kadar yazıldı (kademe ve standstill yok), ertelenmedi.

## Kart bazında yazılmayan bilgi
- Kart 2 (Türk vatandaşı ulusal vize): başvurudan karara işlem süresi yazılmadı. 041 sayfasındaki "mindestens 15 Tage (in Einzelfällen bis zu 45 Tage)" ifadesi aynı sayfada Schengen başvuru akışı içinde geçiyor ve ulusal vize için ayrılmadığından alınmadı. Yazılan süre yalnız randevu bekleme süresidir (kayıttan başvuruya). Ücret 75 Euro (AufenthV md. 46); sayfadaki "max. 90 EUR" ibaresi yazılmadı. iDATA 12 Euro randevu bedeli (042) kart başına 2 kaynak sınırı nedeniyle alınmadı. Tarihe duyarlı (ücret, bekleme): valid_until null (kaynakta bitiş yok).
- Kart 3 (Mavi Kart): 2026 euro eşikleri elimizdeki kaynaklarda yok (Bundesagentur 03-2026 bülteni listede değil, BMI sayfası kapalı). Tutar yazılmadı; yalnız yasadaki yüzdeler (%50 ve %45,3) ve Bundesanzeiger ilanı kuralı yazıldı. Eşik euro olarak bulunursa karta eklenmeli ve valid_until 2026-12-31 yapılmalı. Şimdilik null.
- Kart 4 (Chancenkarte puan tablosu): tam metin sayfasındaki Anlage tablosu satır satır bölünmüş geldiği için ölçüt başına puan değerleri yazılmadı; yalnız asgari puan (6) ve puan veren ölçütlerin kendisi yazıldı. Puan değerleri istenirse tablo sayfası ayrıca düzenlenmeli.
- Kart 6 (aile birleşimi): Türk vatandaşına özgü Almanca muafiyeti kaynakta yok, yazılmadı. Konsolosluğun 12 aylık sertifika kuralı, A1 ve 75 Euro Merkblatt 01F'den. 040 (A1 sağlayıcı sınırlaması) ve AufenthV md. 46 kart başına 2 kaynak sınırı nedeniyle kullanılmadı. Ücret tarihe duyarlı: valid_until null.
- Kart 8 (vatandaşlık): eski vatandaşlıktan çıkma şartının kalktığı StAG md. 10(1) Nr. 4 "weggefallen" olarak görünüyor ama hükmün içeriği metinde yok; yazılmadı. Çoklu vatandaşlık yalnız BVA ifadesiyle ve "Almanların başka vatandaşlık edinmesi" bağlamı belirtilerek yazıldı. Türkiye'nin çifte vatandaşlık kuralı kapsam dışı. 3 yıllık hızlı yolun kaldırıldığı bilgisi (haber özeti) kullanılmadı.
- Kart 10 (Ortaklık Hukuku): ARB 1/80 kademeleri, Katma Protokol md. 41 standstill ve hakkın kimde doğduğu kaynakta yok, yazılmadı. Yazılan: AufenthG md. 4(1)-(2) (hak varsa Aufenthaltserlaubnis ile belgeleme, başvuru üzerine) ve AufenthV md. 52a (ücret Alman kimlik kartı ücreti düzeyinde; 24 yaş altında o yaşa ait kimlik ücreti). Kimlik kartı ücretinin euro tutarı kaynakta yok.
- Kart 11 (oturum belgesi ücretleri): eAT'nin PIN mektubu ve Express ücreti (md. 45a: +35 Euro) kaynak listesinde yok, yazılmadı. BAMF eAT sayfası (049) ve md. 52a (048) kart başına 2 kaynak sınırı nedeniyle bu kartta kullanılmadı; 048 kart 10'da kullanıldı. Kart eAT'yi adıyla değil "oturum belgesi" olarak anlatıyor (md. 45c metni "Dokument nach § 78 Absatz 1" diyor). Ücretler tarihe duyarlı: valid_until null.
- Kart 13 (serbest çalışan): başvuru belge listesi kaynakta yok, yazılmadı. 250.000/500.000 Euro ve 5-10 kişi istihdam eşikleri güncel md. 21'de yok, yazılmadı.
- Kart 14 (AB vatandaşı aile üyesi): kart başına 2 kaynak sınırı nedeniyle 056 (md. 2a: AB'li olmayan aile üyesi için vize gerekir, vize ücretsiz, Aufenthaltskarte sahibi vizeden muaf) kullanılmadı; kartın pratik değeri için ana döngü kart kaynaklarını 055+056 ya da 3 kaynağa çıkarmayı değerlendirebilir.
- Kart 12 (iş değişikliği): çalışanın kendi bildirim yükümlülüğü kaynakta yok; yalnız işverenin 4 haftalık bildirimi (md. 4a(5)) yazıldı.
- Kart 15 (§ 51): Türk vatandaşına özgü Ortaklık Hukuku (ARB 1/80 md. 7) kapsamındaki daha uzun yokluk tanımı kaynakta yok, yazılmadı.

## Kullanılmayan kaynaklar
- 040 (de:kaynak:040, Merkblatt: A1 sağlayıcıları), 042 (de:kaynak:042, Türk vatandaşı iDATA yolu), 056 (de:kaynak:056, FreizügG md. 2a), 049 (de:kaynak:049, BAMF eAT), kart başına 2 kaynak sınırı nedeniyle claim için kullanılmadı. 030 (AufenthG md. 7) de kullanılmadı (kart 1'de 029 ve 031 tercih edildi; "Aufenthaltserlaubnis süreli" bilgisi karta yazılmadı).

## Dikkat notları
- Karta yazılan 15 kartın 4'ü tarihe duyarlı (kart 2, 3, 6, 11); kaynaklarda bitiş tarihi olmadığı için valid_until.json'da null.
- Kart 4: puan veren ölçütler özetlendi; puan değerleri ve ölçüt başına ayrıntı kartta yok.
- Kart 1 ve 10: AB–Türkiye Ortaklık Anlaşması yalnız md. 4'ün metniyle anıldı.
- Kart 5: haftalık iş günü hesabı (2,5 gün) md. 16b(3) Nr. 2 metnine göre özetlendi; ayrıntılı yorum yok.

## Editör turu (G0, 25.10.2026)
- Yeni kaynaklar (snap_oturum-editor1): de:kaynak:204 (PAuswGebV § 1: kimlik kartı ücreti 46 Euro / 24 yaş altı 27,60 Euro; Ortaklık kartı), de:kaynak:205 (SVBezGrV 2026 § 4: yıllık prim tavanı 101.400 Euro; Mavi Kart kartı).
- Mavi Kart (kart 3): 2026 euro eşikleri hâlâ elimizdeki kaynaklarda yok; yalnız yüzdeler ve 2026 prim tavanı yazıldı. Euro karşılığı hesaplanmadı.
- Ortaklık Hukuku (kart 10): kart başına 2 kaynak sınırı için AufenthG § 4 (de:kaynak:029) karttan çıkarıldı; "hakkı Aufenthaltserlaubnis ile belgele" bilgisi oturum-belgesi-turleri kartında duruyor. oturum-belgesi-ucretleri kartında Ortaklık Hukuku ücret uyarısı, üçüncü kaynak (de:kaynak:048) gerektirdiği için eklenemedi.
- Vatandaşlık (kart 8): Almanya'ya naturalize olan yabancı için çifte vatandaşlık (Türk vatandaşlığından çıkma gerekir mi) açıkça anlatan bir resmî Alman sayfası kaynak dizininde yok; karta yazılmadı. BVA notu ters yönlü olduğu için silindi (de:kaynak:053 kartta kullanılmıyor).
- Eş birleşimi (kart 6): AB Adalet Divanı Dogan kararı (Türk işçilerin eşleri için A1 şartı) kaynak dizininde yok; yazılmadı.
- AB vatandaşı aile üyesi (kart 14): sıradan Alman vatandaşının yabancı eşi için ayrı kural (§ 28) üçüncü kaynak gerektirdiği için bu kartta anlatılmadı; yalnız Alman serbest dolaşım hakkını kullananların aile üyelerinin kapsama girdiği yazıldı.
- Çalışanın kendi bildirim yükümlülüğü ve işveren bildirimi: iş değiştirme kartından işveren bildirimi cümlesi çıkarıldı (okuyucuya yönelik değil).

## Editör turu G0b (25.10.2026) - açık kalanlar
- oturum-belgesi-ucretleri: Ortaklık Hukuku (Assoziationsberechtigte) kapsamındaki okuyucu için ücretin farklı olduğu (AufenthV §52a: Alman kimlik kartı ücreti) uyarısı bu kartta yok. Kartın kaynakları 046 ve 047 (2 kaynak sınırı); 047 çıkarılırsa 67 Euro bilgisi düşer, §45c bilgisinin ayrı karta taşınması karar gereği yapılmadı. Çözüm yolu: ana döngü kararıyla kaynak değişikliği.
- ab-vatandasi-turk-aile-uyesi-oturum-karti: Alman vatandaşının sıradan eşi için nereye bakılacağı (AufenthG §28) bu kartın kaynaklarında yok; es-icin-aile-birlesimi-vizesi kartı §28'i anlatıyor.
- es-icin-aile-birlesimi-vizesi: Nüfus Kayıt Örneği için konsolosluk (apostil istemeyen Merkblatt) ile Alman makamları (apostil) ayrımı kaynakta açık değil.
- alman-vatandasligi-sartlari: StAG §12a (de:kaynak:269) eklendi; yabancı mahkeme kararlarının değerlendirilmesi (§12a Abs. 2) kartta yazılmadı.
