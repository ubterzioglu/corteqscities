"""Yeni kaynak adreslerini ayri klasore kopyalar, must_contain kanitini arar, gecenlere kaynak kimligi verir.

Pilot is script'i (toolkit degil). Kullanim:
  python kaynak_ekle.py <_is klasoru> <aday.jsonl> <alt_klasor_adi> <topic>
aday.jsonl satiri: {"url": "...", "must_contain": ["..."], "title": "...", "publisher": "...", "why": "..."}
- fetch_snapshot ayri out-dir'e (_is/<alt_klasor_adi>) calisir; ana snap/index.jsonl'e dokunulmaz.
- must_contain bossa yalniz "kopya var ve ince degil" sarti aranir.
- Gecen adresler kaynak_dizini.jsonl ve kaynak_taslak.jsonl'e eklenir (zaten varsa mevcut kimlik kullanilir).
- stdout tek satir JSON; <alt_klasor_adi>/eklenen.json: {url: source_id} + reddedilenler.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata

ROOT = r"C:\temp_private\corteqs\0000_newera"
PY = os.path.join(ROOT, ".venv", "Scripts", "python.exe")
FETCH = os.path.join(ROOT, "corteqs-skills", "toolkit", "scripts", "fetch_snapshot.py")


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text).replace("\u00a0", " ")).casefold()


def read_jsonl(path: str) -> list[dict]:
    return [json.loads(line) for line in open(path, encoding="utf-8") if line.strip()]


def main(w: str, cand_path: str, sub: str, topic: str) -> int:
    cands = read_jsonl(cand_path)
    out_dir = os.path.join(w, sub)
    os.makedirs(out_dir, exist_ok=True)
    urls = list(dict.fromkeys(c["url"].strip() for c in cands if c.get("url")))
    with open(os.path.join(out_dir, "urls.txt"), "w", encoding="utf-8") as f:
        f.write("".join(u + "\n" for u in urls))
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    subprocess.run([PY, FETCH, "--urls", os.path.join(out_dir, "urls.txt"), "--out-dir", out_dir,
                    "--cache-dir", os.path.join(w, "cache"), "--retry-transient"], env=env, check=False)
    idx = {r["url"]: r for r in read_jsonl(os.path.join(out_dir, "index.jsonl"))}
    kd_path, kt_path = os.path.join(w, "kaynak_dizini.jsonl"), os.path.join(w, "kaynak_taslak.jsonl")
    kd, kt = read_jsonl(kd_path), read_jsonl(kt_path)
    by_url = {r["url"]: r["source_id"] for r in kd}
    n = max(int(r["source_id"].rsplit(":", 1)[1]) for r in kd)
    added, reused, rejected = {}, {}, []
    for c in cands:
        url = c.get("url", "").strip()
        if not url or url in added or url in reused:
            continue
        s = idx.get(url, {})
        flags = s.get("flags") or []
        if not s.get("text_file") or "thin_text" in flags:
            rejected.append({"url": url, "why": f"kopya yok/ince (status {s.get('status')})"})
            continue
        text = norm(open(os.path.join(out_dir, s["text_file"]), encoding="utf-8").read())
        missing = [m for m in (c.get("must_contain") or []) if norm(m) not in text]
        if missing:
            rejected.append({"url": url, "why": f"kanit metinde yok: {missing}"})
            continue
        if url in by_url:
            reused[url] = by_url[url]
            continue
        n += 1
        sid = f"eindhoven:kaynak:{n:03d}"
        added[url] = sid
        kd.append({"source_id": sid, "topic": topic, "url": url, "final_url": s.get("final_url"), "title": s.get("title"),
                   "publisher": c.get("publisher"), "lang": c.get("lang"),
                   "text_file": os.path.join(out_dir, s["text_file"]), "text_chars": s["text_chars"],
                   "html_file": os.path.join(sub, s["html_file"]), "html_sha256": s["html_sha256"], "why": c.get("why", "")})
        kt.append({"source_id": sid, "city_id": "eindhoven", "title": (s.get("title") or c.get("title") or "")[:180],
                   "publisher": (c.get("publisher") or "")[:120], "url": url, "checked_on": s["fetched_on"][:10],
                   "topic": f"eindhoven:{topic}", "summary": c.get("why", ""), "verified": "Hayır"})
    with open(kd_path, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kd))
    with open(kt_path, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kt))
    json.dump({"map": {**reused, **added}, "rejected": rejected}, open(os.path.join(out_dir, "eklenen.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print(json.dumps({"candidates": len(urls), "added": len(added), "reused": len(reused), "rejected": len(rejected),
                      "out": out_dir}, ensure_ascii=False))
    return 1 if rejected else 0


if __name__ == "__main__":
    raise SystemExit(main(*sys.argv[1:5]))
