"""make_template yardımcısı: sayfa, Özet, formül ve çalışma kitabı işlemleri.

Veri sayfası: satır 8+ değerleri silinir (formül kalır), tablo kapasiteye kırpılır (DV/CF/x14 aralıkları dahil), yükseklik
sıfırlanır, satır 8'e kimlik yazılır. Özet: örneğe özgü notlar atılır. Formül: aralık hedef tablonun sonuna uyar, önbellek
boş şablona göre yazılır. Çalışma kitabı: silinen sekmeler, tanımlı adlar ve paylaşımlı metinler temizlenir."""
from __future__ import annotations

import datetime as _dt
import re
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

from openpyxl.utils.cell import column_index_from_string as col_index, get_column_letter as col_letter, range_boundaries

import common
from make_template_zip import (FlatXml, Package, TemplateError, XmlDoc, blank_row, cell_text, clip_sqref, find_tokens, get_cell,
                               has_value, local, m, resolve, row_map, set_cached, set_value, si_text, split_ref, strip_cell)

if TYPE_CHECKING:
    from make_template import TableSpec

DOC_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XM_SQREF = "{http://schemas.microsoft.com/office/excel/2006/main}sqref"
SUMMARY_SHEET = "Özet"
TITLE_CELL = "A3"
UNSUPPORTED = ("hyperlinks", "drawing", "legacyDrawing", "legacyDrawingHF", "drawingHF", "picture", "oleObjects", "controls")
ALLOWED_SHEET_RELS = ("/table", "/printerSettings")
RANGE_TAGS = ("conditionalFormatting", "dataValidation")
RANGE_RE = re.compile(r"(?P<sheet>'(?:[^']|'')+'|[^\s'!:(),=+\-*/&<>^\"]+)!\$(?P<c1>[A-Z]{1,3})\$(?P<r1>\d+)"
                      r":\$(?P<c2>[A-Z]{1,3})\$(?P<r2>\d+)")
COUNT_RE = re.compile(r"^(?:COUNTA|COUNT|SUM)\((?:'(?:[^']|'')+'|[^\s'!(),]+)!\$[A-Z]+\$\d+:\$[A-Z]+\$\d+\)$")
MAX_DIFF_RE = re.compile(r"^MAX\(([A-Z]{1,3}\d+)-([A-Z]{1,3}\d+),0\)$")
IF_BLANK_RE = re.compile(r'^IF\((?:A(\d+)=""|OR\(A(\d+)="",[^()]*\)),0,')


# --- sayfa: yükle, değerleri sil, kapasite, yükseklik, satır 8 -------------------------------------------------------

@dataclass
class Stats:
    cleared: Counter = field(default_factory=Counter)
    dropped_rows: Counter = field(default_factory=Counter)
    heights: Counter = field(default_factory=Counter)
    resized: dict[str, str] = field(default_factory=dict)
    refits: list[dict[str, str]] = field(default_factory=list)
    uncached: list[str] = field(default_factory=list)
    notes_removed: list[str] = field(default_factory=list)
    written: list[dict[str, Any]] = field(default_factory=list)
    removed_parts: list[str] = field(default_factory=list)
    renamed: dict[str, str] = field(default_factory=dict)
    names_removed: list[str] = field(default_factory=list)
    tokens: list[str] = field(default_factory=list)


@dataclass
class Sheet:
    name: str
    part: str
    rid: str
    element: ET.Element  # workbook.xml <sheet>
    doc: XmlDoc | None = None
    keys: dict[str, str] = field(default_factory=dict)  # satır 7 anahtarı -> sütun harfi
    table_part: str | None = None
    table_doc: XmlDoc | None = None
    table_end: int | None = None

    def load(self, pkg: Package, sst: list[str]) -> None:
        self.doc = pkg.xml(self.part)
        rels = pkg.rels(self.part)
        items = rels.items if rels else []
        found = [local(c.tag) for c in self.doc.root if local(c.tag) in UNSUPPORTED]
        found += [a["Type"].rsplit("/", 1)[-1] for _, a in items if not a["Type"].endswith(ALLOWED_SHEET_RELS)]
        if found:
            raise TemplateError(f"{self.name}: desteklenmeyen sayfa içeriği: {', '.join(found)} (araç genişletilmeli)")
        for cell in row_map(self.doc.root).get(common.KEY_ROW, ET.Element("row")).findall(m("c")):
            if (text := cell_text(cell, sst)) and text.strip():
                self.keys[text.strip()] = split_ref(cell.get("r"))[0]
        tables = [resolve(self.part, a["Target"]) for _, a in items if a["Type"].endswith("/table")]
        if len(tables) > 1:
            raise TemplateError(f"{self.name}: birden çok Excel tablosu desteklenmiyor")
        if tables:
            self.table_part, self.table_doc = tables[0], pkg.xml(tables[0])
            self.table_end = range_boundaries(self.table_doc.root.get("ref"))[3]

    def blank_heights(self) -> Counter:
        rows = row_map(self.doc.root)
        return Counter((r.get("ht"), r.get("customHeight")) for n, r in rows.items()
                       if common.FIRST_DATA_ROW <= n <= (self.table_end or 0) and blank_row(r))

    def row8(self, sst: list[str]) -> dict[str, str]:
        row = row_map(self.doc.root).get(common.FIRST_DATA_ROW, ET.Element("row"))
        by_col = {split_ref(c.get("r"))[0]: cell_text(c, sst) for c in row.findall(m("c"))}
        return {key: by_col.get(col) or "" for key, col in self.keys.items()}

    def prepare(self, spec: TableSpec | None, fallback: tuple | None, stats: Stats) -> None:
        """Veri sayfası: satır 8+ değerleri silinir (formül kalır), tablo kapasiteye kırpılır, yükseklik sıfırlanır."""
        if spec is not None and self.table_doc is None:
            raise TemplateError(f"{self.name}: sözleşme tablosu var ama sayfada Excel tablosu yok")
        own = self.blank_heights()
        height = own.most_common(1)[0][0] if own else fallback
        rows = row_map(self.doc.root)
        for number, row in rows.items():
            if number < common.FIRST_DATA_ROW:
                continue
            for cell in [c for c in row.findall(m("c")) if c.find(m("f")) is None]:  # formüller kalır
                stats.cleared[self.name] += has_value(cell)
                strip_cell(cell)
        end = common.KEY_ROW + spec.capacity if spec is not None and spec.capacity else self.table_end
        if end is not None and self.table_end is not None and end != self.table_end:
            if end > self.table_end:
                raise TemplateError(f"{self.name}: tablo {self.table_doc.root.get('ref')} kapasiteden ({spec.capacity}) kısa; "
                                    "büyütme desteklenmiyor")
            self.shrink(rows, end, stats)
        self.reset_heights(rows, height, stats)
        self.refresh_dimension()

    def shrink(self, rows: dict[int, ET.Element], end: int, stats: Stats) -> None:
        old_end, old_ref = self.table_end, self.table_doc.root.get("ref")
        data = self.doc.root.find(m("sheetData"))
        for number in [n for n in rows if end < n <= old_end]:
            data.remove(rows.pop(number))
            stats.dropped_rows[self.name] += 1
        for element in self.doc.root.iter():
            if local(element.tag) in RANGE_TAGS and element.get("sqref") is not None:
                element.set("sqref", clip_sqref(element.get("sqref"), end, old_end))
            elif element.tag == XM_SQREF:  # x14 DV/CF uzantıları
                element.text = clip_sqref(element.text or "", end, old_end)
        prune_ranges(self.doc.root)
        for element in self.table_doc.root.iter():
            if element.get("ref"):
                element.set("ref", clip_sqref(element.get("ref"), end, old_end) or element.get("ref"))
        self.table_end = end
        stats.resized[self.name] = f"{old_ref}->{self.table_doc.root.get('ref')}"

    def reset_heights(self, rows: dict[int, ET.Element], height: tuple | None, stats: Stats) -> None:
        for number in range(common.FIRST_DATA_ROW, (self.table_end or 0) + 1):
            row = rows.get(number)
            if height is None or row is None or (row.get("ht"), row.get("customHeight")) == height:
                continue
            for attr, value in zip(("ht", "customHeight"), height):
                if value is None:
                    row.attrib.pop(attr, None)
                else:
                    row.set(attr, value)
            stats.heights[self.name] += 1

    def refresh_dimension(self) -> None:
        node = self.doc.root.find(m("dimension"))
        refs = [split_ref(c.get("r")) for c in self.doc.root.find(m("sheetData")).iter(m("c"))]
        if node is not None and refs:
            cols, rows = [col_index(c) for c, _ in refs], [r for _, r in refs]
            node.set("ref", f"{col_letter(min(cols))}{min(rows)}:{col_letter(max(cols))}{max(rows)}")

    def write_row8(self, spec: TableSpec, values: dict[str, Any], text_type: str, stats: Stats) -> None:
        row = row_map(self.doc.root).get(common.FIRST_DATA_ROW)
        if row is None:
            raise TemplateError(f"{self.name}: satır 8 yok")
        for key in [k for k in spec.keys if k in values]:
            if key not in self.keys:
                raise TemplateError(f"{self.name}: satır 7'de '{key}' anahtarı yok")
            ref = f"{self.keys[key]}{common.FIRST_DATA_ROW}"
            set_value(get_cell(row, ref), values[key], text_type)
            shown = values[key].isoformat() if isinstance(values[key], _dt.date) else values[key]
            stats.written.append({"sheet": self.name, "key": key, "cell": ref, "value": shown})


def prune_ranges(root: ET.Element) -> None:
    """Aralığı tamamen silinen CF/DV öğelerini (x14 karşılıkları dahil) ve boşalan kaplarını kaldırır."""
    for parent in list(root.iter()):
        for child in [c for c in parent if local(c.tag) in RANGE_TAGS]:
            x14 = child.find(XM_SQREF)
            if child.get("sqref") == "" or (x14 is not None and not (x14.text or "").strip()):
                parent.remove(child)
        if local(parent.tag) == "dataValidations" and parent.get("count") is not None:
            parent.set("count", str(len(parent)))
    for container in ("dataValidations", "conditionalFormattings", "ext", "extLst"):
        for parent in list(root.iter()):
            for child in [c for c in parent if local(c.tag) == container and not len(c)]:
                parent.remove(child)


# --- Özet: başlık ve örneğe özgü notlar ------------------------------------------------------------------------------

def merge_rows(ref: str) -> range:
    _, min_row, _, max_row = range_boundaries(ref)
    return range(min_row, max_row + 1)


def first_note_row(rows: dict[int, ET.Element], sst: list[str], tokens: list[str]) -> int | None:
    """Sayım tablosunun (son formül satırı) ve A3 başlığının altında örnek belirteci taşıyan ilk metin satırı."""
    floor = max([n for n, r in rows.items() if any(c.find(m("f")) is not None for c in r.findall(m("c")))] + [split_ref(TITLE_CELL)[1]])
    for number in sorted(n for n in rows if n > floor):
        if any(has_value(c) and find_tokens(cell_text(c, sst), tokens) for c in rows[number].findall(m("c"))):
            return number
    return None


def drop_merges_from(root: ET.Element, start: int) -> tuple[list[range], set[int]]:
    """start satırından başlayan birleşimleri siler. Döner: (silinenlerin satırları, kalan birleşimlerin satırları)."""
    merges = root.find(m("mergeCells"))
    if merges is None:
        return [], set()
    dropped = [mc for mc in list(merges) if merge_rows(mc.get("ref"))[0] >= start]
    for mc in dropped:
        merges.remove(mc)
    merges.set("count", str(len(merges)))
    covered = {r for mc in merges for r in merge_rows(mc.get("ref"))}
    if not len(merges):
        root.remove(merges)
    return [merge_rows(mc.get("ref")) for mc in dropped], covered


def strip_notes(sheet: Sheet, sst: list[str], tokens: list[str], stats: Stats) -> None:
    """Örnek belirtecini taşıyan ilk nottan itibaren metinler ve birleşimler silinir, satırlar boş ara satır olur;
    sayfa sonundaki not devam satırları atılır (Atınç'ın şablonu notsuz Özet'i orada bitirir)."""
    root, rows = sheet.doc.root, row_map(sheet.doc.root)
    start = first_note_row(rows, sst, tokens)
    if start is None:
        return
    stats.notes_removed = [c.get("r") for n in sorted(rows) if n >= start for c in rows[n].findall(m("c")) if has_value(c)]
    dropped, covered = drop_merges_from(root, start)
    spacer = next((rows[n] for n in sorted(rows, reverse=True) if n < start and blank_row(rows[n]) and n not in covered), None)
    if spacer is None:
        raise TemplateError(f"{SUMMARY_SHEET}: not bölgesinin üstünde boş ara satır yok")
    continuation, last = {r for span in dropped for r in span[1:]}, max(rows)
    while last >= start and last in continuation:
        last -= 1
    data = root.find(m("sheetData"))
    for number in sorted(n for n in rows if n >= start):
        index = list(data).index(rows[number])
        data.remove(rows[number])
        if number > last:
            stats.dropped_rows[sheet.name] += 1
            continue
        copy = deepcopy(spacer)
        copy.set("r", str(number))
        for cell in copy.findall(m("c")):
            cell.set("r", f"{split_ref(cell.get('r'))[0]}{number}")
        data.insert(index, copy)


# --- formüller: hedefe göre aralık ve boş şablon önbelleği --------------------------------------------------------------

def data_ends(sheets: list[Sheet]) -> dict[str, dict[str, int]]:
    """Sayfa -> sütun -> veri sonu (tablo sonu; formül sütunu daha uzunsa formülün son satırı)."""
    ends: dict[str, dict[str, int]] = {}
    for sheet in [s for s in sheets if s.table_end is not None]:
        cols: dict[str, int] = {"_table": sheet.table_end}
        for cell in sheet.doc.root.find(m("sheetData")).iter(m("c")):
            if cell.find(m("f")) is not None:
                col, row = split_ref(cell.get("r"))
                cols[col] = max(cols.get(col, 0), row)
        ends[sheet.name] = cols
    return ends


def refit_text(text: str, ends: dict[str, dict[str, int]]) -> str:
    def replace(match: re.Match) -> str:
        name = match["sheet"][1:-1].replace("''", "'") if match["sheet"].startswith("'") else match["sheet"]
        target = ends.get(name)
        if target is None or int(match["r1"]) != common.FIRST_DATA_ROW:
            return match.group(0)
        span = range(col_index(match["c1"]), col_index(match["c2"]) + 1)
        end = max([target["_table"]] + [target.get(col_letter(c), 0) for c in span])
        return f"{match['sheet']}!${match['c1']}${match['r1']}:${match['c2']}${end}"
    return RANGE_RE.sub(replace, text)


def refit_formulas(sheets: list[Sheet], book: "Book", stats: Stats) -> None:
    ends = data_ends(sheets)
    for sheet in sheets:
        for cell in sheet.doc.root.find(m("sheetData")).iter(m("c")):
            node = cell.find(m("f"))
            if node is not None and node.text and (new := refit_text(node.text, ends)) != node.text:
                stats.refits.append({"sheet": sheet.name, "cell": cell.get("r"), "old": node.text, "new": new})
                node.text = new
    for node in book.doc.root.iter(m("definedName")):
        node.text = refit_text(node.text or "", ends)


def empty_value(cells: dict[str, ET.Element], ref: str, seen: set[str]) -> float | None:
    """Boş şablonda hücrenin sayısal değeri: boş 0, sabit sayı kendisi, formül değerlendirilir, metin bilinmez."""
    cell = cells.get(ref)
    if cell is None or not len(cell):
        return 0.0
    if (node := cell.find(m("f"))) is not None:
        return None if ref in seen else evaluate(node.text or "", cells, seen | {ref})
    value = cell.find(m("v"))
    if value is None or not value.text or cell.get("t") not in (None, "n"):
        return None if has_value(cell) else 0.0
    try:
        return float(value.text)
    except ValueError:
        return None


def evaluate(text: str, cells: dict[str, ET.Element], seen: set[str]) -> float | None:
    """Yalnız bilinen desenler: sayım/toplam (veri sayfaları boş -> 0), MAX(fark,0), IF(A="",0,...)."""
    if COUNT_RE.match(text):
        return 0.0
    if match := MAX_DIFF_RE.match(text):
        a, b = (empty_value(cells, ref, seen) for ref in match.groups())
        return None if a is None or b is None else max(a - b, 0.0)
    if match := IF_BLANK_RE.match(text):
        anchor = cells.get(f"A{match.group(1) or match.group(2)}")
        return 0.0 if anchor is None or not has_value(anchor) else None
    return None


def write_cached(sheets: list[Sheet], stats: Stats) -> None:
    for sheet in sheets:
        cells = {c.get("r"): c for c in sheet.doc.root.find(m("sheetData")).iter(m("c"))}
        for ref, cell in [(r, c) for r, c in cells.items() if c.find(m("f")) is not None]:
            text = cell.find(m("f")).text
            set_cached(cell, value := evaluate(text, cells, {ref}) if text else None)
            if value is None:
                stats.uncached.append(f"{sheet.name}!{ref}")


# --- çalışma kitabı ----------------------------------------------------------------------------------------------------

@dataclass
class Book:
    part: str
    doc: XmlDoc
    rels: FlatXml
    sheets: list[Sheet]
    sst_part: str | None
    sst: list[str]

    @classmethod
    def load(cls, pkg: Package) -> "Book":
        office = next((a for a, _ in pkg.targets("") if a.get("Type", "").endswith("/officeDocument")), None)
        if office is None:
            raise TemplateError("çalışma kitabı parçası (officeDocument) bulunamadı")
        part = resolve("", office["Target"])
        doc, rels = pkg.xml(part), pkg.rels(part)
        if local(doc.root.tag) != "workbook" or doc.root.find(m("sheets")) is None or rels is None:
            raise TemplateError(f"{part} bir Excel çalışma kitabı değil (sekme listesi/ilişkileri yok)")
        targets = {a["Id"]: resolve(part, a["Target"]) for _, a in rels.items}
        rid = f"{{{DOC_REL_NS}}}id"
        sheets = [Sheet(s.get("name"), targets[s.get(rid)], s.get(rid), s) for s in doc.root.find(m("sheets"))]
        sst = next((resolve(part, a["Target"]) for _, a in rels.items if a["Type"].endswith("/sharedStrings")), None)
        if sst not in pkg.data:
            return cls(part, doc, rels, sheets, None, [])
        return cls(part, doc, rels, sheets, sst, [si_text(si) for si in pkg.xml(sst).root.findall(m("si"))])

    def drop_sheets(self, keep: list[Sheet], stats: Stats) -> None:
        old, kept = [s.name for s in self.sheets], [s.name for s in keep]
        container = self.doc.root.find(m("sheets"))
        for sheet in [s for s in self.sheets if s.name not in kept]:
            container.remove(sheet.element)
        for index, element in enumerate(container, start=1):
            element.set("sheetId", str(index))
        gone = {s.rid for s in self.sheets if s.name not in kept}
        self.rels.items = [(t, a) for t, a in self.rels.items if a["Id"] not in gone and not a["Type"].endswith("/calcChain")]
        self.fix_names(old, kept, stats)
        for view in self.doc.root.iter(m("workbookView")):
            for attr in [a for a in ("activeTab", "firstSheet") if view.get(a) is not None]:
                index = int(view.get(attr))
                name = old[index] if index < len(old) else None
                view.set(attr, str(kept.index(name)) if name in kept else "0")

    def fix_names(self, old: list[str], kept: list[str], stats: Stats) -> None:
        names = self.doc.root.find(m("definedNames"))
        gone = [n for n in old if n not in kept]
        references = ["'" + g.replace("'", "''") + "'!" for g in gone] + [g + "!" for g in gone]
        for node in list(names) if names is not None else []:
            scope, text = node.get("localSheetId"), node.text or ""
            if any(r in text for r in references) or (scope is not None and old[int(scope)] in gone):
                names.remove(node)
                stats.names_removed.append(node.get("name"))
            elif scope is not None:
                node.set("localSheetId", str(kept.index(old[int(scope)])))
        if names is not None and not len(names):
            self.doc.root.remove(names)

    def compact_strings(self, sheets: list[Sheet], pkg: Package) -> None:
        """Paylaşımlı metin tablosunda yalnız hâlâ kullanılan metinler kalır (silinen örnek metni dosyada kalmaz)."""
        if self.sst_part is None:
            return
        cells = [c for s in sheets for c in s.doc.root.iter(m("c")) if c.get("t") == "s" and c.find(m("v")) is not None]
        used = sorted({int(c.find(m("v")).text) for c in cells})
        doc = pkg.xml(self.sst_part)
        items = doc.root.findall(m("si"))
        if len(used) == len(items):
            return
        index = {old: new for new, old in enumerate(used)}
        for cell in cells:
            cell.find(m("v")).text = str(index[int(cell.find(m("v")).text)])
        for item in [it for position, it in enumerate(items) if position not in index]:
            doc.root.remove(item)
        doc.root.set("count", str(len(cells)))
        doc.root.set("uniqueCount", str(len(used)))
        pkg.put(self.sst_part, doc)
