"""Ek tur kisa listesi: <dir>/candidates.jsonl + <dir>/tur/decisions_ham.json -> <dir>/tur/decisions.json (kayit basina puan+yatay sirali N).

Kullanim: python ek_kisa_liste.py <ek_tur_klasoru> [N=6]
"""
import collections
import json
import pathlib
import sys

d = pathlib.Path(sys.argv[1])
n = int(sys.argv[2]) if len(sys.argv) > 2 else 6
src = json.loads((d / "tur" / "decisions_ham.json").read_text(encoding="utf-8"))
oran = {}
for l in (d / "candidates.jsonl").read_text(encoding="utf-8").splitlines():
    if l.strip():
        c = json.loads(l)
        w, h = c.get("width") or 0, c.get("height") or 0
        oran[c["candidate_id"]] = w / h if w and h else 0
aday = collections.defaultdict(list)
for x in src["decisions"]:
    if x.get("decision") == "reject":
        continue
    o = oran.get(x["candidate_id"], 0)
    aday[x["entry_id"]].append(((x.get("score") or 0) + (15 if 1.25 <= o <= 2.0 else 0) + (10 if x.get("decision") == "keep" else 0), x["candidate_id"]))
kisa = {e: [c for _, c in sorted(v, reverse=True)[:n]] for e, v in aday.items()}
(d / "tur" / "decisions.json").write_text(json.dumps({"decisions": src["decisions"], "shortlists": kisa, "summary": {}}, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"kayit": len(kisa), "aday": sum(map(len, kisa.values()))}))
