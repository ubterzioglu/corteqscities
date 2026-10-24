"""Yapısal kabul raporunu üretir; insan veya yayın onayı vermez."""

from .schema_definition import ROOT, SCHEMA
from .validation_context import ValidationContext
from .validation_fields import (
    check_city,
    check_metadata,
    check_tables,
    normalized_input,
)
from .validation_graph import check_entry_completeness, check_graph
from .validation_media import check_media, photo_counts
from .web_contract import check_web_contract

LABELS = {
    "answers": "Yanıt",
    "places": "Keşif noktası",
    "neighborhoods": "Mahalle",
    "topics": "Yanıt içeren konu",
    "photos": "Farklı mekân fotoğrafı",
    "hero_photos": "Kapak fotoğrafı",
    "routes": "Rota",
    "glossary": "Sözlük terimi",
}
LIMITATIONS = [
    "Kaynağın bugün erişilebilir veya doğru olması",
    "Dosyanın gerçek fotoğraf olduğunun semantik kanıtı",
    "Fotoğrafçı veya üçüncü kişi haklarının hukuki kesinliği",
    "Yerel mevzuat ve Türkçe metnin editoryal yeterliliği",
    "Şehrin otomatik yayımlanması veya editoryal onay",
]


def counts_for(context):
    venue, hero = photo_counts(context)
    counts = {
        key: len(context.rows(key))
        for key in ("answers", "places", "neighborhoods", "routes", "glossary")
    }
    topics = {
        row.get("topic_id")
        for row in context.rows("answers")
        if row.get("topic_id") in context.indices["topics"]
    }
    counts.update(topics=len(topics), photos=venue, hero_photos=hero)
    return counts


def check_minimum(context, counts):
    issues = context.errors if context.ready else context.warnings
    for key, minimum in SCHEMA["minimum"].items():
        if counts[key] < minimum:
            issues.append(
                f"{LABELS[key]}: {counts[key]} / asgari {minimum}; hedef {SCHEMA['target'][key]}."
            )


def validation_report(context, counts):
    return {
        "valid": not context.errors,
        "mode": context.mode,
        "schema_version": SCHEMA["schema_version"],
        "acceptance_version": SCHEMA["acceptance_version"],
        "counts": counts,
        "minimum": SCHEMA["minimum"],
        "target": SCHEMA["target"],
        "errors": context.errors,
        "warnings": context.warnings,
        "human_acceptance": "Yerel içerik, Türkçe, işlem bağlantısı, lisans ve kare eşleşmesi insan tarafından ayrıca incelenir.",
        "checks_do_not_prove": LIMITATIONS,
    }


def validate(data, mode="draft", assets_root=ROOT, today=None, initial_errors=None):
    errors = list(initial_errors or [])
    if mode not in ("draft", "ready"):
        errors.append("Doğrulama modu draft veya ready olmalı.")
    normalized = normalized_input(data, errors)
    context = ValidationContext(normalized, mode, assets_root, today, errors)
    check_tables(context)
    check_metadata(context)
    check_city(context)
    check_graph(context)
    check_media(context)
    check_entry_completeness(context)
    check_web_contract(context)
    counts = counts_for(context)
    check_minimum(context, counts)
    return validation_report(context, counts)
