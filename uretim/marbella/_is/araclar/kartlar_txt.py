"""Denetim girdisini okunur yapar: <x>_kartlar.jsonl -> <x>_kartlar.txt (kart basina girintili JSON).

Kullanim: python kartlar_txt.py <kartlar.jsonl> [<entry_id> ...]
entry_id verilirse yalniz o kartlar yazilir (jsonl de ayni sekilde suzulur).
Cikis: 0 yazildi, 2 dosya yok.
"""
import json
import pathlib
import sys


def main() -> int:
    src = pathlib.Path(sys.argv[1])
    if not src.is_file():
        print(json.dumps({"hata": f"dosya yok: {src}"}))
        return 2
    keep = set(sys.argv[2:])
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    if keep:
        rows = [r for r in rows if (r.get("entry_id") or r.get("term_id") or r.get("route_id")) in keep]
        src.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    out = src.with_suffix(".txt")
    parts = []
    for i, r in enumerate(rows, 1):
        rid = r.get("entry_id") or r.get("term_id") or r.get("route_id")
        parts.append(f"===== KART {i}/{len(rows)}: {rid} =====\n" + json.dumps(r, ensure_ascii=False, indent=1))
    out.write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    print(json.dumps({"kart": len(rows), "txt": str(out)}, ensure_ascii=False))
    return 0


sys.exit(main())
