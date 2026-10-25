# ev - yazar notları (25.10.2026)

Çıktı: 9 kart (order 701-709), 128 claim, 17 bağlantı, 2 tarihe duyarlı kart. Tüm claim alıntıları kaynak metninde birebir doğrulandı.

## Kart bazında yazılmayan bilgi
- Kart 2 (depozito): depozito iade süresi ve koşulu yazılmadı (kaynakta yok, içtihat). §548 (kiralayanın hasar taleplerinin 6 ay zamanaşımı) kullanılmadı: 2 kaynak sınırı ve depozito iadesi için dolaylı.
- Kart 3 (Mietpreisbremse): hangi eyalet/şehirde geçerli olduğu yazılmadı ("eyalet yönetmeliğine bağlı"). Muafiyetler (2014 sonrası ilk kiralanan yeni konut, kapsamlı modernizasyon) ve 30 aylık iade hakkı yalnızca bmj.de Mietrecht özeti (180) ve Mietpreisbremse sayfasında (181) var; 2 kaynak sınırı yüzünden yazılmadı. valid_until 2029-12-31 (§556d: yönetmelikler en geç bu tarihte sona erer).
- Kart 5 (Mietminderung): küçük onarım (Bagatellreparatur) tavanı, Schönheitsreparaturen kuralı ve kira indirimi yüzdesi yazılmadı (kanunda yok, içtihat). §535 (kiralayanın bakım yükümlülüğü, 168) ve §548 (184) kullanılmadı: 2 kaynak sınırı.
- Kart 6 (WBS + Wohngeld): gelir sınırı rakamları (WoFG §9: 12.000/18.000/4.100/500 euro) yazılmadı; federal taban ve eskimiş, eyaletler farklı belirliyor. Wohngeld tutar tablosu ve gelir sınırları yazılmadı (kaynakta yok). Yabancıların Wohngeld hakkı koşulu (WoGG §3 Abs. 5: Aufenthaltstitel vb., Chancenkarte/arbeitsplatzsuche izinlerinde genelde hak yok; kaynak 171) kullanılmadı: 2 kaynak sınırı (169 + 179 seçildi). Yabancı okuyucu için önemli olduğundan, ana döngü isterse 171 ile ayrı bir Wohngeld kartı ya da 169 yerine 171 düşünülebilir. valid_until 2026-12-31: kaynak (179) 2025 durumu, son artış 1.1.2025 ve iki yıllık düzen; bir sonraki uyarlama 1.1.2027.
- Kart 7 (Wohnungsgeberbestätigung + Bestellerprinzip): Übergabeprotokoll için kaynak yok, yazılmadı; başlıkta da geçmiyor. Kayıt süresinin kendisi (§17 BMG, 2 hafta) 172'de yok, yazılmadı (adres kaydı kartı konusu: `resmi` topic'inde `adres-kaydi-anmeldung-iki-hafta-konut-veren-onayi` kartı Wohnungsgeberbestätigung'u da kapsıyor, kısmi örtüşme var).
- Kart 8 (sahte ilan): tek kaynak (polizei-beratung.de Vorkassebetrug, tarihsiz); kendi ilan sayfası yok. Kaynaktaki "sichere Bezahlmethoden, Kreditkarte" önerisi ürün satın almaya yönelik olduğu için kiralık konuta uyarlanmadı.
- Kart 9 (ev satın alma): Grunderwerbsteuer oranı yazılmadı. 2 kaynak sınırı yüzünden §873 BGB (176: mülkiyet devri için Einigung + Grundbuch tescili), GrEStG §1 (178: alım vergiye tabidir) ve §656c BGB (173: satışta emlakçı komisyonu eşit paylaşım, tek taraf için ücretsiz çalışırsa diğerinden alamaz) kullanılmadı. Karttaki Grundbuch bilgisi yalnız §311b'nin ikinci cümlesine dayanıyor. İstenirse §656c ayrı bir "satışta emlakçı komisyonu" kartı olabilir.

## Kullanılmayan kaynaklar
161 (§542), 162 (§557a), 163 (§557b), 168 (§535), 170 (WoFG §9), 171 (WoGG §3), 173 (§656c), 176 (§873), 178 (GrEStG §1), 181 (bmj Mietpreisbremse), 184 (§548). Kart 1'de §542, §557a ve §557b yerine aynı içeriği veren bmj Mietrecht özeti (180) seçildi; §557a'ya özgü "kiracının fesih hakkı en çok 4 yıl dışlanabilir" kuralı bu yüzden yazılmadı.
Diğer 16 kaynak kartlarda kullanıldı.

## Dikkat notları
- bmj.de Mietrecht özeti (180) 14.09.2022 tarihli; yalnız kart 1 ve 2'de kullanıldı, tarihli sayfa olarak karta yıl yazıldı (kart 1 notu). Kuralın BGB karşılığı (§573c, §551) ikinci kaynak olarak aynı kartta.
- Kart 4 (Betriebskosten) `fatura` konusundaki `isitma-ve-yan-gider-hesabi-nebenkostenabrechnung` kartıyla konu olarak örtüşebilir; bu kart BGB §556 + BetrKV §2 (kalem listesi, 12 ay + 12 ay süresi) üzerine kurulu, ısınma gideri paylaşımını anlatmıyor. Ana döngü kopya/örtüşme taramasında bakabilir.
- Kart 6 Wohngeld bilgisi bmwsb sayfasının 2025 durumuna göre; Wohngeld 1.1.2027'de yeniden uyarlanabilir.
- Hiçbir kartta eyalet adı, eyalet rakamı ya da şehir adı yok; eyalete bağlı konular (Mietpreisbremse bölgeleri, Wohngeld gelir sınırı, Grunderwerbsteuer oranı, WBS sınırı) "eyalete göre değişir" olarak çerçevelendi.
