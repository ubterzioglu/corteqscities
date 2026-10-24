# Commons fotoğraf uygunluk taraması (yerel araştırma aracı)
import json, os, re, sys, time
import requests

API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "CorteqsCityResearch/1.0 (yerel sehir icerigi arastirmasi; dogrulama amacli) python-requests"}
S = requests.Session()
S.headers.update(UA)

ALLOWED = re.compile(r"^(CC[\s-]?0|CC[\s-]?BY|Public domain|PD)", re.I)
DENY = re.compile(r"(NC\b|ND\b|SA-NC|NonCommercial|NoDeriv)", re.I)

def api(params, tries=4):
    for i in range(tries):
        try:
            r = S.get(API, params=params, timeout=40)
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", 5)) + 2); continue
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if i == tries - 1:
                return {"_error": str(e)}
            time.sleep(2 + i * 2)
    return {"_error": "retries"}

def strip_html(s):
    if not s: return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()

def collect_titles(cand):
    titles = []
    if cand.get("cat"):
        d = api({"action": "query", "list": "categorymembers", "cmtitle": "Category:" + cand["cat"],
                 "cmtype": "file", "cmlimit": "200", "format": "json"})
        for m in d.get("query", {}).get("categorymembers", []):
            titles.append(m["title"])
    for term in cand.get("terms", []):
        d = api({"action": "query", "list": "search", "srsearch": term, "srnamespace": "6",
                 "srlimit": "15", "format": "json"})
        for m in d.get("query", {}).get("search", []):
            titles.append(m["title"])
        time.sleep(0.2)
    seen, out = set(), []
    for t in titles:
        if t not in seen:
            seen.add(t); out.append(t)
    return out

def imageinfo(titles):
    out = []
    for i in range(0, len(titles), 25):
        chunk = titles[i:i+25]
        d = api({"action": "query", "titles": "|".join(chunk), "prop": "imageinfo",
                 "iiprop": "url|mime|size|sha1|extmetadata|timestamp", "iiurlwidth": "1600",
                 "format": "json"})
        for pg in d.get("query", {}).get("pages", {}).values():
            ii = (pg.get("imageinfo") or [None])[0]
            if not ii: continue
            em = ii.get("extmetadata", {})
            lic = strip_html(em.get("LicenseShortName", {}).get("value", ""))
            rec = {
                "title": pg.get("title"),
                "mime": ii.get("mime"), "width": ii.get("width"), "height": ii.get("height"),
                "sha1": ii.get("sha1"),
                "license": lic,
                "license_url": strip_html(em.get("LicenseUrl", {}).get("value", "")),
                "author": strip_html(em.get("Artist", {}).get("value", "")),
                "desc": strip_html(em.get("ImageDescription", {}).get("value", ""))[:300],
                "date": strip_html(em.get("DateTimeOriginal", {}).get("value", "")) or ii.get("timestamp", "")[:10],
                "orig_url": ii.get("url"),
                "thumb_url": ii.get("thumburl"),
                "page": "https://commons.wikimedia.org/wiki/" + pg.get("title", "").replace(" ", "_"),
                "restricted": bool(em.get("Restrictions", {}).get("value")),
            }
            out.append(rec)
        time.sleep(0.3)
    return out

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "venue_candidates.json"
    dst = sys.argv[2] if len(sys.argv) > 2 else "commons_probe.json"
    cands = json.load(open(src, encoding="utf-8"))
    done = {}
    if os.path.exists(dst):
        done = json.load(open(dst, encoding="utf-8"))
    for c in cands:
        slug = c["slug"]
        if slug in done:
            print(f"[skip] {slug}"); continue
        titles = collect_titles(c)
        infos = imageinfo(titles[:120])
        ok = [x for x in infos if x["license"] and ALLOWED.match(x["license"]) and not DENY.search(x["license"])
              and x["mime"] in ("image/jpeg", "image/png", "image/webp") and x["width"] and x["width"] >= 800
              and not x["restricted"]]
        done[slug] = {"candidate_count": len(infos), "usable_count": len(ok), "usable": ok[:25], "rejected": [
            {"title": x["title"], "license": x["license"], "why": "license/size/mime"} for x in infos if x not in ok][:5]}
        print(f"[probe] {slug}: {len(infos)} info, {len(ok)} usable")
        json.dump(done, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(0.4)

if __name__ == "__main__":
    main()
