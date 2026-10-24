import json,sys,hashlib
a=json.load(open(sys.argv[1],encoding='utf-8')); b=json.load(open(sys.argv[2],encoding='utf-8'))
fa={f['path']:f['sha256'] for f in a['files']}; fb={f['path']:f['sha256'] for f in b['files']}
added=sorted(set(fb)-set(fa)); removed=sorted(set(fa)-set(fb)); changed=sorted(p for p in set(fa)&set(fb) if fa[p]!=fb[p])
def digest(m): return hashlib.sha256('\n'.join(f'{p}\t{m[p]}' for p in sorted(m)).encode('utf-8')).hexdigest()
print(json.dumps({"start_files":len(fa),"end_files":len(fb),"added":added,"removed":removed,"changed":changed,
 "start_list_digest":digest(fa),"end_list_digest":digest(fb),"identical":fa==fb,
 "xlsx_sha_start":fa.get('CITY-039_eindhoven_v001.xlsx'),"xlsx_sha_end":fb.get('CITY-039_eindhoven_v001.xlsx')},ensure_ascii=False,indent=1))
