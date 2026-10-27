"""manifest.json güncellemesi (L2 sonrası düzeltme turu):
- open_items: notlar.md'nin "## Geçmiş" öncesindeki "- [P0|P1|P2] OI-NNN (owner): metin" satırlarından; evidence eski maddeden
  (aynı id) ya da varsayılan; kural 11: Python ile, UTC ISO tarih.
- --teslim: delivered (at, xlsx_sha256, inventory, files, total_mb, note) ve faz ended_at'leri phase_log'daki son end
  işaretlerinden (answers, photos, assemble, deliver); next_step.

Kullanım: python -I -X utf8 manifest_guncelle.py <WORK> [--teslim] [--next "<metin>"]
"""
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

WORK = Path(sys.argv[1])
IS = WORK / "_is"
mp = WORK / "manifest.json"
m = json.loads(mp.read_text(encoding="utf-8"))
eski = {i["id"]: i for i in m.get("open_items", [])}
VARSAYILAN = {"OI-029": "uretim\\sevilla\\_is\\denetim\\ulasim-d12_degisiklik.jsonl; uretim\\sevilla\\_is\\notlar_skill.md",
              "OI-030": "uretim\\sevilla\\_is\\denetim\\ulasim-d12_degisiklik.jsonl",
              "OI-031": "uretim\\sevilla\\_is\\denetim\\ulasim-d12_degisiklik.jsonl",
              "OI-032": "uretim\\sevilla\\_is\\denetim\\planlama-d12_degisiklik.jsonl",
              "OI-033": "uretim\\sevilla\\_is\\duzeltme_kararlari.jsonl; denetim\\sevilla_2026-10-26_L1\\issues.json",
              "OI-034": "uretim\\sevilla\\_is\\denetim\\kapasite-d12_dogrulama.jsonl; uretim\\sevilla\\_is\\birlestir_rapor.json",
              "OI-035": "uretim\\sevilla\\_is\\denetim\\mekan3-d12_dogrulama.jsonl",
              "OI-036": "uretim\\sevilla\\_is\\acik_mi\\ek5_d12.jsonl",
              "OI-037": "uretim\\sevilla\\_is\\denetim\\mekan3-d12_degisiklik.jsonl; mekan6-d12_degisiklik.jsonl; mekan7-d12_degisiklik.jsonl"}
metin = (IS / "notlar.md").read_text(encoding="utf-8").split("\n## Geçmiş")[0]
items = []
for line in metin.splitlines():
    mm = re.match(r"^- \[(P[012])\] (OI-\d+) \((ai|insan|atinc)\): (.+)$", line.strip())
    if not mm:
        continue
    pr, oid, owner, text = mm.groups()
    it = {"id": oid, "priority": pr, "owner": owner, "text": text,
          "evidence": (eski.get(oid) or {}).get("evidence") or VARSAYILAN.get(oid) or "uretim\\sevilla\\_is\\notlar.md"}
    if (eski.get(oid) or {}).get("check_id"):
        it["check_id"] = eski[oid]["check_id"]
    items.append(it)
if not items:
    sys.exit("notlar.md'de madde bulunamadı")
m["open_items"] = items
if "--teslim" in sys.argv:
    log = [json.loads(l) for l in (IS / "phase_log.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    for faz in ("answers", "photos", "assemble", "deliver"):
        ends = [r["ts"] for r in log if r.get("phase") == faz and r.get("event") == "end"]
        if ends:
            son = max(ends).replace(".000Z", "Z")
            son = re.sub(r"\.\d+Z$", "Z", son)
            if son > m["phases"][faz].get("ended_at", ""):
                m["phases"][faz]["ended_at"] = son
    excel = Path(m["paths"].get("delivery_xlsx") or "")
    if not excel.is_file():
        excel = next((WORK / "paket").glob("CITY-*_v001.xlsx"))
    inv_p = WORK / "paket" / "Teslimler" / "dosya-envanteri.json"
    inv = json.loads(inv_p.read_text(encoding="utf-8"))
    files = inv.get("files") or []
    total_mb = (inv.get("summary") or {}).get("total_mb") or inv.get("total_mb") or round(sum(f.get("bytes", 0) for f in files) / 1e6, 2)
    onceki = (m.get("delivered") or {}).get("xlsx_sha256", "")
    m["delivered"] = {"at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                      "xlsx_sha256": hashlib.sha256(excel.read_bytes()).hexdigest(), "inventory": str(inv_p),
                      "files": len(files), "total_mb": total_mb,
                      "note": f"L2 sonrası düzeltme turu (d11–d13, 26–27.10.2026) sonrası yeniden teslim; önceki SHA {onceki}"}
if "--next" in sys.argv:
    m["next_step"] = sys.argv[sys.argv.index("--next") + 1]
mp.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"open_items": len(items), "delivered": m.get("delivered", {}).get("xlsx_sha256", "")[:12],
                  "ended": {k: m["phases"][k].get("ended_at") for k in ("answers", "photos", "assemble", "deliver")}}, ensure_ascii=False))
