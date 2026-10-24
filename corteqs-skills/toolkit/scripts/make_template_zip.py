"""make_template yardımcısı: zip/XML katmanı ve yeniden numaralama.

Paket bellekte açılır, parçalar XML olarak okunup yazılır (openpyxl kaydetmez; öznitelik/ad alanı kaybı yok). Burada:
XML ve düz paket XML'i, ilişkiler, parça silme/yeniden adlandırma, kalan sayfa/tablo parçalarının Atınç'ın adlarıyla
yeniden numaralanması, paket tutarlılık denetimi ([Content_Types].xml ve ilişkiler) ve hücre/aralık XML yardımcıları.
"""
from __future__ import annotations

import datetime as _dt
import io
import posixpath
import re
import unicodedata
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from openpyxl.utils.cell import column_index_from_string as col_index, get_column_letter as col_letter, range_boundaries

if TYPE_CHECKING:
    from make_template_sheets import Sheet

MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
ATTR_ESCAPES = {'"': "&quot;"}
COORD_RE = re.compile(r"^([A-Z]{1,3})(\d+)$")
NS_DECL_RE = re.compile(r'xmlns:([A-Za-z_][\w.\-]*)="([^"]*)"')


class TemplateError(Exception):
    """Kullanım veya yapı hatası (çıkış 2)."""


def m(tag: str) -> str:
    return f"{{{MAIN_NS}}}{tag}"


def local(tag: Any) -> str:
    return tag.rsplit("}", 1)[-1] if isinstance(tag, str) else ""


# --- XML ve paket ---------------------------------------------------------------------------------------------

@dataclass
class XmlDoc:
    root: ET.Element
    prolog: str
    decls: dict[str, str]  # önek -> ad alanı; kök etikete geri yazılır (mc:Ignorable önekleri kaybolmaz)

    @classmethod
    def parse(cls, data: bytes) -> "XmlDoc":
        text = data.decode("utf-8")
        start = re.search(r"<(?![?!])", text)
        if start is None:
            raise TemplateError("boş XML parçası")
        decls: dict[str, str] = {}
        for prefix, uri in NS_DECL_RE.findall(text):
            decls.setdefault(prefix, uri)
        default = re.search(r'\sxmlns="([^"]*)"', text[start.start(): text.index(">", start.start())])
        if default and default.group(1) not in decls.values():
            decls["x" if "x" not in decls else "xmain"] = default.group(1)  # ElementTree varsayılan ad alanını yazamaz
        parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
        return cls(ET.fromstring(data, parser=parser), text[: start.start()], decls)

    def dump(self) -> bytes:
        for prefix, uri in self.decls.items():
            if prefix != "xml" and not re.fullmatch(r"ns\d+", prefix):
                ET.register_namespace(prefix, uri)
        body = ET.tostring(self.root, encoding="unicode")
        end = body.index(">")
        missing = "".join(f' xmlns:{p}="{u}"' for p, u in self.decls.items() if p != "xml" and f'xmlns:{p}="' not in body[:end])
        cut = end - 1 if body[end - 1] == "/" else end
        return (self.prolog + body[:cut] + missing + body[cut:]).encode("utf-8")


@dataclass
class FlatXml:
    """Düz paket XML'i (.rels, [Content_Types].xml); öğe ve öznitelik sırası korunarak elle yazılır."""
    prolog: str
    tag: str
    namespace: str
    items: list[tuple[str, dict[str, str]]]

    @classmethod
    def parse(cls, data: bytes) -> "FlatXml":
        doc = XmlDoc.parse(data)
        return cls(doc.prolog, local(doc.root.tag), doc.root.tag[1:].split("}")[0], [(local(e.tag), dict(e.attrib)) for e in doc.root])

    def dump(self) -> bytes:
        body = "".join(f"<{t} " + " ".join(f'{k}="{escape(v, ATTR_ESCAPES)}"' for k, v in a.items()) + " />"
                       for t, a in self.items)
        return f'{self.prolog}<{self.tag} xmlns="{self.namespace}">{body}</{self.tag}>'.encode("utf-8")


def rels_name(part: str) -> str:
    folder, base = posixpath.split(part)
    return posixpath.join(folder, "_rels", base + ".rels")


def rels_source(name: str) -> str:
    folder, base = posixpath.split(name)
    return "" if base == ".rels" else posixpath.join(posixpath.dirname(folder), base[: -len(".rels")])


def resolve(source: str, target: str) -> str:
    return target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(posixpath.dirname(source), target))


def retarget(source: str, original: str, new_part: str) -> str:
    return "/" + new_part if original.startswith("/") else posixpath.relpath(new_part, posixpath.dirname(source) or ".")


@dataclass
class Package:
    """Zip'in bellekteki çalışma kopyası; --base dosyası hiç değişmez."""
    infos: dict[str, zipfile.ZipInfo]
    data: dict[str, bytes]

    @classmethod
    def load(cls, source: Path | bytes) -> "Package":
        try:
            with zipfile.ZipFile(io.BytesIO(source) if isinstance(source, bytes) else source) as archive:
                infos = {i.filename: i for i in archive.infolist() if not i.is_dir()}
                return cls(infos, {name: archive.read(name) for name in infos})
        except (OSError, zipfile.BadZipFile, KeyError) as exc:
            raise TemplateError(f"xlsx okunamadı: {type(exc).__name__}: {exc}") from exc

    def xml(self, name: str) -> XmlDoc:
        return XmlDoc.parse(self.data[name])

    def put(self, name: str, payload: XmlDoc | FlatXml) -> None:
        self.data[name] = payload.dump()

    def rels(self, source: str) -> FlatXml | None:
        return FlatXml.parse(self.data[rels_name(source)]) if rels_name(source) in self.data else None

    def targets(self, source: str) -> list[tuple[dict[str, str], str]]:
        rels = self.rels(source)
        return [(a, resolve(source, a["Target"])) for _, a in (rels.items if rels else []) if a.get("TargetMode") != "External"]

    def unreachable(self) -> list[str]:
        """Kök ilişkilerden erişilemeyen parçalar (silinen sekmeler, çizimleri, görseller, calcChain)."""
        keep, stack = {"[Content_Types].xml"}, [""]
        while stack:
            source = stack.pop()
            keep.add(rels_name(source))
            for _, target in self.targets(source):
                if target in self.data and target not in keep:
                    keep.add(target)
                    stack.append(target)
        return [n for n in self.infos if n not in keep]

    def drop(self, names: list[str]) -> None:
        for name in names:
            self.infos.pop(name, None)
            self.data.pop(name, None)

    def rename(self, mapping: dict[str, str]) -> None:
        self.infos = {mapping.get(n, n): i for n, i in self.infos.items()}
        self.data = {mapping.get(n, n): d for n, d in self.data.items()}

    def to_bytes(self) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            for name, info in self.infos.items():
                entry = zipfile.ZipInfo(name, date_time=info.date_time)  # aynı girdi = aynı bayt (tekrar üretilebilir)
                entry.compress_type, entry.external_attr = info.compress_type, info.external_attr
                archive.writestr(entry, self.data[name])
        return buffer.getvalue()


# --- yeniden numaralama ve paket denetimi -----------------------------------------------------------------------------

def renumber(pkg: Package, keep: list[Sheet]) -> dict[str, str]:
    """Kalan sayfa ve tablo parçaları sırayla numaralanır (sheet1..N, table1..M; tablo id'leri de) - Atınç'ın adlarıyla aynı."""
    # İçerik türü kayıtları yeniden adlandırmadan ÖNCEKİ adlara göre süzülür: silinen sekmenin eski kaydı, o adı yeni alan
    # parçanın kaydıyla yinelenmez (yinelenen kayıt = Excel ve .NET dosyayı açmaz). OPC adları harf duyarsızdır.
    present = {n.casefold(): n for n in pkg.data}
    mapping, table_no = {}, 0
    for index, sheet in enumerate(keep, start=1):
        mapping[sheet.part] = posixpath.join(posixpath.dirname(sheet.part), f"sheet{index}.xml")
        for attrs, target in [t for t in pkg.targets(sheet.part) if t[0]["Type"].endswith("/table")]:
            table_no += 1
            mapping[target] = posixpath.join(posixpath.dirname(target), f"table{table_no}.xml")
            doc = pkg.xml(target)
            doc.root.set("id", str(table_no))
            pkg.put(target, doc)
    mapping.update({rels_name(o): rels_name(n) for o, n in list(mapping.items()) if rels_name(o) in pkg.data})
    mapping = {k: v for k, v in mapping.items() if k != v}
    if clash := [n for n in pkg.infos if n in set(mapping.values()) and n not in mapping]:
        raise TemplateError(f"yeniden numaralamada ad çakışması: {clash}")
    for name in [n for n in pkg.infos if n.endswith(".rels")]:
        source, rels = rels_source(name), FlatXml.parse(pkg.data[name])
        hits = [a for _, a in rels.items if a.get("TargetMode") != "External" and resolve(source, a["Target"]) in mapping]
        for attrs in hits:
            attrs["Target"] = retarget(mapping.get(source, source), attrs["Target"], mapping[resolve(source, attrs["Target"])])
        if hits:
            pkg.put(name, rels)
    pkg.rename(mapping)
    types = FlatXml.parse(pkg.data["[Content_Types].xml"])
    extensions = {posixpath.splitext(n)[1].lstrip(".").casefold() for n in pkg.infos} | {"rels", "xml"}
    items = []
    for tag, attrs in types.items:
        old = present.get(attrs.get("PartName", "").lstrip("/").casefold())
        if (tag == "Override" and old is None) or (tag == "Default" and attrs.get("Extension", "").casefold() not in extensions):
            continue
        items.append((tag, {**attrs, "PartName": "/" + mapping.get(old, old)} if tag == "Override" else attrs))
    types.items = items
    pkg.put("[Content_Types].xml", types)
    return mapping


def extension(name: str) -> str:
    base = posixpath.basename(name)
    return base.rpartition(".")[2].casefold() if "." in base else ""  # "_rels/.rels" -> "rels" (splitext "" verir)


def package_findings(pkg: Package) -> list[str]:
    """Excel ve .NET (System.IO.Packaging) paketi katı okur; biri bozuksa dosya açılmaz. Adlar harf duyarsız karşılaştırılır."""
    types = FlatXml.parse(pkg.data["[Content_Types].xml"])
    names = {n.casefold(): n for n in pkg.data if n != "[Content_Types].xml"}
    overrides = [a.get("PartName", "").lstrip("/").casefold() for t, a in types.items if t == "Override"]
    defaults = [a.get("Extension", "").casefold() for t, a in types.items if t == "Default"]
    listed = set(overrides)
    problems = {
        "[Content_Types].xml'de iki kez kayıtlı parça": [n for n, c in Counter(overrides).items() if c > 1],
        "[Content_Types].xml'de iki kez kayıtlı uzantı": [n for n, c in Counter(defaults).items() if c > 1],
        "[Content_Types].xml kaydının parçası yok": [n for n in listed if n not in names],
        "içerik türü olmayan parça": [v for k, v in names.items() if k not in listed and extension(k) not in defaults],
        "ilişkinin hedef parçası yok": [t for r in pkg.data if r.endswith(".rels") for _, t in pkg.targets(rels_source(r))
                                         if t not in pkg.data],
    }
    return [f"paket: {label}: {sorted(set(found))[:5]}" for label, found in problems.items() if found]


# --- hücre yardımcıları ------------------------------------------------------------------------------------------------

def split_ref(ref: str | None) -> tuple[str, int]:
    match = COORD_RE.match(ref or "")
    if not match:
        raise TemplateError(f"desteklenmeyen hücre adresi: {ref!r}")
    return match.group(1), int(match.group(2))


def has_value(cell: ET.Element) -> bool:
    return cell.find(m("f")) is None and any(local(c.tag) in ("v", "is") for c in cell)


def blank_row(row: ET.Element) -> bool:
    return not any(has_value(c) for c in row.findall(m("c")))


def si_text(si: ET.Element) -> str:
    """Paylaşımlı/satır içi metin: düz <t> ve zengin metin <r><t>; fonetik <rPh> hariç."""
    parts = [si.find(m("t"))] + [r.find(m("t")) for r in si.findall(m("r"))]
    return "".join(p.text or "" for p in parts if p is not None)


def cell_text(cell: ET.Element, sst: list[str]) -> str | None:
    if cell.find(m("f")) is not None:
        return cell.find(m("f")).text
    if cell.get("t") == "inlineStr":
        return si_text(cell.find(m("is"))) if cell.find(m("is")) is not None else None
    value = cell.find(m("v"))
    if value is None or value.text is None:
        return None
    return sst[int(value.text)] if cell.get("t") == "s" else value.text


def row_map(root: ET.Element) -> dict[int, ET.Element]:
    rows = {}
    for row in root.find(m("sheetData")):
        if row.get("r") is None:
            raise TemplateError("satır numarası (r) olmayan satır desteklenmiyor")
        rows[int(row.get("r"))] = row
    return rows


def strip_cell(cell: ET.Element) -> None:
    for child in list(cell):
        cell.remove(child)
    for attr in ("t", "cm", "vm"):
        cell.attrib.pop(attr, None)


def get_cell(row: ET.Element, ref: str) -> ET.Element:
    col = col_index(split_ref(ref)[0])
    for cell in row.findall(m("c")):
        current = col_index(split_ref(cell.get("r"))[0])
        if current == col:
            return cell
        if current > col:
            row.insert(list(row).index(cell), new := ET.Element(m("c"), {"r": ref}))
            return new
    return ET.SubElement(row, m("c"), {"r": ref})


def number_text(value: float) -> str:
    return str(int(value)) if float(value).is_integer() else repr(float(value))


def set_value(cell: ET.Element, value: Any, text_type: str) -> None:
    strip_cell(cell)
    if isinstance(value, str) and text_type == "inlineStr":
        cell.set("t", "inlineStr")
        node = ET.SubElement(ET.SubElement(cell, m("is")), m("t"))
        node.text = value
        if value != value.strip():
            node.set(XML_SPACE, "preserve")
        return
    kind, text = (("str", value) if isinstance(value, str) else
                  ("d", f"{value.isoformat()}T00:00:00.000Z") if isinstance(value, _dt.date) else ("n", number_text(value)))
    cell.set("t", kind)
    ET.SubElement(cell, m("v")).text = text


def set_cached(cell: ET.Element, value: float | None) -> None:
    """Formül önbelleği: bilinen değer -> <v>; bilinmeyen -> önbellek kaldırılır (yanlış sayı gösterilmez)."""
    for child in [c for c in cell if local(c.tag) == "v"]:
        cell.remove(child)
    cell.attrib.pop("t", None)
    if value is not None:
        cell.set("t", "n")
        node = ET.Element(m("v"))
        node.text = number_text(value)
        cell.insert(list(cell).index(cell.find(m("f"))) + 1, node)


def clip_sqref(sqref: str, end: int, old_end: int) -> str:
    """end+1..old_end bandı silinir: banttaki aralık atılır, bandı kesen aralık end'de biter."""
    kept = []
    for token in sqref.split():
        min_col, min_row, max_col, max_row = range_boundaries(token)
        if min_row is None or max_row <= end or min_row > old_end:
            kept.append(token)
        elif max_row > old_end:
            raise TemplateError(f"aralık silinen satırların ötesine taşıyor (desteklenmiyor): {token}")
        elif min_row <= end:
            kept.append(f"{col_letter(min_col)}{min_row}:{col_letter(max_col)}{end}")
    return " ".join(kept)


def fold(text: str) -> str:
    """Harf ve aksan duyarsız biçim (build_xlsx.ascii_name gibi): 'BERLİN' -> 'berlin'; casefold 'berli̇n' verir, kaçırır."""
    text = unicodedata.normalize("NFKD", text.replace("ı", "i").replace("İ", "I"))
    return "".join(ch for ch in text if not unicodedata.combining(ch)).casefold()


def find_tokens(text: str | None, tokens: list[str]) -> list[str]:
    """tokens fold() ile hazırlanmış olmalı (sample_identity)."""
    low = fold(text or "")
    return [t for t in tokens if t in low]
