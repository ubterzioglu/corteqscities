"""_is/rota_plan.jsonl'de route:005'in 4 durak satırını d13 hedefli düzeltmedeki yeni plana göre günceller (varış saati,
açık mı, dayanak; ziyaret süresi yeni varışlardan ve değişmeyen yürüyüş bacaklarından hesaplanır). Öteki satırlar aynen.

Kullanım: python -I -X utf8 rota_plan_005.py <WORK_is> <yeni_satirlar.jsonl>
"""
import json
import sys
from pathlib import Path

IS, YENI = Path(sys.argv[1]), Path(sys.argv[2])
p = IS / "rota_plan.jsonl"
rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
yeni = {r["durak"]: r for r in (json.loads(l) for l in YENI.read_text(encoding="utf-8").splitlines() if l.strip())}
r5 = [r for r in rows if r["route_id"] == "sevilla:route:005"]
if len(r5) != 4 or set(yeni) != {r["durak"] for r in r5}:
    sys.exit("route:005 durakları eşleşmiyor")


def dk(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


for r in r5:
    n = yeni[r["durak"]]
    r["varis_saati"], r["acik_mi"], r["dayanak"] = n["varis_saati"], n["acik_mi"], n["dayanak"]
for i, r in enumerate(r5):
    if i + 1 < len(r5):
        r["ziyaret_dk"] = dk(r5[i + 1]["varis_saati"]) - r5[i + 1]["onceki_bacak_yuruyus_dk"] - dk(r["varis_saati"])
        if r["ziyaret_dk"] <= 0:
            sys.exit(f"negatif ziyaret süresi: {r['durak']}")
p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps([(r["durak"][:20], r["varis_saati"], r["ziyaret_dk"], r["onceki_bacak_yuruyus_dk"]) for r in r5], ensure_ascii=False))
