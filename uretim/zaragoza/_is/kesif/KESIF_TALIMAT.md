# Kaynak keşfi talimatı — Zaragoza

## Bilinen erişim durumu (2.11.2026, fetch_snapshot yoklaması: _is/kesif/erisim_snap/index.jsonl, 42 adres)
Engelli alan adını DENEME; ona bağlı bilgiyi başka resmî yayıncıdan bul ya da baştan `gaps`'e yaz.

**Çalışıyor (200):** zaragoza.es (Zaragoza Belediyesi; `/sede/servicio/tramite/` işlem rehberi açılıyor, `/sede/portal/movilidad/` ve `/sede/portal/medioambiente/` açılıyor; `/sede/portal/` kökü 404 — derin sayfaları menüden izle), aragon.es (Gobierno de Aragón; anasayfa ince, `/tramites` ve derin sayfalar), inaem.aragon.es (Aragón iş kurumu), educa.aragon.es (eğitim; okul kaydı), saludinforma.es (Salud Aragón vatandaş portalı), zaragozavivienda.es (belediye konut şirketi), zaragoza.avanzagrupo.com (şehir otobüsü işletmecisi), bizizaragoza.com (BiZi bisiklet), ctaz.es (Zaragoza metropol ulaşım konsorsiyumu; consorciozaragoza.es yönlendirir), aena.es/es/zaragoza.html (ince), renfe.com, sede.policia.gob.es (yabancılar işlemleri), sepe.es, dgt.es, boe.es, ine.es, exteriores.gob.es, administracion.gob.es, hacienda.gob.es, mpr.gob.es, unizar.es, zaragozadeporte.com (belediye spor), turismodezaragoza.es (turizm portalı: ücret/saat/işlem kuralı kaynağı DEĞİL).

**İnce ya da boş metin (derin sayfa dene):** tranviasdezaragoza.es (51 karakter; JS), boa.aragon.es (0; BOA belgelerini doğrudan belge adresinden dene), seg-social.es (anasayfa boş; derin sayfa dene, `?lang=es` ekle — İngilizce sürüme yönlendirebiliyor), iaf.es (0), policia.es (465; sede.policia.gob.es kullan).

**Engelli / erişilemiyor — deneme:**
- inclusion.gob.es, mivau.gob.es, camarazaragoza.com: 403.
- iass.aragon.es, dpz.es, sede.administracionespublicas.gob.es: bağlantı sıfırlandı.
- cortesaragon.es (Aljafería'yı yöneten Cortes de Aragón): bağlantı koptu — Aljafería ziyaret bilgisini önce bir kez dene, açılmazsa places fazında başka resmî sayfa.
- ecociudadzaragoza.es (su/arıtma şirketi): tünel bağlantısı kurulamadı — su aboneliği bilgisini zaragoza.es derin sayfalarında ara.
- sede.agenciatributaria.gob.es: bağlantı sıfırlandı (geçici olabilir; bir kez dene, açılmazsa agenciatributaria.es).

Not: Ulusal kurallar ülke paketinde (`_is/ulke_paketi`, 96 kart; Aragón bölge paketi YOK). Şehir yazarları Zaragoza ve Aragón'a özgü bilgiyi yazar: bölge kuralları (Salud Aragón, INAEM, Aragón okul kaydı, Aragón vergileri, IASS yardımları) ülke paketinde olmadığı için şehir kartlarına girer.
