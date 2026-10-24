"""Kaynak sayfa snapshot'i (K76, T09): ham yanit <sha256>.html, ana metin <sha256>.txt, index.jsonl.

Kullanim: fetch_snapshot.py (--urls urls.txt | --xlsx X [--sheets ...]) --out-dir D [--cache-dir C] [--max-urls N]
          [--retry-transient]  (onbellekteki 429/5xx/ag hatalarini yeniden indirir; yoksa onbellek, deterministik)
          [--must-contain kanit.jsonl]  (satir: {"url": ..., "must_contain": ["ifade", ...]}; ek alanlar serbest)
Dosya adi = icerigin sha256'si (ad, hash'in kendisidir; kanit kendini dogrular). Metin html.parser ile cikarilir
(script/style/nav/footer/noscript/head haric, bosluk normalize). 500 karakterden kisa metin = 'thin_text' (JS kabugu).
Baslikta ya da metnin ilk 1500 karakterinde 'sayfa yok' isareti = 'soft_404'; isaret satirin soft_404 alanina yazilir.
soft_404_signal url_check K51 kuralinin ust kumesidir (K51 ifadelerinin hepsini, bilesik kelimede de yakalar; testli);
url_check henuz kendi kopyasini kullaniyor (takip: page_signals bu fonksiyonu kullanmali).
--must-contain: ifadeler temiz metinde aranir (NFKC, bosluk, buyuk-kucuk harf, tirnak/tire bicimi farki yok sayilir);
satira evidence={needed, found, missing} yazilir, eksik ifade varsa 'evidence_missing'. Ifade verilmeyen satirda null.
Bu calismada indirilmeyen ama index'te olan url'nin kaniti kayitli metinden (hash'i tutan) hesaplanir; ne listede ne
index'te olan must-contain adresi 'must_contain_unmatched' sayilir (yazim farki kaniti sessizce atlatmasin).
Ifade verilmeden yeniden indirilen url'de eski kanit kalir: metin ayniysa gecerli, degistiyse 'evidence_stale'.
index.jsonl url'ye gore BIRLESTIRILIR: bu calismanin satiri eskisini yerinde gunceller, yeni url sona eklenir, digerleri
korunur; okunamayan mevcut index (bozuk JSON, url'siz satir, '<sha256>.<uzanti>' olmayan dosya adi) kullanim hatasidir
ve dosyaya dokunulmaz. Index yazmadan hemen once yeniden okunur (ayni klasore es zamanli calismanin satirlari korunur;
ayni url'de son yazan kazanir); yazim surece ozel gecici dosya + yer degistirme ile. Satirlar yalniz '\\n' ile ayrilir
(U+2028/U+2029/U+0085 ve eslenmemis vekil karakter kacislanir).
index.jsonl satiri: {url, final_url, status, fetched_on, html_file, html_sha256, text_file, text_sha256, text_chars,
title, content_type, flags, error, soft_404, evidence}. Iddia defteri {url -> text_file} eslemesini load_index() ile kurar.
Ozet (stdout, tek satir JSON) bu calismanin satirlarini sayar (kanit sayilarina evidence_from_index dahil);
index_rows/index_kept birlesmis index'i anlatir.
Cikis: 0 temiz, 1 bulgu (fetch_failed, thin_text, soft_404, evidence_missing, evidence_stale, must_contain_unmatched),
2 kullanim.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import sys
import time
import unicodedata
import zipfile
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence

from common import EXIT_FINDINGS, EXIT_OK, EXIT_USAGE, emit, setup_utf8
from url_check import DEFAULT_SHEETS, collect_relations
from web_fetch import MAX_BODY_BYTES, FetchResult, Fetcher, Transport, urllib_transport, utc_today

BODY_LIMIT = MAX_BODY_BYTES
THIN_TEXT_CHARS = 500
INDEX_NAME = "index.jsonl"
RAW_EXTENSIONS = {"application/pdf": ".pdf", "application/json": ".json", "text/plain": ".txt", "application/xml": ".xml",
                  "text/xml": ".xml"}
FINDING_FLAGS = ("fetch_failed", "thin_text", "soft_404", "evidence_missing", "evidence_stale")
EVIDENCE_FLAGS = ("evidence_missing", "evidence_stale")
SNAPSHOT_NAME = re.compile(r"[0-9a-f]{64}\.[a-z0-9]{1,8}")  # icerik adresi: ayrac/'..' yok, klasor disini gosteremez
SURROGATE = re.compile("[\ud800-\udfff]")  # eslenmemis vekil: JSON kacisiyla gelir, UTF-8'e yazilamaz
JSONL_UNSAFE = re.compile("[\x85\u2028\u2029\ud800-\udfff]")  # splitlines'in boldugu + yazilamayan karakterler


# ---------------------------------------------------------------- JSONL okuma/yazma

def _jsonl_lines(path: Path) -> Iterator[tuple[int, str]]:
    """Bos olmayan (satir no, satir) ciftleri. Yalniz '\\n' ile bolunur: str.splitlines U+2028/U+2029/U+0085'te de
    boler ve bu karakterleri kacissiz tasiyan gecerli bir JSON satirini ikiye keserdi."""
    lines = Path(path).read_text(encoding="utf-8-sig").split("\n")
    return ((number, line.rstrip("\r")) for number, line in enumerate(lines, start=1) if line.strip())


def _jsonl_line(row: dict[str, Any]) -> str:
    """Tek satir JSON (UTF-8 okunur kalir); JSONL_UNSAFE karakterleri JSON kacisiyla yazilir (ayni deger)."""
    text = json.dumps(row, ensure_ascii=False, sort_keys=True)
    return JSONL_UNSAFE.sub(lambda match: f"\\u{ord(match.group()):04x}", text) + "\n"


# ---------------------------------------------------------------- eslestirme bicimi (kanit + soft-404)

INVISIBLE = re.compile("[\u00ad\u200b-\u200f\u2060-\u2064\ufeff]")  # yumusak tire, sifir genislik, yon isaretleri
TYPOGRAPHY = str.maketrans({"\u2018": "'", "\u2019": "'", "\u201a": "'", "\u201b": "'", "\u201c": '"', "\u201d": '"',
                            "\u201e": '"', "\u201f": '"', "\u2010": "-", "\u2011": "-", "\u2012": "-", "\u2013": "-",
                            "\u2014": "-", "\u2015": "-", "\u2212": "-"})


def normalize_for_match(text: str) -> str:
    """NFKC, gorunmez karakterler atilir, tirnak/tire tek bicim, bosluklar tek, casefold ('İ' -> 'i')."""
    visible = INVISIBLE.sub("", unicodedata.normalize("NFKC", text)).translate(TYPOGRAPHY)
    return " ".join(visible.split()).casefold().replace("\u0307", "")


# ---------------------------------------------------------------- soft-404 (url_check K51 kuralinin ust kumesi)

SOFT_404_WINDOW = 1500  # "govdenin basi": ana metnin ilk karakterleri (nav/header/footer zaten atilmis)
_PAGE_GONE = (r"(?:does not|doesn't|did not|no longer) (?:seem to )?exist|bestaat (?:helaas )?niet"
              r"|existiert (?:leider )?nicht|(?:could not|cannot|can't|couldn't) be found")
_OTHER_CLAUSE = (r"(?:if|unless|when|whether|that|which|who|whose|what|where|als|indien|wanneer|dat|die|wat|waar"
                 r"|welke|wie|wenn|falls|eğer)\b")
# 'sayfa' ile 'yok' arasinda yalniz ziyaretciye donen kisa yan cumle ("you are looking for", "die u zoekt",
# ", die Sie suchen,") ya da 'helaas/leider' olabilir; kosullu ya da baska ozneli cumle ("page explains what to do
# if your business no longer exists") eslesmez. Sayfa kelimesinin basinda \b yok: webpagina, homepage, Webseite.
_VISITOR_CLAUSE = (r"(?:,? (?:that |which |die |dat |waar |welke |welche )?(?:you're|you|u|je|jij|sie|du)"
                   rf"(?: (?!{_OTHER_CLAUSE})[^\s.!?,]+){{0,6}},?)?(?: (?:unfortunately|sadly|helaas|leider))?")
SOFT_404_PHRASE = re.compile(r"not found|niet gevonden|nicht gefunden|sayfa bulunamad|kon niet worden gevonden"
                             rf"|(?:page|pagina|seite|sayfa)\b{_VISITOR_CLAUSE} (?:{_PAGE_GONE})")
TITLE_404 = re.compile(r"\b404\b")
BODY_404 = re.compile(r"^404\b|\b(?:error|fout(?:code|melding)?|fehler(?:code)?)\s*:?\s*404\b")


def soft_404_signal(title: str | None, text: str | None) -> str | None:
    """200 yanitinda 'sayfa yok' isareti: baslikta ifade veya 404; metnin basinda ifade, 'error/fout/fehler 404'
    ya da 404 ile baslama. Doner: isaretin yeri ve eslesen metin (ornek "gövde: 'niet gevonden'") | None."""
    head = normalize_for_match(title or "")
    body = normalize_for_match((text or "")[:SOFT_404_WINDOW])
    for where, haystack, number in (("başlık", head, TITLE_404), ("gövde", body, BODY_404)):
        match = SOFT_404_PHRASE.search(haystack) or number.search(haystack)
        if match:
            return f"{where}: '{match.group(0)}'"
    return None


# ---------------------------------------------------------------- --must-contain kaniti

def check_evidence(text: str | None, phrases: Sequence[str]) -> dict[str, Any]:
    """Ifadeler temiz metinde mi: {needed, found, missing}; metin yoksa (indirilemedi / HTML degil) hepsi eksik."""
    haystack = normalize_for_match(text or "")
    missing = [phrase for phrase in phrases if normalize_for_match(phrase) not in haystack]
    return {"needed": len(phrases), "found": len(phrases) - len(missing), "missing": missing}


def _evidence_item(item: Any, where: str) -> tuple[str, list[str]]:
    if not isinstance(item, dict) or not isinstance(item.get("url"), str) or not item["url"].strip():
        raise ValueError(f"{where}: 'url' metni olan bir JSON nesnesi olmali")
    phrases = item.get("must_contain")
    if not isinstance(phrases, list) or not all(isinstance(p, str) and normalize_for_match(p) for p in phrases):
        raise ValueError(f"{where}: 'must_contain' bos olmayan metinlerden olusan bir liste olmali ([] serbest)")
    if any(SURROGATE.search(text) for text in (item["url"], *phrases)):
        raise ValueError(f"{where}: eslenmemis vekil karakter (or. '\\ud800'): JSON kacisi bozuk, metin UTF-8 degil")
    return item["url"].strip(), [phrase.strip() for phrase in phrases]


def _unique_phrases(phrases: Iterable[str]) -> list[str]:
    """Eslestirme bicimi ayni olan ifadeler bir kez sayilir (ilk yazilisi ve sirasi kalir)."""
    first: dict[str, str] = {}
    for phrase in phrases:
        first.setdefault(normalize_for_match(phrase), phrase)
    return list(first.values())


def read_must_contain(path: Path) -> dict[str, list[str]]:
    """JSONL -> {url: ifadeler}. Ayni url'nin satirlari birlesir; ifadeler eslestirme bicimine gore tekillesir.
    Bicim hatasi ValueError ('<dosya>:<satir>: ...'); hicbir indirme baslamadan once yukselir."""
    path = Path(path)
    expected: dict[str, list[str]] = {}
    for number, line in _jsonl_lines(path):
        where = f"{path.name}:{number}"
        try:
            item = json.loads(line)
        except ValueError as error:
            raise ValueError(f"{where}: gecersiz JSON ({error})") from error
        url, phrases = _evidence_item(item, where)
        expected[url] = _unique_phrases([*expected.get(url, []), *phrases])
    return expected


# ---------------------------------------------------------------- HTML cozumleme (url_check da kullanir)

SKIP_TAGS = frozenset({"script", "style", "nav", "footer", "noscript", "template", "svg", "head", "iframe"})
CONTENT_TAGS = frozenset({"main", "article"})
BLOCK_TAGS = frozenset({"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "td", "th",
                        "section", "article", "main", "table", "blockquote", "dd", "dt", "figcaption", "pre", "header"})
META_CHARSET = re.compile(rb"<meta[^>]+charset=[\"']?([A-Za-z0-9_\-:.]+)", re.IGNORECASE)
HEADER_CHARSET = re.compile(r"charset=[\"']?([A-Za-z0-9_\-:.]+)", re.IGNORECASE)
WHITESPACE = re.compile(r"\s+")


class _PageParser(HTMLParser):
    """Baslik + ana metin; script/style/nav/footer/noscript/head ve main/article disindaki header atlanir."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self._skip = 0
        self._content = 0
        self._headers: list[bool] = []
        self._in_title = False
        self._title_done = False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "title" and not self._title_done:
            self._in_title = True
        if tag in CONTENT_TAGS:
            self._content += 1
        skip = tag in SKIP_TAGS or (tag == "header" and self._content == 0)
        if tag == "header":
            self._headers.append(skip)
        if skip:
            self._skip += 1
        if tag in BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag == "title" and self._in_title:
            self._in_title, self._title_done = False, True
        if tag in CONTENT_TAGS and self._content:
            self._content -= 1
        skipped = tag in SKIP_TAGS or (tag == "header" and self._headers and self._headers.pop())
        if skipped and self._skip:
            self._skip -= 1
        if tag in BLOCK_TAGS:
            self.text_parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title_parts.append(data)
        elif not self._skip:
            self.text_parts.append(WHITESPACE.sub(" ", data))  # kaynak satir sonu metin satiri degildir


def _squash(text: str) -> str:
    return " ".join(text.split())


def extract_page(html: str) -> tuple[str, str]:
    """(baslik, ana metin). Metin satirlari bosluk-normalize, bos satirlar atilir."""
    parser = _PageParser()
    parser.feed(html)
    parser.close()
    lines = (_squash(line) for line in "".join(parser.text_parts).split("\n"))
    return _squash("".join(parser.title_parts)), "\n".join(line for line in lines if line)


def decode_body(body: bytes, content_type: str = "") -> str:
    """Content-Type charset -> <meta charset> -> UTF-8 (hatali bayt yer tutucuyla)."""
    if body.startswith(b"\xef\xbb\xbf"):
        return body[3:].decode("utf-8", errors="replace")
    header = HEADER_CHARSET.search(content_type or "")
    meta = META_CHARSET.search(body[:4096])
    for charset in (header.group(1) if header else None, meta.group(1).decode("ascii") if meta else None):
        if charset:
            try:
                return body.decode(charset, errors="replace")
            except LookupError:
                continue
    return body.decode("utf-8", errors="replace")


def is_html(content_type: str, body: bytes = b"") -> bool:
    if content_type:
        return "html" in content_type.lower()
    return body.lstrip()[:15].lower().startswith((b"<!doctype html", b"<html"))


def read_url_list(path: Path) -> list[str]:
    """Satir basina bir URL; bos satir ve '#' yorumlari atlanir; tekrarlar ilk sirasiyla tekillesir."""
    lines = (line.strip() for line in Path(path).read_text(encoding="utf-8-sig").splitlines())
    return list(dict.fromkeys(line for line in lines if line and not line.startswith("#")))


def urls_from_xlsx(path: Path, sheets: list[str]) -> list[str]:
    return list(dict.fromkeys(rel["url"].strip() for rel in collect_relations(path, sheets)))


def _write_once(path: Path, data: bytes) -> None:
    """Icerik adresli dosya: ayni ad ayni icerik demektir; varsa yeniden yazilmaz."""
    if not path.exists():
        path.write_bytes(data)


def _base_row(result: FetchResult) -> dict[str, Any]:
    return {"url": result.url, "final_url": result.final_url, "status": result.status, "fetched_on": result.fetched_on,
            "html_file": None, "html_sha256": None, "text_file": None, "text_sha256": None, "text_chars": 0,
            "title": None, "content_type": result.content_type.split(";")[0].strip().lower() or None,
            "flags": [], "error": f"{result.error_kind}: {result.error}" if result.error_kind else None,
            "soft_404": None, "evidence": None}


def _save_text(row: dict[str, Any], result: FetchResult, out_dir: Path) -> tuple[dict[str, Any], str]:
    title, text = extract_page(decode_body(result.body, result.content_type))
    data = text.encode("utf-8")
    sha = hashlib.sha256(data).hexdigest()
    _write_once(out_dir / f"{sha}.txt", data)
    signal = soft_404_signal(title, text)
    flags = row["flags"] + (["thin_text"] if len(text) < THIN_TEXT_CHARS else []) + (["soft_404"] if signal else [])
    return {**row, "text_file": f"{sha}.txt", "text_sha256": sha, "text_chars": len(text), "title": title or None,
            "flags": flags, "soft_404": signal}, text


def _snapshot(result: FetchResult, out_dir: Path) -> tuple[dict[str, Any], str | None]:
    """(index satiri, temiz metin | None); 2xx govde varsa ham dosya (+ HTML ise metin) yazilir."""
    row = _base_row(result)
    if result.error_kind or not (200 <= (result.status or 0) < 300) or not result.body:
        return {**row, "flags": ["fetch_failed"]}, None
    html = is_html(result.content_type, result.body)
    sha = hashlib.sha256(result.body).hexdigest()
    ext = ".html" if html else RAW_EXTENSIONS.get(row["content_type"] or "", ".bin")
    _write_once(out_dir / f"{sha}{ext}", result.body)
    row = {**row, "html_file": f"{sha}{ext}", "html_sha256": sha, "flags": ["truncated"] if result.truncated else []}
    if not html:
        return {**row, "flags": row["flags"] + ["non_html"]}, None
    return _save_text(row, result, out_dir)


def _with_evidence(row: dict[str, Any], evidence: dict[str, Any], stale: bool = False) -> dict[str, Any]:
    """Satirin kaniti yenilenir: eski kanit bayraklari atilir, 'evidence_stale' ya da eksik varsa 'evidence_missing'."""
    flags = [flag for flag in row.get("flags") or [] if flag not in EVIDENCE_FLAGS]
    extra = ["evidence_stale"] if stale else (["evidence_missing"] if evidence.get("missing") else [])
    return {**row, "evidence": evidence, "flags": flags + extra}


def snapshot_row(result: FetchResult, out_dir: Path, must_contain: Sequence[str] | None = None) -> dict[str, Any]:
    """Tek URL'nin index satiri; must_contain verildiyse (bos liste dahil) kanit temiz metinde aranir."""
    row, text = _snapshot(result, out_dir)
    return row if must_contain is None else _with_evidence(row, check_evidence(text, must_contain))


def carry_evidence(row: dict[str, Any], old: dict[str, Any] | None) -> dict[str, Any]:
    """Ifade verilmeden yeniden indirilen url: eski kanit metin ayniysa gecerlidir (tasinir), degistiyse 'evidence_stale'
    ile kalir (--must-contain ile yeniden denetlenmeli). Onceki bulgu sessizce kaybolmaz."""
    old = old or {}
    evidence = old.get("evidence")
    if row["evidence"] is not None or not isinstance(evidence, dict):
        return row
    return _with_evidence(row, evidence, stale=old.get("text_sha256") != row["text_sha256"])


def _saved_text(out_dir: Path, row: dict[str, Any]) -> str | None:
    """Index satirinin kayitli temiz metni; yoksa, okunamazsa ya da adindaki hash'i tutmazsa None (kanit 'eksik')."""
    name = row.get("text_file")  # read_index_rows dogruladi: '<sha256>.<uzanti>'
    if not name:
        return None
    try:
        data = (out_dir / name).read_bytes()
    except OSError:
        return None
    if hashlib.sha256(data).hexdigest() != name.partition(".")[0]:
        return None
    return data.decode("utf-8", errors="replace")


def recheck_kept(kept: dict[str, dict[str, Any]], expected: dict[str, list[str]], fetched: set[str],
                 out_dir: Path) -> list[dict[str, Any]]:
    """Bu calismada indirilmeyen ama index'te olan must-contain url'leri: kanit kayitli metinden hesaplanir."""
    return [_with_evidence(kept[url], check_evidence(_saved_text(out_dir, kept[url]), phrases))
            for url, phrases in expected.items() if url in kept and url not in fetched]


def _check_snapshot_names(row: dict[str, Any], where: str) -> None:
    """html_file/text_file yalniz '<sha256>.<uzanti>' (ya da null): index'teki ad klasor disini gosteremez."""
    for key in ("html_file", "text_file"):
        name = row.get(key)
        if name is not None and not (isinstance(name, str) and SNAPSHOT_NAME.fullmatch(name)):
            raise ValueError(f"{where}: '{key}' '<sha256>.<uzanti>' olmali ({name!r}); dosyaya dokunulmadi")


def read_index_rows(path: Path) -> list[dict[str, Any]]:
    """Mevcut index.jsonl satirlari (dosya yoksa bos). Bozuk satir ValueError: index ezilmez, once duzeltilir."""
    path = Path(path)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for number, line in _jsonl_lines(path):
        where = f"{path}:{number}"
        try:
            row = json.loads(line)
        except ValueError as error:
            raise ValueError(f"{where}: mevcut index okunamadi ({error}); dosyaya dokunulmadi") from error
        if not isinstance(row, dict) or not isinstance(row.get("url"), str):
            raise ValueError(f"{where}: mevcut index satirinda 'url' yok; dosyaya dokunulmadi")
        _check_snapshot_names(row, where)
        rows.append(row)
    return rows


def merge_index(previous: Iterable[dict[str, Any]], fresh: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """url'ye gore birlestirir: yeni satir eskisini yerinde gunceller, yeni url sona eklenir, digerleri korunur.
    Eski index'te ayni url birden cok kez varsa ilk konumunda son satiri kalir."""
    kept = {row["url"]: row for row in previous}
    return list({**kept, **{row["url"]: row for row in fresh}}.values())


def write_index(path: Path, rows: list[dict[str, Any]]) -> None:
    """Surece ozel gecici dosyaya yazip yer degistirir: yarida kesilen ya da es zamanli yazim mevcut index'i bozmaz."""
    path = Path(path)
    temporary = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text("".join(_jsonl_line(row) for row in rows), encoding="utf-8")
        os.replace(temporary, path)
    finally:
        with contextlib.suppress(OSError):  # yarim gecici dosya kalmasin; asil hata (varsa) yukari gider
            temporary.unlink(missing_ok=True)


def load_index(path: Path) -> dict[str, Path]:
    """index.jsonl -> {url: metin dosyasinin tam yolu}; metni olmayan satirlar atlanir. Index yoksa OSError; bozuk
    satir ya da '<sha256>.<uzanti>' olmayan dosya adi ValueError (klasor disindaki dosya cozulmez)."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"index bulunamadi: {path}")
    return {row["url"]: path.parent / row["text_file"] for row in read_index_rows(path) if row.get("text_file")}


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Kaynak sayfa snapshot'i: ham HTML + ana metin + index.jsonl")
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument("--urls", type=Path, help="satir basina bir URL")
    source.add_argument("--xlsx", type=Path, help="Excel (Kaynaklar/Bağlantılar URL'leri)")
    p.add_argument("--sheets", default=",".join(DEFAULT_SHEETS))
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--cache-dir", type=Path)
    p.add_argument("--max-urls", type=int)
    p.add_argument("--retry-transient", action="store_true",
                   help="onbellekteki 429/5xx/ag-TLS hatalarini yeniden indir (basarili ve 404 yanitlar onbellekten)")
    p.add_argument("--must-contain", type=Path,
                   help='JSONL: {"url": ..., "must_contain": ["ifade", ...]}; ifadeler temiz metinde aranir')
    return p


def _load_urls(args: argparse.Namespace) -> list[str]:
    if args.urls is not None:
        return read_url_list(args.urls)
    return urls_from_xlsx(args.xlsx, [s.strip() for s in args.sheets.split(",") if s.strip()])


def _summary(rows: list[dict[str, Any]], rechecked: list[dict[str, Any]], urls: list[str], index_rows: int,
             unmatched: int) -> dict[str, Any]:
    """Bu calismanin sayilari; status yalniz bu calismanin bulgularina bakar (korunan eski satirlar sayilmaz).
    Index'ten yeniden denetlenen satirlarin (rechecked) yalniz kanit sonucu sayilir, eski indirme bayraklari degil."""
    fresh = {flag: sum(1 for r in rows if flag in r["flags"]) for flag in (*FINDING_FLAGS, "non_html", "truncated")}
    counts = {flag: n + sum(1 for r in rechecked if flag in EVIDENCE_FLAGS and flag in r["flags"])
              for flag, n in fresh.items()}
    findings = unmatched or any(counts[flag] for flag in FINDING_FLAGS)
    checked = sum(1 for r in (*rows, *rechecked) if r["evidence"] is not None and "evidence_stale" not in r["flags"])
    return {"status": "findings" if findings else "ok", "urls": len(urls), "fetched": len(rows),
            "saved": sum(1 for r in rows if r["html_file"]), "failed": counts["fetch_failed"],
            "thin_text": counts["thin_text"], "soft_404": counts["soft_404"], "evidence_checked": checked,
            "evidence_missing": counts["evidence_missing"], "evidence_stale": counts["evidence_stale"],
            "evidence_from_index": len(rechecked), "must_contain_unmatched": unmatched,
            "non_html": counts["non_html"], "truncated": counts["truncated"], "skipped": len(urls) - len(rows),
            "index_rows": index_rows, "index_kept": index_rows - len(rows)}


def main(argv: list[str] | None = None, transport: Transport = urllib_transport,
         sleep: Callable[[float], None] = time.sleep, clock: Callable[[], str] = utc_today) -> int:
    setup_utf8()
    try:
        args = _parser().parse_args(argv)
        urls = _load_urls(args)
        expected = read_must_contain(args.must_contain) if args.must_contain is not None else {}
        previous = read_index_rows(args.out_dir / INDEX_NAME)  # indirmeden once: bozuksa ag isi baslamaz
    except SystemExit as stop:
        return EXIT_USAGE if stop.code else EXIT_OK
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        print(f"HATA: {error}", file=sys.stderr)
        return EXIT_USAGE
    if args.max_urls is not None and args.max_urls < 1:
        print("HATA: --max-urls en az 1 olmali", file=sys.stderr)
        return EXIT_USAGE
    selected = urls[:args.max_urls] if args.max_urls else urls
    args.out_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher(transport, args.cache_dir or args.out_dir / ".http-cache", sleep=sleep, clock=clock,
                      refresh_transient=args.retry_transient)
    results = fetcher.fetch_many(selected, mode="get", body_limit=BODY_LIMIT)
    kept = {row["url"]: row for row in previous}
    rows = [carry_evidence(snapshot_row(results[url], args.out_dir, expected.get(url)), kept.get(url))
            for url in selected]
    rechecked = recheck_kept(kept, expected, set(selected), args.out_dir)
    try:  # indirme dakikalar surebilir: index yazmadan hemen once yeniden okunur (es zamanli calismanin satirlari)
        merged = merge_index(read_index_rows(args.out_dir / INDEX_NAME), [*rechecked, *rows])
        write_index(args.out_dir / INDEX_NAME, merged)
    except (OSError, ValueError) as error:  # yakalanmazsa cikis 1 olur ve 'bulgu' ile karisir
        print(f"HATA: index yazilamadi ({error}); onceki index yerinde", file=sys.stderr)
        return EXIT_USAGE
    summary = _summary(rows, rechecked, urls, len(merged), unmatched=len(set(expected) - set(urls) - set(kept)))
    emit({**summary, "requests_made": fetcher.requests_made, "cache_hits": fetcher.cache_hits,
          "retry_transient": args.retry_transient, "index": str(args.out_dir / INDEX_NAME)})
    return EXIT_FINDINGS if summary["status"] == "findings" else EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
