# Kaynak keşfi talimatı — Sevilla

## Bilinen erişim durumu (24.10.2026, fetch_snapshot yoklaması: _is\kesif\erisim_snap\index.jsonl)
Engelli alan adını DENEME; ona bağlı bilgiyi baştan `gaps`'e yaz.

**Çalışıyor (200):** metro-sevilla.es, emasesa.com, visitasevilla.es, sevillaactiva.es, dipusevilla.es, juntadeandalucia.es (sede, SAS sspa.juntadeandalucia.es, SAE), aopandalucia.es, hospitalmacarena.es, policia.es, inclusion.gob.es, sede.agenciatributaria.gob.es, seg-social.es, sepe.es, dgt.es, renfe.com, boe.es, exteriores.gob.es, ine.es, us.es, upo.es, catedraldesevilla.es, alcazarsevilla.org.

**Engelli / erişilemiyor — deneme:**
- sevilla.org ve sede.sevilla.org (Sevilla Belediyesi): bağlantı zaman aşımı (ağ düzeyinde; http ve https). Belediye bilgisi Junta, Diputación (dipusevilla.es, BOP), visitasevilla.es (belediye turizm konsorsiyumu), sevillaactiva.es (belediye istihdam), EMASESA, metro ve ulusal kurumlardan alınır.
- consorciotransportes-sevilla.com (metropol ulaşım konsorsiyumu): zaman aşımı. ctas.ctan.es: DNS yok.
- tussam.es (şehir otobüsü): 403 bot engeli.
- lipasam.es (temizlik): TLS sertifika hatası. aena.es: TLS sertifika hatası.
- hospitaluvirgenrocio.es: DNS yok (hastane bilgisi SAS sayfalarından). clicsalud.es: DNS yok.
- sede.administracionespublicas.gob.es (cita previa): 403. mivau.gob.es, transportes.gob.es: 403.
- juntadeandalucia.es/educacion/portals/web/escolarizacion: 503 (geçici olabilir; başka eğitim sayfası dene).

Not: Ulusal ve Endülüs kuralları ülke paketinde (`_is\ulke_paketi`, 105 kart). Şehir yazarları yalnız Sevilla'ya özgü bilgiyi yazar.
