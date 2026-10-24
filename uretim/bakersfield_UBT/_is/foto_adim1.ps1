. 'C:\temp_private\corteqs\0000_newera\uretim\bakersfield\_is\ortam.ps1'
New-Item -ItemType Directory -Force $WORK\_is\foto | Out-Null
& $PY $TK\photo_candidates.py plan-from-xlsx $WORK\_is\ara --out $WORK\_is\foto\venues.jsonl
Write-Host "### plan exit=$LASTEXITCODE"
& $PY -c @"
import json,sys,pathlib
isd=pathlib.Path(sys.argv[1])
qid={}
for l in (isd/'mekan'/'selected.jsonl').read_text(encoding='utf-8').splitlines():
    if l.strip():
        r=json.loads(l); qid[r['entry_id']]=r.get('qid','')
for l in (isd/'wikidata_dummy').read_text().splitlines() if (isd/'wikidata_dummy').exists() else []: pass
p=isd/'foto'/'venues.jsonl'
rows=[json.loads(l) for l in p.read_text(encoding='utf-8').splitlines() if l.strip()]
n=0
for r in rows:
    q=qid.get(r.get('entry_id'),'')
    if q: r['wikidata']=q; n+=1
p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows),encoding='utf-8')
print(json.dumps({'venues':len(rows),'with_qid':n}))
"@ "$WORK\_is"
& $PY $TK\commons_search.py --plan $WORK\_is\foto\venues.jsonl --out $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache --max-requests 1500 --limit 25 --geo-max 5
Write-Host "### search exit=$LASTEXITCODE"
& $PY $TK\photo_candidates.py from-search $WORK\_is\foto\search.jsonl --out $WORK\_is\foto\candidates.jsonl
Write-Host "### from-search exit=$LASTEXITCODE"
New-Item -ItemType Directory -Force $WORK\_is\foto\tur1 | Out-Null
& $PY $TK\photo_prefilter.py --candidates $WORK\_is\foto\candidates.jsonl --plan $WORK\_is\foto\venues.jsonl --out $WORK\_is\foto\tur1\decisions.json --shortlist 4
Write-Host "### prefilter exit=$LASTEXITCODE"
Write-Host "### BITTI"
