"""xlsx_fidelity.py <template.xlsx> <output.xlsx> [--report R.json] [--accept-openpyxl-parts]

Sablon ile yazilmis cikti arasinda yapisal sadakat denetimi (veri hucreleri haric):
sayfa adlari + sirasi, satir 1-7 degerleri (5 alan notu, 6 Turkce baslik, 7 teknik anahtar), veri sayfasi olmayan
sayfalarin (Ozet) tum hucreleri, sayfa basina veri dogrulamalari (tur, liste, aralik), Excel tablolari (ad, aralik,
stil, sutunlar), formul hucreleri (koordinat + metin), dondurulmus bolme, birlesik hucreler, sutun genislikleri, ayarli
satir yukseklikleri, kosullu bicimlendirme araliklari, otomatik filtre, tanimli adlar, zip parca listesi.

openpyxl 3.1 her kayitta docProps/app.xml + docProps/core.xml ekler ve metinleri satir ici (inlineStr) yazar, yani
xl/sharedStrings.xml parcasini yeniden uretmez. Bu uc parca farki varsayilan olarak HATADIR; yalniz
--accept-openpyxl-parts ile ve yalniz bu yonde (docProps eklendi / sharedStrings kalkti) kabul edilip raporlanir.
stdout: tek satir JSON {fidelity: "ok" | [farklar], accepted: [...]}. Cikis: 0 ayni / 2 fark veya okunamayan dosya.
"""
from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Any

import openpyxl

import common

STRUCT_ROWS = tuple(range(1, common.KEY_ROW + 1))
MAX_LISTED = 8
OPENPYXL_ADDED_PARTS = frozenset({"docProps/app.xml", "docProps/core.xml"})
OPENPYXL_REMOVED_PARTS = frozenset({"xl/sharedStrings.xml"})


def column_widths(ws) -> dict[int, float]:
    widths: dict[int, float] = {}
    for dim in ws.column_dimensions.values():
        if dim.width is not None and (dim.customWidth or dim.width):
            for idx in range(dim.min or 1, (dim.max or dim.min or 1) + 1):
                widths[idx] = round(float(dim.width), 4)
    return widths


def formula_cells(ws) -> dict[str, str]:
    return {c.coordinate: str(c.value) for row in ws.iter_rows() for c in row if common.is_formula(c.value)}


def static_cells(ws) -> dict[str, Any]:
    """Veri sayfasi olmayan sayfalarin (Ozet) tum dolu hucreleri."""
    if ws.title in common.DATA_SHEETS:
        return {}
    return {c.coordinate: c.value for row in ws.iter_rows() for c in row if c.value is not None}


def data_validations(ws) -> list[tuple]:
    return sorted((dv.type or "", dv.formula1 or "", dv.formula2 or "", dv.operator or "", str(dv.sqref))
                  for dv in ws.data_validations.dataValidation)


def tables(ws) -> list[tuple]:
    return sorted((t.name, t.displayName, t.ref, t.tableStyleInfo.name if t.tableStyleInfo else None,
                   tuple(c.name for c in t.tableColumns)) for t in ws.tables.values())


def sheet_snapshot(ws) -> dict[str, Any]:
    width = ws.max_column
    return {
        "rows": {r: tuple(ws.cell(r, c).value for c in range(1, width + 1)) for r in STRUCT_ROWS},
        "static cells": static_cells(ws),
        "data validations": data_validations(ws),
        "tables": tables(ws),
        "formulas": formula_cells(ws),
        "freeze panes": ws.freeze_panes,
        "merged ranges": sorted(str(r) for r in ws.merged_cells.ranges),
        "column widths": column_widths(ws),
        "row heights": {r: d.ht for r, d in ws.row_dimensions.items() if d.ht is not None},
        "conditional formatting": sorted(str(cf.sqref) for cf in ws.conditional_formatting),
        "auto filter": ws.auto_filter.ref,
        "sheet defined names": sorted((n, d.attr_text) for n, d in getattr(ws, "defined_names", {}).items()),
    }


def snapshot(path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(path) as archive:
        parts = sorted(archive.namelist())
    wb = openpyxl.load_workbook(path)
    try:
        return {
            "sheets": list(wb.sheetnames),
            "defined names": sorted((n, d.attr_text) for n, d in wb.defined_names.items()),
            "zip parts": parts,
            "per_sheet": {ws.title: sheet_snapshot(ws) for ws in wb.worksheets},
        }
    finally:
        wb.close()


def listed(items) -> str:
    items = list(items)
    more = f" (+{len(items) - MAX_LISTED} more)" if len(items) > MAX_LISTED else ""
    return ", ".join(str(i) for i in items[:MAX_LISTED]) + more


def diff_collection(label: str, a, b) -> list[str]:
    if a == b:
        return []
    if isinstance(a, dict) and isinstance(b, dict):
        missing = [k for k in a if k not in b]
        extra = [k for k in b if k not in a]
        changed = [k for k in a if k in b and a[k] != b[k]]
        return [f"{label} differ (template {len(a)}, output {len(b)}): missing [{listed(missing)}] "
                f"extra [{listed(extra)}] changed [{listed(changed)}]"]
    if isinstance(a, list) and isinstance(b, list):
        missing = [x for x in a if x not in b]
        extra = [x for x in b if x not in a]
        return [f"{label} differ (template {len(a)}, output {len(b)}): missing [{listed(missing)}] extra [{listed(extra)}]"]
    return [f"{label} differ: template {a!r} != output {b!r}"]


def diff_sheet(name: str, a: dict[str, Any], b: dict[str, Any]) -> list[str]:
    diffs: list[str] = []
    for row in STRUCT_ROWS:
        if a["rows"][row] != b["rows"][row]:
            cols = [i + 1 for i, (x, y) in enumerate(zip(a["rows"][row], b["rows"][row])) if x != y]
            diffs.append(f"{name}: row {row} differs (columns {listed(cols) or 'width'})")
    for label in [k for k in a if k != "rows"]:
        diffs += [f"{name}: {d}" for d in diff_collection(label, a[label], b[label])]
    return diffs


def split_known_parts(a: list[str], b: list[str], accept: bool) -> tuple[list[str], list[str], list[str]]:
    """(sablon parcalari, cikti parcalari, kabul edilen farklar). Kabul yalniz bilinen openpyxl yonu icin."""
    if not accept:
        return a, b, []
    removed = sorted(p for p in OPENPYXL_REMOVED_PARTS if p in a and p not in b)
    added = sorted(p for p in OPENPYXL_ADDED_PARTS if p in b and p not in a)
    accepted = [f"zip part removed by openpyxl: {p}" for p in removed] + [f"zip part added by openpyxl: {p}" for p in added]
    return [p for p in a if p not in removed], [p for p in b if p not in added], accepted


def compare_snapshots(a: dict[str, Any], b: dict[str, Any], accept_openpyxl_parts: bool = False) -> tuple[list[str], list[str]]:
    diffs: list[str] = []
    if a["sheets"] != b["sheets"]:
        diffs.append(f"sheet names/order differ: template {a['sheets']} != output {b['sheets']}")
    diffs += diff_collection("defined names", a["defined names"], b["defined names"])
    parts_a, parts_b, accepted = split_known_parts(a["zip parts"], b["zip parts"], accept_openpyxl_parts)
    diffs += diff_collection("zip parts", parts_a, parts_b)
    for name, snap in a["per_sheet"].items():
        if name in b["per_sheet"]:
            diffs += diff_sheet(name, snap, b["per_sheet"][name])
    return diffs, accepted


def check(template: Path, output: Path, accept_openpyxl_parts: bool = False) -> tuple[list[str], list[str]]:
    """(farklar, kabul edilen bilinen openpyxl farklari). Bos fark listesi = yapisal olarak ayni."""
    return compare_snapshots(snapshot(Path(template)), snapshot(Path(output)), accept_openpyxl_parts)


def compare(template: Path, output: Path) -> list[str]:
    """Kati denetim: hicbir fark kabul edilmez."""
    return check(template, output)[0]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sablon ile cikti xlsx arasinda yapisal sadakat denetimi.")
    parser.add_argument("template", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", "--out-report", dest="report", type=Path, default=None)
    parser.add_argument("--strict-parts", action="store_true",
                        help="varsayilan kabulu kapat: docProps/app.xml+core.xml eklenmesi ve xl/sharedStrings.xml kalkmasi da hata sayilir")
    return parser


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    try:
        diffs, accepted = check(args.template, args.output, not args.strict_parts)
    except (OSError, zipfile.BadZipFile, KeyError, ValueError) as exc:
        common.emit({"error": f"xlsx okunamadi: {type(exc).__name__}: {exc}"})
        return common.EXIT_USAGE
    if args.report:
        common.write_json(args.report, {"template": str(args.template), "output": str(args.output),
                                        "diffs": diffs, "accepted": accepted})
    common.emit({"fidelity": diffs or "ok", "accepted": accepted})
    return common.EXIT_USAGE if diffs else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
