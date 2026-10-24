"""web_fetch: kibar HTTP katmani. Sahte tasima katmaniyla (ag yok) + yalniz loopback sunucuyla gercek urllib testi."""
from __future__ import annotations

import datetime as dt
import hashlib
import http.client
import socket
import ssl
import threading
import time
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import pytest

import web_fetch as wf
from web_fetch import NetworkError, RawResponse

HTML = b"<html><head><title>Hallo</title></head><body><p>Inhoud</p></body></html>"


def ok(body: bytes = HTML, ctype: str = "text/html; charset=utf-8", status: int = 200) -> RawResponse:
    return RawResponse(status, {"Content-Type": ctype}, body)


def redirect(location: str, status: int = 301) -> RawResponse:
    return RawResponse(status, {"Location": location}, b"")


def status(code: int, **headers: str) -> RawResponse:
    return RawResponse(code, {k.replace("_", "-"): v for k, v in headers.items()}, b"err")


class FakeTransport:
    """Sahte tasima: rota -> yanit(lar). Liste sirayla tuketilir, son eleman tekrar eder.

    Rota anahtari (yontem, url) veya url. Cagri gunlugu ve eszamanlilik olcumu tutar.
    """

    def __init__(self, routes: dict, delay: float = 0.0) -> None:
        self.routes = {k: (list(v) if isinstance(v, list) else [v]) for k, v in routes.items()}
        self.delay, self.calls, self._lock = delay, [], threading.Lock()
        self._active: dict[str, int] = {}
        self.max_host: dict[str, int] = {}
        self.max_total = 0

    def __call__(self, method, url, headers, timeout, body_limit):
        host = urlsplit(url).hostname or ""
        with self._lock:
            self.calls.append((method, url, dict(headers), timeout, body_limit))
            self._active[host] = self._active.get(host, 0) + 1
            self.max_host[host] = max(self.max_host.get(host, 0), self._active[host])
            self.max_total = max(self.max_total, sum(self._active.values()))
        try:
            if self.delay:
                time.sleep(self.delay)
            queue = self.routes.get((method, url)) or self.routes.get(url)
            if queue is None:
                return RawResponse(404, {"Content-Type": "text/html"}, b"<title>Not Found</title>")
            with self._lock:
                item = queue.pop(0) if len(queue) > 1 else queue[0]
            if isinstance(item, Exception):
                raise item
            return item
        finally:
            with self._lock:
                self._active[host] -= 1


def make_fetcher(routes: dict, tmp_path=None, **kwargs) -> tuple[wf.Fetcher, FakeTransport, list[float]]:
    fake = FakeTransport(routes, delay=kwargs.pop("delay", 0.0))
    sleeps: list[float] = []
    fetcher = wf.Fetcher(transport=fake, cache_dir=(tmp_path / "cache") if tmp_path else None,
                         sleep=sleeps.append, clock=lambda: "2026-10-22", **kwargs)
    return fetcher, fake, sleeps


# ---------------------------------------------------------------- istek bicimi

def test_get_sends_polite_headers_without_credentials():
    fetcher, fake, _ = make_fetcher({"https://a.example.org/x": ok()})
    result = fetcher.get("https://a.example.org/x")
    method, url, headers, timeout, _ = fake.calls[0]
    assert (method, url, timeout) == ("GET", "https://a.example.org/x", wf.TIMEOUT_SECONDS)
    assert headers["User-Agent"] == wf.USER_AGENT == "CorteqsCityToolkit/0.1 (content QA; contact via project owner)"
    assert not {k.lower() for k in headers} & {"cookie", "authorization", "proxy-authorization"}
    assert result.status == 200 and result.final_url == "https://a.example.org/x"
    assert result.fetched_on == "2026-10-22" and result.body == HTML and not result.from_cache


def test_request_url_strips_credentials_fragment_and_encodes():
    assert wf.request_url("https://user:pw@www.Example.org/päd/ü?q=ç#frag") == "https://www.example.org/p%C3%A4d/%C3%BC?q=%C3%A7"
    assert wf.request_url("https://bücher.example/") == "https://xn--bcher-kva.example/"
    assert wf.request_url("https://x.example/a%20b c") == "https://x.example/a%20b%20c"
    assert wf.request_url("https://x.example:8443") == "https://x.example:8443/"


def test_credentials_in_url_are_never_sent():
    fetcher, fake, _ = make_fetcher({"https://a.example.org/x": ok()})
    result = fetcher.get("https://u:secret@a.example.org/x")
    assert fake.calls[0][1] == "https://a.example.org/x"
    assert "secret" not in repr(fake.calls) and result.status == 200
    assert result.request_url == "https://a.example.org/x"


@pytest.mark.parametrize("url", ["ftp://a.example.org/x", "file:///etc/passwd", "javascript:alert(1)", "geen url", ""])
def test_non_http_urls_are_blocked_without_network(url):
    fetcher, fake, _ = make_fetcher({})
    result = fetcher.get(url)
    assert fake.calls == [] and result.status is None and result.error_kind == "blocked_scheme"


# ---------------------------------------------------------------- yonlendirme

def test_redirect_chain_and_final_url_are_recorded():
    fetcher, _, _ = make_fetcher({
        "https://a.example.org/old": redirect("/mid"),
        "https://a.example.org/mid": redirect("https://b.example.org/final", 302),
        "https://b.example.org/final": ok(),
    })
    result = fetcher.get("https://a.example.org/old")
    assert [(h.url, h.status) for h in result.chain] == [
        ("https://a.example.org/old", 301), ("https://a.example.org/mid", 302), ("https://b.example.org/final", 200)]
    assert result.chain[0].location == "https://a.example.org/mid"
    assert result.final_url == "https://b.example.org/final" and result.status == 200 and result.redirected


def test_redirect_loop_stops_with_error():
    fetcher, fake, _ = make_fetcher({"https://a.example.org/x": redirect("/x")})
    result = fetcher.get("https://a.example.org/x")
    assert result.error_kind == "too_many_redirects" and len(fake.calls) == wf.MAX_REDIRECTS + 1


def test_redirect_without_location_is_kept_as_status():
    fetcher, _, _ = make_fetcher({"https://a.example.org/x": RawResponse(302, {}, b"")})
    result = fetcher.get("https://a.example.org/x")
    assert result.status == 302 and result.error_kind is None


def test_redirect_to_non_http_scheme_is_blocked():
    fetcher, _, _ = make_fetcher({"https://a.example.org/x": redirect("mailto:a@b.example")})
    assert fetcher.get("https://a.example.org/x").error_kind == "blocked_scheme"


# ---------------------------------------------------------------- tekrar / Retry-After

def test_429_respects_retry_after_then_succeeds():
    url = "https://a.example.org/x"
    fetcher, fake, sleeps = make_fetcher({url: [status(429, Retry_After="2"), ok()]})
    result = fetcher.get(url)
    assert result.status == 200 and result.attempts == 2 and sleeps == [2.0]
    assert result.retries == ({"status": 429, "wait_seconds": 2.0},)


def test_retry_after_above_cap_gives_up_without_waiting():
    url = "https://a.example.org/x"
    fetcher, fake, sleeps = make_fetcher({url: status(429, Retry_After="120")})
    result = fetcher.get(url)
    assert result.status == 429 and result.attempts == 1 and sleeps == [] and len(fake.calls) == 1
    assert result.retries == ({"status": 429, "retry_after_seconds": 120.0, "gave_up": True},)


def test_503_is_retried_at_most_three_times_with_capped_backoff():
    url = "https://a.example.org/x"
    fetcher, fake, sleeps = make_fetcher({url: status(503)})
    result = fetcher.get(url)
    assert result.status == 503 and result.attempts == wf.MAX_ATTEMPTS == 3 and len(fake.calls) == 3
    assert len(sleeps) == 2 and all(0 < s <= wf.RETRY_CAP_SECONDS for s in sleeps)


def test_500_is_not_retried():
    fetcher, fake, _ = make_fetcher({"https://a.example.org/x": status(500)})
    assert fetcher.get("https://a.example.org/x").status == 500 and len(fake.calls) == 1


def test_parse_retry_after_forms():
    now = dt.datetime(2026, 10, 21, 7, 28, 0, tzinfo=dt.timezone.utc)
    assert wf.parse_retry_after("5", now) == 5.0
    assert wf.parse_retry_after("Wed, 21 Oct 2026 07:28:30 GMT", now) == 30.0
    assert wf.parse_retry_after("Wed, 21 Oct 2026 07:00:00 GMT", now) == 0.0
    assert wf.parse_retry_after("yakinda", now) is None and wf.parse_retry_after(None, now) is None


# ---------------------------------------------------------------- HEAD / sinirli GET / govde

def test_probe_falls_back_to_limited_get_when_head_rejected():
    url = "https://a.example.org/x"
    fetcher, fake, _ = make_fetcher({("HEAD", url): status(405), ("GET", url): ok()})
    result = fetcher.probe(url)
    assert result.method == "GET" and result.head_status == 405 and result.status == 200
    assert [(c[0], c[1], c[4]) for c in fake.calls] == [("HEAD", url, 0), ("GET", url, wf.PROBE_BODY_BYTES)]


def test_probe_keeps_head_result_when_accepted():
    url = "https://a.example.org/file.pdf"
    fetcher, fake, _ = make_fetcher({("HEAD", url): ok(b"", "application/pdf")})
    result = fetcher.probe(url)
    assert result.method == "HEAD" and result.status == 200 and len(fake.calls) == 1 and result.head_status is None


def test_probe_falls_back_on_head_network_error():
    url = "https://a.example.org/x"
    fetcher, _, _ = make_fetcher({("HEAD", url): NetworkError("connection", "reset"), ("GET", url): ok()})
    result = fetcher.probe(url)
    assert result.method == "GET" and result.status == 200


def test_body_is_cut_at_limit_and_marked_truncated():
    fetcher, _, _ = make_fetcher({"https://a.example.org/x": ok(b"x" * 100)})
    result = fetcher.get("https://a.example.org/x", body_limit=10)
    assert result.body == b"x" * 10 and result.truncated


def test_network_error_is_recorded_not_retried():
    fetcher, fake, _ = make_fetcher({"https://a.example.org/x": NetworkError("timeout", "timed out")})
    result = fetcher.get("https://a.example.org/x")
    assert result.status is None and result.error_kind == "timeout" and "timed out" in result.error
    assert len(fake.calls) == 1 and result.attempts == 1


@pytest.mark.parametrize("exc, kind", [
    (socket.timeout("t"), "timeout"),
    (TimeoutError("t"), "timeout"),
    (urllib.error.URLError(socket.timeout("t")), "timeout"),
    (ssl.SSLCertVerificationError("bad cert"), "tls"),
    (urllib.error.URLError(ssl.SSLError("hs")), "tls"),
    (urllib.error.URLError(socket.gaierror("nodename")), "dns"),
    (ConnectionResetError("reset"), "connection"),
    (http.client.RemoteDisconnected("closed"), "connection"),
    (http.client.InvalidURL("bad"), "protocol"),
    (OSError("other"), "connection"),
])
def test_classify_exception(exc, kind):
    assert wf.classify_exception(exc) == kind


# ---------------------------------------------------------------- onbellek

def test_second_fetch_comes_from_url_sha256_cache(tmp_path):
    url = "https://a.example.org/x"
    first, fake1, _ = make_fetcher({url: ok()}, tmp_path)
    r1 = first.get(url)
    assert (tmp_path / "cache" / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")).exists()
    second, fake2, _ = make_fetcher({url: ok(b"changed")}, tmp_path)
    r2 = second.get(url)
    assert fake2.calls == [] and r2.from_cache and r2.body == r1.body == HTML
    assert (r2.status, r2.final_url, r2.fetched_on, r2.chain) == (r1.status, r1.final_url, r1.fetched_on, r1.chain)
    assert (second.requests_made, second.cache_hits) == (0, 1)


def test_truncated_cache_entry_is_refetched_for_larger_limit(tmp_path):
    url = "https://a.example.org/x"
    fetcher, fake, _ = make_fetcher({url: ok(b"y" * 50)}, tmp_path)
    assert fetcher.get(url, body_limit=10).truncated
    full = fetcher.get(url, body_limit=1000)
    assert not full.truncated and len(full.body) == 50 and len(fake.calls) == 2
    assert fetcher.get(url, body_limit=1000).from_cache and len(fake.calls) == 2
    assert fetcher.get(url, body_limit=20).from_cache and len(fake.calls) == 2


def test_head_and_get_are_cached_separately(tmp_path):
    url = "https://a.example.org/x"
    fetcher, fake, _ = make_fetcher({url: ok()}, tmp_path)
    fetcher.head(url)
    assert not fetcher.get(url).from_cache and len(fake.calls) == 2


def test_refresh_transient_refetches_cached_errors(tmp_path):
    url = "https://a.example.org/x"
    first, _, _ = make_fetcher({url: status(500)}, tmp_path)
    assert first.get(url).status == 500
    cached, fake2, _ = make_fetcher({url: ok()}, tmp_path)
    assert cached.get(url).status == 500 and fake2.calls == []
    fresh, fake3, _ = make_fetcher({url: ok()}, tmp_path, refresh_transient=True)
    assert fresh.get(url).status == 200 and len(fake3.calls) == 1


def test_corrupt_cache_entry_is_ignored(tmp_path):
    url = "https://a.example.org/x"
    fetcher, fake, _ = make_fetcher({url: ok()}, tmp_path)
    (tmp_path / "cache").mkdir(parents=True)
    (tmp_path / "cache" / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")).write_text("{bozuk", encoding="utf-8")
    assert fetcher.get(url).status == 200 and len(fake.calls) == 1


# ---------------------------------------------------------------- eszamanlilik

def test_fetch_many_limits_per_host_and_total_concurrency():
    urls = [f"https://h{h}.example.org/p{i}" for h in range(5) for i in range(4)]
    fetcher, fake, _ = make_fetcher({u: ok() for u in urls}, delay=0.03)
    results = fetcher.fetch_many(urls)
    assert set(results) == set(urls) and all(r.status == 200 for r in results.values())
    assert max(fake.max_host.values()) <= wf.PER_HOST_LIMIT == 2
    assert fake.max_total <= wf.TOTAL_LIMIT == 6 and fake.max_total >= 3


def test_fetch_many_single_host_never_exceeds_two():
    urls = [f"https://one.example.org/p{i}" for i in range(8)]
    fetcher, fake, _ = make_fetcher({u: ok() for u in urls}, delay=0.02)
    fetcher.fetch_many(urls, mode="probe")
    assert fake.max_host["one.example.org"] == 2


def test_fetch_many_rejects_unknown_mode():
    fetcher, _, _ = make_fetcher({})
    with pytest.raises(ValueError):
        fetcher.fetch_many(["https://a.example.org/"], mode="post")


# ---------------------------------------------------------------- gercek urllib (yalniz 127.0.0.1)

class _Handler(BaseHTTPRequestHandler):
    seen: list[dict] = []

    def log_message(self, *args):  # sessiz
        pass

    def _send(self, code: int, body: bytes = b"", headers: dict | None = None) -> None:
        self.send_response(code)
        for k, v in (headers or {"Content-Type": "text/html"}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            try:
                self.wfile.write(body)
            except ConnectionError:  # istemci zaman asimiyla baglantiyi kapatmis olabilir
                pass

    def do_GET(self):
        _Handler.seen.append(dict(self.headers))
        if self.path == "/redir":
            return self._send(302, b"", {"Location": "/ok"})
        if self.path == "/big":
            return self._send(200, b"z" * 5000)
        if self.path == "/slow":
            time.sleep(1.0)
            return self._send(200, b"late")
        if self.path == "/gone":
            return self._send(410, b"gone")
        return self._send(200, HTML)

    def do_HEAD(self):
        if self.path == "/nohead":
            return self._send(405)
        return self._send(200)


@pytest.fixture()
def server():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def test_urllib_transport_does_not_follow_redirects(server):
    raw = wf.urllib_transport("GET", server + "/redir", {"User-Agent": wf.USER_AGENT}, 5, 1000)
    assert raw.status == 302 and {k.lower(): v for k, v in raw.headers.items()}["location"] == "/ok"


def test_urllib_transport_reads_at_most_limit_plus_one(server):
    raw = wf.urllib_transport("GET", server + "/big", {}, 5, 100)
    assert raw.status == 200 and len(raw.body) == 101


def test_urllib_transport_returns_http_errors_as_status(server):
    raw = wf.urllib_transport("GET", server + "/gone", {}, 5, 100)
    assert raw.status == 410 and raw.body == b"gone"


def test_urllib_transport_timeout_and_refused(server):
    with pytest.raises(NetworkError) as slow:
        wf.urllib_transport("GET", server + "/slow", {}, 0.2, 100)
    assert slow.value.kind == "timeout"
    probe = socket.socket()
    probe.bind(("127.0.0.1", 0))
    port = probe.getsockname()[1]
    probe.close()
    with pytest.raises(NetworkError) as refused:  # Windows reddi ~2 sn surer; zaman asimi bundan uzun olmali
        wf.urllib_transport("GET", f"http://127.0.0.1:{port}/", {}, 15, 100)
    assert refused.value.kind == "connection"


def test_fetcher_with_real_transport_end_to_end(server):
    _Handler.seen.clear()
    fetcher = wf.Fetcher(clock=lambda: "2026-10-22")
    result = fetcher.get(server + "/redir")
    assert result.status == 200 and result.final_url == server + "/ok" and len(result.chain) == 2
    assert all(h.get("User-Agent") == wf.USER_AGENT and "Cookie" not in h for h in _Handler.seen)
    probe = fetcher.probe(server + "/nohead")
    assert probe.method == "GET" and probe.head_status == 405 and probe.status == 200


def test_default_clock_is_utc_date():
    assert wf.utc_today() == dt.datetime.now(dt.timezone.utc).date().isoformat()
