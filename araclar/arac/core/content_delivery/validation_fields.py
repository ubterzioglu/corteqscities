"""Teslim alanları, türler ve kimliklerin temel kontrolleri."""

import datetime as dt
import math
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .delivery_values import ID, SHA, normalized_type, web_url
from .schema_definition import SCHEMA


def normalize_rows(table, rows, errors):
    config = SCHEMA["tables"][table]
    if not isinstance(rows, list):
        errors.append(f"{config['sheet']}: satırlar liste olmalı.")
        return []
    result = []
    for row in rows:
        if not isinstance(row, dict):
            errors.append(f"{config['sheet']}: satır nesne olmalı.")
            continue
        result.append(normalize_record(table, row, errors))
    return result


def normalized_field_value(config, row, key, value, fields, errors):
    location = f"{config['sheet']}!{row.get('_row', '?')}"
    if key not in fields:
        errors.append(f"{location}: tanımsız alan: {key}")
        return value
    if value is not None and not normalized_type(value, fields[key]):
        errors.append(f"{location}: {fields[key]['label']} veri türü uygun değil.")
        return None
    return value


def normalize_record(table, row, errors):
    config = SCHEMA["tables"][table]
    fields = {field["key"]: field for field in config["fields"]}
    result = dict(row)
    for key, value in row.items():
        if not isinstance(key, str):
            errors.append(f"{config['sheet']}: alan anahtarları metin olmalı.")
            continue
        if not key.startswith("_"):
            result[key] = normalized_field_value(
                config, row, key, value, fields, errors
            )
    return result


def normalized_input(data, errors):
    if not isinstance(data, dict):
        errors.append("Teslim tabloları nesne olmalı.")
        data = {}
    for key in set(data) - set(SCHEMA["tables"]):
        errors.append(f"Tanımsız tablo: {key}")
    return {
        key: normalize_rows(key, data.get(key, []), errors) for key in SCHEMA["tables"]
    }


def check_choices(context, table, row, field, value):
    if not field.get("choices") or field["type"] == "boolean":
        return
    choices = (
        list(field["choice_map"].values())
        if field.get("choice_map")
        else field["choices"]
    )
    values = value if field["type"] == "id_list" else [value]
    if any(item not in choices for item in values):
        context.error(table, row, f"{field['label']} tanımsız seçim içeriyor.")


def check_date(context, table, row, field, value):
    try:
        valid_format = re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)
        if not valid_format:
            raise ValueError("Tarih biçimi")
        if dt.date.fromisoformat(value) > context.today:
            context.error(table, row, f"{field['label']} gelecekte olamaz.")
    except (ValueError, TypeError):
        context.error(table, row, f"{field['label']} geçerli tarih olmalı.")


def check_number(context, table, row, field, value):
    if not -1e100 < value < 1e100 or not math.isfinite(value):
        context.error(table, row, f"{field['label']} geçerli sonlu sayı olmalı.")
        return
    if field["type"] == "integer" and not float(value).is_integer():
        context.error(table, row, f"{field['label']} tam sayı olmalı.")
    if "minimum" in field and value < field["minimum"]:
        context.error(table, row, f"{field['label']} alt sınırın altında.")
    if "maximum" in field and value > field["maximum"]:
        context.error(table, row, f"{field['label']} üst sınırın üstünde.")


def check_string(context, table, row, field, value):
    key, label = field["key"], field["label"]
    if field.get("max_length") and len(str(value)) > field["max_length"]:
        context.error(table, row, f"{label} en çok {field['max_length']} karakter.")
    if key.endswith("_id") and value and not ID.fullmatch(value):
        context.error(
            table, row, f"{label} yalnız küçük ASCII harf, sayı, -, _ ve : içermeli."
        )
    if key.endswith("sha256") and value and not SHA.fullmatch(value):
        context.error(table, row, f"{label} 64 küçük onaltılık karakter olmalı.")


def check_field(context, table, row, field):
    if field.get("readonly"):
        return
    value = row.get(field["key"])
    if field["required"] and value in (None, "", []):
        context.error(table, row, f"{field['label']} zorunlu.")
        return
    if value is None:
        return
    check_choices(context, table, row, field, value)
    kind = field["type"]
    if kind == "date":
        check_date(context, table, row, field, value)
    if kind in ("number", "integer"):
        check_number(context, table, row, field, value)
    if kind == "url" and not web_url(value):
        context.error(
            table,
            row,
            f"{field['label']} http/https adresi olmalı; kullanıcı/şifre içeremez.",
        )
    check_string(context, table, row, field, value)


def index_row(context, table, row, key):
    value = row.get(key)
    index = context.indices[table]
    if value in index:
        context.error(table, row, f"Yinelenen kimlik: {value}")
    elif value:
        index[value] = row
    if (
        context.ready
        and "editorial_status" in row
        and row.get("editorial_status") != "Onaylandı"
    ):
        context.error(
            table, row, "Editör durumu Onaylandı olmalı; insan incelemesi gerekli."
        )


def check_tables(context):
    for table, config in SCHEMA["tables"].items():
        rows = context.rows(table)
        context.indices[table] = {}
        if table in ("city", "metadata") and len(rows) != 1:
            context.errors.append(f"{config['sheet']}: tam bir satır gerekli.")
        check_table_rows(context, table, config, rows)


def check_table_rows(context, table, config, rows):
    key = config["fields"][0]["key"]
    for row in rows:
        for field in config["fields"]:
            check_field(context, table, row, field)
        index_row(context, table, row, key)


def check_metadata(context):
    meta = context.first("metadata")
    if meta.get("schema_version") != SCHEMA["schema_version"]:
        context.errors.append("Teslimat: desteklenmeyen şema sürümü.")
    if context.ready and meta.get("scope") != "Tam teslim":
        context.errors.append("Kısmi örnek tam teslim olarak dışa aktarılamaz.")
    if context.ready and not meta.get("reviewer"):
        context.errors.append("Teslimat: insan inceleyen adı gerekli.")


def check_city(context):
    city = context.first("city")
    try:
        ZoneInfo(city.get("timezone") or "")
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        context.errors.append("Şehir: geçerli IANA saat dilimi gerekli.")
    if not re.fullmatch(r"[A-Z]{2,3}", city.get("country_code") or ""):
        context.errors.append("Şehir: ülke kodu 2–3 büyük ASCII harf olmalı.")
    if not re.fullmatch(r"[A-Z]{3}", city.get("currency") or ""):
        context.errors.append("Şehir: para birimi 3 büyük ASCII harf olmalı.")
    if (city.get("latitude") is None) != (city.get("longitude") is None):
        context.error("city", city, "Enlem ve boylam birlikte doldurulmalı.")
