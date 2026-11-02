"""Ana dongu: Playa del Chanquete paftasi kararlari -> selected_chanquete_1.jsonl (+ review)."""
import json
import pathlib

W = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\malaga\_is")
sheet = json.loads((W / "foto_ch" / "tur" / "pafta" / "sheets.json").read_text(encoding="utf-8"))[0]
slot = {i["slot"]: i["key"] for i in sheet["items"]}
keep = {
    1: "Geniş, düzenli tırmıklanmış kumsal ve açık mavi deniz; uzakta sahil boyunca sıralanan beyaz binalar görünüyor.",
    4: "Kumsal ile yürüyüş yolu arasındaki palmiyeli yeşil şerit; arkada sahil boyunca uzanan mahalle ve deniz.",
    5: "Kumsala yaslanmış ahşap çardaklı bir plaj barı; çatıda 'El Pescador' yazısı, arkada deniz ve kıyı şeridi görünüyor.",
}
review, selected = [], []
for s, key in sorted(slot.items()):
    sonuc = "keep" if s in keep else "reject" if s in (8, 9, 10, 11, 12) else "flag"
    review.append({"key": key, "sheet": "ch_sheet_01", "slot": s, "entry_id": key.split("|")[0], "result": sonuc, "seen": "",
                   "reason": "ana döngü" + (": mural/levha/sokak, plaj değil" if sonuc == "reject" else ""), "ek_hak": "var" if s == 12 else "yok"})
    if s in keep:
        selected.append({"key": key, "entry_id": key.split("|")[0], "role": "Mekân", "caption": keep[s], "seen": keep[s]})
inc = W / "foto" / "inceleme"
(inc / "review_chanquete_1.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in review), encoding="utf-8")
(inc / "selected_chanquete_1.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected), encoding="utf-8")
print(json.dumps({"keep": [slot[s].split("|")[1] for s in keep]}, ensure_ascii=False))
