"""Tur 1 inceleme kararlarını (ana döngü, temas sayfaları) review/selected dosyalarına çevirir ve foto\\selected.jsonl'i kurar."""
import json, pathlib, sys, collections
sys.path.insert(0, r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
from image_hash import dhash  # noqa: E402

I = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
F = I / "foto"
INC = F / "inceleme"
TURLAR = sys.argv[1:] or ["tur1"]
COVERS = {  # (tur, sheet, slot) -> caption
    ("tur1", 2, 9): "Sevilla'nın simgelerinden Plaza de España: tuğla galeriler, kuleler ve açık mavi gökyüzü.",
    ("tur1", 8, 19): "Sevilla'nın tarihî merkezinde katedral cephesi; meydanda atlı arabalar bekliyor.",
    ("tur1", 2, 19): "Sevilla'da baharda açan jakarandalar ve arkada Triana'ya geçen tarihî demir köprü.",
    ("tur1", 3, 18): "Sevilla'nın en bilinen parkında portakal ağaçları ve geometrik çit bahçeleri.",
    ("tur1", 11, 26): "Sevilla'yı ikiye bölen Guadalquivir; tekneler ve nehrin batı yakasında Triana evleri.",
    ("tur1", 3, 1): "Sevilla'nın Arenal semtinde beyaz-sarı barok cepheli tarihî boğa arenası.",
    ("tur1", 1, 24): "Sevilla'da nehir kıyısına yakın, kırmızı-sarı cepheli barok San Telmo Sarayı.",
    ("tur1", 4, 17): "Sevilla'nın kuzeyindeki Alameda'da ağaç gölgesinde kafeler ve geniş yaya meydanı.",
}
live = set()
for p in (I / "data" / "parcalar").glob("Mekânlar.*.jsonl"):
    live |= {json.loads(l)["entry_id"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}
for p in (I / "data" / "parcalar").glob("Mahalleler.*.jsonl"):
    live |= {json.loads(l)["entry_id"] for l in p.read_text(encoding="utf-8").splitlines() if l.strip()}

sel, drop, covers = [], collections.Counter(), []
for tur in TURLAR:
    base = (I / f"foto_{tur}") if tur.startswith("ek") else F / tur
    sheets = json.load(open(base / "pafta" / "sheets.json", encoding="utf-8"))
    slot = {(int(s["sheet"][6:8]), it["slot"]): it for s in sheets for it in s["items"]}
    dec, cur = {}, None
    for line in (INC / f"{tur}_kararlar.txt").read_text(encoding="utf-8-sig").splitlines():
        if line.startswith("#sheet_"):
            cur = int(line[7:9]); continue
        if not line.strip():
            continue
        n, res, txt = line.split("|", 2)
        dec[(cur, int(n))] = (res, txt)
    review = []
    for (sh, n), it in sorted(slot.items()):
        res, txt = dec.get((sh, n), ("reject", "karar yok"))
        eid = it["key"].split("|", 1)[0]
        if res == "keep" and eid not in live:
            res, txt = "reject", "kayıt pakette yok"
        review.append({"key": it["key"], "sheet": f"sheet_{sh:02d}.jpg", "slot": n, "entry_id": eid, "result": res,
                       "seen": txt if res == "keep" else "", "reason": "" if res == "keep" else txt, "path": it["path"]})
    with open(INC / f"review_{tur}_ana.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in review:
            f.write(json.dumps({k: v for k, v in r.items() if k != "path"}, ensure_ascii=False) + "\n")
    keeps = [r for r in review if r["result"] == "keep"]
    with open(INC / f"selected_{tur}_ana.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in keeps:
            f.write(json.dumps({"key": r["key"], "entry_id": r["entry_id"], "role": "Mekân", "caption": r["seen"], "seen": r["seen"]}, ensure_ascii=False) + "\n")
    sel += keeps
    for (t, sh, n), cap in COVERS.items():
        if t == tur:
            it = slot[(sh, n)]
            covers.append({"key": it["key"], "entry_id": "", "role": "Kapak", "caption": cap, "seen": cap})

per, files, hashes, out = collections.defaultdict(int), set(), collections.defaultdict(list), []
for r in sel:
    fname = r["key"].split("|File:", 1)[1]
    if fname in files:
        drop["ayni_dosya"] += 1; continue
    if per[r["entry_id"]] >= 3:
        drop["kayit_siniri"] += 1; continue
    try:
        h = dhash(r["path"])
    except Exception:
        h = None
    if h is not None and any(bin(h ^ x).count("1") <= 5 for x in hashes[r["entry_id"]]):
        drop["dhash"] += 1; continue
    if h is not None:
        hashes[r["entry_id"]].append(h)
    files.add(fname); per[r["entry_id"]] += 1
    out.append({"key": r["key"], "entry_id": r["entry_id"], "role": "Mekân", "caption": r["seen"], "seen": r["seen"]})
with open(INC / "covers.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for c in covers:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")
with open(F / "selected.jsonl", "w", encoding="utf-8", newline="\n") as f:
    for r in out + covers:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"venue_photos": len(out), "covers": len(covers), "entries_with_photo": len(per),
                  "entries_without": sorted(live - set(per))[:60], "dropped": dict(drop)}, ensure_ascii=False))
