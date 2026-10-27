"""L2 denetim bulgularından düzeltme görevleri (yalnız _is\duzeltme_l2 altına yazar).

Kullanım: python -I -X utf8 gorev_hazirla.py <WORK_is> <DENETIM_OUT>
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IS, DEN = Path(sys.argv[1]), Path(sys.argv[2])
OUTD = IS / "duzeltme_l2"


def JL(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


# kayıt -> parça dosyası
where = {}
for p in sorted((IS / "data" / "parcalar").glob("*.jsonl")):
    sheet = p.name.split(".")[0]
    for r in JL(p):
        k = r.get("entry_id") or r.get("term_id") or r.get("route_id") or r.get("photo_id") or r.get("action_id")
        if k and sheet in ("Yanıtlar", "Sözlük", "Mekânlar", "Mahalleler", "Rotalar", "Fotoğraflar"):
            where.setdefault(k, p.name)
iss = json.loads((DEN / "issues.json").read_text(encoding="utf-8"))["issues"]
cards = {c["entry_id"]: c for c in json.loads((DEN / "claim-checks.json").read_text(encoding="utf-8"))["cards"]}
claims_bad = [c for c in json.loads((DEN / "claim-checks.json").read_text(encoding="utf-8"))["claims"] if c.get("sonuç") != "doğru"]
diger = JL(DEN / "_l" / "diger.jsonl")
sec = set()
for i in iss:
    if i["öncelik"] == "P1" or (i["check_id"] in ("K108", "K14", "K05")):
        sec.add(i["issue_id"])
gorev = defaultdict(list)
for i in iss:
    if i["issue_id"] not in sec:
        continue
    ids = [x.strip() for x in str(i["entry_id/photo_id"]).split(",") if x.strip()]
    if i["check_id"] in ("K60", "K61", "K62", "K63", "K65", "K71", "K72", "K74", "K105"):
        grup = "foto"
    elif i["check_id"] in ("K108", "K42", "K39", "K38", "K43", "K54", "K55"):
        grup = "mekan"
    elif i["check_id"] in ("K19", "K28"):
        grup = "kapsam"
    elif i["check_id"] in ("K05", "K14", "K83"):
        grup = "script"
    else:
        grup = "kart"
    satir = {"issue_id": i["issue_id"], "oncelik": i["öncelik"], "check_id": i["check_id"], "kategori": i["kategori"],
             "kayitlar": [{"id": x, "parca": where.get(x)} for x in ids], "mevcut": i["mevcut_değer"], "beklenen": i["beklenen"],
             "gozlem": i["somut_gözlem"], "kanit": i["kanıt"], "duzeltme": i["önerilen_düzeltme"]}
    if grup == "kart":
        satir["kart_notlari"] = {x: {k: v for k, v in (cards.get(x) or {}).items() if k.endswith("_not") or k in ("K25", "K26", "K31", "K32", "K40", "K41", "K48")} for x in ids}
        satir["iddialar"] = [{k: c.get(k) for k in ("claim_id", "iddia", "sonuç", "doğrusu", "resmî_URL", "alıntı", "karsi")} for c in claims_bad if c["entry_id"] in ids]
    gorev[grup].append(satir)
# K19/K28 ayrıntısı (kapsam)
gorev["kapsam_ayrinti"] = [r for r in diger if r.get("check_id") in ("K19", "K28") and (r.get("sonuc") == "kaldı" or r.get("check_id") == "K28")]
OUTD.mkdir(parents=True, exist_ok=True)
for g, rows in gorev.items():
    (OUTD / f"gorev_{g}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({g: len(v) for g, v in gorev.items()}, ensure_ascii=False))
for g in ("kart", "mekan", "foto", "kapsam", "script"):
    for r in gorev.get(g, []):
        print(g, r["issue_id"], r["oncelik"], r["check_id"], [f"{k['id'].split(':')[-1]}@{k['parca']}" for k in r["kayitlar"]][:14])
