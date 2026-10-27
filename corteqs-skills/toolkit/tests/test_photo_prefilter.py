"""photo_rules + photo_prefilter: deterministik foto on-filtresi (ag yok, ML yok)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import photo_prefilter as pf
import photo_rules as pr


def cand(**over) -> dict:
    base = {"candidate_id": "c1", "entry_id": "tv:museum", "title": "Van Abbemuseum Testville facade",
            "description_text": "Museum building in Testville", "categories": ["Van Abbemuseum", "2019 in Testville"],
            "date_original": "2019-05-04", "year": 2019, "lat": None, "lon": None, "width": 4000, "height": 3000,
            "mime": "image/jpeg", "license": "CC BY-SA 4.0", "restrictions": "", "author_text": "Jane"}
    base.update(over)
    return base


def entry(**over) -> dict:
    base = {"entry_id": "tv:museum", "role": "venue", "name": "Van Abbemuseum", "aliases": [], "municipality": "Testville",
            "municipality_aliases": ["Testville"], "group": "Müzeler", "lat": 51.4347, "lon": 5.4819}
    base.update(over)
    return base


def decide(c: dict, e: dict | None = None, rules: dict | None = None) -> dict:
    return pr.evaluate(c, entry() if e is None else e, rules or pr.DEFAULT_RULES)


def test_clean_candidate_is_keep():
    result = decide(cand())
    assert result["decision"] == "keep" and result["reasons"] == [] and result["score"] > 0


@pytest.mark.parametrize("lic,decision", [
    ("CC0", "keep"), ("Public domain", "keep"), ("PD-self", "keep"), ("CC BY 4.0", "keep"), ("CC BY-SA 3.0 nl", "keep"),
    ("CC BY-SA 2.0 de", "keep"), ("CC BY-NC 2.0", "reject"), ("CC BY-ND 4.0", "reject"), ("", "reject"), ("GFDL", "reject"),
])
def test_license_rule(lic, decision):
    result = decide(cand(license=lic))
    assert result["decision"] == decision
    if decision == "reject":
        assert "license_not_allowed" in result["reasons"]


def test_restrictions_flag():
    result = decide(cand(restrictions="personality"))
    assert result["decision"] == "flag" and "restrictions" in result["reasons"]


def test_mime_and_resolution_rules():
    assert "mime_not_allowed" in decide(cand(mime="image/tiff"))["reasons"]
    assert decide(cand(mime="image/tiff"))["decision"] == "reject"
    low = decide(cand(width=800, height=500))
    assert low["decision"] == "flag" and "low_resolution" in low["reasons"]
    pano = decide(cand(width=8000, height=1800))
    assert "panorama" in pano["reasons"] and pano["decision"] == "flag"


@pytest.mark.parametrize("field,value", [
    ("categories", ["Paintings by Peter Thijs", "Testville"]),
    ("description_text", "Van Abbemuseum 80x65cm oil on linen"),
    ("categories", ["PD-Art (PD-old-70)"]),
    ("categories", ["Etchings of monasteries in the Rijksmuseum"]),
    ("title", "Constant Permeke (1886-1952) Zomer Van Abbemuseum"),
    ("title", "Schetsontwerp Van Abbemuseum"),
])
def test_art_not_photo_rejects(field, value):
    result = decide(cand(**{field: value}))
    assert result["decision"] == "reject" and "art_not_photo" in result["reasons"]


def test_art_keyword_needs_word_boundary():
    # 'ets' (Felemenkce gravur) 'streets' icinde, 'map' 'OpenStreetMap' icinde eslesmemeli
    result = decide(cand(description_text="Streets near the museum in Testville", categories=["OpenStreetMap based", "Testville"]))
    assert result["decision"] == "keep"


def test_ai_generated_rejects():
    result = decide(cand(categories=["AI-generated images", "Testville"]))
    assert result["decision"] == "reject" and "ai_generated" in result["reasons"]


def test_place_mismatch_flag_and_foreign_place_reject():
    nowhere = decide(cand(title="Farm", description_text="A farm", categories=["Farms"]))
    assert nowhere["decision"] == "flag" and "place_mismatch" in nowhere["reasons"]
    foreign = decide(cand(title="Kruisstraat 27", description_text="Boerderij in Zweeloo", categories=["2024 in Coevorden"]))
    assert foreign["decision"] == "reject" and "other_place" in foreign["reasons"]
    # bilinen yer listesinden (config) gelen baska belediye adi
    rules = pr.merge_rules(pr.DEFAULT_RULES, {"place": {"known_other_places": ["Zweeloo"]}})
    named = decide(cand(title="Farm", description_text="Farm in Zweeloo", categories=["Farms"]), rules=rules)
    assert named["decision"] == "reject"


def test_venue_name_counts_as_place_match():
    result = decide(cand(title="Van Abbemuseum entrance", description_text="", categories=["Museums"]))
    assert "place_mismatch" not in result["reasons"]


def test_topic_year_category_is_not_a_place():
    c = cand(title="Stadion", description_text="Tribune", categories=["2017 in field hockey"])
    result = decide(c)
    assert "other_place" not in result["reasons"] and "place_mismatch" in result["reasons"]


def test_containing_region_is_not_other_place():
    result = decide(cand(categories=["2019 in North Brabant", "Van Abbemuseum"], title="Museum", description_text=""))
    assert "other_place" not in result["reasons"]


@pytest.mark.parametrize("lat,lon,decision,code", [
    (51.4350, 5.4820, "keep", None), (51.48, 5.48, "flag", "gps_far"), (47.6, -122.3, "reject", "gps_far"),
])
def test_gps_distance(lat, lon, decision, code):
    result = decide(cand(lat=lat, lon=lon))
    assert result["decision"] == decision
    if code:
        assert code in result["reasons"]


def test_gps_ignored_without_entry_coordinates():
    assert decide(cand(lat=47.6, lon=-122.3), entry(lat=None, lon=None))["decision"] == "keep"


def test_gps_city_radius_for_entries_without_coordinates():
    far = decide(cand(lat=47.6, lon=-122.3), entry(lat=None, lon=None, city_lat=51.43, city_lon=5.5))
    assert far["decision"] == "reject"


def test_archive_flag_and_cover_reject():
    old = cand(year=1966, date_original="1966-05")
    assert decide(old)["decision"] == "flag" and "archive" in decide(old)["reasons"]
    assert decide(old, entry(role="cover"))["decision"] == "reject"
    cat_year = cand(categories=["Van Abbemuseum", "1992 events in the Netherlands", "Testville"])
    assert "archive" in decide(cat_year)["reasons"]


@pytest.mark.parametrize("text", ["Catharinakerk - Orgel", "Heuvelgalerie koepel trappenhuis", "Graf van Arnol Kox",
                                  "Plaquette in het station", "Beer bottles", "Interior of the hall"])
def test_detail_flag_and_district_cover_reject(text):
    c = cand(description_text=f"{text} Testville")
    assert decide(c)["decision"] == "flag" and "detail_interior" in decide(c)["reasons"]
    assert decide(c, entry(role="district"))["decision"] == "reject"
    assert decide(c, entry(role="cover"))["decision"] == "reject"


def test_detail_keyword_in_venue_name_is_ignored():
    e = entry(name="Standbeeld Frits Philips")
    assert "statue_subject" not in decide(cand(title="Standbeeld Frits Philips Testville"), e)["reasons"]

@pytest.mark.parametrize("text", ["standbeeld Frits Philips", "Heilig Hartbeeld", "entrance with statues"])
def test_statue_flags_without_role_escalation(text):
    c = cand(description_text=f"{text} Testville")
    for role in ("venue", "district", "cover"):
        result = decide(c, entry(role=role))
        assert result["decision"] == "flag" and "statue_subject" in result["reasons"]


def test_building_design_credit_is_not_art():
    c = cand(description_text="Woontoren in Testville, naar ontwerp van architectenbureau X")
    assert decide(c)["decision"] == "keep"


def test_mural_painting_goes_to_rights_review_not_art_reject():
    c = cand(title="Memorial Painting Testville", categories=["Murals in Testville"])
    result = decide(c)
    assert result["decision"] == "flag" and "rights_review" in result["reasons"] and "art_not_photo" not in result["reasons"]


def test_street_art_venue_painting_is_not_art_reject():
    c = cand(title="Memorial Painting Testville", categories=["Berenkuil"])
    assert decide(c)["decision"] == "reject"
    assert "art_not_photo" not in decide(c, entry(name="Berenkuil street art"))["reasons"]


def test_rights_review_from_description():
    assert "rights_review" in decide(cand(description_text="Performance during DDW in Testville"))["reasons"]


def test_municipality_prefix_counts_and_street_name_does_not_beat_other_place():
    adjective = cand(title="Brug over Testvilles Kanaal", description_text="", categories=["Bridges"])
    assert "place_mismatch" not in decide(adjective, entry(name="Kanal yolu"))["reasons"]
    street = cand(title="Kruisstraat 27", description_text="Boerderij", categories=["2024 in Coevorden"])
    result = decide(street, entry(name="Kruisstraat ve carsi"))
    assert result["decision"] == "reject" and "other_place" in result["reasons"]


def test_design_does_not_match_sign():
    assert decide(cand(description_text="Dutch Design Week Testville"))["decision"] == "keep"


def test_infrastructure_rejects_for_district():
    c = cand(title="Motorway A67 near Testville")
    assert decide(c, entry(role="district"))["decision"] == "reject"
    assert "off_subject" in decide(c)["reasons"]


def test_rights_review_never_keep():
    result = decide(cand(categories=["GLOW Festival Testville 2018", "Van Abbemuseum"]))
    assert result["decision"] == "flag" and "rights_review" in result["reasons"]
    assert "rights_review" in decide(cand(categories=["Street art in Testville"]))["reasons"]


def test_geosearch_without_name_match_is_flagged_and_ranked_lower():
    geo = cand(query_kind="geosearch", title="Street view Testville", description_text="", categories=["2019 in Testville"])
    result = decide(geo)
    assert result["decision"] == "flag" and "geosearch_unconfirmed" in result["reasons"]
    named = decide(cand(query_kind="geosearch"))  # baslikta mekan adi var -> dogrulanmis
    assert "geosearch_unconfirmed" not in named["reasons"]
    by_category = decide(cand(query_kind="category", title="Street view Testville", description_text="", categories=["Testville"]))
    assert "geosearch_unconfirmed" not in by_category["reasons"]
    rules = pr.merge_rules(pr.DEFAULT_RULES, {"geosearch": {"severity": "reject"}})
    assert decide(geo, rules=rules)["decision"] == "reject"


def _sevilla(name: str, **over) -> dict:
    return entry(entry_id="sevilla:x", name=name, municipality="Sevilla", municipality_aliases=["Seville"],
                 lat=None, lon=None, **over)


def test_longer_source_name_is_flagged_as_possibly_another_building():
    """Sevilla dis denetimi S01: 'Iglesia de San Vicente' kartina Triana'daki 'San Vicente de Paúl' karesi geldi."""
    c = cand(entry_id="sevilla:x", title="File:Sevilla - Triana, Iglesia de San Vicente de Paúl 31.jpg",
             description_text="Puerta de la iglesia", categories=["Iglesia de San Vicente de Paúl (Sevilla)"])
    result = decide(c, _sevilla("Iglesia de San Vicente"))
    assert result["decision"] == "flag" and "name_extended" in result["reasons"], result
    assert any("san vicente de paul" in note for note in result["notes"])


@pytest.mark.parametrize("title, name, extra", [
    ("Iglesia de San Vicente, Sevilla 03.jpg", "Iglesia de San Vicente", {}),  # devam yok
    ("Real Alcázar de Sevilla 2019.jpg", "Real Alcázar", {}),  # sehir adi
    ("Real Alcazar of Seville gardens.jpg", "Real Alcázar", {}),  # sehirin baska adi
    ("Iglesia de Santa Ana de Triana 2.jpg", "Iglesia de Santa Ana", {"district": "Triana"}),  # kendi semti
    ("Iglesia de San Vicente de Paúl 31.jpg", "Iglesia de San Vicente de Paúl", {}),  # adin tamami
    ("Iglesia de San Vicente (Sevilla) - de 2015.jpg", "Iglesia de San Vicente", {}),  # 'de' + sayi ad degil
    ("Torre del Oro de noche.jpg", "Torre del Oro", {}),  # 'de noche': yaygin betimleme
])
def test_legitimate_name_continuations_are_not_flagged(title, name, extra):
    c = cand(entry_id="sevilla:x", title=title, description_text="", categories=[])
    result = decide(c, _sevilla(name, **extra))
    assert "name_extended" not in result["reasons"], result


def test_missing_entry_flags():
    result = pr.evaluate(cand(), None, pr.DEFAULT_RULES)
    assert result["decision"] == "flag" and "no_plan_entry" in result["reasons"]


def test_merge_rules_overrides_without_mutation():
    merged = pr.merge_rules(pr.DEFAULT_RULES, {"resolution": {"min_short_side": 100}})
    assert merged["resolution"]["min_short_side"] == 100
    assert pr.DEFAULT_RULES["resolution"]["min_short_side"] == 600
    assert merged["resolution"]["panorama_ratio"] == pr.DEFAULT_RULES["resolution"]["panorama_ratio"]


def test_evaluate_does_not_mutate():
    c, e = cand(), entry()
    before = json.dumps([c, e], sort_keys=True)
    decide(c, e)
    assert json.dumps([c, e], sort_keys=True) == before


def test_haversine_km():
    assert pr.haversine_km(51.0, 5.0, 51.0, 5.0) == 0
    assert pr.haversine_km(51.4416, 5.4697, 52.3676, 4.9041) == pytest.approx(110, abs=5)


# --- prefilter: shortlist + CLI ---

def test_build_shortlists_orders_keep_then_flag_and_skips_reject():
    decisions = [
        {"candidate_id": "b", "entry_id": "e1", "decision": "flag", "score": 90},
        {"candidate_id": "a", "entry_id": "e1", "decision": "keep", "score": 80},
        {"candidate_id": "c", "entry_id": "e1", "decision": "keep", "score": 80},
        {"candidate_id": "d", "entry_id": "e1", "decision": "reject", "score": 99},
        {"candidate_id": "e", "entry_id": "e1", "decision": "keep", "score": 95},
    ]
    assert pf.build_shortlists(decisions, 3) == {"e1": ["e", "a", "c"]}
    assert pf.build_shortlists(decisions, 10)["e1"] == ["e", "a", "c", "b"]


def _jsonl(path: Path, rows: list[dict]) -> Path:
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")
    return path


def test_cli_end_to_end(tmp_path, capsys):
    cands = _jsonl(tmp_path / "c.jsonl", [cand(), cand(candidate_id="c2", license="CC BY-NC 2.0"),
                                          cand(candidate_id="c3", width=500, height=400)])
    plan = _jsonl(tmp_path / "p.jsonl", [entry()])
    out = tmp_path / "d.json"
    code = pf.main(["--candidates", str(cands), "--plan", str(plan), "--out", str(out), "--shortlist", "2"])
    assert code == 1
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["candidates"] == 3 and summary["reject"] == 1 and summary["flag"] == 1 and summary["keep"] == 1
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["shortlists"]["tv:museum"] == ["c1", "c3"]
    assert payload["decisions"][1]["notes"]


def test_cli_clean_run_exit_zero_and_config(tmp_path, capsys):
    cands = _jsonl(tmp_path / "c.jsonl", [cand(width=500, height=400)])
    plan = _jsonl(tmp_path / "p.jsonl", [entry()])
    cfg = tmp_path / "rules.json"
    cfg.write_text(json.dumps({"resolution": {"min_short_side": 100}}), encoding="utf-8")
    assert pf.main(["--candidates", str(cands), "--plan", str(plan), "--config", str(cfg)]) == 0
    assert json.loads(capsys.readouterr().out.strip())["keep"] == 1


def test_cli_usage_errors(tmp_path, capsys):
    plan = _jsonl(tmp_path / "p.jsonl", [entry()])
    assert pf.main(["--candidates", str(tmp_path / "missing.jsonl"), "--plan", str(plan)]) == 2
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{oops\n", encoding="utf-8")
    assert pf.main(["--candidates", str(bad), "--plan", str(plan)]) == 2
    cfg = tmp_path / "cfg.json"
    cfg.write_text("[1]", encoding="utf-8")
    assert pf.main(["--candidates", str(plan), "--plan", str(plan), "--config", str(cfg)]) == 2
    assert pf.main(["--candidates", str(plan), "--plan", str(plan), "--shortlist", "0"]) == 2
