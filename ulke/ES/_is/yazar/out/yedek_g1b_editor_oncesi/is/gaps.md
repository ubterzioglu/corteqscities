# ES ulusal paketi, konu "is": boşluklar

Genel: 11 kart, order 301-311. Tüm alıntılar kaynak metninde doğrulandı. Kartlar şehir-nötr. valid_until.json: tarihe duyarlı 5 karttan 4'ü 2026-12-31 (SMI, tatil listesi, bordro oranları, otonom tablosu), paro kartı null (kaynak sayfada yıl damgası yok).

## Kart bazında yazılmayanlar
- Kart 2 (SMI): "14 ödeme" ve 14x1.221 hesabı yazılmadı. 17.094 euro yalnız kaynaktaki bağlamla (madde 3, mevcut ücretlerin yıllık karşılaştırma tabanı) yazıldı. Fazla mesai kuralı yazılmadı.
- Kart 3 (tatil): 2027 listesi (BOE-A-2026-21254, 13 Ekim 2026) kasten eklenmedi: kart başına 2 kaynak sınırı dolu (074, 077) ve kart "2026 listesi" diye yıl damgalı; 2027 için ayrı kart gerekir. Yıllık izin ücreti ve hak ediş ayrıntısı yazılmadı. Bölgeye özgü tatil günleri tek tek yazılmadı, yalnız 7 değiştirilemeyen ulusal gün ve 6 Ocak.
- Kart 4 (bordro): devengos/deducciones kalem adları yazılmadı (resmî bordro modeli tablosu metne düşmedi). İşsizlik, FP ve MEI işçi payları yazılmadı.
- Kart 5 (finiquito): finiquito içeriği (kullanılmamış izin, ek maaşın orantısı) ve imzanın hukuki sonucu için resmî derin sayfa yok, yazılmadı.
- Kart 6 (despido): despido objetivo/colectivo için yalnız ET art. 51-53 metnindeki eşik ve süreler yazıldı; ayrıntılı usul (görüşme dönemi içeriği, seçim kriterleri) yazılmadı. 2025 tazminat yeterliliği tartışması resmî sayfada yok, yazılmadı.
- Kart 7 (paro): 2026 ödenek üst/alt tutarları (IPREM'e bağlı) yazılmadı. Yabancılar için NIE/çalışma izni ayrıntıları bu sayfalarda yok.
- Kart 8 (iş kazası): sosyal güvenlik sayfası kaynak listesinden elendiği için yalnız LGSS art. 156-158 yazıldı. Geçici iş göremezlik süresi (365 + 180 gün), ödenek oranları ve prim şartları yazılmadı: LGSS art. 169-172'nin görünen sürümü 1 Aralık 2026'da yürürlüğe girecek RDL 31/2026 değişikliğini içeriyor ("No vigente aún"), mevcut sürümle karıştırma riski var.
- Kart 9 (otonom): aylık euro cuota, tarifa plana tutarı, alta süresi ("faaliyetten önce 60 güne kadar"), mesleki risk oranı (%1,30) ve MEI oranı (%0,90) yazılmadı. Yabancı uyruklu için çalışma/oturum izni şartı bu kaynaklarda yok.
- Kart 10 (ebeveyn izni): yalnız ET art. 48.4-48.6 hafta sayıları ve LGSS art. 178-179 yazıldı. Baz matrah hesabı (olaydan iki ay önceki ay prim bazı), lactancia ve riesgo embarazo yazılmadı. Prematüre doğumda uzayan süre yazılmadı.
- Kart 11 (diploma): meslek bazlı tanıma (düzenlenmiş meslekler, Valida-TE, mesleğe özel kurullar) yazılmadı. Harç tutarı, işlem süresi (üniversite dışı yol) ve üniversite dışı başvurunun adım adım usulü kaynakta yok. Üniversite dışı sayfanın yayıncı kurum adı sayfa metninde geçmediği için kartta kurum adı verilmedi.

## Genel kısıt
- mites.gob.es sayfaları sertifika hatası nedeniyle açılamadı; hiçbir kart ona dayanmıyor.
- prestaciones.seg-social.es JavaScript ile yükleniyor, metin boş; kullanılmadı.
- sepe.es /en/ sayfaları makine çevirisi, kullanılmadı.
