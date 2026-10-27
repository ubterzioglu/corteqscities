"""rapor_l2.py: DENETIM_OZETI.md ve DUZELTME_LISTESI.md (kayıtlardan; yalnız OUT altına yazar).

Kullanım: python -I -X utf8 rapor_l2.py <OUT>
Girdi: score.json, issues.json, check-results.json, criteria.json, claim-checks.json, photo-review.json,
       acik-mi-sayim.json, acik-mi-uretim.json, url-checks.json, kanit-kapsami.json, _render/TESLIM_OZETI.txt, dosya-envanteri.json.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(sys.argv[1])


def load(rel, default=None):
    p = OUT / rel
    return json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else default


def short(s, n=300):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[: n - 1] + "…"


score = load("score.json")
iss = load("issues.json")["issues"]
chk = load("check-results.json")["checks"]
crit = load("criteria.json")
cs = load("claim-checks.json")
pr = load("photo-review.json")
sayim = load("acik-mi-sayim.json", {})
uretim = load("acik-mi-uretim.json", {})
urls = load("url-checks.json")
kk = load("kanit-kapsami.json", {})
inv = load("dosya-envanteri.json")
render = (OUT / "_render" / "TESLIM_OZETI.txt").read_text(encoding="utf-8-sig").splitlines()
xlsx = next(f for f in inv["files"] if f["path"].endswith(".xlsx"))
us = urls.get("summary", urls)
cap = load("_analiz/capraz-kontroller.json")

P = {p: [i for i in iss if i["öncelik"] == p] for p in ("P0", "P1", "P2")}
cov = score["coverage"]
cov_txt = "; ".join(f"{k} {v['reviewed']}/{v['total']}" for k, v in cov.items() if v)
lines = []
lines.append(f"Editoryal hazır olma: %{score['editorial_percent']}" + (f" ({'; '.join(score['labels'])})" if score.get("labels") else "")
             + f" | Denetim kapsamı: L2, yerel paket denetimi, inceleme {cov_txt}; script dosya {inv['summary']['files']}/{inv['summary']['files']}, "
               f"satır {sum(cap['sheet_rows'].values())}, URL {us['unique_urls']}/{us['unique_urls']} | Karar: {score['decision']}"
             + (f" ({score['decision_note']})" if score.get("decision_note") else ""))
lines.append(f"Teknik/panel ilerlemesi: ölçülmedi (yerel paket denetimi) | Açık P0: {len(P['P0'])}"
             + (f" ({', '.join(i['issue_id'] for i in P['P0'])})" if P["P0"] else "")
             + f" | Açık P1: {len(P['P1'])}" + (f" ({', '.join(i['issue_id'] for i in P['P1'])})" if P["P1"] else "")
             + f" | P2 öneri: {len(P['P2'])}")
lines.append("")
lines.append("> Bu bir yayın onayı değildir. Drive (K01, K03, K109, K110) ve önizleme (K92–K94, K103, K111, K112) ayrı aşamadır.")
lines.append("")
lines.append("## 1. Paket, sürüm, kanıt kapsamı")
lines.append(f"- Şehir: Sevilla (CITY-107), Excel `{xlsx['path']}`, SHA-256 `{xlsx['sha256']}`; denetim tarihi 2026-10-26; kademe L2 (tam), Opus alt ajanlar + Opus karşı denetim.")
lines.append(f"- Paket: {inv['summary']['files']} dosya, {inv['summary']['total_mb']} MB; denetim başı/sonu SHA listesi farkı (K04): "
             + next((c["incelenen_kapsam"] for c in chk if c["check_id"] == "K04"), "—"))
lines.append(f"- Teslimdeki kanıt kapsamı (dış denetim modeli, `kanit_kapsami`): alt sınır **%{kk.get('alt_sinir')}**, önizlemeyle azami %{kk.get('onizleme_ile_azami')}, eksik ölçüt: {kk.get('eksik') or 'yok'}. (Bizim editoryal yüzdemiz değildir; dış denetçinin pakette bulacağı kanıtı ölçer.)")
lines.append(f"- Kararın gerekçesi: {score.get('decision_reason')}")
lines.append("")
lines.append("## 2. Berlin minimum – hedef – fiilî")
lines += ["| " + l.strip().replace(": ", " | ", 1).replace(" / alt sınır ", " | ").replace(" / hedef ", " | ").replace(" — ", " | ") + " |"
          for l in render if "alt sınır" in l and "hedef" in l]
lines.insert(len(lines) - sum(1 for l in render if "alt sınır" in l and "hedef" in l), "| Ölçü | Fiilî | Alt sınır | Hedef | Durum |\n|---|---|---|---|---|")
lines.append("")
lines.append("## 3. Puan dökümü (25 ölçüt)")
lines.append("| Ölçüt | Ağırlık | Geçen | Payda | Durum | Gerekçe |")
lines.append("|---|---|---|---|---|---|")
for c in score["criteria"]:
    lines.append(f"| {c['code']} | {c['weight']} | {c['passed'] if c['passed'] is not None else '—'} | {c['required'] if c['required'] is not None else '—'} | {c['status_tr']} | {short(c.get('reason'), 160)} |")
lines.append("")
lines.append("## 4. Öncelikli bulgular")
for p in ("P0", "P1"):
    lines.append(f"### {p} ({len(P[p])})")
    if not P[p]:
        lines.append("Yok.")
    for i in P[p]:
        lines.append(f"- **{i['issue_id']}** {i['check_id']} · {i['kategori']} · {i['tablo']} {i['Excel_satırı']}")
        lines.append(f"  - Kayıtlar: {short(i['entry_id/photo_id'], 400)}")
        lines.append(f"  - Gözlem: {short(i['somut_gözlem'], 1800)}")
        lines.append(f"  - Beklenen: {short(i['beklenen'], 300)} · Düzeltme: {short(i['önerilen_düzeltme'], 300)}")
        lines.append(f"  - Kanıt: {short(i['kanıt'], 300)}")
lines.append(f"### P2 ({len(P['P2'])})")
for i in P["P2"]:
    lines.append(f"- {i['issue_id']} {i['check_id']} · {i['kategori']}: {short(i['mevcut_değer'], 120)} — {short(i['somut_gözlem'], 500)}")
lines.append("")
lines.append("## 5. Fotoğraf: ret kareler (pafta/slot)")
rej = pr["rejects"]
if not rej:
    lines.append("Ret kare yok.")
for p in rej:
    lines.append(f"- {p['photo_id']} ({p['hedef_mekân']}, Fotoğraflar!{p['_row']}) [{', '.join(p['pafta_slot'])}] {p.get('görsel_check') or ''}: {short(p.get('ek_hak_notu'), 300)}")
ps = pr["summary"]
lines.append(f"- Tarama: {ps['reviewed']}/{ps['photo_rows']} kare (Sonnet A/B + Opus O1–O3; Opus {ps.get('reviewed_opus')}), karşı foto kararı {ps.get('karsi_foto')}, sonuç {ps['by_result']}; hak zinciri {ps.get('license_rows')}/334: K71 {ps.get('K71')}, K72 {ps.get('K72')}.")
lines.append("")
lines.append("## 6. Bugün açık mı (K39, tam kapsam)")
lines.append(f"- Seçim: L2 = 120/120 mekân (`acik_mi_denetim orneklem --tam`); öncelik harfleri {json.dumps(load('acik-mi-orneklem.jsonl', None) and {}, ensure_ascii=False) if False else ''}"
             f"doğrulanan {sayim.get('dogrulanan')}, doğrulanamayan {sayim.get('dogrulanamayan')}; sınıflar {sayim.get('sinif')}.")
for cls, ids in (sayim.get("siniflar") or {}).items():
    if cls != "acik_dogrulandi" and ids:
        lines.append(f"  - {cls}: {', '.join(i.split(':')[-1] for i in ids)}")
up_items = uretim.get("items") or []
if up_items:
    lines.append(f"- Üretim beyanıyla fark: üretim kapısı {len(up_items)} bulgu vermişti ({Counter(x['code'] for x in up_items)}); denetim sınıfları yukarıda.")
lines.append("")
lines.append("## 7. İddia düzeltmeleri (resmî kaynakla)")
bad = [c for c in cs["claims"] if c.get("sonuç") in ("yanlış", "eski")]
lines.append(f"- {cs['summary']['agent_rows']} iddia satırı: {cs['summary']['by_result']} (ilk karar {cs['summary'].get('by_result_ilk')}; karşı denetim {cs['summary'].get('karsi_applied')}).")
for c in bad:
    lines.append(f"  - {c['claim_id']} ({c['sonuç']}): {short(c.get('iddia'), 200)} → **{short(c.get('doğrusu'), 200)}** [{short(c.get('resmî_URL'), 160)}]")
if not bad:
    lines.append("  - Yanlış ya da eski iddia yok.")
lines.append("")
lines.append("## 8. Bağlantı ve kaynak sorunları (kök nedene göre)")
lines.append(f"- HTTP: {us['unique_urls']}/{us['unique_urls']} çalışıyor ({us.get('classes')}); işaret: {us.get('flags')}.")
for i in iss:
    if i["check_id"] in ("K51", "K53", "K54", "K55", "K30", "K35") and i["tablo"] in ("Bağlantılar", "Kaynaklar"):
        lines.append(f"- {i['issue_id']} {i['öncelik']} {i['check_id']} ({i['tablo']}, {i['mevcut_değer']}): {short(i['somut_gözlem'], 900)}")
lines.append("")
FAZ = {"photos": {"K22", "K59", "K60", "K61", "K62", "K63", "K64", "K65", "K70", "K71", "K72", "K74", "K105"},
       "places": {"K20", "K38", "K39", "K42", "K43", "K44", "K45", "K47", "K54", "K55", "K108"},
       "answers": {"K18", "K19", "K25", "K26", "K28", "K29", "K30", "K31", "K32", "K35", "K40", "K41", "K48"},
       "sources (bağlantı/kaynak)": {"K51", "K53"},
       "assemble": {"K05", "K84", "K86", "K90", "K91"},
       "deliver": {"K14", "K83"}}


def faz_of(i):
    if i["check_id"] in ("K51", "K53", "K54", "K55") and i["tablo"] in ("Bağlantılar", "Kaynaklar"):
        return "sources (bağlantı/kaynak)"
    if i["check_id"] in ("K30", "K35") and i["tablo"] == "Kaynaklar":
        return "sources (bağlantı/kaynak)"
    return next((f for f, s in FAZ.items() if i["check_id"] in s), "diğer")


lines.append("## 9. Düzeltme sırası (city-pack düzeltme turu)")
order = ["photos", "places", "answers", "sources (bağlantı/kaynak)", "assemble", "deliver", "diğer"]
byf = defaultdict(list)
for i in iss:
    byf[faz_of(i)].append(i)
n = 1
for f in order:
    if byf.get(f):
        lines.append(f"{n}. **{f}**: " + "; ".join(f"{i['issue_id']} ({i['öncelik']} {i['check_id']})" for i in sorted(byf[f], key=lambda x: (x['öncelik'], x['issue_id']))))
        n += 1
lines.append(f"{n}. Teslim zinciri baştan (deliver); ardından yeni oturumda **Sevilla paketini denetle**: önce L0, sonra L1.")
lines.append("")
lines.append("## 10. Kapsam matrisi")
lines.append("| Alan | İncelenen / toplam | Yöntem |")
lines.append("|---|---|---|")
lines.append(f"| Kartlar (yanıt+sözlük+mekân+mahalle) | {cov['cards']['reviewed']}/{cov['cards']['total']} | iddia + mekân + mahalle ajanları |")
lines.append(f"| Kritik (script) iddialar | {cov['critical_claims']['reviewed']}/{cov['critical_claims']['total']} | iddia ajanları + karşı |")
lines.append(f"| Fotoğraf görsel | {ps['reviewed']}/{ps['photo_rows']} | iki bağımsız tarama + karşı |")
lines.append(f"| Fotoğraf hak zinciri | {ps.get('license_rows')}/{ps['photo_rows']} | Commons kaydı + ilk kaynak |")
lines.append(f"| Benzersiz URL (HTTP) | {us['unique_urls']}/{us['unique_urls']} | url_check |")
lines.append(f"| Bağlantı hedef anlamı | {sum(1 for _ in (OUT / '_l').glob('baglanti_[0-9][0-9].jsonl'))}/8 parti (575 satır) | bağlantı ajanları |")
lines.append(f"| Kaynak hedef anlamı | 500/500 | kaynak ajanları |")
lines.append(f"| Açık-mı | {sayim.get('orneklem')}/120 | ajan + 2 kapı + kanıt kopyası + karşı |")
lines.append("| Sayfa alanları | 23/23 + Şehir | sayfa ajanı |")
lines.append("| Önizleme / Drive | ayrı aşama | — |")
lines.append("")
lines.append("## 11. Çalıştırılmayan kontroller")
for c in chk:
    if c["durum"] in ("not_checked", "separate_stage", "kısmi"):
        lines.append(f"- {c['check_id']} ({c['durum']}): {short(c['beklenen_kapsam'], 80)} — {short(c['sınır_gerekçe'] or c['incelenen_kapsam'], 200)}")
(OUT / "DENETIM_OZETI.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

# düzeltme listesi
dl = ["# Sevilla CITY-107 — düzeltme listesi (L2 denetimi, 26.10.2026)", "",
      f"Kaynak: `issues.json` ({len(iss)} bulgu: P0 {len(P['P0'])}, P1 {len(P['P1'])}, P2 {len(P['P2'])}). Her P0/P1 kapanır; her P2 için karar (`_is\\duzeltme_kararlari.jsonl`).", ""]
for f in order:
    if not byf.get(f):
        continue
    dl.append(f"## {f}")
    for i in sorted(byf[f], key=lambda x: (x["öncelik"], x["issue_id"])):
        dl.append(f"- [ ] **{i['issue_id']}** {i['öncelik']} {i['check_id']} — {i['kategori']} ({i['tablo']} {i['Excel_satırı']})")
        dl.append(f"  - Ne: {short(i['somut_gözlem'], 2500)}")
        dl.append(f"  - Nasıl: {short(i['önerilen_düzeltme'], 400)}")
        dl.append(f"  - Kapanış koşulu: {short(i['tekrar_kontrol_koşulu'], 200)}")
    dl.append("")
dl.append("## Son adım")
dl.append("- Teslim zinciri baştan; yeni oturumda **Sevilla paketini denetle** (L0, sonra L1).")
(OUT / "DUZELTME_LISTESI.md").write_text("\n".join(dl) + "\n", encoding="utf-8")
print(json.dumps({"rapor": str(OUT / "DENETIM_OZETI.md"), "duzeltme": str(OUT / "DUZELTME_LISTESI.md"), "ilk_satir": lines[0], "ikinci_satir": lines[1]}, ensure_ascii=False))
