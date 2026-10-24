"""run_log.py testleri: sahte manifest, oturum kaydi, phase_usage CSV'si, alt ajan kayitlari, validate_all ve
editorial_score ciktilari, iddia denetimi ve gorsel inceleme kayitlariyla sehir basina RUN_LOG.csv (IYILESTIRME D).
Ortak yardimcilar run_log_helpers.py'de; --exclude-workflow (A9) ve dosya duzeni testleri test_run_log_exclude.py'de."""
from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

import editorial_score
import phase_usage
import run_log
import run_log_inputs
from run_log_helpers import (DAY, PHASES, PHOTO_GAPS, TIMES, agent_file, audit_dir, full_inputs, manifest, phase_log,
                             phase_state, quality_args, read_rows, rows_by_phase, run, session_file, snapshot,
                             split_city, usage_report, write_json, write_jsonl, write_usage)
from run_log_helpers import work  # noqa: F401  pytest fixture'i

COLUMNS =["sehir", "faz", "baslangic", "bitis", "sure_dk", "toplam_girdi", "onbellek_disi_girdi", "cikti",
           "ajan_sayisi", "kapi_sonucu", "yapi_hatasi", "medya_hatasi", "asgari_eksik", "editoryal_yuzde", "karar",
           "kart", "mekan", "foto", "durum", "model_karisimi", "not", "denetim_hata_orani", "reddedilen_foto"]
QUALITY_COLUMNS = ["yapi_hatasi", "medya_hatasi", "asgari_eksik", "editoryal_yuzde", "karar", "kart", "mekan", "foto",
                   "denetim_hata_orani", "reddedilen_foto"]
MEASURED_COLUMNS = ["toplam_girdi", "onbellek_disi_girdi", "cikti", "ajan_sayisi", "model_karisimi"]
NO_SESSION = "oturum kaydı yok: {} (fazın {} anı hiçbir --session kaydında yok)"


# ---------- tam olcum ----------

def test_full_run_phase_rows_outside_row_and_city_summary(tmp_path, work, capsys):
    code, summary = run(capsys, *full_inputs(tmp_path, work))
    assert code == 0 and summary["status"] == "ok" and summary["gaps"] == []  # kalite (karar) cikis kodunu etkilemez
    out = work / "RUN_LOG.csv"
    assert summary["out"] == str(out)
    rows = read_rows(out)
    assert [r["faz"] for r in rows] == [*PHASES, "(faz dışı)", "ozet"]
    assert {r["sehir"] for r in rows} == {"testkent"}
    by = {r["faz"]: r for r in rows}
    intake = by["intake"]
    assert (intake["baslangic"], intake["bitis"]) == ("2026-10-22T10:00:00Z", "2026-10-22T10:01:00Z")
    assert [by[n]["sure_dk"] for n in PHASES] == ["1.0", "18.0", "120.0", "90.0", "180.0", "30.0", "15.0"]
    assert [by[n]["toplam_girdi"] for n in PHASES] == [str(1110 * k) for k in range(1, 8)]
    assert [by[n]["onbellek_disi_girdi"] for n in PHASES] == [str(110 * k) for k in range(1, 8)]
    assert [by[n]["cikti"] for n in PHASES] == [str(50 * k) for k in range(1, 8)]
    assert [by[n]["kapi_sonucu"] for n in PHASES] == [  # temiz olmayan kapilar adiyla (script=cikis)
        "temiz (1 kapı)", "bulgu (1 kapı): kapi-0=1", "bulgu (2 kapı): kapi-0=1; kapi-1=1", "bulgu (1 kapı): kapi-0=1",
        "temiz (1 kapı)", "bulgu (1 kapı): kapi-0=1", "kapı yok"]
    assert {by[n]["durum"] for n in PHASES} == {"bitti"}
    assert all(by[n][col] == "" for n in PHASES for col in [*QUALITY_COLUMNS, "not"])  # kalite yalniz ozette
    outside = by["(faz dışı)"]
    assert (outside["toplam_girdi"], outside["onbellek_disi_girdi"], outside["cikti"]) == ("555", "55", "25")
    assert outside["baslangic"] == outside["bitis"] == outside["sure_dk"] == outside["kapi_sonucu"] == ""
    total = by["ozet"]
    assert (total["baslangic"], total["bitis"], total["sure_dk"]) == ("2026-10-22T10:00:00Z", "2026-10-22T17:45:00Z",
                                                                       "454.0")
    assert (total["toplam_girdi"], total["onbellek_disi_girdi"], total["cikti"]) == ("31635", "3135", "1425")
    assert total["kapi_sonucu"] == "bulgu (7 kapı; 5 temiz değil)"
    assert (total["yapi_hatasi"], total["medya_hatasi"], total["asgari_eksik"]) == ("0", "0", "foto 156/187; kapak 0/6")
    assert (total["editoryal_yuzde"], total["karar"]) == ("48", "DÜZELTME GEREKLİ")
    assert (total["kart"], total["mekan"], total["foto"]) == ("289", "104", "201")
    assert (total["denetim_hata_orani"], total["reddedilen_foto"]) == ("25.0 (2/8)", "2/5; ikinci göz 1/2")
    assert (total["durum"], total["not"]) == ("bitti 7/7", "ilk deneme")


def test_agents_counted_by_first_timestamp_from_session_folder_including_workflows(tmp_path, work, capsys):
    _, summary = run(capsys, *full_inputs(tmp_path, work))  # --subagents yok: <oturum>\subagents varsayilan
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert [by[n]["ajan_sayisi"] for n in PHASES] == ["0", "1", "2", "3", "0", "0", "0"]
    assert (by["(faz dışı)"]["ajan_sayisi"], by["ozet"]["ajan_sayisi"]) == ("2", "8")
    assert by["sources"]["model_karisimi"] == "sonnet 1"
    assert by["answers"]["model_karisimi"] == "opus 1; sonnet 1"            # <synthetic> atlanir; meta yedek
    assert by["places"]["model_karisimi"] == "haiku 1; opus 1; sonnet 1"
    assert by["(faz dışı)"]["model_karisimi"] == "? 1; sonnet 1"
    assert by["ozet"]["model_karisimi"] == "sonnet 4; opus 2; ? 1; haiku 1"
    assert by["intake"]["model_karisimi"] == ""
    assert (summary["agents"], summary["agents_untimed"], summary["excluded_agents"]) == (8, 1, None)
    assert summary["agents_by_workflow"] == {"(doğrudan)": {"sources": 1, "answers": 2, "(faz dışı)": 2, "places": 1},
                                             "wf_test-1": {"places": 2}}


def test_header_order_utf8_bom_and_turkish_text(tmp_path, work, capsys):
    run(capsys, *full_inputs(tmp_path, work))
    raw = (work / "RUN_LOG.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")  # Excel Turkce karakterleri dogru acsin
    assert raw[3:].decode("utf-8").splitlines()[0].split(",") == COLUMNS == list(run_log.COLUMNS)
    assert "DÜZELTME GEREKLİ" in raw.decode("utf-8-sig")
    assert set(run_log_inputs.USAGE_COLUMNS) <= set(phase_usage.COLUMNS)  # phase_usage sozlesmesi


def test_summary_json_single_line_with_totals(tmp_path, work, capsys):
    _, summary = run(capsys, *full_inputs(tmp_path, work))
    assert (summary["tool"], summary["city"], summary["phases_done"]) == ("run_log", "testkent", "7/7")
    assert summary["sessions"] == ["sess.jsonl 2026-10-22T09:00:00Z..2026-10-22T18:00:00Z"]
    assert (summary["total_input"], summary["uncached_input"], summary["output"]) == (31635, 3135, 1425)
    assert summary["outside_pct"] == round(100 * 555 / 31635, 2)
    assert (summary["structure_errors"], summary["media_errors"]) == (0, 0)
    assert (summary["minimum_gaps"], summary["editorial_percent"], summary["decision"]) == (
        "foto 156/187; kapak 0/6", 48, "DÜZELTME GEREKLİ")
    assert (summary["audit_error_pct"], summary["photos_rejected"]) == (25.0, "2/5; ikinci göz 1/2")
    assert summary["gap_count"] == 0


def test_phase_order_and_statuses_match_manifest_schema():
    schema = Path(__file__).resolve().parents[2] / "city-pack" / "references" / "manifest.schema.json"
    if not schema.is_file():
        pytest.skip(f"şema yok: {schema}")
    defs = json.loads(schema.read_text(encoding="utf-8"))["$defs"]
    assert list(run_log.PHASES) == defs["phase_name"]["enum"]
    assert set(run_log.STATUS_TR) == set(defs["phase_state"]["properties"]["status"]["enum"])


# ---------- eksik olcum (cikis 1) ----------

def test_only_manifest_leaves_unmeasured_cells_blank_and_exits_1(tmp_path, work, capsys):
    m = write_json(work / "manifest.json", manifest(tmp_path))
    code, summary = run(capsys, "--manifest", m)
    assert code == 1 and summary["status"] == "eksik"
    joined = " | ".join(summary["gaps"])
    for flag in ("--session", "--usage", "--subagents", "--validation", "--score", "--claim-audit", "--photo-review"):
        assert flag in joined
    rows = read_rows(work / "RUN_LOG.csv")
    for row in rows:  # olculmeyen hucre 0 degil, bos
        assert [row[c] for c in MEASURED_COLUMNS] == [""] * len(MEASURED_COLUMNS)
    total = rows[-1]
    assert [total[c] for c in QUALITY_COLUMNS] == [""] * len(QUALITY_COLUMNS)
    assert (total["sure_dk"], total["durum"], rows[0]["kapi_sonucu"]) == ("454.0", "bitti 7/7", "temiz (1 kapı)")
    assert (summary["total_input"], summary["agents"], summary["decision"]) == (None, None, None)
    assert (summary["audit_error_pct"], summary["photos_rejected"], summary["sessions"]) == (None, None, None)


def test_unfinished_run_lists_open_phases_and_open_window_takes_agents(tmp_path, work, capsys):
    phases = {n: phase_state(n) for n in PHASES[:4]}
    phases["photos"] = phase_state("photos", status="running", end=False)
    phases["assemble"] = {"status": "pending"}
    m = write_json(work / "manifest.json", manifest(tmp_path, phases=phases, phase="photos"))
    sub = tmp_path / "s2"
    agent_file(sub, "late", f"{DAY}19:00:00.000Z", "claude-opus-4-5")
    code, summary = run(capsys, "--manifest", m, "--subagents", sub)
    assert code == 1
    for gap in ("faz bitmedi: photos (sürüyor)", "faz bitmedi: assemble (başlamadı)", "faz kaydı yok: deliver"):
        assert gap in summary["gaps"]
    by = rows_by_phase(work / "RUN_LOG.csv")
    photos = by["photos"]
    assert (photos["bitis"], photos["sure_dk"], photos["ajan_sayisi"], photos["durum"]) == ("", "", "1", "sürüyor")
    assert (by["assemble"]["durum"], by["assemble"]["kapi_sonucu"], by["assemble"]["ajan_sayisi"]) == (
        "başlamadı", "kapı yok", "0")
    assert (by["deliver"]["durum"], by["deliver"]["kapi_sonucu"], by["deliver"]["ajan_sayisi"]) == (
        "kayıt yok", "", "")  # pencere yok: ajan sayilamaz
    total = by["ozet"]
    assert (total["durum"], total["bitis"], total["sure_dk"]) == ("bitti 4/7", "2026-10-22T14:00:00Z", "229.0")
    assert summary["phases_done"] == "4/7"


def test_done_phase_without_end_does_not_swallow_later_agents(tmp_path, work, capsys):
    data = manifest(tmp_path)
    data["phases"]["deliver"].pop("ended_at")  # bitti ama bitis yazilmamis: acik pencere sayilmaz
    m = write_json(work / "manifest.json", data)
    sub = tmp_path / "s"
    agent_file(sub, "teslim", f"{DAY}17:35:00.000Z", "claude-opus-4-5")
    agent_file(sub, "sonra", f"{DAY}19:00:00.000Z", "claude-opus-4-5")  # teslimden sonra: faz disi
    code, summary = run(capsys, "--manifest", m, "--subagents", sub)
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 1 and "zaman eksik: deliver (manifest started_at/ended_at)" in summary["gaps"]
    assert (by["deliver"]["ajan_sayisi"], by["(faz dışı)"]["ajan_sayisi"], by["assemble"]["ajan_sayisi"]) == (
        "", "2", "0")


def test_phase_not_marked_in_usage_is_a_gap(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    write_usage(work / "_is" / "token_fazlar.csv", {n: k for k, n in enumerate(PHASES[:-1], start=1)})
    code, summary = run(capsys, *args)
    assert code == 1 and summary["gaps"] == ["token satırı yok: deliver (phase_usage mark eksik)"]
    deliver = rows_by_phase(work / "RUN_LOG.csv")["deliver"]
    assert (deliver["toplam_girdi"], deliver["sure_dk"]) == ("", "15.0")


def test_manifest_window_differs_from_phase_log_window_is_a_gap(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    data = manifest(tmp_path)
    data["phases"]["sources"]["ended_at"] = f"{DAY}10:10:00Z"  # manifest 8 dk; phase_log (token) 18 dk
    write_json(work / "manifest.json", data)
    code, summary = run(capsys, *args)
    assert code == 1 and summary["gaps"] == [
        "pencere farkı: sources (manifest 8.0 dk, phase_log 18.0 dk; ajan/süre ve token farklı pencereden)"]


def test_validation_stdout_summary_accepted_but_counts_are_a_gap(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    path = work / "_is" / "validation_emit.json"
    write_json(path, json.loads(path.read_text(encoding="utf-8"))["summary"])  # yalniz tek satir ozet kaydedilmis
    code, summary = run(capsys, *args)
    assert code == 1 and any("validate_all --out" in gap for gap in summary["gaps"])
    total = read_rows(work / "RUN_LOG.csv")[-1]
    assert (total["yapi_hatasi"], total["medya_hatasi"], total["asgari_eksik"]) == ("0", "0", "foto 156/187; kapak 0/6")
    assert total["kart"] == total["mekan"] == total["foto"] == ""


def test_empty_claim_audit_is_a_gap_not_zero(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    audit_dir(work, results=[])
    code, summary = run(capsys, *args)
    assert code == 1 and summary["gaps"] == ["denetim kaydı boş (--claim-audit: iddia satırı yok)"]
    assert read_rows(work / "RUN_LOG.csv")[-1]["denetim_hata_orani"] == "" and summary["audit_error_pct"] is None


# ---------- oturumlar: eksik oturum 0 degil bos ----------

def test_split_city_with_one_session_missing_leaves_blank_cells_and_exits_1(tmp_path, work, capsys):
    city = split_city(tmp_path, capsys)
    code, summary = run(capsys, *quality_args(tmp_path, work), "--session", city["A"], "--usage", city["uA"])
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 1 and summary["status"] == "eksik"
    assert NO_SESSION.format("places", "bitiş") in summary["gaps"]  # A'da basladi, sonu verilmeyen B'de: eksik sayim
    for name in PHASES[4:]:
        assert NO_SESSION.format(name, "başlangıç ve bitiş") in summary["gaps"]
    for name in PHASES[3:]:
        assert [by[name][c] for c in MEASURED_COLUMNS] == [""] * len(MEASURED_COLUMNS), name
    assert (by["intake"]["toplam_girdi"], by["answers"]["toplam_girdi"], by["answers"]["ajan_sayisi"]) == (
        "5", "5", "0")
    for name in ("(faz dışı)", "ozet"):  # eksik oturumla sehir toplami yanlis olur: bos
        assert [by[name][c] for c in MEASURED_COLUMNS] == [""] * len(MEASURED_COLUMNS), name
    assert (summary["total_input"], summary["outside_pct"], summary["agents"]) == (None, None, None)


def test_split_city_with_both_sessions_is_complete(tmp_path, work, capsys):
    city = split_city(tmp_path, capsys)
    code, summary = run(capsys, *quality_args(tmp_path, work), "--session", city["A"], "--session", city["B"],
                        "--usage", city["uA"], "--usage", city["uB"])
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 0 and summary["gaps"] == []  # sifir satirlar iki raporda da ayni: ayni oturum sayilmaz
    assert (by["places"]["toplam_girdi"], by["places"]["ajan_sayisi"], by["places"]["model_karisimi"]) == (
        "13", "1", "opus 1")  # iki oturumun places token'lari toplanir; B'nin alt ajani <B>\subagents'tan
    assert (by["ozet"]["toplam_girdi"], by["ozet"]["ajan_sayisi"]) == ("49", "1")


def test_zero_tokens_in_a_long_done_phase_is_a_gap_without_session(tmp_path, work, capsys):
    city = split_city(tmp_path, capsys)
    code, summary = run(capsys, *quality_args(tmp_path, work), "--usage", city["uA"])
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 1
    assert "oturum kaydı yok: photos (180.0 dk süren fazda bütün --usage raporlarında token 0; o oturumun raporu " \
           "verilmemiş)" in summary["gaps"]
    assert any(gap.startswith("oturum kapsamı denetlenmedi") for gap in summary["gaps"])  # places eksigi gorulemez
    assert by["photos"]["toplam_girdi"] == by["deliver"]["toplam_girdi"] == by["ozet"]["toplam_girdi"] == ""
    assert (by["intake"]["toplam_girdi"], by["places"]["toplam_girdi"]) == ("5", "5")


def test_two_sessions_with_one_usage_report_is_a_gap(tmp_path, work, capsys):
    city = split_city(tmp_path, capsys)
    code, summary = run(capsys, *quality_args(tmp_path, work), "--session", city["A"], "--session", city["B"],
                        "--usage", city["uA"])
    assert code == 1 and "rapor sayısı tutmuyor: 2 oturum, 1 --usage (oturum başına bir rapor)" in summary["gaps"]
    assert any(gap.startswith("oturum kaydı yok: photos (180.0 dk") for gap in summary["gaps"])


def test_short_phase_without_tokens_is_a_measured_zero(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    data = manifest(tmp_path)
    data["phases"]["deliver"]["ended_at"] = f"{DAY}17:30:30Z"  # pilotta assemble/deliver 1 sn surdu
    write_json(work / "manifest.json", data)
    write_usage(work / "_is" / "token_fazlar.csv", {**{n: k for k, n in enumerate(PHASES[:-1], start=1)}, "deliver": 0},
                {"deliver": 30.0})
    code, summary = run(capsys, *args)
    deliver = rows_by_phase(work / "RUN_LOG.csv")["deliver"]
    assert code == 0 and (deliver["toplam_girdi"], deliver["sure_dk"]) == ("0", "0.5")


@pytest.mark.parametrize("make, needle", [
    (lambda d: d / "yok.jsonl", "yok.jsonl"),
    (lambda d: write_jsonl(d / "bos.jsonl", [{"type": "user"}, {"tarih": "dün"}]), "zaman damgası"),
    (lambda d: d / "oturum" / "sess.jsonl", "iki kez"),  # ayni oturum iki kez
])
def test_unusable_or_repeated_session_is_refused(tmp_path, work, capsys, make, needle):
    args = full_inputs(tmp_path, work)
    code, summary = run(capsys, *args, "--session", make(tmp_path))
    assert code == 2 and needle in summary["error"] and not (work / "RUN_LOG.csv").exists()


# ---------- birden cok oturum raporu, ek faz, olculemeyen skor ----------

def test_usage_reports_of_two_sessions_are_summed(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    write_usage(work / "_is" / "token_fazlar.csv", {"intake": 1, "sources": 2, "answers": 3})
    second = write_usage(work / "_is" / "token_fazlar_2.csv",
                         {"answers": 1, "places": 4, "photos": 5, "assemble": 6, "deliver": 7})
    other = session_file(tmp_path / "oturum2.jsonl", "12:00:00", "18:00:00")
    code, summary = run(capsys, *args, "--session", other, "--usage", second)
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert code == 0
    assert (by["answers"]["toplam_girdi"], by["answers"]["sure_dk"]) == (str(1110 * 4), "120.0")
    assert by["(faz dışı)"]["toplam_girdi"] == str(555 * 2)
    assert by["ozet"]["toplam_girdi"] == str(1110 * 29 + 555 * 2) == str(summary["total_input"])


def test_two_session_reports_do_not_double_phase_duration(tmp_path, work, capsys):
    m = write_json(work / "manifest.json", manifest(tmp_path, phases={n: {"status": "done"} for n in PHASES}))
    first = write_usage(work / "_is" / "u1.csv", {"intake": 1, "sources": 2, "answers": 3})
    second = write_usage(work / "_is" / "u2.csv", {"answers": 1, "places": 4, "photos": 5, "assemble": 6, "deliver": 7})
    code, summary = run(capsys, "--manifest", m, "--usage", first, "--usage", second)
    by = rows_by_phase(work / "RUN_LOG.csv")  # manifest'te zaman yok: sure phase_log penceresinden, toplanmaz
    assert [by[n]["sure_dk"] for n in PHASES] == ["1.0", "18.0", "120.0", "90.0", "180.0", "30.0", "15.0"]
    assert (by["ozet"]["sure_dk"], by["answers"]["toplam_girdi"]) == ("454.0", str(1110 * 4))
    assert code == 1 and "zaman eksik: answers (manifest started_at/ended_at)" in summary["gaps"]


@pytest.mark.parametrize("copy", [
    lambda raw: raw,                                   # bayt bayt ayni
    lambda raw: b"\xef\xbb\xbf" + raw,                 # BOM eklenmis (PowerShell Out-File -Encoding utf8BOM)
    lambda raw: raw.replace(b"\r\n", b"\n"),           # satir sonu degismis
], ids=["kopya", "bom", "lf"])
def test_same_usage_report_twice_is_refused(tmp_path, work, capsys, copy):
    args = full_inputs(tmp_path, work)
    duplicate = work / "_is" / "kopya.csv"
    duplicate.write_bytes(copy((work / "_is" / "token_fazlar.csv").read_bytes()))
    code, summary = run(capsys, *args, "--usage", duplicate)
    assert code == 2 and "iki kez" in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


def test_interim_and_final_report_of_one_session_are_refused(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)  # son rapor: token_fazlar.csv (7 faz)
    interim = write_usage(work / "_is" / "token_fazlar_ara.csv", {"intake": 1, "sources": 2, "answers": 9})
    code, summary = run(capsys, *args, "--usage", interim)
    assert code == 2 and "aynı oturumun iki raporu" in summary["error"] and "'intake'" in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


def test_unknown_phase_in_usage_becomes_extra_row(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    write_usage(work / "_is" / "token_fazlar.csv", {**{n: k for k, n in enumerate(PHASES, start=1)}, "answers-ek": 2})
    code, _ = run(capsys, *args)
    rows = read_rows(work / "RUN_LOG.csv")
    assert code == 0
    assert [r["faz"] for r in rows] == [*PHASES, "answers-ek", "(faz dışı)", "ozet"]
    extra = rows[7]
    assert (extra["toplam_girdi"], extra["sure_dk"], extra["durum"], extra["kapi_sonucu"], extra["ajan_sayisi"]) == (
        "2220", "2.0", "kayıt yok", "", "")
    assert (rows[-1]["toplam_girdi"], rows[-1]["sure_dk"]) == ("33855", "454.0")  # ozet suresi: 7 faz


def test_unmeasured_editorial_percent_is_written_as_such(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    write_json(tmp_path / "denetim" / "score.json", editorial_score.build_report({"inventory_available": False}))
    code, summary = run(capsys, *args)
    total = read_rows(work / "RUN_LOG.csv")[-1]
    assert code == 0
    assert (total["editoryal_yuzde"], total["karar"]) == (editorial_score.NOT_MEASURED,
                                                          editorial_score.DECISION_EVIDENCE)
    assert summary["editorial_percent"] is None


def test_usage_with_bom_is_read(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    usage = work / "_is" / "token_fazlar.csv"
    usage.write_bytes(b"\xef\xbb\xbf" + usage.read_bytes())  # PowerShell Out-File -Encoding utf8BOM
    code, summary = run(capsys, *args)
    assert code == 0 and summary["total_input"] == 31635


def test_same_agent_in_two_folders_counted_once(tmp_path, work, capsys):
    m = write_json(work / "manifest.json", manifest(tmp_path))
    first, second = tmp_path / "s1", tmp_path / "s2"
    agent_file(first, "x1", f"{DAY}10:05:00.000Z", "claude-sonnet-4-6")
    agent_file(second, "x1", f"{DAY}10:05:00.000Z", "claude-sonnet-4-6")
    agent_file(second, "x2", f"{DAY}10:06:00.000Z", "claude-sonnet-4-6")
    _, summary = run(capsys, "--manifest", m, "--subagents", first, "--subagents", second)
    assert rows_by_phase(work / "RUN_LOG.csv")["sources"]["ajan_sayisi"] == "2" and summary["agents"] == 2


def test_reads_the_csv_phase_usage_actually_writes(tmp_path, work, capsys):
    def record(clock: str, mid: str, inp: int, cc: int, cr: int, out: int) -> dict:
        usage = {"input_tokens": inp, "cache_creation_input_tokens": cc, "cache_read_input_tokens": cr,
                 "output_tokens": out}
        return {"type": "assistant", "timestamp": f"{DAY}{clock}Z",
                "message": {"id": mid, "role": "assistant", "usage": usage}}

    later = tuple(record(TIMES[n][0][:5] + ":30.000", f"m-{n}", 1, 0, 0, 1) for n in PHASES[3:])
    session = session_file(tmp_path / "oturum" / "sess.jsonl", "10:00:00", "17:50:00", (
        record("10:00:30.000", "m1", 1, 10, 100, 5),   # intake
        record("10:05:00.000", "m2", 4, 0, 0, 1),      # sources
        record("10:25:00.000", "m3", 2, 20, 200, 7),   # sources ile answers arasi: faz disi
        record("11:00:00.000", "m4", 3, 30, 300, 9),   # answers
        record("11:00:01.000", "m4", 3, 30, 300, 9),   # akis tekrari: bir kez sayilir
        *later))                                       # places..deliver: birer kayit
    usage = usage_report(capsys, session, phase_log(tmp_path / "phase_log.jsonl"), work / "_is" / "token_fazlar.csv")
    m = write_json(work / "manifest.json", manifest(tmp_path))
    code, summary = run(capsys, "--manifest", m, "--session", session, "--usage", usage)
    by = rows_by_phase(work / "RUN_LOG.csv")
    assert (by["intake"]["toplam_girdi"], by["intake"]["onbellek_disi_girdi"], by["intake"]["cikti"]) == (
        "111", "11", "5")
    assert (by["sources"]["toplam_girdi"], by["answers"]["toplam_girdi"], by["(faz dışı)"]["toplam_girdi"]) == (
        "4", "333", "222")
    assert (summary["total_input"], summary["uncached_input"], summary["output"]) == (674, 74, 26)
    assert summary["agents"] == 0 and not any(gap.startswith("oturum kaydı yok") for gap in summary["gaps"])
    assert code == 1  # dogrulama, skor, denetim ve inceleme verilmedi


# ---------- yapi / kullanim hatalari (cikis 2) ----------

@pytest.mark.parametrize("edit, needle", [
    (lambda text: "faz,toplam\nintake,1\n", "phase_usage"),
    (lambda text: text.replace(",31635,", ",31636,"), "TOTAL"),
    (lambda text: text.replace(",1110,", ",abc,"), "total_input"),
    (lambda text: text + text.splitlines()[1] + "\n", "yineleniyor"),
])
def test_broken_usage_csv_is_refused(tmp_path, work, capsys, edit, needle):
    args = full_inputs(tmp_path, work)
    usage = work / "_is" / "token_fazlar.csv"
    usage.write_text(edit(usage.read_text(encoding="utf-8")), encoding="utf-8")
    code, summary = run(capsys, *args)
    assert code == 2 and needle in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("flag, name, needle", [("--usage", "yok.csv", "yok.csv"), ("--subagents", "yok", "subagents")])
def test_missing_usage_file_or_subagents_folder_is_refused(tmp_path, work, capsys, flag, name, needle):
    code, summary = run(capsys, *full_inputs(tmp_path, work), flag, tmp_path / name)
    assert code == 2 and needle in summary["error"] and not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("kind, payload, needle", [
    ("validation", {"summary": {"tool": "inventory"}}, "validate_all"),
    ("validation", {"tool": "validate_all", "error": "--tools gerekli"}, "çalışmamış"),
    ("validation", {"summary": {"tool": "validate_all", "structure": {"errors": "çok"}, "media": {"errors": 0},
                                "minimum_gaps": {}}}, "structure"),
    ("score", {"tool": "editorial_score", "editorial_percent": 100, "decision": "HAZIR"}, "karar"),
    ("score", {"tool": "baska", "decision": editorial_score.DECISION_READY}, "editorial_score"),
    ("score", {"tool": "editorial_score", "editorial_percent": 140, "decision": editorial_score.DECISION_READY},
     "editorial_percent"),
])
def test_foreign_or_hand_written_quality_inputs_are_refused(tmp_path, work, capsys, kind, payload, needle):
    args = full_inputs(tmp_path, work)
    target = work / "_is" / "validation_emit.json" if kind == "validation" else tmp_path / "denetim" / "score.json"
    write_json(target, payload)
    code, summary = run(capsys, *args)
    assert code == 2 and needle in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("flag, name, lines, needle", [
    ("--claim-audit", "x_iddia.jsonl", ['{"claim_id": "C-1"}'], "sonuç"),
    ("--claim-audit", "x_iddia.jsonl", ["{bozuk"], "JSON"),
    ("--claim-audit", "x_dogrulama.jsonl", ['{"sonuc": "dogru"}'], "sonuç"),  # dogrulayici kaydi denetim degil
    ("--photo-review", "review_x.jsonl", ['{"key": "k", "result": "belki"}'], "result"),
    ("--photo-review", "verify_x.jsonl", ['{"key": "k", "ok": "evet"}'], "result"),
])
def test_foreign_audit_or_review_records_are_refused(tmp_path, work, capsys, flag, name, lines, needle):
    args = full_inputs(tmp_path, work)
    bad = tmp_path / "yabanci" / name
    bad.parent.mkdir()
    bad.write_text("\n".join(lines) + "\n", encoding="utf-8")
    code, summary = run(capsys, *args, flag, bad)
    assert code == 2 and needle in summary["error"] and not (work / "RUN_LOG.csv").exists()


@pytest.mark.parametrize("flag", ["--claim-audit", "--photo-review"])
def test_audit_or_review_folder_without_its_files_is_refused(tmp_path, work, capsys, flag):
    args = full_inputs(tmp_path, work)
    folder = tmp_path / "bos_klasor"
    write_jsonl(folder / "selected_tur1.jsonl", [{"key": "k"}])
    code, summary = run(capsys, *args, flag, folder)
    assert code == 2 and "bos_klasor" in summary["error"]


@pytest.mark.parametrize("mutate, needle", [
    (lambda m: m.pop("city"), "city_id"),
    (lambda m: m["city"].update(city_id=""), "city_id"),
    (lambda m: m.update(phases=[]), "phases"),
    (lambda m: m["phases"]["sources"].update(status="bitti"), "status"),
    (lambda m: m["phases"]["sources"].update(started_at="dün"), "started_at"),
    (lambda m: m["phases"]["sources"].update(ended_at="2026-10-22T09:00:00Z"), "önce"),
    (lambda m: m["phases"]["answers"]["gates"][0].update(exit_code=3), "exit_code"),
    (lambda m: m["phases"]["answers"]["gates"][0].update(exit_code=[1]), "exit_code"),
    (lambda m: m["phases"]["answers"].update(gates={"x": 1}), "gates"),
])
def test_broken_manifest_is_refused(tmp_path, work, capsys, mutate, needle):
    data = manifest(tmp_path)
    mutate(data)
    code, summary = run(capsys, "--manifest", write_json(work / "manifest.json", data))
    assert code == 2 and needle in summary["error"]
    assert not (work / "RUN_LOG.csv").exists()


def test_unreadable_manifest_is_refused(work, capsys):
    code, summary = run(capsys, "--manifest", work / "yok.json")
    assert code == 2 and "yok.json" in summary["error"]
    bad = work / "bozuk.json"
    bad.write_text("{", encoding="utf-8")
    code, summary = run(capsys, "--manifest", bad)
    assert code == 2 and "JSON" in summary["error"]


def test_out_inside_package_is_refused(tmp_path, work, capsys):
    target = work / "paket" / "RUN_LOG.csv"
    code, summary = run(capsys, *full_inputs(tmp_path, work), "--out", target)
    assert code == 2 and "paket" in summary["error"] and not target.exists()


def test_out_cannot_overwrite_an_input(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    for victim in (work / "_is" / "token_fazlar.csv", tmp_path / "oturum" / "sess.jsonl",
                   work / "_is" / "denetim" / "konu_iddia.jsonl", work / "_is" / "phase_log.jsonl"):
        before = victim.read_bytes()
        code, summary = run(capsys, *args, "--out", victim)
        assert code == 2 and "girdi" in summary["error"] and victim.read_bytes() == before


def test_cli_help_and_missing_manifest_argument(capsys):
    assert run_log.main(["--help"]) == 0
    assert "usage:" in capsys.readouterr().out
    assert run_log.main([]) == 2
    capsys.readouterr()
    parsed = run_log.build_parser().parse_args(["--manifest", "m.json"])
    assert (parsed.usage, parsed.session, parsed.exclude_workflow, parsed.claim_audit) == (None, None, None, None)


# ---------- cikti guvenligi ----------

def test_custom_out_and_rerun_gives_identical_file(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    out = tmp_path / "rapor" / "RUN_LOG.csv"
    run(capsys, *args, "--out", out)
    first = out.read_bytes()
    run(capsys, *args, "--out", out)
    assert out.read_bytes() == first and not (work / "RUN_LOG.csv").exists()


def test_inputs_are_read_only_and_no_temp_files_remain(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    before = snapshot(tmp_path)
    run(capsys, *args)
    assert snapshot(tmp_path) == before and (work / "RUN_LOG.csv").is_file()


@pytest.mark.skipif(os.name != "nt", reason="Windows: acik dosyanin ustune yazilamaz (Excel'de acik RUN_LOG)")
def test_open_run_log_is_a_usage_error_and_old_file_is_kept(tmp_path, work, capsys):
    args = full_inputs(tmp_path, work)
    run(capsys, *args)
    out = work / "RUN_LOG.csv"
    old = out.read_bytes()
    with out.open("rb"):
        code, summary = run(capsys, *args)
    assert code == 2 and "açık olabilir" in summary["error"]
    assert out.read_bytes() == old
    assert sorted(p.name for p in work.iterdir() if p.is_file()) == ["RUN_LOG.csv", "manifest.json"]


# ---------- kucuk birimler ----------

@pytest.mark.parametrize("gates, text", [
    ((), "kapı yok"), ((("a", 0),), "temiz (1 kapı)"),
    ((("a", 0), ("claim_check", 1)), "bulgu (2 kapı): claim_check=1"),
    ((("x", 1), ("y" * 50, 2), ("z", 0)), "hata (3 kapı): x=1; " + "y" * 39 + "…=2")])
def test_gate_result_names_the_gates_that_were_not_clean(gates, text):
    assert run_log.gate_result([run_log.Gate(script, code) for script, code in gates]) == text


@pytest.mark.parametrize("codes, text", [
    ((), "kapı yok"), ((0, 0), "temiz (2 kapı)"), ((0, 1, 2), "hata (3 kapı; 2 temiz değil)")])
def test_gate_total(codes, text):
    assert run_log.gate_total([run_log.Gate("k", code) for code in codes]) == text


@pytest.mark.parametrize("gaps, text", [
    ({}, "yok"), (PHOTO_GAPS, "foto 156/187; kapak 0/6"),
    ({"neighborhoods": {"actual": 10, "minimum": 12}, "bilinmeyen": {"actual": 1, "minimum": 2}},
     "mahalle 10/12; bilinmeyen 1/2")])
def test_format_minimum_gaps(gaps, text):
    assert run_log_inputs.format_minimum_gaps(gaps) == text


@pytest.mark.parametrize("name, family", [
    ("claude-opus-4-5-20251101", "opus"), ("claude-sonnet-4-6", "sonnet"), ("Claude-Haiku-4-5", "haiku"),
    ("gpt-x", "gpt-x"), ("", "?")])
def test_model_family(name, family):
    assert run_log_inputs.model_family(name) == family


@pytest.mark.parametrize("counts, text", [
    ({"reviewed": 4, "rejected": 1}, "1/4"), ({"checked": 3, "second_rejected": 0}, "ikinci göz 0/3"), ({}, None)])
def test_photo_review_cell(counts, text):
    assert run_log.PhotoReview(**counts).cell() == text
