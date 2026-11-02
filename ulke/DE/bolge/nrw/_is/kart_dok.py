"""Verilen slug parcalarina uyan kartlarin metin alanlarini ve istenen claim'leri yazdirir."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).parent / "yazar" / "out"
WANT = {
    "okul-sistemi": ("note",),
    "grunderwerbsteuer": ("cost",),
    "widerspruch-yok": ("subtitle", "summary", "steps", "note"),
    "magaza-acilis": ("summary", "steps", "timing", "note"),
    "kita-ucreti": ("steps",),
    "u-muayeneleri": ("summary", "timing", "note"),
    "kilise-vergisi": ("summary",),
    "kira-tavani": ("steps", "note"),
    "wbs-gelir": ("steps", "documents"),
}
CLAIMS = ("grunderwerbsteuer-orani-ve-odeme-20", "mieterschutzverordnung-13")

for topic_dir in sorted(p for p in OUT.iterdir() if p.is_dir() and not p.name.startswith("yedek")):
    for path in topic_dir.glob("Yanıtlar.*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            card = json.loads(line)
            for key, fields in WANT.items():
                if key in card["slug"]:
                    print(f"===== {card['slug']}")
                    for f in fields:
                        print(f"--- {f}:\n{card.get(f)}\n")
    for path in topic_dir.glob("claims.*.jsonl"):
        for line in path.read_text(encoding="utf-8").splitlines():
            c = json.loads(line)
            if c["claim_id"].endswith(CLAIMS):
                print("CLAIM", json.dumps(c, ensure_ascii=False))
