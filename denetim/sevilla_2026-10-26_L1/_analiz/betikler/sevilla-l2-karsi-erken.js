export const meta = {
  name: 'sevilla-l2-karsi-erken',
  description: 'Sevilla L2 hızlandırma: işi bitmiş grupların karşı denetimleri erken (mekân, foto, açık-mı, lisans, bağlantı, kaynak, mahalle/rota), en çok 3 eşzamanlı',
  phases: [
    { title: 'Ana denetim', detail: 'Opus (high), en çok 14 eşzamanlı' },
    { title: 'Karşı denetim', detail: 'olumsuz kararları çürütmeye çalışan bağımsız Opus ajanları' },
  ],
}

const R = String.raw`C:\temp_private\corteqs\0000_newera`
const OUT = String.raw`C:\temp_private\corteqs\0000_newera\denetim\sevilla_2026-10-26_L1`
const SKILL = String.raw`C:\temp_private\corteqs\0000_newera\corteqs-skills\city-audit`
const AGENTS = String.raw`C:\temp_private\corteqs\0000_newera\corteqs-skills\city-pack\agents`
const SCR = String.raw`C:\Users\BARIS-~1\AppData\Local\Temp\claude\c--temp-private-corteqs-0000-newera\928be71a-0e9c-4b09-b172-91a95baa00e3\scratchpad`
const PY = String.raw`C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe`
const PKG = String.raw`C:\temp_private\corteqs\0000_newera\uretim\sevilla\paket`

const PH = String.raw`Yer tutucular: <OUT>=${OUT} ; <SKILL>=${SKILL} ; <AGENTS>=${AGENTS} ; <ROOT>=${R} ; <Şehir>=Sevilla ; <CITY-NNN>=CITY-107 ; <city_id>=sevilla ; <ülke>=İspanya ; <bölge>=Endülüs (Andalucía) ; <yerel_dil>=İspanyolca ; <kontrol_tarihi>=2026-10-26 ; <şehir merkezi enlem, boylam>=37.405015, -5.980007. Bu bir L2 (tam kapsam) denetimidir.`

const ENV = String.raw`Ortam kuralları: hiçbir komutta cd kullanma; tam yol yaz; dosyaları Read/Glob/Grep ile oku (büyük dosyada önce Grep, sonra offset ile Read); klasörü PowerShell New-Item -ItemType Directory -Force <yol> ile oluştur; 2 dakikada dönmeyen komutu bırak. Python gerekiyorsa kodu komuta gömme (heredoc yok): .py dosyasını geçici klasörüne Write ile yaz, & '${PY}' -I -X utf8 <dosya.py> ile çalıştır. ${R}\uretim\ altına hiçbir şey yazma (paket salt okunur). Arama motoru ya da WebFetch özeti birebir alıntı değildir; olumsuz karar (yanlış/eski/kaldı/reject) yalnız kaynak kopyasındaki ya da sayfanın ham metnindeki birebir alıntıya dayanır (ORTAK.md madde 10). Çıktı dosyanı ilk kayıt biter bitmez oluştur ve her kayıtta ekle; dosya önceki bir denemeden kalmışsa içindeki kimlikleri atla (10 dakika büyümeyen dosya takılmış sayılır). İş bitince yalnız tek satır JSON özet döndür.`

const IDDIA_EK = String.raw`Ek dikkat (önceki dış denetimden): resmî süreç kartlarında (oturum/TIE/izin türleri, arraigo, aile birleşimi, Seguridad Social, vergi, nüfus kaydı, sağlık) "cümle kaynakta var mı" yetmez; kaynağın kartın anlattığı AŞAMA ve STATÜ için olup olmadığına da bak (ilk başvuru ↔ yenileme formu, AB vatandaşı ↔ üçüncü ülke, izinli ↔ izinsiz). Yanlış aşamanın kaynağı yanlış ya da kaynak_yetersizdir. Kartta yılı yazılmamış tarih ("geçen 9 Ekim") belirsizlik olarak not edilir.
L2 ekleri: (a) iddialar.jsonl boşsa ya da kartın sayısal iddiası yoksa kartın en önemli 1–3 kural/olgu iddiasını yine kaynakta doğrula (claim_id = <entry_id>:#kuralK). (b) kart_NN.jsonl satırına ayrıca şu alanları ekle: "K32":"geçti|kaldı","K32_not":"dil hatası, kart içi çelişki, kaynaksız vaat (garanti/kesin/her zaman)","K48":"geçti|kaldı|uygulanmaz","K48_not":"yalnız Sözlük kartı: terim Sevilla'da gerçekten karşılaşılan, işe yarar bir terim mi, tanım doğru mu".`

function acikmi(nn) {
  return String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\ACIKMI_PROMPT.md — onu oku ve aynen uygula.
${PH}
Yerel kapanış sözcükleri: cerrado, cierra definitivamente, cierre, cerrado temporalmente, se traslada, traslado, obras, reforma, rehabilitación, reapertura. Kontrol yılı 2026; açık kanıtı 2025 ya da 2026 tarihli faaliyet olmalı (resmî ajanda, basın haberi, belediye bildirimi). Ziyaretçi yorumu (Google/Tripadvisor), footer telif yılı ve tarihsiz saat sayfası açık kanıtı sayılmaz.
Senin partin: NN = ${nn} → girdi ${OUT}\_acikmi\parti_${nn}.jsonl ve ${OUT}\_acikmi_girdi\girdi_parti_${nn}.jsonl ; çıktı ${OUT}\_acikmi\parti_${nn}_dogrulama.jsonl. Bu dosya varsa içindeki mekânlar önceki turda doğrulandı: onları ATLA, dosyaya yalnız kalan mekânların satırlarını EKLE (mevcut satırları silme, değiştirme). ${OUT}\_acikmi\ klasörüne başka hiçbir dosya yazma.
Geçici klasörün: ${SCR}\l2_acikmi_${nn}_w\
${ENV}`
}

function iddia(nn) {
  return String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\IDDIA_PROMPT.md — onu oku ve aynen uygula.
${PH}
Senin partin: NN = ${nn} → girdi ${OUT}\_iddia\girdi\parti_${nn}\ ; çıktılar ${OUT}\_iddia\parti_${nn}.jsonl ve ${OUT}\_iddia\kart_${nn}.jsonl (ilk kart bitince ikisini de oluştur, her kart bitince ekle; dosya varsa içindeki claim_id/entry_id'leri atla).
${IDDIA_EK}
Geçici klasörün: ${SCR}\l2_iddia_${nn}_w\
${ENV}`
}

function mekan(p) {
  return String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\MEKAN_PROMPT.md — onu oku ve aynen uygula.
${PH}
PAY = ${p} → girdi ${OUT}\_l\girdi\mekan_${p}.jsonl (30 mekân) ; çıktı ${OUT}\_l\mekan_${p}.jsonl.
Script ipuçları (karar değil): aynı koordinatı paylaşan çiftler: metropol-parasol-antiquarium ↔ mercado-de-la-encarnacion (37.39325, -5.99188), jardines-del-prado-de-san-sebastian ↔ ciudad-de-los-ninos-prado (37.37969, -5.98689), estadio-la-cartuja ↔ estadio-benito-villamarin-tur (37.41724, -6.00456). Bu mekânlar senin payındaysa gerçekten aynı yerde olup olmadıklarını kontrol et (Benito Villamarín Heliópolis'te, La Cartuja Isla de la Cartuja'da; tur kartının hangi stadı anlattığını ve Betis'in 2025–2027 geçici stadını resmî kaynakla netleştir). Açık-mı turundan bilinen olgular (kanıt değil): Costurero de la Reina'daki turizm noktası Nisan 2026'da kapandı; Plaza Nueva'da Ekim 2025'ten beri şantiye; Museo Arqueológico 2020'den beri tadilatta; Teatro Lope de Vega Eylül 2026'da yeniden açıldı (kart eski sezon verisi taşıyabilir).
Geçici klasörün: ${SCR}\l2_mekan_${p}_w\
${ENV}`
}

const MAHALLE = String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\MAHALLE_ROTA_PROMPT.md — onu oku; bu görevde YALNIZ madde 1 ve 2'yi (K44, K45; 16 mahalle) yap.
${PH}
Girdi ${OUT}\_l\girdi\mahalleler.jsonl ; çıktı ${OUT}\_l\mahalleler.jsonl. Her mahallede en az iki somut iddiayı (ulaşım, konut, günlük yaşam) kaynakta ara; kanıtsız etnik/gelir/güvenlik sıralaması P1.
Geçici klasörün: ${SCR}\l2_mahalle_w\
${ENV}`

const ROTA = String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\MAHALLE_ROTA_PROMPT.md — onu oku; bu görevde YALNIZ madde 3 ve 4'ü (K47 12 rota, K20 keşif grupları) yap.
${PH}
Girdiler ${OUT}\_l\girdi\rotalar.jsonl, mekan_ozet.jsonl ; çıktılar ${OUT}\_l\rotalar.jsonl ve ${OUT}\_l\k20_gruplar.json. Her rotada durak sırası, toplam kuş uçuşu km, en uzun adım, rotanın vaat ettiği süreyle uyum, kapalı/tadilattaki durak. Bilinen olgular (kanıt değil): Plaza Nueva şantiye (Ekim 2025 – ~Nisan 2027), Jardines del Prado de San Sebastián zemin yenileme (2026), Museo Arqueológico 2020'den beri kapalı, Costurero de la Reina turizm noktası Nisan 2026'da kapandı.
Geçici klasörün: ${SCR}\l2_rota_w\
${ENV}`

function lisans(nn) {
  return String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\LISANS_PROMPT.md — onu oku ve uygula; L2 farkı: şüpheli küme ve örneklem DEĞİL, girdideki HER kareyi incele.
${PH}
Girdi ${OUT}\_l\girdi\lisans_tam_${nn}.jsonl (~84 kare) ; çıktılar ${OUT}\_l\lisans_${nn}.jsonl (her kare bir satır) ve ${OUT}\_l\lisans_ozet_${nn}.json. Her kare için Commons kaydını aç (hızlı yol: https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo|categories&iiprop=extmetadata|url&format=json&titles=File:<ad>; birden çok dosyayı | ile birleştirip 20'li toplu sorgu yapabilirsin): lisans şablonu, Author/Source, ilk köken (Flickr/Panoramio vb. ise review etiketi), PD/CC0 dayanağı, silme tartışması, Excel lisansıyla uyum (K71, K72). Ek hak (K74): kareyi çağdaş heykel, mural, sergi, afiş ya da gösteri dolduruyorsa İspanya TRLPI md. 35.2 (kalıcı + kamusal alan) dayanağına bak. Foto ajanlarının ek hak işaretleri: huevo-de-colon-01/02, plaza-del-duque-01, teatro-central-03, centro-ceramica-triana-01, basilica-del-gran-poder-03, la-macarena-02.
Geçici klasörün: ${SCR}\l2_lisans_${nn}_w\
${ENV}`
}

function foto(k, sheets) {
  return String.raw`Görev talimatın şu dosyada: ${SKILL}\agents\l1\FOTO_PROMPT.md — onu oku ve uygula (L2: ikinci, bağımsız tam görsel tarama; ilk taramayı Sonnet yaptı, onun dosyalarına BAKMA).
${PH}
Senin paftaların: ${sheets} (${OUT}\temas-sayfalari\ ; slot/key için sheets.json). Çıktı: ${OUT}\_foto\photo-review_${k}.jsonl.
L2 kontrolleri: K59 her kare tek tek; K60 her karede Fotoğraflar.jsonl source_url dosya adı ↔ mekân adı/semti (isim benzerliği tuzağı: "San Vicente" ↔ "San Vicente de Paúl"); K62 kapaklar (Sevilla'yı temsil, yatay kırpma); K65 kalite (bulanık, aşırı karanlık, filigran, düşük çözünürlük); K74 ek hak notu; K105: ${OUT}\_foto\eski_cekim.jsonl listesindeki 2014 öncesi kareler mekânın bugünkü hâlini gösteriyor mu (arşiv/eski hâl ise flag). Emin olamadığın karede tek kareye Read ile bakabilirsin (yol: ${PKG}\ + Fotoğraflar.jsonl file alanı; yalnız oku).
Geçici klasörün: ${SCR}\l2_foto_${k}_w\
${ENV}`
}

function baglanti(nn) {
  return String.raw`Sen Corteqs Sevilla (CITY-107) şehir paketinin bağımsız L2 denetiminde bağlantı denetçisisin. Kartları sen yazmadın. Önce oku: ${SKILL}\agents\l1\ORTAK.md.
${PH}
Kontroller: K51 "200 yanıtı ve soft 404" — etiketin vaat ettiği işlem/bilgi gerçekten hedef sayfada; K53 "ilgili işlem sayfası" — kullanıcı doğrudan doğru işi yapabiliyor ya da açık resmî yönlendirmeyi izleyebiliyor (yalnız anasayfa ya da genel portal = kaldı); K54 "resmî üçüncü taraf bilet/rezervasyon sağlayıcısı" — sağlayıcının yetkisi resmî sitede görülüyor, affiliate/uydurma indirim yok; K55 "harita bağlantısı ve telefon" — harita bağlantısı doğru yeri, telefon doğru kurumu gösteriyor (arama yapma).
Girdi: ${OUT}\_l\girdi\baglanti_tam_${nn}.jsonl (~72 bağlantı; kart_basligi, label, url, url_check: son_URL, sayfa_başlığı, flags). Her bağlantının hedef sayfasını aç (ham metin: curl ya da mcp fetch; kaynak kopyası ${OUT}\kanitlar\snap\index.jsonl içinde olabilir) ve etiket + kart başlığıyla karşılaştır.
Çıktı: ${OUT}\_l\baglanti_${nn}.jsonl — her bağlantı bir satır: {"action_id":"","_row":0,"entry_id":"","label":"","url":"","son_url":"","sayfa_basligi":"","K51":"geçti|kaldı|belirsiz","K53":"geçti|kaldı|belirsiz","K54":"geçti|kaldı|uygulanmaz","K55":"geçti|kaldı|uygulanmaz","gozlem":"kısa","alinti":"sayfadan birebir ≤200","bulgular":[{"check_id":"K51|K53|K54|K55","oncelik":"P0|P1|P2","gozlem":"","kanit_url":"","alinti":""}]}
Süre 35 dakika; yetişmeyen kayıt "belirsiz", gozlem "zaman". Dönüş tek satır JSON: {"parti":"${nn}","baglanti":N,"K51_kaldi":a,"K53_kaldi":b,"K54_kaldi":c,"K55_kaldi":d,"P1":[]}
Geçici klasörün: ${SCR}\l2_baglanti_${nn}_w\
${ENV}`
}

const SAYFA = String.raw`Sen Corteqs Sevilla (CITY-107) şehir paketinin bağımsız L2 denetiminde şehir ve sayfa alanları denetçisisin. Önce oku: ${SKILL}\agents\l1\ORTAK.md.
${PH}
Kontroller: K90 "acil yardım ve eczane" — numara/kurum İspanya/Sevilla'ya uygun, Berlin'in numara ya da bağlantıları (110, 116117, berlin.de) kopyalanmamış; belirsiz acil bilgi yayın engeli (P0). K91 "para birimi, zaman dilimi ve hava durumu" — coğrafi kapsamla uyumlu, hava sayfası Sevilla'yı gösteriyor, anlık sıcaklık kalıcı şehir gerçeği diye yazılmamış. Ayrıca her SayfaAlanları değerinin (hero metinleri, notlar) doğruluğu ve Şehir satırının alanları (koordinat, nüfus vb. iddialar) kaynakla.
Girdi: ${OUT}\_l\girdi\sehir_sayfa.jsonl (Şehir + 23 SayfaAlanları). Acil numara ve eczane için ${OUT}\_dump\Yanıtlar.jsonl, SayfaAlanları.jsonl ve Bağlantılar.jsonl içinde 112, 061, 091, 092, 080, 062, 900, farmacia, eczane, nöbetçi, guardia, urgencias geçen kayıtları Grep ile bul ve resmî kaynakla doğrula.
Çıktı: ${OUT}\_l\sehir_sayfa.jsonl — her anahtar ve her acil/eczane kaydı bir satır: {"anahtar":"","deger_ozet":"","K91":"geçti|kaldı|uygulanmaz","K90":"geçti|kaldı|uygulanmaz","dogruluk":"geçti|kaldı|belirsiz|uygulanmaz","kanit_url":"","alinti":"","bulgular":[{"check_id":"K90|K91|K29","oncelik":"P0|P1|P2","gozlem":"","kanit_url":"","alinti":""}]}
Süre 35 dakika. Dönüş tek satır JSON: {"satir":N,"K90_kaldi":a,"K91_kaldi":b,"P0":[],"P1":[]}
Geçici klasörün: ${SCR}\l2_sayfa_w\
${ENV}`

function kaynak(nn) {
  return String.raw`Sen Corteqs Sevilla (CITY-107) şehir paketinin bağımsız L2 denetiminde kaynak denetçisisin (bütün kaynakların anlamsal hedef kontrolü). Kaynak listesini sen yazmadın. Önce oku: ${SKILL}\agents\l1\ORTAK.md.
${PH}
Girdi: ${OUT}\_l\girdi\kaynak_${nn}.jsonl — 50 kaynak (Kaynaklar satırının alanları + kartlar = bu kaynağı kullanan kayıtlar (sheet, id, title), kart_sayisi, taze_kopya = bugünkü sayfanın metin kopyası yolu, taze_baslik, url_check). Kopya yoksa sayfayı aç.
Her kaynak için: (1) sayfa açılıyor ve kayıttaki başlıkla aynı sayfa mı; (2) sayfa onu kullanan kayıtların konusunu GERÇEKTEN anlatıyor mu (yalnız anasayfa, genel portal, başka şehir/ülke, başka konu → K51 kaldı); (3) resmî/kurum etiketi doğru mu (resmî kurum alanı mı, ticari/blog/arama sonucu mu); (4) güncellik: değişken konu (ücret, süre, kural, saat) için sayfa tarihi/yürürlüğü eski mi (2024 öncesi ve sonrası değişmiş olabilir → K35 notu); (5) kart_sayisi 0 ise "kullanılmayan kaynak".
Çıktı: ${OUT}\_l\kaynak_${nn}.jsonl — her kaynak bir satır: {"source_id":"","_row":0,"url":"","kart_sayisi":0,"acildi":"evet|hayır","konu_uyumu":"tam|kısmi|yok","resmi_dogru":"evet|hayır|uygulanmaz","guncellik":"güncel|eski|tarihsiz","K51":"geçti|kaldı|belirsiz","gozlem":"kısa","alinti":"birebir ≤200","bulgular":[{"check_id":"K51|K30|K35","oncelik":"P1|P2","gozlem":"","kayitlar":["kullanan kayıt id"]}]}
Süre 35 dakika; yetişmeyen kayıt "belirsiz", gozlem "zaman". Dönüş tek satır JSON: {"parti":"${nn}","kaynak":N,"K51_kaldi":a,"P1":[]}
Geçici klasörün: ${SCR}\l2_kaynak_${nn}_w\
${ENV}`
}

const DIGER = String.raw`Sen Corteqs Sevilla (CITY-107) şehir paketinin bağımsız L2 denetiminde kartlar arası denetçisin. Önce oku: ${SKILL}\agents\l1\ORTAK.md.
${PH}
Kontroller: K19 "on iki konunun dolu olması" — Konular sekmesindeki 12 konunun her biri için yanıt kartları o konunun bir göçmenin gerçekten soracağı temel sorularını kapsıyor mu, sığ ya da yalnız yönlendirme kartlarıyla doldurulmuş konu var mı; K28 "anlamsal tekrar ve numaralı doldurma" — aynı soruyu farklı başlıkla soran kart çiftleri, "… 2/3" gibi doldurma kartları, birbirinin kopyası içerik; K18 "kullanılabilir kayıt sayısı" — boş, yalnız yönlendirme ya da kaçamak cevap veren, okura iş yaptırmayan kart sayısı (Berlin hedefi 240 yanıt, 60 sözlük).
Girdi: ${OUT}\_dump\Konular.jsonl, ${OUT}\_dump\Yanıtlar.jsonl (240), ${OUT}\_dump\Sözlük.jsonl (60), ${OUT}\text-quality.json (script sayıları: repeated_sentences 34, short_repeat_groups 1, exact/near/template cluster 0).
Çıktı: ${OUT}\_l\diger.jsonl — her konu için bir K19 satırı {"check_id":"K19","konu":"","kart_sayisi":0,"sonuc":"geçti|kaldı","eksik_temel_sorular":[],"sig_kartlar":[],"gozlem":""}, her tekrar kümesi için bir K28 satırı {"check_id":"K28","kartlar":["entry_id"],"tur":"aynı soru|doldurma|kopya içerik","oncelik":"P1|P2","gozlem":""}, en sonda bir K18 satırı {"check_id":"K18","kullanilamaz":["entry_id | neden"],"kullanilabilir_yanit":N,"kullanilabilir_sozluk":M}.
Süre 40 dakika. Dönüş tek satır JSON: {"K19_kaldi":a,"K28_kume":b,"K18_kullanilamaz":c}
Geçici klasörün: ${SCR}\l2_diger_w\
${ENV}`

function karsiIddia(a, b) {
  const list = b ? `${a} ve ${b}` : a
  const files = b
    ? String.raw`${OUT}\_iddia\parti_${a}.jsonl, kart_${a}.jsonl, parti_${b}.jsonl, kart_${b}.jsonl`
    : String.raw`${OUT}\_iddia\parti_${a}.jsonl, kart_${a}.jsonl`
  const sonnet = (a === '01')
    ? String.raw` Bu iki partinin ilk geçişini Sonnet yaptı: ${OUT}\_sonnet\_iddia\parti_01.jsonl, kart_01.jsonl, parti_02.jsonl, kart_02.jsonl. Aynı claim_id ya da entry_id|K.. için Sonnet ile şimdiki (Opus) kararın FARKLI olduğu her kaydı da incele ve hangisinin doğru olduğuna karar ver (tur "fark").`
    : ''
  const name = b ? `${a}_${b}` : a
  return String.raw`Sen Corteqs Sevilla (CITY-107) bağımsız L2 denetiminde KARŞI DENETÇİSİN: başka bir denetçinin olumsuz kararlarını çürütmeye çalışırsın. Kartları da ilk denetimi de sen yapmadın. Önce oku: ${SKILL}\agents\l1\ORTAK.md ve ${SKILL}\agents\l1\IDDIA_PROMPT.md (kontrol tanımları).
${PH}
Partiler: ${list}. Denetçinin çıktıları (yalnız oku, DEĞİŞTİRME): ${files}. Girdiler: ${OUT}\_iddia\girdi\parti_NN\kartlar.jsonl (kart tam metni), iddialar.jsonl, kaynaklar.jsonl (url → kaynak kopyası file).${sonnet}
İncelenecekler: (1) sonuç "yanlış", "eski" ya da "kaynak_yetersiz" olan her CLAIM satırı; (2) kart dosyasında K25, K26, K31, K32, K40, K48 "kaldı" ya da "belirsiz", ya da K41 "var" olan her kart kararı.
Her biri için denetçinin kararını ÇÜRÜTMEYE çalış. CLAIM için kaynak kopyasında (ya da resmî sayfanın ham metninde) değeri ve bağlamı ara: biçim farkı (9,84/9.84; 1.000/1000), aynı bilgiyi veren başka resmî kaynak, kartın anlattığı aşama/statü için doğru değer, güncel yürürlük. Kart kararı için kartın tam metnini oku: başlıktaki soruya ilk cümle doğrudan cevap veriyor mu (K25), "eksik" denen adım/belge/süre/ücret/kanal kartta gerçekten yok mu ve okur için gerçekten gerekli mi (K26), kurum/kanal Sevilla için doğru mu (K31), dil/vaat sorunu gerçek mi (K32), süre türü karışık mı (K40), çelişki gerçek mi ve kartta açıklanmış mı (K41), sözlük maddesi işe yarar mı (K48).
Karar: "teyit" = denetçi haklı (kaynaktan ya da kart metninden birebir alıntıyla göster); "çürütüldü" = denetçi yanılmış (kanıtla); "belirsiz". Kanıtsız teyit ya da çürütme yazma. Önceliği öner: P0 = kritik yanlış bilgi (yayın engeli); P1 = okuru yanıltan ya da işlemi yapamayacak kadar eksik; P2 = iyileştirme.
Çıktı: ${OUT}\_iddia\karsi_${name}.jsonl — incelenen her kayıt bir satır, her kayıtta ekle: {"tur":"claim|kart|fark","id":"<claim_id> ya da <entry_id>|<K..>","ilk_karar":"","karsi_karar":"teyit|çürütüldü|belirsiz","oncelik_onerisi":"P0|P1|P2|bulgu değil","dogrusu":"(claim teyitse doğru değer)","gerekce":"kısa","kanit_url":"","alinti":"birebir ≤200"}. İncelenecek kayıt yoksa tek satır {"tur":"yok","id":"","karsi_karar":"","gerekce":"incelenecek kayıt yok"}.
Süre 30 dakika; yetişmeyende "belirsiz", gerekce "zaman". Dönüş tek satır JSON: {"partiler":"${list}","incelenen":N,"teyit":a,"çürütüldü":b,"belirsiz":c}
Geçici klasörün: ${SCR}\l2_karsi_iddia_${name}_w\
${ENV}`
}

function karsiL(name, talimat, outputs, inputs) {
  return String.raw`Sen Corteqs Sevilla (CITY-107) bağımsız L2 denetiminde KARŞI DENETÇİSİN: başka denetçilerin olumsuz kararlarını çürütmeye çalışırsın. Paketi de ilk denetimi de sen yapmadın. Önce oku: ${SKILL}\agents\l1\ORTAK.md. Kontrol tanımları: ${talimat}.
${PH}
Denetçilerin çıktısı (yalnız oku, DEĞİŞTİRME): ${outputs}. Girdiler: ${inputs}. Kaynak kopyaları: ${OUT}\kanitlar\snap\index.jsonl (url → text_file, aynı klasörde).
İncelenecekler: "bulgular" listesinde önceliği P0 ya da P1 olan her bulgu ve bir kontrol alanı "kaldı" olan her kayıt (yalnız P2 bulguları olan kayıtlara bakma).
Her biri için kararı ÇÜRÜTMEYE çalış: kaynağı kendin aç, kanıtı birebir alıntıyla göster. Karar: "teyit" / "çürütüldü" / "belirsiz"; önceliği yeniden değerlendir (P0 = kritik yanlış bilgi, yayın engeli; P1 = okuru yanıltan ya da önemli eksik; P2 = bakım).
Çıktı: ${OUT}\_l\karsi_${name}.jsonl — incelenen her kayıt bir satır, her kayıtta ekle: {"kayit":"<entry_id|route_id|photo_id|action_id|source_id|anahtar>","check_id":"","ilk_oncelik":"","karsi_karar":"teyit|çürütüldü|belirsiz","oncelik_onerisi":"P0|P1|P2|bulgu değil","gerekce":"kısa","kanit_url":"","alinti":"birebir ≤200"}. İncelenecek kayıt yoksa tek satır {"kayit":"","karsi_karar":"","gerekce":"incelenecek kayıt yok"}.
Süre 35 dakika; yetişmeyende "belirsiz", gerekce "zaman". Dönüş tek satır JSON: {"ad":"${name}","incelenen":N,"teyit":a,"çürütüldü":b,"belirsiz":c}
Geçici klasörün: ${SCR}\l2_karsi_${name}_w\
${ENV}`
}

const KARSI_FOTO = String.raw`Sen Corteqs Sevilla (CITY-107) bağımsız L2 denetiminde fotoğraf karşı denetçisisin. Önce oku: ${SKILL}\agents\l1\ORTAK.md ve ${SKILL}\agents\l1\FOTO_PROMPT.md (kontrol tanımları).
${PH}
İki bağımsız tarama var (yalnız oku): Sonnet ${OUT}\_foto\photo-review_A.jsonl, photo-review_B.jsonl ve Opus ${OUT}\_foto\photo-review_O1.jsonl, O2, O3. Fotoğraf bilgisi ${OUT}\_dump\Fotoğraflar.jsonl (photo_id, entry_id, role, file, source_url, caption, capture_date); kartlar ${OUT}\_dump\Mekânlar.jsonl, Mahalleler.jsonl. K61 script sonucu ${OUT}\_analiz\k61_sha1.json (teslim özgün dosyası Commons SHA-1'iyle 5/334 aynı; farklılar büyük olasılıkla yeniden boyutlandırma) ve varsa ${OUT}\_analiz\k61_dhash.json (görsel benzerlik).
Görev: iki taramadan herhangi birinde "flag" ya da "reject" olan, ya da iki taramanın farklı karar verdiği her benzersiz kare için kesin karar ver: K60 kare bağlı kaydı GERÇEKTEN gösteriyor mu; K61 teslim dosyası Commons'taki kareyle aynı görüntü mü (k61_dhash'te uzak çıkanlar); K62 kapak; K65 kalite; K105 arşiv/eski hâl; K74 ek hak (yalnız not). Yöntem: Commons kaydını aç (https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo|categories&iiprop=extmetadata&format=json&titles=File:<ad>), açıklama, kategoriler, kamera koordinatı; koordinat varsa karttakiyle mesafeyi hesapla; gerekirse kareye Read ile bak (yol ${PKG}\ + file alanı; yalnız oku), en çok 40 kare.
Özellikle: estadio-benito-villamarin-tur-01/02/03 (kart Benito Villamarín stad turu, kareler La Cartuja stadını gösteriyor olabilir; kart koordinatı La Cartuja ile aynı), guadalquivir-paseo-de-las-delicias-01/02, museo-maritimo-torre-del-oro-01 (Commons adı Cumbre_Torre_del_Oro), casa-de-la-guitarra-01, hospital-de-la-santa-caridad-01, el-arenal-02, triana-02, centro-ceramica-triana-01/02, auditorio-cartuja-sevilla-01/02, san-bernardo-01, nervion-02, kapak-08, iglesia-de-san-luis-de-los-franceses-02, casa-de-la-ciencia-03.
Çıktı: ${OUT}\_foto\karsi_foto.jsonl — her kare bir satır, her karede ekle: {"key":"<photo_id>","entry_id":"","ilk":"A/B/O kararları kısaca","karar":"keep|reject","check_id":"K60|K61|K62|K65|K74|K105|—","oncelik":"P0|P1|P2|—","gorulen":"kısa","commons_kanit":"açıklama/kategori/koordinattan birebir ≤200","mesafe_m":null,"gerekce":""}. "reject" yalnız kanıtla. Süre 45 dakika. Dönüş tek satır JSON: {"incelenen":N,"keep":a,"reject":b,"rejects":["key | neden"]}
Geçici klasörün: ${SCR}\l2_karsi_foto_w\
${ENV}`

const KARSI_ACIK = String.raw`Sen Corteqs Sevilla (CITY-107) bağımsız L2 denetiminde "bugün açık mı" karşı denetçisisin. Önce oku: ${SKILL}\agents\l1\ORTAK.md ve ${AGENTS}\acik-mi.md yalnız §2 ve §4.
${PH}
Doğrulayıcıların çıktıları (yalnız oku; bu dosyalara YAZMA): ${OUT}\_acikmi\parti_01_dogrulama.jsonl … parti_15_dogrulama.jsonl (120 mekân; bir kısmını Sonnet, bir kısmını Opus doğruladı). Kart bilgisi: ${OUT}\_acikmi_girdi\girdi_parti_NN.jsonl ve ${OUT}\_dump\Mekânlar.jsonl.
İncelenecekler: (1) eylemi "kartta belirt" ya da "sil" olan her satır; (2) "ret"+"dokunma" satırlarından kanit_tarihi 2025-01-01'den eski olanlar ya da kanıtı yalnız ziyaretçi yorumu, program duyurusu, planlı ziyaret ilanı ya da fiyat kuralı olanlar; (3) "onay"+"dokunma" (belirsiz kalan) her satır: 2025–2026 tarihli gerçek faaliyet ya da kapanış kanıtı ara.
(1) için olguyu ÇÜRÜTMEYE çalış: kontrol tarihi 2026-10-26 itibarıyla HÂLÂ geçerli mi (şantiye bitti mi, yeniden açıldı mı), kaynak bağımsız ve tarihli mi, kart (subtitle/summary/note/visit_status) olguyu zaten tarihli yazıyor mu. (2) ve (3) için resmî ajanda, basın haberi, belediye bildirimi ara.
Çıktı: ${OUT}\_acikmi_karsi\karsi_acikmi.jsonl (klasörü oluştur; ${OUT}\_acikmi\ altına HİÇBİR ŞEY yazma): {"entry_id":"","parti":"NN","ilk_sonuc":"","ilk_eylem":"","karsi_karar":"teyit|çürütüldü|belirsiz|yeni_kanit","guncel_durum":"2026-10-26 itibarıyla","kartta_var_mi":"evet|hayır|kısmen","kanit_url":"","alinti":"birebir ≤200","kanit_tarihi":"","gerekce":""}.
Süre 60 dakika; yetişmeyende "belirsiz", gerekce "zaman". Dönüş tek satır JSON: {"incelenen":N,"teyit":a,"çürütüldü":b,"belirsiz":c,"yeni_kanit":d}
Geçici klasörün: ${SCR}\l2_karsi_acikmi_w\
${ENV}`

// ---- eşzamanlılık (ana 14 + geriden 4 + bu 3)
const LIMIT = 3
let active = 0
const waiters = []
async function slot(fn) {
  while (active >= LIMIT) { await new Promise(r => waiters.push(r)) }
  active++
  try { return await fn() } finally { active--; const w = waiters.shift(); if (w) w() }
}
const karsi = (p, label) => slot(() => agent(p, { label, phase: 'Karşı denetim', agentType: 'general-purpose' }))
const T = [
  [karsiL('mekan_P1P2', String.raw`${SKILL}\agents\l1\MEKAN_PROMPT.md (K42 gerçek mekân/doğru şube P0, K43 koordinat, K108 kapsam şişirme, K38 müze ücret/indirim, K54 bilet sağlayıcısı, K55 harita/telefon)`, String.raw`${OUT}\_l\mekan_P1.jsonl ve mekan_P2.jsonl`, String.raw`${OUT}\_l\girdi\mekan_P1.jsonl ve mekan_P2.jsonl`), 'karşı:mekan_P1P2'],
  [karsiL('mekan_P3P4', String.raw`${SKILL}\agents\l1\MEKAN_PROMPT.md (K42 gerçek mekân/doğru şube P0, K43 koordinat, K108 kapsam şişirme, K38 müze ücret/indirim, K54 bilet sağlayıcısı, K55 harita/telefon)`, String.raw`${OUT}\_l\mekan_P3.jsonl ve mekan_P4.jsonl`, String.raw`${OUT}\_l\girdi\mekan_P3.jsonl ve mekan_P4.jsonl`), 'karşı:mekan_P3P4'],
  [KARSI_FOTO, 'karşı:foto'],
  [KARSI_ACIK, 'karşı:acikmi'],
  [karsiL('lisans', 'K71 kaynak zincirinin ilk kökeni (P0); K72 PD/CC0 dayanağı (P0); K74 kare içindeki ek haklar', String.raw`${OUT}\_l\lisans_01.jsonl … lisans_04.jsonl`, String.raw`${OUT}\_l\girdi\lisans_tam_NN.jsonl`), 'karşı:lisans'],
  [karsiL('baglanti', 'K51 etiketin vaat ettiği iş hedef sayfada; K53 doğrudan ilgili işlem sayfası; K54 resmî üçüncü taraf bilet sağlayıcısı; K55 harita/telefon; K90 acil numara/eczane (P0); K91 para birimi/zaman dilimi/hava', String.raw`${OUT}\_l\baglanti_01.jsonl … baglanti_08.jsonl ve ${OUT}\_l\sehir_sayfa.jsonl`, String.raw`${OUT}\_l\girdi\baglanti_tam_NN.jsonl ve sehir_sayfa.jsonl`), 'karşı:baglanti'],
  [karsiL('kaynak', 'K51 kaynak sayfası onu kullanan kaydın konusunu gerçekten anlatıyor; K30 kaynak yeterliliği; K35 resmî kaynak ve yürürlük', String.raw`${OUT}\_l\kaynak_01.jsonl … kaynak_10.jsonl`, String.raw`${OUT}\_l\girdi\kaynak_NN.jsonl`), 'karşı:kaynak'],
  [karsiL('mahrota', String.raw`${SKILL}\agents\l1\MAHALLE_ROTA_PROMPT.md (K44 mahalle içeriği, K45 karşılaştırma, K47 rota uygulanabilirliği, K20 keşif grupları)`, String.raw`${OUT}\_l\mahalleler.jsonl, rotalar.jsonl, k20_gruplar.json`, String.raw`${OUT}\_l\girdi\mahalleler.jsonl, rotalar.jsonl, mekan_ozet.jsonl`), 'karşı:mahrota'],
]
const sonuc = await Promise.all(T.map(([p, l]) => karsi(p, l).then(r => { log(l + ' bitti'); return r })))
return { tamam: sonuc.filter(Boolean).length, ozet: sonuc.map(x => (typeof x === 'string' ? x.slice(0, 300) : x)) }
