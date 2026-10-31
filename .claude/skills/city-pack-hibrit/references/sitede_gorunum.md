# Alan → sitede nerede görünür

Excel'deki bazı alanlar sitede metin olarak değil, fotoğraf üstü bant, düğme ya da kutu olarak basılır. Yazar ve editör bu tabloya göre yazar. Dayanak: Sevilla dış denetimi (25.10.2026; mevcut `guide.html` şablon parçasıyla yeniden üretildi) ve `preview_checks.py` alan listeleri. Yeni bir görünüm öğrenildikçe buraya eklenir.

| Alan | Sitede | Kural | Emsal |
|---|---|---|---|
| `Mekânlar.visit_status` (ve `overlay`, `status_note`, `EkDetaylar.venue_editorial`) | Kartın fotoğrafının üstünde bant | Her zaman boş. Kapanış, tadilat, taşınma `note`'a tarihli tek cümle. `warning-scan` dolu değeri `kart_bandi` (K103 P1) sayar. | S06: dört kapanış notu banda dönüştü |
| `SayfaAlanları.advice_entry` | Şehir sayfasında "danışmanlık" düğmesi; etiketi şablonun varsayılanı, Excel'den değiştirilemez | Yalnız gerçekten danışma hizmeti anlatan karta bağlanır: kim danışmanlık veriyor, nerede, hangi dilde, ücretli mi (ör. başkonsolosluk, belediyenin göçmen danışma ofisi, tanınmış bir danışma kuruluşu). Bilgi kartına (padron, NIE) bağlanmaz. Türkçe hizmet kaynakla gösterilmedikçe kartta Türkçe hizmet ima edilmez. | S07: düğme padron bilgi kartına gidiyordu |
| `SayfaAlanları.hero_kicker`, `hero_accent`, `hero_note` | Kapak fotoğrafının üstündeki yazı | Kısa, şehre özgü; "kontrol et", "doğrula" gibi emir yok (`bant_emri`). | — |
| `SayfaAlanları.photo_credit` | Galeri bölümünün genel atıf notu | Kare atıflarının yerine geçmez; atıflar her karenin altındadır. | — |
| `Fotoğraflar.caption` | Fotoğrafın altı | Görüntüdeki yapı ve yer; arşiv karesiyse tarihli. Başka yapının karesi altyazıyla düzeltilmez, değiştirilir. | S01 |
| `SayfaAlanları.facts` | Kısa bilgi kutuları, tıklanınca `entry` kartı açılır | Her `value` defterde ve hedef kartta aynı. | — |
| `SayfaAlanları.timeline` | Kişisel hazırlık takvimi | Kişisel hatırlatıcıdır, yasal süre gibi yazılmaz. | — |
| `Rotalar` mesafe ve süre alanları | Rota kartı | Kuş uçuşu mesafe "yürüyüş" diye sunulmaz; her durak o gün ve saatte açık olmalı ya da "dışarıdan" diye ayrılmalı. | S10: pazar sabahı açık durak 17:00 sonrası planda |
