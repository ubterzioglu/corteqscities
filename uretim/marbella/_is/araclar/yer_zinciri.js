export const meta = {
  name: 'marbella-yer-denetim-zinciri',
  description: 'Marbella yer parçaları (mekân, mahalle, sözlük, rota): tam denetim (+mekân doğrulama) → çürütme (ciddi varsa) → editör denetim turu → doğrulayıcı (ciddi varsa)',
  phases: [
    { title: 'Denetim', detail: 'parça başına bağımsız denetçi (Sonnet yüksek)' },
    { title: 'Çürütme', detail: 'yalnız ciddi bulgu varsa' },
    { title: 'Editör', detail: 'denetim turu, görev 1, 2, 6, 7' },
    { title: 'Doğrulama', detail: 'yalnız ciddi bulgu varsa doğrulayıcı + doğrulama turu' },
  ],
}

const W = '/home/user/corteqscities/uretim/marbella'
const D = W + '/_is/denetim'
const P = W + '/_is/data/parcalar'
const AG = '/home/user/corteqscities/.claude/skills/city-pack/agents'
const TK = '/home/user/corteqscities/corteqs-skills/toolkit/scripts'
const PY = '/home/user/venv/bin/python'
const SP = '/tmp/claude-0/-home-user-corteqscities/b3f0bfa3-41f9-5ef5-84ba-25c7cca18097/scratchpad'
const BBOX = '36.40,36.62,-5.18,-4.62'
const ESZAMANLI = (args && args.eszamanli) || 3
const PARCALAR = (args && args.parcalar) || []

const KABUKSUZ = 'Kabuk kullanma (Bash yok): yalnız Read, Glob, Grep ve Write araçları. İnternete çıkma (WebFetch/WebSearch yok). Alt ajan başlatma. Yazacağın JSONL dosyalarını Write aracıyla yaz (UTF-8, satır başına bir JSON nesnesi); her 5 kayıtta bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz.'
const KABUKLU = `Komut kuralı (Linux; PowerShell yok): Bash aracıyla her çağrıda TEK komut, tam yolla; cd, &&, ;, boru, heredoc ve python -c yok. Ortamı komutun başına ver: PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 ${PY} ... Python işi için önce .py dosyasını Write ile <TMP>'ye yaz, sonra ${PY} -I <dosya> ile çalıştır. Dosyaları Read/Glob/Grep ile oku. Ortak kurallardaki PowerShell örneklerini bu kurala çevir. Alt ajan başlatma.`
const ERISIM = 'Erişilemeyen alan adları (deneme): sede.marbella.es, malaga.es, sede.administracionespublicas.gob.es, mivau.gob.es, inclusion.gob.es, hidralia.es, puertobanus.com, museosdeandalucia.es, mgec.es, puertodeandalucia.es, benahavis.es, ojen.es, istan.es; hcs.es kopyası bozuk.'

const S_DENETIM = { type: 'object', properties: { part: { type: 'string' }, cards: { type: 'integer' }, claims: { type: 'integer' }, dogru: { type: 'integer' }, duzelt_kart: { type: 'integer' }, ciddi: { type: 'integer' }, orta: { type: 'integer' }, hafif: { type: 'integer' }, mekan_kaldi: { type: 'integer' } }, required: ['part', 'cards', 'claims', 'dogru', 'duzelt_kart', 'ciddi', 'orta', 'hafif'] }
const S_TEYIT = { type: 'object', properties: { part: { type: 'string' }, kontrol: { type: 'integer' }, gercek: { type: 'integer' }, kismen: { type: 'integer' }, yersiz: { type: 'integer' } }, required: ['part', 'kontrol', 'gercek', 'kismen', 'yersiz'] }
const S_EDITOR = { type: 'object', properties: { part: { type: 'string' }, bulgu_toplam: { type: 'integer' }, uygulanan: { type: 'integer' }, reddedilen: { type: 'integer' }, degisen_kayit: { type: 'integer' }, degisen_ids: { type: 'array', items: { type: 'string' } }, yeni_kaynak: { type: 'integer' }, script_kontrol_hata: { type: 'integer' }, open: { type: 'array', items: { type: 'string' } } }, required: ['part', 'bulgu_toplam', 'uygulanan', 'reddedilen', 'degisen_kayit', 'script_kontrol_hata', 'open'] }
const S_DOGRULAMA = { type: 'object', properties: { part: { type: 'string' }, satir: { type: 'integer' }, dogru: { type: 'integer' }, hatali_duzeltme: { type: 'integer' }, eksik_kalan: { type: 'integer' }, sorunlu_ciddi_orta: { type: 'integer' } }, required: ['part', 'satir', 'dogru', 'hatali_duzeltme', 'eksik_kalan', 'sorunlu_ciddi_orta'] }

function ozel(p) {
  if (p.tur === 'mekan') return `\nBu bir MEKÂN parçası. Ayrıca: (a) iddia-denetcisi.md madde 9'a göre kayıt başına bir satır yaz: ${D}/${p.p}_mekan-dogrulama.jsonl ({"entry_id","kimlik","adres","koordinat","ziyaret","sonuc":"geçti|kaldı","not"}). (b) visit_status dolu her kayıt bulgu (K103). (c) K108: aynı adresi/bileti paylaşan alt nesne ayrı kart olamaz (örn. capilla-de-san-juan-de-dios-marbella ile hospital-real-de-la-misericordia aynı yapı mı? kaynakla karar ver). (d) ücret/saat yalnız mekânın kendi resmî sayfasından; turizm portalı ya da belediye haberi tek dayanaksa ve tarihliyse tarihiyle yazılmalı. (e) "Yakın çevre gezisi" notlu kayıtta kasaba adı ve kaynak tutarlı mı. (f) location alanında kaynakta olmayan adres uydurulmuş mu (genel semt betimi kabul; sokak/numara uydurma ciddi). (g) Not: mekânın kendisini tanıtmayan, kalıp ya da boş not (S08) bulgu.`
  if (p.tur === 'mahalle') return `\nBu MAHALLE parçası. Ayrıca iddia-denetcisi.md madde 9'a göre kayıt başına bir satır: ${D}/${p.p}_mekan-dogrulama.jsonl (adres öğesi mahallede "tutar", notta "mahalle"). compare_json'daki her değerin kaynakta karşılığı ve tarihi (eski otobüs/sezon bilgisi güncel gibi sunulmuş mu). Kanıtsız genelleme (güvenlik, gelir, "en iyi") bulgu.`
  if (p.tur === 'rota') return `\nBu ROTA parçası. Ek girdiler: ${W}/_is/rota_plan.jsonl (yazarın gün/saat planı) ve ${W}/_is/rota_mesafe.jsonl (OSM yaya mesafeleri, ana döngü ölçtü). Kontrol: her durak gerçek Mekânlar kaydı (${P}/Mekânlar.m1.jsonl, m2, m3); önerilen gün/saatte kapalı durak var mı (durak kaydının saatlerinden); yürüyüş rotasında ardışık bacak rota_mesafe'de >3 km mi; notta yürüyüş mesafesi rota_mesafe ile tutarlı mı ("kuş uçuşu" etiketsiz km yazılmış mı); tag süresine sığıyor mu; araçla gidilen bacak notta açıkça yazılı mı.`
  if (p.tur === 'sozluk') return `\nBu SÖZLÜK parçası. Her terimin tanımı kaynakta karşılığı olan bir tanım mı; terim gerçek yerel terim mi; tanım kaynakta olmayan kural/sayı eklemiş mi. Kart düzeyi K25/K26 burada uygulanmaz.`
  return ''
}

function denetciIstemi(p) {
  return `Corteqs Marbella (CITY-080) paketinde BAĞIMSIZ İDDİA DENETÇİSİSİN. Parça: ${p.p}. Kayıtları sen yazmadın.

Önce Read ile oku: ${AG}/iddia-denetcisi.md — yöntem maddeleri 1–9 geçerli; o dosyadaki "Çıktı" ve "Dönüş" bölümleri ESKİ ve geçersiz, çıktı aşağıdaki gibidir.

Girdi: ${D}/${p.p}_kartlar.txt (okunur hâli; aynı içerik ${p.p}_kartlar.jsonl): her kayıt bütün alanları + "kaynaklar" (text_file yolu ${W}/_is/ altına göre) + "iddialar" (yazar defteri) + "butonlar". Yalnız bu dosyaları ve kaynak metinlerini oku. Metin yetmiyorsa sonuç kaynak_yetersiz.${ozel(p)}

Bütün kayıtlar (örneklem değil): defter satırlarını ve metni kaynakla anlamıyla karşılaştır (koşul, istisna, yanlış genelleme, kaynakta olmayan çıkarım, sayı-birim-dönem); okura "siz" hitabı, iş bırakan cümle, iç süreç notu; bağlantı etiketi hedefle aynı mı; kaynağın tarihi eski olup güncel gibi sunulan bilgi.

Çıktı — yalnız bu dosyalar:
1. ${D}/${p.p}_iddia.jsonl — doğru olmayan HER iddia + kayıt başına 1–3 doğru iddia: {"claim_id":"","entry_id":"","iddia":"","ülke_şehir_statü":"","dönem":"","resmî_URL":"","kaynak_bölümü":"","yayın_yürürlük_tarihleri":"","kontrol_tarihi":"2026-10-28","hesap_varsa_girdiler":"","sonuç":"doğru|yanlış|eksik_koşul|kaynak_yetersiz|çelişkili_kaynak","ağırlık":"ciddi|orta|hafif|-","belirsizlik":"","alıntı":"kaynaktan birebir ≤200","doğrusu":""} (defterde olmayan bilgi/kayıt düzeyi bulgu: claim_id "<slug>-K<n>").
2. ${D}/${p.p}_karar.jsonl — kayıt başına: {"entry_id":"","karar":"temiz|düzelt","en_agir":"ciddi|orta|hafif|-","ozet":"","denetlenen_iddia":<defter satırı>,"dogru_ids":[]} (sözlükte entry_id = term_id, rotada route_id).
${p.tur === 'mekan' || p.tur === 'mahalle' ? `3. ${D}/${p.p}_mekan-dogrulama.jsonl (yukarıda).\n` : ''}Başka dosyaya yazma; kayıtları değiştirme.

${KABUKSUZ}
Bütçe: 50 dakika / 170 araç çağrısı.

Dönüş (StructuredOutput): {part:"${p.p}", cards, claims, dogru, duzelt_kart, ciddi, orta, hafif${p.tur === 'mekan' || p.tur === 'mahalle' ? ', mekan_kaldi' : ''}} — sayıları kendi dosyalarından say.`
}

function teyitIstemi(p) {
  return `Corteqs Marbella paketinde ŞÜPHECİ İKİNCİ GÖZSÜN. Parça: ${p.p}. Görevin: ${D}/${p.p}_iddia.jsonl içindeki "ciddi" ağırlıklı, sonucu "doğru" olmayan HER bulguyu kaynak metniyle çürütmeye çalışmak. Girdiler: o dosya, ${D}/${p.p}_kartlar.txt ve kaynak metinleri (text_file, ${W}/_is/ altına göre). Çıktı: ${D}/${p.p}_teyit.jsonl — bulgu başına {"claim_id":"","entry_id":"","teyit":"gercek|kismen|yersiz","gerekce":"","alinti":"birebir ≤200","dogrusu":""}. Başka dosyaya yazma.
${KABUKSUZ}
Bütçe: 25 dakika / 80 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}", kontrol, gercek, kismen, yersiz}.`
}

function editorIstemi(p, tmp) {
  return `Corteqs Marbella (CITY-080) paketinde EDİTÖRSÜN — denetim turu. Parça (<gorev>): ${p.p}. Kayıtları sen yazmadın, denetimi de sen yapmadın.

Önce Read ile oku (bu sırayla): ${AG}/ortak-kurallar.md, ${AG}/editor.md, ${AG}/yer-yazari.md. Açık görevler: 1, 2, 6, 7 (editor.md numaraları). Kayıt ekleme/silme YOK; tek istisna: denetçinin K108 (alt nesne) bulgusu teyitliyse alt nesne kaydı silinebilir — o zaman Bağlantılar ve defter satırlarını da çıkar, rota durağıysa rotayı da düzelt, dönüşte silinen'e yaz.

Değerler: <city_id>=marbella; <WORK>=${W}; <TK>=${TK}; <PY>=${PY}; <tarih>=2026-10-28; <bbox>=${BBOX}; <TMP>=${tmp}. Hitap: sen.
Düzenleyeceğin dosyalar (yalnız bunlar): ${p.dosyalar.map(f => (f.startsWith('/') ? f : P + '/' + f)).join(', ')}, ${W}/_is/claims/${p.p}.jsonl.
Değişiklik kaydı: ${D}/${p.p}_degisiklik.jsonl.
Girdiler: ${D}/${p.p}_iddia.jsonl, ${D}/${p.p}_karar.jsonl${p.tur === 'mekan' || p.tur === 'mahalle' ? `, ${D}/${p.p}_mekan-dogrulama.jsonl ("kaldı" satırlarındaki tutmayan öğeyi düzelt)` : ''}, varsa ${D}/${p.p}_teyit.jsonl ("yersiz" olanı uygulama, kayda reddedildi diye yaz). "doğru" olmayan her bulguyu kaynakla kendin doğrula ve uygula; kaynakla düzeltilemeyen bilgi karttan çıkarılır ya da kaynağın söylediğiyle sınırlanır ("doğrulanamadı" yazılmaz). Yeni kaynak gerekirse add_sources (rol editor, klasör snap_${p.p}-editor<sira>; Glob ile boş sıra), en çok 4. ${ERISIM} Turizm portalı ücret/saat kaynağı değildir. Slug/entry_id değişmez. visit_status her zaman "". Koordinat değiştirme (yalnız resmî adres kaydıyla ve bulgu gerektiriyorsa).

Bitirmeden: ${PY} ${TK}/merge_package.py ${W}/_is --city-id marbella --bbox=${BBOX} --data-out ${tmp}/birlesik --out ${tmp}/birlestir_rapor.json — kendi parçanı ilgilendiren bulgu 0 olmalı. "doğru" olmayan her bulgunun değişiklik kaydında satırı var mı, say.

${KABUKLU}
Bütçe: 50 dakika / 170 araç çağrısı.

Dönüş (StructuredOutput): {part:"${p.p}", bulgu_toplam, uygulanan, reddedilen, degisen_kayit, degisen_ids:[...], yeni_kaynak, script_kontrol_hata, open:[...]} — sayıları dosyalardan say; silinen kayıt varsa open'a "silinen: <id>" yaz.`
}

function dogrulayiciIstemi(p) {
  return `Corteqs Marbella paketinde BAĞIMSIZ DOĞRULAYICISIN. Parça: ${p.p}. Editörün değişikliklerini (${D}/${p.p}_degisiklik.jsonl) kaynak metniyle karşılaştır: kaynakla tutarlı mı, bulguyu kapatıyor mu, yeni yanlış eklemiş mi; değişiklik kaydı olmayan doğru-olmayan bulguları ara (${D}/${p.p}_iddia.jsonl). Kayıtların son hâli: ${p.dosyalar.map(f => (f.startsWith('/') ? f : P + '/' + f)).join(', ')}; defter ${W}/_is/claims/${p.p}.jsonl; kaynak metinleri (${W}/_is/kaynak_dizini.jsonl → text_file). Çıktı: ${D}/${p.p}_dogrulama.jsonl — {"entry_id":"","bulgu_claim_id":"","sonuc":"dogru|hatali_duzeltme|eksik_kalan","agirlik":"ciddi|orta|hafif","aciklama":"","oneri":""}. Dosyaları değiştirme.
${KABUKSUZ}
Bütçe: 30 dakika / 100 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}", satir, dogru, hatali_duzeltme, eksik_kalan, sorunlu_ciddi_orta}.`
}

function dogrulamaTuruIstemi(p, tmp) {
  return `Corteqs Marbella paketinde EDİTÖRSÜN — doğrulama turu. Parça: ${p.p}. Önce oku: ${AG}/ortak-kurallar.md, ${AG}/editor.md. Açık görev 8 (uyguladığın düzeltmede 2, 6, 7). Girdi: ${D}/${p.p}_dogrulama.jsonl — yalnız hatali_duzeltme/eksik_kalan VE ciddi/orta satırlar; öneriyi kaynakla kendin doğrula ve uygula. Dosyalar: ${p.dosyalar.map(f => (f.startsWith('/') ? f : P + '/' + f)).join(', ')}, ${W}/_is/claims/${p.p}.jsonl. Değişiklik kaydı ${D}/${p.p}_degisiklik.jsonl SONUNA (bulgu_claim_id="dogrulama"). <TMP>=${tmp}. Bitirmeden merge_package kontrolü (--data-out ${tmp}/birlesik --out ${tmp}/birlestir_rapor.json --bbox=${BBOX}).
${KABUKLU}
Bütçe: 25 dakika / 80 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}-dogrulama", bulgu_toplam, uygulanan, reddedilen, degisen_kayit, degisen_ids:[], yeni_kaynak:0, script_kontrol_hata, open:[]}.`
}

const OPT_YUKSEK = { model: 'sonnet', effort: 'high', agentType: 'general-purpose' }
const OPT_ORTA = { model: 'sonnet', effort: 'medium', agentType: 'general-purpose' }

async function zincir(p) {
  const kayit = { part: p.p }
  const tmp = (rol) => `${SP}/${rol}_${p.p}_w`
  kayit.denetim = await agent(denetciIstemi(p), { ...OPT_YUKSEK, label: `denetim ${p.p}`, phase: 'Denetim', schema: S_DENETIM })
  if (!kayit.denetim) { log(`${p.p}: denetçi sonuç dönmedi`); return kayit }
  if (kayit.denetim.ciddi > 0) kayit.teyit = await agent(teyitIstemi(p), { ...OPT_YUKSEK, label: `curutme ${p.p}`, phase: 'Çürütme', schema: S_TEYIT })
  if (kayit.denetim.duzelt_kart > 0 || (kayit.denetim.mekan_kaldi || 0) > 0) {
    kayit.editor = await agent(editorIstemi(p, tmp('editor')), { ...OPT_ORTA, label: `editor ${p.p}`, phase: 'Editör', schema: S_EDITOR })
  }
  if (kayit.editor && kayit.denetim.ciddi > 0) {
    kayit.dogrulama = await agent(dogrulayiciIstemi(p), { ...OPT_YUKSEK, label: `dogrulayici ${p.p}`, phase: 'Doğrulama', schema: S_DOGRULAMA })
    if (kayit.dogrulama && kayit.dogrulama.sorunlu_ciddi_orta > 0) kayit.dogrulama_turu = await agent(dogrulamaTuruIstemi(p, tmp('dturu')), { ...OPT_ORTA, label: `dogrulama-turu ${p.p}`, phase: 'Doğrulama', schema: S_EDITOR })
  }
  log(`${p.p}: zincir bitti`)
  return kayit
}

async function havuz(items, n, fn) {
  const sonuc = []
  let k = 0
  async function isci() { while (k < items.length) { const j = k++; sonuc[j] = await fn(items[j]) } }
  await Promise.all(Array.from({ length: n }, isci))
  return sonuc
}

phase('Denetim')
log(`${PARCALAR.length} parça, en çok ${ESZAMANLI} zincir aynı anda`)
return await havuz(PARCALAR, ESZAMANLI, zincir)