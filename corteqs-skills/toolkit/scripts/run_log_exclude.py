r"""run_log A9: ilgisiz workflow'un (subagents\workflows\wf_<id>\) token'larini --usage raporundan dusmek.

Ayni anda calisan iki workflow faz penceresiyle (zamanla) ayrilamaz; klasoruyle ayrilir. Dislanan workflow'un
agent-*.jsonl kullanimi phase_usage report'unun kodu ve kurallariyla (message.id bir kez, faz logu pencereleri)
dogrudan toplanir; run_log onu faz, '(faz dışı)' ve ozet satirlarindan cikarir. Bu ancak rapor o kayitlarin hepsini
iceriyorsa dogrudur ve rapor bunu kendisi gostermez (yalniz toplamlar tasir). Bu yuzden dusmeden once denetlenir;
tutmazsa UsageError (run_log cikis 2), yanlis sayi yazilmaz:
  1. --session verilmeli: rapor ancak oturum kaydindan yeniden hesaplanarak denetlenir.
  2. Faz logu raporu ureten log olmali: ayni fazlar, ayni kapali pencere sureleri.
  3. Workflow'un kayitlari bir --session'in alt ajan klasorunde olmali (<oturum-id>\subagents: phase_usage
     report'unun okudugu yer; baska --subagents klasorundeki workflow o raporda yoktur).
  4. O oturumun tek bir raporu, phase_usage'in o oturumun rapor anina (raporun dosya saati) kadarki kayitlarindan
     ayni pencerelerle yeniden hesapladigiyla faz faz ayni token'i tasimali. Tutmayan: workflow'suz rapor (A9 oncesi
     phase_usage, baska --subagents), baska oturumun ya da elle yazilmis rapor, bir ajan yazarken uretilmis ara rapor.
  5. Workflow rapor anindan sonra kayit yazmamis olmali (rapor workflow bitmeden ya da baslamadan uretilmis).
Cozum hep ayni: workflow ve fazlar bitince phase_usage report'u yeniden uret ve onu ver. Ayrilamayan: ana dongunun
(oturum kaydi) o workflow icin harcadigi token (kayit workflow'a gore bolunmez) ve workflow'suz (dogrudan) ajanlar.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import phase_usage
from run_log_inputs import Session, Usage, UsageError, UsageTable, parse_usage, read_text, real_path, usage_sum

LOG_TOLERANCE_S = 0.01  # faz logu (ms) ile rapordaki duration_s (3 ondalik) ayni pencere sayilir
REMEDY = "workflow ve fazlar bitince phase_usage report'u yeniden üret ve onu ver"
Tokens = dict[str, tuple[int, int, int]]  # faz ve '(outside phases)' -> total_input, uncached_input, output
_UTC = dt.timezone.utc


@dataclass(frozen=True)
class Report:
    path: Path
    tokens: Tokens
    moment: dt.datetime  # dosya saati: rapor bu anda var olan kayitlardan uretildi


def read_phase_log(path: Path) -> list[phase_usage.Window]:
    """phase_usage --log: pencereler phase_usage report'undaki kodla kurulur, token raporla ayni faza duser."""
    if not path.is_file():
        raise UsageError(f"faz logu yok: {path} (dışlanan token'lar için --phase-log ile phase_usage --log "
                         "dosyasını ver)")
    try:
        windows = phase_usage.build_windows(phase_usage.read_log(path))
        phase_usage.check_overlaps(windows)
    except phase_usage.UsageError as exc:
        raise UsageError(f"faz logu {path.name}: {exc}") from exc
    return windows


def check_phase_log(usage: UsageTable, windows: Sequence[phase_usage.Window]) -> None:
    """Faz logu --usage raporlarini ureten log olmali: ayni fazlar, ayni kapali pencere sureleri. Yoksa dislanan
    token, raporun koydugu fazdan baska fazdan dusulur."""
    names = {w.phase for w in windows}
    closed = names - {w.phase for w in windows if w.end is None}  # acik pencerenin suresi rapor anina bagli
    seconds = {name: sum((w.end - w.start).total_seconds() for w in windows if w.phase == name) for name in closed}
    odd = sorted(set(usage.phases) ^ names) or sorted(
        name for name in closed if abs(usage.phases[name].duration_s - seconds[name]) > LOG_TOLERANCE_S)
    if odd:
        raise UsageError(f"faz logu --usage raporlarının faz loguyla tutmuyor ('{odd[0]}' penceresi farklı): rapor "
                         f"faz bitmeden üretilmiş olabilir ({REMEDY}) ya da raporu başka faz logu üretti (onu "
                         "--phase-log ile ver)")


def _row_usage(row: phase_usage.Row) -> Usage:
    return Usage(row.total_input, row.uncached_input, row.output)


def _attributed(records: Iterable[phase_usage.Rec],
                windows: Sequence[phase_usage.Window]) -> tuple[dict[str, Usage], Usage]:
    """phase_usage report'unun dagitimi: kayit [baslangic, bitis) penceresine, dusmezse faz disina."""
    rows, outside = phase_usage.attribute(list(records), list(windows))
    return {row.phase: _row_usage(row) for row in rows}, _row_usage(outside)


def _tokens(phases: dict[str, Usage], outside: Usage) -> Tokens:
    return {**{name: usage.tokens for name, usage in phases.items()}, phase_usage.OUTSIDE: outside.tokens}


def workflow_usage(records: Sequence[phase_usage.Rec], windows: Sequence[phase_usage.Window]) -> UsageTable:
    """Workflow'un (message.id bir kez sayilmis) kayitlari faz logu pencerelerine dagitilir."""
    phases, outside = _attributed(records, windows)
    return UsageTable(phases, outside, usage_sum(phases.values(), outside), {})


def read_reports(paths: Sequence[Path]) -> list[Report]:
    reports = []
    for path in map(Path, paths):
        table = parse_usage(path.name, read_text(path, "--usage"))
        moment = dt.datetime.fromtimestamp(path.stat().st_mtime, tz=_UTC)
        reports.append(Report(path, _tokens(table.phases, table.outside), moment))
    return reports


def _session_of(workflow: str, files: Sequence[Path], sessions: Sequence[Session]) -> tuple[Session, list[Path]]:
    """Workflow kayitlarini okuyan oturum ve phase_usage report'unun o oturumda okudugu butun dosyalar."""
    wanted = {real_path(path) for path in files}
    for session in sessions:
        try:
            transcripts = phase_usage.find_transcripts(session.path, None)
        except phase_usage.UsageError as exc:
            raise UsageError(f"--session {session.path}: {exc}") from exc
        if wanted <= {real_path(path) for path in transcripts}:
            return session, transcripts
    raise UsageError(f"--exclude-workflow {workflow}: kayıtları hiçbir --session'ın alt ajan klasöründe "
                     "(<oturum-id>\\subagents) değil; raporun bu token'ları içerdiği denetlenemez (workflow'un "
                     "oturumunu --session ile ver)")


def _report_of(workflow: str, session: Session, records: Sequence[phase_usage.Rec],
               windows: Sequence[phase_usage.Window], reports: Sequence[Report]) -> Report:
    """Oturumun raporu: rapor anina kadarki kayitlardan ayni pencerelerle yeniden hesaplanan token'larla ayni olan."""
    matches = [report for report in reports if report.tokens == _tokens(*_attributed(
        (r for r in records if r.ts is None or r.ts <= report.moment), windows))]
    if not matches:
        raise UsageError(f"--exclude-workflow {workflow}: {session.path.name} oturumunun raporu yok ya da tutmuyor: "
                         "hiçbir --usage, phase_usage'in bu oturumun rapor anına kadarki kayıtlarından yeniden "
                         "hesapladığıyla aynı değil. Rapor bu workflow'u içermiyor ya da eksik içeriyor olabilir "
                         "(workflow/faz sürerken, A9 öncesi phase_usage ya da başka --subagents ile üretilmiş, elle "
                         f"yazılmış); {REMEDY}")
    if len(matches) > 1:
        raise UsageError(f"--exclude-workflow {workflow}: {session.path.name} oturumunun birden çok raporu verilmiş "
                         f"({matches[0].path} ve {matches[1].path}); oturum başına yalnız son raporu ver")
    return matches[0]


def _check_after(workflow: str, records: Sequence[phase_usage.Rec], report: Report) -> None:
    last = max((r.ts for r in records if r.ts is not None), default=None)
    if last is not None and last > report.moment:
        raise UsageError(f"--exclude-workflow {workflow}: workflow --usage raporundan ({report.path.name}, "
                         f"{phase_usage.format_ts(report.moment)}) sonra da kayıt yazmış (son kayıt "
                         f"{phase_usage.format_ts(last)}); rapor bu token'ları içermiyor; {REMEDY}")


def excluded_usage(usage: UsageTable | None, usage_paths: Sequence[Path], sessions: Sequence[Session] | None,
                   excluded: dict[str, tuple[Path, ...]], phase_log: Path) -> dict[str, UsageTable]:
    """Dislanan workflow -> faz logu pencerelerine dagitilmis token'lari; rapor once denetlenir (modul aciklamasi).
    --usage yoksa token yok: bos, faz logu okunmaz."""
    if usage is None or not excluded:
        return {}
    if sessions is None:
        raise UsageError("--exclude-workflow token'ları için --session gerekli: --usage raporu, dışlanan workflow'un "
                         "oturum kaydından yeniden hesaplanarak denetlenir")
    windows = read_phase_log(phase_log)
    check_phase_log(usage, windows)
    reports = read_reports(usage_paths)
    loaded: dict[Path, list[phase_usage.Rec]] = {}
    removed: dict[str, UsageTable] = {}
    for workflow, files in excluded.items():
        session, transcripts = _session_of(workflow, files, sessions)
        if session.path not in loaded:
            loaded = {**loaded, session.path: phase_usage.load_records(transcripts)[0]}
        report = _report_of(workflow, session, loaded[session.path], windows, reports)
        records, _ = phase_usage.load_records(files)
        _check_after(workflow, records, report)
        removed = {**removed, workflow: workflow_usage(records, windows)}
    return removed
