"""Adetlerden bağımsız olarak gerçek şehir ekranlarının veri gereksinimleri."""

import re
from urllib.parse import urlsplit

from .delivery_values import decode_extra, web_url

BUDGET_KEYS = (
    "income",
    "rent",
    "bills",
    "food",
    "transport",
    "health",
    "leisure",
    "other",
    "deposit",
    "moving",
)
GROUP_KEYS = ("museum", "art", "stage", "sport", "nature", "family", "food", "history")
TEXT_KEYS = (
    "hero_kicker",
    "hero_accent",
    "hero_note",
    "topic_title",
    "topic_intro",
    "journey_title",
    "journey_intro",
    "neighborhood_title",
    "neighborhood_intro",
    "explore_title",
    "explore_intro",
    "sources_note",
    "photo_credit",
    "arrival_note",
)
ARRAY_FIELDS = {
    "facts": (4, ("value", "label", "entry")),
    "quick_links": (3, ("label", "entry")),
    "timeline": (4, ("title", "note", "offset")),
    "budget_fields": (10, ("key", "label")),
    "place_groups": (8, ("key", "label")),
    "emergency": (1, ("tel", "number", "label", "desc")),
}
URL_KEYS = ("emergency_url", "pharmacy_url")


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def public_link(value):
    return web_url(value) and "." in urlsplit(value).hostname


def problem(context, message):
    context.review_issue("page_fields", {}, message)


def values_for(context):
    values = {}
    for row in context.rows("page_fields"):
        try:
            values[row.get("key")] = decode_extra(row)
        except (ValueError, TypeError, OverflowError):
            continue
    return values


def object_list(context, values, key, minimum, fields):
    value = values.get(key)
    if not isinstance(value, list) or len(value) < minimum:
        problem(context, f"{key}: en az {minimum} yapılandırılmış kayıt gerekli.")
        return []
    return [row for row in value if object_valid(context, key, row, fields)]


def object_valid(context, key, row, fields):
    if not isinstance(row, dict) or not all(field in row for field in fields):
        context.error("page_fields", {}, f"{key}: gerekli alanlar {', '.join(fields)}.")
        return False
    text_fields = (field for field in fields if field != "offset")
    if any(not nonempty(row[field]) for field in text_fields):
        context.error("page_fields", {}, f"{key}: metin alanları dolu olmalı.")
        return False
    return True


def check_reference(context, slug, label, allowed):
    if not isinstance(slug, str) or slug not in allowed:
        problem(context, f"{label}: bağlı içerik bu şehirde bulunamadı.")


def check_key_set(context, rows, expected, label):
    keys = [row["key"] for row in rows]
    if len(set(keys)) != len(keys) or set(keys) != set(expected):
        problem(
            context,
            f"{label}: anahtarlar birer kez ve eksiksiz olmalı: {', '.join(expected)}.",
        )


def check_timeline(context, rows):
    slugs = {row.get("slug") for row in context.entries.values()}
    for row in rows:
        if "entry" in row:
            check_reference(context, row["entry"], "timeline", slugs)
        offset = row["offset"]
        if type(offset) is not int or not -730 <= offset <= 730:
            context.error(
                "page_fields",
                {},
                "timeline.offset: -730 ile 730 arasında tam gün gerekli.",
            )


def check_page_data(context):
    values = values_for(context)
    for key in TEXT_KEYS:
        if not nonempty(values.get(key)):
            problem(context, f"{key}: Türkçe sayfa metni eksik.")
    for key in URL_KEYS:
        if not public_link(values.get(key)):
            problem(context, f"{key}: bu ülkeye ait resmî bağlantı gerekli.")
    rows = {
        key: object_list(context, values, key, *spec)
        for key, spec in ARRAY_FIELDS.items()
    }
    slugs = {row.get("slug") for row in context.entries.values()}
    for key in ("facts", "quick_links"):
        for row in rows[key]:
            check_reference(context, row["entry"], key, slugs)
    check_reference(context, values.get("advice_entry"), "advice_entry", slugs)
    check_key_set(context, rows["budget_fields"], BUDGET_KEYS, "budget_fields")
    check_key_set(context, rows["place_groups"], GROUP_KEYS, "place_groups")
    check_timeline(context, rows["timeline"])
    for row in rows["emergency"]:
        if not re.fullmatch(r"\+?[0-9*#]{2,20}", row["tel"]):
            context.error(
                "page_fields", {}, "emergency.tel: geçerli arama numarası gerekli."
            )


def check_routes(context):
    places = set(context.indices["places"])
    for row in context.rows("routes"):
        check_route(context, row, places)


def check_route(context, row, places):
    stops, names = row.get("stop_entry_ids") or [], row.get("stops") or []
    if not 2 <= len(stops) <= 8 or len(stops) != len(set(stops)):
        context.review_issue("routes", row, "Rotada 2–8 farklı mekân kimliği gerekli.")
    if len(names) != len(stops) or any(stop not in places for stop in stops):
        context.review_issue(
            "routes", row, "Durak adları ve mekân kimlikleri aynı sırada eşleşmeli."
        )
    if stops and row.get("entry_id") != stops[0]:
        context.review_issue("routes", row, "Ana kart rotanın ilk durağı olmalı.")


def check_neighborhoods(context):
    for row in context.rows("neighborhoods"):
        compare = row.get("compare_json")
        if not isinstance(compare, dict) or len(compare) < 4:
            context.review_issue(
                "neighborhoods", row, "En az 4 mahalle karşılaştırma alanı gerekli."
            )
        elif not all(nonempty(k) and nonempty(v) for k, v in compare.items()):
            context.error(
                "neighborhoods",
                row,
                "Karşılaştırma başlık ve değerleri dolu metin olmalı.",
            )


def check_web_contract(context):
    check_page_data(context)
    check_routes(context)
    check_neighborhoods(context)
    if len(context.rows("journey_steps")) < 4:
        context.review_issue("journey_steps", {}, "En az 4 yerleşim adımı gerekli.")
    groups = {
        row.get("group") for row in context.rows("places") if not row.get("collection")
    }
    if groups != set(GROUP_KEYS):
        problem(context, "Sekiz keşif grubunun her birinde gerçek mekân gerekli.")
    for key in ("currency_symbol", "currency_label", "forecast_label"):
        if not nonempty(context.first("city").get(key)):
            context.review_issue("city", context.first("city"), f"{key}: zorunlu.")
    for key in ("forecast_url", "provider_url"):
        if not public_link(context.first("city").get(key)):
            context.review_issue(
                "city", context.first("city"), f"{key}: bağlantı gerekli."
            )
