"""Parça, defter ve denetim dosyalarının JSONL sağlamlığı + son 15 dk'da değişenler (yalnız okur)."""
import json
import sys
import time
from pathlib import Path

IS = Path(sys.argv[1])
now = time.time()
bozuk, degisen = [], []
for d in ("data/parcalar", "claims", "denetim"):
    for p in sorted((IS / d).glob("*.jsonl")):
        n, bad = 0, 0
        for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.strip():
                continue
            n += 1
            try:
                json.loads(line)
            except json.JSONDecodeError:
                bad += 1
        if bad:
            bozuk.append(f"{d}/{p.name}: {bad}/{n} bozuk satır")
        if now - p.stat().st_mtime < 900:
            degisen.append(f"{d}/{p.name} ({n} satır, {time.strftime('%H:%M:%S', time.localtime(p.stat().st_mtime))})")
snap = json.loads((IS / "duzeltme_l2" / "d8_eski_satir_sayilari.json").read_text(encoding="utf-8-sig"))
d8_fark = []
for name, cnt in snap.items():
    p = IS / "denetim" / name
    n = sum(1 for l in p.read_text(encoding="utf-8").splitlines() if l.strip()) if p.exists() else 0
    if n != cnt:
        d8_fark.append(f"{name}: {cnt} -> {n}")
new_d8 = [p.name for p in (IS / "denetim").glob("*-d8_*") if p.name not in snap]
print(json.dumps({"bozuk": bozuk, "degisen": degisen, "d8_eski_degisen": d8_fark, "d8_yeni_dosya": new_d8}, ensure_ascii=False, indent=1))
