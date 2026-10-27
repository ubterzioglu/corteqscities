"""K05: Kanıtlar satırlarının bağlamadığı fotoğraf kanıt JSON'larını (Lisans kanıtları/*.source-evidence.json,
*.license-evidence.json) paketten siler. Kaynak kopyalarına (sha256 adlı .html) ve başka dosyalara dokunmaz.

Kullanım: python -I -X utf8 artik_kanit_temizle.py <WORK_is> <PKG> [--dry]
"""
import json
import sys
from pathlib import Path

IS, PKG = Path(sys.argv[1]), Path(sys.argv[2])
DRY = "--dry" in sys.argv
ref = set()
for line in (IS / "data" / "parcalar" / "Kanıtlar.foto.jsonl").read_text(encoding="utf-8").splitlines():
    if line.strip():
        r = json.loads(line)
        for k, v in r.items():
            if k.endswith("_file") and v:
                ref.add(str(v).replace("\\", "/").split("/")[-1])
silinen = []
for p in sorted((PKG / "Lisans kanıtları").glob("*-evidence.json")):
    if p.name.endswith((".source-evidence.json", ".license-evidence.json")) and p.name not in ref:
        silinen.append(p.name)
        if not DRY:
            p.unlink()
print(json.dumps({"bagli": len(ref), "silinen": len(silinen), "ornek": silinen[:20], "dry": DRY}, ensure_ascii=False))
