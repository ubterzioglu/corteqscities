. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$qid = @'
import json, pathlib, unicodedata, re
I = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
q = {}
for f in ["selected.jsonl", "selected_ek.jsonl"]:
    for l in open(I / "mekan" / f, encoding="utf-8"):
        if l.strip():
            r = json.loads(l)
            if r.get("qid"):
                q[r["entry_id"]] = r["qid"]
def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()
pool = {}
for l in open(I / "mekan" / "wikidata_aday.jsonl", encoding="utf-8"):
    r = json.loads(l)
    if any(t in (r.get("types") or "") for t in ("neighborhood", "city district")) and r.get("name"):
        pool.setdefault(norm(r["name"]), r["qid"])
p = I / "foto" / "venues.jsonl"
rows = [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
n = 0
for r in rows:
    eid = r.get("entry_id")
    w = q.get(eid)
    if not w:
        slug = (eid or "").split(":")[-1].replace("-", " ")
        w = pool.get(norm(slug)) or pool.get(norm(slug.replace("cevresi", "").replace(" ve ", " ")))
    if w:
        r["wikidata"] = w; n += 1
with open(p, "w", encoding="utf-8", newline="\n") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"rows": len(rows), "with_qid": n}))
'@
& $PY -c $qid
& $PY $TK\commons_search.py --plan $WORK\_is\foto\venues.jsonl --out $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache --max-requests 1500 --limit 25 --geo-max 5
"commons exit $LASTEXITCODE"
& $PY $TK\photo_sources.py --plan $WORK\_is\foto\venues.jsonl --search $WORK\_is\foto\search.jsonl --cache-dir $WORK\_is\foto\cache_alt --min-per-venue 3 --max-requests 400 --sources openverse,smithsonian,europeana
"sources exit $LASTEXITCODE"
& $PY $TK\photo_candidates.py from-search $WORK\_is\foto\search.jsonl --out $WORK\_is\foto\candidates.jsonl
"cand exit $LASTEXITCODE"
