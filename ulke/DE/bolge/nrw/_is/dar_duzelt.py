"""Dar denetim (dar_denetim.md) bulgularini uygular: yedek alir, birebir metin degistirir, claim ekler/siler, kayit yazar."""
import json
import shutil
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
OUT = Path(__file__).parent / "yazar" / "out"
BACKUP = OUT / "yedek_dar_denetim_oncesi"
LOG = OUT / "degisiklik_dar.jsonl"
TOPICS = ("gunluk", "aile", "saglik", "para", "ev", "resmi")

# (slug parcasi, alan, eski, yeni, derece, bulgu)
TEXT = (
    ("okul-sistemi", "note",
     "1 Ağustos 2029'dan itibaren okul zorunlusu olacak çocuklar için okul, kayıtta Almanca düzeyini saptar ve "
     "yetersizse kabulden önceki okul yılında okulun Vorkurs'una (schulischer Vorkurs) katılmayı zorunlu kılar; bu "
     "yükümlülük 1 Ağustos 2029'dan önce okul zorunlusu olacak çocuklara uygulanmaz.",
     "Okul, ilkokula kayıtta çocuğun Almancayı yeterince bilip bilmediğini saptar. Yetersizse ve çocuk 1 Ağustos "
     "2029'da ya da sonrasında okul zorunlusu oluyorsa kabulden önceki okul yılında okulun Vorkurs'una (schulischer "
     "Vorkurs) katılması zorunludur; 1 Ağustos 2029'dan önce okul zorunlusu olacak çocuklara bu yeni zorunluluk "
     "uygulanmaz, onlar için hükmün 31 Temmuz 2026'ya kadar geçerli eski sürümü uygulanmaya devam eder.",
     "orta", "Vorkurs: kayıtta düzey saptama tarihsiz; 2029 öncesi çocuklar için eski sürüm geçerli"),
    ("grunderwerbsteuer", "cost",
     "arsa ve bina tek sözleşmeyle alınıyorsa bina yapım bedeli de matraha girer",
     "taşınmaz yapılı ya da yapılacak durumda edinildiğinde (bütünleşik sözleşme düzeni, einheitliches Vertragswerk) "
     "bina yapım bedeli de matraha girer",
     "orta", "'tek sözleşme' kaynağı daraltıyor"),
    ("widerspruch-yok", "subtitle",
     "okul, belediye harçları, Wohngeld gibi alanlarda itiraz sürer.",
     "okulun kendi işlemleri, belediye harcı, Wohngeld gibi alanlarda itiraz sürer.",
     "orta", "okul istisnası yalnız okulların çıkardığı işlemler"),
    ("widerspruch-yok", "summary",
     "İstisnalar §110 Abs. 2 ve 3'te sayılır: okul hukuku,",
     "İstisnalar §110 Abs. 2 ve 3'te sayılır: okulların kendi çıkardığı işlemler (okul hukuku),",
     "orta", "okul istisnası yalnız okulların çıkardığı işlemler"),
    ("widerspruch-yok", "summary",
     "Anlatılan yol yalnız idare mahkemesine giden işlemler içindir; sosyal mahkeme ve mali mahkeme yolları bunun "
     "dışındadır.",
     "Bu kural yalnız idare mahkemesine (VwGO yolu) götürülen işlemler içindir.",
     "küçük", "sosyal/mali mahkeme cümlesi kaynaksız; kaynağın sınırına çekildi"),
    ("widerspruch-yok", "steps",
     "(örneğin okul, belediye harcı, Wohngeld)",
     "(örneğin okulun kendi çıkardığı işlemler, belediye harcı, Wohngeld)",
     "orta", "okul istisnası yalnız okulların çıkardığı işlemler"),
    ("magaza-acilis", "summary",
     "tüm belediye alanı için yalnız bir Advent Pazarı serbest olabilir.",
     "belediyenin tamamı için yalnız bir Advent Pazarı serbest bırakılabilir; serbest bırakma belirli bölge, mahalle "
     "ya da ticaret koluyla sınırlıysa her biri için bir, belediye genelinde toplam en çok iki Advent Pazarı serbest "
     "bırakılabilir.",
     "küçük", "Advent Pazarı kuralı eksik"),
    ("kita-ucreti", "steps",
     "Ücretsiz çocuk kardeş indiriminde ücret ödüyormuş gibi sayılır ve aile hem kardeş indiriminden hem "
     "ücretsizlikten tam yararlanmalıdır.",
     "Kardeş indirimi hesaplanırken ücretsiz olan çocuk da, sanki ücret ödenecekmiş gibi kardeş olarak sayılır; aile "
     "hem kardeş indiriminden hem ücretsizlikten tam yararlanmalıdır.",
     "küçük", "kardeş indirimi cümlesi belirsiz"),
    ("u-muayeneleri", "timing",
     "beş Werktag (Pazar ve resmî tatil dışındaki günler) içinde",
     "beş Werktag içinde",
     "küçük", "Werktag tanımı kaynakta yok"),
    ("u-muayeneleri", "summary",
     "Jugendamt aileyle iletişime geçip geçmeyeceğine kendisi karar verir.",
     "belediye (Jugendamt) aileyle iletişime geçip geçmeyeceğine kendisi karar verir.",
     "küçük", "kararı kaynakta belediye veriyor"),
    ("kilise-vergisi", "summary",
     "Protestan (evangelische), Roma Katolik ve Yahudi",
     "Örneğin Protestan (evangelische), Roma Katolik ve Yahudi",
     "küçük", "kaynaktaki 'beispielsweise' düşmüş"),
    ("kira-tavani", "note",
     "Aynı basın bildirisi Mietpreisbremse için 31 Aralık 2025 sınırından söz eder; yürürlükteki yönetmelik (7 Kasım "
     "2025 sürümü) bu bölümün bitişini 31 Aralık 2029 olarak yazar. ",
     "",
     "küçük", "kaynaklar arası çelişki notu okuyucuya dönük metinde"),
    ("kira-tavani", "steps",
     "Aşağıdaki üç kural yalnız yönetmelik kapsamındaki belediyelerde geçerlidir;",
     "Önce yönetmeliğin ekindeki (Anlage) belediye listesine bak: aşağıdaki üç kural yalnız o listedeki belediyelerde "
     "geçerlidir;",
     "küçük", "listeye bakma adımı düşmüş"),
    ("wbs-gelir", "steps",
     "gerekirse ikamet belgesini (Aufenthaltsbescheinigung)",
     "gerekirse oturum hakkını gösteren belgeyi (Aufenthaltsbescheinigung)",
     "küçük", "'ikamet belgesi' adres kaydıyla karışıyor"),
    ("wbs-gelir", "documents",
     "gerekirse ikamet belgesi (Aufenthaltsbescheinigung)",
     "gerekirse oturum hakkını gösteren belge (Aufenthaltsbescheinigung)",
     "küçük", "'ikamet belgesi' adres kaydıyla karışıyor"),
)
# (slug parcasi, kanit alintisi icinde gecen ifade (kaynak secimi icin), alan, iddia, alinti)
NEW_CLAIMS = (
    ("okul-sistemi", "2029", "note", "Okul ilkokula kayıtta çocuğun Almancayı yeterince bilip bilmediğini saptar",
     "Bei der Anmeldung zu einer Schule mit Primarstufe stellt die Schule fest, ob die Kinder die deutsche Sprache "
     "hinreichend beherrschen"),
    ("okul-sistemi", "2029", "note", "2029 öncesi okul zorunlusu çocuklar için hükmün 31.07.2026'ya kadarki sürümü "
     "uygulanmaya devam eder",
     "ist § 36 Absatz 3 Satz 2 in der bis zum 31. Juli 2026 geltenden Fassung weiter anzuwenden"),
    ("magaza-acilis", "Advent", "summary", "Belediye genelinde toplam en çok iki Advent Pazarı serbest bırakılabilir",
     "insgesamt dürfen jedoch nicht mehr als zwei Adventssonntage je Gemeinde freigegeben werden"),
)
CLAIM_TEXT = (("grunderwerbsteuer-orani-ve-odeme-20",
               "Taşınmaz yapılı ya da yapılacak durumda edinildiğinde (einheitliches Vertragswerk) bina yapım bedeli "
               "matraha girer"),)
DROP_CLAIMS = ("mieterschutzverordnung-13",)


def rows(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def write(path: Path, items: list[dict]) -> None:
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in items), encoding="utf-8", newline="\n")


if BACKUP.exists():
    raise SystemExit(f"HATA: yedek zaten var: {BACKUP}")
for t in TOPICS:
    shutil.copytree(OUT / t, BACKUP / t)

log = []
for t in TOPICS:
    cpath, kpath = OUT / t / f"Yanıtlar.{t}.jsonl", OUT / t / f"claims.{t}.jsonl"
    cards, claims = rows(cpath), rows(kpath)
    new_cards = []
    for card in cards:
        new = dict(card)
        for key, field, old, repl, sev, finding in TEXT:
            if key not in card["slug"]:
                continue
            if old not in new[field]:
                raise SystemExit(f"HATA {card['slug']} {field}: bulunamadi: {old[:60]}")
            new[field] = new[field].replace(old, repl)
            log.append({"topic": t, "slug": card["slug"], "severity": sev, "finding": finding,
                        "action": "uygulandı", "note": f"{field} alanı"})
        new_cards.append(new)
    kept = [c for c in claims if not c["claim_id"].endswith(DROP_CLAIMS)]
    for c in claims:
        if c["claim_id"].endswith(DROP_CLAIMS):
            log.append({"topic": t, "slug": c["entry_id"].split(":", 1)[1], "severity": "küçük",
                        "finding": "basın bildirisi 2025 sınırı claim'i", "action": "silindi", "note": c["claim_id"]})
    kept = [dict(c, claim=text) if c["claim_id"].endswith(cid) else c for c in kept for cid, text in [
        next(((cid, text) for cid, text in CLAIM_TEXT if c["claim_id"].endswith(cid)), ("\0", ""))]]
    for key, hint, field, claim_text, quote in NEW_CLAIMS:
        card = next((c for c in new_cards if key in c["slug"]), None)
        if card is None:
            continue
        mine = [c for c in kept if c["entry_id"] == card["entry_id"]]
        ref = next(c for c in mine if hint in c["quote"])
        n = max(int(c["claim_id"].rsplit("-", 1)[1]) for c in mine) + 1
        kept.append({"claim_id": f"C-{card['slug']}-{n}", "entry_id": card["entry_id"], "field": field,
                     "claim": claim_text, "value": "", "unit": "", "period": "", "source_id": ref["source_id"],
                     "url": ref["url"], "quote": quote})
    write(cpath, new_cards)
    write(kpath, kept)

with LOG.open("w", encoding="utf-8", newline="\n") as f:
    f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in log)
print(f"uygulanan degisiklik: {len(log)}; kayit: {LOG}")
