"""fetch_snapshot: ham HTML + ana metin snapshot'i, index.jsonl, thin_text, onbellek (K76, T09). Ag yok."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

import fetch_snapshot as fs
import url_check as uc
import web_fetch as wf
from test_url_check import make_workbook
from test_web_fetch import FakeTransport, ok, redirect, status
from web_fetch import NetworkError

LONG_P = " ".join(["Inwoners van Eindhoven schrijven zich in bij de gemeente binnen vijf dagen na aankomst."] * 8)
PAGE = f"""<!doctype html><html><head><title> Inschrijven
  | Gemeente Eindhoven </title><style>.x{{color:red}}</style><script>var tracking = 1;</script></head>
<body><nav><a href="/">Home</a> Menu</nav><header>Kop</header>
<main><h1>Inschrijven</h1><p>{LONG_P}</p><p>Tweede   alinea
met   spaties.</p></main><footer>Cookies en privacy</footer><noscript>JS uit</noscript></body></html>""".encode("utf-8")
SHELL = b"<html><head><title>App</title><script>window.app()</script></head><body><div id='root'></div></body></html>"
INDEX_KEYS = {"url", "final_url", "status", "fetched_on", "html_file", "html_sha256", "text_file", "text_sha256", "text_chars", "title"}


def run(tmp_path: Path, routes: dict, *args: str) -> tuple[int, dict, FakeTransport]:
    fake = FakeTransport(routes)
    code = fs.main([*args, "--out-dir", str(tmp_path / "snap")], transport=fake, sleep=lambda s: None,
                   clock=lambda: "2026-10-22")
    return code, fake, fake


def read_index(tmp_path: Path) -> list[dict]:
    lines = (tmp_path / "snap" / "index.jsonl").read_text(encoding="utf-8").split("\n")
    return [json.loads(line) for line in lines if line.strip()]


def urls_file(tmp_path: Path, urls: list[str]) -> Path:
    path = tmp_path / "urls.txt"
    path.write_text("\n".join(urls) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------- metin cikarma

def test_extract_page_excludes_boilerplate_and_normalizes_space():
    title, text = fs.extract_page(PAGE.decode("utf-8"))
    assert title == "Inschrijven | Gemeente Eindhoven"
    assert "Inschrijven" in text and "Tweede alinea met spaties." in text
    for junk in ("tracking", "color:red", "Menu", "Cookies en privacy", "JS uit"):
        assert junk not in text
    assert "  " not in text and not text.startswith((" ", "\n"))


def test_decode_body_uses_header_then_meta_charset():
    body = "<p>café</p>".encode("cp1252")
    assert "café" in fs.decode_body(body, "text/html; charset=windows-1252")
    meta = b'<meta charset="iso-8859-1"><p>' + "café".encode("latin-1") + b"</p>"
    assert "café" in fs.decode_body(meta, "text/html")
    assert fs.decode_body(b"\xff\xfeok", "text/html; charset=bogus-charset").endswith("ok")


# ---------------------------------------------------------------- calistirma

def test_urls_file_writes_hash_named_snapshots_and_index(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://b.example.org/app"]
    code, fake, _ = run(tmp_path, {urls[0]: ok(PAGE), urls[1]: ok(SHELL)}, "--urls", str(urls_file(tmp_path, urls)))
    summary = json.loads(capsys.readouterr().out.strip())
    rows = read_index(tmp_path)
    assert [r["url"] for r in rows] == urls and all(INDEX_KEYS <= set(r) for r in rows)
    first = rows[0]
    html_path, text_path = tmp_path / "snap" / first["html_file"], tmp_path / "snap" / first["text_file"]
    assert html_path.read_bytes() == PAGE and first["html_sha256"] == hashlib.sha256(PAGE).hexdigest()
    assert html_path.name == first["html_sha256"] + ".html" and text_path.name == first["text_sha256"] + ".txt"
    text = text_path.read_text(encoding="utf-8")
    assert first["text_chars"] == len(text) > 500 and first["text_sha256"] == hashlib.sha256(text.encode("utf-8")).hexdigest()
    assert first["title"] == "Inschrijven | Gemeente Eindhoven" and first["fetched_on"] == "2026-10-22"
    assert "thin_text" not in first["flags"] and "thin_text" in rows[1]["flags"]
    assert summary["thin_text"] == 1 and summary["saved"] == 2 and code == fs.EXIT_FINDINGS
    assert all(c[0] == "GET" and c[4] == wf.MAX_BODY_BYTES for c in fake.calls)


def test_failed_and_redirected_fetches_are_indexed(tmp_path, capsys):
    urls = ["https://a.example.org/old", "https://a.example.org/missing", "https://a.example.org/old"]
    routes = {urls[0]: redirect("https://a.example.org/new"), "https://a.example.org/new": ok(PAGE), urls[1]: status(404)}
    code, _, _ = run(tmp_path, routes, "--urls", str(urls_file(tmp_path, urls)))
    rows = read_index(tmp_path)
    assert len(rows) == 2
    assert rows[0]["final_url"] == "https://a.example.org/new" and rows[0]["status"] == 200
    assert rows[1]["status"] == 404 and rows[1]["html_file"] is None and rows[1]["text_file"] is None
    assert "fetch_failed" in rows[1]["flags"] and code == fs.EXIT_FINDINGS
    assert json.loads(capsys.readouterr().out)["failed"] == 1


def test_clean_run_exits_zero(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    assert code == fs.EXIT_OK and json.loads(capsys.readouterr().out)["status"] == "ok"


def test_second_run_comes_from_cache_with_identical_index(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://b.example.org/app"]
    listing = str(urls_file(tmp_path, urls))
    run(tmp_path, {urls[0]: ok(PAGE), urls[1]: ok(SHELL)}, "--urls", listing)
    first = json.loads(capsys.readouterr().out)
    before = (tmp_path / "snap" / "index.jsonl").read_bytes()
    _, fake, _ = run(tmp_path, {}, "--urls", listing)
    second = json.loads(capsys.readouterr().out)
    assert fake.calls == [] and second["requests_made"] == 0 and second["cache_hits"] == 2
    assert first["requests_made"] == 2 and (tmp_path / "snap" / "index.jsonl").read_bytes() == before


@pytest.mark.parametrize("failure", [status(503), NetworkError("tls", "certificate verify failed"), status(429)])
def test_retry_transient_refetches_cached_transient_failures(tmp_path, capsys, failure):
    url = "https://a.example.org/inschrijven"
    listing = str(urls_file(tmp_path, [url]))
    run(tmp_path, {url: failure}, "--urls", listing)
    assert "fetch_failed" in read_index(tmp_path)[0]["flags"]
    _, cached, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", listing)
    assert cached.calls == [] and "fetch_failed" in read_index(tmp_path)[0]["flags"]  # varsayilan: onbellek, deterministik
    capsys.readouterr()
    code, fresh, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", listing, "--retry-transient")
    row, summary = read_index(tmp_path)[0], json.loads(capsys.readouterr().out)
    assert len(fresh.calls) == 1 and row["status"] == 200 and row["text_file"] and row["flags"] == []
    assert summary["requests_made"] == 1 and summary["retry_transient"] is True and code == fs.EXIT_OK


def test_retry_transient_keeps_cached_success_and_404(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://a.example.org/missing"]
    listing = str(urls_file(tmp_path, urls))
    run(tmp_path, {urls[0]: ok(PAGE), urls[1]: status(404)}, "--urls", listing)
    before = (tmp_path / "snap" / "index.jsonl").read_bytes()
    _, fake, _ = run(tmp_path, {}, "--urls", listing, "--retry-transient")
    assert fake.calls == [] and (tmp_path / "snap" / "index.jsonl").read_bytes() == before


def test_xlsx_mode_reads_kaynaklar_and_baglantilar(tmp_path, capsys):
    xlsx = make_workbook(tmp_path / "w.xlsx", ["https://a.example.org/inschrijven"], [("Bilgi", "https://b.example.org/app")])
    code, fake, _ = run(tmp_path, {"https://a.example.org/inschrijven": ok(PAGE), "https://b.example.org/app": ok(SHELL)},
                        "--xlsx", str(xlsx))
    assert sorted(r["url"] for r in read_index(tmp_path)) == ["https://a.example.org/inschrijven", "https://b.example.org/app"]


def test_max_urls_limits_fetches(tmp_path, capsys):
    urls = [f"https://a.example.org/p{i}" for i in range(4)]
    run(tmp_path, {u: ok(PAGE) for u in urls}, "--urls", str(urls_file(tmp_path, urls)), "--max-urls", "2")
    summary = json.loads(capsys.readouterr().out)
    assert len(read_index(tmp_path)) == 2 and summary["skipped"] == 2


def test_non_html_is_saved_raw_without_text(tmp_path, capsys):
    url = "https://a.example.org/doc.pdf"
    run(tmp_path, {url: ok(b"%PDF-1.4 data", "application/pdf")}, "--urls", str(urls_file(tmp_path, [url])))
    row = read_index(tmp_path)[0]
    assert row["html_file"].endswith(".pdf") and row["text_file"] is None and "non_html" in row["flags"]
    assert row["content_type"] == "application/pdf"


def test_truncated_body_is_flagged(tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(fs, "BODY_LIMIT", 100)
    url = "https://a.example.org/inschrijven"
    run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    assert "truncated" in read_index(tmp_path)[0]["flags"]


def test_load_index_builds_url_to_text_file_mapping(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://a.example.org/missing"]
    run(tmp_path, {urls[0]: ok(PAGE), urls[1]: status(404)}, "--urls", str(urls_file(tmp_path, urls)))
    mapping = fs.load_index(tmp_path / "snap" / "index.jsonl")
    assert set(mapping) == {urls[0]} and mapping[urls[0]].is_file() and mapping[urls[0]].suffix == ".txt"


@pytest.mark.parametrize("args", [[], ["--urls", "yok.txt"], ["--xlsx", "yok.xlsx"]])
def test_usage_errors_exit_2(tmp_path, capsys, args):
    assert fs.main([*args, "--out-dir", str(tmp_path / "snap")], transport=FakeTransport({})) == fs.EXIT_USAGE


def test_max_urls_below_one_is_usage_error(tmp_path, capsys):
    listing = urls_file(tmp_path, ["https://a.example.org/x"])
    assert fs.main(["--urls", str(listing), "--max-urls", "0", "--out-dir", str(tmp_path / "snap")],
                   transport=FakeTransport({})) == fs.EXIT_USAGE


def test_comment_and_blank_lines_in_urls_file_are_ignored(tmp_path, capsys):
    path = tmp_path / "urls.txt"
    path.write_text("# yorum\n\nhttps://a.example.org/inschrijven\n", encoding="utf-8")
    run(tmp_path, {"https://a.example.org/inschrijven": ok(PAGE)}, "--urls", str(path))
    assert [r["url"] for r in read_index(tmp_path)] == ["https://a.example.org/inschrijven"]


# ---------------------------------------------------------------- A1: ayni --out-dir'e ikinci calistirma index'i ezmez

def test_second_run_with_other_urls_keeps_earlier_rows(tmp_path, capsys):
    first, second = "https://a.example.org/inschrijven", "https://b.example.org/app"
    run(tmp_path, {first: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [first])))
    capsys.readouterr()
    run(tmp_path, {second: ok(SHELL)}, "--urls", str(urls_file(tmp_path, [second])))
    summary = json.loads(capsys.readouterr().out)
    assert [r["url"] for r in read_index(tmp_path)] == [first, second]
    assert summary["fetched"] == 1 and summary["index_rows"] == 2 and summary["index_kept"] == 1
    assert not list((tmp_path / "snap").glob("*.tmp"))


def test_rerun_updates_row_in_place_and_keeps_the_rest(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://b.example.org/app", "https://c.example.org/info"]
    run(tmp_path, {urls[0]: status(503), urls[1]: ok(SHELL), urls[2]: ok(PAGE)}, "--urls", str(urls_file(tmp_path, urls)))
    before = read_index(tmp_path)
    capsys.readouterr()
    code, _, _ = run(tmp_path, {urls[0]: ok(PAGE)}, "--urls", str(urls_file(tmp_path, urls[:1])), "--retry-transient")
    after, summary = read_index(tmp_path), json.loads(capsys.readouterr().out)
    assert [r["url"] for r in after] == urls and after[1:] == before[1:]
    assert after[0]["status"] == 200 and after[0]["text_file"] and "fetch_failed" not in after[0]["flags"]
    assert summary["index_kept"] == 2 and code == fs.EXIT_OK  # cikis kodu yalniz bu calismanin satirlarina bakar


def test_merge_index_updates_in_place_appends_new_and_keeps_inputs():
    old = [{"url": "a", "v": 1}, {"url": "b", "v": 1}]
    new = [{"url": "b", "v": 2}, {"url": "c", "v": 2}]
    assert fs.merge_index(old, new) == [{"url": "a", "v": 1}, {"url": "b", "v": 2}, {"url": "c", "v": 2}]
    assert old == [{"url": "a", "v": 1}, {"url": "b", "v": 1}] and new == [{"url": "b", "v": 2}, {"url": "c", "v": 2}]


def test_index_write_failure_is_usage_error_and_keeps_previous_index(tmp_path, capsys, monkeypatch):
    url, new = "https://a.example.org/inschrijven", "https://b.example.org/app"
    run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    before = (tmp_path / "snap" / "index.jsonl").read_bytes()
    capsys.readouterr()
    real_replace = os.replace

    def locked(src, dst):  # yalniz index kilitli: indirme ve onbellek yazimi (web_fetch) normal calisir
        if Path(dst).name == fs.INDEX_NAME:
            raise PermissionError("dosya baska programda acik")
        return real_replace(src, dst)

    monkeypatch.setattr(fs.os, "replace", locked)
    code, fake, _ = run(tmp_path, {new: ok(SHELL)}, "--urls", str(urls_file(tmp_path, [new])))
    assert code == fs.EXIT_USAGE and (tmp_path / "snap" / "index.jsonl").read_bytes() == before
    assert len(fake.calls) == 1 and (tmp_path / "snap" / f"{hashlib.sha256(SHELL).hexdigest()}.html").is_file()
    assert "index yazilamadi" in capsys.readouterr().err and not list((tmp_path / "snap").rglob("*.tmp"))


@pytest.mark.parametrize("bad_line", ["bozuk satir", '{"no_url": 1}', "[1, 2]",
                                      '{"url": "https://old.example.org/y", "text_file": "../../x.txt"}',
                                      '{"url": "https://old.example.org/y", "html_file": "C:\\\\x.html"}',
                                      '{"url": "https://old.example.org/y", "text_file": 5}'])
def test_unreadable_existing_index_is_usage_error_and_left_untouched(tmp_path, capsys, bad_line):
    index = tmp_path / "snap" / "index.jsonl"
    index.parent.mkdir()
    index.write_text('{"url": "https://old.example.org/x"}\n' + bad_line + "\n", encoding="utf-8")
    before = index.read_bytes()
    url = "https://a.example.org/inschrijven"
    code, fake, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    assert code == fs.EXIT_USAGE and fake.calls == [] and index.read_bytes() == before
    assert "index.jsonl:2" in capsys.readouterr().err


# ---------------------------------------------------------------- A2: --must-contain kaniti

def evidence_file(tmp_path: Path, items: list) -> Path:
    """Satir basina JSON nesnesi (str verilirse oldugu gibi yazilir: bozuk satir denemesi)."""
    path = tmp_path / "kanit.jsonl"
    lines = (item if isinstance(item, str) else json.dumps(item, ensure_ascii=False) for item in items)
    path.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
    return path


def test_must_contain_reports_found_and_missing_phrases(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["inwoners  VAN\neindhoven", "vijf dagen", "Rotterdam"],
                                   "why": "ek alanlar serbest"}])
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    row, summary = read_index(tmp_path)[0], json.loads(capsys.readouterr().out)
    assert row["evidence"] == {"needed": 3, "found": 2, "missing": ["Rotterdam"]}
    assert "evidence_missing" in row["flags"] and code == fs.EXIT_FINDINGS
    assert summary["evidence_checked"] == 1 and summary["evidence_missing"] == 1 and summary["status"] == "findings"


def test_must_contain_all_found_keeps_run_clean(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["Tweede alinea met spaties", "VIJF DAGEN"]}])
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    row, summary = read_index(tmp_path)[0], json.loads(capsys.readouterr().out)
    assert row["evidence"] == {"needed": 2, "found": 2, "missing": []} and row["flags"] == []
    assert summary["evidence_missing"] == 0 and summary["must_contain_unmatched"] == 0 and code == fs.EXIT_OK


def test_must_contain_on_failed_fetch_marks_every_phrase_missing(tmp_path, capsys):
    url = "https://a.example.org/missing"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["Stratumsedijk 2"]}])
    run(tmp_path, {url: status(404)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    row = read_index(tmp_path)[0]
    assert row["evidence"] == {"needed": 1, "found": 0, "missing": ["Stratumsedijk 2"]}
    assert row["flags"] == ["fetch_failed", "evidence_missing"]


def test_rows_without_phrases_have_null_evidence_and_empty_list_needs_nothing(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://b.example.org/info"]
    mc = evidence_file(tmp_path, [{"url": urls[1], "must_contain": []}])
    run(tmp_path, {u: ok(PAGE) for u in urls}, "--urls", str(urls_file(tmp_path, urls)), "--must-contain", str(mc))
    rows, summary = read_index(tmp_path), json.loads(capsys.readouterr().out)
    assert rows[0]["evidence"] is None and rows[1]["evidence"] == {"needed": 0, "found": 0, "missing": []}
    assert all("evidence_missing" not in r["flags"] for r in rows) and summary["evidence_checked"] == 1


def test_without_must_contain_evidence_is_null(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    summary = json.loads(capsys.readouterr().out)
    assert read_index(tmp_path)[0]["evidence"] is None
    assert summary["evidence_checked"] == 0 and summary["evidence_missing"] == 0 and summary["soft_404"] == 0


def test_lines_for_same_url_are_merged_and_phrases_deduplicated(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["vijf dagen", "Rotterdam"]},
                                  {"url": f" {url} ", "must_contain": ["VIJF  dagen", "Utrecht"]}])
    run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    assert read_index(tmp_path)[0]["evidence"] == {"needed": 3, "found": 1, "missing": ["Rotterdam", "Utrecht"]}


def test_must_contain_url_outside_the_url_list_is_a_finding(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["vijf dagen"]},
                                  {"url": "https://a.example.org/inschrijven/", "must_contain": ["vijf dagen"]}])
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    summary = json.loads(capsys.readouterr().out)
    assert summary["must_contain_unmatched"] == 1 and summary["status"] == "findings" and code == fs.EXIT_FINDINGS


def test_must_contain_url_skipped_by_max_urls_is_not_unmatched(tmp_path, capsys):
    urls = ["https://a.example.org/p0", "https://a.example.org/p1"]
    mc = evidence_file(tmp_path, [{"url": urls[1], "must_contain": ["vijf dagen"]}])
    run(tmp_path, {u: ok(PAGE) for u in urls}, "--urls", str(urls_file(tmp_path, urls)), "--max-urls", "1",
        "--must-contain", str(mc))
    summary = json.loads(capsys.readouterr().out)
    assert summary["skipped"] == 1 and summary["must_contain_unmatched"] == 0 and summary["evidence_checked"] == 0


@pytest.mark.parametrize("bad_line", [
    "bozuk", '["https://a.example.org/x"]', '{"must_contain": ["x"]}', '{"url": "  ", "must_contain": ["x"]}',
    '{"url": "https://a.example.org/x"}', '{"url": "https://a.example.org/x", "must_contain": "x"}',
    '{"url": "https://a.example.org/x", "must_contain": [1]}', '{"url": "https://a.example.org/x", "must_contain": ["  "]}',
    # eslenmemis vekil: JSON gecerli ama metin UTF-8'e yazilamaz (index yazimi yarida cokerdi)
    '{"url": "https://a.example.org/x", "must_contain": ["x\\ud800y"]}', '{"url": "https://a.example.org/\\udc00", "must_contain": ["x"]}',
])
def test_bad_must_contain_line_is_usage_error_before_any_fetch(tmp_path, capsys, bad_line):
    url = "https://a.example.org/inschrijven"
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["vijf dagen"]}, bad_line])
    code, fake, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    assert code == fs.EXIT_USAGE and fake.calls == [] and not (tmp_path / "snap" / "index.jsonl").exists()
    assert "kanit.jsonl:2" in capsys.readouterr().err


def test_missing_must_contain_file_is_usage_error(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    code, fake, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])),
                        "--must-contain", str(tmp_path / "yok.jsonl"))
    assert code == fs.EXIT_USAGE and fake.calls == [] and "HATA" in capsys.readouterr().err


def test_evidence_matching_ignores_case_space_nfkc_and_typography():
    text = ("Openingstijden:\u00a0ma\u2013vr  09.00\nuur. \ufb01etsenstalling \uff27\uff32\uff21\uff34\uff29\uff33. "
            "Children\u2019s museum. Ge\u00admeente \u0130stanbul")
    phrases = ["openingstijden: ma-vr 09.00 uur", "Fietsenstalling gratis", "children's MUSEUM", "gemeente istanbul",
               "Rotterdam"]
    assert fs.check_evidence(text, phrases) == {"needed": 5, "found": 4, "missing": ["Rotterdam"]}
    assert fs.check_evidence(None, ["x"]) == {"needed": 1, "found": 0, "missing": ["x"]}


# ---------------------------------------------------------------- A2: soft-404 (url_check ile paylasilan kural)

SOFT_404_PAGE = ("<html><head><title>Van Abbemuseum</title></head><body><main><h1>Oops</h1>"
                 f"<p>This page does not seem to exist\u2026</p><p>{LONG_P}</p></main></body></html>").encode("utf-8")


@pytest.mark.parametrize("title, text, hit", [
    # url_check K51 ornekleri: ortak kural ayni sonucu vermeli
    ("Pagina niet gevonden | Gemeente", "", True),
    ("Gemeente", "Helaas, deze pagina bestaat niet meer.", True),
    ("Error 404", "", True),
    ("Page not found", "", True),
    ("Afval", "Bel 040-238 4040 voor info. Pagina 404 van het archief? nee", False),
    ("Inschrijven", "Uitleg over inschrijven.", False),
    # pilot: Van Abbemuseum sergi sayfasi 200 + normal baslik dondu
    ("Van Abbemuseum", "Skip to main content\nThis page does not seem to exist\u2026\nWe apologize", True),
    ("Stadt Dortmund", "Die angeforderte Seite wurde nicht gefunden.", True),
    ("Gemeente", "404\nOeps! Deze pagina is verhuisd.", True),
    ("Stadt", "Fehler 404: diese Adresse ist ungueltig", True),
    ("Sorry", "The page you requested could not be found.", True),
    ("Belastingdienst", "Deze regeling bestaat niet meer sinds 2024.", False),
    ("Gids", "This page does not cover every permit type.", False),
    ("Lang", "x " * 800 + "pagina niet gevonden", False),  # govdenin basi (ilk 1500 karakter) disinda
    (None, None, False),
    # inceleme: bilesik kelimeler (webpagina, homepage, Webseite) url_check'te yakalaniyordu, burada kaciyordu
    ("Gemeente", "Sorry, deze webpagina bestaat niet (meer).", True),
    ("Home", "The homepage does not exist anymore.", True),
    ("Site", "This webpage could not be found.", True),
    ("Stadt", "Diese Webseite existiert nicht mehr.", True),
    # 'sayfa' ile 'yok' arasinda ziyaretciye donen kisa yan cumle ya da 'helaas/leider' olabilir
    ("Site", "The page you are looking for does not exist.", True),
    ("Site", "We're sorry, the page you were trying to reach no longer exists.", True),
    ("Gemeente", "De pagina die u zoekt bestaat helaas niet meer.", True),
    ("Stadt", "Die Seite, die Sie suchen, existiert leider nicht.", True),
    ("Site", "This page unfortunately does not exist.", True),
    # inceleme: kosul ya da baska ozneli yan cumle 'sayfa yok' demek degildir (KVK, IND, business.gov.nl)
    ("KVK", "This page explains what to do if your business no longer exists.", False),
    ("Formulier", "Read page 3 of the form if the address does not exist in the register.", False),
    ("Gids", "This page lists schemes that no longer exist.", False),
    ("Gids", "On this page you will find permits that no longer exist.", False),
    ("Gids", "On this page you can check if your address does not exist in the register.", False),
])
def test_soft_404_signal(title, text, hit):
    assert (fs.soft_404_signal(title, text) is not None) is hit


# url_check K51 listesinin kopyasi: url_check ortak kurala gecip kendi listesini silince parametreler buradan gelir
K51_PHRASES = ("not found", "niet gevonden", "pagina bestaat niet", "page does not exist", "seite nicht gefunden",
               "sayfa bulunamadı", "kon niet worden gevonden")


@pytest.mark.parametrize("phrase", getattr(uc, "SOFT_404_PHRASES", K51_PHRASES))
@pytest.mark.parametrize("where", ["title", "body", "compound"])
def test_shared_rule_catches_every_url_check_phrase(phrase, where):
    """Ust kume: url_check'in K51 ifadesiyle yakaladigi her ornegi fetch_snapshot da yakalar (bilesik kelime dahil)."""
    title, text = {"title": (phrase.title(), ""), "body": ("Gemeente", f"Helaas: {phrase}."),
                   "compound": ("Gemeente", f"Sorry, deze web{phrase} (meer).")}[where]
    assert uc.soft_404_signal(title, text) and fs.soft_404_signal(title, text)


def test_soft_404_page_is_flagged_and_counted(tmp_path, capsys):
    urls = ["https://a.example.org/inschrijven", "https://museum.example.org/expo"]
    code, _, _ = run(tmp_path, {urls[0]: ok(PAGE), urls[1]: ok(SOFT_404_PAGE)}, "--urls", str(urls_file(tmp_path, urls)))
    rows, summary = read_index(tmp_path), json.loads(capsys.readouterr().out)
    assert rows[0]["flags"] == [] and rows[1]["flags"] == ["soft_404"]  # uzun govde: thin_text degil, yalniz soft_404
    assert rows[0]["soft_404"] is None and rows[1]["soft_404"] == "gövde: 'page does not seem to exist'"  # neden
    assert summary["soft_404"] == 1 and summary["status"] == "findings" and code == fs.EXIT_FINDINGS


# ---------------------------------------------------------------- inceleme: JSONL satir bolme ve yazilamayan metin

@pytest.mark.parametrize("char", ["\u2028", "\u2029", "\x85"])
def test_unicode_line_break_in_phrase_keeps_index_readable_across_runs(tmp_path, capsys, char):
    url, phrase = "https://a.example.org/inschrijven", f"Rotterdam{char}centrum"
    mc = evidence_file(tmp_path, [json.dumps({"url": url, "must_contain": [phrase]})])  # kacisli, gecerli tek satir
    args = ("--urls", str(urls_file(tmp_path, [url])), "--must-contain", str(mc))
    codes = [run(tmp_path, {url: ok(PAGE)}, *args)[0] for _ in range(2)]
    raw = (tmp_path / "snap" / "index.jsonl").read_text(encoding="utf-8")
    assert codes == [fs.EXIT_FINDINGS, fs.EXIT_FINDINGS] and "okunamadi" not in capsys.readouterr().err
    assert len(raw.splitlines()) == 1  # splitlines kullanan okuyucular (claim_check) da tek satir gorur
    assert read_index(tmp_path)[0]["evidence"]["missing"] == [phrase]
    assert set(fs.load_index(tmp_path / "snap" / "index.jsonl")) == {url}


@pytest.mark.parametrize("char", ["\u2028", "\u2029", "\x85"])
def test_jsonl_readers_split_only_on_newline(tmp_path, char):
    """Ham U+2028/U+2029/U+0085 tasiyan gecerli JSON satiri (baska bir arac yazmis olabilir) ikiye bolunmez."""
    name = "a" * 64 + ".txt"
    row = {"url": "https://a.example.org/x", "title": f"Kop{char}titel", "text_file": name}
    index, mc = tmp_path / "index.jsonl", tmp_path / "kanit.jsonl"
    index.write_text(json.dumps(row, ensure_ascii=False) + "\r\n", encoding="utf-8")
    mc.write_text(json.dumps({"url": row["url"], "must_contain": [f"a{char}b"]}, ensure_ascii=False) + "\n",
                  encoding="utf-8")
    assert fs.read_index_rows(index) == [row] and fs.load_index(index) == {row["url"]: tmp_path / name}
    assert fs.read_must_contain(mc) == {row["url"]: [f"a{char}b"]}


def test_preserved_row_with_lone_surrogate_is_written_back_intact(tmp_path, capsys):
    index = tmp_path / "snap" / "index.jsonl"
    index.parent.mkdir()
    index.write_text('{"url": "https://old.example.org/x", "title": "x\\ud800y"}\n', encoding="utf-8")
    url = "https://a.example.org/inschrijven"
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    rows = fs.read_index_rows(index)
    assert code == fs.EXIT_OK and rows[0] == {"url": "https://old.example.org/x", "title": "x\ud800y"}
    assert [r["url"] for r in rows] == ["https://old.example.org/x", url] and not list(index.parent.rglob("*.tmp"))


# ---------------------------------------------------------------- inceleme: A1 + A2 birlikte (kanit index'te kalir)

def test_must_contain_for_url_only_in_earlier_index_is_checked_from_saved_text(tmp_path, capsys):
    old, failed, new = "https://a.example.org/inschrijven", "https://a.example.org/missing", "https://b.example.org/info"
    run(tmp_path, {old: ok(PAGE), failed: status(404)}, "--urls", str(urls_file(tmp_path, [old, failed])))
    capsys.readouterr()
    mc = evidence_file(tmp_path, [{"url": old, "must_contain": ["vijf dagen", "Rotterdam"]},
                                  {"url": failed, "must_contain": ["Stratumsedijk"]},
                                  {"url": new, "must_contain": ["vijf dagen"]},
                                  {"url": f"{old}/", "must_contain": ["vijf dagen"]}])  # yazim farki: gercek bulgu
    code, fake, _ = run(tmp_path, {new: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [new])), "--must-contain", str(mc))
    rows, summary = {r["url"]: r for r in read_index(tmp_path)}, json.loads(capsys.readouterr().out)
    assert rows[old]["evidence"] == {"needed": 2, "found": 1, "missing": ["Rotterdam"]}
    assert rows[old]["flags"] == ["evidence_missing"] and rows[failed]["flags"] == ["fetch_failed", "evidence_missing"]
    assert rows[failed]["evidence"] == {"needed": 1, "found": 0, "missing": ["Stratumsedijk"]}
    assert rows[new]["evidence"]["missing"] == [] and [c[1] for c in fake.calls] == [new]  # eskiler yeniden inmez
    assert summary["evidence_from_index"] == 2 and summary["must_contain_unmatched"] == 1 and summary["failed"] == 0
    assert summary["evidence_checked"] == 3 and summary["evidence_missing"] == 2 and code == fs.EXIT_FINDINGS


def test_saved_text_that_does_not_match_its_hash_is_not_used_as_evidence(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    (tmp_path / "snap" / read_index(tmp_path)[0]["text_file"]).write_text("Rotterdam", encoding="utf-8")  # elle degisti
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["Rotterdam"]}])
    run(tmp_path, {}, "--urls", str(urls_file(tmp_path, ["https://b.example.org/x"])), "--must-contain", str(mc))
    assert read_index(tmp_path)[0]["evidence"] == {"needed": 1, "found": 0, "missing": ["Rotterdam"]}


def test_rerun_without_must_contain_keeps_evidence_of_unchanged_text(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    listing = str(urls_file(tmp_path, [url]))
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["vijf dagen", "Rotterdam"]}])
    run(tmp_path, {url: ok(PAGE)}, "--urls", listing, "--must-contain", str(mc))
    first = read_index(tmp_path)[0]
    capsys.readouterr()
    code, _, _ = run(tmp_path, {}, "--urls", listing)  # onbellekten: ayni metin, bu kez ifade verilmedi
    row, summary = read_index(tmp_path)[0], json.loads(capsys.readouterr().out)
    assert row == first and row["flags"] == ["evidence_missing"]
    assert summary["evidence_missing"] == 1 and code == fs.EXIT_FINDINGS  # onceki bulgu sessizce kaybolmaz


def test_rerun_without_must_contain_marks_evidence_of_changed_text_stale(tmp_path, capsys):
    url = "https://a.example.org/inschrijven"
    listing = str(urls_file(tmp_path, [url]))
    mc = evidence_file(tmp_path, [{"url": url, "must_contain": ["vijf dagen"]}])
    run(tmp_path, {url: status(503)}, "--urls", listing, "--must-contain", str(mc))
    capsys.readouterr()
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", listing, "--retry-transient")  # metin degisti, ifade yok
    row, summary = read_index(tmp_path)[0], json.loads(capsys.readouterr().out)
    assert row["evidence"] == {"needed": 1, "found": 0, "missing": ["vijf dagen"]} and row["flags"] == ["evidence_stale"]
    assert summary["evidence_stale"] == 1 and summary["evidence_checked"] == 0 and code == fs.EXIT_FINDINGS


# ---------------------------------------------------------------- inceleme: es zamanli calisma ve dosya adlari

def run_with_side_effect(tmp_path: Path, url: str, body: bytes, effect) -> int:
    """Indirme surerken effect() calisir (ayni --out-dir'e baska bir calismanin yazmasi gibi)."""
    fake = FakeTransport({url: ok(body)})

    def transport(*args):
        effect()
        return fake(*args)

    return fs.main(["--urls", str(urls_file(tmp_path, [url])), "--out-dir", str(tmp_path / "snap")],
                   transport=transport, sleep=lambda s: None, clock=lambda: "2026-10-22")


def append_line(path: Path, line: str):
    def effect():
        with path.open("a", encoding="utf-8") as stream:
            stream.write(line + "\n")
    return effect


def test_rows_written_by_a_concurrent_run_are_kept(tmp_path, capsys):
    first, other, second = "https://a.example.org/inschrijven", "https://c.example.org/x", "https://b.example.org/app"
    run(tmp_path, {first: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [first])))
    index = tmp_path / "snap" / "index.jsonl"
    run_with_side_effect(tmp_path, second, SHELL, append_line(index, json.dumps({"url": other, "flags": []})))
    assert [r["url"] for r in read_index(tmp_path)] == [first, other, second]


def test_index_broken_during_the_run_is_usage_error_and_left_untouched(tmp_path, capsys):
    first = "https://a.example.org/inschrijven"
    run(tmp_path, {first: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [first])))
    index = tmp_path / "snap" / "index.jsonl"
    capsys.readouterr()
    code = run_with_side_effect(tmp_path, "https://b.example.org/app", SHELL, append_line(index, "bozuk satir"))
    assert code == fs.EXIT_USAGE and index.read_text(encoding="utf-8").split("\n")[-2] == "bozuk satir"
    assert "index.jsonl:2" in capsys.readouterr().err and not list(index.parent.glob("*.tmp"))


def test_temporary_file_name_is_private_to_the_run(tmp_path, capsys):
    foreign = tmp_path / "snap" / "index.jsonl.tmp"
    foreign.parent.mkdir()
    foreign.write_text("baska bir calismanin yarim yazimi", encoding="utf-8")
    url = "https://a.example.org/inschrijven"
    code, _, _ = run(tmp_path, {url: ok(PAGE)}, "--urls", str(urls_file(tmp_path, [url])))
    assert code == fs.EXIT_OK and foreign.read_text(encoding="utf-8") == "baska bir calismanin yarim yazimi"
    assert [r["url"] for r in read_index(tmp_path)] == [url]


@pytest.mark.parametrize("name", ["../secret.txt", "..\\secret.txt", "C:/secret.txt", "sub/" + "a" * 64 + ".txt"])
def test_load_index_refuses_names_outside_the_snapshot_folder(tmp_path, name):
    (tmp_path / "secret.txt").write_text("gizli", encoding="utf-8")
    index = tmp_path / "snap" / "index.jsonl"
    index.parent.mkdir()
    index.write_text(json.dumps({"url": "https://a.example.org/x", "text_file": name}) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="index.jsonl:1"):
        fs.load_index(index)


def test_load_index_of_missing_file_is_an_error(tmp_path):
    with pytest.raises(OSError):
        fs.load_index(tmp_path / "yok" / "index.jsonl")
