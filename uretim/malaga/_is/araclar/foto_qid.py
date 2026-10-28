"""foto/venues.jsonl satirlarina "wikidata" (QID) ekler (B12).

Kullanim: python foto_qid.py <_is> <venues.jsonl>
Mekan: mekan/plan.jsonl'deki ayni entry_id'nin qid'i. Mahalle: havuzda (wikidata_aday.jsonl) types neighborhood/barrio/quarter
olan ve adi birebir (buyuk/kucuk harf ve aksan farki gozetmeden) ayni tek oge. Dosyayi yerinde yazar. Tek satir JSON ozet.
"""
import json
import pathlib
import sys
import unicodedata


def norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c)).strip()


def jl(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


work = pathlib.Path(sys.argv[1])
vpath = pathlib.Path(sys.argv[2])
plan = {r["entry_id"]: r.get("qid", "") for r in jl(work / "mekan" / "plan.jsonl")}
havuz = {}
for r in jl(work / "mekan" / "wikidata_aday.jsonl"):
    if any(t in (r.get("types") or "") for t in ("neighborhood", "barrio", "quarter")) and r.get("name"):
        havuz.setdefault(norm(r["name"]), set()).add(r["qid"])
rows = jl(vpath)
sayi = {"mekan_qid": 0, "mahalle_qid": 0, "qidsiz": []}
for r in rows:
    q = ""
    if r.get("role") == "venue":
        q = plan.get(r["entry_id"], "")
        sayi["mekan_qid"] += bool(q)
    elif r.get("role") == "district":
        aday = havuz.get(norm(r.get("name", "")), set())
        q = next(iter(aday)) if len(aday) == 1 else ""
        sayi["mahalle_qid"] += bool(q)
    if q:
        r["wikidata"] = q
    elif r.get("role") in ("venue", "district"):
        sayi["qidsiz"].append(r["entry_id"])
vpath.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({"satir": len(rows), **{k: (len(v) if isinstance(v, list) else v) for k, v in sayi.items()},
                  "qidsiz_ornek": sayi["qidsiz"][:12]}, ensure_ascii=False))
