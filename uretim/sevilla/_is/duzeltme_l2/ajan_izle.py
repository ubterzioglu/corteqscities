"""Workflow ajanlarının son araç çağrılarını ve yazdıkları dosyaları özetler (yalnız okur)."""
import json
import re
import sys
from collections import Counter
from pathlib import Path

W = Path(sys.argv[1])
N = int(sys.argv[2]) if len(sys.argv) > 2 else 8
for meta in sorted(W.glob("agent-*.meta.json")):
    m = json.loads(meta.read_text(encoding="utf-8"))
    label = m.get("label") or m.get("description") or meta.name
    calls, writes = [], []
    cnt = Counter()
    for line in meta.with_name(meta.name.replace(".meta.json", ".jsonl")).read_text(encoding="utf-8", errors="ignore").splitlines():
        try:
            j = json.loads(line)
        except json.JSONDecodeError:
            continue
        msg = j.get("message") or {}
        for c in msg.get("content") or [] if isinstance(msg.get("content"), list) else []:
            if c.get("type") != "tool_use":
                continue
            name, inp = c.get("name"), c.get("input") or {}
            cnt[name] += 1
            if name in ("Write", "Edit"):
                writes.append(str(inp.get("file_path", ""))[-90:])
            s = inp.get("command") or inp.get("file_path") or inp.get("url") or inp.get("pattern") or inp.get("query") or ""
            s = re.sub(r"\s+", " ", str(s))
            calls.append(f"{name}: {s[:150]}")
    print(f"=== {label} | araç sayısı {sum(cnt.values())} {dict(cnt)}")
    print("  yazdığı dosyalar:", sorted(set(writes))[-10:])
    for c in calls[-N:]:
        print("   ", c)
