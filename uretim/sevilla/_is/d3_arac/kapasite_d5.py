"""Kaynaklar <=500: yalniz buton adresi olarak kalan kaynaklarin butonlarini cikarir (kart baska butonunu korur;
once turizm portali). merge_package'in gecici ciktisindan sayar. Degisiklik kaydi: denetim\\kapasite-d5_degisiklik.jsonl.
Kullanim: python -I kapasite_d5.py <birlestir_data_klasoru> [--uygula]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PARTS = W / "data" / "parcalar"
LIMIT = 500
RX = re.compile(r"\b(?:sevilla|es):kaynak:\d+\b")
PORTAL = re.compile(r"visitasevilla|andalucia\.org|turismo", re.I)


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


def main(data_dir: Path, apply: bool) -> int:
    used = {r["source_id"]: r for r in jl(data_dir / "Kaynaklar.jsonl")}
    ref = set()
    for f in PARTS.glob("*.jsonl"):
        if not f.name.startswith("Bağlantılar"):
            ref |= set(RX.findall(f.read_text(encoding="utf-8")))
    for f in (W / "claims").glob("*.jsonl"):
        ref |= {c.get("source_id") for c in jl(f)}
    url_src = {}
    for sid, r in used.items():
        for u in (r.get("url"), r.get("final_url")):
            if u:
                url_src[u] = sid
    buttons_by_entry = defaultdict(list)
    rows_by_file = {}
    for f in sorted(PARTS.glob("Bağlantılar.*.jsonl")):
        rows_by_file[f] = jl(f)
        for b in rows_by_file[f]:
            buttons_by_entry[b["entry_id"]].append(b)
    only_button = [sid for sid in used if sid not in ref]
    need = max(0, len(used) - LIMIT)
    cands = []
    for sid in only_button:
        urls = {used[sid].get("url"), used[sid].get("final_url")} - {None}
        btns = [(f, b) for f, rows in rows_by_file.items() for b in rows if b.get("url") in urls]
        ok = all(len(buttons_by_entry[b["entry_id"]]) > 1 for _, b in btns)
        cands.append({"source_id": sid, "url": used[sid].get("url"), "portal": bool(PORTAL.search(used[sid].get("url") or "")),
                      "butonlar": [b["action_id"] for _, b in btns], "kart_baska_butonu_var": ok})
    cands.sort(key=lambda c: (not c["kart_baska_butonu_var"], not c["portal"]))
    print(json.dumps({"kaynak": len(used), "gereken_azalma": need, "yalniz_buton": len(only_button)}, ensure_ascii=False))
    for c in cands:
        print(json.dumps(c, ensure_ascii=False))
    if not apply or need == 0:
        return 0
    chosen = [c for c in cands if c["kart_baska_butonu_var"]][:need]
    if len(chosen) < need:
        print("YETERSIZ: butonu cikarilabilir kaynak sayisi", len(chosen))
        return 1
    drop = {a for c in chosen for a in c["butonlar"]}
    log = []
    for f, rows in rows_by_file.items():
        keep = [b for b in rows if b["action_id"] not in drop]
        if len(keep) != len(rows):
            shutil.copy2(f, W / "d3_arac" / f"yedek_kapasite_d5_{f.name}")
            f.write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in keep), encoding="utf-8")
            log += [{"entry_id": b["entry_id"], "alan": "Bağlantılar", "eski": b, "yeni": None, "bulgu_claim_id": "kapasite-kaynaklar-500",
                     "gerekce": "kaynak yalniz bu butonda kaliyordu (Kaynaklar > 500); kart baska butonunu koruyor", "alinti": ""}
                    for b in rows if b["action_id"] in drop]
    with (W / "denetim" / "kapasite-d5_degisiklik.jsonl").open("a", encoding="utf-8") as out:
        for r in log:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"cikan_buton": len(log), "bosalan_kaynak": [c["source_id"] for c in chosen]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(Path(sys.argv[1]), "--uygula" in sys.argv))
