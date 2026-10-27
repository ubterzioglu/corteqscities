"""Bir ya da birkaç kaynak kimliği nerede kullanılıyor: kayıtların source_ids'i, iddia defteri, buton adresleri.

Kullanım: python -I kaynak_kullanim.py sevilla:kaynak:390 [sevilla:kaynak:391 ...]
Kaynak 'serbest' = hiçbir kayıtta, iddiada ve butonda yok -> birleştirme onu Kaynaklar'a koymaz (sayı 1 azalır).
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
RX = re.compile(r"\b(?:sevilla|es):kaynak:\d+\b")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def main(wanted: list[str]) -> int:
    urls = defaultdict(set)
    for row in read_jsonl(W / "kaynak_dizini.jsonl"):
        if row.get("source_id") in wanted:
            urls[row["source_id"]] |= {u for u in (row.get("url"), row.get("final_url")) if u}
    uses = defaultdict(list)
    for f in sorted((W / "data" / "parcalar").glob("*.jsonl")):
        for row in read_jsonl(f):
            rid = row.get("entry_id") or row.get("route_id") or row.get("term_id") or row.get("field_id") or ""
            if f.name.startswith("Bağlantılar"):
                for sid in wanted:
                    if row.get("url") in urls[sid]:
                        uses[sid].append(f"buton {row.get('action_id')}")
                continue
            ids = set(RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False)))
            for sid in wanted:
                if sid in ids:
                    uses[sid].append(f"kayıt {f.name} {rid}")
    for f in sorted((W / "claims").glob("*.jsonl")):
        for row in read_jsonl(f):
            if row.get("source_id") in wanted:
                uses[row["source_id"]].append(f"iddia {f.name} {row.get('entry_id')} {row.get('claim_id')}")
    for sid in wanted:
        print(json.dumps({"source_id": sid, "serbest": not uses[sid], "kullanim_sayisi": len(uses[sid]),
                          "kullanim": uses[sid][:40]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
