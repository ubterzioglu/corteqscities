export const meta = {
  name: 'marbella-cevap-denetim-zinciri',
  description: 'Marbella yanıt kartları: parça başına tam denetim → çürütme → tamamlama editörü → ek denetim → doğrulayıcı → doğrulama turu',
  phases: [
    { title: 'Denetim', detail: 'parça başına bağımsız iddia denetçisi (Sonnet yüksek)' },
    { title: 'Çürütme', detail: 'ciddi/orta bulguları kaynakla çürütmeye çalışan ayrı ajan' },
    { title: 'Editör', detail: 'tamamlama turu, görev 1–7 + script bulguları + eksikler' },
    { title: 'Ek denetim', detail: 'editörün eklediği kartlar (-ek turu) ve editörü' },
    { title: 'Doğrulama', detail: 'bağımsız doğrulayıcı ve gerekirse doğrulama turu editörü' },
  ],
}

const W = '/home/user/corteqscities/uretim/marbella'
const D = W + '/_is/denetim'
const AG = '/home/user/corteqscities/.claude/skills/city-pack/agents'
const TK = '/home/user/corteqscities/corteqs-skills/toolkit/scripts'
const PY = '/home/user/venv/bin/python'
const SP = '/tmp/claude-0/-home-user/b3f0bfa3-41f9-5ef5-84ba-25c7cca18097/scratchpad'
const KT = W + '/_is/araclar/kartlar_txt.py'
const BBOX = '36.45,36.57,-5.02,-4.71'
const ESZAMANLI = (args && args.eszamanli) || 4
const PARCALAR = (args && args.parcalar) || []

const KABUKSUZ = 'Kabuk kullanma (Bash yok): yalnız Read, Glob, Grep ve Write araçları. İnternete çıkma (WebFetch/WebSearch yok). Alt ajan başlatma. Yazacağın JSONL dosyalarını Write aracıyla yaz (UTF-8, satır başına bir JSON nesnesi); her 5 kartta bir dosyayı o ana kadarki TÜM satırlarla yeniden yaz (ana döngü 10 dakika büyümeyen dosyayı takılmış sayar).'
const KABUKLU = `Komut kuralı (Linux; PowerShell yok): Bash aracıyla her çağrıda TEK komut, tam yolla; cd, &&, ;, boru, heredoc ve python -c yok. Ortamı komutun başına ver: PYTHONDONTWRITEBYTECODE=1 PYTHONUTF8=1 ${PY} ... Python işi için önce .py dosyasını Write ile <TMP>'ye yaz, sonra ${PY} -I <dosya> ile çalıştır. Klasör oluşturmak gerekmez (Write açar). Dosyaları Read/Glob/Grep ile oku. Ortak kurallardaki PowerShell örneklerini bu kurala çevir (\\ yerine /, & '<PY>' yerine ${PY}, Test-Path yerine Glob). Alt ajan başlatma. Bir komut 2 dakikadan uzun yanıtsız kalırsa bekleme, notunu open'a yaz ve devam et.`
const ERISIM = 'Erişilemeyen alan adları (deneme): sede.marbella.es, malaga.es, sede.administracionespublicas.gob.es, mivau.gob.es, inclusion.gob.es, hidralia.es, puertobanus.com, museosdeandalucia.es, mgec.es, puertodeandalucia.es; hcs.es kopyası gzip olarak bozuk geliyor (kaynak olmaz).'

const S_DENETIM = {
  type: 'object',
  properties: {
    part: { type: 'string' }, cards: { type: 'integer' }, claims: { type: 'integer' }, dogru: { type: 'integer' },
    duzelt_kart: { type: 'integer' }, ciddi: { type: 'integer' }, orta: { type: 'integer' }, hafif: { type: 'integer' },
  },
  required: ['part', 'cards', 'claims', 'dogru', 'duzelt_kart', 'ciddi', 'orta', 'hafif'],
}
const S_TEYIT = {
  type: 'object',
  properties: { part: { type: 'string' }, kontrol: { type: 'integer' }, gercek: { type: 'integer' }, kismen: { type: 'integer' }, yersiz: { type: 'integer' } },
  required: ['part', 'kontrol', 'gercek', 'kismen', 'yersiz'],
}
const S_EDITOR = {
  type: 'object',
  properties: {
    part: { type: 'string' }, bulgu_toplam: { type: 'integer' }, uygulanan: { type: 'integer' }, reddedilen: { type: 'integer' },
    kural_duzeltme: { type: 'integer' }, eklenen: { type: 'array', items: { type: 'string' } }, silinen: { type: 'array', items: { type: 'string' } },
    degisen_kayit: { type: 'integer' }, yeni_kaynak: { type: 'integer' }, script_kontrol_hata: { type: 'integer' },
    ek_kartlar_hazir: { type: 'boolean' }, open: { type: 'array', items: { type: 'string' } },
  },
  required: ['part', 'bulgu_toplam', 'uygulanan', 'reddedilen', 'eklenen', 'silinen', 'degisen_kayit', 'script_kontrol_hata', 'open'],
}
const S_DOGRULAMA = {
  type: 'object',
  properties: {
    part: { type: 'string' }, satir: { type: 'integer' }, dogru: { type: 'integer' }, hatali_duzeltme: { type: 'integer' },
    eksik_kalan: { type: 'integer' }, sorunlu_ciddi_orta: { type: 'integer' },
  },
  required: ['part', 'satir', 'dogru', 'hatali_duzeltme', 'eksik_kalan', 'sorunlu_ciddi_orta'],
}

function denetciIstemi(p, tur) {
  const ad = tur ? `${p.p}-${tur}` : p.p
  return `Corteqs Marbella (CITY-080) paketinde BAĞIMSIZ İDDİA DENETÇİSİSİN. Parça: ${ad} (konu ${p.p}). Kartları sen yazmadın; yazarın gerekçesini görmüyorsun.

Önce Read ile oku: ${AG}/iddia-denetcisi.md — yöntem maddeleri 1–8 geçerli; o dosyadaki "Çıktı" ve "Dönüş" bölümleri ESKİ ve geçersiz, çıktı aşağıdaki gibidir.

Girdi: ${D}/${ad}_kartlar.txt (okunur hâli; aynı içerik ${ad}_kartlar.jsonl). Her kart: kartın bütün alanları + "kaynaklar" (source_id, url, publisher, text_file) + "iddialar" (yazar defteri: claim_id, field, claim, value, quote, source_id) + "adimlar", "butonlar". Kaynak metinleri: her kaynağın text_file yolu (Read; göreli yol ${W}/_is/ altına göredir). Yalnız bu dosyaları oku. Metin yetmiyorsa sonuç kaynak_yetersiz.

Ne yapacaksın — kartların HEPSİ, örneklem değil:
- Her kartın BÜTÜN defter satırlarını ve kart metnini kaynak metniyle anlamıyla karşılaştır: kime uygulanır (Türk vatandaşı / AB / diğer, statü), koşul, istisna, zorunlu/yasak/hak, yanlış genelleme, anlamı daraltan ya da ters çeviren çeviri, kaynakta olmayan çıkarım, sayı-birim-dönem, işlem aşaması karışıklığı (madde 7: ör. izin başvurusu ↔ TIE, başvuru ↔ yenileme, ulusal kural ↔ Marbella'daki ofis).
- Kart düzeyinde K25 (ilk cümle başlıktaki soruyu cevaplıyor mu) ve K26 (işlem kartında: nereye — Marbella'daki ya da en yakın ofis/kanal ve randevu yolu; ne getir — belge; ne öder — tutar ya da "ücretsiz"; ne kadar sürer / son tarih — gün türüyle). Eksik öğeyi adıyla yaz.
- Ayrıca bulgu: turizm portalına (turismo.marbella.es) dayanan ücret/saat/işlem kuralı; yılsız ya da geçmiş tarihli istisna cümlesi; okura iş bırakan cümle ("kurumdan doğrulayın", "siteye bak" vb.); okura "siz" hitabı ya da aynı kartta sen/siz karışması; kartta iç denetim/süreç notu; bağlantının (butonlar) kartın işlemine gitmemesi; kaynağın tarihi eski (ör. 2019, 2021) olup güncel gibi sunulan bilgi.
- "doğru" kararı yalnız kaynak metninde gördüğün birebir karşılığa dayanır.

Çıktı — yalnız bu iki dosya:
1. ${D}/${ad}_iddia.jsonl — doğru olmayan HER iddia + kart başına 2–4 doğru iddia. Satır:
{"claim_id":"","entry_id":"","iddia":"","ülke_şehir_statü":"","dönem":"","resmî_URL":"","kaynak_bölümü":"","yayın_yürürlük_tarihleri":"","kontrol_tarihi":"2026-10-28","hesap_varsa_girdiler":"","sonuç":"doğru|yanlış|eksik_koşul|kaynak_yetersiz|çelişkili_kaynak","ağırlık":"ciddi|orta|hafif|-","belirsizlik":"","alıntı":"kaynak metinden birebir, en çok 200 karakter","doğrusu":"doğru olmayanda karta konabilecek Türkçe öneri"}
ağırlık doğruda "-". claim_id: defterdeki claim_id; defterde olmayan bilgi ya da kart düzeyi bulgu için "<slug>-K<n>" (K26 eksiği için "<slug>-K26", K25 için "<slug>-K25").
2. ${D}/${ad}_karar.jsonl — kart başına bir satır:
{"entry_id":"","karar":"temiz|düzelt","en_agir":"ciddi|orta|hafif|-","ozet":"kısa; K26 eksik öğesi adıyla","denetlenen_iddia":<kartın defter satırı sayısı>,"dogru_ids":["doğru bulduğun claim_id'ler"]}
Başka dosyaya yazma${tur ? '; tire\'siz ' + p.p + '_iddia/_karar dosyalarına yazma' : '; tire\'li (-ek, -dN) dosyalara yazma'}; kartları değiştirme.

${KABUKSUZ}
Bütçe: 50 dakika / 160 araç çağrısı. Dolarsa bitirdiğin kartlarla dön; sayılar yalnız yazdıklarından.

Dönüş (StructuredOutput): {part:"${ad}", cards, claims, dogru, duzelt_kart, ciddi, orta, hafif} — sayıları kendi iki dosyandan say (claims = iddia satırı, dogru = sonuç doğru satırı, ciddi/orta/hafif = doğru olmayan satırların ağırlıkları).`
}

function teyitIstemi(p) {
  return `Corteqs Marbella paketinde ŞÜPHECİ İKİNCİ GÖZSÜN. Parça: ${p.p}. Bağımsız bir denetçi bu parçanın kartlarında bulgular yazdı. Görevin: "ciddi" ya da "orta" ağırlıklı, sonucu "doğru" olmayan HER bulguyu kaynak metniyle ÇÜRÜTMEYE çalışmak — bulgu gerçekten bir hata mı, yoksa denetçi kaynağı yanlış mı okudu?

Girdiler: ${D}/${p.p}_iddia.jsonl (bulgular), ${D}/${p.p}_kartlar.txt (kartlar, defter ve kaynakların text_file yolları; göreli yol ${W}/_is/ altına göre), kaynak metinleri (Read). Yalnız bunları oku.

Her ciddi/orta bulgu için: kartın ilgili cümlesini ve kaynağın ilgili bölümünü kendin bul, oku. Kararın:
- "gercek": kaynak bulguyu doğruluyor (kart gerçekten yanlış/eksik).
- "kismen": bulgu kısmen doğru; doğrusu önerisi abartılı ya da eksik — neyin doğru olduğunu yaz.
- "yersiz": kaynak kartı destekliyor; denetçi yanılmış — destekleyen birebir alıntıyı yaz.
Emin değilsen "kismen" yaz ve nedenini açıkla.

Çıktı: ${D}/${p.p}_teyit.jsonl — bulgu başına: {"claim_id":"","entry_id":"","teyit":"gercek|kismen|yersiz","gerekce":"","alinti":"kaynak metinden birebir, en çok 200 karakter","dogrusu":"kismen/gercek ise karta konacak doğru bilgi"}
Başka dosyaya yazma.

${KABUKSUZ}
Bütçe: 30 dakika / 100 araç çağrısı.

Dönüş (StructuredOutput): {part:"${p.p}", kontrol, gercek, kismen, yersiz}.`
}

function editorIstemi(p, tmp) {
  const adim = p.adimlar ? `, ${W}/_is/data/parcalar/Adımlar.${p.p}.jsonl` : ''
  return `Corteqs Marbella (CITY-080) paketinde EDİTÖRSÜN — tamamlama turu. Parça (<gorev>): ${p.p}. Kartları sen yazmadın, denetimi de sen yapmadın.

Önce Read ile oku (bu sırayla): ${AG}/ortak-kurallar.md, ${AG}/editor.md. Açık görevler: 1, 2, 3, 4, 5, 6, 7 (editor.md numaraları). Görev 8 ve 9 kapalı.

Değerler: <city_id>=marbella; <WORK>=${W}; <TK>=${TK}; <PY>=${PY}; <tarih>=2026-10-28; <bbox>=${BBOX}; <TMP>=${tmp}. Hitap: sen (okura 2. tekil; "siz" yok; bir kayıtta biçim karışmaz).

Düzenleyeceğin dosyalar (yalnız bunlar): ${W}/_is/data/parcalar/Yanıtlar.${p.p}.jsonl, ${W}/_is/data/parcalar/Bağlantılar.${p.p}.jsonl${adim}, ${W}/_is/claims/${p.p}.jsonl.
Değişiklik kaydı: ${D}/${p.p}_degisiklik.jsonl.

Girdiler:
- Bulgular: ${D}/${p.p}_iddia.jsonl ve ${D}/${p.p}_karar.jsonl. Çürütme sonucu (varsa): ${D}/${p.p}_teyit.jsonl — teyit "yersiz" olan bulguyu UYGULAMA; değişiklik kaydına reddedildi diye (yeni = "", gerekçe ve teyitteki alıntıyla) yaz. "kismen" olanda teyitteki dogrusu'na göre uygula.
- Script bulguları (metin kalitesi, hitap, fotoğraf üstü bant, birleştirme): ${D}/${p.p}_kur.json — her birini kapat (anlamı ve sayıları değiştirmeden yeniden yaz).
- Eksikler (görev 4): ${W}/_is/yazar/${p.p}_eksikler.json — yazarın kaynak bulamadığı bilgiler ve cevapsız "ilk 5" soruları. Her biri için resmî derin sayfa ara (WebSearch/WebFetch), bulursan add_sources ile ekle (ortak kurallar §4; <rol>=editor, klasör snap_${p.p}-editor<sira>; Glob ile ${W}/_is/snap_${p.p}-editor* klasörlerine bakıp boş sırayı bul) ve bilgiyi var olan karta ekle ya da yeni kart yaz. Bulamadığını open'a yaz. ${ERISIM} Turizm portalı ücret/saat/işlem kuralı kaynağı değildir.
- Kaynak bütçesi: bu parçada en çok 6 yeni kaynak; kart başına en çok 2 source_ids, en çok 2 Bağlantılar satırı.
- Görev 5 (değer): konunun toplam kartı (ülke kartları dahil) 18–26 arasında kalsın${p.hedef ? `; bu konuda şu an ${p.toplam} kart var, kaynakla desteklenen yeni Marbella kartlarıyla ${p.hedef}'e kadar çıkabilirsin (değersiz kart yazma)` : ''}; yeni kartın order değeri ${p.order}–${p.order + 99} aralığında, var olan kendi kartlarından sonra. Ülke kartı (order ≥ 9000) silinmez ve değiştirilmez.
- Slug/entry_id hiçbir kartta değişmez. Kart metnine iç denetim/editör notu yazılmaz.

Bitirmeden:
1. Ortak kurallar §8: ${PY} ${TK}/merge_package.py ${W}/_is --city-id marbella --bbox=${BBOX} --data-out ${tmp}/birlesik --out ${tmp}/birlestir_rapor.json  (--data-out ve --out ŞART). Kendi parçanı ilgilendiren bulgu 0 olmalı.
2. "doğru" olmayan her bulgunun değişiklik kaydında en az bir satırı var mı, say.
3. Yeni kart eklediysen ek denetim girdisini hazırla (iki komut, ayrı ayrı):
   ${PY} ${TK}/denetim_girdi.py ${W}/_is --city-id marbella --tur ek --parca ${p.p} --kayit <eklenen entry_id'ler, virgülle>
   ${PY} -I ${KT} ${D}/${p.p}-ek_kartlar.jsonl
   ve dönüşte ek_kartlar_hazir = true yaz. Kart eklemediysen false.

${KABUKLU}
Bütçe: 60 dakika / 200 araç çağrısı.

Dönüş (StructuredOutput): {part:"${p.p}", bulgu_toplam, uygulanan, reddedilen, kural_duzeltme, eklenen:[entry_id], silinen:[entry_id], degisen_kayit, yeni_kaynak, script_kontrol_hata, ek_kartlar_hazir, open:[...]} — sayıları dosyalardan say.`
}

function ekEditorIstemi(p, tmp) {
  const adim = p.adimlar ? `, ${W}/_is/data/parcalar/Adımlar.${p.p}.jsonl` : ''
  return `Corteqs Marbella paketinde EDİTÖRSÜN — denetim turu (eklenen kartlar). Parça (<gorev>): ${p.p}; tur adı: ${p.p}-ek.

Önce Read ile oku: ${AG}/ortak-kurallar.md, ${AG}/editor.md. Açık görevler: 1, 2, 6, 7. Kart ekleme/silme yok.
Değerler: <city_id>=marbella; <WORK>=${W}; <TK>=${TK}; <PY>=${PY}; <tarih>=2026-10-28; <TMP>=${tmp}. Hitap: sen.
Düzenleyeceğin dosyalar: ${W}/_is/data/parcalar/Yanıtlar.${p.p}.jsonl, Bağlantılar.${p.p}.jsonl${adim}, ${W}/_is/claims/${p.p}.jsonl — yalnız ${D}/${p.p}-ek_karar.jsonl içindeki kartlar.
Bulgular: ${D}/${p.p}-ek_iddia.jsonl, ${D}/${p.p}-ek_karar.jsonl. Değişiklik kaydı: ${D}/${p.p}-ek_degisiklik.jsonl.
Yeni kaynak gerekirse add_sources (rol editor, snap_${p.p}-editor<sira>, Glob ile boş sıra). ${ERISIM}
Bitirmeden ortak kurallar §8: ${PY} ${TK}/merge_package.py ${W}/_is --city-id marbella --bbox=${BBOX} --data-out ${tmp}/birlesik --out ${tmp}/birlestir_rapor.json.

${KABUKLU}
Bütçe: 35 dakika / 120 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}-ek", bulgu_toplam, uygulanan, reddedilen, kural_duzeltme, eklenen:[], silinen:[], degisen_kayit, yeni_kaynak, script_kontrol_hata, ek_kartlar_hazir:false, open:[...]}.`
}

function dogrulayiciIstemi(p, ekVar) {
  const ek = ekVar ? ` Ek tur da var: ${D}/${p.p}-ek_degisiklik.jsonl (bulgular ${p.p}-ek_iddia.jsonl, ${p.p}-ek_karar.jsonl) — onun sonucunu ayrı dosyaya, ${D}/${p.p}-ek_dogrulama.jsonl'e yaz.` : ''
  return `Corteqs Marbella paketinde BAĞIMSIZ DOĞRULAYICISIN (yazar, denetçi ve editör değilsin). Parça: ${p.p}.

Görev: editörün her değişikliğini kaynak metniyle karşılaştır — (a) kaynakla tutarlı mı, (b) bulguyu gerçekten kapatıyor mu, (c) yeni yanlış, genelleme ya da kaynakta olmayan bilgi eklemiş mi, (d) okura "siz" hitabı, iş bırakan cümle ya da iç süreç notu eklemiş mi. Sonra değişiklik kaydı OLMAYAN bulguları ara: sonucu "doğru" olmayan her bulgu (iddia dosyası) ya da "düzelt" kararlı her kart için değişiklik kaydında en az bir satır olmalı; yoksa ve kart hâlâ hatalıysa eksik_kalan.

Girdiler: ${D}/${p.p}_degisiklik.jsonl (editör), ${D}/${p.p}_iddia.jsonl, ${D}/${p.p}_karar.jsonl, ${D}/${p.p}_teyit.jsonl (varsa; "yersiz" bulgunun reddi doğrudur, yine de alıntıyı kontrol et), kartların SON hâli ${W}/_is/data/parcalar/Yanıtlar.${p.p}.jsonl ve defter ${W}/_is/claims/${p.p}.jsonl, kaynak metinleri (${W}/_is/kaynak_dizini.jsonl → text_file, göreli yol ${W}/_is/ altına göre).${ek} Yalnız bu dosyaları oku.

Çıktı: ${D}/${p.p}_dogrulama.jsonl — değişiklik ya da eksik bulgu başına: {"entry_id":"","bulgu_claim_id":"","sonuc":"dogru|hatali_duzeltme|eksik_kalan","agirlik":"ciddi|orta|hafif","aciklama":"","oneri":"kaynağa dayalı öneri; alıntıyla"}. Dosyaları değiştirme; başka dosyaya yazma.

${KABUKSUZ}
Bütçe: 40 dakika / 140 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}", satir, dogru, hatali_duzeltme, eksik_kalan, sorunlu_ciddi_orta} — sorunlu_ciddi_orta: sonucu hatali_duzeltme ya da eksik_kalan olup agirlik ciddi ya da orta olan satır sayısı (ek tur dosyası dahil).`
}

function dogrulamaTuruIstemi(p, tmp, ekVar) {
  const adim = p.adimlar ? `, Adımlar.${p.p}.jsonl` : ''
  return `Corteqs Marbella paketinde EDİTÖRSÜN — doğrulama turu. Parça (<gorev>): ${p.p}.

Önce Read ile oku: ${AG}/ortak-kurallar.md, ${AG}/editor.md. Açık görevler: 8; uyguladığın düzeltmede 2, 6, 7. Kart ekleme/silme yok.
Değerler: <city_id>=marbella; <WORK>=${W}; <TK>=${TK}; <PY>=${PY}; <tarih>=2026-10-28; <TMP>=${tmp}. Hitap: sen.
Girdi: ${D}/${p.p}_dogrulama.jsonl${ekVar ? ` ve ${D}/${p.p}-ek_dogrulama.jsonl` : ''} — yalnız sonuc = hatali_duzeltme ya da eksik_kalan VE agirlik = ciddi ya da orta olan satırlar. Her birinin oneri'sini kaynakla KENDİN doğrula, doğruysa uygula; değilse kaynağa göre düzelt.
Dosyalar: ${W}/_is/data/parcalar/Yanıtlar.${p.p}.jsonl, Bağlantılar.${p.p}.jsonl${adim}, ${W}/_is/claims/${p.p}.jsonl. Değişiklik kaydı: ${D}/${p.p}_degisiklik.jsonl'in SONUNA ekle (bulgu_claim_id = "dogrulama"); önceki satırları silme.
Bitirmeden ortak kurallar §8: ${PY} ${TK}/merge_package.py ${W}/_is --city-id marbella --bbox=${BBOX} --data-out ${tmp}/birlesik --out ${tmp}/birlestir_rapor.json.

${KABUKLU}
Bütçe: 30 dakika / 100 araç çağrısı.
Dönüş (StructuredOutput): {part:"${p.p}-dogrulama", bulgu_toplam, uygulanan, reddedilen, kural_duzeltme, eklenen:[], silinen:[], degisen_kayit, yeni_kaynak:0, script_kontrol_hata, ek_kartlar_hazir:false, open:[...]}.`
}

const OPT_YUKSEK = { model: 'sonnet', effort: 'high', agentType: 'general-purpose' }
const OPT_ORTA = { model: 'sonnet', effort: 'medium', agentType: 'general-purpose' }

async function zincir(p) {
  const kayit = { part: p.p }
  const tmp = (rol) => `${SP}/${rol}_${p.p}_w`
  kayit.denetim = await agent(denetciIstemi(p, ''), { ...OPT_YUKSEK, label: `denetim ${p.p}`, phase: 'Denetim', schema: S_DENETIM })
  if (!kayit.denetim) { log(`${p.p}: denetçi sonuç dönmedi — zincir durdu`); return kayit }
  if (kayit.denetim.ciddi + kayit.denetim.orta > 0) {
    kayit.teyit = await agent(teyitIstemi(p), { ...OPT_YUKSEK, label: `curutme ${p.p}`, phase: 'Çürütme', schema: S_TEYIT })
  }
  kayit.editor = await agent(editorIstemi(p, tmp('editor')), { ...OPT_ORTA, label: `editor ${p.p}`, phase: 'Editör', schema: S_EDITOR })
  if (!kayit.editor) { log(`${p.p}: editör sonuç dönmedi — zincir durdu`); return kayit }
  let ekVar = false
  if (kayit.editor.eklenen && kayit.editor.eklenen.length && kayit.editor.ek_kartlar_hazir) {
    ekVar = true
    kayit.ek_denetim = await agent(denetciIstemi(p, 'ek'), { ...OPT_YUKSEK, label: `denetim ${p.p}-ek`, phase: 'Ek denetim', schema: S_DENETIM })
    if (kayit.ek_denetim && kayit.ek_denetim.ciddi + kayit.ek_denetim.orta + kayit.ek_denetim.hafif > 0) {
      kayit.ek_editor = await agent(ekEditorIstemi(p, tmp('ekeditor')), { ...OPT_ORTA, label: `editor ${p.p}-ek`, phase: 'Ek denetim', schema: S_EDITOR })
    }
  } else if (kayit.editor.eklenen && kayit.editor.eklenen.length) {
    log(`${p.p}: editör ${kayit.editor.eklenen.length} kart ekledi ama ek denetim girdisi hazır değil — ana döngü yapacak`)
  }
  const duzeltOrani = kayit.denetim.cards ? kayit.denetim.duzelt_kart / kayit.denetim.cards : 1
  if (kayit.denetim.ciddi > 0 || duzeltOrani >= 0.3 || ekVar) {
    kayit.dogrulama = await agent(dogrulayiciIstemi(p, ekVar), { ...OPT_YUKSEK, label: `dogrulayici ${p.p}`, phase: 'Doğrulama', schema: S_DOGRULAMA })
    if (kayit.dogrulama && kayit.dogrulama.sorunlu_ciddi_orta > 0) {
      kayit.dogrulama_turu = await agent(dogrulamaTuruIstemi(p, tmp('dturu'), ekVar), { ...OPT_ORTA, label: `dogrulama-turu ${p.p}`, phase: 'Doğrulama', schema: S_EDITOR })
    }
  } else {
    log(`${p.p}: ciddi yok ve düzelt oranı <%30 — doğrulayıcı atlandı (SKILL adım 6), değişiklik kaydı script'le sayılacak`)
  }
  log(`${p.p}: zincir bitti`)
  return kayit
}

async function havuz(items, n, fn) {
  const sonuc = []
  let k = 0
  async function isci() {
    while (k < items.length) {
      const j = k++
      sonuc[j] = await fn(items[j])
    }
  }
  await Promise.all(Array.from({ length: n }, isci))
  return sonuc
}

phase('Denetim')
log(`${PARCALAR.length} parça, en çok ${ESZAMANLI} zincir aynı anda`)
const sonuc = await havuz(PARCALAR, ESZAMANLI, zincir)
return sonuc