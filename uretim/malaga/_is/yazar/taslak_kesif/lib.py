import json, re, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r'C:\temp_private\corteqs\0000_newera\uretim\malaga'
PAR = W + r'\_is\data\parcalar'
YAN = PAR + r'\Yanıtlar.kesif.jsonl'
BAG = PAR + r'\Bağlantılar.kesif.jsonl'
CLM = W + r'\_is\claims\kesif.jsonl'
TODAY = '2026-10-25'

SRC = {}
for l in open(W + r'\_is\yazar\kesif_kaynaklar.jsonl', encoding='utf-8'):
    d = json.loads(l)
    SRC[d['source_id'].split(':')[-1]] = d
TXT = {}


def txt(n):
    if n not in TXT:
        t = open(SRC[n]['text_file'], encoding='utf-8').read()
        TXT[n] = re.sub(r'\s+', ' ', t).lower()
    return TXT[n]


def sid(n):
    return SRC[n]['source_id']


def norm(q):
    return re.sub(r'\s+', ' ', q).lower()


KEYS = ['entry_id', 'city_id', 'slug', 'title', 'subtitle', 'summary', 'keywords', 'stages', 'source_ids',
        'reviewed_on', 'order', 'featured', 'editorial_status', 'topic_id', 'steps', 'documents', 'timing',
        'cost', 'note', 'visual_json']


def existing_slugs():
    out = set()
    import glob
    for f in glob.glob(PAR + r'\Yanıtlar.*.jsonl'):
        for l in open(f, encoding='utf-8'):
            d = json.loads(l)
            out.add(d['slug'])
            out.add(d['title'].casefold())
    return out


def add(cards):
    """cards: list of dict(slug,title,subtitle,summary,keywords,stages,src[list],order,featured,steps[list],
    documents[list],timing,cost,note,links[(label,srckey)],claims[(field,claim,value,unit,period,srckey,quote)])"""
    ex = existing_slugs()
    ys, bs, cs = [], [], []
    ok = True
    for c in cards:
        slug = c['slug']
        if slug in ex or c['title'].casefold() in ex:
            print('DUP', slug); ok = False
        ex.add(slug); ex.add(c['title'].casefold())
        if len(c['title']) > 180 or len(c['subtitle']) > 160 or len(slug) > 120:
            print('LEN', slug, len(c['title']), len(c['subtitle'])); ok = False
        if not (2 <= len(c['steps']) <= 7):
            print('STEPS', slug); ok = False
        if len(c['src']) > 2 or len(c['links']) > 2:
            print('LIMITS', slug); ok = False
        eid = 'malaga:' + slug
        row = {
            'entry_id': eid, 'city_id': 'malaga', 'slug': slug, 'title': c['title'], 'subtitle': c['subtitle'],
            'summary': c['summary'], 'keywords': c['keywords'], 'stages': c['stages'],
            'source_ids': ';'.join(sid(n) for n in c['src']), 'reviewed_on': TODAY, 'order': c['order'],
            'featured': c['featured'], 'editorial_status': 'Taslak', 'topic_id': 'malaga:kesif',
            'steps': '\n'.join(c['steps']), 'documents': '\n'.join(c.get('documents', [])),
            'timing': c.get('timing', ''), 'cost': c.get('cost', ''), 'note': c.get('note', ''), 'visual_json': ''}
        ys.append(row)
        for i, (label, k) in enumerate(c['links'], 1):
            bs.append({'action_id': 'malaga:action:%s-%d' % (slug, i), 'city_id': 'malaga', 'entry_id': eid,
                       'label': label, 'url': SRC[k]['url'], 'checked_on': TODAY, 'order': i})
        alltxt = ''
        for i, (field, claim, value, unit, period, k, quote) in enumerate(c['claims'], 1):
            if k not in c['src']:
                print('CLAIM SRC NOT IN CARD', slug, i, k); ok = False
            if norm(quote) not in txt(k):
                print('QUOTE MISS', slug, i, quote); ok = False
            if len(quote) > 200:
                print('QUOTE LONG', slug, i); ok = False
            alltxt += ' ' + claim + ' ' + value + ' ' + quote
            cs.append({'claim_id': 'C-%s-%d' % (slug, i), 'entry_id': eid, 'field': field, 'claim': claim,
                       'value': value, 'unit': unit, 'period': period, 'source_id': sid(k), 'url': SRC[k]['url'],
                       'quote': quote})
        body = ' '.join([c['title'], c['subtitle'], c['summary'], c['timing'], c.get('cost', ''), c.get('note', '')] + c['steps'] + c.get('documents', []))
        nums = set(re.findall(r'\d+(?:[.,:]\d+)?', body))
        miss = [n for n in nums if n not in alltxt.replace(',', ',') and n.replace('.', ',') not in alltxt and n.replace(',', '.') not in alltxt]
        if miss:
            print('NUM?', slug, sorted(miss))
        if 'siz' in re.findall(r'\b(?:siz|sizin|size)\b', body.lower()):
            print('SIZ', slug)
    if not ok:
        print('ABORT - not written')
        return
    with open(YAN, 'a', encoding='utf-8', newline='\n') as f:
        for r in ys:
            f.write(json.dumps({k: r[k] for k in KEYS}, ensure_ascii=False) + '\n')
    with open(BAG, 'a', encoding='utf-8', newline='\n') as f:
        for r in bs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(CLM, 'a', encoding='utf-8', newline='\n') as f:
        for r in cs:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('WROTE', len(ys), 'cards', len(bs), 'links', len(cs), 'claims')
