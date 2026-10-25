. C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\ortam.ps1
$E = "$WORK\_is\foto_ek"
$kod = @'
import json, pathlib
I = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
Q = {"hospital-de-las-cinco-llagas": "Q2983985", "convento-de-santa-ines": "Q10862989", "monasterio-de-san-clemente": "Q6021317",
     "real-fabrica-de-tabacos-rectorado": "Q2542555", "parroquia-de-san-jacinto": "Q22970093", "capilla-del-carmen-triana": "Q2376668",
     "iglesia-de-santa-maria-la-blanca": "Q5555137", "iglesia-de-san-pedro": "Q5911120"}
old = {json.loads(l)["entry_id"] for l in open(I / "foto" / "venues.jsonl", encoding="utf-8") if l.strip()}
rows = [json.loads(l) for l in open(I / "foto_ek" / "plan_tum.jsonl", encoding="utf-8") if l.strip()]
new = []
for r in rows:
    if r.get("entry_id") in old:
        continue
    q = Q.get((r.get("entry_id") or "").split(":")[-1])
    if q:
        r["wikidata"] = q
    new.append(r)
with open(I / "foto_ek" / "venues.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in new:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"new": [r.get("entry_id") for r in new]}))
'@
& $PY -c $kod
for ($i = 1; $i -le 20; $i++) {
  $o = "$(& $PY $TK\commons_search.py --plan $E\venues.jsonl --out $E\search.jsonl --cache-dir $WORK\_is\foto\cache --max-requests 400 --limit 25 --geo-max 5 2>&1 | Select-Object -Last 1)"
  "$i $($o.Substring(0, [Math]::Min(200, $o.Length)))"
  if ($o -notmatch 'resume_later') { break }
  Start-Sleep -Seconds 60
}
& $PY $TK\photo_candidates.py from-search $E\search.jsonl --out $E\candidates.jsonl
New-Item -ItemType Directory -Force $E\tur | Out-Null
& $PY $TK\photo_prefilter.py --candidates $E\candidates.jsonl --plan $E\venues.jsonl --out $E\decisions.json --shortlist 5
& $PY $TK\photo_previews.py $WORK\_is --decisions $E\decisions.json --items-out $E\items.jsonl --width 330 --out $E\onizleme.json | Select-Object -Last 1
& $PY $TK\contact_sheet.py --items $E\items.jsonl --out-dir $E\pafta --per-sheet 30 --cols 6 --dhash-threshold 5 | Select-Object -Last 1

