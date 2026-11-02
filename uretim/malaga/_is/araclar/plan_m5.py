"""secim3_1.jsonl (yedekler) -> mekan/plan_m5.jsonl (yer-yazari plan alanlari) + plan.jsonl'e ekler. Tek satir JSON."""
import json
import pathlib

W = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\malaga\_is")
rows = [json.loads(l) for l in (W / "mekan" / "secim3_1.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
dizin = {json.loads(l)["source_id"] for l in (W / "kaynak_dizini.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
plan_eski = [json.loads(l) for l in (W / "mekan" / "plan.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
eski_slug = {r["slug"] for r in plan_eski}
yeni, sorun = [], []
for r in rows:
    if r["slug"] in eski_slug or r.get("source_id") not in dizin:
        sorun.append(r["slug"])
        continue
    yeni.append({"name": r.get("name"), "group": r["group"], "qid": r.get("qid", ""), "lat": r.get("lat", ""), "lon": r.get("lon", ""),
                 "district": r.get("district", ""), "setting": r.get("setting", ""), "official_url": r["url"], "slug": r["slug"],
                 "entry_id": r["entry_id"], "source_id": r["source_id"], "commons_category": r.get("commons_category", ""),
                 "note": r.get("note", ""), "yerine": r.get("yerine", "")})
(W / "mekan" / "plan_m5.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in yeni), encoding="utf-8")
with open(W / "mekan" / "plan.jsonl", "a", encoding="utf-8") as f:
    f.write("".join(json.dumps({k: v for k, v in r.items() if k != "yerine"}, ensure_ascii=False) + "\n" for r in yeni))
print(json.dumps({"m5": len(yeni), "sorun": sorun, "yerine": [r["yerine"] for r in yeni]}, ensure_ascii=False))
