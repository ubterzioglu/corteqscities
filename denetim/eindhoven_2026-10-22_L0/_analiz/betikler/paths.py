import json,re,sys
from pathlib import Path
from collections import Counter
dump=Path(sys.argv[1]); pkg=Path(sys.argv[2])
pat=re.compile(r'(^[A-Za-z]:[\\/]|(?<![A-Za-z])[A-Za-z]:\\\\|file://|(^|[\\/])\.\.([\\/]|$)|temp_private|\\Users\\|/Users/|/home/|AppData)', re.I)
hits=[]
for f in dump.glob('*.jsonl'):
    for line in f.open(encoding='utf-8'):
        if not line.strip(): continue
        r=json.loads(line)
        for k,v in r.items():
            if isinstance(v,str) and pat.search(v): hits.append((f.stem,r.get('_row'),k,v[:140]))
print('excel_unsafe_hits',len(hits)); [print('  ',h) for h in hits[:10]]
# Teslimler text files: absolute local paths
c=Counter(); ex={}
for f in (pkg/'Teslimler').glob('*'):
    if f.is_file() and f.suffix.lower() in ('.json','.csv','.html','.txt'):
        t=f.read_text(encoding='utf-8',errors='replace')
        for m in re.finditer(r'([A-Za-z]:\\\\[^"\s,<]{0,80}|[A-Za-z]:\\[^"\s,<]{0,80}|[A-Za-z]:/[^"\s,<]{0,60}|temp_private[^"\s,<]{0,60}|/Users/[^"\s,<]{0,60})', t):
            s=m.group(0)
            if s.lower().startswith(('s:/','p:/')) : pass
            if re.match(r'^[A-Za-z]:/', s) and not re.match(r'^[A-Za-z]:/(?!/)', s): continue
            c[f.name]+=1; ex.setdefault(f.name,s)
print('teslimler_abs_path_hits',dict(c)); print(json.dumps(ex,ensure_ascii=False,indent=0)[:1500])
# backslash in Teslimler json paths
c2=Counter(); ex2={}
for f in (pkg/'Teslimler').glob('*.json'):
    t=f.read_text(encoding='utf-8',errors='replace')
    for m in re.finditer(r'"(Teslimler\\\\\\\\[^"]+|Fotoğraflar\\\\\\\\[^"]+|Lisans kanıtları\\\\\\\\[^"]+)"', t):
        c2[f.name]+=1; ex2.setdefault(f.name,m.group(1)[:100])
print('teslimler_json_backslash_paths',dict(c2)); print(ex2)
