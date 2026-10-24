"""phase_usage.py testleri: sentetik Claude Code transcript'leri ile faz bazli token olcumu."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

import phase_usage

HEADER = [
    "phase", "calls", "input_tokens", "cache_creation", "cache_read", "output_tokens",
    "thinking_tokens", "total_input", "uncached_input", "duration_s",
]


def line(ts: str, msg_id: str | None, inp=1, cc=10, cr=100, out=5, think=2, **extra) -> str:
    message = {"role": "assistant", "usage": {
        "input_tokens": inp, "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr,
        "output_tokens": out, "output_tokens_details": {"thinking_tokens": think}}}
    if msg_id:
        message["id"] = msg_id
    return json.dumps({"type": "assistant", "timestamp": ts, "message": message, **extra})


def write_lines(path: Path, lines: list[str]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_log(path: Path, entries: list[tuple[str, str, str]]) -> Path:
    rows = [json.dumps({"phase": p, "event": e, "ts": t}) for p, e, t in entries]
    return write_lines(path, rows)


def run(argv: list[str], capsys) -> tuple[int, str, str]:
    code = phase_usage.main(argv)
    out = capsys.readouterr()
    return code, out.out, out.err


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.fixture()
def session(tmp_path):
    main = write_lines(tmp_path / "s" / "sess.jsonl", [
        line("2026-01-01T10:00:00.000Z", "m1", inp=1, cc=10, cr=100, out=5, think=2),
        line("2026-01-01T10:00:01.000Z", "m1", inp=1, cc=10, cr=100, out=5, think=2),  # dup
        line("2026-01-01T10:05:00.000Z", "m2", inp=2, cc=20, cr=200, out=7, think=0),
        line("2026-01-01T10:10:00.000Z", "m3", inp=3, cc=30, cr=300, out=9, think=4),  # boundary
        line("2026-01-01T10:20:00.000Z", "m4", inp=4, cc=40, cr=400, out=11, think=1),
    ])
    sub = tmp_path / "s" / "sess" / "subagents"
    write_lines(sub / "agent-aaa.jsonl", [
        line("2026-01-01T10:06:00.000Z", "s1", inp=5, cc=50, cr=500, out=13, think=3, isSidechain=True),
        line("2026-01-01T10:06:00.500Z", "s1", inp=5, cc=50, cr=500, out=13, think=3, isSidechain=True),
    ])
    (sub / "agent-aaa.meta.json").write_text("{}", encoding="utf-8")
    log = write_log(tmp_path / "phases.jsonl", [
        ("research", "start", "2026-01-01T10:00:00Z"),
        ("research", "end", "2026-01-01T10:10:00Z"),
        ("build", "start", "2026-01-01T10:10:00Z"),
        ("build", "end", "2026-01-01T10:15:00Z"),
    ])
    return main, sub, log


# ---------- mark ----------

def test_mark_appends_and_creates_log(tmp_path, capsys):
    log = tmp_path / "deep" / "phases.jsonl"
    code, out, _ = run(["mark", "p1", "start", "--log", str(log), "--ts", "2026-01-01T10:00:00Z"], capsys)
    assert code == 0 and json.loads(out)["event"] == "start"
    code, _, _ = run(["mark", "p1", "end", "--log", str(log), "--ts", "2026-01-01T10:01:00Z"], capsys)
    assert code == 0
    rows = [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()]
    assert [(r["phase"], r["event"]) for r in rows] == [("p1", "start"), ("p1", "end")]
    assert rows[0]["ts"].startswith("2026-01-01T10:00:00")


def test_mark_default_ts_is_utc_now(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    assert run(["mark", "p1", "start", "--log", str(log)], capsys)[0] == 0
    ts = json.loads(log.read_text(encoding="utf-8").splitlines()[0])["ts"]
    assert phase_usage.parse_ts(ts).utcoffset().total_seconds() == 0


def test_mark_end_without_start_rejected(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    code, out, err = run(["mark", "p1", "end", "--log", str(log)], capsys)
    assert code == 2 and "p1" in err and out == ""
    assert not log.exists() or log.read_text(encoding="utf-8") == ""


def test_mark_reopen_open_phase_rejected(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    run(["mark", "p1", "start", "--log", str(log), "--ts", "2026-01-01T10:00:00Z"], capsys)
    code, _, err = run(["mark", "p1", "start", "--log", str(log), "--ts", "2026-01-01T10:01:00Z"], capsys)
    assert code == 2 and "open" in err
    assert len(log.read_text(encoding="utf-8").splitlines()) == 1


def test_mark_reopen_after_close_allowed(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    for event, ts in (("start", "10:00"), ("end", "10:01"), ("start", "10:02")):
        assert run(["mark", "p1", event, "--log", str(log), "--ts", f"2026-01-01T{ts}:00Z"], capsys)[0] == 0


def test_mark_invalid_event_and_ts(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    with pytest.raises(SystemExit) as exc:
        phase_usage.main(["mark", "p1", "pause", "--log", str(log)])
    assert exc.value.code == 2
    capsys.readouterr()
    code, _, err = run(["mark", "p1", "start", "--log", str(log), "--ts", "not-a-date"], capsys)
    assert code == 2 and "ts" in err


def test_mark_end_before_start_rejected(tmp_path, capsys):
    log = tmp_path / "p.jsonl"
    run(["mark", "p1", "start", "--log", str(log), "--ts", "2026-01-01T10:05:00Z"], capsys)
    code, _, _ = run(["mark", "p1", "end", "--log", str(log), "--ts", "2026-01-01T10:00:00Z"], capsys)
    assert code == 2


def test_mark_empty_phase_rejected(tmp_path, capsys):
    assert run(["mark", "  ", "start", "--log", str(tmp_path / "p.jsonl")], capsys)[0] == 2


# ---------- report ----------

def report(session, tmp_path, capsys, *extra):
    main, sub, log = session
    out_csv = tmp_path / "out.csv"
    code, out, err = run(["report", "--session", str(main), "--subagents", str(sub),
                          "--log", str(log), "--out", str(out_csv), *extra], capsys)
    return code, out, err, out_csv


def test_report_windows_boundaries_and_dedupe(session, tmp_path, capsys):
    code, out, _, csv_path = report(session, tmp_path, capsys)
    assert code == 0
    rows = {r["phase"]: r for r in read_csv(csv_path)}
    # research [10:00, 10:10): m1 (dedupe), m2, s1 ; build [10:10,10:15): m3 (inclusive start)
    assert rows["research"]["calls"] == "3"
    assert rows["research"]["input_tokens"] == str(1 + 2 + 5)
    assert rows["research"]["cache_creation"] == str(10 + 20 + 50)
    assert rows["research"]["cache_read"] == str(100 + 200 + 500)
    assert rows["research"]["output_tokens"] == str(5 + 7 + 13)
    assert rows["research"]["thinking_tokens"] == str(2 + 0 + 3)
    assert rows["research"]["total_input"] == str(8 + 80 + 800)
    assert rows["research"]["uncached_input"] == str(8 + 80)
    assert rows["research"]["duration_s"] in ("600", "600.0")
    assert rows["build"]["calls"] == "1" and rows["build"]["input_tokens"] == "3"
    assert rows["(outside phases)"]["calls"] == "1"  # m4 at 10:20
    assert rows["(outside phases)"]["input_tokens"] == "4"


def test_report_csv_header_and_row_order(session, tmp_path, capsys):
    _, _, _, csv_path = report(session, tmp_path, capsys)
    assert csv_path.read_text(encoding="utf-8").splitlines()[0].split(",") == HEADER
    assert [r["phase"] for r in read_csv(csv_path)] == ["research", "build", "(outside phases)", "TOTAL"]


def test_report_rows_sum_to_total_and_independent_sum(session, tmp_path, capsys):
    _, out, _, csv_path = report(session, tmp_path, capsys)
    rows = read_csv(csv_path)
    total = rows[-1]
    body = rows[:-1]
    for col in HEADER[1:-1]:
        assert sum(int(r[col]) for r in body) == int(total[col]), col
    # bagimsiz toplam: tum dosyalar, message.id ile tekilleştirilmis
    seen, expect = set(), {"in": 0, "out": 0, "cc": 0, "cr": 0}
    main, sub, _ = session
    for f in [main, *sub.glob("agent-*.jsonl")]:
        for raw in f.read_text(encoding="utf-8").splitlines():
            o = json.loads(raw)
            if o["message"]["id"] in seen:
                continue
            seen.add(o["message"]["id"])
            u = o["message"]["usage"]
            expect["in"] += u["input_tokens"]
            expect["cc"] += u["cache_creation_input_tokens"]
            expect["cr"] += u["cache_read_input_tokens"]
            expect["out"] += u["output_tokens"]
    assert int(total["calls"]) == len(seen) == 5
    assert int(total["input_tokens"]) == expect["in"]
    assert int(total["output_tokens"]) == expect["out"]
    assert int(total["total_input"]) == expect["in"] + expect["cc"] + expect["cr"]
    summary = json.loads(out)
    assert summary["phases"] == 2
    assert summary["total_input"] == int(total["total_input"])
    assert summary["uncached_input"] == int(total["uncached_input"])
    assert summary["output"] == expect["out"]
    outside = int(rows[2]["total_input"])
    assert summary["unattributed_pct"] == pytest.approx(100 * outside / int(total["total_input"]), abs=0.05)


def test_report_subagent_dir_included_and_autodetected(session, tmp_path, capsys):
    main, sub, log = session
    code, out, _ = run(["report", "--session", str(main), "--log", str(log)], capsys)  # autodetect
    assert code == 0
    with_sub = json.loads(out)["total_input"]
    code, out, _ = run(["report", "--session", str(main), "--log", str(log),
                        "--subagents", str(tmp_path / "nope")], capsys)
    assert code == 0 and json.loads(out)["total_input"] < with_sub


def test_report_counts_nested_workflow_agents(session, capsys):
    """Workflow ajanlari subagents/workflows/wf_*/agent-*.jsonl altinda; bunlar da sayilmali (pilotta atlaniyordu)."""
    main, sub, log = session
    code, out, _ = run(["report", "--session", str(main), "--log", str(log)], capsys)
    before = json.loads(out)
    write_lines(sub / "workflows" / "wf_abc" / "agent-bbb.jsonl", [
        line("2026-01-01T10:07:00.000Z", "w1", inp=6, cc=60, cr=600, out=17, think=0, isSidechain=True),
    ])
    write_lines(sub / "workflows" / "wf_abc" / "journal.jsonl", ['{"type":"launched"}'])
    code, out, _ = run(["report", "--session", str(main), "--log", str(log)], capsys)
    after = json.loads(out)
    assert code == 0
    assert after["calls"] == before["calls"] + 1
    assert after["total_input"] == before["total_input"] + 6 + 60 + 600
    assert after["output"] == before["output"] + 17


def test_report_fallback_dedupe_keys(tmp_path, capsys):
    a = json.loads(line("2026-01-01T10:00:00Z", None))
    a["requestId"] = "req_1"
    a_dup = dict(a)
    b = json.loads(line("2026-01-01T10:00:02Z", None))      # no id, no requestId
    b_dup = dict(b)
    sess = write_lines(tmp_path / "x.jsonl", [json.dumps(o) for o in (a, a_dup, b, b_dup)])
    log = write_log(tmp_path / "p.jsonl", [("p", "start", "2026-01-01T09:00:00Z"), ("p", "end", "2026-01-01T11:00:00Z")])
    code, out, _ = run(["report", "--session", str(sess), "--log", str(log), "--out", str(tmp_path / "o.csv")], capsys)
    assert code == 0
    assert read_csv(tmp_path / "o.csv")[-1]["calls"] == "2"


def test_report_malformed_lines_skipped_and_counted(tmp_path, capsys):
    sess = write_lines(tmp_path / "x.jsonl", [
        "{not json", line("2026-01-01T10:00:00Z", "m1"), "", '{"type":"user"}', '[1,2]',
        json.dumps({"type": "assistant", "timestamp": "2026-01-01T10:00:00Z", "message": {"id": "z", "usage": "bad"}}),
    ])
    log = write_log(tmp_path / "p.jsonl", [("p", "start", "2026-01-01T09:00:00Z"), ("p", "end", "2026-01-01T11:00:00Z")])
    code, out, _ = run(["report", "--session", str(sess), "--log", str(log)], capsys)
    summary = json.loads(out)
    assert code == 0 and summary["malformed"] >= 2
    assert summary["total_input"] == 111


def test_report_overlapping_windows_rejected(session, tmp_path, capsys):
    main, sub, _ = session
    log = write_log(tmp_path / "ov.jsonl", [
        ("a", "start", "2026-01-01T10:00:00Z"), ("b", "start", "2026-01-01T10:05:00Z"),
        ("a", "end", "2026-01-01T10:08:00Z"), ("b", "end", "2026-01-01T10:09:00Z"),
    ])
    code, out, err = run(["report", "--session", str(main), "--log", str(log)], capsys)
    assert code == 2 and "overlap" in err and out == ""


def test_report_same_phase_multiple_windows_merged(session, tmp_path, capsys):
    main, _, _ = session
    log = write_log(tmp_path / "m.jsonl", [
        ("p", "start", "2026-01-01T10:00:00Z"), ("p", "end", "2026-01-01T10:01:00Z"),
        ("p", "start", "2026-01-01T10:10:00Z"), ("p", "end", "2026-01-01T10:12:00Z"),
    ])
    out_csv = tmp_path / "o.csv"
    assert run(["report", "--session", str(main), "--log", str(log), "--out", str(out_csv)], capsys)[0] == 0
    rows = read_csv(out_csv)
    assert [r["phase"] for r in rows] == ["p", "(outside phases)", "TOTAL"]
    assert rows[0]["calls"] == "2" and float(rows[0]["duration_s"]) == 180.0  # m1 + m3; m2 outside


def test_report_open_phase_extends_to_end_of_data(session, tmp_path, capsys):
    main, _, _ = session
    log = write_log(tmp_path / "o.jsonl", [("p", "start", "2026-01-01T10:10:00Z")])
    out_csv = tmp_path / "o.csv"
    code, out, _ = run(["report", "--session", str(main), "--log", str(log), "--out", str(out_csv)], capsys)
    assert code == 0 and json.loads(out)["open_phases"] == 1
    rows = {r["phase"]: r for r in read_csv(out_csv)}
    assert rows["p"]["calls"] == "2" and float(rows["p"]["duration_s"]) == 600.0


def test_report_table_output(session, tmp_path, capsys):
    code, out, _, _ = report(session, tmp_path, capsys, "--table")
    lines = out.splitlines()
    assert code == 0 and lines[0].startswith("phase") and any(x.startswith("research") for x in lines)
    assert any(x.startswith("TOTAL") for x in lines)
    assert json.loads(lines[-1])["phases"] == 2


def test_report_json_is_single_line(session, tmp_path, capsys):
    _, out, _, _ = report(session, tmp_path, capsys)
    assert len(out.strip().splitlines()) == 1


def test_report_usage_errors(session, tmp_path, capsys):
    main, _, log = session
    code, _, err = run(["report", "--session", str(tmp_path / "missing.jsonl"), "--log", str(log)], capsys)
    assert code == 2 and "missing" in err
    code, _, _ = run(["report", "--session", str(main), "--log", str(tmp_path / "nolog.jsonl")], capsys)
    assert code == 2
    bad = write_lines(tmp_path / "bad.jsonl", ['{"phase":"p","event":"start","ts":"garbage"}'])
    assert run(["report", "--session", str(main), "--log", str(bad)], capsys)[0] == 2
    dangling = write_log(tmp_path / "d.jsonl", [("p", "end", "2026-01-01T10:00:00Z")])
    assert run(["report", "--session", str(main), "--log", str(dangling)], capsys)[0] == 2


def test_report_empty_usage_no_division_error(tmp_path, capsys):
    sess = write_lines(tmp_path / "x.jsonl", ['{"type":"user"}'])
    log = write_log(tmp_path / "p.jsonl", [("p", "start", "2026-01-01T09:00:00Z"), ("p", "end", "2026-01-01T11:00:00Z")])
    code, out, _ = run(["report", "--session", str(sess), "--log", str(log)], capsys)
    assert code == 0 and json.loads(out)["unattributed_pct"] == 0


def test_streaming_duplicate_keeps_max_output(tmp_path, capsys):
    sess = write_lines(tmp_path / "x.jsonl", [
        line("2026-01-01T10:00:00Z", "m1", out=3), line("2026-01-01T10:00:01Z", "m1", out=40)])
    log = write_log(tmp_path / "p.jsonl", [("p", "start", "2026-01-01T09:00:00Z"), ("p", "end", "2026-01-01T11:00:00Z")])
    code, out, _ = run(["report", "--session", str(sess), "--log", str(log)], capsys)
    assert json.loads(out)["output"] == 40


def test_parse_ts_variants():
    z = phase_usage.parse_ts("2026-01-01T10:00:00.123Z")
    off = phase_usage.parse_ts("2026-01-01T12:00:00.123+02:00")
    naive = phase_usage.parse_ts("2026-01-01T10:00:00.123")
    assert z == off == naive
    with pytest.raises(ValueError):
        phase_usage.parse_ts("")
