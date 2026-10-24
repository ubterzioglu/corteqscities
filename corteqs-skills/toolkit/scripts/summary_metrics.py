"""Teslim ozeti icin olculen degerleri toplar (Excel + envanter + dogrulayici cikti). Salt okunur, saf hesap."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import openpyxl

import common

HUMAN_APPROVED = {"metadata_review_status": "Doğrulandı", "pixel_review_status": "Doğrulandı", "rights_status": "Bu kare için uygun"}
HUMAN_ALLOWED = {"Bekliyor", "Doğrulandı", "Bu kare için uygun"}
# resmi dogrulayici sayim anahtari -> bizim Berlin anahtarimiz
OFFICIAL_KEYS = {"answers": "answers", "places": "places", "neighborhoods": "districts", "topics": "topics",
                 "photos": "photos", "hero_photos": "covers", "routes": "routes", "glossary": "glossary"}
BERLIN_LABELS = {"answers": "Pratik yanıt", "places": "Gerçek mekân", "districts": "Mahalle/yerel bölge", "topics": "Dolu konu",
                 "photos": "Farklı mekân fotoğrafı", "covers": "Farklı kapak fotoğrafı", "routes": "Rota", "glossary": "Sözlük maddesi"}


def _records(wb, name: str) -> list[dict[str, Any]]:
    return list(common.iter_records(wb[name])) if name in wb.sheetnames else []


def _unique_photos(rows: list[dict[str, Any]]) -> int:
    return len(common.group_unique_photos(
        {"photo_id": r["photo_id"], "sha256": r.get("sha256"), "source_url": r.get("source_url")} for r in rows if r.get("photo_id")))


def _photo_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    venue = [r for r in rows if r.get("role") == "Mekân"]
    cover = [r for r in rows if r.get("role") == "Kapak"]
    return {"rows": len(rows), "venue_rows": len(venue), "cover_rows": len(cover),
            "venue_unique": _unique_photos(venue), "cover_unique": _unique_photos(cover)}


def _coverage(entries: list[dict[str, Any]], photo_entries: set[str]) -> dict[str, Any]:
    ids = [e["entry_id"] for e in entries if e.get("entry_id")]
    missing = [i for i in ids if i not in photo_entries]
    return {"total": len(ids), "with_photo": len(ids) - len(missing), "without_photo": missing}


def _source_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    verified = [r for r in rows if r.get("verified") == "Evet"]
    snap = lambda r: bool(r.get("snapshot_file") and r.get("snapshot_sha256"))  # noqa: E731
    return {"total": len(rows), "verified_yes": len(verified), "with_snapshot": sum(snap(r) for r in rows),
            "verified_without_snapshot": sum(1 for r in verified if not snap(r))}


def _human_metrics(rows: list[dict[str, Any]]) -> dict[str, int]:
    pending = invalid = 0
    for row in rows:
        for key, approved in HUMAN_APPROVED.items():
            value = row.get(key)
            if value is not None and value not in HUMAN_ALLOWED:
                invalid += 1
            elif value != approved:
                pending += 1
    return {"rows": len(rows), "pending_fields": pending, "invalid_values": invalid}


def _berlin_rows(raw: dict[str, int], photos: dict[str, int], validation: dict[str, Any] | None) -> list[dict[str, Any]]:
    official = ((validation or {}).get("structure") or {}).get("counts")
    actual = {"answers": raw["answers"], "places": raw["places"], "districts": raw["districts"], "topics": raw["topics"],
              "photos": photos["venue_unique"], "covers": photos["cover_unique"], "routes": raw["routes"], "glossary": raw["glossary"]}
    source = "ham (Excel)"
    if official:
        actual = {ours: official.get(theirs, actual[ours]) for theirs, ours in OFFICIAL_KEYS.items()}
        source = "resmî doğrulayıcı sayımı"
    rows = []
    for key, label in BERLIN_LABELS.items():
        n, low, high = actual[key], common.BERLIN_MIN[key], common.BERLIN_TARGET[key]
        status = "hedef karşılandı" if n >= high else ("hedefin altında (alt sınırın üstünde)" if n >= low else "alt sınırın altında")
        rows.append({"key": key, "label": label, "actual": n, "minimum": low, "target": high, "status": status, "source": source})
    return rows


def collect(xlsx: Path, inventory: dict[str, Any] | None, validation: dict[str, Any] | None) -> dict[str, Any]:
    """Tum olcumleri tek sozlukte toplar; olculmeyen girdi None olarak kalir (uydurma sayi yok)."""
    xlsx = Path(xlsx)
    wb = openpyxl.load_workbook(xlsx)
    sheets = {n: _records(wb, n) for n in common.DATA_SHEETS}
    raw = {"answers": len(sheets["Yanıtlar"]), "places": len(sheets["Mekânlar"]), "districts": len(sheets["Mahalleler"]),
           "topics": len(sheets["Konular"]), "routes": len(sheets["Rotalar"]), "glossary": len(sheets["Sözlük"])}
    photos = _photo_metrics(sheets["Fotoğraflar"])
    photo_entries = {r["entry_id"] for r in sheets["Fotoğraflar"] if r.get("entry_id")}
    city = (sheets["Şehir"] or [{}])[0]
    delivery = (sheets["Teslimat"] or [{}])[0]
    code = re.search(r"CITY-\d+", str(delivery.get("delivery_id", "")) + " " + xlsx.name)
    version = re.search(r"_(v\d+)", xlsx.stem)
    return {
        "xlsx_name": xlsx.name, "version": version.group(1) if version else "bilinmiyor",
        "city_id": city.get("city_id") or delivery.get("city_id") or "bilinmiyor", "city_name": city.get("name", "bilinmiyor"),
        "city_code": code.group(0) if code else "bilinmiyor", "editor": delivery.get("editor", "bilinmiyor"),
        "row_counts": {n: len(r) for n, r in sheets.items()}, "photos": photos,
        "places": _coverage(sheets["Mekânlar"], photo_entries), "districts": _coverage(sheets["Mahalleler"], photo_entries),
        "sources": _source_metrics(sheets["Kaynaklar"]), "human": _human_metrics(sheets["Kanıtlar"]),
        "berlin": _berlin_rows(raw, photos, validation), "inventory": inventory, "validation": validation,
    }
