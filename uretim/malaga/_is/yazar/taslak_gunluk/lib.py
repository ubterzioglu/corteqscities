import json, re, os, sys

W = r'C:\temp_private\corteqs\0000_newera\uretim\malaga'
PAR = W + r'\_is\data\parcalar'
YAN = PAR + r'\Yanıtlar.gunluk.jsonl'
BAG = PAR + r'\Bağlantılar.gunluk.jsonl'
CLM = W + r'\_is\claims\gunluk.jsonl'
TODAY = '2026-10-25'
YKEYS = ['entry_id','city_id','slug','title','subtitle','summary','keywords','stages','source_ids','reviewed_on','order','featured','editorial_status','topic_id','steps','documents','timing','cost','note','visual_json']

def norm(s):
    return re.sub(r'\s+', ' ', s).strip().lower()

_src = {}
for l in open(W + r'\_is\kaynak_dizini.jsonl', encoding='utf-8'):
    if l.strip():
        j = json.loads(l)
        _src[j['source_id']] = j

def text_of(sid):
    j = _src[sid]
    return norm(open(j['text_file'], encoding='utf-8').read())

def read_lines(path):
    if not os.path.exists(path):
        return []
    return [l.rstrip('\n') for l in open(path, encoding='utf-8') if l.strip()]

def build(cards):
    """cards: list of dict(slug,title,subtitle,summary,keywords,stages,sources,order,featured,steps,documents,timing,cost,note,links,claims)"""
    mine = {'malaga:' + c['slug'] for c in cards}
    def keep(lines):
        out = []
        for l in lines:
            if json.loads(l)['entry_id'] not in mine:
                out.append(l)
        return out
    yl, bl, cl = keep(read_lines(YAN)), keep(read_lines(BAG)), keep(read_lines(CLM))
    errs = 0
    for c in cards:
        eid = 'malaga:' + c['slug']
        if len(c['title']) > 180 or len(c['subtitle']) > 160:
            print('LEN', c['slug'], len(c['title']), len(c['subtitle'])); errs += 1
        if len(c['sources']) > 2 or len(c['links']) > 2:
            print('TOO MANY', c['slug']); errs += 1
        row = {
            'entry_id': eid, 'city_id': 'malaga', 'slug': c['slug'], 'title': c['title'],
            'subtitle': c['subtitle'], 'summary': c['summary'], 'keywords': c['keywords'],
            'stages': c['stages'], 'source_ids': ';'.join(c['sources']), 'reviewed_on': TODAY,
            'order': c['order'], 'featured': c['featured'], 'editorial_status': 'Taslak',
            'topic_id': 'malaga:gunluk', 'steps': '\n'.join(c['steps']),
            'documents': '\n'.join(c.get('documents', [])), 'timing': c.get('timing', ''),
            'cost': c.get('cost', ''), 'note': c.get('note', ''), 'visual_json': ''}
        assert list(row.keys()) == YKEYS
        yl.append(json.dumps(row, ensure_ascii=False))
        for n, (label, url) in enumerate(c['links'], 1):
            bl.append(json.dumps({'action_id': f"malaga:action:{c['slug']}-{n}", 'city_id': 'malaga',
                                  'entry_id': eid, 'label': label, 'url': url, 'checked_on': TODAY, 'order': n}, ensure_ascii=False))
        for n, (field, claim, value, unit, period, sid, quote) in enumerate(c['claims'], 1):
            if sid not in c['sources']:
                print('CLAIM SRC NOT IN CARD', c['slug'], n, sid); errs += 1
            if norm(quote) not in text_of(sid):
                print('QUOTE MISS', c['slug'], n, quote[:70]); errs += 1
            if len(quote) > 200:
                print('QUOTE LONG', c['slug'], n); errs += 1
            cl.append(json.dumps({'claim_id': f"C-{c['slug']}-{n}", 'entry_id': eid, 'field': field, 'claim': claim,
                                  'value': value, 'unit': unit, 'period': period, 'source_id': sid,
                                  'url': _src[sid]['url'], 'quote': quote}, ensure_ascii=False))
        for label, url in c['links']:
            urls = {j['url'] for j in _src.values()}
            if url not in urls:
                print('URL NOT IN DIR', c['slug'], url); errs += 1
    if errs:
        print('ERRORS', errs); sys.exit(1)
    for path, lines in ((YAN, yl), (BAG, bl), (CLM, cl)):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write('\n'.join(lines) + '\n')
    print('OK', len(cards), 'cards;', len(yl), 'rows in Yanitlar')
