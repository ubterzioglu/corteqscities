"""Kaynaklar <=500 (2. yol): bir kaynagin (P) dayandigi her iddia alintisi, iddianin sahibi kaydin BASKA bir kaynaginin (S)
metin kopyasinda birebir geciyorsa iddialar S'ye baglanir, P kaydin source_ids'inden cikar. P baska kayitta, butonda ya da
karsilanmayan iddiada kullaniliyorsa aday degildir. Once turizm portali adaylari. Mekanik ve dogrulanabilir: alinti S'de aranir.
Kullanim: python -I kapasite_birlestir.py <gereken_sayi> [--uygula]
Degisiklik kaydi: denetim\\kapasite-d5_degisiklik.jsonl; yedekler d3_arac\\yedek_kapasite_birlestir\\.
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
RX = re.compile(r"\b(?:sevilla|es):kaynak:\d+\b")
PORTAL = re.compile(r"visitasevilla|andalucia\.org|turismo", re.I)
OWN = ("entry_id", "term_id", "route_id", "field_id")
YEDEK = W / "d3_arac" / "yedek_kapasite_birlestir"


def jl(p: Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


def norm(s: str) -> str:
    """Yalniz harf ve rakam (noktalama, tirnak, bosluk farki yok sayilir); merge_package alinti kontrolune yakin."""
    return re.sub(r"[\W_]+", "", (s or "").lower())


def main(need: int, apply: bool) -> int:
    index = {r["source_id"]: r for r in jl(W / "kaynak_dizini.jsonl")}
    text_cache: dict[str, str] = {}

    def text(sid: str) -> str:
        if sid not in text_cache:
            p = Path(index.get(sid, {}).get("text_file") or "")
            text_cache[sid] = norm(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else ""
        return text_cache[sid]

    records = {}  # owner -> (file, row)
    for f in sorted(PARTS.glob("*.jsonl")):
        if f.name.startswith(("Bağlantılar", "Fotoğraf", "Kanıtlar", "Adımlar")):
            continue
        for row in jl(f):
            owner = next((row[k] for k in OWN if row.get(k)), None)
            if owner:
                records[owner] = (f, row)
    rec_uses = defaultdict(set)
    for owner, (f, row) in records.items():
        for sid in RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False)):
            rec_uses[sid].add(owner)
    claim_files = sorted((W / "claims").glob("*.jsonl"))
    claims_by_src = defaultdict(list)
    for f in claim_files:
        for c in jl(f):
            claims_by_src[c.get("source_id")].append((f, c))
    button_urls = {b.get("url") for f in PARTS.glob("Bağlantılar.*.jsonl") for b in jl(f)}
    cands = []
    for sid, owners in rec_uses.items():
        urls = {index.get(sid, {}).get("url"), index.get(sid, {}).get("final_url")} - {None}
        if urls & button_urls:
            continue
        plan, ok = [], True
        claim_owners = {next((c[k] for k in OWN if c.get(k)), None) for _, c in claims_by_src[sid]}
        if not claim_owners <= owners:
            continue  # kaydin source_ids'inde olmayan sahipten iddia: dokunma
        for owner in owners:
            f, row = records[owner]
            others = [s for s in RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False)) if s != sid]
            if not others:
                ok = False
                break
            for cf, c in claims_by_src[sid]:
                if next((c[k] for k in OWN if c.get(k)), None) != owner:
                    continue
                q = norm(c.get("quote"))
                target = next((s for s in others if q and q in text(s)), None)
                if not target:
                    ok = False
                    break
                plan.append((cf, c.get("claim_id"), target))
            if not ok:
                break
        if ok:
            cands.append({"source_id": sid, "portal": bool(PORTAL.search(next(iter(urls), "") or "")), "kayit": sorted(owners),
                          "iddia": len(plan), "plan": plan})
    cands.sort(key=lambda c: (not c["portal"], c["iddia"]))
    print(json.dumps({"aday": len(cands), "gereken": need,
                      "ilk": [(c["source_id"], c["portal"], c["kayit"][:2], c["iddia"]) for c in cands[:12]]}, ensure_ascii=False))
    if not apply:
        return 0
    chosen = cands[:need]
    if len(chosen) < need:
        print("YETERSIZ", len(chosen))
        return 1
    YEDEK.mkdir(parents=True, exist_ok=True)
    touched_rec = defaultdict(set)   # file -> owners to strip sid
    touched_claim = defaultdict(dict)  # claim file -> claim_id -> target
    strip = defaultdict(set)
    for c in chosen:
        for owner in c["kayit"]:
            f, _ = records[owner]
            touched_rec[f].add(owner)
            strip[owner].add(c["source_id"])
        for cf, cid, target in c["plan"]:
            touched_claim[cf][cid] = target
    log = []
    for f, owners in touched_rec.items():
        shutil.copy2(f, YEDEK / f.name)
        rows = jl(f)
        for row in rows:
            owner = next((row[k] for k in OWN if row.get(k)), None)
            if owner in owners:
                old = row.get("source_ids")
                ids = [s for s in RX.findall(json.dumps(old, ensure_ascii=False)) if s not in strip[owner]]
                row["source_ids"] = "\n".join(ids) if isinstance(old, str) and "\n" in old else (", ".join(ids) if isinstance(old, str) else ids)
                log.append({"entry_id": owner, "alan": "source_ids", "eski": old, "yeni": row["source_ids"],
                            "bulgu_claim_id": "kapasite-kaynaklar-500", "gerekce": "iddialarin alintisi kaydin diger kaynaginda birebir; fazlalik kaynak cikti", "alinti": ""})
        f.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    for cf, mapping in touched_claim.items():
        shutil.copy2(cf, YEDEK / f"claims_{cf.name}")
        rows = jl(cf)
        for c in rows:
            if c.get("claim_id") in mapping:
                t = mapping[c["claim_id"]]
                c["source_id"], c["url"] = t, index.get(t, {}).get("url", c.get("url"))
        cf.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    with (W / "denetim" / "kapasite-d5_degisiklik.jsonl").open("a", encoding="utf-8") as out:
        for r in log:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"bosalan": [c["source_id"] for c in chosen], "kayit_degisen": len(log)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(int(sys.argv[1]), "--uygula" in sys.argv))
