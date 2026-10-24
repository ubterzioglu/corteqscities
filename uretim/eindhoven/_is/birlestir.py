"""Yazar parcalarini birlestirir ve kapi oncesi deterministik kontrol yapar (pilot is script'i, toolkit degil).

Kullanim: python birlestir.py <_is klasoru>
Okur: data/parcalar/<Sekme>.<parca>.jsonl, claims/*.jsonl, kaynak_dizini.jsonl, kaynak_taslak.jsonl
Yazar: data/<Sekme>.jsonl (Yanıtlar, Bağlantılar, Adımlar, Mekânlar, Mahalleler, Rotalar, Sözlük, SayfaAlanları, Şehir),
       data/Kaynaklar.jsonl (yalniz kullanilan kaynaklar, verified=Evet), birlestir_rapor.json.
stdout tek satir JSON; cikis 0 temiz / 1 bulgu. Parcasi olmayan sekme yazilmaz (sablondaki gibi kalir).
"""
from __future__ import annotations

import collections
import glob
import json
import os
import re
import sys
import unicodedata

CITY = "eindhoven"
COMMON = ["entry_id", "city_id", "slug", "title", "subtitle", "summary", "keywords", "stages", "source_ids",
          "reviewed_on", "order", "featured", "editorial_status"]
SHEETS = {
    "Teslimat": ["schema_version", "delivery_id", "city_id", "editor", "reviewer", "scope", "updated_on",
                 "editorial_status", "notes"],
    "Yanıtlar": COMMON + ["topic_id", "steps", "documents", "timing", "cost", "note", "visual_json"],
    "Mekânlar": COMMON + ["group", "district", "setting", "location", "latitude", "longitude", "visit_status", "note",
                          "collection", "media_key"],
    "Mahalleler": COMMON + ["location", "tags", "compare_json", "note", "media_key"],
    "Bağlantılar": ["action_id", "city_id", "entry_id", "label", "url", "checked_on", "order"],
    "Adımlar": ["step_id", "city_id", "entry_id", "title", "when", "description", "order"],
    "Rotalar": ["route_id", "city_id", "title", "tag", "stops", "stop_entry_ids", "entry_id", "note", "reviewed_on",
                "source_ids", "order", "editorial_status"],
    "Sözlük": ["term_id", "city_id", "term", "definition", "source_ids", "reviewed_on", "order", "editorial_status"],
    "SayfaAlanları": ["field_id", "city_id", "key", "label", "value_type", "value", "reviewed_on"],
    # Fotoğraflar: formül sütunları (unique_venue_count, unique_hero_count) bilerek yok; yazılamaz.
    "Fotoğraflar": ["photo_id", "city_id", "role", "entry_id", "file", "sha256", "caption", "author", "license",
                    "license_url", "source_url", "capture_date", "source_checked_on", "modifications", "evidence_id",
                    "completion_credit", "order", "editorial_status"],
    "Kanıtlar": ["evidence_id", "city_id", "photo_id", "source_url", "source_title", "author", "license", "license_url",
                 "usage_terms", "attribution", "restrictions", "checked_on", "metadata_review_status",
                 "pixel_review_status", "pixel_review_file", "pixel_review_note", "rights_status", "rights_basis",
                 "source_snapshot_file", "source_snapshot_sha256", "license_snapshot_file", "license_snapshot_sha256",
                 "source_evidence_json"],
    "FotoğrafKaynakları": ["photo_id", "author_url", "attribution_url", "original_file_url", "downloaded_file_url",
                           "downloaded_on", "original_file", "original_sha256", "web_file", "web_sha256", "web_width",
                           "web_height", "derivation", "provenance_status", "provenance_note"],
    "Şehir": ["city_id", "name", "country", "country_code", "region", "kind", "title", "intro", "currency",
              "currency_symbol", "currency_label", "language", "timezone", "latitude", "longitude",
              "coordinate_source_url", "coordinate_checked_on", "coordinate_note", "source_url", "source_checked_on",
              "source_position", "reviewed_on", "priority", "aliases", "locality", "tagline", "directory_order",
              "forecast_url", "provider_url", "forecast_label", "hero_photo_id", "editorial_notes", "editorial_status"],
}
ENTRY_SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler")
GROUPS = {"Müzeler", "Sanat ve sergiler", "Sahne ve müzik", "Spor", "Doğa ve açık hava", "Çocuklarla keşif",
          "Yeme ve içme", "Tarih ve mimari"}
SETTINGS = {"Kapalı alan", "Açık hava", "Karma"}
STAGES = {"before", "planning", "new", "settled"}
PAGE_KEYS = {"hero_kicker", "hero_accent", "hero_note", "topic_title", "topic_intro", "journey_title", "journey_intro",
             "neighborhood_title", "neighborhood_intro", "explore_title", "explore_intro", "sources_note",
             "photo_credit", "arrival_note", "emergency_url", "pharmacy_url", "advice_entry", "facts", "quick_links",
             "timeline", "budget_fields", "place_groups", "emergency"}
RESERVED_PAGE_KEYS = {"routes", "glossary", "directory", "currency", "currency_symbol", "currency_label",
                      "reviewed_on", "weather"}
ID_RE = re.compile(r"^[a-z0-9][a-z0-9:_-]*$")
PLACEHOLDERS = {"-", "?", "null", "none", "bilinmiyor", "yok", "n/a"}
FILLER = re.compile(r"(kurumdan doğrula|güncel bilgi için|resmî siteyi kontrol|değişebilir, lütfen)", re.I)


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", str(text)).replace(" ", " ")
    return re.sub(r"\s+", " ", text).strip().casefold()


def read_jsonl(path: str) -> list[dict]:
    rows = []
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as e:
                rows.append({"_bad": f"{os.path.basename(path)}:{n}: {e}"})
    return rows


def ids(value) -> list[str]:
    return [s for s in str(value or "").split(";") if s]


def merge(w: str, sheet: str, issues: list) -> list[dict]:
    keys, rows = SHEETS[sheet], []
    for path in sorted(glob.glob(os.path.join(w, "data", "parcalar", f"{sheet}.*.jsonl"))):
        part = os.path.basename(path).split(".")[1]
        for r in read_jsonl(path):
            if "_bad" in r:
                issues.append(("json", sheet, r["_bad"]))
                continue
            extra = sorted(set(r) - set(keys) - {"_row", "source_urls"})
            if [k for k in r if k in keys] != keys or extra:
                issues.append(("keys", sheet, part, r.get(keys[0]), extra or sorted(set(keys) - set(r))))
            if r.get("source_urls") and not r.get("source_ids"):
                issues.append(("source_urls_unmapped", sheet, part, r.get(keys[0])))
            rows.append({k: r.get(k, "") for k in keys} | {"_part": part})
    return rows


def check_entries(sheet: str, rows: list[dict], sources: dict, issues: list) -> None:
    for a in rows:
        eid, part = a["entry_id"], a["_part"]
        if eid != f"{CITY}:{a['slug']}" or not ID_RE.match(eid) or len(a["slug"]) > 120:
            issues.append(("entry_id", sheet, part, eid))
        if a["city_id"] != CITY or not a["summary"] or len(a["title"]) > 180 or len(str(a["subtitle"] or "")) > 160:
            issues.append(("required_or_len", sheet, part, eid))
        if a["stages"] and not set(ids(a["stages"])) <= STAGES:
            issues.append(("stages", sheet, part, eid, a["stages"]))
        sids = ids(a["source_ids"])
        if not sids or len(sids) != len(set(sids)) or any(s not in sources for s in sids):
            issues.append(("source_ids", sheet, part, eid, a["source_ids"]))
        if not isinstance(a["order"], int) or a["featured"] not in ("Evet", "Hayır") or a["editorial_status"] != "Taslak":
            issues.append(("enum_order", sheet, part, eid))
        for k in ("subtitle", "note"):
            if norm(a.get(k) or "") in PLACEHOLDERS:
                issues.append(("placeholder", sheet, part, eid, k))
        if FILLER.search(str(a["summary"]) + " " + str(a.get("note") or "")):
            issues.append(("filler", sheet, part, eid))


def check_answers(rows: list[dict], issues: list) -> None:
    for a in rows:
        eid, part = a["entry_id"], a["_part"]
        if a["topic_id"] != f"{CITY}:{part}" or not a["steps"]:
            issues.append(("topic_or_steps", part, eid))
        lines = [s for s in str(a["steps"]).split("\n") if s.strip()]
        if len(lines) != len(set(lines)):
            issues.append(("dup_step_line", part, eid))
        for k in ("cost", "timing", "documents"):
            if norm(a[k] or "") in PLACEHOLDERS:
                issues.append(("placeholder", part, eid, k))
        if a["visual_json"]:
            try:
                assert isinstance(json.loads(a["visual_json"]), dict)
            except Exception:
                issues.append(("visual_json", part, eid))
    for p, n in collections.Counter(a["_part"] for a in rows if a["featured"] == "Evet").items():
        if n > 2:
            issues.append(("featured>2", p, n))


def check_places(rows: list[dict], issues: list) -> None:
    for p in rows:
        eid = p["entry_id"]
        if p["group"] not in GROUPS or p["setting"] not in SETTINGS or not p["district"] or not p["location"]:
            issues.append(("place_enum", eid, p["group"], p["setting"]))
        lat, lon = p["latitude"], p["longitude"]
        if (lat in ("", None)) != (lon in ("", None)):
            issues.append(("coord_pair", eid))
        elif lat not in ("", None) and not (isinstance(lat, (int, float)) and 51.3 < lat < 51.55 and 5.3 < lon < 5.6):
            issues.append(("coord_range", eid, lat, lon))
        if p["collection"] not in ("Evet", "Hayır"):
            issues.append(("collection", eid))
    noncol = {p["group"] for p in rows if p["collection"] == "Hayır"}
    if rows and GROUPS - noncol:
        issues.append(("groups_without_place", sorted(GROUPS - noncol)))


def check_neighborhoods(rows: list[dict], issues: list) -> None:
    keysets = set()
    for n in rows:
        try:
            cj = json.loads(n["compare_json"])
            ok = isinstance(cj, dict) and len(cj) >= 4 and all(isinstance(v, str) and v.strip() for v in cj.values())
            keysets.add(tuple(sorted(cj))) if ok else issues.append(("compare_json", n["entry_id"]))
        except Exception:
            issues.append(("compare_json", n["entry_id"]))
        if not n["location"]:
            issues.append(("location", n["entry_id"]))
    if len(keysets) > 1:
        issues.append(("compare_json_keysets_differ", len(keysets)))


def check_page(rows: list[dict], slugs: set, issues: list) -> None:
    keys = collections.Counter(r["key"] for r in rows)
    if rows:
        if set(keys) != PAGE_KEYS or any(v > 1 for v in keys.values()):
            issues.append(("page_keys", sorted(PAGE_KEYS - set(keys)), sorted(set(keys) - PAGE_KEYS)))
        if set(keys) & RESERVED_PAGE_KEYS:
            issues.append(("page_reserved", sorted(set(keys) & RESERVED_PAGE_KEYS)))
    for r in rows:
        if r["field_id"] != f"{CITY}:field:{r['key']}":
            issues.append(("field_id", r["field_id"]))
        if r["value_type"] == "JSON":
            try:
                val = json.loads(r["value"])
            except Exception:
                issues.append(("page_json", r["key"]))
                continue
            for item in val if isinstance(val, list) else []:
                if isinstance(item, dict) and item.get("entry") and item["entry"] not in slugs:
                    issues.append(("page_entry_missing", r["key"], item["entry"]))
        if r["key"] == "advice_entry" and r["value"] not in slugs:
            issues.append(("advice_entry_missing", r["value"]))


def main(w: str) -> int:
    issues: list = []
    sources = {r["source_id"]: r for r in read_jsonl(os.path.join(w, "kaynak_dizini.jsonl"))}
    url_to_src = {}
    for s in sources.values():
        url_to_src[s["url"]] = s["source_id"]
        if s.get("final_url"):
            url_to_src.setdefault(s["final_url"], s["source_id"])
    texts: dict[str, str] = {}

    def text_of(sid: str) -> str:
        if sid not in texts:
            texts[sid] = norm(open(sources[sid]["text_file"], encoding="utf-8").read())
        return texts[sid]

    data = {s: merge(w, s, issues) for s in SHEETS}
    entries = [r for s in ENTRY_SHEETS for r in data[s]]
    eid_count = collections.Counter(r["entry_id"] for r in entries)
    title_count = collections.Counter(norm(r["title"]) for r in entries)
    issues += [("dup_entry", e) for e, n in eid_count.items() if n > 1]
    issues += [("dup_title", t) for t, n in title_count.items() if n > 1]
    for s in ENTRY_SHEETS:
        check_entries(s, data[s], sources, issues)
    check_answers(data["Yanıtlar"], issues)
    check_places(data["Mekânlar"], issues)
    check_neighborhoods(data["Mahalleler"], issues)
    slugs = {r["slug"] for r in entries}
    check_page(data["SayfaAlanları"], slugs, issues)

    used = {s for sh in ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük") for r in data[sh]
            for s in ids(r.get("source_ids")) if s in sources}
    act_ids = collections.Counter(x["action_id"] for x in data["Bağlantılar"])
    with_action = set()
    for x in data["Bağlantılar"]:
        if x["entry_id"] not in eid_count:
            issues.append(("action_entry", x["_part"], x["action_id"]))
        if act_ids[x["action_id"]] > 1 or not ID_RE.match(x["action_id"]):
            issues.append(("action_id", x["_part"], x["action_id"]))
        if "wikipedia" in x["url"] or not str(x["url"]).startswith("https://"):
            issues.append(("action_url", x["_part"], x["url"]))
        elif x["url"] in url_to_src:
            used.add(url_to_src[x["url"]])
        else:
            issues.append(("action_url_not_in_sources", x["_part"], x["action_id"], x["url"]))
        with_action.add(x["entry_id"])
    issues += [("no_action", r["entry_id"]) for r in entries if r["entry_id"] not in with_action]
    for s in data["Adımlar"]:
        if s["entry_id"] not in eid_count or len(s["title"]) > 120 or len(s["when"]) > 90 or len(s["description"]) > 250:
            issues.append(("step", s["step_id"]))
    place_ids = {p["entry_id"] for p in data["Mekânlar"]}
    for r in data["Rotalar"]:
        stops, sids = [x for x in str(r["stops"]).split("\n") if x.strip()], ids(r["stop_entry_ids"])
        if not 2 <= len(sids) <= 8 or len(sids) != len(set(sids)) or len(stops) != len(sids) \
                or any(s not in place_ids for s in sids) or r["entry_id"] != (sids[0] if sids else None):
            issues.append(("route", r["route_id"]))
    for sh in ("Adımlar", "Rotalar", "Sözlük"):
        dup = [o for o, n in collections.Counter(r["order"] for r in data[sh]).items() if n > 1]
        if dup:
            issues.append(("order_dup", sh, dup[:5]))
    for r in data["Sözlük"]:
        if not ID_RE.match(r["term_id"]) or not ids(r["source_ids"]) or any(s not in sources for s in ids(r["source_ids"])):
            issues.append(("term", r["term_id"]))

    known = (set(eid_count) | {r["term_id"] for r in data["Sözlük"]} | {r["field_id"] for r in data["SayfaAlanları"]}
             | {r["route_id"] for r in data["Rotalar"]} | {CITY})
    claims_total, quote_miss = 0, []
    for path in sorted(glob.glob(os.path.join(w, "claims", "*.jsonl"))):
        for c in read_jsonl(path):
            claims_total += 1
            owner = c.get("entry_id") or c.get("term_id") or c.get("field_id") or c.get("route_id")
            sid = c.get("source_id") if c.get("source_id") in sources else url_to_src.get(c.get("url") or "")
            quote = c.get("quote") or ""
            if owner not in known:
                quote_miss.append((os.path.basename(path), c.get("claim_id"), "sahip_yok", owner))
            elif not sid:
                quote_miss.append((os.path.basename(path), c.get("claim_id"), "kaynak_yok"))
            elif not quote or norm(quote) not in text_of(sid):
                quote_miss.append((os.path.basename(path), c.get("claim_id"), "alinti_metinde_yok"))

    out = os.path.join(w, "data")
    for sheet, rows in data.items():
        if rows:
            with open(os.path.join(out, f"{sheet}.jsonl"), "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps({k: r[k] for k in SHEETS[sheet]}, ensure_ascii=False) + "\n")
    with open(os.path.join(out, "Kaynaklar.jsonl"), "w", encoding="utf-8") as f:
        for r in read_jsonl(os.path.join(w, "kaynak_taslak.jsonl")):
            if r["source_id"] in used:
                f.write(json.dumps({**r, "verified": "Evet"}, ensure_ascii=False) + "\n")
    report = {"rows": {s: len(r) for s, r in data.items() if r},
              "per_topic": dict(collections.Counter(a["_part"] for a in data["Yanıtlar"])),
              "places_by_group": dict(collections.Counter(p["group"] for p in data["Mekânlar"])),
              "sources_used": len(used), "claims": claims_total, "quote_miss": len(quote_miss),
              "issue_kinds": dict(collections.Counter(i[0] for i in issues))}
    json.dump({**report, "issues": issues, "quote_miss_list": quote_miss},
              open(os.path.join(w, "birlestir_rapor.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(report, ensure_ascii=False))
    return 1 if issues or quote_miss else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
