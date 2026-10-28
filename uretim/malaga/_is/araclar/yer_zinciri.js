export const meta = {
  name: 'malaga-yer-zinciri',
  description: 'Málaga mekân/mahalle/sözlük: yazar → (açık-mı tarama/doğrulama/uygulama) → tam denetim → çürütme → editör → doğrulayıcı',
  phases: [
    { title: 'Açık mı', detail: 'grup başına tarayıcı + şüpheci doğrulayıcı' },
    { title: 'Yazım', detail: '4 mekân dilimi, mahalle, sözlük' },
    { title: 'Uygulama', detail: 'açık-mı kararlarının kartlara uygulanması' },
    { title: 'Denetim', detail: 'tam bağımsız denetim + mekân doğrulama satırları' },
    { title: 'Çürütme', detail: 'ciddi/orta bulguları çürütme' },
    { title: 'Editör', detail: 'denetim turu (görev 1, 2, 6, 7)' },
    { title: 'Doğrulama', detail: 'doğrulayıcı ve gerekirse doğrulama turu' },
  ],
}

const W = 'C:\\temp_private\\corteqs\\0000_newera\\uretim\\malaga'
const D = W + '\\_is\\denetim'
const AG = 'C:\\temp_private\\corteqs\\0000_newera\\.claude\\skills\\city-pack\\agents'
const TK = 'C:\\temp_private\\corteqs\\0000_newera\\corteqs-skills\\toolkit\\scripts'
const PY = 'C:\\temp_private\\corteqs\\0000_newera\\.venv\\Scripts\\python.exe'
const SP = 'C:\\Users\\baris-terzioglu\\AppData\\Local\\Temp\\claude\\c--temp-private-corteqs-0000-newera\\d3157213-2d22-4be1-bfdf-bc65d05e1757\\scratchpad'
const DIGEST = 'C:\\temp_private\\corteqs\\0000_newera\\.claude\\skills\\city-pack\\references\\contract_digest.md'
const ITG = W + '\\_is\\araclar\\ilk_tur_girdi.py'
const N = (args && args.eszamanli) || 4
const TARIH = '2026-10-27'
const BBOX = '36.57,36.87,-4.60,-4.28'

const TUM = [
  { p: 'm1', tip: 'mekan', order: 101, gruplar: ['tarih'], grupAd: 'Tarih ve mimari' },
  { p: 'm2', tip: 'mekan', order: 201, gruplar: ['doga', 'yeme'], grupAd: 'Doğa ve açık hava, Yeme ve içme' },
  { p: 'm3', tip: 'mekan', order: 301, gruplar: ['muzeler', 'sanat'], grupAd: 'Müzeler, Sanat ve sergiler' },
  { p: 'm4', tip: 'mekan', order: 401, gruplar: ['sahne', 'spor', 'cocuk'], grupAd: 'Sahne ve müzik, Spor, Çocuklarla keşif' },
  { p: 'mahalle', tip: 'mahalle', order: 1, gruplar: [] },
  { p: 'sozluk', tip: 'sozluk', order: 1, gruplar: [] },
  { p: 'sayfa', tip: 'sayfa', order: 0, gruplar: [] },
  { p: 'rota', tip: 'rota', order: 1, gruplar: [] },
]
const SECILI = (args && args.parcalar) || ['m1', 'm2', 'm3', 'm4', 'mahalle', 'sozluk']
const DILIMLER = TUM.filter(d => SECILI.includes(d.p))
const ACIK = !(args && args.acik === false)
const GRUPLAR = [
  { k: 'tarih', ad: 'Tarih ve mimari' }, { k: 'doga', ad: 'Doğa ve açık hava' }, { k: 'yeme', ad: 'Yeme ve içme' },
  { k: 'muzeler', ad: 'Müzeler' }, { k: 'sanat', ad: 'Sanat ve sergiler' }, { k: 'sahne', ad: 'Sahne ve müzik' },
  { k: 'spor', ad: 'Spor' }, { k: 'cocuk', ad: 'Çocuklarla keşif' },
]
const DOSYALAR = {
  mekan: p => [`${W}\\_is\\data\\parcalar\\Mekânlar.${p}.jsonl`, `${W}\\_is\\data\\parcalar\\Bağlantılar.${p}.jsonl`, `${W}\\_is\\claims\\${p}.jsonl`],
  mahalle: p => [`${W}\\_is\\data\\parcalar\\Mahalleler.${p}.jsonl`, `${W}\\_is\\data\\parcalar\\Bağlantılar.${p}.jsonl`, `${W}\\_is\\claims\\${p}.jsonl`],
  sozluk: p => [`${W}\\_is\\data\\parcalar\\Sözlük.${p}.jsonl`, `${W}\\_is\\claims\\${p}.jsonl`],
  sayfa: p => [`${W}\\_is\\data\\parcalar\\Şehir.${p}.jsonl`, `${W}\\_is\\data\\parcalar\\SayfaAlanları.${p}.jsonl`, `${W}\\_is\\claims\\${p}.jsonl`],
  rota: p => [`${W}\\_is\\data\\parcalar\\Rotalar.${p}.jsonl`, `${W}\\_is\\claims\\${p}.jsonl`],
}

const KABUKSUZ = 'Kabuk kullanma (Bash ve PowerShell yok): yalnız Read, Glob, Grep ve Write araçları. İnternete çıkma (WebFetch/WebSearch yok). Alt ajan başlatma. JSONL dosyalarını Write aracıyla yaz (UTF-8, satır başına bir JSON nesnesi); her 5 kayıtta bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz (ana döngü 10 dakika büyümeyen dosyayı takılmış sayar).'
const KABUKSUZ_WEB = 'Kabuk kullanma (Bash ve PowerShell yok): yalnız Read, Glob, Grep, Write, WebSearch ve WebFetch. Alt ajan başlatma. JSONL dosyasını Write aracıyla yaz (UTF-8, satır başına bir JSON nesnesi); her 5 mekânda bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz.'
const KABUKLU = `Komut kuralı: cd yok, Bash yok. Komutları PowerShell aracıyla, her çağrıda TEK komut, tam yolla çalıştır (bileşik komut yok). Python için önce .py dosyasını <TMP>'ye yaz, sonra & '${PY}' -I -X utf8 '<dosya>' ile çalıştır; python -c ve heredoc yok. Dosyaları Read/Glob/Grep ile oku. <TMP> klasörünü ilk iş New-Item -ItemType Directory -Force ile oluştur. Alt ajan başlatma. Bir komut 2 dakikadan uzun yanıtsız kalırsa bekleme, notunu open'a yaz ve devam et.`
const ERISIM = 'Erişilemeyen alan adları (deneme): malaga.es, sede.malaga.eu (JS), deportes.malaga.eu (JS), sede.administracionespublicas.gob.es, inclusion.gob.es, mivau.gob.es, huvv.es, aena.es, bibliotecas.malaga.eu, gmu.malaga.eu, visita.malaga.eu, tributosmalaga.eu, cacmalaga.eu.'
const DEGERLER = (tmp) => `Değerler: <city_id>=malaga; <WORK>=${W}; <TK>=${TK}; <PY>=${PY}; <tarih>=${TARIH}; <bbox>=${BBOX}; <TMP>=${tmp}. Hitap: sen (okura 2. tekil; "siz" yok; bir kayıtta biçim karışmaz).`
const MERGE = (tmp) => `& '${PY}' -X utf8 '${TK}\\merge_package.py' '${W}\\_is' --city-id malaga --bbox=${BBOX} --data-out '${tmp}\\birlesik' --out '${tmp}\\birlestir_rapor.json'`

const S_YAZAR = { type: 'object', properties: { part: { type: 'string' }, rows: { type: 'integer' }, actions: { type: 'integer' }, claims: { type: 'integer' }, new_sources: { type: 'integer' }, own_issues: { type: 'integer' }, girdi_hazir: { type: 'boolean' }, gaps: { type: 'array', items: { type: 'string' } }, open: { type: 'array', items: { type: 'string' } } }, required: ['part', 'rows', 'claims', 'new_sources', 'own_issues', 'girdi_hazir', 'gaps', 'open'] }
const S_TARAMA = { type: 'object', properties: { grup: { type: 'string' }, count: { type: 'integer' }, flagged: { type: 'array', items: { type: 'string' } }, zayif: { type: 'array', items: { type: 'string' } }, notes: { type: 'array', items: { type: 'string' } } }, required: ['grup', 'count', 'flagged', 'zayif', 'notes'] }
const S_ADOG = { type: 'object', properties: { grup: { type: 'string' }, count: { type: 'integer' }, sil: { type: 'integer' }, kartta_belirt: { type: 'integer' }, flagged: { type: 'array', items: { type: 'string' } }, notes: { type: 'array', items: { type: 'string' } } }, required: ['grup', 'count', 'sil', 'kartta_belirt', 'flagged', 'notes'] }
const S_DENETIM = { type: 'object', properties: { part: { type: 'string' }, cards: { type: 'integer' }, claims: { type: 'integer' }, dogru: { type: 'integer' }, duzelt_kart: { type: 'integer' }, ciddi: { type: 'integer' }, orta: { type: 'integer' }, hafif: { type: 'integer' }, mekan_kaldi: { type: 'integer' } }, required: ['part', 'cards', 'claims', 'dogru', 'duzelt_kart', 'ciddi', 'orta', 'hafif'] }
const S_TEYIT = { type: 'object', properties: { part: { type: 'string' }, kontrol: { type: 'integer' }, gercek: { type: 'integer' }, kismen: { type: 'integer' }, yersiz: { type: 'integer' } }, required: ['part', 'kontrol', 'gercek', 'kismen', 'yersiz'] }
const S_EDITOR = { type: 'object', properties: { part: { type: 'string' }, bulgu_toplam: { type: 'integer' }, uygulanan: { type: 'integer' }, reddedilen: { type: 'integer' }, degisen_kayit: { type: 'integer' }, silinen: { type: 'array', items: { type: 'string' } }, yeni_kaynak: { type: 'integer' }, script_kontrol_hata: { type: 'integer' }, open: { type: 'array', items: { type: 'string' } } }, required: ['part', 'bulgu_toplam', 'uygulanan', 'reddedilen', 'degisen_kayit', 'script_kontrol_hata', 'open'] }
const S_DOGRULAMA = { type: 'object', properties: { part: { type: 'string' }, satir: { type: 'integer' }, dogru: { type: 'integer' }, hatali_duzeltme: { type: 'integer' }, eksik_kalan: { type: 'integer' }, sorunlu_ciddi_orta: { type: 'integer' } }, required: ['part', 'satir', 'dogru', 'hatali_duzeltme', 'eksik_kalan', 'sorunlu_ciddi_orta'] }

// --- yazar istemleri ---
function mekanYazar(d, tmp) {
  return `Corteqs Málaga (CITY-075) paketinde MEKÂN YAZARISIN. <gorev> = ${d.p} (gruplar: ${d.grupAd}).

Önce Read ile oku (bu sırayla): ${AG}\\ortak-kurallar.md, ${AG}\\yer-yazari.md (Mekânlar ve "Kaynak (yer yazarına özgü)" bölümleri), ${AG}\\mekan-yazari.md; anahtarlar için ${DIGEST} §2 Mekânlar ve Bağlantılar. Yol ve biçimde ortak-kurallar.md ile yer-yazari.md esastır.
${DEGERLER(tmp)}

Mekân planı: ${W}\\_is\\mekan\\plan_${d.p}.jsonl — satır: name, group, qid, lat, lon, district, setting, official_url, slug, entry_id, source_id, commons_category, note. slug, entry_id, group, district, setting, lat/lon AYNEN kullanılır (lat boşsa latitude ve longitude ""). Plandaki HER mekân için bir kayıt; kapanmış ya da taşınmış görünen mekânı yazma, gaps'e yaz.
Kaynak: her mekânın source_ids'i plandaki source_id (metin: ${W}\\_is\\kaynak_dizini.jsonl → text_file). Saat, ücret, indirim, ücretsiz gün YALNIZ mekânın kendi resmî sayfasından; sayfada yoksa yazma (gaps). Gerekirse mekânın kendi bilet/ziyaret sayfasını add_sources ile ekleyebilirsin (ortak kurallar §4; klasör snap_${d.p}-yazar<sira>, --topic kesif) — bu dilimde EN ÇOK 2 yeni kaynak (Kaynaklar sayfası 500 sınırına yakın); kayıt başına en çok 2 source_ids. ${ERISIM}

Yazacağın dosyalar (yalnız bunlar): ${DOSYALAR.mekan(d.p).join(', ')}.
- order: ${d.order}'den başlayarak artan; featured en çok 2 Evet.
- visit_status her zaman ""; collection "Hayır"; media_key ""; editorial_status "Taslak"; reviewed_on ${TARIH}.
- title: resmî adı özgün yazımıyla; subtitle ne olduğu ve nerede; summary o yere özgü 2–4 cümle (ne, adres/semt, açık günler-saatler, ücret, kimlere uygun — kaynakta ne varsa); location kaynaktaki açık adres birebir.
- note: yalnız o yere ait pratik bilgi, her mekânda farklı; plandaki note "genel ziyaret yok, etkinlik günleri" diyorsa bunu note'ta tek cümleyle söyle. "Ziyaret öncesi kontrol et" gibi kalıp yok.
- Bağlantılar: her mekâna 1–2 satır; etiket hedefle aynı ("Ziyaret bilgisi" saat/adres sayfası, "Bilet al" yalnız bilet satan sayfa, "Rezervasyon yap" genel rezervasyon sayfası); url kaynak dizinindeki adresle birebir.
- Defter (${W}\\_is\\claims\\${d.p}.jsonl): her kayıtta adres (field=location), saat, ücret, kural için birebir alıntılı satır; entry_id sahipli.

Bitirmeden:
1. Ortak kurallar §8: ${MERGE(tmp)} — kendi parçanı ilgilendiren bulgu 0 olmalı (kendi kimliklerin birleşik çıktıda olmalı).
2. Denetim girdisi: & '${PY}' -I -X utf8 '${ITG}' '${W}\\_is' ${d.p}  → çıkış 0 ise girdi_hazir = true.

${KABUKLU}
Bütçe: 70 dakika / 220 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}", rows, actions, claims, new_sources, own_issues, girdi_hazir, gaps, open} — sayıları dosyalardan say.`
}

function mahalleYazar(d, tmp) {
  return `Corteqs Málaga (CITY-075) paketinde MAHALLE YAZARISIN. <gorev> = mahalle.

Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\yer-yazari.md (Mahalleler ve Kaynak bölümleri), ${AG}\\mekan-yazari.md; anahtarlar ${DIGEST} §2 Mahalleler ve Bağlantılar.
${DEGERLER(tmp)}

Görev: 16 mahalle (en az 12). Málaga'nın resmî mahalle listesi yoksa mahalle = tanınan semt (barrio), ana cadde ya da yapı çevresi; şehri birkaç büyük ilçeye bölüp sayıyı doldurma, farklı ilçelerden adlandırılabilir semtler seç (merkez, sahil, doğu, batı, kuzey, üniversite, çevre semtler). Commons'ta fotoğrafı olan semtleri öne al: ${W}\\_is\\mekan\\wikidata_aday.jsonl içinde types "neighborhood" ya da "barrio" olup has_image true olanlara bak (Grep).
- Her mahalle için en az 2 kaynak (belediye ilçe/Junta Municipal de Distrito sayfası, EMT ya da metro hat sayfası, belediye park/plaj sayfası, SAS sağlık merkezi listesi gibi resmî sayfalar). Önce ${W}\\_is\\kaynak_dizini.jsonl'deki mevcut kaynakları kullan; yeni kaynak add_sources ile (klasör snap_mahalle-yazar<sira>, --topic ev), bu görevde EN ÇOK 16 yeni kaynak. Ticari site, emlak sitesi, turizm portalı yok. ${ERISIM}
- compare_json BÜTÜN mahallelerde tam bu 4 başlıkla: {"Konum":"…","Ulaşım":"…","Yeşil alan ve sahil":"…","Gündelik hizmetler":"…"}; her değer kaynaklı (defterde field = compare.<Başlık>). Güvenlik, gelir, etnik köken genellemesi, "en iyi mahalle", kira tahmini yok.
- slug mahallenin adından (ör. el-palo), entry_id malaga:<slug>; Yanıtlar ve plan slug/başlıklarıyla çakışmasın (${W}\\_is\\mekan\\plan.jsonl ve data\\parcalar\\Yanıtlar.*.jsonl). order 1..16; featured en çok 2 Evet; media_key "".
- Her mahalleye en az 1 Bağlantılar satırı (harita tek bağlantı olamaz).
Yazacağın dosyalar: ${DOSYALAR.mahalle('mahalle').join(', ')}.

Bitirmeden: 1) ${MERGE(tmp)}  2) & '${PY}' -I -X utf8 '${ITG}' '${W}\\_is' mahalle  → çıkış 0 ise girdi_hazir = true.

${KABUKLU}
Bütçe: 75 dakika / 230 araç çağrısı.
Dönüş (StructuredOutput): {part:"mahalle", rows, actions, claims, new_sources, own_issues, girdi_hazir, gaps, open}.`
}

function sozlukYazar(d, tmp) {
  return `Corteqs Málaga (CITY-075) paketinde SÖZLÜK YAZARISIN. <gorev> = sozluk.

Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\yer-yazari.md (Sözlük bölümü); anahtarlar ${DIGEST} §2 Sözlük.
${DEGERLER(tmp)}

Görev: 60 terim (en az 48). Okuyucunun Málaga'da konut, kayıt, oturum, vergi, ulaşım, sağlık, eğitim, iş ve günlük yaşamda karşılaşacağı gerçek yerel terimler, yerel yazımla (ör. empadronamiento, cita previa, TIE, NIE, OMAC, IBI, plusvalía, EMASA, punto limpio, centro de salud, Consorcio de Transportes, escolarización …). Kartlarda geçen terimleri öncele: ${W}\\_is\\data\\parcalar\\Yanıtlar.*.jsonl (Grep). Genel sözlük kelimesi yok; aynı terimin iki yazılışı tek madde.
- term_id malaga:term:001 … sırayla; order 1..N; definition 1–3 cümle Türkçe (ne olduğu, okuyucunun nerede karşılaşacağı); source_ids boş olamaz.
- Kaynak: YALNIZ ${W}\\_is\\kaynak_dizini.jsonl'deki mevcut kaynaklar (text_file); yeni kaynak EKLEME (Kaynaklar sayfası 500 sınırına yakın). Terimi destekleyen kaynak yoksa o terimi yazma.
- Her terimin en az bir defter satırı: field = definition, claim = tanımın ana cümlesi, quote = kaynakta terimin ne olduğunu söyleyen birebir cümle; tanımdaki her kural ve sayı ayrıca defterde (term_id sahipli).
Yazacağın dosyalar: ${DOSYALAR.sozluk('sozluk').join(', ')}.

Bitirmeden: 1) ${MERGE(tmp)}  2) & '${PY}' -I -X utf8 '${ITG}' '${W}\\_is' sozluk  → çıkış 0 ise girdi_hazir = true.

${KABUKLU}
Bütçe: 60 dakika / 200 araç çağrısı.
Dönüş (StructuredOutput): {part:"sozluk", rows, actions:0, claims, new_sources:0, own_issues, girdi_hazir, gaps, open}.`
}

function sayfaYazar(d, tmp) {
  return `Corteqs Málaga (CITY-075) paketinde SAYFA YAZARISIN: Şehir satırı ve SayfaAlanları. <gorev> = sayfa.

Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\yer-yazari.md (SayfaAlanları ve Şehir bölümleri — 23 anahtar tablosu ve Şehir 33 anahtarı burada), ${AG}\\..\\references\\sitede_gorunum.md (varsa; advice_entry açıklaması); anahtarlar ${DIGEST} §2 Şehir ve SayfaAlanları.
${DEGERLER(tmp)}

Şehir satırı: şablon dökümü ${W}\\_is\\sablon_dump\\Şehir.jsonl — dolu alanları AYNEN al (_row hariç), 33 anahtarın tamamıyla yer-yazari.md'deki sırayla yeniden kur. Boş zorunlu alanlar: title (≤160) ve intro (≤350) Málaga'ya özgü Türkçe; currency "EUR", currency_symbol "€", currency_label "Euro"; language "İspanyolca"; timezone "Europe/Madrid"; forecast_url Málaga için AEMET belediye tahmin sayfası, provider_url "https://www.aemet.es", forecast_label Türkçe bağlantı metni (forecast_url'i add_sources ile kaynak yap); hero_photo_id "" (fotoğraf fazı bağlar); editorial_notes ""; editorial_status "Taslak"; reviewed_on ${TARIH}. latitude, longitude, aliases şablondaysa AYNEN (değiştirme). title, intro, tagline aynı metni tekrarlamaz.
SayfaAlanları: 23 anahtar, her biri bir kez (yer-yazari.md tablosu). entry, advice_entry, facts[].entry, quick_links[].entry, timeline[].entry değerleri bu şehrin VAR OLAN kayıt slug'ları (öneksiz) — ${W}\\_is\\data\\parcalar\\Yanıtlar.*.jsonl, Mekânlar.*.jsonl, Mahalleler.*.jsonl içinden; Grep ile doğrula. advice_entry = yeni gelenin ilk başvuracağı DANIŞMA hizmeti kartı (bilgi kartı değil). facts: her value o slug'ın kartında da yazılı ve defterde. emergency: numaralar yalnız resmî kaynaktan (günlük konusundaki acil numaralar kartının kaynakları). emergency_url ve pharmacy_url resmî https sayfa ve kaynak dizininde (nöbetçi eczane için Málaga Eczacılar Odası'nın — Colegio Oficial de Farmacéuticos de Málaga, kamu hukuku kurumu — nöbetçi eczane sayfası add_sources ile eklenebilir). Berlin'in ya da başka şehrin metni, numarası kopyalanmaz.
Kaynak: önce ${W}\\_is\\kaynak_dizini.jsonl'deki mevcut kaynaklar; yeni kaynak add_sources ile (klasör snap_sayfa-yazar<sira>, --topic gunluk), EN ÇOK 3 (Kaynaklar sayfası 500 sınırına yakın).
Defter (${W}\\_is\\claims\\sayfa.jsonl): SayfaAlanları değerlerindeki her sayı, süre, numara için field_id = malaga:field:<key> sahipli satır (field = value); Şehir intro/tagline'daki olgular için entry_id = malaga sahipli satır.
Yazacağın dosyalar: ${DOSYALAR.sayfa('sayfa').join(', ')}.

Bitirmeden: ${MERGE(tmp)} — Şehir ve SayfaAlanları bulgusu 0 olmalı. girdi_hazir = true yaz (bu parçanın denetim girdisi kayıt dosyalarıdır).

${KABUKLU}
Bütçe: 60 dakika / 200 araç çağrısı.
Dönüş (StructuredOutput): {part:"sayfa", rows, actions:0, claims, new_sources, own_issues, girdi_hazir, gaps, open}.`
}

function rotaYazar(d, tmp) {
  return `Corteqs Málaga (CITY-075) paketinde ROTA YAZARISIN. <gorev> = rota.

Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\yer-yazari.md (Rotalar bölümü; gün ve saat planı şart), ${AG}\\mekan-yazari.md; anahtarlar ${DIGEST} §2 Rotalar.
${DEGERLER(tmp)}

Görev: 12 rota (en az 9), her biri 2–8 FARKLI gerçek mekân durağı (stop_entry_ids: ${W}\\_is\\data\\parcalar\\Mekânlar.m1..m4.jsonl içindeki entry_id'ler; mekânın note'unda kapanış/tadilat varsa durak yapma). Çeşitlilik: ilk gün tanışma, tarih, sanat ve müze, açık hava ve sahil, aile, yeme-içme ve çarşı, spor, yağmurlu gün, ücretsiz keşif; farklı semtler.
- Ardışık duraklar arası kuş uçuşu mesafeyi koordinatlardan hesapla (haversine, betik <TMP>'de); yürüyüş rotasında ardışık iki durak 3 km'den yakın. Notta "kuş uçuşu ~X km" yaz ("X km yürüyüş" değil; yürüyüş mesafesini ana döngü sonra OpenStreetMap ile ölçüp ekletecek).
- Gün ve saat planı: her rota bir gün ve başlangıç saati önerir; her durağın o gün o saatte açık olduğunu durak kaydının saatlerinden göster; açık değilse sırayı değiştir ya da "dışarıdan görülür" de. Plan dosyası: ${W}\\_is\\rota_plan.jsonl — durak başına {"route_id","durak","varis_saati","acik_mi","dayanak"} (dayanak = durak kaydının saat alanı/alıntı).
- note'taki her bilgi durak kayıtlarındaki ve kaynaklardaki bilgiyle; defterde route_id sahipli (field = note). source_ids = nottaki bilgilerin kaynakları (durak kayıtlarının kaynakları); boş olamaz. Yeni kaynak EKLEME.
Yazacağın dosyalar: ${DOSYALAR.rota('rota').join(', ')} ve ${W}\\_is\\rota_plan.jsonl.

Bitirmeden: ${MERGE(tmp)} — Rotalar bulgusu 0.

${KABUKLU}
Bütçe: 60 dakika / 200 araç çağrısı.
Dönüş (StructuredOutput): {part:"rota", rows, actions:0, claims, new_sources:0, own_issues, girdi_hazir:false, gaps, open}.`
}

// --- açık mı ---
function tarayici(g) {
  return `Corteqs Málaga paketinde "BUGÜN AÇIK MI" TARAYICISISIN. Grup: ${g.ad} (<grup> = ${g.k}).

Önce Read ile oku: ${AG}\\acik-mi.md (§1–§3 senin görevin; §2 kanıt kuralları şart).
Değerler: <city_id>=malaga; <sehir>=Málaga; <dil>=İspanyolca (kapanış sözcükleri: cerrado, cierre definitivo, cierra, concurso de acreedores, traslado, se traslada, obras, reforma, cerrado temporalmente, reapertura, nueva ubicación); <tarih>=${TARIH} (kontrol yılı 2026; açık kanıtı 2025–2026 tarihli olmalı).
Mekân listesi: ${W}\\_is\\mekan\\plan.jsonl içinde group = "${g.ad}" olan satırlar (entry_id, name, official_url, note). Gruptaki HER mekân için bir satır.
Çıktı: ${W}\\_is\\acik_mi\\${g.k}.jsonl — satır biçimi ve anahtar sırası acik-mi.md §3'teki gibi (title = plandaki name).

${KABUKSUZ_WEB}
Bütçe: 30 dakika; mekân başına en çok 3 web araması ve 1–2 sayfa. Yetişmeyen mekân "belirsiz", not = "zaman".
Dönüş (StructuredOutput): {grup:"${g.k}", count, flagged:["entry_id | durum | kanıt + url" — açık dışındaki her satır], zayif:["entry_id" — açık dediğin ama kanıtı tarihsiz, footer ya da sitenin varlığı olan satırlar], notes}.`
}

function acikDogrulayici(g, t) {
  return `Corteqs Málaga paketinde "BUGÜN AÇIK MI" ŞÜPHECİ DOĞRULAYICISISIN. Taramayı sen yapmadın. Grup: ${g.ad} (<grup> = ${g.k}).

Önce Read ile oku: ${AG}\\acik-mi.md (§2 kanıt kuralları ve §4 senin görevin).
Değerler: <sehir>=Málaga; <dil>=İspanyolca; <tarih>=${TARIH}.
Girdi: ${W}\\_is\\acik_mi\\${g.k}.jsonl. İşaretli satırlar (tarayıcının "açık" dışı kararları): ${JSON.stringify(t.flagged)}. Ayrıca kanıtı zayıf "açık" satırlar: ${JSON.stringify(t.zayif)} — bunlarda tarihli açık kanıtı bul; bulamazsan ve kapanış kanıtı da yoksa sonuc "onay" değil, tarama_durum "açık" için "ret" + "dokunma" yaz ve en iyi bulduğun tarihli izi kanit_alinti'ye koy.
Çıktı: ${W}\\_is\\acik_mi\\${g.k}_dogrulama.jsonl — satır biçimi ve anahtar sırası acik-mi.md §4'teki gibi; işaretli ve zayıf her mekân için bir satır.

${KABUKSUZ_WEB}
Bütçe: 30 dakika; mekân başına en çok 4 arama.
Dönüş (StructuredOutput): {grup:"${g.k}", count, sil, kartta_belirt, flagged:["entry_id | eylem | olgu + url"], notes}.`
}

function uygulamaEditor(d, tmp, gruplar) {
  return `Corteqs Málaga paketinde "AÇIK MI" UYGULAMA EDİTÖRÜSÜN. Parça (<gorev>): ${d.p}.

Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\editor.md, ${AG}\\yer-yazari.md (Mekânlar), ${AG}\\acik-mi.md §5 ve §6. Açık görevler: editor.md 2, 6, 7 ve acik-mi.md §5. §5'in silmesine editor.md'nin "Görev 4–5 açılmadıysa kayıt silme" ve "kapanmış mekânı silme" kuralları uygulanmaz.
${DEGERLER(tmp)}
Girdi: ${gruplar.map(k => `${W}\\_is\\acik_mi\\${k}_dogrulama.jsonl`).join(', ')} — yalnız eylemi "sil" ya da "kartta belirt" olan satırlar; yalnız senin parçandaki mekânlar (${W}\\_is\\data\\parcalar\\Mekânlar.${d.p}.jsonl).
Dosyalar: ${DOSYALAR.mekan(d.p).join(', ')}. Değişiklik kaydı: ${D}\\acikmi_${d.p}_degisiklik.jsonl (editor.md biçimi; bulgu_claim_id = acik_mi:<grup>:<slug>). "kartta belirt" için kanıt adresini add_sources ile ekle (klasör snap_${d.p}-editor<sira>, --topic kesif) ve note'a tarihli tek cümle yaz (acik-mi.md §5 biçimi); visit_status boş kalır. "sil" için gerekce'de ikinci kaynağın tam adresi yoksa silme, open'a yaz.

Bitirmeden: 1) ${MERGE(tmp)}  2) & '${PY}' -X utf8 '${TK}\\acik_mi.py' '${W}\\_is\\acik_mi' --mekanlar '${W}\\_is\\data\\parcalar' --kaynaklar '${W}\\_is\\kaynak_dizini.jsonl' --out '${tmp}\\acik_mi_rapor.json' — yalnız kendi mekânlarına ait bulguları kapat.  3) Denetim girdisini yenile: & '${PY}' -I -X utf8 '${ITG}' '${W}\\_is' ${d.p}

${KABUKLU}
Bütçe: 40 dakika / 140 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}-acikmi", bulgu_toplam, uygulanan, reddedilen, degisen_kayit, silinen:[entry_id], yeni_kaynak, script_kontrol_hata, open}.`
}

// --- denetim zinciri ---
function ozelKontrol(tip) {
  if (tip === 'mekan') return `Mekân kayıtlarında ayrıca bulgu: adres, saat, ücret, indirim mekânın KENDİ resmî sayfasına dayanmıyorsa (turizm portalı tek dayanaksa); note kalıp ya da mekânı tanıtmıyor (S08) ya da başka mekânla aynı; visit_status dolu; aynı adresi/bileti paylaşan alt nesne ayrı kayıt (K108); bağlantı etiketi hedefle uyuşmuyor ("Bilet al" bilet satmayan sayfaya); kaynaktaki ad başka yapıyı anlatıyor (benzer ad); yılsız ya da geçmiş tarihli istisna; okura "siz" hitabı.
Ek çıktı (acik-mi değil, iddia-denetcisi.md madde 9): ${D}\\<PARCA>_mekan-dogrulama.jsonl — kayıt başına bir satır {"entry_id","kimlik","adres","koordinat","ziyaret","sonuc","not"}; "kaldı" satırının kaydı "düzelt" kararı alır.`
  if (tip === 'mahalle') return `Mahalle kayıtlarında ayrıca bulgu: compare_json değeri kaynakta yok ya da genelleme (güvenlik, gelir, "en iyi"); location kaynaksız; kayıt 2 kaynaktan az; semt adı ve sınırı kaynakta geçmiyor; okura "siz" hitabı.
Ek çıktı (iddia-denetcisi.md madde 9): ${D}\\<PARCA>_mekan-dogrulama.jsonl — mahalle başına bir satır (adres: "tutar", notta "mahalle").`
  if (tip === 'sayfa') return 'Şehir ve SayfaAlanları kayıtlarında ayrıca bulgu: entry/advice_entry/facts/quick_links/timeline slug\'ı pakette yok (Yanıtlar/Mekânlar/Mahalleler parçalarında Grep ile bak); facts değeri bağlı kartta yazılı değil ya da defterde yok; acil numara resmî kaynakta yok; advice_entry danışma hizmeti değil (bilgi kartı); timeline yasal süre gibi sunulmuş; metin başka şehirden kopya ya da Málaga\'ya özgü değil; hero_photo_id dolu; şablondaki alan değiştirilmiş; okura "siz" hitabı.'
  if (tip === 'rota') return 'Rota kayıtlarında ayrıca bulgu: durak Mekânlar\'da yok ya da kapalı/tadilatta; durak o gün o saatte kapalı (rota_plan.jsonl ve durak kaydının saatleri); ardışık duraklar uzak; "X km yürüyüş" yazılmış ama ölçüm yok; süre tag\'e sığmıyor; note\'ta kaynaksız bilgi.'
  return 'Sözlük kayıtlarında ayrıca bulgu: terim gerçek yerel terim değil ya da yazımı yanlış; tanım kaynakla çelişiyor, daraltıyor ya da genişletiyor; tanımda kaynakta olmayan kural/sayı; terimin defter satırı yok.'
}

function girdiTanimi(d, ad) {
  if (d.tip === 'sayfa') return `Girdi (bu parçanın denetim dosyası yok; kayıtları doğrudan oku): ${DOSYALAR.sayfa(d.p).join(', ')}; kaynak metinleri ${W}\\_is\\kaynak_dizini.jsonl → text_file; slug kontrolü için ${W}\\_is\\data\\parcalar\\ (Grep). Yalnız bunları oku.`
  return `Girdi: ${D}\\${ad}_kartlar.txt (okunur hâli; aynı içerik ${ad}_kartlar.jsonl): her kayıt + kaynaklar (text_file) + iddialar (yazar defteri) + butonlar${d.tip === 'rota' ? ' + plan ve bacaklar' : ''}. Kaynak metinleri text_file (Read). Yalnız bu dosyaları oku; metin yetmiyorsa kaynak_yetersiz.`
}

function denetci(d, ad) {
  return `Corteqs Málaga (CITY-075) paketinde BAĞIMSIZ DENETÇİSİN. Parça: ${ad} (${d.tip}). Kayıtları sen yazmadın.

Önce Read ile oku: ${AG}\\iddia-denetcisi.md — yöntem maddeleri 1–6 ve 9 geçerli; "Çıktı" ve "Dönüş" bölümleri ESKİ, geçersiz.
${girdiTanimi(d, ad)}
Kayıtların HEPSİ: her kaydın BÜTÜN defter satırlarını ve kayıt metnini kaynak metniyle anlamıyla karşılaştır (kime uygulanır, koşul, istisna, sayı-birim-dönem, kaynakta olmayan çıkarım). ${ozelKontrol(d.tip).replace('<PARCA>', ad)}

Çıktı:
1. ${D}\\${ad}_iddia.jsonl — doğru olmayan HER iddia + kayıt başına 2–4 doğru iddia; satır {"claim_id","entry_id","iddia","ülke_şehir_statü","dönem","resmî_URL","kaynak_bölümü","yayın_yürürlük_tarihleri","kontrol_tarihi":"${TARIH}","hesap_varsa_girdiler","sonuç":"doğru|yanlış|eksik_koşul|kaynak_yetersiz|çelişkili_kaynak","ağırlık":"ciddi|orta|hafif|-","belirsizlik","alıntı":"birebir, ≤200 karakter","doğrusu"}. entry_id: kaydın kimliği (sözlükte term_id değeri). Defterde olmayan bilgi için claim_id "<kimlik-son-kısım>-K<n>".
2. ${D}\\${ad}_karar.jsonl — kayıt başına {"entry_id","karar":"temiz|düzelt","en_agir","ozet","denetlenen_iddia","dogru_ids":[]}.
Tire'li başka tur dosyalarına ve başka dosyaya yazma; kayıtları değiştirme.

${KABUKSUZ}
Bütçe: 55 dakika / 170 araç çağrısı.
Dönüş (StructuredOutput): {part:"${ad}", cards, claims, dogru, duzelt_kart, ciddi, orta, hafif, mekan_kaldi} — sayıları dosyalarından say (mekan_kaldi: madde 9 dosyasında sonuc "kaldı" satır sayısı; sözlükte 0).`
}

function teyitci(d) {
  return `Corteqs Málaga paketinde ŞÜPHECİ İKİNCİ GÖZSÜN. Parça: ${d.p}. Bağımsız bir denetçi bulgular yazdı. Görevin: "ciddi" ya da "orta" ağırlıklı, sonucu "doğru" olmayan HER bulguyu kaynak metniyle ÇÜRÜTMEYE çalışmak.
Girdiler: ${D}\\${d.p}_iddia.jsonl, ${D}\\${d.p}_kartlar.txt (kayıtlar, defter, kaynakların text_file yolları), kaynak metinleri. Yalnız bunları oku.
Karar: "gercek" (kaynak bulguyu doğruluyor), "kismen" (bulgu kısmen doğru; doğrusunu yaz), "yersiz" (kaynak kaydı destekliyor; destekleyen birebir alıntı). Emin değilsen "kismen".
Çıktı: ${D}\\${d.p}_teyit.jsonl — bulgu başına {"claim_id","entry_id","teyit":"gercek|kismen|yersiz","gerekce","alinti","dogrusu"}. Başka dosyaya yazma.

${KABUKSUZ}
Bütçe: 30 dakika / 100 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}", kontrol, gercek, kismen, yersiz}.`
}

function editorDenetim(d, tmp) {
  const yer = d.tip === 'sozluk' ? '' : `, ${AG}\\yer-yazari.md`
  return `Corteqs Málaga paketinde EDİTÖRSÜN — denetim turu. Parça (<gorev>): ${d.p}. Kayıtları sen yazmadın, denetimi de sen yapmadın.
Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\editor.md${yer}. Açık görevler: 1, 2, 6, 7. Kayıt ekleme/silme yok (kapanmış görünen mekânı silme, open'a yaz).
${DEGERLER(tmp)}
Dosyalar (yalnız bunlar): ${DOSYALAR[d.tip](d.p).join(', ')}. Değişiklik kaydı: ${D}\\${d.p}_degisiklik.jsonl.
Bulgular: ${D}\\${d.p}_iddia.jsonl, ${D}\\${d.p}_karar.jsonl${['mekan', 'mahalle'].includes(d.tip) ? `, ${D}\\${d.p}_mekan-dogrulama.jsonl ("kaldı" satırlarının tutmayan öğeleri de bulgudur; bulgu_claim_id = "mekan-dogrulama:<slug>")` : ''}. Çürütme: ${D}\\${d.p}_teyit.jsonl (varsa) — "yersiz" bulguyu uygulama, reddedildi diye kaydet; "kismen"de teyitteki dogrusu'na göre uygula.
Yeni kaynak gerekirse add_sources (rol editor, snap_${d.p}-editor<sira>, Test-Path ile boş sıra, --topic ${d.tip === 'mahalle' ? 'ev' : d.tip === 'sayfa' ? 'gunluk' : 'kesif'}); bu parçada EN ÇOK 3 yeni kaynak (Kaynaklar sayfası 500 sınırına yakın); bulamazsan bilgiyi çıkar ya da kaynağın dediğine daralt. ${ERISIM}
Bitirmeden: ${MERGE(tmp)} — kendi parçanı ilgilendiren bulgu 0. "doğru" olmayan her bulgunun değişiklik kaydında satırı var mı, say.

${KABUKLU}
Bütçe: 55 dakika / 180 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}", bulgu_toplam, uygulanan, reddedilen, degisen_kayit, silinen:[], yeni_kaynak, script_kontrol_hata, open}.`
}

function dogrulayici(d) {
  return `Corteqs Málaga paketinde BAĞIMSIZ DOĞRULAYICISIN (yazar, denetçi, editör değilsin). Parça: ${d.p}.
Görev: editörün her değişikliğini kaynak metniyle karşılaştır — kaynakla tutarlı mı, bulguyu kapatıyor mu, yeni yanlış/genelleme/kaynaksız bilgi, "siz" hitabı, iş bırakan cümle, iç süreç notu eklemiş mi. Sonra değişiklik kaydı OLMAYAN bulguları ara ("doğru" olmayan her bulgu ya da "düzelt" kararlı her kayıt için en az bir satır olmalı; yoksa ve kayıt hâlâ hatalıysa eksik_kalan).
Girdiler: ${D}\\${d.p}_degisiklik.jsonl, ${D}\\${d.p}_iddia.jsonl, ${D}\\${d.p}_karar.jsonl, ${D}\\${d.p}_teyit.jsonl (varsa)${['mekan', 'mahalle'].includes(d.tip) ? `, ${D}\\${d.p}_mekan-dogrulama.jsonl` : ''}, kayıtların SON hâli ${DOSYALAR[d.tip](d.p).join(', ')}, kaynak metinleri (${W}\\_is\\kaynak_dizini.jsonl → text_file). Yalnız bunları oku.
Çıktı: ${D}\\${d.p}_dogrulama.jsonl — satır {"entry_id","bulgu_claim_id","sonuc":"dogru|hatali_duzeltme|eksik_kalan","agirlik":"ciddi|orta|hafif","aciklama","oneri"}. Dosyaları değiştirme.

${KABUKSUZ}
Bütçe: 40 dakika / 140 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}", satir, dogru, hatali_duzeltme, eksik_kalan, sorunlu_ciddi_orta}.`
}

function dogrulamaTuru(d, tmp) {
  const yer = d.tip === 'sozluk' ? '' : `, ${AG}\\yer-yazari.md`
  return `Corteqs Málaga paketinde EDİTÖRSÜN — doğrulama turu. Parça (<gorev>): ${d.p}.
Önce Read ile oku: ${AG}\\ortak-kurallar.md, ${AG}\\editor.md${yer}. Açık görevler: 8; uyguladığın düzeltmede 2, 6, 7. Kayıt ekleme/silme yok.
${DEGERLER(tmp)}
Girdi: ${D}\\${d.p}_dogrulama.jsonl — yalnız sonuc hatali_duzeltme ya da eksik_kalan VE agirlik ciddi ya da orta olan satırlar; her oneri'yi kaynakla kendin doğrula.
Dosyalar: ${DOSYALAR[d.tip](d.p).join(', ')}. Değişiklik kaydı: ${D}\\${d.p}_degisiklik.jsonl SONUNA (bulgu_claim_id = "dogrulama").
Bitirmeden: ${MERGE(tmp)}.

${KABUKLU}
Bütçe: 30 dakika / 100 araç çağrısı.
Dönüş (StructuredOutput): {part:"${d.p}-dogrulama", bulgu_toplam, uygulanan, reddedilen, degisen_kayit, silinen:[], yeni_kaynak:0, script_kontrol_hata, open}.`
}

// --- eşzamanlılık sınırı (bütün agent çağrıları) ---
let aktif = 0
const bekleyen = []
async function sinirli(fn) {
  if (aktif < N) aktif++
  else await new Promise(r => bekleyen.push(r))
  try { return await fn() } finally { const n = bekleyen.shift(); if (n) n(); else aktif-- }
}
const MODEL = (args && args.model) || 'sonnet'
const YUKSEK = { model: MODEL, effort: 'high', agentType: 'general-purpose' }
const ORTA = { model: MODEL, effort: 'medium', agentType: 'general-purpose' }
const SIRA = ['yazar', 'denetim', 'editor', 'dogrulayici', 'dturu']
const BASLAT = (args && args.baslat) || {}
const ajan = (istem, opt) => sinirli(() => agent(istem, opt))

// açık-mı: hemen başlar
const acik = {}
for (const g of (ACIK ? GRUPLAR : [])) {
  acik[g.k] = (async () => {
    const t = await ajan(tarayici(g), { ...ORTA, label: `acik-tara ${g.k}`, phase: 'Açık mı', schema: S_TARAMA })
    if (!t) { log(`açık-mı ${g.k}: tarayıcı sonuç dönmedi`); return { g, t: null, v: null } }
    let v = null
    if ((t.flagged && t.flagged.length) || (t.zayif && t.zayif.length)) {
      v = await ajan(acikDogrulayici(g, t), { ...YUKSEK, label: `acik-dogrula ${g.k}`, phase: 'Açık mı', schema: S_ADOG })
    }
    return { g, t, v }
  })()
}

async function zincir(d) {
  const k = { part: d.p }
  const tmp = rol => `${SP}\\${rol}_${d.p}_w`
  const YAZ = { mekan: mekanYazar, mahalle: mahalleYazar, sozluk: sozlukYazar, sayfa: sayfaYazar, rota: rotaYazar }
  const bi = Math.max(0, SIRA.indexOf(BASLAT[d.p] || 'yazar'))
  if (bi > 0) {
    // önceki turda yarıda kalan zincir: verilen adımdan devam
    if (bi <= 1) {
      k.denetim = await ajan(denetci(d, d.p), { ...YUKSEK, label: `denetim ${d.p}`, phase: 'Denetim', schema: S_DENETIM })
      if (k.denetim && k.denetim.ciddi + k.denetim.orta > 0) k.teyit = await ajan(teyitci(d), { ...YUKSEK, label: `curutme ${d.p}`, phase: 'Çürütme', schema: S_TEYIT })
    }
    if (bi <= 2) k.editor = await ajan(editorDenetim(d, tmp('editor')), { ...ORTA, label: `editor ${d.p}`, phase: 'Editör', schema: S_EDITOR })
    if (bi <= 3) k.dogrulama = await ajan(dogrulayici(d), { ...YUKSEK, label: `dogrulayici ${d.p}`, phase: 'Doğrulama', schema: S_DOGRULAMA })
    if (bi === 4 || (k.dogrulama && k.dogrulama.sorunlu_ciddi_orta > 0)) {
      k.dogrulama_turu = await ajan(dogrulamaTuru(d, tmp('dturu')), { ...ORTA, label: `dogrulama-turu ${d.p}`, phase: 'Doğrulama', schema: S_EDITOR })
    }
    log(`${d.p}: devam zinciri bitti`)
    return k
  }
  if (d.tip === 'rota' && args && args.rota_yazildi) {
    k.yazar = { part: 'rota', rows: -1, claims: -1, new_sources: 0, own_issues: 0, girdi_hazir: true, gaps: [], open: ['yazar önceki turda'] }
  } else {
    k.yazar = await ajan(YAZ[d.tip](d, tmp('yazar')), { ...ORTA, label: `yazar ${d.p}`, phase: 'Yazım', schema: S_YAZAR })
  }
  if (!k.yazar) { log(`${d.p}: yazar sonuç dönmedi — zincir durdu`); return k }
  if (d.tip === 'rota' && !(args && args.rota_yazildi)) { log('rota: yazar bitti; denetimden önce ana döngü yürüyüş ölçümü yapacak'); return k }
  if (d.tip === 'mekan' && ACIK) {
    const ac = await Promise.all(d.gruplar.map(g => acik[g]))
    k.acik = ac.map(a => ({ grup: a.g.k, tarama: a.t && a.t.count, flagged: a.t && a.t.flagged.length, sil: a.v && a.v.sil, belirt: a.v && a.v.kartta_belirt }))
    if (ac.some(a => a.v && (a.v.sil + a.v.kartta_belirt) > 0)) {
      k.uygulama = await ajan(uygulamaEditor(d, tmp('acikmi'), d.gruplar), { ...ORTA, label: `acik-uygula ${d.p}`, phase: 'Uygulama', schema: S_EDITOR })
    }
  }
  if (!k.yazar.girdi_hazir && !(k.uygulama)) log(`${d.p}: yazar denetim girdisi hazır demedi — denetçi yine de deniyor`)
  k.denetim = await ajan(denetci(d, d.p), { ...YUKSEK, label: `denetim ${d.p}`, phase: 'Denetim', schema: S_DENETIM })
  if (!k.denetim) { log(`${d.p}: denetçi sonuç dönmedi — zincir durdu`); return k }
  if (k.denetim.ciddi + k.denetim.orta > 0) {
    k.teyit = await ajan(teyitci(d), { ...YUKSEK, label: `curutme ${d.p}`, phase: 'Çürütme', schema: S_TEYIT })
  }
  if (k.denetim.ciddi + k.denetim.orta + k.denetim.hafif + (k.denetim.mekan_kaldi || 0) + k.denetim.duzelt_kart > 0) {
    k.editor = await ajan(editorDenetim(d, tmp('editor')), { ...ORTA, label: `editor ${d.p}`, phase: 'Editör', schema: S_EDITOR })
    k.dogrulama = await ajan(dogrulayici(d), { ...YUKSEK, label: `dogrulayici ${d.p}`, phase: 'Doğrulama', schema: S_DOGRULAMA })
    if (k.dogrulama && k.dogrulama.sorunlu_ciddi_orta > 0) {
      k.dogrulama_turu = await ajan(dogrulamaTuru(d, tmp('dturu')), { ...ORTA, label: `dogrulama-turu ${d.p}`, phase: 'Doğrulama', schema: S_EDITOR })
    }
  }
  log(`${d.p}: zincir bitti`)
  return k
}

phase('Yazım')
log(`${DILIMLER.length} parça + 8 açık-mı grubu; en çok ${N} ajan aynı anda`)
const sonuclar = await Promise.all(DILIMLER.map(zincir))
const acikSon = await Promise.all((ACIK ? GRUPLAR : []).map(g => acik[g.k]))
return { parcalar: sonuclar, acik_mi: acikSon.map(a => ({ grup: a.g.k, tarama: a.t, dogrulama: a.v })) }
