# ES ulusal paketi, konu "resmi": boşluklar

Genel: 13 kart, 152 claim, 19 bağlantı. Tüm alıntılar kaynak metinde doğrulandı (boşluk ve büyük/küçük harf farkı gözetilmeden). Kartlar şehir-nötr. Sert kural (ortak-kurallar §6.2/§7) "teyit et" ifadesini yasaklıyor; #8 ve #13'te görev mesajı istediği için not alanına yazıldı, ana döngü karar versin.

## Tarihe duyarlı kartlar (valid_until.json hepsi null)
- #8 belge-ceviri-ve-apostil: apostil ücreti kaynakta yok; geçerlilik tarihi bilinmiyor. Not alanında "ücreti teyit et" var.
- #9 noter-islemleri-ve-ucretleri: tutarlar BOE birleştirilmiş metninden (son güncelleme 17/11/2011). Kaynakta bitiş tarihi yok. Tarife 1989 tarihli kararın ekidir; sonraki değişiklikler başka belgelerde olabilir, doğrulanmadı.
- #12 yabanci-ehliyet-degisimi: DGT sayfasında harç tutarı "XX,XX€" yer tutucu olarak görünüyor (harç türü 2.3 ve 2.1). Tutar kartta yok. 032 sayfası "Fecha actualización: 28/04/2025" diyor, bitiş tarihi yok.
- #13 arac-kaydi-ulusal-cerceve: vergi tutarı kaynakta yok (yalnız Modelo 576, 06, 05 ve 3 ay süresi). DGT harcı tutarı (yeni araç genel durum) sayfada yok; yalnız ciclomotor harcı (27,85 EUR) var, kullanılmadı. Not alanında "vergi tutarını teyit et" var.

## Kart bazında
- #1 empadronamiento: yalnız ulusal çerçeve. Zorunlu veri listesi (md. 16.2) kartta yok. Belge listesi, ofis, randevu şehir katmanında.
- #2 certificado/volante: volante/certificado'nun hangi kurumda hangisinin istendiği kaynakta yok; kartta yalnız iki belgenin niteliği var.
- #3 sosyal güvenlik no: 020 kaynağı ev hizmetlisi (TA.2/S) form sayfası; NAF/NUSS'un çevrimiçi hizmetle ya da TA.1 ile alınabildiğini söylüyor. Kimler başvurabilir, hangi belgeler, süre kaynakta yok. Daha uygun bir TGSS "Solicitar el número de Seguridad Social" sayfası bulunursa kaynak değişmeli.
- #4 vida laboral: ücret/süre bilgisi yok (sayfa ücretsizlik demiyor, yazılmadı).
- #5 NIF/NIE: NIE harç tutarı kaynak metninde yok ("Ver importe de tasas" bağlantısı var). NIE başvuru süresi 5 gün; AB vatandaşı kaydı (yeşil NIE, EX18) bu kartta yok (oturum konusunda).
- #6 Cl@ve: kayıt (ofiste ya da çevrimiçi) adımları kaynak sayfalarında yok; kartta yalnız "önce kayıt ol" var.
- #7 FNMT: sayfa başında "DNIe NFC ile sertifika alma şu an çalışmayabilir" uyarısı var; tarihe duyarlı olduğu için karta yazılmadı. Video kimlik doğrulama seçeneği yalnız başlıkta geçiyor, yazılmadı. Sertifika ücreti/geçerlilik süresi kaynakta yok.
- #8 apostil/tercüme: yeminli tercüme ücreti (serbest piyasa) ve apostil ücreti yok. 027 sayfası İspanya'da düzenlenen belgenin apostili ile ilgili; hangi makamın hangi belgeyi apostil ettiği ayrıntısı (noter dışı) kaynakta yok.
- #9 noter: 028 tarifesi 1989 kararı; elektronik şirket kuruluşu, ipotek vb. kalemler kartta yok. Kartta yazılan tutarlar kaynaktaki gibi 6 hane ondalıklı euro; yuvarlama yapılmadı.
- #10 Libro de Familia: Libro de Familia'nın ne olduğu, nasıl alınacağı, hangi işlemde istendiği kaynakta yok. Geçiş rejiminin bitiş tarihi kaynakta yok.
- #11 Registro Civil: kayıt süreleri (doğum bildirimi vb.), çevrimiçi başvuru adresi (Adalet Bakanlığı sedesi) kaynak metninde yalnız adıyla geçiyor, bağlantı verilmedi.
- #12 ehliyet: anlaşmalı ülkeler listesi (Türkiye'nin listede olup olmadığı) kaynak metninde yok; liste açılır menü içinde, indirilen metne girmemiş. Türk okuyucu için kritik: DGT listesinden Türkiye'yi doğrulamak gerekir (ayrı kaynak alınmalı).
- #13 araç kaydı: yalnız ulusal çerçeve. Bölgesel vergi ve ofis bilgisi yok. IVTM belediye vergisi, tutarı yok.

## Bağlantılar
Tüm url'ler resmi_kaynaklar.jsonl'deki url ile aynıdır. #1 (BOE yasa metni), #3 (form sayfası) ve #10 (BOE yasa metni) için işlevsel bir işlem sayfası yok; "Bilgi al" etiketli en yakın resmi sayfa kullanıldı.
