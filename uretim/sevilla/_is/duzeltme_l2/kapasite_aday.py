"""Boşaltılabilir kaynak adayları: tek kayıtta kullanılan, kaydın başka kaynağı olan, ≤3 iddiaya dayanak kaynaklar;
turizm portalı önce. Çıktı: duzeltme_l2/kapasite_aday.jsonl (parça, kaynak, url, iddialar). Yalnız okur + o dosyayı yazar.

Kullanım: python -I -X utf8 kapasite_aday.py <WORK_is>
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

IS = Path(sys.argv[1])
P = IS / "data" / "parcalar"
kd = {json.loads(l)["source_id"]: json.loads(l) for l in (IS / "kaynak_dizini.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
users = defaultdict(list)
nsrc = {}
for p in sorted(P.glob("*.jsonl")):
    if p.name.startswith(("Fotoğraf", "Kanıtlar", "Bağlantılar", "Adımlar")):
        continue
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        if "source_ids" not in r:
            continue
        rid = r.get("entry_id") or r.get("term_id") or r.get("route_id") or r.get("field_id") or r.get("key")
        srcs = [s.strip() for s in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if s.strip()]
        nsrc[rid] = len(srcs)
        for s in srcs:
            users[s].append((p.name.split(".")[1], rid))
cl = defaultdict(list)
for p in (IS / "claims").glob("*.jsonl"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            c = json.loads(l)
            cl[c.get("source_id")].append({"claim_id": c.get("claim_id"), "entry_id": c.get("entry_id"), "field": c.get("field"),
                                           "claim": str(c.get("claim"))[:160], "quote": str(c.get("quote"))[:160]})
rows = []
for s, us in users.items():
    if len(us) != 1:
        continue
    parca, rid = us[0]
    if nsrc.get(rid, 0) < 2 or len(cl.get(s, [])) > 3:
        continue
    url = str((kd.get(s) or {}).get("url", ""))
    rows.append({"parca": parca, "source_id": s, "url": url, "kayit": rid, "iddia_sayisi": len(cl.get(s, [])),
                 "turizm": bool(re.search(r"visitasevilla|turismo|andalucia\.org|spain\.info", url, re.I)), "iddialar": cl.get(s, [])})
rows.sort(key=lambda r: (not r["turizm"], r["iddia_sayisi"]))
(IS / "duzeltme_l2" / "kapasite_aday.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({"aday": len(rows), "turizm": sum(r["turizm"] for r in rows), "parca": dict(Counter(r["parca"] for r in rows)),
                  "iddia_0_1": sum(1 for r in rows if r["iddia_sayisi"] <= 1)}, ensure_ascii=False))
