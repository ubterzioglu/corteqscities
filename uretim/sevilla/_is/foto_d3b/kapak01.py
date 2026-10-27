"""kapak-01 ve plaza-de-espana-01: 1280x574 panorama (gorsel_kalite: dusuk_cozunurluk + kapakta guclu kirpma) yerine
"Plaza de Espana (Sevilla) - 01" (Carlos Delgado, 3888x2592, CC BY-SA 4.0, Own work, WLM 2015; aday foto\\candidates.jsonl).
Ana dongu 1280 px onizlemeyi acip bakti (26.10.2026): iki kule, saray, kanal, kopru, fiskiye; secilebilir yuz yok.
selected.jsonl'de ayni satirlar yerinde degisir (ayni sira = ayni photo_id). Kullanim: python -I kapak01.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
OLD_FILE_PREFIX = "File:9. Mai 1929"
NEW_KEY = "sevilla:plaza-de-espana|File:Plaza de España (Sevilla) - 01.jpg"
CAPTIONS = {
    "Kapak": "Akşamüstü ışığında Plaza de España: iki kulesiyle yarım daire saray, kanal ve fıskiyeli meydan.",
    "Mekân": "Plaza de España'nın revaklı tuğla kanadı, çini oturma nişleri, kanal üstündeki köprü ve sağda fıskiye.",
}


def main() -> int:
    path = W / "foto" / "selected.jsonl"
    rows = [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]
    candidates = {json.loads(l).get("candidate_id") for l in (W / "foto" / "candidates.jsonl").read_text(encoding="utf-8-sig").splitlines() if l.strip()}
    if NEW_KEY not in candidates:
        print(json.dumps({"problem": "yeni anahtar aday dosyasinda yok"}, ensure_ascii=False))
        return 2
    changed = []
    out = []
    for r in rows:
        file_part = r["key"].split("|", 1)[-1]
        if r["key"].startswith("sevilla:plaza-de-espana|") and file_part.startswith(OLD_FILE_PREFIX) and r["role"] in CAPTIONS:
            out.append({**r, "key": NEW_KEY, "caption": CAPTIONS[r["role"]], "seen": CAPTIONS[r["role"]]})
            changed.append((r["role"], r["key"][:80]))
        else:
            out.append(r)
    if sorted(c[0] for c in changed) != ["Kapak", "Mekân"]:
        print(json.dumps({"problem": "beklenen iki satir bulunamadi", "changed": changed}, ensure_ascii=False))
        return 2
    (W / "foto_d3b" / "selected_kapak_oncesi.jsonl").write_text(path.read_text(encoding="utf-8-sig"), encoding="utf-8")
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(json.dumps({"changed": changed, "rows": len(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
