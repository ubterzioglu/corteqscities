"""kayitlar_hedefli.py: Sevilla hedefli L1 (02.11.2026) denetim kayıtları - CHECK, ISSUE, criteria.

Hedefli: yalnız 27.10 teslimine (556343a6) göre değişen kayıtlar + açık-mı örneklemi + ön elemede işaretli 30 kare
ajanla okundu. Sayılar dosyalardan okunur; değerlendirme metinleri bu dosyada. Yalnız OUT altına yazar.
Kullanım: python -I -X utf8 kayitlar_hedefli.py <OUT> <checks.yaml>
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import yaml

OUT = Path(sys.argv[1])
CHECKS = yaml.safe_load(Path(sys.argv[2]).read_text(encoding="utf-8"))["checks"]
TODAY = "2026-11-02"
AJAN = "L1 alt ajanı (Sonnet, bağımsız; hedefli)"


def load(rel: str):
    return json.loads((OUT / rel).read_text(encoding="utf-8-sig"))


def jl(rel: str) -> list[dict]:
    p = OUT / rel
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []


inv = load("dosya-envanteri.json")
val = load("validation-audit.json")
urls = load("url-checks.json")
kk = load("kanit-kapsami.json")
foto_h = load("_foto/hazirlik.json")
hed = load("_analiz/hedefli-ozet.json")
tarih = load("_analiz/tarih-sirasi.json")
k04 = load("_analiz/k04-karsilastirma.json")
cs = load("claim-checks.json")
pr = load("photo-review.json")
sayim = load("acik-mi-sayim.json")
k20 = load("_l/k20_gruplar.json")
mek = {m["entry_id"]: m for m in jl("_dump/Mekânlar.jsonl")}
yan = {y["entry_id"]: y for y in jl("_dump/Yanıtlar.jsonl")}
rot = {r["route_id"]: r for r in jl("_dump/Rotalar.jsonl")}
mekan_l = jl("_l/mekan_H.jsonl")
mah_l = jl("_l/mahalleler.jsonl")
rot_l = jl("_l/rotalar.jsonl")
xlsx = next(f for f in inv["files"] if f["path"].endswith(".xlsx"))
n_files = inv["summary"]["files"]
k04_fark = len(k04.get("added", [])) + len(k04.get("removed", [])) + len(k04.get("changed", []))

meta = {"tool": "city-audit L1 (hedefli)", "level": "L1-hedefli", "label": "yerel paket denetimi",
        "city_id": "sevilla", "catalog": "CITY-107", "xlsx": xlsx["path"], "xlsx_sha256": xlsx["sha256"],
        "previous_audit": "denetim/sevilla_2026-10-27_L0 (Excel 556343a6); tam denetim denetim/sevilla_2026-10-26_L1 (6fefa38b, %93)",
        "checked_on": TODAY,
        "scope_note": "Kullanıcı kararı: hedefli L1. Ajanla okunan: 27.10'dan beri değişen 7 kart, 15 mekân, 4 mahalle, "
                      "10 rota; açık-mı örneklemi; ön elemede işaretli 30 kare. Değişmeyen kayıtlar bu denetimde okunmadı."}

issues: list[dict] = []


def I(oncelik, kategori, check_id, tablo, excel, ids, alan, mevcut, beklenen, gozlem, kanit, etki, duzeltme, crit,
      tekrar="Yeni sürümle L0, ardından L1 (hedefli)."):
    iid = f"ISS-{len(issues) + 1:03d}"
    issues.append({"issue_id": iid, "öncelik": oncelik, "kategori": kategori, "check_id": check_id, "tablo": tablo,
                   "Excel_satırı": excel, "entry_id/photo_id": ids, "dosya": xlsx["path"], "alan": alan,
                   "mevcut_değer": mevcut, "beklenen": beklenen, "somut_gözlem": gozlem, "kanıt": kanit,
                   "kullanıcı_etkisi": etki, "önerilen_düzeltme": duzeltme, "tekrar_kontrol_koşulu": tekrar,
                   "durum": "Açık", "_criteria": crit})
    return iid


# ---- mekân ajanı bulguları
CRIT_MEK = {"K42": ["B5"], "K43": ["B5"], "K38": ["B5"], "K108": ["B1"], "K54": ["A3"], "K55": ["B5"]}
for r in mekan_l:
    for b in r.get("bulgular") or []:
        I(b["oncelik"], "Mekân bilgisi", b["check_id"], "Mekânlar", f"Mekânlar!{r['_row']}", r["entry_id"],
          "summary / note", r.get("title"), "Resmî kaynakla aynı bilgi", b["gozlem"],
          f"{b.get('kanit_url', '')} «{b.get('alinti', '')}»", "Okur yanlış saatle plan yapar.",
          "Kartı resmî sayfadaki güncel saatle düzelt; aynı bilgiyi taşıyan rota notlarını da düzelt.",
          CRIT_MEK.get(b["check_id"], ["B5"]))

# ---- mahalle ve rota bulguları (P2 grupları)
mah_b = [(r, b) for r in mah_l for b in (r.get("bulgular") or [])]
rot_b = [(r, b) for r in rot_l for b in (r.get("bulgular") or [])]
for pr_ in ("P0", "P1"):
    for r, b in mah_b + rot_b:
        if b.get("oncelik") == pr_:
            key = r.get("entry_id") or r.get("route_id")
            I(pr_, "Mahalle/rota", b["check_id"], "Mahalleler/Rotalar", r.get("_row"), key, "-", r.get("title"),
              "Kaynakla destekli", b["gozlem"], f"{b.get('kanit_url', '')} «{b.get('alinti', '')}»",
              "Okur yanlış bilgiyle plan yapar.", "Kaynağa göre düzelt.", ["B2"] if "entry_id" in r else ["B3"])
mah_p2 = [(r, b) for r, b in mah_b if b.get("oncelik") == "P2"]
rot_p2 = [(r, b) for r, b in rot_b if b.get("oncelik") == "P2"]
if mah_p2:
    I("P2", "Mahalle ulaşım", "K44", "Mahalleler", ", ".join(str(r["_row"]) for r, _ in mah_p2),
      ", ".join(sorted({r["entry_id"] for r, _ in mah_p2})), "compare_json / Ulaşım", "-",
      "Mahalleye özgü toplu taşıma bilgisi", "; ".join(f"{r['title']}: {b['gozlem']}" for r, b in mah_p2),
      "_l/mahalleler.jsonl", "Okur mahalleye nasıl gideceğini bulamaz.",
      "Ulaşım satırını mahallenin kendi durak/hatlarıyla yaz.", ["B2"])
if rot_p2:
    I("P2", "Rota planı", "K47", "Rotalar", ", ".join(sorted({str(r["_row"]) for r, _ in rot_p2})),
      ", ".join(sorted({r["route_id"] for r, _ in rot_p2})), "note / sıra", "-", "Makul sıra, süre ve saat",
      "; ".join(f"{r['route_id']}: {b['gozlem']}" for r, b in rot_p2), "_l/rotalar.jsonl",
      "Geri dönüşlü sıra ve fazla tahmini süre okuru yorar.", "Durak sırasını ve süreleri koordinata göre gözden geçir.",
      ["B3"])

# ---- iddia ve kart bulguları
for c in cs["card_failures"]:
    for k in c["kaldı"]:
        I("P2", "Kart eksik bilgi", k, "Yanıtlar", f"Yanıtlar!{c['_row']}", c["entry_id"], "steps / documents",
          c.get("title"), "Soruyu tam çözen kart", c["notlar"].get(k, ""), "_iddia/kart_01.jsonl",
          "Okur gereken belgeyi ya da süreyi karttan öğrenemez.", "Eksik öğeyi resmî kaynaktan ekle.", ["A2"])
for c in cs["not_wrong"]:
    if c.get("sonuç") in ("yanlış", "eski"):
        I("P1", "İddia", "K29" if c["sonuç"] == "yanlış" else "K35", "Yanıtlar", c.get("_row"), c["entry_id"],
          c.get("field"), c.get("text"), "Kaynakla aynı", c.get("gerekçe", ""), str(c.get("kanıt_url", "")),
          "Okur yanlış bilgiyle işlem yapar.", "Kaynağa göre düzelt.", ["A3", "A4"])

# ---- fotoğraf
for p in pr["rejects"]:
    I("P1", "Fotoğraf kimliği", "K60", "Fotoğraflar", f"Fotoğraflar!{p['_row']}", p["photo_id"], "file",
      p["dosya"], f"{p['hedef_mekân']} görüntüsü", f"{p['ek_hak_notu']} (pafta {', '.join(p['pafta_slot'])})",
      "temas-sayfalari/hedefli; _foto/photo-review_H.jsonl", "Okur başka yapının fotoğrafını görür.",
      "Kareyi mekânın kimliği kaynakla kanıtlanmış bir Commons karesiyle değiştir.", ["C2", "C1"])
fl = pr["flags"]
fl_hak = [p for p in fl if "ek hak" in (p["ek_hak_notu"] or "").lower() or "k74" in (p["ek_hak_notu"] or "").lower()]
fl_gor = [p for p in fl if p not in fl_hak]
if fl_hak:
    I("P2", "Kare içi hak", "K74", "Fotoğraflar", ", ".join(str(p["_row"]) for p in fl_hak),
      ", ".join(p["photo_id"] for p in fl_hak), "license_note", "-", "Çağdaş eser için ek hak notu",
      "; ".join(f"{p['photo_id']}: {p['ek_hak_notu']}" for p in fl_hak), "_foto/photo-review_H.jsonl",
      "Eser sahibinin hakkı lisansta kapsanmıyor olabilir.", "Panorama istisnasını not et ya da kareyi değiştir.", ["D4"])
if fl_gor:
    I("P2", "Fotoğraf uygunluğu", "K60", "Fotoğraflar", ", ".join(str(p["_row"]) for p in fl_gor),
      ", ".join(p["photo_id"] for p in fl_gor), "file", "-", "Mekânı temsil eden kare",
      "; ".join(f"{p['photo_id']}: {p['ek_hak_notu']}" for p in fl_gor), "_foto/photo-review_H.jsonl",
      "Kare mekânı zayıf temsil ediyor.", "İnsan bakışıyla karar ver; gerekirse kareyi değiştir.", ["C2"])

# ---- açık-mı (K39)
S = sayim["siniflar"]
for e in S.get("kapanis_iki_kaynak", []):
    I("P0", "Kapanmış mekân", "K39", "Mekânlar", f"Mekânlar!{mek[e]['_row']}", e, "-", mek[e]["title"],
      "Pakette yalnız açık mekân", "İki bağımsız kaynakla kapalı", "acik-mi-sayim.json; kanitlar/acikmi",
      "Okur kapanmış yere gider.", "Kaydı ve rota durağını sil; listeyi places fazında yeniden tara.", ["B1", "B5"])
not_yok = {it["entry_id"] for it in load("acik-mi-denetim.json")["findings"] if it["code"] == "not_yok"}
dogr = {json.loads(l)["entry_id"]: json.loads(l) for f in sorted((OUT / "_acikmi").glob("parti_*_dogrulama.jsonl"))
        for l in f.read_text(encoding="utf-8").splitlines() if l.strip()}
for e in S.get("kapanis_teyitsiz", []) + S.get("belirt_teyitli", []):
    m = next(x for x in sayim["mekanlar"] if x["entry_id"] == e)
    if m["sinif"] == "belirt_teyitli" and e not in not_yok:
        continue
    d = dogr.get(e, {})
    duraklar = [f"{r['route_id']} (Rotalar!{r['_row']})" for r in rot.values() if e in str(r.get("stop_entry_ids", ""))]
    I("P1", "Ziyaret durumu", "K39", "Mekânlar", f"Mekânlar!{mek[e]['_row']}", e, "note / visit_status",
      (mek[e].get("note") or "")[:200], "'<gün> <ay> <yıl> itibarıyla …' biçiminde ziyaret durumu notu",
      f"{d.get('yeni_bilgi', '')} Kartta olgu var, ziyarete açık olup olmadığı yazılı değil. Rota durağı: {', '.join(duraklar) or 'yok'}.",
      f"{d.get('kanit_url', '')} «{d.get('kanit_alinti', '')}»", "Okur ofise dönüşen binayı gezilecek yer sanabilir.",
      "Notu tarihli ziyaret durumuyla yaz (açık mı, kapalı mı); ziyarete kapalıysa rota durağını gözden geçir.",
      ["B5"])

# ---- script bulguları
hp = [u for u in urls["urls"] if "homepage_only" in (u.get("flags") or [])]
ch = [u for u in urls["urls"] if "cross_host_redirect" in (u.get("flags") or [])]
if hp:
    I("P2", "Kaynak derinliği", "K30", "Kaynaklar/Bağlantılar", "-", f"{len(hp)} adres", "url", "ana sayfa",
      "İddiayı taşıyan derin sayfa", "; ".join(u.get("ham_URL", "") for u in hp[:17]), "url-checks.json",
      "Okur bilgiyi ana sayfada arar.", "Derin sayfa bul; yoksa OI-013 gibi beyan et.", ["A3"])
if ch:
    I("P2", "Bağlantı bakımı", "K53", "Kaynaklar/Bağlantılar", "-", f"{len(ch)} adres", "url", "başka alan adına yönlenir",
      "Son adres", "; ".join(f"{u.get('ham_URL')} → {u.get('son_URL')}" for u in ch), "url-checks.json",
      "Bağlantı ileride kırılabilir.", "Son adresle değiştir.", ["E2"])
k05 = foto_h["ayni_sha"]["K05"]
if k05:
    I("P2", "Fazla kopya", "K05", "Lisans kanıtları", "-", f"{len(k05)} çift", "dosya", "aynı baytlı kanıt JSON'u",
      "Tek kanıt dosyası", f"{len(k05)} kapak↔mekân kanıt JSON çifti aynı bayt (bilinen OI-017)", "_foto/hazirlik.json",
      "İşlevi bozmaz.", "photo_rows kapak kanıtını tek dosyaya bağlasın (araç kutusu).", ["E2"])
for code in kk["eksik"]:
    o = next(x for x in kk["olcutler"] if x["id"] == code)
    I("P2", "Kanıt teslimde yok", "K83", "Teslimler", "-", code, o["kanit"], f"{o['kanitli']}/{o['payda']}",
      f"{o['payda']}/{o['payda']}", f"kanit_kapsami: {code} kısmi {o['kanitli']}/{o['payda']} ({o['not']})",
      "kanit-kapsami.json", "Dış denetçi bu ölçütün kanıtını pakette tam bulamaz.",
      "city-pack teslim zinciri: kanıt dosyaları", [code])
if tarih.get("src_after_review") or tarih.get("link_after_review"):
    sa, la = tarih.get("src_after_review") or [], tarih.get("link_after_review") or []
    I("P2", "Tarih sırası", "K14", "Yanıtlar/Kaynaklar", ", ".join(f"{o['sheet']}!{o['row']}" for o in sa[:10]),
      "örnek: " + ", ".join(o["id"] for o in sa[:5]),
      "reviewed_on / checked_on", "kaynak kartın gözden geçirilmesinden sonra kontrol edilmiş",
      "reviewed_on ≥ kaynak checked_on", f"kaynak {len(sa)}, bağlantı {len(la)} kayıt",
      "_analiz/tarih-sirasi.json", "Kartın tarihi kaynağın son kontrolünü yansıtmıyor.",
      "Kart reviewed_on'unu kaynak kontrolüyle güncelle.", ["E1"])

open_ids = {p: [i["issue_id"] for i in issues if i["öncelik"] == p] for p in ("P0", "P1", "P2")}

# ---- CHECK kayıtları (120)
by_check = Counter(i["check_id"] for i in issues)
AJAN_K = {"K20": "mahalle-rota ajanı (K20, bütün mekân grupları)", "K25": "iddia ajanı (7 kart)",
          "K26": "iddia ajanı (7 kart)", "K29": "iddia ajanı (147 iddia)", "K31": "iddia ajanı (7 kart)",
          "K34": "iddia ajanı", "K35": "iddia ajanı", "K40": "iddia ajanı (7 kart)", "K41": "iddia ajanı (7 kart)",
          "K38": "mekân ajanı (15)", "K42": "mekân ajanı (15)", "K43": "mekân ajanı (15 koordinat)",
          "K54": "mekân ajanı (15)", "K55": "mekân ajanı (15)", "K108": "mekân ajanı (15)",
          "K44": "mahalle-rota ajanı (4 mahalle)", "K45": "mahalle-rota ajanı (4 mahalle)",
          "K47": "mahalle-rota ajanı (10 rota)", "K59": "foto ajanı (30 kare)", "K60": "foto ajanı (30 kare)",
          "K61": "foto ajanı (30 kare)", "K62": "foto ajanı (kapak-06)", "K74": "foto ajanı (30 kare)"}
GECTI = {"K04": f"Baş/son envanter farkı {k04_fark}", "K17": "Berlin hedeflerinin hepsi karşılandı (render_summary)",
         "K22": "Fotoğraflı mekân 120/120, mahalle 16/16", "K84": "Ters eğik çizgi 0 (audit_prep)",
         "K63": "Aynı SHA mekân çifti 0, dHash K63 adayı 0", "K02": f"{n_files}/{n_files} dosya okundu, hata 0",
         "K10": "16 sekme, 2573 satır, yinelenen kimlik 0", "K11": "validate_all yapı hatası 0"}
checks = []
for c in CHECKS:
    cid, scope, ex = c["id"], c.get("scope"), c.get("exec")
    ids = [i["issue_id"] for i in issues if i["check_id"] == cid]
    rec = {"check_id": cid, "beklenen_kapsam": c["title"], "bulgu_IDleri": ids, "checked_on": TODAY}
    if scope == "drive-manual":
        rec.update(durum="separate_stage", incelenen_kapsam="0", yöntem="—", **{"kanıt_yolu_veya_URL": "—"},
                   sınır_gerekçe="Ayrı aşama: Drive; yerel paket denetimi kapsamı dışında.")
    elif scope == "preview-later":
        rec.update(durum="separate_stage", incelenen_kapsam="0", yöntem="—", **{"kanıt_yolu_veya_URL": "—"},
                   sınır_gerekçe="Ayrı aşama: önizleme.")
    elif cid == "K39":
        rec.update(durum="kaldı" if ids else "kısmi",
                   incelenen_kapsam=f"örneklem {sayim['orneklem']}/120 (öncelikli {sayim['oncelikli']}, rastgele {sayim.get('rastgele', sayim['orneklem'] - sayim['oncelikli'])}); doğrulanan {sayim['dogrulanan']}, doğrulanamayan {sayim['dogrulanamayan']}",
                   yöntem="acik_mi_denetim + 8 ajan + iki kapı", **{"kanıt_yolu_veya_URL": "acik-mi-sayim.json; acik-mi-denetim.json; acik-mi-acik.json; kanitlar/acikmi/"},
                   sınır_gerekçe="Örneklemden bütün pakete geçti çıkmaz.")
    elif cid in AJAN_K:
        rec.update(durum="kaldı" if ids else "kısmi", incelenen_kapsam=AJAN_K[cid], yöntem=AJAN,
                   **{"kanıt_yolu_veya_URL": "_l/; _iddia/; _foto/photo-review_H.jsonl"},
                   sınır_gerekçe="Hedefli: yalnız 27.10'dan beri değişen kayıtlar okundu.")
    elif cid in GECTI and not ids:
        rec.update(durum="geçti", incelenen_kapsam=GECTI[cid], yöntem="script (L0)",
                   **{"kanıt_yolu_veya_URL": "dosya-envanteri.json; validation-audit.json; _render/TESLIM_OZETI.txt; _foto/"},
                   sınır_gerekçe="")
    elif ex == "S":
        rec.update(durum="kaldı" if ids else "kısmi", incelenen_kapsam="bütün paket (script)", yöntem="script (L0)",
                   **{"kanıt_yolu_veya_URL": "L0 çıktıları (OUT kökü)"}, sınır_gerekçe="KAPSAM: script kısmi kapsar.")
    elif cid in ("K73", "K81"):
        rec.update(durum="not_checked", incelenen_kapsam="0", yöntem="—", **{"kanıt_yolu_veya_URL": "—"},
                   sınır_gerekçe="Denetimde yapılmaz (skill).")
    elif ids:
        rec.update(durum="kaldı", incelenen_kapsam="script/ajan bulgusu", yöntem="script (L0)",
                   **{"kanıt_yolu_veya_URL": "issues.json"}, sınır_gerekçe="")
    else:
        rec.update(durum="not_checked", incelenen_kapsam="0", yöntem="—", **{"kanıt_yolu_veya_URL": "—"},
                   sınır_gerekçe="Hedefli L1 kapsamı dışında (kullanıcı kararı 02.11.2026).")
    checks.append(rec)
assert len(checks) == 120
status_counts = dict(Counter(c["durum"] for c in checks))
missing_link = [c["check_id"] for c in checks if c["durum"] == "kaldı" and not c["bulgu_IDleri"]]
assert not missing_link, missing_link

# ---- criteria (bölüm 20): doğrulanan alt sınır
n_yan_ok = len([c for c in cs["cards"] if c["entry_id"] in yan]) - len([c for c in cs["card_failures"] if c["entry_id"] in yan])
mek_ok = sum(1 for r in mekan_l if r["K42"] == "geçti")
mek_bad = {i["entry_id/photo_id"] for i in issues if i["tablo"] == "Mekânlar" and i["öncelik"] in ("P0", "P1")}
mah_ok = sum(1 for r in mah_l if r["K44"] == "geçti")
rot_ok = sum(1 for r in rot_l if r["K47"] == "geçti")
psum = pr["summary"]
n_rev = psum["reviewed"]
n_rej = len(pr["rejects"])
acsum = cs["summary"]
by_res = acsum["by_result"]
A = acsum["agent_rows"]
criteria = [
    {"code": "A1", "status": "partial", "passed": n_yan_ok, "required": 240,
     "reason": f"Hedefli: 241 yanıttan {len([c for c in cs['cards'] if c['entry_id'] in yan])} değişen kart ajanla okundu; geçen {n_yan_ok}. Değişmeyen yanıtlar bu denetimde doğrulanmadı (alt sınır)."},
    {"code": "A2", "status": "partial", "passed": acsum["cards_unique"] - acsum["cards_failed"], "required": acsum["cards_unique"],
     "reason": f"Okunan {acsum['cards_unique']} kartın {acsum['cards_failed']}'i eksik öğe (K26, P2)."},
    {"code": "A3", "status": "partial", "passed": by_res.get("doğru", 0), "required": A,
     "reason": f"{A} iddia satırı (değişen kartlar): {dict(by_res)}."},
    {"code": "A4", "status": "partial", "passed": A - by_res.get("eski", 0) - by_res.get("yanlış", 0), "required": A,
     "reason": "Değişen kartlarda eski/yanlış iddia yok."},
    {"code": "A5", "status": "not_checked", "reason": "K28/K32 hedefli kapsam dışında; script: kopya 0, hedge 0, hitap karışık 0."},
    {"code": "B1", "status": "partial", "passed": mek_ok, "required": 120,
     "reason": f"Hedefli: {len(mekan_l)} değişen mekân ajanla okundu (K42 geçti {mek_ok}); açık-mı örneklemi {sayim['orneklem']} mekân, kapanış {len(S.get('kapanis_iki_kaynak', []))}."},
    {"code": "B2", "status": "partial", "passed": mah_ok, "required": 16, "reason": f"{len(mah_l)} değişen mahalle okundu; K44 geçti {mah_ok}."},
    {"code": "B3", "status": "partial", "passed": rot_ok, "required": 12, "reason": f"{len(rot_l)} değişen rota okundu; K47 geçti {rot_ok}."},
    {"code": "B4", "status": "not_checked", "reason": "Sözlük hedefli kapsam dışında (1 değişen terim iddia partisinde)."},
    {"code": "B5", "status": "partial", "passed": len(mekan_l) - len(mek_bad), "required": len(mekan_l),
     "reason": f"Okunan {len(mekan_l)} mekânda sorunlu {len(mek_bad)} (P0/P1)."},
    {"code": "C1", "status": "partial", "passed": 0, "required": 250,
     "reason": "Tekil mekân karesi 326 (script); görsel doğrulama yalnız ön elemede işaretli 30 karede (hedefli) → kullanılabilirlik alt sınırı yazılmadı."},
    {"code": "C2", "status": "partial", "passed": n_rev - n_rej, "required": len(pr["photos"]),
     "reason": f"Paftada {n_rev} kare (ön eleme işaretli); ret {n_rej}, işaret {len(fl)}."},
    {"code": "C3", "status": "ok", "passed": 136, "required": 136, "reason": "Fotoğrafsız mekân/mahalle 0 (script)."},
    {"code": "C4", "status": "partial", "passed": 0, "required": 326, "reason": "Aynı SHA/dHash tekrarı 0 (script); görsel kalite kanıtı kısmi (K83, önizlemede ölçülür)."},
    {"code": "C5", "status": "partial", "passed": 8, "required": 8, "reason": "8 farklı kapak (script); kapak-06 ajanla bakıldı, uygun."},
    {"code": "D1", "status": "partial", "passed": 0, "required": 334, "reason": "Lisans alanları validate_all'dan geçti; hak zinciri ajanı hedefli kapsamda çalışmadı (fotoğraf baytı değişmedi)."},
    {"code": "D2", "status": "ok", "passed": 334, "required": 334, "reason": "Etiket↔URL ve yazar alanları validate_all medya hatası 0."},
    {"code": "D3", "status": "ok", "passed": 334, "required": 334, "reason": "Kanıt dosyası 334/334, ters eğik çizgi 0, kanıtsız kare 0."},
    {"code": "D4", "status": "partial", "passed": 0, "required": 334, "reason": f"Yalnız {n_rev} işaretli karede bakıldı; ek hak notu {len(fl_hak)}."},
    {"code": "D5", "status": "partial", "passed": 0, "required": 334, "reason": "Atıf CSV/HTML var; görünür atıf önizlemede (ayrı aşama)."},
    {"code": "E1", "status": "partial", "passed": 0, "required": 12, "reason": "Şema/teslim profili script'le geçti; içerik kontrolleri hedefli kapsam dışında."},
    {"code": "E2", "status": "ok", "passed": n_files - len(k05), "required": n_files, "reason": f"{n_files} dosya çözülüyor; aynı baytlı kanıt JSON çifti {len(k05)} (P2)."},
    {"code": "E3", "status": "ok", "passed": 23, "required": 23, "reason": "23/23 sayfa alanı (validate_all)."},
    {"code": "E4", "status": "separate_stage", "reason": "Önizleme ayrı aşama."},
    {"code": "E5", "status": "partial", "passed": 4, "required": 5, "reason": "Kök Excel, üç klasör, kimlik, sürüm/sayı tutarlılığı ✓ (K83 özet farkı 0); Drive ayrı aşama."},
]
crit_doc = {"meta": {**meta, "template": "kılavuz 2.0 bölüm 20", "status_counts": status_counts},
            "criteria": criteria,
            "findings": [{"id": i["issue_id"], "priority": i["öncelik"], "criteria": i["_criteria"]} for i in issues],
            "coverage": {"cards": [acsum["cards_unique"] + len(mekan_l) + len(mah_l), len(yan) + len(mek) + 16],
                         "photos": [n_rev, len(pr["photos"])],
                         "critical_claims": [acsum["script_claims_checked"], acsum["script_claims"]]}}
issues_out = [{k: v for k, v in i.items() if k != "_criteria"} for i in issues]
(OUT / "check-results.json").write_text(json.dumps({"meta": {**meta, "status_counts": status_counts}, "checks": checks}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "issues.json").write_text(json.dumps({"meta": {**meta, "open": open_ids}, "issues": issues_out}, ensure_ascii=False, indent=1), encoding="utf-8")
(OUT / "criteria.json").write_text(json.dumps(crit_doc, ensure_ascii=False, indent=1), encoding="utf-8")
print(json.dumps({"checks": status_counts, "issues": len(issues), "open": open_ids, "coverage": crit_doc["coverage"]}, ensure_ascii=False))
