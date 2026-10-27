"""d13 sonuçlarının özeti: doğru olmayan iddia satırlarının sonuç türü ve ağırlık dağılımı; orta/ciddi satırların kısa
listesi (kayıt, sonuç, iddia, doğrusu). Yalnız okur.

Kullanım: python -I -X utf8 d13_ozet.py <WORK_is>
"""
import json
import sys
from collections import Counter
from pathlib import Path

DEN = Path(sys.argv[1]) / "denetim"
tur, ag = Counter(), Counter()
orta = []
for p in sorted(DEN.glob("*-d13_iddia.jsonl")):
    parca = p.name.split("-d13")[0]
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        s = r.get("sonuç")
        if s == "doğru":
            continue
        tur[s] += 1
        ag[r.get("ağırlık")] += 1
        if r.get("ağırlık") in ("orta", "ciddi"):
            orta.append((parca, str(r.get("entry_id", "")).replace("sevilla:", ""), s, str(r.get("iddia", ""))[:150], str(r.get("doğrusu", ""))[:150]))
print(json.dumps({"sonuc_turu": dict(tur), "agirlik": dict(ag), "orta_ciddi": len(orta)}, ensure_ascii=False))
for o in orta:
    print(" | ".join(o))
