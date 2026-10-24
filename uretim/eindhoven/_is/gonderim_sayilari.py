"""Teslimden sonra gonderim notu icin sayilari tek yerde toplar (pilot is script'i; salt okur).

Kullanim: python gonderim_sayilari.py <_is klasoru>
Okur: build_final.json, validation.json, url_check_final.json, dosya-envanteri.json, claims/*.jsonl
stdout: okunabilir ozet (GONDERIM_NOTU.md tablosu ve "Bizim olctugumuz" bolumu icin).
"""
from __future__ import annotations

import glob
import json
import os
import sys


def load(path: str) -> dict:
    return json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {}


def main() -> int:
    w = sys.argv[1]
    build = load(os.path.join(w, "build_final.json"))
    val = load(os.path.join(w, "validation.json"))
    url = load(os.path.join(w, "url_check_final.json"))
    inv = load(os.path.join(w, "dosya-envanteri.json"))
    rows = build.get("summary", {}).get("rows_written") or build.get("rows_planned") or {}
    print("== Excel satirlari (build_final):", "red", build.get("summary", {}).get("rejected"))
    for sheet, n in sorted(rows.items()):
        print(f"  {sheet}: {n}")
    st, md, sm = val.get("structure", {}), val.get("media", {}), val.get("summary", {})
    print("== Resmi dogrulayici (validation.json, mode", sm.get("mode"), "new_content", sm.get("new_content"), ")")
    print("  yapi hatasi:", len(st.get("errors", [])), "| medya hatasi:", len(md.get("errors", [])),
          "| asgari eksik:", sm.get("minimum_gaps"), "| technically_complete:", sm.get("technically_complete"))
    for k in sorted(st.get("counts", {})):
        print(f"  {k}: {st['counts'][k]}  (asgari {st.get('minimum', {}).get(k)}, hedef {st.get('target', {}).get(k)})")
    print("  foto:", md.get("photos"), "| farkli dosya:", md.get("different_files"), "| uyari:", len(st.get("warnings", [])))
    for wc in val.get("warning_classes", []):
        print("   uyari sinifi:", json.dumps(wc, ensure_ascii=False)[:160])
    us = url.get("summary", {})
    print("== URL:", us.get("coverage"), "| karar:", json.dumps(us.get("verdicts"), ensure_ascii=False),
          "| bulgu:", us.get("findings"))
    isum = inv.get("summary", {})
    print("== Envanter:", isum.get("files"), "dosya,", isum.get("total_mb"), "MB | eksik", isum.get("missing"),
          "| sha", isum.get("sha_mismatch"), "| uzanti", isum.get("ext_mismatch"), "| dup_sha", isum.get("dup_sha"),
          "| artik", isum.get("orphans"))
    claims = sum(1 for p in glob.glob(os.path.join(w, "claims", "*.jsonl"))
                 for line in open(p, encoding="utf-8") if line.strip())
    print("== Iddia defteri satiri (claims/*.jsonl):", claims)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
