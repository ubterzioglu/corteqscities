import json, sys, urllib.request, urllib.parse
from pathlib import Path
OUT = Path(sys.argv[1])
c = json.loads((OUT / '_foto' / 'candidates.jsonl').read_text(encoding='utf-8').splitlines()[0])
print({k: c.get(k) for k in ('photo_id', 'commons_file', 'title', 'thumb_url', 'original_url', 'source_url')})
for url in [c.get('thumb_url'), 'https://commons.wikimedia.org/wiki/Special:FilePath/' + urllib.parse.quote(str(c.get('title') or '').split('File:', 1)[-1].replace(' ', '_')) + '?width=320']:
    if not url:
        continue
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'CorteqsAudit/1.0 (denetim; corteqssocial@gmail.com)'})
        with urllib.request.urlopen(req, timeout=20) as r:
            print('OK', r.status, r.geturl()[:120], len(r.read()))
    except Exception as e:
        print('HATA', url[:120], repr(e)[:200])
