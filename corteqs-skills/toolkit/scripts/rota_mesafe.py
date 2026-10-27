"""Rota bacaklari: ardisik duraklar arasi kus ucusu ve gercek yaya rotasi (OSM, OSRM foot). Excel'i yalniz okur.

Sevilla dis denetimi (S10, B3 0/12): rotalarda gun/saat plani vardi ama "gercek yuruyus/ulasim mesafesi ya da suresi"
yoktu; haversine kus ucusudur, yuruyus degildir (yer-yazari). Bu arac her rota icin Rotalar.stop_entry_ids sirasiyla
Mekânlar koordinatlarindan bacak satiri yazar: kus_ucusu_m, yuruyus_m, yuruyus_dk, kaynak. Yanitlar --cache-dir'de
saklanir (ayni koordinat cifti yeniden sorulmaz); onbellekte olmayan istekler arasi en az 1 sn (FOSSGIS kullanim kurali).
Cikti JSONL (--out): bacak basina satir; kanit_teslim bunlari rota-plani-v7.jsonl'e ekler.
Cikis: 0 her bacak olculdu; 1 koordinatsiz durak ya da rotalanamayan bacak var (satirinda 'sorun'); 2 kullanim hatasi.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any, Callable

import openpyxl

import common

ENDPOINT = "https://routing.openstreetmap.de/routed-foot/route/v1/foot/{lon1},{lat1};{lon2},{lat2}?overview=false"
SOURCE = "OSRM yaya rotası, OpenStreetMap verisi (routing.openstreetmap.de, FOSSGIS)"
USER_AGENT = "corteqs-city-pack/1.0 (rota_mesafe; kural: saniyede en cok 1 istek)"
MIN_INTERVAL_S = 1.0
EARTH_RADIUS_M = 6371000.0
Transport = Callable[[str], dict[str, Any]]


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def urllib_transport(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310 - sabit https ucu
        return json.loads(response.read().decode("utf-8"))


def _coord(value: Any) -> float | None:
    try:
        return float(str(value).replace(",", "."))
    except (TypeError, ValueError):
        return None


def _ids(value: Any) -> list[str]:
    return [part.strip() for part in re.split(r"[\n,;]+", str(value or "")) if part.strip()]


def load_routes(xlsx: Path) -> tuple[list[tuple[str, list[str]]], dict[str, tuple[float | None, float | None, str]]]:
    """([(route_id, durak kimlikleri)], {entry_id: (enlem, boylam, baslik)})."""
    try:
        wb = openpyxl.load_workbook(xlsx, read_only=False)
    except Exception as exc:  # openpyxl bozuk dosyada farkli hatalar atar
        raise ValueError(f"xlsx okunamadi: {xlsx} ({type(exc).__name__})") from exc
    try:
        for sheet in ("Rotalar", "Mekânlar"):
            if sheet not in wb.sheetnames:
                raise ValueError(f"'{sheet}' sayfasi yok")
        routes = [(str(r["route_id"]), _ids(r.get("stop_entry_ids"))) for r in common.iter_records(wb["Rotalar"])
                  if r.get("route_id")]
        places = {str(r["entry_id"]): (_coord(r.get("latitude")), _coord(r.get("longitude")), str(r.get("title") or ""))
                  for r in common.iter_records(wb["Mekânlar"]) if r.get("entry_id")}
    finally:
        wb.close()
    return routes, places


class Router:
    """Onbellekli OSRM yaya sorgusu; onbellekte olmayan istekler arasi MIN_INTERVAL_S."""

    def __init__(self, cache_dir: Path, transport: Transport, sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self.cache_dir, self.transport, self.sleep, self.clock = cache_dir, transport, sleep, clock
        self.last: float | None = None
        self.requests = self.cache_hits = 0
        cache_dir.mkdir(parents=True, exist_ok=True)

    def route(self, a: tuple[float, float], b: tuple[float, float]) -> dict[str, Any]:
        url = ENDPOINT.format(lat1=f"{a[0]:.6f}", lon1=f"{a[1]:.6f}", lat2=f"{b[0]:.6f}", lon2=f"{b[1]:.6f}")
        path = self.cache_dir / f"{hashlib.sha256(url.encode()).hexdigest()[:24]}.json"
        if path.is_file():
            self.cache_hits += 1
            return json.loads(path.read_text(encoding="utf-8"))
        if self.last is not None and self.clock() - self.last < MIN_INTERVAL_S:
            self.sleep(MIN_INTERVAL_S - (self.clock() - self.last))
        try:
            data = self.transport(url)
        finally:
            self.last = self.clock()
            self.requests += 1
        if data.get("code") == "Ok" and data.get("routes"):
            path.write_text(json.dumps(data), encoding="utf-8")  # yalniz basarili yanit saklanir
        return data


def legs(routes: list[tuple[str, list[str]]], places: dict, router: Router, today: str) -> list[dict[str, Any]]:
    rows = []
    for route_id, stops in routes:
        for n, (src, dst) in enumerate(zip(stops, stops[1:]), start=1):
            a, b = places.get(src, (None, None, "")), places.get(dst, (None, None, ""))
            row: dict[str, Any] = {"route_id": route_id, "bacak": n, "from": src, "to": dst, "from_title": a[2],
                                   "to_title": b[2], "kaynak": SOURCE, "sorgu_tarihi": today}
            if None in (a[0], a[1], b[0], b[1]):
                rows.append({**row, "sorun": "koordinatsiz durak"})
                continue
            row["kus_ucusu_m"] = round(haversine_m(a[0], a[1], b[0], b[1]))
            try:
                data = router.route((a[0], a[1]), (b[0], b[1]))
            except Exception as exc:  # ag/JSON hatasi bacagi sorunlu yapar, digerleri surer
                rows.append({**row, "sorun": f"rota sorgusu: {type(exc).__name__}: {exc}"[:200]})
                continue
            if data.get("code") != "Ok" or not data.get("routes"):
                rows.append({**row, "sorun": f"rota yok: {data.get('code')}"})
                continue
            best = data["routes"][0]
            rows.append({**row, "yuruyus_m": round(best["distance"]), "yuruyus_dk": round(best["duration"] / 60)})
    return rows


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep, today: str | None = None) -> int:
    common.setup_utf8()
    parser = argparse.ArgumentParser(description="Rota bacaklari: kus ucusu + OSM yaya rotasi")
    parser.add_argument("--xlsx", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True, help="bacak JSONL (paket disinda; or. WORK\\_is\\rota_mesafe.jsonl)")
    parser.add_argument("--cache-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.xlsx.is_file():
        common.emit({"tool": "rota_mesafe", "error": f"xlsx yok: {args.xlsx}"})
        return common.EXIT_USAGE
    try:
        routes, places = load_routes(args.xlsx)
    except ValueError as exc:
        common.emit({"tool": "rota_mesafe", "error": str(exc)})
        return common.EXIT_USAGE
    router = Router(args.cache_dir, transport, sleep)
    rows = legs(routes, places, router, today or time.strftime("%Y-%m-%d"))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    problems = [r for r in rows if r.get("sorun")]
    measured = [r for r in rows if "yuruyus_m" in r]
    common.emit({"tool": "rota_mesafe", "routes": len(routes), "legs": len(rows), "measured": len(measured),
                 "problems": len(problems), "problem_examples": [(r["route_id"], r["bacak"], r["sorun"]) for r in problems[:5]],
                 "max_leg_walk_m": max((r["yuruyus_m"] for r in measured), default=0),
                 "requests": router.requests, "cache_hits": router.cache_hits, "out": str(args.out)})
    return common.EXIT_FINDINGS if problems else common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
