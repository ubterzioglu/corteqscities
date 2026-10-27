"""Son tam denetim sonrasi kapanis listesi: her parcanin SON turunda (en yuksek dN) duzelt karari alan ve ciddi/orta
bulgusu kalan kayitlar + o bulgular. Hafif kalanlar ayrica sayilir (acik konulara gider).
Cikti: WORK\\_is\\d3_arac\\kapanis_listesi.json  {parca: {son_tur, sonraki_tur, kayitlar: [{entry_id, bulgular: [...]}], hafif: [...]}}
Kullanim: python -I kapanis_listesi.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
D = W / "denetim"
ROUND = re.compile(r"^(?P<part>.+)-d(?P<n>\d+)_karar\.jsonl$")
HEAVY = {"ciddi", "orta"}


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if path.is_file() else []


def main() -> int:
    rounds: dict[str, list[int]] = defaultdict(list)
    for p in D.glob("*-d*_karar.jsonl"):
        m = ROUND.match(p.name)
        if m and int(m.group("n")) >= 5:
            rounds[m.group("part")].append(int(m.group("n")))
    out, total_heavy, total_light = {}, 0, 0
    for part, ns in sorted(rounds.items()):
        # kayit basina son karar: en yuksek turdaki satir gecerli
        last_verdict, last_round = {}, {}
        for n in sorted(ns):
            for r in jl(D / f"{part}-d{n}_karar.jsonl"):
                last_verdict[r["entry_id"]], last_round[r["entry_id"]] = r, n
        heavy, light = [], []
        for eid, r in last_verdict.items():
            if r.get("karar") != "düzelt":
                continue
            n = last_round[eid]
            claims = [c for c in jl(D / f"{part}-d{n}_iddia.jsonl") if c.get("entry_id") == eid and c.get("sonuç") != "doğru"]
            place = [m for m in jl(D / f"{part}-d{n}_mekan-dogrulama.jsonl") if m.get("entry_id") == eid and m.get("sonuc") == "kaldı"]
            hv = [c for c in claims if c.get("ağırlık") in HEAVY]
            item = {"entry_id": eid, "tur": f"d{n}", "ozet": (r.get("ozet") or "")[:400],
                    "bulgular": [{k: c.get(k) for k in ("claim_id", "sonuç", "ağırlık", "iddia", "doğrusu")} for c in (hv or claims)],
                    "mekan_kaldi": [{k: m.get(k) for k in ("kimlik", "adres", "koordinat", "ziyaret", "not")} for m in place]}
            if hv or place or r.get("en_agir") in HEAVY:
                heavy.append(item)
            else:
                light.append(item)
        if heavy or light:
            out[part] = {"son_tur": f"d{max(ns)}", "sonraki_tur": f"d{max(ns) + 1}", "kayitlar": heavy, "hafif": light}
            total_heavy += len(heavy)
            total_light += len(light)
    (W / "d3_arac" / "kapanis_listesi.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"parca": len(out), "agir_kayit": total_heavy, "hafif_kayit": total_light,
                      "parca_agir": {p: len(v["kayitlar"]) for p, v in out.items() if v["kayitlar"]}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
