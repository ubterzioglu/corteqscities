"""Iki secim turunu tek mekan planinda birlestirir (yalniz kaynagi kabul edilmis mekanlar).

Kullanim: python secim_final.py <_is>
Okur: mekan/selected.jsonl + mekan/secim_durum.jsonl (1. tur kabulleri), mekan/secim2_*.jsonl (2. tur, source_id'li).
Yazar: mekan/plan.jsonl (yer-yazari.md plan alanlari) ve mekan/selected_final.jsonl (tam satirlar).
Tekrar: ayni slug ya da ayni dolu qid ikinci kez gelirse atilir (1. tur onde). source_id kaynak_dizini'nde olmali.
Cikis: 0 tamam, 1 bulgu (satirlar yine yazilir).
"""
import collections
import json
import pathlib
import sys


def jl(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


work = pathlib.Path(sys.argv[1])
dizin = {r["source_id"] for r in jl(work / "kaynak_dizini.jsonl")}
durum = {r["slug"]: r["source_id"] for r in jl(work / "mekan" / "secim_durum.jsonl") if r.get("source_id")}
satirlar = []
for r in jl(work / "mekan" / "selected.jsonl"):
    if r["slug"] in durum:
        satirlar.append({**r, "source_id": durum[r["slug"]], "tur": 1})
for f in sorted((work / "mekan").glob("secim2_*.jsonl")):
    for r in jl(f):
        satirlar.append({**r, "tur": 2, "dosya": f.name})
gorulen_slug, gorulen_qid, son, bulgu, atilan = set(), set(), [], [], []
for r in satirlar:
    if r["slug"] in gorulen_slug or (r.get("qid") and r["qid"] in gorulen_qid):
        atilan.append(f'{r["slug"]} ({r.get("dosya", "tur1")})')
        continue
    if r.get("source_id") not in dizin:
        bulgu.append(f'{r["slug"]}: source_id yok/dizinde degil ({r.get("source_id")})')
        continue
    gorulen_slug.add(r["slug"])
    if r.get("qid"):
        gorulen_qid.add(r["qid"])
    son.append(r)
plan = [{"name": r.get("name"), "group": r["group"], "qid": r.get("qid", ""), "lat": r.get("lat", ""), "lon": r.get("lon", ""),
         "district": r.get("district", ""), "setting": r.get("setting", ""), "official_url": r["url"], "slug": r["slug"],
         "entry_id": r["entry_id"], "source_id": r["source_id"], "commons_category": r.get("commons_category", ""),
         "note": r.get("note", "")} for r in son]
(work / "mekan" / "plan.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in plan), encoding="utf-8")
(work / "mekan" / "selected_final.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in son), encoding="utf-8")
grup = collections.Counter(r["group"] for r in son)
print(json.dumps({"mekan": len(son), "per_group": dict(grup), "koordinatsiz": [r["slug"] for r in son if r.get("lat") in ("", None)],
                  "kategorisiz": sum(not r.get("commons_category") for r in son), "atilan_tekrar": atilan, "bulgu": bulgu},
                 ensure_ascii=False))
sys.exit(1 if bulgu else 0)
