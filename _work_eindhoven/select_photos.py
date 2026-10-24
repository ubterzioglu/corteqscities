# Fotoğraf seçimi v3: başlık-öncelikli eşleşme, türev dışlama, düzeltilmiş havuzlar
import json, re, unicodedata

def norm(s):
    s = unicodedata.normalize('NFKD', s or '')
    s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', s.lower()).strip()

probes = {}
for f in ['commons_probe.json', 'commons_probe2.json', 'commons_probe3.json', 'commons_probe4.json',
          'commons_probe_dc.json', 'commons_probe_dc2.json']:
    try:
        probes.update(json.load(open(f, encoding='utf-8')))
    except FileNotFoundError:
        pass

POOL_MAP = {
 'eikenburg': ['eikenburg', 'eikenburg2'],
 'grote-beek': ['grote-beek', 'grote-beek2'],
 'stadswandelpark': ['stadswandelpark', 'stadswandelpark2'],
 'karpendonkse-plas': ['karpendonkse-plas', 'karpendonkse-plas2', 'mah-karpen2'],
 'leenderheide': ['leenderheide', 'leenderheide2', 'mah-leenderheide'],
 'sint-joriskerk': ['sint-joriskerk', 'sint-joriskerk2'],
 'kasteel-eckart': ['kasteel-eckart', 'kasteel-eckart2'],
 'kanaal-eindhoven': ['kanaal-eindhoven', 'kanaal2'],
 'dommel-eindhoven': ['dommel-eindhoven', 'dommel2'],
 'ijssportcentrum': ['ijssportcentrum', 'ijssportcentrum2'],
 'tue-atlas': ['tue-metaforum', 'tue-auditorium'],
 'speelpark-de-splinter': ['speeltuin'],
 'berenkuil-street-art': ['berenkuil', 'kapak-skyline'],
 'bevrijdingsmonument': ['oorlogsmonument'],
 'oorlogsmonument-fellenoord': ['oorlogsmonument'],
 'zwembad-tongelreep': ['sportpark-aalsterweg'],
 'grote-markt': ['grote-markt', 'markt-eindhoven', 'strijp-s-markt-weekly'],
 'haftalik-pazarlar': ['strijp-s-markt-weekly', 'grote-markt'],
 'de-bergen-horeca': ['de-bergen3', 'de-bergen-horeca'],
 'parktheater': ['parktheater2', 'parktheater'],
 'philips-stadion': ['philips-stadion2', 'philips-stadion'],
 'effenaar': ['effenaar'],
 'hightech-campus': ['hightech-campus2', 'hightech-campus'],
 'genneper-parken': ['genneper-parken', 'kapak-dogal'],
 'winkelcentrum-woensel': ['winkelcentrum-woensel'],
 'porthos-toren': ['winkelcentrum-woensel'],
 'philips-nederland-gebouw': ['philips-nederland-gebouw'],
 'herdgang': ['herdgang'],
 'tue-auditorium': ['tue-auditorium'],
 'strijp-s': ['strijp-s'],
}

KW = {
 'van-abbemuseum': ['van abbe'], 'philips-museum': ['philips museum'],
 'daf-museum': ['daf museum', 'stoombierbrouwerij de valk'], 'next-nature-evoluon': ['evoluon', 'next nature'],
 'historisch-openluchtmuseum': ['openluchtmuseum', 'prehistorisch dorp', 'openlucht eindhoven'],
 'ton-smits-huis': ['jacob reviuslaan 25', 'ton smits'],
 'mu-arthouse': ['mu hybrid'], 'kazerne-design': ['kazerne'],
 'design-academy': ['design academy', 'witte dame'],
 'muziekgebouw': ['muziekgebouw', 'muziekcentrum frits philips'],
 'parktheater': ['schouwburg te eindhoven', 'parktheater'], 'effenaar': ['effenaar'], 'natlab': ['natlab'],
 'cafe-wilhelmina': ['café wilhelmina', 'cafe wilhelmina'],
 'philips-stadion': ['philips stadion', 'psv eindhoven'],
 'hoogenband-zwemstadion': ['hoogenband'],
 'ijssportcentrum': ['ijssportcentrum', 'indoor sportcentrum'],
 'jan-louwers-stadion': ['jan louwers'], 'oranje-rood-hockey': ['oranje rood'],
 'sportpark-aalsterweg': ['aalsterweg sportpark'],
 'herdgang': ['herdgang'],
 'speelpark-de-splinter': ['de splinter'], 'zwembad-tongelreep': ['tongelreep'],
 'genneper-parken': ['genneper parken', 'genneperweg', 'waterbollen'],
 'stadswandelpark': ['stadswandelpark'], 'karpendonkse-plas': ['karpendonkse', 'karpedonkse'],
 'leenderheide': ['leenderheide', 'leendereide'], 'eikenburg': ['eikenburg'],
 'grote-beek': ['grote beek', 'poletlaan'],
 'kanaal-eindhoven': ['eindhovens kanaal', 'eindhovensch kanaal', 'kanaal eindhoven'],
 'dommel-eindhoven': ['dommel'],
 'strijp-s': ['strijp s', 'glasgebouw', 'blok 59'], 'klokgebouw': ['klokgebouw'],
 'lichttoren': ['lichttoren', 'light tower'],
 'witte-dame': ['witte dame'], 'de-blob': ['blob'], 'de-admirant': ['admirant'],
 'vesteda-toren': ['vesteda'], 'trudo-vertical-forest': ['trudo'],
 'station-eindhoven-centraal': ['station eindhoven', 'eindhoven centraal'],
 'stadskantoor': ['stadskantoor', 'stadhuis eindhoven'],
 'bijenkorf-eindhoven': ['bijenkorf'], 'sint-catharinakerk': ['catharinakerk'],
 'oude-toren-woensel': ['oude toren'],
 'watertoren': ['watertoren'], 'hoge-herde': ['fellenoord'],
 'hightech-campus': ['high tech campus', 'htc'],
 '18-septemberplein': ['18 septemberplein'],
 'grote-markt': ['eindhovenmarkt', 'markt eindhoven', 'eindhoven centre', 'markt, standbeeld frits philips'],
 'catharinaplein': ['catharinaplein'], 'wilhelminaplein': ['wilhelminaplein'],
 'sint-trudokerk': ['trudokerk'], 'woenselse-watermolen': ['woenselse watermol'],
 'klooster-marienhage': ['marien hage', 'marienhage'], 'molen-annemie': ['annemie', 'beltmolen'],
 'genneper-watermolen': ['genneper watermolen', 'genneper molen'],
 'collse-watermolen': ['collse'], 'sint-petruskerk': ['petruskerk', 'sint petrus'],
 'sint-lambertuskerk': ['lambertus'], 'steentjeskerk': ['steentjes'],
 'heilig-hartkerk': ['heilig hartkerk', 'ploegstraat'],
 'sint-theresiakerk': ['carmelitessenstraat 2'],
 'sint-martinuskerk': ['martinus'], 'paterskerk': ['paterskerk', 'augustijnenkerk'],
 'clarissenklooster': ['clarissen', 'kloostergang'], 'philips-observatorium': ['observatorium', 'sterrenwacht eindhoven'],
 'van-maerlantlyceum': ['maerlant'], 'gemeentelijke-hbs': ['gemeentelijke hbs'],
 'st-joriscollege': ['joriscollege'], 'w-hal-tue': ['w hal', 'w-hal'],
 'nutsschool-reigerlaan': ['reigerlaan', 'basisschool reigerlaan'],
 'mennen-poortgebouw': ['bergstraat 26', 'rijksmonument14628'],
 'kasteel-eckart': ['eckart'], 'sint-joriskerk': ['joriskerk', 'jorislaan'],
 'gerardus-majellakerk': ['gerardus'], 'villa-de-laak': ['de laak', 'delaak'],
 'tue-atlas': ['gebouw atlas'], 'tue-auditorium': ['auditorium van de th'],
 'bevrijdingsmonument': ['bevrijdingsmonument', 'plaquette in het ns station'],
 'oorlogsmonument-fellenoord': ['fellenoord-oorlogsmonument', 'fellenoord oorlogsmonument'],
 'raadhuis-tongelre': ['raadhuis tongelre'],
 'philips-nederland-gebouw': ['philips nederland', 'kantoorgebouw philips'],
 'eindhoven-airport-terminal': ['eindhoven airport'],
 'porthos-toren': ['porthos'],
 'winkelcentrum-woensel': ['winkelcentrum woensel', 'woens xl'],
 'haftalik-pazarlar': ['markt eindhoven', 'eindhovenmarkt', 'standbeeld frits philips', 'markt 23a'],
 'striatumseind': ['stratumseind'], 'de-bergen-horeca': ['rechtestraat', 'catharinastraat eindhoven'],
 'vershal-het-veem': ['veemgebouw'], 'kruisstraat-keent': ['kruisstraat'],
 'cafe-100-watt': ['100 watt'], 'heuvel-galerie': ['heuvel galerie', 'heuvelgalerie', 'glow festival eindhoven heuvel'],
 'berenkuil-street-art': ['berenkuil'],
}
# başlıkta eşleşme zorunlu (gürültülü havuzlar)
TITLE_ONLY = {'de-bergen-horeca', 'philips-stadion', 'effenaar', 'parktheater', 'hightech-campus',
              'herdgang', 'tue-auditorium', 'oude-toren-woensel', 'grote-markt', 'catharinaplein',
              'watertoren', 'molen-annemie', 'w-hal-tue', 'tue-atlas', 'porthos-toren'}

DISTRICT_POOLS = {
 'binnenstad': [('mah-binnenstad2', ['eindhoven - centrum', 'centrum 1803', 'markt eindhoven']), ('grote-markt', ['eindhoven markt', 'eindhovenmarkt', 'eindhoven centre'])],
 'de-bergen': [('de-bergen3', ['rechtestraat']), ('mah-de-bergen', ['bergen']), ('mah-de-bergen2', ['eindhoven'])],
 'strijp-s': [('mah-strijp-s', ['strijp'])],
 'philipsdorp': [('mah-philipsdorp', ['philipsdorp']), ('mah-philipsdorp2', ['philipsdorp', 'frederiklaan'])],
 'meerhoven': [('mah-meerhoven', ['meerhoven', 'meerr', 'zandrijk'])],
 'oud-woensel': [('mah-oud-woensel', ['eindhoven', 'woensel'])],
 'acht': [('mah-acht', ['acht'])],
 'roosten': [('mah-roosten2', ['roosten'])],
 'doornakkers': [('mah-doornakkers', ['eindhoven', 'doornakkers'])],
 'villapark': [('mah-villapark2', ['laak', 'villapark', 'parklaan'])],
 'karpen-koudenhoven': [('mah-karpen2', ['karpen', 'koudenhoven']), ('mah-karpen', ['karpen, 5631'])],
 'oud-stratum': [('mah-oud-stratum2', ['irisbuurt', 'witte dorp eindhoven', 'tuindorp eindhoven'])],
 'burghplan': [('mah-burghplan', ['burghplan'])],
 'leenderheide': [('mah-leenderheide', ['leenderheide', 'leendereide'])],
 'oud-gestel': [('clarissenklooster', ['clarissen', 'kloostergang']), ('mah-oud-gestel2', ['gestel'])],
 'hofke-tongelre': [('mah-hofke', ['hofke', 'tongelre'])],
}

COVERS = [
 ('kapak-skyline', ['kapak-skyline'], ['berenkuil eindhoven panorama'], 'Şehir panoraması (Berenkuil yönü)', False),
 ('kapak-merkez', ['grote-markt', 'mah-binnenstad2'], ['eindhoven centre', 'eindhovenmarkt', 'centrum 1803'], 'Şehir merkezi gündüz yaşamı', False),
 ('kapak-strijps', ['strijp-s', 'mah-strijp-s'], ['strijp s'], 'Strijp-S yaratıcı bölge', True),
 ('kapak-glow', ['kapak-glow', 'heuvel-galerie'], ['glow festival eindhoven', 'lighttowerduringglow', 'glow'], 'GLOW ışık festivali', True),
 ('kapak-doga', ['kapak-dogal'], ['autumn karpendonkse'], 'Şehrin yeşil yüzü: Karpendonkse Plas', False),
 ('kapak-endustri', ['kapak-endustri'], ['witte dame'], 'Endüstri mirası: Witte Dame', True),
 ('kapak-evoluon', ['next-nature-evoluon'], ['evoluon'], 'Evoluon kubbesi', True),
 ('kapak-stadion', ['philips-stadion2', 'philips-stadion'], ['philips stadion entrance', 'philips stadion - psv eindhoven'], 'Philips Stadion', True),
]

used_sha, used_title = set(), set()
selection = []

def pool_for(keys):
    out = []
    for k in keys:
        p = probes.get(k)
        if p:
            out.extend(p.get('usable', []))
    seen, res = set(), []
    for x in out:
        if x['title'] not in seen:
            seen.add(x['title']); res.append(x)
    return res

def match(x, kws, title_only):
    t = norm(x['title'])
    if any(k in t for k in kws):
        return True
    if title_only:
        return False
    hay = norm(t + ' ' + x['desc'])
    return any(k in hay for k in kws)

EXCLUDE_KW = {
 'genneper-parken': ['ijssportcentrum', 'indoor sportcentrum', 'tongelreep', 'high tech'],
}

def bad_file(x, slug=None):
    t = x['title'].lower()
    if 'cropped logo' in t:
        return True
    if t.endswith('.png'):
        return True
    if 'burning van abbe' in t:
        return True  # görsel üzerinde fotoğrafçı filigranı tespit edildi (sözleşme: filigranlı görsel kullanılmaz)
    if 'kleedkamer' in t:
        return True  # tabela/levha karesi; mekânın kendisini göstermiyor
    if 'het philips stadion img' in t:
        return True  # görsel doğrulamada tabela karesi olduğu görüldü
    for k in EXCLUDE_KW.get(slug or '', []):
        if k in t:
            return True
    return False

def take(pool, kws, n, title_only=False, slug=None):
    picks = []
    scored = [x for x in pool if match(x, kws, title_only) and not bad_file(x, slug)]
    scored.sort(key=lambda x: (0 if any(k in norm(x['title']) for k in kws) else 1,
                               0 if 'eindhoven' in norm(x['title'] + ' ' + x['desc']) else 1,
                               -(x['width'] or 0)))
    series = {}
    for x in scored:
        if x['sha1'] in used_sha or x['title'] in used_title:
            continue
        if (x['license'] or '').startswith('CC BY') and not (x['author'] or '').strip():
            continue  # atıf zorunlu lisanslarda fotoğrafçı belirsizse kullanma
        base = ' '.join(norm(x['title']).split()[:5])
        if series.get(base, 0) >= 2:
            continue
        series[base] = series.get(base, 0) + 1
        if (x['width'] or 0) < 800:
            continue
        picks.append(x)
        if len(picks) >= n:
            break
    for x in picks:
        used_sha.add(x['sha1']); used_title.add(x['title'])
    return picks

# 1) KAPAKLAR
for cid, pools, kws, cap, tonly in COVERS:
    pick = []
    for pk in pools:
        p = probes.get(pk)
        if p:
            pick = take(p.get('usable', []), kws, 1, tonly, cid)
            if pick:
                break
    if not pick:
        print('NO-COVER', cid)
        continue
    selection.append({'photo_id': f"eindhoven:foto:{cid}-01", 'role': 'Kapak', 'entry_id': None,
                      'media_key': cid, 'file': f"Fotoğraflar/eindhoven_{cid}_01",
                      'meta': pick[0], 'caption_hint': cap})

# 2) MAHALLELER
districts = json.load(open('districts_master.json', encoding='utf-8'))
for d in districts:
    slug = d['slug']
    pick = None
    for key, kws in DISTRICT_POOLS.get(slug, []):
        p = probes.get(key)
        if not p:
            continue
        got = take(p.get('usable', []), kws, 1, False, slug)
        if got:
            pick = got[0]; break
    if not pick:
        print('NO-DISTRICT', slug); continue
    selection.append({'photo_id': f"eindhoven:foto:mah-{slug}-01", 'role': 'Mekân',
                      'entry_id': f"eindhoven:mah-{slug}", 'media_key': f"mah-{slug}",
                      'file': f"Fotoğraflar/eindhoven_mah_{slug}_01", 'meta': pick})

# 3) MEKÂNLAR
BIG = {'van-abbemuseum', 'next-nature-evoluon', 'philips-stadion', 'strijp-s', 'hightech-campus',
       'sint-catharinakerk', 'paterskerk', 'nutsschool-reigerlaan', 'collse-watermolen',
       'striatumseind', 'sint-joriskerk', 'parktheater'}
places = json.load(open('places_master.json', encoding='utf-8'))
problems = []
for pl in places:
    slug = pl['slug']
    pool = pool_for(POOL_MAP.get(slug, [slug]))
    kws = KW.get(slug, [norm(pl['title'])])
    if slug in BIG:
        target = 5
    elif len(pool) >= 30:
        target = 4
    elif len(pool) >= 10:
        target = 3
    elif len(pool) >= 4:
        target = 2
    else:
        target = 1
    picks = take(pool, kws, target, slug in TITLE_ONLY, slug)
    if not picks:
        problems.append((slug, 'NO-PHOTO', len(pool)))
        continue
    for i, x in enumerate(picks, 1):
        selection.append({'photo_id': f"eindhoven:foto:{slug}-{i:02d}", 'role': 'Mekân',
                          'entry_id': f"eindhoven:{slug}", 'media_key': slug,
                          'file': f"Fotoğraflar/eindhoven_{slug}_{i:02d}", 'meta': x})

json.dump(selection, open('photo_selection.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
ven = [s for s in selection if s['role'] == 'Mekân' and not s['entry_id'].startswith('eindhoven:mah-')]
mah = [s for s in selection if s['role'] == 'Mekân' and s['entry_id'].startswith('eindhoven:mah-')]
kap = [s for s in selection if s['role'] == 'Kapak']
print(f"TOTAL {len(selection)} | venue {len(ven)} | district {len(mah)} | cover {len(kap)} | unique_venue={len(ven)+len(mah)}")
for p in problems:
    print('  SORUN:', p)
