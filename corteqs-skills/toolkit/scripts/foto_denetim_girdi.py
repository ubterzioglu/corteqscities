"""Son foto denetimi girdisi: paketteki her kare icin pafta ogesi + bilgi satiri (Commons adi ve aciklamasi dahil).

Sevilla dis denetimi S01: inceleme yalniz pafta + mekan adi gordu; Commons dosya adi "San Vicente de Paul" iken
"San Vicente" mekanina "keep" denildi. Son denetimde (26.10.2026) bilgi satiriyla 8 ret, 3 baska yapi, 2 ayni dosyanin
iki kayitta kullanimi ve 16 alt yazi hatasi bulundu.
Cikti (--out-dir): items.jsonl (contact_sheet girdisi: key=photo_id, path=paketteki dosya, label) ve bilgi.jsonl
(photo_id, rol, kayit, kayit_basligi, alt_yazi, commons_dosya, kaynak_sayfa, aciklama, kategoriler, yazar, lisans,
cekim_tarihi, ayni_dosya_kayitlari). Ardindan: contact_sheet --items <out>/items.jsonl --out-dir <out>/pafta.
Cikis: 0; 1 paketde dosyasi olmayan kare var; 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import common


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    p = argparse.ArgumentParser(description="Son foto denetimi girdisi (pafta ogeleri + Commons bilgisi)")
    p.add_argument("work", type=Path, help="is klasoru (_is)")
    p.add_argument("--pkg", type=Path, required=True, dest="package_root", help="paket koku (yalniz okunur)")
    p.add_argument("--out-dir", type=Path, required=True)
    args = p.parse_args(argv)
    photos_path = args.work / "data" / "parcalar" / "Fotoğraflar.foto.jsonl"
    if not photos_path.is_file() or not args.package_root.is_dir():
        common.emit({"tool": "foto_denetim_girdi", "error": f"foto parcasi ya da paket yok: {photos_path}"})
        return common.EXIT_USAGE
    photos = read_jsonl(photos_path)
    key_of = {r["photo_id"]: r.get("key") for r in read_jsonl(args.work / "foto" / "secim_temiz.jsonl")}
    cands: dict[str, dict] = {}
    for f in [args.work / "foto" / "candidates.jsonl", *sorted(args.work.glob("foto_*/candidates.jsonl"))]:
        for c in read_jsonl(f):
            cands.setdefault(c.get("candidate_id"), c)
    titles = {r["entry_id"]: r.get("title", "") for s in ("Mekânlar", "Mahalleler")
              for f in (args.work / "data" / "parcalar").glob(f"{s}.*.jsonl") for r in read_jsonl(f) if r.get("entry_id")}
    by_file: dict[str, set[str]] = defaultdict(set)
    for ph in photos:
        key = key_of.get(ph["photo_id"]) or ""
        if key and ph.get("role") != "Kapak":
            by_file[key.split("|", 1)[-1]].add(ph.get("entry_id") or "")
    args.out_dir.mkdir(parents=True, exist_ok=True)
    items, info, missing = [], [], []
    for ph in photos:
        path = args.package_root / ph["file"]
        if not path.is_file():
            missing.append(ph["photo_id"])
        key = key_of.get(ph["photo_id"]) or ""
        c = cands.get(key, {})
        file = key.split("|", 1)[-1] if key else ""
        items.append({"key": ph["photo_id"], "path": str(path), "label": ph["photo_id"].split(":")[-1]})
        info.append({"photo_id": ph["photo_id"], "rol": ph.get("role"), "kayit": ph.get("entry_id") or "",
                     "kayit_basligi": titles.get(ph.get("entry_id"), ""), "alt_yazi": ph.get("caption", ""),
                     "commons_dosya": file, "kaynak_sayfa": ph.get("source_url", ""),
                     "aciklama": str(c.get("description_text") or "")[:400], "kategoriler": str(c.get("categories") or "")[:300],
                     "yazar": ph.get("author", ""), "lisans": ph.get("license", ""), "cekim_tarihi": ph.get("capture_date", ""),
                     # kapak, mekan karesiyle ayni dosya olabilir (skill); yalniz iki ayri kayit bulgudur
                     "ayni_dosya_kayitlari": [] if ph.get("role") == "Kapak"
                     else sorted(by_file.get(file, set()) - {ph.get("entry_id") or ""})})
    for name, rows in (("items.jsonl", items), ("bilgi.jsonl", info)):
        (args.out_dir / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    common.emit({"tool": "foto_denetim_girdi", "foto": len(items), "dosyasiz": missing[:20],
                 "aciklamasiz": sum(1 for i in info if not i["aciklama"]),
                 "ayni_dosya_iki_kayit": sum(1 for i in info if i["ayni_dosya_kayitlari"]), "out_dir": str(args.out_dir)})
    return common.EXIT_FINDINGS if missing else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
