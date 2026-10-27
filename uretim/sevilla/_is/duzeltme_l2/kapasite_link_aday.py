"""İçerik kaybı olmadan boşaltılabilir kaynaklar: yalnız bir Bağlantılar satırının adresi olarak kullanılan (hiçbir
source_ids'te ve hiçbir iddiada geçmeyen) ve satırın kaydında başka (harita olmayan) bağlantı bulunan kaynaklar.
Satır silinirse kaynak sayımdan düşer. Yalnız okur; aday listesi duzeltme_l2/kapasite_link_aday.jsonl.

Kullanım: python -I -X utf8 kapasite_link_aday.py <WORK_is>
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IS = Path(sys.argv[1])
P = IS / "data" / "parcalar"


def jl(p: Path) -> list:
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


kd = {r["source_id"]: r for r in jl(IS / "kaynak_dizini.jsonl")}
url2src = {str(r.get("url", "")).strip(): s for s, r in kd.items()}
in_ids, in_claims = set(), set()
links = defaultdict(list)
for p in P.glob("*.jsonl"):
    if p.name.startswith("Bağlantılar"):
        for r in jl(p):
            links[r["entry_id"]].append((p.name, r))
        continue
    for r in jl(p):
        in_ids.update(s.strip() for s in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if s.strip())
for p in (IS / "claims").glob("*.jsonl"):
    in_claims.update(str(c.get("source_id")) for c in jl(p))
harita = re.compile(r"google\.[a-z.]+/maps|maps\.app|openstreetmap|maps\.apple", re.I)
rows = []
for eid, ls in links.items():
    for fname, r in ls:
        s = url2src.get(str(r.get("url", "")).strip())
        if not s or s in in_ids or s in in_claims:
            continue
        kullanan = [x for x in links.values() for _, y in x if url2src.get(str(y.get("url", "")).strip()) == s]
        if len(kullanan) != 1:
            continue
        diger = [y for _, y in ls if y is not r and not harita.search(str(y.get("url", "")))]
        if not diger:
            continue
        rows.append({"dosya": fname, "entry_id": eid, "action_id": r.get("action_id"), "label": r.get("label"), "url": r.get("url"),
                     "source_id": s, "kalan_baglanti": [(y.get("label"), y.get("url")) for y in diger]})
(IS / "duzeltme_l2" / "kapasite_link_aday.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
print(json.dumps({"aday": len(rows)}, ensure_ascii=False))
for r in rows[:25]:
    print(r["entry_id"].replace("sevilla:", ""), "|", r["label"], "|", str(r["url"])[:70], "| kalan:", [x[0] for x in r["kalan_baglanti"]])
