"""Wikidata SPARQL: Eindhoven sinirlarindaki koordinatli ogeler (mekan aday havuzu). Pilot is script'i.

Kullanim: python wikidata_aday.py <cikti.jsonl>
Tek sorgu, aciklayici User-Agent; sonuc onbellege (cikti yanina .raw.json) yazilir, ikinci calisma ag kullanmaz.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ENDPOINT = "https://query.wikidata.org/sparql"
USER_AGENT = "CorteqsCityToolkit/0.1 (content research; https://www.mediawiki.org/wiki/API:Etiquette)"
QUERY = """
SELECT ?item ?nl ?en ?coord ?site ?image ?cat ?nlwiki
       (GROUP_CONCAT(DISTINCT ?typeLabel; separator="|") AS ?types)
       (SAMPLE(?districtLabel) AS ?district) WHERE {
  ?item wdt:P131+ wd:Q9832 ; wdt:P625 ?coord .
  FILTER NOT EXISTS { ?item wdt:P576 ?dissolved }
  FILTER NOT EXISTS { ?item wdt:P5817 wd:Q56556915 }
  OPTIONAL { ?item rdfs:label ?nl FILTER(LANG(?nl)="nl") }
  OPTIONAL { ?item rdfs:label ?en FILTER(LANG(?en)="en") }
  OPTIONAL { ?item wdt:P856 ?site }
  OPTIONAL { ?item wdt:P18 ?image }
  OPTIONAL { ?item wdt:P373 ?cat }
  OPTIONAL { ?nlwiki schema:about ?item ; schema:isPartOf <https://nl.wikipedia.org/> }
  OPTIONAL { ?item wdt:P31 ?type . ?type rdfs:label ?typeLabel FILTER(LANG(?typeLabel)="en") }
  OPTIONAL { ?item wdt:P131 ?d . ?d rdfs:label ?districtLabel FILTER(LANG(?districtLabel)="nl") }
}
GROUP BY ?item ?nl ?en ?coord ?site ?image ?cat ?nlwiki
"""


def fetch(raw: Path) -> dict:
    if raw.exists():
        return json.loads(raw.read_text(encoding="utf-8"))
    url = ENDPOINT + "?" + urllib.parse.urlencode({"query": QUERY, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    raw.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return data


def main(out: str) -> int:
    out_path = Path(out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = fetch(out_path.with_suffix(".raw.json"))
    rows = []
    for b in data["results"]["bindings"]:
        v = {k: b[k]["value"] for k in b}
        lon, lat = v["coord"].removeprefix("Point(").removesuffix(")").split()
        rows.append({"qid": v["item"].rsplit("/", 1)[1], "name": v.get("nl") or v.get("en") or "", "name_en": v.get("en", ""),
                     "lat": round(float(lat), 6), "lon": round(float(lon), 6), "types": v.get("types", ""),
                     "district": v.get("district", ""), "website": v.get("site", ""), "has_image": bool(v.get("image")),
                     "commons_category": v.get("cat", ""), "nlwiki": v.get("nlwiki", "")})
    rows.sort(key=lambda r: r["name"].casefold())
    out_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"items": len(rows), "with_site": sum(1 for r in rows if r["website"]),
                      "with_image": sum(1 for r in rows if r["has_image"]),
                      "with_category": sum(1 for r in rows if r["commons_category"]), "out": str(out_path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
