"""render_summary.py --xlsx X --out-dir D [--inventory I.json] [--validation V.json] [--notes N.md] [--manifest M.json] [--date YYYY-MM-DD]

TESLIM_OZETI.txt, ACIK_KONULAR.txt, ILERLEME_KAYDI.txt (adlarda _v7 yok) uretir. Sayilar yalniz olcumden gelir;
olculmeyen girdi 'olculmedi' yazilir. 'Editor tarafindan onaylandi' hicbir kosulda yazilmaz.
ILERLEME_KAYDI girdisi tarih + Excel SHA-256 tasir ve ilk bos satirda biter (manifest metni tek satira indirilir). Ayni gunun
ayni Excel'ine ait girdi (ayni SHA; eski bicimli SHA'siz girdide ayni baslik = Excel adi + surum) ve ayni gunun yalniz SHA'si
farkli son girdisi (yeniden derlenen Excel) tekrar eklenmez: atilir, yenisi sona yazilir. Bas metin, baska girdiler ve girdiden
bos satirla ayrilan elle yazilmis metin yerinde kalir; girdiye bitisik (bos satirsiz) yazilan satir girdiyle birlikte yenilenir.
Sayilar: pakette kaynak = Kaynaklar satiri (olcum); arastirilan kaynak = manifest.sources_researched (kaynak_dizini satiri; bu arac
olcemez), pakettekinden azsa ya da sayi degilse celiski. Foto = envanterde Fotoğraflar klasorundeki dosya (envanter yoksa Excel
satiri); manifest photos_downloaded farkliysa olcum yazilir + not. Celisen manifest alanlari stdout manifest_mismatch'te.
stdout: tek satir JSON (verdict, blocking, info, notes, progress: eklendi|güncellendi, manifest_mismatch, out_dir).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any, NamedTuple

import common
import summary_metrics

NO_ISSUES = "Araştırmada saptanan açık konu yok; editör/hak kabulü ayrıca gereklidir"
NOT_MEASURED = "ölçülmedi"
PROGRESS_FILE = "ILERLEME_KAYDI.txt"
ENTRY_HEAD = re.compile(r"^=== (\d{4}-\d{2}-\d{2}) · ", re.MULTILINE)
ENTRY_END = re.compile(r"\n[ \t]*\n")  # girdi ilk bos satirda biter
SHA_PREFIX = "Excel SHA-256: "
PHOTO_DIR = "Fotoğraflar"
SOURCES_LABEL, PHOTOS_LABEL = "Araştırılan resmî kaynaklar", "İndirilmiş fotoğraflar"
SOURCES_BASIS = "Kaynaklar sekmesindeki satır"
INVENTORY_BLOCKING = ("missing", "sha_mismatch", "file_ne_original", "bad_ext", "ext_mismatch", "errors")
INVENTORY_INFO = ("orphans", "dup_sha")
VERDICT_OK = "TEKNİK KONTROL GEÇTİ — insan paket incelemesi bekliyor"
VERDICT_FIX = "DÜZELTME GEREKLİ"
VERDICT_MISSING = "KANIT EKSİK — doğrulayıcı/envanter çalıştırılmadı"


class InputError(Exception):
    pass


def load_json(path: Path | None, label: str) -> dict[str, Any] | None:
    if path is None:
        return None
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputError(f"{label} okunamadı: {path} ({type(exc).__name__})") from exc


def _short(item: Any) -> str:
    return (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False))[:110]


def _validation_issues(validation: dict[str, Any]) -> tuple[list[str], list[str]]:
    summary = validation.get("summary", {})
    blocking = []
    for group, label in (("error_classes", "yapı"), ("media_classes", "medya")):
        for cls in summary.get(group, []):
            example = (cls.get("examples") or [""])[0]
            blocking.append(f"Resmî doğrulayıcı ({label}): {cls['class']} — {cls['count']}" + (f" (örnek: {example})" if example else ""))
    # minimum_gaps burada listelenmez: ayni eksik Berlin tablosundan (_coverage_issues) tek satir olarak gelir
    extras = [f"ek kontrol, resmî sayıya dahil değil: {name} — {n}" for name, n in (summary.get("extras") or {}).items() if n]
    return blocking, extras


def _inventory_issues(inventory: dict[str, Any]) -> tuple[list[str], list[str]]:
    findings = inventory.get("findings", {})
    blocking, info = [], []
    for key in INVENTORY_BLOCKING + INVENTORY_INFO:
        items = findings.get(key) or []
        if items:
            line = f"Envanter: {key} — {len(items)} (örnek: {_short(items[0])})"
            (blocking if key in INVENTORY_BLOCKING else info).append(line)
    return blocking, info


def _coverage_issues(metrics: dict[str, Any]) -> tuple[list[str], list[str]]:
    blocking = [f"Fotoğrafsız mekân/mahalle: {len(c['without_photo'])} (örnek: {c['without_photo'][0]})"
                for c in (metrics["places"], metrics["districts"]) if c["without_photo"]]
    info = [f"Hedef eksik: {r['label']} {r['actual']}/{r['target']} — {r['status']}" for r in metrics["berlin"]
            if r["status"].startswith("hedefin altında")]
    blocking += [f"Berlin alt sınırının altında: {r['label']} {r['actual']}/{r['minimum']}" for r in metrics["berlin"]
                 if r["status"] == "alt sınırın altında"]
    src = metrics["sources"]
    if src["verified_without_snapshot"]:
        info.append(f"verified=Evet ama kaynak görüntüsü (snapshot) yok: {src['verified_without_snapshot']}/{src['total']}")
    return blocking, info


def collect_issues(metrics: dict[str, Any]) -> dict[str, list[str]]:
    blocking: list[str] = []
    info: list[str] = []
    for source, fn in ((metrics["validation"], _validation_issues), (metrics["inventory"], _inventory_issues)):
        if source:
            b, i = fn(source)
            blocking += b
            info += i
    b, i = _coverage_issues(metrics)
    return {"blocking": list(dict.fromkeys(blocking + b)), "info": list(dict.fromkeys(info + i))}


def verdict(metrics: dict[str, Any], issues: dict[str, list[str]]) -> str:
    if metrics["validation"] is None or metrics["inventory"] is None:
        return VERDICT_MISSING
    complete = metrics["validation"].get("summary", {}).get("technically_complete", False)
    return VERDICT_FIX if (issues["blocking"] or not complete) else VERDICT_OK


def render_open_issues(issues: dict[str, list[str]], notes: list[str]) -> str:
    lines = [f"- {x}" for x in issues["blocking"] + issues["info"] + notes]
    if not lines:
        return NO_ISSUES + "\n"
    return "AÇIK KONULAR\n" + "\n".join(lines) + "\n\nEditör ve hak incelemesi ayrıca gereklidir.\n"


def _count(value: Any) -> str:
    return NOT_MEASURED if value is None else str(value)


def render_summary(metrics: dict[str, Any], issues: dict[str, list[str]], verdict_text: str, date: str) -> str:
    inv, val, ph, human = metrics["inventory"], metrics["validation"], metrics["photos"], metrics["human"]
    out = [f"Şehir: {metrics['city_name']} | city_id: {metrics['city_id']} | CITY kodu: {metrics['city_code']}",
           f"Hazırlayan: {metrics['editor']}", f"Excel sürümü/tarihi: {metrics['version']} · {date}",
           "Dosya: YEREL DENEME - Drive'a yüklenmedi (manuel yüklenecek)", "Klasör: YEREL DENEME - Drive'a yüklenmedi (manuel yüklenecek)",
           f"Durum: {verdict_text}", "Editör tarafından onaylandı: HAYIR (AI kontrolü yayın veya hak onayı değildir)", "",
           "Sekme satır sayıları: " + ", ".join(f"{k} {v}" for k, v in metrics["row_counts"].items()), "",
           f"Berlin karşılaştırması (kaynak: {metrics['berlin'][0]['source']}):"]
    out += [f"  {r['label']}: {r['actual']} / alt sınır {r['minimum']} / hedef {r['target']} — {r['status']}" for r in metrics["berlin"]]
    out += ["", f"Fotoğraf: {ph['rows']} ilişki; tekil mekân karesi {ph['venue_unique']}, tekil kapak {ph['cover_unique']} (aynı SHA veya aynı kaynak sayfası tek sayılır)",
            f"Fotoğraflı mekân: {metrics['places']['with_photo']}/{metrics['places']['total']}; fotoğraflı mahalle: {metrics['districts']['with_photo']}/{metrics['districts']['total']}",
            f"Kaynaklar: {metrics['sources']['total']} kayıt; verified=Evet {metrics['sources']['verified_yes']}; kaynak görüntüsü (snapshot) olan {metrics['sources']['with_snapshot']}",
            f"Çalışan işlem bağlantısı (URL) sayısı: {NOT_MEASURED} (bu araç URL'leri test etmez)",
            f"İnsan incelemesi bekleyen: {human['pending_fields']} alan ({human['rows']} kanıt satırı × 3 alan)"
            + (f"; geçersiz değer {human['invalid_values']}" if human["invalid_values"] else ""),
            f"Resmî doğrulayıcı: " + (NOT_MEASURED if val is None else
                                     f"yapı hata {val['summary']['structure']['errors']}, uyarı {val['summary']['structure']['warnings']}, medya hata {val['summary']['media']['errors']}, technically_complete={val['summary']['technically_complete']}"),
            f"Paket: " + (NOT_MEASURED if inv is None else f"{_count(inv['totals']['files'])} dosya, {inv['totals']['total_mb']} MB (ölçülen)"),
            f"Açık konu sayısı: {len(issues['blocking'])} engelleyici, {len(issues['info'])} bilgi (ayrıntı: ACIK_KONULAR.txt)", "",
            "Talep: Editör ve hak incelemesi."]
    return "\n".join(out) + "\n"


def _photo_files(inventory: dict[str, Any] | None) -> int | None:
    """Envanterde Fotoğraflar klasorundeki dosya sayisi (NFC/NFD ad farki yok sayilir); envanter/klasor bilgisi yoksa None."""
    folders = (inventory or {}).get("folders")
    if not isinstance(folders, dict):
        return None
    by_name = {unicodedata.normalize("NFC", str(name)): info for name, info in folders.items()}
    info = by_name.get(PHOTO_DIR)
    return int(info.get("files", 0)) if isinstance(info, dict) else 0


def _photo_count(metrics: dict[str, Any]) -> tuple[int, str]:
    """(olculen foto sayisi, olcum dayanagi): envanterdeki klasor, envanter yoksa Excel satiri."""
    files = _photo_files(metrics["inventory"])
    if files is not None:
        return files, "Fotoğraflar klasöründeki dosya"
    return metrics["photos"]["rows"], "Excel Fotoğraflar satırı; envanter yok"


def _one_line(value: Any) -> str:
    """Girdi satir tabanlidir ve ilk bos satirda biter: manifest metnindeki satir sonlari bosluga cevrilir."""
    return " ".join(str(value).split())


def _manifest_int(value: Any) -> int | None:
    """Manifest sayisi: tam sayi ya da rakam metni (bool degil); degilse None."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    return int(text) if text.isdigit() else None


def _sources_line(package: int, claimed: Any) -> tuple[str, bool]:
    """Arastirilan kaynak manifest'ten (kaynak_dizini satiri; bu arac olcemez), pakettekinden az olamaz -> (satir, celiski)."""
    measured = f"· pakette {package} (ölçüm: {SOURCES_BASIS})"
    if claimed is None:
        return f"{SOURCES_LABEL}: belirtilmedi (manifest'te yok) {measured}", False
    number = _manifest_int(claimed)
    if number is not None and number >= package:
        return f"{SOURCES_LABEL}: {number} (manifest: kaynak dizini satırı) {measured}", False
    why = "sayı değil" if number is None else "pakettekinden az olamaz"
    return f"{SOURCES_LABEL}: en az {package} (manifest {_one_line(claimed)} diyor; {why}) {measured}", True


def _photos_line(metrics: dict[str, Any], claimed: Any) -> tuple[str, bool]:
    """Indirilmis foto olcumden; manifest farkliysa olcum esas + not -> (satir, celiski)."""
    value, basis = _photo_count(metrics)
    conflict = claimed is not None and str(claimed) != str(value)
    note = f"; manifest {_one_line(claimed)} diyor, ölçüm esas alındı" if conflict else ""
    return f"{PHOTOS_LABEL}: {value} (ölçüm: {basis}{note})", conflict


def _count_lines(metrics: dict[str, Any], manifest: dict[str, Any]) -> tuple[list[str], list[str]]:
    sources, sources_bad = _sources_line(metrics["sources"]["total"], manifest.get("sources_researched"))
    photos, photos_bad = _photos_line(metrics, manifest.get("photos_downloaded"))
    mismatch = [key for key, bad in (("sources_researched", sources_bad), ("photos_downloaded", photos_bad)) if bad]
    return [sources, photos], mismatch


def render_progress(metrics: dict[str, Any], manifest: dict[str, Any], issues: dict[str, list[str]], date: str,
                    xlsx_sha: str) -> tuple[str, list[str]]:
    """Ilerleme girdisi ve manifest'in olcumle celisen alanlari."""
    rows = ", ".join(f"{k} {v}" for k, v in metrics["row_counts"].items() if v)
    counts, mismatch = _count_lines(metrics, manifest)
    ids = ", ".join(_one_line(i) for i in manifest.get("last_ids", []))
    lines = [f"=== {date} · {metrics['xlsx_name']} ({metrics['version']}) ===", f"{SHA_PREFIX}{xlsx_sha}",
             f"Faz: {_one_line(manifest.get('phase', 'belirtilmedi'))}", f"Mevcut sayılar: {rows}",
             f"Son kullanılan kimlikler: {ids or 'belirtilmedi'}", *counts, f"Çözülemeyen konular: {len(issues['blocking'])}",
             f"Sonraki somut adım: {_one_line(manifest.get('next_step', 'belirtilmedi'))}"]
    return "\n".join(lines) + "\n\n", mismatch


class EntryKey(NamedTuple):
    date: str
    sha: str | None  # eski bicimli girdide None
    head: str  # '=== tarih · Excel adi (surum) ==='
    body: tuple[str, ...]  # SHA satiri disindaki satirlar


def split_entries(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Kaydi (bas metin, [(girdi, ardindan gelen serbest metin)]) olarak boler.

    Girdi '=== YYYY-AA-GG · ' satiriyla baslar ve ilk bos satirda biter; oradan sonraki girdiye kadarki metin elle yazilmistir.
    """
    starts = [m.start() for m in ENTRY_HEAD.finditer(text)]
    chunks = [text[a:b] for a, b in zip(starts, starts[1:] + [len(text)])]
    return (text[:starts[0]] if starts else text), [_split_chunk(chunk) for chunk in chunks]


def _split_chunk(chunk: str) -> tuple[str, str]:
    end = ENTRY_END.search(chunk)
    return (chunk, "") if end is None else (chunk[:end.start() + 1], chunk[end.end():])


def _entry_key(entry: str) -> EntryKey:
    lines = entry.strip().splitlines()
    sha = next((ln[len(SHA_PREFIX):].strip() for ln in lines if ln.startswith(SHA_PREFIX)), None)
    body = tuple(ln for ln in lines if not ln.startswith(SHA_PREFIX))
    return EntryKey(ENTRY_HEAD.match(entry).group(1), sha, lines[0], body)


def _same_excel(old: EntryKey, new: EntryKey) -> bool:
    """Ayni gunun ayni Excel'i: SHA ayni ya da eski bicimli (SHA'siz) girdide baslik (Excel adi + surum) ayni."""
    return old.date == new.date and ((old.sha == new.sha) if old.sha else (old.head == new.head))


def _kept_entries(entries: list[str], new: EntryKey) -> list[str | None]:
    """Atilan girdi None: ayni gunun ayni Excel'i ve ayni gunun yalniz SHA'si farkli son girdisi (yeniden derlenen Excel)."""
    kept: list[str | None] = [None if _same_excel(_entry_key(e), new) else e for e in entries]
    last = next((i for i in range(len(kept) - 1, -1, -1) if kept[i] is not None), None)
    if last is not None:
        key = _entry_key(kept[last])
        if key.date == new.date and key.body == new.body:
            kept[last] = None
    return kept


def merge_progress(existing: str, entry: str) -> tuple[str, str]:
    """Yeni girdi sona yazilir; ayni Excel'in eski girdileri atilir (_kept_entries); bas metin ve serbest metin yerinde kalir."""
    head, chunks = split_entries(existing)
    kept = _kept_entries([e for e, _ in chunks], _entry_key(entry))
    pieces = [p for k, (_, free) in zip(kept, chunks) for p in (k, free) if p and p.strip()] + [entry]
    head = head if not head or head.endswith("\n") else head + "\n"
    status = "güncellendi" if None in kept else "eklendi"
    return head + "".join(p.strip("\n") + "\n\n" for p in pieces), status


def read_progress(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8-sig")  # elle duzenlenip BOM almis kayit da okunur
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"ilerleme kaydı okunamadı: {path} ({type(exc).__name__})") from exc


def write_atomic(path: Path, text: str) -> None:
    """Once gecici dosyaya, sonra yerine: yarida kalan yazim eski kaydi bozmaz."""
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def read_notes(path: Path | None) -> list[str]:
    if path is None:
        return []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError(f"notlar okunamadı: {path}") from exc
    return [ln.strip().lstrip("-• ").strip() for ln in text.splitlines() if ln.strip()]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Teslim ozeti, acik konular ve ilerleme kaydi uretir.")
    p.add_argument("--xlsx", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--inventory", type=Path)
    p.add_argument("--validation", type=Path)
    p.add_argument("--notes", type=Path)
    p.add_argument("--manifest", type=Path)
    p.add_argument("--date", default=None, help="YYYY-MM-DD (varsayilan: bugun)")
    return p


def parse_date(value: str | None) -> str:
    """--date gecerli YYYY-AA-GG olmali (girdi basligi ve ayni gun karsilastirmasi buna dayanir); yoksa bugun."""
    if value is None:
        return dt.date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise InputError(f"--date YYYY-MM-DD olmalı: {value}")
    try:
        return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise InputError(f"--date geçersiz tarih: {value}") from exc


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if not args.xlsx.is_file():
        raise InputError(f"Excel bulunamadı: {args.xlsx}")
    date = parse_date(args.date)
    inventory, validation = load_json(args.inventory, "envanter"), load_json(args.validation, "doğrulama")
    manifest = load_json(args.manifest, "manifest") or {}
    notes = read_notes(args.notes)
    metrics = summary_metrics.collect(args.xlsx, inventory, validation)
    issues = collect_issues(metrics)
    text = verdict(metrics, issues)
    entry, mismatch = render_progress(metrics, manifest, issues, date, common.sha256_file(args.xlsx))
    progress_path = args.out_dir / PROGRESS_FILE
    progress, status = merge_progress(read_progress(progress_path), entry)  # okunamayan kayit varken hicbir sey yazilmaz
    args.out_dir.mkdir(parents=True, exist_ok=True)
    (args.out_dir / "TESLIM_OZETI.txt").write_text(render_summary(metrics, issues, text, date), encoding="utf-8")
    (args.out_dir / "ACIK_KONULAR.txt").write_text(render_open_issues(issues, notes), encoding="utf-8")
    write_atomic(progress_path, progress)
    summary = {"verdict": text, "blocking": len(issues["blocking"]), "info": len(issues["info"]), "notes": len(notes),
               "progress": status, "manifest_mismatch": mismatch, "out_dir": str(args.out_dir.resolve())}
    findings = issues["blocking"] or issues["info"] or notes or text != VERDICT_OK
    return (common.EXIT_FINDINGS if findings else common.EXIT_OK), summary


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    try:
        code, summary = run(build_parser().parse_args(argv))
    except (InputError, OSError, ValueError) as exc:
        common.emit({"error": str(exc)})
        return common.EXIT_USAGE
    common.emit(summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
