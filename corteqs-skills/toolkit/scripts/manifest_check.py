r"""Manifest kontrolu (IYILESTIRME_LISTESI C4): <WORK>\manifest.json semaya ve phase_log'a uyuyor mu.

Kullanim:
  manifest_check.py <WORK>\manifest.json [--schema manifest.schema.json] [--phase-log <WORK>\_is\phase_log.jsonl]
                    [--pkg <PKG>] [--out rapor.json]

Bulgular (kod):
  sema           manifest.schema.json'a uymuyor (Draft 2020-12; 'date' ve 'date-time' bicimi de denetlenir: saat
                 dilimsiz zaman ve PowerShell'in yerel tarih bicimi reddedilir).
  dosya          manifest UTF-8 BOM ile yazilmis (render_summary okuyamaz; Python ile BOM'suz yazilir).
  log_kaydi      phase_log satiri okunamiyor (JSON degil, phase/event/ts eksik ya da gecersiz, BOM) ya da faz adi
                 semada yok (ad basina bir kez).
  log_penceresi  phase_usage kurallari: start acikken yeniden start, eslesen start'i olmayan end, end start'tan once,
                 pencereler cakisiyor (phase_usage report bunlarda durur).
  isaret         'done' fazin phase_log'da start ve end isareti yok ya da son penceresi acik; 'running' fazin start
                 isareti yok ya da penceresi kapali.
  coklu_running  birden cok 'running' faz.
  faz_sirasi     fazlar semadaki sirayla ($defs.phase_name.enum) ilerlemiyor: bitmemis (pending/running) fazdan sonraki
                 faz baslamis; ust duzey 'phase' fazlarin durumuna uymuyor; phase_log'da (her fazin ilk start'i) ya da
                 manifest zamanlarinda fazlar bu sirayla baslamiyor ya da cakisiyor (manifest'te 1 sn yuvarlama payi).
  zaman          manifest'te bir fazin ended_at'i started_at'tan once (run_log bunda durur).
  teslim         deliver 'done' ama delivered.xlsx_sha256 yok; --pkg verilirse teslim Excel'i bulunamadi ya da
                 SHA-256'si delivered.xlsx_sha256 ile ayni degil.
'blocked' faz sonraki fazlari durdurmaz (son baslayan faz blocked ise ust duzey 'phase' sonraki faz da olabilir).
'pending' fazda isaret aranmaz (phase_log faz basinda, manifest faz sonunda yazilir). Kaydi olmayan faz 'pending'
sayilir; gecersiz durumlu faz yalniz sema bulgusu verir.
Yeniden acilan faz (duzeltme turu; SKILL: her duzeltmeden sonra zincir bastan) sirayi bozmaz: phase_log'da her fazin
ilk start'i sayilir. Manifest faz basina tek pencere tutar: phase_log'da bir faz, sonraki faz basladiktan sonra yeniden
acildiysa bu iki fazin manifest zamanlari birbiriyle karsilastirilmaz (sira log'daki ilk start'larla denetlenir).

Varsayilanlar: --schema = <corteqs-skills>\city-pack\references\manifest.schema.json; --phase-log = <manifest
klasoru>\_is\phase_log.jsonl (yoksa bos sayilir; elle verilen dosya yoksa cikis 2). Teslim Excel'i: --pkg kokunde
paths.delivery_xlsx'in dosya adi; o alan yoksa koktaki tek .xlsx (~$ kilit dosyasi ve alt klasorler sayilmaz).
Salt okunur: girdilere yazmaz. --out (tam rapor JSON) bir girdinin ustune ya da paket klasorune yazilmaz (--pkg,
paths.package_root -goreli ise manifest klasorune gore, run_log gibi- ve SKILL duzenindeki <manifest klasoru>\paket).
stdout tek satir JSON (ilk MAX_ITEMS bulgu). Cikis: 0 temiz / 1 bulgu / 2 kullanim hatasi ya da okunamayan girdi.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

try:  # requirements.txt; yoksa cikis 2 (yakalanmayan ImportError cikis 1 olur, 'bulgu' ile karisir)
    import jsonschema
    from jsonschema.validators import validator_for
    from referencing.exceptions import Unresolvable
except ImportError:  # pragma: no cover - kurulum hatasi
    jsonschema = None

import common
import phase_usage

TOOL = "manifest_check"
DEFAULT_SCHEMA = Path(__file__).resolve().parents[2] / "city-pack" / "references" / "manifest.schema.json"
LOG_RELATIVE = Path("_is") / "phase_log.jsonl"  # SKILL.md: phase_usage mark ... --log $WORK\_is\phase_log.jsonl
MAX_ITEMS = 20  # stdout'taki bulgu sayisi; tamami --out raporunda
STATUSES = ("pending", "running", "done", "blocked")  # manifest.schema $defs.phase_state.status
STARTED = ("running", "done", "blocked")
ENDED = ("done", "blocked")  # faz kapandi: sonraki faza gecilebilir ('blocked' sonrakileri durdurmaz)
DELIVER_PHASE = "deliver"  # delivered alani bu fazin ciktisi (SKILL.md faz 7)
PACKAGE_DIR = "paket"  # SKILL.md: PKG = WORK\paket (manifest WORK kokunde)
EVENTS = phase_usage.EVENTS
ROUNDING_SLACK = dt.timedelta(seconds=1)  # manifest zamanlari saniyeye yuvarlanmis yazilabilir
BOM = chr(0xFEFF)  # UTF-8 BOM; kaynakta gorunmez karakter tutulmaz
ROOT_WHERE = "(kök)"
FILE_WHERE = "(dosya)"
RFC3339 = re.compile(r"\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})")
FORMAT_HINTS = {"date-time": "RFC 3339 tarih-saat değil (ör. 2026-10-22T13:19:53Z; saat dilimi şart)",
                "date": "tarih değil (YYYY-AA-GG)"}
JSON_TYPES = {dict: "object", list: "array", str: "string", bool: "boolean", int: "integer", float: "number",
              type(None): "null"}


class UsageError(Exception):
    """Kullanim hatasi ya da okunamayan girdi (cikis 2)."""


@dataclass(frozen=True)
class Finding:
    code: str
    where: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "where": self.where, "message": self.message}


@dataclass(frozen=True)
class Mark:
    line: int
    phase: str
    event: str
    ts: dt.datetime


@dataclass(frozen=True)
class Window:
    phase: str
    start: Mark
    end: Mark | None  # None: pencere acik


@dataclass(frozen=True)
class PhaseLog:
    path: Path
    found: bool
    marks: tuple[Mark, ...]
    findings: tuple[Finding, ...]


@dataclass(frozen=True)
class Span:
    name: str
    start: dt.datetime
    end: dt.datetime | None


# ---------- okuma ----------

def read_bytes(path: Path, label: str) -> bytes:
    try:
        return Path(path).read_bytes()
    except FileNotFoundError as exc:
        raise UsageError(f"{label} yok: {path}") from exc
    except OSError as exc:
        raise UsageError(f"{label} okunamadı: {path} ({exc.strerror or exc})") from exc


def read_text(path: Path, label: str) -> str:
    try:
        return read_bytes(path, label).decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UsageError(f"{label} UTF-8 değil: {path}") from exc


def load_json(path: Path, label: str) -> tuple[Any, bool]:
    """(icerik, BOM var mi). BOM'lu dosya da okunur; manifest'te BOM ayrica bulgudur."""
    text = read_text(path, label)
    try:
        return json.loads(text.removeprefix(BOM)), text.startswith(BOM)
    except json.JSONDecodeError as exc:
        raise UsageError(f"{label} JSON değil: {path} ({exc.msg}, satır {exc.lineno})") from exc


# ---------- sema ----------

def is_datetime(value: object) -> bool:
    """RFC 3339 tarih-saat, saat dilimi zorunlu (2026-10-22T13:19:53Z). Metin olmayan deger 'type' kuralinindir."""
    if not isinstance(value, str):
        return True
    if not RFC3339.fullmatch(value):
        return False
    try:
        dt.datetime.fromisoformat(value.upper())
    except ValueError:
        return False
    return True


def make_validator(schema: Any) -> Any:
    if jsonschema is None:
        raise UsageError("jsonschema kurulu değil: pip install -r toolkit\\requirements.txt")
    if not isinstance(schema, dict):
        raise UsageError("şema JSON nesnesi değil")
    cls = validator_for(schema, default=jsonschema.Draft202012Validator)
    try:
        cls.check_schema(schema)
    except jsonschema.exceptions.SchemaError as exc:
        raise UsageError(f"şema geçersiz: {exc.message}") from exc
    checker = jsonschema.FormatChecker()  # ornek kendi kopyasini tutar; genel kayit degismez
    checker.checks("date-time")(is_datetime)  # rfc3339-validator kurulu degilken jsonschema date-time'i atlar
    return cls(schema, format_checker=checker)


def phase_order(schema: dict) -> tuple[str, ...]:
    """Faz sirasi semadan: $defs.phase_name.enum."""
    defs = schema.get("$defs") if isinstance(schema.get("$defs"), dict) else {}
    names = defs.get("phase_name", {}).get("enum") if isinstance(defs.get("phase_name"), dict) else None
    if not (isinstance(names, list) and names and all(isinstance(n, str) and n for n in names)
            and len(set(names)) == len(names)):
        raise UsageError("şemada faz sırası yok ya da bozuk ($defs.phase_name.enum)")
    return tuple(names)


def where_of(parts: Iterable[Any]) -> str:
    """['phases', 'places', 'gates', 0] -> 'phases.places.gates[0]'."""
    text = ""
    for part in parts:
        text += f"[{part}]" if isinstance(part, int) else (f".{part}" if text else str(part))
    return text or ROOT_WHERE


def show(value: Any, limit: int = 60) -> str:
    text = f"'{value}'" if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _choices(values: Iterable[Any]) -> str:
    return ", ".join(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False) for v in values)


def schema_message(error: Any) -> str:
    """jsonschema hatasinin Turkce, kisa metni; tanimadigi kuralda kutuphanenin metni."""
    kind, rule, value = error.validator, error.validator_value, error.instance
    if "propertyNames" in error.schema_path:
        return f"izinsiz anahtar: {show(value)}" + (f" (izinli: {_choices(rule)})" if kind == "enum" else "")
    if kind == "required":
        return f"zorunlu alan eksik: {', '.join(key for key in rule if key not in value)}"
    if kind == "additionalProperties" and isinstance(value, dict):
        extra = sorted(set(value) - set(error.schema.get("properties", {})))
        return f"şemada olmayan alan: {', '.join(extra)}" if extra else error.message
    if kind == "enum":
        return f"izinli değer değil: {show(value)} (izinli: {_choices(rule)})"
    if kind == "const":
        return f"değer {show(rule)} olmalı ({show(value)} yazılmış)"
    if kind == "type":
        expected = "/".join(rule) if isinstance(rule, list) else rule
        return f"tür {expected} olmalı ({JSON_TYPES.get(type(value), '?')} yazılmış)"
    if kind == "pattern":
        return f"{show(value)} biçime uymuyor ({rule})"
    if kind == "format":
        return f"{show(value)} {FORMAT_HINTS.get(rule, f'{rule} biçiminde değil')}"
    if kind in ("minimum", "minLength"):
        return f"en az {rule}{' karakter' if kind == 'minLength' else ''} olmalı ({show(value)} yazılmış)"
    return error.message


def _path_key(error: Any) -> list[tuple[bool, Any]]:
    """Yola gore sayisal sira (open_items[2] < open_items[10]); int ile str hic karsilastirilmaz."""
    return [(isinstance(part, str), part) for part in error.absolute_path]


def schema_findings(validator: Any, manifest: Any) -> list[Finding]:
    try:
        errors = sorted(validator.iter_errors(manifest), key=_path_key)
    except Unresolvable as exc:
        raise UsageError(f"şemadaki $ref çözülemedi: {exc}") from exc
    return [Finding("sema", where_of(error.absolute_path), schema_message(error)) for error in errors]


# ---------- phase_log ----------

def parse_mark(number: int, raw: str) -> tuple[Mark | None, Finding | None]:
    """phase_usage.read_log kurallari; ilk sorunda bulgu (dosya okunmaya devam eder)."""
    where = f"phase_log satır {number}"
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError as exc:
        return None, Finding("log_kaydi", where, f"JSON değil ({exc.msg})")
    if not isinstance(obj, dict):
        return None, Finding("log_kaydi", where, "JSON nesnesi değil")
    phase, event, ts = obj.get("phase"), obj.get("event"), obj.get("ts")
    if not isinstance(phase, str) or not phase.strip():
        return None, Finding("log_kaydi", where, "faz adı (phase) yok")
    if event not in EVENTS:
        return None, Finding("log_kaydi", where, f"event 'start' ya da 'end' olmalı ({show(event)})")
    try:
        stamp = phase_usage.parse_ts(ts)
    except ValueError:
        return None, Finding("log_kaydi", where, f"geçersiz zaman (ts): {show(ts)}")
    return Mark(number, phase, event, stamp), None


def read_phase_log(path: Path, explicit: bool, order: Sequence[str]) -> PhaseLog:
    """Dosya yoksa (varsayilan yol) bos log; elle verilen yol yoksa UsageError."""
    if not explicit and not path.exists():
        return PhaseLog(path, False, (), ())
    marks: list[Mark] = []
    findings: list[Finding] = []
    unknown: set[str] = set()
    for number, raw in enumerate(read_text(path, "phase_log").splitlines(), start=1):
        if not raw.strip():
            continue
        where = f"phase_log satır {number}"
        if raw.startswith(BOM):  # phase_usage utf-8 (BOM'suz) okur: bu satirda durur
            findings.append(Finding("log_kaydi", where, "UTF-8 BOM var (phase_usage okuyamaz; BOM'suz yaz)"))
        mark, problem = parse_mark(number, raw.removeprefix(BOM))
        if problem is not None:
            findings.append(problem)
            continue
        if mark.phase not in order and mark.phase not in unknown:
            unknown.add(mark.phase)
            findings.append(Finding("log_kaydi", where, f"şemada olmayan faz adı: {show(mark.phase)}"))
        marks.append(mark)
    return PhaseLog(path, True, tuple(marks), tuple(findings))


def pair_windows(marks: Sequence[Mark]) -> tuple[list[Window], list[Finding]]:
    """phase_usage.build_windows kurallari (dosya sirasi) ama ilk hatada durmaz. Pencereler baslangica gore sirali."""
    open_starts: dict[str, Mark] = {}
    windows: list[Window] = []
    findings: list[Finding] = []
    for mark in marks:
        where = f"phase_log satır {mark.line}"
        if mark.event == "start":
            if mark.phase in open_starts:
                findings.append(Finding("log_penceresi", where, f"'{mark.phase}' zaten açıkken yeniden start "
                                                                f"(açık start satır {open_starts[mark.phase].line})"))
            else:
                open_starts[mark.phase] = mark
            continue
        start = open_starts.pop(mark.phase, None)
        if start is None:
            findings.append(Finding("log_penceresi", where, f"'{mark.phase}' end işaretinin eşleşen start'ı yok"))
            continue
        if mark.ts < start.ts:
            findings.append(Finding("log_penceresi", where, f"'{mark.phase}' end işareti ({_ts(mark.ts)}) start'tan "
                                                            f"({_ts(start.ts)}, satır {start.line}) önce"))
        windows.append(Window(mark.phase, start, mark))
    windows += [Window(phase, start, None) for phase, start in open_starts.items()]
    return sorted(windows, key=lambda w: (w.start.ts, w.start.line)), findings


def overlap_findings(windows: Sequence[Window]) -> list[Finding]:
    """phase_usage.check_overlaps: onceki pencere kapanmadan sonraki baslamamali."""
    return [Finding("log_penceresi", f"phase_log satır {nxt.start.line}",
                    f"'{prev.phase}' penceresi (satır {prev.start.line}) kapanmadan '{nxt.phase}' başlamış; "
                    "phase_usage report bunu reddeder")
            for prev, nxt in zip(windows, windows[1:]) if prev.end is None or nxt.start.ts < prev.end.ts]


def start_marks(windows: Sequence[Window], order: Sequence[str]) -> dict[str, list[Mark]]:
    """Faz -> pencerelerinin start'lari, zaman sirasiyla (ilki fazin ilk start'i); semada olmayan faz atlanir."""
    starts: dict[str, list[Mark]] = {}
    for window in windows:  # pencereler baslangica gore sirali
        if window.phase in order:
            starts.setdefault(window.phase, []).append(window.start)
    return starts


def log_order_findings(starts: dict[str, list[Mark]], order: Sequence[str]) -> list[Finding]:
    """Her fazin ilk start'i sema sirasini izler; sonradan yeniden acilan pencere (duzeltme turu) sayilmaz."""
    sequence = sorted(((name, marks[0]) for name, marks in starts.items()),
                      key=lambda item: (item[1].ts, order.index(item[0])))
    return [Finding("faz_sirasi", f"phase_log satır {mark.line}",
                    f"'{name}' fazı '{prev}' fazından sonra başlamış; şema sırasında önce gelir")
            for (prev, _), (name, mark) in zip(sequence, sequence[1:]) if order.index(name) < order.index(prev)]


def reopened_after(starts: dict[str, list[Mark]], earlier: str, later: str) -> bool:
    """phase_log'da 'earlier' fazi, 'later' fazi ilk kez basladiktan sonra yeniden acilmis (ilk penceresi disinda)."""
    begun = starts.get(later)
    return begun is not None and any(mark.ts > begun[0].ts for mark in starts.get(earlier, [])[1:])


def _ts(value: dt.datetime) -> str:
    return phase_usage.format_ts(value)


# ---------- manifest durumu ----------

def phase_states(manifest: Any, order: Sequence[str]) -> dict[str, str | None] | None:
    """Faz -> durum. Kaydi olmayan faz 'pending', gecersiz durum None; phases nesne degilse None (sema bulgusu)."""
    phases = manifest.get("phases") if isinstance(manifest, dict) else None
    if not isinstance(phases, dict):
        return None
    states: dict[str, str | None] = {}
    for name in order:
        raw = phases.get(name)
        status = raw.get("status") if isinstance(raw, dict) else None
        states[name] = "pending" if raw is None else (status if status in STATUSES else None)
    return states


def mark_findings(states: dict[str, str | None], marks: Sequence[Mark], windows: Sequence[Window]) -> list[Finding]:
    """done: start ve end isareti var, son pencere kapali. running: start var, son pencere acik."""
    events = {(mark.phase, mark.event) for mark in marks}
    last = {window.phase: window for window in windows}  # pencereler baslangica gore sirali: en son acilan kalir
    findings = []
    for name, state in states.items():
        where = f"phases.{name}"
        if state == "done":
            missing = [event for event in EVENTS if (name, event) not in events]
            if missing:
                findings.append(Finding("isaret", where, f"done ama phase_log'da {' ve '.join(missing)} işareti yok"))
            elif last[name].end is None:
                findings.append(Finding("isaret", where, f"done ama phase_log'daki son penceresi açık "
                                                         f"(satır {last[name].start.line} start'ının end'i yok)"))
        elif state == "running":
            if (name, "start") not in events:
                findings.append(Finding("isaret", where, "running ama phase_log'da start işareti yok"))
            elif last[name].end is not None:
                findings.append(Finding("isaret", where, f"running ama phase_log'daki penceresi kapalı (end satır "
                                                         f"{last[name].end.line}); faz bittiyse manifest'te done yaz"))
    return findings


def running_findings(states: dict[str, str | None]) -> list[Finding]:
    running = [name for name, state in states.items() if state == "running"]
    message = f"birden çok running faz: {', '.join(running)} (en çok bir tane olabilir)"
    return [Finding("coklu_running", "phases", message)] if len(running) > 1 else []


def status_order_findings(states: dict[str, str | None], order: Sequence[str]) -> list[Finding]:
    """Baslamis faz, onceki fazlar bitmeden (pending ya da running) gelemez; 'blocked' sonrakileri durdurmaz.
    running'den sonraki running coklu_running'dir, burada tekrarlanmaz."""
    findings: list[Finding] = []
    pending = running = None
    for name in order:
        state = states[name]
        culprit = pending or (running if state in ENDED else None)
        if state in STARTED and culprit:
            findings.append(Finding("faz_sirasi", f"phases.{name}", f"{state} ama önceki faz '{culprit}' "
                                                                    f"{states[culprit]}; sıra: {' → '.join(order)}"))
        pending = pending or (name if state == "pending" else None)
        running = running or (name if state == "running" else None)
    return findings


def current_phase_findings(manifest: dict, states: dict[str, str | None], order: Sequence[str]) -> list[Finding]:
    """Ust duzey 'phase' = son baslayan faz; o faz kapandiysa (done ya da blocked) sonraki faz da olur. Hic faz
    baslamadiysa ilk faz."""
    phase = manifest.get("phase")
    if phase not in order:  # sema bulgusu
        return []
    started = [name for name in order if states[name] in STARTED]
    if not started:
        allowed, context = [order[0]], "hiçbir faz başlamamış"
    else:
        last = started[-1]
        index = order.index(last)
        allowed = [last, *([order[index + 1]] if states[last] in ENDED and index + 1 < len(order) else [])]
        context = f"son başlayan faz '{last}' {states[last]}"
    if phase in allowed:
        return []
    return [Finding("faz_sirasi", "phase", f"'{phase}' fazların durumuna uymuyor ({context}); "
                                           f"beklenen: {' ya da '.join(allowed)}")]


def _when(value: Any) -> dt.datetime | None:
    """Manifest zamani; bicimi bozuk ya da bos deger None (bicim hatasi zaten sema bulgusu)."""
    try:
        return phase_usage.parse_ts(value) if is_datetime(value) else None
    except ValueError:
        return None


def manifest_time_findings(manifest: dict, order: Sequence[str], starts: dict[str, list[Mark]]) -> list[Finding]:
    """ended_at started_at'tan once olamaz; fazlar sema sirasiyla, oncekini bitirdikten sonra baslar. Manifest faz
    basina tek pencere tutar: phase_log'da sonraki faz basladiktan sonra yeniden acilan fazla o faz karsilastirilmaz."""
    phases = manifest["phases"]
    spans = []
    for name in order:
        raw = phases.get(name)
        start = _when(raw.get("started_at")) if isinstance(raw, dict) else None
        if start is not None:
            spans.append(Span(name, start, _when(raw.get("ended_at"))))
    findings = [Finding("zaman", f"phases.{span.name}.ended_at",
                        f"ended_at ({_ts(span.end)}) started_at'tan ({_ts(span.start)}) önce")
                for span in spans if span.end is not None and span.end < span.start]
    for prev, cur in zip(spans, spans[1:]):
        if reopened_after(starts, prev.name, cur.name):
            continue  # sira phase_log'daki ilk start'larla denetlendi (log_order_findings)
        where = f"phases.{cur.name}.started_at"
        hint = f"; '{prev.name}' yeniden açıldıysa phase_log'da start/end işareti olmalı"
        if cur.start < prev.start - ROUNDING_SLACK:
            findings.append(Finding("faz_sirasi", where, f"'{cur.name}' fazı '{prev.name}' fazından önce başlıyor "
                                                         f"({_ts(cur.start)} < {_ts(prev.start)}){hint}"))
        elif prev.end is not None and cur.start < prev.end - ROUNDING_SLACK:
            findings.append(Finding("faz_sirasi", where, f"'{cur.name}' fazı '{prev.name}' bitmeden başlıyor "
                                                         f"({_ts(cur.start)} < {_ts(prev.end)}){hint}"))
    return findings


# ---------- teslim ----------

def find_delivery_xlsx(pkg: Path, paths: Any) -> tuple[Path | None, Finding | None]:
    """paths.delivery_xlsx'in dosya adi paket kokunde; alan yoksa koktaki tek .xlsx (~$ kilit dosyasi haric)."""
    declared = paths.get("delivery_xlsx") if isinstance(paths, dict) else None
    if isinstance(declared, str) and declared.strip():
        name = declared.replace("\\", "/").rstrip("/").rsplit("/", 1)[-1]
        target = pkg / name
        if target.is_file():
            return target, None
        return None, Finding("teslim", "paths.delivery_xlsx", f"teslim Excel'i pakette yok: {name}")
    found = sorted(path for path in pkg.iterdir()
                   if path.is_file() and path.suffix.lower() == ".xlsx" and not path.name.startswith("~$"))
    if len(found) == 1:
        return found[0], None
    if not found:
        return None, Finding("teslim", "--pkg", "pakette Excel yok (kökte .xlsx)")
    return None, Finding("teslim", "--pkg", f"pakette birden çok Excel: {', '.join(p.name for p in found)}; "
                                            "paths.delivery_xlsx yazılmalı")


def delivery_findings(manifest: dict, states: dict[str, str | None] | None,
                      pkg: Path | None) -> tuple[list[Finding], dict[str, Any] | None]:
    """deliver done -> delivered.xlsx_sha256 var; --pkg verilirse gercek Excel'in SHA-256'si ayni."""
    delivered = manifest.get("delivered")
    if delivered is not None and not isinstance(delivered, dict):  # sema bulgusu
        return [], None if pkg is None else {"checked": False, "reason": "delivered nesne değil"}
    expected = delivered.get("xlsx_sha256") if isinstance(delivered, dict) else None
    has_sha = isinstance(expected, str) and bool(expected.strip())
    findings = []
    if not has_sha and states is not None and states.get(DELIVER_PHASE) == "done":
        findings.append(Finding("teslim", "delivered", "deliver done ama delivered.xlsx_sha256 yok"))
    if pkg is None:
        return findings, None
    if not has_sha:
        return findings, {"checked": False, "reason": "delivered.xlsx_sha256 yok"}
    xlsx, problem = find_delivery_xlsx(pkg, manifest.get("paths"))
    if problem is not None:
        return [*findings, problem], {"checked": False, "reason": problem.message}
    actual = common.sha256_file(xlsx)
    match = actual == expected.strip().lower()
    if not match:
        message = f"gerçek dosyayla aynı değil: {xlsx.name} {actual[:12]}… (manifest {expected.strip()[:12]}…)"
        findings.append(Finding("teslim", "delivered.xlsx_sha256", message))
    return findings, {"checked": True, "file": xlsx.name, "match": match, "sha256": actual}


# ---------- toplama ve CLI ----------

def collect(validator: Any, order: Sequence[str], manifest: Any, has_bom: bool, log: PhaseLog,
            pkg: Path | None) -> tuple[list[Finding], dict[str, Any] | None, dict[str, str | None] | None]:
    """Doner: (bulgular, xlsx ozeti, faz durumlari). Ayni bulgu bir kez, kontrol sirasiyla."""
    findings = schema_findings(validator, manifest)
    if has_bom:
        findings.append(Finding("dosya", FILE_WHERE,
                                "UTF-8 BOM var: render_summary manifest'i okuyamaz (Python ile BOM'suz yaz)"))
    windows, window_problems = pair_windows(log.marks)
    starts = start_marks(windows, order)
    findings += [*log.findings, *window_problems, *overlap_findings(windows), *log_order_findings(starts, order)]
    states = phase_states(manifest, order)
    if states is not None:
        findings += [*mark_findings(states, log.marks, windows), *running_findings(states),
                     *status_order_findings(states, order), *current_phase_findings(manifest, states, order),
                     *manifest_time_findings(manifest, order, starts)]
    if isinstance(manifest, dict):
        delivery, xlsx = delivery_findings(manifest, states, pkg)
    else:
        delivery, xlsx = [], None if pkg is None else {"checked": False, "reason": "manifest nesne değil"}
    return list(dict.fromkeys([*findings, *delivery])), xlsx, states


def _real(path: Path) -> str:
    return os.path.normcase(os.path.realpath(path))


def _inside(child: Path, parent: Path) -> bool:
    child_real, parent_real = _real(child), _real(parent)
    return child_real == parent_real or child_real.startswith(parent_real.rstrip(os.sep) + os.sep)


def check_out(out: Path, inputs: Sequence[Path], packages: Sequence[Path]) -> None:
    if any(_real(out) == _real(path) for path in inputs):
        raise UsageError(f"--out bir girdinin üstüne yazamaz: {out}")
    for root in packages:
        if _inside(out, root):
            raise UsageError(f"--out paket klasörüne yazamaz: {out} (paket: {root})")


def package_dirs(pkg: Path | None, manifest: Any, manifest_path: Path) -> list[Path]:
    """--out'un yazamayacagi klasorler: --pkg, paths.package_root (goreli ise calisma klasorune degil manifest
    klasorune gore; run_log gibi) ve SKILL duzenindeki PKG = WORK\\paket (manifest klasorundeki 'paket')."""
    base = manifest_path.parent
    paths = manifest.get("paths") if isinstance(manifest, dict) else None
    declared = paths.get("package_root") if isinstance(paths, dict) else None
    named = [base / declared] if isinstance(declared, str) and declared.strip() else []  # mutlak yol base'i ezer
    return [base / PACKAGE_DIR, *([pkg] if pkg else []), *named]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Manifest kontrolü: şema, phase_log işaretleri, faz sırası ve teslim SHA-256'sı (C4)")
    parser.add_argument("manifest", type=Path, help="WORK\\manifest.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA,
                        help="varsayılan: city-pack\\references\\manifest.schema.json")
    parser.add_argument("--phase-log", type=Path,
                        help="phase_usage mark logu (varsayılan: <manifest klasörü>\\_is\\phase_log.jsonl; "
                             "yoksa boş sayılır)")
    parser.add_argument("--pkg", dest="package_root", type=Path,
                        help="paket kökü: teslim Excel'inin SHA-256'sı delivered.xlsx_sha256 ile karşılaştırılır")
    parser.add_argument("--out", type=Path, help="tam rapor JSON (girdinin üstüne ve paket klasörüne yazılmaz)")
    return parser


def run(args: argparse.Namespace) -> int:
    manifest_path, schema_path = Path(args.manifest), Path(args.schema)
    log_path = Path(args.phase_log) if args.phase_log else manifest_path.parent / LOG_RELATIVE
    pkg = Path(args.package_root) if args.package_root else None
    if pkg is not None and not pkg.is_dir():
        raise UsageError(f"--pkg klasör değil: {pkg}")
    schema, _ = load_json(schema_path, "şema")
    validator, order = make_validator(schema), phase_order(schema)
    manifest, has_bom = load_json(manifest_path, "manifest")
    out = Path(args.out) if args.out else None
    if out is not None:
        check_out(out, [manifest_path, log_path, schema_path], package_dirs(pkg, manifest, manifest_path))
    log = read_phase_log(log_path, args.phase_log is not None, order)
    findings, xlsx, states = collect(validator, order, manifest, has_bom, log, pkg)
    report = {
        "tool": TOOL, "manifest": str(manifest_path), "schema": str(schema_path), "order": list(order),
        "phase": manifest.get("phase") if isinstance(manifest, dict) else None, "phases": states,
        "phase_log": {"path": str(log_path), "found": log.found, "marks": len(log.marks)}, "xlsx": xlsx,
        "findings": [finding.as_dict() for finding in findings],
        "by_code": dict(Counter(finding.code for finding in findings)), "out": None if out is None else str(out)}
    if out is not None:
        common.write_json(out, report)
    common.emit({**{k: v for k, v in report.items() if k not in ("schema", "order", "findings")},
                 "findings": len(findings), "items": report["findings"][:MAX_ITEMS]})
    return common.EXIT_FINDINGS if findings else common.EXIT_OK


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return common.EXIT_USAGE if stop.code else common.EXIT_OK
    try:
        return run(args)
    except (UsageError, OSError) as exc:  # yakalanmazsa cikis 1 olur, 'bulgu' ile karisir
        common.emit({"tool": TOOL, "error": str(exc)})
        return common.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
