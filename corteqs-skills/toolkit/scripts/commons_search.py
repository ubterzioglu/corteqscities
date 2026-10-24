"""Wikimedia Commons aday arama: mekan basina dosya adaylari + ham imageinfo (extmetadata dahil).

Cikti (--out, JSONL): {entry_id, query_kind, title, imageinfo:{...}} (Commons imageinfo; adres sorgulari disinda ham).
Kaynak sirasi: wikidata P18 -> kategori uyeleri -> metin arama -> geosearch; dosya adina gore tekillestirilir.
Geosearch en son gelir ve --geo-max ile sinirlidir (yalniz yakinlik bulur, olculmus yanlis eslesme kaynagi).
Planda wikidata yoksa mekan adi Wikidata'da aranir; yalniz koordinati mekana 2 km'den yakin oge kabul edilir.
Wikimedia 2026: thumb'lar thumb.wikimedia.org'dan ve yalniz standart genisliklerde (330/500/960/1280...; 1600 = HTTP
400) -> iiurlwidth=DEFAULT_THUMB_WIDTH. API adreslere ?utm_* ekliyor -> ciktida url/thumburl/descriptionurl (ve
thumbattribs.src, responsiveUrls) sorgusuz; descriptionshorturl'in ?curid= sorgusu kimliktir, korunur. Onbellek hamdir.
API nezaketi: aciklayici User-Agent, seri istek, maxlag=5, 429/503 + Retry-After (<=30 sn, 3 deneme, sonra
'resume_later'), istekler arasi kucuk bekleme, URL'ye gore dosya onbellegi, --max-requests sert ust sinir.
Kimlik bilgisi veya kisisel veri gonderilmez.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8
from photo_rules import haversine_km

USER_AGENT = "CorteqsCityToolkit/0.1 (content research; https://www.mediawiki.org/wiki/API:Etiquette)"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
WIKIDATA_API = "https://www.wikidata.org/w/api.php"
MAXLAG = "5"
MAX_ATTEMPTS = 3
RETRY_CAP_SECONDS = 30
IMAGEINFO_BATCH = 50
DEFAULT_DELAY = 0.3
IIPROP = "url|size|mime|sha1|extmetadata"
DEFAULT_THUMB_WIDTH = 1280  # standart genislik; 1600 thumb adresi HTTP 400 veriyor
URL_FIELDS = ("url", "thumburl", "descriptionurl")
QUERY_IN_SRCSET_RE = re.compile(r"\?[^\s,]*")  # '<adres>?q 1.5x, <adres>?q 2x'
DEFAULT_GEO_MAX = 5
WIKIDATA_MATCH_KM = 2.0
WIKIDATA_SEARCH_LIMIT = "5"

Transport = Callable[[str, dict[str, str]], "tuple[int, dict[str, str], bytes]"]


class ResumeLater(Exception):
    """Sunucu daha sonra denememizi istiyor (veya deneme hakki bitti); sonra devam edilir."""


class BudgetExceeded(Exception):
    """--max-requests siniri doldu."""


class ApiError(Exception):
    """Kalici API/ag hatasi (yeniden denemek anlamsiz)."""


def urllib_transport(url: str, headers: dict[str, str]) -> tuple[int, dict[str, str], bytes]:
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers or {}), error.read()
    except (urllib.error.URLError, TimeoutError, OSError) as error:
        raise ApiError(f"ag hatasi: {error}") from error


def _retry_delay(headers: dict[str, str], attempt: int) -> float:
    raw = {k.lower(): v for k, v in headers.items()}.get("retry-after", "")
    if raw.strip().isdigit():
        delay = int(raw)
    elif raw.strip():
        raise ResumeLater(f"Retry-After anlasilamadi: {raw!r}")
    else:
        delay = attempt * 5
    if delay > RETRY_CAP_SECONDS:
        raise ResumeLater(f"sunucu {delay} sn bekletmek istiyor (> {RETRY_CAP_SECONDS}); sonra devam edin")
    return float(delay)


class Client:
    """Seri, onbellekli, nazik API istemcisi."""

    def __init__(self, transport: Transport, cache_dir: Path, max_requests: int,
                 sleep: Callable[[float], None] = time.sleep, delay: float = DEFAULT_DELAY) -> None:
        self.transport, self.cache_dir, self.max_requests = transport, Path(cache_dir), max_requests
        self.sleep, self.delay = sleep, delay
        self.requests_made = 0
        self.cache_hits = 0

    def _cache_path(self, url: str) -> Path:
        return self.cache_dir / (hashlib.sha256(url.encode("utf-8")).hexdigest() + ".json")

    def get_json(self, endpoint: str, params: dict[str, str]) -> dict[str, Any]:
        query = {**params, "format": "json", "formatversion": "2", "maxlag": MAXLAG}
        url = f"{endpoint}?{urlencode(sorted(query.items()))}"
        cached = self._cache_path(url)
        if cached.exists():
            self.cache_hits += 1
            return json.loads(cached.read_text(encoding="utf-8"))
        data = self._fetch(url)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cached.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data

    def _fetch(self, url: str) -> dict[str, Any]:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if self.requests_made >= self.max_requests:
                raise BudgetExceeded(f"--max-requests={self.max_requests} doldu")
            self.sleep(self.delay)
            self.requests_made += 1
            status, headers, body = self.transport(url, {"User-Agent": USER_AGENT, "Accept": "application/json"})
            retry = status in (429, 503)
            data: dict[str, Any] = {}
            if status == 200:
                data = self._parse(body)
                retry = data.get("error", {}).get("code") == "maxlag"
                if "error" in data and not retry:
                    raise ApiError(f"API hatasi: {data['error']}")
            elif not retry:
                raise ApiError(f"HTTP {status}")
            if not retry:
                return data
            if attempt == MAX_ATTEMPTS:
                break
            self.sleep(_retry_delay(headers, attempt))
        raise ResumeLater(f"{MAX_ATTEMPTS} deneme sonrasi hala 429/503/maxlag; sonra devam edin")

    @staticmethod
    def _parse(body: bytes) -> dict[str, Any]:
        try:
            data = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ApiError(f"gecersiz JSON: {error}") from error
        if not isinstance(data, dict):
            raise ApiError("JSON nesne degil")
        return data


def norm_title(title: str) -> str:
    cleaned = title.replace("_", " ").strip()
    return cleaned[:1].upper() + cleaned[1:]


def strip_query(url: str) -> str:
    """Adresin sorgu dizesini (?utm_* ...) ve #parcasini atar; geri kalani aynen birakir."""
    return url.split("#", 1)[0].split("?", 1)[0]


def clean_imageinfo(info: dict[str, Any]) -> dict[str, Any]:
    """imageinfo kopyasi, adresleri sorgusuz: URL_FIELDS, thumbattribs.src/srcset, responsiveUrls. Girdi degismez.

    extmetadata (lisans kaniti HTML'i) ve descriptionshorturl (?curid= kimliktir) oldugu gibi kalir.
    """
    cleaned = {**info, **{key: strip_query(info[key]) for key in URL_FIELDS if isinstance(info.get(key), str)}}
    attribs, responsive = info.get("thumbattribs"), info.get("responsiveUrls")
    if isinstance(attribs, dict):
        cleaned["thumbattribs"] = {**attribs, **{key: QUERY_IN_SRCSET_RE.sub("", attribs[key]) for key in ("src", "srcset")
                                                 if isinstance(attribs.get(key), str)}}
    if isinstance(responsive, dict):
        cleaned["responsiveUrls"] = {k: strip_query(v) if isinstance(v, str) else v for k, v in responsive.items()}
    return cleaned


def _claim_values(entity: dict[str, Any], prop: str) -> list[str]:
    values = []
    for claim in entity.get("claims", {}).get(prop, []):
        value = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(value, str) and value.strip():
            values.append(value)
    return values


def _coordinates(entity: dict[str, Any]) -> list[tuple[float, float]]:
    coords = []
    for claim in entity.get("claims", {}).get("P625", []):
        value = claim.get("mainsnak", {}).get("datavalue", {}).get("value")
        if isinstance(value, dict) and all(isinstance(value.get(k), (int, float)) for k in ("latitude", "longitude")):
            coords.append((float(value["latitude"]), float(value["longitude"])))
    return coords


def _entity_sources(entity: dict[str, Any]) -> tuple[list[str], str | None]:
    files = ["File:" + norm_title(v) for v in _claim_values(entity, "P18")]
    cats = _claim_values(entity, "P373")
    return files, (norm_title(cats[0]) if cats else None)


def wikidata_sources(client: Client, qid: str) -> tuple[list[str], str | None]:
    data = client.get_json(WIKIDATA_API, {"action": "wbgetentities", "ids": qid, "props": "claims"})
    return _entity_sources(data.get("entities", {}).get(qid, {}))


def resolve_wikidata(client: Client, venue: dict[str, Any]) -> tuple[str, dict[str, Any]] | None:
    """Ada gore Wikidata ogesi; yalniz koordinati mekana WIKIDATA_MATCH_KM'den yakin ilk aday (ad tek basina yetmez)."""
    lat, lon = venue.get("lat"), venue.get("lon")
    if not venue.get("name") or lat is None or lon is None:
        return None
    found = client.get_json(WIKIDATA_API, {"action": "wbsearchentities", "search": venue["name"], "type": "item",
                                           "language": venue.get("language") or "en", "limit": WIKIDATA_SEARCH_LIMIT})
    ids = [item["id"] for item in found.get("search", []) if item.get("id")]
    if not ids:
        return None
    entities = client.get_json(WIKIDATA_API, {"action": "wbgetentities", "ids": "|".join(ids), "props": "claims"})
    for qid in ids:
        entity = entities.get("entities", {}).get(qid, {})
        if any(haversine_km(lat, lon, a, b) <= WIKIDATA_MATCH_KM for a, b in _coordinates(entity)):
            return qid, entity
    return None


def _list_titles(client: Client, params: dict[str, str], key: str) -> list[str]:
    data = client.get_json(COMMONS_API, {"action": "query", **params})
    return [item["title"] for item in data.get("query", {}).get(key, []) if item.get("title")]


def _wikidata_step(client: Client, venue: dict[str, Any]) -> tuple[list[str], str | None, str | None]:
    """(P18 dosyalari, P373 kategorisi, ada gore cozulen QID)."""
    if venue.get("wikidata"):
        return (*wikidata_sources(client, venue["wikidata"]), None)
    resolved = resolve_wikidata(client, venue)
    if resolved is None:
        return [], None, None
    return (*_entity_sources(resolved[1]), resolved[0])


def gather_titles(client: Client, venue: dict[str, Any], radius: int, limit: int,
                  geo_max: int = DEFAULT_GEO_MAX) -> tuple[list[tuple[str, str]], str | None]:
    """((baslik, query_kind) listesi, cozulen QID); kaynak sirasina gore, tekillestirilmis, limit ile sinirli."""
    files, wd_cat, resolved_qid = _wikidata_step(client, venue)
    found: list[tuple[str, str]] = [(t, "wikidata_p18") for t in files]
    category = venue.get("commons_category") or wd_cat
    if category:
        cat = category if category.startswith("Category:") else f"Category:{category}"
        found += [(t, "category") for t in _list_titles(
            client, {"list": "categorymembers", "cmtitle": cat, "cmtype": "file", "cmlimit": str(limit)}, "categorymembers")]
    if venue.get("name"):
        text = f"\"{venue['name']}\" {venue.get('municipality', '')}".strip()
        found += [(t, "search") for t in _list_titles(
            client, {"list": "search", "srsearch": text, "srnamespace": "6", "srlimit": str(limit)}, "search")]
    if geo_max > 0 and venue.get("lat") is not None and venue.get("lon") is not None:
        found += [(t, "geosearch") for t in _list_titles(client, {
            "list": "geosearch", "gscoord": f"{venue['lat']}|{venue['lon']}", "gsradius": str(radius),
            "gsnamespace": "6", "gslimit": str(min(geo_max, limit))}, "geosearch")]
    seen: dict[str, str] = {}
    for title, kind in found:
        seen.setdefault(norm_title(title), kind)
    return list(seen.items())[:limit], resolved_qid


def fetch_imageinfo(client: Client, titles: list[str]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for start in range(0, len(titles), IMAGEINFO_BATCH):
        batch = titles[start:start + IMAGEINFO_BATCH]
        data = client.get_json(COMMONS_API, {"action": "query", "prop": "imageinfo", "iiprop": IIPROP,
                                             "iiurlwidth": str(DEFAULT_THUMB_WIDTH), "titles": "|".join(batch)})
        for page in data.get("query", {}).get("pages", []):
            if page.get("imageinfo"):
                result[norm_title(page["title"])] = clean_imageinfo(page["imageinfo"][0])
    return result


def search_venue_detail(client: Client, venue: dict[str, Any], radius: int, limit: int,
                        geo_max: int = DEFAULT_GEO_MAX) -> tuple[list[dict[str, Any]], str | None]:
    titles, resolved_qid = gather_titles(client, venue, radius, limit, geo_max)
    infos = fetch_imageinfo(client, [t for t, _ in titles])
    records = [{"entry_id": venue["entry_id"], "query_kind": kind, "title": title, "imageinfo": infos[title]}
               for title, kind in titles if title in infos]
    return records, resolved_qid


def search_venue(client: Client, venue: dict[str, Any], radius: int, limit: int,
                 geo_max: int = DEFAULT_GEO_MAX) -> list[dict[str, Any]]:
    return search_venue_detail(client, venue, radius, limit, geo_max)[0]


def load_venues(path: Path) -> list[dict[str, Any]]:
    venues = []
    for number, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{path}:{number}: gecersiz JSON ({error})") from error
        if not isinstance(row, dict) or not row.get("entry_id"):
            raise ValueError(f"{path}:{number}: entry_id zorunlu")
        venues.append(row)
    return venues


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in records), encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Wikimedia Commons aday arama (ham imageinfo)")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--radius", type=int, default=400)
    p.add_argument("--limit", type=int, default=30)
    p.add_argument("--max-requests", type=int, default=200)
    p.add_argument("--geo-max", type=int, default=DEFAULT_GEO_MAX,
                   help="mekan basina en fazla geosearch adayi (0 = geosearch yok)")
    return p


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep) -> int:
    setup_utf8()
    args = _parser().parse_args(argv)
    try:
        if args.geo_max < 0:
            raise ValueError("--geo-max negatif olamaz")
        venues = load_venues(args.plan)
    except (OSError, ValueError) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE
    cache_dir = args.cache_dir or args.out.parent / ".commons-cache"
    client = Client(transport, cache_dir, args.max_requests, sleep=sleep)
    records: list[dict[str, Any]] = []
    per_venue: dict[str, int] = {}
    resolved: dict[str, str] = {}
    errors: list[str] = []
    status = "ok"
    for venue in venues:
        try:
            found, qid = search_venue_detail(client, venue, args.radius, args.limit, args.geo_max)
        except (ResumeLater, BudgetExceeded) as error:
            status = "resume_later"
            errors.append(f"{venue['entry_id']}: {error}")
            break
        except ApiError as error:
            found, qid = [], None
            errors.append(f"{venue['entry_id']}: {error}")
        records += found
        per_venue[venue["entry_id"]] = len(found)
        if qid:
            resolved[venue["entry_id"]] = qid
    _write_jsonl(args.out, records)
    emit({"status": status, "venues": len(venues), "requests_made": client.requests_made, "cache_hits": client.cache_hits,
          "candidates": len(records), "per_venue": per_venue, "wikidata_resolved": resolved,
          "venues_with_zero_candidates": [k for k, v in per_venue.items() if v == 0], "errors": errors, "out": str(args.out)})
    return EXIT_FINDINGS if errors else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
