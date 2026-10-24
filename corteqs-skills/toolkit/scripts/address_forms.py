"""Okura dogrudan hitap olcumu (B16; standart city-pack intake'te hitap.txt'ye yazilir: Baris karari 23.10.2026 'sen').

Morfolojik cozumleyici yok: kural + kucuk sozluk (address_lexicon.py), yanlis pozitiften kacinacak bicimde.
- Okunmaz: tirnak icindeki alinti, web/e-posta adresi, cumle ortasinda buyuk harfle baslayan kelime (ozel ad,
  Hollandaca/Almanca ad). Kesmeli kelimede (DigiD'niz) yalniz Turkce ek okunur; tireli bilesikte (GFT-bak) emir
  kurallari uygulanmaz; JSON alaninda (visual_json, compare_json) yalniz metin degerleri, her biri ayri yan cumle.
- siz: zamir; sesliden sonra unlu uyumlu -(n)InIz / -sInIz (+hal eki; deniz, henuz, beniz, organize ve n ile biten
  govde + 1. cogul -Iz (eminiz; 'biz' gecen yan cumlede hepsi) disarida); -mAyIn; yan cumle sonunda emir (sozluk;
  sozlukte olmayan en az uc heceli -yIn / ettirgen -DIrIn, ilgi eki ve zaman zarfi listesi disarida).
- sen: zamir; zaman/kip ekinden sonra -sIn/-sAn (-yorsun, -AcAksIn, -mAlIsIn, -mAzsIn, -Ir/-Ar+sIn, -DIysAn ...;
  iki heceli -rsIn ve -DIrsIn 3. tekil emir/ilgi eki, Hollandaca -rsen disarida); govdeyle uyumlu -DIgIn/-AcAgIn
  (gelecegin, plastigin disarida); iyelik + var/yok ('var olan' disarida); -mAn + gerek/icin (ad ve uyumsuz alinti
  disarida); yan cumle sonunda sozlukteki emir kok bicimi (makul alt kume; 3. tekil genis zamanla ayni 'cikar' yok).
- Ad/sifat okumasi da olan emir (yaz, sorun, kalin, koyun, gorus, bak...): cumlenin ilk kelimesi olmayan, virgulden
  hemen sonra gelmeyen (keci, tavsan, koyun) ve onunde belirleyici/sifat/derece zarfi/baglac/mastar/yalin cogul
  olmayan yerde sayilir; Hollandaca 'bak' (kutu) kisaltma ya da Hollandaca kelimeden sonra sayilmaz.
- Cogul 'siz' (sen + es/aile): ayni yan cumlede hepiniz/ikiniz, birlikte/beraber, 'iki ebeveyn', 2. tekil iyelikli
  es/partner (partnerin ve ...), karsilikli eylem/iliski adi (kararlastirmasaniz, iliskiniz); metinde 'sen ve X' ya
  da 'sen dahil' varsa kaydin butun 2. cogul bicimleri. Cogul 'siz' hitaptir ama sen metnini karisik yapmaz.
- Belirsiz bicimler sayilmaz: DigiD'in, pasaportunu, yaninda (2. tekil iyelik mi, ilgi/3. tekil mi ayrilmaz).
- Baglantilar.label (buton metni) kayit bicimine girmez, ayri sayilir (`labels`), bulgu uretmez: sozlesme buton
  etiketini emir olarak ister (Basvur / Randevu al / Bilet al / Haritada ac).
Kayit bicimi: hitapsiz / siz / sen / karisik (ayni kayitta resmi 'siz' ile 'sen').
"""
from __future__ import annotations

import json
import re
from collections import Counter
from typing import Any, Iterable, Iterator, Mapping, NamedTuple

from address_lexicon import (
    ADJ_GIN, AORIST_2SG_SHORT, BACK_VOWELS, BIZ_WORDS, COMPANION, CONJUNCTIONS, COORDINATORS, COPULA_CONDITIONAL,
    COPULA_NOT, DIK_NOUNS, DUTCH_HOMOGRAPHS, DUTCH_PAIRS, EDINMEK_NOUNS, EXISTENTIAL, GENERIC_NOT, GUARDED, HARMONY,
    IMPERATIVES, INFINITIVE, JOINT, LOCATIVE, MAN_NEED, MAN_NOT, N_STEMS_1PL, NOUN_GUARD, PLURAL_NOMINATIVE,
    PLURAL_YOU, POSS_NOT, POSSESSIVE, PREV_REQUIRED, R3SG_DIR, R3SG_NOT, R_VERBS_1SYL, RECIPROCAL, REFLEXIVE,
    RELATION, SEN_AFTER_APOSTROPHE, SEN_AORIST, SEN_PARTICIPLE, SEN_TENSE, SEN_WORDS, SIZ_AFTER_APOSTROPHE,
    SIZ_GENERIC, SIZ_IMPERATIVES, SIZ_NEGATIVE, SIZ_STEMS_NOT, SIZ_SUFFIX, SIZ_WORDS, TOGETHER, TR_ONLY, VERBAL_NOUN,
    VOWELS)

STANDARDS = ("hitapsiz", "siz", "sen", "off")
FORMS = ("hitapsiz", "siz", "sen", "karisik")
MAX_EXAMPLES = 5
# sayfa -> (kayit kimligi, okura gorunen metin alanlari); Mekanlar basligi mekan adidir, okunmaz
ADDRESS_FIELDS: dict[str, tuple[str, tuple[str, ...]]] = {
    "Yanıtlar": ("entry_id", ("title", "subtitle", "summary", "steps", "documents", "timing", "cost", "note",
                              "visual_json")),
    "Mekânlar": ("entry_id", ("subtitle", "summary", "note")),
    "Mahalleler": ("entry_id", ("subtitle", "summary", "note", "tags", "compare_json")),
    "Rotalar": ("route_id", ("title", "note")),
    "Adımlar": ("step_id", ("title", "description", "when")),
    "Konular": ("topic_id", ("title", "description")),
    "Sözlük": ("term_id", ("definition",)),
    "SayfaAlanları": ("field_id", ("value",)),
    "Şehir": ("city_id", ("title", "tagline", "intro")),
    "Fotoğraflar": ("photo_id", ("caption",)),
}
LABEL_SHEET, LABEL_FIELD = "Bağlantılar", "label"  # buton metni: ayri sayilir, kayit bicimine ve bulguya girmez

TOKEN = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*")
BOUNDARY = frozenset(".!?;:\n…")
SPACE = frozenset(" \t\r" + chr(0xA0))  # bosluk, sekme, bolunmez bosluk; yeni satir yan cumle sonudur
MASK = "¤"
QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”|„[^“”\n]*[“”]|«[^»\n]*»'
                    r"|(?<![^\W\d_])['‘’](?:[^'‘’\n]|(?<=[^\W\d_])['’](?=[^\W\d_])){1,300}?['’](?![^\W\d_])")
ADDRESS_LIKE = re.compile(r"(?:https?://|www\.)\S+|[\w.+-]+@[\w-]+\.[\w.]+")


class Marks(NamedTuple):
    siz: tuple[str, ...]
    sen: tuple[str, ...]
    plural: tuple[str, ...] = ()  # yalniz cogul 'siz' baglaminda (ikiniz de ... edin) gecen siz kelimeleri
    joint: bool = False  # metin 'sen ve X' / 'sen dahil' der: butun 2. cogul bicimler cogul 'siz'


class Token(NamedTuple):
    surface: str
    low: str
    word: str  # tireli bilesikte son parca
    suffix: str | None  # kesmeli kelimede kesmeden sonraki ek
    hyphen: bool
    pos: int  # yan cumledeki sira (0 = ilk kelime)
    prev: str  # ayni yan cumlede onceki kelime (kucuk harf)
    prev2: str  # ondan onceki kelime
    final: bool  # yan cumle sonunda mi (noktalama, metin sonu, virgul ya da baglac)
    after_comma: bool  # hemen once virgul var mi (liste ogesi)
    prev_foreign: bool  # onceki kelime atlanan ozel ad/kisaltma ya da eksiz Hollandaca kelime mi


def tr_lower(text: str) -> str:
    return text.replace("I", "ı").replace("İ", "i").lower()


def markers(text: Any) -> Marks:
    """Metindeki 'siz' ve 'sen' isaretleri (metindeki yazilisla, sirali, tekrarsiz); cogul 'siz' ayrica isaretli."""
    found: dict[str, list[str]] = {"siz": [], "sen": []}
    formal: set[str] = set()
    joint = False
    for chunk in _chunks(text):
        clean = ADDRESS_LIKE.sub(MASK, QUOTED.sub(MASK, chunk))
        joint = joint or bool(JOINT.search(tr_lower(clean)))
        for kind, word, plural in _scan(clean):
            found[kind].append(word)
            if kind == "siz" and not plural:
                formal.add(word)
    return _marks(found["siz"], found["sen"], set() if joint else formal, joint)


def _marks(siz: Iterable[str], sen: Iterable[str], formal: set[str], joint: bool = False) -> Marks:
    unique = _unique(siz)
    return Marks(unique, _unique(sen), tuple(word for word in unique if word not in formal), joint)


def form_of(text: Any) -> str:
    return classify(markers(text))


def is_plural_you(word: str) -> bool:
    return tr_lower(word).startswith(PLURAL_YOU)


def classify(marks: Marks) -> str:
    """hitapsiz / siz / sen / karisik; cogul 'siz' baglami (ikiniz de ... edin) sen isaretiyle birlikteyse karisik degil."""
    formal = any(word not in marks.plural for word in marks.siz)
    return _form(formal or (bool(marks.siz) and not marks.sen), bool(marks.sen))


def _form(siz: bool, sen: bool) -> str:
    return "karisik" if siz and sen else "siz" if siz else "sen" if sen else "hitapsiz"


def _unique(words: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(words))


def _chunks(text: Any) -> Iterator[str]:
    """JSON alaninda yalniz metin degerleri (her biri ayri yan cumle); digerinde metnin kendisi."""
    if not isinstance(text, str) or not text.strip():
        return
    if text.lstrip()[0] in "[{":
        try:
            yield from _json_strings(json.loads(text))
            return
        except ValueError:
            pass
    yield text


def _json_strings(node: Any) -> Iterator[str]:
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for value in node.values():
            yield from _json_strings(value)
    elif isinstance(node, list):
        for value in node:
            yield from _json_strings(value)


def _scan(text: str) -> Iterator[tuple[str, str, bool]]:
    """(tur, kelime, cogul baglam) yan cumle yan cumle; cogul ipucu ve 'biz' ayni yan cumlede aranir."""
    tokens = _tokens(text)
    starts = [i for i, tok in enumerate(tokens) if not tok.pos] + [len(tokens)]
    for begin, end in zip(starts, starts[1:]):
        clause = tokens[begin:end]
        plural, biz = _plural_cue(clause), any(tok.low in BIZ_WORDS for tok in clause)
        for i, tok in enumerate(clause):
            nxt, nxt2 = (clause[i + 1:i + 3] + [None, None])[:2]
            for kind in _kinds(tok, nxt, nxt2, biz):
                yield kind, tok.surface, plural or _self_plural(tok.word)


def _plural_cue(clause: list[Token]) -> bool:
    """Cogul hitap ipucu: hepiniz/ikiniz, birlikte/beraber, 'iki ebeveyn', 2. tekil iyelikli es/partner/aile."""
    return any(is_plural_you(tok.low) or tok.low in TOGETHER or COMPANION.match(tok.low)
               or (tok.low.startswith("ebeveyn") and tok.prev == "iki") for tok in clause)


def _self_plural(word: str) -> bool:
    """Karsilikli eylem ya da iliski adi (kararlastirmasaniz, iliskiniz): kelimenin kendisi cogul ozneyi gosterir."""
    return word.startswith(RECIPROCAL) or word.startswith(RELATION)


def _tokens(text: str) -> list[Token]:
    """Kelimeler yan cumle konumuyla; cumle ortasinda buyuk harfle baslayan kelime (ozel ad, kisaltma) okunmaz."""
    out: list[Token] = []
    pos, prev, prev2, foreign, last_end = 0, "", "", False, 0
    for match in TOKEN.finditer(text):
        gap = text[last_end:match.start()]
        if out and any(ch in BOUNDARY for ch in gap):
            pos, prev, prev2, foreign = 0, "", "", False
        surface = match.group()
        low = tr_lower(surface.replace("’", "'"))
        if surface[0].isupper() and pos and "'" not in low:
            pos, prev, prev2, foreign, last_end = pos + 1, low, prev, True, match.end()
            continue
        suffix = low.rsplit("'", 1)[1] if "'" in low else None
        out.append(Token(surface, low, low.rsplit("-", 1)[-1], suffix, "-" in low, pos, prev, prev2,
                         _is_final(text, match.end(), pos), "," in gap, foreign))
        pos, prev, prev2, last_end = pos + 1, low, prev, match.end()
        foreign = suffix is None and _dutch(low)  # 'huisarts'a sorun': Turkce ekli kelime yabanci sayilmaz
    return out


def _is_final(text: str, end: int, pos: int) -> bool:
    """Yan cumle sonu: noktalama ya da metin sonu; virgul ve baglac (ve, veya...) cumlenin ilk kelimesinde sayilmaz."""
    j = _skip(text, end)
    if j >= len(text) or text[j] in BOUNDARY:
        return True
    if not pos:
        return False
    if text[j] == ",":
        return True
    following = TOKEN.match(text, j)
    return bool(following) and tr_lower(following.group()) in CONJUNCTIONS


def _skip(text: str, i: int) -> int:
    """Bosluklari ve aradaki parantezli aciklamayi atlar: 'Randevu al (online).' -> 'al' yan cumle sonunda."""
    while True:
        while i < len(text) and text[i] in SPACE:
            i += 1
        if i < len(text) and text[i] == "(" and (close := text.find(")", i)) != -1:
            i = close + 1
            continue
        return i


def _dutch(word: str) -> bool:
    return any(pair in word for pair in DUTCH_PAIRS)


def _vowels(word: str) -> int:
    return sum(ch in VOWELS for ch in word)


def _last_vowel(text: str) -> str | None:
    return next((ch for ch in reversed(text) if ch in VOWELS), None)


def _kinds(tok: Token, nxt: Token | None, nxt2: Token | None, biz: bool) -> list[str]:
    if tok.suffix is not None:
        if _siz_ending(SIZ_AFTER_APOSTROPHE.search(tok.suffix)):
            return ["siz"]
        return ["sen"] if SEN_AFTER_APOSTROPHE.fullmatch(tok.suffix) else []
    return [kind for kind, hit in (("siz", _is_siz(tok, biz)), ("sen", _is_sen(tok, nxt, nxt2))) if hit]


def _siz_ending(match: re.Match[str] | None) -> bool:
    """-(n)InIz/-sInIz (+hal eki): n'den onceki unlu varsa nIz unlusuyle uyumlu (organize, henuz uyumsuz: disarida)."""
    return bool(match) and (match["v"] is None or HARMONY[match["v"]] == match["w"])


def _imperative_slot(tok: Token) -> bool:
    """Emir yalniz yan cumle sonunda ve tireli bilesik disinda (GFT-bak, kuzey-guneyin) sayilir."""
    return tok.final and not tok.hyphen


def _is_siz(tok: Token, biz: bool) -> bool:
    word = tok.word
    if tok.low in SIZ_WORDS or _siz_suffix(word, biz):
        return True
    if len(word) >= 6 and SIZ_NEGATIVE.search(word):
        return True
    return _imperative_slot(tok) and _siz_imperative(tok)


def _siz_suffix(word: str, biz: bool) -> bool:
    """-(n)InIz/-sInIz (+hal eki); deniz/beniz ve n ile biten govde + 1. cogul -Iz (eminiz, 'biz' cumlesi) degil."""
    match = SIZ_SUFFIX.search(word)
    if not _siz_ending(match) or "deniz" in word or word.startswith(SIZ_STEMS_NOT):
        return False
    return bool(match["case"]) or not (word[:-2] in N_STEMS_1PL or biz)


def _reflexive_2sg(low: str, prev: str) -> bool:
    """'edin'/'bulun' 2. tekil emir mi: bilgi edin (edinmek), hazir bulun, talepte bulun (bulunmak)."""
    if low == "edin":
        return prev in EDINMEK_NOUNS
    return prev == "hazır" or prev.endswith(LOCATIVE)


def _siz_imperative(tok: Token) -> bool:
    low = tok.low
    if low in REFLEXIVE:
        return not _reflexive_2sg(low, tok.prev)
    if low in SIZ_IMPERATIVES:
        return _unguarded(tok)
    return _generic_siz(tok)


def _generic_siz(tok: Token) -> bool:
    """Sozlukte olmayan -yIn / ettirgen -DIrIn: en az uc hece; ilgi eki (mudurun) ve zaman zarfi (sabahleyin) degil."""
    low = tok.low
    return (bool(SIZ_GENERIC.search(low)) and _vowels(low) >= 3 and low not in GENERIC_NOT
            and tok.prev not in NOUN_GUARD)


def _is_sen(tok: Token, nxt: Token | None, nxt2: Token | None) -> bool:
    word = tok.word
    if tok.low in SEN_WORDS or _sen_suffix(word) or _copula_conditional(word):
        return True
    if nxt is not None and not tok.hyphen and _sen_before(word, nxt.low, nxt2.low if nxt2 else ""):
        return True
    return _imperative_slot(tok) and _sen_imperative(tok)


def _sen_suffix(word: str) -> bool:
    """Zaman/kip eki + 2. tekil -sIn/-sAn; genis zaman (-Ir/-Ar+sIn) ve -DIgIn/-AcAgIn ayrica sinanir."""
    if word in R3SG_NOT:
        return False
    if SEN_TENSE.search(word):
        return True
    if aorist := SEN_AORIST.search(word):
        return _aorist_2sg(word, aorist["v"])
    participle = SEN_PARTICIPLE.search(word)
    return bool(participle) and _participle_2sg(word, participle)


def _aorist_2sg(word: str, vowel: str) -> bool:
    """-Ir/-Ar + sIn/sAn: iki heceli -rsIn (versin, bursun, dersin) ve -DIrsIn (degerlendirsin) 3. tekil emir ya da
    ilgi eki; iki heceli -rsAn yalniz tek heceli fiilde (versen, dersen; kersen degil); Hollandaca harf cifti degil."""
    vowels = _vowels(word)
    if vowel in "ae":
        return (word[:-3] in R_VERBS_1SYL if vowels == 2 else vowels > 2) and not _dutch(word)
    if vowels <= 2:
        return word in AORIST_2SG_SHORT
    return not R3SG_DIR.search(word)


def _participle_2sg(word: str, match: re.Match[str]) -> bool:
    """-DIgIn/-AcAgIn: ek govdeyle uyumlu (plastigin, butigin alinti ad) ve govde -DIk/-AcAk adi degil (gelecegin)."""
    last = _last_vowel(word[:match.start()])
    if last is None:
        return False
    harmonic = HARMONY[last] == match["i"] if match["i"] else (last in BACK_VOWELS) == (match["a"] == "a")
    return harmonic and word[:-3] + "k" not in DIK_NOUNS


def _copula_conditional(word: str) -> bool:
    """Ad + -sAn (degilsen, gencsen, issizsen): govdede Turkceye ozgu harf; Hollandaca/Almanca -ssen, -tsen disarida."""
    match = COPULA_CONDITIONAL.search(word)
    stem = word[:match.start()] if match else ""
    return len(stem) >= 2 and not stem.endswith("s") and bool(TR_ONLY & set(stem)) and word not in COPULA_NOT


def _sen_before(word: str, following: str, after: str) -> bool:
    """Iyelik + var/yok (hakkin varsa; 'var olan' degil), -mAn + gerek/icin (basvurman gerekir)."""
    if following in EXISTENTIAL:
        return _possessive_2sg(word) and not (following in ("var", "yok") and after == "olan")
    return (following.startswith(MAN_NEED) or following == "için") and _verbal_noun_2sg(word)


def _possessive_2sg(word: str) -> bool:
    """Unsuzle biten ad + -In (hakkin, cocugun): sik ad/sifat (izin, sabun, sakin) ve -gIn sifati (yorgun) degil."""
    return len(word) >= 4 and bool(POSSESSIVE.search(word)) and word not in POSS_NOT and not ADJ_GIN.search(word)


def _verbal_noun_2sg(word: str) -> bool:
    """-mAn eylem adi (kurman, gitmen): ad (zaman, secmen) ve govdeyle uyumsuz alinti (examen, Musluman) degil."""
    last = _last_vowel(word[:-3])
    return (len(word) >= 5 and bool(VERBAL_NOUN.search(word)) and word not in MAN_NOT and last is not None
            and (last in BACK_VOWELS) == (word[-2] == "a"))


def _sen_imperative(tok: Token) -> bool:
    low = tok.low
    if low in REFLEXIVE:
        return _reflexive_2sg(low, tok.prev)
    if low not in IMPERATIVES:
        return False
    needed = PREV_REQUIRED.get(low)
    return tok.prev in needed if needed is not None else _unguarded(tok)


def _unguarded(tok: Token) -> bool:
    """Ad/sifat okumasi da olan emir (yaz, sorun, kalin): ilk kelime degil, virgulden hemen sonra gelmeyen (liste
    ogesi) ve onunde belirleyici/sifat/baglac/mastar/yalin cogul olmayan yerde sayilir."""
    if tok.low not in GUARDED:
        return True
    return tok.pos > 0 and not tok.after_comma and not _noun_context(tok)


def _noun_context(tok: Token) -> bool:
    prev = tok.prev
    return (prev in NOUN_GUARD or prev in COORDINATORS or (prev in ("da", "de") and tok.prev2 == "ya")
            or prev.endswith(INFINITIVE) or bool(PLURAL_NOMINATIVE.search(prev))
            or (tok.prev_foreign and tok.low in DUTCH_HOMOGRAPHS))


# --- kayit duzeyi rapor -----------------------------------------------------------------------------------

def address_report(sheets: Mapping[str, list[Mapping[str, Any]]], standard: str = "off",
                   skipped: Mapping[str, str] | None = None) -> dict[str, Any]:
    """Kayit basina hitap bicimi; standart disi ve karisik kayitlar bulgu (off: yalniz olcum). Girdi degismez.
    skipped: okunamadigi icin olculmeyen sayfa -> hata (text_quality yukler); raporda 'skipped' olarak listelenir."""
    if standard not in STANDARDS:
        raise ValueError(f"bilinmeyen hitap standardi: {standard!r} (gecerli: {', '.join(STANDARDS)})")
    records = [_record(sheet, rec) for sheet in ADDRESS_FIELDS for rec in sheets.get(sheet, [])]
    items = [rec for rec in records if rec["form"] != "hitapsiz"]
    findings = [{**rec, "reason": "karisik" if rec["form"] == "karisik" else "standart_disi"}
                for rec in items if _violates(rec["form"], standard)]
    counts = Counter(rec["form"] for rec in records)
    return {"standard": standard, "records": len(records), **{form: counts[form] for form in FORMS},
            "by_sheet": _by_sheet(records, sheets), "labels": _label_forms(sheets.get(LABEL_SHEET, [])),
            "skipped": [{"sheet": sheet, "error": error} for sheet, error in (skipped or {}).items()],
            "findings": findings, "items": items}


def address_summary(report: Mapping[str, Any]) -> dict[str, Any]:
    return {"standard": report["standard"], "records": report["records"], **{f: report[f] for f in FORMS},
            "findings": len(report["findings"]), "labels": dict(report["labels"]),
            "skipped": [entry["sheet"] for entry in report["skipped"]]}


def _record(sheet: str, rec: Mapping[str, Any]) -> dict[str, Any]:
    id_key, fields = ADDRESS_FIELDS[sheet]
    per_field = {field: markers(rec.get(field)) for field in fields}
    if any(marks.joint for marks in per_field.values()):  # bir alanda 'sen ve X': kaydin butun 2. cogullari cogul
        per_field = {field: marks._replace(plural=marks.siz) for field, marks in per_field.items()}
    formal = {word for marks in per_field.values() for word in marks.siz if word not in marks.plural}
    combined = _marks((w for m in per_field.values() for w in m.siz), (w for m in per_field.values() for w in m.sen),
                      formal)
    return {"sheet": sheet, "row": rec.get("_row"), "id": rec.get(id_key) or rec.get("entry_id"),
            "form": classify(combined), "fields": {f: classify(m) for f, m in per_field.items() if m.siz or m.sen},
            "siz": list(combined.siz[:MAX_EXAMPLES]), "sen": list(combined.sen[:MAX_EXAMPLES])}


def _label_forms(links: Iterable[Mapping[str, Any]]) -> dict[str, int]:
    """Buton metni (Baglantilar.label) kayit bicimine girmez: sozlesme etiketi emir ister; ayri sayilir, bulgu degil."""
    forms = Counter(form_of(link.get(LABEL_FIELD)) for link in links)
    return {"records": sum(forms.values()), **{form: forms[form] for form in FORMS}}


def _violates(form: str, standard: str) -> bool:
    if standard == "off" or form == "hitapsiz":
        return False
    return form == "karisik" or standard == "hitapsiz" or form != standard


def _by_sheet(records: list[dict[str, Any]], sheets: Mapping[str, Any]) -> dict[str, dict[str, int]]:
    out = {}
    for sheet in (s for s in ADDRESS_FIELDS if s in sheets):
        forms = Counter(rec["form"] for rec in records if rec["sheet"] == sheet)
        out[sheet] = {"records": sum(forms.values()), **{form: forms[form] for form in FORMS}}
    return out
