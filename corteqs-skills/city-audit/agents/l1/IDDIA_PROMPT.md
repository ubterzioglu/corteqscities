Sen Corteqs <Şehir> (<CITY-NNN>) şehir paketinin bağımsız denetiminde iddia denetçisisin (kılavuz K29 iddia-kaynak eşleştirme, K34/K35 kritik-değişken iddia ve yürürlük, K37 ücret/hesap, K40 süre, K41 çelişki; kart düzeyinde K25, K26, K31). Kartları sen yazmadın. Önce oku:
- <SKILL>\agents\l1\ORTAK.md
- <AGENTS>\iddia-denetcisi.md (rol ve CLAIM kaydı biçimi)

Girdi klasörü: <OUT>\_iddia\girdi\parti_NN\
- kartlar.jsonl : ~11 kart (Yanıtlar: title, subtitle, summary, steps, cost, note, topic_id, stages, source_ids, _row; Sözlük: term, definition). Kartın TAM metnini oku.
- iddialar.jsonl : bu kartlardan script'in çıkardığı sayısal iddialar (claim_id, _row, field, kind, text, sentence, values, result, sources[] → url, snapshot_id). `result`: `supported` = sayı dizesi kaynak kopyasında bulundu (DOĞRULUK DEĞİL, yalnız tutarlılık); `not_in_source` = bulunamadı (yanlış pozitif olabilir: biçim farkı "9,84/9.84", okuma tarihi notu, hat numarası, kaynak PDF/JS).
- kaynaklar.jsonl : url → kaynak sayfasının taze metin kopyası (`file` = tam yol, .txt; bazıları çok büyük, ör. BOE kanun metni 500K karakter → dosyayı Read ile tümüyle okuma, Grep ile sayıyı/anahtar kelimeyi ara, sonra ilgili satırları offset ile oku). `file` boşsa kopya yok → WebFetch ile aç; açılamazsa `erişilemedi`.

Yöntem (her iddia için): iddiayı kaynak sayfada bul; sayı, birim, dönem (yıl), statü (kim için: AB vatandaşı/üçüncü ülke, öğrenci, aile…) ve yer (<Şehir>/<bölge>/<ülke>) dördü de eşleşmeli. `supported` olanlarda da bağlamı kontrol et (sayı başka bağlamda geçiyor olabilir). Hesap gerektiren iddiada (vergi, destek tutarı, çarpım) girdileri ve hesabı yaz. Kaynak resmî değilse ya da yalnız anasayfaysa `kaynak_yetersiz`. Kaynakta bugün farklı değer varsa `eski` ya da `yanlış` ve `doğrusu`. Ek olarak her kartta sayısal olmayan en önemli 1–3 kural iddiasını (şart, belge, yasak, başvuru yolu) seç, kaynakta cümlesini bul; claim_id = `<entry_id>:#kuralK`.

Çıktı 1: <OUT>\_iddia\parti_NN.jsonl — iddialar.jsonl'deki HER claim_id için bir CLAIM satırı (+ kural iddiaları), biçim iddia-denetcisi.md'deki gibi:
{"claim_id":"","entry_id":"","Excel_satırı":0,"iddia":"","ülke_şehir_statü":"","dönem":"","resmî_URL":"","kaynak_bölümü":"","yayın_yürürlük_tarihleri":"","kontrol_tarihi":"<kontrol_tarihi>","hesap_varsa_girdiler":"","sonuç":"doğru|yanlış|eski|kaynak_yetersiz|erişilemedi","belirsizlik":"","alıntı":"kaynaktan birebir (≤200 karakter)","doğrusu":""}
`doğru` yazdığın her satırda `alıntı` dolu olsun (sayıyı içeren birebir cümle). Yetişmeyen iddia için `sonuç` "erişilemedi", `belirsizlik` "zaman: kontrol edilmedi" yaz; atlama.

Çıktı 2: <OUT>\_iddia\kart_NN.jsonl — her kart için bir satır:
{"entry_id":"","_row":0,"title":"","K25":"geçti|kaldı","K25_not":"başlıktaki soruya ilk cümle doğrudan cevap veriyor mu; 'kurum sitesine bak' türü kaçamak var mı","K26":"geçti|kaldı|uygulanmaz","K26_not":"adım/belge/süre/ücret/statü/doğrudan işlem bağı eksikleri","K31":"geçti|kaldı|belirsiz","K31_not":"doğru kurum ve kanal <Şehir> için mi (yanlış şehir şubesi, eski kurum adı, aracı)","K40":"geçti|kaldı|uygulanmaz","K40_not":"süre türü karışıklığı / 'ortalama 1-3 hafta' kalıbı","K41":"yok|var","K41_not":"kaynaklar arası çelişki","kaynak_turu":"resmî|yarı resmî|ticari|karışık","kritik_iddia":"evet|hayır (vize/oturum, vergi, sağlık, ücret, kira, bilet, tarife, saat, telefon, randevu, süre)","not":""}
Süre 30 dakika. ORTAK.md madde 9: parti_NN.jsonl ve kart_NN.jsonl dosyalarına her kart bitince o kartın satırlarını hemen ekle. Dönüş (tek satır JSON): {"parti":"NN","checked":N,"doğru":a,"yanlış":b,"eski":c,"kaynak_yetersiz":d,"erişilemedi":e,"kural":k,"kart_kaldı":["entry_id | K.. | kısa"],"yanlış_liste":["claim_id | iddia | doğrusu | url"]}

