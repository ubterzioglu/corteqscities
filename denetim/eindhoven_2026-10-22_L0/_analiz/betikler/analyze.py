"""L0 cross-checks on audit outputs (read-only on PKG). Prints a JSON summary to stdout."""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(sys.argv[1])
PKG = Path(sys.argv[2])
DUMP = OUT / "_dump"


def load(name):
    p = DUMP / f"{name}.jsonl"
    with p.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


inv = json.loads((OUT / "dosya-envanteri.json").read_text(encoding="utf-8"))
_inv_raw = {f["path"]: f for f in inv["files"]}


class _InvLookup(dict):
    """Lookup that tolerates backslash separators (recorded separately as a portability finding)."""

    def get(self, key, default=None):
        if key is None:
            return default
        return _inv_raw.get(str(key).replace("\\", "/"), default)


inv_by_path = _InvLookup()
places, districts = load("Mekânlar"), load("Mahalleler")
photos, prov, evid = load("Fotoğraflar"), load("FotoğrafKaynakları"), load("Kanıtlar")
answers, topics, links = load("Yanıtlar"), load("Konular"), load("Bağlantılar")
sources, routes, gloss, steps, pagef = load("Kaynaklar"), load("Rotalar"), load("Sözlük"), load("Adımlar"), load("SayfaAlanları")
res = {}

# K22: photo coverage per place/district
photo_entries = Counter(p["entry_id"] for p in photos if p.get("entry_id"))
res["places_without_photo"] = [{"entry_id": r["entry_id"], "row": r["_row"], "title": r["title"], "group": r["group"]}
                               for r in places if photo_entries[r["entry_id"]] == 0]
res["districts_without_photo"] = [{"entry_id": r["entry_id"], "row": r["_row"], "title": r["title"]}
                                  for r in districts if photo_entries[r["entry_id"]] == 0]
res["places_with_photo"] = sum(1 for r in places if photo_entries[r["entry_id"]] > 0)
res["districts_with_photo"] = sum(1 for r in districts if photo_entries[r["entry_id"]] > 0)
res["group_photo_gap"] = Counter(x["group"] for x in res["places_without_photo"])
res["group_counts"] = Counter(r["group"] for r in places)
res["photos_per_entry_hist"] = Counter(photo_entries.values())

# K19 counts: answers per topic
tcount = Counter(a["topic_id"] for a in answers)
res["answers_per_topic"] = {t["topic_id"]: tcount.get(t["topic_id"], 0) for t in topics}

# K80/K114/K58: provenance vs inventory
prob = []
dims = Counter()
for r in prov:
    pid = r["photo_id"]
    of, wf = r["original_file"], r["web_file"]
    io, iw = inv_by_path.get(of), inv_by_path.get(wf)
    if io is None:
        prob.append((pid, "original_file yok", of))
    elif io["sha256"] != r["original_sha256"]:
        prob.append((pid, "original_sha256 farkli", of))
    if iw is None:
        prob.append((pid, "web_file yok", wf))
    else:
        if iw["sha256"] != r["web_sha256"]:
            prob.append((pid, "web_sha256 farkli", wf))
        if (iw.get("width"), iw.get("height")) != (int(r["web_width"]), int(r["web_height"])):
            prob.append((pid, f"web boyut beyan {r['web_width']}x{r['web_height']} olculen {iw.get('width')}x{iw.get('height')}", wf))
        if iw.get("format") != "WEBP":
            prob.append((pid, f"web format {iw.get('format')}", wf))
        dims[f"{iw.get('width')}x{iw.get('height')}"] += 1
res["prov_vs_inventory_problems"] = prob
res["web_dims_top"] = dims.most_common(5)
ph_by_id = {p["photo_id"]: p for p in photos}
mism = []
for r in prov:
    p = ph_by_id.get(r["photo_id"])
    if p is None:
        mism.append((r["photo_id"], "Fotograflar satiri yok"))
        continue
    if p["file"] != r["original_file"]:
        mism.append((r["photo_id"], f"file {p['file']} != original_file {r['original_file']}"))
    if p["sha256"] != r["original_sha256"]:
        mism.append((r["photo_id"], "Fotograflar.sha256 != original_sha256"))
res["photo_vs_prov_mismatch"] = mism
odims = Counter()
for p in photos:
    i = inv_by_path.get(p["file"])
    if i:
        odims[f"{i.get('width')}x{i.get('height')}"] += 1
res["orig_dims_top"] = odims.most_common(5)

# K81: pixel_review_file == file
ev_by_pid = {e["photo_id"]: e for e in evid}
k81 = [(p["photo_id"], p["file"], ev_by_pid.get(p["photo_id"], {}).get("pixel_review_file"))
       for p in photos if ev_by_pid.get(p["photo_id"], {}).get("pixel_review_file") != p["file"]]
res["pixel_review_file_mismatch"] = k81

# K79: dates
res["capture_date_empty"] = sum(1 for p in photos if not p.get("capture_date"))
res["capture_date_top"] = Counter(str(p.get("capture_date")) for p in photos).most_common(4)
res["downloaded_on_top"] = Counter(str(r.get("downloaded_on")) for r in prov).most_common(3)
res["source_checked_on_top"] = Counter(str(p.get("source_checked_on")) for p in photos).most_common(3)

# K78: five URL roles
k78 = []
for r in prov:
    p = ph_by_id.get(r["photo_id"], {})
    if r.get("original_file_url") == p.get("source_url"):
        k78.append((r["photo_id"], "original_file_url == source_url"))
    if r.get("downloaded_file_url") == p.get("source_url"):
        k78.append((r["photo_id"], "downloaded_file_url == source_url"))
    if r.get("author_url") and r.get("author_url") == p.get("source_url"):
        k78.append((r["photo_id"], "author_url == source_url"))
res["k78_role_mixups"] = k78
res["author_url_empty"] = [r["photo_id"] for r in prov if not r.get("author_url")]

# K15/K84: absolute or unsafe paths anywhere in Excel string cells
bad = []
pat = re.compile(r"([A-Za-z]:\\\\|[A-Za-z]:/|file://|\.\./|temp_private|/Users/|drive\.google)", re.I)
for f in DUMP.glob("*.jsonl"):
    with f.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            for k, v in row.items():
                if isinstance(v, str) and pat.search(v):
                    bad.append((f.stem, row.get("_row"), k, v[:120]))
res["unsafe_paths_in_excel"] = bad[:20]
res["unsafe_paths_in_excel_count"] = len(bad)

# K16: longest cell
longest = (0, None)
for f in DUMP.glob("*.jsonl"):
    with f.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            row = json.loads(line)
            for k, v in row.items():
                if isinstance(v, str) and len(v) > longest[0]:
                    longest = (len(v), f"{f.stem}!{row.get('_row')}.{k}")
res["longest_cell"] = longest

# K46: routes
k46 = []
place_ids = {p["entry_id"] for p in places}
for r in routes:
    ids = [x.strip() for x in str(r.get("stop_entry_ids") or "").replace("\n", ";").split(";") if x.strip()]
    stops = [x.strip() for x in str(r.get("stops") or "").replace("\n", ";").split(";") if x.strip()]
    if not 2 <= len(set(ids)) <= 8:
        k46.append((r["route_id"], f"durak sayisi {len(set(ids))}"))
    if len(ids) != len(stops):
        k46.append((r["route_id"], f"stops {len(stops)} != ids {len(ids)}"))
    if any(i not in place_ids for i in ids):
        k46.append((r["route_id"], "bilinmeyen durak id"))
    if ids and r.get("entry_id") != ids[0]:
        k46.append((r["route_id"], f"entry_id {r.get('entry_id')} ilk durak degil"))
res["routes_problems"] = k46

# K21: answers/places/districts without links
linked = Counter(l["entry_id"] for l in links)
res["entries_without_link"] = [e["entry_id"] for e in (*answers, *places, *districts) if linked[e["entry_id"]] == 0]

# K87 steps
res["adimlar_count"] = len(steps)
res["sayfa_keys"] = [r["key"] for r in pagef]

# Kaynaklar snapshot files present + sha
snap_prob = []
for s in sources:
    sf = s.get("snapshot_file")
    i = inv_by_path.get(sf)
    if not sf or i is None:
        snap_prob.append((s["source_id"], "snapshot dosyasi yok", sf))
    elif i["sha256"] != s.get("snapshot_sha256"):
        snap_prob.append((s["source_id"], "snapshot sha farkli", sf))
res["source_snapshot_problems"] = snap_prob
res["source_snapshot_files_unique"] = len({s.get("snapshot_file") for s in sources})

# cover photos
res["covers"] = [(p["photo_id"], p["_row"], p["file"]) for p in photos if p["role"] == "Kapak"]

# K15/K84: backslash separators in relative path fields
path_fields = {"Fotoğraflar": ["file"], "FotoğrafKaynakları": ["original_file", "web_file"],
               "Kanıtlar": ["pixel_review_file"], "Kaynaklar": ["snapshot_file"]}
bs = {}
for sheet, fields in path_fields.items():
    rows = load(sheet)
    for fld in fields:
        vals = [r for r in rows if r.get(fld)]
        hits = [r for r in vals if "\\" in str(r[fld])]
        bs[f"{sheet}.{fld}"] = {"total": len(vals), "backslash": len(hits),
                                "first_rows": [r["_row"] for r in hits[:3]],
                                "example": hits[0][fld] if hits else None}
res["backslash_paths"] = bs
print(json.dumps(res, ensure_ascii=False, indent=1, default=str))
