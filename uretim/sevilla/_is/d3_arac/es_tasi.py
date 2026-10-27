"""Duzeltilmis ES paket kartlarini Sevilla'ya tasir (country_apply hedef varsa durdugu icin gecici klasorde calisir).

1. pack_merge: ulke\\ES + bolge\\andalucia -> gecici birlesik paket
2. country_apply apply: bos gecici is klasoru (Sevilla'nin kaynak_dizini/taslak kopyasi ile; ayni adres ayni kimligi alir)
3. Yalniz SLUGS kartlarinin Yanitlar/Baglantilar/claims satirlari Sevilla parcalarinda yer degistirir (order korunur);
   yeni kaynak_dizini/taslak satirlari ve snap dosyalari Sevilla'ya eklenir; ulke_kart_kaydi guncellenir.
"""
import json, shutil, subprocess, sys, glob, os
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(r"C:\temp_private\corteqs\0000_newera")
W = ROOT / "uretim" / "sevilla" / "_is"
PY = str(ROOT / ".venv" / "Scripts" / "python.exe")
DUP = ROOT / "corteqs-skills" / "deneme_ulke_paketi"
TMP = Path(sys.argv[1])
SLUGS = ["oturum-izni-yenileme", "aile-birlesimi-ile-oturum", "kalici-oturum-bes-yil", "arraigo-kok-salma-oturumu",
         "kar-amaci-gutmeyen-oturum-vizesi", "libro-de-familia-nedir", "registro-civil-ne-ise-yarar"]
IDS = {f"sevilla:{s}" for s in SLUGS}

def rj(p): return [json.loads(l) for l in open(p, encoding="utf-8-sig") if l.strip()]
def wj(p, rows): open(p, "w", encoding="utf-8", newline="\n").write("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
def run(args):
    r = subprocess.run([PY, "-X", "utf8", *map(str, args)], capture_output=True, text=True, encoding="utf-8")
    print(" ".join(map(str, args[:2])), "->", r.returncode, (r.stdout or r.stderr).strip()[-400:])
    if r.returncode >= 2: sys.exit(f"durdu: {args[0]}")

if TMP.exists(): shutil.rmtree(TMP)
work, pack = TMP / "is", TMP / "paket"
(work / "data" / "parcalar").mkdir(parents=True); (work / "claims").mkdir()
for name in ("kaynak_dizini.jsonl", "kaynak_taslak.jsonl"):
    shutil.copy2(W / name, work / name)
yedek = TMP / "sevilla_yedek"; yedek.mkdir()
for name in ("kaynak_dizini.jsonl", "kaynak_taslak.jsonl", "ulke_kart_kaydi.jsonl"):
    shutil.copy2(W / name, yedek / name)
shutil.copytree(W / "data" / "parcalar", yedek / "parcalar"); shutil.copytree(W / "claims", yedek / "claims")

run([DUP / "pack_merge.py", "--pack", ROOT / "ulke" / "ES", "--pack", ROOT / "ulke" / "ES" / "bolge" / "andalucia", "--out", pack])
run([DUP / "country_apply.py", "apply", work, "--pack", pack, "--city-id", "sevilla", "--city-name", "Sevilla",
     "--order-start", "9000", "--today", "2026-10-26"])

def by_id(rows, key): return {r[key]: r for r in rows if r.get(key)}
changed = {"Yanıtlar": 0, "Bağlantılar": 0, "claims": 0}
new_cards = {}
for f in glob.glob(str(work / "data" / "parcalar" / "Yanıtlar.*.jsonl")):
    for r in rj(f):
        if r["entry_id"] in IDS: new_cards[r["entry_id"]] = r
missing = IDS - set(new_cards)
if missing: sys.exit(f"pakette bulunamadi: {missing}")
for f in glob.glob(str(W / "data" / "parcalar" / "Yanıtlar.*.jsonl")):
    rows = rj(f); hit = False
    for i, r in enumerate(rows):
        if r["entry_id"] in IDS:
            new = dict(new_cards[r["entry_id"]]); new["order"] = r["order"]; new["featured"] = r.get("featured", new.get("featured"))
            rows[i] = new; hit = True; changed["Yanıtlar"] += 1
    if hit: wj(f, rows)

def replace_owned(pattern_city, pattern_tmp, key, owner_key, label):
    fresh = [r for f in glob.glob(str(pattern_tmp)) for r in rj(f) if r.get(owner_key) in IDS]
    for f in glob.glob(str(pattern_city)):
        rows = rj(f)
        owners = {r.get(owner_key) for r in rows if r.get(owner_key) in IDS}
        if not owners: continue
        keep = [r for r in rows if r.get(owner_key) not in owners]
        add = [r for r in fresh if r.get(owner_key) in owners]
        wj(f, keep + add); changed[label] += len(add)

replace_owned(W / "data" / "parcalar" / "Bağlantılar.*.jsonl", work / "data" / "parcalar" / "Bağlantılar.*.jsonl", "action_id", "entry_id", "Bağlantılar")
replace_owned(W / "claims" / "*.jsonl", work / "claims" / "*.jsonl", "claim_id", "entry_id", "claims")

for name in ("kaynak_dizini.jsonl", "kaynak_taslak.jsonl"):
    old = rj(W / name); have = {r.get("source_id") for r in old}
    extra = [r for r in rj(work / name) if r.get("source_id") not in have]
    wj(W / name, old + extra); print(name, "+", len(extra))
src, dst = work / "snap_ulke_es", W / "snap_ulke_es"
added = 0
for p in src.rglob("*"):
    if p.is_file():
        t = dst / p.relative_to(src)
        if not t.exists(): t.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(p, t); added += 1
print("snap +", added)
reg_new = by_id(rj(work / "ulke_kart_kaydi.jsonl"), "entry_id")
reg = rj(W / "ulke_kart_kaydi.jsonl")
wj(W / "ulke_kart_kaydi.jsonl", [reg_new.get(r["entry_id"], r) if r.get("entry_id") in IDS else r for r in reg])
print(json.dumps(changed, ensure_ascii=False), "yedek:", yedek)
