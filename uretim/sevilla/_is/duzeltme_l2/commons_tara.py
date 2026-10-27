"""Commons: La Cartuja 2025+ kareleri ve Auditorio adaylarının yazar/lisans kaydı (yalnız _is\duzeltme_l2\foto altına yazar)."""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

IS = Path(sys.argv[1])
OUT = IS / "duzeltme_l2" / "foto"
OUT.mkdir(parents=True, exist_ok=True)
UA = "CorteqsCityPack/1.0 (duzeltme; corteqssocial@gmail.com)"
API = "https://commons.wikimedia.org/w/api.php"


def get(params):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        time.sleep(0.2)
        return json.loads(r.read().decode("utf-8"))


def clean(v):
    return re.sub(r"<[^>]+>", "", str(v or "")).strip()


def meta(titles):
    res = []
    for i in range(0, len(titles), 40):
        d = get({"action": "query", "titles": "|".join(titles[i:i + 40]), "prop": "imageinfo",
                 "iiprop": "extmetadata|size|url|user", "iiurlwidth": 330})
        for p in d.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            em = ii.get("extmetadata", {})
            res.append({"file": p.get("title"), "w": ii.get("width"), "h": ii.get("height"), "thumb": ii.get("thumburl"),
                        "user": ii.get("user"), "date": clean(em.get("DateTimeOriginal", {}).get("value"))[:19],
                        "artist": clean(em.get("Artist", {}).get("value"))[:80], "license": clean(em.get("LicenseShortName", {}).get("value")),
                        "credit": clean(em.get("Credit", {}).get("value"))[:80], "desc": clean(em.get("ImageDescription", {}).get("value"))[:160],
                        "permission": clean(em.get("Permission", {}).get("value"))[:80]})
    return res


files = []
for cat in ("Category:Estadio de La Cartuja", "Category:Estadio La Cartuja", "Category:Estadio Olímpico de la Cartuja"):
    cont = {}
    while True:
        d = get({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmtype": "file|subcat", "cmlimit": 500, **cont})
        for m in d.get("query", {}).get("categorymembers", []):
            if m["title"].startswith("File:"):
                files.append(m["title"])
            elif m["title"].startswith("Category:") and re.search(r"202[5-6]|remodel|reform|ampli", m["title"], re.I):
                d2 = get({"action": "query", "list": "categorymembers", "cmtitle": m["title"], "cmtype": "file", "cmlimit": 500})
                files += [x["title"] for x in d2.get("query", {}).get("categorymembers", [])]
        if "continue" not in d:
            break
        cont = d["continue"]
files = sorted(set(files))
cartuja = [m for m in meta(files) if m["date"][:4] in ("2025", "2026")]
aud = meta(["File:Interior Auditorio Nissan cartuja.jpg", "File:Butacas Interior Auditorio.jpg", "File:Entrada exterior.jpg",
            "File:Interior Auditorio.jpg", "File:Vista exterior Auditorio Nissan Cartuja.jpg", "File:Auditorio Nissan Cartuja.jpg",
            "File:Interior Sala Oasis - vista 2.jpg", "File:Paseo Delicias - Séville (ES61) - 2023-04-25 - 1.jpg",
            "File:Paseo Delicias - Séville (ES61) - 2023-04-25 - 2.jpg", "File:Paseo Delicias - Séville (ES61) - 2023-04-25 - 3.jpg",
            "File:PS delicias 2017001.jpg"])
(OUT / "commons_tara.json").write_text(json.dumps({"cartuja_toplam": len(files), "cartuja_2025": cartuja, "diger": aud}, ensure_ascii=False, indent=1), encoding="utf-8")
items = []
for i, m in enumerate(cartuja + aud):
    if not m.get("thumb"):
        continue
    dest = OUT / "onizleme" / f"c{i:03d}.jpg"
    if not dest.exists():
        try:
            req = urllib.request.Request(m["thumb"], headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as r:
                dest.write_bytes(r.read())
            time.sleep(0.15)
        except Exception:  # noqa: BLE001
            continue
    items.append({"key": m["file"], "label": f"{m['file'][5:45]} {m['date'][:10]} {m['w']}x{m['h']}", "path": str(dest)})
(OUT / "items_c.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8")
print(json.dumps({"cartuja_dosya": len(files), "cartuja_2025": len(cartuja)}, ensure_ascii=False))
for m in cartuja + aud:
    print(f"{m['date'][:10]} | {m['w']}x{m['h']} | {m['license']} | artist={m['artist'][:40]} | user={m['user']} | {m['file']}")
