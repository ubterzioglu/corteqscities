"""Kisa listedeki Commons adaylarinin kucuk onizlemelerini indirir, contact_sheet girdisi (items.jsonl) yazar (A6; pilot: foto_onizleme.py).

Kullanim: photo_previews.py <is_klasoru> [--decisions <is>/foto/decisions.json] [--candidates <dosya> ...]
                            [--preview-dir <is>/foto/onizleme] [--items-out <is>/foto/items.jsonl]
                            [--width 330] [--max 600] [--out rapor.json]
Okur: decisions (photo_prefilter --out: {decisions: [...], shortlists: {entry_id: [candidate_id, ...]}}), adaylar,
      <is>/data/Mekânlar.jsonl ve Mahalleler.jsonl (etiketteki ad); data/'da olmayan kayit (ek turun yeni mekani) icin
      aday ve karar dosyalarinin yanindaki venues.jsonl 'name'i; o da yoksa entry_id.
Adaylar: varsayilan ana tur <is>/foto/candidates.jsonl (sart), ek tur klasorleri <is>/foto_*/candidates.jsonl (A12, or.
      foto_ek16) ve karar dosyasinin yanindaki candidates.jsonl (varsa; klasor foto_* disinda da olur, pilot
      foto_onizleme), bu sirayla; --candidates (tekrarlanabilir) verilirse yalniz onlar. Ayni kimlikte onceki dosyanin
      kaydi kalir. Okunan dosyalar ozette (candidate_files). Tarama kurali photo_rows ile ortak (photo_rounds);
      photo_rows karar dosyasinin klasorunu taramaz: ek tur foto_* disindaysa photo_rows'a --candidates verilir.
Yazar: <preview-dir>/<sha1(url)>.jpg (onbellek: dosya varsa yeniden indirilmez) ve items.jsonl
       {key, path, label, group, decision}.
Yalniz https://upload.wikimedia.org/ ve https://thumb.wikimedia.org/; thumb adresi istenen genislige cevrilir, sorgu
(utm_*) atilir. Wikimedia 2026: dogrudan istekte yalniz standart genislikler (download_plan.STANDARD_WIDTHS, or.
330/500/960/1280; 1600 = HTTP 400); --width bunlardan biri olmali (degilse kullanim hatasi).
Nezaket: seri istek, istekler arasi 0.5 sn, aciklayici User-Agent, 429/503'te Retry-After (en cok 30 sn) ile 3 deneme;
hak biterse calisma tamamen durur (status=resume_later). Gorsel olmayan yanit (or. HTML hata sayfasi) yazilmaz.
stdout tek satir JSON; cikis 0 hepsi hazir / 1 eksik var / 2 kullanim (okunamayan ya da UTF-8 olmayan girdi,
yazilamayan onizleme/cikti dahil).
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterator

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8, write_json
from download_plan import STANDARD_WIDTHS
from photo_rounds import load_candidates, read_jsonl, round_files, shown

USER_AGENT = "CorteqsCityToolkit/0.1 (content research; https://www.mediawiki.org/wiki/API:Etiquette)"
ALLOWED_PREFIXES = ("https://upload.wikimedia.org/", "https://thumb.wikimedia.org/")
REQUEST_DELAY = 0.5
MAX_ATTEMPTS = 3
RETRY_CAP_SECONDS = 30
TIMEOUT_SECONDS = 30
RETRY_STATUSES = (429, 503)
NAME_SHEETS = ("Mekânlar", "Mahalleler")
THUMB_WIDTH = re.compile(r"/(\d+)px-")
CANDIDATES, VENUES = "candidates.jsonl", "venues.jsonl"

Response = tuple[int, dict[str, str], bytes]
Transport = Callable[[str, dict[str, str], float], Response]


class TransportError(Exception):
    """Ag/baglanti hatasi (HTTP durumu yok)."""


class UsageError(Exception):
    """Eksik/bozuk girdi ya da gecersiz arguman (cikis 2)."""


@dataclass(frozen=True)
class Outcome:
    body: bytes | None = None
    error: str | None = None
    stop: bool = False


@dataclass(frozen=True)
class Inputs:
    shortlists: dict[str, list[str]]
    decision_of: dict[str, Any]
    candidates: dict[str, dict[str, Any]]
    names: dict[str, str]


def urllib_transport(url: str, headers: dict[str, str], timeout: float) -> Response:
    """Gercek tasima: HTTP hatasi durum kodu olarak doner, ag hatasi TransportError olur."""
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, dict(response.headers.items()), response.read()
    except urllib.error.HTTPError as error:
        headers_out = dict(error.headers.items()) if error.headers else {}
        error.close()
        return error.code, headers_out, b""
    except (urllib.error.URLError, http.client.HTTPException, OSError, ValueError) as error:
        raise TransportError(f"{type(error).__name__}: {error}") from error


def thumb_url(url: str, width: int) -> str:
    """Commons thumb adresini istenen genislige cevirir, sorguyu (utm_*) atar; thumb degilse yalniz sorguyu atar."""
    url = url.split("?", 1)[0]
    return THUMB_WIDTH.sub(f"/{width}px-", url, count=1) if "/thumb/" in url else url


def _header(headers: dict[str, str], name: str) -> str:
    return next((str(v) for k, v in headers.items() if k.lower() == name), "")


def retry_wait(headers: dict[str, str], attempt: int) -> float:
    raw = _header(headers, "retry-after").strip()
    return float(min(int(raw), RETRY_CAP_SECONDS)) if raw.isdigit() else float(attempt * 5)


def _accept(headers: dict[str, str], body: bytes) -> Outcome:
    ctype = _header(headers, "content-type").lower()
    if ctype and not ctype.startswith("image/"):
        return Outcome(error=f"gorsel degil ({ctype.split(';')[0].strip()})")
    return Outcome(body=body) if body else Outcome(error="bos yanit")


def fetch(transport: Transport, sleep: Callable[[float], None], url: str) -> Outcome:
    """Tek onizleme; 429/503'te Retry-After ile en cok 3 deneme, hak biterse stop=True."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            status, headers, body = transport(url, {"User-Agent": USER_AGENT}, TIMEOUT_SECONDS)
        except TransportError as error:
            return Outcome(error=f"ag: {error}")
        if 200 <= status < 300:
            return _accept(headers, body)
        if status not in RETRY_STATUSES:
            return Outcome(error=f"HTTP {status}")
        if attempt == MAX_ATTEMPTS:
            return Outcome(error=f"HTTP {status} ({MAX_ATTEMPTS} deneme)", stop=True)
        sleep(retry_wait(headers, attempt))
    raise AssertionError("ulasilamaz")  # pragma: no cover


def write_atomic(target: Path, data: bytes) -> None:
    temporary = target.with_name(target.name + ".part")
    temporary.write_bytes(data)
    os.replace(temporary, target)


def candidate_files(work: Path, decisions_path: Path) -> list[Path]:
    """Varsayilan aday dosyalari (photo_rounds kurali): ana tur foto/ (sart), ek tur klasorleri foto_*/ (A12, varsa)
    ve karar dosyasinin yanindaki candidates.jsonl (varsa, listede yoksa; pilot foto_onizleme)."""
    return round_files(work, CANDIDATES, [decisions_path.parent])


def load_names(work: Path, folders: list[Path]) -> dict[str, str]:
    """entry_id -> etiketteki ad: data/ basliklari; data/'da olmayan kayit (ek turun henuz birlestirilmemis yeni
    mekani) icin verilen klasorlerdeki venues.jsonl 'name'i (photo_candidates plan-from-xlsx bicimi)."""
    names: dict[str, str] = {}
    for sheet in NAME_SHEETS:
        path = work / "data" / f"{sheet}.jsonl"
        if path.is_file():
            names.update({r.get("entry_id"): r.get("title") for r in read_jsonl(path) if r.get("entry_id")})
    for folder in dict.fromkeys(folders):
        path = folder / VENUES
        if not path.is_file():
            continue
        for row in read_jsonl(path):
            if row.get("entry_id") and not names.get(row["entry_id"]):
                names[row["entry_id"]] = row.get("name") or row.get("title")
    return names


def load_inputs(work: Path, decisions_path: Path, candidate_paths: list[Path]) -> Inputs:
    try:
        decisions = json.loads(decisions_path.read_text(encoding="utf-8-sig"))
    except UnicodeDecodeError as error:
        raise UsageError(f"{decisions_path}: UTF-8 degil ({error.reason})") from error
    except json.JSONDecodeError as error:
        raise UsageError(f"{decisions_path}: gecersiz JSON ({error.msg})") from error
    shortlists = decisions.get("shortlists") if isinstance(decisions, dict) else None
    rows = decisions.get("decisions", []) if isinstance(decisions, dict) else None
    if not isinstance(shortlists, dict) or not all(isinstance(v, list) for v in shortlists.values()):
        raise UsageError(f"{decisions_path}: shortlists {{entry_id: [candidate_id, ...]}} olmali")
    if not isinstance(rows, list) or not all(isinstance(d, dict) for d in rows):
        raise UsageError(f"{decisions_path}: decisions nesne listesi olmali")
    folders = [path.parent for path in candidate_paths] + [decisions_path.parent]
    return Inputs(shortlists=shortlists, decision_of={d.get("candidate_id"): d.get("decision") for d in rows},
                  candidates=load_candidates(candidate_paths), names=load_names(work, folders))


def pairs(shortlists: dict[str, list[str]]) -> Iterator[tuple[str, str]]:
    for entry_id, candidate_ids in shortlists.items():
        for candidate_id in candidate_ids:
            yield entry_id, candidate_id


def item_for(inputs: Inputs, entry_id: str, cid: str, target: Path) -> dict[str, Any]:
    candidate = inputs.candidates[cid]
    file_name = str(candidate.get("commons_file") or cid).replace("File:", "")[:60]
    return {"key": cid, "path": str(target), "label": f"{inputs.names.get(entry_id) or entry_id} · {file_name}",
            "group": entry_id, "decision": inputs.decision_of.get(cid)}


def collect(inputs: Inputs, args: argparse.Namespace, preview_dir: Path, transport: Transport,
            sleep: Callable[[float], None]) -> dict[str, Any]:
    items, errors, counts, stopped = [], [], {"downloaded": 0, "cached": 0}, False
    for entry_id, cid in pairs(inputs.shortlists):
        if len(items) >= args.max:
            break
        candidate = inputs.candidates.get(cid)
        source = str((candidate or {}).get("thumb_url") or (candidate or {}).get("original_url") or "")
        second_source = (candidate or {}).get("provider", "Wikimedia Commons") != "Wikimedia Commons"  # photo_sources.py
        if candidate is None or not source.startswith(("https://",) if second_source else ALLOWED_PREFIXES):
            errors.append({"key": cid, "why": "aday yok" if candidate is None else "izinli olmayan adres"})
            continue
        url = thumb_url(source, args.width)
        target = preview_dir / (hashlib.sha1(url.encode(), usedforsecurity=False).hexdigest() + ".jpg")
        if target.is_file() and target.stat().st_size > 0:
            counts["cached"] += 1
        else:
            sleep(REQUEST_DELAY)
            outcome = fetch(transport, sleep, url)
            if outcome.error:
                errors.append({"key": cid, "why": outcome.error})
                stopped = outcome.stop
                if stopped:
                    break
                continue
            write_atomic(target, outcome.body)
            counts["downloaded"] += 1
        items.append(item_for(inputs, entry_id, cid, target))
    return {"items": items, "errors": errors, "stopped": stopped, **counts}


def _positive(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError("en az 1 olmali")
    return number


def _standard_width(value: str) -> int:
    """Wikimedia 2026 dogrudan istekte yalniz standart genislikleri verir (1600 = HTTP 400: her istek bosa gider)."""
    number = int(value)
    if number not in STANDARD_WIDTHS:
        raise argparse.ArgumentTypeError(f"Wikimedia standart genisligi olmali: {'/'.join(map(str, STANDARD_WIDTHS))}")
    return number


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Commons kisa liste onizlemeleri + contact_sheet girdisi (items.jsonl)")
    p.add_argument("work", help="is klasoru (_is)")
    p.add_argument("--decisions", type=Path, help="varsayilan <is>/foto/decisions.json")
    p.add_argument("--candidates", type=Path, action="append",
                   help="aday dosyasi, tekrarlanabilir; verilmezse <is>/foto/, ek tur klasorleri <is>/foto_*/ (A12) "
                        "ve karar dosyasinin yanindaki candidates.jsonl")
    p.add_argument("--preview-dir", type=Path, help="onizleme onbellegi (varsayilan <is>/foto/onizleme)")
    p.add_argument("--items-out", type=Path, help="varsayilan <is>/foto/items.jsonl")
    p.add_argument("--width", type=_standard_width, default=330,
                   help="Wikimedia standart genislik (or. 330/500/960/1280; 1600 = HTTP 400)")
    p.add_argument("--max", type=_positive, default=600, help="en fazla onizleme sayisi")
    p.add_argument("--out", type=Path, help="ayrinti JSON (tum hatalar)")
    return p


def run(args: argparse.Namespace, transport: Transport, sleep: Callable[[float], None]) -> int:
    work = Path(os.path.abspath(args.work))
    if not work.is_dir():
        raise UsageError(f"is klasoru yok: {work}")
    decisions_path = Path(os.path.abspath(args.decisions or work / "foto" / "decisions.json"))
    candidate_paths = args.candidates or candidate_files(work, decisions_path)
    inputs = load_inputs(work, decisions_path, candidate_paths)
    preview_dir = Path(os.path.abspath(args.preview_dir or work / "foto" / "onizleme"))
    preview_dir.mkdir(parents=True, exist_ok=True)
    result = collect(inputs, args, preview_dir, transport, sleep)
    items_out = Path(os.path.abspath(args.items_out or work / "foto" / "items.jsonl"))
    items_out.parent.mkdir(parents=True, exist_ok=True)
    items_out.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in result["items"]), encoding="utf-8")
    if args.out:
        write_json(args.out, {"errors": result["errors"], "stopped": result["stopped"]})
    status = "resume_later" if result["stopped"] else ("findings" if result["errors"] else "ok")
    emit({"status": status, "items": len(result["items"]), "downloaded": result["downloaded"],
          "cached": result["cached"], "errors": len(result["errors"]), "error_examples": result["errors"][:5],
          "candidate_files": [shown(work, path) for path in candidate_paths], "items_out": str(items_out)})
    return EXIT_FINDINGS if result["errors"] else EXIT_OK


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    try:
        return run(args, transport, sleep)
    except (UsageError, OSError, ValueError) as error:  # yakalanmazsa cikis 1 olur ve 'bulgu' ile karisir
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    raise SystemExit(main())
