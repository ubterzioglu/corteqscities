"""Dikey kare degisimi: ana dongu foto_dikey\\pafta\\sheet_01..09'a bakti (26.10.2026); secim = photo_id -> aday sirasi.
foto\\selected.jsonl'de ayni satir yerinde degisir (ayni sira = ayni photo_id). Alt yazilar karede gorulen.
Kullanim: python -I uygula.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
D = W / "foto_dikey"
P = "sevilla:photo:"
PICKS = {
    "convento-de-santa-ines-02": (1, "Santa Inés Manastırı'nın beyaz badanalı cephesi ve oymalı taş çerçeveli ahşap kapısı."),
    "monasterio-de-san-clemente-03": (1, "San Clemente Manastırı'nın uzun beyaz duvarı ve çan kulesi, önünde ağaçlar ve sokak."),
    "capilla-del-carmen-triana-03": (3, "Triana Köprüsü'nün ucundaki Capilla del Carmen'in tuğla kulesi ve çinili kubbesi, yanında Guadalquivir."),
    "iglesia-de-santa-maria-la-blanca-01": (1, "Santa María la Blanca Kilisesi'nin gotik sivri kemerli taş kapısı ve ahşap kanatları."),
    "museo-ve-plaza-nueva-02": (1, "Plaza Nueva'da San Fernando'nun atlı heykeli, fenerler ve meydanda yürüyen insanlar."),
    "sevilla-del-29-02": (3, "Plaza de España kanalının çinili korkulukları ve arkada yarım daire saray kanadı."),
    "cine-cervantes-sevilla-02": (1, "Cervantes Sineması salonunun kırmızı-altın süslemeli kubbeli tavanı, avizesi ve balkonları."),
    "cine-cervantes-sevilla-03": (2, "Cervantes Sineması'nın kırmızı perdeli sahnesi, önündeki koltuk sıraları ve balkonlar."),
    "parroquia-de-la-o-01": (1, "Nuestra Señora de la O Kilisesi cephesinde kırmızı zemin üzerinde melek kabartmalı barok süsleme."),
    "monasterio-de-san-jeronimo-de-buenavista-01": (1, "San Jerónimo de Buenavista Manastırı'nın taş çan kulesi ve uzun dış duvarı, önünde selvi."),
    "iglesia-de-santa-marina-01": (2, "Santa Marina Kilisesi'nin sivri kemerli nefi, sıra sıra oturaklar ve apsisteki sunak."),
    "iglesia-de-santa-marina-02": (1, "Santa Marina Kilisesi'nin tuğla saçağı altındaki aslan başı biçimli taş konsollar."),
    "archivo-historico-provincial-de-sevilla-01": (1, "İl Tarih Arşivi'nin uzun neoklasik cephesi, sıra pencereleri ve önündeki sokak."),
    "real-alcazar-de-sevilla-01": (2, "Alcázar'daki Patio de las Doncellas: oymalı mudéjar kemerler, üst kat galerisi ve ortadaki uzun havuz."),
    "real-alcazar-de-sevilla-02": (1, "Alcázar bahçelerinden Jardín de las Damas: palmiyeler, budanmış çitler ve arkada saray duvarları."),
    "palacio-de-las-duenas-02": (1, "Dueñas Sarayı'nın sarı çerçeveli giriş kapısı, üstündeki çini arma ve beyaz duvarlar."),
    "palacio-de-las-duenas-03": (3, "Dueñas Sarayı giriş kemerinin üstündeki çini arma ve sarı kemer çerçevesi."),
    "palacio-de-la-condesa-de-lebrija-01": (3, "Lebrija Sarayı'nın Roma mozaikli avlusu, kemerli revaklar ve saksı bitkileri."),
    "palacio-de-la-condesa-de-lebrija-02": (1, "Lebrija Sarayı'nın ahşap korkuluklu ana merdiveni ve çinili duvarları."),
    "metropol-parasol-antiquarium-01": (2, "Metropol Parasol'ün tepesindeki yürüme yolundan ahşap petek çatı ve ardında Sevilla'nın damları."),
    "capilla-de-los-marineros-01": (1, "Capilla de los Marineros'un içi: kırmızı perdeli nişte haç taşıyan İsa heykeli ve sunak."),
    "costurero-de-la-reina-01": (1, "Costurero de la Reina'nın kırmızı-beyaz çizgili, mazgallı küçük köşkü ve önündeki yol."),
    "costurero-de-la-reina-03": (2, "Costurero de la Reina'nın çizgili duvarında oymalı kemerli pencereler ve demir balkon."),
    "espacio-santa-clara-01": (1, "Santa Clara'nın ince sütunlu revaklarla çevrili manastır avlusu ve ortadaki bahçe."),
    "espacio-santa-clara-03": (3, "Espacio Santa Clara'nın bahçe avlusu, tuğla duvar ve avluda yürüyen ziyaretçiler."),
    "parque-de-maria-luisa-02": (1, "María Luisa Parkı'nda çimen, çiçek tarhı, küçük havuz ve sık ağaçlar."),
    "parque-de-maria-luisa-03": (3, "María Luisa Parkı'nda palmiyeler ve ağaçlar arasında uzanan geniş toprak yol."),
    "jardines-de-las-delicias-03": (2, "Delicias Bahçeleri'nde palmiyeler ve ağaçlarla çevrili çimenlik ve kum yol."),
    "museo-de-artes-y-costumbres-populares-01": (1, "Halk Sanatları ve Gelenekleri Müzesi'nde seramik tabaklarla döşenmiş eski bir mutfak odası."),
    "museo-de-artes-y-costumbres-populares-02": (2, "Halk Sanatları ve Gelenekleri Müzesi'nde tezgâh ve aletlerle kurulmuş eski bir zanaat atölyesi."),
    "real-academia-bellas-artes-sevilla-01": (1, "Casa de los Pinelo'nun kemerli avlusu, ortadaki çeşme ve saksı bitkileri."),
    "palacio-marqueses-de-la-algaba-02": (1, "Algaba Markizleri Sarayı'nın tuğla cephesi, taş çerçeveli kapısı ve yanındaki kule."),
    "palacio-marqueses-de-la-algaba-03": (3, "Algaba Markizleri Sarayı'nın taş çerçeveli büyük ahşap kapısı."),
    "casa-de-la-provincia-sevilla-01": (1, "Plaza Nueva'daki Casa de la Provincia'nın kırmızı-beyaz cephesi, bayraklar ve fenerler."),
    "teatro-central-sevilla-02": (1, "Guadalquivir'in karşı kıyısından Teatro Central'in yapısı ve kıyıdaki ağaçlar."),
    "el-rinconcillo-02": (1, "El Rinconcillo'nun yeşil tabelalı eski dükkân cephesi ve çini süslemeli duvarı."),
    "catedral-de-sevilla-giralda-03": (3, "Sevilla Katedrali'nin gotik yan cephesi, Giralda kulesi ve önündeki fayton sırası."),
    "casa-de-pilatos-02": (1, "Casa de Pilatos'ta oymalı alçı süslemeli mudéjar kemerler ve madalyonlar."),
    "basilica-de-la-macarena-01": (1, "Macarena Bazilikası'nın sarı-beyaz barok cephesi ve kapı üstündeki çan kulesi."),
    "basilica-de-la-macarena-03": (3, "Macarena Bazilikası'nın içinde freskli tonoz ve oymalı ahşap koro."),
    "iglesia-de-san-luis-de-los-franceses-03": (1, "San Luis de los Franceses Kilisesi'nin içi: freskli tonoz, kubbe ve yaldızlı sunaklar."),
    "convento-de-santa-paula-02": (1, "Santa Paula Manastırı'nın iki katlı kemerli avlusu, kemer arasından görünüm."),
    "convento-de-santa-paula-03": (2, "Santa Paula Manastırı'nın beyaz revaklı avlusu ve ortadaki çeşme."),
    "iglesia-de-santa-catalina-01": (2, "Santa Catalina Kilisesi'nin gotik sivri kemerli taş kapısı ve kademeli kemer süslemeleri."),
    "iglesia-de-santa-catalina-03": (1, "Santa Catalina Kilisesi'nde yaldızlı oyma retablo ve ortasında haç."),
    "iglesia-de-san-marcos-02": (1, "San Marcos Kilisesi'nin beyaz badanalı nefi, kemerler ve sıralar."),
    "santa-cruz-02": (1, "Santa Cruz semtinin damları ve kubbeli kilise, ardında şehrin uzanan çatıları."),
    "los-remedios-02": (1, "Guadalquivir'in karşı kıyısında Los Remedios'un apartmanları ve nehirde tur teknesi."),
    "la-macarena-02": (2, "Macarena Kemeri: sarı-beyaz barok kapı, üstündeki çini Meryem panosu ve sivri süslemeler."),
    "nervion-01": (2, "Nervión'da El Corte Inglés mağazasının çok katlı cephesi ve önündeki cadde."),
    "nervion-02": (3, "Nervión'da El Corte Inglés binasının yan cephesi, ağaçlı kaldırım ve cadde."),
    "la-cartuja-02": (2, "Santa María de las Cuevas Kartuzyen Manastırı'nın sarı duvarı, kemerli giriş kapısı ve çan kulesi."),
    "el-porvenir-02": (2, "El Porvenir'de Güney ilçe karakolu ve ilçe binası: tuğla ve taş cephe, bayraklar."),
    "auditorio-cartuja-sevilla-03": (2, "Auditorio Cartuja'nın Sala Oasis bölümü: yüksek masalar, tabureler ve yeşil duvar."),
    "real-fabrica-de-artilleria-02": (1, "Top Fabrikası'nın çatı pencereli uzun iç holü ve taş zemini."),
    "real-fabrica-de-artilleria-03": (2, "Top Fabrikası'nın kemerli geçidinden avlu ve karşıdaki kiremit çatılı yapı."),
    "jardines-de-cristina-02": (1, "Cristina Bahçeleri'nde ağaçların gölgesinde beyaz sütunlu pergola."),
    "casa-de-salinas-02": (1, "Casa de Salinas'ın kırmızı duvarlı avlusunda taş yalak, sütun başlığı ve saksılar."),
    "iglesia-de-san-nicolas-de-bari-02": (1, "San Nicolás de Bari Kilisesi'nin sarı çan kulesi ve çanları."),
    "iglesia-de-omnium-sanctorum-01": (1, "Omnium Sanctorum Kilisesi'nin beyaz cephesi, gül penceresi ve sivri kemerli kapısı."),
    "iglesia-de-san-esteban-02": (1, "San Esteban Kilisesi'nin mazgallı tuğla yan duvarı, gotik kapısı ve çan kulesi."),
}


def jl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8-sig").splitlines() if l.strip()]


def main() -> int:
    cands = {(r["photo_id"], r["sira"]): r for r in jl(D / "adaylar.jsonl")}
    key_of = {r["photo_id"]: r["key"] for r in jl(W / "foto" / "secim_temiz.jsonl")}
    sel_path = W / "foto" / "selected.jsonl"
    selected = jl(sel_path)
    index = {r["key"]: i for i, r in enumerate(selected)}
    problems, new_keys = [], {}
    for short, (rank, caption) in PICKS.items():
        pid = P + short
        cand = cands.get((pid, rank))
        old = key_of.get(pid)
        if not cand or old not in index:
            problems.append(f"{short}: aday ya da eski satir yok")
            continue
        if len(caption) > 250:
            problems.append(f"{short}: alt yazi uzun")
        new_keys[pid] = (index[old], cand["key"], caption)
    files = [k.split("|", 1)[-1] for _, k, _ in new_keys.values()]
    dup = {f for f in files if files.count(f) > 1}
    if dup:
        problems.append(f"ayni dosya iki kez: {sorted(dup)}")
    if problems:
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 2
    (D / "selected_oncesi.jsonl").write_text(sel_path.read_text(encoding="utf-8-sig"), encoding="utf-8")
    out = list(selected)
    for pid, (i, key, caption) in new_keys.items():
        out[i] = {**selected[i], "key": key, "caption": caption, "seen": caption}
    sel_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    # ana dongu incelemesi: ek tur karar dosyasi (kanit_teslim 'degistir' satirlarini 'ek tur karari' olarak okur)
    karar = [{"photo_id": pid, "entry_id": out[i]["entry_id"], "bulgu": "C4-dikey", "karar": "degistir",
              "yeni_commons_file": key.split("|", 1)[-1], "gorulen": caption, "ek_hak": "yok",
              "gerekce": "dikey kare 16:9/4:3 yuvada alanin yarisini kaybediyordu; ayni kaydin yatay, Own work, lisansi uygun adayi"}
             for pid, (i, key, caption) in new_keys.items()]
    (D / "karar.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in karar), encoding="utf-8")
    print(json.dumps({"degisen": len(new_keys), "selected": len(out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
