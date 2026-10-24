"""claim_check.py --claims claims.jsonl --snapshots <dir> [--snapshot-format toolkit|qwen-cache] [--mode unit|number]
                  [--min-chars 500] --out claim-checks.json
claim_extract iddialarinin degeri kartin kaynak snapshot metninde geciyor mu (K29/K34/K37/K40). Ag erisimi yok.
Eslesme: Kaynaklar.url -> snapshot url VEYA final_url (sema, 'www.', sondaki '/', #parca yok sayilir).
  toolkit    : <dir>/index.jsonl (fetch_snapshot) {url, final_url?, text_file, status|http_status?, error?, thin?, fetched_on|at?}
  qwen-cache : <dir>/<id>.json {url, final_url, status, error?, fetched_at} + <id>.txt (URL/FETCHED/TITLE basligi atilir)
  bicim verilmezse: index.jsonl varsa toolkit, yoksa *.json varsa qwen-cache.
Snapshot durumu: ok (>= --min-chars) / thin / http_error (>=400) / fetch_error / no_text; bulunamazsa not_found.
Deger duzeyi: 'unit' = sayi + birim/para/yuzde/gun adi (85,15 | 85.15 | € 85,15; 26 weken | 26 weeks; donderdag);
'number' = yalniz sayi. --mode unit (varsayilan) yalniz 'unit'i, --mode number ikisini kabul eder.
Ceviri es anlamlilari (yas, sure, saat, gun; hepsi 'unit') claim_synonyms'tadir; birimsiz sayi kelimesi kanit degildir.
Para 'scale' tasirsa ('€1,5 milyon') '1.500.000' ve '1,5 miljoen' kabul edilir. Alinti: kartin sayi/adlarina en yakin olan.
Sonuc onceligi: no_source > homepage_only_source (tum kaynaklar anasayfa) > supported (tum degerler ok/thin metinde)
> not_in_source (en az bir ok metin var, deger yok) > no_snapshot (metin yok / thin / hata).
'supported' DOGRULUK KANITI DEGILDIR, yalniz tutarliliktir. stdout tek satir JSON; cikis 0 hepsi supported / 1 bulgu / 2 hata
(UTF-8 olmayan ya da bozuk claims/index.jsonl dahil). Sayi bicimleri ve claims.jsonl okuyucusu claim_extract'tadir."""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from itertools import islice
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping
from urllib.parse import urlsplit

import common
from claim_extract import ClaimError, alternation as _alts, number_regex, read_claims
from claim_synonyms import (AMPM, ARTICLES, CLOCK_WORDS, DAY_NAMES, MONTH_NAMES, NUMBER_WORDS, NUMERIC_TEMPLATES, ORDINAL_WORDS,
                            SCALE_WORDS, TEMPLATE_PARTS, UNIT_WORDS, WORDED_KINDS, day_rx, ordinal_day_rx, words_rx)
from extra_checks import is_homepage

RESULTS = ("supported", "not_in_source", "no_snapshot", "homepage_only_source", "no_source")
STATE_RANK = {"ok": 0, "thin": 1, "no_text": 2, "http_error": 3, "fetch_error": 4}
SEARCHABLE = frozenset({"ok", "thin"})
DEFAULT_MIN_CHARS, SNIPPET_WIDTH, MAX_MATCHES = 500, 80, 50
NOTE = ("'supported' yalnız tutarlılıktır: değer, kartın gösterdiği kaynak snapshot metninde geçiyor. İddianın doğru, güncel "
        "ya da aynı statü/dönem için geçerli olduğunun kanıtı değil (doğruluk kanıtı değil); resmî kaynakla ayrıca doğrulanmalı. "
        "'not_in_source' kaynak metni olduğu hâlde değerin bulunmadığını, 'no_snapshot' metin olmadığı/ince olduğu için "
        "karar verilemediğini, 'homepage_only_source' kartın yalnız anasayfa(lar)a dayandığını gösterir.")
HEADER_LINE = re.compile(r"^(URL|FINAL_URL|FETCHED|TITLE|STATUS):\s?(.*)$", re.IGNORECASE)
MOJIBAKE_RUN = re.compile(r"[^\x00-\x7f]+")
DASHES = re.compile(r"[‐-―−]")
ANCHOR, WORD = re.compile(r"\d+|[A-ZÇĞİÖŞÜ]\w{3,}"), re.compile(r"\w+")  # kaynakta da ayni yazilan adlar/sayilar ('Heuvel')

Rows = list[tuple[dict[str, Any], "Snapshot | None"]]


class CheckError(Exception):
    """Kullanim veya yapi hatasi (cikis kodu 2)."""


@dataclass(frozen=True)
class Snapshot:
    snapshot_id: str
    url: str
    final_url: str | None
    status: int | None
    state: str
    text: str
    fetched_at: str | None


@dataclass(frozen=True)
class SnapshotIndex:
    fmt: str
    by_key: Mapping[str, Snapshot]
    skipped: tuple[str, ...] = ()


def _repair_run(run: str) -> str:
    for encoding in ("cp1252", "latin-1"):
        try:
            return run.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
    return run


def fix_mojibake(text: str) -> str:
    """UTF-8'in cp1252/latin-1 diye okunmasiyla bozulmus parcalari onarir ('Ã©' -> 'é'); saglam metne dokunmaz."""
    return MOJIBAKE_RUN.sub(lambda m: _repair_run(m.group(0)), text)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", fix_mojibake(text)).replace("­", "")
    return re.sub(r"\s+", " ", DASHES.sub("-", text)).strip()


def strip_header(raw: str) -> tuple[str, dict[str, str]]:
    """qwen .txt basligini (URL:/FETCHED:/TITLE:) govdeden ayirir."""
    lines, header, index = raw.splitlines(), {}, 0
    while index < len(lines) and (m := HEADER_LINE.match(lines[index])):
        header[m.group(1).upper()] = m.group(2).strip()
        index += 1
    return "\n".join(lines[index:]), header


def url_key(url: str) -> str:
    try:
        parts = urlsplit(str(url).strip())
    except ValueError:
        return str(url).strip().lower()
    query = f"?{parts.query}" if parts.query else ""
    return f"{(parts.hostname or '').lower().removeprefix('www.')}{parts.path.rstrip('/')}{query}"


def _numeric_rx(value: Mapping[str, Any]) -> tuple[str, str] | None:
    number, kind, unit = value.get("value"), value["kind"], UNIT_WORDS.get(str(value.get("unit")), "")
    if not isinstance(number, (int, float)) or isinstance(number, bool) or (kind == "duration" and not unit):
        return None
    num, scale = number_regex(number), value.get("scale")
    if isinstance(scale, int) and scale in SCALE_WORDS:  # '€1,5 milyon' -> '1.500.000' ya da '1,5 miljoen'
        num = rf"(?:{num}|{number_regex(round(number / scale, 6))}\s?{SCALE_WORDS[scale]})"
    words = NUMBER_WORDS.get(number, ()) if kind in WORDED_KINDS else ()  # 'number' duzeyi yalniz rakam: kelime kanit degil
    spelled, prefixed = (rf"(?:{num}|{words_rx(ws)})" if ws else num for ws in (words, [w for w in words if w not in ARTICLES]))
    return NUMERIC_TEMPLATES[kind].format(n=spelled, d=num, w=prefixed, unit=unit, **TEMPLATE_PARTS), num


def _weekday_rx(value: Mapping[str, Any]) -> tuple[str, str | None] | None:
    day = str(value.get("value"))
    if day not in DAY_NAMES:
        return None
    return (ordinal_day_rx(day, value["ordinal"]), day_rx(day)) if value.get("ordinal") in ORDINAL_WORDS else (day_rx(day), None)


def _time_rx(value: Mapping[str, Any]) -> tuple[str, None] | None:
    """24 saat ('18.00', '18:00', '18 uur') + 12 saat ('6 pm', '6:00 p.m.'; 00:30 = '12:30 AM', 12:00 = '12 pm')."""
    m = re.fullmatch(r"(\d{1,2}):(\d{2})", str(value.get("value", "")))
    if m is None:
        return None
    hour, minute, lead = int(m.group(1)), m.group(2), r"(?<![\d.,:])0?"
    clash = AMPM["pm"] if 0 < hour < 12 else AMPM["am"] if hour == 12 else None  # '10:00 pm' = 22:00, '12:30 am' = 00:30
    parts = [rf"{lead}{hour}[:.]{minute}(?!\d)" + (rf"(?!\s?{clash})" if clash else "")]
    if minute == "00":
        parts.append(rf"{lead}{hour}\s?(?:uur|u|h)(?!\w)")
    minutes = rf"(?:[:.]{minute})?" if minute == "00" else rf"[:.]{minute}"  # '6 pm' 18:00'dir, 18:30 degil
    if hour < 24:  # elle yazilmis '24:00' icin 12 saat bicimi yok
        parts.append(rf"{lead}{hour % 12 or 12}{minutes}\s?{AMPM['pm' if hour >= 12 else 'am']}")
    return "|".join([*parts, *CLOCK_WORDS.get((hour, minute), ())]), None


def _phone_rx(value: Mapping[str, Any]) -> tuple[str, None] | None:
    digits = re.sub(r"\D", "", str(value.get("value", "")))
    if len(digits) < 3:
        return None
    sep, national = r"(?:\s?[-./]?\s?)", digits.startswith("0") and len(digits) >= 9
    prefix, rest = (r"(?:(?:\+|00)\s?31\s*(?:\(0\)\s*)?|0)", digits[1:]) if national else ("", digits)
    return rf"(?<![\d+]){prefix}{sep.join(rest)}(?!\d)", None


def _date_rx(value: Mapping[str, Any]) -> tuple[str, None] | None:
    day, month = value.get("day"), value.get("month")
    if not isinstance(day, int) or not isinstance(month, int) or not 1 <= month <= 12:
        return None
    names = _alts(MONTH_NAMES[month - 1])
    return (rf"(?<![\d.,])0?{day}(?:e|ste|de|st|nd|rd|th)?\.?\s{names}\.?(?!\w)|\b{names}\.?\s0?{day}(?:st|nd|rd|th)?(?!\d)"
            rf"|(?<![\d.,])0?{day}[-/]0?{month}(?:[-/]\d{{2,4}})?(?!\d)"), None


PATTERN_BUILDERS = {**{kind: _numeric_rx for kind in NUMERIC_TEMPLATES},
                    "weekday": _weekday_rx, "time": _time_rx, "phone": _phone_rx, "date": _date_rx}


@lru_cache(maxsize=4096)
def _compiled(value_json: str) -> tuple[re.Pattern | None, re.Pattern | None]:
    value = json.loads(value_json)
    builder = PATTERN_BUILDERS.get(value.get("kind"))
    built = builder(value) if builder else None
    return (None, None) if built is None else tuple(re.compile(rx, re.IGNORECASE) if rx else None for rx in built)


def _snippet(text: str, m: re.Match) -> str:
    start, end = max(0, m.start() - SNIPPET_WIDTH), min(len(text), m.end() + SNIPPET_WIDTH)
    return ("…" if start else "") + text[start:end] + ("…" if end < len(text) else "")


def _best_match(rx: re.Pattern, text: str, anchors: tuple[frozenset[str], ...]) -> re.Match | None:
    """Ilk eslesme; anchors varsa alintisinda sirayla her kumeden en cok gecen eslesme (esitlikte ilki, MAX_MATCHES aday)."""
    def hits(m: re.Match) -> tuple[int, ...]:
        words = set(WORD.findall(_snippet(text, m).lower()))
        return tuple(len(group & words) for group in anchors)
    return max(islice(rx.finditer(text), MAX_MATCHES if any(anchors) else 1), key=hits, default=None)


def _claim_anchors(claim: Mapping[str, Any]) -> tuple[frozenset[str], frozenset[str]]:
    """(kart parcasinin sayi/adlari, cumlenin geri kalan ozel adlari/sayilari): '4-11 yaş' -> 4, 11; 'Heuvel ... 04:30'."""
    own, sentence = ({t.lower() for t in ANCHOR.findall(str(claim.get(key) or ""))} for key in ("text", "sentence"))
    return frozenset(own), frozenset(sentence - own)


def match_value(value: Mapping[str, Any], text: str, anchors: tuple[frozenset[str], ...] = ()) -> tuple[str | None, str | None]:
    """(duzey, alinti): 'unit' (sayi+birim) > 'number' (yalniz sayi) > None."""
    unit_rx, bare_rx = _compiled(json.dumps(value, sort_keys=True, ensure_ascii=False))
    for level, rx in (("unit", unit_rx), ("number", bare_rx)):
        if rx is not None and (m := _best_match(rx, text, anchors)):
            return level, _snippet(text, m)
    return None, None


def _state(status: Any, error: Any, text: str | None, min_chars: int, thin_flag: Any) -> str:
    if error and not status:
        return "fetch_error"
    if isinstance(status, int) and status >= 400:
        return "http_error"
    return "no_text" if text is None else "thin" if thin_flag is True or len(text) < min_chars else "ok"


def _snapshot(sid: str, meta: Mapping[str, Any], raw: str | None, min_chars: int) -> Snapshot:
    body, header = strip_header(raw) if raw is not None else ("", {})
    text = normalize_text(body) if raw is not None else None
    status, dates = meta.get("status", meta.get("http_status")), [meta.get(k) for k in ("fetched_at", "fetched_on", "checked_on")]
    return Snapshot(snapshot_id=sid, url=str(meta["url"]), final_url=meta.get("final_url"), status=status,
                    state=_state(status, meta.get("error"), text, min_chars, meta.get("thin")), text=text or "",
                    fetched_at=next(filter(None, dates), header.get("FETCHED")))


def _read_text(path: Path | None) -> str | None:
    return path.read_text(encoding="utf-8", errors="replace") if path is not None and path.is_file() else None


def _qwen_items(root: Path) -> Iterator[tuple[str, Any, str | None]]:
    for meta_path in sorted(root.glob("*.json")):
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            meta = None  # bozuk meta: atlanan listesine girer
        yield meta_path.name, meta, _read_text(meta_path.with_suffix(".txt"))


def _toolkit_items(root: Path) -> Iterator[tuple[str, Any, str | None]]:
    for number, line in enumerate((root / "index.jsonl").read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            meta = json.loads(line)
        except ValueError as exc:
            raise CheckError(f"index.jsonl:{number}: gecersiz JSON ({exc})") from exc
        try:
            path = common.safe_relpath(root, str(meta["text_file"])) if isinstance(meta, dict) and meta.get("text_file") else None
        except ValueError:
            path = None  # paket kokunden cikan yol okunmaz -> no_text
        sid = str(meta.get("id") or meta.get("text_file") or f"index.jsonl:{number}") if isinstance(meta, dict) else str(number)
        yield sid, meta, _read_text(path)


def detect_format(root: Path) -> str:
    if (root / "index.jsonl").is_file():
        return "toolkit"
    if any(root.glob("*.json")):
        return "qwen-cache"
    raise CheckError(f"snapshot bicimi taninmadi (index.jsonl ya da *.json yok): {root}")


def load_snapshots(root: Path, fmt: str | None = None, min_chars: int = DEFAULT_MIN_CHARS) -> SnapshotIndex:
    """Anahtar cakisirsa: url > final_url, sonra daha iyi durum, sonra kimlik sirasi (belirlenimci)."""
    root = Path(root)
    if not root.is_dir():
        raise CheckError(f"snapshot klasoru yok: {root}")
    fmt = fmt or detect_format(root)
    items = list(_toolkit_items(root) if fmt == "toolkit" else _qwen_items(root))
    usable = [(sid, meta, raw) for sid, meta, raw in items if isinstance(meta, dict) and meta.get("url")]
    snapshots = [_snapshot(sid.removesuffix(".json"), meta, raw, min_chars) for sid, meta, raw in usable]
    candidates = [(url_key(url), prio, STATE_RANK[s.state], s.snapshot_id, s)
                  for s in snapshots for prio, url in enumerate((s.url, s.final_url)) if url]
    best: dict[str, Snapshot] = {}
    for key, *_rank, snap in sorted(candidates, key=lambda c: c[:4]):
        best.setdefault(key, snap)
    skipped = tuple(sorted(sid for sid, meta, _ in items if not (isinstance(meta, dict) and meta.get("url"))))
    return SnapshotIndex(fmt=fmt, by_key=best, skipped=skipped)


def find_snapshot(index: SnapshotIndex, url: str | None) -> Snapshot | None:
    return index.by_key.get(url_key(url)) if url else None


def _source_rows(claim: Mapping[str, Any], index: SnapshotIndex) -> Rows:
    rows: Rows = []
    for src in claim.get("sources") or []:
        url = src.get("url")
        snap = find_snapshot(index, url)
        rows.append(({"source_id": src.get("source_id"), "url": url, "homepage": bool(url) and is_homepage(url),
                      "snapshot_id": snap.snapshot_id if snap else None, "chars": len(snap.text) if snap else 0,
                      "snapshot_state": snap.state if snap else ("not_found" if url else "no_url")}, snap))
    return rows


def _value_hit(index: int, value: Mapping[str, Any], rows: Rows, anchors: tuple) -> tuple[str | None, dict[str, Any] | None]:
    """En iyi duzey: ilk 'unit' eslesmesi, yoksa ilk 'number' eslesmesi."""
    best: tuple[str | None, dict[str, Any] | None] = (None, None)
    for view, snap in rows:
        if snap is None or snap.state not in SEARCHABLE:
            continue
        level, snippet = match_value(value, snap.text, anchors)
        hit = {"value_index": index, "source_id": view["source_id"], "url": view["url"], "snapshot_id": snap.snapshot_id,
               "level": level, "snippet": snippet, "fetched_at": snap.fetched_at}
        if level == "unit":
            return level, hit
        if level == "number" and best[0] is None:
            best = (level, hit)
    return best


def _classify(rows: Rows, levels: list[str | None], mode: str) -> str:
    cited = [view for view, _ in rows if view["url"]]
    if not cited:
        return "no_source"
    if all(view["homepage"] for view in cited):
        return "homepage_only_source"
    accepted = {"unit"} if mode == "unit" else {"unit", "number"}
    if levels and all(level in accepted for level in levels):
        return "supported"
    return "not_in_source" if any(snap is not None and snap.state == "ok" for _, snap in rows) else "no_snapshot"


def _uncertainty(result: str, rows: Rows, levels: list[str | None]) -> str:
    cited = [(view, snap) for view, snap in rows if view["url"]]
    if not cited:
        return "kartta çözülebilen kaynak URL'si yok"
    full = sum(1 for _, snap in cited if snap is not None and snap.state == "ok")
    parts = [f"kaynakların {full}/{len(cited)} tanesi tam metinle denetlendi"]
    parts += ["anasayfa kaynak var"] if any(view["homepage"] for view, _ in cited) else []
    parts += ["sayı birimsiz geçiyor (birim eşleşmedi)"] if "number" in levels and result != "supported" else []
    parts += ["yalnız tutarlılık; doğruluk/güncellik/statü ayrıca doğrulanmalı"] if result == "supported" else []
    return "; ".join(parts)


def check_claim(claim: Mapping[str, Any], index: SnapshotIndex, mode: str = "unit") -> dict[str, Any]:
    rows, anchors = _source_rows(claim, index), _claim_anchors(claim)
    hits = [_value_hit(i, value, rows, anchors) for i, value in enumerate(claim.get("values") or [])]
    levels, evidence = [level for level, _ in hits], [hit for _, hit in hits if hit is not None]
    result = _classify(rows, levels, mode)
    uncertainty = _uncertainty(result, rows, levels)
    searchable = [snap for _, snap in rows if snap is not None and snap.state in SEARCHABLE]
    checked = evidence[0]["fetched_at"] if evidence else (searchable[0].fetched_at if searchable else None)
    record = {"claim_id": claim.get("claim_id"), "entry_id": claim.get("entry_id"),
              "Excel_satırı": f"{claim.get('sheet')}!{claim.get('_row')}", "iddia": claim.get("sentence"),
              "ülke_şehir_statü": None, "dönem": None, "resmî_URL": [view["url"] for view, _ in rows if view["url"]],
              "kaynak_bölümü": evidence[0]["snippet"] if evidence else None, "yayın_yürürlük_tarihleri": None,
              "kontrol_tarihi": checked, "hesap_varsa_girdiler": None, "sonuç": result, "belirsizlik": uncertainty}
    keep = ("claim_id", "entry_id", "sheet", "_row", "field", "kind", "text", "sentence")
    return {**{k: claim.get(k) for k in keep}, "values": [dict(v) for v in claim.get("values") or []], "result": result,
            "value_levels": levels, "sources": [view for view, _ in rows], "evidence": evidence,
            "uncertainty": uncertainty, "claim_record": record}


def _summary(results: list[dict[str, Any]], mode: str) -> dict[str, Any]:
    by_kind: dict[str, Counter] = {}
    for res in results:
        by_kind.setdefault(str(res["kind"]), Counter())[res["result"]] += 1  # str: kind'siz satir siralamayi bozmaz
    states = {src["url"]: src["snapshot_state"] for res in results for src in res["sources"] if src["url"]}
    return {"claims": len(results), "entries": len({r["entry_id"] for r in results}), "mode": mode,
            "by_result": {name: sum(1 for r in results if r["result"] == name) for name in RESULTS},
            "by_kind": {kind: dict(sorted(c.items())) for kind, c in sorted(by_kind.items())},
            "number_only_hits": sum(1 for r in results
                                    if r["result"] == "not_in_source" and r["value_levels"] and None not in r["value_levels"]),
            "source_states": dict(sorted(Counter(states.values()).items()))}


def check_claims(claims: Iterable[Mapping[str, Any]], index: SnapshotIndex, mode: str = "unit") -> dict[str, Any]:
    results = [check_claim(claim, index, mode) for claim in claims]
    return {"note": NOTE, "summary": _summary(results, mode), "results": results}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Iddia degerlerini kaynak snapshot metninde arar (tutarlilik, dogruluk degil).")
    parser.add_argument("--claims", type=Path, required=True)
    parser.add_argument("--snapshots", type=Path, required=True)
    parser.add_argument("--snapshot-format", choices=("toolkit", "qwen-cache"), default=None)
    parser.add_argument("--mode", choices=("unit", "number"), default="unit", help="unit: sayi+birim sart; number: sayi yeter")
    parser.add_argument("--min-chars", type=int, default=DEFAULT_MIN_CHARS, help="bundan kisa metin 'thin' sayilir")
    parser.add_argument("--out", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    try:
        index = load_snapshots(args.snapshots, args.snapshot_format, args.min_chars)
        report = check_claims(read_claims(args.claims), index, args.mode)
        report["summary"] = {**report["summary"], "snapshot_format": index.fmt, "snapshots_indexed": len(index.by_key),
                             "snapshots_skipped": list(index.skipped)}
        common.write_json(args.out, report)
    except (CheckError, ClaimError, OSError, UnicodeDecodeError) as exc:  # UTF-8 olmayan index.jsonl de yapi hatasi
        common.emit({"error": str(exc)})
        return common.EXIT_USAGE
    common.emit({**report["summary"], "out": str(args.out)})
    return common.EXIT_OK if all(r["result"] == "supported" for r in report["results"]) else common.EXIT_FINDINGS


if __name__ == "__main__":
    sys.exit(main())
