# Excel satır verilerinin montajı: tüm sekmeler için nihai satır listeleri
import json, os, re, datetime

TODAY = datetime.date(2026, 10, 20)
CITY = "eindhoven"

sources = json.load(open('data_sources.json', encoding='utf-8'))
topics = json.load(open('data_topics.json', encoding='utf-8'))
topic_by_slug = {t['slug']: t for t in topics}
src_by_cache = {s['source_id'].split(':')[-1]: s for s in sources}
wiki = json.load(open('wiki_data.json', encoding='utf-8')) if os.path.exists('wiki_data.json') else {}
monumenten = json.load(open('monumenten.json', encoding='utf-8'))
places = json.load(open('places_master.json', encoding='utf-8'))
districts = json.load(open('districts_master.json', encoding='utf-8'))
routes = json.load(open('routes_master.json', encoding='utf-8'))
glossary = json.load(open('glossary_master.json', encoding='utf-8'))
misc = json.load(open('misc_master.json', encoding='utf-8'))

answers = []
import glob
for f in sorted(glob.glob('answers_t*.json')):
    answers.extend(json.load(open(f, encoding='utf-8')))

def sid(cache_id):
    return f"eindhoven:kaynak:{cache_id}"

# ---------- wiki kaynakları ekle ----------
extra_sources = []
wiki_src_ids = {}
for slug, w in wiki.items():
    if not w.get('url'):
        continue
    src_id = f"eindhoven:kaynak:wiki-{slug}"
    wiki_src_ids[slug] = src_id
    ex = (w.get('extract') or '').replace('\n', ' ').strip()
    extra_sources.append({
        "source_id": src_id, "city_id": CITY,
        "title": f"Wikipedia: {w['wiki_title']}", "publisher": "Wikipedia (NL)",
        "url": w['url'], "checked_on": TODAY.isoformat(), "topic": "kesif",
        "summary": (ex[:240] + '…') if len(ex) > 240 else (ex or 'Madde özeti.'),
        "verified": "Evet", "order": 900,
    })

# ---------- mekân meta: anıt eşleme ----------
MON_MAP = {
 'klooster-marienhage': 'Mariënhage', 'molen-annemie': 'Annemie',
 'genneper-watermolen': 'Genneper Watermolen', 'collse-watermolen': 'Collse Watermolen',
 'sint-petruskerk': 'Sint-Petruskerk', 'sint-lambertuskerk': 'Sint-Lambertuskerk',
 'steentjeskerk': 'Steentjeskerk', 'heilig-hartkerk': 'Heilig Hartkerk',
 'sint-theresiakerk': 'Theresiakerk', 'sint-martinuskerk': 'Martinuskerk',
 'paterskerk': 'Paterskerk', 'clarissenklooster': 'Clarissenklooster',
 'philips-observatorium': 'Observatorium', 'van-maerlantlyceum': 'Maerlant',
 'gemeentelijke-hbs': 'Gemeentelijke HBS', 'st-joriscollege': 'Joriscollege',
 'w-hal-tue': 'W-Hal', 'nutsschool-reigerlaan': 'Nutsschool',
 'mennen-poortgebouw': 'Bergstraat 26', 'kasteel-eckart': 'Eckart',
 'sint-joriskerk': 'Joriskerk', 'gerardus-majellakerk': 'Gerardus Majellakerk',
 'villa-de-laak': 'De Laak', 'oude-toren-woensel': 'Oude Toren',
 'sint-catharinakerk': 'Catharinakerk', 'lichttoren': 'Lichttoren',
 'witte-dame': 'Witte Dame', 'next-nature-evoluon': 'Evoluon',
 'watertoren': 'Watertoren', 'sint-trudokerk': 'Trudokerk',
 'raadhuis-tongelre': 'Raadhuis', 'station-eindhoven-centraal': None,
}
mon_by_key = {}
for m in monumenten:
    mon_by_key.setdefault(m['name'], m)

def find_mon(key):
    if not key:
        return None
    for m in monumenten:
        if key.lower() in (m['name'] or '').lower() or key.lower() in (m['commonscat'] or '').lower():
            return m
    return None

OFFICIAL_SRC = {
 'van-abbemuseum': 'vanabbemuseum', 'philips-museum': 'philipsmuseum',
 'daf-museum': 'dafmuseum-info', 'next-nature-evoluon': 'nextnature',
 'ton-smits-huis': 'tonsmitshuis', 'mu-arthouse': 'mu-arthouse',
 'kazerne-design': 'kazerne-org', 'design-academy': 'designacademy',
 'muziekgebouw': 'muziekgebouw', 'parktheater': 'parktheater',
 'effenaar': 'effenaar', 'natlab': 'natlab', 'philips-stadion': 'psv',
 'strijp-s': 'strijp-s', 'hightech-campus': 'hightechcampus',
 'tue-atlas': 'tue', 'tue-auditorium': 'tue', 'w-hal-tue': 'tue',
 'eindhoven-airport-terminal': 'eindhoven-airport',
 'historisch-openluchtmuseum': 'wiki-rijksmonumenten-eindhoven',
 'strijp-s-markt-weekly': 'tie-central-market',
 'haftalik-pazarlar': 'tie-central-market',
 'kruisstraat-keent': 'tie-woenselse-markt',
 'winkelcentrum-woensel': 'tie-woenselse-markt',
}

SETTING = {
 'Müzeler': 'Kapalı alan', 'Sahne ve müzik': 'Kapalı alan', 'Sanat ve sergiler': 'Kapalı alan',
 'Spor': 'Açık hava', 'Çocuklarla keşif': 'Açık hava', 'Doğa ve açık hava': 'Açık hava',
 'Yeme ve içme': 'Karma', 'Tarih ve mimari': 'Açık hava',
}
SETTING_OVR = {
 'historisch-openluchtmuseum': 'Açık hava', 'berenkuil-street-art': 'Açık hava',
 'kazerne-design': 'Karma', 'design-academy': 'Karma', 'natlab': 'Karma',
 'ijssportcentrum': 'Kapalı alan', 'zwembad-tongelreep': 'Kapalı alan',
 'hoogenband-zwemstadion': 'Kapalı alan', 'philips-stadion': 'Açık hava',
 'vershal-het-veem': 'Kapalı alan', 'winkelcentrum-woensel': 'Kapalı alan',
 'heuvel-galerie': 'Kapalı alan', 'cafe-100-watt': 'Kapalı alan',
 'cafe-wilhelmina': 'Kapalı alan', 'strijp-s': 'Karma', 'klokgebouw': 'Karma',
 'eindhoven-airport-terminal': 'Karma', 'hightech-campus': 'Karma',
 'de-bergen-horeca': 'Açık hava', 'striatumseind': 'Açık hava',
 'tue-atlas': 'Karma', 'tue-auditorium': 'Karma', 'w-hal-tue': 'Karma',
 'strijp-s-markt-weekly': 'Açık hava', 'haftalik-pazarlar': 'Açık hava',
 'muziekgebouw': 'Kapalı alan', 'parktheater': 'Kapalı alan', 'effenaar': 'Kapalı alan',
 'mu-arthouse': 'Kapalı alan',
 'sint-catharinakerk': 'Karma', 'paterskerk': 'Karma', 'steentjeskerk': 'Karma',
 'sint-petruskerk': 'Karma', 'sint-lambertuskerk': 'Karma', 'sint-martinuskerk': 'Karma',
 'sint-trudokerk': 'Karma', 'sint-joriskerk': 'Karma', 'gerardus-majellakerk': 'Karma',
 'sint-theresiakerk': 'Karma', 'heilig-hartkerk': 'Karma',
 'klooster-marienhage': 'Karma', 'clarissenklooster': 'Karma',
 'philips-museum': 'Kapalı alan', 'daf-museum': 'Kapalı alan',
 'van-abbemuseum': 'Kapalı alan', 'next-nature-evoluon': 'Karma',
 'ton-smits-huis': 'Kapalı alan',
}

def good_coord(lat, lon):
    try:
        la, lo = float(lat), float(lon)
    except (TypeError, ValueError):
        return None
    if 51.3 <= la <= 51.55 and 5.2 <= lo <= 5.7:
        return la, lo
    return None

# ---------- YANITLAR ----------
rows_answers = []
order = 0
for a in answers:
    t = topic_by_slug[a['topic']]
    rows_answers.append({
        'entry_id': f"eindhoven:{a['slug']}", 'city_id': CITY, 'slug': a['slug'],
        'title': a['title'], 'subtitle': t['title'], 'summary': a['summary'],
        'keywords': a['keywords'], 'stages': a['stages'],
        'source_ids': ';'.join(sid(s) for s in a['sources']),
        'reviewed_on': TODAY, 'order': order,
        'featured': 'Evet' if a.get('featured') else 'Hayır',
        'editorial_status': 'İnceleme', 'topic_id': f"eindhoven:{a['topic']}",
        'steps': '\n'.join(a['steps']),
        'documents': '\n'.join(a['documents']) if isinstance(a.get('documents'), list) else a.get('documents'),
        'timing': a.get('timing'), 'cost': a.get('cost'), 'note': a.get('note'),
        'visual_json': None,
    })
    order += 1

# ---------- MEKÂNLAR ----------
rows_places = []
place_titles = {}
for pl in places:
    slug = pl['slug']
    place_titles[slug] = pl['title']
    mon = find_mon(MON_MAP.get(slug))
    lat = lon = None
    if mon:
        c = good_coord(mon.get('lat'), mon.get('lon'))
        if c:
            lat, lon = c
        addr = mon.get('adres')
    else:
        addr = pl.get('addr')
    w = wiki.get(slug)
    if lat is None and w:
        c = good_coord(w.get('lat'), w.get('lon'))
        if c:
            lat, lon = c
    srcs = []
    off = OFFICIAL_SRC.get(slug)
    if off and (off in src_by_cache or off.startswith('wiki-')):
        if off.startswith('wiki-'):
            srcs.append(sid(off[5:] if off[5:] in src_by_cache else off))
        else:
            srcs.append(sid(off))
    if w and slug in wiki_src_ids:
        srcs.append(wiki_src_ids[slug])
    if mon:
        srcs.append(sid('wiki-rijksmonumenten-eindhoven'))
    if not srcs:
        srcs.append(sid('thisiseindhoven') if 'thisiseindhoven' in src_by_cache else sid('wiki-eindhoven-nl'))
    loc = addr or f"{pl.get('district', 'Eindhoven')}, Eindhoven"
    note = pl.get('visit_note', '')
    disclaimer = "Saat, ücret ve kapalı günleri ziyaret öncesi kurumdan doğrula; bilet/rezervasyon kurumun kendi kanalındadır."
    rows_places.append({
        'entry_id': f"eindhoven:{slug}", 'city_id': CITY, 'slug': slug,
        'title': pl['title'], 'subtitle': f"{pl['group']} · {pl.get('district', '')}".strip(' ·'),
        'summary': note, 'keywords': f"{pl['title']} {pl['group']} {pl.get('district', '')} Eindhoven".strip(),
        'stages': None, 'source_ids': ';'.join(dict.fromkeys(srcs)),
        'reviewed_on': TODAY, 'order': order,
        'featured': 'Evet' if pl.get('featured') else 'Hayır',
        'editorial_status': 'İnceleme', 'group': pl['group'], 'district': pl.get('district'),
        'setting': SETTING_OVR.get(slug, SETTING.get(pl['group'], 'Karma')),
        'location': loc, 'latitude': lat, 'longitude': lon,
        'visit_status': 'Aktif', 'note': disclaimer,
        'collection': 'Evet' if pl.get('featured') else 'Hayır', 'media_key': slug,
    })
    order += 1

# ---------- MAHALLELER ----------
DIST_TAGS = {
 'binnenstad': ['Alışveriş ve gece hayatı', 'Kültür kurumları', 'Yürünebilirlik'],
 'de-bergen': ['Butik restoranlar', 'Tarihi sokak dokusu', 'Merkeze komşu'],
 'strijp-s': ['Tasarım ve atölyeler', 'Endüstriyel mimari', 'Etkinlik sahneleri'],
 'philipsdorp': ['Bahçe-köy dokusu', 'İşçi mahallesi mirası', 'Merkeze 5 dk'],
 'meerhoven': ['Planlı aile mahallesi', 'Havalimanı yakınlığı', 'Park ve su öğeleri'],
 'oud-woensel': ['Çok kültürlü çarşı', 'Uygun kiralar', 'Cumartesi pazarı'],
 'acht': ['Köy meydanı', 'Yel değirmeni', 'Kırsal sakinlik'],
 'roosten': ['Genneper Parken komşuluğu', 'Okul kampüsleri', 'Yeşil kenar'],
 'doornakkers': ['Uygun konut', 'Modernist okul mirası', 'Merkeze yakın'],
 'villapark': ['Korunmuş villa dokusu', 'Dommel vadisi yeşili', 'Sessiz prestij'],
 'karpen-koudenhoven': ['Göl kıyısı', 'Villa yerleşimi', 'Yüzme ve yürüyüş'],
 'oud-stratum': ['Witte Dorp bahçe-köyü', 'Irisbuurt', 'Aile ölçeği'],
 'burghplan': ['Bahçe-banliyö', 'Park bantları', 'Sakinlik'],
 'leenderheide': ['Fundalık doğa', 'Bisiklet rotaları', 'Kır havası'],
 'oud-gestel': ['Manastır ve kilise dokusu', 'Uygun kiralar', 'Yerel mahalle'],
 'hofke-tongelre': ['Köy meydanı', 'Martinuskerk', 'Tarihi doku'],
}
rows_districts = []
for d in districts:
    slug = d['slug']
    cmp_json = json.dumps(d['compare'], ensure_ascii=False)
    rows_districts.append({
        'entry_id': f"eindhoven:mah-{slug}", 'city_id': CITY, 'slug': f"mah-{slug}",
        'title': d['title'], 'subtitle': d.get('who_for', ''),
        'summary': d['description'],
        'keywords': f"{d['title']} mahalle bölge Eindhoven {d.get('who_for', '')}".replace('  ', ' '),
        'stages': None,
        'source_ids': ';'.join([sid('wiki-wijken'), sid('gemeente-woning-huren')]),
        'reviewed_on': TODAY, 'order': order,
        'featured': 'Evet' if slug in ('binnenstad', 'strijp-s', 'de-bergen') else 'Hayır',
        'editorial_status': 'İnceleme',
        'location': f"{d['title']}, Eindhoven",
        'tags': '\n'.join(DIST_TAGS.get(slug, [])),
        'compare_json': cmp_json,
        'note': f"Kimine uygun: {d.get('who_for', '')}. Ev bakarken sokağı farklı saatlerde gör; bina bazında gürültü, park ve ulaşımı değerlendir.",
        'media_key': f"mah-{slug}",
    })
    order += 1

# ---------- ROTALAR ----------
ROUTE_NOTES = {
 'merkez-ikonlari': 'Tamamı yürüyüş; müze girişlerini eklersen yarım güne uzar. Pazar günleri mağazalar kapalı, meydanlar sakindir.',
 'philips-mirasi': 'Bisiklet önerilir; Philips Museum pazartesi kapalı olabilir, saatleri kontrol et.',
 'dommel-sanat': 'Dommel kıyısı patikaları; Van Abbe pazartesi kapalı. Gözlemevi akşam programlarında açıktır.',
 'strijp-tasarim': 'DDW/GLOW dönemlerinde yoğunluk artar; Natlab ve Vershal gün boyu açık.',
 'woensel-cok-kulturlu': 'Cumartesi Woenselse Markt günü en canlısı; pazar tezgâhları erken toplanır.',
 'guney-yesil': 'Uzun tur; su ve rüzgâr koruması al. Açık hava müzesinin etkinlik günlerini kontrol et.',
 'tongelre-su-miras': 'Kanal ve Dommel kıyısı; Collse Watermolen restoranında mola verilebilir.',
 'kilise-manzume': 'Kilise ziyaretlerinde ayin saatlerine saygı; bazıları yalnız gündüz açıktır.',
 'mimari-zaman-cizelgesi': 'Bisikletle tam gün; kampüs binaları dışarıdan görülür, iç ziyaret kuruma bağlıdır.',
 'spor-gunu': 'PSV maç gününde merkez ve stadion çevresi çok yoğun; P+R Genneper Parken pratik.',
 'aile-rota': 'Arabayla kolay; De Splinter ve havuzlarda sezon saatlerini kontrol et.',
 'lezzet-pazar': 'Salı veya cumartesi planla; akşam Stratumseind ile bitir. Pazar günleri tezgâh yoktur.',
}
rows_routes = []
for i, r in enumerate(routes):
    stops_names = [place_titles.get(s, s) for s in r['stops']]
    rows_routes.append({
        'route_id': f"eindhoven:route:{i+1:03d}", 'city_id': CITY, 'title': r['title'],
        'tag': f"{r['duration']} · {r['mode']}",
        'stops': '\n'.join(stops_names),
        'stop_entry_ids': ';'.join(f"eindhoven:{s}" for s in r['stops']),
        'entry_id': f"eindhoven:{r['stops'][0]}",
        'note': ROUTE_NOTES.get(r['slug'], 'Editoryal rota önerisi; mesafe ve süre tahmindir.') + (f" En iyi zaman: {r['best_time']}." if r.get('best_time') else ''),
        'reviewed_on': TODAY,
        'source_ids': ';'.join([sid('thisiseindhoven'), sid('gemeente-fietsen')]),
        'order': i, 'editorial_status': 'İnceleme',
    })

# ---------- SÖZLÜK ----------
rows_glossary = []
for i, g in enumerate(glossary):
    rows_glossary.append({
        'term_id': f"eindhoven:term:{i+1:03d}", 'city_id': CITY, 'term': g['term'],
        'definition': g['desc'],
        'source_ids': ';'.join(sid(s) for s in g['sources']),
        'reviewed_on': TODAY, 'order': i, 'editorial_status': 'İnceleme',
    })

# ---------- ADIMLAR ----------
rows_steps = []
for st in misc['steps']:
    rows_steps.append({
        'step_id': f"eindhoven:step:{st['order']+1}", 'city_id': CITY,
        'entry_id': st['entry'], 'title': st['title'], 'when': st['when'],
        'description': st['description'], 'order': st['order'],
    })

# ---------- BAĞLANTILAR ----------
src_url = {s['source_id']: s['url'] for s in sources}
rows_actions = []
def add_action(entry_id, label, url, idx):
    rows_actions.append({
        'action_id': f"eindhoven:action:{entry_id.split(':',1)[1]}-{idx}",
        'city_id': CITY, 'entry_id': entry_id, 'label': label, 'url': url,
        'checked_on': TODAY, 'order': idx - 1,
    })
# yanıtlar: ilk kaynak + (varsa) ikinci farklı-alan adı kaynak
seen_dom = {}
for a in answers:
    eid = f"eindhoven:{a['slug']}"
    urls = []
    for s in a['sources']:
        u = src_url.get(sid(s))
        if u and u not in urls:
            urls.append(u)
    if urls:
        add_action(eid, 'Resmî işlem ve bilgi', urls[0], 1)
    if len(urls) > 1:
        from urllib.parse import urlparse
        d0 = urlparse(urls[0]).netloc
        for u in urls[1:]:
            if urlparse(u).netloc != d0:
                add_action(eid, 'Ek resmî kaynak', u, 2)
                break
# mekânlar: resmî site veya harita
OFFICIAL_URL_OVERRIDE = {
 'van-abbemuseum': 'https://vanabbemuseum.nl/', 'philips-museum': src_url.get(sid('philipsmuseum')),
 'daf-museum': src_url.get(sid('dafmuseum-info')), 'next-nature-evoluon': src_url.get(sid('nextnature')),
 'ton-smits-huis': src_url.get(sid('tonsmitshuis')), 'mu-arthouse': src_url.get(sid('mu-arthouse')),
 'kazerne-design': src_url.get(sid('kazerne-org')), 'design-academy': src_url.get(sid('designacademy')),
 'muziekgebouw': src_url.get(sid('muziekgebouw')), 'parktheater': src_url.get(sid('parktheater')),
 'effenaar': src_url.get(sid('effenaar')), 'natlab': src_url.get(sid('natlab')),
 'philips-stadion': src_url.get(sid('psv')), 'strijp-s': src_url.get(sid('strijp-s')),
 'hightech-campus': src_url.get(sid('hightechcampus')), 'tue-atlas': src_url.get(sid('tue')),
 'tue-auditorium': src_url.get(sid('tue')), 'w-hal-tue': src_url.get(sid('tue')),
 'eindhoven-airport-terminal': src_url.get(sid('eindhoven-airport')),
 'haftalik-pazarlar': src_url.get(sid('tie-central-market')),
 'kruisstraat-keent': src_url.get(sid('tie-woenselse-markt')),
}
import urllib.parse
for pr in rows_places:
    eid = pr['entry_id']
    u = OFFICIAL_URL_OVERRIDE.get(pr['slug'])
    if u:
        add_action(eid, 'Resmî site', u, 1)
        q = urllib.parse.quote(f"{pr['title']}, Eindhoven")
        add_action(eid, 'Konum (Google Haritalar)', f"https://www.google.com/maps/search/?api=1&query={q}", 2)
    else:
        q = urllib.parse.quote(f"{pr['title']}, Eindhoven")
        add_action(eid, 'Konum (Google Haritalar)', f"https://www.google.com/maps/search/?api=1&query={q}", 1)
for dr in rows_districts:
    q = urllib.parse.quote(f"{dr['title']}, Eindhoven")
    add_action(dr['entry_id'], 'Bölgeyi haritada gör', f"https://www.google.com/maps/search/?api=1&query={q}", 1)

# ---------- SAYFAALANLARI ----------
rows_fields = []
def add_field(key, vtype, value, label=None):
    rows_fields.append({
        'field_id': f"eindhoven:field:{key}", 'city_id': CITY, 'key': key,
        'label': label or f"Özgün sayfa alanı: {key}", 'value_type': vtype,
        'value': value if isinstance(value, str) else json.dumps(value, ensure_ascii=False),
        'reviewed_on': TODAY,
    })
pf = misc['pagefields']
add_field('facts', 'JSON', pf['facts'])
add_field('timeline', 'JSON', pf['timeline'])
add_field('emergency', 'JSON', pf['emergency'])
add_field('quick_links', 'JSON', pf['quick_links'])
add_field('budget_fields', 'JSON', pf['budget_fields'])
add_field('place_groups', 'JSON', pf['place_groups'])
for k, v in pf['texts'].items():
    add_field(k, 'Metin', v['value'], f"Özgün sayfa alanı: {k}")
add_field('expansion_version', 'Sayı', '1')

# ---------- ŞEHİR / TESLİMAT ----------
city_row = misc['city']
teslimat_row = misc['teslimat']

out = {
 'topics': topics,
 'sources': sources + extra_sources,
 'answers': rows_answers,
 'places': rows_places,
 'districts': rows_districts,
 'routes': rows_routes,
 'glossary': rows_glossary,
 'steps': rows_steps,
 'actions': rows_actions,
 'fields': rows_fields,
 'city': city_row,
 'teslimat': teslimat_row,
}
json.dump(out, open('excel_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('answers', len(rows_answers), '| places', len(rows_places), '| districts', len(rows_districts),
      '| routes', len(rows_routes), '| glossary', len(rows_glossary), '| steps', len(rows_steps),
      '| actions', len(rows_actions), '| fields', len(rows_fields), '| sources', len(sources) + len(extra_sources))
# koordinat doluluk
noc = [p['slug'] for p in rows_places if p['latitude'] is None]
print('places without coords:', len(noc), noc[:20])
noaddr = [p['slug'] for p in rows_places if not p['location']]
print('places without location:', len(noaddr))
