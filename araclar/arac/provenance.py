"""Preserve explicit source evidence; never invent a photographer or download URL."""
import html
import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            href = dict(attrs).get('href')
            if href:
                self.links.append(href)

def safe_url(value, base='https://commons.wikimedia.org/'):
    if not value:
        return ''
    value = urljoin(base, html.unescape(str(value)))
    parsed = urlsplit(value)
    if parsed.scheme not in ('https', 'http') or not parsed.hostname or parsed.username or parsed.password:
        return ''
    return value

def author_link(raw, author, base):
    parser = Links()
    parser.feed(raw or '')
    urls = [safe_url(link, base) for link in parser.links]
    urls = [url for url in urls if usable_author_url(url)]
    if urls:
        return urls[0]
    match = re.search(r'https?://[^\s<>()]+', author or '')
    return safe_url(match.group(0)) if match else ''

def usable_author_url(url):
    return bool(url) and not any(x in url for x in ['/w/index.php?', '/wiki/File:', 'creativecommons.org', 'action=edit', 'redlink=1'])

def object_value(value):
    return json.loads(value) if isinstance(value, str) else value or {}

def extract(photo, evidence):
    raw = object_value(evidence.get('source_evidence_json'))
    info = raw.get('original_api_record', {})
    delivered = raw.get('delivered_file', {})
    artist = info.get('extmetadata', {}).get('Artist', {}).get('value', '')
    base = photo.get('source_url', '')
    profile = author_link(artist, photo.get('author', ''), base)
    return {
        'photo_id': photo['photo_id'],
        'author_url': profile,
        'attribution_url': profile or base,
        'original_file_url': safe_url(info.get('url', '')),
        'downloaded_file_url': safe_url(delivered.get('url', '')),
        'downloaded_on': raw.get('retrieved_on', ''),
        'original_file': photo.get('file', ''),
        'original_sha256': photo.get('sha256', ''),
        'web_file': '',
        'web_sha256': '',
        'web_width': None,
        'web_height': None,
        'derivation': '',
        'provenance_status': 'Kayıttan doğrulandı' if profile and info.get('url') and delivered.get('url') else 'Eksik alan var',
        'provenance_note': '' if profile else 'Kaynakta ayrı fotoğrafçı profil bağlantısı bulunmadı; fotoğraf kaynak sayfasına atıf korunur. Bağlantı uydurulmaz.',
    }

FIELDS = [
    ('photo_id', 'Fotoğraf kimliği', 32),
    ('author_url', 'Fotoğrafçı profil / portföy bağlantısı', 48),
    ('attribution_url', 'Görünür fotoğrafçı atıf bağlantısı', 48),
    ('original_file_url', 'Kaynakta özgün fotoğraf dosyası URL', 55),
    ('downloaded_file_url', 'Fiilen indirilen dosyanın URL’si', 55),
    ('downloaded_on', 'Kaydedilmiş indirme tarihi', 24),
    ('original_file', 'Korunan mevcut fotoğraf dosyası', 48),
    ('original_sha256', 'Korunan dosya SHA-256', 40),
    ('web_file', 'Hafif web kopyası (varsa)', 48),
    ('web_sha256', 'Web kopyası SHA-256', 40),
    ('web_width', 'Web genişliği (px)', 20),
    ('web_height', 'Web yüksekliği (px)', 20),
    ('derivation', 'Dönüştürme kaydı', 58),
    ('provenance_status', 'Kaynak zinciri kontrolü', 30),
    ('provenance_note', 'Açık nokta / kanıt açıklaması', 65),
]
