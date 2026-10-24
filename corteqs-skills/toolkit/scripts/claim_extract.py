"""claim_extract.py <xlsx> --out claims.jsonl [--topics a,b]

Kart metinlerinden degisken iddia envanteri (K29 / K34 / K37 / K40) cikarir; ag erisimi yok, Excel salt okunur.
Kaynak alanlar: Yanıtlar (summary, steps, documents, timing, cost, note) ve Sözlük (definition).
Iddia turleri: money (EUR), percent, duration (hour/day/week/month/year), age, weekday (+ayin n. gunu), time, phone, date.
Sayi bicimi: Turkce/Hollandaca virgul ondalik + nokta binlik ('1.234,56', '85,15', '2.500'); '4.4' ve '1,234.56' de cozulur.
Para carpani: '€1,5 milyon' -> value 1500000 + scale 1000000 (claim_check '1,5 miljoen' ve '1.500.000' bicimlerini arar).
Yer adi icindeki gun-ay tarih degildir (claim_places): '18 Septemberplein', '18 September-plein', '19 Mayıs Caddesi'. Tarih kalir:
'18 september', '20 Kasım Cuma', '18 Eylül Markt'ta', '4 Mayıs Dam Meydanı'nda', '4 Mayısta …', '1 Mayıs 2026 Sokak şenliği'.

Her satir bir iddia: claim_id (<entry_id>:#n), entry_id (Sözlük'te term_id), sheet, _row (Excel satiri), field, kind,
text (eslesen parca), sentence (iddia cumlesi), values (normallestirilmis), source_ids, sources [{source_id, url}],
missing_source_ids (Kaynaklar'da olmayan), topic_id, reviewed_on. Ayni kartta ayni alan+cumle+deger bir kez yazilir.
--topics: virgulle topic_id (tam ya da ':' sonrasi son ek); verilirse yalniz eslesen Yanıtlar kartlari, Sözlük atlanir.
stdout: tek satir JSON ozeti. Cikis: 0 temiz / 1 kaynaksiz iddia ya da Kaynaklar'da olmayan source_id / 2 kullanim-yapi hatasi.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

import claim_places
import common
import xlsx_dump

TEXT_FIELDS = {"Yanıtlar": ("summary", "steps", "documents", "timing", "cost", "note"), "Sözlük": ("definition",)}
ID_KEYS = {"Yanıtlar": "entry_id", "Sözlük": "term_id"}
REQUIRED_SHEETS = ("Yanıtlar", "Kaynaklar")
LOADED_SHEETS = ("Yanıtlar", "Sözlük", "Kaynaklar")

NUM = r"(?:\d{1,3}(?:[.,]\d{3})+(?:[.,]\d{1,2})?(?!\d)|\d+(?:[.,]\d+)?)"
DASH = r"\s?[-–—]\s?"
RANGE = rf"(?P<a>{NUM})(?:{DASH}(?P<b>{NUM}))?"
NUM_TOKEN = r"(?<![\d.,]){alts}(?![\d]|[.,]\d)"
PREFIX_PCT = r"(?<![\d.,])(?<![\d.,]\s)%"  # Turkce '%4,4'; '35,75% 2' icindeki % onceki sayiya aittir
COUNT_WORDS = r"(?:ziyaret|kişi|kez|defa|adet|kat|oda|gece|gün|hafta|ay\b|yıl|saat|bilet)"  # '4+ ziyaret' yas degil
SPACES = re.compile(r"[   ]")
SENTENCE_END = re.compile(r"(?<=[.!?;])\s+")

# Turkce ekler beyaz listededir: 'güncel/güney/güneş', 'yıldız/yılbaşı', 'senet' birim degildir.
UNIT_PATTERNS = {
    "hour": r"saat(?:lik|te|ten|tir|e|i)?(?!\w)|uur(?!\w)|uren(?!\w)|hours?(?!\w)",
    "day": (r"(?:iş\s)?gün(?:ü\w*|lü[kğ]\w*|ler\w*|e|de|den|da|dür|dir)?(?!\w)|(?:werk|kalender)?dag(?:en)?(?!\w)"
            r"|(?:business\s|working\s)?days?(?!\w)"),
    "week": r"hafta\w*|weken(?!\w)|weeks?(?!\w)",
    "month": r"ay(?:lar|ları|lık|lığına|lıktır|da|dan|dır|a|ı)?(?!\w)|maand(?:en)?(?!\w)|months?(?!\w)",
    "year": (r"yıl(?:ı\w*|l\w*|a|da|dan|dır|dir)?(?!\w)|sene(?:s\w*|l\w*|ye|yi|de|den|dir)?(?!\w)"
             r"|jaar(?!\w)|jaren(?!\w)|years?(?!\w)"),
}
SCALES = {"bin": 10**3, "duizend": 10**3, "thousand": 10**3, "milyon": 10**6, "miljoen": 10**6, "million": 10**6,
          "mln": 10**6, "mio": 10**6, "milyar": 10**9, "miljard": 10**9, "billion": 10**9, "mld": 10**9, "mrd": 10**9}
UNIT_RX = {unit: re.compile(rx, re.IGNORECASE) for unit, rx in UNIT_PATTERNS.items()}
MONTHS = {name: i for i, name in enumerate(("ocak", "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül",
                                             "ekim", "kasım", "aralık"), start=1)}
MONTHS.update({name: i for i, name in enumerate(("januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
                                                  "september", "oktober", "november", "december"), start=1)})
DAYS = {"pazartesi": "monday", "salı": "tuesday", "çarşamba": "wednesday", "perşembe": "thursday", "cumartesi": "saturday",
        "cuma": "friday", "pazar": "sunday", "maandag": "monday", "dinsdag": "tuesday", "woensdag": "wednesday",
        "donderdag": "thursday", "vrijdag": "friday", "zaterdag": "saturday", "zondag": "sunday"}
ORDINALS = {"ilk": 1, "birinci": 1, "ikinci": 2, "üçüncü": 3, "dördüncü": 4, "son": -1}
TR_DAY_SUFFIX = re.compile(r"(?:ları|leri|lari|ya|ye|yı|yi|dan|den|da|de|ı|i|sı|si|nın|nin|ki)?", re.IGNORECASE)
NL_DAY_SUFFIX = re.compile(r"(?:en|s|avond|middag|ochtend|morgen|nacht)?", re.IGNORECASE)
SUNDAY_NEXT = re.compile(r"\s(?:gün\w*|sabah\w*|akşam\w*|öğle\w*|açılış\w*)", re.IGNORECASE)
SUNDAY_PREV = re.compile(r"(?:\bher|cumartesi|cuma|pazartesi)\s*(?:ve|veya|-|–|,)?\s*$", re.IGNORECASE)


def _fold(text: str) -> str:
    """Turkce noktasiz/noktali i farkini yok sayan kucuk harf ('ARALIK' -> 'aralik', 'Aralık' -> 'aralik')."""
    return text.lower().replace("i̇", "i").replace("ı", "i")


MONTH_LOOKUP = {_fold(name): number for name, number in MONTHS.items()}
DAY_LOOKUP = {_fold(name): day for name, day in DAYS.items()}
ORDINAL_LOOKUP = {_fold(name): number for name, number in ORDINALS.items()}
SCALE_LOOKUP = {_fold(name): number for name, number in SCALES.items()}
NL_DAYS = frozenset(name for name in DAYS if name.endswith("dag"))


class ClaimError(Exception):
    """Kullanim veya yapi hatasi (cikis kodu 2)."""


def parse_number(text: str) -> int | float:
    """'85,15' -> 85.15, '1.234,56' -> 1234.56, '2.500' -> 2500, '4.4' -> 4.4, '1,234.56' -> 1234.56."""
    s = text.strip()
    if "," in s and "." in s:
        dec = "," if s.rfind(",") > s.rfind(".") else "."
        s = s.replace("." if dec == "," else ",", "").replace(dec, ".")
    elif s.count(",") > 1 or s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3):
        s = s.replace(",", "").replace(".", "")
    else:
        s = s.replace(",", ".")
    value = float(s)
    return int(value) if value.is_integer() else round(value, 6)


def alternation(forms: Iterable[str]) -> str:
    """Kacisli, en uzun once, belirlenimci regex secenekleri: (?:a|b)."""
    return "(?:" + "|".join(re.escape(f) for f in sorted(set(forms), key=lambda f: (-len(f), f))) + ")"


def _int_forms(n: int) -> set[str]:
    grouped = f"{n:,}"
    return {str(n)} | ({grouped, grouped.replace(",", "."), grouped.replace(",", " ")} if n >= 1000 else set())


def number_regex(value: float) -> str:
    """parse_number'in tersi: degerin metin bicimleri (85.15 -> 85,15|85.15; 80 -> 80|80,00|80,-; 2500 -> 2.500|2,500|2500).

    Sayi daha buyuk bir sayinin parcasi olamaz ('185,15', '800', '80,50' eslesmez).
    """
    number = float(value)
    if number.is_integer():
        return NUM_TOKEN.format(alts=alternation(_int_forms(int(number))) + r"(?:[.,]00?|,-)?")
    whole, frac = f"{number:.6f}".rstrip("0").split(".")
    fracs = {frac} | ({frac + "0"} if len(frac) == 1 else set())
    return NUM_TOKEN.format(alts=alternation(f"{i}{sep}{f}" for i in _int_forms(int(whole)) for sep in ",." for f in fracs))


def _range_values(m: re.Match, make: Callable[[int | float], dict[str, Any]]) -> list[dict[str, Any]]:
    return [make(parse_number(m.group(g))) for g in ("a", "b") if m.group(g)]


def _scaled_money(number: int | float, scale: int) -> dict[str, Any]:
    value = round(number * scale, 6)
    money = {"kind": "money", "value": int(value) if float(value).is_integer() else value, "currency": "EUR"}
    return {**money, "scale": scale} if scale > 1 else money


def _money(m: re.Match, _text: str) -> list[dict[str, Any]]:
    """'€1,5 milyon' -> 1500000 (scale 1000000); carpan kelimesi aralikta iki degere de uygulanir."""
    scale = SCALE_LOOKUP[_fold(m.group("x"))] if m.group("x") else 1
    return _range_values(m, lambda v: _scaled_money(v, scale))


def _percent(m: re.Match, _text: str) -> list[dict[str, Any]]:
    return _range_values(m, lambda v: {"kind": "percent", "value": v})


def _age(m: re.Match, _text: str) -> list[dict[str, Any]]:
    return _range_values(m, lambda v: {"kind": "age", "value": v})


def _duration(m: re.Match, _text: str) -> list[dict[str, Any]]:
    unit = next((u for u, rx in UNIT_RX.items() if rx.fullmatch(m.group("u"))), None)
    if unit is None:
        return []
    values = _range_values(m, lambda v: {"kind": "duration", "value": v, "unit": unit})
    if any(isinstance(v["value"], int) and 1900 <= v["value"] <= 2100 for v in values):
        return []  # '2025 yilinda', '2026 aylik', '2026 haftasinda': takvim yilidir, sure degil
    return values


def _phone(m: re.Match, _text: str) -> list[dict[str, Any]]:
    raw = m.group(0).replace("(0)", "").strip()
    digits = re.sub(r"\D", "", raw)
    if raw.startswith("+31"):
        digits = "0" + digits[2:]
    elif raw.startswith("0031"):
        digits = "0" + digits[4:]
    return [{"kind": "phone", "value": digits}]


def _date(m: re.Match, text: str) -> list[dict[str, Any]]:
    day = int(m.group("d"))
    if not 1 <= day <= 31 or claim_places.in_place_name(m, text):
        return []
    value: dict[str, Any] = {"kind": "date", "day": day, "month": MONTH_LOOKUP[_fold(m.group("m"))]}
    if m.group("y"):
        value["year"] = int(m.group("y"))
    return [value]


def _time(m: re.Match, _text: str) -> list[dict[str, Any]]:
    return [{"kind": "time", "value": f"{int(m.group('h')):02d}:{m.group('m')}"}]


def _weekday_ok(m: re.Match, text: str) -> bool:
    day, suffix, ordinal = _fold(m.group("d")), m.group("s"), m.group("o")
    if day in NL_DAYS:
        return NL_DAY_SUFFIX.fullmatch(suffix) is not None
    if TR_DAY_SUFFIX.fullmatch(suffix) is None:
        return False
    if day != "pazar":
        return True
    if ordinal or _fold(suffix) in ("lari", "leri"):
        return True
    return bool(SUNDAY_NEXT.match(text, m.end()) or SUNDAY_PREV.search(text[:m.start()]))


def _weekday(m: re.Match, text: str) -> list[dict[str, Any]]:
    if not _weekday_ok(m, text):
        return []
    value: dict[str, Any] = {"kind": "weekday", "value": DAY_LOOKUP[_fold(m.group("d"))]}
    if m.group("o"):
        value["ordinal"] = ORDINAL_LOOKUP[_fold(m.group("o"))]
    return [value]


def _rx(pattern: str, flags: int = re.IGNORECASE) -> re.Pattern:
    return re.compile(pattern, flags)


_DAY_ALTS = "|".join(sorted(DAYS, key=len, reverse=True))
_MONTH_ALTS = "|".join(sorted(MONTHS, key=len, reverse=True))
_UNIT_ALTS = "|".join(UNIT_PATTERNS.values())
_PHONE = (r"(?<![\d+])(?:(?:\+|00)31[\s-]?(?:\(0\)[\s-]?)?[1-9](?:[\s-]?\d){8}|0[89]0[069][\s-]?\d{4,7}"
          r"|0[1-9](?:[\s-]?\d){8}|14[\s-]?0\d{2,3})(?!\d)")
_SCALE = rf"(?:\s?(?P<x>{alternation(SCALES)})(?!\w))?"

# Sira onemlidir: once eslesen parca sonraki kurallar icin kilitlenir (ör. '€50+KDV' yas degil, '040-2386000' sure degil).
# On ek para yalniz '€'/'EUR' ile: 'Euro 4/5/6' emisyon sinifidir; 'euro' kelimesi yalniz tutardan sonra para sayilir.
RULES: tuple[tuple[str, re.Pattern, Callable[[re.Match, str], list[dict[str, Any]]]], ...] = (
    ("phone", _rx(_PHONE, 0), _phone),
    ("money", _rx(rf"(?:€|\bEUR\b)\s?(?P<a>{NUM})(?:,-)?(?:{DASH}(?:€\s?)?(?P<b>{NUM}))?{_SCALE}"), _money),
    ("money", _rx(rf"(?<![\d.,]){RANGE}{_SCALE}\s?(?:€|\bEUR\b|\beuro|\bavro)"), _money),
    ("percent", _rx(rf"{PREFIX_PCT}\s?(?P<a>{NUM})(?:{DASH}%?\s?(?P<b>{NUM}))?"), _percent),
    ("percent", _rx(rf"(?<![\d.,%]){RANGE}\s?(?:%|\bprocent\b|\bpercent\b)"), _percent),
    ("percent", _rx(rf"\byüzde\s{RANGE}"), _percent),
    ("age", _rx(r"(?<![\d.,])(?P<a>\d{1,3})(?:" + DASH + r"(?P<b>\d{1,3}))?\s?(?:yaş\w*|-?jarig\w*|years?\sold)"), _age),
    ("age", _rx(r"(?<![\d.,])(?P<a>\d{1,2})(?P<b>)\+(?![\d+])(?!\s?" + COUNT_WORDS + ")"), _age),
    ("duration", _rx(rf"(?<![\d.,]){RANGE}\s?(?P<u>{_UNIT_ALTS})"), _duration),
    ("date", _rx(rf"(?<![\d.,])(?P<d>[0-3]?\d)\s(?P<m>{_MONTH_ALTS})(?P<t>\w*)(?:\s(?P<y>(?:19|20)\d{{2}})(?!\d))?"), _date),
    ("time", _rx(r"(?<![\d.,:])(?P<h>[01]?\d|2[0-3])[:.](?P<m>[0-5]\d)(?!\d|[.,]\d)"), _time),
    ("weekday", _rx(rf"(?:\bayın\s(?P<o>ilk|birinci|ikinci|üçüncü|dördüncü|son)\s)?\b(?P<d>{_DAY_ALTS})(?P<s>\w*)"), _weekday),
)


def split_sentences(text: Any) -> list[str]:
    """Satir ve cumle sonu ('.', '!', '?', ';' + bosluk) ile boler; ondalik noktalar bolunmez."""
    if not isinstance(text, str):
        return []
    parts = (piece.strip() for line in text.splitlines() for piece in SENTENCE_END.split(line))
    return [p for p in parts if p]


def extract_values(sentence: str) -> list[dict[str, Any]]:
    """Cumledeki iddialar: [{'kind', 'text', 'values'}], metin sirasiyla. Cakisan parcalar ilk kurala kalir."""
    text = SPACES.sub(" ", sentence)
    taken: list[tuple[int, int]] = []
    found: list[tuple[int, dict[str, Any]]] = []
    for kind, pattern, build in RULES:
        for m in pattern.finditer(text):
            if any(m.start() < end and start < m.end() for start, end in taken):
                continue
            values = build(m, text)
            if not values:
                continue
            taken.append((m.start(), m.end()))
            found.append((m.start(), {"kind": kind, "text": m.group(0).strip(), "values": values}))
    return [claim for _, claim in sorted(found, key=lambda item: item[0])]


def split_ids(value: Any) -> list[str]:
    return [p.strip() for p in re.split(r"[;,\n]", str(value or "")) if p.strip()]


def _topic_ok(record: Mapping[str, Any], topics: set[str] | None) -> bool:
    if topics is None:
        return True
    topic = str(record.get("topic_id") or "")
    return topic in topics or topic.rsplit(":", 1)[-1] in topics


def _record_claims(sheet: str, record: Mapping[str, Any], urls: Mapping[str, str]) -> list[dict[str, Any]]:
    entry_id = str(record.get(ID_KEYS[sheet]) or f"{sheet}!{record.get('_row')}")
    ids = split_ids(record.get("source_ids"))
    sources = [{"source_id": sid, "url": urls.get(sid)} for sid in ids]
    missing = [sid for sid in ids if sid not in urls]
    seen: set[tuple[str, str, str, str]] = set()
    claims: list[dict[str, Any]] = []
    for field in TEXT_FIELDS[sheet]:
        for sentence in split_sentences(record.get(field)):
            for found in extract_values(sentence):
                key = (field, sentence, found["kind"], json.dumps(found["values"], sort_keys=True))
                if key in seen:
                    continue
                seen.add(key)
                claims.append({"claim_id": f"{entry_id}:#{len(claims) + 1}", "entry_id": entry_id, "sheet": sheet,
                               "_row": record.get("_row"), "field": field, "kind": found["kind"], "text": found["text"],
                               "sentence": sentence, "values": found["values"], "source_ids": list(ids),
                               "sources": [dict(s) for s in sources], "missing_source_ids": list(missing),
                               "topic_id": record.get("topic_id"), "reviewed_on": record.get("reviewed_on")})
    return claims


def extract_claims(sheets: Mapping[str, Iterable[Mapping[str, Any]]], topics: set[str] | None = None) -> list[dict[str, Any]]:
    """{sayfa: [kayit]} -> iddia listesi (girdi degismez). Kaynaklar.source_id -> url ile kaynaklar cozulur."""
    urls = {str(r["source_id"]).strip(): str(r["url"]).strip()
            for r in sheets.get("Kaynaklar", []) if r.get("source_id") and r.get("url")}
    claims: list[dict[str, Any]] = []
    for sheet in ("Yanıtlar", "Sözlük"):
        if sheet == "Sözlük" and topics is not None:
            continue
        for record in sheets.get(sheet, []):
            if sheet == "Yanıtlar" and not _topic_ok(record, topics):
                continue
            claims.extend(_record_claims(sheet, record, urls))
    return claims


def summarize(claims: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "claims": len(claims),
        "by_kind": dict(sorted(Counter(c["kind"] for c in claims).items())),
        "by_sheet": dict(sorted(Counter(c["sheet"] for c in claims).items())),
        "entries_with_claims": len({c["entry_id"] for c in claims}),
        "claims_without_source": sum(1 for c in claims if not any(s.get("url") for s in c["sources"])),
        "claims_with_missing_source_ids": sum(1 for c in claims if c["missing_source_ids"]),
    }


def _claim_ok(claim: Any) -> bool:
    """claim_id metin; values {kind: metin} nesneleri; sources {url: metin|None} nesneleri."""
    if not (isinstance(claim, dict) and isinstance(claim.get("claim_id"), str)
            and isinstance(claim.get("values"), list) and isinstance(claim.get("sources"), list)):
        return False
    return (all(isinstance(v, dict) and isinstance(v.get("kind"), str) for v in claim["values"])
            and all(isinstance(s, dict) and isinstance(s.get("url"), (str, type(None))) for s in claim["sources"]))


def read_claims(path: Path) -> list[dict[str, Any]]:
    """claims.jsonl'i okur ve dogrular; UTF-8 olmayan dosya ve bozuk ogeler ClaimError (cikis 2) olur."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        raise ClaimError(f"claims okunamadi: {path} ({exc})") from exc
    claims = []
    for number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            claim = json.loads(line)
        except ValueError as exc:
            raise ClaimError(f"{path}:{number}: gecersiz JSON ({exc})") from exc
        if not _claim_ok(claim):
            raise ClaimError(f"{path}:{number}: claim_id/values/sources eksik ya da hatali")
        claims.append(claim)
    return claims


def load_sheets(xlsx: Path) -> dict[str, list[dict[str, Any]]]:
    """Excel'i salt okur (satir 7 anahtarlari). Yanıtlar ve Kaynaklar zorunlu; Sözlük yoksa bos."""
    try:
        wb = xlsx_dump.open_workbook(xlsx)
    except xlsx_dump.DumpError as exc:
        raise ClaimError(str(exc)) from exc
    try:
        missing = [name for name in REQUIRED_SHEETS if name not in wb.sheetnames]
        if missing:
            raise ClaimError(f"eksik sayfa: {', '.join(missing)}")
        return {name: list(common.iter_records(wb[name])) if name in wb.sheetnames else [] for name in LOADED_SHEETS}
    except ValueError as exc:
        raise ClaimError(str(exc)) from exc
    finally:
        wb.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Kart metinlerinden degisken iddia envanteri (K29/K34/K37/K40).")
    parser.add_argument("xlsx", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="claims.jsonl (iddia basina bir JSON satiri)")
    parser.add_argument("--topics", default=None, help="virgulle topic_id listesi (tam veya son ek)")
    return parser


def main(argv: list[str] | None = None) -> int:
    common.setup_utf8()
    args = build_parser().parse_args(argv)
    topics = {t.strip() for t in args.topics.split(",") if t.strip()} if args.topics else None
    try:
        claims = extract_claims(load_sheets(args.xlsx), topics)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        xlsx_dump.write_jsonl(args.out, claims)
    except (ClaimError, OSError) as exc:
        common.emit({"error": str(exc)})
        return common.EXIT_USAGE
    summary = summarize(claims)
    common.emit({**summary, "out": str(args.out)})
    if summary["claims_without_source"] or summary["claims_with_missing_source_ids"]:
        return common.EXIT_FINDINGS
    return common.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
