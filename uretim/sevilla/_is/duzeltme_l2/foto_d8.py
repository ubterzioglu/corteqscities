"""d8 foto turu: elle seçilen Commons kareleri için aday/arama satırları (_is/foto_d8) ve selected.jsonl güncellemesi.

Kullanım: python -I -X utf8 foto_d8.py <WORK_is> <karar.json>
karar.json: {"cikar": [key...], "ekle": [{"entry_id","file","caption","seen"}], "sablon_entry": "sevilla:estadio-benito-villamarin-tur"}
"""
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

IS = Path(sys.argv[1])
K = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
UA = "CorteqsCityPack/1.0 (duzeltme; corteqssocial@gmail.com)"
OUTD = IS / "foto_d8"
OUTD.mkdir(exist_ok=True)


def JL(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


def api(titles):
    q = {"action": "query", "titles": "|".join(titles), "prop": "imageinfo|categories", "iiprop": "url|size|sha1|mime|extmetadata|timestamp|user",
         "iiurlwidth": 1280, "cllimit": 50, "format": "json"}
    req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(q), headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))["query"]["pages"].values()


def clean(v):
    return re.sub(r"<[^>]+>", "", str(v or "")).strip()


# şablon satırlar (önceki elle karar turu)
t_c = next((r for r in JL(IS / "foto_d3" / "candidates.jsonl")), None)
t_s = next((r for r in JL(IS / "foto_d3" / "search.jsonl")), None)
# mevcut aday/arama satırı olan dosyalar (ana klasör ve foto_*)
known = {}
for p in [IS / "foto" / "candidates.jsonl"] + sorted(IS.glob("foto_*/candidates.jsonl")):
    for r in JL(p):
        known[r.get("candidate_id")] = r
need = [a for a in K["ekle"] if f"{a['entry_id']}|{a['file']}" not in known]
cand_rows, search_rows = [], []
if need:
    pages = {p["title"]: p for p in api([a["file"] for a in need])}
    for a in need:
        p = pages[a["file"]]
        ii = p["imageinfo"][0]
        em = ii.get("extmetadata", {})
        v = lambda k: (em.get(k) or {}).get("value")
        c = {k: None for k in t_c}
        c.update({"candidate_id": f"{a['entry_id']}|{a['file']}", "title": a["file"][5:].rsplit(".", 1)[0],
                  "description_text": clean(v("ImageDescription"))[:500], "categories": [x["title"][9:] for x in p.get("categories", [])],
                  "date_original": clean(v("DateTimeOriginal"))[:19], "year": int(clean(v("DateTimeOriginal"))[:4]) if clean(v("DateTimeOriginal"))[:4].isdigit() else None,
                  "width": ii["width"], "height": ii["height"], "mime": ii.get("mime"), "license": clean(v("LicenseShortName")),
                  "license_url": clean(v("LicenseUrl")), "usage_terms": clean(v("UsageTerms")), "author_text": clean(v("Artist")),
                  "credit_text": clean(v("Credit")), "restrictions": clean(v("Restrictions")), "attribution_required": clean(v("AttributionRequired")),
                  "copyrighted": clean(v("Copyrighted")), "source_url": ii.get("descriptionurl"), "original_url": ii.get("url"),
                  "thumb_url": ii.get("thumburl"), "sha1": ii.get("sha1"), "provider": "wikimedia_commons"})
        for k in ("lat", "lon"):
            c.setdefault(k, None)
        cand_rows.append(c)
        s = {k: None for k in t_s}
        s.update({"entry_id": a["entry_id"], "query_kind": "elle_karar_d8", "title": a["file"], "imageinfo": ii})
        search_rows.append(s)
    (OUTD / "candidates.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in JL(OUTD / "candidates.jsonl") + cand_rows), encoding="utf-8")
    (OUTD / "search.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in JL(OUTD / "search.jsonl") + search_rows), encoding="utf-8")
# selected.jsonl: çıkar + ekle (eklenen, aynı kaydın ilk çıkarılan satırının yerine)
sp = IS / "foto" / "selected.jsonl"
sel = JL(sp)
bak = IS / "duzeltme_l2" / "selected_oncesi_d8.jsonl"
if not bak.exists():
    bak.write_text(sp.read_text(encoding="utf-8"), encoding="utf-8")
cikar = set(K["cikar"])
ekle_by = {}
for a in K["ekle"]:
    ekle_by.setdefault(a["entry_id"], []).append({"key": f"{a['entry_id']}|{a['file']}", "entry_id": a["entry_id"], "role": "Mekân", "caption": a["caption"], "seen": a["seen"]})
out, done = [], set()
for r in sel:
    if r["key"] in cikar:
        e = r["entry_id"]
        if e in ekle_by and e not in done:
            out += ekle_by[e]
            done.add(e)
        continue
    out.append(r)
for e, rows in ekle_by.items():
    if e not in done:
        # kaydın son satırından sonra ekle
        idx = max((i for i, r in enumerate(out) if r["entry_id"] == e), default=len(out) - 1)
        out[idx + 1:idx + 1] = rows
sp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
missing = [k for k in cikar if k not in {r["key"] for r in sel}]
print(json.dumps({"once": len(sel), "sonra": len(out), "cikarilan": len(cikar) - len(missing), "bulunamayan": missing,
                  "eklenen": sum(len(v) for v in ekle_by.values()), "yeni_aday": len(cand_rows)}, ensure_ascii=False))
