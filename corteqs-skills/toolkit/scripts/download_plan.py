"""Secilen fotograflardan Atinc'in resmi indirme kuyrugu (download_media.py) icin plan uretir. Ag erisimi yok.

Plan: JSON dizisi, her satir {photo_id, original_file, downloaded_file_url}.
original_file = 'Fotoğraflar/<sehir>_<slug>_<NN>.<uzanti>'; uzanti URL yolundan (sorgu/fragment olmadan) alinir.
Izinli adres Atinc'in public_url kuraliyla ayni: https, izinli alan, kimlik bilgisi yok, port yok ya da 443.
Varsayilan izinli alanlar: upload.wikimedia.org, thumb.wikimedia.org. Wikimedia adreslerinde (*.wikimedia.org) sorgu
(2026 ?utm_*) ve #parca atilir; --allow-host ile eklenen baska alanlarda adres aynen kalir (imzali/boyutlu sorgu).
Varsayilan indirilen dosya ORIJINALdir (v7). --prefer-thumb: satirdaki width THUMB_WIDTH'ten buyukse ve thumb_url AYNI
dosyanin (<onek>/thumb/<a>/<ab>/<ad>/<N>px-...) ayni bicimdeki standart Wikimedia thumb'i ise THUMB_WIDTH px kopya
(1600 px = HTTP 400), degilse orijinal. Thumb'li planda resmi kuyruga --allow-host thumb.wikimedia.org verilmeli
(ozet: download_hosts).
original_url'in kendisi upload/thumb.wikimedia.org thumb'i ve genisligi standart disi (STANDARD_WIDTHS disi: 1600 =
HTTP 400) ya da THUMB_WIDTH'ten genisse (sozlesme en cok 1600 px kopya, teslim 1280) o adres plana girmez: ayni
dosyanin ozgun adresine (thumb klasorunun tersi, https://upload.wikimedia.org/<onek>/<a>/<ab>/<ad>) cevrilir, kurallar
ondan uygulanir (--prefer-thumb'da thumb_url kullanilamazsa THUMB_WIDTH px kopya verilen thumb adresinden turetilir);
ozgun adres cikarilamazsa satir reddedilir (hata). Cevrilen satirin ret gerekcesinde verilen adres de yazar. Standart
ve en cok THUMB_WIDTH px thumb aynen kalir.
Ozet sayaclari: thumb_rows (thumb indiren satir), thumb_skipped_missing (bayrak acikken width ya da gereken thumb_url
eksik oldugu icin orijinale dusen satir), original_is_thumb (plana giren original_url'in kendisi olcekli kopya),
original_thumb_fixed (original_url'i ozgun dosya adresine cevrilen satir).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable
from urllib.parse import SplitResult, unquote, urlsplit

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json

DEFAULT_HOSTS = ("upload.wikimedia.org", "thumb.wikimedia.org")
ORIGINAL_HOST = DEFAULT_HOSTS[0]  # ozgun dosyalar burada; olcekli kopyalar 2026'dan beri thumb.wikimedia.org'da
ALLOWED_PORTS = (None, 443)  # Atinc public_url ile ayni
WIKIMEDIA_DOMAIN = "wikimedia.org"
THUMB_DIR = "thumb"
THUMB_WIDTH = 1280  # Wikimedia 2026 standart thumb genisligi (= commons_search.DEFAULT_THUMB_WIDTH; testte sabit)
# Wikimedia 2026 standart thumb genislikleri (mediawiki.org "Common thumbnail sizes", Commons Ocak 2026): dogrudan
# istekte yalniz bunlar verilir, digerleri (or. 1600) HTTP 400
STANDARD_WIDTHS = (20, 40, 60, 120, 250, 330, 500, 960, 1280, 1920, 3840)
THUMB_NAME_RE = re.compile(r"^\d+px-(.+)$")
THUMB_SIZE_RE = re.compile(r"^(?:(?:lossy|lossless)-)?(?:page\d+-)?(\d+)px-")  # sayfali dosya: page1-<N>px-
HASH_DIRS_RE = re.compile(r"[0-9a-f]/[0-9a-f]{2}")  # Commons dosya duzeni: <a>/<ab> (MD5'in ilk bir ve iki hanesi)
TR_MAP = str.maketrans({"ı": "i", "İ": "i", "ş": "s", "Ş": "s", "ğ": "g", "Ğ": "g", "ü": "u", "Ü": "u",
                        "ö": "o", "Ö": "o", "ç": "c", "Ç": "c"})
CITY_RE = re.compile(r"^[a-z0-9-]+$")


def slugify(text: str) -> str:
    ascii_text = text.translate(TR_MAP).lower()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")


def _clean_ext(raw: str) -> str | None:
    ext = raw.lower().lstrip(".")
    ext = "jpg" if ext == "jpeg" else ext
    return ext if ext in {"jpg", "png", "webp"} else None


def extension(url: str) -> str | None:
    """URL YOLUNUN uzantisi (sorgu/fragment haric); gecersizse None."""
    return _clean_ext(PurePosixPath(urlsplit(url).path).suffix)


def _row_ext(row: dict[str, Any]) -> str | None:
    found = extension(row["original_url"])
    if found:
        return found
    if PurePosixPath(urlsplit(row["original_url"]).path).suffix:
        return None  # URL'de baska/bozuk uzanti var: ipucuyla kurtarma yok
    hint = row.get("ext") or PurePosixPath(str(row.get("filename") or "")).suffix
    return _clean_ext(str(hint)) if hint else None


def _row_slug(row: dict[str, Any]) -> str:
    return slugify(str(row.get("slug") or str(row.get("entry_id", "")).rsplit(":", 1)[-1]))


def _split(url: Any) -> SplitResult | None:
    """Adresin parcalari; metin degilse ya da cozulemiyorsa (bozuk IPv6, sayi olmayan/aralik disi port) None."""
    if not isinstance(url, str):
        return None
    try:
        parts = urlsplit(url)
        parts.port  # noqa: B018 -- bozuk port ancak okununca ValueError verir
    except ValueError:
        return None
    return parts


def _allowed(url: Any, allow_hosts: tuple[str, ...]) -> bool:
    """Atinc public_url kurali: https, izinli alan, kimlik bilgisi yok, port yok ya da 443."""
    parts = _split(url)
    return (parts is not None and parts.scheme == "https" and parts.hostname in allow_hosts
            and not parts.username and not parts.password and parts.port in ALLOWED_PORTS)


def _wikimedia_parts(url: Any) -> SplitResult | None:
    """Wikimedia (wikimedia.org ve alt alanlari) adresinin sorgusuz parcalari; baska alan ya da bozuk adreste None."""
    parts = _split(url)
    host = parts.hostname if parts is not None else None
    if not host or (host != WIKIMEDIA_DOMAIN and not host.endswith(f".{WIKIMEDIA_DOMAIN}")):
        return None
    return parts._replace(query="", fragment="")


def clean_url(url: str) -> str:
    """Wikimedia adresinde sorgu (?utm_*) ve #parca atilir; baska alanda adres aynen kalir (imzali/boyutlu sorgu)."""
    return url.split("#", 1)[0].split("?", 1)[0] if _wikimedia_parts(url) is not None else url


def is_thumb(url: str) -> bool:
    """Adres yolu bir thumb klasorunde mi (/thumb/: olcekli kopya, orijinal degil)."""
    parts = _split(url)
    return parts is not None and f"/{THUMB_DIR}/" in parts.path


def _thumb_dir(original_path: str) -> str | None:
    """Orijinalin thumb klasoru (Commons hash duzeni): <onek>/<a>/<ab>/<ad> -> <onek>/thumb/<a>/<ab>/<ad>."""
    segments = original_path.split("/")
    if len(segments) < 4:
        return None
    return "/".join([*segments[:-3], THUMB_DIR, *segments[-3:]])


def thumb_at_width(thumb_url: str, original_url: str, width: int = THUMB_WIDTH) -> str | None:
    """original_url'in Wikimedia thumb'ini <width> px'e cevirir (sorgusuz); uygun degilse None.

    Ayni dosya sarti (K81: incelenen kare = teslim edilen kare): thumb <onek>/thumb/<a>/<ab>/<ad>/<N>px-<x> olmali ve
    <onek>/<a>/<ab>/<ad> orijinalin yolu olmali (yuzde kodlama farki onemsiz). Baska dosyanin thumb'i, /thumb/
    klasorunde olmayan adres ya da Wikimedia disi alan None verir; yoksa B'nin kopyasi A'nin adi ve lisansiyla iner.
    """
    thumb, original = _wikimedia_parts(thumb_url), _wikimedia_parts(original_url)
    if thumb is None or original is None:
        return None
    head, _, name = thumb.path.rpartition("/")
    match = THUMB_NAME_RE.match(name)
    expected = _thumb_dir(original.path)
    if not match or expected is None or unquote(head) != unquote(expected):
        return None
    return thumb._replace(path=f"{head}/{width}px-{match.group(1)}").geturl()


def same_file_thumb(sources: Iterable[Any], original: str, ext: str | None, accept: Callable[[str], bool],
                    width: int = THUMB_WIDTH) -> str | None:
    """sources'tan sirayla ilk uygun adres: original'in <width> px Wikimedia thumb'i (thumb_at_width: ayni dosya, K81),
    uzantisi ext ve accept(adres) dogru; yoksa None. Metin olmayan kaynak atlanir; ext yoksa None."""
    if not ext:
        return None
    for source in sources:
        scaled = thumb_at_width(source, original, width) if isinstance(source, str) else None
        if scaled and accept(scaled) and extension(scaled) == ext:
            return scaled
    return None


def thumb_width(url: Any) -> int | None:
    """Thumb adresindeki genislik: yol /thumb/ klasorunde ve son parca '<N>px-...' (sayfali dosyada
    '[lossy-]page<n>-<N>px-...'); thumb degilse ya da adres cozulemiyorsa None."""
    parts = _split(url)
    if parts is None or f"/{THUMB_DIR}/" not in parts.path:
        return None
    match = THUMB_SIZE_RE.match(parts.path.rsplit("/", 1)[-1])
    return int(match.group(1)) if match else None


def _original_path(thumb_path: str) -> str | None:
    """_thumb_dir'in tersi: <onek>/thumb/<a>/<ab>/<ad>/<thumb adi> -> <onek>/<a>/<ab>/<ad> (ayni dosya, K81). Commons
    hash duzeni (<a>: onaltilik bir hane, <ab>: <a> ile baslayan iki hane) ya da dosya adi yoksa None."""
    segments = thumb_path.split("/")[:-1]
    if len(segments) < 5 or segments[-4] != THUMB_DIR:
        return None
    first, second, name = segments[-3:]
    if not (HASH_DIRS_RE.fullmatch(f"{first}/{second}") and second.startswith(first) and name):
        return None
    return "/".join([*segments[:-4], first, second, name])


def needs_original(url: Any) -> bool:
    """original_url bu haliyle plana giremez: upload/thumb.wikimedia.org thumb'i (kimlik bilgisi yok) ve genisligi
    standart disi (STANDARD_WIDTHS disi; 1600 = HTTP 400) ya da THUMB_WIDTH'ten genis (sozlesme: en cok 1600 px kopya)."""
    parts = _wikimedia_parts(url)
    if parts is None or parts.hostname not in DEFAULT_HOSTS or parts.username or parts.password:
        return False
    width = thumb_width(url)
    return width is not None and (width not in STANDARD_WIDTHS or width > THUMB_WIDTH)


def standard_original(url: Any) -> Any:
    """Plana girecek ozgun adres: needs_original degilse url aynen; ise ayni dosyanin ozgun adresi (ORIGINAL_HOST,
    sorgusuz; sema ve port korunur, izin kurali ayrica uygulanir); ozgun adres cikarilamazsa None."""
    if not needs_original(url):
        return url
    parts = _wikimedia_parts(url)
    path = _original_path(parts.path)
    if path is None:
        return None
    netloc = ORIGINAL_HOST if parts.port is None else f"{ORIGINAL_HOST}:{parts.port}"
    return parts._replace(netloc=netloc, path=path).geturl()


def original_problem(url: Any) -> str:
    """standard_original None verdiginde satirin/karenin ret gerekcesi."""
    return (f"standart disi ya da {THUMB_WIDTH} px'ten genis thumb ({thumb_width(url)} px; Wikimedia dogrudan istekte "
            f"yalniz {'/'.join(map(str, STANDARD_WIDTHS))} px verir), ozgun dosya adresi cikarilamadi: {url}")


def given_thumb_note(url: Any) -> str:
    """Ozgun adrese cevrilen satirin/karenin ret gerekcesine eklenen not: verilen thumb adresi (izi kaybolmasin)."""
    return f" ({url} thumb'inin ozgun dosyasi)" if needs_original(url) else ""


def _width(row: dict[str, Any]) -> int:
    try:
        return int(row.get("width") or 0)
    except (TypeError, ValueError):
        return 0


def _thumb_data_missing(row: dict[str, Any]) -> bool:
    """--prefer-thumb karari verilemiyor: width yok/gecersiz ya da width > THUMB_WIDTH iken thumb_url yok/bos."""
    width, thumb = _width(row), row.get("thumb_url")
    return width <= 0 or (width > THUMB_WIDTH and not (isinstance(thumb, str) and thumb.strip()))


def _prepare_row(row: dict[str, Any], allow_hosts: tuple[str, ...]) -> tuple[dict[str, Any] | None, str | None]:
    """(plana girecek satir, None) ya da (None, sorun). original_url standart disi ya da THUMB_WIDTH'ten genis Wikimedia
    thumb'i ise satirin kopyasinda ayni dosyanin ozgun adresi olur (standard_original); girdi satiri degismez."""
    if not row.get("photo_id") or not row.get("original_url"):
        return None, "photo_id ve original_url zorunlu"
    given = row["original_url"]
    if not _allowed(given, allow_hosts):
        return None, f"izin verilmeyen indirme adresi: {given}"
    original = standard_original(given)
    if original is None:
        return None, original_problem(given)
    note = given_thumb_note(given)
    if not _allowed(original, allow_hosts):
        return None, f"izin verilmeyen indirme adresi: {original}{note}"
    ready = row if original == given else {**row, "original_url": original}
    if not _row_slug(ready):
        return None, "entry_id/slug'tan slug cikarilamadi"
    if not _row_ext(ready):
        return None, f"gecersiz uzanti (jpg/png/webp bekleniyor): {ready['original_url']}{note}"
    return ready, None


def _download_url(row: dict[str, Any], ext: str | None, allow_hosts: tuple[str, ...], prefer_thumb: bool,
                  fixed_from: Any = None) -> str:
    """Indirme adresi (Wikimedia'da sorgusuz); prefer_thumb'da orijinal THUMB_WIDTH'ten genisse ayni dosyanin izinli,
    ayni bicimli thumb'i: once thumb_url, o kullanilamazsa ozgun adrese cevrilen verilen adres (fixed_from)."""
    original = clean_url(row["original_url"])
    if not prefer_thumb or _width(row) <= THUMB_WIDTH:
        return original
    scaled = same_file_thumb((row.get("thumb_url"), fixed_from), row["original_url"], ext,
                             lambda url: _allowed(url, allow_hosts))
    return scaled or original


def build_plan_detail(rows: list[dict[str, Any]], city_id: str, allow_hosts: tuple[str, ...] = DEFAULT_HOSTS,
                      prefer_thumb: bool = False) -> tuple[list[dict[str, str]], list[str], dict[str, int]]:
    """(plan, hatalar, sayaclar); sayaclar plana giren satirlar icindir: thumb_skipped_missing, original_is_thumb,
    original_thumb_fixed."""
    plan: list[dict[str, str]] = []
    errors: list[str] = []
    kept: list[tuple[dict[str, Any], str]] = []  # (plana giren satir, indirme adresi)
    seen_ids: set[str] = set()
    counters: dict[str, int] = {}
    fixed = 0
    for index, row in enumerate(rows, start=1):
        ready, problem = _prepare_row(row, allow_hosts)
        if not problem and row["photo_id"] in seen_ids:
            problem = f"yinelenen photo_id: {row['photo_id']}"
        if problem:
            errors.append(f"satir {index}: {problem}")
            continue
        seen_ids.add(row["photo_id"])
        slug, ext = _row_slug(ready), _row_ext(ready)
        counters[slug] = counters.get(slug, 0) + 1
        original = f"Fotoğraflar/{city_id}_{slug}_{counters[slug]:02d}.{ext}"
        url = _download_url(ready, ext, allow_hosts, prefer_thumb, row["original_url"] if ready is not row else None)
        plan.append({"photo_id": row["photo_id"], "original_file": original, "downloaded_file_url": url})
        kept.append((ready, url))
        fixed += ready is not row
    # thumb_skipped_missing: veri eksik ve gercekten orijinale dusen satir (verilen thumb'dan turetilen kopya sayilmaz)
    skipped = sum(prefer_thumb and _thumb_data_missing(r) and url == clean_url(r["original_url"]) for r, url in kept)
    stats = {"thumb_skipped_missing": skipped, "original_is_thumb": sum(is_thumb(r["original_url"]) for r, _ in kept),
             "original_thumb_fixed": fixed}
    return plan, errors, stats


def build_plan(rows: list[dict[str, Any]], city_id: str, allow_hosts: tuple[str, ...] = DEFAULT_HOSTS,
               prefer_thumb: bool = False) -> tuple[list[dict[str, str]], list[str]]:
    plan, errors, _ = build_plan_detail(rows, city_id, allow_hosts, prefer_thumb)
    return plan, errors


def load_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}: gecersiz JSON ({error})") from error
        if not isinstance(row, dict):
            raise ValueError(f"{path}:{number}: nesne bekleniyor")
        rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    p = argparse.ArgumentParser(description="Secilen fotograflardan indirme plani (Atinc kuyrugu)")
    p.add_argument("--selected", required=True, type=Path)
    p.add_argument("--city-id", required=True)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--allow-host", action="append", default=[])
    p.add_argument("--prefer-thumb", action="store_true",
                   help=f"orijinal {THUMB_WIDTH} px'ten genisse ayni dosyanin ayni bicimdeki {THUMB_WIDTH} px "
                        "Wikimedia thumb'ini indir (satirda width + thumb_url gerekir, eksikse ozet "
                        "thumb_skipped_missing; Fotoğraflar.modifications olceklemeyi belirtmeli)")
    args = p.parse_args(argv)
    if not CITY_RE.match(args.city_id):
        print("HATA: --city-id kucuk harf ASCII/rakam/tire olmali", file=sys.stderr)
        return EXIT_USAGE
    try:
        rows = load_rows(args.selected)
    except (OSError, ValueError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE
    hosts = (*DEFAULT_HOSTS, *args.allow_host)
    plan, errors, stats = build_plan_detail(rows, args.city_id, hosts, prefer_thumb=args.prefer_thumb)
    write_json(args.out, plan)
    urls = [r["downloaded_file_url"] for r in plan]
    emit({"rows": len(rows), "plan_rows": len(plan), "prefer_thumb": args.prefer_thumb,
          "thumb_rows": sum(map(is_thumb, urls)), **stats,
          "download_hosts": sorted({urlsplit(u).hostname for u in urls}), "errors": len(errors),
          "error_list": errors[:20], "out": str(args.out)})
    return EXIT_FINDINGS if errors else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
