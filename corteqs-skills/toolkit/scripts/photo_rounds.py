"""Foto turlarinin ortak girdi kurali (A12; pilot foto_satirlari.py ve foto_onizleme.py): photo_rows ve photo_previews
aday (candidates.jsonl) ve ham arama (search.jsonl) dosyalarini bu modulle, ayni sirayla okur. Kutuphane; CLI yok.

Varsayilan dosyalar, bu sirayla: ana tur <is>/foto/<ad> (sart: yoksa okuyan script cikis 2 verir), ek tur klasorleri
<is>/foto_*/<ad> (or. foto_ek16; varsa, klasor adina gore) ve cagiranin verdigi ek klasorlerdeki <ad> (photo_previews:
karar dosyasinin klasoru; varsa, listede yoksa). Ek tur bu duzenin disindaysa (or. <is>/foto/ek16/, <is>/ek_tur/)
photo_rows onu bulmaz: o zaman --candidates/--search verilir (verilince tarama kapanir, ana dosya da yazilmali).
Birlestirme: ayni kimlikte onceki dosyanin kaydi kalir (ana tur onde); dosya icinde son satir.
Bozuk JSONL (gecersiz JSON, nesne olmayan satir, UTF-8 olmayan dosya) InputError'dur (ValueError: iki script cikis 2).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable

MAIN_ROUND, EXTRA_ROUNDS = "foto", "foto_*"


class InputError(ValueError):
    """Okunamayan JSONL girdisi; dosya ve satir adiyla (cikis 2)."""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """JSONL nesne satirlari (BOM'lu UTF-8 de okunur); bos satir atlanir."""
    rows = []
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise InputError(f"{path}:{number}: gecersiz JSON ({error.msg})") from error
                if not isinstance(row, dict):
                    raise InputError(f"{path}:{number}: nesne bekleniyor")
                rows.append(row)
    except UnicodeDecodeError as error:
        raise InputError(f"{path}: UTF-8 degil ({error.reason})") from error
    return rows


def _same_file(path: Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def round_files(work: Path, name: str, extra_dirs: Iterable[Path] = ()) -> list[Path]:
    """Varsayilan dosyalar: <is>/foto/<ad> (sart), <is>/foto_*/<ad> (varsa) ve ek klasorlerdeki <ad> (varsa); ayni
    dosya iki kez verilmez."""
    found = [work / MAIN_ROUND / name, *sorted(path for path in work.glob(f"{EXTRA_ROUNDS}/{name}") if path.is_file())]
    known = {_same_file(path) for path in found}
    for folder in extra_dirs:
        path = Path(folder) / name
        if path.is_file() and _same_file(path) not in known:
            found.append(path)
            known.add(_same_file(path))
    return found


def shown(work: Path, path: Path) -> str:
    """Ozetteki dosya adi: is klasorune goreli ('/' ile), disindaysa tam yol."""
    absolute = Path(os.path.abspath(path))
    return absolute.relative_to(work).as_posix() if absolute.is_relative_to(work) else str(absolute)


def load_candidates(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    """candidate_id -> aday: dosyalar verilen sirayla birlesir, ayni kimlikte onceki dosyanin kaydi kalir (ana tur
    onde); dosya icinde son satir."""
    merged: dict[str, dict[str, Any]] = {}
    for path in paths:
        for cid, row in {r.get("candidate_id"): r for r in read_jsonl(path)}.items():
            merged.setdefault(cid, row)
    return merged
