r"""Acik-mi denetimi (city-audit L1/L2, K39; IYILESTIRME_LISTESI B15): orneklem, acik kaniti, sayim.

Kapi acik_mi.py'dir (uretimde de denetimde de); bu arac denetimin dosyalarini kurar ve kapilarin ciktisini sayar. Yazma
yalniz OUT altina; teslim Excel'i ve uretimin acik-mi klasoru (ACIKMI) yalniz okunur. city-audit SKILL.md'deki sira:
uretim beyani kapisi -> orneklem -> (ajanlar) -> denetim kapisi -> kanit -> ikinci kapi -> fetch_snapshot -> sayim.

Kullanim (OUT = denetim klasoru):
  acik_mi_denetim.py orneklem <OUT> --xlsx <teslim Excel'i> [--acik-mi <ACIKMI>] [--tam]
      Girdi: OUT\_dump\Mekânlar.jsonl (xlsx_dump). --acik-mi bos degilse ve OUT\acik-mi-uretim.json (uretim beyani
      kapisinin raporu: ayni klasor, ayni mekan listesi) varsa ACIKMI'nin satirlari da okunur; rapor yoksa (kapi
      okuyamadi ya da calismadi) okunmaz.
      n = en az MIN_SAMPLE ve mekan sayisinin onda biri (yukari; daha az mekanda hepsi; --tam: hepsi). Oncelikliler
      hepsi (PRIORITIES): a uretim kapisinin bulgusu; b uretimde belirsiz (tarama 'belirsiz' ve dogrulama satiri yok,
      ya da 'onay' + 'dokunma'); c kart metninde (acik_mi.TEXT_FIELDS) '... itibarıyla' tarihli not, yili ne olursa
      olsun; d cekismeli (tarama 'kapalı' ya da 'taşındı', dogrulama 'ret' + 'dokunma'). Sonra kalanlardan en az
      ceil(n/2) mekan (oncelikliler n'yi doldursa da), toplam en az n; sira sha256((excel_sha256 + entry_id)
      .encode('utf-8')) kucukten buyuge, excel_sha256 teslim Excel'inin SHA-256'si (kucuk harf onaltilik).
      Yazar: OUT\acik-mi-orneklem.jsonl (Mekânlar satiri aynen + neden: 'a+c' gibi harfler, 'rastgele', --tam'da
      'tam'; once oncelikliler Excel sirasiyla). OUT\_acikmi bastan kurulur: parti_NN.jsonl (en cok BATCH mekan;
      tarama satiri acik_mi.TARAMA_ALANLARI sirasiyla, durum 'belirsiz', kanit bos, not SCAN_NOTE). Sonraki adimlarin
      eski ciktilari da silinir (ajan dosyalari dahil: adim bastan baslar).
  acik_mi_denetim.py kanit <OUT>
      Girdi: orneklem ve OUT\_acikmi\*_dogrulama.jsonl (ajan satirlari; ayni mekanin son satiri gecer).
      'sil' ve 'kartta belirt' disindaki her ornek mekani ikinci kapinin tarama satiri olur: 'ret' + 'dokunma' ->
      'açık', geri kalani (onay + dokunma, satiri yok ya da gecersiz) -> 'belirsiz'; kanit alanlari ajan satirindan
      (kapi 'açık' satirinda eski_kanit/footer_kanit'a bakar, dogrulama satirinda bakmaz). Bastan yazar:
      OUT\_acikmi_acik\acik.jsonl, OUT\acik-mi-acik-liste.jsonl (o mekanlarin orneklem satirlari) ve
      OUT\kanitlar\acikmi\kanit.jsonl + urls.txt (fetch_snapshot --must-contain / --urls): 'sil' ve 'kartta belirt'
      satirinin kanit_url + kanit_alinti'si, 'sil'in gerekce'sindeki her 'adres «alıntı»' (ikinci kaynak).
      ikinci_alintisiz: gerekce'sinde kanit_url'den baska sitede 'adres «alıntı»' olmayan 'sil' mekanlari.
  acik_mi_denetim.py sayim <OUT>
      Girdi: orneklem, ajan satirlari, kanit'in dosyalari (o zamandan beri degismemis olmali), OUT\acik-mi-acik.json
      (ikinci kapi; liste bossa gerekmez), OUT\kanitlar\acikmi\index.jsonl (fetch_snapshot; kanit adresi yoksa
      gerekmez). Mekan basina sinif (CLASSES): acik_dogrulandi ('ret' + 'dokunma', ikinci kapida bulgusuz),
      dogrulanamadi (ikinci kapida bulgulu), kapanis_iki_kaynak ('sil'; en az iki ayri sitede alinti kopyada teyitli),
      kapanis_teyitsiz ('sil'; digerleri), belirt_teyitli / belirt_teyitsiz ('kartta belirt'; kanit_url alintisi
      kopyada teyitli mi). Alinti teyitli: adresin index satirinda BAD_FLAGS yok ve alinti evidence.missing'de degil.
      dogrulanan = VERIFIED siniflar; yeni_ajan = RETRY siniflari + ikinci kapida bulgulu 'ret' + 'dokunma'.
      Yazar: OUT\acik-mi-sayim.json (sayilar, siniflar, mekan basina ayrinti).
stdout tek satir JSON (hata: {"tool", "error"}). Cikis: 0 tamam, 2 kullanim ya da girdi hatasi (girdiler silmeden once
okunur: hatada hicbir sey silinmez; kilitli eski cikti da cikis 2).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Any

import acik_mi
import common
import fetch_snapshot

TOOL = "acik_mi_denetim"
VENUES = Path("_dump", "Mekânlar.jsonl")
PRODUCTION_REPORT = "acik-mi-uretim.json"
SAMPLE_NAME = "acik-mi-orneklem.jsonl"
BATCH_DIR = "_acikmi"
AUDIT_REPORT = "acik-mi-denetim.json"
OPEN_DIR, OPEN_ROWS = "_acikmi_acik", "acik.jsonl"
OPEN_LIST, OPEN_REPORT = "acik-mi-acik-liste.jsonl", "acik-mi-acik.json"
EVIDENCE_DIR = Path("kanitlar", "acikmi")
EVIDENCE_NAME, URLS_NAME, INDEX_NAME = "kanit.jsonl", "urls.txt", fetch_snapshot.INDEX_NAME
COUNT_NAME = "acik-mi-sayim.json"
MIN_SAMPLE, SHARE, BATCH = 8, 10, 8  # en az 8 mekan ve mekanlarin 1/SHARE'i; parti basina en cok BATCH mekan
PRIORITIES = MappingProxyType({"a": "üretim kapısının bulgusu", "b": "üretimde belirsiz", "c": "tarihli not",
                               "d": "çekişmeli karar"})
RANDOM, FULL = "rastgele", "tam"
SCAN_NOTE = "denetim örneklemi"
UNSURE, MOVED, REJECT = "belirsiz", "taşındı", "ret"
CONTESTED = (acik_mi.CLOSED, MOVED)
EVIDENCE_KEYS = ("kanit_url", "kanit_alinti", "kanit_tarihi")
SECOND_SOURCE = re.compile(r"(https?://[^\s«»]+)\s*«([^»]+)»")  # gerekce'de 'adres «alıntı»'
URL_TAIL = ".,;:!?"
BAD_FLAGS = frozenset({"fetch_failed", "soft_404", "evidence_stale"})  # alinti duzeyi: evidence.missing
CLASSES = ("acik_dogrulandi", "dogrulanamadi", "kapanis_iki_kaynak", "kapanis_teyitsiz", "belirt_teyitli",
           "belirt_teyitsiz")
VERIFIED = ("acik_dogrulandi", "kapanis_iki_kaynak", "belirt_teyitli")
RETRY = ("kapanis_teyitsiz", "belirt_teyitsiz")
text = acik_mi.text


class AuditError(Exception):
    """Kullanim ya da girdi hatasi (cikis 2)."""


@dataclass(frozen=True)
class Plan:
    """Orneklem + ajan satirlarindan kanit'in yazdiklari; sayim ayni plani diskteki dosyalarla karsilastirir."""
    listed: tuple[dict[str, Any], ...]    # ikinci kapinin mekanlari (orneklem satirlari)
    scans: tuple[dict[str, Any], ...]     # ikinci kapinin tarama satirlari
    evidence: tuple[dict[str, Any], ...]  # fetch_snapshot --must-contain satirlari
    no_second: tuple[str, ...]            # P0 icin ikinci kaynak alintisi olmayan 'sil' mekanlari


# ------------------------------------------------------------------ okuma ve yazma

def entry_of(row: dict[str, Any] | None) -> str:
    return text((row or {}).get("entry_id"))


def action(row: dict[str, Any] | None) -> str:
    return text((row or {}).get("eylem"))


def found_open(row: dict[str, Any] | None) -> bool:
    return bool(row) and (text(row.get("sonuc")), action(row)) == (REJECT, acik_mi.KEEP)


def same_path(left: str | Path, right: str | Path) -> bool:
    return os.path.normcase(os.path.abspath(left)) == os.path.normcase(os.path.abspath(right))


def inside(path: Path, folder: Path) -> bool:
    path, folder = path.resolve(), folder.resolve()
    return path == folder or folder in path.parents


def read_rows(path: Path, what: str) -> list[dict[str, Any]]:
    """JSONL nesne satirlari (acik_mi.read_jsonl); dosya yoksa ya da bozuksa AuditError."""
    if not path.is_file():
        raise AuditError(f"{what} yok: {path}")
    try:
        return [record.row for record in acik_mi.read_jsonl(path)]
    except acik_mi.UsageError as exc:
        raise AuditError(str(exc)) from exc
    except OSError as exc:
        raise AuditError(f"{what} okunamadı: {path} ({exc})") from exc


def read_report(path: Path, what: str) -> dict[str, Any]:
    """acik_mi --out raporu (findings listesi olan JSON nesnesi)."""
    if not path.is_file():
        raise AuditError(f"{what} yok: {path}")
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AuditError(f"{what} okunamadı: {path} ({exc})") from exc
    if not isinstance(report, dict) or not isinstance(report.get("findings"), list):
        raise AuditError(f"{what} acik_mi raporu değil (findings listesi yok): {path}")
    return report


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _writable(function: Callable[[str], object], path: str, error: BaseException) -> None:
    """rmtree hata cagrisi: salt okunur dosyayi (Copy-Item ozniteligi korur) yazilabilir yapip bir kez daha dener."""
    if not isinstance(error, PermissionError):
        raise error
    os.chmod(path, stat.S_IWRITE)
    function(path)


def clear(folders: Iterable[Path], files: Iterable[Path]) -> None:
    """Eski ciktilar: klasorler ve dosyalar silinir; silinemeyen (kilitli) dosya cikis 2."""
    try:
        for folder in folders:
            if folder.exists():
                shutil.rmtree(folder, onexc=_writable)
        for path in files:
            path.unlink(missing_ok=True)
    except OSError as exc:
        raise AuditError(f"eski çıktı silinemedi ({exc}); kilitli dosyayı kapatıp yeniden çalıştır") from exc


def check_out(out: Path, xlsx: Path | None = None, folder: str = "") -> None:
    """OUT var; paketin (Excel'in klasoru) icinde degil; ACIKMI aracin sildigi klasorlerle cakismiyor."""
    if not out.is_dir():
        raise AuditError(f"OUT klasörü yok: {out} (önce L0)")
    if xlsx is not None and inside(out, xlsx.parent):
        raise AuditError(f"OUT paketin içinde: {out} (denetim pakete yazmaz)")
    managed = (out / BATCH_DIR, out / OPEN_DIR, out / EVIDENCE_DIR)
    if folder and any(inside(Path(folder), path) or inside(path, Path(folder)) for path in managed):
        raise AuditError(f"ACIKMI aracın sildiği klasörle çakışıyor: {folder}")


# ------------------------------------------------------------------ orneklem

def load_venues(out: Path) -> list[dict[str, Any]]:
    venues = read_rows(out / VENUES, "xlsx_dump'ın mekân listesi (önce L0'ın xlsx_dump'ı)")
    nameless = [number for number, row in enumerate(venues, 1) if not entry_of(row)]
    if not venues or nameless:
        raise AuditError(f"mekân listesi boş ya da entry_id'siz satır var (satır {nameless[:5]}): {out / VENUES}")
    return venues


def production_groups(report: dict[str, Any], sweep: acik_mi.Sweep) -> dict[str, set[str]]:
    """Uretim beyanindan (a), (b), (d) kumeleri."""
    scans = [(entry_of(rec.row), text(rec.row.get("durum"))) for rec in sweep.scans]
    verifs = [(entry_of(rec.row), text(rec.row.get("sonuc")), action(rec.row)) for rec in sweep.verifs]
    verified = {entry for entry, _, _ in verifs}
    unsure = {entry for entry, durum in scans if durum == UNSURE and entry not in verified}
    kept = {entry for entry, sonuc, eylem in verifs if (sonuc, eylem) == (acik_mi.CONFIRM, acik_mi.KEEP)}
    reopened = {entry for entry, sonuc, eylem in verifs if (sonuc, eylem) == (REJECT, acik_mi.KEEP)}
    contested = {entry for entry, durum in scans if durum in CONTESTED} & reopened
    flagged = {text(item.get("entry_id")) for item in report["findings"] if isinstance(item, dict)}
    return {"a": flagged - {""}, "b": (unsure | kept) - {""}, "d": contested - {""}}


def production(out: Path, folder: str) -> tuple[dict[str, set[str]], str]:
    """(a, b, d kumeleri, uretim durumu). Rapor yoksa ACIKMI okunmaz; baska klasorun ya da listenin raporu hatadir."""
    if not folder:
        return {}, "verilmedi"
    path = out / PRODUCTION_REPORT
    if not path.is_file():
        return {}, "rapor yok"
    report = read_report(path, "üretim beyanı kapısının raporu")
    lists = report.get("mekanlar")
    same_list = isinstance(lists, list) and len(lists) == 1 and same_path(str(lists[0]), out / VENUES)
    if not same_list or not same_path(str(report.get("acik_mi", "")), folder):
        raise AuditError(f"{path} bu açık-mı klasörünün ve teslim listesinin raporu değil "
                         f"(acik_mi={report.get('acik_mi')!r}, mekanlar={lists!r}): üretim beyanı kapısını yeniden "
                         "çalıştır")
    try:
        sweep = acik_mi.load_sweep(Path(folder))
    except acik_mi.UsageError as exc:
        raise AuditError(f"üretim açık-mı klasörü okunamadı: {exc}") from exc
    return production_groups(report, sweep), "okundu"


def has_dated_note(card: dict[str, Any]) -> bool:
    return bool(acik_mi.AS_OF.search("\n".join(text(card.get(field)) for field in acik_mi.TEXT_FIELDS)))


def reasons(venues: Sequence[dict[str, Any]], groups: dict[str, set[str]]) -> dict[str, str]:
    """entry_id -> oncelik harfleri ('a+c'; oncelikli degilse bos)."""
    groups = {**groups, "c": {entry_of(card) for card in venues if has_dated_note(card)}}
    return {entry_of(card): "+".join(letter for letter in PRIORITIES if entry_of(card) in groups.get(letter, ()))
            for card in venues}


def sample_size(count: int, full: bool = False) -> int:
    """n: en az MIN_SAMPLE ve onda bir (yukari yuvarlanir); daha az mekanda ya da --tam'da hepsi."""
    return count if full else min(count, max(MIN_SAMPLE, -(-count // SHARE)))


def random_key(excel_sha256: str, entry_id: str) -> str:
    return hashlib.sha256((excel_sha256.lower() + entry_id).encode("utf-8")).hexdigest()


def choose(venues: Sequence[dict[str, Any]], why: dict[str, str], excel_sha256: str,
           full: bool) -> list[dict[str, Any]]:
    """Once oncelikliler (Excel sirasiyla), sonra kalanlardan en az ceil(n/2), toplam en az n (sha256 sirasiyla)."""
    n = sample_size(len(venues), full)
    first = [{**card, "neden": why[entry_of(card)]} for card in venues if why[entry_of(card)]]
    rest = sorted((card for card in venues if not why[entry_of(card)]),
                  key=lambda card: random_key(excel_sha256, entry_of(card)))
    label = FULL if full else RANDOM
    return first + [{**card, "neden": label} for card in rest[:max(-(-n // 2), n - len(first))]]


def scan_row(card: dict[str, Any], durum: str = UNSURE, evidence: dict[str, Any] | None = None,
             note: str = SCAN_NOTE) -> dict[str, Any]:
    """Tarama satiri, acik_mi.TARAMA_ALANLARI sirasiyla."""
    return {**dict.fromkeys(acik_mi.TARAMA_ALANLARI, ""), **(evidence or {}), "entry_id": entry_of(card),
            "title": text(card.get("title")), "durum": durum, "not": note}


def split_counts(chosen: Sequence[dict[str, Any]]) -> dict[str, int]:
    full = any(card.get("neden") == FULL for card in chosen)
    picked = sum(1 for card in chosen if card.get("neden") not in (RANDOM, FULL))
    return {"orneklem": len(chosen), "oncelikli": picked, (FULL if full else RANDOM): len(chosen) - picked}


def sample_command(args: argparse.Namespace) -> dict[str, Any]:
    out, folder = args.out, (args.acik_mi or "").strip()
    check_out(out, args.xlsx, folder)
    venues = load_venues(out)
    if not args.xlsx.is_file():
        raise AuditError(f"teslim Excel'i bulunamadı: {args.xlsx}")
    excel = common.sha256_file(args.xlsx)
    groups, status = production(out, folder)
    why = reasons(venues, groups)
    chosen = choose(venues, why, excel, args.tam)
    clear((out / BATCH_DIR, out / OPEN_DIR, out / EVIDENCE_DIR),
          [out / name for name in (SAMPLE_NAME, AUDIT_REPORT, OPEN_LIST, OPEN_REPORT, COUNT_NAME)])
    write_jsonl(out / SAMPLE_NAME, chosen)
    (out / BATCH_DIR).mkdir()
    batches = [chosen[start:start + BATCH] for start in range(0, len(chosen), BATCH)]
    for number, batch in enumerate(batches, 1):
        write_jsonl(out / BATCH_DIR / f"parti_{number:02d}.jsonl", map(scan_row, batch))
    tally = {letter: sum(1 for card in venues if letter in why[entry_of(card)].split("+")) for letter in PRIORITIES}
    return {"tool": TOOL, "komut": "orneklem", "mekan": len(venues), "n": sample_size(len(venues), args.tam),
            **split_counts(chosen), "oncelik": tally, "parti": len(batches), "uretim": status,
            "excel_sha256": excel, "orneklem_dosyasi": str(out / SAMPLE_NAME)}


# ------------------------------------------------------------------ kanit

def agent_rows(out: Path) -> dict[str, dict[str, Any]]:
    """entry_id -> ajanin son satiri (dosya adi, sonra satir sirasiyla); entry_id'siz satir sayilmaz (kapi bulur)."""
    folder = out / BATCH_DIR
    if not folder.is_dir():
        raise AuditError(f"parti klasörü yok: {folder} (önce orneklem)")
    rows: dict[str, dict[str, Any]] = {}
    for path in sorted(folder.glob(f"*{acik_mi.VERIFY_SUFFIX}.jsonl")):
        for row in read_rows(path, "ajan satırları"):
            if entry_of(row):
                rows[entry_of(row)] = row
    return rows


def open_scan(card: dict[str, Any], row: dict[str, Any] | None) -> dict[str, Any]:
    """Ikinci kapinin tarama satiri: 'ret' + 'dokunma' -> 'açık', geri kalani 'belirsiz'; kanit ajan satirindan."""
    evidence = {key: (row or {}).get(key, "") for key in EVIDENCE_KEYS}
    note = f"denetim: {text(row.get('sonuc'))} + {action(row)}" if row else "denetim: doğrulama satırı yok"
    return scan_row(card, acik_mi.OPEN if found_open(row) else UNSURE, evidence, note)


def second_sources(row: dict[str, Any]) -> list[tuple[str, str]]:
    return [(url.rstrip(URL_TAIL), quote.strip()) for url, quote in SECOND_SOURCE.findall(text(row.get("gerekce")))]


def evidence_lines(entry: str, row: dict[str, Any]) -> list[dict[str, Any]]:
    """fetch_snapshot --must-contain satirlari: kanit adresi + alintisi; 'sil'de her ikinci kaynak."""
    pairs = [(text(row.get("kanit_url")), text(row.get("kanit_alinti")), "kanit")]
    if action(row) == acik_mi.DELETE:
        pairs += [(url, quote, "ikinci_kaynak") for url, quote in second_sources(row)]
    return [{"url": url, "must_contain": [quote], "entry_id": entry, "rol": role} for url, quote, role in pairs
            if url and quote]


def lacks_second_source(row: dict[str, Any]) -> bool:
    first = acik_mi.host_of(text(row.get("kanit_url")))
    hosts = [acik_mi.host_of(url) for url, quote in second_sources(row) if quote]
    return not any(host and not acik_mi.same_site(host, first) for host in hosts)


def build_plan(chosen: Sequence[dict[str, Any]], rows: dict[str, dict[str, Any]]) -> Plan:
    listed, scans, evidence, no_second = [], [], [], []
    for card in chosen:
        entry = entry_of(card)
        row = rows.get(entry)
        if action(row) in (acik_mi.DELETE, acik_mi.NOTE):
            evidence += evidence_lines(entry, row)
            if action(row) == acik_mi.DELETE and lacks_second_source(row):
                no_second.append(entry)
        else:
            listed.append(card)
            scans.append(open_scan(card, row))
    return Plan(tuple(listed), tuple(scans), tuple(evidence), tuple(no_second))


def load_plan(out: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], Plan]:
    check_out(out)
    chosen = read_rows(out / SAMPLE_NAME, "örneklem (önce orneklem)")
    rows = agent_rows(out)
    return chosen, rows, build_plan(chosen, rows)


def evidence_command(args: argparse.Namespace) -> dict[str, Any]:
    out = args.out
    chosen, _, plan = load_plan(out)
    clear((out / OPEN_DIR, out / EVIDENCE_DIR), [out / name for name in (OPEN_LIST, OPEN_REPORT, COUNT_NAME)])
    write_jsonl(out / OPEN_DIR / OPEN_ROWS, plan.scans)
    write_jsonl(out / OPEN_LIST, plan.listed)
    write_jsonl(out / EVIDENCE_DIR / EVIDENCE_NAME, plan.evidence)
    urls = list(dict.fromkeys(line["url"] for line in plan.evidence))
    (out / EVIDENCE_DIR / URLS_NAME).write_text("".join(f"{url}\n" for url in urls), encoding="utf-8")
    opened = sum(1 for scan in plan.scans if scan["durum"] == acik_mi.OPEN)
    return {"tool": TOOL, "komut": "kanit", "orneklem": len(chosen), "liste": len(plan.listed), "acik": opened,
            "belirsiz": len(plan.scans) - opened, "kanit_mekan": len(chosen) - len(plan.listed),
            "kanit_adres": len(urls), "ikinci_alintisiz": list(plan.no_second),
            "kanit_dosyasi": str(out / EVIDENCE_DIR / EVIDENCE_NAME)}


# ------------------------------------------------------------------ sayim

def check_unchanged(out: Path, plan: Plan) -> None:
    """kanit'ten sonra orneklem ya da ajan satirlari degistiyse ikinci kapi ve kopya eski satirlara aittir."""
    expected = {out / OPEN_DIR / OPEN_ROWS: plan.scans, out / OPEN_LIST: plan.listed,
                out / EVIDENCE_DIR / EVIDENCE_NAME: plan.evidence}
    stale = [path.name for path, rows in expected.items() if read_rows(path, "kanit çıktısı (önce kanit)") != list(rows)]
    if stale:
        raise AuditError(f"örneklem ya da ajan satırları kanit'ten sonra değişti ({', '.join(stale)}): kanit'ten "
                         "başlayarak yeniden çalıştır")


def open_codes(out: Path, plan: Plan) -> dict[str, list[str]]:
    """Ikinci kapinin bulgu kodlari, mekan basina; liste bossa kapi calismaz (bos liste cikis 2)."""
    if not plan.listed:
        return {}
    path = out / OPEN_REPORT
    report = read_report(path, "ikinci kapının raporu (kanit'ten sonra acik_mi çalışmalı)")
    listed = {entry_of(card) for card in plan.listed}
    if not same_path(str(report.get("acik_mi", "")), out / OPEN_DIR) or report.get("mekan") != len(listed):
        raise AuditError(f"{path} bu listenin raporu değil (acik_mi={report.get('acik_mi')!r}, "
                         f"mekan={report.get('mekan')!r}): ikinci kapıyı yeniden çalıştır")
    codes: dict[str, list[str]] = {}
    for item in report["findings"]:
        if isinstance(item, dict):
            codes.setdefault(text(item.get("entry_id")), []).append(text(item.get("code")))
    return codes


def quote_found(row: dict[str, Any] | None, quote: str) -> bool:
    evidence = (row or {}).get("evidence")
    if not row or set(row.get("flags") or ()) & BAD_FLAGS or not isinstance(evidence, dict):
        return False
    missing = {fetch_snapshot.normalize_for_match(str(item)) for item in evidence.get("missing") or ()}
    return (evidence.get("needed") or 0) > 0 and fetch_snapshot.normalize_for_match(quote) not in missing


def confirmed_quotes(out: Path, plan: Plan) -> set[tuple[str, str]]:
    """(adres, alinti) ciftleri: kopyada teyitli olanlar; kanit adresi varsa fetch_snapshot index'i sart."""
    if not plan.evidence:
        return set()
    path = out / EVIDENCE_DIR / INDEX_NAME
    if not path.is_file():
        raise AuditError(f"kanıt kopyası yok: {path} (kanit'ten sonra fetch_snapshot çalışmalı)")
    try:
        index = {row["url"]: row for row in fetch_snapshot.read_index_rows(path)}
    except (OSError, ValueError) as exc:
        raise AuditError(f"kanıt kopyası okunamadı: {exc}") from exc
    pairs = ((line["url"], line["must_contain"][0]) for line in plan.evidence)
    return {(url, quote) for url, quote in pairs if quote_found(index.get(url), quote)}


def distinct_sites(urls: Iterable[str]) -> int:
    """Ayri site sayisi (alt alan adi ayni site: acik_mi.same_site)."""
    sites: list[str] = []
    for host in map(acik_mi.host_of, urls):
        if host and not any(acik_mi.same_site(host, site) for site in sites):
            sites.append(host)
    return len(sites)


def venue_class(row: dict[str, Any] | None, codes: list[str], good: list[dict[str, Any]]) -> str:
    if action(row) == acik_mi.DELETE:
        return "kapanis_iki_kaynak" if distinct_sites(line["url"] for line in good) >= 2 else "kapanis_teyitsiz"
    if action(row) == acik_mi.NOTE:
        return "belirt_teyitli" if any(line["rol"] == "kanit" for line in good) else "belirt_teyitsiz"
    return "acik_dogrulandi" if found_open(row) and not codes else "dogrulanamadi"


def classify(card: dict[str, Any], row: dict[str, Any] | None, codes: list[str], lines: list[dict[str, Any]],
             confirmed: set[tuple[str, str]]) -> dict[str, Any]:
    good = [line for line in lines if (line["url"], line["must_contain"][0]) in confirmed]
    sinif = venue_class(row, codes, good)
    return {"entry_id": entry_of(card), "title": text(card.get("title")), "neden": card.get("neden"),
            "sinif": sinif, "kodlar": codes, "teyitli": [line["url"] for line in good],
            "teyitsiz": [line["url"] for line in lines if line not in good],
            "yeni_ajan": sinif in RETRY or (found_open(row) and bool(codes))}


def count_command(args: argparse.Namespace) -> dict[str, Any]:
    out = args.out
    chosen, rows, plan = load_plan(out)
    check_unchanged(out, plan)
    codes, confirmed = open_codes(out, plan), confirmed_quotes(out, plan)
    lines: dict[str, list[dict[str, Any]]] = {}
    for line in plan.evidence:
        lines.setdefault(line["entry_id"], []).append(line)
    details = [classify(card, rows.get(entry_of(card)), codes.get(entry_of(card), []), lines.get(entry_of(card), []),
                        confirmed) for card in chosen]
    classes = {name: [item["entry_id"] for item in details if item["sinif"] == name] for name in CLASSES}
    verified = sum(len(classes[name]) for name in VERIFIED)
    summary = {"tool": TOOL, "komut": "sayim", **split_counts(chosen), "dogrulanan": verified,
               "dogrulanamayan": len(chosen) - verified, "sinif": {name: len(ids) for name, ids in classes.items()},
               "yeni_ajan": [item["entry_id"] for item in details if item["yeni_ajan"]],
               "sayim_dosyasi": str(out / COUNT_NAME)}
    common.write_json(out / COUNT_NAME, {**summary, "siniflar": classes, "mekanlar": details})
    return summary


# ------------------------------------------------------------------ komut satiri

COMMANDS: MappingProxyType[str, Callable[[argparse.Namespace], dict[str, Any]]] = MappingProxyType(
    {"orneklem": sample_command, "kanit": evidence_command, "sayim": count_command})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="city-audit açık-mı adımı (K39, B15): örneklem, açık kanıtı, sayım")
    sub = parser.add_subparsers(dest="command", required=True)
    sample = sub.add_parser("orneklem", help=r"öncelikli + rastgele örneklem ve OUT\_acikmi\parti_NN.jsonl")
    sample.add_argument("out", type=Path, help="denetim klasörü (OUT)")
    sample.add_argument("--xlsx", type=Path, required=True, help="teslim Excel'i (rastgele sıranın tohumu; okunur)")
    sample.add_argument("--acik-mi", help="üretimin açık-mı klasörü (ACIKMI; boş = verilmedi)")
    sample.add_argument("--tam", action="store_true", help="L2: bütün mekânlar")
    for name, purpose in (("kanit", "ikinci kapının tarama satırları ve kanıt kopyası listesi"),
                          ("sayim", r"sınıflar ve sayılar -> OUT\acik-mi-sayim.json")):
        sub.add_parser(name, help=purpose).add_argument("out", type=Path, help="denetim klasörü (OUT)")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    common.setup_utf8()
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return common.EXIT_USAGE if stop.code else common.EXIT_OK
    try:
        summary = COMMANDS[args.command](args)
    except AuditError as exc:
        common.emit({"tool": TOOL, "error": str(exc)})
        return common.EXIT_USAGE
    except OSError as exc:  # OUT'a yazilamadi (izin, disk); yakalanmazsa cikis 1 'bulgu' ile karisir
        common.emit({"tool": TOOL, "error": f"yazılamadı: {exc}"})
        return common.EXIT_USAGE
    common.emit(summary)
    return common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
