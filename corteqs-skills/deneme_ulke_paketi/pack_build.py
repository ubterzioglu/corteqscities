"""Yazar ciktisindan ulke paketini kurar (ROOT\\ulke\\<ISO>): kartlar, claim'ler, baglantilar, kullanilan kaynaklar, pack.json.

Kullanim: pack_build.py <ES klasoru> --country ES --version 1 [--built YYYY-AA-GG]
Girdi: <ES>\\_is\\yazar\\out\\<konu>\\ (Yanıtlar/Bağlantılar/claims/valid_until.json), <ES>\\_is\\kaynak_dizini.jsonl.
Cikti (her kosuda bastan yazilir; _is'e dokunulmaz): Yanıtlar.ulusal.jsonl, Bağlantılar.ulusal.jsonl, claims\\ulusal.jsonl,
kaynak_dizini.jsonl + kaynaklar\\ (yalniz kartlarda kullanilan kaynaklarin metin ve html kopyasi), pack.json.
pack.json cards[slug] = {sha256 (country_apply.card_hash), valid_until, topic}.
Cikis 0 tamam / 2 hata (kayip kaynak, tekrarlanan slug).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import country_apply as ca  # noqa: E402

TOPICS = ("oturum", "resmi", "para", "is", "fatura")


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def write(path: Path, items: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8", newline="\n")


def build(es: Path, country: str, version: int, built: str) -> dict:
    work = es / "_is"
    out = work / "yazar" / "out"
    index = {r["source_id"]: r for r in rows(work / "kaynak_dizini.jsonl")}
    cards, actions, claims, valid = [], [], [], {}
    for topic in TOPICS:
        cards += rows(out / topic / f"Yanıtlar.{topic}.jsonl")
        actions += rows(out / topic / f"Bağlantılar.{topic}.jsonl")
        claims += rows(out / topic / f"claims.{topic}.jsonl")
        valid.update(json.loads((out / topic / "valid_until.json").read_text(encoding="utf-8")))
    slugs = [c["slug"] for c in cards]
    if len(set(slugs)) != len(slugs):
        raise ca.UsageError("tekrarlanan slug")
    used = sorted({s for c in cards for s in str(c["source_ids"]).split(";") if s})
    missing = [s for s in used if s not in index]
    if missing:
        raise ca.UsageError(f"dizinde olmayan kaynak: {missing}")
    for stale in ("kaynaklar", "claims"):
        shutil.rmtree(es / stale, ignore_errors=True)
    pack_sources = []
    for sid in used:
        row, name = index[sid], sid.replace(":", "_")
        text_src = Path(row["text_file"])
        html_src = work / row["html_file"]
        for src, ext in ((text_src, ".txt"), (html_src, ".html")):
            if not src.is_file():
                raise ca.UsageError(f"kopya yok: {src}")
        (es / "kaynaklar").mkdir(exist_ok=True)
        shutil.copyfile(text_src, es / "kaynaklar" / f"{name}.txt")
        shutil.copyfile(html_src, es / "kaynaklar" / f"{name}.html")
        pack_sources.append({**{k: row.get(k) for k in ("source_id", "topic", "url", "final_url", "title", "publisher",
                                                        "lang", "text_chars", "html_sha256", "why")},
                             "checked_on": built, "text_file": f"kaynaklar/{name}.txt",
                             "html_file": f"kaynaklar/{name}.html"})
    by_entry: dict[str, list[dict]] = {}
    for claim in claims:
        by_entry.setdefault(claim["entry_id"], []).append(claim)
    meta_cards = {c["slug"]: {"sha256": ca.card_hash(c, by_entry.get(c["entry_id"], [])),
                              "valid_until": valid.get(c["slug"]), "topic": ca.topic_slug(c["topic_id"])}
                  for c in cards}
    write(es / ca.CARDS_FILE, cards)
    write(es / ca.ACTIONS_FILE, actions)
    write(es / ca.CLAIMS_FILE, claims)
    write(es / "kaynak_dizini.jsonl", pack_sources)
    meta = {"country": country, "version": version, "built": built, "cards": meta_cards}
    (es / ca.PACK_FILE).write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"cards": len(cards), "claims": len(claims), "actions": len(actions), "sources": len(pack_sources),
            "dated_cards": sum(1 for v in meta_cards.values() if v["valid_until"])}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Yazar ciktisindan ulke paketini kurar")
    parser.add_argument("es", type=Path)
    parser.add_argument("--country", required=True)
    parser.add_argument("--version", type=int, required=True)
    parser.add_argument("--built", default=dt.date.today().isoformat())
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.es, args.country, args.version, args.built), ensure_ascii=False))
    except (ca.UsageError, OSError, KeyError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
