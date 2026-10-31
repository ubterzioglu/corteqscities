r"""Ilk tur denetim 'duzelt' orani, yazim rolune gore (city-pack-hibrit olcumu).

Kullanim:
  duzelt_orani.py <WORK>\_is\denetim [<WORK2>\_is\denetim ...] [--out rapor.json]

Yalniz ilk tur karar dosyalari sayilir: <parca>_karar.jsonl (parca adinda '-' yok; -ek, -dN turlari yazarin degil
editorun isidir). Parca -> rol: mekan* mekan-yazari, mahalle* mahalle-yazari, sozluk sozluk-yazari, rota rota-yazari,
sayfa sayfa-yazari, kalan konu parcalari yanit-yazari. Karar satiri {entry_id, karar: temiz|duzelt, ...}.
Salt okunur. stdout tek satir JSON: {"<klasor>": {"<rol>": {"kart": n, "duzelt": m, "oran": yuzde}}}.
Cikis: 0 / 2 kullanim hatasi ya da okunamayan dosya.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROL_ONEKLERI = (("mekan", "mekan-yazari"), ("mahalle", "mahalle-yazari"), ("sozluk", "sozluk-yazari"),
                ("rota", "rota-yazari"), ("sayfa", "sayfa-yazari"))


def rol(parca: str) -> str:
    return next((r for onek, r in ROL_ONEKLERI if parca.startswith(onek)), "yanit-yazari")


def klasor_say(klasor: Path) -> dict[str, dict[str, float]]:
    kart: Counter[str] = Counter()
    duzelt: Counter[str] = Counter()
    for dosya in sorted(klasor.glob("*_karar.jsonl")):
        parca = dosya.name[: -len("_karar.jsonl")]
        if "-" in parca:
            continue
        for satir in dosya.read_text(encoding="utf-8-sig").splitlines():
            if not satir.strip():
                continue
            karar = json.loads(satir).get("karar")
            kart[rol(parca)] += 1
            duzelt[rol(parca)] += karar == "duzelt" or karar == "düzelt"
    return {r: {"kart": kart[r], "duzelt": duzelt[r], "oran": round(100 * duzelt[r] / kart[r], 1)}
            for r in sorted(kart)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ilk tur duzelt orani, role gore")
    ap.add_argument("klasorler", nargs="+", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args(argv)
    eksik = [str(k) for k in args.klasorler if not k.is_dir()]
    if eksik:
        print(json.dumps({"hata": f"klasor yok: {eksik}"}, ensure_ascii=False))
        return 2
    try:
        sonuc = {str(k): klasor_say(k) for k in args.klasorler}
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({"hata": str(e)}, ensure_ascii=False))
        return 2
    metin = json.dumps(sonuc, ensure_ascii=False)
    if args.out:
        args.out.write_text(metin + "\n", encoding="utf-8")
    print(metin)
    return 0


if __name__ == "__main__":
    sys.exit(main())
