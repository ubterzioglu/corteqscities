"""Foto D3 ek turu: karar.jsonl'deki degistir/cikar kararlarini uygular.

1) Aday dosyalarinda olmayan yeni Commons dosyalari icin imageinfo+extmetadata (commons_search fonksiyonlariyla,
   ana onbellek) -> foto_d3/search.jsonl; candidates.jsonl ayrica photo_candidates from-search ile uretilir.
2) foto/selected.jsonl: degistir -> ayni satirda key/caption/seen degisir (ayni sira = ayni photo_id);
   cikar -> satir silinir (photo_rows numarayi slug basina sirayla verdigi icin kalanlar bosluksuz kayar).
Kullanim: python -I d3_hazirla.py search | select
"""
from __future__ import annotations

import glob
import json
import sys
from pathlib import Path

W = Path(r"C:\temp_private\corteqs\0000_newera\uretim\sevilla\_is")
TK = Path(r"C:\temp_private\corteqs\0000_newera\corteqs-skills\toolkit\scripts")
D3 = W / "foto_d3"
SKIP = "S14-yedek"
# karar satirindaki 'gorulen'den kisaltildi (<=250, yalniz karede gorulen; mekanin diger kare alt yazilarindan farkli)
CAPTIONS = {
    "sevilla:photo:iglesia-de-san-vicente-01": "San Vicente Kilisesi'nin üç nefli içi: koyu ahşap mudéjar tavan, "
                                               "sivri kemerler ve apsiste altın kaplama ana retablo.",
    "sevilla:photo:estadio-benito-villamarin-tur-02": "Gün ışığında La Cartuja Stadı'nın içi: oval çatı kenarı, "
                                                      "yeşil-beyaz kalabalık tribünler ve sahada açılış töreni.",
    "sevilla:photo:estadio-benito-villamarin-tur-03": "Gece maç ışıkları altında La Cartuja Stadı'nın tribünleri ve "
                                                      "sahası, panoda 'Forever Green' yazısı.",
    "sevilla:photo:catedral-de-sevilla-giralda-02": "Açık mavi gökyüzü altında Sevilla Katedrali'nin kubbesi, sivri "
                                                    "kuleleri ve Giralda'nın tamamı.",
    "sevilla:photo:caac-centro-andaluz-arte-contemporaneo-01": "Ağaçlı meydandan Endülüs Çağdaş Sanat Merkezi'nin "
                                                               "girişi: kırmızı tabela, baca ve gül pencereli kilise cephesi.",
    "sevilla:photo:el-patio-sevillano-01": "El Patio Sevillano'nun Paseo de Cristóbal Colón'daki sarı-beyaz cephesi, "
                                           "çini tabelası ve 'FLAMENCO' pankartları.",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def decisions() -> list[dict]:
    return [d for d in read_jsonl(D3 / "karar.jsonl") if d.get("bulgu") != SKIP]


def candidate_ids() -> set[str]:
    files = [W / "foto" / "candidates.jsonl"] + [Path(p) for p in sorted(glob.glob(str(W / "foto_*" / "candidates.jsonl")))
                                                  if Path(p).parent != D3]
    return {r.get("candidate_id") for f in files for r in read_jsonl(f)}


def run_search() -> int:
    sys.path.insert(0, str(TK))
    import commons_search as cs
    have = candidate_ids()
    need = [d for d in decisions() if d["karar"] == "degistir"
            and f"{d['entry_id']}|{d['yeni_commons_file']}" not in have]
    client = cs.Client(cs.urllib_transport, W / "foto" / "cache", 20)
    infos = cs.fetch_imageinfo(client, [cs.norm_title(d["yeni_commons_file"]) for d in need])
    rows, missing = [], []
    for d in need:
        title = cs.norm_title(d["yeni_commons_file"])
        if title not in infos:
            missing.append(title)
            continue
        rows.append({"entry_id": d["entry_id"], "query_kind": "elle_karar_d3", "title": title, "imageinfo": infos[title]})
    (D3 / "search.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    print(json.dumps({"need": len(need), "written": len(rows), "missing": missing,
                      "titles": [r["title"] for r in rows]}, ensure_ascii=False))
    return 1 if missing else 0


def run_select() -> int:
    sel_path = W / "foto" / "selected.jsonl"
    selected = read_jsonl(sel_path)
    clean = {r["photo_id"]: r for r in read_jsonl(W / "foto" / "secim_temiz.jsonl")}
    by_key = {r["key"]: i for i, r in enumerate(selected)}
    replaced, removed, problems = [], [], []
    drop_idx: set[int] = set()
    new_rows = list(selected)
    for d in decisions():
        if d["karar"] == "tut":
            continue
        old = clean.get(d["photo_id"])
        if not old or old.get("entry_id") != d["entry_id"] or old["key"] not in by_key:
            problems.append(f"photo_id bulunamadi: {d['photo_id']}")
            continue
        idx = by_key[old["key"]]
        if d["karar"] == "cikar":
            drop_idx.add(idx)
            removed.append(d["photo_id"])
        elif d["karar"] == "degistir":
            key = f"{d['entry_id']}|{d['yeni_commons_file']}"
            if key in by_key:
                problems.append(f"yeni anahtar zaten secimde: {key}")
                continue
            cap = CAPTIONS[d["photo_id"]]
            new_rows[idx] = {**selected[idx], "key": key, "caption": cap, "seen": cap}
            replaced.append(d["photo_id"])
    if problems:
        print(json.dumps({"problems": problems}, ensure_ascii=False))
        return 2
    out = [r for i, r in enumerate(new_rows) if i not in drop_idx]
    sel_path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out), encoding="utf-8")
    print(json.dumps({"selected_before": len(selected), "selected_after": len(out), "replaced": replaced,
                      "removed": removed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(run_search() if sys.argv[1] == "search" else run_select())
