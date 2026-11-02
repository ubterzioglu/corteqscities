# Yanıt yazarı görevi — Zaragoza (CITY-128)

Önce oku: `/home/user/corteqscities/.claude/skills/city-pack/agents/ortak-kurallar.md`, sonra `/home/user/corteqscities/.claude/skills/city-pack/agents/yanit-yazari.md`. Alan anahtarları ve uzunluklar: `/home/user/corteqscities/.claude/skills/city-pack/references/contract_digest.md` §2 (Yanıtlar, Bağlantılar, Adımlar). Yol ve biçimde ortak kurallar esastır; yalnız **kabuk farkı** aşağıda.

## Değerler
- `<city_id>` = `zaragoza`; şehir: Zaragoza, İspanya (Aragón özerk bölgesinin başkenti, Zaragoza ili; Ebro kıyısında)
- `<WORK>` = `/home/user/corteqscities/uretim/zaragoza`
- `<TK>` = `/home/user/corteqscities/corteqs-skills/toolkit/scripts`
- `<PY>` = `/home/user/venv/bin/python`
- `<tarih>` = `2026-11-02`; `<bbox>` = `41.559,41.76,-1.053,-0.777`
- **Hitap: `sen`** (okura 2. tekil; "siz" yok; bir kayıtta biçim karışmaz).
- `<gorev>` = `<konu>` = görev mesajındaki konu slug'ı; `topic_id` = `zaragoza:<konu>`.

## Kabuk (bu oturum Linux; ortak kurallardaki PowerShell yerine)
- PowerShell yok. Komutları Bash aracıyla, **her çağrıda tek komut**, tam yolla çalıştır; `cd`, `&&`, `;`, boru ve heredoc kullanma. Önce ortamı komutun başına tek satır değişken olarak ver: `PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 /home/user/venv/bin/python <TK>/add_sources.py ...`.
- Python işi için önce `.py` dosyasını Write ile `<TMP>` altına yaz, sonra `/home/user/venv/bin/python -I <TMP>/<dosya>.py` ile çalıştır.
- Klasör oluşturma gerekmez: Write aracı klasörü kendisi açar.
- Yollarda `\` yerine `/`.

## Dosyalar (yalnız bunlar)
- `<WORK>/_is/data/parcalar/Yanıtlar.<konu>.jsonl`
- `<WORK>/_is/data/parcalar/Bağlantılar.<konu>.jsonl`
- `<WORK>/_is/claims/<konu>.jsonl`
- (yalnız planlama) `<WORK>/_is/data/parcalar/Adımlar.planlama.jsonl`: ≥4 taşınma yolculuğu adımı.

## ÜLKE PAKETİ KARTLARI — ÇOK ÖNEMLİ
Bu üç dosyada (keşif konusu hariç) ülke paketinden gelmiş kartlar ZATEN VAR (`order` 9000–9095, `featured` = `Hayır`). Bunlar `country_cards`'tır:
- Bu satırları **SİLME ve DEĞİŞTİRME** (Yanıtlar, Bağlantılar ve claims satırlarının hiçbiri). Dosyayı baştan yazma: mevcut satırları oku, kendi satırlarını **SONUNA ekle** (Python'la `open(...,'a')`).
- Ülke kartıyla aynı konuyu tekrar yazma. Ulusal kural orada; sen **Zaragoza'ya ve Aragón'a özgü** olanı yaz: Zaragoza'daki ofis, adres, randevu yolu, yerel hizmet, yerel tarife, yerel kurum. **Aragón bölge paketi YOK:** Aragón kuralları (Salud Aragón, INAEM, Aragón okul kaydı, Aragón vergileri, Aragón yardımları) senin kartlarına girer. Bir ülke kartını "Zaragoza'da nasıl yapılır" diye tamamlayan ayrı kart yazabilirsin (farklı slug, farklı başlık).
- Slug'ın ülke kartlarının slug'larıyla çakışmasın.
- `featured`: konunun en çok 2 kartı `Evet` olabilir; bunları **kendi Zaragoza kartlarından** seç (ülke kartlarına dokunma), geri kalan `Hayır`.

## Kapsam
- `order`: görev mesajındaki aralık (konu sırası × 100 ile başlar), kendi kartlarında artan.
- Kart sayısı: görev mesajındaki hedef (yalnız SENİN ekleyeceğin Zaragoza kartları). Kaynak desteklemiyorsa daha az yaz; hedefi değersiz kartla doldurma. Konunun toplamı (ülke + sen) 26'yı geçmesin.
- Keşifte bulunamayanlar: `<WORK>/_is/kesif/gaps.json` (senin konunun anahtarı). Bunları `gaps`e taşıyabilirsin; uydurma.
- `ilk5.json`'daki 5 soru (`<WORK>/_is/yazar/ilk5.json`, senin konunun anahtarı): her biri bir kartla (ülke kartı ya da senin kartın) cevaplanmalı; kaynağı yoksa `gaps`'e yaz.
- Kaynakların: `<WORK>/_is/yazar/<konu>_kaynaklar.jsonl` (`text_file` = kopyanın temiz metninin tam yolu; yalnız bunları oku). Ülke kartlarının kaynaklarını kendi kartında kullanman gerekirse `source_id`'leri o kartlardaki gibi kullanabilirsin.
- **İşlem kartı (K26):** bir işlemi anlatan kartta dört öğe olmalı: nereye (Zaragoza'daki ofis/kanal ve randevu yolu), ne getir (belge listesi), ne öder (tutar ya da "ücretsiz"), ne kadar sürer / son tarih. Kaynak bir öğeyi vermiyorsa onu uydurma; o öğeyi `gaps`'e yaz. İlk cümle başlıktaki soruyu doğrudan cevaplar (K25).
- Kart başına **en çok 2** `source_ids`; iddiayı desteklemeyen kaynak bağlanmaz. Kart başına en çok 2 Bağlantılar satırı (en az 1 işlem bağlantısı; harita tek bağlantı olamaz).
- Yeni kaynak gerekirse ortak kurallar §4 ile `add_sources` (klasör `snap_<konu>-yazar<sira>`), **konu başına en çok 4 yeni kaynak**. Yalnız resmî yayıncının derin sayfası.
- **Erişim:** `<WORK>/_is/kesif/KESIF_TALIMAT.md` "Bilinen erişim durumu". inclusion.gob.es, mivau.gob.es, camarazaragoza.com, iass.aragon.es, dpz.es, sede.administracionespublicas.gob.es, cortesaragon.es, ecociudadzaragoza.es, educacionfpydeportes.gob.es, mapaoficinas.fnmt.es, hola-zaragoza.avanzagrupo.com, aeropuerto.ctaz.es ERİŞİLEMEZ; tranviasdezaragoza.es JS (boş metin): deneme; o bilgi yoksa `gaps`. Turizm portalı (turismodezaragoza.es) ücret/saat/işlem kuralı kaynağı değildir.
- Tarihe duyarlı bilgi (ücret, tarife, süre, yaş eşiği, 2026 kural değişikliği): kaynağın tarihinden sonra yeni kural çıktı mı, kısa bir arama yap; çelişki varsa `gaps`'e yaz.
- Bellekten bilgi yok; her değişken iddia defterde birebir alıntıyla.

## Sınırlar
- **Alt ajan başlatma.** Geçici dosyalar yalnız görev mesajındaki `<TMP>` klasöründe.
- Bütçe: konu başına 35 dakika / 100 araç çağrısı. Dolunca yazdıklarını tutarlı bırak ve dön.
- Kartları parça parça yaz: her 3–4 kartta bir dosyaya ekle (sonda toplu yazma; ana döngü 10 dk büyümeyen dosyayı takılmış sayar).
- İki konun varsa önce birini bitir, sonra ötekine geç.

## Dönüş (tek satır JSON, konu başına bir nesne; sayıları dosyadan say)
`[{"topic_id":"zaragoza:<konu>","cards":<SENİN eklediğin kart>,"country_cards_kept":<dosyadaki ülke kartı>,"claims":<senin iddiaların>,"new_sources":<add_sources ile eklenen>,"ilk5_covered":[true,...],"gaps":[...]}, ...]`
