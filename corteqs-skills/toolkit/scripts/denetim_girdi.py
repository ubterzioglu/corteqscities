"""Son tam denetim girdisi: parca basina <is>/denetim/<parca>-<tur>_kartlar.jsonl.

Satir = kaydin parca dosyasindaki hali + 'kaynaklar' (source_id, url, publisher, text_file; kaydin source_ids'i ve
iddialarinin kaynaklari) + 'iddialar' (yazar defteri) + Yanitlarda 'adimlar' ve 'butonlar', mekan/mahallede 'butonlar',
rotalarda 'plan' ve 'bacaklar' (rota_plan.jsonl, rota_mesafe.jsonl) ile duraklarin konum/not alanlari.
Sevilla son denetimi (26.10.2026): 448 kayit, 5.855 defter satiri; denetci internete cikmadan yalniz bu dosyayi ve
kaynak metinlerini okudu. Yeniden denetimde --kayit yalniz duzelt kararli/degisen kayitlari yazar.
Cikis: 0 yazildi (ya da --dry-run ozet); 1 metin kopyasi olmayan kaynak var; 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import common

SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler", "Sözlük", "Rotalar")
OWNER = {"Yanıtlar": "entry_id", "Mekânlar": "entry_id", "Mahalleler": "entry_id", "Sözlük": "term_id", "Rotalar": "route_id"}
CLAIM_OWNER_KEYS = ("entry_id", "term_id", "field_id", "route_id")
CLAIM_FIELDS = ("claim_id", "field", "claim", "value", "unit", "period", "source_id", "quote")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def _ids(value: Any) -> list[str]:
    return [p.strip() for p in re.split(r"[\n,;]+", str(value or "")) if p.strip()]


def build(work: Path, city: str, tur: str, part: str | None, only: set[str] | None) -> tuple[dict[str, list[dict]], list[dict]]:
    rx = re.compile(rf"\b(?:{re.escape(city)}|[a-z]{{2}}):kaynak:\d+\b")
    parts_dir = work / "data" / "parcalar"
    index = {r["source_id"]: r for r in read_jsonl(work / "kaynak_dizini.jsonl") if r.get("source_id")}
    claims: dict[str, list[dict]] = defaultdict(list)
    for f in sorted((work / "claims").glob("*.jsonl")):
        for c in read_jsonl(f):
            owner = next((c[k] for k in CLAIM_OWNER_KEYS if c.get(k)), None)
            claims[owner].append({k: c.get(k) for k in CLAIM_FIELDS})
    steps, buttons = defaultdict(list), defaultdict(list)
    for f in parts_dir.glob("Adımlar.*.jsonl"):
        for s in read_jsonl(f):
            steps[s.get("entry_id")].append({k: s.get(k) for k in ("step_id", "title", "when", "description")})
    for f in parts_dir.glob("Bağlantılar.*.jsonl"):
        for b in read_jsonl(f):
            buttons[b.get("entry_id")].append({k: b.get(k) for k in ("action_id", "label", "url")})
    places = {r["entry_id"]: r for f in parts_dir.glob("Mekânlar.*.jsonl") for r in read_jsonl(f) if r.get("entry_id")}
    plan, legs = defaultdict(list), defaultdict(list)
    for r in read_jsonl(work / "rota_plan.jsonl"):
        plan[r.get("route_id")].append(r)
    for r in read_jsonl(work / "rota_mesafe.jsonl"):
        legs[r.get("route_id")].append(r)

    def sources(row: dict, owner: str) -> list[dict]:
        found = rx.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False))
        ids = list(dict.fromkeys(found + [c["source_id"] for c in claims[owner] if c.get("source_id")]))
        return [{"source_id": s, **{k: index.get(s, {}).get(k) for k in ("url", "publisher", "text_file")}} for s in ids]

    out: dict[str, list[dict]] = {}
    summary = []
    for sheet in SHEETS:
        for f in sorted(parts_dir.glob(f"{sheet}.*.jsonl")):
            name = f.name.split(".")[1]
            if part and name != part:
                continue
            rows = []
            for row in read_jsonl(f):
                owner = row.get(OWNER[sheet])
                if not owner or (only is not None and owner not in only):
                    continue
                item = {**row, "_sekme": sheet, "kaynaklar": sources(row, owner), "iddialar": claims[owner]}
                if sheet == "Yanıtlar":
                    item |= {"adimlar": steps[owner], "butonlar": buttons[owner]}
                elif sheet in ("Mekânlar", "Mahalleler"):
                    item["butonlar"] = buttons[owner]
                elif sheet == "Rotalar":
                    item |= {"plan": plan[owner], "bacaklar": legs[owner],
                             "duraklar": [{k: places.get(s, {}).get(k) for k in ("entry_id", "title", "location", "note", "latitude", "longitude")}
                                          for s in _ids(row.get("stop_entry_ids"))]}
                rows.append(item)
            if not rows:
                continue
            out[name] = rows
            summary.append({"parca": name, "sekme": sheet, "kayit": len(rows), "iddia": sum(len(i["iddialar"]) for i in rows),
                            "metinsiz_kaynak": sorted({s["source_id"] for i in rows for s in i["kaynaklar"] if not s.get("text_file")})})
    return out, summary


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    p = argparse.ArgumentParser(description="Son tam denetim girdisi (parca basina <parca>-<tur>_kartlar.jsonl)")
    p.add_argument("work", type=Path, help="is klasoru (_is)")
    p.add_argument("--city-id", required=True)
    p.add_argument("--tur", default="d5", help="tur adi (d5, d6, ...); dosya adinin parcasi")
    p.add_argument("--parca", help="yalniz bu parca")
    p.add_argument("--kayit", help="yalniz bu kayitlar (virgulle; yeniden denetim)")
    p.add_argument("--dry-run", action="store_true", help="yazmadan ozet")
    args = p.parse_args(argv)
    if not (args.work / "data" / "parcalar").is_dir():
        common.emit({"tool": "denetim_girdi", "error": f"parca klasoru yok: {args.work / 'data' / 'parcalar'}"})
        return common.EXIT_USAGE
    if not re.fullmatch(r"d\d+|ek\d*", args.tur):
        common.emit({"tool": "denetim_girdi", "error": f"gecersiz tur: {args.tur} (d5, d6, ek ...)"})
        return common.EXIT_USAGE
    only = {i.strip() for i in args.kayit.split(",") if i.strip()} if args.kayit else None
    out, summary = build(args.work, args.city_id, args.tur, args.parca, only)
    if not args.dry_run:
        (args.work / "denetim").mkdir(exist_ok=True)
        for name, rows in out.items():
            target = args.work / "denetim" / f"{name}-{args.tur}_kartlar.jsonl"
            target.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    missing = sorted({s for x in summary for s in x["metinsiz_kaynak"]})
    common.emit({"tool": "denetim_girdi", "tur": args.tur, "parca": len(summary), "kayit": sum(x["kayit"] for x in summary),
                 "iddia": sum(x["iddia"] for x in summary), "metinsiz_kaynak": missing[:20], "yazildi": not args.dry_run})
    return common.EXIT_FINDINGS if missing else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
