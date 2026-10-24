"""Ortak kibar HTTP katmani (stdlib urllib): url_check ve fetch_snapshot bunu paylasir.

Nezaket: aciklayici User-Agent, alan adi basina en fazla 2 / toplam en fazla 6 eszamanli istek, 429/503'te
Retry-After (en cok 30 sn, en cok 3 deneme), HEAD reddedilirse sinirli GET, yonlendirme zinciri elle izlenir ve
kaydedilir, 20 sn zaman asimi, en fazla 3 MB govde. Kimlik bilgisi, cerez veya Authorization gonderilmez.
Onbellek: URL'nin sha256'si ile <cache>/<sha>.json (+ .body). Testler sahte tasima katmani verir (ag yok).
"""
from __future__ import annotations

import datetime as _dt
import email.utils
import hashlib
import http.client
import json
import os
import socket
import ssl
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Mapping
from urllib.parse import quote, urljoin, urlsplit, urlunsplit

USER_AGENT = "CorteqsCityToolkit/0.1 (content QA; contact via project owner)"
PER_HOST_LIMIT = 2
TOTAL_LIMIT = 6
MAX_ATTEMPTS = 3
RETRY_CAP_SECONDS = 30
TIMEOUT_SECONDS = 20
MAX_BODY_BYTES = 3 * 1024 * 1024
PROBE_BODY_BYTES = 256 * 1024
MAX_REDIRECTS = 10
RETRY_STATUSES = (429, 503)
REDIRECT_STATUSES = (301, 302, 303, 307, 308)
LOCAL_ERRORS = ("blocked_scheme", "invalid_url")
HEAD_FALLBACK_ERRORS = ("connection", "protocol")
BASE_HEADERS = {"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml;q=0.9,*/*;q=0.8",
                "Accept-Encoding": "identity"}
KEPT_HEADERS = ("content-type", "content-length", "content-language", "last-modified", "retry-after", "location")
SAFE_PATH = "/%:@!$&'()*+,;=-._~"
SAFE_QUERY = SAFE_PATH + "?"


@dataclass(frozen=True)
class RawResponse:
    """Tek bir HTTP alisverisi (yonlendirme izlenmez)."""
    status: int
    headers: Mapping[str, str]
    body: bytes


class NetworkError(Exception):
    """Baglanti/zaman asimi/TLS/DNS hatasi; kind siniflamayi tasir."""

    def __init__(self, kind: str, message: str) -> None:
        super().__init__(message)
        self.kind = kind


Transport = Callable[[str, str, Mapping[str, str], float, int], RawResponse]


@dataclass(frozen=True)
class Hop:
    url: str
    status: int | None
    location: str | None = None


@dataclass(frozen=True)
class FetchResult:
    url: str
    request_url: str
    method: str
    status: int | None
    final_url: str
    chain: tuple[Hop, ...] = ()
    headers: Mapping[str, str] = field(default_factory=dict)
    body: bytes = b""
    truncated: bool = False
    body_limit: int = 0
    error_kind: str | None = None
    error: str | None = None
    attempts: int = 0
    retries: tuple[dict[str, Any], ...] = ()
    fetched_on: str = ""
    from_cache: bool = False
    head_status: int | None = None

    @property
    def redirected(self) -> bool:
        return len(self.chain) > 1

    @property
    def content_type(self) -> str:
        return str(self.headers.get("content-type", ""))

    @property
    def transient(self) -> bool:
        return self.error_kind is not None or self.status == 429 or (self.status or 0) >= 500

    def to_meta(self) -> dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if k not in ("body", "from_cache")}

    @classmethod
    def from_meta(cls, meta: Mapping[str, Any], body: bytes) -> "FetchResult":
        return cls(**{**meta, "body": body, "chain": tuple(Hop(**hop) for hop in meta.get("chain", ())),
                      "retries": tuple(dict(r) for r in meta.get("retries", ()))})


def utc_today() -> str:
    return _dt.datetime.now(_dt.timezone.utc).date().isoformat()


def request_url(url: str) -> str:
    """Istek URL'si: kimlik bilgisi ve parca atilir, alan adi IDNA, yol/sorgu yuzde-kodlanir. ValueError olabilir."""
    parts = urlsplit(url.strip())
    if not parts.hostname:
        raise ValueError(f"alan adi yok: {url!r}")
    host = parts.hostname.encode("idna").decode("ascii")
    if ":" in host:
        host = f"[{host}]"
    netloc = f"{host}:{parts.port}" if parts.port else host
    return urlunsplit((parts.scheme.lower(), netloc, quote(parts.path or "/", safe=SAFE_PATH),
                       quote(parts.query, safe=SAFE_QUERY), ""))


_ERROR_KINDS = ((TimeoutError, "timeout"), (ssl.SSLError, "tls"), (socket.gaierror, "dns"),
                (ConnectionError, "connection"), ((http.client.HTTPException, ValueError), "protocol"))


def classify_exception(exc: BaseException) -> str:
    """Ag hatasi turu: timeout | tls | dns | connection | protocol (sira onemli: alt siniflar once)."""
    if isinstance(exc, urllib.error.URLError) and isinstance(exc.reason, BaseException):
        return classify_exception(exc.reason)
    return next((kind for types, kind in _ERROR_KINDS if isinstance(exc, types)), "connection")


def parse_retry_after(value: str | None, now: _dt.datetime | None = None) -> float | None:
    """Retry-After: saniye veya HTTP tarihi -> saniye; anlasilmazsa None."""
    text = str(value).strip() if value is not None else ""
    if not text:
        return None
    if text.isdigit():
        return float(int(text))
    try:
        when = email.utils.parsedate_to_datetime(text)
    except (TypeError, ValueError):
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=_dt.timezone.utc)
    now = now or _dt.datetime.now(_dt.timezone.utc)
    return max(0.0, (when - now).total_seconds())


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401 - urllib arayuzu
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)  # cerez/kimlik isleyicisi yok


def _read_limited(stream: Any, method: str, limit: int) -> bytes:
    return b"" if method == "HEAD" or limit <= 0 else stream.read(limit + 1)


def urllib_transport(method: str, url: str, headers: Mapping[str, str], timeout: float, body_limit: int) -> RawResponse:
    """Gercek tasima: tek alisveris, yonlendirme izlenmez, govde en fazla body_limit+1 bayt okunur."""
    request = urllib.request.Request(url, headers=dict(headers), method=method)
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            return RawResponse(response.status, dict(response.headers.items()), _read_limited(response, method, body_limit))
    except urllib.error.HTTPError as error:
        try:
            body = _read_limited(error, method, body_limit)
        except (OSError, http.client.HTTPException, AttributeError):
            body = b""
        finally:
            error.close()
        return RawResponse(error.code, dict(error.headers.items()) if error.headers else {}, body)
    except (urllib.error.URLError, OSError, http.client.HTTPException, ValueError) as error:
        raise NetworkError(classify_exception(error), f"{type(error).__name__}: {error}") from error


def _header(headers: Mapping[str, str], name: str) -> str | None:
    return next((v for k, v in headers.items() if k.lower() == name), None)


def _kept_headers(headers: Mapping[str, str]) -> dict[str, str]:
    return {k.lower(): str(v) for k, v in headers.items() if k.lower() in KEPT_HEADERS}


def _host(url: str) -> str:
    try:
        return (urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def _scheme_ok(url: str) -> bool:
    try:
        return urlsplit(url.strip()).scheme.lower() in ("http", "https")
    except ValueError:
        return False


class HostLimiter:
    """Alan adi basina ve toplamda eszamanli istek siniri (once alan adi, sonra genel; kilitlenme yok)."""

    def __init__(self, per_host: int, total: int) -> None:
        self._per_host, self._total, self._lock = per_host, threading.BoundedSemaphore(total), threading.Lock()
        self._hosts: dict[str, threading.BoundedSemaphore] = {}

    @contextmanager
    def slot(self, host: str) -> Iterator[None]:
        with self._lock:
            sem = self._hosts.setdefault(host, threading.BoundedSemaphore(self._per_host))
        with sem, self._total:
            yield


class _Cache:
    def __init__(self, root: Path | None, refresh_transient: bool) -> None:
        self.root, self.refresh_transient = root, refresh_transient

    @staticmethod
    def key(method: str, url: str) -> str:
        text = url if method == "GET" else f"{method} {url}"
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def load(self, method: str, url: str, body_limit: int) -> FetchResult | None:
        if self.root is None:
            return None
        base = self.root / self.key(method, url)
        try:
            meta = json.loads(base.with_suffix(".json").read_text(encoding="utf-8"))
            body = base.with_suffix(".body").read_bytes() if meta.pop("has_body", False) else b""
            result = FetchResult.from_meta(meta, body)
        except (OSError, ValueError, TypeError, KeyError):
            return None
        if (result.truncated and body_limit > result.body_limit) or (self.refresh_transient and result.transient):
            return None
        if len(result.body) > body_limit:
            result = replace(result, body=result.body[:body_limit], truncated=True)
        return replace(result, from_cache=True)

    def store(self, result: FetchResult) -> None:
        if self.root is None:
            return
        self.root.mkdir(parents=True, exist_ok=True)
        base = self.root / self.key(result.method, result.url)
        if result.body:
            _atomic_write(base.with_suffix(".body"), result.body)
        meta = {**result.to_meta(), "has_body": bool(result.body)}
        # anahtar sirasi korunur: onbellekten donen kayit ilk kayitla bayt bayt ayni cikti uretmeli
        _atomic_write(base.with_suffix(".json"), json.dumps(meta, ensure_ascii=False).encode("utf-8"))


def _atomic_write(path: Path, data: bytes) -> None:
    tmp = path.with_name(f"{path.name}.{threading.get_ident()}.tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


class Fetcher:
    """Onbellekli, sinirli eszamanli, kibar HTTP istemcisi."""

    def __init__(self, transport: Transport = urllib_transport, cache_dir: Path | None = None, *,
                 sleep: Callable[[float], None] = time.sleep, clock: Callable[[], str] = utc_today,
                 per_host: int = PER_HOST_LIMIT, total: int = TOTAL_LIMIT, timeout: float = TIMEOUT_SECONDS,
                 refresh_transient: bool = False) -> None:
        self.transport, self.sleep, self.clock, self.timeout, self.total = transport, sleep, clock, timeout, total
        self._limiter = HostLimiter(per_host, total)
        self._cache = _Cache(Path(cache_dir) if cache_dir else None, refresh_transient)
        self._stats = threading.Lock()
        self.requests_made = self.cache_hits = 0

    def get(self, url: str, body_limit: int = MAX_BODY_BYTES) -> FetchResult:
        return self._cached("GET", url, body_limit)

    def head(self, url: str) -> FetchResult:
        return self._cached("HEAD", url, 0)

    def probe(self, url: str, body_limit: int = PROBE_BODY_BYTES) -> FetchResult:
        """HEAD; reddedilirse (>=400, 429 haric, veya baglanti/protokol hatasi) sinirli GET."""
        head = self.head(url)
        if ((head.status or 0) < 400 and head.error_kind not in HEAD_FALLBACK_ERRORS) or head.status == 429:
            return head
        return replace(self.get(url, body_limit), head_status=head.status)

    def fetch_many(self, urls: Iterable[str], mode: str = "get", body_limit: int | None = None) -> dict[str, FetchResult]:
        if mode not in ("get", "probe", "head"):
            raise ValueError(f"bilinmeyen kip: {mode}")
        unique = list(dict.fromkeys(urls))
        with ThreadPoolExecutor(max_workers=self.total) as pool:
            futures = {url: pool.submit(self._one, mode, body_limit, url) for url in interleave_by_host(unique)}
            return {url: futures[url].result() for url in unique}

    def _one(self, mode: str, body_limit: int | None, url: str) -> FetchResult:
        try:
            if mode == "probe":
                return self.probe(url, body_limit or PROBE_BODY_BYTES)
            return self.head(url) if mode == "head" else self.get(url, body_limit or MAX_BODY_BYTES)
        except Exception as error:  # beklenmeyen hata sonuc kaydina yazilir, sessizce yutulmaz
            return FetchResult(url=url, request_url="", method=mode.upper(), status=None, final_url=url,
                               error_kind="internal_error", error=f"{type(error).__name__}: {error}", fetched_on=self.clock())

    def _cached(self, method: str, url: str, body_limit: int) -> FetchResult:
        hit = self._cache.load(method, url, body_limit)
        if hit is not None:
            with self._stats:
                self.cache_hits += 1
            return hit
        result = self._fetch(method, url, body_limit)
        if result.error_kind not in LOCAL_ERRORS:
            self._cache.store(result)
        return result

    def _fetch(self, method: str, url: str, body_limit: int) -> FetchResult:
        base = FetchResult(url=url, request_url="", method=method, status=None, final_url=url,
                           body_limit=body_limit, fetched_on=self.clock())
        if not _scheme_ok(url):
            return replace(base, error_kind="blocked_scheme", error="yalniz http/https izinli")
        try:
            current = request_url(url)
        except (ValueError, UnicodeError) as error:
            return replace(base, error_kind="invalid_url", error=str(error))
        return self._follow(replace(base, request_url=current), method, current, body_limit)

    def _follow(self, base: FetchResult, method: str, current: str, body_limit: int) -> FetchResult:
        chain: list[Hop] = []
        attempts, retries = 0, []
        for _ in range(MAX_REDIRECTS + 1):
            raw, error, tries, log = self._exchange(method, current, body_limit)
            attempts, retries = attempts + tries, retries + list(log)
            done = replace(base, attempts=attempts, retries=tuple(retries), final_url=current)
            if error is not None:
                return replace(done, chain=tuple(chain + [Hop(current, None)]), error_kind=error.kind, error=str(error))
            location = _header(raw.headers, "location")
            if raw.status not in REDIRECT_STATUSES or not location:
                return replace(done, status=raw.status, chain=tuple(chain + [Hop(current, raw.status)]),
                               headers=_kept_headers(raw.headers), body=raw.body[:body_limit],
                               truncated=len(raw.body) > body_limit)
            target = urljoin(current, location.strip())
            chain.append(Hop(current, raw.status, target))
            if not _scheme_ok(target):
                return replace(done, chain=tuple(chain), error_kind="blocked_scheme", error=f"yonlendirme hedefi: {target}")
            try:
                current = request_url(target)
            except (ValueError, UnicodeError) as error:
                return replace(done, chain=tuple(chain), error_kind="invalid_url", error=str(error))
        return replace(base, chain=tuple(chain), final_url=current, attempts=attempts, retries=tuple(retries),
                       error_kind="too_many_redirects", error=f"{MAX_REDIRECTS} yonlendirmeden fazla")

    def _exchange(self, method: str, url: str, body_limit: int) -> tuple:
        """(ham yanit | None, ag hatasi | None, deneme, tekrar kaydi); 429/503'te Retry-After <= 30 sn, en cok 3 deneme."""
        retries: list[dict[str, Any]] = []
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                raw = self._send(method, url, body_limit)
            except NetworkError as error:
                return None, error, attempt, tuple(retries)
            if raw.status not in RETRY_STATUSES:
                return raw, None, attempt, tuple(retries)
            wait = parse_retry_after(_header(raw.headers, "retry-after"))
            if wait is not None and wait > RETRY_CAP_SECONDS:
                retries.append({"status": raw.status, "retry_after_seconds": wait, "gave_up": True})
                return raw, None, attempt, tuple(retries)
            if attempt == MAX_ATTEMPTS:
                retries.append({"status": raw.status, "gave_up": True})
                return raw, None, attempt, tuple(retries)
            wait = wait if wait is not None else float(min(RETRY_CAP_SECONDS, 2 ** attempt))
            retries.append({"status": raw.status, "wait_seconds": wait})
            self.sleep(wait)
        raise AssertionError("ulasilamaz")  # pragma: no cover

    def _send(self, method: str, url: str, body_limit: int) -> RawResponse:
        with self._limiter.slot(_host(url)):
            with self._stats:
                self.requests_made += 1
            return self.transport(method, url, dict(BASE_HEADERS), self.timeout, body_limit)


def interleave_by_host(urls: list[str]) -> list[str]:
    """Ayni alan adini art arda kuyruklamamak icin alan adlarina gore sirali dagitim (round-robin)."""
    groups: dict[str, list[str]] = {}
    for url in urls:
        groups.setdefault(_host(url), []).append(url)
    ordered: list[str] = []
    for index in range(max((len(g) for g in groups.values()), default=0)):
        ordered += [g[index] for g in groups.values() if index < len(g)]
    return ordered
