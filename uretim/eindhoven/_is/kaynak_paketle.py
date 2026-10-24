"""Kullanilan kaynaklarin HTML kopyalarini pakete tasir ve Kaynaklar satirlarina snapshot_file/sha256 yazar (pilot is script'i).

Kullanim: python kaynak_paketle.py <_is klasoru> <paket_koku>
Okur: data/Kaynaklar.jsonl (birlestir.py ciktisi; yalniz kullanilan kaynaklar), kaynak_dizini.jsonl (html_file)
Yazar: <paket>/Lisans kanıtları/kaynaklar/<sha256>.<uzanti> ve data/Kaynaklar.jsonl (snapshot_file, snapshot_sha256 dolu)
Sozlesme (DIGEST §2 Kaynaklar): snapshot_file doluysa dosya pakette olmali ve hash eslesmeli. Kullanilmayan kopya pakete girmez (K05).
birlestir.py her calismada Kaynaklar.jsonl'i yeniden yazar; bu script ondan SONRA calistirilir. stdout tek satir JSON.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys

SUBDIR = "Lisans kanıtları/kaynaklar"


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def resolve(w: str, html_file: str) -> str:
    """Ana kopya klasoru (snap/) dosya adiyla; kaynak_ekle.py ile eklenenler '<alt_klasor>\\<ad>' bicimiyle kayitli."""
    return os.path.join(w, html_file) if ("\\" in html_file or "/" in html_file) else os.path.join(w, "snap", html_file)


def main(w: str, pkg: str) -> int:
    index = {}
    for line in open(os.path.join(w, "kaynak_dizini.jsonl"), encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            index[r["source_id"]] = r
    rows = [json.loads(l) for l in open(os.path.join(w, "data", "Kaynaklar.jsonl"), encoding="utf-8") if l.strip()]
    target_dir = os.path.join(pkg, *SUBDIR.split("/"))
    os.makedirs(target_dir, exist_ok=True)
    copied, missing, out = 0, [], []
    for r in rows:
        src = index.get(r["source_id"], {})
        path = resolve(w, src.get("html_file") or "") if src.get("html_file") else ""
        if not path or not os.path.exists(path):
            missing.append(r["source_id"])
            out.append({**r, "snapshot_file": "", "snapshot_sha256": "", "verified": "Hayır"})
            continue
        digest = sha256(path)
        ext = os.path.splitext(path)[1] or ".html"
        name = f"{digest}{ext}"
        dest = os.path.join(target_dir, name)
        if not os.path.exists(dest):
            shutil.copyfile(path, dest)
            copied += 1
        if sha256(dest) != digest:
            raise SystemExit(f"hash uyusmuyor: {dest}")
        out.append({**r, "snapshot_file": f"{SUBDIR}/{name}", "snapshot_sha256": digest})
    with open(os.path.join(w, "data", "Kaynaklar.jsonl"), "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
    keep = {os.path.basename(r["snapshot_file"]) for r in out if r["snapshot_file"]}
    stale = [n for n in os.listdir(target_dir) if n not in keep]
    for n in stale:
        os.remove(os.path.join(target_dir, n))
    print(json.dumps({"sources": len(rows), "with_snapshot": len(rows) - len(missing), "copied": copied,
                      "removed_unused": len(stale), "missing": missing[:10]}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], sys.argv[2]))
