"""photo_prefilter.py --candidates C.jsonl --plan venues.jsonl [--out decisions.json] [--shortlist 3] [--config rules.json]

Adaylari photo_rules ile eler/isaretler; mekan basina en fazla N adaylik kisa liste verir (keep once, sonra flag).
Ag yok, ML yok. Cikis: 0 hepsi keep, 1 reject/flag var, 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import common
import photo_rules


class InputError(Exception):
    pass


def read_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise InputError(f"{label} okunamadi: {path}") from exc
    rows = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise InputError(f"{label} satir {number}: gecersiz JSON") from exc
        if not isinstance(row, dict):
            raise InputError(f"{label} satir {number}: nesne bekleniyor")
        rows.append(row)
    return rows


def load_rules(path: Path | None) -> dict[str, Any]:
    if path is None:
        return photo_rules.DEFAULT_RULES
    try:
        override = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"kural dosyasi okunamadi: {path}") from exc
    if not isinstance(override, dict):
        raise InputError("kural dosyasi bir JSON nesnesi olmali")
    return photo_rules.merge_rules(photo_rules.DEFAULT_RULES, override)


def build_shortlists(decisions: list[dict[str, Any]], size: int) -> dict[str, list[str]]:
    """Mekan basina: keep (puan azalan), sonra flag; reject asla. Esitlikte candidate_id ile deterministik."""
    by_entry: dict[str, list[dict[str, Any]]] = {}
    for d in decisions:
        if d["decision"] != "reject":
            by_entry.setdefault(d["entry_id"], []).append(d)
    order = {"keep": 0, "flag": 1}
    return {entry: [d["candidate_id"] for d in sorted(rows, key=lambda d: (order[d["decision"]], -d["score"], str(d["candidate_id"])))][:size]
            for entry, rows in by_entry.items()}


def run(candidates: list[dict[str, Any]], plan: list[dict[str, Any]], rules: dict[str, Any], size: int) -> dict[str, Any]:
    entries = {row.get("entry_id"): row for row in plan}
    decisions = [photo_rules.evaluate(c, entries.get(c.get("entry_id")), rules) for c in candidates]
    counts = {k: sum(1 for d in decisions if d["decision"] == k) for k in ("keep", "flag", "reject")}
    reasons: dict[str, int] = {}
    for d in decisions:
        for code in d["reasons"]:
            reasons[code] = reasons.get(code, 0) + 1
    shortlists = build_shortlists(decisions, size)
    return {"decisions": decisions, "shortlists": shortlists,
            "summary": {"candidates": len(decisions), **counts, "entries": len(entries),
                        "entries_without_shortlist": sorted(e for e in entries if e not in shortlists),
                        "reasons": dict(sorted(reasons.items(), key=lambda kv: -kv[1]))}}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Deterministik foto on-filtresi.")
    p.add_argument("--candidates", type=Path, required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--out", type=Path)
    p.add_argument("--shortlist", type=int, default=3)
    p.add_argument("--config", type=Path)
    return p


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    try:
        if args.shortlist < 1:
            raise InputError("--shortlist en az 1 olmali")
        rules = load_rules(args.config)
        result = run(read_jsonl(args.candidates, "adaylar"), read_jsonl(args.plan, "plan"), rules, args.shortlist)
    except InputError as exc:
        common.emit({"error": str(exc)})
        return common.EXIT_USAGE
    if args.out:
        common.write_json(args.out, result)
    s = result["summary"]
    common.emit({k: s[k] for k in ("candidates", "keep", "flag", "reject", "entries")}
                | {"entries_without_shortlist": len(s["entries_without_shortlist"]), "top_reasons": dict(list(s["reasons"].items())[:6])})
    return common.EXIT_OK if s["flag"] + s["reject"] == 0 else common.EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
