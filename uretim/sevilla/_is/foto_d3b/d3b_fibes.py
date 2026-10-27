"""Foto D3b ek turu: foto_d3/karar.jsonl'de atlanan 'S14-yedek' satiri (Fibes) - mekanin karesi yoktu, bu bir ekleme.

1) search: Commons imageinfo (commons_search fonksiyonlari, ana onbellek) -> foto_d3b/search.jsonl;
   candidates.jsonl ayrica photo_candidates from-search ile uretilir.
2) select: foto/selected.jsonl sonuna tek satir eklenir (photo_rows numarayi slug basina verir -> fibes-01).
Kullanim: python -I d3b_fibes.py search | select
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
TK = Path(r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
D3B = W / "foto_d3b"
BULGU = "S14-yedek"
# karar satirindaki 'gorulen'den (<=250, yalniz karede gorulen); ana dongu pafta yerine kareyi acip bakti (26.10.2026)
CAPTION = ("Fibes Kongre ve Fuar Sarayı'nın altın kubbesi ve tuğla kemerli revakları; önde tuğla duvar, "
           "bisiklet yolu, AB ve Fibes bayrakları.")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def decision() -> dict:
    rows = [d for d in read_jsonl(W / "foto_d3" / "karar.jsonl") if d.get("bulgu") == BULGU]
    if len(rows) != 1:
        raise SystemExit(f"{BULGU} satiri {len(rows)} adet")
    return rows[0]


def run_search() -> int:
    sys.path.insert(0, str(TK))
    import commons_search as cs
    d = decision()
    title = cs.norm_title(d["yeni_commons_file"])
    client = cs.Client(cs.urllib_transport, W / "foto" / "cache", 20)
    infos = cs.fetch_imageinfo(client, [title])
    if title not in infos:
        print(json.dumps({"missing": title}, ensure_ascii=False))
        return 1
    row = {"entry_id": d["entry_id"], "query_kind": "elle_karar_d3", "title": title, "imageinfo": infos[title]}
    (D3B / "search.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"written": 1, "title": title}, ensure_ascii=False))
    return 0


def run_select() -> int:
    d = decision()
    sel_path = W / "foto" / "selected.jsonl"
    selected = read_jsonl(sel_path)
    key = f"{d['entry_id']}|{d['yeni_commons_file']}"
    if any(r["key"] == key or r.get("entry_id") == d["entry_id"] for r in selected):
        print(json.dumps({"problems": [f"zaten secimde: {d['entry_id']}"]}, ensure_ascii=False))
        return 2
    row = {"key": key, "entry_id": d["entry_id"], "role": "Mekân", "caption": CAPTION, "seen": d["gorulen"]}
    sel_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in [*selected, row]), encoding="utf-8")
    print(json.dumps({"selected_before": len(selected), "selected_after": len(selected) + 1, "added": key},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(run_search() if sys.argv[1] == "search" else run_select())
