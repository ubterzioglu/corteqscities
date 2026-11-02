"""Geçici kökte yazılan download-progress-v7.json'u paketteki dosyalarla SHA karşılaştırıp pakete al."""
import hashlib
import json
import pathlib
import sys

S = pathlib.Path(sys.argv[1])
PKG = pathlib.Path(sys.argv[2])


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blok in iter(lambda: f.read(1 << 20), b""):
            h.update(blok)
    return h.hexdigest()


prog = json.loads((S / "Teslimler" / "download-progress-v7.json").read_text(encoding="utf-8-sig"))
uyusmaz = [r["photo_id"] for r in prog if not (PKG / r["original_file"]).exists() or sha(PKG / r["original_file"]) != r["original_sha256"]]
if uyusmaz:
    print(json.dumps({"durum": "uyusmaz", "sayi": len(uyusmaz), "ornek": uyusmaz[:5]}))
    sys.exit(1)
hedef = PKG / "Teslimler" / "download-progress-v7.json"
for eski in ("download-progress-v7.part", "download-progress-v7.eski.json"):
    (PKG / "Teslimler" / eski).unlink(missing_ok=True)
hedef.write_text(json.dumps(prog, ensure_ascii=False, indent=2))
print(json.dumps({"durum": "tamam", "kayit": len(prog)}))
