"""Manifest: fotograf/kaynak sayilari (once) ya da teslim kaydi (sonra). UTC ISO; Python ile yazilir (kural 11).
Kullanim: python -I manifest_d5.py sayilar | teslim
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla")
M = W / "manifest.json"
EXCEL = W / "paket" / "CITY-107_sevilla_v001.xlsx"


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main(mode: str) -> int:
    m = json.loads(M.read_text(encoding="utf-8"))
    if mode == "sayilar":
        m["photos_downloaded"] = len(json.loads((W / "_is" / "foto" / "indirme_plani.json").read_text(encoding="utf-8")))
        m["sources_researched"] = sum(1 for l in (W / "_is" / "kaynak_dizini.jsonl").read_text(encoding="utf-8-sig").splitlines() if l.strip())
        m["next_step"] = "Yeni oturumda city-audit: 'Sevilla paketini denetle' (L0, sonra L1); sonra Drive + city-preview"
    else:
        sha = hashlib.sha256(EXCEL.read_bytes()).hexdigest()
        m["delivered"] = {**m.get("delivered", {}), "at": now(), "xlsx_sha256": sha,
                          "inventory": str(W / "paket" / "Teslimler" / "dosya-envanteri.json")}
        ph = m.setdefault("phases", {})
        for name in ("assemble", "deliver"):
            if name in ph:
                ph[name]["ended_at"] = now()
    M.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"mod": mode, "photos_downloaded": m.get("photos_downloaded"), "sources_researched": m.get("sources_researched"),
                      "delivered": m.get("delivered", {}).get("xlsx_sha256", "")[:12]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1]))
