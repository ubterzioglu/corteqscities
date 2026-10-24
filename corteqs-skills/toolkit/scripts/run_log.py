r"""Sehir basina RUN_LOG.csv: faz basina sure, token, ajan ve kapi sonucu + sehir ozeti satiri (IYILESTIRME_LISTESI D).

Kullanim:
  run_log.py --manifest <WORK>\manifest.json --session <oturum.jsonl>... --usage token_fazlar.csv...
             [--subagents <klasor>]... [--exclude-workflow wf_<id>]... [--phase-log <WORK>\_is\phase_log.jsonl]
             [--validation validation_emit.json] [--score score.json] [--claim-audit <WORK>\_is\denetim]...
             [--photo-review <WORK>\_is\foto\inceleme]... [--note "ilk deneme"] [--out <WORK>\RUN_LOG.csv]

Girdiler (hepsi salt okunur; '...' tekrarlanabilir):
  --manifest     zorunlu: sehir kimligi, fazlar (status, started_at, ended_at, gates[].script/exit_code),
                 paths.package_root.
  --session      sehrin islendigi HER Claude Code oturumunun kaydi (<proje>\<oturum-id>.jsonl). Kapsam = kayittaki
                 ilk..son zaman damgasi (+-1 dk); fazin baslangic ya da bitis ani hicbir oturumda yoksa (isareti
                 yazan oturum verilmemis) faz olculmemis sayilir. Alt ajanlar <oturum-id>\subagents'tan (phase_usage).
  --usage        phase_usage report --out CSV'si, oturum basina bir dosya (sayisi --session ile tutmali). Token faz
                 bazinda toplanir; sure toplanmaz (her rapor ayni phase_log penceresini tasir, en buyugu alinir).
                 Ayni rapor (BOM/satir sonu farki dahil) ya da ayni oturumun ara+son raporu (calls>0 bir faz satiri
                 birebir ayni) reddedilir; TOTAL faz satirlariyla tutmali. >=1 dk suren bitmis fazda butun
                 raporlarda token 0 ise o fazin oturum raporu eksik sayilir.
  --subagents    ek alt ajan klasoru (workflows\ dahil). Ajan, kaydindaki ilk zaman damgasinin dustugu faza sayilir
                 [baslangic, bitis); bitissiz pencere yalniz running/blocked fazda aciktir. Model ilk asistan
                 mesajindan, yoksa .meta.json'dan (aile adi: opus/sonnet/haiku; bilinmiyorsa '?').
  --exclude-workflow  ilgisiz workflow'un (subagents\workflows\wf_<id>\) ajanlari sayilmaz ve token'lari dusulur
                 (A9: ayni anda calisan workflow zaman penceresiyle ayrilamaz, klasoruyle ayrilir). O klasordeki
                 agent-*.jsonl kullanimi phase_usage report'unun kodu ve kurallariyla (message.id bir kez, faz logu
                 penceresi) dogrudan toplanir; faz, '(faz dışı)' ve ozet satirlarindan cikarilir. Ozet JSON'da
                 agents_by_workflow (workflow -> faz -> ajan), excluded_agents, excluded_tokens. --usage ile birlikte
                 --session ve faz logu gerekir; dusmeden once rapor denetlenir (run_log_exclude.py): workflow bir
                 --session'in alt ajan klasorunde, o oturumun raporu phase_usage'in rapor anina (dosya saati) kadarki
                 kayitlardan yeniden hesapladigiyla ayni ve workflow rapordan sonra kayit yazmamis olmali; faz logu
                 raporunkiyle tutmali. Tutmazsa cikis 2: rapor workflow ya da faz bitmeden (ara rapor), workflow'suz
                 (A9 oncesi phase_usage) ya da elle uretilmis; workflow bitince phase_usage report'u yeniden uret.
                 Ayrilamayan: ana dongunun (oturum kaydi) o workflow icin harcadigi token ve dogrudan ajanlar.
  --phase-log    phase_usage --log (faz logu); varsayilan manifest paths.usage_log (goreliyse manifest klasorune
                 gore), yoksa <manifest klasoru>\_is\phase_log.jsonl. Yalniz dislanan token'lar icin okunur.
  --validation   validate_all --out raporu: yapi/medya hatasi, asgari eksik; kart/mekan/foto = structure.counts
                 (answers, places, photos; kapak haric). Yalniz tek satir ozeti verilirse sayimlar bos kalir.
  --score        editorial_score --out ciktisi (city-audit score.json): editoryal yuzde ve karar. Karar yalniz
                 buradan gelir; bilinmeyen karar metni (elle yazilmis) reddedilir.
  --claim-audit  bagimsiz iddia denetimi: <parca>_iddia.jsonl ya da klasoru (icindeki *_iddia.jsonl).
                 denetim_hata_orani = 'sonuç' alani 'doğru' olmayan iddialarin yuzdesi (hata/iddia).
  --photo-review gorsel inceleme: review_*.jsonl (result keep/flag/reject), verify_*.jsonl (ikinci goz, ok) ya da
                 klasoru. reddedilen_foto = reject/incelenen; ikinci goz ayri. On eleme (photo_prefilter) sayilmaz.
Cikti: --out (varsayilan: manifest'in klasoru\RUN_LOG.csv); paket klasorune ve bir girdinin ustune yazilmaz. UTF-8
  (Excel icin BOM'lu) CSV, her calismada bastan ve atomik yazilir: city-audit sonrasi ayni komut --score eklenerek
  yeniden calistirilir. Satirlar: 7 faz (sema sirasi), CSV'de olup manifest'te olmayan fazlar, '(faz dışı)' (faz
  penceresi disindaki token ve ajanlar), 'ozet' (sehir ozeti). Zaman manifest'ten (UTC); sure_dk = bitis -
  baslangic, yoksa phase_log suresi; ozette 7 fazin toplami. Olculmeyen hucre bos kalir (0 yazilmaz); nedeni ozet
  JSON'daki gaps listesindedir. Bir faz olculemediyse sehir toplamlari ('(faz dışı)', 'ozet') da bos kalir.
stdout tek satir JSON. Cikis: 0 olcum tam / 1 RUN_LOG yazildi ama olcum eksik (gaps) / 2 kullanim veya yapi hatasi.
Kalite (yapi hatasi, karar, denetim orani) cikis kodunu etkilemez: kapi validate_all, karar city-audit'tir.
Girdi okuyuculari run_log_inputs.py'de, dislanan workflow token'larinin denetimi ve toplami run_log_exclude.py'dedir.
"""
from __future__ import annotations

import argparse
import contextlib
import csv
import datetime as dt
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence

import common
import editorial_score
from run_log_exclude import REMEDY, excluded_usage
from run_log_inputs import (AUDIT_GLOBS, GATE_WORDS, REVIEW_GLOBS, STATUS_TR, WINDOW_TOLERANCE_S, Agent, Audit, Gate,
                            Manifest, Phase, PhotoReview, Quality, Score, Session, Usage, UsageError, UsageTable,
                            expand_inputs, load_json, parse_manifest, read_claim_audit, read_photo_review,
                            read_score, read_sessions, read_usage, read_validation, real_path, scan_agents,
                            session_agent_dirs, workflow_ids)

TOOL = "run_log"
PHASES = ("intake", "sources", "answers", "places", "photos", "assemble", "deliver")  # manifest.schema phase_name
NO_RECORD = "kayıt yok"
OUTSIDE_ROW = "(faz dışı)"
SUMMARY_ROW = "ozet"
COLUMNS = ("sehir", "faz", "baslangic", "bitis", "sure_dk", "toplam_girdi", "onbellek_disi_girdi", "cikti",
           "ajan_sayisi", "kapi_sonucu", "yapi_hatasi", "medya_hatasi", "asgari_eksik", "editoryal_yuzde", "karar",
           "kart", "mekan", "foto", "durum", "model_karisimi", "not", "denetim_hata_orani", "reddedilen_foto")
GATE_NAME_MAX = 40  # faz hucresinde kapi (script) adi en cok bu kadar karakter
COUNT_COLUMNS = {"kart": "answers", "mekan": "places", "foto": "photos"}  # resmi structure.counts anahtarlari
MIN_MEASURED_S = 60.0  # bu kadar suren bitmis fazda token 0 ise oturum raporu eksik sayilir (pilot: 1 sn'lik fazlar)
MAX_GAPS_SHOWN = 12
DEFAULT_PHASE_LOG = ("_is", "phase_log.jsonl")  # city-pack SKILL.md: phase_usage mark ... --log $WORK\_is\...
TOKEN_KEYS = ("total_input", "uncached_input", "output")
_UTC = dt.timezone.utc


@dataclass(frozen=True)
class Inputs:
    manifest: Manifest
    sessions: list[Session] | None
    usage: UsageTable | None  # dislanan workflow'larin token'lari dusulmus
    usage_reports: int
    agents: list[Agent] | None
    excluded: dict[str, int]
    removed: dict[str, UsageTable]  # dislanan workflow -> dusulen token'lari
    quality: Quality | None
    score: Score | None
    audit: Audit | None
    photos: PhotoReview | None
    note: str


# ---------- ajanlarin fazlara dagilimi ----------

def assign_agents(agents: Iterable[Agent], phases: Iterable[Phase]) -> dict[str, list[Agent]]:
    """Ajan, baslangici [start, end) icine dusen faza (cakisirsa en gec baslayana); dusmezse faz disina. Bitisi
    yazilmamis 'done' faz pencere sayilmaz: teslimden sonraki ajanlari yutmaz."""
    windows = sorted((p for p in phases if p.has_window), key=lambda p: p.start)
    buckets: dict[str, list[Agent]] = {}
    for agent in agents:
        home = OUTSIDE_ROW
        for phase in windows if agent.start is not None else ():
            if phase.start <= agent.start and (phase.end is None or agent.start < phase.end):
                home = phase.name
        buckets = {**buckets, home: [*buckets.get(home, []), agent]}
    return buckets


def agents_by_workflow(buckets: dict[str, list[Agent]]) -> dict[str, dict[str, int]]:
    """workflow -> faz -> ajan sayisi: ilgisiz paralel workflow'un fazlara karismasi gorunsun."""
    table: dict[str, dict[str, int]] = {}
    for home, members in buckets.items():
        for agent in members:
            row = table.get(agent.workflow, {})
            table = {**table, agent.workflow: {**row, home: row.get(home, 0) + 1}}
    return dict(sorted(table.items()))


def model_mix(agents: Iterable[Agent]) -> str:
    counts = Counter(agent.model for agent in agents)
    return "; ".join(f"{model} {n}" for model, n in sorted(counts.items(), key=lambda item: (-item[1], item[0])))


# ---------- dislanan workflow'larin token'lari (A9; denetim ve toplam run_log_exclude.py'de) ----------

def phase_log_path(args: argparse.Namespace, manifest_path: Path, manifest: Manifest) -> Path:
    if args.phase_log is not None:
        return Path(args.phase_log)
    log = Path(manifest.usage_log) if manifest.usage_log else Path(*DEFAULT_PHASE_LOG)
    return log if log.is_absolute() else manifest_path.parent / log


def without_workflows(usage: UsageTable, removed: dict[str, UsageTable]) -> UsageTable:
    """Dislanan workflow'larin token'lari faz, faz disi ve toplam satirlarindan dusulur. Rapor denetimden gectiyse
    eksiye dusmez; duserse (denetimin gormedigi durum) yanlis sayi yazilmaz, hata."""
    phases, outside, total = usage.phases, usage.outside, usage.total
    for workflow, part in removed.items():
        phases = {name: row.minus(part.phases.get(name, Usage())) for name, row in phases.items()}
        outside, total = outside.minus(part.outside), total.minus(part.total)
        short = [name for name, row in (*phases.items(), (OUTSIDE_ROW, outside), (SUMMARY_ROW, total))
                 if min(row.tokens) < 0]
        if short:
            raise UsageError(f"--exclude-workflow {workflow}: '{short[0]}' satırında rapordakinden çok token "
                             "düşülecekti; --usage raporu bu workflow'u içermiyor ya da eksik içeriyor (rapor "
                             "workflow bitmeden, A9 öncesi phase_usage ile ya da başka oturum için üretilmiş "
                             f"olabilir); {REMEDY}")
    return UsageTable(phases, outside, total, {})


# ---------- satirlar ----------

def _short(text: str) -> str:
    return text if len(text) <= GATE_NAME_MAX else text[: GATE_NAME_MAX - 1] + "…"


def gate_result(gates: Sequence[Gate]) -> str:
    """Faz hucresi: en kotu sonuc, kapi sayisi ve temiz olmayan kapilar (script=cikis kodu)."""
    if not gates:
        return "kapı yok"
    head = f"{GATE_WORDS[max(gate.code for gate in gates)]} ({len(gates)} kapı)"
    loud = [f"{_short(gate.script)}={gate.code}" for gate in gates if gate.code]
    return f"{head}: {'; '.join(loud)}" if loud else head


def gate_total(gates: Sequence[Gate]) -> str:
    """Ozet hucresi: butun fazlarin kapilari ve temiz olmayanlarin sayisi."""
    if not gates:
        return "kapı yok"
    loud = sum(gate.code > 0 for gate in gates)
    head = f"{GATE_WORDS[max(gate.code for gate in gates)]} ({len(gates)} kapı"
    return f"{head}; {loud} temiz değil)" if loud else f"{head})"


def _ts(value: dt.datetime | None) -> str:
    return value.astimezone(_UTC).strftime("%Y-%m-%dT%H:%M:%SZ") if value else ""


def _minutes(seconds: float | None) -> str:
    return "" if seconds is None else f"{seconds / 60:.1f}"


def phase_list(inputs: Inputs) -> list[Phase]:
    """7 faz (sema sirasi), sonra manifest'te ya da CSV'de gecen diger fazlar (ilk gorulus sirasi)."""
    known = inputs.manifest.phases
    extra = [name for name in known if name not in PHASES]
    if inputs.usage is not None:
        extra += [name for name in inputs.usage.phases if name not in PHASES and name not in extra]
    return [known.get(name, Phase(name, None, None, None)) for name in (*PHASES, *extra)]


def _usage_of(inputs: Inputs, name: str) -> Usage | None:
    return None if inputs.usage is None else inputs.usage.phases.get(name)


def _seconds(phase: Phase, usage: Usage | None) -> float | None:
    if phase.seconds is not None:
        return phase.seconds
    return usage.duration_s if usage is not None and usage.duration_s > 0 else None


def _token_cells(usage: Usage | None) -> dict[str, Any]:
    if usage is None:
        return {}
    return {"toplam_girdi": usage.total_input, "onbellek_disi_girdi": usage.uncached_input, "cikti": usage.output}


def _agent_cells(agents: list[Agent] | None) -> dict[str, Any]:
    return {} if agents is None else {"ajan_sayisi": len(agents), "model_karisimi": model_mix(agents)}


def _quality_cells(inputs: Inputs) -> dict[str, Any]:
    quality, score = inputs.quality, inputs.score
    cells: dict[str, Any] = {"denetim_hata_orani": None if inputs.audit is None else inputs.audit.cell(),
                             "reddedilen_foto": None if inputs.photos is None else inputs.photos.cell()}
    if quality is not None:
        counts = quality.counts or {}
        cells = {**cells, "yapi_hatasi": quality.structure_errors, "medya_hatasi": quality.media_errors,
                 "asgari_eksik": quality.minimum_gaps,
                 **{column: counts[key] for column, key in COUNT_COLUMNS.items() if key in counts}}
    if score is not None:
        percent = editorial_score.NOT_MEASURED if score.percent is None else score.percent
        cells = {**cells, "editoryal_yuzde": percent, "karar": score.decision}
    return cells


def _phase_row(inputs: Inputs, phase: Phase, buckets: dict[str, list[Agent]] | None,
               holes: dict[str, str]) -> dict[str, Any]:
    usage = _usage_of(inputs, phase.name)
    measured = phase.name not in holes
    # baslamamis faz 0 ajandir; pencere yoksa (manifest kaydi ya da bitisi yok) ajan sayilamaz: bos
    countable = buckets is not None and measured and (phase.status == "pending" or phase.has_window)
    return {"sehir": inputs.manifest.city_id, "faz": phase.name, "baslangic": _ts(phase.start),
            "bitis": _ts(phase.end), "sure_dk": _minutes(_seconds(phase, usage)),
            **(_token_cells(usage) if measured else {}),
            **_agent_cells(buckets.get(phase.name, []) if countable else None),
            "kapi_sonucu": gate_result(phase.gates) if phase.status else "",
            "durum": STATUS_TR.get(phase.status, NO_RECORD)}


def build_rows(inputs: Inputs, phases: list[Phase], holes: dict[str, str],
               buckets: dict[str, list[Agent]] | None) -> list[dict[str, Any]]:
    complete = not holes  # bir faz olculemediyse sehir toplamlari da eksik: 0 ya da yarim sayi degil, bos
    outside = {"sehir": inputs.manifest.city_id, "faz": OUTSIDE_ROW,
               **_token_cells(inputs.usage.outside if inputs.usage is not None and complete else None),
               **_agent_cells(buckets.get(OUTSIDE_ROW, []) if buckets is not None and complete else None)}
    rows = [_phase_row(inputs, phase, buckets, holes) for phase in phases]
    return [*rows, outside, summary_row(inputs, phases, complete)]


def summary_row(inputs: Inputs, phases: list[Phase], complete: bool) -> dict[str, Any]:
    canonical = phases[: len(PHASES)]
    seconds = [s for s in (_seconds(p, _usage_of(inputs, p.name)) for p in canonical) if s is not None]
    starts, ends = [p.start for p in phases if p.start], [p.end for p in phases if p.end]
    gates = tuple(gate for phase in phases for gate in phase.gates)
    done = sum(phase.status == "done" for phase in canonical)
    return {"sehir": inputs.manifest.city_id, "faz": SUMMARY_ROW,
            "baslangic": _ts(min(starts)) if starts else "", "bitis": _ts(max(ends)) if ends else "",
            "sure_dk": _minutes(sum(seconds)) if seconds else "",
            **_token_cells(inputs.usage.total if inputs.usage is not None and complete else None),
            **_agent_cells(inputs.agents if complete else None),
            "kapi_sonucu": gate_total(gates) if any(p.status for p in phases) else "",
            **_quality_cells(inputs), "durum": f"bitti {done}/{len(PHASES)}", "not": inputs.note}


# ---------- eksik olcum ----------

def _uncovered(phase: Phase, sessions: Sequence[Session] | None) -> list[str]:
    """Fazin hicbir verilen oturumun icermedigi sinirlari: o siniri isaretleyen oturumun kaydi (ve raporu) eksik."""
    if sessions is None or not phase.has_window:
        return []
    marks = (("başlangıç", phase.start), ("bitiş", phase.end))
    return [label for label, moment in marks if moment is not None and not any(s.holds(moment) for s in sessions)]


def find_holes(inputs: Inputs, phases: Sequence[Phase]) -> dict[str, str]:
    """Olculemeyen fazlar -> neden (token/ajan hucresi bos, 0 yazilmaz): baslangic ya da bitis ani hicbir --session
    kaydinda yok (faz kayip oturuma tasmis) ya da >=1 dk suren bitmis fazda butun raporlarda token 0."""
    holes: dict[str, str] = {}
    for phase in phases:
        usage = _usage_of(inputs, phase.name)
        seconds = _seconds(phase, usage)
        lost = _uncovered(phase, inputs.sessions)
        silent = usage is not None and not usage.total_input and (seconds or 0) >= MIN_MEASURED_S
        if lost:
            holes = {**holes, phase.name: f"fazın {' ve '.join(lost)} anı hiçbir --session kaydında yok"}
        elif phase.status == "done" and silent:
            holes = {**holes, phase.name: f"{_minutes(seconds)} dk süren fazda bütün --usage raporlarında token 0; "
                                          "o oturumun raporu verilmemiş"}
    return holes


def _phase_gaps(phase: Phase, usage: UsageTable | None) -> list[str]:
    if phase.status is None:
        return [f"faz kaydı yok: {phase.name}"]
    if phase.status != "done":
        return [f"faz bitmedi: {phase.name} ({STATUS_TR[phase.status]})"]
    gaps = []
    if phase.start is None or phase.end is None:
        gaps.append(f"zaman eksik: {phase.name} (manifest started_at/ended_at)")
    row = None if usage is None else usage.phases.get(phase.name)
    if usage is not None and row is None:
        gaps.append(f"token satırı yok: {phase.name} (phase_usage mark eksik)")
    elif row is not None and phase.seconds is not None and abs(phase.seconds - row.duration_s) >= WINDOW_TOLERANCE_S:
        gaps.append(f"pencere farkı: {phase.name} (manifest {_minutes(phase.seconds)} dk, phase_log "
                    f"{_minutes(row.duration_s)} dk; ajan/süre ve token farklı pencereden)")
    return gaps


def find_gaps(inputs: Inputs, phases: list[Phase], holes: dict[str, str]) -> list[str]:
    sessions, usage = inputs.sessions, inputs.usage
    gaps = [message for absent, message in (
        (sessions is None, "oturum kapsamı denetlenmedi (--session verilmedi; eksik oturum fark edilmez)"),
        (usage is None, "token ölçümü yok (--usage verilmedi)"),
        (inputs.agents is None, "ajan sayısı ölçülmedi (--session/--subagents verilmedi)"),
        (inputs.quality is None, "resmî doğrulama yok (--validation verilmedi)"),
        (inputs.score is None, "editoryal skor yok (city-audit sonrası --score ile yeniden üret)"),
        (inputs.audit is None, "denetim hata oranı yok (--claim-audit verilmedi)"),
        (inputs.photos is None, "reddedilen foto yok (--photo-review verilmedi)"),
        (sessions is not None and usage is not None and inputs.usage_reports != len(sessions),
         f"rapor sayısı tutmuyor: {len(sessions or ())} oturum, {inputs.usage_reports} --usage "
         "(oturum başına bir rapor)"),
        (inputs.audit is not None and inputs.audit.cell() is None,
         "denetim kaydı boş (--claim-audit: iddia satırı yok)"),
        (inputs.photos is not None and inputs.photos.cell() is None,
         "görsel inceleme kaydı boş (--photo-review: karar satırı yok)"),
    ) if absent]
    if inputs.quality is not None:
        counts = inputs.quality.counts or {}
        missing = [column for column, key in COUNT_COLUMNS.items() if key not in counts]
        if missing:
            gaps.append(f"sayım yok: {', '.join(missing)} (validate_all --out raporu verilmeli)")
    gaps += [f"oturum kaydı yok: {name} ({reason})" for name, reason in holes.items()]
    for phase in phases[: len(PHASES)]:
        gaps += _phase_gaps(phase, usage)
    return gaps


# ---------- cikti ----------

def _inside(child: Path, parent: Path) -> bool:
    try:
        return os.path.commonpath([real_path(child), real_path(parent)]) == real_path(parent)
    except ValueError:  # farkli suruculer
        return False


def check_out(out: Path, manifest_path: Path, package_root: str | None, inputs: Iterable[Path]) -> None:
    if package_root:
        root = Path(package_root)
        if _inside(out, root if root.is_absolute() else manifest_path.parent / root):
            raise UsageError(f"--out paket klasörünün içinde olamaz: {out}")
    for path in inputs:
        if real_path(out) == real_path(path):
            raise UsageError(f"--out bir girdinin üstüne yazamaz: {path}")


def write_csv(path: Path, rows: Sequence[dict[str, Any]]) -> None:
    """Ayni klasorde gecici dosyaya yazar, sonra yerine koyar: yarim RUN_LOG kalmaz."""
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=COLUMNS)
            writer.writeheader()
            writer.writerows({column: "" if row.get(column) is None else row[column] for column in COLUMNS}
                             for row in rows)
        os.replace(temp, path)
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(temp)
        raise


def summary_json(inputs: Inputs, phases: list[Phase], out: Path, gaps: list[str], holes: dict[str, str],
                 buckets: dict[str, list[Agent]] | None) -> dict[str, Any]:
    usage, agents, quality, score, audit = inputs.usage, inputs.agents, inputs.quality, inputs.score, inputs.audit
    total = usage.total if usage is not None and not holes else None  # eksik oturumla sehir toplami yok
    outside_pct = None if total is None else (
        round(100 * usage.outside.total_input / total.total_input, 2) if total.total_input else 0)
    return {
        "tool": TOOL, "status": "eksik" if gaps else "ok", "city": inputs.manifest.city_id, "out": str(out),
        "phases_done": f"{sum(p.status == 'done' for p in phases[: len(PHASES)])}/{len(PHASES)}",
        "sessions": None if inputs.sessions is None else [
            f"{s.path.name} {_ts(s.first)}..{_ts(s.last)}" for s in inputs.sessions],
        "total_input": None if total is None else total.total_input,
        "uncached_input": None if total is None else total.uncached_input,
        "output": None if total is None else total.output, "outside_pct": outside_pct,
        "agents": None if agents is None or holes else len(agents),
        "agents_untimed": None if agents is None else sum(agent.start is None for agent in agents),
        "agents_by_workflow": None if buckets is None else agents_by_workflow(buckets),
        "excluded_agents": inputs.excluded or None,
        "excluded_tokens": {workflow: dict(zip(TOKEN_KEYS, part.total.tokens))
                            for workflow, part in inputs.removed.items()} or None,
        "structure_errors": None if quality is None else quality.structure_errors,
        "media_errors": None if quality is None else quality.media_errors,
        "minimum_gaps": None if quality is None else quality.minimum_gaps,
        "editorial_percent": None if score is None else score.percent,
        "decision": None if score is None else score.decision,
        "audit_error_pct": None if audit is None or not audit.claims else round(100 * audit.errors / audit.claims, 1),
        "photos_rejected": None if inputs.photos is None else inputs.photos.cell(),
        "gap_count": len(gaps), "gaps": gaps[:MAX_GAPS_SHOWN],
    }


# ---------- CLI ----------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Şehir başına RUN_LOG.csv: faz başına süre, token, ajan, kapı sonucu ve şehir özeti satırı")
    parser.add_argument("--manifest", type=Path, required=True, help="WORK\\manifest.json")
    parser.add_argument("--session", type=Path, action="append",
                        help="şehrin işlendiği her oturumun kaydı (<oturum-id>.jsonl, tekrarlanabilir); kapsam ve "
                             "varsayılan alt ajan klasörü (<oturum-id>\\subagents)")
    parser.add_argument("--usage", type=Path, action="append",
                        help="phase_usage report --out CSV'si (oturum başına bir dosya, tekrarlanabilir)")
    parser.add_argument("--subagents", type=Path, action="append",
                        help="ek alt ajan klasörü (workflows alt klasörleri dahil, tekrarlanabilir)")
    parser.add_argument("--exclude-workflow", action="append", metavar="WF",
                        help="şehirle ilgisiz workflow'un (wf_<id>) ajanlarını sayma, token'larını düş "
                             "(tekrarlanabilir)")
    parser.add_argument("--phase-log", type=Path,
                        help="phase_usage --log (faz logu), dışlanan token'ları fazlara dağıtmak için; varsayılan: "
                             "manifest paths.usage_log, yoksa manifest klasörü\\_is\\phase_log.jsonl")
    parser.add_argument("--validation", type=Path, help="validate_all --out raporu")
    parser.add_argument("--score", type=Path, help="editorial_score --out (city-audit score.json)")
    parser.add_argument("--claim-audit", type=Path, action="append",
                        help="iddia denetimi: <parça>_iddia.jsonl ya da klasörü (tekrarlanabilir)")
    parser.add_argument("--photo-review", type=Path, action="append",
                        help="görsel inceleme: review_*.jsonl / verify_*.jsonl ya da klasörü (tekrarlanabilir)")
    parser.add_argument("--note", default="", help="özet satırına not, ör. 'ilk deneme'")
    parser.add_argument("--out", type=Path, help="varsayılan: manifest klasörü\\RUN_LOG.csv")
    return parser


def collect_inputs(args: argparse.Namespace, manifest: Manifest, sessions: list[Session] | None,
                   audit_files: list[Path], review_files: list[Path], phase_log: Path) -> Inputs:
    exclude = workflow_ids(args.exclude_workflow or [])
    measured = sessions is not None or bool(args.subagents)  # oturum verildiyse alt ajansiz oturum = 0 ajan
    if exclude and not measured:
        raise UsageError("--exclude-workflow için --session ya da --subagents gerekli")
    folders = [*(args.subagents or []), *session_agent_dirs(sessions)]
    agents, excluded = scan_agents(folders, exclude) if measured else (None, {})
    usage = read_usage(list(args.usage or []))
    removed = excluded_usage(usage, list(args.usage or []), sessions, excluded, phase_log)
    return Inputs(
        manifest, sessions, without_workflows(usage, removed) if removed else usage, len(args.usage or []), agents,
        {workflow: len(paths) for workflow, paths in excluded.items()}, removed,
        None if args.validation is None else read_validation(load_json(args.validation, "--validation")),
        None if args.score is None else read_score(load_json(args.score, "--score")),
        read_claim_audit(audit_files) if args.claim_audit else None,
        read_photo_review(review_files) if args.photo_review else None, (args.note or "").strip())


def run(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    manifest = parse_manifest(load_json(manifest_path, "manifest"))
    out = Path(args.out) if args.out else manifest_path.parent / "RUN_LOG.csv"
    sessions = read_sessions(list(args.session or []))
    audit_files = expand_inputs(args.claim_audit or [], AUDIT_GLOBS, "--claim-audit")
    review_files = expand_inputs(args.photo_review or [], REVIEW_GLOBS, "--photo-review")
    phase_log = phase_log_path(args, manifest_path, manifest)
    singles = [path for path in (args.validation, args.score) if path is not None]
    check_out(out, manifest_path, manifest.package_root,
              [manifest_path, phase_log, *(args.usage or []), *singles, *(s.path for s in sessions or ()),
               *audit_files, *review_files])
    inputs = collect_inputs(args, manifest, sessions, audit_files, review_files, phase_log)
    phases = phase_list(inputs)
    holes = find_holes(inputs, phases)
    gaps = find_gaps(inputs, phases, holes)
    buckets = None if inputs.agents is None else assign_agents(inputs.agents, phases)
    try:
        write_csv(out, build_rows(inputs, phases, holes, buckets))
    except OSError as exc:
        hint = "; dosya Excel'de açık olabilir" if isinstance(exc, PermissionError) else ""
        raise UsageError(f"RUN_LOG yazılamadı: {out} ({exc.strerror or exc}){hint}") from exc
    common.emit(summary_json(inputs, phases, out, gaps, holes, buckets))
    return common.EXIT_FINDINGS if gaps else common.EXIT_OK


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return common.EXIT_USAGE if stop.code else common.EXIT_OK
    try:
        return run(args)
    except (UsageError, OSError, ValueError, csv.Error) as exc:  # yakalanmazsa cikis 1 olur, 'eksik' ile karisir
        common.emit({"tool": TOOL, "error": str(exc)})
        return common.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
