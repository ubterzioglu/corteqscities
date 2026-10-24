"""k04.py: K04 sabitleme - baslangic ve bitis envanterinin SHA listesi karsilastirmasi (Python ile; Turkce yol guvenli).
Kullanim: python -I -X utf8 k04.py <OUT> <PKG>"""
import hashlib
import json
import sys
from pathlib import Path

out, pkg = Path(sys.argv[1]), Path(sys.argv[2])


def lines(name):
    data = json.loads((out / name).read_text(encoding="utf-8"))
    return sorted(f"{f['path']} {f['sha256']}" for f in data["files"])


a, b = lines("dosya-envanteri.json"), lines("_dosya-envanteri-son.json")
pa = {l.rsplit(" ", 1)[0]: l.rsplit(" ", 1)[1] for l in a}
pb = {l.rsplit(" ", 1)[0]: l.rsplit(" ", 1)[1] for l in b}
xlsx = "CITY-039_eindhoven_v001.xlsx"
summ = (pkg / "Teslimler" / "TESLIM_OZETI.txt").read_text(encoding="utf-8-sig").splitlines()
rend = (out / "_render" / "TESLIM_OZETI.txt").read_text(encoding="utf-8-sig").splitlines()
pkg_inv = json.loads((pkg / "Teslimler" / "dosya-envanteri.json").read_text(encoding="utf-8"))
res = {
    "start_files": len(a), "end_files": len(b),
    "added": sorted(set(pb) - set(pa)), "removed": sorted(set(pa) - set(pb)),
    "changed": sorted(p for p in set(pa) & set(pb) if pa[p] != pb[p]),
    "sha_list_digest_start": hashlib.sha256("\n".join(a).encode("utf-8")).hexdigest(),
    "sha_list_digest_end": hashlib.sha256("\n".join(b).encode("utf-8")).hexdigest(),
    "xlsx_sha_start": pa.get(xlsx), "xlsx_sha_end": pb.get(xlsx),
    "k83_summary_line_diffs": [{"paket": x, "denetim": y} for x, y in zip(summ, rend) if x != y]
    + ([{"satir_sayisi": [len(summ), len(rend)]}] if len(summ) != len(rend) else []),
    "k83_path_diffs": sorted(set(f["path"] for f in pkg_inv["files"]) ^ set(pa)),
}
(out / "_analiz" / "k04-karsilastirma.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps(res, ensure_ascii=False))
