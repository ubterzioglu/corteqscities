"""manifest_check.py testleri (IYILESTIRME_LISTESI C4): sema, phase_log isaretleri, faz sirasi, teslim SHA'si.

Sentetik manifest + phase_log + sahte paket (gercek veriye dokunmaz). Sema: gercek city-pack sozlesmesi.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

import manifest_check

TOOLKIT = Path(__file__).resolve().parent.parent
SCRIPT = TOOLKIT / "scripts" / "manifest_check.py"
SCHEMA = TOOLKIT.parent / "city-pack" / "references" / "manifest.schema.json"
PHASES = ("intake", "sources", "answers", "places", "photos", "assemble", "deliver")
XLSX_NAME = "CITY-999_testville_v001.xlsx"


def stamp(minute: int, second: int = 0) -> str:
    """2026-10-22T10:00:00Z + dakika/saniye (negatif saniye geri gider)."""
    total = minute * 60 + second
    return f"2026-10-22T{10 + total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}Z"


def done_state(index: int) -> dict:
    return {"status": "done", "started_at": stamp(10 * index), "ended_at": stamp(10 * index + 9),
            "gates": [{"script": "validate_all", "exit_code": 0, "summary": {"structure_errors": 0}}],
            "outputs": ["_is/x.json"]}


def full_manifest(work: Path, sha: str) -> dict:
    """7 faz bitti, teslim yazildi; sema ile gecerli."""
    return {
        "schema_version": "1",
        "city": {"city_id": "testville", "name": "Testville", "country": "TL", "city_code": "CITY-999"},
        "paths": {"work": str(work), "package_root": str(work / "paket"),
                  "template_xlsx": str(work / "_is" / "sablon.xlsx"),
                  "tools": str(work / "araclar"), "delivery_xlsx": str(work / "paket" / XLSX_NAME),
                  "usage_log": str(work / "_is" / "phase_log.jsonl")},
        "country_pack": None,
        "phase": "deliver",
        "phases": {name: done_state(i) for i, name in enumerate(PHASES)},
        "last_ids": [], "sources_researched": 3, "photos_downloaded": 2, "next_step": "city-audit",
        "open_items": [{"id": "X-1", "priority": "P2", "check_id": "K50", "text": "örnek açık konu",
                        "evidence": "_is/a.json", "owner": "ai"}],
        "delivered": {"at": stamp(70), "xlsx_sha256": sha, "inventory": "_is/dosya-envanteri.json"},
    }


def staged(data: dict, done: int, running: bool = False) -> dict:
    """Ilk `done` faz bitti; running ise sonraki suruyor; kalanlar pending; teslim yok."""
    phases = {}
    for i, name in enumerate(PHASES):
        if i < done:
            phases[name] = data["phases"][name]
        elif i == done and running:
            phases[name] = {"status": "running", "started_at": stamp(10 * i)}
        else:
            phases[name] = {"status": "pending"}
    current = PHASES[done] if running or done == 0 else PHASES[done - 1]
    return {**{k: v for k, v in data.items() if k != "delivered"}, "phases": phases, "phase": current}


def log_entries(done: int = len(PHASES), running: bool = False) -> list[tuple[str, str, str]]:
    entries = []
    for i, name in enumerate(PHASES[:done]):
        entries += [(name, "start", stamp(10 * i)), (name, "end", stamp(10 * i + 9))]
    if running:
        entries.append((PHASES[done], "start", stamp(10 * done)))
    return entries


@dataclass
class City:
    work: Path
    pkg: Path
    xlsx: Path
    manifest: Path
    log: Path
    sha: str

    def data(self) -> dict:
        return full_manifest(self.work, self.sha)

    def write(self, data) -> Path:
        self.manifest.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.manifest

    def write_log(self, entries, extra_lines=()) -> Path:
        lines = [json.dumps({"phase": p, "event": e, "ts": t}) for p, e, t in entries] + list(extra_lines)
        self.log.write_text("".join(f"{line}\n" for line in lines), encoding="utf-8")
        return self.log


@pytest.fixture()
def city(tmp_path) -> City:
    work = tmp_path / "work"
    (work / "_is").mkdir(parents=True)
    pkg = work / "paket"
    pkg.mkdir()
    xlsx = pkg / XLSX_NAME
    xlsx.write_bytes(b"PK\x03\x04 sahte teslim excel")
    made = City(work, pkg, xlsx, work / "manifest.json", work / "_is" / "phase_log.jsonl",
                hashlib.sha256(xlsx.read_bytes()).hexdigest())
    made.write(made.data())
    made.write_log(log_entries())
    return made


def run(capsys, *argv) -> tuple[int, dict]:
    code = manifest_check.main([str(a) for a in argv])
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1, lines  # stdout tek satir JSON
    return code, json.loads(lines[0])


def items(summary: dict, code: str | None = None) -> list[dict]:
    return [i for i in summary["items"] if code is None or i["code"] == code]


def text(summary: dict, code: str | None = None) -> str:
    return " | ".join(f"{i['where']}: {i['message']}" for i in items(summary, code))


def schema_copy(tmp_path: Path, mutate) -> Path:
    data = json.loads(SCHEMA.read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "sema.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


# ---------- temiz durumlar ----------

def test_clean_city_passes_with_package_sha(city, capsys):
    code, s = run(capsys, city.manifest, "--pkg", city.pkg)
    assert code == 0, s
    assert s["tool"] == "manifest_check" and s["phase"] == "deliver"
    assert s["findings"] == 0 and s["items"] == [] and s["by_code"] == {}
    assert s["phases"] == {name: "done" for name in PHASES}
    assert s["phase_log"] == {"path": str(city.log), "found": True, "marks": 14}
    assert s["xlsx"] == {"checked": True, "file": XLSX_NAME, "match": True, "sha256": city.sha}


def test_without_pkg_sha_is_not_checked(city, capsys):
    city.xlsx.write_bytes(b"degisti")
    code, s = run(capsys, city.manifest)
    assert code == 0 and s["xlsx"] is None


@pytest.mark.parametrize("done, running", [(0, True), (3, False), (3, True), (6, False)])
def test_partial_progress_is_clean(city, capsys, done, running):
    city.write_log(log_entries(done, running))
    code, s = run(capsys, city.write(staged(city.data(), done, running)))
    assert code == 0, s


def test_fresh_intake_without_log_is_clean(city, capsys):
    city.log.unlink()
    code, s = run(capsys, city.write(staged(city.data(), done=0)))
    assert code == 0, s
    assert s["phase_log"]["found"] is False and s["phases"]["intake"] == "pending"


def test_blocked_phase_does_not_stop_later_phases(city, capsys):
    data = staged(city.data(), done=4)
    data["phases"]["answers"] = {**data["phases"]["answers"], "status": "blocked", "blocked_reason": "SVB 403"}
    city.write_log(log_entries(4))
    code, s = run(capsys, city.write(data))
    assert code == 0, s


# ---------- sema ----------

def test_schema_violations_are_findings_with_path_and_turkish_message(city, capsys):
    data = city.data()
    data["phases"]["answers"]["status"] = "finished"
    data["phases"]["places"]["gates"][0]["exit_code"] = 3
    data["extra"] = 1
    del data["city"]["name"], data["city"]["country"]
    data["delivered"]["xlsx_sha256"] = "ABC"
    data["country_pack"] = {"path": "nl", "valid_until": "2026-13-01"}
    data["schema_version"] = 1
    code, s = run(capsys, city.write(data))
    assert code == 1 and set(s["by_code"]) == {"sema"}, s
    where = {i["where"]: i["message"] for i in items(s)}
    assert where["phases.answers.status"] == "izinli değer değil: 'finished' (izinli: pending, running, done, blocked)"
    assert where["phases.places.gates[0].exit_code"] == "izinli değer değil: 3 (izinli: 0, 1, 2)"
    assert where["city"] == "zorunlu alan eksik: name, country"  # iki hata tek bulgu
    assert where["delivered.xlsx_sha256"].startswith("'ABC' biçime uymuyor")
    assert where["country_pack.valid_until"] == "'2026-13-01' tarih değil (YYYY-AA-GG)"
    assert where["schema_version"] == "değer '1' olmalı (1 yazılmış)"
    assert where["(kök)"] == "şemada olmayan alan: extra"
    assert s["findings"] == 7


def test_minimum_and_min_length_messages(city, capsys):
    data = city.data()
    data["sources_researched"] = -1
    data["city"]["name"] = ""
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"sema": 2}, s
    where = {i["where"]: i["message"] for i in items(s)}
    assert where == {"city.name": "en az 1 karakter olmalı ('' yazılmış)",
                     "sources_researched": "en az 0 olmalı (-1 yazılmış)"}


def test_unknown_rule_falls_back_to_library_message(city, capsys, tmp_path):
    schema = schema_copy(tmp_path, lambda d: d["properties"]["city"]["properties"]["name"].update(maxLength=3))
    code, s = run(capsys, city.manifest, "--schema", schema)
    assert code == 1 and s["by_code"] == {"sema": 1}, s
    assert items(s)[0] == {"code": "sema", "where": "city.name", "message": "'Testville' is too long"}


def test_invalid_current_phase_is_only_schema_finding(city, capsys):
    code, s = run(capsys, city.write({**city.data(), "phase": "translate"}))
    assert code == 1 and s["by_code"] == {"sema": 1} and items(s)[0]["where"] == "phase", s


def test_unknown_phase_key_is_schema_finding(city, capsys):
    data = city.data()
    data["phases"]["bogus"] = {"status": "done"}
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"sema": 1}
    assert items(s)[0]["where"] == "phases"
    assert items(s)[0]["message"].startswith("izinsiz anahtar: 'bogus' (izinli: intake, sources, answers")


@pytest.mark.parametrize("value, ok", [
    ("2026-10-22T13:41:30Z", True),
    ("2026-10-22T13:41:30.123+02:00", True),
    ("22.10.2026 13:41:30", False),  # PowerShell ConvertFrom-Json yerel bicimi (SKILL kural 11)
    ("2026-10-22T13:41:30", False),  # saat dilimi yok
    ("2026-10-22 13:41:30Z", False),
    ("2026-02-30T10:00:00Z", False),
    ("", False),
])
def test_datetime_format_is_enforced(city, capsys, value, ok):
    data = city.data()
    data["delivered"]["at"] = value
    code, s = run(capsys, city.write(data))
    if ok:
        assert code == 0, s
    else:
        assert code == 1 and s["by_code"] == {"sema": 1}, s
        assert items(s)[0]["where"] == "delivered.at" and "RFC 3339 tarih-saat değil" in items(s)[0]["message"]


@pytest.mark.parametrize("mutate", [
    lambda d: [],
    lambda d: {**d, "phases": []},
    lambda d: {**d, "phases": {**d["phases"], "answers": "done"}},
    lambda d: {**d, "delivered": "dün teslim edildi"},
    lambda d: {**d, "city": None, "paths": "x", "open_items": {}},
], ids=["kok-liste", "phases-liste", "faz-metin", "delivered-metin", "karisik"])
def test_broken_shapes_are_schema_findings_not_crashes(city, capsys, mutate):
    code, s = run(capsys, city.write(mutate(city.data())), "--pkg", city.pkg)
    assert code == 1 and set(s["by_code"]) == {"sema"}, s


def test_manifest_bom_is_flagged_because_render_summary_cannot_read_it(city, capsys):
    city.manifest.write_bytes(b"\xef\xbb\xbf" + city.manifest.read_bytes())
    code, s = run(capsys, city.manifest)
    assert code == 1 and s["by_code"] == {"dosya": 1}, s
    assert "BOM" in items(s)[0]["message"] and s["phase"] == "deliver"  # icerik yine okundu


# ---------- phase_log isaretleri ----------

def test_done_phase_without_marks(city, capsys):
    city.write_log([e for e in log_entries() if e[0] != "answers"])
    code, s = run(capsys, city.manifest)
    assert code == 1 and s["by_code"] == {"isaret": 1}, s
    assert items(s)[0] == {"code": "isaret", "where": "phases.answers",
                           "message": "done ama phase_log'da start ve end işareti yok"}


def test_done_phase_missing_end_mark(city, capsys):
    city.write_log(log_entries(3)[:-1])
    code, s = run(capsys, city.write(staged(city.data(), done=3)))
    assert code == 1 and s["by_code"] == {"isaret": 1}, s
    assert items(s)[0]["message"] == "done ama phase_log'da end işareti yok"


def test_done_phase_with_reopened_open_window(city, capsys):
    city.write_log(log_entries(2) + [("sources", "start", stamp(25))])
    code, s = run(capsys, city.write(staged(city.data(), done=2)))
    assert code == 1 and s["by_code"] == {"isaret": 1}, s
    assert items(s)[0]["where"] == "phases.sources" and "son penceresi açık (satır 5" in items(s)[0]["message"]


def test_missing_default_log_flags_every_done_phase(city, capsys):
    city.log.unlink()
    code, s = run(capsys, city.manifest)
    assert code == 1 and s["by_code"] == {"isaret": 7}, s
    assert s["phase_log"]["found"] is False and s["phase_log"]["marks"] == 0


def test_running_phase_needs_open_start_mark(city, capsys):
    manifest = city.write(staged(city.data(), done=2, running=True))
    city.write_log(log_entries(2))
    code, s = run(capsys, manifest)
    assert code == 1 and s["by_code"] == {"isaret": 1}, s
    assert items(s)[0] == {"code": "isaret", "where": "phases.answers",
                           "message": "running ama phase_log'da start işareti yok"}
    city.write_log(log_entries(2, running=True) + [("answers", "end", stamp(29))])
    code, s = run(capsys, manifest)
    assert code == 1 and s["by_code"] == {"isaret": 1}, s
    assert "penceresi kapalı (end satır 6)" in items(s)[0]["message"]


def test_more_than_one_running_phase(city, capsys):
    data = staged(city.data(), done=2, running=True)
    data["phases"]["places"] = {"status": "running", "started_at": stamp(30)}
    data["phase"] = "places"
    city.write_log(log_entries(2, running=True) + [("places", "start", stamp(30))])
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"].get("coklu_running") == 1, s
    assert "answers, places" in text(s, "coklu_running")


# ---------- phase_log kayit ve pencereleri ----------

def test_end_before_start_in_log(city, capsys):
    entries = log_entries(3)
    entries[-1] = ("answers", "end", stamp(19, 30))  # answers start 10:20:00
    city.write_log(entries)
    code, s = run(capsys, city.write(staged(city.data(), done=3)))
    assert code == 1 and s["by_code"] == {"log_penceresi": 1}, s
    item = items(s)[0]
    assert item["where"] == "phase_log satır 6"
    assert "'answers' end" in item["message"] and "start'tan" in item["message"] and "satır 5" in item["message"]


def test_unmatched_end_and_double_start(city, capsys):
    base = log_entries(2)
    city.write_log([base[0], base[1], ("intake", "end", stamp(9, 30)),  # satir 3: eslesen start yok
                    base[2], ("sources", "start", stamp(11)), base[3]])  # satir 5: acikken yeniden start
    code, s = run(capsys, city.write(staged(city.data(), done=2)))
    assert code == 1 and s["by_code"] == {"log_penceresi": 2}, s
    where = {i["where"]: i["message"] for i in items(s)}
    assert "eşleşen start'ı yok" in where["phase_log satır 3"]
    assert "zaten açıkken yeniden start" in where["phase_log satır 5"]


def test_overlapping_log_windows(city, capsys):
    city.write_log(log_entries(2) + [("answers", "start", stamp(20)), ("places", "start", stamp(25)),
                                     ("answers", "end", stamp(29)), ("places", "end", stamp(39))])
    code, s = run(capsys, city.write(staged(city.data(), done=4)))
    assert code == 1 and s["by_code"] == {"log_penceresi": 1}, s
    assert "'answers' penceresi" in items(s)[0]["message"] and "kapanmadan 'places'" in items(s)[0]["message"]


def test_bad_log_lines_are_findings_and_rest_is_checked(city, capsys):
    city.write_log(log_entries(), extra_lines=[
        "bozuk satir",
        "[1, 2]",
        json.dumps({"phase": "answers"}),
        json.dumps({"phase": "answers", "event": "pause", "ts": stamp(80)}),
        json.dumps({"phase": "answers", "event": "end", "ts": "dün"}, ensure_ascii=False),
        json.dumps({"phase": "foto_ek16", "event": "start", "ts": stamp(80)}),
        json.dumps({"phase": "foto_ek16", "event": "end", "ts": stamp(81)}),
        "",  # bos satir atlanir (bulgu degil)
        json.dumps({"event": "start", "ts": stamp(82)}),
    ])
    code, s = run(capsys, city.manifest)
    assert code == 1 and s["by_code"] == {"log_kaydi": 7}, s
    where = {i["where"]: i["message"] for i in items(s)}
    assert where["phase_log satır 15"].startswith("JSON değil")
    assert where["phase_log satır 16"] == "JSON nesnesi değil"
    assert "event" in where["phase_log satır 17"]
    assert "'pause'" in where["phase_log satır 18"]
    assert "'dün'" in where["phase_log satır 19"]
    assert where["phase_log satır 20"] == "şemada olmayan faz adı: 'foto_ek16'"  # ad basina bir kez
    assert where["phase_log satır 23"] == "faz adı (phase) yok"


def test_log_bom_is_flagged_because_phase_usage_cannot_read_it(city, capsys):
    city.log.write_bytes(b"\xef\xbb\xbf" + city.log.read_bytes())
    code, s = run(capsys, city.manifest)
    assert s["by_code"].get("log_kaydi") == 1 and code == 1, s
    assert items(s, "log_kaydi")[0]["where"] == "phase_log satır 1" and "BOM" in items(s, "log_kaydi")[0]["message"]


def test_explicit_missing_phase_log_is_usage_error(city, capsys, tmp_path):
    code, s = run(capsys, city.manifest, "--phase-log", tmp_path / "yok.jsonl")
    assert code == 2 and "phase_log" in s["error"]


# ---------- faz sirasi ----------

def test_started_phase_after_pending_phase_breaks_order(city, capsys):
    data = staged(city.data(), done=3)
    data["phases"]["sources"] = {"status": "pending"}
    city.write_log([e for e in log_entries(3) if e[0] != "sources"])
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"faz_sirasi": 1}, s
    assert items(s)[0]["where"] == "phases.answers" and "önceki faz 'sources' pending" in items(s)[0]["message"]


def test_done_phase_after_running_phase_breaks_order(city, capsys):
    data = staged(city.data(), done=4)
    data["phases"]["answers"] = {"status": "running", "started_at": stamp(20)}
    code, s = run(capsys, city.write(data))
    assert code == 1 and "önceki faz 'answers' running" in text(s, "faz_sirasi"), s


@pytest.mark.parametrize("done, phase, ok", [
    (0, "intake", True), (0, "sources", False),
    (3, "answers", True), (3, "places", True), (3, "photos", False), (3, "sources", False),
    (7, "deliver", True), (7, "assemble", False),
])
def test_current_phase_must_match_statuses(city, capsys, done, phase, ok):
    data = city.data() if done == len(PHASES) else staged(city.data(), done)
    city.write_log(log_entries(done))
    code, s = run(capsys, city.write({**data, "phase": phase}))
    if ok:
        assert code == 0, s
    else:
        assert code == 1 and s["by_code"] == {"faz_sirasi": 1} and items(s)[0]["where"] == "phase", s


@pytest.mark.parametrize("phase, ok", [("answers", True), ("places", True), ("photos", False)])
def test_current_phase_may_move_past_blocked_phase(city, capsys, phase, ok):
    """'blocked' sonraki fazlari durdurmaz: son baslayan faz blocked ise ust duzey phase sonraki faz da olabilir."""
    data = staged(city.data(), done=3)
    data["phases"]["answers"] = {**data["phases"]["answers"], "status": "blocked", "blocked_reason": "SVB 403"}
    city.write_log(log_entries(3))
    code, s = run(capsys, city.write({**data, "phase": phase}))
    if ok:
        assert code == 0, s
    else:
        assert code == 1 and s["by_code"] == {"faz_sirasi": 1} and items(s)[0]["where"] == "phase", s
        assert "son başlayan faz 'answers' blocked); beklenen: answers ya da places" in items(s)[0]["message"]


def test_missing_phase_record_counts_as_pending(city, capsys):
    """Kaydi olmayan faz 'pending' sayilir: kaydi olmayan sources'tan sonra answers bitmis olamaz."""
    data = staged(city.data(), done=3)
    del data["phases"]["sources"]
    city.write_log([e for e in log_entries(3) if e[0] != "sources"])
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"faz_sirasi": 1}, s
    assert s["phases"]["sources"] == "pending"
    assert items(s)[0]["where"] == "phases.answers" and "önceki faz 'sources' pending" in items(s)[0]["message"]


def test_intake_manifest_with_only_its_own_phase_is_clean(city, capsys):
    """Intake'te manifest ilk yazilirken yalniz kendi fazi olabilir; kalanlar 'pending' sayilir, bulgu vermez."""
    data = staged(city.data(), done=0, running=True)
    city.write_log(log_entries(0, running=True))
    code, s = run(capsys, city.write({**data, "phases": {"intake": data["phases"]["intake"]}}))
    assert code == 0, s
    assert s["phases"] == {"intake": "running", **{name: "pending" for name in PHASES[1:]}}


@pytest.mark.parametrize("manifest_times", ["eski", "ended_at", "started_at+ended_at"])
def test_phase_reopened_after_delivery_is_clean(city, capsys, manifest_times):
    """SKILL: her duzeltmeden sonra zincir bastan calisir. Teslimden sonra yeniden acilan faz sirayi bozmaz: log'da
    her fazin ilk start'i sayilir; manifest faz basina tek pencere tutar, o faz ciftinin zamanlari karsilastirilmaz."""
    data = city.data()
    if manifest_times != "eski":
        data["phases"]["answers"]["ended_at"] = stamp(75)
    if manifest_times == "started_at+ended_at":
        data["phases"]["answers"]["started_at"] = stamp(72)
    city.write_log(log_entries() + [("answers", "start", stamp(72)), ("answers", "end", stamp(75))])
    code, s = run(capsys, city.write(data), "--pkg", city.pkg)
    assert code == 0, s
    assert s["phase_log"]["marks"] == 16


@pytest.mark.parametrize("restarted, message", [(False, "bitmeden başlıyor"), (True, "önce başlıyor")])
def test_reopen_missing_from_phase_log_is_flagged(city, capsys, restarted, message):
    """Manifest yeniden acilisi gosteriyor ama phase_log'da isareti yok: sira bulgusu, cozum ipucuyla."""
    data = city.data()
    data["phases"]["answers"]["ended_at"] = stamp(75)
    if restarted:
        data["phases"]["answers"]["started_at"] = stamp(72)
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"faz_sirasi": 1}, s
    item = items(s)[0]
    assert item["where"] == "phases.places.started_at" and message in item["message"]
    assert "'answers' yeniden açıldıysa phase_log'da" in item["message"]


def test_log_phases_must_start_in_schema_order(city, capsys):
    swapped = [("places", "start", stamp(20)), ("places", "end", stamp(29)),
               ("answers", "start", stamp(30)), ("answers", "end", stamp(39))]
    city.write_log(log_entries(2) + swapped)
    code, s = run(capsys, city.write(staged(city.data(), done=4)))
    assert code == 1 and s["by_code"] == {"faz_sirasi": 1}, s
    assert items(s)[0]["where"] == "phase_log satır 7" and "'answers'" in items(s)[0]["message"]


def test_manifest_end_before_start(city, capsys):
    data = staged(city.data(), done=3)
    data["phases"]["answers"]["ended_at"] = stamp(15)
    city.write_log(log_entries(3))
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"zaman": 1}, s
    assert items(s)[0]["where"] == "phases.answers.ended_at"


def test_manifest_phase_starts_before_previous_phase(city, capsys):
    data = staged(city.data(), done=4)
    data["phases"]["places"]["started_at"] = stamp(15)
    city.write_log(log_entries(4))
    code, s = run(capsys, city.write(data))
    assert code == 1 and s["by_code"] == {"faz_sirasi": 1}, s
    assert items(s)[0]["where"] == "phases.places.started_at" and "önce başlıyor" in items(s)[0]["message"]


@pytest.mark.parametrize("offset, flagged", [(-1, False), (-2, True)])
def test_manifest_phase_overlap_has_one_second_slack(city, capsys, offset, flagged):
    data = staged(city.data(), done=4)
    data["phases"]["places"]["started_at"] = stamp(29, offset)  # answers ended_at 10:29:00
    city.write_log(log_entries(4))
    code, s = run(capsys, city.write(data))
    assert (code, s["by_code"]) == ((1, {"faz_sirasi": 1}) if flagged else (0, {})), s
    if flagged:
        assert "bitmeden başlıyor" in items(s)[0]["message"]


def test_phase_order_comes_from_schema(city, capsys, tmp_path):
    order = ["intake", "sources", "places", "answers", "photos", "assemble", "deliver"]
    schema = schema_copy(tmp_path, lambda d: d["$defs"]["phase_name"].update(enum=order))
    code, s = run(capsys, city.manifest, "--schema", schema)
    assert code == 1 and s["by_code"] == {"faz_sirasi": 2}, s  # phase_log + manifest zamanlari


# ---------- teslim (delivered.xlsx_sha256) ----------

def test_delivered_sha_must_match_package_excel(city, capsys):
    city.xlsx.write_bytes(b"PK\x03\x04 yeniden kuruldu")
    code, s = run(capsys, city.manifest, "--pkg", city.pkg)
    assert code == 1 and s["by_code"] == {"teslim": 1}, s
    assert items(s)[0]["where"] == "delivered.xlsx_sha256" and "aynı değil" in items(s)[0]["message"]
    assert s["xlsx"]["checked"] is True and s["xlsx"]["match"] is False


def test_deliver_done_requires_delivered_sha(city, capsys):
    data = city.data()
    del data["delivered"]
    code, s = run(capsys, city.write(data), "--pkg", city.pkg)
    assert code == 1 and s["by_code"] == {"teslim": 1}, s
    assert items(s)[0] == {"code": "teslim", "where": "delivered",
                           "message": "deliver done ama delivered.xlsx_sha256 yok"}
    assert s["xlsx"] == {"checked": False, "reason": "delivered.xlsx_sha256 yok"}


def test_excel_named_in_manifest_must_exist_in_package(city, capsys):
    city.xlsx.rename(city.pkg / "CITY-999_testville_v002.xlsx")
    code, s = run(capsys, city.manifest, "--pkg", city.pkg)
    assert code == 1 and s["by_code"] == {"teslim": 1}, s
    assert items(s)[0]["where"] == "paths.delivery_xlsx" and XLSX_NAME in items(s)[0]["message"]


@pytest.mark.parametrize("extra, remove_main, expected", [
    ({"~$CITY-999_testville_v001.xlsx": b"kilit", "Teslimler/eski.xlsx": b"alt klasor"}, False, None),
    ({"CITY-999_testville_v002.xlsx": b"ikinci"}, False, "birden çok Excel"),
    ({}, True, "pakette Excel yok"),
], ids=["kilit-ve-alt-klasor-sayilmaz", "iki-excel", "excel-yok"])
def test_excel_found_in_package_root_without_delivery_path(city, capsys, extra, remove_main, expected):
    data = city.data()
    del data["paths"]["delivery_xlsx"]
    for name, content in extra.items():
        (city.pkg / name).parent.mkdir(parents=True, exist_ok=True)
        (city.pkg / name).write_bytes(content)
    if remove_main:
        city.xlsx.unlink()
    code, s = run(capsys, city.write(data), "--pkg", city.pkg)
    if expected is None:
        assert code == 0 and s["xlsx"]["file"] == XLSX_NAME, s
    else:
        assert code == 1 and s["by_code"] == {"teslim": 1} and expected in text(s, "teslim"), s


# ---------- kullanim, cikti, salt okunurluk ----------

@pytest.mark.parametrize("case", ["manifest-yok", "manifest-klasor", "manifest-json-degil", "manifest-utf8-degil",
                                  "sema-gecersiz", "sema-nesne-degil", "sema-faz-sirasi-yok", "sema-ref-cozulmuyor",
                                  "jsonschema-yok", "pkg-klasor-degil", "bilinmeyen-arguman"])
def test_usage_errors_exit_2(city, capsys, tmp_path, monkeypatch, case):
    argv = [city.manifest]
    if case == "manifest-yok":
        argv = [tmp_path / "yok.json"]
    elif case == "manifest-klasor":
        argv = [city.work]
    elif case == "manifest-json-degil":
        city.manifest.write_text("{bozuk", encoding="utf-8")
    elif case == "manifest-utf8-degil":
        city.manifest.write_bytes(b"\xff\xfe{}")
    elif case == "sema-gecersiz":
        argv += ["--schema", schema_copy(tmp_path, lambda d: d.update(type=5))]
    elif case == "sema-nesne-degil":
        (tmp_path / "liste.json").write_text("[]", encoding="utf-8")
        argv += ["--schema", tmp_path / "liste.json"]
    elif case == "sema-faz-sirasi-yok":
        argv += ["--schema", schema_copy(tmp_path, lambda d: d["$defs"].update(phase_name={"type": "string"}))]
    elif case == "sema-ref-cozulmuyor":
        argv += ["--schema", schema_copy(tmp_path, lambda d: d["properties"].update(phase={"$ref": "#/$defs/yok"}))]
    elif case == "jsonschema-yok":
        monkeypatch.setattr(manifest_check, "jsonschema", None)
    elif case == "pkg-klasor-degil":
        argv += ["--pkg", city.xlsx]
    else:
        argv += ["--bilinmeyen"]
    code = manifest_check.main([str(a) for a in argv])
    out = capsys.readouterr().out
    assert code == 2
    if case != "bilinmeyen-arguman":
        assert json.loads(out)["error"]
    if case == "jsonschema-yok":
        assert "requirements.txt" in json.loads(out)["error"]


def test_out_writes_full_report_while_stdout_is_capped(city, capsys, tmp_path):
    data = city.data()
    count = manifest_check.MAX_ITEMS + 5
    data["open_items"] = [{"text": f"madde {i}"} for i in range(count)]
    out = tmp_path / "rapor" / "manifest_check.json"
    code, s = run(capsys, city.write(data), "--out", out)
    assert code == 1 and s["findings"] == count and len(s["items"]) == manifest_check.MAX_ITEMS
    assert s["out"] == str(out)
    report = json.loads(out.read_text(encoding="utf-8"))
    assert len(report["findings"]) == count
    assert [f["where"] for f in report["findings"][:11]] == [f"open_items[{i}]" for i in range(11)]  # sayisal sira
    assert report["findings"][0]["message"] == "zorunlu alan eksik: id, priority, evidence"


@pytest.mark.parametrize("target, with_pkg", [("manifest", True), ("log", True), ("pkg", True), ("pkg", False)])
def test_out_never_overwrites_inputs_or_writes_into_package(city, capsys, target, with_pkg):
    before = (city.manifest.read_bytes(), city.log.read_bytes())
    out = {"manifest": city.manifest, "log": city.log, "pkg": city.pkg / "Teslimler" / "m.json"}[target]
    argv = [city.manifest, "--out", out] + (["--pkg", city.pkg] if with_pkg else [])
    code = manifest_check.main([str(a) for a in argv])
    assert code == 2 and json.loads(capsys.readouterr().out)["error"]
    assert (city.manifest.read_bytes(), city.log.read_bytes()) == before
    assert not (city.pkg / "Teslimler").exists()


@pytest.mark.parametrize("declared, target", [("teslim", "teslim"), (None, "paket")],
                         ids=["goreli-package_root", "skill-duzeni-WORK-paket"])
def test_out_never_writes_into_package_named_by_manifest(city, capsys, tmp_path, monkeypatch, declared, target):
    """Goreli paths.package_root manifest klasorune gore cozulur (run_log gibi); SKILL'de PKG = WORK\\paket."""
    data = city.data()
    data["paths"]["package_root"] = declared or str(tmp_path / "baska_paket")
    city.write(data)
    monkeypatch.chdir(tmp_path)  # goreli yol calisma klasorune gore cozulurse paket korunmaz
    out = city.work / target / "Teslimler" / "m.json"
    code = manifest_check.main([str(city.manifest), "--out", str(out)])
    assert code == 2 and "paket klasörüne yazamaz" in json.loads(capsys.readouterr().out)["error"]
    assert not out.parent.exists()


def test_inputs_are_never_modified(city, capsys, tmp_path):
    snapshot = {p: p.read_bytes() for p in (city.manifest, city.log, city.xlsx)}
    listing = sorted(p.relative_to(city.work) for p in city.work.rglob("*"))
    code, _ = run(capsys, city.manifest, "--pkg", city.pkg, "--out", tmp_path / "r.json")
    assert code == 0
    assert {p: p.read_bytes() for p in snapshot} == snapshot
    assert sorted(p.relative_to(city.work) for p in city.work.rglob("*")) == listing


def test_help_exits_0_and_pkg_is_read_only_input(capsys):
    assert manifest_check.main(["--help"]) == 0
    assert "--phase-log" in capsys.readouterr().out
    args = manifest_check.build_parser().parse_args(["m.json", "--pkg", "P"])
    assert args.package_root == Path("P")  # B1: PKG'yi gosteren salt okunur girdi (READ_ONLY_DESTS)


def test_cli_prints_one_utf8_json_line(city):
    city.write_log([e for e in log_entries() if e[0] != "answers"])
    result = subprocess.run([sys.executable, "-B", str(SCRIPT), str(city.manifest)], capture_output=True, timeout=120)
    assert result.returncode == 1, result.stderr
    lines = result.stdout.decode("utf-8").splitlines()
    assert len(lines) == 1 and "işareti yok" in json.loads(lines[0])["items"][0]["message"]
