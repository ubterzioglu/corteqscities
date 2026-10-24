"""run_log testlerinin ortak yardimcilari (test_run_log, test_run_log_exclude): sahte manifest, oturum kaydi, faz
logu, phase_usage CSV'si, alt ajan kayitlari, validate_all ve editorial_score ciktilari, iddia denetimi ve gorsel
inceleme kayitlari; `work` fixture'i ve tek satir JSON okuyan `run`."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

import editorial_score
import phase_usage
import run_log

PHASES = ["intake", "sources", "answers", "places", "photos", "assemble", "deliver"]
DAY = "2026-10-22T"
TIMES = {"intake": ("10:00:00", "10:01:00"), "sources": ("10:02:00", "10:20:00"), "answers": ("10:30:00", "12:30:00"),
         "places": ("12:30:00", "14:00:00"), "photos": ("14:00:00", "17:00:00"),
         "assemble": ("17:00:00", "17:30:00"), "deliver": ("17:30:00", "17:45:00")}
GATES = {"intake": [0], "sources": [1], "answers": [1, 1], "places": [1], "photos": [0], "assemble": [1], "deliver": []}
COUNTS = {"answers": 289, "places": 104, "neighborhoods": 16, "routes": 12, "glossary": 60, "topics": 12,
          "photos": 201, "hero_photos": 8}
PHOTO_GAPS = {"photos": {"actual": 156, "minimum": 187}, "hero_photos": {"actual": 0, "minimum": 6}}
SCORE_P1 = editorial_score.build_report({"categories": {"A": 20, "B": 10, "C": 10, "D": 5, "E": 3},
                                         "findings": [{"id": "ISS-001", "priority": "P1"}]})
OUTSIDE_USAGE = phase_usage.Row(phase_usage.OUTSIDE, calls=1, input=5, cache_creation=50, cache_read=500, output=25)
AUDIT_RESULTS = ["doğru"] * 6 + ["yanlış", "eksik_koşul"]  # hata orani 2/8
REVIEW_RESULTS = ["keep", "keep", "flag", "reject", "reject"]  # 5 karenin 2'si reddedildi
VERIFY_OK = [True, False]  # ikinci goz 2 karenin 1'ini atti


# ---------- sahte girdiler ----------

def write_json(path: Path, payload) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_jsonl(path: Path, records) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")
    return path


def phase_state(name: str, status: str = "done", end: bool = True) -> dict:
    start, finish = TIMES[name]
    state = {"status": status, "started_at": f"{DAY}{start}Z",
             "gates": [{"script": f"kapi-{i}", "exit_code": code, "summary": {"n": i}}
                       for i, code in enumerate(GATES[name])]}
    return {**state, "ended_at": f"{DAY}{finish}Z"} if end else state


def manifest(tmp_path: Path, phases: dict | None = None, **extra) -> dict:
    return {"schema_version": "1",
            "city": {"city_id": "testkent", "name": "Testkent", "country": "NL", "city_code": "CITY-999"},
            "paths": {"work": str(tmp_path / "work"), "package_root": str(tmp_path / "work" / "paket"),
                      "template_xlsx": "sablon.xlsx", "tools": "arac"},
            "phase": "deliver", "phases": {n: phase_state(n) for n in PHASES} if phases is None else phases,
            "open_items": [], **extra}


def window_seconds(name: str) -> float:
    start, end = (phase_usage.parse_ts(f"{DAY}{clock}Z") for clock in TIMES[name])
    return (end - start).total_seconds()


def urow(name: str, k: int, seconds: float | None = None) -> phase_usage.Row:
    """total_input 1110k, uncached_input 110k, output 50k; sure = faz penceresi (phase_log, manifest ile ayni)."""
    duration = seconds if seconds is not None else window_seconds(name) if name in TIMES else 60.0 * k
    return phase_usage.Row(name, calls=k, input=10 * k, cache_creation=100 * k, cache_read=1000 * k,
                           output=50 * k, thinking=k, duration=duration)


def write_usage(path: Path, phases: dict[str, int], seconds: dict[str, float] | None = None) -> Path:
    """phase_usage'in kendi yazicisiyla (sozlesme) elle kurulmus rapor: faz satirlari + disarisi + TOTAL."""
    rows = [urow(name, k, (seconds or {}).get(name)) for name, k in phases.items()] + [OUTSIDE_USAGE]
    phase_usage.write_csv(path, [*rows, phase_usage.total_row(rows)])
    return path


def all_phases_usage(path: Path) -> Path:
    return write_usage(path, {name: k for k, name in enumerate(PHASES, start=1)})


def validation_report(errors: int = 0, media: int = 0, gaps: dict | None = None) -> dict:
    gaps = {} if gaps is None else gaps
    summary = {"tool": "validate_all", "mode": "emit", "new_content": True,
               "structure": {"errors": errors, "warnings": 7}, "media": {"errors": media}, "minimum_gaps": gaps,
               "error_classes": [], "media_classes": [], "technically_complete": not (errors or media or gaps)}
    return {"summary": summary,
            "structure": {"valid": not errors, "counts": COUNTS, "errors": ["Yanıtlar!8: x"] * errors, "warnings": []},
            "media": {"errors": ["m"] * media}}


def agent_file(directory: Path, agent_id: str, ts: str | None, model: str | None, meta_model: str | None = None,
               synthetic_first: bool = False) -> Path:
    stamp = {"timestamp": ts} if ts else {}
    usage = {"input_tokens": 1, "output_tokens": 1}
    lines = [{"type": "user", "isSidechain": True, "agentId": agent_id,
              "message": {"role": "user", "content": "görev"}, **stamp}]
    if synthetic_first:
        lines.append({"type": "assistant", **stamp, "message": {"model": "<synthetic>", "usage": usage}})
    if model:
        lines.append({"type": "assistant", **stamp, "message": {"id": f"m-{agent_id}", "model": model, "usage": usage}})
    path = write_jsonl(directory / f"agent-{agent_id}.jsonl", lines)
    if meta_model:
        write_json(directory / f"agent-{agent_id}.meta.json", {"agentType": "general-purpose", "model": meta_model})
    return path


def make_subagents(sub: Path) -> Path:
    agent_file(sub, "a1", f"{DAY}10:05:00.000Z", "claude-sonnet-4-6")                  # sources
    agent_file(sub, "a2", f"{DAY}10:35:00.000Z", "claude-opus-4-5-20251101", synthetic_first=True)  # answers
    agent_file(sub, "a3", f"{DAY}11:00:00.000Z", None, meta_model="sonnet")            # answers, model meta'dan
    agent_file(sub, "a4", f"{DAY}10:25:00.000Z", "claude-sonnet-4-6")                  # fazlar arasi: faz disi
    agent_file(sub, "a5", None, None)                                                   # zamansiz: faz disi
    agent_file(sub, "b1", f"{DAY}12:30:00.000Z", "claude-sonnet-4-6")                  # sinir: places (baslangic dahil)
    workflow = sub / "workflows" / "wf_test-1"
    agent_file(workflow, "w1", f"{DAY}12:45:00.000Z", "claude-opus-4-5")              # places (workflow alt klasoru)
    agent_file(workflow, "w2", f"{DAY}12:50:00.000Z", "claude-haiku-4-5-20251001")    # places
    return sub


def assistant(clock: str, mid: str, tokens: int) -> dict:
    return {"type": "assistant", "timestamp": f"{DAY}{clock}Z",
            "message": {"id": mid, "role": "assistant", "usage": {"input_tokens": tokens, "output_tokens": tokens}}}


def session_file(path: Path, first: str, last: str, records: tuple[dict, ...] = ()) -> Path:
    """Claude Code oturum kaydi: ilk ve son zaman damgali satirlar, arada asistan kayitlari."""
    return write_jsonl(path, [{"type": "queue-operation", "timestamp": f"{DAY}{first}Z"}, *records,
                              {"type": "system", "timestamp": f"{DAY}{last}Z"}])


def audit_dir(work: Path, results: list[str] = AUDIT_RESULTS) -> Path:
    folder = work / "_is" / "denetim"
    write_jsonl(folder / "konu_iddia.jsonl", [{"claim_id": f"C-{i}", "sonuç": r} for i, r in enumerate(results)])
    write_jsonl(folder / "konu_karar.jsonl", [{"entry_id": "e1", "karar": "düzelt"}])  # klasorde yalniz *_iddia okunur
    return folder


def review_dir(work: Path) -> Path:
    folder = work / "_is" / "foto" / "inceleme"
    write_jsonl(folder / "review_tur1_p1.jsonl", [{"key": f"k{i}", "result": r} for i, r in enumerate(REVIEW_RESULTS)])
    write_jsonl(folder / "verify_tur1_p1.jsonl", [{"key": f"k{i}", "ok": ok} for i, ok in enumerate(VERIFY_OK)])
    write_jsonl(folder / "selected_tur1_p1.jsonl", [{"key": "k0", "entry_id": "e1"}])  # secim dosyasi sayilmaz
    return folder


def quality_args(tmp_path: Path, work: Path) -> list[str]:
    """Oturumdan bagimsiz girdiler: manifest, dogrulama, skor, iddia denetimi, gorsel inceleme, not."""
    m = write_json(work / "manifest.json", manifest(tmp_path))
    v = write_json(work / "_is" / "validation_emit.json", validation_report(gaps=PHOTO_GAPS))
    s = write_json(tmp_path / "denetim" / "score.json", SCORE_P1)
    return [str(x) for x in ("--manifest", m, "--validation", v, "--score", s, "--claim-audit", audit_dir(work),
                             "--photo-review", review_dir(work), "--note", "ilk deneme")]


def full_inputs(tmp_path: Path, work: Path) -> list[str]:
    session = session_file(tmp_path / "oturum" / "sess.jsonl", "09:00:00", "18:00:00")
    make_subagents(tmp_path / "oturum" / "sess" / "subagents")  # oturumdan turetilen varsayilan alt ajan klasoru
    usage = all_phases_usage(work / "_is" / "token_fazlar.csv")
    phase_log(work / "_is" / "phase_log.jsonl")  # SKILL.md yeri; yalniz --exclude-workflow token'lari icin okunur
    return [*quality_args(tmp_path, work), "--session", str(session), "--usage", str(usage)]


def phase_log(path: Path, **clocks: tuple[str, str]) -> Path:
    times = {**TIMES, **clocks}  # varsayilan: manifest ile ayni saatler
    return write_jsonl(path, [{"phase": n, "event": e, "ts": f"{DAY}{times[n][i]}Z"}
                              for n in PHASES for i, e in enumerate(("start", "end"))])


def usage_report(capsys, session: Path, log: Path, out: Path, *extra: str) -> Path:
    """Gercek phase_usage report'u (oturum + <oturum>\\subagents, workflow'lar dahil)."""
    assert phase_usage.main(["report", "--session", str(session), "--log", str(log), "--out", str(out),
                             *extra]) == 0
    capsys.readouterr()
    return out


def split_city(tmp_path: Path, capsys) -> dict[str, Path]:
    """Sehir iki oturumda: A intake..places'in basi (12:45'te oturum sinirinda kapandi), B places'in sonu..deliver."""
    log = phase_log(tmp_path / "phase_log.jsonl")
    a = session_file(tmp_path / "A.jsonl", "09:59:00", "12:45:00", tuple(
        assistant(c, f"a{i}", 5) for i, c in enumerate(("10:00:30", "10:05:00", "11:00:00", "12:40:00"))))
    b = session_file(tmp_path / "B.jsonl", "12:50:00", "17:50:00", tuple(
        assistant(c, f"b{i}", 7) for i, c in enumerate(("13:00:00", "15:00:00", "17:10:00", "17:40:00"))))
    agent_file(tmp_path / "B" / "subagents", "pb", f"{DAY}13:05:00.000Z", "claude-opus-4-5")
    return {"A": a, "B": b, "uA": usage_report(capsys, a, log, tmp_path / "uA.csv"),
            "uB": usage_report(capsys, b, log, tmp_path / "uB.csv")}


@pytest.fixture()
def work(tmp_path: Path) -> Path:
    root = tmp_path / "work"
    (root / "paket").mkdir(parents=True)
    (root / "_is").mkdir()
    return root


def run(capsys, *argv) -> tuple[int, dict]:
    code = run_log.main([str(a) for a in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1, lines
    return code, json.loads(lines[0])


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def rows_by_phase(path: Path) -> dict[str, dict[str, str]]:
    return {row["faz"]: row for row in read_rows(path)}


def snapshot(root: Path) -> dict[Path, bytes]:
    return {p: p.read_bytes() for p in root.rglob("*") if p.is_file() and p.name != "RUN_LOG.csv"}
