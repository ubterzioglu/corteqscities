"""Mekan secim dosyalarini birlestirir ve dogrular (ana dongu, kural 6).

Kullanim: python secim_birlestir.py <_is> <cikti.jsonl> [--yedek-dahil] [--haric <selected.jsonl> ...]
secim_*.jsonl okunur; ayni slug ya da ayni dolu qid ikinci kez gelirse atilir (--haric dosyalarindakiler de).
Alan dogrulamasi: url https, must_contain bos degil, group gecerli, setting gecerli, koordinat kutuda, slug bicimi.
Tek satir JSON ozet basar. Cikis: 0 tamam, 1 bulgu var (satirlar yine yazilir, bulgulu satir atilir).
"""
import collections
import json
import pathlib
import re
import sys

GRUPLAR = {"Müzeler", "Sanat ve sergiler", "Sahne ve müzik", "Spor", "Doğa ve açık hava",
           "Çocuklarla keşif", "Yeme ve içme", "Tarih ve mimari"}
SETTING = {"Kapalı alan", "Açık hava", "Karma"}
LAT0, LAT1, LON0, LON1 = 36.57, 36.87, -4.60, -4.28
SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{1,59}$")


def jl(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


def main() -> int:
    work = pathlib.Path(sys.argv[1])
    out = pathlib.Path(sys.argv[2])
    yedek_dahil = "--yedek-dahil" in sys.argv
    haric = [pathlib.Path(a) for a in sys.argv[sys.argv.index("--haric") + 1:]] if "--haric" in sys.argv else []
    kart_slug = set()
    for f in (work / "data" / "parcalar").glob("Yanıtlar.*.jsonl"):
        kart_slug |= {r.get("slug") for r in jl(f)}
    gorulen_slug, gorulen_qid = set(), set()
    for h in haric:
        for r in jl(h):
            gorulen_slug.add(r.get("slug"))
            if r.get("qid"):
                gorulen_qid.add(r["qid"])
    secilen, bulgu, atilan = [], [], collections.Counter()
    dosyalar = sorted((work / "mekan").glob("secim_*.jsonl"), key=lambda p: p.name)
    for f in dosyalar:
        for r in jl(f):
            if r.get("rol") == "yedek" and not yedek_dahil:
                atilan["yedek"] += 1
                continue
            neden = []
            if not str(r.get("url", "")).startswith("https://"):
                neden.append("url")
            if not r.get("must_contain"):
                neden.append("must_contain")
            if r.get("group") not in GRUPLAR:
                neden.append("group")
            if r.get("setting") not in SETTING:
                neden.append("setting")
            if not SLUG.match(str(r.get("slug", ""))) or r.get("entry_id") != f"malaga:{r.get('slug')}":
                neden.append("slug")
            lat, lon = r.get("lat"), r.get("lon")
            if lat not in ("", None) and not (isinstance(lat, (int, float)) and LAT0 <= lat <= LAT1 and LON0 <= lon <= LON1):
                neden.append("koordinat")
            if r.get("slug") in kart_slug:
                neden.append("slug_kartla_cakisiyor")
            if r.get("slug") in gorulen_slug or (r.get("qid") and r["qid"] in gorulen_qid):
                atilan["tekrar"] += 1
                continue
            if neden:
                bulgu.append({"dosya": f.name, "slug": r.get("slug"), "neden": neden})
                atilan["bulgu"] += 1
                continue
            gorulen_slug.add(r["slug"])
            if r.get("qid"):
                gorulen_qid.add(r["qid"])
            r.setdefault("title", r.get("name", ""))
            r.setdefault("lang", "es")
            secilen.append(r)
    out.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in secilen), encoding="utf-8")
    grup = collections.Counter(r["group"] for r in secilen)
    print(json.dumps({"dosya": len(dosyalar), "secilen": len(secilen), "per_group": dict(grup),
                      "koordinatsiz": sum(r.get("lat") in ("", None) for r in secilen),
                      "fotolu_kategori": sum(bool(r.get("commons_category")) for r in secilen),
                      "atilan": dict(atilan), "bulgu": bulgu}, ensure_ascii=False))
    return 1 if bulgu else 0


sys.exit(main())
