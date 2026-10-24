import json,sys,csv,io
from pathlib import Path
pkg=Path(sys.argv[1]); dump=Path(sys.argv[2])
pp=json.loads((pkg/'Teslimler'/'photo-provenance-v7.json').read_text(encoding='utf-8'))
print(type(pp).__name__, list(pp.keys())[:10] if isinstance(pp,dict) else len(pp))
items = pp.get('photos') if isinstance(pp,dict) else pp
if items is None:
    for k,v in pp.items():
        if isinstance(v,list): items=v; print('list key',k); break
print('n items',len(items)); print('item keys',list(items[0].keys()))
def load(n): return [json.loads(l) for l in open(dump/f'{n}.jsonl',encoding='utf-8') if l.strip()]
ph={r['photo_id']:r for r in load('Fotoğraflar')}; fk={r['photo_id']:r for r in load('FotoğrafKaynakları')}; ev={r['photo_id']:r for r in load('Kanıtlar')}
diffs=[]
for it in items:
    pid=it.get('photo_id')
    if pid not in ph: diffs.append((pid,'excelde yok')); continue
    x={**ev.get(pid,{}),**fk.get(pid,{}),**ph[pid]}
    for k,v in it.items():
        if k in x and str(x[k]).strip()!=str(v).strip() and not isinstance(v,(dict,list)):
            diffs.append((pid,k,str(x[k])[:60],str(v)[:60]))
print('photo-provenance vs excel field diffs:',len(diffs))
from collections import Counter
print(Counter(d[1] for d in diffs).most_common(10))
for d in diffs[:6]: print('  ',d)
# attribution csv
t=(pkg/'Teslimler'/'fotograf-atiflari-v7.csv').read_text(encoding='utf-8-sig')
rows=list(csv.DictReader(io.StringIO(t)))
print('csv rows',len(rows),'cols',list(rows[0].keys()))
d2=[]
for r in rows:
    pid=r.get('photo_id')
    if pid not in ph: d2.append((pid,'excelde yok')); continue
    x={**ev.get(pid,{}),**fk.get(pid,{}),**ph[pid]}
    for k,v in r.items():
        if k in x and str(x[k]).strip()!=str(v).strip():
            d2.append((pid,k,str(x[k])[:60],str(v)[:60]))
print('csv vs excel diffs',len(d2)); print(Counter(d[1] for d in d2).most_common(10)); [print('  ',d) for d in d2[:5]]
