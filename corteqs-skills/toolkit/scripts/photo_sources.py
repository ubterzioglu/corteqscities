"""Commons yetersiz kalinca ikinci kaynaklardan foto adayi arar (Bakersfield: yalniz Commons = 38 foto, Atinc: Commons + Flickr = 275).

Kullanim: photo_sources.py --plan venues.jsonl --search search.jsonl [--sources openverse,smithsonian] [--min-per-venue 3]
                           [--per-source 6] [--cache-dir <dir>] [--max-requests 400]
Okur: --plan (photo_candidates plan-from-xlsx ciktisi: entry_id, role, name, aliases, municipality), --search (commons_search
      ciktisi). Commons'ta adayi --min-per-venue'den az olan her mekan/mahalle icin kaynaklari SIRAYLA dener, esik dolunca
      durur ("bulamadiginda siradaki kaynaga gec"). Yeni satirlar --search dosyasina EKLENIR (query_kind 'alt:<kaynak>');
      photo_candidates from-search, photo_prefilter ve photo_rows degismeden okur (imageinfo Commons bicimindedir, ek anahtar
      'provider').
Kaynaklar (sira = gecis sirasi):
  openverse    api.openverse.org; Flickr ve baska CC kaynaklari tek aramada. Anahtarsiz (anonim limit dusuk; OPENVERSE_TOKEN
               varsa Bearer ile gonderilir). Yalniz CC BY, CC BY-SA, CC0, PDM; Wikimedia sonuclari atilir (Commons zaten tarandi).
  smithsonian  api.si.edu/openaccess; yalniz CC0. SMITHSONIAN_API_KEY yoksa DEMO_KEY (dusuk limit). Gorsel adresi uzantisiz
               ise (ids.si.edu) kare indirilemez, atlanir.
  europeana    api.europeana.eu; yalniz acik haklar (CC BY, CC BY-SA, CC0, PDM). EUROPEANA_API_KEY yoksa api2demo. Avrupa
               sehirleri icin; varsayilan sirada YOK (--sources ile acilir).
Denendi ve alinmadi: Library of Congress (otomatik erisime 403, bot engeli asilmaz), Mapillary (anahtar zorunlu), Geograph (anahtar).
Lisans yazarin/kaynak sayfasinin beyanidir; resmi dogrulayici ve piksel incelemesi sonrasinda yine kapidir. Indirme icin
stdout'taki download_hosts, download_plan'a --allow-host olarak verilmelidir.
stdout tek satir JSON; cikis 0 tamam / 1 butce ya da sunucu bekletmesi (sonra devam) / 2 kullanim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlencode, urlsplit

from commons_search import (ApiError, BudgetExceeded, ResumeLater, USER_AGENT, _retry_delay, urllib_transport)
from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8

MAX_ATTEMPTS = 3
MAX_SOURCE_FAILURES = 3
DEFAULT_DELAY = 0.5
IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
WIKIMEDIA_SOURCES = ("wikimedia", "wikimedia_commons", "commons")
CC0_URL = "https://creativecommons.org/publicdomain/zero/1.0/"
GENERIC = {"museum", "park", "the", "and", "center", "centre", "theatre", "theater", "library", "church", "school", "of",
           "restaurant", "cafe", "gallery", "hall", "club", "national", "state", "county", "city", "historic", "old"}
Transport = Callable[[str, dict[str, str]], tuple[int, dict[str, str], bytes]]


class Fetcher:
    """Seri, onbellekli JSON istemcisi (commons_search.Client'in genel surumu)."""

    def __init__(self, transport: Transport, cache_dir: Path, max_requests: int,
                 sleep: Callable[[float], None] = time.sleep, delay: float = DEFAULT_DELAY) -> None:
        self.transport, self.cache_dir, self.max_requests = transport, Path(cache_dir), max_requests
        self.sleep, self.delay, self.requests_made = sleep, delay, 0

    def get(self, endpoint: str, params: dict[str, str], headers: dict[str, str] | None = None) -> dict[str, Any]:
        # anahtar/belirtec onbellek adina girmez (gizli bilgi diske yazilmaz)
        public = {k: v for k, v in params.items() if k not in ("api_key", "wskey")}
        cache = self.cache_dir / (hashlib.sha256(f"{endpoint}?{urlencode(sorted(public.items()))}".encode()).hexdigest() + ".json")
        if cache.exists():
            return json.loads(cache.read_text(encoding="utf-8"))
        url = f"{endpoint}?{urlencode(sorted(params.items()))}"
        data = self._fetch(url, {"User-Agent": USER_AGENT, "Accept": "application/json", **(headers or {})})
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data

    def _fetch(self, url: str, headers: dict[str, str]) -> dict[str, Any]:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            if self.requests_made >= self.max_requests:
                raise BudgetExceeded(f"--max-requests={self.max_requests} doldu")
            self.sleep(self.delay)
            self.requests_made += 1
            status, response_headers, body = self.transport(url, headers)
            if status == 200:
                try:
                    data = json.loads(body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    raise ApiError(f"gecersiz JSON: {error}") from error
                if not isinstance(data, dict):
                    raise ApiError("JSON nesne degil")
                return data
            if status not in (429, 503):
                raise ApiError(f"HTTP {status}")
            if attempt < MAX_ATTEMPTS:
                self.sleep(_retry_delay(response_headers, attempt))
        raise ResumeLater(f"{MAX_ATTEMPTS} deneme sonrasi hala 429/503; sonra devam edin")


def fold(text: Any) -> str:
    raw = unicodedata.normalize("NFKD", str(text or ""))
    return re.sub(r"[^a-z0-9]+", " ", "".join(c for c in raw if not unicodedata.combining(c)).lower()).strip()


def name_tokens(name: str) -> list[str]:
    return [t for t in fold(name).split() if len(t) >= 4 and t not in GENERIC]


def matches_name(plan: dict[str, Any], text: str) -> bool:
    """Ayirt edici sozcuklerin en az yarisi metinde gecmeli (alias da kabul). Tek sozcuklu adda (Jones Art Gallery ->
    jones: "Burne Jones" tablosu) sehir adi da metinde gecmeli."""
    haystack = f" {fold(text)} "
    city = fold(plan.get("municipality"))
    for name in [plan.get("name", ""), *(plan.get("aliases") or [])]:
        tokens = name_tokens(str(name))
        if not tokens or sum(f" {t} " in haystack for t in tokens) * 2 < len(tokens):
            continue
        if len(tokens) > 1 or not city or f" {city} " in haystack:
            return True
    return False


def usable_image(url: Any) -> bool:
    parts = urlsplit(str(url or ""))
    return (parts.scheme == "https" and bool(parts.hostname) and not parts.username
            and Path(parts.path).suffix.lower() in IMAGE_EXTENSIONS)


def cc_license(kind: str, version: str = "") -> tuple[str, str] | None:
    """('CC BY 2.0', adres) ya da None; yalniz BY, BY-SA, CC0, PDM (NC/ND yok)."""
    kind = kind.lower()
    if kind == "cc0":
        return "CC0 1.0", CC0_URL
    if kind == "pdm":
        return "Public domain", ""
    if kind in ("by", "by-sa") and re.fullmatch(r"\d\.\d", version or ""):
        return f"CC {kind.upper()} {version}", f"https://creativecommons.org/licenses/{kind}/{version}/"
    return None


def europeana_license(url: str) -> tuple[str, str] | None:
    match = re.match(r"https?://creativecommons\.org/licenses/(by|by-sa)/(\d\.\d)/?", url or "")
    if match:
        return cc_license(match.group(1), match.group(2))
    if "publicdomain/zero" in (url or ""):
        return cc_license("cc0")
    return cc_license("pdm") if "publicdomain/mark" in (url or "") else None


def html_escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def record(plan: dict[str, Any], provider: str, **f: Any) -> dict[str, Any]:
    """Commons imageinfo bicimli satir (photo_candidates.normalize_imageinfo okur)."""
    artist = html_escape(f["creator"] or "")
    if f.get("creator_url") and artist:
        artist = f'<a href="{html_escape(f["creator_url"])}">{artist}</a>'
    label, license_url = f["license"]
    meta = {"ObjectName": f["title"], "LicenseShortName": label, "LicenseUrl": license_url, "UsageTerms": label,
            "Artist": artist, "Credit": provider, "ImageDescription": f.get("description", ""),
            "AttributionRequired": "true"}
    if f.get("date"):
        meta["DateTimeOriginal"] = f["date"]
    info = {"url": f["image_url"], "descriptionurl": f["page_url"], "width": f.get("width"), "height": f.get("height"),
            "mime": f.get("mime"), "provider": provider, "extmetadata": {k: {"value": v} for k, v in meta.items() if v}}
    title = f["title"] or "adsiz"
    return {"entry_id": plan["entry_id"], "query_kind": f"alt:{f['source']}", "title": f"{provider}: {title}"[:200],
            "imageinfo": info}


def queries(plan: dict[str, Any]) -> list[str]:
    name, city = str(plan.get("name") or "").strip(), str(plan.get("municipality") or "").strip()
    return [q for q in dict.fromkeys([f"{name} {city}".strip(), name]) if q]


def search_openverse(fetch: Fetcher, plan: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {os.environ['OPENVERSE_TOKEN']}"} if os.environ.get("OPENVERSE_TOKEN") else {}
    found: list[dict[str, Any]] = []
    for query in queries(plan):
        data = fetch.get("https://api.openverse.org/v1/images/", {
            "q": query, "license": "by,by-sa,cc0,pdm", "page_size": "20", "mature": "false"}, headers)
        for item in data.get("results") or []:
            if str(item.get("source") or item.get("provider") or "").lower() in WIKIMEDIA_SOURCES:
                continue
            lic = cc_license(str(item.get("license") or ""), str(item.get("license_version") or ""))
            tags = [str(t.get("name") or "") for t in item.get("tags") or [] if isinstance(t, dict)]
            text = " ".join([str(item.get("title") or ""), *tags])
            if not lic or not usable_image(item.get("url")) or not item.get("foreign_landing_url") or not matches_name(plan, text):
                continue
            found.append(record(plan, str(item.get("source") or item.get("provider") or "openverse").capitalize(),
                                source="openverse", title=str(item.get("title") or ""), image_url=item["url"],
                                page_url=item["foreign_landing_url"], width=item.get("width"), height=item.get("height"),
                                mime=f"image/{str(item.get('filetype') or 'jpeg').replace('jpg', 'jpeg')}", license=lic,
                                creator=str(item.get("creator") or ""), creator_url=item.get("creator_url"),
                                description=text))
        if len(found) >= limit:
            break
    return found[:limit]


def search_smithsonian(fetch: Fetcher, plan: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    key = os.environ.get("SMITHSONIAN_API_KEY", "DEMO_KEY")
    found: list[dict[str, Any]] = []
    for query in queries(plan):
        data = fetch.get("https://api.si.edu/openaccess/api/v1.0/search", {"q": query, "rows": "20", "api_key": key})
        for row in (data.get("response") or {}).get("rows") or []:
            desc = (row.get("content") or {}).get("descriptiveNonRepeating") or {}
            title = str((desc.get("title") or {}).get("content") or row.get("title") or "")
            for media in (desc.get("online_media") or {}).get("media") or []:
                if media.get("type") != "Images" or (media.get("usage") or {}).get("access") != "CC0":
                    continue
                if not usable_image(media.get("content")) or not matches_name(plan, title):
                    continue
                found.append(record(plan, "Smithsonian Open Access", source="smithsonian", title=title,
                                    image_url=media["content"], page_url=desc.get("record_link") or row.get("url", ""),
                                    license=cc_license("cc0"), creator=str(desc.get("data_source") or "Smithsonian")))
        if len(found) >= limit:
            break
    return [r for r in found if r["imageinfo"]["descriptionurl"].startswith("http")][:limit]


def search_europeana(fetch: Fetcher, plan: dict[str, Any], limit: int) -> list[dict[str, Any]]:
    key = os.environ.get("EUROPEANA_API_KEY", "api2demo")
    found: list[dict[str, Any]] = []
    for query in queries(plan):
        data = fetch.get("https://api.europeana.eu/record/v2/search.json", {
            "wskey": key, "query": query, "rows": "20", "media": "true", "reusability": "open", "profile": "standard"})
        for item in data.get("items") or []:
            lic = europeana_license((item.get("rights") or [""])[0])
            image = (item.get("edmIsShownBy") or [""])[0]
            title = str((item.get("title") or [""])[0])
            page = str(item.get("guid") or "")
            if not lic or not usable_image(image) or not page.startswith("http") or not matches_name(plan, title):
                continue
            found.append(record(plan, "Europeana", source="europeana", title=title, image_url=image, page_url=page,
                                license=lic, creator=str((item.get("dcCreator") or [item.get("dataProvider", [""])[0]])[0])))
        if len(found) >= limit:
            break
    return found[:limit]


SOURCES: dict[str, Callable[[Fetcher, dict[str, Any], int], list[dict[str, Any]]]] = {
    "openverse": search_openverse, "smithsonian": search_smithsonian, "europeana": search_europeana}
DEFAULT_SOURCES = ("openverse", "smithsonian")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def candidate_counts(rows: list[dict[str, Any]]) -> tuple[dict[str, int], set[tuple[str, str]]]:
    """Mekan basina benzersiz aday sayisi ve (entry_id, kaynak) olarak daha once denenmis ikinci kaynaklar."""
    pages: dict[str, set[str]] = {}
    tried: set[tuple[str, str]] = set()
    for row in rows:
        entry = str(row.get("entry_id") or "")
        pages.setdefault(entry, set()).add(str((row.get("imageinfo") or {}).get("descriptionurl") or row.get("title")))
        kind = str(row.get("query_kind") or "")
        if kind.startswith("alt:"):
            tried.add((entry, kind[4:]))
    return {entry: len(urls) for entry, urls in pages.items()}, tried


def new_rows(rows: list[dict[str, Any]], seen: set[tuple[str, str]]) -> list[dict[str, Any]]:
    """Ayni kaynak sayfasi ayni mekana iki kez girmez (iki sorgu ayni sonucu verebilir); seen yerinde buyur."""
    fresh = []
    for row in rows:
        key = (str(row["entry_id"]), str(row["imageinfo"]["descriptionurl"]))
        if key not in seen:
            seen.add(key)
            fresh.append(row)
    return fresh


def run(args: argparse.Namespace, transport: Transport = urllib_transport) -> int:
    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    unknown = [s for s in sources if s not in SOURCES]
    if unknown:
        print(f"HATA: bilinmeyen kaynak {unknown}; gecerli: {sorted(SOURCES)}", file=sys.stderr)
        return EXIT_USAGE
    plan = [p for p in read_jsonl(Path(args.plan)) if p.get("role") in ("venue", "district")]
    existing = read_jsonl(Path(args.search))
    counts, tried = candidate_counts(existing)
    fetch = Fetcher(transport, Path(args.cache_dir), args.max_requests, delay=args.delay)
    seen = {(str(r.get("entry_id")), str((r.get("imageinfo") or {}).get("descriptionurl"))) for r in existing}
    added: list[dict[str, Any]] = []
    per_source = {s: 0 for s in sources}
    failures = {s: 0 for s in sources}
    errors: list[str] = []
    stopped = ""
    try:
        for entry in plan:
            have = counts.get(entry["entry_id"], 0)
            for source in sources:
                if have >= args.min_per_venue:
                    break
                if (entry["entry_id"], source) in tried:
                    continue
                if failures[source] >= MAX_SOURCE_FAILURES:
                    continue
                try:
                    rows = new_rows(SOURCES[source](fetch, entry, args.per_source), seen)
                except ApiError as error:  # tek kaynagin hatasi digerlerini durdurmaz; 3 hatadan sonra o kaynak birakilir
                    failures[source] += 1
                    errors.append(f"{source}: {entry['entry_id']}: {error}")
                    continue
                added.extend(rows)
                per_source[source] += len(rows)
                have += len(rows)
    except (BudgetExceeded, ResumeLater) as error:
        stopped = str(error)
    if added:
        with Path(args.search).open("a", encoding="utf-8", newline="\n") as stream:
            for row in added:
                stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    final, _ = candidate_counts(existing + added)
    short = [e["entry_id"] for e in plan if final.get(e["entry_id"], 0) < args.min_per_venue]
    hosts = sorted({urlsplit(r["imageinfo"]["url"]).hostname for r in added})
    emit({"status": "stopped" if stopped else "ok", "stopped": stopped, "requests": fetch.requests_made,
          "added": len(added), "per_source": per_source, "entries_still_short": len(short), "short_sample": short[:10],
          "download_hosts": hosts, "source_errors": errors[:10], "search": str(args.search)})
    return EXIT_FINDINGS if stopped else EXIT_OK


def main(argv: list[str] | None = None) -> int:
    setup_utf8()
    p = argparse.ArgumentParser(description="Commons yetersizse ikinci kaynaklardan foto adayi ekler")
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--search", required=True, type=Path, help="commons_search ciktisi; yeni satirlar buna eklenir")
    p.add_argument("--sources", default=",".join(DEFAULT_SOURCES))
    p.add_argument("--min-per-venue", type=int, default=3)
    p.add_argument("--per-source", type=int, default=6)
    p.add_argument("--cache-dir", type=Path, default=Path("foto_alt_cache"))
    p.add_argument("--max-requests", type=int, default=400)
    p.add_argument("--delay", type=float, default=DEFAULT_DELAY)
    try:
        args = p.parse_args(argv)
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
