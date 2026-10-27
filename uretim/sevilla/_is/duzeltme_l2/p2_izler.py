"""Her P2 bulgusu için değişiklik kayıtlarındaki izler: bulgu_claim_id'si o issue olan satırlar ve bulgudaki kayıtlardan
d11/d12'de değişenler; kaydı artık olmayanlar. Karar yazmak için girdi (karar değil).

Kullanım: python -I -X utf8 p2_izler.py <denetim_OUT> <WORK_is>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

OUT, IS = Path(sys.argv[1]), Path(sys.argv[2])
d = json.loads((OUT / "issues.json").read_text(encoding="utf-8"))
log_by_issue = defaultdict(int)
changed = defaultdict(set)
for p in (IS / "denetim").glob("*-d1[12]_degisiklik.jsonl"):
    tur = p.name.split("-")[-1].split("_")[0]
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            log_by_issue[str(r.get("bulgu_claim_id"))] += 1
            changed[str(r.get("entry_id"))].add(tur)
var = set()
for p in (IS / "data" / "parcalar").glob("*.jsonl"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            for k in ("entry_id", "term_id", "route_id", "photo_id", "source_id"):
                if r.get(k):
                    var.add(str(r[k]))
for r in d["issues"]:
    if r.get("öncelik") != "P2":
        continue
    ent = [x.strip() for x in str(r.get("entry_id/photo_id") or "").split(",") if x.strip()]
    full = [e if ":" in e else f"sevilla:{e}" for e in ent]
    deg = [e for e in full if changed.get(e)]
    yok = [e for e in full if e not in var and not e.startswith("sevilla:kaynak") and not e.startswith("photo:")]
    print(json.dumps({"issue": r["issue_id"], "kayit": len(full), "issue_izi": log_by_issue.get(r["issue_id"], 0),
                      "d11_d12_degisen": len(deg), "degisenler": [e.replace("sevilla:", "") for e in deg[:8]],
                      "artik_yok": yok[:5]}, ensure_ascii=False))
