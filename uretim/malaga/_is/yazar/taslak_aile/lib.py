import json, re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
W = r'C:\temp_private\corteqs\0000_newera\uretim\malaga\_is'
P = W + r'\data\parcalar'
CL = W + r'\claims\aile.jsonl'
TARIH = '2026-10-25'
KEYS = ['entry_id','city_id','slug','title','subtitle','summary','keywords','stages','source_ids','reviewed_on','order','featured','editorial_status','topic_id','steps','documents','timing','cost','note','visual_json']

SRC = {}
for l in open(W + r'\kaynak_dizini.jsonl', encoding='utf-8'):
    d = json.loads(l)
    SRC[d['source_id']] = d
for l in open(W + r'\yazar\aile_kaynaklar.jsonl', encoding='utf-8'):
    d = json.loads(l)
    SRC.setdefault(d['source_id'], d)

def norm(s):
    return re.sub(r'\s+', ' ', s).strip().lower()

_text = {}
def text(sid):
    if sid not in _text:
        _text[sid] = norm(open(SRC[sid]['text_file'], encoding='utf-8').read())
    return _text[sid]

def url(sid):
    return SRC[sid]['url']

def build(card, order):
    """card: dict with slug,title,subtitle,summary,keywords,stages,sids(list),featured,steps(list),documents(list),timing,cost,note,links(list of (label,sid)),claims(list of (field,claim,value,unit,period,sid,quote))"""
    slug = card['slug']
    eid = 'malaga:' + slug
    assert len(card['sids']) <= 2 and len(card['links']) <= 2 and 1 <= len(card['links'])
    assert len(card['title']) <= 180 and len(card['subtitle']) <= 160 and len(slug) <= 120, slug
    assert 2 <= len(card['steps']) <= 7, slug
    assert not any(x.startswith('=') for x in [card['title'], card['summary']] + card['steps'])
    row = {
        'entry_id': eid, 'city_id': 'malaga', 'slug': slug, 'title': card['title'], 'subtitle': card['subtitle'],
        'summary': card['summary'], 'keywords': card['keywords'], 'stages': card['stages'],
        'source_ids': ';'.join(card['sids']), 'reviewed_on': TARIH, 'order': order, 'featured': card.get('featured', 'Hayır'),
        'editorial_status': 'Taslak', 'topic_id': 'malaga:aile', 'steps': '\n'.join(card['steps']),
        'documents': '\n'.join(card.get('documents', [])), 'timing': card.get('timing', ''), 'cost': card.get('cost', ''),
        'note': card.get('note', ''), 'visual_json': ''}
    assert list(row.keys()) == KEYS
    links = []
    for i, (label, sid) in enumerate(card['links'], 1):
        links.append({'action_id': f'malaga:action:{slug}-{i}', 'city_id': 'malaga', 'entry_id': eid, 'label': label,
                      'url': url(sid), 'checked_on': TARIH, 'order': i})
    claims = []
    for i, (field, claim, value, unit, period, sid, quote) in enumerate(card['claims'], 1):
        assert sid in card['sids'], (slug, sid)
        assert len(quote) <= 200, (slug, i, len(quote))
        if norm(quote) not in text(sid):
            raise SystemExit(f'QUOTE MISS {slug} #{i}: {quote[:80]}')
        claims.append({'claim_id': f'C-{slug}-{i}', 'entry_id': eid, 'field': field, 'claim': claim, 'value': value,
                       'unit': unit, 'period': period, 'source_id': sid, 'url': url(sid), 'quote': quote})
    return row, links, claims

def existing_slugs():
    s = set()
    for l in open(P + r'\Yanıtlar.aile.jsonl', encoding='utf-8'):
        s.add(json.loads(l)['slug'])
    return s

def append(cards, start_order):
    ex = existing_slugs()
    out = []
    for i, c in enumerate(cards):
        assert c['slug'] not in ex, c['slug']
        out.append(build(c, start_order + i))
    with open(P + r'\Yanıtlar.aile.jsonl', 'a', encoding='utf-8', newline='\n') as f:
        for r, _, _ in out:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    with open(P + r'\Bağlantılar.aile.jsonl', 'a', encoding='utf-8', newline='\n') as f:
        for _, ls, _ in out:
            for x in ls:
                f.write(json.dumps(x, ensure_ascii=False) + '\n')
    with open(CL, 'a', encoding='utf-8', newline='\n') as f:
        for _, _, cs in out:
            for x in cs:
                f.write(json.dumps(x, ensure_ascii=False) + '\n')
    print('appended', len(out), 'cards;', sum(len(c) for _, _, c in out), 'claims')
