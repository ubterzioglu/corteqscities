"""Secilen mekanlarin kaynak durumunu cikarir: kabul (source_id) / ret (neden).

Kullanim: python secim_durum.py <_is> <selected.jsonl> <snap_klasoru> [<snap_klasoru> ...]
Yazar: <_is>/mekan/secim_durum.jsonl (mekan basina {slug, group, name, url, source_id|"" , ret}).
Tek satir JSON ozet basar. Cikis 0.
"""
import collections
import json
import pathlib
import sys


def jl(p: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in p.read_text(encoding="utf-8-sig").splitlines() if l.strip()] if p.is_file() else []


work = pathlib.Path(sys.argv[1])
secim = jl(pathlib.Path(sys.argv[2]))
harita, ret = {}, {}
for d in sys.argv[3:]:
    e = json.loads((work / d / "eklenen.json").read_text(encoding="utf-8"))
    harita.update(e.get("map", {}))
    for r in e.get("rejected", []):
        ret[r.get("url")] = r.get("reason") or r.get("neden") or json.dumps(r, ensure_ascii=False)[:200]
out, kabul, red = [], collections.Counter(), []
for s in secim:
    sid = harita.get(s["url"], "")
    satir = {"slug": s["slug"], "group": s["group"], "name": s.get("name"), "url": s["url"], "source_id": sid,
             "ret": "" if sid else ret.get(s["url"], "haritada yok")}
    out.append(satir)
    if sid:
        kabul[s["group"]] += 1
    else:
        red.append(f'{s["group"]} | {s.get("name")} | {satir["ret"][:120]}')
(work / "mekan" / "secim_durum.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
print(json.dumps({"kabul": sum(kabul.values()), "kabul_grup": dict(kabul), "ret": len(red)}, ensure_ascii=False))
for r in red:
    print(r)
