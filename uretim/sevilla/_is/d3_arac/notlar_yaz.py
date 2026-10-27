"""notlar.md (ACIK_KONULAR kaynagi) son hal: kapanis listesi (son turda kalanlar) + sabit acik maddeler; eski icerik 'Gecmis'e."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
PY = r"C:\temp_private\corteqs\0000_newera\.venv\Scripts\python.exe"


def main() -> int:
    subprocess.run([PY, "-I", str(W / "d3_arac" / "kapanis_listesi.py")], check=True, capture_output=True)
    data = json.loads((W / "d3_arac" / "kapanis_listesi.json").read_text(encoding="utf-8"))
    heavy = [(p, r) for p, v in data.items() for r in v["kayitlar"]]
    light = [(p, r) for p, v in data.items() for r in v["hafif"]]
    old = (W / "notlar.md").read_text(encoding="utf-8") if (W / "notlar.md").is_file() else ""
    lines = ["# Açık konular — Sevilla (CITY-107)", "",
             "Son tam bağımsız denetim (26.10.2026): 448 kayıt, 5.855 defter satırı; d5 denetim → çürütme → editör → d6/d7, mekânlarda d8/d9 kapatma, en son kapanış turu ve kontrol (d10). Denetim dosyaları Teslimler\\bagimsiz-denetim-v7.csv; kanıt kapsamı kanit_kapsami.json.", "",
             "## Son kontrolde orta bulgusu kalan kayıtlar (yeni tur açılmadı)", ""]
    for p, r in heavy:
        lines.append(f"- [P2] {r['entry_id']} ({p}, {r['tur']}): {r['ozet'][:260]}")
    if not heavy:
        lines.append("- Yok.")
    lines += ["", f"## Yalnız hafif bulgusu kalan kayıtlar: {len(light)}", "",
              "Ayrıntı Teslimler\\bagimsiz-denetim-v7.csv (son tur satırları). Çoğu çeviri inceliği, K26'da kaynakta olmayan öğe (ücret/süre/ofis adresi kaynakta yok) ya da alt başlık sözcüğü.", "",
              "## Diğer açık konular", "",
              "- [P2] Bazı mekânlarda resmî tanıtım ya da saat sayfası bulunamadı; kartta yalnız kaynaklı bilgi kaldı (turizm portalına dayanan saat/ücret kartlardan çıkarıldı). Kaynak kapasitesi 500/500.",
              "- [P2] 51 mekân karesi dikey (yatay yedek yoktu ya da eser/başka yapıydı); sitenin dikey kareyi kırpıp kırpmadığı önizlemede (city-preview) kesinleşir.",
              "- [P2] Huevo de Colón ve Chillida Hoşgörü Anıtı kareleri: kalıcı kamusal alan eseri, TRLPI md. 35.2 panorama serbestliğiyle kullanıldı (foto inceleme kaydında not).",
              "- [P2] Şehirde düzeltilen İspanya ülke paketi kartları ulke\\ES'ye geri işlenmeli (Málaga öncesi).",
              "- [önizleme] D5 görünür atıf ve E4 web senaryoları yalnız Drive yüklemesinden sonra city-preview ile ölçülür.",
              "- Bu paket yeni oturumda city-audit (L0, L1) ile denetlenmeden gönderilmez.", ""]
    if old.strip():
        lines += ["## Geçmiş (25–26.10.2026, önceki turlar)", "", old.replace("# Açık konular", "### Önceki açık konular", 1)]
    (W / "notlar.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"orta_kalan": len(heavy), "hafif_kalan": len(light)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
