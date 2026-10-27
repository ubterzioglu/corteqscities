"""Sevilla son temizlik: tablao-el-arenal'i cikar; merge sonrasi kaynak sayisi 500'u gecerse iddiasiz kaynaklari dusur.

Kullanim: son_temizlik.py <yedek_klasoru> [--limit 500]
Kaynak dusurme kurali: hicbir iddianin dayanmadigi kaynak, kaydin baska kaynagi varsa kaydin source_ids'inden cikar
(en az kullanilan once). Degisiklikler _is\\denetim\\dis-d3_degisiklik.jsonl'e yazilir.
"""
import json, glob, sys, shutil, collections, subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\temp_private\corteqs\0000_newera")
W = ROOT / "uretim" / "sevilla" / "_is"
P = W / "data" / "parcalar"
LOG = W / "denetim" / "dis-d3_degisiklik.jsonl"
YED = Path(sys.argv[1]); LIMIT = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 500
TAB = "sevilla:tablao-el-arenal"
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")

def rj(p): return [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]
def wj(p, rows): open(p, "w", encoding="utf-8", newline="\n").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
def log(e, alan, eski, yeni, bid, g):
    open(LOG, "a", encoding="utf-8").write(json.dumps(dict(entry_id=e, alan=alan, eski=eski, yeni=yeni, bulgu_claim_id=bid, gerekce=g, alinti=""), ensure_ascii=False) + "\n")

if YED.exists(): shutil.rmtree(YED)
shutil.copytree(P, YED / "parcalar"); shutil.copytree(W / "claims", YED / "claims")

removed = collections.Counter()
for f in glob.glob(str(P / "Mekânlar.*.jsonl")) + glob.glob(str(P / "Bağlantılar.*.jsonl")) + glob.glob(str(W / "claims" / "*.jsonl")):
    rows = rj(f); keep = [r for r in rows if r.get("entry_id") != TAB]
    if len(keep) != len(rows): wj(f, keep); removed[Path(f).name] += len(rows) - len(keep)
for f in glob.glob(str(P / "Rotalar.*.jsonl")) + glob.glob(str(P / "SayfaAlanları.*.jsonl")):
    if TAB.split(":")[1] in open(f, encoding="utf-8").read(): print("UYARI: tablao kullaniliyor:", f)
if removed: log(TAB, "kayit", "Mekânlar satırı", "", "dis:S14", "Tek karesi kimliği belirsiz flamenko gösterisiydi; fotoğraflı yedek mekânla değiştirildi (Barış onayı 26.10.2026)")
print("tablao cikarilan satir:", dict(removed))

def owners_and_claims():
    claims = collections.Counter(json.loads(l).get("source_id") for f in glob.glob(str(W / "claims" / "*.jsonl")) for l in open(f, encoding="utf-8") if l.strip())
    owners = collections.defaultdict(list)
    for f in glob.glob(str(P / "*.jsonl")):
        for r in rj(f):
            ids = r.get("source_ids")
            if isinstance(ids, str): ids = [x.strip() for x in ids.replace(",", ";").split(";") if x.strip()]
            for s in ids or []: owners[s].append((f, r))
    return claims, owners

r = subprocess.run([PY, "-X", "utf8", str(ROOT / "corteqs-skills" / "toolkit" / "scripts" / "merge_package.py"), str(W), "--city-id", "sevilla",
                    "--bbox=" + open(W / "ortam.ps1", encoding="utf-8").read().split("$BBOX = '")[1].split("'")[0]], capture_output=True, text=True, encoding="utf-8")
used = json.loads(r.stdout.strip().splitlines()[-1]).get("sources_used")
print("sources_used:", used)
over = (used or 0) - LIMIT
if over > 0:
    claims, owners = owners_and_claims()
    def n_src(rec):
        ids = rec.get("source_ids"); return len(ids if isinstance(ids, list) else [x for x in str(ids).replace(",", ";").split(";") if x.strip()])
    cand = sorted((s for s, o in owners.items() if claims[s] == 0 and all(n_src(rec) >= 2 for _, rec in o)), key=lambda s: len(owners[s]))
    drop = cand[:over]
    if len(drop) < over: print(f"UYARI: yalniz {len(drop)} kaynak dusurulebilir, {over} gerekiyordu")
    for f in {f for s in drop for f, _ in owners[s]}:
        rows = rj(f)
        for rec in rows:
            ids = rec.get("source_ids"); lst = ids if isinstance(ids, list) else [x.strip() for x in str(ids or "").replace(",", ";").split(";") if x.strip()]
            new = [x for x in lst if x not in drop]
            if len(new) != len(lst):
                rid = rec.get("entry_id") or rec.get("route_id") or rec.get("field_id") or rec.get("term_id") or rec.get("step_id")
                log(rid, "source_ids", ";".join(lst), ";".join(new), "kapasite:Kaynaklar500", "Sözleşme sınırı 500; iddiası olmayan, kaydın başka kaynağı var")
                rec["source_ids"] = new if isinstance(ids, list) else ";".join(new)
        wj(f, rows)
    print("dusurulen kaynak:", drop)
