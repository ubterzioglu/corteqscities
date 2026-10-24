"""merge_package: yazar parcalarini sekmelere birlestirme + kapi kontrolleri (A6; pilot birlestir.py).

Ag yok; sentetik mini is klasoru: 2 yanit, 8 mekan (her grupta bir), 1 mahalle, adim, rota, terim, 23 sayfa alani,
Sehir satiri ve kaynak metninde gecen alintilar.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import merge_package as mp
import package_sources as ps

CITY = "testville"
BOX = "51.3,51.55,5.3,5.6"
TEXTS = {
    1: "Inwoners schrijven zich in bij de gemeente binnen vijf dagen na aankomst. De afspraak is gratis.",
    2: "Het museum is open van dinsdag tot zondag. Een ticket kost 16 euro.",
    3: "De wijk ligt dicht bij het station en heeft veel groen.",
    4: "Deze bron wordt niet gebruikt.",
}
PLACE_SLUGS = [f"yer-{i}" for i in range(8)]


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def src(n: int, city: str = CITY) -> str:
    return f"{city}:kaynak:{n:03d}"


def url(n: int) -> str:
    return f"https://bron{n}.example.org/pagina"


def entry(slug: str, order: int, source: int, city: str = CITY, **extra) -> dict:
    return {"entry_id": f"{city}:{slug}", "city_id": city, "slug": slug, "title": f"Başlık {slug}",
            "subtitle": "Kısa alt başlık", "summary": "Somut bir özet.", "keywords": "a, b", "stages": "new",
            "source_ids": src(source, city), "reviewed_on": "2026-10-22", "order": order, "featured": "Hayır",
            "editorial_status": "Taslak", **extra}


def answer(slug: str, order: int, city: str = CITY) -> dict:
    return entry(slug, order, 1, city, topic_id=f"{city}:genel", steps="Adım bir\nAdım iki", documents="Pasaport",
                 timing="Beş gün", cost="Ücretsiz", note="Randevu alın.", visual_json="")


def place(slug: str, order: int, group: str, city: str = CITY) -> dict:
    return entry(slug, order, 2, city, group=group, district="Centrum", setting="Kapalı alan", location="Straat 1",
                 latitude=51.44, longitude=5.47, visit_status="", note="Salı ücretsiz.", collection="Hayır", media_key="")


def hood(slug: str, order: int, city: str = CITY) -> dict:
    compare = json.dumps({"Ulaşım": "Tren yakın", "Yaşam ritmi": "Canlı", "Konut tipi": "Daire", "Yeşil alan": "Park"},
                         ensure_ascii=False)
    return entry(slug, order, 3, city, location="Merkez", tags="Tren", compare_json=compare, note="Bölge kartı.",
                 media_key="")


def make_sources(work: Path, city: str) -> None:
    index = []
    for n, text in TEXTS.items():
        path = work / "snap" / f"{n}.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        index.append({"source_id": src(n, city), "url": url(n), "final_url": url(n) + ("?son=1" if n == 2 else ""),
                      "text_file": str(path), "html_file": f"{n}.html"})
    write_jsonl(work / "kaynak_dizini.jsonl", index)
    write_jsonl(work / "kaynak_taslak.jsonl", [{"source_id": src(n, city), "city_id": city, "title": f"Bron {n}",
                                                "url": url(n), "checked_on": "2026-10-22", "verified": "Hayır"}
                                               for n in TEXTS])


def make_work(tmp_path: Path, city: str = CITY) -> Path:
    work = tmp_path / "is"
    make_sources(work, city)
    parts = work / "data" / "parcalar"
    answers = [answer("kayit", 1, city), answer("sigorta", 2, city)]
    places = [place(slug, 10 + i, group, city) for i, (slug, group) in enumerate(zip(PLACE_SLUGS, sorted(mp.GROUPS)))]
    hoods = [hood("merkez", 20, city)]
    write_jsonl(parts / "Yanıtlar.genel.jsonl", answers)
    write_jsonl(parts / "Mekânlar.m1.jsonl", places)
    write_jsonl(parts / "Mahalleler.mahalle.jsonl", hoods)
    write_jsonl(parts / "Bağlantılar.genel.jsonl", [
        {"action_id": f"{city}:action:{e['slug']}-1", "city_id": city, "entry_id": e["entry_id"], "label": "Bilgi al",
         "url": url(int(e["source_ids"].rsplit(":", 1)[1])), "checked_on": "2026-10-22", "order": 1}
        for e in answers + places + hoods])
    write_jsonl(parts / "Adımlar.planlama.jsonl", [
        {"step_id": f"{city}:step:1", "city_id": city, "entry_id": f"{city}:kayit", "title": "Kayıt olun",
         "when": "İlk hafta", "description": "Belediyeye gidin.", "order": 1}])
    write_jsonl(parts / "Rotalar.rota.jsonl", [
        {"route_id": f"{city}:route:001", "city_id": city, "title": "Merkez turu", "tag": "Yarım gün",
         "stops": "Yer 0\nYer 1", "stop_entry_ids": f"{city}:yer-0;{city}:yer-1", "entry_id": f"{city}:yer-0",
         "note": "Yürüyerek.", "reviewed_on": "2026-10-22", "source_ids": src(2, city), "order": 1,
         "editorial_status": "Taslak"}])
    write_jsonl(parts / "Sözlük.sozluk.jsonl", [
        {"term_id": f"{city}:term:001", "city_id": city, "term": "Gemeente", "definition": "Belediye.",
         "source_ids": src(1, city), "reviewed_on": "2026-10-22", "order": 1, "editorial_status": "Taslak"}])
    write_jsonl(parts / "SayfaAlanları.sayfa.jsonl", [
        {"field_id": f"{city}:field:{key}", "city_id": city, "key": key, "label": key, "value_type": "Metin",
         "value": "kayit" if key == "advice_entry" else "Metin", "reviewed_on": "2026-10-22"}
        for key in sorted(mp.PAGE_KEYS)])
    city_row = {k: "" for k in mp.SHEETS["Şehir"]} | {"city_id": city, "name": "Testville", "latitude": 51.43,
                                                      "longitude": 5.48}
    write_jsonl(parts / "Şehir.sayfa.jsonl", [city_row])
    write_jsonl(work / "claims" / "genel.jsonl", [
        {"claim_id": "C-1", "entry_id": f"{city}:kayit", "source_id": src(1, city), "quote": "binnen vijf  dagen na AANKOMST"},
        {"claim_id": "C-2", "entry_id": f"{city}:yer-0", "url": url(2), "quote": "Een ticket kost 16 euro."},
        {"claim_id": "C-3", "term_id": f"{city}:term:001", "source_id": src(1, city), "quote": "De afspraak is gratis."},
        {"claim_id": "C-4", "entry_id": city, "url": url(2) + "?son=1", "quote": "open van dinsdag tot zondag"},
    ])
    return work


def run(capsys, work: Path, *extra: str, city: str = CITY, bbox: str = BOX) -> tuple[int, dict]:
    out = work.parent / "out"
    code = mp.main([str(work), "--city-id", city, "--bbox", bbox, "--data-out", str(out / "data"),
                    "--out", str(out / "rapor.json"), *extra])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1  # tek satir JSON ozet
    return code, json.loads(lines[0])


def report_of(tmp_path: Path) -> dict:
    return json.loads((tmp_path / "out" / "rapor.json").read_text(encoding="utf-8"))


# ---------------------------------------------------------------- mutlu yol

def test_happy_path_merges_sheets_writes_used_sources_and_report(tmp_path, capsys):
    code, summary = run(capsys, make_work(tmp_path))
    report, data = report_of(tmp_path), tmp_path / "out" / "data"
    assert code == mp.EXIT_OK and summary["status"] == "ok", report["issues"]
    assert report["issues"] == [] and report["quote_miss_list"] == []
    assert summary["rows"] == {"Yanıtlar": 2, "Mekânlar": 8, "Mahalleler": 1, "Bağlantılar": 11, "Adımlar": 1,
                               "Rotalar": 1, "Sözlük": 1, "SayfaAlanları": 23, "Şehir": 1}
    assert (summary["claims"], summary["quote_miss"], summary["sources_used"]) == (4, 0, 3)
    assert summary["sources_claims_only"] == 0  # iddialarin kaynaklari kartlarda da var
    assert summary["per_topic"] == {"genel": 2} and summary["city_id"] == CITY
    answers = read_jsonl(data / "Yanıtlar.jsonl")
    assert [list(r) for r in answers] == [mp.SHEETS["Yanıtlar"]] * 2  # sozlesme anahtar sirasi, _part yok
    assert not (data / "Fotoğraflar.jsonl").exists()  # parcasi olmayan sekme yazilmaz
    sources = read_jsonl(data / "Kaynaklar.jsonl")
    assert [s["source_id"] for s in sources] == [src(1), src(2), src(3)]  # kullanilmayan 004 yok
    assert {s["verified"] for s in sources} == {"Evet"}


def test_default_outputs_go_to_work_data_and_report(tmp_path, capsys):
    work = make_work(tmp_path)
    code = mp.main([str(work), "--city-id", CITY, "--bbox", BOX])
    summary = json.loads(capsys.readouterr().out)
    assert code == mp.EXIT_OK and (work / "data" / "Yanıtlar.jsonl").is_file()
    assert summary["out"] == str(work / "birlestir_rapor.json") and (work / "birlestir_rapor.json").is_file()


# ---------------------------------------------------------------- parametreler (sehir sabitleri)

def test_city_id_parameter_drives_identity_checks(tmp_path, capsys):
    code, summary = run(capsys, make_work(tmp_path), city="otherville")  # veri testville
    assert code == mp.EXIT_FINDINGS
    for kind in ("entry_id", "required_or_len", "topic_or_steps", "field_id", "city_id"):
        assert kind in summary["issue_kinds"], kind


def test_bbox_parameter_controls_coordinate_range(tmp_path, capsys):
    work = make_work(tmp_path)
    path = work / "data" / "parcalar" / "Mekânlar.m1.jsonl"
    rows = read_jsonl(path)
    rows[0]["latitude"] = 52.0
    write_jsonl(path, rows)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"coord_range": 1}
    code, summary = run(capsys, work, bbox="51.3,52.5,5.3,5.6")
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {}


def test_swapped_bbox_order_is_caught_by_city_coordinate(tmp_path, capsys):
    code, summary = run(capsys, make_work(tmp_path), bbox="5.3,5.6,51.3,51.55")  # boylam/enlem sirasi karismis
    assert code == mp.EXIT_FINDINGS
    assert summary["issue_kinds"]["city_outside_bbox"] == 1 and summary["issue_kinds"]["coord_range"] == 8


# ---------------------------------------------------------------- kirma testleri

def test_fabricated_quote_unknown_owner_and_unknown_source_are_quote_misses(tmp_path, capsys):
    work = make_work(tmp_path)
    write_jsonl(work / "claims" / "uydurma.jsonl", [
        {"claim_id": "X-1", "entry_id": f"{CITY}:kayit", "source_id": src(1), "quote": "Inschrijven kost 50 euro."},
        {"claim_id": "X-2", "entry_id": f"{CITY}:yok", "source_id": src(1), "quote": "De afspraak is gratis."},
        {"claim_id": "X-3", "entry_id": f"{CITY}:kayit", "url": "https://elders.example.org/", "quote": "x"}])
    code, summary = run(capsys, work)
    misses = report_of(tmp_path)["quote_miss_list"]
    assert code == mp.EXIT_FINDINGS and summary["status"] == "findings" and summary["quote_miss"] == 3
    assert sorted(m[2] for m in misses) == ["alinti_metinde_yok", "kaynak_yok", "sahip_yok"]
    assert {m[1] for m in misses} == {"X-1", "X-2", "X-3"}


def test_missing_source_text_is_a_finding_not_a_crash(tmp_path, capsys):
    work = make_work(tmp_path)
    (work / "snap" / "1.txt").unlink()
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["quote_miss"] == 2  # C-1 ve C-3 bu kaynaga dayaniyor
    assert {m[2] for m in report_of(tmp_path)["quote_miss_list"]} == {"kaynak_metni_yok"}


def test_non_utf8_source_text_is_a_quote_miss_not_a_crash(tmp_path, capsys):
    work = make_work(tmp_path)
    (work / "snap" / "1.txt").write_bytes(TEXTS[1].replace("dagen", "dägen").encode("cp1252"))
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["quote_miss"] == 2
    assert {m[2] for m in report_of(tmp_path)["quote_miss_list"]} == {"kaynak_metni_yok"}


def test_action_urls_must_be_registered_https_non_wikipedia_sources(tmp_path, capsys):
    work = make_work(tmp_path)
    path = work / "data" / "parcalar" / "Bağlantılar.genel.jsonl"
    rows = read_jsonl(path)
    rows[0]["url"] = "https://nergens.example.org/"
    rows[1]["url"] = "https://nl.wikipedia.org/wiki/Eindhoven"
    write_jsonl(path, rows)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS
    assert summary["issue_kinds"] == {"action_url_not_in_sources": 1, "action_url": 1}


def test_source_urls_without_source_ids_are_rejected(tmp_path, capsys):
    work = make_work(tmp_path)
    path = work / "data" / "parcalar" / "Mahalleler.mahalle.jsonl"
    rows = read_jsonl(path)
    rows[0] = {**rows[0], "source_ids": "", "source_urls": "https://yeni.example.org/"}  # B6
    write_jsonl(path, rows)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS
    assert summary["issue_kinds"]["source_urls_unmapped"] == 1 and summary["issue_kinds"]["source_ids"] == 1


def test_broken_part_line_and_text_coordinate_do_not_crash(tmp_path, capsys):
    work = make_work(tmp_path)
    path = work / "data" / "parcalar" / "Mekânlar.m1.jsonl"
    rows = read_jsonl(path)
    rows[0]["longitude"] = "5.47"  # metin boylam: pilot burada TypeError ile cokuyordu
    write_jsonl(path, rows)
    with path.open("a", encoding="utf-8") as stream:
        stream.write("{bozuk\n")
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"json": 1, "coord_range": 1}


def test_placeholder_and_duplicate_step_lines_are_flagged(tmp_path, capsys):
    work = make_work(tmp_path)
    path = work / "data" / "parcalar" / "Yanıtlar.genel.jsonl"
    rows = read_jsonl(path)
    rows[0] = {**rows[0], "cost": "-", "steps": "Aynı adım\nAynı adım"}
    write_jsonl(path, rows)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"placeholder": 1, "dup_step_line": 1}


# ---------------------------------------------------------------- kural basina tek satir kirma (parametrik)

PART = {"answer": "Yanıtlar.genel.jsonl", "place": "Mekânlar.m1.jsonl", "hood": "Mahalleler.mahalle.jsonl",
        "action": "Bağlantılar.genel.jsonl", "step": "Adımlar.planlama.jsonl", "route": "Rotalar.rota.jsonl",
        "term": "Sözlük.sozluk.jsonl", "page": "SayfaAlanları.sayfa.jsonl", "city": "Şehir.sayfa.jsonl"}


def part_path(work: Path, kind: str) -> Path:
    return work / "data" / "parcalar" / PART.get(kind, kind)


def edit(kind: str, index: int = 0, **changes):
    """Tek satiri bozar: alanlari degistirir (None verilen anahtar silinir)."""
    def mutate(work: Path) -> None:
        rows = read_jsonl(part_path(work, kind))
        row = {**rows[index], **changes}
        rows[index] = {k: v for k, v in row.items() if v is not None}
        write_jsonl(part_path(work, kind), rows)
    return mutate


def edit_where(kind: str, column: str, match, **changes):
    def mutate(work: Path) -> None:
        rows = read_jsonl(part_path(work, kind))
        edit(kind, next(i for i, r in enumerate(rows) if r[column] == match), **changes)(work)
    return mutate


def append(kind: str, row: dict):
    def mutate(work: Path) -> None:
        path = part_path(work, kind)
        write_jsonl(path, (read_jsonl(path) if path.exists() else []) + [row])
    return mutate


def drop_where(kind: str, key: str, value):
    def mutate(work: Path) -> None:
        write_jsonl(part_path(work, kind), [r for r in read_jsonl(part_path(work, kind)) if r[key] != value])
    return mutate


def both(*mutations):
    def mutate(work: Path) -> None:
        for mutation in mutations:
            mutation(work)
    return mutate


def action(slug: str, number: int = 1, entry: str | None = None, **extra) -> dict:
    return {"action_id": f"{CITY}:action:{slug}-{number}", "city_id": CITY, "entry_id": entry or f"{CITY}:{slug}",
            "label": "Bilgi al", "url": url(2), "checked_on": "2026-10-22", "order": 1, **extra}


def reorder_title(work: Path) -> None:
    rows = read_jsonl(part_path(work, "place"))
    rows[0] = {**{k: v for k, v in rows[0].items() if k != "title"}, "title": rows[0]["title"]}  # sira bozuk
    write_jsonl(part_path(work, "place"), rows)


def bad_claim_line(work: Path) -> None:
    with (work / "claims" / "genel.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("{bozuk\n")


def three_featured(work: Path) -> None:
    rows = [{**r, "featured": "Evet"} for r in read_jsonl(part_path(work, "answer"))]
    write_jsonl(part_path(work, "answer"), rows + [{**answer("vize", 3), "featured": "Evet"}])
    append("action", action("vize", entry=f"{CITY}:vize", url=url(1)))(work)


FIRST_GROUP = sorted(mp.GROUPS)[0]
OTHER_KEYS = json.dumps({"A": "Bir", "B": "İki", "C": "Üç", "D": "Dört"}, ensure_ascii=False)
BREAKS = {
    "keys_extra": (edit("place", fazla="x"), {"keys": 1}),
    "keys_order": (reorder_title, {"keys": 1}),
    "keys_missing": (edit("place", media_key=None), {"keys": 1}),
    "entry_id": (edit("place", slug="baska-slug"), {"entry_id": 1}),
    "required_summary": (edit("place", summary=""), {"required_or_len": 1}),
    "required_title_len": (edit("place", title="x" * 181), {"required_or_len": 1}),
    "stages": (edit("place", stages="new;sonra"), {"stages": 1}),
    # yer-0'in iddiasi C-2 hala 002'ye dayaniyor ama kart artik onu gostermiyor: ikinci bulgu da beklenir
    "source_ids_unknown": (edit("place", source_ids=src(9)), {"source_ids": 1, "claim_source_not_in_owner": 1}),
    "source_ids_dup": (edit("place", source_ids=f"{src(2)};{src(2)}"), {"source_ids": 1}),
    "enum_featured": (edit("place", featured="Belki"), {"enum_order": 1}),
    "enum_order_text": (edit("place", order="10"), {"enum_order": 1}),
    "enum_status": (edit("place", editorial_status="Yayında"), {"editorial_status": 1}),
    "status_empty_multirow": (edit("route", editorial_status=""), {"editorial_status": 1}),  # bos hucre yazilmaz
    "delivery_json": (lambda work: (work / "data" / "Teslimat.jsonl").write_text("{bozuk\n", encoding="utf-8"),
                      {"json": 1}),
    "placeholder_note": (edit("place", note="-"), {"placeholder": 1}),
    "filler": (edit("place", note="Güncel bilgi için siteye bakın."), {"filler": 1}),
    "topic": (edit("answer", topic_id=f"{CITY}:baska"), {"topic_or_steps": 1}),
    "no_steps": (edit("answer", steps=""), {"topic_or_steps": 1}),
    "dup_step_line": (edit("answer", steps="Aynı\nAynı"), {"dup_step_line": 1}),
    "placeholder_cost": (edit("answer", cost="?"), {"placeholder": 1}),
    "visual_json": (edit("answer", visual_json="[1, 2]"), {"visual_json": 1}),
    "visual_json_text": (edit("answer", visual_json="{bozuk"), {"visual_json": 1}),
    "featured>2": (three_featured, {"featured>2": 1}),
    "place_setting": (edit("place", setting="Çatı"), {"place_enum": 1}),
    "place_district": (edit("place", district=""), {"place_enum": 1}),
    "coord_pair": (edit("place", longitude=""), {"coord_pair": 1}),
    "collection": (both(edit("place", collection="Belki"), append("place", place("yer-ek", 30, FIRST_GROUP)),
                        append("action", action("yer-ek"))), {"collection": 1}),
    "groups_without_place": (edit("place", collection="Evet"), {"groups_without_place": 1}),
    "compare_json": (edit("hood", compare_json="{}"), {"compare_json": 1}),
    "compare_json_short": (edit("hood", compare_json=json.dumps({"Ulaşım": "Tren"})), {"compare_json": 1}),
    "compare_json_text": (edit("hood", compare_json="{bozuk"), {"compare_json": 1}),
    "hood_location": (edit("hood", location=""), {"location": 1}),
    "compare_keysets": (both(append("hood", {**hood("yeni", 21), "compare_json": OTHER_KEYS}),
                             append("action", action("yeni"))), {"compare_json_keysets_differ": 1}),
    "page_key_missing": (drop_where("page", "key", "facts"), {"page_keys": 1}),
    "page_key_dup": (append("page", {"field_id": f"{CITY}:field:facts", "city_id": CITY, "key": "facts", "label": "x",
                                     "value_type": "Metin", "value": "x", "reviewed_on": "2026-10-22"}), {"page_keys": 1}),
    "page_reserved": (append("page", {"field_id": f"{CITY}:field:weather", "city_id": CITY, "key": "weather",
                                      "label": "x", "value_type": "Metin", "value": "x", "reviewed_on": "2026-10-22"}),
                      {"page_reserved": 1}),
    "field_id": (edit_where("page", "key", "facts", field_id=f"{CITY}:field:yanlis"), {"field_id": 1}),
    "page_json": (edit_where("page", "key", "facts", value_type="JSON", value="{bozuk"), {"page_json": 1}),
    "page_entry": (edit_where("page", "key", "facts", value_type="JSON", value='[{"entry": "yok"}]'),
                   {"page_entry_missing": 1}),
    "advice_entry": (edit_where("page", "key", "advice_entry", value="yok"), {"advice_entry_missing": 1}),
    "city_id": (edit("city", city_id="baska"), {"city_id": 1}),
    "city_bbox": (edit("city", latitude=60.0), {"city_outside_bbox": 1}),
    "dup_entry": (append("Mekânlar.m2.jsonl", {**place("yer-0", 40, FIRST_GROUP), "title": "Başka başlık"}),
                  {"dup_entry": 1}),
    "dup_title": (edit("place", 1, title="Başlık yer-0"), {"dup_title": 1}),
    "no_action": (drop_where("action", "entry_id", f"{CITY}:yer-0"), {"no_action": 1}),
    "action_entry": (append("action", action("yok")), {"action_entry": 1}),
    "action_id_bad": (edit("action", action_id="Kötü Kimlik"), {"action_id": 1}),
    "action_id_dup": (append("action", action("kayit", entry=f"{CITY}:yer-0")), {"action_id": 2}),
    "step_len": (edit("step", title="x" * 121), {"step": 1}),
    "step_entry": (edit("step", entry_id=f"{CITY}:yok"), {"step": 1}),
    "route_one_stop": (edit("route", stops="Yer 0", stop_entry_ids=f"{CITY}:yer-0"), {"route": 1}),
    "route_first_stop": (edit("route", entry_id=f"{CITY}:yer-1"), {"route": 1}),
    "order_dup": (append("step", {"step_id": f"{CITY}:step:2", "city_id": CITY, "entry_id": f"{CITY}:kayit",
                                  "title": "Sigorta", "when": "İlk ay", "description": "Poliçe alın.", "order": 1}),
                  {"order_dup": 1}),
    "term_source": (edit("term", source_ids=""), {"term": 1, "claim_source_not_in_owner": 1}),  # C-3 001'e dayaniyor
    "claims_json": (bad_claim_line, {"json": 1}),
}


@pytest.mark.parametrize("case", sorted(BREAKS))
def test_each_gate_rule_catches_its_single_broken_row(tmp_path, capsys, case):
    mutate, expected = BREAKS[case]
    work = make_work(tmp_path)
    mutate(work)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == expected, report_of(tmp_path)["issues"]
    assert summary["quote_miss"] == 0


def test_valid_optional_shapes_are_not_flagged(tmp_path, capsys):
    """Dallarin 'gecer' yonu: bos stages, koordinatsiz mekan, gecerli visual_json, JSON sayfa alaninda liste disi
    deger, sozluk olmayan oge ve entry'siz oge."""
    work = make_work(tmp_path)
    both(edit("place", stages="", latitude="", longitude=""),
         edit("answer", featured="Evet",
              visual_json='{"kind": "steps", "items": [{"label": "Adım bir"}, {"label": "Adım iki"}]}'),
         edit_where("page", "key", "facts", value_type="JSON", value='[{"entry": "kayit"}, "metin", {"label": "x"}]'),
         edit_where("page", "key", "timeline", value_type="JSON", value='{"adim": 1}'))(work)
    with (work / "kaynak_dizini.jsonl").open("a", encoding="utf-8") as stream:  # adressiz (kullanilmayan) kaynak
        stream.write(json.dumps({"source_id": src(5), "url": None, "text_file": ""}) + "\n")
    with part_path(work, "hood").open("a", encoding="utf-8") as stream:
        stream.write("\n   \n")  # bos satirlar atlanir
    code, summary = run(capsys, work)
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {}, report_of(tmp_path)["issues"]


def test_sheet_without_parts_is_left_to_template(tmp_path, capsys):
    work = make_work(tmp_path)
    part_path(work, "page").unlink()
    code, summary = run(capsys, work)
    assert code == mp.EXIT_OK and "SayfaAlanları" not in summary["rows"]
    assert not (tmp_path / "out" / "data" / "SayfaAlanları.jsonl").exists()


def test_unexpected_value_types_are_findings_not_crashes(tmp_path, capsys):
    work = make_work(tmp_path)
    edit("place", group=["Müzeler"])(work)  # liste: hashlenemez, kume anahtari JSON metni olur
    code, summary = run(capsys, work)
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"place_enum": 1, "groups_without_place": 1}


# ---------------------------------------------------------------- AI kendi isini onaylamaz (K97, S4)

PENDING = "Bekliyor"


def photo_parts(work: Path, city: str = CITY) -> Path:
    """photo_rows bicimli tek karelik Fotoğraflar + Kanıtlar parcalari (onay alanlari bekleyen degerde)."""
    photo = {k: "" for k in mp.SHEETS["Fotoğraflar"]} | {
        "photo_id": f"{city}:photo:yer-0-01", "city_id": city, "role": "Mekân", "entry_id": f"{city}:yer-0",
        "evidence_id": f"{city}:evidence:yer-0-01", "order": 1, "editorial_status": "Taslak"}
    evidence = {k: "" for k in mp.SHEETS["Kanıtlar"]} | {
        "evidence_id": f"{city}:evidence:yer-0-01", "city_id": city, "photo_id": f"{city}:photo:yer-0-01",
        "metadata_review_status": PENDING, "pixel_review_status": PENDING, "rights_status": PENDING}
    write_jsonl(work / "data" / "parcalar" / "Fotoğraflar.foto.jsonl", [photo])
    write_jsonl(work / "data" / "parcalar" / "Kanıtlar.foto.jsonl", [evidence])
    return work


SELF_APPROVALS = [  # (sekme, parca dosyasi, alan, AI'in yazamayacagi deger)
    ("Yanıtlar", "Yanıtlar.genel.jsonl", "editorial_status", "Onaylandı"),
    ("Mekânlar", "Mekânlar.m1.jsonl", "editorial_status", "Onaylandı"),
    ("Mahalleler", "Mahalleler.mahalle.jsonl", "editorial_status", "Onaylandı"),
    ("Rotalar", "Rotalar.rota.jsonl", "editorial_status", "Onaylandı"),
    ("Sözlük", "Sözlük.sozluk.jsonl", "editorial_status", "Düzeltme"),
    ("Fotoğraflar", "Fotoğraflar.foto.jsonl", "editorial_status", "Onaylandı"),
    ("Şehir", "Şehir.sayfa.jsonl", "editorial_status", "Onaylandı"),
    ("Kanıtlar", "Kanıtlar.foto.jsonl", "metadata_review_status", "Doğrulandı"),
    ("Kanıtlar", "Kanıtlar.foto.jsonl", "pixel_review_status", "Doğrulandı"),
    ("Kanıtlar", "Kanıtlar.foto.jsonl", "rights_status", "Bu kare için uygun"),
]


@pytest.mark.parametrize("sheet, name, field, value", SELF_APPROVALS,
                         ids=[f"{sheet}-{field}" for sheet, _, field, _ in SELF_APPROVALS])
def test_ai_self_approval_is_flagged_on_every_sheet_that_carries_the_field(tmp_path, capsys, sheet, name, field,
                                                                          value):
    """Onay alani tasiyan her sekmede bozulan satir adiyla bildirilir: [alan, sekme, parca, kimlik, deger].
    Once yalniz Yanıtlar/Mekânlar/Mahalleler'e bakiliyordu; Rotalar/Sözlük/Fotoğraflar/Şehir hicbir kapida
    yakalanmiyordu (S4), Kanıtlar'i yalniz build_xlsx yakaliyordu."""
    work = photo_parts(make_work(tmp_path))
    path = part_path(work, name)
    rows = read_jsonl(path)
    row_id = rows[0][mp.SHEETS[sheet][0]]
    write_jsonl(path, [{**rows[0], field: value}, *rows[1:]])
    code, summary = run(capsys, work)
    issues = report_of(tmp_path)["issues"]
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {field: 1}, issues
    assert [field, sheet, name.split(".")[1], row_id, value] in issues


def test_pending_values_and_cells_left_to_build_are_not_approvals(tmp_path, capsys):
    """Gecen yon: 'Taslak' / 'Bekliyor'; bos inceleme alani (build_xlsx 'Bekliyor' yazar); tek satirlik Şehir'de bos
    editorial_status (build_xlsx bos hucreyi yazmaz, sablondaki deger kalir)."""
    work = photo_parts(make_work(tmp_path))
    edit("Kanıtlar.foto.jsonl", pixel_review_status="", rights_status="")(work)
    edit("city", editorial_status="")(work)
    code, summary = run(capsys, work)
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {}, report_of(tmp_path)["issues"]
    assert (summary["rows"]["Fotoğraflar"], summary["rows"]["Kanıtlar"]) == (1, 1)


def delivery(**changes) -> dict:
    """Teslimat satiri: SKILL.md'ye gore parcadan degil dogrudan <is>/data/Teslimat.jsonl'e yazilir."""
    return {"schema_version": "1.0", "delivery_id": "city-901-v001", "city_id": CITY, "editor": "Atınç",
            "reviewer": "", "scope": "Tam teslim", "updated_on": "2026-10-22", "editorial_status": "Taslak",
            "notes": "YEREL DENEME - Drive'a yüklenmedi"} | changes


def test_delivery_row_in_data_is_checked_for_approval_but_never_rewritten(tmp_path, capsys):
    """Teslimat'ta da insan onayi alanlari var (editorial_status, reviewer: AI icin bos). merge_package dosyayi
    birlestirmez ve yazmaz (varsayilan --data-out <is>/data iken de); yalniz onay alanlarini denetler."""
    work = make_work(tmp_path)
    direct = write_jsonl(work / "data" / "Teslimat.jsonl", [delivery()])
    code, summary = run(capsys, work)
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {} and "Teslimat" not in summary["rows"]
    assert not (tmp_path / "out" / "data" / "Teslimat.jsonl").exists()
    write_jsonl(direct, [delivery(reviewer="Claude", editorial_status="Onaylandı")])
    before = direct.read_bytes()
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_FINDINGS
    capsys.readouterr()
    issues = json.loads((work / mp.REPORT_NAME).read_text(encoding="utf-8"))["issues"]
    assert direct.read_bytes() == before
    assert ["editorial_status", "Teslimat", "data", "city-901-v001", "Onaylandı"] in issues
    assert ["reviewer", "Teslimat", "data", "city-901-v001", "Claude"] in issues
    assert sorted(i[0] for i in issues) == ["editorial_status", "reviewer"]


# ---------------------------------------------------------------- iddia kaynaklari da kullanilan kaynak (S4)

PAGE_CLAIMS = [  # SayfaAlanları'nin source_ids sutunu yok: sayfa/Şehir metnini kaynagina yalniz iddia defteri baglar
    {"claim_id": "S-1", "field_id": f"{CITY}:field:facts", "source_id": src(4),
     "quote": "Deze bron wordt niet gebruikt."},
    {"claim_id": "S-2", "entry_id": CITY, "url": url(4), "quote": "wordt niet gebruikt"}]


def test_source_cited_only_by_page_or_city_claims_is_a_used_source(tmp_path, capsys):
    """Kart/rota/terim source_ids'inde ve baglantilarda olmayan, yalniz iddialarin dayandigi kaynak da Kaynaklar'a
    (verified=Evet) girer; ozet bunlari ayrica sayar, rapor listeler."""
    work = make_work(tmp_path)
    write_jsonl(work / "claims" / "sayfa.jsonl", PAGE_CLAIMS)
    code, summary = run(capsys, work)
    sources = read_jsonl(tmp_path / "out" / "data" / "Kaynaklar.jsonl")
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {} and summary["quote_miss"] == 0
    assert [s["source_id"] for s in sources] == [src(1), src(2), src(3), src(4)]
    assert {s["verified"] for s in sources} == {"Evet"}
    assert (summary["sources_used"], summary["sources_claims_only"]) == (4, 1)
    assert report_of(tmp_path)["claims_only_sources"] == [src(4)]


def test_only_claims_of_package_content_make_their_source_used(tmp_path, capsys):
    """Sahipsiz iddia (silinmis kart) kaynagini kullanilmis saydirmaz. Icerigin iddiasi alintisi tutmasa da kaynagini
    gosterir; alinti eksigi ayri bulgudur."""
    work = make_work(tmp_path)
    claims = work / "claims" / "sayfa.jsonl"
    write_jsonl(claims, [{"claim_id": "S-9", "field_id": f"{CITY}:field:yok", "source_id": src(4),
                          "quote": "wordt niet gebruikt"}])
    code, summary = run(capsys, work)
    kept = [s["source_id"] for s in read_jsonl(tmp_path / "out" / "data" / "Kaynaklar.jsonl")]
    assert code == mp.EXIT_FINDINGS and summary["quote_miss"] == 1 and src(4) not in kept
    assert (summary["sources_used"], summary["sources_claims_only"]) == (3, 0)
    write_jsonl(claims, [{"claim_id": "S-8", "field_id": f"{CITY}:field:facts", "source_id": src(4),
                          "quote": "Uydurma bir cümle."}])
    code, summary = run(capsys, work)
    misses = report_of(tmp_path)["quote_miss_list"]
    assert code == mp.EXIT_FINDINGS and [m[1:] for m in misses] == [["S-8", "alinti_metinde_yok"]]
    assert (summary["sources_used"], summary["sources_claims_only"]) == (4, 1)


def test_used_source_missing_from_draft_is_flagged_not_silently_dropped(tmp_path, capsys):
    """Kaynaklar satirlari kaynak_taslak'tan gelir: taslakta satiri olmayan kullanilan kaynak eskiden sessizce
    dusuyordu (kart source_ids'i Kaynaklar'da olmayan kaynagi gosterir, iddia kaynagi pakete girmez)."""
    work = make_work(tmp_path)
    write_jsonl(work / "claims" / "sayfa.jsonl", PAGE_CLAIMS)
    draft = read_jsonl(work / "kaynak_taslak.jsonl")
    write_jsonl(work / "kaynak_taslak.jsonl", [r for r in draft if r["source_id"] not in (src(3), src(4))])
    code, summary = run(capsys, work)
    issues = report_of(tmp_path)["issues"]
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"source_not_in_draft": 2}, issues
    assert ["source_not_in_draft", src(3)] in issues and ["source_not_in_draft", src(4)] in issues


def test_source_cited_only_by_claims_reaches_the_package(tmp_path, capsys):
    """Uctan uca, varsayilan yollarla: merge_package -> package_sources; iddia kaynaginin kopyasi pakete girer."""
    work = make_work(tmp_path)
    pages = {n: f"<html><body>{text}</body></html>" for n, text in TEXTS.items()}
    for n, page in pages.items():
        (work / "snap" / f"{n}.html").write_text(page, encoding="utf-8")
    write_jsonl(work / "claims" / "sayfa.jsonl", PAGE_CLAIMS)
    package = tmp_path / "paket"
    package.mkdir()
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_OK
    assert ps.main([str(work), str(package)]) == ps.EXIT_OK
    capsys.readouterr()
    rows = {r["source_id"]: r for r in read_jsonl(work / "data" / "Kaynaklar.jsonl")}
    assert sorted(rows) == [src(n) for n in sorted(TEXTS)]
    assert (package / rows[src(4)]["snapshot_file"]).read_text(encoding="utf-8") == pages[4]


# ---------------------------------------------------------------- iddianin kaynagi sahibinin source_ids'inde olmali

QUOTES = {1: "De afspraak is gratis.", 2: "Een ticket kost 16 euro.", 3: "dicht bij het station",
          4: "wordt niet gebruikt"}
FOREIGN_CLAIMS = {  # (sahip anahtari, sahip, kaynak no, iddiada kaynagi gosteren alan): kaynak sahibin source_ids'inde
    # yok
    "kart": ("entry_id", f"{CITY}:kayit", 4, "source_id"),
    "kart_adresle": ("entry_id", f"{CITY}:merkez", 4, "url"),
    "kart_baska_kartin_kaynagi": ("entry_id", f"{CITY}:yer-0", 1, "source_id"),
    "rota": ("route_id", f"{CITY}:route:001", 4, "source_id"),
    "terim": ("term_id", f"{CITY}:term:001", 4, "source_id"),
}


def ledger_claim(claim_id: str, key: str, owner: str, n: int, ref: str = "source_id") -> dict:
    return {"claim_id": claim_id, key: owner, ref: src(n) if ref == "source_id" else url(n), "quote": QUOTES[n]}


@pytest.mark.parametrize("case", sorted(FOREIGN_CLAIMS))
def test_claim_backed_by_source_missing_from_owner_source_ids_is_flagged(tmp_path, capsys, case):
    """Kart/rota/terim iddiasi kendi source_ids'inde olmayan kaynaga dayaniyorsa web karti o kaynagi gostermez
    (kaynaklari source_ids'ten gosterir). Eskiden kaynak sessizce 'yalniz iddiadan gelen' sayilir, cikis 0 olurdu.
    Artik bulgu: [claim_source_not_in_owner, iddia dosyasi, claim_id, sahip, kaynak]. Kaynak yine kullanilan sayilir
    (pakete girer). SayfaAlanları/Şehir iddialari (source_ids sutunu yok) bu kuralin disinda: bkz.
    test_source_cited_only_by_page_or_city_claims_is_a_used_source."""
    key, owner, n, ref = FOREIGN_CLAIMS[case]
    work = make_work(tmp_path)
    write_jsonl(work / "claims" / "ek.jsonl", [ledger_claim("E-1", key, owner, n, ref)])
    code, summary = run(capsys, work)
    issues = report_of(tmp_path)["issues"]
    assert code == mp.EXIT_FINDINGS and summary["issue_kinds"] == {"claim_source_not_in_owner": 1}, issues
    assert issues == [["claim_source_not_in_owner", "ek.jsonl", "E-1", owner, src(n)]]
    assert summary["quote_miss"] == 0
    assert src(n) in [s["source_id"] for s in read_jsonl(tmp_path / "out" / "data" / "Kaynaklar.jsonl")]


def test_claims_backed_by_their_owners_own_sources_are_not_flagged(tmp_path, capsys):
    """Gecen yon: rota ve mahalle iddiasi kendi source_ids'indeki kaynaga dayaniyor (kimlikle ya da yalniz adresle);
    birden cok kaynakli kartta herhangi biri yeter."""
    work = make_work(tmp_path)
    edit("answer", source_ids=f"{src(1)};{src(4)}")(work)
    write_jsonl(work / "claims" / "ek.jsonl", [
        ledger_claim("E-2", "route_id", f"{CITY}:route:001", 2),
        ledger_claim("E-3", "entry_id", f"{CITY}:merkez", 3, "url"),
        ledger_claim("E-4", "entry_id", f"{CITY}:kayit", 4)])
    code, summary = run(capsys, work)
    assert code == mp.EXIT_OK and summary["issue_kinds"] == {}, report_of(tmp_path)["issues"]
    assert (summary["claims"], summary["quote_miss"], summary["sources_claims_only"]) == (7, 0, 0)


# ---------------------------------------------------------------- kullanim hatalari

@pytest.mark.parametrize("bbox", ["51.3,51.55,5.3", "51.55,51.3,5.3,5.6", "a,b,c,d", "95,96,5.3,5.6", "nan,51.5,5.3,5.6"])
def test_invalid_bbox_is_usage_error(tmp_path, capsys, bbox):
    assert mp.main([str(make_work(tmp_path)), "--city-id", CITY, "--bbox", bbox]) == mp.EXIT_USAGE


def test_usage_errors_exit_2(tmp_path, capsys):
    work = make_work(tmp_path)
    assert mp.main([str(work), "--city-id", "Bad City", "--bbox", BOX]) == mp.EXIT_USAGE
    assert mp.main([str(tmp_path / "yok"), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_USAGE
    assert mp.main([str(work), "--city-id", CITY]) == mp.EXIT_USAGE  # --bbox zorunlu
    (work / "kaynak_dizini.jsonl").write_text("{bozuk\n", encoding="utf-8")
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_USAGE
    (work / "kaynak_dizini.jsonl").unlink()
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_USAGE
    write_jsonl(work / "kaynak_dizini.jsonl", [{"url": url(1)}])  # source_id yok
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_USAGE
    other = tmp_path / "parcasiz"
    other.mkdir()
    assert mp.main([str(other), "--city-id", CITY, "--bbox", BOX]) == mp.EXIT_USAGE  # data/parcalar yok
    assert mp.main(["--help"]) == mp.EXIT_OK


@pytest.mark.parametrize("name", ["data/parcalar/Mekânlar.m1.jsonl", "claims/genel.jsonl", "kaynak_taslak.jsonl",
                                  "data/Teslimat.jsonl"])
def test_non_utf8_input_is_usage_error_not_finding(tmp_path, capsys, name):
    """UnicodeDecodeError main disina kacinca Python cikisi 1 oluyordu ('bulgu' ile karisir); cikti yazilmamali.
    data/Teslimat.jsonl istege bagli girdi (make_work yazmaz): once gecerli satiriyla olusturulur."""
    work = make_work(tmp_path)
    path = work / name
    if not path.exists():
        write_jsonl(path, [delivery()])
    path.write_bytes(path.read_bytes() + '{"note": "Müze"}\n'.encode("cp1252"))
    out = tmp_path / "out"
    code = mp.main([str(work), "--city-id", CITY, "--bbox", BOX, "--data-out", str(out / "data"),
                    "--out", str(out / "rapor.json")])
    captured = capsys.readouterr()
    assert code == mp.EXIT_USAGE and f"{path.name}: UTF-8 degil" in captured.err and captured.out == ""
    assert not out.exists()


def test_unwritable_outputs_are_usage_errors(tmp_path, capsys):
    work = make_work(tmp_path)
    blocker = tmp_path / "dosya"
    blocker.write_text("klasor degil", encoding="utf-8")
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX, "--data-out", str(blocker)]) == mp.EXIT_USAGE
    folder = tmp_path / "rapor_klasoru"
    folder.mkdir()
    assert mp.main([str(work), "--city-id", CITY, "--bbox", BOX, "--data-out", str(tmp_path / "d"),
                    "--out", str(folder)]) == mp.EXIT_USAGE
    assert "HATA" in capsys.readouterr().err
