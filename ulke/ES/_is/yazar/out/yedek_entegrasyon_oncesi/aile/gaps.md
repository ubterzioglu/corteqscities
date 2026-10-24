# ES ulusal paketi, konu "aile": boşluklar (order 801-804)

Genel: 4 kart, kart başına en çok 2 source_id, tüm alıntılar kaynak metninde doğrulandı. Kart 3 (okul diploması denkliği) mevcut kartla çakıştığı için yazılmadı.

## Yazılmayanlar
- Kart 801 (eğitim sistemi): yabancı çocuğun okula kaydı için ikamet izni/homologación gerekip gerekmediği kaynakta yok. Başvuru takvimi, form ve puanlama bölgeye göre değişir; yalnız LOE art. 84 çerçevesi yazıldı. Zorunlu eğitimin 6 yaş başlangıcı/16 yaş bitişi LOE art. 4'ten; Bakanlık derin sayfası bulunamadı. Gelir/yakınlık ölçütlerinin puan ağırlıkları (art. 84.2'deki yüzde sınırı) yazılmadı.
- Kart 802 (yabancı diploma): Türk lise diploması için hangi yolun geçerli olduğu ülke bazlı kaynakta (UNEDasiss "Información país por país") okunmadı; kartta yalnız UNEDasiss'in sınavsız grup listesi ve "AB dışı diğer ülkeler" yolu aktarıldı. Orden EFD/550/2025 (meslek diplomaları listesi) ve PCE tarihleri/ücretleri yazılmadı. UNEDasiss kamu üniversitesi (UNED) sitesidir, .gob.es değildir.
- Kart 803 (IMV): başvuru sonuç süresi, ödeme tarihi, gelir/varlık eşik tablosunun tamamı (yalnız garantili gelirin iki tutarı ve çocuk eki yazıldı) ve yasal ikamet süresinin oturum türlerine göre farkı kaynakta yok. inclusion.gob.es erişim reddi verdi. Sede electrónica doğrudan adresi kaynak listesinde olmadığı için Bağlantılar'a konmadı.
- Kart 804 (MEC bursu): 19 Mayıs bitiş tarihi yalnız "FP, Bachillerato ve diğer üniversite dışı" sayfasında geçiyor; üniversite (grado/máster) bursu için başvuru dönemi kaynakta yok. Kaynak sayfada 19 Mayıs için yıl yazmıyor. BOE 2026-2027 çağrısı (convocatoria) metni okunmadı; gelir eşiği tablosu (umbral 1-3) ve engelli/ada ek tutarları yazılmadı. Bölge (özerk) bursları kaynakta yok.

## Tarihe duyarlı kartlar (valid_until.json)
- ingreso-minimo-vital-ve-cocuk-destegi: 2026-12-31 (kaynak tutarlar "en 2026" diyor; açık bitiş tarihi yok, yıl sonu alındı).
- mec-burslari-ab-disi-sart-ve-basvuru-donemi: null. Tutarlar 2026-2027 dönemi için yazıldı ama kaynakta açık bitiş tarihi yok; kart metni dönemi belirtir. Editör bir bitiş tarihi (ör. dönem sonu) belirlemek isterse güncellenmeli.
- egitim-sistemi-zorunlu-egitim-ve-okul-turleri, yabanci-lise-diplomasi-ile-universiteye-giris: null (yasal çerçeve; UNEDasiss sayfasının "Fechas clave 2026" tarihleri metinde yok).

## Editör (G3) eklemeleri
- Kart 802 (yabancı diploma): Türk lise diplomasının homologación'unun zorunlu olup olmadığı kartın kaynaklarında (RD 534/2024, UNEDasiss publico_destino) açıkça yazmıyor; kaynak yalnız "homologación şartlarını karşılayanlar bu yoldan girer" diyor. Denetçi canlı UNEDasiss SSS'inde AB dışı/anlaşmasız sistemler için homologación'un "trámite indispensable" olduğunu gördü; SSS kayıtlı kaynak olmadığı için karta yazılmadı, başlık kaynağın cevaplayabildiği soruya daraltıldı. Kayıtlı kaynağa UNEDasiss SSS eklenirse (kart başına 2 kaynak kotası gözetilerek) başlığa net cevap yazılabilir. Türkiye'nin UNEDasiss ülke bazlı sayfadaki yeri de okunamadı (oturum gerektiriyor).
- Kart 801: özel (concertado olmayan) okulların ücretlerine dair bilgi kaynakta yok; kartta yalnız kanundaki "zorunlu ve ücretsiz" tanımı yazıldı.
- Kart 803: birimler için varlık sınırı tablosunun tamamı (birim büyüklüğüne göre) yazılmadı; yalnız tek yetişkin tutarları var.
- Kart 804: üniversite (grado/máster) bursu için başvuru dönemi ve yılı kaynakta yok (kayıtlı üniversite "cómo solicitarla" sayfası yok); kartta yalnız FP/bachillerato sayfasındaki "19 Mayıs'ta sona erdi" cümlesi, kapsamı belirtilerek ve yılsız duruyor. valid_until 2027-05-31: 2026/27 tutarları, sonraki çağrıdan önce yeniden bakılmalı.
