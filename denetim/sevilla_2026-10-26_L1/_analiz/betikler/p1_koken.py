"""P1 bulgularının kökeni: önceki L1 (25.10) seçiminde var mıydı, kontrol türü önceden yapılıyor muydu (yalnız okur)."""
import json
import sys
from pathlib import Path

OUT = Path(sys.argv[1])
PREV = OUT.parent / "sevilla_2026-10-25_L1"


def JL(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


iss = json.loads((OUT / "issues.json").read_text(encoding="utf-8"))["issues"]
prev_sel = set()
for d in (PREV / "_iddia" / "girdi").glob("parti_*"):
    for c in JL(d / "kartlar.jsonl"):
        prev_sel.add(c.get("entry_id") or c.get("term_id"))
prev_issues = json.loads((PREV / "issues.json").read_text(encoding="utf-8"))["issues"] if (PREV / "issues.json").exists() else []
prev_ids = {x.strip() for i in prev_issues for x in str(i.get("entry_id/photo_id", "")).split(",")}
rev = {}
for sheet in ("Yanıtlar", "Sözlük", "Mekânlar", "Mahalleler"):
    for r in JL(OUT / "_dump" / f"{sheet}.jsonl"):
        rev[r.get("entry_id") or r.get("term_id")] = str(r.get("reviewed_on") or "")[:10]
YENI_KONTROL = {"K19": "kartlar arası konu kapsamı (önce hiç yapılmadı)", "K28": "kartlar arası anlamsal tekrar (önce hiç yapılmadı)",
                "K105": "fotoğrafın güncel hâli (önce yalnız paftadan)"}
for i in iss:
    if i["öncelik"] != "P1":
        continue
    ids = [x.strip() for x in str(i["entry_id/photo_id"]).split(",") if x.strip()]
    once_sec = sum(1 for x in ids if x in prev_sel)
    once_bulgu = sum(1 for x in ids if x in prev_ids)
    son_tur = sum(1 for x in ids if rev.get(x) == "2026-10-26")
    print(json.dumps({"id": i["issue_id"], "check": i["check_id"], "kayit": len(ids),
                      "L1_secimindeydi": once_sec, "L1_bulgusuydu": once_bulgu, "26.10_duzenlenen": son_tur,
                      "yeni_kontrol": YENI_KONTROL.get(i["check_id"], "")}, ensure_ascii=False))
