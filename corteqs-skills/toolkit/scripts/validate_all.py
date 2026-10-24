"""Resmi v7 teslim dogrulayicisini (Atinc, araclar/arac) surec icinde, salt okunur calistirir.

Kullanim:
  python validate_all.py <xlsx> <paket_koku> --tools <araclar/arac> [--mode audit|emit] [--new-content]
                         [--out rapor.json] [--max-examples 3]

--mode audit (varsayilan): read() + validate_files() + delivery_tools.audit(); paket klasorune HICBIR sey yazmaz.
--mode emit: ayni kontroller + check_delivery.py'nin Teslimler/ ciktilari (yalniz uretim sonunda).
Resmi okuyucu ';' listesinde yinelenen degerde cokuyor; burada tekrarlar atilip sayilir (geri alinan yama).
stdout: tek satir JSON ozet; tam listeler --out dosyasina. Cikis: 0 temiz, 1 bulgu, 2 kullanim/yapi hatasi.
Ek kontroller (extra_checks) 'ek kontrol' olarak ayri raporlanir; resmi sayilara karismaz, cikis kodunu etkilemez.
"""
from __future__ import annotations

import argparse
import contextlib
import importlib
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable, Iterator

import extra_checks
from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json

OFFICIAL_PACKAGES = ("read_delivery_v7", "v7_validation", "delivery_tools", "core")
UTF8_HINT = "resmî araçlar UTF-8 modu ister: python -X utf8 (veya PYTHONUTF8=1)"


class ToolsError(Exception):
    """--tools klasoru eksik/bozuk ya da resmi moduller yuklenemedi."""


class UsageError(Exception):
    """Gecersiz yol veya secenek."""


@dataclass(frozen=True)
class OfficialRun:
    data: dict[str, Any]
    provenance: list[dict[str, Any]]
    archives: dict[str, Any]
    structure: dict[str, Any]
    media: dict[str, Any]
    tolerated: list[str]


# --- hata siniflari -----------------------------------------------------------------

def error_class(message: str) -> str:
    """Satir/kimlik onekini atar: 'Sayfa!12: X: deger' -> 'Sayfa: X'; 'kimlik:a:b: X' -> 'X'; onek yoksa mesajin kendisi."""
    head, sep, rest = message.partition(": ")
    if not sep:
        return message
    if "!" in head:
        return f"{head.split('!', 1)[0]}: {_first_clause(rest)}"
    if ":" in head and not any(ch.isspace() for ch in head):
        return _first_clause(rest)
    return message


def _first_clause(text: str) -> str:
    """Ilk ': ' ayracina kadar keser; metnin icindeki ' : ' (onunde bosluk) ayrac sayilmaz."""
    return re.split(r"(?<! ): ", text, maxsplit=1)[0]


def group_classes(messages: Iterable[str], max_examples: int) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for message in messages:
        groups.setdefault(error_class(message), []).append(message)
    ordered = sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))
    return [{"class": name, "count": len(found), "examples": list(dict.fromkeys(found))[:max_examples]} for name, found in ordered]


# --- resmi araclarin yuklenmesi ve toleransli liste yamasi ------------------------------

@contextlib.contextmanager
def tolerant_lists(dv: Any) -> Iterator[list[str]]:
    """dv.parse_list ve dv.PARSERS['id_list'] yinelenen degerde hata yerine tekrarsiz liste dondurur.

    Sorunlu hucre degerleri verilen listeye eklenir; cikista (hata olsa bile) orijinaller geri yuklenir.
    """
    original_parse, original_id = dv.parse_list, dv.PARSERS.get("id_list")
    offending: list[str] = []

    def tolerant(value: Any, separator: str) -> list[str]:
        try:
            return original_parse(value, separator)
        except ValueError:
            offending.append(str(value))
            return list(dict.fromkeys(p.strip() for p in str(value).split(separator) if p.strip()))

    dv.parse_list = tolerant
    dv.PARSERS["id_list"] = lambda value: tolerant(value, ";")
    try:
        yield offending
    finally:
        dv.parse_list = original_parse
        dv.PARSERS["id_list"] = original_id


def _purge_official_modules() -> None:
    for name in [n for n in sys.modules if n.split(".")[0] in OFFICIAL_PACKAGES]:
        del sys.modules[name]


def load_tools(tools_dir: Path) -> SimpleNamespace:
    """Resmi modulleri verilen klasorden (onbellek temizlenerek) yukler; __pycache__ yazilmaz."""
    tools = Path(tools_dir).resolve()
    if not (tools / "read_delivery_v7.py").is_file():
        raise ToolsError(f"--tools klasöründe read_delivery_v7.py yok: {tools}")
    _purge_official_modules()
    importlib.invalidate_caches()
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(tools))
    try:
        delivery = importlib.import_module("delivery_tools")
        return SimpleNamespace(
            dv=importlib.import_module("core.content_delivery.delivery_values"),
            read=importlib.import_module("read_delivery_v7").read,
            validate_files=importlib.import_module("v7_validation").validate_files,
            audit=delivery.audit, export_attributions=delivery.export_attributions)
    except Exception as exc:  # noqa: BLE001 - resmi kodun her yukleme hatasi kullanim hatasidir
        raise ToolsError(f"resmî araçlar yüklenemedi ({type(exc).__name__}: {exc}); {UTF8_HINT}") from exc
    finally:
        sys.dont_write_bytecode = previous
        with contextlib.suppress(ValueError):
            sys.path.remove(str(tools))


def run_official(tools: SimpleNamespace, workbook: Path, root: Path, new_content: bool) -> OfficialRun:
    with tolerant_lists(tools.dv) as offending:
        try:
            data, provenance, archives = tools.read(workbook)
        except Exception as exc:  # noqa: BLE001 - okunamayan calisma kitabi = yapi hatasi (cikis 2)
            raise UsageError(f"çalışma kitabı okunamadı ({type(exc).__name__}: {exc})") from exc
        structure = tools.validate_files(data, assets_root=root)
        media = tools.audit(root, data["photos"], provenance, require_new_chain=new_content)
    return OfficialRun(data, provenance, archives, structure, media, list(offending))


# --- ozet / rapor -------------------------------------------------------------------------

def minimum_gaps(structure: dict[str, Any]) -> dict[str, dict[str, int]]:
    counts, minimum = structure.get("counts", {}), structure.get("minimum", {})
    return {key: {"actual": counts.get(key, 0), "minimum": need} for key, need in minimum.items() if counts.get(key, 0) < need}


def technically_complete(run: OfficialRun) -> bool:
    media_ok = run.media.get("structural_passed", not run.media.get("errors"))
    return bool(media_ok and run.structure.get("valid") and not minimum_gaps(run.structure))


def build_summary(args: argparse.Namespace, run: OfficialRun, extras: dict[str, Any]) -> dict[str, Any]:
    history = extras["history_share"]
    return {
        "tool": "validate_all", "mode": args.mode, "new_content": args.new_content,
        "structure": {"errors": len(run.structure.get("errors", [])), "warnings": len(run.structure.get("warnings", []))},
        "media": {"errors": len(run.media.get("errors", []))},
        "minimum_gaps": minimum_gaps(run.structure),
        "error_classes": group_classes(run.structure.get("errors", []), args.max_examples),
        "media_classes": group_classes(run.media.get("errors", []), args.max_examples),
        "tolerated_duplicate_list_cells": len(run.tolerated),
        "extras": extra_checks.counts(extras),
        "extras_note": f"ek kontrol, resmî sayılara dahil değil; tarih payı {history['history']}/{history['total']} "
                       f"(eşik {history['threshold']}, öneri)",
        "technically_complete": technically_complete(run),
    }


def build_report(summary: dict[str, Any], run: OfficialRun, extras: dict[str, Any], max_examples: int) -> dict[str, Any]:
    return {
        "summary": summary,
        "structure": run.structure,
        "media": run.media,
        "warning_classes": group_classes(run.structure.get("warnings", []), max_examples),
        "tolerated_duplicate_list_cells": run.tolerated,
        "extras": extras,
    }


def emit_deliverables(tools: SimpleNamespace, root: Path, run: OfficialRun) -> list[str]:
    """check_delivery.py ile ayni Teslimler/ ciktilari (UTF-8 olarak) yazar."""
    result = {
        "version": "7.0", "media": run.media, "structure": run.structure, "minimum_gaps": minimum_gaps(run.structure),
        "long_values_restored": len(run.archives), "technically_complete": technically_complete(run),
        "whole_package_human_approval": "Not granted by this tool", "database_written": False, "published": False,
        "tolerated_duplicate_list_cells": len(run.tolerated),
    }
    output = root / "Teslimler"
    output.mkdir(exist_ok=True)
    files = {"photo-provenance-v7.json": run.provenance, "normalized-tables-v7.json": run.data, "paket-kontrol-v7.json": result}
    for name, payload in files.items():
        (output / name).write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    tools.export_attributions(root, run.data["photos"], run.provenance)
    return sorted(files) + ["fotograf-atiflari-v7.csv", "fotograf-atif-onizleme.html"]


# --- CLI -------------------------------------------------------------------------------------

def _non_negative(value: str) -> int:
    number = int(value)
    if number < 0:
        raise argparse.ArgumentTypeError("negatif olamaz")
    return number


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Corteqs v7 resmî doğrulayıcı sarmalayıcısı (salt okunur denetim)")
    parser.add_argument("workbook", type=Path)
    parser.add_argument("package_root", type=Path)
    parser.add_argument("--tools", type=Path, default=None, help="araclar/arac klasörü (yoksa CORTEQS_TOOLS)")
    parser.add_argument("--mode", choices=("audit", "emit"), default="audit")
    parser.add_argument("--new-content", action="store_true")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-examples", type=_non_negative, default=3)
    return parser.parse_args(argv)


def check_inputs(args: argparse.Namespace) -> tuple[Path, Path]:
    tools = args.tools or (Path(os.environ["CORTEQS_TOOLS"]) if os.environ.get("CORTEQS_TOOLS") else None)
    if tools is None:
        raise UsageError("--tools veya CORTEQS_TOOLS gerekli")
    if not args.workbook.is_file():
        raise UsageError(f"çalışma kitabı yok: {args.workbook}")
    root = args.package_root.resolve()
    if not root.is_dir():
        raise UsageError(f"paket kökü yok: {root}")
    if args.mode == "audit" and args.out and args.out.resolve().is_relative_to(root):
        raise UsageError("audit modunda --out paket klasörünün içinde olamaz (salt okunur)")
    return tools, root


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    args = parse_args(argv)
    try:
        tools_dir, root = check_inputs(args)
        tools = load_tools(tools_dir)
        run = run_official(tools, args.workbook, root, args.new_content)
    except (UsageError, ToolsError) as exc:
        emit({"tool": "validate_all", "error": str(exc)})
        return EXIT_USAGE
    extras = extra_checks.run_all(extra_checks.load_sheets(args.workbook))
    summary = build_summary(args, run, extras)
    if args.mode == "emit":
        summary["emitted"] = emit_deliverables(tools, root, run)
    if args.out:
        write_json(args.out, build_report(summary, run, extras, args.max_examples))
    emit(summary)
    clean = summary["technically_complete"] and not summary["structure"]["errors"] and not summary["media"]["errors"]
    return EXIT_OK if clean else EXIT_FINDINGS


if __name__ == "__main__":
    if not sys.flags.utf8_mode:  # resmi kod open()/read_text() varsayilan kodlamasini kullanir
        sys.exit(subprocess.run([sys.executable, "-X", "utf8", *sys.argv]).returncode)
    sys.exit(main())
