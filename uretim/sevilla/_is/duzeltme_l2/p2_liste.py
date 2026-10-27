"""L2 denetiminin P2 (ve P1) bulgularını kısa satırlarla yazar: issue_id | öncelik | kontrol | kayıt | başlık.

Kullanım: python -I -X utf8 p2_liste.py <denetim_OUT>
"""
import json
import sys
from pathlib import Path

d = json.loads((Path(sys.argv[1]) / "issues.json").read_text(encoding="utf-8"))
rows = d.get("issues", d) if isinstance(d, dict) else d
for r in rows:
    pr = r.get("öncelik")
    if pr != "P2":
        continue
    ent = [x.strip().replace("sevilla:", "") for x in str(r.get("entry_id/photo_id") or "").split(",") if x.strip()]
    ents = ",".join(ent[:4]) + (f" (+{len(ent) - 4})" if len(ent) > 4 else "")
    print(r.get("issue_id"), "|", r.get("kategori"), "|", len(ent), "|", ents, "|", str(r.get("mevcut_değer"))[:60], "|",
          str(r.get("önerilen_düzeltme"))[:110])
