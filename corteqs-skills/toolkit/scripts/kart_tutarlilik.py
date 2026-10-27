"""Kartlar arasi tutarlilik adaylari: ayni sozluk terimini ya da form/harc kodunu tasiyan kayitlari gruplar.

Sevilla dis denetimi (25.10.2026): kartlar tek tek denetlendi, birbirleriyle karsilastirilmadi. Libro de Familia bir
kartta "verilir", baskasinda "2021'den beri verilmiyor" (S05); okul kayit son tarihi kartlar arasinda farkli (S12);
790-012 harci izin ve kart islemlerinde karisti (S02). Bu arac her grup icin terimin gectigi cumleleri ve o
cumlelerdeki ucret, sure, tarih degerlerini listeler; farkli deger tasiyan grup once gelir. Karar degildir: editor
grubu okur, celiskiyi kaynakla kapatir ya da farkin gerekcesini (farkli islem, farkli donem) karta yazar.

Cikis: 0 farkli degerli grup yok; 1 var (inceleme adayi); 2 girdi hatasi. Excel'i yalniz okur.
"""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

import openpyxl

import common

SHEETS = {"Yanıtlar": "entry_id", "Mekânlar": "entry_id", "Mahalleler": "entry_id", "Sözlük": "term_id",
          "Adımlar": "step_id"}
TEXT_FIELDS = ("term", "title", "subtitle", "summary", "steps", "documents", "cost", "duration", "note", "definition",
               "description")
CODES = (re.compile(r"\b(EX|MI|TA)[- ]?(\d{2})\b"),  # 'EX15', 'EX-17'; buyuk harf: Turkce 'mi 12', 'ta 20' kod degil
         re.compile(r"\b(790)(?:[- ]|\s+(?:kodu|c[oó]digo|code)\s+)(\d{3})\b", re.I),  # '790 kodu 012', 'tasa 790 012'
         re.compile(r"\b(modelo) (?!790\b)(\d{3})\b", re.I))
MONEY = re.compile(r"(?<![\d.,-])((?:[1-9]\d*|0)(?:[.,]\d+)?)\s?(?:€|euro\b)", re.I)  # '012,10 €' kodun parcasi
_MONTHS = "ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik"
DATE = re.compile(rf"\b(\d{{1,2}}) ({_MONTHS})\b")
DURATION = re.compile(r"\b(\d+) (gun|hafta|ay|yil)\b")
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")


def fold(text: Any) -> str:
    lowered = unicodedata.normalize("NFKD", "" if text is None else str(text).lower())
    plain = "".join(ch for ch in lowered if not unicodedata.combining(ch)).replace("ı", "i")
    return " ".join(re.sub(r"[^\w\s-]|_", " ", plain).split())


def code_anchors(text: str) -> list[str]:
    return list(dict.fromkeys(f"{m.group(1).lower()}-{m.group(2)}" if m.group(1).lower() != "modelo"
                              else f"modelo {m.group(2)}" for rx in CODES for m in rx.finditer(text)))


def _money(raw: str) -> str:
    number = raw.replace(".", "").replace(",", "") if re.fullmatch(r"\d{1,3}[.,]\d{3}", raw) else raw.replace(".", ",")
    return f"{number} €"


def facts(text: str) -> dict[str, set[str]]:
    folded = fold(text).replace("-", " ")
    found = {"ucret": {_money(m.group(1)) for m in MONEY.finditer(text)},
             "sure": {f"{m.group(1)} {m.group(2)}" for m in DURATION.finditer(folded)},
             "tarih": {f"{m.group(1)} {m.group(2)}" for m in DATE.finditer(folded)}}
    return {kind: values for kind, values in found.items() if values}


def load(xlsx: Path) -> tuple[list[dict[str, Any]], list[str]]:
    """(kayitlar [{id, sheet, row, term, sentences}], sozluk terimleri)."""
    try:
        wb = openpyxl.load_workbook(xlsx, read_only=False)
    except Exception as exc:  # openpyxl bozuk dosyada farkli hatalar atar
        raise ValueError(f"xlsx okunamadi: {xlsx} ({type(exc).__name__})") from exc
    records, terms = [], []
    try:
        for sheet, key in SHEETS.items():
            if sheet not in wb.sheetnames:
                continue
            for record in common.iter_records(wb[sheet]):
                text = "\n".join(str(record[f]) for f in TEXT_FIELDS if isinstance(record.get(f), str))
                term = fold(str(record.get("term") or "").split("(")[0]) if sheet == "Sözlük" else ""
                terms += [term] if len(term) >= 3 else []
                records.append({"id": str(record.get(key) or ""), "sheet": sheet, "row": record["_row"], "term": term,
                                "sentences": [s.strip() for s in SENTENCE.split(text) if s.strip()]})
    finally:
        wb.close()
    return records, list(dict.fromkeys(terms))


def _mentions(records: list[dict[str, Any]], anchor: str, is_code: bool) -> list[dict[str, Any]]:
    pattern = re.compile(rf"(?<![\w-]){re.escape(anchor)}(?![\w-])")
    found = []
    for record in records:
        hits = [s for s in record["sentences"]
                if (anchor in code_anchors(s) if is_code else pattern.search(fold(s)))]
        if hits or record["term"] == anchor:
            found.append({"id": record["id"], "sheet": record["sheet"], "row": record["row"],
                          "sentences": [s[:200] for s in (hits or record["sentences"])[:3]], "_all": hits})
    return found


def build(xlsx: Path) -> dict[str, Any]:
    records, terms = load(xlsx)
    codes = list(dict.fromkeys(c for r in records for s in r["sentences"] for c in code_anchors(s)))
    groups = []
    for anchor, is_code in [(t, False) for t in terms] + [(c, True) for c in codes]:
        mentions = _mentions(records, anchor, is_code)
        if len({m["id"] for m in mentions}) < 2:
            continue
        values: dict[str, set[str]] = {}
        for mention in mentions:
            for kind, found in facts(" ".join(mention.pop("_all"))).items():
                values.setdefault(kind, set()).update(found)
        differing = sorted(kind for kind, found in values.items() if len(found) > 1)
        groups.append({"anchor": anchor, "kind": "kod" if is_code else "sozluk", "farkli_deger": differing,
                       "values": {kind: sorted(found) for kind, found in sorted(values.items())}, "mentions": mentions})
    groups.sort(key=lambda g: (-len(g["farkli_deger"]), -len(g["mentions"]), g["anchor"]))
    return {"tool": "kart_tutarlilik", "workbook": xlsx.name, "groups": groups,
            "summary": {"groups": len(groups), "farkli_degerli": sum(1 for g in groups if g["farkli_deger"])},
            "not": "Aday listesi; karar degildir. Farkli deger farkli islem ya da donemden de gelebilir."}


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    parser = argparse.ArgumentParser(description="Kartlar arasi tutarlilik adaylari")
    parser.add_argument("xlsx", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if not args.xlsx.is_file():
            raise ValueError(f"xlsx yok: {args.xlsx}")
        report = build(args.xlsx)
    except ValueError as exc:
        common.emit({"tool": "kart_tutarlilik", "error": str(exc)})
        return common.EXIT_USAGE
    common.write_json(args.out, report)
    common.emit({"tool": "kart_tutarlilik", **report["summary"], "out": str(args.out)})
    return common.EXIT_FINDINGS if report["summary"]["farkli_degerli"] else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
