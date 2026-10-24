"""Ulke paketinin sehir-notr kartlarini sehrin is klasorune uygular (SKILL 'country' fazi).

Kullanim:
  country_apply.py apply <is_klasoru> --pack <ROOT>\\ulke\\ES --city-id sevilla --city-name Sevilla --order-start 7000
                   [--today YYYY-AA-GG] [--out ozet.json]
  country_apply.py audit-scope <is_klasoru> --pack <ROOT>\\ulke\\ES [--today YYYY-AA-GG] [--out rapor.json]

Paket duzeni (ulke\\<ISO>\\): pack.json {country, version, built, cards: {slug: {sha256, valid_until}}},
Yanitlar.ulusal.jsonl, Baglantilar.ulusal.jsonl (Bağlantılar.ulusal.jsonl), claims\\ulusal.jsonl, kaynak_dizini.jsonl ve
text_file/html_file'in gosterdigi kopyalar. Kartlarda sehir adi yerine {sehir} yer tutucusu bulunur.

apply
- Her kart: sha256'si pack.json'dakiyle ayni mi (degilse cikis 2), valid_until gecmis mi (gecmisse 'stale': kopyalanmaz,
  ozette listelenir; yazar yeniden dogrular). Kalan kartlar topic_id'ye gore <is>\\data\\parcalar\\Yanıtlar.<konu>.jsonl,
  Bağlantılar.<konu>.jsonl ve <is>\\claims\\<konu>.jsonl dosyalarina yazilir; entry_id/slug/topic_id/action_id sehre gore
  yeniden kurulur, order --order-start'tan arka arkaya verilir, {sehir} doldurulur.
- Kaynaklar AGSIZ alinir: pakettaki kopya <is>\\snap_ulke_<iso>'ya kopyalanir, kaynak_dizini.jsonl ve kaynak_taslak.jsonl'a
  add_sources'in kilidi ve kimlik mantigiyla eklenir (sehirde zaten kayitli adres mevcut kimligini alir).
- <is>\\ulke_kart_kaydi.jsonl: entry_id -> pakete koken, pakettaki ve sehirdeki hash. Excel'e sutun eklenmez.
- Hedef dosyalardan biri zaten varsa cikis 2 (uzerine yazilmaz).

audit-scope
- Pakette denetlenmis kart sehirde degismediyse ve valid_until gecmediyse claim denetimini atlar ('skip'); degisen,
  paketi sonradan duzeltilen, paketten kalkan ya da suresi dolan kart 'audit' (neden ile).
stdout tek satir JSON. Cikis: 0 tamam / 2 kullanim (bozuk paket, okunamayan girdi, var olan hedef dosya).
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toolkit" / "scripts"))  # ortak araclar (deneme: toolkit'e dosya eklenmez)

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

import add_sources
from common import EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json

PACK_FILE = "pack.json"
CARDS_FILE = "Yanıtlar.ulusal.jsonl"
ACTIONS_FILE = "Bağlantılar.ulusal.jsonl"
CLAIMS_FILE = Path("claims") / "ulusal.jsonl"
REGISTER_NAME = "ulke_kart_kaydi.jsonl"
PLACEHOLDER = "{sehir}"
CARD_IDENTITY = frozenset({"entry_id", "city_id", "slug", "order", "source_ids", "topic_id"})
CLAIM_IDENTITY = frozenset({"claim_id", "entry_id", "source_id"})
PARCALAR = Path("data") / "parcalar"


class UsageError(Exception):
    """Bozuk paket, okunamayan girdi ya da var olan hedef dosya (cikis 2)."""


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def card_hash(card: dict[str, Any], claims: list[dict[str, Any]]) -> str:
    """Kimlik alanlari haric kart + kartin claim'leri; sehir/paket arasinda ayni icerik ayni hash."""
    body = {k: v for k, v in card.items() if k not in CARD_IDENTITY}
    rest = sorted(canonical({k: v for k, v in c.items() if k not in CLAIM_IDENTITY}) for c in claims)
    return hashlib.sha256(canonical([body, rest]).encode("utf-8")).hexdigest()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        return add_sources.read_jsonl(path)
    except add_sources.UsageError as error:
        raise UsageError(str(error)) from error
    except FileNotFoundError as error:
        raise UsageError(f"dosya yok: {path}") from error


def read_optional(path: Path) -> list[dict[str, Any]]:
    return read_jsonl(path) if path.exists() else []


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes("".join(canonical_line(r) for r in rows).encode("utf-8"))


def canonical_line(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False) + "\n"


def fill(value: Any, city_name: str) -> Any:
    """Metinlerdeki {sehir} yer tutucusunu doldurur (kopya doner; girdi degismez)."""
    if isinstance(value, str):
        return value.replace(PLACEHOLDER, city_name)
    if isinstance(value, list):
        return [fill(v, city_name) for v in value]
    if isinstance(value, dict):
        return {k: fill(v, city_name) for k, v in value.items()}
    return value


def load_pack_meta(pack: Path) -> dict[str, Any]:
    path = pack / PACK_FILE
    try:
        meta = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as error:
        raise UsageError(f"{PACK_FILE} yok: {pack}") from error
    except (OSError, json.JSONDecodeError) as error:
        raise UsageError(f"{path} okunamadi ({error})") from error
    if not isinstance(meta, dict) or not isinstance(meta.get("cards"), dict) or not meta.get("country"):
        raise UsageError(f"{path}: country ve cards alanlari gerekli")
    return meta


def topic_slug(topic_id: str) -> str:
    return topic_id.split(":", 1)[-1]


def rebuilt_action_id(action_id: Any, iso: str, city_id: str) -> str:
    prefix = f"{iso.lower()}:action:"
    text = str(action_id)
    return f"{city_id}:action:{text[len(prefix):]}" if text.startswith(prefix) else text


def is_stale(valid_until: Any, today: str) -> bool:
    return isinstance(valid_until, str) and valid_until < today  # YYYY-AA-GG metin karsilastirmasi


def group_by_entry(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(str(row.get("entry_id")), []).append(row)
    return grouped


def check_pack_cards(pack: Path, meta: dict[str, Any], cards: list[dict[str, Any]],
                     claims: dict[str, list[dict[str, Any]]]) -> None:
    for card in cards:
        slug = card.get("slug")
        expected = (meta["cards"].get(slug) or {}).get("sha256")
        if not expected:
            raise UsageError(f"{PACK_FILE}'da kart yok: {slug}")
        if card_hash(card, claims.get(card["entry_id"], [])) != expected:
            raise UsageError(f"paket karti pack.json'daki hash ile uyusmuyor: {slug} (paket elle degismis olabilir)")


def plan_sources(pack: Path, cards: list[dict[str, Any]],
                 actions: list[dict[str, Any]] = ()) -> tuple[list[str], dict[str, dict[str, Any]]]:
    """Kopyalanacak kaynak kimlikleri (ilk gorulme sirasiyla) ve paket dizin satirlari. Kartlarin source_ids'ine ek
    olarak baglanti adresi paket dizininde olan kaynak da kopyalanir (merge_package baglantiyi kaynakta arar)."""
    index = {str(r.get("source_id")): r for r in read_jsonl(pack / "kaynak_dizini.jsonl")}
    wanted: list[str] = []
    for card in cards:
        for sid in str(card.get("source_ids") or "").split(";"):
            sid = sid.strip()
            if not sid:
                continue
            if sid not in index:
                raise UsageError(f"kaynak paketin dizininde yok: {sid} (kart {card.get('slug')})")
            if sid not in wanted:
                wanted.append(sid)
    by_url = {r.get("url"): sid for sid, r in index.items()}
    for action in actions:
        sid = by_url.get(action.get("url"))
        if sid and sid not in wanted:
            wanted.append(sid)
    return wanted, index


def register_sources(work: Path, pack: Path, city: str, wanted: list[str],
                     index: dict[str, dict[str, Any]], iso: str) -> tuple[dict[str, str], int, int]:
    """Paket kaynaklarini sehre kaydeder; doner: (paket kimligi -> sehir kimligi, eklenen, yeniden kullanilan)."""
    out_dir = work / f"snap_ulke_{iso.lower()}"
    mapping: dict[str, str] = {}
    with add_sources.index_lock(work, lambda seconds: None):
        city_index = add_sources.read_jsonl(work / add_sources.INDEX_NAME)
        draft = add_sources.read_jsonl(work / add_sources.DRAFT_NAME)
        by_url = {r.get("url"): r for r in city_index}
        number = add_sources.next_number(city_index, city)
        index_rows, draft_rows, reused = [], [], 0
        for sid in wanted:
            row = index[sid]
            known = by_url.get(row.get("url"))
            if known and known.get("source_id"):
                mapping[sid] = str(known["source_id"])
                reused += 1
                continue
            number += 1
            new_id = f"{city}:kaynak:{number:03d}"
            mapping[sid] = new_id
            index_rows.append(copy_source(pack, out_dir, work, new_id, row))
            snap = {"title": row.get("title"), "fetched_on": row.get("checked_on")}
            draft_rows.append(add_sources.draft_row(city, str(row.get("topic") or "ulusal"), new_id, row, snap))
        result = add_sources.Registration({r["url"]: r["source_id"] for r in index_rows}, {}, {}, [],
                                          index_rows, draft_rows)
        add_sources.save(work, result)
    return mapping, len(index_rows), reused


def copy_source(pack: Path, out_dir: Path, work: Path, new_id: str, row: dict[str, Any]) -> dict[str, Any]:
    """Paketteki kopyayi sehrin snap klasorune alir; kaynak_dizini satiri add_sources.index_row ile ayni bicimde."""
    out_dir.mkdir(parents=True, exist_ok=True)
    copied = {}
    for key in ("text_file", "html_file"):
        source = pack / str(row[key])
        if not source.is_file():
            raise UsageError(f"kopya pakette yok: {source}")
        target = out_dir / f"{new_id.replace(':', '_')}_{source.name}"
        shutil.copyfile(source, target)
        copied[key] = target
    return {**{k: row.get(k) for k in ("topic", "url", "final_url", "title", "publisher", "lang", "text_chars",
                                       "html_sha256", "why")},
            "source_id": new_id, "text_file": os.path.join(out_dir, copied["text_file"].name),
            "html_file": os.path.join(out_dir.name, copied["html_file"].name)}


def target_files(work: Path, topics: list[str]) -> list[Path]:
    paths = [work / REGISTER_NAME]
    for topic in topics:
        paths += [work / PARCALAR / f"Yanıtlar.{topic}.jsonl", work / PARCALAR / f"Bağlantılar.{topic}.jsonl",
                  work / "claims" / f"{topic}.jsonl"]
    return paths


def apply_pack(*, work: Path, pack: Path, city_id: str, city_name: str, order_start: int, today: str) -> dict[str, Any]:
    work, pack = Path(work), Path(pack)
    if not work.is_dir():
        raise UsageError(f"is klasoru yok: {work}")
    meta = load_pack_meta(pack)
    cards = read_jsonl(pack / CARDS_FILE)
    claims = group_by_entry(read_optional(pack / CLAIMS_FILE))
    actions = group_by_entry(read_optional(pack / ACTIONS_FILE))
    check_pack_cards(pack, meta, cards, claims)
    stale = [c["slug"] for c in cards if is_stale(meta["cards"][c["slug"]].get("valid_until"), today)]
    live = [c for c in cards if c["slug"] not in stale]
    topics = sorted({topic_slug(c["topic_id"]) for c in live})
    existing = [p for p in target_files(work, topics) if p.exists()]
    if existing:
        raise UsageError(f"hedef dosya zaten var, uzerine yazilmaz: {', '.join(p.name for p in existing)}")
    live_ids = {c["entry_id"] for c in live}
    wanted, index = plan_sources(pack, live, [a for e in live_ids for a in actions.get(e, [])])
    iso = str(meta["country"])
    mapping, added, reused = register_sources(work, pack, city_id, wanted, index, iso)
    by_topic: dict[str, dict[str, list[dict[str, Any]]]] = {t: {"cards": [], "actions": [], "claims": []} for t in topics}
    register = []
    for position, card in enumerate(live):
        entry_id = f"{city_id}:{card['slug']}"
        topic = topic_slug(card["topic_id"])
        source_ids = ";".join(mapping[s.strip()] for s in str(card.get("source_ids") or "").split(";") if s.strip())
        new_claims = [{**fill(c, city_name), "entry_id": entry_id, "source_id": mapping[c["source_id"]]}
                      for c in claims.get(card["entry_id"], []) if c.get("source_id") in mapping]
        new_card = {**fill(card, city_name), "entry_id": entry_id, "city_id": city_id,
                    "topic_id": f"{city_id}:{topic}", "source_ids": source_ids, "order": order_start + position}
        new_actions = [{**fill(a, city_name), "action_id": rebuilt_action_id(a["action_id"], iso, city_id),
                        "entry_id": entry_id, "city_id": city_id} for a in actions.get(card["entry_id"], [])]
        by_topic[topic]["cards"].append(new_card)
        by_topic[topic]["actions"] += new_actions
        by_topic[topic]["claims"] += new_claims
        register.append({"entry_id": entry_id, "pack_slug": card["slug"], "country": iso,
                         "pack_version": meta.get("version"), "pack_sha256": meta["cards"][card["slug"]]["sha256"],
                         "city_sha256": card_hash(new_card, new_claims),
                         "valid_until": meta["cards"][card["slug"]].get("valid_until")})
    for topic, parts in by_topic.items():
        write_rows(work / PARCALAR / f"Yanıtlar.{topic}.jsonl", parts["cards"])
        if parts["actions"]:
            write_rows(work / PARCALAR / f"Bağlantılar.{topic}.jsonl", parts["actions"])
        write_rows(work / "claims" / f"{topic}.jsonl", parts["claims"])
    write_rows(work / REGISTER_NAME, register)
    return {"copied": len(live), "stale": stale, "topics": topics, "sources_added": added, "sources_reused": reused,
            "pack_version": meta.get("version"), "order_range": [order_start, order_start + max(len(live) - 1, 0)]}


def city_cards(work: Path) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    cards: dict[str, dict[str, Any]] = {}
    for path in sorted((work / PARCALAR).glob("Yanıtlar.*.jsonl")):
        cards.update({str(r.get("entry_id")): r for r in read_jsonl(path)})
    claims: dict[str, list[dict[str, Any]]] = {}
    for path in sorted((work / "claims").glob("*.jsonl")):
        for entry_id, rows in group_by_entry(read_jsonl(path)).items():
            claims.setdefault(entry_id, []).extend(rows)
    return cards, claims


def audit_scope(work: Path, pack: Path, *, today: str) -> dict[str, Any]:
    """Claim denetimini atlayabilecek ('skip') ve denetlenecek ('audit': entry_id -> neden) paket kartlari."""
    work, pack = Path(work), Path(pack)
    meta = load_pack_meta(pack)
    cards, claims = city_cards(work)
    skip: list[str] = []
    audit: dict[str, str] = {}
    for record in read_jsonl(work / REGISTER_NAME):
        entry_id, slug = record["entry_id"], record["pack_slug"]
        current = meta["cards"].get(slug)
        card = cards.get(entry_id)
        if card is None:
            audit[entry_id] = "kart şehirde yok"
        elif card_hash(card, claims.get(entry_id, [])) != record["city_sha256"]:
            audit[entry_id] = "şehirde değişti"
        elif current is None:
            audit[entry_id] = "paketten kalktı"
        elif current.get("sha256") != record["pack_sha256"]:
            audit[entry_id] = "paket kartı sonradan değişti"
        elif is_stale(current.get("valid_until"), today):
            audit[entry_id] = f"valid_until geçti ({current['valid_until']})"
        else:
            skip.append(entry_id)
    return {"skip": skip, "audit": audit, "pack_version": meta.get("version")}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ülke paketinin kartlarını şehre uygular ya da denetim kapsamını çıkarır")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("apply", "audit-scope"):
        p = sub.add_parser(name)
        p.add_argument("work", type=Path, help="is klasoru (_is)")
        p.add_argument("--pack", required=True, type=Path, help="ROOT\\ulke\\<ISO>")
        p.add_argument("--today", help="YYYY-AA-GG (varsayilan: bugun)")
        p.add_argument("--out", type=Path, help="tam sonuc JSON")
        if name == "apply":
            p.add_argument("--city-id", required=True)
            p.add_argument("--city-name", required=True)
            p.add_argument("--order-start", required=True, type=int)
    return parser


def run(args: argparse.Namespace) -> int:
    import datetime as dt
    today = args.today or dt.date.today().isoformat()
    try:
        dt.date.fromisoformat(today)
    except ValueError as error:
        raise UsageError(f"--today YYYY-AA-GG olmali: {today}") from error
    if args.command == "apply":
        if not add_sources.CITY_RE.match(args.city_id):
            raise UsageError("--city-id kucuk harf ASCII/rakam/tire olmali (or. sevilla)")
        result = apply_pack(work=args.work, pack=args.pack, city_id=args.city_id, city_name=args.city_name,
                            order_start=args.order_start, today=today)
    else:
        result = audit_scope(args.work, args.pack, today=today)
    if args.out:
        write_json(args.out, result)
    emit({"tool": "country_apply", "command": args.command, **summarize(result)})
    return EXIT_OK


def summarize(result: dict[str, Any]) -> dict[str, Any]:
    if "skip" in result:
        return {"skip": len(result["skip"]), "audit": len(result["audit"]), "audit_reasons": result["audit"]}
    return result


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        return run(args)
    except (UsageError, add_sources.UsageError, OSError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
