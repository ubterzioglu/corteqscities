"""Yanit parcalarinin ilk tur denetim girdilerini hazirlar (ana dongu; kural 6 sayimlari dahil).

Kullanim: python hazirla_denetim.py <_is> <parca1,parca2,...>
Onkosul: denetim_girdi.py --tur ilk --parca <p> calismis (denetim/<p>-ilk_kartlar.jsonl) ve KUR blogu
(text_quality.json, uyari_tarama.json, birlestir_rapor.json, claim_check_number.json) guncel.
Yazar: denetim/<p>_kartlar.jsonl + .txt (kapsam: sehir kartlari + ulke_denetim_kapsami 'audit'),
       yazar/<p>_eksikler.json, denetim/<p>_kur.json. Tek satir JSON ozet basar.
Cikis: 0 tamam, 1 bir parcanin girdisi eksik, 2 kullanim hatasi.
"""
import json
import pathlib
import sys


def jl(p: pathlib.Path) -> list[dict]:
    if not p.is_file():
        return []
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def js(p: pathlib.Path, varsayilan):
    return json.loads(p.read_text(encoding="utf-8-sig")) if p.is_file() else varsayilan


def bul(nesne, idler: set[str], yol: str = "") -> list[dict]:
    """Rapor icinde kimliklerden birini anan her yaprak sozlugu toplar (bicimden bagimsiz)."""
    out = []
    if isinstance(nesne, dict):
        metin = json.dumps(nesne, ensure_ascii=False)
        if len(metin) < 4000 and any(i in metin for i in idler) and not any(isinstance(v, (dict, list)) and len(json.dumps(v, ensure_ascii=False)) > 400 for v in nesne.values()):
            return [{"yer": yol, **nesne}]
        for k, v in nesne.items():
            out += bul(v, idler, f"{yol}.{k}" if yol else str(k))
    elif isinstance(nesne, list):
        for i, v in enumerate(nesne):
            out += bul(v, idler, f"{yol}[{i}]")
    return out


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    work = pathlib.Path(sys.argv[1])
    parcalar = [p for p in sys.argv[2].split(",") if p]
    den = work / "denetim"
    kapsam = set(js(work / "ulke_denetim_kapsami.json", {}).get("audit", []))
    gaps = js(work / "kesif" / "gaps.json", {})
    ilk5 = js(work / "yazar" / "ilk5.json", {})
    donus = {}
    for f in (work / "yazar").glob("donus_*.jsonl"):
        for r in jl(f):
            donus[str(r.get("topic_id", "")).split(":")[-1]] = r
    tq = js(work / "text_quality.json", {})
    uy = js(work / "uyari_tarama.json", {})
    br = js(work / "birlestir_rapor.json", {})
    ccn = js(work / "claim_check_number.json", {})
    ozet, kod = {}, 0
    for p in parcalar:
        src = den / f"{p}-d1_kartlar.jsonl"
        satir = jl(src)
        if not satir:
            ozet[p] = {"hata": f"{src.name} yok ya da bos"}
            kod = 1
            continue
        secili = [r for r in satir if int(r.get("order") or 0) < 9000 or r.get("entry_id") in kapsam]
        hedef = den / f"{p}_kartlar.jsonl"
        hedef.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in secili), encoding="utf-8")
        parts = [f"===== KART {i}/{len(secili)}: {r.get('entry_id')} =====\n" + json.dumps(r, ensure_ascii=False, indent=1)
                 for i, r in enumerate(secili, 1)]
        hedef.with_suffix(".txt").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
        src.unlink()
        idler = {r.get("entry_id") for r in satir if r.get("entry_id")}
        claim_ids = {c.get("claim_id") for c in jl(work / "claims" / f"{p}.jsonl") if c.get("claim_id")}
        d = donus.get(p, {})
        cevapsiz = [q for q, ok in zip(ilk5.get(p, []), d.get("ilk5_covered", [])) if ok is False]
        eksik = {"yazar_gaps": d.get("gaps", []), "kesif_gaps": gaps.get(p, []), "ilk5_cevapsiz": cevapsiz,
                 "not": "Her madde icin resmi derin sayfa ara; bulamadigini open'a yaz. Uydurma yok."}
        (work / "yazar" / f"{p}_eksikler.json").write_text(json.dumps(eksik, ensure_ascii=False, indent=1), encoding="utf-8")
        olcum = ("address.items", "address.labels", "address.records")
        kur = {"text_quality": [x for x in bul(tq, idler) if not str(x.get("yer", "")).startswith(olcum)],
               "uyari_tarama": [x for x in bul(uy, idler) if not str(x.get("yer", "")).startswith(("records", "items"))],
               "birlestir": [x for x in bul(br, idler | claim_ids | {f"claims/{p}", f"claims\\{p}", f".{p}.jsonl"})],
               "claim_check_number_kalan": [x for x in bul(ccn, claim_ids) if str(x.get("status", x.get("sonuc", ""))).lower() not in ("supported", "ok")]}
        (den / f"{p}_kur.json").write_text(json.dumps(kur, ensure_ascii=False, indent=1), encoding="utf-8")
        ozet[p] = {"kart_kapsam": len(secili), "sehir": sum(int(r.get("order") or 0) < 9000 for r in secili),
                   "ulke_audit": sum(int(r.get("order") or 0) >= 9000 for r in secili),
                   "defter": sum(len(r.get("iddialar") or []) for r in secili),
                   "eksik": len(eksik["yazar_gaps"]) + len(eksik["kesif_gaps"]) + len(cevapsiz),
                   "kur": {k: len(v) for k, v in kur.items()}}
    print(json.dumps(ozet, ensure_ascii=False))
    return kod


sys.exit(main())
