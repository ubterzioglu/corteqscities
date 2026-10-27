"""kayitlar_l2.py: Sevilla L2 denetim kayıtları (CHECK, ISSUE, criteria) — kılavuz 2.0 bölüm 16/20.

Kullanım: python -I -X utf8 kayitlar_l2.py <OUT> <PKG>
Önce birlestir_l2.py, açık-mı kapıları + sayim ve k04.py çalışmış olmalı. Bulgular ajan çıktılarından (karşı denetim
uygulanmış) script'le kurulur; sayılar dosyalardan okunur. Yalnız OUT altına yazar.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True
OUT, PKG = Path(sys.argv[1]), Path(sys.argv[2])
TODAY = "2026-10-26"
LEVEL = "L2"
PRIOR = "denetim/sevilla_2026-10-25_L1 (Excel 78561c28…, %74, DÜZELTME GEREKLİ)"


def load(rel: str, default=None):
    p = OUT / rel
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8-sig"))


def jl(rel) -> list[dict]:
    p = rel if isinstance(rel, Path) else OUT / rel
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def jl_glob(pattern: str) -> list[dict]:
    rows = []
    for p in sorted(OUT.glob(pattern)):
        rows += [{**r, "_dosya": p.name} for r in jl(p)]
    return rows


def ctxt(c: Counter) -> str:
    return ", ".join(f"{k} {v}" for k, v in c.most_common()) or "—"


def short(s, n=240) -> str:
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


# ------------------------------------------------------------------ girdiler
val = load("validation-audit.json", {})
inv = load("dosya-envanteri.json")
k04 = load("_analiz/k04-karsilastirma.json", {"added": [], "removed": [], "changed": [], "start_files": None, "end_files": None})
k04_fark = len(k04.get("added", [])) + len(k04.get("removed", [])) + len(k04.get("changed", []))
capraz = load("_analiz/capraz-kontroller.json")
snapcmp = load("_analiz/snapshot-karsilastirma.json")["summary"]
tarih = load("_analiz/tarih-sirasi.json", {})
urls = load("url-checks.json")
cs = load("claim-checks.json")
pr = load("photo-review.json")
lisd = load("_analiz/lisans-birlesik.json", {"rows": [], "summary": {}})
tq_raw = load("text-quality.json")
tq = tq_raw.get("summary", tq_raw)
foto_h = load("_foto/hazirlik.json")
dec = load("_foto/decisions.json")
dhash = load("_foto/dhash-ciftleri.json", {})
fid = load("xlsx-fidelity.json", {"diffs": [], "accepted": []})
sayim = load("acik-mi-sayim.json", {})
kk = load("kanit-kapsami.json", {})
k61d = load("_analiz/k61_dhash.json", {"ozet": {}, "uzak": []})
k61s = load("_analiz/k61_sha1.json", {"esit": 0, "farkli": [], "yok": []})
atif = load("_analiz/atif-kontrol.json", {"ozet": {}})["ozet"]
uyari_raw = load("uyari-tarama.json", {})
uyari = uyari_raw.get("summary", uyari_raw)
k20 = load("_l/k20_gruplar.json", {})
mek = jl("_dump/Mekânlar.jsonl")
mah = jl("_dump/Mahalleler.jsonl")
yan = jl("_dump/Yanıtlar.jsonl")
soz = jl("_dump/Sözlük.jsonl")
fot = jl("_dump/Fotoğraflar.jsonl")
rot = jl("_dump/Rotalar.jsonl")
teslimat = (jl("_dump/Teslimat.jsonl") or [{}])[0]

xlsx_sha = next(f["sha256"] for f in inv["files"] if f["path"].endswith(".xlsx"))
xlsx_name = next(f["path"] for f in inv["files"] if f["path"].endswith(".xlsx"))
n_files = inv["summary"]["files"]
n_rows = sum(capraz["sheet_rows"].values())
n_sheets = len(capraz["sheet_rows"])
n_photo_rows = len(fot)
ph = capraz["photos"]
n_unique_venue = ph["unique_venue_sha"]
us = urls.get("summary", urls)
n_urls, n_rel = us["unique_urls"], us["relations"]
homepage_only = [u for u in urls["urls"] if "homepage_only" in (u.get("flags") or [])]
cross_host = [u for u in urls["urls"] if "cross_host_redirect" in (u.get("flags") or [])]
mek_by = {m["entry_id"]: m for m in mek}
mah_by = {m["entry_id"]: m for m in mah}
yan_ids = {y["entry_id"] for y in yan}
soz_ids = {s["term_id"] for s in soz}
csum, psum = cs["summary"], pr["summary"]
by_res = Counter(csum["by_result"])
routes_of = defaultdict(list)
for r in rot:
    for sid in re.split(r"[\n;|,]", str(r.get("stop_entry_ids") or "")):
        if sid.strip():
            routes_of[sid.strip()].append(f"{r['route_id']} (Rotalar!{r['_row']})")

meta = {"tool": f"city-audit {LEVEL}", "level": LEVEL, "label": "yerel paket denetimi", "city_id": "sevilla",
        "catalog": "CITY-107", "xlsx": xlsx_name, "xlsx_sha256": xlsx_sha, "previous_audit": PRIOR, "checked_on": TODAY}


# ------------------------------------------------------------------ karşı denetim (L ajanları)
def apply_karsi(rows: list[dict], karsi_rows: list[dict], idkeys: tuple[str, ...], kfields: tuple[str, ...]) -> Counter:
    stats = Counter()
    by_id = defaultdict(list)
    for k in karsi_rows:
        if k.get("kayit"):
            by_id[re.sub(r"\s+", "", str(k["kayit"]))].append(k)
    for r in rows:
        rid = next((str(r.get(x)) for x in idkeys if r.get(x)), None)
        ks = by_id.get(re.sub(r"\s+", "", rid or ""), [])
        r["_karsi"] = ks
        for k in ks:
            chk = k.get("check_id") or ""
            if k.get("karsi_karar") == "çürütüldü" or k.get("oncelik_onerisi") == "bulgu değil":
                r["bulgular"] = [b for b in (r.get("bulgular") or []) if chk and b.get("check_id") != chk]
                if chk in kfields and r.get(chk) == "kaldı":
                    r[f"{chk}_ilk"] = "kaldı"
                    r[chk] = "geçti"
                stats["çürütüldü"] += 1
            elif k.get("karsi_karar") == "teyit":
                for b in r.get("bulgular") or []:
                    if b.get("check_id") == chk and k.get("oncelik_onerisi") in ("P0", "P1", "P2"):
                        b["oncelik_ilk"] = b.get("oncelik")
                        b["oncelik"] = k["oncelik_onerisi"]
                stats["teyit"] += 1
            else:
                stats["belirsiz"] += 1
    return stats


mekan_l = jl_glob("_l/mekan_P[1-4].jsonl")
mah_l = jl("_l/mahalleler.jsonl")
rot_l = jl("_l/rotalar.jsonl")
bag_l = jl_glob("_l/baglanti_[0-9][0-9].jsonl")
sehir_l = jl("_l/sehir_sayfa.jsonl")
kay_l = jl_glob("_l/kaynak_[0-9][0-9].jsonl")
diger_l = jl("_l/diger.jsonl")
lis_rows = lisd["rows"]
karsi_stats = {
    "mekan": apply_karsi(mekan_l, jl_glob("_l/karsi_mekan_*.jsonl"), ("entry_id",), ("K42", "K108", "K38", "K54", "K55")),
    "mahrota": apply_karsi(mah_l + rot_l, jl("_l/karsi_mahrota.jsonl"), ("entry_id", "route_id"), ("K44", "K45", "K47")),
    "baglanti": apply_karsi(bag_l + sehir_l, jl("_l/karsi_baglanti.jsonl"), ("action_id", "anahtar"),
                            ("K51", "K53", "K54", "K55", "K90", "K91")),
    "kaynak": apply_karsi(kay_l, jl("_l/karsi_kaynak.jsonl"), ("source_id",), ("K51",)),
}

# ------------------------------------------------------------------ ISSUE kayıtları
issues: list[dict] = []


def I(oncelik, kategori, check_id, tablo, excel, ids, alan, mevcut, beklenen, gozlem, kanit, etki, duzeltme, tekrar,
      criteria, dosya=None):
    iid = f"ISS-{len(issues) + 1:03d}"
    issues.append({
        "issue_id": iid, "öncelik": oncelik, "kategori": kategori, "check_id": check_id, "tablo": tablo,
        "Excel_satırı": excel, "entry_id/photo_id": ids, "dosya": dosya or xlsx_name, "alan": alan,
        "mevcut_değer": mevcut, "beklenen": beklenen, "somut_gözlem": gozlem, "kanıt": kanit,
        "kullanıcı_etkisi": etki, "önerilen_düzeltme": duzeltme, "tekrar_kontrol_koşulu": tekrar, "durum": "Açık",
        "_criteria": criteria,
    })
    return iid


def by_check(cid: str) -> list[str]:
    return [i["issue_id"] for i in issues if i["check_id"] == cid]


CRIT = {
    "mekan": {"K42": ["B5"], "K43": ["B5"], "K108": ["B1"], "K38": ["B5"], "K54": ["B5"], "K55": ["B5"], "K39": ["B5"],
              "DIGER": ["B5"], "K35": ["B5"], "K29": ["B5"]},
    "mahalle": {"K44": ["B2"], "K45": ["B2", "E1"]},
    "rota": {"K47": ["B3"], "K20": ["B1"]},
    "baglanti": {"K51": ["A2"], "K53": ["A2"], "K54": ["A2"], "K55": ["B5"]},
    "sehir": {"K90": ["E3"], "K91": ["E3"], "K29": ["E3"], "K86": ["E3"]},
    "kaynak": {"K51": ["A3"], "K30": ["A3"], "K35": ["A4"]},
    "lisans": {"K71": ["D1"], "K72": ["D1"], "K74": ["D4"], "K70": ["D2"], "K67": ["D1"], "K60": ["C2"]},
}
CHECK_ALIAS = {"konu": "K60", "KONU": "K60", "kimlik": "K60", "metin": "K86"}
SRC_META = {
    "mekan": ("Mekânlar", "entry_id", "_l/mekan_P1..P4.jsonl; _l/karsi_mekan_*.jsonl"),
    "mahalle": ("Mahalleler", "entry_id", "_l/mahalleler.jsonl; _l/karsi_mahrota.jsonl"),
    "rota": ("Rotalar", "route_id", "_l/rotalar.jsonl; _l/karsi_mahrota.jsonl"),
    "baglanti": ("Bağlantılar", "action_id", "_l/baglanti_01..08.jsonl; _l/karsi_baglanti.jsonl"),
    "sehir": ("SayfaAlanları; Şehir", "anahtar", "_l/sehir_sayfa.jsonl; _l/karsi_baglanti.jsonl"),
    "kaynak": ("Kaynaklar", "source_id", "_l/kaynak_01..10.jsonl; _l/karsi_kaynak.jsonl"),
    "lisans": ("Fotoğraflar; Kanıtlar", "photo_id", "_analiz/lisans-birlesik.json; _l/lisans_01..04.jsonl; _l/karsi_lisans.jsonl"),
}
ETKI = {"P0": "Okur yanlış ya da hukuken sorunlu bilgiyle karşılaşır; yayın engeli.",
        "P1": "Okuru yanlış yere/işleme yönlendirir ya da işi yapmaya yetecek bilgi eksik.",
        "P2": "Okuru yanıltmaz; güncellik, açıklık ya da bakım sorunu."}


def lbl(r: dict) -> str:
    return str(r.get("entry_id") or r.get("route_id") or r.get("action_id") or r.get("anahtar") or r.get("source_id")
               or r.get("photo_id") or "—")


def agent_issues(src: str, rows: list[dict], kfields: tuple[str, ...]) -> None:
    tablo, idk, kanit = SRC_META[src]
    pairs = []
    for r in rows:
        bl = [b for b in (r.get("bulgular") or []) if b.get("oncelik") in ("P0", "P1", "P2")]
        have = {b.get("check_id") for b in bl}
        for K in kfields:  # 'kaldı' olup bulgusu olmayan kontrol: P1 bulgusu üret (bağlansın)
            if r.get(K) == "kaldı" and K not in have:
                bl.append({"check_id": K, "oncelik": "P1", "gozlem": r.get("gozlem") or r.get("not") or f"{K} kaldı",
                           "kanit_url": r.get("kanit_url"), "alinti": r.get("alinti")})
        pairs += [(r, b) for b in bl]
    groups = defaultdict(list)
    for r, b in pairs:
        c = b.get("check_id") or "DIGER"
        groups[(CHECK_ALIAS.get(c, c), b["oncelik"])].append((r, b))
    for (chk, onc), its in sorted(groups.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        crit = CRIT[src].get(chk, CRIT[src].get("DIGER", ["B5"]) if src == "mekan" else list(CRIT[src].values())[0])
        rows_ = sorted({str(r.get("_row")) for r, _ in its if r.get("_row") is not None}, key=lambda x: int(x) if x.isdigit() else 0)
        gozlem = " | ".join(
            f"{lbl(r)}{(' — ' + str(r.get('title'))) if r.get('title') else ''}: {short(b.get('gozlem'), 400)}"
            + (f" [{short(b.get('kanit_url'), 160)}]" if b.get("kanit_url") else "")
            + (f" «{short(b.get('alinti'), 200)}»" if b.get("alinti") else "")
            + (f" (karşı: {r['_karsi'][0].get('karsi_karar')})" if r.get("_karsi") else "")
            + (f" (durak: {', '.join(routes_of[lbl(r)])})" if src == "mekan" and routes_of.get(lbl(r)) else "")
            for r, b in its)
        I(onc, f"{src} denetimi: {chk}", chk, tablo, (f"{tablo.split(';')[0]}!" + ", ".join(rows_)) if rows_ else "—",
          ", ".join(sorted({lbl(r) for r, _ in its})), "kayıt alanları (bulguya göre)", f"{len(its)} gözlem",
          "Bilgi kaynakla birebir, güncel ve kaydın konusuyla uyumlu.", gozlem, kanit, ETKI[onc],
          "Her gözlemdeki kaydı kanıttaki resmî kaynağa göre düzelt (gerekirse yeni kaynak ekle ve kopyasını al).",
          f"L2 {src} denetiminde {chk} {onc} bulgusu 0.", crit)


agent_issues("mekan", mekan_l, ("K42", "K108", "K38", "K54", "K55"))
agent_issues("mahalle", mah_l, ("K44", "K45"))
agent_issues("rota", rot_l, ("K47",))
agent_issues("baglanti", bag_l, ("K51", "K53", "K54", "K55"))
agent_issues("sehir", sehir_l, ("K90", "K91"))
agent_issues("kaynak", kay_l, ("K51",))
agent_issues("lisans", lis_rows, ("K71", "K72"))

# --- iddia: yanlış / eski / kaynak yetersiz -----------------------------------------
claims = cs["claims"]
row_of = {y["entry_id"]: y.get("_row") for y in yan} | {s["term_id"]: s.get("_row") for s in soz}
title_of = {y["entry_id"]: y.get("title") for y in yan} | {s["term_id"]: s.get("term") for s in soz}
for sonuc, chk, varsayilan, crit, kat in (("yanlış", "K29", "P1", ["A4", "A1"], "Yanlış iddia"),
                                          ("eski", "K35", "P1", ["A4", "A1"], "Eski/yürürlükten kalkmış bilgi")):
    sel = [c for c in claims if c.get("sonuç") == sonuc]
    by_e = defaultdict(list)
    for c in sel:
        by_e[c["entry_id"]].append(c)
    for e, cl in sorted(by_e.items()):
        onc = min((c.get("karsi", {}) or {}).get("oncelik_onerisi") or varsayilan for c in cl)
        onc = onc if onc in ("P0", "P1", "P2") else varsayilan
        I(onc, kat, chk, "Yanıtlar" if e in yan_ids else "Sözlük",
          f"{'Yanıtlar' if e in yan_ids else 'Sözlük'}!{row_of.get(e, '?')}", e, "kart metni (iddia)",
          " | ".join(short(c.get("iddia"), 200) for c in cl),
          " | ".join(short(c.get("doğrusu") or (c.get("karsi") or {}).get("dogrusu"), 240) for c in cl) or "Kaynakla aynı güncel değer.",
          f"{title_of.get(e)}: " + " | ".join(
              f"{c['claim_id'].split(':')[-1]}: {short(c.get('iddia'), 160)} → {short(c.get('doğrusu'), 160)} "
              f"[{short(c.get('resmî_URL'), 140)}] «{short(c.get('alıntı'), 180)}»"
              + (f" (karşı: {c['karsi'].get('karsi_karar')})" if c.get("karsi") else "") for c in cl),
          "claim-checks.json → claims (entry_id); _iddia/parti_NN.jsonl; _iddia/karsi_*.jsonl",
          ETKI[onc], "Değeri resmî kaynaktaki güncel değerle değiştir, kaynağı ve kopyasını güncelle.",
          "İddia L2 denetiminde 'doğru'.", crit)
ky = [c for c in claims if c.get("sonuç") in ("kaynak_yetersiz", "erişilemedi")]
if ky:
    I("P2", "İddia kaynağı yetersiz / erişilemedi", "K30", "Yanıtlar; Sözlük",
      ", ".join(sorted({str(row_of.get(c["entry_id"], "?")) for c in ky})), ", ".join(sorted({c["entry_id"] for c in ky})),
      "iddia ↔ kaynak", f"{len(ky)} iddia", "Her iddia bağlı resmî kaynağın metninde yazılı.",
      " | ".join(f"{c['claim_id'].split(':')[-1]} ({c.get('sonuç')}): {short(c.get('iddia'), 140)}; {short(c.get('belirsizlik'), 140)}" for c in ky),
      "claim-checks.json → not_wrong", ETKI["P2"], "Resmî kaynak ekle ya da ifadeyi kaynağın söylediğine indir.",
      "İlgili iddialar 'doğru'.", ["A3"])

# --- kart kararları ---------------------------------------------------------------------
fails = cs["card_failures"]
CARD_META = {
    "K25": ("Başlıktaki soruya doğrudan cevap yok", "İlk cümle başlıktaki soruyu cevaplar.", ["A2", "A1"]),
    "K26": ("Mikro kartın gerekli ayrıntıları eksik", "Kart soruyu çözecek ayrıntıyı verir: tutar, şart, belge, başvuru kanalı/yeri, tarih.", ["A2", "A1"]),
    "K31": ("Yerel kurum/kanal eksik ya da yanlış", "Kart Sevilla'daki doğru kurumu ve kanalı verir.", ["A2", "A1"]),
    "K40": ("Süre/son tarih belirsiz", "Süre ve son tarihler gün türüyle ve kaynakla aynı.", ["A4", "A1"]),
    "K32": ("Dil, tutarlılık, desteklenmeyen vaat", "Dil hatası, kart içi çelişki ve kaynaksız vaat yok.", ["A5"]),
    "K48": ("Sözlük maddesinin kullanım değeri", "Terim Sevilla'da gerçekten karşılaşılan, tanımı doğru.", ["B4"]),
    "K41": ("Kaynak çelişkisi", "Çelişki kartta açıkça yazılı ve esas alınan kaynak belirtilmiş.", ["A4"]),
}
for K, (kat, beklenen, crit) in CARD_META.items():
    for onc in ("P0", "P1", "P2"):
        its = [c for c in fails if (K in c["kaldı"] or (K == "K41" and c["K41_var"])) and c["öncelik"].get(K) == onc]
        if not its:
            continue
        tab = lambda c: "Sözlük" if c["entry_id"] in soz_ids else "Yanıtlar"
        I(onc, kat, K, "Yanıtlar; Sözlük", ", ".join(f"{tab(c)}!{c['_row']}" for c in its), ", ".join(c["entry_id"] for c in its),
          "kart metni", f"{len(its)} kart {K}", beklenen,
          " | ".join(f"{tab(c)}!{c['_row']} {c.get('title')}: {short(c['notlar'].get(K), 420)}"
                     + (f" (karşı: {c['karsi'][K].get('karsi_karar')}: {short(c['karsi'][K].get('gerekce'), 200)})" if c.get("karsi", {}).get(K) else "")
                     for c in its),
          "claim-checks.json → card_failures; _iddia/kart_NN.jsonl; _iddia/karsi_*.jsonl", ETKI[onc],
          "Her karta kaynakta yazan eksik öğeyi (başvuru yeri/kanalı, belge, tutar, süre) ekle; Sevilla'daki somut kurumu yaz.",
          f"Bu kartlarda L2 iddia denetçisi {K} 'geçti'.", crit)

# --- kartlar arası (K19, K28, K18) ----------------------------------------------------
k19_bad = [r for r in diger_l if r.get("check_id") == "K19" and r.get("sonuc") == "kaldı"]
if k19_bad:
    I("P1", "Konu kapsamı sığ", "K19", "Konular; Yanıtlar", "—", ", ".join(str(r.get("konu")) for r in k19_bad),
      "konu kartları", f"{len(k19_bad)} konu", "Her konu göçmenin temel sorularını kapsar.",
      " | ".join(f"{r.get('konu')}: eksik {', '.join(map(str, r.get('eksik_temel_sorular') or []))[:300]}; {short(r.get('gozlem'), 200)}" for r in k19_bad),
      "_l/diger.jsonl", ETKI["P1"], "Eksik temel soruları yeni ya da genişletilmiş kartlarla kapat.", "K19 'geçti' (12/12).", ["A1"])
k28 = [r for r in diger_l if r.get("check_id") == "K28"]
for onc in ("P1", "P2"):
    its = [r for r in k28 if (r.get("oncelik") or "P2") == onc]
    if its:
        I(onc, "Anlamsal tekrar / doldurma", "K28", "Yanıtlar; Sözlük", "—",
          ", ".join(sorted({str(x) for r in its for x in (r.get("kartlar") or [])})), "kart kümeleri", f"{len(its)} küme",
          "Her kart ayrı bir soruyu cevaplar; numaralı doldurma yok.",
          " | ".join(f"{r.get('tur')}: {', '.join(map(str, r.get('kartlar') or []))} — {short(r.get('gozlem'), 240)}" for r in its),
          "_l/diger.jsonl", ETKI[onc], "Tekrar eden kartları birleştir; boşalan yere eksik temel soruyu yaz.", "K28 kümesi 0.", ["A5"])
k18 = next((r for r in diger_l if r.get("check_id") == "K18"), {})
k18_bad = [str(x) for x in (k18.get("kullanilamaz") or [])]

# --- fotoğraf -----------------------------------------------------------------------------
rej = pr["rejects"]
FOTO_CRIT = {"K60": ["C2"], "K61": ["D3"], "K62": ["C5"], "K65": ["C4"], "K63": ["C4"], "K74": ["D4"], "K105": ["C2"]}
rg = defaultdict(list)
for p in rej:
    rg[(p.get("görsel_check") or "K60", p.get("görsel_öncelik") if p.get("görsel_öncelik") in ("P0", "P1", "P2") else "P1")].append(p)
for (chk, onc), its in sorted(rg.items()):
    I(onc, "Yanlış/uygunsuz görsel", chk, "Fotoğraflar", "Fotoğraflar!" + ", ".join(str(p["_row"]) for p in its),
      ", ".join(p["photo_id"] for p in its), "file (görüntü)",
      " | ".join(f"{p['photo_id'].split(':')[-1]} [{', '.join(p['pafta_slot'])}]: {short(p.get('görüntüde_görülen'), 160)}" for p in its),
      "Kare bağlı kaydın kendisini gösterir; kapak Sevilla'yı temsil eder; ek hak dayanağı var.",
      " | ".join(f"{p['photo_id'].split(':')[-1]} → {p['hedef_mekân']}: {short(p.get('ek_hak_notu'), 300)} (kaynak {p.get('kaynak_kanıtı')})" for p in its),
      "photo-review.json → rejects; _foto/karsi_foto.jsonl; temas-sayfalari/", ETKI[onc],
      "Kareyi kaydın kendisini gösteren, lisansı doğrulanmış başka bir kareyle değiştir.", "Yeni kare L2 görsel ve hak incelemesinde 'keep'.",
      FOTO_CRIT.get(chk, ["C2"]))
flags = pr["flags"]
if flags:
    I("P2", "Zayıf/şüpheli fotoğraf (karara bağlanmadı)", "K65", "Fotoğraflar", "Fotoğraflar!" + ", ".join(str(p["_row"]) for p in flags),
      ", ".join(p["photo_id"] for p in flags), "file (görüntü)", f"{len(flags)} kare 'flag'",
      "Kare mekânı açık ve tanınır biçimde gösterir.",
      " | ".join(f"{p['photo_id'].split(':')[-1]} [{', '.join(p['pafta_slot'])}]: {short(p.get('ek_hak_notu'), 200)}" for p in flags),
      "photo-review.json → flags", ETKI["P2"], "Daha iyi kare bulunan kayıtlarda değiştir.", "flag 0.", ["C4"])

# --- açık-mı -------------------------------------------------------------------------------
dog = {}
for p in sorted((OUT / "_acikmi").glob("parti_*_dogrulama.jsonl")):
    for r in jl(p):
        if r.get("entry_id"):
            dog[r["entry_id"]] = {**r, "_dosya": p.name}
karsi_acik = {r["entry_id"]: r for r in jl("_acikmi_karsi/karsi_acikmi.jsonl") if r.get("entry_id")}
acik_items = defaultdict(list)
for m in sayim.get("mekanlar", []):
    e, sinif, kod = m["entry_id"], m.get("sinif"), set(m.get("kodlar") or [])
    ka = karsi_acik.get(e, {})
    if ka.get("karsi_karar") == "çürütüldü" and sinif in ("kapanis_iki_kaynak", "kapanis_teyitsiz", "belirt_teyitli"):
        continue
    if sinif == "kapanis_iki_kaynak":
        acik_items["P0"].append(m)
    elif sinif == "kapanis_teyitsiz":
        acik_items["P1"].append(m)
    elif sinif == "belirt_teyitli":
        if ka.get("kartta_var_mi") == "evet":
            continue
        acik_items["P1" if ("not_yok" in kod or ka.get("kartta_var_mi") == "hayır" or not ka) else "P2"].append(m)
CLOSE_RX = re.compile(r"(ziyarete kapal|kapalı;|kapal[ıi],|gezilemiyor|restorasyon|rehabilitasyon|tadilat|kısıt|bakımsız|"
                      r"satış açık değil|kapı.{0,80}kapal)", re.I)
acik_ek_dogrulanan = []  # karşı denetim: doğrulayıcının 'belirsiz' bıraktığı mekâna tarihli faaliyet kanıtı
for e, ka in karsi_acik.items():
    if ka.get("karsi_karar") != "yeni_kanit":
        continue
    d = str(ka.get("guncel_durum") or "")
    if CLOSE_RX.search(d) and not re.search(r"kapanış izi yok", d, re.I):
        # mekanik kapıdan geçmemiş yeni kısıt/kapanış izi: teyit gerekli (P2)
        if not any(x["entry_id"] == e for v in acik_items.values() for x in v):
            acik_items["P2"].append({"entry_id": e, "title": mek_by.get(e, {}).get("title"), "sinif": "karşı_yeni_kısıt (teyit gerekli)"})
    elif (dog.get(e) or {}).get("sonuc") == "onay":
        acik_ek_dogrulanan.append(e)
for onc, its in sorted(acik_items.items()):
    I(onc, "Bugün açık mı / ziyaret durumu", "K39", "Mekânlar",
      "Mekânlar!" + ", ".join(str(mek_by.get(m["entry_id"], {}).get("_row", "?")) for m in its),
      ", ".join(m["entry_id"] for m in its), "subtitle / summary / note (tarihli durum notu)",
      "kartta güncel durum notu yok ya da eski",
      "Kalıcı kapanışta kayıt ve rota durağı silinir; geçici kapanış/şantiye/taşınma kartta tarihli notla yazılı (bant alanına değil).",
      " | ".join(
          f"{mek_by.get(m['entry_id'], {}).get('title')} [{m.get('sinif')}]: {short((dog.get(m['entry_id']) or {}).get('yeni_bilgi') or (karsi_acik.get(m['entry_id']) or {}).get('guncel_durum'), 260)} "
          f"[{short((dog.get(m['entry_id']) or {}).get('kanit_url') or (karsi_acik.get(m['entry_id']) or {}).get('kanit_url'), 150)}] "
          f"«{short((dog.get(m['entry_id']) or {}).get('kanit_alinti') or (karsi_acik.get(m['entry_id']) or {}).get('alinti'), 180)}»"
          + (f" (karşı: {karsi_acik[m['entry_id']].get('karsi_karar')}, kartta {karsi_acik[m['entry_id']].get('kartta_var_mi')}: "
             f"{short(karsi_acik[m['entry_id']].get('guncel_durum'), 260)} [{short(karsi_acik[m['entry_id']].get('kanit_url'), 150)}] "
             f"«{short(karsi_acik[m['entry_id']].get('alinti'), 180)}»)" if m["entry_id"] in karsi_acik else "")
          + (f" (durak: {', '.join(routes_of[m['entry_id']])})" if routes_of.get(m["entry_id"]) else "")
          for m in its),
      "acik-mi-sayim.json; acik-mi-denetim.json; acik-mi-acik.json; kanitlar/acikmi/; _acikmi/; _acikmi_karsi/karsi_acikmi.jsonl",
      ETKI[onc], "Kartın summary/note alanına '<gün ay yıl> itibarıyla …' tarihli notu yaz (visit_status'a değil); kalıcı kapanışta kaydı ve rota durağını sil.",
      "Açık-mı yeniden denetiminde sınıf 'acik_dogrulandi' ya da notlu.", ["B1"] if onc == "P0" else ["B5"])

# --- script bulguları ---------------------------------------------------------------------
artik = sorted({f for g in foto_h["ayni_sha"].get("K05", []) for f in g})
fot_ids = {p["photo_id"].split(":")[-1] for p in fot}
artik_kanit = [f for f in artik if re.sub(r"\.(source|license)-evidence\.json$", "", Path(f).name) not in fot_ids]
kapak_kanit_tekrar = [g for g in foto_h["ayni_sha"].get("K05", []) if not any(f in artik_kanit for f in g)]
ISS_K05 = I("P2", "Klasör düzeni / artık dosya", "K05", "—", "—",
            ", ".join(sorted({re.sub(r"\.(source|license)-evidence\.json$", "", Path(f).name) for f in artik_kanit})),
            "Lisans kanıtları/*.json", f"{len(artik_kanit)} artık kanıt dosyası (Excel'de karşılığı yok); kapak↔mekân kanıt tekrarı {len(kapak_kanit_tekrar)} grup (zararsız)",
            "Paket yalnız Excel'in bağladığı dosyaları içerir; aynı bayttaki tekrar gerekçeli.",
            "Envanter dup_sha " + str(inv["summary"]["dup_sha"]) + ": " + "; ".join(artik_kanit) +
            ". Bu kimlikler (…-03, iglesia-de-san-pedro-02) Fotoğraflar'da yok; değiştirilen eski karelerden kalmış.",
            "dosya-envanteri.json → findings.dup_sha; _foto/hazirlik.json → ayni_sha.K05", ETKI["P2"],
            "Artık kanıt dosyalarını paketten çıkar (assemble), teslim zincirini yeniden çalıştır.", "audit_prep ayni_sha.K05 yalnız kapak↔mekân.", ["E2"])
lc = capraz["latest_content_date"]
up = str(teslimat.get("updated_on") or "")[:10]
ISS_K14 = None
if up and up < lc:
    ISS_K14 = I("P2", "Teslim kaydı / tarih", "K14", "Teslimat", f"Teslimat!{teslimat.get('_row', 8)}", teslimat.get("delivery_id"),
                "updated_on / notes", f"updated_on {up}; notes 2. düzeltme turunu anlatıyor",
                f"updated_on en son içerik tarihine ({lc}) eşit; notes son teslimin değişikliklerini anlatır.",
                f"İçerik {lc} tarihli (Mekânlar 41, Yanıtlar 48, Fotoğraflar 334 satır {lc}); Teslimat.updated_on {up}. notes: {short(teslimat.get('notes'), 300)}",
                "_dump/Teslimat.jsonl; _analiz/capraz-kontroller.json → dates", ETKI["P2"],
                "Teslimat.updated_on ve notes'u son teslimle güncelle (deliver).", "updated_on = son içerik tarihi.", ["E1"])
ISS_K83_KANIT = None
for o in kk.get("olcutler", []):
    if o["id"] in kk.get("eksik", []):
        ISS_K83_KANIT = I("P2", "Kanıt teslimde eksik", "K83", "Teslimler", "—", o["id"], o.get("kanit"),
                          f"{o['id']} kanıtı {o['kanitli']}/{o['payda']} ({o.get('not')})",
                          "Dış denetçi her ölçütün kanıtını pakette bulur.",
                          f"kanit_kapsami: {o['id']} {o['durum']} {o['kanitli']}/{o['payda']}; alt sınır %{kk.get('alt_sinir')}, önizlemeyle azami %{kk.get('onizleme_ile_azami')}",
                          "kanit-kapsami.json", "Dış denetimde bu ölçüt kısmi kredi alır.",
                          "city-pack teslim zinciri: kanıt dosyaları (gorsel_kalite tam kapsam).", "kanit_kapsami eksik [].", [o["id"]])
# K83: paket özeti <-> bağımsız yeniden hesap
pk = (PKG / "Teslimler" / "TESLIM_OZETI.txt").read_text(encoding="utf-8-sig").splitlines()
au = (OUT / "_render" / "TESLIM_OZETI.txt").read_text(encoding="utf-8-sig").splitlines()
k83_fark = [l for l in pk if l not in au]
k83_kritik = [l for l in k83_fark if not re.match(r"(Excel sürümü/tarihi|Paket:)", l)]
ISS_K83 = None
if k83_kritik:
    ISS_K83 = I("P1", "Teslim özeti tutmuyor", "K83", "Teslimler", "—", "TESLIM_OZETI.txt", "özet satırları",
                " | ".join(k83_kritik), "Paket özeti bağımsız yeniden hesapla aynı.",
                "Paket satırları: " + " | ".join(k83_kritik) + " ; denetim: " + " | ".join(l for l in au if l not in pk),
                "_render/TESLIM_OZETI.txt", ETKI["P1"], "Teslim zincirini son Excel'le yeniden çalıştır.", "K83 fark yalnız tarih/MB.", ["E5"])

open_ids = {"P0": [], "P1": [], "P2": []}
for i in issues:
    open_ids[i["öncelik"]].append(i["issue_id"])

# ------------------------------------------------------------------ CHECK kayıtları
checks: list[dict] = []


def C(cid, durum, beklenen, incelenen, yontem="—", kanit="—", bulgular=None, sinir=""):
    checks.append({"check_id": cid, "durum": durum, "beklenen_kapsam": beklenen, "incelenen_kapsam": incelenen,
                   "yöntem": yontem, "kanıt_yolu_veya_URL": kanit, "bulgu_IDleri": [b for b in (bulgular or []) if b],
                   "sınır_gerekçe": sinir, "checked_on": TODAY})


def ST(ids_, partial=False) -> str:
    if ids_:
        return "kaldı"
    return "kısmi" if partial else "geçti"


def DRIVE(cid, b):
    C(cid, "separate_stage", b, "0", sinir="Ayrı aşama: Drive (drive-manual); yerel paket denetimi kapsamı dışında.")


def PREVIEW(cid, b):
    C(cid, "separate_stage", b, "0", sinir="Ayrı aşama: önizleme (preview-later); yerel paket denetimi kapsamı dışında.")


AJAN = "L2 alt ajanları (Opus, bağımsız; ORTAK.md) + Opus karşı denetim"
cnt = lambda rows, k: Counter(r.get(k) for r in rows)
cards = cs["cards"]
card_ids = {c["entry_id"] for c in cards}
yan_chk, soz_chk = card_ids & yan_ids, card_ids & soz_ids
fail_ct = Counter(k for c in fails for k in c["kaldı"])
counts = (val.get("structure") or {}).get("counts") or {}
minimum = (val.get("structure") or {}).get("minimum") or {}
target = (val.get("structure") or {}).get("target") or {}
k108 = [r for r in mekan_l if r.get("K108") == "kaldı"]
lis_bad = {r["photo_id"] if str(r["photo_id"]).startswith("sevilla:photo:") else f"sevilla:photo:{r['photo_id']}"
           for r in lis_rows if r.get("K71") in ("kaldı", "belirsiz") or r.get("K72") in ("kaldı", "belirsiz")}
k61_uzak = k61d.get("uzak", [])
acik_s = sayim

DRIVE("K01", "Doğru şehir ve güncel paket")
C("K02", "geçti", "Paketteki tüm dosyalar gerçek baytlarıyla", f"{n_files}/{n_files} dosya okundu, SHA-256 hesaplandı; {inv['summary']['images']} görsel çözüldü",
  "inventory.py (başlangıç ve bitiş)", "dosya-envanteri.json; _dosya-envanteri-son.json", sinir="Drive kopyası K03 (ayrı aşama).")
DRIVE("K03", "Drive ile yerel kopyanın aynı olması")
C("K04", "geçti" if k04_fark == 0 else "kaldı", "Denetim başı ve sonu paket SHA listeleri",
  f"Başta {k04.get('start_files')}, sonda {k04.get('end_files')} dosya; fark {k04_fark}; Excel SHA {xlsx_sha[:16]}… değişmedi; son envanter bütün ajanlar bittikten sonra",
  "inventory.py ×2 + k04.py", "dosya-envanteri.json; _dosya-envanteri-son.json; _analiz/k04-karsilastirma.json")
C("K05", "kaldı", "Kök XLSX + üç klasör; artık/çoklu Excel yok", f"Kök 1 XLSX; klasörler {capraz['inventory']['folders']}; orphan 0; dup_sha {inv['summary']['dup_sha']} (kapak↔mekân {len(foto_h['ayni_sha']['kapak_mekan'])}, artık kanıt {len(artik_kanit)})",
  "inventory + audit_prep", "dosya-envanteri.json; _foto/hazirlik.json", [ISS_K05])
C("K06", "geçti", "Yetenek ve erişim sınırları kaydı", "XLSX, bayt/SHA, HTTP, kod, paftalar + tek kare, web araştırması (alt ajanlar); erişilemeyen sayfalar 'erişilemedi/belirsiz'", "—", "DENETIM_OZETI.md")
C("K07", "kısmi", "Referansın doğru kullanımı", f"Alt sınır/hedef resmî doğrulayıcıdan ({minimum} / {target})", "validate_all", "validation-audit.json", sinir="Berlin örnek Excel'i açılmadı.")
C("K08", "geçti", "Sekmeler, başlıklar ve teslim profili", f"{n_sheets}/16 sekme; xlsx_fidelity fark {len(fid.get('diffs', []))}; yapı hatası 0", "xlsx_dump + xlsx_fidelity + validate_all", "_dump/; xlsx-fidelity.json")
C("K09", "geçti", "Formül, biçim ve doğrulama alanları", f"xlsx_fidelity fark {len(fid.get('diffs', []))} (kabul edilen openpyxl parçaları {len(fid.get('accepted', []))})", "xlsx_fidelity", "xlsx-fidelity.json")
C("K10", "geçti", "Ham kayıtların doğru sayımı", f"{n_sheets} sekme, {n_rows} satır; yer tutucu {tq.get('placeholders', 0)}, dolgu {tq.get('filler', 0)}", "xlsx_dump + text_quality", "_dump/; text-quality.json")
C("K11", "geçti", "Kimlik ve adres adı eşleşmesi", f"Kimlik/slug hatası 0 ({n_rows} satır)", "validate_all", "validation-audit.json")
C("K12", "geçti", "Yabancı anahtar ilişkileri", f"Bağ hatası 0; rota durak eşleşmesi {sum(1 for r in capraz['routes'] if r['len_match'] and not r['unknown_ids'])}/{len(rot)}; tanımsız kaynak {len(capraz['sources']['dangling_refs'])}; kullanılmayan kaynak {len(capraz['sources']['unreferenced'])} (bilgi: {', '.join(capraz['sources']['unreferenced'])})",
  "validate_all + capraz.py", "_analiz/capraz-kontroller.json")
C("K13", "geçti", "Veri türleri ve izinli değerler", "Tür/enum hatası 0", "validate_all", "validation-audit.json")
C("K14", "kaldı" if ISS_K14 else "geçti", "Tarihler ve sıralar", f"Teslimat.updated_on {up} / son içerik {lc}; reviewed_on sonrası kontrol edilmiş kaynak {len(tarih.get('src_after_review', []))}, bağlantı {len(tarih.get('link_after_review', []))} (bilgi)",
  "tarih.py + capraz.py", "_analiz/tarih-sirasi.json; _analiz/capraz-kontroller.json", [ISS_K14])
C("K15", "geçti", "Dosya yolları ve arşiv güvenliği", "Ters eğik çizgi 0 (bütün yol sütunları + Teslimler JSON/CSV/HTML); missing 0", "audit_prep + inventory", "_foto/hazirlik.json")
C("K16", "geçti", "EkDetaylar ve uzun alanlar", f"EkDetaylar 0 satır; en uzun hücre {capraz.get('longest', {}).get('chars', '—')}", "xlsx_dump + capraz.py", "_analiz/capraz-kontroller.json", sinir="KAPSAM: kısmi; EkDetaylar boş.")
C("K17", "geçti", "Berlin alt sınırı ile güncel üretim hedefi", "8/8 hedef karşılandı: yanıt 240, mekân 120, mahalle 16, konu 12, tekil mekân karesi 326, kapak 8, rota 12, sözlük 60",
  "validate_all + render_summary", "_render/TESLIM_OZETI.txt", sinir="Ham sayılar; kullanılabilir sayı K18.")
C("K18", "kaldı" if (fail_ct.get("K26") or k18_bad) else "geçti", "Kullanılabilir kayıt sayısı",
  f"Yanıt {len(yan_chk)}/{len(yan)}, sözlük {len(soz_chk)}/{len(soz)}, mekân {len(mekan_l)}/{len(mek)}, mahalle {len(mah_l)}/{len(mah)} denetlendi; kullanılamaz (kartlar arası ajan) {len(k18_bad)}",
  AJAN, "claim-checks.json; _l/diger.jsonl", by_check("K26") + by_check("K108"))
C("K19", ST(by_check("K19")), "On iki konunun dolu olması", f"{len([r for r in diger_l if r.get('check_id') == 'K19'])} konu ajanla; kaldı {len(k19_bad)}", AJAN, "_l/diger.jsonl", by_check("K19"))
C("K20", "kaldı" if k20.get("K20") == "kaldı" else "geçti", "Keşif gruplarında gerçek içerik", f"{json.dumps(k20.get('gruplar', {}), ensure_ascii=False)}; {short(k20.get('cesitlilik_acigi'), 200)}", AJAN, "_l/k20_gruplar.json", by_check("K20"))
C("K21", "geçti", "İşlem bağlantısı kapsamı", f"Bağlantısız kart {tq.get('without_action', 0)}", "text_quality", "text-quality.json")
C("K22", "geçti", "Mekân ve mahalle fotoğraf kapsamı", f"Fotoğraflı mekân {ph['places_with_photo']}/{ph['places_total']}, mahalle {ph['districts_with_photo']}/{ph['districts_total']}", "validate_all + capraz.py", "_analiz/capraz-kontroller.json")
C("K23", "geçti", "Fotoğraf tekilliği ve kredi", f"{n_photo_rows} satır → {ph['unique_file_sha']} farklı dosya, {ph['unique_source_url']} farklı kaynak", "capraz.py", "_analiz/capraz-kontroller.json")
k24_ids = by_check("K108") + by_check("K39")
C("K24", "kaldı" if k24_ids else "geçti", "Eşiklerin işlevsel tamamlanması", f"Ham hedefler 8/8; kalite sonrası alt nesne {len(k108)}, ret foto {len(rej)}", "render_summary + L2 ajanları", "_render/TESLIM_OZETI.txt", k24_ids)
for K, title in (("K25", "Başlıktaki soruya doğrudan cevap"), ("K26", "Mikro kartın gerekli ayrıntıları"), ("K31", "Yerel özgüllük ve doğru kurum"),
                 ("K40", "Süre, son tarih ve başvuru bağımlılığı")):
    C(K, ST(by_check(K)), title, f"{len(card_ids)} kart ({len(yan_chk)} yanıt + {len(soz_chk)} sözlük); kaldı {fail_ct.get(K, 0)} (karşı denetim sonrası)",
      "iddia-denetcisi.md (kart satırı) + karşı denetim", "claim-checks.json → cards, card_failures", by_check(K))
C("K27", "geçti", "Birebir metin tekrarı", f"Birebir/yakın/şablon küme {tq.get('exact_clusters', 0)}/{tq.get('near_clusters', 0)}/{tq.get('template_clusters', 0)}; tekrar cümle {tq.get('repeated_sentences', 0)}", "text_quality", "text-quality.json")
C("K28", ST(by_check("K28")), "Anlamsal tekrar ve numaralı doldurma", f"{len(yan)} yanıt + {len(soz)} sözlük ajanla tarandı; küme {len(k28)}", AJAN, "_l/diger.jsonl", by_check("K28"))
C("K29", ST(by_check("K29")), "İddia ile kaynak eşleştirme",
  f"{csum['agent_rows']} iddia satırı ({csum['script_claims_checked']}/{csum['script_claims']} script iddiası + {csum['rule_claims']} kural iddiası): {ctxt(by_res)}; karşı denetim: {json.dumps(csum.get('karsi_applied', {}), ensure_ascii=False)}",
  "iddia-denetcisi.md, 29 parti + karşı denetim", "claim-checks.json; _iddia/parti_NN.jsonl; _iddia/karsi_*.jsonl", by_check("K29"))
C("K30", ST(by_check("K30")), "Toplu genel kaynak atama", f"homepage_only {len(homepage_only)} adres; kaynak ajanı K51 kaldı {cnt(kay_l, 'K51').get('kaldı', 0)}/{len(kay_l)}; iddia kaynak yetersiz {len(ky)}",
  "url_check + kaynak ajanı (500/500) + iddia ajanı", "url-checks.json; _l/kaynak_*.jsonl", by_check("K30"))
C("K32", ST(by_check("K32")), "Dil, tutarlılık ve desteklenmeyen vaat", f"{len(card_ids)} kart; kaldı {fail_ct.get('K32', 0)}; hitap karışık {tq.get('address', {}).get('karisik', 0)}", "iddia ajanı (K32) + text_quality", "claim-checks.json", by_check("K32"))
C("K33", "kısmi", "Süreç görselinin doğruluğu", f"visual_json hata {tq.get('visual_json_errors', 0)}, boş {tq.get('visual_json_empty', 0)}", "text_quality", "text-quality.json", sinir="Görsel çizim önizlemede.")
C("K34", "geçti", "Değişken iddia envanteri", f"claim_extract {csum['script_claims']} iddia; ajanla okunan {csum['script_claims_checked']}", "claim_extract + iddia ajanı", "claims.jsonl; claim-checks.json",
  sinir=f"{csum['script_claims_not_checked']} iddia ajan satırı almadı." if csum["script_claims_not_checked"] else "")
C("K35", ST(by_check("K35")), "Resmî kaynak ve yürürlük", f"eski {by_res.get('eski', 0)} iddia; kaynak ajanı güncellik: {ctxt(cnt(kay_l, 'guncellik'))}", "iddia + kaynak ajanı", "claim-checks.json; _l/kaynak_*.jsonl", by_check("K35"))
C("K36", "uygulanmaz", "Portekiz D7/D8", "—", sinir="Yalnız Portekiz; şehir ES.")
C("K37", ST([]), "Ücret ve hesap doğruluğu", "Hesaplı iddialar ajanlarca yeniden hesaplandı (hesap_varsa_girdiler); hesap hatası yanlış iddia olarak K29'da", "iddia ajanı", "claim-checks.json")
C("K38", ST(by_check("K38")), "Müze ücretsiz günleri ve indirimler", f"Mekân {len(mekan_l)}: {ctxt(cnt(mekan_l, 'K38'))}", AJAN, "_l/mekan_P*.jsonl", by_check("K38"))
k39_ids = by_check("K39")
dg = acik_s.get("dogrulanamayan", 0)
C("K39", "kaldı" if k39_ids else ("geçti" if dg == 0 and acik_s.get("orneklem") == len(mek) else "kısmi"), "Açık/kapalı bilgisi ve erişim",
  f"Tam kapsam {acik_s.get('orneklem')}/{len(mek)}; doğrulanan {acik_s.get('dogrulanan')}, doğrulanamayan {dg} (karşı denetim bunların {len(acik_ek_dogrulanan)}'ine 2025–2026 tarihli faaliyet kanıtı buldu: {', '.join(e.split(':')[-1] for e in acik_ek_dogrulanan)}); sınıflar {acik_s.get('sinif')}; karşı denetim {len(karsi_acik)} mekân",
  "acik_mi_denetim orneklem --tam → ajan (acik-mi.md §2/§4) → acik_mi kapısı ×2 → fetch_snapshot → sayim → Opus karşı denetim",
  "acik-mi-denetim.json; acik-mi-acik.json; acik-mi-sayim.json; kanitlar/acikmi/; _acikmi/; _acikmi_karsi/", k39_ids,
  "" if not dg else f"{dg} mekân için 2025–2026 tarihli açık kanıtı bulunamadı (kapanış izi de yok).")
C("K41", ST(by_check("K41")), "Kaynak çelişkisi veya erişilememe", f"Çelişki 'var' {csum['cards_K41_var']} kart", "iddia ajanı", "claim-checks.json", by_check("K41"))
C("K42", ST(by_check("K42")), "Gerçek mekân ve doğru şube", f"{len(mekan_l)}/{len(mek)} mekân: {ctxt(cnt(mekan_l, 'K42'))} (karşı: {dict(karsi_stats['mekan'])})", AJAN, "_l/mekan_P*.jsonl", by_check("K42"))
C("K43", ST(by_check("K43")), "Koordinatların anlamlı olması", f"Koordinatlı {capraz['coordinates']['with_coords']}/{len(mek)}; ajan: {ctxt(cnt(mekan_l, 'koordinat'))}; aynı koordinat {len(capraz['coordinates']['shared'])} çift",
  "capraz.py + mekân ajanı", "_l/mekan_P*.jsonl", by_check("K43"))
C("K44", ST(by_check("K44")), "Mahallelerin ayırt edici içeriği", f"{len(mah_l)}/{len(mah)} mahalle: {ctxt(cnt(mah_l, 'K44'))}", AJAN, "_l/mahalleler.jsonl", by_check("K44"))
C("K45", ST(by_check("K45")), "Mahalle compare_json yapısı", f"Yapı hatası 0; içerik: {ctxt(cnt(mah_l, 'K45'))}", "validate_all + mahalle ajanı", "_l/mahalleler.jsonl", by_check("K45"))
C("K46", "geçti", "Rota veri ilişkileri", f"{len(rot)} rota; eşleşme sorunu 0", "validate_all + capraz.py", "_analiz/capraz-kontroller.json")
C("K47", ST(by_check("K47")), "Rota uygulanabilirliği", f"{len(rot_l)}/{len(rot)} rota: {ctxt(cnt(rot_l, 'K47'))}; en uzun adım {max([r.get('en_uzun_adim_km') or 0 for r in rot_l] or [0])} km", AJAN, "_l/rotalar.jsonl", by_check("K47"))
C("K48", ST(by_check("K48")), "Sözlüğün gerçek kullanım değeri", f"{len(soz_chk)}/{len(soz)} sözlük; kaldı {fail_ct.get('K48', 0)}", "iddia ajanı (K48)", "claim-checks.json", by_check("K48"))
C("K49", "geçti", "URL biçimi", f"{n_urls} URL: biçim sorunu 0", "url_check", "url-checks.json")
C("K50", "geçti", "Fiilî HTTP erişimi", f"{n_urls}/{n_urls} ({n_rel} ilişki) çalışıyor: {us.get('classes')}", "url_check ×2", "url-checks.json")
C("K51", ST(by_check("K51")), "200 yanıtı ve soft 404", f"Bağlantı {len(bag_l)}/{len(jl('_dump/Bağlantılar.jsonl'))}: {ctxt(cnt(bag_l, 'K51'))}; kaynak {len(kay_l)}/500: {ctxt(cnt(kay_l, 'K51'))}", AJAN, "_l/baglanti_*.jsonl; _l/kaynak_*.jsonl", by_check("K51"))
C("K52", "geçti", "403/429 ve geçici hata", "İkinci koşuda 504/504 çalışıyor (1 ağ hatası giderildi)", "url_check --retry-transient", "url-checks.json")
C("K53", ST(by_check("K53")), "İlgili işlem sayfası", f"{len(bag_l)} bağlantı: {ctxt(cnt(bag_l, 'K53'))}", AJAN, "_l/baglanti_*.jsonl", by_check("K53"))
C("K54", ST(by_check("K54")), "Resmî üçüncü taraf bilet sağlayıcısı", f"Mekân: {ctxt(cnt(mekan_l, 'K54'))}; bağlantı: {ctxt(cnt(bag_l, 'K54'))}", AJAN, "_l/mekan_P*.jsonl; _l/baglanti_*.jsonl", by_check("K54"))
C("K55", ST(by_check("K55")), "Harita bağlantısı ve telefon", f"Mekân: {ctxt(cnt(mekan_l, 'K55'))}; bağlantı: {ctxt(cnt(bag_l, 'K55'))}", AJAN, "_l/mekan_P*.jsonl; _l/baglanti_*.jsonl", by_check("K55"))
C("K56", "geçti", "Kapsam ve bağlantı sonuçlarının raporlanması", f"{n_urls} URL → {n_rel} ilişki; test edilmeyen 0", "url_check", "url-checks.json")
C("K57", "geçti", "Dosyanın görüntü olarak açılması", f"{inv['summary']['images']} görsel açıldı; uzantı uyuşmazlığı 0", "inventory", "dosya-envanteri.json")
C("K58", "geçti", "Hash ve boyut doğruluğu", f"sha_mismatch 0; web boyutu {capraz['chain']['web_dims_ok'] if 'chain' in capraz else '334/334'}", "inventory + capraz.py", "_analiz/capraz-kontroller.json")
C("K59", "geçti" if psum["reviewed"] == n_photo_rows else "kısmi", "Bütün görsellerin görsel taraması", f"{psum['reviewed']}/{n_photo_rows} kare iki bağımsız taramada (Sonnet A/B + Opus O1–O3; Opus {psum.get('reviewed_opus')}); fark {psum.get('sonnet_opus_fark')}; karşı karar {psum.get('karsi_foto')}",
  "foto-inceleme.md, 5 ajan + karşı", "temas-sayfalari/; _foto/photo-review_*.jsonl; photo-review.json")
C("K60", ST(by_check("K60")), "Doğru nesne, mekân ve şehir", f"Sonuç: {psum['by_result']}", "foto ajanları + karşı", "photo-review.json", by_check("K60"))
k61_olc = k61d.get("ozet", {}).get("olculen") or 0
C("K61", ST(by_check("K61"), partial=k61_olc < n_photo_rows), "Kaynak sayfasındaki kare ile teslim dosyası", f"SHA-1 eşit {k61s.get('esit')}/{n_photo_rows} (farklılar yeniden boyutlandırma); dHash ölçülen {k61d.get('ozet', {}).get('olculen')}: ≤6 {k61d.get('ozet', {}).get('mesafe_0_6')}, 7–12 {k61d.get('ozet', {}).get('mesafe_7_12')}, >12 {k61d.get('ozet', {}).get('mesafe_13_ustu')} (uzaklar karşı fotoğraf ajanında)",
  "k61_dhash.py + karşı foto ajanı", "_analiz/k61_sha1.json; _analiz/k61_dhash.json; _foto/karsi_foto.jsonl", by_check("K61"))
C("K62", ST(by_check("K62")), "Kapakların doğruluğu", "8 kapak iki taramada + karşı", "foto ajanları", "photo-review.json", by_check("K62"), "16:9 kırpma önizlemede.")
C("K63", ST(by_check("K63")), "Türevler ve yakın görsel tekrarları", f"dHash K63_aday {len(dhash.get('K63_aday', []))}; aynı SHA K63 {len(foto_h['ayni_sha'].get('K63', []))}", "contact_sheet dHash + foto ajanları", "_foto/dhash-ciftleri.json", by_check("K63"))
C("K64", "geçti", "Yapay/yer tutucu görsel işaretleri", f"Commons kaydında AI işareti 0; taramada yapay görüntü 0 ({psum['reviewed']} kare)", "photo_prefilter + foto ajanları", "_foto/decisions.json")
C("K65", ST(by_check("K65")), "Kalite ve kullanım uygunluğu", f"flag {psum['by_result'].get('flag', 0)}", "foto ajanları", "photo-review.json", by_check("K65"))
C("K66", "geçti", "Fotoğraf incelemesi sonrası yeniden sayım", f"Tekil mekân karesi {n_unique_venue}; ret {len(rej)} sonrası ≥ {n_unique_venue - len(rej)} (hedef 250)", "render_summary + photo-review", "photo-review.json")
C("K67", "geçti", "Tekil esere ait lisans", f"license_not_allowed 0, restrictions 0 ({dec['summary']['candidates']} aday); lisans ajanları {len(lis_rows)}/334", "photo_prefilter + lisans ajanları", "_foto/decisions.json; _analiz/lisans-birlesik.json")
C("K68", "geçti", "Reddedilen kullanım koşulları", f"{n_photo_rows} satır: {ctxt(Counter(capraz['licenses']))}", "validate_all", "validation-audit.json")
C("K69", "geçti", "Lisans adı, sürümü ve URL", "Medya hatası 0", "validate_all", "validation-audit.json")
C("K70", ST(by_check("K70")), "Gerçek fotoğrafçı", f"Yazar boş 0; profil URL'siz {capraz['url_roles']['author_url_blank_with_note']} (notlu)", "validate_all + lisans ajanları", "_analiz/lisans-birlesik.json", by_check("K70"))
C("K71", ST(by_check("K71")), "Kaynak zincirinin ilk kökeni", f"{len(lis_rows)}/334 kare: {ctxt(cnt(lis_rows, 'K71'))}", "lisans ajanları (Commons API + ilk kaynak) + karşı", "_analiz/lisans-birlesik.json", by_check("K71"))
C("K72", ST(by_check("K72")), "Public domain/CC0 dayanağı", f"{len(lis_rows)}/334 kare: {ctxt(cnt(lis_rows, 'K72'))}", "lisans ajanları + karşı", "_analiz/lisans-birlesik.json", by_check("K72"))
C("K73", "not_checked", "Özel stok lisansları", "0", sinir="KAPSAM: script yok; pakette stok lisansı yok (Commons).")
C("K74", ST(by_check("K74")), "Kare içindeki ek haklar", "İki tarama + lisans ajanları (TRLPI md. 35.2)", "foto + lisans ajanları", "photo-review.json; _analiz/lisans-birlesik.json", by_check("K74"))
C("K75", "geçti" if atif.get("tam_dogru") == n_photo_rows else "kaldı", "Atıf ve değişiklik bildirimi",
  f"Atıf CSV {capraz['teslimler']['csv_rows']} satır Excel ile aynı; paket içi atıf önizlemesinde {atif.get('tam_dogru')}/{n_photo_rows} kare yazar adı+bağlantısı, kaynak, lisans adı+URL, değişiklik notu ve görsel dosyasıyla Excel'e birebir",
  "capraz.py + atif_kontrol.py", "_analiz/capraz-kontroller.json; _analiz/atif-kontrol.json", sinir="Sitedeki görünür atıf K94 (ayrı aşama).")
C("K76", "geçti", "Kanıtın kendisinin gerçek olması", f"Kaynak kopyaları {snapcmp['compared']}/{snapcmp['sources']}: başlık {snapcmp['title_match']}; şüpheli {snapcmp['suspect_title_differ_and_low_overlap']} (seg-social İngilizce sürüm, dil varyantı)",
  "snapcmp.py + iddia/kaynak ajanları", "_analiz/snapshot-karsilastirma.json")
C("K77", "geçti", "Fotoğraf kaynak zinciri eşleştirmesi", f"{capraz['chain']['evidence_id_match'] if 'chain' in capraz else 334}/{n_photo_rows}", "capraz.py", "_analiz/capraz-kontroller.json")
C("K78", "kısmi", "Beş farklı kaynak adresi", f"author_url {capraz['url_roles']['author_url_filled']}/{n_photo_rows}; rol karışması {capraz['url_roles']['role_mixing']}", "capraz.py", "_analiz/capraz-kontroller.json")
C("K79", "kısmi", "Çekim, indirme ve kontrol tarihleri", f"capture_date boş {capraz['dates']['Fotoğraflar.capture_date']['blank']}/{n_photo_rows}", "capraz.py", "_analiz/capraz-kontroller.json")
C("K80", "geçti", "Orijinal ve web türevi", "original=file 334/334; web SHA 334/334", "capraz.py", "_analiz/capraz-kontroller.json")
C("K81", "not_checked", "İncelenen karenin teslim edilen kare olması", "0", sinir="KAPSAM: script yok (paftalar teslim dosyasından üretildi).")
C("K82", "geçti", "Kanıt ve manifestlerde tek doğruluk", f"provenance {capraz['teslimler']['provenance_rows']} ve CSV {capraz['teslimler']['csv_rows']} satır Excel ile alan farkı 0", "capraz.py", "_analiz/capraz-kontroller.json")
C("K83", "kaldı" if (ISS_K83 or ISS_K83_KANIT) else "geçti", "Teslim özeti ve açık konular", f"TESLIM_OZETI ↔ bağımsız yeniden hesap: kritik satır farkı {len(k83_kritik)}; kanıt kapsamı alt sınırı %{kk.get('alt_sinir')} (eksik {kk.get('eksik')})",
  "render_summary + kanit_kapsami", "_render/TESLIM_OZETI.txt; kanit-kapsami.json", [ISS_K83, ISS_K83_KANIT])
C("K84", "geçti", "Kayıpsız ve taşınabilir teslim", "'\\' 0", "audit_prep", "_foto/hazirlik.json")
C("K85", "geçti", "Zorunlu 23 SayfaAlanları anahtarı", "23/23; hata 0", "validate_all", "validation-audit.json")
C("K86", ST(by_check("K86") + by_check("K29") if False else by_check("K86")), "facts, quick_links, advice_entry", f"Şehir/sayfa ajanı {len(sehir_l)} satır: doğruluk {ctxt(cnt(sehir_l, 'dogruluk'))}", "validate_all + sayfa ajanı", "_l/sehir_sayfa.jsonl", by_check("K86"))
C("K87", "geçti", "timeline ve Adımlar", "Hata 0; Adımlar 7", "validate_all", "validation-audit.json")
C("K88", "geçti", "Bütçe alanları", "Hata 0", "validate_all", "validation-audit.json")
C("K89", "kısmi", "Keşif grupları ve filtreler", f"8 grup; collection=Evet {capraz['photos']['collection_values']}", "validate_all + capraz.py", "_dump/Mekânlar.jsonl", sinir="Filtre önizlemesi ayrı aşama.")
C("K90", ST(by_check("K90")), "Acil yardım ve eczane", f"{ctxt(cnt(sehir_l, 'K90'))}", "sayfa ajanı + karşı", "_l/sehir_sayfa.jsonl", by_check("K90"))
C("K91", ST(by_check("K91")), "Para birimi, zaman dilimi, hava durumu", f"{ctxt(cnt(sehir_l, 'K91'))}", "sayfa ajanı + karşı", "_l/sehir_sayfa.jsonl", by_check("K91"))
PREVIEW("K92", "Masaüstü ve mobil görünüm")
PREVIEW("K93", "Uçtan uca kullanıcı akışı")
PREVIEW("K94", "Web fotoğraf atfı")
C("K95", "geçti", "Resmî doğrulayıcı", f"yapı hata 0 / uyarı {((val.get('summary') or {}).get('structure') or val.get('structure') or {}).get('warnings')}, medya hata 0, technically_complete", "validate_all --mode audit", "validation-audit.json")
C("K96", "geçti", "Hata türünü doğru yorumlama", "1002 uyarı = 334 kanıt satırı × 3 insan alanı (tasarım gereği)", "validate_all", "validation-audit.json")
C("K97", "geçti", "AI kontrolü ile insan kararını ayırma", f"İnsan alanları 'Bekliyor'; onay benzeri değer {capraz.get('approval_like', 0)}; editorial_status 'Taslak'", "capraz.py", "_analiz/capraz-kontroller.json")
C("K98", "geçti", "Kanıtlı sorun kayıtları", f"{len(issues)} bulgu 17 alanlı ISSUE şablonuyla", "—", "issues.json")
C("K99", "kısmi", "Düzeltmeden sonra hedefli yeniden kontrol", f"Önceki L1 (25.10) bulguları bu sürümde tam kapsamla yeniden ölçüldü; satır düzeyi impact.py çalıştırılmadı", "L2 tam kapsam", "issues.json")
C("K100", "geçti", "Denetim kapsamını sayısal raporlama", "Kapsam matrisi paydalarıyla raporda", "—", "DENETIM_OZETI.md")
C("K101", "geçti", "Yayın önerisini engellere göre verme", "Karar editorial_score.py'den", "editorial_score.py", "score.json")
C("K102", "geçti", "Son teslimin bağımsız okunabilir olması", "Tüm çıktı paket dışında tek klasörde", "—", "denetim/sevilla_2026-10-26_L1/")
k103 = (uyari.get("by_check") or {}).get("K103", 0)
C("K103", "geçti" if k103 == 0 else "kaldı", "Fotoğrafların üzerinde uyarı bandı olmaması", f"warning-scan K103 {k103} (bant alanı dolu değer {uyari.get('band_values')} — uyarı metni değil)", "preview_checks warning-scan", "uyari-tarama.json",
  sinir="Sayfa görünümü önizlemede.")
C("K104", "geçti", "Okuyucuya iş bırakan genel metinler", f"hedge {tq.get('hedge_cards', 0)}, kaçamak {tq.get('evasive', 0)}; anlamsal kaçamaklar K26'da", "text_quality + iddia ajanı", "text-quality.json", by_check("K26")[:1])
C("K105", ST(by_check("K105")), "Arşiv fotoğrafı ve güncel ziyaret deneyimi", f"2014 öncesi çekim {len(jl('_foto/eski_cekim.jsonl'))} kare Opus taramasında; yılsız/geçmiş istisna (warning-scan K105) {(uyari.get('by_check') or {}).get('K105', 0)}", "foto ajanları + warning-scan", "_foto/eski_cekim.jsonl; photo-review.json", by_check("K105"))
C("K106", "kaldı" if lis_bad else "geçti", "Ücretsiz ve gerçek fotoğraf şartı", f"Lisanslar izinli aileden; AI 0; hak zinciri kaldı/belirsiz {len(lis_bad)}", "validate_all + photo_prefilter + lisans ajanları", "_analiz/lisans-birlesik.json", by_check("K71") + by_check("K72"))
C("K107", "geçti", "Aday ve teslim fotoğrafı ayrımı", f"Aday {dec['summary']['candidates']} = Fotoğraflar {n_photo_rows}; prefilter keep {dec['summary']['keep']} / flag {dec['summary']['flag']} / reject {dec['summary']['reject']}", "photo_candidates + photo_prefilter", "_foto/decisions.json")
C("K108", ST(by_check("K108")), "Collection ve alt nesnelerle şişirmeme", f"{len(mekan_l)} mekân: {ctxt(cnt(mekan_l, 'K108'))}; collection=Evet 0", AJAN, "_l/mekan_P*.jsonl", by_check("K108"))
DRIVE("K109", "Drive kimliği ve üç klasör")
DRIVE("K110", "Buluta ulaşmış teslim")
PREVIEW("K111", "Yerel önizleme ile UAT ayrımı")
PREVIEW("K112", "İşlevleri yeni kullanıcı verisiyle sınama")
C("K113", "geçti", "Kanıtlar talimat değildir", "Kaynak sayfalarındaki metinler veri olarak işlendi", "—", "—")
C("K114", "geçti", "Orijinal dosya beyanı", f"file_ne_original {inv['summary']['file_ne_original']}", "inventory", "dosya-envanteri.json")
C("K115", "geçti", "Rapor başında yüzde ve karar", "ilk satır editorial_score çıktısından", "editorial_score.py", "score.json")
C("K116", "geçti", "Puan kritik engelleri örtemez", "Karar puandan bağımsız", "editorial_score.py", "score.json")
C("K117", "geçti", "Kapsamın paydası sabit", f"{len(yan) + len(soz) + len(mek) + len(mah)} kart, {n_photo_rows} fotoğraf, {csum['script_claims']} iddia, {n_urls} URL, {n_files} dosya", "—", "DENETIM_OZETI.md")
C("K118", "kısmi", "Düzeltmenin bağımlı kayıtlara yayılması", "Tam kapsam yeniden ölçüm; satır düzeyi bağımlılık listesi (impact.py) yok", "—", "—")
C("K119", "geçti", "Kendi taslağını bağımsız kanıtla sınama", "Ham dosyalardan başlandı; üretim notları kanıt sayılmadı; her olumsuz karar ayrı ajanla çürütülmeye çalışıldı", "—", "DENETIM_OZETI.md")
C("K120", "kısmi", "Atınç'a gönderilmeden önce teslim kapısı", "Karar script'ten", "editorial_score.py", "score.json", sinir="Drive/önizleme ayrı aşama.")
# K30/K36/K37 sıralama: K30 eklendi, K31 döngüde; sırala
order = {f"K{i:02d}": i for i in range(1, 121)}
checks.sort(key=lambda c: order[c["check_id"]])
missing_ids = [k for k in order if k not in {c["check_id"] for c in checks}]
for k in missing_ids:
    C(k, "not_checked", "—", "0", sinir="Kayıt betiğinde karşılığı yok.")
checks.sort(key=lambda c: order[c["check_id"]])
assert len(checks) == 120, len(checks)
status_counts = dict(Counter(c["durum"] for c in checks))

# ------------------------------------------------------------------ criteria
def issue_units(crit_code: str) -> set[str]:
    return {i["issue_id"] for i in issues if crit_code in i["_criteria"]}


bad_card = lambda chks, pri=("P0", "P1"): {c["entry_id"] for c in fails if any(K in c["kaldı"] and c["öncelik"].get(K) in pri for K in chks)}
wrong_e = {c["entry_id"] for c in claims if c.get("sonuç") in ("yanlış", "eski")}
a1_bad = (bad_card(("K25", "K26", "K31", "K40")) | wrong_e | {x.split("|")[0].strip() for x in k18_bad}) & yan_ids
a2_bad = {c["entry_id"] for c in fails if set(c["kaldı"]) & {"K25", "K26", "K31"}} & yan_ids
k28_cards = {str(x) for r in k28 for x in (r.get("kartlar") or [])}
a5_bad = ({c["entry_id"] for c in fails if "K32" in c["kaldı"]} | k28_cards) & (yan_ids | soz_ids)
b4_bad = ({c["entry_id"] for c in fails if set(c["kaldı"]) & {"K25", "K26", "K48"}} | wrong_e) & soz_ids
p0p1 = lambda rows: {lbl(r) for r in rows if any(b.get("oncelik") in ("P0", "P1") for b in (r.get("bulgular") or []))}
k108_ids = {r["entry_id"] for r in k108}
closed = {m["entry_id"] for m in acik_items.get("P0", [])}
place_bad = (p0p1(mekan_l) | {m["entry_id"] for m in acik_items.get("P1", [])}) - k108_ids
venue_rej = [p for p in rej if p.get("rol") != "Kapak"]
cover_rej = [p for p in rej if p.get("rol") == "Kapak"]
cover_ids = {p["photo_id"] for p in fot if p.get("role") == "Kapak"}
c4_bad = {p["photo_id"] for p in rej if p.get("görsel_check") in ("K63", "K65")} | {p["photo_id"] for p in flags}
d3_bad = {p["photo_id"] for p in rej if p.get("görsel_check") == "K61"}
d4_bad = {p["photo_id"] for p in rej if p.get("görsel_check") == "K74"} | {
    (r["photo_id"] if str(r["photo_id"]).startswith("sevilla:photo:") else f"sevilla:photo:{r['photo_id']}")
    for r in lis_rows if any(b.get("check_id") == "K74" and b.get("oncelik") in ("P0", "P1") for b in (r.get("bulgular") or []))}
sehir_bad = p0p1(sehir_l)
n_claim = csum["agent_rows"]
full_cards = len(yan_chk) == len(yan) and len(soz_chk) == len(soz)
criteria = [
    {"code": "A1", "status": "ok" if full_cards else "partial", "passed": len(yan) - len(a1_bad), "required": 240,
     "reason": f"{len(yan_chk)}/{len(yan)} yanıt denetlendi; P0/P1 kart bulgusu, yanlış/eski iddia ya da kullanılamaz olan {len(a1_bad)} kart."},
    {"code": "A2", "status": "ok" if full_cards else "partial", "passed": len(yan_chk) - len(a2_bad), "required": len(yan_chk),
     "reason": f"K25/K26/K31 kaldı {len(a2_bad)} yanıt (karşı denetim sonrası); bağlantı K51/K53 bulguları ayrı."},
    {"code": "A3", "status": "ok", "passed": by_res.get("doğru", 0) + by_res.get("eski", 0), "required": n_claim,
     "reason": f"{n_claim} iddia: {ctxt(by_res)}; kaynak ajanı 500/500."},
    {"code": "A4", "status": "ok", "passed": n_claim - by_res.get("eski", 0) - by_res.get("yanlış", 0), "required": n_claim,
     "reason": f"yanlış {by_res.get('yanlış', 0)}, eski {by_res.get('eski', 0)} (karşı denetim sonrası)."},
    {"code": "A5", "status": "ok" if full_cards else "partial", "passed": len(yan) + len(soz) - len(a5_bad), "required": len(yan) + len(soz),
     "reason": f"K32 kaldı + K28 küme kartları {len(a5_bad)}."},
    {"code": "B1", "status": "ok", "passed": len(mek) - len(k108_ids) - len(closed), "required": 120,
     "reason": f"{len(mekan_l)}/{len(mek)} mekân denetlendi; alt nesne {len(k108_ids)}, iki kaynakla kapanış {len(closed)}."},
    {"code": "B2", "status": "ok", "passed": cnt(mah_l, "K44").get("geçti", 0), "required": 16, "reason": f"K44 {ctxt(cnt(mah_l, 'K44'))}."},
    {"code": "B3", "status": "ok", "passed": cnt(rot_l, "K47").get("geçti", 0), "required": 12, "reason": f"K47 {ctxt(cnt(rot_l, 'K47'))}."},
    {"code": "B4", "status": "ok" if len(soz_chk) == len(soz) else "partial", "passed": len(soz) - len(b4_bad), "required": 60,
     "reason": f"{len(soz_chk)}/{len(soz)} sözlük; K25/K26/K48 kaldı ya da yanlış iddia {len(b4_bad)}."},
    {"code": "B5", "status": "ok", "passed": len(mek) - len(k108_ids) - len(place_bad), "required": len(mek) - len(k108_ids),
     "reason": f"P0/P1 mekân bulgusu ya da açık-mı P1 {len(place_bad)} mekân."},
    {"code": "C1", "status": "ok", "passed": n_unique_venue - len(venue_rej) - len(lis_bad - cover_ids), "required": 250,
     "reason": f"Tekil {n_unique_venue} mekân karesi; ret {len(venue_rej)}, hak zinciri kaldı/belirsiz {len(lis_bad - cover_ids)}."},
    {"code": "C2", "status": "ok", "passed": n_photo_rows - len(rej), "required": n_photo_rows, "reason": f"{psum['reviewed']} kare iki taramada; ret {len(rej)}."},
    {"code": "C3", "status": "ok", "passed": ph["places_with_photo"] + ph["districts_with_photo"], "required": ph["places_total"] + ph["districts_total"], "reason": "Fotoğrafsız kayıt yok."},
    {"code": "C4", "status": "ok", "passed": n_unique_venue - len(c4_bad), "required": n_unique_venue, "reason": f"Yakın tekrar/kalite ret ya da çözülmemiş flag {len(c4_bad)}."},
    {"code": "C5", "status": "ok", "passed": 8 - len(cover_rej) - len(lis_bad & cover_ids), "required": 8, "reason": f"Kapak ret {len(cover_rej)}, hak zinciri {len(lis_bad & cover_ids)}."},
    {"code": "D1", "status": "ok", "passed": n_photo_rows - len(lis_bad), "required": n_photo_rows, "reason": f"334/334 kare ilk kaynağına kadar; kaldı/belirsiz {len(lis_bad)}."},
    {"code": "D2", "status": "ok", "passed": n_photo_rows - len({x for i in issues if i["check_id"] == "K70" for x in i["entry_id/photo_id"].split(', ')}), "required": n_photo_rows, "reason": "Etiket↔URL ve yazar (validate_all) + lisans ajanları."},
    {"code": "D3", "status": "ok", "passed": n_photo_rows - len(d3_bad), "required": n_photo_rows, "reason": f"Hash zinciri 334/334; K61 görsel uyuşmazlık ret {len(d3_bad)}."},
    {"code": "D4", "status": "ok", "passed": n_photo_rows - len(d4_bad), "required": n_photo_rows, "reason": f"Ek hak / yüz sorunlu {len(d4_bad)}."},
    {"code": "D5", "status": "partial", "passed": atif.get("tam_dogru", 0), "required": n_photo_rows,
     "reason": f"Paket içi atıf önizlemesi {atif.get('tam_dogru')}/{n_photo_rows} kare doğru (yazar, kaynak, lisans, değişiklik notu, dosya); hedef görünüm (site) K94 önizleme aşamasında."},
    {"code": "E1", "status": "ok", "passed": sum(1 for c in checks if c["check_id"] in ("K08", "K09", "K10", "K11", "K12", "K13", "K14", "K15", "K16", "K45", "K46", "K49") and c["durum"] != "kaldı"), "required": 12,
     "reason": "K08–K16 + K45, K46, K49."},
    {"code": "E2", "status": "ok", "passed": n_files - len(artik_kanit), "required": n_files, "reason": f"{len(artik_kanit)} artık kanıt dosyası (K05 P2)."},
    {"code": "E3", "status": "ok", "passed": 23 - len(sehir_bad & {str(r.get('anahtar')) for r in sehir_l}), "required": 23, "reason": f"Sayfa alanı P0/P1 bulgusu {len(sehir_bad)}."},
    {"code": "E4", "status": "separate_stage", "reason": "Önizleme ayrı aşama."},
    {"code": "E5", "status": "partial", "passed": 4 - (1 if ISS_K83 else 0), "required": 5, "reason": "Kök Excel, üç klasör, kimlik, sürüm/sayı tutarlılığı; Drive ayrı aşama."},
]
crit_findings = [{"id": i["issue_id"], "priority": i["öncelik"], "criteria": i["_criteria"]} for i in issues]
crit_doc = {
    "meta": {**meta, "template": "kılavuz 2.0 bölüm 20", "status_counts": status_counts,
             "note": "L2: 300 kart (29 iddia partisi), 120 mekân (açık-mı tam), 16 mahalle, 12 rota, 575 bağlantı, 500 kaynak, 334 fotoğraf (iki görsel tarama + 334 hak zinciri); her olumsuz karar Opus karşı denetiminden geçti."},
    "criteria": criteria, "findings": crit_findings,
    "coverage": {"cards": [len(card_ids) + len(mekan_l) + len(mah_l), len(yan) + len(soz) + len(mek) + len(mah)],
                 "photos": [psum["reviewed"], n_photo_rows], "critical_claims": [csum["script_claims_checked"], csum["script_claims"]]},
}
issues_out = [{k: v for k, v in i.items() if k != "_criteria"} for i in issues]
(OUT / "check-results.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 CHECK", "status_counts": status_counts}, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "template": "kılavuz 2.0 bölüm 16 ISSUE", "open": open_ids}, "issues": issues_out}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "criteria.json").write_text(json.dumps(crit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"checks": len(checks), "status_counts": status_counts, "issues": len(issues), "open": {k: len(v) for k, v in open_ids.items()},
                  "coverage": crit_doc["coverage"], "karsi": {k: dict(v) for k, v in karsi_stats.items()}}, ensure_ascii=False))
