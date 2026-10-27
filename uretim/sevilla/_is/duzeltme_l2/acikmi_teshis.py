"""Açık-mı kapısının bulguları için teşhis: bulgunun satırı (durum, eylem, kanıt adresi), kanıt adresinin kaynak kimliği,
o kaynağın pakette başka yerde kullanılıp kullanılmadığı, kartın source_ids'i ve notu (tarihli cümle var mı).

Kullanım: python -I -X utf8 acikmi_teshis.py <WORK_is> <acik_mi_rapor.json>
"""
import json
import re
import sys
from pathlib import Path

IS, RAPOR = Path(sys.argv[1]), Path(sys.argv[2])


def jl(p: Path) -> list:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


kd = {r["source_id"]: r for r in jl(IS / "kaynak_dizini.jsonl")}
url2src = {str(r.get("url", "")).strip(): s for s, r in kd.items()}
kayit, kullanan = {}, {}
for p in (IS / "data" / "parcalar").glob("*.jsonl"):
    for r in jl(p):
        sids = [s.strip() for s in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if s.strip()]
        if r.get("entry_id"):
            kayit[r["entry_id"]] = (p.name, r)
        for s in sids:
            kullanan.setdefault(s, set()).add(r.get("entry_id") or r.get("term_id") or r.get("route_id"))
        if p.name.startswith("Bağlantılar"):
            s = url2src.get(str(r.get("url", "")).strip())
            if s:
                kullanan.setdefault(s, set()).add("link:" + str(r.get("entry_id")))
rapor = json.loads(RAPOR.read_text(encoding="utf-8"))
items = rapor.get("items") or next((v for v in rapor.values() if isinstance(v, list) and v and isinstance(v[0], dict) and "code" in v[0]), [])
if not items:
    print("rapor anahtarları:", sorted(rapor))
for it in items:
    eid = it["entry_id"]
    out = {"code": it["code"], "entry": eid.replace("sevilla:", ""), "where": it["where"]}
    if it["code"] != "tarama_yok":
        dosya, satir = it["where"].split(":")
        row = jl(IS / "acik_mi" / dosya)[int(satir) - 1]
        url = str(row.get("kanit_url") or row.get("url") or row.get("kanit", {}).get("url") if isinstance(row.get("kanit"), dict) else row.get("kanit_url") or row.get("url") or "")
        out.update({"satir_anahtarlar": sorted(row)[:14], "durum": row.get("durum"), "eylem": row.get("eylem"), "sonuc": row.get("sonuc"),
                    "kanit_url": url[:110], "kanit_kaynak": url2src.get(url.strip()), "kanit_kaynak_kullanan": sorted(kullanan.get(url2src.get(url.strip()), set()))[:4]})
    if eid in kayit:
        f, r = kayit[eid]
        out.update({"kart_dosya": f, "source_ids": r.get("source_ids"),
                    "not_tarihli": bool(re.search(r"\b20\d\d itibar", str(r.get("summary", "")) + " " + str(r.get("note", ""))))})
    print(json.dumps(out, ensure_ascii=False))
