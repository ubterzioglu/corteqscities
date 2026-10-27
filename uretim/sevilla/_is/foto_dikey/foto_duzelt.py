"""Son foto denetiminin (foto\\inceleme\\denetim_N[b].jsonl) uygulanmasi.

hazirla: kararlar Commons anahtarina (key) gore saklanir (son_karar.json); selected.jsonl'den ret/yinelenen kareler
         cikar, alt yazilar duzeltilir, kapak-05 degisir. photo_rows numaralari slug basina yeniden verir, bu yuzden
         photo_id degil key esastir.
son:     foto zincirinden sonra yeni secim_temiz ile key -> yeni photo_id; denetim_son.jsonl yazilir, eski denetim_*
         dosyalari denetim_arsiv\\'e tasinir (kanit_teslim yalniz son hali okusun).
Kullanim: python -I foto_duzelt.py hazirla | son
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
INS = W / "foto" / "inceleme"
D = W / "foto_dikey"
P = "sevilla:photo:"
DROP = ["auditorio-cartuja-sevilla-01", "caixaforum-sevilla-02", "casa-de-la-memoria-al-andalus-02", "el-arenal-03",
        "iglesia-de-san-esteban-02", "iglesia-de-san-pedro-01", "iglesia-de-san-sebastian-01", "teatro-de-la-maestranza-02",
        "estadio-sanchez-pizjuan-tur-03", "capilla-de-los-marineros-01", "ciudad-de-los-ninos-prado-02", "museo-ve-plaza-nueva-01"]
CAPTIONS = {
    "alfalfa-ve-encarnacion-01": "Encarnación Meydanı'nda Metropol Parasol'ün ahşap çatısı altından sokağa bakış; sağda bir çan kulesi, yayalar geçiyor.",
    "alfalfa-ve-encarnacion-02": "Plaza de la Encarnación'da akşam: aydınlatılmış taş kilise portalı, kafe ve ışık izi bırakan trafik.",
    "auditorio-cartuja-sevilla-02": "Auditorio Cartuja'nın karanlık salonu: sahne, ışıklar ve basamaklı koltuk sıraları.",
    "caixaforum-sevilla-01": "CaixaForum Sevilla'nın beyaz, kıvrımlı dış duvarı ağaçların ardında, tepede beyaz yelken biçimli parça.",
    "casa-de-la-provincia-sevilla-01": "Casa de la Provincia'nın kırmızı-beyaz cephesi, balkonda bayraklar, önde narenciye ağaçları ve sokak lambası.",
    "estadio-benito-villamarin-tur-02": "Gün ışığında La Cartuja Stadı'nın içi: oval çatı kenarı ve yeşil-beyaz kalabalık tribünler.",
    "estadio-benito-villamarin-tur-03": "Gece maç ışıkları altında La Cartuja Stadı'nın dolu tribünleri ve sahası.",
    "guadalquivir-paseo-de-las-delicias-01": "Guadalquivir Nehri üzerindeki köprü; karşı kıyıda yüksek binalar, sağda Torre Sevilla.",
    "iglesia-de-san-sebastian-03": "San Sebastián Kilisesi'nin tuğla çerçeveli, sivri kemerli ana portalı ve çivili koyu ahşap kapısı.",
    "monasterio-de-san-jeronimo-de-buenavista-02": "San Jerónimo Manastırı'nın taş sütunlu, yuvarlak kemerli ana klostrosu.",
    "muelle-de-la-sal-02": "Muelle de la Sal rıhtımında taş döşeli yol, palmiyeler ve Chillida'nın Hoşgörü Anıtı; yürüyen birkaç kişi.",
    "museo-ve-plaza-nueva-03": "Plaza Nueva'da balkonlu, süslemeli Edificio Generali cephesi (1957) ve ağaç dalları.",
    "san-lorenzo-ve-san-vicente-01": "San Lorenzo semtinde Calle Flandes; sokağın sonunda kırmızı-sarı cepheli, balkonlu barok bir yapı.",
    "teatro-central-sevilla-03": "Teatro Central'ın taş cephesi ve duvarda sezon afişi.",
    "teatro-de-la-maestranza-01": "Maestranza Tiyatrosu'nun yuvarlak modern binası ve önündeki su kanalı.",
    "plaza-nueva-01": "Plaza Nueva'nın rengârenk çiçek tarhları ve palmiyeleri.",
}
PANORAMA = ("kalıcı kamusal alan eseri; İspanya Fikrî Mülkiyet Kanunu (TRLPI) md. 35.2 parklarda, sokaklarda ve "
            "meydanlarda kalıcı olarak bulunan eserlerin fotoğrafla çoğaltılmasına izin verir")
RIGHTS = {"huevo-de-colon-01": ("var", PANORAMA), "huevo-de-colon-02": ("var", PANORAMA),
          "muelle-de-la-sal-02": ("var", PANORAMA), "muelle-de-la-sal-03": ("var", PANORAMA)}
COVER5_KEY = 'sevilla:metropol-parasol-antiquarium|File:"Das größte Holzbauwerk der Welt". 17.jpg'
COVER5_CAPTION = "Mantar biçimli ahşap Metropol Parasol çatısı ve ufka uzanan Sevilla damları, açık mavi gökyüzü altında."


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def wjl(path: Path, rows: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")


def hazirla() -> int:
    key_of = {r["photo_id"]: r["key"] for r in jl(W / "foto" / "secim_temiz.jsonl")}
    final = {}
    for p in sorted(INS.glob("denetim_*.jsonl")):
        for r in jl(p):
            final[r["photo_id"]] = r
    by_key = {}
    for pid, r in final.items():
        short = pid.removeprefix(P)
        key = key_of.get(pid)
        if not key or short in DROP:
            continue
        row = {k: r.get(k) for k in ("gorsel_sonuc", "ek_hak", "kimlik", "not")}
        if short in CAPTIONS:
            row |= {"gorsel_sonuc": "keep", "not": f"alt yazı denetim notuna göre düzeltildi. {r.get('not', '')}"[:700]}
        if short in RIGHTS:
            row |= {"gorsel_sonuc": "keep", "ek_hak": RIGHTS[short][0], "not": f"{RIGHTS[short][1]}. {r.get('not', '')}"[:700]}
        if short == "kapak-05":
            key = COVER5_KEY
            row = {"gorsel_sonuc": "keep", "ek_hak": "yok", "kimlik": "tutar",
                   "not": "kapak değişti: eski kare kasvetli ve triana-02 ile aynı dosyaydı; ana döngü pafta 4 slot 17'de baktı"}
        if short == "triana-02":
            row |= {"gorsel_sonuc": "keep", "not": "kapak-05 değişince yinelenme kalktı"}
        by_key[key] = row
    selected = jl(W / "foto" / "selected.jsonl")
    drop_keys = {key_of[P + s] for s in DROP}
    cap_keys = {key_of[P + s]: c for s, c in CAPTIONS.items()}
    cover_old = key_of[P + "kapak-05"]
    out, dropped = [], 0
    for r in selected:
        if r["key"] in drop_keys:
            dropped += 1
            continue
        if r["key"] in cap_keys and r.get("role") != "Kapak":
            r = {**r, "caption": cap_keys[r["key"]], "seen": cap_keys[r["key"]]}
        if r["key"] == cover_old and r.get("role") == "Kapak":
            r = {**r, "key": COVER5_KEY, "caption": COVER5_CAPTION, "seen": COVER5_CAPTION}
        out.append(r)
    (D / "selected_denetim_oncesi.jsonl").write_text((W / "foto" / "selected.jsonl").read_text(encoding="utf-8-sig"), encoding="utf-8")
    wjl(W / "foto" / "selected.jsonl", out)
    (D / "son_karar.json").write_text(json.dumps(by_key, ensure_ascii=False, indent=0), encoding="utf-8")
    print(json.dumps({"cikan": dropped, "beklenen_cikan": len(DROP), "selected": len(out), "karar_key": len(by_key)}, ensure_ascii=False))
    return 0 if dropped == len(DROP) else 2


def son() -> int:
    by_key = json.loads((D / "son_karar.json").read_text(encoding="utf-8"))
    rows, missing = [], []
    for r in jl(W / "foto" / "secim_temiz.jsonl"):
        k = by_key.get(r["key"])
        if k is None:
            missing.append(r["photo_id"])
            continue
        rows.append({"photo_id": r["photo_id"], **k})
    arsiv = INS / "denetim_arsiv"
    arsiv.mkdir(exist_ok=True)
    for p in INS.glob("denetim_*.jsonl"):
        shutil.move(str(p), str(arsiv / p.name))
    wjl(INS / "denetim_son.jsonl", rows)
    print(json.dumps({"satir": len(rows), "kararsiz": missing}, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(hazirla() if sys.argv[1] == "hazirla" else son())
