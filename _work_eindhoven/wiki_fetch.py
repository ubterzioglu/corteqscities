# Wikipedia koordinat/özet toplu getirici (yerel araştırma)
import json, time, requests

UA = {"User-Agent": "CorteqsCityResearch/1.0 (yerel sehir icerigi arastirmasi) python-requests"}
S = requests.Session(); S.headers.update(UA)
API = "https://nl.wikipedia.org/w/api.php"

def api(params, tries=4):
    for i in range(tries):
        try:
            r = S.get(API, params=params, timeout=30)
            if r.status_code == 429:
                time.sleep(6); continue
            return r.json()
        except Exception as e:
            if i == tries - 1:
                return {"_error": str(e)}
            time.sleep(3)
    return {"_error": "retries"}

def fetch(place):
    title = place.get("wiki") or place["title"]
    # önce doğrudan başlık, olmazsa arama
    d = api({"action": "query", "titles": title, "prop": "coordinates|extracts|pageprops",
             "exintro": 1, "explaintext": 1, "format": "json", "formatversion": 2, "redirects": 1})
    pages = d.get("query", {}).get("pages", [])
    if not pages or pages[0].get("missing"):
        d = api({"action": "query", "list": "search", "srsearch": title + " Eindhoven", "srlimit": 3, "format": "json"})
        hits = d.get("query", {}).get("search", [])
        if not hits:
            return None
        title = hits[0]["title"]
        d = api({"action": "query", "titles": title, "prop": "coordinates|extracts|pageprops",
                 "exintro": 1, "explaintext": 1, "format": "json", "formatversion": 2, "redirects": 1})
        pages = d.get("query", {}).get("pages", [])
        if not pages or pages[0].get("missing"):
            return None
    p = pages[0]
    coord = (p.get("coordinates") or [{}])[0]
    return {
        "slug": place["slug"],
        "wiki_title": p.get("title"),
        "lat": coord.get("lat"),
        "lon": coord.get("lon"),
        "extract": (p.get("extract") or "")[:900],
        "url": "https://nl.wikipedia.org/wiki/" + p.get("title", "").replace(" ", "_"),
    }

def main():
    places = json.load(open("places_master.json", encoding="utf-8"))
    out = {}
    for pl in places:
        if pl["slug"] in out:
            continue
        w = fetch(pl)
        if w:
            out[pl["slug"]] = w
            print(f"[wiki] {pl['slug']:28s} -> {w['wiki_title'][:40]:42s} lat={w['lat']}")
        else:
            print(f"[wiki] {pl['slug']:28s} -> YOK")
        json.dump(out, open("wiki_data.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
