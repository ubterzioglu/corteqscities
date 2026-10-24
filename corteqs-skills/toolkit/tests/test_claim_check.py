"""claim_check: iddia degerlerinin kartin kaynak snapshot metninde gecip gecmedigi (tutarlilik, dogruluk degil)."""
from __future__ import annotations

import copy
import json

import pytest

import claim_check as cc

FILLER = "Algemene informatie over de dienstverlening en de voorwaarden. " * 12


def _money(v):
    return {"kind": "money", "value": v, "currency": "EUR"}


def _dur(v, unit):
    return {"kind": "duration", "value": v, "unit": unit}


def _claim(cid: str, values: list[dict], urls: list, kind: str | None = None) -> dict:
    return {"claim_id": cid, "entry_id": cid.split(":#")[0], "sheet": "Yanıtlar", "_row": 8, "field": "cost",
            "kind": kind or values[0]["kind"], "text": "x", "sentence": "Örnek cümle.", "values": values,
            "source_ids": [f"s{i}" for i in range(len(urls))],
            "sources": [{"source_id": f"s{i}", "url": u} for i, u in enumerate(urls)],
            "missing_source_ids": [f"s{i}" for i, u in enumerate(urls) if u is None]}


# --- metin normallestirme -------------------------------------------------------------------

def test_fix_mojibake_repairs_only_broken_runs():
    assert cc.fix_mojibake("Alles in Ã©Ã©n overzicht € 5") == "Alles in één overzicht € 5"
    assert cc.fix_mojibake("één café") == "één café"
    assert cc.fix_mojibake("SÃO PAULO") == "SÃO PAULO"


def test_normalize_text_unifies_spaces_dashes_and_soft_hyphens():
    raw = "Kosten: € 85,15\n\n1–2 weken  Abonnementen­wijzer"
    assert cc.normalize_text(raw) == "Kosten: € 85,15 1-2 weken Abonnementenwijzer"


def test_url_key_ignores_scheme_www_trailing_slash_and_fragment():
    assert cc.url_key("https://www.KVK.nl/inschrijven/#x") == cc.url_key("http://kvk.nl/inschrijven")
    assert cc.url_key("https://a.nl/p?x=1") != cc.url_key("https://a.nl/p")


# --- deger eslestirme ----------------------------------------------------------------------------

@pytest.mark.parametrize("value,text,level", [
    (_money(85.15), "Inschrijven kost € 85,15 eenmalig.", "unit"),
    (_money(85.15), "Price 85.15 euro.", "unit"),
    (_money(85.15), "Kosten € 85 per jaar.", None),
    (_money(85.15), "Kosten € 185,15 per jaar.", None),
    (_money(80), "Boete € 80,- per keer.", "unit"),
    (_money(80), "Boete €80 per keer.", "unit"),
    (_money(80), "Boete 80 euro.", "unit"),
    (_money(80), "Boete € 80,00.", "unit"),
    (_money(80), "Boete € 800.", None),
    (_money(80), "Boete € 80,50.", None),
    (_money(80), "Ongeveer 80 procent.", "number"),
    (_money(2500), "Maximaal € 2.500 per jaar.", "unit"),
    (_money(2500), "Up to EUR 2,500.", "unit"),
    ({"kind": "percent", "value": 4.4}, "Maximaal 4,4% verhoging.", "unit"),
    ({"kind": "percent", "value": 4.4}, "Maximaal 4,4 procent.", "unit"),
    ({"kind": "percent", "value": 4.4}, "Maximaal 4,45% verhoging.", None),
    ({"kind": "percent", "value": 10.4}, "Tarief 10,4%.", "unit"),
    ({"kind": "percent", "value": 2}, "Oran %2 uygulanır.", "unit"),
    ({"kind": "percent", "value": 2}, "Tarief 1 35,75% 2 Meer dan € 38.883", "number"),
    ({"kind": "percent", "value": 2}, "Tarief 35,75 % 2 Meer dan", "number"),
    (_dur(26, "week"), "Minimaal 26 weken gewerkt.", "unit"),
    (_dur(26, "week"), "At least 26 weeks.", "unit"),
    (_dur(26, "week"), "26 van de 36 weken gewerkt.", "number"),
    (_dur(1, "week"), "Reactie binnen 1 tot 2 weken.", "unit"),
    (_dur(2, "week"), "Reactie binnen 1 tot 2 weken.", "unit"),
    (_dur(5, "year"), "In de laatste 5 jaar.", "unit"),
    (_dur(14, "day"), "Binnen 14 dagen.", "unit"),
    (_dur(14, "day"), "Binnen 14 werkdagen.", "unit"),
    (_dur(2, "month"), "Na 2 maanden.", "unit"),
    (_dur(5, "day"), "Op 5 december.", "number"),
    ({"kind": "age", "value": 16}, "Tot je 16 jaar bent.", "unit"),
    ({"kind": "age", "value": 18}, "Voor 18+ huurders.", "unit"),
    ({"kind": "age", "value": 18}, "Alle 18-jarigen.", "unit"),
    ({"kind": "weekday", "value": "thursday"}, "Koopavond op donderdagavond.", "unit"),
    ({"kind": "weekday", "value": "thursday"}, "Late shopping on Thursday.", "unit"),
    ({"kind": "weekday", "value": "saturday"}, "Elke zondag open.", None),
    ({"kind": "weekday", "value": "sunday", "ordinal": 3}, "Elke derde zondag van de maand.", "unit"),
    ({"kind": "weekday", "value": "sunday", "ordinal": 3}, "Op de 3e zondag.", "unit"),
    ({"kind": "weekday", "value": "sunday", "ordinal": 3}, "Elke zondag open.", "number"),
    ({"kind": "time", "value": "18:00"}, "Open tot 18.00 uur.", "unit"),
    ({"kind": "time", "value": "18:00"}, "Open until 18:00.", "unit"),
    ({"kind": "time", "value": "18:00"}, "Open tot 18 uur.", "unit"),
    ({"kind": "time", "value": "09:30"}, "Vanaf 9.30 uur.", "unit"),
    ({"kind": "time", "value": "18:00"}, "Open tot 17.00 uur.", None),
    ({"kind": "phone", "value": "0402386000"}, "Bel +31 (0)40 238 6000.", "unit"),
    ({"kind": "phone", "value": "0402386000"}, "Bel 040 - 238 60 00.", "unit"),
    ({"kind": "phone", "value": "0402386000"}, "Bel 040-2386000.", "unit"),
    ({"kind": "phone", "value": "0402386000"}, "Bel 040-2386001.", None),
    ({"kind": "phone", "value": "14040"}, "Bel ons op 14 040.", "unit"),
    ({"kind": "date", "day": 31, "month": 12}, "Aanvragen tot en met 31 december.", "unit"),
    ({"kind": "date", "day": 31, "month": 12}, "Apply by December 31.", "unit"),
    ({"kind": "date", "day": 31, "month": 12}, "Uiterlijk 31-12-2025.", "unit"),
    ({"kind": "date", "day": 31, "month": 12}, "Uiterlijk 31 januari.", None),
    ({"kind": "date", "day": 1, "month": 7}, "Per 1 juli verhoging.", "unit"),
])
def test_match_value_levels(value, text, level):
    found, snippet = cc.match_value(value, cc.normalize_text(text))
    assert found == level
    assert (snippet is not None) == (level is not None)


def test_match_value_unknown_kind_returns_none():
    assert cc.match_value({"kind": "mystery", "value": 1}, "1 2 3") == (None, None)


def test_snippet_contains_the_match():
    _, snippet = cc.match_value(_money(85.15), cc.normalize_text(FILLER + " Inschrijven kost € 85,15. " + FILLER))
    assert "85,15" in snippet and len(snippet) < 250


# --- snapshot yukleme ------------------------------------------------------------------------------

def _write_pair(root, stem, meta, body=None):
    (root / f"{stem}.json").write_text(json.dumps({"id": stem, **meta}), encoding="utf-8")
    if body is not None:
        header = f"URL: {meta.get('url')}\nFETCHED: 2026-10-20T21:00:00+0200\nTITLE: {stem}\n\n"
        (root / f"{stem}.txt").write_text(header + body, encoding="utf-8")


@pytest.fixture()
def qwen_cache(tmp_path):
    root = tmp_path / "cache"
    root.mkdir()
    _write_pair(root, "kvk", {"url": "https://www.kvk.nl/inschrijven", "final_url": "https://www.kvk.nl/inschrijven/", "status": 200,
                              "fetched_at": "2026-10-20T21:00:00+0200"}, FILLER + " Inschrijven kost € 85,15 eenmalig. " + FILLER)
    _write_pair(root, "uwv", {"url": "https://uwv.nl/ww", "final_url": "https://www.uwv.nl/nl/ww", "status": 200},
                FILLER + " U heeft in de laatste 36 weken minimaal 26 weken gewerkt. Kies optie 5 in het menu. " + FILLER)
    _write_pair(root, "thin", {"url": "https://www.eindhoven.nl/onderwijs", "final_url": "https://www.eindhoven.nl/onderwijs", "status": 200},
                "Onderwijs vanaf 5 jaar")
    _write_pair(root, "gone", {"url": "https://www.acm.nl/oud", "final_url": "https://www.acm.nl/oud", "status": 404},
                "Pagina niet gevonden € 80 " + FILLER)
    _write_pair(root, "err", {"url": "https://www.cbr.nl/", "status": None, "error": "timeout"})
    _write_pair(root, "home", {"url": "https://www.example.nl/", "final_url": "https://www.example.nl/", "status": 200},
                FILLER + " Elke zaterdag markt. Kosten € 80. " + FILLER)
    _write_pair(root, "nolink", {"url": "https://www.nolink.nl/page", "status": 200})
    (root / "blob.bin").write_bytes(b"\x00\x01")
    return root


def test_load_qwen_cache_states_and_header_stripping(qwen_cache):
    index = cc.load_snapshots(qwen_cache, "qwen-cache", min_chars=500)
    kvk = cc.find_snapshot(index, "https://kvk.nl/inschrijven")
    assert kvk.snapshot_id == "kvk" and kvk.state == "ok" and not kvk.text.startswith("URL:")
    assert kvk.fetched_at == "2026-10-20T21:00:00+0200"
    assert cc.find_snapshot(index, "https://www.uwv.nl/nl/ww/").snapshot_id == "uwv"
    assert cc.find_snapshot(index, "https://www.eindhoven.nl/onderwijs").state == "thin"
    assert cc.find_snapshot(index, "https://www.acm.nl/oud").state == "http_error"
    assert cc.find_snapshot(index, "https://www.cbr.nl/").state == "fetch_error"
    assert cc.find_snapshot(index, "https://www.nolink.nl/page").state == "no_text"
    assert cc.find_snapshot(index, "https://nergens.nl/") is None
    assert cc.find_snapshot(index, None) is None


def test_load_toolkit_snapshots(tmp_path):
    root = tmp_path / "snap"
    (root / "texts").mkdir(parents=True)
    (root / "texts" / "a.txt").write_text(FILLER + " Kosten € 85,15.", encoding="utf-8")
    lines = [{"url": "https://www.kvk.nl/a", "final_url": "https://www.kvk.nl/a/", "text_file": "texts/a.txt", "text_chars": 900, "status": 200},
             {"url": "https://www.kvk.nl/b", "text_file": "texts/missing.txt", "text_chars": 0},
             {"url": "https://www.kvk.nl/c", "text_file": "../outside.txt"},
             {"url": "https://www.kvk.nl/d", "http_status": 503}]
    (root / "index.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n\n", encoding="utf-8")
    index = cc.load_snapshots(root, "toolkit", min_chars=500)
    assert cc.find_snapshot(index, "https://kvk.nl/a").state == "ok"
    assert cc.find_snapshot(index, "https://kvk.nl/b").state == "no_text"
    assert cc.find_snapshot(index, "https://kvk.nl/c").state == "no_text"
    assert cc.find_snapshot(index, "https://kvk.nl/d").state == "http_error"


def test_toolkit_index_written_by_fetch_snapshot_keeps_fetched_on(tmp_path):
    root = tmp_path / "snap"
    root.mkdir()
    (root / "abc.txt").write_text(FILLER + " Kosten € 85,15.", encoding="utf-8")
    row = {"url": "https://www.kvk.nl/a", "final_url": "https://www.kvk.nl/a", "status": 200, "fetched_on": "2026-10-22",
           "text_file": "abc.txt", "text_chars": 900, "flags": [], "error": None}
    (root / "index.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
    snap = cc.find_snapshot(cc.load_snapshots(root), "https://kvk.nl/a")
    assert snap.state == "ok" and snap.fetched_at == "2026-10-22"


def test_detect_format(tmp_path, qwen_cache):
    assert cc.detect_format(qwen_cache) == "qwen-cache"
    root = tmp_path / "snap"
    root.mkdir()
    (root / "index.jsonl").write_text("", encoding="utf-8")
    assert cc.detect_format(root) == "toolkit"


# --- siniflandirma ----------------------------------------------------------------------------

@pytest.fixture()
def index(qwen_cache):
    return cc.load_snapshots(qwen_cache, "qwen-cache", min_chars=500)


def test_supported_when_value_in_source(index):
    res = cc.check_claim(_claim("e:kvk:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"]), index)
    assert res["result"] == "supported"
    assert res["value_levels"] == ["unit"]
    assert "85,15" in res["evidence"][0]["snippet"] and res["evidence"][0]["source_id"] == "s0"
    rec = res["claim_record"]
    assert rec["Excel_satırı"] == "Yanıtlar!8" and rec["sonuç"] == "supported" and rec["resmî_URL"] == ["https://kvk.nl/inschrijven"]
    assert "85,15" in rec["kaynak_bölümü"] and rec["kontrol_tarihi"] == "2026-10-20T21:00:00+0200"


def test_not_in_source_when_text_lacks_value(index):
    res = cc.check_claim(_claim("e:kvk:#2", [_money(80)], ["https://www.kvk.nl/inschrijven"]), index)
    assert res["result"] == "not_in_source" and res["value_levels"] == [None]
    assert res["sources"][0]["snapshot_state"] == "ok"


def test_duration_unit_mode_vs_number_mode(index):
    claim = _claim("e:ww:#1", [_dur(5, "year")], ["https://www.uwv.nl/nl/ww"])
    assert cc.check_claim(claim, index)["result"] == "not_in_source"
    assert cc.check_claim(claim, index)["value_levels"] == ["number"]
    assert cc.check_claim(claim, index, mode="number")["result"] == "supported"


def test_range_needs_all_values(index):
    res = cc.check_claim(_claim("e:ww:#2", [_dur(26, "week"), _dur(30, "week")], ["https://www.uwv.nl/nl/ww"]), index)
    assert res["result"] == "not_in_source" and res["value_levels"] == ["unit", None]
    res = cc.check_claim(_claim("e:ww:#3", [_dur(26, "week"), _dur(36, "week")], ["https://www.uwv.nl/nl/ww"]), index)
    assert res["result"] == "supported"


@pytest.mark.parametrize("url", ["https://www.acm.nl/oud", "https://www.cbr.nl/nl/x", "https://nergens.nl/pagina", "https://www.nolink.nl/page"])
def test_no_snapshot_for_missing_error_or_unknown_pages(index, url):
    res = cc.check_claim(_claim("e:x:#1", [_money(80)], [url]), index)
    assert res["result"] == "no_snapshot"


def test_thin_page_without_value_is_no_snapshot_but_with_value_is_supported(index):
    url = "https://www.eindhoven.nl/onderwijs"
    assert cc.check_claim(_claim("e:x:#1", [_money(80)], [url]), index)["result"] == "no_snapshot"
    assert cc.check_claim(_claim("e:x:#2", [{"kind": "age", "value": 5}], [url]), index)["result"] == "supported"


def test_homepage_only_takes_precedence(index):
    res = cc.check_claim(_claim("e:x:#1", [{"kind": "weekday", "value": "saturday"}], ["https://www.example.nl/"]), index)
    assert res["result"] == "homepage_only_source"
    assert res["value_levels"] == ["unit"]  # deger anasayfada gecse bile sinif anasayfa


def test_mixed_sources_partial_checks_report_uncertainty(index):
    res = cc.check_claim(_claim("e:x:#1", [_money(80)], ["https://www.kvk.nl/inschrijven", "https://www.eindhoven.nl/onderwijs"]), index)
    assert res["result"] == "not_in_source"
    assert "1/2" in res["uncertainty"]


def test_homepage_value_counts_when_other_source_is_specific(index):
    res = cc.check_claim(_claim("e:x:#1", [_money(80)], ["https://www.example.nl/", "https://www.kvk.nl/inschrijven"]), index)
    assert res["result"] == "supported" and res["evidence"][0]["source_id"] == "s0"


@pytest.mark.parametrize("value,text,sentence,near,far", [  # ilk eslesme degil: once kart parcasinin sayilari, sonra cumlenin adlari
    ({"kind": "weekday", "value": "saturday"}, "Cumartesi", "Heuvel Cuma-Cumartesi 04:30'a kadar açık.", "Heuvel", "Septemberplein"),
    ({"kind": "age", "value": 4}, "4-11 yaş", "Dutch Bilingual (4-12 yaş), Primary International (4-11 yaş).", "4-11", "4-12"),
])
def test_evidence_prefers_the_match_near_the_claims_numbers_and_names(tmp_path, value, text, sentence, near, far):
    _write_pair(tmp_path, "p", {"url": "https://www.example.org/p", "status": 200}, f"{FILLER} 18 Septemberplein: ma t/m za 07.00 - 01.00"
                f" uur. Dutch Bilingual (ages 4-12). {FILLER} Heuvel: vrij & za 08.00 - 04.30 uur. Primary International (ages 4-11). {FILLER}")
    claim = {**_claim("e:x:#1", [value], ["https://www.example.org/p"]), "text": text, "sentence": sentence}
    snippet = cc.check_claim(claim, cc.load_snapshots(tmp_path, "qwen-cache"))["evidence"][0]["snippet"]
    assert near in snippet and far not in snippet


@pytest.mark.parametrize("text,level", [
    ("Het fonds bedraagt € 1,5 miljoen per jaar.", "unit"), ("Budget 1.500.000 euro.", "unit"),
    ("Budget van 1,5 million EUR.", "unit"), ("Er is 1,5 miljoen beschikbaar.", "number"),
    ("Het kost € 1,5 per stuk.", None), ("Budget 1,5 mld euro.", None),
])
def test_scaled_money_matches_mantissa_with_magnitude_word_or_full_number(text, level):
    value = {"kind": "money", "value": 1500000, "currency": "EUR", "scale": 1000000}
    assert cc.match_value(value, text)[0] == level


def test_no_source(index):
    assert cc.check_claim(_claim("e:x:#1", [_money(80)], []), index)["result"] == "no_source"
    assert cc.check_claim(_claim("e:x:#2", [_money(80)], [None]), index)["result"] == "no_source"


def test_check_claim_does_not_mutate_claim(index):
    claim = _claim("e:kvk:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"])
    before = copy.deepcopy(claim)
    cc.check_claim(claim, index)
    assert claim == before


def test_check_claims_summary(index):
    claims = [_claim("e:a:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"]),
              _claim("e:a:#2", [_money(80)], ["https://kvk.nl/inschrijven"]),
              _claim("e:b:#1", [_dur(5, "year")], ["https://www.uwv.nl/nl/ww"]),
              _claim("e:c:#1", [_money(80)], [])]
    report = cc.check_claims(claims, index)
    s = report["summary"]
    assert s["claims"] == 4
    assert s["by_result"] == {"supported": 1, "not_in_source": 2, "no_snapshot": 0, "homepage_only_source": 0, "no_source": 1}
    assert s["by_kind"]["money"]["supported"] == 1
    assert s["number_only_hits"] == 1
    assert s["source_states"] == {"ok": 2}
    assert "doğruluk kanıtı değil" in report["note"]
    assert [r["claim_id"] for r in report["results"]] == ["e:a:#1", "e:a:#2", "e:b:#1", "e:c:#1"]


# --- CLI ----------------------------------------------------------------------------------------

def _write_claims(path, claims):
    path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in claims), encoding="utf-8")
    return path


def test_main_writes_report_and_one_line_summary(tmp_path, qwen_cache, capsys):
    claims = _write_claims(tmp_path / "claims.jsonl", [_claim("e:a:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"]),
                                                       _claim("e:a:#2", [_money(80)], ["https://kvk.nl/inschrijven"])])
    out = tmp_path / "rep" / "claim-checks.json"
    code = cc.main(["--claims", str(claims), "--snapshots", str(qwen_cache), "--snapshot-format", "qwen-cache", "--out", str(out)])
    lines = capsys.readouterr().out.strip().splitlines()
    assert code == 1 and len(lines) == 1
    summary = json.loads(lines[0])
    assert summary["by_result"]["supported"] == 1 and summary["snapshot_format"] == "qwen-cache"
    report = json.loads(out.read_text(encoding="utf-8"))
    assert len(report["results"]) == 2


def test_main_exit_zero_when_all_supported_and_auto_format(tmp_path, qwen_cache, capsys):
    claims = _write_claims(tmp_path / "claims.jsonl", [_claim("e:a:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"])])
    out = tmp_path / "claim-checks.json"
    assert cc.main(["--claims", str(claims), "--snapshots", str(qwen_cache), "--out", str(out)]) == 0
    assert json.loads(capsys.readouterr().out)["snapshot_format"] == "qwen-cache"


def test_main_is_deterministic(tmp_path, qwen_cache, capsys):
    claims = _write_claims(tmp_path / "claims.jsonl", [_claim("e:a:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"]),
                                                       _claim("e:b:#1", [_money(80)], ["https://www.example.nl/"])])
    a, b = tmp_path / "a.json", tmp_path / "b.json"
    cc.main(["--claims", str(claims), "--snapshots", str(qwen_cache), "--out", str(a)])
    cc.main(["--claims", str(claims), "--snapshots", str(qwen_cache), "--out", str(b)])
    assert a.read_bytes() == b.read_bytes()


def test_main_usage_errors(tmp_path, qwen_cache, capsys):
    out = tmp_path / "x.json"
    assert cc.main(["--claims", str(tmp_path / "yok.jsonl"), "--snapshots", str(qwen_cache), "--out", str(out)]) == 2
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{not json}\n", encoding="utf-8")
    assert cc.main(["--claims", str(bad), "--snapshots", str(qwen_cache), "--out", str(out)]) == 2
    shape = _write_claims(tmp_path / "shape.jsonl", [{"claim_id": "x"}])
    assert cc.main(["--claims", str(shape), "--snapshots", str(qwen_cache), "--out", str(out)]) == 2
    good = _write_claims(tmp_path / "good.jsonl", [_claim("e:a:#1", [_money(80)], [])])
    assert cc.main(["--claims", str(good), "--snapshots", str(tmp_path / "yok"), "--out", str(out)]) == 2
    empty = tmp_path / "empty"
    empty.mkdir()
    assert cc.main(["--claims", str(good), "--snapshots", str(empty), "--out", str(out)]) == 2
    for line in capsys.readouterr().out.strip().splitlines():
        assert "error" in json.loads(line)


@pytest.mark.parametrize("name,content", [
    ("sources_str", json.dumps({"claim_id": "x", "values": [{"kind": "money", "value": 80}], "sources": ["https://kvk.nl"]})),
    ("values_str", json.dumps({"claim_id": "x", "values": ["80"], "sources": []})),
    ("latin", None),
])
def test_main_malformed_claims_exit_2_with_one_json_line(tmp_path, qwen_cache, capsys, name, content):
    path = tmp_path / f"{name}.jsonl"
    if content is None:
        path.write_bytes(b"\xff" + '{"claim_id": "ü"}'.encode("latin-1"))
    else:
        path.write_text(content + "\n", encoding="utf-8")
    assert cc.main(["--claims", str(path), "--snapshots", str(qwen_cache), "--out", str(tmp_path / "x.json")]) == 2
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1 and "error" in json.loads(lines[0])


def test_main_claims_without_top_level_kind_do_not_crash(tmp_path, qwen_cache, capsys):
    bare = {k: v for k, v in _claim("e:b:#1", [_money(80)], ["https://kvk.nl/inschrijven"]).items() if k != "kind"}
    claims = _write_claims(tmp_path / "claims.jsonl", [_claim("e:a:#1", [_money(85.15)], ["https://kvk.nl/inschrijven"]), bare])
    assert cc.main(["--claims", str(claims), "--snapshots", str(qwen_cache), "--out", str(tmp_path / "x.json")]) == 1
    assert json.loads(capsys.readouterr().out)["by_kind"] == {"None": {"not_in_source": 1}, "money": {"supported": 1}}


def test_main_non_utf8_toolkit_index_exit_2(tmp_path, capsys):
    root = tmp_path / "snap"
    root.mkdir()
    (root / "index.jsonl").write_bytes(b"\xff" + '{"url": "https://kvk.nl/ü"}'.encode("latin-1"))
    good = _write_claims(tmp_path / "good.jsonl", [_claim("e:a:#1", [_money(80)], [])])
    assert cc.main(["--claims", str(good), "--snapshots", str(root), "--out", str(tmp_path / "x.json")]) == 2
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1 and "error" in json.loads(lines[0])
