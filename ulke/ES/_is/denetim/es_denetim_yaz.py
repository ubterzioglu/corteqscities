"""İspanya ülke paketi 7 oturum/resmî kartının bağımsız denetim sonuçlarını (26.10.2026, workflow günlükleri)
iddia_defteri'nin okuduğu biçimde yazar: <slug>-dN_iddia.jsonl ve <slug>-dN_karar.jsonl.

Turlar: 'denetim:' -> d2, 'yeniden:' -> d3, 'denetim3:' -> d4 (editör değişiklik kayıtları oturum-d2/d3/d4 ile aynı sıra).
Kullanım: python -I es_denetim_yaz.py ornek | yaz
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

BASE = Path(r"C:\Users\baris-terzioglu\.claude\projects\c--temp-private-corteqs-0000-newera"
            r"\e1640e62-11af-476a-83cc-e29539d8a592\subagents\workflows")
JOURNALS = (BASE / "wf_e3d4cc33-aa0" / "journal.jsonl", BASE / "wf_4d01fe4e-117" / "journal.jsonl")
OUT = Path(__file__).resolve().parent
ROUNDS = {"denetim": "d2", "yeniden": "d3", "denetim3": "d4"}
KONTROL_TARIHI = "2026-10-26"


def journal_results() -> list[tuple[str, str, dict]]:
    """(tur, slug, sonuç) - label 'started' satırından, sonuç aynı key'in 'result' satırından."""
    out = []
    for path in JOURNALS:
        labels, results = {}, {}
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row.get("type") == "started":
                labels[row["key"]] = row.get("label", "")
            elif row.get("type") == "result":
                results[row["key"]] = row.get("result")
        for key, label in labels.items():
            prefix, _, slug = label.partition(":")
            if prefix in ROUNDS and isinstance(results.get(key), dict):
                out.append((ROUNDS[prefix], slug.split(":", 1)[-1], results[key]))
    return out


def claim_rows(slug: str, tur: str, result: dict) -> list[dict]:
    """'bulgular' (d4) yalnız bulguları taşır ve claim_id'siz gelir: kimlik tur adıyla üretilir (d2 kimlikleriyle çakışmasın)."""
    items = result.get("iddialar") or result.get("bulgular") or []
    rows = []
    for n, item in enumerate(items, 1):
        if not isinstance(item, dict):
            raise SystemExit(f"{slug}: iddia satırı nesne değil: {str(item)[:120]}")
        rows.append({"claim_id": item.get("claim_id") or f"C-{slug}-{tur}-{n}", "entry_id": f"es:{slug}",
                     "iddia": item.get("iddia", ""), "sonuç": item.get("sonuc", item.get("sonuç", "")),
                     "ağırlık": item.get("agirlik", item.get("ağırlık", "")),
                     "resmî_URL": item.get("resmi_url", item.get("resmî_URL", "")), "kontrol_tarihi": KONTROL_TARIHI,
                     "alıntı": item.get("alinti", item.get("alıntı", "")),
                     "doğrusu": item.get("dogrusu", item.get("doğrusu", "")),
                     "belirsizlik": item.get("belirsizlik", "")})
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def main(mode: str) -> int:
    results = journal_results()
    print(json.dumps({"sonuc": len(results), "tur_kart": sorted(f"{t}:{s}" for t, s, _ in results)}, ensure_ascii=False))
    if mode == "ornek":
        for tur, slug, res in results:
            if tur == "d4":
                print(json.dumps((res.get("bulgular") or res.get("iddialar") or [None])[0], ensure_ascii=False)[:700])
                break
        return 0
    written = []
    for tur, slug, res in results:
        stem = f"{slug}-{tur}"
        for suffix in ("_iddia.jsonl", "_karar.jsonl"):
            if (OUT / f"{stem}{suffix}").exists():
                raise SystemExit(f"zaten var, ezilmez: {stem}{suffix}")
        claims = claim_rows(slug, tur, res)
        write_jsonl(OUT / f"{stem}_iddia.jsonl", claims)
        write_jsonl(OUT / f"{stem}_karar.jsonl", [{"entry_id": f"es:{slug}", "karar": res.get("karar", ""),
                                                    "en_agir": res.get("en_agir", ""), "ozet": res.get("ozet", "")}])
        written.append((stem, len(claims), res.get("karar")))
    print(json.dumps({"yazilan": written}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
