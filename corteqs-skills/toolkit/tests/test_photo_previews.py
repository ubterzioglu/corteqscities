"""photo_previews: Commons kisa liste onizlemeleri + contact_sheet girdisi (A6; pilot foto_onizleme.py). Ag yok, sahte tasima."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import photo_previews as pp

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
IMG = (200, {"Content-Type": "image/jpeg"}, JPEG)
BASE = "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab"
ORIGINAL_B1 = "https://upload.wikimedia.org/wikipedia/commons/c/cd/B1.jpg"


def thumb(name: str, width: int = 1600, query: str = "?utm_source=commons.wikimedia.org") -> str:
    return f"{BASE}/{name}.jpg/{width}px-{name}.jpg{query}"


def preview(name: str, width: int = 330) -> str:
    return thumb(name, width, "")


ROUTES = {preview("A1"): IMG, preview("A2"): IMG, ORIGINAL_B1: IMG}


class FakeTransport:
    """Sahte tasima: url -> yanit ya da yanit listesi (sirayla, son eleman tekrar eder); bilinmeyen adres 404."""

    def __init__(self, routes: dict) -> None:
        self.routes = {k: (list(v) if isinstance(v, list) else [v]) for k, v in routes.items()}
        self.calls: list[str] = []
        self.headers: list[dict] = []

    def __call__(self, url, headers, timeout):
        self.calls.append(url)
        self.headers.append(dict(headers))
        queue = self.routes.get(url)
        if queue is None:
            return 404, {"Content-Type": "text/html"}, b"<title>Not Found</title>"
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item


def write_jsonl(path: Path, rows: list[dict]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    return path


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_work(tmp_path: Path, extra: list[dict] | None = None, shortlists: dict | None = None) -> Path:
    work = tmp_path / "is"
    cands = [{"candidate_id": "t:yer-a|File:A1.jpg", "thumb_url": thumb("A1"), "commons_file": "File:A1.jpg"},
             {"candidate_id": "t:yer-a|File:A2.jpg", "thumb_url": thumb("A2"), "commons_file": "File:A2.jpg"},
             {"candidate_id": "t:merkez|File:B1.jpg", "thumb_url": "", "original_url": ORIGINAL_B1 + "?utm_source=x",
              "commons_file": "File:B1.jpg"}] + (extra or [])
    write_jsonl(work / "foto" / "candidates.jsonl", cands)
    lists = shortlists or {"t:yer-a": ["t:yer-a|File:A1.jpg", "t:yer-a|File:A2.jpg"], "t:merkez": ["t:merkez|File:B1.jpg"]}
    decisions = [{"candidate_id": c["candidate_id"], "entry_id": c["candidate_id"].split("|")[0],
                  "decision": "keep" if i else "flag"} for i, c in enumerate(cands)]
    (work / "foto" / "decisions.json").write_text(json.dumps({"decisions": decisions, "shortlists": lists}), encoding="utf-8")
    write_jsonl(work / "data" / "Mekânlar.jsonl", [{"entry_id": "t:yer-a", "title": "Yer A"}])
    write_jsonl(work / "data" / "Mahalleler.jsonl", [{"entry_id": "t:merkez", "title": "Merkez"}])
    return work


def run(capsys, work: Path, fake, *extra: str):
    sleeps: list[float] = []
    code = pp.main([str(work), *map(str, extra)], transport=fake, sleep=sleeps.append)
    lines = capsys.readouterr().out.strip().splitlines()
    return code, (json.loads(lines[-1]) if lines else None), sleeps


def cache_name(link: str) -> str:
    return hashlib.sha1(link.encode()).hexdigest() + ".jpg"


# ---------------------------------------------------------------- mutlu yol

def test_thumb_url_rewrites_width_and_drops_query():
    assert pp.thumb_url(thumb("A1"), 330) == preview("A1")
    assert pp.thumb_url(ORIGINAL_B1 + "?utm_source=x", 330) == ORIGINAL_B1


def test_downloads_shortlist_previews_and_writes_items(tmp_path, capsys):
    work = make_work(tmp_path)
    fake = FakeTransport(ROUTES)
    code, summary, sleeps = run(capsys, work, fake)
    items = read_jsonl(work / "foto" / "items.jsonl")
    assert code == pp.EXIT_OK and summary["status"] == "ok"
    assert (summary["items"], summary["downloaded"], summary["cached"], summary["errors"]) == (3, 3, 0, 0)
    assert fake.calls == [preview("A1"), preview("A2"), ORIGINAL_B1] and sleeps == [0.5, 0.5, 0.5]
    assert all("CorteqsCityToolkit" in h["User-Agent"] for h in fake.headers)
    target = work / "foto" / "onizleme" / cache_name(preview("A1"))
    assert items[0] == {"key": "t:yer-a|File:A1.jpg", "path": str(target), "label": "Yer A · A1.jpg",
                        "group": "t:yer-a", "decision": "flag"}
    assert target.read_bytes() == JPEG and items[2]["label"] == "Merkez · B1.jpg" and items[2]["decision"] == "keep"


def test_second_run_uses_cached_previews_without_network(tmp_path, capsys):
    work = make_work(tmp_path)
    run(capsys, work, FakeTransport(ROUTES))
    offline = FakeTransport({})
    code, summary, sleeps = run(capsys, work, offline)
    assert code == pp.EXIT_OK and offline.calls == [] and sleeps == []
    assert (summary["cached"], summary["downloaded"], summary["items"]) == (3, 0, 3)


def test_width_max_and_output_paths_are_parameters(tmp_path, capsys):
    work = make_work(tmp_path)
    items_out, preview_dir = tmp_path / "x" / "items.jsonl", tmp_path / "onbellek"
    fake = FakeTransport({preview("A1", 500): IMG, preview("A2", 500): IMG, ORIGINAL_B1: IMG})
    code, summary, _ = run(capsys, work, fake, "--width", "500", "--max", "2", "--items-out", items_out,
                           "--preview-dir", preview_dir)
    assert code == pp.EXIT_OK and summary["items"] == 2 and fake.calls == [preview("A1", 500), preview("A2", 500)]
    assert len(read_jsonl(items_out)) == 2 and sorted(p.name for p in preview_dir.iterdir()) == sorted(
        [cache_name(preview("A1", 500)), cache_name(preview("A2", 500))])


def make_extra_round(work: Path) -> Path:
    """A12: ek tur ayri klasorde (<is>/foto_ek/: candidates, venues, decisions); yeni mekan data/'da henuz yok."""
    extra = work / "foto_ek"
    write_jsonl(extra / "candidates.jsonl", [{"candidate_id": "t:yeni|File:Y1.jpg", "thumb_url": thumb("Y1"),
                                              "commons_file": "File:Y1.jpg"}])
    write_jsonl(extra / "venues.jsonl", [{"entry_id": "t:yeni", "role": "venue", "name": "Yeni Yer"}])
    decisions = {"decisions": [{"candidate_id": "t:yeni|File:Y1.jpg", "decision": "keep"}],
                 "shortlists": {"t:yeni": ["t:yeni|File:Y1.jpg"], "t:yer-a": ["t:yer-a|File:A1.jpg"]}}
    (extra / "decisions.json").write_text(json.dumps(decisions), encoding="utf-8")
    return extra


def test_extra_round_folder_candidates_and_venue_names_are_read(tmp_path, capsys):
    """A12: ana tur foto/ ve ek tur foto_*/ adaylari birlikte okunur; data/'da olmayan yeni mekanin etiketi turun
    venues.jsonl'indeki addan gelir (yoksa entry_id)."""
    work = make_work(tmp_path)
    extra = make_extra_round(work)
    fake = FakeTransport({preview("Y1"): IMG, preview("A1"): IMG})
    code, summary, _ = run(capsys, work, fake, "--decisions", extra / "decisions.json",
                           "--items-out", extra / "items.jsonl")
    items = read_jsonl(extra / "items.jsonl")
    assert code == pp.EXIT_OK and summary["status"] == "ok"
    assert summary["candidate_files"] == ["foto/candidates.jsonl", "foto_ek/candidates.jsonl"]
    assert [(i["label"], i["decision"]) for i in items] == [("Yeni Yer · Y1.jpg", "keep"), ("Yer A · A1.jpg", None)]


def test_decisions_folder_outside_the_round_convention_adds_its_candidates(tmp_path, capsys):
    """Pilot foto_onizleme'nin asil yolu: karar dosyasinin yanindaki candidates.jsonl ve venues.jsonl, klasor foto_*
    duzeninde olmasa da (or. <is>/ek_tur/) okunur; liste ana tur ve foto_*'dan sonra gelir, ayni dosya iki kez
    okunmaz. photo_rows bu klasoru taramaz (test_photo_rows: ek tur duzen disindaysa --candidates gerekir)."""
    work = make_work(tmp_path)
    side = work / "ek_tur"
    write_jsonl(side / "candidates.jsonl", [{"candidate_id": "t:yeni|File:Y1.jpg", "thumb_url": thumb("Y1"),
                                             "commons_file": "File:Y1.jpg"}])
    write_jsonl(side / "venues.jsonl", [{"entry_id": "t:yeni", "name": "Yeni Yer"}])
    decisions = {"decisions": [], "shortlists": {"t:yeni": ["t:yeni|File:Y1.jpg"], "t:yer-a": ["t:yer-a|File:A1.jpg"]}}
    (side / "decisions.json").write_text(json.dumps(decisions), encoding="utf-8")
    fake = FakeTransport({preview("Y1"): IMG, preview("A1"): IMG})
    code, summary, _ = run(capsys, work, fake, "--decisions", side / "decisions.json",
                           "--items-out", side / "items.jsonl")
    assert code == pp.EXIT_OK and summary["candidate_files"] == ["foto/candidates.jsonl", "ek_tur/candidates.jsonl"]
    assert [i["label"] for i in read_jsonl(side / "items.jsonl")] == ["Yeni Yer · Y1.jpg", "Yer A · A1.jpg"]
    code, summary, _ = run(capsys, work, FakeTransport(ROUTES))  # karar dosyasi foto/'da: ana dosya iki kez okunmaz
    assert code == pp.EXIT_OK and summary["candidate_files"] == ["foto/candidates.jsonl"]


def test_repeated_candidates_option_replaces_the_folder_scan(tmp_path, capsys):
    work = make_work(tmp_path)
    extra = make_extra_round(work)
    main = work / "foto" / "candidates.jsonl"
    routes = {preview("Y1"): IMG, preview("A1"): IMG}
    code, summary, _ = run(capsys, work, FakeTransport(routes), "--decisions", extra / "decisions.json",
                           "--candidates", main, "--out", tmp_path / "r.json")
    errors = json.loads((tmp_path / "r.json").read_text(encoding="utf-8"))["errors"]
    assert code == pp.EXIT_FINDINGS and errors == [{"key": "t:yeni|File:Y1.jpg", "why": "aday yok"}]
    assert summary["candidate_files"] == ["foto/candidates.jsonl"]
    code, summary, _ = run(capsys, work, FakeTransport(routes), "--decisions", extra / "decisions.json",
                           "--candidates", main, "--candidates", extra / "candidates.jsonl")
    assert code == pp.EXIT_OK and summary["items"] == 2
    assert run(capsys, work, FakeTransport(routes), "--candidates", tmp_path / "yok.jsonl")[0] == pp.EXIT_USAGE


def test_nonstandard_preview_width_is_a_usage_error(tmp_path, capsys):
    # Wikimedia 2026: dogrudan istekte standart disi genislik (1600) HTTP 400; her onizleme istegi bosa gider
    work = make_work(tmp_path)
    fake = FakeTransport(ROUTES)
    assert run(capsys, work, fake, "--width", "1600")[0] == pp.EXIT_USAGE
    assert run(capsys, work, fake, "--width", "331")[0] == pp.EXIT_USAGE and fake.calls == []
    assert run(capsys, work, FakeTransport({preview("A1", 960): IMG}), "--width", "960", "--max", "1")[0] == pp.EXIT_OK


def test_transient_503_is_retried_then_succeeds(tmp_path, capsys):
    work = make_work(tmp_path)
    fake = FakeTransport({preview("A1"): [(503, {}, b""), IMG], preview("A2"): IMG, ORIGINAL_B1: IMG})
    code, summary, sleeps = run(capsys, work, fake)
    assert code == pp.EXIT_OK and summary["downloaded"] == 3 and sleeps[:2] == [0.5, 5.0]


# ---------------------------------------------------------------- kirma testleri

def test_rate_limit_exhaustion_stops_whole_run(tmp_path, capsys):
    work = make_work(tmp_path)
    fake = FakeTransport({preview("A1"): (429, {"Retry-After": "120"}, b""), preview("A2"): IMG, ORIGINAL_B1: IMG})
    code, summary, sleeps = run(capsys, work, fake)
    assert code == pp.EXIT_FINDINGS and summary["status"] == "resume_later" and summary["items"] == 0
    assert fake.calls == [preview("A1")] * 3  # ayni mekanin ve baska mekanin adaylarina istek gitmez
    assert sleeps == [0.5, 30.0, 30.0]  # Retry-After en cok 30 sn
    assert read_jsonl(work / "foto" / "items.jsonl") == []


def test_bad_sources_are_reported_and_run_continues(tmp_path, capsys):
    extra = [{"candidate_id": "t:yer-a|File:X.jpg", "thumb_url": "https://example.org/X.jpg"},
             {"candidate_id": "t:yer-a|File:H.jpg", "thumb_url": thumb("H")},
             {"candidate_id": "t:yer-a|File:N.jpg", "thumb_url": thumb("N")},
             {"candidate_id": "t:yer-a|File:E.jpg", "thumb_url": thumb("E")}]
    keys = ["X", "yok", "H", "N", "E", "A1"]
    work = make_work(tmp_path, extra, {"t:yer-a": [f"t:yer-a|File:{k}.jpg" for k in keys]})
    fake = FakeTransport({preview("H"): (200, {"Content-Type": "text/html; charset=utf-8"}, b"<html>hata</html>"),
                          preview("E"): pp.TransportError("baglanti koptu"), preview("A1"): IMG})
    code, summary, _ = run(capsys, work, fake, "--out", tmp_path / "rapor.json")
    detail = json.loads((tmp_path / "rapor.json").read_text(encoding="utf-8"))
    whys = {e["key"].split("|")[1]: e["why"] for e in detail["errors"]}
    assert code == pp.EXIT_FINDINGS and summary["status"] == "findings"
    assert (summary["items"], summary["errors"]) == (1, 5)
    assert whys["File:X.jpg"] == "izinli olmayan adres" and whys["File:yok.jpg"] == "aday yok"
    assert whys["File:H.jpg"].startswith("gorsel degil") and whys["File:N.jpg"] == "HTTP 404"
    assert whys["File:E.jpg"].startswith("ag:") and "https://example.org/X.jpg" not in fake.calls
    assert not (work / "foto" / "onizleme" / cache_name(preview("H"))).exists()  # gorsel olmayan yanit yazilmaz


def test_usage_errors_exit_2(tmp_path, capsys):
    work = make_work(tmp_path)
    fake = FakeTransport({})
    assert run(capsys, work, fake, "--width", "0")[0] == pp.EXIT_USAGE
    assert run(capsys, work, fake, "--max", "0")[0] == pp.EXIT_USAGE
    assert run(capsys, tmp_path / "yok", fake)[0] == pp.EXIT_USAGE
    (work / "foto" / "decisions.json").write_text(json.dumps({"decisions": [], "shortlists": ["liste"]}), encoding="utf-8")
    assert run(capsys, work, fake)[0] == pp.EXIT_USAGE
    (work / "foto" / "decisions.json").write_text("{bozuk", encoding="utf-8")
    assert run(capsys, work, fake)[0] == pp.EXIT_USAGE
    assert fake.calls == [] and pp.main(["--help"]) == pp.EXIT_OK


def test_non_utf8_inputs_are_usage_errors_not_findings(tmp_path, capsys):
    """UnicodeDecodeError main disina kacinca Python cikisi 1 oluyordu ('eksik var' bulgusu ile karisir)."""
    work = make_work(tmp_path)
    fake = FakeTransport(ROUTES)
    candidates = work / "foto" / "candidates.jsonl"
    original = candidates.read_bytes()
    candidates.write_bytes(original + '{"candidate_id": "Müze"}\n'.encode("cp1252"))
    code = pp.main([str(work)], transport=fake, sleep=lambda s: None)
    assert code == pp.EXIT_USAGE and "candidates.jsonl: UTF-8 degil" in capsys.readouterr().err
    candidates.write_bytes(original)
    decisions = work / "foto" / "decisions.json"
    decisions.write_bytes(decisions.read_bytes().replace(b'"keep"', '"Müze"'.encode("cp1252"), 1))
    code = pp.main([str(work)], transport=fake, sleep=lambda s: None)
    assert code == pp.EXIT_USAGE and "decisions.json" in capsys.readouterr().err and fake.calls == []


def test_unwritable_outputs_exit_2_not_1(tmp_path, capsys):
    work = make_work(tmp_path)
    folder = tmp_path / "klasor"
    folder.mkdir()
    blocker = tmp_path / "dosya"
    blocker.write_text("klasor degil", encoding="utf-8")
    for extra in (["--items-out", str(folder)], ["--preview-dir", str(blocker)], ["--out", str(folder)]):
        code = pp.main([str(work), *extra], transport=FakeTransport(ROUTES), sleep=lambda s: None)
        assert code == pp.EXIT_USAGE and "HATA" in capsys.readouterr().err, extra
