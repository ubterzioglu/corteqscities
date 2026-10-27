"""Verilen mekân kayıtlarının note ve summary alanlarını yazar (yalnız okur).

Kullanım: python -I -X utf8 not_goster.py <WORK_is> <entry_id> [<entry_id> ...]
"""
import json
import sys
from pathlib import Path

IS = Path(sys.argv[1])
ids = set(sys.argv[2:])
for p in sorted((IS / "data" / "parcalar").glob("Mekânlar.*.jsonl")):
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        if l.strip():
            r = json.loads(l)
            if r.get("entry_id") in ids:
                print(f"== {p.name}:{i} {r['entry_id']}")
                print("note:", r.get("note"))
                print("summary:", r.get("summary"))
