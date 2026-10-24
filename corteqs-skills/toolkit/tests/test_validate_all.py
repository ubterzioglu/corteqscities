"""validate_all: resmi v7 dogrulayiciyi salt okunur sarar. Testler sahte (stub) --tools klasoru ile hermetiktir."""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
import types
from pathlib import Path

import pytest

import validate_all as va
from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE

REAL_TOOLS = Path(r"C:\temp_private\corteqs\0000_newera\araclar\arac")

STUB_VALUES = '''
def parse_list(value, separator):
    if not isinstance(value, str):
        raise TypeError("Liste hücresi metin olmalı.")
    pieces = [p.strip() for p in value.split(separator) if p.strip()]
    if len(pieces) != len(set(pieces)):
        raise ValueError("Listede yinelenen değer var.")
    return pieces

PARSERS = {"id_list": lambda value: parse_list(value, ";"), "text_list": lambda value: parse_list(value, "\\n")}

def parse_value(value, field):
    if value in (None, ""):
        return None
    return PARSERS.get(field["type"], str)(value)
'''
STUB_READ = '''
import json
from pathlib import Path
from core.content_delivery.delivery_values import parse_value

CFG = Path(__file__).with_name("stub_config.json")

def read(path):
    cfg = json.loads(CFG.read_text(encoding="utf-8"))
    if not Path(path).is_file():
        raise FileNotFoundError(str(path))
    if cfg.get("read_error"):
        raise ValueError(cfg["read_error"])
    answers = [{"source_ids": parse_value(v, {"type": "id_list"})} for v in cfg.get("lists", [])]
    data = {"photos": cfg.get("photos", []), "answers": answers, "_structure": cfg["structure"]}
    return data, cfg.get("provenance", []), {}
'''
STUB_VALIDATION = '''
def validate_files(data, assets_root):
    return dict(data["_structure"])
'''
STUB_DELIVERY = '''
from pathlib import Path

def audit(root, photos, provenance, require_new_chain=False):
    errors = [p["photo_id"] + ": " + p["err"] for p in photos if p.get("err")]
    if require_new_chain:
        errors += [p["photo_id"] + ": yeni üretimde zorunlu downloaded_on" for p in photos if p.get("new_err")]
    return {"photos": len(photos), "errors": errors, "structural_passed": not errors}

def export_attributions(root, photos, provenance):
    target = Path(root) / "Teslimler/fotograf-atiflari-v7.csv"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("photo_id\\n" + "\\n".join(p["photo_id"] for p in photos), encoding="utf-8")
'''


def structure(errors=(), warnings=(), counts=None, minimum=None):
    counts = counts or {"answers": 5, "places": 3}
    minimum = minimum or {"answers": 5, "places": 2}
    return {"errors": list(errors), "warnings": list(warnings), "counts": counts, "minimum": minimum, "valid": not errors}


def make_tools(base: Path, config: dict, name: str = "tools") -> Path:
    tools = base / name
    pkg = tools / "core" / "content_delivery"
    pkg.mkdir(parents=True)
    (tools / "core" / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    for path, body in ((pkg / "delivery_values.py", STUB_VALUES), (tools / "read_delivery_v7.py", STUB_READ),
                       (tools / "v7_validation.py", STUB_VALIDATION), (tools / "delivery_tools.py", STUB_DELIVERY)):
        path.write_text(textwrap.dedent(body), encoding="utf-8")
    (tools / "stub_config.json").write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    return tools


CLEAN = {"structure": structure(), "photos": [{"photo_id": "t:foto:1"}], "lists": ["a;b"]}
DIRTY = {
    "structure": structure(
        errors=[f"Kanıtlar!{r}: Kaynak bilgisi incelemesi tanımsız seçim içeriyor." for r in range(8, 13)]
        + ["Yanıtlar!?: Yinelenen kimlik: t:a", "Şehir: geçerli IANA saat dilimi gerekli."],
        warnings=["Kanıtlar!?: rights_status incelemesi açık."],
        counts={"answers": 4, "places": 3}),
    "photos": [{"photo_id": "t:foto:1", "err": "eksik license_url"}, {"photo_id": "t:foto:2", "new_err": True},
               {"photo_id": "t:foto:3", "err": "eksik license_url"}],
    "lists": ["a;a", "b;c;b", "d"],
}


def snapshot(root: Path) -> dict[str, int]:
    return {str(p.relative_to(root)): p.stat().st_mtime_ns for p in root.rglob("*")}


def run(capsys, argv):
    code = va.main([str(a) for a in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1, lines
    return code, json.loads(lines[0])


# --- class grouping ------------------------------------------------------------

@pytest.mark.parametrize("message,expected", [
    ("Kanıtlar!?: Kaynak bilgisi incelemesi tanımsız seçim içeriyor.", "Kanıtlar: Kaynak bilgisi incelemesi tanımsız seçim içeriyor."),
    ("Kanıtlar!123: Kaynak bilgisi incelemesi tanımsız seçim içeriyor.", "Kanıtlar: Kaynak bilgisi incelemesi tanımsız seçim içeriyor."),
    ("Yanıtlar!9: Yinelenen kimlik: x:a", "Yanıtlar: Yinelenen kimlik"),
    ("SayfaAlanları!?: quick_links: gerekli alanlar label, entry.", "SayfaAlanları: quick_links"),
    ("Şehir: geçerli IANA saat dilimi gerekli.", "Şehir: geçerli IANA saat dilimi gerekli."),
    ("eindhoven:foto:klokgebouw-01: ana fotoğraf kaydı ile kaynak dosyası uyuşmuyor", "ana fotoğraf kaydı ile kaynak dosyası uyuşmuyor"),
    ("t:foto:1: dosya okunamadı original_file (OSError)", "dosya okunamadı original_file (OSError)"),
    ("Yinelenen kaynak photo_id", "Yinelenen kaynak photo_id"),
    # metnin icindeki ' : ' (onunde bosluk olan iki nokta) sinifi kesmemeli
    ("Bağlantılar!?: Bağlantı kimliği yalnız küçük ASCII harf, sayı, -, _ ve : içermeli.",
     "Bağlantılar: Bağlantı kimliği yalnız küçük ASCII harf, sayı, -, _ ve : içermeli."),
])
def test_error_class(message, expected):
    assert va.error_class(message) == expected


def test_group_classes_counts_and_distinct_examples():
    messages = ["Kanıtlar!?: X yok."] * 4 + ["Kanıtlar!8: X yok.", "Kanıtlar!9: X yok.", "Kanıtlar!10: X yok.", "Rotalar!?: Y."]
    groups = va.group_classes(messages, max_examples=3)
    assert groups[0] == {"class": "Kanıtlar: X yok.", "count": 7,
                         "examples": ["Kanıtlar!?: X yok.", "Kanıtlar!8: X yok.", "Kanıtlar!9: X yok."]}
    assert groups[1] == {"class": "Rotalar: Y.", "count": 1, "examples": ["Rotalar!?: Y."]}
    assert va.group_classes([], 3) == []


# --- tolerant list patch ---------------------------------------------------------

def _fake_dv():
    def parse_list(value, separator):
        pieces = [p.strip() for p in value.split(separator) if p.strip()]
        if len(pieces) != len(set(pieces)):
            raise ValueError("dup")
        return pieces
    dv = types.SimpleNamespace(parse_list=parse_list)
    dv.PARSERS = {"id_list": lambda v: dv.parse_list(v, ";"), "date": str}
    return dv


def test_tolerant_lists_dedupes_counts_and_restores():
    dv = _fake_dv()
    original_parse, original_id = dv.parse_list, dv.PARSERS["id_list"]
    with va.tolerant_lists(dv) as offending:
        assert dv.PARSERS["id_list"]("a;b;a") == ["a", "b"]
        assert dv.parse_list("x\ny\nx", "\n") == ["x", "y"]
        assert dv.PARSERS["id_list"]("c;d") == ["c", "d"]
    assert offending == ["a;b;a", "x\ny\nx"]
    assert dv.parse_list is original_parse and dv.PARSERS["id_list"] is original_id
    with pytest.raises(ValueError):
        dv.PARSERS["id_list"]("a;a")


def test_tolerant_lists_restores_on_exception():
    dv = _fake_dv()
    original_parse, original_id = dv.parse_list, dv.PARSERS["id_list"]
    with pytest.raises(RuntimeError):
        with va.tolerant_lists(dv):
            raise RuntimeError("boom")
    assert dv.parse_list is original_parse and dv.PARSERS["id_list"] is original_id


# --- tools loading ------------------------------------------------------------------

def test_load_tools_switches_between_tool_dirs(tmp_path):
    first = va.load_tools(make_tools(tmp_path, CLEAN, "one"))
    second = va.load_tools(make_tools(tmp_path, DIRTY, "two"))
    assert Path(first.read.__code__.co_filename).parent.name == "one"
    assert Path(second.read.__code__.co_filename).parent.name == "two"
    assert not list(tmp_path.rglob("__pycache__"))  # bytecode yazilmaz


def test_load_tools_missing_dir_raises(tmp_path):
    with pytest.raises(va.ToolsError):
        va.load_tools(tmp_path / "yok")
    (tmp_path / "bos").mkdir()
    with pytest.raises(va.ToolsError):
        va.load_tools(tmp_path / "bos")


# --- CLI ------------------------------------------------------------------------------

def test_clean_package_exit_0_and_summary(tmp_path, package, capsys):
    tools = make_tools(tmp_path, CLEAN)
    out = tmp_path / "rapor" / "report.json"
    code, summary = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--out", out])
    assert code == EXIT_OK
    assert summary["technically_complete"] is True
    assert summary["structure"] == {"errors": 0, "warnings": 0}
    assert summary["media"] == {"errors": 0}
    assert summary["minimum_gaps"] == {} and summary["error_classes"] == [] and summary["tolerated_duplicate_list_cells"] == 0
    assert summary["mode"] == "audit" and summary["new_content"] is False
    assert set(summary["extras"]) == {"placeholders", "wikipedia_labeled_official", "verified_without_snapshot",
                                      "shared_coordinates", "homepage_only_sources", "history_share"}
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["summary"] == summary
    assert report["extras"]["placeholders"]["label"] == "ek kontrol"


def test_dirty_package_findings_classes_and_new_content(tmp_path, package, capsys):
    tools = make_tools(tmp_path, DIRTY)
    out = tmp_path / "r.json"
    code, summary = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--out", out, "--max-examples", 2])
    assert code == EXIT_FINDINGS
    assert summary["technically_complete"] is False
    assert summary["structure"] == {"errors": 7, "warnings": 1}
    assert summary["media"] == {"errors": 2}
    assert summary["minimum_gaps"] == {"answers": {"actual": 4, "minimum": 5}}
    assert summary["tolerated_duplicate_list_cells"] == 2
    top = summary["error_classes"][0]
    assert top["class"] == "Kanıtlar: Kaynak bilgisi incelemesi tanımsız seçim içeriyor." and top["count"] == 5
    assert len(top["examples"]) == 2
    assert summary["media_classes"] == [{"class": "eksik license_url", "count": 2,
                                         "examples": ["t:foto:1: eksik license_url", "t:foto:3: eksik license_url"]}]
    report = json.loads(out.read_text(encoding="utf-8"))
    assert len(report["structure"]["errors"]) == 7
    assert report["tolerated_duplicate_list_cells"] == ["a;a", "b;c;b"]
    assert report["warning_classes"][0]["count"] == 1

    _, summary_new = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--new-content"])
    assert summary_new["media"] == {"errors": 3} and summary_new["new_content"] is True


def test_audit_mode_is_read_only(tmp_path, package, capsys):
    tools = make_tools(tmp_path, DIRTY)
    before = snapshot(package["root"])
    code, _ = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--new-content", "--out", tmp_path / "o.json"])
    assert code == EXIT_FINDINGS
    assert snapshot(package["root"]) == before
    assert not list((package["root"] / "Teslimler").glob("*"))


def test_audit_refuses_out_inside_package(tmp_path, package, capsys):
    tools = make_tools(tmp_path, CLEAN)
    before = snapshot(package["root"])
    code, summary = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--out", package["root"] / "Teslimler" / "x.json"])
    assert code == EXIT_USAGE and "error" in summary
    assert snapshot(package["root"]) == before


def test_emit_mode_writes_official_deliverables(tmp_path, package, capsys):
    tools = make_tools(tmp_path, DIRTY)
    code, summary = run(capsys, [package["xlsx"], package["root"], "--tools", tools, "--mode", "emit", "--new-content"])
    assert code == EXIT_FINDINGS and summary["mode"] == "emit"
    out = package["root"] / "Teslimler"
    names = {p.name for p in out.iterdir()}
    assert {"photo-provenance-v7.json", "normalized-tables-v7.json", "paket-kontrol-v7.json", "fotograf-atiflari-v7.csv"} <= names
    result = json.loads((out / "paket-kontrol-v7.json").read_text(encoding="utf-8"))
    assert result["version"] == "7.0" and result["technically_complete"] is False
    assert len(result["media"]["errors"]) == 3 and len(result["structure"]["errors"]) == 7
    assert result["minimum_gaps"] == {"answers": {"actual": 4, "minimum": 5}}


@pytest.mark.parametrize("problem", ["tools_missing", "workbook_missing", "root_missing", "read_error"])
def test_usage_and_structure_errors_exit_2(tmp_path, package, capsys, problem):
    config = {**CLEAN, "read_error": "Yanıtlar: headers changed"} if problem == "read_error" else CLEAN
    tools = make_tools(tmp_path, config)
    args = {"tools": tools, "xlsx": package["xlsx"], "root": package["root"]}
    args.update({"tools_missing": {"tools": tmp_path / "yok"}, "workbook_missing": {"xlsx": tmp_path / "yok.xlsx"},
                 "root_missing": {"root": tmp_path / "paket-yok"}}.get(problem, {}))
    code, summary = run(capsys, [args["xlsx"], args["root"], "--tools", args["tools"]])
    assert code == EXIT_USAGE
    assert summary["error"]


def test_tools_from_env_and_missing_everywhere(tmp_path, package, capsys, monkeypatch):
    tools = make_tools(tmp_path, CLEAN)
    monkeypatch.setenv("CORTEQS_TOOLS", str(tools))
    code, _ = run(capsys, [package["xlsx"], package["root"]])
    assert code == EXIT_OK
    monkeypatch.delenv("CORTEQS_TOOLS")
    code, summary = run(capsys, [package["xlsx"], package["root"]])
    assert code == EXIT_USAGE and "--tools" in summary["error"]


def test_bad_max_examples_is_usage_error(tmp_path, package):
    with pytest.raises(SystemExit) as exc:
        va.main([str(package["xlsx"]), str(package["root"]), "--tools", str(tmp_path), "--max-examples", "-1"])
    assert exc.value.code == EXIT_USAGE


# --- real tools (integration) ------------------------------------------------------

@pytest.mark.real
@pytest.mark.skipif(not (REAL_TOOLS / "read_delivery_v7.py").is_file(), reason="gercek araclar/arac klasoru yok")
def test_real_tools_run_read_only_on_mini_package(tmp_path, package):
    before_pkg = snapshot(package["root"])
    before_tools = {p for p in REAL_TOOLS.rglob("*")}
    # CLI olarak calistirilir: resmi kod UTF-8 modu ister (betik kendini -X utf8 ile yeniden baslatir)
    script = Path(va.__file__).resolve()
    proc = subprocess.run([sys.executable, str(script), str(package["xlsx"]), str(package["root"]), "--tools", str(REAL_TOOLS),
                           "--new-content", "--out", str(tmp_path / "real.json")], capture_output=True, text=True,
                          encoding="utf-8", timeout=300)
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1, proc.stdout + proc.stderr
    summary = json.loads(lines[0])
    assert proc.returncode in (EXIT_FINDINGS, EXIT_USAGE), proc.stderr
    assert ("structure" in summary) or summary.get("error")
    assert snapshot(package["root"]) == before_pkg
    assert {p for p in REAL_TOOLS.rglob("*")} == before_tools  # __pycache__ dahil hicbir dosya eklenmez
