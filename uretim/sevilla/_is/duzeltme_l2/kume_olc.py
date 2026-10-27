"""K28 kümeleri: kart -> parça, başka sekmede kullanım; konu başına kart sayısı ve order aralığı (yalnız okur)."""
import json
import re
import sys
from pathlib import Path

IS = Path(sys.argv[1])
P = IS / "data" / "parcalar"


def JL(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


yan = {}
for p in sorted(P.glob("Yanıtlar.*.jsonl")):
    rows = JL(p)
    orders = [r.get("order") for r in rows if isinstance(r.get("order"), (int, float))]
    print(f"{p.name}: {len(rows)} kart, order {min(orders) if orders else '-'}..{max(orders) if orders else '-'}")
    for r in rows:
        yan[r["entry_id"]] = p.name
blob = {}
for p in list(P.glob("Adımlar.*.jsonl")) + list(P.glob("SayfaAlanları.*.jsonl")) + list(P.glob("Rotalar.*.jsonl")) + list(P.glob("Şehir.*.jsonl")):
    blob[p.name] = p.read_text(encoding="utf-8")
kume = [json.loads(l) for l in (IS / "duzeltme_l2" / "gorev_kapsam_ayrinti.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
for k in kume:
    if k.get("check_id") != "K28" or k.get("oncelik") != "P1":
        continue
    out = []
    for c in k.get("kartlar", []):
        e = c if c.startswith("sevilla:") else f"sevilla:{c}"
        slug = e.split(":")[-1]
        used = [n for n, t in blob.items() if re.search(re.escape(slug) + r"\b", t)]
        out.append(f"{slug} @{yan.get(e, '?')} kullanım:{used or '-'}")
    print("K28:", " | ".join(out))
