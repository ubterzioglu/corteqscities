"""d12 turunun parça başına durumu: girdi kayıt sayısı, iddia/karar/değişiklik satırları, düzelt kararı sayısı.

Kullanım: python -I -X utf8 durum_d12.py <WORK_is> [tur]
"""
import datetime
import json
import sys
from pathlib import Path

IS = Path(sys.argv[1])
TUR = sys.argv[2] if len(sys.argv) > 2 else "d12"
DEN = IS / "denetim"


def satirlar(p: Path) -> list:
    if not p.exists():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


ozet = {}
for k in sorted(DEN.glob(f"*-{TUR}_kartlar.jsonl")):
    parca = k.name[: -len(f"-{TUR}_kartlar.jsonl")]
    kart = satirlar(k)
    karar = satirlar(DEN / f"{parca}-{TUR}_karar.jsonl")
    ozet[parca] = {
        "kayit": len(kart),
        "iddia": len(satirlar(DEN / f"{parca}-{TUR}_iddia.jsonl")),
        "karar": len(karar),
        "duzelt": sum(1 for r in karar if r.get("karar") == "düzelt"),
        "degisiklik": len(satirlar(DEN / f"{parca}-{TUR}_degisiklik.jsonl")),
    }
print(datetime.datetime.now().strftime("%H:%M"), json.dumps(ozet, ensure_ascii=False))
