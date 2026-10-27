"""Önceki oturumun (e1640e62, 26.10.2026 10:23) duzeltme_kararlari.jsonl'e yazdığı 21 dış denetim kararını (S01–S21)
oturum kaydındaki komut metninden kurtarır ve bu turun L2 P2 kararlarıyla birlikte dosyaya yazar (önce dış denetim
satırları, sonra L2). Her satıra "denetim" alanı eklenir.

Kullanım: python -I -X utf8 kurtar.py <oturum.jsonl> <WORK_is>
"""
import ast
import json
import re
import sys
from pathlib import Path

kayit, IS = Path(sys.argv[1]), Path(sys.argv[2])
komut = None
for line in kayit.open(encoding="utf-8"):
    if "duzeltme_kararlari.jsonl','w'" not in line:
        continue
    r = json.loads(line)
    for c in (r.get("message") or {}).get("content") or []:
        if isinstance(c, dict) and c.get("type") == "tool_use":
            cmd = str((c.get("input") or {}).get("command", ""))
            if "duzeltme_kararlari.jsonl','w'" in cmd:
                komut = cmd
if not komut:
    sys.exit("komut bulunamadı")
m = re.search(r"\nK\s*=\s*(\[.*?\])\nopen\('uretim/sevilla/_is/duzeltme_kararlari\.jsonl'", komut, re.S)
if not m:
    sys.exit("K listesi ayrıştırılamadı")
eski = [{"issue_id": a, "karar": b, "neden": c, "denetim": "dis_denetim_Sevilla_Detayli_Denetim_20261025 (3. düzeltme turu, 26.10.2026)"}
        for a, b, c in ast.literal_eval(m.group(1))]
p = IS / "duzeltme_kararlari.jsonl"
yeni = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
yeni = [r for r in yeni if not str(r.get("issue_id", "")).startswith("S")]
for r in yeni:
    r.setdefault("denetim", "sevilla_2026-10-26_L2 (L2 sonrası düzeltme turu, 26–27.10.2026)")
p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in eski + yeni), encoding="utf-8")
print(json.dumps({"dis_denetim": len(eski), "l2": len(yeni), "ilk": eski[0]["issue_id"], "son": eski[-1]["issue_id"]}, ensure_ascii=False))
