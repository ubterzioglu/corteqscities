# fatura — keşif boşlukları ve notlar (25.10.2026)

Özet: 9 kartın 9'u en az 1 kaynakla kanıtlandı; 23 kaynak adresi (yazar kart başına en çok 2 seçer; havuz bilerek geniş). Tüm `must_contain` ifadeleri indirilen sayfa metninde birebir doğrulandı.

## Kısmi kartlar (kanıtsız kalan bilgi)
- Kart 2: "Arbeitspreis / Grundpreis" terimleri federal yasa/yönetmelik metinlerinde (EnWG §40, §40b, §41; StromGVV) geçmiyor; kanıtlanabilir olan: yıllık hesap (§40b), Abschlag (StromGVV §13, yalnız temel tedarik), fiyat artışında özel fesih (§41). Birim fiyat/sabit ücret tanımı yazarda "kaynaksız" bırakılmalı ya da kart tanımsız anlatmalı. Not: §41 Abs.5'teki bildirim süresi (fiyat değişikliği en geç 1 ay önce, Haushaltskunden) sayfada var ("spätestens einen Monat"); must_contain'e konmadı.
- Kart 4: Su/atık su faturalaması belediyeye göre değişir (Gebühr/Beitrag, Satzung). Federal çerçeve yalnız BetrKV §2 Nr.2-3 (yan gider kalemi) ve BGB §556 (yıllık hesap, 12 ay). Kimin hangi belediye tarifesiyle fatura kestiği (doğrudan belediye/Stadtwerke vs. kiralayan üzerinden) için federal tek sayfa bulunmadı; "belediyeye göre değişir" denmeli.
- Kart 3: HeizkostenV §7 yalnız dağıtım oranı (%50-70 tüketime göre); Warmwasser (§8) ve Abrechnungspflicht (§§1-3, 6) ayrıca açılmadı. Nebenkostenabrechnung süresi (12 ay) BGB §556 Abs.3'ten; kiracının itiraz süresi de aynı maddede (12 ay).
- Kart 5: Rundfunkbeitrag tutarı 18,36 Euro/ay (rundfunkbeitrag.de, 2026 görünümü; sayfa tarihsiz, tutar valid_until = 2026-12-31). Yasa kaynağı (Rundfunkbeitragsstaatsvertrag) eyalet sözleşmesidir, kullanılmadı. Sayfalarda yumuşak tire (U+00AD) çok; must_contain yalnız tireleme içermeyen ifadelerden seçildi. Muafiyet nedenlerinin tam listesi (Blindenhilfe, Asylbewerberleistungsgesetz vb.) sayfada var ama ifadeler yumuşak tireli olduğu için must_contain'e girmedi; yazar sayfadan okuyabilir.
- Kart 6: TKG'de "taahhüt sonrası fesih" §56 Abs.3 (1 ay), taşınma §60. Sözleşme özeti (Vertragszusammenfassung) ve Kündigungsbutton (BGB §312k) açılmadı.
- Kart 7: Ölçüm yöntemi BNetzA sayfasında (Allgemeinverfügung Nr. 35/2026, 20.04.2026'dan geçerli); sayfa tarihe duyarlı, eşik değerleri kartta rakam vermemek önerilir. BNetzA şikayet formu sayfası (AnfragenBeschwerden/Beschwerde_Internet_Telefon) açılmadı; Schlichtung sayfası kullanıldı (bekleme süresi sayfada günceldir ve değişir, karta yazılmamalı).
- Kart 8: Numara taşıma ücretsizliği ve 1 ay kuralı BNetzA sayfasında; TKG §59 metninde taşıma tutarı için 10 Euro/%20 tazminat var. Mobil numaranın sözleşme bitmeden taşınması BNetzA sayfasında var, ayrı kaynak aranmadı.
- Kart 9: EnWG §41f/§41g (2026 konsolide metin) kesme şartlarını kapsıyor (Mahnung + 4 hafta tehdit, en az 100 Euro, 8 iş günü önceden bildirim). StromGVV §19 yalnız tahrif/usulsüz kullanımda uyarısız kesme; ödeme güçlüğü kuralları EnWG'de. Hartz/Grundsicherung kuruluşlarına bildirim (Sozialhilfeträger) §41g Abs.3-6.

## Tamamen boş kart
Yok.

## Erişim
- Engel yok. gesetze-im-internet.de, rundfunkbeitrag.de, bundesnetzagentur.de açıldı. Tekil madde sayfaları 500 karakterin üstünde (en kısa: StromGVV §20 ≈ 960 karakter, §60 TKG ≈ 1670).

## Dikkat notları
- "Neue Grundsicherung / Grundsicherungsgeld (früher Bürgergeld)": rundfunkbeitrag.de sayfası bu adı kullanıyor; kart bu adı yazarsa kaynak sayfa tarihini söylesin.
- TKG 2021 madde numaraları: §56 sözleşme süresi/sessiz uzama, §57 değişiklik/ücret indirimi/özel fesih, §58 arıza ve tazminat, §59 operatör değişimi ve numara taşıma, §60 taşınma.
- Enerji: kesme kuralı (Stromsperre) EnWG §41f (Haushaltskunden), temel tedarikte ek koruma §41g; StromGVV §19 başka konudur.
- Ikincil kaynak (verbraucherzentrale) kullanılmadı.
