"""Son foto denetimi girdisi: paketteki her kare icin pafta ogesi + bilgi satiri (Commons adi ve aciklamasi dahil).

Sevilla dis denetimi S01: inceleme yalniz pafta + mekan adi gordu; Commons dosya adi "San Vicente de Paul" iken
"San Vicente" mekanina "keep" denildi. Bu yuzden bilgi satiri Commons dosya adini, aciklamasini ve kategorilerini tasir.
Cikti: WORK\\_is\\foto_denetim\\items.jsonl (contact_sheet girdisi: key=photo_id, path=paketteki dosya, label) ve
bilgi.jsonl (photo_id, rol, kayit, baslik, alt yazi, commons_dosya, aciklama, kategoriler, yazar, lisans).
Kullanim: python -I foto_denetim_hazirla.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PKG = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\paket")
OUT = W / "foto_denetim"


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def main() -> int:
    photos = jl(W / "data" / "parcalar" / "Fotoğraflar.foto.jsonl")
    key_of = {r["photo_id"]: r.get("key") for r in jl(W / "foto" / "secim_temiz.jsonl")}
    cands = {}
    for f in [W / "foto" / "candidates.jsonl", *sorted(W.glob("foto_*/candidates.jsonl"))]:
        for c in jl(f):
            cands.setdefault(c.get("candidate_id"), c)
    titles = {}
    for sheet in ("Mekânlar", "Mahalleler"):
        for f in (W / "data" / "parcalar").glob(f"{sheet}.*.jsonl"):
            for r in jl(f):
                titles[r["entry_id"]] = r.get("title", "")
    OUT.mkdir(parents=True, exist_ok=True)
    items, info, missing = [], [], []
    for p in photos:
        path = PKG / p["file"]
        if not path.is_file():
            missing.append(p["photo_id"])
        key = key_of.get(p["photo_id"]) or ""
        c = cands.get(key, {})
        items.append({"key": p["photo_id"], "path": str(path), "label": p["photo_id"].split(":")[-1]})
        info.append({"photo_id": p["photo_id"], "rol": p.get("role"), "kayit": p.get("entry_id") or "",
                     "kayit_basligi": titles.get(p.get("entry_id"), ""), "alt_yazi": p.get("caption", ""),
                     "commons_dosya": key.split("|", 1)[-1] if key else "", "kaynak_sayfa": p.get("source_url", ""),
                     "aciklama": str(c.get("description_text") or "")[:400], "kategoriler": str(c.get("categories") or "")[:300],
                     "yazar": p.get("author", ""), "lisans": p.get("license", ""), "cekim_tarihi": p.get("capture_date", "")})
    (OUT / "items.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")
    (OUT / "bilgi.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in info), encoding="utf-8")
    print(json.dumps({"foto": len(items), "dosyasiz": missing, "aciklamasiz": sum(1 for i in info if not i["aciklama"]),
                      "out": str(OUT)}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
