"""snapcmp.py: K76 (kismi) paketteki kaynak kopyasi <-> ayni adresin taze kopyasi (baslik + metin ortusmesi).

Kullanim: python -I -X utf8 snapcmp.py <OUT> <PKG> <TK>
PKG yalniz okunur. Iki taraf da toolkit fetch_snapshot.extract_page ile ayni bicimde metne cevrilir.
Cikti: OUT/_analiz/snapshot-karsilastirma.json
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True
OUT, PKG, TK = (Path(a) for a in sys.argv[1:4])
sys.path.insert(0, str(TK))
from fetch_snapshot import decode_body, extract_page, normalize_for_match  # noqa: E402


def words(text: str) -> set[str]:
    return set(re.findall(r"\w{4,}", (text or "").lower()))


def norm_title(text: str | None) -> str:
    return normalize_for_match(text or "").strip()


def page(path: Path) -> tuple[str, str]:
    title, text = extract_page(decode_body(path.read_bytes(), "text/html"))
    return title or "", text or ""


sources = [json.loads(l) for l in (OUT / "_dump" / "Kaynaklar.jsonl").open(encoding="utf-8") if l.strip()]
index = {}
for line in (OUT / "kanitlar" / "snap" / "index.jsonl").open(encoding="utf-8"):
    if line.strip():
        row = json.loads(line)
        index[row["url"]] = row

rows = []
for _i, s in enumerate(sources):
    print('ILERLEME', _i, s['source_id'], s['snapshot_file'], flush=True)
    pkg_title, pkg_text = page(PKG / s["snapshot_file"])
    print('  pkg ok', flush=True)
    fresh = index.get(s["url"], {})
    item = {"source_id": s["source_id"], "row": s["_row"], "url": s["url"], "pkg_title": pkg_title[:160],
            "fresh_status": fresh.get("status"), "fresh_title": (fresh.get("title") or "")[:160],
            "title_match": None, "overlap_fresh": None, "jaccard": None, "pkg_chars": len(pkg_text)}
    if fresh.get("html_file"):
        print('  fresh', fresh['html_file'], flush=True)
        f_title, f_text = page(OUT / "kanitlar" / "snap" / fresh["html_file"])
        a, b = words(f_text), words(pkg_text)
        item["overlap_fresh"] = round(len(a & b) / len(a), 3) if a else None
        item["jaccard"] = round(len(a & b) / len(a | b), 3) if (a | b) else None
        nt, nf = norm_title(pkg_title), norm_title(f_title or fresh.get("title"))
        item["title_match"] = bool(nt and nf and (nt == nf or nt in nf or nf in nt))
    rows.append(item)

checked = [r for r in rows if r["title_match"] is not None]
suspect = [r for r in checked if not r["title_match"] and (r["overlap_fresh"] or 0) < 0.5]
low_overlap = [r for r in checked if (r["overlap_fresh"] or 0) < 0.5]
vals = sorted(r["overlap_fresh"] for r in checked if r["overlap_fresh"] is not None)
summary = {"sources": len(rows), "compared": len(checked), "not_compared": [r["source_id"] for r in rows
                                                                            if r["title_match"] is None],
           "title_match": sum(1 for r in checked if r["title_match"]),
           "title_differ": sum(1 for r in checked if not r["title_match"]),
           "overlap_median": vals[len(vals) // 2] if vals else None,
           "overlap_lt_0_5": len(low_overlap), "suspect_title_differ_and_low_overlap": len(suspect),
           "pkg_thin_text_lt_500": [r["source_id"] for r in rows if r["pkg_chars"] < 500]}
result = {"summary": summary, "suspect": suspect, "title_differ": [r for r in checked if not r["title_match"]],
          "low_overlap": low_overlap, "rows": rows}
(OUT / "_analiz" / "snapshot-karsilastirma.json").write_text(json.dumps(result, ensure_ascii=False, indent=1),
                                                            encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False))
for r in result["title_differ"]:
    print("TITLE_DIFF", json.dumps({k: r[k] for k in ("source_id", "row", "url", "pkg_title", "fresh_title",
                                                      "overlap_fresh", "jaccard")}, ensure_ascii=False))
for r in low_overlap:
    if r["title_match"]:
        print("LOW_OVERLAP", json.dumps({k: r[k] for k in ("source_id", "row", "url", "overlap_fresh", "jaccard",
                                                           "pkg_chars")}, ensure_ascii=False))

