"""Hücre değerlerini ve kaynak URL kimliğini tek kuralla çözer."""

import datetime as dt
import json
import math
import re
from urllib.parse import parse_qs, unquote, urlsplit, urlunsplit

ID = re.compile(r"[a-z0-9][a-z0-9:_-]*\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
CC = re.compile(
    r"CC (BY(?:-SA)?) (1\.0|2\.0|2\.5|3\.0|4\.0)(?: ([a-z]{2}))?\Z", re.IGNORECASE
)


def web_url(value):
    try:
        parsed = urlsplit(value)
        return (
            parsed.scheme in ("https", "http")
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
    except (ValueError, TypeError):
        return False


def identity(url):
    parsed = urlsplit(url)
    scheme, host = parsed.scheme.lower(), parsed.netloc.lower()
    path = unquote(parsed.path).replace(" ", "_")
    query = parsed.query
    if host == "commons.wikimedia.org":
        title = parse_qs(query).get("title", [""])[0]
        if path == "/w/index.php" and title.startswith("File:"):
            path = "/wiki/" + title.replace(" ", "_")
        if path.startswith("/wiki/File:"):
            scheme, query = "https", ""
    return urlunsplit((scheme, host, path, query, ""))


def parse_date(value):
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Tarih YYYY-MM-DD olmalı.")
    return dt.date.fromisoformat(value).isoformat()


def parse_number(value, integer=False):
    if isinstance(value, bool):
        raise TypeError("Sayı alanı mantıksal değer olamaz.")
    number = float(value)
    if not math.isfinite(number) or not -1e100 < number < 1e100:
        raise ValueError("Geçerli sonlu sayı gerekli.")
    if integer and not number.is_integer():
        raise ValueError("Tam sayı gerekli.")
    return int(number) if integer else number


def parse_boolean(value):
    if value is True or value == "Evet":
        return True
    if value is False or value == "Hayır":
        return False
    raise ValueError("Evet veya Hayır seçin.")


def parse_object(value):
    data = json.loads(value) if isinstance(value, str) else value
    if not isinstance(data, dict):
        raise TypeError("JSON nesnesi gerekli; { } kullanın.")
    return data


def parse_list(value, separator):
    if not isinstance(value, str):
        raise TypeError("Liste hücresi metin olmalı.")
    pieces = [piece.strip() for piece in value.split(separator) if piece.strip()]
    if len(pieces) != len(set(pieces)):
        raise ValueError("Listede yinelenen değer var.")
    return pieces


def parse_text(value):
    if not isinstance(value, str):
        raise TypeError("Metin alanına metin yazın.")
    return value.strip()


PARSERS = {
    "date": parse_date,
    "number": parse_number,
    "integer": lambda value: parse_number(value, integer=True),
    "boolean": parse_boolean,
    "object": parse_object,
    "id_list": lambda value: parse_list(value, ";"),
    "text_list": lambda value: parse_list(value, "\n"),
}


def parse_value(value, field):
    if value is None or value == "":
        return None
    if isinstance(value, str):
        value = field.get("choice_map", {}).get(value, value)
    return PARSERS.get(field["type"], parse_text)(value)


def normalized_type(value, field):
    kind = field["type"]
    if kind in ("id_list", "text_list"):
        return isinstance(value, list) and all(isinstance(item, str) for item in value)
    if kind == "object":
        return isinstance(value, dict)
    if kind == "boolean":
        return isinstance(value, bool)
    if kind in ("integer", "number"):
        return isinstance(value, (float, int)) and not isinstance(value, bool)
    return isinstance(value, str)


def decode_extra(row):
    value, kind = row.get("value"), row.get("value_type")
    if kind == "JSON":
        return json.loads(value)
    if kind == "Sayı":
        return parse_number(value)
    if kind == "Mantıksal":
        if value in ("true", "Evet"):
            return True
        if value in ("false", "Hayır"):
            return False
        raise ValueError("Mantıksal değer gerekli")
    return value
