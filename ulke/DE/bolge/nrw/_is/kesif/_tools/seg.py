import sys, os, re
sys.path.insert(0, os.path.dirname(__file__))
from fetch import get, strip

# usage: seg.py URL "phrase" [length] [occurrence_index]
url, phrase = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 1500
idx = int(sys.argv[4]) if len(sys.argv) > 4 else 0
raw, final = get(url)
t = re.sub(r'[ \t]+', ' ', strip(raw))
hits = [m.start() for m in re.finditer(re.escape(phrase), t)]
print('FINAL', final, 'hits', len(hits))
if hits:
    i = hits[min(idx, len(hits) - 1)]
    print(t[i:i + n])
