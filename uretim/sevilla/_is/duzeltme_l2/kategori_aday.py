"""Commons kategorisindeki dosyalar: yazar/lisans/tarih/boyut + 330 px önizleme + pafta girdisi (yalnız _is/duzeltme_l2/foto altına).

Kullanım: python -I -X utf8 kategori_aday.py <WORK_is> "<Category adı>" <ad_on_eki>
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

IS, CAT, AD = Path(sys.argv[1]), sys.argv[2], sys.argv[3]
OUT = IS / "duzeltme_l2" / "foto"
(OUT / "onizleme").mkdir(parents=True, exist_ok=True)
UA = "CorteqsCityPack/1.0 (duzeltme; corteqssocial@gmail.com)"


def get(params):
    req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({**params, "format": "json"}),
                                 headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        time.sleep(0.2)
        return json.loads(r.read().decode("utf-8"))


def clean(v):
    return re.sub(r"<[^>]+>", "", str(v or "")).strip()


cat = CAT if CAT.startswith("Category:") else "Category:" + CAT
files = [m["title"] for m in get({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmtype": "file", "cmlimit": 200})
         .get("query", {}).get("categorymembers", [])]
rows = []
for i in range(0, len(files), 40):
    d = get({"action": "query", "titles": "|".join(files[i:i + 40]), "prop": "imageinfo", "iiprop": "extmetadata|size|url|user", "iiurlwidth": 330})
    for p in d.get("query", {}).get("pages", {}).values():
        ii = (p.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata", {})
        rows.append({"file": p.get("title"), "w": ii.get("width"), "h": ii.get("height"), "thumb": ii.get("thumburl"), "user": ii.get("user"),
                     "date": clean(em.get("DateTimeOriginal", {}).get("value"))[:19], "artist": clean(em.get("Artist", {}).get("value"))[:60],
                     "license": clean(em.get("LicenseShortName", {}).get("value")), "credit": clean(em.get("Credit", {}).get("value"))[:60]})
rows.sort(key=lambda r: r["file"])
items = []
for i, r in enumerate(rows):
    dest = OUT / "onizleme" / f"{AD}{i:03d}.jpg"
    if r.get("thumb") and not dest.exists():
        try:
            req = urllib.request.Request(r["thumb"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as resp:
                dest.write_bytes(resp.read())
            time.sleep(0.15)
        except Exception:  # noqa: BLE001
            continue
    if dest.exists():
        items.append({"key": r["file"], "label": f"{r['file'][5:40]} {r['date'][:10]} {r['w']}x{r['h']}", "path": str(dest)})
(OUT / f"items_{AD}.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in items), encoding="utf-8")
(OUT / f"kategori_{AD}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"kategori": cat, "dosya": len(files), "onizleme": len(items)}, ensure_ascii=False))
for i, r in enumerate(rows):
    print(f"{i + 1:02d} | {r['date'][:10]} | {r['w']}x{r['h']} | {r['license']} | artist={r['artist'][:30]} | user={r['user']} | credit={r['credit'][:25]} | {r['file']}")
