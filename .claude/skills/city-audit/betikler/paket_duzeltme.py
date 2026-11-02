"""Ulke/bolge paketinin kaydettigi duzeltmeler sehrin teslim Excel'inde duruyor mu (K118). Kullanim:
  python -I -X utf8 paket_duzeltme.py <OUT> <XLSX> <ulke_denetim_klasoru> [<bolge_denetim_klasoru> ...]
Yalniz paketin (ROOT\\ulke\\<ISO>\\...\\_is\\denetim) degisiklik kayitlarini ve teslim Excel'ini okur; sehrin uretim
klasoru okunmaz (temiz baglam). Alan basina en son `yeni` metin Excel'in ayni kaydinda yoksa listelenir.
Malaga 02.11.2026: sehir ulke paketinin 25.10 kopyasiyla kuruldu, paket 26.10'da 7 karti duzeltti; aile birlesimi
gelir istisnasi dahil 50 alan teslimde yoktu (dis denetim MAL-002 P0). Cikti OUT\\_analiz\\paket-duzeltme.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "toolkit" / "scripts"))
import iddia_defteri as idf  # noqa: E402

out, xlsx, pack_dirs = Path(sys.argv[1]), Path(sys.argv[2]), [Path(p) for p in sys.argv[3:]]
missing_dirs = [str(p) for p in pack_dirs if not p.is_dir()]
if not pack_dirs or missing_dirs:
    print(json.dumps({"error": "paket denetim klasoru yok", "klasorler": missing_dirs}, ensure_ascii=False))
    sys.exit(2)
fields = idf.load_fields(xlsx)
resolve = idf.Resolver({key: ("", 0) for key in fields})
# son klasor 'sehir' sayilir; bos bir yer tutucu eklenince butun paket klasorleri 'paket' olur
rows = idf.unapplied_changes(pack_dirs + [out / "_yok"], resolve, fields)
for row in rows:
    row["satir"] = fields[row["entry_id"]].get("_row")
cards = sorted({(r["entry_id"], r["satir"]) for r in rows})
(out / "_analiz").mkdir(parents=True, exist_ok=True)
(out / "_analiz" / "paket-duzeltme.json").write_text(
    json.dumps({"alan": len(rows), "kart": [{"entry_id": e, "satir": s} for e, s in cards], "ayrinti": rows},
               ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"uygulanmamis_alan": len(rows), "kart": len(cards), "ornek": [e for e, _ in cards][:8]}, ensure_ascii=False))
sys.exit(1 if rows else 0)
