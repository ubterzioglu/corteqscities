# 4 Augen Prinzip: GUNLUK_2026-10-22_pilot.md bağımsız incelemesi

- **İncelenen:** `GUNLUK_2026-10-22_pilot.md` (2. oturum günlüğü)
- **İnceleyen:** Claude (Cowork, ayrı oturum); yalnız okuma, başka dosya değiştirilmedi
- **Tarih:** 22.10.2026
- **Öncelik:** token harcamasını azaltmak. Bulgular bu yüzden token etkisine göre sıralandı.
- **Kural:** Düzeltmeyi yerel Claude Code yapar; "Durum" sütununa `Kapandı – <ne, hangi dosya>` yazar.

Sütunlar: **Nerede** (günlükte hangi bölüm) · **Kazanç** (düzeltilirse ne kazanılır) · **Neden bulunamadı** (yazan Claude neden görmedi).
Token etkisi: **Yüksek** = tur/ajan düzeyinde tasarruf · **Orta** = tekrar eden arama/yeniden iş · **Düşük** = yalnız belge doğruluğu.
Tasarruf rakamları günlükteki ajan raporlarından türetilmiş **tahmindir**; ölçüm `phase_usage report` ile yapılmalı.

---

## A. Token etkisi YÜKSEK

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| T1 | Ülke paketi yok (`country_pack: null`); Hollanda'nın ulusal kartları (oturum, resmi, para, sağlık, iş, aile) her NL şehri için yeniden yazılacak. | 3.5 | En büyük kalem. Kart yazımı ≈2,67 M token; 12 konunun çoğu ulusal. Bir kez "NL ülke paketi" yazılırsa sonraki her NL şehrinde bu payın büyük kısmı (tahmin: yarısından fazlası) harcanmaz. | Pilotta kıyas için bilerek yeniden yazıldı; doğru karar, ama ileriye dönük maliyet notu düşülmemiş. Yazar o anki işe odaklıydı. | Açık |
| B2 | Faz 3 kapanış eşiği yok ("kabul edilebilirse"). | 9.2, 3.8B | Eşik yoksa "düzelt → denetle" döngüsü bitmez. Bir Opus denetimi ≈371 bin, bir editör turu 6 ajan. Eşik bir fazladan turu bile önlerse yüz binlerce token. Öneri: yanlış iddia = 0, "düzelt" ≤ %10; sonuç görülmeden yazılır. | Günlük editörler çalışırken yazıldı; yazar kendi sonucunu beklerken ölçüt koyma ihtiyacını görmez (onay eğilimi). | Açık |
| T2 | Editörler konudaki **bütün** kartları (270) baştan gözden geçiriyor. | 3.8C | Denetimde hata kural kartlarında çıktı. Gözden geçirme yalnız kural/koşul içeren kartlarla sınırlansa editör turu belirgin küçülür. | Denetim sonucu "diğer kural kartlarında da hata olabilir" dedi; yazar bunu "hepsini oku" diye genişletti. | Açık |
| T3 | Kart sayısı hedefi (18–26/konu) var, kart **planı** yok → para'da 6 kart tek vergi anlaşmasından yazıldı, şimdi silinecek. | 3.7, 3.8C | Kart başına ≈10 bin token (2,67 M / 270). Yazımdan önce ucuz bir adımda yalnız başlık listesi onaylansa yazılıp silinen kart olmaz. | Talimat sayı hedefi verdi; ajan sayıyı doldurdu. Yazar sorunu gördü ama kök nedeni (plan adımı yok) skill'e yazmadı. | Açık |

## B. Token etkisi ORTA

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| T4 | Bilgi taşımayan sayfalar (JS ile yüklenen, yalnız menü) yazarlara verildi; yazarlar boş kaynakta veri aradı, sonra ek arama ajanı (≈203 bin) + editör turu gerekti. | 3.6, 3.7, 5.1 | Yazımdan **önce** konu başına `must_contain` kapsama kontrolü: eksikler yazımdan önce kapanır, ikinci tur gerekmez. | Sorun 5.1'de araç eksiği olarak görüldü ama token maliyetine bağlanmadı. | Açık |
| T5 | 23 görsel şema (`visual_json`) yazıldı, sonra silindi. | 3.7 | Şema, adımlar kesinleştikten sonra ayrı küçük adımda üretilirse boşa yazım olmaz. | Yazar talimatı şemayı kartla aynı anda istiyor; silme "kapı çalıştı" diye olumlu görüldü. | Açık |
| B8 | SVB içeriği (kinderbijslag, TR–NL sosyal güvenlik) için "insan bakabilir" denmiş, sorumlu/tarih yok. | 3.8A, 6 | Her turda ajanlar SVB'yi yeniden arıyor. İnsan 5 dakikada bakarsa tekrar eden arama biter. | "Bot engelini aşmıyoruz" kararı doğru verildi, ama yerine kimin bakacağı atanmadı. | Açık |
| B4 | İki açık konu (SVB, teslimat kimliği harfi) manifest'e yazılmamış. | 6 | Manifest'te yoksa sonraki oturum sorunları yeniden keşfeder (ek okuma ve arama). | Günlük iş yarıdayken yazıldı. | Açık |
| B7 | Faz 4: yeme-içme 4, çocuklu gezi 2 aday; sözleşme her grupta mekân istiyor. | 3.9 | Ajan Wikidata'da boşuna aramaz; resmî şehir kaynağı listesi baştan verilir. | Faz 4 hazırlığı yarım kaldı. | Açık |
| B9 | İkinci denetim örneklemi tanımlanırken editörün değiştirdiği kartlar ayrıca ele alınmıyor. | 3.8C, 9.2 | Gizli hata sonradan daha pahalı turla çıkar. İki ayrı oran (değişen kart / denetlenmemiş kural kartı) hangi işin tekrar edileceğini daraltır. | Denetim planı editör turundan önce yazıldı. | Açık |
| B6 | Miami token rakamı belgede yok. | 7 | Tasarruf ölçülemezse AMAÇ 1 kanıtlanamaz; hangi optimizasyonun işe yaradığı bilinmez. | Yazar yalnız kendi ajanlarını saydı; kıyas tabanı başka belgede. | Açık |

## C. Token etkisi DÜŞÜK (yalnız belge doğruluğu)

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| B3 | "1.549 sayıda 1 hata" fazla güçlü; `claim_check` sayının kaynakta geçtiğini doğrular, doğru bağlamda kullanıldığını değil. | 1, 3.7 | Yanlış güven önlenir; denetim bütçesi doğru yere (kural kartları) gider. | Yazar kendi kurduğu kapının sonucunu değerlendirdi. | Açık |
| B1 | Mekân grup toplamı 370, metinde 368. | 3.9 | Doğruluk. | Yazar tablolarını toplamıyor (bölüm 11: iki kez yanlış toplam). | Açık |
| B5 | Saat dilimi karışık (fazlar UTC, yazım anı yerel). | Başlık, 3.5–3.7 | Başka oturum sırayı doğru kurar. | Araçlar UTC, yazar yerel saatle yazdı. | Açık |

---

## Neden "diğer Claude" bunları bulmadı? (ortak nedenler)

1. **Kendi işini denetleme:** Yazan aynı oturumdu; kendi kararlarını doğru varsayar. Bu, skill'in kendi kuralıdır ("kendini onaylamaz"), günlüğe uygulanmamış.
2. **Kalite odaklıydı, maliyet odaklı değil:** Kapıların hepsi doğruluk ölçüyor; hiçbir kapı "bu adım kaç token harcadı, gerekli miydi" sormuyor.
3. **İş sürerken yazıldı:** 6 ajan çalışırken yazıldığı için kapanmamış konular "sonra" kaldı.
4. **Toplam kontrolü yok:** Sayılar script'ten geliyor ama tablo toplamları elle yazılıyor.

## Öneri: maliyet kapısı

Her faz sonunda `phase_usage` ile token yazılsın ve şu soru cevaplansın: "Bu fazda yazılıp silinen / yeniden yapılan iş var mı?" (T3, T5 türü kayıplar böyle görünür hale gelir).

## Güçlü yanlar (korunmalı)

- Ajan adres bulur, script indirir ve doğrular (7 uydurma adres yakalandı).
- `must_contain` kanıtı kendi kopyamızda aranıyor.
- Yazar ≠ editör ≠ denetçi ayrımı.
- Kaynak çelişkisinde resmî kurum esas.
- Bölüm 11'deki hata kaydı.

---
---

# Ek: OTURUM_RAPORU_2026-10-22_ayrintili.md incelemesi (1. oturum: analiz + araç kutusu)

Sayı kontrolü: Miami tablosu (girdi %, çıktı %, süre, 48,4 toplamı), ön eleme karışıklık tablosu (272; 16/23; %26), `checks.yaml` dağılımları (120 / 110 / 62 = 42+18+2) ve pafta oranları (24–39 kat) **tutuyor**. Bulgular aşağıda; aynı sınıflandırma kullanıldı.

## A. Token etkisi YÜKSEK

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| R1 | Bu oturumun ana döngüsü, raporun teşhis ettiği hatanın kendisi: 393 çağrıda 112,3 M girdi → **çağrı başına ≈286 K**. Miami'de bu ≈153 K, aynı oturumun iş akışı ajanlarında ≈149 K (67,3 M / 451). Toplam 179,6 M girdi, Miami'nin bütün şehir üretiminin (27,2 M) **≈6,6 katı**. | Bölüm 10 | Ana döngü çağrı başına bağlamı yarıya inse aynı iş için on milyonlarca girdi token'ı daha az. Bu, en büyük tek kalem. | Rapor sorunu gördü ve yazdı ("analiz ettiğimiz sorunun ta kendisi") ama **kurala çevirmedi**. | Açık |
| R2 | SKILL.md'de "ana döngü yalnız yönetir" kuralı var, ama **oturum bölme kuralı yok** (faz başına yeni oturum / bağlam tavanı / devir tetikleyicisi). Pilot da 3+ fazı tek oturumda yürüttü. manifest.json kaldığı yeri zaten tutuyor, yani bölmek ucuz. | SKILL.md satır 8, 38 (kontrol edildi) | R1'deki şişmenin pilotta ve her şehirde tekrarını önler. Öneri: her faz (en geç her 2 faz) yeni oturumda; manifest + tek satırlık durum notuyla başla. | Manifest "oturum kesilirse" diye tasarlandı, "oturumu bilerek kes" diye değil. | Açık |
| R3 | İki oturum **farklı birimle** token raporluyor: 1. oturum `phase_usage` ile girdi/önbellek dışı/çıktı (tekilleştirilmiş); pilot günlüğü "ajan bildirimindeki toplam token" (önbellek dahil olabilir, tekilleştirme yok, rapor 2,4 kat tekrar uyarıyor). Bu sayılar birbiriyle ve Miami ile kıyaslanamaz. | Bölüm 8.4, 10; günlük bölüm 7 | Hangi önlemin token düşürdüğü ancak tek ölçüyle görülür. Öneri: her yerde aynı üçlü (önbellek dışı girdi, önbellek okuması, çıktı) + maliyet-eşdeğeri. | Her oturum kendi aracını kullandı; ortak birim tanımı yok. (Bkz. B6.) | Açık |
| R4 | Miami'de "kart başına 17,2 K girdi, 169 çıktı": pahalı olan çıktı değil, her çağrıda taşınan bağlam. Pilotta yazar ajanları yine konu başına bütün kaynak kopyalarını okudu (≈1,02 M karakter toplam). | Bölüm 4.4; günlük 3.6–3.7 | Yazar ajanına kaynak metninin tamamı yerine yalnız ilgili bölüm (ör. `must_contain` çevresi / başlık bazlı parça) verilirse yazım girdisi düşer. Ölçülmeli. | Kalite odaklı tasarım "her şeyi oku" yönünde; girdi boyutu kapısı yok. | Açık |

## B. Token etkisi ORTA

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| R5 | Ön eleme görsel incelemeyi %26'ya indiriyor, ama kaçan 7 yanlış fotoğraf yalnız gözle yakalanıyor. Yani tasarruf ancak **tüm karelerin ucuz pafta taraması** (30'lu, ≈16 K) korunursa geçerli. | Bölüm 1, 8.3 | Yanlış okuma: "yalnız işaretlileri incele" uygulanırsa kalite düşer → denetimde geri dönüş turu (pahalı). Kural açık yazılmalı: genel pafta herkese, yakın inceleme işaretlilere. | Özet satırı iki ayrı adımı tek orana indirmiş. | Açık |
| R6 | v7 prompt'u (≈15–18 K) yerine ≈5 K sözleşme özeti önerildi; pilot ajan talimatlarında hangi metinlerin yüklendiği ve toplam başlangıç bağlamı ölçülmemiş. | Bölüm 4.5 | Her alt ajanda başlangıç yükü (talimat + özet + ortak talimat) ölçülürse 12–16 ajanlık turda kazanç doğrulanır. | Öneri uygulandı ama etkisi ölçüme bağlanmadı. | Açık |
| R7 | Bir ajan oturum limitine takıldı, iş bölündü. | Bölüm 3 (13:45–14:05) | Limit/yeniden başlama yeniden okuma demek. Ajan başına iş boyutu sınırı (dosya/kart sayısı) konmalı. | Tek seferlik olay olarak görüldü. | Açık |

## C. Token etkisi DÜŞÜK (doğruluk / belge)

| No | Bulgu | Nerede | Kazanç | Neden bulunamadı | Durum |
|---|---|---|---|---|---|
| R8 | qwen zaman çizelgesi parçaları 15+72+40+5+52+10 = **194 dk (3 sa 14 dk)**; başlıkta "≈4 sa 25 dk". ≈71 dk açıklanmamış. | Bölüm 4.2 | Doğruluk; açıklanmayan süre bekleme/yeniden deneme ise bu da bir israf kalemi olabilir. | Parçalar toplanmamış. | Açık |
| R9 | "Eindhoven'ın 12 bilgi hatası" deniyor; denetimde B01–B18 var. 12'nin hangi alt küme olduğu yazılmamış. | Bölüm 1, 8.2 | "11/12" başarı oranının kapsamı netleşir. | Bağlam yazanın kafasında. | Açık |
| R10 | Doğrulayıcı sayı farkı 364 / 365 / 363 hâlâ açıklanmamış. | 8.1, 12.3 | Kapı güvenilirliği. | Açık nokta olarak zaten kayıtlı. | Açık |
| R11 | Bu rapor saatleri **yerel**, pilot günlüğü **UTC** yazıyor (1. oturum ~15:00 yerel biter, pilot 13:19 UTC = 15:19 yerel başlar). B5'i doğrular. | Bölüm 3; günlük 3.5 | Sıra karışmaz. | Belge başına farklı alışkanlık. | Açık |

## Bu raporda iyi olan (korunmalı)

- Kendi sayılarını ikinci script'le yeniden üretmiş (269 → 272, karışıklık tablosu).
- `phase_usage` tekilleştirme sorununu (≈2,4 kat şişme) bulup düzeltmiş.
- Erişilemeyen veriyi (`kilo.db`) zorlamamış, tahmini "tahmin" diye işaretlemiş.
- Bölüm 13'te doğrulamadığı şeyi "doğrulanmadı" diye yazmış.

## İki belge birlikte: en büyük 3 token kaldıracı

1. **Oturum bölme kuralı** (R1, R2): ana döngünün çağrı başına bağlamı en büyük kalem.
2. **NL ülke paketi** (T1): ulusal kartlar bir kez yazılır.
3. **Tek token ölçüsü + faz sonu maliyet kapısı** (R3, B6): hangi önlemin işe yaradığı ancak böyle görülür.

---

## İş kaydı

| Tarih-Saat (Berlin) | İş | Durum | Dosya | Not |
|---|---|---|---|---|
| 22.10.2026 | GUNLUK_2026-10-22_pilot.md 4 göz incelemesi (B1–B9, T1–T5, token odaklı) | Biten | bu dosya, bölüm A–C | Düzeltmeler yerel Claude Code'da; Durum sütunları açık |
| 22.10.2026 | OTURUM_RAPORU_2026-10-22_ayrintili.md 4 göz incelemesi (R1–R11) | Biten | bu dosya, "Ek" bölümü | En büyük kaldıraçlar: oturum bölme, NL ülke paketi, tek token ölçüsü |
| — | Bulguların Claude Code tarafından işlenmesi | Açık | — | Kapanışlar sonra tekrar incelenecek |
