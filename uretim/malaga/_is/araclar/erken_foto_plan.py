"""Mekan planindan erken foto arama plani kurar (Commons onbellegini isitmak icin; resmi plan plan-from-xlsx'tir).

Kullanim: python erken_foto_plan.py <_is> <out.jsonl>
Satir bicimi photo_candidates.plan-from-xlsx ile ayni (+ "wikidata" = plandaki qid). Tek satir JSON ozet.
"""
import json
import pathlib
import sys

sys.path.insert(0, r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
import photo_candidates as pc  # noqa: E402

work = pathlib.Path(sys.argv[1])
sehir = json.loads((work / "sablon_dump" / "Şehir.jsonl").read_text(encoding="utf-8-sig").splitlines()[0])
ad = str(sehir.get("name", "")).strip()
city = {"municipality": ad, "municipality_aliases": sorted({ad, *pc._aliases(sehir.get("aliases"))} - {""}),
        "city_lat": pc._float(sehir.get("latitude")), "city_lon": pc._float(sehir.get("longitude"))}
plan = [json.loads(l) for l in (work / "mekan" / "plan.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
rows = []
for r in plan:
    name = str(r.get("name") or "").strip()
    row = {"entry_id": r["entry_id"], "role": "venue", "name": name, "aliases": pc._name_aliases(name), "group": r["group"],
           "lat": pc._float(r.get("lat")), "lon": pc._float(r.get("lon")), **city}
    if r.get("qid"):
        row["wikidata"] = r["qid"]
    rows.append(row)
pathlib.Path(sys.argv[2]).write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
print(json.dumps({"satir": len(rows), "qid": sum("wikidata" in x for x in rows), "sehir": city}, ensure_ascii=False))
