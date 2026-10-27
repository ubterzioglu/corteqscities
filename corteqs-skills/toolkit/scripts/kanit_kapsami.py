"""Teslimdeki kanitlarin 25 olcutu ne kadar kapattigi + dis denetim modeliyle puan alt siniri.

Sevilla dis denetimi (25.10.2026, %44,7): olcut basina agirlik x min(1, dogrulanan/payda); paydasi kanitla kapanmayan
olcut kredi almaz. Kaybin ~54 puani "kapatilmadi"dan geldi; cunku kanit pakette yoktu. Bu arac teslim klasorundeki
kanit dosyalarini okur, her olcut icin payda / kanitli / durum (tam | kismi | yok | onizleme) ve alt siniri yazar.
D5 (gorunur atif) ve E4 (web islevleri) yalniz Drive yuklemesinden sonra city-preview ile kapanir: 'onizleme'.

Kanit dosyalari (PKG\\Teslimler): iddia-defteri-ozet-v7.json (iddia_defteri), rota-plani-v7.jsonl, mekan-dogrulama-v7.jsonl,
foto-inceleme-v7.jsonl, gorsel-kalite-v7.json (gorsel_kalite), paket-kontrol-v7.json ve photo-provenance-v7.json (emit),
TESLIM_OZETI.txt, ACIK_KONULAR.txt. Paydalar Excel'den; hedefli olcutlerde payda = max(sayi, Berlin hedefi).
Cikis: 0 eksik yok (onizleme haric); 1 eksik var; 2 girdi hatasi. Excel'i yalniz okur, pakete yazmaz.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import openpyxl

import common

TARGETS = dict(common.BERLIN_TARGET)
WEIGHTS = {**{f"A{i}": 7 for i in range(1, 6)}, **{f"B{i}": 4 for i in range(1, 6)}, **{f"C{i}": 4 for i in range(1, 6)},
           **{f"D{i}": 3 for i in range(1, 6)}, **{f"E{i}": 2 for i in range(1, 6)}}
PREVIEW = {"D5", "E4"}
OK_CARD = {"temiz", "düzeltildi"}
KEEP = {"keep", "tut"}
RIGHTS_OPEN = {"açık", "acik", "belirsiz"}


class KapsamError(Exception):
    pass


def _records(xlsx: Path) -> dict[str, list[dict[str, Any]]]:
    try:
        wb = openpyxl.load_workbook(xlsx, read_only=False)
    except Exception as exc:  # openpyxl bozuk dosyada farkli hatalar atar
        raise KapsamError(f"xlsx okunamadi: {xlsx} ({type(exc).__name__})") from exc
    try:
        return {s: list(common.iter_records(wb[s])) for s in ("Yanıtlar", "Mekânlar", "Mahalleler", "Rotalar", "Sözlük",
                                                              "Fotoğraflar") if s in wb.sheetnames}
    finally:
        wb.close()


def _load(path: Path) -> Any:
    if not path.is_file():
        return None
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _ids(rows: list[dict[str, Any]], key: str) -> list[str]:
    return [str(r[key]) for r in rows if r.get(key)]


def _validator_errors(check: Any) -> int | None:
    """Resmi dogrulayicinin emit ciktisi (paket-kontrol-v7.json): structure.errors + media.errors listeleri;
    technically_complete False ise hata var sayilir. Okunamayan bicim None (kanit yok)."""
    if not isinstance(check, dict):
        return None
    parts = [(check.get(key) or {}).get("errors") for key in ("structure", "media")]
    if not all(isinstance(part, list) for part in parts):
        return None
    return sum(len(part) for part in parts) + (1 if check.get("technically_complete") is False else 0)


def _item(cid: str, payda: int, kanitli: int, dosya: str, available: bool, note: str = "") -> dict[str, Any]:
    if cid in PREVIEW:
        durum = "onizleme"
    elif not available or kanitli <= 0:
        durum = "yok"
    else:
        durum = "tam" if kanitli >= payda else "kismi"
    kanitli = max(0, min(kanitli, payda))
    puan = 0.0 if durum in {"yok", "onizleme"} else WEIGHTS[cid] * kanitli / payda if payda else 0.0
    return {"id": cid, "agirlik": WEIGHTS[cid], "payda": payda, "kanitli": kanitli, "durum": durum, "puan": round(puan, 2),
            "kanit": dosya, "not": note}


def evaluate(xlsx: Path, teslim: Path) -> list[dict[str, Any]]:
    rec = _records(xlsx)
    ans, places, dists = _ids(rec.get("Yanıtlar", []), "entry_id"), _ids(rec.get("Mekânlar", []), "entry_id"), _ids(rec.get("Mahalleler", []), "entry_id")
    routes, terms = _ids(rec.get("Rotalar", []), "route_id"), _ids(rec.get("Sözlük", []), "term_id")
    photos = rec.get("Fotoğraflar", [])
    photo_ids = _ids(photos, "photo_id")
    covers = [str(p["photo_id"]) for p in photos if p.get("role") == "Kapak" and p.get("photo_id")]
    led = _load(teslim / "iddia-defteri-ozet-v7.json") or {}
    status = led.get("son_durum", {})
    unaudited = {i for ids in (led.get("denetlenmemis_kayit") or {}).values() for i in ids}
    noclaim = {i for ids in (led.get("iddiasiz_kayit") or {}).values() for i in ids}
    flagged_check = set(led.get("dogrulama_sorunlu") or [])
    good = {i for i, s in status.items() if s in OK_CARD} - unaudited - flagged_check
    route_plan = _load(teslim / "rota-plani-v7.jsonl") or []
    planned = {r["route_id"] for r in route_plan if r.get("route_id") and r.get("acik_mi")}
    place_check = {r["entry_id"] for r in (_load(teslim / "mekan-dogrulama-v7.jsonl") or []) if r.get("sonuc") in {"geçti", "gecti"}}
    review = {r["photo_id"]: r for r in (_load(teslim / "foto-inceleme-v7.jsonl") or []) if r.get("photo_id")}
    kept = {p for p, r in review.items() if str(r.get("gorsel_sonuc")) in KEEP}
    quality = _load(teslim / "gorsel-kalite-v7.json") or {}
    clean = {r["photo_id"] for r in quality.get("photos", []) if r.get("photo_id") and not r.get("flags")}
    prov = _load(teslim / "photo-provenance-v7.json") or []  # resmi emit: foto satirlarinin listesi
    prov_rows = prov if isinstance(prov, list) else prov.get("photos", [])
    proven = {str(r.get("photo_id")) for r in prov_rows if isinstance(r, dict)}
    errors = _validator_errors(_load(teslim / "paket-kontrol-v7.json"))
    with_photo = {str(p.get("entry_id")) for p in photos if str(p.get("photo_id")) in kept}
    t = TARGETS
    have = {k: (teslim / k).is_file() for k in ("iddia-defteri-ozet-v7.json", "rota-plani-v7.jsonl", "mekan-dogrulama-v7.jsonl",
                                                 "foto-inceleme-v7.jsonl", "gorsel-kalite-v7.json", "paket-kontrol-v7.json",
                                                 "photo-provenance-v7.json")}
    ledger = have["iddia-defteri-ozet-v7.json"]
    card_ok = [i for i in ans if i in good]
    claim_ok = [i for i in card_ok if i not in noclaim]
    pa = max(len(ans), t["answers"])
    items = [
        _item("A1", pa, len(card_ok), "iddia-defteri-ozet-v7.json", ledger, "kart başına son bağımsız denetim kararı"),
        _item("A2", pa, len(card_ok), "iddia-defteri-ozet-v7.json", ledger),
        _item("A3", pa, len(claim_ok) - len(led.get("kopyasiz_iddia") or []), "iddia-defteri-v7.csv", ledger, "iddia-kaynak-alıntı"),
        _item("A4", pa, len(claim_ok) - len(led.get("duzelt_kayitsiz") or []), "bagimsiz-denetim-v7.csv", ledger),
        _item("A5", pa, len(card_ok), "iddia-defteri-ozet-v7.json", ledger),
        _item("B1", max(len(places), t["places"]), len([p for p in places if p in place_check]), "mekan-dogrulama-v7.jsonl", have["mekan-dogrulama-v7.jsonl"]),
        _item("B2", max(len(dists), t["districts"]), len([d for d in dists if d in place_check]), "mekan-dogrulama-v7.jsonl", have["mekan-dogrulama-v7.jsonl"]),
        _item("B3", max(len(routes), t["routes"]), len([r for r in routes if r in planned]), "rota-plani-v7.jsonl", have["rota-plani-v7.jsonl"]),
        _item("B4", max(len(terms), t["glossary"]), len([s for s in terms if s in good and s not in noclaim]), "iddia-defteri-ozet-v7.json", ledger),
        _item("B5", len(places) + len(dists), len([e for e in places + dists if e in place_check]), "mekan-dogrulama-v7.jsonl", have["mekan-dogrulama-v7.jsonl"]),
        _item("C1", max(t["photos"], 1), len([p for p in photos if p.get("role") != "Kapak" and str(p.get("photo_id")) in kept]), "foto-inceleme-v7.jsonl", have["foto-inceleme-v7.jsonl"]),
        _item("C2", len(photo_ids), len([p for p in photo_ids if p in kept]), "foto-inceleme-v7.jsonl", have["foto-inceleme-v7.jsonl"]),
        _item("C3", len(places) + len(dists), len([e for e in places + dists if e in with_photo]), "foto-inceleme-v7.jsonl", have["foto-inceleme-v7.jsonl"]),
        _item("C4", len(photo_ids), len([p for p in photo_ids if p in clean]), "gorsel-kalite-v7.json", have["gorsel-kalite-v7.json"], "kırpma + netlik; kesin sonuç önizlemede"),
        _item("C5", max(len(covers), t["covers"]), len([c for c in covers if c in clean and c in kept]), "gorsel-kalite-v7.json", have["gorsel-kalite-v7.json"]),
        _item("D1", len(photo_ids), len([p for p in photo_ids if p in proven]), "photo-provenance-v7.json", have["photo-provenance-v7.json"]),
        _item("D2", len(photo_ids), len([p for p in photo_ids if p in proven]), "photo-provenance-v7.json", have["photo-provenance-v7.json"]),
        _item("D3", len(photo_ids), len([p for p in photo_ids if p in proven]), "photo-provenance-v7.json", have["photo-provenance-v7.json"]),
        _item("D4", len(photo_ids), len([p for p in photo_ids if p in review and str(review[p].get("ek_hak", "")).lower() not in RIGHTS_OPEN]), "foto-inceleme-v7.jsonl", have["foto-inceleme-v7.jsonl"]),
        _item("D5", len(photo_ids), 0, "city-preview", False, "görünür atıf yalnız Drive yüklemesinden sonra"),
    ]
    tech_ok = 1 if errors == 0 else 0
    summaries = int((teslim / "TESLIM_OZETI.txt").is_file() and (teslim / "ACIK_KONULAR.txt").is_file())
    items += [_item("E1", 1, tech_ok, "paket-kontrol-v7.json", have["paket-kontrol-v7.json"]),
              _item("E2", 1, tech_ok, "paket-kontrol-v7.json", have["paket-kontrol-v7.json"]),
              _item("E3", 1, tech_ok, "paket-kontrol-v7.json", have["paket-kontrol-v7.json"]),
              _item("E4", 12, 0, "city-preview", False, "12 web senaryosu yalnız Drive yüklemesinden sonra"),
              _item("E5", 1, summaries, "TESLIM_OZETI.txt + ACIK_KONULAR.txt", bool(summaries))]
    return items


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    parser = argparse.ArgumentParser(description="Teslim kanıtlarının 25 ölçüt kapsamı ve dış denetim alt sınırı")
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--pkg", type=Path, required=True, dest="package_root", help="paket koku (yalniz okunur)")
    parser.add_argument("--out", type=Path, required=True, help="paket dışında")
    args = parser.parse_args(argv)
    try:
        if not args.xlsx.is_file():
            raise KapsamError(f"xlsx yok: {args.xlsx}")
        pkg = args.package_root.resolve()
        if pkg in args.out.resolve().parents:
            raise KapsamError("çıktı paketin içine yazılamaz")
        items = evaluate(args.xlsx, pkg / "Teslimler")
    except KapsamError as exc:
        common.emit({"tool": "kanit_kapsami", "error": str(exc)})
        return common.EXIT_USAGE
    bound = round(sum(i["puan"] for i in items), 2)
    preview = sum(i["agirlik"] for i in items if i["durum"] == "onizleme")
    missing = [i["id"] for i in items if i["durum"] in {"yok", "kismi"}]
    report = {"tool": "kanit_kapsami", "workbook": args.xlsx.name, "alt_sinir": bound, "onizleme_ile_azami": round(bound + preview, 2),
              "olcutler": items, "eksik": missing,
              "not": "Dış denetim modeli: ağırlık × min(1, kanıtlı/payda); kanıtı teslimde olmayan ölçüt 0. Kanıt kapsamıdır, "
                     "içerik doğruluğunun garantisi değildir."}
    common.write_json(args.out, report)
    common.emit({"tool": "kanit_kapsami", "alt_sinir": bound, "onizleme_ile_azami": report["onizleme_ile_azami"],
                 "eksik": missing, "out": str(args.out)})
    return common.EXIT_FINDINGS if missing else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
