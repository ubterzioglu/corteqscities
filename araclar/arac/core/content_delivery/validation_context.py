"""Doğrulama durumu ve paket içindeki kanıt dosyası denetimleri."""

import datetime as dt
import hashlib
import json
from pathlib import Path

from PIL import Image

from .delivery_values import SHA, identity
from .schema_definition import ROOT, SCHEMA


def blocked_sources():
    policy = ROOT / "core/data/media_rights.json"
    if not policy.is_file():
        return set()
    return {
        identity(url)
        for url in json.loads(policy.read_text()).get("blocked_sources", [])
    }


class ValidationContext:
    def __init__(self, data, mode, assets_root, today, initial_errors):
        self.data = data
        self.ready = mode == "ready"
        self.mode = mode
        self.root = Path(assets_root).resolve()
        self.today = today or dt.datetime.now(dt.timezone.utc).astimezone().date()
        self.errors = list(initial_errors or [])
        self.warnings = []
        self.indices = {}
        self.entries = {}
        self.blocked = blocked_sources()

    def rows(self, table):
        return self.data.get(table, [])

    def first(self, table):
        rows = self.rows(table)
        return rows[0] if rows else {}

    def error(self, table, row, message):
        self.errors.append(self.location(table, row, message))

    def warning(self, table, row, message):
        self.warnings.append(self.location(table, row, message))

    def review_issue(self, table, row, message):
        handler = self.error if self.ready else self.warning
        handler(table, row, message)

    @staticmethod
    def location(table, row, message):
        return f"{SCHEMA['tables'][table]['sheet']}!{row.get('_row', '?')}: {message}"

    def file_check(self, table, row, key, hashkey=None, image=False, required=False):
        value = row.get(key)
        if not value:
            if required:
                self.error(table, row, f"{key} kanıt dosyası gerekli.")
            return
        try:
            target = safe_file(self.root, value)
            if hashkey:
                self.check_hash(table, row, target, hashkey)
            if image:
                verify_image(target)
        except (OSError, ValueError, TypeError) as error:
            self.error(table, row, f"{key}: {error}")

    def check_hash(self, table, row, target, key):
        expected = row.get(key, "")
        if not SHA.fullmatch(str(expected)):
            self.error(table, row, f"{key} 64 karakter SHA-256 olmalı.")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            self.error(
                table,
                row,
                f"Dosyanın SHA-256 özeti eşleşmiyor: {row.get('file', target.name)}",
            )


def safe_file(root, value):
    path = Path(value)
    target = (root / path).resolve()
    if path.is_absolute() or ".." in path.parts or not target.is_relative_to(root):
        raise ValueError("Göreli yol olmalı ve dosya kökü dışına çıkmamalı.")
    candidate = root
    for part in path.parts:
        candidate = candidate / part
        if candidate.is_symlink():
            raise ValueError("Sembolik bağlantı kanıt dosyası olarak kabul edilmez.")
    if not target.is_file():
        raise ValueError(f"Dosya bulunamadı: {value}")
    return target


def verify_image(path):
    try:
        with Image.open(path) as image:
            if image.format not in ("JPEG", "PNG", "WEBP"):
                raise ValueError(
                    "Yalnız gerçek JPEG, PNG veya WebP dosyası kabul edilir."
                )
            image.verify()
    except (
        SyntaxError,
        OSError,
        Image.DecompressionBombError,
    ) as error:
        raise ValueError(f"Görsel dosyası çözümlenemedi: {path.name}") from error
