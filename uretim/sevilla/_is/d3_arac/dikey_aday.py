"""Dikey/asiri genis/dusuk cozunurluklu paket kareleri icin ayni kaydin havuzundan yatay yedek adaylari.

Isaret (gorsel_kalite ile ayni esik): 16:9 ya da 4:3 merkez kirpmasinda alanin %60'indan azi kalir ya da kisa kenar < 600.
Aday: ayni entry_id, secimde olmayan ve baska kayitta kullanilmayan Commons dosyasi, en-boy 1.25-2.0, genislik >= 1600,
lisans CC BY / CC BY-SA / CC0 / PD, kaynak "Own work" (dis kaynaktan aktarilmamis; hak zinciri on kontrolu),
daha once incelemede reddedilmemis. Kayit basina en cok 3 aday; onizleme (1280 px thumb) indirilir.
Cikti: WORK\\_is\\foto_dikey\\isaretli.jsonl, adaylar.jsonl, items.jsonl (contact_sheet), onizleme\\*.jpg
Kullanim: python -I dikey_aday.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

from PIL import Image

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PKG = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\paket")
OUT = W / "foto_dikey"
OWN = re.compile(r"own work|trabajo propio|travail personnel|eigenes werk|opera propria|treball propi|obra pr[oó]pia|werk van", re.I)
LICENSE_OK = re.compile(r"^(cc[ -]by(-sa)?[ -]\d|cc0|public domain|pdm|cc by|cc-by)", re.I)
UA = "corteqs-city-pack/1.0 (dikey kare yedekleri)"


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def kept(w: int, h: int, rw: int, rh: int) -> float:
    return (h * rw / rh) / w if w * rh >= h * rw else (w * rh / rw) / h


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "onizleme").mkdir(exist_ok=True)
    photos = jl(W / "data" / "parcalar" / "Fotoğraflar.foto.jsonl")
    selected_keys = {r["key"] for r in jl(W / "foto" / "selected.jsonl")}
    used_files = {k.split("|", 1)[-1] for k in selected_keys}
    rejected = {r["key"] for p in (W / "foto" / "inceleme").glob("review_*.jsonl") for r in jl(p) if r.get("result") == "reject"}
    cands: dict[str, list[dict]] = {}
    seen = set()
    for f in [W / "foto" / "candidates.jsonl", *sorted(W.glob("foto_*/candidates.jsonl"))]:
        for c in jl(f):
            if c.get("candidate_id") in seen:
                continue
            seen.add(c.get("candidate_id"))
            cands.setdefault(c.get("entry_id"), []).append(c)
    flagged = []
    for p in photos:
        if p.get("role") != "Mekân":
            continue
        with Image.open(PKG / p["file"]) as im:
            w, h = im.size
        k169, k43 = kept(w, h, 16, 9), kept(w, h, 4, 3)
        reasons = [r for r, bad in (("dikey_ya_da_genis", min(k169, k43) < 0.6), ("dusuk_cozunurluk", min(w, h) < 600)) if bad]
        if reasons:
            flagged.append({"photo_id": p["photo_id"], "entry_id": p["entry_id"], "w": w, "h": h, "nedenler": reasons,
                            "alt_yazi": p.get("caption", "")})
    rows, items = [], []
    for fl in flagged:
        pool = []
        for c in cands.get(fl["entry_id"], []):
            cw, ch = c.get("width") or 0, c.get("height") or 0
            file = c.get("commons_file") or ("File:" + str(c.get("title", "")))
            lic = str(c.get("license") or c.get("usage_terms") or "")
            if (not cw or not ch or c.get("candidate_id") in selected_keys or c.get("candidate_id") in rejected
                    or file in used_files or not (1.25 <= cw / ch <= 2.0) or cw < 1600
                    or not LICENSE_OK.search(lic) or not OWN.search(str(c.get("credit_text") or ""))
                    or "nc" in lic.lower().replace("cc", "") or "nd" in lic.lower()):
                continue
            pool.append(c)
        pool.sort(key=lambda c: (c.get("query_kind") != "wikidata_p18", -(c.get("year") or 0), -(c.get("width") or 0)))
        for rank, c in enumerate(pool[:3], 1):
            name = hashlib.sha1(c["candidate_id"].encode()).hexdigest()[:16] + ".jpg"
            target = OUT / "onizleme" / name
            if not target.is_file() and c.get("thumb_url"):
                req = urllib.request.Request(c["thumb_url"], headers={"User-Agent": UA})
                for attempt in range(3):
                    try:
                        with urllib.request.urlopen(req, timeout=40) as r:
                            target.write_bytes(r.read())
                        break
                    except Exception as exc:  # 429/ag: kisa bekle, sonra atla
                        if attempt == 2:
                            print("indirilemedi:", c["candidate_id"][:80], type(exc).__name__)
                        time.sleep(3 * (attempt + 1))
                time.sleep(0.5)
            if not target.is_file():
                continue
            rows.append({"photo_id": fl["photo_id"], "entry_id": fl["entry_id"], "sira": rank, "key": c["candidate_id"],
                         "w": c.get("width"), "h": c.get("height"), "lisans": c.get("license"), "yazar": c.get("author_text"),
                         "kredi": c.get("credit_text"), "yil": c.get("year"), "aciklama": str(c.get("description_text") or "")[:200],
                         "onizleme": str(target)})
            items.append({"key": f"{fl['photo_id']}#{rank}", "path": str(target),
                          "label": f"{fl['photo_id'].split(':')[-1][:22]}#{rank}"})
    for name, data in (("isaretli.jsonl", flagged), ("adaylar.jsonl", rows), ("items.jsonl", items)):
        (OUT / name).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in data), encoding="utf-8")
    with_cand = {r["photo_id"] for r in rows}
    print(json.dumps({"isaretli": len(flagged), "adayli": len(with_cand), "adaysiz": len(flagged) - len(with_cand),
                      "aday_kare": len(rows), "neden": {k: sum(1 for f in flagged if k in f["nedenler"]) for k in ("dikey_ya_da_genis", "dusuk_cozunurluk")}},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
