"""build_xlsx.py: JSONL -> sablon kopyasi (anahtara gore yazim, reddetme kurallari, guvenlik, butunluk)."""
import datetime as dt
import json
from pathlib import Path

import openpyxl
import pytest

import build_xlsx
import common
import helpers


def write_jsonl(data_dir: Path, sheet: str, records: list, raw_lines: list[str] | None = None) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    path = data_dir / f"{sheet}.jsonl"
    lines = [json.dumps(r, ensure_ascii=False) for r in records] + list(raw_lines or [])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run(capsys, template: Path, data_dir: Path, out: Path, *extra: str) -> tuple[int, dict, dict]:
    report = out.parent / (out.stem + "_report.json")
    code = build_xlsx.main(["--template", str(template), "--data-dir", str(data_dir), "--out", str(out),
                            "--report", str(report), *extra])
    summary = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    payload = json.loads(report.read_text(encoding="utf-8")) if report.exists() else {}
    return code, summary, payload


def cell(path: Path, sheet: str, row: int, key: str):
    wb = openpyxl.load_workbook(path)
    ws = wb[sheet]
    return ws.cell(row, common.sheet_keys(ws)[key]).value


def answer(i: int = 1, **extra) -> dict:
    base = {"entry_id": f"testville:soru-{i}", "city_id": "testville", "slug": f"soru-{i}", "title": f"Soru {i}",
            "summary": "Kisa yanit", "source_ids": "testville:kaynak:a", "reviewed_on": "2026-10-20", "order": i,
            "featured": "Hayır", "editorial_status": "Taslak", "topic_id": "testville:konu:a"}
    return {**base, **extra}


def reasons(report: dict) -> str:
    return " | ".join(f"{r.get('key')}:{r['reason']}" for r in report["rejected"])


def test_happy_path_writes_by_key_in_any_order(tmp_path, capsys, template):
    rec = answer(1, featured=True, order="3", visual_json={"tip": "adım", "n": [1, 2]})
    shuffled = dict(reversed(list(rec.items())))
    shuffled["_row"] = 99
    write_jsonl(tmp_path / "d", "Yanıtlar", [shuffled, answer(2)])
    out = tmp_path / "out.xlsx"
    code, summary, report = run(capsys, template, tmp_path / "d", out)
    assert code == common.EXIT_OK, report
    assert summary["rows_written"] == {"Yanıtlar": 2} and summary["rejected"] == 0 and summary["fidelity"] == "ok"
    assert summary["out"] == str(out.resolve())
    assert cell(out, "Yanıtlar", 8, "entry_id") == "testville:soru-1"
    assert cell(out, "Yanıtlar", 8, "featured") == "Evet"
    assert cell(out, "Yanıtlar", 8, "order") == 3
    assert cell(out, "Yanıtlar", 8, "reviewed_on").date() == dt.date(2026, 10, 20)
    assert json.loads(cell(out, "Yanıtlar", 8, "visual_json")) == {"tip": "adım", "n": [1, 2]}
    assert cell(out, "Yanıtlar", 8, "visual_json") == '{"tip":"adım","n":[1,2]}'
    assert cell(out, "Yanıtlar", 9, "entry_id") == "testville:soru-2"
    assert cell(out, "Konular", 8, "used_count").startswith("=")  # formuller korunur


def test_ascii_file_name_accepted(tmp_path, capsys, template):
    (tmp_path / "d").mkdir()
    (tmp_path / "d" / "Yanitlar.jsonl").write_text(json.dumps(answer(1)) + "\n", encoding="utf-8")
    code, summary, _ = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 0 and summary["rows_written"] == {"Yanıtlar": 1}


def test_ambiguous_and_unknown_files_are_usage_errors(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    (tmp_path / "d" / "Yanitlar.jsonl").write_text(json.dumps(answer(1)) + "\n", encoding="utf-8")
    code, summary, _ = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == common.EXIT_USAGE and "Yanitlar" in summary["error"]
    write_jsonl(tmp_path / "e", "Yanitlr", [answer(1)])
    code, summary, _ = run(capsys, template, tmp_path / "e", tmp_path / "out.xlsx")
    assert code == common.EXIT_USAGE and "Yanitlr" in summary["error"]


def test_merge_mode_updates_only_given_keys(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Şehir", [{"city_id": "testville", "intro": "Merhaba", "latitude": "51.4", "_row": 8}])
    write_jsonl(tmp_path / "d", "Teslimat", [{"delivery_id": "CITY-999-v001", "updated_on": "2026-10-21", "editor": "AI"}])
    out = tmp_path / "out.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 0 and summary["rows_written"] == {"Şehir": 1, "Teslimat": 1}
    assert cell(out, "Şehir", 8, "intro") == "Merhaba"
    assert cell(out, "Şehir", 8, "name") == "Testville" and cell(out, "Şehir", 8, "longitude") == 5.5
    assert cell(out, "Teslimat", 8, "editor") == "AI" and cell(out, "Teslimat", 8, "schema_version") == "1.0"
    assert cell(out, "Teslimat", 8, "updated_on").date() == dt.date(2026, 10, 21)
    assert cell(out, "Şehir", 9, "city_id") is None


def test_merge_identity_change_rejected(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Şehir", [{"city_id": "testville", "name": "Başka", "intro": "x"}])
    out = tmp_path / "out.xlsx"
    code, summary, report = run(capsys, template, tmp_path / "d", out)
    assert code == common.EXIT_FINDINGS and summary["rejected"] == 1 and not out.exists()
    assert "name:" in reasons(report) and "identity" in reasons(report)


def test_merge_second_record_exceeds_capacity(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Teslimat", [{"editor": "a"}, {"editor": "b"}])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 1 and summary["rejected"] == 1 and "capacity" in reasons(report)


@pytest.mark.parametrize("sheet,record,needle", [
    ("Konular", {"topic_id": "t:k", "used_count": 3}, "formula"),
    ("Yanıtlar", answer(1, titel="typo"), "unknown key"),
    ("Yanıtlar", answer(1, editorial_status="Yayında"), "not in list"),
    ("Yanıtlar", answer(1, title="=HYPERLINK(\"http://x\")"), "formula injection"),
    ("Yanıtlar", answer(1, summary="x" * (common.MAX_CELL_CHARS + 1)), "too long"),
    ("Yanıtlar", answer(1, visual_json="{bozuk json"), "json"),
    ("Yanıtlar", answer(1, reviewed_on="20.10.2026"), "date"),
    ("Yanıtlar", answer(1, order="üç"), "number"),
    ("Yanıtlar", answer(1, order=True), "number"),
    ("Yanıtlar", answer(1, title="kontrol\x07karakteri"), "control"),
])
def test_rejected_rows(tmp_path, capsys, template, sheet, record, needle):
    write_jsonl(tmp_path / "d", sheet, [record])
    out = tmp_path / "out.xlsx"
    code, summary, report = run(capsys, template, tmp_path / "d", out)
    assert code == common.EXIT_FINDINGS and summary["rejected"] == 1, report
    assert needle in reasons(report).lower()
    assert report["rejected"][0]["sheet"] == sheet and report["rejected"][0]["line"] == 1
    assert not out.exists()


def test_long_text_is_not_truncated_when_within_limit(tmp_path, capsys, template):
    text = "y" * common.MAX_CELL_CHARS
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1, summary=text)])
    out = tmp_path / "out.xlsx"
    code, _, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 0 and cell(out, "Yanıtlar", 8, "summary") == text


def test_bad_json_line_and_non_object_rejected(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)], raw_lines=["{bozuk", "[1,2]", ""])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 1 and summary["rejected"] == 2
    assert [r["line"] for r in report["rejected"]] == [2, 3]


def test_ozet_is_never_written(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Özet", [{"A1": "x"}])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 1 and "not writable" in reasons(report)


def test_duplicate_ids_deduped_and_counted(tmp_path, capsys, template):
    rec = answer(1, source_ids="testville:kaynak:a;testville:kaynak:b;testville:kaynak:a; testville:kaynak:b")
    rec2 = answer(2, source_ids=["testville:kaynak:c", "testville:kaynak:c"])
    write_jsonl(tmp_path / "d", "Yanıtlar", [rec, rec2, answer(3, source_ids="testville:kaynak:a; testville:kaynak:b")])
    out = tmp_path / "out.xlsx"
    code, summary, report = run(capsys, template, tmp_path / "d", out)
    assert code == 0 and summary["deduped"] == 3
    assert cell(out, "Yanıtlar", 8, "source_ids") == "testville:kaynak:a;testville:kaynak:b"
    assert cell(out, "Yanıtlar", 9, "source_ids") == "testville:kaynak:c"
    assert cell(out, "Yanıtlar", 10, "source_ids") == "testville:kaynak:a; testville:kaynak:b"  # tekrar yoksa dokunulmaz
    assert {d["row"] for d in report["deduped"]} == {8, 9}


def evidence(i: int = 1, **extra) -> dict:
    return {"evidence_id": f"testville:kanit:{i}", "city_id": "testville", "photo_id": f"testville:foto:{i}",
            "checked_on": "2026-10-20", **extra}


def test_human_fields_default_to_pending(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Kanıtlar", [evidence(1), evidence(2, rights_status="Bekliyor")])
    out = tmp_path / "out.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 0 and summary["defaults_applied"] == 5
    for row in (8, 9):
        for key in common.HUMAN_REVIEW_KEYS:
            assert cell(out, "Kanıtlar", row, key) == common.HUMAN_PENDING_VALUE


def test_self_approval_rejected_unless_flag(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Kanıtlar", [evidence(1, metadata_review_status="Doğrulandı")])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 1 and "human" in reasons(report)
    out = tmp_path / "out2.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out, "--allow-human-values")
    assert code == 0 and cell(out, "Kanıtlar", 8, "metadata_review_status") == "Doğrulandı"
    write_jsonl(tmp_path / "e", "Kanıtlar", [evidence(1, metadata_review_status="Tamam")])
    code, summary, report = run(capsys, template, tmp_path / "e", tmp_path / "out3.xlsx", "--allow-human-values")
    assert code == 1 and "not in list" in reasons(report)


def test_capacity_overflow_rejected(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(i) for i in range(1, helpers.CAPACITY + 2)])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 1 and summary["rejected"] == 1
    assert "capacity" in reasons(report) and report["rejected"][0]["line"] == helpers.CAPACITY + 1


def test_all_or_nothing_and_partial(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1), answer(2, featured="Belki"), answer(3)])
    out = tmp_path / "out.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 1 and not out.exists() and summary["out"] is None and summary["rows_written"] == {}
    code, summary, _ = run(capsys, template, tmp_path / "d", out, "--partial")
    assert code == 1 and out.exists() and summary["rows_written"] == {"Yanıtlar": 2}
    assert cell(out, "Yanıtlar", 9, "entry_id") == "testville:soru-3"


def test_out_equal_to_template_refused(tmp_path, capsys, template):
    before = common.sha256_file(template)
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    code, summary, _ = run(capsys, template, tmp_path / "d", template, "--overwrite")
    assert code == common.EXIT_USAGE and "template" in summary["error"]
    assert common.sha256_file(template) == before


def test_existing_out_needs_overwrite(tmp_path, capsys, template):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    out = tmp_path / "out.xlsx"
    out.write_bytes(b"eski")
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == common.EXIT_USAGE and out.read_bytes() == b"eski"
    code, summary, _ = run(capsys, template, tmp_path / "d", out, "--overwrite")
    assert code == 0 and cell(out, "Yanıtlar", 8, "entry_id") == "testville:soru-1"


def test_template_bytes_unchanged(tmp_path, capsys, template):
    before = common.sha256_file(template)
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    write_jsonl(tmp_path / "d", "Şehir", [{"intro": "x"}])
    code, _, _ = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 0 and common.sha256_file(template) == before


def test_missing_inputs_are_usage_errors(tmp_path, capsys, template):
    code, summary, _ = run(capsys, template, tmp_path / "yok", tmp_path / "out.xlsx")
    assert code == 2 and "data-dir" in summary["error"]
    (tmp_path / "d").mkdir()
    code, summary, _ = run(capsys, tmp_path / "yok.xlsx", tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 2 and "template" in summary["error"]


def test_non_empty_template_sheet_is_structure_error(tmp_path, capsys, package):
    write_jsonl(tmp_path / "d", "Fotoğraflar", [{"photo_id": "testville:foto:x"}])
    code, summary, _ = run(capsys, package["xlsx"], tmp_path / "d", tmp_path / "out.xlsx")
    assert code == 2 and "Fotoğraflar" in summary["error"]


def test_empty_data_dir_copies_template(tmp_path, capsys, template):
    (tmp_path / "d").mkdir()
    out = tmp_path / "out.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 0 and summary["rows_written"] == {} and summary["fidelity"] == "ok" and out.exists()


def make_tools(root: Path) -> Path:
    target = root / "core" / "content_delivery"
    target.mkdir(parents=True)
    (target / "schema_definition.py").write_text(
        "TABLES = {'answers': {'sheet': 'Yanıtlar', 'fields': [\n"
        "  {'key': 'slug', 'type': 'id_list'}, {'key': 'order', 'type': 'integer'},\n"
        "  {'key': 'summary', 'type': 'text_list'}, {'key': 'title', 'type': 'date'}]}}\n", encoding="utf-8")
    return root


def test_tools_schema_supplies_list_fields(tmp_path, capsys, template):
    tools = make_tools(tmp_path / "arac")
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1, slug="a;b;a", summary=["x", "y"], title="2026-01-02")])
    out = tmp_path / "out.xlsx"
    code, summary, report = run(capsys, template, tmp_path / "d", out, "--tools", str(tools))
    assert code == 0, report["rejected"]
    assert cell(out, "Yanıtlar", 8, "slug") == "a;b" and summary["deduped"] == 1
    assert cell(out, "Yanıtlar", 8, "summary") == "x\ny"
    assert report["schema_source"].endswith("schema_definition.py")


def test_tools_without_schema_is_usage_error(tmp_path, capsys, template):
    (tmp_path / "d").mkdir()
    code, summary, _ = run(capsys, template, tmp_path / "d", tmp_path / "out.xlsx", "--tools", str(tmp_path))
    assert code == 2 and "schema_definition" in summary["error"]


def test_fidelity_failure_blocks_output(tmp_path, capsys, template, monkeypatch):
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    monkeypatch.setattr(build_xlsx.xlsx_fidelity, "check", lambda a, b, accept=False: (["Yanıtlar: freeze panes differ"], []))
    out = tmp_path / "out.xlsx"
    code, summary, _ = run(capsys, template, tmp_path / "d", out)
    assert code == 2 and summary["fidelity"] == ["Yanıtlar: freeze panes differ"] and not out.exists()
    assert not list(tmp_path.glob("*.tmp*"))


def test_openpyxl_parts_accepted_by_default_strict_on_request(tmp_path, capsys, template, monkeypatch):
    seen = []

    def fake_check(a, b, accept=False):
        seen.append(accept)
        return [], (["zip part added by openpyxl: docProps/app.xml"] if accept else [])

    monkeypatch.setattr(build_xlsx.xlsx_fidelity, "check", fake_check)
    write_jsonl(tmp_path / "d", "Yanıtlar", [answer(1)])
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "a.xlsx")
    assert code == 0 and seen == [True]
    assert summary["fidelity_accepted"] == ["zip part added by openpyxl: docProps/app.xml"]  # kabul edilen parca raporlanir
    code, summary, report = run(capsys, template, tmp_path / "d", tmp_path / "b.xlsx", "--strict-parts")
    assert code == 0 and seen == [True, False] and summary["fidelity_accepted"] == []
