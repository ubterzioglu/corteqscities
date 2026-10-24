"""Wikidata SPARQL: bir yonetim biriminin (--qid) sinirlarindaki koordinatli ogeler = mekan aday havuzu (A6; pilot: wikidata_aday.py).

Kullanim: wikidata_places.py --qid Q9832 --lang nl --out <is>/mekan/wikidata_aday.jsonl [--raw <out>.raw.json]
                              [--refresh]
--lang zorunlu (yerel dil: ad, ilce etiketi ve <lang>wiki; sabit varsayilan baska ulkede sessizce yanlis dil verirdi).
Tek sorgu (P131+ ile alt birimler dahil; kapanmis ogeler ve P5817=yikilmis haric), aciklayici User-Agent,
429/503'te Retry-After (en cok 30 sn) ile en cok 3 deneme. Ham yanit --raw'a yazilir (varsayilan: ciktinin yanina
.raw.json); ikinci calisma ag kullanmaz. Onbellek sorguya baglidir: yanina <raw>.meta.json {qid, lang, query_sha256}
yazilir; kaydi olmayan, bozuk ya da --qid/--lang/sorgu metniyle uyusmayan onbellek 'cache_mismatch' bulgusudur (eski
sehrin sonucu yeni qid adina donmez); --refresh ile yeniden sorgulanir.
Cikti satiri: {qid, name (<lang> etiketi, yoksa en), name_en, lat, lon, types, district, website, has_image,
commons_category, <lang>wiki}; ada gore sirali (--lang nl ile pilotla bayt bayt ayni). Koordinati okunamayan satir
(or. baska gok cismi) atlanir ve sayilir.
stdout tek satir JSON; cikis 0 / 1 (sorgu basarisiz, onbellek uyusmuyor/bozuk ya da sonuc yok) / 2 kullanim
(yazilamayan cikti dahil).
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import string
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "CorteqsCityToolkit/0.1 (content research; https://www.mediawiki.org/wiki/API:Etiquette)"
TIMEOUT_SECONDS = 90
MAX_ATTEMPTS = 3
RETRY_CAP_SECONDS = 30
RETRY_STATUSES = (429, 503)
QID_RE = re.compile(r"^Q[1-9][0-9]*\Z")
LANG_RE = re.compile(r"^[a-z]{2,3}\Z")
POINT_RE = re.compile(r"^Point\(\s*([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s+([-+]?[0-9.]+(?:[eE][-+]?[0-9]+)?)\s*\)\Z")
QUERY = string.Template("""
SELECT ?item $labels ?coord ?site ?image ?cat ?${lang}wiki
       (GROUP_CONCAT(DISTINCT ?typeLabel; separator="|") AS ?types)
       (SAMPLE(?districtLabel) AS ?district) WHERE {
  ?item wdt:P131+ wd:$qid ; wdt:P625 ?coord .
  FILTER NOT EXISTS { ?item wdt:P576 ?dissolved }
  FILTER NOT EXISTS { ?item wdt:P5817 wd:Q56556915 }
  OPTIONAL { ?item rdfs:label ?$lang FILTER(LANG(?$lang)="$lang") }
  OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en)="en") }
  OPTIONAL { ?item wdt:P856 ?site }
  OPTIONAL { ?item wdt:P18 ?image }
  OPTIONAL { ?item wdt:P373 ?cat }
  OPTIONAL { ?${lang}wiki schema:about ?item ; schema:isPartOf <https://$lang.wikipedia.org/> }
  OPTIONAL { ?item wdt:P31 ?type . ?type rdfs:label ?typeLabel FILTER(LANG(?typeLabel)="en") }
  OPTIONAL { ?item wdt:P131 ?d . ?d rdfs:label ?districtLabel FILTER(LANG(?districtLabel)="$lang") }
}
GROUP BY ?item $labels ?coord ?site ?image ?cat ?${lang}wiki
""")

Response = tuple[int, dict[str, str], bytes]
Transport = Callable[[str, dict[str, str], float], Response]


class TransportError(Exception):
    """Ag/baglanti hatasi (HTTP durumu yok)."""


class QueryError(Exception):
    """Sorgu basarisiz: HTTP hatasi, deneme hakki bitti ya da yanit SPARQL JSON degil."""


class UsageError(Exception):
    """Gecersiz arguman (cikis 2)."""


def urllib_transport(url: str, headers: dict[str, str], timeout: float) -> Response:
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


def build_query(qid: str, lang: str) -> str:
    """--lang nl icin pilot sorgusunun aynisi (degisken adlari ?nl, ?nlwiki)."""
    labels = " ".join(f"?{name}" for name in dict.fromkeys((lang, "en")))
    return QUERY.substitute(qid=qid, lang=lang, labels=labels)


def _retry_after(headers: dict[str, str], attempt: int) -> float:
    raw = next((str(v) for k, v in headers.items() if k.lower() == "retry-after"), "").strip()
    return float(int(raw)) if raw.isdigit() else float(attempt * 5)


def parse_result(body: bytes) -> dict[str, Any]:
    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise QueryError(f"yanit JSON degil ({type(error).__name__})") from error
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, dict) or not isinstance(results.get("bindings"), list):
        raise QueryError("yanit SPARQL sonucu degil (results.bindings yok)")
    return data


def fetch(transport: Transport, sleep: Callable[[float], None], query: str) -> tuple[dict[str, Any], int]:
    """(SPARQL sonucu, istek sayisi); 429/503'te Retry-After <= 30 sn ile en cok 3 deneme."""
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    headers = {"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"}
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            status, response_headers, body = transport(url, headers, TIMEOUT_SECONDS)
        except TransportError as error:
            raise QueryError(f"ag: {error}") from error
        if status == 200:
            return parse_result(body), attempt
        if status not in RETRY_STATUSES or attempt == MAX_ATTEMPTS:
            raise QueryError(f"HTTP {status} ({attempt} istek)")
        wait = _retry_after(response_headers, attempt)
        if wait > RETRY_CAP_SECONDS:
            raise QueryError(f"sunucu {wait:.0f} sn bekletmek istiyor (> {RETRY_CAP_SECONDS}); sonra deneyin")
        sleep(wait)
    raise AssertionError("ulasilamaz")  # pragma: no cover


def parse_point(value: str) -> tuple[float, float]:
    """WKT 'Point(boylam enlem)' -> (enlem, boylam); baska gok cismi ya da bozuk deger ValueError."""
    match = POINT_RE.match(value)
    if not match:
        raise ValueError(f"okunamayan koordinat: {value[:60]}")
    return float(match.group(2)), float(match.group(1))


def to_rows(data: dict[str, Any], lang: str) -> tuple[list[dict[str, Any]], int]:
    """(ada gore sirali satirlar, atlanan satir sayisi); alan sirasi pilotla ayni."""
    rows, bad = [], 0
    for binding in data["results"]["bindings"]:
        try:
            v = {k: b["value"] for k, b in binding.items()}
            lat, lon = parse_point(v["coord"])
            qid = v["item"].rsplit("/", 1)[1]
        except (KeyError, TypeError, ValueError, IndexError, AttributeError):
            bad += 1
            continue
        rows.append({"qid": qid, "name": str(v.get(lang) or v.get("en") or ""), "name_en": v.get("en", ""),
                     "lat": round(lat, 6), "lon": round(lon, 6), "types": v.get("types", ""),
                     "district": v.get("district", ""), "website": v.get("site", ""), "has_image": bool(v.get("image")),
                     "commons_category": v.get("cat", ""), f"{lang}wiki": v.get(f"{lang}wiki", "")})
    rows.sort(key=lambda r: r["name"].casefold())
    return rows, bad


def query_record(qid: str, lang: str, query: str) -> dict[str, str]:
    """Onbellegin hangi sorguya ait oldugu: qid, dil ve sorgu metninin ozeti (sablon degisirse de uyusmaz)."""
    return {"qid": qid, "lang": lang, "query_sha256": hashlib.sha256(query.encode("utf-8")).hexdigest()}


def read_record(path: Path) -> dict[str, Any] | None:
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):  # yok, bozuk ya da UTF-8 degil: sorgu bilinmiyor
        return None
    return record if isinstance(record, dict) else None


def cached_result(raw: Path, record_file: Path, expected: dict[str, str],
                  lang: str) -> tuple[dict[str, Any] | None, str | None, dict[str, Any] | None]:
    """(onbellekteki sonuc, sorun durumu, onbellegin sorgu kaydi). Sorgu kaydi yok/bozuk ya da qid, dil ya da sorgu
    metni uyusmuyorsa 'cache_mismatch': eski sehrin sonucu yeni qid adina sessizce donmez."""
    try:
        data = parse_result(raw.read_bytes())
    except (OSError, QueryError):
        return None, "cache_corrupt", None
    record = read_record(record_file)
    if record != expected:
        return None, "cache_mismatch", record
    head = data.get("head")
    names = head.get("vars") if isinstance(head, dict) else None
    if isinstance(names, list) and not {lang, f"{lang}wiki"} <= set(names):
        return None, "cache_mismatch", record
    return data, None, record


def write_cache(raw: Path, record_file: Path, data: dict[str, Any], record: dict[str, str]) -> None:
    """Once eski sorgu kaydi silinir: ham dosya yazilip kayit yazilamazsa onbellek dogrulanamaz kalir, yanlis
    sehre ait sayilmaz."""
    raw.parent.mkdir(parents=True, exist_ok=True)
    record_file.unlink(missing_ok=True)
    raw.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    record_file.write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Wikidata SPARQL mekan aday havuzu (koordinatli ogeler)")
    p.add_argument("--qid", required=True, help="sehrin Wikidata kimligi (or. Eindhoven Q9832)")
    p.add_argument("--out", required=True, type=Path, help="aday JSONL (or. <is>/mekan/wikidata_aday.jsonl)")
    p.add_argument("--lang", required=True, help="yerel dil kodu: ad, ilce etiketi ve <lang>wiki (or. nl, de)")
    p.add_argument("--raw", type=Path, help="ham SPARQL onbellegi (varsayilan <out>.raw.json; kaydi <raw>.meta.json)")
    p.add_argument("--refresh", action="store_true", help="onbellegi yok sayip yeniden sorgula")
    return p


def raw_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    """(ham onbellek, sorgu kaydi)."""
    raw = args.raw or args.out.with_suffix(".raw.json")
    return raw, raw.with_suffix(".meta.json")


def check_args(args: argparse.Namespace) -> str | None:
    if not QID_RE.match(args.qid):
        return "--qid 'Q' + sayi olmali (or. Q9832)"
    if not LANG_RE.match(args.lang):
        return "--lang kucuk harfli 2-3 harf olmali (or. nl, de)"
    raw, record_file = raw_paths(args)
    if raw.resolve() == args.out.resolve():
        return "--raw ile --out ayni dosya olamaz"
    if record_file.resolve() == args.out.resolve():
        return f"--out onbellek kaydiyla ({record_file.name}) ayni dosya olamaz"
    return None


def run(args: argparse.Namespace, transport: Transport, sleep: Callable[[float], None]) -> int:
    problem = check_args(args)
    if problem:
        raise UsageError(problem)
    raw, record_file = raw_paths(args)
    query = build_query(args.qid, args.lang)
    expected = query_record(args.qid, args.lang, query)
    base = {"qid": args.qid, "lang": args.lang, "out": str(args.out), "raw": str(raw)}
    requests_made = 0
    if raw.exists() and not args.refresh:
        data, status, cached = cached_result(raw, record_file, expected, args.lang)
        if data is None:
            emit({"status": status, **base, "cached": cached, "hint": "--refresh ile yeniden sorgulayin"})
            return EXIT_FINDINGS
    else:
        try:
            data, requests_made = fetch(transport, sleep, query)
        except QueryError as error:
            emit({"status": "fetch_failed", **base, "error": str(error)})
            return EXIT_FINDINGS
        write_cache(raw, record_file, data, expected)
    rows, bad = to_rows(data, args.lang)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    emit({"status": "ok" if rows else "empty", **base, "items": len(rows),
          "with_site": sum(1 for r in rows if r["website"]), "with_image": sum(1 for r in rows if r["has_image"]),
          "with_category": sum(1 for r in rows if r["commons_category"]), "bad_rows": bad,
          "duplicate_qids": sum(n - 1 for n in Counter(r["qid"] for r in rows).values() if n > 1),
          "from_cache": requests_made == 0, "requests_made": requests_made})
    return EXIT_OK if rows else EXIT_FINDINGS


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
