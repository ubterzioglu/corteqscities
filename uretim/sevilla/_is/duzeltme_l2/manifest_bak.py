"""manifest.json'un üst düzey alanlarını, faz pencerelerini ve delivered bloğunu kısaca yazar (yalnız okur)."""
import json
import sys
from pathlib import Path

m = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(json.dumps({k: (v if not isinstance(v, (dict, list)) else f"<{type(v).__name__} {len(v)}>") for k, v in m.items()}, ensure_ascii=False))
print("delivered:", json.dumps(m.get("delivered"), ensure_ascii=False))
for k, v in (m.get("phases") or {}).items():
    print(k, v.get("status"), v.get("started_at"), v.get("ended_at"), "gates:", str(v.get("gates"))[:160])
print("next_step:", str(m.get("next_step"))[:400])
