"""Foto adım 7 sonrası: (1) parça foto satırlarında dosya yollarında ters bölü yok mu (K84), (2) paketin Fotoğraflar
klasöründe ne foto satırlarında ne indirme planında geçen artık dosyaları siler. Güvenlik: silinecek dosya 20'yi
aşarsa hiçbir şey silmez, çıkış 2.

Kullanım: python -I -X utf8 foto_temizle.py <WORK_is> <PKG> [--uygula]
Çıkış: 0 temiz; 1 ters bölü bulundu (silme yapılmaz); 2 girdi yok ya da silinecek dosya > 20.
"""
import json
import sys
from pathlib import Path

IS, PKG = Path(sys.argv[1]), Path(sys.argv[2])
UYGULA = "--uygula" in sys.argv
fs = sorted((IS / "data" / "parcalar").glob("*.foto.jsonl"))
alan, keep = [], set()
for p in fs:
    for l in p.read_text(encoding="utf-8-sig").splitlines():
        if not l.strip():
            continue
        for k, v in json.loads(l).items():
            if k == "file" or k.endswith("_file"):
                alan.append((p.name, k, str(v)))
                if str(v).startswith("Fotoğraflar"):
                    keep.add(str(v).replace("\\", "/").split("/")[-1])
plan = IS / "foto" / "indirme_plani.json"
if plan.exists():
    keep |= {str(r.get("original_file", "")).split("/")[-1] for r in json.loads(plan.read_text(encoding="utf-8"))}
bad = [a for a in alan if "\\" in a[2]]
klasor = PKG / "Fotoğraflar"
artik = sorted(f.name for f in klasor.iterdir() if f.is_file() and f.name not in keep) if klasor.exists() else []
print(json.dumps({"foto_dosyasi": len(fs), "alan": len(alan), "ters_bolu": len(bad), "ornek": bad[:3], "korunan": len(keep),
                  "artik": len(artik), "artik_ornek": artik[:10]}, ensure_ascii=False))
if not fs or not keep:
    sys.exit(2)
if bad:
    sys.exit(1)
if len(artik) > 20:
    print("silinecek dosya 20'yi aşıyor; hiçbir şey silinmedi")
    sys.exit(2)
if UYGULA:
    for name in artik:
        (klasor / name).unlink()
    print(json.dumps({"silinen": len(artik)}, ensure_ascii=False))
