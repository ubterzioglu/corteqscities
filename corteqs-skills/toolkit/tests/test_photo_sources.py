"""photo_sources: ikinci kaynaklardan aday ekleme, esik ve gecis sirasi (ag yok, sahte transport)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import photo_candidates as pc  # noqa: E402
import photo_sources as ps  # noqa: E402

PLAN = [{"entry_id": "t:kern-museum", "role": "venue", "name": "Kern County Museum", "aliases": [],
         "municipality": "Bakersfield"},
        {"entry_id": "t:cover", "role": "cover", "name": "Bakersfield", "aliases": []}]


def openverse_item(**over):
    base = {"title": "Kern County Museum Bakersfield entrance", "creator": "A & B", "creator_url": "https://www.flickr.com/photos/ab/",
            "url": "https://live.staticflickr.com/1/2_o.jpg", "foreign_landing_url": "https://www.flickr.com/photos/ab/2/",
            "license": "by", "license_version": "2.0", "source": "flickr", "provider": "flickr", "width": 2000,
            "height": 1500, "filetype": "jpg", "tags": [{"name": "museum"}]}
    return {**base, **over}


def transport_for(responses):
    calls = []

    def transport(url, headers):
        calls.append(url)
        for marker, payload in responses.items():
            if marker in url:
                return 200, {}, json.dumps(payload).encode()
        return 404, {}, b""
    transport.calls = calls
    return transport


def run(tmp_path, responses, **kw):
    import argparse
    plan, search = tmp_path / "venues.jsonl", tmp_path / "search.jsonl"
    plan.write_text("".join(json.dumps(r) + "\n" for r in PLAN), encoding="utf-8")
    search.write_text("".join(json.dumps(r) + "\n" for r in kw.get("existing", [])) , encoding="utf-8")
    args = argparse.Namespace(plan=plan, search=search, sources=kw.get("sources", "openverse,smithsonian"),
                              min_per_venue=kw.get("min_per", 3), per_source=6, cache_dir=tmp_path / "c",
                              max_requests=50, delay=0)
    transport = transport_for(responses)
    return ps.run(args, transport), transport, [json.loads(x) for x in search.read_text(encoding="utf-8").splitlines() if x]


def test_openverse_result_becomes_commons_shaped_record_that_photo_candidates_reads(tmp_path, capsys):
    code, transport, rows = run(tmp_path, {"openverse.org": {"results": [openverse_item()]}})
    assert code == 0 and len(rows) == 1 and rows[0]["query_kind"] == "alt:openverse"
    candidate = pc.normalize_imageinfo(rows[0]["imageinfo"])
    assert (candidate["license"], candidate["license_url"]) == ("CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/")
    assert candidate["provider"] == "Flickr" and candidate["source_url"] == "https://www.flickr.com/photos/ab/2/"
    assert candidate["original_url"].endswith("2_o.jpg")
    assert 'href="https://www.flickr.com/photos/ab/"' in rows[0]["imageinfo"]["extmetadata"]["Artist"]["value"]
    assert "A &amp; B" in rows[0]["imageinfo"]["extmetadata"]["Artist"]["value"]
    out = json.loads(capsys.readouterr().out)
    assert out["download_hosts"] == ["live.staticflickr.com"] and out["added"] == 1


def test_wrong_license_wrong_venue_and_wikimedia_results_are_dropped(tmp_path):
    items = [openverse_item(license="by-nc"), openverse_item(title="Sunset at the beach", tags=[]),
             openverse_item(source="wikimedia"), openverse_item(url="https://x.example/p.gif"),
             openverse_item(foreign_landing_url="")]
    _, _, rows = run(tmp_path, {"openverse.org": {"results": items}})
    assert rows == []


def test_covers_are_not_searched_and_entries_with_enough_commons_candidates_are_skipped(tmp_path):
    commons = [{"entry_id": "t:kern-museum", "query_kind": "p18", "title": f"File:{n}.jpg",
                "imageinfo": {"descriptionurl": f"https://commons.wikimedia.org/wiki/File:{n}.jpg"}} for n in "abc"]
    code, transport, rows = run(tmp_path, {"openverse.org": {"results": [openverse_item()]}}, existing=commons)
    assert code == 0 and transport.calls == [] and len(rows) == 3


def test_falls_through_to_next_source_when_first_finds_nothing(tmp_path):
    si = {"response": {"rows": [{"title": "Kern County Museum", "content": {"descriptiveNonRepeating": {
        "title": {"content": "Kern County Museum Bakersfield photo"}, "record_link": "https://www.si.edu/object/x",
        "data_source": "Smithsonian Archives",
        "online_media": {"media": [{"type": "Images", "usage": {"access": "CC0"},
                                    "content": "https://example.si.edu/img.jpg"}]}}}}]}}
    code, transport, rows = run(tmp_path, {"openverse.org": {"results": []}, "api.si.edu": si}, min_per=1)
    assert code == 0 and [r["query_kind"] for r in rows] == ["alt:smithsonian"]
    assert rows[0]["imageinfo"]["extmetadata"]["LicenseShortName"]["value"] == "CC0 1.0"
    assert any("openverse" in u for u in transport.calls) and any("api.si.edu" in u for u in transport.calls)


def test_second_run_does_not_repeat_a_source_already_tried(tmp_path):
    first, _, rows = run(tmp_path, {"openverse.org": {"results": [openverse_item()]}}, sources="openverse")
    again, transport, rows2 = run(tmp_path, {"openverse.org": {"results": [openverse_item()]}}, sources="openverse",
                                  existing=rows)
    assert transport.calls == [] and len(rows2) == 1


def test_license_helpers():
    assert ps.cc_license("by-sa", "4.0") == ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/")
    assert ps.cc_license("by-nc", "2.0") is None and ps.cc_license("by", "") is None
    assert ps.europeana_license("http://creativecommons.org/licenses/by/4.0/")[0] == "CC BY 4.0"
    assert ps.europeana_license("http://rightsstatements.org/vocab/InC/1.0/") is None


def test_api_key_is_not_written_to_cache_name(tmp_path):
    fetch = ps.Fetcher(transport_for({"si.edu": {"response": {}}}), tmp_path, 5, delay=0)
    fetch.get("https://api.si.edu/x", {"q": "a", "api_key": "SECRET"})
    assert not any("SECRET" in p.name for p in tmp_path.iterdir())


def test_unknown_source_is_usage_error(tmp_path, capsys):
    code, _, _ = run(tmp_path, {}, sources="nope")
    assert code == 2


def test_one_failing_source_does_not_stop_the_others(tmp_path, capsys):
    code, _, rows = run(tmp_path, {"openverse.org": {"results": [openverse_item()]}}, sources="smithsonian,openverse")
    out = json.loads(capsys.readouterr().out)
    assert code == 0 and len(rows) == 1 and out["source_errors"] and "smithsonian" in out["source_errors"][0]


def test_single_distinctive_word_needs_the_city_in_text():
    plan = {"name": "Jones Art Gallery", "aliases": [], "municipality": "Bakersfield"}
    assert not ps.matches_name(plan, "Burne Jones, Resurrection")
    assert ps.matches_name(plan, "Jones Art Gallery Bakersfield exterior")
    assert ps.matches_name({"name": "Lengthwise Brewing Company", "municipality": "Bakersfield"}, "Lengthwise Brewing sampler")


def test_delivery_url_for_second_source_keeps_original_https_address_and_commons_rule_is_unchanged():
    import photo_rows as pr
    flickr = {"provider": "Flickr", "original_url": "https://live.staticflickr.com/1/2_o.jpg?x=1", "width": 3000}
    assert pr.delivery_url(flickr) == flickr["original_url"]  # Wikimedia disinda sorgu (imzali adres) korunur
    assert pr.delivery_url({"provider": "Flickr", "original_url": "http://insecure.example/a.jpg"}) == ""
    assert pr.delivery_url({"original_url": "https://example.org/a.jpg"}) == ""  # Commons adayi: yalniz upload.wikimedia.org
