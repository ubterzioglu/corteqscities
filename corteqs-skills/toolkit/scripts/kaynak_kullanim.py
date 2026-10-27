"""Kaynak kimlikleri nerede kullaniliyor: kayitlarin source_ids'i, iddia defteri, buton adresleri.

Kapasite (Kaynaklar 500/500) dolu iken editorun yeni kaynagi ancak bir kaynagi tamamen bosaltarak eklemesi gerekir
(net 0). 'serbest: true' = hicbir kayitta, iddiada ve butonda yok -> merge_package onu Kaynaklar'a koymaz.
Sevilla 3. tur: 8 kaynak yalniz buton adresi olarak kaldigi icin Kaynaklar 504'e cikti, kurulum 4 kaynagi reddetti.
Kullanim: kaynak_kullanim.py <is> <kaynak_id> [<kaynak_id> ...]   (JSON satiri / kaynak)
Cikis: 0 hepsi kullanimda; 1 serbest kaynak var; 2 kullanim hatasi.
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

RX = re.compile(r"\b[a-z0-9-]+:kaynak:\d+\b")
OWNER_KEYS = ("entry_id", "route_id", "term_id", "field_id", "step_id")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def usage(work: Path, wanted: list[str]) -> dict[str, list[str]]:
    urls: dict[str, set[str]] = defaultdict(set)
    for row in read_jsonl(work / "kaynak_dizini.jsonl"):
        if row.get("source_id") in wanted:
            urls[row["source_id"]] |= {u for u in (row.get("url"), row.get("final_url")) if u}
    uses: dict[str, list[str]] = {sid: [] for sid in wanted}
    for f in sorted((work / "data" / "parcalar").glob("*.jsonl")):
        for row in read_jsonl(f):
            rid = next((row[k] for k in OWNER_KEYS if row.get(k)), "")
            if f.name.startswith("Bağlantılar"):
                for sid in wanted:
                    if row.get("url") in urls[sid]:
                        uses[sid].append(f"buton {row.get('action_id')}")
                continue
            ids = set(RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False)))
            for sid in wanted:
                if sid in ids:
                    uses[sid].append(f"kayıt {f.name} {rid}")
    for f in sorted((work / "claims").glob("*.jsonl")):
        for row in read_jsonl(f):
            if row.get("source_id") in uses:
                owner = next((row[k] for k in OWNER_KEYS if row.get(k)), "")
                uses[row["source_id"]].append(f"iddia {f.name} {owner} {row.get('claim_id')}")
    return uses


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    p = argparse.ArgumentParser(description="Kaynak kimliklerinin kayit, iddia ve buton kullanimi (kapasite net 0 icin)")
    p.add_argument("work", type=Path, help="is klasoru (_is)")
    p.add_argument("source_ids", nargs="+")
    args = p.parse_args(argv)
    if not (args.work / "data" / "parcalar").is_dir():
        common.emit({"tool": "kaynak_kullanim", "error": f"parca klasoru yok: {args.work}"})
        return common.EXIT_USAGE
    uses = usage(args.work, args.source_ids)
    for sid in args.source_ids:
        print(json.dumps({"source_id": sid, "serbest": not uses[sid], "kullanim_sayisi": len(uses[sid]),
                          "kullanim": uses[sid][:40]}, ensure_ascii=False))
    return common.EXIT_FINDINGS if any(not v for v in uses.values()) else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
