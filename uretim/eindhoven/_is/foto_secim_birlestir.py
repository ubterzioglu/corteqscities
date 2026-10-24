"""Gorsel inceleme ciktilarini tek secim listesine birlestirir (pilot is script'i).

Kullanim: python foto_secim_birlestir.py <_is klasoru> [--max-per-entry 3]
Okur: foto/inceleme/selected_*.jsonl, verify_*.jsonl (ok=false atilir, caption_fix uygulanir), covers.jsonl
Yazar: foto/selected.jsonl ({key, entry_id, role, caption, seen}); stdout tek satir JSON.
Kurallar: mekan basina en cok N kare; ayni Commons dosyasi iki ayri mekana verilmez (ilk gelen kalir);
kapaklar (rol Kapak) mekan fotolariyla ayni dosya olabilir.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()] if os.path.exists(path) else []


def preview_paths(work: str) -> dict:
    """Tum paftalardan key -> onizleme yolu (foto/pafta* ve ek tur klasorleri foto_*/pafta*)."""
    out = {}
    sheets = glob.glob(os.path.join(work, "foto", "pafta*", "sheets.json")) + \
        glob.glob(os.path.join(work, "foto_*", "pafta*", "sheets.json"))
    for sj in sheets:
        for sheet in json.load(open(sj, encoding="utf-8")):
            for it in sheet["items"]:
                out[it["key"]] = it["path"]
    return out


def dhash_of(path: str):
    """toolkit image_hash.dhash (64 bit); yol yoksa None."""
    sys.path.insert(0, r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
    sys.dont_write_bytecode = True
    from image_hash import dhash
    return dhash(path) if path and os.path.exists(path) else None


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("work")
    p.add_argument("--max-per-entry", type=int, default=3)
    p.add_argument("--dhash", type=int, default=5, help="ayni kayitta bu Hamming uzakligina kadar yakin kopya atilir")
    a = p.parse_args()
    d = os.path.join(a.work, "foto", "inceleme")
    verdict = {}
    for path in glob.glob(os.path.join(d, "verify_*.jsonl")):
        for v in read_jsonl(path):
            verdict[v["key"]] = v
    per_entry, used_file, out = collections.Counter(), {}, []
    dropped = collections.Counter()
    previews = preview_paths(a.work)
    kept_hashes = collections.defaultdict(list)  # entry -> [dhash]; farkli turlarin seri cekimlerini ele
    for path in sorted(glob.glob(os.path.join(d, "selected_*.jsonl"))):
        for s in read_jsonl(path):
            v = verdict.get(s["key"])
            if v is None:
                dropped["ikinci_goz_yok"] += 1
                continue
            if not v.get("ok"):
                dropped["ikinci_goz_red"] += 1
                continue
            entry = s.get("entry_id") or s["key"].split("|", 1)[0]
            commons_file = s["key"].split("|", 1)[-1]
            if per_entry[entry] >= a.max_per_entry:
                dropped["mekan_basina_ust_sinir"] += 1
                continue
            if commons_file in used_file and used_file[commons_file] != entry:
                dropped["ayni_dosya_baska_mekanda"] += 1
                continue
            h = dhash_of(previews.get(s["key"]))
            if h is not None and any(bin(h ^ k).count("1") <= a.dhash for k in kept_hashes[entry]):
                dropped["yakin_kopya_dhash"] += 1
                continue
            if h is not None:
                kept_hashes[entry].append(h)
            used_file[commons_file] = entry
            per_entry[entry] += 1
            caption = (v.get("caption_fix") or s.get("caption") or "").strip()
            out.append({"key": s["key"], "entry_id": entry, "role": "Mekân", "caption": caption[:250], "seen": s.get("seen", "")})
    covers = read_jsonl(os.path.join(d, "covers.jsonl"))
    for c in covers:
        out.append({"key": c["key"], "entry_id": "", "role": "Kapak", "caption": (c.get("caption") or "")[:250],
                    "seen": c.get("seen", "")})
    with open(os.path.join(a.work, "foto", "selected.jsonl"), "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    print(json.dumps({"venue_photos": sum(1 for r in out if r["role"] == "Mekân"), "covers": len(covers),
                      "entries_with_photo": len(per_entry), "dropped": dict(dropped)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
