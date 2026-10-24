import json,sys
from pathlib import Path
pkg=Path(sys.argv[1]); out=Path(sys.argv[2])
p=json.loads((pkg/'Teslimler'/'dosya-envanteri.json').read_text(encoding='utf-8'))
mine=json.loads((out/'dosya-envanteri.json').read_text(encoding='utf-8'))
print('pkg inventory keys:', list(p.keys())[:12])
for k in ('summary','totals'):
    if k in p: print('pkg',k, json.dumps(p[k],ensure_ascii=False)[:400])
pf={f['path']:f for f in p.get('files',[])}
mf={f['path']:f for f in mine['files']}
only_mine=sorted(set(mf)-set(pf)); only_pkg=sorted(set(pf)-set(mf))
diff=[x for x in set(mf)&set(pf) if mf[x].get('sha256')!=pf[x].get('sha256')]
print('files pkg-inventory:',len(pf),'audit-inventory:',len(mf))
print('only in audit inventory:',len(only_mine), only_mine[:12])
print('only in pkg inventory:',len(only_pkg), only_pkg[:12])
print('sha differs:',len(diff), sorted(diff)[:12])
k=json.loads((pkg/'Teslimler'/'paket-kontrol-v7.json').read_text(encoding='utf-8'))
print('paket-kontrol keys:', list(k.keys())[:20])
print(json.dumps({kk:(v if not isinstance(v,(list,dict)) else type(v).__name__+str(len(v))) for kk,v in k.items()},ensure_ascii=False)[:1200])
