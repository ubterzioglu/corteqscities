import sys, yaml
sys.stdout.reconfigure(encoding="utf-8")
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))["checks"]
S = {c["id"]: c for c in d if c["exec"] == "S"}
k = lambda *n: {f"K{i:02d}" for i in n}
DONE = k(2,8,9,10,11,12,13,14,15,17,21,22,23,27,45,46,49,50,52,56,57,58,63,68,69,70,77,80,83,84,85,86,87,88,95,97,99,100,104,114,115,118)
PARTIAL = k(4,5,16,24,30,33,43,64,66,67,75,76,78,79,82,89,106,107)
IMPL = {"K02":"inventory","K04":"inventory (SHA'lar; onceki/sonraki karsilastirma elle)","K05":"inventory (artik/orphan; coklu Excel yok)",
 "K08":"build_xlsx fidelity + validate_all","K09":"xlsx_fidelity + xlsx_dump","K10":"xlsx_dump","K11":"validate_all (resmi)","K12":"validate_all (resmi)",
 "K13":"validate_all + build_xlsx DV","K14":"validate_all (resmi)","K15":"inventory + validate_all","K16":"validate_all (uzun deger geri yukleme sayisi)",
 "K17":"render_summary (resmi sayim)","K22":"render_summary (varlik; dogruluk degil)","K23":"common.group_unique_photos","K24":"render_summary",
 "K30":"extra_checks.homepage_only_sources","K33":"-","K43":"validate_all (aralik) + extra_checks.shared_coordinates","K45":"validate_all","K46":"validate_all",
 "K49":"validate_all (URL bicimi)","K57":"inventory + validate_all","K58":"inventory","K66":"render_summary","K68":"validate_all","K69":"validate_all",
 "K70":"validate_all --new-content","K75":"validate_all --mode emit (atif CSV/HTML)","K77":"validate_all","K78":"validate_all","K79":"validate_all (kismi)",
 "K80":"inventory + validate_all","K82":"validate_all (kismi)","K83":"render_summary","K84":"inventory","K85":"validate_all","K86":"validate_all","K87":"validate_all",
 "K88":"validate_all","K89":"validate_all (kismi)","K95":"validate_all","K97":"build_xlsx + render_summary","K100":"render_summary (x/y yok: URL/iddia olculmedi)",
 "K106":"validate_all (lisans) + photo_rules (AI etiketi)","K114":"inventory + validate_all",
 "K21":"text_quality","K27":"text_quality","K104":"text_quality","K50":"url_check + web_fetch","K52":"url_check + web_fetch","K56":"url_check",
 "K63":"image_hash + contact_sheet (dHash)","K64":"photo_rules (AI etiketi; piksel analizi yok)","K67":"photo_candidates + photo_rules (Commons lisans alani)",
 "K76":"fetch_snapshot (snapshot hash)","K99":"impact","K118":"impact","K115":"editorial_score","K107":"photo_prefilter (aday/kisa liste)"}
IMPL["K33"] = "text_quality (visual_json)"
IMPL["K100"] = "editorial_score + render_summary"
TODO = set(S) - DONE - PARTIAL
extra = (DONE | PARTIAL) - set(S)
print("S kontrol sayisi:", len(S), "| tam:", len(DONE & set(S)), "| kismi:", len(PARTIAL & set(S)), "| yapilmadi:", len(TODO))
print("S disi ama listede:", sorted(extra))
print("TODO:", ", ".join(f"{i}({S[i]['title'][:34]})" for i in sorted(TODO)))
with open(sys.argv[2], "w", encoding="utf-8") as f:
    f.write("# Script kapsami (checks.yaml 'S' kontrolleri)\n\nUretim: coverage_map.py; atamalar yazarin yorumudur.\n\n")
    f.write(f"- Toplam script kontrolu: {len(S)} | tam: {len(DONE & set(S))} | kismi: {len(PARTIAL & set(S))} | henuz yok: {len(TODO)}\n\n")
    for title, ids in (("Tam kapsanan", DONE & set(S)), ("Kismi", PARTIAL & set(S)), ("Henuz script yok", TODO)):
        f.write(f"## {title} ({len(ids)})\n\n| Kontrol | Baslik | Oncelik | Script |\n|---|---|---|---|\n")
        for i in sorted(ids):
            f.write(f"| {i} | {S[i]['title']} | {S[i]['sev']} | {IMPL.get(i, '-')} |\n")
        f.write("\n")
