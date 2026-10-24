"""Faz bazli token/sure olcumu: Claude Code transcript'lerinden faz tablosu uretir.

Kullanim:
  phase_usage.py mark <faz> start|end --log phases.jsonl [--ts ISO]
  phase_usage.py report --session s.jsonl [--subagents dir] --log phases.jsonl [--out x.csv] [--table]

Kural: transcript'ler yalniz okunur; ayni message.id birden cok satirda gecebilir (akis bloklari),
bir kez sayilir. Pencere [start, end): baslangic dahil, bitis haric.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import datetime as dt
import json
import sys
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Iterable

import common

OUTSIDE = "(outside phases)"
TOTAL = "TOTAL"
EVENTS = ("start", "end")
COLUMNS = (
    "phase", "calls", "input_tokens", "cache_creation", "cache_read", "output_tokens",
    "thinking_tokens", "total_input", "uncached_input", "duration_s",
)
_UTC = dt.timezone.utc
_FAR_FUTURE = dt.datetime.max.replace(tzinfo=_UTC)


class UsageError(Exception):
    """Kullanici/girdi hatasi: stderr'e yazilir, cikis kodu 2."""


@dataclass(frozen=True)
class Window:
    phase: str
    start: dt.datetime
    end: dt.datetime | None  # None: hala acik


@dataclass(frozen=True)
class Rec:
    ts: dt.datetime | None
    input: int
    cache_creation: int
    cache_read: int
    output: int
    thinking: int


@dataclass(frozen=True)
class Row:
    phase: str
    calls: int = 0
    input: int = 0
    cache_creation: int = 0
    cache_read: int = 0
    output: int = 0
    thinking: int = 0
    duration: float = 0.0

    @property
    def total_input(self) -> int:
        return self.input + self.cache_creation + self.cache_read

    @property
    def uncached_input(self) -> int:
        return self.input + self.cache_creation

    def add(self, rec: Rec) -> "Row":
        return replace(
            self, calls=self.calls + 1, input=self.input + rec.input,
            cache_creation=self.cache_creation + rec.cache_creation,
            cache_read=self.cache_read + rec.cache_read,
            output=self.output + rec.output, thinking=self.thinking + rec.thinking)

    def csv_values(self) -> list[Any]:
        return [self.phase, self.calls, self.input, self.cache_creation, self.cache_read, self.output,
                self.thinking, self.total_input, self.uncached_input, _fmt_seconds(self.duration)]


# ---------- zaman ----------

def parse_ts(value: Any) -> dt.datetime:
    """ISO-8601 -> UTC farkindalikli datetime ('Z' ve ofset desteklenir; saatsiz = UTC)."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"gecersiz zaman damgasi: {value!r}")
    parsed = dt.datetime.fromisoformat(value.strip())
    return (parsed.replace(tzinfo=_UTC) if parsed.tzinfo is None else parsed).astimezone(_UTC)


def format_ts(ts: dt.datetime) -> str:
    return ts.astimezone(_UTC).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _fmt_seconds(seconds: float) -> str:
    return f"{seconds:.3f}".rstrip("0").rstrip(".")


# ---------- faz logu ----------

def read_log(path: Path) -> list[dict[str, Any]]:
    """Faz logunu dogrulayarak okur. Dosya yoksa bos liste."""
    path = Path(path)
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
            entry = {"phase": str(obj["phase"]), "event": obj["event"], "ts": parse_ts(obj["ts"])}
        except (ValueError, KeyError, TypeError) as exc:
            raise UsageError(f"{path.name} satir {number}: gecersiz kayit ({exc})") from exc
        if entry["event"] not in EVENTS:
            raise UsageError(f"{path.name} satir {number}: gecersiz event '{entry['event']}'")
        entries.append(entry)
    return entries


def build_windows(entries: Iterable[dict[str, Any]]) -> list[Window]:
    """Log kayitlarindan pencereler kurar; esleşmeyen end / yeniden acma hata."""
    open_starts: dict[str, dt.datetime] = {}
    closed: list[Window] = []
    for entry in entries:
        phase, ts = entry["phase"], entry["ts"]
        if entry["event"] == "start":
            if phase in open_starts:
                raise UsageError(f"faz '{phase}' zaten open (start {format_ts(open_starts[phase])})")
            open_starts[phase] = ts
            continue
        if phase not in open_starts:
            raise UsageError(f"faz '{phase}' icin eslesen open start yok")
        if ts < open_starts[phase]:
            raise UsageError(f"faz '{phase}': end ({format_ts(ts)}) start'tan once")
        closed.append(Window(phase, open_starts.pop(phase), ts))
    still_open = [Window(phase, start, None) for phase, start in open_starts.items()]
    return sorted([*closed, *still_open], key=lambda w: w.start)


def check_overlaps(windows: list[Window]) -> None:
    for prev, nxt in zip(windows, windows[1:]):
        if prev.end is None or nxt.start < prev.end:
            raise UsageError(
                f"overlap: '{prev.phase}' ve '{nxt.phase}' pencereleri cakisiyor "
                f"({format_ts(nxt.start)} oncesinde '{prev.phase}' bitmemis)")


def cmd_mark(args: argparse.Namespace) -> int:
    phase = args.phase.strip()
    if not phase:
        raise UsageError("faz adi bos")
    try:
        ts = parse_ts(args.ts) if args.ts else dt.datetime.now(_UTC)
    except ValueError as exc:
        raise UsageError(f"--ts gecersiz: {exc}") from exc
    entries = read_log(Path(args.log))
    build_windows([*entries, {"phase": phase, "event": args.event, "ts": ts}])  # dogrulama
    line = {"phase": phase, "event": args.event, "ts": format_ts(ts)}
    path = Path(args.log)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(line, ensure_ascii=False, separators=(",", ":")) + "\n")
    common.emit(line)
    return common.EXIT_OK


# ---------- transcript okuma ----------

def _num(value: Any) -> int:
    return int(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else 0


def _dedupe_key(obj: dict[str, Any], message: dict[str, Any]) -> tuple[Any, ...]:
    if message.get("id"):
        return ("id", message["id"])
    if obj.get("requestId"):
        return ("req", obj["requestId"])
    return ("ts", obj.get("timestamp"), json.dumps(message["usage"], sort_keys=True))


def _to_rec(obj: dict[str, Any], usage: dict[str, Any]) -> Rec:
    try:
        ts = parse_ts(obj.get("timestamp"))
    except ValueError:
        ts = None
    details = usage.get("output_tokens_details")
    return Rec(
        ts=ts, input=_num(usage.get("input_tokens")),
        cache_creation=_num(usage.get("cache_creation_input_tokens")),
        cache_read=_num(usage.get("cache_read_input_tokens")),
        output=_num(usage.get("output_tokens")),
        thinking=_num(details.get("thinking_tokens")) if isinstance(details, dict) else 0)


def _merge_dup(old: Rec, new: Rec) -> Rec:
    """Akis tekrari: ilk zaman damgasi, en buyuk (son) output'lu kullanim."""
    stamps = [t for t in (old.ts, new.ts) if t is not None]
    best = new if new.output > old.output else old
    return replace(best, ts=min(stamps) if stamps else None)


def load_records(paths: Iterable[Path]) -> tuple[list[Rec], dict[str, int]]:
    """Dosyalari bellege okur; message.id (yoksa requestId, yoksa (ts,usage)) ile tekillestirir."""
    unique: dict[tuple[Any, ...], Rec] = {}
    stats = {"malformed": 0, "raw_usage_lines": 0, "duplicates": 0}
    for path in paths:
        for raw in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw)
            except ValueError:
                stats["malformed"] += 1
                continue
            message = obj.get("message") if isinstance(obj, dict) else None
            if not isinstance(obj, dict):
                stats["malformed"] += 1
                continue
            if obj.get("type") != "assistant" or not isinstance(message, dict):
                continue
            if not isinstance(message.get("usage"), dict):
                continue
            stats["raw_usage_lines"] += 1
            key, rec = _dedupe_key(obj, message), _to_rec(obj, message["usage"])
            if key in unique:
                stats["duplicates"] += 1
                rec = _merge_dup(unique[key], rec)
            unique[key] = rec
    return list(unique.values()), stats


def find_transcripts(session: Path, subagents: str | None) -> list[Path]:
    if not session.is_file():
        raise UsageError(f"session dosyasi yok: {session}")
    directory = Path(subagents) if subagents else session.with_suffix("") / "subagents"
    if subagents and not directory.is_dir():
        print(f"uyari: subagents klasoru yok, atlandi: {directory}", file=sys.stderr)
    # rglob: workflow ajanlari subagents/workflows/wf_*/agent-*.jsonl altinda (duz glob onlari atliyordu)
    found = sorted(directory.rglob("agent-*.jsonl")) if directory.is_dir() else []
    return [session, *found]


# ---------- aggregation ----------

def attribute(records: list[Rec], windows: list[Window]) -> tuple[list[Row], Row]:
    """Kayitlari pencerelere dagitir. Doner: (faz satirlari, disarisi satiri)."""
    starts = [w.start for w in windows]
    stamps = [r.ts for r in records if r.ts is not None]
    horizon = max(stamps) if stamps else None
    rows: dict[str, Row] = {}
    for w in windows:
        end = w.end if w.end is not None else max(horizon or w.start, w.start)
        base = rows.get(w.phase, Row(w.phase))
        rows[w.phase] = replace(base, duration=base.duration + (end - w.start).total_seconds())
    outside = Row(OUTSIDE)
    for rec in records:
        idx = bisect.bisect_right(starts, rec.ts) - 1 if rec.ts is not None else -1
        if idx >= 0 and rec.ts < (windows[idx].end or _FAR_FUTURE):
            name = windows[idx].phase
            rows[name] = rows[name].add(rec)
        else:
            outside = outside.add(rec)
    return list(rows.values()), outside


def total_row(rows: Iterable[Row]) -> Row:
    rows = list(rows)
    return Row(
        TOTAL, calls=sum(r.calls for r in rows), input=sum(r.input for r in rows),
        cache_creation=sum(r.cache_creation for r in rows), cache_read=sum(r.cache_read for r in rows),
        output=sum(r.output for r in rows), thinking=sum(r.thinking for r in rows),
        duration=sum(r.duration for r in rows))


def write_csv(path: Path, rows: Iterable[Row]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(COLUMNS)
        writer.writerows(row.csv_values() for row in rows)


def render_table(rows: Iterable[Row]) -> str:
    body = [[str(v) for v in row.csv_values()] for row in rows]
    table = [list(COLUMNS), *body]
    widths = [max(len(r[i]) for r in table) for i in range(len(COLUMNS))]
    return "\n".join(
        "  ".join(cell.ljust(widths[0]) if i == 0 else cell.rjust(widths[i]) for i, cell in enumerate(r))
        for r in table)


def cmd_report(args: argparse.Namespace) -> int:
    log_path = Path(args.log)
    if not log_path.is_file():
        raise UsageError(f"faz logu yok: {log_path}")
    windows = build_windows(read_log(log_path))
    check_overlaps(windows)
    records, stats = load_records(find_transcripts(Path(args.session), args.subagents))
    phase_rows, outside = attribute(records, windows)
    rows = [*phase_rows, outside]
    total = total_row(rows)
    all_rows = [*rows, total]
    if args.out:
        write_csv(Path(args.out), all_rows)
    if args.table:
        print(render_table(all_rows))
    pct = round(100 * outside.total_input / total.total_input, 2) if total.total_input else 0
    common.emit({
        "phases": len(phase_rows), "total_input": total.total_input, "uncached_input": total.uncached_input,
        "output": total.output, "unattributed_pct": pct, "calls": total.calls,
        "duplicates": stats["duplicates"], "malformed": stats["malformed"],
        "open_phases": sum(1 for w in windows if w.end is None)})
    return common.EXIT_OK


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Faz bazli token/sure olcumu")
    sub = parser.add_subparsers(dest="command", required=True)
    mark = sub.add_parser("mark", help="faz sinirini logla")
    mark.add_argument("phase")
    mark.add_argument("event", choices=EVENTS)
    mark.add_argument("--log", required=True)
    mark.add_argument("--ts", help="ISO-8601 (varsayilan: simdi, UTC)")
    report = sub.add_parser("report", help="transcript kullanimini fazlara dagit")
    report.add_argument("--session", required=True)
    report.add_argument("--subagents", help="varsayilan: <session-adi>/subagents (varsa)")
    report.add_argument("--log", required=True)
    report.add_argument("--out", help="CSV cikti yolu")
    report.add_argument("--table", action="store_true", help="kompakt tablo da yazdir")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return cmd_mark(args) if args.command == "mark" else cmd_report(args)
    except UsageError as exc:
        print(f"hata: {exc}", file=sys.stderr)
        return common.EXIT_USAGE


if __name__ == "__main__":
    common.setup_utf8()
    sys.exit(main())
