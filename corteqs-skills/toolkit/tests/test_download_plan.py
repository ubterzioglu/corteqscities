"""download_plan testleri; plan, Atinc'in download_media.py dogrulama fonksiyonlarina verilir."""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

import commons_search as cs
import download_plan as dp

ARAC = Path(r"C:\temp_private\corteqs\0000_newera\araclar\arac")
WM = "https://upload.wikimedia.org/wikipedia/commons/a/ab/"
TH = "https://thumb.wikimedia.org/wikipedia/commons/thumb/a/ab/"
UTM = "?utm_source=commons.wikimedia.org&utm_campaign=imageinfo&utm_content="


def row(i, entry="eindhoven:van-abbemuseum", url=None, **extra):
    return {"photo_id": f"eindhoven:foto:{i}", "entry_id": entry, "original_url": url or f"{WM}Van_{i}.JPG",
            "thumb_url": f"{WM}thumb/Van_{i}.jpg/1600px-Van_{i}.jpg", **extra}


def row26(i, width=4000, **extra):
    """Wikimedia 2026 satiri (Eindhoven candidates.jsonl bicimi): utm sorgulu orijinal + thumb.wikimedia.org thumb."""
    return row(i, url=f"{WM}Van_{i}.JPG{UTM}original", width=width,
               **{"thumb_url": f"{TH}Van_{i}.JPG/1920px-Van_{i}.JPG{UTM}thumbnail", **extra})


def atinc_modules():
    if not (ARAC / "download_media.py").exists():
        pytest.skip("Atinc arac klasoru yok")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ARAC))
    try:
        import download_media as dm
        import delivery_tools as dt
    finally:
        sys.path.remove(str(ARAC))
    return dm, dt


def run_main(tmp_path, capsys, rows, *flags):
    """(cikis kodu, ozet, plan) -- main'i JSONL secimle calistirir."""
    sel, out = tmp_path / "sel.jsonl", tmp_path / "plan.json"
    sel.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    code = dp.main(["--selected", str(sel), "--city-id", "eindhoven", "--out", str(out), *flags])
    return code, json.loads(capsys.readouterr().out.strip()), json.loads(out.read_text(encoding="utf-8"))


def test_slugify_turkish_and_ascii():
    assert dp.slugify("Ğüneş Çiçek Öğle Işık İstasyon") == "gunes-cicek-ogle-isik-istasyon"
    assert dp.slugify("Strijp-S!!  Park") == "strijp-s-park"


def test_extension_ignores_query_and_normalizes():
    assert dp.extension(f"{WM}A.JPEG?x=1#f") == "jpg"
    assert dp.extension(f"{WM}A.org&utm_campaign=x") is None  # qwen hatasi: gecersiz uzanti
    assert dp.extension(f"{WM}A.png") == "png"
    assert dp.extension(f"{WM}A.tif") is None


def test_build_plan_naming_and_numbering():
    plan, errors = dp.build_plan([row(1), row(2), row(3, entry="eindhoven:philips-stadion")], "eindhoven")
    assert errors == []
    assert [p["original_file"] for p in plan] == [
        "Fotoğraflar/eindhoven_van-abbemuseum_01.jpg", "Fotoğraflar/eindhoven_van-abbemuseum_02.jpg",
        "Fotoğraflar/eindhoven_philips-stadion_01.jpg"]
    assert set(plan[0]) == {"photo_id", "original_file", "downloaded_file_url"}
    assert plan[0]["downloaded_file_url"] == f"{WM}Van_1.JPG"


def test_ext_fallback_from_filename_field():
    plan, errors = dp.build_plan([row(1, url=f"{WM}noext?x=1", filename="a.PNG")], "eindhoven")
    assert errors == [] and plan[0]["original_file"].endswith("_01.png")


def test_rejections():
    rows = [row(1, url="https://example.org/a.jpg"), row(2, url="http://upload.wikimedia.org/a.jpg"),
            row(3, url=f"{WM}A.org&utm=1"), {"entry_id": "e:x"}, row(5, entry="")]
    plan, errors = dp.build_plan(rows, "eindhoven")
    assert plan == [] and len(errors) == 5


def test_port_and_malformed_urls_rejected_without_crash():
    # Atinc public_url 443 disi portu reddeder: planda kalirsa kuyruk ilk satirda tumden durur. Bozuk adres cokertmez.
    rows = [row(1, url="https://upload.wikimedia.org:8443/wikipedia/commons/a/ab/Van_1.JPG"),
            row(2, url="https://upload.wikimedia.org:abc/wikipedia/commons/a/ab/Van_2.JPG"),
            row(3, url="https://[::1/wikipedia/commons/a/ab/Van_3.JPG"), row(4, url=5)]
    plan, errors = dp.build_plan(rows, "eindhoven")
    assert plan == [] and len(errors) == 4 and all("izin verilmeyen indirme adresi" in e for e in errors)
    plan, errors = dp.build_plan([row(5, url="https://upload.wikimedia.org:443/wikipedia/commons/a/ab/Van_5.JPG")],
                                 "eindhoven")
    assert errors == [] and len(plan) == 1


def test_query_dropped_only_on_wikimedia_hosts():
    # A3 yalniz Commons/Wikimedia icin: imzali CDN (?itok=, ?sig=) ya da Unsplash (?fm=&w=) sorgusu silinirse
    # 403/404 ya da baska bicim/boyutta dosya gelir, hata mesaji cikmaz
    urls = ["https://cdn.example.org/foto.jpg?itok=AbC1", "https://cdn.example.org/b.png?sig=x#f",
            "https://images.unsplash.com/photo-1506744038136?fm=jpg&w=1600", "https://notwikimedia.org/c.jpg?sig=2"]
    hosts = (*dp.DEFAULT_HOSTS, "cdn.example.org", "images.unsplash.com", "notwikimedia.org")
    plan, errors = dp.build_plan([*(row(i, url=u, ext="jpg") for i, u in enumerate(urls, start=1)), row26(5)],
                                 "eindhoven", allow_hosts=hosts)
    assert errors == []
    assert [p["downloaded_file_url"] for p in plan] == [*urls, f"{WM}Van_5.JPG"]


def test_allow_host():
    r = row(1, url="https://example.org/a.jpg")
    plan, errors = dp.build_plan([r], "eindhoven", allow_hosts=("example.org",))
    assert errors == [] and len(plan) == 1


def test_duplicate_photo_id_rejected():
    plan, errors = dp.build_plan([row(1), row(1)], "eindhoven")
    assert len(plan) == 1 and "yinelenen photo_id" in errors[0]


def test_same_url_for_two_photos_is_allowed():
    plan, errors = dp.build_plan([row(1), row(2, url=f"{WM}Van_1.JPG")], "eindhoven")
    assert errors == [] and len(plan) == 2


def test_slug_collision_numbers_do_not_collide():
    plan, errors = dp.build_plan([row(1, entry="e:a b"), row(2, entry="e:a-b")], "eindhoven")
    assert errors == [] and len({p["original_file"] for p in plan}) == 2


def test_main_writes_plan_and_summary(tmp_path, capsys):
    sel = tmp_path / "sel.jsonl"
    sel.write_text("\n".join(json.dumps(r) for r in [row(1), row(2)]) + "\n", encoding="utf-8")
    out = tmp_path / "plan.json"
    assert dp.main(["--selected", str(sel), "--city-id", "eindhoven", "--out", str(out)]) == 0
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["plan_rows"] == 2 and summary["errors"] == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 2


def test_main_errors_exit_1_and_usage_exit_2(tmp_path, capsys):
    sel = tmp_path / "sel.jsonl"
    sel.write_text(json.dumps(row(1, url="https://example.org/a.jpg")) + "\n", encoding="utf-8")
    args = ["--selected", str(sel), "--city-id", "eindhoven", "--out", str(tmp_path / "p.json")]
    assert dp.main(args) == 1
    assert dp.main(["--selected", str(tmp_path / "none.jsonl"), "--city-id", "e", "--out", str(tmp_path / "p.json")]) == 2
    assert dp.main(["--selected", str(sel), "--city-id", "Bad City", "--out", str(tmp_path / "p.json")]) == 2
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{oops\n", encoding="utf-8")
    assert dp.main(["--selected", str(bad), "--city-id", "e", "--out", str(tmp_path / "p.json")]) == 2


def test_default_hosts_include_thumb_host():
    assert set(dp.DEFAULT_HOSTS) == {"upload.wikimedia.org", "thumb.wikimedia.org"}
    plan, errors = dp.build_plan([row(1, url=f"{TH}Van_1.JPG/1280px-Van_1.JPG")], "eindhoven")
    assert errors == [] and plan[0]["downloaded_file_url"] == f"{TH}Van_1.JPG/1280px-Van_1.JPG"


def test_downloaded_url_has_no_query_and_ext_from_path():
    plan, errors = dp.build_plan([row26(1), row(2, url=f"{WM}B.png?f=x.jpg#a")], "eindhoven")
    assert errors == []
    assert [p["downloaded_file_url"] for p in plan] == [f"{WM}Van_1.JPG", f"{WM}B.png"]
    assert [p["original_file"] for p in plan] == [
        "Fotoğraflar/eindhoven_van-abbemuseum_01.jpg", "Fotoğraflar/eindhoven_van-abbemuseum_02.png"]


def test_prefer_thumb_uses_1280_thumb_only_for_wider_originals():
    rows = [row26(1, width=4000), row26(2, width=1280), row26(3, width=900), row26(4, width=None), row26(5, width="1500")]
    plan, errors = dp.build_plan(rows, "eindhoven", prefer_thumb=True)
    assert errors == []
    assert [p["downloaded_file_url"] for p in plan] == [
        f"{TH}Van_1.JPG/1280px-Van_1.JPG", f"{WM}Van_2.JPG", f"{WM}Van_3.JPG", f"{WM}Van_4.JPG",
        f"{TH}Van_5.JPG/1280px-Van_5.JPG"]
    assert plan[0]["original_file"] == "Fotoğraflar/eindhoven_van-abbemuseum_01.jpg"
    default_plan, _ = dp.build_plan(rows, "eindhoven")  # bayrak yoksa hep orijinal
    assert [p["downloaded_file_url"] for p in default_plan] == [f"{WM}Van_{i}.JPG" for i in range(1, 6)]


def thumb_on(netloc, i, scheme="https"):
    """TH dosya duzeninde Van_<i>.JPG thumb'i, baska alan/port/sema ile."""
    return f"{scheme}://{netloc}/wikipedia/commons/thumb/a/ab/Van_{i}.JPG/1920px-Van_{i}.JPG"


def test_prefer_thumb_falls_back_to_original_when_thumb_unusable():
    rows = [row26(1, thumb_url=None),  # thumb yok
            row26(2, thumb_url=f"{WM}Van_2.JPG{UTM}thumbnail_unscaled"),  # thumb degil, orijinalin kendisi
            row26(3, thumb_url=thumb_on("evil.example", 3)),  # izinsiz alan
            row26(4, thumb_url=thumb_on("thumb.wikimedia.org", 4, scheme="http")),
            row26(5, thumb_url=f"{TH}Van_5.JPG/page1-1920px-Van_5.JPG.jpg"),  # standart disi thumb adi
            row(6, url=f"{WM}Van_6.webp", thumb_url=f"{TH}Van_6.webp/1920px-Van_6.webp.png", width=4000),  # bicim
            row26(7, thumb_url=f"{WM}1920px-Van_7.JPG"),  # thumb adi var, /thumb/ klasoru yok
            row26(8, thumb_url=f"{WM}Van_8.JPG/1920px-Van_8.JPG"),  # dosya klasoru dogru, /thumb/ yok: uydurma adres
            row26(9, thumb_url=thumb_on("thumb.wikimedia.org:8443", 9)),  # Atinc kuyrugu 443 disi portu reddeder
            row26(10, thumb_url=thumb_on("[::1", 10))]  # bozuk adres (cozulemez)
    plan, errors = dp.build_plan(rows, "eindhoven", prefer_thumb=True)
    assert errors == []
    assert [p["downloaded_file_url"] for p in plan] == [f"{WM}Van_{i}.{'webp' if i == 6 else 'JPG'}"
                                                        for i in range(1, 11)]
    assert plan[5]["original_file"].endswith("_06.webp")
    # thumb alani izinli degil / izinli ama Wikimedia disi (boyut adresi yalniz Wikimedia'da yazilir) -> orijinal
    hosts = (*dp.DEFAULT_HOSTS, "mirror.example")
    only_upload, _ = dp.build_plan([row26(11)], "eindhoven", allow_hosts=("upload.wikimedia.org",), prefer_thumb=True)
    mirrored, _ = dp.build_plan([row26(12, thumb_url=thumb_on("mirror.example", 12))], "eindhoven", allow_hosts=hosts,
                                prefer_thumb=True)
    assert [only_upload[0]["downloaded_file_url"], mirrored[0]["downloaded_file_url"]] == [
        f"{WM}Van_11.JPG", f"{WM}Van_12.JPG"]


def test_prefer_thumb_only_uses_a_thumb_of_the_same_file():
    # K81 (incelenen kare = teslim edilen kare): baska dosyanin (B) thumb'i A'nin adi, lisansi ve kaynagiyla inmesin
    rows = [row26(1, thumb_url=f"{TH}Other_1.JPG/1920px-Other_1.JPG"),  # ayni hash dizini, baska dosya
            row26(2, thumb_url=f"{TH.replace('/a/ab/', '/c/cd/')}Van_2.JPG/1920px-Van_2.JPG"),  # ayni ad, baska dizin
            row26(3, thumb_url=f"{TH.replace('/commons/', '/en/')}Van_3.JPG/1920px-Van_3.JPG"),  # baska proje
            row26(4, thumb_url=f"{TH}Van_4.JPG/1920px-thumbnail.JPG"),  # uzun adli dosyada Commons thumb adi boyle
            row(5, url=f"{WM}Van%2C_5.JPG", width=4000, thumb_url=f"{TH}Van,_5.JPG/1920px-Van,_5.JPG")]  # kodlama farki
    plan, errors = dp.build_plan(rows, "eindhoven", prefer_thumb=True)
    assert errors == []
    assert [p["downloaded_file_url"] for p in plan] == [
        f"{WM}Van_1.JPG", f"{WM}Van_2.JPG", f"{WM}Van_3.JPG", f"{TH}Van_4.JPG/1280px-thumbnail.JPG",
        f"{TH}Van,_5.JPG/1280px-Van,_5.JPG"]


def test_main_counts_rows_without_thumb_data(tmp_path, capsys):
    # belgelenen selected.jsonl semasinda width/thumb_url yok: bayrak sessizce hicbir sey yapmasin istemiyoruz
    bare = {k: v for k, v in row26(5).items() if k not in ("width", "thumb_url")}
    rows = [row26(1), row26(2, width=None), row26(3, thumb_url=None), row26(4, width=900, thumb_url=None), bare,
            row26(6, thumb_url=""), row26(7, width="abc")]
    code, summary, _ = run_main(tmp_path, capsys, rows, "--prefer-thumb")
    assert code == 0 and summary["prefer_thumb"] is True
    assert summary["thumb_rows"] == 1 and summary["thumb_skipped_missing"] == 5  # 900 px'lik satir eksik sayilmaz
    code, summary, _ = run_main(tmp_path, capsys, rows)
    assert code == 0 and summary["prefer_thumb"] is False and summary["thumb_skipped_missing"] == 0


def test_main_counts_original_urls_that_are_thumbs(tmp_path, capsys):
    # v7 'teslim edilen dosya orijinaldir': olcekli kopya original_url olarak hatasiz gecer (davranis ayni) ama sayilir
    old_style = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Van_2.JPG/960px-Van_2.JPG"
    code, summary, plan = run_main(tmp_path, capsys, [row(1, url=f"{TH}Van_1.JPG/1280px-Van_1.JPG"),
                                                     row(2, url=old_style), row(3)])
    assert code == 0 and summary["errors"] == 0 and len(plan) == 3
    assert summary["original_is_thumb"] == 2 and summary["thumb_rows"] == 2


def test_plan_script_stays_off_the_network_client():
    # plan scripti ag kullanmaz: ag istemcisi (commons_search) ya da ag kutuphanesi yuklenmez; 1280 iki scriptte ayni
    tree = ast.parse(Path(dp.__file__).read_text(encoding="utf-8"))
    imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    imported |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    assert not imported & {"commons_search", "urllib.request", "http.client", "socket"}
    assert dp.THUMB_WIDTH == cs.DEFAULT_THUMB_WIDTH == 1280


UT = "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/"  # eski bicim: upload alaninda thumb klasoru


def test_standard_widths_are_wikimedias_2026_thumbnail_steps():
    # mediawiki.org "Common thumbnail sizes" (Commons, Ocak 2026): dogrudan istekte yalniz bunlar; 1600 = HTTP 400
    assert dp.STANDARD_WIDTHS == (20, 40, 60, 120, 250, 330, 500, 960, 1280, 1920, 3840)
    assert dp.THUMB_WIDTH in dp.STANDARD_WIDTHS and 1600 not in dp.STANDARD_WIDTHS
    assert [dp.thumb_width(u) for u in (f"{UT}A.jpg/1600px-A.jpg?x=1", f"{TH}A.tif/lossy-page1-960px-A.tif.jpg",
                                        f"{WM}A.jpg", f"{WM}1600px-A.jpg", 5)] == [1600, 960, None, None, None]


def test_wide_or_nonstandard_thumb_in_original_url_never_reaches_the_plan():
    """original_url'in kendisi standart disi (1600 px: HTTP 400) ya da 1280'den genis thumb ise plana girmez: ayni
    dosyanin ozgun adresine cevrilir (thumb klasorunun tersi; K81 ayni dosya), teslim kurali ondan uygulanir
    (--prefer-thumb: 1280 px). Ozgun adres cikarilamazsa (hash klasoru yok/tutarsiz, bicim desteklenmiyor) satir
    reddedilir. Standart ve en cok 1280 px thumb eskisi gibi aynen kalir (original_is_thumb)."""
    rows = [row(1, url=f"{UT}Van_1.JPG/1600px-Van_1.JPG{UTM}x", width=4000, thumb_url=f"{TH}Van_1.JPG/1920px-Van_1.JPG"),
            row(2, url=f"{TH}Van_2.JPG/1600px-Van_2.JPG", width=4000, thumb_url=None),
            row(3, url=f"{TH}Van_3.JPG/1920px-Van_3.JPG", width=4000, thumb_url=f"{TH}Van_3.JPG/1920px-Van_3.JPG"),
            row(4, url=f"{TH}Van_4.JPG/960px-Van_4.JPG", width=4000),
            row(5, url="https://upload.wikimedia.org/wikipedia/commons/thumb/Van_5.JPG/1600px-Van_5.JPG"),  # hash yok
            row(6, url=f"{UT.replace('/a/ab/', '/a/cd/')}Van_6.JPG/1600px-Van_6.JPG"),  # 'cd' 'a' ile baslamaz
            row(7, url=f"{UT}Doc_7.tif/lossy-page1-1600px-Doc_7.tif.jpg", width=4000)]  # ozgun tif: bicim yok
    plan, errors, stats = dp.build_plan_detail(rows, "eindhoven")
    assert [p["downloaded_file_url"] for p in plan] == [
        f"{WM}Van_1.JPG", f"{WM}Van_2.JPG", f"{WM}Van_3.JPG", f"{TH}Van_4.JPG/960px-Van_4.JPG"]
    assert [p["original_file"][-6:] for p in plan] == ["01.jpg", "02.jpg", "03.jpg", "04.jpg"]
    assert [e.split(":", 1)[0] for e in errors] == ["satir 5", "satir 6", "satir 7"]
    assert all("ozgun dosya adresi cikarilamadi" in e and "1600 px" in e for e in errors[:2])
    assert "gecersiz uzanti" in errors[2] and f"{UT}Doc_7.tif/lossy-page1-1600px-Doc_7.tif.jpg" in errors[2]
    assert (stats["original_thumb_fixed"], stats["original_is_thumb"]) == (3, 1)
    prefer, prefer_errors, _ = dp.build_plan_detail(rows, "eindhoven", prefer_thumb=True)
    assert [p["downloaded_file_url"] for p in prefer] == [  # 2: thumb_url yok, 1280 px verilen thumb'dan
        f"{TH}Van_1.JPG/1280px-Van_1.JPG", f"{TH}Van_2.JPG/1280px-Van_2.JPG", f"{TH}Van_3.JPG/1280px-Van_3.JPG",
        f"{TH}Van_4.JPG/960px-Van_4.JPG"]
    assert len(prefer_errors) == 3
    urls = [p["downloaded_file_url"] for p in plan + prefer]
    assert all(dp.thumb_width(u) in (None, *dp.STANDARD_WIDTHS) and (dp.thumb_width(u) or 0) <= dp.THUMB_WIDTH
               for u in urls)


def test_prefer_thumb_scales_a_fixed_thumb_original_when_thumb_url_is_unusable():
    """original_url ayni dosyanin standart disi (1600 px) thumb'i, thumb_url yok ya da kullanilamaz: --prefer-thumb'da
    1280 px kopya verilen adresten turetilir (ayni dosya olusu standard_original'da dogrulandi; tam boy ozgun dosya
    inmez) ve thumb_skipped_missing sayilmaz. Genisligi bilinmeyen satir ve bayraksiz plan ozgun dosyayi indirir."""
    rows = [row(1, url=f"{TH}Van_1.JPG/1600px-Van_1.JPG", width=4000, thumb_url=None),
            row(2, url=f"{UT}Van_2.JPG/1600px-Van_2.JPG{UTM}x", width=4000, thumb_url=""),  # eski bicim: upload alani
            row(3, url=f"{TH}Van_3.JPG/1600px-Van_3.JPG", width=4000, thumb_url=f"{TH}Other_3.JPG/1920px-Other_3.JPG"),
            row(4, url=f"{TH}Van_4.JPG/1600px-Van_4.JPG", width=None, thumb_url=None)]
    plan, errors, stats = dp.build_plan_detail(rows, "eindhoven", prefer_thumb=True)
    assert errors == [] and [p["downloaded_file_url"] for p in plan] == [
        f"{TH}Van_1.JPG/1280px-Van_1.JPG", f"{UT}Van_2.JPG/1280px-Van_2.JPG", f"{TH}Van_3.JPG/1280px-Van_3.JPG",
        f"{WM}Van_4.JPG"]
    assert (stats["original_thumb_fixed"], stats["thumb_skipped_missing"]) == (4, 1)  # yalniz genisligi bilinmeyen
    default, _ = dp.build_plan(rows, "eindhoven")
    assert [p["downloaded_file_url"] for p in default] == [f"{WM}Van_{i}.JPG" for i in range(1, 5)]


def test_thumb_original_fix_keeps_the_hosts_rules():
    # yalniz upload/thumb.wikimedia.org thumb'i cevrilir; kimlik bilgili, http ya da izinsiz alan eskisi gibi reddedilir
    rows = [row(1, url=f"{UT.replace('https://', 'https://u:p@')}Van_1.JPG/1600px-Van_1.JPG"),
            row(2, url=f"{UT.replace('https:', 'http:')}Van_2.JPG/1600px-Van_2.JPG"),
            row(3, url="https://mirror.example/wikipedia/commons/thumb/a/ab/Van_3.JPG/1600px-Van_3.JPG", ext="jpg")]
    plan, errors = dp.build_plan(rows, "eindhoven")
    assert plan == [] and len(errors) == 3 and all("izin verilmeyen indirme adresi" in e for e in errors)
    plan, errors = dp.build_plan([rows[2]], "eindhoven", allow_hosts=(*dp.DEFAULT_HOSTS, "mirror.example"))
    assert errors == [] and plan[0]["downloaded_file_url"] == rows[2]["original_url"]  # Wikimedia disi: dokunulmaz
    only_thumb_host, errors = dp.build_plan([row(4, url=f"{TH}Van_4.JPG/1600px-Van_4.JPG")], "eindhoven",
                                            allow_hosts=("thumb.wikimedia.org",))
    assert only_thumb_host == [] and "izin verilmeyen indirme adresi" in errors[0]  # ozgun dosyanin alani izinli degil


def test_main_reports_fixed_and_rejected_thumb_originals(tmp_path, capsys):
    rows = [row(1, url=f"{UT}Van_1.JPG/1600px-Van_1.JPG", width=4000, thumb_url=f"{TH}Van_1.JPG/1280px-Van_1.JPG"),
            row(2, url="https://upload.wikimedia.org/wikipedia/commons/thumb/Van_2.JPG/1600px-Van_2.JPG")]
    code, summary, plan = run_main(tmp_path, capsys, rows, "--prefer-thumb")
    assert code == 1 and (summary["original_thumb_fixed"], summary["errors"], summary["plan_rows"]) == (1, 1, 1)
    assert [p["downloaded_file_url"] for p in plan] == [f"{TH}Van_1.JPG/1280px-Van_1.JPG"]
    assert "1600 px" in summary["error_list"][0] and "/1600px-" not in json.dumps(plan)


def test_main_prefer_thumb_flag_and_summary(tmp_path, capsys):
    sel = tmp_path / "sel.jsonl"
    sel.write_text("\n".join(json.dumps(r) for r in [row26(1), row26(2, width=800)]) + "\n", encoding="utf-8")
    out = tmp_path / "plan.json"
    base = ["--selected", str(sel), "--city-id", "eindhoven", "--out", str(out)]
    assert dp.main(base) == 0
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["thumb_rows"] == 0 and summary["download_hosts"] == ["upload.wikimedia.org"]
    assert dp.main([*base, "--prefer-thumb"]) == 0
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["thumb_rows"] == 1 and summary["download_hosts"] == ["thumb.wikimedia.org", "upload.wikimedia.org"]
    urls = [p["downloaded_file_url"] for p in json.loads(out.read_text(encoding="utf-8"))]
    assert urls == [f"{TH}Van_1.JPG/1280px-Van_1.JPG", f"{WM}Van_2.JPG"]


@pytest.mark.real
def test_thumb_plan_needs_thumb_host_in_atinc_queue(tmp_path):
    dm, dt = atinc_modules()
    plan, errors = dp.build_plan([row26(1), row26(2, width=900)], "eindhoven", prefer_thumb=True)
    assert errors == []
    for r in plan:  # download_media ... --allow-host thumb.wikimedia.org
        assert dt.local_file(tmp_path, r["original_file"]).is_relative_to(tmp_path.resolve())
        assert dm.public_url(r["downloaded_file_url"], {"upload.wikimedia.org", "thumb.wikimedia.org"}, resolve=False)
    with pytest.raises(ValueError):  # bayraksiz resmi kuyruk (yalniz upload) thumb'i reddeder
        dm.public_url(plan[0]["downloaded_file_url"], {"upload.wikimedia.org"}, resolve=False)


@pytest.mark.real
def test_plan_accepts_exactly_what_atinc_queue_accepts():
    dm, _ = atinc_modules()
    hosts = ("upload.wikimedia.org", "thumb.wikimedia.org")
    urls = [f"{WM}A.jpg", "https://upload.wikimedia.org:443/b.jpg", "https://upload.wikimedia.org:8443/c.jpg",
            "https://upload.wikimedia.org:abc/d.jpg", "http://upload.wikimedia.org/e.jpg",
            "https://u:p@upload.wikimedia.org/f.jpg", "https://example.org/g.jpg", f"{TH}H.jpg/1280px-H.jpg"]

    def atinc_accepts(url):
        try:
            return bool(dm.public_url(url, set(hosts), resolve=False))
        except ValueError:
            return False

    plan, _ = dp.build_plan([row(i, url=u) for i, u in enumerate(urls, start=1)], "eindhoven", allow_hosts=hosts)
    assert [p["downloaded_file_url"] for p in plan] == [u for u in urls if atinc_accepts(u)]


@pytest.mark.real
def test_plan_passes_atinc_validation(tmp_path):
    dm, dt = atinc_modules()
    plan, errors = dp.build_plan([row(1), row(2), row(3, entry="eindhoven:strijp-s")], "eindhoven")
    assert errors == []
    assert len({r["photo_id"] for r in plan}) == len(plan)
    for r in plan:
        target = dt.local_file(tmp_path, r["original_file"])
        assert target.is_relative_to(tmp_path.resolve())
        assert dm.public_url(r["downloaded_file_url"], {"upload.wikimedia.org"}, resolve=False)
