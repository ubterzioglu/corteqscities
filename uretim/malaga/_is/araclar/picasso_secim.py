"""Ana dongu Picasso paftasi kararlarini inceleme dosyalarina yazar (skill: tek pafta ana dongude incelenir)."""
import json
import pathlib

W = pathlib.Path(r"C:\temp_private\corteqs\0000_newera\uretim\malaga\_is")
sheet = json.loads((W / "foto_picasso" / "tur" / "pafta" / "sheets.json").read_text(encoding="utf-8"))[0]
slot = {i["slot"]: i["key"] for i in sheet["items"]}
keep = {
    8: "Museo Picasso Málaga'nın bulunduğu Palacio de Buenavista'nın iç avlusu: iki katlı kemerli revaklar, beyaz korkuluklu üst galeri ve ortada budanmış yeşil çalılar.",
    21: "Palacio de Buenavista'nın taş kulesi: üst katta kemerli açıklıklar, altta ahşap kepenkli pencereler; kule bulutlu gökyüzüne karşı yükseliyor.",
}
red = {1: "kalabalık, yüzler seçilebilir", 2: "kalabalık ön planda", 3: "kalabalık ön planda", 4: "kalabalık, dikey", 5: "kalabalık",
       6: "iç mekân arkeolojik kalıntı, bina değil", 7: "siyah-beyaz", 10: "arkeolojik kalıntı", 11: "arkeolojik kalıntı",
       12: "8 ile aynı avlu (yakın kopya)", 13: "bina seçilmiyor", 16: "ön planda kişiler", 24: "detay süsleme",
       28: "logo/tabela ağırlıklı", 29: "başka bina", 30: "mural/ek hak"}
review, selected = [], []
for s, key in sorted(slot.items()):
    sonuc = "keep" if s in keep else "reject" if s in red else "flag"
    neden = "ana döngü: avlu/kule, eser ve yüz yok" if s in keep else red.get(s, "uygun ama 3 sınırı / zayıf detay; seçilmedi")
    review.append({"key": key, "sheet": "picasso_sheet_01", "slot": s, "entry_id": key.split("|")[0], "result": sonuc,
                   "seen": "", "reason": neden, "ek_hak": "var" if s == 30 else "yok"})
    if s in keep:
        selected.append({"key": key, "entry_id": key.split("|")[0], "role": "Mekân", "caption": keep[s], "seen": keep[s]})
inc = W / "foto" / "inceleme"
(inc / "review_picasso_1.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in review), encoding="utf-8")
(inc / "selected_picasso_1.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in selected), encoding="utf-8")
print(json.dumps({"review": len(review), "keep": [slot[s].split("|")[1] for s in keep]}, ensure_ascii=False))
