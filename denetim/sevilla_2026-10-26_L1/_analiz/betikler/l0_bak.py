"""L0 çıktılarından kısa özet (yalnız okur)."""
import json, sys, collections
from pathlib import Path
OUT = Path(sys.argv[1])
def L(p): return json.loads((OUT/p).read_text(encoding='utf-8-sig'))
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]

kk = L('kanit-kapsami.json')
print('C4/eksik:', [o for o in kk['olcutler'] if o['id'] in kk.get('eksik', [])])
d = L('_foto/decisions.json')
print('decisions summary:', d.get('summary'))
reasons = collections.Counter(r for x in d['decisions'] for r in x.get('reasons', []))
print('reasons:', dict(reasons))
print('non-keep:', [(x['candidate_id'], x['decision'], x.get('reasons')) for x in d['decisions'] if x['decision'] != 'keep'][:60])
h = L('_foto/hazirlik.json')
print('hazirlik keys:', list(h.keys()))
for k in ('ayni_sha',):
    v = h.get(k)
    if isinstance(v, dict):
        for kk2, vv in v.items():
            print(' ', kk2, (vv if not isinstance(vv, list) else vv[:6]), '...' if isinstance(vv, list) and len(vv) > 6 else '')
dc = L('_foto/dhash-ciftleri.json')
print('dhash keys:', list(dc.keys()), {k: (len(v) if isinstance(v, list) else v) for k, v in dc.items()})
print('K63_aday:', dc.get('K63_aday', [])[:20])
cand = JL('_foto/candidates.jsonl')
print('candidates:', len(cand))
inv = L('dosya-envanteri.json')
print('inventory summary:', {k: v for k, v in inv.items() if k != 'files'} if isinstance(inv, dict) else None)
