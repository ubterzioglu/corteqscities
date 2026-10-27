"""Kaynaklar 504 -> 500: yalnız buton adresi olarak kalan 4 kaynağın butonu çıkarılır (kart başka butonunu korur);
ehliyet kartının 3. butonu (kural: kart başına <=2) da çıkarılır. Satırlar birebir korunur, yalnız silinir.
Değişiklik kaydı: _is/denetim/kapasite-d3_degisiklik.jsonl. Yedek: _is/d3_arac/yedek_kapasite/."""
import json
import shutil
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PARTS = W / "data" / "parcalar"
YEDEK = W / "d3_arac" / "yedek_kapasite"
LOG = W / "denetim" / "kapasite-d3_degisiklik.jsonl"
DROP = {
    "sevilla:action:real-alcazar-de-sevilla-2": "ikinci buton iletişim sayfası (kaynak 439 yalnız bu butonda); Bilet al butonu kalıyor",
    "sevilla:action:palacio-de-la-condesa-de-lebrija-2": "ikinci buton iletişim sayfası (kaynak 440 yalnız bu butonda); Bilet al butonu kalıyor",
    "sevilla:action:dijital-gocebe-vizesi-2": "ikinci buton kanun metni (kaynak 142 yalnız bu butonda); konsolosluk butonu kalıyor",
    "sevilla:action:mec-burslari-ab-disi-sart-ve-basvuru-donemi-2": "ikinci buton (kaynak 483 yalnız bu butonda); aynı sitenin şartlar butonu kalıyor",
    "sevilla:action:yabanci-ehliyet-degisimi-1": "kartta 3 buton vardı (kural: <=2); kanun metni butonu çıktı, DGT Başvur ve Bilgi al kalıyor",
}


def main() -> int:
    YEDEK.mkdir(parents=True, exist_ok=True)
    found, log_rows = set(), []
    for f in sorted(PARTS.glob("Bağlantılar.*.jsonl")):
        raw = f.read_text(encoding="utf-8")
        lines = raw.splitlines(keepends=True)
        keep = []
        for line in lines:
            row = json.loads(line) if line.strip() else None
            if row and row.get("action_id") in DROP:
                found.add(row["action_id"])
                log_rows.append({"entry_id": row["entry_id"], "alan": "Bağlantılar", "eski": row, "yeni": None,
                                 "bulgu_claim_id": "kapasite-kaynaklar-500", "gerekce": DROP[row["action_id"]],
                                 "alinti": ""})
                continue
            keep.append(line)
        if len(keep) != len(lines):
            shutil.copy2(f, YEDEK / f.name)
            f.write_text("".join(keep), encoding="utf-8", newline="")
            print(f"{f.name}: {len(lines) - len(keep)} satır çıktı")
    missing = set(DROP) - found
    if missing:
        print("BULUNAMADI:", sorted(missing))
        return 1
    with LOG.open("a", encoding="utf-8") as out:
        for r in log_rows:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("kayıt:", LOG, len(log_rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
