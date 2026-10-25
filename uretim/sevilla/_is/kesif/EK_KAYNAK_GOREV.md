# Hedefli ek kaynak araması — Sevilla (yazar boşlukları)

Kurallar ve erişim haritası `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\kesif\KESIF_GOREV.md` ile aynı (resmî derin sayfa, `must_contain` birebir ve sayfada doğrulanmış, Wikipedia/ticari yok, engelli alan adlarını deneme: sevilla.org, sede.sevilla.org, tussam.es, consorciotransportes-sevilla.com, lipasam.es, aena.es, cita previa sede.administracionespublicas.gob.es).

Yazarlar aşağıdaki bilgileri kaynak bulamadığı için yazamadı. Her biri için **başka bir resmî yayıncıda** derin sayfa ara (ör. BOE/BOJA/BOP Sevilla duyuruları, Delegación/Subdelegación del Gobierno, Junta'nın il sayfaları, Diputación, kamu hastaneleri, mfa.gov.tr / Türkiye'nin temsilcilik sayfaları, renfe.com derin sayfa, ctan.es). Bulamadığını uzun uğraşma; `gaps`'e yaz.

Öncelik sırası:
1. **oturum:** Sevilla Oficina de Extranjería adresi ve işleri (Subdelegación del Gobierno en Sevilla / mpt.gob.es / administracionespublicas.gob.es dışındaki alt sayfalar); Sevilla'da TIE parmak izi (Policía Nacional, Comisaría Provincial de Sevilla, Plaza de España) adresi; Türkiye'nin Sevilla'ya en yakın konsolosluğu ya da fahri konsolosluğu (mfa.gov.tr derin sayfa).
2. **resmi:** Sevilla'da empadronamiento (belediye sitesi dışında resmî bir anlatım, ör. BOP'ta yayımlanan Padrón yönetmeliği, Junta/INE'nin Sevilla'ya özgü sayfası); DGT Jefatura Provincial de Sevilla adresi (dgt.es derin sayfa); Registro Civil de Sevilla adresi (mjusticia.gob.es / sedejudicial.justicia.es).
3. **para:** Sevilla şehrinde IBI ve araç vergisini (IVTM) hangi kurumun topladığı: Agencia Tributaria de Sevilla (belediye) mi, OPAEF mi? (BOP'taki vergi takvimi / ordenanza fiscal duyurusu, OPAEF'in kapsadığı belediyeler listesi).
4. **fatura:** Sevilla'da çöp vergisi (tasa de basura / TRU) nasıl toplanıyor (BOP ordenanza fiscal; EMASESA faturasına dahil mi).
5. **ulasim:** TUSSAM ya da Consorcio de Transportes Metropolitano del Área de Sevilla tarife (BOP/BOJA'da yayımlanmış tarife duyurusu; ctan.es / juntadeandalucia.es Red de Consorcios derin sayfa); Sevilla havalimanı–şehir otobüsü (EA) resmî bilgi.
6. **gunluk:** Feria de Abril 2027 resmî tarihi; Sevilla belediye halk kütüphaneleri (sevilla.org dışı resmî liste).

## Çıktı
Her konu için `C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\kesif\<konu>_ek\selected.jsonl` (klasörü oluştur), satır: `{"url","must_contain":["..."],"title","publisher","lang","why","gap":"hangi boşluğu kapatır (Türkçe, kısa)"}`. UTF-8, BOM'suz.

## Sınırlar
Alt ajan başlatma. Geçici dosyalar yalnız görev mesajındaki klasörde. Bütçe 30 dk / 100 araç çağrısı.

## Dönüş
Tek satır JSON: `{"topics":{"<konu>":<adres sayısı>},"gaps":["<konu>: <bulunamayan>"]}`
