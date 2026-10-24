"""pack_merge: ulke + bolge paketini sehre tek seferde uygulanacak birlesik pakete toplar. Ag yok."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "toolkit" / "scripts"))  # ortak araclar (deneme: toolkit'e dosya eklenmez)

import json

import pytest

import country_apply as ca
import pack_merge

TODAY = "2026-10-24"


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_pack(root: Path, prefix: str, slugs: list[tuple[str, str]], region: str | None = None,
              country: str = "ES") -> Path:
    """slugs: [(slug, konu)]; kaynak kimlikleri <prefix>:kaynak:NNN."""
    cards, claims, actions, index = [], [], [], []
    for n, (slug, topic) in enumerate(slugs, 1):
        sid = f"{prefix}:kaynak:{n:03d}"
        cards.append({"entry_id": f"es:{slug}", "city_id": "es", "slug": slug, "title": f"{slug}?",
                      "summary": "{sehir} için kural.", "source_ids": sid, "order": n, "topic_id": f"es:{topic}"})
        claims.append({"claim_id": f"C-{slug}-1", "entry_id": f"es:{slug}", "claim": "x", "source_id": sid,
                       "quote": "texto"})
        actions.append({"action_id": f"es:action:{slug}-1", "city_id": "es", "entry_id": f"es:{slug}",
                        "label": "Bilgi al", "url": f"https://{prefix}.example.es/{n}"})
        name = sid.replace(":", "_")
        (root / "kaynaklar").mkdir(parents=True, exist_ok=True)
        (root / "kaynaklar" / f"{name}.txt").write_text(f"texto {sid}", encoding="utf-8")
        (root / "kaynaklar" / f"{name}.html").write_text("<p>texto</p>", encoding="utf-8")
        index.append({"source_id": sid, "topic": topic, "url": f"https://{prefix}.example.es/{n}",
                      "text_file": f"kaynaklar/{name}.txt", "html_file": f"kaynaklar/{name}.html"})
    write_jsonl(root / ca.CARDS_FILE, cards)
    write_jsonl(root / ca.ACTIONS_FILE, actions)
    write_jsonl(root / ca.CLAIMS_FILE, claims)
    write_jsonl(root / "kaynak_dizini.jsonl", index)
    meta = {"country": country, "version": 7, "built": "2026-10-24", **({"region": region} if region else {}),
            "cards": {c["slug"]: {"sha256": ca.card_hash(c, [x for x in claims if x["entry_id"] == c["entry_id"]]),
                                  "valid_until": None} for c in cards}}
    (root / ca.PACK_FILE).write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    return root


@pytest.fixture
def packs(tmp_path):
    country = make_pack(tmp_path / "ES", "es", [("nie", "oturum"), ("sas-genel", "saglik")])
    region = make_pack(tmp_path / "ES" / "bolge" / "andalucia", "es-an", [("endulus-saglik-karti", "saglik")],
                       region="andalucia")
    return country, region


def test_merged_pack_applies_once_with_region_cards_in_same_topic_file(tmp_path, packs):
    out = tmp_path / "birlesik"
    summary = pack_merge.merge(list(packs), out)
    assert summary["cards"] == 3 and summary["sources"] == 2 + 1
    work = tmp_path / "is"
    work.mkdir()
    (work / "kaynak_dizini.jsonl").write_text("", encoding="utf-8")
    (work / "kaynak_taslak.jsonl").write_text("", encoding="utf-8")
    result = ca.apply_pack(work=work, pack=out, city_id="sevilla", city_name="Sevilla", order_start=9000, today=TODAY)
    assert result["copied"] == 3 and result["stale"] == []
    saglik = read_jsonl(work / ca.PARCALAR / "Yanıtlar.saglik.jsonl")
    assert {c["slug"] for c in saglik} == {"sas-genel", "endulus-saglik-karti"}
    assert all(c["topic_id"] == "sevilla:saglik" for c in saglik)
    scope = ca.audit_scope(work, out, today=TODAY)
    assert len(scope["skip"]) == 3 and scope["audit"] == {}


def test_parts_and_source_copies_are_recorded(tmp_path, packs):
    out = tmp_path / "birlesik"
    pack_merge.merge(list(packs), out)
    meta = json.loads((out / "pack.json").read_text(encoding="utf-8"))
    assert [p["region"] for p in meta["parts"]] == [None, "andalucia"]
    for row in read_jsonl(out / "kaynak_dizini.jsonl"):
        assert (out / row["text_file"]).is_file() and (out / row["html_file"]).is_file()


def test_duplicate_slug_is_rejected(tmp_path, packs):
    country, _ = packs
    clash = make_pack(tmp_path / "bolge2", "es-x", [("nie", "oturum")], region="x")
    with pytest.raises(ca.UsageError, match="tekrarlanan slug"):
        pack_merge.merge([country, clash], tmp_path / "out")


def test_duplicate_source_id_is_rejected(tmp_path, packs):
    country, _ = packs
    clash = make_pack(tmp_path / "bolge2", "es", [("baska-kart", "ev")], region="x")
    with pytest.raises(ca.UsageError, match="tekrarlanan kaynak"):
        pack_merge.merge([country, clash], tmp_path / "out")


def test_tampered_region_card_is_rejected(tmp_path, packs):
    country, region = packs
    rows = read_jsonl(region / ca.CARDS_FILE)
    rows[0]["summary"] = "elle değişti"
    write_jsonl(region / ca.CARDS_FILE, rows)
    with pytest.raises(ca.UsageError, match="hash"):
        pack_merge.merge([country, region], tmp_path / "out")


def test_different_country_is_rejected(tmp_path, packs):
    country, _ = packs
    other = make_pack(tmp_path / "PT", "pt", [("nif", "resmi")], country="PT")
    with pytest.raises(ca.UsageError, match="ulke kodu"):
        pack_merge.merge([country, other], tmp_path / "out")


def test_single_pack_is_rejected(tmp_path, packs):
    with pytest.raises(ca.UsageError, match="en az iki"):
        pack_merge.merge([packs[0]], tmp_path / "out")
