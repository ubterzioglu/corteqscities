import io
import json
import tempfile
import unittest
from pathlib import Path
from PIL import Image
from download_media import public_url, read_image_response, cached_record, install_copy
from delivery_tools import digest


class DownloadQueueTests(unittest.TestCase):
    def test_only_explicit_https_hosts(self):
        for url in ('http://upload.wikimedia.org/x', 'https://localhost/x', 'https://upload.wikimedia.org@evil.example/x', 'https://upload.wikimedia.org:8443/x'):
            with self.assertRaises(ValueError): public_url(url, {'upload.wikimedia.org'}, resolve=False)

    def test_non_images_and_oversize_fail(self):
        with tempfile.TemporaryDirectory() as path:
            target = Path(path) / 'download'
            with self.assertRaises(ValueError): read_image_response(io.BytesIO(b'a'*100), target, 50)
            with self.assertRaises(OSError): read_image_response(io.BytesIO(b'not a photo'), target)

    def test_cached_hash_must_match(self):
        import hashlib
        with tempfile.TemporaryDirectory() as path:
            root = Path(path); url = 'https://upload.wikimedia.org/test.jpg'; key = hashlib.sha256(url.encode()).hexdigest()
            image = root / (key+'.image'); image.write_bytes(b'kept bytes')
            meta = {'downloaded_file_url':url, 'sha256':digest(image)}
            (root/(key+'.json')).write_text(json.dumps(meta))
            self.assertEqual(cached_record(root,url)[0], meta)
            image.write_bytes(b'changed bytes')
            self.assertIsNone(cached_record(root,url)[0])

    def test_existing_user_file_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as path:
            root=Path(path); cached=root/'cached'; cached.write_bytes(b'new'); target=root/'photo.jpg'; target.write_bytes(b'user work')
            with self.assertRaises(ValueError): install_copy(root, {'photo_id':'x','original_file':'photo.jpg'}, {'sha256':digest(cached)},cached)
            self.assertEqual(target.read_bytes(),b'user work')


if __name__ == '__main__': unittest.main()
