"""Uretimde kalan inceleme kanitlarini teslim klasorune yazar (dis denetim B1-B3/B5, C1-C5, D4). Excel'i yalniz okur.

Sevilla dis denetimi (25.10.2026, %44,7): rota saat plani, mekan dogrulamasi, foto incelemesi ve kirpma olcumu uretim
klasorunde kaldi; denetci paydayi kuramadi, ilgili olcutler 0 aldi. Bu arac son Excel'deki kayitlar icin:
- rota-plani-v7.jsonl      <- WORK\\_is\\rota_plan.jsonl (yer-yazari gun/saat plani: route_id, gun, durak, varis_saati,
                              acik_mi, dayanak) + WORK\\_is\\rota_mesafe.jsonl (bacaklar: kus ucusu, OSM yaya m/dk);
                              Excel'deki her rota en az bir plan satiri ve olculmus bacaklar ister.
- mekan-dogrulama-v7.jsonl <- WORK\\_is\\denetim\\*_mekan-dogrulama.jsonl (bagimsiz mekan/mahalle denetcisi: entry_id,
                              sonuc gecti|kaldi, ...); tur sirasi iddia_defteri'ndeki gibi, son tur gecerli.
- foto-inceleme-v7.jsonl   <- foto inceleme (review_*, verify_*, covers), ek tur kararlari (foto*\\karar.jsonl, yalniz
                              'degistir' yeni kareyi tasir) ve son foto denetimi (foto\\inceleme\\denetim_*.jsonl:
                              photo_id, gorsel_sonuc, ek_hak, ...). Oncelik: son denetim > ikinci goz > ek tur > inceleme.
                              ek_hak (kare ici cagdas eser/gosteri/belirgin kisi: yok | var | belirsiz) satirin kendi
                              alanindan; yazilmamissa 'belirsiz' (D4 kaniti degil, uydurulmaz).
- gorsel-kalite-v7.json    <- --quality ile verilen gorsel_kalite raporu (kopya).
Cikis: 0 her kayit kanitli; 1 kanitsiz kayit ya da eksik girdi var (ozet 'eksik'); 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import openpyxl

import common
from iddia_defteri import round_rank

ROUTE_OUT, PLACE_OUT, PHOTO_OUT, QUALITY_OUT = ("rota-plani-v7.jsonl", "mekan-dogrulama-v7.jsonl",
                                                "foto-inceleme-v7.jsonl", "gorsel-kalite-v7.json")
PLACE_SUFFIX = "_mekan-dogrulama.jsonl"
LEGS_NAME = "rota_mesafe.jsonl"  # rota_mesafe ciktisi: bacak basina kus ucusu + OSM yaya mesafe/sure
UNKNOWN_RIGHTS = "belirsiz"


class TeslimError(Exception):
    pass


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), start=1):
        if line.strip():
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TeslimError(f"{path.name}:{number} JSON degil ({exc})") from exc
            if isinstance(row, dict):
                rows.append(row)
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def load_excel(xlsx: Path) -> dict[str, list[dict[str, Any]]]:
    try:
        wb = openpyxl.load_workbook(xlsx, read_only=False)
    except Exception as exc:  # openpyxl bozuk dosyada farkli hatalar atar
        raise TeslimError(f"xlsx okunamadi: {xlsx} ({type(exc).__name__})") from exc
    try:
        return {s: list(common.iter_records(wb[s])) for s in ("Mekânlar", "Mahalleler", "Rotalar", "Fotoğraflar")
                if s in wb.sheetnames}
    finally:
        wb.close()


def route_rows(work: Path, routes: list[str]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """(durak saat satirlari + bacak satirlari, plansiz rotalar, olculmemis bacagi olan rotalar)."""
    plan_path, leg_path = work / "rota_plan.jsonl", work / LEGS_NAME
    plan = [r for r in (read_jsonl(plan_path) if plan_path.is_file() else []) if r.get("route_id") in set(routes)]
    legs = [r for r in (read_jsonl(leg_path) if leg_path.is_file() else []) if r.get("route_id") in set(routes)]
    covered = {r["route_id"] for r in plan if r.get("acik_mi")}
    measured = {r["route_id"] for r in legs} - {r["route_id"] for r in legs if "yuruyus_m" not in r}
    return plan + legs, [r for r in routes if r not in covered], [r for r in routes if r not in measured]


def place_rows(work: Path, ids: list[str]) -> tuple[list[dict[str, Any]], list[str]]:
    folder = work / "denetim"
    files = sorted(folder.glob(f"*{PLACE_SUFFIX}"), key=lambda p: (round_rank(p.name[: -len(PLACE_SUFFIX)]), p.name)) \
        if folder.is_dir() else []
    latest: dict[str, dict[str, Any]] = {}
    for path in files:
        for row in read_jsonl(path):
            if row.get("entry_id") in set(ids):
                latest[row["entry_id"]] = {**row, "tur": path.name[: -len(PLACE_SUFFIX)]}
    return [latest[i] for i in ids if i in latest], [i for i in ids if i not in latest]


def _review_sources(work: Path) -> tuple[dict[str, dict], dict[str, dict], dict[str, dict], dict[str, dict]]:
    """(inceleme key->satir, ikinci goz key->satir, ek tur key->satir, son denetim photo_id->satir); sonraki dosya ezer."""
    ins = work / "foto" / "inceleme"
    review = {r["key"]: r for p in sorted(ins.glob("review_*.jsonl")) for r in read_jsonl(p) if r.get("key")}
    review.update({r["key"]: {**r, "result": "keep", "reason": "kapak secimi"}
                   for p in sorted(ins.glob("covers*.jsonl")) for r in read_jsonl(p) if r.get("key")})
    verify = {r["key"]: r for p in sorted(ins.glob("verify_*.jsonl")) for r in read_jsonl(p) if r.get("key")}
    extra = {f"{r['entry_id']}|{r['yeni_commons_file']}": r for p in sorted(work.glob("foto*/karar.jsonl"))
             for r in read_jsonl(p) if r.get("karar") == "degistir" and r.get("entry_id") and r.get("yeni_commons_file")}
    final = {r["photo_id"]: r for p in sorted(ins.glob("denetim_*.jsonl")) for r in read_jsonl(p) if r.get("photo_id")}
    return review, verify, extra, final


def photo_rows(work: Path, photos: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    clean_path = work / "foto" / "secim_temiz.jsonl"
    key_of = {r["photo_id"]: r.get("key") for r in read_jsonl(clean_path) if r.get("photo_id")} if clean_path.is_file() else {}
    review, verify, extra, final = _review_sources(work)
    rows, missing = [], []
    for photo in photos:
        pid, key = str(photo["photo_id"]), key_of.get(str(photo["photo_id"]))
        base = {"photo_id": pid, "entry_id": photo.get("entry_id"), "role": photo.get("role"), "key": key}
        if pid in final:
            f = final[pid]
            rows.append({**base, "gorsel_sonuc": f.get("gorsel_sonuc", ""), "ek_hak": f.get("ek_hak") or UNKNOWN_RIGHTS,
                         "dayanak": "son foto denetimi", "not": f.get("not", "")})
        elif key in verify:
            v = verify[key]
            rows.append({**base, "gorsel_sonuc": "keep" if v.get("ok") else "reject",
                         "ek_hak": v.get("ek_hak") or review.get(key, {}).get("ek_hak") or UNKNOWN_RIGHTS,
                         "dayanak": "ikinci göz", "not": v.get("why", "")})
        elif key in extra:
            rows.append({**base, "gorsel_sonuc": "keep", "ek_hak": extra[key].get("ek_hak") or UNKNOWN_RIGHTS,
                         "dayanak": "ek tur kararı", "not": extra[key].get("gorulen", "")})
        elif key in review:
            r = review[key]
            rows.append({**base, "gorsel_sonuc": r.get("result", ""), "ek_hak": r.get("ek_hak") or UNKNOWN_RIGHTS,
                         "dayanak": "inceleme", "not": r.get("reason", "")})
        else:
            missing.append(pid)
    return rows, missing


def build(xlsx: Path, work: Path, teslim: Path, quality: Path | None) -> dict[str, Any]:
    rec = load_excel(xlsx)
    ids = {s: [str(r.get(k)) for r in rec.get(s, []) if r.get(k)]
           for s, k in (("Mekânlar", "entry_id"), ("Mahalleler", "entry_id"), ("Rotalar", "route_id"))}
    photos = [r for r in rec.get("Fotoğraflar", []) if r.get("photo_id")]
    routes, no_plan, no_legs = route_rows(work, ids["Rotalar"])
    places, unchecked = place_rows(work, ids["Mekânlar"] + ids["Mahalleler"])
    reviews, unreviewed = photo_rows(work, photos)
    teslim.mkdir(parents=True, exist_ok=True)
    write_jsonl(teslim / ROUTE_OUT, routes)
    write_jsonl(teslim / PLACE_OUT, places)
    write_jsonl(teslim / PHOTO_OUT, reviews)
    copied = bool(quality and quality.is_file())
    if copied:
        shutil.copyfile(quality, teslim / QUALITY_OUT)
    missing = {"rota_plansiz": no_plan, "rota_bacaksiz": no_legs, "mekan_denetimsiz": unchecked, "foto_incelemesiz": unreviewed,
               "gorsel_kalite": [] if copied else [str(quality or "--quality verilmedi")]}
    return {"tool": "kanit_teslim", "rota_satiri": len(routes), "mekan_dogrulama": len(places),
            "mekan_gecti": sum(1 for r in places if str(r.get("sonuc")) in {"geçti", "gecti"}),
            "foto_inceleme": len(reviews), "foto_ek_hak_belirsiz": sum(1 for r in reviews if r["ek_hak"] == UNKNOWN_RIGHTS),
            "eksik_sayim": {k: len(v) for k, v in missing.items()}, "eksik": {k: v[:20] for k, v in missing.items() if v}}


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    parser = argparse.ArgumentParser(description="Inceleme kanitlarini Teslimler'e yazar (rota plani, mekan dogrulama, "
                                                 "foto inceleme, gorsel kalite)")
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True, help="WORK\\_is")
    parser.add_argument("--pkg", type=Path, required=True)
    parser.add_argument("--quality", type=Path, help="gorsel_kalite raporu (paket disinda uretilmis gorsel-kalite-v7.json)")
    args = parser.parse_args(argv)
    try:
        for path, kind in ((args.xlsx, "xlsx"), (args.work, "is klasoru"), (args.pkg, "paket")):
            if not path.exists():
                raise TeslimError(f"{kind} yok: {path}")
        summary = build(args.xlsx, args.work, args.pkg / "Teslimler", args.quality)
    except TeslimError as exc:
        common.emit({"tool": "kanit_teslim", "error": str(exc)})
        return common.EXIT_USAGE
    common.emit(summary)
    return common.EXIT_FINDINGS if summary["eksik"] else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
