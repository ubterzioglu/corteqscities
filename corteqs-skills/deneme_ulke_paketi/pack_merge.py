"""Ulke paketi ile bolge paket(ler)ini sehre tek seferde uygulanacak birlesik pakete toplar.

Kullanim: pack_merge.py --pack <ROOT>\\ulke\\ES --pack <ROOT>\\ulke\\ES\\bolge\\andalucia --out <birlesik klasor>
Neden: country_apply bir is klasorune tek paket uygular (kayit dosyasi ve konu dosyalari ikinci kosuda zaten var), ve
merge_package her konu icin tek parca dosyasi bekler. Bolge kartlari ulusal kartlarla ayni konu dosyasina girmeli.
Kurallar: her paketin kartlari kendi pack.json hash'iyle dogrulanir (country_apply.check_pack_cards); slug ve source_id
paketler arasinda tekrarlanamaz; ulke kodu ayni olmali. Kaynak kopyalari <out>\\kaynaklar\\ altina alinir.
Cikti (her kosuda bastan yazilir): pack.json {country, version (ilk paket), built, parts: [{path, version, region}],
cards}, Yanıtlar.ulusal.jsonl, Bağlantılar.ulusal.jsonl, claims\\ulusal.jsonl, kaynak_dizini.jsonl, kaynaklar\\.
Cikis 0 tamam / 2 hata.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import country_apply as ca  # noqa: E402


def write(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8", newline="\n")


def merge(packs: list[Path], out: Path) -> dict[str, Any]:
    if len(packs) < 2:
        raise ca.UsageError("en az iki paket gerekli (ulke + bolge)")
    if any(out.resolve() == p.resolve() for p in packs):
        raise ca.UsageError("cikti klasoru bir girdi paketi olamaz")
    metas = [ca.load_pack_meta(p) for p in packs]
    if len({str(m["country"]) for m in metas}) != 1:
        raise ca.UsageError("paketlerin ulke kodu farkli")
    cards, actions, claims, sources, meta_cards, parts = [], [], [], [], {}, []
    seen_sources: set[str] = set()
    for pack, meta in zip(packs, metas):
        pack_cards = ca.read_jsonl(pack / ca.CARDS_FILE)
        pack_claims = ca.read_optional(pack / ca.CLAIMS_FILE)
        ca.check_pack_cards(pack, meta, pack_cards, ca.group_by_entry(pack_claims))
        for card in pack_cards:
            if card["slug"] in meta_cards:
                raise ca.UsageError(f"tekrarlanan slug: {card['slug']} ({pack})")
            meta_cards[card["slug"]] = meta["cards"][card["slug"]]
        for row in ca.read_jsonl(pack / "kaynak_dizini.jsonl"):
            sid = str(row["source_id"])
            if sid in seen_sources:
                raise ca.UsageError(f"tekrarlanan kaynak kimligi: {sid} ({pack})")
            seen_sources.add(sid)
            sources.append((pack, row))
        cards += pack_cards
        claims += pack_claims
        actions += ca.read_optional(pack / ca.ACTIONS_FILE)
        parts.append({"path": str(pack), "version": meta.get("version"), "region": meta.get("region")})
    for stale in ("kaynaklar", "claims"):
        shutil.rmtree(out / stale, ignore_errors=True)
    (out / "kaynaklar").mkdir(parents=True, exist_ok=True)
    index = []
    for pack, row in sources:
        copied = dict(row)
        for key in ("text_file", "html_file"):
            src = pack / str(row[key])
            if not src.is_file():
                raise ca.UsageError(f"kopya yok: {src}")
            name = f"{str(row['source_id']).replace(':', '_')}{src.suffix}"
            shutil.copyfile(src, out / "kaynaklar" / name)
            copied[key] = f"kaynaklar/{name}"
        index.append(copied)
    write(out / ca.CARDS_FILE, cards)
    write(out / ca.ACTIONS_FILE, actions)
    write(out / ca.CLAIMS_FILE, claims)
    write(out / "kaynak_dizini.jsonl", index)
    merged = {"country": metas[0]["country"], "version": metas[0].get("version"),
              "built": max(str(m.get("built", "")) for m in metas), "parts": parts, "cards": meta_cards}
    (out / ca.PACK_FILE).write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"cards": len(cards), "claims": len(claims), "actions": len(actions), "sources": len(index),
            "parts": [{"path": p["path"], "version": p["version"]} for p in parts]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ulke ve bolge paketlerini birlesik pakete toplar")
    parser.add_argument("--pack", type=Path, action="append", required=True, help="once ulke, sonra bolge paketi")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(merge(args.pack, args.out), ensure_ascii=False))
    except (ca.UsageError, OSError, KeyError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
