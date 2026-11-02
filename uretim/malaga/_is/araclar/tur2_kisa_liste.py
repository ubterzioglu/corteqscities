"""Tur2 kisa listesi: fotografi 3'ten az kayitlar icin, daha once incelenmemis adaylardan en yuksek puanli N.

Kullanim: python tur2_kisa_liste.py <_is> <tur1_decisions.json> <out_decisions.json> [N=8]
Sayim: inceleme/selected_* (verify ok:false olanlar haric; verify yoksa sayilir). Puan: decisions.score, yatay (1.25-2.0) +15,
keep > flag. reject alinmaz. Cikti decisions.json bicimi (decisions aynen, shortlists yeni). Tek satir JSON ozet.
"""
import collections
import json
import pathlib
import sys

work = pathlib.Path(sys.argv[1])
src = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
inc = work / "foto" / "inceleme"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


ok = {r["key"]: bool(r.get("ok")) for f in inc.glob("verify_*.jsonl") for r in jl(f)}
say = collections.Counter(r["entry_id"] for f in inc.glob("selected_*.jsonl") for r in jl(f) if ok.get(r["key"], True))
gorulen = {r["key"] for f in inc.glob("review_*.jsonl") for r in jl(f)}
olcu = {}
for c in jl(work / "foto" / "candidates.jsonl"):
    w, h = c.get("width") or 0, c.get("height") or 0
    olcu[c.get("candidate_id") or f'{c.get("entry_id")}|{c.get("commons_file")}'] = (w / h) if w and h else 0
kayitlar = [r["entry_id"] for r in jl(work / "foto" / "venues.jsonl") if r.get("role") in ("venue", "district")]
aday = collections.defaultdict(list)
for d in src["decisions"]:
    if d.get("decision") == "reject" or d["candidate_id"] in gorulen:
        continue
    oran = olcu.get(d["candidate_id"], 0)
    puan = (d.get("score") or 0) + (15 if 1.25 <= oran <= 2.0 else 0) + (10 if d.get("decision") == "keep" else 0)
    aday[d["entry_id"]].append((puan, d["candidate_id"]))
kisa, bos = {}, []
for e in kayitlar:
    if say[e] >= 3:
        continue
    secim = [cid for _, cid in sorted(aday.get(e, []), reverse=True)[:(n if say[e] == 0 else max(2, n - 3))]]
    if secim:
        kisa[e] = secim
    else:
        bos.append(e)
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({"decisions": src["decisions"], "shortlists": kisa,
                           "summary": {"tur": 2, "kayit": len(kisa), "aday": sum(map(len, kisa.values()))}}, ensure_ascii=False), encoding="utf-8")
print(json.dumps({"kayit": len(kisa), "aday": sum(map(len, kisa.values())), "adaysiz": bos}, ensure_ascii=False))
