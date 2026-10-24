# ES ulusal paketi, konu "saglik": boşluklar

Genel: 7 kart (order 601-607), kart başına en çok 2 source_id, tüm alıntılar kaynak metninde doğrulandı. Kartlar şehir-nötr; sağlık hizmetini özerk bölgeler yönettiği için bölgeye göre değişen yerler kaynaktaki cümleyle çerçevelendi, bölge adı ve bölgeye özgü rakam verilmedi.

## Yazılmayanlar (kaynak kanıtlamadığı için)
- #1 Kamu sağlığı: Türkiye-İspanya ikili sağlık anlaşması yazılmadı (kaynakta yok). Kayıtsız yabancı için "belge nereden alınır / randevu" bölgeye bağlı, bölge adı verilmedi.
- #2 Sigorta: "tüm vizeler için sigorta zorunlu" yazılmadı; yalnız RD 1155/2024 art. 35 (uzun süreli öğrenci vizesi) ve art. 61.b (çalışmaksızın geçici oturum) anıldı. Convenio especial tutarları (60 € / 157 €) Sanidad sayfasındaki hâliyle yazıldı; sayfada yıl yok, "RD 576/2013 sabit tutarı" ve "bölgeler ek hizmet eklerse artabilir" bilgisi bu sayfa metninde geçmediği için yazılmadı. Sanidad sayfasının <title> alanı hatalı ("Vacantes en organismos internacionales"), içerik doğru.
- #3 Copago: oranlar ve tavanlar BOE konsolide metnindeki (son güncelleme 31/07/2026) hâliyle yazıldı. Çalışan sigortalılarda 35.000 € üzeri gelir için aylık tavan metinde yok, yazılmadı. Muafiyet listesinden yalnız dört kalem yazıldı (liste daha uzun).
- #4 Acil: 061 (sağlık acil) için ulusal kaynak yok, hiç yazılmadı. 112.es sayfası https ile açılmadığı için kullanılmadı. RD 903/1997 1997 tarihli özgün metindir.
- #5 Aşı takvimi: hangi aşının hangi yaşta yapıldığı yazılmadı (takvim PDF'i okunmadı). Yalnız takvimin varlığı, 2026 yılı, CISNS ortak yapısı ve uygulamanın özerk bölgelere ait olduğu yazıldı.
- #6 Hamilelik/doğum: izin süresi (hafta sayısı) yazılmadı; Seguridad Social sayfası süreyi ET art. 48'e atıf yaparak veriyor. Sayfadaki 6 haftalık zorunlu dinlenme, çoklu doğumda 6 hafta ek ödenek, 4 hafta önceden başlama ve prim şartsız ödenekte +14 gün hükümleri süre rakamı sayıldığı için yazılmadı. Güncel IPREM tutarı kaynakta yok. Doğum ödeneğinin yabancı uyruklara göre farkı kaynakta yok. Ayrıntılı pediatri takvimi (hangi ay hangi muayene) kaynakta yok.
- #7 Ruh sağlığı ve yaşlı bakımı: Ley 39/2006 art. 5 güncel metni (23/10/2026 yürürlük) metinden okunarak yazıldı; asilo/geçici koruma istisnası metinde açıkça var. 6 yaşından küçük çocuklar için DA 13 içeriği okunmadı, yalnız varlığı anıldı. Bağımlılık derecelerinin tanımı, başvuru yeri ve süreç Ley metninde bölgelere bırakılıyor; Imserso SSS sayfası (başvuru bölgenin órgano gestor'una yapılır, karar tüm ülkede geçerli; 2022-2023 tarihli) kart başına 2 kaynak sınırı nedeniyle kullanılmadı. Gerekirse: https://imserso.es/autonomia-personal-dependencia/sistema-autonomia-atencion-dependencia-saad/preguntas-frecuentes/tramitacion-reconocimiento-situacion-dependencia-derecho-prestaciones-sistema

## Tarihe duyarlı kartlar (valid_until.json)
- #2, #3, #5, #6, #7: kaynakta ileriye dönük bitiş tarihi yok, hepsi null. #3 sayfa tarihi 31/07/2026, #7 yürürlük 23/10/2026 ve #5 takvim yılı 2026 kart metninde belirtildi.
- #3 copago oranları RDL 11/2026 ve RDL 12/2026 ile değişen metindir; yeni değişiklikte kart güncellenmeli.
- #7 art. 5'in 23/10/2026'dan önceki metni farklıdır; kart yalnız güncel metni anlatır.

## Editör G2 turu: yazılmayanlar
- #1 Kamu sağlığı: "Türk vatandaşı AB serbest dolaşım rejiminin dışındadır" cümlesi kartın kaynaklarında (092, 091) olmadığı için silindi; RD 240/2007 art. 2 (AB vatandaşının aile üyesi, uyruğu ne olursa olsun) kart başına 2 kaynak sınırına sığmadı. Convenio especial'in 1 yıl ikamet ve empadronamiento koşulları kart #2'de; kart #1 yalnız 091'deki "başka kamu korumasına erişimi olmayan" kaydını ve Orden SSI/1475/2014 atfını yazar.
- #2 Sigorta: art. 35 ve art. 61 dışındaki vize/oturum türleri için sigorta şartı yazılmadı (kaynakta ayrıca taranmadı). Avrupa Sağlık Sigortası Kartı (TSE) notu Türk okuyucu için ilgisiz olduğundan silindi.
- #3 Copago: "asegurado activo" tanımı kaynakta yok; "çalışan" çevirisi çıkarıldı, çalışmayan sigortalıların hangi satıra girdiği yazılmadı. Art. 101.3 (hak edilen ödeme biçiminin gerekçelendirilmesi) kaynakta var, adım 3 korundu.
- #6 Doğum ödeneği: prim şartsız ödeneğin +14 gün hükümleri ve ayrıntılı süre rakamları yazılmadı.
- #7 Dependencia: Ley 39/2006 art. 5.2'nin (yabancılar için LO 4/2000, antlaşmalar) havale cümlesi silindi; genel yabancının hak koşulu kaynakta olmadığından yazılmadı.
