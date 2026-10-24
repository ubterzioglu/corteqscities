"""İçerik, kaynak ve ek alan bağlarını doğrular."""

from .delivery_values import decode_extra, identity, web_url

ENTRY_TABLES = ("answers", "places", "neighborhoods")
RESERVED_PAGE = {
    "routes",
    "glossary",
    "directory",
    "currency",
    "currency_symbol",
    "currency_label",
    "reviewed_on",
    "weather",
}
OWNED_DETAILS = {
    "coordinates",
    "visual",
    "compare",
    "tags",
    "group",
    "district",
    "setting",
    "collection",
    "location",
    "media_key",
    "note",
    "steps",
    "documents",
    "timing",
    "cost",
    "status",
    "actions",
}


def check_common_links(context):
    city_id = context.first("city").get("city_id")
    for table in context.data:
        for row in context.rows(table):
            check_row_links(context, table, row, city_id)


def check_row_links(context, table, row, city_id):
    if row.get("city_id") != city_id:
        context.error(table, row, "Şehir kimliği Şehir sayfasıyla eşleşmiyor.")
    for source in row.get("source_ids") or []:
        if source not in context.indices["sources"]:
            context.error(table, row, f"Kaynak kimliği bulunamadı: {source}")


def check_entry(context, table, row, titles):
    entry_id = row.get("entry_id")
    title = str(row.get("title", "")).casefold().strip()
    if entry_id in context.entries:
        context.error(
            table, row, f"Başka kart türünde aynı içerik kimliği var: {entry_id}"
        )
    context.entries[entry_id] = row
    if title in titles:
        context.error(table, row, "Başka kartla yinelenen başlık.")
    titles.add(title)
    if entry_id != f"{context.first('city').get('city_id')}:{row.get('slug')}":
        context.error(table, row, "İçerik kimliği şehir:adres-adı biçiminde olmalı.")
    if table == "answers" and row.get("topic_id") not in context.indices["topics"]:
        context.error(table, row, "Konu kimliği bulunamadı.")
    if (row.get("latitude") is None) != (row.get("longitude") is None):
        context.error(table, row, "Enlem ve boylam birlikte doldurulmalı.")


def check_entries(context):
    titles = set()
    for table in ENTRY_TABLES:
        for row in context.rows(table):
            check_entry(context, table, row, titles)
    city_id = context.first("city").get("city_id")
    for row in context.rows("topics"):
        if row.get("topic_id") != f"{city_id}:{row.get('slug')}":
            context.error(
                "topics", row, "Konu kimliği şehir:konu-adı biçiminde olmalı."
            )


def check_orders(context):
    for table in ("journey_steps", "routes", "glossary", "topics"):
        orders = set()
        for row in context.rows(table):
            order = row.get("order")
            if order in orders:
                context.error(table, row, "Aynı sayfada sıra numarası yineleniyor.")
            orders.add(order)


def check_sources(context):
    urls = set()
    for row in context.rows("sources"):
        if web_url(row.get("url")):
            url = identity(row["url"])
            if url in urls:
                context.error(
                    "sources", row, "Aynı URL için birden çok kaynak kimliği var."
                )
            urls.add(url)
        if context.ready and row.get("verified") is not True:
            context.error("sources", row, "Kaynak incelemesi tamamlanmalı.")
        context.file_check("sources", row, "snapshot_file", "snapshot_sha256")


def check_linked_row(context, table, row):
    if row.get("entry_id") not in context.entries:
        context.error(table, row, "Bağlı içerik kimliği bulunamadı.")
    for entry_id in row.get("stop_entry_ids") or []:
        if entry_id not in context.entries:
            context.error(table, row, f"Rota durak kimliği bulunamadı: {entry_id}")


def check_linked_tables(context):
    for table in ("actions", "routes", "journey_steps", "entry_details"):
        for row in context.rows(table):
            check_linked_row(context, table, row)
    pairs = set()
    for row in context.rows("entry_details"):
        pair = (row.get("entry_id"), row.get("key"))
        if pair in pairs:
            context.error(
                "entry_details", row, "Aynı kartın ek alanı birden çok kez tanımlanmış."
            )
        pairs.add(pair)


def check_extra_values(context):
    for table in ("page_fields", "entry_details"):
        for row in context.rows(table):
            try:
                decode_extra(row)
            except (ValueError, TypeError, OverflowError):
                context.error(
                    table, row, "Alan değeri seçilen veri türüne uygun değil."
                )


def check_extra_keys(context):
    keys = set()
    for row in context.rows("page_fields"):
        key = row.get("key")
        if key in RESERVED_PAGE:
            context.error(
                "page_fields", row, "Bu alan ayrı giriş sayfası tarafından yönetilir."
            )
        if key in keys:
            context.error("page_fields", row, "Yinelenen sayfa anahtarı.")
        keys.add(key)
    for row in context.rows("entry_details"):
        if row.get("key") in OWNED_DETAILS:
            context.error(
                "entry_details",
                row,
                "Bu detay anahtarı ana kart veya Bağlantılar sayfasında doldurulur.",
            )


def check_entry_requirements(context, table, row, actions, photos):
    entry_id = row.get("entry_id")
    if entry_id not in actions:
        context.review_issue(table, row, "Doğrudan işlem / kurum bağlantısı eksik.")
    if table != "answers" and not row.get("collection") and entry_id not in photos:
        context.review_issue(
            table, row, "Mekân / mahalleye bağlı gerçek fotoğraf eksik."
        )


def check_entry_completeness(context):
    actions = {row.get("entry_id") for row in context.rows("actions")}
    photos = {
        row.get("entry_id")
        for row in context.rows("photos")
        if row.get("completion_credit") is True
    }
    for table in ENTRY_TABLES:
        for row in context.rows(table):
            check_entry_requirements(context, table, row, actions, photos)


def check_graph(context):
    check_common_links(context)
    check_entries(context)
    check_orders(context)
    check_sources(context)
    check_linked_tables(context)
    check_extra_values(context)
    check_extra_keys(context)
