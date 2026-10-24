r"""audit_prep.py: city-audit fotograf adiminin hazirligi (paket salt okunur; yazma yalniz OUT altina).

Eskiden city-audit SKILL.md'de gomulu iki Python yardimcisiydi ($hazirla, $ciftler); cikti ayni.

Kullanim (OUT = denetim klasoru, PKG = paket koku):
  audit_prep.py hazirla <OUT> <PKG>
      Girdi: OUT\_dump\*.jsonl (xlsx_dump --out-dir), OUT\dosya-envanteri.json (inventory --out),
             PKG\Teslimler\*.json|csv|html (yalniz okunur).
      Cikti: OUT\_foto\kanit\Lisans kanıtları\NNNN.source-evidence.json: Kanitlar.source_evidence_json ->
               original_api_record, photo_candidates from-evidence bicimi (Excel kopyasi yanina SKILL.md'de konur);
             OUT\_foto\items.jsonl: contact_sheet girdisi, teslim edilen her kare (key, path, label, group,
               excel_row, role);
             OUT\_foto\hazirlik.json (ayrinti):
               ters_egik_cizgi  yol basina 'kotu/taranan' (K84): Excel'de 'file' ve '*_file' sutunlari, Teslimler'deki
                                JSON/CSV'de paket koku klasorleriyle baslayan degerler, HTML'de goreli src/href ('\'
                                ya da %5C); okunamayan dosya 'okunamadı: ...'
               kanit_dosyasi    yazilan kanit dosyasi sayisi (Kanitlar satir sayisina esit olmali)
               kanitsiz_foto    photo_id -> neden (JSON değil, JSON nesnesi değil, UzunAlanlar'da (çözülmedi),
                                original_api_record yok)
               ayni_sha         envanterin dup_sha gruplari: kapak_mekan (zararsiz), K05 (Fotoğraflar/ disinda ya da
                                hicbir satira bagli degil), K63 (iki mekan ya da iki kapak karesi ayni dosya)
               eksik_alanli_foto  yalniz varsa: photo_id ya da file'i olmayan Fotoğraflar satirlari [{excel_row, eksik}];
                                paket kusuru (bulgu), girdi hatasi degil; satir paftaya (items.jsonl) girmez
      OUT\_foto\kanit ve OUT\temas-sayfalari her kosuda bastan kurulur (eski kanit, Excel kopyasi, pafta kalmaz; salt
      okunur dosya da silinir, kilitli dosya varsa cikis 2).
      Girdiler silmeden once okunur: girdi hatasinda hicbir sey silinmez.
  audit_prep.py ciftler <OUT>
      Girdi: OUT\temas-sayfalari\dhash.json (contact_sheet), OUT\_dump\Fotoğraflar.jsonl.
      Cikti: OUT\_foto\dhash-ciftleri.json: dhash_cift, kapak_mekan (ayni bayttaki kapak<->mekan ciftleri),
             K63_aday (kalan ciftler; karar L1'de foto ajaninin).
stdout tek satir JSON (hazirla: sayilar + 'ayrinti' yolu; ciftler: dosyanin aynisi; hata: {"error": ...}).
Cikis: 0 bulgu yok / 1 bulgu adayi var (karar degil, ayrinti dosyada) / 2 kullanim, girdi ya da yazma hatasi
(eski klasor silinemedi dahil).
PKG'ye yazilmaz: OUT paketin icinde olamaz; PKG, silinen ya da yazilan klasorlerin (OUT\_foto, OUT\temas-sayfalari)
icinde olamaz.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import stat
import sys
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8
from photo_candidates import EVIDENCE_DIR as EVIDENCE_SUBDIR, EVIDENCE_GLOB

DUMP_DIR, PREP_DIR, SHEETS_DIR, EVIDENCE_DIR = "_dump", "_foto", "temas-sayfalari", "kanit"
INVENTORY_NAME, DHASH_NAME = "dosya-envanteri.json", "dhash.json"
ITEMS_NAME, DETAIL_NAME, PAIRS_NAME = "items.jsonl", "hazirlik.json", "dhash-ciftleri.json"
EVIDENCE_SUFFIX = EVIDENCE_GLOB.lstrip("*")  # '.source-evidence.json'
PHOTO_SHEET, EVIDENCE_SHEET, PLACE_SHEETS = "Fotoğraflar", "Kanıtlar", ("Mekânlar", "Mahalleler")
REQUIRED_SHEETS = (EVIDENCE_SHEET, PHOTO_SHEET, *PLACE_SHEETS)
PHOTO_FIELDS = ("photo_id", "file")  # items.jsonl'de karenin anahtari ve dosyasi
PACKAGE_ROOTS = ("Teslimler", "Fotoğraflar", "Lisans kanıtları")  # paket kokunden goreli yol baslari
PHOTO_PREFIX = "Fotoğraflar/"
DELIVERY_TYPES = (".json", ".csv", ".html")
COVER, VENUE = "Kapak", "Mekân"
LINK = re.compile(r"""\b(?:src|href)\s*=\s*["']([^"']*)["']""", re.I)
SCHEME = re.compile(r"[a-z][a-z0-9+.-]*:", re.I)  # mutlak adres (https:, mailto:, data:): paket yolu degil


class PrepError(Exception):
    """Kullanim ya da girdi hatasi (cikis 2)."""


# ------------------------------------------------------------------ okuma

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Satir basina bir JSON nesnesi. Dosya nesnesi yalniz '\\n'de boler (str.splitlines U+2028'de de bolerdi)."""
    rows = []
    try:
        with open(path, encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, start=1):
                if line.strip():
                    rows.append(json_object(line, f"{path.name} satir {number}"))
    except OSError as exc:
        raise PrepError(f"okunamadi: {path} ({exc.strerror or exc})") from exc
    except UnicodeDecodeError as exc:
        raise PrepError(f"{path.name}: UTF-8 degil ({exc})") from exc
    return rows


def json_object(text: str, where: str) -> dict[str, Any]:
    try:
        value = json.loads(text)
    except ValueError as exc:
        raise PrepError(f"{where}: JSON degil ({exc})") from exc
    if not isinstance(value, dict):
        raise PrepError(f"{where}: JSON nesnesi degil")
    return value


def load_dump(out: Path) -> dict[str, list[dict[str, Any]]]:
    """xlsx_dump ciktisi: sayfa adi -> kayitlar (glob sirasi = eski yardimcinin tarama sirasi)."""
    dump = out / DUMP_DIR
    sheets = {path.stem: path for path in sorted(dump.glob("*.jsonl"))}
    missing = [f"{name}.jsonl" for name in REQUIRED_SHEETS if name not in sheets]
    if missing:
        raise PrepError(f"xlsx_dump ciktisi eksik ({dump}): {', '.join(missing)}; once xlsx_dump --out-dir calismali")
    return {name: read_jsonl(path) for name, path in sheets.items()}


def load_duplicates(out: Path) -> list[dict[str, Any]]:
    """inventory raporundaki findings.dup_sha gruplari ({sha256, files: [paket yolu, ...]})."""
    path = out / INVENTORY_NAME
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PrepError(f"envanter okunamadi: {path} ({exc.strerror or exc}); once inventory --out calismali") from exc
    except ValueError as exc:
        raise PrepError(f"envanter JSON degil: {path} ({exc})") from exc
    findings = report.get("findings") if isinstance(report, dict) else None
    groups = findings.get("dup_sha") if isinstance(findings, dict) else None
    valid = isinstance(groups, list) and all(
        isinstance(g, dict) and isinstance(g.get("files"), list) and all(isinstance(p, str) for p in g["files"])
        for g in groups)
    if not valid:
        raise PrepError(f"envanterde findings.dup_sha listesi yok ya da bicimi bozuk: {path}")
    return groups


def is_complete(photo: dict[str, Any]) -> bool:
    return all(field in photo for field in PHOTO_FIELDS)


def incomplete_photos(photos: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """photo_id ya da file'i olmayan Fotoğraflar satirlari (xlsx_dump bos hucreyi yazmaz). Paket kusurudur, girdi hatasi
    degil: satir paftaya girmez; dosyasi varsa ayni SHA eslemesinde kalir (dosya bir satira bagli, artik degil)."""
    return [{"excel_row": row.get("_row"), "eksik": [field for field in PHOTO_FIELDS if field not in row]}
            for row in photos if not is_complete(row)]


def check_locations(out: Path, package: Path) -> None:
    """Paket salt okunur: OUT paketin icinde olamaz; paket silinen/yazilan klasorlerin icinde olamaz."""
    if not package.is_dir():
        raise PrepError(f"paket klasoru yok: {package}")
    out_real, package_real = out.resolve(), package.resolve()
    if out_real == package_real or package_real in out_real.parents:
        raise PrepError(f"OUT paketin icinde: {out} (denetim pakete yazmaz; OUT paket disinda olmali)")
    for folder in (out / PREP_DIR, out / SHEETS_DIR):
        real = folder.resolve()
        if package_real == real or real in package_real.parents:
            raise PrepError(f"paket, audit_prep'in sildigi/yazdigi klasorun icinde: {package} ({folder})")


# ------------------------------------------------------------------ yol taramasi (K84)

def strings(value: Any) -> Iterator[str]:
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, str):
        yield value


def ratio(values: Iterable[str], bad: Callable[[str], bool]) -> str:
    """'kotu/taranan' yol sayisi."""
    values = list(values)
    return f"{sum(map(bad, values))}/{len(values)}"


def has_backslash(value: str) -> bool:
    """Paket yolunda '\\': Windows'ta araclar kabul eder, Linux'ta dosya bulunamaz."""
    return "\\" in value


def excel_path_scan(sheets: dict[str, list[dict[str, Any]]]) -> dict[str, str]:
    """Excel: 'file' ve adi '_file' ile biten her sutun."""
    found = {}
    for sheet, records in sheets.items():
        for column in sorted({key for row in records for key in row if key == "file" or key.endswith("_file")}):
            found[f"{sheet}.{column}"] = ratio([str(row[column]) for row in records if column in row], has_backslash)
    return found


def delivery_path_scan(package: Path) -> dict[str, str]:
    """Teslimler'deki dogrudan JSON/CSV/HTML dosyalari (alt klasorler taranmaz)."""
    found = {}
    for path in sorted(p for p in (package / "Teslimler").glob("*") if p.is_file()):
        kind = path.suffix.lower()
        if kind in DELIVERY_TYPES:
            found[f"Teslimler/{path.name}"] = scan_delivery_file(path, kind)
    return found


def scan_delivery_file(path: Path, kind: str) -> str:
    try:
        text = path.read_text(encoding="utf-8-sig")
        if kind == ".html":  # goreli src/href; '\' adreste %5C olur
            links = [url for url in LINK.findall(text) if not SCHEME.match(url)]
            return ratio(links, lambda url: "\\" in url or "%5c" in url.lower())
        values = strings(json.loads(text)) if kind == ".json" else (
            cell for row in csv.reader(text.splitlines()) for cell in row)
        return ratio([value for value in values if value.startswith(PACKAGE_ROOTS)], has_backslash)
    except (OSError, ValueError, csv.Error) as exc:
        return f"okunamadı: {exc}"


# ------------------------------------------------------------------ kanit, kareler, ayni SHA

def api_record(text: Any) -> tuple[dict[str, Any] | None, str]:
    """Kanitlar.source_evidence_json -> (Commons kaydi, '') ya da (None, neden)."""
    try:
        value = json.loads(text or "{}")
    except (TypeError, ValueError):
        return None, "JSON değil"
    if not isinstance(value, dict):
        return None, "JSON nesnesi değil"
    if "corteqs_long_value" in value:
        return None, "UzunAlanlar'da (çözülmedi)"
    api = value.get("original_api_record")
    return (api, "") if isinstance(api, dict) and api else (None, "original_api_record yok")


def write_evidence(folder: Path, rows: list[dict[str, Any]]) -> tuple[int, dict[str, str]]:
    """Kanitlar -> from-evidence bicimi ({photo_id, api_imageinfo}). Doner: (yazilan, kanitsiz photo_id -> neden)."""
    written, missing = 0, {}
    for row in rows:
        api, reason = api_record(row.get("source_evidence_json"))
        if api is None:
            missing[str(row.get("photo_id"))] = reason
            continue
        written += 1
        (folder / f"{written:04d}{EVIDENCE_SUFFIX}").write_text(
            json.dumps({"photo_id": row.get("photo_id"), "api_imageinfo": api}, ensure_ascii=False), encoding="utf-8")
    return written, missing


def photo_items(photos: list[dict[str, Any]], sheets: dict[str, list[dict[str, Any]]],
                package: Path) -> list[dict[str, Any]]:
    """contact_sheet girdisi: teslim edilen her kare (photo_id ve file'i olan satir); etiket = mekan/mahalle adi
    (kapakta 'Kapak') + dosya adi."""
    names = {row["entry_id"]: row.get("title") or row["entry_id"]
             for sheet in PLACE_SHEETS for row in sheets[sheet] if "entry_id" in row}
    items = []
    for photo in filter(is_complete, photos):
        rel = str(photo["file"]).replace("\\", "/")
        place = names.get(photo.get("entry_id")) or (
            COVER if photo.get("role") == COVER else photo.get("entry_id") or "?")
        items.append({"key": photo["photo_id"], "path": str(package / rel), "label": f"{place} · {Path(rel).name}",
                      "group": photo.get("entry_id"), "excel_row": photo.get("_row"), "role": photo.get("role")})
    return items


def classify_duplicates(groups: list[dict[str, Any]], photos: list[dict[str, Any]]) -> dict[str, list[list[str]]]:
    """Ayni SHA'li dosya gruplari: kapak_mekan (zararsiz), K05 (artik/fazla kopya), K63 (gercek tekrar)."""
    roles: dict[str, set[Any]] = {}
    for photo in photos:
        roles.setdefault(str(photo.get("file") or "").replace("\\", "/"), set()).add(photo.get("role"))
    found: dict[str, list[list[str]]] = {"kapak_mekan": [], "K05": [], "K63": []}
    for group in groups:
        paths = group["files"]
        if any(path not in roles or not path.startswith(PHOTO_PREFIX) for path in paths):
            found["K05"].append(paths)  # pilot: Teslimler/.download-cache artigi
        elif sorted("+".join(sorted(map(str, roles[path]))) for path in paths) == [COVER, VENUE]:
            found["kapak_mekan"].append(paths)  # ayni kare iki rolde; tekil sayimda bir kez
        else:
            found["K63"].append(paths)  # iki mekan karesi (ya da iki kapak) ayni dosya
    return found


def retry_writable(function: Callable[[str], object], path: str, error: BaseException) -> None:
    """rmtree hata cagrisi: izin hatasinda salt okunur ozniteligini (Copy-Item korur) kaldirip bir kez daha dener.
    Baska hata ya da yine silinemeyen (kilitli) dosya yukari firlar."""
    if not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IWRITE)
    function(path)


def clear_previous(out: Path) -> None:
    """Ayni klasorde ikinci kosu: eski kanit, Excel kopyasi (photo_candidates ilk xlsx'i alir) ve pafta kalmasin."""
    for folder in (out / PREP_DIR / EVIDENCE_DIR, out / SHEETS_DIR):
        if folder.exists():
            try:
                shutil.rmtree(folder, onexc=retry_writable)
            except OSError as exc:
                raise PrepError(f"eski klasor silinemedi: {folder} ({exc}); icinde kilitli ya da salt okunur dosya var "
                                "(ornegin Excel'de acik): kapatip yeniden calistir") from exc


def has_findings(scan: dict[str, str], missing: dict[str, str], duplicates: dict[str, list[list[str]]],
                 incomplete: list[dict[str, Any]]) -> bool:
    bad_paths = any(not value.startswith("0/") for value in scan.values())
    return bad_paths or bool(missing) or bool(duplicates["K05"] or duplicates["K63"]) or bool(incomplete)


def prepare(out: Path, package: Path) -> tuple[dict[str, Any], bool]:
    """hazirla: once butun girdiler okunur ve dogrulanir, sonra eski ciktilar silinip yenileri yazilir."""
    check_locations(out, package)
    sheets = load_dump(out)
    photos = sheets[PHOTO_SHEET]
    incomplete = incomplete_photos(photos)
    groups = load_duplicates(out)
    scan = {**excel_path_scan(sheets), **delivery_path_scan(package)}
    items = photo_items(photos, sheets, package)
    clear_previous(out)
    prep = out / PREP_DIR
    evidence = prep / EVIDENCE_DIR / EVIDENCE_SUBDIR
    evidence.mkdir(parents=True)
    written, missing = write_evidence(evidence, sheets[EVIDENCE_SHEET])
    with open(prep / ITEMS_NAME, "w", encoding="utf-8") as stream:
        stream.writelines(json.dumps(item, ensure_ascii=False) + "\n" for item in items)
    duplicates = classify_duplicates(groups, photos)
    flagged = {"eksik_alanli_foto": incomplete} if incomplete else {}  # yalniz varsa: diger ciktilar eskisiyle ayni
    result = {"ters_egik_cizgi": scan, "kanit_dosyasi": written, "kanitsiz_foto": missing, "ayni_sha": duplicates,
              **flagged}
    detail = prep / DETAIL_NAME
    detail.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    summary = {**result, "kanitsiz_foto": len(missing), "ayni_sha": {k: len(v) for k, v in duplicates.items()},
               **{key: len(rows) for key, rows in flagged.items()}, "ayrinti": str(detail)}
    return summary, has_findings(scan, missing, duplicates, incomplete)


# ------------------------------------------------------------------ dHash ciftleri (K63)

def load_pairs(path: Path) -> list[dict[str, Any]]:
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PrepError(f"okunamadi: {path} ({exc.strerror or exc}); once contact_sheet calismali") from exc
    except ValueError as exc:
        raise PrepError(f"{path.name} JSON degil: {path} ({exc})") from exc
    pairs = report.get("pairs") if isinstance(report, dict) else None
    scalar = (str, int, float, bool, type(None))
    if not isinstance(pairs, list) or not all(
            isinstance(p, dict) and isinstance(p.get("a", []), scalar) and isinstance(p.get("b", []), scalar)
            for p in pairs):
        raise PrepError(f"{path} icinde 'pairs' listesi yok ya da ogeler a/b tasimiyor")
    return pairs


def same_cover_venue(pair: dict[str, Any], photos: dict[Any, dict[str, Any]]) -> bool:
    """Kapak ile mekan karesi ayni bayt: zararsiz (rol ayri, tekil sayimda bir kez)."""
    a, b = photos.get(pair["a"], {}), photos.get(pair["b"], {})
    return {a.get("role"), b.get("role")} == {COVER, VENUE} and bool(a.get("sha256")) and a.get("sha256") == b.get(
        "sha256")


def dhash_pairs(out: Path) -> tuple[dict[str, Any], bool]:
    """ciftler: dhash.json ciftlerinden ayni bayttaki kapak-mekan ciftleri dusulur, kalanlar K63_aday."""
    photos = {row.get("photo_id"): row for row in read_jsonl(out / DUMP_DIR / f"{PHOTO_SHEET}.jsonl")}
    pairs = load_pairs(out / SHEETS_DIR / DHASH_NAME)
    candidates = [pair for pair in pairs if not same_cover_venue(pair, photos)]
    result = {"dhash_cift": len(pairs), "kapak_mekan": len(pairs) - len(candidates), "K63_aday": candidates}
    target = out / PREP_DIR / PAIRS_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    return result, bool(candidates)


# ------------------------------------------------------------------ komut satiri

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="city-audit fotograf hazirligi (paket salt okunur; yazma OUT altina).")
    sub = parser.add_subparsers(dest="command", required=True)
    prep = sub.add_parser("hazirla", help="kanit dosyalari, items.jsonl, yol taramasi (K84), ayni SHA (K05/K63)")
    prep.add_argument("out", type=Path, help=r"denetim klasoru (OUT): _dump\ ve dosya-envanteri.json burada")
    prep.add_argument("package_root", type=Path, help="paket koku (PKG), yalniz okunur")
    pairs = sub.add_parser("ciftler", help=r"temas-sayfalari\dhash.json ciftleri -> _foto\dhash-ciftleri.json (K63)")
    pairs.add_argument("out", type=Path, help="denetim klasoru (OUT)")
    return parser


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    args = build_parser().parse_args(argv)
    try:
        if args.command == "hazirla":
            summary, findings = prepare(args.out, args.package_root)
        else:
            summary, findings = dhash_pairs(args.out)
    except PrepError as exc:
        emit({"error": str(exc)})
        return EXIT_USAGE
    except OSError as exc:  # OUT'a yazilamadi (izin, disk, kilitli dosya)
        emit({"error": f"yazilamadi: {exc}"})
        return EXIT_USAGE
    emit(summary)
    return EXIT_FINDINGS if findings else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
