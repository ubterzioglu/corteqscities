"""Foto turlarinin kapsamini sayar: kayit basina ikinci gozden gecmis kare (ok:true; verify yoksa beklemede).

Kullanim: python foto_kapsam.py <_is>
Okur: foto/venues.jsonl (kayitlar), foto/inceleme/selected_*.jsonl ve verify_*.jsonl.
Ayni Commons dosyasi iki kayda verilmisse yalniz ilk kayitta sayilir. Tek satir JSON + liste.
"""
import collections
import json
import pathlib
import sys

work = pathlib.Path(sys.argv[1])
inc = work / "foto" / "inceleme"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


kayit = {r["entry_id"]: r for r in jl(work / "foto" / "venues.jsonl") if r.get("role") in ("venue", "district")}
ok, bekle = {}, set()
for f in sorted(inc.glob("verify_*.jsonl")):
    for r in jl(f):
        ok[r["key"]] = bool(r.get("ok"))
say, dosya = collections.Counter(), set()
for f in sorted(inc.glob("selected_*.jsonl")):
    for r in jl(f):
        k = r["key"]
        if k not in ok:
            bekle.add(k)
            continue
        if not ok[k]:
            continue
        cf = k.split("|", 1)[-1]
        if cf in dosya:
            continue
        dosya.add(cf)
        say[r["entry_id"]] += 1
sifir = sorted(e for e in kayit if say[e] == 0)
az = sorted(e for e in kayit if 0 < say[e] < 3)
print(json.dumps({"kayit": len(kayit), "kare_ok": sum(say.values()), "mekan_kare": sum(v for e, v in say.items() if kayit.get(e, {}).get("role") == "venue"),
                  "bekleyen": len(bekle), "sifir": len(sifir), "az": len(az)}, ensure_ascii=False))
print("SIFIR:", ", ".join(f"{e.split(':')[1]}({kayit[e].get('role')[0]})" for e in sifir))
print("AZ:", ", ".join(f"{e.split(':')[1]}={say[e]}" for e in az))
