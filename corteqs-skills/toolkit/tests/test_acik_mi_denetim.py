"""acik_mi_denetim: city-audit acik-mi adimi (K39, B15; W2 incelemesi): orneklem, acik kaniti, sayim.

Ag yok: fetch_snapshot sahte tasimayla, kapilar gercek acik_mi.main()'iyle calisir; yazma yalniz tmp_path. SKILL.md'deki
komutlarin sirasi, siniflar ve P dereceleri test_skill_pack_phases.py'de (city-audit bolumu).
Calistirma: $env:PYTHONDONTWRITEBYTECODE=1; <PY> -m pytest -q -p no:cacheprovider tests\\test_acik_mi_denetim.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

import acik_mi
import acik_mi_denetim as ad
import fetch_snapshot
import test_acik_mi as am
from test_web_fetch import FakeTransport, ok

SCRIPT = Path(ad.__file__)
EXCEL = b"teslim excel baytlari"
OLD_NOTE = "1 Ağustos 2022 itibarıyla yeni saatler."  # (c): yili ne olursa olsun
FOOTER = {"kanit_alinti": "© 2019 Golfbaan", "kanit_tarihi": "tarihsiz (footer © 2019)"}
SINGLE = "Kapandı; ikinci bağımsız kaynak bulunamadı (belediye ve yerel gazete arandı)."
CLOSURE = {"eylem": "sil", "kanit_url": "https://nieuws.example/golf", "kanit_alinti": "De golfbaan sluit definitief",
           "gerekce": "Kapanış iki kaynakta. İkinci kaynak: https://gemeente.example/nieuws/sluiting «definitief gesloten»; "
                      "arşiv: https://archief.nieuws.example/golf, «sluit definitief»."}
PAGES = {"https://nieuws.example/golf": "De golfbaan sluit definitief de deuren aan het einde van dit jaar.",
         "https://gemeente.example/nieuws/sluiting": "Het terrein is definitief gesloten.",
         "https://nieuws.example/mevsim": "Het museum blijft gewoon open. De speeltuin is in de winter dicht."}
ROUTES = {url: ok(f"<html><head><title>Nieuws</title></head><body><main><p>{body}</p></main></body></html>".encode())
          for url, body in PAGES.items()}


def slugs(count: int) -> list[str]:
    return [f"yer{index:02d}" for index in range(1, count + 1)]


def setup(tmp_path: Path, cards: list[dict]) -> tuple[Path, Path]:
    """OUT\\_dump\\Mekânlar.jsonl (xlsx_dump) ve paket kokunde teslim Excel'i (baytlari rastgele siranin tohumu)."""
    out, xlsx = tmp_path / "out", tmp_path / "paket" / "teslim.xlsx"
    am.write_jsonl(out / "_dump" / "Mekânlar.jsonl", cards)
    xlsx.parent.mkdir(parents=True, exist_ok=True)
    xlsx.write_bytes(EXCEL)
    return out, xlsx


def run(capsys, *argv) -> tuple[int, dict]:
    code = ad.main([str(arg) for arg in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1, lines  # stdout tek satir JSON
    return code, json.loads(lines[0])


def rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rank(entry: str, excel: bytes = EXCEL) -> str:
    """SKILL.md'deki sira, aractan bagimsiz: sha256((excel_sha256 kucuk harf + entry_id).encode('utf-8'))."""
    return hashlib.sha256((hashlib.sha256(excel).hexdigest() + entry).encode("utf-8")).hexdigest()


def production(tmp_path: Path, out: Path, capsys) -> Path:
    """Uretim acik-mi klasoru ve SKILL.md'deki gibi uretim beyani kapisinin raporu. (a) yer01 footer kaniti, yer02
    dogrulamasiz 'belirsiz'; (b) yer02, yer03 'onay' + 'dokunma'; (d) yer04 'kapalı', yer07 'taşındı' + 'ret' +
    'dokunma'."""
    folder = tmp_path / "uretim" / "acik_mi"
    special = {"yer01": am.scan("yer01", **FOOTER), "yer02": am.scan("yer02", "belirsiz"),
               "yer03": am.scan("yer03", "belirsiz"), "yer04": am.scan("yer04", "kapalı"),
               "yer07": am.scan("yer07", "taşındı")}
    am.write_jsonl(folder / "spor.jsonl", [special.get(slug) or am.scan(slug) for slug in slugs(30)])
    am.write_jsonl(folder / "spor_dogrulama.jsonl", [am.verify("yer03", sonuc="onay"),
                                                     am.verify("yer04", tarama_durum="kapalı"),
                                                     am.verify("yer07", tarama_durum="taşındı")])
    sources = am.write_jsonl(out / "_dump" / "Kaynaklar.jsonl", [])
    code, _ = am.run_main(capsys, [folder, "--mekanlar", out / ad.VENUES, "--kaynaklar", sources,
                                   "--min-year", am.MIN_YEAR, "--out", out / ad.PRODUCTION_REPORT])
    assert code == 1
    return folder


def cards_with_notes(count: int, notes: dict[str, str]) -> list[dict]:
    return [am.venue(slug, note=notes.get(slug, "")) for slug in slugs(count)]


# ------------------------------------------------------------------ orneklem


@pytest.mark.parametrize("count, full, expected", [(1, False, 1), (7, False, 7), (8, False, 8), (30, False, 8),
                                                   (80, False, 8), (81, False, 9), (120, False, 12), (30, True, 30)])
def test_sample_size_is_at_least_eight_and_ten_percent(count, full, expected):
    assert ad.sample_size(count, full) == expected


def test_priorities_come_first_and_the_random_part_still_runs(tmp_path, capsys):
    cards = cards_with_notes(30, {"yer05": am.NOTE, "yer06": OLD_NOTE})
    out, xlsx = setup(tmp_path, cards)
    folder = production(tmp_path, out, capsys)
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx, "--acik-mi", folder)
    sample = rows(out / ad.SAMPLE_NAME)
    assert [(row["entry_id"], row["neden"]) for row in sample[:7]] == [
        (am.eid("yer01"), "a"), (am.eid("yer02"), "a+b"), (am.eid("yer03"), "b"), (am.eid("yer04"), "d"),
        (am.eid("yer05"), "c"), (am.eid("yer06"), "c"), (am.eid("yer07"), "d")]  # Excel sirasiyla
    random_part = sorted((am.eid(slug) for slug in slugs(30)[7:]), key=rank)[:4]  # en az ceil(8/2)
    assert [(row["entry_id"], row["neden"]) for row in sample[7:]] == [(entry, "rastgele") for entry in random_part]
    assert sample[0] == {**cards[0], "neden": "a"}  # Mekânlar satiri aynen
    assert code == 0 and {key: summary[key] for key in ("mekan", "n", "orneklem", "oncelikli", "rastgele", "parti")} == {
        "mekan": 30, "n": 8, "orneklem": 11, "oncelikli": 7, "rastgele": 4, "parti": 2}
    assert summary["oncelik"] == {"a": 2, "b": 2, "c": 2, "d": 2} and summary["uretim"] == "okundu"
    assert [len(rows(out / ad.BATCH_DIR / name)) for name in ("parti_01.jsonl", "parti_02.jsonl")] == [8, 3]


def test_random_part_is_at_least_half_of_n_even_when_priorities_fill_it(tmp_path, capsys):
    out, xlsx = setup(tmp_path, cards_with_notes(30, dict.fromkeys(slugs(10), am.NOTE)))
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx)
    sample = rows(out / ad.SAMPLE_NAME)
    assert code == 0 and [row["neden"] for row in sample] == ["c"] * 10 + ["rastgele"] * 4
    assert [row["entry_id"] for row in sample[10:]] == sorted((am.eid(slug) for slug in slugs(30)[10:]), key=rank)[:4]


def test_batches_hold_scan_rows_and_every_run_starts_clean(tmp_path, capsys):
    """W2 incelemesi: ayni OUT'ta adim yeniden calisinca eski parti_NN.jsonl ornek disi mekan icin dogrulama_yok
    veriyordu; parti klasoru ve sonraki adimlarin ciktilari bastan (salt okunur dosya da silinir), L0 kanitlari kalir."""
    out, xlsx = setup(tmp_path, [am.venue(slug) for slug in slugs(20)])
    stale = [out / ad.BATCH_DIR / "parti_05.jsonl", out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl",
             out / ad.OPEN_DIR / ad.OPEN_ROWS, out / ad.EVIDENCE_DIR / ad.INDEX_NAME,
             *(out / name for name in (ad.AUDIT_REPORT, ad.OPEN_LIST, ad.OPEN_REPORT, ad.COUNT_NAME))]
    for path in stale:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("{}\n", encoding="utf-8")
    os.chmod(stale[0], stat.S_IREAD)  # Copy-Item salt okunur ozniteligi korur
    kept = out / "kanitlar" / "snap" / "index.jsonl"
    kept.parent.mkdir(parents=True)
    kept.write_text("L0", encoding="utf-8")
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx)
    assert code == 0 and [path for path in stale if path.exists()] == [] and kept.read_text(encoding="utf-8") == "L0"
    sample = rows(out / ad.SAMPLE_NAME)
    assert sorted(path.name for path in (out / ad.BATCH_DIR).iterdir()) == ["parti_01.jsonl"]
    scans = rows(out / ad.BATCH_DIR / "parti_01.jsonl")
    assert [list(scan) for scan in scans] == [list(acik_mi.TARAMA_ALANLARI)] * 8  # anahtar sirasi aynen
    assert [scan["entry_id"] for scan in scans] == [row["entry_id"] for row in sample]
    assert {tuple(scan[field] for field in ("durum", "kanit_url", "kanit_alinti", "kanit_tarihi", "not"))
            for scan in scans} == {("belirsiz", "", "", "", "denetim örneklemi")}


def test_without_a_production_report_only_card_notes_are_priorities(tmp_path, capsys):
    """W2 incelemesi: uretim dosyasi okunamazsa kapi rapor yazmaz (SKILL.md eski raporu once siler); ornekleyici
    ACIKMI'yi okumaz, (a), (b), (d) olmadan devam eder. --acik-mi bos = verilmedi."""
    out, xlsx = setup(tmp_path, cards_with_notes(30, {"yer05": am.NOTE}))
    broken = tmp_path / "uretim" / "acik_mi"
    broken.mkdir(parents=True)
    (broken / "spor.jsonl").write_text("{bozuk\n", encoding="utf-8")
    for folder, status in ((broken, "rapor yok"), ("", "verilmedi")):
        code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx, "--acik-mi", folder)
        assert (code, summary["uretim"], summary["oncelikli"], summary["rastgele"]) == (0, status, 1, 7), summary


def test_full_level_takes_every_venue(tmp_path, capsys):
    out, xlsx = setup(tmp_path, cards_with_notes(12, {"yer03": am.NOTE}))
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx, "--tam")
    sample = rows(out / ad.SAMPLE_NAME)
    assert code == 0 and len(sample) == 12 and sample[0]["neden"] == "c" and {row["neden"] for row in sample[1:]} == {"tam"}
    assert summary["tam"] == 11 and "rastgele" not in summary and summary["parti"] == 2


def test_same_excel_gives_the_same_sample_and_a_new_version_reorders(tmp_path, capsys):
    out, xlsx = setup(tmp_path, [am.venue(slug) for slug in slugs(40)])
    run(capsys, "orneklem", out, "--xlsx", xlsx)
    first = (out / ad.SAMPLE_NAME).read_bytes()
    run(capsys, "orneklem", out, "--xlsx", xlsx)
    assert (out / ad.SAMPLE_NAME).read_bytes() == first
    xlsx.write_bytes(EXCEL + b" v002")
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx)
    expected = sorted((am.eid(slug) for slug in slugs(40)), key=lambda entry: rank(entry, EXCEL + b" v002"))[:8]
    assert [row["entry_id"] for row in rows(out / ad.SAMPLE_NAME)] == expected
    sha = hashlib.sha256(EXCEL + b" v002").hexdigest()
    assert summary["excel_sha256"] == sha and ad.random_key(sha.upper(), "x") == ad.random_key(sha, "x")


def test_unusable_inputs_exit_2_with_a_reason_and_delete_nothing(tmp_path, capsys):
    out, xlsx = setup(tmp_path, [am.venue(slug) for slug in slugs(10)])
    marker = am.write_jsonl(out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl", [am.verify("yer01")])
    folder = tmp_path / "uretim" / "acik_mi"
    am.write_jsonl(folder / "spor.jsonl", [am.scan("yer01")])
    report = out / ad.PRODUCTION_REPORT

    def expect(*argv, reason: str) -> None:
        code, summary = run(capsys, *argv)
        assert code == 2 and reason in summary["error"] and summary["tool"] == ad.TOOL, summary
        assert marker.is_file(), "hatada silinmemeli"

    expect("orneklem", out, "--xlsx", xlsx.parent / "yok.xlsx", reason="yok.xlsx")
    expect("orneklem", tmp_path / "yok", "--xlsx", xlsx, reason="OUT")
    expect("orneklem", xlsx.parent, "--xlsx", xlsx, reason="paketin içinde")
    expect("orneklem", out, "--xlsx", xlsx, "--acik-mi", out / ad.BATCH_DIR, reason="ACIKMI")
    report.write_text("{bozuk", encoding="utf-8")
    expect("orneklem", out, "--xlsx", xlsx, "--acik-mi", folder, reason=ad.PRODUCTION_REPORT)
    stranger = {"acik_mi": str(tmp_path / "baska"), "mekanlar": [str(out / ad.VENUES)], "findings": []}
    report.write_text(json.dumps(stranger), encoding="utf-8")
    expect("orneklem", out, "--xlsx", xlsx, "--acik-mi", folder, reason="raporu değil")
    report.write_text(json.dumps({**stranger, "acik_mi": str(folder)}), encoding="utf-8")
    (folder / "spor.jsonl").write_text("[1]\n", encoding="utf-8")
    expect("orneklem", out, "--xlsx", xlsx, "--acik-mi", folder, reason="okunamadı")
    am.write_jsonl(out / ad.VENUES, [{"title": "kimliksiz"}])
    expect("orneklem", out, "--xlsx", xlsx, reason="entry_id")
    (out / ad.VENUES).unlink()
    expect("orneklem", out, "--xlsx", xlsx, reason="xlsx_dump")
    for command in ("kanit", "sayim"):
        expect(command, out, reason="orneklem")


def test_broken_later_inputs_exit_2_too(tmp_path, capsys, monkeypatch):
    """Bozuk ajan satiri, findings'siz rapor, parti klasoru yok, bozuk kopya index'i, eksik arguman, yazma hatasi."""
    out, xlsx = setup(tmp_path, [am.venue("yer"), am.venue("golf")])
    folder = tmp_path / "uretim" / "acik_mi"
    am.write_jsonl(folder / "spor.jsonl", [am.scan("yer")])
    (out / ad.PRODUCTION_REPORT).write_text("[]", encoding="utf-8")
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx, "--acik-mi", folder)
    assert code == 2 and "findings" in summary["error"], summary
    (out / ad.PRODUCTION_REPORT).unlink()
    assert run(capsys, "orneklem", out, "--xlsx", xlsx)[0] == 0
    (out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl").write_text("{bozuk\n", encoding="utf-8")
    code, summary = run(capsys, "kanit", out)
    assert code == 2 and "JSON" in summary["error"], summary
    am.write_jsonl(out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl", [am.verify("golf", **CLOSURE)])
    assert run(capsys, "kanit", out)[0] == 0
    (out / ad.EVIDENCE_DIR / ad.INDEX_NAME).write_text("{bozuk\n", encoding="utf-8")
    am.run_main(capsys, [out / ad.OPEN_DIR, "--mekanlar", out / ad.OPEN_LIST, "--out", out / ad.OPEN_REPORT])
    code, summary = run(capsys, "sayim", out)
    assert code == 2 and "kanıt kopyası okunamadı" in summary["error"], summary
    shutil.rmtree(out / ad.BATCH_DIR)
    code, summary = run(capsys, "kanit", out)
    assert code == 2 and "parti klasörü yok" in summary["error"], summary
    assert ad.main(["orneklem", str(out)]) == 2 and ad.main(["--help"]) == 0  # --xlsx zorunlu
    capsys.readouterr()

    def unwritable(*_args, **_kwargs):
        raise OSError(28, "disk dolu")

    monkeypatch.setattr(ad, "write_jsonl", unwritable)
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx)
    assert code == 2 and "yazılamadı" in summary["error"], summary


def test_a_locked_old_output_stops_before_writing(tmp_path, capsys, monkeypatch):
    out, xlsx = setup(tmp_path, [am.venue("yer")])
    (out / ad.BATCH_DIR).mkdir()

    def locked(path, **_):
        raise PermissionError(13, "kilitli", str(path))

    monkeypatch.setattr(shutil, "rmtree", locked)
    code, summary = run(capsys, "orneklem", out, "--xlsx", xlsx)
    assert code == 2 and "silinemedi" in summary["error"] and not (out / ad.SAMPLE_NAME).exists()


# ------------------------------------------------------------------ kanit


def sampled(tmp_path: Path, capsys, cards: list[dict], verifs: list[dict]) -> Path:
    """Orneklem (8'den az mekan: hepsi) + ajanin parti_01_dogrulama.jsonl'i."""
    out, xlsx = setup(tmp_path, cards)
    assert run(capsys, "orneklem", out, "--xlsx", xlsx)[0] == 0
    am.write_jsonl(out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl", verifs)
    return out


def test_kanit_turns_every_other_row_into_a_scan_row_for_the_second_gate(tmp_path, capsys):
    """W2 incelemesi (ORTA): kapi dogrulama satirinin acik kanitina bakmaz. 'sil' ve 'kartta belirt' disindaki her
    ornek mekani ikinci kapinin tarama satiri olur: 'ret' + 'dokunma' -> 'açık' (kanit alanlariyla), geri kalani
    'belirsiz'."""
    cards = [am.venue(slug) for slug in ("acik", "belirsiz", "atlandi", "gecersiz", "kapali", "mevsim")]
    out = sampled(tmp_path, capsys, cards, [
        am.verify("acik"), am.verify("belirsiz", sonuc="onay"), am.verify("gecersiz", sonuc="doğrulandı"),
        am.verify("kapali", **CLOSURE), am.verify("mevsim", eylem="kartta belirt")])
    code, summary = run(capsys, "kanit", out)
    scans = {scan["entry_id"]: scan for scan in rows(out / ad.OPEN_DIR / ad.OPEN_ROWS)}
    assert {entry: scan["durum"] for entry, scan in scans.items()} == {
        am.eid("acik"): "açık", am.eid("belirsiz"): "belirsiz", am.eid("atlandi"): "belirsiz", am.eid("gecersiz"): "belirsiz"}
    assert list(scans[am.eid("acik")].items()) == [
        ("entry_id", am.eid("acik")), ("title", "Acik"), ("durum", "açık"), ("kanit_url", "https://nieuws.example/acik"),
        ("kanit_alinti", "Het museum blijft gewoon open."), ("kanit_tarihi", "2026-05-01"),
        ("not", "denetim: ret + dokunma")]
    assert scans[am.eid("atlandi")]["not"] == "denetim: doğrulama satırı yok"
    listed = rows(out / ad.OPEN_LIST)
    assert sorted(row["entry_id"] for row in listed) == sorted(scans) and all("neden" in row for row in listed)
    assert code == 0 and {key: summary[key] for key in ("orneklem", "liste", "acik", "belirsiz", "kanit_mekan")} == {
        "orneklem": 6, "liste": 4, "acik": 1, "belirsiz": 3, "kanit_mekan": 2}


def test_kanit_lists_the_evidence_and_second_sources_for_fetch_snapshot(tmp_path, capsys):
    """W2 incelemesi (DUSUK): P0/P1 satirlarinin kanit adresi + alintisi ve 'sil'in gerekce'deki her 'adres «alıntı»'
    fetch_snapshot --must-contain bicimindedir; ikinci kaynagi ayni sitede ya da alintisiz olan 'sil' listelenir."""
    cards = [am.venue(slug) for slug in ("kapali", "tek", "mevsim")]
    out = sampled(tmp_path, capsys, cards, [
        am.verify("kapali", **CLOSURE),
        am.verify("tek", eylem="sil", sonuc="onay", gerekce=f"{SINGLE} Arşiv: https://archief.nieuws.example/tek «weg»"),
        am.verify("mevsim", eylem="kartta belirt", gerekce="https://baska.example/x «yok sayılır»")])
    code, summary = run(capsys, "kanit", out)
    folder = out / ad.EVIDENCE_DIR
    expected = {"https://nieuws.example/golf": ["De golfbaan sluit definitief"],
                "https://gemeente.example/nieuws/sluiting": ["definitief gesloten"],
                "https://archief.nieuws.example/golf": ["sluit definitief"],  # sondaki virgul atilir
                "https://nieuws.example/tek": ["Het museum blijft gewoon open."],
                "https://archief.nieuws.example/tek": ["weg"],
                "https://nieuws.example/mevsim": ["Het museum blijft gewoon open."]}
    assert fetch_snapshot.read_must_contain(folder / ad.EVIDENCE_NAME) == expected
    urls = fetch_snapshot.read_url_list(folder / ad.URLS_NAME)
    assert sorted(urls) == sorted(expected) and len(urls) == len(expected)
    roles = {(line["entry_id"], line["rol"]) for line in rows(folder / ad.EVIDENCE_NAME)}
    assert (am.eid("mevsim"), "ikinci_kaynak") not in roles and (am.eid("kapali"), "ikinci_kaynak") in roles
    assert (code, summary["liste"], summary["kanit_adres"], summary["ikinci_alintisiz"]) == (0, 0, 6, [am.eid("tek")])


def test_the_last_row_of_a_venue_decides(tmp_path, capsys):
    out = sampled(tmp_path, capsys, [am.venue("yer")], [am.verify("yer", eylem="sil", gerekce=am.SECOND)])
    am.write_jsonl(out / ad.BATCH_DIR / "parti_02_dogrulama.jsonl", [am.verify("yer")])
    code, summary = run(capsys, "kanit", out)
    assert (code, summary["acik"], summary["kanit_mekan"]) == (0, 1, 0)


# ------------------------------------------------------------------ sayim


def second_gate(out: Path, capsys) -> int:
    code, _ = am.run_main(capsys, [out / ad.OPEN_DIR, "--mekanlar", out / ad.OPEN_LIST, "--min-year", am.MIN_YEAR,
                                   "--out", out / ad.OPEN_REPORT])
    return code


def copies(out: Path, capsys, routes: dict = ROUTES) -> int:
    folder = out / ad.EVIDENCE_DIR
    code = fetch_snapshot.main(["--urls", str(folder / ad.URLS_NAME), "--must-contain", str(folder / ad.EVIDENCE_NAME),
                                "--out-dir", str(folder), "--cache-dir", str(out / "_cache")],
                               transport=FakeTransport(routes), sleep=lambda seconds: None, clock=lambda: "2026-10-23")
    capsys.readouterr()
    return code


def test_sayim_classifies_every_sampled_venue_from_the_gate_and_the_copies(tmp_path, capsys):
    """W2 incelemesi (ORTA + DUSUK): dogrulanan/dogrulanamayan ana dongunun elle kontrolunden degil, ikinci kapinin
    raporundan ve kanit kopyasindan. Telif satiri ve eski tarih bulgu verir; kapanis yalniz iki ayri sitenin alintisi
    kopyada bulununca 'iki kaynak'; teyitsiz kanit ve bulgulu 'açık' karari bir kez yeni ajana."""
    names = ("acik", "telif", "eski", "belirsiz", "atlandi", "kapali", "tek", "mevsim", "kayip")
    out = sampled(tmp_path, capsys, [am.venue(slug) for slug in names[:8]], [
        am.verify("acik"), am.verify("telif", **FOOTER),
        am.verify("eski", kanit_alinti="Golfbaan Welschap blijft open", kanit_tarihi="2019-03-01 (haber tarihi)"),
        am.verify("belirsiz", sonuc="onay"), am.verify("kapali", **CLOSURE),
        am.verify("tek", eylem="sil", sonuc="onay", gerekce=SINGLE), am.verify("mevsim", eylem="kartta belirt")])
    assert run(capsys, "kanit", out)[0] == 0 and second_gate(out, capsys) == 1 and copies(out, capsys) == 1
    code, summary = run(capsys, "sayim", out)
    report = json.loads((out / ad.COUNT_NAME).read_text(encoding="utf-8"))
    found = {item["entry_id"]: (item["sinif"], item["kodlar"]) for item in report["mekanlar"]}
    assert found == {
        am.eid("acik"): ("acik_dogrulandi", []), am.eid("telif"): ("dogrulanamadi", ["eski_kanit", "footer_kanit"]),
        am.eid("eski"): ("dogrulanamadi", ["eski_kanit"]), am.eid("belirsiz"): ("dogrulanamadi", ["dogrulama_yok"]),
        am.eid("atlandi"): ("dogrulanamadi", ["dogrulama_yok", "bos_alinti", "bos_url"]),
        am.eid("kapali"): ("kapanis_iki_kaynak", []), am.eid("tek"): ("kapanis_teyitsiz", []),
        am.eid("mevsim"): ("belirt_teyitli", [])}
    details = {item["entry_id"]: item for item in report["mekanlar"]}
    assert details[am.eid("kapali")]["teyitsiz"] == ["https://archief.nieuws.example/golf"]
    assert sorted(summary["yeni_ajan"]) == sorted(am.eid(slug) for slug in ("telif", "eski", "tek"))
    assert (code, summary["orneklem"], summary["dogrulanan"], summary["dogrulanamayan"]) == (0, 8, 3, 5)
    assert summary["sinif"] == {"acik_dogrulandi": 1, "dogrulanamadi": 4, "kapanis_iki_kaynak": 1,
                                "kapanis_teyitsiz": 1, "belirt_teyitli": 1, "belirt_teyitsiz": 0}


def test_a_quote_missing_from_its_page_is_not_confirmed(tmp_path, capsys):
    """Ayni adresi iki mekan anarsa bayrak adres duzeyindedir; teyit alinti duzeyinde (evidence.missing)."""
    out = sampled(tmp_path, capsys, [am.venue("mevsim"), am.venue("kayip")], [
        am.verify("mevsim", eylem="kartta belirt", kanit_url="https://nieuws.example/mevsim"),
        am.verify("kayip", eylem="kartta belirt", kanit_url="https://nieuws.example/mevsim", kanit_alinti="Gesloten.")])
    assert run(capsys, "kanit", out)[0] == 0 and copies(out, capsys) == 1
    code, summary = run(capsys, "sayim", out)
    assert code == 0 and summary["sinif"]["belirt_teyitli"] == 1 and summary["sinif"]["belirt_teyitsiz"] == 1
    assert summary["yeni_ajan"] == [am.eid("kayip")] and summary["dogrulanamayan"] == 1


def test_sayim_refuses_outputs_older_than_the_agent_rows(tmp_path, capsys):
    out = sampled(tmp_path, capsys, [am.venue("yer"), am.venue("golf")], [am.verify("yer"), am.verify("golf", **CLOSURE)])
    assert run(capsys, "kanit", out)[0] == 0
    code, summary = run(capsys, "sayim", out)
    assert code == 2 and ad.OPEN_REPORT in summary["error"], summary  # ikinci kapi calismadi
    second_gate(out, capsys)
    code, summary = run(capsys, "sayim", out)
    assert code == 2 and "fetch_snapshot" in summary["error"], summary
    copies(out, capsys)
    assert run(capsys, "sayim", out)[0] == 0
    am.write_jsonl(out / ad.BATCH_DIR / "parti_01_dogrulama.jsonl", [am.verify("yer", sonuc="onay"),
                                                                     am.verify("golf", **CLOSURE)])  # yeni ajan
    code, summary = run(capsys, "sayim", out)
    assert code == 2 and "kanit" in summary["error"], summary
    assert run(capsys, "kanit", out)[0] == 0 and not (out / ad.OPEN_REPORT).exists()  # eski rapor kalmaz
    report = out / ad.OPEN_REPORT
    report.write_text(json.dumps({"acik_mi": str(tmp_path), "mekan": 1, "findings": []}), encoding="utf-8")
    code, summary = run(capsys, "sayim", out)
    assert code == 2 and "raporu değil" in summary["error"], summary


def test_cli_prints_one_utf8_json_line(tmp_path):
    out, xlsx = setup(tmp_path, [am.venue("yer")])
    env = {key: value for key, value in os.environ.items() if key not in ("PYTHONUTF8", "PYTHONIOENCODING")}
    done = subprocess.run([sys.executable, str(SCRIPT), "orneklem", str(out), "--xlsx", str(xlsx.parent / "yok.xlsx")],
                          capture_output=True, text=True, encoding="utf-8", env={**env, "PYTHONDONTWRITEBYTECODE": "1"},
                          timeout=60, check=False)
    lines = done.stdout.strip().splitlines()
    assert done.returncode == 2 and len(lines) == 1 and "bulunamadı" in json.loads(lines[0])["error"], done.stderr
