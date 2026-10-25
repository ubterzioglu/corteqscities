"""koordinat_uygula.py: L0 bulgulari ISS-006 (koordinat) ve ISS-007 (collection) icin mekanik duzeltme (ana dongu betigi).

Kullanim: python -I -X utf8 koordinat_uygula.py <WORK> [--dry]
- Koordinat: _is\\mekan\\koordinat_cartociudad.json'dan; oncelik Wikidata (wikidata.lat/lon), sonra CartoCiudad ilk tur, sonra retry.
  Yalniz kutu icindeki (37.30-37.45, -6.03..-5.89) degerler yazilir; entry 'ciudad-de-los-ninos-prado' icin Prado bahcesi Wikidata Q6083964 kullanilir.
- collection: bagimsiz muze/tesislerde Evet -> Hayir (liste asagida); museo-taurino-real-maestranza Evet kalir (plaza-de-toros kaydinin alt nesnesi).
- Her degisiklik _is\\denetim\\duzeltme_L0_degisiklik.jsonl'e yazilir (editor.md bicimi).
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
WORK = Path(sys.argv[1])
DRY = "--dry" in sys.argv
IS = WORK / "_is"
BB = (37.30, 37.45, -6.03, -5.89)
PRADO = {"ciudad-de-los-ninos-prado": (37.379694, -5.986895, "Wikidata Q6083964 (Prado de San Sebastián bahçesi; kart konumu bu bahçe)")}
COLLECTION_HAYIR = [
    "museo-de-bellas-artes-de-sevilla", "museo-arqueologico-de-sevilla", "museo-de-artes-y-costumbres-populares",
    "museo-del-baile-flamenco", "casa-fabiola-coleccion-bellver", "centro-ceramica-triana", "museo-historico-militar-sevilla",
    "museo-maritimo-torre-del-oro", "museo-historia-de-la-farmacia-us", "estadio-sanchez-pizjuan-tur", "casa-de-la-ciencia",
    "convento-de-santa-paula",
]


def inb(la, lo):
    return la is not None and lo is not None and BB[0] <= la <= BB[1] and BB[2] <= lo <= BB[3]


def pick(c: dict):
    s = c["entry_id"].split(":")[1]
    if s in PRADO:
        la, lo, src = PRADO[s]
        return la, lo, src
    w = c.get("wikidata")
    if w and inb(w.get("lat"), w.get("lon")):
        return w["lat"], w["lon"], f"Wikidata {w['qid']} ({w.get('name')})"
    if inb(c.get("lat"), c.get("lon")):
        return round(c["lat"], 6), round(c["lon"], 6), f"CartoCiudad (IGN) portal: {c.get('matched')}"
    r = c.get("retry") or {}
    if inb(r.get("lat"), r.get("lon")):
        return round(r["lat"], 6), round(r["lon"], 6), f"CartoCiudad (IGN) portal: {r.get('matched')}"
    return None


cc = json.loads((IS / "mekan" / "koordinat_cartociudad.json").read_text(encoding="utf-8"))
coords = {}
for c in cc:
    p = pick(c)
    if p:
        coords[c["entry_id"]] = p
log = IS / "denetim" / "duzeltme_L0_degisiklik.jsonl"
changes, applied_coord, applied_coll, no_coord = [], [], [], []
for path in sorted(glob.glob(str(IS / "data" / "parcalar" / "Mekânlar.*.jsonl"))):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    changed = False
    for r in rows:
        eid = r["entry_id"]
        slug = eid.split(":")[1]
        if r.get("latitude") in (None, ""):
            if eid in coords:
                la, lo, src = coords[eid]
                changes.append({"entry_id": eid, "alan": "latitude/longitude", "eski": "", "yeni": f"{la},{lo}", "bulgu_claim_id": "L0:ISS-006",
                                "gerekce": f"Bağımsız L0 denetimi ISS-006: koordinat boştu; kaynak {src}; kart adresi: {r.get('location')}", "alinti": ""})
                r["latitude"], r["longitude"] = la, lo
                applied_coord.append(eid)
                changed = True
            else:
                no_coord.append(eid)
        if slug in COLLECTION_HAYIR and r.get("collection") == "Evet":
            changes.append({"entry_id": eid, "alan": "collection", "eski": "Evet", "yeni": "Hayır", "bulgu_claim_id": "L0:ISS-007",
                            "gerekce": "Bağımsız L0 denetimi ISS-007 / K108: bağımsız adresli, kendi giriş ve saatleri olan müze/tesis; collection etiketi alt nesne için ayrılmıştır.", "alinti": ""})
            r["collection"] = "Hayır"
            applied_coll.append(eid)
            changed = True
    if changed and not DRY:
        with Path(path).open("w", encoding="utf-8", newline="\n") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
if not DRY and changes:
    with log.open("a", encoding="utf-8", newline="\n") as f:
        for ch in changes:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")
print(json.dumps({"dry": DRY, "koordinat_yazildi": len(applied_coord), "koordinatsiz_kalan": no_coord, "collection_hayir": len(applied_coll), "degisiklik": len(changes)}, ensure_ascii=False))
