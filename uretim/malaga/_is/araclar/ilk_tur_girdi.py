"""Bir parcanin ilk tur denetim girdisini uretir: denetim/<p>_kartlar.jsonl + .txt (eksiz ad).

Kullanim: python ilk_tur_girdi.py <_is> <parca>
denetim_girdi.py'yi --tur d1 ile cagirir (arac ilk tur adini kabul etmiyor), ciktiyi eksiz ada tasir.
Cikis: denetim_girdi'nin cikisi (0 yazildi, 1 metinsiz kaynak, 2 kullanim).
"""
import json
import pathlib
import subprocess
import sys

work = pathlib.Path(sys.argv[1])
parca = sys.argv[2]
tk = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
r = subprocess.run([sys.executable, "-X", "utf8", str(tk / "denetim_girdi.py"), str(work), "--city-id", "malaga",
                    "--tur", "d1", "--parca", parca], capture_output=True, text=True, encoding="utf-8")
src = work / "denetim" / f"{parca}-d1_kartlar.jsonl"
if src.is_file():
    hedef = work / "denetim" / f"{parca}_kartlar.jsonl"
    rows = [json.loads(l) for l in src.read_text(encoding="utf-8").splitlines() if l.strip()]
    hedef.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
    parts = []
    for i, x in enumerate(rows, 1):
        rid = x.get("entry_id") or x.get("term_id") or x.get("route_id") or x.get("field_id")
        parts.append(f"===== KAYIT {i}/{len(rows)}: {rid} =====\n" + json.dumps(x, ensure_ascii=False, indent=1))
    hedef.with_suffix(".txt").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    src.unlink()
    print(json.dumps({"parca": parca, "kayit": len(rows), "girdi": str(hedef), "denetim_girdi": r.stdout.strip()[-300:]},
                     ensure_ascii=False))
else:
    print(json.dumps({"parca": parca, "hata": "girdi uretilmedi", "stdout": r.stdout[-400:], "stderr": r.stderr[-400:]},
                     ensure_ascii=False))
sys.exit(r.returncode)
