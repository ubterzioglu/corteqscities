"""Ulke paketi yazar ciktisini script ile denetler (yazarin kendi dogrulamasina guvenmez).

Kullanim: pack_check.py <ES\\_is> <konu>
Bakilanlar: kart/claim/baglanti alan ve kimlikleri, kart basina <=2 kaynak, kaynak kimliklerinin dizinde olmasi, claim
alintisinin kaynak metninde (NFKC + bosluk + harf buyuklugu normalize) gecmesi, claim kaynaginin kartin source_ids'inde
olmasi, sehir adi ve yasakli ifade ('teyit et'), her kartta >=1 baglanti ve claim. valid_until.json yalniz tarihe
duyarli kartlari listeler (eksik kart = tarihe duyarsiz); yazar null yazdiysa kart 'bitis tarihi bilinmiyor' demektir.
Cikis 0 temiz / 1 bulgu.
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

CITIES = ("barcelona", "madrid", "sevilla", "valensiya", "valencia", "málaga", "malaga", "bilbao", "palma", "marbella",
          "alicante", "tarragona", "zaragoza", "tenerife")
BANNED = ("teyit et", "doğrulayın")
REQUIRED = ("entry_id", "city_id", "slug", "title", "summary", "source_ids", "order", "topic_id", "editorial_status")


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", text)).strip().casefold()


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def main(work: Path, topic: str) -> int:
    out = work / "yazar" / "out" / topic
    cards, claims = rows(out / f"Yanıtlar.{topic}.jsonl"), rows(out / f"claims.{topic}.jsonl")
    actions = rows(out / f"Bağlantılar.{topic}.jsonl")
    valid = json.loads((out / "valid_until.json").read_text(encoding="utf-8"))
    index = {r["source_id"]: r for r in rows(work / "kaynak_dizini.jsonl")}
    texts: dict[str, str] = {}
    findings: list[str] = []
    for card in cards:
        slug = card.get("slug")
        miss = [k for k in REQUIRED if not card.get(k)]
        if miss:
            findings.append(f"{slug}: eksik alan {miss}")
        ids = [s for s in str(card.get("source_ids", "")).split(";") if s]
        if not 1 <= len(ids) <= 2:
            findings.append(f"{slug}: kaynak sayisi {len(ids)}")
        findings += [f"{slug}: kaynak dizinde yok {s}" for s in ids if s not in index]
        blob = norm(json.dumps(card, ensure_ascii=False))
        findings += [f"{slug}: sehir adi '{c}'" for c in CITIES if re.search(rf"\b{c}\b", blob)]
        findings += [f"{slug}: yasakli ifade '{b}'" for b in BANNED if b in blob]
        if not any(a.get("entry_id") == card.get("entry_id") for a in actions):
            findings.append(f"{slug}: baglanti yok")
        if not any(c.get("entry_id") == card.get("entry_id") for c in claims):
            findings.append(f"{slug}: claim yok")
    by_entry = {c["entry_id"]: set(str(c.get("source_ids", "")).split(";")) for c in cards}
    for claim in claims:
        sid = claim.get("source_id")
        if claim.get("entry_id") not in by_entry:
            findings.append(f"{claim.get('claim_id')}: karti yok")
            continue
        if sid not in by_entry[claim["entry_id"]]:
            findings.append(f"{claim['claim_id']}: kaynak {sid} kartin source_ids'inde degil")
        if sid in index and sid not in texts:
            texts[sid] = norm(Path(index[sid]["text_file"]).read_text(encoding="utf-8"))
        if sid in texts and norm(str(claim.get("quote", ""))) not in texts[sid]:
            findings.append(f"{claim['claim_id']}: alinti kaynak metninde yok")
    print(json.dumps({"topic": topic, "cards": len(cards), "claims": len(claims), "actions": len(actions),
                      "findings": len(findings)}, ensure_ascii=False))
    for item in findings:
        print(" -", item)
    return 1 if findings else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))
