"""Ortak yardimcilar: city-pack / city-audit script'leri bunu paylasir.

Kural: bu modul ag erisimi yapmaz, paket klasorune yazmaz. Excel satir 7 anahtarlarina gore okunur.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Iterator
from urllib.parse import parse_qs, unquote, urlsplit

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

HEADER_ROW = 6
KEY_ROW = 7
FIRST_DATA_ROW = 8

# Berlin alt sinir / uretim hedefi (v7 sozlesmesi)
BERLIN_MIN = {"answers": 212, "places": 92, "districts": 12, "topics": 12, "photos": 187, "covers": 6, "routes": 9, "glossary": 48}
BERLIN_TARGET = {"answers": 240, "places": 120, "districts": 16, "topics": 12, "photos": 250, "covers": 8, "routes": 12, "glossary": 60}
# Bir Excel sayfasinin hangi icerik turunu saydigi
SHEET_FOR_METRIC = {"answers": "Yanıtlar", "places": "Mekânlar", "districts": "Mahalleler", "topics": "Konular", "routes": "Rotalar", "glossary": "Sözlük"}

# Veri sayfalari (Ozet formul sayfasidir; satir 7 anahtari yok)
DATA_SHEETS = (
    "Teslimat", "Şehir", "Konular", "Yanıtlar", "Mekânlar", "Mahalleler", "Bağlantılar", "Rotalar", "Sözlük",
    "Adımlar", "Kaynaklar", "Fotoğraflar", "Kanıtlar", "SayfaAlanları", "EkDetaylar", "FotoğrafKaynakları",
)
# Tek satirlik kimlik sayfalari: satir 8 sablonda onceden dolu gelir
SINGLE_ROW_SHEETS = ("Teslimat", "Şehir")
IDENTITY_KEYS = {
    "Teslimat": ("schema_version", "delivery_id", "city_id"),
    "Şehir": ("city_id", "name", "country", "country_code", "region", "kind", "latitude", "longitude", "aliases"),
}
# AI'in kendi kendine onaylayamayacagi insan inceleme alanlari
HUMAN_REVIEW_KEYS = ("metadata_review_status", "pixel_review_status", "rights_status")
HUMAN_PENDING_VALUE = "Bekliyor"

MAX_CELL_CHARS = 32767


def setup_utf8() -> None:
    """Windows cp1252 konsolunda Turkce karakter hatasini onler."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def safe_relpath(root: Path, relative: str) -> Path:
    """Paket kokunden gocmeyen guvenli yol cozer; mutlak yol ve '..' reddedilir."""
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError("bos yol")
    posix = PurePosixPath(relative.replace("\\", "/"))
    if posix.is_absolute() or ".." in posix.parts or ":" in posix.parts[0]:
        raise ValueError(f"guvensiz yol: {relative}")
    root = Path(root).resolve()
    target = (root / Path(*posix.parts)).resolve()
    if root != target and root not in target.parents:
        raise ValueError(f"yol paket kokunden cikiyor: {relative}")
    return target


def sheet_keys(ws) -> dict[str, int]:
    """Satir 7 teknik anahtarlarini {anahtar: sutun_no} olarak dondurur (sutun no 1 tabanli)."""
    keys: dict[str, int] = {}
    for cell in ws[KEY_ROW]:
        value = cell.value
        if value is None or str(value).strip() == "":
            continue
        key = str(value).strip()
        if key in keys:
            raise ValueError(f"{ws.title}: yinelenen teknik anahtar '{key}' (satir {KEY_ROW})")
        keys[key] = cell.column
    return keys


def is_formula(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("=")


def normalize_value(value: Any) -> Any:
    """Excel degerini JSON'a uygun hale getirir: tarih -> 'YYYY-MM-DD'; tam sayi float -> int."""
    if isinstance(value, _dt.datetime):
        return value.date().isoformat() if value.time() == _dt.time(0, 0) else value.isoformat()
    if isinstance(value, _dt.date):
        return value.isoformat()
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def iter_records(ws, *, include_formulas: bool = False) -> Iterator[dict[str, Any]]:
    """Satir 8'den itibaren dolu kayitlari verir. Her kayit {'_row': n, anahtar: deger}.

    Formul hucreleri varsayilan olarak kayda girmez (sayim/formul sutunlari veri degildir);
    include_formulas=True ise ham formul metniyle girer. Bos hucreler kayda girmez.
    """
    keys = sheet_keys(ws)
    for row in ws.iter_rows(min_row=FIRST_DATA_ROW):
        record: dict[str, Any] = {}
        for key, col in keys.items():
            value = row[col - 1].value if col - 1 < len(row) else None
            if value is None or (isinstance(value, str) and value == ""):
                continue
            if is_formula(value) and not include_formulas:
                continue
            record[key] = normalize_value(value)
        if record:
            record["_row"] = row[0].row
            yield record


def formula_columns(ws) -> set[str]:
    """Veri satirlarinda formul tasiyan teknik anahtarlar (satir 8'e gore)."""
    keys = sheet_keys(ws)
    return {key for key, col in keys.items() if is_formula(ws.cell(FIRST_DATA_ROW, col).value)}


def emit(summary: dict[str, Any]) -> None:
    """Konsola tek satir JSON ozeti yazar (token tasarrufu)."""
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":")))


def write_json(path: Path, payload: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def canonical_source_url(url: str) -> str:
    """Ayni eseri gosteren URL bicimlerini birlestirir (Commons /wiki/File:X ile index.php?title=File:X)."""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return url.strip()
    host = (parts.hostname or "").lower().removeprefix("www.")
    title = parse_qs(parts.query).get("title", [None])[0]
    path = ("/wiki/" + title) if title else unquote(parts.path)
    path = path.replace(" ", "_").rstrip("/")
    return f"{host}{path}"


def group_unique_photos(rows: Iterable[dict[str, Any]]) -> list[list[str]]:
    """Ayni SHA VEYA ayni kanonik kaynak sayfasi uzerinden bagli fotograflari kumeler (K23, union-find).

    rows: {'photo_id', 'sha256' (opsiyonel), 'source_url' (opsiyonel)}. Doner: photo_id listeleri.
    """
    items = list(rows)
    parent = list(range(len(items)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(a: int, b: int) -> None:
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    seen: dict[tuple[str, str], int] = {}
    for idx, row in enumerate(items):
        for kind, value in (("sha", row.get("sha256")), ("src", canonical_source_url(row["source_url"]) if row.get("source_url") else None)):
            if not value:
                continue
            mark = (kind, value)
            if mark in seen:
                union(idx, seen[mark])
            else:
                seen[mark] = idx
    groups: dict[int, list[str]] = {}
    for idx, row in enumerate(items):
        groups.setdefault(find(idx), []).append(row["photo_id"])
    return list(groups.values())
