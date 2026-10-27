"""Gorsel kalite kaniti (denetim K-C4 gercek hedef-ekran kirpmasi + netlik, K-C5 kapak sunumu). Salt okunur.

Kullanim: gorsel_kalite.py --xlsx X --pkg P --out-dir D [--ratios 16:9,4:3,1:1] [--flag-ratios 16:9,4:3]
          [--min-short 600] [--blur-threshold F]
Cikti (yalniz --out-dir'e): gorsel-kalite-v7.json (ozet + foto satirlari + isaretliler), kirpma/kirpma_NN.jpg
(her foto 16:9 ve 1:1 merkez kirpmasiyla yan yana, once kapaklar; paftada en cok 24 foto, en fazla 2400 px genislik).
--ratios'taki her oran olculur ve raporlanir; guclu kirpma isareti yalniz --flag-ratios oranlarindan gelir
(varsayilan 16:9 ve 4:3, olculenlerle kesisim). Sevilla (26.10.2026): 1:1 de isaretlenince 350 karenin 126'si yalniz
1:1 yuzunden isaretlendi; mekan karesinin 1:1 gosterildigi bir yuva bilinmiyor, 1:1 yalniz bilgi olarak kalir.
stdout tek satir JSON; cikis 0 (isaretli yok) / 1 (isaretli var) / 2 (kullanim hatasi: xlsx/pkg yok, out-dir paket icinde).
Paket klasorune ASLA yazilmaz.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any, NamedTuple

import openpyxl
from PIL import Image, ImageDraw, ImageFilter, ImageStat

import common
from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json
from contact_sheet import JPEG_QUALITY, load_font, truncate_label

REPORT_NAME = "gorsel-kalite-v7.json"
SHEET_DIR = "kirpma"
PHOTO_SHEET = "Fotoğraflar"
DEFAULT_RATIOS = "16:9,4:3,1:1"
DEFAULT_FLAG_RATIOS = "16:9,4:3"  # guclu kirpma isareti yalniz bu oranlardan (varsayilanda olculenlerle kesisim)
DEFAULT_MIN_SHORT = 600
STRONG_CROP_KEPT = 0.60  # herhangi bir oranda alanin %60'indan azi kaliyorsa guclu kirpma
COVER_RATIO = (16, 9)
COVER_MIN_KEPT = 0.75  # kapak 16:9 kirpmada alanin en az %75'ini korumali
SHARP_MAX_SIDE = 1024  # netlik olcumunden once en uzun kenar bu degere indirilir
# Netlik esigi: Laplace varyansinin (gri, <=1024 px) SABIT alt siniri. Sevilla paketinde (345 okunan foto) olculdu:
# min 95, p5 534, p10 849, medyan 2791, p90 8320. En dusuk 6 fotoya elle bakildi: hicbiri gercekten bulanik degil
# (gokyuzu/su agirlikli, detaysiz sahneler; olcu icerige bagli). Bu yuzden esik dagilimin en uc kuyrugunda (~%1)
# tutuldu: yalniz belirgin odak kaybi (sentetik bulanik < 10) ve cok detaysiz kareler isaretlenir, gozle bakilir.
# --blur-threshold ile ezilir.
BLUR_THRESHOLD = 150.0
LAPLACE_KERNEL = (0, 1, 0, 1, -4, 1, 0, 1, 0)
LAPLACE_SCALE = 2  # cekirdek ciktisi 2'ye bolunur ve 128 ofsetlenir: |laplace| > 254 kirpilir; varyans sonra x4 duzeltilir
LAPLACE_OFFSET = 128

# paftalar
PER_SHEET = 24
MAX_SHEET_WIDTH = 2400
TILE_H = 180
TILE_W = {"16:9": 320, "1:1": 180}
SHEET_RATIOS = ("16:9", "1:1")
CAPTION_H = 22
CELL_GAP = 8
PAIR_GAP = 2
BG, CAPTION_BG, FLAG_COLOR, OK_COLOR = (255, 255, 255), (30, 30, 30), (255, 120, 90), (255, 255, 255)
LABEL_MAX = 44

# neden kodlari
R_UNREADABLE, R_LOW_RES, R_STRONG, R_BLUR = "dosya_okunamadi", "dusuk_cozunurluk", "guclu_kirpma", "bulanik"
R_COVER_PORTRAIT, R_COVER_CROP = "kapak_dikey", "kapak_kirpma"
REASONS = (R_UNREADABLE, R_LOW_RES, R_STRONG, R_BLUR, R_COVER_PORTRAIT, R_COVER_CROP)


class Crop(NamedTuple):
    box: tuple[int, int, int, int]
    kept: float


def parse_ratios(text: str) -> list[tuple[str, int, int]]:
    """'16:9,4:3' -> [('16:9',16,9),('4:3',4,3)]. Gecersiz oran ValueError."""
    out = []
    for part in text.split(","):
        match = re.fullmatch(r"\s*(\d+)\s*:\s*(\d+)\s*", part)
        if not match or int(match.group(1)) < 1 or int(match.group(2)) < 1:
            raise ValueError(f"gecersiz oran: '{part.strip()}' (ornek 16:9)")
        a, b = int(match.group(1)), int(match.group(2))
        out.append((f"{a}:{b}", a, b))
    if not out:
        raise ValueError("oran listesi bos")
    return out


def center_crop(width: int, height: int, rw: int, rh: int) -> Crop:
    """Gorselin ortasindan rw:rh oraninda en buyuk kutu ve korunan alan orani."""
    if width * rh >= height * rw:  # gorsel hedeften genis: yanlardan kes
        cw, ch = max(1, round(height * rw / rh)), height
    else:  # gorsel hedeften dar/uzun: ustten-alttan kes
        cw, ch = width, max(1, round(width * rh / rw))
    cw, ch = min(cw, width), min(ch, height)
    left, top = (width - cw) // 2, (height - ch) // 2
    return Crop((left, top, left + cw, top + ch), round(cw * ch / (width * height), 4))


def sharpness(img: Image.Image) -> float:
    """Gri, en uzun kenari <=1024 px gorselde Laplace benzeri filtrenin varyansi (yuksek = keskin)."""
    gray = img.convert("L")
    gray.thumbnail((SHARP_MAX_SIDE, SHARP_MAX_SIDE), Image.Resampling.LANCZOS)
    if gray.width < 3 or gray.height < 3:
        return 0.0
    kernel = ImageFilter.Kernel((3, 3), LAPLACE_KERNEL, scale=LAPLACE_SCALE, offset=LAPLACE_OFFSET)
    lap = gray.filter(kernel).crop((1, 1, gray.width - 1, gray.height - 1))  # filtre kenar pikselini degistirmez: at
    return round(ImageStat.Stat(lap).var[0] * LAPLACE_SCALE ** 2, 2)


def resolve_file(pkg: Path, row: dict[str, Any]) -> tuple[Path | None, str, str]:
    """(yol, kullanilan_alan, hata). web_file varsa onu, yoksa file'i kullanir; yol paket kokunden cikamaz."""
    field = "web_file" if row.get("web_file") else "file"
    rel = row.get(field)
    if not rel:
        return None, field, "bos yol"
    try:
        return common.safe_relpath(pkg, str(rel)), field, ""
    except ValueError as exc:
        return None, field, str(exc)


def resolve_flag_ratios(text: str | None, ratios: list[tuple[str, int, int]]) -> list[str]:
    """Isaret oranlari: verilmediyse varsayilanin olculenlerle kesisimi; verildiyse hepsi olculenlerde olmali (ValueError)."""
    measured = [name for name, _, _ in ratios]
    if text is None:
        return [name for name, _, _ in parse_ratios(DEFAULT_FLAG_RATIOS) if name in measured]
    names = [name for name, _, _ in parse_ratios(text)]
    missing = [name for name in names if name not in measured]
    if missing:
        raise ValueError(f"--flag-ratios olculmeyen oran iceriyor: {', '.join(missing)} (--ratios'a ekleyin)")
    return names


def analyse_photo(pkg: Path, row: dict[str, Any], ratios: list[tuple[str, int, int]], min_short: int, blur: float,
                  flag_ratios: list[str] | None = None) -> dict[str, Any]:
    """Tek foto icin olcum satiri; 'flags' bos degilse isaretlidir. Gorsel kare bilgisi '_path' ile doner (JSON'a girmez).
    flag_ratios None ise olculen her oran guclu kirpma isaretine bakar."""
    path, field, error = resolve_file(pkg, row)
    result: dict[str, Any] = {
        "photo_id": row.get("photo_id"), "entry_id": row.get("entry_id"), "role": row.get("role"),
        "source_field": field, "file": row.get(field), "flags": [],
    }
    result["_path"] = path
    try:
        if path is None:
            raise OSError(error)
        with Image.open(path) as src:
            img = src.convert("RGB")
    except Exception as exc:  # eksik/bozuk/desteklenmeyen dosya
        result.update({"error": f"{type(exc).__name__}: {exc}"[:200], "flags": [R_UNREADABLE]})
        return result
    width, height = img.size
    crops = {name: center_crop(width, height, a, b) for name, a, b in ratios}
    result.update({
        "width": width, "height": height, "short_side": min(width, height), "aspect": round(width / height, 4),
        "crops": {name: {"box": list(c.box), "kept": c.kept} for name, c in crops.items()},
        "min_kept": min(c.kept for c in crops.values()),
        "sharpness": sharpness(img),
    })
    flags: list[str] = result["flags"]
    if result["short_side"] < min_short:
        flags.append(R_LOW_RES)
    strong = [name for name, c in crops.items()
              if c.kept < STRONG_CROP_KEPT and (flag_ratios is None or name in flag_ratios)]
    if strong:
        flags.append(R_STRONG)
        result["strong_crop_ratios"] = strong
    if result["sharpness"] < blur:
        flags.append(R_BLUR)
    if row.get("role") == "Kapak":
        if width <= height:
            flags.append(R_COVER_PORTRAIT)
        if center_crop(width, height, *COVER_RATIO).kept < COVER_MIN_KEPT:
            flags.append(R_COVER_CROP)
    return result


def percentiles(values: list[float], points: tuple[int, ...] = (5, 10, 25, 50, 75, 90)) -> dict[str, float]:
    """Dogrusal aradegerlemeli yuzdelikler (numpy yok)."""
    if not values:
        return {}
    data = sorted(values)
    out = {}
    for p in points:
        pos = (len(data) - 1) * p / 100
        lo = int(pos)
        hi = min(lo + 1, len(data) - 1)
        out[f"p{p}"] = round(data[lo] + (data[hi] - data[lo]) * (pos - lo), 2)
    out["min"], out["max"] = round(data[0], 2), round(data[-1], 2)
    return out


def _caption_text(row: dict[str, Any]) -> str:
    label = truncate_label(str(row.get("photo_id") or "?"), LABEL_MAX)
    return f"{label}  !{','.join(row['flags'])}" if row["flags"] else label


def render_cell(row: dict[str, Any], ratios_wh: dict[str, tuple[int, int]]) -> Image.Image:
    """Bir fotonun 16:9 ve 1:1 merkez kirpmasi yan yana + alt seritte photo_id (ve varsa isaretler)."""
    pair_w = sum(TILE_W[n] for n in SHEET_RATIOS) + PAIR_GAP
    cell = Image.new("RGB", (pair_w, TILE_H + CAPTION_H), CAPTION_BG)
    draw = ImageDraw.Draw(cell)
    font = load_font(13)
    try:
        with Image.open(row["_path"]) as src:
            img = src.convert("RGB")
        x = 0
        for name in SHEET_RATIOS:
            a, b = ratios_wh[name]
            box = center_crop(img.width, img.height, a, b).box
            cell.paste(img.crop(box).resize((TILE_W[name], TILE_H), Image.Resampling.LANCZOS), (x, 0))
            x += TILE_W[name] + PAIR_GAP
    except Exception:  # okunamayan dosya: gri yer tutucu
        draw.rectangle([0, 0, pair_w, TILE_H], fill=(150, 150, 150))
        draw.text((pair_w // 2, TILE_H // 2), "OKUNAMADI", font=load_font(18), fill=(255, 255, 255), anchor="mm")
    draw.text((4, TILE_H + 3), _caption_text(row), font=font, fill=FLAG_COLOR if row["flags"] else OK_COLOR)
    return cell


def build_sheet(rows: list[dict[str, Any]]) -> Image.Image:
    ratios_wh = {"16:9": (16, 9), "1:1": (1, 1)}
    cells = [render_cell(r, ratios_wh) for r in rows]
    cw, ch = cells[0].size
    cols = max(1, min(len(cells), (MAX_SHEET_WIDTH - CELL_GAP) // (cw + CELL_GAP)))
    n_rows = -(-len(cells) // cols)
    sheet = Image.new("RGB", (cols * (cw + CELL_GAP) + CELL_GAP, n_rows * (ch + CELL_GAP) + CELL_GAP), BG)
    for i, cell in enumerate(cells):
        sheet.paste(cell, (CELL_GAP + (i % cols) * (cw + CELL_GAP), CELL_GAP + (i // cols) * (ch + CELL_GAP)))
    return sheet


def make_sheets(rows: list[dict[str, Any]], out_dir: Path) -> list[dict[str, Any]]:
    """Kapaklar once (kendi paftalarinda), sonra diger fotolar; eski kirpma_NN.jpg dosyalari silinir."""
    sheet_dir = out_dir / SHEET_DIR
    sheet_dir.mkdir(parents=True, exist_ok=True)
    for old in sheet_dir.glob("kirpma_*.jpg"):
        old.unlink()
    covers = [r for r in rows if r.get("role") == "Kapak"]
    others = [r for r in rows if r.get("role") != "Kapak"]
    sheets = []
    for group, kind in ((covers, "kapak"), (others, "mekan")):
        for start in range(0, len(group), PER_SHEET):
            chunk = group[start:start + PER_SHEET]
            image = build_sheet(chunk)
            name = f"kirpma_{len(sheets) + 1:02d}.jpg"
            image.save(sheet_dir / name, "JPEG", quality=JPEG_QUALITY)
            sheets.append({"sheet": f"{SHEET_DIR}/{name}", "kind": kind, "width": image.width, "height": image.height,
                           "photo_ids": [r["photo_id"] for r in chunk]})
    return sheets


def summarize(rows: list[dict[str, Any]], threshold: float, sheets: list[dict[str, Any]]) -> dict[str, Any]:
    by_reason = {reason: sum(1 for r in rows if reason in r["flags"]) for reason in REASONS}
    values = [r["sharpness"] for r in rows if "sharpness" in r]
    return {
        "photos": len(rows), "covers": sum(1 for r in rows if r.get("role") == "Kapak"),
        "flagged": sum(1 for r in rows if r["flags"]),
        "by_reason": {k: v for k, v in by_reason.items() if v},
        "blur_threshold": threshold, "sharpness_percentiles": percentiles(values), "sheets": len(sheets),
    }


def read_photo_rows(xlsx: Path) -> list[dict[str, Any]]:
    wb = openpyxl.load_workbook(xlsx, read_only=False, data_only=True)
    if PHOTO_SHEET not in wb.sheetnames:
        raise ValueError(f"'{PHOTO_SHEET}' sayfasi yok")
    return [r for r in common.iter_records(wb[PHOTO_SHEET]) if r.get("photo_id")]


def guard_out(out_dir: Path, pkg: Path, xlsx: Path) -> str | None:
    """--out-dir paket kokunun (ya da Excel'in yanindaki paket kokunun) icindeyse hata metni dondurur."""
    out = out_dir.resolve()
    for root in {pkg.resolve(), xlsx.resolve().parent}:
        if out == root or out.is_relative_to(root):
            if root == pkg.resolve() or any((root / n).is_dir() for n in ("Fotoğraflar", "Teslimler", "Lisans kanıtları")):
                return f"--out-dir paket icinde: {out_dir} (paket salt okunur; ciktiyi disina yazin)"
    return None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Gorsel kalite kaniti: hedef-ekran kirpmasi, netlik, kapak sunumu.")
    p.add_argument("--xlsx", type=Path, required=True)
    p.add_argument("--pkg", type=Path, required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--ratios", default=DEFAULT_RATIOS)
    p.add_argument("--flag-ratios", default=None,
                   help=f"guclu kirpma isaretine bakan oranlar (varsayilan {DEFAULT_FLAG_RATIOS}, olculenlerle kesisim)")
    p.add_argument("--min-short", type=int, default=DEFAULT_MIN_SHORT)
    p.add_argument("--blur-threshold", type=float, default=BLUR_THRESHOLD)
    return p


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    args = build_parser().parse_args(argv)
    if not args.xlsx.is_file():
        print(f"xlsx yok: {args.xlsx}", file=sys.stderr)
        return EXIT_USAGE
    if not args.pkg.is_dir():
        print(f"paket klasoru yok: {args.pkg}", file=sys.stderr)
        return EXIT_USAGE
    if args.min_short < 1 or args.blur_threshold < 0:
        print("gecersiz --min-short/--blur-threshold", file=sys.stderr)
        return EXIT_USAGE
    problem = guard_out(args.out_dir, args.pkg, args.xlsx)
    if problem:
        print(problem, file=sys.stderr)
        return EXIT_USAGE
    try:
        ratios = parse_ratios(args.ratios)
        flag_ratios = resolve_flag_ratios(args.flag_ratios, ratios)
        photo_rows = read_photo_rows(args.xlsx)
    except (ValueError, OSError) as exc:
        print(f"girdi okunamadi: {exc}", file=sys.stderr)
        return EXIT_USAGE
    rows = [analyse_photo(args.pkg, r, ratios, args.min_short, args.blur_threshold, flag_ratios) for r in photo_rows]
    args.out_dir.mkdir(parents=True, exist_ok=True)
    sheets = make_sheets(rows, args.out_dir)
    for row in rows:
        row.pop("_path", None)
    summary = summarize(rows, args.blur_threshold, sheets)
    report = {
        "tool": "gorsel_kalite", "version": "v7",
        "params": {"ratios": [n for n, _, _ in ratios], "flag_ratios": flag_ratios,
                   "min_short": args.min_short, "blur_threshold": args.blur_threshold,
                   "strong_crop_kept": STRONG_CROP_KEPT, "cover_min_kept_16x9": COVER_MIN_KEPT},
        "summary": summary, "photos": rows,
        "flagged": [{"photo_id": r["photo_id"], "role": r.get("role"), "reasons": r["flags"]} for r in rows if r["flags"]],
        "sheets": sheets,
    }
    write_json(args.out_dir / REPORT_NAME, report)
    emit({"tool": "gorsel_kalite", **summary, "out_dir": str(args.out_dir)})
    return EXIT_FINDINGS if summary["flagged"] else EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
