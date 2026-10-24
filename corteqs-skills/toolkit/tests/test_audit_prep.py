"""audit_prep.py: city-audit fotograf hazirligi (eskiden city-audit SKILL.md'deki gomulu $hazirla / $ciftler).

S2'nin scratchpad testinin kalici hali (sentetik paket, yalniz tmp_path; ag yok, paket ve depo yazilmaz):
- (a) eski kanit dosyalari, eski Excel kopyasi ve eski pafta her kosuda silinir (salt okunur olsalar da); kilitli
  dosya sessiz gecilmez, cikis 2;
- (b) bozuk source_evidence_json adimi dusurmez, nedeniyle kanitsiz_foto'ya yazilir;
- (c) items.jsonl excel_row ve role tasir (pilot L0 items.jsonl alanlari); etiket Mekânlar ya da Mahalleler adi;
- yol taramasi (K84) her 'file' / '*_file' sutununu ve Teslimler'deki JSON/CSV/HTML'yi kapsar (alt klasorleri degil);
- envanterin dup_sha gruplari kapak_mekan / K05 / K63 diye ayrilir; dHash ciftlerinde yalniz ayni bayttaki
  kapak-mekan cifti dusulur (K63).
Ek: cikti gomulu yardimcininkiyle ayni (tam beklenen deger ve sira), cikis 0/1/2 (her bulgu turu tek basina 1),
photo_id ya da file'i olmayan Fotoğraflar satiri bulgu adayidir (girdi hatasi degil), girdi hatasi hicbir sey
silinmeden yakalanir, BOM'lu dump okunur, paket salt okunur (OUT paketin icinde ya da paket silinen klasorde olamaz),
ciktilari tuketiciler okur (photo_candidates from-evidence, contact_sheet), city-audit SKILL.md gomulu Python yerine
script'i cagirir ve cikis 2'de blogu durdurur.
Calistirma (toolkit klasorunden): $env:PYTHONDONTWRITEBYTECODE=1; <PY> -m pytest -q -p no:cacheprovider tests\\test_audit_prep.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

import audit_prep
import contact_sheet
import photo_candidates
import skill_commands_helpers as sc

SCRIPT = Path(audit_prep.__file__).resolve()
API = {"url": "https://upload.wikimedia.org/a.jpg", "descriptionurl": "https://commons.wikimedia.org/wiki/File:A.jpg",
       "extmetadata": {"LicenseShortName": {"value": "CC BY-SA 4.0"}}}
FOTO = [  # 4 mekan + 1 kapak + 1 mahalle karesi; kapak-01 ve m1 ayni bayt, m2 ve m3 ayni bayt
    {"_row": 8, "photo_id": "x:photo:m1", "role": "Mekân", "entry_id": "x:m", "file": "Fotoğraflar/m1.jpg", "sha256": "aa"},
    {"_row": 9, "photo_id": "x:photo:m2", "role": "Mekân", "entry_id": "x:m", "file": "Fotoğraflar\\m2.jpg", "sha256": "bb"},
    {"_row": 10, "photo_id": "x:photo:m3", "role": "Mekân", "entry_id": "x:n", "file": "Fotoğraflar/m3.jpg", "sha256": "bb"},
    {"_row": 11, "photo_id": "x:photo:m4", "role": "Mekân", "entry_id": "x:n", "file": "Fotoğraflar/m4.jpg", "sha256": "dd"},
    {"_row": 12, "photo_id": "x:photo:kapak-01", "role": "Kapak", "file": "Fotoğraflar/kapak_01.jpg", "sha256": "aa"},
    {"_row": 13, "photo_id": "x:photo:h1", "role": "Mekân", "entry_id": "x:h", "file": "Fotoğraflar/h1.jpg", "sha256": "ff"},
]
KANIT = [
    {"_row": 8, "photo_id": "x:photo:m1", "pixel_review_file": "Fotoğraflar/m1.jpg",
     "source_snapshot_file": "Lisans kanıtları\\s1.html", "license_snapshot_file": "Lisans kanıtları/l1.html",
     "source_evidence_json": json.dumps({"original_api_record": API})},
    {"_row": 9, "photo_id": "x:photo:m2", "source_evidence_json": "bu JSON degil {"},
    {"_row": 10, "photo_id": "x:photo:m3", "source_evidence_json": "[1, 2]"},
    {"_row": 11, "photo_id": "x:photo:m4", "source_evidence_json": json.dumps({"corteqs_long_value": "k1", "sha256": "f"})},
    {"_row": 12, "photo_id": "x:photo:kapak-01", "source_evidence_json": json.dumps({"author": "A"})},
]
MEKAN = [{"_row": 8, "entry_id": "x:m", "title": "Müze"}, {"_row": 9, "entry_id": "x:n", "title": "Park"}]
MAHALLE = [{"_row": 8, "entry_id": "x:h", "title": "Merkez"}]
DUP = [
    {"sha256": "aa", "files": ["Fotoğraflar/kapak_01.jpg", "Fotoğraflar/m1.jpg"]},   # zararsiz
    {"sha256": "bb", "files": ["Fotoğraflar/m2.jpg", "Fotoğraflar/m3.jpg"]},         # iki mekan karesi: K63
    {"sha256": "dd", "files": ["Fotoğraflar/m4.jpg", "Teslimler/.download-cache/9f"]},  # artik: K05
    {"sha256": "ee", "files": ["Fotoğraflar/sahipsiz.jpg", "Fotoğraflar/sahipsiz2.jpg"]},  # satira bagli degil: K05
]
TESLIM = {
    "photo-provenance-v7.json": json.dumps(
        [{"web_file": "Teslimler\\WebKopyalari\\a.webp", "original_file": "Fotoğraflar/m1.jpg", "not": "a\\b"}]),
    "fotograf-atiflari-v7.csv": "photo_id,web_file\nx:photo:m1,Teslimler\\WebKopyalari\\a.webp\n",
    "fotograf-atif-onizleme.html": '<img src="../Teslimler%5CWebKopyalari%5Ca.webp"><img src=\'../Fotoğraflar/m1.jpg\'>'
                                   '<a href="https://commons.wikimedia.org/wiki/File:A%5CB.jpg">x</a>'
                                   '<a href="../Teslimler\\b.webp">y</a>',
    "bozuk.json": "{bozuk",  # okunamayan dosya adimi dusurmez
    "TESLIM_OZETI.txt": "Paket: 1 dosya",
}
CACHE_FILE = "onbellek.json"  # Teslimler\.download-cache altinda '\' yollu artik; alt klasor taranmaz
NO_FILE_ROW = {"_row": 20, "photo_id": "x:photo:m9", "role": "Mekân", "entry_id": "x:m", "sha256": "99"}
NO_ID_ROW = {"_row": 21, "role": "Mekân", "entry_id": "x:n", "file": "Fotoğraflar/m9.jpg", "sha256": "99"}


def unreadable(text: str) -> str:
    """Okunamayan Teslimler JSON'u icin tarama degeri; hata metni Python'un json modulunden gelir."""
    try:
        json.loads(text)
    except ValueError as exc:
        return f"okunamadı: {exc}"
    raise AssertionError(f"gecerli JSON: {text!r}")


# Gomulu yardimcinin (S2, pilotta denenmis) bu fikstur icin ciktisi; sira dahil (Windows ve POSIX'te ayni)
EXPECTED_SCAN = [
    ("FotoğrafKaynakları.original_file", "0/1"), ("FotoğrafKaynakları.web_file", "1/1"), ("Fotoğraflar.file", "1/6"),
    ("Kanıtlar.license_snapshot_file", "0/1"), ("Kanıtlar.pixel_review_file", "0/1"),
    ("Kanıtlar.source_snapshot_file", "1/1"), ("Kaynaklar.snapshot_file", "0/1"),
    ("Teslimler/bozuk.json", unreadable(TESLIM["bozuk.json"])),
    ("Teslimler/fotograf-atif-onizleme.html", "2/3"), ("Teslimler/fotograf-atiflari-v7.csv", "1/1"),
    ("Teslimler/photo-provenance-v7.json", "1/2"),
]
EXPECTED_MISSING = {"x:photo:m2": "JSON değil", "x:photo:m3": "JSON nesnesi değil",
                    "x:photo:m4": "UzunAlanlar'da (çözülmedi)", "x:photo:kapak-01": "original_api_record yok"}
EXPECTED_DUP = {"kapak_mekan": [["Fotoğraflar/kapak_01.jpg", "Fotoğraflar/m1.jpg"]],
                "K05": [["Fotoğraflar/m4.jpg", "Teslimler/.download-cache/9f"],
                        ["Fotoğraflar/sahipsiz.jpg", "Fotoğraflar/sahipsiz2.jpg"]],
                "K63": [["Fotoğraflar/m2.jpg", "Fotoğraflar/m3.jpg"]]}
EXPECTED_ITEMS = [  # (key, paket icindeki yol, label, group, excel_row, role)
    ("x:photo:m1", "Fotoğraflar/m1.jpg", "Müze · m1.jpg", "x:m", 8, "Mekân"),
    ("x:photo:m2", "Fotoğraflar/m2.jpg", "Müze · m2.jpg", "x:m", 9, "Mekân"),
    ("x:photo:m3", "Fotoğraflar/m3.jpg", "Park · m3.jpg", "x:n", 10, "Mekân"),
    ("x:photo:m4", "Fotoğraflar/m4.jpg", "Park · m4.jpg", "x:n", 11, "Mekân"),
    ("x:photo:kapak-01", "Fotoğraflar/kapak_01.jpg", "Kapak · kapak_01.jpg", None, 12, "Kapak"),
    ("x:photo:h1", "Fotoğraflar/h1.jpg", "Merkez · h1.jpg", "x:h", 13, "Mekân"),  # ad Mahalleler'den
]
PAIRS = [{"a": "x:photo:kapak-01", "b": "x:photo:m1", "distance": 0, "same_group": False},  # ayni bayt: zararsiz
         {"a": "x:photo:m2", "b": "x:photo:m3", "distance": 0, "same_group": False},
         {"a": "x:photo:kapak-01", "b": "x:photo:m4", "distance": 3, "same_group": False},  # farkli bayt: aday
         {"a": "x:photo:m1", "b": "x:photo:m4", "distance": 4, "same_group": False}]
NO_FINDINGS = {"yol": {}, "kanitsiz_foto": 0, "K05": 0, "K63": 0, "eksik_alanli_foto": 0}


# ------------------------------------------------------------------ yardimcilar

def jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def read_rows(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build(root: Path, foto: list[dict], kanit: list[dict], dup: list[dict], teslim: dict[str, str],
          extra: dict[str, list[dict]] | None = None) -> tuple[Path, Path]:
    """OUT (xlsx_dump ve inventory ciktilari) ve PKG (Teslimler) kurar."""
    out, pkg = root / "out", root / "pkg"
    dump = out / "_dump"
    sheets = {"Fotoğraflar": foto, "Kanıtlar": kanit, "Mekânlar": MEKAN, "Mahalleler": MAHALLE, **(extra or {})}
    for sheet, rows in sheets.items():
        jsonl(dump / f"{sheet}.jsonl", rows)
    (dump / "summary.json").write_text("{}", encoding="utf-8")  # xlsx_dump ozeti taranmaz (.jsonl degil)
    (out / "dosya-envanteri.json").write_text(json.dumps({"findings": {"dup_sha": dup}}), encoding="utf-8")
    tes = pkg / "Teslimler"
    (tes / ".download-cache").mkdir(parents=True)
    (tes / ".download-cache" / CACHE_FILE).write_text(json.dumps(["Teslimler\\WebKopyalari\\a.webp"]), encoding="utf-8")
    (tes / "WebKopyalari").mkdir()
    for name, text in teslim.items():
        (tes / name).write_text(text, encoding="utf-8-sig" if name.endswith(".csv") else "utf-8")
    return out, pkg


@pytest.fixture()
def paket(tmp_path: Path) -> tuple[Path, Path]:
    extra = {"Kaynaklar": [{"_row": 8, "source_id": "x:src:1", "snapshot_file": "Lisans kanıtları/kaynaklar/1.html"}],
             "FotoğrafKaynakları": [{"_row": 8, "photo_id": "x:photo:m1", "original_file": "Fotoğraflar/m1.jpg",
                                     "web_file": "Teslimler\\WebKopyalari\\a.webp"}]}
    return build(tmp_path, FOTO, KANIT, DUP, TESLIM, extra)


@pytest.fixture()
def temiz(tmp_path: Path) -> tuple[Path, Path]:
    """Bulgusuz paket: '/' yollar, her karenin kaniti var, ayni SHA yalniz kapak-mekan."""
    foto = [FOTO[0], FOTO[4]]
    kanit = [{"_row": 8, "photo_id": "x:photo:m1", "pixel_review_file": "Fotoğraflar/m1.jpg",
              "source_evidence_json": json.dumps({"original_api_record": API})},
             {"_row": 12, "photo_id": "x:photo:kapak-01", "source_evidence_json": json.dumps({"original_api_record": API})}]
    teslim = {"photo-provenance-v7.json": json.dumps([{"web_file": "Teslimler/WebKopyalari/a.webp"}]),
              "fotograf-atiflari-v7.csv": "photo_id,web_file\nx:photo:m1,Teslimler/WebKopyalari/a.webp\n",
              "fotograf-atif-onizleme.html": '<img src="../Teslimler/WebKopyalari/a.webp">'}
    return build(tmp_path, foto, kanit, DUP[:1], teslim)


def run(capsys: pytest.CaptureFixture[str], *argv: object) -> tuple[int, dict]:
    code = audit_prep.main([str(a) for a in argv])
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1, lines  # stdout tek satir JSON
    return code, json.loads(lines[0])


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def read_items(out: Path) -> list[dict]:
    return read_rows(out / "_foto" / "items.jsonl")


def write_pairs(out: Path, pairs: list[dict]) -> None:
    (out / "temas-sayfalari").mkdir(parents=True, exist_ok=True)
    (out / "temas-sayfalari" / "dhash.json").write_text(json.dumps({"pairs": pairs}), encoding="utf-8")


def snapshot(root: Path) -> dict[str, str]:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "<klasor>"
            for p in sorted(root.rglob("*"))}


def stale_files(out: Path) -> list[Path]:
    """Onceki kosudan kalmis kanit, Excel kopyasi ve pafta."""
    old = [out / "_foto" / "kanit" / "Lisans kanıtları" / "0300.source-evidence.json",
           out / "_foto" / "kanit" / "CITY-039_x_v000.xlsx", out / "temas-sayfalari" / "sheet_09.jpg"]
    for path in old:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"eski")
    return old


def found(result: dict) -> dict:
    """hazirla ozetindeki bulgu turleri (bulgusuz tur 0 ya da bos); okunamayan dosyanin hata metni kirpilir."""
    paths = {key: "okunamadı" if value.startswith("okunamadı") else value
             for key, value in result["ters_egik_cizgi"].items() if not value.startswith("0/")}
    return {"yol": paths, "kanitsiz_foto": result["kanitsiz_foto"], "K05": result["ayni_sha"]["K05"],
            "K63": result["ayni_sha"]["K63"], "eksik_alanli_foto": result.get("eksik_alanli_foto", 0)}


def edit_row(path: Path, photo_id: str, **changes: str) -> None:
    jsonl(path, [{**row, **changes} if row.get("photo_id") == photo_id else row for row in read_rows(path)])


def append_rows(path: Path, rows: list[dict]) -> None:
    jsonl(path, [*read_rows(path), *rows])


def add_dup_group(out: Path, group: dict) -> None:
    path = out / "dosya-envanteri.json"
    report = read_json(path)
    findings = {**report["findings"], "dup_sha": [*report["findings"]["dup_sha"], group]}
    path.write_text(json.dumps({**report, "findings": findings}), encoding="utf-8")


# ------------------------------------------------------------------ S2 bulgulari (gomulu yardimcidan tasindi)

def test_stale_evidence_xlsx_and_sheets_are_cleared(paket, capsys):  # bulgu (a)
    out, pkg = paket
    old = stale_files(out)
    code, _ = run(capsys, "hazirla", out, pkg)
    assert code == 1  # fikstur bulgu tasir; karar degil
    assert [p.exists() for p in old] == [False, False, False]  # photo_candidates.find_xlsx eski v000'i secerdi
    evidence = out / "_foto" / "kanit" / "Lisans kanıtları"
    assert sorted(p.name for p in evidence.iterdir()) == ["0001.source-evidence.json"]
    assert sorted(p.name for p in (out / "_foto" / "kanit").iterdir()) == ["Lisans kanıtları"]
    assert not (out / "temas-sayfalari").exists()  # contact_sheet bastan kurar


def test_read_only_stale_files_are_cleared(paket, capsys):  # Copy-Item salt okunur ozniteligi korur
    out, pkg = paket
    old = stale_files(out)
    for path in old:
        os.chmod(path, stat.S_IREAD)
    try:
        code, result = run(capsys, "hazirla", out, pkg)
    finally:
        for path in old:
            if path.exists():
                os.chmod(path, stat.S_IWRITE)
    assert code == 1, result
    assert [p.exists() for p in old] == [False, False, False]


def test_locked_stale_file_exits_two_and_says_why(paket, capsys, monkeypatch):
    """Excel'de acik (kilitli) dosya silinemez: sessiz gecilirse eski kopya kalir; cikis 2 ve neden yazilir."""
    out, pkg = paket
    old = stale_files(out)
    real_unlink = os.unlink

    def locked(path, *args, **kwargs):  # rmtree her dosyayi os.unlink ile siler (Windows ve POSIX)
        if Path(os.fspath(path)).name == old[1].name:
            raise PermissionError(13, "dosya baska bir islemde acik", os.fspath(path))
        return real_unlink(path, *args, **kwargs)

    monkeypatch.setattr(os, "unlink", locked)
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 2 and "kilitli ya da salt okunur" in result["error"], result
    assert old[1].exists()
    assert not (out / "_foto" / "items.jsonl").exists() and not (out / "_foto" / "hazirlik.json").exists()


def test_bad_evidence_json_is_reported_not_fatal(paket, capsys):  # bulgu (b)
    out, pkg = paket
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 1 and result["kanit_dosyasi"] == 1 and result["kanitsiz_foto"] == 4
    detail = read_json(out / "_foto" / "hazirlik.json")
    assert detail["kanitsiz_foto"] == EXPECTED_MISSING
    written = read_json(out / "_foto" / "kanit" / "Lisans kanıtları" / "0001.source-evidence.json")
    assert written == {"photo_id": "x:photo:m1", "api_imageinfo": API}


def test_items_carry_excel_row_and_role(paket, capsys):  # bulgu (c): pilot L0 items.jsonl alanlari
    out, pkg = paket
    run(capsys, "hazirla", out, pkg)
    items = read_items(out)
    assert [list(i) for i in items] == [["key", "path", "label", "group", "excel_row", "role"]] * len(EXPECTED_ITEMS)
    assert [(i["key"], i["path"], i["label"], i["group"], i["excel_row"], i["role"]) for i in items] == [
        (key, str(pkg / rel), label, group, row, role) for key, rel, label, group, row, role in EXPECTED_ITEMS]


def test_path_scan_covers_every_file_column_and_html_links(paket, capsys):  # tarama yalniz json/csv + sabit alan degil
    out, pkg = paket
    scan = run(capsys, "hazirla", out, pkg)[1]["ters_egik_cizgi"]
    assert scan["Kanıtlar.source_snapshot_file"] == "1/1" and scan["Kanıtlar.license_snapshot_file"] == "0/1"
    assert scan["Fotoğraflar.file"] == "1/6" and scan["FotoğrafKaynakları.web_file"] == "1/1"
    assert scan["Teslimler/fotograf-atif-onizleme.html"] == "2/3"  # %5C ve '\'; mutlak https adresi sayilmaz
    assert scan["Teslimler/photo-provenance-v7.json"] == "1/2" and scan["Teslimler/fotograf-atiflari-v7.csv"] == "1/1"
    assert scan["Teslimler/bozuk.json"].startswith("okunamadı: ")  # adim dusmez, dosya bulgu olur
    assert "Teslimler/TESLIM_OZETI.txt" not in scan  # yalniz JSON/CSV/HTML
    assert f"Teslimler/{CACHE_FILE}" not in scan  # alt klasor (.download-cache) taranmaz


def test_dup_sha_groups_are_classified(paket, capsys):  # dup_sha kosulsuz 'bilgi amacli' degil
    out, pkg = paket
    _, result = run(capsys, "hazirla", out, pkg)
    assert result["ayni_sha"] == {"kapak_mekan": 1, "K05": 2, "K63": 1}
    assert read_json(out / "_foto" / "hazirlik.json")["ayni_sha"] == EXPECTED_DUP


def test_dhash_pairs_drop_only_identical_cover_venue(paket, capsys):  # dhash.json pairs L0'da okunur
    out, pkg = paket
    run(capsys, "hazirla", out, pkg)  # gercek sira: hazirla -> contact_sheet (dhash.json) -> ciftler
    write_pairs(out, PAIRS)
    code, result = run(capsys, "ciftler", out)
    assert code == 1  # K63 adayi var: karar L1'de
    assert read_json(out / "_foto" / "dhash-ciftleri.json") == result
    assert result["dhash_cift"] == 4 and result["kapak_mekan"] == 1
    assert result["K63_aday"] == PAIRS[1:]


# ------------------------------------------------------------------ ayni cikti, cikis kodlari

def test_output_is_the_embedded_helpers_output(paket, capsys):
    out, pkg = paket
    _, result = run(capsys, "hazirla", out, pkg)
    detail = out / "_foto" / "hazirlik.json"
    assert list(result) == ["ters_egik_cizgi", "kanit_dosyasi", "kanitsiz_foto", "ayni_sha", "ayrinti"]
    assert list(result["ters_egik_cizgi"].items()) == EXPECTED_SCAN
    assert result["ayni_sha"] == {"kapak_mekan": 1, "K05": 2, "K63": 1} and result["ayrinti"] == str(detail)
    assert read_json(detail) == {"ters_egik_cizgi": dict(EXPECTED_SCAN), "kanit_dosyasi": 1,
                                 "kanitsiz_foto": EXPECTED_MISSING, "ayni_sha": EXPECTED_DUP}
    assert list(read_json(detail)["kanitsiz_foto"]) == list(EXPECTED_MISSING)  # Kanıtlar satir sirasi


def test_dump_files_with_bom_are_read(paket, capsys):  # ör. PowerShell 5.1 'Set-Content -Encoding utf8' BOM yazar
    out, pkg = paket
    for path in (out / "_dump").glob("*.jsonl"):
        path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8-sig")
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 1 and list(result["ters_egik_cizgi"].items()) == EXPECTED_SCAN
    assert read_json(out / "_foto" / "hazirlik.json")["kanitsiz_foto"] == EXPECTED_MISSING
    assert [item["label"] for item in read_items(out)] == [item[2] for item in EXPECTED_ITEMS]
    write_pairs(out, PAIRS)
    code, result = run(capsys, "ciftler", out)
    assert code == 1 and result["K63_aday"] == PAIRS[1:]


def test_clean_package_exits_zero(temiz, capsys):
    out, pkg = temiz
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 0, result
    assert found(result) == NO_FINDINGS and "eksik_alanli_foto" not in result  # alan yalniz varsa yazilir
    assert all(value.startswith("0/") for value in result["ters_egik_cizgi"].values()), result["ters_egik_cizgi"]
    assert (result["kanit_dosyasi"], result["kanitsiz_foto"]) == (2, 0)
    assert result["ayni_sha"] == {"kapak_mekan": 1, "K05": 0, "K63": 0}
    write_pairs(out, PAIRS[:1])  # yalniz ayni bayttaki kapak-mekan cifti
    code, result = run(capsys, "ciftler", out)
    assert (code, result) == (0, {"dhash_cift": 1, "kapak_mekan": 1, "K63_aday": []})


def _evidence_not_json(out: Path, pkg: Path) -> None:
    edit_row(out / "_dump" / "Kanıtlar.jsonl", "x:photo:kapak-01", source_evidence_json="bozuk {")


def _orphan_copies(out: Path, pkg: Path) -> None:  # iki dosya da hicbir Fotoğraflar satirina bagli degil
    add_dup_group(out, DUP[3])


def _twin_venue_photos(out: Path, pkg: Path) -> None:  # iki mekan karesi ayni dosya
    twins = [{"_row": 13, "photo_id": "x:photo:m5", "role": "Mekân", "entry_id": "x:m", "file": "Fotoğraflar/m5.jpg",
              "sha256": "cc"},
             {"_row": 14, "photo_id": "x:photo:m6", "role": "Mekân", "entry_id": "x:m", "file": "Fotoğraflar/m6.jpg",
              "sha256": "cc"}]
    append_rows(out / "_dump" / "Fotoğraflar.jsonl", twins)
    add_dup_group(out, {"sha256": "cc", "files": ["Fotoğraflar/m5.jpg", "Fotoğraflar/m6.jpg"]})


def _backslash_in_excel(out: Path, pkg: Path) -> None:
    edit_row(out / "_dump" / "Kanıtlar.jsonl", "x:photo:m1", pixel_review_file="Fotoğraflar\\m1.jpg")


def _backslash_in_html_link(out: Path, pkg: Path) -> None:
    (pkg / "Teslimler" / "fotograf-atif-onizleme.html").write_text(
        '<img src="../Teslimler%5CWebKopyalari%5Ca.webp">', encoding="utf-8")


def _unreadable_delivery_json(out: Path, pkg: Path) -> None:
    (pkg / "Teslimler" / "bozuk.json").write_text(TESLIM["bozuk.json"], encoding="utf-8")


def _undecodable_delivery_html(out: Path, pkg: Path) -> None:  # gomulu yardimci burada cokerdi
    (pkg / "Teslimler" / "eski.html").write_bytes(b'<img src="\xff.webp">')


def _photo_row_without_file(out: Path, pkg: Path) -> None:
    append_rows(out / "_dump" / "Fotoğraflar.jsonl", [NO_FILE_ROW])


def _photo_row_without_id(out: Path, pkg: Path) -> None:
    append_rows(out / "_dump" / "Fotoğraflar.jsonl", [NO_ID_ROW])


@pytest.mark.parametrize("damage, finding", [
    pytest.param(_evidence_not_json, {"kanitsiz_foto": 1}, id="kanitsiz-kare"),
    pytest.param(_orphan_copies, {"K05": 1}, id="K05"),
    pytest.param(_twin_venue_photos, {"K63": 1}, id="K63"),
    pytest.param(_backslash_in_excel, {"yol": {"Kanıtlar.pixel_review_file": "1/1"}}, id="excel-ters-egik"),
    pytest.param(_backslash_in_html_link, {"yol": {"Teslimler/fotograf-atif-onizleme.html": "1/1"}}, id="html-5C"),
    pytest.param(_unreadable_delivery_json, {"yol": {"Teslimler/bozuk.json": "okunamadı"}}, id="okunamayan-json"),
    pytest.param(_undecodable_delivery_html, {"yol": {"Teslimler/eski.html": "okunamadı"}}, id="utf8-olmayan-html"),
    pytest.param(_photo_row_without_file, {"eksik_alanli_foto": 1}, id="file-yok"),
    pytest.param(_photo_row_without_id, {"eksik_alanli_foto": 1}, id="photo_id-yok"),
])
def test_each_finding_alone_exits_one(temiz, capsys, damage, finding):
    """Cikis 1 her bulgu turunde tek basina (temiz paket + tek bozulma); toplu fikstur bunu ayirt etmez."""
    out, pkg = temiz
    damage(out, pkg)
    code, result = run(capsys, "hazirla", out, pkg)
    assert found(result) == {**NO_FINDINGS, **finding}, result  # yalniz bu bulgu
    assert code == 1


def test_photo_rows_without_id_or_file_are_findings_not_input_errors(paket, capsys):
    """xlsx_dump bos hucreyi yazmaz: photo_id/file'i olmayan satir paket kusurudur (bulgu); adim durmaz."""
    out, pkg = paket
    old = stale_files(out)
    append_rows(out / "_dump" / "Fotoğraflar.jsonl", [NO_FILE_ROW, NO_ID_ROW])
    add_dup_group(out, {"sha256": "99", "files": ["Fotoğraflar/h1.jpg", "Fotoğraflar/m9.jpg"]})
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 1 and result["eksik_alanli_foto"] == 2, result
    assert list(result) == ["ters_egik_cizgi", "kanit_dosyasi", "kanitsiz_foto", "ayni_sha", "eksik_alanli_foto",
                            "ayrinti"]
    assert [p.exists() for p in old] == [False, False, False]  # adim tamamlandi
    detail = read_json(out / "_foto" / "hazirlik.json")
    assert detail["eksik_alanli_foto"] == [{"excel_row": 20, "eksik": ["file"]}, {"excel_row": 21, "eksik": ["photo_id"]}]
    assert [item["key"] for item in read_items(out)] == [item[0] for item in EXPECTED_ITEMS]  # paftaya girmez
    # dosyasi olan satir ayni SHA eslemesinde kalir: m9.jpg bir satira bagli, artik (K05) degil
    assert detail["ayni_sha"] == {**EXPECTED_DUP, "K63": [*EXPECTED_DUP["K63"], ["Fotoğraflar/h1.jpg", "Fotoğraflar/m9.jpg"]]}


def _drop_sheet(name: str) -> Callable[[Path, Path], None]:
    def damage(out: Path, pkg: Path) -> None:
        (out / "_dump" / f"{name}.jsonl").unlink()
    return damage


def _broken_dump_line(out: Path, pkg: Path) -> None:
    with (out / "_dump" / "Fotoğraflar.jsonl").open("a", encoding="utf-8") as stream:
        stream.write("{bozuk\n")


def _drop_inventory(out: Path, pkg: Path) -> None:
    (out / "dosya-envanteri.json").unlink()


def _inventory_without_dup_sha(out: Path, pkg: Path) -> None:
    (out / "dosya-envanteri.json").write_text(json.dumps({"findings": {}}), encoding="utf-8")


def _drop_package(out: Path, pkg: Path) -> None:
    shutil.rmtree(pkg)


@pytest.mark.parametrize("damage, message", [  # sekme adlari sabit: script'in listesinden turetilmez
    pytest.param(_drop_sheet("Kanıtlar"), "Kanıtlar.jsonl", id="kanitlar-yok"),
    pytest.param(_drop_sheet("Fotoğraflar"), "Fotoğraflar.jsonl", id="fotograflar-yok"),
    pytest.param(_drop_sheet("Mekânlar"), "Mekânlar.jsonl", id="mekanlar-yok"),
    pytest.param(_drop_sheet("Mahalleler"), "Mahalleler.jsonl", id="mahalleler-yok"),
    pytest.param(_broken_dump_line, "Fotoğraflar.jsonl satir 7", id="bozuk-dump-satiri"),
    pytest.param(_drop_inventory, "dosya-envanteri.json", id="envanter-yok"),
    pytest.param(_inventory_without_dup_sha, "dup_sha", id="dup_sha-yok"),
    pytest.param(_drop_package, "paket klasoru yok", id="paket-yok"),
])
def test_input_errors_exit_two_before_anything_is_deleted(paket, capsys, damage, message):
    out, pkg = paket
    old = stale_files(out)
    damage(out, pkg)
    code, result = run(capsys, "hazirla", out, pkg)
    assert code == 2 and message in result["error"], result
    assert all(p.exists() for p in old), "girdi hatasinda onceki kosunun dosyalari silinmemeli"
    assert not (out / "_foto" / "items.jsonl").exists() and not (out / "_foto" / "hazirlik.json").exists()


@pytest.mark.parametrize("pairs_text, message", [
    (None, "dhash.json"), ("{}", "pairs"), ('{"pairs": [{"a": "x:photo:m1"}]}', "pairs"), ("[", "dhash.json"),
])
def test_ciftler_input_errors_exit_two(paket, capsys, pairs_text, message):
    out, pkg = paket
    if pairs_text is not None:
        (out / "temas-sayfalari").mkdir()
        (out / "temas-sayfalari" / "dhash.json").write_text(pairs_text, encoding="utf-8")
    code, result = run(capsys, "ciftler", out)
    assert code == 2 and message in result["error"], result
    assert not (out / "_foto" / "dhash-ciftleri.json").exists()


def test_ciftler_needs_the_photo_dump(paket, capsys):
    out, _ = paket
    write_pairs(out, PAIRS)
    (out / "_dump" / "Fotoğraflar.jsonl").unlink()
    code, result = run(capsys, "ciftler", out)
    assert code == 2 and "Fotoğraflar.jsonl" in result["error"]


def test_ciftler_creates_its_output_folder(paket, capsys):  # _foto yoksa da yazar (hazirla'ya bagli degil)
    out, _ = paket
    write_pairs(out, PAIRS)
    code, result = run(capsys, "ciftler", out)
    assert code == 1 and read_json(out / "_foto" / "dhash-ciftleri.json") == result


# ------------------------------------------------------------------ paket salt okunur

def test_package_is_never_written(paket, capsys):
    out, pkg = paket
    before = snapshot(pkg)
    run(capsys, "hazirla", out, pkg)
    write_pairs(out, PAIRS)
    run(capsys, "ciftler", out)
    assert snapshot(pkg) == before


def test_out_inside_the_package_is_refused(paket, capsys):
    out, pkg = paket
    inside = pkg / "denetim"
    shutil.copytree(out, inside)  # girdiler tam: ret yalniz konumdan gelir
    before = snapshot(pkg)
    code, result = run(capsys, "hazirla", inside, pkg)
    assert code == 2 and "paket" in result["error"], result
    assert snapshot(pkg) == before
    code, result = run(capsys, "hazirla", pkg, pkg)
    assert code == 2 and "paket" in result["error"], result
    assert snapshot(pkg) == before


@pytest.mark.parametrize("folder", ["temas-sayfalari", "_foto", "_foto/kanit"])
def test_package_inside_a_cleared_folder_is_refused(paket, capsys, folder):
    out, pkg = paket
    moved = out / folder / "paket"
    shutil.copytree(pkg, moved)
    before = snapshot(moved)
    code, result = run(capsys, "hazirla", out, moved)
    assert code == 2 and "paket" in result["error"], result
    assert snapshot(moved) == before


# ------------------------------------------------------------------ tuketiciler ve komut satiri

def test_outputs_are_read_by_their_consumers(paket, capsys):
    out, pkg = paket
    run(capsys, "hazirla", out, pkg)
    candidates, errors = photo_candidates.load_evidence_dir(out / "_foto" / "kanit")  # from-evidence ile ayni okuma
    assert errors == [] and [(c["photo_id"], c["license"]) for c in candidates] == [("x:photo:m1", "CC BY-SA 4.0")]
    rows = contact_sheet.read_items(out / "_foto" / "items.jsonl")
    assert [r["key"] for r in rows] == [item[0] for item in EXPECTED_ITEMS]


def test_runs_from_the_command_line_without_utf8_mode(paket):
    out, pkg = paket
    env = {key: value for key, value in os.environ.items() if key not in ("PYTHONUTF8", "PYTHONIOENCODING")}
    proc = subprocess.run([sys.executable, str(SCRIPT), "hazirla", str(out), str(pkg)], capture_output=True,
                          env={**env, "PYTHONDONTWRITEBYTECODE": "1"}, text=True, encoding="utf-8", check=False)
    assert proc.returncode == 1, proc.stderr[-2000:]
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["ters_egik_cizgi"] == dict(EXPECTED_SCAN)


# ------------------------------------------------------------------ city-audit SKILL.md

def skill_calls() -> list[tuple[str, list[str], int]]:
    text = sc.SKILLS["city-audit"].read_text(encoding="utf-8")
    return [(c.script, c.args.split(), c.line) for c in sc.extract_commands("city-audit", text) if c.kind == "tk"]


def test_city_audit_skill_calls_the_script_instead_of_embedded_python():
    text = sc.SKILLS["city-audit"].read_text(encoding="utf-8")
    assert "& $PY -c" not in text and "@'" not in text, "gomulu Python kalmamali"
    assert "taşınacak" not in text
    calls = skill_calls()
    prep = [(args, line) for script, args, line in calls if script == "audit_prep"]
    assert [args for args, _ in prep] == [["hazirla", "$OUT", "$PKG"], ["ciftler", "$OUT"]]
    (_, hazirla), (_, ciftler) = prep
    first = {script: line for script, _, line in reversed(calls)}
    evidence = next(line for script, args, line in calls if script == "photo_candidates" and args[0] == "from-evidence")
    assert first["xlsx_dump"] < hazirla and first["inventory"] < hazirla  # girdiler once uretilir
    assert hazirla < evidence < first["contact_sheet"] < ciftler  # ciftler contact_sheet'in dhash.json'unu okur
    lines = text.splitlines()
    copy = next(n for n, line in enumerate(lines, start=1) if line.startswith("Copy-Item -LiteralPath $XLSX"))
    assert hazirla < copy < evidence, "Excel kopyasi hazirla temizledikten sonra, from-evidence'tan once"


def test_skill_stops_the_photo_block_when_hazirla_exits_two():
    """Blok tek PowerShell cagrisi: cikis 2'de (girdi hatasi, kilitli dosya) sonraki adimlar eski dosyalarla calismaz."""
    lines = sc.SKILLS["city-audit"].read_text(encoding="utf-8").splitlines()
    hazirla = next(line for script, args, line in skill_calls() if script == "audit_prep" and args[0] == "hazirla")
    guard = lines[hazirla]  # hazirla'dan hemen sonraki satir (satir numarasi 1 tabanli)
    assert guard.replace(" ", "").startswith("if($LASTEXITCODE-eq2){throw"), guard


def test_skill_paths_match_the_script_layout():
    calls = skill_calls()
    sheet = next(args for script, args, _ in calls if script == "contact_sheet")
    assert sheet[sheet.index("--items") + 1] == rf"$OUT\{audit_prep.PREP_DIR}\{audit_prep.ITEMS_NAME}"
    assert sheet[sheet.index("--out-dir") + 1] == rf"$OUT\{audit_prep.SHEETS_DIR}"
    evidence = next(args for script, args, _ in calls if script == "photo_candidates" and args[0] == "from-evidence")
    assert evidence[1] == rf"$OUT\{audit_prep.PREP_DIR}\{audit_prep.EVIDENCE_DIR}"
    dump = next(args for script, args, _ in calls if script == "xlsx_dump")
    assert dump[dump.index("--out-dir") + 1] == rf"$OUT\{audit_prep.DUMP_DIR}"
    inventory = next(args for script, args, _ in calls if script == "inventory")
    assert inventory[inventory.index("--out") + 1] == rf"$OUT\{audit_prep.INVENTORY_NAME}"
