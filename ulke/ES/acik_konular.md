# İspanya ulusal paketi v1 — açık konular (2026-10-24)

Kapsam: 27 kart (oturum 14, resmi 13). Üç bağımsız denetim turundan sonra: 0 ciddi, 2 orta (kapatıldı), 22 küçük bulgu açık.
Kural: şehir yazarı bu boşlukları kendi bilgisinden doldurmaz; kaynaklı ek kart ya da bölge/şehir katmanı yazar.

## Pakette olmayan kart
- NIE/TIE randevusu: ulusal resmî sayfalar bot engeli veriyor, usul ofise göre değişiyor → şehir katmanı.

## Kaynak bulunamadığı için kartlarda olmayan bilgi
- Apostil ücreti; Türkiye'deki apostil makamının adı (kart yalnız İspanya'da düzenlenen belgeleri kapsar).
- Noter ücretine KDV ve diğer masraflar; noter ölçeğinde matriz yaprağı ek ücreti.
- Vatandaşlık başvuru harcı; vatandaşlığın Türk vatandaşlığına etkisi; önceden DELE A2 almış olanın muafiyeti (RD 1004/2015 md. 6.5).
- Oturum yenilemede yenileme şartları ve 183 gün kuralı.
- Cl@ve için yabancıdan istenen belgeler.
- Arraigo harcı (38,28), NLV harcı (10,94), vize ücretleri (kaynak 2 kaynak sınırına takıldı; ikisi de Orden PJC/617/2025'te).
- IPREM 2026 (600 euro) resmî sayfada yalnız Yeni Delhi konsolosluk sayfasında; kartlarda euro tutarı olarak kullanılmadı.
- Ehliyet harç tutarı: DGT sayfasında yer tutucu (XX,XX).

## Canlı doğrulanamayan noktalar (denetçiler)
- İstanbul Başkonsolosluğu sayfası 503 verdi; "Nuevas Tasas Consulares 2026" ve "Auto de 12 de octubre de 2026" duyuruları okunmadı. Dijital göçebe, NLV ve apostil kartları anlık görüntüye dayanıyor.
- Yargıtay 2026 kararlarının tüm iptal listesi okunmadı.
- Código Civil md. 22'nin 2026'da değişip değişmediği canlı doğrulanmadı (anlık görüntüde son güncelleme 2021).
- claims, Bağlantılar ve valid_until dosyaları satır satır insan ya da model gözüyle denetlenmedi; yalnız script denetiminden geçti (alıntı kaynak metninde, kimlikler tutarlı).

## Bilinen küçük kusurlar
- dijital-gocebe: 34.188 euro kartın kendi türetmesi (yıllık SMI × yüzde 200), `steps`'te çekincesiz.
- kar-amaci-gutmeyen: karar süresi cümlesi çıkarıldı; Delhi sayfası 3 ay, RD md. 63.4 bir ay + sessizlik = ret diyor, kart bu çelişkiyi söylemiyor. `cost` boş.
- arraigo: EX10 / 790-012 kaynağı zayıf; "yalnız şahsen" cümlesi md. 197 ile tam örtüşmüyor; ikinci fırsatta yenilememe nedeni ve sosyal-eğitimde 30 saat sınırı eksik.
- brexit: Türk aile üyesi için form (EX21) ve belge yenileme anlatılmıyor.
- belge-ceviri: "Adalet Bakanlığı adli ve idari belgelerin tek mercii" kaynakta açık değil (yalnız noter için "únicamente").
- noter: "folio" sayfa diye çevrilmiş; "ek olarak uygulanır" cümlesi yüzde 5 dışındaki indirimleri de kapsıyor gibi okunur.

## Güncellik
- valid_until yazılan kartlar: dijital-gocebe-vizesi ve kar-amaci-gutmeyen-oturum-vizesi (2026-12-31). Diğer harç kartlarında kaynak yıl etiketi yok (polis harç sayfası 24.10.2026'da güncel, Orden PJC/617/2025 ile aynı); Ocak'ta yeniden bakılmalı.

---
# Grup 1 eki (paket v2: 59 kart, para + iş + fatura eklendi) — 2026-10-24

Süreç: kaynak keşfi → yazar → bağımsız denetim → düzeltme editörü. Editör sonrası ikinci bir bağımsız denetim YAPILMADI (v1'de yapılmıştı, 0 ciddi çıkmıştı). Editörün yeniden yazdığı cümleler yalnız script denetiminden geçti (alıntı kaynak metninde var).

## Kartlara yazılmayan bilgiler (resmî kaynak bulunamadı ya da 2 kaynak sınırı)
- para: bankadan NIE/pasaport şartı; "gestor ne zaman gerekir" yargısı; Türkiye-İspanya sosyal güvenlik düzeni; Baskiya/Navarra foral IRPF ve mukim olmayan (IRNR) rejimi; Beckham başvuru yolu ve süresi; Türkiye havalesinin SEPA dışı sayıldığı; işsizlik/FOGASA/meslek eğitimi prim oranları; Renta 2026 kampanya tarihleri; IVA geçici elektrik/gaz oranı.
- is: SMI için "14 ödeme" ve 14×1.221 hesabı (RD metninde yok); otonom aylık euro cuota ve alta süresi; paro 2026 üst/alt tutar sınırları; finiquito içeriği; meslek bazlı tanıma; yabancı için otonom çalışma izni şartı; 2027 tatil listesi (BOE-A-2026-21254, kart 2 kaynak sınırında).
- fatura: güncel IVA, güç değişikliği ücreti, TUR tutarları, taahhüt cezası hesabı ve numara taşıma; 2.0TD tanımı (kart kaynaklarında yok); borç nedeniyle elektrik kesintisi; gaz şikâyet yolu; Katalonya için yedek fon dışındaki apartman kuralları (çağrı süresi, devir sorumluluğu).

## Doğrulanmayan ya da dikkat isteyen noktalar
- Renta kartı: 2025 gelirinin kampanyası kapandı; kart geçmiş kampanyayı tarihli anlatıyor, sonraki kampanya tarihi yayımlanınca güncellenmeli.
- IBAN kartı: alıcı adı kontrolü "9 Ekim 2025'ten beri" — resmî sayfa yılı yazmıyor (yıl sayfa tarihinden çıkarım).
- Bizum kartı: kaynak 20.07.2021 tarihli; güncel resmî sayfa yok, cümleler tarihli yazıldı.
- İş kazası kartı: LGSS 169-172 maddeleri 1 Aralık 2026'da değişiyor (RDL 31/2026); kart bu maddelere dayanmıyor.
- Fatura kart 9 (apartman): Katalonya dışı genel kural (Ley 49/1960) olarak çerçevelendi; Katalonya için yalnız yedek fon (BOE Ley 5/2006 md. 553-6). Navarra/Bask özel rejimleri araştırılmadı.
- mites.gob.es sertifika hatası verdi; hiçbir iş kartı o siteye dayanmıyor.

## Güncellik (2027'ye girerken)
- valid_until 2026-12-31 olan 7 kart 1 Ocak 2027'de yeniden doğrulanmalı: dijital göçebe, NLV, SMI 2026, yıllık izin ve tatiller 2026, bordro, otonom prim tablosu, bono social. country_apply bunları bayat sayıp yeniden denetime alıyor (denendi).

## v3 notu (editör sonrası dar denetim + son düzeltme turu)
- Editör sonrası bağımsız denetim yapıldı (para 0 ciddi/1 orta, iş 0/0, fatura 0/4); orta bulgular ve seçili küçükler son turda kapatıldı. Kalan küçük bulgular raporlarda: yazar\out\denetim_g1b_*.md.
- Bono social kartı: kWh sınırları BOE Anexo I'e göre hane bileşimiyle yazıldı; kaynak sınırı yüzünden şikâyet adımı karttan çıktı (şikâyet kart "elektrik-ve-telekom-sikayet-yollari" kartında).
- Elektrik aboneliği kartı: MITECO "her an cezasız çıkar" cümlesi çıkarıldı (CNMC'nin şartlı cezası ile uzlaştırılamadı).
- Bizum kartı: güncel resmî sayfa yok; cümleler 2021 tarihli kaynağa bağlı.
- Doğrulama ölçüsü: v3'te editör sonrası ikinci denetimden sonra yapılan son düzeltmeler yalnız script denetiminden geçti.
