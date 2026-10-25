. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$E = "$WORK\_is\foto_ek2"
$kod = @'
import json, pathlib
I = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
sel = {json.loads(l)["entry_id"] for l in open(I / "foto" / "selected.jsonl", encoding="utf-8") if l.strip()}
rows = {}
for f in [I / "foto" / "venues.jsonl", I / "foto_ek" / "venues.jsonl"]:
    for l in open(f, encoding="utf-8"):
        if l.strip():
            r = json.loads(l); rows[r["entry_id"]] = r
live = set()
for g in ("Mekânlar", "Mahalleler"):
    for p in (I / "data" / "parcalar").glob(g + ".*.jsonl"):
        live |= {json.loads(l)["entry_id"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}
miss = [rows[e] for e in sorted(live - sel) if e in rows]
with open(I / "foto_ek2" / "venues.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in miss:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
open(I / "foto_ek2" / "search.jsonl", "w").close()
print(json.dumps({"venues": len(miss), "not_in_plan": sorted(live - sel - set(rows))}))
'@
& $PY -c $kod
& $PY $TK\photo_sources.py --plan $E\venues.jsonl --search $E\search.jsonl --cache-dir $WORK\_is\foto\cache_alt --min-per-venue 3 --max-requests 300 --sources openverse,smithsonian,europeana
"sources exit $LASTEXITCODE"
& $PY $TK\photo_candidates.py from-search $E\search.jsonl --out $E\candidates.jsonl
& $PY $TK\photo_prefilter.py --candidates $E\candidates.jsonl --plan $E\venues.jsonl --out $E\decisions.json --shortlist 5
& $PY $TK\photo_previews.py $WORK\_is --decisions $E\decisions.json --items-out $E\items.jsonl --width 330 --out $E\onizleme.json | Select-Object -Last 1
& $PY $TK\contact_sheet.py --items $E\items.jsonl --out-dir $E\pafta --per-sheet 30 --cols 6 --dhash-threshold 5 | Select-Object -Last 1
