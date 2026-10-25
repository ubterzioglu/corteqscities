import json, sys, collections, re
from pathlib import Path
OUT = Path(sys.argv[1])
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
cands = JL('_foto/candidates.jsonl'); fot = {p['photo_id']: p for p in JL('_dump/Fotoğraflar.jsonl')}; fk = {p['photo_id']: p for p in JL('_dump/FotoğrafKaynakları.jsonl')}
comp = []
for c in cands:
    pid = c['photo_id']; p = fot.get(pid, {}); s = fk.get(pid, {})
    comp.append({'photo_id': pid, 'entry_id': p.get('entry_id'), '_row': p.get('_row'), 'role': p.get('role'), 'file': p.get('file'), 'excel_license': p.get('license'), 'excel_license_url': p.get('license_url'), 'excel_author': p.get('author'), 'source_url': p.get('source_url'), 'author_url': s.get('author_url'), 'provenance_note': s.get('provenance_note'), 'commons_title': c.get('title'), 'commons_license': c.get('license'), 'commons_license_url': c.get('license_url'), 'usage_terms': c.get('usage_terms'), 'author_text': re.sub('<[^>]+>','',str(c.get('author_text') or ''))[:150], 'credit_text': re.sub('<[^>]+>','',str(c.get('credit_text') or ''))[:200], 'restrictions': c.get('restrictions'), 'copyrighted': c.get('copyrighted'), 'date_original': c.get('date_original'), 'description': re.sub('<[^>]+>','',str(c.get('description_text') or ''))[:200]})
(OUT/'_l'/'girdi'/'lisans_zinciri.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False)+'\n' for r in comp), encoding='utf-8')
own = sum(1 for c in comp if re.search(r'own work|trabajo propio|self-made', (c['credit_text'] or ''), re.I))
pd = [c['photo_id'] for c in comp if re.search(r'public domain|cc0|pd', str(c['commons_license']), re.I)]
flickr = [c['photo_id'] for c in comp if re.search(r'flickr|geograph|panoramio|openverse', (c['credit_text'] or '')+(c['source_url'] or ''), re.I)]
print(json.dumps({'n': len(comp), 'own_work': own, 'not_own_work': len(comp)-own, 'pd_cc0': pd, 'external_origin': flickr, 'commons_lic': dict(collections.Counter(c['commons_license'] for c in comp)), 'restrictions_nonempty': [c['photo_id'] for c in comp if c['restrictions']]}, ensure_ascii=False))
