"""Kaynaklar <=500 icin icerik adaylari (salt okunur): tek kayitta ve en cok 2 iddiada kullanilan, kaydin baska kaynagi da
olan, butonu olmayan kaynaklar; once turizm portali. Cikti: d3_arac\\kapasite_aday.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PARTS = W / "data" / "parcalar"
RX = re.compile(r"\b(?:sevilla|es):kaynak:\d+\b")
PORTAL = re.compile(r"visitasevilla|andalucia\.org|turismo", re.I)
OWN = ("entry_id", "term_id", "route_id", "field_id")


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


index = {r["source_id"]: r for r in jl(W / "kaynak_dizini.jsonl")}
rec_uses, rec_srcs, rec_file = defaultdict(set), {}, {}
for f in sorted(PARTS.glob("*.jsonl")):
    if f.name.startswith(("Bağlantılar", "Fotoğraf", "Kanıtlar", "Adımlar")):
        continue
    for row in jl(f):
        owner = next((row[k] for k in OWN if row.get(k)), None)
        if not owner:
            continue
        ids = RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False))
        rec_srcs[owner], rec_file[owner] = ids, f.name
        for s in ids:
            rec_uses[s].add(owner)
claims = defaultdict(list)
for f in sorted((W / "claims").glob("*.jsonl")):
    for c in jl(f):
        claims[c.get("source_id")].append({"dosya": f.name, "claim_id": c.get("claim_id"), "claim": (c.get("claim") or "")[:140],
                                            "owner": next((c[k] for k in OWN if c.get(k)), None)})
buttons = {b.get("url") for f in PARTS.glob("Bağlantılar.*.jsonl") for b in jl(f)}
out = []
for sid, owners in rec_uses.items():
    url = index.get(sid, {}).get("url") or ""
    if len(owners) != 1 or url in buttons or len(claims[sid]) > 2:
        continue
    owner = next(iter(owners))
    if len(rec_srcs[owner]) < 2 or any(c["owner"] != owner for c in claims[sid]):
        continue
    out.append({"source_id": sid, "portal": bool(PORTAL.search(url)), "url": url, "kayit": owner, "dosya": rec_file[owner],
                "iddialar": claims[sid]})
out.sort(key=lambda c: (not c["portal"], len(c["iddialar"])))
(W / "d3_arac" / "kapasite_aday.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps({"aday": len(out), "portal": sum(1 for c in out if c["portal"]),
                  "ilk": [(c["source_id"], c["portal"], c["kayit"].split(":")[-1][:40], len(c["iddialar"])) for c in out[:10]]}, ensure_ascii=False))
