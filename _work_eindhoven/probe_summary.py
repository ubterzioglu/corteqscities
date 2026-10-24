import json
d = json.load(open('commons_probe.json', encoding='utf-8'))
tot = 0
zero = []
for k, v in d.items():
    tot += v['usable_count']
    if v['usable_count'] == 0:
        zero.append(k)
    else:
        print(f"{k:34s} cand={v['candidate_count']:4d} usable={v['usable_count']:4d}")
print()
print('ZERO:', zero)
print('TOTAL usable:', tot)
