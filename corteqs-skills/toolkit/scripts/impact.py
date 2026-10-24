"""impact.py <xlsx> [--ids id1,id2] [--diff old.xlsx] [--depth 1|2] [--no-text] [--out impact.json] [--checks checks.yaml]

K99/K118: duzeltmeden sonra yalniz bagimli kayitlari yeniden denetlemek icin etki analizi (token tasarrufu). --ids: entry_id/
source_id/photo_id/evidence_id/route_id/action_id/topic_id..., slug veya sehir onekisiz kimlik (kaynak:kvk); --diff: eski Excel'e
gore degisen/eklenen/silinen kayitlar (sayfa+kimlik+alan). Yonler: self; backward (tohuma bakan, <= 2 seviye: kaynak -> yanit ->
facts); forward (tohumun baktigi; --diff'te eski hedef previous=true); text (Mekan/Mahalle basligi anmasi, sezgisel; --no-text
kapatir, ozet text_only sayar). Sahipsiz hedefe bakan kayit dangling=true (K12). stdout: tek satir JSON ozet; --out (hicbir
girdinin ustune yazmaz): kimlik -> [{sheet,_row,id,field,relation,level,direction}] + K onerisi. Cikis: 0 denetlenecek kayit
yok / 1 kayit, degisiklik veya bilinmeyen kimlik var / 2 kullanim-yapi hatasi."""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, NamedTuple, Sequence

import openpyxl
import yaml
from openpyxl.utils.exceptions import InvalidFileException

import common

Record = Mapping[str, Any]
Sheets = Mapping[str, Sequence[Record]]
RecKey = tuple[str, int]  # (sayfa, sayfa icindeki sira)

DEFAULT_CATALOG = Path(__file__).resolve().parent.parent / "checks.yaml"
OWNER_KEYS = {
    "Teslimat": "delivery_id", "Şehir": "city_id", "Konular": "topic_id", "Yanıtlar": "entry_id", "Mekânlar": "entry_id",
    "Mahalleler": "entry_id", "Bağlantılar": "action_id", "Rotalar": "route_id", "Sözlük": "term_id", "Adımlar": "step_id",
    "Kaynaklar": "source_id", "Fotoğraflar": "photo_id", "Kanıtlar": "evidence_id", "SayfaAlanları": "field_id", "EkDetaylar": "detail_id"}
DIFF_KEYS = {**OWNER_KEYS, "FotoğrafKaynakları": "photo_id"}  # FK satiri fotografin sahibi degil, ona baglidir
SOURCE_REF = ("source_ids", "cites_source")
REF_FIELDS: dict[str, tuple[tuple[str, str], ...]] = {
    "Şehir": (("hero_photo_id", "hero_photo"),), "Yanıtlar": (SOURCE_REF, ("topic_id", "answer_topic")),
    "Mekânlar": (SOURCE_REF,), "Mahalleler": (SOURCE_REF,), "Sözlük": (SOURCE_REF,),
    "Rotalar": (("entry_id", "route_start"), ("stop_entry_ids", "route_stop"), SOURCE_REF),
    "Bağlantılar": (("entry_id", "action_of_entry"),), "Adımlar": (("entry_id", "step_of_entry"),),
    "EkDetaylar": (("entry_id", "detail_of_entry"),), "Kanıtlar": (("photo_id", "evidence_of_photo"),),
    "Fotoğraflar": (("entry_id", "photo_of_entry"), ("evidence_id", "photo_evidence")),
    "FotoğrafKaynakları": (("photo_id", "photo_source_chain"),)}
ID_FIELDS = frozenset(f for refs in REF_FIELDS.values() for f, _ in refs) | frozenset(DIFF_KEYS.values())
SLUG_SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler", "Konular")
TITLED_SHEETS = ("Mekânlar", "Mahalleler")
MENTION_SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük", "Adımlar", "SayfaAlanları", "EkDetaylar")
SKIP_TEXT_KEYS = frozenset({"slug", "url", "media_key", "city_id", "key", "value_type"})
MIN_TITLE_MENTION, MIN_SLUG_MENTION, TRUNC = 5, 6, 160

# Yeniden denetim onerisi (checks.yaml kodlari): sayfa bazli; iliski ozelse onu kullan; alan degisikligi ek kod getirir
SHEET_CHECKS: dict[str, tuple[str, ...]] = {
    "Şehir": ("K62", "K91"), "Konular": ("K19",), "Yanıtlar": ("K25", "K26", "K29"), "Mekânlar": ("K42", "K43", "K55"),
    "Mahalleler": ("K44", "K45"), "Bağlantılar": ("K49", "K50", "K51", "K53"), "Rotalar": ("K46", "K47"),
    "Sözlük": ("K48",), "Adımlar": ("K87",), "Kaynaklar": ("K29", "K35", "K50", "K51"),
    "Fotoğraflar": ("K22", "K23", "K57", "K58", "K59", "K60", "K61", "K62", "K80"),
    "Kanıtlar": ("K61", "K67", "K69", "K76"), "SayfaAlanları": ("K86", "K87"), "EkDetaylar": ("K16",),
    "FotoğrafKaynakları": ("K58", "K77", "K80")}
RELATION_CHECKS: dict[str, tuple[str, ...]] = {"hero_photo": ("K62",), "mentions_title": ("K29", "K32")}
FIELD_CHECKS: dict[str, tuple[str, ...]] = {
    "location": ("K42", "K55"), "latitude": ("K43",), "longitude": ("K43",), "url": ("K49", "K50", "K51"),
    "source_ids": ("K29", "K30"), "stop_entry_ids": ("K46",), "slug": ("K11",), "license": ("K67", "K69"),
    "license_url": ("K69",), "author": ("K70",), "sha256": ("K58",), "file": ("K57", "K80"), "web_file": ("K57", "K80"),
    "original_file": ("K80", "K114"), "hero_photo_id": ("K62",), "visit_status": ("K39",)}
FK_CHECK = "K12"
EMPTY_SEED: Mapping[str, list] = {"changes": [], "previous": [], "deleted": [], "old": []}  # yalniz okunur; birlestirme yeni liste uretir
DIRECTION_ORDER = {"self": 0, "backward": 1, "forward": 2, "text": 3}
SHEET_ORDER = {name: i for i, name in enumerate(common.DATA_SHEETS)}
_sheet_rank = lambda name: (SHEET_ORDER.get(name, 99), name)  # noqa: E731  sayfa sirasi; bilinmeyen sayfa sona, ada gore

class ImpactError(Exception):
    """Kullanim veya yapi hatasi (cikis kodu 2)."""

Ref = NamedTuple("Ref", [("field", str), ("relation", str), ("target", str)])

@dataclass(frozen=True)
class Graph:
    sheets: Mapping[str, tuple[Record, ...]]
    city: str
    owners: Mapping[str, tuple[RecKey, ...]]
    reverse: Mapping[str, tuple[tuple[RecKey, Ref], ...]]
    slugs: Mapping[str, tuple[str, ...]]

    def record(self, key: RecKey) -> Record:
        return self.sheets[key[0]][key[1]]

# --- okuma, ayrisma, graf ------------------------------------------------------------------------
def load_sheets(path: Path) -> dict[str, tuple[dict[str, Any], ...]]:
    """Excel'i salt okur (satir 7 anahtarlari, formul hucreleri haric)."""
    try:
        wb = openpyxl.load_workbook(path, data_only=False)
    except (OSError, zipfile.BadZipFile, InvalidFileException, KeyError, ValueError) as exc:
        raise ImpactError(f"xlsx okunamadi: {path} ({type(exc).__name__}: {exc})") from exc
    try:
        return {name: tuple(common.iter_records(wb[name])) for name in common.DATA_SHEETS if name in wb.sheetnames}
    except ValueError as exc:
        raise ImpactError(str(exc)) from exc
    finally:
        wb.close()

def split_ids(value: Any) -> list[str]:
    return [] if value is None else [part.strip() for part in re.split(r"[;\n]", str(value)) if part.strip()]

def _walk_entries(node: Any) -> Iterator[str]:
    if isinstance(node, dict) and isinstance(node.get("entry"), str) and node["entry"].strip():
        yield node["entry"].strip()
    for child in node.values() if isinstance(node, dict) else node if isinstance(node, list) else ():
        yield from _walk_entries(child)

def json_entry_slugs(value: Any) -> list[str]:
    """SayfaAlanlari JSON degerindeki tum 'entry' slug'lari (facts, quick_links, timeline); bozuk JSON -> []."""
    try:
        data = json.loads(value) if isinstance(value, str) else value
    except ValueError:
        return []
    return list(_walk_entries(data))

def city_of(sheets: Sheets) -> str:
    found = (str(r["city_id"]) for name in ("Şehir", "Teslimat") for r in sheets.get(name, ()) if r.get("city_id"))
    return next(found, "")

def record_refs(sheet: str, rec: Record, city: str) -> tuple[Ref, ...]:
    """Kaydin baska kimliklere verdigi baglar; SayfaAlanlari 'entry' slug'lari city_id:slug'a cevrilir."""
    if sheet != "SayfaAlanları":
        refs = [Ref(field, rel, target) for field, rel in REF_FIELDS.get(sheet, ()) for target in split_ids(rec.get(field))]
        return tuple(dict.fromkeys(refs))
    key, rec_city = str(rec.get("key", "")), str(rec.get("city_id") or city)
    to_id = lambda slug: slug if ":" in slug else f"{rec_city}:{slug}"  # noqa: E731
    if key == "advice_entry":
        refs = [Ref("advice_entry", "advice_entry", to_id(s)) for s in split_ids(rec.get("value"))]
    else:
        refs = [Ref(f"{key}.entry", "page_field_entry", to_id(s)) for s in json_entry_slugs(rec.get("value"))]
    return tuple(dict.fromkeys(refs))

def build_graph(sheets: Sheets) -> Graph:
    frozen = {name: tuple(recs) for name, recs in sheets.items()}
    city = city_of(frozen)
    owners: dict[str, list[RecKey]] = {}
    reverse: dict[str, list[tuple[RecKey, Ref]]] = {}
    slugs: dict[str, list[str]] = {}
    for name, recs in frozen.items():
        owner_key = OWNER_KEYS.get(name)
        for idx, rec in enumerate(recs):
            ident = rec.get(owner_key) if owner_key else None
            if ident not in (None, ""):
                owners.setdefault(str(ident), []).append((name, idx))
                if name in SLUG_SHEETS and rec.get("slug"):
                    slugs.setdefault(str(rec["slug"]), []).append(str(ident))
            for ref in record_refs(name, rec, city):
                reverse.setdefault(ref.target, []).append(((name, idx), ref))
    freeze = lambda d: {k: tuple(v) for k, v in d.items()}  # noqa: E731
    return Graph(frozen, city, freeze(owners), freeze(reverse), freeze(slugs))

def resolve(graph: Graph, token: str) -> list[str]:
    """Belirteci kimlik(ler)e cozer: slug -> city_id:slug; tam kimlik; onekisiz kimlik (kaynak:kvk); bilinmiyorsa []."""
    token = token.strip()
    if token in graph.slugs:
        return sorted(set(graph.slugs[token]))
    prefixed = token if token.startswith(f"{graph.city}:") else f"{graph.city}:{token}"
    return [c for c in dict.fromkeys((token, prefixed)) if c in graph.owners or c in graph.reverse][:1]

# --- etki ----------------------------------------------------------------------------------------
def _item(graph: Graph, key: RecKey, field: str, relation: str, level: int, direction: str, **extra: Any) -> dict[str, Any]:
    rec = graph.record(key)
    return {"sheet": key[0], "_row": rec.get("_row"), "id": rec.get(DIFF_KEYS.get(key[0], "")), "field": field,
            "relation": relation, "level": level, "direction": direction, **extra}

def _sort_key(item: Mapping[str, Any]) -> tuple:
    return (item["level"], DIRECTION_ORDER[item["direction"]], SHEET_ORDER.get(item["sheet"], 99), item["_row"] or 0,
            item["field"], item["relation"])

def _unique(items: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[tuple, dict[str, Any]] = {}
    for item in items:
        seen.setdefault((item["sheet"], item["_row"], item["field"], item["relation"]), item)
    return list(seen.values())

def _covered(items: Iterable[Mapping[str, Any]]) -> frozenset[tuple[str, Any]]:
    return frozenset((i["sheet"], i["_row"]) for i in items)

def _backward(graph: Graph, target: str, level: int, covered: frozenset, dangling: bool, via: str | None = None) -> list[dict]:
    extra = {**({"via": via} if via else {}), **({"dangling": True} if dangling else {})}
    items = [_item(graph, key, ref.field, ref.relation, level, "backward", **extra) for key, ref in graph.reverse.get(target, ())]
    return _unique(i for i in items if (i["sheet"], i["_row"]) not in covered)

def _forward(graph: Graph, owner_keys: Sequence[RecKey], previous: Iterable[Ref], covered: frozenset) -> list[dict]:
    current = tuple(ref for key in owner_keys for ref in record_refs(key[0], graph.record(key), graph.city))
    old = tuple(ref for ref in dict.fromkeys(previous) if ref not in current)
    flagged = [(ref, False) for ref in current] + [(ref, True) for ref in old]
    items = [_item(graph, key, ref.field, ref.relation, 1, "forward", **({"previous": True} if prev else {}))
             for ref, prev in flagged for key in graph.owners.get(ref.target, ())]
    return _unique(i for i in items if (i["sheet"], i["_row"]) not in covered)

def mention_patterns(rec: Record) -> list[re.Pattern[str]]:
    """Baslik, parantezsiz baslik ve slug sozcukleri; buyuk/kucuk harf duyarsiz, sozcuk sinirli."""
    title = str(rec.get("title") or "").strip()
    variants = {title, re.sub(r"\s*\([^)]*\)", "", title).strip()}
    parts = [r"\s+".join(map(re.escape, v.split())) for v in variants if len(v) >= MIN_TITLE_MENTION]
    slug = str(rec.get("slug") or "")
    if len(slug) >= MIN_SLUG_MENTION:
        parts.append(r"[\s-]+".join(re.escape(w) for w in slug.split("-") if w))
    return [re.compile(rf"(?<!\w){p}(?!\w)", re.IGNORECASE) for p in sorted(set(parts))]

def _mentioning_fields(rec: Record, patterns: Sequence[re.Pattern[str]]) -> list[str]:
    text = lambda f: not f.startswith("_") and not f.endswith(("_id", "_ids")) and f not in SKIP_TEXT_KEYS  # noqa: E731
    return [f for f, v in rec.items() if text(f) and isinstance(v, str) and any(p.search(v) for p in patterns)]

def _mentions(graph: Graph, owner_keys: Sequence[RecKey], covered: frozenset, old: Sequence[tuple[str, Record]]) -> list[dict]:
    """Guncel ve (--diff'te) eski basliklarin metin anmalari: yeniden adlandirmada bayat anmalar da bulunur (K118)."""
    recs = [(key[0], graph.record(key)) for key in owner_keys] + list(old)
    patterns = [p for sheet, rec in recs if sheet in TITLED_SHEETS for p in mention_patterns(rec)]
    if not patterns:
        return []
    return [_item(graph, (sheet, idx), field, "mentions_title", 1, "text")
            for sheet in MENTION_SHEETS for idx, rec in enumerate(graph.sheets.get(sheet, ()))
            if (sheet, rec.get("_row")) not in covered for field in _mentioning_fields(rec, patterns)]

def _second_level(graph: Graph, level1: Sequence[Mapping[str, Any]], covered: frozenset) -> list[dict]:
    via_ids = dict.fromkeys(str(i["id"]) for i in level1 if i["sheet"] in OWNER_KEYS and i["id"] not in (None, ""))
    return _unique(item for ident in via_ids for item in _backward(graph, ident, 2, covered, False, via=ident))

def impact(graph: Graph, seed: str, depth: int = 2, previous: Iterable[Ref] = (),
           old: Sequence[tuple[str, Record]] = (), text: bool = True) -> list[dict[str, Any]]:
    """Tohumun etkiledigi kayitlar (geri bag <= depth, dongu korumali); previous/old: --diff'te eski bag/kayit; text: anma."""
    owner_keys = graph.owners.get(seed, ())
    items = [_item(graph, key, OWNER_KEYS[key[0]], "self", 0, "self") for key in owner_keys]
    level1 = _backward(graph, seed, 1, _covered(items), dangling=not owner_keys)
    items = items + level1
    items = items + _forward(graph, owner_keys, previous, _covered(items))
    items = items + (_mentions(graph, owner_keys, _covered(items), old) if text else [])
    if depth >= 2:
        items = items + _second_level(graph, level1, _covered(items))
    return sorted(items, key=_sort_key)

# --- diff ----------------------------------------------------------------------------------------
def _keyed(sheet: str, records: Sequence[Record]) -> dict[tuple[str, str, int], Record]:
    """Kimlige gore (yinelenen kimlikte gorulme sirasi ile) anahtarlar; kimliksiz kayit satir no ile."""
    key_field, seen, out = DIFF_KEYS.get(sheet), Counter(), {}
    for rec in records:
        ident = rec.get(key_field) if key_field else None
        base = ("id", str(ident)) if ident not in (None, "") else ("row", str(rec.get("_row")))
        out[(*base, seen[base])] = rec
        seen[base] += 1
    return out

def _short(value: Any) -> Any:
    value = value if isinstance(value, (str, int, float, bool, type(None))) else str(value)
    return value[:TRUNC] + "…" if isinstance(value, str) and len(value) > TRUNC else value

def _compare(sheet: str, key: tuple[str, str, int], old: Record | None, new: Record | None) -> dict[str, Any] | None:
    base = {"sheet": sheet, "id": key[1] if key[0] == "id" else None}
    if old is None:
        return {**base, "_row": new["_row"], "old_row": None, "change": "added", "fields": [], "values": {}}
    if new is None:
        return {**base, "_row": old["_row"], "old_row": old["_row"], "change": "deleted", "fields": [], "values": {}}
    fields = sorted(f for f in old.keys() | new.keys() if f != "_row" and old.get(f) != new.get(f))
    if not fields:
        return None
    values = {f: {"old": _short(old.get(f)), "new": _short(new.get(f))} for f in fields}
    return {**base, "_row": new["_row"], "old_row": old["_row"], "change": "changed", "fields": fields, "values": values}

def diff_sheets(old: Sheets, new: Sheets) -> list[dict[str, Any]]:
    """Iki Excel'in kayit farki (sayfa+kimlik+alan); satir kaymasi tek basina degisiklik sayilmaz."""
    keyed = [(s, _keyed(s, old.get(s, ())), _keyed(s, new.get(s, ()))) for s in sorted(set(old) | set(new), key=_sheet_rank)]
    return [c for s, before, after in keyed for k in sorted(before.keys() | after.keys())
            if (c := _compare(s, k, before.get(k), after.get(k)))]

# --- kontrol onerisi -----------------------------------------------------------------------------
def load_catalog(path: Path) -> dict[str, dict[str, Any]]:
    """checks.yaml -> {K kodu: {title, exec}}; okunamazsa {} (kodlar basliksiz verilir)."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return {}
    checks = data.get("checks", []) if isinstance(data, dict) else []
    return {str(c["id"]): {"title": c.get("title"), "exec": c.get("exec")} for c in checks if isinstance(c, dict) and c.get("id")}

def _item_codes(item: Mapping[str, Any]) -> tuple[str, ...]:
    codes = RELATION_CHECKS.get(item.get("relation", "")) or SHEET_CHECKS.get(item["sheet"], ())
    return codes + ((FK_CHECK,) if item.get("dangling") else ())

def _change_codes(change: Mapping[str, Any]) -> tuple[str, ...]:
    fk = change["change"] != "changed" or any(f in ID_FIELDS for f in change["fields"])
    by_field = tuple(code for f in change["fields"] for code in FIELD_CHECKS.get(f, ()))
    return SHEET_CHECKS.get(change["sheet"], ()) + by_field + ((FK_CHECK,) if fk else ())

def recommend_checks(items: Iterable[Mapping[str, Any]], changes: Iterable[Mapping[str, Any]],
                     catalog: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    pairs = [(code, i["sheet"]) for i in items for code in _item_codes(i)]
    pairs += [(code, c["sheet"]) for c in changes for code in _change_codes(c)]
    codes = sorted({code for code, _ in pairs if not catalog or code in catalog}, key=lambda c: int(c[1:]))
    return [{"id": code, "title": catalog.get(code, {}).get("title"), "exec": catalog.get(code, {}).get("exec"),
             "sheets": sorted({s for c, s in pairs if c == code}, key=_sheet_rank)} for code in codes]

# --- analiz ve CLI -------------------------------------------------------------------------------
def _token_seeds(graph: Graph, tokens: Sequence[str]) -> tuple[dict[str, list[str]], list[str]]:
    resolved = [(token, resolve(graph, token)) for token in tokens]
    seeds = {ident: [t for t, ids in resolved if ident in ids] for _, ids in resolved for ident in ids}
    return seeds, [t for t, ids in resolved if not ids]

def _change_seeds(changes: Sequence[Mapping[str, Any]], old: Sheets) -> dict[str, dict[str, list]]:
    """Degisiklik kimligi -> {changes, previous (eski baglar), deleted (silinen self ogesi), old (eski kayitlar)}."""
    old_rows = {(name, rec.get("_row")): rec for name, recs in old.items() for rec in recs}
    city, seeds = city_of(old), {}
    for ch in (c for c in changes if c["id"] is not None):
        prev = old_rows.get((ch["sheet"], ch["old_row"]))
        refs = list(record_refs(ch["sheet"], prev, city)) if prev is not None else []
        gone = [{"sheet": ch["sheet"], "_row": ch["_row"], "id": ch["id"], "field": DIFF_KEYS.get(ch["sheet"]),
                 "relation": "self", "level": 0, "direction": "self", "status": "deleted"}] if ch["change"] == "deleted" else []
        entry = seeds.get(ch["id"], EMPTY_SEED)
        seeds = {**seeds, ch["id"]: {"changes": entry["changes"] + [ch], "previous": entry["previous"] + refs,
                                     "deleted": entry["deleted"] + gone,
                                     "old": entry["old"] + ([(ch["sheet"], prev)] if prev is not None else [])}}
    return seeds

def _seed_report(graph: Graph, seed: str, depth: int, tokens: list[str], info: Mapping[str, list] | None,
                 catalog: Mapping[str, Any], text: bool = True) -> dict[str, Any]:
    info = info or EMPTY_SEED
    items = sorted(info["deleted"] + impact(graph, seed, depth, info["previous"], info["old"], text), key=_sort_key)
    changes = [{"sheet": c["sheet"], "change": c["change"], "fields": c["fields"]} for c in info["changes"]]
    return {"tokens": tokens, "changes": changes, "items": items,
            "checks": [c["id"] for c in recommend_checks(items, info["changes"], catalog)]}

def _counts(items: Sequence[Mapping[str, Any]], changes: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    live = {(i["sheet"], i["_row"]) for i in items if i.get("status") != "deleted"}
    structural = {(i["sheet"], i["_row"]) for i in items if i.get("status") != "deleted" and i["direction"] != "text"}
    sheets = sorted({s for s, _ in live}, key=_sheet_rank)
    kinds = {k: sum(1 for c in changes if c["change"] == k) for k in ("changed", "added", "deleted")}
    return {"changes": kinds, "impacted": len(live), "text_only": len(live - structural),
            "by_sheet": {s: sum(1 for x, _ in live if x == s) for s in sheets}}

def analyze(xlsx: Path, tokens: Sequence[str], diff_path: Path | None, depth: int,
            catalog: Mapping[str, Any], text: bool = True) -> dict[str, Any]:
    graph = build_graph(load_sheets(xlsx))
    by_token, unknown = _token_seeds(graph, tokens)
    if tokens and not by_token:
        raise ImpactError("hicbir kimlik cozulemedi: " + ", ".join(unknown))
    old = load_sheets(diff_path) if diff_path else {}
    changes = diff_sheets(old, graph.sheets) if diff_path else []
    by_change = _change_seeds(changes, old)
    impacts = {seed: _seed_report(graph, seed, depth, by_token.get(seed, []), by_change.get(seed), catalog, text)
               for seed in sorted(by_token.keys() | by_change.keys())}
    items = [i for rep in impacts.values() for i in rep["items"]]
    mode = "+".join(m for m, on in (("ids", bool(tokens)), ("diff", diff_path is not None)) if on)
    return {"xlsx": Path(xlsx).name, "diff": Path(diff_path).name if diff_path else None, "mode": mode, "depth": depth,
            "text": text, "catalog_loaded": bool(catalog), "unknown_ids": unknown, "counts": _counts(items, changes),
            "checks": recommend_checks(items, changes, catalog), "changes": changes, "impacts": impacts}

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Duzeltme etki analizi: bagimli kayitlar ve yeniden denetim onerisi (K99/K118).")
    parser.add_argument("xlsx", type=Path, help="guncel (duzeltilmis) Excel")
    parser.add_argument("--ids", default=None, help="virgulle ayrilmis kimlik veya slug listesi")
    parser.add_argument("--diff", type=Path, default=None, help="karsilastirilacak eski Excel")
    parser.add_argument("--depth", type=int, choices=(1, 2), default=2, help="geri bag seviyesi (en fazla 2)")
    parser.add_argument("--no-text", action="store_true", help="metin anmalarini (sezgisel, genis yayilir) atla")
    parser.add_argument("--out", type=Path, default=None, help="ayrintili JSON raporu (girdilerden farkli olmali)")
    parser.add_argument("--checks", type=Path, default=DEFAULT_CATALOG, help="checks.yaml (K kodu basliklari)")
    return parser

def same_file(a: Path, b: Path) -> bool:
    """Ayni dosya mi: '..'/goreli yazim, harf farki ve sabit bag dahil (build_xlsx.py ile ayni koruma)."""
    try:
        return a.resolve() == b.resolve() or (a.exists() and b.exists() and a.samefile(b))
    except OSError:
        return False

def check_usage(args: argparse.Namespace, tokens: Sequence[str]) -> None:
    """Tohum yoksa ya da --out bir girdinin (xlsx, --diff, --checks) ustune yazacaksa ImpactError; gercek veri salt okunur."""
    if not tokens and args.diff is None:
        raise ImpactError("--ids (bos olmayan) veya --diff gerekli")
    inputs = (args.xlsx, args.diff, args.checks) if args.out is not None else ()
    clash = next((p for p in inputs if p is not None and same_file(args.out, p)), None)
    if clash is not None:
        raise ImpactError(f"--out bir girdinin ustune yazamaz: {clash}")

def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    tokens = list(dict.fromkeys(t.strip() for t in (args.ids or "").split(",") if t.strip()))
    try:
        check_usage(args, tokens)
        report = analyze(args.xlsx, tokens, args.diff, args.depth, load_catalog(args.checks), text=not args.no_text)
    except ImpactError as exc:
        common.emit({"error": str(exc)})
        return common.EXIT_USAGE
    if args.out is not None:
        common.write_json(args.out, report)
    counts = report["counts"]
    common.emit({**{k: report[k] for k in ("mode", "xlsx", "diff", "depth", "text")}, "seeds": len(report["impacts"]),
                 "unknown_ids": report["unknown_ids"], **{k: counts[k] for k in ("changes", "impacted", "text_only", "by_sheet")},
                 "checks": [c["id"] for c in report["checks"]], "out": str(args.out) if args.out else None})
    busy = counts["impacted"] or report["unknown_ids"] or any(counts["changes"].values())
    return common.EXIT_FINDINGS if busy else common.EXIT_OK

if __name__ == "__main__":
    sys.exit(main())
