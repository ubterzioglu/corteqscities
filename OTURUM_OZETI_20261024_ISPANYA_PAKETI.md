# Oturum özeti: İspanya ulusal ön araştırma paketi — son durum (24.10.2026)

Bu belge başka bir Claude oturumuna devir içindir. Önce `OTURUM_OZETI_20261024.md` (Bakersfield karşılaştırması, skill düzeltmeleri) okunmuş olmalı; bu belge onun devamıdır.

## 1. Amaç ve kapsam
Amaç: İspanya'daki 11 şehirde (Barcelona hariç: Alicante, Bilbao, Madrid, Málaga, Marbella, Palma, Sevilla, Tarragona, Tenerife, Valensiya, Zaragoza) aynı ulusal bilgiyi her şehirde yeniden araştırmamak. Ulusal bilgi bir kez araştırılıp "ülke paketi" olarak saklanır; şehirde yalnız şehre/bölgeye özgü iş yapılır.
Plan dosyası: `C:\Users\baris-terzioglu\.claude\plans\linear-inventing-thacker.md` (üç katman: ulusal / bölge / şehir; ilk şehir önerisi Sevilla).

## 2. Kullanıcı kuralları (bağlayıcı)
- **Şehirleri paralel yapma** (kalite düşüyor); sırayla, kullanıcı söyledikçe. (Aynı şehrin konuları paralel çalışabilir; bunu yaptık.)
- **İspanya bilgisi eski 3 skill'e (`city-pack`, `city-audit`, `city-preview`) girmeyecek.** Deneme tamamen `corteqs-skills\deneme_ulke_paketi\` altında. Eski skill dosyalarına yalnız İspanya'dan bağımsız, genel şehir çıktısı iyileştirmesi için dokunulabilir. Bu turda eski skill/toolkit/test dosyalarında hiçbir değişiklik yapılmadı.
- Sade Türkçe, jargonsuz, kararlar tek öneriyle. Maliyete (token, süre) çok hassas: önce script, ajan son çare, bütçe koy. Ölçülmeyeni ölçülmüş gibi sunma, kendi hatanı söyle.
- Hesap iki kez değişti; haftalık limite bir kez takıldık (ajanlar yarım iş bıraktı). Ajanlara "bulduğunu her 3-10 adımda dosyaya ekle" talimatı verildi, kayıp olmadı.

## 3. Şu anki durum: paket v4 — 80 kart
Konum: `C:\temp_private\corteqs\0000_newera\ulke\ES\` (`pack.json` sürüm 4, `Yanıtlar.ulusal.jsonl`, `Bağlantılar.ulusal.jsonl`, `claims\ulusal.jsonl`, `kaynak_dizini.jsonl`, `kaynaklar\` (100 kaynak kopyası), `acik_konular.md`; çalışma klasörü `_is\`).

| Konu | Kart | Yazılma süreci |
|---|---|---|
| oturum | 14 | yazar + 3 denetim + 2 editör (v1) |
| resmi | 13 | yazar + 3 denetim + 2 editör (v1) |
| para | 12 | keşif + yazar + denetim + editör + dar denetim + son düzeltme |
| iş | 11 | aynı |
| fatura | 9 | aynı |
| sağlık | 7 | keşif + yazar + denetim + editör |
| ev | 6 | aynı |
| planlama | 8 | aynı (7 aday kart; kaynak sınırı yüzünden biri ikiye bölündü) |

Toplam 1528 iddia (claim), 135 bağlantı, 100 resmî kaynak, 13 tarihli kart (`valid_until`: 7 kart 2026-12-31, 6 ev kartı 2026-11-05).
Yazılmayan konu: `kesif` (ulusal kart yok, şehre özgü). **Kalan: grup 3 = aile (5), ulaşım (5), günlük yaşam (5) = 15 aday kart** (liste: `ES_aday_kartlar_kalan_konular.md`). Bitince toplam ~95 kart.
NIE/TIE randevu kartı pakette YOK (resmî sayfalar bot engeli veriyor, usul ofise göre değişir) → şehir katmanı.

## 4. Araçlar (hepsi `corteqs-skills\deneme_ulke_paketi\`)
- `country_apply.py`: `apply` (paket kartlarını şehrin `_is` klasörüne uygular: kimlik/order yeniden kurulur, `{sehir}` doldurulur, kaynaklar AĞSIZ yerel kopyalanır, `ulke_kart_kaydi.jsonl` yazılır; `valid_until` geçmiş kart "stale" sayılıp kopyalanmaz) ve `audit-scope` (pakette denetlenmiş + şehirde değişmemiş + süresi geçmemiş kart claim denetimini atlar; değişen/bayat kart "audit"e düşer). `add_sources.py`'nin kilit ve kimlik mantığını yeniden kullanır. 16 test (`test_country_apply.py`) geçiyor: `python -X utf8 -m pytest corteqs-skills\deneme_ulke_paketi\test_country_apply.py -q`. Toolkit'in kendi testleri (2445) bu işle değişmedi.
- `pack_build.py`: yazar çıktısından (`_is\yazar\out\<konu>\`) paketi baştan kurar. `TOPICS` listesinde 8 konu var; yeni konu eklenince listeye eklenmeli. Komut: `python -X utf8 pack_build.py <ulke\ES> --country ES --version <N> --built <tarih>`.
- `pack_check.py <ES\_is> <konu>`: yazar çıktısını script ile denetler (alanlar, kart başına ≤2 kaynak, her iddia alıntısının kaynak metninde geçmesi, şehir adı, yasak "teyit et" kalıbı, bağlantı ve claim varlığı). Yazar/editör "doğruladım" dese de önce bu çalıştırılır.
- `kaynak_listesi.py <ES\_is> <konu>`: `add_sources` sonucundan (eklenen.json) yazara verilecek `yazar\<konu>_kaynaklar.jsonl`'i üretir.
- `YAZAR_KURALLARI.md`: yazar ek kuralları (denetimlerden çıkan dersler; her yazar/editör talimatına verildi). `ULKE_FAZI.md`: akış ve paket düzeni. `ES_aday_kartlar_*.md`: aday kart listeleri.
- Şehre uygulama örneği: `python -X utf8 country_apply.py apply <şehir\_is> --pack <ulke\ES> --city-id sevilla --city-name Sevilla --order-start 9000`. Sahte "Sevilla" klasöründe (scratchpad) 80 kartla denendi, çalışıyor. **Gerçek bir şehir klasörüne hiç uygulanmadı.**

## 5. Çalıştırılan süreç (konu başına; grup grup)
1. Kaynak keşfi: tek Sonnet ajanı, resmî derin sayfa, `must_contain` ile `selected.jsonl` (`_is\kesif\<konu>\`).
2. Ana döngü `toolkit\scripts\add_sources.py <ES\_is> --candidates ... --subdir snap_kesif_<konu> --topic <konu> --city-id es` ile gerçek indirme + kanıt ölçümü. **Ajanın "hepsini doğruladım" sözüne güvenilmedi; her turda 1-2 adres bu ölçümde elendi.** Elenen adres kullanılmaz.
3. Yazar (Sonnet, konu başına): `YAZAR_KURALLARI.md` + `ortak-kurallar.md` + `yanit-yazari.md`; çıktı `_is\yazar\out\<konu>\` (Yanıtlar, Bağlantılar, claims, valid_until.json, gaps.md). Sonra `pack_check`.
4. Bağımsız denetçi (Sonnet, yazarı/editörü görmemiş): kart cümlelerini kartın KENDİ kaynak metniyle ve canlı resmî sayfalarla karşılaştırır; rapor `yazar\out\denetim_*.md`.
5. Editör (Sonnet): bulguları uygular; kaynak yoksa yazmaz/siler; `pack_check` temiz olana dek. Yedek her turda `yazar\out\yedek_*_editor_oncesi\`.
6. `pack_build` → paket sürümü artar → sahte şehirde `apply` + `audit-scope` denemesi.
Not: denetçi sayıları. v1 (oturum+resmi): 1. denetim 4 ciddi, 2. denetim 1 ciddi, 3. denetim 0 ciddi. Grup 1 ilk denetim: para 1 ciddi, iş 0, fatura 1 (koşullu); editör sonrası dar denetim: 0 ciddi (para 1 orta, iş 0 orta, fatura 4 orta). Grup 2 ilk denetim: sağlık 1, ev 2, planlama 2 ciddi (hepsi düzeltildi; editör sonrası denetim yok).

## 6. Denetimlerin yakaladığı gerçek hatalar (ders)
Ehliyet kartı Türkiye'nin anlaşmalı olduğunu söylemiyordu; Libro de Familia "kalkıyor" deniyordu (2021'den beri verilmiyor); Brexit 3 ay kuralı yanlış kapsamdaydı; Yargıtay'ın iptal ettiği bir cümle; Renta kartı yurtdışı emekli maaşı alanı kapsamıyordu; apartman kartı Katalonya'da yanlış (yedek fon %5 vs %10); sigorta kartı "Hayır" diyordu (öğrenci vizesi ve çalışmaksızın oturumda şart var); gümrük kartı "10.000 € dan fazla" yazıyordu (doğrusu "ve üzeri") ve nakit için sözlü beyan diyordu (doğrusu yazılı); evden çıkış kartı Meclis onayı bekleyen bir kararnameye dayanıyordu. Ders: yazarlar yalnız indirilmiş metne bakar; yeni kural, bölge farkı ve Türk okuyucu etkisini bağımsız denetçi buluyor. Editör sonrası ikinci denetim ciddi bulguyu azaltıyor.

## 7. Doğrulanmayanlar / bilinen eksikler (devralan bilmeli)
- **Editör sonrası ikinci denetim grup 2 (sağlık, ev, planlama) için YAPILMADI**; grup 1 için yapıldı (0 ciddi). Grup 2'de 5 ciddi çıktığı için burada risk daha yüksek. Önerim: 21 kart için dar denetim.
- Her turun SON düzeltmeleri yalnız script denetiminden geçti (alıntı kaynak metninde var).
- `claims`, `Bağlantılar`, `valid_until` dosyaları insan/model gözüyle satır satır denetlenmedi.
- **`package_sources` ile teslim klasörüne dönüşüm uçtan uca denenmedi** (`country_apply` kopyaları `snap_ulke_es\` altına aynı kayıt biçimiyle yazıyor; uyum beklenti, kanıt değil).
- **Eski Barcelona dosyası:** doğru dosya `barcelona\CITY-009_barcelona_v001.xlsx` (240 kart); kökteki aynı adlı dosya boş şablon. Barcelona dosyasına dokunulmadı; yalnız başlıklar aday liste için okundu, kaynakları zayıf (32) olduğundan kartlar sıfırdan kaynaklandırıldı.
- Kart içeriğinde kaynak bulunamadığı için YAZILMAYAN bilgiler `ES\acik_konular.md` dosyasında (grup 1 ve grup 2 ekleri dahil): ör. IVA geçici oranı, SMI "14 ödeme", otonom aylık cuota, apostil ücreti, IPREM euro tutarı, Türkiye-İspanya sosyal güvenlik düzeni, vize ücretleri, Bizum güncel limitleri.
- **Acil güncelleme tarihleri:** 6 ev kartı 2026-11-05 (kira kararnamesi RDL 29/2026 onayı, RDL 28/2026 15 Kasım'da md. 10'u değiştiriyor); 7 kart 2026-12-31 (SMI 2026, tatiller 2026, bordro, otonom prim, bono social, dijital göçebe, NLV). `audit-scope` bunları yeniden denetime alıyor.
- **Türk okuyucu uyarısı eksik (sağlık):** "AB rejimi Türk vatandaşına uygulanmaz / AB vatandaşının Türk aile üyesi" cümlesi kaynaksız bulunup çıkarıldı; ayrı kart önerildi. **Yolcu bagajı gümrük kartı yok** (430/300 € ve tütün/alkol; kaynak `es:kaynak:101`, sayfa "10.000 €'dan fazla" ile hatalı, kullanırken dikkat).
- Bot/sertifika engelleri: `inclusion.gob.es`, `interior.gob.es` 403; `mites.gob.es` sertifika hatası; MIVAU sayfaları ajanın tarayıcısında açıldı ama `add_sources` indirmesinde 403 (kart yazılırken yalnız kabul edilen kaynaklar kullanıldı); `exteriores.gob.es` İstanbul sayfaları aralıklı 503/504. **Sertifika doğrulamasını kapatmak bir ajan tarafından denendi, sistem reddetti, geri alındı; hiçbir ajanın buna izni yok.**

## 8. Sıradaki işler (öneri sırası)
1. Grup 2 (21 kart) için dar bağımsız denetim → bulgu varsa kısa editör turu → `pack_build` v5.
2. Grup 3 (aile, ulaşım, günlük yaşam; 15 kart) aynı süreçle; `pack_build.py` `TOPICS`'e yeni konular eklenecek.
3. Ek kartlar: yolcu bagajı gümrük muafiyeti; sağlıkta AB dışı vatandaşlar için erişim/AB-aile üyesi kartı.
4. Bölge katmanı (Andalucía): sağlık sistemi/kartı, bölge vergileri, fianza kurumu, ulaşım biletleri. Sevilla'nın kendi işi (mekân, mahalle, fotoğraf, şehre özgü kartlar) hiç başlamadı; `mekan_kaynaklari.md` yazılmadı.
5. İlk gerçek şehirde (kullanıcı söyleyince) `country_apply apply` + `audit-scope` ölçümü; `package_sources` uçtan uca denemesi; ülke/bölge/şehir fazı ayrı süre-token raporu (hedef: Sevilla toplamı Bakersfield ~7 saatten düşük; Málaga ve Marbella Sevilla şehir fazının %60'ını geçmesin).
6. 15 Kasım ve 1 Ocak 2027'de tarihli kartların yeniden yazılması (bkz. yukarı).

## 9. Maliyet (ajan token'ı, ajanların raporladığı; kaba)
v1 (oturum+resmi): ~2,3 M. Grup 1 (para, iş, fatura; keşif+yazar+denetim+editör+dar denetim+son düzeltme): ~5 M. Grup 2 (sağlık, ev, planlama; keşif+yazar+denetim+editör): ~4,6 M. Toplam yaklaşık 12 M, çoğu Sonnet. Süre: ajanlar paralel/arka planda; duvar saati toplamı ölçülmedi. Karşılaştırma tabanı (Bakersfield): ~7 saat / 6,9 M çıktı / ~130 ajan. Bu paket bir kez ödenen ülke fazıdır; kazanç ikinci şehirden itibaren ölçülecek (henüz ölçülmedi).

## 10. Dosya haritası
- Paket: `ulke\ES\` (yukarıda). Çalışma: `ulke\ES\_is\` → `kesif\<konu>\selected.jsonl + gaps.md`, `snap_kesif_<konu>\` ve `snap_editor_*\` (indirilen kaynaklar), `kaynak_dizini.jsonl` + `kaynak_taslak.jsonl` (kimlik `es:kaynak:NNN`), `yazar\<konu>_kaynaklar.jsonl`, `yazar\out\<konu>\` (güncel kartlar), `yazar\out\yedek_*` (editör öncesi), `yazar\out\denetim_*.md` (bağımsız denetim raporları).
- Araçlar ve belgeler: `corteqs-skills\deneme_ulke_paketi\`.
- Önceki oturum özeti: `OTURUM_OZETI_20261024.md` (Bakersfield, skill değişiklikleri, 2445 test).
