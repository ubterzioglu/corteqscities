"""Kisa listedeki Commons adaylarinin kucuk onizlemelerini indirir ve contact_sheet girdisi (items.jsonl) yazar.

Pilot is script'i. Kullanim: python foto_onizleme.py <_is klasoru> [--width 330] [--max 600]
Okur: foto/decisions.json (photo_prefilter --out), foto/candidates.jsonl, data/Mekânlar.jsonl, data/Mahalleler.jsonl;
      --decisions baska klasordeyse o klasordeki candidates.jsonl ve venues.jsonl de (ek turlar, ör. foto_ek16).
Yazar: foto/onizleme/<sha1(url)>.jpg (onbellek), foto/items.jsonl {key, path, label, group, decision}
Nezaket: seri istek, istekler arasi 0.5 sn, aciklayici User-Agent, 429/503'te Retry-After (<=30 sn) ile 3 deneme, sonra dur.
stdout tek satir JSON; cikis 0 hepsi indi / 1 eksik var / 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

USER_AGENT = "CorteqsCityToolkit/0.1 (content research; https://www.mediawiki.org/wiki/API:Etiquette)"
# Wikimedia 2026: onizlemeler thumb.wikimedia.org'dan, yalniz standart genisliklerle (330/500/960/1280...; 1600 = HTTP 400).
ALLOWED_HOSTS = ("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def thumb_url(url: str, width: int) -> str:
    """Commons thumb adresini istenen genislige cevirir, sorgu (utm_*) parametrelerini atar; thumb degilse yalniz sorguyu atar."""
    url = url.split("?", 1)[0]
    return re.sub(r"/(\d+)px-", f"/{width}px-", url, count=1) if "/thumb/" in url else url


def fetch(url: str, target: str) -> str | None:
    for attempt in range(1, 4):
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
            with open(target, "wb") as f:
                f.write(data)
            return None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < 3:
                wait = e.headers.get("Retry-After", "")
                time.sleep(min(int(wait), 30) if wait.isdigit() else attempt * 5)
                continue
            return f"HTTP {e.code}"
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            return f"ag: {e}"
    return "deneme hakki bitti"


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("work")
    p.add_argument("--width", type=int, default=330)
    p.add_argument("--max", type=int, default=600)
    p.add_argument("--decisions", default=None, help="varsayilan: foto/decisions.json")
    p.add_argument("--items-out", default=None, help="varsayilan: foto/items.jsonl")
    a = p.parse_args()
    w = a.work
    dec_path = a.decisions or os.path.join(w, "foto", "decisions.json")
    dec = json.load(open(dec_path, encoding="utf-8"))
    cands = {c["candidate_id"]: c for c in read_jsonl(os.path.join(w, "foto", "candidates.jsonl"))}
    # Ayri tur klasoru (ör. foto_ek16): karar dosyasinin yanindaki candidates.jsonl ve venues.jsonl de okunur.
    side = os.path.dirname(os.path.abspath(dec_path))
    side_cands = os.path.join(side, "candidates.jsonl")
    if os.path.exists(side_cands):
        cands.update({c["candidate_id"]: c for c in read_jsonl(side_cands)})
    decision_of = {d["candidate_id"]: d["decision"] for d in dec["decisions"]}
    names = {}
    for sheet in ("Mekânlar", "Mahalleler"):
        path = os.path.join(w, "data", f"{sheet}.jsonl")
        if os.path.exists(path):
            names.update({r["entry_id"]: r["title"] for r in read_jsonl(path)})
    side_venues = os.path.join(side, "venues.jsonl")
    if os.path.exists(side_venues):
        for r in read_jsonl(side_venues):
            names.setdefault(r["entry_id"], r.get("name") or r["entry_id"])
    out_dir = os.path.join(w, "foto", "onizleme")
    os.makedirs(out_dir, exist_ok=True)
    items, errors, downloaded, cached = [], [], 0, 0
    for entry_id, cids in dec["shortlists"].items():
        for cid in cids:
            if len(items) >= a.max:
                break
            c = cands.get(cid) or {}
            src = c.get("thumb_url") or c.get("original_url") or ""
            if not src.startswith(ALLOWED_HOSTS):
                errors.append({"key": cid, "why": "izinli olmayan adres"})
                continue
            url = thumb_url(src, a.width)
            target = os.path.join(out_dir, hashlib.sha1(url.encode()).hexdigest() + ".jpg")
            if os.path.exists(target) and os.path.getsize(target) > 0:
                cached += 1
            else:
                time.sleep(0.5)
                err = fetch(url, target)
                if err:
                    errors.append({"key": cid, "why": err})
                    if "429" in err or "503" in err:
                        break
                    continue
                downloaded += 1
            file_name = str(c.get("commons_file") or cid).replace("File:", "")[:60]
            items.append({"key": cid, "path": target, "label": f"{names.get(entry_id, entry_id)} · {file_name}",
                          "group": entry_id, "decision": decision_of.get(cid)})
    with open(a.items_out or os.path.join(w, "foto", "items.jsonl"), "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items))
    print(json.dumps({"items": len(items), "downloaded": downloaded, "cached": cached, "errors": len(errors),
                      "error_examples": errors[:5]}, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
