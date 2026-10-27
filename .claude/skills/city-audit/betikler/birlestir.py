"""birlestir.py: L1 ajan çıktılarını birleştirir (CLAIM + PHOTO kayıtları).

Kullanım: python -I -X utf8 birlestir.py <OUT>
Okur: claim-script.json, _iddia/parti_NN.jsonl + kart_NN.jsonl, _foto/photo-review_A/B.jsonl,
      _l/lisans.jsonl, dosya-envanteri.json, _dump/Fotoğraflar.jsonl, FotoğrafKaynakları.jsonl, Mekânlar, Mahalleler.
Yazar (yalnız OUT altına): claim-checks.json, photo-review.json.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(sys.argv[1])
SEVERITY = {"reject": 2, "flag": 1, "keep": 0}


def load(rel: str):
    return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


# ------------------------------------------------------------------ CLAIM
script = load("claim-script.json")
script_by_id = {r["claim_id"]: r for r in script["results"]}
agent_claims: list[dict] = []
cards: list[dict] = []
parts = sorted(p.stem.split("_")[1] for p in (OUT / "_iddia").glob("parti_*.jsonl"))
for nn in parts:
    for row in jl(OUT / "_iddia" / f"parti_{nn}.jsonl"):
        s = script_by_id.get(row["claim_id"])
        agent_claims.append({**row, "parti": nn, "script_result": s["result"] if s else "kural (script dışı)",
                             "script_kind": s["kind"] if s else None})
    kart = OUT / "_iddia" / f"kart_{nn}.jsonl"
    if kart.exists():
        cards += [{**c, "parti": nn} for c in jl(kart)]

ids = [c["claim_id"] for c in agent_claims]
dups = [k for k, v in Counter(ids).items() if v > 1]
checked_script = {i for i in ids if i in script_by_id}
not_checked = [cid for cid, r in script_by_id.items() if cid not in checked_script]
card_fails = [
    {"entry_id": c["entry_id"], "_row": c.get("_row"), "title": c.get("title"), "parti": c["parti"],
     "kaldı": [k for k in ("K25", "K26", "K31", "K40") if c.get(k) == "kaldı"],
     "K41_var": c.get("K41") == "var",
     "notlar": {k: c.get(f"{k}_not") for k in ("K25", "K26", "K31", "K40", "K41") if c.get(f"{k}_not")}}
    for c in cards
    if any(c.get(k) == "kaldı" for k in ("K25", "K26", "K31", "K40")) or c.get("K41") == "var"
]
claim_doc = {
    "meta": {"tool": "city-audit L1 birlestir", "parts": parts,
             "note": "script sonucu tutarlılıktır; doğruluk kararı ajan CLAIM satırıdır. Kural iddiaları (:#kural) script dışıdır."},
    "summary": {
        "script_claims": len(script_by_id), "agent_rows": len(agent_claims), "duplicate_claim_ids": dups,
        "script_claims_checked": len(checked_script), "script_claims_not_checked": len(not_checked),
        "rule_claims": sum(1 for c in agent_claims if c["claim_id"] not in script_by_id),
        "by_result": dict(Counter(c["sonuç"] for c in agent_claims)),
        "by_result_x_script": dict(Counter(f"{c['sonuç']}|{c['script_result']}" for c in agent_claims)),
        "cards_checked": len(cards), "cards_unique": len({c["entry_id"] for c in cards}),
        "cards_failed": len(card_fails),
        "card_fail_by_check": dict(Counter(k for c in card_fails for k in c["kaldı"])),
        "cards_K41_var": sum(1 for c in card_fails if c["K41_var"]),
    },
    "not_wrong": [c for c in agent_claims if c["sonuç"] not in ("doğru",)],
    "card_failures": card_fails,
    "script_claims_not_checked": not_checked,
    "claims": agent_claims,
    "cards": cards,
}
(OUT / "claim-checks.json").write_text(json.dumps(claim_doc, ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------------ PHOTO
inv = {f["path"]: f for f in load("dosya-envanteri.json")["files"]}
fot = jl(OUT / "_dump" / "Fotoğraflar.jsonl")
fk = {r["photo_id"]: r for r in jl(OUT / "_dump" / "FotoğrafKaynakları.jsonl")}
names = {r["entry_id"]: r.get("title") for name in ("Mekânlar", "Mahalleler")
         for r in jl(OUT / "_dump" / f"{name}.jsonl")}
review: dict[str, list[dict]] = {}
for pay in ("A", "B"):
    for r in jl(OUT / "_foto" / f"photo-review_{pay}.jsonl"):
        review.setdefault(r["key"], []).append({**r, "pay": pay})
lisans = {r["photo_id"]: r for r in jl(OUT / "_l" / "lisans.jsonl")}

photos = []
for p in fot:
    pid = p["photo_id"]
    seen = review.get(pid, [])
    worst = max(seen, key=lambda r: SEVERITY.get(r["result"], 0)) if seen else None
    f = inv.get(p["file"], {})
    k = fk.get(pid, {})
    lic = lisans.get(pid)
    photos.append({
        "photo_id": pid, "dosya": p["file"], "SHA256": f.get("sha256"), "gerçek_format": f.get("ext"),
        "width": k.get("web_width"), "height": k.get("web_height"), "bağlı_entry_id": p.get("entry_id"),
        "hedef_mekân": names.get(p.get("entry_id"), p.get("entry_id") or "kapak"), "rol": p.get("role"), "_row": p["_row"],
        "görüntüde_görülen": worst["seen"] if worst else None,
        "eser_kaynak_eşleşmesi": None, "gerçek_yazar": p.get("author"), "lisans_sürümü": p.get("license"),
        "lisans_URL": p.get("license_url"), "ek_hak_notu": worst["reason"] if worst and worst["result"] != "keep" else "",
        "kaynak_kanıtı": p.get("source_url"), "lisans_kanıtı": p.get("license_url"),
        "türev_grubu": None,
        "görsel_sonuç": worst["result"] if worst else "incelenmedi",
        "pafta_slot": [f"{r['sheet']}/{r['slot']}" for r in seen],
        "hak_zinciri_sonucu": ({"K71": lic.get("K71"), "K72": lic.get("K72"), "bulgular": lic.get("bulgular")}
                               if lic else "örneklem dışı (validate_all lisans alanları geçti)"),
        "incelenen_dosya_hashi": f.get("sha256"),
    })
reviewed_keys = set(review)
photo_doc = {
    "meta": {"tool": "city-audit L1 birlestir", "note": "görsel sonuç foto ajanından (pafta), hak zinciri lisans ajanından (64 örneklem), bayt/SHA envanterden"},
    "summary": {
        "photo_rows": len(fot), "reviewed": sum(1 for p in photos if p["görsel_sonuç"] != "incelenmedi"),
        "not_reviewed": [p["photo_id"] for p in photos if p["görsel_sonuç"] == "incelenmedi"],
        "review_keys_not_in_excel": sorted(reviewed_keys - {p["photo_id"] for p in fot}),
        "by_result": dict(Counter(p["görsel_sonuç"] for p in photos)),
        "license_sampled": len(lisans),
        "K71": dict(Counter(r.get("K71") for r in lisans.values())),
        "K72": dict(Counter(r.get("K72") for r in lisans.values())),
    },
    "rejects": [p for p in photos if p["görsel_sonuç"] == "reject"],
    "flags": [p for p in photos if p["görsel_sonuç"] == "flag"],
    "photos": photos,
}
(OUT / "photo-review.json").write_text(json.dumps(photo_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"claims": claim_doc["summary"], "photos": photo_doc["summary"]}, ensure_ascii=False))
