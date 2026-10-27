"""Parque de los Bermejales kareleri için ana döngünün görsel inceleme satırlarını review_d8_ana.jsonl'e ekler
(önizlemeler duzeltme_l2/foto/bermejales altına kopyalanır). Aynı anahtar zaten varsa eklemez.

Kullanım: python -I -X utf8 foto_inceleme_bermejales.py <WORK_is> <onizleme_klasoru>
"""
import json
import shutil
import sys
from pathlib import Path

IS, SRC = Path(sys.argv[1]), Path(sys.argv[2])
DST = IS / "duzeltme_l2" / "foto" / "bermejales"
DST.mkdir(parents=True, exist_ok=True)
REV = IS / "foto" / "inceleme" / "review_d8_ana.jsonl"
EID = "sevilla:parque-de-los-bermejales"
KARARLAR = [
    ("Parque de los Bermejales 08.jpg", "Parkın içinden geçen yaya yolu ve yeşil bisiklet yolu, iki yanda ağaçlar, çim ve banklar; insan yok (2021).",
     "Mekânı doğrudan gösteriyor; Commons own work, CC BY-SA 4.0, yazar CarlosVdeHabsburgo."),
    ("Parque de los Bermejales 03.jpg", "Akşam ışığında çimenlik alan ve ağaç grupları; geride yol ve yapılar (2018).",
     "Parkın yeşil alanını gösteriyor; Commons own work, CC BY-SA 4.0, yazar CarlosVdeHabsburgo."),
    ("Parque de los Bermejales 01.jpg", "Ağaçlı toprak yürüyüş yolu ve banklar; uzakta bankta oturan, tanınmayacak ölçekte bir kişi (2018).",
     "Parkın yürüyüş yolunu gösteriyor; kişi ana konu değil ve tanınmıyor; Commons own work, CC BY-SA 4.0, yazar CarlosVdeHabsburgo."),
]
var = {json.loads(l)["key"] for l in REV.read_text(encoding="utf-8").splitlines() if l.strip()}
yeni = []
for slot, (dosya, seen, reason) in enumerate(KARARLAR, 1):
    key = f"{EID}|File:{dosya}"
    if key in var:
        continue
    shutil.copy2(SRC / dosya.replace(" ", "_"), DST / dosya.replace(" ", "_"))
    yeni.append({"key": key, "sheet": f"duzeltme_l2/foto/bermejales/{dosya.replace(' ', '_')}", "slot": slot, "entry_id": EID,
                 "result": "keep", "seen": seen, "reason": reason, "ek_hak": "yok"})
with REV.open("a", encoding="utf-8") as f:
    for r in yeni:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")
print(json.dumps({"eklenen": len(yeni), "toplam": len(var) + len(yeni)}, ensure_ascii=False))
