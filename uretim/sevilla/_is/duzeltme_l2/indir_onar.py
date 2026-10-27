"""Foto indirme onarımı (Atınç'ın download_media.py'si değiştirilmeden):
1) İndirme planındaki her satırın Commons dosyasını, son teslimdeki (L2 denetiminin xlsx dökümü) aynı photo_id'nin
   Commons dosyasıyla karşılaştırır; farklıysa paketteki eski hedef dosyayı paket DIŞINDAKİ yedek klasöre taşır
   (download_media farklı içerikli dosyanın üzerine yazmayı reddediyor).
2) download_media'yı döngüde çalıştırır: "refusing to overwrite: <photo_id>" hatasında o dosyayı da yedeğe taşır;
   PermissionError'da (ilerleme dosyası, Windows) bekleyip yeniden dener. En çok 15 deneme.
3) Sonda ilerleme dosyasında plan kadar satır ve her hedef dosyanın varlığını doğrular.

Kullanım: python -I -X utf8 indir_onar.py <WORK_is> <PKG> <TOOLS> <eski_Fotoğraflar.jsonl> [--kuru]
Çıkış: 0 tamam; 1 eksik kaldı; 2 girdi hatası.
"""
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import unquote

IS, PKG, TOOLS, ESKI = (Path(a) for a in sys.argv[1:5])
KURU = "--kuru" in sys.argv
plan = json.loads((IS / "foto" / "indirme_plani.json").read_text(encoding="utf-8"))
if "--dogrula" in sys.argv:  # yalnız son kontrol: taşıma ve indirme yok (zincirin yeniden çalıştırılması için)
    prog = json.loads((PKG / "Teslimler" / "download-progress-v7.json").read_text(encoding="utf-8"))
    eksik = [r["original_file"] for r in plan if not (PKG / r["original_file"]).exists()]
    pid_prog = {r.get("photo_id") for r in prog}
    eksik_ilerleme = [r["photo_id"] for r in plan if r["photo_id"] not in pid_prog]
    ok = not eksik and not eksik_ilerleme
    print(json.dumps({"dogrula": True, "plan": len(plan), "ilerleme_satiri": len(prog), "eksik_dosya": len(eksik),
                      "ilerlemede_olmayan": len(eksik_ilerleme), "ornek": (eksik + eksik_ilerleme)[:5], "tamam": ok}, ensure_ascii=False))
    sys.exit(0 if ok else 1)
eski = {r["photo_id"]: r for r in (json.loads(l) for l in ESKI.read_text(encoding="utf-8").splitlines() if l.strip())}
YEDEK = IS / "foto_yedek_d13"


def commons_adi(url: str) -> str:
    u = unquote(str(url or "")).split("?")[0]
    if "/wiki/File:" in u:
        ad = u.split("/wiki/File:", 1)[1]
    elif "/thumb/" in u:
        ad = u.split("/thumb/", 1)[1].split("/")[2]  # thumb/<a>/<ab>/<Dosya>/<NNNpx-Dosya>
    else:
        ad = u.rsplit("/", 1)[-1]
    return ad.replace(" ", "_").lower()


def tasi(rel: str, neden: str) -> bool:
    hedef = PKG / rel
    if not hedef.exists():
        return False
    if not KURU:
        YEDEK.mkdir(parents=True, exist_ok=True)
        shutil.move(str(hedef), str(YEDEK / hedef.name))
    print(json.dumps({"tasindi": hedef.name, "neden": neden}, ensure_ascii=False))
    return True


by_pid = {r["photo_id"]: r for r in plan}
farkli = 0
for r in plan:
    e = eski.get(r["photo_id"])
    if e is None or commons_adi(e.get("source_url")) != commons_adi(r["downloaded_file_url"]):
        farkli += tasi(r["original_file"], "kaynak değişti" if e else "yeni photo_id")
print(json.dumps({"plan": len(plan), "farkli_tasinan": farkli, "kuru": KURU}, ensure_ascii=False))
if KURU:
    sys.exit(0)
cmd = [sys.executable, "-X", "utf8", "-B", "download_media.py", str(IS / "foto" / "indirme_plani.json"), str(PKG),
       "--allow-host", "upload.wikimedia.org", "--allow-host", "thumb.wikimedia.org", "--allow-host", "live.staticflickr.com",
       "--workers", "2"]
for deneme in range(1, 16):
    cp = subprocess.run(cmd, cwd=str(TOOLS), capture_output=True, text=True, encoding="utf-8", errors="replace")
    son = (cp.stdout.strip().splitlines() or [""])[-1]
    if cp.returncode == 0:
        print(json.dumps({"deneme": deneme, "sonuc": son[:200]}, ensure_ascii=False))
        break
    m = re.search(r"refusing to overwrite: (\S+)", cp.stderr)
    if m and m.group(1) in by_pid:
        tasi(by_pid[m.group(1)]["original_file"], "download_media içerik farkı")
        continue
    if "PermissionError" in cp.stderr:
        print(json.dumps({"deneme": deneme, "hata": "PermissionError, bekleniyor"}, ensure_ascii=False))
        time.sleep(10)
        continue
    print(json.dumps({"deneme": deneme, "hata": cp.stderr.strip()[-600:]}, ensure_ascii=False))
    time.sleep(10)
prog = json.loads((PKG / "Teslimler" / "download-progress-v7.json").read_text(encoding="utf-8"))
eksik_dosya = [r["original_file"] for r in plan if not (PKG / r["original_file"]).exists()]
ok = len(prog) == len(plan) and not eksik_dosya
print(json.dumps({"ilerleme_satiri": len(prog), "plan": len(plan), "eksik_dosya": len(eksik_dosya), "ornek": eksik_dosya[:5], "tamam": ok},
                 ensure_ascii=False))
sys.exit(0 if ok else 1)
