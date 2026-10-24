"""Duzeltme oncesi/sonrasi url-checks.json ozetlerini karsilastirir (salt okunur)."""
import json
import sys
from pathlib import Path

before = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
after = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
diff = {k: {"before": before["summary"][k], "after": after["summary"][k]}
        for k in before["summary"] if before["summary"][k] != after["summary"][k]}
url_diff = [a["ham_URL"] for b, a in zip(before["urls"], after["urls"]) if b != a]
home_before = {r["ham_URL"] for r in before["urls"] if "homepage_only" in r["flags"]}
home_after = {r["ham_URL"] for r in after["urls"] if "homepage_only" in r["flags"]}
kay = [r for r in after["relations"] if r["sheet"] == "Kaynaklar"]
out = {
    "summary_keys_changed": diff,
    "url_records_changed": len(url_diff),
    "classes_same": before["summary"]["classes"] == after["summary"]["classes"],
    "verdicts_same": before["summary"]["verdicts"] == after["summary"]["verdicts"],
    "url_flags_same": before["summary"]["flags"] == after["summary"]["flags"],
    "findings": [before["summary"]["findings"], after["summary"]["findings"]],
    "homepage_only": [len(home_before), len(home_after)],
    "homepage_only_set_same": home_before == home_after,
    "kaynaklar_wikipedia_rows": sum(1 for r in kay if "wikipedia" in r["flags"]),
    "kaynaklar_labeled_official_rows": sum(1 for r in kay if "wikipedia_labeled_official" in r["flags"]),
    "baglantilar_labeled_official_rows": sum(1 for r in after["relations"]
                                             if r["sheet"] == "Bağlantılar" and "wikipedia_labeled_official" in r["flags"]),
}
kay_home = sum(1 for r in kay if "homepage_only" in r["flags"])
out["kaynaklar_homepage_rows"] = kay_home
sys.stdout.reconfigure(encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=1))
