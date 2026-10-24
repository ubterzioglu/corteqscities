"""Secilen Commons karelerinden indirme plani ve Fotoğraflar/Kanıtlar/FotoğrafKaynakları satirlari (A6; pilot: foto_satirlari.py).

Kullanim:
  photo_rows.py plan <is_klasoru> --city-id eindhoven --tools <araclar/arac> [--candidates <dosya> ...]
                [--plan-out <is>/foto/indirme_plani.json] [--clean-out <is>/foto/secim_temiz.jsonl] [--out rapor.json]
  photo_rows.py rows <is_klasoru> --package <paket_koku> --city-id eindhoven --tools <araclar/arac> [--date YYYY-MM-DD]
                [--candidates <dosya> ...] [--search <dosya> ...]
                [--clean <is>/foto/secim_temiz.jsonl] [--parts-dir <is>/data/parcalar] [--out rapor.json]
Aday (candidates.jsonl) ve ham arama (search.jsonl) kayitlari: varsayilan ana tur <is>/foto/ (sart) ve ek tur
      klasorleri <is>/foto_*/ (A12, or. foto_ek16; varsa) birlikte, bu sirayla; --candidates/--search (tekrarlanabilir)
      verilirse yalniz onlar, verilen sirayla. Ayni kimlikte onceki dosyanin kaydi kalir (ana tur onde). Okunan
      dosyalar ozette (candidate_files, search_files). Kural photo_previews ile ortak (photo_rounds). Ek tur bu duzenin
      disindaysa (or. <is>/foto/ek16/) taranmaz: kareleri 'aday yok' ile atilir; --candidates (ana dosya dahil) verilir.
plan: foto/selected.jsonl {key, entry_id, role: Mekân|Kapak, caption, seen} + adaylar + data/Mekânlar ve Mahalleler
      (slug) -> indirme plani (Atinc download_media.py girdisi) ve secim_temiz.jsonl (lisans/yazar normalize).
      Mekan rolundeki kare kapak adina dusmez: kaydi data/'da yoksa (yeni mekan birlestirilmemis: once merge_package)
      atilir ve kimligi ozette missing_entries'te; kaydi olup slug'i bos, gecersiz ya da kapak karelerinin adi
      ('kapak') ise de atilir (gerekce raporun dropped'inda; missing_entries'e girmez).
      Indirme adresi download_plan --prefer-thumb kuraliyla ayni (ayni fonksiyonlar): original_url standart disi ya
      da 1280'den genis thumb ise ayni dosyanin ozgun adresine cevrilir (ozette original_thumb_fixed; cikarilamazsa
      ya da bicim desteklenmezse kare atilir, gerekcede verilen adres de yazar); genislik > 1280 ise AYNI dosyanin
      ayni bicimli 1280 px kopyasi (K81): once thumb_url'den, o kullanilamazsa ozgun adrese cevrilen original_url'den;
      ikisi de olmazsa ozgun dosya; uzanti .jpeg -> .jpg.
rows: secim_temiz + <paket>/Teslimler/download-progress-v7.json + arama kayitlari (ham imageinfo) + adaylar ->
      data/parcalar/{Fotoğraflar,Kanıtlar,FotoğrafKaynakları}.foto.jsonl. Web kopyasi resmi create_web_copy ile
      <paket>/Teslimler/WebKopyalari/ altina yazilir. Paket yolu alanlari ('file', '*_file') her isletim sisteminde
      '/' ile yazilir (L0 ISS-004: create_web_copy Windows'ta '\\' dondurur). modifications paketteki dosyanin
      kendisinden yazilir (K75): Commons dosya adi, ozgun en×boy (aday kaydi), PIL ile olculen en×boy (EXIF yonu dahil),
      teslim dosyasi adi ve SHA-256 oneki; ayni dizinin numarali kareleri ve iki satirda secilen ayni dosya da
      text_quality'de kume uretmez (K27/K28). Okunamayan indirilmis dosya o kare icin bulgudur.
Lisans/yazar ve kaynak zinciri kurallari resmi dogrulayicinin kendi fonksiyonlariyla (--tools ya da CORTEQS_TOOLS:
CC, cc_license_matches, official_cc_url, provenance.extract, create_web_copy) uygulanir; uymayan kare atilir.
Araclar sys.dont_write_bytecode=True ile yuklenir (araclar klasorune __pycache__ yazilmaz). Insan inceleme alanlari
daima 'Bekliyor' (K97: AI kendi isini onaylamaz). --date varsayilani bugunun UTC tarihi.
stdout tek satir JSON; cikis 0 temiz / 1 bulgu (atilan kare, eksik indirme, web kopyasi hatasi) / 2 kullanim.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import importlib
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable
from urllib.parse import urlsplit

from PIL import Image

import download_plan
from common import (EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, HUMAN_PENDING_VALUE, emit, safe_relpath, setup_utf8,
                    sha256_file, write_json)
from photo_rounds import load_candidates, read_jsonl, round_files, shown

CITY_RE = re.compile(r"^[a-z0-9-]+\Z")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*\Z")
BAD_AUTHOR = re.compile(r"^(own work|unknown|anonymous|unknown author|bilinmiyor)?$", re.I)
DELIVERY_WIDTH = download_plan.THUMB_WIDTH  # 1280: sozlesme <=1600 px kopyaya izin verir; Wikimedia 1600'u reddeder
ORIGINAL_PREFIX = "https://upload.wikimedia.org/"
SCALED_PREFIXES = tuple(f"https://{host}/" for host in download_plan.DEFAULT_HOSTS)  # https, port/kimlik yok
ORIENTATION_TAG = 0x0112
ROTATED = (5, 6, 7, 8)  # EXIF yonu 90/270 derece: Commons en×boyu dondurulmus olcuyle verir
NAME_MAX = 90
SHA_PREFIX = 12  # notu kareye ozgu kilar: ayni olculu numarali dizide rakam disi tek ayirt edici olgu
CC0_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
CC0_PATH = r"/publicdomain/zero/1\.0(?:/deed\.[a-z]{2})?/?"
ROLES = ("Mekân", "Kapak")
COVER_BASE = "kapak"  # Kapak karelerinin adi ve numara sayaci: mekan slug'i olamaz (kimlikler cakisir)
MISSING_ENTRY = "mekan kaydi yok"
TOOL_MODULES = ("core", "provenance", "delivery_tools")
PART_NAMES = ("Fotoğraflar", "Kanıtlar", "FotoğrafKaynakları")
PROGRESS = ("Teslimler", "download-progress-v7.json")


class UsageError(Exception):
    """Eksik/bozuk girdi, gecersiz arguman ya da yuklenemeyen --tools (cikis 2)."""


@dataclass(frozen=True)
class Tools:
    """Resmi araclardan (araclar/arac) yalniz kullanilan parcalar."""
    cc: Any
    cc_license_matches: Callable[[str, str], bool]
    official_cc_url: Callable[[str, str], bool]
    extract: Callable[[dict, dict], dict]
    create_web_copy: Callable[[Path, dict], dict]


def load_tools(tools_dir: Path) -> Tools:
    """Resmi modulleri verilen klasorden yukler; bayt kodu yazilmaz, sys.path ve bayrak eski haline doner."""
    tools = Path(tools_dir).resolve()
    if not (tools / "provenance.py").is_file() or not (tools / "delivery_tools.py").is_file():
        raise UsageError(f"--tools klasorunde provenance.py / delivery_tools.py yok: {tools}")
    for name in [n for n in sys.modules if n.split(".")[0] in TOOL_MODULES]:
        del sys.modules[name]  # baska bir --tools klasorunden kalan modul kullanilmasin
    importlib.invalidate_caches()
    previous_flag, previous_path = sys.dont_write_bytecode, list(sys.path)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(tools))
    try:
        values = importlib.import_module("core.content_delivery.delivery_values")
        media = importlib.import_module("core.content_delivery.validation_media")
        provenance = importlib.import_module("provenance")
        delivery = importlib.import_module("delivery_tools")
        return Tools(values.CC, media.cc_license_matches, media.official_cc_url, provenance.extract,
                     delivery.create_web_copy)
    except Exception as error:  # noqa: BLE001 - resmi kodun her yukleme hatasi kullanim hatasidir
        raise UsageError(f"resmi araclar yuklenemedi ({type(error).__name__}: {error})") from error
    finally:
        sys.dont_write_bytecode = previous_flag
        sys.path[:] = previous_path


# ---------------------------------------------------------------- kurallar

def norm_license(tools: Tools, label: Any, url: Any, source_url: Any) -> tuple[str, str] | None:
    """(etiket, adres) ya da None. CC adresi https, sorgusuz, '/' ile biter; PD dayanagi Commons dosya sayfasi."""
    label, url = str(label or "").strip(), str(url or "").strip()
    if url.startswith("//"):
        url = "https:" + url
    url = url.replace("http://", "https://").split("?")[0]
    if label.lower() in ("public domain", "pd"):
        return ("Public domain", source_url) if source_url else None
    if label.upper() in ("CC0", "CC0 1.0", "CC-ZERO"):
        return ("CC0 1.0", CC0_URL) if tools.official_cc_url(CC0_URL, CC0_PATH) else None
    if tools.cc.fullmatch(label):
        url = url if url.endswith("/") else url + "/"
        return (label, url) if tools.cc_license_matches(label, url) else None
    return None


def _int(value: Any) -> int:
    try:
        return max(int(value or 0), 0)
    except (TypeError, ValueError):
        return 0


COMMONS = "Wikimedia Commons"


def delivery_url(candidate: dict[str, Any]) -> str:
    """Teslim adresi; download_plan --prefer-thumb kuraliyla ayni (standard_original/same_file_thumb/clean_url):
    original_url standart disi ya da 1280'den genis thumb ise ayni dosyanin ozgun adresi kullanilir; ozgun dosya
    https://upload.wikimedia.org/ altinda olmali (yoksa ''); genislik > 1280 ise AYNI dosyanin ayni bicimli 1280 px
    Wikimedia kopyasi (once thumb_url'den, o kullanilamazsa ozgun adrese cevrilen original_url'den), yoksa sorgusuz
    ozgun dosya. Baska dosyanin thumb'i asla secilmez (K81)."""
    given = candidate.get("original_url")
    if candidate.get("provider", COMMONS) != COMMONS:  # ikinci kaynak (Flickr vb.): ozgun adres aynen, sorgusuz, https
        parts = urlsplit(str(given or ""))
        return download_plan.clean_url(str(given)) if parts.scheme == "https" and parts.hostname else ""
    original = download_plan.standard_original(given)
    if not isinstance(original, str) or not original.startswith(ORIGINAL_PREFIX):
        return ""
    original = download_plan.clean_url(original)
    if _int(candidate.get("width")) <= DELIVERY_WIDTH:
        return original
    fixed_from = given if download_plan.needs_original(given) else None
    scaled = download_plan.same_file_thumb((candidate.get("thumb_url"), fixed_from), original,
                                           download_plan.extension(original),
                                           lambda url: url.startswith(SCALED_PREFIXES), DELIVERY_WIDTH)
    return scaled or original


def capture_date(value: Any) -> str:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})", str(value or ""))
    return f"{match.group(1)}-{match.group(2)}-{match.group(3)}" if match else ""


def measured_size(path: Path) -> tuple[int, int]:
    """Dosyanin PIL ile olculen gorunen en×boyu; EXIF yonu 90/270 ise eksenler yer degistirir (Commons olcusu gibi)."""
    with Image.open(path) as image:
        width, height = image.size
        orientation = image.getexif().get(ORIENTATION_TAG)
    return (height, width) if orientation in ROTATED else (width, height)


def commons_name(candidate: dict[str, Any]) -> str:
    raw = candidate.get("commons_file") or str(candidate.get("candidate_id") or "").split("|", 1)[-1]
    name = re.sub(r"^File:", "", str(raw or candidate.get("title") or "")).replace("_", " ").strip()
    prefix = f"{candidate.get('provider', COMMONS)}: "
    return (name[len(prefix):] if name.startswith(prefix) else name)[:NAME_MAX]


def modification_note(candidate: dict[str, Any], downloaded_url: str, delivered: Path) -> str:
    """Kareye ozgu degisiklik bildirimi (K75), paketteki dosyanin kendisinden: Commons dosya adi, ozgun en×boy (aday
    kaydi; yoksa yazilmaz), PIL ile olculen en×boy, teslim dosyasi adi ve SHA-256 oneki. Dosya okunamazsa OSError."""
    width, height = measured_size(delivered)
    name = commons_name(candidate)
    provider = candidate.get("provider", COMMONS)
    delivered_file = f" Teslim dosyası: {delivered.name} (SHA-256 {sha256_file(delivered)[:SHA_PREFIX]})."
    if "/thumb/" in urlsplit(downloaded_url).path:
        source_w, source_h = _int(candidate.get("width")), _int(candidate.get("height"))
        source = f" ({source_w}×{source_h} px)" if source_w and source_h else ""
        return (f"{provider}'taki \"{name}\"{source} özgün dosyasının {width}×{height} px küçültülmüş kopyası "
                f"indirildi; kırpma, rötuş ve renk düzeltmesi yapılmadı.{delivered_file}")
    return (f"{provider}'taki \"{name}\" özgün dosyası ({width}×{height} px) değiştirilmeden indirildi."
            f"{delivered_file}")


def venue_problem(sel: dict, slugs: dict) -> str | None:
    """Mekan rolundeki karenin kayit sorunu (yoksa None): kare 'kapak' adina dusmez, atilir (pilot A12)."""
    entry = sel.get("entry_id")
    if not entry or entry not in slugs:
        return (f"{MISSING_ENTRY}: {entry} (data/Mekânlar.jsonl ve Mahalleler.jsonl'da yok; yeni mekan once "
                f"merge_package ile birlestirilmeli)")
    slug = str(slugs.get(entry) or "")
    if not SLUG_RE.match(slug):
        return f"mekan slug'i gecersiz: {entry} '{slug}'"
    if slug == COVER_BASE:
        return f"slug ayrilmis: '{COVER_BASE}' kapak karelerinin adi ({entry}); mekanin slug'i degismeli"
    return None


def check_selection(tools: Tools, sel: dict, candidates: dict, slugs: dict) -> tuple[dict | None, str | None]:
    """(normalize alanlar, None) ya da (None, ret gerekcesi)."""
    candidate = candidates.get(sel.get("key"))
    if not candidate:
        return None, "aday yok"
    if sel.get("role") not in ROLES:
        return None, f"rol gecersiz: {sel.get('role')}"
    problem = venue_problem(sel, slugs) if sel["role"] == "Mekân" else None
    if problem:
        return None, problem
    lic = norm_license(tools, candidate.get("license"), candidate.get("license_url"), candidate.get("source_url"))
    if not lic:
        return None, f"lisans uygun degil: {candidate.get('license')} {candidate.get('license_url')}"
    author = re.sub(r"\s+", " ", str(candidate.get("author_text") or "")).strip()
    if BAD_AUTHOR.match(author) or len(author) > 200:
        return None, f"yazar uygun degil: {author[:40]}"
    given = candidate.get("original_url")
    if download_plan.needs_original(given) and download_plan.standard_original(given) is None:
        return None, download_plan.original_problem(given)
    note = download_plan.given_thumb_note(given)  # ozgun adrese cevrildiyse verilen thumb adresi gerekcede kalir
    url = delivery_url(candidate)
    if not url:
        return None, f"indirme adresi izinli degil{note}"
    ext = download_plan.extension(url)  # jpg/png/webp; .jpeg -> jpg (download_plan ile ayni dosya adi)
    if not ext:
        return None, f"desteklenmeyen dosya turu: {PurePosixPath(urlsplit(url).path).suffix.lower() or '(yok)'}{note}"
    return {"license": lic[0], "license_url": lic[1], "author": author, "url": url, "ext": f".{ext}"}, None


@dataclass(frozen=True)
class PlanResult:
    plan: list[dict[str, str]]
    clean: list[dict[str, Any]]
    dropped: list[list[Any]]  # [anahtar, gerekce]
    fixed: list[list[Any]]  # [anahtar, verilen original_url, kullanilan ozgun adres] (download_plan.standard_original)
    missing_entries: list[str]  # Mekan rolunde data/'da kaydi olmayan entry_id'ler (once merge_package)


def build_plan(tools: Tools, city: str, selected: list[dict], candidates: dict, slugs: dict) -> PlanResult:
    """Indirme plani, secim_temiz satirlari ve raporlar; numara slug basina artar."""
    plan, clean, dropped, fixed, counter = [], [], [], [], collections.Counter()
    missing: set[str] = set()
    for sel in selected:
        fields, why = check_selection(tools, sel, candidates, slugs)
        if why:
            dropped.append([sel.get("key"), why])
            if why.startswith(MISSING_ENTRY) and sel.get("entry_id"):
                missing.add(str(sel["entry_id"]))
            continue
        given = candidates[sel["key"]].get("original_url")
        if download_plan.needs_original(given):
            fixed.append([sel.get("key"), given, download_plan.standard_original(given)])
        base = slugs[sel["entry_id"]] if sel["role"] == "Mekân" else COVER_BASE
        counter[base] += 1
        number = counter[base]
        row = {"photo_id": f"{city}:photo:{base}-{number:02d}",
               "original_file": f"Fotoğraflar/{city}_{base}_{number:02d}{fields['ext']}",
               "downloaded_file_url": fields["url"]}
        plan.append(row)
        clean.append({**sel, "photo_id": row["photo_id"], "file": row["original_file"], "license": fields["license"],
                      "license_url": fields["license_url"], "author": fields["author"]})
    return PlanResult(plan, clean, dropped, fixed, sorted(missing))


def photo_record(city: str, date: str, sel: dict, candidate: dict, download: dict, order: int,
                 note: str) -> dict[str, Any]:
    return {"photo_id": sel["photo_id"], "city_id": city, "role": sel["role"],
            "entry_id": sel.get("entry_id") if sel["role"] == "Mekân" else "", "file": sel["file"],
            "sha256": download.get("sha256", ""), "caption": str(sel.get("caption") or "")[:250],
            "author": sel["author"], "license": sel["license"], "license_url": sel["license_url"],
            "source_url": candidate["source_url"], "capture_date": capture_date(candidate.get("date_original")),
            "source_checked_on": date, "modifications": note,
            "evidence_id": f"{city}:evidence:{sel['photo_id'].split(':')[-1]}", "completion_credit": "Evet",
            "order": order, "editorial_status": "Taslak"}


def delivered_note(package: Path, sel: dict, candidate: dict, download: dict) -> tuple[str | None, str | None]:
    """(degisiklik notu, None) ya da (None, hata): paketteki dosya guvenli yolda olmali ve PIL ile okunmali."""
    try:
        path = safe_relpath(package, str(sel.get("file") or ""))
        return modification_note(candidate, str(download.get("downloaded_file_url") or ""), path), None
    except (OSError, ValueError, Image.DecompressionBombError) as error:  # PIL okuyamazsa OSError
        return None, f"indirilen dosya okunamadi ({type(error).__name__}: {error})"


def evidence_record(city: str, date: str, photo: dict, sel: dict, candidate: dict, download: dict,
                    raw: dict) -> dict[str, Any]:
    source_evidence = {"source_url": candidate["source_url"], "author": sel["author"], "license": sel["license"],
                       "license_url": sel["license_url"], "original_api_record": raw.get(candidate["source_url"]) or {},
                       "delivered_file": {"url": download.get("downloaded_file_url") or ""},
                       "retrieved_on": download.get("downloaded_on") or date}
    return {"evidence_id": photo["evidence_id"], "city_id": city, "photo_id": photo["photo_id"],
            "source_url": candidate["source_url"],
            "source_title": str(candidate.get("commons_file") or candidate.get("title") or "")[:180],
            "author": sel["author"], "license": sel["license"], "license_url": sel["license_url"],
            "usage_terms": candidate.get("usage_terms") or sel["license"],
            "attribution": f"{sel['author']} · {sel['license']} · {candidate.get('provider', COMMONS)}",
            "restrictions": candidate.get("restrictions") or "", "checked_on": date,
            "metadata_review_status": HUMAN_PENDING_VALUE, "pixel_review_status": HUMAN_PENDING_VALUE,
            "pixel_review_file": sel["file"], "pixel_review_note": str(sel.get("seen") or "")[:500],
            "rights_status": HUMAN_PENDING_VALUE,
            "rights_basis": (f"Wikimedia Commons dosya sayfasındaki lisans: {sel['license']}"
                         if candidate.get("provider", COMMONS) == COMMONS
                         else f"{candidate['provider']} kaynak sayfasındaki lisans: {sel['license']}"),
            "source_snapshot_file": "", "source_snapshot_sha256": "", "license_snapshot_file": "",
            "license_snapshot_sha256": "", "source_evidence_json": json.dumps(source_evidence, ensure_ascii=False)}


EVIDENCE_DIR = "Lisans kanıtları"  # düz klasör (Drive alt klasörü korumuyor)


def with_evidence_files(package: Path, evidence: dict[str, Any]) -> dict[str, Any]:
    """Kaynak ve lisans kaydını gerçek dosya olarak yazar, Kanıtlar'ın dört snapshot alanını doldurur. Uygulamanın
    ready aşaması bu dosyaları zorunlu tutar (Bakersfield: 46 foto için 92 eksik); Kaynaklar sekmesine bağlı değildir."""
    base = evidence["photo_id"].split(":")[-1]
    folder = package / EVIDENCE_DIR
    folder.mkdir(parents=True, exist_ok=True)
    payloads = {"source": json.loads(evidence["source_evidence_json"]),
                "license": {"license": evidence["license"], "license_url": evidence["license_url"],
                            "usage_terms": evidence["usage_terms"], "author": evidence["author"],
                            "source_url": evidence["source_url"], "checked_on": evidence["checked_on"]}}
    filled = {}
    for kind, payload in payloads.items():
        path = folder / f"{base}.{kind}-evidence.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        filled[f"{kind}_snapshot_file"] = f"{EVIDENCE_DIR}/{path.name}"
        filled[f"{kind}_snapshot_sha256"] = sha256_file(path)
    return {**evidence, **filled}


def posix_paths(row: dict[str, Any]) -> dict[str, Any]:
    """Paket kokunden goreli yol alanlari ('file' ve '*_file') '/' ile (L0 ISS-004): resmi create_web_copy web_file'i
    str(Path) ile, Windows'ta '\\' ile yazar; Atinc'in local_file'i yolu PurePosixPath ile okur, '\\'li yol Linux/Mac'te
    bulunamaz. Anahtar sirasi korunur (merge_package sozlesmesi)."""
    return {key: value.replace("\\", "/") if isinstance(value, str) and (key == "file" or key.endswith("_file"))
            else value for key, value in row.items()}


def build_rows(tools: Tools, city: str, date: str, package: Path, sources: dict) -> dict[str, Any]:
    """Uc sekmenin satirlari; indirilmemis kare 'missing', web kopyasi/aday hatasi 'errors' olur (atlanir). Paket yolu
    alanlari secim dosyasi ya da resmi araclar ne verirse versin '/' ile yazilir (posix_paths)."""
    out = {"photos": [], "evidence": [], "provenance": [], "missing": [], "errors": []}
    order: collections.Counter = collections.Counter()
    for sel in map(posix_paths, sources["clean"]):
        download = sources["done"].get(sel.get("photo_id"))
        candidate = sources["candidates"].get(sel.get("key"))
        if not download:
            out["missing"].append(sel.get("photo_id"))
            continue
        if not candidate:
            out["errors"].append({"photo_id": sel.get("photo_id"), "why": "aday yok"})
            continue
        note, why = delivered_note(package, sel, candidate, download)
        if why:
            out["errors"].append({"photo_id": sel.get("photo_id"), "why": why})
            continue
        key = (sel["role"], sel.get("entry_id") or "")
        photo = photo_record(city, date, sel, candidate, download, order[key] + 1, note)
        evidence = with_evidence_files(package, evidence_record(city, date, photo, sel, candidate, download,
                                                                sources["raw"]))
        try:
            provenance = tools.create_web_copy(package, tools.extract(photo, evidence))
        except Exception as error:  # noqa: BLE001 - resmi aracin her hatasi o kare icin bulgudur, toplu is surer
            out["errors"].append({"photo_id": sel["photo_id"], "why": f"{type(error).__name__}: {error}"})
            continue
        order[key] += 1
        out["photos"].append(posix_paths(photo))
        out["evidence"].append(posix_paths(evidence))
        out["provenance"].append(posix_paths(provenance))
    return out


# ---------------------------------------------------------------- girdi / cikti (okuma kurallari: photo_rounds)

def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_slugs(work: Path) -> dict[str, str]:
    slugs: dict[str, str] = {}
    for sheet in ("Mekânlar", "Mahalleler"):
        path = work / "data" / f"{sheet}.jsonl"
        if path.is_file():
            slugs.update({r["entry_id"]: r.get("slug") for r in read_jsonl(path) if r.get("entry_id")})
    return slugs


def load_raw(paths: list[Path]) -> dict[str, Any]:
    """Commons dosya sayfasi (imageinfo.descriptionurl) -> ham imageinfo (Kanıtlar original_api_record); ilk gelen
    kalir."""
    raw: dict[str, Any] = {}
    for path in paths:
        for record in read_jsonl(path):
            info = record.get("imageinfo")
            if isinstance(info, dict):
                raw.setdefault(info.get("descriptionurl"), info)
    return raw


def load_rows_sources(args: argparse.Namespace, work: Path, package: Path, candidate_files: list[Path],
                      search_files: list[Path]) -> dict[str, Any]:
    progress_path = package.joinpath(*PROGRESS)
    try:
        progress = json.loads(progress_path.read_text(encoding="utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise UsageError(f"{progress_path}: okunamadi ({type(error).__name__})") from error
    if not isinstance(progress, list) or not all(isinstance(r, dict) for r in progress):
        raise UsageError("download-progress-v7.json satir listesi olmali")
    raw = load_raw(search_files)
    return {"clean": read_jsonl(args.clean or work / "foto" / "secim_temiz.jsonl"), "raw": raw,
            "candidates": load_candidates(candidate_files), "done": {r.get("photo_id"): r for r in progress}}


def run_plan(args: argparse.Namespace, tools: Tools, work: Path) -> int:
    selected = read_jsonl(work / "foto" / "selected.jsonl")
    candidate_files = args.candidates or round_files(work, "candidates.jsonl")
    result = build_plan(tools, args.city_id, selected, load_candidates(candidate_files), load_slugs(work))
    plan_out = Path(args.plan_out or work / "foto" / "indirme_plani.json")
    plan_out.parent.mkdir(parents=True, exist_ok=True)
    plan_out.write_text(json.dumps(result.plan, ensure_ascii=False, indent=1), encoding="utf-8")
    clean_out = Path(args.clean_out or work / "foto" / "secim_temiz.jsonl")
    write_jsonl(clean_out, result.clean)
    if args.out:
        write_json(args.out, {"dropped": result.dropped, "missing_entries": result.missing_entries,
                              "original_thumb_fixed": result.fixed})
    emit({"status": "findings" if result.dropped else "ok", "selected": len(selected), "planned": len(result.plan),
          "dropped": len(result.dropped), "drop_examples": result.dropped[:8],
          "missing_entries": result.missing_entries, "original_thumb_fixed": len(result.fixed),
          "candidate_files": [shown(work, path) for path in candidate_files], "plan_out": str(plan_out),
          "clean_out": str(clean_out)})
    return EXIT_FINDINGS if result.dropped else EXIT_OK


def run_rows(args: argparse.Namespace, tools: Tools, work: Path) -> int:
    package = Path(args.package).resolve()
    if not package.is_dir():
        raise UsageError(f"paket koku yok: {package}")
    candidate_files = args.candidates or round_files(work, "candidates.jsonl")
    search_files = args.search or round_files(work, "search.jsonl")
    sources = load_rows_sources(args, work, package, candidate_files, search_files)
    result = build_rows(tools, args.city_id, args.date, package, sources)
    parts_dir = Path(args.parts_dir or work / "data" / "parcalar")
    for name, key in zip(PART_NAMES, ("photos", "evidence", "provenance")):
        write_jsonl(parts_dir / f"{name}.foto.jsonl", result[key])
    if args.out:
        write_json(args.out, {"missing": result["missing"], "errors": result["errors"]})
    photos, findings = result["photos"], bool(result["missing"] or result["errors"])
    emit({"status": "findings" if findings else "ok", "photos": len(photos),
          "roles": dict(collections.Counter(p["role"] for p in photos)), "missing_download": len(result["missing"]),
          "entries_with_photo": len({p["entry_id"] for p in photos if p["entry_id"]}), "errors": len(result["errors"]),
          "error_examples": result["errors"][:5], "candidate_files": [shown(work, path) for path in candidate_files],
          "search_files": [shown(work, path) for path in search_files], "parts_dir": str(parts_dir)})
    return EXIT_FINDINGS if findings else EXIT_OK


# ---------------------------------------------------------------- CLI

def _date_arg(text: str) -> str:
    try:
        return dt.date.fromisoformat(text).isoformat()
    except ValueError as error:
        raise argparse.ArgumentTypeError("YYYY-AA-GG olmali") from error


def _city_arg(text: str) -> str:
    if not CITY_RE.match(text):
        raise argparse.ArgumentTypeError("kucuk harf ASCII/rakam/tire olmali (or. eindhoven)")
    return text


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Commons secimi -> indirme plani ve foto sekme satirlari (resmi araclarla)")
    commands = p.add_subparsers(dest="command", required=True)
    for name in ("plan", "rows"):
        sub = commands.add_parser(name)
        sub.add_argument("work", help="is klasoru (_is)")
        sub.add_argument("--city-id", required=True, type=_city_arg)
        sub.add_argument("--tools", type=Path, help="araclar/arac klasoru (yoksa CORTEQS_TOOLS)")
        sub.add_argument("--out", type=Path, help="ayrinti JSON")
        sub.add_argument("--candidates", type=Path, action="append",
                         help="aday dosyasi (candidates.jsonl), tekrarlanabilir; verilmezse <is>/foto/ ve ek tur "
                              "klasorleri <is>/foto_*/ (A12)")
    plan, rows = commands.choices["plan"], commands.choices["rows"]
    rows.add_argument("--search", type=Path, action="append",
                      help="ham arama dosyasi (search.jsonl), tekrarlanabilir; verilmezse <is>/foto/ ve <is>/foto_*/")
    plan.add_argument("--plan-out", type=Path, help="varsayilan <is>/foto/indirme_plani.json")
    plan.add_argument("--clean-out", type=Path, help="varsayilan <is>/foto/secim_temiz.jsonl")
    rows.add_argument("--package", required=True, type=Path, help="paket koku (Teslimler/download-progress-v7.json)")
    rows.add_argument("--date", type=_date_arg, default=dt.datetime.now(dt.timezone.utc).date().isoformat(),
                      help="kontrol tarihi (source_checked_on, checked_on); varsayilan bugun (UTC)")
    rows.add_argument("--clean", type=Path, help="varsayilan <is>/foto/secim_temiz.jsonl")
    rows.add_argument("--parts-dir", type=Path, help="varsayilan <is>/data/parcalar")
    return p


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        work = Path(os.path.abspath(args.work))
        if not work.is_dir():
            raise UsageError(f"is klasoru yok: {work}")
        tools_dir = args.tools or (Path(os.environ["CORTEQS_TOOLS"]) if os.environ.get("CORTEQS_TOOLS") else None)
        if tools_dir is None:
            raise UsageError("--tools veya CORTEQS_TOOLS gerekli (araclar/arac)")
        tools = load_tools(tools_dir)
        return run_plan(args, tools, work) if args.command == "plan" else run_rows(args, tools, work)
    except (UsageError, OSError, ValueError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
