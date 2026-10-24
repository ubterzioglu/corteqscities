r"""Acik-mi kapisi (IYILESTIRME_LISTESI B15, P0): places fazinda her mekanin "bugun acik mi" taramasi tam mi,
supheci dogrulamadan gecti mi, kararlar kartlara islendi mi. Ajan talimati: city-pack agents\acik-mi.md.

Kullanim: acik_mi.py <WORK>\_is\acik_mi --mekanlar <WORK>\_is\data\parcalar
            [--kaynaklar <WORK>\_is\kaynak_dizini.jsonl] [--min-year YYYY] [--out rapor.json]
Girdi (semalar pilot ciktilariyla ayni: TARAMA_ALANLARI, DOGRULAMA_ALANLARI): klasordeki <grup>.jsonl tarayici,
<grup>_dogrulama.jsonl supheci dogrulayici satirlaridir (bos dosya olabilir; alt klasor okunmaz). --mekanlar: dosya
(data\Mekânlar.jsonl), klasor (icindeki Mekânlar*.jsonl, or. data\parcalar) ya da son bileseni joker desen; birden cok
verilebilir, ayni entry_id tek mekan sayilir. --kaynaklar (istege bagli; source_id, url, final_url): verilirse
'kartta belirt' kartinda kanit kaynaginin kimligi de aranir. --min-year: 'açık' kanitinin en eski yili (varsayilan bu
yil - 1; B15 '2025-26'); kontrol yili = --min-year + 1, kart notu bu yil ya da sonrasi tarihli olmali.

Bulgular (kod; CODES):
  tarama_yok      listedeki mekanin hicbir tarama dosyasinda satiri yok.
  gecersiz_durum  tarama 'durum'u DURUMLAR'dan biri degil (bosluk ve Unicode bicimi esitlenir, buyuk/kucuk harf degil).
  gecersiz_eylem, gecersiz_sonuc  dogrulama 'eylem'i EYLEMLER'den, 'sonuc'u SONUCLAR'dan biri degil.
  dogrulama_yok   'açık' olmayan tarama satirinin (gecersiz durum dahil) dogrulama satiri yok.
  eylem_celiski   'onay' verilen kararla eylem celisiyor: 'kapalı' yalniz 'sil'le, CHANGED durumlari 'dokunma' disiyla
                  gecer. Durum dogrulama satirinin serbest metni 'tarama_durum'dan degil, ayni grubun (grupta yoksa her
                  grubun) ayni entry_id'li tarama satirindan okunur.
  sil_listede     'sil' eylemli mekan hala listede.
  ikinci_kaynak_yok  'sil' satirinin gerekce'sinde kanit_url'nin alan adindan (ve alt alan adlarindan) baska alan adli
                  tam adres (http/https) yok: ikinci bagimsiz kaynak sart; tek kaynakli kapanis insan kararina gider.
  not_yok         'kartta belirt' kartinin metninde (TEXT_FIELDS) "<gün> <ay> <yıl> itibarıyla" notu (ay-yil, YYYY-AA-GG,
                  GG.AA.YYYY de olur; yil >= kontrol yili) yok. Kaynak izi notun yerini tutmaz.
  kaynak_izi_yok  (yalniz --kaynaklar ile) 'kartta belirt' kartinin source_ids'inde kanit_url'nin kaynak kimligi yok.
  bos_alinti, bos_url  kanit_alinti ya da kanit_url bos.
  eski_kanit      'açık' satirinin kanit_tarihi'nde parantezden onceki tarih yok, 'tarihsiz…' ya da --min-year'dan
                  eski; ya da tarih footer / telif / erisim gunu kaynakli (DATE_SOURCE_MARK).
  footer_kanit    'açık' satirinin alintisi yalniz telif (footer) satiri: sitenin varligi acik kaniti degildir.
  kimliksiz       tarama ya da dogrulama satirinda entry_id yok.
Dogrulama satiri olan mekanda karar onundur: tarama satirinin kanitina ve dogrulama_yok kuralina bakilmaz. Eylem
kurallari 'sonuc'tan bagimsizdir (pilotta 'ret' + 'kartta belirt' vardi); yalniz eylem_celiski 'onay'a bakar. Her satir
ayri denetlenir (pilotta bir mekan iki grupta tarandi). Listede olmayan mekanin (or. 'sil' sonrasi) 'açık' kaniti
aranmaz (pakette degil); 'açık' disi kararin dogrulamasi ve dogrulama satirinin kurallari listeden bagimsizdir. Bu
satirlar 'listede_olmayan' altinda sayilir.
Salt okunur; --out (tam rapor JSON) bir girdinin ustune ya da acik-mi klasorune yazilmaz. stdout tek satir JSON
(sayilar, durum dagilimi, eylem/sonuc sayilari, ilk MAX_ITEMS bulgu). Cikis: 0 temiz / 1 bulgu / 2 kullanim hatasi ya
da okunamayan girdi (bozuk JSONL, bos ya da kimliksiz mekan listesi, eksik klasor/dosya).
"""
from __future__ import annotations

import argparse
import datetime as dt
import fnmatch
import json
import os
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Sequence
from urllib.parse import urlsplit

import common

TOOL = "acik_mi"
MAX_ITEMS = 20  # stdout'taki bulgu sayisi; tamami --out raporunda
OPEN, CLOSED, DELETE, NOTE, KEEP, CONFIRM = "açık", "kapalı", "sil", "kartta belirt", "dokunma", "onay"
DURUMLAR = (OPEN, CLOSED, "geçici kapalı", "taşındı", "insaat", "belirsiz")
CHANGED = ("geçici kapalı", "taşındı", "insaat")  # onaylanirsa kart degismeli: 'dokunma' olmaz
EYLEMLER = (DELETE, NOTE, KEEP)
SONUCLAR = (CONFIRM, "ret")
CODES = ("tarama_yok", "gecersiz_durum", "gecersiz_eylem", "gecersiz_sonuc", "dogrulama_yok", "eylem_celiski",
         "sil_listede", "ikinci_kaynak_yok", "not_yok", "kaynak_izi_yok", "bos_alinti", "bos_url", "eski_kanit",
         "footer_kanit", "kimliksiz")
TARAMA_ALANLARI = ("entry_id", "title", "durum", "kanit_url", "kanit_alinti", "kanit_tarihi", "not")
DOGRULAMA_ALANLARI = ("entry_id", "title", "tarama_durum", "sonuc", "eylem", "kanit_url", "kanit_alinti",
                      "kanit_tarihi", "yeni_bilgi", "gerekce")
VERIFY_SUFFIX = "_dogrulama"
VENUE_GLOB = "Mekânlar*.jsonl"
TEXT_FIELDS = ("subtitle", "summary", "note", "visit_status")  # okuyucunun gordugu kart metni
YEAR_RANGE = (1900, 2100)
MONTHS = ("Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık")
_MONTH = "|".join(sorted({form for name in MONTHS for form in (name, name[0].lower() + name[1:])}, key=len, reverse=True))
_DATE = rf"(?:\d{{1,2}}\s+)?(?:{_MONTH})\s+\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}\.\d{{1,2}}\.\d{{4}}"
AS_OF = re.compile(rf"(?<![\w.])({_DATE})(?:\s+tarihi)?\s+itibar[ıi]\s*(?:yla|yle|ile)\b")
YEAR = re.compile(r"(?<!\d)(?:19|20)\d{2}(?!\d)")
URL = re.compile(r"https?://[^\s\"'<>()\[\]]+", re.I)
DATE_SOURCE_MARK = re.compile(r"©|\(c\)|\bcopyright\b|\bfooter\b|\btelif\b|\beri[sş]i[lm]", re.I)  # kanit_tarihi'nde
FOOTER_MARK = re.compile(r"©|\(c\)|\bcopyright\b|\ball rights reserved\b|\balle rechten voorbehouden\b|"
                         r"\balle rechte vorbehalten\b|\btüm hakları saklıdır\b", re.I)
FOOTER_EXTRAS = (  # footer'da yaygin, rakami tarih olmayan bilgiler; sira onemli (telefon posta kodundan once)
    re.compile(r"\b(?:kvk|btw|vat|ust-?id\w*|steuer\w*|hr[ab]|mersis|vergi)\b[^\d|•·]{0,20}\d[\d ./]{3,}[\dA-Z]*",
               re.I),  # sicil / vergi numarasi
    re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+|\b(?:https?://|www\.)\S+", re.I),  # e-posta, web adresi
    re.compile(r"(?:\+|(?<!\d)0)\d(?:[ ()/.-]*\d){8,}"),  # telefon (en az 10 rakam; GG.AA.YYYY 8 rakamdir)
    re.compile(r"(?<!\d)\d{4} ?[A-Z]{2}(?![A-Za-z])|(?<!\d)\d{5}(?!\d)"),  # posta kodu: NL 1234 AB, DE/TR 12345
)
HOUSE_NUMBER = re.compile(r"\b[^\W\d_][\w'.-]*\s+\d{1,4}[a-zA-Z]?(?=\s*(?:[,|•·–-]|$))")  # "Ventoselaan 1," / "… 15 |"
FOOTER_MAX_WORDS = 8  # telif isareti ve yil cikinca kalan sahip adi (or. "Neoseum, Next-Gen Reality B.V." = 6)


class UsageError(Exception):
    """Kullanim hatasi ya da okunamayan girdi (cikis 2)."""


@dataclass(frozen=True)
class Rec:
    path: Path
    line: int
    row: dict[str, Any]

    @property
    def where(self) -> str:
        return f"{self.path.name}:{self.line}"


@dataclass(frozen=True)
class Finding:
    code: str
    entry_id: str
    where: str
    message: str


@dataclass(frozen=True)
class Sweep:
    scans: tuple[Rec, ...]
    verifs: tuple[Rec, ...]
    scan_files: int
    verify_files: int


@dataclass(frozen=True)
class Gate:
    """Kapinin girdileri: sources None = --kaynaklar verilmedi (kaynak izi aranmaz)."""
    venues: dict[str, list[Rec]]
    sweep: Sweep
    sources: dict[str, set[str]] | None
    min_year: int


# ---------- metin kurallari ----------

def nfc(value: str) -> str:
    return unicodedata.normalize("NFC", value)


def text(value: Any) -> str:
    """Alan degeri: metin degilse bos; NFC, kenar bosluklari atilir."""
    return nfc(value).strip() if isinstance(value, str) else ""


def default_min_year(today: dt.date | None = None) -> int:
    """B15: 'açık' kaniti kontrol yili ya da bir onceki yil tarihli olmali."""
    return (today or dt.date.today()).year - 1


def dated_note(value: str, min_year: int) -> bool:
    """Metinde '<gün> <ay> <yıl> itibarıyla' (ay-yil, YYYY-AA-GG, GG.AA.YYYY de olur) var ve yili >= min_year."""
    return any(max(int(year) for year in re.findall(r"\d{4}", match.group(1))) >= min_year
               for match in AS_OF.finditer(nfc(value)))


def evidence_year(when: str) -> int | None:
    """kanit_tarihi'nin yili: parantezden onceki kismin en buyuk yili (parantez tarihin kaynagini anlatir);
    'tarihsiz…' ya da yilsizsa None."""
    head = nfc(when).split("(", 1)[0]
    if head.strip().casefold().startswith("tarihsiz"):
        return None
    years = [int(year) for year in YEAR.findall(head)]
    return max(years) if years else None


def is_footer_only(quote: str) -> bool:
    """Alinti yalniz telif satiri mi: telif isareti var; sicil/vergi no, e-posta, web adresi, telefon, posta kodu,
    isaretler, yillar ve adres numarasi cikinca kalan rakamsiz ve en cok FOOTER_MAX_WORDS sozcuk (sahibin adi)."""
    value = nfc(quote)
    if not FOOTER_MARK.search(value):
        return False
    for pattern in (*FOOTER_EXTRAS, FOOTER_MARK, YEAR, HOUSE_NUMBER):
        value = pattern.sub(" | ", value)  # ayirac birakir: adres numarasi ondan once gelir
    return not re.search(r"\d", value) and len(re.findall(r"\w+", value)) <= FOOTER_MAX_WORDS


def host_of(url: str) -> str:
    """Adresin alan adi (kucuk harf; 'www.' ve sondaki nokta atilir); cozulemezse bos."""
    try:
        host = urlsplit(url.strip().rstrip(".,;:!?")).hostname or ""
    except ValueError:
        return ""
    return host.rstrip(".").removeprefix("www.")


def same_site(host: str, other: str) -> bool:
    """Ayni alan adi ya da biri digerinin alt alan adi (or. archief.nieuws.example ~ nieuws.example)."""
    return host == other or host.endswith("." + other) or other.endswith("." + host)


# ---------- okuma ----------

def read_jsonl(path: Path) -> list[Rec]:
    """JSONL nesne satirlari (BOM'lu UTF-8 de okunur; bos satir atlanir)."""
    records = []
    try:
        with Path(path).open(encoding="utf-8-sig") as stream:
            for number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as error:
                    raise UsageError(f"{path}:{number}: geçersiz JSON ({error.msg})") from error
                if not isinstance(row, dict):
                    raise UsageError(f"{path}:{number}: JSON nesnesi bekleniyor")
                records.append(Rec(Path(path), number, row))
    except UnicodeDecodeError as error:
        raise UsageError(f"{path}: UTF-8 değil ({error.reason})") from error
    return records


def matching(folder: Path, pattern: str) -> list[Path]:
    """Klasorde adi (NFC) desene uyan dosyalar, ad sirasiyla: baska sistemden gelen NFD ad da bulunur."""
    if not folder.is_dir():
        return []
    wanted = nfc(pattern)
    found = [path for path in folder.iterdir() if path.is_file() and fnmatch.fnmatch(nfc(path.name), wanted)]
    return sorted(found, key=lambda path: nfc(path.name))


def venue_files(specs: Sequence[str]) -> list[Path]:
    files: dict[str, Path] = {}
    for spec in specs:
        path = Path(spec)
        if any(char in path.name for char in "*?["):
            found, problem = matching(path.parent, path.name), f"--mekanlar desenine uyan dosya yok: {spec}"
        elif path.is_dir():
            found, problem = matching(path, VENUE_GLOB), f"--mekanlar klasöründe {VENUE_GLOB} yok: {spec}"
        else:
            found, problem = ([path] if path.is_file() else []), f"--mekanlar bulunamadı: {spec}"
        if not found:
            raise UsageError(problem)
        for item in found:
            files.setdefault(os.path.normcase(os.path.abspath(item)), item)
    return list(files.values())


def load_venues(files: Sequence[Path]) -> dict[str, list[Rec]]:
    """entry_id -> kart satirlari (ayni kimlik birlesik dosyada ve parcada birlikte olabilir)."""
    venues: dict[str, list[Rec]] = {}
    for path in files:
        for rec in read_jsonl(path):
            entry = text(rec.row.get("entry_id"))
            if not entry:
                raise UsageError(f"{path}:{rec.line}: entry_id yok")
            venues.setdefault(entry, []).append(rec)
    if not venues:
        raise UsageError("mekân listesi boş: " + ", ".join(str(path) for path in files))
    return venues


def load_sweep(folder: Path) -> Sweep:
    if not folder.is_dir():
        raise UsageError(f"açık-mı klasörü yok: {folder}")
    files = sorted(path for path in folder.glob("*.jsonl") if path.is_file())
    verify = [path for path in files if path.stem.endswith(VERIFY_SUFFIX)]
    scan = [path for path in files if path not in verify]
    return Sweep(tuple(rec for path in scan for rec in read_jsonl(path)),
                 tuple(rec for path in verify for rec in read_jsonl(path)), len(scan), len(verify))


def load_sources(files: Sequence[Path]) -> dict[str, set[str]] | None:
    """Kanonik adres (url ve final_url) -> kaynak kimlikleri; dosya verilmediyse None. Kimliksiz ya da adressiz
    satir iz vermez."""
    if not files:
        return None
    index: dict[str, set[str]] = {}
    for path in files:
        if not path.is_file():
            raise UsageError(f"--kaynaklar bulunamadı: {path}")
        for rec in read_jsonl(path):
            sid = text(rec.row.get("source_id"))
            urls = [text(rec.row.get(key)) for key in ("url", "final_url")]
            for url in (url for url in urls if sid and url):
                index.setdefault(common.canonical_source_url(url), set()).add(sid)
    return index


# ---------- kurallar: tarama ----------

def ids_of(records: Iterable[Rec]) -> set[str]:
    return {text(rec.row.get("entry_id")) for rec in records} - {""}


def coverage_findings(venues: dict[str, list[Rec]], scanned: set[str]) -> list[Finding]:
    return [Finding("tarama_yok", entry, cards[0].where,
                    f"{text(cards[0].row.get('title')) or entry}: hiçbir tarama dosyasında satırı yok")
            for entry, cards in venues.items() if entry not in scanned]


def evidence_findings(rec: Rec, entry: str) -> list[Finding]:
    rules = (("kanit_alinti", "bos_alinti", "kararın birebir alıntısı yok"), ("kanit_url", "bos_url", "alıntının sayfası yok"))
    return [Finding(code, entry, rec.where, f"{key} boş: {why}") for key, code, why in rules if not text(rec.row.get(key))]


def open_evidence_findings(rec: Rec, entry: str, min_year: int) -> list[Finding]:
    found = []
    when = text(rec.row.get("kanit_tarihi"))
    year = evidence_year(when)
    if DATE_SOURCE_MARK.search(when):
        found.append(Finding("eski_kanit", entry, rec.where,
                             f"kanit_tarihi footer / telif / erişim tarihine dayanıyor ({when!r}): tarihli faaliyet değil"))
    elif year is None or year < min_year:
        found.append(Finding("eski_kanit", entry, rec.where,
                             f"'açık' kanıtı {min_year} ya da sonrası tarihli değil (kanit_tarihi {when!r})"))
    if is_footer_only(text(rec.row.get("kanit_alinti"))):
        found.append(Finding("footer_kanit", entry, rec.where,
                             "alıntı yalnız telif (footer) satırı; sitenin varlığı açık kanıtı değildir"))
    return found


def scan_findings(gate: Gate) -> list[Finding]:
    found: list[Finding] = []
    verified = ids_of(gate.sweep.verifs)
    for rec in gate.sweep.scans:
        entry, durum = text(rec.row.get("entry_id")), text(rec.row.get("durum"))
        if not entry:
            found.append(Finding("kimliksiz", "", rec.where, "tarama satırında entry_id yok"))
            continue
        if durum not in DURUMLAR:
            found.append(Finding("gecersiz_durum", entry, rec.where,
                                 f"durum {durum!r} geçersiz; izinli: {' | '.join(DURUMLAR)}"))
        if entry in verified:
            continue  # karar dogrulayicinin: kanit dogrulama satirinda aranir
        if durum != OPEN:
            found.append(Finding("dogrulama_yok", entry, rec.where, f"{durum!r} kararının doğrulama satırı yok"))
        if entry not in gate.venues:
            continue  # pakette degil: 'açık' kaniti aranmaz
        found += evidence_findings(rec, entry)
        if durum == OPEN:
            found += open_evidence_findings(rec, entry, gate.min_year)
    return found


# ---------- kurallar: dogrulama ----------

def scan_statuses(scans: Iterable[Rec]) -> dict[tuple[str | None, str], frozenset[str]]:
    """(grup, entry_id) ve (None, entry_id) -> gecerli tarama durumlari."""
    found: dict[tuple[str | None, str], set[str]] = {}
    for rec in scans:
        entry, durum = text(rec.row.get("entry_id")), text(rec.row.get("durum"))
        if entry and durum in DURUMLAR:
            for key in ((rec.path.stem, entry), (None, entry)):
                found.setdefault(key, set()).add(durum)
    return {key: frozenset(value) for key, value in found.items()}


def conflict_findings(rec: Rec, entry: str, statuses: dict[tuple[str | None, str], frozenset[str]]) -> list[Finding]:
    """'onay' verilen kararla celisen eylem; durum ayni grubun (grupta yoksa her grubun) tarama satirindan."""
    sonuc, eylem = text(rec.row.get("sonuc")), text(rec.row.get("eylem"))
    if sonuc != CONFIRM or eylem not in EYLEMLER:
        return []
    group = rec.path.stem.removesuffix(VERIFY_SUFFIX)
    durumlar = statuses.get((group, entry)) or statuses.get((None, entry), frozenset())
    changed = sorted(durumlar & set(CHANGED))
    if CLOSED in durumlar and eylem != DELETE:
        why = f"'{CLOSED}' kararı onaylandı ama eylem {eylem!r}: kalıcı kapanışta yalnız 'sil' geçer"
    elif changed and eylem == KEEP:
        why = f"{changed[0]!r} kararı onaylandı ama eylem 'dokunma': kart değişmeden kalamaz"
    else:
        return []
    return [Finding("eylem_celiski", entry, rec.where, why + " (durum tarama satırından)")]


def second_source_findings(rec: Rec, entry: str) -> list[Finding]:
    first = host_of(text(rec.row.get("kanit_url")))
    hosts = {host_of(url) for url in URL.findall(text(rec.row.get("gerekce")))} - {""}
    if first and any(not same_site(host, first) for host in hosts):
        return []
    return [Finding("ikinci_kaynak_yok", entry, rec.where,
                    "'sil' için ikinci bağımsız kaynak yok: gerekce'de kanit_url'den başka alan adlı tam adres "
                    "(https://…) bekleniyor; tek kaynaklı kapanış insan kararına gider")]


def card_source_ids(card: dict[str, Any]) -> set[str]:
    raw = card.get("source_ids")
    return {text(item) for item in (raw if isinstance(raw, list) else str(raw or "").split(";"))} - {""}


def note_findings(rec: Rec, entry: str, cards: Sequence[Rec], sources: dict[str, set[str]] | None,
                  control_year: int) -> list[Finding]:
    """'kartta belirt': tarihli not her zaman, kanit kaynaginin kimligi --kaynaklar verildiyse ayrica aranir."""
    url = text(rec.row.get("kanit_url"))
    traced = sources.get(common.canonical_source_url(url), set()) if sources is not None and url else set()
    found = []
    for card in cards:
        if not dated_note("\n".join(text(card.row.get(key)) for key in TEXT_FIELDS), control_year):
            found.append(Finding("not_yok", entry, rec.where,
                                 f"'kartta belirt' kartında {control_year} ya da sonrası tarihli not yok ({card.where}): "
                                 "'<gün> <ay> <yıl> itibarıyla …' cümlesi bekleniyor"))
        if sources is not None and url and not card_source_ids(card.row) & traced:
            found.append(Finding("kaynak_izi_yok", entry, rec.where,
                                 f"kanıt adresinin kaynak kimliği kartın source_ids'inde yok ({card.where}): "
                                 "add_sources ile kaynak yapıp kimliği ekle"))
    return found


def action_findings(rec: Rec, entry: str, cards: Sequence[Rec], gate: Gate) -> list[Finding]:
    eylem = text(rec.row.get("eylem"))
    if eylem == DELETE:
        return [*(Finding("sil_listede", entry, rec.where, f"'sil' eylemli mekân hâlâ listede ({card.where})")
                  for card in cards[:1]), *second_source_findings(rec, entry)]
    if eylem == NOTE:
        return note_findings(rec, entry, cards, gate.sources, gate.min_year + 1)
    return []


def verify_findings(gate: Gate) -> list[Finding]:
    found: list[Finding] = []
    statuses = scan_statuses(gate.sweep.scans)
    for rec in gate.sweep.verifs:
        entry = text(rec.row.get("entry_id"))
        if not entry:
            found.append(Finding("kimliksiz", "", rec.where, "doğrulama satırında entry_id yok"))
            continue
        for key, code, allowed in (("sonuc", "gecersiz_sonuc", SONUCLAR), ("eylem", "gecersiz_eylem", EYLEMLER)):
            value = text(rec.row.get(key))
            if value not in allowed:
                found.append(Finding(code, entry, rec.where, f"{key} {value!r} geçersiz; izinli: {' | '.join(allowed)}"))
        found += evidence_findings(rec, entry)
        found += conflict_findings(rec, entry, statuses)
        found += action_findings(rec, entry, gate.venues.get(entry, []), gate)
    return found


def collect(gate: Gate) -> list[Finding]:
    return [*coverage_findings(gate.venues, ids_of(gate.sweep.scans)), *scan_findings(gate), *verify_findings(gate)]


# ---------- rapor ve komut satiri ----------

def tally(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items(), key=lambda item: (-item[1], item[0])))


def unlisted(records: Iterable[Rec], venues: dict[str, list[Rec]]) -> int:
    entries = (text(rec.row.get("entry_id")) for rec in records)
    return sum(1 for entry in entries if entry and entry not in venues)


def build_report(folder: Path, inputs: dict[str, list[str]], gate: Gate, findings: Sequence[Finding],
                 out: Path | None) -> dict[str, Any]:
    sweep, venues = gate.sweep, gate.venues
    return {
        "tool": TOOL, "acik_mi": str(folder), **inputs, "min_year": gate.min_year, "mekan": len(venues),
        "tarama": {"dosya": sweep.scan_files, "satir": len(sweep.scans), "mekan": len(ids_of(sweep.scans))},
        "dogrulama": {"dosya": sweep.verify_files, "satir": len(sweep.verifs)},
        "durum": tally(text(rec.row.get("durum")) for rec in sweep.scans),
        "eylem": tally(text(rec.row.get("eylem")) for rec in sweep.verifs),
        "sonuc": tally(text(rec.row.get("sonuc")) for rec in sweep.verifs),
        "listede_olmayan": {"tarama": unlisted(sweep.scans, venues), "dogrulama": unlisted(sweep.verifs, venues)},
        "findings": [asdict(finding) for finding in findings],
        "by_code": tally(finding.code for finding in findings), "out": None if out is None else str(out)}


def check_out(out: Path, inputs: Sequence[Path], folder: Path) -> None:
    def real(path: Path) -> str:
        return os.path.normcase(os.path.realpath(path))

    if any(real(out) == real(path) for path in inputs):
        raise UsageError(f"--out bir girdinin üstüne yazamaz: {out}")
    if real(out) == real(folder) or real(out).startswith(real(folder).rstrip(os.sep) + os.sep):
        raise UsageError(f"--out açık-mı klasörüne yazamaz: {out}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Açık-mı kapısı (B15): mekân taraması ve şüpheci doğrulama tam mı, kararlar kartlara işlendi mi")
    parser.add_argument("acik_mi", metavar="ACIK_MI_KLASORU", help="<grup>.jsonl ve <grup>_dogrulama.jsonl klasörü")
    parser.add_argument("--mekanlar", action="extend", nargs="+", required=True, metavar="YOL",
                        help="mekân listesi: Mekânlar.jsonl, klasör (içindeki Mekânlar*.jsonl) ya da desen")
    parser.add_argument("--kaynaklar", action="extend", nargs="+", type=Path, metavar="JSONL",
                        help="kaynak dizini (source_id, url, final_url): 'kartta belirt' kartında kanıt kaynağı izi")
    parser.add_argument("--min-year", type=int,
                        help="'açık' kanıtının en eski yılı (varsayılan: bu yıl - 1); kart notu bunun bir sonrası")
    parser.add_argument("--out", type=Path, help="tam rapor JSON (girdinin üstüne ve açık-mı klasörüne yazılmaz)")
    return parser


def run(args: argparse.Namespace) -> int:
    min_year = default_min_year() if args.min_year is None else args.min_year
    if not YEAR_RANGE[0] <= min_year <= YEAR_RANGE[1]:
        raise UsageError(f"--min-year {YEAR_RANGE[0]}–{YEAR_RANGE[1]} arasında olmalı: {min_year}")
    folder, out = Path(args.acik_mi), args.out
    venue_paths, source_paths = venue_files(args.mekanlar), list(args.kaynaklar or [])
    if out is not None:
        check_out(out, [*venue_paths, *source_paths], folder)
    gate = Gate(load_venues(venue_paths), load_sweep(folder), load_sources(source_paths), min_year)
    findings = collect(gate)
    inputs = {"mekanlar": [str(path) for path in venue_paths], "kaynaklar": [str(path) for path in source_paths]}
    report = build_report(folder, inputs, gate, findings, out)
    if out is not None:
        common.write_json(out, report)
    common.emit({**{key: value for key, value in report.items() if key not in ("mekanlar", "kaynaklar", "findings")},
                 "findings": len(findings), "items": report["findings"][:MAX_ITEMS]})
    return common.EXIT_FINDINGS if findings else common.EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    common.setup_utf8()
    try:
        args = build_parser().parse_args(argv)
    except SystemExit as stop:
        return common.EXIT_USAGE if stop.code else common.EXIT_OK
    try:
        return run(args)
    except (UsageError, OSError) as exc:  # yakalanmazsa cikis 1 olur, 'bulgu' ile karisir
        common.emit({"tool": TOOL, "error": str(exc)})
        return common.EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
