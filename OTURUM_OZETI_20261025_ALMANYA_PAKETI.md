# Oturum özeti: Almanya ulusal paketi v1 (25.10.2026, Windows oturumu)

Bu belge başka bir Claude oturumuna ya da ileride Barış'a devir içindir. Önceki ülke paketi belgeleri: `OTURUM_OZETI_20261024_ISPANYA_PAKETI.md`, `OTURUM_OZETI_20261024_BULUT.md`. Tarif: `YENI_ULKE_SEHIR.md` (Yol B), `corteqs-skills\deneme_ulke_paketi\ULKE_FAZI.md`. Şehir başlatma: `ALMANYA_YENI_SEHIR.md`.

## 1. İstek ve karar
Barış tek cümle yazdı: "Yeni ülke paketi: Almanya". Drive kataloğunda 33 Almanya şehri olduğu için Yol B (önce ülke paketi) doğru karardı; başka soru sorulmadı, İspanya akışı aynen uygulandı. Oturum boyunca kullanıcıdan mesaj gelmedi; kararlar varsayılanla alındı ve `ulke\DE\_is\yazar\out\orkestrator_notlari.md` dosyasına yazıldı.

## 2. Sonuç
- Paket `ulke\DE\` v1: **113 kart, 11 konu, 2120 iddia, 213 bağlantı, 193 kaynak, 13 tarihli kart.** `pack.json`, `Yanıtlar.ulusal.jsonl`, `Bağlantılar.ulusal.jsonl`, `claims\ulusal.jsonl`, `kaynak_dizini.jsonl`, `kaynaklar\`, `acik_konular.md`.
- Konu dağılımı: oturum 15, resmi 12, para 12, is 11, ulasim 10, fatura 9, saglik 9, ev 9, planlama 9, gunluk 9, aile 8. `kesif` konusu ulusal pakete girmez.
- Sahte şehirde `country_apply apply` 113 kart kopyaladı, `audit-scope` 113 atla, `merge_package` 0 bulgu / 0 alıntı kaybı.
- Bölge (eyalet) paketi YOK. Commit: `8f116987`.

## 3. Ölçüm (gerçek, phase_usage ile)
| Faz (log penceresi) | Süre | Çıktı token | Önbellek dışı girdi |
|---|---|---|---|
| hazırlık (erişim yoklaması, aday kart listesi, görev metinleri) | 14 dk | 43 K | 67 K |
| keşif + ilk yazarlar | 58 dk | 1,62 M | 7,08 M |
| yazar + denetim + editör + dar denetim | 66 dk | 2,21 M | 8,21 M |
| kurulum ve test | 3 dk | 7 K | 5 K |
| **Toplam** | **2 sa 21 dk** (02:56–05:17 UTC) | **3,9 M** | **15,6 M** |

Kaynak: `ulke\DE\_is\phase_usage.csv`, `phase_log.jsonl`. Fazlar gerçekte paralel koştu (keşif sürerken yazarlar başladı); log ardışık pencerelere indirildi, bu yüzden faz paylaşımı kaba, toplam kesin.
Ajan: 52 Sonnet (11 keşif, 11 yazar, 11 denetçi, 11 editör, 4 dar denetim, 4 kısa editör), ajan başına ~160–450 K token. Ana döngü Fable. Karşılaştırma: İspanya 96 kart ≈ 12 M ajan token'ı, iki güne yayılmış; Bakersfield şehri ~7 sa / 6,9 M / ~130 ajan.

## 4. Süreç (konu başına, dört grupta paralel)
1. Hazırlık: `ulke\DE\_is` açıldı, `phase_usage mark`; 75 resmî adres `fetch_snapshot` ile yoklandı (`_is\kesif\erisim_ozet.md`); Berlin örneği (212 kart) + İspanya yapısından 108 aday kart (`DE_aday_kartlar.md`); ülkeye özgü yazar notları (`DE_YAZAR_NOTLARI.md`); ortak görev metinleri dosyaya yazıldı: `_is\kesif\KESIF_GOREV.md`, `_is\yazar\YAZAR_GOREV.md`, `DENETCI_GOREV.md`, `EDITOR_GOREV.md` (ajan prompt'u yalnız parametre ve konuya özgü notları taşıdı).
2. Keşif (Sonnet, konu başına 1 ajan, 30 dk / 60 çağrı bütçe): `selected.jsonl` + `gaps.md`. Ajanlar sayfayı Python ile düz indirip `must_contain`'i kopyada doğruladı (WebFetch özet verir). 264 adaydan 261'i `add_sources`'ta kabul; 3 ince/soft-404, 4 geçici ağ hatası `--retry-transient` ile alındı.
3. Ana döngü: `add_sources` → `kaynak_listesi.py` → yazar listesi; ek kaynaklar `snap_kesif_<konu>_2` klasörüyle.
4. Yazar (Sonnet): `out\<konu>\` Yanıtlar/Bağlantılar/claims/valid_until/gaps; `pack_check` çıkış 0 şartı. Ana döngü her dönüşte `pack_check`'i kendisi yeniden koştu.
5. Bağımsız denetçi (yazarı görmemiş, gaps.md okumaz): kart cümleleri kaynak kopyası + canlı sayfa ile; rapor `out\denetim_g<N>_<konu>.md`. İlk tur toplam: 9 ciddi, ~105 orta, ~165 küçük.
6. Editör: yedek `out\yedek_g<N>_editor_oncesi\<konu>\`, kayıt `out\degisiklik_g<N>_<konu>_editor.jsonl`; ciddi/orta için `add_sources` ile kaynak ekleyebilir (kart başına 2 sınırı korunur).
7. Dar denetim grup başına (`denetim_g<N>b_dar.md`): kapanış tablosu + editörün değiştirdiği cümlelerin kaynak kontrolü. Sonuç: ciddi 0 (g0 0/2/15, g1 0/6/19, g2 0/7/12, g3 0/5/13).
8. Kısa editör grup başına (`degisiklik_g<N>b_editor.jsonl`), sonra `pack_build.py ulke\DE --country DE --version 1`.

## 5. Denetimlerin yakaladığı gerçek hatalar (ders)
Emeklilik yaşı "67" genellemesi (1964 öncesi doğumlular için kademeli); eAT ücretinde 67 Euro'nun yanlış nedeni; yan gider kartında §556 istisnasının ters yazılması; "iş günü" çevirisinin "Werktag"ı daraltması; GKV zorunluluğunun herkese genellenmesi (JAEG üstü, serbest çalışan, memur); mağaza saatlerinin federal yasa gibi sunulması (eyalet yetkisi); Kinderzuschlag/Unterhaltsvorschuss'ta yabancı şartları; itiraz kartında dava süresinin eksikliği; vergi oranlarının (%42/%45) formül katsayısından türetilmesi; kaynaksız "sigortayı girişten önce ayarla" sırası. Ders aynı: yazar yalnız indirilmiş metne bakar; kapsam kaymasını ve eyalet farkını bağımsız denetçi buluyor; editör sonrası dar denetim yeni hataları (kaynaksız tavsiye, havale cümlesi) yakalıyor.

## 6. Araç ve belge değişiklikleri
- `pack_check.py`: şehir adı taraması ülkeye göre (`CITIES_BY_COUNTRY`; `ulke\<ISO>` yolundan seçilir, Almanya'da 39 şehir adı); alıntı karşılaştırması yumuşak tire (U+00AD) ve sıfır genişlikli karakterleri yok sayar.
- `toolkit\scripts\merge_package.py` `norm`: aynı görünmez karakter kuralı (ülkeden bağımsız iyileştirme; rundfunkbeitrag.de gibi tireli sayfalar için). Toolkit testleri 2445/2445, deneme testleri 25/25.
- `EDITOR_GOREV.md`: editör ciddi/orta bulgu için kaynak ekleyebilir.
- Belgeler: `DE_aday_kartlar.md`, `DE_YAZAR_NOTLARI.md`, `ALMANYA_YENI_SEHIR.md`, `ULKE_FAZI.md` "İkinci ülke: Almanya", `YENI_ULKE_SEHIR.md` ölçüm bölümü. Bellek: `project_almanya_paketi.md`.

## 7. Erişim ve ortam notları
- Kapalı: bmi.bund.de (HTTP 400, tarayıcı taklidi denenmedi ve izin verilmez), bund.de ve bzr.bund.de (TLS), bmftr.bund.de (bağlantı). make-it-in-germany.com ve auswaertiges-amt.de JavaScript ile yüklüyor, kopyada metin yok. eur-lex bot korumalı.
- Windows sertifika deposu familienportal, DRV, BMF, Bundesbank, 116117 sitelerinin ara sertifikasını ilk denemede tanımadı (`tls` hatası); `curl` ile bir kez açılınca Python da açtı. Kural: ilk `tls` hatasında `--retry-transient`, ikinci hata = kapalı.
- gesetze-im-internet tek madde sayfaları çoğu zaman 500 karakterin altında (ince, elenir); yasanın tam metin sayfası (`BJNR….html`) kullanıldı. SGB V tam metni 3 MB sınırında kesildi (de:kaynak:265), kullanılan maddeler kopyada.
- Bash bu ortamda `/c/...` yollarını görmüyor; her şey PowerShell + Python (`-X utf8`) ile yapıldı. Python'u `-I` ile çalıştırma: toolkit script'leri yan modül import ediyor.

## 8. Açık konular (ayrıntı `ulke\DE\acik_konular.md`)
- 2026 Mavi Kart euro maaş eşikleri açık resmî HTML sayfada yok; kartta yalnız yüzdeler.
- Kart başına 2 kaynak sınırı yüzünden sığmayan, v2 için ayrı kart adayları: Abschlag, Mutterschaftsgeld, Pflegegrad 1–5, Elternzeit, Elterngeld yabancı şartı, Wohngeld yabancı hakkı, §656c satış komisyonu, Bürgergeld/Grundsicherung aylık tutarı, EStG §62 eğitim istisnası, euro ve yaz saati, ilk hafta banka/sağlık kasası, Türkiye'de doğan çocuğun kaydı, Werktag/Cumartesi açıklaması.
- Tarihli kartlar: AB dışı paket gümrük 31.10.2026 (1 Kasım işlem ücreti planlı); 11 kart 31.12.2026; asgari ücret 31.12.2027. `apply` eskiyen kartı kopyalamaz.
- Bürgergeld 1.7.2026'da "Neue Grundsicherung"a dönüştü; kart kaynağın tarihleriyle yazıldı, güncel tutar yok.
- Eyalete giden konular: tatiller, Kirchensteuer oranı, Grunderwerbsteuer, Mietpreisbremse alanı, okul/Kita, mağaza saatleri, WBS sınırları, eyalet aile ödemeleri, Zulassung/HU ücretleri.
- Kaynak kopyaları satır satır insan gözüyle okunmadı (yalnız script + denetçi örneklemesi). `package_sources` ile teslim klasörüne dönüşüm gerçek şehirde denenecek (İspanya'da da öyle).

## 9. Sıradaki işler
1. İlk Alman şehri (Barış seçer). Öneri: NRW'den bir şehir; ondan önce NRW bölge paketi (`ulke\DE\bolge\nrw`, Endülüs akışı, ~yarım gün). Başlangıç mesajı `ALMANYA_YENI_SEHIR.md`'de.
2. 1 Kasım 2026 sonrası gümrük paketi kartı; 1 Ocak 2027'de 11 tarihli kart yenilenir (v2).
3. v2'de yukarıdaki ayrı kart adayları ve `para/yillik-vergi` için ELSTER 2026 sayfası.
4. Üçüncü ülkede: görev metinleri (`KESIF_GOREV`, `YAZAR_GOREV`, `DENETCI_GOREV`, `EDITOR_GOREV`) kopyalanır, kimlikler (`de:` → `<kod>:`) ve `CITIES_BY_COUNTRY` güncellenir; keşif ajanlarına "düz indirme ile doğrula" notu baştan verilir.

## 10. Dosya haritası
- Paket: `ulke\DE\` (pack.json, Yanıtlar/Bağlantılar/claims, kaynak_dizini.jsonl, kaynaklar\ 193×2 dosya, acik_konular.md).
- Çalışma: `ulke\DE\_is\` → `kesif\<konu>\selected.jsonl + gaps.md`, `kesif\erisim_ozet.md`, `kesif\KESIF_GOREV.md`, `snap_kesif_<konu>[_2]\`, `snap_<konu>-editor<N>\`, `kaynak_dizini.jsonl` (269 kaynak; pakete yalnız kullanılan 193 girdi), `yazar\<konu>_kaynaklar.jsonl`, `yazar\{YAZAR,DENETCI,EDITOR}_GOREV.md`, `yazar\out\<konu>\` (güncel kartlar + gaps.md), `yazar\out\denetim_*.md` (15 rapor), `yazar\out\degisiklik_*.jsonl` (15 kayıt), `yazar\out\yedek_*\`, `yazar\out\orkestrator_notlari.md`, `phase_log.jsonl`, `phase_usage.csv`, `oturum_kaydi.txt`.
- Araç ve belgeler: `corteqs-skills\deneme_ulke_paketi\` (pack_check güncel, DE_* belgeler, ULKE_FAZI).
