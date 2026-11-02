"""resmi kartinin alt basligini 160 karakter sinirina indirir."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
PATH = Path(__file__).parent / "yazar" / "out" / "resmi" / "Yanıtlar.resmi.jsonl"
NEW = ("İdare mahkemesi yolunda NRW'de kural olarak Widerspruch yok, doğrudan dava açılır; okulun kendi işlemleri, "
       "belediye harcı, Wohngeld gibi alanlarda itiraz sürer.")
if len(NEW) > 160:
    raise SystemExit(f"HATA: hala uzun {len(NEW)}")
cards = [json.loads(l) for l in PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
cards = [dict(c, subtitle=NEW) if "widerspruch-yok" in c["slug"] else c for c in cards]
PATH.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in cards), encoding="utf-8", newline="\n")
print("alt baslik", len(NEW))
