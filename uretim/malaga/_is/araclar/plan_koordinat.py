"""Koordinatsiz plan satirlarini Wikidata havuzundan tamamlar (yalniz tek ve net ad eslesmesi).

Kullanim: python plan_koordinat.py <_is> <slug>=<havuz ad parcasi> ...
Eslesen havuz satiri tek olmali; lat/lon/qid (bos ise) ve commons_category (bos ise) plan.jsonl ve
selected_final.jsonl'e yazilir. Tek satir JSON ozet. Cikis 0.
"""
import json
import pathlib
import sys


def jl(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


work = pathlib.Path(sys.argv[1])
havuz = jl(work / "mekan" / "wikidata_aday.jsonl")
istek = dict(a.split("=", 1) for a in sys.argv[2:])
sonuc = {}
for slug, parca in istek.items():
    es = {r["qid"]: r for r in havuz if parca.lower() in (r.get("name") or "").lower() and r.get("lat")}
    sonuc[slug] = list(es.values())[0] if len(es) == 1 else {"eslesme": len(es)}
for ad in ("plan.jsonl", "selected_final.jsonl"):
    p = work / "mekan" / ad
    rows = jl(p)
    for r in rows:
        h = sonuc.get(r["slug"])
        if h and "qid" in h and r.get("lat") in ("", None):
            r["lat"], r["lon"] = h["lat"], h["lon"]
            r["qid"] = r.get("qid") or h["qid"]
            r["commons_category"] = r.get("commons_category") or h.get("commons_category", "")
            r["note"] = (r.get("note") or "") + ("; " if r.get("note") else "") + f"koordinat Wikidata {h['qid']}"
    p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({k: (v.get("qid"), v.get("name"), v.get("commons_category")) if "qid" in v else v for k, v in sonuc.items()},
                 ensure_ascii=False))
