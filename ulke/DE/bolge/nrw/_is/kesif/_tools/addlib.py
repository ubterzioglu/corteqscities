import sys, json, re, os
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, strip

BASE = r'C:\temp_private\corteqs\0000_newera\ulke\DE\bolge\nrw\_is\kesif'


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def add(topic, rows):
    path = os.path.join(BASE, topic, 'selected.jsonl')
    os.makedirs(os.path.dirname(path), exist_ok=True)
    existing = set()
    if os.path.exists(path):
        with open(path, encoding='utf-8') as f:
            for ln in f:
                if ln.strip():
                    existing.add(json.loads(ln)['url'])
    ok = []
    for r in rows:
        if r['url'] in existing:
            print('ZATEN VAR', r['url']); continue
        try:
            raw, final = get(r['url'])
        except Exception as e:
            print('ERISIM HATA', r['url'], repr(e)[:150]); continue
        txt = norm(strip(raw))
        miss = [m for m in r['must_contain'] if norm(m) not in txt]
        if miss:
            print('EKSIK must_contain', r['url'], miss); continue
        ok.append(r)
        print('OK', r['url'], r['cards'])
    with open(path, 'a', encoding='utf-8') as f:
        for r in ok:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')
    print('yazildi', len(ok), '/', len(rows))
