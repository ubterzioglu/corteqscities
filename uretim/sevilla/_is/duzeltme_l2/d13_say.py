"""d13 karar ve iddia dosyalarından sayım: kayıt, temiz/düzelt, en ağır dağılımı, iddia satırı, doğru olmayan satırların türü."""
import json
import sys
from collections import Counter
from pathlib import Path

DEN = Path(sys.argv[1]) / "denetim"
karar, en_agir, sonuc, agirlik = Counter(), Counter(), Counter(), Counter()
satir = 0
for p in DEN.glob("*-d13_karar.jsonl"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            karar[r.get("karar")] += 1
            en_agir[r.get("en_agir")] += 1
for p in DEN.glob("*-d13_iddia.jsonl"):
    for l in p.read_text(encoding="utf-8").splitlines():
        if l.strip():
            r = json.loads(l)
            satir += 1
            sonuc[r.get("sonuç")] += 1
            if r.get("sonuç") != "doğru":
                agirlik[r.get("ağırlık")] += 1
print(json.dumps({"kayit": sum(karar.values()), "karar": dict(karar), "en_agir": dict(en_agir), "iddia_satiri": satir,
                  "sonuc": dict(sonuc), "dogru_olmayan_agirlik": dict(agirlik)}, ensure_ascii=False))
