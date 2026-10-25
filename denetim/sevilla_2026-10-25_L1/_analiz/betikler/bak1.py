import json, collections, sys
from pathlib import Path
OUT = Path(sys.argv[1])
def L(p): return json.loads((OUT/p).read_text(encoding='utf-8-sig'))
def JL(p): return [json.loads(l) for l in (OUT/p).read_text(encoding='utf-8').splitlines() if l.strip()]
dec = L('_foto/decisions.json')
print('FLAGS:', json.dumps([{k:d.get(k) for k in ('candidate_id','entry_id','decision','reasons')} for d in dec['decisions'] if d['decision']!='keep'], ensure_ascii=False))
print('EWS:', dec['summary'].get('entries_without_shortlist'))
h = L('_foto/hazirlik.json')
print('K05 groups:', len(h['ayni_sha']['K05']), json.dumps(h['ayni_sha']['K05'][:3], ensure_ascii=False)[:600])
print('eksik_alanli:', h.get('eksik_alanli_foto'))
imp = L('impact.json')
print('IMPACT keys:', list(imp.keys()))
print('IMPACT changes sample:', json.dumps({k: imp.get(k) for k in ('summary','changes') if k in imp}, ensure_ascii=False)[:1500])
val = L('validation-audit.json')
print('VAL warning classes:', json.dumps(val.get('warning_classes') or val['structure'].get('warning_classes'), ensure_ascii=False)[:800])
print('VAL counts:', json.dumps(val['structure'].get('counts'), ensure_ascii=False))
print('VAL minimum/target:', json.dumps(val['structure'].get('minimum')), json.dumps(val['structure'].get('target')))
urls = L('url-checks.json')
print('HOMEPAGE_ONLY:', json.dumps([{k:u.get(k) for k in ('url','rows','relations','verdict')} for u in urls['urls'] if 'homepage_only' in (u.get('flags') or [])], ensure_ascii=False)[:2000])
print('CROSS_HOST:', json.dumps([{k:u.get(k) for k in ('url','final_url','verdict')} for u in urls['urls'] if 'cross_host_redirect' in (u.get('flags') or [])], ensure_ascii=False)[:1200])
cs = L('claim-script.json')
print('CLAIM keys:', list(cs.keys()), 'results n:', len(cs.get('results',[])))
r0 = cs['results'][0]; print('CLAIM result sample keys:', list(r0.keys())); print(json.dumps(r0, ensure_ascii=False)[:700])
yan = {y['entry_id']: y for y in JL('_dump/Yanıtlar.jsonl')}
print('YANIT keys:', list(next(iter(yan.values())).keys()))
by_entry = collections.Counter(r['entry_id'] for r in cs['results'] if r['result']!='supported')
by_topic = collections.Counter(); ent_topic=collections.Counter()
for e,n in by_entry.items():
    t = yan.get(e,{}).get('topic_id','?'); by_topic[t]+=n; ent_topic[t]+=1
print('UNSUPPORTED by topic (claims):', dict(by_topic)); print('entries w/ unsupported by topic:', dict(ent_topic))
print('entries with any claim:', len({r['entry_id'] for r in cs['results']}), 'entries with unsupported:', len(by_entry))
tq = L('text-quality.json'); print('TQ keys:', list(tq.keys())); print('hedges:', tq.get('hedges',{}).get('count') if isinstance(tq.get('hedges'),dict) else tq.get('hedges'), 'evasive:', (tq.get('evasive_answers') or {}).get('count') if isinstance(tq.get('evasive_answers'),dict) else None)
print('repeated_sentences sample:', json.dumps((tq.get('repeated_sentences') or [])[:5] if isinstance(tq.get('repeated_sentences'),list) else tq.get('repeated_sentences'), ensure_ascii=False)[:800])
