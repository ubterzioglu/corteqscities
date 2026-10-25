"""capraz.py: L0 capraz kontrolleri (paket salt okunur; cikti yalniz OUT altina).

Kullanim: python -I -X utf8 capraz.py <OUT> <PKG>
Girdi: OUT/_dump/*.jsonl, OUT/dosya-envanteri.json, OUT/validation-audit.json, PKG/Teslimler/* (yalniz okunur),
       PKG altindaki gorseller (PIL ile yalniz boyut okunur).
Cikti: OUT/_analiz/capraz-kontroller.json ve stdout ozet.
"""
from __future__ import annotations

import collections
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

OUT = Path(sys.argv[1])
PKG = Path(sys.argv[2])
TODAY = "2026-10-25"


def jl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


dump = {p.stem: jl(p) for p in sorted((OUT / "_dump").glob("*.jsonl")) if p.stat().st_size}
inv = load_json(OUT / "dosya-envanteri.json")
inv_by_path = {f["path"]: f for f in inv["files"]}
val = load_json(OUT / "validation-audit.json")
res: dict = {}

# ---------------------------------------------------------------- 1. sayimlar
res["sheet_rows"] = {name: len(rows) for name, rows in dump.items()}

# ---------------------------------------------------------------- 2. fotograf kapsami (K22, K23, K66)
photos = dump["Fotoğraflar"]
places = dump["Mekânlar"]
districts = dump["Mahalleler"]
role_counts = collections.Counter(p.get("role") for p in photos)
per_entry = collections.Counter(p.get("entry_id") for p in photos if p.get("role") != "Kapak")
place_ids = {p["entry_id"] for p in places}
district_ids = {d["entry_id"] for d in districts}
places_wo = [{"entry_id": p["entry_id"], "row": p["_row"], "group": p.get("group"), "title": p.get("title")}
             for p in places if per_entry.get(p["entry_id"], 0) == 0]
districts_wo = [{"entry_id": d["entry_id"], "row": d["_row"], "title": d.get("title")}
                for d in districts if per_entry.get(d["entry_id"], 0) == 0]
unknown_photo_entries = sorted({p.get("entry_id") for p in photos if p.get("role") != "Kapak"}
                               - place_ids - district_ids)
covers = [p for p in photos if p.get("role") == "Kapak"]
group_counts = collections.Counter(p.get("group") for p in places)
group_wo = collections.Counter(p["group"] for p in places_wo)
res["photos"] = {
    "rows": len(photos), "roles": dict(role_counts),
    "unique_file_sha": len({p.get("sha256") for p in photos}),
    "unique_venue_sha": len({p.get("sha256") for p in photos if p.get("role") != "Kapak"}),
    "unique_cover_sha": len({p.get("sha256") for p in covers}),
    "unique_source_url": len({p.get("source_url") for p in photos}),
    "covers": [{"photo_id": c["photo_id"], "row": c["_row"], "file": c.get("file")} for c in covers],
    "cover_sha_also_venue": sum(1 for c in covers if c.get("sha256") in
                                {p.get("sha256") for p in photos if p.get("role") != "Kapak"}),
    "places_with_photo": len(place_ids) - len(places_wo), "places_total": len(place_ids),
    "districts_with_photo": len(district_ids) - len(districts_wo), "districts_total": len(district_ids),
    "places_without_photo": places_wo, "districts_without_photo": districts_wo,
    "group_counts": dict(group_counts), "group_without_photo": dict(group_wo),
    "max_per_entry": max(per_entry.values()) if per_entry else 0,
    "entries_over_5": sorted(k for k, v in per_entry.items() if v > 5),
    "unknown_photo_entries": unknown_photo_entries,
    "hero_photo_id": dump["Şehir"][0].get("hero_photo_id"),
    "hero_exists": dump["Şehir"][0].get("hero_photo_id") in {p["photo_id"] for p in photos},
    "collection_values": dict(collections.Counter(p.get("collection") for p in places)),
}

# ---------------------------------------------------------------- 3. koordinatlar (K43)
coords = collections.defaultdict(list)
lats, lons = [], []
for p in places:
    lat, lon = p.get("latitude"), p.get("longitude")
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        lats.append(lat)
        lons.append(lon)
        coords[(round(lat, 5), round(lon, 5))].append(p["entry_id"])
res["coordinates"] = {
    "with_coords": len(lats), "lat_range": [min(lats), max(lats)], "lon_range": [min(lons), max(lons)],
    "shared": [{"lat": k[0], "lon": k[1], "entries": v} for k, v in coords.items() if len(v) > 1],
}

# ---------------------------------------------------------------- 4. rotalar (K46)
all_ids = place_ids | district_ids
route_rows = []
for r in dump["Rotalar"]:
    stops = [s.strip() for s in re.split(r"[\n;|]", str(r.get("stops", ""))) if s.strip()]
    ids = [s.strip() for s in re.split(r"[\n;|]", str(r.get("stop_entry_ids", ""))) if s.strip()]
    route_rows.append({
        "route_id": r["route_id"], "row": r["_row"], "title": r.get("title"), "stops": len(stops),
        "stop_ids": len(ids), "len_match": len(stops) == len(ids),
        "first_is_entry": bool(ids) and ids[0] == r.get("entry_id"),
        "unknown_ids": [i for i in ids if i not in all_ids], "ids": ids,
    })
res["routes"] = route_rows

# ---------------------------------------------------------------- 5. metin artigi taramasi (yalniz bilgi)
PATTERNS = {"welschap": re.compile(r"welschap", re.I), "golfbaan": re.compile(r"golfbaan", re.I),
            "vonderweg": re.compile(r"vonderweg", re.I), "seksen_atolye": re.compile(r"seksen\s+atölye", re.I),
            "tachtig": re.compile(r"tachtig", re.I)}
hits = []
for sheet, rows in dump.items():
    if sheet in ("Kanıtlar",):
        continue
    for row in rows:
        for key, value in row.items():
            if not isinstance(value, str):
                continue
            for name, rx in PATTERNS.items():
                m = rx.search(value)
                if m:
                    start = max(0, m.start() - 80)
                    hits.append({"pattern": name, "sheet": sheet, "row": row.get("_row"),
                                 "id": row.get("entry_id") or row.get("source_id") or row.get("action_id")
                                 or row.get("route_id") or row.get("photo_id"),
                                 "field": key, "snippet": value[start:m.end() + 80]})
res["residue_scan"] = hits

# ---------------------------------------------------------------- 6. ters egik cizgi (tum hucreler; K84 ek)
bs = collections.Counter()
bs_samples = {}
for sheet, rows in dump.items():
    for row in rows:
        for key, value in row.items():
            if isinstance(value, str) and "\\" in value:
                bs[f"{sheet}.{key}"] += 1
                bs_samples.setdefault(f"{sheet}.{key}", value[:120])
res["backslash_cells"] = {"by_column": dict(bs), "samples": bs_samples}

# ---------------------------------------------------------------- 7. tarihler (K14, K79)
DATE_COLS = ("reviewed_on", "checked_on", "source_checked_on", "updated_on", "coordinate_checked_on",
             "downloaded_on", "capture_date")
dates = {}
latest_content = ""
for sheet, rows in dump.items():
    for col in DATE_COLS:
        values = [str(r[col])[:10] for r in rows if r.get(col) not in (None, "")]
        if not values:
            continue
        dates[f"{sheet}.{col}"] = {"n": len(values), "blank": len(rows) - len(values), "min": min(values),
                                   "max": max(values), "top": collections.Counter(values).most_common(3),
                                   "future": sum(1 for v in values if v > TODAY)}
        if col in ("reviewed_on", "checked_on", "source_checked_on") and sheet != "Teslimat":
            latest_content = max(latest_content, max(values))
res["dates"] = dates
res["latest_content_date"] = latest_content
res["teslimat"] = dump["Teslimat"][0]

# ---------------------------------------------------------------- 8. insan alanlari ve durumlar (K97; degerlendirme disi)
status = {}
for sheet, rows in dump.items():
    for col in ("editorial_status", "metadata_review_status", "pixel_review_status", "rights_status",
                "completion_credit", "verified", "provenance_status"):
        vals = [r.get(col) for r in rows if col in r]
        if vals:
            status[f"{sheet}.{col}"] = dict(collections.Counter(vals))
res["status_values"] = status
approval_words = re.compile(r"^(Onaylandı|Doğrulandı|Approved)$", re.I)
res["approval_like_values"] = [
    {"sheet": s, "row": r.get("_row"), "field": k, "value": v}
    for s, rows in dump.items() for r in rows for k, v in r.items()
    if isinstance(v, str) and approval_words.match(v.strip())]

# ---------------------------------------------------------------- 9. lisans, yazar, URL rolleri (K68, K69, K70, K78)
src = {r["photo_id"]: r for r in dump["FotoğrafKaynakları"]}
ev = {r["photo_id"]: r for r in dump["Kanıtlar"]}
res["licenses"] = dict(collections.Counter(p.get("license") for p in photos))
res["license_url_by_label"] = {lab: sorted({p.get("license_url") for p in photos if p.get("license") == lab})
                               for lab in res["licenses"]}
role_mix = []
for p in photos:
    s = src.get(p["photo_id"], {})
    urls = {"source_url": p.get("source_url"), "author_url": s.get("author_url"),
            "original_file_url": s.get("original_file_url"), "downloaded_file_url": s.get("downloaded_file_url"),
            "license_url": p.get("license_url")}
    present = {k: v for k, v in urls.items() if v}
    dup = [k for k, v in present.items() if list(present.values()).count(v) > 1]
    if dup:
        role_mix.append({"photo_id": p["photo_id"], "same": dup})
res["url_roles"] = {"author_url_filled": sum(1 for s in src.values() if s.get("author_url")),
                    "author_url_blank_with_note": sum(1 for s in src.values()
                                                      if not s.get("author_url") and s.get("provenance_note")),
                    "author_url_blank_no_note": [k for k, s in src.items()
                                                 if not s.get("author_url") and not s.get("provenance_note")],
                    "role_mixing": role_mix, "author_blank": [p["photo_id"] for p in photos if not p.get("author")]}

# ---------------------------------------------------------------- 10. fotograf zinciri (K77, K80, K114, K58)
chain = {"ids_photos": len(photos), "ids_sources": len(src), "ids_evidence": len(ev),
         "id_sets_equal": {p["photo_id"] for p in photos} == set(src) == set(ev),
         "orig_eq_file": 0, "orig_sha_eq": 0, "web_in_inventory": 0, "web_sha_eq": 0,
         "pixel_review_eq_file": 0, "evidence_id_match": 0, "problems": []}
try:
    from PIL import Image  # yalniz boyut okunur
except ImportError:  # pragma: no cover
    Image = None
dims_ok, dims_checked = 0, 0
for p in photos:
    s = src.get(p["photo_id"], {})
    e = ev.get(p["photo_id"], {})
    chain["orig_eq_file"] += s.get("original_file") == p.get("file")
    chain["orig_sha_eq"] += s.get("original_sha256") == p.get("sha256")
    chain["pixel_review_eq_file"] += e.get("pixel_review_file") == p.get("file")
    chain["evidence_id_match"] += e.get("evidence_id") == p.get("evidence_id")
    web = s.get("web_file")
    entry = inv_by_path.get(web)
    if entry:
        chain["web_in_inventory"] += 1
        chain["web_sha_eq"] += entry["sha256"] == s.get("web_sha256")
        if Image is not None:
            dims_checked += 1
            with Image.open(PKG / web) as im:
                if (im.width, im.height) == (s.get("web_width"), s.get("web_height")):
                    dims_ok += 1
                else:
                    chain["problems"].append({"photo_id": p["photo_id"], "declared": [s.get("web_width"),
                                              s.get("web_height")], "actual": [im.width, im.height]})
    else:
        chain["problems"].append({"photo_id": p["photo_id"], "web_file_missing": web})
    fe = inv_by_path.get(p.get("file"))
    if not fe or fe["sha256"] != p.get("sha256"):
        chain["problems"].append({"photo_id": p["photo_id"], "file_sha": "mismatch_or_missing"})
chain["web_dims_ok"] = f"{dims_ok}/{dims_checked}"
chain["web_files_unique"] = len({s.get("web_file") for s in src.values()})
chain["derivation_filled"] = sum(1 for s in src.values() if s.get("derivation"))
chain["modifications_filled"] = sum(1 for p in photos if p.get("modifications"))
res["photo_chain"] = chain

# ---------------------------------------------------------------- 11. kaynaklar (K76 on hazirlik, K82)
sources = dump["Kaynaklar"]
snap_ok, snap_missing = 0, []
for s in sources:
    entry = inv_by_path.get(s.get("snapshot_file"))
    if entry and entry["sha256"] == s.get("snapshot_sha256"):
        snap_ok += 1
    else:
        snap_missing.append(s["source_id"])
referenced = set()
for sheet in ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük"):
    for row in dump.get(sheet, []):
        for sid in re.split(r"[\n;|]", str(row.get("source_ids", ""))):
            if sid.strip():
                referenced.add(sid.strip())
shared_snap = collections.defaultdict(list)
for s in sources:
    shared_snap[s.get("snapshot_file")].append({"source_id": s["source_id"], "url": s.get("url")})
url_dups = collections.Counter(s.get("url") for s in sources)
res["sources"] = {
    "rows": len(sources), "verified": dict(collections.Counter(s.get("verified") for s in sources)),
    "snapshot_sha_ok": snap_ok, "snapshot_problems": snap_missing,
    "unreferenced": sorted(set(s["source_id"] for s in sources) - referenced),
    "dangling_refs": sorted(referenced - set(s["source_id"] for s in sources)),
    "shared_snapshot": [v for v in shared_snap.values() if len(v) > 1],
    "duplicate_urls": {u: c for u, c in url_dups.items() if c > 1},
    "checked_on": dict(collections.Counter(s.get("checked_on") for s in sources)),
}

# ---------------------------------------------------------------- 12. Teslimler ciktilari (K75, K82, K83)
T = PKG / "Teslimler"
prov = load_json(T / "photo-provenance-v7.json")
prov_by = {r["photo_id"]: r for r in prov}
prov_diff = collections.Counter()
for pid, s in src.items():
    pr = prov_by.get(pid)
    if pr is None:
        prov_diff["missing"] += 1
        continue
    for key, value in s.items():
        if key.startswith("_"):
            continue
        a, b = value, pr.get(key)
        if key == "downloaded_on":
            a, b = str(a)[:10], str(b)[:10]
        if a != b and not (a in (None, "") and b in (None, "")):
            prov_diff[key] += 1
with open(T / "fotograf-atiflari-v7.csv", encoding="utf-8-sig", newline="") as stream:
    csv_rows = list(csv.DictReader(stream))
photo_by = {p["photo_id"]: p for p in photos}
csv_diff = collections.Counter()
for row in csv_rows:
    pid = row["photo_id"]
    merged = {**photo_by.get(pid, {}), **src.get(pid, {})}
    for key, value in row.items():
        if key not in merged:
            if value not in ("", None):
                csv_diff[f"{key}(excel'de yok)"] += 1
            continue
        a, b = str(merged[key]), str(value)
        if key in ("downloaded_on", "capture_date", "source_checked_on"):
            a, b = a[:10], b[:10]
        if a != b:
            csv_diff[key] += 1
html = (T / "fotograf-atif-onizleme.html").read_text(encoding="utf-8")
srcs = re.findall(r"""\bsrc\s*=\s*["']([^"']*)["']""", html, re.I)
rel = [s for s in srcs if not re.match(r"[a-z][a-z0-9+.-]*:", s, re.I)]
from urllib.parse import unquote
missing_html = [s for s in rel if not (T / unquote(s)).resolve().exists()]
norm = load_json(T / "normalized-tables-v7.json")
pk = load_json(T / "paket-kontrol-v7.json")
pkg_inv = load_json(T / "dosya-envanteri.json")
pkg_paths = {f["path"]: f["sha256"] for f in pkg_inv["files"]}
my_paths = {f["path"]: f["sha256"] for f in inv["files"]}
dl = load_json(T / "download-progress-v7.json")
res["teslimler"] = {
    "files": sorted(p.name for p in T.iterdir() if p.is_file()),
    "subdirs": {p.name: sum(1 for _ in p.rglob("*") if _.is_file()) for p in T.iterdir() if p.is_dir()},
    "provenance_rows": len(prov), "provenance_field_diffs": dict(prov_diff),
    "csv_rows": len(csv_rows), "csv_field_diffs": dict(csv_diff),
    "csv_downloaded_on_sample": csv_rows[0].get("downloaded_on") if csv_rows else None,
    "html_img_src": len(srcs), "html_relative": len(rel), "html_missing_targets": missing_html[:5],
    "html_missing_count": len(missing_html),
    "normalized_counts": {k: len(v) for k, v in norm.items() if isinstance(v, list)},
    "paket_kontrol": {"technically_complete": pk.get("technically_complete"),
                      "long_values_restored": pk.get("long_values_restored"),
                      "structure_errors": len(pk.get("structure", {}).get("errors", [])),
                      "structure_warnings": len(pk.get("structure", {}).get("warnings", [])),
                      "media_errors": len(pk.get("media", {}).get("errors", [])),
                      "counts": pk.get("structure", {}).get("counts")},
    "pkg_inventory": {"files": len(pkg_paths), "summary": pkg_inv.get("summary"),
                      "only_in_pkg_inventory": sorted(set(pkg_paths) - set(my_paths)),
                      "only_in_audit_inventory": sorted(set(my_paths) - set(pkg_paths)),
                      "sha_differs": sorted(p for p in set(pkg_paths) & set(my_paths)
                                            if pkg_paths[p] != my_paths[p])},
    "download_progress": {"rows": len(dl), "downloaded_on": dict(collections.Counter(
        str(r.get("downloaded_on"))[:10] for r in dl)),
        "sha_matches_excel": sum(1 for r in dl if photo_by.get(r.get("photo_id"), {}).get("sha256") == r.get(
            "sha256"))},
}

# ---------------------------------------------------------------- 13. envanter ozeti (K02, K05, K57)
folders = collections.Counter(f["path"].split("/")[0] if "/" in f["path"] else "." for f in inv["files"])
ext = collections.Counter(f["ext"] for f in inv["files"])
res["inventory"] = {"summary": inv["summary"], "folders": dict(folders), "ext": dict(ext),
                    "dup_sha": inv["findings"]["dup_sha"], "orphans_excluded": inv["findings"]["orphans_excluded"],
                    "xlsx_root": [f["path"] for f in inv["files"] if f["path"].lower().endswith(".xlsx")]}

# ---------------------------------------------------------------- 14. uzun alanlar (K16)
longest = max(((len(str(v)), s, r.get("_row"), k) for s, rows in dump.items() for r in rows
               for k, v in r.items() if isinstance(v, str)), default=(0, "", 0, ""))
res["longest_cell"] = {"chars": longest[0], "sheet": longest[1], "row": longest[2], "field": longest[3]}
res["ekdetaylar_rows"] = len(dump.get("EkDetaylar", []))

out = OUT / "_analiz" / "capraz-kontroller.json"
out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
brief = {k: res[k] for k in ("sheet_rows", "latest_content_date")}
brief["photos"] = {k: v for k, v in res["photos"].items() if k not in ("places_without_photo",
                                                                       "districts_without_photo", "covers")}
print(json.dumps(brief, ensure_ascii=False))
print("routes:", json.dumps([{k: r[k] for k in ("route_id", "stops", "stop_ids", "len_match", "first_is_entry",
                                                "unknown_ids")} for r in route_rows], ensure_ascii=False))
print("coords:", json.dumps(res["coordinates"], ensure_ascii=False))
print("residue:", json.dumps(hits, ensure_ascii=False))
print("backslash:", json.dumps(res["backslash_cells"]["by_column"], ensure_ascii=False))
print("dates:", json.dumps(dates, ensure_ascii=False))
print("teslimat:", json.dumps(res["teslimat"], ensure_ascii=False))
print("status:", json.dumps(status, ensure_ascii=False))
print("approval_like:", len(res["approval_like_values"]))
print("licenses:", json.dumps(res["licenses"], ensure_ascii=False))
print("url_roles:", json.dumps({k: (v if not isinstance(v, list) else len(v)) for k, v in res["url_roles"].items()},
                               ensure_ascii=False), json.dumps(res["url_roles"]["role_mixing"][:5], ensure_ascii=False))
print("chain:", json.dumps({k: v for k, v in chain.items() if k != "problems"}, ensure_ascii=False),
      "problems:", json.dumps(chain["problems"][:10], ensure_ascii=False))
print("sources:", json.dumps({k: (v if not isinstance(v, list) or len(v) < 15 else f"{len(v)} items")
                              for k, v in res["sources"].items()}, ensure_ascii=False))
print("teslimler:", json.dumps({k: v for k, v in res["teslimler"].items() if k != "pkg_inventory"},
                               ensure_ascii=False))
print("pkg_inventory:", json.dumps(res["teslimler"]["pkg_inventory"], ensure_ascii=False))
print("inventory:", json.dumps({k: v for k, v in res["inventory"].items() if k != "dup_sha"}, ensure_ascii=False))
print("longest:", res["longest_cell"], "ekdetaylar:", res["ekdetaylar_rows"])
