import json, os
d = json.load(open('commons_probe_dc.json', encoding='utf-8'))
for k, v in d.items():
    print(f"{k:24s} cand={v['candidate_count']:4d} usable={v['usable_count']:4d}")
    for u in v['usable'][:4]:
        print("    -", u['title'][:80], "|", u['license'], "|", u['author'][:30])
