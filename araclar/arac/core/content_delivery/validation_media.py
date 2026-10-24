"""Fotoğraf, lisans, kare incelemesi ve fiziksel kaynak sayımı."""

import re
from urllib.parse import urlsplit

from .delivery_values import CC, identity, web_url

PLACE_ROLE = "Mekân"
FREE_LICENSES = {
    "CC0",
    "CC0 1.0",
    "FAL",
    "Özgür Sanat Lisansı",
    "Kamu malı",
    "Public domain",
    "Unsplash License",
    "Open Government Licence – Oman",
}
GENERATED = ("ai-generated", "generated", "quarantined-external")


def official_cc_url(url, path):
    if not web_url(url):
        return False
    parsed = urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "creativecommons.org"
        and not parsed.query
        and re.fullmatch(path, parsed.path) is not None
    )


def cc_license_matches(label, url):
    match = CC.fullmatch(label)
    if not match:
        return False
    kind, version, region = match.groups()
    base = rf"/licenses/{kind.lower()}/{re.escape(version)}"
    jurisdiction = "/" + region.lower() if region else ""
    # Bir ülke etiketi varsa aynı yetki alanı gerekir; yoksa portlanmamış lisans.
    return official_cc_url(
        url, base + jurisdiction + r"(?:/deed\.[a-z]{2}(?:_[A-Z]{2})?)?/?"
    )


def evidence_object(value):
    return value if isinstance(value, dict) else {}


def check_license(context, photo, raw):
    label = photo.get("license") or ""
    url = photo.get("license_url") or ""
    if not CC.fullmatch(label) and label not in FREE_LICENSES:
        context.error(
            "photos",
            photo,
            "Ücretsiz ticari kullanım lisansı desteklenmiyor; NC/ND, ücretli veya belirsiz hak kabul edilmez.",
        )
    if label in ("CC0", "CC0 1.0") and not official_cc_url(
        url, r"/publicdomain/zero/1\.0(?:/deed\.[a-z]{2})?/?"
    ):
        context.error("photos", photo, "CC0 için resmî 1.0 lisans bağlantısı gerekli.")
    if CC.fullmatch(label) and not cc_license_matches(label, url):
        context.error(
            "photos",
            photo,
            "Creative Commons etiketi ve resmî lisans bağlantısı eşleşmiyor.",
        )
    check_special_license(context, photo, raw)


def check_special_license(context, photo, raw):
    label = photo.get("license")
    if label == "Unsplash License" and not unsplash_grant(photo, raw):
        context.error("photos", photo, "Unsplash ücretsiz ticari lisans kanıtı eksik.")
    if label == "Open Government Licence – Oman" and not raw.get(
        "open_government_license"
    ):
        context.error(
            "photos", photo, "Umman açık lisansı için özgün lisans kanıtı gerekli."
        )
    provenance = evidence_object(raw.get("provenance"))
    if raw.get("kind") in GENERATED or provenance.get("kind") in GENERATED:
        context.error(
            "photos", photo, "AI üretilmiş veya kullanım dışı görsel kabul edilmez."
        )


def unsplash_grant(photo, raw):
    if not web_url(photo.get("source_url")):
        return False
    grant = evidence_object(raw.get("unsplash_license"))
    return (
        photo.get("license_url") == "https://unsplash.com/license"
        and urlsplit(photo["source_url"]).hostname == "unsplash.com"
        and grant.get("commercial_reuse") is True
        and grant.get("free_photo_grant") is True
    )


def check_original_evidence(context, photo, evidence):
    raw = evidence_object(evidence.get("source_evidence_json"))
    check_evidence_structure(context, evidence, raw)
    for key in ("author", "license", "license_url"):
        if raw.get(key) and raw[key] != evidence.get(key):
            context.error(
                "evidence",
                evidence,
                f"Özgün JSON içindeki {key} kanıt sütunuyla eşleşmiyor.",
            )
    source_url = raw.get("source_url")
    if source_url and not matching_source(source_url, evidence.get("source_url")):
        context.error(
            "evidence", evidence, "Özgün JSON kaynak URL'si kanıt sütunuyla eşleşmiyor."
        )
    check_license(context, photo, raw)


def check_evidence_structure(context, evidence, raw):
    for key in (
        "provenance",
        "unsplash_license",
        "open_government_license",
    ):
        if key in raw and not isinstance(raw[key], dict):
            context.error("evidence", evidence, f"Özgün JSON {key} alanı nesne olmalı.")
    if "kind" in raw and not isinstance(raw["kind"], str):
        context.error("evidence", evidence, "Özgün JSON kind alanı metin olmalı.")


def matching_source(first, second):
    return web_url(first) and web_url(second) and identity(first) == identity(second)


def check_photo_evidence(context, photo):
    evidence = context.indices["evidence"].get(photo.get("evidence_id"))
    if not evidence:
        context.error("photos", photo, "Kanıt kimliği bulunamadı.")
        check_license(context, photo, {})
        return
    if evidence.get("photo_id") != photo.get("photo_id"):
        context.error("photos", photo, "Kanıtın fotoğraf kimliği eşleşmiyor.")
    for key in ("author", "license", "license_url"):
        if evidence.get(key) != photo.get(key):
            context.error(
                "photos", photo, f"Kanıtın {key} alanı fotoğrafla eşleşmiyor."
            )
    if not matching_source(photo.get("source_url"), evidence.get("source_url")):
        context.error("photos", photo, "Kanıtın kaynak URL'si fotoğrafla eşleşmiyor.")
    check_original_evidence(context, photo, evidence)


def check_photo_links(context, photo):
    role, entry_id = photo.get("role"), photo.get("entry_id")
    if role == PLACE_ROLE and entry_id not in context.entries:
        context.error("photos", photo, "Mekân fotoğrafının içerik kimliği bulunamadı.")
    if role == PLACE_ROLE and entry_id in context.indices["answers"]:
        context.error("photos", photo, "Mekân fotoğrafı yanıt kartına bağlanamaz.")
    if role == "Kapak" and entry_id:
        context.error("photos", photo, "Kapak fotoğrafında içerik kimliği boş olmalı.")
    source = photo.get("source_url")
    if web_url(source) and identity(source) in context.blocked:
        context.error(
            "photos",
            photo,
            "Kaynak mevcut Corteqs medya politikasında kullanım dışı bırakılmış.",
        )


def check_photos(context):
    pairs = set()
    for photo in context.rows("photos"):
        check_photo_links(context, photo)
        pair = (photo.get("role"), photo.get("entry_id"), photo.get("order"))
        if pair in pairs:
            context.error("photos", photo, "Aynı galeride sıra numarası yineleniyor.")
        pairs.add(pair)
        context.file_check("photos", photo, "file", "sha256", image=True, required=True)
        check_photo_evidence(context, photo)


def check_review_states(context, row):
    for key in ("metadata_review_status", "pixel_review_status", "rights_status"):
        expected = (
            "reviewed-clear-for-exact-frame" if key == "rights_status" else "verified"
        )
        if row.get(key) != expected:
            context.review_issue("evidence", row, f"{key} incelemesi açık.")
    if not context.ready:
        return
    for key in ("pixel_review_file", "pixel_review_note", "rights_basis"):
        if not row.get(key):
            context.error("evidence", row, f"{key} gerekli.")
    if not row.get("source_evidence_json"):
        context.error("evidence", row, "Tam özgün kaynak kanıtı JSON yapısı gerekli.")


def check_evidence(context):
    for row in context.rows("evidence"):
        photo = context.indices["photos"].get(row.get("photo_id"), {})
        if not photo:
            context.error("evidence", row, "Fotoğraf kimliği bulunamadı.")
        elif photo.get("evidence_id") != row.get("evidence_id"):
            context.error(
                "evidence", row, "Fotoğrafın kanıt kimliği bu satıra geri bağlanmalı."
            )
        check_review_states(context, row)
        check_evidence_files(context, row, photo)


def check_evidence_files(context, row, photo):
    context.file_check(
        "evidence",
        row,
        "source_snapshot_file",
        "source_snapshot_sha256",
        required=context.ready,
    )
    context.file_check(
        "evidence",
        row,
        "license_snapshot_file",
        "license_snapshot_sha256",
        required=context.ready,
    )
    context.file_check("evidence", row, "pixel_review_file")
    if row.get("pixel_review_file") and row["pixel_review_file"] != photo.get("file"):
        context.error(
            "evidence", row, "İncelenen kare teslim edilen dosyayla aynı olmalı."
        )


def check_hero(context):
    city = context.first("city")
    if city.get("hero_photo_id"):
        hero = context.indices["photos"].get(city["hero_photo_id"])
        if not hero or hero.get("role") != "Kapak":
            context.errors.append("Şehir: ana kapak kimliği Kapak satırına bağlanmalı.")
    elif context.ready:
        context.errors.append("Şehir: ana kapak fotoğrafı gerekli.")


class PhotoIdentity:
    """Hash veya kanonik kaynak ortaksa tek fiziksel görsel grubu."""

    def __init__(self):
        self.parents = {}
        self.by_token = {}

    def root(self, index):
        while self.parents[index] != index:
            self.parents[index] = self.parents[self.parents[index]]
            index = self.parents[index]
        return index

    def add(self, index, photo):
        self.parents[index] = index
        tokens = [("sha", photo.get("sha256"))]
        if web_url(photo.get("source_url")):
            tokens.append(("source", identity(photo["source_url"])))
        for token in tokens:
            if not token[1]:
                continue
            if token in self.by_token:
                self.parents[self.root(index)] = self.root(self.by_token[token])
            self.by_token[token] = index


def check_derivative_credit(context):
    sources = {}
    for photo in context.rows("photos"):
        if photo.get("completion_credit") is not True or not web_url(
            photo.get("source_url")
        ):
            continue
        source = identity(photo["source_url"])
        hashes = sources.setdefault(source, set())
        if hashes and photo.get("sha256") not in hashes:
            context.review_issue(
                "photos",
                photo,
                "Aynı kaynak fotoğrafının farklı dosya türevi ek tamamlama kredisi alamaz; tek kare olarak sayıldı.",
            )
        hashes.add(photo.get("sha256"))


def photo_counts(context):
    photos = context.rows("photos")
    groups = PhotoIdentity()
    for index, photo in enumerate(photos):
        groups.add(index, photo)
    credited = {PLACE_ROLE: set(), "Kapak": set()}
    for index, photo in enumerate(photos):
        if photo.get("completion_credit") is True and photo.get("role") in credited:
            credited[photo["role"]].add(groups.root(index))
    check_derivative_credit(context)
    return len(credited[PLACE_ROLE]), len(credited["Kapak"])


def check_media(context):
    check_photos(context)
    check_evidence(context)
    check_hero(context)
