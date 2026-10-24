"""Iletisim sayfasi: cok sayida kucuk resmi etiketli tek JPEG'e dizer (vision token tasarrufu).

Kullanim: contact_sheet.py --items items.jsonl --out-dir D [--per-sheet 20] [--cols 5] [--tile 256] [--dhash-threshold 5]
Cikti: sheet_NN.jpg, sheets.json, dhash.json (yalniz --out-dir'e yazar). stdout tek satir JSON; cikis 0/1/2.
Karo etiketi: ustte buyuk slot numarasi (paftadaki konum 1..N = sheets.json 'slot'), altta kucuk label (mekan · dosya).
Her --tile boyunda numara etiketten buyuktur ve yazilar karodan tasmaz (kucuk karoda alt serit uzar, etiket erken kesilir).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, NamedTuple

from PIL import Image, ImageDraw, ImageFont

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json
from image_hash import dhash, pairs

FONT_CANDIDATES = ("segoeui.ttf", "arial.ttf", "DejaVuSans.ttf")
LABEL_MAX = 28
JPEG_QUALITY = 80
TOKEN_DIVISOR = 750
PLACEHOLDER_TEXT = "OKUNAMADI"
BG, TILE_BG, CAPTION_BG = (255, 255, 255), (235, 235, 235), (30, 30, 30)
GAP = 4
PAD, SLOT_Y = 4, 1  # yazilarin karo kenarina uzakligi; numaranin seritteki y'si
DIGITS = "0123456789"
INK_SAMPLE = "ÅÉĞİŞ|()[]_gjpqy"  # etikette en uste/en alta tasan glifler (serit yuksekligi bunlarla olculur)


class Caption(NamedTuple):
    """Karonun alt serit yerlesimi (yalniz karo boyuna bagli)."""

    height: int
    label_y: int
    slot_font: ImageFont.ImageFont
    label_font: ImageFont.ImageFont


def load_font(size: int) -> ImageFont.ImageFont:
    for name in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def truncate_label(text: str, limit: int = LABEL_MAX) -> str:
    text = " ".join(str(text or "").split())
    # 'eindhoven:foto:yer-01' gibi bosluksuz kimlik onekini at; 'Not: kapak' gibi bosluklu metin korunur
    while re.match(r"^[a-z0-9_-]+:\S", text):
        text = text.split(":", 1)[1]
    return text if len(text) <= limit else text[: limit - 1] + "…"


def order_by_group(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Ayni grup yan yana (ilk gorunme sirasina gore); grupsuzlar kendi yerinde kalir."""
    first: dict[Any, int] = {}
    keyed = []
    for idx, row in enumerate(rows):
        group = row.get("group")
        if group is not None:
            first.setdefault(group, idx)
        keyed.append((first[group] if group is not None else idx, idx, row))
    return [row for _, _, row in sorted(keyed, key=lambda t: (t[0], t[1]))]


def fit_label(text: str, font: ImageFont.ImageFont, width: int) -> str:
    """truncate_label; sonuc width pikseline sigmazsa daha erken '…' ile keser."""
    label = truncate_label(text)
    limit = len(label)
    while limit > 1 and font.getlength(label) > width:
        limit -= 1
        label = truncate_label(text, limit)
    return label


@lru_cache(maxsize=None)
def caption_layout(tile: int) -> Caption:
    """Numara etiketten en az 4 px buyuk; etiket numaranin altindan baslar, seritte biter (gerekirse serit uzar)."""
    height = int(tile * 0.30)
    small = max(11, tile // 16)
    slot_font, label_font = load_font(max(small + 4, int(height * 0.5))), load_font(small)
    _, ink_top, _, ink_bottom = label_font.getbbox(INK_SAMPLE)
    label_y = max(int(height * 0.58), SLOT_Y + slot_font.getbbox(DIGITS)[3] + 1 - ink_top)
    return Caption(max(height, label_y + ink_bottom + 1), label_y, slot_font, label_font)


def _caption(canvas: Image.Image, top: int, tile: int, slot: int, label: str) -> None:
    cap = caption_layout(tile)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, top, tile, top + cap.height], fill=CAPTION_BG)
    draw.text((PAD, top + SLOT_Y), str(slot), font=cap.slot_font, fill=(255, 220, 60))
    text = fit_label(label, cap.label_font, tile - 2 * PAD)
    draw.text((PAD, top + cap.label_y), text, font=cap.label_font, fill=(255, 255, 255))


def _placeholder(canvas: Image.Image, tile: int, img_h: int) -> None:
    """Gri 'OKUNAMADI' yer tutucu; yazi karo genisligine sigana kadar kuculur."""
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, tile, img_h], fill=(150, 150, 150))
    size = max(12, tile // 10)
    while size > 6 and load_font(size).getlength(PLACEHOLDER_TEXT) > tile - 2 * PAD:
        size -= 1
    draw.text((tile // 2, img_h // 2), PLACEHOLDER_TEXT, font=load_font(size), fill=(255, 255, 255), anchor="mm")


def render_tile(path: str | None, tile: int, slot: int, label: str) -> tuple[Image.Image, str | None]:
    """(tile_gorseli, hata). Buyuk etiket slot numarasi, kucuk etiket label. Okunamazsa gri 'OKUNAMADI' yer tutucu."""
    img_h = int(tile * 0.75)
    canvas = Image.new("RGB", (tile, img_h + caption_layout(tile).height), TILE_BG)
    error = None
    try:
        with Image.open(path) as src:
            thumb = src.convert("RGB")
        thumb.thumbnail((tile, img_h), Image.Resampling.LANCZOS)
        canvas.paste(thumb, ((tile - thumb.width) // 2, (img_h - thumb.height) // 2))
    except Exception as exc:  # bozuk/eksik/desteklenmeyen dosya: yer tutucu
        error = f"{type(exc).__name__}: {exc}"[:200]
        _placeholder(canvas, tile, img_h)
    _caption(canvas, img_h, tile, slot, label)
    return canvas, error


def sheet_items(chunk: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Bir paftanin sheets.json kayitlari. Slot numarasinin TEK kaynagi: paftadaki konum (satir satir, 1'den)."""
    return [{"slot": i, "key": r["key"], "path": r["path"], "label": r.get("label", "")} for i, r in enumerate(chunk, 1)]


def build_sheet(items: list[dict[str, Any]], tile: int, cols: int) -> tuple[Image.Image, list[str | None]]:
    """sheet_items kayitlarini sirayla satir satir dizer; karoya kaydin 'slot'u yazilir (burada numara uretilmez)."""
    tiles = [render_tile(it["path"], tile, it["slot"], it["label"]) for it in items]
    n_rows = -(-len(items) // cols)
    th = tiles[0][0].height
    sheet = Image.new("RGB", (cols * (tile + GAP) + GAP, n_rows * (th + GAP) + GAP), BG)
    for i, (img, _) in enumerate(tiles):
        sheet.paste(img, (GAP + (i % cols) * (tile + GAP), GAP + (i // cols) * (th + GAP)))
    return sheet, [err for _, err in tiles]


def read_items(path: Path) -> list[dict[str, Any]]:
    rows = []
    for no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict) or "key" not in row or "path" not in row:
            raise ValueError(f"satir {no}: 'key' ve 'path' zorunlu")
        rows.append(row)
    if not rows:
        raise ValueError("items bos")
    return rows


def compute_hashes(rows: list[dict[str, Any]], errors: dict[Any, str]) -> dict[Any, int]:
    hashes: dict[Any, int] = {}
    for row in rows:
        if row["key"] in errors:
            continue
        try:
            hashes[row["key"]] = dhash(row["path"])
        except Exception as exc:
            errors[row["key"]] = f"{type(exc).__name__}: {exc}"[:200]
    return hashes


def make_sheets(rows: list[dict[str, Any]], out_dir: Path, per_sheet: int, cols: int, tile: int) -> tuple[list[dict[str, Any]], dict[Any, str]]:
    sheets, errors = [], {}
    for n, start in enumerate(range(0, len(rows), per_sheet), 1):
        items = sheet_items(rows[start:start + per_sheet])  # resimdeki numara ile sheets.json ayni listeden
        image, errs = build_sheet(items, tile, min(cols, len(items)))
        name = f"sheet_{n:02d}.jpg"
        image.save(out_dir / name, "JPEG", quality=JPEG_QUALITY)
        errors.update({it["key"]: e for it, e in zip(items, errs) if e})
        sheets.append({
            "sheet": name, "width": image.width, "height": image.height,
            "est_tokens": round(image.width * image.height / TOKEN_DIVISOR),
            "items": items,
        })
    return sheets, errors


def build_dhash_report(rows: list[dict[str, Any]], hashes: dict[Any, int], errors: dict[Any, str], threshold: int) -> dict[str, Any]:
    group_of = {r["key"]: r.get("group") for r in rows}
    found = [
        {"a": a, "b": b, "distance": d, "same_group": group_of[a] is not None and group_of[a] == group_of[b]}
        for a, b, d in pairs(hashes, threshold)
    ]
    return {
        "threshold": threshold,
        "hashes": {str(k): f"{v:016x}" for k, v in hashes.items()},
        "pairs": found,
        "errors": [{"key": k, "error": e} for k, e in errors.items()],
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Etiketli kucuk resimlerden iletisim sayfasi uretir.")
    p.add_argument("--items", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--per-sheet", type=int, default=20)
    p.add_argument("--cols", type=int, default=5)
    p.add_argument("--tile", type=int, default=256)
    # olculen: #134/#135 uzaklik 2, #132/#133 uzaklik 4; esik 10'a kadar baska cift/yanlis pozitif yok
    p.add_argument("--dhash-threshold", type=int, default=5)
    return p


def parse_args(argv: list[str] | None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    args = parse_args(argv)
    if min(args.per_sheet, args.cols) < 1 or args.tile < 64 or args.dhash_threshold < 0:
        print("gecersiz --per-sheet/--cols/--tile/--dhash-threshold", file=sys.stderr)
        return EXIT_USAGE
    try:
        rows = order_by_group(read_items(args.items))
    except (OSError, ValueError) as exc:  # JSONDecodeError ValueError alt sinifidir
        print(f"items okunamadi: {exc}", file=sys.stderr)
        return EXIT_USAGE
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sheets, errors = make_sheets(rows, args.out_dir, args.per_sheet, args.cols, args.tile)
    hashes = compute_hashes(rows, errors)
    report = build_dhash_report(rows, hashes, errors, args.dhash_threshold)
    write_json(args.out_dir / "sheets.json", sheets)
    write_json(args.out_dir / "dhash.json", report)
    emit({
        "sheets": len(sheets), "items": len(rows), "errors": len(errors),
        "est_tokens": [s["est_tokens"] for s in sheets],
        "total_est_tokens": sum(s["est_tokens"] for s in sheets),
        "dhash_pairs": len(report["pairs"]), "out_dir": str(args.out_dir),
    })
    return EXIT_FINDINGS if errors else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
