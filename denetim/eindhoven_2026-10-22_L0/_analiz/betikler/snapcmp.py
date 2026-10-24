"""K76 (partial): package source snapshots vs fresh fetch - title match + text overlap. Read-only on PKG."""
import html
import json
import re
import sys
from pathlib import Path

OUT, PKG = Path(sys.argv[1]), Path(sys.argv[2])
TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)


def norm(text):
    return re.sub(r"\s+", " ", html.unescape(text or "")).strip().lower()


def title_of(path):
    try:
        raw = path.read_bytes()[:400000].decode("utf-8", errors="replace")
    except OSError:
        return None
    m = TITLE.search(raw)
    return norm(m.group(1)) if m else ""


def words(text):
    return set(re.findall(r"\w{4,}", text.lower()))


sources = [json.loads(l) for l in (OUT / "_dump" / "Kaynaklar.jsonl").open(encoding="utf-8") if l.strip()]
urls = {u["ham_URL"]: u for u in json.loads((OUT / "url-checks.json").read_text(encoding="utf-8"))["urls"]}
snap_index = {}
for line in (OUT / "kanitlar" / "snap" / "index.jsonl").open(encoding="utf-8"):
    if line.strip():
        row = json.loads(line)
        snap_index[row["url"]] = row
rows, same, differ, notitle = [], 0, [], 0
for s in sources:
    pkg_title = title_of(PKG / s["snapshot_file"])
    fresh = urls.get(s["url"], {})
    fresh_title = norm(fresh.get("sayfa_başlığı"))
    fresh_snap = snap_index.get(s["url"], {})
    overlap = None
    if fresh_snap.get("text_file"):
        fresh_text = (OUT / "kanitlar" / "snap" / fresh_snap["text_file"]).read_text(encoding="utf-8", errors="replace")
        pkg_raw = (PKG / s["snapshot_file"]).read_text(encoding="utf-8", errors="replace")
        pkg_text = re.sub(r"<[^>]+>", " ", re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", pkg_raw))
        a, b = words(fresh_text), words(pkg_text)
        overlap = round(len(a & b) / len(a), 3) if a else None
    if not pkg_title:
        notitle += 1
    if pkg_title and fresh_title and (pkg_title == fresh_title or pkg_title in fresh_title or fresh_title in pkg_title):
        same += 1
    else:
        differ.append({"source_id": s["source_id"], "row": s["_row"], "url": s["url"], "pkg_title": pkg_title,
                       "fresh_title": fresh_title, "fresh_text_word_overlap": overlap})
    rows.append(overlap)
valid = [o for o in rows if o is not None]
low = [d for d in differ if (d["fresh_text_word_overlap"] or 0) < 0.5]
print(json.dumps({"sources": len(sources), "title_match": same, "title_differ": len(differ), "pkg_no_title": notitle,
                  "overlap_median": sorted(valid)[len(valid) // 2] if valid else None,
                  "overlap_lt_0_5_all": sum(1 for o in valid if o < 0.5),
                  "differ_and_low_overlap": low[:15], "differ_sample": differ[:8]}, ensure_ascii=False, indent=1))
