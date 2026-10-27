"""Tam son denetim (d5) girdileri: parca basina denetim\\<parca>-d5_kartlar.jsonl.

Satir = kaydin parca dosyasindaki hali + 'kaynaklar' (source_id, url, publisher, text_file; kaydin source_ids'i ve
iddialarinin kaynaklari) + 'iddialar' (defter satirlari) + Yanitlarda 'adimlar' ve 'butonlar', rotalarda 'plan' ve
'bacaklar' (rota_plan.jsonl, rota_mesafe.jsonl) ile duraklarin saat/not alanlari.
Kullanim: python -I d5_hazirla.py [--yaz]   (bayraksiz yalniz ozet basar)
          python -I d5_hazirla.py --yaz --tur d6 --parca mekan1 --kayit sevilla:a,sevilla:b
          (yeniden denetim: yalniz verilen kayitlar, denetim\\<parca>-<tur>_kartlar.jsonl; parcanin guncel hali okunur)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PARTS = W / "data" / "parcalar"
RX = re.compile(r"\b(?:sevilla|es):kaynak:\d+\b")
SHEETS = ("Yanıtlar", "Mekânlar", "Mahalleler", "Sözlük", "Rotalar")
OWNER = {"Yanıtlar": "entry_id", "Mekânlar": "entry_id", "Mahalleler": "entry_id", "Sözlük": "term_id", "Rotalar": "route_id"}
ROUND = "d5"


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def _opt(name: str) -> str | None:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv and sys.argv.index(name) + 1 < len(sys.argv) else None


def main(write: bool, tur: str = ROUND, only_part: str | None = None, only_ids: set[str] | None = None) -> int:
    index = {r["source_id"]: r for r in jl(W / "kaynak_dizini.jsonl")}
    claims = defaultdict(list)
    for f in (W / "claims").glob("*.jsonl"):
        for c in jl(f):
            owner = next((c[k] for k in ("entry_id", "term_id", "field_id", "route_id") if c.get(k)), None)
            claims[owner].append({k: c.get(k) for k in ("claim_id", "field", "claim", "value", "unit", "period", "source_id", "quote")})
    steps, buttons = defaultdict(list), defaultdict(list)
    for f in PARTS.glob("Adımlar.*.jsonl"):
        for s in jl(f):
            steps[s.get("entry_id")].append({k: s.get(k) for k in ("step_id", "title", "when", "description")})
    for f in PARTS.glob("Bağlantılar.*.jsonl"):
        for b in jl(f):
            buttons[b.get("entry_id")].append({k: b.get(k) for k in ("action_id", "label", "url")})
    places = {r["entry_id"]: r for f in PARTS.glob("Mekânlar.*.jsonl") for r in jl(f)}
    plan, legs = defaultdict(list), defaultdict(list)
    for r in jl(W / "rota_plan.jsonl"):
        plan[r.get("route_id")].append(r)
    for r in jl(W / "rota_mesafe.jsonl"):
        legs[r.get("route_id")].append(r)

    def sources(row: dict, owner: str) -> list[dict]:
        ids = list(dict.fromkeys(RX.findall(json.dumps(row.get("source_ids", ""), ensure_ascii=False))
                                 + [c["source_id"] for c in claims[owner] if c.get("source_id")]))
        return [{"source_id": s, "url": index.get(s, {}).get("url"), "publisher": index.get(s, {}).get("publisher"),
                 "text_file": index.get(s, {}).get("text_file")} for s in ids]

    summary = []
    for sheet in SHEETS:
        for f in sorted(PARTS.glob(f"{sheet}.*.jsonl")):
            part = f.name.split(".")[1]
            if only_part and part != only_part:
                continue
            out = []
            for row in jl(f):
                owner = row[OWNER[sheet]]
                if only_ids is not None and owner not in only_ids:
                    continue
                item = {**row, "_sekme": sheet, "kaynaklar": sources(row, owner), "iddialar": claims[owner]}
                if sheet == "Yanıtlar":
                    item |= {"adimlar": steps[owner], "butonlar": buttons[owner]}
                if sheet in ("Mekânlar", "Mahalleler"):
                    item["butonlar"] = buttons[owner]
                if sheet == "Rotalar":
                    stops = [s.strip() for s in re.split(r"[\n,;]+", str(row.get("stop_entry_ids") or "")) if s.strip()]
                    item |= {"plan": plan[owner], "bacaklar": legs[owner],
                             "duraklar": [{k: places.get(s, {}).get(k) for k in ("entry_id", "title", "location", "note", "latitude", "longitude")} for s in stops]}
                out.append(item)
            missing_text = sum(1 for i in out for s in i["kaynaklar"] if not s.get("text_file"))
            summary.append({"parca": part, "sekme": sheet, "kayit": len(out), "iddia": sum(len(i["iddialar"]) for i in out),
                            "kaynak": len({s["source_id"] for i in out for s in i["kaynaklar"]}), "metinsiz_kaynak": missing_text})
            if write:
                target = W / "denetim" / f"{part}-{tur}_kartlar.jsonl"
                target.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in out), encoding="utf-8")
    for s in summary:
        print(json.dumps(s, ensure_ascii=False))
    print(json.dumps({"toplam_kayit": sum(s["kayit"] for s in summary), "toplam_iddia": sum(s["iddia"] for s in summary),
                      "yazildi": write}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    ids = _opt("--kayit")
    sys.exit(main("--yaz" in sys.argv, _opt("--tur") or ROUND, _opt("--parca"),
                  {i.strip() for i in ids.split(",") if i.strip()} if ids else None))
