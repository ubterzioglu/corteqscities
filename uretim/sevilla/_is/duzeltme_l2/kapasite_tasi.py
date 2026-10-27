"""Kaynak kapasitesi (≤500), içerik kaybı olmadan: bir kaynağa dayanan HER iddianın birebir alıntısı, aynı kaydın başka bir
kaynağının paketteki metin kopyasında da geçiyorsa iddia o kaynağa taşınır ve ilk kaynak kayıtlardan çıkarılır.

Kullanım: python -I -X utf8 kapasite_tasi.py <WORK_is> <hedef> [--uygula]
Değişiklik kaydı: denetim/<parça>-d11_degisiklik.jsonl (bulgu_claim_id "kapasite").
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

IS, HEDEF = Path(sys.argv[1]), int(sys.argv[2])
UYGULA = "--uygula" in sys.argv
P = IS / "data" / "parcalar"


def norm(s):
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


kd = {}
for l in (IS / "kaynak_dizini.jsonl").read_text(encoding="utf-8").splitlines():
    if l.strip():
        r = json.loads(l)
        kd[r["source_id"]] = r
_text = {}


def text(s):
    if s not in _text:
        tf = (kd.get(s) or {}).get("text_file")
        p = Path(tf) if tf else None
        if p and not p.is_absolute():
            p = IS / tf
        _text[s] = norm(p.read_text(encoding="utf-8", errors="ignore")) if p and p.exists() else ""
    return _text[s]


recs, owner_srcs = {}, {}
users = defaultdict(set)
for p in sorted(P.glob("*.jsonl")):
    if p.name.startswith(("Fotoğraf", "Kanıtlar", "Bağlantılar", "Adımlar")):
        continue
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines()):
        if not l.strip():
            continue
        r = json.loads(l)
        if "source_ids" not in r:
            continue
        rid = r.get("entry_id") or r.get("term_id") or r.get("route_id") or r.get("field_id") or r.get("key")
        srcs = [s.strip() for s in re.split(r"[\n;|]", str(r.get("source_ids") or "")) if s.strip()]
        recs[(p.name, i)] = (rid, srcs)
        owner_srcs.setdefault(rid, set()).update(srcs)
        for s in srcs:
            users[s].add((p.name, i))
claims = []  # (file, line_idx, claim)
for p in sorted((IS / "claims").glob("*.jsonl")):
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines()):
        if l.strip():
            claims.append((p.name, i, json.loads(l)))
by_src = defaultdict(list)
for f, i, c in claims:
    by_src[c.get("source_id")].append((f, i, c))
aday = []
for s, us in users.items():
    cl = by_src.get(s, [])
    plan, ok = [], True
    for f, i, c in cl:
        q = norm(c.get("quote"))
        alts = [a for a in sorted(owner_srcs.get(c.get("entry_id"), set())) if a != s]
        alt = next((a for a in alts if q and q in text(a)), None)
        if not alt:
            ok = False
            break
        plan.append((f, i, alt))
    if not ok:
        continue
    if any(len(recs[u][1]) < 2 for u in us):
        continue
    turizm = 0 if re.search(r"visitasevilla|turismo|andalucia\.org", str((kd.get(s) or {}).get("url", "")), re.I) else 1
    aday.append(((turizm, len(cl)), s, us, plan))
aday.sort(key=lambda x: x[0])
secilen = aday[:HEDEF]
print(json.dumps({"aday": len(aday), "secilen": len(secilen), "tasinan_iddia": sum(len(x[3]) for x in secilen)}, ensure_ascii=False))
for _, s, us, plan in secilen:
    print(s, str((kd.get(s) or {}).get("url", ""))[:80], "| kayıt", len(us), "| iddia", len(plan))
if UYGULA and secilen:
    # iddiaları taşı
    cl_edit = defaultdict(dict)
    for _, s, us, plan in secilen:
        for f, i, alt in plan:
            cl_edit[f][i] = alt
    for f, edits in cl_edit.items():
        p = IS / "claims" / f
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, alt in edits.items():
            rows[i]["source_id"] = alt
            rows[i]["url"] = (kd.get(alt) or {}).get("url", rows[i].get("url"))
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    # kayıtlardan çıkar
    rec_edit = defaultdict(dict)
    for _, s, us, plan in secilen:
        for (fname, i) in us:
            rec_edit[fname].setdefault(i, set()).add(s)
    for fname, edits in rec_edit.items():
        p = P / fname
        rows = [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
        parca = fname.split(".")[1]
        log = []
        for i, ss in edits.items():
            eski = rows[i]["source_ids"]
            sep = "\n" if "\n" in str(eski) else ";"
            rows[i]["source_ids"] = sep.join(x.strip() for x in re.split(r"[\n;|]", str(eski)) if x.strip() and x.strip() not in ss)
            rid = rows[i].get("entry_id") or rows[i].get("term_id") or rows[i].get("route_id") or rows[i].get("field_id")
            log.append({"entry_id": rid, "alan": "source_ids", "eski": eski, "yeni": rows[i]["source_ids"], "bulgu_claim_id": "kapasite",
                        "gerekce": "Kaynaklar kapasitesi 500: bu kaynağa dayanan iddiaların birebir alıntısı kaydın öteki kaynağında da geçiyor; iddialar o kaynağa taşındı, kaynak çıkarıldı (" + ", ".join(sorted(ss)) + ").",
                        "alinti": ""})
        p.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        with (IS / "denetim" / f"{parca}-d11_degisiklik.jsonl").open("a", encoding="utf-8") as fh:
            for x in log:
                fh.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("uygulandı: iddia dosyası", len(cl_edit), "kayıt dosyası", len(rec_edit))
