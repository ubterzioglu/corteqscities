"""commons_search testleri: sahte HTTP katmani, ag yok."""
from __future__ import annotations

import io
import json
import urllib.error
import urllib.request
from urllib.parse import parse_qs, urlsplit

import pytest

import commons_search as cs


def info(title: str) -> dict:
    return {"url": f"https://upload.wikimedia.org/x/{title}", "width": 4000, "height": 3000, "mime": "image/jpeg",
            "sha1": "ab" * 20, "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}}}


UTM = "?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content="
UP = "https://upload.wikimedia.org/wikipedia/commons/a/ab/"
TH = "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/"


ARTIST_HTML = f'<a href="//commons.wikimedia.org/wiki/User:X">X</a><img src="{UP}Pencil.svg{UTM}x">'


def info_2026(title: str) -> dict:
    """Wikimedia 2026 bicimi (Eindhoven search.jsonl'den): thumb.wikimedia.org thumb, adreslerde ?utm_* sorgusu."""
    name = title.removeprefix("File:").replace(" ", "_")
    thumb, unscaled = f"{TH}{name}/1280px-{name}{UTM}thumbnail", f"{UP}{name}{UTM}thumbnail_unscaled"
    return {**info(title), "url": f"{UP}{name}{UTM}original", "thumburl": thumb, "thumbwidth": 1280,
            "thumbattribs": {"src": thumb, "srcset": f"{unscaled} 1.5x, {unscaled} 2x", "decoding": "async", "width": 1280},
            "responsiveUrls": {"2": unscaled},
            "descriptionurl": f"https://commons.wikimedia.org/wiki/File:{name}?uselang=tr#Licensing",
            "descriptionshorturl": "https://commons.wikimedia.org/w/index.php?curid=1035337",
            "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}, "Artist": {"value": ARTIST_HTML}}}


class FakeApi:
    """Wikimedia API taklidi; her cagriyi kaydeder."""

    def __init__(self, entities=None, cats=None, geo=None, search=None, missing=(), wd_search=None, info_fn=info):
        self.entities, self.cats, self.geo, self.search = entities or {}, cats or {}, geo or [], search or []
        self.missing, self.wd_search, self.info_fn = set(missing), wd_search or {}, info_fn
        self.calls: list[tuple[dict, dict]] = []

    def __call__(self, url: str, headers: dict):
        q = {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}
        self.calls.append((q, headers))
        if q.get("action") == "wbgetentities":
            ids = q["ids"].split("|")
            return 200, {}, json.dumps({"entities": {i: self.entities.get(i, {}) for i in ids}}).encode()
        if q.get("action") == "wbsearchentities":
            return 200, {}, json.dumps({"search": [{"id": i} for i in self.wd_search.get(q["search"], [])]}).encode()
        if q.get("list") == "categorymembers":
            body = {"query": {"categorymembers": [{"title": t} for t in self.cats.get(q["cmtitle"], [])]}}
        elif q.get("list") == "geosearch":
            body = {"query": {"geosearch": [{"title": t} for t in self.geo[:int(q["gslimit"])]]}}
        elif q.get("list") == "search":
            body = {"query": {"search": [{"title": t} for t in self.search]}}
        elif q.get("prop") == "imageinfo":
            pages = []
            for t in q["titles"].split("|"):
                pages.append({"title": t, "missing": True} if t in self.missing else {"title": t, "imageinfo": [self.info_fn(t)]})
            body = {"query": {"pages": pages}}
        else:
            body = {}
        return 200, {}, json.dumps(body).encode()


def entity(p18=None, p373=None, coord=None) -> dict:
    claims = {}
    if p18:
        claims["P18"] = [{"mainsnak": {"datavalue": {"value": p18}}}]
    if p373:
        claims["P373"] = [{"mainsnak": {"datavalue": {"value": p373}}}]
    if coord:
        claims["P625"] = [{"mainsnak": {"datavalue": {"value": {"latitude": coord[0], "longitude": coord[1]}}}}]
    return {"claims": claims}


VENUE = {"entry_id": "e:van", "name": "Van Abbemuseum", "aliases": [], "municipality": "Eindhoven",
         "lat": 51.43, "lon": 5.48, "wikidata": "Q1", "commons_category": None}


def make_client(tmp_path, transport, max_requests=50, sleeps=None):
    sl = sleeps if sleeps is not None else []
    return cs.Client(transport, tmp_path / "cache", max_requests, sleep=sl.append, delay=0.0), sl


def test_candidates_order_and_dedupe(tmp_path):
    api = FakeApi(entities={"Q1": entity("Van_Abbemuseum 1.jpg", "Van Abbemuseum")},
                  cats={"Category:Van Abbemuseum": ["File:Van Abbemuseum 1.jpg", "File:Cat2.jpg"]},
                  geo=["File:Cat2.jpg", "File:Geo3.jpg"], search=["File:Geo3.jpg", "File:Search4.jpg"])
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, VENUE, radius=400, limit=30)
    # sira: wikidata -> kategori -> isim aramasi -> geosearch (geosearch en son, ayni dosyayi baska kaynak bulduysa onun etiketi)
    assert [(r["title"], r["query_kind"]) for r in records] == [
        ("File:Van Abbemuseum 1.jpg", "wikidata_p18"), ("File:Cat2.jpg", "category"),
        ("File:Geo3.jpg", "search"), ("File:Search4.jpg", "search")]
    assert all(r["entry_id"] == "e:van" and "extmetadata" in r["imageinfo"] for r in records)
    searched = [q for q, _ in api.calls if q.get("list") == "search"][0]
    assert searched["srsearch"] == '"Van Abbemuseum" Eindhoven' and searched["srnamespace"] == "6"
    geo = [q for q, _ in api.calls if q.get("list") == "geosearch"][0]
    assert geo["gsradius"] == "400" and geo["gsnamespace"] == "6" and geo["gscoord"] == "51.43|5.48"
    assert geo["gslimit"] == str(cs.DEFAULT_GEO_MAX)


GEO30 = [f"File:Geo{i}.jpg" for i in range(30)]


def test_geosearch_capped_and_cannot_crowd_out_name_search(tmp_path):
    # Eindhoven kabul testi: 30+ geotag'li mekanda geosearch tavani dolduruyor, isim aramasi kesiliyordu
    api = FakeApi(entities={"Q1": entity("P.jpg", "Van Abbemuseum")},
                  cats={"Category:Van Abbemuseum": ["File:C1.jpg", "File:C2.jpg"]},
                  geo=GEO30, search=["File:S1.jpg", "File:S2.jpg", "File:S3.jpg"])
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, VENUE, radius=400, limit=30)
    kinds = [r["query_kind"] for r in records]
    assert kinds.count("wikidata_p18") == 1 and kinds.count("category") == 2 and kinds.count("search") == 3
    assert kinds.count("geosearch") == cs.DEFAULT_GEO_MAX
    assert kinds[-cs.DEFAULT_GEO_MAX:] == ["geosearch"] * cs.DEFAULT_GEO_MAX


def test_geo_max_zero_skips_geosearch(tmp_path):
    api = FakeApi(geo=GEO30, search=["File:S1.jpg"])
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, {**VENUE, "wikidata": None}, 400, 30, geo_max=0)
    assert [r["query_kind"] for r in records] == ["search"]
    assert not [q for q, _ in api.calls if q.get("list") == "geosearch"]


NEAR, FAR = (51.4335, 5.4815), (52.37, 4.89)  # ~0,4 km / Amsterdam ~110 km


def test_wikidata_resolved_by_name_only_when_coordinates_match(tmp_path):
    api = FakeApi(wd_search={"Van Abbemuseum": ["Q9", "Q7"]},
                  entities={"Q9": entity("Far.jpg", "Far", FAR), "Q7": entity("Near.jpg", "Near", NEAR)},
                  cats={"Category:Near": ["File:N1.jpg"], "Category:Far": ["File:F1.jpg"]})
    client, _ = make_client(tmp_path, api)
    records, qid = cs.search_venue_detail(client, {**VENUE, "wikidata": None}, 400, 30)
    assert qid == "Q7"
    assert [(r["title"], r["query_kind"]) for r in records] == [("File:Near.jpg", "wikidata_p18"), ("File:N1.jpg", "category")]
    searched = [q for q, _ in api.calls if q.get("action") == "wbsearchentities"][0]
    assert searched["type"] == "item" and searched["language"] == "en"
    batch = [q for q, _ in api.calls if q.get("action") == "wbgetentities"]
    assert len(batch) == 1 and batch[0]["ids"] == "Q9|Q7"  # adaylar tek istekte


def test_wikidata_resolution_rejects_far_items_and_needs_coordinates(tmp_path):
    api = FakeApi(wd_search={"Van Abbemuseum": ["Q9"]}, entities={"Q9": entity("Far.jpg", None, FAR)})
    client, _ = make_client(tmp_path, api)
    records, qid = cs.search_venue_detail(client, {**VENUE, "wikidata": None}, 400, 30)
    assert qid is None and not records
    api2 = FakeApi(wd_search={"Van Abbemuseum": ["Q9"]}, entities={"Q9": entity("Near.jpg", None, NEAR)})
    client2, _ = make_client(tmp_path / "b", api2)
    _, qid2 = cs.search_venue_detail(client2, {**VENUE, "wikidata": None, "lat": None, "lon": None}, 400, 30)
    assert qid2 is None and not [q for q, _ in api2.calls if q.get("action") == "wbsearchentities"]


def test_wikidata_resolution_skips_items_without_coordinates_and_empty_search(tmp_path):
    api = FakeApi(wd_search={"Van Abbemuseum": ["Q5", "Q7"]},
                  entities={"Q5": entity("NoCoord.jpg"), "Q7": entity("Near.jpg", None, NEAR)})
    client, _ = make_client(tmp_path, api)
    _, qid = cs.search_venue_detail(client, {**VENUE, "wikidata": None, "language": "nl"}, 400, 30)
    assert qid == "Q7"
    assert [q for q, _ in api.calls if q.get("action") == "wbsearchentities"][0]["language"] == "nl"
    client2, _ = make_client(tmp_path / "b", FakeApi())
    _, qid2 = cs.search_venue_detail(client2, {**VENUE, "wikidata": None}, 400, 30)
    assert qid2 is None


def test_given_wikidata_is_not_overridden(tmp_path):
    api = FakeApi(wd_search={"Van Abbemuseum": ["Q7"]}, entities={"Q1": entity("Given.jpg")})
    client, _ = make_client(tmp_path, api)
    records, qid = cs.search_venue_detail(client, VENUE, 400, 30)
    assert qid is None and records[0]["title"] == "File:Given.jpg"
    assert not [q for q, _ in api.calls if q.get("action") == "wbsearchentities"]


def test_etiquette_params_and_user_agent(tmp_path):
    api = FakeApi(search=["File:A.jpg"])
    client, sleeps = make_client(tmp_path, api)
    cs.search_venue(client, {**VENUE, "wikidata": None, "lat": None, "lon": None}, 400, 30)
    for q, headers in api.calls:
        assert q["maxlag"] == "5" and q["format"] == "json" and q["formatversion"] == "2"
        assert headers["User-Agent"].startswith("CorteqsCityToolkit/0.1")
    assert len(sleeps) == 0 or all(s >= 0 for s in sleeps)


def test_sources_skipped_without_data(tmp_path):
    api = FakeApi(search=["File:A.jpg"])
    client, _ = make_client(tmp_path, api)
    cs.search_venue(client, {"entry_id": "e:x", "name": "X", "municipality": "Y"}, 400, 30)
    kinds = [q.get("list") or q.get("prop") for q, _ in api.calls]
    assert kinds == ["search", "imageinfo"]


def test_wikidata_category_used_when_not_given(tmp_path):
    api = FakeApi(entities={"Q1": entity(None, "Cat X")}, cats={"Category:Cat X": ["File:C.jpg"]})
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, {**VENUE, "lat": None, "lon": None, "name": ""}, 400, 30)
    assert [r["title"] for r in records] == ["File:C.jpg"]


def test_imageinfo_batches_of_50_and_missing_skipped(tmp_path):
    titles = [f"File:T{i}.jpg" for i in range(120)]
    api = FakeApi(cats={"Category:Big": titles}, missing={"File:T5.jpg"})
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, {"entry_id": "e:b", "name": "", "municipality": "", "commons_category": "Big"}, 400, 200)
    batches = [q["titles"].count("|") + 1 for q, _ in api.calls if q.get("prop") == "imageinfo"]
    assert batches == [50, 50, 20]
    assert len(records) == 119


def test_imageinfo_requests_standard_thumb_width(tmp_path):
    # Wikimedia 2026: yalniz standart genislikler (330/500/960/1280...); 1600 px thumb HTTP 400 veriyor
    api = FakeApi(search=["File:A.jpg"])
    client, _ = make_client(tmp_path, api)
    cs.search_venue(client, {**VENUE, "wikidata": None, "lat": None, "lon": None}, 400, 30)
    widths = {q["iiurlwidth"] for q, _ in api.calls if q.get("prop") == "imageinfo"}
    assert cs.DEFAULT_THUMB_WIDTH == 1280 and widths == {"1280"}


def test_strip_query_removes_query_and_fragment_only():
    base = f"{UP}Van_Abbemuseum%2C_Eindhoven.jpg"
    assert cs.strip_query(f"{base}{UTM}original") == base
    assert cs.strip_query(f"{base}#Licensing") == base
    assert cs.strip_query(f"{base}#a?b") == base
    assert cs.strip_query(base) == base


def test_clean_imageinfo_returns_copy_and_skips_non_strings():
    raw = info_2026("File:A.jpg")
    before = json.dumps(raw, sort_keys=True)
    cleaned = cs.clean_imageinfo(raw)
    assert json.dumps(raw, sort_keys=True) == before  # girdi degismez
    assert "utm_" not in json.dumps({k: v for k, v in cleaned.items() if k != "extmetadata"})
    assert cleaned["extmetadata"] == raw["extmetadata"]  # lisans kaniti HTML'i oldugu gibi kalir
    assert cleaned["thumbattribs"]["decoding"] == "async"
    odd = {"url": None, "thumburl": 5, "thumbattribs": None, "responsiveUrls": {"2": None}, "width": 10}
    assert cs.clean_imageinfo(odd) == odd


def test_output_urls_have_no_query_but_curid_kept(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [{"entry_id": "e:x", "name": "X", "municipality": "Y"}])
    code, out = run_main(tmp_path, FakeApi(search=["File:Van Abbemuseum.jpg"], info_fn=info_2026))
    assert code == 0
    rec = json.loads(out.read_text(encoding="utf-8").splitlines()[0])["imageinfo"]
    assert "utm_" not in json.dumps({k: v for k, v in rec.items() if k != "extmetadata"}) and "uselang" not in json.dumps(rec)
    assert rec["url"] == f"{UP}Van_Abbemuseum.jpg"
    assert rec["thumburl"] == rec["thumbattribs"]["src"] == f"{TH}Van_Abbemuseum.jpg/1280px-Van_Abbemuseum.jpg"
    assert rec["thumbattribs"]["srcset"] == f"{UP}Van_Abbemuseum.jpg 1.5x, {UP}Van_Abbemuseum.jpg 2x"
    assert rec["responsiveUrls"] == {"2": f"{UP}Van_Abbemuseum.jpg"}
    assert rec["descriptionurl"] == "https://commons.wikimedia.org/wiki/File:Van_Abbemuseum.jpg"
    assert rec["descriptionshorturl"].endswith("?curid=1035337")  # bu sorgu adresin kimligi: korunur
    assert rec["extmetadata"]["Artist"]["value"] == ARTIST_HTML  # lisans kaniti: dokunulmaz


def test_limit_caps_candidates(tmp_path):
    api = FakeApi(cats={"Category:Big": [f"File:T{i}.jpg" for i in range(40)]})
    client, _ = make_client(tmp_path, api)
    records = cs.search_venue(client, {"entry_id": "e:b", "name": "", "municipality": "", "commons_category": "Big"}, 400, 10)
    assert len(records) == 10


def test_cache_makes_rerun_free(tmp_path):
    api = FakeApi(search=["File:A.jpg"])
    c1, _ = make_client(tmp_path, api)
    cs.search_venue(c1, VENUE, 400, 30)
    made = c1.requests_made
    assert made > 0 and c1.cache_hits == 0
    c2, _ = make_client(tmp_path, api)
    cs.search_venue(c2, VENUE, 400, 30)
    assert c2.requests_made == 0 and c2.cache_hits == made


def test_budget_cap(tmp_path):
    client, _ = make_client(tmp_path, FakeApi(search=["File:A.jpg"]), max_requests=1)
    with pytest.raises(cs.BudgetExceeded):
        cs.search_venue(client, VENUE, 400, 30)
    assert client.requests_made == 1


class Flaky:
    def __init__(self, responses):
        self.responses, self.n = list(responses), 0

    def __call__(self, url, headers):
        self.n += 1
        return self.responses.pop(0)


def ok(body=None):
    return 200, {}, json.dumps(body or {"query": {}}).encode()


def test_retry_after_then_success(tmp_path):
    flaky = Flaky([(429, {"Retry-After": "2"}, b""), ok()])
    client, sleeps = make_client(tmp_path, flaky)
    assert client.get_json("https://x/w/api.php", {"a": "1"}) == {"query": {}}
    assert 2 in sleeps and flaky.n == 2


def test_retry_after_too_long_stops(tmp_path):
    client, _ = make_client(tmp_path, Flaky([(503, {"Retry-After": "120"}, b"")]))
    with pytest.raises(cs.ResumeLater):
        client.get_json("https://x/w/api.php", {"a": "1"})


def test_three_failures_resume_later(tmp_path):
    flaky = Flaky([(503, {}, b"")] * 3)
    client, _ = make_client(tmp_path, flaky)
    with pytest.raises(cs.ResumeLater):
        client.get_json("https://x/w/api.php", {"a": "1"})
    assert flaky.n == 3


def test_maxlag_error_is_retried_and_errors_not_cached(tmp_path):
    lag = (200, {"Retry-After": "1"}, json.dumps({"error": {"code": "maxlag"}}).encode())
    client, _ = make_client(tmp_path, Flaky([lag, ok({"query": {"a": 1}})]))
    assert client.get_json("https://x/w/api.php", {"a": "1"})["query"] == {"a": 1}


def test_api_error_and_http_error(tmp_path):
    client, _ = make_client(tmp_path, Flaky([(200, {}, json.dumps({"error": {"code": "badparam", "info": "x"}}).encode())]))
    with pytest.raises(cs.ApiError):
        client.get_json("https://x/w/api.php", {"a": "1"})
    client, _ = make_client(tmp_path / "b", Flaky([(404, {}, b"")]))
    with pytest.raises(cs.ApiError):
        client.get_json("https://x/w/api.php", {"a": "1"})


def test_urllib_transport(monkeypatch):
    class Resp(io.BytesIO):
        status = 200
        headers = {"X": "1"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    seen = {}

    def fake_urlopen(req, timeout):
        seen["ua"] = req.get_header("User-agent")
        return Resp(b"{}")

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert cs.urllib_transport("https://x/", {"User-Agent": "UA"})[0] == 200 and seen["ua"] == "UA"

    def raising(req, timeout):
        raise urllib.error.HTTPError("https://x/", 429, "slow", {"Retry-After": "3"}, io.BytesIO(b""))

    monkeypatch.setattr(urllib.request, "urlopen", raising)
    status, headers, _ = cs.urllib_transport("https://x/", {})
    assert status == 429 and headers["Retry-After"] == "3"

    def neterr(req, timeout):
        raise urllib.error.URLError("down")

    monkeypatch.setattr(urllib.request, "urlopen", neterr)
    with pytest.raises(cs.ApiError):
        cs.urllib_transport("https://x/", {})


def write_plan(path, rows):
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")


def run_main(tmp_path, api, extra=()):
    plan, out = tmp_path / "venues.jsonl", tmp_path / "out" / "cand.jsonl"
    argv = ["--plan", str(plan), "--out", str(out), "--cache-dir", str(tmp_path / "cache"), *extra]
    return cs.main(argv, transport=api, sleep=lambda s: None), out


def test_main_end_to_end(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [VENUE, {"entry_id": "e:none", "name": "Nirgendwo", "municipality": "Z"}, ])
    api = FakeApi(search=["File:A.jpg"])
    code, out = run_main(tmp_path, api)
    assert code == 0
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["venues"] == 2 and summary["candidates"] == 2 and summary["status"] == "ok"
    assert summary["per_venue"] == {"e:van": 1, "e:none": 1}
    rows = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
    assert {r["entry_id"] for r in rows} == {"e:van", "e:none"} and set(rows[0]) == {"entry_id", "query_kind", "title", "imageinfo"}
    # ikinci calisma: sifir istek
    code, _ = run_main(tmp_path, api)
    summary = json.loads(capsys.readouterr().out.strip())
    assert code == 0 and summary["requests_made"] == 0 and summary["cache_hits"] > 0


def test_main_geo_max_option_and_resolved_summary(tmp_path, capsys):
    venue = {**VENUE, "wikidata": None}
    write_plan(tmp_path / "venues.jsonl", [venue])
    api = FakeApi(geo=GEO30, wd_search={"Van Abbemuseum": ["Q7"]}, entities={"Q7": entity("Near.jpg", None, NEAR)})
    code, out = run_main(tmp_path, api, ("--geo-max", "2"))
    summary = json.loads(capsys.readouterr().out.strip())
    assert code == 0 and summary["wikidata_resolved"] == {"e:van": "Q7"}
    kinds = [json.loads(line)["query_kind"] for line in out.read_text(encoding="utf-8").splitlines()]
    assert kinds == ["wikidata_p18", "geosearch", "geosearch"]


def test_main_rejects_negative_geo_max(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [VENUE])
    code, _ = run_main(tmp_path, FakeApi(), ("--geo-max", "-1"))
    assert code == 2


def test_main_zero_candidates_listed(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [{"entry_id": "e:z", "name": "Z", "municipality": "Y"}])
    code, _ = run_main(tmp_path, FakeApi())
    summary = json.loads(capsys.readouterr().out.strip())
    assert code == 0 and summary["venues_with_zero_candidates"] == ["e:z"]


def test_main_budget_stops_and_writes_partial(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [VENUE])
    code, out = run_main(tmp_path, FakeApi(search=["File:A.jpg"]), ("--max-requests", "2"))
    summary = json.loads(capsys.readouterr().out.strip())
    assert code == 1 and summary["status"] == "resume_later" and summary["requests_made"] == 2 and out.exists()


def test_main_api_error_per_venue_continues(tmp_path, capsys):
    write_plan(tmp_path / "venues.jsonl", [VENUE])
    code, _ = run_main(tmp_path, Flaky([(404, {}, b"")] * 20))
    summary = json.loads(capsys.readouterr().out.strip())
    assert code == 1 and summary["errors"] and summary["venues_with_zero_candidates"] == ["e:van"]


def test_main_usage_errors(tmp_path, capsys):
    assert cs.main(["--plan", str(tmp_path / "nope.jsonl"), "--out", str(tmp_path / "o.jsonl")]) == 2
    write_plan(tmp_path / "bad.jsonl", [{"name": "no entry id"}])
    assert cs.main(["--plan", str(tmp_path / "bad.jsonl"), "--out", str(tmp_path / "o.jsonl")]) == 2
    (tmp_path / "bad2.jsonl").write_text("{not json\n", encoding="utf-8")
    assert cs.main(["--plan", str(tmp_path / "bad2.jsonl"), "--out", str(tmp_path / "o.jsonl")]) == 2
