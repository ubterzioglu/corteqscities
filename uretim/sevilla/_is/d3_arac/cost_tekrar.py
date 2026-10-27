"""text_quality exact_duplicate: iki okul kartinin cost alani birebir ayni. Yerlestirme kartinin cost'u kendi baglamiyla
yeniden ifade edilir (anlam ve sayilar ayni). Degisiklik kaydi: denetim\\aile-kapanis_degisiklik.jsonl."""
import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
F = W / "data" / "parcalar" / "Yanıtlar.aile.jsonl"
TARGET = "sevilla:sevilla-okul-yerlestirme-sonuclari-itiraz-ve-matrikul-takvimi"
PREFIX_OLD = "Okul yeri ücretsizdir: "
PREFIX_NEW = "Yerleştirme, itiraz ve matrikül ücretsizdir; okul yeri de ücretsizdir: "

sys.stdout.reconfigure(encoding="utf-8")
lines = F.read_text(encoding="utf-8").splitlines()
out, done = [], None
for line in lines:
    if line.strip():
        r = json.loads(line)
        if r.get("entry_id") == TARGET and str(r.get("cost", "")).startswith(PREFIX_OLD):
            old = r["cost"]
            r["cost"] = PREFIX_NEW + old[len(PREFIX_OLD):]
            done = (old, r["cost"])
            line = json.dumps(r, ensure_ascii=False)
    out.append(line)
if not done:
    print("degisiklik yok: hedef ya da onek bulunamadi")
    sys.exit(1)
F.write_text("\n".join(out) + "\n", encoding="utf-8")
with (W / "denetim" / "aile-kapanis_degisiklik.jsonl").open("a", encoding="utf-8") as f:
    f.write(json.dumps({"entry_id": TARGET, "alan": "cost", "eski": done[0], "yeni": done[1], "bulgu_claim_id": "text_quality-exact-duplicate",
                        "gerekce": "iki kartin cost alani birebir ayniydi (K27); anlam ve sayilar degismeden ifade ayrildi", "alinti": ""}, ensure_ascii=False) + "\n")
print(json.dumps({"yeni": done[1][:160]}, ensure_ascii=False))
