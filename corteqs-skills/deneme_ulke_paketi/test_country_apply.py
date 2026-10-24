"""country_apply: ulke paketinin sehir-notr kartlarini sehrin is klasorune uygular (SKILL 'country' fazi, plan C).

Ag yok: kaynak kopyalari paketten yerel olarak alinir.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toolkit" / "scripts"))  # ortak araclar (deneme: toolkit'e dosya eklenmez)

import json
from pathlib import Path

import pytest

import country_apply as ca

TODAY = "2026-10-24"
HASH_PLACEHOLDER = "x"


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def card(slug: str, topic: str = "resmi", sources: str = "es:kaynak:001", **extra) -> dict:
    return {"entry_id": f"es:{slug}", "city_id": "es", "slug": slug, "title": f"{{sehir}}'de {slug} nasıl yapılır?",
            "summary": "Ulusal kural; {sehir} için de geçerli.", "source_ids": sources, "order": 1,
            "topic_id": f"es:{topic}", "reviewed_on": "2026-10-01", **extra}


def claim(slug: str, n: int = 1, source: str = "es:kaynak:001") -> dict:
    return {"claim_id": f"C-{slug}-{n}", "entry_id": f"es:{slug}", "field": "body", "claim": "ücret 10 euro",
            "value": "10", "unit": "EUR", "period": "2026", "source_id": source,
            "url": "https://boe.example.es/a", "quote": "diez euros"}


def action(slug: str) -> dict:
    return {"action_id": f"es:action:{slug}-1", "city_id": "es", "entry_id": f"es:{slug}", "label": "Bilgi al",
            "url": "https://boe.example.es/a", "checked_on": "2026-10-01", "order": 1}


def source_row(number: int, url: str) -> dict:
    sid = f"es:kaynak:{number:03d}"
    return {"source_id": sid, "topic": "resmi", "url": url, "final_url": url, "title": f"Kaynak {number}",
            "publisher": "BOE", "lang": "es", "text_file": f"kaynaklar/{number:03d}.txt", "text_chars": 40,
            "html_file": f"kaynaklar/{number:03d}.html", "html_sha256": "ab" * 32, "why": "resmi"}


def make_pack(tmp_path: Path, valid_until: dict[str, str | None] | None = None) -> Path:
    pack = tmp_path / "ulke" / "ES"
    cards = [card("nie-basvurusu", sources="es:kaynak:001;es:kaynak:002"), card("smi", topic="is", sources="es:kaynak:002")]
    claims = [claim("nie-basvurusu"), claim("nie-basvurusu", 2, "es:kaynak:002"), claim("smi", 1, "es:kaynak:002")]
    write_jsonl(pack / "Yanıtlar.ulusal.jsonl", cards)
    write_jsonl(pack / "Bağlantılar.ulusal.jsonl", [action("nie-basvurusu"), action("smi")])
    write_jsonl(pack / "claims" / "ulusal.jsonl", claims)
    write_jsonl(pack / "kaynak_dizini.jsonl", [source_row(1, "https://boe.example.es/a"),
                                               source_row(2, "https://sepe.example.es/b")])
    for number in (1, 2):
        (pack / "kaynaklar").mkdir(exist_ok=True)
        (pack / "kaynaklar" / f"{number:03d}.txt").write_text(f"metin {number}", encoding="utf-8")
        (pack / "kaynaklar" / f"{number:03d}.html").write_text(f"<p>{number}</p>", encoding="utf-8")
    until = valid_until or {}
    meta = {"country": "ES", "version": 3, "built": "2026-10-01",
            "cards": {c["slug"]: {"sha256": ca.card_hash(c, [x for x in claims if x["entry_id"] == c["entry_id"]]),
                                  "valid_until": until.get(c["slug"])} for c in cards}}
    (pack / "pack.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return pack


def make_work(tmp_path: Path, existing=()) -> Path:
    work = tmp_path / "is"
    work.mkdir()
    write_jsonl(work / "kaynak_dizini.jsonl", [{"source_id": sid, "url": url, "topic": "kesif"} for sid, url in existing])
    write_jsonl(work / "kaynak_taslak.jsonl", [{"source_id": sid, "url": url} for sid, url in existing])
    return work


def apply(work: Path, pack: Path, **overrides) -> dict:
    args = {"work": work, "pack": pack, "city_id": "sevilla", "city_name": "Sevilla", "order_start": 7000,
            "today": TODAY}
    return ca.apply_pack(**{**args, **overrides})


def test_copies_cards_and_rebuilds_identity(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    summary = apply(work, pack)
    assert summary["copied"] == 2 and summary["stale"] == []
    resmi = read_jsonl(work / "data" / "parcalar" / "Yanıtlar.resmi.jsonl")
    assert len(resmi) == 1
    row = resmi[0]
    assert row["entry_id"] == "sevilla:nie-basvurusu" and row["city_id"] == "sevilla"
    assert row["topic_id"] == "sevilla:resmi" and row["slug"] == "nie-basvurusu"
    assert row["title"] == "Sevilla'de nie-basvurusu nasıl yapılır?" and "{sehir}" not in row["summary"]
    orders = sorted(r["order"] for p in (work / "data" / "parcalar").glob("Yanıtlar.*.jsonl") for r in read_jsonl(p))
    assert orders == [7000, 7001]


def test_sources_are_copied_locally_and_renumbered(tmp_path):
    pack = make_pack(tmp_path)
    work = make_work(tmp_path, existing=[("sevilla:kaynak:007", "https://old.example.org/x")])
    summary = apply(work, pack)
    assert summary["sources_added"] == 2
    index = read_jsonl(work / "kaynak_dizini.jsonl")
    assert [r["source_id"] for r in index] == ["sevilla:kaynak:007", "sevilla:kaynak:008", "sevilla:kaynak:009"]
    assert len(read_jsonl(work / "kaynak_taslak.jsonl")) == 3
    row = read_jsonl(work / "data" / "parcalar" / "Yanıtlar.resmi.jsonl")[0]
    assert row["source_ids"] == "sevilla:kaynak:008;sevilla:kaynak:009"
    claims = read_jsonl(work / "claims" / "resmi.jsonl")
    assert {c["source_id"] for c in claims} == {"sevilla:kaynak:008", "sevilla:kaynak:009"}
    assert all(c["entry_id"] == "sevilla:nie-basvurusu" for c in claims)
    assert len({c["claim_id"] for c in claims}) == len(claims)
    copied = list((work / "snap_ulke_es").glob("*.txt"))
    assert len(copied) == 2


def test_existing_source_url_reuses_its_id(tmp_path):
    pack = make_pack(tmp_path)
    work = make_work(tmp_path, existing=[("sevilla:kaynak:003", "https://boe.example.es/a")])
    summary = apply(work, pack)
    assert summary["sources_added"] == 1 and summary["sources_reused"] == 1
    row = read_jsonl(work / "data" / "parcalar" / "Yanıtlar.resmi.jsonl")[0]
    assert row["source_ids"] == "sevilla:kaynak:003;sevilla:kaynak:004"


def test_action_url_source_outside_card_sources_is_copied(tmp_path):
    pack = make_pack(tmp_path)
    write_jsonl(pack / "kaynak_dizini.jsonl", read_jsonl(pack / "kaynak_dizini.jsonl")
                + [source_row(3, "https://dgt.example.es/canje")])
    for ext in ("txt", "html"):
        (pack / "kaynaklar" / f"003.{ext}").write_text("3", encoding="utf-8")
    extra = {**action("smi"), "action_id": "es:action:smi-2", "url": "https://dgt.example.es/canje"}
    write_jsonl(pack / "Bağlantılar.ulusal.jsonl", read_jsonl(pack / "Bağlantılar.ulusal.jsonl") + [extra])
    work = make_work(tmp_path)
    assert apply(work, pack)["sources_added"] == 3
    assert "https://dgt.example.es/canje" in {r["url"] for r in read_jsonl(work / "kaynak_dizini.jsonl")}
    row = read_jsonl(work / "data" / "parcalar" / "Yanıtlar.is.jsonl")[0]
    assert row["source_ids"] == "sevilla:kaynak:002"


def test_actions_are_rebuilt(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    actions = read_jsonl(work / "data" / "parcalar" / "Bağlantılar.resmi.jsonl")
    assert actions[0]["action_id"] == "sevilla:action:nie-basvurusu-1"
    assert actions[0]["entry_id"] == "sevilla:nie-basvurusu" and actions[0]["city_id"] == "sevilla"


def test_expired_card_is_stale_and_not_copied(tmp_path):
    pack = make_pack(tmp_path, valid_until={"smi": "2026-10-01", "nie-basvurusu": "2027-01-01"})
    work = make_work(tmp_path)
    summary = apply(work, pack)
    assert summary["copied"] == 1 and summary["stale"] == ["smi"]
    assert not (work / "data" / "parcalar" / "Yanıtlar.is.jsonl").exists()
    # kopyalanmayan kartin kaynagi (yalniz o kartta kullanilan) sehre alinmaz
    assert summary["sources_added"] == 2  # kaynak 2 baska karta da bagli


def test_valid_until_today_is_still_valid(tmp_path):
    pack = make_pack(tmp_path, valid_until={"smi": TODAY})
    assert apply(make_work(tmp_path), pack)["stale"] == []


def test_tampered_pack_card_is_rejected(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    path = pack / "Yanıtlar.ulusal.jsonl"
    rows = read_jsonl(path)
    rows[0]["summary"] = "sessizce değişti"
    write_jsonl(path, rows)
    with pytest.raises(ca.UsageError, match="nie-basvurusu"):
        apply(work, pack)


def test_unknown_source_id_is_an_error(tmp_path):
    pack = make_pack(tmp_path)
    path = pack / "kaynak_dizini.jsonl"
    write_jsonl(path, read_jsonl(path)[:1])
    with pytest.raises(ca.UsageError, match="es:kaynak:002"):
        apply(make_work(tmp_path), pack)


def test_refuses_to_overwrite_existing_city_files(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    with pytest.raises(ca.UsageError, match="zaten var"):
        apply(work, pack)


def test_register_file_records_origin(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    rows = {r["entry_id"]: r for r in read_jsonl(work / "ulke_kart_kaydi.jsonl")}
    assert set(rows) == {"sevilla:nie-basvurusu", "sevilla:smi"}
    one = rows["sevilla:nie-basvurusu"]
    assert one["pack_slug"] == "nie-basvurusu" and one["pack_version"] == 3 and one["country"] == "ES"
    assert len(one["pack_sha256"]) == 64 and len(one["city_sha256"]) == 64


def test_unchanged_cards_skip_claim_audit(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    report = ca.audit_scope(work, pack, today=TODAY)
    assert sorted(report["skip"]) == ["sevilla:nie-basvurusu", "sevilla:smi"] and report["audit"] == {}


def test_edited_city_card_goes_to_audit(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    path = work / "data" / "parcalar" / "Yanıtlar.resmi.jsonl"
    rows = read_jsonl(path)
    rows[0]["summary"] += " Sevilla'da Cartuja ofisine git."
    write_jsonl(path, rows)
    report = ca.audit_scope(work, pack, today=TODAY)
    assert report["audit"] == {"sevilla:nie-basvurusu": "şehirde değişti"}
    assert report["skip"] == ["sevilla:smi"]


def test_city_writer_appending_keeps_skip_but_deleting_is_caught(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    path = work / "data" / "parcalar" / "Yanıtlar.resmi.jsonl"
    city_card = {**read_jsonl(path)[0], "entry_id": "sevilla:empadronamiento-ofisi", "slug": "empadronamiento-ofisi"}
    write_jsonl(path, read_jsonl(path) + [city_card])  # sehir yazari sona ekler
    report = ca.audit_scope(work, pack, today=TODAY)
    assert report["audit"] == {} and sorted(report["skip"]) == ["sevilla:nie-basvurusu", "sevilla:smi"]
    write_jsonl(path, [city_card])  # sehir yazari dosyayi bastan yazar, ulke karti kaybolur
    report = ca.audit_scope(work, pack, today=TODAY)
    assert report["audit"] == {"sevilla:nie-basvurusu": "kart şehirde yok"}


def test_edited_claim_goes_to_audit(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    path = work / "claims" / "is.jsonl"
    rows = read_jsonl(path)
    rows[0]["value"] = "11"
    write_jsonl(path, rows)
    assert ca.audit_scope(work, pack, today=TODAY)["audit"] == {"sevilla:smi": "şehirde değişti"}


def test_card_expired_since_copy_goes_to_audit(tmp_path):
    pack, work = make_pack(tmp_path, valid_until={"smi": "2026-12-31"}), make_work(tmp_path)
    apply(work, pack)
    report = ca.audit_scope(work, pack, today="2027-01-02")
    assert report["audit"] == {"sevilla:smi": "valid_until geçti (2026-12-31)"}


def test_pack_card_revised_after_copy_goes_to_audit(tmp_path):
    pack, work = make_pack(tmp_path), make_work(tmp_path)
    apply(work, pack)
    meta_path = pack / "pack.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["cards"]["smi"]["sha256"] = "0" * 64
    meta["version"] = 4
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    assert ca.audit_scope(work, pack, today=TODAY)["audit"] == {"sevilla:smi": "paket kartı sonradan değişti"}


def test_card_hash_ignores_identity_fields():
    a, b = card("x"), {**card("x"), "entry_id": "k:x", "city_id": "k", "order": 99, "source_ids": "k:kaynak:009"}
    assert ca.card_hash(a, [claim("x")]) == ca.card_hash(b, [{**claim("x"), "claim_id": "Z", "source_id": "k:kaynak:9"}])
    assert ca.card_hash(a, []) != ca.card_hash({**a, "summary": "başka"}, [])
