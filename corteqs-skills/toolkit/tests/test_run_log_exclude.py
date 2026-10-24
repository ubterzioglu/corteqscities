"""run_log --exclude-workflow (A9) testleri: ilgisiz paralel workflow'un ajanlari sayilmaz, token'lari faz logu
pencereleriyle --usage raporundan dusulur. Dusmeden once rapor denetlenir: workflow'un oturumu --session ile
verilmeli, o oturumun raporu phase_usage'in rapor anina kadarki kayitlardan yeniden hesapladigiyla tutmali ve
workflow rapordan sonra kayit yazmamis olmali; yoksa cikis 2. Sonda run_log dosya duzeni ve satir sinirlari."""
from __future__ import annotations

import importlib
import json
import os
from pathlib import Path

import pytest

import phase_usage
import run_log
import run_log_inputs
from run_log_helpers import (DAY, PHASES, TIMES, agent_file, assistant, full_inputs, manifest, phase_log,
                             quality_args, rows_by_phase, run, session_file, usage_report, write_json, write_jsonl)
from run_log_helpers import work  # noqa: F401  pytest fixture'i

FLOWS = ("oturum", "sess", "subagents", "workflows")  # tmp_path altinda oturumun workflow klasorleri
BASKA = (("12:30:00.500", "o0", 3), ("12:50:00", "o1", 1000), ("12:50:01", "o1", 1000), ("19:00:00", "o2", 7))
UNTIMED = {"type": "assistant", "message": {"id": "m-zamansiz", "role": "assistant",  # rapor da yeniden hesap da
                                            "usage": {"input_tokens": 0, "output_tokens": 0}}}  # faz disina koyar
REMEDY = "phase_usage report'u yeniden üret"  # rapor workflow/faz bitmeden uretildiyse cozum


def flow_dir(tmp_path: Path, workflow: str) -> Path:
    return tmp_path.joinpath(*FLOWS, workflow)


def report_written_at(report: Path, clock: str) -> None:
    """Raporun dosya saati = uretildigi an; run_log rapor anini buradan okur."""
    moment = phase_usage.parse_ts(f"{DAY}{clock}Z").timestamp()
    os.utime(report, (moment, moment))


def parallel_workflows(tmp_path: Path, work: Path, capsys, log: Path, subagents: Path | None = None,
                       main_outside: int = 0) -> list[str]:
    """Tek oturum, places sirasinda iki paralel workflow (A9). Ana dongu her fazda 5 token (main_outside verilirse
    teslimden sonra 17:50'de o kadar, faz disi); sehrin wf_sehir-1'i places'ta 100; ilgisiz wf_baska-9 places'ta
    1000 (akis tekrari bir kez), faz logunda places 12:30:01'de baslar (manifest 12:30:00): 12:30:00.5'teki 3 token
    faz disidir; teslimden sonra 7 (faz disi). Rapor gercek phase_usage report'u; subagents verilirse workflow
    ajanlari rapora girmez (A9 oncesi phase_usage gibi)."""
    phase_log(log, places=("12:30:01", TIMES["places"][1]))
    main = tuple(assistant(f"{TIMES[n][0][:5]}:30", f"m-{n}", 5) for n in PHASES)
    late = (assistant("17:50:00", "m-out", main_outside),) if main_outside else ()
    session = session_file(tmp_path / "oturum" / "sess.jsonl", "09:00:00", "18:00:00", (*main, *late, UNTIMED))
    write_jsonl(flow_dir(tmp_path, "wf_sehir-1") / "agent-s1.jsonl", [assistant("12:45:00", "s1", 100)])
    write_jsonl(flow_dir(tmp_path, "wf_baska-9") / "agent-o1.jsonl", [assistant(*record) for record in BASKA])
    usage = usage_report(capsys, session, log, work / "_is" / "token_fazlar.csv",
                         *(["--subagents", str(subagents)] if subagents else []))
    return [*quality_args(tmp_path, work), "--session", str(session), "--usage", str(usage)]


# ---------- dogru dislama ----------

@pytest.mark.parametrize("where", ["varsayilan", "manifest", "arguman"])
def test_excluded_workflow_agents_and_tokens_are_removed_by_the_phase_log_windows(tmp_path, work, capsys, where):
    log = {"varsayilan": work / "_is" / "phase_log.jsonl", "manifest": work / "kayit" / "faz.jsonl",
           "arguman": tmp_path / "baska" / "faz.jsonl"}[where]
    args = parallel_workflows(tmp_path, work, capsys, log)
    if where == "manifest":  # paths.usage_log manifest klasorune gore
        data = manifest(tmp_path)
        data["paths"]["usage_log"] = "kayit/faz.jsonl"
        write_json(work / "manifest.json", data)
    _, before = run(capsys, *args)
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert (by["places"]["toplam_girdi"], by["(faz dışı)"]["toplam_girdi"]) == ("1105", "10")  # dislamadan: hepsi
    assert (by["places"]["ajan_sayisi"], before["total_input"], before["excluded_tokens"]) == ("2", 1145, None)
    assert before["agents_by_workflow"] == {"wf_baska-9": {"places": 1}, "wf_sehir-1": {"places": 1}}  # gorunur
    code, after = run(capsys, *args, *(["--phase-log", log] if where == "arguman" else []),
                      "--exclude-workflow", "wf_baska-9")
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 0 and after["gaps"] == [] and after["excluded_agents"] == {"wf_baska-9": 1}
    assert after["agents_by_workflow"] == {"wf_sehir-1": {"places": 1}}
    assert (by["places"]["ajan_sayisi"], by["ozet"]["ajan_sayisi"]) == ("1", "1")
    assert [by["places"][c] for c in ("toplam_girdi", "onbellek_disi_girdi", "cikti")] == ["105"] * 3  # 5 + 100
    assert by["(faz dışı)"]["toplam_girdi"] == "0"  # sinirdaki 3 token faz logunda faz disi: oradan dusulur
    assert [by[n]["toplam_girdi"] for n in PHASES if n != "places"] == ["5"] * 6
    assert (after["total_input"], after["uncached_input"], after["output"], by["ozet"]["toplam_girdi"]) == (
        135, 135, 135, "135")
    assert after["excluded_tokens"] == {"wf_baska-9": {"total_input": 1010, "uncached_input": 1010, "output": 1010}}


def test_session_that_went_on_after_the_report_still_allows_exclusion(tmp_path, work, capsys):
    args = parallel_workflows(tmp_path, work, capsys, work / "_is" / "phase_log.jsonl")
    with (tmp_path / "oturum" / "sess.jsonl").open("a", encoding="utf-8") as stream:  # ana dongu rapordan sonra da
        stream.write(json.dumps(assistant("19:20:00", "m-sonra", 20)) + "\n")       # yazar (ornegin run_log cagrisi)
    report_written_at(work / "_is" / "token_fazlar.csv", "19:10:00")  # workflow'un son kaydi 19:00: rapordan once
    code, after = run(capsys, *args, "--exclude-workflow", "wf_baska-9")
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 0 and (by["places"]["toplam_girdi"], by["(faz dışı)"]["toplam_girdi"]) == ("105", "0")
    assert after["total_input"] == 135  # rapordan sonraki 20 token ne raporda ne denetimde


def test_exclude_without_usage_needs_no_phase_log(tmp_path, work, capsys):
    m = write_json(work / "manifest.json", manifest(tmp_path))
    sub = tmp_path / "s"
    agent_file(sub / "workflows" / "wf_x-1", "x1", f"{DAY}10:05:00.000Z", "claude-opus-4-5")
    agent_file(sub, "d1", f"{DAY}10:06:00.000Z", "claude-opus-4-5")
    code, summary = run(capsys, "--manifest", m, "--subagents", sub, "--exclude-workflow", "wf_x-1")
    assert not (work / "_is" / "phase_log.jsonl").exists()  # token yok: faz logu okunmaz
    assert code == 1 and summary["excluded_agents"] == {"wf_x-1": 1} and summary["excluded_tokens"] is None
    assert rows_by_phase(work / "RUN_LOG.csv")["sources"]["ajan_sayisi"] == "1"


@pytest.mark.parametrize("bad", ["wf_yok-1", "baska-9"])
def test_unknown_or_malformed_workflow_id_is_refused(tmp_path, work, capsys, bad):
    code, summary = run(capsys, *full_inputs(tmp_path, work), "--exclude-workflow", bad)
    assert code == 2 and bad in summary["error"] and not (work / "RUN_LOG.csv").exists()


# ---------- rapor dislanan token'lari icermiyorsa cikis 2 ----------

@pytest.mark.parametrize("case", ["sahte_rapor", "rapordan_sonra_basladi"])
def test_report_that_never_had_the_workflow_is_refused_even_if_no_row_goes_negative(tmp_path, work, capsys, case):
    if case == "sahte_rapor":  # elle kurulmus rapor workflow'u hic gormedi; places 4440'tan sessizce 1 dusulurdu
        args = full_inputs(tmp_path, work)
        agent_file(flow_dir(tmp_path, "wf_baska-9"), "o1", f"{DAY}12:40:00.000Z", "claude-opus-4-5")
        workflow = "wf_baska-9"
    else:  # Eindhoven: rapor 19:15'te yazildi, ilgisiz workflow 19:30'da basladi; faz disi 60'tan 2 dusulurdu
        args = parallel_workflows(tmp_path, work, capsys, work / "_is" / "phase_log.jsonl", main_outside=50)
        write_jsonl(flow_dir(tmp_path, "wf_gec-3") / "agent-g1.jsonl", [assistant("19:30:00", "g1", 2)])
        report_written_at(work / "_is" / "token_fazlar.csv", "19:15:00")
        workflow = "wf_gec-3"
    code, summary = run(capsys, *args, "--exclude-workflow", workflow)
    assert code == 2 and workflow in summary["error"] and REMEDY in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("report_at", ["19:15:00", None], ids=["rapor_ani_19_15", "dosya_saati"])
def test_workflow_that_kept_writing_after_the_report_is_refused(tmp_path, work, capsys, report_at):
    args = parallel_workflows(tmp_path, work, capsys, work / "_is" / "phase_log.jsonl", main_outside=50)
    late = [assistant(*record) for record in (*BASKA, ("19:30:00", "o3", 30))]  # rapordan sonra 30 token daha
    write_jsonl(flow_dir(tmp_path, "wf_baska-9") / "agent-o1.jsonl", late)
    if report_at:
        report_written_at(work / "_is" / "token_fazlar.csv", report_at)
    code, summary = run(capsys, *args, "--exclude-workflow", "wf_baska-9")  # faz disi 60-40=20 olurdu (dogrusu 50)
    assert code == 2 and "wf_baska-9" in summary["error"] and REMEDY in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


def test_report_without_the_excluded_workflow_tokens_is_refused(tmp_path, work, capsys):
    args = parallel_workflows(tmp_path, work, capsys, work / "_is" / "phase_log.jsonl", subagents=tmp_path / "bos")
    code, summary = run(capsys, *args, "--exclude-workflow", "wf_baska-9")  # A9 oncesi phase_usage gibi workflow'suz
    assert code == 2 and "wf_baska-9" in summary["error"] and "içermiyor" in summary["error"]
    assert REMEDY in summary["error"] and not (work / "RUN_LOG.csv").exists()


def test_two_reports_of_the_workflows_session_are_refused(tmp_path, work, capsys):
    log = work / "_is" / "phase_log.jsonl"
    args = parallel_workflows(tmp_path, work, capsys, log)
    early = session_file(tmp_path / "ara" / "sess.jsonl", "09:00:00", "09:30:00")  # ayni oturum 09:30'da: kayit yok
    interim = usage_report(capsys, early, log, work / "_is" / "token_ara.csv")
    report_written_at(interim, "09:30:00")  # calls>0 satiri yok: read_usage ikinciyi yakalayamaz
    code, summary = run(capsys, *args, "--usage", interim, "--exclude-workflow", "wf_baska-9")
    assert code == 2 and "birden çok raporu" in summary["error"] and not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("case, needle", [("oturumsuz", "--session gerekli"),
                                          ("oturum_disi", "alt ajan klasöründe")])
def test_excluded_tokens_that_cannot_be_checked_against_a_session_are_refused(tmp_path, work, capsys, case, needle):
    args = parallel_workflows(tmp_path, work, capsys, work / "_is" / "phase_log.jsonl")
    workflow = "wf_baska-9"
    if case == "oturumsuz":  # rapor hicbir oturum kaydiyla karsilastirilamaz
        at = args.index("--session")
        args = [*args[:at], *args[at + 2:], "--subagents", str(tmp_path.joinpath(*FLOWS[:-1]))]
    else:  # workflow verilen oturumun alt ajan klasorunde degil: o oturumun raporu onu icermez
        write_jsonl(tmp_path / "ek" / "workflows" / "wf_ek-2" / "agent-e1.jsonl", [assistant("12:55:00", "e1", 1)])
        args, workflow = [*args, "--subagents", str(tmp_path / "ek")], "wf_ek-2"
    code, summary = run(capsys, *args, "--exclude-workflow", workflow)
    assert code == 2 and needle in summary["error"] and not (work / "RUN_LOG.csv").exists()


def test_excluded_workflow_tokens_need_the_phase_log(tmp_path, work, capsys):
    args = parallel_workflows(tmp_path, work, capsys, tmp_path / "gecici" / "faz.jsonl")  # varsayilan yerde log yok
    code, summary = run(capsys, *args, "--exclude-workflow", "wf_baska-9")
    assert code == 2 and "--phase-log" in summary["error"] and not (work / "RUN_LOG.csv").exists()


def test_phase_log_that_does_not_match_the_report_is_refused(tmp_path, work, capsys):
    args = parallel_workflows(tmp_path, work, capsys, tmp_path / "rapor_logu.jsonl")
    other = phase_log(tmp_path / "baska_logu.jsonl")  # places 12:30:00'da baslar: raporun penceresi degil
    code, summary = run(capsys, *args, "--phase-log", other, "--exclude-workflow", "wf_baska-9")
    assert code == 2 and "faz logu" in summary["error"] and "places" in summary["error"]
    assert REMEDY in summary["error"] and not (work / "RUN_LOG.csv").exists()  # ara rapor da olabilir


def test_subtracting_more_than_the_report_holds_is_refused():
    row, empty = run_log_inputs.Usage(5, 5, 5, 60.0), run_log_inputs.Usage()
    usage = run_log_inputs.UsageTable({"places": row}, empty, row, {})
    part = run_log_inputs.UsageTable({"places": run_log_inputs.Usage(6, 6, 6)}, empty, run_log_inputs.Usage(6, 6, 6),
                                     {})
    with pytest.raises(run_log_inputs.UsageError, match=f"places.*{REMEDY}"):
        run_log.without_workflows(usage, {"wf_x-1": part})


# ---------- dosya duzeni ----------

READERS = ("parse_manifest", "read_sessions", "session_agent_dirs", "read_usage", "scan_agents", "workflow_ids",
           "read_validation", "read_score", "read_claim_audit", "read_photo_review", "expand_inputs", "load_json")
EXCLUSION = ("read_phase_log", "check_phase_log", "workflow_usage", "excluded_usage")
SCRIPT_MAX_LINES = 600  # gorev hedefi: run_log betiklerinin her biri 600 satirin altinda
TEST_MAX_LINES = 800  # kodlama kurali: dosya en cok 800 satir (bolmenin nedeni)


def test_input_readers_live_in_run_log_inputs():
    for name in READERS:
        reader = getattr(run_log_inputs, name)
        assert reader.__module__ == "run_log_inputs", name
        assert getattr(run_log, name, None) in (None, reader), name  # run_log'da ikinci kopya yok
    assert run_log.UsageError is run_log_inputs.UsageError  # okuyucu hatasi run_log'da cikis 2 olur


def test_exclusion_lives_in_run_log_exclude():
    module = importlib.import_module("run_log_exclude")
    for name in EXCLUSION:
        function = getattr(module, name)
        assert function.__module__ == "run_log_exclude", name
        assert getattr(run_log, name, None) in (None, function), name


@pytest.mark.parametrize("name", ["run_log.py", "run_log_inputs.py", "run_log_exclude.py"])
def test_script_stays_under_600_lines(name):
    path = Path(run_log.__file__).with_name(name)
    assert len(path.read_text(encoding="utf-8").splitlines()) < SCRIPT_MAX_LINES


@pytest.mark.parametrize("name", ["test_run_log.py", "test_run_log_exclude.py", "run_log_helpers.py"])
def test_test_file_stays_under_the_line_limit(name):
    assert len(Path(__file__).with_name(name).read_text(encoding="utf-8").splitlines()) <= TEST_MAX_LINES
