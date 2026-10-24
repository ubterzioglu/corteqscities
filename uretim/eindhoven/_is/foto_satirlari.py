"""Secilen Commons karelerinden indirme plani ve Fotoğraflar/Kanıtlar/FotoğrafKaynakları satirlari (pilot is script'i).

Kullanim:
  python foto_satirlari.py plan <_is> <paket_koku>   -> foto/indirme_plani.json (download_media.py girdisi), foto/secim_temiz.jsonl
  python foto_satirlari.py rows <_is> <paket_koku>   -> data/parcalar/Fotoğraflar.foto.jsonl, Kanıtlar.foto.jsonl, FotoğrafKaynakları.foto.jsonl
Girdi: foto/selected.jsonl {key, entry_id, role: Mekân|Kapak, caption, seen}, foto/candidates.jsonl, foto/search.jsonl.
Lisans/yazar kurallari resmi dogrulayicinin kendi fonksiyonlariyla (araclar/arac) kontrol edilir; uymayan kare atilir.
Indirilen dosya Commons'un 1600 px kopyasidir (downloaded_file_url); original_file_url tam cozunurluk adresidir.
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(r"C:\temp_private\corteqs\0000_newera\araclar\arac")
sys.path.insert(0, str(TOOLS))
from core.content_delivery.delivery_values import CC  # noqa: E402
from core.content_delivery.validation_media import FREE_LICENSES, cc_license_matches, official_cc_url  # noqa: E402
import provenance  # noqa: E402
from delivery_tools import create_web_copy  # noqa: E402

CITY = "eindhoven"
TODAY = "2026-10-22"
BAD_AUTHOR = re.compile(r"^(own work|unknown|anonymous|unknown author|bilinmiyor)?$", re.I)


def read_jsonl(path):
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def slugify(text):
    s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s)).strip("-")[:60]


def norm_license(label, url, source_url):
    """(etiket, adres) veya None. CC adresi https, sorgusuz; PD icin Commons dosya sayfasi."""
    label = (label or "").strip()
    url = (url or "").strip()
    if url.startswith("//"):
        url = "https:" + url
    url = url.replace("http://", "https://").split("?")[0]
    if label.lower() in ("public domain", "pd"):
        return "Public domain", source_url
    if label.upper() in ("CC0", "CC0 1.0", "CC-ZERO"):
        u = "https://creativecommons.org/publicdomain/zero/1.0/"
        return ("CC0 1.0", u) if official_cc_url(u, r"/publicdomain/zero/1\.0(?:/deed\.[a-z]{2})?/?") else None
    m = CC.fullmatch(label)
    if m:
        if not url.endswith("/"):
            url += "/"
        return (label, url) if cc_license_matches(label, url) else None
    return None


DELIVERY_WIDTH = 1280  # sozlesme <=1600 px kopyaya izin verir; Wikimedia 1600'u reddeder (standart genislik degil)


def delivery_url(c):
    """Teslim edilecek dosyanin adresi: genislik >1280 ise 1280 px thumb, degilse orijinal; utm sorgusu atilir."""
    orig = str(c.get("original_url") or "").split("?", 1)[0]
    thumb = str(c.get("thumb_url") or "").split("?", 1)[0]
    width = c.get("width") or 0
    if width > DELIVERY_WIDTH and "/thumb/" in thumb and thumb.startswith("https://thumb.wikimedia.org/"):
        return re.sub(r"/(\d+)px-", f"/{DELIVERY_WIDTH}px-", thumb, count=1)
    return orig if orig.startswith("https://upload.wikimedia.org/") else ""


def modification_note(c, delivered):
    """Fotograf basina olguya dayali degisiklik notu: ozgun ve teslim edilen piksel olculeri (kalip not degil)."""
    from PIL import Image
    with Image.open(delivered) as im:
        dw, dh = im.size
    ow, oh = c.get("width") or 0, c.get("height") or 0
    name = str(c.get("commons_file") or c.get("candidate_id", "").split("|", 1)[-1]).replace("File:", "").strip()[:90]
    if ow and (ow, oh) != (dw, dh):
        return (f"Wikimedia Commons'taki \"{name}\" ({ow}×{oh} px) özgün dosyasının {dw}×{dh} px küçültülmüş kopyası "
                "indirildi; kırpma, rötuş ve renk düzeltmesi yapılmadı.")
    return f"Wikimedia Commons'taki \"{name}\" özgün dosyası ({dw}×{dh} px) değiştirilmeden indirildi."


def capture_date(value):
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(value or ""))
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def load(w):
    sel = read_jsonl(os.path.join(w, "foto", "selected.jsonl"))
    # Ana tur foto/ ve ek turlar foto_*/ (ör. foto_ek16): aday ve arama kayitlari birlikte okunur.
    cands, raw = {}, {}
    for path in [os.path.join(w, "foto", "candidates.jsonl")] + sorted(glob.glob(os.path.join(w, "foto_*", "candidates.jsonl"))):
        for c in read_jsonl(path):
            cands.setdefault(c["candidate_id"], c)
    for path in [os.path.join(w, "foto", "search.jsonl")] + sorted(glob.glob(os.path.join(w, "foto_*", "search.jsonl"))):
        for r in read_jsonl(path):
            raw.setdefault((r.get("imageinfo") or {}).get("descriptionurl"), r.get("imageinfo"))
    slugs = {}
    for sheet in ("Mekânlar", "Mahalleler"):
        for r in read_jsonl(os.path.join(w, "data", f"{sheet}.jsonl")):
            slugs[r["entry_id"]] = r["slug"]
    return sel, cands, raw, slugs


def cmd_plan(w, pkg):
    sel, cands, _raw, slugs = load(w)
    plan, clean, dropped, counter = [], [], [], {}
    for s in sel:
        c = cands.get(s["key"])
        if not c:
            dropped.append((s["key"], "aday yok"))
            continue
        lic = norm_license(c.get("license"), c.get("license_url"), c.get("source_url"))
        author = re.sub(r"\s+", " ", c.get("author_text") or "").strip()
        if not lic:
            dropped.append((s["key"], f"lisans uygun degil: {c.get('license')} {c.get('license_url')}"))
            continue
        if BAD_AUTHOR.match(author) or len(author) > 200:
            dropped.append((s["key"], f"yazar uygun degil: {author[:40]}"))
            continue
        url = delivery_url(c)
        if not url:
            dropped.append((s["key"], "indirme adresi izinli degil"))
            continue
        if s["role"] == "Mekân" and s.get("entry_id") not in slugs:
            # yeni mekan data/'da yoksa (birlestir calismadi) "kapak" adina dusmesin
            dropped.append((s["key"], "mekan slug'i yok: once birlestir.py"))
            continue
        base = slugs[s["entry_id"]] if s["role"] == "Mekân" else "kapak"
        counter[base] = counter.get(base, 0) + 1
        n = counter[base]
        ext = Path(url.split("?")[0]).suffix.lower() or ".jpg"
        pid = f"{CITY}:photo:{base}-{n:02d}"
        row = {"photo_id": pid, "original_file": f"Fotoğraflar/{CITY}_{base}_{n:02d}{ext}", "downloaded_file_url": url}
        plan.append(row)
        clean.append({**s, "photo_id": pid, "file": row["original_file"], "license": lic[0], "license_url": lic[1], "author": author})
    Path(w, "foto", "indirme_plani.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    with open(os.path.join(w, "foto", "secim_temiz.jsonl"), "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in clean))
    print(json.dumps({"selected": len(sel), "planned": len(plan), "dropped": len(dropped), "drop_examples": dropped[:8]}, ensure_ascii=False))
    return 0


def cmd_rows(w, pkg):
    _sel, cands, raw, _slugs = load(w)
    clean = read_jsonl(os.path.join(w, "foto", "secim_temiz.jsonl"))
    done = {r["photo_id"]: r for r in json.loads(Path(pkg, "Teslimler", "download-progress-v7.json").read_text(encoding="utf-8"))}
    photos, evid, prov, missing = [], [], [], []
    order = {}
    for i, s in enumerate(clean, 1):
        d = done.get(s["photo_id"])
        if not d:
            missing.append(s["photo_id"])
            continue
        c = cands[s["key"]]
        eid = f"{CITY}:evidence:{s['photo_id'].split(':')[-1]}"
        key = (s["role"], s.get("entry_id") or "")
        order[key] = order.get(key, 0) + 1
        photo = {"photo_id": s["photo_id"], "city_id": CITY, "role": s["role"],
                 "entry_id": s.get("entry_id") if s["role"] == "Mekân" else "", "file": s["file"], "sha256": d["sha256"],
                 "caption": s["caption"][:250], "author": s["author"], "license": s["license"], "license_url": s["license_url"],
                 "source_url": c["source_url"], "capture_date": capture_date(c.get("date_original")),
                 "source_checked_on": TODAY,
                 "modifications": modification_note(c, Path(pkg, s["file"])),
                 "evidence_id": eid, "completion_credit": "Evet", "order": order[key], "editorial_status": "Taslak"}
        sej = {"source_url": c["source_url"], "author": s["author"], "license": s["license"], "license_url": s["license_url"],
               "original_api_record": raw.get(c["source_url"]) or {}, "delivered_file": {"url": d["downloaded_file_url"]},
               "retrieved_on": d.get("downloaded_on") or TODAY}
        evidence = {"evidence_id": eid, "city_id": CITY, "photo_id": s["photo_id"], "source_url": c["source_url"],
                    "source_title": (c.get("commons_file") or c.get("title") or "")[:180], "author": s["author"],
                    "license": s["license"], "license_url": s["license_url"], "usage_terms": c.get("usage_terms") or s["license"],
                    "attribution": f"{s['author']} · {s['license']} · Wikimedia Commons", "restrictions": c.get("restrictions") or "",
                    "checked_on": TODAY, "metadata_review_status": "Bekliyor", "pixel_review_status": "Bekliyor",
                    "pixel_review_file": s["file"], "pixel_review_note": (s.get("seen") or "")[:500], "rights_status": "Bekliyor",
                    "rights_basis": f"Wikimedia Commons dosya sayfasındaki lisans: {s['license']}",
                    "source_snapshot_file": "", "source_snapshot_sha256": "", "license_snapshot_file": "", "license_snapshot_sha256": "",
                    "source_evidence_json": json.dumps(sej, ensure_ascii=False)}
        p = provenance.extract(photo, evidence)
        p = create_web_copy(Path(pkg).resolve(), p)
        # create_web_copy yolu isletim sistemine gore yazar (Windows'ta "\"); paket yollari her yerde "/" olmali (L0 ISS-004).
        p = {**p, "web_file": str(p.get("web_file") or "").replace("\\", "/")}
        photos.append(photo)
        evid.append(evidence)
        prov.append(p)
    out = Path(w, "data", "parcalar")
    for name, rows in (("Fotoğraflar", photos), ("Kanıtlar", evid), ("FotoğrafKaynakları", prov)):
        (out / f"{name}.foto.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    roles = {}
    for p in photos:
        roles[p["role"]] = roles.get(p["role"], 0) + 1
    print(json.dumps({"photos": len(photos), "roles": roles, "missing_download": len(missing),
                      "entries_with_photo": len({p['entry_id'] for p in photos if p['entry_id']})}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    cmd, w, pkg = sys.argv[1:4]
    raise SystemExit({"plan": cmd_plan, "rows": cmd_rows}[cmd](w, pkg))
