"""onceki.py: onceki L0 (2026-10-22) ile bu L0b denetiminin karsilastirmasi (salt okunur; cikti OUT altina).

Kullanim: python -I -X utf8 onceki.py <OUT> <ONCEKI_OUT> <PKG>
Girdi: OUT ve ONCEKI_OUT altindaki _dump/*.jsonl, issues.json, claim-script.json, url-checks*.json, impact.json;
       PKG/Teslimler/ILERLEME_KAYDI.txt (yalniz okunur).
Cikti: OUT/_analiz/onceki-karsilastirma.json ve stdout ozet.
"""
from __future__ import annotations

import collections
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

OUT, PREV, PKG = (Path(a) for a in sys.argv[1:4])


def jl(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as stream:
        return [json.loads(line) for line in stream if line.strip()]


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump(base: Path) -> dict[str, list[dict]]:
    return {p.stem: jl(p) for p in sorted((base / "_dump").glob("*.jsonl")) if p.stat().st_size}


new, old = dump(OUT), dump(PREV)
res: dict = {}

# ---------------------------------------------------------------- mekanlar: eklenen / cikan
old_places = {r["entry_id"]: r for r in old["Mekânlar"]}
new_places = {r["entry_id"]: r for r in new["Mekânlar"]}
added = sorted(set(new_places) - set(old_places))
removed = sorted(set(old_places) - set(new_places))
photo_count = collections.Counter(p.get("entry_id") for p in new["Fotoğraflar"] if p.get("role") != "Kapak")
res["places_added"] = [{"entry_id": e, "row": new_places[e]["_row"], "title": new_places[e].get("title"),
                        "group": new_places[e].get("group"), "photos": photo_count.get(e, 0),
                        "source_ids": new_places[e].get("source_ids")} for e in added]
res["places_removed"] = removed
res["group_old"] = dict(collections.Counter(r.get("group") for r in old["Mekânlar"]))
res["group_new"] = dict(collections.Counter(r.get("group") for r in new["Mekânlar"]))

# ---------------------------------------------------------------- ISS-003: fotografsiz kayitlar
prev_issues = {i["issue_id"]: i for i in load(PREV / "issues.json")["issues"]}
old_wo = [x.strip() for x in prev_issues["ISS-003"]["entry_id/photo_id"].split(",")]
ids_all = {r["entry_id"]: (s, r) for s in ("Mekânlar", "Mahalleler") for r in new[s]}
now_wo = [e for e, (s, r) in ids_all.items() if photo_count.get(e, 0) == 0]
res["iss003"] = {
    "old_without": len(old_wo), "now_without": len(now_wo),
    "closed": [{"entry_id": e, "photos": photo_count.get(e, 0)} for e in old_wo if photo_count.get(e, 0) > 0],
    "still": [e for e in old_wo if e in now_wo],
    "new_without": [{"entry_id": e, "sheet": ids_all[e][0], "row": ids_all[e][1]["_row"],
                     "title": ids_all[e][1].get("title"), "new_entry": e in added}
                    for e in now_wo if e not in old_wo],
    "removed_from_package": [e for e in old_wo if e not in ids_all],
    "now_without_rows": {s: [r["_row"] for e, (sh, r) in ids_all.items() if sh == s and e in now_wo]
                         for s in ("Mekânlar", "Mahalleler")},
    "now_without_ids": now_wo,
}

# ---------------------------------------------------------------- ISS-007: Yanitlar!194 opstal karti
OPSTAL = "eindhoven:ev-sigortalari-opstal-inboedel-aansprakelijkheid"
o_card = next((r for r in old["Yanıtlar"] if r["entry_id"] == OPSTAL), {})
n_card = next((r for r in new["Yanıtlar"] if r["entry_id"] == OPSTAL), {})
res["iss007"] = {"row_old": o_card.get("_row"), "row_new": n_card.get("_row"),
                 "changed_fields": sorted(k for k in set(o_card) | set(n_card)
                                          if k != "_row" and o_card.get(k) != n_card.get(k)),
                 "old_summary": o_card.get("summary"), "new_summary": n_card.get("summary"),
                 "old_note": o_card.get("note"), "new_note": n_card.get("note"),
                 "new_source_ids": n_card.get("source_ids"), "old_source_ids": o_card.get("source_ids")}
for key in ("summary", "note", "steps", "cost", "timing", "documents"):
    text = str(n_card.get(key) or "")
    for rx in (r"yasal dayana", r"doğrulanamadı", r"göstermiyor", r"zorunlu"):
        if re.search(rx, text, re.I):
            res["iss007"].setdefault("hits", []).append({"field": key, "pattern": rx})

# ---------------------------------------------------------------- hedge/evasive kartlari: degisti mi
def card(rows, entry):
    return next((r for r in rows if r.get("entry_id") == entry), {})


for entry in ("eindhoven:turkiye-belgeleri-apostilsiz", "eindhoven:inburgering-ucretleri-duo-kredisi"):
    a, b = card(old["Yanıtlar"], entry), card(new["Yanıtlar"], entry)
    res.setdefault("tq_cards", {})[entry] = {
        "row": b.get("_row"), "changed_fields": sorted(k for k in set(a) | set(b) if k != "_row" and a.get(k) != b.get(k))}

# ---------------------------------------------------------------- ISS-005: ILERLEME_KAYDI son kayit
log = (PKG / "Teslimler" / "ILERLEME_KAYDI.txt").read_text(encoding="utf-8-sig")
blocks = [b.strip() for b in re.split(r"(?m)^(?==== )", log) if b.strip()]
res["iss005"] = {"records": len(blocks), "identical_trailing": 0, "last": blocks[-1] if blocks else ""}
if blocks:
    res["iss005"]["identical_trailing"] = sum(1 for b in blocks if b == blocks[-1])
    m = re.search(r"İndirilmiş fotoğraflar:\s*(\d+)", blocks[-1])
    s = re.search(r"Araştırılan resmî kaynaklar:\s*(\d+)", blocks[-1])
    res["iss005"]["last_downloaded_photos"] = int(m.group(1)) if m else None
    res["iss005"]["last_official_sources"] = int(s.group(1)) if s else None

# ---------------------------------------------------------------- K14: reviewed_on ile kaynak tarihi
src_date = {s["source_id"]: s.get("checked_on") for s in new["Kaynaklar"]}
late = []
for sheet in ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük"):
    for r in new[sheet]:
        ids = [x.strip() for x in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if x.strip()]
        newest = max((src_date.get(i) or "" for i in ids), default="")
        text = " ".join(str(v) for k, v in r.items() if isinstance(v, str))
        dated_note = bool(re.search(r"23\.10\.2026|23 Ekim 2026", text))
        if (newest and str(r.get("reviewed_on")) < newest) or (dated_note and str(r.get("reviewed_on")) < "2026-10-23"):
            late.append({"sheet": sheet, "row": r["_row"], "id": r.get("entry_id") or r.get("route_id")
                         or r.get("term_id"), "reviewed_on": r.get("reviewed_on"), "newest_source_checked_on": newest,
                         "sources_checked_2026_10_23": [i for i in ids if src_date.get(i) == "2026-10-23"],
                         "text_dated_23_10": dated_note})
res["k14_review_before_source"] = late
links_late = [{"row": r["_row"], "id": r["action_id"], "entry_id": r.get("entry_id"), "checked_on": r.get("checked_on")}
              for r in new["Bağlantılar"] if r.get("checked_on") == "2026-10-23"]
res["links_checked_2026_10_23"] = links_late
res["sources_checked_2026_10_23"] = [{"source_id": s["source_id"], "row": s["_row"], "url": s.get("url"),
                                      "publisher": s.get("publisher")}
                                     for s in new["Kaynaklar"] if s.get("checked_on") == "2026-10-23"]

# ---------------------------------------------------------------- iddia: not_in_source karsilastirmasi
def nis(base: Path):
    data = load(base / "claim-script.json")
    return {(r["entry_id"], r["field"], json.dumps(r.get("values"), ensure_ascii=False)): r
            for r in data["results"] if r["result"] != "supported"}


n_nis, o_nis = nis(OUT), nis(PREV)
res["claims_not_supported"] = {
    "now": len(n_nis), "before": len(o_nis),
    "same": len(set(n_nis) & set(o_nis)),
    "new": [{"entry_id": k[0], "field": k[1], "values": k[2], "row": v.get("_row"), "result": v["result"],
             "sentence": (v.get("sentence") or "")[:200]} for k, v in n_nis.items() if k not in o_nis],
    "gone": [{"entry_id": k[0], "field": k[1], "values": k[2]} for k in o_nis if k not in n_nis],
    "all_now": [{"entry_id": k[0], "field": k[1], "values": k[2], "row": v.get("_row"), "result": v["result"],
                 "sentence": (v.get("sentence") or "")[:160]} for k, v in n_nis.items()],
}

# ---------------------------------------------------------------- URL bayraklari karsilastirmasi
def url_flags(paths: list[Path]):
    found = {}
    for path in paths:
        if path.exists():
            for u in load(path)["urls"]:
                found[u["ham_URL"]] = u
    return found


n_urls = url_flags([OUT / "url-checks.json"])
o_urls = url_flags([PREV / "url-checks.json", PREV / "url-checks-sehir-sayfa.json"])
flagged = []
for url, u in n_urls.items():
    flags = [f for f in (u.get("flags") or []) if f not in ("wikipedia",)]
    if flags or u.get("class") not in ("ok_200", "redirect_ok"):
        o = o_urls.get(url)
        flagged.append({"url": url, "class": u.get("class"), "flags": flags, "final": u.get("son_URL"),
                        "rows": u.get("Excel_satırları"), "ids": u.get("bağlı_IDler"),
                        "status": u.get("HTTP_durumu"), "verdict": u.get("erişim_sonucu"),
                        "in_previous": o is not None,
                        "previous_flags": (o.get("flags") if o else None), "previous_class": (o.get("class") if o else None)})
res["url_flagged"] = flagged
res["url_counts"] = {"now": len(n_urls), "before": len(o_urls), "new_urls": len(set(n_urls) - set(o_urls)),
                     "gone_urls": len(set(o_urls) - set(n_urls))}

# ---------------------------------------------------------------- impact ozeti
imp = load(OUT / "impact.json")
by = collections.defaultdict(lambda: collections.Counter())
fields = collections.defaultdict(collections.Counter)
for c in imp["changes"]:
    by[c["sheet"]][c["change"]] += 1
    for f in c.get("fields", []):
        fields[c["sheet"]][f] += 1
res["impact"] = {"counts": imp["counts"], "by_sheet": {k: dict(v) for k, v in by.items()},
                 "changed_fields": {k: dict(v.most_common(12)) for k, v in fields.items()},
                 "changed_answers": [c["id"] for c in imp["changes"] if c["sheet"] == "Yanıtlar"],
                 "changed_routes": [{"id": c["id"], "fields": c.get("fields")} for c in imp["changes"]
                                    if c["sheet"] == "Rotalar"],
                 "changed_konular": [{"id": c["id"], "fields": c.get("fields")} for c in imp["changes"]
                                     if c["sheet"] == "Konular"],
                 "changed_sehir": [{"id": c["id"], "fields": c.get("fields")} for c in imp["changes"]
                                   if c["sheet"] == "Şehir"]}

(OUT / "_analiz" / "onceki-karsilastirma.json").write_text(json.dumps(res, ensure_ascii=False, indent=1),
                                                          encoding="utf-8")
print("places_added:", json.dumps(res["places_added"], ensure_ascii=False))
print("places_removed:", removed)
print("group old/new:", res["group_old"], res["group_new"])
print("iss003:", json.dumps({k: v for k, v in res["iss003"].items() if k not in ("now_without_ids", "still")},
                            ensure_ascii=False))
print("iss007:", json.dumps(res["iss007"], ensure_ascii=False)[:3000])
print("tq_cards:", json.dumps(res["tq_cards"], ensure_ascii=False))
print("iss005:", json.dumps({k: v for k, v in res["iss005"].items() if k != "last"}, ensure_ascii=False))
print("k14 late:", len(late), json.dumps(late, ensure_ascii=False)[:4000])
print("links 23:", json.dumps(links_late, ensure_ascii=False))
print("sources 23:", json.dumps(res["sources_checked_2026_10_23"], ensure_ascii=False)[:3000])
print("claims:", json.dumps({k: v for k, v in res["claims_not_supported"].items() if k != "all_now"},
                            ensure_ascii=False)[:3000])
print("url_counts:", res["url_counts"])
for f in flagged:
    print("url:", json.dumps(f, ensure_ascii=False)[:600])
print("impact:", json.dumps(res["impact"], ensure_ascii=False)[:4000])
