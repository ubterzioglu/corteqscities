"""Yazar parcalarini sekmelere birlestirir, kapi oncesi deterministik kontrol yapar (A6; pilot: birlestir.py).

Kullanim:
  merge_package.py <is_klasoru> --city-id eindhoven --bbox 51.3,51.55,5.3,5.6 [--data-out D] [--out R.json]
Okur: <is>/data/parcalar/<Sekme>.<parca>.jsonl, <is>/claims/*.jsonl, <is>/kaynak_dizini.jsonl, <is>/kaynak_taslak.jsonl,
      varsa <is>/data/Teslimat.jsonl (SKILL.md: parcadan degil dogrudan yazilir; yalniz onay alanlari denetlenir,
      birlestirilmez ve yeniden yazilmaz).
Yazar: <data-out>/<Sekme>.jsonl (yalniz parcasi olan sekmeler; olmayan sablondaki gibi kalir),
       <data-out>/Kaynaklar.jsonl (yalniz kullanilan kaynaklar, verified=Evet) ve --out rapor
       {ozet, issues, quote_miss_list, claims_only_sources}.
       Varsayilan: --data-out <is>/data, --out <is>/birlestir_rapor.json.
--bbox LAT_MIN,LAT_MAX,LON_MIN,LON_MAX: mekan koordinat kutusu (sinirlar haric). Sehir satirinin koordinati da kutuda
olmali; enlem ile boylam sirasi karisirsa 'city_outside_bbox' bulgusu cikar.
Iddia alintisi kaynak metninde (NFKC + bosluk + harf buyuklugu normalize) birebir aranir.
Kullanilan kaynak: giris/rota/terim source_ids'i, baglanti adresi ve icerigin (sahibi bilinen) iddialarinin dayandigi
kaynak. SayfaAlanları'nin source_ids sutunu yok: sayfa/Sehir metnini kaynagina yalniz iddia defteri baglar; yalniz
iddialardan gelenler ozette 'sources_claims_only' olarak sayilir. Giris/rota/terim iddiasinin kaynagi o kaydin kendi
source_ids'inde yoksa (web karti kaynaklari source_ids'ten gosterir) 'claim_source_not_in_owner' [iddia dosyasi,
claim_id, sahip, kaynak] bulgusudur; kaynak yine kullanilan sayilir. Kaynaklar satiri kaynak_taslak'tan gelir; taslakta
satiri olmayan kullanilan kaynak 'source_not_in_draft' bulgusudur (sessizce dusmez).
Skill kendi isini onaylamaz (K97): onay alani tasiyan her sekmede (editorial_status; Kanıtlar inceleme alanlari;
Teslimat.reviewer) AI'in yazamayacagi deger [alan, sekme, parca, kimlik, deger] bulgusudur (bkz. ai_values).
SayfaAlanları: eksik/yinelenen/bilinmeyen anahtar 'page_keys', ayrilmis anahtar (routes, weather...) yalniz
'page_reserved' olarak raporlanir (her kural kendi bulgusu).
stdout tek satir JSON; cikis 0 temiz / 1 bulgu (kural ihlali ya da alinti/kaynak eksigi) / 2 kullanim (okunamayan ya
da UTF-8 olmayan girdi, yazilamayan cikti dahil; bozuk JSON satiri ise bulgudur).
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import (EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, HUMAN_PENDING_VALUE, HUMAN_REVIEW_KEYS, SINGLE_ROW_SHEETS,
                    emit, setup_utf8, write_json)

COMMON = ["entry_id", "city_id", "slug", "title", "subtitle", "summary", "keywords", "stages", "source_ids",
          "reviewed_on", "order", "featured", "editorial_status"]
SHEETS = {
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
    # Fotoğraflar: formul sutunlari (unique_venue_count, unique_hero_count) bilerek yok; yazilamaz.
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
# Parcadan degil dogrudan <is>/data/ altina yazilan sekme (SKILL.md); yalniz onay alanlari denetlenir.
DIRECT_SHEETS = {"Teslimat": ["schema_version", "delivery_id", "city_id", "editor", "reviewer", "scope", "updated_on",
                              "editorial_status", "notes"]}
DIRECT_PART = "data"  # dogrudan dosyanin bulgulardaki parca adi
EDITORIAL_PENDING = "Taslak"
ENTRY_SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler")
SOURCE_SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük")
ORDERED_SHEETS = ("Adımlar", "Rotalar", "Sözlük")
OWNER_FIELDS = (("Sözlük", "term_id"), ("SayfaAlanları", "field_id"), ("Rotalar", "route_id"))
CLAIM_OWNER_KEYS = ("entry_id", "term_id", "field_id", "route_id")
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
ID_RE = re.compile(r"^[a-z0-9][a-z0-9:_-]*\Z")
CITY_RE = re.compile(r"^[a-z0-9-]+\Z")
PLACEHOLDERS = {"-", "?", "null", "none", "bilinmiyor", "yok", "n/a"}
FILLER = re.compile(r"(kurumdan doğrula|güncel bilgi için|resmî siteyi kontrol|değişebilir, lütfen)", re.I)
REPORT_NAME = "birlestir_rapor.json"
NO_COORD = ("", None)


class UsageError(Exception):
    """Eksik/bozuk zorunlu girdi ya da gecersiz arguman (cikis 2)."""


@dataclass(frozen=True)
class Box:
    """Koordinat kutusu; sinirlar haric (pilotla ayni: 51.3 < enlem < 51.55)."""
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float

    def contains(self, lat: Any, lon: Any) -> bool:
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool) for v in (lat, lon)):
            return False
        return self.lat_min < lat < self.lat_max and self.lon_min < lon < self.lon_max


@dataclass(frozen=True)
class Context:
    city: str
    box: Box


@dataclass(frozen=True)
class Paths:
    parts: Path
    direct: Path  # <is>/data: dogrudan yazilan sekme dosyalari (Teslimat)
    claims: Path
    sources: Path
    draft: Path
    data_out: Path
    report: Path


# ---------------------------------------------------------------- argumanlar ve okuma

def parse_bbox(text: str) -> Box:
    parts = [p.strip() for p in str(text).split(",")]
    if len(parts) != 4:
        raise ValueError("--bbox dort sayi olmali: LAT_MIN,LAT_MAX,LON_MIN,LON_MAX")
    try:
        lat_min, lat_max, lon_min, lon_max = (float(p) for p in parts)
    except ValueError as error:
        raise ValueError(f"--bbox sayi degil: {text}") from error
    if not (-90 <= lat_min < lat_max <= 90 and -180 <= lon_min < lon_max <= 180):
        raise ValueError(f"--bbox araligi gecersiz (min < max; enlem -90..90, boylam -180..180): {text}")
    return Box(lat_min, lat_max, lon_min, lon_max)


def _bbox_arg(text: str) -> Box:
    try:
        return parse_bbox(text)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from error


def _city_arg(text: str) -> str:
    if not CITY_RE.match(text):
        raise argparse.ArgumentTypeError("kucuk harf ASCII/rakam/tire olmali (or. eindhoven)")
    return text


def norm(text: Any) -> str:
    text = unicodedata.normalize("NFKC", str(text))
    return re.sub(r"\s+", " ", text).strip().casefold()


def _s(value: Any) -> str:
    """Duzenli ifade / uzunluk / onek kontrolu icin metin (beklenmeyen tip cokertmez)."""
    return value if isinstance(value, str) else ("" if value is None else str(value))


def _key(value: Any) -> Any:
    """Sayac/kume anahtari: hashlenebilir deger aynen, liste/sozluk JSON metni olarak."""
    try:
        hash(value)
    except TypeError:
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return value


def ids(value: Any) -> list[str]:
    return [s for s in str(value or "").split(";") if s]


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Satir satir JSON; bozuk satir {'_bad': 'dosya:satir: hata'} olur (bulgu olarak raporlanir, cokertmez).
    UTF-8 olmayan dosya satir satir ayrilamaz: UsageError (cikis 2)."""
    rows: list[dict[str, Any]] = []
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    rows.append({"_bad": f"{Path(path).name}:{number}: {error.msg}"})
                    continue
                rows.append(row if isinstance(row, dict) else {"_bad": f"{Path(path).name}:{number}: nesne degil"})
    except UnicodeDecodeError as error:
        raise UsageError(f"{path}: UTF-8 degil ({error.reason})") from error
    return rows


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Zorunlu girdi: dosya yoksa ya da bozuk satir varsa UsageError."""
    if not Path(path).is_file():
        raise UsageError(f"dosya yok: {path}")
    rows = read_jsonl(path)
    bad = [r["_bad"] for r in rows if "_bad" in r]
    if bad:
        raise UsageError(f"bozuk JSON satiri: {bad[0]}")
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_sources(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    """(kaynak_id -> satir, url/final_url -> kaynak_id); url atamasi son satirla, final_url ilk eslesmeyle."""
    sources: dict[str, dict[str, Any]] = {}
    for row in load_jsonl(path):
        if not isinstance(row.get("source_id"), str) or not row["source_id"]:
            raise UsageError(f"{Path(path).name}: source_id eksik satir var")
        sources[row["source_id"]] = row
    url_to_src: dict[str, str] = {}
    for row in sources.values():
        if isinstance(row.get("url"), str):
            url_to_src[row["url"]] = row["source_id"]
        if isinstance(row.get("final_url"), str) and row["final_url"]:
            url_to_src.setdefault(row["final_url"], row["source_id"])
    return sources, url_to_src


def merge(parts_dir: Path, sheet: str, issues: list) -> list[dict[str, Any]]:
    """<Sekme>.<parca>.jsonl dosyalarini ad sirasiyla birlestirir; anahtar sirasi ve fazlasi denetlenir."""
    keys, rows = SHEETS[sheet], []
    for path in sorted(parts_dir.glob(f"{sheet}.*.jsonl"), key=lambda p: p.name):
        part = path.name.split(".")[1]
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


def read_direct(path: Path, sheet: str, issues: list) -> list[dict[str, Any]]:
    """Dogrudan data/ altina yazilan sekmenin satirlari (dosya yoksa bos); bozuk satir 'json' bulgusu."""
    rows: list[dict[str, Any]] = []
    for r in read_jsonl(path) if path.is_file() else []:
        if "_bad" in r:
            issues.append(("json", sheet, r["_bad"]))
        else:
            rows.append({**r, "_part": DIRECT_PART})
    return rows


# ---------------------------------------------------------------- onay alanlari (K97: skill kendi isini onaylamaz)

def ai_values(sheet: str, field: str) -> frozenset[str] | None:
    """Insan onayi alanina AI'in yazabilecegi degerler; onay alani degilse None (sozlesme §0 editorial_status, §2
    Kanıtlar ve Teslimat). Bos deger: build_xlsx hucreyi yazmaz; inceleme alanina 'Bekliyor' koyar, tek satirlik
    sayfada (Teslimat, Şehir) sablondaki deger kalir. Cok satirli sayfada bos editorial_status zorunlu alan
    eksigidir."""
    if field == "reviewer":  # Teslimat: AI icin bos, hazir kipi insan ister
        return frozenset({""})
    if field in HUMAN_REVIEW_KEYS:
        return frozenset({HUMAN_PENDING_VALUE, ""})
    if field == "editorial_status":
        return frozenset({EDITORIAL_PENDING, ""}) if sheet in SINGLE_ROW_SHEETS else frozenset({EDITORIAL_PENDING})
    return None


def check_approvals(sheet: str, rows: list[dict], issues: list) -> None:
    """Onay alani tasiyan her satirda yalniz AI'in yazabilecegi deger; bulgu [alan, sekme, parca, kimlik, deger]."""
    keys = SHEETS.get(sheet) or DIRECT_SHEETS[sheet]
    fields = {key: allowed for key in keys if (allowed := ai_values(sheet, key)) is not None}
    if not fields:
        return
    id_key = next(key for key in keys if key.endswith("_id"))  # entry/route/term/photo/evidence/city/delivery_id
    for row in rows:
        for field, allowed in fields.items():
            value = row.get(field)
            if _key("" if value is None else value) not in allowed:
                issues.append((field, sheet, row["_part"], row.get(id_key), value))


# ---------------------------------------------------------------- sekme kontrolleri

def check_entries(ctx: Context, sheet: str, rows: list[dict], sources: dict, issues: list) -> None:
    for a in rows:
        eid, part, slug = _s(a["entry_id"]), a["_part"], _s(a["slug"])
        if eid != f"{ctx.city}:{slug}" or not ID_RE.match(eid) or len(slug) > 120:
            issues.append(("entry_id", sheet, part, eid))
        if (a["city_id"] != ctx.city or not a["summary"] or len(_s(a["title"])) > 180
                or len(_s(a["subtitle"])) > 160):
            issues.append(("required_or_len", sheet, part, eid))
        if a["stages"] and not set(ids(a["stages"])) <= STAGES:
            issues.append(("stages", sheet, part, eid, a["stages"]))
        sids = ids(a["source_ids"])
        if not sids or len(sids) != len(set(sids)) or any(s not in sources for s in sids):
            issues.append(("source_ids", sheet, part, eid, a["source_ids"]))
        if not isinstance(a["order"], int) or a["featured"] not in ("Evet", "Hayır"):  # editorial_status: onay
            issues.append(("enum_order", sheet, part, eid))
        for k in ("subtitle", "note"):
            if norm(a.get(k) or "") in PLACEHOLDERS:
                issues.append(("placeholder", sheet, part, eid, k))
        if FILLER.search(f"{a['summary']} {a.get('note') or ''}"):
            issues.append(("filler", sheet, part, eid))


def _is_object_json(value: Any) -> bool:
    try:
        return isinstance(json.loads(value), dict)
    except (TypeError, ValueError):
        return False


def check_answers(ctx: Context, rows: list[dict], issues: list) -> None:
    for a in rows:
        eid, part = a["entry_id"], a["_part"]
        if a["topic_id"] != f"{ctx.city}:{part}" or not a["steps"]:
            issues.append(("topic_or_steps", part, eid))
        lines = [s for s in _s(a["steps"]).split("\n") if s.strip()]
        if len(lines) != len(set(lines)):
            issues.append(("dup_step_line", part, eid))
        for k in ("cost", "timing", "documents"):
            if norm(a[k] or "") in PLACEHOLDERS:
                issues.append(("placeholder", part, eid, k))
        if a["visual_json"] and not _is_object_json(a["visual_json"]):
            issues.append(("visual_json", part, eid))
    for part, count in collections.Counter(a["_part"] for a in rows if a["featured"] == "Evet").items():
        if count > 2:
            issues.append(("featured>2", part, count))


def check_places(ctx: Context, rows: list[dict], issues: list) -> None:
    for p in rows:
        eid = p["entry_id"]
        if (_key(p["group"]) not in GROUPS or _key(p["setting"]) not in SETTINGS or not p["district"]
                or not p["location"]):
            issues.append(("place_enum", eid, p["group"], p["setting"]))
        lat, lon = p["latitude"], p["longitude"]
        if (lat in NO_COORD) != (lon in NO_COORD):
            issues.append(("coord_pair", eid))
        elif lat not in NO_COORD and not ctx.box.contains(lat, lon):
            issues.append(("coord_range", eid, lat, lon))
        if p["collection"] not in ("Evet", "Hayır"):
            issues.append(("collection", eid))
    noncollection = {_key(p["group"]) for p in rows if p["collection"] == "Hayır"}
    if rows and GROUPS - noncollection:
        issues.append(("groups_without_place", sorted(GROUPS - noncollection)))


def _compare_object(value: Any) -> dict | None:
    try:
        data = json.loads(value)
    except (TypeError, ValueError):
        return None
    valid = isinstance(data, dict) and len(data) >= 4 and all(isinstance(v, str) and v.strip() for v in data.values())
    return data if valid else None


def check_neighborhoods(rows: list[dict], issues: list) -> None:
    keysets = set()
    for n in rows:
        compare = _compare_object(n["compare_json"])
        if compare is None:
            issues.append(("compare_json", n["entry_id"]))
        else:
            keysets.add(tuple(sorted(compare)))
        if not n["location"]:
            issues.append(("location", n["entry_id"]))
    if len(keysets) > 1:
        issues.append(("compare_json_keysets_differ", len(keysets)))


def check_page(ctx: Context, rows: list[dict], slugs: set, issues: list) -> None:
    keys = collections.Counter(_key(r["key"]) for r in rows)
    if rows:
        missing = sorted(PAGE_KEYS - set(keys))
        unknown = sorted(map(str, set(keys) - PAGE_KEYS - RESERVED_PAGE_KEYS))
        repeated = sorted(str(k) for k, n in keys.items() if n > 1)
        if missing or unknown or repeated:
            issues.append(("page_keys", missing, unknown, repeated))
        reserved = sorted(set(keys) & RESERVED_PAGE_KEYS)
        if reserved:
            issues.append(("page_reserved", reserved))
    for r in rows:
        if r["field_id"] != f"{ctx.city}:field:{r['key']}":
            issues.append(("field_id", r["field_id"]))
        if r["value_type"] == "JSON":
            check_page_json(r, slugs, issues)
        if r["key"] == "advice_entry" and _key(r["value"]) not in slugs:
            issues.append(("advice_entry_missing", r["value"]))


def check_page_json(row: dict, slugs: set, issues: list) -> None:
    try:
        value = json.loads(row["value"])
    except (TypeError, ValueError):
        issues.append(("page_json", row["key"]))
        return
    for item in value if isinstance(value, list) else []:
        if isinstance(item, dict) and item.get("entry") and _key(item["entry"]) not in slugs:
            issues.append(("page_entry_missing", row["key"], item["entry"]))


def check_city(ctx: Context, rows: list[dict], issues: list) -> None:
    """Sehir satiri bu sehre ait olmali ve koordinati --bbox icinde olmali (karisik enlem/boylam sirasini yakalar)."""
    for r in rows:
        if r["city_id"] != ctx.city:
            issues.append(("city_id", "Şehir", r["city_id"]))
        if r["latitude"] not in NO_COORD and not ctx.box.contains(r["latitude"], r["longitude"]):
            issues.append(("city_outside_bbox", r["latitude"], r["longitude"]))


def check_actions(actions: list[dict], eid_count: collections.Counter, url_to_src: dict,
                  issues: list) -> tuple[set, set[str]]:
    """(baglantisi olan kayitlar, baglanti adreslerinin kaynaklari)."""
    counts = collections.Counter(_key(x["action_id"]) for x in actions)
    with_action, used = set(), set()
    for x in actions:
        link = _s(x["url"])
        if _key(x["entry_id"]) not in eid_count:
            issues.append(("action_entry", x["_part"], x["action_id"]))
        if counts[_key(x["action_id"])] > 1 or not ID_RE.match(_s(x["action_id"])):
            issues.append(("action_id", x["_part"], x["action_id"]))
        if "wikipedia" in link or not link.startswith("https://"):
            issues.append(("action_url", x["_part"], x["url"]))
        elif link in url_to_src:
            used.add(url_to_src[link])
        else:
            issues.append(("action_url_not_in_sources", x["_part"], x["action_id"], x["url"]))
        with_action.add(_key(x["entry_id"]))
    return with_action, used


def check_steps(rows: list[dict], eid_count: collections.Counter, issues: list) -> None:
    for s in rows:
        if (_key(s["entry_id"]) not in eid_count or len(_s(s["title"])) > 120 or len(_s(s["when"])) > 90
                or len(_s(s["description"])) > 250):
            issues.append(("step", s["step_id"]))


def check_routes(rows: list[dict], place_ids: set, issues: list) -> None:
    for r in rows:
        stops, sids = [x for x in _s(r["stops"]).split("\n") if x.strip()], ids(r["stop_entry_ids"])
        if (not 2 <= len(sids) <= 8 or len(sids) != len(set(sids)) or len(stops) != len(sids)
                or any(s not in place_ids for s in sids) or r["entry_id"] != (sids[0] if sids else None)):
            issues.append(("route", r["route_id"]))


def check_orders(data: dict[str, list[dict]], issues: list) -> None:
    for sheet in ORDERED_SHEETS:
        dup = [o for o, n in collections.Counter(_key(r["order"]) for r in data[sheet]).items() if n > 1]
        if dup:
            issues.append(("order_dup", sheet, dup[:5]))


def check_terms(rows: list[dict], sources: dict, issues: list) -> None:
    for r in rows:
        sids = ids(r["source_ids"])
        if not ID_RE.match(_s(r["term_id"])) or not sids or any(s not in sources for s in sids):
            issues.append(("term", r["term_id"]))


def check_data(ctx: Context, data: dict[str, list[dict]], sources: dict, url_to_src: dict,
               issues: list) -> tuple[set[str], set]:
    """Tum sekme kontrolleri; (kullanilan kaynaklar, iddia sahibi olabilecek kimlikler)."""
    entries = [r for sheet in ENTRY_SHEETS for r in data[sheet]]
    eid_count = collections.Counter(_key(r["entry_id"]) for r in entries)
    title_count = collections.Counter(norm(r["title"]) for r in entries)
    issues += [("dup_entry", e) for e, n in eid_count.items() if n > 1]
    issues += [("dup_title", t) for t, n in title_count.items() if n > 1]
    for sheet in ENTRY_SHEETS:
        check_entries(ctx, sheet, data[sheet], sources, issues)
    for sheet, rows in data.items():
        check_approvals(sheet, rows, issues)
    check_answers(ctx, data["Yanıtlar"], issues)
    check_places(ctx, data["Mekânlar"], issues)
    check_neighborhoods(data["Mahalleler"], issues)
    check_page(ctx, data["SayfaAlanları"], {_key(r["slug"]) for r in entries}, issues)
    check_city(ctx, data["Şehir"], issues)
    used = {s for sheet in SOURCE_SHEETS for r in data[sheet] for s in ids(r.get("source_ids")) if s in sources}
    with_action, action_sources = check_actions(data["Bağlantılar"], eid_count, url_to_src, issues)
    issues += [("no_action", r["entry_id"]) for r in entries if _key(r["entry_id"]) not in with_action]
    check_steps(data["Adımlar"], eid_count, issues)
    check_routes(data["Rotalar"], {_key(p["entry_id"]) for p in data["Mekânlar"]}, issues)
    check_orders(data, issues)
    check_terms(data["Sözlük"], sources, issues)
    known = set(eid_count) | {_key(r[key]) for sheet, key in OWNER_FIELDS for r in data[sheet]} | {ctx.city}
    return used | action_sources, known


def owner_sources(data: dict[str, list[dict]]) -> dict[Any, set[str]]:
    """source_ids sutunu olan iddia sahipleri (giris/rota/terim kimligi) -> kendi kaynaklari. SayfaAlanları ve Şehir'de
    bu sutun yok (metinlerini kaynagina yalniz iddia defteri baglar); onlarin iddialari bu kontrolun disindadir."""
    owners: dict[Any, set[str]] = collections.defaultdict(set)
    for sheet in SOURCE_SHEETS:
        id_key = SHEETS[sheet][0]  # entry_id / route_id / term_id
        for row in data[sheet]:
            owners[_key(row[id_key])].update(ids(row["source_ids"]))
    return dict(owners)


# ---------------------------------------------------------------- iddia alintilari

class SourceTexts:
    """Kaynak metinleri (normalize, onbellekli); dosya okunamazsa None."""

    def __init__(self, sources: dict[str, dict[str, Any]]) -> None:
        self.sources, self.cache = sources, {}

    def get(self, sid: str) -> str | None:
        if sid not in self.cache:
            text_file = self.sources[sid].get("text_file")
            try:
                valid = isinstance(text_file, str) and text_file
                self.cache[sid] = norm(Path(text_file).read_text(encoding="utf-8")) if valid else None
            except (OSError, UnicodeDecodeError):  # okunamayan kopya: alinti 'kaynak_metni_yok' bulgusu olur
                self.cache[sid] = None
        return self.cache[sid]


def claim_owner(claim: dict) -> Any:
    return next((claim[k] for k in CLAIM_OWNER_KEYS if claim.get(k)), None)


def claim_source(claim: dict, sources: dict, url_to_src: dict) -> str | None:
    """Iddianin dayandigi kaynak: dizindeki source_id, yoksa adresi (url/final_url) dizinde olan kaynak."""
    source_id = claim.get("source_id")
    return source_id if isinstance(source_id, str) and source_id in sources else url_to_src.get(_s(claim.get("url")))


def check_claim(claim: dict, owner: Any, sid: str | None, known: set, texts: SourceTexts) -> tuple | None:
    """Alinti eksigi (sebep ile) ya da None."""
    quote = _s(claim.get("quote"))
    if _key(owner) not in known:
        return ("sahip_yok", owner)
    if not sid:
        return ("kaynak_yok",)
    text = texts.get(sid)
    if text is None:
        return ("kaynak_metni_yok", sid)
    if not quote or norm(quote) not in text:
        return ("alinti_metinde_yok",)
    return None


def check_claims(claims_dir: Path, known: set, owners: dict[Any, set[str]], sources: dict, url_to_src: dict,
                 issues: list) -> tuple[int, list[tuple], set[str]]:
    """(iddia sayisi, alinti eksikleri, icerigin iddialarinin dayandigi kaynaklar). Sahibi bilinen iddianin kaynagi
    alintisi tutmasa da kullanilan sayilir (eksik ayri bulgu); sahipsiz iddianinki sayilmaz. Giris/rota/terim iddiasinin
    kaynagi sahibin source_ids'inde degilse 'claim_source_not_in_owner' (kart o kaynagi gostermez)."""
    texts, total, misses, cited = SourceTexts(sources), 0, [], set()
    for path in sorted(claims_dir.glob("*.jsonl"), key=lambda p: p.name) if claims_dir.is_dir() else []:
        for claim in read_jsonl(path):
            if "_bad" in claim:
                issues.append(("json", "claims", claim["_bad"]))
                continue
            total += 1
            owner, sid = claim_owner(claim), claim_source(claim, sources, url_to_src)
            if sid and _key(owner) in known:
                cited.add(sid)
            own = owners.get(_key(owner))
            if sid and own is not None and sid not in own:
                issues.append(("claim_source_not_in_owner", path.name, claim.get("claim_id"), owner, sid))
            miss = check_claim(claim, owner, sid, known, texts)
            if miss:
                misses.append((path.name, claim.get("claim_id"), *miss))
    return total, misses, cited


def check_draft(used: set[str], draft: list[dict], issues: list) -> None:
    """Kaynaklar satiri kaynak_taslak'tan gelir: taslakta satiri olmayan kullanilan kaynak sessizce dusmesin."""
    drafted = {_key(r.get("source_id")) for r in draft}
    issues.extend(("source_not_in_draft", sid) for sid in sorted(used - drafted))


# ---------------------------------------------------------------- cikti

def write_outputs(paths: Paths, data: dict[str, list[dict]], used: set[str], draft: list[dict]) -> None:
    paths.data_out.mkdir(parents=True, exist_ok=True)
    for sheet, rows in data.items():
        if rows:
            write_jsonl(paths.data_out / f"{sheet}.jsonl", [{k: r[k] for k in SHEETS[sheet]} for r in rows])
    write_jsonl(paths.data_out / "Kaynaklar.jsonl",
                [{**r, "verified": "Evet"} for r in draft if _key(r.get("source_id")) in used])


def build_report(data: dict[str, list[dict]], used: set[str], claims_only: set[str], claims: int, misses: list,
                 issues: list) -> dict:
    return {"rows": {s: len(r) for s, r in data.items() if r},
            "per_topic": dict(collections.Counter(a["_part"] for a in data["Yanıtlar"])),
            "places_by_group": dict(collections.Counter(_s(p["group"]) for p in data["Mekânlar"])),
            "sources_used": len(used), "sources_claims_only": len(claims_only), "claims": claims,
            "quote_miss": len(misses), "issue_kinds": dict(collections.Counter(i[0] for i in issues))}


def resolve_paths(args: argparse.Namespace) -> Paths:
    work = Path(os.path.abspath(args.work))
    if not work.is_dir():
        raise UsageError(f"is klasoru yok: {work}")
    parts = work / "data" / "parcalar"
    if not parts.is_dir():
        raise UsageError(f"parca klasoru yok: {parts}")
    return Paths(parts=parts, direct=work / "data", claims=work / "claims", sources=work / "kaynak_dizini.jsonl",
                 draft=work / "kaynak_taslak.jsonl", data_out=Path(os.path.abspath(args.data_out or work / "data")),
                 report=Path(os.path.abspath(args.out or work / REPORT_NAME)))


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Yazar parcalarini birlestirir + kapi oncesi kontrol (merge_package)")
    p.add_argument("work", help="is klasoru (_is): data/parcalar, claims, kaynak_dizini.jsonl, kaynak_taslak.jsonl")
    p.add_argument("--city-id", required=True, type=_city_arg)
    p.add_argument("--bbox", required=True, type=_bbox_arg,
                   help="LAT_MIN,LAT_MAX,LON_MIN,LON_MAX (or. 51.3,51.55,5.3,5.6)")
    p.add_argument("--data-out", type=Path, help="birlesik sekmelerin klasoru (varsayilan <is>/data)")
    p.add_argument("--out", type=Path, help=f"ayrintili rapor (varsayilan <is>/{REPORT_NAME})")
    return p


def run(args: argparse.Namespace) -> int:
    paths = resolve_paths(args)
    sources, url_to_src = load_sources(paths.sources)
    draft = load_jsonl(paths.draft)
    ctx, issues = Context(args.city_id, args.bbox), []
    data = {sheet: merge(paths.parts, sheet, issues) for sheet in SHEETS}
    for sheet in DIRECT_SHEETS:
        check_approvals(sheet, read_direct(paths.direct / f"{sheet}.jsonl", sheet, issues), issues)
    by_rows, known = check_data(ctx, data, sources, url_to_src, issues)
    claims, misses, cited = check_claims(paths.claims, known, owner_sources(data), sources, url_to_src, issues)
    used, claims_only = by_rows | cited, cited - by_rows
    check_draft(used, draft, issues)
    write_outputs(paths, data, used, draft)
    report = build_report(data, used, claims_only, claims, misses, issues)
    write_json(paths.report, {**report, "issues": issues, "quote_miss_list": misses,
                              "claims_only_sources": sorted(claims_only)})
    findings = bool(issues or misses)
    emit({"status": "findings" if findings else "ok", "city_id": ctx.city, **report, "out": str(paths.report)})
    return EXIT_FINDINGS if findings else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        return run(args)
    except (UsageError, OSError, ValueError) as error:  # yakalanmazsa cikis 1 olur ve 'bulgu' ile karisir
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
