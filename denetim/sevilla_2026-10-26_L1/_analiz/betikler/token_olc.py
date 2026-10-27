"""Bu oturumun ana döngü + alt ajan token kullanımını kayıtlardan toplar (yalnız okur)."""
import json
import sys
from collections import defaultdict
from pathlib import Path

PROJ = Path(r"C:\Users\baris-terzioglu\.claude\projects\c--temp-private-corteqs-0000-newera")
SID = "928be71a-0e9c-4b09-b172-91a95baa00e3"


def usage(path: Path):
    seen, tot = set(), defaultdict(int)
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        m = j.get("message") or {}
        u = m.get("usage")
        if not u:
            continue
        key = m.get("id") or j.get("uuid")
        if key in seen:
            continue
        seen.add(key)
        model = m.get("model") or "?"
        for k in ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"):
            tot[(model, k)] += int(u.get(k) or 0)
    return tot


groups = defaultdict(lambda: defaultdict(int))
main = PROJ / f"{SID}.jsonl"
if main.exists():
    for k, v in usage(main).items():
        groups["ana döngü"][k] += v
sub = PROJ / SID / "subagents"
for p in sub.rglob("agent-*.jsonl"):
    g = "workflow " + p.parent.name if p.parent.name.startswith("wf_") else "Agent aracı"
    for k, v in usage(p).items():
        groups[g][k] += v
grand = defaultdict(int)
for g, t in groups.items():
    by_model = defaultdict(lambda: defaultdict(int))
    for (model, k), v in t.items():
        by_model[model][k] += v
        grand[k] += v
    for model, d in by_model.items():
        fresh = d["input_tokens"] + d["cache_creation_input_tokens"]
        print(f"{g:28s} {model:22s} yeni_girdi {fresh/1e6:7.2f} M | önbellek_okuma {d['cache_read_input_tokens']/1e6:8.2f} M | çıktı {d['output_tokens']/1e6:6.2f} M")
fresh = grand["input_tokens"] + grand["cache_creation_input_tokens"]
print(f"TOPLAM yeni_girdi {fresh/1e6:.2f} M | önbellek_okuma {grand['cache_read_input_tokens']/1e6:.2f} M | çıktı {grand['output_tokens']/1e6:.2f} M | hepsi {(fresh+grand['cache_read_input_tokens']+grand['output_tokens'])/1e6:.2f} M")
