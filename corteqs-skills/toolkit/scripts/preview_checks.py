"""preview_checks.py: city-preview kanit araclari. Ag yok; paket ve Excel salt okunur; yalniz --out/--out-dir'e yazar.
stdout tek satir JSON; cikis 0 temiz, 1 bulgu, 2 kullanim/girdi hatasi.
drive-compare (K01/K03/K109/K110): Drive listesi <-> yerel envanter. Liste {root, files} dosyasi ya da arac sonuclari
  klasoru; kayit baglayicinin ham kaydi (title, fileSize, parentId: yol parentId'den) ya da {path, size, md5Checksum}.
  Icerik yalniz indirilen baytin SHA-256'siyla ya da kayittaki md5Checksum'la dogrulanir; ad+boyut hash degildir.
warning-scan (K103/K104): bant alanlari ve kapak metinlerinde her denetim emri; caption ve K104 metinlerinde okura
  denetim isi birakan kaliplar (muaflik yalniz gun-ay ya da tam tarih + kapanis/tadilat/rezervasyon birlikteyse).
report: ONIZLEME_OZETI.md; kurala, kapsama, K93/K112 islevlerine ya da Drive kanitina uymayan sonuclar.json reddedilir.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import datetime as dt
import hashlib
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Iterator

import openpyxl
import yaml
from openpyxl.utils.exceptions import InvalidFileException

import common

TOOL = "preview_checks"
DEFAULT_CHECKS = Path(__file__).resolve().parent.parent / "checks.yaml"
PREVIEW_SCOPES, DRIVE_SCOPE, OPTIONAL_CHECKS = ("drive-manual", "preview-later"), "drive-manual", ("K113",)
EXPECTED_FOLDERS = ("Fotoğraflar", "Lisans kanıtları", "Teslimler")
EVIDENCE_DIR = "Lisans kanıtları/"


class PreviewError(Exception):
    """Kullanim ya da girdi hatasi (cikis 2); problems ayrinti listesidir."""
    def __init__(self, message: str, problems: list[str] | None = None) -> None:
        super().__init__(message)
        self.problems = problems or []

# --- ortak yardimcilar ---
def fold(text: Any) -> str:
    """Kucuk harf, aksansiz (Turkce dahil), noktalamasiz, tek bosluklu metin (text_quality.normalize kurali)."""
    lowered = unicodedata.normalize("NFKD", "" if text is None else str(text).lower())
    plain = "".join(ch for ch in lowered if not unicodedata.combining(ch)).replace("ı", "i")
    return " ".join(re.sub(r"[^\w\s]|_", " ", plain).split())

def norm_path(value: Any) -> str:
    """Yol karsilastirma bicimi: NFC, '/' ayirici, bos ve '.' parcasiz."""
    text = unicodedata.normalize("NFC", str(value)).replace("\\", "/").strip()
    return "/".join(part for part in text.split("/") if part not in ("", "."))

def _load_json(path: Path, what: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PreviewError(f"{what} okunamadi: {path} ({type(exc).__name__}: {exc})") from exc

def _clip(text: Any, limit: int = 160) -> str:
    flat = " ".join(str(text).split())
    return flat if len(flat) <= limit else flat[:limit] + "…"

def _is_root_xlsx(path: str) -> bool:
    return "/" not in path and path.lower().endswith(".xlsx")

def _package_of(xlsx: Path) -> Path | None:
    """Excel bir paket kokundeyse (yaninda Fotoğraflar/Teslimler/Lisans kanıtları) o kok; degilse None."""
    parent = Path(xlsx).resolve().parent
    return parent if any((parent / name).is_dir() for name in EXPECTED_FOLDERS) else None

def _guard_out(out: Path, inputs: Iterable[Path | None], package: Path | None) -> None:
    if any(Path(item).resolve() == Path(out).resolve() for item in inputs if item is not None):
        raise PreviewError(f"--out girdiyle ayni dosya: {out} (girdi asla uzerine yazilmaz)")
    if package is not None and Path(out).resolve().is_relative_to(Path(package).resolve()):
        raise PreviewError(f"--out paket icinde: {out} (paket salt okunur; ciktiyi OUT'a yazin)")

def _finish(out: Path, report: dict[str, Any], tool: str) -> int:
    try:
        common.write_json(out, report)
    except (OSError, ValueError) as exc:
        raise PreviewError(f"--out yazilamadi: {type(exc).__name__}: {exc}") from exc
    common.emit({"tool": tool, **report["summary"], "out": str(out)})
    return common.EXIT_FINDINGS if report["summary"]["findings"] else common.EXIT_OK

# --- drive-compare (K01, K03, K109, K110) ---
FOLDER_MIME, GOOGLE_NATIVE = "application/vnd.google-apps.folder", "application/vnd.google-apps."
SHA_EXPECTED = (".xlsx", ".json")  # ana Excel ve JSON'lar icin SHA-256 (indirilen bayt) beklenir
FINDING_RESULTS = ("eksik", "fazla", "boyut_farki", "md5_farki", "sha256_farki", "google_bicimi", "yinelenen_dosya")
DIFFER_RESULTS = FINDING_RESULTS[2:]
VERIFIED_RESULTS = ("sha256_dogrulandi", "md5_eslesti")
UNVERIFIED_RESULTS = ("yalniz_ad_boyut", "yalniz_ad", "zipte_olabilir")  # bulgu degil; icerik de dogrulanmadi
K01_KINDS = ("kokte_excel_yok", "birden_fazla_excel", "excel_adi_farkli", "kok_adi_uyumsuz", "benzer_adli_klasor")
COPY_MARK = re.compile(r"\b(?:\d+|v\d+|kopya(?:si)?|copy(?: of)?)\b")
CITY_EXCEL = re.compile(r"^(CITY-\d+)_(.+?)_v\d+\.xlsx$", re.I)
ALIASES = {"name": ("title", "name"), "size": ("size", "fileSize"), "md5": ("md5Checksum", "md5"),
           "url": ("viewUrl", "webViewLink", "url")}  # Drive baglayicisi (2026-10): title, fileSize, viewUrl; md5 yok
METHOD_NOTE = {"sha256": "indirilen gerçek baytın SHA-256'sı = yerel envanterdeki SHA-256 (içerik özdeşliği kanıtı)",
               "md5": "kayıttaki Drive md5Checksum = yerel MD5 (yalnız bağlayıcı md5Checksum verdiyse; bugünkü vermiyor)",
               "ad+boyut": "yalnız ad ve boyut eşit: hash doğrulaması DEĞİL (dogrulanmayan listesinde)",
               "ad": "yalnız ad eşit, boyut yok: hash doğrulaması DEĞİL ve K110'un asgari ID/ad/boyut şartı yok",
               "zip": "dosya Drive'da tek tek yok, kanıt ZIP'inde olabilir (G.2): doğrulanmadı, K110 için ID/ad/boyut yok"}

def load_local(path: Path) -> dict[str, dict[str, Any]]:
    """inventory.py ciktisi -> {NFC yol: {size, sha256, disk}}; 'disk' diskteki asil ad (NFD olabilir), okuma onunla."""
    data = _load_json(path, "--local envanter")
    files = data.get("files") if isinstance(data, dict) else None
    if not isinstance(files, list) or not all(isinstance(f, dict) and f.get("path") and isinstance(f.get("size"), int)
                                              for f in files):
        raise PreviewError("--local: inventory.py ciktisi degil ('files' listesi, her kayitta path ve size)")
    return {norm_path(f["path"]): {"size": f["size"], "sha256": str(f.get("sha256") or "").lower(),
                                   "disk": str(f["path"]).replace("\\", "/")} for f in files}

def _payloads(value: Any, source: Path) -> Iterator[tuple[str, Any]]:
    """Arac sonucu -> ('root'|'file', kayit): sayfa ({} bos), {root, files}, kok kaydi ya da [{type: text}] sarmali."""
    if isinstance(value, list) and value and all(isinstance(v, dict) and v.get("type") == "text" for v in value):
        for block in value:
            yield from _payloads(json.loads(block.get("text") or "{}"), source)
    elif isinstance(value, dict) and ("files" in value or "root" in value or not value):
        yield from ([("root", value["root"])] if isinstance(value.get("root"), dict) else [])
        yield from (("file", item) for item in value.get("files") or [])
    elif isinstance(value, dict) and value.get("id"):
        yield "root", value
    else:
        raise PreviewError(f"--remote: taninmayan bicim: {source} (sayfa, kok kaydi ya da {{root, files}} beklenir)")

def _remote_entries(path: Path) -> tuple[dict[str, Any], list[Any]]:
    """--remote: {'root', 'files'} dosyasi ya da klasor (her dosya bir arac sonucu: kok kaydi ya da sayfa)."""
    target = Path(path)
    if not target.exists():
        raise PreviewError(f"--remote yok: {path}")
    sources = sorted(p for p in target.iterdir() if p.is_file() and p.suffix.lower() in (".json", ".txt")) \
        if target.is_dir() else [target]
    try:
        found = [item for source in sources for item in _payloads(_load_json(source, "--remote"), source)]
    except json.JSONDecodeError as exc:
        raise PreviewError(f"--remote: arac sonucu metni JSON degil ({exc})") from exc
    roots = {str(value.get("id")): value for kind, value in found if kind == "root"}
    if len(roots) > 1:
        raise PreviewError(f"--remote: birden fazla kok kaydi ({', '.join(sorted(roots))}); yalniz listelenen kok konur")
    return next(iter(roots.values()), {}), [value for kind, value in found if kind == "file"]

def _pick(item: dict[str, Any], field: str) -> Any:
    return next((item[key] for key in ALIASES[field] if item.get(key) not in (None, "")), None)

def _remote_item(item: Any) -> dict[str, Any]:
    path = str(item.get("path") or "").strip() if isinstance(item, dict) else ""
    if not isinstance(item, dict) or not item.get("id") or not (path or (_pick(item, "name") and item.get("parentId"))):
        raise PreviewError(f"--remote: her kayitta 'id' ve 'path' ya da 'title'+'parentId' zorunlu: {str(item)[:100]}")
    try:
        size = None if _pick(item, "size") is None else int(_pick(item, "size"))
    except (TypeError, ValueError) as exc:
        raise PreviewError(f"--remote: gecersiz boyut (size/fileSize): {str(item)[:100]}") from exc
    md5 = _pick(item, "md5")
    return {"path": norm_path(path) if path else None, "name": str(_pick(item, "name") or ""),
            "parent": item.get("parentId"), "id": str(item["id"]), "mimeType": str(item.get("mimeType") or ""),
            "size": size, "md5": str(md5).strip().lower() if md5 else None, "modifiedTime": item.get("modifiedTime"),
            "createdTime": item.get("createdTime"), "url": _pick(item, "url"), "revision": item.get("headRevisionId")}

def _with_paths(root_id: str | None, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Yolu olmayan kaydin yolu parentId zincirinden kurulur; zincir listelenen koke varmali."""
    by_id = {item["id"]: item for item in items}
    def path_of(item: dict[str, Any], depth: int = 0) -> str:
        if item["path"] is not None:
            return item["path"]
        if root_id and item["parent"] == root_id:
            return norm_path(item["name"])
        if item["parent"] not in by_id or depth > 30:
            raise PreviewError(f"--remote: koke baglanmayan kayit: {item['name']} (parentId {item['parent']}); kok kaydi "
                               "(get_file_metadata) ve her alt klasorun listesi gerekir")
        return f"{path_of(by_id[item['parent']], depth + 1)}/{norm_path(item['name'])}"
    return [{**item, "path": path_of(item)} for item in items]

def load_remote(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], int]:
    """Drive listesi -> (kok, klasorler, dosyalar, sayfa sinirinda yinelenen kayit sayisi)."""
    root, raw = _remote_entries(path)
    records = [item for item in map(_remote_item, raw) if item["id"] != str(root.get("id"))]
    unique: dict[str, dict[str, Any]] = {}
    for item in records:
        unique.setdefault(item["id"], item)  # ayni id ikinci kez: ayni dosya (sayfa siniri), cift yukleme degil
    items = _with_paths(root.get("id"), list(unique.values()))
    folders = [item for item in items if item["mimeType"] == FOLDER_MIME]
    return root, folders, [item for item in items if item["mimeType"] != FOLDER_MIME], len(records) - len(unique)

def load_downloads(path: Path | None) -> dict[str, dict[str, str]]:
    """indirilenler.json: [{path (Drive yolu), file (yerel dosya), format: raw|base64}] -> {yol: {...}}."""
    data = [] if path is None else _load_json(path, "--downloads")
    bad = [i for i in data if not isinstance(i, dict) or i.get("format") not in ("raw", "base64") or not i.get("path")
           or not i.get("file") or not Path(i["file"]).is_file()] if isinstance(data, list) else [data]
    if bad:
        raise PreviewError(f"--downloads: path, var olan file ve format (raw|base64) zorunlu: {str(bad[0])[:100]}")
    return {norm_path(i["path"]): {"file": str(i["file"]), "format": str(i["format"])} for i in data}

def _longest_text(value: Any, depth: int = 0) -> str:
    """JSON icindeki en uzun metin; JSON gibi gorunen metin de acilir (arac sonucu dosyasi ic ice JSON olabilir)."""
    if isinstance(value, (dict, list)):
        return max((_longest_text(item, depth) for item in (value.values() if isinstance(value, dict) else value)),
                   key=len, default="")
    text = value.strip() if isinstance(value, str) else ""
    try:
        return _longest_text(json.loads(text), depth + 1) if depth < 3 and text[:1] in ("[", "{", '"') else text
    except json.JSONDecodeError:
        return text

def downloaded_bytes(spec: dict[str, str]) -> bytes:
    """raw: dosyanin kendisi; base64: arac sonucundaki en uzun metin (ic ice JSON acilir), data: oneki atilir."""
    if spec["format"] == "raw":
        return Path(spec["file"]).read_bytes()
    text = _longest_text(Path(spec["file"]).read_text(encoding="utf-8-sig"))
    payload = re.sub(r"\s+", "", re.sub(r"^data:[^,]*;base64,", "", text))
    padded = payload + "=" * (-len(payload) % 4)
    try:
        return base64.b64decode(padded, validate=True)
    except (binascii.Error, ValueError):
        return base64.b64decode(padded.translate(str.maketrans("-_", "+/")), validate=True)  # URL-guvenli base64

def check_local_files(local: dict[str, dict[str, Any]], pkg: Path | None) -> None:
    """--pkg verildiyse envanterdeki her dosya pakette ayni boyutta olmali (eski envanterle karsilastirma olmaz)."""
    if pkg is not None and not Path(pkg).is_dir():
        raise PreviewError(f"--pkg klasoru yok: {pkg}")
    stale = [p for p, info in local.items() if pkg is not None
             and (not (pkg / info["disk"]).is_file() or (pkg / info["disk"]).stat().st_size != info["size"])]
    if stale:
        raise PreviewError(f"envanter paketle uyusmuyor ({len(stale)} dosya, ilk: {stale[0]}); envanteri yeniden alin")

def _download_sha(path: str, size: int | None, ctx: dict[str, Any]) -> tuple[str | None, str | None]:
    """(indirilen baytin SHA-256'si, indirme sorunu). Beklenen boyutu tutmayan indirme hash'e girmez."""
    spec = ctx["downloads"].get(path)
    if spec is None:
        return None, None
    try:
        data = downloaded_bytes(spec)
    except (OSError, UnicodeDecodeError, binascii.Error, ValueError) as exc:
        return None, f"okunamadi ({type(exc).__name__}): {spec['file']}"
    if size is not None and len(data) != size:
        return None, f"indirilen {len(data)} bayt, beklenen {size} bayt (eksik ya da bozuk indirme): {spec['file']}"
    return hashlib.sha256(data).hexdigest(), None

def _verdict(path: str, info: dict[str, Any] | None, remotes: list[dict[str, Any]], ctx: dict[str, Any]) -> dict[str, Any]:
    if path in ctx["zips"]:  # ekip akisi G.2: Lisans kanitlari tek ZIP olabilir (fazla degil)
        return {"method": "liste", "result": "kanit_zip"}
    if not remotes and info is not None and ctx["zips"] and path.startswith(EVIDENCE_DIR):
        return {"method": "zip", "result": "zipte_olabilir"}  # eksik degil ama Drive'da tek tek de gorunmuyor
    google = any(r["mimeType"].startswith(GOOGLE_NATIVE) for r in remotes)
    if not remotes or google or len(remotes) > 1 or info is None:
        return {"method": "liste", "result": "eksik" if not remotes else "google_bicimi" if google
                else "yinelenen_dosya" if len(remotes) > 1 else "fazla"}
    remote = remotes[0]
    if remote["size"] is not None and remote["size"] != info["size"]:
        return {"method": "boyut", "result": "boyut_farki"}
    sha, problem = _download_sha(path, info["size"], ctx)
    extra = {"indirme_sorunu": problem} if problem else {}
    if sha is not None:
        verdict = "sha256_dogrulandi" if sha == info["sha256"] else "sha256_farki"
        return {"method": "sha256", "remote_sha256": sha, "result": verdict}
    if remote["md5"] and ctx["pkg"] is not None:
        with (ctx["pkg"] / info["disk"]).open("rb") as stream:
            local_md5 = hashlib.file_digest(stream, lambda: hashlib.md5(usedforsecurity=False)).hexdigest()
        return {**extra, "method": "md5", "local_md5": local_md5,
                "result": "md5_eslesti" if local_md5 == remote["md5"] else "md5_farki"}
    sized = remote["size"] is not None
    return {**extra, "method": "ad+boyut" if sized else "ad", "result": "yalniz_ad_boyut" if sized else "yalniz_ad"}

def compare_files(local: dict[str, dict[str, Any]], files: list[dict[str, Any]], pkg: Path | None,
                  downloads: dict[str, dict[str, str]]) -> list[dict[str, Any]]:
    by_path: dict[str, list[dict[str, Any]]] = {}
    for item in files:
        by_path.setdefault(item["path"], []).append(item)
    zips = [p for p in by_path if p.startswith(EVIDENCE_DIR) and p.lower().endswith(".zip") and p not in local]
    ctx = {"pkg": Path(pkg) if pkg is not None else None, "downloads": downloads, "zips": zips}
    rows = []
    for path in sorted(set(local) | set(by_path)):
        info, remotes = local.get(path), by_path.get(path, [])
        first = remotes[0] if remotes else {}
        rows.append({"path": path, "local_size": info["size"] if info else None, "remote_size": first.get("size"),
                     "remote_id": [r["id"] for r in remotes] if len(remotes) > 1 else first.get("id"),
                     "remote_md5": first.get("md5"), "modifiedTime": first.get("modifiedTime"),
                     **_verdict(path, info, remotes, ctx)})
    return rows

def _folder_problems(folders: list[dict[str, Any]], files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_path: dict[str, list[str]] = {}
    for folder in folders:
        by_path.setdefault(folder["path"], []).append(folder["id"])
    implied = {"/".join(parts[:i]) for f in files for parts in [f["path"].split("/")] for i in range(1, len(parts))}
    top = sorted({p for p in set(by_path) | implied if "/" not in p})
    problems = [{"kind": "eksik_klasor", "ad": name} for name in EXPECTED_FOLDERS if name not in top]
    problems += [{"kind": "fazla_ust_klasor", "ad": p, "id": by_path.get(p, [])} for p in top if p not in EXPECTED_FOLDERS]
    problems += [{"kind": "yinelenen_klasor", "yol": p, "id": ids} for p, ids in sorted(by_path.items()) if len(set(ids)) > 1]
    groups: dict[tuple[str, str], set[str]] = {}
    for path in set(by_path) | implied:  # 'Lisans kanitlari' / 'Fotoğraflar 2' gibi benzer adli kardes klasorler
        parent, _, name = path.rpartition("/")
        groups.setdefault((parent, re.sub(r"[^a-z0-9]", "", COPY_MARK.sub(" ", fold(name)))), set()).add(path)
    return problems + [{"kind": "benzer_adli_klasor", "yollar": sorted(g)} for _, g in sorted(groups.items()) if len(g) > 1]

def structure_problems(root: dict[str, Any], folders: list[dict[str, Any]], files: list[dict[str, Any]],
                       excel_name: str | None) -> list[dict[str, Any]]:
    """K01/K109: kokte tek Excel (beklenen adla), tam uc klasor, fazla/yinelenen/benzer klasor, kok adinda CITY kodu+slug."""
    problems = _folder_problems(folders, files)
    root_xlsx = sorted({f["path"] for f in files if _is_root_xlsx(f["path"])})
    if not root_xlsx:
        problems.append({"kind": "kokte_excel_yok"})
    elif len(root_xlsx) > 1:
        problems.append({"kind": "birden_fazla_excel", "adlar": root_xlsx})
    elif excel_name and root_xlsx[0] != norm_path(excel_name):
        problems.append({"kind": "excel_adi_farkli", "beklenen": excel_name, "bulunan": root_xlsx[0]})
    code, name = CITY_EXCEL.match(Path(excel_name or "").name), fold(_pick(root, "name") or "")
    if code and not all(re.search(rf"(?<!\w){re.escape(fold(part))}(?!\w)", name) for part in code.groups()):
        problems.append({"kind": "kok_adi_uyumsuz", "beklenen": list(code.groups()), "bulunan": _pick(root, "name")})
    return problems

def root_identity(root: dict[str, Any], expected: str | None, source: str | None) -> dict[str, Any]:
    """K109: listelenen kokun kimligi bagimsiz kaynaktakiyle (yonetim karti ya da uretim promptu) ayni mi."""
    found = root.get("id")
    if not expected:
        return {"durum": "beklenen_yok", "bulunan": found}
    return {"durum": "eslesti" if found == expected else "farkli", "beklenen": expected, "kaynak": source, "bulunan": found}

def id_map(root: dict[str, Any], folders: list[dict[str, Any]], files: list[dict[str, Any]]) -> dict[str, Any]:
    top: dict[str, list[str]] = {}
    for folder in (f for f in folders if "/" not in f["path"]):
        top.setdefault(folder["path"], []).append(folder["id"])
    excel = next((f for f in files if _is_root_xlsx(f["path"])), None)
    keys = ("path", "id", "size", "md5", "modifiedTime", "createdTime", "revision", "url")
    kok = {"id": root.get("id"), "name": _pick(root, "name"), "url": _pick(root, "url"), "createdTime": root.get("createdTime")}
    return {"kok": kok, "excel": {k: excel[k] for k in keys} if excel else None, "klasorler": top}

def id_changes(current: dict[str, Any], previous: Path | None) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """K109 'guncellemede kimlikler korunmus': onceki _ONIZLEME kosusunun id_map'iyle kok, Excel ve klasor kimlikleri."""
    if previous is None:
        return None, []
    data = _load_json(previous, "--previous")
    old = data.get("id_map") if isinstance(data, dict) else None
    if not isinstance(old, dict):
        raise PreviewError(f"--previous: drive-compare ciktisi degil (id_map yok): {previous}")
    pairs = [("kok", (old.get("kok") or {}).get("id"), current["kok"].get("id")),
             ("excel", (old.get("excel") or {}).get("id"), (current["excel"] or {}).get("id"))]
    pairs += [(f"klasor:{name}", sorted(ids), sorted(current["klasorler"].get(name, [])))
              for name, ids in (old.get("klasorler") or {}).items()]
    changed = [{"kind": "kimlik_degisti", "oge": what, "onceki": was, "simdi": now} for what, was, now in pairs
               if was and was != now]
    return {"dosya": str(previous), "checked_at": data.get("checked_at"), "degisen": len(changed)}, changed

def drive_summary(local: dict[str, Any], files: list[dict[str, Any]], folders: list[dict[str, Any]],
                  rows: list[dict[str, Any]], problems: list[dict[str, Any]], repeats: int) -> dict[str, Any]:
    counts = Counter(row["result"] for row in rows)
    summary = {"local_files": len(local), "remote_files": len(files), "remote_folders": len(folders),
               "eslesen": len(set(local) & {f["path"] for f in files}),
               "icerik_dogrulanan": sum(counts[k] for k in VERIFIED_RESULTS),
               **{k: counts[k] for k in (*VERIFIED_RESULTS, *UNVERIFIED_RESULTS, "kanit_zip", *FINDING_RESULTS)},
               "yapi": len(problems), "indirme_sorunu": sum(1 for r in rows if r.get("indirme_sorunu")), "yinelenen_kayit": repeats}
    return {**summary, "findings": sum(counts[k] for k in FINDING_RESULTS) + len(problems)}

def drive_lists(rows: list[dict[str, Any]]) -> dict[str, Any]:
    def pick(*results: str) -> list[str]:
        return [row["path"] for row in rows if row["result"] in results]
    return {"eksik": pick("eksik"), "fazla": pick("fazla"), "farkli": pick(*DIFFER_RESULTS),
            "dogrulanmayan": pick(*UNVERIFIED_RESULTS),
            "sha256_beklenen": [row["path"] for row in rows if row["path"].lower().endswith(SHA_EXPECTED)
                                and row["result"] not in ("eksik", "fazla", "sha256_dogrulandi")],
            "indirme_sorunlari": [{"path": r["path"], "sorun": r["indirme_sorunu"]} for r in rows if r.get("indirme_sorunu")]}

def run_drive(args: argparse.Namespace) -> int:
    if args.root_id and not args.root_source:
        raise PreviewError("--root-id icin --root-source (yonetim|prompt) zorunlu: kimlik bagimsiz kaynaktan gelir")
    _guard_out(args.out, (args.local, args.remote, args.downloads, args.previous), args.package_root)
    local = load_local(args.local)
    check_local_files(local, args.package_root)
    root, folders, files, repeats = load_remote(args.remote)
    rows = compare_files(local, files, args.package_root, load_downloads(args.downloads))
    excel_name = args.excel_name or next((p for p in sorted(local) if _is_root_xlsx(p)), None)
    identity, ids = root_identity(root, args.root_id, args.root_source), id_map(root, folders, files)
    previous, changed = id_changes(ids, args.previous)
    problems = structure_problems(root, folders, files, excel_name) + changed
    problems += [{"kind": "kok_kimligi_farkli", **identity}] if identity["durum"] == "farkli" else []
    excel = local.get(norm_path(excel_name)) if excel_name else None
    report = {"tool": f"{TOOL} drive-compare", "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
              "method": METHOD_NOTE, "summary": drive_summary(local, files, folders, rows, problems, repeats),
              "id_map": ids, "kok_kimligi": identity, "onceki_kimlik": previous,
              "excel_yerel": {"path": norm_path(excel_name), "size": excel["size"], "sha256": excel["sha256"]}
              if excel else None, "yapi": problems, "files": rows, **drive_lists(rows)}
    return _finish(args.out, report, f"{TOOL} drive-compare")

# --- warning-scan (K103, K104) ---
BAND_FIELDS = ("overlay", "status_note", "venue_editorial", "visit_status",  # fotograf ustunde bant ya da rozet
               "hero_kicker", "hero_accent", "hero_note", "photo_credit")  # SayfaAlanlari: kapak fotografinin ustu
K103_FIELDS = (*BAND_FIELDS, "caption")
K104_FIELDS = ("note", "summary", "subtitle", "steps", "description", "intro", "tagline")
SCAN_FIELDS = K103_FIELDS + K104_FIELDS
KEYED_SHEETS = ("EkDetaylar", "SayfaAlanları")  # alan adi 'key', metin 'value' sutununda
PRIMARY_KEY = {"Fotoğraflar": "photo_id", "FotoğrafKaynakları": "photo_id", "EkDetaylar": "detail_id", "Rotalar": "route_id",
               "Adımlar": "step_id", "Bağlantılar": "action_id", "Sözlük": "term_id", "Kaynaklar": "source_id",
               "Kanıtlar": "evidence_id", "SayfaAlanları": "field_id", "Konular": "topic_id"}
_CHECK = r"(?:kontrol|teyit) (?:et|edin|ediniz|etmelisin|etmelisiniz|etmeli|edilmeli|edilmelidir)"
_VERIFY = r"dogrula(?:yin|yiniz|malisin|malisiniz|nmali|nmalidir)?"
_LOOK = r"(?:bak|bakin|bakiniz|goz at|goz atin|goz atiniz)"
_ANY = rf"(?:{_CHECK}|{_VERIFY})\b"
_ANY_LOOK = rf"(?:{_CHECK}|{_VERIFY}|{_LOOK})\b"
_INFO = r"(?:bilgi|saat|ucret|fiyat|tarih|durum|program|acilis|kapanis|takvim|kosul)\w*"
_SOURCE = r"(?:(?:site|sayfa|kaynak|uygulama|duyuru)\w*|hesa(?:p|b\w*)(?:tan|dan|den))"  # hesap yalniz -dan: 'hesabi
# kontrol et' hesaplamayi denetlemektir; site/sayfa her hal ekiyle (siteden, siteyi, siteye, sayfasini)
ORDER = re.compile(rf"\b{_ANY_LOOK}")  # bant alaninda baglamindan bagimsiz her denetim emri
HARD = {name: re.compile(pattern) for name, pattern in {  # her zaman bulgu
    "tekrar_kontrol": rf"\b(?:tekrar|yeniden|bir kez daha) {_ANY}",
    "kurumdan_dogrula": rf"\bkurum\w*(?:dan|den|la|le)\b(?: \w+){{0,3}} {_ANY}"
                        rf"|\bkurum\w*(?: \w+){{0,2}} (?:site|sayfa)\w*(?:den|dan)\b(?: \w+){{0,3}} {_ANY}",
    "arsiv_olabilir": r"\barsiv\w*(?: \w+){0,2} olabilir\b",
    # 'kaldirilmis olabilir' yok: Eindhoven'da 'bisikletin belediyece kaldirilmis olabilir' kaydin durumu degil, bilgidir
    "belirsiz_durum": r"\b(?:guncel|gecerli) olmayabilir\b|\b(?:degismis|kapanmis|tasinmis) olabilir\b",
    "editor_notu": r"\b(?:todo|tbd|fixme|editor notu|editore not)\b",
}.items()}
SOFT = {name: re.compile(pattern) for name, pattern in {  # gun-ay/tam tarih + somut durum cumlesinde muaf (bant haric)
    "gitmeden_kontrol": rf"\b(?:gitmeden|gelmeden|yola cikmadan|bilet almadan|ziyaret\w*(?: etmeden)? once\w*)\b"
                        rf"(?: \w+){{0,6}} {_ANY_LOOK}",
    "kaynaktan_dogrula": rf"\b(?:resmi|guncel)\b(?: \w+){{0,4}} {_SOURCE}\b(?: \w+){{0,4}} {_ANY_LOOK}",
    "siteden_bilgi_dogrula": rf"\b{_INFO}\b(?: \w+){{0,5}} {_SOURCE}\b(?: \w+){{0,3}} {_ANY}"
                             rf"|\b{_SOURCE}\b(?: \w+){{0,4}} {_INFO}\b(?: \w+){{0,3}} {_ANY}",
    # 'guncel kosullari ... kontrol et' (Berlin 168 kez); 'kaydinin guncel oldugunu kontrol et' kendi kaydini denetler
    "guncel_kontrol": rf"\bguncel\w*(?!(?: \w+){{0,3}} oldugunu\b)(?: \w+){{0,8}} {_ANY}",
}.items()}
BARE = re.compile(rf"(?:lutfen )?(?:bunu |bilgileri |bilgiyi |tekrar )?(?:{_CHECK}|{_VERIFY})")  # cumlenin tamami
_MONTHS = "ocak|subat|mart|nisan|mayis|haziran|temmuz|agustos|eylul|ekim|kasim|aralik"
DATE_RAW = re.compile(r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b")
DATE_FOLDED = re.compile(rf"\b\d{{1,2}} (?:{_MONTHS})\w*")  # gun + ay; tek basina yil yetmez
STATUS = re.compile(r"\b(?:kapali|kapanis|kapan(?:di|acak|iyor)|tadilat|renovasyon|insaat|rezervasyon|yeniden acil)\w*")
# yalniz kapanis/tadilat/rezervasyon ailesi: 'bilet' ve 'yenileme' (kayit yenileme de olabilir) somut durum degil
SENTENCE = re.compile(r"(?<=[.!?])\s+|\n+")

def sentence_patterns(sentence: str, band: bool = False) -> tuple[list[str], list[str]]:
    """(bulgu, muaf). Bantta muaflik yok, her emir 'bant_emri'; digerinde muaf: gun-ay/tam tarih VE somut durum."""
    folded = fold(sentence)
    hard = [name for name, rx in HARD.items() if rx.search(folded)]
    soft = [name for name, rx in SOFT.items() if rx.search(folded)]
    if band:
        return hard + soft + (["bant_emri"] if ORDER.search(folded) else []), []
    concrete = bool(DATE_RAW.search(sentence) or DATE_FOLDED.search(folded)) and bool(STATUS.search(folded))
    hits, exempt = hard + ([] if concrete else soft), (soft if concrete else [])
    return (["yalin_uyari"] if not hits and not exempt and BARE.fullmatch(folded) else hits), exempt

def scan_value(text: str, band: bool = False) -> dict[str, list[str]]:
    """{'hits', 'hit_sentences', 'exempt', 'exempt_sentences'}: cumle cumle kaliplar."""
    result: dict[str, list[str]] = {"hits": [], "hit_sentences": [], "exempt": [], "exempt_sentences": []}
    for sentence in filter(None, (part.strip() for part in SENTENCE.split(text))):
        for kind, new in zip(("hits", "exempt"), sentence_patterns(sentence, band)):
            if new:
                result[kind].extend(name for name in new if name not in result[kind])
                result[f"{kind.removesuffix('s')}_sentences"].append(_clip(sentence))
    return result

def load_scan_records(xlsx: Path) -> tuple[list[tuple[str, dict[str, Any]]], list[str]]:
    try:
        wb = openpyxl.load_workbook(xlsx, data_only=False)
    except (OSError, zipfile.BadZipFile, InvalidFileException, KeyError, ValueError) as exc:
        raise PreviewError(f"xlsx okunamadi: {xlsx} ({type(exc).__name__}: {exc})") from exc
    records, skipped = [], []  # (sayfa, kayit), atlanan sayfa nedenleri
    try:
        for ws in (ws for ws in wb.worksheets if ws.title in common.DATA_SHEETS):
            try:
                records.extend((ws.title, record) for record in common.iter_records(ws))
            except ValueError as exc:
                skipped.append(f"{ws.title}: {exc}")
    finally:
        wb.close()
    return records, skipped

def _field_values(sheet: str, record: dict[str, Any]) -> list[tuple[str, str]]:
    """(alan, metin). SayfaAlanlari: kapak metni bant, diger metin K104; JSON/URL ve '_' (Berlin _db_) anahtari yok."""
    if sheet not in KEYED_SHEETS:
        return [(field, record[field]) for field in SCAN_FIELDS if isinstance(record.get(field), str)]
    key, value = str(record.get("key") or ""), record.get("value")
    page_text = sheet == "SayfaAlanları" and not str(value).lstrip().startswith(("[", "{", "http"))
    return [(key, value)] if isinstance(value, str) and not key.startswith("_") and (key in SCAN_FIELDS or page_text) else []

def _hit_base(sheet: str, record: dict[str, Any], field: str) -> dict[str, Any]:
    """Sayfanin kendi kimligi (Fotoğraflar: photo_id, EkDetaylar: detail_id ...) + bagli kart (entry_id)."""
    record_id = str(record.get(PRIMARY_KEY.get(sheet, "entry_id")) or record.get("entry_id") or f"{sheet}!{record.get('_row')}")
    base = {"sheet": sheet, "row": record.get("_row"), "id": record_id, "field": field}
    entry = str(record.get("entry_id") or "")
    return {**base, "entry_id": entry} if entry and entry != record_id else base

def scan_records(records: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
    hits, exempt, bands, values = [], [], [], 0
    for sheet, record in records:
        for field, text in _field_values(sheet, record):
            values += 1
            base = _hit_base(sheet, record, field)
            if field in BAND_FIELDS and text.strip():
                bands.append({**base, "value": _clip(text)})
            result = scan_value(text, field in BAND_FIELDS)
            if result["hits"]:
                hits.append({**base, "check": "K103" if field in K103_FIELDS else "K104", "patterns": result["hits"],
                             "sentences": result["hit_sentences"][:3]})
            if result["exempt"]:
                exempt.append({**base, "patterns": result["exempt"], "sentences": result["exempt_sentences"][:3],
                               "reason": "tarihli somut durum bilgisi (kapanis/rezervasyon/tadilat)"})
    return {"hits": hits, "exempt": exempt, "band_values": bands, "values": values, "records": len(records)}

def scan_summary(scan: dict[str, Any], skipped: list[str]) -> dict[str, Any]:
    by_pattern = Counter(name for hit in scan["hits"] for name in hit["patterns"])
    return {"records": scan["records"], "values": scan["values"], "hits": len(scan["hits"]),
            "hit_records": len({(hit["sheet"], hit["row"]) for hit in scan["hits"]}), "exempt": len(scan["exempt"]),
            "by_check": {check: sum(1 for hit in scan["hits"] if hit["check"] == check) for check in ("K103", "K104")},
            "by_pattern": dict(sorted(by_pattern.items())), "band_values": len(scan["band_values"]),
            "skipped_sheets": skipped, "findings": len(scan["hits"])}

def run_scan(args: argparse.Namespace) -> int:
    if not args.xlsx.is_file():
        raise PreviewError(f"xlsx yok: {args.xlsx}")
    _guard_out(args.out, (args.xlsx,), _package_of(args.xlsx))
    records, skipped = load_scan_records(args.xlsx)
    scan = scan_records(records)
    samples: dict[str, list[str]] = {}
    for name, hit in ((name, hit) for hit in scan["hits"] for name in hit["patterns"]):  # kalip basina en cok 5 kayit
        samples.setdefault(name, []).extend([] if hit["id"] in samples[name] or len(samples[name]) >= 5 else [hit["id"]])
    report = {"tool": f"{TOOL} warning-scan", "workbook": args.xlsx.name,
              "fields": {"bant": list(BAND_FIELDS), "K103": list(K103_FIELDS), "K104": [*K104_FIELDS, "SayfaAlanları"]},
              "summary": scan_summary(scan, skipped), "samples": samples, "hits": scan["hits"], "exempt": scan["exempt"],
              "band_values": scan["band_values"]}
    return _finish(args.out, report, f"{TOOL} warning-scan")

# --- report (ONIZLEME_OZETI.md) ---
RESULTS = ("GEÇTİ", "KALDI", "KONTROL EDİLEMEDİ", "UYGULANMAZ")
NEEDS_EVIDENCE, NEEDS_REASON = ("GEÇTİ", "KALDI"), ("KONTROL EDİLEMEDİ", "UYGULANMAZ")
PAGE_CHECKS = ("K92", "K93", "K94", "K103", "K112")  # sehir sayfasi gorulmeden GEÇTİ olamaz
NOT_NA = ("K01", "K03", "K92", "K94", "K109", "K110", "K111")  # her pakette uygulanir; kilavuz yoksa ne yazilacagini soyler
FLOWS = {"K93": ("arama_filtre", "kart_acma", "islem_butonu", "rota_duraklari", "adimlar", "kisayollar", "butce_takvim"),
         "K112": ("kaydet_kaldir", "mahalle_karsilastirma", "gezi_listesi", "butce", "takvim_ics")}  # kilavuz K93/K112
EXTRA_FLOW = "diger"
DECISION = re.compile(r"\byayina (?:hazir|uygun|alin\w*)\b|\byay(?:im|in)lan(?:di|abilir|mistir|maya hazir)\b|\byayinda\b"
                      r"|\byayin icin (?:hazir|uygun)\b|\bcanli(?:ya alin\w*|da)\b|\bkabul edil(?:di|mistir)\b"
                      r"|\bonay(?:landi|lanmistir|li|i verildi)\b|\binceleme tamamlandi\b"
                      r"|\b(?:approved|published|ready to publish)\b")
QUOTED = re.compile(r"«[^»]*»|“[^”]*”|\"[^\"]*\"")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
SECRET = re.compile(r"\b(?:\w*token|csrf\w*|parola|password|passwd|şifre|sifre|secret|api[_-]?key)\s*[:=]\s*\S+", re.I)
URL = re.compile(r"^https?://", re.I)
SECTIONS = {"KALDI": ("Kalan maddeler (KALDI)", "gozlem"), "KONTROL EDİLEMEDİ": ("Kontrol edilemeyenler", "gerekce")}

def read_checks(path: Path | None = None) -> tuple[dict[str, str], list[str], list[str]]:
    """checks.yaml -> ({id: baslik}, scope drive-manual + preview-later kimlikleri, drive-manual kimlikleri)."""
    source = Path(path or DEFAULT_CHECKS)
    try:
        data = yaml.safe_load(source.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
        raise PreviewError(f"checks.yaml okunamadi: {source} ({type(exc).__name__})") from exc
    checks = [c for c in data.get("checks", []) if isinstance(c, dict) and c.get("id")] if isinstance(data, dict) else []
    scope = [c["id"] for c in checks if c.get("scope") in PREVIEW_SCOPES]
    if not scope:
        raise PreviewError(f"checks.yaml'da scope drive-manual/preview-later kontrolu yok: {source}")
    return {c["id"]: str(c.get("title") or "") for c in checks}, scope, [c["id"] for c in checks
                                                                          if c.get("scope") == DRIVE_SCOPE]

def load_scope(path: Path | None = None) -> dict[str, str]:
    titles, scope, _ = read_checks(path)
    return {cid: titles[cid] for cid in scope}

def _as_list(value: Any) -> list[str]:
    items = value if isinstance(value, list) else [value]
    return [str(item).strip() for item in items if item is not None and str(item).strip()]

def decision_words(text: Any) -> list[str]:
    """Tirnak (« », “ ”, \"...\") disindaki karar ifadeleri; tirnak icindeki metin ekranda gorulenin aktarimidir."""
    return [m.group(0) for m in DECISION.finditer(fold(QUOTED.sub(" ", text)))] if isinstance(text, str) else []

def _sensitive(where: str, values: Iterable[Any]) -> list[str]:
    """K113: kisisel veri (e-posta) ve gorulen parola/token rapora kopyalanmaz."""
    texts = [str(value) for value in values if value is not None]
    return [f"{where}: {what} var; rapora kopyalanmaz (K113)" for what, rx in
            (("e-posta (kişisel veri)", EMAIL), ("parola/token gibi gizli değer", SECRET)) if any(rx.search(t) for t in texts)]

def _missing_evidence(items: list[str], out_dir: Path) -> list[str]:
    return [item for item in items if not URL.match(item)
            and not (Path(item) if Path(item).is_absolute() else out_dir / item).is_file()]

def _check_problems(check: dict[str, Any], allowed: set[str], out_dir: Path) -> list[str]:
    cid, result, evidence = check.get("id"), check.get("sonuc"), _as_list(check.get("kanit"))
    problems = [] if cid in allowed else [f"{cid}: bu skill'in kontrolü değil (izinli: {sorted(allowed)})"]
    if result not in RESULTS:
        problems.append(f"{cid}: sonuç '{result}' geçersiz (yalnız {' / '.join(RESULTS)})")
    if result in NEEDS_EVIDENCE and not evidence:
        problems.append(f"{cid}: {result} için kanıt (ekran yolu, dosya ya da URL) zorunlu")
    problems += [f"{cid}: kanıt bulunamadı: {item}" for item in _missing_evidence(evidence, out_dir)]
    if result in NEEDS_REASON and not str(check.get("gerekce") or "").strip():
        problems.append(f"{cid}: {result} için gerekçe zorunlu")
    if result == "UYGULANMAZ" and cid in NOT_NA:
        problems.append(f"{cid}: UYGULANMAZ olamaz (her pakette uygulanır; yapılamadıysa KONTROL EDİLEMEDİ, "
                        "uygulamada atıf/işlev yoksa açık teknik iş: KALDI)")
    texts = [check.get("gozlem"), check.get("gerekce")]
    return problems + _sensitive(str(cid), [*texts, *evidence]) + [
        f"{cid}: karar ifadesi '{word}' (karar insanın; ekranda görüleni «...» içinde aktarın)"
        for text in texts for word in decision_words(text)]

def _coverage_problems(passed: set[str], coverage: dict[str, Any]) -> list[str]:
    problems = [] if "K111" not in passed or coverage.get("yonetim") else ["K111 GEÇTİ ama yönetim ekranı okunmadı"]
    if not (coverage.get("masaustu") or coverage.get("mobil")):
        return problems + [f"{cid} GEÇTİ ama şehir sayfası görülmedi (kapsam.masaustu/mobil)" for cid in PAGE_CHECKS
                           if cid in passed]
    if "K92" in passed and not (coverage.get("masaustu") and coverage.get("mobil")):
        problems.append("K92 GEÇTİ için masaüstü ve mobil görünümün ikisi de gerekli")
    return problems

def _scenario_problems(scenarios: list[Any], out_dir: Path) -> list[str]:
    problems = []
    for index, item in enumerate(s if isinstance(s, dict) else {} for s in scenarios):
        cid, result = item.get("kontrol"), item.get("sonuc")
        where = f"senaryo {index + 1} ({cid}/{item.get('islev')})"
        if cid not in FLOWS or result not in RESULTS:
            problems.append(f"{where}: kontrol {'/'.join(FLOWS)} ve sonuç {'/'.join(RESULTS)} olmalı")
        elif item.get("islev") not in (*FLOWS[cid], EXTRA_FLOW):
            problems.append(f"{where}: islev {' / '.join(FLOWS[cid])} ya da {EXTRA_FLOW} olmalı")
        screen = _as_list(item.get("ekran"))
        if result in NEEDS_EVIDENCE and (not screen or _missing_evidence(screen, out_dir)):
            problems.append(f"{where}: {result} için var olan ekran görüntüsü zorunlu")
        values = [item.get(key) for key in ("senaryo", "girdi", "beklenen", "gozlenen", "ekran")]
        problems += _sensitive(where, values) + [f"{where}: karar ifadesi '{w}'" for v in values for w in decision_words(v)]
    return problems

def _flow_problems(scenarios: list[Any], by_id: dict[str, dict[str, Any]]) -> list[str]:
    """K93/K112 GEÇTİ: kilavuzdaki her islevin GEÇTİ senaryosu var ve o maddede GEÇTİ olmayan senaryo yok."""
    problems = []
    for cid in (c for c in FLOWS if by_id.get(c, {}).get("sonuc") == "GEÇTİ"):
        mine = [s for s in scenarios if isinstance(s, dict) and s.get("kontrol") == cid]
        missing = [f for f in FLOWS[cid] if f not in {s.get("islev") for s in mine if s.get("sonuc") == "GEÇTİ"}]
        others = sorted({f"{s.get('islev')}={s.get('sonuc')}" for s in mine if s.get("sonuc") != "GEÇTİ"})
        problems += [f"{cid} GEÇTİ ama GEÇTİ senaryosu olmayan işlev: {', '.join(missing)}"] if missing else []
        problems += [f"{cid} GEÇTİ ama GEÇTİ olmayan senaryo var: {', '.join(others)}"] if others else []
    return problems

def _drive_problems(passed: set[str], drive: dict[str, Any] | None, drive_ids: list[str]) -> list[str]:
    """Drive maddelerinde GEÇTİ, drive-compare kanitiyla celismemeli; kanit (--drive) yoksa GEÇTİ olamaz."""
    if drive is None:
        return [f"{cid} GEÇTİ ama Drive ölçülmedi (--drive yok): Drive maddesi KONTROL EDİLEMEDİ yazılır"
                for cid in drive_ids if cid in passed]
    s, kinds = drive["summary"], {p.get("kind") for p in drive.get("yapi", [])} & set(K01_KINDS)
    differ, unseen = sum(s.get(k, 0) for k in DIFFER_RESULTS), s.get("yalniz_ad", 0) + s.get("zipte_olabilir", 0)
    excel, root = (drive.get("excel_yerel") or {}).get("path"), (drive.get("kok_kimligi") or {}).get("durum")
    verified = any(r.get("path") == excel and r.get("result") in VERIFIED_RESULTS for r in drive.get("files", []))
    rules = {"K01": (not verified or kinds, f"ana Excel hash'le doğrulanmadı ya da kök/Excel tutarsız ({excel}; "
                                            f"{sorted(kinds)})"),
             "K03": (differ or not verified, f"farklı {differ} ya da ana Excel hash'le doğrulanmadı ({excel})"),
             "K109": (s.get("yapi", 0) or root != "eslesti", f"yapı bulgusu {s.get('yapi', 0)} ya da kök kimliği bağımsız "
                                                              f"kaynakla eşleşmedi ({root})"),
             "K110": (s.get("eksik", 0) or s.get("fazla", 0) or differ or unseen,
                      f"eksik {s.get('eksik', 0)}, fazla {s.get('fazla', 0)}, farklı {differ}, boyutsuz ya da ZIP'te "
                      f"doğrulanmayan {unseen} (en az ID/ad/boyut gerekir)")}
    return [f"{cid} GEÇTİ ama {text}" for cid, (bad, text) in rules.items() if cid in passed and bad]

def validate_results(data: Any, scope: dict[str, str], out_dir: Path, drive: dict[str, Any] | None = None,
                     drive_ids: list[str] | None = None) -> list[str]:
    if not isinstance(data, dict) or not isinstance(data.get("kontroller"), list):
        return ["sonuclar.json: 'kontroller' listesi zorunlu"]
    problems = [f"'{key}' zorunlu" for key in ("sehir", "ortam") if not str(data.get(key) or "").strip()]
    checks = [check if isinstance(check, dict) else {} for check in data["kontroller"]]
    ids = [check.get("id") for check in checks]
    problems += [f"{cid}: birden fazla kez yazılmış" for cid, n in Counter(ids).items() if n > 1]
    problems += [f"{cid}: eksik (her kontrol yazılır; yapılamayan KONTROL EDİLEMEDİ)" for cid in scope if cid not in ids]
    problems += [p for check in checks for p in _check_problems(check, set(scope) | set(OPTIONAL_CHECKS), out_dir)]
    by_id = {check.get("id"): check for check in checks}
    passed = {cid for cid, check in by_id.items() if check.get("sonuc") == "GEÇTİ"}
    coverage = data.get("kapsam") if isinstance(data.get("kapsam"), dict) else {}
    scenarios = data.get("senaryolar") if isinstance(data.get("senaryolar"), list) else []
    problems += _coverage_problems(passed, coverage) + _scenario_problems(scenarios, out_dir)
    problems += _flow_problems(scenarios, by_id) + _drive_problems(passed, drive, drive_ids or [])
    notes = _as_list(data.get("notlar"))
    return problems + _sensitive("not", notes) + [f"not: karar ifadesi '{w}'" for note in notes for w in decision_words(note)]

def _cell(text: Any) -> str:
    return " ".join(str(text or "").split()).replace("|", "\\|")

def first_line(data: dict[str, Any], counts: dict[str, int], drive_text: str) -> str:
    """ONIZLEME_OZETI.md ilk satiri; karar kelimesi yok (yayin karari insanin). ' | ' ayiricisi metinde '/' olur."""
    coverage = data.get("kapsam") if isinstance(data.get("kapsam"), dict) else {}
    seen = {key: "var" if coverage.get(key) else "yok" for key in ("masaustu", "mobil")}
    flat = {key: " ".join(str(data.get(key) or "").split()).replace("|", "/") for key in ("sehir", "ortam")}
    result = f"Sonuç: {counts['GEÇTİ']}/{sum(counts.values()) - counts['UYGULANMAZ']}, KALDI {counts['KALDI']}, " \
             f"KONTROL EDİLEMEDİ {counts['KONTROL EDİLEMEDİ']}"
    return " | ".join([f"Önizleme kontrolü: {flat['sehir']}", f"Ortam: {flat['ortam']}",
                       f"Kapsam: {drive_text}, yönetim ekranı {'okundu' if coverage.get('yonetim') else 'okunmadı'}, "
                       f"şehir sayfası (masaüstü {seen['masaustu']}/mobil {seen['mobil']})",
                       result + (f", UYGULANMAZ {counts['UYGULANMAZ']}" if counts["UYGULANMAZ"] else "")])

def load_drive(path: Path | None) -> tuple[str, dict[str, Any] | None]:
    if path is None:
        return "Drive ölçülmedi", None
    data = _load_json(path, "--drive")
    summary = data.get("summary") if isinstance(data, dict) else None
    if not isinstance(summary, dict) or "icerik_dogrulanan" not in summary:
        raise PreviewError("--drive: drive-compare ciktisi degil")
    return f"Drive {summary['icerik_dogrulanan']}/{summary.get('local_files', 0)}", data

def _meta_lines(data: dict[str, Any], drive: dict[str, Any] | None) -> list[str]:
    urls = data.get("adresler") if isinstance(data.get("adresler"), dict) else {}
    lines = [f"- Adres ({_cell(name)}): {_cell(url)}" for name, url in urls.items() if url]
    lines += [f"- Kontrol zamanı: {_cell(data['zaman'])}"] if data.get("zaman") else []
    if not drive:
        return lines
    s, local = drive["summary"], drive.get("excel_yerel") or {}
    root, before = drive.get("kok_kimligi") or {}, drive.get("onceki_kimlik")
    lines += [f"- Yerel Excel: {local.get('path')} · SHA-256 {local.get('sha256')}"] if local else []
    return lines + [
        f"- Drive karşılaştırması ({drive.get('checked_at')}): içerik hash'iyle doğrulanan {s['icerik_dogrulanan']}/"
        f"{s.get('local_files', 0)} (SHA-256 {s.get('sha256_dogrulandi', 0)}, MD5 {s.get('md5_eslesti', 0)}), yalnız "
        f"ad/boyut {s.get('yalniz_ad_boyut', 0)} (hash doğrulaması değil), boyutsuz {s.get('yalniz_ad', 0)}, ZIP'te "
        f"doğrulanmayan {s.get('zipte_olabilir', 0)}, eksik {s.get('eksik', 0)}, fazla {s.get('fazla', 0)}, farklı "
        f"{sum(s.get(k, 0) for k in DIFFER_RESULTS)}, yapı bulgusu {s.get('yapi', 0)}",
        f"- Kök kimliği: {root.get('durum')} (beklenen {root.get('beklenen') or '-'}, kaynak {root.get('kaynak') or '-'}, "
        f"bulunan {root.get('bulunan')}); önceki koşu: "
        + (f"{before.get('degisen')} kimlik değişti ({before.get('checked_at')})" if before else "yok")]

def _tables(data: dict[str, Any], titles: dict[str, str]) -> list[str]:
    order = {cid: index for index, cid in enumerate(titles)}
    lines = ["| Kontrol | Başlık | Sonuç | Kanıt | Gözlem / gerekçe |", "|---|---|---|---|---|"]
    for check in sorted(data["kontroller"], key=lambda c: order.get(c["id"], len(order))):
        note = " · ".join(_as_list([check.get("gozlem"), check.get("gerekce")]))
        lines.append(f"| {check['id']} | {_cell(titles.get(check['id'], ''))} | {check['sonuc']} | "
                     f"{'<br>'.join(_cell(e) for e in _as_list(check.get('kanit')))} | {_cell(note)} |")
    scenarios = [s for s in data.get("senaryolar") or [] if isinstance(s, dict)]
    keys = ("kontrol", "islev", "senaryo", "girdi", "beklenen", "gozlenen", "sonuc", "ekran")
    lines += ["", "## Senaryolar (K93, K112; yalnız sentetik veri)", "", "| Kontrol | İşlev | Senaryo | Girdi | Beklenen | "
              "Gözlenen | Sonuç | Ekran |", "|---|---|---|---|---|---|---|---|"] if scenarios else []
    return lines + ["| " + " | ".join(_cell(item.get(key)) for key in keys) + " |" for item in scenarios]

def render(data: dict[str, Any], titles: dict[str, str], counts: dict[str, int], drive_text: str,
           drive: dict[str, Any] | None) -> str:
    lines = [first_line(data, counts, drive_text), "Bu özet kanıt listesidir; yayın kararı ve insan onayı ekibindir. "
             "Yönetim ekranında yenileme içerik aktarımı değildir.", ""]
    lines += _meta_lines(data, drive) + [""] + _tables(data, titles)
    for result, (heading, field) in SECTIONS.items():
        items = [c for c in data["kontroller"] if c["sonuc"] == result]
        lines += ["", f"## {heading}", ""] + [f"- {c['id']}: {_cell(c.get(field) or c.get('gozlem'))}" for c in items] \
            if items else []
    notes = _as_list(data.get("notlar"))
    lines += ["", "## Notlar", ""] + [f"- {_cell(note)}" for note in notes] if notes else []
    return "\n".join(lines) + "\n"

def run_report(args: argparse.Namespace) -> int:
    titles, scope_ids, drive_ids = read_checks(args.checks)
    scope = {cid: titles[cid] for cid in scope_ids}
    data = _load_json(args.results, "--results")
    drive_text, drive = load_drive(args.drive)
    problems = validate_results(data, scope, args.out_dir, drive, drive_ids)
    if problems:
        raise PreviewError(f"sonuclar.json geçersiz ({len(problems)} sorun); rapor yazılmadı", problems)
    tally = Counter(check["sonuc"] for check in data["kontroller"])
    counts = {result: tally.get(result, 0) for result in RESULTS}
    out = Path(args.out_dir) / "ONIZLEME_OZETI.md"
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(render(data, {**scope, **{c: titles.get(c, "") for c in OPTIONAL_CHECKS}}, counts, drive_text,
                              drive), encoding="utf-8")
    except OSError as exc:
        raise PreviewError(f"rapor yazilamadi: {type(exc).__name__}: {exc}") from exc
    summary = {"gecti": counts["GEÇTİ"], "kaldi": counts["KALDI"], "kontrol_edilemedi": counts["KONTROL EDİLEMEDİ"],
               "uygulanmaz": counts["UYGULANMAZ"], "toplam": sum(counts.values()) - counts["UYGULANMAZ"]}
    common.emit({"tool": f"{TOOL} report", **summary, "out": str(out)})
    return common.EXIT_FINDINGS if summary["kaldi"] or summary["kontrol_edilemedi"] else common.EXIT_OK

# --- komut satiri ---
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="preview_checks.py", description="city-preview kanit araclari (ag yok, salt okunur).")
    sub = parser.add_subparsers(dest="command", required=True)
    drive = sub.add_parser("drive-compare", help="Drive listesi <-> yerel envanter (K01, K03, K109, K110)")
    drive.add_argument("--local", type=Path, required=True, help="inventory.py ciktisi (dosya-envanteri.json)")
    drive.add_argument("--remote", type=Path, required=True, help="{root, files} .json ya da arac sonuclari klasoru")
    drive.add_argument("--pkg", dest="package_root", type=Path, default=None, help="yerel paket koku (MD5; salt okunur)")
    drive.add_argument("--downloads", type=Path, default=None, help="indirilenler.json: [{path, file, format: raw|base64}]")
    drive.add_argument("--excel-name", default=None, help="kokte beklenen Excel adi (varsayilan: yerel kokteki .xlsx)")
    drive.add_argument("--root-id", default=None, help="bagimsiz kaynaktaki (yonetim karti/uretim promptu) kok kimligi")
    drive.add_argument("--root-source", choices=("yonetim", "prompt"), default=None, help="--root-id'nin kaynagi")
    drive.add_argument("--previous", type=Path, default=None, help="onceki _ONIZLEME kosusunun drive_karsilastirma.json'u")
    drive.add_argument("--out", type=Path, required=True)
    scan = sub.add_parser("warning-scan", help="K103/K104 uyari kaliplari (Excel salt okunur)")
    scan.add_argument("--xlsx", type=Path, required=True)
    scan.add_argument("--out", type=Path, required=True)
    report = sub.add_parser("report", help="ONIZLEME_OZETI.md (sonuclar.json kurallariyla)")
    report.add_argument("--results", type=Path, required=True, help="sonuclar.json")
    report.add_argument("--out-dir", type=Path, required=True, help="OUT klasoru (goreli kanit yollari buna gore)")
    report.add_argument("--drive", type=Path, default=None, help="drive_karsilastirma.json (yoksa Drive GEÇTİ olmaz)")
    report.add_argument("--checks", type=Path, default=DEFAULT_CHECKS, help="checks.yaml (kapsam)")
    return parser

def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    try:
        return {"drive-compare": run_drive, "warning-scan": run_scan, "report": run_report}[args.command](args)
    except PreviewError as exc:
        common.emit({"tool": f"{TOOL} {args.command}", "error": str(exc), **({"problems": exc.problems} if exc.problems else {})})
        return common.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
