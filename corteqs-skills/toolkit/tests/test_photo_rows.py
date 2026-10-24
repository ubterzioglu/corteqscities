"""photo_rows: indirme plani + Fotoğraflar/Kanıtlar/FotoğrafKaynakları satirlari (A6; pilot foto_satirlari.py).

Lisans/kaynak zinciri kurallari resmi araclardan (--tools) gelir: 'real' testler gercek araclar/arac kopyasini salt
okunur kullanir (yoksa atlanir); yukleyici ve plan akisi ayrica sahte (stub) arac klasoruyle hermetik test edilir.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

import download_plan as dp
import merge_package as mp
import photo_previews as pp
import photo_rows as pr
import text_quality as tq

ARAC = Path(r"C:\temp_private\corteqs\0000_newera\araclar\arac")
needs_tools = pytest.mark.skipif(not (ARAC / "provenance.py").is_file(), reason="gercek araclar/arac klasoru yok")
CITY = "testville"
COMMONS = "https://commons.wikimedia.org/wiki/File:"
UPLOAD = "https://upload.wikimedia.org/wikipedia/commons/a/ab"
THUMB = "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab"


def cand(cid: str, name: str, width: int, **extra) -> dict:
    height = width * 3 // 4 if isinstance(width, int) else 0
    base = {"candidate_id": cid, "title": name, "width": width, "height": height, "license": "CC BY-SA 4.0",
            "license_url": "http://creativecommons.org/licenses/by-sa/4.0", "usage_terms": "Creative Commons",
            "author_text": " Jan   Jansen ", "restrictions": "", "date_original": "2019-01-20 10:50:00",
            "source_url": COMMONS + name, "original_url": f"{UPLOAD}/{name}?utm_source=x",
            "thumb_url": f"{THUMB}/{name}/1600px-{name}?utm_source=x", "commons_file": "File:" + name.replace("_", " ")}
    return {**base, **extra}


GOOD = [cand("k1", "Van_Abbe_1.jpg", 4000),
        cand("k2", "Van_Abbe_2.jpg", 1000, license="CC BY 4.0", license_url="https://creativecommons.org/licenses/by/4.0/"),
        cand("k3", "Skyline.jpg", 2000, license="CC0", license_url="")]
SELECTED = [{"key": "k1", "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": "Müze binası", "seen": "Gri bina"},
            {"key": "k2", "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": "Giriş", "seen": "Giriş kapısı"},
            {"key": "k3", "entry_id": "", "role": "Kapak", "caption": "Şehir silueti", "seen": "Silüet"}]


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def search_rows(cands: list[dict]) -> list[dict]:
    artist = '<a href="https://commons.wikimedia.org/wiki/User:Jan">Jan Jansen</a>'
    return [{"entry_id": "x", "title": c["commons_file"],
             "imageinfo": {"descriptionurl": c["source_url"], "url": c["original_url"].split("?")[0],
                           "extmetadata": {"Artist": {"value": artist if c["candidate_id"] == "k1" else "Jan"}}}}
            for c in cands]


def make_work(tmp_path: Path, cands: list[dict] = GOOD, selected: list[dict] = SELECTED) -> tuple[Path, Path]:
    work = tmp_path / "is"
    write_jsonl(work / "foto" / "candidates.jsonl", cands)
    write_jsonl(work / "foto" / "selected.jsonl", selected)
    write_jsonl(work / "foto" / "search.jsonl", search_rows(cands))
    write_jsonl(work / "data" / "Mekânlar.jsonl", [{"entry_id": f"{CITY}:van-abbe", "slug": "van-abbe", "title": "Van Abbe"}])
    write_jsonl(work / "data" / "Mahalleler.jsonl", [{"entry_id": f"{CITY}:centrum", "slug": "centrum", "title": "Centrum"}])
    package = tmp_path / "paket"
    (package / "Teslimler").mkdir(parents=True)
    return work, package


def fake_download(work: Path, package: Path, broken: set[str] = frozenset(), skip: set[str] = frozenset(),
                  size: tuple[int, int] = (1280, 960)) -> None:
    """Atinc download_media.py yerine: plana gore gercek JPEG yazar (ayni adres = ayni bayt, gercekteki gibi) ve
    download-progress-v7.json uretir."""
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    progress = []
    for row in plan:
        if row["photo_id"] in skip:
            continue
        path = package / row["original_file"]
        path.parent.mkdir(parents=True, exist_ok=True)
        color = tuple(hashlib.sha256(row["downloaded_file_url"].encode("utf-8")).digest()[:3])
        Image.new("RGB", size, color).save(path, format="JPEG")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        progress.append({**row, "downloaded_on": "2026-10-21", "sha256": "0" * 64 if row["photo_id"] in broken else digest,
                         "original_sha256": digest})
    (package / "Teslimler" / "download-progress-v7.json").write_text(json.dumps(progress), encoding="utf-8")


def run(capsys, *args) -> tuple[int, dict | None]:
    code = pr.main([str(a) for a in args])
    lines = capsys.readouterr().out.strip().splitlines()
    return code, (json.loads(lines[-1]) if lines else None)


def official_audit(package: Path, photos: list[dict], prov: list[dict]) -> dict:
    before = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ARAC))
    try:
        import delivery_tools  # resmi dogrulayici; araclar klasorune bayt kodu yazilmaz
    finally:
        sys.path.remove(str(ARAC))
        sys.dont_write_bytecode = before
    return delivery_tools.audit(package.resolve(), photos, prov, require_new_chain=True)


WINDOWS_STUB = {  # resmi araclarin Windows ciktisi gibi: create_web_copy yollari '\' ile dondurur (L0 ISS-004)
    "provenance.py": ("def extract(photo, evidence):\n"
                      "    return {'photo_id': photo['photo_id'], 'original_file': photo['file'], 'web_file': ''}\n"),
    "delivery_tools.py": ("def create_web_copy(root, row):\n"
                          "    return {**row, 'original_file': row['original_file'].replace('/', '\\\\'),\n"
                          "            'web_file': 'Teslimler\\\\WebKopyalari\\\\abc.webp'}\n"),
}


def make_stub_tools(root: Path, overrides: dict[str, str] | None = None) -> Path:
    files = {
        "core/__init__.py": "",
        "core/content_delivery/__init__.py": "",
        "core/content_delivery/delivery_values.py": "import re\nCC = re.compile(r'CC (BY(?:-SA)?) (4\\.0)\\Z', re.I)\n",
        "core/content_delivery/validation_media.py": (
            "def official_cc_url(url, path):\n    return url.startswith('https://creativecommons.org/')\n"
            "def cc_license_matches(label, url):\n    return url.startswith('https://creativecommons.org/licenses/')\n"),
        "provenance.py": "def extract(photo, evidence):\n    return {'photo_id': photo['photo_id'], 'stub': True}\n",
        "delivery_tools.py": "def create_web_copy(root, row):\n    return {**row, 'web_file': 'stub.webp'}\n",
        **(overrides or {}),
    }
    for relative, text in files.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


# ---------------------------------------------------------------- arac yukleyici (hermetik)

def test_load_tools_imports_without_bytecode_and_restores_interpreter_state(tmp_path):
    stub = make_stub_tools(tmp_path / "arac")
    before_flag, before_path = sys.dont_write_bytecode, list(sys.path)
    sys.dont_write_bytecode = False
    try:
        tools = pr.load_tools(stub)
        assert sys.dont_write_bytecode is False and sys.path == before_path
    finally:
        sys.dont_write_bytecode = before_flag
    assert tools.extract({"photo_id": "p"}, {}) == {"photo_id": "p", "stub": True}
    assert pr.norm_license(tools, "cc by 4.0", "http://creativecommons.org/licenses/by/4.0", "s") == (
        "cc by 4.0", "https://creativecommons.org/licenses/by/4.0/")
    page = COMMONS + "X.jpg"
    assert pr.norm_license(tools, "PD", "", page) == ("Public domain", page)
    assert pr.norm_license(tools, "Public domain", "", "") is None  # dayanak sayfasi yoksa kabul yok
    assert pr.norm_license(tools, "GFDL", "https://www.gnu.org/", page) is None
    assert not list(stub.rglob("__pycache__")) and not list(stub.rglob("*.pyc"))


def test_plan_runs_with_any_tools_folder(tmp_path, capsys):
    stub = make_stub_tools(tmp_path / "arac")
    work, _ = make_work(tmp_path, GOOD[:2], SELECTED[:2])
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    assert code == pr.EXIT_OK and (summary["selected"], summary["planned"], summary["dropped"]) == (2, 2, 0)


def test_broken_tools_folder_is_usage_error(tmp_path, capsys):
    stub = make_stub_tools(tmp_path / "arac")
    (stub / "provenance.py").write_text("def extract(:\n", encoding="utf-8")
    work, _ = make_work(tmp_path)
    assert pr.main(["plan", str(work), "--city-id", CITY, "--tools", str(stub)]) == pr.EXIT_USAGE


def test_usage_errors_exit_2(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("CORTEQS_TOOLS", raising=False)
    work, package = make_work(tmp_path)
    stub = make_stub_tools(tmp_path / "arac")
    assert pr.main(["plan", str(work), "--city-id", CITY]) == pr.EXIT_USAGE  # --tools yok
    assert pr.main(["plan", str(work), "--city-id", CITY, "--tools", str(tmp_path / "bos")]) == pr.EXIT_USAGE
    assert pr.main(["plan", str(work), "--city-id", "Bad City", "--tools", str(stub)]) == pr.EXIT_USAGE
    assert pr.main(["plan", str(tmp_path / "yok"), "--city-id", CITY, "--tools", str(stub)]) == pr.EXIT_USAGE
    rows = ["rows", str(work), "--package", str(package), "--city-id", CITY, "--tools", str(stub)]
    assert pr.main([*rows, "--date", "2026-13-01"]) == pr.EXIT_USAGE
    assert pr.main(rows) == pr.EXIT_USAGE  # plan calismadi: secim_temiz / download-progress yok
    assert pr.main(["rows", str(work), "--city-id", CITY, "--tools", str(stub)]) == pr.EXIT_USAGE  # --package zorunlu
    assert pr.main([]) == pr.EXIT_USAGE and pr.main(["--help"]) == pr.EXIT_OK
    capsys.readouterr()
    (work / "foto" / "selected.jsonl").write_bytes('{"caption": "Müze"}\n'.encode("cp1252"))  # UTF-8 degil
    assert pr.main(["plan", str(work), "--city-id", CITY, "--tools", str(stub)]) == pr.EXIT_USAGE
    assert "selected.jsonl: UTF-8 degil" in capsys.readouterr().err


# ---------------------------------------------------------------- teslim adresi (hermetik)

def test_plan_url_rule_is_download_plans_and_never_takes_another_files_thumb(tmp_path, capsys):
    """K81 (incelenen kare = teslim edilen kare): thumb_url baska dosyanin kopyasiysa o kare bu karenin lisans ve yazar
    bilgisiyle inmez, ozgun dosyaya dusulur. Kural download_plan --prefer-thumb ile ayni; .jpeg -> .jpg."""
    other_dir = THUMB.replace("/a/ab", "/c/cd")
    cands = [cand("k1", "Van_Abbe_1.jpg", 4000),  # ayni dosyanin thumb'i: 1280 px kopya
             cand("k2", "Van_Abbe_2.jpg", 4000, thumb_url=f"{THUMB}/Baska.jpg/1600px-Baska.jpg"),  # baska dosya
             cand("k3", "Van_Abbe_3.jpg", 4000, thumb_url=f"{other_dir}/Van_Abbe_3.jpg/1600px-Van_Abbe_3.jpg"),  # baska dizin
             cand("k4", "Gevel.jpeg", 900),  # dar: ozgun dosya, uzanti .jpg
             cand("k5", "Plein.png", 4000, thumb_url=f"{THUMB}/Plein.png/1600px-Plein.png.jpg"),  # thumb bicimi farkli
             cand("k6", "Toren.jpg", "4000", thumb_url=THUMB.replace("https:", "http:") + "/Toren.jpg/1600px-Toren.jpg")]
    selected = [{"key": c["candidate_id"], "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": c["title"]}
                for c in cands]
    work, _ = make_work(tmp_path, cands, selected)
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", make_stub_tools(tmp_path / "arac"))
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    assert code == pr.EXIT_OK and summary["planned"] == 6
    assert [p["downloaded_file_url"] for p in plan] == [
        f"{THUMB}/Van_Abbe_1.jpg/1280px-Van_Abbe_1.jpg", f"{UPLOAD}/Van_Abbe_2.jpg", f"{UPLOAD}/Van_Abbe_3.jpg",
        f"{UPLOAD}/Gevel.jpeg", f"{UPLOAD}/Plein.png", f"{UPLOAD}/Toren.jpg"]
    assert plan[3]["original_file"] == f"Fotoğraflar/{CITY}_van-abbe_04.jpg" and plan[4]["original_file"].endswith(".png")
    rows = [{"photo_id": p["photo_id"], "slug": "van-abbe", **{k: c[k] for k in ("original_url", "thumb_url", "width")}}
            for p, c in zip(plan, cands)]
    reference, errors, _ = dp.build_plan_detail(rows, CITY, prefer_thumb=True)
    assert errors == [] and reference == plan  # iki plan ureticisi ayni karari verir


UT = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab"  # eski bicim: upload alaninda thumb klasoru


def test_plan_never_plans_a_wide_or_nonstandard_original_thumb(tmp_path, capsys):
    """Wikimedia 2026 yalniz standart genislikleri verir (1600 px = HTTP 400). Adayin original_url'i 1600 px (ya da
    1280'den genis) thumb ise o adres plana girmez: ayni dosyanin ozgun adresine cevrilir, teslim kurali (1280 px)
    ondan uygulanir ve raporlanir. thumb_url bos ya da kullanilamazsa 1280 px kopya verilen thumb'dan turetilir (ayni
    dosya olusu dogrulandi; tam boy ozgun dosya inmez). Ozgun adresi cikarilamayan ya da bicimi desteklenmeyen kare
    atilir; gerekcede verilen adres de yazar. Kural download_plan --prefer-thumb ile ayni."""
    tif_given = f"{UT}/Plan_4.tif/lossy-page1-1600px-Plan_4.tif.jpg"
    cands = [cand("k1", "Van_Abbe_1.jpg", 4000, original_url=f"{UT}/Van_Abbe_1.jpg/1600px-Van_Abbe_1.jpg?utm_source=x"),
             cand("k2", "Van_Abbe_2.jpg", 4000, original_url=f"{THUMB}/Van_Abbe_2.jpg/1600px-Van_Abbe_2.jpg",
                  thumb_url=""),
             cand("k3", "Van_Abbe_3.jpg", 4000,
                  original_url="https://upload.wikimedia.org/wikipedia/commons/thumb/Van_Abbe_3.jpg/1600px-Van_Abbe_3.jpg"),
             cand("k4", "Plan_4.tif", 4000, original_url=tif_given, thumb_url="")]  # ozgun tif: bicim desteklenmez
    selected = [{"key": c["candidate_id"], "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": "x"} for c in cands]
    work, _ = make_work(tmp_path, cands, selected)
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", make_stub_tools(tmp_path / "arac"),
                        "--out", tmp_path / "rapor.json")
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "rapor.json").read_text(encoding="utf-8"))
    assert [p["downloaded_file_url"] for p in plan] == [f"{THUMB}/Van_Abbe_1.jpg/1280px-Van_Abbe_1.jpg",
                                                        f"{THUMB}/Van_Abbe_2.jpg/1280px-Van_Abbe_2.jpg"]
    assert code == pr.EXIT_FINDINGS and (summary["planned"], summary["dropped"]) == (2, 2)
    assert summary["original_thumb_fixed"] == 2 and "/1600px-" not in json.dumps(plan)
    assert report["dropped"][0][0] == "k3" and "1600 px" in report["dropped"][0][1]
    assert report["dropped"][1] == ["k4", f"desteklenmeyen dosya turu: .tif ({tif_given} thumb'inin ozgun dosyasi)"]
    assert [(key, new) for key, _old, new in report["original_thumb_fixed"]] == [
        ("k1", f"{UPLOAD}/Van_Abbe_1.jpg"), ("k2", f"{UPLOAD}/Van_Abbe_2.jpg")]
    no_url = {**cands[0], "candidate_id": "k4", "original_url": None}  # adres yok: thumb gerekcesi verilmez
    sel = {"key": "k4", "entry_id": f"{CITY}:van-abbe", "role": "Mekân"}
    tools = pr.load_tools(make_stub_tools(tmp_path / "arac2"))
    assert pr.check_selection(tools, sel, {"k4": no_url}, {f"{CITY}:van-abbe": "van-abbe"}) == (
        None, "indirme adresi izinli degil")
    rows = [{"photo_id": p["photo_id"], "slug": "van-abbe", **{k: c[k] for k in ("original_url", "thumb_url", "width")}}
            for p, c in zip(plan, cands)]
    reference, errors, _ = dp.build_plan_detail(rows, CITY, prefer_thumb=True)
    assert errors == [] and reference == plan  # iki plan ureticisi ayni karari verir


# ---------------------------------------------------------------- ek tur klasorleri (A12, hermetik)

EXTRA = cand("e1", "Yeni_Yer.jpg", 3000)  # ek turda bulunan yeni mekanin karesi (foto_ek/)


def make_extra_round(tmp_path: Path) -> tuple[Path, Path]:
    """Ana tur foto/ (k1) + ek tur foto_ek/ (e1 ve k1'in lisansi farkli ikinci kaydi: ana tur onde gelir)."""
    selected = [SELECTED[0], {"key": "e1", "entry_id": f"{CITY}:yeni-yer", "role": "Mekân", "caption": "Yeni yer"}]
    work, package = make_work(tmp_path, GOOD[:1], selected)
    write_jsonl(work / "data" / "Mekânlar.jsonl", [{"entry_id": f"{CITY}:van-abbe", "slug": "van-abbe"},
                                                  {"entry_id": f"{CITY}:yeni-yer", "slug": "yeni-yer"}])
    nonfree = {**GOOD[0], "license": "CC BY-NC 4.0", "license_url": "https://creativecommons.org/licenses/by-nc/4.0/"}
    write_jsonl(work / "foto_ek" / "candidates.jsonl", [EXTRA, nonfree])
    write_jsonl(work / "foto_ek" / "search.jsonl", search_rows([EXTRA]))
    return work, package


def test_plan_and_rows_read_extra_round_folders(tmp_path, capsys):
    """A12: ek foto turu ayri klasorde (<is>/foto_ek/: kendi candidates/search'u). Ana tur ve foto_*/ klasorlerinin
    aday ve ham arama kayitlari birlikte okunur; ayni kimlikte ana tur onde gelir (sonraki kayit yok sayilir)."""
    work, package = make_extra_round(tmp_path)
    stub = make_stub_tools(tmp_path / "arac")
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    assert code == pr.EXIT_OK and (summary["planned"], summary["dropped"]) == (2, 0)
    assert summary["candidate_files"] == ["foto/candidates.jsonl", "foto_ek/candidates.jsonl"]
    assert [p["photo_id"] for p in plan] == [f"{CITY}:photo:van-abbe-01", f"{CITY}:photo:yeni-yer-01"]
    clean = read_jsonl(work / "foto" / "secim_temiz.jsonl")
    assert clean[0]["license"] == "CC BY-SA 4.0"  # ana turun kaydi (ek turdaki NC kaydi degil)
    fake_download(work, package)
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", stub)
    assert code == pr.EXIT_OK and summary["photos"] == 2 and summary["entries_with_photo"] == 2
    assert summary["search_files"] == ["foto/search.jsonl", "foto_ek/search.jsonl"]
    evidence = read_jsonl(work / "data" / "parcalar" / "Kanıtlar.foto.jsonl")
    raw = json.loads(evidence[1]["source_evidence_json"])["original_api_record"]
    assert raw["descriptionurl"] == EXTRA["source_url"]  # ek turun ham arama kaydi


def test_explicit_candidate_and_search_files_replace_the_folder_scan(tmp_path, capsys):
    work, package = make_extra_round(tmp_path)
    stub = make_stub_tools(tmp_path / "arac")
    main = work / "foto" / "candidates.jsonl"
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub, "--candidates", main,
                        "--out", tmp_path / "r.json")
    dropped = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))["dropped"]
    assert code == pr.EXIT_FINDINGS and summary["planned"] == 1 and dropped == [["e1", "aday yok"]]
    extra = work / "foto_ek" / "candidates.jsonl"
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub, "--candidates", extra,
                        "--candidates", main)
    clean = read_jsonl(work / "foto" / "secim_temiz.jsonl")
    assert code == pr.EXIT_FINDINGS and summary["planned"] == 1 and summary["dropped"] == 1  # k1: ek turun NC kaydi
    assert [c["key"] for c in clean] == ["e1"]
    code, _ = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    fake_download(work, package)
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", stub,
                        "--search", work / "foto" / "search.jsonl")
    evidence = read_jsonl(work / "data" / "parcalar" / "Kanıtlar.foto.jsonl")
    assert code == pr.EXIT_OK and summary["search_files"] == ["foto/search.jsonl"]
    assert json.loads(evidence[1]["source_evidence_json"])["original_api_record"] == {}  # ek tur aramasi verilmedi
    assert pr.main(["plan", str(work), "--city-id", CITY, "--tools", str(stub), "--candidates",
                    str(work / "yok.jsonl")]) == pr.EXIT_USAGE


def image_transport(url, headers, timeout):
    return 200, {"Content-Type": "image/jpeg"}, b"\xff\xd8\xff\xe0" + b"\x00" * 16


def test_extra_round_outside_the_foto_star_convention_needs_explicit_candidates(tmp_path, capsys):
    """A12 sozlesmesi: photo_rows ve photo_previews ayni tarama kuralini kullanir (ana tur foto/, ek turlar foto_*/);
    photo_previews ayrica karar dosyasinin klasorunu okur (pilot foto_onizleme). Ek tur bu duzenin disindaysa (or.
    <is>/foto/ek16/) onizleme adaylari bulur, photo_rows bulmaz: kare 'aday yok' ile atilir, cikis 1 (sessiz degil),
    ozetteki candidate_files okunanlari gosterir; --candidates ile (ana dosya dahil) kare planlanir."""
    work, _ = make_extra_round(tmp_path)  # foto/ (k1) + foto_ek/ (e1); e1 ek16'ya tasinir
    write_jsonl(work / "foto_ek" / "candidates.jsonl", [cand("x1", "Baska_Yer.jpg", 3000)])  # duzene uyan baska tur
    side = work / "foto" / "ek16"
    write_jsonl(side / "candidates.jsonl", [EXTRA])
    (side / "decisions.json").write_text(json.dumps({"decisions": [], "shortlists": {f"{CITY}:yeni-yer": ["e1"]}}),
                                         encoding="utf-8")
    code = pp.main([str(work), "--decisions", str(side / "decisions.json"), "--items-out", str(side / "items.jsonl"),
                    "--preview-dir", str(tmp_path / "onizleme")], transport=image_transport, sleep=lambda s: None)
    previews = json.loads(capsys.readouterr().out.strip().splitlines()[-1])
    assert code == pp.EXIT_OK and previews["items"] == 1
    assert previews["candidate_files"] == ["foto/candidates.jsonl", "foto_ek/candidates.jsonl",
                                           "foto/ek16/candidates.jsonl"]
    stub = make_stub_tools(tmp_path / "arac")
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub, "--out", tmp_path / "r.json")
    assert summary["candidate_files"] == previews["candidate_files"][:2]  # ortak kisim ayni dosyalar, ayni sira
    assert code == pr.EXIT_FINDINGS and summary["status"] == "findings" and summary["planned"] == 1
    assert json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))["dropped"] == [["e1", "aday yok"]]
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", stub, "--candidates",
                        work / "foto" / "candidates.jsonl", "--candidates", side / "candidates.jsonl")
    assert code == pr.EXIT_OK and (summary["planned"], summary["dropped"]) == (2, 0)


# ---------------------------------------------------------------- mekan kaydi olmayan kare (hermetik)

def test_venue_photo_without_merged_entry_is_dropped_and_reported_not_named_kapak(tmp_path, capsys):
    """Pilot: yeni mekan data/'ya birlestirilmeden plan yapilinca kare sessizce 'kapak-NN' adini aliyordu. Mekan rolunde
    slug yoksa (ya da slug kapak karelerinin adi 'kapak' ise) kare atilir, kayit kimligi ozette ve raporda gorunur
    (once merge_package); kapak numaralari kaymaz."""
    selected = [{"key": "k1", "entry_id": f"{CITY}:yeni-mekan", "role": "Mekân", "caption": "x"},
                {"key": "k2", "entry_id": f"{CITY}:kapak-mekan", "role": "Mekân", "caption": "x"},
                {"key": "k3", "entry_id": "", "role": "Kapak", "caption": "y"}]
    work, _ = make_work(tmp_path, GOOD, selected)
    write_jsonl(work / "data" / "Mekânlar.jsonl", [{"entry_id": f"{CITY}:van-abbe", "slug": "van-abbe"},
                                                  {"entry_id": f"{CITY}:kapak-mekan", "slug": "kapak"}])
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", make_stub_tools(tmp_path / "arac"),
                        "--out", tmp_path / "rapor.json")
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    reasons = dict(json.loads((tmp_path / "rapor.json").read_text(encoding="utf-8"))["dropped"])
    assert code == pr.EXIT_FINDINGS and [p["photo_id"] for p in plan] == [f"{CITY}:photo:kapak-01"]
    assert summary["missing_entries"] == [f"{CITY}:yeni-mekan"]
    assert reasons["k1"].startswith(f"mekan kaydi yok: {CITY}:yeni-mekan") and "merge_package" in reasons["k1"]
    assert "kapak" in reasons["k2"] and reasons["k2"].startswith("slug ayrilmis")


def test_venue_with_empty_or_invalid_slug_is_dropped_but_not_listed_as_missing_entry(tmp_path, capsys):
    """data/'da kaydi olan ama slug'i bos, alani hic olmayan ya da gecersiz mekanin karesi atilir ('mekan slug'i
    gecersiz'), kapak adina dusmez; missing_entries yalniz data/'da kaydi olmayan kimliklerdir (once merge_package)."""
    selected = [{"key": "k1", "entry_id": f"{CITY}:bos", "role": "Mekân", "caption": "x"},
                {"key": "k2", "entry_id": f"{CITY}:alansiz", "role": "Mekân", "caption": "x"},
                {"key": "k3", "entry_id": f"{CITY}:buyuk", "role": "Mekân", "caption": "x"},
                {"key": "k3", "entry_id": "", "role": "Kapak", "caption": "y"}]
    work, _ = make_work(tmp_path, GOOD, selected)
    write_jsonl(work / "data" / "Mekânlar.jsonl", [{"entry_id": f"{CITY}:bos", "slug": ""},
                                                  {"entry_id": f"{CITY}:alansiz"},
                                                  {"entry_id": f"{CITY}:buyuk", "slug": "Van Abbe"}])
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", make_stub_tools(tmp_path / "arac"),
                        "--out", tmp_path / "rapor.json")
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    report = json.loads((tmp_path / "rapor.json").read_text(encoding="utf-8"))
    assert code == pr.EXIT_FINDINGS and [p["photo_id"] for p in plan] == [f"{CITY}:photo:kapak-01"]
    assert summary["missing_entries"] == [] == report["missing_entries"]
    assert report["dropped"] == [["k1", f"mekan slug'i gecersiz: {CITY}:bos ''"],
                                 ["k2", f"mekan slug'i gecersiz: {CITY}:alansiz ''"],
                                 ["k3", f"mekan slug'i gecersiz: {CITY}:buyuk 'Van Abbe'"]]


# ---------------------------------------------------------------- paket yollari (hermetik)

def test_rows_write_every_package_path_with_forward_slashes(tmp_path, capsys):
    """L0 ISS-004 (P1): Atinc'in create_web_copy'si yolu str(Path), Windows'ta '\\' ile dondurur; local_file yolu
    PurePosixPath ile okur, '\\'li yol Linux/Mac'te bulunamaz. Uc sekmenin paket yolu alanlari ('file', '*_file')
    araclar ya da secim dosyasi '\\' verse de '/' ile yazilir."""
    work, package = make_work(tmp_path, GOOD[:2], SELECTED[:2])
    stub = make_stub_tools(tmp_path / "arac", WINDOWS_STUB)
    run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    fake_download(work, package)
    clean_path = work / "foto" / "secim_temiz.jsonl"
    write_jsonl(clean_path, [{**c, "file": c["file"].replace("/", "\\")} for c in read_jsonl(clean_path)])
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", stub)
    parts = work / "data" / "parcalar"
    photos, evidence = read_jsonl(parts / "Fotoğraflar.foto.jsonl"), read_jsonl(parts / "Kanıtlar.foto.jsonl")
    prov = read_jsonl(parts / "FotoğrafKaynakları.foto.jsonl")
    assert code == pr.EXIT_OK and summary["photos"] == 2
    assert [p["file"] for p in photos] == [f"Fotoğraflar/{CITY}_van-abbe_01.jpg", f"Fotoğraflar/{CITY}_van-abbe_02.jpg"]
    assert [e["pixel_review_file"] for e in evidence] == [p["file"] for p in photos]
    assert [(p["original_file"], p["web_file"]) for p in prov] == [
        (photo["file"], "Teslimler/WebKopyalari/abc.webp") for photo in photos]
    paths = [value for row in photos + evidence + prov for key, value in row.items()
             if key == "file" or key.endswith("_file")]
    assert paths and not [value for value in paths if "\\" in str(value)]


# ---------------------------------------------------------------- degisiklik notu (hermetik)

def jpeg(path: Path, size: tuple[int, int], orientation: int | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    exif = Image.Exif()
    if orientation:
        exif[0x0112] = orientation
    Image.new("RGB", size, (90, 120, 150)).save(path, format="JPEG", exif=exif.tobytes())
    return path


def test_modification_note_is_built_from_the_downloaded_file(tmp_path):
    scaled = jpeg(tmp_path / "Fotoğraflar" / "testville_van-abbe_01.jpg", (1280, 853))
    digest = hashlib.sha256(scaled.read_bytes()).hexdigest()
    note = pr.modification_note(cand("k1", "Van_Abbe_1.jpg", 6000, height=4000),
                                f"{THUMB}/Van_Abbe_1.jpg/1280px-Van_Abbe_1.jpg", scaled)
    assert note == ("Wikimedia Commons'taki \"Van Abbe 1.jpg\" (6000×4000 px) özgün dosyasının 1280×853 px küçültülmüş "
                    "kopyası indirildi; kırpma, rötuş ve renk düzeltmesi yapılmadı. "
                    f"Teslim dosyası: testville_van-abbe_01.jpg (SHA-256 {digest[:12]}).")
    original = jpeg(tmp_path / "Fotoğraflar" / "testville_van-abbe_02.jpg", (1000, 750))
    note = pr.modification_note(cand("k2", "Van_Abbe_2.jpg", 1000, height=750), f"{UPLOAD}/Van_Abbe_2.jpg", original)
    assert note.startswith("Wikimedia Commons'taki \"Van Abbe 2.jpg\" özgün dosyası (1000×750 px) değiştirilmeden indirildi.")
    assert "önizleme" not in note
    rotated = jpeg(tmp_path / "r.jpg", (400, 300), orientation=6)  # EXIF 90 derece: Commons olcusu 300×400
    assert "özgün dosyası (300×400 px)" in pr.modification_note(cand("k3", "R.jpg", 300, height=400), f"{UPLOAD}/R.jpg",
                                                                rotated)
    unknown = pr.modification_note(cand("k4", "U.jpg", 0, height=0), f"{THUMB}/U.jpg/1280px-U.jpg", scaled)
    assert "\"U.jpg\" özgün dosyasının 1280×853 px küçültülmüş kopyası" in unknown  # ozgun olcu yoksa uydurulmaz


SERIES = [cand(f"s{n}", f"Speelpark_De_Splinter_(2025)_({n}).jpg", 6000, height=4000) for n in (10, 11, 12, 13)]


def test_rows_modifications_are_unique_and_not_flagged_by_text_quality(tmp_path, capsys):
    """Gercek kayitta 209 satirda 2 farkli not vardi (K27 kopya kumesi). Ayni dizinin numarali kareleri (ayni olcu, adda
    yalniz rakam farki) ve iki satirda secilen ayni dosya da text_quality'de kume uretmemeli."""
    selected = [{"key": c["candidate_id"], "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": f"Oyun {n}",
                 "seen": "x"} for n, c in enumerate(SERIES)]
    selected.append({"key": "s10", "entry_id": "", "role": "Kapak", "caption": "Kapak", "seen": "x"})
    work, package = make_work(tmp_path, SERIES, selected)
    stub = make_stub_tools(tmp_path / "arac")
    run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    fake_download(work, package, size=(1280, 853))
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", stub)
    photos = read_jsonl(work / "data" / "parcalar" / "Fotoğraflar.foto.jsonl")
    notes = [p["modifications"] for p in photos]
    assert code == pr.EXIT_OK and len(photos) == 5 and len(set(notes)) == 5
    assert all("(6000×4000 px) özgün dosyasının 1280×853 px küçültülmüş kopyası" in n for n in notes)
    sheets = {"Fotoğraflar": [{**p, "_row": 8 + i} for i, p in enumerate(photos)], "Şehir": [{"name": "Testville"}]}
    report = tq.analyze(sheets)
    clusters = [(kind, c["size"]) for kind in ("exact", "near", "template") for c in report[f"{kind}_duplicates"]
                if c["field"] == "modifications"]
    assert clusters == []


def test_rows_unreadable_downloaded_file_is_a_finding(tmp_path, capsys):
    work, package = make_work(tmp_path, GOOD[:2], SELECTED[:2])
    stub = make_stub_tools(tmp_path / "arac")
    run(capsys, "plan", work, "--city-id", CITY, "--tools", stub)
    fake_download(work, package)
    (package / "Fotoğraflar" / f"{CITY}_van-abbe_01.jpg").write_bytes(b"jpeg degil")
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", stub)
    assert code == pr.EXIT_FINDINGS and (summary["photos"], summary["errors"]) == (1, 1)
    assert summary["error_examples"][0]["photo_id"] == f"{CITY}:photo:van-abbe-01"


# ---------------------------------------------------------------- plan (gercek resmi araclarla)

@pytest.mark.real
@needs_tools
def test_plan_normalizes_licenses_numbers_photos_and_picks_delivery_url(tmp_path, capsys):
    work, _ = make_work(tmp_path)
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", ARAC)
    plan = json.loads((work / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
    clean = read_jsonl(work / "foto" / "secim_temiz.jsonl")
    assert code == pr.EXIT_OK and (summary["planned"], summary["dropped"]) == (3, 0)
    assert plan == [
        {"photo_id": f"{CITY}:photo:van-abbe-01", "original_file": f"Fotoğraflar/{CITY}_van-abbe_01.jpg",
         "downloaded_file_url": f"{THUMB}/Van_Abbe_1.jpg/1280px-Van_Abbe_1.jpg"},  # genis: 1280 px thumb
        {"photo_id": f"{CITY}:photo:van-abbe-02", "original_file": f"Fotoğraflar/{CITY}_van-abbe_02.jpg",
         "downloaded_file_url": f"{UPLOAD}/Van_Abbe_2.jpg"},  # dar: ozgun dosya, sorgusuz
        {"photo_id": f"{CITY}:photo:kapak-01", "original_file": f"Fotoğraflar/{CITY}_kapak_01.jpg",
         "downloaded_file_url": f"{THUMB}/Skyline.jpg/1280px-Skyline.jpg"}]
    assert [(c["license"], c["license_url"]) for c in clean] == [
        ("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/"),
        ("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0/"),
        ("CC0 1.0", "https://creativecommons.org/publicdomain/zero/1.0/")]
    assert clean[0]["author"] == "Jan Jansen" and clean[0]["file"] == plan[0]["original_file"]
    assert clean[0]["seen"] == "Gri bina" and clean[2]["photo_id"] == f"{CITY}:photo:kapak-01"


@pytest.mark.real
@needs_tools
def test_plan_drops_nonfree_mismatched_anonymous_offsite_and_unknown(tmp_path, capsys):
    bad = [cand("nc", "NC.jpg", 3000, license="CC BY-NC-SA 4.0", license_url="https://creativecommons.org/licenses/by-nc-sa/4.0/"),
           cand("mm", "MM.jpg", 3000, license_url="https://creativecommons.org/licenses/by-sa/3.0/"),
           cand("ow", "OW.jpg", 3000, author_text="Own work"),
           cand("ex", "EX.jpg", 900, original_url="https://example.org/EX.jpg"),
           cand("gif", "Anim.gif", 300, thumb_url="")]
    selected = [{"key": c["candidate_id"], "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": "x"} for c in bad]
    selected += [{"key": "yok", "entry_id": f"{CITY}:van-abbe", "role": "Mekân", "caption": "x"},
                 {"key": "k1", "entry_id": f"{CITY}:bilinmeyen", "role": "Mekân", "caption": "x"},
                 {"key": "k1", "entry_id": "", "role": "Galeri", "caption": "x"}]
    work, _ = make_work(tmp_path, GOOD + bad, selected)
    code, summary = run(capsys, "plan", work, "--city-id", CITY, "--tools", ARAC, "--out", tmp_path / "rapor.json")
    reasons = [why for _, why in json.loads((tmp_path / "rapor.json").read_text(encoding="utf-8"))["dropped"]]
    assert code == pr.EXIT_FINDINGS and summary["status"] == "findings"
    assert (summary["planned"], summary["dropped"]) == (0, 8)
    for expected in ("lisans uygun degil: CC BY-NC-SA 4.0", "lisans uygun degil: CC BY-SA 4.0 https://creativecommons.org/licenses/by-sa/3.0/",
                     "yazar uygun degil: Own work", "indirme adresi izinli degil", "desteklenmeyen dosya turu: .gif",
                     "aday yok", "mekan kaydi yok", "rol gecersiz"):
        assert any(r.startswith(expected) for r in reasons), expected


# ---------------------------------------------------------------- rows (gercek resmi araclarla)

@pytest.mark.real
@needs_tools
def test_rows_build_sheet_rows_web_copies_and_pass_official_audit(tmp_path, capsys):
    work, package = make_work(tmp_path)
    run(capsys, "plan", work, "--city-id", CITY, "--tools", ARAC)
    fake_download(work, package)
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", ARAC, "--date", "2026-10-30")
    parts = work / "data" / "parcalar"
    photos, evidence = read_jsonl(parts / "Fotoğraflar.foto.jsonl"), read_jsonl(parts / "Kanıtlar.foto.jsonl")
    prov = read_jsonl(parts / "FotoğrafKaynakları.foto.jsonl")
    assert code == pr.EXIT_OK and summary["photos"] == 3 and summary["roles"] == {"Mekân": 2, "Kapak": 1}
    for name, rows in (("Fotoğraflar", photos), ("Kanıtlar", evidence), ("FotoğrafKaynakları", prov)):
        assert rows and all(list(r) == mp.SHEETS[name] for r in rows), name  # merge_package anahtar sozlesmesi
    assert [p["order"] for p in photos] == [1, 2, 1] and photos[2]["entry_id"] == "" and photos[0]["capture_date"] == "2019-01-20"
    assert {p["source_checked_on"] for p in photos} == {"2026-10-30"} == {e["checked_on"] for e in evidence}
    assert "(4000×3000 px) özgün dosyasının 1280×960 px küçültülmüş kopyası" in photos[0]["modifications"]
    assert '"Van Abbe 2.jpg" özgün dosyası (1280×960 px) değiştirilmeden' in photos[1]["modifications"]
    assert len({p["modifications"] for p in photos}) == 3
    for e in evidence:  # K97: AI insan inceleme alanlarini kendi onaylamaz
        assert (e["metadata_review_status"], e["pixel_review_status"], e["rights_status"]) == ("Bekliyor",) * 3
    sej = json.loads(evidence[0]["source_evidence_json"])
    assert sej["retrieved_on"] == "2026-10-21" and sej["delivered_file"]["url"].endswith("1280px-Van_Abbe_1.jpg")
    assert evidence[0]["evidence_id"] == f"{CITY}:evidence:van-abbe-01" == photos[0]["evidence_id"]
    assert prov[0]["author_url"] == "https://commons.wikimedia.org/wiki/User:Jan"
    for p in prov:
        web = package / p["web_file"]
        assert web.is_file() and hashlib.sha256(web.read_bytes()).hexdigest() == p["web_sha256"]
        # L0 ISS-004: gercek create_web_copy Windows'ta '\' dondurur; paket yolu her isletim sisteminde '/' olmali
        assert p["web_file"].startswith("Teslimler/WebKopyalari/") and "\\" not in p["original_file"] + p["web_file"]
    assert official_audit(package, photos, prov)["errors"] == []


@pytest.mark.real
@needs_tools
def test_rows_report_missing_download_and_checksum_mismatch(tmp_path, capsys):
    work, package = make_work(tmp_path)
    run(capsys, "plan", work, "--city-id", CITY, "--tools", ARAC)
    fake_download(work, package, broken={f"{CITY}:photo:van-abbe-01"}, skip={f"{CITY}:photo:kapak-01"})
    code, summary = run(capsys, "rows", work, "--package", package, "--city-id", CITY, "--tools", ARAC,
                        "--date", "2026-10-30", "--out", tmp_path / "r.json")
    photos = read_jsonl(work / "data" / "parcalar" / "Fotoğraflar.foto.jsonl")
    detail = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))
    assert code == pr.EXIT_FINDINGS and (summary["missing_download"], summary["errors"]) == (1, 1)
    assert [p["photo_id"] for p in photos] == [f"{CITY}:photo:van-abbe-02"] and photos[0]["order"] == 1  # sira bosluksuz
    assert "checksum" in detail["errors"][0]["why"].lower() and detail["missing"] == [f"{CITY}:photo:kapak-01"]
