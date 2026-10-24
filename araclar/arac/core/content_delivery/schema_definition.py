"""İçerik ekibi teslim sözleşmesi; uygulama veya veritabanı bağımlılığı yoktur."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "output/content-team/template/rev-20261012-01"
SCHEMA_VERSION = "1.0"
STATUS = ["Taslak", "İnceleme", "Düzeltme", "Onaylandı"]
YES_NO = ["Evet", "Hayır"]
ENTRY_LABEL = "İçerik kimliği"
CITY_LABEL = "Şehir kimliği"
SOURCES_LABEL = "Kaynak kimlikleri"


def field(key, label, type="string", required=False, **kwargs):
    return {"key": key, "label": label, "type": type, "required": required, **kwargs}


def string_field(key, label, required=False, **kwargs):
    return field(key, label, required=required, **kwargs)


def date_field(key, label, required=False):
    return field(key, label, "date", required, not_future=True)


def integer_field(key, label, required=False):
    return field(key, label, "integer", required, minimum=0)


def object_field(key, label, required=False):
    return field(key, label, "object", required)


def id_list_field(key, label, required=False, **kwargs):
    return field(key, label, "id_list", required, separator=";", **kwargs)


def text_list_field(key, label, required=False):
    return field(key, label, "text_list", required, separator="newline")


def boolean_field(key, label, required=False):
    return field(key, label, "boolean", required, choices=YES_NO)


def url_field(key, label, required=False):
    return field(key, label, "url", required)


def status():
    return string_field("editorial_status", "Editör durumu", True, choices=STATUS)


def choice(key, label, mapping, required=True):
    return string_field(key, label, required, choices=list(mapping), choice_map=mapping)


COMMON = [
    string_field("entry_id", ENTRY_LABEL, True),
    string_field("city_id", CITY_LABEL, True),
    string_field("slug", "Adres adı", True, max_length=120),
    string_field("title", "Başlık", True, max_length=180),
    string_field("subtitle", "Alt başlık", max_length=160),
    string_field("summary", "Türkçe kısa yanıt / özet", True),
    string_field("keywords", "Arama sözcükleri"),
    id_list_field("stages", "Yaşam aşamaları", choices=["before", "planning", "new", "settled"]),
    id_list_field("source_ids", SOURCES_LABEL, True),
    date_field("reviewed_on", "İçerik kontrol tarihi", True),
    integer_field("order", "Sıra", True),
    boolean_field("featured", "Öne çıkar", True),
    status(),
]

TABLES = {
    "metadata": {
        "sheet": "Teslimat",
        "title": "Teslimat bilgileri",
        "capacity": 1,
        "fields": [
            string_field("schema_version", "Şema sürümü", True),
            string_field("delivery_id", "Teslimat kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("editor", "Hazırlayan", True),
            string_field("reviewer", "İnceleyen"),
            string_field("scope", "Dosya kapsamı", True, choices=["Tam teslim", "Kısmi örnek"]),
            date_field("updated_on", "Dosya güncelleme tarihi", True),
            status(),
            string_field("notes", "Teslim notu"),
        ],
    },
    "city": {
        "sheet": "Şehir",
        "title": "Şehir profili",
        "capacity": 1,
        "fields": [
            string_field("city_id", CITY_LABEL, True),
            string_field("name", "Şehir adı", True, max_length=100),
            string_field("country", "Ülke", True, max_length=100),
            string_field("country_code", "Ülke kodu", True, max_length=3),
            string_field(
                "region",
                "Dünya bölgesi",
                True,
                choices=["EU", "AS", "AF", "NA", "SA", "OC"],
            ),
            string_field(
                "kind",
                "Coğrafi kapsam",
                True,
                choices=["city", "region", "island", "country"],
            ),
            string_field("title", "Rehber başlığı", True, max_length=160),
            string_field("intro", "Rehber giriş metni", True, max_length=350),
            string_field("currency", "Para birimi kodu", True),
            string_field("currency_symbol", "Para simgesi"),
            string_field("currency_label", "Para birimi adı"),
            string_field("language", "Yerel dil", True),
            string_field("timezone", "Saat dilimi", True),
            field("latitude", "Enlem", "number", True, minimum=-90, maximum=90),
            field("longitude", "Boylam", "number", True, minimum=-180, maximum=180),
            url_field("coordinate_source_url", "Konum kaynağı", True),
            date_field("coordinate_checked_on", "Konum kontrol tarihi", True),
            string_field("coordinate_note", "Konum açıklaması"),
            url_field("source_url", "Kapsam kaynağı", True),
            date_field("source_checked_on", "Kapsam kontrol tarihi", True),
            integer_field("source_position", "Katalog sıra numarası", True),
            date_field("reviewed_on", "Rehber kontrol tarihi", True),
            integer_field("priority", "Öncelik", True),
            string_field("aliases", "Diğer adlar"),
            string_field("locality", "Yerel ad"),
            string_field("tagline", "Şehir cümlesi"),
            integer_field("directory_order", "Şehir dizini sırası"),
            url_field("forecast_url", "Hava tahmini bağlantısı"),
            url_field("provider_url", "Hava veri sağlayıcısı"),
            string_field("forecast_label", "Tahmin bağlantı metni"),
            string_field("hero_photo_id", "Ana kapak kimliği"),
            string_field("editorial_notes", "Editoryal şehir notları"),
            status(),
        ],
    },
    "topics": {
        "sheet": "Konular",
        "title": "Pratik yaşam konuları",
        "capacity": 30,
        "fields": [
            string_field("topic_id", "Konu kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("slug", "Konu adres adı", True),
            string_field("title", "Konu başlığı", True, max_length=100),
            string_field("description", "Açıklama", True, max_length=180),
            string_field("icon", "Simge anahtarı", True),
            integer_field("order", "Sıra", True),
            field("used_count", "Yanıt içeren konu (hesap)", "integer", readonly=True),
        ],
    },
    "answers": {
        "sheet": "Yanıtlar",
        "title": "Pratik yaşam yanıtları",
        "capacity": 300,
        "fields": COMMON
        + [
            string_field("topic_id", "Konu kimliği", True),
            text_list_field("steps", "İşlem adımları", True),
            text_list_field("documents", "Gereken belgeler"),
            string_field("timing", "Süre / son tarih"),
            string_field("cost", "Ücret / maliyet"),
            string_field("note", "İstisna ve dikkat notu"),
            object_field("visual_json", "Görsel açıklama yapısı (JSON)"),
        ],
    },
    "places": {
        "sheet": "Mekânlar",
        "title": "Keşif noktaları",
        "capacity": 180,
        "fields": COMMON
        + [
            choice(
                "group",
                "Keşif grubu",
                {
                    "Müzeler": "museum",
                    "Sanat ve sergiler": "art",
                    "Sahne ve müzik": "stage",
                    "Spor": "sport",
                    "Doğa ve açık hava": "nature",
                    "Çocuklarla keşif": "family",
                    "Yeme ve içme": "food",
                    "Tarih ve mimari": "history",
                },
            ),
            string_field("district", "Mahalle / ilçe", True),
            choice(
                "setting",
                "Ortam",
                {"Kapalı alan": "indoor", "Açık hava": "outdoor", "Karma": "mixed"},
            ),
            string_field("location", "Adres / konum", True),
            field("latitude", "Enlem", "number", minimum=-90, maximum=90),
            field("longitude", "Boylam", "number", minimum=-180, maximum=180),
            string_field("visit_status", "Ziyaret durumu"),
            string_field("note", "Ziyaret notu"),
            boolean_field("collection", "Derleme / dizin", True),
            string_field("media_key", "Medya eşleştirme anahtarı"),
        ],
    },
    "neighborhoods": {
        "sheet": "Mahalleler",
        "title": "Mahalle ve yerel bölge",
        "capacity": 40,
        "fields": COMMON
        + [
            string_field("location", "Yer / konum", True),
            text_list_field("tags", "Öne çıkan özellikler"),
            object_field("compare_json", "Karşılaştırma alanları (JSON)"),
            string_field("note", "Yaşam ve ev seçimi notu"),
            string_field("media_key", "Medya eşleştirme anahtarı"),
        ],
    },
    "actions": {
        "sheet": "Bağlantılar",
        "title": "Doğrudan kurum ve işlem bağlantıları",
        "capacity": 800,
        "fields": [
            string_field("action_id", "Bağlantı kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("entry_id", ENTRY_LABEL, True),
            string_field("label", "Bağlantı metni", True),
            url_field("url", "Doğrudan bağlantı", True),
            date_field("checked_on", "Bağlantı kontrol tarihi", True),
            integer_field("order", "Sıra", True),
        ],
    },
    "routes": {
        "sheet": "Rotalar",
        "title": "Keşif rotaları",
        "capacity": 30,
        "fields": [
            string_field("route_id", "Rota kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("title", "Rota başlığı", True),
            string_field("tag", "Süre / rota türü", True),
            text_list_field("stops", "Sıralı durak adları", True),
            id_list_field("stop_entry_ids", "Sıralı durak içerik kimlikleri"),
            string_field("entry_id", "Ana kart kimliği", True),
            string_field("note", "Rota ve erişim notu", True),
            date_field("reviewed_on", "Rota kontrol tarihi", True),
            id_list_field("source_ids", SOURCES_LABEL, True),
            integer_field("order", "Sıra", True),
            status(),
        ],
    },
    "glossary": {
        "sheet": "Sözlük",
        "title": "Yerel terimler sözlüğü",
        "capacity": 100,
        "fields": [
            string_field("term_id", "Terim kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("term", "Yerel terim", True),
            string_field("definition", "Türkçe açıklama", True),
            id_list_field("source_ids", SOURCES_LABEL, True),
            date_field("reviewed_on", "Terim kontrol tarihi", True),
            integer_field("order", "Sıra", True),
            status(),
        ],
    },
    "journey_steps": {
        "sheet": "Adımlar",
        "title": "Yerleşim yol haritası",
        "capacity": 40,
        "fields": [
            string_field("step_id", "Adım kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("entry_id", ENTRY_LABEL, True),
            string_field("title", "Adım başlığı", True, max_length=120),
            string_field("when", "Ne zaman", True, max_length=90),
            string_field("description", "Adım açıklaması", True, max_length=250),
            integer_field("order", "Sıra", True),
        ],
    },
    "sources": {
        "sheet": "Kaynaklar",
        "title": "Birincil bilgi kaynakları",
        "capacity": 500,
        "fields": [
            string_field("source_id", "Kaynak kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("title", "Kaynak başlığı", True, max_length=180),
            string_field("publisher", "Yayıncı / kurum", True, max_length=120),
            url_field("url", "Kaynak bağlantısı", True),
            date_field("checked_on", "Kaynak kontrol tarihi", True),
            string_field("topic", "Araştırma konusu"),
            string_field("summary", "Türkçe araştırma notu"),
            boolean_field("verified", "Kaynak notu incelendi", True),
            string_field("snapshot_file", "Varsa kaynak kanıt dosyası"),
            string_field("snapshot_sha256", "Varsa kanıt SHA-256"),
        ],
    },
    "photos": {
        "sheet": "Fotoğraflar",
        "title": "Gerçek fotoğraf teslimi",
        "capacity": 350,
        "fields": [
            string_field("photo_id", "Fotoğraf kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("role", "Kullanım", True, choices=["Mekân", "Kapak"]),
            string_field("entry_id", "Mekân / mahalle kimliği"),
            string_field("file", "Görsel dosyası", True),
            string_field("sha256", "Görsel SHA-256", True),
            string_field("caption", "Türkçe açıklama", True, max_length=250),
            string_field("author", "Fotoğrafçı / atıf", True),
            string_field("license", "Ücretsiz ticari lisans", True),
            url_field("license_url", "Lisans bağlantısı", True),
            url_field("source_url", "Fotoğraf kaynak sayfası", True),
            date_field("capture_date", "Varsa çekim tarihi"),
            date_field("source_checked_on", "Hak / kaynak kontrol tarihi", True),
            string_field("modifications", "Yapılan değişiklikler", True),
            string_field("evidence_id", "Kanıt kimliği", True),
            boolean_field("completion_credit", "Sayımda kullanılabilir", True),
            integer_field("order", "Galeri sırası", True),
            status(),
            field(
                "unique_venue_count",
                "Farklı mekân fotoğrafı (hesap)",
                "integer",
                readonly=True,
            ),
            field(
                "unique_hero_count",
                "Farklı kapak fotoğrafı (hesap)",
                "integer",
                readonly=True,
            ),
        ],
    },
    "evidence": {
        "sheet": "Kanıtlar",
        "title": "Fotoğraf kaynak ve hak kanıtı",
        "capacity": 350,
        "fields": [
            string_field("evidence_id", "Kanıt kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("photo_id", "Fotoğraf kimliği", True),
            url_field("source_url", "Kaynak sayfası", True),
            string_field("source_title", "Kaynak görsel başlığı", True),
            string_field("author", "Kaynak fotoğrafçısı", True),
            string_field("license", "Kaynak lisansı", True),
            url_field("license_url", "Kaynak lisans bağlantısı", True),
            string_field("usage_terms", "Kullanım koşulları", True),
            string_field("attribution", "Gerekli atıf metni"),
            string_field("restrictions", "Kısıt / üçüncü kişi hakkı"),
            date_field("checked_on", "Kanıt kontrol tarihi", True),
            choice(
                "metadata_review_status",
                "Kaynak bilgisi incelemesi",
                {"Bekliyor": "pending", "Doğrulandı": "verified"},
            ),
            choice(
                "pixel_review_status",
                "Kare / mekân incelemesi",
                {"Bekliyor": "pending", "Doğrulandı": "verified"},
            ),
            string_field("pixel_review_file", "İncelenen görsel dosyası"),
            string_field("pixel_review_note", "Mekân eşleşmesi ve kare notu"),
            choice(
                "rights_status",
                "Üçüncü kişi hak incelemesi",
                {
                    "Bekliyor": "pending",
                    "Bu kare için uygun": "reviewed-clear-for-exact-frame",
                },
            ),
            string_field("rights_basis", "Hak değerlendirmesi gerekçesi"),
            string_field("source_snapshot_file", "Kaynak sayfası kanıt dosyası"),
            string_field("source_snapshot_sha256", "Kaynak kanıt SHA-256"),
            string_field("license_snapshot_file", "Lisans kanıt dosyası"),
            string_field("license_snapshot_sha256", "Lisans kanıt SHA-256"),
            object_field("source_evidence_json", "Tam özgün kanıt yapısı (JSON)"),
        ],
    },
    "page_fields": {
        "sheet": "SayfaAlanları",
        "title": "Sayfa metinleri ve ek yapılandırma",
        "capacity": 120,
        "fields": [
            string_field("field_id", "Alan kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("key", "Sayfa alanı anahtarı", True),
            string_field("label", "Türkçe alan açıklaması", True),
            string_field(
                "value_type",
                "Değer türü",
                True,
                choices=["Metin", "Sayı", "Mantıksal", "JSON"],
            ),
            string_field("value", "Alan değeri", True),
            date_field("reviewed_on", "Alan kontrol tarihi", True),
        ],
    },
    "entry_details": {
        "sheet": "EkDetaylar",
        "title": "Ek kart alanları",
        "capacity": 200,
        "fields": [
            string_field("detail_id", "Detay kimliği", True),
            string_field("city_id", CITY_LABEL, True),
            string_field("entry_id", ENTRY_LABEL, True),
            string_field("key", "Detay anahtarı", True),
            string_field("label", "Türkçe alan açıklaması", True),
            string_field(
                "value_type",
                "Değer türü",
                True,
                choices=["Metin", "Sayı", "Mantıksal", "JSON"],
            ),
            string_field("value", "Alan değeri", True),
        ],
    },
}

SCHEMA = {
    "schema_version": SCHEMA_VERSION,
    "acceptance_version": "2026-10-13.1",
    "language": "tr",
    "human_header_row": 6,
    "machine_header_row": 7,
    "first_data_row": 8,
    "list_separator": ";",
    "text_list_separator": "newline",
    "minimum": {
        "answers": 212,
        "places": 92,
        "neighborhoods": 12,
        "topics": 12,
        "photos": 187,
        "hero_photos": 6,
        "routes": 9,
        "glossary": 48,
    },
    "target": {
        "answers": 240,
        "places": 120,
        "neighborhoods": 16,
        "topics": 12,
        "photos": 250,
        "hero_photos": 8,
        "routes": 12,
        "glossary": 60,
    },
    "tables": TABLES,
    "rules": {
        "ids": "ASCII: şehir slug; içerik şehir:slug; tablo kimlikleri şehir:tip:slug.",
        "date": "Tarihler boş olabilen çekim tarihi dışında zorunlu alanlarda dolu, YYYY-MM-DD; gelecek olamaz.",
        "acceptance": "Sayım ve yapısal doğrulama insanın yerel içerik ve hak onayı yerine geçmez.",
        "publication": "Araç yalnız JSON üretir; PostgreSQL, UAT veya yayın durumunu değiştirmez.",
    },
}


def property_choices(prop, field):
    kind = field["type"]
    if kind in ("id_list", "text_list"):
        prop.update(items={"type": "string"}, uniqueItems=True)
        if field.get("choices"):
            prop["items"]["enum"] = field["choices"]
    elif field.get("choices") and kind != "boolean":
        prop["enum"] = (
            list(field["choice_map"].values())
            if field.get("choice_map")
            else field["choices"]
        )


def field_property(field):
    kind = field["type"]
    prop = {
        "title": field["label"],
        "type": {
            "date": "string",
            "url": "string",
            "id_list": "array",
            "text_list": "array",
        }.get(kind, kind),
    }
    if kind in ("date", "url"):
        prop["format"] = {"date": "date", "url": "uri"}[kind]
    property_choices(prop, field)
    for own, out in (
        ("max_length", "maxLength"),
        ("minimum", "minimum"),
        ("maximum", "maximum"),
    ):
        if own in field:
            prop[out] = field[own]
    if field["required"] and kind == "string":
        prop["minLength"] = 1
    return prop


def table_schema(key, config):
    fields = [field for field in config["fields"] if not field.get("readonly")]
    table = {
        "type": "array",
        "items": {
            "type": "object",
            "additionalProperties": False,
            "properties": {field["key"]: field_property(field) for field in fields},
            "required": [field["key"] for field in fields if field["required"]],
        },
    }
    if key in ("metadata", "city"):
        table.update(minItems=1, maxItems=1)
    return table


def formal_schema():
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://corteqs.com/schemas/content-team-1.0.json",
        "title": "Corteqs şehir içerik teslim tabloları",
        "type": "object",
        "additionalProperties": False,
        "properties": {
            key: table_schema(key, config) for key, config in TABLES.items()
        },
        "required": list(TABLES),
    }


def write_schema():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for filename, value in (
        ("sharedschema.json", SCHEMA),
        ("normalized-tables.schema.json", formal_schema()),
    ):
        (OUTPUT / filename).write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    write_schema()
