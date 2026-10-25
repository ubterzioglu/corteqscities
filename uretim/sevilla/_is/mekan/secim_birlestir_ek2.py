"""secim_birlestir_ek2.py: secim_G/H ciktilarini selected_ek2.jsonl'de birlestirir (ana dongu betigi).

Kullanim: python -I -X utf8 secim_birlestir_ek2.py <WORK> [harfler: G,H]
Kurallar (SKILL faz 4): ayni slug ya da ayni dolu qid ikinci kez gelirse atilir; bos qid eslesme sayilmaz.
Pakette olan slug/title ve selected/selected_ek'teki slug/qid atilir. Koordinat yalniz kutu icinde; disi bos yazilir ve raporlanir.
Cikti: _is\\mekan\\selected_ek2.jsonl + stdout ozet (grup dagilimi, atilanlar).
"""
from __future__ import annotations

import glob
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
WORK = Path(sys.argv[1])
LETTERS = (sys.argv[2] if len(sys.argv) > 2 else "G,H").split(",")
IS = WORK / "_is"
BB = (37.30, 37.45, -6.03, -5.89)
GROUPS = {"Müzeler", "Sanat ve sergiler", "Sahne ve müzik", "Spor", "Doğa ve açık hava", "Çocuklarla keşif", "Yeme ve içme", "Tarih ve mimari"}


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.exists() else []


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFKD", (s or "").lower()).encode("ascii", "ignore").decode()).strip()


existing_slugs, existing_titles, existing_qids = set(), set(), set()
for p in glob.glob(str(IS / "data" / "parcalar" / "*.jsonl")):
    for r in jl(Path(p)):
        if r.get("slug"):
            existing_slugs.add(r["slug"])
        if r.get("title"):
            existing_titles.add(norm(r["title"]))
for name in ("selected.jsonl", "selected_ek.jsonl"):
    for r in jl(IS / "mekan" / name):
        if r.get("slug"):
            existing_slugs.add(r["slug"])
        if r.get("qid"):
            existing_qids.add(r["qid"])

out, dropped, seen_slug, seen_qid = [], [], set(), set()
for L in LETTERS:
    for r in jl(IS / "mekan" / f"secim_{L.strip()}.jsonl"):
        slug = r.get("slug") or ""
        qid = r.get("qid") or ""
        why = None
        if not slug or not r.get("url") or not r.get("must_contain") or not r.get("name"):
            why = "eksik alan"
        elif r.get("group") not in GROUPS:
            why = f"grup geçersiz: {r.get('group')}"
        elif slug in existing_slugs or slug in seen_slug:
            why = "slug çakışması"
        elif norm(r.get("name")) in existing_titles:
            why = "başlık pakette var"
        elif qid and (qid in existing_qids or qid in seen_qid):
            why = "qid çakışması"
        if why:
            dropped.append({"harf": L, "slug": slug, "name": r.get("name"), "neden": why})
            continue
        lat, lon = r.get("lat"), r.get("lon")
        try:
            lat, lon = (float(lat), float(lon)) if lat not in ("", None) and lon not in ("", None) else ("", "")
        except (TypeError, ValueError):
            lat, lon = "", ""
        if lat != "" and not (BB[0] <= lat <= BB[1] and BB[2] <= lon <= BB[3]):
            dropped.append({"harf": L, "slug": slug, "name": r.get("name"), "neden": f"kutu dışı koordinat {lat},{lon} (boşaltıldı, aday kaldı)"})
            lat, lon = "", ""
        r["lat"], r["lon"] = lat, lon
        r["entry_id"] = f"sevilla:{slug}"
        r["_harf"] = L
        seen_slug.add(slug)
        if qid:
            seen_qid.add(qid)
        out.append(r)

dst = IS / "mekan" / "selected_ek2.jsonl"
with dst.open("w", encoding="utf-8", newline="\n") as f:
    for r in out:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
groups: dict[str, int] = {}
for r in out:
    groups[r["group"]] = groups.get(r["group"], 0) + 1
print(json.dumps({"selected": len(out), "groups": groups, "with_coords": sum(1 for r in out if r["lat"] != ""), "with_qid": sum(1 for r in out if r.get("qid")),
                  "dropped": dropped, "out": str(dst)}, ensure_ascii=False))
