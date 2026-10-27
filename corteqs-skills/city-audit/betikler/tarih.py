import json, sys, re, collections
from pathlib import Path
OUT = Path(sys.argv[1])
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
kay = {k['source_id']: k for k in JL('_dump/Kaynaklar.jsonl')}
bag = collections.defaultdict(list)
for b in JL('_dump/Bağlantılar.jsonl'): bag[b['entry_id']].append(b)
out = {'src_after_review': [], 'link_after_review': []}
for sheet in ('Yanıtlar','Mekânlar','Mahalleler','Rotalar','Sözlük'):
    for r in JL(f'_dump/{sheet}.jsonl'):
        rv = str(r.get('reviewed_on') or '')[:10]; eid = r.get('entry_id') or r.get('route_id') or r.get('term_id')
        for sid in re.split(r'[\n;|]', str(r.get('source_ids',''))):
            sid = sid.strip()
            if sid in kay and str(kay[sid].get('checked_on') or '')[:10] > rv: out['src_after_review'].append({'sheet': sheet, 'row': r['_row'], 'id': eid, 'reviewed_on': rv, 'source': sid, 'checked_on': str(kay[sid]['checked_on'])[:10]})
        for b in bag.get(eid, []):
            if str(b.get('checked_on') or '')[:10] > rv: out['link_after_review'].append({'sheet': sheet, 'row': r['_row'], 'id': eid, 'reviewed_on': rv, 'link_row': b['_row'], 'checked_on': str(b['checked_on'])[:10]})
sehir = JL('_dump/Şehir.jsonl')[0]
out['sehir_dates'] = {k: sehir.get(k) for k in ('reviewed_on','source_checked_on','coordinate_checked_on') if k in sehir}
(OUT/'_analiz'/'tarih-sirasi.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
print(json.dumps({'src_after_review': len(out['src_after_review']), 'link_after_review': len(out['link_after_review']), 'ornek': (out['src_after_review']+out['link_after_review'])[:5], 'sehir': out['sehir_dates']}, ensure_ascii=False))
