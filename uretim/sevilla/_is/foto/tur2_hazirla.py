"""Tur 2: fotoğrafı 3'ten az kayıtlar için, tur1'de incelenmemiş adaylardan karar dosyası kurar."""
import json, pathlib, collections
F = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is\foto")
d1 = json.load(open(F / "tur1" / "decisions.json", encoding="utf-8"))
d8 = json.load(open(F / "tur2" / "decisions_full.json", encoding="utf-8"))
seen = {json.loads(l)["key"] for l in open(F / "tur1" / "items.jsonl", encoding="utf-8") if l.strip()}
have = collections.Counter(json.loads(l)["entry_id"] for l in open(F / "selected.jsonl", encoding="utf-8") if l.strip() and json.loads(l)["role"] == "Mekân")
sl = d8.get("shortlists", {})
new = {}
for eid, keys in sl.items():
    need = 3 - have.get(eid, 0)
    if need <= 0:
        continue
    rest = [k for k in keys if (k if isinstance(k, str) else k.get("key")) not in seen]
    if rest:
        new[eid] = rest[: need + 2]
out = dict(d8)
out["shortlists"] = new
json.dump(out, open(F / "tur2" / "decisions.json", "w", encoding="utf-8"), ensure_ascii=False)
print(json.dumps({"entries": len(new), "items": sum(len(v) for v in new.values()), "keys": list(d8.keys())}))
