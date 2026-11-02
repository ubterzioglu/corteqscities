r"""city-pack -> city-pack-hibrit esitleme: asil skill degisince hibrit kopyasini yeniden kurar.

Kullanim:
  esitle.py [--kuru]

Yapilan:
  1. city-pack\agents\*.md ve city-pack\references\* hibrite kopyalanir (hibrite ozel dosyalar korunur:
     agents\qwen-ek-kurallar.md, references\isci_dagilimi.json).
  2. Hibrit SKILL.md = guncel city-pack\SKILL.md + hibrit ekleri: ust bilgi ve baslik, "## Hibrit is bolumu"
     (bugunku hibrit SKILL.md'den aynen alinir), Sabit yollar'a BETIK/ISCI/DAGILIM, uc satir ici degisiklik.
Bir capa city-pack'te bulunamazsa hicbir sey yazilmaz (cikis 1): city-pack o satiri degistirmistir, bu dosyadaki
DEGISIKLIKLER listesi elle guncellenir. Uretim surerken calistirma (SKILL kural 14).
stdout tek satir JSON. Cikis: 0 esit ya da esitlendi / 1 capa bulunamadi / 2 dosya hatasi.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

HIBRIT = Path(__file__).resolve().parent.parent
ASIL = HIBRIT.parent / "city-pack"
HIBRITE_OZEL = {"qwen-ek-kurallar.md", "isci_dagilimi.json"}
BOLUM_BAS, BOLUM_SON = "## Hibrit iş bölümü\n", "## Sabit yollar\n"

UST_ESKI_ONEK = "---\nname: city-pack\n"
UST_YENI = (
    "---\n"
    "name: city-pack-hibrit\n"
    "description: Corteqs v7 şehir paketini hibrit üretir - basit yazım rolleri Qwen'e (API, betikler\\qwen_isci.py), "
    "kaynak keşfi, denetim, editör ve doğrulama Claude'a. Yalnız kullanıcı açıkça \"hibrit\" dediğinde kullan "
    "(\"<şehir> hibrit\", \"hibrit paket\", \"city-pack-hibrit\"). Yalnız şehir adı yazıldığında city-pack kullanılır, "
    "bu değil. Denetim için city-audit, Drive/önizleme için kullanma.\n"
    "---\n\n"
    "# city-pack-hibrit: şehir paketi üretimi (Qwen + Claude)\n\n"
    "Bu skill `city-pack`'in kopyasıdır; bütün kurallar aynen geçerlidir. Tek fark aşağıdaki **Hibrit iş bölümü** "
    "bölümüdür ve çeliştiği yerde o bölüm esastır.\n"
)
BASLIK_ASIL = "# city-pack: şehir paketi üretimi\n"

DEGISIKLIKLER = [
    (
        "AGENTS  = <bu skill>\\agents\\                       (alt ajan talimatları)\n",
        "AGENTS  = <bu skill>\\agents\\                       (alt ajan talimatları)\n"
        "BETIK   = <bu skill>\\betikler\\                     (hibrit: qwen_isci.py, duzelt_orani.py)\n"
        "ISCI    = BETIK\\qwen_isci.py                       (Qwen yazım işçisi; API anahtarı ortamda QWEN_API_KEY)\n"
        "DAGILIM = <bu skill>\\references\\isci_dagilimi.json (rol → qwen | claude, Qwen ayarları)\n",
    ),
    (
        "    - **Varsayılan model ve ayar:** yazar ve editör Sonnet orta;",
        "    - **Varsayılan model ve ayar:** `DAGILIM`'de `qwen` olan yazar rolleri Qwen (Hibrit iş bölümü); "
        "öteki yazarlar ve editör Sonnet orta;",
    ),
    (
        "- Yazarlar: konu başına bir Sonnet ajanı (12 paralel), talimat",
        "- Yazarlar: konu başına bir yazar (`DAGILIM` `yanit-yazari`: `qwen` ise `ISCI` çağrısı, en çok 4 eşzamanlı; "
        "`claude` ise Sonnet ajanı, 12 paralel), talimat",
    ),
    (
        "- Yazarlar (paralel; talimat `AGENTS\\ortak-kurallar.md` + `AGENTS\\yer-yazari.md`, mekân ve rota yazarları "
        "ayrıca `AGENTS\\mekan-yazari.md`):",
        "- Yazarlar (paralel; talimat `AGENTS\\ortak-kurallar.md` + `AGENTS\\yer-yazari.md`, mekân ve rota yazarları "
        "ayrıca `AGENTS\\mekan-yazari.md`; mekân, mahalle, sözlük ve rota yazarı `DAGILIM`'de `qwen` ise `ISCI` "
        "çağrısıdır, sayfa yazarı Claude; Qwen mekân yazarında reddedilen kaynak ve yedek mekân `open`'a gelir, "
        "ana döngü kaynak ajanıyla çözer):",
    ),
]


class CapaYok(Exception):
    """Cikis 1."""


def oku(yol: Path) -> str:
    return yol.read_text(encoding="utf-8").replace("\r\n", "\n")


def hibrit_bolumu(hibrit_skill: str) -> str:
    bas, son = hibrit_skill.find(BOLUM_BAS), hibrit_skill.find(BOLUM_SON)
    if bas < 0 or son < bas:
        raise CapaYok("hibrit SKILL.md'de '## Hibrit iş bölümü' bölümü yok")
    return hibrit_skill[bas:son]


def yeni_skill(asil: str, bolum: str) -> str:
    if not asil.startswith(UST_ESKI_ONEK) or BASLIK_ASIL not in asil:
        raise CapaYok("city-pack SKILL.md üst bilgi ya da başlık beklenen biçimde değil")
    govde = asil.split(BASLIK_ASIL, 1)[1]
    metin = UST_YENI + govde
    if metin.count(BOLUM_SON) != 1:
        raise CapaYok("'## Sabit yollar' başlığı tek değil")
    metin = metin.replace(BOLUM_SON, bolum + BOLUM_SON)
    for eski, yeni in DEGISIKLIKLER:
        if metin.count(eski) != 1:
            raise CapaYok(f"çapa {metin.count(eski)} kez bulundu (1 olmalı): {eski[:70]}")
        metin = metin.replace(eski, yeni)
    return metin


def kopyalanacaklar() -> list[tuple[Path, Path]]:
    ciftler = []
    for klasor in ("agents", "references"):
        for kaynak in sorted((ASIL / klasor).iterdir()):
            if kaynak.is_file() and kaynak.name not in HIBRITE_OZEL:
                ciftler.append((kaynak, HIBRIT / klasor / kaynak.name))
    return ciftler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="city-pack -> city-pack-hibrit esitleme")
    ap.add_argument("--kuru", action="store_true", help="yazmadan ne degisecegini soyle")
    args = ap.parse_args(argv)
    try:
        hedef_skill = HIBRIT / "SKILL.md"
        yeni = yeni_skill(oku(ASIL / "SKILL.md"), hibrit_bolumu(oku(hedef_skill)))
        degisen = [h.relative_to(HIBRIT).as_posix() for k, h in kopyalanacaklar()
                   if not h.exists() or oku(k) != oku(h)]
        skill_degisti = yeni != oku(hedef_skill)
        if not args.kuru:
            for kaynak, hedef in kopyalanacaklar():
                shutil.copyfile(kaynak, hedef)
            if skill_degisti:
                hedef_skill.write_text(yeni, encoding="utf-8", newline="\n")
    except CapaYok as e:
        print(json.dumps({"hata": str(e)}, ensure_ascii=False))
        return 1
    except OSError as e:
        print(json.dumps({"hata": f"dosya: {e}"}, ensure_ascii=False))
        return 2
    print(json.dumps({"kuru": args.kuru, "skill_degisti": skill_degisti, "dosyalar": degisen}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
