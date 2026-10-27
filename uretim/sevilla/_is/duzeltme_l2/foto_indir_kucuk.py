"""search.jsonl'deki bir kaydın Commons kareleri için küçük önizleme indirir (görsel inceleme için; pakete girmez).

Kullanım: python -I -X utf8 foto_indir_kucuk.py <search.jsonl> <entry_id> <hedef_klasor>
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

SRC, ENTRY, OUT = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
OUT.mkdir(parents=True, exist_ok=True)
UA = {"User-Agent": "CorteqsCityPack/1.0 (corteqssocial@gmail.com) photo-review"}
for line in SRC.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    r = json.loads(line)
    if r.get("entry_id") != ENTRY:
        continue
    thumb = (r.get("imageinfo") or {}).get("thumburl", "").split("?")[0]
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", r["title"].removeprefix("File:"))
    for size in ("500px", "330px"):
        url = re.sub(r"/\d+px-", f"/{size}-", thumb)
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as resp:
                (OUT / name).write_bytes(resp.read())
            print("ok", size, name)
            break
        except Exception as exc:  # noqa: BLE001 - bir sonraki boyutu dene
            print("hata", size, name, exc)
