"""editorial_score.py testleri: kontrol listesi bolum 20 (editoryal yuzde ve karar), K100/K101/K115-K117."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

import editorial_score as es

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "editorial_score.py"
FIXED = {"A1": 240, "B1": 120, "B2": 16, "B3": 12, "B4": 60, "C1": 250, "E3": 23, "E5": 5}
CODES = [f"{c}{i}" for c in "ABCDE" for i in range(1, 6)]
FULL_COVERAGE = {"cards": [240, 240], "photos": [250, 250], "critical_claims": [40, 40]}
READY = "ATINÇ’IN SON PAKET İNCELEMESİNE HAZIR"
FIX = "DÜZELTME GEREKLİ"
EVIDENCE = "KARAR İÇİN KANIT EKSİK"


def crit(code: str, passed: int | None = None, required: int | None = None, status: str = "ok", reason: str = "") -> dict:
    req = FIXED.get(code, 10) if required is None else required
    return {"code": code, "passed": req if passed is None else passed, "required": req, "status": status, "reason": reason}


def full_criteria(**overrides: dict) -> list[dict]:
    return [overrides.get(code, crit(code)) for code in CODES]


def payload(criteria=None, findings=None, coverage=FULL_COVERAGE, **extra) -> dict:
    data = {"criteria": full_criteria() if criteria is None else criteria, "findings": findings or []}
    if coverage is not None:
        data["coverage"] = coverage
    return {**data, **extra}


def run(tmp_path: Path, data, capsys, *extra: str, raw: str | None = None) -> tuple[int, dict, dict | None]:
    src = tmp_path / "criteria.json"
    src.write_text(raw if raw is not None else json.dumps(data, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "out" / "score.json"
    code = es.main(["--input", str(src), "--out", str(out), *extra])
    lines = capsys.readouterr().out.strip().splitlines()
    summary = json.loads(lines[-1]) if lines else {}
    report = json.loads(out.read_text(encoding="utf-8")) if out.exists() else None
    return code, summary, report


def pdf_example_rows() -> list[dict]:
    """A=28/35 (her A olcutu 0.8; A1 192/240), B=16/20, C=12/20, D=9/15, E=6/10."""
    over = {f"A{i}": crit(f"A{i}", passed=4, required=5) for i in range(2, 6)}
    over["A1"] = crit("A1", passed=192)
    for code in ("B5", "C4", "C5", "D4", "D5", "E4", "E5"):
        over[code] = crit(code, passed=0)
    return full_criteria(**over)


# --- Kabul (1): PDF hayali ornegi ---

def test_pdf_example_category_mode_with_p0_needs_fix(tmp_path, capsys):
    data = {"categories": {"A": 28, "B": 16, "C": 12, "D": 9, "E": 6},
            "findings": [{"id": "ISS-1", "priority": "P0"}], "coverage": FULL_COVERAGE}
    code, summary, report = run(tmp_path, data, capsys)
    assert code == 1
    assert report["editorial_percent"] == 71
    assert report["decision"] == FIX
    assert summary["percent"] == 71 and summary["decision"] == FIX
    assert report["cover_line"].startswith("Editoryal hazır olma: %71 (kategori toplamı modu) | İnceleme kapsamı: kart 240/240;")


def test_pdf_example_criteria_mode_gives_71(tmp_path, capsys):
    data = payload(pdf_example_rows(), findings=[{"id": "KAPAK-1", "priority": "P0"}])
    code, _, report = run(tmp_path, data, capsys)
    assert code == 1
    cats = {c["code"]: c["score"] for c in report["categories"]}
    assert cats == {"A": 28, "B": 16, "C": 12, "D": 9, "E": 6}
    assert report["raw_total"] == 71 and report["editorial_percent"] == 71
    assert report["decision"] == FIX
    assert "KAPAK-1" in report["decision_reason"]


# --- Kabul (2): Codex Eindhoven kategori katkilari ---

def test_codex_eindhoven_category_totals_give_55(tmp_path, capsys):
    data = {"categories": {"A": 18, "B": 11, "C": 14, "D": 9, "E": 3}, "findings": []}
    code, summary, report = run(tmp_path, data, capsys)
    assert report["mode"] == "categories"
    assert report["editorial_percent"] == 55 and report["raw_total"] == 55
    assert report["decision"] == EVIDENCE  # alt olcut kaniti yok: hazir denemez
    assert report["decision_note"] == "önizleme ve Drive kontrolleri ayrı aşamada"
    assert code == 1 and summary["percent"] == 55


# --- Kabul (3): sinir durumlari ---

def test_ratio_above_one_is_clipped(tmp_path, capsys):
    rows = full_criteria(A1=crit("A1", passed=300), A2=crit("A2", passed=12, required=10))
    _, _, report = run(tmp_path, payload(rows), capsys)
    by = {r["code"]: r for r in report["criteria"]}
    assert by["A1"]["ratio"] == 1 and by["A1"]["subscore"] == 7
    assert by["A2"]["ratio"] == 1 and by["A2"]["subscore"] == 7
    assert "kırpıldı" in by["A2"]["note"]
    assert report["editorial_percent"] == 100


def test_zero_denominator_scores_zero_and_blocks_ready(tmp_path, capsys):
    rows = full_criteria(B5=crit("B5", passed=0, required=0))
    code, _, report = run(tmp_path, payload(rows), capsys)
    by = {r["code"]: r for r in report["criteria"]}
    assert by["B5"]["ratio"] == 0 and by["B5"]["subscore"] == 0
    assert report["editorial_percent"] == 96
    assert report["decision"] == EVIDENCE
    assert any("B5" in gap and "payda 0" in gap for gap in report["evidence_gaps"])
    assert code == 1


def test_whole_category_not_applicable_keeps_weight_and_is_not_final(tmp_path, capsys):
    na = {f"E{i}": crit(f"E{i}", status="not_applicable", reason="şehirde web işlevi yok") for i in range(1, 6)}
    code, _, report = run(tmp_path, payload(full_criteria(**na)), capsys)
    assert report["raw_total"] == 90 and report["editorial_percent"] == 90
    assert report["max_possible"] == 90
    assert "nihai değil" in report["labels"]
    cats = {c["code"]: c for c in report["categories"]}
    assert cats["A"]["weight"] == 35 and cats["E"]["weight"] == 10  # agirlik aktarilmaz
    assert "nihai değil" in report["cover_line"]
    assert report["decision"] == EVIDENCE and code == 1  # butun olcut uygulanmaz: Atinc payda karari bekler
    assert any(gap.startswith("E1:") and "Atınç" in gap for gap in report["evidence_gaps"])


def test_raw_70_9_floors_to_70_in_criteria_mode(tmp_path, capsys):
    over = {f"E{i}": crit(f"E{i}", status="not_checked") for i in range(1, 6)}
    over.update({f"D{i}": crit(f"D{i}", passed=0) for i in range(1, 6)})
    over["C2"] = crit("C2", passed=0)
    over["B1"] = crit("B1", passed=117)
    _, _, report = run(tmp_path, payload(full_criteria(**over)), capsys)
    assert report["raw_total"] == pytest.approx(70.9)
    assert report["raw_total_exact"] == "709/10"
    assert report["editorial_percent"] == 70


@pytest.mark.parametrize("a_score,expected", [(28.9, 70), (29.99, 71), (28, 71)])
def test_category_mode_floors_not_rounds(tmp_path, capsys, a_score, expected):
    data = {"categories": {"A": a_score, "B": 16, "C": 12, "D": 9, "E": 5 if a_score != 28 else 6}}
    _, _, report = run(tmp_path, data, capsys)
    assert report["editorial_percent"] == expected


# --- Karar sirasi (K101, K116) ---

def test_all_complete_is_ready_and_cover_line_exact(tmp_path, capsys):
    code, summary, report = run(tmp_path, payload(), capsys)
    assert code == 0
    assert report["cover_line"] == (
        "Editoryal hazır olma: %100 | İnceleme kapsamı: kart 240/240; fotoğraf 250/250; kritik iddia 40/40"
        f" | Karar: {READY}")
    assert summary["decision"] == READY and summary["percent"] == 100


def test_high_score_cannot_hide_p0(tmp_path, capsys):
    code, _, report = run(tmp_path, payload(findings=[{"id": "YANLIS-SEHIR", "priority": "P0"}]), capsys)
    assert report["editorial_percent"] == 100 and report["decision"] == FIX and code == 1


def test_open_p1_needs_fix(tmp_path, capsys):
    _, _, report = run(tmp_path, payload(findings=[{"id": "BAG-3", "priority": "P1"}]), capsys)
    assert report["decision"] == FIX
    assert report["open_findings"]["P1"] == ["BAG-3"]


def test_p2_only_stays_ready_and_is_listed(tmp_path, capsys):
    findings = [{"id": "Z", "priority": "P2"}, {"id": "A", "priority": "P2"}, {"id": "A", "priority": "P2"}]
    code, _, report = run(tmp_path, payload(findings=findings), capsys)
    assert report["decision"] == READY and code == 0
    assert report["open_findings"]["P2"] == ["A", "Z"]


def test_missing_target_needs_fix(tmp_path, capsys):
    rows = full_criteria(A1=crit("A1", passed=200, required=200))
    _, _, report = run(tmp_path, payload(rows), capsys)
    a1 = {r["code"]: r for r in report["criteria"]}["A1"]
    assert a1["required"] == 240 and "240" in a1["note"]
    assert report["missing_targets"] == ["A1"]
    assert report["decision"] == FIX


def test_not_checked_scores_zero_and_needs_evidence(tmp_path, capsys):
    rows = full_criteria(A4=crit("A4", status="not_checked", reason="resmî kaynak açılmadı"))
    _, _, report = run(tmp_path, payload(rows), capsys)
    assert report["raw_total"] == 93
    assert report["decision"] == EVIDENCE
    assert "doğrulanan alt sınır, kısmi denetim" in report["labels"]


def test_partial_is_lower_bound(tmp_path, capsys):
    rows = full_criteria(A3=crit("A3", passed=5, required=10, status="partial"))
    _, _, report = run(tmp_path, payload(rows), capsys)
    assert report["raw_total"] == 96.5 and report["editorial_percent"] == 96
    assert report["decision"] == EVIDENCE
    assert "%96 (doğrulanan alt sınır, kısmi denetim)" in report["cover_line"]


def test_separate_stage_e4_scores_zero_but_does_not_block(tmp_path, capsys):
    rows = full_criteria(E4=crit("E4", passed=0, status="separate_stage", reason="önizleme ayrı aşama"))
    out_md = tmp_path / "out" / "score.md"
    code, summary, report = run(tmp_path, payload(rows), capsys, "--format", "md")
    assert report["raw_total"] == 98
    assert report["decision"] == READY and code == 0
    assert report["decision_note"] == "önizleme ve Drive kontrolleri ayrı aşamada"
    assert report["labels"] == ["doğrulanan alt sınır, kısmi denetim"]  # E4 olculmedi: alt sinir
    assert "%98 (doğrulanan alt sınır, kısmi denetim)" in report["cover_line"]
    assert report["cover_line"].endswith(f"Karar: {READY} (önizleme ve Drive kontrolleri ayrı aşamada)")
    assert report["deviations"] and "E4" in report["deviations"][0]
    md = out_md.read_text(encoding="utf-8")
    assert "Sapma" in md and summary["md"] == str(out_md)


def test_inventory_missing_is_not_measured(tmp_path, capsys):
    code, summary, report = run(tmp_path, {"inventory_available": False, "findings": []}, capsys)
    assert report["editorial_percent"] is None and report["raw_total"] is None
    assert report["cover_line"].startswith("Editoryal hazır olma: ÖLÇÜLEMEDİ | İnceleme kapsamı: kart ?/?;")
    assert report["decision"] == EVIDENCE and code == 1
    assert summary["percent"] is None


def test_inventory_missing_with_p0_needs_fix(tmp_path, capsys):
    data = {"inventory_available": False, "findings": [{"id": "X", "priority": "P0"}]}
    assert run(tmp_path, data, capsys)[2]["decision"] == FIX


@pytest.mark.parametrize("code", ["A1", "B1", "B2", "B3", "B4", "C1"])
def test_target_criterion_not_applicable_is_missing_target(tmp_path, capsys, code):
    rows = full_criteria(**{code: crit(code, status="not_applicable", reason="kart yok")})
    exit_code, _, report = run(tmp_path, payload(rows), capsys)
    assert report["missing_targets"] == [code] and report["decision"] == FIX and exit_code == 1
    assert code in report["decision_reason"] and "tamam" not in report["decision_reason"]
    assert "nihai değil" in report["labels"] and report["max_possible"] == 100  # hedef paydadan cikmaz
    assert "sabit payda" in {r["code"]: r for r in report["criteria"]}[code]["note"]


@pytest.mark.parametrize("findings,expected", [
    ([], EVIDENCE),                                                   # KALDI var, bulgu yok
    ([{"id": "BASKA", "priority": "P2", "criteria": ["B5"]}], EVIDENCE),  # bulgu baska olcute bagli
    ([{"id": "ALT-1", "priority": "P2", "criteria": ["A5"]}], READY),     # P2 olarak siniflanmis
    ([{"id": "ALT-1", "priority": "P1", "criteria": ["A5"]}], FIX),
])
def test_failed_units_need_a_linked_finding(tmp_path, capsys, findings, expected):
    rows = full_criteria(A5=crit("A5", passed=9, required=10))
    code, _, report = run(tmp_path, payload(rows, findings=findings), capsys)
    assert report["decision"] == expected and code == (0 if expected == READY else 1)
    unlinked = [gap for gap in report["evidence_gaps"] if gap.startswith("A5:") and "KALDI" in gap]
    assert bool(unlinked) == (expected == EVIDENCE)


@pytest.mark.parametrize("findings", [[], [{"id": "LIS-1", "priority": "P2", "criteria": ["D1"]}]])
def test_d1_license_failure_is_p0_gate_even_if_linked_to_p2(tmp_path, capsys, findings):
    rows = full_criteria(D1=crit("D1", passed=50, required=100))
    code, _, report = run(tmp_path, payload(rows, findings=findings), capsys)
    assert report["raw_total"] == 98.5 and report["decision"] == FIX and code == 1
    assert "D1" in report["decision_reason"] and report["gates"] and "D1" in report["gates"][0]


def test_markdown_multiline_reason_keeps_table_rows(tmp_path, capsys):
    rows = full_criteria(A2=crit("A2", status="not_applicable", reason="satir1\nsatir2 | x\r\nsatir3"))
    run(tmp_path, payload(rows), capsys, "--format", "md")
    lines = (tmp_path / "out" / "score.md").read_text(encoding="utf-8").splitlines()
    table = [ln for ln in lines if ln.startswith("| ") and ln.split("|")[1].strip() in CODES]
    assert len(table) == 25 and all(ln.endswith(" |") for ln in table)
    assert "satir1 satir2 \\| x satir3" in next(ln for ln in table if ln.startswith("| A2 "))
    assert not any(ln.startswith("satir") for ln in lines)


# --- Kapsam (K100, K117) ---

def test_missing_coverage_shows_question_marks_and_blocks_ready(tmp_path, capsys):
    _, _, report = run(tmp_path, payload(coverage=None), capsys)
    assert "kart ?/?; fotoğraf ?/?; kritik iddia ?/?" in report["cover_line"]
    assert report["decision"] == EVIDENCE


def test_incomplete_coverage_is_partial(tmp_path, capsys):
    cov = {"cards": {"reviewed": 200, "total": 240}, "photos": [250, 250], "critical_claims": [40, 40]}
    _, _, report = run(tmp_path, payload(coverage=cov), capsys)
    assert "kart 200/240" in report["cover_line"]
    assert "doğrulanan alt sınır, kısmi denetim" in report["labels"]
    assert report["decision"] == EVIDENCE


def test_markdown_has_cover_line_and_25_rows(tmp_path, capsys):
    code, _, report = run(tmp_path, payload(), capsys, "--format", "md")
    md = (tmp_path / "out" / "score.md").read_text(encoding="utf-8")
    lines = md.splitlines()
    assert lines[0] == report["cover_line"]
    rows = [ln for ln in lines if ln.startswith("| ") and ln.split("|")[1].strip() in CODES]
    assert len(rows) == 25
    assert "Açık P0: 0" in md


def test_category_mode_markdown(tmp_path, capsys):
    data = {"categories": {"A": 18, "B": 11, "C": 14, "D": 9, "E": 3}}
    run(tmp_path, data, capsys, "--format", "md")
    md = (tmp_path / "out" / "score.md").read_text(encoding="utf-8")
    assert "| A | Bilgi kartları ve kaynaklar | 35 | 18 |" in md


# --- Kullanim / yapi hatalari (cikis 2) ---

@pytest.mark.parametrize("mutate", [
    lambda d: d["criteria"].pop(),                                          # eksik kod
    lambda d: d["criteria"].append(crit("A1")),                             # yinelenen kod
    lambda d: d["criteria"].append(crit("F1")),                             # bilinmeyen kod
    lambda d: d["criteria"][1].update(status="bilinmiyor"),                 # gecersiz durum
    lambda d: d["criteria"][1].update(passed=-1),                           # negatif
    lambda d: d["criteria"][1].update(passed=True),                         # bool sayi degil
    lambda d: d["criteria"][1].update(status="not_applicable", reason=" "),  # gerekcesiz uygulanmaz
    lambda d: d["criteria"][0].update(status="separate_stage"),             # yalniz E4
    lambda d: d.update(findings=[{"id": "X", "priority": "P3"}]),           # gecersiz oncelik
    lambda d: d.update(findings=[{"priority": "P0"}]),                      # id yok
    lambda d: d.update(categories={"A": 1, "B": 1, "C": 1, "D": 1, "E": 1}),  # iki mod birden
    lambda d: d.update(coverage={"cards": [5, 4]}),                         # incelenen > toplam
    lambda d: d["criteria"].__setitem__(0, "A1"),                           # kayit nesne degil
    lambda d: d.update(criteria={"A1": 1}),                                 # criteria liste degil
    lambda d: d.update(findings={"id": "X"}),                               # findings liste degil
    lambda d: d.update(coverage=[1, 2]),                                    # coverage nesne degil
    lambda d: d.update(coverage={"cards": [1, 2, 3]}),                      # [a, b] degil
    lambda d: d.update(inventory_available="hayir"),                        # bool degil
    lambda d: d.update(findings=[{"id": "X", "priority": "P2", "criteria": ["Z9"]}]),  # bilinmeyen bag
    lambda d: d.update(findings=[{"id": "X", "priority": "P2", "criteria": "A5"}]),    # bag liste degil
])
def test_structure_errors_exit_2(tmp_path, capsys, mutate):
    data = payload()
    mutate(data)
    code, summary, report = run(tmp_path, data, capsys)
    assert code == 2 and report is None
    assert "error" in summary


@pytest.mark.parametrize("categories", [
    {"A": 36, "B": 0, "C": 0, "D": 0, "E": 0},
    {"A": 1, "B": 1, "C": 1, "D": 1},
    {"A": "x", "B": 1, "C": 1, "D": 1, "E": 1},
    {"A": -1, "B": 1, "C": 1, "D": 1, "E": 1},
])
def test_category_errors_exit_2(tmp_path, capsys, categories):
    code, _, report = run(tmp_path, {"categories": categories}, capsys)
    assert code == 2 and report is None


def test_bad_json_and_missing_file_exit_2(tmp_path, capsys):
    code, summary, _ = run(tmp_path, None, capsys, raw="{bozuk")
    assert code == 2 and "error" in summary
    missing = es.main(["--input", str(tmp_path / "yok.json"), "--out", str(tmp_path / "s.json")])
    assert missing == 2
    capsys.readouterr()


def test_no_mode_and_non_object_exit_2(tmp_path, capsys):
    assert run(tmp_path, {"findings": []}, capsys)[0] == 2
    assert run(tmp_path, [1, 2], capsys)[0] == 2


def test_md_format_rejects_md_out(tmp_path, capsys):
    src = tmp_path / "c.json"
    src.write_text(json.dumps(payload()), encoding="utf-8")
    code = es.main(["--input", str(src), "--out", str(tmp_path / "x.md"), "--format", "md"])
    assert code == 2
    capsys.readouterr()


# --- Sozlesme: tek satir, deterministik, girdi degismez ---

def test_stdout_single_line_and_deterministic(tmp_path, capsys):
    src = tmp_path / "c.json"
    src.write_text(json.dumps(payload(), ensure_ascii=False), encoding="utf-8")
    outs = []
    for name in ("a.json", "b.json"):
        es.main(["--input", str(src), "--out", str(tmp_path / name)])
        printed = capsys.readouterr().out
        assert printed.count("\n") == 1
        outs.append((tmp_path / name).read_bytes())
    assert outs[0] == outs[1]


def test_build_report_does_not_mutate_input():
    data = payload(findings=[{"id": "B", "priority": "P1"}])
    before = copy.deepcopy(data)
    es.build_report(data)
    assert data == before


def test_runs_as_script(tmp_path):
    src = tmp_path / "c.json"
    src.write_text(json.dumps({"categories": {"A": 18, "B": 11, "C": 14, "D": 9, "E": 3}}), encoding="utf-8")
    proc = subprocess.run([sys.executable, str(SCRIPT), "--input", str(src), "--out", str(tmp_path / "s.json")],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 1
    assert json.loads(proc.stdout)["percent"] == 55
