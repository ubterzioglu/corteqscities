"""Değişecek fotoğraflar için aday listesi + 330 px önizleme indirme + pafta girdisi (yalnız _is\duzeltme_l2\foto altına yazar)."""
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

IS = Path(sys.argv[1])
HEDEF = sys.argv[2].split(",")  # entry_id slug listesi
OUT = IS / "duzeltme_l2" / "foto"
(OUT / "onizleme").mkdir(parents=True, exist_ok=True)
UA = "CorteqsCityPack/1.0 (duzeltme; corteqssocial@gmail.com)"


def JL(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


sel = JL(IS / "foto" / "selected.jsonl")
used_files = {s["key"].split("|", 1)[1] for s in sel if "|" in s["key"]}
cands = []
for p in [IS / "foto" / "candidates.jsonl"] + sorted(IS.glob("foto_*/candidates.jsonl")):
    cands += JL(p)
items, rows = [], []
for c in cands:
    cid = str(c.get("candidate_id") or "")
    if "|" not in cid:
        continue
    e, fname = cid.split("|", 1)
    slug = e.split(":")[-1]
    if slug not in HEDEF:
        continue
    if fname in used_files:
        continue
    lic = str(c.get("license") or c.get("license_short") or "")
    year = str(c.get("year") or c.get("date_original") or "")[:10]
    w, h = c.get("width"), c.get("height")
    thumb = c.get("thumb_url") or ""
    thumb = re.sub(r"/\d+px-", "/330px-", thumb)
    key = f"{e}|{fname}"
    rows.append({"key": key, "entry_id": e, "file": fname, "year": year, "w": w, "h": h, "license": lic,
                 "credit": re.sub("<[^>]+>", "", str(c.get("credit_text") or ""))[:80], "thumb": thumb})
seen = set()
rows = [r for r in rows if not (r["key"] in seen or seen.add(r["key"]))]
for i, r in enumerate(rows):
    dest = OUT / "onizleme" / f"{i:03d}.jpg"
    if not dest.exists() and r["thumb"]:
        try:
            req = urllib.request.Request(r["thumb"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as resp:
                dest.write_bytes(resp.read())
            time.sleep(0.15)
        except Exception as ex:  # noqa: BLE001
            r["hata"] = str(ex)[:120]
    if dest.exists():
        items.append({"key": r["key"], "label": f"{r['entry_id'].split(':')[-1]} {r['year']} {r['w']}x{r['h']} {r['license']}", "path": str(dest)})
(OUT / "adaylar.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
(OUT / "items.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8")
from collections import Counter
print(json.dumps({"aday": len(rows), "onizleme": len(items), "kayit": dict(Counter(r["entry_id"].split(":")[-1] for r in rows))}, ensure_ascii=False))
