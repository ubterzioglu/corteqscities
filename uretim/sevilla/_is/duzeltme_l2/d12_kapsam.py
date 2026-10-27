"""d12 bulgularının değişiklik kaydıyla kapsamı: parça başına "doğru" olmayan iddia bulguları ve "düzelt" kararlı kartlar;
her biri için değişiklik kaydı var mı (bulgu_claim_id eşleşmesi ya da aynı kartta değişiklik). Kayıtsız olanları listeler.

Kullanım: python -I -X utf8 d12_kapsam.py <WORK_is> [parça,parça,...]
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

IS = Path(sys.argv[1])
DEN = IS / "denetim"
SECIM = set(sys.argv[2].split(",")) if len(sys.argv) > 2 else None


def jl(p: Path) -> list:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


ozet = {}
for k in sorted(DEN.glob("*-d12_karar.jsonl")):
    parca = k.name[: -len("-d12_karar.jsonl")]
    if SECIM and parca not in SECIM:
        continue
    bulgu = [r for r in jl(DEN / f"{parca}-d12_iddia.jsonl") if r.get("sonuç") not in ("doğru", None)]
    duzelt = [r["entry_id"] for r in jl(k) if r.get("karar") == "düzelt"]
    deg = jl(DEN / f"{parca}-d12_degisiklik.jsonl")
    by_claim = {str(r.get("bulgu_claim_id")) for r in deg}
    by_entry = defaultdict(int)
    for r in deg:
        by_entry[str(r.get("entry_id"))] += 1
    kayitsiz = [b["claim_id"] for b in bulgu if b.get("claim_id") not in by_claim and not by_entry.get(str(b.get("entry_id")))]
    ozet[parca] = {"bulgu": len(bulgu), "duzelt_kart": len(duzelt), "degisiklik": len(deg),
                   "bulgu_izli": sum(1 for b in bulgu if b.get("claim_id") in by_claim),
                   "dokunulmayan_duzelt_kart": [e.replace("sevilla:", "") for e in duzelt if not by_entry.get(e)],
                   "kayitsiz_bulgu": kayitsiz[:10], "kapasite_satiri": sum(1 for r in deg if r.get("bulgu_claim_id") in ("kapasite", "kural8"))}
print(json.dumps(ozet, ensure_ascii=False, indent=0))
