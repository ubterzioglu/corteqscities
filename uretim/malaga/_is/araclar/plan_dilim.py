"""Mekan planini yazar dilimlerine boler: mekan/plan_<gorev>.jsonl.

Kullanim: python plan_dilim.py <_is> <gorev>=<Grup1>|<Grup2> ...
Tek satir JSON ozet (dilim basina mekan ve grup sayisi). Planda dilime dusmeyen grup varsa cikis 1.
"""
import collections
import json
import pathlib
import sys

work = pathlib.Path(sys.argv[1])
plan = [json.loads(l) for l in (work / "mekan" / "plan.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
dilim = {g: a.split("=", 1)[0] for a in sys.argv[2:] for g in a.split("=", 1)[1].split("|")}
ozet, kalan = collections.defaultdict(collections.Counter), []
yaz = collections.defaultdict(list)
for r in plan:
    d = dilim.get(r["group"])
    if not d:
        kalan.append(r["slug"])
        continue
    yaz[d].append(r)
    ozet[d][r["group"]] += 1
for d, rows in yaz.items():
    (work / "mekan" / f"plan_{d}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({d: {"mekan": sum(c.values()), **c} for d, c in ozet.items()} | {"dilimsiz": kalan}, ensure_ascii=False))
sys.exit(1 if kalan else 0)
