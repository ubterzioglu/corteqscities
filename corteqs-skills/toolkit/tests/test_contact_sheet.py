"""contact_sheet testleri."""
from __future__ import annotations

import itertools
import json

import pytest
from PIL import Image, ImageChops, ImageDraw

import contact_sheet as cs

LONG_LABEL = "DAF Museum · DAF Museum, Eindhoven (16061771014).jpg"
EDGE_LABEL = "Ğİ Çarşı gjpqy (Ünye) · DAF Museum, Eindhoven.jpg"  # uzun + ustten/alttan tasan glifler


@pytest.fixture()
def drawn(monkeypatch):
    """ImageDraw.text cagrilarini (konum, metin, font, anchor) kaydeder; cizim yine yapilir."""
    calls = []
    original = ImageDraw.ImageDraw.text

    def spy(self, xy, text, *args, **kwargs):
        font = kwargs.get("font") or (args[1] if len(args) > 1 else None)
        calls.append({"xy": xy, "y": xy[1], "text": text, "font": font,
                      "size": getattr(font, "size", 0), "anchor": kwargs.get("anchor")})
        return original(self, xy, text, *args, **kwargs)

    monkeypatch.setattr(ImageDraw.ImageDraw, "text", spy)
    return calls


def _bbox(call):
    """Kaydedilen yazinin piksel kutusu (sol, ust, sag, alt)."""
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    return measure.textbbox(call["xy"], call["text"], font=call["font"], anchor=call["anchor"])


def _labels(calls):
    """Cizim sirasiyla (buyuk, kucuk) etiket metinleri; yer tutucu metni haric."""
    caption = [c for c in calls if c["text"] != cs.PLACEHOLDER_TEXT]
    big = max(c["size"] for c in caption)
    return [c["text"] for c in caption if c["size"] == big], [c["text"] for c in caption if c["size"] < big]


def _img(path, color, size=(300, 200), box=None):
    img = Image.new("RGB", size, color)
    if box:
        ImageDraw.Draw(img).rectangle(box, fill=(255, 255, 255))
    img.save(path)
    return path


def _items(tmp_path, n, groups=None):
    rows = []
    for i in range(n):
        p = _img(tmp_path / f"i{i}.png", (i * 9 % 256, 40, 90), box=(i * 7 % 200, 10, i * 7 % 200 + 40, 100))
        row = {"key": i + 1, "path": str(p), "label": f"Şişli Ğ İ place {i}"}
        if groups:
            row["group"] = groups[i]
        rows.append(row)
    return rows


def _write(tmp_path, rows):
    f = tmp_path / "items.jsonl"
    f.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows), encoding="utf-8")
    return f


def _run(tmp_path, rows, *extra):
    out = tmp_path / "out"
    code = cs.main(["--items", str(_write(tmp_path, rows)), "--out-dir", str(out), *extra])
    return code, out


def test_truncate_label_drops_city_id_prefix():
    # 'eindhoven:' gibi tekrar eden kimlik oneki etiketi yer kaplamasin; bosluklu metindeki ':' korunur
    assert cs.truncate_label("eindhoven:cafe-100-watt Mekân") == "cafe-100-watt Mekân"
    assert cs.truncate_label("eindhoven:foto:yer-01 Kapak") == "yer-01 Kapak"
    assert cs.truncate_label("Not: kapak") == "Not: kapak"


def test_default_dhash_threshold_is_5():
    assert cs.build_parser().get_default("dhash_threshold") == 5


def test_truncate_label():
    assert cs.truncate_label("kısa", 28) == "kısa"
    t = cs.truncate_label("x" * 40, 28)
    assert len(t) == 28 and t.endswith("…")


def test_order_by_group_keeps_adjacent():
    rows = [{"key": 1, "group": "A"}, {"key": 2, "group": "B"}, {"key": 3, "group": "A"}, {"key": 4}]
    ordered = cs.order_by_group(rows)
    assert [r["key"] for r in ordered] == [1, 3, 2, 4]
    assert [r["key"] for r in rows] == [1, 2, 3, 4]  # girdi degismez


def test_font_loads_and_renders_turkish():
    font = cs.load_font(20)
    assert font.getlength("Şişli Ğ İ") > 0


def test_main_makes_sheets_and_summary(tmp_path, capsys):
    code, out = _run(tmp_path, _items(tmp_path, 7), "--per-sheet", "3", "--cols", "3", "--tile", "128")
    assert code == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1
    summary = json.loads(lines[0])
    assert summary["sheets"] == 3 and summary["errors"] == 0
    assert summary["total_est_tokens"] == sum(s["est_tokens"] for s in json.loads((out / "sheets.json").read_text("utf-8")))
    for n in (1, 2, 3):
        assert (out / f"sheet_{n:02d}.jpg").exists()
    sheets = json.loads((out / "sheets.json").read_text("utf-8"))
    assert [len(s["items"]) for s in sheets] == [3, 3, 1]
    assert sheets[0]["items"][0]["slot"] == 1 and sheets[0]["items"][0]["key"] == 1
    w, h = Image.open(out / "sheet_01.jpg").size
    assert sheets[0]["est_tokens"] == round(w * h / 750)


def test_dhash_json_pairs_within_and_across(tmp_path):
    rows = _items(tmp_path, 3, groups=["g1", "g1", "g2"])
    rows[1]["path"] = str(_img(tmp_path / "dup.png", (0, 40, 90), box=(0, 10, 40, 100)))
    rows[0]["path"] = str(_img(tmp_path / "orig.png", (0, 40, 90), box=(0, 10, 40, 100)))
    rows[2]["path"] = str(_img(tmp_path / "dup2.png", (0, 40, 90), box=(0, 10, 40, 100)))
    code, out = _run(tmp_path, rows)
    d = json.loads((out / "dhash.json").read_text("utf-8"))
    assert len(d["hashes"]) == 3
    assert any(p["same_group"] for p in d["pairs"])
    assert any(not p["same_group"] for p in d["pairs"])


def test_corrupt_image_gives_placeholder_and_exit1(tmp_path, capsys):
    rows = _items(tmp_path, 2)
    bad = tmp_path / "bad.png"
    bad.write_bytes(b"not an image")
    rows[1]["path"] = str(bad)
    rows.append({"key": 9, "path": str(tmp_path / "missing.png"), "label": "yok"})
    code, out = _run(tmp_path, rows)
    assert code == 1
    summary = json.loads(capsys.readouterr().out.strip())
    assert summary["errors"] == 2
    sheets = json.loads((out / "sheets.json").read_text("utf-8"))
    assert [i["key"] for i in sheets[0]["items"]] == [1, 2, 9]
    assert (out / "sheet_01.jpg").exists()
    assert {e["key"] for e in json.loads((out / "dhash.json").read_text("utf-8"))["errors"]} == {2, 9}


@pytest.mark.parametrize("broken", [False, True])
def test_render_tile_big_label_is_slot_number(tmp_path, drawn, broken):
    # A10: buyuk etiket = paftadaki konum (slot); kucuk etiket = mevcut label (mekan · dosya). Bozuk karoda da.
    path = tmp_path / "t.png"
    if broken:
        path.write_bytes(b"bozuk")
    else:
        _img(path, (10, 120, 200))
    _, error = cs.render_tile(str(path), 256, 7, LONG_LABEL)
    assert (error is not None) is broken
    caption = [c for c in drawn if c["text"] != cs.PLACEHOLDER_TEXT]
    assert len(caption) == 2
    big, small = sorted(caption, key=lambda c: -c["size"])
    assert big["text"] == "7"
    assert small["text"] == "DAF Museum · DAF Museum, Ei…"  # 28 karakter; varsayilan 256'da sigar
    assert big["size"] > small["size"] and big["y"] < small["y"]


@pytest.mark.parametrize("broken", [False, True])
@pytest.mark.parametrize("tile", [64, 128, 256])
def test_caption_fits_tile_and_slot_is_biggest(tmp_path, drawn, tile, broken):
    # her karo boyunda: buyuk yazi numara; numara ile etiket ust uste binmez; hicbir yazi karodan tasmaz
    path = tmp_path / "t.png"
    if broken:
        path.write_bytes(b"bozuk")
    else:
        _img(path, (10, 120, 200))
    canvas, _ = cs.render_tile(str(path), tile, 20, EDGE_LABEL)
    number, label = [c for c in drawn if c["text"] != cs.PLACEHOLDER_TEXT]
    assert number["text"] == "20" and number["size"] > label["size"]
    assert len(label["text"]) >= 5 and EDGE_LABEL.startswith(label["text"].removesuffix("…"))
    assert _bbox(number)[3] <= _bbox(label)[1]
    for call in drawn:
        left, top, right, bottom = _bbox(call)
        assert 0 <= left and right <= canvas.width and 0 <= top and bottom <= canvas.height, (call["text"], tile)


def test_fit_label_cuts_to_pixel_width():
    font = cs.load_font(11)
    assert cs.fit_label("kısa", font, 200) == "kısa"
    assert cs.fit_label(LONG_LABEL, font, 10_000) == "DAF Museum · DAF Museum, Ei…"  # LABEL_MAX yine gecerli
    cut = cs.fit_label(LONG_LABEL, font, 60)
    assert cut.endswith("…") and LONG_LABEL.startswith(cut[:-1]) and len(cut) > 3
    assert font.getlength(cut) <= 60


def test_slot_number_is_painted_in_caption_band(tmp_path):
    path = str(_img(tmp_path / "t.png", (10, 120, 200)))
    one, _ = cs.render_tile(path, 128, 1, LONG_LABEL)
    two, _ = cs.render_tile(path, 128, 2, LONG_LABEL)
    box = ImageChops.difference(one, two).getbbox()
    assert box is not None and box[1] >= int(128 * 0.75)  # fark yalniz alttaki etiket seridinde


def test_sheet_slot_labels_match_sheets_json(tmp_path, drawn):
    # gruplama sirayi degistirir; paftadaki numara yine sheets.json'daki slot -> key/label eslesmesini verir
    rows = _items(tmp_path, 7, groups=["a", "b", "a", "c", "b", "a", "c"])
    rows = [{**r, "key": f"eindhoven:mekan-{r['key']}|File:F{r['key']}.jpg"} for r in rows]
    code, out = _run(tmp_path, rows, "--per-sheet", "4", "--cols", "2", "--tile", "128")
    assert code == 0
    items = [it for s in json.loads((out / "sheets.json").read_text("utf-8")) for it in s["items"]]
    assert all(set(it) == {"slot", "key", "path", "label"} for it in items)  # sheets.json bicimi ayni
    big, small = _labels(drawn)
    assert big == [str(it["slot"]) for it in items] == ["1", "2", "3", "4", "1", "2", "3"]
    assert small == [it["label"] for it in items]  # kisa etiketler oldugu gibi yazilir
    assert not any("mekan-" in c["text"] for c in drawn)  # aday kimligi karoya yazilmaz


def test_slot_numbers_come_only_from_sheet_items(tmp_path, drawn, monkeypatch):
    # numara tek yerde uretilir: numaralama degisirse (or. paftalar boyunca surerse) resim ve sheets.json birlikte degisir
    original, counter = cs.sheet_items, itertools.count(1)
    monkeypatch.setattr(cs, "sheet_items", lambda chunk: [{**it, "slot": next(counter)} for it in original(chunk)])
    code, out = _run(tmp_path, _items(tmp_path, 5), "--per-sheet", "2", "--cols", "2", "--tile", "128")
    assert code == 0
    slots = [it["slot"] for s in json.loads((out / "sheets.json").read_text("utf-8")) for it in s["items"]]
    assert slots == [1, 2, 3, 4, 5]
    assert _labels(drawn)[0] == ["1", "2", "3", "4", "5"]


def test_tile_at_grid_cell_is_slot_k(tmp_path):
    # numara paftadaki konumdur: (r, c) hucresi = k = r*cols+c+1 icin render_tile ciktisi (satir satir, 1'den)
    rows, tile, cols = _items(tmp_path, 5), 128, 2
    sheet, _ = cs.build_sheet(cs.sheet_items(rows), tile, cols)
    th = cs.render_tile(rows[0]["path"], tile, 1, "")[0].height
    assert sheet.size == (cols * (tile + cs.GAP) + cs.GAP, 3 * (th + cs.GAP) + cs.GAP)
    for k in range(1, 3 * cols + 1):
        r, c = divmod(k - 1, cols)
        x, y = cs.GAP + c * (tile + cs.GAP), cs.GAP + r * (th + cs.GAP)
        cell = sheet.crop((x, y, x + tile, y + th))
        if k <= len(rows):
            expected, _ = cs.render_tile(rows[k - 1]["path"], tile, k, rows[k - 1]["label"])
            assert ImageChops.difference(cell, expected).getbbox() is None, (r, c, k)
        else:
            assert cell.getcolors() == [(tile * th, cs.BG)], (r, c, k)  # bos hucre zemin rengi


def test_sheet_pixels_do_not_depend_on_key(tmp_path):
    rows = _items(tmp_path, 4)
    renamed = [{**r, "key": f"eindhoven:baska-{r['key']}"} for r in rows]
    a, _ = cs.build_sheet(cs.sheet_items(rows), 128, 2)
    b, _ = cs.build_sheet(cs.sheet_items(renamed), 128, 2)
    assert ImageChops.difference(a, b).getbbox() is None


def test_usage_errors(tmp_path):
    with pytest.raises(SystemExit) as e:
        cs.main([])
    assert e.value.code == 2
    assert cs.main(["--items", str(tmp_path / "nope.jsonl"), "--out-dir", str(tmp_path / "o")]) == 2
    f = tmp_path / "bad.jsonl"
    f.write_text('{"key": 1}\n', encoding="utf-8")
    assert cs.main(["--items", str(f), "--out-dir", str(tmp_path / "o")]) == 2
    f.write_text("", encoding="utf-8")
    assert cs.main(["--items", str(f), "--out-dir", str(tmp_path / "o")]) == 2
    assert cs.main(["--items", str(f), "--out-dir", str(tmp_path / "o"), "--per-sheet", "0"]) == 2
