"""d13 mini denetim girdisi: d12 doğrulayıcısının hatali_duzeltme/eksik_kalan işaretlediği kayıtlar ile verilen ek
kayıtlar (ör. açık-mı uygulama editörünün değiştirdikleri). Parça başına denetim_girdi --tur d13 çalıştırır.
Önce d13 dosyası var mı bakar (tur adı çakışmasın); varsa çıkış 2.

Kullanım: python -I -X utf8 d13_girdi.py <WORK_is> <TK> [--ek parca:entry_id,parca:entry_id] [--bak]
--bak: yalnız listeyi yazar, denetim_girdi çalıştırmaz.
"""
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

IS, TK = Path(sys.argv[1]), Path(sys.argv[2])
DEN = IS / "denetim"
BAK = "--bak" in sys.argv
ek = sys.argv[sys.argv.index("--ek") + 1].split(",") if "--ek" in sys.argv else []
if not BAK and list(DEN.glob("*-d13_*.jsonl")):
    sys.exit("d13 dosyaları zaten var; tur adı çakışması")
hedef = defaultdict(set)
for p in DEN.glob("*-d12_dogrulama.jsonl"):
    parca = p.name[: -len("-d12_dogrulama.jsonl")]
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            if r.get("sonuc") in ("hatali_duzeltme", "eksik_kalan"):
                hedef[parca].add(r["entry_id"])
for x in ek:
    parca, eid = x.split(":", 1)
    hedef[parca].add(eid)
# doğrulama turu ve kural 8 değişiklikleri; kapasite doğrulayıcısının görmediği kapasite değişiklikleri
kap_dog = set()
kd_path = DEN / "kapasite-d12_dogrulama.jsonl"
if kd_path.exists():
    kap_dog = {json.loads(l)["entry_id"] for l in kd_path.read_text(encoding="utf-8").splitlines() if l.strip()}
for p in DEN.glob("*-d12_degisiklik.jsonl"):
    parca = p.name[: -len("-d12_degisiklik.jsonl")]
    for l in p.read_text(encoding="utf-8").splitlines():
        if not l.strip():
            continue
        r = json.loads(l)
        b = str(r.get("bulgu_claim_id"))
        if b in ("dogrulama", "kural8") or (b == "kapasite" and r.get("entry_id") not in kap_dog):
            hedef[parca].add(r["entry_id"])
# kapasite doğrulamasının parçası "kapasite": kaydın gerçek parçasını data/parcalar'dan bul
if "kapasite" in hedef:
    yer = {}
    for p in (IS / "data" / "parcalar").glob("*.jsonl"):
        for l in p.read_text(encoding="utf-8").splitlines():
            if l.strip():
                r = json.loads(l)
                if r.get("entry_id") and "action_id" not in r and "photo_id" not in r:
                    yer[r["entry_id"]] = p.name.split(".")[1]
    for eid in hedef.pop("kapasite"):
        if eid in yer:
            hedef[yer[eid]].add(eid)
ozet = {}
for parca, ids in sorted(hedef.items()):
    ids = sorted(ids)
    if BAK:
        ozet[parca] = ids
        continue
    cp = subprocess.run([sys.executable, "-X", "utf8", str(TK / "denetim_girdi.py"), str(IS), "--city-id", "sevilla", "--tur", "d13",
                         "--parca", parca, "--kayit", ",".join(ids)], capture_output=True, text=True, encoding="utf-8")
    ozet[parca] = {"kayit": len(ids), "cikis": cp.returncode, "son": (cp.stdout.strip().splitlines() or [""])[-1][:200],
                   "hata": cp.stderr.strip()[-200:]}
print(json.dumps(ozet, ensure_ascii=False, indent=0))
