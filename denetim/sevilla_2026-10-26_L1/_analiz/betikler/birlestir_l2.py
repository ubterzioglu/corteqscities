"""birlestir_l2.py: L2 ajan çıktılarını karşı denetim kararlarıyla birleştirir (CLAIM, PHOTO, lisans).

Kullanım: python -I -X utf8 birlestir_l2.py <OUT>
Okur: claim-script.json; _iddia/parti_NN.jsonl, kart_NN.jsonl, karsi_*.jsonl; _sonnet/_iddia/* (01-02 ilk geçiş);
      _foto/photo-review_A,B (Sonnet), _O1..O3 (Opus), karsi_foto.jsonl; _l/lisans_NN.jsonl, karsi_lisans.jsonl;
      _analiz/k61_dhash.json; dosya-envanteri.json; _dump/*.
Yazar (yalnız OUT altına): claim-checks.json, photo-review.json, _analiz/lisans-birlesik.json.
Karşı denetim kuralı: "çürütüldü" ilk olumsuz kararı kaldırır; "teyit" korur ve önceliği (oncelik_onerisi) taşır;
"belirsiz" ilk kararı değiştirmez. 01-02'de Sonnet ile Opus farkı ("fark") çürütülmüşse Sonnet kararı geçerlidir.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(sys.argv[1])
SEVERITY = {"reject": 2, "flag": 1, "keep": 0}
NEG = ("yanlış", "eski", "kaynak_yetersiz", "erişilemedi")
CARD_CHECKS = ("K25", "K26", "K31", "K32", "K40", "K48")


def load(rel: str):
    return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))


def jl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def norm_id(s) -> str:
    return re.sub(r"\s+", "", str(s or ""))


def pid_full(p: str) -> str:
    p = str(p or "")
    return p if p.startswith("sevilla:photo:") else f"sevilla:photo:{p}"


# ------------------------------------------------------------------ CLAIM
script = load("claim-script.json")
script_by_id = {r["claim_id"]: r for r in script["results"]}
parts = sorted({p.stem.split("_")[1] for p in (OUT / "_iddia").glob("parti_*.jsonl")})
agent_claims, cards = [], []
for nn in parts:
    seen = set()
    for row in jl(OUT / "_iddia" / f"parti_{nn}.jsonl"):
        cid = row.get("claim_id")
        if not cid or cid in seen:
            continue
        seen.add(cid)
        s = script_by_id.get(cid)
        agent_claims.append({**row, "parti": nn, "script_result": s["result"] if s else "kural (script dışı)",
                             "script_kind": s["kind"] if s else None})
    seen_c = set()
    for c in jl(OUT / "_iddia" / f"kart_{nn}.jsonl"):
        if c.get("entry_id") and c["entry_id"] not in seen_c:
            seen_c.add(c["entry_id"])
            cards.append({**c, "parti": nn})

karsi: dict[tuple[str, str], dict] = {}
karsi_rows = 0
for f in sorted((OUT / "_iddia").glob("karsi_*.jsonl")):
    for r in jl(f):
        tur, rid = r.get("tur"), norm_id(r.get("id"))
        if tur in ("claim", "kart", "fark") and rid:
            karsi[(tur, rid)] = {**r, "_dosya": f.name}
            karsi_rows += 1

sonnet_claims = {r["claim_id"]: r for nn in ("01", "02") for r in jl(OUT / "_sonnet" / "_iddia" / f"parti_{nn}.jsonl")
                 if r.get("claim_id")}
sonnet_cards = {r["entry_id"]: r for nn in ("01", "02") for r in jl(OUT / "_sonnet" / "_iddia" / f"kart_{nn}.jsonl")
                if r.get("entry_id")}

applied = Counter()
for c in agent_claims:
    c["sonuç_ilk"] = c.get("sonuç")
    k = karsi.get(("claim", norm_id(c["claim_id"])))
    fk = karsi.get(("fark", norm_id(c["claim_id"])))
    if k:
        c["karsi"] = {x: k.get(x) for x in ("karsi_karar", "oncelik_onerisi", "dogrusu", "gerekce", "kanit_url", "alinti")}
        if k.get("karsi_karar") == "çürütüldü" and c.get("sonuç") in NEG:
            c["sonuç"] = "doğru"
            applied["claim_çürütüldü"] += 1
        elif k.get("karsi_karar") == "teyit":
            applied["claim_teyit"] += 1
            if k.get("dogrusu") and not c.get("doğrusu"):
                c["doğrusu"] = k["dogrusu"]
        else:
            applied["claim_belirsiz"] += 1
    if fk:
        c["karsi_fark"] = {x: fk.get(x) for x in ("ilk_karar", "karsi_karar", "gerekce", "kanit_url", "alinti")}
        if fk.get("karsi_karar") == "çürütüldü" and c["claim_id"] in sonnet_claims:
            c["sonuç"] = sonnet_claims[c["claim_id"]].get("sonuç", c["sonuç"])
            applied["fark_sonnet_kabul"] += 1

for card in cards:
    card["karsi"] = {}
    for K in CARD_CHECKS + ("K41",):
        k = karsi.get(("kart", norm_id(f"{card['entry_id']}|{K}")))
        fk = karsi.get(("fark", norm_id(f"{card['entry_id']}|{K}")))
        if fk and fk.get("karsi_karar") == "çürütüldü" and card["entry_id"] in sonnet_cards:
            card[f"{K}_ilk"] = card.get(K)
            card[K] = sonnet_cards[card["entry_id"]].get(K, card.get(K))
            applied["fark_kart_sonnet_kabul"] += 1
        if not k:
            continue
        card["karsi"][K] = {x: k.get(x) for x in ("karsi_karar", "oncelik_onerisi", "gerekce", "kanit_url", "alinti")}
        ilk = card.get(K)
        if k.get("karsi_karar") == "çürütüldü" or k.get("oncelik_onerisi") == "bulgu değil":
            card[f"{K}_ilk"] = ilk
            card[K] = "yok" if K == "K41" else "geçti"
            applied["kart_çürütüldü"] += 1
        elif k.get("karsi_karar") == "teyit":
            if ilk == "belirsiz":
                card[f"{K}_ilk"] = ilk
                card[K] = "kaldı"
            applied["kart_teyit"] += 1
        else:
            applied["kart_belirsiz"] += 1


def card_priority(card: dict, K: str) -> str:
    k = card.get("karsi", {}).get(K) or {}
    p = k.get("oncelik_onerisi")
    if p in ("P0", "P1", "P2"):
        return p
    return "P2" if K in ("K32", "K48", "K41") else "P1"


card_fails = []
for c in cards:
    kal = [K for K in CARD_CHECKS if c.get(K) == "kaldı"]
    k41 = c.get("K41") == "var"
    if kal or k41:
        card_fails.append({
            "entry_id": c["entry_id"], "_row": c.get("_row"), "title": c.get("title"), "parti": c["parti"],
            "kaldı": kal, "öncelik": {K: card_priority(c, K) for K in kal + (["K41"] if k41 else [])},
            "K41_var": k41,
            "notlar": {K: c.get(f"{K}_not") for K in CARD_CHECKS + ("K41",) if c.get(f"{K}_not")},
            "karsi": c.get("karsi", {}),
        })

ids = [c["claim_id"] for c in agent_claims]
checked_script = {i for i in ids if i in script_by_id}
claim_doc = {
    "meta": {"tool": "city-audit L2 birlestir", "parts": parts,
             "note": "script sonucu tutarlılıktır; doğruluk kararı ajan CLAIM satırıdır (Opus, 01-02 için Sonnet+Opus); "
                     "karşı denetim 'çürütüldü' kararları uygulandı."},
    "summary": {
        "script_claims": len(script_by_id), "agent_rows": len(agent_claims),
        "script_claims_checked": len(checked_script), "script_claims_not_checked": len(script_by_id) - len(checked_script),
        "rule_claims": sum(1 for c in agent_claims if c["claim_id"] not in script_by_id),
        "by_result": dict(Counter(c["sonuç"] for c in agent_claims)),
        "by_result_ilk": dict(Counter(c["sonuç_ilk"] for c in agent_claims)),
        "by_result_x_script": dict(Counter(f"{c['sonuç']}|{c['script_result']}" for c in agent_claims)),
        "cards_checked": len(cards), "cards_unique": len({c["entry_id"] for c in cards}),
        "cards_failed": len(card_fails),
        "card_fail_by_check": dict(Counter(k for c in card_fails for k in c["kaldı"])),
        "cards_K41_var": sum(1 for c in card_fails if c["K41_var"]),
        "karsi_rows": karsi_rows, "karsi_applied": dict(applied),
    },
    "not_wrong": [c for c in agent_claims if c["sonuç"] != "doğru"],
    "card_failures": card_fails,
    "script_claims_not_checked": [cid for cid in script_by_id if cid not in checked_script],
    "claims": agent_claims,
    "cards": cards,
}
(OUT / "claim-checks.json").write_text(json.dumps(claim_doc, ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------------ LİSANS
lis = {}
for f in sorted((OUT / "_l").glob("lisans_[0-9][0-9].jsonl")):
    for r in jl(f):
        if r.get("photo_id"):
            lis[pid_full(r["photo_id"])] = {**r, "_dosya": f.name}
lis_karsi = Counter()
for r in jl(OUT / "_l" / "karsi_lisans.jsonl"):
    pid = pid_full(r.get("kayit"))
    if pid not in lis:
        continue
    row, chk = lis[pid], r.get("check_id")
    row.setdefault("karsi", []).append(r)
    if r.get("karsi_karar") == "çürütüldü" or r.get("oncelik_onerisi") == "bulgu değil":
        if chk in ("K71", "K72"):
            row[f"{chk}_ilk"] = row.get(chk)
            row[chk] = "geçti"
        row["bulgular"] = [b for b in (row.get("bulgular") or []) if b.get("check_id") != chk]
        lis_karsi["çürütüldü"] += 1
    elif r.get("karsi_karar") == "teyit" and r.get("oncelik_onerisi") in ("P0", "P1", "P2"):
        for b in row.get("bulgular") or []:
            if b.get("check_id") == chk:
                b["oncelik"] = r["oncelik_onerisi"]
        lis_karsi["teyit"] += 1
lis_doc = {"summary": {"incelenen": len(lis), "K71": dict(Counter(r.get("K71") for r in lis.values())),
                       "K72": dict(Counter(r.get("K72") for r in lis.values())), "karsi": dict(lis_karsi)},
           "rows": list(lis.values())}
(OUT / "_analiz" / "lisans-birlesik.json").write_text(json.dumps(lis_doc, ensure_ascii=False, indent=1), encoding="utf-8")

# ------------------------------------------------------------------ PHOTO
inv = {f["path"]: f for f in load("dosya-envanteri.json")["files"]}
fot = jl(OUT / "_dump" / "Fotoğraflar.jsonl")
fk = {r["photo_id"]: r for r in jl(OUT / "_dump" / "FotoğrafKaynakları.jsonl")}
names = {r["entry_id"]: r.get("title") for name in ("Mekânlar", "Mahalleler") for r in jl(OUT / "_dump" / f"{name}.jsonl")}
review: dict[str, list[dict]] = {}
for pay, model in (("A", "sonnet"), ("B", "sonnet"), ("O1", "opus"), ("O2", "opus"), ("O3", "opus")):
    for r in jl(OUT / "_foto" / f"photo-review_{pay}.jsonl"):
        if r.get("key"):
            review.setdefault(pid_full(r["key"]), []).append({**r, "pay": pay, "model": model})
karsi_foto = {pid_full(r["key"]): r for r in jl(OUT / "_foto" / "karsi_foto.jsonl") if r.get("key")}
k61 = {}
if (OUT / "_analiz" / "k61_dhash.json").exists():
    k61 = {r["photo_id"]: r for r in load("_analiz/k61_dhash.json").get("satirlar", [])}

photos = []
for p in fot:
    pid = p["photo_id"]
    seen = review.get(pid, [])
    opus = [r for r in seen if r["model"] == "opus"]
    base = opus or seen
    worst = max(base, key=lambda r: SEVERITY.get(r.get("result"), 0)) if base else None
    kf = karsi_foto.get(pid)
    if kf:
        sonuc, neden, chk, onc = kf.get("karar"), kf.get("gerekce"), kf.get("check_id"), kf.get("oncelik")
        gorulen = kf.get("gorulen") or (worst or {}).get("seen")
    elif worst:
        sonuc, neden, chk, onc = worst.get("result"), worst.get("reason"), None, None
        gorulen = worst.get("seen")
    else:
        sonuc, neden, chk, onc, gorulen = "incelenmedi", "", None, None, None
    f = inv.get(p["file"], {})
    k = fk.get(pid, {})
    lic = lis.get(pid)
    d = k61.get(pid)
    photos.append({
        "photo_id": pid, "dosya": p["file"], "SHA256": f.get("sha256"), "gerçek_format": f.get("ext"),
        "width": k.get("web_width"), "height": k.get("web_height"), "bağlı_entry_id": p.get("entry_id"),
        "hedef_mekân": names.get(p.get("entry_id"), p.get("entry_id") or "kapak"), "rol": p.get("role"), "_row": p["_row"],
        "görüntüde_görülen": gorulen,
        "eser_kaynak_eşleşmesi": (f"dHash {d['mesafe']} (Commons küçük resmi ↔ teslim)" if d else None),
        "gerçek_yazar": p.get("author"), "lisans_sürümü": p.get("license"), "lisans_URL": p.get("license_url"),
        "ek_hak_notu": neden if sonuc != "keep" else "", "kaynak_kanıtı": p.get("source_url"),
        "lisans_kanıtı": p.get("license_url"), "türev_grubu": None,
        "görsel_sonuç": sonuc, "görsel_check": chk, "görsel_öncelik": onc,
        "ilk_kararlar": {r["pay"]: r.get("result") for r in seen},
        "pafta_slot": [f"{r.get('sheet')}/{r.get('slot')}" for r in seen],
        "hak_zinciri_sonucu": ({"K71": lic.get("K71"), "K72": lic.get("K72"), "bulgular": lic.get("bulgular")}
                               if lic else "lisans ajanı satırı yok"),
        "incelenen_dosya_hashi": f.get("sha256"),
    })
photo_doc = {
    "meta": {"tool": "city-audit L2 birlestir",
             "note": "görsel sonuç: karşı foto kararı > Opus taraması > Sonnet taraması; hak zinciri lisans ajanlarından "
                     "(334/334) karşı denetimle; bayt/SHA envanterden; dHash k61_dhash.py"},
    "summary": {
        "photo_rows": len(fot), "reviewed": sum(1 for p in photos if p["görsel_sonuç"] != "incelenmedi"),
        "reviewed_opus": sum(1 for p in fot if any(r["model"] == "opus" for r in review.get(p["photo_id"], []))),
        "not_reviewed": [p["photo_id"] for p in photos if p["görsel_sonuç"] == "incelenmedi"],
        "by_result": dict(Counter(p["görsel_sonuç"] for p in photos)),
        "karsi_foto": len(karsi_foto),
        "sonnet_opus_fark": sum(1 for p in photos if len(set(p["ilk_kararlar"].values())) > 1),
        "license_rows": len(lis),
        "K71": dict(Counter(r.get("K71") for r in lis.values())),
        "K72": dict(Counter(r.get("K72") for r in lis.values())),
    },
    "rejects": [p for p in photos if p["görsel_sonuç"] == "reject"],
    "flags": [p for p in photos if p["görsel_sonuç"] == "flag"],
    "photos": photos,
}
(OUT / "photo-review.json").write_text(json.dumps(photo_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"claims": claim_doc["summary"], "photos": photo_doc["summary"], "lisans": lis_doc["summary"]},
                 ensure_ascii=False))
