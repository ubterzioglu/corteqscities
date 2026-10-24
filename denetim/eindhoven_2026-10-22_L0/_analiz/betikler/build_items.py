"""items.jsonl for contact_sheet: one row per delivered photo (Fotograflar sheet dump), read-only on PKG."""
import json
import sys
from pathlib import Path


def load(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main() -> int:
    dump, pkg, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
    titles = {}
    for sheet in ("Mekânlar", "Mahalleler"):
        for row in load(dump / f"{sheet}.jsonl"):
            titles[row["entry_id"]] = row.get("title") or row["entry_id"]
    rows, missing = [], []
    for photo in load(dump / "Fotoğraflar.jsonl"):
        rel = str(photo["file"]).replace("\\", "/")
        real = (pkg / rel).resolve()
        if not real.is_file():
            missing.append(rel)
        entry = photo.get("entry_id") or None
        place = titles.get(entry, "Kapak" if photo.get("role") == "Kapak" else (entry or "?"))
        rows.append({"key": photo["photo_id"], "path": str(real), "label": f"{place} · {Path(rel).name}",
                     "group": entry, "excel_row": photo.get("_row"), "role": photo.get("role")})
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps({"items": len(rows), "missing_files": missing}, ensure_ascii=False))
    return 0 if not missing else 1


if __name__ == "__main__":
    sys.exit(main())
