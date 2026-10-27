"""Ağsız uçtan uca mini şehir (C2) ve kırma testleri (C3): skill'in teslim zinciri gerçek araçlarla.

Zincir pilotun teslim.ps1 sırasıyla, toolkit karşılıklarıyla:
  add_sources (sahte HTTP; snapshot index.jsonl + metin) -> merge_package -> photo_rows plan -> sahte indirme
  (girişi Atınç download_media.py'nin kendi public_url/local_file kontrolleriyle, teslim.ps1'deki --allow-host'larla;
  ilerleme biçimi aynı, Pillow JPEG) -> photo_rows rows -> merge_package -> package_sources ->
  build_xlsx (Eindhoven şablonunun tmp kopyası) -> validate_all --mode audit --new-content (gerçek araclar/arac).
Veri: fixtures/mini_city (mini _is klasörü): 2 konu x 2 kart, 2 mekân, 1 mahalle, 1 rota, 3 terim, 1 adım,
SayfaAlanları 23 anahtar, Şehir satırı, 8 sahte kaynak sayfası (biri hiçbir kartta kullanılmaz), 2 Commons karesi
(Mekân + Kapak). Kaynak sayfaları örnek alan adlarındadır (example.org); gerçek kurum sayfası değildir.
Gerçek dosyalar salt okunur: şablonun aslı ve araclar/arac (her dosyanın SHA-256'sı ve dosya listesi karşılaştırılır;
__pycache__ yazılmaz). Şablon kopyasında Atınç'ın büyük harfli teslimat kimliği küçük harfe çevrilir (pilotla aynı
zip düzeyi düzeltme, B10); çevrilmezse resmî doğrulayıcı tek yapı hatası verir.
Beklenen kapsam bulguları ayrı kontrol edilir: merge_package 'groups_without_place' (2 mekân 8 grubu dolduramaz) ve
validate_all asgari sayı eksikleri. Windows'ta resmî doğrulayıcı '\\'li paket yolunu da çözer, yani '0 medya hatası'
taşınabilirliği kanıtlamaz; paket yolu alanlarının '/' kontrolü bu yüzden mutlu yoldadır (L0 ISS-004).
Kırma testlerinde her bozulma kendi kapısında, beklenen bulgunun adıyla yakalanmalı (ilgisiz bulgu ya da red
sayılmaz); yakalanmayan kırma xfail yapılmaz, test kırmızı kalır (bulgu olarak raporlanır).
"""
from __future__ import annotations

import contextlib
import dataclasses
import hashlib
import importlib.util
import io
import json
import os
import shutil
import socket
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Callable

import openpyxl
import pytest
from PIL import Image

import add_sources
import build_xlsx
import common
import download_plan
import merge_package
import package_sources
import photo_rows
from web_fetch import RawResponse

ROOT = Path(r"C:\temp_private\corteqs\0000_newera")
ARAC = ROOT / "araclar" / "arac"
TEMPLATE = ROOT / "ekler" / "eindhoven" / "CITY-039_eindhoven_v001.xlsx"
SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "mini_city"
CITY, BBOX, DATE = "eindhoven", "51.3,51.55,5.3,5.6", "2026-10-22"
FETCHED_ON, DOWNLOADED_ON = "2026-10-20", "2026-10-21"
XLSX_NAME = "CITY-039_eindhoven_v001.xlsx"
UPPER_ID, LOWER_ID = b"CITY-039-v001", b"city-039-v001"
SOURCE_DIR = "Lisans kanıtları"
OFFICIAL_FILES = ("read_delivery_v7.py", "provenance.py", "delivery_tools.py", "download_media.py")
QUEUE_HOSTS = frozenset({"upload.wikimedia.org", "thumb.wikimedia.org"})  # teslim.ps1: download_media --allow-host
COVERAGE = {"groups_without_place": 1}  # mini şehrin beklenen kapsam bulgusu (hata değil)
ROWS = {"Yanıtlar": 4, "Mekânlar": 2, "Mahalleler": 1, "Bağlantılar": 7, "Adımlar": 1, "Rotalar": 1, "Sözlük": 3,
        "SayfaAlanları": 23, "Şehir": 1}
PHOTO_ROWS = {"Fotoğraflar": 2, "Kanıtlar": 2, "FotoğrafKaynakları": 2}
# 008 hiçbir yerde kullanılmaz. merge_package 'kullanılan' kaynağı 5 sekmenin source_ids'inden, bağlantı adreslerinden
# ve içeriğin iddialarından sayar; 112 sayfası (007) aile-hekimine-kayit kartında da kaynak (ve kartın iddia dayanağı).
# 007'ye yalnız SayfaAlanları iddialarının dayandığı durum ayrı kırma testidir.
USED_SOURCES = [f"{CITY}:kaynak:{n:03d}" for n in range(1, 8)]
PAGE_SOURCE = f"{CITY}:kaynak:007"
CLAIMS = 22
COUNTS = {"answers": 4, "places": 2, "neighborhoods": 1, "topics": 2, "photos": 1, "hero_photos": 1, "routes": 1,
          "glossary": 3}
MINIMUM = {"answers": 212, "places": 92, "neighborhoods": 12, "topics": 12, "photos": 187, "hero_photos": 6,
           "routes": 9, "glossary": 48}
MUSEUM, PARK = f"{CITY}:van-abbemuseum", f"{CITY}:stadswandelpark"
# Paket kökünden göreli dosya yolu taşıyan ve mini şehirde dolu olan alanlar: her yerde '/' olmalı (L0 ISS-004)
PACKAGE_PATHS = {"Fotoğraflar": ("file",), "Kanıtlar": ("pixel_review_file",),
                 "FotoğrafKaynakları": ("original_file", "web_file"), "Kaynaklar": ("snapshot_file",)}

pytestmark = [
    pytest.mark.real,
    pytest.mark.skipif(not (all((ARAC / name).is_file() for name in OFFICIAL_FILES) and TEMPLATE.is_file()),
                       reason="gercek araclar/arac ya da Eindhoven sablonu yok"),
]


# ---------------------------------------------------------------- yardımcılar

def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_state(root: Path) -> dict[str, str]:
    """Ağacın durumu: göreli yol -> dosyanın SHA-256'sı (klasör: '<klasör>'); ad, içerik ve yeni dosya kıyaslanır."""
    return {str(p.relative_to(root)): sha256(p) if p.is_file() else "<klasör>" for p in root.rglob("*")}


def changed_paths(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(path for path in before.keys() | after.keys() if before.get(path) != after.get(path))


def call(main: Callable[..., int], *args: Any, **kwargs: Any) -> tuple[int, dict]:
    """Script'i süreç içinde CLI argümanlarıyla çalıştırır: (çıkış kodu, tek satır JSON özet)."""
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = main([str(a) for a in args], **kwargs)
    lines = [line for line in buffer.getvalue().splitlines() if line.strip()]
    return code, (json.loads(lines[-1]) if lines else {})


def merge(work: Path) -> tuple[int, dict, dict]:
    code, summary = call(merge_package.main, work, "--city-id", CITY, "--bbox", BBOX)
    return code, summary, read_json(work / merge_package.REPORT_NAME)


def build(work: Path, out: Path, report: Path, *extra: str) -> tuple[int, dict]:
    return call(build_xlsx.main, "--template", work / "sablon.xlsx", "--data-dir", work / "data", "--out", out,
                "--report", report, "--tools", ARAC, *extra)


def rejections(report: Path) -> list[dict]:
    """build_xlsx --report redleri: {sheet, line (birleşik JSONL satırı, 1 tabanlı), _row, key, reason}."""
    return read_json(report)["rejected"]


def validate(xlsx: Path, package: Path, out: Path) -> tuple[int, dict]:
    """validate_all CLI'si ayrı süreçte (resmî kod UTF-8 kipi ister); audit kipinde rapor paket dışında."""
    proc = subprocess.run([sys.executable, "-X", "utf8", str(SCRIPTS / "validate_all.py"), str(xlsx), str(package),
                           "--tools", str(ARAC), "--mode", "audit", "--new-content", "--out", str(out)],
                          capture_output=True, text=True, encoding="utf-8", timeout=180,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    lines = proc.stdout.strip().splitlines()
    assert len(lines) == 1, proc.stdout + proc.stderr
    return proc.returncode, json.loads(lines[0])


def lowercase_delivery_id(source: Path, target: Path) -> None:
    """Pilotla aynı düzeltme (DEVIR §4b): sayfa XML'indeki büyük harfli teslimat kimliği küçük harfe; başka parça
    değişmez (sıkıştırma ve sıra korunur)."""
    with zipfile.ZipFile(source) as zin, zipfile.ZipFile(target, "w") as zout:
        for info in zin.infolist():
            data = zin.read(info.filename)
            if info.filename.startswith("xl/worksheets/"):
                data = data.replace(UPPER_ID, LOWER_ID)
            zout.writestr(info, data)
    with zipfile.ZipFile(target) as check:
        assert not any(UPPER_ID in check.read(name) for name in check.namelist())


def block_network(patch: pytest.MonkeyPatch) -> None:
    def refuse(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("ağ erişimi yasak: mini şehir testi ağsızdır")
    patch.setattr(socket.socket, "connect", refuse)
    patch.setattr(socket, "create_connection", refuse)
    patch.setattr(socket, "getaddrinfo", refuse)


def page_transport(pages: dict[str, bytes]) -> Callable[..., RawResponse]:
    """fetch_snapshot taşıyıcısının ağsız eşi: fixture sayfası 200 text/html, bilinmeyen adres 404."""
    def transport(method: str, url: str, _headers: Any, _timeout: float, _limit: int) -> RawResponse:
        body = pages.get(url)
        if body is None:
            return RawResponse(404, {"content-type": "text/plain"}, b"")
        return RawResponse(200, {"content-type": "text/html; charset=utf-8"}, body if method == "GET" else b"")
    return transport


def register_sources(work: Path) -> dict[str, tuple[int, dict]]:
    """Kaynak adayları konu sırasıyla add_sources'tan geçer (her konu kendi snap_<konu> klasörüne; pilot kaynak_ekle).
    kaynak_adaylari.jsonl = add_sources aday satırı + test alanları: topic (--topic), sayfa (sahte yanıtın dosyası),
    beklenen_kimlik (add_sources'ın vermesi gereken kaynak kimliği)."""
    candidates = read_jsonl(work / "kaynak_adaylari.jsonl")
    pages = {c["url"]: (FIXTURE / "kaynak_sayfalari" / c["sayfa"]).read_bytes() for c in candidates}
    for name in (add_sources.INDEX_NAME, add_sources.DRAFT_NAME):
        (work / name).write_text("", encoding="utf-8")
    results = {}
    for topic in dict.fromkeys(c["topic"] for c in candidates):
        path = work / f"aday_{topic}.jsonl"
        write_jsonl(path, [c for c in candidates if c["topic"] == topic])
        results[topic] = call(add_sources.main, work, "--candidates", path, "--subdir", f"snap_{topic}",
                              "--topic", topic, "--city-id", CITY, transport=page_transport(pages),
                              sleep=lambda _s: None, clock=lambda: FETCHED_ON)
    return results


@dataclasses.dataclass(frozen=True)
class QueueChecks:
    """Atınç download_media.py'nin plan girişindeki iki kontrol, gerçek araçtan."""
    public_url: Callable[..., str]
    local_file: Callable[[Path, str], Path]


def load_queue_checks() -> QueueChecks:
    """download_media.py araclar/arac'tan bayt kodu yazılmadan yüklenir (photo_rows.load_tools gibi: başka bir araç
    klasöründen kalan resmî modül silinir; sys.path ve bayrak eski hâline döner)."""
    for name in [n for n in sys.modules if n.split(".")[0] in ("core", "delivery_tools")]:
        del sys.modules[name]
    previous_flag, previous_path = sys.dont_write_bytecode, list(sys.path)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ARAC))
    try:
        spec = importlib.util.spec_from_file_location("atinc_download_media", ARAC / "download_media.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous_flag
        sys.path[:] = previous_path
    return QueueChecks(module.public_url, module.local_file)


def check_queue_entry(rows: list[dict], package: Path, queue: QueueChecks) -> None:
    """download_media.main'in indirmeden önceki girişi: yinelenen photo_id, sonra her satırda local_file (yol paketten
    çıkmaz) ve public_url (https, izinli alan, port 443, kimlik yok; resolve=False). Ret: AssertionError."""
    if len({r["photo_id"] for r in rows}) != len(rows):
        raise AssertionError("resmî indirme kuyruğu planı reddeder: yinelenen photo_id")
    for row in rows:
        try:
            queue.local_file(package, row["original_file"])
            queue.public_url(row["downloaded_file_url"], QUEUE_HOSTS, resolve=False)
        except ValueError as error:
            raise AssertionError(f"resmî indirme kuyruğu bu plan satırını reddeder ({error}): {row}") from error


def fake_download(plan_file: Path, package: Path, queue: QueueChecks) -> None:
    """download_media.py'nin ağsız eşi. Giriş gerçek kuyruk kadar katı (check_queue_entry); sonra plandaki adres başına
    Pillow JPEG (thumb 1280×960, özgün 1200×800) ve aynı biçimde Teslimler/download-progress-v7.json ({**satır,
    resolved_download_url, downloaded_on, sha256, bytes, original_sha256})."""
    rows = read_json(plan_file)
    check_queue_entry(rows, package, queue)
    progress = []
    for row in rows:
        url = row["downloaded_file_url"]
        target = package / row["original_file"]
        target.parent.mkdir(parents=True, exist_ok=True)
        size = (1280, 960) if "/thumb/" in url else (1200, 800)
        Image.new("RGB", size, tuple(hashlib.sha256(url.encode("utf-8")).digest()[:3])).save(target, format="JPEG")
        digest = sha256(target)
        progress.append({**row, "resolved_download_url": url, "downloaded_on": DOWNLOADED_ON, "sha256": digest,
                         "bytes": target.stat().st_size, "original_sha256": digest})
    out = package.joinpath(*photo_rows.PROGRESS)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(progress, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------- zincir (modül başına bir kez)

@dataclasses.dataclass(frozen=True)
class Chain:
    work: Path
    package: Path
    xlsx: Path
    steps: dict[str, Any]
    validation: tuple[int, dict]
    report: dict
    template_sha: tuple[str, str]
    tools_state: tuple[dict[str, str], dict[str, str]]


@pytest.fixture(scope="module")
def chain(tmp_path_factory: pytest.TempPathFactory) -> Chain:
    tools_before, template_before = tree_state(ARAC), sha256(TEMPLATE)  # araçlardan ilk yüklemeden önce
    base = tmp_path_factory.mktemp("mini_city")
    work, package = base / "_is", base / "paket"
    shutil.copytree(FIXTURE, work, ignore=shutil.ignore_patterns("kaynak_sayfalari"))
    package.mkdir()
    shutil.copyfile(TEMPLATE, work / "sablon_orijinal_kopya.xlsx")
    lowercase_delivery_id(work / "sablon_orijinal_kopya.xlsx", work / "sablon.xlsx")
    xlsx, steps = package / XLSX_NAME, {}
    with pytest.MonkeyPatch.context() as patch:
        block_network(patch)
        queue = load_queue_checks()
        steps["sources"] = register_sources(work)
        steps["merge_1"] = merge(work)
        steps["photo_plan"] = call(photo_rows.main, "plan", work, "--city-id", CITY, "--tools", ARAC)
        fake_download(work / "foto" / "indirme_plani.json", package, queue)
        steps["photo_rows"] = call(photo_rows.main, "rows", work, "--package", package, "--city-id", CITY,
                                   "--tools", ARAC, "--date", DATE)
        steps["merge_2"] = merge(work)
        steps["package_sources"] = call(package_sources.main, work, package)
        steps["build"] = build(work, xlsx, work / "build.json")
    validation = validate(xlsx, package, work / "validation.json")
    return Chain(work, package, xlsx, steps, validation, read_json(work / "validation.json"),
                 (template_before, sha256(TEMPLATE)), (tools_before, tree_state(ARAC)))


@pytest.fixture()
def clean_copy(chain: Chain, tmp_path: Path) -> tuple[Path, Path]:
    """Temiz zincirin _is ve paket kopyası: kırma testi asıl zinciri bozmaz."""
    work, package = tmp_path / "_is", tmp_path / "paket"
    shutil.copytree(chain.work, work)
    shutil.copytree(chain.package, package)
    return work, package


# ---------------------------------------------------------------- mutlu yol

def test_sources_are_snapshotted_offline_and_registered_with_stable_ids(chain: Chain) -> None:
    candidates = read_jsonl(chain.work / "kaynak_adaylari.jsonl")
    for topic, (code, summary) in chain.steps["sources"].items():
        expected = sum(1 for c in candidates if c["topic"] == topic)
        assert code == 0 and (summary["added"], summary["rejected"]) == (expected, 0), (topic, summary)
        index = read_jsonl(chain.work / f"snap_{topic}" / "index.jsonl")  # fetch_snapshot ciktisi
        assert len(index) == expected and all(r["status"] == 200 and r["text_chars"] >= 500 for r in index)
        assert all((chain.work / f"snap_{topic}" / r["text_file"]).is_file() for r in index)
    registered = {r["url"]: r["source_id"] for r in read_jsonl(chain.work / "kaynak_dizini.jsonl")}
    assert registered == {c["url"]: c["beklenen_kimlik"] for c in candidates}
    draft = read_jsonl(chain.work / "kaynak_taslak.jsonl")
    assert {r["checked_on"] for r in draft} == {FETCHED_ON} and {r["verified"] for r in draft} == {"Hayır"}


def test_each_gate_passes_with_only_the_expected_coverage_finding(chain: Chain) -> None:
    steps = chain.steps
    for name, rows in (("merge_1", ROWS), ("merge_2", {**ROWS, **PHOTO_ROWS})):
        code, summary, report = steps[name]
        assert code == 1 and summary["issue_kinds"] == COVERAGE, report["issues"]
        assert (summary["quote_miss"], summary["claims"], summary["sources_used"]) == (0, CLAIMS, 7), report
        assert summary["rows"] == rows and summary["per_topic"] == {"resmi": 2, "saglik": 2}
    code, summary = steps["photo_plan"]
    assert code == 0 and (summary["planned"], summary["dropped"]) == (2, 0), summary
    code, summary = steps["photo_rows"]
    assert code == 0 and summary["roles"] == {"Mekân": 1, "Kapak": 1} and summary["missing_download"] == 0
    code, summary = steps["package_sources"]
    assert code == 0 and (summary["sources"], summary["with_snapshot"], summary["copied"]) == (7, 7, 7)
    code, summary = steps["build"]
    assert code == 0 and summary["rejected"] == 0 and summary["fidelity"] == "ok", summary
    assert summary["rows_written"] == {**ROWS, **PHOTO_ROWS, "Konular": 2, "Kaynaklar": 7}


def test_official_validator_reports_zero_structure_and_media_errors(chain: Chain) -> None:
    # Windows'ta resmî doğrulayıcı '\'li paket yolunu da çözer: buradaki 0 medya hatası taşınabilirliği kanıtlamaz
    # (Linux/Mac'te aynı paket 'dosya okunamadı web_file' verir); '/' kontrolü bir sonraki testte (L0 ISS-004).
    code, summary = chain.validation
    assert summary["structure"]["errors"] == 0, summary["error_classes"]
    assert summary["media"]["errors"] == 0, summary["media_classes"]
    assert summary["error_classes"] == [] and summary["media_classes"] == []
    assert chain.report["structure"]["counts"] == COUNTS
    # asgari sayı eksikleri ayrı: mini şehir hiçbir alt sınıra ulaşmaz, bu yüzden teknik olarak tamam değil (çıkış 1)
    assert summary["minimum_gaps"] == {k: {"actual": COUNTS[k], "minimum": MINIMUM[k]} for k in COUNTS}
    assert code == 1 and summary["technically_complete"] is False
    assert summary["extras"]["verified_without_snapshot"] == 0 and summary["extras"]["placeholders"] == 0


def package_path_values(chain: Chain) -> dict[str, list[str]]:
    """'<kaynak> <Sekme>.<alan>' -> dolu değerler; kaynak 'data' (birleşik JSONL, build_xlsx girdisi) ve 'Excel'
    (teslim dosyası, satır 7 anahtarlarıyla)."""
    workbook = openpyxl.load_workbook(chain.xlsx)
    values: dict[str, list[str]] = {}
    for sheet, fields in PACKAGE_PATHS.items():
        origins = (("data", read_jsonl(chain.work / "data" / f"{sheet}.jsonl")),
                   ("Excel", list(common.iter_records(workbook[sheet]))))
        for origin, rows in origins:
            for field in fields:
                values[f"{origin} {sheet}.{field}"] = [str(r[field]) for r in rows if r.get(field)]
    return values


def test_package_path_fields_use_forward_slashes(chain: Chain) -> None:
    """L0 ISS-004 (P1): paket kökünden göreli yollar her yerde '/' olmalı (sözleşme: Teslimler/WebKopyalari/<sha>.webp).
    Atınç'ın local_file'ı yolu PurePosixPath ile okur: '\\'li yol Linux/Mac'te bulunamaz, aynı paket orada medya
    hatası verir. Birleşik veri ve teslim Excel'i ayrı denetlenir; her alanda en az bir dolu değer olmalı (denetim
    boşa geçmesin). Kök neden: create_web_copy web_file'ı str(Path) ile yazar; pilot foto_satirlari.py '/' yapıyordu."""
    values = package_path_values(chain)
    assert all(values.values()), {name: len(found) for name, found in values.items()}
    backslashed = {name: [v for v in found if "\\" in v] for name, found in values.items()
                   if any("\\" in v for v in found)}
    assert not backslashed, f"paket yolunda '\\' var (Linux/Mac'te dosya bulunamaz): {backslashed}"


def test_only_used_sources_are_packaged_with_matching_hashes(chain: Chain) -> None:
    rows = read_jsonl(chain.work / "data" / "Kaynaklar.jsonl")
    assert [r["source_id"] for r in rows] == USED_SOURCES and {r["verified"] for r in rows} == {"Evet"}
    for row in rows:
        assert row["snapshot_file"].startswith(f"{SOURCE_DIR}/")
        assert sha256(chain.package / row["snapshot_file"]) == row["snapshot_sha256"]
    packaged = sorted(p.name for p in chain.package.joinpath(*SOURCE_DIR.split("/")).iterdir() if not p.name.endswith("-evidence.json"))
    assert packaged == sorted(Path(r["snapshot_file"]).name for r in rows)


def test_ai_writes_only_pending_review_values(chain: Chain) -> None:
    for row in read_jsonl(chain.work / "data" / "Kanıtlar.jsonl"):  # K97: insan inceleme alanları hep Bekliyor
        assert (row["metadata_review_status"], row["pixel_review_status"], row["rights_status"]) == ("Bekliyor",) * 3
    for sheet in ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük", "Fotoğraflar", "Şehir"):
        assert {r["editorial_status"] for r in read_jsonl(chain.work / "data" / f"{sheet}.jsonl")} == {"Taslak"}


# ---------------------------------------------------------------- kırma testleri: merge_package

def test_break_fabricated_quote_is_a_quote_miss(clean_copy: tuple[Path, Path]) -> None:
    work, _ = clean_copy
    path = work / "claims" / "resmi.jsonl"
    claims = read_jsonl(path)
    write_jsonl(path, claims + [{**claims[0], "claim_id": "C-uydurma-1", "quote": "De inschrijving kost 50 euro."}])
    code, summary, report = merge(work)
    assert code == 1 and summary["quote_miss"] == 1
    assert [m[1:] for m in report["quote_miss_list"]] == [["C-uydurma-1", "alinti_metinde_yok"]]


def test_break_source_id_missing_from_index_is_caught(clean_copy: tuple[Path, Path]) -> None:
    work, _ = clean_copy
    ghost = f"{CITY}:kaynak:099"
    part = work / "data" / "parcalar" / "Yanıtlar.saglik.jsonl"
    rows = read_jsonl(part)
    rows[0]["source_ids"] += f";{ghost}"
    write_jsonl(part, rows)
    path = work / "claims" / "saglik.jsonl"
    claims = read_jsonl(path)
    write_jsonl(path, claims + [{**claims[0], "claim_id": "C-hayalet-1", "source_id": ghost, "url": ""}])
    code, summary, report = merge(work)
    assert code == 1 and summary["issue_kinds"].get("source_ids") == 1
    assert ["source_ids", "Yanıtlar", "saglik", rows[0]["entry_id"], rows[0]["source_ids"]] in report["issues"]
    assert [m[1:] for m in report["quote_miss_list"]] == [["C-hayalet-1", "kaynak_yok"]]


def test_break_card_without_action_link_is_no_action(clean_copy: tuple[Path, Path]) -> None:
    work, _ = clean_copy
    part = work / "data" / "parcalar" / "Bağlantılar.m1.jsonl"
    write_jsonl(part, [r for r in read_jsonl(part) if r["entry_id"] != PARK])
    code, summary, report = merge(work)
    assert code == 1 and summary["issue_kinds"].get("no_action") == 1
    assert ["no_action", PARK] in report["issues"]


def test_break_source_backing_only_page_claims_is_packaged_or_flagged(clean_copy: tuple[Path, Path]) -> None:
    """Fixture'ın dolandığı açık: yalnız SayfaAlanları/Şehir iddialarının dayandığı kaynak da Kaynaklar'a (ve pakete)
    girmeli ya da merge_package onu adıyla bildirmeli. merge_package 'kullanılan' kaynağı eskiden yalnız 5 sekmenin
    source_ids'inden ve bağlantı adreslerinden sayıyordu (pilot birlestir.py de); SayfaAlanları'nın source_ids sütunu
    yok, iddia yine geçiyordu. Artık içeriğin iddialarının dayandığı kaynak da sayılır (U2). Mutlu yol 007'yi
    aile-hekimine-kayit kartında da kaynak gösterir; bu test kartın 007 dayanağını (source_ids ve kartın 007
    iddiası) kaldırır."""
    work, _ = clean_copy
    parts = work / "data" / "parcalar"
    page_url = next(r["url"] for r in read_jsonl(work / "kaynak_dizini.jsonl") if r["source_id"] == PAGE_SOURCE)
    part = parts / "Yanıtlar.saglik.jsonl"
    write_jsonl(part, [{**r, "source_ids": ";".join(s for s in r["source_ids"].split(";") if s != PAGE_SOURCE)}
                       for r in read_jsonl(part)])
    claims = work / "claims" / "saglik.jsonl"
    write_jsonl(claims, [c for c in read_jsonl(claims)
                         if c.get("source_id") != PAGE_SOURCE and c.get("url") != page_url])
    backing = [c["claim_id"] for path in sorted((work / "claims").glob("*.jsonl")) for c in read_jsonl(path)
               if c.get("source_id") == PAGE_SOURCE or c.get("url") == page_url]
    cited = [r for sheet in merge_package.SOURCE_SHEETS for path in parts.glob(f"{sheet}.*.jsonl")
             for r in read_jsonl(path) if PAGE_SOURCE in str(r.get("source_ids") or "").split(";")]
    linked = [r for path in parts.glob("Bağlantılar.*.jsonl") for r in read_jsonl(path) if r["url"] == page_url]
    assert backing == ["C-sayfa-1", "C-sayfa-2"] and not cited and not linked  # 007'ye yalnız sayfa iddiaları dayanır
    code, summary, report = merge(work)
    packaged = [r["source_id"] for r in read_jsonl(work / "data" / "Kaynaklar.jsonl")]
    flagged = code == 1 and any(PAGE_SOURCE in json.dumps(item, ensure_ascii=False)
                                for item in report["issues"] + report["quote_miss_list"])
    assert PAGE_SOURCE in packaged or flagged, (
        f"{PAGE_SOURCE} yalnız SayfaAlanları iddialarının ({backing}) dayanağı: Kaynaklar'a girmedi ({len(packaged)} "
        f"kaynak) ve merge_package adıyla bildirmedi (bulgular {summary['issue_kinds']}, alıntı eksiği "
        f"{summary['quote_miss']})")


# ---------------------------------------------------------------- kırma testleri: validate_all (medya)

def test_break_wrong_cc_license_url_is_a_media_error_in_validate_all(clean_copy: tuple[Path, Path],
                                                                    tmp_path: Path) -> None:
    """CC BY-SA 4.0 karesinin adresi 3.0 sürümüne kayarsa resmî medya denetimi yakalar (fotoğraf, kanıt ve özgün kanıt
    JSON'u tutarlı değiştirilir; tek fark sürüm). merge_package bu alana bakmaz; build_xlsx ileride reddederse kırma
    daha erken yakalanmış olur, o da kabul, ama yalnız red bozulan satırın değişen alanlarındaysa (ilgisiz red
    sayılmaz)."""
    work, package = clean_copy
    wrong = "https://creativecommons.org/licenses/by-sa/3.0/"
    parts = work / "data" / "parcalar"
    photos, evidence = read_jsonl(parts / "Fotoğraflar.foto.jsonl"), read_jsonl(parts / "Kanıtlar.foto.jsonl")
    index = next(i for i, p in enumerate(photos) if p["entry_id"] == MUSEUM)
    assert photos[index]["license"] == "CC BY-SA 4.0"
    raw = json.loads(evidence[index]["source_evidence_json"])
    photos[index]["license_url"] = evidence[index]["license_url"] = raw["license_url"] = wrong
    evidence[index]["source_evidence_json"] = json.dumps(raw, ensure_ascii=False)
    write_jsonl(parts / "Fotoğraflar.foto.jsonl", photos)
    write_jsonl(parts / "Kanıtlar.foto.jsonl", evidence)
    merge(work)
    assert call(package_sources.main, work, package)[0] == 0
    build_code, build_summary = build(work, package / XLSX_NAME, tmp_path / "build.json", "--overwrite")
    assert build_code in (0, 1), build_summary
    if build_summary["rejected"]:  # build_xlsx lisansı reddetti: kırma resmî doğrulayıcıdan önce yakalandı
        found = {(r["sheet"], r["key"], r["line"]) for r in rejections(tmp_path / "build.json")}
        changed = (("Fotoğraflar", "license_url"), ("Kanıtlar", "license_url"), ("Kanıtlar", "source_evidence_json"))
        assert found <= {(sheet, key, index + 1) for sheet, key in changed}, found
        return
    code, summary = validate(package / XLSX_NAME, package, tmp_path / "dogrulama.json")
    assert code == 1 and summary["media"]["errors"] >= 1, summary
    assert "lisans etiketi ve resmî sürüm URL uyuşmuyor" in [c["class"] for c in summary["media_classes"]]
    assert "Fotoğraflar: Creative Commons etiketi ve resmî lisans bağlantısı eşleşmiyor." in [
        c["class"] for c in summary["error_classes"]]


# ---------------------------------------------------------------- kırma testleri: foto indirme planı

@pytest.mark.parametrize("field, value", [
    ("downloaded_file_url", "http://upload.wikimedia.org/wikipedia/commons/a/ab/Kare.jpg"),
    ("downloaded_file_url", "https://media.example.org/wikipedia/commons/a/ab/Kare.jpg"),
    ("downloaded_file_url", "https://upload.wikimedia.org:8443/wikipedia/commons/a/ab/Kare.jpg"),
    ("original_file", "../Fotoğraflar/paket_disi.jpg"),
], ids=["http", "izinsiz_alan", "port", "paket_disi_yol"])
def test_fake_download_refuses_plans_the_real_queue_refuses(chain: Chain, tmp_path: Path, field: str,
                                                           value: str) -> None:
    """Sahte indirme gerçek kuyruktan gevşek değil: download_media.py'nin girişte reddedeceği plan satırı (http,
    izinsiz alan, 443 dışı port, paket dışına çıkan yol) zincirde sessizce geçmez; kontroller araclar/arac'taki gerçek
    public_url/local_file. Temiz plan zincirde aynı kontrolden geçti."""
    rows = read_json(chain.work / "foto" / "indirme_plani.json")
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps([{**rows[0], field: value}, *rows[1:]], ensure_ascii=False), encoding="utf-8")
    package = tmp_path / "paket"
    package.mkdir()
    with pytest.raises(AssertionError, match="resmî indirme kuyruğu"):
        fake_download(plan_file, package, load_queue_checks())
    assert not package.joinpath(*photo_rows.PROGRESS).exists()


@pytest.mark.parametrize("case", ["thumb_url_1600", "original_url_1600"])
def test_break_1600px_download_address_never_reaches_the_plan(clean_copy: tuple[Path, Path], case: str) -> None:
    """Wikimedia 2026: 1600 px standart genişlik değil (HTTP 400). Eski Commons varsayılanı olan 1600 px önizleme
    adresi (thumb_url) ya da özgün adres yerine yazılmış 1600 px kopya planlara girmemeli: photo_rows plan ve
    download_plan --prefer-thumb ya 1280 px'e çevirir ya da kareyi reddeder. Plan yeni dosyaya yazılır ve iki adımın
    çıkış kodu sınanır: çöken adım temiz zincirin eski 1280 px planını okutup testi boşa geçirmez."""
    work, _ = clean_copy
    path = work / "foto" / "candidates.jsonl"
    candidates = read_jsonl(path)
    index = next(i for i, c in enumerate(candidates) if c["candidate_id"].startswith(MUSEUM))
    original = candidates[index]["original_url"].split("?")[0]
    head, name = original.replace("/commons/", "/commons/thumb/").rsplit("/", 1)[0], original.rsplit("/", 1)[1]
    scaled = f"{head}/{name}/1600px-{name}"
    field, value = (("thumb_url", scaled.replace("//upload.", "//thumb.")) if case == "thumb_url_1600"
                    else ("original_url", scaled))
    museum = {**candidates[index], field: value}
    write_jsonl(path, [*candidates[:index], museum, *candidates[index + 1:]])
    plan_file = work / "foto" / "kirma_plani.json"
    code, summary = call(photo_rows.main, "plan", work, "--city-id", CITY, "--tools", ARAC, "--plan-out", plan_file,
                         "--out", work / "plan_rapor.json")
    assert code in (0, 1) and plan_file.is_file(), summary  # 2 = kullanım/girdi hatası: plan yazılmadı
    rows_file = work / "foto" / "plan_girdisi.jsonl"
    write_jsonl(rows_file, [{"photo_id": f"{CITY}:photo:van-abbemuseum-01", "entry_id": MUSEUM,
                             **{k: museum[k] for k in ("original_url", "thumb_url", "width")}}])
    dp_code, dp_summary = call(download_plan.main, "--selected", rows_file, "--city-id", CITY,
                               "--out", work / "dp_plani.json", "--prefer-thumb")
    assert dp_code in (0, 1), dp_summary
    leaked = [row["downloaded_file_url"] for row in read_json(plan_file) + read_json(work / "dp_plani.json")
              if "/1600px-" in row["downloaded_file_url"]]
    assert not leaked, (f"1600 px adres indirme planına girdi (photo_rows çıkış {code}, download_plan çıkış "
                        f"{dp_code}, original_is_thumb={dp_summary.get('original_is_thumb')}): {leaked}")


# ---------------------------------------------------------------- kırma testleri: AI kendi onayı

def test_break_ai_self_approval_of_review_fields_is_rejected_by_build_xlsx(clean_copy: tuple[Path, Path],
                                                                         tmp_path: Path) -> None:
    work, package = clean_copy
    part = work / "data" / "parcalar" / "Kanıtlar.foto.jsonl"
    rows = read_jsonl(part)
    rows[0] = {**rows[0], "metadata_review_status": "Doğrulandı", "pixel_review_status": "Tamam"}
    rows[1] = {**rows[1], "rights_status": "Bu kare için uygun"}
    write_jsonl(part, rows)
    merge(work)  # merge_package bu alanları bulgu olarak bildirir ama veriyi yine yazar; burada sınanan kapı build_xlsx
    assert call(package_sources.main, work, package)[0] == 0
    out = tmp_path / "onayli.xlsx"
    code, summary = build(work, out, tmp_path / "build.json")
    reasons = {(r["sheet"], r["key"]): r["reason"] for r in rejections(tmp_path / "build.json")}
    assert code == 1 and summary["rejected"] == 2 and not out.exists()  # red varken hiçbir şey yazılmaz
    assert "human review field" in reasons[("Kanıtlar", "metadata_review_status")]
    assert "human review field" in reasons[("Kanıtlar", "rights_status")]
    assert "not in list" in reasons[("Kanıtlar", "pixel_review_status")]  # 'Tamam' seçeneklerde yok


EDITORIAL = {"Yanıtlar": "Yanıtlar.resmi.jsonl", "Mekânlar": "Mekânlar.m1.jsonl",
             "Mahalleler": "Mahalleler.mahalle.jsonl", "Rotalar": "Rotalar.rota.jsonl",
             "Sözlük": "Sözlük.sozluk.jsonl", "Fotoğraflar": "Fotoğraflar.foto.jsonl", "Şehir": "Şehir.sayfa.jsonl"}
EDITORIAL_KINDS = ("enum_order", "editorial_status")  # eski (yalnız giriş sekmeleri) ve bugünkü bulgu adı


def merge_names_row(report: dict, sheet: str, part: str, row_id: str) -> bool:
    """merge_package bozulan satırı adıyla bildirdi mi: [enum_order|editorial_status, sekme, parça, kimlik, ...]."""
    expected = [[kind, sheet, part, row_id] for kind in EDITORIAL_KINDS]
    return any(issue[:4] in expected for issue in report["issues"])


@pytest.mark.parametrize("sheet", list(EDITORIAL))
def test_break_ai_editorial_approval_is_caught_on_every_sheet(clean_copy: tuple[Path, Path], tmp_path: Path,
                                                              sheet: str) -> None:
    """Skill kendi işini onaylamaz: yazar 'Onaylandı' yazarsa merge_package bozulan satırı adıyla bildirmeli
    ([enum_order|editorial_status, sekme, parça, kimlik]) ya da build_xlsx o sekmenin editorial_status alanını
    reddetmeli; ilgisiz bulgu ya da red sayılmaz. Resmî doğrulayıcı taslak kipinde editör durumuna bakmaz."""
    work, package = clean_copy
    part = work / "data" / "parcalar" / EDITORIAL[sheet]
    rows = read_jsonl(part)
    row_id = rows[0][merge_package.SHEETS[sheet][0]]  # entry_id / route_id / term_id / photo_id / city_id
    write_jsonl(part, [{**rows[0], "editorial_status": "Onaylandı"}, *rows[1:]])
    _, merge_summary, report = merge(work)
    by_merge, by_build = merge_names_row(report, sheet, EDITORIAL[sheet].split(".")[1], row_id), False
    if not by_merge:
        assert call(package_sources.main, work, package)[0] == 0
        build_code, build_summary = build(work, tmp_path / "onayli.xlsx", tmp_path / "build.json")
        assert build_code in (0, 1), build_summary  # 2 = başka bir kullanım/sadakat hatası; kırma sonucu değil
        by_build = any((r["sheet"], r["key"]) == (sheet, "editorial_status")
                       for r in rejections(tmp_path / "build.json"))
    assert by_merge or by_build, (f"{sheet}: editorial_status 'Onaylandı' hiçbir kapıda yakalanmadı (merge_package "
                                  f"{row_id} için enum_order/editorial_status bulgusu vermedi, bulgular "
                                  f"{merge_summary['issue_kinds']}; build_xlsx editorial_status reddi yok)")


# ---------------------------------------------------------------- kırma testleri: paket yolları

def test_break_windows_backslash_web_file_is_normalized_or_flagged(clean_copy: tuple[Path, Path],
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """L0 ISS-004 (P1): Atınç'ın create_web_copy'si web_file'ı str(Path), yani işletim sistemi ayracıyla yazar
    (Windows'ta '\\'); paket yolları her yerde '/' olmalı (pilot foto_satirlari.py düzeltiyordu). Kırma: create_web_copy
    çıktısı Windows biçimine çevrilir. Linux/Mac'te bu Windows çıktısını taklit eder; Windows'ta gerçek çıktı zaten
    böyledir (taklit etkisiz; aynı açığı temiz zincirde test_package_path_fields_use_forward_slashes gösterir).
    photo_rows'a '\\'li değer verildiği ayrıca doğrulanır. Yakalandı: photo_rows web_file'ı '/' ile yazar YA DA
    merge_package '\\'li parçayı '/' ile birleştirir ya da web_file'ı anan bir bulgu verir (çıkış 1)."""
    work, package = clean_copy
    real_load, given = photo_rows.load_tools, []

    def windows_tools(tools_dir: Path) -> photo_rows.Tools:
        tools = real_load(tools_dir)

        def web_copy(root: Path, row: dict) -> dict:
            made = tools.create_web_copy(root, row)
            given.append(str(made["web_file"]).replace("/", "\\"))
            return {**made, "web_file": given[-1]}
        return dataclasses.replace(tools, create_web_copy=web_copy)

    monkeypatch.setattr(photo_rows, "load_tools", windows_tools)
    code, summary = call(photo_rows.main, "rows", work, "--package", package, "--city-id", CITY, "--tools", ARAC,
                         "--date", DATE)
    assert code == 0 and len(given) == PHOTO_ROWS["FotoğrafKaynakları"], summary
    assert all("\\" in w for w in given), given  # kırma etkili: photo_rows'a '\'li web_file verildi
    expected = [w.replace("\\", "/") for w in given]
    part = work / "data" / "parcalar" / "FotoğrafKaynakları.foto.jsonl"
    rows = read_jsonl(part)
    produced = [r["web_file"] for r in rows]
    write_jsonl(part, [{**r, "web_file": w} for r, w in zip(rows, given)])  # merge kapısı da '\'li parçayla sınanır
    merge_code, merge_summary, report = merge(work)
    merged = [r["web_file"] for r in read_jsonl(work / "data" / "FotoğrafKaynakları.jsonl")]
    flagged = merge_code == 1 and any("web_file" in json.dumps(issue, ensure_ascii=False) for issue in report["issues"])
    assert produced == expected or merged == expected or flagged, (
        f"web_file '\\' ile pakete gidiyor (L0 ISS-004): photo_rows çıktısı {produced}, merge_package sonrası "
        f"{merged}, merge bulguları {merge_summary['issue_kinds']}")


# ---------------------------------------------------------------- en son: gerçek dosyalar salt okunur kaldı mı

def test_real_template_and_official_tools_stay_read_only(chain: Chain) -> None:
    """Dosyadaki son test: zincir ve (sırayla koşan) bütün kırma testlerinden sonra şablonun aslı ve araclar/arac
    değişmemiş olmalı: araçlarda dosya eklenmemiş ya da silinmemiş, var olan her dosyanın içeriği (SHA-256) aynı
    (__pycache__ dahil)."""
    template_before, template_after_chain = chain.template_sha
    assert template_before == template_after_chain == sha256(TEMPLATE)
    tools_before, tools_after_chain = chain.tools_state
    after_chain, now = changed_paths(tools_before, tools_after_chain), changed_paths(tools_before, tree_state(ARAC))
    assert not after_chain and not now, f"araclar/arac değişti: zincirden sonra {after_chain}, şimdi {now}"
