"""wikidata_places: Wikidata SPARQL mekan aday havuzu (A6; pilot wikidata_aday.py). Ag yok, sahte tasima."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

import wikidata_places as wp

ROW_KEYS = ["qid", "name", "name_en", "lat", "lon", "types", "district", "website", "has_image", "commons_category",
            "nlwiki"]
NL = ("--lang", "nl")


def lit(value: str) -> dict:
    return {"type": "literal", "value": value}


def binding(qid: str, coord: str | None, **values: str) -> dict:
    row = {"item": {"type": "uri", "value": f"http://www.wikidata.org/entity/{qid}"}}
    if coord is not None:
        row["coord"] = lit(coord)
    return {**row, **{k: lit(v) for k, v in values.items()}}


def result(bindings: list[dict], lang: str = "nl") -> dict:
    return {"head": {"vars": ["item", lang, "en", "coord", "site", "image", "cat", f"{lang}wiki", "types", "district"]},
            "results": {"bindings": bindings}}


BINDINGS = [
    binding("Q1", "Point(5.48194 51.43472)", nl="Van Abbemuseum", en="Van Abbemuseum", site="https://vanabbemuseum.nl/",
            image="http://commons.wikimedia.org/wiki/Special:FilePath/V.jpg", cat="Van Abbemuseum",
            nlwiki="https://nl.wikipedia.org/wiki/Van_Abbemuseum", types="art museum|museum", district="Eindhoven"),
    binding("Q2", "Point(5.4675 51.4417)", en="Philips Stadion", types="stadium"),
    binding("Q3", "Point(5.4 51.4)", nl="aardappelmarkt"),
]


def ok(data: dict) -> tuple:
    return 200, {"Content-Type": "application/sparql-results+json"}, json.dumps(data).encode("utf-8")


class FakeTransport:
    """Sahte tasima: yanitlar sirayla tuketilir (son eleman tekrar eder); hata nesnesi firlatilir."""

    def __init__(self, responses: list) -> None:
        self.responses, self.calls = list(responses), []

    def __call__(self, url, headers, timeout):
        self.calls.append((url, dict(headers), timeout))
        item = self.responses.pop(0) if len(self.responses) > 1 else self.responses[0]
        if isinstance(item, Exception):
            raise item
        return item


def offline() -> FakeTransport:
    return FakeTransport([wp.TransportError("ag yok")])


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def query_of(fake: FakeTransport, index: int = 0) -> str:
    return parse_qs(urlsplit(fake.calls[index][0]).query)["query"][0]


def run(capsys, fake: FakeTransport, *args):
    sleeps: list[float] = []
    code = wp.main([str(a) for a in args], transport=fake, sleep=sleeps.append)
    lines = capsys.readouterr().out.strip().splitlines()
    return code, (json.loads(lines[-1]) if lines else None), sleeps


# ---------------------------------------------------------------- mutlu yol

def test_query_rows_are_sorted_by_name_and_raw_is_cached(tmp_path, capsys):
    out = tmp_path / "mekan" / "wikidata_aday.jsonl"
    fake = FakeTransport([ok(result(BINDINGS))])
    code, summary, _ = run(capsys, fake, "--qid", "Q9832", *NL, "--out", out)
    rows = read_jsonl(out)
    assert code == wp.EXIT_OK and summary["status"] == "ok" and summary["items"] == 3
    assert [r["name"] for r in rows] == ["aardappelmarkt", "Philips Stadion", "Van Abbemuseum"]  # nl yoksa en
    assert all(list(r) == ROW_KEYS for r in rows)  # pilotla ayni alan sirasi
    assert rows[2] == {"qid": "Q1", "name": "Van Abbemuseum", "name_en": "Van Abbemuseum", "lat": 51.43472,
                       "lon": 5.48194, "types": "art museum|museum", "district": "Eindhoven",
                       "website": "https://vanabbemuseum.nl/", "has_image": True, "commons_category": "Van Abbemuseum",
                       "nlwiki": "https://nl.wikipedia.org/wiki/Van_Abbemuseum"}
    assert (summary["with_site"], summary["with_image"], summary["with_category"]) == (1, 1, 1)
    assert summary["from_cache"] is False and summary["requests_made"] == 1
    link, headers, _ = fake.calls[0]
    assert link.startswith(wp.ENDPOINT) and "CorteqsCityToolkit" in headers["User-Agent"]
    assert "sparql-results+json" in headers["Accept"]
    query = query_of(fake)
    assert "wd:Q9832" in query and 'LANG(?nl)="nl"' in query and "<https://nl.wikipedia.org/>" in query
    assert (tmp_path / "mekan" / "wikidata_aday.raw.json").is_file()
    meta = json.loads((tmp_path / "mekan" / "wikidata_aday.raw.meta.json").read_text(encoding="utf-8"))
    assert (meta["qid"], meta["lang"], len(meta["query_sha256"])) == ("Q9832", "nl", 64)  # onbellek sorguya bagli


def test_second_run_reads_raw_cache_without_network(tmp_path, capsys):
    out = tmp_path / "w.jsonl"
    run(capsys, FakeTransport([ok(result(BINDINGS))]), "--qid", "Q9832", *NL, "--out", out)
    first = out.read_bytes()
    fake = offline()
    code, summary, _ = run(capsys, fake, "--qid", "Q9832", *NL, "--out", out)
    assert code == wp.EXIT_OK and fake.calls == [] and summary["from_cache"] is True
    assert summary["requests_made"] == 0 and out.read_bytes() == first


def test_qid_and_lang_are_parameters(tmp_path, capsys):
    rows = [binding("Q7", "Point(7.465 51.514)", de="Dortmunder U", en="Dortmund U-Tower",
                    dewiki="https://de.wikipedia.org/wiki/Dortmunder_U")]
    fake = FakeTransport([ok(result(rows, "de"))])
    out = tmp_path / "w.jsonl"
    code, _, _ = run(capsys, fake, "--qid", "Q1295", "--lang", "de", "--out", out)
    query = query_of(fake)
    assert code == wp.EXIT_OK and "wd:Q1295" in query and 'LANG(?de)="de"' in query
    assert "<https://de.wikipedia.org/>" in query and "Q9832" not in query and '"nl"' not in query
    row = read_jsonl(out)[0]
    assert row["name"] == "Dortmunder U" and row["dewiki"].endswith("Dortmunder_U") and "nlwiki" not in row


def test_rate_limit_retry_after_is_honoured(tmp_path, capsys):
    fake = FakeTransport([(429, {"Retry-After": "7"}, b""), ok(result(BINDINGS))])
    code, summary, sleeps = run(capsys, fake, "--qid", "Q9832", *NL, "--out", tmp_path / "w.jsonl")
    assert code == wp.EXIT_OK and sleeps == [7.0] and summary["requests_made"] == 2


# ---------------------------------------------------------------- kirma testleri

@pytest.mark.parametrize("response", [(500, {}, b"err"), (429, {"Retry-After": "600"}, b""),
                                      (200, {}, b"<html>json degil</html>"), (200, {}, b'{"head": {}}'),
                                      (200, {}, b'{"results": []}'), wp.TransportError("baglanti yok")])
def test_failed_query_writes_nothing_and_exits_1(tmp_path, capsys, response):
    out = tmp_path / "w.jsonl"
    code, summary, sleeps = run(capsys, FakeTransport([response]), "--qid", "Q9832", *NL, "--out", out)
    assert code == wp.EXIT_FINDINGS and summary["status"] == "fetch_failed" and summary["error"]
    assert not out.exists() and not out.with_suffix(".raw.json").exists()
    assert not (tmp_path / "w.raw.meta.json").exists()
    assert all(s <= wp.RETRY_CAP_SECONDS for s in sleeps)


def test_unreadable_coordinates_are_skipped_and_counted(tmp_path, capsys):
    rows = BINDINGS + [binding("Q8", "<http://www.wikidata.org/entity/Q405> Point(1 2)", nl="Maankrater"),
                       binding("Q9", None, nl="Zonder coordinaat")]
    code, summary, _ = run(capsys, FakeTransport([ok(result(rows))]), "--qid", "Q9832", *NL, "--out",
                           tmp_path / "w.jsonl")
    assert code == wp.EXIT_OK and (summary["items"], summary["bad_rows"]) == (3, 2)


def test_empty_result_is_a_finding(tmp_path, capsys):
    code, summary, _ = run(capsys, FakeTransport([ok(result([]))]), "--qid", "Q9832", *NL, "--out", tmp_path / "w.jsonl")
    assert code == wp.EXIT_FINDINGS and summary["status"] == "empty"


def test_raw_cache_of_other_language_needs_refresh(tmp_path, capsys):
    out = tmp_path / "w.jsonl"
    run(capsys, FakeTransport([ok(result(BINDINGS))]), "--qid", "Q9832", *NL, "--out", out)
    fake = offline()
    code, summary, _ = run(capsys, fake, "--qid", "Q9832", "--lang", "de", "--out", out)
    assert code == wp.EXIT_FINDINGS and summary["status"] == "cache_mismatch" and fake.calls == []
    fresh = FakeTransport([ok(result([binding("Q7", "Point(7.4 51.5)", de="U")], "de"))])
    code, _, _ = run(capsys, fresh, "--qid", "Q9832", "--lang", "de", "--out", out, "--refresh")
    assert code == wp.EXIT_OK and len(fresh.calls) == 1 and read_jsonl(out)[0]["name"] == "U"


def test_raw_cache_of_other_city_is_not_returned_under_the_new_qid(tmp_path, capsys):
    """Ayni --out ile baska --qid: eski sehrin sonucu 'ok' ile yeni qid adina donuyordu (Q9803 istendi, Q9832 geldi)."""
    out = tmp_path / "w.jsonl"
    run(capsys, FakeTransport([ok(result(BINDINGS))]), "--qid", "Q9832", *NL, "--out", out)
    first = out.read_bytes()
    fake = offline()
    code, summary, _ = run(capsys, fake, "--qid", "Q9803", *NL, "--out", out)
    assert code == wp.EXIT_FINDINGS and summary["status"] == "cache_mismatch" and fake.calls == []
    assert summary["qid"] == "Q9803" and summary["cached"]["qid"] == "Q9832" and out.read_bytes() == first
    fresh = FakeTransport([ok(result([binding("Q5", "Point(5.1 51.5)", nl="Tilburg station")]))])
    code, summary, _ = run(capsys, fresh, "--qid", "Q9803", *NL, "--out", out, "--refresh")
    assert code == wp.EXIT_OK and "wd:Q9803" in query_of(fresh) and read_jsonl(out)[0]["qid"] == "Q5"
    code, summary, _ = run(capsys, offline(), "--qid", "Q9803", *NL, "--out", out)
    assert code == wp.EXIT_OK and summary["from_cache"] is True


@pytest.mark.parametrize("meta", [None, "{bozuk", json.dumps({"qid": "Q9832", "lang": "nl"})])
def test_raw_cache_without_matching_query_record_is_not_trusted(tmp_path, capsys, meta):
    """Sorgusu bilinmeyen ham dosya (eski surum/pilot, bozuk ya da eksik kayit) dogrulanamaz: --refresh istenir."""
    out = tmp_path / "w.jsonl"
    (tmp_path / "w.raw.json").write_text(json.dumps(result(BINDINGS)), encoding="utf-8")
    if meta is not None:
        (tmp_path / "w.raw.meta.json").write_text(meta, encoding="utf-8")
    fake = offline()
    code, summary, _ = run(capsys, fake, "--qid", "Q9832", *NL, "--out", out)
    assert code == wp.EXIT_FINDINGS and summary["status"] == "cache_mismatch" and fake.calls == []
    assert not out.exists()


def test_corrupt_raw_cache_is_a_finding(tmp_path, capsys):
    (tmp_path / "w.raw.json").write_bytes(b"\xff\xfe bozuk")
    code, summary, _ = run(capsys, offline(), "--qid", "Q9832", *NL, "--out", tmp_path / "w.jsonl")
    assert code == wp.EXIT_FINDINGS and summary["status"] == "cache_corrupt"


@pytest.mark.parametrize("args", [["--qid", "9832", *NL], ["--qid", "Q0", *NL], ["--qid", "Q9832", "--lang", "NL"],
                                  ["--qid", "Q9832", "--lang", "n1"], ["--qid", "Q9832", *NL, "--raw", "SAME"],
                                  ["--qid", "Q9832"], ["--qid", "Q9832", *NL, "--raw", "META_OF_OUT"]])
def test_usage_errors_exit_2(tmp_path, capsys, args):
    fake = FakeTransport([ok(result(BINDINGS))])
    out = tmp_path / "w.meta.json" if "META_OF_OUT" in args else tmp_path / "w.jsonl"
    swap = {"SAME": str(out), "META_OF_OUT": str(tmp_path / "w.json")}  # --raw w.json -> kayit w.meta.json = --out
    argv = [swap.get(a, a) for a in args] + ["--out", str(out)]
    assert wp.main(argv, transport=fake, sleep=lambda s: None) == wp.EXIT_USAGE and fake.calls == []


def test_out_is_required_and_help_exits_0(capsys):
    fake = FakeTransport([ok(result(BINDINGS))])
    assert wp.main(["--qid", "Q9832", *NL], transport=fake) == wp.EXIT_USAGE and fake.calls == []
    assert wp.main(["--help"], transport=fake) == wp.EXIT_OK


def test_unwritable_outputs_exit_2_not_1(tmp_path, capsys):
    """Beklenmeyen yazma hatasi main disina kacarsa Python cikisi 1 olur ve 'bulgu' ile karisir."""
    folder = tmp_path / "klasor"
    folder.mkdir()
    code = wp.main(["--qid", "Q9832", *NL, "--out", str(folder)], transport=FakeTransport([ok(result(BINDINGS))]),
                   sleep=lambda s: None)
    assert code == wp.EXIT_USAGE and "HATA" in capsys.readouterr().err
    code = wp.main(["--qid", "Q9832", *NL, "--out", str(tmp_path / "w.jsonl"), "--raw", str(folder), "--refresh"],
                   transport=FakeTransport([ok(result(BINDINGS))]), sleep=lambda s: None)
    assert code == wp.EXIT_USAGE and "HATA" in capsys.readouterr().err
