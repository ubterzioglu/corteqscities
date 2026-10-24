"""package_sources: kullanilan kaynak kopyalarini pakete tasir, snapshot_file/sha256 yazar (A6; pilot kaynak_paketle.py)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import package_sources as ps

SUB = "Lisans kanıtları"
A, B, C = b"<html>Kaynak A</html>", b"<html>Kaynak B</html>", b"%PDF-1.4 kaynak C"
TAMPERED = b"<html>degistirilmis</html>"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def row(n: int) -> dict:
    return {"source_id": f"t:kaynak:{n:03d}", "city_id": "t", "title": f"Kaynak {n}", "url": f"https://k{n}.example.org/",
            "verified": "Evet"}


def make_work(tmp_path: Path) -> tuple[Path, Path]:
    """Ana snap/ (duz ad), alt klasor (ters ve duz egik cizgi), eksik ve guvensiz yol iceren kaynak dizini."""
    work = tmp_path / "is"
    (work / "snap").mkdir(parents=True)
    (work / "snap_ek").mkdir()
    (work / "snap" / f"{sha(A)}.html").write_bytes(A)
    (work / "snap_ek" / f"{sha(B)}.html").write_bytes(B)
    (work / "snap_ek" / f"{sha(C)}.pdf").write_bytes(C)
    write_jsonl(work / "kaynak_dizini.jsonl", [
        {"source_id": "t:kaynak:001", "html_file": f"{sha(A)}.html", "html_sha256": sha(A)},
        {"source_id": "t:kaynak:002", "html_file": f"snap_ek\\{sha(B)}.html", "html_sha256": sha(B)},
        {"source_id": "t:kaynak:003", "html_file": f"snap_ek/{sha(C)}.pdf", "html_sha256": sha(C)},
        {"source_id": "t:kaynak:004", "html_file": "snap_ek/yok.html", "html_sha256": "0" * 64},
        {"source_id": "t:kaynak:005", "html_file": "../disari.html", "html_sha256": sha(b"is klasoru disi")}])
    (tmp_path / "disari.html").write_bytes(b"is klasoru disi")  # var ama is klasorunun disinda: okunmamali
    write_jsonl(work / "data" / "Kaynaklar.jsonl", [row(1), row(2), row(3)])
    package = tmp_path / "paket"
    stale = package / "Lisans kanıtları" / ("a"*64 + ".html")
    stale.parent.mkdir(parents=True)
    stale.write_bytes(b"eski kopya")
    return work, package


def run(capsys, work: Path, package: Path, *extra) -> tuple[int, dict]:
    code = ps.main([str(work), str(package), *map(str, extra)])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    return code, json.loads(lines[0])


# ---------------------------------------------------------------- mutlu yol

def test_used_snapshots_are_copied_by_hash_and_rows_point_to_them(tmp_path, capsys):
    work, package = make_work(tmp_path)
    code, summary = run(capsys, work, package)
    rows = read_jsonl(work / "data" / "Kaynaklar.jsonl")
    assert code == ps.EXIT_OK and summary["status"] == "ok"
    assert (summary["sources"], summary["with_snapshot"], summary["copied"], summary["removed_unused"]) == (3, 3, 3, 1)
    assert [(r["snapshot_file"], r["snapshot_sha256"]) for r in rows] == [
        (f"{SUB}/{sha(A)}.html", sha(A)), (f"{SUB}/{sha(B)}.html", sha(B)), (f"{SUB}/{sha(C)}.pdf", sha(C))]
    assert sorted(p.name for p in (package / SUB).iterdir()) == sorted([f"{sha(A)}.html", f"{sha(B)}.html", f"{sha(C)}.pdf"])
    assert {r["verified"] for r in rows} == {"Evet"}
    for r in rows:
        assert sha((package / r["snapshot_file"]).read_bytes()) == r["snapshot_sha256"]


def test_second_run_is_idempotent(tmp_path, capsys):
    work, package = make_work(tmp_path)
    run(capsys, work, package)
    first = (work / "data" / "Kaynaklar.jsonl").read_bytes()
    code, summary = run(capsys, work, package)
    assert code == ps.EXIT_OK and (summary["copied"], summary["removed_unused"]) == (0, 0)
    assert (work / "data" / "Kaynaklar.jsonl").read_bytes() == first


def test_rows_out_leaves_input_untouched_and_deletes_nothing(tmp_path, capsys):
    work, package = make_work(tmp_path)
    before = (work / "data" / "Kaynaklar.jsonl").read_bytes()
    out, detail = tmp_path / "cikti" / "Kaynaklar.jsonl", tmp_path / "rapor.json"
    code, summary = run(capsys, work, package, "--rows-out", out, "--out", detail)
    report = json.loads(detail.read_text(encoding="utf-8"))
    assert code == ps.EXIT_OK and (work / "data" / "Kaynaklar.jsonl").read_bytes() == before
    assert len(read_jsonl(out)) == 3 and (report["removed"], report["unused"], report["pruned"]) == ([], ["a"*64 + ".html"], False)
    assert (summary["removed_unused"], summary["unused_kept"]) == (0, 1) and (package / SUB / ("a"*64 + ".html")).is_file()


def test_partial_rows_never_delete_copies_of_other_sources(tmp_path, capsys):
    """Kismi --rows (yerinde) ile kosu: oteki kaynaklarin kopyalari silinirse asil Kaynaklar.jsonl silinen dosyalari
    gostermeye devam eder (denemede 3 dosya 1'e indi, cikis 0)."""
    work, package = make_work(tmp_path)
    run(capsys, work, package)  # tam kosu: A, B, C pakette
    full = read_jsonl(work / "data" / "Kaynaklar.jsonl")
    partial = write_jsonl(tmp_path / "kismi.jsonl", [row(1)])
    code, summary = run(capsys, work, package, "--rows", partial)
    assert code == ps.EXIT_OK and (summary["removed_unused"], summary["unused_kept"]) == (0, 2)
    for r in full:  # asil satirlarin gosterdigi her dosya yerinde ve hash'i tutuyor
        assert sha((package / r["snapshot_file"]).read_bytes()) == r["snapshot_sha256"]
    code, summary = run(capsys, work, package, "--rows", partial, "--prune")  # acik istek: silinir
    assert code == ps.EXIT_OK and summary["removed_unused"] == 2
    assert sorted(p.name for p in (package / SUB).iterdir()) == [f"{sha(A)}.html"]


# ---------------------------------------------------------------- kirma testleri

def test_missing_unsafe_and_unknown_sources_get_no_snapshot(tmp_path, capsys):
    work, package = make_work(tmp_path)
    write_jsonl(work / "data" / "Kaynaklar.jsonl", [row(1), row(4), row(5), row(9)])
    code, summary = run(capsys, work, package)
    rows = {r["source_id"]: r for r in read_jsonl(work / "data" / "Kaynaklar.jsonl")}
    assert code == ps.EXIT_FINDINGS and summary["missing"] == ["t:kaynak:004", "t:kaynak:005", "t:kaynak:009"]
    for sid in ("t:kaynak:004", "t:kaynak:005", "t:kaynak:009"):
        assert (rows[sid]["snapshot_file"], rows[sid]["snapshot_sha256"], rows[sid]["verified"]) == ("", "", "Hayır")
    assert sorted(p.name for p in (package / SUB).iterdir()) == [f"{sha(A)}.html"]  # disaridaki dosya kopyalanmadi


def test_tampered_snapshot_is_not_packaged(tmp_path, capsys):
    work, package = make_work(tmp_path)
    (work / "snap" / f"{sha(A)}.html").write_bytes(TAMPERED)  # icerik dizindeki html_sha256 ile tutmuyor
    code, summary = run(capsys, work, package)
    first = read_jsonl(work / "data" / "Kaynaklar.jsonl")[0]
    assert code == ps.EXIT_FINDINGS and summary["hash_mismatch"] == ["t:kaynak:001"]
    assert (first["snapshot_file"], first["verified"]) == ("", "Hayır")
    assert not (package / SUB / f"{sha(TAMPERED)}.html").exists()


def test_corrupted_package_copy_is_repaired(tmp_path, capsys):
    work, package = make_work(tmp_path)
    run(capsys, work, package)
    (package / SUB / f"{sha(A)}.html").write_bytes(b"bozuk")
    code, summary = run(capsys, work, package)
    assert code == ps.EXIT_OK and summary["copied"] == 1 and (package / SUB / f"{sha(A)}.html").read_bytes() == A


def test_usage_errors_exit_2(tmp_path, capsys):
    work, package = make_work(tmp_path)
    assert ps.main([str(work), str(tmp_path / "yok")]) == ps.EXIT_USAGE  # paket koku yoksa olusturulmaz
    assert not (tmp_path / "yok").exists()
    assert ps.main([str(work), str(package), "--rows", str(tmp_path / "yok.jsonl")]) == ps.EXIT_USAGE
    assert ps.main([str(tmp_path / "is_yok"), str(package)]) == ps.EXIT_USAGE
    (work / "kaynak_dizini.jsonl").unlink()
    assert ps.main([str(work), str(package)]) == ps.EXIT_USAGE
    assert ps.main(["--help"]) == ps.EXIT_OK


def test_unreadable_input_and_failed_writes_exit_2_not_1(tmp_path, capsys):
    """Beklenmeyen hata main disina kacarsa Python cikisi 1 olur ve 'bulgu' (kopyasi eksik kaynak) ile karisir."""
    work, package = make_work(tmp_path)
    rows = work / "data" / "Kaynaklar.jsonl"
    original = rows.read_bytes()
    rows.write_bytes(original + '{"title": "Müze"}\n'.encode("cp1252"))  # UTF-8 olmayan satir
    assert ps.main([str(work), str(package)]) == ps.EXIT_USAGE and "Kaynaklar.jsonl: UTF-8 degil" in capsys.readouterr().err
    rows.write_bytes(original)
    folder = tmp_path / "klasor"
    folder.mkdir()
    assert ps.main([str(work), str(package), "--rows-out", str(folder)]) == ps.EXIT_USAGE  # satirlar yazilamaz
    blocked = tmp_path / "paket2"
    blocked.mkdir()
    (blocked / "Lisans kanıtları").write_text("klasor degil", encoding="utf-8")  # hedef klasor kurulamaz
    assert ps.main([str(work), str(blocked)]) == ps.EXIT_USAGE and "HATA" in capsys.readouterr().err
