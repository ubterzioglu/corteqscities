# Eindhoven (CITY-039) şehir paketi — gönderim notu

Bu klasör (`paket\`) Corteqs v7 sözleşmesine göre üretilmiş Eindhoven paketidir. İnsan yayın onayı **verilmemiştir**; bu not paketi kendi ayarlarınla denetlemen için yazıldı. Son güncelleme 23 Ekim 2026: 16 mekân eklendi, kapanmış olduğu anlaşılan bir mekân çıkarıldı ve bütün mekânlar "bugün açık mı" diye tarandı.

## Paket içeriği
| | Sayı | Berlin asgari / hedef |
|---|---|---|
| Bilgi kartı (Yanıtlar) | 289 | 212 / 240 |
| Mekân | 119 | 92 / 120 |
| Mahalle | 16 | 12 / 16 |
| Konu | 12 | 12 |
| Rota | 12 | 9 / 12 |
| Sözlük | 60 | 48 / 60 |
| Mekân fotoğrafı (farklı) | 218 | 187 / 250 |
| Kapak fotoğrafı | 8 | 6 / 8 |
| Kaynak (kopyası pakette) | 397 | — |

- `CITY-039_eindhoven_v001.xlsx` (17 sekme), `Fotoğraflar\` (226 dosya; Wikimedia Commons'un 1280 px kopyaları), `Lisans kanıtları\kaynaklar\` (397 kaynak sayfa kopyası, SHA eşleşir), `Teslimler\` (teslim özeti, açık konular, ilerleme kaydı, dosya envanteri, foto atıf CSV/HTML, web kopyaları, resmî araç çıktıları). Toplam 851 dosya, 225 MB.
- Excel SHA-256: `18b0c295710b6fb4b15b49a409b03f333ace00fa07cb9ab9dd347a83bb9e135b`

## Bizim ölçtüğümüz
- **Resmî doğrulayıcı** (`araclar\arac`, `--new-content`): **yapı 0 hata, medya 0 hata, asgari eksik yok, technically_complete = True.** 744 uyarının 678'i insan inceleme alanları (226 kanıt satırı × 3; tasarım gereği "Bekliyor", yapay zekâ onaylamaz), 66'sı fotoğrafsız mekân/mahalle.
- **Teslim özeti "DÜZELTME GEREKLİ" diyor**, çünkü iki *hedef* tutmadı: mekân 119/120, mekân fotoğrafı 218/250. Asgari sayıların hepsi geçildi.
- **Bağlantılar:** 397 adres, hepsi çalışıyor (bozuk 0); Wikipedia kaynağı yok. 12 kaynak yalnız ana sayfa (işaretli).
- **Bilgi doğruluğu:** kartlardaki her sayı ve kural için kaynaktan birebir alıntılı iddia defteri var (**5.880 alıntı, hepsi kaynak kopyasında birebir**). 289 kartın ve 119 mekânın tamamı en az bir kez bağımsız (Opus) denetimden geçti; bulunan sorunlar düzeltildi ve düzeltmeler bağımsız doğrulandı.
- **Sayı kontrolü:** kartlardaki 2.139 sayının 2.122'si kaynak kopyasında birebir var. Kalan 17'nin 13'ü kaynağın okunma tarihi ("22 Ekim 2026'da okundu"), 4'ü bilet toplamı hesabı (ör. 2 × 32,50 + 19,50 = 84,50; aritmetik doğru).
- **"Bugün açık mı" taraması (23 Ekim):** 119 mekânın hepsi bağımsız tarandı. Mekânın kendi sitesinin varlığı açık kanıtı sayılmadı; 2025–26 tarihli faaliyet kanıtı, Hollandaca kapanış araması ve kararı çürütmeye çalışan ikinci bir ajan kullanıldı.
  - Golfbaan Welschap 2020 sonunda kapanmış (sitesi 2019'dan beri duruyordu) → çıkarıldı.
  - Başka kapalı mekân çıkmadı.
  - 5 karta tarihli not eklendi: POM taşındı (Ventoselaan 1, TAC binası), iki oyun bahçesi ve bir kano işletmesi sezon dışı, bir escape room'un iki odası kapanacak.
  - 3 mekân için tarihli faaliyet kanıtı bulunamadı ama kapanış kanıtı da yok (açık konu).
- **Fotoğraflar:** beş tur görsel kontrol ve her turda bağımsız ikinci göz (maket, yanlış bina, eski görünüm, filigran, tanınabilir yüz elendi).
- **Bizim bağımsız denetimimiz (city-audit L0, 23 Ekim, temiz oturum; `denetim\eindhoven_2026-10-23_L0b\`):** "DÜZELTME GEREKLİ"; P0 0, P1 3, P2 4. P1'lerin üçü yukarıdaki hedef eksikleri ve fotoğrafsız 66 yer. Önceki denetimin ters eğik çizgi bulgusu kapandı. P2'ler: iki tarih alanı (Teslimat `updated_on` ve bugün değişen 10 kaydın `reviewed_on`'u 22 Ekim kaldı; v002'de düzeltilecek), ev sigortası kartının tek kaynağa dayanması, ilerleme kaydı (düzeltildi). L0 yalnız script denetimidir; içerik okuma (L1) senin denetimine kalıyor.

## Ortam uyarıları (denetlerken)
1. **Windows'ta `tzdata`** Python paketi yoksa resmî doğrulayıcı "Şehir: geçerli IANA saat dilimi gerekli" diye sahte hata verir (`pip install tzdata`).
2. **`download_media.py`** planı UTF-8 okumuyor: Windows'ta `python -X utf8 download_media.py ...` ile çalıştırılmazsa `FotoÄŸraflar` adlı klasöre indirir. Ayrıca önbelleğini paket içine (`Teslimler\.download-cache`) yazar; bu pakette silindi.
3. Teslimat kimliği şablonda `CITY-039-v001` (büyük harf) idi; resmî doğrulayıcı küçük harf istediği için paketteki Excel'de `city-039-v001`.
4. Doğrulayıcının "ek kontrol" bölümündeki tek "placeholder" bulgusu **yanlış alarm**: vergi beyanı kartında tırnakla aktarılan resmî başlık "Kan ik nog uitstel aanvragen voor de belastingaangifte 2025?" (kural, rakamdan sonra gelen "?"yi yer tutucu sayıyor).

## Bilinen açık konular (insan/uzman bakmalı)
- **[P1] IND gelir eşikleri:** Ortaklık Anlaşması kapsamındaki Türk vatandaşlarına uygulanıp uygulanmadığı kaynaklarda yok; kartlar "tablo uyruk ayrımı yapmıyor" diyor.
- **[P1] Inburgering muafiyeti:** Türk vatandaşlarında muafiyetin yalnız belirli bir izin türüne ait olduğu IND metninin yorumuna dayanıyor.
- **[P1] SVB:** Çocuk yardımı tutarları ve Türkiye–Hollanda sosyal güvenlik anlaşması yazılamadı (svb.nl script'e kapalı).
- **[P1] 66 yer fotoğrafsız** (64 mekân, 2 mahalle): Commons'ta kullanılabilir kare yok; çoğu galeri, kafe, kulüp.
- [P2] **Okura hitap tutarsız:** kartların çoğu "siz", bir kısmı "sen" diyor; Berlin örneği ise neredeyse hiç doğrudan hitap etmiyor. Bir standart seçilip tek geçişte uygulanmalı.
- [P2] Kaynak çelişkileri kartta açıkça yazıldı (sigorta geriye dönük prim, ehliyet değişimi sırasında araç kullanma, kira artış formülü, bebek sigorta kaydı); resmî devlet kaynağı esas alındı.
- [P2] Mevsimlik ve geçici durumlar kartlarda tarihli; ilkbaharda yeniden bakılmalı. TAC yenileniyor (saatler DDW sonrası duyurulacak, tam açılış Nisan 2027).
- [P2] Mahalle kartlarında ticari kaynak (Expatica, Expat Arrivals) kullanıldı; kartta atıf var.
- Tam liste (26 madde): `Teslimler\ACIK_KONULAR.txt`.

## Üretim
Claude Code ile `city-pack` skill'inin ilk gerçek denemesi (pilot). Süreç ve ölçümler ayrıca raporlanacak.
