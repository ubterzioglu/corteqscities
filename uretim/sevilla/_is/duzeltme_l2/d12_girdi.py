"""d11 değişiklik kayıtlarından değişen/yeni kayıtları çıkarır ve parça başına denetim_girdi --tur d12 çalıştırır.

Kullanım: python -I -X utf8 d12_girdi.py <WORK_is> <TK> <parca,parca,...>
"""
import json
import subprocess
import sys
from pathlib import Path

IS, TK, PARCALAR = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3].split(",")
PY = sys.executable
ozet = {}
for parca in PARCALAR:
    log = IS / "denetim" / f"{parca}-d11_degisiklik.jsonl"
    if not log.exists():
        ozet[parca] = "değişiklik kaydı yok"
        continue
    rows = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    silinen = {r["entry_id"] for r in rows if r.get("alan") == "kayit_silindi"}
    ids = sorted({r["entry_id"] for r in rows if r.get("entry_id")} - silinen)
    # yalnız parçada hâlâ bulunan kayıtlar
    var = set()
    for p in (IS / "data" / "parcalar").glob(f"*.{parca}.jsonl"):
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                var.add(r.get("entry_id") or r.get("term_id") or r.get("route_id"))
    ids = [i for i in ids if i in var]
    if not ids:
        ozet[parca] = "değişen kayıt yok"
        continue
    cp = subprocess.run([PY, "-X", "utf8", str(TK / "denetim_girdi.py"), str(IS), "--city-id", "sevilla", "--tur", "d12", "--parca", parca,
                         "--kayit", ",".join(ids)], capture_output=True, text=True, encoding="utf-8")
    ozet[parca] = {"kayit": len(ids), "silinen": len(silinen), "cikis": cp.returncode, "son": (cp.stdout.strip().splitlines() or [""])[-1][:300],
                   "hata": cp.stderr.strip()[-300:]}
print(json.dumps(ozet, ensure_ascii=False, indent=1))
