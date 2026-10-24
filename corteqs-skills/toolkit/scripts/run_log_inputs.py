r"""run_log girdi okuyuculari: manifest, oturum kayitlari, phase_usage CSV'si, alt ajan kayitlari, validate_all ve
editorial_score ciktilari, iddia denetimi ve gorsel inceleme kayitlari. Kurallar ve CLI: run_log.py; dislanan
workflow'un token'larini faz loguyla toplayan ve raporu denetleyen A9 bolumu: run_log_exclude.py.

Hepsi salt okunur. Okunamayan, yabanci ya da elle degistirilmis girdi UsageError'dur (run_log cikis 2).
"""
from __future__ import annotations

import contextlib
import csv
import datetime as dt
import functools
import hashlib
import io
import json
import math
import os
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import editorial_score
import phase_usage

STATUS_TR = {"pending": "başlamadı", "running": "sürüyor", "done": "bitti", "blocked": "engelli"}
OPEN_STATUSES = ("running", "blocked")  # bitisi yazilmamis pencere yalniz bunlarda acik sayilir
GATE_WORDS = {0: "temiz", 1: "bulgu", 2: "hata"}
USAGE_COLUMNS = ("phase", "calls", "input_tokens", "cache_creation", "cache_read", "output_tokens", "total_input",
                 "uncached_input", "duration_s")  # phase_usage.COLUMNS'tan okunanlar
FINGERPRINT = ("calls", "input_tokens", "cache_creation", "cache_read", "output_tokens")  # ayni oturumun iki raporu
COUNT_LABELS = {"answers": "kart", "places": "mekan", "neighborhoods": "mahalle", "districts": "mahalle",
                "routes": "rota", "glossary": "sozluk", "topics": "konu", "photos": "foto", "hero_photos": "kapak",
                "covers": "kapak"}
DECISIONS = (editorial_score.DECISION_FIX, editorial_score.DECISION_EVIDENCE, editorial_score.DECISION_READY)
MODEL_FAMILIES = ("opus", "sonnet", "haiku", "fable")
UNKNOWN_MODEL = "?"
SYNTHETIC_MODEL = "<synthetic>"
AGENT_PREFIX, AGENT_SUFFIX = "agent-", ".jsonl"
WORKFLOW_PREFIX, DIRECT_AGENTS = "wf_", "(doğrudan)"  # subagents\workflows\wf_<id>\ ya da dogrudan ajan
AUDIT_GLOBS = ("*_iddia.jsonl",)
AUDIT_FIELD, AUDIT_OK = "sonuç", "doğru"  # agents\iddia-denetcisi.md CLAIM kaydi
REVIEW_GLOBS = ("review_*.jsonl", "verify_*.jsonl", "photo-review*.jsonl")
REVIEW_RESULTS = ("keep", "flag", "reject")  # agents\foto-inceleme.md
WINDOW_TOLERANCE_S = 60.0  # izinli fark: manifest suresi ile phase_log suresi; faz siniri ile oturum kapsami
MAX_SCAN_LINES = 500  # ajan kaydinda ilk zaman damgasi ve model en cok bu kadar satirda aranir


class UsageError(Exception):
    """Okunamayan/yabanci girdi, gecersiz arguman ya da yazilamayan cikti (cikis 2)."""


@dataclass(frozen=True)
class Gate:
    script: str
    code: int


@dataclass(frozen=True)
class Phase:
    name: str
    status: str | None  # None: manifest'te kaydi yok
    start: dt.datetime | None
    end: dt.datetime | None
    gates: tuple[Gate, ...] = ()

    @property
    def seconds(self) -> float | None:
        return (self.end - self.start).total_seconds() if self.start and self.end else None

    @property
    def has_window(self) -> bool:
        """Ajan ve oturum penceresi var mi: baslangic + bitis; bitissiz yalniz running/blocked fazda acik."""
        return self.start is not None and (self.end is not None or self.status in OPEN_STATUSES)


@dataclass(frozen=True)
class Usage:
    total_input: int = 0
    uncached_input: int = 0
    output: int = 0
    duration_s: float = 0.0  # faz penceresi (phase_log)

    def plus(self, other: "Usage") -> "Usage":
        """Token'lar toplanir; sure toplanmaz: her oturum raporu ayni phase_log penceresini tasir, en buyugu alinir."""
        return Usage(self.total_input + other.total_input, self.uncached_input + other.uncached_input,
                     self.output + other.output, max(self.duration_s, other.duration_s))

    def minus(self, other: "Usage") -> "Usage":
        """Dislanan workflow'un token'lari cikarilir; sure (faz penceresi) ayni kalir."""
        return Usage(self.total_input - other.total_input, self.uncached_input - other.uncached_input,
                     self.output - other.output, self.duration_s)

    @property
    def tokens(self) -> tuple[int, int, int]:
        return self.total_input, self.uncached_input, self.output


def usage_sum(items: Iterable[Usage], start: Usage = Usage()) -> Usage:
    return functools.reduce(Usage.plus, items, start)


@dataclass(frozen=True)
class UsageTable:
    phases: dict[str, Usage]
    outside: Usage
    total: Usage
    fingerprints: dict[str, tuple[int, ...]]  # calls>0 faz satirlari: ayni oturumun iki raporu tespiti


@dataclass(frozen=True)
class Session:
    path: Path
    first: dt.datetime
    last: dt.datetime

    def holds(self, moment: dt.datetime) -> bool:
        """Faz isaretini (mark start/end) yazan oturum o ani icerir; elle yuvarlanmis saate pay birakilir."""
        slack = dt.timedelta(seconds=WINDOW_TOLERANCE_S)
        return self.first - slack <= moment <= self.last + slack


@dataclass(frozen=True)
class Agent:
    agent_id: str
    start: dt.datetime | None
    model: str
    workflow: str = DIRECT_AGENTS


@dataclass(frozen=True)
class Quality:
    structure_errors: int
    media_errors: int
    minimum_gaps: str
    counts: dict[str, int] | None  # None: yalniz ozet verildi


@dataclass(frozen=True)
class Score:
    percent: int | None  # None: editorial_score OLCULEMEDI dedi
    decision: str


@dataclass(frozen=True)
class Audit:
    claims: int
    errors: int

    def cell(self) -> str | None:
        return f"{100 * self.errors / self.claims:.1f} ({self.errors}/{self.claims})" if self.claims else None


@dataclass(frozen=True)
class PhotoReview:
    reviewed: int = 0
    rejected: int = 0
    checked: int = 0  # ikinci goz
    second_rejected: int = 0

    def cell(self) -> str | None:
        parts = [f"{self.rejected}/{self.reviewed}"] if self.reviewed else []
        parts += [f"ikinci göz {self.second_rejected}/{self.checked}"] if self.checked else []
        return "; ".join(parts) or None


@dataclass(frozen=True)
class Manifest:
    city_id: str
    phases: dict[str, Phase]
    package_root: str | None
    usage_log: str | None = None  # paths.usage_log (phase_usage --log)


# ---------- okuma yardimcilari ----------

def real_path(path: Path) -> str:
    return os.path.normcase(os.path.realpath(path))


def read_bytes(path: Path, label: str) -> bytes:
    try:
        return Path(path).read_bytes()
    except FileNotFoundError as exc:
        raise UsageError(f"{label} yok: {path}") from exc
    except OSError as exc:
        raise UsageError(f"{label} okunamadı: {path} ({exc.strerror or exc})") from exc


def read_text(path: Path, label: str) -> str:
    try:
        return read_bytes(path, label).decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise UsageError(f"{label} UTF-8 değil: {path}") from exc


def load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(read_text(path, label))
    except json.JSONDecodeError as exc:
        raise UsageError(f"{label} JSON değil: {path} ({exc.msg}, satır {exc.lineno})") from exc


def read_jsonl(path: Path, label: str) -> list[tuple[str, dict[str, Any]]]:
    """(konum, kayit) listesi; bos satir atlanir, bozuk satir ya da nesne olmayan kayit hatadir."""
    records = []
    for number, line in enumerate(read_text(path, label).splitlines(), start=1):
        if not line.strip():
            continue
        where = f"{label} {Path(path).name} satır {number}"
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise UsageError(f"{where}: JSON değil ({exc.msg})") from exc
        if not isinstance(record, dict):
            raise UsageError(f"{where}: JSON nesnesi değil")
        records.append((where, record))
    return records


def expand_inputs(paths: Sequence[Path], patterns: Sequence[str], label: str) -> list[Path]:
    """Dosya aynen; klasor -> icinde desene uyan dosyalar (alt klasorsuz). Ayni dosya bir kez."""
    found: dict[str, Path] = {}
    for path in map(Path, paths):
        if path.is_dir():
            matches = sorted({match for pattern in patterns for match in path.glob(pattern) if match.is_file()})
            if not matches:
                raise UsageError(f"{label} klasöründe {' / '.join(patterns)} yok: {path}")
        elif path.is_file():
            matches = [path]
        else:
            raise UsageError(f"{label} yok: {path}")
        found = {**found, **{real_path(m): m for m in matches if real_path(m) not in found}}
    return list(found.values())


def _count(value: Any, where: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise UsageError(f"{where} negatif olmayan tam sayı olmalı ({value!r})")
    return value


# ---------- manifest ----------

def _timestamp(value: Any, where: str) -> dt.datetime | None:
    if value is None or value == "":
        return None
    try:
        return phase_usage.parse_ts(value)
    except ValueError as exc:
        raise UsageError(f"manifest {where} geçersiz zaman: {value!r}") from exc


def _gates(raw: Any, name: str) -> tuple[Gate, ...]:
    if raw is None:
        return ()
    if not isinstance(raw, list):
        raise UsageError(f"manifest phases.{name}.gates liste olmalı")
    gates = []
    for index, gate in enumerate(raw):
        code = gate.get("exit_code") if isinstance(gate, dict) else None
        if isinstance(code, bool) or not isinstance(code, int) or code not in GATE_WORDS:
            raise UsageError(f"manifest phases.{name}.gates[{index}].exit_code 0, 1 ya da 2 olmalı ({code!r})")
        script = gate.get("script")
        gates.append(Gate(script.strip() if isinstance(script, str) and script.strip() else f"kapı-{index + 1}", code))
    return tuple(gates)


def parse_phase(name: str, raw: Any) -> Phase:
    if not isinstance(raw, dict):
        raise UsageError(f"manifest phases.{name} nesne olmalı")
    status = raw.get("status")
    if not isinstance(status, str) or status not in STATUS_TR:
        raise UsageError(f"manifest phases.{name}.status geçersiz ({status!r}; izinli: {', '.join(STATUS_TR)})")
    start = _timestamp(raw.get("started_at"), f"phases.{name}.started_at")
    end = _timestamp(raw.get("ended_at"), f"phases.{name}.ended_at")
    if start and end and end < start:
        raise UsageError(f"manifest phases.{name}: ended_at started_at'tan önce")
    return Phase(name, status, start, end, _gates(raw.get("gates"), name))


def parse_manifest(data: Any) -> Manifest:
    if not isinstance(data, dict):
        raise UsageError("manifest kökü JSON nesnesi olmalı")
    city = data.get("city")
    city_id = city.get("city_id") if isinstance(city, dict) else None
    if not isinstance(city_id, str) or not city_id.strip():
        raise UsageError("manifest city.city_id yok")
    phases = data.get("phases")
    if not isinstance(phases, dict):
        raise UsageError("manifest phases nesne olmalı")
    paths = data.get("paths") if isinstance(data.get("paths"), dict) else {}
    root, log = (value if isinstance(value, str) and value.strip() else None
                 for value in (paths.get("package_root"), paths.get("usage_log")))
    return Manifest(city_id.strip(), {str(name): parse_phase(str(name), raw) for name, raw in phases.items()},
                    root, log)


# ---------- oturum kayitlari ----------

def read_session(path: Path) -> Session:
    """Oturumun kapsami: kayittaki ilk ve son gecerli zaman damgasi (satir sirasi zaman sirasi olmayabilir)."""
    stamps = []
    try:
        with Path(path).open(encoding="utf-8", errors="replace") as stream:
            for raw in stream:
                with contextlib.suppress(ValueError, AttributeError):  # bozuk satir / zaman damgasiz kayit
                    stamps.append(phase_usage.parse_ts(json.loads(raw).get("timestamp")))
    except FileNotFoundError as exc:
        raise UsageError(f"--session yok: {path}") from exc
    except OSError as exc:
        raise UsageError(f"--session okunamadı: {path} ({exc.strerror or exc})") from exc
    if not stamps:
        raise UsageError(f"--session kaydında zaman damgası yok (Claude Code oturum kaydı değil): {path}")
    return Session(Path(path), min(stamps), max(stamps))


def read_sessions(paths: Sequence[Path]) -> list[Session] | None:
    if not paths:
        return None
    reals = [real_path(path) for path in paths]
    twice = [path for path, real in zip(paths, reals) if reals.count(real) > 1]
    if twice:
        raise UsageError(f"aynı --session iki kez verildi: {twice[0]}")
    return [read_session(Path(path)) for path in paths]


def session_agent_dirs(sessions: Sequence[Session] | None) -> list[Path]:
    """<oturum-id>.jsonl'in alt ajanlari <oturum-id>\\subagents altinda (phase_usage kurali); klasor yoksa ajan yok."""
    return [d for d in (s.path.with_suffix("") / "subagents" for s in sessions or ()) if d.is_dir()]


# ---------- phase_usage CSV ----------

def _int_cell(row: dict[str, Any], column: str, where: str) -> int:
    value = (row.get(column) or "").strip()
    try:
        number = int(value)
    except ValueError as exc:
        raise UsageError(f"{where}: {column} tam sayı değil ({value!r})") from exc
    return _count(number, f"{where}: {column}")


def _usage_from(row: dict[str, Any], where: str) -> Usage:
    raw = (row.get("duration_s") or "").strip()
    try:
        duration = float(raw) if raw else 0.0
    except ValueError as exc:
        raise UsageError(f"{where}: duration_s sayı değil ({raw!r})") from exc
    if not math.isfinite(duration) or duration < 0:
        raise UsageError(f"{where}: duration_s geçersiz ({raw!r})")
    return Usage(_int_cell(row, "total_input", where), _int_cell(row, "uncached_input", where),
                 _int_cell(row, "output_tokens", where), duration)


def parse_usage(name: str, text: str) -> UsageTable:
    """Tek phase_usage raporu: faz satirlari, '(outside phases)' ve TOTAL (varsa faz toplamiyla tutmali)."""
    reader = csv.DictReader(io.StringIO(text))
    missing = [column for column in USAGE_COLUMNS if column not in (reader.fieldnames or [])]
    if missing:
        raise UsageError(f"{name}: phase_usage report CSV'si değil (eksik sütun: {', '.join(missing)})")
    phases: dict[str, Usage] = {}
    special: dict[str, Usage] = {}
    fingerprints: dict[str, tuple[int, ...]] = {}
    for number, row in enumerate(reader, start=2):
        where = f"{name} satır {number}"
        phase = (row.get("phase") or "").strip()
        if not phase:
            raise UsageError(f"{where}: faz adı boş")
        bucket = special if phase in (phase_usage.OUTSIDE, phase_usage.TOTAL) else phases
        if phase in bucket:
            raise UsageError(f"{where}: '{phase}' satırı yineleniyor")
        bucket[phase] = _usage_from(row, where)
        mark = tuple(_int_cell(row, column, where) for column in FINGERPRINT)
        if bucket is phases and mark[0] > 0:
            fingerprints[phase] = mark
    outside = special.get(phase_usage.OUTSIDE, Usage())
    computed = usage_sum(phases.values(), outside)
    total = special.get(phase_usage.TOTAL)
    if total is not None and total.tokens != computed.tokens:
        raise UsageError(f"{name}: TOTAL satırı faz satırlarının toplamıyla tutmuyor (elle değiştirilmiş olabilir)")
    return UsageTable(phases, outside, computed if total is None else total, fingerprints)


def read_usage(paths: Sequence[Path]) -> UsageTable | None:
    """Oturum basina raporlar faz bazinda toplanir. Ayni rapor ya da ayni oturumun iki raporu cift sayimdir: red."""
    if not paths:
        return None
    seen: dict[str, Path] = {}
    tables: list[tuple[Path, UsageTable]] = []
    for path in map(Path, paths):
        text = read_text(path, "--usage")
        digest = hashlib.sha256("\n".join(text.splitlines()).strip().encode("utf-8")).hexdigest()  # BOM/satir sonu
        if digest in seen:
            raise UsageError(f"aynı phase_usage raporu iki kez verildi: {seen[digest]} ve {path}")
        seen = {**seen, digest: path}
        table = parse_usage(path.name, text)
        for other_path, other in tables:
            same = [phase for phase, mark in table.fingerprints.items() if other.fingerprints.get(phase) == mark]
            if same:
                raise UsageError(f"aynı oturumun iki raporu (ara ve son rapor?): {other_path} ve {path}; '{same[0]}' "
                                 "satırı birebir aynı. Oturum başına yalnız son raporu ver.")
        tables = [*tables, (path, table)]
    merged: dict[str, Usage] = {}
    for _, table in tables:
        merged = {**merged, **{name: merged[name].plus(usage) if name in merged else usage
                               for name, usage in table.phases.items()}}
    return UsageTable(merged, usage_sum(t.outside for _, t in tables), usage_sum(t.total for _, t in tables), {})


# ---------- alt ajan kayitlari ----------

def model_family(name: str) -> str:
    lowered = name.strip().lower()
    return next((family for family in MODEL_FAMILIES if family in lowered), lowered or UNKNOWN_MODEL)


def _record_model(record: dict[str, Any]) -> str | None:
    message = record.get("message")
    if record.get("type") != "assistant" or not isinstance(message, dict):
        return None
    model = message.get("model")
    usable = isinstance(model, str) and model.strip() and model != SYNTHETIC_MODEL
    return model_family(model) if usable else None


def _meta_model(transcript: Path) -> str | None:
    meta = transcript.with_name(transcript.name[: -len(AGENT_SUFFIX)] + ".meta.json")
    try:
        data = json.loads(meta.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):  # meta yok/bozuk: model bilinmiyor sayilir
        return None
    model = data.get("model") if isinstance(data, dict) else None
    return model_family(model) if isinstance(model, str) and model.strip() else None


def read_agent(path: Path, workflow: str = DIRECT_AGENTS) -> Agent:
    """Ilk gecerli zaman damgasi (ajanin basladigi an) ve ilk gercek asistan modeli; yalniz ust satirlar okunur."""
    start: dt.datetime | None = None
    model: str | None = None
    with path.open(encoding="utf-8", errors="replace") as stream:
        for number, raw in enumerate(stream):
            if number >= MAX_SCAN_LINES or (start is not None and model is not None):
                break
            try:
                record = json.loads(raw)
            except ValueError:  # bos/bozuk satir: sonrakine bak
                continue
            if not isinstance(record, dict):
                continue
            if start is None:
                with contextlib.suppress(ValueError):  # bu satirda zaman damgasi yok
                    start = phase_usage.parse_ts(record.get("timestamp"))
            model = model or _record_model(record)
    agent_id = path.name[len(AGENT_PREFIX): -len(AGENT_SUFFIX)]
    return Agent(agent_id, start, model or _meta_model(path) or UNKNOWN_MODEL, workflow)


def _workflow_of(path: Path, root: Path) -> str:
    """subagents\\workflows\\wf_<id>\\agent-*.jsonl -> 'wf_<id>'; dogrudan baslatilan ajan -> DIRECT_AGENTS."""
    parts = (root.name, *path.relative_to(root).parts[:-1])
    return next((part for part in reversed(parts) if part.startswith(WORKFLOW_PREFIX)), DIRECT_AGENTS)


def workflow_ids(values: Sequence[str]) -> tuple[str, ...]:
    ids = tuple(Path(value.strip()).name for value in values)  # klasor yolu verilirse adi
    bad = [value for value in ids if not value.startswith(WORKFLOW_PREFIX)]
    if bad:
        raise UsageError(f"--exclude-workflow '{bad[0]}' workflow kimliği değil (beklenen: {WORKFLOW_PREFIX}<id>)")
    return ids


def scan_agents(directories: Sequence[Path],
                exclude: Sequence[str]) -> tuple[list[Agent], dict[str, tuple[Path, ...]]]:
    """Klasorlerdeki (alt klasorler dahil) agent-*.jsonl kayitlari; ayni ajan kimligi bir kez; dislanan workflow
    ajanlari sayilmaz, workflow basina kayit yollari doner (token'lari icin). Bulunamayan --exclude-workflow hatadir
    (yazim yanlisi)."""
    seen: set[str] = set()
    agents: list[Agent] = []
    excluded: dict[str, tuple[Path, ...]] = {}
    for root in map(Path, directories):
        if not root.is_dir():
            raise UsageError(f"--subagents klasörü yok: {root}")
        for path in sorted(root.rglob(f"{AGENT_PREFIX}*{AGENT_SUFFIX}")):
            agent_id = path.name[len(AGENT_PREFIX): -len(AGENT_SUFFIX)]
            if agent_id in seen or not path.is_file():
                continue
            seen.add(agent_id)
            workflow = _workflow_of(path, root)
            if workflow in exclude:
                excluded = {**excluded, workflow: (*excluded.get(workflow, ()), path)}
            else:
                agents.append(read_agent(path, workflow))
    unknown = sorted(set(exclude) - set(excluded))
    if unknown:
        raise UsageError(f"--exclude-workflow alt ajan klasörlerinde yok: {', '.join(unknown)}")
    return agents, excluded


# ---------- kalite girdileri ----------

def _error_count(value: Any, where: str) -> int:
    return len(value) if isinstance(value, list) else _count(value, f"--validation {where}")


def format_minimum_gaps(gaps: Any) -> str:
    if not isinstance(gaps, dict):
        raise UsageError("--validation minimum_gaps nesne olmalı")
    parts = []
    for key, value in gaps.items():
        if not isinstance(value, dict):
            raise UsageError(f"--validation minimum_gaps.{key} nesne olmalı")
        actual = _count(value.get("actual"), f"--validation minimum_gaps.{key}.actual")
        minimum = _count(value.get("minimum"), f"--validation minimum_gaps.{key}.minimum")
        parts.append(f"{COUNT_LABELS.get(key, key)} {actual}/{minimum}")
    return "; ".join(parts) or "yok"


def read_validation(data: Any) -> Quality:
    """validate_all --out raporu ya da onun tek satir ozeti (summary)."""
    if not isinstance(data, dict):
        raise UsageError("--validation kökü JSON nesnesi olmalı")
    summary = data["summary"] if isinstance(data.get("summary"), dict) else data
    if summary.get("tool") != "validate_all":
        raise UsageError("--validation validate_all çıktısı değil (tool alanı)")
    if "error" in summary:
        raise UsageError(f"--validation: doğrulayıcı çalışmamış ({summary['error']})")
    if "minimum_gaps" not in summary:
        raise UsageError("--validation minimum_gaps yok")
    structure = summary.get("structure") if isinstance(summary.get("structure"), dict) else {}
    media = summary.get("media") if isinstance(summary.get("media"), dict) else {}
    full = data.get("structure") if summary is not data and isinstance(data.get("structure"), dict) else {}
    counts = full.get("counts")
    if counts is not None and not isinstance(counts, dict):
        raise UsageError("--validation structure.counts nesne olmalı")
    return Quality(_error_count(structure.get("errors"), "structure.errors"),
                   _error_count(media.get("errors"), "media.errors"), format_minimum_gaps(summary["minimum_gaps"]),
                   None if counts is None else {k: _count(v, f"--validation structure.counts.{k}")
                                                for k, v in counts.items()})


def read_score(data: Any) -> Score:
    if not isinstance(data, dict) or data.get("tool") != editorial_score.TOOL:
        raise UsageError("--score editorial_score çıktısı değil (tool alanı)")
    decision = data.get("decision")
    if decision not in DECISIONS:
        raise UsageError(f"--score karar bilinmiyor ({decision!r}); karar yalnız editorial_score'dan gelir")
    percent = data.get("editorial_percent")
    if percent is not None and (isinstance(percent, bool) or not isinstance(percent, int) or not 0 <= percent <= 100):
        raise UsageError(f"--score editorial_percent 0..100 tam sayı olmalı ({percent!r})")
    return Score(percent, decision)


def read_claim_audit(files: Sequence[Path]) -> Audit:
    """CLAIM kayitlari: 'sonuç' zorunlu (dogrulayicinin 'sonuc'u baska kayittir); 'doğru' disindaki her sonuc hata."""
    claims = errors = 0
    for path in files:
        for where, record in read_jsonl(path, "--claim-audit"):
            result = record.get(AUDIT_FIELD)
            if not isinstance(result, str) or not result.strip():
                raise UsageError(f"{where}: '{AUDIT_FIELD}' alanı yok; iddia denetimi (CLAIM) kaydı değil")
            claims += 1
            errors += unicodedata.normalize("NFC", result).strip().casefold() != AUDIT_OK
    return Audit(claims, errors)


def read_photo_review(files: Sequence[Path]) -> PhotoReview:
    """Gorsel inceleme kararlari: result (keep/flag/reject) ya da ikinci goz ok (true/false)."""
    counts: Counter[str] = Counter()
    for path in files:
        for where, record in read_jsonl(path, "--photo-review"):
            if record.get("result") in REVIEW_RESULTS:
                counts.update(reviewed=1, rejected=int(record["result"] == "reject"))
            elif isinstance(record.get("ok"), bool):
                counts.update(checked=1, second_rejected=int(not record["ok"]))
            else:
                raise UsageError(f"{where}: result ({'/'.join(REVIEW_RESULTS)}) ya da ok (true/false) yok; "
                                 "görsel inceleme kaydı değil")
    return PhotoReview(**counts)
