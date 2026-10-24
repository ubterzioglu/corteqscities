"""Kullanilan kaynaklarin HTML kopyalarini pakete tasir, Kaynaklar satirlarina snapshot_file/sha256 yazar (A6; pilot: kaynak_paketle.py).

Kullanim: package_sources.py <is_klasoru> <paket_koku> [--rows <is>/data/Kaynaklar.jsonl] [--rows-out <--rows>]
                             [--snap-dir <is>/snap] [--prune] [--out rapor.json]
Okur: --rows (merge_package ciktisi: yalniz kullanilan kaynaklar; yalniz iddia defterinin dayandiklari dahil),
      <is>/kaynak_dizini.jsonl (html_file, html_sha256).
      html_file duz ad ise --snap-dir altinda, 'alt_klasor\\ad' ya da 'alt_klasor/ad' ise <is> altinda aranir
      (add_sources bicimi); <is> disina cikan yol okunmaz.
Yazar: <paket>/Lisans kanıtları/<sha256>.<uzanti> (düz klasör) ve --rows-out (snapshot_file, snapshot_sha256 dolu; kopyasi
       olmayan satirda bos + verified=Hayır).
Klasorde kalan kullanilmayan kopyalar (K05) yalniz TAM ve YERINDE kosuda silinir: --rows = <is>/data/Kaynaklar.jsonl
(varsayilan) ve --rows-out = --rows; ya da acik --prune ile (baska --data-out kullaniliyorsa). Kismi --rows ya da baska
bir --rows-out ile kosuda hicbir kopya silinmez, 'unused' olarak raporlanir (asil satirlarin gosterdigi dosya kalir).
Sozlesme (DIGEST §2 Kaynaklar): snapshot_file doluysa dosya pakette olmali ve hash eslesmeli. Kopyanin icerigi
kaynak_dizini'ndeki html_sha256 ile tutmazsa pakete alinmaz (bulgu); paketteki bozuk kopya yeniden kopyalanir.
merge_package her calismada Kaynaklar.jsonl'i yeniden yazar; bu script ondan SONRA calisir. Paket koku olusturulmaz.
stdout tek satir JSON; cikis 0 hepsi kopyalandi / 1 kopyasi eksik ya da bozuk kaynak var / 2 kullanim (okunamayan
girdi, UTF-8 olmayan JSONL, yazilamayan cikti dahil).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, safe_relpath, setup_utf8, sha256_file, write_json

SUBDIR = "Lisans kanıtları"  # düz: Drive'a yüklenince alt klasör korunmuyor (Bakersfield: 798 yol bozuk çıktı)
HASH_NAME = re.compile(r"^[0-9a-f]{64}\.[A-Za-z0-9]+$")  # yalnız kendi yazdığımız kopyalar; foto kanıtlarına dokunulmaz
INDEX_NAME = "kaynak_dizini.jsonl"
DEFAULT_ROWS = Path("data", "Kaynaklar.jsonl")  # <is> altinda; merge_package varsayilan ciktisi
NO_SNAPSHOT = {"snapshot_file": "", "snapshot_sha256": "", "verified": "Hayır"}


class UsageError(Exception):
    """Eksik/bozuk girdi ya da gecersiz arguman (cikis 2)."""


@dataclass(frozen=True)
class Layout:
    work: Path
    package: Path
    rows: Path
    rows_out: Path
    snap_dir: Path

    @property
    def target(self) -> Path:
        return self.package.joinpath(*SUBDIR.split("/"))

    @property
    def full_in_place(self) -> bool:
        """Asil satir dosyasi (<is>/data/Kaynaklar.jsonl) yerinde guncelleniyor: kullanilmayan kopya silinebilir."""
        return same_path(self.rows, self.work / DEFAULT_ROWS) and same_path(self.rows_out, self.rows)


def same_path(a: Path, b: Path) -> bool:
    return os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise UsageError(f"{path}:{number}: gecersiz JSON ({error.msg})") from error
                if not isinstance(row, dict):
                    raise UsageError(f"{path}:{number}: nesne bekleniyor")
                rows.append(row)
    except UnicodeDecodeError as error:
        raise UsageError(f"{path}: UTF-8 degil ({error.reason})") from error
    return rows


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def resolve_html(layout: Layout, html_file: Any) -> Path | None:
    """Kopya yolu: duz ad --snap-dir altinda, alt klasorlu ad <is> altinda; guvensiz/bos yol None."""
    if not isinstance(html_file, str) or not html_file.strip():
        return None
    relative = html_file.replace("\\", "/")
    try:
        return safe_relpath(layout.work, relative) if "/" in relative else safe_relpath(layout.snap_dir, relative)
    except ValueError:
        return None


def package_one(layout: Layout, row: dict[str, Any], source: dict[str, Any]) -> tuple[dict[str, Any], str]:
    """(cikis satiri, sonuc: copied | kept | missing | mismatch)."""
    path = resolve_html(layout, source.get("html_file"))
    if path is None or not path.is_file():
        return {**row, **NO_SNAPSHOT}, "missing"
    digest = sha256_file(path)
    if source.get("html_sha256") and digest != source["html_sha256"]:
        return {**row, **NO_SNAPSHOT}, "mismatch"
    name = f"{digest}{path.suffix or '.html'}"
    dest = layout.target / name
    outcome = "kept"
    if not dest.is_file() or sha256_file(dest) != digest:
        shutil.copyfile(path, dest)
        outcome = "copied"
        if sha256_file(dest) != digest:
            return {**row, **NO_SNAPSHOT}, "mismatch"
    return {**row, "snapshot_file": f"{SUBDIR}/{name}", "snapshot_sha256": digest}, outcome


def unused_files(target: Path, keep: set[str]) -> list[str]:
    """Klasorde kalan, bu satirlarin hicbirinin gostermedigi dosyalar (K05 adayi)."""
    return sorted(p.name for p in target.iterdir()
                  if p.is_file() and HASH_NAME.match(p.name) and p.name not in keep)


def make_layout(args: argparse.Namespace) -> Layout:
    work, package = Path(os.path.abspath(args.work)), Path(os.path.abspath(args.package))
    if not work.is_dir():
        raise UsageError(f"is klasoru yok: {work}")
    if not package.is_dir():
        raise UsageError(f"paket koku yok (olusturulmaz): {package}")
    rows = Path(os.path.abspath(args.rows or work / DEFAULT_ROWS))
    return Layout(work, package, rows, Path(os.path.abspath(args.rows_out or rows)),
                  Path(os.path.abspath(args.snap_dir or work / "snap")))


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Kullanilan kaynak kopyalarini pakete tasir, snapshot alanlarini doldurur")
    p.add_argument("work", help="is klasoru (_is): kaynak_dizini.jsonl ve kopya klasorleri")
    p.add_argument("package", help="paket koku (Lisans kanıtları/ bunun altinda)")
    p.add_argument("--rows", type=Path, help="Kaynaklar satirlari (varsayilan <is>/data/Kaynaklar.jsonl)")
    p.add_argument("--rows-out", type=Path, help="guncel satirlarin yazilacagi yer (varsayilan --rows, yerinde)")
    p.add_argument("--snap-dir", type=Path, help="duz adli kopyalarin klasoru (varsayilan <is>/snap)")
    p.add_argument("--prune", action="store_true",
                   help="bu satirlarin gostermedigi kopyalari sil (tam ve yerinde kosuda zaten silinir)")
    p.add_argument("--out", type=Path, help="ayrinti JSON (eksik, bozuk, silinen ve silinmeyen kullanilmayan dosyalar)")
    return p


def run(args: argparse.Namespace) -> int:
    layout = make_layout(args)
    index = {r.get("source_id"): r for r in read_jsonl(layout.work / INDEX_NAME)}
    rows = read_jsonl(layout.rows)
    layout.target.mkdir(parents=True, exist_ok=True)
    results = [package_one(layout, row, index.get(row.get("source_id")) or {}) for row in rows]
    out_rows = [row for row, _ in results]
    write_jsonl(layout.rows_out, out_rows)
    unused = unused_files(layout.target, {Path(r["snapshot_file"]).name for r in out_rows if r.get("snapshot_file")})
    prune = args.prune or layout.full_in_place
    for name in unused if prune else []:
        (layout.target / name).unlink()
    removed, kept = (unused, []) if prune else ([], unused)
    missing = [row.get("source_id") for row, (_, kind) in zip(rows, results) if kind == "missing"]
    mismatch = [row.get("source_id") for row, (_, kind) in zip(rows, results) if kind == "mismatch"]
    copied = sum(1 for _, kind in results if kind == "copied")
    if args.out:
        write_json(args.out, {"missing": missing, "hash_mismatch": mismatch, "removed": removed, "unused": kept,
                              "pruned": prune, "copied": copied})
    findings = bool(missing or mismatch)
    emit({"status": "findings" if findings else "ok", "sources": len(rows),
          "with_snapshot": len(rows) - len(missing) - len(mismatch), "copied": copied, "removed_unused": len(removed),
          "unused_kept": len(kept), "pruned": prune, "missing": missing[:10], "hash_mismatch": mismatch[:10],
          "rows_out": str(layout.rows_out), "target_dir": str(layout.target)})
    return EXIT_FINDINGS if findings else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        return run(args)
    except (UsageError, OSError, ValueError) as error:  # yakalanmazsa cikis 1 olur ve 'bulgu' ile karisir
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
