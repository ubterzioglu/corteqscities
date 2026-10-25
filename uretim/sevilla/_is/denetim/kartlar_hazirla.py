"""kartlar_hazirla.py: bagimsiz denetci icin <parca>_kartlar.jsonl kurar (ana dongu betigi, dosya yalniz _is\\denetim altina).

Kullanim: python -I -X utf8 kartlar_hazirla.py <WORK> <Sekme> <parca> [--ids id1,id2,...] [--out-name <ad>]
  <Sekme>: Yanıtlar | Mekânlar | Mahalleler
  <parca>: data\\parcalar\\<Sekme>.<parca>.jsonl dosyasinin parca adi
  --ids: yalniz bu entry_id'ler (virgulle); verilmezse parcanin tum satirlari
  --out-name: cikti adi (varsayilan <parca>); dosya: _is\\denetim\\<ad>_kartlar.jsonl
Kaynak metinleri kaynak_dizini.jsonl'den (source_ids -> text_file); claim_check_kalan _is\\claim_check.json'dan (unit modu, supported disi).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
FIELDS = {
    "Yanıtlar": ["entry_id", "topic_id", "title", "subtitle", "summary", "steps", "documents", "timing", "cost", "note", "source_ids"],
    "Mekânlar": ["entry_id", "title", "subtitle", "summary", "group", "district", "setting", "location", "latitude", "longitude", "visit_status", "note", "collection", "source_ids"],
    "Mahalleler": ["entry_id", "title", "subtitle", "summary", "location", "tags", "compare_json", "note", "source_ids"],
}


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("work")
    ap.add_argument("sheet", choices=list(FIELDS))
    ap.add_argument("part")
    ap.add_argument("--ids", default="")
    ap.add_argument("--out-name", default="")
    a = ap.parse_args()
    work = Path(a.work)
    is_ = work / "_is"
    rows = jl(is_ / "data" / "parcalar" / f"{a.sheet}.{a.part}.jsonl")
    ids = {s.strip() for s in a.ids.split(",") if s.strip()}
    if ids:
        rows = [r for r in rows if r.get("entry_id") in ids]
    kaynak = {k["source_id"]: k for k in jl(is_ / "kaynak_dizini.jsonl")}
    kalan: dict[str, list] = {}
    cc = is_ / "claim_check.json"
    if cc.exists():
        for r in json.loads(cc.read_text(encoding="utf-8")).get("results", []):
            if r.get("result") != "supported":
                kalan.setdefault(r.get("entry_id"), []).append({"sentence": r.get("sentence"), "values": r.get("values"), "result": r.get("result")})
    out = []
    missing = []
    for r in rows:
        card = {f: r.get(f, "") for f in FIELDS[a.sheet]}
        srcs = []
        for sid in str(r.get("source_ids") or "").split(";"):
            sid = sid.strip()
            if not sid:
                continue
            k = kaynak.get(sid)
            if not k:
                missing.append((r.get("entry_id"), sid))
                continue
            srcs.append({"source_id": sid, "url": k.get("url"), "text_file": k.get("text_file")})
        card["sources"] = srcs
        card["claim_check_kalan"] = kalan.get(r.get("entry_id"), [])
        out.append(card)
    name = a.out_name or a.part
    dst = is_ / "denetim" / f"{name}_kartlar.jsonl"
    with dst.open("w", encoding="utf-8", newline="\n") as f:
        for c in out:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(json.dumps({"out": str(dst), "cards": len(out), "sources_missing": missing, "kalan_total": sum(len(c["claim_check_kalan"]) for c in out)}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
