"""B1 metin-kod uyumu: city-pack ve city-audit SKILL.md'deki her `& $PY $TK\\<script>.py ...` komutu toolkit
script'inin argparse'indan gecmeli; degiskenler skill'in kendi tanimlarindan gelir, 'Sabit yollar' depoyla tutarli,
ara dosya zinciri kopuksuz, city-audit paketi salt okunur. Yardimcilar ve kapsam: skill_commands_helpers.py.
city-pack SKILL.md ayrica kod turunun sonuclarina ve ajan talimatlarina uymali (U5): guney yarikure --bbox, ajan
add_sources klasoru, run_log girdileri ve beklenen cikisi, faz sonu manifest_check, ek foto turu (A12), foto yol
kontrolu (yalniz sayar), teslim kapisinda merge_package, uzun islerin bolunmesi (B14). U5 incelemesinin bulgulari:
bos qid tekrar sayilmaz, yeniden acilan faz (phase/started_at ayni, beklenen 'pencere farki' gap'i), paralel foto isi
faz pencerelerini cakistirmaz, ek foto turu yalniz yeni kayitlar + ortak onbellek, photo_rows cikis 2'de zincir durur,
ikinci denetim turu ayri dosyada, ortam.ps1 degerleri tam yol, onizleme genislikleri ornek, secim/kesif dusunme ayari.
skill-son-hal-3 testleri (B13, B15, A14, B16) test_skill_pack_phases.py'de; SKILL.md yardimcilarini buradan alir.
Sonda B16 hitap olcumunun kapilara baglanmasi (skill-son-hal-4): komutlarin --address-standard'i intake standardi.
Ag yok, toolkit script'i alt surec olarak calismaz. tmp_path'te iki deneme var: SKILL.md'deki satir ici foto yol
kontrolu sahte parca dosyalariyla; yeniden acilan faz senaryosu gercek phase_usage, manifest_check ve run_log
main()'leriyle.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from pathlib import Path, PureWindowsPath
from types import MappingProxyType

import pytest

import address_forms
import manifest_check
import merge_package
import phase_usage
import photo_previews
import photo_rounds
import run_log_helpers as rh
import run_log_inputs
import skill_commands_helpers as sc
import text_quality

MINI_SKILL = r"""# ornek
## Sabit yollar

```
ROOT   = C:\gercek\kok
PY     = ROOT\.venv\Scripts\python.exe
TK     = ROOT\corteqs-skills\toolkit\scripts      (arac kutusu)
CHECKS = ROOT\corteqs-skills\toolkit\checks.yaml
KAPSAM = ROOT\corteqs-skills\toolkit\KAPSAM.md   (S kontrolleri)
TOOLS  = ROOT\araclar\arac
DIGEST = <bu skill>\references\contract_digest.md (v7 sozlesmesi)
```

Calisma klasoru `WORK = ROOT\uretim\<city_id>\`; paket `PKG = WORK\paket\`. `snapshot_file = "x"` tanim degil.
Girdi: `XLSX` (teslim Excel'i), `LEVEL` (L0/L1/L2). Çıktı: `OUT = ROOT\denetim\<city_id>_<LEVEL>\` (paket disi).
"""
SAMPLE_VARIABLES = sc.skill_variables(MINI_SKILL)

SAMPLE = r"""Kapı: `& $PY $TK\xlsx_dump.py $WORK\_is\sablon.xlsx --summary --out-dir $WORK\_is\d` → 17 sekme.
```powershell
& $PY $TK\photo_candidates.py plan-from-xlsx <ara Excel'in bulunduğu klasör> --out $WORK\_is\v.jsonl
& $PY $TK\inventory.py $PKG --xlsx $XLSX --out $OUT\son.json   # K04: ilkiyle SHA karşılaştır
& $PY $TOOLS\download_media.py $WORK\plan.json $PKG --workers 2
```
2. ```powershell
   & $PY $TK\editorial_score.py --input $OUT\criteria.json --out $OUT\score.json --format md
   ```
- `impact.py $XLSX --diff <önceki.xlsx> --checks $CHECKS --out $OUT\impact.json`; `TOOLS\check_delivery.py` yok; `claim_check --mode number`.
"""


def _one(text: str, skill: str = "ornek") -> sc.Command:
    found = sc.extract_commands(skill, text)
    assert len(found) == 1, found
    return found[0]


# --- birim testleri: sentetik SKILL.md parcalari, gercek toolkit parser'lari ---

def test_variables_are_read_from_skill_md():
    assert isinstance(SAMPLE_VARIABLES, MappingProxyType)
    assert dict(SAMPLE_VARIABLES) == {
        "ROOT": r"C:\sahte", "PY": r"C:\sahte\.venv\Scripts\python.exe",
        "TK": r"C:\sahte\corteqs-skills\toolkit\scripts", "CHECKS": r"C:\sahte\corteqs-skills\toolkit\checks.yaml",
        "KAPSAM": r"C:\sahte\corteqs-skills\toolkit\KAPSAM.md", "TOOLS": r"C:\sahte\araclar\arac",
        "DIGEST": r"sahte-deger\references\contract_digest.md", "WORK": r"C:\sahte\uretim\sahte-sehir",
        "PKG": sc.FAKE_PKG, "OUT": r"C:\sahte\denetim\sahte-sehir_sahte-deger",
        "XLSX": sc.FAKE_PKG + r"\teslim.xlsx", "LEVEL": "L1"}


def test_extracts_code_blocks_inline_list_fences_and_bare_calls():
    found = sc.extract_commands("ornek", SAMPLE)
    assert [(c.line, c.script, c.kind, c.prefixed) for c in found] == [
        (1, "xlsx_dump", "tk", True), (3, "photo_candidates", "tk", True), (4, "inventory", "tk", True),
        (8, "editorial_score", "tk", True), (10, "impact", "bare", False)]  # $TOOLS\ ve TOOLS\ toolkit disi
    assert found[0].id == "ornek:L1:xlsx_dump"


def test_placeholders_are_single_arguments_and_comments_are_dropped():
    by_script = {c.script: c for c in sc.extract_commands("ornek", SAMPLE)}
    work, out, xlsx = SAMPLE_VARIABLES["WORK"], SAMPLE_VARIABLES["OUT"], SAMPLE_VARIABLES["XLSX"]
    assert sc.to_argv(by_script["photo_candidates"].args, SAMPLE_VARIABLES) == [
        "plan-from-xlsx", sc.FAKE_PKG, "--out", work + r"\_is\v.jsonl"]
    assert sc.to_argv(by_script["inventory"].args, SAMPLE_VARIABLES) == [
        sc.FAKE_PKG, "--xlsx", xlsx, "--out", out + r"\son.json"]
    previous = sc.PLACEHOLDERS["<önceki.xlsx>"]
    assert sc.to_argv(by_script["impact"].args, SAMPLE_VARIABLES)[:3] == [xlsx, "--diff", previous]
    # bilinmeyen yer tutucu tek arguman; '...' acilmaz, "..." ve $ad acilir; kelime icindeki '#' yorum degil
    assert sc.to_argv("<yeni yer tutucu> 'tek $PKG' \"$pkg\\a\" x#y", SAMPLE_VARIABLES) == [
        sc.GENERIC_PLACEHOLDER, "tek $PKG", sc.FAKE_PKG + r"\a", "x#y"]


def test_supported_powershell_forms_match_powershell_7():
    # PowerShell 7.6'da denenen ciktilar: tirnak icinde ve kelime ortasinda '.uzanti' duz metindir
    pkg = sc.FAKE_PKG
    text = r'''"$PKG.xlsx" x$PKG.xlsx --out=$PKG.xlsx $PKG-x $PKG/x a"b c"d 'a`b' a,b $PKG\x[1].json'''
    assert sc.to_argv(text, SAMPLE_VARIABLES) == [
        pkg + ".xlsx", "x" + pkg + ".xlsx", "--out=" + pkg + ".xlsx", pkg + "-x", pkg + "/x", "ab cd", "a`b", "a,b",
        pkg + r"\x[1].json"]


@pytest.mark.parametrize("bad", [
    "$WRK\\a.xlsx", "--out $WORK_is\\x", "a; b", "a | b", "'kapanmamis", "a `",
    "$PKG.xlsx", r"--out $($OUT)\x", "${PKG}.xlsx", "$PKG[0]", "$PKG:x", "$PKG..\\x", "$PKG=x",  # arguman duser/bolunur
    "@(1)", "@{a=1}", "@args", "(a)", "a(b)", "{a}", "a > b", "a&b", "--%", "$5x",  # PowerShell'e ozel sozdizimi
    '"a"b', "'a'.Length", '"a""b"', "$PKG,x", "x$PKG,y",  # tirnakla baslayan kelime, bitisik tirnak, virgul
])
def test_unsupported_powershell_is_an_explicit_error(bad):
    with pytest.raises(sc.CommandError):
        sc.to_argv(bad, SAMPLE_VARIABLES)


def test_sample_commands_pass_real_parsers():
    found = sc.extract_commands("ornek", SAMPLE)
    assert len(found) == 5
    for command in found:
        namespace, problems = sc.check_command(command, SAMPLE_VARIABLES)
        assert problems == [] and namespace is not None, problems


@pytest.mark.parametrize("expected, text", [
    ("toolkit'te yok", r"`& $PY $TK\yok_boyle.py --out $OUT\x.json`"),
    ("unrecognized arguments: --outdir", r"`& $PY $TK\xlsx_dump.py $XLSX --outdir $OUT\d`"),
    ("required: --snapshots", r"`& $PY $TK\claim_check.py --claims $OUT\c.jsonl --out $OUT\x.json`"),
    ("invalid choice: 'yayin'", r"`& $PY $TK\validate_all.py $XLSX $PKG --mode yayin`"),
    ("invalid choice: 'from-pkg'", r"`& $PY $TK\photo_candidates.py from-pkg $PKG --out $OUT\c.jsonl`"),
    ("invalid int value: 'otuz'", r"`& $PY $TK\contact_sheet.py --items $OUT\i --out-dir $OUT\p --per-sheet otuz`"),
    ("bicimi degil", r"`$PY $TK\xlsx_dump.py $XLSX`"),
    ("tanimsiz degisken $WRK", r"`& $PY $TK\xlsx_dump.py $WRK\a.xlsx`"),
    # kisaltma kapali (inceleme problari): bugun tamamlanir, ayni onekli yeni secenekle kirilir
    ("unrecognized arguments: --per-shee",
     r"`& $PY $TK\contact_sheet.py --items $OUT\i --out-dir $OUT\p --per-shee 30`"),
    ("unrecognized arguments: --mod", r"`& $PY $TK\validate_all.py $XLSX $PKG --mod emit`"),
    ("unrecognized arguments: --tab", r"`& $PY $TK\phase_usage.py report --session s --log l --tab`"),  # alt parser
])
def test_mismatches_are_red(expected, text):
    namespace, problems = sc.check_command(_one(text), SAMPLE_VARIABLES)
    assert namespace is None or "bicimi degil" in expected
    assert any(expected in problem for problem in problems), problems


def test_parser_is_captured_from_main_without_running_it(tmp_path, capsys):
    marker = tmp_path / "calisti.txt"

    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser()
        parser.add_subparsers(dest="command", required=True).add_parser("plan").add_argument("--out", required=True)
        try:
            parser.parse_args(argv)
        except Exception:  # yakalama 'except Exception' ile yutulmamali
            return 2
        marker.write_text("main calisti", encoding="utf-8")
        return 0

    captured = sc.parser_from_main(main)
    assert captured is not None and not marker.exists()
    assert list(sc.subcommands(captured)) == ["plan"] and sc.parse_quietly(captured, ["plan", "--out", "x"])[1] == ""
    assert sc.parser_from_main(lambda argv: 0) is None
    assert isinstance(sc.load_parser("download_plan"), argparse.ArgumentParser)  # gercek script, argparse main()'de
    assert capsys.readouterr().out == ""  # main ozet basmadi: calismadi


def test_inline_mentions_bind_option_only_pieces_to_the_sentence_script():
    assert sc.option_mentions("ornek", SAMPLE) == [("ornek:L10", "claim_check", ["--mode", "number"])]
    text = "\n".join([
        "`claim_check --mode unit` sayar; `--mode number` ile ikinci gecis. `--partial` YOK.",
        "`build_xlsx` aksini reddeder; `--allow-human-values` kullanilmaz.",
        "`phase_usage report --subagents` ve `--tabel`; `inventory.py $PKG` ile `--xlsx x.xlsx`.",
        "`--mode emit` yalniz burada.",
    ])
    assert sc.option_mentions("x", text) == [  # cumlesinde script anmasi olmayan --partial/--mode emit kapsam disi
        ("x:L1", "claim_check", ["--mode", "unit"]), ("x:L1", "claim_check", ["--mode", "number"]),
        ("x:L2", "build_xlsx", ["--allow-human-values"]),
        ("x:L3", "phase_usage", ["report", "--subagents"]), ("x:L3", "phase_usage", ["report", "--tabel"]),
        ("x:L3", "inventory", ["--xlsx", "x.xlsx"])]


def test_mention_options_are_looked_up_in_the_named_subcommand():
    for script, words in [("phase_usage", ["report", "--subagents"]), ("phase_usage", ["report", "--table"]),
                          ("phase_usage", ["mark", "--log"]), ("phase_usage", ["--subagents"]),
                          ("claim_check", ["--mode", "number"]), ("build_xlsx", ["--allow-human-values"])]:
        assert sc.mention_problems(script, words) == [], (script, words)
    for script, words in [("phase_usage", ["mark", "--subagents"]), ("phase_usage", ["mark", "--table"]),
                          ("phase_usage", ["report", "--tabel"]), ("phase_usage", ["rapor", "--log"]),
                          ("claim_check", ["--mode", "sayi"]), ("build_xlsx", ["--partiall"])]:
        assert sc.mention_problems(script, words), (script, words)


@pytest.mark.parametrize("old, new, expected", [
    (r"toolkit\scripts ", r"toolkit ", r"TK = ROOT\corteqs-skills\toolkit (beklenen"),  # inceleme probu
    ("checks.yaml", "checks.yml", "checks.yml yok"),
    ("KAPSAM.md", "KAPSAM2.md", "KAPSAM2.md yok"),
    (r"references\contract_digest.md", r"references\yok.md", "yok.md yok"),
    ("TK     =", "TKX    =", "'TK = ...' tanimi yok"),
])
def test_broken_constant_paths_are_red(old, new, expected):
    assert sc.path_problems("city-pack", MINI_SKILL) == []  # <bu skill> -> city-pack klasoru
    problems = sc.path_problems("city-pack", MINI_SKILL.replace(old, new, 1))
    assert any(expected in problem for problem in problems), problems


def test_package_writes_allow_only_read_only_inputs():
    package = PureWindowsPath(sc.FAKE_PKG)
    log = _one(r"`& $PY $TK\phase_usage.py mark x start --log $PKG\log.jsonl`")  # inceleme probu
    read = _one(r"`& $PY $TK\validate_all.py $XLSX $PKG --mode audit --out $OUT\v.json`")
    namespace, problems = sc.check_command(log, SAMPLE_VARIABLES)
    assert problems == [] and sc.package_writes(log, namespace, package) == [f"{log.id} log={sc.FAKE_PKG}\\log.jsonl"]
    namespace, problems = sc.check_command(read, SAMPLE_VARIABLES)
    assert problems == [] and sc.package_writes(read, namespace, package) == []


FLOW = r"""```powershell
& $PY $TK\photo_candidates.py plan-from-xlsx $PKG --out $WORK\_is\foto\plan.jsonl
& $PY $TK\commons_search.py --plan $WORK\_is\foto\plan.jsonl --out $WORK\_is\foto\search.jsonl
& $PY $TK\contact_sheet.py --items $WORK\_is\foto\items.jsonl --out-dir $WORK\_is\foto\pafta
```"""


def test_flow_inputs_must_come_from_earlier_outputs():
    assert sc.flow_problems(sc.extract_commands("ornek", FLOW), SAMPLE_VARIABLES) == []  # items.jsonl: ajan dosyasi
    renamed = FLOW.replace(r"--out $WORK\_is\foto\plan.jsonl", r"--out $WORK\_is\foto\venues.jsonl")  # pilot hatasi
    problems = sc.flow_problems(sc.extract_commands("ornek", renamed), SAMPLE_VARIABLES)
    assert len(problems) == 1 and problems[0].startswith(r"ornek:L3:commons_search: --plan"), problems
    lines = FLOW.splitlines()
    reordered = "\n".join([lines[0], lines[2], lines[1], *lines[3:]])  # girdi, ureten komuttan once
    assert sc.flow_problems(sc.extract_commands("ornek", reordered), SAMPLE_VARIABLES)


# --- gercek SKILL.md dosyalari ---

def _skill_text(skill: str) -> str:
    path = sc.SKILLS[skill]
    return path.read_text(encoding="utf-8") if path.is_file() else ""


VARIABLES_BY_SKILL = MappingProxyType({skill: sc.skill_variables(_skill_text(skill)) for skill in sc.SKILLS})
COMMANDS = [command for skill in sc.SKILLS for command in sc.extract_commands(skill, _skill_text(skill))]
USED_SCRIPTS = sorted({c.script for c in COMMANDS if (sc.SCRIPTS / f"{c.script}.py").is_file()})


def test_skill_files_exist_and_every_tk_call_is_extracted():
    for skill, path in sc.SKILLS.items():
        assert path.is_file(), f"{path} yok"
        text = path.read_text(encoding="utf-8")
        calls = [c for c in sc.extract_commands(skill, text) if c.kind == "tk"]
        assert calls, f"{skill}: hic '& $PY $TK\\...' komutu bulunamadi"
        assert len(calls) == len(re.findall(r"\$TK[\\/]", text)), f"{skill}: ayiklanamayan $TK\\ anmasi var"


@pytest.mark.parametrize("skill", list(sc.SKILLS))
def test_skill_constant_paths_match_the_repo(skill):
    problems = sc.path_problems(skill, _skill_text(skill))
    assert problems == [], "\n".join(problems)


def test_each_skill_uses_only_its_own_variables():
    pack, audit = VARIABLES_BY_SKILL["city-pack"], VARIABLES_BY_SKILL["city-audit"]
    common = {"ROOT", "PY", "TK", "CHECKS", "TOOLS", "DIGEST", "AGENTS", "PKG"}
    assert common | {"SCHEMA", "WORK"} <= set(pack)
    assert common | {"KAPSAM", "XLSX", "LEVEL", "OUT"} <= set(audit)
    assert len(sc.to_argv("$KAPSAM $LEVEL $DIGEST $AGENTS $OUT", audit)) == 5  # eskiden 'tanimsiz' sayiliyordu
    assert len(sc.to_argv("$SCHEMA $DIGEST $AGENTS $WORK", pack)) == 4
    for skill, text, name in [  # inceleme probu: baska skill'in degiskeni PowerShell'de bos acilir
        ("city-pack", r"`& $PY $TK\text_quality.py $XLSX --out $OUT\tq.json`", "$XLSX"),
        ("city-pack", r"`& $PY $TK\xlsx_dump.py $WORK\_is\a.xlsx --out-dir $OUT\d`", "$OUT"),
        ("city-audit", r"`& $PY $TK\xlsx_dump.py $WORK\_is\a.xlsx`", "$WORK"),
    ]:
        namespace, problems = sc.check_command(_one(text, skill), VARIABLES_BY_SKILL[skill])
        assert namespace is None and any(f"tanimsiz degisken {name}" in p for p in problems), problems


@pytest.mark.parametrize("command", COMMANDS, ids=[c.id for c in COMMANDS])
def test_skill_command_matches_toolkit_argparse(command):
    _, problems = sc.check_command(command, VARIABLES_BY_SKILL[command.skill])
    assert problems == [], "\n".join(problems)


@pytest.mark.parametrize("script", USED_SCRIPTS)
def test_used_script_help_works(script):
    assert sc.help_problems(script) == []


def test_skill_inline_option_mentions_exist():
    problems = []
    for skill in sc.SKILLS:
        for where, script, words in sc.option_mentions(skill, _skill_text(skill)):
            problems.extend(f"{where}: {problem}" for problem in sc.mention_problems(script, words))
    assert problems == [], "\n".join(problems)


@pytest.mark.parametrize("skill", list(sc.SKILLS))
def test_skill_flow_inputs_come_from_earlier_outputs(skill):
    problems = sc.flow_problems([c for c in COMMANDS if c.skill == skill], VARIABLES_BY_SKILL[skill])
    assert problems == [], "\n".join(problems)


def _parsed(skill: str) -> list[tuple[sc.Command, argparse.Namespace]]:
    rows = []
    for command in (c for c in COMMANDS if c.skill == skill):
        namespace, _ = sc.check_command(command, VARIABLES_BY_SKILL[skill])
        if namespace is not None:
            rows.append((command, namespace))
    assert rows, f"{skill}: ayristirilan komut yok"
    return rows


def test_city_audit_commands_stay_out_of_package_and_audit_only():
    package = PureWindowsPath(VARIABLES_BY_SKILL["city-audit"]["PKG"])
    rows = _parsed("city-audit")
    writes = [write for command, namespace in rows for write in sc.package_writes(command, namespace, package)]
    assert writes == [], "city-audit salt okunur: PKG icine yazan komut"
    assert {ns.mode for c, ns in rows if c.script == "validate_all"} == {"audit"}


def test_city_pack_never_allows_human_values_and_emits_once():
    rows = _parsed("city-pack")
    assert [c.id for c, ns in rows if getattr(ns, "allow_human", False)] == []
    assert len([c for c, ns in rows if c.script == "validate_all" and ns.mode == "emit"]) == 1


# --- city-pack SKILL.md: kod turu ve ajan talimatlariyla tutarlilik (U5) ---

SOUTH_BBOX = "-34.7,-34.5,-58.5,-58.3"  # guney yarikure: kutu '-' ile baslar
SNAP = re.compile(r"snap_[\w<>-]*")
PHOTO_PATH_CHECK = re.compile(r'^& \$PY -X utf8 -c "(?P<code>[^"]+)" "(?P<arg>[^"]+)"$')
EXPECTED_DELIVER_GAP = "editoryal skor yok"  # run_log: --score (city-audit, yeni oturum) yokken yazdigi gap
PHOTO_SUMMARY_KEYS = ("candidate_files", "search_files", "missing_entries", "original_thumb_fixed")
PHOTO_PARTS = {  # photo_rows rows'un yazdigi parcalar: paket yolu alanlari ('file', '*_file') ve yol olmayan alan
    "Fotoğraflar": {"photo_id": "x:photo:a-01", "file": "Fotoğraflar/a-01.jpg", "modifications": "C:\\yerel\\not"},
    "Kanıtlar": {"evidence_id": "x:evidence:a-01", "pixel_review_file": "Fotoğraflar/a-01.jpg",
                 "original_api_record": json.dumps({"descriptionurl": "https:\\/\\/commons"})},
    "FotoğrafKaynakları": {"photo_id": "x:photo:a-01", "original_file": "Teslimler/Orijinaller/a.jpg",
                           "web_file": "Teslimler/WebKopyalari/a.webp"},
}


def _section(text: str, heading: str) -> str:
    """Basliktan (or. '### 5. photos') ayni ya da ust duzeydeki bir sonraki basliga kadar (kod bloklari icinde degil)."""
    lines = text.splitlines()
    assert heading in lines, f"baslik yok: {heading}"
    start, level, inside = lines.index(heading), len(heading) - len(heading.lstrip("#")), False
    for index in range(start + 1, len(lines)):
        if sc.FENCE.match(lines[index]):
            inside = not inside
        elif not inside and re.match(rf"^#{{1,{level}}} ", lines[index]):
            return "\n".join(lines[start:index])
    return "\n".join(lines[start:])


def test_city_pack_bbox_survives_southern_hemisphere():
    """S3: `--bbox $BBOX` guney yarikurede ('-' ile baslayan kutu) argparse'ta secenek sanilir, cikis 2."""
    south = MappingProxyType({**VARIABLES_BY_SKILL["city-pack"], "BBOX": SOUTH_BBOX})
    uses = [c for c in COMMANDS if c.skill == "city-pack" and "$BBOX" in c.args]
    assert uses, "city-pack: $BBOX kullanan komut yok"
    for command in uses:
        namespace, problems = sc.check_command(command, south)
        assert problems == [], "\n".join(problems)
        if command.script == "merge_package":
            assert namespace.bbox == merge_package.parse_bbox(SOUTH_BBOX), command.id


def test_city_pack_agent_snap_folder_matches_common_rules():
    """S3: ajanin add_sources klasoru ortak-kurallar §4'teki kalip (her kosu yeni klasor); SKILL.md baska ad anlatmaz."""
    common = (sc.SKILLS["city-pack"].parent / "agents" / "ortak-kurallar.md").read_text(encoding="utf-8")
    template = re.search(r"add_sources\.py[^\n]*--subdir (\S+)", common)[1]
    text = _skill_text("city-pack")
    agent_side = {token for token in SNAP.findall(text) if "<" in token and not token.startswith("snap_kesif_")}
    assert agent_side == {template}, f"SKILL.md ajan klasoru {sorted(agent_side)}, ortak kurallar §4: {template}"
    assert "ek koşuda aynı klasör" not in text


def test_city_pack_run_log_gets_every_session_and_quality_input():
    """S5: oturum kapsami --session'dan (alt ajanlar <oturum-id>\\subagents'tan), oturum basina bir --usage; denetim
    orani ve reddedilen foto SKILL.md'nin belgeledigi dosyalardan (run_log'un okudugu desenler)."""
    rows = _parsed("city-pack")
    logs = [ns for c, ns in rows if c.script == "run_log"]
    reports = [ns for c, ns in rows if c.script == "phase_usage" and ns.command == "report"]
    assert len(logs) == 1 and len(reports) == 1, (logs, reports)
    log, report = logs[0], reports[0]
    assert [str(p) for p in log.session or []] == [report.session], "her oturumun kaydi --session ile verilmeli"
    assert [str(p) for p in log.usage or []] == [report.out], "oturum basina bir --usage (phase_usage report --out)"
    work = PureWindowsPath(VARIABLES_BY_SKILL["city-pack"]["WORK"], "_is")
    assert log.validation is not None
    assert [PureWindowsPath(p) for p in log.claim_audit or []] == [work / "denetim"]
    assert [PureWindowsPath(p) for p in log.photo_review or []] == [work / "foto" / "inceleme"]
    text = _skill_text("city-pack")
    for documented, globs in ((r"denetim\<parça>_iddia.jsonl", run_log_inputs.AUDIT_GLOBS),
                              (r"inceleme\review_<tur>_<parti>.jsonl", run_log_inputs.REVIEW_GLOBS),
                              (r"inceleme\verify_<tur>_<parti>.jsonl", run_log_inputs.REVIEW_GLOBS)):
        name = sc.PLACEHOLDER.sub("x1", PureWindowsPath(documented).name)
        assert documented in text and any(fnmatch.fnmatch(name, glob) for glob in globs), (documented, globs)


def test_city_pack_names_the_expected_run_log_gap():
    """S5: faz 7'de skor henuz yok; beklenen cikis 1'in tek gap'i SKILL.md'de run_log'un yazdigi adla anilmali."""
    assert f'"{EXPECTED_DELIVER_GAP} (' in (sc.SCRIPTS / "run_log.py").read_text(encoding="utf-8")
    assert f"`{EXPECTED_DELIVER_GAP}`" in _section(_skill_text("city-pack"), "### 7. deliver")


def test_city_pack_checks_manifest_after_every_phase_end():
    """U6: her `mark ... end`'den hemen sonra manifest_check (once calisirsa 'end isareti yok' bulgusu); teslimde --pkg."""
    rows = _parsed("city-pack")
    ends = [index for index, (c, ns) in enumerate(rows)
            if c.script == "phase_usage" and ns.command == "mark" and ns.event == "end"]
    assert ends and all(index + 1 < len(rows) and rows[index + 1][0].script == "manifest_check" for index in ends), \
        [rows[index][0].id for index in ends]
    checks = {rows[index][1].phase: rows[index + 1][1] for index in ends}
    assert "deliver" in checks and checks["deliver"].package_root is not None
    assert PureWindowsPath(checks["deliver"].package_root) == PureWindowsPath(VARIABLES_BY_SKILL["city-pack"]["PKG"])
    assert any(check.package_root is None for phase, check in checks.items() if phase != "deliver")


def _photo_path_check() -> tuple[str, str]:
    """Kod blogundaki `& $PY -X utf8 -c "<kod>" "<parca klasoru ya da dosyasi>"` satiri (kod, arguman)."""
    found = []
    inside = False
    for line in _skill_text("city-pack").splitlines():
        if sc.FENCE.match(line):
            inside = not inside
        elif inside and (match := PHOTO_PATH_CHECK.match(line.strip())) and r"\data\parcalar" in match["arg"]:
            found.append((match["code"], match["arg"]))
    assert len(found) == 1, f"foto yol kontrolu satiri {len(found)} tane (1 bekleniyor)"
    return found[0]


def _run_check(code: str, folder: Path) -> tuple[int, dict]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    done = subprocess.run([sys.executable, "-X", "utf8", "-c", code, str(folder)], capture_output=True, text=True,
                          encoding="utf-8", env=env, cwd=folder.parent, timeout=60, check=False)
    lines = done.stdout.strip().splitlines()
    return done.returncode, json.loads(lines[-1]) if lines else {}


def _write_parts(folder: Path, parts: dict) -> dict:
    for sheet, row in parts.items():
        (folder / f"{sheet}.foto.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    return {path.name: path.read_bytes() for path in folder.iterdir()}


def test_city_pack_photo_path_check_only_counts(tmp_path):
    """U1/S1: photo_rows rows paket yollarini '/' ile yazar; SKILL.md'deki satir yalniz SAYAR (dosyaya yazmaz), uc
    parcanin her yol alanina ('file', '*_file') bakar, yol olmayan alandaki '\\' bulgu degildir."""
    code, arg = _photo_path_check()
    assert not set(code) & set('$`"'), "PowerShell cift tirnakli metinde $, ` ve \" kodu bozar"
    rows = [ns for c, ns in _parsed("city-pack") if c.script == "photo_rows" and ns.command == "rows"]
    assert len(rows) == 1 and rows[0].parts_dir is None, "kontrol photo_rows rows'un varsayilan parca klasorune bakar"
    parts_dir = PureWindowsPath(rows[0].work, "data", "parcalar")
    assert PureWindowsPath(sc.to_argv(f'"{arg}"', VARIABLES_BY_SKILL["city-pack"])[0]) == parts_dir
    folder = tmp_path / "parcalar"
    folder.mkdir()
    assert _run_check(code, folder)[0] == 2, "foto parcasi yokken temiz sayilmamali"
    cases = [(None, None), ("Fotoğraflar", "file"), ("Kanıtlar", "pixel_review_file"),
             ("FotoğrafKaynakları", "web_file")]
    for sheet, field in cases:
        parts = PHOTO_PARTS if sheet is None else {
            **PHOTO_PARTS, sheet: {**PHOTO_PARTS[sheet], field: PHOTO_PARTS[sheet][field].replace("/", "\\")}}
        before = _write_parts(folder, parts)
        exit_code, summary = _run_check(code, folder)
        expected = (0, 0) if sheet is None else (1, 1)
        assert (exit_code, summary.get("ters_bolu")) == expected, (sheet, field, summary)
        assert {path.name: path.read_bytes() for path in folder.iterdir()} == before, "kontrol dosyaya yazdi"


def test_city_pack_extra_photo_round_layout_matches_toolkit():
    """U1/A12: anilan her foto klasoru ana tur ya da photo_rounds'un taradigi ek tur deseni; ek tur klasoru kendi
    dosyalariyla birlikte anlatilir; dogrulama icin anilan ozet alanlari photo_rows'ta."""
    photos = _section(_skill_text("city-pack"), "### 5. photos")
    folders = set(re.findall(r"_is\\(foto[^\\`\s]*)\\", photos)) - {photo_rounds.MAIN_ROUND}
    assert folders, "ek tur klasoru (A12) anlatilmamis"
    assert all(fnmatch.fnmatch(sc.PLACEHOLDER.sub("ek16", f), photo_rounds.EXTRA_ROUNDS) for f in folders), folders
    own_files = ("venues.jsonl", "search.jsonl", "candidates.jsonl", "decisions.json")
    assert any(re.search(r"_is\\foto_[^\\`\s]+\\", line) and all(f"`{name}`" in line for name in own_files)
               for line in photos.splitlines()), f"ek tur klasoru kendi dosyalariyla ({own_files}) anlatilmamis"
    source = (sc.SCRIPTS / "photo_rows.py").read_text(encoding="utf-8")
    assert [key for key in PHOTO_SUMMARY_KEYS if f"`{key}`" not in photos] == []
    assert [key for key in PHOTO_SUMMARY_KEYS if f'"{key}"' not in source] == []


def test_city_pack_delivery_gate_requires_clean_merge():
    """U2: Teslimat onay alanlarina ve AI onayina yalniz merge_package bakar; faz 6 kapisi onun temiz cikmasini ister."""
    assemble = _section(_skill_text("city-pack"), "### 6. assemble")
    gate = next((line for line in assemble.splitlines() if line.startswith("- Kapı:")), "")
    assert "`merge_package` çıkış 0" in gate and "birlestir_rapor.json" in gate, gate
    named = ("quote_miss_list", "editorial_status", "source_not_in_draft", "claim_source_not_in_owner")
    assert [name for name in named if f"`{name}`" not in gate] == [], gate
    source = (sc.SCRIPTS / "merge_package.py").read_text(encoding="utf-8")
    assert [name for name in named if f'"{name}"' not in source] == [], "merge_package bu adla yazmiyor"


def test_city_pack_long_jobs_are_split_and_budgeted():
    """B14: uzun secim/kesif isi paralel ajanlara bolunur, her ajana sure/adim butcesi; mekanik is dusuk ayarda. U5
    inceleme notu: secim ve kesif ajaninin ayari da yazili (pilotun asil sorunu en yuksek ayarda 85+ dk'lik secim)."""
    text = _skill_text("city-pack")
    for heading in ("### 2. sources", "### 4. places", "### 5. photos"):
        part = _section(text, heading).casefold()
        assert "bütçe" in part and "paralel" in part, heading
    assert "düşük düşünme ayarında" in _section(text, "## Değişmez kurallar"), "genel kural (B14) yok"
    rule = _starting(_section(text, "## Değişmez kurallar"), "12. ")
    assert "kaynak keşfi ve mekân seçimi orta ayarda" in rule, rule


# --- city-pack SKILL.md: U5 incelemesinin bulgulari (2 ORTA, 5 DUSUK, 3 not) ---

REOPENED = "places"  # teslimden (17:45) sonra 30 dk yeniden acilan faz
REOPEN_CLOCKS = ("18:00:00", "18:30:00")
SESSION_CLOCKS = ("10:00:30", "10:10:00", "11:00:00", "13:00:00", "15:00:00", "17:10:00", "17:40:00", "18:10:00")
WINDOW_GAP = "pencere farkı: <faz>"  # run_log: manifest suresi phase_log suresini tutmayan faz
EXIT_TWO_GUARD = re.compile(r"^if \(\$LASTEXITCODE -ge 2\) \{ throw '[^'$`\"]+' \}$")


def _containing(text: str, phrase: str) -> str:
    """`phrase`'i iceren ilk satir (bas/son bosluksuz); yoksa bos dize (assert mesajinda gorunur)."""
    return next((line.strip() for line in text.splitlines() if phrase in line), "")


def _starting(text: str, prefix: str) -> str:
    """`prefix` ile baslayan ilk satir (bas bosluklari atilmis); yoksa bos dize."""
    return next((line.strip() for line in text.splitlines() if line.strip().startswith(prefix)), "")


def _quiet(capsys, main, *argv) -> tuple[int, dict]:
    """Toolkit main()'i (tek satir JSON basar): (cikis, son satirin JSON'u)."""
    code = main([str(arg) for arg in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    return code, json.loads(lines[-1]) if lines else {}


def test_city_pack_venue_merge_ignores_empty_qid():
    """U5 inceleme 1 (ORTA): secim dosyalari birlesirken tekrar `slug` ya da DOLU `qid` ile aranir. Resmi siteden
    tamamlanan gruplarda qid bostur (pilot: 120 mekanin 61'i); bos qid tekrar sayilirsa ilki disindakiler sessizce
    duser ve ancak sonradan '>=92' kapisinda gorulur."""
    rule = _containing(_section(_skill_text("city-pack"), "### 4. places"), "ikinci kez gelirse atılır")
    assert "dolu `qid`" in rule and "boş `qid`" in rule, rule


def _reopened_city(tmp_path: Path) -> tuple[Path, Path, dict]:
    """Yedi faz bitti ve teslim edildi; places SKILL.md'deki kuralla yeniden acildi: phase_log'da ikinci pencere,
    manifest'te done, ust duzey phase ve started_at ayni, yalniz ended_at guncel. Doner: (manifest, log, icerik)."""
    work = tmp_path / "work"
    (work / "paket").mkdir(parents=True)
    marks = [{"phase": name, "event": event, "ts": f"{rh.DAY}{rh.TIMES[name][index]}Z"}
             for name in rh.PHASES for index, event in enumerate(phase_usage.EVENTS)]
    reopen = [{"phase": REOPENED, "event": event, "ts": f"{rh.DAY}{clock}Z"}
              for event, clock in zip(phase_usage.EVENTS, REOPEN_CLOCKS)]
    log = rh.write_jsonl(work / "_is" / "phase_log.jsonl", [*marks, *reopen])
    phases = {name: rh.phase_state(name) for name in rh.PHASES}
    reopened = {**phases[REOPENED], "ended_at": f"{rh.DAY}{REOPEN_CLOCKS[1]}Z"}
    data = rh.manifest(tmp_path, phases={**phases, REOPENED: reopened},
                       delivered={"at": f"{rh.DAY}{rh.TIMES['deliver'][1]}Z", "xlsx_sha256": "0" * 64})
    return rh.write_json(work / "manifest.json", data), log, data


def test_city_pack_reopened_phase_rule_matches_tools(tmp_path, capsys):
    """U5 inceleme 2 (ORTA) ve 3: kurala gore yeniden acilan faz manifest_check'ten temiz gecer, ust duzey phase'i geri
    almak faz_sirasi bulgusudur. run_log'un gap'leri `editoryal skor yok` ve `pencere farki: <faz>` (manifest faz basina
    tek pencere tutar, phase_log pencereleri toplar); SKILL.md ikisini de beklenen sayar, open_items'a yazdirmaz. Faz
    basinda da manifest yazilir (phase, running): 'basinda okunur, sonunda guncellenir' celiskiliydi. run_log cok
    pencereli fazda phase_log suresini kullanirsa gap kalkar ve bu test kirmizi olur: SKILL.md notu da kalkmali."""
    manifest, log, data = _reopened_city(tmp_path)
    assert _quiet(capsys, manifest_check.main, manifest)[0] == 0
    rolled_back = rh.write_json(tmp_path / "geri" / "manifest.json", {**data, "phase": REOPENED})
    code, summary = _quiet(capsys, manifest_check.main, rolled_back, "--phase-log", log)
    assert code == 1 and "faz_sirasi" in summary.get("by_code", {}), summary
    work = manifest.parent
    session = rh.session_file(tmp_path / "oturum" / "s.jsonl", "09:00:00", "19:00:00",
                              tuple(rh.assistant(clock, f"m{i}", 5) for i, clock in enumerate(SESSION_CLOCKS)))
    usage = rh.usage_report(capsys, session, log, work / "_is" / "token_s.csv")
    validation = rh.write_json(work / "_is" / "validation_emit.json", rh.validation_report())
    code, summary = rh.run(capsys, "--manifest", manifest, "--session", session, "--usage", usage,
                           "--validation", validation, "--claim-audit", rh.audit_dir(work),
                           "--photo-review", rh.review_dir(work), "--out", work / "RUN_LOG.csv")
    gaps = sorted(gap.split(" (")[0] for gap in summary["gaps"])
    assert (code, gaps) == (1, sorted([EXPECTED_DELIVER_GAP, WINDOW_GAP.replace("<faz>", REOPENED)])), summary
    text = _skill_text("city-pack")
    reopen = _containing(_section(text, "## Manifest ve ölçüm"), "Yeniden açılan faz")
    named = ("üst düzey `phase`", "`started_at`", "değişmez", f"`{WINDOW_GAP}`", "`open_items`")
    assert [word for word in named if word not in reopen] == [], reopen
    exit_rule = _containing(_section(text, "### 7. deliver"), "kural 4'ün istisnası")
    assert f"`{WINDOW_GAP}`" in exit_rule and "`open_items`" in exit_rule, exit_rule
    assert "Her faz başında okunur, sonunda güncellenir" not in text, "faz basinda da yazilir (phase, running)"


def test_city_pack_extra_photo_round_searches_only_new_entries():
    """U5 inceleme 4: plan-from-xlsx ara Excel'deki butun kayitlari yazar, suzme secenegi yok. Ek tur yalniz ana
    foto\\venues.jsonl'de olmayan entry_id'leri arar (pilot: 120 yerine 16 satir; yoksa her mekan yeniden aranir,
    onizlenir, inceletilir), yeni kayitlar once KUR'dan gecer, commons_search onbellegi ana turunki kalir."""
    plan = sc.subcommands(sc.load_parser("photo_candidates"))["plan-from-xlsx"]
    assert set(sc.option_actions([plan])) == {"-h", "--help", "--out"}, "plan-from-xlsx suzuyorsa SKILL.md anlatmali"
    caches = {PureWindowsPath(ns.cache_dir) for c, ns in _parsed("city-pack") if c.script == "commons_search"}
    assert caches == {PureWindowsPath(VARIABLES_BY_SKILL["city-pack"]["WORK"], "_is", "foto", "cache")}, caches
    extra = _containing(_section(_skill_text("city-pack"), "### 5. photos"), "Ek tur (A12")
    needed = (r"ana `_is\foto\venues.jsonl`", "`entry_id`", "KUR", "`commons_search --cache-dir`", r"`_is\foto\cache\`")
    assert [word for word in needed if word not in extra] == [], extra


def test_city_pack_parallel_photo_work_keeps_phase_windows_apart():
    """U5 inceleme 5: kural 12 foto turlarini mekan yazimiyla paralel yurutur. Faz pencereleri cakisamaz (phase_usage
    report 'overlap' ile cikis 2, RUN_LOG uretilemez; manifest_check log_penceresi): places bitmeden yapilan foto isi
    places penceresinde sayilir, `mark photos start` places kapaninca yazilir."""
    entries = [{"phase": phase, "event": event, "ts": phase_usage.parse_ts(f"{rh.DAY}{clock}Z")}
               for phase, event, clock in (("places", "start", "12:00:00"), ("photos", "start", "12:30:00"),
                                           ("places", "end", "13:00:00"))]
    with pytest.raises(phase_usage.UsageError, match="overlap"):
        phase_usage.check_overlaps(phase_usage.build_windows(entries))
    rule = _starting(_section(_skill_text("city-pack"), "## Değişmez kurallar"), "12. ")
    assert "foto turları mekân yazımıyla paralel" in rule, rule
    assert "places penceresinde" in rule and "`mark photos start` places kapanınca" in rule, rule


def test_city_pack_stops_chain_when_photo_rows_fails():
    """U5 inceleme 6: photo_rows cikis 2'de (kullanim/girdi hatasi) dosya yazmaz. Teslim zinciri her duzeltmeden sonra
    bastan calistigi icin onceki kosunun indirme_plani.json'u ve foto parcalari yerinde kalir (eski planla indirme ve
    silme, eski satirlarla KUR). Her photo_rows satirindan hemen sonra cikis 2 zinciri durdurur; 1 (atilan kare)
    gecer."""
    lines = [line.strip() for line in _section(_skill_text("city-pack"), "### 5. photos").splitlines()]
    calls = [index for index, line in enumerate(lines) if line.startswith(r"& $PY $TK\photo_rows.py ")]
    assert [lines[index].split()[3] for index in calls] == ["plan", "rows"], calls
    assert [lines[index + 1] for index in calls if not EXIT_TWO_GUARD.match(lines[index + 1])] == []


def test_city_pack_second_audit_round_keeps_the_first():
    """U5 inceleme 7: tamamlama turunda eklenen kartlar adim 4'e doner. Ikinci tur ayni adla yazilirsa ilkini ezer:
    run_log denetim oranini yalniz son turdan hesaplar, 'her satir en az bir kez denetlendi' dosyadan sayilamaz. Ikinci
    turun dosyalari ayri adla ve run_log'un okudugu desende; kapanis iki turun karar dosyalarindan sayilir."""
    loop = _section(_skill_text("city-pack"), "## Standart kalite döngüsü")
    documented = set(re.findall(r"<parça>[^`\s\\]*iddia[^`\s\\]*\.jsonl", loop))  # iddia dosyasi adlari
    outside = [n for n in documented if not any(fnmatch.fnmatch(sc.PLACEHOLDER.sub("x1", n), glob)
                                                for glob in run_log_inputs.AUDIT_GLOBS)]
    assert "<parça>_iddia.jsonl" in documented and outside == [], (documented, outside)
    back = _containing(loop, "Eklenen kartlar adım 4'e döner")
    second = re.findall(r"<parça>(-[a-z]+)_iddia\.jsonl", back)
    assert second, f"ikinci denetim turunun ayri iddia dosyasi yok: {back}"
    closing = _containing(loop, "**Kapanış:**")
    assert [s for s in ("", *second) if f"<parça>{s}_karar.jsonl" not in closing] == [], closing


def test_city_pack_environment_file_holds_literal_values():
    """U5 inceleme notu: ortam.ps1 degerleri tek tirnakli (BBOX'un virgulu dizi yapmasin). Tek tirnak icinde $ROOT
    acilmaz (`$PY = '$ROOT\\...'` bozuk): ornek degerlerde $ yok ve metin her degerin tam yol oldugunu soyler."""
    line = _containing(_skill_text("city-pack"), "ortam.ps1` dosyasına")
    examples = re.findall(r"`\$(\w+) = '([^'`]*)'`", line)
    assert examples and [name for name, value in examples if "$" in value] == [], examples
    assert "tam yol" in line and "açılmaz" in line, line


def test_city_pack_preview_widths_follow_toolkit():
    """U5 inceleme notu: photo_previews --width STANDARD_WIDTHS'ten birini kabul eder (20-3840 arasi 11 deger). SKILL.md
    listesi bunun alt kumesi; tamami degilse 'ör.' ile verilir (yoksa kapali liste gibi okunur, 250 de gecer)."""
    found = re.search(r"standart genişlik \((?P<example>ör\. )?(?P<widths>\d+(?:/\d+)+)",
                      _section(_skill_text("city-pack"), "### 5. photos"))
    assert found, "onizleme genislik listesi yok"
    widths = tuple(int(width) for width in found["widths"].split("/"))
    assert set(widths) <= set(photo_previews.STANDARD_WIDTHS), widths
    assert found["example"] or widths == tuple(photo_previews.STANDARD_WIDTHS), found.group()


# --- city-pack SKILL.md: B16 hitap olcumu kapilarda (skill-son-hal-4, W1'in --address-standard'i) ---

HITAP_FILE = re.compile(r"`_is\\yazar\\hitap\.txt`'ye `(?P<standard>[a-z]+)` yazılır")  # intake karari
ADDRESS_FLAG = re.compile(r"--address-standard\s+(?P<standard>[a-z]+)")
ADDRESS_GATES = ("### 3. answers", "### 4. places", "### 6. assemble")  # iki faz kapisi + teslim oncesi kalite kapisi
KUR_HEADING = "## KUR bloğu: birleştir → kur → kapılar"
MIXED_ADDRESS = MappingProxyType({  # her standartta bulgu (ayni kayitta 'siz' ve 'sen'); buton metni emir, bulgu degil
    "Yanıtlar": [{"_row": 8, "entry_id": "x:a", "title": "Kayıt",
                  "summary": "Kayıttan sonra randevunuzu alın; kartı da yanında götür."}],
    "Bağlantılar": [{"_row": 8, "action_id": "x:action:a-1", "entry_id": "x:a", "label": "Başvur",
                     "url": "https://example.org/basvur"}]})


def test_city_pack_gates_count_direct_address_with_the_intake_standard():
    """B16 + W1: text_quality hitabi varsayilan 'off'ta yalniz olcer, bulgu saymaz. KUR'daki (answers ve places kapisi
    'KUR temiz' ister) ve faz 6'daki (teslim oncesi) her text_quality cagrisi ve metindeki her --address-standard
    anmasi intake'te hitap.txt'ye yazilan standardi verir: standart degisirse intake satiri ve kapilar birlikte degisir.
    Uc kapi hitap bulgusunu anar; KUR'un text_quality maddesi bulgunun yerini (address.findings: sayfa, kimlik),
    duzelteni (yazar, editor) ve buton metninin (Baglantilar.label) bulgu olmadigini soyler."""
    text = _skill_text("city-pack")
    decided = HITAP_FILE.search(_section(text, "### 1. intake"))
    assert decided and decided["standard"] in address_forms.STANDARDS and decided["standard"] != "off", decided
    standard = decided["standard"]
    calls = [(c, ns) for c, ns in _parsed("city-pack") if c.script == "text_quality"]
    homes = [heading for heading in (KUR_HEADING, "### 6. assemble")
             if any(c.text in _section(text, heading) for c, _ in calls)]
    assert homes == [KUR_HEADING, "### 6. assemble"], [c.id for c, _ in calls]
    assert [c.id for c, ns in calls if ns.address_standard != standard] == [], [c.text for c, _ in calls]
    named = {match["standard"] for match in ADDRESS_FLAG.finditer(text)}
    assert named == {standard}, f"metindeki --address-standard {sorted(named)}, intake: {standard}"
    gates = {heading: _starting(_section(text, heading), "- Kapı:") for heading in ADDRESS_GATES}
    assert [heading for heading, gate in gates.items() if "hitap bulgusu 0" not in gate] == [], gates
    rule = _starting(_section(text, KUR_HEADING), "- `text_quality`:")
    needed = ("`hitap.txt`", "`address.findings`", "`sheet`", "`id`", "yazar", "editör", "`Bağlantılar.label`",
              "bulgu değildir")
    assert [phrase for phrase in needed if phrase not in rule] == [], rule
    off = text_quality.analyze(MIXED_ADDRESS)
    on = text_quality.analyze(MIXED_ADDRESS, address_standard=standard)
    assert (off["summary"]["address"]["findings"], on["summary"]["address"]["findings"]) == (0, 1)
    assert on["summary"]["address"]["labels"]["sen"] == 1 and {"sheet", "id"} <= set(on["address"]["findings"][0])
