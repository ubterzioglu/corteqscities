"""photo_rounds: photo_rows ve photo_previews'in ortak tur dosyasi kurali (A12: ek tur klasorleri <is>/foto_*/).

Kural tek yerde durur: iki scriptte ayri kopya olunca biri degisirse scriptler farkli dosyalari okur (inceleme U1).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import photo_previews
import photo_rounds as rounds
import photo_rows


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def names(work: Path, paths: list[Path]) -> list[str]:
    return [rounds.shown(work, path) for path in paths]


def test_round_files_main_first_then_foto_star_folders_then_extra_dirs(tmp_path):
    work = tmp_path / "is"
    for folder in ("foto", "foto_b", "foto_a", "foto/tur1", "ek_tur", "fotolar"):
        write_jsonl(work / folder / "candidates.jsonl", [{"candidate_id": folder}])
    (work / "foto_bos").mkdir()  # aday dosyasi olmayan tur klasoru listeye girmez
    assert names(work, rounds.round_files(work, "candidates.jsonl")) == [
        "foto/candidates.jsonl", "foto_a/candidates.jsonl", "foto_b/candidates.jsonl"]  # foto/tur1, ek_tur taranmaz
    extra = rounds.round_files(work, "candidates.jsonl",
                               [work / "ek_tur", work / "foto_a", work / "foto", work / "ek_tur", work / "yok"])
    assert names(work, extra) == ["foto/candidates.jsonl", "foto_a/candidates.jsonl", "foto_b/candidates.jsonl",
                                  "ek_tur/candidates.jsonl"]  # ayni dosya iki kez okunmaz; dosyasiz klasor eklenmez
    empty = tmp_path / "bos"
    # ana tur sart: dosya yoksa da listede kalir, okuyan script cikis 2 verir
    assert rounds.round_files(empty, "search.jsonl") == [empty / "foto" / "search.jsonl"]


def test_load_candidates_keeps_the_first_file_and_the_last_line_within_a_file(tmp_path):
    first = write_jsonl(tmp_path / "a.jsonl", [{"candidate_id": "k1", "v": 1}, {"candidate_id": "k1", "v": 2}])
    second = write_jsonl(tmp_path / "b.jsonl", [{"candidate_id": "k1", "v": 3}, {"candidate_id": "k2", "v": 4}])
    merged = rounds.load_candidates([first, second])
    assert {cid: row["v"] for cid, row in merged.items()} == {"k1": 2, "k2": 4}


def test_bad_jsonl_is_an_input_error_naming_the_file_and_line(tmp_path):
    bad = tmp_path / "bozuk.jsonl"
    bad.write_text('{"a": 1}\n[1, 2]\n', encoding="utf-8")
    with pytest.raises(rounds.InputError, match=r"bozuk\.jsonl:2: nesne bekleniyor"):
        rounds.read_jsonl(bad)
    bad.write_text('{"a": 1}\n{oops\n', encoding="utf-8")
    with pytest.raises(ValueError, match=r"bozuk\.jsonl:2: gecersiz JSON"):  # ValueError: iki script de cikis 2 verir
        rounds.read_jsonl(bad)
    bad.write_bytes('{"a": "Müze"}\n'.encode("cp1252"))
    with pytest.raises(rounds.InputError, match=r"bozuk\.jsonl: UTF-8 degil"):
        rounds.read_jsonl(bad)
    bom = tmp_path / "bom.jsonl"
    bom.write_bytes(b"\xef\xbb\xbf" + b'{"a": 1}\n\n')
    assert rounds.read_jsonl(bom) == [{"a": 1}]


def test_shown_is_relative_with_slashes_inside_work_and_absolute_outside(tmp_path):
    work = tmp_path / "is"
    assert rounds.shown(work, work / "foto_ek" / "candidates.jsonl") == "foto_ek/candidates.jsonl"
    outside = tmp_path / "baska" / "candidates.jsonl"
    assert rounds.shown(work, outside) == str(outside)


def test_both_scripts_use_the_one_shared_rule():
    for module in (photo_rows, photo_previews):
        assert module.round_files is rounds.round_files and module.load_candidates is rounds.load_candidates
        assert module.read_jsonl is rounds.read_jsonl and module.shown is rounds.shown
