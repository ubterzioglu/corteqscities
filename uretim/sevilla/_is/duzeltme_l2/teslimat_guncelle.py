"""_is/data/Teslimat.jsonl: updated_on ve notes'u günceller; öteki alanlar (reviewer boş, editorial_status Taslak) aynen kalır.

Kullanım: python -I -X utf8 teslimat_guncelle.py <WORK_is> <YYYY-AA-GG> <notes metni>
"""
import json
import sys
from pathlib import Path

p = Path(sys.argv[1]) / "data" / "Teslimat.jsonl"
tarih, notes = sys.argv[2], sys.argv[3]
rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
if len(rows) != 1:
    sys.exit(f"Teslimat satır sayısı 1 değil: {len(rows)}")
yeni = {**rows[0], "updated_on": tarih, "notes": notes}
if yeni.get("reviewer") or yeni.get("editorial_status") != "Taslak":
    sys.exit("reviewer boş ve editorial_status Taslak olmalı (kural 2)")
p.write_text(json.dumps(yeni, ensure_ascii=False) + "\n", encoding="utf-8")
print(json.dumps({"updated_on": tarih, "notes_len": len(notes)}, ensure_ascii=False))
