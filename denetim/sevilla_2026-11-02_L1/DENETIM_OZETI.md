Editoryal hazır olma: %46 (doğrulanan alt sınır, kısmi denetim) | Denetim kapsamı: L1 hedefli, yerel paket denetimi; inceleme kart 26/377, fotoğraf 30/334, kritik iddia 127/2602; script dosya 1950/1950, satır 2573/2573, URL 504/504 | Karar: DÜZELTME GEREKLİ (önizleme ve Drive kontrolleri ayrı aşamada)
Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: 0 | Açık P1: 3 (ISS-001, ISS-006, ISS-009) | P2 öneri: 18

> Bu bir yayın onayı değildir. %46 düşük görünüyor çünkü bu denetim **hedefli**: kullanıcı kararıyla (02.11.2026) yalnız 27.10 teslimine göre değişen kayıtlar ajanla okundu; okunmayan kayıtlar "doğrulanmadı" sayılır. Paketin kendi kanıtlarıyla dış denetim modelinin alt sınırı ayrıca **%93,05** (önizlemeyle azami %98,05; `kanit-kapsami.json`).

## Paket
- Sevilla, CITY-107, `CITY-107_sevilla_v001.xlsx`, şema 1.0, teslim 02.11.2026 18:44
- Excel SHA-256: `7eece588179954135049ee330eb4a425eae1a71878bdebfe5da2ffa02e6a96a3`
- 1950 dosya, 407,81 MB; K04 sabitleme: baş/son envanter farkı 0
- Önceki denetimler: `denetim\sevilla_2026-10-26_L1` (tam kapsam, Excel 6fefa38b, %93) ve `denetim\sevilla_2026-10-27_L0` (Excel 556343a6). 26.10'dan bu yana 941 kayıt değişti, o denetimin sonuçları bu pakete taşınmadı.
- Hedefli kapsam (`impact.json`, 556343a6 → 7eece588): 59 kayıt değişti (48 değişen, 5 eklenen, 6 silinen). Ajanla okunan: 7 kart (147 iddia satırı), 15 mekân, 4 mahalle, 10 rota, ön elemede işaretli 30 kare, açık-mı örneklemi 62 mekân.

## Berlin matrisi (minimum – hedef – fiilî)
| Ölçü | Alt sınır | Hedef | Fiilî |
|---|---|---|---|
| Pratik yanıt | 212 | 240 | 241 |
| Gerçek mekân | 92 | 120 | 120 |
| Mahalle | 12 | 16 | 16 |
| Dolu konu | 12 | 12 | 12 |
| Farklı mekân fotoğrafı | 187 | 250 | 326 |
| Farklı kapak | 6 | 8 | 8 |
| Rota | 9 | 12 | 12 |
| Sözlük | 48 | 60 | 60 |

Hepsi hedefte. Fotoğraflı mekân 120/120, mahalle 16/16. Teslim özeti ile denetimin yeniden hesabı birebir aynı (K83 özet ve yol farkı 0).

## Öncelikli bulgular (P1)
| ID | Kontrol | Satır | Bulgu | Kanıt |
|---|---|---|---|---|
| ISS-001 | K42 | Mekânlar!66 `catedral-de-sevilla-giralda` | Kart pazartesi–cumartesi 10:45–19:00, gişe 18:00 diyor; resmî sayfa 10:45–18:00, gişe 17:00 (19:00 yalnız pazar kapanışı). Aynı saat rota 001'in notunda (ISS-003). | Katedral resmî sayfası: «LUNES A SÁBADOS 10:45h. a 18:00h. Cierre de taquillas a las 17:00 horas.» |
| ISS-006 | K60 | Fotoğraflar!159 `estadio-la-cartuja-01` | Commons açıklaması yalnız "Real Betis - Girona, jornada 13"; stadyum adı yok, Betis iç saha maçı Benito Villamarín'de oynanır, karede La Cartuja'nın atletizm pisti yok. Kare büyük olasılıkla başka stadyum. | Pafta `temas-sayfalari\hedefli\sheet_01.jpg`, slot 16 |
| ISS-009 | K39 | Mekânlar!22 `costurero-de-la-reina` | Turismo 30.04.2026'da binadan çekildi, bina Sevilla 2029 Komiserliği ofisi olacak. Kart olguyu tarihiyle yazıyor ama ziyarete açık mı söylemiyor; mekân rota 003'ün (Rotalar!10) durağı. | andaluciainformacion.es (30.04.2026): «…pasará a ser la Oficina del Comisariado del 29.» |

## Yanlış görseller (pafta ve slot)
- Ret: `estadio-la-cartuja-01` → `hedefli/sheet_01`, slot 16 (ISS-006).
- İşaret (P2): `huevo-de-colon-01/02` ve `auditorio-cartuja-sevilla-01` (kare içi eser/logo, ISS-007); `palacio-de-las-duenas-03` (yakın çini detayı) ve `la-cartuja-02` (manastır karesi, semt kaydında; ISS-008).
- Ön elemenin `name_extended` dediği `casa-de-la-provincia-02/03` ve `plaza-de-toros-de-la-maestranza-02/03` aynı yapı çıktı, geçti. Kapak-06 uygun.

## Açık-mı örneklemi (K39)
- Kural: n = en az 8 ve mekânların %10'u → 12; öncelikliler hepsi (üretimde belirsiz kalan 43, tarihli notlu 20; üretim beyanının kendi bulgusu 0) + rastgele 6 → 62 mekân, 8 parti.
- Sonuç (`acik-mi-sayim.json`): açık doğrulandı 39, kartta tarihli yazılı kapanış/tadilat 5, doğrulanamadı 18, kapanış 0.
- Doğrulanamayan 18 (tarihli açık kanıtı da kapanış kanıtı da yok): Palacio de la Condesa de Lebrija, Palacio de San Telmo, Jardines de las Delicias, Plaza del Duque, Plaza de Doña Elvira, Plaza de los Refinadores, Museo Histórico Militar, Museo Marítimo Torre del Oro, Sevilla FC stadyum turu, El Patio Sevillano, Mercado de la calle Feria, Confitería La Campana, Cerámica Santa Ana, Parque de Miraflores, Iglesia de San Marcos, Jardines de Cristina, Jardín Americano, Capilla de los Luises.
- Teyit gerekli (bulgu sayılmadı, kanıt yetersiz):
  - **El Patio Sevillano**: kendi sitesinde tarihsiz "1 Temmuz'dan itibaren Avenida de las Razas 20'ye taşınıyor" yazısı var; kart Paseo Cristóbal Colón 11 diyor. Adres insan kontrolüne açık.
  - Plaza del Duque: Temmuz 2026'da yenileme başladığı iddiası yalnız güvenilmez bir forum sayfasında.
  - Mercado de la calle Feria: 17.04.2026 belediye kararında çatı/onarım işi var, kapanış kanıtı yok.
- Üretim beyanıyla fark: üretimin açık-mı kapısı temizdi (bulgu 0); denetim Costurero de la Reina'da ziyaret durumu notunun eksik olduğunu buldu (ISS-009).
- Zayıf açık kanıtları (üçüncü taraf yorum/ajanda): Casa de la Guitarra, Casa Román, Bodega Dos de Mayo, Convento de Santa Paula, Convento de Santa Inés.

## İddia düzeltmeleri ve resmî kaynak
- Değişen 7 kartta 147 iddia satırı: hepsi doğru (yanlış 0, eski 0). Script'in "kaynakta yok" dediği 68 iddia biçim farkıydı (İspanyolca tarih ve süre yazımı).
- K26 eksik öğe (P2): `endulus-saglik-karti…` (Yanıtlar!213) DNI'sı olmayan TIE/NIE sahibi için yol yok (ISS-004); `saglik-sigortasi-sarti-ve-convenio-especial` (Yanıtlar!207) karar süresi (RD 576/2013 md. 4: 30 gün) ve 3 aylık imza süresi yok (ISS-005).

## Bağlantılar (kök nedene göre)
- 504 benzersiz adres: çalışıyor 501, bozuk 0, erişim teyidi açık 3 (spain.info 403 ×2, hospitaluvrocio.es ağ hatası).
- Yalnız ana sayfa: 17 adres (ISS-010, P2). Başka alan adına yönlenen: 2 (casadelaguitarra.es → flamencoensevilla.com, aussa.es → aussa.com; ISS-011, P2).

## Diğer P2
- ISS-002 dört mahallede ulaşım satırı mahalleye özgü değil; ISS-003 rota bulguları (001/003/008'de süre kuş uçuşunun ~2 katı, 002/003/009'da geri dönüş, 004'te Perdigones koordinatı); ISS-012 14 aynı baytlı kanıt JSON çifti (OI-017); ISS-013–020 kanıt kapsamı eksik ölçütler (A1–A5: 4 kart d19v sonrası yeniden doğrulanmadı; B1/B5: 12 mekân; C4); ISS-021 22 kartın reviewed_on'u kaynağın son kontrolünden eski.

## Düzeltme sırası
1. ISS-001: Katedral saatini resmî sayfaya göre düzelt (kart + rota 001 notu).
2. ISS-006: `estadio-la-cartuja-01` karesini kimliği kanıtlı bir La Cartuja karesiyle değiştir.
3. ISS-009: Costurero de la Reina notuna tarihli ziyaret durumu yaz; ziyarete kapalıysa rota 003 durağını gözden geçir.
4. El Patio Sevillano adresini insan teyidiyle kontrol et.
5. city-pack teslim zinciri: kanıt dosyaları (ISS-013–020) ve P2'ler (isteğe bağlı).
6. Yeni sürümle L0, ardından L1.

## Çalıştırılmayan kontroller
- not_checked (hedefli kapsam dışında): K06, K07, K18, K19, K28, K32, K36, K37, K48, K51, K65, K71, K72, K90, K91, K96, K98, K101, K102, K105, K113, K116, K117, K119, K120.
- separate_stage (Drive/önizleme): K01, K03, K92, K93, K94, K103, K109, K110, K111, K112.
- Lisans hak zinciri ajanı çalışmadı (fotoğraf baytları 27.10'dan beri değişmedi); `photo-review.json` lisans alanları validate_all'dan.
- Değişmeyen 2475 iddia, 234 yanıt, 105 mekân, 12 mahalle, 2 rota ve 304 kare bu denetimde okunmadı.

Kanıtlar: `check-results.json`, `issues.json`, `criteria.json`, `score.json`, `claim-checks.json`, `photo-review.json`, `acik-mi-*.json`, `_l\`, `_iddia\`, `_foto\`, `temas-sayfalari\hedefli\`, `_analiz\betikler\hedefli.py`, `_analiz\betikler\kayitlar_hedefli.py`.
