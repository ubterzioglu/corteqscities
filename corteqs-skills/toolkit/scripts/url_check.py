"""URL denetimi (K49 bicim, K50 fiili HTTP, K51 soft-404/anasayfa, K52 403/429/gecici, K56 geri dagitim).

Kullanim: url_check.py <xlsx> [--sheets Kaynaklar,Bağlantılar] [--cache-dir D] [--out url-checks.json] [--max-urls N]
Benzersiz URL'ler bir kez test edilir; sonuc bagli tum satirlara (sayfa!satir, kimlik) dagitilir.
Kesin bozuk = 404/410/soft_404; 'erisim teyidi acik' = 403/429/5xx/ag hatasi (bozuk SAYILMAZ).
URL kaydi denetim kilavuzu bolum 16 alanlarini tasir. Excel salt okunur; ag erisimi web_fetch uzerinden kibar yapilir.
"""
from __future__ import annotations

import argparse
import ipaddress
import re
import sys
import time
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import parse_qsl, urlsplit

import openpyxl

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, iter_records, setup_utf8, sha256_file, write_json
from web_fetch import PROBE_BODY_BYTES, FetchResult, Fetcher, Transport, request_url, urllib_transport, utc_today

DEFAULT_SHEETS = ("Kaynaklar", "Bağlantılar")
URL_RECORD_KEYS = ("ham_URL", "istek_URL", "bağlı_IDler", "Excel_satırları", "checked_on", "HTTP_durumu", "son_URL",
                   "sayfa_başlığı", "erişim_sonucu", "anlamsal_hedef_sonucu", "tekrar_kaydı", "açıklama")
ID_KEYS = ("source_id", "action_id", "field_id", "entry_id", "term_id", "route_id", "evidence_id", "photo_id", "city_id")
TEXT_SCAN_FIELDS = {"SayfaAlanları": ("value",)}
URL_IN_TEXT = re.compile(r"https?://[^\s\"'<>\\]+")

WORKING, BROKEN, OPEN, UNTESTED, INVALID = "çalışıyor", "bozuk", "erişim teyidi açık", "test edilmedi", "geçersiz"
VERDICTS = (WORKING, BROKEN, OPEN, UNTESTED, INVALID)
CLASS_VERDICT = {"ok_200": WORKING, "redirect_ok": WORKING, "not_found_404": BROKEN, "gone_410": BROKEN,
                 "soft_404": BROKEN, "forbidden_403": OPEN, "rate_limited_429": OPEN, "server_5xx": OPEN,
                 "network_error": OPEN, "intercepted": OPEN, "other_4xx": OPEN, "other_status": OPEN,
                 "not_tested": UNTESTED, "invalid_url": INVALID}
FLAGS = ("homepage_only", "wikipedia", "wikipedia_labeled_official", "redirected_to_homepage", "cross_host_redirect")
FINDING_FLAGS = ("homepage_only", "wikipedia_labeled_official", "redirected_to_homepage")
INFO_ISSUES = ("non_ascii", "tracking_param", "map_search")  # map_search: K55 insan kontrolu ister, kusur sayilmaz
ERROR_HINTS = {
    "tls": "TLS doğrulanamadı: sunucu ara sertifikayı göndermiyor olabilir (tarayıcı AIA ile tamamlayabilir); doğrulama kapatılmaz",
    "too_many_redirects": "yönlendirme döngüsü: site çerez bekliyor olabilir, araç çerez göndermez",
    "timeout": "20 sn içinde yanıt yok", "dns": "alan adı çözülemedi", "connection": "bağlantı kurulamadı veya koptu",
}
FATAL_ISSUES = ("bad_scheme", "no_host")

PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost", "127.0.0.1", "0.0.0.0"}
SESSION_KEY = re.compile(r"^(?:sid|session|sessionid|session_id|phpsessid|jsessionid|aspsessionid\w*|token|"
                         r"access_token|auth_token|id_token|auth|apikey|api_key|signature|sig|x-amz-\w+)$", re.I)
TRACKING_KEY = re.compile(r"^(?:utm_\w+|fbclid|gclid|msclkid|mc_cid|mc_eid|_ga)$", re.I)
SEARCH_SEGMENTS = {"search", "zoeken", "zoekresultaten", "suche", "recherche", "zoek"}
SEARCH_KEYS = {"q", "s", "query", "search", "zoekterm", "searchterm", "keyword"}
HOME_LANGS = "en|nl|de|fr|fy|tr|es|it|pt|pl|ar|ru|uk|zh|ja|ko"  # dil koku; '/ov', '/tv' gibi icerik yollari degil
HOME_PATH = re.compile(rf"/?(?:(?:{HOME_LANGS})(?:[-_][a-z]{{2}})?|(?:home|index)(?:\.(?:html?|php))?)?/?", re.I)
OFFICIAL_LABEL = re.compile(r"resm[iî]|official", re.I)
SOFT_404_PHRASES = ("not found", "niet gevonden", "pagina bestaat niet", "page does not exist", "seite nicht gefunden",
                    "sayfa bulunamadı", "kon niet worden gevonden")
TITLE_404 = re.compile(r"\b404\b")
BODY_404 = re.compile(r"\b(?:error|fout(?:melding|code)?)\s*:?\s*404\b", re.I)
BODY_WINDOW = 1500


# ---------------------------------------------------------------- Excel -> iliskiler

def _record_id(record: Mapping[str, Any]) -> Any:
    return next((record[k] for k in ID_KEYS if record.get(k)), None)


def _record_relations(sheet: str, record: Mapping[str, Any]) -> list[dict[str, Any]]:
    base = {"sheet": sheet, "row": record["_row"], "id": _record_id(record)}
    extras = {k: record[k] for k in ("label", "entry_id") if sheet == "Bağlantılar" and k in record}
    found: list[dict[str, Any]] = []
    for key, value in record.items():
        if key.startswith("_") or not isinstance(value, str) or not value.strip():
            continue
        if key == "url" or key.endswith("_url"):
            found.append({**base, "field": key, "url": value, **extras})
        elif key in TEXT_SCAN_FIELDS.get(sheet, ()):
            found += [{**base, "field": key, "url": url, **extras} for url in dict.fromkeys(URL_IN_TEXT.findall(value))]
    return found


def collect_relations(workbook: Path, sheets: Iterable[str]) -> list[dict[str, Any]]:
    """Her URL hucresi bir iliski: {sheet, row, id, field, url, [label, entry_id]}. Excel salt okunur."""
    names = list(sheets)
    wb = openpyxl.load_workbook(workbook, data_only=False)
    try:
        missing = [name for name in names if name not in wb.sheetnames]
        if missing:
            raise ValueError(f"sayfa bulunamadi: {', '.join(missing)}")
        return [rel for name in names for record in iter_records(wb[name]) for rel in _record_relations(name, record)]
    finally:
        wb.close()


# ---------------------------------------------------------------- K49 bicim

def _query_keys(query: str) -> list[str]:
    return [k for k, _ in parse_qsl(query, keep_blank_values=True)]


def _is_search(path: str, keys: list[str]) -> bool:
    segments = {s.lower() for s in path.split("/") if s}
    return bool(segments & SEARCH_SEGMENTS) or any(k.lower() in SEARCH_KEYS for k in keys)


def _is_map(host: str, path: str) -> bool:
    bare = host.removeprefix("www.")
    return (bare.startswith("maps.") or bare.endswith("openstreetmap.org")
            or ((bare.startswith("google.") or bare == "bing.com") and path.startswith("/maps")))


def format_issues(url: str) -> list[str]:
    """Bicim sorunlari (sirali). non_ascii ve tracking_param bilgi amaclidir; digerleri bulgudur."""
    text = url.strip()
    try:
        parts = urlsplit(text)
        scheme, host = parts.scheme.lower(), (parts.hostname or "").lower()
    except ValueError:
        return ["bad_scheme"]
    if scheme not in ("http", "https"):
        return ["bad_scheme"]
    if not host:
        return ["no_host"]
    keys = _query_keys(parts.query)
    search, on_map = _is_search(parts.path, keys), _is_map(host, parts.path)
    checks = [
        ("whitespace", url != text or any(ch.isspace() for ch in text)),
        ("not_https", scheme == "http"),
        ("credentials", "@" in parts.netloc),
        ("placeholder", host.removeprefix("www.") in PLACEHOLDER_HOSTS),
        ("session_param", any(SESSION_KEY.match(k) for k in keys) or ";jsessionid=" in parts.path.lower()),
        ("tracking_param", any(TRACKING_KEY.match(k) for k in keys)),
        ("search_results", search and not on_map),
        ("map_search", search and on_map),
        ("non_ascii", any(ord(ch) > 127 for ch in text)),
    ]
    return [name for name, hit in checks if hit]


def is_homepage(url: str) -> bool:
    """Yalniz alan adi: yol bos, '/', dil koku ('/en', '/nl', '/nl-nl') veya '/home', '/index.html'; sorgu yok."""
    try:
        parts = urlsplit(url.strip())
    except ValueError:
        return False
    return bool(parts.hostname) and not parts.query and HOME_PATH.fullmatch(parts.path) is not None


def _host(url: str) -> str:
    try:
        return (urlsplit(url.strip()).hostname or "").lower()
    except ValueError:
        return ""


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def is_wikipedia(url: str) -> bool:
    host = _host(url)
    return host == "wikipedia.org" or host.endswith(".wikipedia.org")


# ---------------------------------------------------------------- K50-K52 siniflama

def soft_404_signal(title: str | None, text: str | None) -> str | None:
    """200 yanitinda 'bulunamadi' isareti: baslikta ifade veya 404; govdenin basinda ifade veya 'error 404'."""
    head = (title or "").lower()
    body = (text or "")[:BODY_WINDOW].lower()
    for phrase in SOFT_404_PHRASES:
        if phrase in head:
            return f"başlık: '{phrase}'"
    if TITLE_404.search(head):
        return "başlık: '404'"
    for phrase in SOFT_404_PHRASES:
        if phrase in body:
            return f"gövde: '{phrase}'"
    match = BODY_404.search(body)
    return f"gövde: '{match.group(0)}'" if match else None


def page_signals(result: FetchResult) -> tuple[str | None, str | None]:
    """(sayfa basligi, soft-404 isareti); yalniz govdeli 2xx HTML icin."""
    from fetch_snapshot import decode_body, extract_page, is_html  # gec ice aktarma: fetch_snapshot url_check'i kullanir

    if not result.body or not (200 <= (result.status or 0) < 300) or not is_html(result.content_type, result.body):
        return None, None
    title, text = extract_page(decode_body(result.body, result.content_type))
    return title or None, soft_404_signal(title, text)


def classify(result: FetchResult, soft_signal: str | None = None) -> str:
    if result.error_kind in ("blocked_scheme", "invalid_url"):
        return "invalid_url"
    if result.error_kind:
        return "network_error"
    if result.redirected and _is_ip(_host(result.final_url)) and not _is_ip(_host(result.url)):
        return "intercepted"  # alan adindan ciplak IP'ye yonlenme: ag/proxy engel sayfasi olasi (K52)
    code = result.status or 0
    if 200 <= code < 300:
        return "soft_404" if soft_signal else ("redirect_ok" if result.redirected else "ok_200")
    named = {404: "not_found_404", 410: "gone_410", 403: "forbidden_403", 429: "rate_limited_429"}
    if code in named:
        return named[code]
    if code >= 500:
        return "server_5xx"
    return "other_4xx" if 400 <= code < 500 else "other_status"


def _same_site(a: str, b: str) -> bool:
    return _host(a).removeprefix("www.") == _host(b).removeprefix("www.")


def url_flags(url: str, result: FetchResult | None, relations: list[Mapping[str, Any]]) -> list[str]:
    wiki = is_wikipedia(url)
    labeled = wiki and any(OFFICIAL_LABEL.search(str(r.get("label", ""))) for r in relations)
    landed = result is not None and result.error_kind is None and 200 <= (result.status or 0) < 300 and result.redirected
    hits = {
        "homepage_only": is_homepage(url),
        "wikipedia": wiki,
        "wikipedia_labeled_official": labeled,
        "redirected_to_homepage": landed and not is_homepage(url) and is_homepage(result.final_url),
        "cross_host_redirect": landed and not _same_site(url, result.final_url),
    }
    return [flag for flag in FLAGS if hits[flag]]


# ---------------------------------------------------------------- URL kaydi (bolum 16)

def _safe_request_url(url: str) -> str | None:
    try:
        return request_url(url)
    except (ValueError, UnicodeError):
        return None


def _note(result: FetchResult | None, issues: list[str], soft: str | None) -> str:
    parts = [f"biçim: {', '.join(issues)}"] if issues else []
    if result is None:
        parts.append("test edilmedi (--max-urls kapsamı dışında veya geçersiz URL)")
    else:
        if result.head_status is not None:
            parts.append(f"HEAD {result.head_status} reddetti; sınırlı GET kullanıldı")
        if result.error:
            hint = ERROR_HINTS.get(result.error_kind or "")
            parts.append(f"{result.error_kind}: {result.error}" + (f" ({hint})" if hint else ""))
        if classify(result) == "intercepted":
            parts.append(f"son URL çıplak IP adresi ({result.final_url}); ağ/proxy engel sayfası olası, erişim teyit edilemedi")
        if soft:
            parts.append(f"soft-404 işareti {soft}")
        if result.truncated:
            parts.append("gövde sınırda kesildi")
    return "; ".join(parts)


def _semantic(cls: str, flags: list[str], soft: str | None) -> str:
    if cls == "soft_404":
        return f"soft_404 ({soft})"
    return "uyarı: " + ", ".join(flags) if flags else "otomatik sinyal yok (işlem/iddia eşleşmesi insan incelemesi ister)"


def build_url_record(url: str, relations: list[Mapping[str, Any]], result: FetchResult | None) -> dict[str, Any]:
    issues = format_issues(url)
    title, soft = page_signals(result) if result is not None else (None, None)
    cls = classify(result, soft) if result is not None else ("invalid_url" if set(issues) & set(FATAL_ISSUES) else "not_tested")
    flags = url_flags(url, result, relations)
    record = {
        "ham_URL": url, "istek_URL": (result.request_url or None) if result else _safe_request_url(url),
        "bağlı_IDler": sorted({str(r["id"]) for r in relations if r.get("id") is not None}),
        "Excel_satırları": sorted({f"{r['sheet']}!{r['row']}" for r in relations}),
        "checked_on": result.fetched_on if result else None, "HTTP_durumu": result.status if result else None,
        "son_URL": result.final_url if result else None, "sayfa_başlığı": title, "erişim_sonucu": CLASS_VERDICT[cls],
        "anlamsal_hedef_sonucu": _semantic(cls, flags, soft), "tekrar_kaydı": list(result.retries) if result else [],
        "açıklama": _note(result, issues, soft),
    }
    extra = {"class": cls, "flags": flags, "format_issues": issues, "domain": _host(url),
             "error_kind": result.error_kind if result else None, "method": result.method if result else None,
             "content_type": result.content_type if result else None,
             "redirect_chain": [{"url": h.url, "status": h.status, "location": h.location} for h in result.chain] if result else [],
             "relation_count": len(relations)}
    return {**record, **extra}


# ---------------------------------------------------------------- ozet (K56)

def _is_finding(record: Mapping[str, Any]) -> bool:
    return (record["erişim_sonucu"] != WORKING or any(f in FINDING_FLAGS for f in record["flags"])
            or any(i not in INFO_ISSUES for i in record["format_issues"]))


def summarize(records: list[dict[str, Any]], relations: list[dict[str, Any]]) -> dict[str, Any]:
    classes = Counter(r["class"] for r in records)
    by_relation = Counter(r["class"] for r in relations)
    tested = sum(1 for r in records if r["class"] not in ("not_tested", "invalid_url"))
    groups: dict[str, Counter] = {}
    for rec in records:
        if rec["erişim_sonucu"] in (BROKEN, OPEN, INVALID):
            groups.setdefault(rec["domain"], Counter())[rec["class"]] += 1
    relation_flags: dict[str, Counter] = {}
    for rel in relations:
        relation_flags.setdefault(rel["sheet"], Counter()).update(rel["flags"])
    return {
        "unique_urls": len(records), "relations": len(relations), "tested": tested, "coverage": f"{tested}/{len(records)}",
        "classes": {c: classes.get(c, 0) for c in CLASS_VERDICT},
        "relation_classes": {c: by_relation.get(c, 0) for c in CLASS_VERDICT},
        "verdicts": {v: sum(1 for r in records if r["erişim_sonucu"] == v) for v in VERDICTS},
        "flags": {f: sum(1 for r in records if f in r["flags"]) for f in FLAGS},
        "relation_flags": {s: dict(sorted(c.items())) for s, c in sorted(relation_flags.items())},
        "relations_by_sheet": dict(sorted(Counter(r["sheet"] for r in relations).items())),
        "format_issues": dict(sorted(Counter(i for r in records for i in r["format_issues"]).items())),
        "error_groups": {d: dict(sorted(c.items())) for d, c in sorted(groups.items(), key=lambda kv: (-sum(kv[1].values()), kv[0]))},
        "findings": sum(1 for r in records if _is_finding(r)),
    }


def relation_flags(relation: Mapping[str, Any], flags: list[str]) -> list[str]:
    """URL bayraklari satira iner; 'wikipedia_labeled_official' yalniz kendi etiketi resmi olan satirda kalir."""
    own_label = OFFICIAL_LABEL.search(str(relation.get("label") or ""))
    return [f for f in flags if f != "wikipedia_labeled_official" or own_label]


def check_urls(relations: list[dict[str, Any]], fetcher: Fetcher, max_urls: int | None, head_only: bool) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for rel in relations:
        grouped.setdefault(rel["url"], []).append(rel)
    fetchable = [u for u in grouped if not set(format_issues(u)) & set(FATAL_ISSUES)]
    selected = fetchable[:max_urls] if max_urls else fetchable
    results = fetcher.fetch_many(selected, mode="probe" if head_only else "get", body_limit=PROBE_BODY_BYTES)
    records = sorted((build_url_record(u, rels, results.get(u)) for u, rels in grouped.items()), key=lambda r: r["ham_URL"])
    by_url = {r["ham_URL"]: r for r in records}
    linked = [{**rel, "class": by_url[rel["url"]]["class"], "erişim_sonucu": by_url[rel["url"]]["erişim_sonucu"],
               "flags": relation_flags(rel, by_url[rel["url"]]["flags"])} for rel in relations]
    return {"summary": summarize(records, linked), "urls": records, "relations": linked}


# ---------------------------------------------------------------- CLI

def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Excel URL denetimi (bicim + fiili HTTP + soft-404 + geri dagitim)")
    p.add_argument("xlsx", type=Path)
    p.add_argument("--sheets", default=",".join(DEFAULT_SHEETS), help="virgulle ayrilmis sayfalar (Şehir, SayfaAlanları eklenebilir)")
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--out", type=Path, default=Path("url-checks.json"))
    p.add_argument("--max-urls", type=int)
    p.add_argument("--head-only", action="store_true", help="HEAD (reddedilirse sinirli GET); soft-404 icin govde okunmaz")
    p.add_argument("--retry-transient", action="store_true", help="onbellekteki 429/5xx/ag hatalarini yeniden dene")
    return p


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep, clock: Callable[[], str] = utc_today) -> int:
    setup_utf8()
    args = _parser().parse_args(argv)
    sheets = [s.strip() for s in args.sheets.split(",") if s.strip()]
    if args.max_urls is not None and args.max_urls < 1:
        print("HATA: --max-urls en az 1 olmali", file=sys.stderr)
        return EXIT_USAGE
    try:
        relations = collect_relations(args.xlsx, sheets)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE
    fetcher = Fetcher(transport, args.cache_dir or args.out.parent / ".url-cache", sleep=sleep, clock=clock,
                      refresh_transient=args.retry_transient)
    report = check_urls(relations, fetcher, args.max_urls, args.head_only)
    write_json(args.out, {"tool": "url_check", "workbook": str(args.xlsx), "workbook_sha256": sha256_file(args.xlsx),
                          "sheets": sheets, "mode": "head" if args.head_only else "get", **report})
    s = report["summary"]
    emit({"status": "findings" if s["findings"] else "ok", "unique_urls": s["unique_urls"], "relations": s["relations"],
          "tested": s["tested"], "classes": {k: v for k, v in s["classes"].items() if v}, "verdicts": s["verdicts"],
          "flags": s["flags"], "findings": s["findings"], "error_domains_top": dict(list(s["error_groups"].items())[:5]),
          "requests_made": fetcher.requests_made, "cache_hits": fetcher.cache_hits, "out": str(args.out)})
    return EXIT_FINDINGS if s["findings"] else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
