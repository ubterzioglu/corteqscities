"""add_sources: yeni kaynak adreslerini alt klasore kopyalar, must_contain kanitini arar, kimlik verir (A6; pilot kaynak_ekle.py).

Ag yok: fetch_snapshot surec icinde sahte tasima katmaniyla calisir.
"""
from __future__ import annotations

import errno
import hashlib
import json
import os
import time
from pathlib import Path

import pytest

import add_sources as ad
from web_fetch import NetworkError, RawResponse

LONG = " ".join(["De gemeente registreert nieuwe inwoners binnen vijf dagen na aankomst."] * 10)
PAGE = (f"<html><head><title>Inschrijven | Gemeente</title></head><body><main><p>{LONG}</p>"
        "<p>Afspraak   maken is GRATIS.</p></main></body></html>").encode("utf-8")
SOFT_404 = (f"<html><head><title>Pagina niet gevonden | Gemeente</title></head><body><main><p>{LONG}</p></main>"
            "</body></html>").encode("utf-8")  # 200 doner, metin uzun (ince degil) ama sayfa yok
SHELL = b"<html><head><title>App</title></head><body><div id='root'></div></body></html>"
NEW, OLD = "https://a.example.org/inschrijven", "https://old.example.org/bron"
THIN, NOEVID, GONE = "https://b.example.org/app", "https://c.example.org/pagina", "https://d.example.org/weg"
EVIDENCE = "Afspraak maken is gratis."


def html(body: bytes = PAGE, code: int = 200) -> RawResponse:
    return RawResponse(code, {"Content-Type": "text/html; charset=utf-8"}, body)


class FakeTransport:
    """Sahte tasima: url -> yanit (ya da firlatilacak hata); bilinmeyen adres 404. Cagri gunlugu tutar."""

    def __init__(self, routes: dict) -> None:
        self.routes, self.calls = routes, []

    def __call__(self, method, url, headers, timeout, body_limit):
        self.calls.append((method, url))
        item = self.routes.get(url, html(b"<title>Not Found</title>", 404))
        if isinstance(item, Exception):
            raise item
        return item


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_work(tmp_path: Path, existing=(("testville:kaynak:007", OLD),)) -> Path:
    work = tmp_path / "is"
    work.mkdir()
    write_jsonl(work / "kaynak_dizini.jsonl", [
        {"source_id": sid, "topic": "genel", "url": link, "final_url": link, "title": "Oud", "publisher": "old",
         "lang": "nl", "text_file": str(work / "snap" / "x.txt"), "text_chars": 900, "html_file": "x.html",
         "html_sha256": "0" * 64, "why": "eski"} for sid, link in existing])
    write_jsonl(work / "kaynak_taslak.jsonl", [
        {"source_id": sid, "city_id": "testville", "title": "Oud", "publisher": "old", "url": link,
         "checked_on": "2026-10-01", "topic": "testville:genel", "summary": "eski", "verified": "Hayır"}
        for sid, link in existing])
    return work


def candidates(tmp_path: Path, rows: list[dict], name: str = "aday.jsonl") -> Path:
    return write_jsonl(tmp_path / name, rows)


def run(capsys, work: Path, cands: Path, fake, *extra: str, sub: str = "snap_ek", topic: str = "kesif",
        city: str = "testville"):
    code = ad.main([str(work), "--candidates", str(cands), "--subdir", sub, "--topic", topic, "--city-id", city, *extra],
                   transport=fake, sleep=lambda s: None, clock=lambda: "2026-10-22")
    lines = capsys.readouterr().out.strip().splitlines()
    return code, (json.loads(lines[-1]) if lines else None), lines


# ---------------------------------------------------------------- mutlu yol

def test_new_url_gets_next_city_id_and_known_url_is_reused(tmp_path, capsys):
    work = make_work(tmp_path)
    cands = candidates(tmp_path, [
        {"url": NEW, "must_contain": [EVIDENCE], "title": "Inschrijven", "publisher": "Gemeente", "lang": "nl",
         "why": "kayıt adımları"},
        {"url": OLD + " ", "must_contain": []}])  # bosluk kirpilir
    code, summary, lines = run(capsys, work, cands, FakeTransport({NEW: html(), OLD: html()}))
    assert code == ad.EXIT_OK and len(lines) == 1  # fetch_snapshot ozeti stdout'a sizmaz
    assert (summary["added"], summary["reused"], summary["rejected"], summary["candidates"]) == (1, 1, 0, 2)
    new, sha = read_jsonl(work / "kaynak_dizini.jsonl")[-1], hashlib.sha256(PAGE).hexdigest()
    assert (new["source_id"], new["topic"], new["url"], new["lang"]) == ("testville:kaynak:008", "kesif", NEW, "nl")
    assert new["html_file"] == os.path.join("snap_ek", f"{sha}.html") and (work / new["html_file"]).is_file()
    assert new["html_sha256"] == sha and new["why"] == "kayıt adımları" and new["title"] == "Inschrijven | Gemeente"
    assert Path(new["text_file"]).is_absolute() and Path(new["text_file"]).is_file()
    assert read_jsonl(work / "kaynak_taslak.jsonl")[-1] == {
        "source_id": "testville:kaynak:008", "city_id": "testville", "title": "Inschrijven | Gemeente",
        "publisher": "Gemeente", "url": NEW, "checked_on": "2026-10-22", "topic": "testville:kesif",
        "summary": "kayıt adımları", "verified": "Hayır"}
    detail = json.loads((work / "snap_ek" / "eklenen.json").read_text(encoding="utf-8"))
    assert detail["map"] == {NEW: "testville:kaynak:008", OLD: "testville:kaynak:007"} and detail["rejected"] == []
    assert (work / "snap_ek" / "urls.txt").read_text(encoding="utf-8").splitlines() == [NEW, OLD]


def test_existing_rows_are_preserved_byte_for_byte(tmp_path, capsys):
    work = make_work(tmp_path)
    before = (work / "kaynak_dizini.jsonl").read_bytes()
    run(capsys, work, candidates(tmp_path, [{"url": NEW}]), FakeTransport({NEW: html()}))
    after = (work / "kaynak_dizini.jsonl").read_bytes()
    assert after.startswith(before) and after.count(b"\n") == before.count(b"\n") + 1


@pytest.mark.parametrize("newline", [b"\n", b"\r\n"])
def test_lf_and_crlf_files_keep_their_bytes_and_line_ending(tmp_path, capsys, newline):
    """Windows'ta metin kipi LF dosyayi CRLF'e ceviriyordu (fixture'lar CRLF oldugu icin gorunmuyordu)."""
    work = make_work(tmp_path)
    names = ("kaynak_dizini.jsonl", "kaynak_taslak.jsonl")
    for name in names:
        path = work / name
        path.write_bytes(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", newline))
    before = {name: (work / name).read_bytes() for name in names}
    code, _, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), FakeTransport({NEW: html()}))
    assert code == ad.EXIT_OK
    for name in names:
        after = (work / name).read_bytes()
        assert after.startswith(before[name]) and after.count(newline) == before[name].count(newline) + 1, name
        assert after.count(b"\n") == after.count(newline), name  # tek tip satir sonu


def test_second_run_is_served_from_cache_and_reuses_id(tmp_path, capsys):
    work = make_work(tmp_path)
    cands = candidates(tmp_path, [{"url": NEW, "must_contain": [EVIDENCE]}])
    run(capsys, work, cands, FakeTransport({NEW: html()}))
    index_before = (work / "kaynak_dizini.jsonl").read_bytes()
    offline = FakeTransport({})
    code, summary, _ = run(capsys, work, cands, offline)
    assert offline.calls == [] and code == ad.EXIT_OK and (summary["added"], summary["reused"]) == (0, 1)
    assert (work / "kaynak_dizini.jsonl").read_bytes() == index_before


def test_numbering_continues_from_city_max_and_ignores_foreign_ids(tmp_path, capsys):
    work = make_work(tmp_path, [("otherville:kaynak:999", "https://o.example.org/"), ("testville:kaynak:012", OLD),
                                ("testville:kaynak:ekstra", "https://e.example.org/")])
    code, _, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), FakeTransport({NEW: html()}))
    assert code == ad.EXIT_OK and read_jsonl(work / "kaynak_dizini.jsonl")[-1]["source_id"] == "testville:kaynak:013"


def test_empty_index_starts_at_001_and_string_must_contain_is_one_phrase(tmp_path, capsys):
    work = make_work(tmp_path, ())
    code, _, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW, "must_contain": EVIDENCE}]),
                     FakeTransport({NEW: html()}))
    assert code == ad.EXIT_OK and read_jsonl(work / "kaynak_dizini.jsonl")[-1]["source_id"] == "testville:kaynak:001"


def test_source_added_by_another_editor_during_fetch_is_not_overwritten_or_reused(tmp_path, capsys):
    """Paralel editor (B6): indirme surerken baska bir kosu kaynak eklerse yeni kimlik ondan sonra gelmeli."""
    work = make_work(tmp_path)
    other = {"source_id": "testville:kaynak:050", "topic": "genel", "url": "https://p.example.org/", "why": "paralel"}

    class ParallelEditor(FakeTransport):
        def __call__(self, method, url, headers, timeout, body_limit):
            with (work / "kaynak_dizini.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(other) + "\n")
            return super().__call__(method, url, headers, timeout, body_limit)

    code, _, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), ParallelEditor({NEW: html()}))
    ids = [r["source_id"] for r in read_jsonl(work / "kaynak_dizini.jsonl")]
    assert code == ad.EXIT_OK and ids == ["testville:kaynak:007", "testville:kaynak:050", "testville:kaynak:051"]


def test_live_lock_is_never_taken_over_however_old_the_file(tmp_path, capsys, monkeypatch):
    """Yaris: iki bekleyen ayni 'bayat' kilidi gorup biri digerinin taze kilidini silerse ikisi birden yazar. Kilit
    sahibi yasadikca (dosya yasi ne olursa olsun) bekleyen devralmaz; zaman asiminda dizine yazmadan durur."""
    work = make_work(tmp_path)
    monkeypatch.setattr(ad, "LOCK_TIMEOUT_SECONDS", 0.05)
    cands = candidates(tmp_path, [{"url": NEW}])
    with ad.index_lock(work, lambda s: None):  # baska bir editorun kosusu kritik bolumde
        old = time.time() - 3600
        os.utime(work / ad.LOCK_NAME, (old, old))
        code, _, _ = run(capsys, work, cands, FakeTransport({NEW: html()}))
        assert code == ad.EXIT_USAGE and len(read_jsonl(work / "kaynak_dizini.jsonl")) == 1
    code, summary, _ = run(capsys, work, cands, FakeTransport({NEW: html()}))
    assert code == ad.EXIT_OK and summary["added"] == 1


def test_lock_file_left_by_crashed_run_does_not_block_and_is_not_deleted(tmp_path, monkeypatch):
    """Coken kosunun kilidi isletim sistemince birakilir: kalan dosya beklemeden alinir. Dosya hic silinmez (silmek,
    baska surecin kilidini silme yarisini geri getirir)."""
    monkeypatch.setattr(ad, "LOCK_TIMEOUT_SECONDS", 0.05)
    lock = tmp_path / ad.LOCK_NAME
    lock.write_text("12345\n", encoding="ascii")
    waits: list[float] = []
    with ad.index_lock(tmp_path, waits.append):
        assert waits == []
    with ad.index_lock(tmp_path, waits.append):  # birakildiysa yeniden alinir
        pass
    assert waits == [] and lock.exists()


# ---------------------------------------------------------------- kirma testleri

def test_thin_copy_missing_evidence_and_404_are_rejected(tmp_path, capsys):
    work = make_work(tmp_path)
    before = (work / "kaynak_dizini.jsonl").read_bytes(), (work / "kaynak_taslak.jsonl").read_bytes()
    cands = candidates(tmp_path, [{"url": THIN}, {"url": NOEVID, "must_contain": ["Bestaat niet"]}, {"url": GONE},
                                  {"url": THIN}])  # tekrar eden adres bir kez degerlendirilir
    code, summary, _ = run(capsys, work, cands, FakeTransport({THIN: html(SHELL), NOEVID: html()}))
    detail = json.loads((work / "snap_ek" / "eklenen.json").read_text(encoding="utf-8"))
    whys = {r["url"]: r["why"] for r in detail["rejected"]}
    assert code == ad.EXIT_FINDINGS and summary["status"] == "findings"
    assert (summary["rejected"], summary["added"]) == (3, 0) and len(detail["rejected"]) == 3
    assert "ince" in whys[THIN] and "kanit metinde yok" in whys[NOEVID] and "status 404" in whys[GONE]
    assert ((work / "kaynak_dizini.jsonl").read_bytes(), (work / "kaynak_taslak.jsonl").read_bytes()) == before


def test_soft_404_page_is_rejected_even_without_must_contain(tmp_path, capsys):
    """200 donen 'Pagina niet gevonden' sayfasi kimlik almamali (Baglantilar uzerinden verified=Evet kaynak olurdu)."""
    work = make_work(tmp_path)
    before = (work / "kaynak_dizini.jsonl").read_bytes(), (work / "kaynak_taslak.jsonl").read_bytes()
    cands = candidates(tmp_path, [{"url": NEW, "must_contain": []}])
    code, summary, _ = run(capsys, work, cands, FakeTransport({NEW: html(SOFT_404)}))
    detail = json.loads((work / "snap_ek" / "eklenen.json").read_text(encoding="utf-8"))
    assert code == ad.EXIT_FINDINGS and (summary["added"], summary["rejected"]) == (0, 1) and detail["map"] == {}
    assert "soft-404" in detail["rejected"][0]["why"] and "niet gevonden" in detail["rejected"][0]["why"]
    assert ((work / "kaynak_dizini.jsonl").read_bytes(), (work / "kaynak_taslak.jsonl").read_bytes()) == before


def test_retry_transient_is_default_and_can_be_disabled(tmp_path, capsys):
    work = make_work(tmp_path)
    cands = candidates(tmp_path, [{"url": NEW}])
    code, _, _ = run(capsys, work, cands, FakeTransport({NEW: html(b"busy", 503)}))
    assert code == ad.EXIT_FINDINGS
    frozen = FakeTransport({NEW: html()})
    code, _, _ = run(capsys, work, cands, frozen, "--no-retry-transient")
    assert code == ad.EXIT_FINDINGS and frozen.calls == []  # onbellekteki 503 aynen kullanildi
    fresh = FakeTransport({NEW: html()})
    code, summary, _ = run(capsys, work, cands, fresh)
    assert code == ad.EXIT_OK and len(fresh.calls) == 1 and summary["added"] == 1


def test_network_error_is_a_rejection_not_a_crash(tmp_path, capsys):
    work = make_work(tmp_path)
    fake = FakeTransport({NEW: NetworkError("tls", "certificate verify failed")})
    code, summary, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), fake)
    assert code == ad.EXIT_FINDINGS and summary["rejected"] == 1


@pytest.mark.parametrize("sub", ["snap", "SNAP", "../disari", "data", "snap_ek/alt", ""])
def test_main_snapshot_or_unsafe_subdir_is_refused(tmp_path, capsys, sub):
    work = make_work(tmp_path)
    fake = FakeTransport({NEW: html()})
    code, _, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), fake, sub=sub)
    assert code == ad.EXIT_USAGE and fake.calls == []


def test_usage_errors_exit_2(tmp_path, capsys):
    work = make_work(tmp_path)
    good = candidates(tmp_path, [{"url": NEW}])
    fake = FakeTransport({})
    assert run(capsys, work, good, fake, city="Bad City")[0] == ad.EXIT_USAGE
    assert run(capsys, work, good, fake, topic="Kötü Konu")[0] == ad.EXIT_USAGE
    broken = tmp_path / "bozuk.jsonl"
    broken.write_text("{oops\n", encoding="utf-8")
    assert run(capsys, work, broken, fake)[0] == ad.EXIT_USAGE
    wrong = candidates(tmp_path, [{"url": NEW, "must_contain": {"a": 1}}], "yanlis.jsonl")
    assert run(capsys, work, wrong, fake)[0] == ad.EXIT_USAGE
    assert run(capsys, work, tmp_path / "yok.jsonl", fake)[0] == ad.EXIT_USAGE
    bare = tmp_path / "dizinsiz"  # dizin dosyasi hic yazilmaz: az once yazilani silmek antivirus tutarken WinError 32
    bare.mkdir()
    (bare / "kaynak_taslak.jsonl").write_text("", encoding="utf-8")
    assert run(capsys, bare, good, fake)[0] == ad.EXIT_USAGE
    assert fake.calls == [] and ad.main(["--help"]) == ad.EXIT_OK


def test_unreadable_input_and_failed_writes_exit_2_not_1(tmp_path, capsys):
    """Beklenmeyen hata main disina kacarsa Python cikisi 1 olur ve 'bulgu' ile karisir."""
    work = make_work(tmp_path)
    fake = FakeTransport({NEW: html()})
    argv = [str(work), "--candidates", str(candidates(tmp_path, [{"url": NEW}])), "--subdir", "snap_ek", "--topic", "kesif",
            "--city-id", "testville"]

    def main(*extra: str) -> int:
        capsys.readouterr()
        return ad.main([*argv, *extra], transport=fake, sleep=lambda s: None, clock=lambda: "2026-10-22")

    index = work / "kaynak_dizini.jsonl"
    original = index.read_bytes()
    index.write_bytes(original + '{"title": "Müze"}\n'.encode("cp1252"))  # UTF-8 olmayan satir
    assert main() == ad.EXIT_USAGE and "kaynak_dizini.jsonl: UTF-8 degil" in capsys.readouterr().err
    index.write_bytes(original)
    (work / "snap_ek").write_text("klasor degil", encoding="utf-8")  # kopya klasoru kurulamaz
    assert main() == ad.EXIT_USAGE and fake.calls == [] and "HATA" in capsys.readouterr().err
    (work / "snap_ek").unlink()
    folder = tmp_path / "rapor_klasoru"
    folder.mkdir()
    assert main("--out", str(folder)) == ad.EXIT_USAGE and "HATA" in capsys.readouterr().err  # ayrinti yazilamaz


# ---------------------------------------------------------------- kilitli dosya (Windows os.replace)

JSONL_NAMES = (ad.INDEX_NAME, ad.DRAFT_NAME)
UNCHANGED = f"{ad.INDEX_NAME} ve {ad.DRAFT_NAME} kosudan onceki gibi"  # mesajdaki dosya durumu: ikisi de ayni
DENIED = PermissionError(errno.EACCES, "Erisim engellendi")
INVALID = OSError(errno.EINVAL, "Gecersiz arguman")
ADDED_DRAFT_ROW = {"source_id": "testville:kaynak:008", "city_id": "testville", "title": "Inschrijven | Gemeente",
                   "publisher": "Gemeente", "url": NEW, "checked_on": "2026-10-22", "topic": "testville:kesif",
                   "summary": "kayıt adımları", "verified": "Hayır"}


class FakeLock:
    """Windows dosya kilidi taklidi (os.replace sahtesi). plan[hedef adi]: o hedefe sirayla yapilan denemelerin sonucu,
    son oge tekrar eder; None gercek os.replace, hata ogesi o hatayi firlatir. calls: izlenen hedeflere mantiksal
    denemeler (kaynak, hedef, 'ok'/'ret'). Gercek hata (antivirusun kisa kilidi) kaydedilmez, sayilmaz ve ardindan
    gercekten beklenir: kod yeniden dener, test kararsizlasmaz. Sahte retten sonraki bekleme yalniz waits'e yazilir."""

    def __init__(self, monkeypatch, plan: dict[str, list]) -> None:
        self.plan, self.calls, self.waits, self.faked = plan, [], [], False
        self.real_replace, self.real_sleep = os.replace, time.sleep
        monkeypatch.setattr(ad.os, "replace", self.replace)
        monkeypatch.setattr(ad.time, "sleep", self.sleep)

    def replace(self, src, dst) -> None:
        name = Path(dst).name
        steps = self.plan.get(name, [None])
        error = steps[min(sum(call[1] == name for call in self.calls), len(steps) - 1)]
        self.faked = error is not None
        if error is None:
            self.real_replace(src, dst)  # gercek hata buradan yukari gider, kaydedilmez
        if name in self.plan:
            self.calls.append((Path(src).name, name, "ret" if error else "ok"))
        if error is not None:
            raise type(error)(*error.args)

    def sleep(self, seconds: float) -> None:
        if self.faked:
            self.waits.append(seconds)
        else:
            self.real_sleep(seconds)


def run_err(capsys, work: Path, cands: Path) -> tuple[int, str, str]:
    """Kosu (sahte tasima NEW'i verir): cikis, stdout ve stderr (hata mesaji)."""
    code = ad.main([str(work), "--candidates", str(cands), "--subdir", "snap_ek", "--topic", "kesif", "--city-id",
                    "testville"], transport=FakeTransport({NEW: html()}), sleep=lambda s: None,
                   clock=lambda: "2026-10-22")
    out, err = capsys.readouterr()
    return code, out, err


def test_index_briefly_held_open_by_another_program_is_retried(tmp_path, capsys, monkeypatch):
    """Windows: baska program (antivirus, dizinleyici, Excel) dizini acik tutarken os.replace gercek WinError 5 verir
    (tam kosuda bir kez gorulen kararsiz test_documented_add_sources_runs_keep_every_eklenen_json). Program dosyayi ilk
    basarisiz denemeden sonra birakir: kosu geri cekilip yeniden dener ve tamamlanir. Bekleme gercek zamanlidir
    (time.sleep): main'e verilen sleep testlerde bostur, kilidi gecirmez. Test de gercekten bekler: antivirusun
    make_work'un az once yazdigi dosyalardaki kisa kilidi bu testi dusurmez."""
    work = make_work(tmp_path)
    index = work / "kaynak_dizini.jsonl"
    before, holder, failures, waits = index.read_bytes(), index.open("rb"), [], []
    real_replace = os.replace

    def replace(src, dst):
        try:
            return real_replace(src, dst)
        except PermissionError as error:
            if Path(dst) == index:
                failures.append(getattr(error, "winerror", error.errno))
                holder.close()  # diger program dosyayi birakti
            raise

    real_sleep = time.sleep
    monkeypatch.setattr(ad.os, "replace", replace)
    monkeypatch.setattr(ad.time, "sleep", lambda seconds: (waits.append(seconds), real_sleep(seconds)))
    try:
        code, summary, _ = run(capsys, work, candidates(tmp_path, [{"url": NEW}]), FakeTransport({NEW: html()}))
    finally:
        holder.close()
    blocked = os.name == "nt"  # POSIX acik dosyanin yerine yazmaya izin verir; kilit yalniz Windows'ta olusur
    assert failures[:1] == ([5] if blocked else []) and bool(waits) == blocked
    assert code == ad.EXIT_OK and summary["added"] == 1
    assert index.read_bytes().startswith(before) and read_jsonl(index)[-1]["url"] == NEW
    assert read_jsonl(work / "kaynak_taslak.jsonl")[-1]["url"] == NEW and not list(work.glob("*.tmp"))


@pytest.mark.parametrize("locked, error, tries, message", [
    (ad.INDEX_NAME, DENIED, 5, "kaynak_dizini.jsonl yazilamadi: 5 denemede"),
    (ad.DRAFT_NAME, DENIED, 5, "kaynak_taslak.jsonl yazilamadi: 5 denemede"),
    (ad.INDEX_NAME, INVALID, 1, "Gecersiz arguman"),
    (ad.DRAFT_NAME, INVALID, 1, "Gecersiz arguman")],
    ids=["dizin_kilitli", "taslak_kilitli", "dizin_baska_hata", "taslak_baska_hata"])
def test_file_that_stays_unwritable_exits_2_and_leaves_both_files_untouched(tmp_path, capsys, monkeypatch, locked,
                                                                            error, tries, message):
    """Kilit kalkmazsa 5 deneme (aralarda 0,1-0,5 sn artan bekleme), sonra acik mesaj + cikis 2; yalniz PermissionError
    yeniden denenir, baska OSError beklemeden durur. Once dizin yazilir; taslak yazilamazsa (or. Excel'de acik) dizin
    eski baytlarina doner. Eskiden dizin yeni kimligi tutuyor, taslak tutmuyor, mesaj yine 'degismedi' diyordu. Iki
    dosya bayt bayt ayni ve mesaj bunu soyler; gecici dosya, eklenen.json, ozet yok."""
    work = make_work(tmp_path)
    before = {name: (work / name).read_bytes() for name in JSONL_NAMES}
    lock = FakeLock(monkeypatch, {**{name: [None] for name in JSONL_NAMES}, locked: [error]})
    code, out, err = run_err(capsys, work, candidates(tmp_path, [{"url": NEW}]))
    assert code == ad.EXIT_USAGE and out == "" and err.startswith("HATA:") and message in err and UNCHANGED in err
    index_ok, refused = [(f"{ad.INDEX_NAME}.tmp", ad.INDEX_NAME, "ok")], [(f"{locked}.tmp", locked, "ret")] * tries
    assert lock.calls == (refused if locked == ad.INDEX_NAME else index_ok + refused + index_ok)  # yaz, dene, geri al
    assert len(lock.waits) == tries - 1 and all(0.1 <= w <= 0.5 for w in lock.waits)
    assert all(a < b for a, b in zip(lock.waits, lock.waits[1:]))  # artan: sabit bekleme kabul edilmez
    assert {name: (work / name).read_bytes() for name in JSONL_NAMES} == before
    assert not list(work.glob("*.tmp")) and not (work / "snap_ek" / ad.DETAIL_NAME).exists()


def test_failed_rollback_names_ids_left_in_index_and_rerun_repairs_draft(tmp_path, capsys, monkeypatch):
    """Taslak kilitli ve dizin de geri alinamazsa mesaj dizinde kalan kimligi ve cozumu soyler. Kilit surerken yeniden
    kosu dizine dokunmaz; kilit kalkinca ayni adaylarla kosu yeni kimlik vermez, eksik taslak satirini ekler. Eskiden
    'reused' deyip taslagi eksik birakiyordu: merge_package source_not_in_draft verir, elle duzeltme yasak (cikmaz)."""
    work = make_work(tmp_path)
    draft_before = (work / ad.DRAFT_NAME).read_bytes()
    cands = candidates(tmp_path, [{"url": NEW, "must_contain": [EVIDENCE], "publisher": "Gemeente",
                                   "why": "kayıt adımları"}])
    with monkeypatch.context() as patch:
        lock = FakeLock(patch, {ad.INDEX_NAME: [None, DENIED], ad.DRAFT_NAME: [DENIED]})  # yazim olur, geri alma olmaz
        code, out, err = run_err(capsys, work, cands)
        assert code == ad.EXIT_USAGE and out == "" and "kaynak_taslak.jsonl yazilamadi: 5 denemede" in err
        assert "testville:kaynak:008 dizinde var, taslakta yok" in err and "yeniden kosu" in err
        assert UNCHANGED not in err
        stuck = (work / ad.INDEX_NAME).read_bytes()
        assert [r["source_id"] for r in read_jsonl(work / ad.INDEX_NAME)] == ["testville:kaynak:007",
                                                                              "testville:kaynak:008"]
        assert (work / ad.DRAFT_NAME).read_bytes() == draft_before and not list(work.glob("*.tmp"))
        lock.calls.clear()
        code, out, err = run_err(capsys, work, cands)  # kilit suruyor: yalniz taslak onarimi denenir
        assert code == ad.EXIT_USAGE and UNCHANGED in err and {call[1] for call in lock.calls} == {ad.DRAFT_NAME}
        assert (work / ad.INDEX_NAME).read_bytes() == stuck and (work / ad.DRAFT_NAME).read_bytes() == draft_before
    code, summary, _ = run(capsys, work, cands, FakeTransport({NEW: html()}))
    assert code == ad.EXIT_OK and (summary["added"], summary["reused"], summary["draft_repaired"]) == (0, 1, 1)
    draft = (work / ad.DRAFT_NAME).read_bytes()
    assert (work / ad.INDEX_NAME).read_bytes() == stuck and draft.startswith(draft_before)
    assert read_jsonl(work / ad.DRAFT_NAME)[1:] == [ADDED_DRAFT_ROW]
    code, summary, _ = run(capsys, work, cands, FakeTransport({}))  # onarildi: bir daha eklenmez
    assert code == ad.EXIT_OK and summary["draft_repaired"] == 0 and (work / ad.DRAFT_NAME).read_bytes() == draft


def test_missing_draft_row_is_rebuilt_from_its_index_row_when_url_comes_again(tmp_path, capsys):
    """Eski surumun biraktigi durum: dizinde 008 var, taslakta yok. Adres baska konuda, baska notla yeniden gelince
    kimlik yeniden kullanilir; taslak satiri dizin satirinin konusu, basligi, yayincisi ve notuyla kurulur (iki dosya
    ayni kaydi anlatir), tarih bu kosunun kopyasindan. Dizin degismez."""
    work = make_work(tmp_path)
    with (work / ad.INDEX_NAME).open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"source_id": "testville:kaynak:008", "topic": "kesif", "url": NEW, "final_url": NEW,
                                 "title": "Inschrijven (eski)", "publisher": "Gemeente", "lang": "nl",
                                 "why": "kayıt adımları"}, ensure_ascii=False) + "\n")
    index_before = (work / ad.INDEX_NAME).read_bytes()
    cands = candidates(tmp_path, [{"url": NEW, "title": "Aday", "publisher": "Başka", "why": "başka not"}])
    code, summary, _ = run(capsys, work, cands, FakeTransport({NEW: html()}), topic="mahalle")
    assert code == ad.EXIT_OK and (summary["added"], summary["reused"], summary["draft_repaired"]) == (0, 1, 1)
    detail = json.loads((work / "snap_ek" / ad.DETAIL_NAME).read_text(encoding="utf-8"))
    assert detail["map"] == {NEW: "testville:kaynak:008"} and (work / ad.INDEX_NAME).read_bytes() == index_before
    assert read_jsonl(work / ad.DRAFT_NAME)[1:] == [{**ADDED_DRAFT_ROW, "title": "Inschrijven (eski)"}]


def test_interrupt_while_draft_is_written_rolls_index_back(tmp_path, capsys, monkeypatch):
    """Ctrl+C taslak yazilirken (or. kilit beklemesinde) gelirse de dizin yeni kimligi taslaksiz tutmaz."""
    work = make_work(tmp_path)
    before = {name: (work / name).read_bytes() for name in JSONL_NAMES}
    lock = FakeLock(monkeypatch, {ad.INDEX_NAME: [None], ad.DRAFT_NAME: [KeyboardInterrupt()]})
    with pytest.raises(KeyboardInterrupt):
        run_err(capsys, work, candidates(tmp_path, [{"url": NEW}]))
    assert [call[1] for call in lock.calls] == [ad.INDEX_NAME, ad.DRAFT_NAME, ad.INDEX_NAME]
    assert {name: (work / name).read_bytes() for name in JSONL_NAMES} == before and not list(work.glob("*.tmp"))
