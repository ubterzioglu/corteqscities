"""Editor oncesi yedek ile guncel kartlari karsilastirir; dar denetim icin yalniz degisen alanlari ve yeni claim'leri yazar."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).parent / "yazar" / "out"
BACKUP = OUT / "yedek_editor_oncesi"
TOPICS = ("gunluk", "aile", "saglik", "para", "ev", "resmi")
FIELDS = ("title", "subtitle", "summary", "steps", "documents", "timing", "cost", "note", "source_ids")


def rows(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


lines = ["# NRW editör farkı (dar denetim girdisi)", "",
         "Her kart için yalnız editörün değiştirdiği alanlar (ÖNCE → SONRA) ve yeni/değişen claim'ler.", ""]
totals = {"cards": 0, "fields": 0, "claims": 0}
for topic in TOPICS:
    before = {c["slug"]: c for c in rows(BACKUP / topic / f"Yanıtlar.{topic}.jsonl")}
    after = rows(OUT / topic / f"Yanıtlar.{topic}.jsonl")
    old_claims = {(c["entry_id"], c["quote"], c.get("claim")) for c in rows(BACKUP / topic / f"claims.{topic}.jsonl")}
    new_claims = rows(OUT / topic / f"claims.{topic}.jsonl")
    for card in after:
        prev = before.get(card["slug"], {})
        changed = [f for f in FIELDS if prev.get(f) != card.get(f)]
        added = [c for c in new_claims if c["entry_id"] == card["entry_id"]
                 and (c["entry_id"], c["quote"], c.get("claim")) not in old_claims]
        if not changed and not added:
            continue
        totals["cards"] += 1
        totals["fields"] += len(changed)
        totals["claims"] += len(added)
        lines += [f"## {topic} / {card['slug']}", f"source_ids: {card['source_ids']}", ""]
        for f in changed:
            lines += [f"### {f}", f"- ÖNCE: {prev.get(f)}", f"- SONRA: {card.get(f)}", ""]
        if added:
            lines.append("### yeni/değişen claim")
            lines += [f"- {c['claim_id']} [{c['source_id']}] {c.get('claim')} | \"{c['quote']}\"" for c in added]
            lines.append("")
(OUT / "editor_farki.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(json.dumps(totals, ensure_ascii=False))
