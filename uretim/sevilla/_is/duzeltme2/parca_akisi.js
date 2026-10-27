export const meta = {
  name: 'sevilla-mekan-parca-akisi',
  description: 'Sevilla yeni mekan parcasi: acik-mi taramasi ve bagimsiz denetim paralel, sonra dogrulayici ve duzeltme',
  phases: [
    { title: 'Tara+Denetle', detail: 'acik-mi tarayici ve iddia denetcisi ayni anda' },
    { title: 'Dogrula+Duzelt', detail: 'acik-mi dogrulayici (gerekirse), sonra editor' },
  ],
}

const W = 'C:\\temp_private\\corteqs\\0000_newera\\uretim\\sevilla'
const A = 'C:\\temp_private\\corteqs\\0000_newera\\.claude\\skills\\city-pack\\agents'
const S = 'C:\\Users\\BARIS-~1\\AppData\\Local\\Temp\\claude\\c--temp-private-corteqs-0000-newera\\56c9766a-06a1-495c-9d57-190d48973e42\\scratchpad'
const part = args.part
const ORTAK = `Değerler: <WORK> = ${W} ; <city_id> = sevilla ; <TK> = C:\\temp_private\\corteqs\\0000_newera\\corteqs-skills\\toolkit\\scripts ; <PY> = C:\\temp_private\\corteqs\\0000_newera\\.venv\\Scripts\\python.exe ; <tarih> = 2026-10-25 ; <bbox> = 37.30,37.45,-6.03,-5.89 ; hitap sen. Alt ajan başlatma. Yalnız sana verilen dosyalara yaz.`

const TARA_SCHEMA = { type: 'object', properties: { count: { type: 'number' }, flagged: { type: 'array', items: { type: 'string' } }, notes: { type: 'array', items: { type: 'string' } } }, required: ['count', 'flagged'] }
const DEN_SCHEMA = { type: 'object', properties: { cards: { type: 'number' }, claims: { type: 'number' }, dogru: { type: 'number' }, duzelt_kart: { type: 'number' }, ciddi: { type: 'number' }, orta: { type: 'number' }, hafif: { type: 'number' }, gaps: { type: 'array', items: { type: 'string' } } }, required: ['cards', 'claims', 'duzelt_kart', 'ciddi'] }

phase('Tara+Denetle')
const [tara, den] = await parallel([
  () => agent(`Önce oku: ${A}\\acik-mi.md (§1–§3) ve ${A}\\ortak-kurallar.md §1. Rolün: TARAYICI. ${ORTAK} <sehir> = Sevilla ; dil ES (cerrado, cierre, obras, reforma, cerrado temporalmente, reapertura).
Mekânlar: ${W}\\_is\\data\\parcalar\\Mekânlar.${part}.jsonl içindeki HER satır. Kilise ve meydan için de tarihli faaliyet kanıtı (2025–2026 tarihli cofradía/parroquia etkinliği, ayin programı, belediye/Junta duyurusu, haber) ara.
Çıktı yalnız: ${W}\\_is\\acik_mi\\ek4_${part}.jsonl (§3 satır biçimi, Python ile UTF-8). Geçici dosyalar: ${S}\\${part}_tara_w\\ . Bütçe 20 dk.
Dönüş: count (yazdığın satır), flagged (açık dışındaki her satır: "entry_id | durum | kanıt + url"), notes.`, { label: `tara:${part}`, phase: 'Tara+Denetle', schema: TARA_SCHEMA, model: 'sonnet', effort: 'medium' }),
  () => agent(`Görev talimatın: ${W}\\_is\\duzeltme2\\DENETCI2_GOREV.md ve ${A}\\iddia-denetcisi.md "Yöntem" bölümü. Kartlar Yanıtlar değil mekân; "Odak 2" yerine şu ölçütler: "K38" ücret/saat yalnız mekânın kendi resmî sayfasından ve kaynakla tutarlı; "K42" ad/adres/ziyaret bilgisi kaynakla tutarlı; "K54" bağlantı etiketi gittiği sayfanın işine uyuyor (${W}\\_is\\data\\parcalar\\Bağlantılar.${part}.jsonl); "K108" kart ayrı bir mekân (başka mekânın parçası değil, paketteki ${W}\\_is\\data\\Mekânlar.jsonl kayıtlarıyla karşılaştır). Karar satırında K25/K26/K31/K40 yerine K38/K42/K54/K108.
Girdi: ${W}\\_is\\denetim\\${part}_kartlar.jsonl, defter ${W}\\_is\\claims\\${part}.jsonl. İnternete çıkma, kartları değiştirme.
Çıktı yalnız: ${W}\\_is\\denetim\\${part}_iddia.jsonl ve ${part}_karar.jsonl. Geçici dosyalar: ${S}\\${part}_den_w\\ . ${ORTAK} Bütçe 30 dk.
Dönüş: sayıları dosyadan say.`, { label: `denetle:${part}`, phase: 'Tara+Denetle', schema: DEN_SCHEMA, model: 'sonnet', effort: 'high' }),
])

phase('Dogrula+Duzelt')
let dog = null
if (tara && tara.flagged && tara.flagged.length) {
  dog = await agent(`Önce oku: ${A}\\acik-mi.md (§1, §2, §4) ve ${A}\\ortak-kurallar.md §1. Rolün: ŞÜPHECİ DOĞRULAYICI; taramayı sen yapmadın. ${ORTAK} <sehir> = Sevilla ; dil ES.
Girdi: ${W}\\_is\\acik_mi\\ek4_${part}.jsonl. İşaretli satırlar: ${JSON.stringify(tara.flagged)}.
Çıktı yalnız: ${W}\\_is\\acik_mi\\ek4_${part}_dogrulama.jsonl (§4 satır biçimi, Python ile UTF-8). Geçici: ${S}\\${part}_dog_w\\ . Bütçe 20 dk.
Dönüş: §4'teki tek satır JSON.`, { label: `dogrula:${part}`, phase: 'Dogrula+Duzelt', model: 'sonnet', effort: 'high' })
}
const needEdit = (den && den.duzelt_kart > 0) || (dog && /kartta belirt|sil/.test(String(dog)))
let ed = null
if (needEdit) {
  ed = await agent(`Önce oku: ${A}\\ortak-kurallar.md, editor.md, yer-yazari.md, mekan-yazari.md, acik-mi.md §5. ${ORTAK}
Tur: denetim turu, açık görevler 1, 2, 6, 7 ve acik-mi.md §5 (yalnız doğrulama satırlarındaki "kartta belirt"/"sil" eylemleri; "sil" iki bağımsız kaynakla).
Bulgular: ${W}\\_is\\denetim\\${part}_iddia.jsonl + ${part}_karar.jsonl ("doğru" olmayan her iddia ve "kaldı" her ölçüt); açık-mı: ${W}\\_is\\acik_mi\\ek4_${part}_dogrulama.jsonl (varsa).
Düzenlenecek dosyalar: ${W}\\_is\\data\\parcalar\\Mekânlar.${part}.jsonl, Bağlantılar.${part}.jsonl, ${W}\\_is\\claims\\${part}.jsonl. Değişiklik kaydı: ${W}\\_is\\denetim\\${part}_degisiklik.jsonl (açık-mı için ${W}\\_is\\denetim\\acik_mi_degisiklik.jsonl). Kaynakta olmayan bilgi çıkarılır; turizm portalı ücret/saat kaynağı değildir; engelli alan adları: sevilla.org, sede.sevilla.org, tussam.es, lipasam.es, aena.es, femas.es.
Bitirmeden: ortak kurallar §8 merge_package (çıktılar ${S}\\${part}_ed_w\\) kendi parçana bulgu 0. Bütçe 25 dk. Dönüş: editor.md tek satır JSON.`, { label: `duzelt:${part}`, phase: 'Dogrula+Duzelt', model: 'sonnet', effort: 'medium' })
}
return { part, tara, den, dog, ed }
