# Corteqs yerel araştırma önbellek aracı
# Kullanım: python fetch.py urls.json  (urls.json: [{"id":"...","url":"..."}])
import json, sys, os, hashlib, re, time
import requests
from bs4 import BeautifulSoup

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
os.makedirs(CACHE, exist_ok=True)
UA = {"User-Agent": "CorteqsCityResearch/1.0 (yerel icerik arastirmasi; tek seferlik dogrulama; contact: yerel calisma)"}

def clean_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "noscript", "svg", "nav", "header", "footer", "form"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    main = soup.find("main") or soup.body or soup
    text = main.get_text("\n", strip=True)
    text = re.sub(r"\n{2,}", "\n", text)
    return title, text

def fetch(item, timeout=30):
    url = item["url"]
    sid = item["id"]
    out_json = os.path.join(CACHE, sid + ".json")
    out_txt = os.path.join(CACHE, sid + ".txt")
    if os.path.exists(out_json) and not item.get("force"):
        print(f"[skip] {sid} cached")
        return
    try:
        r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
        ctype = r.headers.get("Content-Type", "")
        status = r.status_code
        rec = {"id": sid, "url": url, "final_url": r.url, "status": status,
               "content_type": ctype, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
               "bytes": len(r.content), "sha256": hashlib.sha256(r.content).hexdigest()}
        if "html" in ctype or "text" in ctype:
            title, text = clean_text(r.text)
            rec["title"] = title
            with open(out_txt, "w", encoding="utf-8") as f:
                f.write(f"URL: {r.url}\nFETCHED: {rec['fetched_at']}\nTITLE: {title}\n\n{text}")
        else:
            with open(os.path.join(CACHE, sid + ".bin"), "wb") as f:
                f.write(r.content)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=1)
        print(f"[ok] {sid} {status} {rec.get('title','')[:80]}")
    except Exception as e:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump({"id": sid, "url": url, "error": str(e), "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z")}, f, ensure_ascii=False, indent=1)
        print(f"[ERR] {sid} {url} -> {e}")

def main():
    with open(sys.argv[1], encoding="utf-8") as f:
        items = json.load(f)
    for it in items:
        fetch(it)
        time.sleep(0.4)

if __name__ == "__main__":
    main()
