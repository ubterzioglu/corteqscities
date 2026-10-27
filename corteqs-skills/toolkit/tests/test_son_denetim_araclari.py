"""Son tam denetim araclari: denetim_girdi, kaynak_kullanim, foto_denetim_girdi (Sevilla 26.10.2026 son denetimi)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import denetim_girdi as dg  # noqa: E402
import foto_denetim_girdi as fg  # noqa: E402
import kaynak_kullanim as kk  # noqa: E402


def _jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


@pytest.fixture()
def work(tmp_path: Path) -> Path:
    w = tmp_path / "_is"
    p = w / "data" / "parcalar"
    _jsonl(w / "kaynak_dizini.jsonl", [
        {"source_id": "t:kaynak:001", "url": "https://a.example/1", "publisher": "A", "text_file": "a.txt"},
        {"source_id": "t:kaynak:002", "url": "https://a.example/2", "publisher": "B", "text_file": "b.txt"},
        {"source_id": "t:kaynak:003", "url": "https://a.example/3", "publisher": "C", "text_file": ""},
        {"source_id": "t:kaynak:004", "url": "https://a.example/4", "publisher": "D", "text_file": "d.txt"}])
    _jsonl(p / "Yanıtlar.resmi.jsonl", [{"entry_id": "t:y1", "title": "Bir", "source_ids": "t:kaynak:001"},
                                       {"entry_id": "t:y2", "title": "İki", "source_ids": "t:kaynak:002"}])
    _jsonl(p / "Adımlar.resmi.jsonl", [{"step_id": "t:step:1", "entry_id": "t:y1", "title": "Başvur"}])
    _jsonl(p / "Bağlantılar.resmi.jsonl", [{"action_id": "t:action:y1-1", "entry_id": "t:y1", "url": "https://a.example/4"}])
    _jsonl(p / "Mekânlar.mekan1.jsonl", [{"entry_id": "t:m1", "title": "Müze", "source_ids": "t:kaynak:003", "latitude": 1, "longitude": 2},
                                        {"entry_id": "t:m2", "title": "Köprü", "source_ids": "t:kaynak:001"}])
    _jsonl(p / "Rotalar.rota.jsonl", [{"route_id": "t:route:001", "stop_entry_ids": "t:m1\nt:m2", "source_ids": "t:kaynak:001"}])
    _jsonl(p / "Sözlük.sozluk.jsonl", [{"term_id": "t:term:001", "term": "NIE", "source_ids": "t:kaynak:002"}])
    _jsonl(w / "claims" / "resmi.jsonl", [{"claim_id": "C-1", "entry_id": "t:y1", "claim": "x", "source_id": "t:kaynak:001", "quote": "q"}])
    _jsonl(w / "claims" / "sozluk.jsonl", [{"claim_id": "C-T1", "term_id": "t:term:001", "claim": "t", "source_id": "t:kaynak:002"}])
    _jsonl(w / "rota_plan.jsonl", [{"route_id": "t:route:001", "durak": "Müze", "acik_mi": "evet"}])
    _jsonl(w / "rota_mesafe.jsonl", [{"route_id": "t:route:001", "bacak": 1, "yuruyus_m": 500}])
    return w


def _out(capsys) -> dict:
    return json.loads(capsys.readouterr().out.strip().splitlines()[-1])


def test_denetim_girdi_writes_parts_with_sources_claims_and_extras(work, capsys):
    code = dg.main([str(work), "--city-id", "t"])
    s = _out(capsys)
    assert s["parca"] == 4 and s["kayit"] == 6 and s["metinsiz_kaynak"] == ["t:kaynak:003"] and code == 1
    rows = {r["entry_id"]: r for r in map(json.loads, (work / "denetim" / "resmi-d5_kartlar.jsonl").read_text(encoding="utf-8").splitlines())}
    assert rows["t:y1"]["iddialar"][0]["claim_id"] == "C-1" and rows["t:y1"]["adimlar"][0]["step_id"] == "t:step:1"
    assert rows["t:y1"]["butonlar"][0]["url"] == "https://a.example/4" and rows["t:y1"]["kaynaklar"][0]["text_file"] == "a.txt"
    term = json.loads((work / "denetim" / "sozluk-d5_kartlar.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert term["iddialar"][0]["claim_id"] == "C-T1"  # term_id sahipli defter satiri
    route = json.loads((work / "denetim" / "rota-d5_kartlar.jsonl").read_text(encoding="utf-8").splitlines()[0])
    assert [d["entry_id"] for d in route["duraklar"]] == ["t:m1", "t:m2"] and route["bacaklar"][0]["yuruyus_m"] == 500


def test_denetim_girdi_reaudit_subset_and_dry_run(work, capsys):
    dg.main([str(work), "--city-id", "t", "--tur", "d6", "--parca", "resmi", "--kayit", "t:y2"])
    lines = (work / "denetim" / "resmi-d6_kartlar.jsonl").read_text(encoding="utf-8").splitlines()
    assert [json.loads(l)["entry_id"] for l in lines] == ["t:y2"] and _out(capsys)["kayit"] == 1
    dg.main([str(work), "--city-id", "t", "--tur", "d7", "--dry-run"])
    assert _out(capsys)["yazildi"] is False and not list((work / "denetim").glob("*-d7_kartlar.jsonl"))
    assert dg.main([str(work), "--city-id", "t", "--tur", "x1"]) == 2


def test_kaynak_kullanim_counts_records_claims_buttons(work, capsys):
    code = kk.main([str(work), "t:kaynak:001", "t:kaynak:004", "t:kaynak:009"])
    rows = {r["source_id"]: r for r in map(json.loads, capsys.readouterr().out.strip().splitlines())}
    assert rows["t:kaynak:001"]["kullanim_sayisi"] == 4  # y1, m2, rota kaydi + iddia
    assert rows["t:kaynak:004"]["kullanim"] == ["buton t:action:y1-1"] and not rows["t:kaynak:004"]["serbest"]
    assert rows["t:kaynak:009"]["serbest"] and code == 1


def test_foto_denetim_girdi_marks_same_file_on_two_records(work, tmp_path, capsys):
    pkg = tmp_path / "PKG"
    (pkg / "Fotoğraflar").mkdir(parents=True)
    for n in ("a", "b", "k"):
        (pkg / "Fotoğraflar" / f"{n}.jpg").write_bytes(b"x")
    _jsonl(work / "data" / "parcalar" / "Fotoğraflar.foto.jsonl", [
        {"photo_id": "t:photo:m1-01", "entry_id": "t:m1", "role": "Mekân", "file": "Fotoğraflar/a.jpg", "caption": "Müze"},
        {"photo_id": "t:photo:m2-01", "entry_id": "t:m2", "role": "Mekân", "file": "Fotoğraflar/b.jpg", "caption": "Köprü"},
        {"photo_id": "t:photo:kapak-01", "entry_id": "", "role": "Kapak", "file": "Fotoğraflar/k.jpg", "caption": "Şehir"},
        {"photo_id": "t:photo:m2-02", "entry_id": "t:m2", "role": "Mekân", "file": "Fotoğraflar/yok.jpg"}])
    _jsonl(work / "foto" / "secim_temiz.jsonl", [{"photo_id": "t:photo:m1-01", "key": "t:m1|File:X.jpg"},
                                                {"photo_id": "t:photo:m2-01", "key": "t:m2|File:X.jpg"},
                                                {"photo_id": "t:photo:kapak-01", "key": "t:m1|File:X.jpg"}])
    _jsonl(work / "foto" / "candidates.jsonl", [{"candidate_id": "t:m1|File:X.jpg", "description_text": "San Vicente de Paúl"}])
    out = tmp_path / "fd"
    code = fg.main([str(work), "--pkg", str(pkg), "--out-dir", str(out)])
    s = _out(capsys)
    info = {r["photo_id"]: r for r in map(json.loads, (out / "bilgi.jsonl").read_text(encoding="utf-8").splitlines())}
    assert info["t:photo:m1-01"]["ayni_dosya_kayitlari"] == ["t:m2"] and info["t:photo:m1-01"]["aciklama"] == "San Vicente de Paúl"
    assert info["t:photo:m1-01"]["kayit_basligi"] == "Müze" and info["t:photo:kapak-01"]["commons_dosya"] == "File:X.jpg"
    assert s["dosyasiz"] == ["t:photo:m2-02"] and s["ayni_dosya_iki_kayit"] == 2 and code == 1
