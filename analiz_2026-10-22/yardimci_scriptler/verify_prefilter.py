"""Bagimsiz yeniden uretim: prefilter'i yeniden calistir, karisiklik tablosunu kendi temel gercegimle hesapla."""
import json, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8")
TK, PY, ACC = sys.argv[1], sys.argv[2], sys.argv[3]
out = ACC + "/verify_decisions.json"
r = subprocess.run([PY, TK + "/scripts/photo_prefilter.py", "--candidates", ACC + "/candidates.jsonl", "--plan", ACC + "/venues.jsonl",
                    "--out", out, "--shortlist", "3"], capture_output=True, text=True, encoding="utf-8")
print("prefilter exit", r.returncode, r.stdout.strip()[:300])
cands = {}
for line in open(ACC + "/candidates.jsonl", encoding="utf-8"):
    c = json.loads(line); cands[c["candidate_id"]] = int(c["photo_index"])
dec = {cands[d["candidate_id"]]: d for d in json.load(open(out, encoding="utf-8"))["decisions"]}
WRONG = [255, 258, 22, 136, 26, 28, 168, 236, 156, 158, 232, 233, 240, 241, 2, 148, 149, 162, 164, 140, 247, 248, 249]
ARCH = [27, 53, 54, 55, 169, 170, 269, 270]
LOW = [1, 12, 19, 57, 65, 82, 86, 87, 88, 143, 146, 147, 205]
RIGHTS = [4, 43, 44, 45, 49, 50, 51, 79, 80, 111, 112, 260, 261]
bad = set(WRONG) | set(ARCH) | set(LOW) | set(RIGHTS)
GOOD = [i for i in dec if i not in bad]
print("toplam karar", len(dec))
for name, ids in (("Yanlis", WRONG), ("Arsiv", ARCH), ("Dusuk coz.", LOW), ("Hak", RIGHTS), ("Iyi", GOOD)):
    n = {k: sum(1 for i in ids if dec[i]["decision"] == k) for k in ("reject", "flag", "keep")}
    print(f"{name:11} n={len(ids):3}  reject={n['reject']:3} flag={n['flag']:3} keep={n['keep']:3}")
print("yanlis ama keep:", [i for i in WRONG if dec[i]["decision"] == "keep"])
print("arsiv dogru kodla mi:", all("archive" in dec[i]["reasons"] for i in ARCH))
print("iyi ama reject:", [i for i in GOOD if dec[i]["decision"] == "reject"])
from collections import Counter
print("iyi fotolardaki flag nedenleri:", Counter(r for i in GOOD if dec[i]["decision"] == "flag" for r in dec[i]["reasons"]).most_common(6))
flagged = sum(1 for d in dec.values() if d["decision"] == "flag")
print(f"gorsel incelemeye gidecek (flag): {flagged} / {len(dec)} = {100*flagged/len(dec):.0f}%")
