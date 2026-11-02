"""NRW kapanisi: denetim dosyalarini _is\\denetim'e kopyalar, gaps.md'leri tek dosyada toplar, paket ozetini yazdirir."""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
NRW = Path(__file__).parent.parent
OUT = NRW / "_is" / "yazar" / "out"
TOPICS = ("gunluk", "aile", "saglik", "para", "ev", "resmi")

audit = NRW / "_is" / "denetim"
audit.mkdir(exist_ok=True)
for name in ("denetim_A.md", "denetim_B.md", "dar_denetim.md", "editor_farki.md",
             "degisiklik_A.jsonl", "degisiklik_B.jsonl", "degisiklik_dar.jsonl"):
    shutil.copyfile(OUT / name, audit / name)
print("denetim dosyalari:", sorted(p.name for p in audit.iterdir()))

parts = []
for t in TOPICS:
    for label, path in (("keşif", NRW / "_is" / "kesif" / t / "gaps.md"), ("yazar/editör", OUT / t / "gaps.md")):
        if path.is_file():
            parts.append(f"### {t} — {label}\n\n{path.read_text(encoding='utf-8').strip()}\n")
(NRW / "_is" / "gaps_toplu.md").write_text("\n".join(parts), encoding="utf-8")
print("gaps_toplu.md bolum:", len(parts))

pack = json.loads((NRW / "pack.json").read_text(encoding="utf-8"))
cards = [json.loads(l) for l in (NRW / "Yanıtlar.ulusal.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
print("pack:", {k: v for k, v in pack.items() if k != "cards"})
for c in sorted(cards, key=lambda c: c["order"]):
    print(f"{c['order']} | {c['topic_id']} | {c['slug']} | valid_until={pack['cards'][c['slug']]['valid_until']}"
          f" | {c['title']}")
