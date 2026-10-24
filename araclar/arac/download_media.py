"""Bounded public-media download queue for future city packages; never uploads."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import shutil
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
from PIL import Image
from delivery_tools import digest, local_file

MAX_BYTES = 100 * 1024 * 1024


def public_url(url, hosts, resolve=True):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != 'https' or parsed.hostname not in hosts or parsed.username or parsed.password or parsed.port not in (None, 443):
        raise ValueError('Only HTTPS on explicitly allowed public media hosts is accepted')
    if resolve:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
        if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
            raise ValueError('Non-public destination is blocked')
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def __init__(self, hosts):
        self.hosts = hosts

    def redirect_request(self, request, fp, code, message, headers, newurl):
        public_url(newurl, self.hosts)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def read_image_response(response, target, max_bytes=MAX_BYTES):
    total = 0
    with target.open('wb') as output:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            total += len(block)
            if total > max_bytes:
                raise ValueError('Download exceeds configured byte limit')
            output.write(block)
    with Image.open(target) as image:
        if image.format not in ('JPEG', 'PNG', 'WEBP'):
            raise ValueError('Only real JPEG, PNG or WebP images are accepted')
        image.verify()
    return total


def cached_record(cache, url):
    key = hashlib.sha256(url.encode()).hexdigest()
    metadata, image = cache / (key + '.json'), cache / (key + '.image')
    if metadata.exists() and image.exists():
        record = json.loads(metadata.read_text())
        if record.get('downloaded_file_url') == url and digest(image) == record.get('sha256'):
            return record, image
    return None, image


def fetch_one(cache, url, hosts, max_bytes):
    public_url(url, hosts, resolve=False)
    record, target = cached_record(cache, url)
    if record:
        return record, target
    public_url(url, hosts)
    opener = urllib.request.build_opener(PublicRedirect(hosts))
    partial = target.with_suffix('.part')
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Corteqs-content-delivery/7.0 (source-attributed editorial media)'})
            with opener.open(request, timeout=45) as response:
                size = read_image_response(response, partial, max_bytes)
                final_url = public_url(response.geturl(), hosts)
            partial.replace(target)
            record = {'downloaded_file_url': url, 'resolved_download_url': final_url, 'downloaded_on': datetime.now(timezone.utc).date().isoformat(), 'sha256': digest(target), 'bytes': size}
            temporary = target.with_suffix('.json.part')
            temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2))
            temporary.replace(target.with_suffix('.json'))
            return record, target
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503, 504) or attempt == 2:
                raise
            retry = error.headers.get('Retry-After', '')
            delay = int(retry) if retry.isdigit() else (attempt + 1) * 5
            if delay > 30 or (retry and not retry.isdigit()):
                raise ValueError('Source asks for a later retry; resume this queue later') from error
            time.sleep(delay)
        finally:
            partial.unlink(missing_ok=True)
    raise RuntimeError('Download attempts exhausted')


def install_copy(root, row, record, cached):
    target = local_file(root, row['original_file'])
    if target.exists():
        if digest(target) != record['sha256']:
            raise ValueError('Existing destination differs; refusing to overwrite: ' + row['photo_id'])
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + '.part')
        shutil.copyfile(cached, temporary)
        temporary.replace(target)
    return {**row, **record, 'original_sha256': record['sha256']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('root', type=Path)
    parser.add_argument('--allow-host', action='append', default=['upload.wikimedia.org'])
    parser.add_argument('--workers', type=int, choices=(1, 2, 3), default=2)
    args = parser.parse_args()
    rows = json.loads(args.manifest.read_text())
    if len({r['photo_id'] for r in rows}) != len(rows):
        raise ValueError('Duplicate photo IDs')
    cache = args.root / 'Teslimler/.download-cache'; cache.mkdir(parents=True, exist_ok=True)
    grouped = {}
    for row in rows:
        local_file(args.root, row['original_file'])
        public_url(row['downloaded_file_url'], set(args.allow_host), resolve=False)
        grouped.setdefault(row['downloaded_file_url'], []).append(row)
    def work(url):
        record, file = fetch_one(cache, url, set(args.allow_host), MAX_BYTES)
        return [install_copy(args.root, row, record, file) for row in grouped[url]]
    completed = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for batch in pool.map(work, grouped):
            completed.extend(batch)
            output = args.root / 'Teslimler/download-progress-v7.json'
            temporary = output.with_suffix('.part')
            temporary.write_text(json.dumps(completed, ensure_ascii=False, indent=2))
            temporary.replace(output)
    print(json.dumps({'completed': len(completed), 'unique_urls': len(grouped), 'rights_approval_granted': False}))


if __name__ == '__main__':
    main()
